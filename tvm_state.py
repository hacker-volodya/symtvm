from typing import Union, List

from z3 import BoolRef

from tvm_primitives import ConcreteSlice, Cell, Int257, StackEntry, Slice


class TvmState:
    def __init__(self, cc: ConcreteSlice, stack=None, actions=None, regs=None, constraints=None, gl=0, gc=0, gr=0,
                 gm=0):
        if actions is None:
            actions = []
        if stack is None:
            stack = []
        if regs is None:
            regs = {
                # default regs value
            }
        if constraints is None:
            constraints = []
        self.constraints = constraints
        self.actions = actions
        self.stack = stack
        self.cc = cc
        self.regs = regs
        self.gl = gl
        self.gc = gc
        self.gr = gr
        self.gm = gm

    def copy(self):
        return TvmState(self.cc.copy(),
                        self.stack.copy(),
                        self.actions.copy(),
                        self.regs.copy(),
                        self.constraints.copy(),
                        self.gl,
                        self.gc,
                        self.gr,
                        self.gm)

    @classmethod
    def send_message(cls, code: ConcreteSlice, data: Cell, body: Cell, selector: Int257):
        return TvmState(code, [StackEntry.slice(Slice.slice(body)), StackEntry.int(selector)], regs={4: data})

    @classmethod
    def call_getmethod(cls):
        pass

    def s(self, i):
        return self.stack[-1 - i]

    def exchange(self, i, j):
        self.stack[-1 - i], self.stack[-1 - j] = self.stack[-1 - j], self.stack[-1 - i]

    def push(self, v):
        self.stack.append(v)

    def pop(self):
        return self.stack.pop()

    def drop(self, n=1):
        self.stack = self.stack[:-n]

    def error(self, exception: Union[Exception, str], constraints: List[BoolRef]):
        return TvmErrorState(self, exception, self.constraints + constraints)

    def __repr__(self):
        return f"TvmState @ {self.cc.hash().hex()[:6]}:{self.cc.data_off}"


class TvmErrorState:
    def __init__(self, parent_state: TvmState, exception: Union[Exception, str], constraints: List[BoolRef]):
        self.parent_state = parent_state.copy()
        self.exception = exception
        self.constraints = constraints

    def __repr__(self):
        return f"TvmErrorState <{self.parent_state!r}>: {self.exception}"