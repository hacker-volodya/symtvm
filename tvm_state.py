from typing import Union, List

from z3 import BoolRef, Not, Solver, simplify, BoolVal

from instructions.utils import disasm
from symcell import SymCell
from tvm_primitives import ConcreteSlice, Cell, Int257, StackEntry


class TvmState:
    def __init__(self, cc: ConcreteSlice, stack=None, actions=None, regs=None, gl=0, gc=0, gr=0,
                 gm=0, solver=None):
        if actions is None:
            actions = []
        if stack is None:
            stack = []
        if regs is None:
            regs = {
                # default regs value
            }
        if solver is None:
            solver = Solver()
        self.actions = actions
        self.stack = stack
        self.cc = cc
        self.regs = regs
        self.gl = gl
        self.gc = gc
        self.gr = gr
        self.gm = gm
        self.solver = solver

    def copy(self):
        s = Solver()
        s.assert_exprs(self.solver.assertions())
        return TvmState(self.cc.copy(),
                        self.stack.copy(),
                        self.actions.copy(),
                        self.regs.copy(),
                        self.gl,
                        self.gc,
                        self.gr,
                        self.gm,
                        s)

    @classmethod
    def send_message(cls, code: ConcreteSlice, data: SymCell, body: Cell, selector: Int257):
        return TvmState(code, [StackEntry.slice(body), StackEntry.int(selector)], regs={4: data})

    @classmethod
    def call_getmethod(cls):
        pass

    def s(self, i):
        return self.stack[-1 - i]

    def exchange(self, i, j):
        self.stack[-1 - i], self.stack[-1 - j] = self.stack[-1 - j], self.stack[-1 - i]

    def push(self, v):
        self.stack.append(v)

    def pop(self, n=1):
        return self.stack.pop(-n)

    def drop(self, n=1):
        self.stack = self.stack[:-n]

    def error(self, parent_state: "TvmState", exception: Union[Exception, str], constraints: List[BoolRef]):
        s = Solver()
        s.assert_exprs(self.solver.assertions())
        s.add(constraints)
        err = TvmErrorState(parent_state, exception, s)
        for constr in constraints:
            self.add_constraints(Not(constr))
        return err

    def disasm(self, need_print=True):
        cc = self.cc.copy()
        cc.data_off = 0
        d = disasm(cc, self.cc.data_off)
        if need_print:
            print(d)
        else:
            return d

    def add_constraints(self, exprs):
        self.solver.add(exprs)

    def simple_assertions(self):
        return [s for s in [simplify(s) for s in self.solver.assertions()] if not s.eq(BoolVal(True))]

    def simple_stack(self):
        return [simplify(s) for s in self.stack]

    def addr(self):
        return f"{self.cc.hash().hex()[:6]}:{self.cc.data_off}"

    def __repr__(self):
        return f"TvmState @ {self.addr()}"


class TvmErrorState:
    def __init__(self, parent_state: TvmState, exception: Union[Exception, str], solver: Solver):
        self.parent_state = parent_state
        self.exception = exception
        self.solver = solver

    def simple_assertions(self):
        return [s for s in [simplify(s) for s in self.solver.assertions()] if not s.eq(BoolVal(True))]

    def addr(self):
        return self.parent_state.addr()

    def __repr__(self):
        return f"TvmErrorState <{self.parent_state!r}>: {self.exception}"
