import random
import pygame


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
        self.max_relpos = [0.5, 0.5]

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

    def add_copy_on_cell(self, cell):
        copy = self.copy()
        copy.cell = cell
        cell.objects.append(copy)
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


