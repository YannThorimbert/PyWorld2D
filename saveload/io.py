import pickle
from mapobjects.objects import MapObject

def ask_save(editor):
    pass

def ask_load():
    pass
################################################################################


def load_list(s, primitive_type):
    return [primitive_type(v) for v in s[1:-1].split(",")]

def load_tuple(s, primitive_type):
    return tuple(load_list(s,primitive_type))

def load_bool(s, primitive_type):
    if s[0] == "F":
        return False
    elif s[0] == "T":
        return True
    raise Exception("Could not convert string to boolean:",s)

load = {list:load_list,
        tuple:load_tuple,
        bool:load_bool}

################################################################################
save = {}

##def to_file(obj, fn):
##    f = open(fn, "w")
##    for attr in obj.saved_attrs:
##        value = getattr(obj, attr)
##        type_ = type(value)
##        conversion = save.get(type_, str)
##        str_value = conversion(value)
##        f.write(str_value+"\n")
##    f.close()
##
##def from_file(obj, fn):
##    f = open(fn, "r")
##    lines = f.readlines()
##    f.close()
##    for i,attr in enumerate(obj.saved_attrs):
##        value = getattr(obj, attr)
##        str_value = lines[i][:-1] #remove last '\n'
##        type_ = type(value)
##        conversion = load.get(type_)
##        if conversion:
##            primitive_type = obj.primitive_types.get(attr, int)
##            value = conversion(str_value, primitive_type)
##        else:
##            value = type_(str_value)
##        setattr(obj, attr, value)

##def to_file(obj, f):
####    f = open(fn, "wb")
##    for attr in obj.saved_attrs:
##        attribute = getattr(obj, attr)
##        pickle.dump(attribute, f)
##    f.close()

##def from_file(fn):
##    loaded = []
##    with open(fn, "rb") as f: #this is how we load it
##        while True:
##            try:
##                value = pickle.load(f)
##                loaded.append(value)
##            except:
##                break
##    return loaded

def obj_to_file(obj, f):
    for attr in obj.saved_attrs:
        value = getattr(obj, attr)
        pickle.dump(value, f)

def file_to_obj(f, obj):
    for attr in obj.saved_attrs:
        value = pickle.load(f)
        setattr(me, attr, value)

def to_file(me, fn):
    print("Saving map to",fn)
    with open(fn, "rb") as f:
        obj_to_file(me, f) #me
        pickle.dump(len(me.dynamic_objects), f) #len(dynamic_objects)
        for obj in me.dynamic_objects:
            pickle.dump(obj.get_cell_coord(), f) #coord
            obj_to_file(obj, f) #dyn obj



def from_file(fn, me):
    print("Loading map from",fn)
    with open(fn, "rb") as f: #this is how we load it
        file_to_obj(f, me) #me
        me.refresh_derived_parameters()
        n = pickle.load(f) #len(dynamic_objects)
        for i in range(n):
            coord = pickle.load(f) #coord
            a = {}
            for attr_name in MapObject.saved_attrs:
                a[attr_name] = pickle.load(f)
            #
            obj = MapObject(me, fns=a["fns"], name=a["name"], factor=a["factor"],
                            relpos=a["relpos"], build=a["build"], new_type=a["new_type"])
            obj_added = me.add_unit(coord, obj, a["quantity"])

##def from_file(obj, fn):
##    loaded = {}
##    with open(fn, "rb") as f: #this is how we load it
##        for attr in obj.saved_attrs:
##            value = pickle.load(f)
##            setattr(obj, attr, value)
##            loaded[attr] = value
##    return loaded

def save_all(objs, fn):
    f = open(fn, "wb")
    for obj in objs:
        for attr in obj.saved_attrs:
            attribute = getattr(obj, attr)
            pickle.dump(attribute, f)
    f.close()

def load_all(objs, fn):
    loaded = {}
    f = open(fn, "rb")
    for obj in objs:
        for attr in obj.saved_attrs:
            value = pickle.load(f)
            setattr(obj, attr, value)
            loaded[attr] = value
    f.close()
    return loaded

#sauver:
##attributs non-proceduraux des cells (e.g noms non-proceduraux)
##units

##class Gru:
##
##    def __init__(self):
##        self.a = "grosfu"
##        self.b = (2,3)
##        self.c = [1, 3, 4, 5.6]
##        self.d = (1,2,0.5)
##        self.e = [4,5,7]
##        self.f = True
##        self.g = False
##        self.h = -1.3
##        self.i = 34
##        self.saved_attrs = ["a","b","c","d","e","f","g","h","i"]
##        self.primitive_types = {"c":float,"d":float} #default is int
##
##

