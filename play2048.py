#! /usr/bin/env python3
"""
Graphic User Interface to play to '2048'
See config.py to tune players mode.
"""


# --- imports ---------------------------------------------------

#
import os
import tkinter
import traceback
from collections import defaultdict

import rules
import config

# NB: automatic strategies are run into in a separate process
# This is faster and makes the GUI more reactive !
# import multiprocessing
from multiprocessing import Process, Value

import sys
if os.name == 'nt':
    sys.path.append(os.path.dirname(__file__))


# --- constants --------------------------------------------------
# colors from http://gabrielecirulli.github.io/2048/style/main.css
COLORS = defaultdict(
    lambda: ("#3c3a32", "#f9f6f2"), {
        0: ("#ccc0b4", "#776e65"),
        2: ("#eee4da", "#776e65"),
        4: ("#ede0c8", "#776e65"),
        8: ("#f2b179", "#f9f6f2"),
        16: ("#f59563", "#f9f6f2"),
        32: ("#f67c5f", "#f9f6f2"),
        64: ("#f65e3b", "#f9f6f2"),
        128: ("#edcf72", "#f9f6f2"),
        256: ("#edcc61", "#f9f6f2"),
        512: ("#edc850", "#f9f6f2"),
        1024: ("#edc53f", "#f9f6f2"),
        2048: ("#edc22e", "#f9f6f2"),
    })

FONT = "Helvetica 55 bold"
FONT1 = "Helvetica 44 bold"
FONT2 = "Helvetica 32 bold"
FONT3 = "Helvetica 26 bold"

# building the window

BACKGROUND_COLOR = "#bbada0"


PLAYERS = tuple(range(3))
PLAY_TILE, PLAY_DIR, GAME_OVER = PLAYERS
PLAYER_NAME = "TILE", "DIRECTION", "GAME OVER"
RUN_PLAYER = config.TILE_PLAYER, config.DIRECTION_PLAYER
IS_OVER = rules.is_full, rules.game_over
player = config.FIRST_PLAYER

# windows
window = tkinter.Tk()
helper = None
askplayer_helper = False


autoplayer = None     # Process for "automatic player"
autoplayer_res = Value('i', -2)  # Result (shared object) of autoplayer

board = config.INIT_BOARD
tiles = None  # grid window of the tiles
num_tiles = 0

# 1 millisecond is the minimum
config.WAIT_DURATION = max(1, config.WAIT_DURATION)


# ---------------------------
#  Windows and their contents


def close_on_error():
    """display the current error trace on console and exit"""
    traceback.print_exc()
    sys.stderr.flush()
    window.destroy()


def update_helper(info, askplayer=False):
    """Default helper with a pop-up"""
    global helper, askplayer_helper
    if helper is not None:
        helper.destroy()
    askplayer_helper = askplayer
    helper = tkinter.Toplevel(window)
    helper.title("play2048 help")
    helper.protocol("WM_DELETE_WINDOW", destroy_helper)
    helper.configure(bg="#f9f6f2")
    msg = tkinter.Message(helper,
                          text=info,
                          font=config.FONT_HELP,
                          bg="#f9f6f2",
                          aspect=500
                          )
    msg.pack()


def destroy_helper():
    global helper, askplayer_helper
    if helper is None:
        return
    helper.destroy()
    helper = None
    askplayer_helper = False


def update_helper_console(info, askplayer=False):
    """Alternative help, using console instead of a pop-up"""
    global askplayer_helper
    askplayer_helper = askplayer
    print()
    print(info)
    sys.stdout.flush()


def start():
    global tiles, player, update_helper
    assert player == PLAY_TILE or player == PLAY_DIR
    window.configure(bg=BACKGROUND_COLOR, border=config.TILE_SEP)
    window.resizable(0, 0)
    tiles = [[Tile(i, j) for j in range(rules.SIZE)]
             for i in range(rules.SIZE)]
    update()
    if config.DIRECTION_PLAYER is None or config.TILE_PLAYER is None:
        window.bind_all("<ButtonPress-1>", button1_press)
        window.bind_all("<ButtonRelease-1>", button1_release)
        if config.DIRECTION_PLAYER is None:
            window.bind_all("<Left>", key_press(rules.LEFT))
            window.bind_all("<Right>", key_press(rules.RIGHT))
            window.bind_all("<Up>", key_press(rules.UP))
            window.bind_all("<Down>", key_press(rules.DOWN))
    if config.HELP_ON_CONSOLE:
        update_helper = update_helper_console
    if board == rules.EMPTYBOARD:
        if player == PLAY_DIR:
            update_helper(
                "Config error: DIRECTION cannot be first player on empty board.")
        player = PLAY_TILE
    elif IS_OVER[player](board):
        player = GAME_OVER
    run_next_player()
    window.mainloop()


class MyLabel(tkinter.Label):

    def __init__(self, tile):
        super().__init__(tile, font=FONT)
        self.tile = tile
        self.place(anchor="c", relx=.5, rely=.52)

    def coord(self):
        return self.tile.coord()


class Tile(tkinter.Frame):
    """Class of tiles widget on the grid """

    def __init__(self, i, j):
        super().__init__(window,
                         width=config.TILE_SIZE,
                         height=config.TILE_SIZE)
        self.grid(row=i, column=j,
                  padx=config.TILE_SEP,
                  pady=config.TILE_SEP)
        self.label = MyLabel(self)
        self.i = i
        self.j = j

    def update_from_board(self):
        v = board[self.i][self.j]
        if v != 0:
            v = 1 << v
        if player == GAME_OVER:
            fg, bg = COLORS[v]
        else:
            bg, fg = COLORS[v]
        self.label.configure(bg=bg, fg=fg,
                             text=str(v) if v else "",
                             font=get_font(v))
        self.configure(bg=bg)

    def coord(self):
        return (self.i, self.j)


def get_font(v):
    """font of tile with value v"""
    if v < 100:
        return FONT
    elif v < 1000:
        return FONT1
    elif v < 100000:
        return FONT2
    else:
        return FONT3


def update():
    """Update the display from the current board"""
    for r in tiles:
        for t in r:
            t.update_from_board()


# ---------------------------
# automatic players

def autoplayer_dir(board, strategy, res):
    """run a direction strategy and put its result in res.value"""
    try:
        res.value = strategy(board)
        assert res.value >= 0
    except:
        traceback.print_exc()
        res.value = -1


def autoplayer_tile(board, strategy, res):
    """run a tile strategy and put its result in res.value"""
    try:
        i, j, k = strategy(board)
        res.value = i * 8 + j * 2 + k - 1
        assert res.value >= 0
    except:
        traceback.print_exc()
        res.value = -1


AUTOPLAYER = autoplayer_tile, autoplayer_dir


def move_autoplay_dir():
    """move direction according to value in autoplayer_res.value"""
    d = autoplayer_res.value
    if d < 0:
        if d == -1:
            update_helper("Direction player failed !\n" +
                          "See error trace on console\n")
        else:
            update_helper("Automatic player has been interrupted !\n")
        close_on_error()
        return
    try:
        move_dir(d)
    except:
        close_on_error()


def move_autoplay_tile():
    """move tile according to value in autoplayer_res.value"""
    r = autoplayer_res.value
    if r < 0:
        if r == -1:
            update_helper("Tile player failed !\n" +
                          "See error trace on console\n")
        else:
            update_helper("Automatic player has been interrupted !\n")
        close_on_error()
        return
    i = r // 8
    j = (r // 2) % 4
    k = (r % 2) + 1
    try:
        move_tile((i, j, k))
    except:
        close_on_error()


MOVE = move_autoplay_tile, move_autoplay_dir

# time in microsecond to check autoplayer process
AUTOPLAYER_REACT = min(config.WAIT_DURATION, 50)


def wait_autoplayer():
    """Check the activity of autoplayer process, and update GUI accordingly"""
    global autoplayer
    if autoplayer is None:
        return
    if autoplayer.is_alive():
        window.after(AUTOPLAYER_REACT, wait_autoplayer)
        return
    autoplayer = None
    MOVE[player]()


def start_autoplayer():
    """Start the autoplayer process, and wait it !"""
    global autoplayer
    assert autoplayer is None
    strategy = RUN_PLAYER[player]
    assert strategy is not None
    autoplayer_res.value = -2
    autoplayer = Process(target=AUTOPLAYER[player],
                         args=(board,
                               strategy,
                               autoplayer_res))
    autoplayer.start()
    window.after(config.WAIT_DURATION, wait_autoplayer)


# Currently, useless
#
# def kill_autoplayer():
#    global autoplayer
#    if autoplayer is not None and autoplayer.is_alive():
#        update
#        autoplayer.terminate()
#        autoplayer.join()
#        autoplayer = None

# -------------------------------
# handling button and key events


# state variable indicating whether the user is expected to emit some event
# invariant:
#  is_interactive <=> (player != GAME_OVER and RUN_PLAYER[player] is None)
is_interactive = False


def interactive():
    global is_interactive
    sys.stdout.flush()
    is_interactive = True


def uninteractive():
    global is_interactive
    sys.stdout.flush()
    is_interactive = False


HELP_TILE = \
    "TO PLAY A TILE: first touch an empty tile on the board, then move LEFT for a 2, or move RIGHT for a 4 (while still touching the board)."

HELP_DIRECTION = \
    "TO PLAY A DIRECTION: move DOWN or LEFT or UP or RIGHT, while touching the board."

HELP_INTERACTIVE = HELP_TILE, HELP_DIRECTION


def help_interactive(error=None):
    if error is not None:
        msg = "ERROR: " + error + "!\n"
    else:
        msg = ""
    update_helper(msg + HELP_INTERACTIVE[player])


def help_noninteractive():
    global autoplayer_helper
    if player == GAME_OVER:
        update_helper("The game is over. The max tile is {0}. You can safely close the board...".format(
            rules.score(board)))
        return
    if autoplayer is not None and autoplayer.is_alive():
        update_helper("Current player {0} is a bit slow to play... Please wait !".format(
            PLAYER_NAME[player]), True)


def key_press(direction):
    def callback(event):
        destroy_helper()
        if not is_interactive:
            help_noninteractive()
            return
        if player == PLAY_TILE:
            update_helper(
                "ERROR: you cannot play a tile on keyboard!\n" + HELP_TILE)
            return
        assert player == PLAY_DIR
        move_dir(direction)
    return callback


press_tile, press_x, press_y = None, None, None


def button1_press(event):
    global press_tile, press_x, press_y
    destroy_helper()
    if not is_interactive:
        return  # help given on button release, below !
    press_tile = event.widget
    press_x = event.x
    press_y = event.y


def move_tile_from_direction(direction):
    "move tile according to a direction on a button release (see below)."
    if type(press_tile) is not Tile:
        help_interactive("You have not touched a tile of the board")
        return  # invalid move !
    (i, j) = press_tile.coord()  # press_tile from button1_press
    if board[i][j] != 0:
        help_interactive("Tile {0} is not empty".format((i, j)))
        return
    if direction != rules.LEFT and direction != rules.RIGHT:
        help_interactive("Cannot  dectect a LEFT or RIGHT move")
        return
    # We have now a valid move !
    if direction == rules.LEFT:
        value = 1
    else:
        value = 2
    move_tile((i, j, value))


def button1_release(event):
    global press_x, press_y
    if not is_interactive:
        help_noninteractive()
        return
    try:
        delta_x = event.x - press_x
        delta_y = event.y - press_y
    except:
        help_interactive("Cannot detect a valid move")
        return
    d = abs(delta_x) - abs(delta_y)
    press_x, press_y = None, None
    if abs(d) <= config.SENSITIVE:
        help_interactive("Cannot detect a valid move")
        return
    if d > 0:
        if delta_x > 0:
            direction = rules.RIGHT
        else:
            assert delta_x < 0
            direction = rules.LEFT
    elif delta_y > 0:
        direction = rules.DOWN
    else:
        assert delta_y < 0
        direction = rules.UP
    if player == PLAY_TILE:
        move_tile_from_direction(direction)
    elif player == PLAY_DIR:
        move_dir(direction)


# ---------------------------
# game automaton


def move_dir(direction):
    global player, board
    old = board
    board = rules.move_dir(direction, old)
    if board is old:
        if is_interactive:
            help_interactive("direction {0} does not change the board".format(
                rules.DIR_NAME[direction]))
        else:
            print("ERROR: direction {0} is invalid !".format(
                rules.DIR_NAME[direction]))
            assert False
    else:
        update()
        player = PLAY_TILE
    run_next_player()


def move_tile(move):
    global player, num_tiles
    num_tiles += 1
    rules.move_tile(move, board)
    tiles[move[0]][move[1]].update_from_board()
    if rules.game_over(board):
        player = GAME_OVER
    else:
        player = PLAY_DIR
    run_next_player()


def run_next_player():
    window.wm_title("play2048 -- num tiles={0} -- next player={1}".format(
        num_tiles,
        PLAYER_NAME[player]))
    if player == GAME_OVER:
        uninteractive()
        window.configure(bg="#880000")
        update()
        if askplayer_helper:
            update_helper("Now, game is over !")
        return
    if config.OBSERVER is not None:
        try:
            config.OBSERVER(board, player)
        except:
            close_on_error()
    if RUN_PLAYER[player] is None:
        interactive()
        if askplayer_helper:
            update_helper("Now, please, play a {0}...".format(
                PLAYER_NAME[player]))
        return
    uninteractive()
    start_autoplayer()


if __name__ == "__main__":
    start()
    print()
    print("Exit on board:", board)
    print("num tiles={0} -- next player={1}".format(
            num_tiles,
            PLAYER_NAME[player]))
