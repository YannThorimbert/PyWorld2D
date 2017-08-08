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

def sgn(x):
    if x < 0:
        return -1.
    elif x > 0:
        return 1.
    return 0.

class MapEditor:

    def __init__(self):
        self.screen = thorpy.get_screen()
        self.W, self.H = self.screen.get_size() #self.screen size, wont change
        #values below are default values; they can change and
        # self.refresh_derived_parameters() must be called
        self.fps = 80
        self.box_hmap_margin = 20 #box of the minimap
        self.menu_width = 200
        self.zoom_cell_sizes = [20,16,10]
        self.nframes = 16 #number of different tiles for one material (used for moving water)
        self.max_wanted_minimap_size = 128 #in pixels.
        self.show_grid_lines = False
        #
        self.lm = None
        self.cam = None #camera, to be built later
        self.map_rects = None
        self.zoom_level = 0
        self.materials = {}
        self.material_couples = None
        self.dynamic_objects = []
        self.last_cell_clicked = None
        #
        self.cursor_color = (255,255,0)
        self.cursors = None
        self.idx_cursor = 0
        self.img_cursor = None
        self.cursor_slowness = None
        #gui
        self.e_box = None
        self.cell_info = None
        self.unit_info = None
        self.misc_info = None
        self.e_hmap = None
        self.box_hmap = None
        #
        self.ap = gui.AlertPool()
        self.e_ap_move = gui.get_help_text("To move the map, drag it with", "<LBM>",
                                        "or hold", "<left shift>", "while moving mouse")
        self.ap.add_alert_countdown(self.e_ap_move, guip.DELAY_HELP * self.fps)

    def build_gui_elements(self): #worst function ever
        e_hmap = thorpy.Image.make(self.cam.img_hmap)
        e_hmap.stick_to("screen", "right", "right", False)
        e_hmap.add_reaction(thorpy.Reaction(pygame.MOUSEMOTION,
                                            self.func_reac_mousemotion))
        e_hmap.add_reaction(thorpy.Reaction(pygame.MOUSEBUTTONDOWN,
                                            self.func_reac_click))
        e_hmap.add_reaction(thorpy.Reaction(pygame.MOUSEBUTTONUP,
                                            self.func_reac_unclick))
        self.e_hmap = e_hmap
        e_title_hmap = guip.get_title("Map")
        box_hmap = thorpy.Box.make([e_hmap])
        box_hmap.fit_children((self.box_hmap_margin,)*2)
        thorpy.makeup.add_basic_help(box_hmap,
                                     "Click to move camera on miniature map")
        self.topbox = thorpy.make_group([e_title_hmap, box_hmap], "v")
        self.box_hmap = box_hmap
        ########################################################################
        self.cam.set_gui_elements(e_hmap, box_hmap)
        ########################################################################
        self.e_zoom = thorpy.SliderX.make(self.menu_width//4, (0, 100),
                                            "Zoom (%)", int, initial_value=100)
        def func_reac_zoom(e):
            levels = len(self.zoom_cell_sizes) - 1
            level = int(levels*self.e_zoom.get_value()/self.e_zoom.limvals[1])
            self.set_zoom(levels-level)
        ########################################################################
        self.cell_info = gui.CellInfo(self.menu_rect.inflate((-10,0)).size,
                         self.cell_rect.size, self.draw_no_update, e_hmap)
        self.unit_info = gui.CellInfo(self.menu_rect.inflate((-10,0)).size,
                         self.cell_rect.size, self.draw_no_update, e_hmap)
        self.misc_info = gui.CellInfo(self.menu_rect.inflate((-10,0)).size,
                         self.cell_rect.size, self.draw_no_update, e_hmap)
        self.menu_button = thorpy.make_menu_button()
        ########################################################################
        self.e_box = thorpy.Element.make(elements=[self.e_zoom,
                                                self.topbox,
                                                self.misc_info.e,
                                                self.cell_info.e,
                                                self.unit_info.e,
                                                self.menu_button],
                                        size=self.menu_rect.size)
        thorpy.store(self.e_box)
        self.e_box.stick_to("screen","right","right")
        ########################################################################
        reac_zoom = thorpy.Reaction(reacts_to=thorpy.constants.THORPY_EVENT,
                                    reac_func=func_reac_zoom,
                                    event_args={"id":thorpy.constants.EVENT_SLIDE,
                                                "el":self.e_zoom},
                                    reac_name="zoom slide")
        self.e_box.add_reaction(reac_zoom)
        ########################################################################
        thorpy.add_keydown_reaction(self.e_box, pygame.K_KP_PLUS,
                                    self.increment_zoom, params={"value":-1},
                                    reac_name="k plus")
        thorpy.add_keydown_reaction(self.e_box, pygame.K_KP_MINUS,
                                    self.increment_zoom, params={"value":1},
                                    reac_name="k minus")
        ########################################################################
        velocity = 0.2
        thorpy.add_keydown_reaction(self.e_box, pygame.K_LEFT,
                                    self.move_cam_and_refresh,
                                    params={"delta":(-velocity,0)},
                                    reac_name="k left")
        thorpy.add_keydown_reaction(self.e_box, pygame.K_RIGHT,
                                    self.move_cam_and_refresh,
                                    params={"delta":(velocity,0)},
                                    reac_name="k right")
        thorpy.add_keydown_reaction(self.e_box, pygame.K_UP,
                                    self.move_cam_and_refresh,
                                    params={"delta":(0,-velocity)},
                                    reac_name="k up")
        thorpy.add_keydown_reaction(self.e_box, pygame.K_DOWN,
                                    self.move_cam_and_refresh,
                                    params={"delta":(0,velocity)},
                                    reac_name="k down")
        ########################################################################
        self.help_box = gui.HelpBox([
        ("Move camera",
            [("To move the map, drag it with", "<LMB>",
                "or hold", "<LEFT SHIFT>", "while moving mouse."),
             ("The minimap on the upper right can be clicked or hold with",
                "<LMB>", "in order to move the camera."),
             ("The","<KEYBOARD ARROWS>",
              "can also be used to scroll the map view.")]),

        ("Zoom",
            [("Use the","zoom slider","or","<NUMPAD +/- >",
              "to change zoom level."),
             ("You can also alternate zoom levels by pressing","<RMB>",".")]),

        ("Miscellaneous",
            [("Press","<g>","to toggle grid lines display.")])
        ])
        thorpy.add_keydown_reaction(self.e_box, pygame.K_g,
                                    self.toggle_show_grid_lines,
                                    reac_name="toggle grid")


    def toggle_show_grid_lines(self):
            self.show_grid_lines = not(self.show_grid_lines)

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

    def set_key_scroll_velocity(self, velnorm):
        for name in ["left", "right", "up", "down"]:
            name = "k "+name
            value = self.e_box.get_reaction(name).params["delta"]
            value = sgn(value) * velnorm
            self.e_box.get_reaction(name).params["delta"] = value


    def build_surfaces(self):
        self.lm.build_surfaces()
        self.lm.blit_objects()
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
        center_before = self.cam.get_center_coord()
        self.zoom_level = level
        self.refresh_derived_parameters()
        self.cam.set_parameters(self.cell_size,
                            self.viewport_rect,
                            self.cam.img_hmap,
                            self.max_minimap_size)
        self.lm.set_zoom(level)
        self.cam.reinit_pos()
        self.move_cam_and_refresh((center_before[0]-self.cam.nx//2,
                                    center_before[1]-self.cam.ny//2))
        #cursor
        self.cursors = gui.get_cursors(self.cell_rect.inflate((2,2)),
                                            self.cursor_color)
        self.idx_cursor = 0
        self.img_cursors = self.cursors[self.idx_cursor]
        #
        self.unblit_map()
        self.draw_no_update()


    def increment_zoom(self, value):
        self.zoom_level += value
        self.zoom_level %= len(self.zoom_cell_sizes)
        self.set_zoom(self.zoom_level)

    def update_cell_info(self):
        mousepos = pygame.mouse.get_pos()
        cell = self.cam.get_cell(mousepos)
        if cell:
    ##        pygame.draw.rect(self.screen, (0,0,0), get_rect_at_pix(mousepos), 1)
            rcursor = self.img_cursors.get_rect()
            rcursor.center = self.cam.get_rect_at_pix(mousepos).center
            self.screen.blit(self.img_cursors, rcursor)
            if self.cell_info.cell is not cell:
                self.cell_info.update_e(cell)
    ##        if cell.objects:
    ##            print(cell.objects)

    def unblit_map(self):
        pygame.draw.rect(self.screen, (0,0,0), self.cam.map_rect)

    def draw(self):
        self.cam.set_rmouse_from_rcam()
        #blit map frame
        self.screen.fill((0,0,0))
        #blit map
        self.cam.draw_grid(self.screen)
        #blit grid
        if self.show_grid_lines:
            self.cam.draw_grid_lines(self.screen)
        #blit objects
        self.cam.draw_objects(self.screen, self.dynamic_objects)
        #update right pane
        self.update_cell_info()
        #blit right pane and draw rect on minimap
        self.e_box.blit()
        pygame.draw.rect(self.screen, (255,255,255), self.cam.rmouse, 1)

    def draw_no_update(self):
        #blit map frame
        self.screen.fill((0,0,0))
        #blit map
        self.cam.draw_grid(self.screen)
        #blit grid
        if self.show_grid_lines:
            self.cam.draw_grid_lines(self.screen)
        #blit objects
        self.cam.draw_objects(self.screen, self.dynamic_objects)
        #blit right pane and draw rect on minimap
        self.e_box.blit()
        pygame.draw.rect(self.screen, (255,255,255), self.cam.rmouse, 1)

    def func_reac_time(self):
        self.process_mouse_navigation()
        self.draw()
        self.ap.refresh()
        self.ap.draw(self.screen, 20,20)
        #
        self.lm.next_frame()
        if self.lm.tot_time%self.cursor_slowness == 0:
            self.idx_cursor = (self.idx_cursor+1)%len(self.cursors)
            self.img_cursors = self.cursors[self.idx_cursor]


    def func_reac_click(self, e):
        if e.button == 1: #left click
            if self.box_hmap.get_rect().collidepoint(e.pos):
                self.cam.center_on(e.pos)
        elif e.button == 3: #right click
            self.increment_zoom(1)

    def func_reac_unclick(self, e):
        if e.button == 1:
            cell = self.cam.get_cell(e.pos)
            if cell:
                if cell is not self.last_cell_clicked:
                    if not self.cell_info.launched:
                        self.last_cell_clicked = cell
                        self.cell_info.launch_em(cell, e.pos, self.cam.map_rect)
            self.last_cell_clicked = None

    def func_reac_mousemotion(self, e):
    ##    if pygame.key.get_mods() & pygame.KMOD_CTRL:
        if pygame.mouse.get_pressed()[0]:
            if self.box_hmap.get_rect().collidepoint(e.pos):
                self.cam.center_on(e.pos)
            elif self.cam.map_rect.collidepoint(e.pos):
                delta = -V2(e.rel)/self.cam.cell_rect.w #assuming square cells
                self.move_cam_and_refresh(delta)
                self.last_cell_clicked = self.cam.get_cell(e.pos)
                self.ap.add_alert_countdown(self.e_ap_move, guip.DELAY_HELP * self.fps)

    def move_cam_and_refresh(self, delta):
        self.cam.move(delta)
        self.cam.set_mg_pos_from_rcam()

    def process_mouse_navigation(self): #cam can move even with no mousemotion!
        if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
            pos = pygame.mouse.get_pos()
            d = V2(pos) - self.cam.map_rect.center
            if d != (0,0):
                intensity = 2e-8*d.length_squared()**1.5
                if intensity > 1.:
                    intensity = 1.
                d.scale_to_length(intensity)
                delta = V2(self.cam.correct_move(d))
                self.cam.move(delta)
                self.cam.set_mg_pos_from_rcam()
                self.ap.add_alert_countdown(self.e_ap_move, guip.DELAY_HELP * self.fps)


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