import random, math
import pygame
import thorpy



def get_distributor(me, objects, forest_map, material_names,
                    limit_relpos_y=True):
    if limit_relpos_y:
        for obj in objects:
            obj.max_relpos[1] = (1. - obj.factor)/2.
            if obj.min_relpos[1] > obj.max_relpos[1]:
                obj.min_relpos[1] = obj.max_relpos[1]
    distributor = RandomObjectDistribution(objects, forest_map, me.lm)
    for name in material_names:
        if name in me.materials:
            distributor.materials.append(me.materials[name])
    distributor.max_density = 3
    distributor.homogeneity = 0.75
    distributor.zones_spread = [(0.1, 0.02), (0.5,0.02), (0.9,0.02)]
    return distributor

class RandomObjectDistribution:

    def __init__(self, objs, hmap, master_map):
        self.objs = objs
        self.hmap = hmap
        self.master_map = master_map
        assert master_map.nx <= len(hmap) and master_map.ny <= len(hmap[0])
        self.materials = []
        self.max_density = 1
        self.homogeneity = 0.5
        self.zones_spread = [(0.,1.)]


    def distribute_objects(self, layer, exclusive=False):
        nx,ny = self.master_map.nx, self.master_map.ny
        dx, dy = random.randint(0,nx-1), random.randint(0,ny-1)
        for x,y in self.master_map:
            h = self.hmap[(x+dx)%nx][(y+dy)%ny]
            right_h = False
            for heigth,spread in self.zones_spread:
                if abs(h-heigth) < spread:
                    right_h = True
                    break
            if right_h:
                cell = self.master_map.cells[x][y]
                if cell.material in self.materials:
                    if exclusive:
                        remove_objects(cell, layer)
                    for i in range(self.max_density):
                        if random.random() < self.homogeneity:
                            obj = random.choice(self.objs)
                            obj = obj.add_copy_on_cell(cell)
                            obj.randomize_relpos()
                            layer.static_objects.append(obj)


def remove_objects(cell, layer):
    if cell.objects:
        for obj in cell.objects:
            layer.static_objects.remove(obj)
        cell.objects = []

class MapObject:

    def __init__(self, editor, fn, name="", factor=1., relpos=(0,0), build=True):
        """Object that looks the same at each frame"""
        self.editor = editor
        ref_size = editor.zoom_cell_sizes[0]
        if fn:
            img = thorpy.load_image(fn, colorkey=(255,255,255))
            img = thorpy.get_resized_image(img, (factor*ref_size,)*2)
        else:
            img = None
        self.factor = factor
        self.original_img = img
        self.relpos = [0,0]
        self.imgs = None
        self.cell = None
        self.name = name
        self.ncopies = 0
        self.min_relpos = [-0.4, -0.4]
        self.max_relpos = [0.4,   0.4]
##        self.min_relpos = [-0.1, -0.1]
##        self.max_relpos = [0.1,   0.1]
        self.quantity = 1 #not necessarily 1 for units
        if build and fn:
            self.build_imgs()

    def ypos(self):
        h = self.original_img.get_size()[1]
        s = self.editor.zoom_cell_sizes[0]
        return self.cell.coord[1]  + 0.5*h/s + self.relpos[1]

    def randomize_relpos(self):
        self.relpos[0] = self.min_relpos[0] +\
                         random.random()*(self.max_relpos[0]-self.min_relpos[0])
        self.relpos[1] = self.min_relpos[1] +\
                         random.random()*(self.max_relpos[1]-self.min_relpos[1])

    def copy(self):
        """The copy references the same images as the original !"""
        self.ncopies += 1
        obj = MapObject(self.editor, "", self.name, self.factor, list(self.relpos))
        obj.original_img = self.original_img
        obj.imgs = self.imgs
        obj.min_relpos = list(self.min_relpos)
        obj.max_relpos = list(self.max_relpos)
        return obj

    def deep_copy(self):
        obj = MapObject(self.editor, "", self.name, self.factor, list(self.relpos))
        obj.original_img = self.original_img.copy()
        obj.imgs = [i.copy() for i in self.imgs]
        obj.min_relpos = list(self.min_relpos)
        obj.max_relpos = list(self.max_relpos)
        return obj


    def flip(self, x=True, y=False):
        obj = self.deep_copy()
        obj.original_img = pygame.transform.flip(obj.original_img, x, y)
        for i in range(len(obj.imgs)):
            obj.imgs[i] = pygame.transform.flip(obj.imgs[i], x, y)
        return obj

    def add_copy_on_cell(self, cell):
        copy = self.copy()
        copy.cell = cell
        cell.objects.append(copy)
        return copy

    def add_unit_on_cell(self, cell):
        assert cell.unit is None
        copy = self.copy()
        copy.cell = cell
        cell.unit = copy
        return copy

    def build_imgs(self):
        W,H = self.original_img.get_size()
        w0 = float(self.editor.zoom_cell_sizes[0])
        imgs = []
        for w in self.editor.zoom_cell_sizes:
            factor = w/w0
            zoom_size = (int(factor*W), int(factor*H))
            img = pygame.transform.scale(self.original_img, zoom_size)
            imgs.append(img)
        self.imgs = imgs

    def get_current_img(self):
        return self.imgs[self.cell.map.current_zoom_level]



def distribute_random_path(editor, layer, cobbles, woods, cell_i, cell_f, k=3):
    villages = [o for o in layer.static_objects if "village" in o.name]
    if villages:
        if cell_i == "auto":
            cell_i = random.choice(villages).cell
        if cell_f == "auto":
            cell_f = random.choice(villages).cell


##            if editor.cells[x][y].objects
##    path = build_random_path(cell_i.coord[0], cell_i.coord[1],
##                             cell_f.coord[0], cell_f.coord[1], k)


##for x,y in build_random_path(30,30, 45,32, k=3):
##    c = random.choice(cobbles)
##    c = c.add_copy_on_cell(lm.cells[x][y])
##    c.randomize_relpos()
##    layer2.static_objects.append(c)

def sgn(x):
    if x < 0:
        return -1.
    elif x > 0:
        return 1.
    return 0.

def build_random_path(xi,yi, xf,yf, k=3, nmax=10000):
    x,y = xi,yi
    path = set([(x,y)])
    dx = xf-xi
    dy = yf-yi
    if dx != 0:
        choices_x = [int(sgn(dx)),]*k + [-1*int(sgn(dx))]
    else:
        choices_x = [-1,1]
    if dy != 0:
        choices_y = [int(sgn(dy)),]*k + [-1*int(sgn(dy))]
    else:
        choices_y = [-1,1]
    iters = 0
    while x != xf or y != yf:
        if iters > nmax:
            break
        dx = xf-x
        dy = yf-y
        if dy != 0:
            probx = 1. / (1. + math.exp(-abs(float(dx)/dy)))
        else:
            probx = 1.
        if random.random() < probx:
            x += random.choice(choices_x)
        else:
            y += random.choice(choices_y)
        path.add((x,y))
        iters += 1
    return path




