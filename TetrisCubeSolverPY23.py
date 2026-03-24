# Tetris cube solver in python by Michael Pannekoek
from __future__ import absolute_import
from __future__ import print_function
from itertools import product, permutations
import profile
from time import perf_counter as clock
from six.moves import range

lasttime = clock()

def lap():
    global lasttime
    newtime = clock()
    lasttime, newtime = newtime, newtime - lasttime
    return newtime

out = open('TetrisSolutions-1.txt', 'w')

# board dimensions
bheight = 3
brows = 2
bcols = 2

pieces = [
          [['111',
            '11.']],

  
          [['1.',
            '..'],

           ['11',
            '11']],

          [['11']]
]

'''[
          # 0
          [['1..',
            '1..',
            '111'],
           
           ['...',
            '1..',
            '...']],
          
          # 1
          [['1..',
            '1..',
            '111'],
           
           ['1..',
            '...',
            '...']],

          # 2
          [['11.',
            '.11',
            '.1.'],
           
           ['1..',
            '...',
            '...']],
          
          # 3
          [['.1.',
            '...'],
           
           ['111',
            '.1.'],
           
           ['...',
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
          [['1..',
            '1..',
            '111']],
          
          # 7
          [['1.',
            '11',
            '..'],
           
           ['..',
            '.1',
            '.1']],

          # 8
          [['.1.',
            '...'],
           
           ['.1.',
            '111']],

          # 9
          [['11',
            '1.',
            '1.'],
           
           ['.1',
            '..',
            '..']],

          # 10 or A
          [['1.',
            '11',
            '.1'],
           
           ['..',
            '..',
            '.1']],

          # 11 or B
          [['1.',
            '..'],

           ['11',
            '11']]]'''

def count(var):
    return list(range(len(var)))

# A function that returns a new piece, with the dimensions of the input piece
# plotted to the axes inputted in the order stated in negatives list input
def transform(piece, axes, negatives):
    hl = len(piece)
    rl = len(piece[0])
    cl = len(piece[0][0])
    dim = [hl, rl, cl]
    new = []
    hn, rn, cn = axes
    for h in range(dim[hn]):
        new.append([])
        for r in range(dim[rn]):
            new[-1].append('')          
    nAxes = []
    axesI = [0] * 3
    for i in range(3):
        axesI[axes[i]] = i
        if negatives[i] == 0:
            nAxes.append(list(range(dim[axes[i]])))
        else:
            nAxes.append(list(range(dim[axes[i]] - 1, -1, -1)))
    hi, ri, ci = axesI
    for a, b in zip(product(list(range(dim[hn])), list(range(dim[rn])), list(range(dim[cn]))),
                     product(*nAxes)):
        new[a[0]][a[1]] += str(piece[b[hi]][b[ri]][b[ci]])
    return new

# check if a 3D piece is contained in a list or not
def check(piece, array):
    for prev in array:
        if len(piece) != len(prev):
            continue
        for i in count(piece):
            if piece[i] != prev[i]:
                break
        else:
            break
    else:
        return False
    return True

# function to print a 3D array
def print3D(array, file=None): ### file is NIY
    text = ''
    for r in count(array[0]):
        for h in count(array):
            for c in count(array[0][0]):
                text += array[h][r][c] + ' '
            text += '   '
        text += '\n'
    text += '\n'
    return text

orientations = []

# find all different piece orientations
for piece in pieces:
    nextPiece = []
    for perm in permutations(list(range(3))):
        if perm[1] - perm[0] in [-1, 2]:
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
        else:
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
    orientations.append(nextPiece)
### print results
##for i in count(orientations):
##    print 'piece', i, 'has', len(orientations[i]), 'orientations.'


# declerations usefull to test certain placements
placements = []
values = []
for h in range(bheight):
    values.append([])
    for r in range(brows):
        values[-1].append('.' * bcols)

def add(p, o, hn, rn, cn):
    # returns True if piece is in a valid position, otherwise  False
    # and in the process adds the piece.
    # first find the piece representation
    piece = orientations[p][o]
    # check if piece fits in values
    for h, r, c in product(count(piece), count(piece[0]), count(piece[0][0])):
        if piece[h][r][c] == '1' and values[hn+h][rn+r][cn+c] != '.':
            return False
    # then add to placements and values
    placements.append(list([p, o, hn, rn, cn]))
    for h, r, c in product(count(piece), count(piece[0]), count(piece[0][0])):
        if piece[h][r][c] == '1':
            row = values[hn+h][rn+r]
            values[hn+h][rn+r] = row[:cn+c] + hex(p)[2:] + row[cn+c+1:]
    ###show progress
##    print print3D(values)
##    print
    ###
    # check if there are any gaps too small
    if checkGaps():
        removeLast()
        return False
    return True

def removeLast():
    # find the piece properties
    p, o, hn, rn, cn = placements[-1]
    piece = orientations[p][o]
    # remove from values list first
    for h, r, c in product(count(piece), count(piece[0]), count(piece[0][0])):
        if piece[h][r][c] == '1':
            row = values[hn+h][rn+r]
            values[hn+h][rn+r] = row[:cn+c] + '.' + row[cn+c+1:]
    # then remove from placements list
    del placements[-1]

# function to test a solution to see if it is just a duplicate, then add it to
# the list if it isnt.
def newSolution():
    # go through each possible orientations, and stop at a duplicate
    for perm in permutations(list(range(3))):
        if perm[0] - perm[1] in [-1, 2]:
            # all positive in order
            negatives = [0] * 3
            if check(transform(values, perm, negatives), solutions):
                return False
            for i in range(3):
                # all negative except i
                negatives = [1] * 3
                negatives[i] = 0
                if check(transform(values, perm, negatives), solutions):
                    return False
        else:
            # all negative in order
            negatives = [1] * 3
            if check(transform(values, perm, negatives), solutions):
                return False
            for i in range(3):
                # all positive except i
                negatives = [0] * 3
                negatives[i] = 1
                if check(transform(values, perm, negatives), solutions):
                    return False
    return True

                    

# functions to test empty spaces in order to skip impossible starting positions
def checkGaps():
    global checked
    checked = set()
    # go thorugh each unchecked position and check how large the gap is
    for h, r, c in product(list(range(bheight)), list(range(brows)), list(range(bcols))):
        if checkCoordinates(h, r, c):
            if floodCheck(h, r, c) < 5:
                # if the gap is too small, return True
                return True
    # if none are too small return False
    return False

def floodCheck(h, r, c):
    checked.add((h, r, c))
    count = 1
    if checkCoordinates(h + 1, r, c):
        count += floodCheck(h + 1, r, c)
    if checkCoordinates(h, r + 1, c):
        count += floodCheck(h, r + 1, c)
    if checkCoordinates(h, r, c + 1):
        count += floodCheck(h, r, c + 1)
    if checkCoordinates(h, r - 1, c):
        count += floodCheck(h, r - 1, c)
    if checkCoordinates(h, r, c - 1):
        count += floodCheck(h, r, c - 1)
    if checkCoordinates(h - 1, r, c):
        count += floodCheck(h - 1, r, c)
    return count

# check if coordinates are valid, unchecked and not occupied
# returns True if these conditions are all true, otherwise False
def checkCoordinates(h, r, c):
    if h < 0 or r < 0 or c < 0 or h >= bheight or r >= brows or c >= bcols:
        return False
    if values[h][r][c] == '.' and not (h, r, c) in checked:
        return True
    else:
        return False


solutions = []

# function that runs through every piece, orientation and position
# adding one piece at a time and removing 
def piece(p):
    print(p)
    for o in count(orientations[p]):
        orient = orientations[p][o]
        hl, rl, cl = len(orient), len(orient[0]), len(orient[0][0])
        for h, r, c in product(list(range(bheight-hl+1)), list(range(brows-rl+1)),
                               list(range(bcols-cl+1))):
            if add(p, o, h, r, c):
                if p == 11:
                    solutions.append(values)
                    print('Found a solution! - ' + str(len(solutions)))
                    print(print3D(solutions[-1]))
                    print('Interval:', lap())
                        
##                    if newSolution():
##                        solutions.append(values)
##                        print 'Found new solution! - ' + str(len(solutions))
##                        print print3D(solutions[-1])
##                    else:
##                        solutions.append(values)
##                        print 'Found a duplicate solution.- ' + str(len(solutions))
##                        print print3D(solutions[-1])
                    removeLast()
                else:

                    piece(p + 1)
                    removeLast()

# start solving
piece(0)

