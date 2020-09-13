#!/usr/bin/env python3

"""rules of 2048 game + auxiliary functions"""

DIRECTIONS = tuple(range(4))
DOWN, LEFT, RIGHT, UP = DIRECTIONS
DIR_NAME = ('DOWN', 'LEFT', 'RIGHT', 'UP')
SIZE = 4  # board size
LAST = SIZE - 1


# PERMUTATIONS
   
IDENTITY = tuple(tuple((i, j) for j in range(SIZE)) for i in range(SIZE))
MIRROR = tuple(tuple((i, j) for j in reversed(range(SIZE))) for i in range(SIZE))
TRANSPOSE = tuple(tuple((j, i) for j in range(SIZE)) for i in range(SIZE))
ANTITRANS = tuple(tuple((j, i) for j in reversed(range(SIZE))) for i in reversed(range(SIZE)))

PERM = (ANTITRANS, # DOWN
        IDENTITY,  # LEFT
        MIRROR,    # RIGHT
        TRANSPOSE)  # UP


# A few predefined boards

EMPTYBOARD = [[0] * SIZE for _ in range(SIZE)]

STEP0 = [[0, 0, 0, 0],
         [0, 0, 0, 0],
         [0, 0, 0, 0],
         [3, 2, 0, 0]]

FULLBOARD = [[1, 2, 3, 4],
             [5, 6, 7, 8],
             [9, 10, 11, 12],
             [13, 14, 15, 16]]

XFULLBOARD = [[1, 2, 3, 4],
              [2, 3, 4, 5],
              [3, 4, 3, 2],
              [4, 1, 5, 5]
]

FINAL1 = [[2, 4, 5, 2],
          [9, 8, 7, 4],
          [10, 11, 12, 13],
          [17, 16, 15, 14]]


def move_tile(new_tile_move, board):
    """set on a new tile on the board
       'new_tile_move' is given as a triple (i,j,log2_value)
       where (i,j) is the position of the tile
       and 2**log2_value is the value of the tile"""
    i, j, log2_value = new_tile_move
    if not ((log2_value == 1 or log2_value == 2) and board[i][j] == 0):
        raise AssertionError
    board[i][j] = log2_value


def is_full(board):
    """test whether the board has no empty cell"""
    for l in board:
        for v in l:
            if v == 0:
                return False
    return True

def slide_is_possible(board, i, perm=IDENTITY):
    """test whether a LEFT move_dir applied to line 'i' is possible 
       on the 'board' permutated by 'perm'

       contents follows the log convention:
       0 means "empty cell" and N>0 means "cell containing 2 ** N".
    """
    
    for j in range(LAST):
    #-------------- Généralisation -----------------
        i_perm, j_perm = perm[i][j]
        i_suivant, j_suivant = perm[i][j+1]
    #-----------------------------------------------
        case_courante, case_suivante = board[i_perm][j_perm], board[i_suivant][j_suivant]
        if (case_courante == 0 and case_suivante != 0) or (case_courante == case_suivante != 0):
            return True
        
    return False

def move_dir_possible(direction, board):
    """test whether a move_dir applied on board is possible."""

    return any((slide_is_possible(board, i, PERM[direction]) for i in range(SIZE)))

def game_over(board):
    """check if a direction can be played !
       PRECONDITION: the board is not empty !
    """
    
    return all([not move_dir_possible(direction, board) for direction in range(SIZE)])


def slide(in_board, out_board, i, perm=IDENTITY):
    """performs the slide inside board (for the same slide than in 
       slide_is_possible(board, i, perm)
       
    For example, if the line was initially [2, 2, 0, 0]
    then it becomes [3, 0, 0, 0].

    Returns True iff 'board' has changed
    """
    
    changement = False

    ligne = list(val for val in (out_board[perm[i][j][0]][perm[i][j][1]] for j in range(SIZE)) if val != 0) #Removes all the 0
    while len(ligne) < SIZE:
        ligne.append(0) #Adds the new 0 at the end

    #Adds the numbers together

    case = 0
    while case <= LAST - 1:
        if ligne[case] != 0 and ligne[case] == ligne[case + 1]:
            ligne[case] += 1
            ligne.pop(case + 1)
            ligne.append(0)
        case += 1
    
    #Updates out_board

    for j in range(SIZE):
        i_perm, j_perm = perm[i][j]
        if out_board[i_perm][j_perm] != ligne[j]:
            changement = True
            out_board[i_perm][j_perm] = ligne[j]
    
    return changement

def move_dir(direction, board):
    """Returns a board resulting from the slide of 'board'
       according to 'direction'.
       'board' remains unchanged.
       The resulting board 'res' satisfies 'res == board' iff 'res is board'
    """
    
    res = [line.copy() for line in board]
    return res if any([slide(board, res, i, PERM[direction]) for i in range(SIZE)]) else board

def compte_horiz(board):
    score = 0
    
    for line in board:
        j = 0
        while j < len(line) - 1:
            cour = line[j]
            if cour != 0:
                if cour == line[j + 1]:
                    score += 9**(2*cour - 1)
                    j += 1
                else:
                    score += 9**(2*(cour-1))
            j += 1
        
        last = line[-1]
        if last != 0 and j < len(line):
            score +=  9 ** (2*(last - 1))
      
    return score

def level(board):
    dplc_h = compte_horiz(board)
    transpose = [list(elt) for elt in zip(*board)]
    return max(dplc_h, compte_horiz(transpose))


def max_tile(board):
    """return the max tile on the board."""

    res = 0
    for l in board:
        for v in l:
            if v > res:
                res = v
    return res


def score(board):
    res = max_tile(board)
    if res == 0:
        return res
    return 1 << res  # equiv to 2 ** res


# -- Example of observer for play2048 below
# This function is blocking for play2048
# For example:
#  'input' function below waits a response of the user;
#  in the meanwhile, the GUI is stopped and no more responsive to events !


log = 0
PLAYER_NAME = ('TILE', 'DIRECTION')


def observer_example(board, player):
    """player is the next player in play2048.py"""
    global log
    v = max_tile(board)
    if v > log:
        print('reach', 1 << v, ' on board: ', board)
        print('next player is:', PLAYER_NAME[player])
        log = v
        input('press return to continue --')

