import pygame
import thornoise.purepython.noisegen as ng
import rendering.tilers.tilemanager as tm
from mapobjects.objects import MapObject
import mapobjects.objects as objs


class MapInitializer:

    def __init__(self, name):
        self.name = name #name of the map
        #terrain generation:
        self.world_size = (128,128) #in number of cells. Put a power of 2 for tilable maps
        self.chunk = (1310,14) #Used for random generation. To give when saving. Neighboring chunk give tilable maps.
        self.persistance = 2. #parameter of the random terrain generation.
        self.n_octaves = "max" #parameter of the random terrain generation.
        #graphical options:
        self.zoom_cell_sizes = [32, 16, 8] #size of one cell for the different zoom levels.
        self.nframes = 16 #number of frames per world cycle (impacts memory requirement!)
        self.fps = 60 #frame per second
        self.menu_width = 200 #width of the right menu in pixels
        self.max_wanted_minimap_size = 64 #size of the MINIMAP in pixels
        #


FRAME_K = 0.1

def configure_map_editor(me):
    """Set the properties of the map editor"""
    ##me.zoom_cell_sizes = [32, 20, 16, 12, 8] #side in pixels of the map's square cells
    ##me.zoom_cell_sizes = [64, 32, 12, 8]
    me.zoom_cell_sizes = [32,12]
    me.nframes = 16 #number of frames per world cycle (impact the need in memory!)
    me.fps = 60 #frame per second
    me.menu_width = 200 #width of the right menu in pixels
    me.max_wanted_minimap_size = 64 #size of the MINIMAP in pixels
    me.world_size = (128,128) #in number of cells. Put a power of 2 for tilable maps
    me.chunk = (1310,14) #to give when saving. Neighboring chunk give tilable maps.
    me.persistance = 2.
    me.n_octaves = "max"
    me.refresh_derived_parameters()

def build_hmap(me):
    """Build the pure height map"""
    hmap = me.build_hmap()
    ##hmap[2][1] = 0.7 #this is how you manually change the height of a given cell
    #Here we build the miniature map image
    img_hmap = ng.build_surface(hmap)
    new_img_hmap = pygame.Surface(me.world_size)
    new_img_hmap.blit(img_hmap, (0,0))
    img_hmap = new_img_hmap
    me.build_camera(img_hmap)
    return hmap

def build_materials(me, fast=False, use_beach_tiler=True, load_tilers=False):
    """
    <fast> : quality a bit lower if true, loading time a bit faster.
    <use_beach_tiler>: quality much better if true, loading buch slower.
    Requires Numpy !
    <load_tilers> : use precomputed textures from disk. Very slow but needed if
    you don't have Numpy but still want beach_tiler.
    """
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
    if load_tilers:
        load_tilers = "./rendering/tiles/precomputed/"
    me.build_materials(cell_radius_divider, fast=fast,
                        use_beach_tiler=use_beach_tiler,
                        load_tilers=load_tilers)
##                        load_tilers="./rendering/tiles/precomputed/")
    ##me.save_tilers("./rendering/tiles/precomputed/")
    ##import sys;app.quit();pygame.quit();sys.exit();exit()


def build_lm(me):
    """Build the logical map corresponding to me's properties"""
    lm = me.build_map() #build a logical map with me's properties
    lm.frame_slowness = FRAME_K*me.fps #frame will change every k*FPS [s]
    me.set_map(lm) #we attach the map to the editor


def add_static_objects(me):
    #1) We use another hmap to decide where we want trees (or any other object)
##    S = len(me.lm) lerreur est ici!!!!
    S = len(me.hmap)
    forest_map = ng.generate_terrain(S, n_octaves=None, persistance=1.7, chunk=(12,23))
    ng.normalize(forest_map)
    #we can use as many layers as we want.
    #layer2 is a superimposed map on which we decide to blit some static objects:
    layer2 = me.add_layer()
    #3) We build the objects that we want.
    # its up to you to decide what should be the size of the object (3rd arg)
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
    village1.set_same_type([village2, village3, village4]) #3 images for 1 object
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
    #4) we add the objects via distributors, to add them randomly in a nice way
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

    ############################################################################
    #Here we show how to use the path finder for a given unit of the game
    #Actually, we use it here in order to build cobblestone roads on the map
    costs_materials = {name:1. for name in me.materials}
    costs_materials["Snow"] = 10. #unit is 10 times slower in snow
    costs_materials["Thin snow"] = 2. #twice slower on thin snow...
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
    number_of_roads = 5
    for i in range(number_of_roads): #now we add 5 roads
        objs.add_random_road(me.lm, layer2, cobbles, [wood], costs_materials,
                            costs_objects, possible_materials, possible_objects)
    #now we build a path for rivers, just like we did with roads.
    costs_materials = {name:1. for name in me.materials}
    ##costs_materials["Snow"] = 10. #unit is 10 times slower in snow
    ##costs_materials["Thin snow"] = 2.
    ##costs_materials["Sand"] = 2.
    ##costs_objects = {bush.object_type: 2.}
    #Materials allowed (here we allow water because we add bridges)
    possible_materials=list(me.materials)
    #Objects allowed
    possible_objects=[]
    river_img = me.get_material_image("Shallow water")
    for i in range(5):
        objs.add_random_river(me, me.lm, river_img, costs_materials, costs_objects,
                                possible_materials, possible_objects)


def add_dynamic_objects(me): #here we add two units for instance
    char1 = MapObject(me, "./mapobjects/images/char1.png", "My Unit", 1.)
    obj = me.add_unit(coord=(15,15), obj=char1, quantity=12)
    obj.name = "My first unit"
    obj = me.add_unit((13,13), char1, 1)
    obj.name = "My second unit"
