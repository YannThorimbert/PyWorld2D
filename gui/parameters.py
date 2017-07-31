import thorpy

#titles
TFS = thorpy.style.TITLE_FONT_SIZE
TFC = thorpy.style.TITLE_FONT_COLOR

#normal
NFS = thorpy.style.FONT_SIZE
NFC = thorpy.style.FONT_COLOR

#small
SFS = thorpy.style.FONT_SIZE - 2
SFC = thorpy.style.FONT_COLOR


def get_title(text):
    return thorpy.make_text(text, TFS, TFC)

def get_text(text):
    return thorpy.make_text(text, NFS, NFC)

def get_small_text(text):
    return thorpy.make_text(text, SFS, SFC)

def get_button(text, func, params=None):
    b = thorpy.make_button(text, func, params)
    b.set_font_size(NFS)
    b.set_font_color(NFC)
    return b

def get_small_button(text, func, params=None):
    b = thorpy.make_button(text, func, params)
    b.set_font_size(SFS)
    b.set_font_color(SFC)
    return b