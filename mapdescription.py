import pygame
import thornoise.purepython.noisegen as ng
import rendering.tilers.tilemanager as tm

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
    return hmap

def build_materials(me):
    #might be chosen by user:
    #cell_radius = cell_size//radius_divider
    # change how "round" look cell transitions
    cell_radius_divider = 8
    #we load simple images - they can be of any size, they will be resized
    water_img = me.load_image("./rendering/tiles/water1.png")
    sand_img = me.load_image("./rendering/tiles/sand1.jpg")
    grass_img = me.load_image("./rendering/tiles/grass1.png")
    grass_img2 = me.load_image("./rendering/tiles/grass8.png")
    rock_img = me.load_image("./rendering/tiles/rock1.png")
    black_img = me.get_color_image((0,0,0))
    white_img = me.get_color_image((255,255,255))
    #mixed images - we superimpose different image to make a new one
    deepwater_img = tm.get_mixed_tiles(water_img, black_img, 127)
    mediumwater_img = tm.get_mixed_tiles(water_img, black_img, 50)
    shore_img = tm.get_mixed_tiles(sand_img, water_img, 127) # alpha of water is 127
    thinsnow_img = tm.get_mixed_tiles(rock_img, white_img, 200)
    ##river_img = tm.get_mixed_tiles(rock_img, water_img, 200)
    river_img = shore_img
    #water movement is obtained by using a delta-x (dx_divider) and delta-y shifts,
    # here dx_divider = 10 and dy_divider = 8
    #hmax=0.1 means one will find deepwater only below height = 0.1
    ##deepwater = me.add_material("Very deep water", 0.1, deepwater_img, 10, 8)
    me.add_material("Deep water", 0.4, mediumwater_img, 10, 8)
    me.add_material("Water", 0.55, water_img, 10, 8)
    me.add_material("Shallow water", 0.6, shore_img, 10, 8)
    me.add_material("Sand", 0.62, sand_img)
    me.add_material("Grass", 0.8, grass_img)
    ##me.add_material("Grass", 0.8, grass_img2, id_="Grass2")
    me.add_material("Rock", 0.83, rock_img)
    me.add_material("Thin snow", 0.9, thinsnow_img)
    me.add_material("Snow", float("inf"), white_img)
    #Outside material is mandatory. The only thing you can change is black_img
    outside = me.add_material("outside", -1, black_img)
    #this is the heavier computing part, especially if the maximum zoom is large:
    print("Building material couples")
    #fast option: quality a bit lower, loading time a bit faster
    #use_beach_tiler option: quality much better, loading time much slower. Need numpy.
    #load_tilers option: use precomputed textures from disk
    me.build_materials(cell_radius_divider, fast=True, use_beach_tiler=False,
                        load_tilers=False)
    ##                    load_tilers="./rendering/tiles/precomputed/")
    ##me.save_tilers("./rendering/tiles/precomputed/")
    ##import sys;app.quit();pygame.quit();sys.exit();exit()