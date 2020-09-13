"""Configutation file for play2048 and mean_score"""

import rules
import players

DEPTH = 3

# --- INITIAL BOARD ----------
INIT_BOARD = rules.EMPTYBOARD
# INIT_BOARD = rules.STEP0
# INIT_BOARD = rules.XFULLBOARD
# INIT_BOARD = [[0, 0, 0, 2], [0, 0, 0, 3], [0, 0, 3, 5], [12, 11, 9, 6]]

# --- FIRST PLAYER -------
FIRST_PLAYER = 0  # for PLAYER TILE
# FIRST_PLAYER = 1  # for PLAYER DIRECTION


# --- TILE PLAYER ----------------------
# TILE_PLAYER = None # means interactive (for play2048 only)
TILE_PLAYER = players.random_tile
#TILE_PLAYER = players.first_tile
#TILE_PLAYER = players.basic_coop_tile
#TILE_PLAYER = players.coop_tile


# --- DIRECTION PLAYER -----------------
#DIRECTION_PLAYER = None # means interactive (for play2048 only)
#DIRECTION_PLAYER = players.random_direction
#DIRECTION_PLAYER = players.first_direction
DIRECTION_PLAYER = players.basic_coop_direction
#DIRECTION_PLAYER = players.coop_direction

# --- OBSERVER (to debug player2048) -------
OBSERVER = None  # for nothing
# OBSERVER = rules.observer_example

# --- GUI DETAILS (for play2048 only) ------------------
WAIT_DURATION = 0  # 1000 # 50 # 1000 # time in miliseconds between players

TILE_SIZE = 140  # pixels
TILE_SEP = 5  # pixels
SENSITIVE = 2 * TILE_SEP  # precision of "touch move" on the board

HELP_ON_CONSOLE = False  # or True in order to avoid help pop-up
FONT_HELP = "Helvetica 16"


# --- NUMBER of GAMES (for mean_score only) -----------------
GAMES_NUMBER = 100  # 5 # 1000