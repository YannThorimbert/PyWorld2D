import math
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
        self.imgs = None

    def get_altitude(self):
        return (self.h-0.6)*2e4

    def get_img_at_zoom(self, level):
        return self.map.get_img_at_zoom(self.coord, level)

    def extract_all_layers_img_at_zoom(self, level):
        return self.map.extract_all_layers_img_at_zoom(self.coord, level)

class WhiteLogicalCell:

    def __init__(self, logical_map):
        self.map = logical_map
        self.imgs = None

    def get_img_at_zoom(self, level):
        return self.map.get_img_at_zoom(self.coord, level)


class GraphicalCell:

    def __init__(self):
        self.imgs = None



class LogicalMap(BaseGrid):

    def __init__(self, hmap, material_couples, actual_frames, outsides,
                    restrict_size):
        self.material_couples = material_couples
        self.zoom_levels = list(range(len(material_couples[0].tilers)))
        self.current_zoom_level = 0
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
        self.layers = []
        #
        self.nframes = len(material_couples[0].get_tilers(0))
        self.t = 0
        self.tot_time = 0
        self.frame_slowness = 20
        #
        self.refresh_cell_heights(hmap)
        self.refresh_cell_types()
        self.colorkey = None #used at build_surface()
        self.static_objects = []

    def add_layer(self, lay):
        lay.frame_slowness = self.frame_slowness
        self.layers.append(lay)

    def get_current_cell_size(self):
        return self.cell_sizes[self.current_zoom_level]

    def set_zoom(self, level):
        self.current_zoom_level = level
        self.current_gm = self.graphical_maps[level]
        if self.current_x < 0:
            self.current_x = 0
        elif self.current_x > self.nx-2:
            self.current_x = self.nx-2
        if self.current_y < 0:
            self.current_y = 0
        elif self.current_y > self.ny-2:
            self.current_y = self.ny-2
        for lay in self.layers:
            lay.set_zoom(level)

    def next_frame(self):
        self.tot_time += 1
        if self.tot_time % self.frame_slowness == 0:
            self.t = (self.t+1) % self.nframes
            for lay in self.layers:
                lay.t = self.t
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


    def get_img_at_zoom(self, coord, zoom):
        """Returns the image contained on permanent cell of self.
        Use extract_img_at_zoom if you need the cell plus all what has been
        drawn on self's surface."""
        if self.is_inside(coord):
            return self.graphical_maps[zoom][coord].imgs[self.t]
        else:
            return self.graphical_maps[zoom].outside_imgs[self.t]

    def extract_img_at_zoom(self, coord, zoom, img):
        """Returns the image of the cell of self plus what has been drawn on
        self's surface.
        Use get_img_at_zoom if you need the cell only."""
        if self.is_inside(coord):
            self.graphical_maps[zoom].extract_img(coord, self.t, img)
        else:
            img.blit(self.graphical_maps[zoom].outside_imgs[self.t],(0,0))

    def extract_all_layers_img_at_zoom(self, coord, zoom):
        """Fusion all the images extracted from all the layers of self."""
        if self.is_inside(coord):
            img = pygame.Surface((self.cell_sizes[zoom],)*2)
            img.blit(self.get_img_at_zoom(coord, zoom), (0,0)) #I dont know why I have to do that to avoir bug of spurious static objects...
            for lay in self.layers:
                lay.extract_img_at_zoom(coord, zoom, img)
            return img
        else:
            img = self.graphical_maps[zoom].outside_imgs[self.t]
            for lay in self.layers:
                img.blit(lay[coord].imgs[self.t], (0,0))
            return img


    def get_graphical_cell(self, coord, zoom):
        return self.graphical_maps[zoom][coord]

    def draw_on_cell(self, img, x, y, relx, rely): #used for dynamic objects
        """relx and rely are the relative center coordinates"""
        cell_size0 = self.cell_sizes[0]
        wobj0, hobj0 = img.get_size()
        coord = (x,y)
##        self.cells[x][y].objects.append("lol")
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


    def draw(self, screen, topleft, dx_pix, dy_pix):
        x0 = self.current_x
        y0 = self.current_y
        self.current_gm.draw(screen, topleft, x0, y0, dx_pix, dy_pix, self.t)

    def build_surfaces(self):
        for gm in self.graphical_maps:
            gm.build_surfaces(self.colorkey)

    def blit_img(self, imgs, coord, relpos): #this is permanent
        """Permanently blit images <imgs> corresponding to different zoom levels
        onto self's surfaces."""
        for level, gm in enumerate(self.graphical_maps):
            gm.blit_img(imgs[level], coord, relpos)

    def save_pure_surfaces(self):
        for gm in self.graphical_maps:
            gm.save_pure_surfaces()

    def reset_pure_surfaces(self):
        for gm in self.graphical_maps:
            gm.surfaces = gm.pure_surfaces
            gm.save_pure_surfaces()

    def blit_objects(self, objects=None): #this is permanent
        if objects is None:
            objects = self.static_objects
        for obj in objects:
            self.blit_img(obj.imgs, obj.cell.coord, obj.relpos)

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
        self.cell_size = cell_size
        for coord in self:
            self[coord] = GraphicalCell()
        self.surfaces = None
        self.pure_surfaces = None #surfaces with no objects
        self.surf_size = None
        self.nsurf_x = None
        self.nsurf_y = None

    def build_surfaces(self, colorkey):
        #heuristic
        nx = int(200/self.cell_size)
        ny = int(200/self.cell_size)
        nframes = len(self[(0,0)].imgs)
        size_x = nx*self.cell_size
        size_y = ny*self.cell_size
        surf_size = (size_x, size_y)
        nsurf_x = self.frame.w//size_x + 1
        nsurf_y = self.frame.h//size_y + 1
        #create table of surfaces
        surfaces = [[[pygame.Surface(surf_size) for frame in range(nframes)]
                        for y in range(nsurf_y)]
                          for x in range(nsurf_x)]
        #fill table of surfaces
        for x,y in self:
            surfx = x*self.cell_size//surf_size[0]
            surfy = y*self.cell_size//surf_size[1]
            xpix = x*self.cell_size - surfx*surf_size[0]
            ypix = y*self.cell_size - surfy*surf_size[1]
##            print(x, size_x, nsurf_x, surfx)
            for t in range(nframes):
                img = self[(x,y)].imgs[t]
                surfaces[surfx][surfy][t].blit(img, (xpix,ypix))
                if colorkey is not None:
                    surfaces[surfx][surfy][t].set_colorkey(colorkey)
        #
        self.surfaces = surfaces
        self.surf_size = surf_size
        self.nsurf_x = nsurf_x
        self.nsurf_y = nsurf_y

    def save_pure_surfaces(self):
        self.pure_surfaces = []
        for x in range(len(self.surfaces)):
            self.pure_surfaces.append([])
            for y in range(len(self.surfaces[0])):
                self.pure_surfaces[x].append([])
                for t in range(len(self.surfaces[0][0])):
                    self.pure_surfaces[x][y].append(None)
                    self.pure_surfaces[x][y][t] = self.surfaces[x][y][t].copy()


    def blit_img(self, obj_img, obj_coord, relpos):
        """blit image <obj_img> on self's surface"""
        xobj, yobj = obj_coord
        obj_rect = obj_img.get_rect()
        obj_rect.center = (self.cell_size//2,)*2
        dx, dy = int(relpos[0]*self.cell_size), int(relpos[1]*self.cell_size)
        obj_rect.move_ip(dx,dy)
        #heuristic
        nx = int(200/self.cell_size)
        ny = int(200/self.cell_size)
        nframes = len(self[(0,0)].imgs)
        size_x = nx*self.cell_size
        size_y = ny*self.cell_size
        surf_size = (size_x, size_y)
        nsurf_x = self.frame.w//size_x + 1
        nsurf_y = self.frame.h//size_y + 1
        #fill table of surfaces
        surfx = xobj*self.cell_size//surf_size[0]
        surfy = yobj*self.cell_size//surf_size[1]
        xpix = xobj*self.cell_size - surfx*surf_size[0] + obj_rect.x
        ypix = yobj*self.cell_size - surfy*surf_size[1] + obj_rect.y
        for t in range(nframes):
            for dx in range(-1,2):
                for dy in range(-1,2):
                    cx,cy = surfx+dx, surfy+dy
                    if 0 <= cx < nsurf_x and 0 <= cy <nsurf_y:
                        x = xpix - dx*surf_size[0]
                        y = ypix - dy*surf_size[1]
                        self.surfaces[cx][cy][t].blit(obj_img, (x,y))

    def draw(self, screen, topleft, x0, y0, xpix, ypix, t):
        delta_x = topleft[0] - xpix - x0*self.cell_size
        delta_y = topleft[1] - ypix - y0*self.cell_size
        oldposx = delta_x
        for x in range(self.nsurf_x):
            posx = round(x*self.surf_size[0] + delta_x)
            for y in range(self.nsurf_y):
                posy = round(y*self.surf_size[1] + delta_y)
                screen.blit(self.surfaces[x][y][t], (posx,posy))

    def extract_img(self, coord, frame, img):
        """blit (onto <img>) self'surface cell at <coord>"""
        nx = int(200/self.cell_size)
        ny = int(200/self.cell_size)
        size_x = nx*self.cell_size
        size_y = ny*self.cell_size
        surfx = coord[0]*self.cell_size//size_x
        surfy = coord[1]*self.cell_size//size_y
        xpix = coord[0]*self.cell_size - surfx*size_x
        ypix = coord[1]*self.cell_size - surfy*size_y
        img.blit(self.surfaces[surfx][surfy][frame], (-xpix, -ypix))
##        if coord[1] == 7:
##            import thorpy
##            app = thorpy.get_application()
##            app.fill((255,255,255))
##            screen = thorpy.get_screen()
##            screen.blit(img, (0,0))
##            app.update()
##            print(xpix, ypix, coord)
##            app.pause()


class WhiteLogicalMap(LogicalMap):

    def __init__(self, actual_frames, outsides, zoom_sizes, nframes,
                    restrict_size, white_value=(255,255,255)):
        self.zoom_levels = list(range(len(zoom_sizes)))
        self.current_zoom_level = 0
        self.cell_sizes = zoom_sizes
        self.actual_frames = actual_frames
        nx, ny = restrict_size
        BaseGrid.__init__(self, int(nx), int(ny))
        self.current_x = 0
        self.current_y = 0
        self.graphical_maps = []
        self.whites = []
        self.white_value = white_value
        for z in self.zoom_levels:
            cell_size = self.cell_sizes[z]
            gm = GraphicalMap(nx, ny, cell_size, actual_frames[z], outsides[z])
            self.graphical_maps.append(gm)
            white = pygame.Surface((cell_size,)*2)
            white.fill(self.white_value)
            self.whites.append(white)
        self.current_gm = self.graphical_maps[0]
        self.layers = []
        #
        self.nframes = nframes
        self.t = 0
        self.tot_time = 0
        self.frame_slowness = 20
        #
        self.refresh_cell_heights()
        self.refresh_cell_types()
        self.colorkey = white_value
        self.static_objects = []

    def refresh_cell_heights(self):
        for x,y in self:
            self[x,y] = WhiteLogicalCell(self)

    def refresh_cell_types(self):
        for x,y in self:
            cell = self[x,y]
            for zoom_level, gm in enumerate(self.graphical_maps):
                gm[x,y].imgs = [self.whites[zoom_level] for i in range(self.nframes)]


