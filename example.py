import pygame
from pygame.math import Vector2 as V2
import thorpy
import thornoise.purepython.noisegen as ng
import rendering.tilers.tilemanager as tm
from rendering.mapgrid import MapGrid
import gui.parameters as guip
import gui.elements as gui
from rendering.camera import Camera

##thorpy.application.SHOW_FPS = True

#cell.get_image() pour 2 raisons: 1) zoom, 2) personnaliser les images ==> attribut img, et changement de method plutot que if else

#objets : arbres, sapins(+ grand h), montagnes, villages, chateaux, murailles.
#units: (herite de objet)
#materials: chemin, riviere (eau peu profonde) (a generer?)



#finalement: editeur, load/save/quit

#v2:
#quand res + grande, nb de couples peut augmenter! ==> automatiser sur la base des materiaux existants

#ridged noise

#zoom: on genere les tilers de MAX_CELLSIZE a MIN_CELLSIZE
#   quand zoom change, cell.imgs pointe juste vers un autre #cell.imgs devient un dict ?

#effets: vent dans arbres et fumee villages, ronds dans l'eau, herbe dans pieds, traces dans neige et sable, précipitations

#surface preproduites ? Lourd en memoire mais cool en perfs...
## ==> a faire en cas de problemes de perfs ingame

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

def draw():
    cam.set_rmouse_from_rcam()
    #blit map and its frame
    cam.draw_grid(screen)
    screen.blit(frame_map, (0,0))
    #update right pane
    update_cell_info()
    #blit right pane and draw rect on minimap
    box.blit()
    pygame.draw.rect(screen, (255,255,255), cam.rmouse, 1)

def draw_no_update():
    cam.draw_grid(screen)
    screen.blit(frame_map, (0,0))
    box.blit()
    pygame.draw.rect(screen, (255,255,255), cam.rmouse, 1)

def func_reac_time():
    global img_cursor, idx_cursor
    process_mouse_navigation()
    draw()
    pygame.display.flip()
    #
    mg.next_frame()
    if mg.tot_time%cursor_slowness == 0:
        idx_cursor = (idx_cursor+1)%len(cursors)
        img_cursor = cursors[idx_cursor]


def func_reac_click(e):
    if e.button == 1: #left click
        if box_hmap.get_rect().collidepoint(e.pos):
            cam.center_on(e.pos)

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
            delta = -V2(e.rel)/cam.cell_size
            cam.move(delta)
            cam.set_mg_pos_from_rcam()
            cell_clicked = cam.get_cell(e.pos)

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
    return pygame.transform.smoothscale(img, CELL_RECT.size)


W, H = 900, 600
FPS = 80
app = thorpy.Application((W,H), "PyWorld2D example")
screen = thorpy.get_screen()

CELL_SIZE = 20
CELL_RADIUS = CELL_SIZE//8
CELL_RECT = pygame.Rect(0,0,CELL_SIZE,CELL_SIZE)
S = 128
MAX_MINIMAP_SIZE = 128
MAX_MINIMAP_SIZE = (MAX_MINIMAP_SIZE,)*2
MENU_SIZE = (200, H)
MENU_RECT = pygame.Rect((0,0),MENU_SIZE)
MENU_RECT.right = W
BOX_HMAP_MARGIN = 20

if MENU_RECT.w < MAX_MINIMAP_SIZE[0] + BOX_HMAP_MARGIN*2:
    s = MENU_RECT.w - BOX_HMAP_MARGIN*2 - 2
    MAX_MINIMAP_SIZE = (s,s)

VIEWPORT_RECT = pygame.Rect((0,0),(MENU_RECT.left,MENU_RECT.bottom))

print("Building hmap")
hmap = ng.generate_terrain(S, chunk=(1310,14)) #1310,14, S=64
ng.normalize(hmap)
hmap[2][1] = 0.7
hmap[S-1][S-1] = 1.
img_hmap = ng.build_surface(hmap)

#possibility to use other sizes
new_img_hmap = pygame.Surface((S,S//3))
new_img_hmap.blit(img_hmap, (0,0))
img_hmap = new_img_hmap

WORLD_SIZE = img_hmap.get_size() #can differ from hmap size!



w,h = WORLD_SIZE
if w >= h and w > MAX_MINIMAP_SIZE[0]:
    M = MAX_MINIMAP_SIZE[0]
    scale_factor = M / w #scale factor is always smaller or equal to 1
    size_y = int(MAX_MINIMAP_SIZE[1]*h/w)
    img_hmap = pygame.transform.smoothscale(img_hmap, (M,size_y))
elif w < h and h > MAX_MINIMAP_SIZE[1]:
    M = MAX_MINIMAP_SIZE[1]
    scale_factor = M / h
    size_x = int(MAX_MINIMAP_SIZE[0]*w/h)
    img_hmap = pygame.transform.smoothscale(img_hmap, (size_x,M))
else:
    scale_factor = 1. #to update if (un)zoom the map!!!

MINIMAP_SIZE = img_hmap.get_size() #can differ from WORLD_SIZE !
################################################################################

################################################################################
#USER DEFINED MATERIALS

NFRAMES = 16
WATER = "./rendering/tiles/water1.png"
SAND = "./rendering/tiles/sand1.jpg"
GRASS1 = "./rendering/tiles/grass1.png"
GRASS2 = "./rendering/tiles/grass7.png"
ROCK = "./rendering/tiles/rock1.png"
WHITE = pygame.Surface(CELL_RECT.size)
BLACK = WHITE.copy()
WHITE.fill((255,255,255))

##radiuses = get_radiuses(NFRAMES, initial_value=CELL_RADIUS-3, increment=1)
radiuses = tm.get_radiuses(NFRAMES, initial_value=CELL_RADIUS, increment=0)

deepwater = tm.get_mixed_tiles(load_image(WATER),BLACK,127)
deepwaters = tm.get_shifted_tiles(deepwater, NFRAMES, dx=CELL_SIZE//10, dy=CELL_SIZE//8)

mediumwater = tm.get_mixed_tiles(load_image(WATER),BLACK,50)
mediumwaters = tm.get_shifted_tiles(mediumwater, NFRAMES, dx=CELL_SIZE//10, dy=CELL_SIZE//8)

waters = tm.get_shifted_tiles(load_image(WATER), NFRAMES, dx=CELL_SIZE//10, dy=CELL_SIZE//8)

shore = tm.get_mixed_tiles(load_image(SAND), load_image(WATER), 127)
shores = tm.get_shifted_tiles(shore, NFRAMES, dx=CELL_SIZE//10, dy=CELL_SIZE//8)

sands = tm.get_shifted_tiles(load_image(SAND), NFRAMES, dx=0, dy=0)
grasses1 = tm.get_shifted_tiles(load_image(GRASS1), NFRAMES)
##grasses2 = tm.get_shifted_tiles(load_image(GRASS2), NFRAMES)
rocks = tm.get_shifted_tiles(load_image(ROCK), NFRAMES)

thinsnow = tm.get_mixed_tiles(load_image(ROCK), WHITE, 160)
snows1 = tm.get_shifted_tiles(thinsnow, NFRAMES)
snows2 = tm.get_shifted_tiles(WHITE, NFRAMES)

deepwater = tm.Material("Deep water", 0.1, deepwaters)
mediumwater = tm.Material("Medium water", 0.4, mediumwaters)
water = tm.Material("Water", 0.55, waters)
shore = tm.Material("Shallow water", 0.6, shores)
sand = tm.Material("Sand", 0.62, sands) #means sand below 0.65
badlands = tm.Material("Grass", 0.8, grasses1)
rock = tm.Material("Rock", 0.83, rocks)
snow1 = tm.Material("Thin snow", 0.9, snows1)
snow2 = tm.Material("Snow", float("inf"), snows2)

materials = [deepwater, mediumwater, water, shore, sand, badlands, rock, snow1, snow2]
material_couples = tm.get_material_couples(materials, radiuses)

################################################################################

cam = Camera()
cam.set_parameters(WORLD_SIZE, CELL_SIZE, VIEWPORT_RECT, MINIMAP_SIZE)

################################################################################
screen.fill(thorpy.style.DEF_COLOR)

mg = MapGrid(hmap, material_couples, cam.map_rect, WORLD_SIZE)
mg.frame_slowness = 0.1*FPS #frame will change every k*FPS [s]
print("Refreshing cell types")
mg.refresh_cell_types()

mg.cells[3][3].name = "Roflburg"

cam.set_map_data(mg)

################################################################################
frame_map = pygame.Surface(VIEWPORT_RECT.size)
frame_map.fill((200,200,200))
pygame.draw.rect(frame_map, (255,255,255), cam.map_rect)
frame_map.set_colorkey((255,255,255))

cell_clicked = None

e_hmap = thorpy.Image.make(img_hmap)
e_hmap.stick_to("screen", "right", "right", False)
e_hmap.add_reaction(thorpy.Reaction(pygame.MOUSEMOTION, func_reac_mousemotion))
e_hmap.add_reaction(thorpy.Reaction(pygame.MOUSEBUTTONDOWN, func_reac_click))
e_hmap.add_reaction(thorpy.Reaction(pygame.MOUSEBUTTONUP, func_reac_unclick))


thorpy.add_time_reaction(e_hmap, func_reac_time)
e_title_hmap = guip.get_title("Map")
box_hmap = thorpy.Box.make([e_hmap])
box_hmap.fit_children((BOX_HMAP_MARGIN,)*2)
topbox = thorpy.make_group([e_title_hmap, box_hmap], "v")

cell_info = gui.CellInfo(MENU_RECT.inflate((-10,0)).size, CELL_RECT.size, draw_no_update, e_hmap) #material, coord, alt, img, name
unit_info = gui.CellInfo(MENU_RECT.inflate((-10,0)).size, CELL_RECT.size, draw_no_update, e_hmap) #type, name, life, food, img
misc_info = gui.CellInfo(MENU_RECT.inflate((-10,0)).size, CELL_RECT.size, draw_no_update, e_hmap)

##e_help.stick_to(VIEWPORT_RECT, "bottom", "bottom", False)

##menu_button = thorpy.make_button("Quit", thorpy.functions.quit_menu_func)
menu_button = thorpy.make_menu_button() #==> load, save, settings
##quit_button = thorpy.make_button("Quit", thorpy.functions.quit_menu_func)
box = thorpy.Element.make(elements=[topbox, #thorpy.Line.make(MENU_RECT.w-20),
                                    misc_info.e, #thorpy.Line.make(MENU_RECT.w-20),
                                    cell_info.e, #thorpy.Line.make(MENU_RECT.w-20),
                                    unit_info.e, #thorpy.Line.make(MENU_RECT.w-20),
                                    menu_button],
                            size=MENU_RECT.size)
thorpy.store(box)
box.stick_to("screen","right","right")


cam.e_hmap = e_hmap
cam.box_hmap = box_hmap

cursors = gui.get_cursors(CELL_RECT.inflate((2,2)), (255,255,0))
idx_cursor = 0
img_cursor = cursors[idx_cursor]
cursor_slowness = int(0.3*FPS)

cam.rmouse.topleft = e_hmap.get_rect().topleft
cam.set_campos_from_rcam()

thorpy.makeup.add_basic_help(box_hmap, "Hold CTRL to move camera on miniature map")
m = thorpy.Menu([box],fps=FPS)
m.play()

app.quit()

#pour FS: ajouter un info box quand on click sur material name, quand on click sur une cellule



