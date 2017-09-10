import random, math
import pygame
import thorpy

from ia.path import BranchAndBoundForMap
import rendering.tilers.tilemanager as tm

VON_NEUMAN = [(-1,0), (1,0), (0,-1), (0,1)]



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

def put_static_obj(obj, lm, coord, layer):
    cop = obj.add_copy_on_cell(lm[coord])
    layer.static_objects.append(cop)
    return cop

def remove_objects(cell, layer):
    if cell.objects:
        for obj in cell.objects:
            layer.static_objects.remove(obj)
        cell.objects = []




##class MapObject:
##    current_id = 1
##
##    def __init__(self, editor, fn, name="", factor=1., relpos=(0,0), build=True,
##                 new_type=True):
##        """Object that looks the same at each frame"""
##        self.editor = editor
##        ref_size = editor.zoom_cell_sizes[0]
##        if fn:
##            if isinstance(fn,str):
##                img = thorpy.load_image(fn, colorkey=(255,255,255))
##            else:
##                img = fn
##            img = thorpy.get_resized_image(img, (factor*ref_size,)*2)
##        else:
##            img = None
##        self.factor = factor
##        self.original_img = img
##        self.relpos = [0,0]
##        self.imgs = None
##        self.cell = None
##        self.name = name
##        self.ncopies = 0
##        self.min_relpos = [-0.4, -0.4]
##        self.max_relpos = [0.4,   0.4]
####        self.min_relpos = [-0.1, -0.1]
####        self.max_relpos = [0.1,   0.1]
##        self.quantity = 1 #not necessarily 1 for units
##        if build and fn:
##            self.build_imgs()
##        if new_type:
##            self.object_type = MapObject.current_id
##            MapObject.current_id += 1
##        else:
##            self.object_type = None
##
##    def ypos(self):
##        h = self.original_img.get_size()[1]
##        s = self.editor.zoom_cell_sizes[0]
##        return self.cell.coord[1]  + 0.5*h/s + self.relpos[1]
##
##    def randomize_relpos(self):
##        self.relpos[0] = self.min_relpos[0] +\
##                         random.random()*(self.max_relpos[0]-self.min_relpos[0])
##        self.relpos[1] = self.min_relpos[1] +\
##                         random.random()*(self.max_relpos[1]-self.min_relpos[1])
##
##    def copy(self):
##        """The copy references the same images as the original !"""
##        self.ncopies += 1
##        obj = MapObject(self.editor, "", self.name, self.factor,
##                        list(self.relpos), new_type=False)
##        obj.original_img = self.original_img
##        obj.imgs = self.imgs
##        obj.min_relpos = list(self.min_relpos)
##        obj.max_relpos = list(self.max_relpos)
##        obj.object_type = self.object_type
##        return obj
##
##    def deep_copy(self):
##        obj = MapObject(self.editor, "", self.name, self.factor,
##                        list(self.relpos), new_type=False)
##        obj.original_img = self.original_img.copy()
##        obj.imgs = [i.copy() for i in self.imgs]
##        obj.min_relpos = list(self.min_relpos)
##        obj.max_relpos = list(self.max_relpos)
##        obj.object_type = self.object_type
##        return obj
##
##
##    def flip(self, x=True, y=False):
##        obj = self.deep_copy()
##        obj.original_img = pygame.transform.flip(obj.original_img, x, y)
##        for i in range(len(obj.imgs)):
##            obj.imgs[i] = pygame.transform.flip(obj.imgs[i], x, y)
##        return obj
##
##    def add_copy_on_cell(self, cell):
##        copy = self.copy()
##        copy.cell = cell
##        cell.objects.append(copy)
##        return copy
##
##    def add_unit_on_cell(self, cell):
##        assert cell.unit is None
##        copy = self.copy()
##        copy.cell = cell
##        cell.unit = copy
##        return copy
##
##    def build_imgs(self):
##        W,H = self.original_img.get_size()
##        w0 = float(self.editor.zoom_cell_sizes[0])
##        imgs = []
##        for w in self.editor.zoom_cell_sizes:
##            factor = w/w0
##            zoom_size = (int(factor*W), int(factor*H))
##            img = pygame.transform.scale(self.original_img, zoom_size)
##            imgs.append(img)
##        self.imgs = imgs
##
##    def get_current_img(self):
##        return self.imgs[self.cell.map.current_zoom_level]
##
##    def set_same_type(self, objs):
##        for o in objs:
##            o.object_type = self.object_type


class MapObject:
    current_id = 1

    def __init__(self, editor, fns, name="", factor=1., relpos=(0,0), build=True,
                 new_type=True):
        """Object that looks the same at each frame"""
        self.editor = editor
        ref_size = editor.zoom_cell_sizes[0]
        self.frame_imgs = []
        self.original_imgs = []
        if isinstance(fns, str):
            fns = [fns]
        for thing in fns:
            if thing:
                if isinstance(thing,str):
                    img = thorpy.load_image(thing, colorkey=(255,255,255))
                else:
                    img = thing
                img = thorpy.get_resized_image(img, (factor*ref_size,)*2)
            else:
                img = None
            self.frame_imgs.append(img)
            self.original_imgs.append(img)
        self.nframes = len(self.original_imgs)
        self.factor = factor
        self.relpos = [0,0]
        self.imgs_z_t = None
        self.cell = None
        self.name = name
        self.ncopies = 0
        self.min_relpos = [-0.4, -0.4]
        self.max_relpos = [0.4,   0.4]
        self.quantity = 1 #not necessarily 1 for units
        if build and thing:
            self.build_imgs()
        if new_type:
            self.object_type = MapObject.current_id
            MapObject.current_id += 1
        else:
            self.object_type = None

    def ypos(self):
        h = self.original_imgs[0].get_size()[1]
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
        obj = MapObject(self.editor, [""], self.name, self.factor,
                        list(self.relpos), new_type=False)
        obj.original_imgs = self.original_imgs
        obj.nframes = self.nframes
        obj.imgs_z_t = self.imgs_z_t
        obj.min_relpos = list(self.min_relpos)
        obj.max_relpos = list(self.max_relpos)
        obj.object_type = self.object_type
        return obj

    def deep_copy(self):
        obj = MapObject(self.editor, [""], self.name, self.factor,
                        list(self.relpos), new_type=False)
        obj.original_imgs = [i.copy() for i in self.original_imgs]
        obj.nframes = len(obj.original_imgs)
        obj.imgs_z_t = []
        for frame in range(len(self.imgs_z_t)):
            obj.imgs_z_t.append([])
            for scale in range(len(self.imgs_z_t[frame])):
                obj.imgs_z_t[frame].append(self.imgs_z_t[frame][scale].copy())
##        for imgs in self.imgs_z_t:
##            obj.imgs_z_t = [i.copy() for i in imgs]
        obj.min_relpos = list(self.min_relpos)
        obj.max_relpos = list(self.max_relpos)
        obj.object_type = self.object_type
        return obj


    def flip(self, x=True, y=False):
        obj = self.deep_copy()
        obj.original_imgs = [pygame.transform.flip(i, x, y) for i in obj.original_imgs]
        for frame in range(len(obj.imgs_z_t)):
            for scale in range(len(obj.imgs_z_t[frame])):
                obj.imgs_z_t[frame][scale] = pygame.transform.flip(obj.imgs_z_t[frame][scale], x, y)
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

##    def build_imgs(self):
##        self.imgs_z_t = [] #list of list of images - idx0:scale, idx1:frame
##        for img in self.original_imgs: #loop over frames
##            W,H = img.get_size()
##            w0 = float(self.editor.zoom_cell_sizes[0])
##            imgs = []
##            for w in self.editor.zoom_cell_sizes: #loop over sizes
##                factor = w/w0
##                zoom_size = (int(factor*W), int(factor*H))
##                img = pygame.transform.scale(img, zoom_size)
##                imgs.append(img)
##            self.imgs_z_t.append(imgs)

    def build_imgs(self):
        self.imgs_z_t = [] #list of list of images - idx0:scale, idx1:frame
        for w in self.editor.zoom_cell_sizes: #loop over sizes
            imgs = []
            for img in self.original_imgs: #loop over frames
                W,H = img.get_size()
                w0 = float(self.editor.zoom_cell_sizes[0])
                factor = w/w0
                zoom_size = (int(factor*W), int(factor*H))
                img = pygame.transform.scale(img, zoom_size)
                imgs.append(img)
            self.imgs_z_t.append(imgs)

    def get_current_img(self):
        return self.imgs_z_t[self.editor.zoom_level][self.cell.map.t%self.nframes]

    def set_same_type(self, objs):
        for o in objs:
            o.object_type = self.object_type



def distance(coord1, coord2):
    return abs(coord1[0]-coord2[0]) + abs(coord1[1]-coord2[1])




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

def add_random_river(me, layer,
                    img_fullsize,
                    costs_materials, costs_objects,
                    possible_materials, possible_objects):
    """Computes and draw a random river."""
    lm = me.lm
    #0)build tiles
    imgs = {}
    for dx in [-1,0,1]:
        for dy in[-1,0,1]:
            imgs[(dx,dy)] = tm.build_tiles(img_fullsize, lm.cell_sizes,
                                            lm.nframes,
                                            dx*lm.nframes, dy*lm.nframes, #dx, dy
                                            sin=False)
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
    #2) change the end to first shallow cell
    actual_path = []
    for cell in path: #mettre riviere qui bouge (mais besoin d'objets frames)
        actual_path.append(cell)
        if "water" in cell.material.name.lower():
            break
        else:
            next_to_water = False
            for neigh in cell.get_neighbors_von_neuman():
                if neigh:
                    if "water" in neigh.material.name.lower():
                        next_to_water = True
                        break
            if next_to_water:
                break

    #
    objs = {}
    for key in imgs:
        objs[key] = MapObject(me, imgs[key][0], "River", 1.)
    #3) add river cells to map and layer
    for i,cell in enumerate(actual_path):
        dx, dy = 0, 0
        if i > 0:
            dx += cell.coord[0] - actual_path[i-1].coord[0]
            dy += cell.coord[1] - actual_path[i-1].coord[1]
        if i + 1 < len(actual_path):
            dx += actual_path[i+1].coord[0] - cell.coord[0]
            dy += actual_path[i+1].coord[1] - cell.coord[1]
        if dx > 0:
            dx = 1
        elif dx < 0:
            dx = -1
        if dy > 0:
            dy = 1
        elif dy < 0:
            dy = -1
        c = objs.get((dx,dy))
        if not c:
            raise Exception("No river object for delta", dx, dy)
        c = c.add_copy_on_cell(cell)
        cell.name = "River"
        layer.static_objects.append(c)
    return path



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
