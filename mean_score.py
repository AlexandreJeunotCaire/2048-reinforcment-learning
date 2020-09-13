#! /usr/bin/env python3
"""
Compute the average score to '2048' between automatic players.
"""

import rules
import config
import time


def game_direction_first(dir_player, tile_player, board):
    i = 0
    while not rules.game_over(board):
        direction = dir_player(board)
        assert(direction is not None) #On peut jouer
        assert(0 <= direction < 4) #On ne peut jouer que 4 directions
        assert(rules.move_dir_possible(direction, board))
        board = rules.move_dir(direction, board)
        tuile = tile_player(board)
        assert(tuile is not None)
        rules.move_tile(tuile, board)
        i += 1
    return (1 << rules.max_tile(board), i) #1 << a is 2 ** a


def game_tile_first(dir_player, tile_player, board):
    tab = [line.copy() for line in board]
    if rules.is_full(board):
        return (1 << rules.max_tile(board), 0)
    
    if tile_player(tab) is not None:
        rules.move_tile(tile_player(tab), tab)
    
    tuile_max, nombre_coups = game_direction_first(dir_player, tile_player, tab)
    return tuile_max, nombre_coups + 1


def mean_score():
    if config.FIRST_PLAYER == 0:
        game = game_tile_first
    else:
        game = game_direction_first
        # NB: direction can not start the game on a empty board !
        assert (config.INIT_BOARD != rules.EMPTYBOARD)
    # NB: no interactive players here !
    assert config.TILE_PLAYER is not None
    assert config.DIRECTION_PLAYER is not None
    n = 0
    s = 0
    best = 0
    nbest = 0
    worst = None
    nworst = 0
    INIT_TIME = time.time()
    for i in range(config.GAMES_NUMBER):
        print("running game:", i + 1)
        ss, nn = game(config.DIRECTION_PLAYER,
                      config.TILE_PLAYER,
                      config.INIT_BOARD)
        n += nn
        s += ss
        if ss > best:
            best = ss
            nbest = 1
        elif ss == best:
            nbest += 1
        if worst is None or ss < worst:
            worst = ss
            nworst = 1
        elif ss == worst:
            nworst += 1
    print("TOTAL TIME:", time.time() - INIT_TIME)
    print("MEAN MAX TILE:{0} -- MEAN TILE NUMBER: {1}".format(
        s / config.GAMES_NUMBER,
        n / config.GAMES_NUMBER))
    print("MAX of MAX TILE:{0} -- PROBA: {1}".format(
        best,
        nbest / config.GAMES_NUMBER))
    print("MIN of MAX TILE:{0} -- PROBA: {1}".format(
        worst,
        nworst / config.GAMES_NUMBER))


# CODE TO RUN when the file is used as a single executable
if __name__ == "__main__":
    mean_score()

