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
FROM_FILE = False
if FROM_FILE:
    savefile = open("coucou.dat", "rb")
    io.from_file_base(savefile, me)
else:
    description.configure_map_editor(me)

################################################################################
print("Building hmap")
description.build_hmap(me)

################################################################################
print("Building tilers")
description.build_materials(me)

print("Building map surfaces")
lm = me.build_map()
lm.frame_slowness = 0.1*me.fps #frame will change every k*FPS [s]
me.set_map(lm) #we attach the map to the editor

################################################################################
print("Adding static objects")
##description.add_static_objects(me)

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
    obj = me.add_unit((13,13), char1, 1)
    me.lm.cells[14][15].set_name("frujt") #this is how we set the name of a cell
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