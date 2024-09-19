import pygame
import pygame.freetype
import atexit
import saved
import os

# Custom
name = "Fally_Boi"

# SCREEN
WIDTH = 480
HEIGHT = 320
FULLSCREEN = False

# OUTPUT_WIDTH = 720
# OUTPUT_HEIGHT = 720

# Menu Position
menu_x = 10
menu_y = 60 #140

# Menu Position
footer_x = 0
footer_y = 290 #631

# Description box Position
description_box_x = 0 #350
description_box_y = 100  #240
description_box_width = 450

# COLORS
black = (0, 0, 0)
bright = (0, 230, 0)
light = (0, 170, 0)
mid = (0, 120, 0)
dim = (0, 70, 0)
dark = (0, 40, 0)

# MAP
# MAP_FOCUS = (-5.9347681, 54.5889076)
# MAP_FOCUS = (-102.3016145, 21.8841274) #Old Default?
# MAP_FOCUS = (-118.5723894,34.3917171)#CodeNinjasValencia
# MAP_FOCUS = (32.7157, 117.1611)
# MAP_FOCUS = (-92.1943197, 38.5653437)
# MAP_FOCUS = (-98.0878917, 30.1914818) # Zap's Hometown
MAP_FOCUS = (-71.0594587, 42.3614408)  # Boston MA
LOAD_CACHED_MAP = False

# Open Strett Map settings
WORLD_MAP_FOCUS = 0.07  # Needed to handle the 50k node limit from OSM

# Google maps:
MAP_TYPE = "hybrid"  # Select Hybrid if you want labels and roads, satellite if you want imagry only
MAP_STYLE = "feature:all|geometry.stroke|labels.text.stroke"
WORLD_MAP_ZOOM = 12
LOCAL_MAP_ZOOM = 17

EVENTS = {
    'SONG_END': pygame.USEREVENT + 1,
    'PLAYPAUSE': pygame.USEREVENT + 2,
    'HOLOTAPE_END': pygame.USEREVENT + 3
}

MODULES = {
    0: "STAT",
    1: "INV",
    2: "DATA",
    3: "MAP",
    4: "RADIO",
    5: "BOOT",

}

MODULE_TEXT = ["STAT", "INV", "DATA", "MAP", "RADIO"]

STARTER_MODULE = "boot"

ACTIONS = {
    pygame.K_F1: "module_stats",
    pygame.K_F2: "module_items",
    pygame.K_F3: "module_data",
    pygame.K_F4: "module_map",
    pygame.K_F5: "module_radio",
    pygame.K_F6: "module_boot",
    pygame.K_F7: "module_passcode",
    pygame.K_1: "knob_1",
    pygame.K_2: "knob_2",
    pygame.K_3: "knob_3",
    pygame.K_4: "knob_4",
    pygame.K_5: "knob_5",
    pygame.K_UP: "dial_up",
    pygame.K_DOWN: "dial_down",
    pygame.K_PLUS: "zoom_in",
    pygame.K_EQUALS: "zoom_in",
    pygame.K_MINUS: "zoom_out",
    pygame.K_KP_PLUS: "zoom_in",
    pygame.K_KP_MINUS: "zoom_out",
}

submenucount = 3
currentmenu = 1

# Using GPIO.BCM as mode
# GPIO 23 pin16 reboot
# GPIO 25 pin 22 blank screen do not use
GPIO_ACTIONS = {
    #    19: "module_stats", #GPIO 4
    #    26: "module_items", #GPIO 14
    #    16: "module_data", #GPIO 15
    #	18:	"knob_1", #GPIO 18 Do Not enable messes with the screen.
    #	18: "knob_2", #GPIO 18 Turns screen off do not use
    #	7: "knob_3", #GPIO 7
    #	22: "knob_1", #GPIO 22
    #	22: "dial_down", #GPIO 22
    #	25: "dial_up", #GPIO 25
    #    20: "knob_2", #GPIO 24
    #	25: "knob_3" #GPIO 23
}
#
# MAP_ICONS = {
#     "camp": pygame.image.load('images/map_icons/camp.png'),
#     "factory": pygame.image.load('images/map_icons/factory.png'),
#     "metro": pygame.image.load('images/map_icons/metro.png'),
#     "misc": pygame.image.load('images/map_icons/misc.png'),
#     "monument": pygame.image.load('images/map_icons/monument.png'),
#     "vault": pygame.image.load('images/map_icons/vault.png'),
#     "settlement": pygame.image.load('images/map_icons/settlement.png'),
#     "ruin": pygame.image.load('images/map_icons/ruin.png'),
#     "cave": pygame.image.load('images/map_icons/cave.png'),
#     "landmark": pygame.image.load('images/map_icons/landmark.png'),
#     "city": pygame.image.load('images/map_icons/city.png'),
#     "office": pygame.image.load('images/map_icons/office.png'),
#     "sewer": pygame.image.load('images/map_icons/sewer.png'),
# }
#
# AMENITIES = {
#     'pub': MAP_ICONS['vault'],
#     'nightclub': MAP_ICONS['vault'],
#     'bar': MAP_ICONS['vault'],
#     'fast_food': MAP_ICONS['settlement'],
#     'cafe': MAP_ICONS['settlement'],
#     #	'drinking_water': 	MAP_ICONS['sewer'],
#     'restaurant': MAP_ICONS['settlement'],
#     'cinema': MAP_ICONS['office'],
#     'pharmacy': MAP_ICONS['office'],
#     'school': MAP_ICONS['office'],
#     'bank': MAP_ICONS['monument'],
#     'townhall': MAP_ICONS['monument'],
#     #	'bicycle_parking': 	MAP_ICONS['misc'],
#     #	'place_of_worship': MAP_ICONS['misc'],
#     'theatre': MAP_ICONS['office'],
#     #	'bus_station': 		MAP_ICONS['misc'],
#     #	'parking': 			MAP_ICONS['misc'],
#     #	'fountain': 		MAP_ICONS['misc'],
#     #	'marketplace': 		MAP_ICONS['misc'],
#     #	'atm': 				MAP_ICONS['misc'],
#     'misc': MAP_ICONS['misc']
# }
#
# INVENTORY_OLD = [
#     "Ranger Sequoia",
#     "Anti-Materiel Rifle ",
#     "Deathclaw Gauntlet",
#     "Flamer",
#     "NCR dogtag",
#     ".45-70 Gov't(20)",
#     ".44 Magnum(20)",
#     "Pulse Grenade (2)"
# ]

# Menu Structure: ["Menu item",Quantity,"Image (or folder for animation")","Description text",[["stats_text_1","stats_number_1"],["stats_text_2","stats_number_2"]]],

FOOTER_RADIO = ["", "", "", "", False]

SPECIAL = [
    ["Strength", 4, "images/stats/special/strength",
     "Strength is a measure of your raw physical power. It affects how much you can carry, and the damage of all melee attacks."],
    ["Perception", 8, "images/stats/special/perception",
     "Perception is your environmental awareness and 'sixth sense', and affects weapon accuracy in V.A.T.S."],
    ["Endurance", 3, "images/stats/special/endurance",
     "Endurance is a measure of your overall physical fitness. It affect your total Health and the Action Point drain from sprinting."],
    ["Charisma", 5, "images/stats/special/charisma",
     "Charisma is your ability to charm and convince others. It affects your success to persuade in dialogue and prices when you barter."],
    ["Intelligence", 6, "images/stats/special/intelligence",
     'Intelligence is a measure of your overall metal acuity, and affects the number of Experience Points earned'],
    ["Agility", 3, "images/stats/special/agility",
     "Agility is a measure of your overall fitnesse and reflexes. It affects the number of Action Points in V.A.T.S. and your ability to sneak"],
    ["Luck", 3, "images/stats/special/luck",
     "Luck is a measure of your general good fortune, and affects the recharge rate of Critical Hits"],
]

STATUS_FOOTER = ["HP 90/100", "LEVEL 120", "AP 90/90", 90, True]

WEAPONS = [
    ["10mm Pistol", "1", "images/inventory/10mmpistol", "",
     [["Damage", 18], ["10mm", 57, ], ["Fire Rate", 46], ["Range", 83], ["Accuracy", 60], ["Weight", 3.5],
      ["Value", 50]]],
    ["Bottle Cap Mine", "1", "images/inventory/bottlecapmine", "",
     [["Damage", 301], ["Fire Rate", 0], ["Range", 93], ["Accuracy", 0], ["Weight", 0.5], ["Value", 75]]],
    ["Combat Knife", "1", "images/inventory/combatknife", "",
     [["Damage", 10], ["Speed", "FAST"], ["Weight", 1], ["Value", 25]]],
    ["Fragmentation Grenade", 2, "images/inventory/grenadefrag", "",
     [["Damage", 151], ["Fire Rate", 0], ["Range", 93], ["Accuracy", 0], ["Weight", 0.5], ["Value", 50]]],
    ["Laser Musket", 1, "images/inventory/lasermusket", "",
     [["Damage", 30], ["Cell", 30], ["Fire Rate", 6], ["Range", 107], ["Accuracy", 70], ["Weight", 12.6],
      ["Value", 61]]],
    ["Laser Rifle", 1, "images/inventory/laserrifle", "",
     [["Damage", 30], ["Cell", 30], ["Fire Rate", 6], ["Range", 107], ["Accuracy", 70], ["Weight", 12.6],
      ["Value", 61]]],
    ["Plasma Mine", 3, "images/inventory/plasmamine", "",
     [["Damage", 150], ["Fire Rate", 0], ["Range", 93], ["Accuracy", 0], ["Weight", 0.5], ["Value", 100]]],
]

FOOTER_WEAPONS = ["WEIGHT 186/200", "CAPS: 35", "AMMO: 500", None, False]

STATS = [
    ["General", "", "~", "",
     [["Locations Discovered", 221], ["Locations Cleared", 66, ], ["Days Passed", 80], ["Hours Slept", 36], ["Hours Waiting", 24], ["Caps Found", 18488], ["Most Caps Carried", 3694], ["Junk Collected", 2831], ["Chests Looted", 586], ["Magazines Found", 26], ["Food Eaten", 51], ["Simspacks Taken", 202], ["Rad-X Taken", 43]]],
    ["Quests", "", "", "",
     [["Quests Completed", 82], ["Misc Objectives Completed", 35, ], ["Main Quests Completed", 12], ["Side Quests Completed", 15], ["Brotherhood of Steel Quests Completed", 37], ["Institue Quests Completed", 4], ["Minutemen Quests Completed", 6]]],
    ["Combat", "", "", "",
     [["People Killed", 691], ["Animals Killed", 168, ], ["Creatures Killed", 967], ["Robots Killed", 77], ["Synths Killed", 146], ["Turrets Killed", 149], ["Legendary Enemies Killed", 77], ["Critical Strikes", 22], ["Sneak Attacks", 16], ["Backstabs", 0], ["Weapons Disarmed", 0], ["Grand Slams", 0], ["Fits of Rage", 0]]],
    ["Crafting", "", "", "",
     [["Weapon Mods Crafted", 14], ["Armor Mods Crafted", 13, ], ["Plants Harvested", 14], ["Chems Crafted", 0], ["Food Cooked", 0], ["Wokshops Unlocked", 0], ["Items Scrapped", 208], ["Objects Built", 32], ["Supply Lines Created", 0]]],
    ["Crime", "", "", "",
     [["Locks Picked", 105], ["Computers Hacked", 43, ], ["Pockets Picked", 1], ["Items Stolen", 105], ["Assaults", 1], ["Murders", 13], ["Trespasses", 0]]],

]

STATS_FOOTER = ["DATE", "TIME", "", None, False]

ARMOR = [
    ["Vault 111 Jumpsuit", "", "images/inventory/armor_suit", "", [["DMG Resist", 15],["", 20], ["Weight", 1], ["Value", 20]]],
    ["Mask", "", "images/inventory/armor_mask", "", [["DMG Resist", 15],["", 20], ["Weight", 1], ["Value", 20]]],
    ["Eyeglasses", "", "images/inventory/armor_glasses", "", [["PER", 1], ["Weight", 0.1], ["Value", 7]]],
    ["Helmet", "", "images/inventory/armor_helmet", "", [["DMG Resist", 15],["", 20], ["Weight", 7], ["Value", 48]]],
    ["Chest Armor", "", "images/inventory/armor_chest", "", [["DMG Resist", 27],["", 22], ["Weight", 9], ["Value", 75]]],
    ["Left Arm", "", "images/inventory/armor_left_arm", "", [["DMG Resist", 14],["", 12], ["Weight", 5], ["Value", 112]]],
    ["Right Arm", "", "images/inventory/armor_right_arm", "", [["DMG Resist", 15],["", 11], ["Weight", 6], ["Value", 76]]],
    ["Left Leg", "", "images/inventory/armor_left_leg", "", [["DMG Resist", 18],["", 10], ["Weight", 5], ["Value", 88]]],
    ["Right Leg", "", "images/inventory/armor_right_leg", "", [["DMG Resist", 12],["", 7], ["Weight", 7], ["Value", 145]]],
    ["Wedding Ring", "", "images/inventory/armor_ring", "", [["Weight", 0], ["Value", 250]]],
]

FOOTER_ARMOR = ["WEIGHT 186/200", "CAPS: 35", "ARMOR: 50 / RADIATION: 1", None, False]

AID = [
    ["StimPak (3)", "", "images/inventory/stimpak",
     "A stimpak is an autoinjector loaded with a variety of healing medications and stimulants. By injecting the stimpak, one drastically increase one's own recuperative functions and gains lost hit points almost instantly."],
    ["Purified Water (14)", "", "images/inventory/purified_water",
     "A can of water, which has been cleansed of radiation. It restores 40 health."],
    ["RadAway (22)", "", "images/inventory/radaway",
     "RadAway is an intravenous chemical solution that bonds with radioactive particles and removes them from the user's system"],
]

FOOTER_AID = ["WEIGHT 186/200", "CAPS: 35", "HEALTH", 90, False]

MISC = [
    ["Pencil (3)", "", "images/inventory/pencil",
     "An orange pencil with a pink eraser. Use it to mark objects or poke eyes out."],
    ["Pre-War Money (250)", "", "images/inventory/prewarmoney", "Useless to all but time travelers. Can be used as tinder."],
    ["Wonderglue (2)", "", "images/inventory/wonderglue",
     "Joins this to that instantly. Will also bond fingers together faster than you can blink!"],
]

FOOTER_MISC = ["WEIGHT 20/200", "CAPS: 1", "", None, False]

AMMO = [
    ["10mm Rounds (15)", "", "images/inventory/10mmAmmo", "", [["Weight", 0], ["Value", 2]]],
    ["Fusion Cells (47)", "", "images/inventory/fusion_cells", "", [["Weight", 0], ["Value", 3]]],
]

FOOTER_TIME = ["DATE", "TIME", "", None, False]

QUESTS = [
    ["War Never Changes","","images/quests/war_never_changes","Get to Vault 111. Survive."],
    ["Out of Time","","images/quests/out_of_time",
     "While cryogenically frozen in Vault 111, I awoke just long enough to witness the murder of my wife/husband and the abduction of my infant son. I need to escape Vault 111 and return home, so I can begin to make sense of this tragedy."],
    ["Unlikely Valentine","","images/quests/unlikely_valentine",
     "Nick Valentine apparently went missing while investigating a case. If I want his help in locating Shaun, I'll need to find him first. His last known location was Park Street Station."],
    ["Reunions","","images/quests/reunions",
     "Kellogg is dead, and Shaun isn't here with him. I need to search around for some information that may lead me to my son."],
    ["The Glowing Sea","","images/quests/the_glowing_sea",
     "I need to find Virgil, the escaped Institute scientist, somewhere in the Glowing Sea and hope that he can help me reach the Institute."],
]

SKILLS = [
    ["Action Boy"],
    ["Animal Friend"],
    ["Awareness"],
    ["Gunslinger"],
    ["Hacker"],
    ["Mysterious Stranger"],
    ["Rifleman"],
    ["Science"],
]

PERKS = [
    ["Action Boy", 2, "images/perks/action_boy", "Your Action Points now regenerate 50% faster."],
    ["Animal Friend", 3, "images/perks/animal_friend",
     "When you successfully pacify an animal, you can give it specific commands."],
    ["Awareness", 1, "images/perks/awareness",
     "To defeat your enemies, know their weaknesses! You can view a target's specific damage resistances in V.A.T.S."],
    ["Blacksmith", 3, "images/perks/blacksmith",
     "Fire up the forge and gain access to base level and Rank 3 melee weapon mods."],
    ["Fortune Finder", 1, "images/perks/fortune_finder",
     "You've learned to discover the Wasteland's hidden wealth, and discover more bottle caps in containers."],
    ["Gunslinger", 1, "images/perks/gunslinger",
     "Channel the spirit of the old west! Non-automatic pistols do 20% more damage."],
    ["Hacker", 4, "images/perks/hacker", "When hacking, you never get locked out of a terminal when things go wrong."],
    ["Lone Wanderer", 2, "images/perks/lone_wanderer",
     "When adventuring without a companion, you take 30% less damage and carry weight increases by 100"],
    ["Mysterious Stranger", 1, "images/perks/mysterious_stranger",
     "Who is he? Why does he help? Who cares! The Mysterious Stranger will appear occasionally in V.A.T.S. to lend a hand, with deadly efficiency..."],
    ["Rifleman", 5, "images/perks/rifleman",
     "Attacks with non-automatic rifles do double damage and ignore 30% of a target's armor. They also have a slightly higher chance of crippling a limb."],
    ["Robotics Expert", 3, "images/perks/robotics_expert",
     "Machines will always serve humans, if you have anything to say about it. Hack a robot, and gain a chance to power it on or off, or initiate a self-destruct."],
    ["Sneak", 4, "images/perks/sneak",
     "Become whisper, become shadow. You are 50% harder to detect while sneaking."],
    ["Sniper",3,"images/perks/sniper/","It's all about focus. You have improved control and can hold your breath longer when aiming with scopes."],
]

# Detect if running on a Raspberry Pi
PI = False
if os.name == "posix":
    PI = True
else:
    PI - False

pygame.font.init()
RobotoB = {}
RobotoR = {}
TechMono = {}
for x in range(10, 34):
    RobotoB[x] = pygame.font.Font('fonts/RobotoCondensed-Bold.ttf', x)
    RobotoR[x] = pygame.font.Font('fonts/RobotoCondensed-Regular.ttf', x)
    TechMono[x] = pygame.font.Font('fonts/TechMono.ttf', x)

pygame.freetype.init()
FreeRobotoB = {}
FreeRobotoR = {}
FreeTechMono = {}
for x in range(10, 34):
    FreeRobotoB[x] = pygame.freetype.Font('fonts/RobotoCondensed-Bold.ttf', x)
    FreeRobotoR[x] = pygame.freetype.Font('fonts/RobotoCondensed-Regular.ttf', x)
    FreeTechMono[x] = pygame.freetype.Font('fonts/TechMono.ttf', x)

# Get and save volume and station setting
global VOLUME
try:
    VOLUME = float(saved.SAVED_VOLUME)
except:
    VOLUME = 0.5
global STATION
try:
    STATION = int(saved.SAVED_STATION)
except:
    STATION = 0

hide_top_menu = False
hide_submenu = False
hide_main_menu = False
hide_footer = False


def save_settings():
    file = open("saved.py", "w")
    file.write("SAVED_VOLUME = " + str(VOLUME) + "\n" + "SAVED_STATION = " + str(STATION))
    print("exiting", "SAVED_VOLUME = ", str(VOLUME), "SAVED_STATION = ", str(STATION))


atexit.register(save_settings)

# Glitch the screen up/down
glitch = False
glitch_time = 0.1
glitch_next = 0



#
# # Force caching waveforms
# # This can take a very long time on a Raspberry Pi or fail completely if the song is too long.
# # I recommend running on a PC first.
# force_caching = False
#
# # Generate waveforms at song load
# do_not_use_cache = True

# Set the target frames_per_second
frame_per_second = 32
fps_rate = (1/frame_per_second)

# Waveform related:
waveform_frequency = 48000  # All your OGG files should be this rate to keep things in sync

# This is the amount of pixel scrolling the waveform does per frame. It is basically a zoom control
# A setting of 250 is the max, and close to a real-time view
waveform_rate = 48

# Setting this value too high will greatly delay song waveform generation
waveform_fps = int(frame_per_second / 2)
frame_skip = int(waveform_frequency / (waveform_fps * waveform_rate))

CURRENT_SONG = None

# Holotape related:
holotape_generic = "images\inventory\holotape"

# slow code debugger
# debug_time = time.time()
# time_past = time.time() - debug_time
# if time_past:
#     max_fps = int(1 / time_past)
#     print("Holotape render took:", time_past, "max fps:", max_fps)


