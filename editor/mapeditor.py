import math, random
import pygame
from pygame.math import Vector2 as V2
import thorpy
import thornoise.purepython.noisegen as ng
import rendering.tilers.tilemanager as tm
from rendering.mapgrid import LogicalMap, WhiteLogicalMap
import gui.parameters as guip
import gui.elements as gui
from rendering.camera import Camera
import saveload.io as io

class MapEditor:

    def __init__(self):
        self.screen = thorpy.get_screen()
        self.W, self.H = self.screen.get_size() #screen size, wont change
        #values below are default values; they can change and
        # self.refresh_derived_parameters() must be called
        self.fps = 80
        self.box_hmap_margin = 20 #box of the minimap
        self.menu_width = 200
        self.zoom_cell_sizes = [20,16,10]
        self.nframes = 16 #number of different tiles for one material (used for moving water)
        self.max_wanted_minimap_size = 128 #in pixels.
        #
        self.lm = None
        self.cam = None #camera, to be built later
        self.map_rects = None
        self.zoom_level = 0
        self.materials = {}
        self.material_couples = None
        #
        self.cursor_color = (255,255,0)
        self.cursors = None
        self.idx_cursor = 0
        self.img_cursor = None
        self.cursor_slowness = None


    def build_map(self, hmap, desired_world_size):
        outsides = self.materials["outside"].imgs
        self.lm = LogicalMap(hmap, self.material_couples, self.map_rects,
                             outsides, desired_world_size)
        return self.lm

    def set_map(self, logical_map):
        self.cam.set_map_data(logical_map)

    def add_layer(self, white_value=(255,255,255)):
        outsides = self.materials["outside"].imgs
        lay = WhiteLogicalMap(self.map_rects, outsides, self.lm.cell_sizes,
                                self.nframes, self.cam.world_size, white_value)
##        lay = WhiteLogicalMap(hmap, map_rects, outsides, desired_world_size,
##                                white_value=white_value)
        self.lm.add_layer(lay)
        return lay


    def build_camera(self, img_hmap):
        cam = Camera()
        map_rects = []
        for level in range(len(self.zoom_cell_sizes)):
            self.zoom_level = level
            self.refresh_derived_parameters()
            cam.set_parameters(self.cell_size, self.viewport_rect, img_hmap,
                                self.max_minimap_size)
            map_rects.append(pygame.Rect(cam.map_rect))
        self.zoom_level = 0
        self.refresh_derived_parameters()
        cam.set_parameters(self.cell_size, self.viewport_rect, img_hmap,
                                self.max_minimap_size)
        self.cam = cam
        self.map_rects = map_rects


    def build_surfaces(self):
        self.lm.build_surfaces()
        for lay in self.lm.layers:
            lay.build_surfaces()
             #save BEFORE we blit objects (unless we want the objects to be part of the permanent map)
            lay.save_pure_surfaces()
            lay.blit_objects()
        #
        self.cursors = gui.get_cursors(self.cell_rect.inflate((2,2)),
                                        self.cursor_color)
        self.idx_cursor = 0
        self.img_cursor = self.cursors[self.idx_cursor]
        self.cursor_slowness = int(0.3*self.fps)


    def set_zoom(self, level):
        center_before = cam.get_center_coord()
        self.zoom_level = level
        refresh_derived_constants()
        cam.set_parameters(self.cell_size,
                            self.viewport_rect,
                            img_hmap,
                            self.max_minimap_size)
        lm.set_zoom(level)
        cam.reinit_pos()
        move_cam_and_refresh((center_before[0]-cam.nx//2,
                                center_before[1]-cam.ny//2))
        #cursor
        self.cursors = gui.get_self.cursors(self.cell_rect.inflate((2,2)),
                                            (255,255,0))
        self.self.idx_cursor = 0
        self.img_cursos = self.cursors[self.self.idx_cursor]
        #
        unblit_map()
        draw_no_update()



    def increment_zoom(self, value):
        self.zoom_level += value
        self.zoom_level %= len(self.zoom_cell_sizes)
        set_zoom(self.zoom_level)

    def update_cell_info(self):
        mousepos = pygame.mouse.get_pos()
        cell = cam.get_cell(mousepos)
        if cell:
    ##        pygame.draw.rect(screen, (0,0,0), get_rect_at_pix(mousepos), 1)
            rcursor = self.img_cursos.get_rect()
            rcursor.center = cam.get_rect_at_pix(mousepos).center
            screen.blit(self.img_cursos, rcursor)
            if cell_info.cell is not cell:
                cell_info.update_e(cell)
    ##        if cell.objects:
    ##            print(cell.objects)

    def unblit_map(self):
        pygame.draw.rect(screen, (0,0,0), cam.map_rect)

    def draw(self):
        cam.set_rmouse_from_rcam()
        #blit map frame
        screen.fill((0,0,0))
        #blit map
        cam.draw_grid(screen)
        #blit grid
        if show_grid_lines:
            cam.draw_grid_lines(screen)
        #blit objects
        cam.draw_objects(screen, dynamic_objects)
        #update right pane
        update_cell_info()
        #blit right pane and draw rect on minimap
        box.blit()
        pygame.draw.rect(screen, (255,255,255), cam.rmouse, 1)

    def draw_no_update(self):
        cam.draw_grid(screen)
        box.blit()
        pygame.draw.rect(screen, (255,255,255), cam.rmouse, 1)

    def func_reac_time(self):
        process_mouse_navigation()
        draw()
        ap.refresh()
        ap.draw(screen, 20,20)
        pygame.display.flip()
        #
        lm.next_frame()
        if lm.tot_time%cursor_slowness == 0:
            self.idx_cursor = (self.idx_cursor+1)%len(self.cursors)
            self.img_cursos = self.cursors[self.idx_cursor]


    def func_reac_click(self, e):
        if e.button == 1: #left click
            if box_hmap.get_rect().collidepoint(e.pos):
                cam.center_on(e.pos)
        elif e.button == 3: #right click
            print("Uh")
            increment_zoom(1)

    def func_reac_unclick(self, e):
        if e.button == 1:
            cell = cam.get_cell(e.pos)
            if cell:
                if cell is not self.last_cell_clicked:
                    if not cell_info.launched:
                        self.last_cell_clicked = cell
                        cell_info.launch_em(cell, e.pos, cam.map_rect)
            self.last_cell_clicked = None

    def func_reac_mousemotion(self, e):
    ##    if pygame.key.get_mods() & pygame.KMOD_CTRL:
        if pygame.mouse.get_pressed()[0]:
            if box_hmap.get_rect().collidepoint(e.pos):
                cam.center_on(e.pos)
            elif cam.map_rect.collidepoint(e.pos):
                delta = -V2(e.rel)/cam.cell_rect.w #assuming square cells
                move_cam_and_refresh(delta)
                self.last_cell_clicked = cam.get_cell(e.pos)
                ap.add_alert_countdown(e_help_move, guip.DELAY_HELP * self.fps)

    def move_cam_and_refresh(self, delta):
        cam.move(delta)
        cam.set_mg_pos_from_rcam()

    def process_mouse_navigation(self): #cam can move even with no mousemotion!
        if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
            pos = pygame.mouse.get_pos()
            d = V2(pos) - cam.map_rect.center
            if d != (0,0):
                intensity = 2e-8*d.length_squared()**1.5
                if intensity > 1.:
                    intensity = 1.
                d.scale_to_length(intensity)
                delta = V2(cam.correct_move(d))
                cam.move(delta)
                cam.set_mg_pos_from_rcam()
                ap.add_alert_countdown(e_help_move, guip.DELAY_HELP * self.fps)


    def load_image(self, fn):
        img = thorpy.load_image(fn)
        return pygame.transform.smoothscale(img, (self.zoom_cell_sizes[0],)*2)

    def get_color_image(self, color):
        surface = pygame.Surface((self.zoom_cell_sizes[0],)*2)
        surface.fill(color)
        return surface

    def refresh_derived_parameters(self):
        self.cell_size = self.zoom_cell_sizes[self.zoom_level]
        self.cell_rect = pygame.Rect(0,0,self.cell_size,self.cell_size)
        self.max_minimap_size = (self.max_wanted_minimap_size,)*2
        self.menu_size = (self.menu_width, self.H)
        self.menu_rect = pygame.Rect((0,0),self.menu_size)
        self.menu_rect.right = self.W
        if self.menu_rect.w < self.max_minimap_size[0] + self.box_hmap_margin*2:
            s = self.menu_rect.w - self.box_hmap_margin*2 - 2
            self.max_minimap_size = (s,s)
        self.viewport_rect = pygame.Rect((0,0),(self.menu_rect.left,
                                                self.menu_rect.bottom))

    def build_tiles(self, img_full_size, dx_divider=0, dy_divider=0):
        return tm.build_tiles(img_full_size, self.zoom_cell_sizes, self.nframes,
                                dx_divider, dy_divider)

    def add_material(self, name, hmax, img_fullsize, dx_divider=0, dy_divider=0):
        imgs = self.build_tiles(img_fullsize, dx_divider, dy_divider)
        self.materials[name] = tm.Material(name, hmax, imgs)

    def build_materials(self, cell_radius_divider):
        materials = list(self.materials.values())
        self.material_couples = tm.get_material_couples(materials,
                                                        cell_radius_divider)