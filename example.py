import pygame
from pygame.math import Vector2 as V2
import thorpy
import thornoise.purepython.noisegen as ng
from rendering.tilers.tilemanager import TileManager, get_shifted_tiles
from rendering.mapgrid import MapGrid

#navigation
#autres tiles. Plages ? nb arbitraire de materials...
#si terrain crop, croper aussi hmap pour perfs!

W, H = 900, 600
S = 128
CELL_SIZE = 25
CELL_RADIUS = CELL_SIZE//6
MAX_MAP_SIZE_PIX = 128, 128

FPS = 80

MENU_SIZE = (200,H)
MENU_RECT = pygame.Rect((0,0),MENU_SIZE)
MENU_RECT.right = W

MARGIN_NAV = (50, 50)
NOT_MENU_RECT = pygame.Rect((0,0),(MENU_RECT.left,MENU_RECT.bottom))
NOT_MENU_RECT_DEFLATED = NOT_MENU_RECT.inflate(MARGIN_NAV[0], MARGIN_NAV[1])

WRENDER = W-MENU_RECT.w
HRENDER = H
NXRENDER,NYRENDER = WRENDER//CELL_SIZE-1, HRENDER//CELL_SIZE-1
MAP_SIZE = NXRENDER*CELL_SIZE, NYRENDER*CELL_SIZE
MAP_RECT = pygame.Rect((0,0), MAP_SIZE)
MAP_RECT.centery = H//2
MAP_RECT.centerx = (W - MENU_RECT.w)//2

app = thorpy.Application((W,H), "PyWorld2D example")
screen = thorpy.get_screen()

print("Building hmap")
hmap = ng.generate_terrain(S)
ng.normalize(hmap)
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

##e_hmap.unblit_and_reblit()
##app.pause()

################################################################################

GRASS = "./rendering/tiles/grass1.png"
WATER = "./rendering/tiles/water1.png"
NFRAMES = 16
grasses = get_shifted_tiles(thorpy.load_image(GRASS), NFRAMES, dx=0, dy=0)
waters = get_shifted_tiles(thorpy.load_image(WATER), NFRAMES, dx=5, dy=7)
tm = TileManager(grasses, waters, CELL_SIZE, CELL_RADIUS)
tm.frame_slowness = 0.2*FPS #frame will change every k*FPS [s]

###############################################################################
##screen.fill((255,255,255))
##x = 0
##y = 0
##i = 0
##tiler = tm.tilers[0]
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

mg = MapGrid(hmap, CELL_SIZE, MAP_RECT.topleft)
print("Refreshing cell types")
mg.refresh_cell_types()

rmouse = pygame.Rect(0, 0, NXRENDER*scale_factor, NYRENDER*scale_factor)

def draw_grid():
    mg.draw(screen, mg.current_x, NXRENDER, mg.current_y, NYRENDER, tm)


def set_current_pos():
    rmap = e_hmap.get_rect()
    rmouse.clamp_ip(rmap)
    x, y = rmouse.topleft
    xm, ym = rmap.topleft
    mg.current_x = int((x-xm)/scale_factor)
    mg.current_y = int((y-ym)/scale_factor)
    box.blit()
    pygame.draw.rect(screen, (255,255,255), rmouse, 1)
    box.update()



def func_reac_mousemotion(e):
    if pygame.key.get_mods() & pygame.KMOD_CTRL:
        if box_hmap.get_rect().collidepoint(e.pos):
            rmouse.center = e.pos
            set_current_pos()
    else:
        if not(NOT_MENU_RECT_DEFLATED.collidepoint(e.pos)):
            if NOT_MENU_RECT.collidepoint(e.pos):#then we are near the border
                displ = V2(e.pos)-NOT_MENU_RECT.center
                rmouse.move_ip(displ//10)
                print(displ, displ//10)

def func_reac_time():
    draw_grid()
    pygame.display.flip()
    tm.next_frame()

e_hmap.add_reaction(thorpy.Reaction(pygame.MOUSEMOTION, func_reac_mousemotion))
thorpy.add_time_reaction(e_hmap, func_reac_time)

box_hmap = thorpy.Box.make([e_hmap])
box_hmap.fit_children((20,20))

################################################################################


quit_button = thorpy.make_button("Quit", thorpy.functions.quit_menu_func)
box = thorpy.Box.make([box_hmap, quit_button], size=MENU_RECT.size)
box.stick_to("screen","right","right")


m = thorpy.Menu([box],fps=FPS)
m.play()

app.quit()


