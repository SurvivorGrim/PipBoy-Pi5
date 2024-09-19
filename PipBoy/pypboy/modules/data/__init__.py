from pypboy import BaseModule
from pypboy.modules.data import quests
#from pypboy.modules.data import stats
from pypboy.modules.data import stats
import settings


class Module(BaseModule):

    def __init__(self, *args, **kwargs):
        self.submodules = [
            #holotape_processor.Module(self),
            quests.Module(self),
            stats.Module(self),
        ]
        super(Module, self).__init__(*args, **kwargs)
        
    def handle_resume(self):
        settings.hide_top_menu = False
        settings.hide_submenu = False
        settings.hide_main_menu = False
        settings.hide_footer = False
        self.active.handle_action("resume")
