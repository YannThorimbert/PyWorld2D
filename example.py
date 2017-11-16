import random, math
import pygame
from pygame.math import Vector2 as V2
import thorpy
from rendering.mapgrid import LogicalMap, WhiteLogicalMap
import gui.parameters as guip
import gui.elements as gui
from rendering.camera import Camera
import mapobjects.objects as objs
from mapobjects.objects import MapObject
import saveload.io as io
from ia.path import BranchAndBoundForMap
from editor.mapeditor import MapEditor
import mapdescription as description


##thorpy.application.SHOW_FPS = True

#toute la partie du building qui est dans example.py (ici) devrait migrer ailleurs dans un fichier world_building!
#ou alors faire le laad en plusieurs partie separees par bcp de lignes
#==> ou alors vraiment faire un fichier de description du monde, ce serait + propre.

#finalement: editeur, load/save/quit
#nb: l'editeur permet de faire terrain (hmap), materials, objects (dyn/statics)

#alert pour click droit sur units quand click gauche sur units, et pour click gauche sur terrain quand click droit sur terrain

#meilleur wood : taper wood texture pixel art sur google. Wooden planks?

#ne pas oublier d'ajouter thorpy

#quand meme tester sans numpy, parce que bcp de modules l'importent (surfarray)
#tester python2


#*********************************v2:
#herbe animee
#ombres des objets en mode pil
#ridged noise
#effets: fumee villages, ronds dans l'eau, herbe dans pieds, traces dans neige et sable, precipitations
#
#couples additionnels (ex: shallow_water with all the others...) ajoute au moment de la creation de riviere ?
#comment gerer brulage d'arbres ? Si ca doit changer l'architecture, y penser maintenant...
### ==> reconstruire localement le layer concerne
#quand res + grande, nb de couples peut augmenter! ==> automatiser sur la base des materiaux existants
#info sur material/unit quand on click dessus dans cell/unit_info.em

W,H = 800, 600 #screen size you want
app = thorpy.Application((W,H))
me = MapEditor() #me stands for "Map Editor" everywhere in PyWorld2D package.

TO_FILE = True
FROM_FILE = True
if FROM_FILE:
    savefile = open("coucou.dat", "rb")
    io.from_file_base(savefile, me)
else:
    ##me.zoom_cell_sizes = [32, 20, 16, 12, 8] #side in pixels of the map's square cells
    ##me.zoom_cell_sizes = [64, 32, 12, 8]
    me.zoom_cell_sizes = [32,12]
    me.nframes = 16 #number of frames per world cycle (impact the need in memory!)
    me.fps = 60 #frame per second
    me.menu_width = 200 #width of the right menu in pixels
    me.max_wanted_minimap_size = 64 #in pixels
    me.world_size = (64,64) #in number of cells. Put a power of 2 for tilable maps
    me.chunk = (1310,14) #to give when saving. Neighboring chunk give tilable maps.
    me.persistance = 2.
    me.n_octaves = "max"
    me.refresh_derived_parameters()


################################################################################
print("Building hmap")
hmap = description.build_hmap(me)

################################################################################
print("Building tilers")
description.build_materials(me)

print("Building map surfaces")
lm = me.build_map(hmap, me.world_size)
lm.frame_slowness = 0.1*me.fps #frame will change every k*FPS [s]
lm.cells[3][3].name = "Roflburg" #this is how we set the name of a cell
me.set_map(lm) #we attach the map to the editor

################################################################################
print("Adding static objects")

###1) We use another hmap to decide where we want trees
##forest_map = ng.generate_terrain(S, n_octaves=None, persistance=1.7, chunk=(12,23))
##ng.normalize(forest_map)
##
###2) We build a static object representing a Fir
###we can use as many layers as we want.
###layer2 is a superimposed map on which we decide to blit some static objects:
##layer2 = me.add_layer()
##
###3) We build the objects that we want.
### its up to you to decide what should be the size of the object...
### the size is set through the imgs_dict argument of get_distributor
##fir1 = MapObject(me,"./mapobjects/images/yar_fir1.png","forest",1.5)
##fir2 = MapObject(me,"./mapobjects/images/yar_fir2.png","forest",1.5)
##fir3 = MapObject(me,"./mapobjects/images/firsnow2.png","forest",1.5)
##fir1.set_same_type([fir2, fir3])
##tree = MapObject(me,"./mapobjects/images/tree.png","forest",1.5)
##palm = MapObject(me,"./mapobjects/images/skeddles.png","forest",1.7)
##palm.max_relpos[0] = 0.1 #restrict because they are near to water
##palm.min_relpos[0] = -0.1
##bush = MapObject(me,"./mapobjects/images/yar_bush.png","bush",1.)
##village1 = MapObject(me,"./mapobjects/images/pepperRacoon.png","village",1.3)
##village2 = MapObject(me,"./mapobjects/images/rgbfumes1.png","village",2.2)
##village3 = MapObject(me,"./mapobjects/images/rgbfumes2.png","village",2.6)
##village4 = MapObject(me,"./mapobjects/images/rgbfumes3.png","village",2.6)
####village5 = MapObject(me,"./mapobjects/images/rgbfumes4.png","village",2.2)
##village1.set_same_type([village2, village3, village4])
##
##cobble = MapObject(me,"./mapobjects/images/cobblestone2.png","cobblestone",1.)
##wood = MapObject(me,"./mapobjects/images/wood1.png","wooden bridge",1.)
##
##magic = MapObject(me,
##                 [  "./mapobjects/images/wood1.png",
##                    "./mapobjects/images/yar_bush.png"],
##                 "magic",1.)
##
##gru = objs.put_static_obj(magic, me.lm, (12,12), layer2)
##gru.frame_slowness = 12
##
##for v in[village1,village2,village3,village4]:
##    v.max_relpos = [0., 0.]
##    v.min_relpos = [0., 0.]


###4) we add the objects via distributors
##distributor = objs.get_distributor(me, [fir1, fir2, tree], forest_map, ["Grass","Rock"])
##distributor.distribute_objects(layer2)
##
##distributor = objs.get_distributor(me, [tree], forest_map, ["Grass"])
##distributor.max_density = 1
##distributor.homogeneity = 0.1
##distributor.zones_spread = [(0.5,0.2)]
##distributor.distribute_objects(layer2)
##
##distributor = objs.get_distributor(me, [fir3, fir3.flip()],
##                                forest_map, ["Thin snow","Snow"])
##distributor.homogeneity = 0.5
##distributor.distribute_objects(layer2)
##
##
##distributor = objs.get_distributor(me, [palm, palm.flip()], forest_map, ["Sand"])
##distributor.max_density = 1
##distributor.homogeneity = 0.5
##distributor.zones_spread = [(0., 0.05), (0.3,0.05), (0.6,0.05)]
##distributor.distribute_objects(layer2)
##
##distributor = objs.get_distributor(me, [bush], forest_map, ["Grass"])
##distributor.max_density = 2
##distributor.homogeneity = 0.2
##distributor.zones_spread = [(0., 0.05), (0.3,0.05), (0.6,0.05)]
##distributor.distribute_objects(layer2)
##
##distributor = objs.get_distributor(me,
##                        [village1, village1.flip(), village2, village2.flip(),
##                         village3, village3.flip(), village4, village4.flip()],
##                        forest_map, ["Grass"], limit_relpos_y=False)
##distributor.max_density = 1
##distributor.homogeneity = 0.05
##distributor.zones_spread = [(0.1, 0.05), (0.2,0.05), (0.4,0.05)]
##distributor.distribute_objects(layer2, exclusive=True)
##
##
##cobbles = [cobble, cobble.flip(True,False), cobble.flip(False,True), cobble.flip(True,True)]
##
##################################################################################
###Here we show how to use the path finder for a given unit of the game
##
##costs_materials = {name:1. for name in me.materials}
##costs_materials["Snow"] = 10. #unit is 10 times slower in snow
##costs_materials["Thin snow"] = 2.
##costs_materials["Sand"] = 2.
##for name in me.materials:
##    if "water" in name.lower():
##        costs_materials[name] = 1.1
##costs_objects = {bush.object_type: 2., #unit is 2 times slower in bushes
##                 cobble.object_type: 0.9}
###Materials allowed (here we allow water because we add bridges)
##possible_materials=list(me.materials)
###Objects allowed
##possible_objects=[cobble.object_type, bush.object_type, village1.object_type]
##
##for i in range(5):
##    objs.add_random_road(lm, layer2, cobbles, [wood], costs_materials,
##                     costs_objects, possible_materials, possible_objects)
##
##
##costs_materials = {name:1. for name in me.materials}
####costs_materials["Snow"] = 10. #unit is 10 times slower in snow
####costs_materials["Thin snow"] = 2.
####costs_materials["Sand"] = 2.
####costs_objects = {bush.object_type: 2.}
###Materials allowed (here we allow water because we add bridges)
##possible_materials=list(me.materials)
###Objects allowed
##possible_objects=[]
##
##for i in range(5):
##    objs.add_random_river(me, lm, river_img, costs_materials, costs_objects,
##                            possible_materials, possible_objects)
##
### sp = BranchAndBoundForMap(lm, lm.cells[15][15], lm.cells[8][81],
###                         costs_materials, costs_objects,
###                         possible_materials, possible_objects)
### path = sp.solve()
### draw_path(path, objects=cobbles, layer=lm)



#Now that we finished to add static objects, we generate the surface
print("Building surfaces") #this is also a long process
me.build_surfaces()

################################################################################
#Here we add a dynamic object
if FROM_FILE:
    io.from_file_cells(savefile, me)
    io.from_file_units(savefile, me)
else: #to remove
    char1 = MapObject(me, "./mapobjects/images/char1.png", "My Unit", 1.)
    obj = me.add_unit(coord=(15,15), obj=char1, quantity=12)
    obj = me.add_unit((10,0), char1, 1)
    me.lm.cells[14][15].set_name("frujt")
    me.lm.cells[15][14].set_name("pat")




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

if FROM_FILE:
    savefile.close()

def at_exit():
    io.to_file(me, "coucou.dat")
if not TO_FILE:
    at_exit = None
me.set_zoom(level=0)
m = thorpy.Menu(me.e_box,fps=me.fps)
m.play(at_exit=at_exit)

app.quit()

#pour FS: ajouter un info box quand on click sur material name, quand on click sur une cellule

#pour fs: chateaux, murailles, units: (herite de objet dynamique)

#pour fs : vu que statis prennet de la place, on considere qu'on est dans un village quand on est pres de lui ?
# ou sinon relpos tres petit...