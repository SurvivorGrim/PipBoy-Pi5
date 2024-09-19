import pypboy
import settings
import pygame
import os
import imp
import glob
import time
import game
from collections import deque
import mutagen
import random
import configparser
import sys
import threading
import numpy as np

from pypboy.modules.data import entities
import pypboy.data

song = None
start_pos = 0
waveform = []
waveform_length = 0
song_length = 0
song_fileload = None

def generate_waveform():
    global waveform, waveform_length, song, song_fileload

    while True:
        if song and song.endswith(".ogg") and song_fileload and waveform == []:
            print("Generating waveform for", song)
            amplitude = pygame.sndarray.array(song_fileload)  # Load the sound file
            amplitude = amplitude.flatten()  # Load the sound file)

            # amplitude = amplitude[:, 0] + amplitude[:, 1]
            amplitude = amplitude[::settings.frame_skip]

            # scale the amplitude to fit in the frame height and translate it to height/2(central line)
            amplitude = amplitude.astype('float64')

            # Normalised [0,255] as integer: don't forget the parenthesis before astype(int)
            amplitude = (200 * (amplitude - np.min(amplitude)) / np.ptp(amplitude)).astype(int)

            waveform = [int(200 / 2)] * 200 + list(amplitude)
            waveform_length = len(waveform)
            song_fileload = None
        else:
            time.sleep(0.1)

waveform_thread = threading.Thread(target=generate_waveform)
waveform_thread.daemon = True
waveform_thread.start()

class Module(pypboy.SubModule):
    global waveform, waveform_length, song, song_fileload
    label = "hidden"

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)

        self.audiofolders = 'sounds/radio/'
        self.stations = []
        self.station_menu = []
        self.station_data = self.get_station_data()
        self.total_length = 0
        self.station_meta_data_file = None
        self.station_files = []
        self.station_lengths = []

        self.grid = Grid()
        self.grid.rect[0] = 260
        self.grid.rect[1] = 40
        self.add(self.grid)

        self.animation = Animation()
        self.animation.rect[0] = 270
        self.animation.rect[1] = 15
        self.add(self.animation)

        for station in self.station_data:
            # station_data = [station_name, folder, station_files, station_ordered, station_lengths, total_length]
            station_folder = station[1] + "/"
            station_name = station[0]
            self.station_menu.append([station_name])
            self.stations.append(RadioClass(station_name, station_folder, station))

        for station in self.stations:
            self.add(station)
        self.active_station = None
        settings.radio = self

        stationCallbacks = []
        for i, station in enumerate(self.stations):
            stationCallbacks.append(lambda i=i: self.select_station(i))
            # print ("station labels = ",stationLabels)
            # print ("station callbacks = ",stationCallbacks)

        self.topmenu = pypboy.ui.TopMenu()
        self.add(self.topmenu)
        self.topmenu.label = "RADIO"
        self.topmenu.title = settings.MODULE_TEXT

        self.menu = pypboy.ui.Menu(self.station_menu, stationCallbacks, settings.STATION)
        self.menu.rect[0] = settings.menu_x
        self.menu.rect[1] = settings.menu_y
        self.add(self.menu)
        self.menu.select(settings.STATION)

        self.footer = pypboy.ui.Footer(settings.FOOTER_RADIO)
        self.footer.rect[0] = settings.footer_x
        self.footer.rect[1] = settings.footer_y
        self.add(self.footer)

    def select_station(self, station):
        if hasattr(self, 'active_station') and self.active_station:
            self.active_station.new_selection = True
            self.active_station.stop()
        self.active_station = self.stations[station]
        settings.STATION = station
        self.active_station.play_song()

    def handle_radio_event(self, event):
        if event.type == settings.EVENTS['SONG_END']:
            if hasattr(self, 'active_station') and self.active_station:
                if self.active_station.new_selection:
                    self.active_station.new_selection = False
                else:
                    self.active_station.files.rotate(-1)
                    self.active_station.song_lengths.rotate(-1)
                    self.active_station.play_song()
                    self.active_station.new_selection = False
                    print("Song ended, Playing next song")
        if event.type == settings.EVENTS['PLAYPAUSE']:
            if hasattr(self, 'active_station') and self.active_station:
                self.active_station.pause_play()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                if hasattr(self, 'active_station') and self.active_station:
                    self.active_station.volume_up()
            elif event.key == pygame.K_PAGEDOWN:
                if hasattr(self, 'active_station') and self.active_station:
                    self.active_station.volume_down()
            elif event.key == pygame.K_END:
                if hasattr(self, 'active_station') and self.active_station:
                    self.active_station.next_song()
            elif event.key == pygame.K_HOME:
                if hasattr(self, 'active_station') and self.active_station:
                    self.active_station.prev_song()
            elif event.key == pygame.K_DELETE:
                if hasattr(self, 'active_station') and self.active_station:
                    self.active_station.randomize_station()
            elif event.key == pygame.K_INSERT:
                if hasattr(self, 'active_station') and self.active_station:
                    self.active_station.pauseplay()

    def get_station_data(self):

        # Get list of folders
        folders = []
        stations = []
        self.station_name = None
        self.station_ordered = True

        for f in sorted(os.listdir(self.audiofolders)):
            if not f.endswith("/"):
                folders.append(self.audiofolders + f)

        for folder in folders:
            config = configparser.SafeConfigParser()

            folder_name = os.path.basename(folder)  # Get the folder name without the full path
            if len(glob.glob(folder + "/*.ogg")) == 0:
                print("No .ogg files in:", folder)
                continue

            song_data = self.load_files(folder)
            self.station_files = song_data[0]
            self.station_lengths = song_data[1]
            self.total_length = sum(self.station_lengths)

            self.station_meta_data_file = ("./" + folder + "/" + "station.ini")

            try:
                assert os.path.exists(self.station_meta_data_file)
                config.read(self.station_meta_data_file, encoding=None)
            except Exception as e:
                print("Error reading the following:", str(e))

            try:
                self.station_name = config.get('metadata', 'station_name')
                self.station_ordered = eval(config.get('metadata', 'ordered'))
            except Exception as e:
                self.station_name = folder_name
                self.station_ordered = True
                print(str(e), "could not read configuration file in", folder)

            if self.station_ordered == False:
                # print("randomizing", folder)
                seed = random.random()
                random.Random(seed).shuffle(self.station_files)
                random.Random(seed).shuffle(self.station_lengths)

            station_data = self.station_name, folder, self.station_files, self.station_ordered, self.station_lengths, self.total_length
            stations.append(station_data)

        return stations

    def load_files(self, folder):
        files = []
        song_lengths = []

        for file in sorted(os.listdir(folder)):
            if file.endswith(".ogg"):
                files.append("./" + folder + "/" + file)
                song_lengths.append(mutagen.File("./" + folder + "/" + file).info.length)

        return [files, song_lengths]



class Animation(game.Entity):

    def __init__(self):
        super(Animation, self).__init__()

        self.width, self.height = 150, 150
        self.center = [self.width / 2, self.height / 2]
        self.image = pygame.Surface((self.width, self.height))
        self.animation_time = 1 / settings.waveform_fps  # 25 fps
        self.prev_time = 0
        self.index = 0
        self.prev_song = None
        self.s_time = 0
        self.current_time = 0
        self.delta_time = 0
        self.length = 0
        self.prev_song = 0
        self.max_length = 0

    def expand(self, oldvalue, oldmin, oldmax, newmin, newmax):
        oldRange = oldmax - oldmin
        newRange = newmax - newmin
        newvalue = ((oldvalue - oldmin) * newRange / oldRange) + newmin
        return newvalue

    def render(self, *args, **kwargs):
        global waveform, waveform_length, song, song_length

        self.current_time = time.time()
        self.delta_time = self.current_time - self.prev_time

        if self.delta_time >= self.animation_time:
            self.prev_time = self.current_time
            self.image.fill((0, 0, 0))

            if not song:
                pygame.draw.line(self.image, settings.bright, [0, self.height / 2], [self.width, self.height / 2], 2)
                self.prev_song = 0

            else:
                if song != self.prev_song:
                    self.prev_song = song
                    song_length = mutagen.File(song).info.length
                    self.max_length = int(song_length * 1000)

                if waveform:
                    song_time = pygame.mixer.music.get_pos()
                    self.index = int(
                        self.expand(song_time, 0, self.max_length, 0, waveform_length))

                    if self.index >= waveform_length:
                        self.index = 0

                    prev_x, prev_y = 0, waveform[self.index]
                    for x, y in enumerate(waveform[self.index + 1:self.index + 1 + self.width][::1]):
                        pygame.draw.line(self.image, settings.bright, [prev_x, prev_y], [x, y], 2)
                        prev_x, prev_y = x, y
                        # Credit to https://github.com/prtx/Music-Visualizer-in-Python/blob/master/music_visualizer.py

                elif self.index >= waveform_length - settings.waveform_rate or self.index == 0:
                    pygame.draw.line(self.image, settings.bright, [0, self.height / 2],
                                     [self.width, self.height / 2],
                                     2)
                    settings.FreeRobotoB[18].render_to(self.image, (5, 106), "Locking onto signal...", settings.dim)


class Grid(game.Entity):

    def __init__(self):
        super(Grid, self).__init__()

        self.image = pygame.Surface((210, 150))
        self.image.fill((0, 0, 0))
        long_line = 14
        long_lines = 10
        short_line = 9
        short_lines = long_lines * 3
        line_start = 0
        bottom = self.image.get_rect().bottom
        right = self.image.get_rect().right

        pygame.draw.lines(self.image, settings.light, False, [(0, 268), (268, 268), (268, 0)], 3)

        line_x = int(self.image.get_rect().height / long_lines)
        while long_lines >= 1:
            line_start += line_x
            pygame.draw.line(self.image, settings.light, (line_start, bottom), (line_start, bottom - long_line), 2)
            pygame.draw.line(self.image, settings.light, (right, line_start), (right - long_line, line_start), 2)
            long_lines -= 1

        line_start = 0
        line_x = int(self.image.get_rect().height / short_lines)
        while short_lines > 2:
            line_start += line_x
            pygame.draw.line(self.image, settings.light, (line_start, bottom), (line_start, bottom - short_line), 2)
            pygame.draw.line(self.image, settings.light, (right, line_start), (right - short_line, line_start), 2)
            short_lines -= 1


class RadioStation(game.Entity):
    STATES = {
        'stopped': 0,
        'playing': 1,
        'paused': 2
    }
    global static_sound

    def __init__(self, *args, **kwargs):
        super(RadioStation, self).__init__((10, 10), *args, **kwargs)
        self.state = self.STATES['stopped']

        self.station_length = 0
        self.filename = 0
        self.new_selection = True
        self.last_filename = None
        self.start_time = time.time()
        self.sum_of_song_lengths = 0
        self.start_pos = 0
        self.static = pygame.mixer.Sound("sounds/pipboy/Radio/UI_Pipboy_Radio_StaticBackground_LP.ogg")
        pygame.mixer.music.set_endevent(settings.EVENTS['SONG_END'])

    def play_song(self):
        global song, start_pos, waveform, song_length, waveform_length, song_fileload
        self.start_pos = 0
        if settings.SOUND_ENABLED:
            if self.files[0].endswith("Silence.ogg"):
                settings.AMPLITUDE = []
                song = None
                start_pos = 0
                waveform = []
                waveform_length = 0
                settings.FOOTER_RADIO[0] = ""
                Module.active_station = None
                Module.active_station = None
                print("Radio off")
                self.stop()
            else:
                if hasattr(self, 'last_filename') and self.last_filename:  # Support resuming
                    self.start_pos = self.last_playpos + (time.time() - self.last_playtime)
                    print("Resuming song:", self.last_filename)
                    self.filename = self.last_filename
                    self.last_filename = None

                elif self.files:
                    if self.new_selection:  # If changed stations manually
                        self.static.play()
                        song_length = self.song_lengths[0]  # length of the current song
                        self.start_pos = time.time() - self.start_time
                        # print("time based start_pos =", self.start_pos)

                        if self.start_pos > song_length:
                            i = 0
                            lengths = list(self.song_lengths)
                            if self.start_pos > self.station_length:
                                print("start_pos longer than station length", self.start_pos, self.station_length)
                                self.start_time = time.time()
                                self.start_pos = 0
                            else:
                                #  Find where in the station list we should be base on current time
                                while sum(lengths[0:i]) <= self.start_pos:
                                    i += 1
                                    self.files.rotate(-1)
                                    self.song_lengths.rotate(-1)

                                i -= 1  # compensate for overshoot
                                self.files.rotate(1)
                                self.song_lengths.rotate(1)

                                self.sum_of_song_lengths = sum(lengths[0:i])
                                self.start_pos = self.start_pos - self.sum_of_song_lengths
                                self.start_time = time.time() - self.start_pos
                                print("Jumping to song index: :", i,
                                      "New Song Length =", lengths[i],
                                      "start_pos =", self.start_pos,
                                      "self.sum_of_song_lengths", self.sum_of_song_lengths
                                      )

                        self.new_selection = False

                    else:
                        # print("Same station, new song")
                        self.start_pos = 0

                start_pos = self.start_pos

                self.filename = self.files[0]
                song = self.filename
                settings.CURRENT_SONG = song

                song_fileload = pygame.mixer.Sound(song)  # Load song into memory for waveform generator
                waveform = []
                waveform_length = 0

                print("Playing =", self.filename,
                      "length =", str(round(self.song_lengths[0], 2)),
                      "start_pos =", str(round(self.start_pos, 2))
                      )
                try:
                    song_meta_data = mutagen.File(self.filename, easy=True)
                    # print("All song meta_data = ",song_meta_data)
                    song_artist = str(song_meta_data['artist'])
                    song_title = str(song_meta_data['title'])
                    song_title = song_title.strip("['").strip("']")
                    song_artist = song_artist.strip("['").strip("']")
                except:
                    song_artist = ""
                    song_title = ""

                settings.FOOTER_RADIO[0] = song_artist + " / " + song_title
                pygame.mixer.music.load(song)  # Play using streaming player (mixer.sound doesn't support start_pos)
                self.static.stop()
                try:
                    pygame.mixer.music.play(0, self.start_pos)
                except:
                    pygame.mixer.music.play(0, 0)
                self.state = self.STATES['playing']

    def volume_up(self):
        if settings.SOUND_ENABLED:
            print("Volume up")
            settings.VOLUME = settings.VOLUME + 0.05
            pygame.mixer.music.set_volume(settings.VOLUME)

    def volume_down(self):
        if settings.SOUND_ENABLED:
            print("Volume down")
            settings.VOLUME = settings.VOLUME - 0.05
            pygame.mixer.music.set_volume(settings.VOLUME)

    def play(self):
        if settings.SOUND_ENABLED:
            if self.state == self.STATES['paused']:
                pygame.mixer.music.unpause()
                self.state = self.STATES['playing']
            else:
                self.play_song()
            print("Music resumed")

    def pause_play(self):
        print ("Play/pause triggered")
        if settings.SOUND_ENABLED:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.state = self.STATES['playing']
                print("Music Paused")
            else:
                pygame.mixer.music.unpause()
                self.state = self.STATES['playing']
                print("Music Resumed")

    def pause(self):
        if settings.SOUND_ENABLED:
            self.state = self.STATES['paused']
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                settings.ACTIVE_SONG = None
                self.state = self.STATES['paused']
            print("Music paused")

    def stop(self):
        if settings.SOUND_ENABLED:
            self.state = self.STATES['stopped']
            if self.filename:
                self.last_filename = self.filename
                self.last_playpos = pygame.mixer.music.get_pos()
                self.last_playtime = time.time()
            settings.ACTIVE_SONG = None
            pygame.mixer.music.stop()
            print("Music stopped")

    def next_song(self):
        if settings.SOUND_ENABLED:
            print("Next song")
            self.files.rotate(-1)
            self.song_lengths.rotate(-1)
            self.start_time = time.time()
            self.play_song()

    def prev_song(self):
        if settings.SOUND_ENABLED:
            print("Prev song")
            self.files.rotate(1)
            self.song_lengths.rotate(1)
            self.start_time = time.time()
            self.play_song()

    def randomize_station(self):
        seed = random.random()
        random.Random(seed).shuffle(self.files)
        random.Random(seed).shuffle(self.song_lengths)
        print("Randomized song order")

    def __le__(self, other):
        if type(other) is not RadioStation:
            return 0
        else:
            return self.label <= other.label

    def __ge__(self, other):
        if type(other) is not RadioStation:
            return 0
        else:
            return self.label >= other.label


class RadioClass(RadioStation):
    def __init__(self, station_name, station_folder, station_data, *args, **kwargs):
        # self.station_data = [folder, station_name, station_files, station_ordered, station_lengthss]

        self.label = station_name
        self.directory = station_folder
        self.files = deque(station_data[2])
        self.song_lengths = deque(station_data[4])
        self.total_length = station_data[5]

        super(RadioClass, self).__init__(self, *args, **kwargs)
