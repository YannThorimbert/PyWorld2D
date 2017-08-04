import random
import pygame


class MapObject:

    def __init__(self, img, name="", relpos=(0,0)):
        """Object that looks the same at each frame"""
        self.original_img = img
        self.relpos = (0,0)
        self.imgs = None
        self.cell = None
        self.name = name
        self.ncopies = 0

    def randomize_relpos(self):
        self.relpos = -0.5 + random.random(), -0.5 + random.random()

    def copy(self):
        self.ncopies += 1
        obj = MapObject(self.original_img)
        obj.imgs = self.imgs
        if self.name:
            obj.name = self.name + " " + str(self.ncopies)
        return obj

    def add_copy_on_cell(self, cell, relpos=(0,0)):
        copy = self.copy()
        copy.relpos = relpos
        copy.cell = cell
        cell.objects.append(copy)
        return copy

    def build_imgs(self, sizes):
        W,H = self.original_img.get_size()
        w0 = float(sizes[0])
        imgs = []
        for w in sizes:
            factor = w/w0
            zoom_size = (int(factor*W), int(factor*H))
            img = pygame.transform.scale(self.original_img, zoom_size)
            imgs.append(img)
        self.imgs = imgs

    def get_current_img(self):
        return self.imgs[self.cell.map.current_zoom_level]


