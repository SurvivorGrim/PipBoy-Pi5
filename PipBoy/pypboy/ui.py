# ui.py

import game
import pygame
import settings
import time
import os
import os
import imp
import io
import cairosvg
from datetime import datetime
from collections import deque

# Global variable to store the selected submenu text
current_submenu_text = None

def word_wrap(surf, text, font):
    text = str(text)
    font.origin = True
    words = text.split()
    width, height = surf.get_size()
    line_spacing = font.get_sized_height()
    x, y = 0, line_spacing
    for word in words:
        word = word + "  "
        bounds = font.get_rect(word)
        if x + bounds.width + bounds.x >= width:
            x, y = 0, y + line_spacing
        font.render_to(surf, (x, y), word, settings.bright, None, 1)
        x += bounds.width
    return x, y

def load_svg(filename, width, height):
    drawing = cairosvg.svg2png(url=filename)
    byte_io = io.BytesIO(drawing)
    image = pygame.image.load(byte_io, 'converted.png').convert_alpha()

    size = image.get_size()
    scale = min(width / size[0], (height-10) / size[1])
    if size[1] != height:
        new_width = int(round(size[0] * scale))
        new_height = int(round(size[1] * scale))
        image = pygame.transform.smoothscale(image, (new_width, new_height))
    image.fill(settings.bright, None, pygame.BLEND_RGBA_MULT)
    return image

class TopMenu(game.Entity):
    def __init__(self, label=None, title=[]):
        self.label = None
        self.prev_label = 0
        self.title = []
        self.saved_label = None
        super(TopMenu, self).__init__((480, 30)) # Width and height of TopMenu
        self.rect[0] = 0  # X position of TopMenu
        self.rect[1] = 0  # Y position of TopMenu

    def render(self):
        if settings.hide_top_menu and settings.hide_top_menu != 3:
            self.image.fill((0, 0, 0))
            settings.hide_top_menu = 3
            if self.label:
                self.saved_label = self.label
                self.prev_label = None
                self.label = None
        elif not settings.hide_top_menu:
            if self.saved_label:
                self.label = self.saved_label
                self.saved_label = None
            spacing = 15
            prev_text_width = 40
            text_pos = 70 - spacing - prev_text_width
            if self.label:
                if (self.label != self.prev_label):
                    self.image.fill((0, 0, 0))
                    for section in self.title:
                        text = settings.RobotoB[18].render(section, True, (settings.bright), (0, 0, 0))
                        text_pos = text_pos + prev_text_width + spacing
                        self.image.blit(text, (text_pos, 0))
                        text_rect = text.get_rect()
                        prev_text_width = text_rect.width

                        if section == self.label:
                            pygame.draw.line(self.image, settings.bright, (0, 25), (text_pos - 10, 25), 2)
                            pygame.draw.line(self.image, settings.bright, (text_pos + text_rect.width + 10, 25), (480, 25), 2)
                            pygame.draw.line(self.image, settings.bright, (text_pos - 11, 5), (text_pos - 11, 25), 2)
                            pygame.draw.line(self.image, settings.bright, (text_pos - 12, 5), (text_pos - 3, 5), 2)
                            pygame.draw.line(self.image, settings.bright, (text_pos + text_rect.width + 2, 5), (text_pos + text_rect.width + 12, 5), 2)
                            pygame.draw.line(self.image, settings.bright, (text_pos + text_rect.width + 11, 5), (text_pos + text_rect.width + 11, 25), 2)
                        else:
                            pygame.draw.line(self.image, settings.bright, (text_pos - 10, 25), (text_pos + text_rect.width + 10, 25), 2)
                self.prev_label = self.label

class Scanlines(game.core.Entity):
    def __init__(self):
        super(Scanlines, self).__init__((480, 380)) # Width and height of Scanlines
        self.image = pygame.image.load('images/scanline.png').convert_alpha()
        self.rectimage = self.image.get_rect()
        self.rect[1] = 0  # Y position of Scanlines
        self.top = -130  # Initial Y position for animation
        self.speed = 10
        self.clock = pygame.time.Clock()
        self.animation_time = 0.05
        self.prev_time = 0
        self.dirty = 2

    def render(self, *args, **kwargs):
        self.current_time = time.time()
        self.delta_time = self.current_time - self.prev_time

        if self.delta_time >= self.animation_time:
            self.prev_time = self.current_time
            self.top = self.top + self.speed
            if self.top >= 320 + 130:
                self.top = -130
            self.rect[0] = -100  # X position of Scanlines
            self.rect[1] = self.top  # Updated Y position for animation
        super(Scanlines, self).render(self, *args, **kwargs)

class Overlay(game.Entity):
    def __init__(self):
        super(Overlay, self).__init__()
        self.image = pygame.image.load('images/overlay.png').convert_alpha()

class SubMenu(game.Entity):
    def __init__(self):
        super(SubMenu, self).__init__((480, 30)) # Width and height of SubMenu
        self.menu = []
        self.rect[0] = 0  # X position of SubMenu
        self.rect[1] = 30  # Y position of SubMenu
        self.saved_module = None

    def render(self):
        if settings.hide_submenu and settings.hide_submenu != 3:
            settings.hide_submenu = 3
            self.image.fill(settings.black)
            self.saved_module = self.selected
        elif not settings.hide_submenu and self.saved_module:
            self.select(self.saved_module)
            self.saved_module = None

    def select(self, module):
        global current_submenu_text
        self.selected = module
        current_submenu_text = module
        print(f"Selected SubMenu Item: {current_submenu_text}")
        
        # Change description box position if the selected submenu is "STATS"
        if current_submenu_text == "STATS":
            print("yes")
            settings.description_box_y = 10  # Y position of description box
            settings.description_box_x = 210  # X position of description box
            settings.description_box_width = 250  # Width of description box
            Menu.render
        else:
            print("no")
            settings.description_box_y = 120  # Default Y position of description box
            settings.description_box_x = 260  # Default X position of description box
            settings.description_box_width = 160  # Default width of description box
            
            
        self.image.fill(settings.black)
        self.textoffset = 18
        if not settings.hide_submenu:
            for m in self.menu:
                padding = 1
                text_width = 0
                while text_width < 54:
                    spaces = " ".join([" " for x in range(padding)])
                    text = settings.RobotoR[14].render("%s%s%s" % (spaces, m, spaces), True, settings.mid, (0, 0, 0))
                    text_width = text.get_size()[0]
                    padding += 1
                if m == self.selected:
                    text = settings.RobotoR[14].render("%s%s%s" % (spaces, m, spaces), True, settings.bright, (0, 0, 0))
                self.image.blit(text, (self.textoffset, 0))
                self.textoffset = self.textoffset + text_width

class Footer(game.Entity):
    def __init__(self, sections=[]):
        super(Footer, self).__init__((480, 50)) # Width and height of Footer
        self.sections = sections

        self.text_left = None
        self.text_middle = None
        self.text_right = None
        self.bar_graph_num = None
        self.bar_graph_centered = False
        self.line_1 = None
        self.line_2 = None
        self.current_time = 0

        self.padding = 8
        self.animation_time = 0.5
        self.delta_time = 0
        self.prev_time = 0

    def expand(self, oldValue, oldMin, oldMax, newMin, newMax):
        oldRange = oldMax - oldMin
        newRange = newMax - newMin
        newValue = ((oldValue - oldMin) * newRange / oldRange) + newMin
        return newValue

    def time_text(self):
        now = datetime.now()
        date = str(now.strftime("%m") + "/" + now.strftime("%d") + "/" + now.strftime("%Y"))
        time = now.strftime("%H:%M:%S")
        return date, time

    def render(self):
        if settings.hide_footer and settings.hide_footer != 3:
            self.image.fill((0, 0, 0))
            settings.hide_footer = 3
        elif not settings.hide_footer:
            self.current_time = time.time()
            self.delta_time = self.current_time - self.prev_time

            if self.delta_time >= self.animation_time:
                self.prev_time = self.current_time

                if self.sections:
                    self.image.fill(settings.dark)

                    self.text_width = 0
                    self.line_1 = 0
                    self.line_2 = 0

                    try:
                        self.text_left = str(self.sections[0])
                    except:
                        self.text_left = None

                    try:
                        self.text_middle = str(self.sections[1])
                    except:
                        self.text_middle = None

                    try:
                        self.text_right = str(self.sections[2])
                    except:
                        self.text_right = None

                    try:
                        self.bar_graph_num = self.sections[3]
                    except:
                        self.bar_graph_num = None

                    try:
                        self.bar_graph_centered = self.sections[4]
                    except:
                        self.bar_graph_centered = False

                    if self.text_left == "DATE" or self.text_middle == "TIME":
                        time_text = self.time_text()
                        self.date = time_text[0]
                        self.time = time_text[1]
                        self.text_left = self.date
                        self.text_middle = self.time

                    if self.text_left:
                        text = settings.RobotoB[12].render(self.text_left, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (self.padding, 3))
                        self.line_1 = self.text_width + self.padding * 3
                        if self.text_right != "" or self.text_middle != "":
                            pygame.draw.line(self.image, settings.black, (self.line_1, 0), (self.line_1, 30), 3)

                    if isinstance(self.bar_graph_num, int) and self.bar_graph_centered:
                        text = settings.RobotoB[12].render(self.text_right, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (480 - self.text_width - self.padding, 3))
                        self.line_2 = 480 - self.text_width - self.padding * 3
                        pygame.draw.line(self.image, settings.black, (self.line_2, 0), (self.line_2, 30), 3)

                        text = settings.RobotoB[12].render(self.text_middle, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (self.line_1 + self.padding, 3))
                        bar_graph_start = self.line_1 + self.text_width + self.padding * 2
                        bar_graph_end = self.line_2 - self.padding

                        pygame.draw.lines(self.image, settings.light, True,
                                          [(bar_graph_start, 5), (bar_graph_end, 5),
                                           (bar_graph_end, 14), (bar_graph_start, 14)], 2)
                        bar_start = bar_graph_start + 2
                        bar_max_width = bar_graph_end - 2 - bar_start + 2
                        bar_width = int(self.expand(self.bar_graph_num, 0, 100, 0, bar_max_width))
                        pygame.draw.rect(self.image, settings.bright, (bar_start, 7, bar_width, 7))

                    elif isinstance(self.bar_graph_num, int) and not self.bar_graph_centered:
                        text = settings.RobotoB[12].render(self.text_middle, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (self.line_1 + self.padding, 3))
                        self.line_2 = self.line_1 + self.text_width + self.padding * 2
                        pygame.draw.line(self.image, settings.black, (self.line_2, 0), (self.line_2, 30), 3)

                        text = settings.RobotoB[12].render(self.text_right, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (self.line_2 + self.padding, 3))

                        bar_graph_start = self.line_2 + self.text_width + self.padding * 2
                        bar_graph_end = 480 - self.padding

                        pygame.draw.lines(self.image, settings.light, True,
                                          [(bar_graph_start, 5), (bar_graph_end, 5),
                                           (bar_graph_end, 14), (bar_graph_start, 14)], 2)

                        bar_start = bar_graph_start + 2
                        bar_max_width = bar_graph_end - 2 - bar_start + 2
                        bar_width = int(self.expand(self.bar_graph_num, 0, 100, 0, bar_max_width))
                        pygame.draw.rect(self.image, settings.bright, (bar_start, 7, bar_width, 7))

                    else:
                        text = settings.RobotoB[12].render(self.text_middle, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (self.line_1 + self.padding, 3))
                        self.line_2 = self.line_1 + self.text_width + self.padding * 2
                        if self.text_middle != "":
                            pygame.draw.line(self.image, settings.black, (self.line_2, 0), (self.line_2, 30), 3)

                        text = settings.RobotoB[12].render(self.text_right, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (480 - self.text_width - self.padding, 3))
        self.rect[0] = 0  # X position of Footer
        self.rect[1] = 300  # Y position of Footer

class Menu(game.Entity):
    def __init__(self, menu_array=[], callbacks=[], selected=0):
        super(Menu, self).__init__((480, 380)) # Width and height of Menu
        self.source_array = menu_array

        self.prev_time = 0
        self.prev_fps_time = 0
        self.clock = pygame.time.Clock()
        self.animation_time = 0.2
        self.index = 0
        self.top_of_menu = 0
        self.max_items = 10
        self.menu_array = self.source_array[self.top_of_menu:self.max_items]
        self.prev_selection = 0
        self.descriptionbox = pygame.Surface((200, 250)) # Width of description box is dynamic, height fixed
        self.imagebox = pygame.Surface((150, 120)) # Width and height of imagebox
        
        

        self.saved_selection = 0

        try:
            self.callbacks = callbacks
        except:
            self.callbacks = []

        self.arrow_img_up = load_svg("./images/inventory/arrow.svg", 20, 20) # Width and height of arrow image
        self.arrow_img_down = pygame.transform.flip(self.arrow_img_up, False, True)

        self.selected = selected
        self.select(self.selected)

        if settings.SOUND_ENABLED:
            self.dial_move_sfx = pygame.mixer.Sound('sounds/pipboy/RotaryVertical/UI_PipBoy_RotaryVertical_01.ogg')
            self.dial_move_sfx.set_volume(settings.VOLUME)

        self.rect[0] = 0  # X position of Menu
        self.rect[1] = 0  # Y position of Menu

    def select(self, item):
        if not settings.hide_main_menu:
            self.selected = item
            self.redraw()
            if len(self.callbacks) > item and self.callbacks[item]:
                self.callbacks[item]()

    def handle_action(self, action):
        if not settings.hide_main_menu:
            if action == "dial_up":
                if self.selected > 0:
                    if settings.SOUND_ENABLED:
                        self.dial_move_sfx.play()
                    self.selected -= 1
                    self.select(self.selected)

            if action == "dial_down":
                if self.selected < len(self.source_array) - 1:
                    self.selected += 1
                    if settings.SOUND_ENABLED:
                        self.dial_move_sfx.play()
                    self.select(self.selected)

    def redraw(self):
        self.image.fill((0, 0, 0))
        offset = 10

        if self.selected > self.max_items - 1:
            self.top_of_menu = self.selected - self.max_items + 1
            self.menu_array = self.source_array[self.top_of_menu:(self.top_of_menu + self.max_items)]
        else:
            self.top_of_menu = 0
            self.menu_array = self.source_array[self.top_of_menu:(self.top_of_menu + self.max_items)]
            self.prev_selection = None

        for i in range(len(self.menu_array)):
            if self.selected > self.max_items - 1:
                self.prev_selection = self.selected
                self.selected = self.selected - self.top_of_menu

            if i == self.selected:
                text = settings.RobotoB[12].render(" %s " % self.menu_array[i][0], True, (0, 0, 0), (settings.bright))
                try:
                    number = settings.RobotoB[12].render(" %s " % self.menu_array[i][1], True, (0, 0, 0), (settings.bright))
                except:
                    number = ""

                selected_rect = (0, offset, 200, text.get_size()[1])  # Rectangle dimensions for selected menu item
                pygame.draw.rect(self.image, (settings.bright), selected_rect)

                self.images = []
                try:
                    self.image_url = self.menu_array[i][2]
                    if os.path.isdir(self.image_url):
                        for filename in sorted(os.listdir(self.image_url)):
                            if filename.endswith(".png"):
                                filename = self.image_url + "/" + filename
                                self.images.append(pygame.image.load(filename).convert_alpha())
                                self.frameorder = []
                            if filename.endswith(".svg"):
                                svg_surface = load_svg(self.image_url + "/" + filename, self.imagebox.get_width(), self.imagebox.get_height())
                                self.images.append(svg_surface)
                                self.frameorder = []
                            if filename == "frameorder.py":
                                url = self.image_url + "/" + filename
                                file = imp.load_source("frameorder.py", os.path.join(self.image_url, "frameorder.py"))
                                self.frameorder = file.frameorder
                                self.frame = 0
                    else:
                        if self.image_url:
                            self.frameorder = []
                            if self.image_url.endswith(".svg"):
                                graphic = load_svg(self.image_url, self.imagebox.get_width(), self.imagebox.get_height())
                                self.imagebox.blit(graphic, (0, 0))
                                self.image.blit(self.imagebox, (0, 0))
                            else:
                                graphic = pygame.image.load(self.image_url).convert_alpha()
                                self.image.blit(graphic, (0, 0))
                except:
                    self.image_url = ""

                try:
                    description = self.menu_array[i][3]
                except:
                    description = ""


                # Change description box position if the selected submenu is "STATS"
                if current_submenu_text == "STATS":
                    self.descriptionbox = pygame.Surface((250, 250)) # Width of description box is dynamic, height fixed
                    settings.description_box_width = 250
                    print(settings.description_box_width)
                else:
                    settings.description_box_width = 160
                    self.descriptionbox = pygame.Surface((160, 250)) # Width of description box is dynamic, height fixed
                    print(settings.description_box_width)
                    

                if description:
                    self.descriptionbox.fill((0, 0, 0))
                    word_wrap(self.descriptionbox, description, settings.FreeRobotoR[11])
         
                    self.image.blit(self.descriptionbox, (settings.description_box_x, settings.description_box_y))
                try:
                    stats = self.menu_array[i][4]
                except:
                    stats = ""

                if stats:
                    stat_offset = 0
                    self.descriptionbox.fill((0, 0, 0))
                    for each in stats:
                        stat_text = settings.RobotoB[10].render(" %s " % each[0], True, (settings.bright), (settings.dark))
                        stat_number = settings.RobotoB[10].render(" %s " % each[1], True, (settings.bright), (settings.dark))
                        stat_rect = (0, stat_offset, settings.description_box_width, stat_text.get_size()[1])
                        pygame.draw.rect(self.descriptionbox, (settings.dark), stat_rect)
                        self.descriptionbox.blit(stat_text, (0, stat_offset))
                        self.descriptionbox.blit(stat_number, (settings.description_box_width - stat_number.get_size()[0], stat_offset))
                        stat_offset += stat_text.get_size()[1] + 4
                        self.image.blit(self.descriptionbox, (settings.description_box_x, settings.description_box_y))

            else:
                text = settings.RobotoB[12].render(" %s " % self.menu_array[i][0], True, (settings.bright), (0, 0, 0))
                try:
                    number = settings.RobotoB[12].render(" %s " % self.menu_array[i][1], True, (settings.bright), (0, 0, 0))
                except:
                    number = None

            if self.prev_selection:
                self.selected = self.prev_selection

            self.image.blit(text, (20, offset))

            if number:
                self.image.blit(number, (200 - number.get_size()[0], offset))
            offset += text.get_size()[1] + 4

        if len(self.source_array) > len(self.menu_array):
            if self.top_of_menu != 0:
                self.image.blit(self.arrow_img_up, (100, 0))

        if len(self.source_array) > len(self.menu_array):
            if self.top_of_menu != len(self.source_array) - self.max_items:
                self.image.blit(self.arrow_img_down, (100, 200))
                
    def render(self, *args, **kwargs):            
        self.image.blit(self.descriptionbox, (settings.description_box_x, settings.description_box_y))
        
        if settings.hide_main_menu and settings.hide_main_menu != 3:
            settings.hide_main_menu = 3
            self.image.fill(settings.black)
            self.saved_selection = self.selected

        elif not settings.hide_main_menu:
            if self.saved_selection:
                self.select(self.saved_selection)
                self.saved_selection = None

            self.current_time = time.time()
            self.delta_time = self.current_time - self.prev_time                
                
            if hasattr(self, 'images') and self.images:
                if self.delta_time >= self.animation_time:
                    self.prev_time = self.current_time

                    self.imagebox.fill((0, 0, 0))

                    if self.index >= len(self.images):
                        self.index = 0

                    if self.frameorder:
                        if self.frame >= len(self.frameorder):
                            self.frame = 0
                        self.index = self.frameorder[self.frame]
                        self.frame += 1

                    self.file = self.images[self.index]
                    self.imagebox.blit(self.file, (0, 0))
                    self.imagebox.fill(settings.bright, None, pygame.BLEND_RGBA_MULT)
                    self.image.blit(self.imagebox, (280, 0)) #imgbox position

                    self.index += 1
