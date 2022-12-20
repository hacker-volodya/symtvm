import tvm_valuetypes
from z3 import *

from instructions.operand_parsers import load_uint, load_int
from instructions.registry import insn
from tvm_primitives import StackEntry, Cell, CellData, CellDataIndex, ConcreteSlice, Slice, Int257, \
    symcell_preload_bits, symcell_preload_uint, CellHash, CheckSignatureUInt
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


@insn("A6cc", custom_decoders={"c": load_int})
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


@insn("2i")
def push(state: TvmState, i: int):
    successors = Successors()
    state.push(state.s(i))
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
    if i > 10:
        i -= 16
    successors = Successors()
    state.push(i)
    successors.ok(state)
    return successors


@insn("80xx", custom_decoders={"x": load_int})
@insn("81xxxx", custom_decoders={"x": load_int})
def push_const_int(state: TvmState, x):
    successors = Successors()
    state.push(StackEntry.int(x))
    successors.ok(state)
    return successors


@insn("82lxxx", custom_decoders={
    "l": lambda cc, kwargs, size: load_uint(cc, None, 5),
    "x": lambda cc, kwargs, size: load_int(cc, None, 8 * kwargs["l"] + 19),
})
def push_const_int_wide(state: TvmState, l, x):
    successors = Successors()
    state.push(StackEntry.int(x))
    successors.ok(state)
    return successors


@insn("9xccc", custom_decoders={
    "c": lambda cc, kwargs, size: cc.load_bits(kwargs["x"] * 8),
})
def cont(state: TvmState, x, c):
    successors = Successors()
    continuation = ConcreteSlice(tvm_valuetypes.Cell())
    continuation.data.data = c
    state.push(continuation)
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


@insn("D0")
def ctos(state: TvmState):
    successors = Successors()
    state.push(StackEntry.slice(Slice.slice(StackEntry.cell_val(state.pop()))))
    successors.ok(state)
    return successors


@insn("D1")
def ends(state: TvmState):
    successors = Successors()
    s = Slice.cell(StackEntry.slice_val(state.pop()))
    state.constraints.append(Cell.data_len(s) == 0)
    successors.ok(state)
    successors.err(state.error("Slice is not empty", [Cell.data_len(s) != 0]))
    return successors


@insn("D3cc")
def ldu(state: TvmState, c):
    successors = Successors()
    s = Slice.cell(StackEntry.slice_val(state.pop()))
    state.push(StackEntry.int(symcell_preload_uint(s, c + 1)))
    s1 = StackEntry.slice(Slice.slice(Cell.cell(Cell.data(s) << (c + 1), Cell.data_len(s) - (c + 1))))
    state.push(s1)
    successors.ok(state)
    return successors


@insn("D4")
def ldref(state: TvmState):
    successors = Successors()
    successors.ok(state)
    return successors


@insn("D70Bcc")
def pldu(state: TvmState, c):
    successors = Successors()
    s = Slice.cell(StackEntry.slice_val(state.pop()))
    state.push(StackEntry.int(symcell_preload_uint(s, c + 1)))
    successors.ok(state)
    return successors


@insn("D718")
def ldslicex(state: TvmState):
    successors = Successors()
    l = Extract(9, 0, StackEntry.int_val(state.pop()))
    s = Slice.cell(StackEntry.slice_val(state.pop()))
    split_at = If(Cell.data_len(s) < l, Cell.data_len(s), l)
    s2 = StackEntry.slice(Slice.slice(Cell.cell(Cell.data(s), split_at)))
    s1 = StackEntry.slice(Slice.slice(Cell.cell(Cell.data(s) << ZeroExt(1013, split_at), Cell.data_len(s) - split_at)))
    state.push(s2)
    state.push(s1)
    successors.ok(state)
    return successors


@insn("D9")
def jmpx(state: TvmState):
    successors = Successors()
    continuation = state.pop()
    assert type(continuation) == ConcreteSlice, "Continuation must be concrete"
    state.cc = continuation
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


@insn("E0")
def ifjmp(state: TvmState):
    successors = Successors()
    continuation = state.pop()
    cond = state.pop()
    assert type(continuation) == ConcreteSlice, "Continuation must be concrete"
    state_jmp = state.copy()
    state_jmp.constraints.append(cond != StackEntry.int(0))
    state_jmp.cc = continuation
    successors.ok(state_jmp)
    state.constraints.append(cond == StackEntry.int(0))
    successors.ok(state)
    return successors


@insn("ED4i")
def pushctr(state: TvmState, i: int):
    successors = Successors()
    if state.regs.get(i) is None:
        reg_val = Const(f"regs_c{i}", Cell)
        state.push(StackEntry.cell(reg_val))
        state.regs[i] = reg_val
    else:
        state.push(StackEntry.cell(state.regs[i]))
    successors.ok(state)
    return successors


@insn("ED5i")
def popctr(state: TvmState, i: int):
    successors = Successors()
    state.regs[i] = StackEntry.cell_val(state.pop())
    successors.ok(state)


@insn("F26_n")
def throwif(state: TvmState, n: int):
    successors = Successors()
    f = state.pop()
    throw_state = state.copy()
    throw_state.constraints.append(f != StackEntry.int(0))
    throw_state.stack = [StackEntry.int(0), StackEntry.int(n)]
    state.constraints.append(f == StackEntry.int(0))
    successors.ok(state)
    if throw_state.regs.get(2) is not None:
        throw_state.cc = throw_state.regs[2]
        successors.ok(throw_state)
    else:
        successors.finish(throw_state)
    return successors


@insn("F2A_n")
def throwifnot(state: TvmState, n: int):
    successors = Successors()
    f = state.pop()
    throw_state = state.copy()
    throw_state.constraints.append(f == StackEntry.int(0))
    throw_state.stack = [StackEntry.int(0), StackEntry.int(n)]
    state.constraints.append(f != StackEntry.int(0))
    successors.ok(state)
    if throw_state.regs.get(2) is not None:
        throw_state.cc = throw_state.regs[2]
        successors.ok(throw_state)
    else:
        successors.finish(throw_state)
    return successors


@insn("F800")
def accept(state: TvmState):
    successors = Successors()
    successors.ok(state)
    return successors


@insn("F900")
def hashcu(state: TvmState):
    successors = Successors()
    c = StackEntry.cell_val(state.pop())
    state.push(CellHash(c))
    successors.ok(state)
    return successors


@insn("F901")
def hashsu(state: TvmState):
    successors = Successors()
    c = Slice.cell(StackEntry.slice_val(state.pop()))
    state.push(CellHash(c))
    successors.ok(state)
    return successors


@insn("F910")
def checksignu(state: TvmState):
    successors = Successors()
    k = StackEntry.int_val(state.pop())
    s = Slice.cell(StackEntry.slice_val(state.pop()))
    h = StackEntry.int_val(state.pop())
    state.push(CheckSignatureUInt(h, s, k))
    successors.ok(state)
    return successors
