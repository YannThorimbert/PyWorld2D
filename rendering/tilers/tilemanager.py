import math
import pygame
import thorpy

from rendering.tilers.beachtiler import BeachTiler
from rendering.tilers.basetiler import BaseTiler
from rendering.tilers.roundtiler import RoundTiler

def get_mixed_tiles(img1, img2, alpha_img_2):
    i1 = img1.copy()
    i2 = img2.copy()
    i2.set_alpha(alpha_img_2)
    i1.blit(i2,(0,0))
    return i1

def get_shifted_tiles(img, nframes, dx=0, dy=0, reverse=False, sin=True):
    w, h = img.get_size()
    s = pygame.Surface((2*w,2*h))
    s.blit(img, (0,0))
    s.blit(img, (w,0))
    s.blit(img, (0,h))
    s.blit(img, (w,h))
    #now we just have to take slices
    images = []
    for i in range(nframes):
        if sin:
            delta_x = dx*math.sin(2.*math.pi*i/float(nframes))
            delta_y = dy*math.sin(2.*math.pi*i/float(nframes))
        else:
            delta_x = i*dx
            delta_y = i*dy
        result = pygame.Surface((w,h))
        result.blit(s,(delta_x-w//2,delta_y-h//2))
        images.append(result)
    if reverse:
        images += images[::-1][1:-1]
    return images

def build_tiles(img_fullsize, sizes, nframes, dx_divider=0, dy_divider=0,
                reverse=False, sin=True):
    imgs = []
    for size in sizes:
        img = pygame.transform.smoothscale(img_fullsize, (size,)*2)
        dx = 0
        if dx_divider:
            dx = size//dx_divider
        dy = 0
        if dy_divider:
            dy = size//dy_divider
        imgs.append(get_shifted_tiles(img, nframes, dx, dy, reverse, sin))
    return imgs

def get_radiuses(nframes, initial_value, increment, reverse=False, sin=True):
    values = []
    if sin:
        current = initial_value
    else:
        current = 0
    for i in range(nframes):
        if sin:
            delta = increment*math.sin(2.*math.pi*i/float(nframes))
        else:
            delta = increment
        current += delta
        values.append(int(current))
    if reverse:
        values = values[::-1][1:-1]
    return values


def build_tilers(grasses, waters, radius_divider):
    nzoom = len(grasses)
    assert nzoom == len(waters) #same number of zoom levels
    nframes = len(grasses[0])
    for z in range(nzoom):
        assert nframes == len(waters[z]) #same number of frames
    tilers = [[None for n in range(nframes)] for z in range(nzoom)]
    for z in range(nzoom):
        cell_size = grasses[z][0].get_width()
        radius = cell_size//radius_divider
        for n in range(nframes):
            tiler = BeachTiler(grasses[z][n], waters[z][n])
            tiler.make(size=(cell_size,)*2, radius=radius)
            tilers[z][n] = tiler
    return tilers

def get_material_couples(materials, radius_divider):
    materials.sort(key=lambda x:x.hmax)
    couples = []
    imgs_zoom0_mat0 = materials[0].imgs[0]
    nframes = len(imgs_zoom0_mat0)
    max_cell_size = imgs_zoom0_mat0[0].get_width()
    for i in range(len(materials)-1):
        print("     Building tilers for couple",i)
        assert nframes == len(materials[i+1].imgs[0])
        couple = MaterialCouple(materials[i],materials[i+1],radius_divider,max_cell_size)
        couples.append(couple)
    return couples

def get_couple(h, couples):
    if h < 0.:
        return couples[0]
    else:
        for couple in couples:
            if couple.grass.hmax > h:
                return couple
    return couples[-1]

class Material:

    def __init__(self, name, hmax, imgs):
        self.name = name
        self.hmax = hmax
        self.imgs = imgs

class MaterialCouple:

    def __init__(self, material1, material2, radius_divider, max_cell_size):
        assert material1.hmax != material2.hmax
        if material1.hmax > material2.hmax:
            self.grass, self.water = material1, material2
        else:
            self.grass, self.water = material2, material1
        self.tilers = build_tilers(self.grass.imgs, self.water.imgs, radius_divider)
        self.transition = self.water.hmax
        self.max_cell_size = max_cell_size

    def get_tilers(self, zoom):
        return self.tilers[zoom]

    def get_cell_size(self, zoom):
        return self.tilers[zoom][0].imgs["c"].get_width()

    def get_all_frames(self, zoom, type_):
        return [self.tilers[zoom][t].imgs[type_] for t in range(len(self.tilers[zoom]))]

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


