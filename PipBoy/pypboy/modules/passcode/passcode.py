# -*- coding: utf-8 -*-
# Credit to: https://github.com/Metavolt/Fallout_Terminal_Game
# Adapted to use Pygcurse by ZapWizard

import pypboy
import pygame
import game
import settings
import pygcurse
import pypboy.modules.passcode.passwordgen as passwordgen
import locale
import random
import string
import os
import sys
import time

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

class Module(pypboy.SubModule):
    label = "hidden"

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)
        self.passcode = Passcode()
        self.passcode.rect[0] = 11
        self.passcode.rect[1] = 90
        self.add(self.passcode)

    def handle_resume(self):
        if self.paused == True:
            self.paused = False
            print("Resumed Passcode")
            self.passcode.handle_resume()
            super(Module, self).handle_resume()

    def handle_event(self, event):
        self.passcode.handle_event(event)

class Passcode(game.Entity):

    def __init__(self):
        super(Passcode, self).__init__()

        self.logged_in = False
        self.locked_out = False
        self.entry_denied = False
        self.terminal_status = 'Accessible'
        self.attempts = 4
        self.likeness = 0
        self.test_result = ''
        self.address = 0
        self.rows = 16
        self.word_length = 5  # Password length from 4 to 14
        self.num_words = 12
        self.selectable_size = 384  # 16 rows of 12 char columns
        self.side_text_size = 225  # 15 rows of 15 char columns
        self.max_spacing = 0
        self.word_list = []
        self.word_start_locations = []
        self.side_text = []
        self.selectable_text = []
        self.selection_length = 1
        self.selection_index = 0
        self.highlightable_indices = []
        self.bonus_indices = []
        self.password = ''
        self.word_to_print = ''
        self.button_pressed = 0
        self.offset = 0
        self.cursor_x = 7
        self.cursor_y = 6
        self.y_row = 0
        self.x_col = 0
        self.make_new_dataset()

        self.image = pygame.Surface((settings.WIDTH - 10, settings.HEIGHT - 100))
        self.rect[0] = 11
        self.rect[1] = 201


        self.screen_surface = pygame.Surface((settings.WIDTH - 10, settings.HEIGHT - 100))
        # self.screen_surface.fill((0, 0, 0))
        self.rect[0] = 11
        self.rect[1] = 51

        # Create the pygcurse surface
        font = settings.TechMono[22]
        char_width, char_height = font.size("X")
        self.max_chars = int(settings.WIDTH / char_width) - 4
        self.max_lines = int((settings.HEIGHT - 100) / char_height)

        self.screen = pygcurse.PygcurseSurface(self.max_chars, self.max_lines, font,
                                               settings.bright, settings.black, self.screen_surface, True, 1000)
        self.screen._autoupdate = False
        self.screen._autodisplayupdate = False

        self.screen.cursor = (0, 0)
        self.screen.pushcursor()

        self.animation_time = 1 / 24
        self.prev_time = 0
        self.current_time = 0
        self.button = None

        self.cursor_time = 1  # Cursor blink speed
        self.prev_cursor_time = 0

        self.wait = 0

        if settings.SOUND_ENABLED:
            self.dial_move_sfx = pygame.mixer.Sound('./sounds/pipboy/RotaryVertical/UI_PipBoy_RotaryVertical_01.ogg')
            self.dial_move_sfx.set_volume(settings.VOLUME)
            self.pass_bad = pygame.mixer.Sound('./sounds/terminal/UI_Hacking_PassBad.ogg')
            self.pass_bad.set_volume(settings.VOLUME)
            self.pass_good = pygame.mixer.Sound('./sounds/terminal/UI_Hacking_PassGood.ogg')
            self.pass_good.set_volume(settings.VOLUME)
            self.help_attempts = pygame.mixer.Sound('./sounds/terminal/UI_Hacking_PasswordHelpAttempts.ogg')
            self.help_attempts.set_volume(settings.VOLUME)
            self.help_dud = pygame.mixer.Sound('./sounds/terminal/UI_Hacking_PasswordHelpDud.ogg')
            self.help_dud.set_volume(settings.VOLUME)

    def handle_resume(self):
        self.logged_in = False
        self.locked_out = False
        self.entry_denied = False
        self.terminal_status = 'Accessible'
        self.attempts = 4
        self.make_new_dataset()


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.button = "up"
            elif event.key == pygame.K_DOWN:
                self.button = "down"
            elif event.key == pygame.K_LEFT:
                self.button = "left"
            elif event.key == pygame.K_RIGHT:
                self.button = "right"
            elif event.key == pygame.K_RETURN:
                self.button = "enter"
            elif event.key == pygame.K_BACKSPACE:
                self.button = "reset"
            if self.locked_out:
                if settings.SOUND_ENABLED:
                    self.pass_bad.play()

            print("Key = ", self.button)

    def render(self, *args, **kwargs):
        super(Passcode, self).render(self, *args, **kwargs)




        self.current_time = time.time()

        if (self.current_time - self.prev_time) >= self.animation_time:
            self.prev_time = self.current_time

            if self.button == "reset":
                self.make_new_dataset()
                self.button = None
                pygame.event.clear()

            if not self.locked_out and not self.logged_in:


                # self.screen.write(str(self.current_time), 0, 1)

                self.update_cursor()

                self.get_index_from_cursor_pos(self.cursor_y, self.cursor_x)
                self.word_to_print = self.get_indices_of_selection()

                # Test Selection, pass, incorrect, bonus, or lockout
                # Also, "scroll" the printed side output up after testing

                if self.button == "enter":
                    self.button = None
                    pygame.event.clear()
                    self.terminal_status = self.test_selection()
                    if self.terminal_status == 'Entry denied.':
                        self.scroll_side_text(self.word_to_print)
                        self.scroll_side_text(self.terminal_status)
                        self.scroll_side_text('Likeness=' + str(self.likeness))
                    elif self.terminal_status == 'TERMINAL LOCKED' or \
                            self.terminal_status == 'Password Accepted.':
                        print("Terminal Finished")
                    elif self.terminal_status == 'Tries Reset.' or \
                            self.terminal_status == 'Dud Removed.':
                        self.scroll_side_text(self.word_to_print)
                        self.scroll_side_text(self.terminal_status)

                self.screen.write('Welcome to ROBCO Industries (TM) Termlink\n\n', 0, 0)
                self.screen.write('Password Required\n\n', 0, 2)
                self.screen.write('Attempts Remaining:', 0, 4)

                # Update attempts remaining after testing
                for blank in range(0, 4):
                    self.screen.write(" ", 19 + blank, 4)
                for attempt in range(self.attempts):
                    self.screen.write("▯", 19 + attempt, 4)

                # Show the "memory" dump
                # With the selectable text wrapping in columns
                for row in range(self.rows):
                    self.screen.write(hex(self.address + (row * 12)).upper(), 0, row + 6)
                    self.screen.write(''.join(self.selectable_text[12 * row:(12 * row) + 12]), 7, row + 6)
                    self.screen.write(hex(self.address + row + 16).upper(), 20, row + 6)
                    self.screen.write(''.join(self.selectable_text[(12 * row) + 192:(12 * row) + 204]), 27, row + 6)


                # Highlight the appropriate characters
                for i, _ in enumerate(self.highlightable_indices):
                    self.y_row, self.x_col = self.get_cursor_pos_from_index(self.highlightable_indices[i])
                    self.screen.reversecolors((self.x_col, self.y_row, 1, 1))
                    # self.screen.setfgcolor(settings.black, (self.x_col, self.y_row, 1, 1))
                    # self.screen.setbgcolor(settings.bright, (self.x_col, self.y_row, 1, 1))
                #
                # if (self.current_time - self.prev_cursor_time) >= self.cursor_time:
                #     self.prev_cursor_time = self.current_time
                #     for i, _ in enumerate(self.highlightable_indices):
                #         self.y_row, self.x_col = self.get_cursor_pos_from_index(self.highlightable_indices[i])
                #         self.screen.reversecolors((self.x_col, self.y_row, 1, 1))

                    # self.screen.write(self.y_row, self.x_col, 1, curses.color_pair(2))

                # Show hidden location/password data for debugging
                # self.screen.write(str(self.word_start_locations), 20, 1)
                # self.screen.write('likeness=' + str(self.likeness), 40, 1)
                self.screen.write(self.password, 0, 5, settings.dark)
                # self.screen.write(str(self.attempts), 0, 5,settings.dim)
                # self.screen.write(str(self.selection_index), 40, 3)
                # self.screen.write(str(self.get_cursor_pos_from_index(self.selection_index)), 40, 3)
                # self.screen.write(self.terminal_status, 40, 3)
                # self.screen.write(str(self.highlightable_indices), 40, 5)
                # self.screen.write(str(self.bonus_indices), 40, 5)

                # Draw the side text of scrolling entries
                for row in range(15):
                    self.screen.write(''.join(self.side_text[15 * row:(15 * row) + 15]), 40, row + 6)

                self.screen.write('>' + self.word_to_print, 40, 21)
                # Adding the blink attribute cleared the color attribute, so we need to add it again
                # Multiple attributes for curses require a bitwise OR (go figure)
                self.screen.write('█')
                # screen.addch('█', curses.A_BLINK | curses.color_pair(1))


            elif self.locked_out:
                # Only allow system reboot
                self.screen.fill(" ")

                self.screen.write(self.terminal_status, 20, 9)
                self.screen.write('PLEASE CONTACT ADMINISTRATOR', 14, 11)

            elif self.logged_in:

                # Allow "logging out" to reset the game
                self.screen.fill(" ")
                self.screen.write('Welcome to ROBCO Industries (TM) Termlink', 0, 0)
                self.screen.write(self.terminal_status, 0, 21)
                if self.wait < 50:
                    self.wait += 1
                else:
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F6))

                # self.screen.write('█')
                # screen.addch('█', curses.A_BLINK | curses.color_pair(1))

            self.screen.update()
            self.image.blit(self.screen_surface, (0, 0))

    def make_new_dataset(self):
        print("Making a new passcode dataset")

        self.logged_in = False
        self.locked_out = False
        self.entry_denied = False
        self.terminal_status = 'Accessible'
        self.attempts = 4

        # Choose a new "memory" address to look at
        junk_chars = list(string.punctuation)
        self.address = random.randint(4096, 65500)
        self.selectable_text.clear()
        self.side_text.clear()

        # Test of side text
        for _ in range(self.side_text_size):
            self.side_text.append(' ')

        # Generate a new "memory" dump populated with junk
        for char in range(self.selectable_size):
            self.selectable_text.append(random.choice(junk_chars))

        # Generate a list of words with one password
        self.word_list = passwordgen.get_list_of_words(self.num_words,
                                                       self.word_length)
        random.shuffle(self.word_list)
        self.password = random.choice(self.word_list)
        # Keep track of where the password is for later bonus testing
        # It needs to be randomly placed, but we can't accidentally delete it
        # if a "dud replaced" bonus event occurs
        self.password_location = self.word_list.index(self.password)

        # Randomly insert the words and password among the junk chars,
        # but distribute somewhat evenly to prevent overlap
        self.max_spacing = (self.selectable_size - (self.word_length * self.num_words)) // self.num_words
        self.offset = random.randint(1, self.max_spacing)

        for word in self.word_list:
            # Overwrite the junk chars with the words we want
            for char_idx, char in enumerate(list(word)):
                # Place the individual letters
                self.selectable_text[self.offset + char_idx] = word[char_idx]
                # Mark the start of all non-passwords
                if word is not self.word_list[self.password_location] and char_idx == 0:
                    self.word_start_locations.append(self.offset)
            self.offset = self.offset + self.word_length + \
                          random.randint(self.max_spacing - 2, self.max_spacing)
            # Keep from placing words too near the end
            if self.offset > self.selectable_size:
                self.offset = self.selectable_size - self.word_length

    def update_cursor(self):

        if self.button == "down":
            self.cursor_y = self.cursor_y + 1
            # print("Down")
            self.button = None
            if settings.SOUND_ENABLED:
                self.dial_move_sfx.play()
        elif self.button == "up":
            self.cursor_y = self.cursor_y - 1
            # print("Up")
            self.button = None
            if settings.SOUND_ENABLED:
                self.dial_move_sfx.play()
        elif self.button == "right":
            self.cursor_x = self.cursor_x + 1
            # print("Right")
            self.button = None
            if settings.SOUND_ENABLED:
                self.dial_move_sfx.play()
        elif self.button == "left":
            self.cursor_x = self.cursor_x - 1
            # print("Left")
            self.button = None
            if settings.SOUND_ENABLED:
                self.dial_move_sfx.play()

        # Constrain the position to selectable areas of the two columns
        if self.cursor_y < 6:
            self.cursor_y = 21
        elif self.cursor_y > 21:
            self.cursor_y = 6

        if self.cursor_x < 7:
            self.cursor_x = 38
        elif self.cursor_x == 26:  # Did we move left from the column on the right
            self.cursor_x = 18
        elif 18 < self.cursor_x < 27:
            self.cursor_x = 27
        elif self.cursor_x > 38:
            self.cursor_x = 7

        return self.cursor_y, self.cursor_x

    def get_cursor_pos_from_index(self, index):
        # Convert from a spot in selectable_text so
        # we can more easily modify the displayed characters

        self.index = index
        self.x_col = 7
        self.y_row = 6

        self.x_col = self.x_col + (self.index % 12)
        if self.index > 191:
            self.x_col = self.x_col + 20
            self.index = self.index - 192

        self.y_row = self.y_row + (self.index // 12)

        return [self.y_row, self.x_col]

    def get_index_from_cursor_pos(self, cur_y, cur_x):
        # Convert from a displayable cursor location
        # to a spot suitable for iterating through selectable_text

        self.selection_index = 0
        self.x_col = cur_x - 6
        self.y_row = cur_y - 6
        self.selection_characters = []
        self.end_of_word = 0

        if self.x_col > 18:
            self.selection_index = self.selection_index + 191 + (self.x_col - 20)
        else:
            self.selection_index = self.selection_index + self.x_col - 1

        self.selection_index = self.selection_index + (12 * self.y_row)

    def get_indices_of_selection(self):
        # Check for capital letters and open bracket characters
        # Now, look right of a letter in the list until a non letter is found

        self.highlightable_indices.clear()

        if self.selectable_text[self.selection_index].isupper():
            # At most, look right of a letter up to the current word length
            for len_offset, char in enumerate(range(self.word_length + 1)):
                # Any junk character marks the end of the word
                if not self.selectable_text[self.selection_index + len_offset].isupper():
                    self.end_of_word = self.selection_index + len_offset
                    self.selection_characters = self.selectable_text[self.end_of_word - self.word_length:
                                                                     self.end_of_word]
                    for idx in range(self.end_of_word - self.word_length, self.end_of_word, 1):
                        self.highlightable_indices.append(idx)
                    break
            return ''.join(self.selection_characters)
        # Or, try and find a matching closing character
        elif self.selectable_text[self.selection_index] in ['(', '{', '[', '<']:
            # I could have iterated over a matching set of closing characters, but this is more readable to me
            if self.selectable_text[self.selection_index] == '(':
                self.closing_char = ')'
            elif self.selectable_text[self.selection_index] == '{':
                self.closing_char = '}'
            elif self.selectable_text[self.selection_index] == '[':
                self.closing_char = ']'
            elif self.selectable_text[self.selection_index] == '<':
                self.closing_char = '>'
            # Columns are 12 chars wide, so search up to that many spaces away within selectable text
            for len_offset, char in enumerate(range(13)):
                # Don't look past the end of the list
                if self.selection_index + len_offset > 383:
                    break
                # Record the indices of the enclosing brackets
                if self.selectable_text[self.selection_index + len_offset] == self.closing_char:
                    self.end_of_word = self.selection_index + len_offset + 1
                    self.selection_characters = self.selectable_text[self.end_of_word - len_offset - 1:
                                                                     self.end_of_word]
                    for idx in range(self.end_of_word - len_offset - 1, self.end_of_word, 1):
                        self.highlightable_indices.append(idx)
                    return ''.join(self.selection_characters)
            self.highlightable_indices.append(self.selection_index)
            return self.selectable_text[self.selection_index]
        else:  # Neither a letter or set of brackets found
            self.highlightable_indices.append(self.selection_index)
            return self.selectable_text[self.selection_index]

    def test_selection(self):

        self.likeness = 0
        self.entry_denied = False

        # Characters in a submission must match at the same index within a password
        if self.selectable_text[self.highlightable_indices[0]].isupper():
            for char_loc, idx in enumerate(self.highlightable_indices):
                if self.selectable_text[idx] == self.password[char_loc]:
                    self.likeness = self.likeness + 1
            # Only the password will have maximum likeness
            if self.likeness == self.word_length:
                self.logged_in = True
                if settings.SOUND_ENABLED:
                    self.pass_good.play()
                return 'Password Accepted.'
            else:
                self.entry_denied = True
        # Apply bonus action if a matching set of brackets is found
        elif self.selectable_text[self.highlightable_indices[0]] in ['(', '{', '[', '<'] and \
                len(self.highlightable_indices) > 1 and \
                self.highlightable_indices[0] not in self.bonus_indices:
            # Randomly remove a dud word or reset attempts
            self.bonus_indices.append(self.highlightable_indices[0])
            if random.randint(0, 100) > 20:
                self.dud = random.choice(self.word_start_locations)
                self.word_start_locations.remove(self.dud)
                for idx in range(self.word_length):
                    self.selectable_text[self.dud + idx] = '.'
                if settings.SOUND_ENABLED:
                    self.help_dud.play()
                return 'Dud Removed.'
            else:
                self.attempts = 4
                if settings.SOUND_ENABLED:
                    self.help_attempts.play()
                return 'Tries Reset.'
        # There's neither a penalty nor a bonus for clicking a valid bracket pair again
        elif self.highlightable_indices[0] in self.bonus_indices:
            return ''
        else:  # Junk characters are automatically incorrect
            self.entry_denied = True

        if self.entry_denied:
            if settings.SOUND_ENABLED:
                self.pass_bad.play()
            if self.attempts > 1:
                self.attempts = self.attempts - 1
                return 'Entry denied.'
            else:
                self.locked_out = True
                return 'TERMINAL LOCKED'  # PLEASE CONTACT ADMINISTRATOR

    def scroll_side_text(self, text_to_scroll):

        for col in range(14):
            self.side_text[0 + col] = ' '
        for row in range(14):
            # Copy the next row of characters onto the current row of characters
            self.side_text[row * 15:(row * 15) + 15] = \
                self.side_text[(row + 1) * 15: ((row + 1) * 15) + 15]
            # Clear the copied row since next row doesn't necessarily overwrite all spots
            self.side_text[(row + 1) * 15: ((row + 1) * 15) + 15] = '               '

        self.side_text[210] = '>'
        # Copy the player's entry separately as the last line
        for offset, letter in enumerate(list(text_to_scroll)):
            self.side_text[211 + offset] = letter
