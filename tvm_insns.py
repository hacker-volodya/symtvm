from z3 import *

from cell import StackEntry, Cell, Int257, CellData, CellDataIndex


def add(stack):
    a = StackEntry.int_val(stack.pop())
    b = StackEntry.int_val(stack.pop())
    is_overflow = BVAddNoOverflow(a, b, signed=True)
    is_underflow = BVAddNoUnderflow(a, b)
    stack.append(StackEntry.int(a + b))


def sub(stack):
    a = StackEntry.int_val(stack.pop())
    b = StackEntry.int_val(stack.pop())
    is_overflow = BVSubNoOverflow(a, b)
    is_underflow = BVSubNoUnderflow(a, b, signed=True)
    stack.append(StackEntry.int(a - b))


def addconst(stack, const):
    a = StackEntry.int_val(stack.pop())
    b = StackEntry.int_val(StackEntry.int(const))
    is_overflow = BVAddNoOverflow(a, b, signed=True)
    is_underflow = BVAddNoUnderflow(a, b)
    stack.append(StackEntry.int(a + b))


def inc(stack):
    addconst(stack, 1)


def dec(stack):
    addconst(stack, -1)


def dup(stack):
    stack.append(stack[-1])


def drop(stack):
    stack.pop()


def xchg(stack, i, j):
    stack[-1 - j], stack[-1 - i] = stack[-1 - i], stack[-1 - j]


def xchg0(stack, i):
    xchg(stack, 0, i)


def xchg2(stack, i, j):
    xchg(stack, 1, i)
    xchg0(stack, j)


def xc2pu(stack, i, j, k):
    xchg2(stack, i, j)
    push(stack, k)


def xcpu(stack, i, j):
    xchg0(stack, i)
    push(stack, j)


def push(stack, i):
    stack.push(stack[-1 - i])


def nip(stack):
    stack.pop(-2)


def push_const_int(stack, value):
    stack.append(StackEntry.int(value))


def newc(stack):
    stack.append(StackEntry.builder(Cell.cell(CellData.cast(0), CellDataIndex.cast(0))))


def equal(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(If(a == b, StackEntry.int(-1), StackEntry.int(0)))
