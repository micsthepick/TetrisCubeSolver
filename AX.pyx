#cython: language_level=3, profile=True
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from cython.operator cimport dereference as deref

cdef struct Node:
    Node* L
    Node* U
    Node* R
    Node* D
    Node* C
    int S
    int id

cdef Node* create_node():
    cdef Node* node = <Node *>PyMem_Malloc(sizeof(Node))
    if not node:
        raise MemoryError()
    deref(node).L = node
    deref(node).U = node
    deref(node).R = node
    deref(node).D = node
    deref(node).C = node
    deref(node).S = 0
    return node

cdef void destroy_node(Node* node):
    PyMem_Free(node)

cdef void _cover(Node* c):
    cdef Node* i
    cdef Node* j

    deref(deref(c).L).R = deref(c).R
    deref(deref(c).R).L = deref(c).L

    i = deref(c).D
    while i is not c:
        j = deref(i).R
        while j is not i:
            deref(deref(j).U).D = deref(j).D
            deref(deref(j).D).U = deref(j).U
            deref(deref(j).C).S -= 1
            j = deref(j).R
        i = deref(i).D

cdef void _uncover(Node* c):
    cdef Node* i
    cdef Node* j

    i = deref(c).U
    while i is not c:
        j = deref(i).L
        while j is not i:
            deref(deref(j).U).D = j
            deref(deref(j).D).U = j
            deref(deref(j).C).S += 1
            j = deref(j).L
        i = deref(i).U

    deref(deref(c).L).R = c
    deref(deref(c).R).L = c

cdef bint is_self_linked(Node* h):
    return deref(h).R is h

cdef Node* scan_right(Node* h):
    cdef Node* cur = deref(h).R
    cdef Node* col = <Node*>0
    while cur is not h:
        if not col or deref(cur).S < deref(col).S:
            col = cur
        cur = deref(cur).R
    return col

cdef void cover_right(Node* cur, Node* r):
    while cur is not r:
        _cover(deref(cur).C)
        cur = deref(cur).R

cdef void cover_left(Node* cur, Node* l):
    while cur is not l:
        _uncover(deref(cur).C)
        cur = deref(cur).L

cdef class AlgorithmX:
    cdef size_t* cols
    cdef size_t col_len
    cdef dict tags
    cdef int rows
    cdef int limit
    cdef Node* h

    def __init__(self, cols):
        assert cols >= 0, "Number of columns must be non-negative"
        self.cols =  <size_t*>PyMem_Malloc(cols * sizeof(size_t))
        if not self.cols:
            raise MemoryError()
        self.col_len = cols
        self.tags = {}
        self.rows = 0
        self.h = create_node()
        self.tags[<size_t>self.h] = None

        last = self.h
        for i in range(cols):
            cur = create_node()
            self.tags[<size_t>cur] = None
            deref(last).R = cur
            deref(cur).L = last
            last = cur
            self.cols[i] = <size_t>cur

        deref(last).R = self.h
        deref(self.h).L = last

    def __dealloc__(self):
        for node in self.tags.keys():
            destroy_node(<Node*>node)
        PyMem_Free(self.cols)


    def appendRow(self, cols, tag=None):
        if tag is None:
            tag = self.rows

        cols = list(sorted(set(cols)))
        first = <Node*>0
        last = <Node*>0
        for idx in cols:
            assert 0 <= idx < self.col_len, "Column index must be between 0 and number of columns - 1"

            deref(<Node*>self.cols[idx]).S += 1

            cur = create_node()
            self.tags[<size_t>cur] = tag
            if not first:
                first = cur

            deref(cur).U = deref(<Node*>self.cols[idx]).U
            deref(deref(cur).U).D = cur
            deref(cur).D = <Node*>self.cols[idx]
            deref(deref(cur).D).U = cur
            deref(cur).C = <Node*>self.cols[idx]

            if last:
                deref(last).R = cur
                deref(cur).L = last

            last = cur

        if first:
            deref(last).R = first
            deref(first).L = last

        self.rows += 1

    def _solve(self):
        if is_self_linked(self.h):
            yield []
            return

        if self.limit != -2:
            self.limit -= 1
            if self.limit == -1:
                return

        cdef Node* col = scan_right(self.h)

        _cover(col)

        cdef Node* r = deref(col).D

        while r is not col:
            cover_right(deref(r).R, r)

            for sol in self._solve():
                yield [self.tags[<size_t>r]] + sol

            cover_left(deref(r).L, r)

            r = deref(r).D

        _uncover(col)

    def solve(self, limit=-2):
        self.limit = limit
        c = self._solve()
        return c
