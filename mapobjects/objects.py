import random
import pygame
import thorpy



def get_forest_distributor(me, imgdict, forest_map, material_names):
    """<imgdict> is a dict of the form:
                    {img_filename:(object_name, size_factor, also_flip)}"""
    objects = []
    ref_size = me.zoom_cell_sizes[0]
    for fn in imgdict:
        name, factor, flip = imgdict[fn]
        img = thorpy.load_image(fn, colorkey=(255,255,255))
        img = thorpy.get_resized_image(img, (factor*ref_size,)*2)
        obj = MapObject(me, img, name)
        obj.build_imgs()
        obj.max_relpos[1] = 0.
        objects.append(obj)
        if flip:
            objects.append(obj.get_flipped_true_copy())
    distributor = RandomObjectDistribution(objects, forest_map, me.lm)
    for name in material_names:
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


    def distribute_objects(self, layer):
        for x,y in self.master_map:
            h = self.hmap[x][y]
            right_h = False
            for heigth,spread in self.zones_spread:
                if abs(h-heigth) < spread:
                    right_h = True
                    break
            if right_h:
                cell = self.master_map.cells[x][y]
                if cell.material in self.materials:
                    for i in range(self.max_density):
                        if random.random() < self.homogeneity:
                            obj = random.choice(self.objs)
                            obj = obj.add_copy_on_cell(cell)
                            obj.randomize_relpos()
                            layer.static_objects.append(obj)

class MapObject:

    def __init__(self, editor, img, name="", relpos=(0,0)):
        """Object that looks the same at each frame"""
        self.editor = editor
        self.original_img = img
        self.relpos = [0,0]
        self.imgs = None
        self.cell = None
        self.name = name
        self.ncopies = 0
        self.min_relpos = [-0.5, -0.5]
        self.max_relpos = [0.5,   0.5]
        self.quantity = 1 #not necessarily 1 for units

    def randomize_relpos(self):
        self.relpos[0] = self.min_relpos[0] +\
                         random.random()*(self.max_relpos[0]-self.min_relpos[0])
        self.relpos[1] = self.min_relpos[1] +\
                         random.random()*(self.max_relpos[1]-self.min_relpos[1])

    def copy(self):
        self.ncopies += 1
        obj = MapObject(self.editor, self.original_img)
        obj.imgs = self.imgs
        if self.name:
            obj.name = self.name + " " + str(self.ncopies)
        obj.relpos = list(self.relpos)
        obj.min_relpos = list(self.min_relpos)
        obj.max_relpos = list(self.max_relpos)
        return obj

    def get_flipped_true_copy(self, x=True, y=False):
        img = pygame.transform.flip(self.original_img, x, y)
        obj = MapObject(self.editor, img)
        obj.name = self.name
        obj.build_imgs()
        obj.relpos = list(self.relpos)
        obj.min_relpos = list(self.min_relpos)
        obj.max_relpos = list(self.max_relpos)
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


