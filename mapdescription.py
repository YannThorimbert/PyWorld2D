import pygame
import thornoise.purepython.noisegen as ng

def build_hmap(me):
    hmap = me.build_hmap()
    S = len(hmap)
    ##hmap[2][1] = 0.7 #this is how you manually change the height of a given cell

    #Here we build the miniature map image
    img_hmap = ng.build_surface(hmap)
    new_img_hmap = pygame.Surface(me.world_size)
    new_img_hmap.blit(img_hmap, (0,0))
    img_hmap = new_img_hmap
    me.build_camera(img_hmap)