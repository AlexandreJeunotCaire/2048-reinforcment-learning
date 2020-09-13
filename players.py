# -*- coding: utf-8 -*-

import rules
import random
import config

VALS = (1, 1, 1, 1, 1, 1, 1, 1, 1, 2)

def cases_possibles(board):
    return [(i, j) for i, line in enumerate(board) for j, col in enumerate(line) if col == 0] #Liste les cases sur lesquelles on pourra placer une tuile

def random_direction(board):
    l = [d for d in rules.DIRECTIONS if rules.move_dir_possible(d, board)]
    if l:
        return random.choice(l)


def random_tile(board):
    possible = cases_possibles(board) 
    if possible:
        coup = random.choice(VALS)
        case = random.choice(possible)
        return (case[0], case[1], coup)


def first_direction(board):
    for d in rules.DIRECTIONS:
        if rules.move_dir_possible(d, board):
            return d


def first_tile(board):
    for i in range(rules.LAST, -1, -1):
        for j in range(rules.LAST, -1, -1):
            if board[i][j] == 0:
                return (i, j, 2)

#----------------------------basic------------------------------

def basic_coop_direction(board):
    possibles = [d for d in rules.DIRECTIONS if rules.move_dir_possible(d, board)]

    if possibles != [3] and 3 in possibles:
        possibles.remove(3) #Ne jamais jouer haut quand on peut l'éviter
     
    score = {basic_coop_score(rules.move_dir(d, board)): d for d in possibles}
    
    return score[max(score)]

def basic_coop_tile(board):

    top_score = 0
    i_max, j_max = 0, 0
    for i, line in enumerate(board):
        for j, valeur in enumerate(line):
            if valeur == 0:
                board[i][j] = 2
                test = basic_coop_score(board)
                board[i][j] = 0
                if top_score < test:
                    top_score = test
                    i_max, j_max = i, j
    
    return (i_max, j_max, 2)

def basic_coop_score(board):
    return rules.level(board)