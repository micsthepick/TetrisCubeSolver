# some prerequisite definitions for the Tetris cube solver.
from itertools import product
try:
    from itertools import izip as zip
except ImportError:
    pass


def count(var):
    return range(len(var))

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
    for a, b in zip(product(range(dim[hn]), range(dim[rn]), range(dim[cn])),
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


def print3D(array):
    text = ''
    for r in count(array[0]):
        for h in count(array):
            for c in count(array[0][0]):
                text += array[h][r][c] + ' '
            text += '   '
        text += '\n'
    text = text[:-2]
    return text

