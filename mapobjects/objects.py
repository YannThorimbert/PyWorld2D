import random, math
import pygame
import thorpy

from ia.path import BranchAndBoundForMap



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
    current_id = 1

    def __init__(self, editor, fn, name="", factor=1., relpos=(0,0), build=True,
                 new_type=True):
        """Object that looks the same at each frame"""
        self.editor = editor
        ref_size = editor.zoom_cell_sizes[0]
        if fn:
            if isinstance(fn,str):
                img = thorpy.load_image(fn, colorkey=(255,255,255))
            else:
                img = fn
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
        if new_type:
            self.object_type = MapObject.current_id
            MapObject.current_id += 1
        else:
            self.object_type = None

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
        obj = MapObject(self.editor, "", self.name, self.factor,
                        list(self.relpos), new_type=False)
        obj.original_img = self.original_img
        obj.imgs = self.imgs
        obj.min_relpos = list(self.min_relpos)
        obj.max_relpos = list(self.max_relpos)
        obj.object_type = self.object_type
        return obj

    def deep_copy(self):
        obj = MapObject(self.editor, "", self.name, self.factor,
                        list(self.relpos), new_type=False)
        obj.original_img = self.original_img.copy()
        obj.imgs = [i.copy() for i in self.imgs]
        obj.min_relpos = list(self.min_relpos)
        obj.max_relpos = list(self.max_relpos)
        obj.object_type = self.object_type
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

    def set_same_type(self, objs):
        for o in objs:
            o.object_type = self.object_type



def distance(coord1, coord2):
    return abs(coord1[0]-coord2[0]) + abs(coord1[1]-coord2[1])


VON_NEUMAN = [(-1,0), (1,0), (0,-1), (0,1)]

def find_free_next_to(lm, coord):
    ok = []
    for x,y in VON_NEUMAN:
        cell = lm.get_cell_at(coord[0]+x,coord[1]+y)
        if cell:
            if not cell.objects:
                if not cell.unit:
                    ok.append(cell)
    if ok:
        return random.choice(ok)

def add_random_road(lm, layer,
                    cobbles, woods,
                    costs_materials, costs_objects,
                    possible_materials, possible_objects):
    """Computes and draw a random road between two random villages."""
    villages = [o for o in layer.static_objects if "village" in o.name]
    v1 = random.choice(villages)
    c1 = find_free_next_to(lm, v1.cell.coord)
    # c1 = v1.cell
    if c1:
        v2 = random.choice(villages)
        c2 = find_free_next_to(lm, v2.cell.coord)
        # c2 = v2.cell
        if c2:
            sp = BranchAndBoundForMap(lm, c1, c2,
                                    costs_materials, costs_objects,
                                    possible_materials, possible_objects)
            path = sp.solve()
            draw_road(path, cobbles, woods, lm)

def add_random_river(lm,
                    objects,
                    costs_materials, costs_objects,
                    possible_materials, possible_objects):
    """Computes and draw a random road between two random villages."""
    #1) pick one random source and one random end in water:
    for i in range(1000):
        x,y = random.randint(0,lm.nx-1), random.randint(0,lm.ny-1)
        cell_water = lm.cells[x][y]
        if "shallow" in cell_water.material.name.lower():
            break
    else:
        return
    for i in range(1000):
        x,y = random.randint(0,lm.nx-1), random.randint(0,lm.ny-1)
        cell_land = lm.cells[x][y]
        if "snow" in cell_land.material.name.lower():
            break
    else:
        return
    sp = BranchAndBoundForMap(lm, cell_land, cell_water,
                            costs_materials, costs_objects,
                            possible_materials, possible_objects)
    path = sp.solve()
    actual_path = []
    for cell in path:
        if "shallow" in cell.material.name.lower():
            actual_path.append(cell)
            break
        else:
            actual_path.append(cell)
    draw_path(actual_path, objects, lm)



def draw_path(path, objects, layer):
    """<path> is a list of cells"""
    for cell in path:
        c = random.choice(objects)
        c = c.add_copy_on_cell(cell)
        layer.static_objects.append(c)

def draw_road(path, cobbles, woods, layer):
    """<path> is a list of cells"""
    for cell in path:
        if "water" in cell.material.name.lower():
            c = random.choice(woods)
        else:
            c = random.choice(cobbles)
        c = c.add_copy_on_cell(cell)
        layer.static_objects.append(c)
