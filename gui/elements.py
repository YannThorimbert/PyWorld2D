import pygame, thorpy
import gui.parameters as guip


def get_help_text(*texts,start="normal"):
    if start == "normal":
        state = 0
    else:
        state = 1
    get_text = {0:guip.get_info_text, 1:guip.get_highlight_text}
    els = []
    for text in texts:
        els.append(get_text[state](text))
        state = 1 if state==0 else 0
    return thorpy.make_group(els)

def get_help_text_normal(*texts,start="normal"):
    if start == "normal":
        state = 0
    else:
        state = 1
    get_text = {0:guip.get_text, 1:guip.get_highlight_text}
    els = []
    for text in texts:
        els.append(get_text[state](text))
        state = 1 if state==0 else 0
    return thorpy.make_group(els)


def get_cursors(rect, color):
    assert color != (255,255,255) #used for transparency
    thick = int(rect.w/5)
    if thick != 0:
        if thick%2 != 0: thick -= 1
    thick2 = int(rect.w/3)
    if thick2 != 0:
        if thick2%2 != 0: thick2 -= 1
    cursors = [get_cursor(rect, color, 0, thick2)]
    for thick in range(1,thick):
        cursors.append(get_cursor(rect, color, thick, thick2))
    if len(cursors) > 1:
        cursors.pop(0)
    cursors += cursors[::-1][1:-1]
    return cursors[::-1]

def get_cursor(rect, color, thick, thick2):
    surface = pygame.Surface(rect.size)
    surface = pygame.Surface(rect.size)
    surface.fill(color)
    rbulk = rect.inflate((-2*thick,-2*thick))
    rbulk.topleft = (thick,thick)
    pygame.draw.rect(surface, (255,255,255), rbulk)
    rh = pygame.Rect(0,thick2,rect.w,rect.h-2*thick2)
    pygame.draw.rect(surface, (255,255,255), rh)
    rw = pygame.Rect(thick2,0,rect.w-2*thick2,rect.w)
    pygame.draw.rect(surface, (255,255,255), rw)
    surface.set_colorkey((255,255,255))
    return surface

class CellInfo:
    def __init__(self, size, cell_size, redraw, external_e):
        self.e_coordalt = guip.get_text("")
        self.e_mat_img = thorpy.Image.make(pygame.Surface(cell_size))
        self.e_mat_name = guip.get_text("")
        self.e_mat = thorpy.make_group([self.e_mat_img, self.e_mat_name])
##        self.e_mat = thorpy.Clickable.make(elements=[self.e_mat_img, self.e_mat_name])
##        self.e_mat.set_size((size[0]-10,None))
##        thorpy.store(self.e_mat, mode="h", x=2, margin=2)
##        self.e_mat.fit_children(axis=(False, True))
        self.elements = [self.e_mat, self.e_coordalt]
        self.e = thorpy.Box.make(self.elements)
        self.e.set_size((size[0],None))
        for e in self.e.get_elements():
            e.recenter()
        self.cell = None
        #emap : to be displayed when a cell is clicked
        self.em_title = guip.get_title("Cell informations")
        self.em_coord = guip.get_text("")
        self.em_altitude = guip.get_text("")
        self.em_name = guip.get_small_text("")
        self.em_rename = guip.get_small_button("Rename", self.rename_current_cell)
        self.em_name_rename = thorpy.make_group([self.em_name, self.em_rename])
##        self.em_name_rename = thorpy.Clickable.make(elements=[self.em_name, self.em_rename])
##        thorpy.store(self.em_name_rename)
        self.em_name_rename.fit_children()
        self.em_mat_img_img = thorpy.Image.make(pygame.Surface(cell_size))
        self.em_mat_img = thorpy.Clickable.make(elements=[self.em_mat_img_img])
        self.em_mat_img.fit_children()
        self.em_mat_name = guip.get_text("")
        self.em_mat = thorpy.make_group([self.em_mat_img, self.em_mat_name])
        self.em_elements = [self.em_title, thorpy.Line.make(100), self.em_mat, self.em_coord, self.em_altitude, self.em_name_rename]
        self.em = thorpy.Box.make(self.em_elements)
        self.em.set_main_color((200,200,200,150))
        self.launched = False
        self.redraw = redraw
        self.external_e = external_e
        reac = thorpy.Reaction(thorpy.THORPY_EVENT, self.set_unlaunched,
                                {"id":thorpy.constants.EVENT_UNLAUNCH})
        external_e.add_reaction(reac)

    def set_unlaunched(self, e):
        if e.launcher.launched == self.em:
            self.launched = False

    def update_em(self, cell):
        self.em_mat_img_img.set_image(cell.get_img_at_zoom(0))
        self.em_mat_name.set_text(cell.material.name)
        thorpy.store(self.em_mat, mode="h")
        self.em_coord.set_text("Coordinates: "+str(cell.coord))
        self.em_altitude.set_text("Altitude: "+str(round(cell.get_altitude()))+"m")
        if not cell.name:
            cellname = "This location has no name"
        else:
            cellname = cell.name
        self.em_name.set_text(cellname)
        thorpy.store(self.em_name_rename, mode="h")
        self.em.store()
        self.em.fit_children()

    def launch_em(self, cell, pos, rect):
        if not self.launched:
            self.launched = True
            self.redraw()
            self.update_em(cell)
            #
            self.em.set_visible(False)
            for e in self.em.get_descendants():
                e.set_visible(False)
            thorpy.launch_nonblocking(self.em,True)
            self.em.set_visible(True)
            for e in self.em.get_descendants():
                e.set_visible(True)
            self.em.set_center(pos)
            self.em.clamp(rect)
            self.em.blit()
            self.em.update()
        else:
            print("Already launched!")

    def rename_current_cell(self):
        varset = thorpy.VarSet()
        varset.add("newname", "", "New name")
##        ps = thorpy.ParamSetterLauncher.make(varset)
        ps = thorpy.ParamSetter.make([varset])
        for h in ps.get_handlers():
            ins = ps.handlers[h]
        ins.set_main_color((200,200,200,150))
        ps.center()
        ins.enter() #put focus on inserter
        thorpy.launch_blocking(ps)
        newname = ins.get_value()
        if newname:
            self.cell.name = newname
        self.update_em(self.cell)
        self.redraw()
        self.em.blit()
        pygame.display.flip()

##    def em_react(self, event):
##        if self.launched:
##            self.menu.react(event)

    def update_e(self, cell):
        self.cell = cell
        if cell.name:
            name = cell.name + " (" + cell.material.name + ")"
        else:
            name = cell.material.name
        self.e_mat_name.set_text(name)
        new_img = cell.extract_all_layers_img_at_zoom(0)
        self.e_mat_img.set_image(new_img)
        thorpy.store(self.e_mat, mode="h")
        #
        altitude = round(cell.get_altitude())
        alt_text = str(altitude) + "m"
        coord_text = str(cell.coord) + "     "
        self.e_coordalt.set_text(coord_text+alt_text)
        self.e_coordalt.recenter()
        #
##        if cell.name:
##            self.e_title.set_text(cell.name)
##            self.e_title.recenter()
        #
##        self.e.blit()

class AlertPool:

    def __init__(self):
        self.alerts = []
        self.countdowns = {}

    def add_alert_countdown(self, element, countdown):
        self.countdowns[element] = countdown

    def add_alert(self, element, counter):
        self.alerts.append([element, counter])

    def alert_indices(self):
        for i in range(len(self.alerts)-1, -1, -1):
            yield i

    def refresh(self):
        for i in self.alert_indices():
            self.alerts[i][1] -= 1
            if self.alerts[i][1] < 0:
                self.alerts.pop(i)
        for e in self.countdowns:
            self.countdowns[e] -= 1


    def draw(self, screen, x, y, gap=5):
        for i in self.alert_indices():
            e = self.alerts[i][0]
            e.set_topleft((x,y))
            e.blit()
            y += e.get_fus_size()[1] + gap
        for e in self.countdowns:
            if self.countdowns[e] < 0:
                e.set_topleft((x,y))
                e.blit()
                y += e.get_fus_size()[1] + gap




class HelpBox:

    def __init__(self, helps):
        """helps is a list of tuple on the form (title, list_of_help_texts)."""
        elements = []
        for title, texts in helps:
            e_title = guip.get_title(title)
            e_line = thorpy.Line.make(e_title.get_fus_size()[0])
            e_helps = []
            for h in texts:
                e_helps.append(get_help_text_normal(*h))
            elements += [e_line,e_title] + e_helps
        self.e = thorpy.make_ok_box(elements)
        self.b = thorpy.Element.make(size=thorpy.functions.get_screen_size())
        self.b.set_main_color((200,200,200,100))
        self.e.center()
        self.launcher = thorpy.make_button("See commands", self.launch)

    def launch(self):
        self.b.blit()
        pygame.display.flip()
        thorpy.launch_blocking(self.e)
        thorpy.functions.quit_menu_func()


