import sys
from itertools import product
from collections import Counter, deque
from time import monotonic as time

startTime = time()
print(f'start time {startTime:.3f}')

BDEPTH = 4
BHEIGHT = 4
BWIDTH = 4

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
                    for m1, m2, m3, m4 in [
                        (1, 1, 1, 0),
                        (-1, -1, 1, 1),
                        (-1, 1, -1, 2),
                        (1, -1, -1, 3)
                    ]:
                        orientations[6*m4+0].append((z*m1, r*m2, c*m3))
                        orientations[6*m4+1].append((c*m1, z*m2, r*m3))
                        orientations[6*m4+2].append((r*m1, c*m2, z*m3))
                        orientations[6*m4+3].append((c*m1, -r*m2, z*m3))
                        orientations[6*m4+4].append((r*m1, -z*m2, c*m3))
                        orientations[6*m4+5].append((z*m1, -c*m2, r*m3))
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

empty = set(allPoints)
#filled = set()

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

def emptyNeighbors(point, empty):
    z, r, c = point
    return {(z-1, r, c), (z+1, r, c), (z, r-1, c), (z, r+1, c), (z, r, c-1), (z, r, c+1)} & empty

def checkSolvable(p, empty):
    possibleSizes = possibleSizesList[p]
    chains = {}
    ends = set()
    toVisit = set(empty)
    groups = []
    while toVisit:
        point = toVisit.pop()
        singles = []
        neighborsToVisit = deque([point])
        seen = {point}
        updateSeen = seen.update
        while neighborsToVisit:
            p1 = neighborsToVisit.popleft()
            z, r, c = p1
            neighbors = {(z-1, r, c), (z+1, r, c), (z, r-1, c), (z, r+1, c), (z, r, c-1), (z, r, c+1)} & empty
            neighborsToVisit.extend(neighbors - seen)
            updateSeen(neighbors)
            l = len(neighbors)
            if l == 1:
                ends.add(p1)
            if l <= 2:
                chains[p1] = neighbors
        toVisit -= seen
        groups.append(seen)
        if len(seen) not in possibleSizes:
            return False
    for singleP in ends:
        nxt = singleP
        temp = None
        for sc in range(7):
            try:
                temp = nxt
                nxt = chains[nxt]
                nxt.discard(temp)
                nxt = nxt.pop()
            except KeyError:
                break
        # assumption: pieces sorted by chain length, values here
        if sc > 6 or (sc > 5 and p > 0) or (sc > 4 and p > 5) or (sc > 2 and p > 7) or (sc > 1 and p > 10):
            return False
    return True

def place(p, outFile, empty, placements=None):
    global iterations
    iterations += 1
    if iterations > 1000:
        sys.exit()
    if placements is None:
        placements = deque()
    for position in positionedPieces[p]:
        # place piece
        if position.issubset(empty):
            placements.append(position)
            printGrid(placements, sys.stdout)#DEBUG
            empty -= position
            # sucessfully placed a piece
            if p == PIECECOUNTSUB1:
                printSolvedGrid(placements, outFile)
            elif checkSolvable(p+1, empty):
                place(p+1, outFile, empty, placements)
            placements.pop()
            empty |= position

def main(outFile, empty):
    place(0, outFile, empty)

iterations = 0
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
        main(f, empty)
