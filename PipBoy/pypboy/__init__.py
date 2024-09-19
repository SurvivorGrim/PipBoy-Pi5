import pygame
import game
import pypboy.ui
import settings
from enum import Enum

if settings.GPIO_AVAILABLE:
    import RPi.GPIO as GPIO


class GameState(Enum):
    PASSCODE = -5
    BOOT = -4
    RADIO = -3
    MAP = -2
    DATA = -1
    INV = 0
    STATS = 1


class BaseModule(game.EntityGroup):
    submodules = []
    currentSubmodule = 0

    def __init__(self, boy, *args, **kwargs):
        super(BaseModule, self).__init__()

        # if settings.GPIO_AVAILABLE:
        # GPIO.setup(self.GPIO_LED_ID, GPIO.OUT)
        # GPIO.output(self.GPIO_LED_ID, False)
        self.active = None

        self.pypboy = boy
        self.position = (0, 50)
        #
        self.submenu = pypboy.ui.SubMenu()
        self.submenu.menu = []
        for mod in self.submodules:
            self.submenu.menu.append(mod.label)
        self.submenu.selected = self.submenu.menu[0]
        self.submenu.position = (73, 93)
        self.add(self.submenu)

        self.action_handlers = {
            "pause": self.handle_pause,
            "resume": self.handle_resume
        }

        self.switch_submodule(0)

        if settings.SOUND_ENABLED:
            self.module_change_sfx = pygame.mixer.Sound('sounds/pipboy/UI_Pipboy_OK.ogg')
            self.module_change_sfx.set_volume(settings.VOLUME)

    def move(self, x, y):
        super(BaseModule, self).move(x, y)
        if hasattr(self, 'active'):
            self.active.move(x, y)

    def switch_submodule(self, module):
        # print("Changing to sub-module", module)
        if module < len(self.submodules):
            if hasattr(self, 'active') and self.active:
                self.active.handle_action("pause")
                self.remove(self.active)
            self.active = self.submodules[module]
            self.active.parent = self
            self.active.handle_action("resume")
            self.submenu.select(self.submenu.menu[module])
            self.add(self.active)
            self.currentSubmodule = module
        else:
            print("No submodule at %d" % module)

    # def render(self):
    #     super(BaseModule, self).render()

    def handle_action(self, action, value=0):

        if action.startswith("knob_"):
            # if action.startswith("knob_") and not settings.hide_submenu:
            num = int(action[-1])
            self.switch_submodule(num - 1)
        elif action in self.action_handlers:
            self.action_handlers[action]()
        else:
            if hasattr(self, 'active') and self.active:
                self.active.handle_action(action, value)

    def handle_event(self, event):
        if hasattr(self, 'active') and self.active:
            self.active.handle_event(event)

    def handle_pause(self):
        self.paused = True
        self.currentSubmodule = 0
        self.switch_submodule(0)
        # if settings.GPIO_AVAILABLE:
        # GPIO.output(self.GPIO_LED_ID, False)

    def handle_resume(self):
        self.paused = False
        self.currentSubmodule = 0
        self.switch_submodule(0)
        # if settings.GPIO_AVAILABLE:
        # GPIO.output(self.GPIO_LED_ID, True)
        if settings.SOUND_ENABLED:
            self.module_change_sfx.play()


class SubModule(game.EntityGroup):

    def __init__(self, parent, *args, **kwargs):
        super(SubModule, self).__init__()
        self.parent = parent
        self.paused = True

        self.action_handlers = {
            "pause": self.handle_pause,
            "resume": self.handle_resume
        }

        if settings.SOUND_ENABLED:
            self.submodule_change_sfx = pygame.mixer.Sound('sounds/pipboy/UI_Pipboy_OK.ogg')
            self.submodule_change_sfx.set_volume(settings.VOLUME)

    def handle_action(self, action, value=0):
        if action.startswith("dial_"):
            if hasattr(self, "menu"):
                self.menu.handle_action(action)
        elif action in self.action_handlers:
            self.action_handlers[action]()

    def handle_event(self, event):
        pass

    def handle_pause(self):
        if self.paused == False:
            self.paused = True

    def handle_resume(self):
        if self.paused == True:
            self.paused = False
            if settings.SOUND_ENABLED:
                self.submodule_change_sfx.play()
