# Pentomino cube solver in python by Michael Pannekoek
from itertools import product, permutations

import numpy as np
import numba as nb
from time import perf_counter as clock

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
            hom_orients[p,l,s] = pos

@nb.njit('void(int64,int64,boolean[:,:,:])')
def removeLast(pn, i, values):
    # remove from values list
    for t in range(len(hom_orients[pn,i])):
        values[hom_orients[pn,i,t,0],hom_orients[pn,i,t,1],hom_orients[pn,i,t,2]] = False

bcords = np.array(list(product(range(bheight), range(brows), range(bcols))))

# check if coordinates are valid, unchecked and not occupied
# returns True if these conditions are all true, otherwise False
@nb.njit('b1(int64,int64,int64,boolean[:,:,:])')
def checkCoordinates(h, r, c, unchecked):
    if h < 0 or r < 0 or c < 0 or h >= bheight or r >= brows or c >= bcols:
        return False
    if unchecked[h, r, c]:
        unchecked[h, r, c] = False
        return True
    else:
        return False

@nb.njit('int64(int64,int64,int64,boolean[:,:,:])')
def floodCheck(h, r, c, unchecked):
    count = 1
    if checkCoordinates(h + 1, r, c, unchecked):
        count += floodCheck(h + 1, r, c, unchecked)
    if checkCoordinates(h, r + 1, c, unchecked):
        count += floodCheck(h, r + 1, c, unchecked)
    if checkCoordinates(h, r, c + 1, unchecked):
        count += floodCheck(h, r, c + 1, unchecked)
    if checkCoordinates(h, r - 1, c, unchecked):
        count += floodCheck(h, r - 1, c, unchecked)
    if checkCoordinates(h, r, c - 1, unchecked):
        count += floodCheck(h, r, c - 1, unchecked)
    if checkCoordinates(h - 1, r, c, unchecked):
        count += floodCheck(h - 1, r, c, unchecked)
    return count


@nb.njit('b1(boolean[:,:,:])')
def checkGaps(values):
    unchecked = ~values
    # go thorugh each unchecked position and check how large the gap is
    for i in range(bcells):
        q, c = divmod(i, bcols)
        h, r = divmod(q, brows)
        if checkCoordinates(h, r, c, unchecked):
            unchecked[h, r, c] = False
            if floodCheck(h, r, c, unchecked) % 5:
                # if the gap is too small, return True
                return True
    # if none are too small return False
    return False

@nb.njit('b1(int64,int64,boolean[:,:,:])')
def add(pn, i, values):
    # returns True if piece is in a valid position, otherwise  False
    # and in the process adds the piece.
    # first find the piece representation
    # check if piece fits in values
    for t in range(len(hom_orients[pn,i])):
        if values[hom_orients[pn,i,t,0],hom_orients[pn,i,t,1],hom_orients[pn,i,t,2]]:
            return False
    # then add to placements and values
    for t in range(len(hom_orients[pn,i])):
        values[hom_orients[pn,i,t,0],hom_orients[pn,i,t,1],hom_orients[pn,i,t,2]] = True
    # check if there are any gaps too small
    if checkGaps(values):
        removeLast(pn, i, values)
        return False
    return True

# function that runs through every piece, orientation and position
# adding one piece at a time and removing
@nb.njit('int64(int64,int64,boolean[:,:,:])')
    if solcount >= 30:
def try_piece(pn, solcount, values):
        return solcount
    for i in range(len(hom_orients[pn])):
        if hom_orients[pn,i,0,0] < 0:
            break
        if add(pn, i, values):
            if pn == 11:
                solcount += 1
                with nb.objmode:
                    print(f'soln: {solcount} at {solcount / (clock()-start_time)} slns/s')
                removeLast(pn, i, values)
                return solcount
            else:
                solcount = try_piece(pn + 1, solcount, values)
            removeLast(pn, i, values)
    return solcount

@nb.njit()
def doSolve():
    values = np.zeros((bheight, brows, bcols), dtype=np.bool_)
    try_piece(nb.int64(0), nb.int64(0), values)

def solve():
    global start_time
    start_time = clock()
    doSolve()
    print(f'finished in {(clock()-start_time)/60} minutes')

if __name__ == '__main__':
    # start solving
    solve()
