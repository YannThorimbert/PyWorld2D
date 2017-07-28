import pygame
from pygame.math import Vector2 as V2
import thorpy
import thornoise.purepython.noisegen as ng
import rendering.tilers.tilemanager as tm
from rendering.mapgrid import MapGrid
import gui.parameters as guip
import gui.elements as gui

#ergonomie => click

#thorpy: recenter()

##thorpy.application.SHOW_FPS = True
#visualiseur de map dans menu. Faire un nouveau painter et tout mettre dans ce style ?

#zoom: on genere les tilers de MAX_CELLSIZE a MIN_CELLSIZE
#   quand zoom change, cell.imgs pointe juste vers un autre #cell.imgs devient un dict ?

#objets : arbres, sapins(+ grand h), montagnes, villages, chateaux, murailles.
#materials: chemin, riviere (eau peu profonde) (a generer?)


#effets: vent dans arbres et fumee villages, ronds dans l'eau, herbe dans pieds, traces dans neige et sable, précipitations

#finalement: editeur.
#pas oublier curseur juste dans coins

#surface preproduites ? Lourd en memoire mais cool en perfs...
## ==> a faire en cas de problemes de perfs ingame

def sgn(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    return 0

def get_dpix():
    return (camposx - rmouse.x)*CELL_SIZE, (camposy - rmouse.y)*CELL_SIZE

def draw_grid():
    xpix, ypix = get_dpix()
    mg.draw(screen, xpix, ypix, mg.current_x, NXRENDER, mg.current_y, NYRENDER)

def set_current_pos():
    rmap = e_hmap.get_rect()
##    rmouse.clamp_ip(rmap)
    x, y = rmouse.topleft
    xm, ym = rmap.topleft
    mg.current_x = int((x-xm)/scale_factor)
    mg.current_y = int((y-ym)/scale_factor)

def set_campos_from_rmouse():
    global camposx, camposy #ici epsx = 0
    camposx = float(rmouse.left)
    camposy = float(rmouse.top)

def set_rmouse_from_campos():
    rmouse.top = int(camposy)
    rmouse.left = int(camposx)

def move_cam(dx,dy):
    global camposx, camposy
    camposx += dx
    camposy += dy
    set_rmouse_from_campos()

def func_reac_mousemotion(e):
    if pygame.key.get_mods() & pygame.KMOD_CTRL:
        if box_hmap.get_rect().collidepoint(e.pos):
            rmouse.center = e.pos
            set_current_pos()
            set_campos_from_rmouse()

def process_mouse_navigation():
    if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
        pos = pygame.mouse.get_pos()
        d = V2(pos) - MAP_RECT.center
        intensity = 2e-8*d.length_squared()**1.5
##        print(intensity)
        if intensity > 1.:
            intensity = 1.
        d.normalize_ip()
        dx = intensity*d.x
        dy = intensity*d.y
        dx, dy = correct_move(dx, dy)
        move_cam(dx,dy)
        set_current_pos()

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

def draw():
    draw_grid()
    screen.blit(frame_map, (0,0))
    box.blit()
    pygame.draw.rect(screen, (255,255,255), rmouse, 1)
    #
    mousepos = pygame.mouse.get_pos()
    if MAP_RECT.collidepoint(mousepos):
        coord = get_coord_at_pix(mousepos)
        if mg.is_inside(coord):
            cell = mg[coord]
            if cell_info.cell is not cell:
                pygame.draw.rect(screen, (0,0,0), get_rect_at_pix(mousepos), 1)
                cell_info.update_and_draw(cell)
##        print(x,y)
##        print("Coord =",(x,y), "h =",hmap[x][y], "Material =", cell.material.name)
    pygame.display.flip()


def func_reac_time():
    process_mouse_navigation()
    draw()
    #
    mg.next_frame()


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
S = 32
CELL_SIZE = 25
CELL_RADIUS = CELL_SIZE//8
MAX_MAP_SIZE_PIX = 128, 128

FPS = 80

MENU_SIZE = (200, H)
MENU_RECT = pygame.Rect((0,0),MENU_SIZE)
MENU_RECT.right = W
assert MENU_RECT.w > MAX_MAP_SIZE_PIX[0]

NOT_MENU_RECT = pygame.Rect((0,0),(MENU_RECT.left,MENU_RECT.bottom))

WRENDER = W-MENU_RECT.w
HRENDER = H
NXRENDER,NYRENDER = WRENDER//CELL_SIZE - 1, HRENDER//CELL_SIZE - 1
MAP_SIZE = NXRENDER*CELL_SIZE, NYRENDER*CELL_SIZE
MAP_RECT = pygame.Rect((0,0), MAP_SIZE)
MAP_RECT.centery = H//2
MAP_RECT.centerx = (W - MENU_RECT.w)//2
CELL_RECT = pygame.Rect(0,0,CELL_SIZE,CELL_SIZE)

frame_map = pygame.Surface(NOT_MENU_RECT.size)
frame_map.fill((200,200,200))
pygame.draw.rect(frame_map, (255,255,255), MAP_RECT)
frame_map.set_colorkey((255,255,255))

app = thorpy.Application((W,H), "PyWorld2D example")
screen = thorpy.get_screen()

print("Building hmap")
hmap = ng.generate_terrain(S, chunk=(1310,14)) #1310,14, S=64
##hmap = grow_map(hmap)
ng.normalize(hmap)
hmap[2][1] = 0.7
hmap[S-1][S-1] = 1.
img_hmap = ng.build_surface(hmap)

###possibility to use other sizes
##new_img_hmap = pygame.Surface((256,100))
##new_img_hmap.blit(img_hmap, (0,0))
##img_hmap = new_img_hmap

w,h = img_hmap.get_size()
if w >= h and w > MAX_MAP_SIZE_PIX[0]:
    M = MAX_MAP_SIZE_PIX[0]
    scale_factor = M / w
    sy = int(MAX_MAP_SIZE_PIX[1]*h/w)
    img_hmap = pygame.transform.smoothscale(img_hmap, (M,sy))
elif w < h and h > MAX_MAP_SIZE_PIX[1]:
    M = MAX_MAP_SIZE_PIX[1]
    scale_factor = M / h
    sx = int(MAX_MAP_SIZE_PIX[0]*w/h)
    img_hmap = pygame.transform.smoothscale(img_hmap, (sx,M))
else:
    scale_factor = 1. #to update if (un)zoom the map!!!

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
screen.fill(thorpy.style.DEF_COLOR)

mg = MapGrid(hmap, material_couples, MAP_RECT)
mg.frame_slowness = 0.1*FPS #frame will change every k*FPS [s]
print("Refreshing cell types")
mg.refresh_cell_types()

################################################################################


camposx, camposy = 0., 0.
rmouse = pygame.Rect(0, 0, NXRENDER*scale_factor, NYRENDER*scale_factor)

e_hmap = thorpy.Image.make(img_hmap)
e_hmap.stick_to("screen", "right", "right", False)
e_hmap.add_reaction(thorpy.Reaction(pygame.MOUSEMOTION, func_reac_mousemotion))
thorpy.add_time_reaction(e_hmap, func_reac_time)
box_hmap = thorpy.Box.make([e_hmap])
box_hmap.fit_children((20,20))

e_cell_infos_title = thorpy.make_text("Cell infos", guip.TFS, guip.TFC)
e_coord = thorpy.make_text("(x;y)")
e_altitude = thorpy.make_text("Altitude: h")
e_mat_img = thorpy.Image.make( mg[0,0].imgs[0])
e_mat_name = thorpy.make_text("Material name", guip.NFS, guip.NFC)
e_mat = thorpy.Clickable.make(elements=[e_mat_name, e_mat_img])
thorpy.store(e_mat)
e_mat.fit_children()
cell_info = gui.CellInfo(MAX_MAP_SIZE_PIX, CELL_RECT.size)

##import gui.elements as gui
##e_infos = thorpy.Image.make(gui.get_rounded_frame_img((100,100), 5, (0,0,0), 2))#, colorkey=(255,255,255))
##e_infos.add_elements([e_mat_name, e_coord, e_altitude])
##thorpy.store(e_infos)


quit_button = thorpy.make_button("Quit", thorpy.functions.quit_menu_func)
box = thorpy.Element.make(elements=[box_hmap, cell_info.e, quit_button],
                            size=MENU_RECT.size)
thorpy.store(box, gap=40)
box.stick_to("screen","right","right")


rmouse.topleft = e_hmap.get_rect().topleft
set_campos_from_rmouse()

thorpy.makeup.add_basic_help(box_hmap, "Hold CTRL to move camera on miniature map")
m = thorpy.Menu([box],fps=FPS)
m.play()

app.quit()


