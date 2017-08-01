import pygame
from pygame.math import Vector2 as V2
import thorpy
import thornoise.purepython.noisegen as ng
import rendering.tilers.tilemanager as tm
from rendering.mapgrid import MapGrid
import gui.parameters as guip
import gui.elements as gui

##thorpy.application.SHOW_FPS = True

#finir le chantier de cam
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

def sgn(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    return 0

def get_dpix():
    return (camposx - rcam.x)*CELL_SIZE, (camposy - rcam.y)*CELL_SIZE

def draw_grid():
    xpix, ypix = get_dpix()
    mg.draw(screen, xpix, ypix, mg.current_x, NXRENDER, mg.current_y, NYRENDER)
    screen.blit(frame_map, (0,0))

def set_mg_pos_from_rcam():
    mg.current_x = int(rcam.x)
    mg.current_y = int(rcam.y)

def set_campos_from_rcam():
    global camposx, camposy #ici dpix = 0
    camposx = float(rcam.left)
    camposy = float(rcam.top)

def set_rcam_from_campos():
    rcam.top = int(camposy)
    rcam.left = int(camposx)

def set_rcam_from_rmouse():
    rminimap = e_hmap.get_rect()
    #dc/ws = dm/ms ==> dc = dm*ws/ms
    rcam.x = (rmouse.x - rminimap.x)*WORLD_SIZE[0]/MINIMAP_SIZE[0]
    rcam.y = (rmouse.y - rminimap.y)*WORLD_SIZE[1]/MINIMAP_SIZE[1]

def set_rmouse_from_rcam():
    rminimap = e_hmap.get_rect()
    rmouse.x = rcam.x*MINIMAP_SIZE[0]/WORLD_SIZE[0] + rminimap.x
    rmouse.y = rcam.y*MINIMAP_SIZE[1]/WORLD_SIZE[1] + rminimap.y
##    rmouse.x = rcam.x//scale_factor + rminimap.x
##    rmouse.y = rcam.y/scale_factor + rminimap.y

def move_cam(dx,dy):
    global camposx, camposy
    camposx += dx
    camposy += dy
    set_rcam_from_campos()


def get_cell(pix):
    if MAP_RECT.collidepoint(pix):
        coord = get_coord_at_pix(pix)
        if mg.is_inside(coord):
            return mg[coord]

def func_reac_click(e):
    if e.button == 1: #left click
        if box_hmap.get_rect().collidepoint(e.pos):
            center_cam_on(e.pos)
##        else:
##            cell = get_cell(e.pos)
##            if cell:
##                want_cell_info = cell, e.pos
##                cell_info.launch_em(cell, e.pos, MAP_RECT)

def func_reac_unclick(e):
    global cell_clicked
    if e.button == 1:
        cell = get_cell(e.pos)
        if cell:
            if cell is not cell_clicked:
                if not cell_info.launched:
                    cell_clicked = cell
                    cell_info.launch_em(cell, e.pos, MAP_RECT)
        cell_clicked = None


def center_cam_on(pos):
    if box_hmap.get_rect().collidepoint(pos):
        rmouse.center = pos
        set_rcam_from_rmouse()
        set_mg_pos_from_rcam()
        set_campos_from_rcam()

cell_clicked = None
def func_reac_mousemotion(e):
    global cell_clicked
##    if pygame.key.get_mods() & pygame.KMOD_CTRL:
    if pygame.mouse.get_pressed()[0]:
        if box_hmap.get_rect().collidepoint(e.pos):
            center_cam_on(e.pos)
        elif MAP_RECT.collidepoint(e.pos):
            move_cam(-e.rel[0]/CELL_SIZE,-e.rel[1]/CELL_SIZE)
            set_mg_pos_from_rcam()
            cell_clicked = get_cell(e.pos)

def process_mouse_navigation(): #cam can move even with no mousemotion!
    if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
        pos = pygame.mouse.get_pos()
        d = V2(pos) - MAP_RECT.center
        intensity = 2e-8*d.length_squared()**1.5
        if intensity > 1.:
            intensity = 1.
        d.normalize_ip()
        dx = intensity*d.x
        dy = intensity*d.y
        dx, dy = correct_move(dx, dy)
        move_cam(dx,dy)
        set_mg_pos_from_rcam()

def correct_move(dx,dy):
    if mg.current_x + NXRENDER > mg.nx + 2 and dx > 0:
        dx = 0
    elif mg.current_x < -2 and dx < 0:
        dx = 0
    if mg.current_y + NYRENDER > mg.ny + 2 and dy > 0:
        dy = 0
    elif mg.current_y < -2 and dy < 0:
        dy = 0
    return dx, dy

def update_cell_info():
    mousepos = pygame.mouse.get_pos()
    cell = get_cell(mousepos)
    if cell:
##        pygame.draw.rect(screen, (0,0,0), get_rect_at_pix(mousepos), 1)
        rcursor = img_cursor.get_rect()
        rcursor.center = get_rect_at_pix(mousepos).center
        screen.blit(img_cursor, rcursor)
        if cell_info.cell is not cell:
            cell_info.update_e(cell)


def draw():
    set_rmouse_from_rcam()
    #blit map and its frame
    draw_grid()
    #update right pane
    update_cell_info()
    #blit right pane and draw rect on minimap
    box.blit()
    pygame.draw.rect(screen, (255,255,255), rmouse, 1)

def draw_no_update():
    draw_grid()
    box.blit()
    pygame.draw.rect(screen, (255,255,255), rmouse, 1)

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


def get_rect_at_coord(coord):
    dx, dy = get_dpix()
    #
    shift_x = (coord[0] - mg.current_x + 1) * CELL_SIZE - int(dx)
    shift_y = (coord[1] - mg.current_y + 1) * CELL_SIZE - int(dy)
    return CELL_RECT.move((shift_x, shift_y)).move(MAP_RECT.topleft)

def get_coord_at_pix(pix):
    dx, dy = get_dpix()
    #
    x = pix[0] - MAP_RECT.x + dx
    y = pix[1] - MAP_RECT.y + dy
    cx = int(x * NXRENDER / MAP_RECT.width)
    cy = int(y * NYRENDER / MAP_RECT.height)
    return (cx + mg.current_x - 1, cy + mg.current_y - 1)

def get_rect_at_pix(pix):
    return get_rect_at_coord(get_coord_at_pix(pix))

def grow_map(hmap):
    global S
    newhmap = [[0. for x in range(2*S)] for y in range(2*S)]
    for x in range(S):
        x2 = 2*x
        for y in range(S):
            y2 = 2*y
            h = hmap[x][y]
            newhmap[x2][y2] = h
            newhmap[x2+1][y2] = h
            newhmap[x2][y2+1] = h
            newhmap[x2+1][y2+1] = h
    S *= 2
    return newhmap


def load_image(fn):
    img = thorpy.load_image(fn)
    return pygame.transform.smoothscale(img, CELL_RECT.size)


W, H = 900, 600
app = thorpy.Application((W,H), "PyWorld2D example")
screen = thorpy.get_screen()

CELL_SIZE = 20
CELL_RADIUS = CELL_SIZE//8
CELL_RECT = pygame.Rect(0,0,CELL_SIZE,CELL_SIZE)


################################################################################

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
#WORLD : total map (img_hmap)
#MINIMAP : minimap, shows the world
#MAP : part of the world displayed in the view port

S = 128
MAX_MINIMAP_SIZE = 128

##REDUC = MAX_WORLD_SIZEc // MAX_MINIMAP_SIZE
MAX_MINIMAP_SIZE = (MAX_MINIMAP_SIZE,)*2

FPS = 80
MENU_SIZE = (200, H)
MENU_RECT = pygame.Rect((0,0),MENU_SIZE)
MENU_RECT.right = W
BOX_HMAP_MARGIN = 20

if MENU_RECT.w < MAX_MINIMAP_SIZE[0] + BOX_HMAP_MARGIN*2:
    s = MENU_RECT.w - BOX_HMAP_MARGIN*2 - 2
    MAX_MINIMAP_SIZE = (s,s)

VIEWPORT_RECT = pygame.Rect((0,0),(MENU_RECT.left,MENU_RECT.bottom))

NXRENDER = VIEWPORT_RECT.w//CELL_SIZE - 1
NYRENDER = VIEWPORT_RECT.h//CELL_SIZE - 1
MAP_SIZE = NXRENDER*CELL_SIZE, NYRENDER*CELL_SIZE
MAP_RECT = pygame.Rect((0,0), MAP_SIZE)
MAP_RECT.centery = H//2
MAP_RECT.centerx = (W - MENU_RECT.w)//2

frame_map = pygame.Surface(VIEWPORT_RECT.size)
frame_map.fill((200,200,200))
pygame.draw.rect(frame_map, (255,255,255), MAP_RECT)
frame_map.set_colorkey((255,255,255))


print("Building hmap")
hmap = ng.generate_terrain(S, chunk=(1310,14)) #1310,14, S=64
##hmap = grow_map(hmap)
ng.normalize(hmap)
hmap[2][1] = 0.7
hmap[S-1][S-1] = 1.
img_hmap = ng.build_surface(hmap)

#possibility to use other sizes
new_img_hmap = pygame.Surface((S,S//3))
new_img_hmap.blit(img_hmap, (0,0))
img_hmap = new_img_hmap

WORLD_SIZE = img_hmap.get_size() #can differ from hmap!

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

camposx, camposy = 0., 0.
rcam = pygame.Rect(0, 0, NXRENDER, NYRENDER)
rmouse = pygame.Rect(0, 0, int(MINIMAP_SIZE[0]*NXRENDER/WORLD_SIZE[0]),
                            int(MINIMAP_SIZE[1]*NYRENDER/WORLD_SIZE[1]))


################################################################################
screen.fill(thorpy.style.DEF_COLOR)

mg = MapGrid(hmap, material_couples, MAP_RECT, WORLD_SIZE)
mg.frame_slowness = 0.1*FPS #frame will change every k*FPS [s]
print("Refreshing cell types")
mg.refresh_cell_types()

mg.cells[3][3].name = "Roflburg"

################################################################################



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


cursors = gui.get_cursors(CELL_RECT.inflate((2,2)), (255,255,0))
idx_cursor = 0
img_cursor = cursors[idx_cursor]
cursor_slowness = int(0.3*FPS)

rmouse.topleft = e_hmap.get_rect().topleft
set_campos_from_rcam()

thorpy.makeup.add_basic_help(box_hmap, "Hold CTRL to move camera on miniature map")
m = thorpy.Menu([box],fps=FPS)
m.play()

app.quit()

#pour FS: ajouter un info box quand on click sur material name, quand on click sur une cellule


