# Pentomino cube solver in python by Michael Pannekoek
from itertools import product, permutations

from copy import deepcopy
import numpy as np
import numba as nb


# board dimensions
bheight = 3
brows = 4
bcols = 5

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
    hl = len(piece)
    rl = len(piece[0])
    cl = len(piece[0][0])
    dim = [hl, rl, cl]
    hn, rn, cn = axes
    nAxes = []
    axesI = [0] * 3
    for i in range(3):
        axesI[axes[i]] = i
        if negatives[i] == 0:
            nAxes.append(range(dim[axes[i]]))
        else:
            nAxes.append(range(dim[axes[i]] - 1, -1, -1))
    hi, ri, ci = axesI
    new = [[[False]*dim[cn] for r in range(dim[rn])] for h in range(dim[hn])]
    for a, b in zip(product(range(dim[hn]), range(dim[rn]), range(dim[cn])),
                     product(*nAxes)):
        new[a[0]][a[1]][a[2]] = piece[b[hi]][b[ri]][b[ci]] == '1'
    hn = len(new)
    rn = len(new[0])
    cn = len(new[0][0])
    loc = list(product(range(bheight-hn+1), range(brows-rn+1), range(bcols-cn+1)))
    cor = list(product(range(hn), range(rn), range(cn)))
    return (np.array(new), np.array(loc, dtype=np.int64), np.array(cor, dtype=np.int64), np.array((hn, rn, cn), dtype=np.int64))

# check if a 3D piece is contained in a list or not
def check(piece, array):
    pa = piece[0]
    for pa1, *_ in array:
        if pa1.shape == pa.shape:
            comp = pa1 == pa
            if comp.all():
                return True
    return False

orientations = []

# find all different piece orientations
for piece in pieces:
    nextPiece = []
    for perm in permutations(range(3)):
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

values = np.array([[[False]*bcols for r in range(brows)] for h in range(bheight)])

@nb.njit
def add(piece, cor, n, sz):
    # returns True if piece is in a valid position, otherwise  False
    # and in the process adds the piece.
    # first find the piece representation
    # check if piece fits in values

    f1 = piece.flat
    f2 = values[n[0]:n[0]+sz[0],n[1]:n[1]+sz[1],n[2]:n[2]+sz[2]].flat
    for i in range(sz[0]*sz[1]*sz[2]):
        if f1[i] and f2[i]:
            return False;
    ##for a, b in zip(piece.flat, values[tuple(slice(a, b) for a, b in zip(n, n+sz))].flat):
    ##    if a and b:
    ##        return False
    # then add to placements and values
    for t in cor:
        if piece[tuple(t)]:
            values[tuple(n + t)] = True
    # check if there are any gaps too small
    if checkGaps():
        removeLast(cor, p, n)
        return False
    return True

@nb.njit
def removeLast(cor, p, n):
    # find the piece properties
    # remove from values list first
    for t in cor:
        if p[tuple(t)]:
            values[tuple(n + t)] = False
    # then remove from placements list


bcords = product(range(bheight), range(brows), range(bcols))

# functions to test empty spaces in order to skip impossible starting positions
@nb.njit
def checkGaps():
    global checked
    checked = set()
    # go thorugh each unchecked position and check how large the gap is
    for n in bcords:
        if checkCoordinates(n):
            if floodCheck(n) % 5:
                # if the gap is too small, return True
                return True
    # if none are too small return False
    return False

plusH = np.array((1, 0, 0), dtype=np.int64)
plusR = np.array((0, 1, 0), dtype=np.int64)
plusC = np.array((0, 0, 1), dtype=np.int64)

def floodCheck(n):
    checked.add(tuple(n))
    count = 1
    if checkCoordinates(n + plusH):
        count += floodCheck(n + plusH)
    if checkCoordinates(n + plusR):
        count += floodCheck(n + plusR)
    if checkCoordinates(n + plusC):
        count += floodCheck(n + plusC)
    if checkCoordinates(n - plusR):
        count += floodCheck(n - plusR)
    if checkCoordinates(n - plusC):
        count += floodCheck(n - plusC)
    if checkCoordinates(n - plusH):
        count += floodCheck(n - plusH)
    return count

# check if coordinates are valid, unchecked and not occupied
# returns True if these conditions are all true, otherwise False
def checkCoordinates(n):
    h, r, c = n
    if h < 0 or r < 0 or c < 0 or h >= bheight or r >= brows or c >= bcols:
        return False
    if values[h][r][c] and not (h, r, c) in checked:
        return True
    else:
        return False


solutions = []

# function that runs through every piece, orientation and position
# adding one piece at a time and removing
def piece(p):
    global i
    i += 1
    if i > 100000:
         return
    for orient, loc, cor, sz in orientations[p]:
        for n in loc:
            if add(orient, cor, n, sz):
                if p == 11:
                    removeLast(cor, orient, n)
                else:
                    piece(p + 1)
                    removeLast(cor, orient, n)

if __name__ == '__main__':
    # start solving
    piece(0)
