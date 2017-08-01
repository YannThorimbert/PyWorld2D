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


def get_tilers(grasses, waters, radius, cell_size):
    assert len(grasses) == len(waters)
    tilers = []
    nframes = len(grasses)
    for n in range(nframes):
        tiler = BeachTiler(grasses[n], waters[n])
        tiler.make(size=(cell_size,)*2, radius=radius)
        tilers.append(tiler)
    return tilers

def get_material_couples(materials, radius):
    materials.sort(key=lambda x:x.hmax)
    couples = []
    nframes = len(materials[0].imgs)
    cell_size = materials[0].imgs[0].get_width()
    for i in range(len(materials)-1):
        assert nframes == len(materials[i+1].imgs)
        couple = MaterialCouple(materials[i],materials[i+1],radius,cell_size)
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

    def __init__(self, material1, material2, radius, cell_size):
        assert material1.hmax != material2.hmax
        if material1.hmax > material2.hmax:
            self.grass, self.water = material1, material2
        else:
            self.grass, self.water = material2, material1
        self.tilers = get_tilers(self.grass.imgs, self.water.imgs,
                                 radius, cell_size)
        self.transition = self.water.hmax
        self.cell_size = cell_size

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


