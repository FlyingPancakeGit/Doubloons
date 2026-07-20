import pygame

import os
import sys
import math
import random
import copy
import csv
import numpy as np


# setup
pygame.init()

# constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1260, 840
TILE_SIZE = 128

DRAG_FACTOR = 1

PORT = 'port'
STARBOARD = 'starboard'

# graphics
FONT = pygame.font.Font('graphics/fonts/comic_sans.ttf', 24)
SMALL_FONT = pygame.font.Font('graphics/fonts/comic_sans.ttf', 16)
LARGE_FONT = pygame.font.Font('graphics/fonts/comic_sans.ttf', 72)

# colours
SEA = (0, 187, 221)
SEA_FOAM = (200, 200, 200)
SAND = (248, 232, 91)
BORDER_SAND = (228, 212, 70)
GRASS = (69, 242, 94)
BORDER_GRASS = (45, 195, 67)

TEXT_BOX_BLACK = (50, 50, 50)
TEXT_BOX_GREY = (100, 100, 100)
TEXT_BOX_RED = (255, 105, 97)

RARITY_COLOURS = {
    'common': (200, 200, 200),
    'uncommon': (128, 255, 124),
    'rare': (124, 249, 255),
    'epic': (255, 124, 253),
    'legendary': (255, 173, 78)
}

RARITY_LOOKUP = {
    'common': 1,
    'uncommon': 1.5,
    'rare': 2,
    'epic': 2.5,
    'legendary': 3
}

# map

# islands
ISLAND_SPAWN_DIST = 100000

DESERTED_ISLAND_SIZE = 800
MERCHANT_ISLAND_SIZE = 1200
