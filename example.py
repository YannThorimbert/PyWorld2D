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

##thorpy.application.SHOW_FPS = True

#bliter les statis (layer) sur miniature

#objects avec des frames

#quand meme mettre un texte pour les keys...

#generaliser le nb de calques ==> voir fps

#revoir le draw no update

#restreindre les relpos par obj (pour sapin, relpos[1] tj positif

#mettre un max d'objets en static. Tout ce qui est movable n'apparait pas dans l'apercu de infos cell.

#a l'interieur d'une cellule donnee, on peut se permettre de trier objs dynamiques en fonction de coord y pour un affichage correct

#ajouter noms des objets dans infos cell

#POUR OBJECtS STATICS; si jen fais:
#       -on blit les parties qui debordent sur les voisins!
#       -on les construits a partir des imgs des objects dynamics, car deja bien scaled


################################################################################
#objets de base: palmiers, feuillu, sapins(+ sapin enneigÃ©), montagnes, villages, chemin
#pour fs: chateaux, murailles, units: (herite de objet)

#peut etre que marche pas sans numpy a cause du beach tiler.
#Dans ce cas, favoriser la hmap issue de version numpy
#==> a tester sur une machine vierge

#finalement: editeur, load/save/quit

#v2:
#quand res + grande, nb de couples peut augmenter! ==> automatiser sur la base des materiaux existants

#ridged noise

#effets: vent dans arbres et fumee villages, ronds dans l'eau, herbe dans pieds, traces dans neige et sable, precipitations


#faire le outside en beachtiler?


def set_zoom(level):
    global CURRENT_ZOOM_LEVEL, img_cursor, cursors, frame_map
    center_before = cam.get_center_coord()
    CURRENT_ZOOM_LEVEL = level
    refresh_derived_constants()
    cam.set_parameters(CELL_SIZE, VIEWPORT_RECT, img_hmap, MAX_MINIMAP_SIZE)
    lm.set_zoom(level)
    layer2.set_zoom(level)
    cam.reinit_pos()
    move_cam_and_refresh((center_before[0]-cam.nx//2,center_before[1]-cam.ny//2))
    #cursor
    cursors = gui.get_cursors(CELL_RECT.inflate((2,2)), (255,255,0))
    idx_cursor = 0
    img_cursor = cursors[idx_cursor]
    #
    unblit_map()
    draw_no_update()



def increment_zoom(value):
    global CURRENT_ZOOM_LEVEL
    CURRENT_ZOOM_LEVEL += value
    CURRENT_ZOOM_LEVEL %= len(ZOOM_CELL_SIZES)
    set_zoom(CURRENT_ZOOM_LEVEL)

def update_cell_info():
    mousepos = pygame.mouse.get_pos()
    cell = cam.get_cell(mousepos)
    if cell:
##        pygame.draw.rect(screen, (0,0,0), get_rect_at_pix(mousepos), 1)
        rcursor = img_cursor.get_rect()
        rcursor.center = cam.get_rect_at_pix(mousepos).center
        screen.blit(img_cursor, rcursor)
        if cell_info.cell is not cell:
            cell_info.update_e(cell)
##        if cell.objects:
##            print(cell.objects)

def unblit_map():
    pygame.draw.rect(screen, (0,0,0), cam.map_rect)

def draw():
    cam.set_rmouse_from_rcam()
    #blit map frame
    screen.fill((0,0,0))
    #blit map
    cam.draw_grid(screen)
    cam.draw_layer(screen)
    #blit grid
    if show_grid_lines:
        cam.draw_grid_lines(screen)
    #blit objects
    cam.draw_objects(screen, dynamic_objects)
    #update right pane
    update_cell_info()
    #blit map frame
##    screen.blit(frame_map, (0,0))
    #blit right pane and draw rect on minimap
    box.blit()
    pygame.draw.rect(screen, (255,255,255), cam.rmouse, 1)

def draw_no_update():
    cam.draw_grid(screen)
##    screen.blit(frame_map, (0,0))
    box.blit()
    pygame.draw.rect(screen, (255,255,255), cam.rmouse, 1)

def func_reac_time():
    global img_cursor, idx_cursor
    process_mouse_navigation()
    draw()
    pygame.display.flip()
    #
    lm.next_frame()
    layer2.t = lm.t
    if lm.tot_time%cursor_slowness == 0:
        idx_cursor = (idx_cursor+1)%len(cursors)
        img_cursor = cursors[idx_cursor]


def func_reac_click(e):
    if e.button == 1: #left click
        if box_hmap.get_rect().collidepoint(e.pos):
            cam.center_on(e.pos)
    elif e.button == 3:
        print("Uh")
        increment_zoom(1)

def func_reac_unclick(e):
    global cell_clicked
    if e.button == 1:
        cell = cam.get_cell(e.pos)
        if cell:
            if cell is not cell_clicked:
                if not cell_info.launched:
                    cell_clicked = cell
                    cell_info.launch_em(cell, e.pos, cam.map_rect)
        cell_clicked = None

def func_reac_mousemotion(e):
    global cell_clicked
##    if pygame.key.get_mods() & pygame.KMOD_CTRL:
    if pygame.mouse.get_pressed()[0]:
        if box_hmap.get_rect().collidepoint(e.pos):
            cam.center_on(e.pos)
        elif cam.map_rect.collidepoint(e.pos):
            delta = -V2(e.rel)/cam.cell_rect.w #assuming square cells
            move_cam_and_refresh(delta)
            cell_clicked = cam.get_cell(e.pos)

def move_cam_and_refresh(delta):
    cam.move(delta)
    cam.set_mg_pos_from_rcam()

def process_mouse_navigation(): #cam can move even with no mousemotion!
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


def load_image(fn):
    img = thorpy.load_image(fn)
    return pygame.transform.smoothscale(img, (ZOOM_CELL_SIZES[0],)*2)


#arbitrary constants
W, H = 900, 600
FPS = 80
BOX_HMAP_MARGIN = 20 #box of the minimap
MENU_WIDTH = 200
MAX_WANTED_MINIMAP_SIZE = 128
S = 128 #size of the produced hmap (to be completed with croping!)
ZOOM_CELL_SIZES = [32, 25, 20, 16, 12, 8, 4]
##ZOOM_CELL_SIZES = [20]
CURRENT_ZOOM_LEVEL = 0
CELL_RADIUS_DIVIDER = 8 #cell_radius = cell_size//radius_divider
NFRAMES = 16 #number of different tiles for one material (used for moving water)


app = thorpy.Application((W,H), "PyWorld2D example")
screen = thorpy.get_screen()

################################################################################
print("Building hmap")
hmap = ng.generate_terrain(S, chunk=(1310,14)) #1310,14, S=64
ng.normalize(hmap)
hmap[2][1] = 0.7
hmap[S-1][S-1] = 1.
img_hmap = ng.build_surface(hmap)

#possibility to use other sizes:
new_img_hmap = pygame.Surface((S,S//3))
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
black_img = pygame.Surface((ZOOM_CELL_SIZES[0],)*2)
white_img = black_img.copy()
white_img.fill((255,255,255))
#mixed images
deepwater = tm.get_mixed_tiles(water_img, black_img, 127)
mediumwater = tm.get_mixed_tiles(water_img, black_img,50)
shore = tm.get_mixed_tiles(sand_img, water_img, 127)  #alpha of water is 127
thinsnow = tm.get_mixed_tiles(rock_img, white_img, 160)
#build tiles
deepwaters = tm.build_tiles(deepwater, ZOOM_CELL_SIZES, NFRAMES,
                            dx_divider=10, dy_divider=8) #water movement
mediumwaters = tm.build_tiles(mediumwater, ZOOM_CELL_SIZES, NFRAMES, 10, 8)
waters = tm.build_tiles(water_img, ZOOM_CELL_SIZES, NFRAMES, 10, 8)
shores = tm.build_tiles(shore, ZOOM_CELL_SIZES, NFRAMES, 10, 8)
sands = tm.build_tiles(sand_img, ZOOM_CELL_SIZES, NFRAMES)
grasses = tm.build_tiles(grass_img, ZOOM_CELL_SIZES, NFRAMES)
rocks = tm.build_tiles(rock_img, ZOOM_CELL_SIZES, NFRAMES)
snows1 = tm.build_tiles(thinsnow, ZOOM_CELL_SIZES, NFRAMES)
snows2 = tm.build_tiles(white_img, ZOOM_CELL_SIZES, NFRAMES)
outsides = tm.build_tiles(black_img, ZOOM_CELL_SIZES, NFRAMES)
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
#here water.imgs is a list of images list whose index refer to zoom level

print("Building material couples")
##materials = [deepwater, mediumwater, water, shore, sand, badlands, rock, snow1, snow2]
##material_couples = tm.get_material_couples(materials, CELL_RADIUS_DIVIDER)
material_couples = tm.get_material_couples([shore,badlands], CELL_RADIUS_DIVIDER)
################################################################################
#derived constants
CELL_SIZE = None
CELL_RECT = None
MENU_SIZE = None
MENU_RECT = None
VIEWPORT_RECT = None
MAX_MINIMAP_SIZE = None
def refresh_derived_constants():
    global CELL_SIZE, CELL_RECT, MAX_MINIMAP_SIZE, MENU_SIZE, MENU_RECT, VIEWPORT_RECT
    CELL_SIZE = ZOOM_CELL_SIZES[CURRENT_ZOOM_LEVEL]
    CELL_RECT = pygame.Rect(0,0,CELL_SIZE,CELL_SIZE)
    MAX_MINIMAP_SIZE = (MAX_WANTED_MINIMAP_SIZE,)*2
    MENU_SIZE = (MENU_WIDTH, H)
    MENU_RECT = pygame.Rect((0,0),MENU_SIZE)
    MENU_RECT.right = W
    if MENU_RECT.w < MAX_MINIMAP_SIZE[0] + BOX_HMAP_MARGIN*2:
        s = MENU_RECT.w - BOX_HMAP_MARGIN*2 - 2
        MAX_MINIMAP_SIZE = (s,s)
    VIEWPORT_RECT = pygame.Rect((0,0),(MENU_RECT.left,MENU_RECT.bottom))
refresh_derived_constants()
################################################################################
cam = Camera()

map_rects = []
for i,level in enumerate(ZOOM_CELL_SIZES):
    CURRENT_ZOOM_LEVEL = i
    refresh_derived_constants()
    cam.set_parameters(CELL_SIZE, VIEWPORT_RECT, img_hmap, MAX_MINIMAP_SIZE)
    map_rects.append(pygame.Rect(cam.map_rect))
CURRENT_ZOOM_LEVEL = 0 #reset to zero
refresh_derived_constants()
cam.set_parameters(CELL_SIZE, VIEWPORT_RECT, img_hmap, MAX_MINIMAP_SIZE)


################################################################################

frame_map = pygame.Surface(VIEWPORT_RECT.size)
frame_map.fill(guip.FRAME_MAP_COLOR)
pygame.draw.rect(frame_map, (255,255,255), cam.map_rect)
frame_map.set_colorkey((255,255,255))


################################################################################
layer2 = WhiteLogicalMap(hmap, map_rects, outsides, ZOOM_CELL_SIZES, NFRAMES,
                            cam.world_size, white_value=(255,255,255))

################################################################################
lm = LogicalMap(hmap, material_couples, map_rects, outsides, cam.world_size)
lm.frame_slowness = 0.1*FPS #frame will change every k*FPS [s]
lm.refresh_cell_heights(hmap)
lm.refresh_cell_types()
lm.cells[3][3].name = "Roflburg"
cam.set_map_data(lm, layer2)


layer2.frame_slowness = lm.frame_slowness
layer2.refresh_cell_heights(hmap)
layer2.refresh_cell_types()

################################################################################
print("Adding objects")
fir0_img = thorpy.load_image("./mapobjects/images/fir0.png", (255,255,255))
fir0_img = thorpy.get_resized_image(fir0_img, (ZOOM_CELL_SIZES[0]-1,)*2)

char1_img = thorpy.load_image("./mapobjects/images/char1.png", (255,255,255))
char1_img = thorpy.get_resized_image(char1_img, (ZOOM_CELL_SIZES[0]-1,)*2)

forest_map = ng.generate_terrain(S,n_octaves=3) #generer sur map + grande et reduite, ou alors avec persistance +- faible suivant ce qu'on veut
ng.normalize(forest_map)

################################################################################
##objects

fir = MapObject(fir0_img)
fir.build_imgs(ZOOM_CELL_SIZES)

char1 = MapObject(char1_img)
char1.build_imgs(ZOOM_CELL_SIZES)

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

menu_button = thorpy.make_menu_button() #==> load, save, settings
box = thorpy.Element.make(elements=[topbox, #thorpy.Line.make(MENU_RECT.w-20),
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

set_zoom(0)
m = thorpy.Menu([box],fps=FPS)
m.play()



app.quit()

#pour FS: ajouter un info box quand on click sur material name, quand on click sur une cellule

