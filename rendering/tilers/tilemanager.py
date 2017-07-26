import math
import pygame

from rendering.tilers.beachtiler import BeachTiler
from rendering.tilers.basetiler import BaseTiler
from rendering.tilers.roundtiler import RoundTiler


def get_shifted_tiles(img, nframes, dx, dy, reverse=False, sin=True):
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

class TileManager:

    def __init__(self, grasses, waters, cell_size, cell_radius):
        assert len(grasses) == len(waters)
        self.tilers = []
        self.nframes = len(grasses)
        for n in range(self.nframes):
            tiler = BeachTiler(grasses[n], waters[n])
            tiler.make(size=(cell_size,)*2, radius=cell_radius)
            self.tilers.append(tiler)
        self.time = 0
        self.current_frame = 0
        self.frame_slowness = 20

    def next_frame(self):
        self.time += 1
        if self.time % self.frame_slowness == 0:
            self.current_frame = (self.current_frame+1)%self.nframes

    def get_tile(self, name):
        return self.tilers[self.current_frame].imgs[name]