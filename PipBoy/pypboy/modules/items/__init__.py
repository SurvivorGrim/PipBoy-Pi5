from pypboy import BaseModule
from pypboy.modules.items import weapons
from pypboy.modules.items import apparel
from pypboy.modules.items import aid
from pypboy.modules.items import misc
from pypboy.modules.items import ammo
import settings

class Module(BaseModule):

    def __init__(self, *args, **kwargs):
        self.submodules = [
            weapons.Module(self),
            apparel.Module(self),
            aid.Module(self),
            misc.Module(self),
            ammo.Module(self)
        ]
        super(Module, self).__init__(*args, **kwargs)
        
    def handle_resume(self):
        settings.hide_top_menu = False
        settings.hide_submenu = False
        settings.hide_main_menu = False
        settings.hide_footer = False
        self.active.handle_action("resume")