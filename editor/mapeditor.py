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
from mapobjects.objects import MapObject
import saveload.io as io

class MapEditor:

    def __init__(self):
        self.screen = thorpy.get_screen()
        self.W, self.H = screen.size #screen size, wont change
        #values below are default values; they can change and
        # self.refresh_derived_parameters() must be called
        self.fps = 80
        self.box_hmap_margin = 20 #box of the minimap
        self.menu_width = 200
        self.zoom_cell_sizes = [20,16,10]
        self.zoom_level = 0
        self.nframes = 16 #number of different tiles for one material (used for moving water)
        #


    def set_zoom(self, level):
        center_before = cam.get_center_coord()
        self.zoom_level = level
        refresh_derived_constants()
        cam.set_parameters(self.cell_size, self.viewport_rect, img_hmap, self.max_minimap_size)
        lm.set_zoom(level)
        cam.reinit_pos()
        move_cam_and_refresh((center_before[0]-cam.nx//2,center_before[1]-cam.ny//2))
        #cursor
        self.cursors = gui.get_self.cursors(self.cell_rect.inflate((2,2)), (255,255,0))
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
        surface = pygame.Surface(self.zoom_cell_sizes[0])
        surface.fill(color)
        return surface



    def refresh_derived_constants(self, max_wanted_minimap_size):
        self.cell_size = self.zoom_cell_sizes[self.zoom_level]
        self.cell_rect = pygame.Rect(0,0,self.cell_size,self.cell_size)
        self.max_minimap_size = (max_wanted_minimap_size,)*2
        self.menu_size = (self.menu_width, self.H)
        self.menu_rect = pygame.Rect((0,0),self.menu_size)
        self.menu_rect.right = self.W
        if self.menu_rect.w < self.max_minimap_size[0] + self.box_hmap_margin*2:
            s = self.menu_rect.w - self.box_hmap_margin*2 - 2
            self.max_minimap_size = (s,s)
        self.viewport_rect = pygame.Rect((0,0),(self.menu_rect.left,self.menu_rect.bottom))

    def build_tiles(self, img_full_size, dx_divider=0, dy_divider=0):
        return tm.build_tiles(img_full_size, self.zoom_cell_sizes, self.nframes,
                                dx_divider, dy_divider)


################################################################################
print("Building hmap")
DESIRED_WORLD_SIZE = (100,50)
power = int(math.log2(max(DESIRED_WORLD_SIZE)))
if 2**power < max(DESIRED_WORLD_SIZE):
    power += 1
S = int(2**power)
chunk=(1310,14) #to give when saving


hmap = ng.generate_terrain(S, chunk)
ng.normalize(hmap)
hmap[2][1] = 0.7
hmap[S-1][S-1] = 1.
img_hmap = ng.build_surface(hmap)

#possibility to use other sizes:
new_img_hmap = pygame.Surface(DESIRED_WORLD_SIZE)
new_img_hmap.blit(img_hmap, (0,0))
img_hmap = new_img_hmap


################################################################################
print("Building tilers")
#Here we arbitrary choose how to interpret height as type of terrain
water = "./rendering/tiles/water1.png"
sand = "./rendering/tiles/sand1.jpg"
grass = "./rendering/tiles/grass1.png"
rock = "./rendering/tiles/rock1.png"
#simple images
water_img = load_image(water)
sand_img = load_image(sand)
grass_img = load_image(grass)
rock_img = load_image(rock)
black_img = pygame.Surface((self.zoom_cell_sizes[0],)*2)
white_img = black_img.copy()
white_img.fill((255,255,255))
#mixed images
deepwater = tm.get_mixed_tiles(water_img, black_img, 127)
mediumwater = tm.get_mixed_tiles(water_img, black_img,50)
shore = tm.get_mixed_tiles(sand_img, water_img, 127)  #alpha of water is 127
thinsnow = tm.get_mixed_tiles(rock_img, white_img, 160)
#build tiles
deepwaters = tm.build_tiles(deepwater, self.zoom_cell_sizes, self.nframes,
                            dx_divider=10, dy_divider=8) #water movement
mediumwaters = tm.build_tiles(mediumwater, self.zoom_cell_sizes, self.nframes, 10, 8)
waters = tm.build_tiles(water_img, self.zoom_cell_sizes, self.nframes, 10, 8)
shores = tm.build_tiles(shore, self.zoom_cell_sizes, self.nframes, 10, 8)
sands = tm.build_tiles(sand_img, self.zoom_cell_sizes, self.nframes)
grasses = tm.build_tiles(grass_img, self.zoom_cell_sizes, self.nframes)
rocks = tm.build_tiles(rock_img, self.zoom_cell_sizes, self.nframes)
snows1 = tm.build_tiles(thinsnow, self.zoom_cell_sizes, self.nframes)
snows2 = tm.build_tiles(white_img, self.zoom_cell_sizes, self.nframes)
outsides = tm.build_tiles(black_img, self.zoom_cell_sizes, self.nframes)
#build materials
deepwater = tm.Material("Very deep water", 0.1, deepwaters)
mediumwater = tm.Material("Deep water", 0.4, mediumwaters)
water = tm.Material("Water", 0.55, waters)
shore = tm.Material("Shallow water", 0.6, shores)
sand = tm.Material("Sand", 0.62, sands) #means sand below 0.62
badlands = tm.Material("Grass", 0.8, grasses)
rock = tm.Material("Rock", 0.83, rocks)
snow1 = tm.Material("Thin snow", 0.9, snows1)
snow2 = tm.Material("Snow", float("inf"), snows2)
space = tm.Material("Space", -float("inf"), outsides)
#here water.imgs is a list of images list whose index refer to zoom level

print("Building material couples")
##materials = [deepwater, mediumwater, water, shore, sand, badlands, rock, snow1, snow2]
##material_couples = tm.get_material_couples(materials, CELL_RADIUS_DIVIDER)
material_couples = tm.get_material_couples([shore,badlands], CELL_RADIUS_DIVIDER)
##materials = [space,deepwater, mediumwater, water, shore, sand, badlands, rock, snow1, snow2]
##material_couples = tm.get_material_couples(materials, CELL_RADIUS_DIVIDER)
################################################################################
#derived constants
self.cell_size = None
self.cell_rect = None
self.menu_size = None
self.menu_rect = None
self.viewport_rect = None
self.max_minimap_size = None



refresh_derived_constants()
################################################################################
cam = Camera()

map_rects = []
for i,level in enumerate(self.zoom_cell_sizes):
    self.zoom_level = i
    refresh_derived_constants()
    cam.set_parameters(self.cell_size, self.viewport_rect, img_hmap, self.max_minimap_size)
    map_rects.append(pygame.Rect(cam.map_rect))
self.zoom_level = 0 #reset to zero
refresh_derived_constants()
cam.set_parameters(self.cell_size, self.viewport_rect, img_hmap, self.max_minimap_size)


################################################################################
layer2 = WhiteLogicalMap(hmap, map_rects, outsides, self.zoom_cell_sizes, self.nframes,
                            cam.world_size, white_value=(255,255,255))

################################################################################
lm = LogicalMap(hmap, material_couples, map_rects, outsides, cam.world_size)
lm.frame_slowness = 0.1*self.fps #frame will change every k*self.fps [s]
lm.refresh_cell_heights(hmap)
lm.refresh_cell_types()
lm.cells[3][3].name = "Roflburg"
lm.add_layer(layer2)

cam.set_map_data(lm)

layer2.refresh_cell_heights(hmap)
layer2.refresh_cell_types()

################################################################################
print("Adding objects")
fir0_img = thorpy.load_image("./mapobjects/images/fir0.png", (255,255,255))
fir0_img = thorpy.get_resized_image(fir0_img, (self.zoom_cell_sizes[0]-1,)*2)

char1_img = thorpy.load_image("./mapobjects/images/char1.png", (255,255,255))
char1_img = thorpy.get_resized_image(char1_img, (self.zoom_cell_sizes[0]-1,)*2)

forest_map = ng.generate_terrain(S,n_octaves=3) #generer sur map + grande et reduite, ou alors avec persistance +- faible suivant ce qu'on veut
ng.normalize(forest_map)

################################################################################
##objects

fir = MapObject(fir0_img)
fir.build_imgs(self.zoom_cell_sizes)

char1 = MapObject(char1_img)
char1.build_imgs(self.zoom_cell_sizes)

static_objects = []
dynamic_objects = []


for x in range(lm.nx):
    for y in range(lm.ny):
        h = forest_map[x][y]
        if 0.3 < h < 0.35 or 0.8 < h < 0.85:
            if lm.cells[x][y].material is badlands:
                for i in range(3):
                    if random.random() < 0.75:
                        obj = fir.add_copy_on_cell(lm.cells[x][y])
                        obj.randomize_relpos()
                        static_objects.append(obj)
##                        print(x,y)
##                        xrel = random.random()/10.
##                        yrel = random.random()/10.
##                        layer2.blit_on_cell(fir0_img, x, y, xrel, yrel)

obj = char1.add_copy_on_cell(lm.cells[32][15])
dynamic_objects.append(obj)


###############################################################################


print("Building untiled surfaces")
lm.build_surfaces()
print("Builing object layer untiled surfaces()")
layer2.build_surfaces(colorkey=(255,255,255))
layer2.save_pure_surfaces() #save BEFORE we blit objects (unless we want the objects to be part of the permanent map)
layer2.blit_objects(static_objects)


################################################################################
print("Building GUI")
self.last_cell_clicked = None
show_grid_lines = False

def set_show_grid_lines(value):
    global show_grid_lines
    show_grid_lines = value


e_hmap = thorpy.Image.make(img_hmap)
e_hmap.stick_to("screen", "right", "right", False)
e_hmap.add_reaction(thorpy.Reaction(pygame.MOUSEMOTION, func_reac_mousemotion))
e_hmap.add_reaction(thorpy.Reaction(pygame.MOUSEBUTTONDOWN, func_reac_click))
e_hmap.add_reaction(thorpy.Reaction(pygame.MOUSEBUTTONUP, func_reac_unclick))


thorpy.add_time_reaction(e_hmap, func_reac_time)
thorpy.add_keydown_reaction(e_hmap, pygame.K_KP_PLUS, increment_zoom, params={"value":-1})
thorpy.add_keydown_reaction(e_hmap, pygame.K_KP_MINUS, increment_zoom, params={"value":1})


velocity = 0.2
thorpy.add_keydown_reaction(e_hmap, pygame.K_LEFT, move_cam_and_refresh, params={"delta":(-velocity,0)})
thorpy.add_keydown_reaction(e_hmap, pygame.K_RIGHT, move_cam_and_refresh, params={"delta":(velocity,0)})
thorpy.add_keydown_reaction(e_hmap, pygame.K_UP, move_cam_and_refresh, params={"delta":(0,-velocity)})
thorpy.add_keydown_reaction(e_hmap, pygame.K_DOWN, move_cam_and_refresh, params={"delta":(0,velocity)})

thorpy.add_keydown_reaction(e_hmap, pygame.K_g, set_show_grid_lines, params={"value":True})
thorpy.add_keyup_reaction(e_hmap, pygame.K_g, set_show_grid_lines, params={"value":False})

def rofl():
    layer2.reset_pure_surfaces()
thorpy.add_keydown_reaction(e_hmap, pygame.K_SPACE, rofl)

##commands = thorpy.commands.Commands(e_hmap)
##thorpy.commands.playing(self.fps)
##commands.add_reaction(pygame.K_g, set_show_grid_lines)
##commands.default_func = reinit_frame

e_title_hmap = guip.get_title("Map")
box_hmap = thorpy.Box.make([e_hmap])
box_hmap.fit_children((self.box_hmap_margin,)*2)
topbox = thorpy.make_group([e_title_hmap, box_hmap], "v")

cell_info = gui.CellInfo(self.menu_rect.inflate((-10,0)).size, self.cell_rect.size, draw_no_update, e_hmap)
unit_info = gui.CellInfo(self.menu_rect.inflate((-10,0)).size, self.cell_rect.size, draw_no_update, e_hmap)
misc_info = gui.CellInfo(self.menu_rect.inflate((-10,0)).size, self.cell_rect.size, draw_no_update, e_hmap)

help_box = gui.HelpBox([
("Move camera",
    [("To move the map, drag it with", "<LMB>",
        "or hold", "<LEFT SHIFT>", "while moving mouse."),
     ("The minimap on the upper right can be clicked or hold with","<LMB>",
        "in order to move the camera."),
     ("The","<KEYBOARD ARROWS>", "can also be used to scroll the map view.")]),
("Zoom",
    [("Use the","zoom slider","or","<NUMPAD +/- >","to change zoom level."),
     ("You can also alternate zoom levels by pressing","<RMB>",".")])])


e_quit = thorpy.make_button("Quit game", thorpy.functions.quit_func)
e_save = thorpy.make_button("Save", io.ask_save, {"editor":None})
e_load = thorpy.make_button("Load", io.ask_load)

menu_button = thorpy.make_menu_button()
menu_button_launched = thorpy.make_ok_box([help_box.launcher,
                                            e_save,
                                            e_load,
                                            e_quit])
menu_button_launched.center()

menu_button.user_func = thorpy.launch_blocking
menu_button.user_params = {"element":menu_button_launched}


e_zoom = thorpy.SliderX.make(self.menu_width//4, (0, 100), "Zoom (%)", int)
def troll(e):
    print("orofl",e_zoom.get_value())
    levels = len(self.zoom_cell_sizes) - 1
    level = int(levels*e_zoom.get_value()/e_zoom.limvals[1])
    print(level)
    set_zoom(level)
reac_zoom = thorpy.Reaction(reacts_to=thorpy.constants.THORPY_EVENT,
                            reac_func=troll,
                            event_args={"id":thorpy.constants.EVENT_SLIDE,
                                        "el":e_zoom})
e_hmap.add_reaction(reac_zoom)

box = thorpy.Element.make(elements=[e_zoom,
                                    topbox, #thorpy.Line.make(self.menu_rect.w-20),
                                    misc_info.e, #thorpy.Line.make(self.menu_rect.w-20),
                                    cell_info.e, #thorpy.Line.make(self.menu_rect.w-20),
                                    unit_info.e, #thorpy.Line.make(self.menu_rect.w-20),
                                    menu_button],
                            size=self.menu_rect.size)
thorpy.store(box)
box.stick_to("screen","right","right")


cam.set_elements(e_hmap, box_hmap)


self.cursors = gui.get_self.cursors(self.cell_rect.inflate((2,2)), (255,255,0))
self.idx_cursor = 0
self.img_cursos = self.cursors[self.idx_cursor]
cursor_slowness = int(0.3*self.fps)


thorpy.makeup.add_basic_help(box_hmap, "Click to move camera on miniature map")
##thorpy.makeup.add_basic_help(box_hmap, "Click to move camera on miniature map")

ap = gui.AlertPool()
e_help_move = gui.get_help_text("To move the map, drag it with", "<LBM>",
                                "or hold", "<left shift>", "while moving mouse")
ap.add_alert_countdown(e_help_move, guip.DELAY_HELP * self.fps)

set_zoom(0)
m = thorpy.Menu([box],fps=self.fps)
m.play()


app.quit()

#pour FS: ajouter un info box quand on click sur material name, quand on click sur une cellule

