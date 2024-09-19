import pypboy
from pypboy import BaseModule
from pypboy.modules.passcode import passcode
import settings

class Module(BaseModule):

    label = "PASSCODE"

    def __init__(self, *args, **kwargs):
        self.submodules = [
            passcode.Module(self),
        ]
        super(Module, self).__init__(*args, **kwargs)
        
    def handle_resume(self):
        settings.hide_top_menu = True
        settings.hide_submenu = True
        settings.hide_main_menu = True
        settings.hide_footer = True
        self.active.handle_action("resume")