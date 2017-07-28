import pygame
from pygame.math import Vector2 as V2
import thorpy
import thornoise.purepython.noisegen as ng
import rendering.tilers.tilemanager as tm
from rendering.mapgrid import MapGrid


##thorpy.application.SHOW_FPS = True

#en fait camposx devrait direct etre le deltapix
#autres tiles. Plages ? nb arbitraire de materials...

#surface preproduites ? Lourd en memoire mais cool en perfs...

def sgn(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    return 0

def draw_grid():
    xpix = (camposx - rmouse.x)*CELL_SIZE
    ypix = (camposy - rmouse.y)*CELL_SIZE
    mg.draw(screen, xpix, ypix, mg.current_x, NXRENDER, mg.current_y, NYRENDER)

def set_current_pos():
    rmap = e_hmap.get_rect()
##    rmouse.clamp_ip(rmap)
    x, y = rmouse.topleft
    xm, ym = rmap.topleft
    mg.current_x = int((x-xm)/scale_factor)
    mg.current_y = int((y-ym)/scale_factor)

def set_campos_from_rmouse():
    global camposx, camposy
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
        x, y = get_coord_at_pix(mousepos)
##        cell = mg[x,y]
        pygame.draw.rect(screen, (0,0,0), get_rect_at_pix(mousepos),1)
        print(x,y)
##        print("Coord =",(x,y), "h =",hmap[x][y], "Material =", cell.material.name)
    pygame.display.flip()

def func_reac_time():
    process_mouse_navigation()
    draw()
    #
    mg.next_frame()


def get_rect_at_coord(coord):
    dx = (camposx - rmouse.x)*CELL_SIZE
    dy = (camposy - rmouse.y)*CELL_SIZE
    #
    shift_x = (coord[0] - mg.current_x + 1) * CELL_SIZE - int(dx)
    shift_y = (coord[1] - mg.current_y + 1) * CELL_SIZE - int(dy)
    return CELL_RECT.move((shift_x, shift_y)).move(MAP_RECT.topleft)

def get_coord_at_pix(pix):
    dx = (camposx - rmouse.x)*CELL_SIZE
    dy = (camposy - rmouse.y)*CELL_SIZE
    #
    x = pix[0] - MAP_RECT.x + dx
    y = pix[1] - MAP_RECT.y + dy
    cx = int(x * NXRENDER / MAP_RECT.width)
    cy = int(y * NYRENDER / MAP_RECT.height)
    return (cx + mg.current_x - 1, cy + mg.current_y - 1)

def get_rect_at_pix(pix):
    return get_rect_at_coord(get_coord_at_pix(pix))

GRASS = "./rendering/tiles/grass1.png"
WATER = "./rendering/tiles/water1.png"
SAND = "./rendering/tiles/sand1.jpg"

W, H = 900, 600
S = 128
CELL_SIZE = 25
CELL_RADIUS = CELL_SIZE//6
MAX_MAP_SIZE_PIX = 128, 128

FPS = 80

MENU_SIZE = (200, H)
MENU_RECT = pygame.Rect((0,0),MENU_SIZE)
MENU_RECT.right = W

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
hmap = ng.generate_terrain(S, chunk=(1310,14))
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

e_hmap = thorpy.Image.make(img_hmap)
e_hmap.stick_to("screen", "right", "right", False)
e_hmap.move((-5,-5))

################################################################################

NFRAMES = 16

##radiuses = get_radiuses(NFRAMES, initial_value=CELL_RADIUS-3, increment=1)
radiuses = tm.get_radiuses(NFRAMES, initial_value=CELL_RADIUS, increment=0)
waters = tm.get_shifted_tiles(thorpy.load_image(WATER), NFRAMES, dx=CELL_SIZE//5, dy=CELL_SIZE//4)
sands = tm.get_shifted_tiles(thorpy.load_image(SAND), NFRAMES, dx=0, dy=0)
grasses = tm.get_shifted_tiles(thorpy.load_image(GRASS), NFRAMES, dx=0, dy=0)

water = tm.Material("Water", 0.6, waters)
sand = tm.Material("Sand", 0.85, sands)
grass = tm.Material("Grass", float("inf"), grasses)

materials = [water, sand, grass]
material_couples = tm.get_material_couples(materials, radiuses, CELL_SIZE)


###############################################################################
##screen.fill((255,255,255))
##x = 0
##y = 0
##i = 0
##tiler = tilemanager.tilers[0]
##keys = list(tiler.imgs.keys())
##keys.sort()
##for key in keys:
##    img = tiler.imgs[key]
##    rect = img.get_rect()
##    rect.topleft = (x,y)
##    screen.blit(img, rect.topleft)
##    pygame.draw.rect(screen, (0,0,0), rect, 1)
##    text = thorpy.make_text(key+" "+str(i), font_color=(255,255,255),
##                            font_size=CELL_SIZE//4)
##    text.set_center(rect.center)
##    text.blit()
##    x += CELL_SIZE
##    if x >= W - CELL_SIZE:
##        x = 0
##        y += CELL_SIZE
##    i += 1
####    print(i,x,y)
##pygame.display.flip()
##app.pause()

################################################################################
screen.fill(thorpy.style.DEF_COLOR)

mg = MapGrid(hmap, material_couples, MAP_RECT)
mg.frame_slowness = 0.1*FPS #frame will change every k*FPS [s]
print("Refreshing cell types")
mg.refresh_cell_types()


camposx, camposy = 0., 0.
rmouse = pygame.Rect(0, 0, NXRENDER*scale_factor, NYRENDER*scale_factor)

e_hmap.add_reaction(thorpy.Reaction(pygame.MOUSEMOTION, func_reac_mousemotion))
thorpy.add_time_reaction(e_hmap, func_reac_time)

box_hmap = thorpy.Box.make([e_hmap])
box_hmap.fit_children((20,20))

################################################################################

quit_button = thorpy.make_button("Quit", thorpy.functions.quit_menu_func)
box = thorpy.Box.make([box_hmap, quit_button], size=MENU_RECT.size)
box.stick_to("screen","right","right")

thorpy.makeup.add_basic_help(e_hmap, "Hold CTRL to move camera on miniature map")

rmouse.topleft = e_hmap.get_rect().topleft
set_campos_from_rmouse()

m = thorpy.Menu([box],fps=FPS)
m.play()

app.quit()


