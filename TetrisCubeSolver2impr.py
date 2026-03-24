# Tetris Cube solver with new optimisations

from itertools import izip, product, permutations
from time import clock

print('tetris cube solver 2')

lasttime = clock()

def lap():
    global lasttime
    newtime = clock()
    lasttime, newtime = newtime, newtime - lasttime
    return newtime

DEPTH = 4
HEIGHT = 4
WIDTH = 4



def transform(points, dims, axes, negatives):
    #zl, yl, xl = dims
    #def this(z, y, x):
    newcoords = []
    newdims = []
    for coords in points:
        new = []
        for axis in axes:
            if negatives[axis]:
                new.append(dims[axis] - coords[axis] - 1)
            else:
                new.append(coords[axis])
        newcoords.append(tuple(new))
    for axis in axes:
        newdims.append(dims[axis])
    return (frozenset(newcoords),) + tuple(newdims)


class Piece():
    def __init__(self, strarray, idn):
        clist = []
        self.idn = idn
        self.dimensions = (len(strarray), len(strarray[0]), len(strarray[0][0]))
        for z, layer in enumerate(piece):
            for y, row in enumerate(layer):
                for x, char in enumerate(row):
                    if char == '1':
                        clist.append((z, y, x))
        self.orientations = []
        seen = set()
        for ap in permutations(range(3)):
            if ap[1] - ap[0] in [-1, 2]:
                for negatives in [(1, 1, 1), (1, 0, 0), (0, 1, 0), (0, 0, 1)]:
                    points, a, b, c = transform(clist, self.dimensions, ap,
                                               negatives)
                    if points in seen:
                        continue
                    else:
                        seen.add(points)
                        self.orientations.append([list(points), a, b, c])
            else:
                for negatives in [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]:
                    points, a, b, c = transform(clist, self.dimensions, ap,
                                               negatives)
                    if points in seen:
                        continue
                    else:
                        seen.add(points)
                        self.orientations.append([list(points), a, b, c])                        

pieces = [
          # A
          [['1..',
            '1..',
            '111'],
           
           ['...',
            '1..',
            '...']],
          
          # B
          [['1..',
            '1..',
            '111'],
           
           ['1..',
            '...',
            '...']],

          # C
          [['11.',
            '.11',
            '.1.'],
           
           ['1..',
            '...',
            '...']],
          
          # D
          [['.1.',
            '...'],
           
           ['111',
            '.1.'],
           
           ['...',
            '.1.']],
          
          # E
          [['.1',
            '11',
            '.1',
            '.1']],
          
          # F
          [['1.',
            '11',
            '.1',
            '.1']],
          
          # G
          [['1..',
            '1..',
            '111']],
          
          # H
          [['1.',
            '11',
            '..'],
           
           ['..',
            '.1',
            '.1']],

          # I
          [['.1.',
            '...'],
           
           ['.1.',
            '111']],

          # J
          [['11',
            '1.',
            '1.'],
           
           ['.1',
            '..',
            '..']],

          # K
          [['1.',
            '11',
            '.1'],
           
           ['..',
            '..',
            '.1']],

          # L
          [['1.',
            '..'],

           ['11',
            '11']]]

piecelist = []
c = 0
for piece in pieces:
    piecelist.append(Piece(piece, c))
    c += 1

##max_orientations = 0
##
##for piece in piecelist:
##    o = len(piece.orientations)
##    if o > max_orientations:
##        max_orientations = o
##        bestpiece = piece
##
##piecelist.remove(bestpiece)
##piecelist = [bestpiece] + piecelist

def print3D(grid):
##    out = ''
##    for y in range(HEIGHT):
##        for z in range(DEPTH):
##            for x in range(WIDTH):
##                out += grid[z][y][x] + ' '
##            out += '   '
##        out += '\n'
##    return out.rstrip('\n')
    conversion = {i:c for i, c in enumerate('ABCDEFGHIJKL')}
    conversion[None] = '0'
    return '\n'.join('   '.join(' '.join(conversion[c] for c in grid[z][y])
                                for z in range(DEPTH))
                     for y in range(HEIGHT)) + '\n'

def place(piece, z, y, x, grid, rem, idn):
    newgrid = [[list(row) for row in layer] for layer in grid]
    rem = set(rem)
    for zo, yo, xo in piece:
        zn = z + zo
        yn = y + yo
        xn = x + xo
        if newgrid[zn][yn][xn] != None:
            return False
        newgrid[zn][yn][xn] = idn
        rem.remove((zn, yn, xn))
    else:
        return (newgrid, rem)

def checkCoordinates(z, y, x, grid):
    if 0 <= z < DEPTH and 0 <= y < HEIGHT and 0 <= x < WIDTH and \
              (z, y, x) not in checked and grid[z][y][x] == None:
        return True
    return False

def floodCheck(z, y, x, grid):
    checked.add((z, y, x))
    spaces.discard((z, y, x))
    count = 1
    if checkCoordinates(z + 1, y, x, grid):
        count += floodCheck(z + 1, y, x, grid)
    if checkCoordinates(z, y + 1, x, grid):
        count += floodCheck(z, y + 1, x, grid)
    if checkCoordinates(z, y, x + 1, grid):
        count += floodCheck(z, y, x + 1, grid)
    if checkCoordinates(z, y - 1, x, grid):
        count += floodCheck(z, y - 1, x, grid)
    if checkCoordinates(z, y, x - 1, grid):
        count += floodCheck(z, y, x - 1, grid)
    if checkCoordinates(z - 1, y, x, grid):
        count += floodCheck(z - 1, y, x, grid)
    return count

def checkgaps(grid):
    global checked
    checked = set()
    while spaces:
        z, y, x = spaces.pop()
        if floodCheck(z, y, x, grid) % 5:
            return False
    return True


def nextpiece(i, piece, grid, rem, singleOrientation=False):
    if singleOrientation:
        orientations = piece.orientations[:1]
    else:
        orientations = piece.orientations
    for orientation, zl, yl, xl in orientations:
        for z, y, x in product(range(DEPTH-zl+1), range(HEIGHT-yl+1),
                               range(WIDTH-xl+1)):
            result = place(orientation, z, y, x, grid, rem, piece.idn)
            if result:
                newgrid, newrem = result
                if i == len(piecelist) - 1:
                    print print3D(newgrid)
                    print 'interval:', lap() 
                else:
                    global spaces
                    spaces = set(newrem)
                    if checkgaps(newgrid):
                        nextpiece(i+1, piecelist[i+1], newgrid, newrem)
            
            
startgrid = [[[None]*WIDTH for y in range(HEIGHT)] for z in range(DEPTH)]
startrem = {(z, y, x) for z, y, x in product(range(DEPTH), range(HEIGHT),
                                             range(WIDTH))} # < play around with

nextpiece(0, piecelist[0], startgrid, startrem, True)
