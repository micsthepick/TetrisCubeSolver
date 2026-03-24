import random
import numba
from numba import njit, jit
from numba import deferred_type, optional, int64, void
from numba.experimental import jitclass
import numpy as np


node_type = deferred_type()
tag_type = optional(int64[:])

class AlgorithmX:
    def get_uid(self):
        temp = self.node_uid
        self.node_uid += 1
        return temp

    def __init__(self, cols):
        assert cols >= 0, "Number of columns must be non-negative"
        
        self.rows = 0
        self.cols = np.array([AlgorithmX.Node(i) for i in range(cols)])
        self.node_uid = cols
        self.h = self.cols[0]

        last = self.h
        for col in range(cols):
            cur = self.cols[col]
            last.R = cur
            cur.L = last
            last = cur

        last.R = self.h
        self.h.L = last

    @jitclass([
        ('L', node_type),
        ('U', node_type),
        ('R', node_type),
        ('D', node_type),
        ('C', node_type),
        ('S', int64),
        ('id', int64),
        ('tag', tag_type)
    ])
    class Node:
        def __init__(self, id, tag=None):
            self.L = self
            self.U = self
            self.R = self
            self.D = self
            self.C = self
            self.S = 0
            self.id = id
            self.tag = tag

    def appendRow(self, cols, tag=None):

        if tag is None:
            tag = self.rows

        cols = list(sorted(set(cols)))
        first = None
        last = None
        for idx in cols:
            assert 0 <= idx < len(self.cols), "Column index must be between 0 and number of columns - 1"

            self.cols[idx].S += 1

            cur = AlgorithmX.Node(self.get_uid(), tag)
            if first is None:
                first = cur

            cur.U = self.cols[idx].U
            cur.U.D = cur
            cur.D = self.cols[idx]
            cur.D.U = cur
            cur.C = self.cols[idx]

            if last is not None:
                last.R = cur
                cur.L = last

            last = cur

        if first is not None:
            last.R = first
            first.L = last

        self.rows += 1

    def solve(self, limit=None):
        for _, soln in _solve(self.h, limit):
            yield soln

node_type.define(AlgorithmX.Node.class_type.instance_type)

@njit(void(node_type))
def _cover(c):
    c.L.R = c.R
    c.R.L = c.L

    i = c.D
    while i.id != c.id:
        j = i.R
        while j.id !=  i.id:
            j.U.D = j.D
            j.D.U = j.U
            j.C.S -= 1
            j = j.R
        i = i.D

@njit(void(node_type))
def _uncover(c):
    i = c.U
    while i.id != c.id:
        j = i.L
        while j.id != i.id:
            j.U.D = j
            j.D.U = j
            j.C.S += 1
            j = j.L
        i = i.U

    c.L.R = c
    c.R.L = c

@njit(void(node_type,optional(int64)))
def _solve(h, limit):
    if h.R.id == h.id:
        yield (h, [])
        return

    if limit is not None:
        limit -= 1
        if limit < 0:
            return

    col = None
    cur = h.R
    while cur.id != h.id:
        if col is None or cur.S < col.S:
            col = cur
        cur = cur.R

    assert col is not None
    _cover(col)

    r = col.D
    while r.id != col.id:
        cur = r.R
        while cur.id != r.id:
            _cover(cur.C)
            cur = cur.R

        for h1, sol in _solve(h, limit):
            h = h1
            yield (h1, [r.tag] + sol)

        cur = r.L
        while cur.id != r.id:
            _uncover(cur.C)
            cur = cur.L

        r = r.D

    _uncover(col)