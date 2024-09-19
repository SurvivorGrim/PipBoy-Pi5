from pypboy import BaseModule
from pypboy.modules.boot import boot_text
from pypboy.modules.boot import pip_os
from pypboy.modules.boot import thumbs
import settings

class Module(BaseModule):

    def __init__(self, *args, **kwargs):
        self.submodules = [
            boot_text.Module(self),
            pip_os.Module(self),
            thumbs.Module(self),
        ]
        super(Module, self).__init__(*args, **kwargs)
        
    def handle_resume(self):
        settings.hide_top_menu = True
        settings.hide_submenu = True
        settings.hide_main_menu = True
        settings.hide_footer = True
        self.active.handle_action("resume")

