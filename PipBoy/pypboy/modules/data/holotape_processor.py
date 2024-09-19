# -*- coding: utf-8 -*-
import glob
import numpy as np
import pypboy
import pygame
import game
import settings
import pygcurse
import os
import time
import xml.etree.ElementTree as ET


class Module(pypboy.SubModule):
    label = "HOLOTAPES"

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)

        self.holotape_folder = 'holotapes/'
        self.holotapes = []
        self.main_menu = []
        self.holotapes_data_set = []
        self.holotapes_data_set = self.get_data()

        self.grid = pygame.Surface((270, 270))

        for holotapes_data in self.holotapes_data_set:
            # holotapes_data = [holotape_name, folder_name, static_text, dynamic_text, menu, action, image]
            # Menu Structure: ["Menu item",Quantity,"Image (or folder for animation")","Description text",[["stats_text_1","stats_number_1"],["stats_text_2","stats_number_2"]]],
            holotape_name = holotapes_data[0]
            image = settings.holotape_generic
            self.main_menu.append([holotape_name, "", image])
            self.holotapes.append(HolotapeClass(holotape_name, holotapes_data))

        self.active_holotape = None

        holotapeCallbacks = []
        for i, holotape in enumerate(self.holotapes):
            holotapeCallbacks.append(lambda i=i: self.select_holotape(i))

        self.topmenu = pypboy.ui.TopMenu()
        self.topmenu.label = "DATA"
        self.topmenu.title = settings.MODULE_TEXT
        self.add(self.topmenu)

        self.menu = pypboy.ui.Menu(self.main_menu, holotapeCallbacks, 0)
        self.menu.rect[0] = settings.menu_x
        self.menu.rect[1] = settings.menu_y
        self.add(self.menu)

        settings.FOOTER_TIME[2] = ""
        self.footer = pypboy.ui.Footer(settings.FOOTER_TIME)
        self.footer.rect[0] = settings.footer_x
        self.footer.rect[1] = settings.footer_y
        self.add(self.footer)

        self.prev_static_text = None

    def select_holotape(self, holotape):
        if hasattr(self, 'active_holotape') and self.active_holotape:
            self.remove(self.active_holotape)
            if self.active_holotape.alive():
                self.remove(self.active_holotape)
        self.active_holotape = self.holotapes[holotape]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:

                self.add(self.active_holotape)

                if self.active_holotape.alive():
                    settings.hide_top_menu = True
                    settings.hide_submenu = True
                    settings.hide_main_menu = True
                    settings.hide_footer = False
                    # self.active_holotape.write_display(0, False)
                    print("Loading Holotape:", self.active_holotape.label)

                if self.active_holotape and not self.active_holotape.skip and self.active_holotape.crawling:
                    self.active_holotape.handle_event(event)

            elif event.key == pygame.K_BACKSPACE:
                self.handle_resume()
                print("Back to main holotape menu")

        if self.active_holotape and self.active_holotape.waiting_for_input:
            self.active_holotape.handle_event(event)

    def handle_resume(self):
        super(Module, self).handle_resume()
        if hasattr(self, 'active_holotape') and self.active_holotape:
            self.active_holotape.clear_display()
        if self.active_holotape.alive():
            self.remove(self.active_holotape)
        if self.paused:
            self.paused = False
            settings.hide_top_menu = False
            settings.hide_submenu = False
            settings.hide_main_menu = False
            settings.hide_footer = False

    def handle_pause(self):
        # print("Holotape paused")
        self.active_holotape.clear_display()

    def get_data(self):
        # Get list of folders
        folders = []
        holotapes_data = []
        holotape_name = None
        holotape_type = None
        folder_name = None

        for f in sorted(os.listdir(self.holotape_folder)):
            if not f.endswith("/"):
                folders.append(self.holotape_folder + f)

        for folder in folders:
            holotape_page_data = []
            folder_name = os.path.basename(folder)  # Get the folder name without the full path
            if len(glob.glob(folder + "/holotape.xml")) == 0:
                print("No holotape.xml file in:", folder)
                continue
            menu_file = ("./" + folder + "/" + "holotape.xml")

            try:
                holotape_xml = ET.parse(menu_file).getroot()

                for element in holotape_xml.iter("title"):
                    holotape_name = element.text
                for element in holotape_xml.iter("type"):
                    holotape_type = element.text

                pages = []
                for page in holotape_xml.iter("page"):
                    page_data = []
                    static_text = None
                    static_texts = []
                    try:
                        static_text = page.find("static_text").text
                        self.prev_static_text = static_text
                    except:
                        if self.prev_static_text:
                            static_text = self.prev_static_text
                        else:
                            static_text = None

                    dynamic_text = None
                    try:
                        dynamic_text = page.find("dynamic_text").text
                    except:
                        dynamic_text = None

                    menu = []
                    action = []
                    try:
                        for element in page.find("menu"):
                            menu.append(element.text)
                            try:
                                attribute = element.attrib
                                if attribute["page"]:
                                    action.append(attribute["page"])
                            except:
                                action.append("0")
                    except:
                        # print("No menu found in:",page)
                        menu = ["[< Back]"]
                        action = ["Previous"]
                    page_data.append(static_text)
                    page_data.append(dynamic_text)
                    page_data.append(menu)
                    page_data.append(action)
                    pages.append(page_data)
                    # print("********************")
                    # print(page_data)
                    # print("********************")

            except Exception as e:
                holotape_name = folder_name
                print(str(e), ' could not read xml file in', folder_name)

            holotape_page_data = [holotape_name, folder_name, holotape_type, pages]
            # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            # print(holotape_page_data)
            # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxx")

            holotapes_data.append(holotape_page_data)

        return holotapes_data


class HolotapeDisplay(game.Entity):
    def __init__(self, *args, **kwargs):
        super(HolotapeDisplay, self).__init__((settings.WIDTH, settings.HEIGHT - 100), *args, **kwargs)

        self.holotape_image_width = settings.WIDTH - 10
        self.holotape_image = pygame.Surface((self.holotape_image_width, settings.HEIGHT - 100))
        self.holotape_image.fill((0, 0, 0))
        self.rect[0] = 11
        self.rect[1] = 51

        self.cursor_x = 0
        self.cursor_y = 0
        self.prev_x = 0
        self.prev_y = 0

        self.prev_time = 0
        self.current_time = 0
        self.button = None
        self.cursor_time = 1  # Cursor blink speed
        self.prev_cursor_time = 0
        self.char_index = 0
        self.menu_index = 0
        self.prev_line = 0
        self.blink = False
        self.static_text_index = 0
        self.dynamic_text_index = 0
        self.menu_text_index = 0
        self.menu_start = 0
        self.menu_end = 0
        self.line = 0
        self.waiting_for_input = False
        self.crawling = False

        # Audio holotape related:
        self.holotape_waveform_width, self.holotape_waveform_height = 250, 250
        self.holotape_waveform_image = pygame.Surface((self.holotape_waveform_width, self.holotape_waveform_height))
        self.holotape_waveform_animation_time = 1 / settings.waveform_fps
        self.grid = pygame.Surface((270, 270))

        self.prev_time = 0
        self.index = 0
        self.current_time = 0
        self.delta_time = 0
        self.prev_waveform_time = 0
        self.holotape_waveform = None
        self.holotape_waveform_length = None
        self.audio_file = None
        self.audio_file_length = 0
        self.sound_object = None
        self.max_length = 0
        self.page = 0
        self.previous_page = 0
        self.skip = False
        self.console_text = None
        self.saved_song = None
        self.saved_song_pos = None

        if settings.SOUND_ENABLED:
            self.sfx_dial_move = pygame.mixer.Sound('./sounds/pipboy/RotaryVertical/UI_PipBoy_RotaryVertical_01.ogg')
            self.sfx_dial_move.set_volume(settings.VOLUME)
            self.sfx_text = pygame.mixer.Sound('./sounds/terminal/UI_Terminal_CharScroll_LP.ogg')
            self.sfx_text.set_volume(settings.VOLUME / 3)
            self.sfx_ok = pygame.mixer.Sound('./sounds/pipboy/UI_Pipboy_OK_Press.ogg')
            self.sfx_ok.set_volume(settings.VOLUME)

        self.font = settings.TechMono[25]
        self.char_width, self.char_height = self.font.size("X")
        self.max_chars = int(settings.WIDTH / self.char_width) - 5
        self.max_lines = int((settings.HEIGHT - 100) / self.char_height) - 1


        # Create the pygcurse surface
        self.holotape_screen = pygcurse.PygcurseSurface(self.max_chars, self.max_lines + 1, self.font,
                                                        settings.bright, settings.black, self.holotape_image, True,
                                                        1000)
        self.holotape_screen._autoupdate = False
        self.holotape_screen._autodisplayupdate = False

    def write_display(self, page, skip=False):
        # print ("Drawing page:", page, "self.previous_page = ",self.previous_page,'Skip=',skip)
        self.waiting_for_input = False
        self.skip = skip
        self.previous_page = self.page
        self.page = page
        settings.hide_top_menu = True
        settings.hide_submenu = True
        settings.hide_main_menu = True
        settings.hide_footer = True
        self.line = 0
        self.static_text_index = 0
        self.dynamic_text_index = 0
        self.menu_text_index = 0
        self.char_index = 0
        self.holotape_screen.cursor = (0, 0)

        if self.page >= len(self.holotape_data[3]):
            print("Selected an invalid page", self.page, len(self.holotape_data[3]))
            self.page = 0

        self.static_text, self.dynamic_text, self.menu, self.actions = self.fetch_page(self.holotape_data, self.page)

        self.static_text = self.static_text.replace('\\n', '\n').replace('\\t', '\t')

        if self.dynamic_text:
            self.dynamic_text = self.dynamic_text.replace('\\n', '\n').replace('\\t', '\t')

    def clear_display(self):
        self.holotape_image.fill((0, 0, 0))
        self.static_text_index = 0
        self.dynamic_text_index = 0
        self.menu_text_index = 0
        self.char_index = 0
        self.waiting_for_input = False
        settings.hide_top_menu = False
        settings.hide_submenu = False
        settings.hide_main_menu = False
        settings.hide_footer = False
        self.line = 0
        self.skip = False
        self.holotape_screen.cursor = (0, 0)

        if self.holotape_waveform:
            print("Clearing waveform")
            self.holotape_waveform_image.fill((0, 0, 0))
            pygame.mixer.music.stop()
            self.audio_file = None
            self.holotape_waveform = None
            pygame.mixer.music.set_endevent(settings.EVENTS['SONG_END'])
            pygame.event.post(pygame.event.Event(settings.EVENTS['SONG_END']))

        print("Clear Holotape")
        self.image.fill((0, 0, 0))

    def handle_event(self, event):
        if event.type == settings.EVENTS['HOLOTAPE_END']:
            if self.holotape_waveform:
                print("End of Audio Holotape")
                self.holotape_waveform = None
                self.holotape_image.fill((0, 0, 0))
                self.write_display(self.previous_page, True)
            if self.saved_song:
                # pygame.event.post(pygame.event.Event(settings.EVENTS['SONG_END']))
                # print("Resuming song", self.saved_song, "at position", self.saved_song_pos)
                pygame.mixer.music.load(self.saved_song)
                try:
                    pygame.mixer.music.play(0, self.saved_song_pos)
                except:
                    pygame.mixer.music.play(0, 0)
                self.saved_song = None
                self.saved_song_pos = None
                pygame.mixer.music.set_endevent(settings.EVENTS['SONG_END'])

        if self.waiting_for_input:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.update_cursor("Up")
                if event.key == pygame.K_DOWN:
                    self.update_cursor("Down")
                if event.key == pygame.K_RETURN:
                    self.update_cursor("Enter")
        elif not self.skip:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if settings.SOUND_ENABLED:
                        self.sfx_ok.play()
                    self.skip = True

    def fetch_page(self, holotape_data, page):
        try:
            static_text = holotape_data[3][page][0]
        except:
            static_text = None
        try:
            dynamic_text = holotape_data[3][page][1]
        except:
            dynamic_text = None
        try:
            menu = holotape_data[3][page][2]
        except:
            menu = []
        try:
            actions = holotape_data[3][page][3]
        except:
            actions = []

        return static_text, dynamic_text, menu, actions

    def strip_end_block(self, line):
        text = self.holotape_screen.getchars((0, self.line, self.max_chars, 1))
        text = str(text[0])
        text = text.rstrip()
        text = text.rstrip("▯")
        return text

    def draw_holotape_screen(self):
        self.line = self.holotape_screen.cursory
        self.holotape_screen.erase((0,0,self.max_chars,self.max_lines))

        if self.alive():
            if not self.skip:
                self.crawling = True
                # Draw static text
                if self.static_text_index < len(self.static_text):
                    # print("Drawing static_text", self.static_text)
                    if not self.page:  # Draw static text slowly on first screen only
                        self.holotape_screen.write(self.static_text[self.static_text_index])
                        self.holotape_screen.putchar("▯", self.holotape_screen.cursorx, self.holotape_screen.cursory)
                        self.static_text_index += 1
                    else:
                        self.holotape_screen.write(self.static_text, 0, 0)
                        self.static_text_index = 1000

                # Draw dynamic text
                elif self.dynamic_text and self.dynamic_text_index < len(self.dynamic_text):
                    # print("Drawing dynamic_text", self.dynamic_text)
                    text = str(self.dynamic_text[self.dynamic_text_index])
                    self.holotape_screen.write(self.dynamic_text[self.dynamic_text_index])
                    self.holotape_screen.putchar("▯", self.holotape_screen.cursorx, self.holotape_screen.cursory)
                    self.dynamic_text_index += 1
                    self.menu_start = self.holotape_screen.cursory

                # Draw menu
                elif self.menu and self.menu_index < len(self.menu):
                    if self.menu_text_index < len(self.menu[self.menu_index]):
                        self.holotape_screen.write(self.menu[self.menu_index][self.menu_text_index])
                        self.holotape_screen.putchar("▯", self.holotape_screen.cursorx, self.holotape_screen.cursory)
                        self.menu_text_index += 1
                    else:
                        self.menu_text_index = 0
                        self.menu_index += 1
                        self.holotape_screen.cursory += 1
                        self.holotape_screen.cursorx = 0
                elif self.menu and self.menu_index == len(self.menu):
                    self.menu_text_index = 0
                    self.menu_end = self.holotape_screen.cursory - 1
                    self.menu_index += 1
                    self.skip = True

            if self.line != self.holotape_screen.cursory:
                text = self.strip_end_block(self.line)
                self.holotape_screen.putchars(text + " ", 0, self.line)

            # Skip and just draw everything at once
            if self.skip:
                self.crawling = False
                print("Skip text crawl", self.skip)
                self.holotape_screen.fill(" ")
                self.holotape_screen.write(self.static_text, 0, 0)
                if self.dynamic_text:
                    self.holotape_screen.write(self.dynamic_text, 0, self.holotape_screen.cursory)
                if self.menu:
                    self.menu_start = self.holotape_screen.cursory
                    for each in self.menu:
                        self.holotape_screen.write(each, 0, self.holotape_screen.cursory)
                        self.menu_end = self.holotape_screen.cursory
                        self.holotape_screen.cursory += 1
                    self.holotape_screen.reversecolors((0, self.menu_start, self.max_chars, 1))
                    self.holotape_screen.cursorx = 0
                    self.holotape_screen.cursory = self.menu_start
                    self.cursor_x = self.holotape_screen.cursorx
                    self.cursor_y = self.holotape_screen.cursory
                self.waiting_for_input = True
                self.skip = False

            # Play sound on each action
            if settings.SOUND_ENABLED:
                self.sfx_text.play()

    def render(self, *args, **kwargs):
        super(HolotapeDisplay, self).render(self, *args, **kwargs)
        # self.current_time = time.time()
        print ("Rendering Holotape")
    #
    #     if not self.debug_time:
    #         self.debug_time = 0
    #
    #     time_past = time.time() - self.debug_time
    #     if time_past:
    #         max_fps = int(1 / time_past)
    #         print("Holotape render took:", time_past, "max fps:", max_fps)
    #
    #     debug_time = time.time()
    #
    #     if self.alive():
    #         if (self.current_time - self.prev_time) >= settings.fps_rate:
    #                 self.prev_time = self.current_time
    #                 print("Should be showing holotape", self.label)
    #         #
    #         #     self.image.fill((128,128,0))
    #         #
    #         #
    #         #     if not self.waiting_for_input:
    #         #         self.draw_holotape_screen()
    #         #     else:
    #         #         # Blink cursor at the bottom
    #         #         if self.current_time - self.prev_cursor_time >= self.cursor_time:
    #         #             self.prev_cursor_time = self.current_time
    #         #             for char in range(self.max_chars):
    #         #                 self.holotape_screen.putchar(' ', char, self.max_lines)
    #         #             self.holotape_screen.putchar(">", 0, self.max_lines)
    #         #             if self.console_text:
    #         #                 self.holotape_screen.putchars(self.console_text, 2, self.max_lines)
    #         #             else:
    #         #                 if self.blink:
    #         #                     self.holotape_screen.putchar(' ', 2, self.max_lines)
    #         #                     self.blink = False
    #         #                 else:
    #         #                     self.holotape_screen.putchar('▯', 2, self.max_lines)
    #         #                     self.blink = True
    #         #     self.holotape_screen.update()
    #         #     self.image.blit(self.holotape_image, (0, 0))
    #         #
    #         # if self.holotape_waveform:
    #         #     self.console_text = "Playing Holotape Audio..."
    #         #     self.draw_grid()
    #         #     self.render_holotape_waveform()
    #         #     self.image.blit(self.grid, (225, 230))
    #         #     self.image.blit(self.holotape_waveform_image, (225, 230))
    #         #     if not pygame.mixer.music.get_busy():
    #         #         pygame.draw.line(self.holotape_waveform_image, settings.bright,
    #         #                          [0, self.holotape_waveform_height / 2 + 10],
    #         #                          [self.holotape_waveform_width, self.holotape_waveform_height / 2 + 10], 2)
    #         # else:
    #         #     self.holotape_waveform_image.fill((0, 0, 0))
    #         #     self.grid.fill((0, 0, 0))
    #         #     self.console_text = None
    #
    # #

    def draw_grid(self):
        self.grid.fill((0, 0, 0))
        long_line = 14
        long_lines = 10
        short_line = 9
        short_lines = long_lines * 3
        line_start = 0
        bottom = self.grid.get_rect().bottom
        right = self.grid.get_rect().right

        pygame.draw.lines(self.grid, settings.light, False, [(0, 268), (268, 268), (268, 0)], 3)

        line_x = int(self.grid.get_rect().height / long_lines)
        while long_lines >= 1:
            line_start += line_x
            pygame.draw.line(self.grid, settings.light, (line_start, bottom), (line_start, bottom - long_line), 2)
            pygame.draw.line(self.grid, settings.light, (right, line_start), (right - long_line, line_start), 2)
            long_lines -= 1

        line_start = 0
        line_x = int(self.grid.get_rect().height / short_lines)
        while short_lines > 2:
            line_start += line_x
            pygame.draw.line(self.grid, settings.light, (line_start, bottom), (line_start, bottom - short_line), 2)
            pygame.draw.line(self.grid, settings.light, (right, line_start), (right - short_line, line_start), 2)
            short_lines -= 1

    def expand(self, oldvalue, oldmin, oldmax, newmin, newmax):
        oldRange = oldmax - oldmin
        newRange = newmax - newmin
        newvalue = ((oldvalue - oldmin) * newRange / oldRange) + newmin
        return newvalue

    def load_audio_file(self, file):
        if file and file.endswith(".ogg"):
            print("Loading holotape page")
            self.write_display(len(self.holotape_data[3]) - 1, True)
            self.audio_file = file
            print("Generating waveform for", self.audio_file)
            self.sound_object = pygame.mixer.Sound(self.audio_file)  # Load song into memory for waveform gen

            if settings.CURRENT_SONG:
                # print("Saving song", settings.CURRENT_SONG, "at position", pygame.mixer.music.get_pos())
                self.saved_song = settings.CURRENT_SONG
                self.saved_song_pos = pygame.mixer.music.get_pos()
                pygame.mixer.music.pause()

            pygame.mixer.music.load(self.audio_file)  # Load for streaming playback
            self.audio_file_length = self.sound_object.get_length()
            amplitude = pygame.sndarray.array(self.sound_object)  # Load the sound file
            amplitude = amplitude.flatten()  # Load the sound file)
            amplitude = amplitude[::settings.frame_skip]
            amplitude = amplitude.astype('float64')
            amplitude = (self.holotape_waveform_height * (amplitude - np.min(amplitude)) / np.ptp(amplitude)).astype(
                int)
            self.holotape_waveform = [int(self.holotape_waveform_height / 2)] * self.holotape_waveform_height + list(
                amplitude + 27)
            self.holotape_waveform_length = len(self.holotape_waveform)
            pygame.mixer.music.set_endevent(settings.EVENTS['HOLOTAPE_END'])
            pygame.mixer.music.play()

    def render_holotape_waveform(self):
        self.current_time = time.time()
        self.delta_time = self.current_time - self.prev_waveform_time
        if self.delta_time >= self.holotape_waveform_animation_time:
            file_pos = self.holotape_waveform_length
            self.prev_waveform_time = self.current_time
            self.holotape_waveform_image.fill((0, 0, 0))
            length = int(self.audio_file_length * 1000)
            if pygame.mixer.music.get_busy():
                file_pos = pygame.mixer.music.get_pos()

            self.index = int(
                self.expand(file_pos, 0, length, 0, self.holotape_waveform_length))

            if self.index < self.holotape_waveform_length and pygame.mixer.music.get_busy():
                prev_x, prev_y = 0, self.holotape_waveform[self.index]
                for x, y in enumerate(
                        self.holotape_waveform[self.index + 1:self.index + 1 + self.holotape_waveform_width][::1]):
                    pygame.draw.line(self.holotape_waveform_image, settings.bright, [prev_x, prev_y], [x, y], 2)
                    prev_x, prev_y = x, y
                    # Credit to https://github.com/prtx/Music-Visualizer-in-Python/blob/master/music_visualizer.py

    def update_cursor(self, button=None):

        if button == "Down":
            self.line = self.cursor_y
            self.cursor_y = self.cursor_y + 1
            print("Down")
        elif button == "Up":
            self.line = self.cursor_y
            self.cursor_y = self.cursor_y - 1
            print("Up")

        if button == "Down" or button == "Up":
            # Constrain the position to selectable areas
            if self.cursor_y < self.menu_start:
                self.cursor_y = self.menu_start
                self.cursor_x = 0
            elif self.cursor_y > self.menu_end:
                self.cursor_y = self.menu_end
                self.cursor_x = 0

            if self.cursor_y != self.line:
                if settings.SOUND_ENABLED:
                    self.sfx_dial_move.play()
                self.holotape_screen.cursor = (0, self.cursor_y)
                self.holotape_screen.reversecolors((0, self.line, self.max_chars, 1))
                self.holotape_screen.reversecolors((0, self.cursor_y, self.max_chars, 1))
                # print("prev_y = ", self.prev_y, "cursor_y =", self.cursor_y, "menu_start=", self.menu_start, "menu_end = ",
                #       self.menu_end)

        elif button == "Enter":
            print("Return")
            if settings.SOUND_ENABLED:
                self.sfx_ok.play()
            if self.menu and self.actions:
                if len(self.actions) > 1:
                    menu_selection = int(
                        self.expand(self.cursor_y, self.menu_start, self.menu_end, 0, len(self.menu) - 1))
                else:
                    menu_selection = 0

                action = self.actions[menu_selection]
                # print("Action=", action, "Actions =", self.actions)

                if str.isdigit(action):
                    action = int(action)
                    self.clear_display()
                    # print("Jumping to page", action)
                    self.write_display(action)
                else:
                    if action.endswith(".ogg"):
                        print("Found audio file:", action)
                        self.load_audio_file("holotapes/" + self.directory + "/" + action)
                    elif action == "Exit":
                        settings.hide_top_menu = False
                        settings.hide_submenu = False
                        settings.hide_main_menu = False
                        settings.hide_footer = False
                        self.clear_display()
                    elif action == "Previous":
                        # print("Going to previous page", self.page, self.previous_page)
                        if self.page > 0:
                            self.page = self.previous_page
                            self.clear_display()
                            self.write_display(self.page, True)
                            print("Previous page")
                    elif action == "Pause":
                        print("Pausing/Resuming Holotape", self.page, self.previous_page)
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                    else:
                        settings.hide_top_menu = False
                        settings.hide_submenu = False
                        settings.hide_main_menu = False
                        settings.hide_footer = False
                        self.clear_display()
                        print("Exiting to main menu")
            else:
                settings.hide_top_menu = False
                settings.hide_submenu = False
                settings.hide_main_menu = False
                settings.hide_footer = False
                self.clear_display()
                print("Going back to main menu")

        return self.cursor_y, self.cursor_x

    def __le__(self, other):
        if type(other) is not HolotapeDisplay:
            return 0
        else:
            return self.label <= other.label

    def __ge__(self, other):
        if type(other) is not HolotapeDisplay:
            return 0
        else:
            return self.label >= other.label


class HolotapeClass(HolotapeDisplay):
    def __init__(self, holotape_name, holotape_data, *args, **kwargs):
        super(HolotapeClass, self).__init__(self, *args, **kwargs)
        # holotapes_data = [holotape_name, folder_name, holotape_type, static_text, dynamic_text, menu, action]
        self.label = holotape_name
        self.directory = holotape_data[1]
        self.holotape_type = holotape_data[2]
        holotape_display_page = ['Welcome to ROBCO Industries (TM) Termlink\\n\\n', 'Holotape Audio\\n\\n', [
            '[< Back]', '[Play / Pause]'], ['Previous', 'Pause']]
        holotape_data[3].append(holotape_display_page)

        self.holotape_data = holotape_data


class Health(game.Entity):

    def __init__(self):
        super(Health, self).__init__()

        self.image = pygame.Surface((settings.WIDTH, settings.HEIGHT - 180))
        self.image.fill((0, 0, 0))
        #
        # # Bottom Boxes
        # pygame.draw.rect(self.image, settings.dim, (0, 501, 166, 38)) #Hit point background
        # pygame.draw.rect(self.image, settings.dim, (170, 501, 370, 38)) #Level bar background
        # pygame.draw.lines(self.image, settings.mid,True,[(282,515),(529,515),(529,529),(282,529)], 3) #Level bar surround
        # pygame.draw.rect(self.image, settings.bright, (285, 517, 179, 11)) #Level bar fill
        # pygame.draw.rect(self.image, settings.dim, (544, 501, 176, 38)) #Actiion background

        # Middle Boxes
        pygame.draw.rect(self.image, settings.dim, (203, 358, 64, 62))  # Gun box
        pygame.draw.rect(self.image, settings.dim, (273, 358, 38, 62))  # Ammo box
        pygame.draw.rect(self.image, settings.dim, (328, 358, 64, 62))  # Helmet box
        pygame.draw.rect(self.image, settings.dim, (398, 358, 38, 62))  # Armor box
        pygame.draw.rect(self.image, settings.dim, (440, 358, 38, 62))  # Energy box
        pygame.draw.rect(self.image, settings.dim, (483, 358, 38, 62))  # Radiation box

        # Icons
        self.image.blit(pygame.image.load('images/stats/gun.png').convert_alpha(), (210, 374))
        self.image.blit(pygame.image.load('images/stats/reticle.png').convert_alpha(), (284, 363))
        self.image.blit(pygame.image.load('images/stats/helmet.png').convert_alpha(), (338, 373))
        self.image.blit(pygame.image.load('images/stats/shield.png').convert_alpha(), (410, 362))
        self.image.blit(pygame.image.load('images/stats/bolt.png').convert_alpha(), (453, 362))
        self.image.blit(pygame.image.load('images/stats/radiation.png').convert_alpha(), (491, 363))

        # Health Bars
        pygame.draw.line(self.image, settings.bright, (344, 32), (379, 32), 9)
        pygame.draw.line(self.image, settings.bright, (465, 134), (500, 134), 9)
        pygame.draw.line(self.image, settings.bright, (465, 266), (500, 266), 9)
        pygame.draw.line(self.image, settings.bright, (344, 318), (379, 318), 9)
        pygame.draw.line(self.image, settings.bright, (216, 266), (251, 266), 9)
        pygame.draw.line(self.image, settings.bright, (216, 134), (251, 134), 9)

        # Stat text
        settings.FreeRobotoB[24].render_to(self.image, (281, 395), "18", settings.bright)  # Ammo count
        settings.FreeRobotoB[24].render_to(self.image, (406, 395), "10", settings.bright)  # Armor count
        settings.FreeRobotoB[24].render_to(self.image, (447, 395), "20", settings.bright)  # Energy count
        settings.FreeRobotoB[24].render_to(self.image, (490, 395), "10", settings.bright)  # Rad count
        #
        # # Bottom text
        # settings.FreeRobotoB[30].render_to(self.image, (7, 509), "HP 115/115", settings.bright)
        # settings.FreeRobotoB[24].render_to(self.image, (188, 513), "LEVEL 66", settings.bright)
        # settings.FreeRobotoB[30].render_to(self.image, (602, 509), "AP 90/90", settings.bright)

        # User name
        settings.FreeRobotoB[24].render_to(self.image, (301, 448), settings.name, settings.bright)

    # def handle_resume(self):
    #     pass
    #     super(Module, self).handle_resume()
