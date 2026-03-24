import sys
from itertools import product
from collections import Counter, deque
from time import monotonic as time
import numpy as np
import numba as nb


startTime = time()
print(f'start time {startTime:.3f}')

BDEPTH = 4
BHEIGHT = 4
BWIDTH = 4

BOARDSIZE = BDEPTH*BHEIGHT*BWIDTH

EMPTYCHARS = set(' .x')
PREFERREDEMPTY = '.'

PIECECHARS = 'ABCDEFGHIJKL'

PIECES = [
          # 0: A
          [['1..',
            '1..',
            '111'],
           
           ['1..',
            '...',
            '...']],
          
          # 1: B
          [['1.',
            '11',
            '.1',
            '.1']],
          
          # 2: C
          [['1..',
            '1..',
            '111']],
          
          # 3: D
          [['1.',
            '11',
            '..'],
           
           ['..',
            '.1',
            '.1']],
          
          # 4: E
          [['11',
            '1.',
            '1.'],
           
           ['.1',
            '..',
            '..']],
          
          # 5: F
          [['1.',
            '11',
            '.1'],
           
           ['..',
            '..',
            '.1']],
          
          # 6: G
          [['1..',
            '1..',
            '111'],
           
           ['...',
            '1..',
            '...']],
          
          # 7: H
          [['11.',
            '.11',
            '.1.'],
           
           ['1..',
            '...',
            '...']],
          
          # 8: I
          [['.1.',
            '...'],
           
           ['111',
            '.1.'],
           
           ['...',
            '.1.']],

          # 9: J
          [['.1',
            '11',
            '.1',
            '.1']],
          
          # 10: K
          [['.1.',
            '...'],
           
           ['.1.',
            '111']],

          # 11: L
          [['1.',
            '..'],

           ['11',
            '11']]]

PIECECOUNT = len(PIECES)
PIECECOUNTSUB1 = PIECECOUNT-1

def singleOrient(piece):
    points = []
    for z, plane in enumerate(piece):
        for r, row in enumerate(plane):
            for c, item in enumerate(row):
                if item not in EMPTYCHARS:
                    points.append((z, r, c))
    return [points]


def orientPiece(piece):
    orientations = [[] for i in range(24)]
    for z, plane in enumerate(piece):
        for r, row in enumerate(plane):
            for c, item in enumerate(row):
                if item not in EMPTYCHARS:
                    for perm, sign, i in [
                        (lambda z, r, c:(z, r, c), 1, 0),
                        (lambda z, r, c:(c, z, r), 1, 1),
                        (lambda z, r, c:(r, c, z), 1, 2),
                        (lambda z, r, c:(c, r, z), -1, 3),
                        (lambda z, r, c:(r, z, c), -1, 4),
                        (lambda z, r, c:(z, c, r), -1, 5),
                    ]:
                        zm = len(piece)-1-z
                        rm = len(piece[0])-1-r
                        cm = len(piece[0][0])-1-c
                        if sign == -1:
                            z, zm = zm, z
                        orientations[i].append(perm(z, r, c))
                        orientations[i+6].append(perm(zm, rm, c))
                        orientations[i+12].append(perm(zm, r, cm))
                        orientations[i+18].append(perm(z, rm, cm))
    seen = set()
    filtered = []
    for orientation in orientations:
        t = tuple(orientation)
        if t in seen:
            continue
        seen.add(t)
        filtered.append(orientation)
    return filtered

orientedPieces = [singleOrient(PIECES[0])]
orientedPieces = orientedPieces + [orientPiece(p) for p in PIECES[1:]]
boundaries = [
    [
        [
            max(pos[j] for pos in orientation) for j in range(3)
        ] for orientation in orientedPiece
    ] for orientedPiece in orientedPieces
]

pieceSizes = [len(orientedPiece[0]) for orientedPiece in orientedPieces]

possibleSizesList = []
for i in range(PIECECOUNT):
    ctr = Counter(pieceSizes[i:])
    possibleSizesList.append(
        {
            sum(
                pieceSize*m for pieceSize, m in zip(ctr, multiples)
            ) for multiples in product(
                *(range(v+1) for v in ctr.values())
            )
            # for a set of multiples that range from 0 to the count in the counter
        }
    )

#impossibleSizes = {i for i in range(BDEPTH*BHEIGHT*BWIDTH+1)} - possibleSizes
#print(impossibleSizes)

positionedPieces = []
for pieceOrients, boundss in zip(orientedPieces, boundaries):
    piece = []
    for pieceOrient, bounds in  zip(pieceOrients, boundss):
        orient = []
        for spos in product(
            *(
                range(bs-bound) for bound, bs in zip(
                    bounds, [BDEPTH, BHEIGHT, BWIDTH]
                )
            )
        ):
            piece.append(
                {
                    tuple(
                        sp+op for sp, op in zip(spos, opos)
                    ) for opos in pieceOrient
                }
            )
    positionedPieces.append(piece)


def convertToInt(z, r, c):
    return z*BHEIGHT*BWIDTH+r*BWIDTH+c

bitPieces = [
    [
        sum(1 << convertToInt(z, r, c) for z, r, c in position) for position in piece
    ] for piece in positionedPieces
]

bitmask = (1 << BDEPTH*BHEIGHT*BWIDTH) - 1

bitfull = 0

#bitempty = bitmask

'''board = [
    [
        [PREFERREDEMPTY]*BWIDTH for r in range(BHEIGHT)
    ] for c in range(BDEPTH)
]'''

allPoints = [
    (z, r, c) for z, r, c in product(
        range(BDEPTH),
        range(BHEIGHT),
        range(BWIDTH)
    )
]

allPointsSet = set(allPoints)


def printGrid(placements, outFile):
    grid = [
        [
            [PREFERREDEMPTY]*BWIDTH for r in range(BHEIGHT)
        ] for c in range(BDEPTH)
    ]
    for points, char in zip(placements, PIECECHARS):
        for z, r, c in points:
            grid[z][r][c] = char
    print('\n\n'.join(
        '\n'.join(' '.join(row) for row in plane) for plane in grid
    ), file=outFile, end='\n\n')

def printSolvedGrid(placements, outFile):
    global solutions
    solutions += 1
    print(f'solution {solutions} at {time():.3f}:', file=outFile)
    printGrid(placements, outFile)
    print(f'solution {solutions} at {time():.3f}:')
    printGrid(placements, sys.stdout)

def filteredNeighbors(point, filt):
    z, r, c = point
    return {(z-1, r, c), (z+1, r, c), (z, r-1, c), (z, r+1, c), (z, r, c-1), (z, r, c+1)} & filt

IntNeighbors = [None]*BOARDSIZE

for z, r, c in product(range(BDEPTH), range(BHEIGHT), range(BWIDTH)):
    i = convertToInt(z, r, c)
    IntNeighbors[i] = [convertToInt(zn, rn, cn) for zn, rn, cn in filteredNeighbors((z, r, c), allPointsSet)]

def checkSolvable(p, bitfull):
    possibleSizes = possibleSizesList[p]
    chains = [[] for _ in range(BOARDSIZE)]
    ends = []
    appendToEnds = ends.append
    empty = np.zeros(shape=(BOARDSIZE), dtype=bool)
    q = bitfull
    i = 0
    while q > 0:
        r = q & 1
        if r == 1:
            empty[i] = True
        i += 1
        q = q >> 1
    for point, status in enumerate(toVisit):
        if status:
            empty[point] = False
            neighborsToVisit = deque([point])
            ntvPopleft = neighborsToVisit.popleft
            ntvAppend = neighborsToVisit.append
            c = 0
            while neighborsToVisit:
                p1 = ntvPopleft()
                c += 1
                neighbors = IntNeighbors[p1]
                emptyNeighbors = []
                eappend = emptyNeighbors.append
                for neighbor in neighbors:
                    if empty[neighbor]:
                        eappend(neighbor)
                        if toVisit[neighbor]:
                            ntvAppend(neighbor)
                            toVisit[neighbor] = False
                l = len(emptyNeighbors)
                if l == 1:
                    appendToEnds(p1)
                if l <= 2:
                    chains[p1] = emptyNeighbors
            if c not in possibleSizes:
                return False
    for singleP in ends:
        nxt = singleP
        prev = None
        for sc in range(7):
            try:
                temp = nxt
                nxt = chains[nxt]
                item = nxt[0]
                if item == prev:
                    item = nxt[1]
                nxt = item
                prev = temp
            except IndexError:
                break
        # assumption: pieces sorted by chain length, values here
        if sc > 6 or (sc > 5 and p > 0) or (sc > 4 and p > 5) or (sc > 2 and p > 7) or (sc > 1 and p > 10):
            return False
    return True

i = 0
def place(p, outFile, bitfull=0, placements=None):
    global i
    i += 1
    if i > 10000:
        return
    if placements is None:
        placements = deque()
    for position, bitPosition in zip(positionedPieces[p], bitPieces[p]):
        # place piece
        if (bitPosition & bitfull) == 0:
            placements.append(position)
            bitfull |= bitPosition
            # sucessfully placed a piece
            if p == PIECECOUNTSUB1:
                printSolvedGrid(placements, outFile)
            elif checkSolvable(p+1, bitfull):
                place(p+1, outFile, bitfull, placements)
            placements.pop()
            bitfull &= (bitPosition ^  bitmask)

def main(outFile):
    place(0, outFile)

solutions = 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        #print('expected file for solutions.')
        #sys.exit()
        file = 'solutions.txt'
    else:
        file = sys.argv[1]
    with open(file, 'w') as f:
        print(f'start time {startTime:.3f}', file=f)
        print(f'finished initialization at {time():.3f}')
        print(f'finished initialization at {time():.3f}', file=f)
        main(f)
