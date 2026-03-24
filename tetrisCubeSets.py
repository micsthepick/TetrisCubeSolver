import sys
from itertools import product
from collections import Counter
from time import monotonic as time

print(f'start time {time():.3f}')

BDEPTH = 4
BHEIGHT = 4
BWIDTH = 4

EMPTYCHARS = set(' .x')
PREFERREDEMPTY = '.'

PIECECHARS = 'ABCDEFGHIJKL'

pieces = [
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

orientedPieces = [orientPiece(p) for p in pieces]
boundaries = [
    [
        [max(p[j] for p in o) for j in range(3)] for o in oPiece
    ] for oPiece in orientedPieces
]
pieceSizes = [len(piece[0]) for piece in orientedPieces]
c = Counter(pieceSizes).items()
possibleSizes = {
    sum(
        k*v for k, (v, _) in zip(prod, c)
    ) for prod in product(*(range(v+1) for k, v in c))
}
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
            orient.append(
                {
                    tuple(
                        sp+op for sp, op in zip(spos, opos)
                    ) for opos in pieceOrient
                }
            )
        piece.append(orient)
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

'''def neighbors(point):
    z, r, c = point
    global board
    if z > 0:
        yield (z-1, r, c), board[z-1][r][c]
    if z < BDEPTH-1:        
        yield (z+1, r, c), board[z+1][r][c]
    if r > 0:
        yield (z, r-1, c), board[z][r-1][c]
    if r < BHEIGHT-1:        
        yield (z, r+1, c), board[z][r+1][c]
    if c > 0:
        yield (z, r, c-1), board[z][r][c-1]
    if c < BWIDTH-1:        
        yield (z, r, c+1), board[z][r][c+1]
##    for zc, rc, cc in product(
##        range(max(0, z-1), min(DEPTH, z+2)),
##        range(max(0, r-1), min(HEIGHT, r+2)),
##        range(max(0, c-1), min(WIDTH, c+2))
##    ):
##        if z == zc and r == rc and c == cc:
##            continue
##        yield (zc, rc, cc), board[zc][rc][cc]'''

def emptyNeighbors(point, empty):
    z, r, c = point
    if (z-1, r, c) in empty:
        yield (z-1, r, c)
    if (z+1, r, c) in empty:
        yield (z+1, r, c)
    if (z, r-1, c) in empty:
        yield (z, r-1, c)
    if (z, r+1, c) in empty:
        yield (z, r+1, c)
    if (z, r, c-1) in empty:
        yield (z, r, c-1)
    if (z, r, c+1) in empty:
        yield (z, r, c+1)
##    for point, item in neighbors(point):
##        if item in EMPTYCHARS:
##            yield point

def checkSolvable(p, empty):
    toVisit = set(allPoints)
    while len(toVisit) > 0:
        point = toVisit.pop()
        if point not in empty:
            continue
        singles = []
        count = 0
        neighborsToVisit = [point]
        seen = set(point)
        while len(neighborsToVisit) != 0:
            p1 = neighborsToVisit.pop()
            count += 1
            seen.add(p1)
            neighbors = set(emptyNeighbors(p1, empty))
            if len(neighbors) == 1:
                singles.append(p1)
            new = neighbors-seen
            neighborsToVisit.extend(new)
            seen.update(new)
        toVisit -= seen
        if count not in possibleSizes:
            #print(f'impossibleSize {count}')
            return False
        for singleP in singles:
            sc = 1
            while True:
                seen1 = False
                neighbors = set(emptyNeighbors(singleP, empty))
                neighbors.discard(singleP)
                if len(neighbors) == 1:
                    # only 1 neighbor, not including previous point
                    sc += 1
                    singleP = neighbors.pop()
                    continue
                else:
                    # more than one neighbour, break
                    break
##            if sc >= 7:
##                return False
##            elif sc >= 6:
##                return p <= 0
##            elif sc >= 5:
##                return p <= 5
##            elif sc >= 3:
##                return p <= 7
##            elif sc >= 2:
##                return p <= 10
    return True

def place(p, outFile, empty, placements=None):
    # global iterations
    if placements is None:
        placements = []
    for orientation in positionedPieces[p]:
        for position in orientation:
            # iterations += 1
            # if iterations >= 100000:
            #     sys.exit()
            # place piece
            placements.append([])
            for point in position:
                try:
                    empty.remove(point)
                    placements[-1].append(point)
                except KeyError:
                    # position not empty, remember position in loop
                    breakat = point
                    break
            else:
                # sucessfully placed a piece
                breakat = None
                if p == len(pieces)-1:
                    printSolvedGrid(placements, outFile)
                elif checkSolvable(p+1, empty):
                    place(p+1, outFile, empty, placements)
            # remove piece
            placements.pop()
            for point in position:
                if point == breakat:
                    break
                empty.add(point)

def main(outFile, empty):
    global solutions
    solutions = 0
    place(0, outFile, empty)

# iterations = 0
solutions = 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        #print('expected file for solutions.')
        #sys.exit()
        file = 'solutions.txt'
    else:
        file = sys.argv[1]
    with open(file, 'w') as f:
        print(f'finished initialization at {time():.3f}')
        print(f'finished initialization at {time():.3f}', file=f)
        main(f, empty)
