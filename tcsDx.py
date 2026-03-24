# Tetris cube solver in python by Michael Pannekoek
from __future__ import absolute_import, print_function
from TetrisC import transform, check
from itertools import product, permutations
import numba
import numpy as np
from tqdm import tqdm
try:
    range = xrange
except NameError:
    pass
from time import time

# depends on Algorithm-x
# (an implementation by github.com/SuprDewd
# of Algorithm X by Donald Knuth)
## added custom optimized implementation using numba
from aXf import AlgorithmX


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

# board dimensions
bheight = 3
brows = 4
bcols = 5

bcells = bheight * brows * bcols

pieces = [
          # 0
          [['1..',
            '1..',
            '111']],
          
          # 1
          [['1..',
            '11.',
            '.11']],

          # 2
          [['11.',
            '.11',
            '.1.']],
          
          # 3
          [['.1.',
            '111',
            '.1.']],
          
          # 4
          [['.1',
            '11',
            '.1',
            '.1']],
          
          # 5
          [['1.',
            '11',
            '.1',
            '.1']],
          
          # 6
          [['.1.',
            '.1.',
            '111']],
          
          # 7
          [['1..',
            '111',
            '..1']],

          # 8
          [['11',
            '.1',
            '.1',
            '.1']],

          # 9
          [['11',
            '1.',
            '11']],

          # 10 or A
          [['1.',
            '11',
            '11']],

          # 11 or B
          [['11111']]]

# A function that returns a new piece, with the dimensions of the input piece
# plotted to the axes inputted in the order stated in negatives list input
def transform(piece, axes, negatives):
    base = []
    for h, layer in enumerate(piece):
        for r, row in enumerate(layer):
            for c, item in enumerate(row):
                if item == '1':
                    base.append((h, r, c))
    arr = np.array(base)
    dim = np.max(arr, axis=0)
    axesI = [0] * 3
    for i in range(3):
        axesI[axes[i]] = i
    arr = arr[:,axesI]
    newdim = dim[axesI]
    for i, neg in enumerate(negatives):
        if neg == 1:
            arr[:,i] = newdim[i] - arr[:,i]
    new = []
    ph, pr, pc = newdim
    for x in product(range(bheight-ph), range(brows-pr), range(bcols-pc)):
        new.append(np.array(x) + arr)
    return new

# check if a 3D piece is invalid, or contained in a list or not
def check(piece, array):
    if len(piece) == 0:
        return False
    pa = set(tuple(c) for c in piece[0])
    if pa in [set(tuple(c) for c in piece[0]) for piece in array]:
        return False
    return True

orientations = []

# find all different piece orientations
for piece in pieces:
    nextPiece = []
    orientation = transform(piece, (0,1,2), [0, 0, 0])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (0,1,2), [1, 1, 0])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (0,1,2), [1, 0, 1])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (0,1,2), [0, 1, 1])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (1,2,0), [0, 0, 0])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (1,2,0), [1, 1, 0])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (1,2,0), [1, 0, 1])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (1,2,0), [0, 1, 1])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (2,0,1), [0, 0, 0])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (2,0,1), [1, 1, 0])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (2,0,1), [1, 0, 1])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (2,0,1), [0, 1, 1])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    
    orientation = transform(piece, (2,1,0), [1, 0, 0])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (2,1,0), [0, 1, 0])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (2,1,0), [0, 0, 1])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (2,1,0), [1, 1, 1])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (1,0,2), [1, 0, 0])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (1,0,2), [0, 1, 0])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (1,0,2), [0, 0, 1])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (1,0,2), [1, 1, 1])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (0,2,1), [1, 0, 0])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (0,2,1), [0, 1, 0])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (0,2,1), [0, 0, 1])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientation = transform(piece, (0,2,1), [1, 1, 1])
    if check(orientation, nextPiece):
        nextPiece.append(orientation)
    orientations.append(sum(nextPiece, []))

hom_orients = np.ones((len(orientations), max(len(v) for v in orientations), max(len(v) for v in orientations[0])), dtype=(np.int64, 3))*-1
for p, piece in enumerate(orientations):
    for l, loc in enumerate(piece):
        for s, pos in enumerate(loc):
            hom_orients[p][l][s] = pos

def get_wrapped_index(h, r, c):
    return c + r * bcols + h * brows * bcols


def unwrap_index(i):
    hr, c = divmod(i, bcols)
    h, r = divmod(hr, brows)
    return (h, r, c)


piece_rows = []

for piece in orientations:
    piece_l = []
    for orient in piece:
        piece_l.append([get_wrapped_index(h, r, c) for h, r, c in orient])
    piece_rows.append(piece_l)

solver = AlgorithmX(bcells + len(pieces))
for i, piece_placements in enumerate(piece_rows):
    for piece_placement in piece_placements:
        solver.appendRow(piece_placement + [i+bcells], np.array(piece_placement, dtype=np.int64))

with open('tcsDXsolutions.txt', 'w') as f:
    start = time()
    for i, solution in tqdm(enumerate(solver.solve()), smoothing=0, unit=' sols'):
        print(solution, file=f)
    print('Solutions found:', i+1)
    print('Time:', time() - start)
    print('Solutions per second:', (i+1) / (time() - start))
