# ------------------------------------------------------------------------------
# Collections, Iterators, and Algorithms
# ------------------------------------------------------------------------------
# TODO decide: does this belong in commoncode ??

import sys
from collections import deque
from collections.abc import Iterator
from itertools import tee, islice

import logging
log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Collections
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Iterators
# ------------------------------------------------------------------------------
class PeekIter(Iterator):
    """prefetches the current element for the curious"""
    def __init__(self, it):
        self.it, self.nextIt = tee(it)
        self.current = next(self.nextIt, None)

    def __iter__(self):
        return self

    def __next__(self):
        retval = next(self.it)
        self.current = next(self.nextIt, None)
        return retval

    def advanceTo(self, target):
        while self.current is not target:
            next(self)

    def advanceUntil(self, pred):
        while not pred(self.current):
            next(self)


class LoopIter(Iterator):
    """Loop through a collection, starting from anywhere, optionally forever"""
    notSet = object()
    empty  = object()
    def __init__(self, collection, start=notSet, it=None, continuous=False):
        collectIt = iter(collection)
        if collection is collectIt:
            raise TypeError("Need a real collection not just an iterator")
        if it is None:
            if start is self.notSet:
                it = collectIt
            else:
                it = PeekIter(collection)
                it.advanceTo(start)
        self.collection = collection
        self.it         = it
        self.continuous = continuous
        self.start = self.notSet

    def __iter__(self):
        return self

    def __next__(self):
        try:
            retval = next(self.it)
        except StopIteration:
            self.it = iter(self.collection)
            retval = next(self.it)
        if self.start is self.notSet:
            self.start = retval
        elif not self.continuous and self.start is retval:
            self.collection = []
            self.it = iter(self.collection)
            raise StopIteration()
        return retval


class PeekLoopIter(PeekIter):
    """For your convenience"""
    def __init__(self, collection, start=LoopIter.notSet, it=None, continuous=False):
        self.loop = LoopIter(collection, start, it, continuous)
        super().__init__(self.loop)

# ------------------------------------------------------------------------------
# Algorithms
# ------------------------------------------------------------------------------

# from http://docs.python.org/3/library/itertools.html#itertools-recipes
def consume(it, n):
    "Advance the iterator n-steps ahead. If n is none, consume entirely."
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        deque(it, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(it, n, n), None)


def advanceUntilAfter(it, what):
    while next(it) is not what:
        pass

def getNextAfter(it, what):
    advanceUntilAfter(it, what)
    return next(it)


