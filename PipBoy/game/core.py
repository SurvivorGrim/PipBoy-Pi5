import statistics
from collections import deque

import pygame
import time

from pygame.constants import HWSURFACE
import settings

class Engine(object):

    EVENTS_UPDATE = pygame.USEREVENT + 1
    EVENTS_RENDER = pygame.USEREVENT + 2

    def __init__(self, title, width, height, *args, **kwargs):
        super(Engine, self).__init__(*args, **kwargs)

        # pygame.mixer.init(44100, -16, 2, 512)  # frequency, size, channels, buffersize
        pygame.mixer.init()
        pygame.init()
        
        if settings.FULLSCREEN == True or settings.PI == True:
            self.window = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
        else:
            self.window = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.HWSURFACE)
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption(title)
        pygame.mouse.set_visible(False)
        
        self.groups = []
        self.root_persitant = EntityGroup()
        self.background = pygame.surface.Surface(self.screen.get_size())
        self.background.fill(settings.black)

        self.rescale = False
        self.last_render_time = 0

        self.prev_time = 0
        self.rects_to_update = []

        self.prev_fps_time = 0
        self.fps_average = deque()

    def render(self):

        self.current_time= time.time()
        self.delta_time = self.current_time - self.prev_time

        if self.delta_time >= settings.fps_rate:
            self.prev_time = self.current_time

            self.root_persitant.clear(self.screen, self.background) #Remove background from render queue?
            self.root_persitant.render()
            self.root_persitant.draw(self.screen)
            for group in self.groups:
                group.render()
                group.draw(self.screen)

            # if hasattr(self, 'active'):
            #     self.active.render()

            current_time = time.time()
            fps_delta_time = current_time - self.prev_fps_time
            self.prev_fps_time = current_time

            #  FPS debugging
            if fps_delta_time:
                fps = int(1 / fps_delta_time)

                if len(self.fps_average) > 6:
                    self.fps_average.popleft()
                    # self.fps_average.pop()
                self.fps_average.append(fps)
                fps = int(statistics.mean(self.fps_average))
                # self.screen.putchars(str(fps) + " " + str(self.fps_average), 0, 1)
                #settings.FreeRobotoB[33].render_to(self.screen, (0, 0), str(fps), settings.bright, settings.black)

            # Wait until frame rate hits
            if fps_delta_time < settings.fps_rate:
                wait = int(1000 * settings.fps_rate - fps_delta_time)
                # print("Waiting for", wait, fps_delta_time)
                pygame.time.wait(wait)

            pygame.display.flip()

    def add(self, group):
        if group not in self.groups:
            self.groups.append(group)

    def remove(self, group):
        if group in self.groups:
            self.groups.remove(group)


class EntityGroup(pygame.sprite.LayeredDirty):
    def render(self):
        for entity in self:
            entity.render()

    def move(self, x, y):
        for child in self:
            child.rect.move(x, y)


class Entity(pygame.sprite.DirtySprite):
    def __init__(self, dimensions=(0, 0), layer=0, *args, **kwargs):
        super(Entity, self).__init__(*args, **kwargs)
        self.image = pygame.surface.Surface(dimensions)
        self.rect = self.image.get_rect()
        self.image = self.image.convert_alpha()
        self.groups = pygame.sprite.LayeredDirty()
        self.layer = layer
        self.dirty = 2
        self.blendmode = pygame.BLEND_RGB_ADD

    def render(self, *args, **kwargs):
        pass

    def __le__(self, other):
        if type(self) == type(other):
            return self.label <= other.label
        else:
            return 0

    def __str__(self):
        return "Entity"
