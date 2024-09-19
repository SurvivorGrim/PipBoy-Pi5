import pypboy
from pypboy import BaseModule
from pypboy.modules.stats import status
from pypboy.modules.stats import special
from pypboy.modules.stats import perks
import settings

class Module(BaseModule):


    def __init__(self, *args, **kwargs):
        self.submodules = [
            status.Module(self),
            special.Module(self),
            perks.Module(self),
        ]
        super(Module, self).__init__(*args, **kwargs)

    def handle_resume(self):
        settings.hide_top_menu = False
        settings.hide_submenu = False
        settings.hide_main_menu = False
        settings.hide_footer = False
        self.active.handle_action("resume")
