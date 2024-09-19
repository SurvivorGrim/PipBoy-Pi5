from game.core import Entity
import pypboy
import pygame
import game
import settings
import pypboy.ui
import os
import time
global STATION

class Module(pypboy.SubModule):
    global STATION
    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)
        
        self.label = "STATUS"
        self.images = []

        self.topmenu = pypboy.ui.TopMenu()
        self.add(self.topmenu)
        self.topmenu.label = "STAT"
        self.topmenu.title = settings.MODULE_TEXT


        self.health = Health()
        self.health.rect[0] = -100  #0
        self.health.rect[1] = 30 #131
        self.add(self.health)
        
        self.animation = Animation()
        self.animation.rect[0] = 200 #296
        self.animation.rect[1] = 60 #190
        self.add(self.animation)

        self.prev_time = 0

        self.footer = pypboy.ui.Footer(settings.STATUS_FOOTER)
        self.footer.rect[0] = settings.footer_x
        self.footer.rect[1] = settings.footer_y
        self.add(self.footer)
        # STATUS_FOOTER = ["HP 115/115", "LEVEL 66", "AP 90/90", 90, True]

    #     self.menu = pypboy.ui.Menu(["CND", "RAD", "EFF"], [self.show_cnd, self.show_rad, self.show_eff], 0)
    #     self.menu.rect[0] = settings.menu_x
    #     self.menu.rect[1] = settings.menu_y
    #     self.add(self.menu)

    # def show_cnd(self):
    #     print("CND")

    # def show_rad(self):
    #     print("RAD")

    # def show_eff(self):
    #     print("EFF")

    def render(self, *args, **kwargs):
        global STATION


    # def handle_resume(self):
    #     pass
    #     super(Module, self).handle_resume()

class Animation(game.Entity):

    def __init__(self):
        super(Animation, self).__init__()

        self.image = pygame.Surface((100,230)) #120 250   
        self.animation_time = 0.125 # 8 fps
        self.steps = list(range(4)) + list(range(4, 0, -1))
        self.index = 0                
        self.images = []
        self.prev_time = 0
        self.prev_fps_time = 0

        path = "./images/stats/legs1"
        for f in  sorted(os.listdir(path)):
            if f.endswith(".png"):
                image = pygame.image.load(path + "/" + f).convert_alpha()
                self.images.append(image)
        self.head = pygame.image.load("images/stats/head1/1.png").convert_alpha()

    def render(self, *args, **kwargs):

        self.current_time = time.time()
        self.delta_time = self.current_time - self.prev_time

        if self.delta_time >= self.animation_time:
            self.prev_time = self.current_time

            self.image.fill((0,0,0))

            if self.index >= len(self.images):
                self.index = 0
            self.file = self.images[self.index]

            self.image.blit((self.file),(5 + self.steps[self.index] // 20,62 + self.steps[self.index]))
            self.image.blit((self.head),(22 + self.steps[self.index] // 20,19 + self.steps[self.index]))

            self.index += 1


class Health(game.Entity):

    def __init__(self):
        super(Health, self).__init__()

        self.image = pygame.Surface((480, 320)) #settings.WIDTH, settings.HEIGHT - 180))
        self.image.fill((0,0,0))
        

        # Middle Boxes
        offestx = 35
        offsety = 20
        pygame.draw.rect(self.image, settings.dim, (offestx + 205, offsety + 205, 40, 27)) #Gun box
        pygame.draw.rect(self.image, settings.dim, (offestx + 248, offsety + 205, 21, 27)) #Ammo box
        pygame.draw.rect(self.image, settings.dim, (offestx + 280, offsety + 205, 45, 27)) #Helmet box
        pygame.draw.rect(self.image, settings.dim, (offestx + 328, offsety + 205, 20, 27)) #Armor box
        pygame.draw.rect(self.image, settings.dim, (offestx + 351, offsety + 205, 20, 27)) #Energy box
        pygame.draw.rect(self.image, settings.dim, (offestx + 374, offsety + 205, 20, 27)) #Radiation box

        # Icons
        self.image.blit(pygame.image.load('images/stats/gun.png').convert_alpha(),(offestx + 210, offsety + 208))
        self.image.blit(pygame.image.load('images/stats/reticle.png').convert_alpha(),(offestx + 253, offsety + 207))
        self.image.blit(pygame.image.load('images/stats/helmet.png').convert_alpha(),(offestx + 290, offsety + 207))
        self.image.blit(pygame.image.load('images/stats/shield.png').convert_alpha(),(offestx + 334, offsety + 207))
        self.image.blit(pygame.image.load('images/stats/bolt.png').convert_alpha(),(offestx + 358, offsety + 207))
        self.image.blit(pygame.image.load('images/stats/radiation.png').convert_alpha(),(offestx + 378, offsety + 207))
      
        #Stat text
        settings.FreeRobotoB[14].render_to(self.image, (offestx + 252, offsety + 220), "18", settings.bright) # Ammo count 395
        settings.FreeRobotoB[14].render_to(self.image, (offestx + 333, offsety + 220), "10", settings.bright) # Armor count
        settings.FreeRobotoB[14].render_to(self.image, (offestx + 354, offsety + 220), "20", settings.bright) # Energy count
        settings.FreeRobotoB[14].render_to(self.image, (offestx + 378, offsety + 221), "10", settings.bright) # Rad count
        
        # Health Bars
        pygame.draw.line(self.image, settings.bright, (324, 35), (360, 35), 7)
        pygame.draw.line(self.image, settings.bright, (224, 85), (260, 85), 7)
        pygame.draw.line(self.image, settings.bright, (415, 85), (455, 85), 7)
        pygame.draw.line(self.image, settings.bright, (224, 165), (260, 165), 7)
        pygame.draw.line(self.image, settings.bright, (415, 165), (455, 165), 7)
        pygame.draw.line(self.image, settings.bright, (324, 210), (360, 210), 7)
