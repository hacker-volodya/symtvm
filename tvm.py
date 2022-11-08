from cell import *
from z3 import *

from tvm_insns import *


class TVMState:
    def __init__(self, stack, cc):
        self.stack = stack
        self.cc = cc


def test_tvm():
    stack = [StackEntry.int(1), StackEntry.int(2), StackEntry.int(Const('x', Int257))]
    add(stack)
    equal(stack)
    print(simplify(stack[-1]))


if __name__ == '__main__':
    test_tvm()
