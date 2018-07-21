import random, math
import pygame
from pygame.math import Vector2 as V2
import thorpy
from rendering.mapgrid import LogicalMap, WhiteLogicalMap
import gui.parameters as guip
import gui.elements as gui
from rendering.camera import Camera
from mapobjects.objects import MapObject
import saveload.io as io
from ia.path import BranchAndBoundForMap
from editor.mapeditor import MapEditor
import mapdescription as description


##thorpy.application.SHOW_FPS = True

##mieux illustrer les exemples dans add_static_objects : SEPARER paths de distributors
##Below is shown how to get a path, if you need it for an IA for instance:
    # sp = BranchAndBoundForMap(lm, lm.cells[15][15], lm.cells[8][81],
    #                         costs_materials, costs_objects,
    #                         possible_materials, possible_objects)
    # path = sp.solve()
    # draw_path(path, objects=cobbles, layer=lm)

##essayer en mode load

#finalement: editeur, load/save/quit marche avec tout (dyn objs, stat objs... ? beaucoup tester)
##NB static objects : tout est regenerable a partir de seed, donc deja fait!
#nb: l'editeur permet de faire terrain (hmap), materials, objects (dyn/statics)

#proposer un ciel + nuages (cf perigeo) au lieu de mer ; le mettre par defaut dans le noir ?

#quand curseur passe au dessus d'un village, ajouter (village) a cote du material dans la description de fenetre de droite

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

W,H = 800, 600 #screen size
app = thorpy.Application((W,H))
me = MapEditor("map123") #me stands for "Map Editor" everywhere in PyWorld2D package.

TO_FILE = False #save when leaving
FROM_FILE = False #load at building
if FROM_FILE:
    savefile = open(me.get_fn(), "rb")
    io.from_file_base(savefile, me)
else:
    description.configure_map_editor(me)

#in mapdescription.py you can modify all the properties of the map !
#just check the different functions and play with the variables

print("Building hmap")
description.build_hmap(me)
print("Building tilers")
description.build_materials(me, fast=False, use_beach_tiler=True, load_tilers=False)
print("Building map surfaces")
description.build_lm(me)
print("Adding static objects") #seeded ??????????????????????????????????????????????
description.add_static_objects(me)
print("Adding dynamic objects")
description.add_dynamic_objects(me)
#Now that we finished to add static objects, we generate the surface
print("Building surfaces") #this is also a long process
me.build_surfaces()


#ou sont definis les deux units ?
################################################################################
if FROM_FILE: #load things that cannot be regenerated from seed
    io.from_file_cells(savefile, me)
    io.from_file_units(savefile, me)

me.lm.cells[14][15].set_name("My left cell") #this is how we set the name of a cell
me.lm.cells[15][14].set_name("My top cell")

################################################################################
print("Building GUI")
me.build_gui_elements()


def func_reac_time(): #here put wathever you want, in addition to me's reac
    me.func_reac_time()
    pygame.display.flip()
thorpy.add_time_reaction(me.e_box, func_reac_time)


#here you can add/remove buttons to the menu ###################################
def quit_func():
    io.ask_save(me)
    thorpy.functions.quit_func()
e_quit = thorpy.make_button("Quit game", quit_func)
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

if not TO_FILE:
    at_exit = None
me.set_zoom(level=0)
m = thorpy.Menu(me.e_box,fps=me.fps)
m.play()

app.quit()

#pour FS: ajouter un info box quand on click sur material name, quand on click sur une cellule

#pour fs: chateaux, murailles, units: (herite de objet dynamique)

#pour fs : vu que statics prennet de la place, on considere qu'on est dans un village quand on est pres de lui ?
# ou sinon relpos tres petit...