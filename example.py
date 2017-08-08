import random
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

##thorpy.application.SHOW_FPS = True

#zoom avec slider
#help button
#alerts pour autres trucs

#space_material pour hauteurs negatives, qui sont mises sur la hmap apres que la miniature soit construite

#temperature a la place de altitude!

#objects avec des frames
#restreindre les relpos par obj (pour sapin, relpos[1] tj positif
#ajouter noms des objets dans infos cell

#objets dynamiques
#a l'interieur d'une cellule donnee, on peut se permettre de trier objs dynamiques en fonction de coord y pour un affichage correct

#revoir le draw no update

################################################################################
#objets de base: palmiers, feuillu, sapins(+ sapin enneige), montagnes, villages, chemin
#pour fs: chateaux, murailles, units: (herite de objet dynamique)

#peut etre que marche pas sans numpy a cause du beach tiler.
#Dans ce cas, favoriser la hmap issue de version numpy
#==> a tester sur une machine vierge

#finalement: editeur, load/save/quit

#v2:
#quand res + grande, nb de couples peut augmenter! ==> automatiser sur la base des materiaux existants

#ridged noise

#effets: vent dans arbres et fumee villages, ronds dans l'eau, herbe dans pieds, traces dans neige et sable, precipitations

#faire le outside en beachtiler?==> fonction speciale qui met en hauteur negative les bords

from editor.mapeditor import MapEditor

W,H = 800, 600 #screen size you want
app = thorpy.Application((W,H))

#might be chosen by user:

chunk =(1310,14) #to give when saving. Neighboring chunk give tilable maps.
desired_world_size = (100,50) #in number of cells. Put a power of 2 for tilable maps


#cell_radius = cell_size//radius_divider
# change how "round" look cell transitions
cell_radius_divider = 8

me = MapEditor()
me.zoom_cell_sizes = [20, 16, 12, 8] #side in pixels of the map's square cells
me.nframes = 16 #number of frames per world cycle (impact the need in memory!)
me.fps = 60 #frame per second
me.menu_width = 200 #width of the right menu in pixels
me.max_wanted_minimap_size = 128 #in pixels.

me.refresh_derived_parameters()


################################################################################
print("Building hmap")
power = int(math.log2(max(desired_world_size)))
if 2**power < max(desired_world_size):
    power += 1
S = int(2**power)
hmap = ng.generate_terrain(S, chunk)
ng.normalize(hmap)
##hmap[2][1] = 0.7 #this is how you manually change the height of a cell

#Here we build the miniature map image
img_hmap = ng.build_surface(hmap)
new_img_hmap = pygame.Surface(desired_world_size)
new_img_hmap.blit(img_hmap, (0,0))
img_hmap = new_img_hmap

################################################################################
print("Building tilers")
#Here and below we arbitrary choose how to interpret height as type of terrain
water = "./rendering/tiles/water1.png"
sand = "./rendering/tiles/sand1.jpg"
grass = "./rendering/tiles/grass1.png"
rock = "./rendering/tiles/rock1.png"

#we load simple images - they can be of any size, they will be resized
water_img = me.load_image(water)
sand_img = me.load_image(sand)
grass_img = me.load_image(grass)
rock_img = me.load_image(rock)
black_img = me.get_color_image((0,0,0))
white_img = me.get_color_image((255,255,255))

#mixed images - we superimpose different image to make a new one
deepwater_img = tm.get_mixed_tiles(water_img, black_img, 127)
mediumwater_img = tm.get_mixed_tiles(water_img, black_img, 50)
shore_img = tm.get_mixed_tiles(sand_img, water_img, 127) # alpha of water is 127
thinsnow_img = tm.get_mixed_tiles(rock_img, white_img, 160)

#build tiles
#water movement is made by using a delta-x (dx_divider) and delta-y shifts
deepwaters = me.build_tiles(deepwater_img, dx_divider=10, dy_divider=8)
mediumwaters = me.build_tiles(mediumwater_img, 10, 8)
waters = me.build_tiles(water_img, 10, 8)
shores = me.build_tiles(shore_img, 10, 8)
sands = me.build_tiles(sand_img)
grasses = me.build_tiles(grass_img)
rocks = me.build_tiles(rock_img)
snows1 = me.build_tiles(thinsnow_img)
snows2 = me.build_tiles(white_img)
outsides = me.build_tiles(black_img)


#build materials
#water movement is made by using a delta-x (dx_divider) and delta-y shifts,
# here dx_divider = 10 and dy_divider = 8
#hmax=0.1 means one will find deepwater only below height = 0.1
deepwater = me.add_material("Very deep water", 0.1, deepwater_img, 10, 8)
mediumwater = me.add_material("Deep water", 0.4, mediumwater_img, 10, 8)
water = me.add_material("Water", 0.55, water_img, 10, 8)
shore = me.add_material("Shallow water", 0.6, shore_img, 10, 8)
sand = me.add_material("Sand", 0.62, sand_img)
badlands = me.add_material("Grass", 0.8, grass_img)
rock = me.add_material("Rock", 0.83, rock_img)
snow1 = me.add_material("Thin snow", 0.9, thinsnow_img)
snow2 = me.add_material("Snow", float("inf"), white_img)
##space = me.add_material("Intergalactic Space", -1, black_img)

print("Building material couples")
material_couples = tm.get_material_couples([shore,badlands], cell_radius_divider)


################################################################################
me.build_camera()


################################################################################

frame_map = pygame.Surface(VIEWPORT_RECT.size)
frame_map.fill(guip.FRAME_MAP_COLOR)
pygame.draw.rect(frame_map, (255,255,255), cam.map_rect)
frame_map.set_colorkey((255,255,255))


################################################################################
layer2 = WhiteLogicalMap(hmap, map_rects, outsides,
                            cam.world_size, white_value=(255,255,255))

################################################################################
lm = LogicalMap(hmap, material_couples, map_rects, outsides, cam.world_size)
lm.frame_slowness = 0.1*FPS #frame will change every k*FPS [s]
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
fir0_img = thorpy.get_resized_image(fir0_img, (zoom_cell_sizes[0]-1,)*2)

char1_img = thorpy.load_image("./mapobjects/images/char1.png", (255,255,255))
char1_img = thorpy.get_resized_image(char1_img, (zoom_cell_sizes[0]-1,)*2)

forest_map = ng.generate_terrain(S,n_octaves=3) #generer sur map + grande et reduite, ou alors avec persistance +- faible suivant ce qu'on veut
ng.normalize(forest_map)

################################################################################
##objects

fir = MapObject(fir0_img)
fir.build_imgs(zoom_cell_sizes)

char1 = MapObject(char1_img)
char1.build_imgs(zoom_cell_sizes)

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
cell_clicked = None
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
##thorpy.commands.playing(FPS)
##commands.add_reaction(pygame.K_g, set_show_grid_lines)
##commands.default_func = reinit_frame

e_title_hmap = guip.get_title("Map")
box_hmap = thorpy.Box.make([e_hmap])
box_hmap.fit_children((BOX_HMAP_MARGIN,)*2)
topbox = thorpy.make_group([e_title_hmap, box_hmap], "v")

cell_info = gui.CellInfo(MENU_RECT.inflate((-10,0)).size, CELL_RECT.size, draw_no_update, e_hmap)
unit_info = gui.CellInfo(MENU_RECT.inflate((-10,0)).size, CELL_RECT.size, draw_no_update, e_hmap)
misc_info = gui.CellInfo(MENU_RECT.inflate((-10,0)).size, CELL_RECT.size, draw_no_update, e_hmap)

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


e_zoom = thorpy.SliderX.make(MENU_WIDTH//4, (0, 100), "Zoom (%)", int)
def troll(e):
    print("orofl",e_zoom.get_value())
    levels = len(zoom_cell_sizes) - 1
    level = int(levels*e_zoom.get_value()/e_zoom.limvals[1])
    print(level)
    set_zoom(level)
reac_zoom = thorpy.Reaction(reacts_to=thorpy.constants.THORPY_EVENT,
                            reac_func=troll,
                            event_args={"id":thorpy.constants.EVENT_SLIDE,
                                        "el":e_zoom})
e_hmap.add_reaction(reac_zoom)

box = thorpy.Element.make(elements=[e_zoom,
                                    topbox, #thorpy.Line.make(MENU_RECT.w-20),
                                    misc_info.e, #thorpy.Line.make(MENU_RECT.w-20),
                                    cell_info.e, #thorpy.Line.make(MENU_RECT.w-20),
                                    unit_info.e, #thorpy.Line.make(MENU_RECT.w-20),
                                    menu_button],
                            size=MENU_RECT.size)
thorpy.store(box)
box.stick_to("screen","right","right")


cam.set_elements(e_hmap, box_hmap)


cursors = gui.get_cursors(CELL_RECT.inflate((2,2)), (255,255,0))
idx_cursor = 0
img_cursor = cursors[idx_cursor]
cursor_slowness = int(0.3*FPS)


thorpy.makeup.add_basic_help(box_hmap, "Click to move camera on miniature map")
##thorpy.makeup.add_basic_help(box_hmap, "Click to move camera on miniature map")

ap = gui.AlertPool()
e_help_move = gui.get_help_text("To move the map, drag it with", "<LBM>",
                                "or hold", "<left shift>", "while moving mouse")
ap.add_alert_countdown(e_help_move, guip.DELAY_HELP * FPS)

set_zoom(0)
m = thorpy.Menu([box],fps=FPS)
m.play()


app.quit()

#pour FS: ajouter un info box quand on click sur material name, quand on click sur une cellule

