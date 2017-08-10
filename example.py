import random, math
import pygame
from pygame.math import Vector2 as V2
import thorpy
import thornoise.purepython.noisegen as ng
import rendering.tilers.tilemanager as tm
from rendering.mapgrid import LogicalMap, WhiteLogicalMap
import gui.parameters as guip
import gui.elements as gui
from rendering.camera import Camera
from mapobjects.objects import MapObject, RandomObjectDistribution, get_forest_distributor
import saveload.io as io

from editor.mapeditor import MapEditor

##thorpy.application.SHOW_FPS = True

#trier les statics pour blit dans le bon ordre ?

#rename unit

#objets de base: feuillu, montagnes, villages, chemin, rivieres.
#pour fs: chateaux, murailles, units: (herite de objet dynamique)

#peut etre que marche pas sans numpy a cause du beach tiler.
#Dans ce cas, favoriser la hmap issue de version numpy
#==> a tester sur une machine vierge

#finalement: editeur, load/save/quit

#alerts pour autres trucs

#v2:
#quand res + grande, nb de couples peut augmenter! ==> automatiser sur la base des materiaux existants

#ridged noise

#effets: vent dans arbres et fumee villages, ronds dans l'eau, herbe dans pieds, traces dans neige et sable, precipitations

#ne pas oublier d'ajouter thorpy
#objects avec des frames


W,H = 800, 600 #screen size you want
app = thorpy.Application((W,H))

#might be chosen by user:

chunk =(1310,14) #to give when saving. Neighboring chunk give tilable maps.
desired_world_size = (100,50) #in number of cells. Put a power of 2 for tilable maps


#cell_radius = cell_size//radius_divider
# change how "round" look cell transitions
cell_radius_divider = 8

me = MapEditor()
me.zoom_cell_sizes = [32, 20, 16, 12, 8] #side in pixels of the map's square cells
##me.zoom_cell_sizes = [25]
me.nframes = 16 #number of frames per world cycle (impact the need in memory!)
me.fps = 60 #frame per second
me.menu_width = 200 #width of the right menu in pixels
me.max_wanted_minimap_size = 128 #in pixels.

me.refresh_derived_parameters()



################################################################################
print("Building hmap")
power = int(math.log2(max(desired_world_size)))
if 2**power < max(desired_world_size):
    power += 1
S = int(2**power)
hmap = ng.generate_terrain(S, chunk=chunk)
ng.normalize(hmap)
##hmap[2][1] = 0.7 #this is how you manually change the height of a cell

#Here we build the miniature map image
img_hmap = ng.build_surface(hmap)
new_img_hmap = pygame.Surface(desired_world_size)
new_img_hmap.blit(img_hmap, (0,0))
img_hmap = new_img_hmap
me.build_camera(img_hmap)

################################################################################
print("Building tilers")

#we load simple images - they can be of any size, they will be resized
water_img = me.load_image("./rendering/tiles/water1.png")
sand_img = me.load_image("./rendering/tiles/sand1.jpg")
grass_img = me.load_image("./rendering/tiles/grass1.png")
rock_img = me.load_image("./rendering/tiles/rock1.png")
black_img = me.get_color_image((0,0,0))
white_img = me.get_color_image((255,255,255))

#mixed images - we superimpose different image to make a new one
deepwater_img = tm.get_mixed_tiles(water_img, black_img, 127)
mediumwater_img = tm.get_mixed_tiles(water_img, black_img, 50)
shore_img = tm.get_mixed_tiles(sand_img, water_img, 127) # alpha of water is 127
thinsnow_img = tm.get_mixed_tiles(rock_img, white_img, 200)

#water movement is obtained by using a delta-x (dx_divider) and delta-y shifts,
# here dx_divider = 10 and dy_divider = 8
#hmax=0.1 means one will find deepwater only below height = 0.1
##deepwater = me.add_material("Very deep water", 0.1, deepwater_img, 10, 8)
mediumwater = me.add_material("Deep water", 0.4, mediumwater_img, 10, 8)
water = me.add_material("Water", 0.55, water_img, 10, 8)
shore = me.add_material("Shallow water", 0.6, shore_img, 10, 8)
sand = me.add_material("Sand", 0.62, sand_img)
badlands = me.add_material("Grass", 0.8, grass_img)
rock = me.add_material("Rock", 0.83, rock_img)
snow1 = me.add_material("Thin snow", 0.9, thinsnow_img)
snow2 = me.add_material("Snow", float("inf"), white_img)
#Outside material is mandatory. The only thing you can change is black_img
outside = me.add_material("outside", -1, black_img)

#this is the heavier computing part, especially if the maximum zoom is large:
print("Building material couples")
me.build_materials(cell_radius_divider)

################################################################################


lm = me.build_map(hmap, desired_world_size)
lm.frame_slowness = 0.1*me.fps #frame will change every k*FPS [s]
lm.cells[3][3].name = "Roflburg" #this is how we set the name of a cell
me.set_map(lm) #we attach the map to the editor

################################################################################
print("Adding static objects")

#1) We use another hmap to decide where we want trees
forest_map = ng.generate_terrain(S, n_octaves=None, persistance=1.7, chunk=(12,23))
ng.normalize(forest_map)

#2) We build a static object representing a Fir
#we can use as many layers as we want.
#layer2 is a superimposed map on which we decide to blit some static objects:
layer2 = me.add_layer()


#3) we add the objects via distributors
#dont forget to resize the object to the size corresponding to largest zoom:
# its up to you to decide what should be the size of the object...
# the size is set through the imgs_dict argument of get_forest_distributor
trees = {"./mapobjects/images/fir0.png":("forest",1.5,False)}
distributor = get_forest_distributor(me, trees, forest_map, ["Grass","Rock"])
distributor.distribute_objects(layer2)

trees = {"./mapobjects/images/firsnow2.png":("forest",1.5,True)}
distributor = get_forest_distributor(me, trees, forest_map, ["Thin snow","Snow"])
distributor.homogeneity = 0.5
distributor.distribute_objects(layer2)

trees = {"./mapobjects/images/oasis0.png":("palm forest",1.3,True)}
distributor = get_forest_distributor(me, trees, forest_map, ["Sand"])
distributor.max_density = 1
distributor.homogeneity = 0.5
distributor.zones_spread = [(0., 0.05), (0.3,0.05), (0.6,0.05)]
distributor.distribute_objects(layer2)


trees = {"./mapobjects/images/yar_bush.png":("bush",1.,False)}
distributor = get_forest_distributor(me, trees, forest_map, ["Grass"])
distributor.max_density = 2
distributor.homogeneity = 0.2
distributor.zones_spread = [(0., 0.05), (0.3,0.05), (0.6,0.05)]
distributor.distribute_objects(layer2)

#Now that we finished to add static objects, we generate the surface
print("Building surfaces") #this is also a long process
layer2.static_objects.sort(key=lambda x:x.ypos())
me.build_surfaces()

################################################################################
#Here we add a dynamic object
char1_img = thorpy.load_image("./mapobjects/images/char1.png", (255,255,255))
char1_img = thorpy.get_resized_image(char1_img, (me.zoom_cell_sizes[0],)*2)
char1 = MapObject(me, char1_img, "My Unit")
char1.build_imgs()
obj = char1.add_unit_on_cell(lm.cells[32][15])
obj.quantity = 12 #logical (not graphical) quantity
me.dynamic_objects.append(obj)


################################################################################
print("Building GUI")
me.build_gui_elements()


def func_reac_time(): #here put wathever you want, in addition to me's reac
    me.func_reac_time()
    pygame.display.flip()
thorpy.add_time_reaction(me.e_box, func_reac_time)


#here you can add/remove buttons to the menu ###################################
e_quit = thorpy.make_button("Quit game", thorpy.functions.quit_func)
e_save = thorpy.make_button("Save", io.ask_save, {"editor":me})
e_load = thorpy.make_button("Load", io.ask_load)

launched_menu = thorpy.make_ok_box([ me.help_box.launcher,
                                            e_save,
                                            e_load,
                                            e_quit])
launched_menu.center()
me.menu_button.user_func = thorpy.launch_blocking
me.menu_button.user_params = {"element":launched_menu}
# ##############################################################################


#me.e_box includes many default reactions. You can remove them as follow:
#remove <g> key:
##me.e_box.remove_reaction("toggle grid")
#remove arrows keys, replacing <direction> by left, right, up or down:
##me.e_box.remove_reaction("k <direction>")
#remove +/- numpad keys for zoom, replacing <sign> by plus or minus:
##me.e_box.remove_reaction("k <sign>")
#remember to modify/deactivate the help text corresponding to the removed reac


me.set_zoom(level=0)
m = thorpy.Menu(me.e_box,fps=me.fps)
m.play()

app.quit()

#pour FS: ajouter un info box quand on click sur material name, quand on click sur une cellule

