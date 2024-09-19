#!/usr/bin/python3

import os
import pygame
import optparse
import sys
import settings
import time
from gpiozero import RotaryEncoder, Button
from signal import pause
from evdev import UInput, ecodes as e

# Ensure uinput module is loaded and set permissions
os.system('sudo modprobe uinput')
os.system('sudo chmod 666 /dev/uinput')

# Setup evdev UInput device for GPIO actions
ui = UInput()

# Rotary Encoder GPIO setup
encoder = RotaryEncoder(a=12, b=16)
encoder_button = Button(20)  # Using GPIO 20 for encoder click

# Define rotary encoder callback
def rotary_callback():
    global last_rotary_event
    if time.time() - last_rotary_event < 0.1:
        return
    last_rotary_event = time.time()
    
    if encoder.steps > 0:
        print("Rotated left")
        ui.write(e.EV_KEY, e.KEY_UP, 1)
        ui.write(e.EV_KEY, e.KEY_UP, 0)
    elif encoder.steps < 0:
        print("Rotated right")
        ui.write(e.EV_KEY, e.KEY_DOWN, 1)
        ui.write(e.EV_KEY, e.KEY_DOWN, 0)
    ui.syn()
    encoder.steps = 0

# Attach the rotary encoder callback
encoder.when_rotated = rotary_callback
last_rotary_event = time.time()

# Define encoder button callback
def encoder_button_callback():
    global last_button_event
    if time.time() - last_button_event < 0.5:
        return
    last_button_event = time.time()
    
    print("Encoder button pressed")
    # Increment currentmenu
    settings.currentmenu += 1
    if settings.currentmenu > settings.submenucount:
        settings.currentmenu = 1
    # Send the corresponding key press
    ui.write(e.EV_KEY, e.KEY_1 + (settings.currentmenu - 1), 1)
    ui.write(e.EV_KEY, e.KEY_1 + (settings.currentmenu - 1), 0)
    ui.syn()
    print(f"Current menu: {settings.currentmenu}, Submenu count: {settings.submenucount}")

# Attach the encoder button callback
encoder_button.when_pressed = encoder_button_callback
last_button_event = time.time()

# Additional knob GPIO setup
knob_buttons = {
    5: e.KEY_F1,
    6: e.KEY_F2,
    13: e.KEY_F3,
    19: e.KEY_F4,
    26: e.KEY_F5,
}

# Define knob button callback
def knob_button_callback(button):
    global last_knob_event
    if time.time() - last_knob_event < 0.1:
        return
    last_knob_event = time.time()
    
    pin = button.pin.number
    key = knob_buttons[pin]
    key_name = pygame.key.name(key)
    print(f"Knob button on GPIO {pin} pressed, sending key {key_name}")
    ui.write(e.EV_KEY, key, 1)
    ui.write(e.EV_KEY, key, 0)
    ui.syn()
    print(f"Sent {key_name} key")

# Attach the knob button callbacks
for pin, key in knob_buttons.items():
    button = Button(pin)
    button.when_pressed = lambda button=button: knob_button_callback(button)

last_knob_event = time.time()

# Pygame setup
parser = optparse.OptionParser(usage='python %prog -c True\nor:\npython %prog -c True', version="0.0.1", prog=sys.argv[0])
parser.add_option('-c', '--cached-map', action="store_true", help="Loads the cached map file stored in map.cache", dest="load_cached", default=False)
options, args = parser.parse_args()

try:
    import RPi.GPIO as GPIO
    settings.GPIO_AVAILABLE = True
except Exception:
    _, err, _ = sys.exc_info()
    print("GPIO UNAVAILABLE (%s)" % err)
    settings.GPIO_AVAILABLE = False

if settings.GPIO_AVAILABLE:
    pass

try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    settings.SOUND_ENABLED = True
except Exception as e:
    settings.SOUND_ENABLED = False

from pypboy.core import Pypboy

def main():
    pygame.init()
    screen = pygame.display.set_mode((480, 320), pygame.FULLSCREEN)
    pygame.display.set_caption('Pip-Boy 3000 MK IV')
    running = True
    current_module = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                print(f"Key pressed: {pygame.key.name(event.key)}")  # Debug print
                if event.key in [pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5, pygame.K_F6]:
                    action = settings.ACTIONS.get(event.key)
                    current_module = action
                    handle_top_menu(action.split('_')[1])

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    boy = Pypboy('Pip-Boy 3000 MK IV', settings.WIDTH, settings.HEIGHT)
    print("RUN")
    boy.run()
    main()
