from typing import List

from z3 import Not, BoolRef, unsat

from symtvm.state.concreteslice import ConcreteSlice
from symtvm.state.exit_codes import VmExitStatus, TypeCheckError, StackUnderflow
from symtvm.state.sym_state import TvmState
from symtvm.state.symcell import SymCell
from symtvm.state.types import StackEntry
from symtvm.transition.successors import Successors


class InsnContext:
    def __init__(self, state: TvmState, parent_state: TvmState = None):
        self.finished = False
        self.parent_state = parent_state.copy() if parent_state is not None else state.copy()
        self.state = state
        self.successors = Successors()

    def push(self, stackentry):
        self.state.push(stackentry)

    def push_int(self, expr):
        self.state.push(StackEntry.int(expr))

    def push_cell(self, expr: SymCell):
        self.state.push(StackEntry.cell(expr.cell))

    def push_slice(self, expr: SymCell):
        self.state.push(StackEntry.slice(expr.cell))

    def push_builder(self, expr: SymCell):
        self.state.push(StackEntry.builder(expr.cell))

    def push_continuation(self, cont: ConcreteSlice):
        self.state.push(cont)

    def error(self, exception: VmExitStatus, constraints: List[BoolRef]):
        self.successors.err(self.state.error(self.parent_state, exception, constraints))

    def typecheck(self, expr, expected):
        self.error(TypeCheckError(expected, expr), [Not(getattr(StackEntry, f"is_{expected}")(expr))])
        return expr

    def stackunderflowcheck(self, n):
        self.error(StackUnderflow(), [n > len(self.state.stack)])

    def pop(self, n=1):
        self.stackunderflowcheck(n)
        return self.state.pop(n)

    def pop_int(self):
        return StackEntry.int_val(self.typecheck(self.pop(), "int"))

    def pop_cell(self) -> SymCell:
        return SymCell(StackEntry.cell_val(self.typecheck(self.pop(), "cell")), self.error)

    def pop_slice(self) -> SymCell:
        return SymCell(StackEntry.slice_val(self.typecheck(self.pop(), "slice")), self.error)

    def pop_builder(self) -> SymCell:
        return SymCell(StackEntry.builder_val(self.typecheck(self.pop(), "builder")), self.error)

    def pop_continuation(self):
        c = self.pop()
        assert type(c) == ConcreteSlice, "Continuation must be concrete"
        return c

    def empty_cell(self):
        return SymCell.empty(self.error)

    def s(self, i):
        self.stackunderflowcheck(i + 1)
        return self.state.s(i)

    def drop(self, n=1):
        self.stackunderflowcheck(n)
        self.state.drop(n)

    def exchange(self, i, j):
        self.stackunderflowcheck(max(i, j) + 1)
        self.state.exchange(i, j)

    def branch(self, condition):
        taken_state = self.state.copy()
        taken_state.add_constraints(condition)
        self.state.add_constraints(Not(condition))
        return InsnContext(self.state.copy(), self.parent_state)

    def join(self, branched_context: "InsnContext"):
        self.successors.add_all(branched_context.finalize())

    def finish(self):
        self.finished = True

    def finalize(self):
        if self.state.solver.check() == unsat:
            self.successors.add_unsat(self.state)
        elif not self.finished:
            self.successors.ok(self.state)
        else:
            self.successors.finish(self.state)
        return self.successors
