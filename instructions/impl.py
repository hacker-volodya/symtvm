from bitarray.util import ba2int
from z3 import *

from instructions.registry import insn
from tvm_primitives import StackEntry, Cell, CellData, CellDataIndex
from tvm_state import TvmState
from tvm_successors import Successors


@insn("FF00")
def setcp0(state: TvmState):
    successors = Successors()
    successors.ok(state)
    return successors


@insn("A0")
def add(state: TvmState):
    successors = Successors()
    a = StackEntry.int_val(state.pop())
    b = StackEntry.int_val(state.pop())
    is_overflow = BVAddNoOverflow(a, b, signed=True)
    is_underflow = BVAddNoUnderflow(a, b)
    successors.err(state.error("int overflow", [is_overflow]))
    successors.err(state.error("int underflow", [is_underflow]))
    state.push(StackEntry.int(a + b))
    successors.ok(state)
    return successors


@insn("A1")
def sub(state: TvmState):
    successors = Successors()
    a = StackEntry.int_val(state.pop())
    b = StackEntry.int_val(state.pop())
    is_overflow = BVSubNoOverflow(a, b)
    is_underflow = BVSubNoUnderflow(a, b, signed=True)
    successors.err(state.error("int overflow", [is_overflow]))
    successors.err(state.error("int underflow", [is_underflow]))
    state.push(StackEntry.int(a - b))
    successors.ok(state)
    return successors


@insn("A6cc")
def addconst(state: TvmState, c):
    successors = Successors()
    a = StackEntry.int_val(state.pop())
    b = StackEntry.int_val(StackEntry.int(c))
    is_overflow = BVAddNoOverflow(a, b, signed=True)
    is_underflow = BVAddNoUnderflow(a, b)
    successors.err(state.error("int overflow", [is_overflow]))
    successors.err(state.error("int underflow", [is_underflow]))
    state.push(StackEntry.int(a + b))
    successors.ok(state)
    return successors


@insn("A4")
def inc(state: TvmState):
    return addconst(state, c=1)


@insn("A5")
def dec(state: TvmState):
    return addconst(state, c=-1)


@insn("20")
def dup(state: TvmState):
    successors = Successors()
    state.push(state.s(0))
    successors.ok(state)
    return successors


@insn("30")
def drop(state: TvmState):
    successors = Successors()
    state.drop()
    successors.ok(state)
    return successors


@insn("10ij")
def xchg(state: TvmState, i, j):
    successors = Successors()
    state.exchange(i, j)
    successors.ok(state)
    return successors


@insn("0i")
def xchg0(state: TvmState, i):
    return xchg(state, 0, i)


@insn("50ij")
def xchg2(state: TvmState, i, j):
    successors = Successors()
    successors.add_err(xchg(state, 1, i))
    successors.add_err(xchg0(state, j))
    successors.ok(state)
    return successors


@insn("541ijk")
def xc2pu(state: TvmState, i, j, k):
    successors = Successors()
    successors.add_err(xchg2(state, i, j))
    successors.add_err(push(state, k))
    successors.ok(state)
    return successors


@insn("51ij")
def xcpu(state: TvmState, i, j):
    successors = Successors()
    successors.add_err(xchg0(state, i))
    successors.add_err(push(state, j))
    successors.ok(state)
    return successors


@insn("2i")
def push(state: TvmState, i):
    successors = Successors()
    state.push(state.s(i))
    successors.ok(state)
    return successors


@insn("31")
def nip(state: TvmState):
    successors = Successors()
    state.stack.pop(-2)
    successors.ok(state)
    return successors


@insn("7i")
def push_const_smallint(state: TvmState, i):
    successors = Successors()
    state.push(i)
    successors.ok(state)
    return successors


@insn("80xx")
@insn("81xxxx")
def push_const_int(state: TvmState, x):
    successors = Successors()
    state.push(StackEntry.int(x))
    successors.ok(state)
    return successors


@insn("82lxxx", custom_decoders={
    "l": lambda cc, kwargs, size: ba2int(cc.load_bits(5), signed=False),
    "x": lambda cc, kwargs, size: ba2int(cc.load_bits(8 * kwargs["l"] + 19), signed=True),
})
def push_const_int_wide(state: TvmState, l, x):
    successors = Successors()
    state.push(StackEntry.int(x))
    successors.ok(state)
    return successors


@insn("C8")
def newc(state: TvmState):
    successors = Successors()
    state.push(StackEntry.builder(Cell.cell(CellData.cast(0), CellDataIndex.cast(0))))
    successors.ok(state)
    return successors


@insn("BA")
def equal(state: TvmState):
    successors = Successors()
    a = state.pop()
    b = state.pop()
    state.push(If(a == b, StackEntry.int(-1), StackEntry.int(0)))
    successors.ok(state)
    return successors


@insn("DD")
def ifnotret(state: TvmState):
    successors = Successors()
    a = state.pop()
    ret_state = state.copy()
    ret_state.constraints.append(a == StackEntry.int(0))
    if state.regs.get(0) is not None:
        ret_state.cc = state.regs[0]
        successors.ok(ret_state)
    else:
        successors.finish(ret_state)
    state.constraints.append(a != StackEntry.int(0))
    successors.ok(state)
    return successors
