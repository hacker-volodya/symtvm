from cell import StackEntry, Cell, Int257
from z3 import *


class TVMState:
    def __init__(self, stack, cc):
        self.stack = stack
        self.cc = cc


def add(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(StackEntry.int(StackEntry.int_val(a) + StackEntry.int_val(b)))


def sub(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(StackEntry.int(StackEntry.int_val(a) - StackEntry.int_val(b)))


def newc(stack):
    stack.append(StackEntry.builder(Cell.cell(BitVec('cell_x', 1023))))


def test_tvm():
    stack = [StackEntry.int(1), StackEntry.int(2), StackEntry.int(Const('x', Int257))]
    add(stack)
    sub(stack)
    newc(stack)
    print(simplify(stack[-1]))


if __name__ == '__main__':
    test_tvm()
