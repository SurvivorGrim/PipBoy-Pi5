import pypboy
import pygame
import game
import settings
import pypboy.ui
import os
import time

class Module(pypboy.SubModule):

    label = "hidden"
    images = []

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)
        self.thumbs = Thumbs()
        self.thumbs.rect[0] = 200
        self.thumbs.rect[1] = 110
        self.add(self.thumbs)

        if settings.SOUND_ENABLED:
            self.sound = pygame.mixer.Sound('sounds/pipboy/BootSequence/UI_PipBoy_BootSequence_C.ogg')
            self.sound.set_volume(settings.VOLUME)
    
    def handle_pause(self):
        # self.sound.stop()
        super(Module, self).handle_pause()

    def handle_resume(self):
        if settings.SOUND_ENABLED:
            self.sound.play()
            self.playing = True  
        self.thumbs.handle_resume()
        super(Module, self).handle_resume()

class Thumbs(game.Entity):

    def __init__(self):
        super(Thumbs, self).__init__()

        self.image = pygame.Surface((180, 300))
        self.image.fill((0, 0, 0))

        self.clock = pygame.time.Clock()
        self.animation_time = 0.125
        self.current_time = 0
        self.index = 0                
        self.images = []
        self.prev_time = 0   
        self.frameorder = [0,0,0,0,0,0,0,0,0,0,0,1,2,0,0,0,0,0,0,0,0,3,4,5,6,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7]

        self.brightness = list(range(0, 150, 15)) + list(range(150, 0, -15))
        self.brightness_index = 0
        path = "./images/boot"
        for filename in sorted(os.listdir(path)):
            if filename.endswith(".png"):
                self.images.append(pygame.image.load(path + "/" + filename).convert_alpha())
                      
    def render(self):
        
        self.current_time = time.time()
        self.delta_time = self.current_time - self.prev_time
        
        if self.delta_time >= self.animation_time:
            self.prev_time = time.time()

            if self.index >= len(self.frameorder): #Loop the animation
                self.index = 0
                settings.glitch = True
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F1))

            self.image.fill((0,0,0))
            self.image.blit((self.images[self.frameorder[self.index]]),(0,0))
            
            self.index += 1
            
            self.brightness_index += 1
            if self.brightness_index >= len(self.brightness):
                self.brightness_index = 0
            self.color = (0, self.brightness[self.brightness_index], 0)

            settings.FreeRobotoB[29].render_to(self.image, (10, 270), "INITIATING...", self.color)

    def handle_resume(self):
        self.index = 0
