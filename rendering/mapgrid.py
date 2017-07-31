import pygame
from thorpy.gamestools.grid import PygameGrid
from rendering.tilers.tilemanager import get_couple

#pour eviter de tj faire des tuples, ne pas heriter de PygameGrid et faire moi meme

from thorpy import Monitor
monitor = Monitor()

WATER = 1
GRASS = 0

class Cell:

    def __init__(self, h, coord, material_couples):
        self.couple = get_couple(h, material_couples)
        self.tilers = self.couple.tilers
        self.h = h
        self.coord = coord
        if h > self.couple.transition:
            self.value = 0
            self.material = self.couple.grass
        else:
            self.value = 1
            self.material = self.couple.water
        self.type = None
        self.imgs = None
        self.name = ""


    def get_altitude(self):
        return (self.h-0.6)*2e4

    def get_img(self): #todo
        pass

class MapGrid(PygameGrid):

    def __init__(self, hmap, material_couples, actual_frame, restrict_size=None):
        cell_size = material_couples[0].cell_size
        self.actual_frame = actual_frame
        if restrict_size is None:
            nx, ny = len(hmap), len(hmap[0])
        else:
            nx, ny= restrict_size
        PygameGrid.__init__(self, nx, ny,
                cell_size=(cell_size, cell_size),
                topleft=actual_frame.topleft,
                value=None)
        self.refresh_cell_heights(hmap, material_couples)
        self.black_img = pygame.Surface((cell_size,cell_size))
        self.current_x = 0
        self.current_y = 0
        #
        self.nframes = len(material_couples[0].tilers)
        self.t = 0
        self.tot_time = 0
        self.frame_slowness = 20

    def next_frame(self):
        self.tot_time += 1
        if self.tot_time % self.frame_slowness == 0:
            self.t = (self.t+1) % self.nframes
            return True

    def refresh_cell_heights(self, hmap, material_couples):
##        assert len(hmap) == self.nx and len(hmap[0]) == self.ny
        for x,y in self:
            self[x,y] = Cell(hmap[x][y], (x,y), material_couples)

    def get_cell_at(self, x,y):
        if self.is_inside((x,y)):
            return self[x,y]
        else:
            return None

    def get_neighbour_value_at(self, x, y, x0, y0):
        neighbour = self.get_cell_at(x,y)
        origin = self[x0,y0]
        if neighbour is None:
            return origin.value #then returns the same as demanding
        else:
            if neighbour.material is origin.material:
                return origin.value
            elif neighbour.material.hmax > origin.material.hmax:
                return GRASS
            else:
                return WATER

    def refresh_cell_types(self):
        for x,y in self:
            cell = self[x,y]
            if cell.value == GRASS:
                t = self.get_neighbour_value_at(x,y-1,x,y)
                b = self.get_neighbour_value_at(x,y+1,x,y)
                l = self.get_neighbour_value_at(x-1,y,x,y)
                r = self.get_neighbour_value_at(x+1,y,x,y)
                n = t*"t" + b*"b" + l*"l" + r*"r"
                if not n:
                    n = "c"
                tl = self.get_neighbour_value_at(x-1,y-1,x,y)
                tr = self.get_neighbour_value_at(x+1,y-1,x,y)
                bl = self.get_neighbour_value_at(x-1,y+1,x,y)
                br = self.get_neighbour_value_at(x+1,y+1,x,y)
                if tl and not(t) and not(l):
                    n += "k"
                if tr and not(t) and not(r):
                    n += "x"
                if bl and not(b) and not(l):
                    n += "y"
                if br and not(b) and not(r):
                    n += "z"
                cell.type = n
            else:
                cell.type = "s"
            cell.imgs = [cell.tilers[t].imgs[cell.type] for t in range(self.nframes)]

    def draw_cell(self, screen, xpix, ypix, coord, x0, y0):
        x,y = coord
        if self.is_inside(coord):
            img = self[coord].imgs[self.t]
        else:
            img = self.black_img
        rect = self.get_rect_at_coord((x-x0,y-y0))
        rect.move_ip(-xpix, -ypix)
        screen.blit(img, rect)

    def draw(self, screen, xpix, ypix, x0, w, y0, h):
        x0 -= 1
        y0 -= 1
        w += 1
        h += 1
        for x in range(x0,x0+w):
            for y in range(y0,y0+h):
                self.draw_cell(screen, xpix, ypix, (x,y), x0, y0)

    def show(self):
        monitor.show()
