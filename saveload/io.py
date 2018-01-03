import pickle
import thorpy
from mapobjects.objects import MapObject

def ask_save(editor):
    choice = thorpy.launch_binary_choice("Do you want to save this map ?")
    if choice:
        to_file(editor, editor.get_fn())
    thorpy.functions.quit_menu_func()

def ask_load():
    pass
################################################################################

def obj_to_file(obj, f):
    for attr in obj.saved_attrs:
        value = getattr(obj, attr)
        pickle.dump(value, f)

def file_to_obj(f, obj):
    for attr in obj.saved_attrs:
        value = pickle.load(f)
        setattr(obj, attr, value)

def to_file(me, fn):
    print("Saving map to",fn)
    with open(fn, "wb") as f:
        obj_to_file(me, f) #me
        #
        print("dumping", len(me.modified_cells), "cells")
        pickle.dump(len(me.modified_cells), f) #len(modified cells)
        for x,y in me.modified_cells:
            cell = me.lm.cells[x][y]
            pickle.dump((x,y),f)
            pickle.dump(cell.name,f) #cell name
        #
        print("dumping", len(me.dynamic_objects), "dynamic objects")
        pickle.dump(len(me.dynamic_objects), f) #len(dynamic_objects)
        for obj in me.dynamic_objects:
            pickle.dump(obj.get_cell_coord(), f) #coord
            obj_to_file(obj, f) #dyn obj



def from_file_base(f, me):
    print("Loading map")
    file_to_obj(f, me) #me
    me.refresh_derived_parameters()

def from_file_cells(f, me):
    """Load cells and their logical content (names, properties, etc.)"""
    print("Loading cells")
    n = pickle.load(f) #len(modified cells)
    for i in range(n):
        x,y = pickle.load(f) #coord
        name = pickle.load(f) #name
        #
        me.lm.cells[x][y].set_name(name)

def from_file_units(f, me):
    """Load units and their logical content (names, properties, etc.)"""
    print("Loading units")
    n = pickle.load(f) #len(dynamic_objects)
    for i in range(n):
        coord = pickle.load(f) #coord
        a = {}
        for attr_name in MapObject.saved_attrs:
            a[attr_name] = pickle.load(f)
        #
        print("*** Loadig unit", a["name"])
        print(a)
        obj = MapObject(me, fns=a["fns"], name=a["name"], factor=a["factor"],
                        relpos=a["relpos"], build=a["build"], new_type=a["new_type"])
        obj_added = me.add_unit(coord, obj, a["quantity"])


#sauver:
##attributs non-proceduraux des cells (e.g noms non-proceduraux)
#==> me maintient une liste au format [(coord, nom), ...] des cellules renommees
#idem avec tous les terrains dont le hmap ou material a ete modifie
