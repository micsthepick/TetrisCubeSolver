# Tetris cube solver in python by Michael Pannekoek
from __future__ import absolute_import, print_function
from TetrisC import transform, check
from itertools import product, permutations
from tqdm import tqdm
import datetime
from time import time_ns
if 'xrange' in globals():
    range = globals()['xrange']

# depends on Algorithm-x
# (an implementation by github.com/SuprDewd
# of Algorithm X by Donald Knuth)
from algorithm_x import AlgorithmX


# board dimensions
bheight = 4
brows = 4
bcols = 4

bcells = bheight * brows * bcols

pieces = [
    # 0
    [['1..', '1..', '111'], ['...', '1..', '...']],

    # 1
    [['1..', '1..', '111'], ['1..', '...', '...']],

    # 2
    [['11.', '.11', '.1.'], ['1..', '...', '...']],

    # 3
    [['.1.', '...'], ['111', '.1.'], ['...', '.1.']],

    # 4
    [['.1', '11', '.1', '.1']],

    # 5
    [['1.', '11', '.1', '.1']],

    # 6
    [['1..', '1..', '111']],

    # 7
    [['1.', '11', '..'], ['..', '.1', '.1']],

    # 8
    [['.1.', '...'], ['.1.', '111']],

    # 9
    [['11', '1.', '1.'], ['.1', '..', '..']],

    # 10 or A
    [['1.', '11', '.1'], ['..', '..', '.1']],

    # 11 or B
    [['1.', '..'], ['11', '11']]
]

orientations = [[pieces[0]]]

# find all different piece orientations, except for first piece
# (skip first piece so that it every solution appears in only one orientation)
# ASSUMES that first piece has 24 orientations, i.e. no rotational symmetry!!!
for piece in pieces[1:]:
    nextPiece = []
    for perm in permutations(list(range(3))):
        if perm[0] - perm[1] in [-1, 2]:
            # all positive in order
            negatives = [0] * 3
            orientation = transform(piece, perm, negatives)
            if not check(orientation, nextPiece):
                nextPiece.append(orientation)
            for i in range(3):
                # all negative except i
                negatives = [1] * 3
                negatives[i] = 0
                orientation = transform(piece, perm, negatives)
                if not check(orientation, nextPiece):
                    nextPiece.append(orientation)
        else:
            # all negative in order
            negatives = [1] * 3
            orientation = transform(piece, perm, negatives)
            if not check(orientation, nextPiece):
                nextPiece.append(orientation)
            for i in range(3):
                # all positive except i
                negatives = [0] * 3
                negatives[i] = 1
                orientation = transform(piece, perm, negatives)
                if not check(orientation, nextPiece):
                    nextPiece.append(orientation)
    orientations.append(nextPiece)


def get_wrapped_index(h, r, c):
    return c + r * bcols + h * brows * bcols


def unwrap_index(i):
    hr, c = divmod(i, bcols)
    h, r = divmod(hr, brows)
    return (h, r, c)


piece_rows = []

for p_i, piece in enumerate(orientations):
    piece_l = []
    for o_i, orient in enumerate(piece):
        hl, rl, cl = len(orient), len(orient[0]), len(orient[0][0])
        t_i = 0
        for h, r, c in product(
                range(bheight - hl + 1),
                range(brows - rl + 1), range(bcols - cl + 1)):
            row = []
            for x, y, z in product(range(hl), range(rl), range(cl)):
                if orient[x][y][z] == '1':
                    # link to last
                    # data = (index, piece id, orientation id)
                    # TODO: may want to change this to just index?
                    row.append(get_wrapped_index(h + x, r + y, c + z))
            piece_l.append(row)
    piece_rows.append(piece_l)

solver = AlgorithmX(bcells + len(pieces))
for i, piece_placements in enumerate(piece_rows):
    for piece_placement in piece_placements:
        solver.appendRow(piece_placement + [i + bcells], piece_placement)

with open('tcsDXsolutions.txt', 'w') as f:
    start = time_ns()
    for i, solution in tqdm(enumerate(solver.solve()), unit=' sols'):
        print(solution, file=f)
    print(
        '\nTime:',
        datetime.timedelta(milliseconds=(time_ns() - start) // 1000000)
    )
