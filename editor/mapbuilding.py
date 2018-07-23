import pygame, thorpy
import thornoise.purepython.noisegen as ng
import rendering.tilers.tilemanager as tm
from mapobjects.objects import MapObject
import mapobjects.objects as objs
from editor.mapeditor import MapEditor


class MapInitializer:

    def __init__(self, name):
        self.name = name #name of the map
        ############ terrain generation:
        self.world_size = (128,128) #in number of cells. Put a power of 2 for tilable maps
        self.chunk = (1310,14) #Used for random generation. To give when saving. Neighboring chunk give tilable maps.
        self.persistance = 2. #parameter of the random terrain generation.
        self.n_octaves = "max" #parameter of the random terrain generation.
        ############ graphical options:
        self.zoom_cell_sizes = [32, 16, 8] #size of one cell for the different zoom levels.
        self.nframes = 16 #number of frames per world cycle (impacts memory requirement!)
        self.fps = 60 #frame per second
        self.menu_width = 200 #width of the right menu in pixels
        self.max_wanted_minimap_size = 64 #size of the MINIMAP in pixels
        ############ material options:
        #cell_radius = cell_size//radius_divider
        # change how "round" look cell transitions
        self.cell_radius_divider = 8
        #path or color of the image of the different materials
        self.water = "./rendering/tiles/water1.png"
        self.sand = "./rendering/tiles/sand1.jpg"
        self.grass = "./rendering/tiles/grass1.png"
        self.grass2 = "./rendering/tiles/grass8.png"
        self.rock = "./rendering/tiles/rock1.png"
        self.black = (0,0,0)
        self.white = (255,255,255)
        #mixed images - we superimpose different image to make a new one
        #the value indicated correspond
        self.deepwater= 127 #mix water with black : 127 is the alpha of black
        self.mediumwater= 50 #mix water with black : 50 is the alpha of black
        self.shore = 127 #mix sand with water : 127 is the alpha of water
        self.thinsnow = 200 #mix rock with white : 200 is the alpha of white
        #water movement is obtained by using shifts.
        #x-shift is dx_divider and y-shift is dy_divider. Unit is pixel.
        self.dx_divider = 10
        self.dy_divider = 8
        #here we specify at which altitude is each biome
        self.hdeepwater = 0.4 #deep water only below 0.4
        self.hwater = 0.55 #normal water between 0.4 and 0.55
        self.hshore = 0.6 #shore water between 0.55 and 0.6
        self.hsand = 0.62 #and so on...
        self.hgrass = 0.8
        self.hrock = 0.83
        self.hthinsnow = 0.9
        self.hsnow = float("inf")
        #precomputed tiles are used only if load_tilers=True is passed to build_materials()
        self.precomputed_tiles = "./rendering/tiles/precomputed/"
        #NB : if you want to add your own materials, then you must write your
        #   own version of build_materials function below, and modify the above
        #   parameters accordingly in order to include the additional material
        #   or remove the ones you don't want.
        ############ static objects options:
        self.static_objects_n_octaves = None
        self.static_objects_persistance = 1.7
        self.static_objects_chunk = (12,24)
        #normal forest:
        self.forest_text = "forest"
        self.tree = "./mapobjects/images/tree.png"
        self.tree_size = 1.5
        self.fir1 = "./mapobjects/images/yar_fir1.png"
        self.fir1_size = 1.5
        self.fir2 = "./mapobjects/images/yar_fir2.png"
        self.fir2_size = 1.5
        self.forest_max_density = 1 #integer : number of trees per world cell
        self.forest_homogeneity = 0.1
        self.forest_zones_spread = [(0.5,0.2)]
        #snow forest:
        self.firsnow = "./mapobjects/images/firsnow2.png"
        self.firsnow_size = 1.5
        self.forest_snow_text = "forest"
        self.forest_snow_max_density = 1
        self.forest_snow_homogeneity = 0.5
        self.forest_snow_zones_spread = [(0.5,0.2)]
        #palm forest:
        self.palm = "./mapobjects/images/skeddles.png"
        self.palm_size = 1.7
        self.palm_text = "forest"
        self.palm_max_density = 1
        self.palm_homogeneity = 0.5
        self.palm_zones_spread = [(0., 0.05), (0.3,0.05), (0.6,0.05)]
        #other things:
        self.bush = "./mapobjects/images/yar_bush.png"
        self.bush_size = 1.
        self.village1 = "./mapobjects/images/pepperRacoon.png"
        self.village1_size = 1.3
        self.village2 = "./mapobjects/images/rgbfumes1.png"
        self.village2_size = 2.2
        self.village3 = "./mapobjects/images/rgbfumes2.png"
        self.village3_size = 2.6
        self.village4 = "./mapobjects/images/rgbfumes3.png"
        self.village4_size = 2.6
        self.cobble = "./mapobjects/images/cobblestone2.png"
        self.cobble_size = 1.
        self.wood = "./mapobjects/images/wood1.png"
        self.wood_size = 1.
        #if you want to add objects by yourself, look at add_static_objects(self)
        self.min_road_length = 10
        self.max_road_length = 40
        self.max_number_of_roads = 5
        self.min_river_length = 10
        self.max_river_length = 80
        self.max_number_of_rivers = 5
        ############ End of user-defined parameters
        self.forest_map = None
        self.layer2 = None


    def get_image(self, me, name):
        value = getattr(self, name)
        if isinstance(value, str):
            return me.load_image(value)
        elif isinstance(value, tuple):
            return me.get_color_image(value)


    def configure_map_editor(self):
        """Set the properties of the map editor"""
        me = MapEditor(self.name)
        me.zoom_cell_sizes = self.zoom_cell_sizes
        me.nframes = self.nframes
        me.fps = self.fps
        me.menu_width = self.menu_width
        me.max_wanted_minimap_size = self.max_wanted_minimap_size
        me.world_size = self.world_size
        me.chunk = self.chunk
        me.persistance = self.persistance
        me.n_octaves = self.n_octaves
        me.refresh_derived_parameters()
        return me

    def build_materials(self, me, fast, use_beach_tiler, load_tilers):
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
        water_img = self.get_image(me, "water")
        sand_img = self.get_image(me, "sand")
        grass_img = self.get_image(me, "grass")
        grass_img2 = self.get_image(me, "grass2")
        rock_img = self.get_image(me, "rock")
        black_img = self.get_image(me, "black")
        white_img = self.get_image(me, "white")
        #mixed images - we superimpose different image to make a new one
        deepwater_img = tm.get_mixed_tiles(water_img, black_img, self.deepwater)
        mediumwater_img = tm.get_mixed_tiles(water_img, black_img, self.mediumwater)
        shore_img = tm.get_mixed_tiles(sand_img, water_img, self.shore) # alpha of water is 127
        thinsnow_img = tm.get_mixed_tiles(rock_img, white_img, self.thinsnow)
        ##river_img = tm.get_mixed_tiles(rock_img, water_img, 200)
        river_img = shore_img
        #water movement is obtained by using a delta-x (dx_divider) and delta-y shifts,
        # here dx_divider = 10 and dy_divider = 8
        #hmax=0.1 means one will find deepwater only below height = 0.1
        ##deepwater = me.add_material("Very deep water", 0.1, deepwater_img, self.dx_divider, self.dy_divider)
        me.add_material("Deep water", self.hdeepwater, mediumwater_img, self.dx_divider, self.dy_divider)
        me.add_material("Water", self.hwater, water_img, self.dx_divider, self.dy_divider)
        me.add_material("Shallow water", self.hshore, shore_img, self.dx_divider, self.dy_divider)
        me.add_material("Sand", self.hsand, sand_img)
        me.add_material("Grass", self.hgrass, grass_img)
        ##me.add_material("Grass", 0.8, grass_img2, id_="Grass2")
        me.add_material("Rock", self.hrock, rock_img)
        me.add_material("Thin snow", self.hthinsnow, thinsnow_img)
        me.add_material("Snow", self.hsnow, white_img)
        #Outside material is mandatory. The only thing you can change is black_img
        outside = me.add_material("outside", -1, black_img)
        #this is the heavier computing part, especially if the maximum zoom is large:
        print("Building material couples")
        if load_tilers:
            load_tilers = self.precomputed_tiles
        me.build_materials(cell_radius_divider, fast=fast,
                            use_beach_tiler=use_beach_tiler,
                            load_tilers=load_tilers)
    ##                        load_tilers="./rendering/tiles/precomputed/")
        ##me.save_tilers("./rendering/tiles/precomputed/")
        ##import sys;app.quit();pygame.quit();sys.exit();exit()


    def add_static_objects(self, me):
        #1) We use another hmap to decide where we want trees (or any other object)
    ##    S = len(me.lm) lerreur est ici!!!!
        S = len(me.hmap)
        self.forest_map = ng.generate_terrain(S, n_octaves=self.static_objects_n_octaves,
                                            persistance=self.static_objects_persistance,
                                            chunk=self.static_objects_chunk)
        ng.normalize(self.forest_map)
        #we can use as many layers as we want.
        #self.layer2 is a superimposed map on which we decide to blit some static objects:
        self.layer2 = me.add_layer()
        #3) We build the objects that we want.
        # its up to you to decide what should be the size of the object (3rd arg)
        tree = MapObject(me,self.tree,self.forest_text,self.tree_size)
        fir1 = MapObject(me,self.fir1,self.forest_text,self.fir1_size)
        fir2 = MapObject(me,self.fir2,self.forest_text,self.fir2_size)
        firsnow = MapObject(me,self.firsnow,self.forest_snow_text,self.firsnow_size)
        fir1.set_same_type([fir2, firsnow])
        palm = MapObject(me,self.palm,self.palm_text,self.palm_size)
        palm.max_relpos[0] = 0.1 #restrict because they are near to water
        palm.min_relpos[0] = -0.1
        bush = MapObject(me,self.bush,"bush",self.bush_size)
        village1 = MapObject(me,self.village1, "village",self.village1_size)
        village2 = MapObject(me,self.village2,"village",self.village2_size)
        village3 = MapObject(me,self.village3,"village",self.village3_size)
        village4 = MapObject(me,self.village4,"village",self.village4_size)
        ##village5 = MapObject(me,"./mapobjects/images/rgbfumes4.png","village",2.2)
        village1.set_same_type([village2, village3, village4]) #3 images for 1 object
        #
        cobble = MapObject(me,self.cobble,"cobblestone",self.cobble_size)
        wood = MapObject(me,self.wood,"wooden bridge",self.wood_size)
        #
##        anim_tree = MapObject(me, [self.fir1]*3+[self.fir2]*3, "My animated tree",1.)
##        anim_tree = objs.put_static_obj(anim_tree, me.lm, (12,12), self.layer2)
        #
        for v in[village1,village2,village3,village4]:
            v.max_relpos = [0., 0.]
            v.min_relpos = [0., 0.]
        #4) we add the objects via distributors, to add them randomly in a nice way
        #normal forest
        distributor = objs.get_distributor(me, [fir1, fir2, tree],
                                            self.forest_map, ["Grass","Rock"])
        distributor.max_density = self.forest_max_density
        distributor.homogeneity = self.forest_homogeneity
        distributor.zones_spread = self.forest_zones_spread
        distributor.distribute_objects(self.layer2)
        #more trees in plains
        distributor = objs.get_distributor(me, [tree], self.forest_map, ["Grass"])
        distributor.max_density = self.forest_max_density
        distributor.homogeneity = self.forest_homogeneity
        distributor.zones_spread = self.forest_zones_spread
        distributor.distribute_objects(self.layer2)
        #snow forest
        distributor = objs.get_distributor(me, [firsnow, firsnow.flip()],
                                        self.forest_map, ["Thin snow","Snow"])
        distributor.max_density = self.forest_snow_max_density
        distributor.homogeneity = self.forest_snow_homogeneity
        distributor.zones_spread = self.forest_snow_zones_spread
        distributor.distribute_objects(self.layer2)
        #palm forest
        distributor = objs.get_distributor(me, [palm, palm.flip()], self.forest_map, ["Sand"])
        distributor.max_density = self.palm_max_density
        distributor.homogeneity = self.palm_homogeneity
        distributor.zones_spread = self.palm_zones_spread
        distributor.distribute_objects(self.layer2)
        #bushes
        distributor = objs.get_distributor(me, [bush], self.forest_map, ["Grass"])
        distributor.max_density = 2
        distributor.homogeneity = 0.2
        distributor.zones_spread = [(0., 0.05), (0.3,0.05), (0.6,0.05)]
        distributor.distribute_objects(self.layer2)
        #villages
        distributor = objs.get_distributor(me,
                                [village1, village1.flip(), village2, village2.flip(),
                                 village3, village3.flip(), village4, village4.flip()],
                                self.forest_map, ["Grass"], limit_relpos_y=False)
        distributor.max_density = 1
        distributor.homogeneity = 0.05
        distributor.zones_spread = [(0.1, 0.05), (0.2,0.05), (0.4,0.05)]
        distributor.distribute_objects(self.layer2, exclusive=True)

        cobbles = [cobble, cobble.flip(True,False),
                    cobble.flip(False,True), cobble.flip(True,True)]
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
        for i in range(self.max_number_of_roads): #now we add 5 roads
            objs.add_random_road(me.lm, self.layer2, cobbles, [wood], costs_materials,
                                costs_objects, possible_materials, possible_objects,
                                min_length=self.min_road_length,
                                max_length=self.max_road_length)
        #now we build a path for rivers, just like we did with roads.
        costs_materials = {name:1. for name in me.materials}
        #Materials allowed (here we allow water because we add bridges)
        possible_materials=list(me.materials)
        #Objects allowed
        possible_objects=[]
        river_img = me.get_material_image("Shallow water")
        for i in range(self.max_number_of_rivers): #try to add 5 rivers
            objs.add_random_river(me, me.lm, river_img, costs_materials, costs_objects,
                                    possible_materials, possible_objects,
                                    min_length=self.min_river_length,
                                    max_length=self.max_river_length)


    def build_map(self, me, fast=False, use_beach_tiler=True, load_tilers=False,
                    graphical_load=True):
        """
        <fast> : quality a bit lower if true, loading time a bit faster.
        <use_beach_tiler>: quality much better if true, loading buch slower.
        Requires Numpy !
        <load_tilers> : use precomputed textures from disk. Very slow but needed if
        you don't have Numpy but still want beach_tiler.
        """
        if graphical_load: #just ignore this- nothing to do with map configuration
            screen = thorpy.get_screen()
            screen.fill((255,255,255))
            loading_bar = thorpy.LifeBar.make(" ",
                size=(thorpy.get_screen().get_width()//2,30))
            loading_bar.center(element="screen")
            update_loading_bar(loading_bar, "Building height map...", 0., graphical_load)
        build_hmap(me)
        if graphical_load:
            img = thorpy.get_resized_image(me.original_img_hmap, screen.get_size(), max)
            screen.blit(img, (0,0))
            update_loading_bar(loading_bar,"Building tilers...",0.1,graphical_load)
        self.build_materials(me, fast, use_beach_tiler, load_tilers)
        update_loading_bar(loading_bar,"Building map surfaces...",0.2,graphical_load)
        build_lm(me)
        update_loading_bar(loading_bar,"Adding static objects...",0.3,graphical_load)
        self.add_static_objects(me)
        #Now that we finished to add objects, we generate the pygame surface
        update_loading_bar(loading_bar, "Building surfaces", 0.9, graphical_load)
        me.build_surfaces()

def update_loading_bar(loading_bar, text, progress, on):
    print(text)
    if on:
        loading_bar.set_text(text)
        loading_bar.set_life(progress)
        loading_bar.blit()
        pygame.display.flip()


def build_lm(me):
    """Build the logical map corresponding to me's properties"""
    lm = me.build_map() #build a logical map with me's properties
    lm.frame_slowness = 0.1*me.fps #frame will change every k*FPS [s]
    me.set_map(lm) #we attach the map to the editor

def build_hmap(me):
    """Build a pure height map"""
    hmap = me.build_hmap()
    ##hmap[2][1] = 0.7 #this is how you manually change the height of a given cell
    #Here we build the miniature map image
    img_hmap = ng.build_surface(hmap)
    new_img_hmap = pygame.Surface(me.world_size)
    new_img_hmap.blit(img_hmap, (0,0))
    img_hmap = new_img_hmap
    me.build_camera(img_hmap)
    return hmap


def add_dynamic_objects(me): #here we add two units for instance
    char1 = MapObject(me, "./mapobjects/images/char1.png", "My Unit", 1.)
    obj = me.add_unit(coord=(15,15), obj=char1, quantity=12)
    obj.name = "My first unit"
    obj = me.add_unit((13,13), char1, 1)
    obj.name = "My second unit"
