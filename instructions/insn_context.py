from typing import List

from z3 import Not, Int, BoolRef

from exceptions import TypeCheckError, StackUnderflow, VmError
from tvm_primitives import StackEntry, ConcreteSlice
from tvm_state import TvmState
from tvm_successors import Successors


class InsnContext:
    def __init__(self, state: TvmState):
        self.state = state
        self.successors = Successors()

    def push_int(self, expr):
        self.state.push(StackEntry.int(expr))

    def push_cell(self, expr):
        self.state.push(StackEntry.cell(expr))

    def push_slice(self, expr):
        self.state.push(StackEntry.slice(expr))

    def push_builder(self, expr):
        self.state.push(StackEntry.builder(expr))

    def push_continuation(self, cont: ConcreteSlice):
        self.state.push(cont)

    def error(self, exception: VmError, constraints: List[BoolRef]):
        self.successors.err(self.state.error(exception, constraints))

    def typecheck(self, expr, expected):
        self.error(TypeCheckError(expected, expr), [Not(getattr(StackEntry, f"is_{expected}")(expr))])
        return expr

    def stackunderflowcheck(self, n):
        self.error(StackUnderflow(), [Int(n) > Int(len(self.state.stack))])

    def _pop(self):
        self.stackunderflowcheck(1)
        return self.state.pop()

    def pop_int(self):
        return StackEntry.int_val(self.typecheck(self._pop(), "int"))

    def pop_cell(self):
        return StackEntry.cell_val(self.typecheck(self._pop(), "cell"))

    def pop_slice(self):
        return StackEntry.slice_val(self.typecheck(self._pop(), "slice"))

    def pop_builder(self):
        return StackEntry.builder_val(self.typecheck(self._pop(), "builder"))

    def s(self, i):
        self.stackunderflowcheck(i + 1)
        return self.state.s(i)

    def drop(self, n=1):
        self.stackunderflowcheck(n)
        self.state.drop(n)

    def exchange(self, i, j):
        self.stackunderflowcheck(max(i, j) + 1)
        self.state.exchange(i, j)

    def finalize(self):
        self.successors.ok(self.state)
        return self.successors
