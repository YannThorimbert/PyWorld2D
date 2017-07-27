import pygame
from thorpy.gamestools.grid import PygameGrid

#pour eviter de tj faire des tuples, ne pas heriter de PygameGrid et faire moi meme

from thorpy import Monitor
monitor = Monitor()

WATER = 1
GRASS = 0

VON_NEUMANN = [(1, 0), (-1, 0), (0, 1), (0, -1)]
MOORE = [(1, 1), (1, -1), (-1, 1), (-1, -1)] + VON_NEUMANN

def get_material(h):
    if h < 0.6:
        return WATER
    else:
        return GRASS

class Cell:

    def __init__(self, h):
        self.h = h
        self.material = get_material(h)
        self.type = None

class MapGrid(PygameGrid):

    def __init__(self, hmap, cell_size, topleft=(0,0)):
        PygameGrid.__init__(self, len(hmap), len(hmap[0]),
                cell_size=(cell_size, cell_size), topleft=topleft, value=None)
        self.refresh_cell_heights(hmap)
        self.black_img = pygame.Surface((cell_size,cell_size))
        self.current_x = 0
        self.current_y = 0

    def refresh_cell_heights(self, hmap):
        assert len(hmap) == self.nx and len(hmap[0]) == self.ny
        for x,y in self:
            self[x,y] = Cell(hmap[x][y])

    def get_cell_at(self, x,y):
        if self.is_inside((x,y)):
            return self[x,y]
        else:
            return None

    def get_cell_material_at(self, x, y, x0, y0):
        cell = self.get_cell_at(x,y)
        if cell is None:
            return self[x0,y0].material
        return cell.material

    def refresh_cell_types(self):
        for x,y in self:
            if self[x,y].material == GRASS:
                t = self.get_cell_material_at(x,y-1,x,y)
                b = self.get_cell_material_at(x,y+1,x,y)
                l = self.get_cell_material_at(x-1,y,x,y)
                r = self.get_cell_material_at(x+1,y,x,y)
                n = t*"t" + b*"b" + l*"l" + r*"r"
                if not n:
                    n = "c" #remplacer "c" par "" dans tiler!
                #
                tl = self.get_cell_material_at(x-1,y-1,x,y)
                tr = self.get_cell_material_at(x+1,y-1,x,y)
                bl = self.get_cell_material_at(x-1,y+1,x,y)
                br = self.get_cell_material_at(x+1,y+1,x,y)
                if tl and not(t) and not(l):
                    n += "k"
                if tr and not(t) and not(r):
                    n += "x"
                if bl and not(b) and not(l):
                    n += "y"
                if br and not(b) and not(r):
                    n += "z"
                self[x,y].type = n
            else:
                self[x,y].type = "s"

    def draw_cell(self, screen, xpix, ypix, coord, x0, y0, imgs):
        x,y = coord
        if self.is_inside(coord):
            img = imgs[self[coord].type]
        else:
            img = self.black_img
        rect = self.get_rect_at_coord((x-x0,y-y0))
        rect.move_ip(-xpix, -ypix)
        screen.blit(img, rect)

    def draw(self, screen, xpix, ypix, x0, w, y0, h, imgs):
        x0 -= 1
        y0 -= 1
        w += 1
        h += 1
        for x in range(x0,x0+w):
            for y in range(y0,y0+h):
                self.draw_cell(screen, xpix, ypix, (x,y), x0, y0, imgs)

    def show(self):
        monitor.show()
