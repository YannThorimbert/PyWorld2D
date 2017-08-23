
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

def to_file(obj, fn):
    f = open(fn, "w")
    for attr in obj.saved_attrs:
        value = getattr(obj, attr)
        type_ = type(value)
        conversion = save.get(type_, str)
        str_value = conversion(value)
        f.write(str_value+"\n")
    f.close()

def from_file(obj, fn):
    f = open(fn, "r")
    lines = f.readlines()
    f.close()
    for i,attr in enumerate(obj.saved_attrs):
        value = getattr(obj, attr)
        str_value = lines[i][:-1] #remove last '\n'
        type_ = type(value)
        conversion = load.get(type_)
        if conversion:
            primitive_type = obj.primitive_types.get(attr, int)
            value = conversion(str_value, primitive_type)
        else:
            value = type_(str_value)
        setattr(obj, attr, value)


#sauver:
##attributs non-proceduraux des cells (e.g noms non-proceduraux)
##chunks et persistance et octaves
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

