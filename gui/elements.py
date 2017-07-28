import pygame, thorpy
import gui.parameters as guip

def get_rounded_frame_img(size, radius, color, thickness):
    assert color != (255,255,255)
    surface = pygame.Surface(size)
    surface.fill((255,255,255))
    outer = thorpy.graphics.get_aa_round_rect(size, radius, color)
    size2 = (size[0]-2*thickness, size[1]-2*thickness)
    radius2 = radius - thickness
    inner = thorpy.graphics.get_aa_round_rect(size2, radius2, (255,255,255))
    r = inner.get_rect()
    r.center = surface.get_rect().center
    surface.blit(outer, (0,0))
    surface.blit(inner, r.topleft)
    surface.set_colorkey((255,255,255))
    return surface


class CellInfo:
    def __init__(self, size, cell_size):
        self.e_title = thorpy.make_text("Cell infos", guip.TFS, guip.TFC)
        self.e_coord = thorpy.make_text("", guip.NFS, guip.NFC)
        self.e_altitude = thorpy.make_text("", guip.NFS, guip.NFC)
        self.e_mat_img = thorpy.Image.make(pygame.Surface(cell_size))
        self.e_mat_name = thorpy.make_text("", guip.NFS, guip.NFC)
        self.e_mat = thorpy.Clickable.make(elements=[self.e_mat_name, self.e_mat_img])
        self.e_mat.set_size((size[0]-20,None))
        thorpy.store(self.e_mat)
        self.e_mat.fit_children(axis=(False, True))
        self.elements = [self.e_title, self.e_mat, self.e_coord, self.e_altitude]
        self.e = thorpy.Box.make(self.elements, size=size)
        self.cell = None

    def update_and_draw(self, cell):
        self.e_mat_name.set_text(cell.material.name)
        self.e_mat_name.recenter()
        self.e_mat_img.set_image(cell.imgs[0])
        self.e.blit()
        self.e.fit_children()

class MaterialViewer:

    def __init__(self, size):
        self.size = size