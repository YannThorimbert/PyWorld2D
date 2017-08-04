import pygame.math.Vector2 as V2


class MapObject:

    def __init__(self, img, cell, relpos):
        self.img = img
        self.cell = cell
        self.relpos = V2(relpos)

    def get_relpos(self, cellsize):
        return self.relpos * cellsize

    def apply_to_cell(self):
        img = self.cell.get_img0
        self.cell.