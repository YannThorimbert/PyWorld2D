import pygame
from pygame.math import Vector2 as V2


class Camera:

    def __init__(self):
        self.mg = None
        self.cell_rect = pygame.Rect(0,0,0,0)
        self.e_hmap = None
        self.box_hmap = None
        self.campos = V2()
        self.rcam = None
        self.rmouse = None
        self.world_size = V2()
        self.nx, self.ny = 0, 0

    def set_parameters(self, world_size, cell_size, viewport_rect, minimap_size):
        self.world_size = V2(world_size)
        self.cell_rect.size = (cell_size,)*2
        self.nx = viewport_rect.w//self.cell_rect.w - 1
        self.ny = viewport_rect.h//self.cell_rect.h - 1
        map_size = self.nx*self.cell_rect.w, self.ny*self.cell_rect.h
        self.map_rect = pygame.Rect((0,0), map_size)
        self.map_rect.center = viewport_rect.center
        self.rcam = pygame.Rect(0,0,self.nx,self.ny)
        w = int(self.nx*minimap_size[0]/self.world_size.x)
        h = int(self.ny*minimap_size[1]/self.world_size.y)
        self.rmouse = pygame.Rect(0,0,w,h)

    def set_map_data(self, mg):
        self.mg = mg
        assert mg.nx == self.world_size.x and mg.ny == self.world_size.y


    def get_dpix(self):
       x = (self.campos.x - self.rcam.x)*self.cell_rect.w
       y = (self.campos.y - self.rcam.y)*self.cell_rect.h
       return x,y

    def draw_grid(self, screen):
        xpix, ypix = self.get_dpix()
        #appeller self.mg.draw_current(xpix,ypix,self.nx,self.ny)
        self.mg.draw(screen, xpix, ypix, self.mg.current_x, self.nx, self.mg.current_y, self.ny)

    def set_mg_pos_from_rcam(self):
        self.mg.current_x = int(self.rcam.x)
        self.mg.current_y = int(self.rcam.y)

    def set_campos_from_rcam(self):
        self.campos = V2(self.rcam.topleft)

    def set_rcam_from_campos(self):
        self.rcam.topleft = self.campos

    def set_rcam_from_rmouse(self):
        rminimap = self.e_hmap.get_rect()
        self.rcam.x = (self.rmouse.x - rminimap.x)*self.world_size.x/rminimap.w
        self.rcam.y = (self.rmouse.y - rminimap.y)*self.world_size.y/rminimap.h

    def set_rmouse_from_rcam(self):
        rminimap = self.e_hmap.get_rect()
        self.rmouse.x = self.rcam.x*rminimap.w/self.world_size.x + rminimap.x
        self.rmouse.y = self.rcam.y*rminimap.h/self.world_size.y + rminimap.y

    def move(self, delta):
        self.campos += delta
        self.set_rcam_from_campos()

    def get_cell(self, pix):
        if self.map_rect.collidepoint(pix):
            coord = self.get_coord_at_pix(pix)
            if self.mg.is_inside(coord):
                return self.mg[coord]

    def center_on(self, minimap_pos):
        if self.box_hmap.get_rect().collidepoint(minimap_pos):
            self.rmouse.center = minimap_pos
            self.set_rcam_from_rmouse()
            self.set_mg_pos_from_rcam()
            self.set_campos_from_rcam()

    def correct_move(self, d):
        dx, dy = d
        mg = self.mg
        if mg.current_x + self.nx > mg.nx + 2 and dx > 0:
            dx = 0
        elif mg.current_x < -2 and dx < 0:
            dx = 0
        if mg.current_y + self.ny > mg.ny + 2 and dy > 0:
            dy = 0
        elif mg.current_y < -2 and dy < 0:
            dy = 0
        return dx, dy

    def get_rect_at_coord(self, coord):
        dx, dy = self.get_dpix()
        shift_x = (coord[0] - self.mg.current_x + 1) * self.cell_rect.w - int(dx)
        shift_y = (coord[1] - self.mg.current_y + 1) * self.cell_rect.h - int(dy)
        return self.cell_rect.move((shift_x, shift_y)).move(self.map_rect.topleft)

    def get_coord_at_pix(self, pix):
        pos = V2(self.get_dpix()) + pix - self.map_rect.topleft
        pos.x *= self.nx/self.map_rect.w
        pos.y *= self.ny/self.map_rect.h
        return (int(pos.x) + self.mg.current_x - 1,
                int(pos.y) + self.mg.current_y - 1)

    def get_rect_at_pix(self, pix):
        return self.get_rect_at_coord(self.get_coord_at_pix(pix))