import pygame
from thorpy.gamestools.basegrid import BaseGrid
from thorpy.gamestools.grid import PygameGrid
from rendering.tilers.tilemanager import get_couple

#pour eviter de tj faire des tuples, ne pas heriter de PygameGrid et faire moi meme

WATER = 1
GRASS = 0

##from thorpy import Monitor
##monitor = Monitor()


class LogicalCell:

    def __init__(self, h, coord, logical_map):
        self.map = logical_map
        self.couple = get_couple(h, self.map.material_couples)
        self.h = h
        self.coord = coord
        if h > self.couple.transition:
            self.value = GRASS
            self.material = self.couple.grass
        else:
            self.value = WATER
            self.material = self.couple.water
        self.type = None
        self.name = ""
        self.objects = []
        self.spec_imgs = None

    def get_altitude(self):
        return (self.h-0.6)*2e4

##    def get_img(self):
##        return self.map.get_img_at(self.coord)

    def get_img_at_zoom(self, level):
        return self.map.get_img_at_zoom(self.coord, level)



class GraphicalCell:

    def __init__(self):
        self.imgs = None

    def set_imgs(self, news):
        self.imgs = [img for img in news]


class LogicalMap(BaseGrid):

    def __init__(self, hmap, material_couples, actual_frames, outsides,
                    restrict_size=None):
        self.material_couples = material_couples
        self.zoom_levels = list(range(len(material_couples[0].tilers)))
        self.actual_frames = actual_frames
        if restrict_size is None:
            nx, ny = len(hmap), len(hmap[0])
        else:
            nx, ny = restrict_size
        BaseGrid.__init__(self, int(nx), int(ny))
        self.current_x = 0
        self.current_y = 0
        self.graphical_maps = []
        self.cell_sizes = []
        for z in self.zoom_levels:
            cell_size = material_couples[0].get_cell_size(z)
            gm = GraphicalMap(nx, ny, cell_size, actual_frames[z], outsides[z])
            self.graphical_maps.append(gm)
            self.cell_sizes.append(cell_size)
        self.current_gm = self.graphical_maps[0]
        #
        self.nframes = len(material_couples[0].get_tilers(0))
        self.t = 0
        self.tot_time = 0
        self.frame_slowness = 20

    def set_zoom(self, level):
        self.current_gm = self.graphical_maps[level]
        if self.current_x < 0:
            self.current_x = 0
        elif self.current_x > self.nx-2:
            self.current_x = self.nx-2
        if self.current_y < 0:
            self.current_y = 0
        elif self.current_y > self.ny-2:
            self.current_y = self.ny-2

    def next_frame(self):
        self.tot_time += 1
        if self.tot_time % self.frame_slowness == 0:
            self.t = (self.t+1) % self.nframes
            return True

    def refresh_cell_heights(self, hmap):
        for x,y in self:
            self[x,y] = LogicalCell(hmap[x][y], (x,y), self)


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
            for zoom, gm in enumerate(self.graphical_maps):
                gm[x,y].imgs = cell.couple.get_all_frames(zoom, cell.type)

    def draw_cell(self, screen, xpix, ypix, coord, x0, y0):
        x,y = coord
        img = self.get_img_at(coord)
        rect = self.current_gm.get_rect_at_coord((x-x0,y-y0))
        rect.move_ip(-xpix, -ypix)
        screen.blit(img, rect)

    def get_img_at(self, coord): #a utiliser dans draw_cell!
        if self.is_inside(coord):
            return self.current_gm[coord].imgs[self.t]
        else:
            return self.current_gm.outside_imgs[self.t]

    def get_img_at_zoom(self, coord, zoom):
        if self.is_inside(coord):
            return self.graphical_maps[zoom][coord].imgs[self.t]
        else:
            return self.graphical_maps[zoom].outside_imgs[self.t]

    def get_img(self, coord, zoom, frame):
        if self.is_inside(coord):
            return self.graphical_maps[zoom][coord].imgs[frame]
        else:
            return self.graphical_maps[zoom].outside_imgs[frame]

    def get_graphical_cell(self, coord, zoom):
        return self.graphical_maps[zoom][coord]

    def blit_on_cell(self, img, x, y, relx, rely):
        """relx and rely are the relative center coordinates"""
        cell_size0 = self.cell_sizes[0]
        wobj0, hobj0 = img.get_size()
        coord = (x,y)
        for zoom, cell_size in enumerate(self.cell_sizes):
            factor = float(cell_size) / cell_size0
            w = int(wobj0 * factor)
            h = int(hobj0 * factor)
            #no smoothscale because problems with colorkey
            obj_img = pygame.transform.scale(img, (w,h))
            obj_rect = obj_img.get_rect()
            obj_rect.center = (cell_size//2,)*2
            dx, dy = int(relx*cell_size), int(rely*cell_size)
            obj_rect.move_ip(dx,dy)
            #
            gc = self.get_graphical_cell(coord, zoom)
            new_imgs = []
            for original in gc.imgs:
                new_ = original.copy()
                new_.blit(obj_img, obj_rect.topleft)
                new_imgs.append(new_)
            gc.imgs = [new_ for new_ in new_imgs]

    def draw(self, screen, xpix, ypix, x0, w, y0, h):
        x0 -= 1
        y0 -= 1
        w += 1
        h += 1
        for x in range(x0,x0+w):
            for y in range(y0,y0+h):
                self.draw_cell(screen, xpix, ypix, (x,y), x0, y0)

##    def show(self):
##        monitor.show()


class GraphicalMap(PygameGrid):

    def __init__(self, nx, ny, cell_size, actual_frame, outside_imgs):
##        cell_size = material_couples[0].get_cell_size(zoom_level)
        self.actual_frame = actual_frame
        PygameGrid.__init__(self, int(nx), int(ny),
                            cell_size=(cell_size,)*2,
                            topleft=actual_frame.topleft)
        self.outside_imgs = outside_imgs
        for coord in self:
            self[coord] = GraphicalCell()
