import glob
import os
import xml.etree.ElementTree as ET
import numpy as np
import pygame
import game
import pypboy
import settings


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
            holotapes_data = ["holotape_name", "folder_name", "static_text", "dynamic_text", "menu", "action", "image"]
            holotape_name = holotapes_data[0]
            image = settings.holotape_generic
            self.main_menu.append([holotape_name, "", image])
            self.holotapes.append(HolotapeClass(holotape_name, holotapes_data))

        # for tape in self.holotapes:
        #     pass
            # self.add(tape)
        # self.active_holotape = None
        # settings.holotape = self2

        holotapeCallbacks = []
        for i, holotape in enumerate(self.holotapes):
            holotapeCallbacks.append(lambda i=i: self.select_holotape(i))

        self.topmenu = pypboy.ui.TopMenu()
        self.add(self.topmenu)
        self.topmenu.label = "DATA"
        self.topmenu.title = settings.MODULE_TEXT

        settings.FOOTER_TIME[2] = ""
        self.footer = pypboy.ui.Footer(settings.FOOTER_TIME)
        self.footer.rect[0] = settings.footer_x
        self.footer.rect[1] = settings.footer_y
        self.add(self.footer)

        self.menu = pypboy.ui.Menu(self.main_menu, holotapeCallbacks, 0)
        self.menu.rect[0] = settings.menu_x
        self.menu.rect[1] = settings.menu_y
        self.add(self.menu)

        self.prev_static_text = None

    def select_holotape(self, holotape):
        if hasattr(self, 'active_holotape') and self.active_holotape:
            print("Removing:",self.active_holotape)
            self.active_holotape.selected = True
            self.remove(self.active_holotape)
        print("Adding:",holotape)
        self.add(holotape)
        self.active_holotape = self.holotapes[holotape]

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
        self.screen = None
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
        self.active = False
        self.selected = False
        self.page = 0
        self.previous_page = 0
        self.skip = False
        self.console_text = None
        self.saved_song = None
        self.saved_song_pos = None

        self.font = settings.TechMono[25]
        self.char_width, self.char_height = self.font.size("X")
        self.max_chars = int(settings.WIDTH / self.char_width) - 5
        self.max_lines = int((settings.HEIGHT - 100) / self.char_height) - 1


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
        elif not self.skip and self.active:
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
        self.label = holotape_name
        self.directory = holotape_data[1]
        self.holotape_type = holotape_data[2]
        holotape_display_page = []
        holotape_display_page = 'Welcome to ROBCO Industries (TM) Termlink\\n\\n', 'Holotape Audio\\n\\n', [
            '[< Back]', '[Play / Pause]'], ['Previous', 'Pause']
        # holotape_data[3].append(holotape_display_page)

        self.holotape_data = holotape_data


