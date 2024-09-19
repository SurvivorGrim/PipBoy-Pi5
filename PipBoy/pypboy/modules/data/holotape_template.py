# import configparser
# import glob
# from collections import deque
#
# import numpy as np
#
# import pypboy
# import pygame
# import game
# import settings
# import pygcurse
# import locale
# import os
# import time
# import xml.etree.ElementTree as ET
#
# locale.setlocale(locale.LC_ALL, '')
# code = locale.getpreferredencoding()
#
#
# class Module(pypboy.SubModule):
#     label = "HOLOTAPES"
#
#     def __init__(self, *args, **kwargs):
#         super(Module, self).__init__(*args, **kwargs)
#
#         self.holotape_folder = 'holotapes/'
#         self.holotapes = []
#         self.main_menu = []
#         self.holotapes_data_set = []
#         self.holotapes_data_set = self.get_data()
#
#         for holotapes_data in self.holotapes_data_set:
#             # holotapes_data = [holotape_name, folder_name, static_text, dynamic_text, menu, action]
#             holotape_name = holotapes_data[0]
#             self.main_menu.append([holotape_name])
#             self.holotapes.append(HolotapeClass(holotape_name, holotapes_data))
#
#         for tape in self.holotapes:
#             self.add(tape)
#         self.active_holotape = None
#         settings.holotape = self
#
#         holotapeCallbacks = []
#         for i, holotape in enumerate(self.holotapes):
#             holotapeCallbacks.append(lambda i=i: self.select_holotape(i))
#
#         self.topmenu = pypboy.ui.TopMenu()
#         self.topmenu.label = "DATA"
#         self.topmenu.title = settings.MODULE_TEXT
#         self.add(self.topmenu)
#
#         self.menu = pypboy.ui.Menu(self.main_menu, holotapeCallbacks, 0)
#         self.menu.rect[0] = settings.menu_x
#         self.menu.rect[1] = settings.menu_y
#         self.add(self.menu)
#
#         settings.FOOTER_TIME[2] = ""
#         self.footer = pypboy.ui.Footer(settings.FOOTER_TIME)
#         self.footer.rect[0] = settings.footer_x
#         self.footer.rect[1] = settings.footer_y
#         self.add(self.footer)
#
#         self.prev_static_text = None
#
#     def select_holotape(self, holotape):
#         if hasattr(self, 'active_holotape') and self.active_holotape:
#             self.active_holotape.new_selection = True
#         self.active_holotape = self.holotapes[holotape]
#         if self.active_holotape.holotape_type:
#             settings.FOOTER_TIME[2] = self.active_holotape.holotape_type
#
#     def handle_event(self, event):
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_RETURN:
#                 if not self.active_holotape.screen:
#                     settings.hide_top_menu = True
#                     settings.hide_submenu = True
#                     settings.hide_main_menu = True
#                     settings.hide_footer = True
#                     self.active_holotape.write_display()
#                     print("Enter pressed")
#             elif event.key == pygame.K_BACKSPACE:
#                 settings.hide_top_menu = False
#                 settings.hide_submenu = False
#                 settings.hide_main_menu = False
#                 settings.hide_footer = False
#                 self.active_holotape.clear_display()
#                 print("Backspace pressed")
#         if self.active_holotape.screen:
#             self.active_holotape.handle_event(event)
#
#     def handle_resume(self):
#         if self.paused == True:
#             self.paused = False
#             settings.hide_top_menu = False
#             settings.hide_submenu = False
#             settings.hide_main_menu = False
#             settings.hide_footer = False
#             self.active_holotape.clear_display()
#             # print("Resumed Holotape", self)
#             # self.holotape.handle_resume()
#             super(Module, self).handle_resume()
#
#     def handle_pause(self):
#         # print("Holotape paused")
#         self.active_holotape.clear_display()
#
#     def get_data(self):
#
#         # Get list of folders
#         folders = []
#         holotapes_data = []
#         holotape_name = None
#         holotape_type = None
#         folder_name = None
#
#         for f in sorted(os.listdir(self.holotape_folder)):
#             if not f.endswith("/"):
#                 folders.append(self.holotape_folder + f)
#
#         for folder in folders:
#
#             folder_name = os.path.basename(folder)  # Get the folder name without the full path
#             if len(glob.glob(folder + "/holotape.xml")) == 0:
#                 print("No holotape.xml file in:", folder)
#                 continue
#             menu_file = ("./" + folder + "/" + "holotape.xml")
#
#             try:
#                 holotape_xml = ET.parse(menu_file).getroot()
#
#                 for element in holotape_xml.iter("title"):
#                     holotape_name = element.text
#                 for element in holotape_xml.iter("type"):
#                     holotape_type = element.text
#                 for page in holotape_xml.iter("page"):
#                     static_text = None
#                     dynamic_text = None
#
#                     try:
#                         static_text = page.find("static_text").text
#                         self.prev_static_text = static_text
#                     except:
#                         if self.prev_static_text:
#                             static_text = self.prev_static_text
#                         else:
#                             static_text = None
#
#                     try:
#                         dynamic_text = page.find("dynamic_text").text
#                     except:
#                         dynamic_text = None
#
#                     menu = []
#                     action = []
#                     try:
#
#                         for element in page.find("menu"):
#                             menu.append(element.text)
#                             try:
#                                 attribute = element.attrib
#                                 if attribute["page"]:
#                                     action.append(attribute["page"])
#                                 elif attribute["audio"]:
#                                     action.append(attribute["audio"])
#                             except:
#                                 action.append("0")
#                     except:
#                         # print("No menu found in:",page)
#                         menu = []
#                         action = ["Previous"]
#
#
#                     holotape_data = [holotape_name, folder_name, holotape_type, static_text, dynamic_text, menu, action]
#
#                     # print("Static text = ",static_text,"\n","dynamic_text = ",dynamic_text,"\n","menu = ",menu,"\n","action=",action)
#                     # print("Holotape name = ", holotape_name, "Holotape type =", holotape_type, "HOlotape folder = ",folder)
#
#             except Exception as e:
#                 holotape_name = folder_name
#                 print(str(e), ' could not read xml file in',folder_name)
#
#             holotapes_data.append(holotape_data)
#
#         return holotapes_data
#
# def word_wrap(surf, text, font):
#     text = str(text)
#     font.origin = True
#     words = text.split()
#     width, height = surf.get_size()
#     line_spacing = font.get_sized_height()
#     x, y = 0, line_spacing
#     for word in words:
#         word = word + str("  ")
#         bounds = font.get_rect(word)
#         if x + bounds.width + bounds.x >= width:
#             x, y = 0, y + line_spacing
#         # if x + bounds.width + bounds.x >= width:
#         #    raise ValueError("word too wide for the surface")
#         # if y + bounds.height - bounds.y >= height:
#         #    raise ValueError("text to long for the surface")
#         font.render_to(surf, (x, y), word, settings.bright, None, 1)
#         x += bounds.width
#     return x, y
#
# class HolotapeDisplay(game.Entity):
#     def __init__(self, *args, **kwargs):
#         super(HolotapeDisplay, self).__init__((settings.WIDTH, settings.HEIGHT - 100), *args, **kwargs)
#
#         self.selection_index = 0
#         self.highlightable_indices = []
#         self.button_pressed = 0
#         self.offset = 0
#         self.cursor_x = 0
#         self.cursor_y = 0
#         self.prev_x = 0
#         self.prev_y = 0
#
#         self.holotape_image = pygame.Surface((settings.WIDTH - 10, settings.HEIGHT - 100))
#         self.holotape_image.fill((0, 0, 0))
#         self.rect[0] = 11
#         self.rect[1] = 51
#
#         self.animation_time = 1 / settings.terminal_speed
#         self.prev_time = 0
#         self.current_time = 0
#         self.button = None
#         self.cursor_time = 1  # Cursor blink speed
#         self.prev_cursor_time = 0
#         self.char_index = 0
#         self.menu_index = 0
#         self.prev_line = 0
#         self.blink = False
#         self.screen = None
#         self.static_text_index = 0
#         self.dynamic_text_index = 0
#         self.menu_text_index = 0
#         self.menu_start = 0
#         self.menu_end = 0
#         self.line = 0
#         self.waiting_for_input = False
#
#         # Audio holotape related:
#         self.holotape_waveform_width, self.holotape_waveform_height = settings.WIDTH - 20, settings.HEIGHT - 100
#         self.holotape_waveform_image = pygame.Surface((self.holotape_waveform_width, self.holotape_waveform_height))
#         self.holotape_waveform_animation_time = 1 / settings.waveform_fps  # 25 fps
#         self.prev_time = 0
#         self.index = 0
#         self.prev_song = None
#         self.s_time = 0
#         self.current_time = 0
#         self.delta_time = 0
#         self.holotape_waveform = None
#         self.holotape_waveform_length = None
#         self.audio_file = None
#         self.audio_file_length = 0
#         self.sound_object = None
#         self.max_length = 0
#
#         if settings.SOUND_ENABLED:
#             self.dial_move_sfx = pygame.mixer.Sound('./sounds/pipboy/RotaryVertical/UI_PipBoy_RotaryVertical_01.ogg')
#             self.dial_move_sfx.set_volume(settings.VOLUME)
#             self.text_snd = pygame.mixer.Sound('./sounds/terminal/UI_Terminal_CharScroll_LP.ogg')
#             self.text_snd.set_volume(settings.VOLUME)
#
#         self.font = settings.FreeTechMono[22]
#         # char_width, char_height = self.font.size("X")
#         # self.max_chars = int(settings.WIDTH / char_width) - 6
#         # self.max_lines = int((settings.HEIGHT - 100) / char_height) - 1
#
#     def write_display(self):
#
#         settings.hide_top_menu = True
#         settings.hide_submenu = True
#         settings.hide_main_menu = True
#         settings.hide_footer = True
#
#         # Create the pygcurse surface
#         # self.screen = pygcurse.PygcurseSurface(self.max_chars, self.max_lines + 1, self.font,
#         #                                        settings.bright, settings.black, self.holotape_image, True, 1000)
#         # self.screen._autoupdate = False
#         # self.screen._autodisplayupdate = False
#         #
#         # self.screen.cursor = (0, 0)
#         self.static_text_index = 0
#         self.dynamic_text_index = 0
#         self.menu_text_index = 0
#         self.char_index = 0
#         # self.screen.pushcursor()
#
#     def clear_display(self):
#         self.holotape_image.fill((0, 0, 0))
#         self.screen = None
#         self.static_text_index = 0
#         self.dynamic_text_index = 0
#         self.menu_text_index = 0
#         self.char_index = 0
#         self.waiting_for_input = False
#         settings.hide_top_menu = False
#         settings.hide_submenu = False
#         settings.hide_main_menu = False
#         settings.hide_footer = False
#
#         if self.holotape_waveform:
#             self.holotape_waveform_image.fill((0, 0, 0))
#             pygame.mixer.music.stop()
#             self.audio_file = None
#             self.holotape_waveform = None
#
#         print("Clear Holotape")
#         self.image.fill((0,0,0))
#
#     def handle_event(self, event):
#         if self.waiting_for_input:
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_UP:
#                     self.update_cursor("Up")
#                 if event.key == pygame.K_DOWN:
#                     self.update_cursor("Down")
#                 if event.key == pygame.K_RETURN:
#                     self.update_cursor("Enter")
#
#                     self.holotape_image.fill((0, 0, 0))
#                     self.screen = None
#                     self.static_text_index = 0
#                     self.dynamic_text_index = 0
#                     self.menu_text_index = 0
#                     self.char_index = 0
#                     self.waiting_for_input = False
#
#                     file = self.directory + self.holotape_audio[0]
#                     self.holotape_image.blit(self.holotape_waveform_image, (0, 0))
#                     self.load_audio_file(file)
#
#     def render(self, *args, **kwargs):
#         super(HolotapeDisplay, self).render(self, *args, **kwargs)
#         if self.screen:
#             self.current_time = time.time()
#             if (self.current_time - self.prev_time) >= self.animation_time:
#                 self.prev_time = self.current_time
#
#                 print ("self.static_text=", self.static_text)
#                 if self.static_text_index < len(self.static_text):
#                     pass
#
#                 if self.line >= len(self.text_array):  # Check if at the end of the paragraph
#                     self.text = self.text_array[self.line]  # Get the line of text
#
#                 word_wrap(self.image,self.static_text,self.font)
#
#                 #
#                 # # Draw static text
#                 # if self.static_text_index < len(self.static_text):
#                 #
#                 #     if self.char_index < len(self.static_text):
#                 #         # Play sound on each char
#                 #         if settings.SOUND_ENABLED:
#                 #             self.text_snd.play()
#                 #
#                 #         self.screen.write(str(self.static_text[self.char_index] + '▯'), self.char_index, self.static_text_index)
#                 #         # self.screen.putchar('▯', self.char_index + 1, self.static_text_index)
#                 #         self.char_index += 1
#                 #     else:
#                 #         self.screen.putchar(' ', self.char_index, self.static_text_index)
#                 #         self.static_text_index += 1
#                 #         self.char_index = 0
#                 #         self.line = self.static_text_index
#                 #
#                 #         # Draw dynamic text
#                 # elif self.dynamic_text and self.dynamic_text_index < len(self.dynamic_text):
#                 #     text = str(self.dynamic_text[self.dynamic_text_index])
#                 #
#                 #     if self.char_index < len(text):
#                 #         # Play sound on each char
#                 #         if settings.SOUND_ENABLED:
#                 #             self.text_snd.play()
#                 #         self.screen.putchars(str(text[self.char_index] + '▯'), self.char_index, self.line)
#                 #         self.char_index += 1
#                 #     else:
#                 #         self.screen.putchar(' ', self.char_index, self.line)
#                 #         self.dynamic_text_index += 1
#                 #         self.line += 1
#                 #         self.char_index = 0
#                 #         self.menu_start = self.line
#                 #         for x in range(self.max_chars):
#                 #             self.screen.putchars(" ", x, self.line)
#                 #
#                 # # Draw menu
#                 # elif self.holotape_menu and self.menu_text_index < len(self.holotape_menu):
#                 #     text = str(self.holotape_menu[self.menu_text_index])
#                 #
#                 #     if self.char_index < len(text):
#                 #         # Play sound on each char
#                 #         if settings.SOUND_ENABLED:
#                 #             self.text_snd.play()
#                 #         self.screen.putchars(str(text[self.char_index] + '▯'), self.char_index, self.line)
#                 #         self.char_index += 1
#                 #     else:
#                 #         self.screen.putchar(' ', self.char_index, self.line)
#                 #         self.menu_text_index += 1
#                 #         self.char_index = 0
#                 #         self.menu_end = self.line
#                 #         self.line += 1
#                 # elif not self.waiting_for_input:
#                 #     self.screen.cursorx = 0
#                 #     self.screen.cursory = self.menu_start
#                 #     self.cursor_x = self.screen.cursorx
#                 #     self.cursor_y = self.screen.cursory
#                 #     self.waiting_for_input = True
#                 #     self.screen.reversecolors((0, self.menu_start, self.max_chars, 1))
#                 #     self.prev_y = 99
#                 # else:
#                 #     if self.current_time - self.prev_cursor_time >= self.cursor_time:
#                 #         self.prev_cursor_time = self.current_time
#                 #         self.screen.putchar(">", 0, self.max_lines)
#                 #         if self.screen.getchar(2, self.max_lines) == ' ':
#                 #             self.screen.putchar('▯', 2, self.max_lines)
#                 #         else:
#                 #             self.screen.putchar(' ', 2, self.max_lines)
#                 #
#                 # # self.screen.putchars(str(self.current_time), 0, self.max_lines - 2)
#                 #
#                 # self.screen.update()
#                 # self.image.blit(self.holotape_image, (0, 0))
#
#         if self.holotape_waveform:
#             self.render_holotape_waveform()
#         else:
#             self.holotape_waveform_image.fill((0, 0, 0))
#
#     def expand(self, oldvalue, oldmin, oldmax, newmin, newmax):
#         oldRange = oldmax - oldmin
#         newRange = newmax - newmin
#         newvalue = ((oldvalue - oldmin) * newRange / oldRange) + newmin
#         return newvalue
#
#     def load_audio_file(self, file):
#         if file and file.endswith(".ogg"):
#             self.audio_file = file
#             print("Generating waveform for", self.audio_file)
#             self.sound_object = pygame.mixer.Sound(self.audio_file)  # Load song into memory for waveform
#             self.audio_file_length = self.sound_object.get_length()
#             amplitude = pygame.sndarray.array(self.sound_object)  # Load the sound file
#             amplitude = amplitude.flatten()  # Load the sound file)
#             amplitude = amplitude[::settings.frame_skip]
#             amplitude = amplitude.astype('float64')
#             amplitude = (self.holotape_waveform_height * (amplitude - np.min(amplitude)) / np.ptp(amplitude)).astype(int)
#             self.holotape_waveform = [int(self.holotape_waveform_height / 2)] * self.holotape_waveform_height + list(amplitude)
#             self.holotape_waveform_length = len(self.holotape_waveform)
#             pygame.mixer.music.load(self.audio_file)
#             pygame.mixer.music.play()
#
#     def render_holotape_waveform(self):
#         self.current_time = time.time()
#         self.delta_time = self.current_time - self.prev_time
#         if self.delta_time >= self.holotape_waveform_animation_time:
#             self.prev_time = self.current_time
#             if self.holotape_waveform:
#                 self.holotape_waveform_image.fill((0, 0, 0))
#                 file_pos = pygame.mixer.music.get_pos()
#                 length = int(self.audio_file_length * 1000)
#                 self.index = int(
#                     self.expand(file_pos, 0, length, 0, self.holotape_waveform_length))
#
#                 if self.index >= self.holotape_waveform_length - 1:
#                     # print("self.index out of range =", self.index, self.holotape_waveform_length,"audio_file_length = ",self.audio_file_length)
#                     self.holotape_waveform_image.fill((0, 0, 0))
#                     self.index = 0
#                     self.audio_file = None
#                     self.holotape_waveform = None
#                     self.write_display()
#
#                 if self.holotape_waveform:
#                     prev_x, prev_y = 0, self.holotape_waveform[self.index]
#                     for x, y in enumerate(self.holotape_waveform[self.index + 1:self.index + 1 + self.holotape_waveform_width][::1]):
#                         pygame.draw.line(self.holotape_waveform_image, settings.bright, [prev_x, prev_y], [x, y], 2)
#                         prev_x, prev_y = x, y
#                         # Credit to https://github.com/prtx/Music-Visualizer-in-Python/blob/master/music_visualizer.py
#             else:
#                 self.holotape_waveform_image.fill((0, 0, 0))
#                 self.audio_file = None
#
#             self.holotape_image.blit(self.holotape_waveform_image, (0, 0))
#             self.image.blit(self.holotape_image, (0, 0))
#
#     def update_cursor(self, action=None):
#
#         if action == "Down":
#             self.prev_y = self.cursor_y
#             self.cursor_y = self.cursor_y + 1
#             print("Down")
#             if settings.SOUND_ENABLED:
#                 self.dial_move_sfx.play()
#         elif action == "Up":
#             self.prev_y = self.cursor_y
#             self.cursor_y = self.cursor_y - 1
#             print("Up")
#             if settings.SOUND_ENABLED:
#                 self.dial_move_sfx.play()
#         elif action == "Enter":
#             print("Return")
#             if settings.SOUND_ENABLED:
#                 self.dial_move_sfx.play()
#
#         # Constrain the position to selectable areas
#         if self.cursor_y < self.menu_start:
#             self.cursor_y = self.menu_start
#             self.cursor_x = 0
#         elif self.cursor_y > self.menu_end:
#             self.cursor_y = self.menu_end
#             self.cursor_x = 0
#
#         if self.cursor_y != self.prev_y:
#             self.screen.cursor = (0, self.cursor_y)
#             self.screen.reversecolors((0, self.prev_y, self.max_chars, 1))
#             self.screen.reversecolors((0, self.cursor_y, self.max_chars, 1))
#             # print("prev_y = ", self.prev_y, "cursor_y =", self.cursor_y, "menu_start=", self.menu_start, "menu_end = ",
#             #       self.menu_end)
#
#         return self.cursor_y, self.cursor_x
#
#     def __le__(self, other):
#         if type(other) is not HolotapeDisplay:
#             return 0
#         else:
#             return self.label <= other.label
#
#     def __ge__(self, other):
#         if type(other) is not HolotapeDisplay:
#             return 0
#         else:
#             return self.label >= other.label
#
#
# class HolotapeClass(HolotapeDisplay):
#     def __init__(self, holotape_name, holotape_data, *args, **kwargs):
#         # holotapes_data = [holotape_name, folder_name, holotape_type, static_text, dynamic_text, menu, action]
#         self.label = holotape_name
#         self.directory = holotape_data[1]
#         self.holotape_type = holotape_data[2]
#         self.static_text = holotape_data[3]
#         self.dynamic_text = holotape_data[4]
#         self.holotape_menu = holotape_data[5]
#         self.actions = holotape_data[6]
#
#
#
#         super(HolotapeClass, self).__init__(self, *args, **kwargs)
