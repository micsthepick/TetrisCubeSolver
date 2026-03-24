import sys
from itertools import product
from collections import Counter

BDEPTH = 4
BHEIGHT = 4
BWIDTH = 4

EMPTYCHARS = set(' .x')
PREFERREDEMPTY = ' '

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
    return orientations

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
impossibleSizes = {i for i in range(BDEPTH*BHEIGHT*BWIDTH+1)} - possibleSizes

board = [
    [
        [PREFERREDEMPTY]*BWIDTH for r in range(BHEIGHT)
    ] for c in range(BDEPTH)
]

allPoints = [
    (z, r, c) for z, r, c in product(
        range(BDEPTH),
        range(BHEIGHT),
        range(BWIDTH)
    )
]

def printSolvedGrid(placements, outFile):
    grid = [
        [
            [PREFERREDEMPTY]*BWIDTH for r in range(BHEIGHT)
        ] for c in range(BDEPTH)
    ]
    for points, char in zip(placements, PIECECHARS):
        for z, r, c in points:
            grid[z][r][c] = char
    print('new solution:', file=outFile)
    #print('solution')
    print('\n\n'.join(
        '\n'.join(' '.join(row) for row in plane) for plane in grid
    ), file=outFile)

def neighbors(point):
    z, r, c = point
    global board
    if z > 0:
        yield (z-1, r, c), board[z-1][r][c]
    if z < BDEPTH-1:
        yield (z+1, r, c), board[z+1][r][c]
    if r > 0:
        yield (z, r-1, c), board[z][r-1][c]
    if r < BHEIGHT-1:
        yield (z, r+1, c), board[z][r-1][c]
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
##        yield (zc, rc, cc), board[zc][rc][cc]

def emptyNeighbors(point):
    z, r, c = point
    global board
    if z > 0 and board[z-1][r][c] in EMPTYCHARS:
        yield (z-1, r, c)
    if z < BDEPTH-1 and board[z+1][r][c] in EMPTYCHARS:
        yield (z+1, r, c)
    if r > 0 and board[z][r-1][c] in EMPTYCHARS:
        yield (z, r-1, c)
    if r < BHEIGHT-1 and board[z][r-1][c] in EMPTYCHARS:
        yield (z, r+1, c)
    if c > 0 and board[z][r][c-1] in EMPTYCHARS:
        yield (z, r, c-1)
    if c < BWIDTH-1 and board[z][r][c+1] in EMPTYCHARS:
        yield (z, r, c+1)
##    for point, item in neighbors(point):
##        if item in EMPTYCHARS:
##            yield point

def checkSolvable(p):
    global board
    toVisit = set(allPoints)
    while len(toVisit) > 0:
        p = toVisit.pop()
        zo, ro, co = p
        if board[zo][ro][co] not in EMPTYCHARS:
            continue
        singles = []
        count = 0
        neighborsToVisit = [p]
        seen = set()
        while len(neighborsToVisit) != 0:
            p1 = neighborsToVisit.pop()
            count += 1
            seen.add(p1)
            neighbors = list(emptyNeighbors(p1))
            if len(neighbors) == 1:
                singles.append(neighbors[0])
            for n in neighbors:
                if n not in seen:
                    neighborsToVisit.append(n)
        if count in impossibleSizes:
            return False
        for point in singles:
            sc = 1
            while True:
                seen1 = False
                for n in emptyNeighbors(point):
                    if n == point:
                        continue
                    if seen1:
                        break
                    seen1 = True
                else:
                    # only 1 neighbor, not including previous point
                    sc += 1
                    point = n
                    continue
                # more than one neighbour, break
                break
            if sc >= 7:
                return False
            elif sc >= 6:
                return p <= 0
            elif sc >= 5:
                return p <= 5
            elif sc >= 3:
                return p <= 7
            elif sc >= 2:
                return p <= 10
    return True

def place(p, outFile, placements=None):
    global board
    if placements is None:
        placements = []
    for points, (zb, rb, cb) in zip(orientedPieces[p], boundaries[p]):
        for zo, ro, co in product(
            range(BDEPTH-zb),
            range(BHEIGHT-rb),
            range(BWIDTH-cb)
        ):
            if co == BWIDTH-cb-1:
                break # profiling test
            # place piece
            placements.append([])
            for zd, rd, cd in points:
                z = zo+zd
                r = ro+rd
                c = co+cd
                if board[z][r][c] in EMPTYCHARS:
                    board[z][r][c] = '1'
                    placements[-1].append((z, r, c))
                else:
                    # position conflicts with placed piece
                    breakat = (z, r, c)
                    break
            else:
                # sucessfully placed a piece
                breakat = None
                if checkSolvable(p+1):
                    if p == len(pieces)-1:
                        printSolvedGrid(placements, outFile)
                    else:
                        place(p+1, outFile, placements)
            # remove piece
            placements.pop()
            for zd, rd, cd in points:
                z = zo+zd
                r = ro+rd
                c = co+cd
                if (z, r, c) == breakat:
                    break
                board[z][r][c] = PREFERREDEMPTY

def main(outfileName):
    with open(outfileName, 'w') as f:
        place(11, f) # changed from 0 to profile

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('expected file for solutions.')
        sys.exit()
    else:
        file = sys.argv[1]
    main(file)

