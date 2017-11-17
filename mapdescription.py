import pygame
import thornoise.purepython.noisegen as ng
import rendering.tilers.tilemanager as tm

def configure_map_editor(me):
    ##me.zoom_cell_sizes = [32, 20, 16, 12, 8] #side in pixels of the map's square cells
    ##me.zoom_cell_sizes = [64, 32, 12, 8]
    me.zoom_cell_sizes = [32,12]
    me.nframes = 16 #number of frames per world cycle (impact the need in memory!)
    me.fps = 60 #frame per second
    me.menu_width = 200 #width of the right menu in pixels
    me.max_wanted_minimap_size = 64 #in pixels
    me.world_size = (64,16) #in number of cells. Put a power of 2 for tilable maps
    me.chunk = (1310,14) #to give when saving. Neighboring chunk give tilable maps.
    me.persistance = 2.
    me.n_octaves = "max"
    me.refresh_derived_parameters()

def build_hmap(me):
    hmap = me.build_hmap()
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
##                        load_tilers="./rendering/tiles/precomputed/")
    ##me.save_tilers("./rendering/tiles/precomputed/")
    ##import sys;app.quit();pygame.quit();sys.exit();exit()


def add_static_objects(me):
    #1) We use another hmap to decide where we want trees
    S = len(me.lm)
    forest_map = ng.generate_terrain(S, n_octaves=None, persistance=1.7, chunk=(12,23))
    ng.normalize(forest_map)
    #we can use as many layers as we want.
    #layer2 is a superimposed map on which we decide to blit some static objects:
    layer2 = me.add_layer()
    #3) We build the objects that we want.
    # its up to you to decide what should be the size of the object...
    # the size is set through the imgs_dict argument of get_distributor
    fir1 = MapObject(me,"./mapobjects/images/yar_fir1.png","forest",1.5)
    fir2 = MapObject(me,"./mapobjects/images/yar_fir2.png","forest",1.5)
    fir3 = MapObject(me,"./mapobjects/images/firsnow2.png","forest",1.5)
    fir1.set_same_type([fir2, fir3])
    tree = MapObject(me,"./mapobjects/images/tree.png","forest",1.5)
    palm = MapObject(me,"./mapobjects/images/skeddles.png","forest",1.7)
    palm.max_relpos[0] = 0.1 #restrict because they are near to water
    palm.min_relpos[0] = -0.1
    bush = MapObject(me,"./mapobjects/images/yar_bush.png","bush",1.)
    village1 = MapObject(me,"./mapobjects/images/pepperRacoon.png","village",1.3)
    village2 = MapObject(me,"./mapobjects/images/rgbfumes1.png","village",2.2)
    village3 = MapObject(me,"./mapobjects/images/rgbfumes2.png","village",2.6)
    village4 = MapObject(me,"./mapobjects/images/rgbfumes3.png","village",2.6)
    ##village5 = MapObject(me,"./mapobjects/images/rgbfumes4.png","village",2.2)
    village1.set_same_type([village2, village3, village4])
    #
    cobble = MapObject(me,"./mapobjects/images/cobblestone2.png","cobblestone",1.)
    wood = MapObject(me,"./mapobjects/images/wood1.png","wooden bridge",1.)
    #
    magic = MapObject(me,
                     [  "./mapobjects/images/wood1.png",
                        "./mapobjects/images/yar_bush.png"],
                     "magic",1.)
    #
    gru = objs.put_static_obj(magic, me.lm, (12,12), layer2)
    gru.frame_slowness = 12
    #
    for v in[village1,village2,village3,village4]:
        v.max_relpos = [0., 0.]
        v.min_relpos = [0., 0.]
    #4) we add the objects via distributors
    distributor = objs.get_distributor(me, [fir1, fir2, tree], forest_map, ["Grass","Rock"])
    distributor.distribute_objects(layer2)

    distributor = objs.get_distributor(me, [tree], forest_map, ["Grass"])
    distributor.max_density = 1
    distributor.homogeneity = 0.1
    distributor.zones_spread = [(0.5,0.2)]
    distributor.distribute_objects(layer2)

    distributor = objs.get_distributor(me, [fir3, fir3.flip()],
                                    forest_map, ["Thin snow","Snow"])
    distributor.homogeneity = 0.5
    distributor.distribute_objects(layer2)


    distributor = objs.get_distributor(me, [palm, palm.flip()], forest_map, ["Sand"])
    distributor.max_density = 1
    distributor.homogeneity = 0.5
    distributor.zones_spread = [(0., 0.05), (0.3,0.05), (0.6,0.05)]
    distributor.distribute_objects(layer2)

    distributor = objs.get_distributor(me, [bush], forest_map, ["Grass"])
    distributor.max_density = 2
    distributor.homogeneity = 0.2
    distributor.zones_spread = [(0., 0.05), (0.3,0.05), (0.6,0.05)]
    distributor.distribute_objects(layer2)

    distributor = objs.get_distributor(me,
                            [village1, village1.flip(), village2, village2.flip(),
                             village3, village3.flip(), village4, village4.flip()],
                            forest_map, ["Grass"], limit_relpos_y=False)
    distributor.max_density = 1
    distributor.homogeneity = 0.05
    distributor.zones_spread = [(0.1, 0.05), (0.2,0.05), (0.4,0.05)]
    distributor.distribute_objects(layer2, exclusive=True)


    cobbles = [cobble, cobble.flip(True,False), cobble.flip(False,True), cobble.flip(True,True)]

    ################################################################################
    #Here we show how to use the path finder for a given unit of the game

    costs_materials = {name:1. for name in me.materials}
    costs_materials["Snow"] = 10. #unit is 10 times slower in snow
    costs_materials["Thin snow"] = 2.
    costs_materials["Sand"] = 2.
    for name in me.materials:
        if "water" in name.lower():
            costs_materials[name] = 1.1
    costs_objects = {bush.object_type: 2., #unit is 2 times slower in bushes
                     cobble.object_type: 0.9}
    #Materials allowed (here we allow water because we add bridges)
    possible_materials=list(me.materials)
    #Objects allowed
    possible_objects=[cobble.object_type, bush.object_type, village1.object_type]

    for i in range(5):
        objs.add_random_road(lm, layer2, cobbles, [wood], costs_materials,
                         costs_objects, possible_materials, possible_objects)


    costs_materials = {name:1. for name in me.materials}
    ##costs_materials["Snow"] = 10. #unit is 10 times slower in snow
    ##costs_materials["Thin snow"] = 2.
    ##costs_materials["Sand"] = 2.
    ##costs_objects = {bush.object_type: 2.}
    #Materials allowed (here we allow water because we add bridges)
    possible_materials=list(me.materials)
    #Objects allowed
    possible_objects=[]

    for i in range(5):
        objs.add_random_river(me, lm, river_img, costs_materials, costs_objects,
                                possible_materials, possible_objects)

    # sp = BranchAndBoundForMap(lm, lm.cells[15][15], lm.cells[8][81],
    #                         costs_materials, costs_objects,
    #                         possible_materials, possible_objects)
    # path = sp.solve()
    # draw_path(path, objects=cobbles, layer=lm)