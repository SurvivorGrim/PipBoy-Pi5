import pypboy
import pygame
import game
import settings


class Module(pypboy.SubModule):

    label = "STATS"

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)

        self.menu = pypboy.ui.Menu(settings.STATS)
        self.menu.rect[0] = settings.menu_x
        self.menu.rect[1] = settings.menu_y
        self.add(self.menu)

        self.topmenu = pypboy.ui.TopMenu()
        self.add(self.topmenu)
        self.topmenu.label = "DATA"
        self.topmenu.title = settings.MODULE_TEXT

        self.footer = pypboy.ui.Footer(settings.STATS_FOOTER)
        self.footer.rect[0] = settings.footer_x
        self.footer.rect[1] = settings.footer_y
        self.add(self.footer)
