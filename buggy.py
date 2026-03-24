# Tetris cube solver - uncompilable version
from itertools import product, permutations, izip

# board dimensions
bheight = 4
brows = 4
bcols = 4

pieces = [# 0
          [['1.',
            '..'],

           ['11',
            '11']],
          
          # 1
          [['1..',
            '1..',
            '111']],

          # 2
          [['.1',
            '11',
            '.1',
            '.1']],
          
          # 3
          [['1.',
            '11',
            '.1',
            '.1']],
          
          # 4
          [['1..',
            '1..',
            '111'],
           
           ['...',
            '1..',
            '...']],
          
          # 5
          [['1..',
            '1..',
            '111'],
           
           ['1..',
            '...',
            '...']],
          # 6
          [['.1.',
            '...'],
           
           ['.1.',
            '111']],
          
          # 7
          [['.1.',
            '...'],
           
           ['111',
            '.1.'],
           
           ['...',
            '.1.']],

          # 8
          [['.1',
            '11',
            '..'],
           
           ['..',
            '1.',
            '1.']],

          # 9
          [['11',
            '.1',
            '..'],
           
           ['..',
            '.1',
            '.1']],

          # 10 or A
          [['1.',
            '..',
            '..'],
           
           ['11',
            '.1',
            '.1']],

          # 11 or B
          [['11.',
            '.11',
            '.1.'],
           
           ['1..',
            '...',
            '...']]]

orientations = []


# some general declerations
def count(var):
    return range(len(var))

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
def print3D(array):
    ###test if function is called
    print 'hey'
    text = '\n'
    for h in array:
        for r in h:
            for c in r:
                text += c,
            text += '\n'
        text += '\n'
    text += '\n'
    print(text)


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
            nAxes.append(range(dim[axes[i]]))
        else:
            nAxes.append(range(dim[axes[i]] - 1, -1, -1))
    hi, ri, ci = axesI
    
    for a, b in izip(product(range(dim[hn]), range(dim[rn]), range(dim[cn])),
                     product(*nAxes)):
        new[a[0]][a[1]] += str(piece[b[hi]][b[ri]][b[ci]])
    return new


# find all different piece orientations
for num in count(pieces):
    piece = pieces[num]
    orientations.append([])
    for perm in permutations(range(3)):
        if perm[0] - perm[1] in [-1, 2]:
            # all positive in order
            negatives = [0] * 3
            orientation = transform(piece, perm, negatives)
            if not check(orientation, orientations[-1]):
                orientations[-1].append(orientation)
            for i in range(3):
                # all negative except i
                negatives = [1] * 3
                negatives[i] = 0
                orientation = transform(piece, perm, negatives)
                if not check(orientation, orientations[-1]):
                    orientations[-1].append(orientation)
        else:
            # all negative in order
            negatives = [1] * 3
            orientation = transform(piece, perm, negatives)
            if not check(orientation, orientations[-1]):
                orientations[-1].append(orientation)
            for i in range(3):
                # all positive except i
                negatives = [0] * 3
                negatives[i] = 1
                orientation = transform(piece, perm, negatives)
                if not check(orientation, orientations[-1]):
                    orientations[-1].append(orientation)
# print results
for i in count(orientations):
    print 'piece', i, 'has', len(orientations[i]), 'orientations.'


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
        if piece[h][r][c] == '1' and values[hn + h][rn + r][cn + c] != '.':
            return False
    # then add to placements and values
    placements.append(list(p, o, h, r, c))
    for h, r, c in product(count(piece), count(piece[0]), count(piece[0][0])):
        if piece[h][r][c] == '1':
            row = values[hn + h][rn + r]
            values[hn + h][rn + r] = row[:cn + c] + hex(piece)[2:] +\
            row[cn + c + 1:]
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
            row = values[hn + h][rn + r]
            values[hn + h][rn + r] = row[:cn + c] + '.' +\
            row[cn + c + 1:]
    # then remove from placements list
    del placements[-1]

# function to test a solution to see if it is just a duplicate, then add it to
# the list if it isnt.
def newSolution():
    global values
    global solutions
    # go through each possible orientations, and stop at a duplicate

    for perm in permutations(range(3)):
        if perm[0] - perm[1] in [-1, 2]:
            # all positive in order
            negatives = [0] * 3
            if check(transform(values, perm, negatives), solutions):
                # found a dupe solution, so break
                break
            for i in range(3):
                # all negative except i
                negatives = [1] * 3
                negatives[i] = 0
                if check(transform(values, perm, negatives), solutions):
                    # found a dupe solution, so break
                    break
            else:
                # continue, no duplicate orientations in this permutation
                continue
            # solution is a duplicate so stop searching
            break
        else:
            # all negative in order
            negatives = [1] * 3
            if check(transform(values, perm, negatives), solutions):
                # found a dupe solution, so break
                break
            for i in range(3):
                # all positive except i
                negatives = [0] * 3
                negatives[i] = 1
                if check(transform(values, perm, negatives), solutions):
                    # found a dupe solution, so break
                    break
            else:
                # continue, no duplicate orientations in this permutation
                continue
            # solution is a duplicate so stop searching
            break
    else:
        # went through without finding any duplicates, new solution!
        solutions.append(values)
        return True
    # stopped loop early because the solution was a duplicate
    return False

                    

# functions to test empty spaces in order to skip impossible starting positions
def checkGaps():
    global checked
    checked = []
    # go thorugh each unchecked position and check how large the gap is
    for h, r, c in product(range(bheight), range(brows), range(bcols)):
        if checkCoordinates(r, c) == 0:
            if floodcheck(h, r, c) < 5:
                # if the gap is too small, return True
                return True
    # if none are too small return False
    return False

def floodCheck(h, r, c):
    checked.append((r, c))
    count = 1
    if checkCoordinates(h + 1, r, c) == 0:
        count += floodCheck(h + 1, r, c)
    if checkCoordinates(h, r + 1, c) == 0:
        count += floodCheck(h, r + 1, c)
    if checkCoordinates(h, r, c + 1) == 0:
        count += floodCheck(h, r, c + 1)
    if checkCoordinates(h, r - 1, c) == 0:
        count += floodCheck(h, r - 1, c)
    if checkCoordinates(h, r, c - 1) == 0:
        count += floodCheck(h, r, c - 1)
    if checkCoordinates(h - 1, r, c) == 0:
        count += floodCheck(h - 1, r, c)
    return count

# check wether coordinates have been checked allready or occupied.
def checkCoordinates(h, r, c): # 0 means empty, 1 full or allready checked
    #if h < 0 or r < 0 or c < 0 or h >= bhieght or r >= brows or c >= bcols:
        #return True
    if values[h][r][c] == '.' and not (h, r, c) in checked:
        return False
    else:
        return True


solutions = []

# function that runs through every piece, orientation and position
# adding one piece at a time and removing 
def piece(p):
    global orientations
    for orient in orientations[p]:
        for h, r, c in product(hieght - len(orient) + 1,
                               brows - len(orient[0]) + 1,
                               bcols - len(orient[0][0]) + 1):
            if add(p, o, h, r, c):
                ###show progress
                print3D(values)
                if piece == 11:
                    if newSolution():
                        print 'Found new solution! -', len(solutions)
                    else:
                        print 'Found a duplicate solution.'
                    print3D(solutions[-1])
                    removeLast()
                else:
                    piece(p + 1)
                    remove(piece)

