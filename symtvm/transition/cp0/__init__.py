import tvm_valuetypes
from z3 import *

from symtvm.decoder.operand_parsers import load_uint, load_int
from symtvm.state.types import Int257, Cell, StackEntry
from symtvm.state.concreteslice import ConcreteSlice
from symtvm.state.exit_codes import *
from symtvm.state.types import CheckSignatureUInt, CellData
from symtvm.transition.context import InsnContext
from symtvm.transition.registry import insn


@insn("FF00")
def setcp0(ctx: InsnContext):
    pass


@insn("A0")
def add(ctx: InsnContext):
    a = ctx.pop_int()
    b = ctx.pop_int()
    ctx.error(IntegerOverflow(), [Or(Not(BVAddNoUnderflow(a, b)), Not(BVAddNoOverflow(a, b, signed=True)))])
    ctx.push_int(a + b)


@insn("A1")
def sub(ctx: InsnContext):
    a = ctx.pop_int()
    b = ctx.pop_int()
    ctx.error(IntegerOverflow(), [Or(Not(BVSubNoOverflow(a, b)), Not(BVSubNoUnderflow(a, b, signed=True)))])
    ctx.push_int(a - b)


@insn("A6cc", custom_decoders={"c": load_int})
def addconst(ctx: InsnContext, c):
    a = ctx.pop_int()
    b = Int257.cast(c)
    ctx.error(IntegerOverflow(), [Or(Not(BVAddNoUnderflow(a, b)), Not(BVAddNoOverflow(a, b, signed=True)))])
    ctx.push_int(a + b)


@insn("A4")
def inc(ctx: InsnContext):
    addconst(ctx, c=1)


@insn("A5")
def dec(ctx: InsnContext):
    addconst(ctx, c=-1)


@insn("2i")
def push(ctx: InsnContext, i: int):
    ctx.push(ctx.s(i))


@insn("30")
def drop(ctx: InsnContext):
    ctx.drop()


@insn("10ij")
def xchg(ctx: InsnContext, i, j):
    ctx.exchange(i, j)


@insn("0i")
def xchg0(ctx: InsnContext, i):
    xchg(ctx, 0, i)


@insn("50ij")
def xchg2(ctx: InsnContext, i, j):
    xchg(ctx, 1, i)
    xchg0(ctx, j)


@insn("541ijk")
def xc2pu(ctx: InsnContext, i, j, k):
    xchg2(ctx, i, j)
    push(ctx, k)


@insn("51ij")
def xcpu(ctx: InsnContext, i, j):
    xchg0(ctx, i)
    push(ctx, j)


@insn("31")
def nip(ctx: InsnContext):
    ctx.pop(2)


@insn("7i")
def push_const_smallint(ctx: InsnContext, i):
    if i > 10:
        i -= 16
    ctx.push_int(Int257.cast(i))


@insn("80xx", custom_decoders={"x": load_int})
@insn("81xxxx", custom_decoders={"x": load_int})
@insn("82lxxx", custom_decoders={
    "l": lambda cc, kwargs, size: load_uint(cc, None, 5),
    "x": lambda cc, kwargs, size: load_int(cc, None, 8 * kwargs["l"] + 19),
})
def push_const_int(ctx: InsnContext, x, l=None):
    ctx.push_int(Int257.cast(x))


@insn("9xccc", custom_decoders={
    "c": lambda cc, kwargs, size: cc.load_bits(kwargs["x"] * 8),
})
def cont(ctx: InsnContext, x, c):
    continuation = ConcreteSlice(tvm_valuetypes.Cell())
    continuation.data.data = c
    ctx.push_continuation(continuation)


@insn("C8")
def newc(ctx: InsnContext):
    ctx.push_builder(ctx.empty_cell())


@insn("C9")
def endc(ctx: InsnContext):
    ctx.push_cell(ctx.pop_builder())


@insn("CBcc")
def stu(ctx: InsnContext, c: int):
    c += 1
    b = ctx.pop_builder()
    x = ctx.pop_int()
    b.store_int(x, c, signed=False)
    ctx.push_builder(b)


@insn("BA")
def equal(ctx: InsnContext):
    a = ctx.pop_int()
    b = ctx.pop_int()
    ctx.push_int(If(a == b, Int257.cast(-1), Int257.cast(0)))


@insn("D0")
def ctos(ctx: InsnContext):
    ctx.push_slice(ctx.pop_cell())


@insn("D1")
def ends(ctx: InsnContext):
    s = ctx.pop_slice()
    ctx.error(CellUnderflow(), [Or(s.data_size() != 0, s.ref_size() != 0)])


@insn("D3cc")
def ldu(ctx: InsnContext, c):
    c += 1
    s = ctx.pop_slice()
    ctx.push_int(s.load_int(c, signed=False))
    ctx.push_slice(s)


@insn("D4")
def ldref(ctx: InsnContext):
    s = ctx.pop_slice()
    ctx.push_cell(s.load_ref())
    ctx.push_slice(s)


@insn("D70Bcc")
def pldu(ctx: InsnContext, c):
    c += 1
    s = ctx.pop_slice()
    ctx.push_int(s.preload_int(c, signed=False))


@insn("D718")
def ldslicex(ctx: InsnContext):
    split_at = ctx.pop_int()
    s = ctx.pop_slice()
    ctx.error(OutOfRange(), [UGT(split_at, CellData.size())])
    bits = s.load_bits(split_at)
    s2 = ctx.empty_cell()
    s2.store_bits(bits, split_at, check_overflow=False)
    ctx.push_slice(s2)
    ctx.push_slice(s)


@insn("D9")
def jmpx(ctx: InsnContext):
    ctx.state.cc = ctx.pop_continuation()


@insn("DD")
def ifnotret(ctx: InsnContext):
    a = ctx.pop_int()
    ret_ctx = ctx.branch(a == Int257.cast(0))
    if ret_ctx.state.regs.get(0) is not None:
        ret_ctx.state.cc = ret_ctx.state.regs[0]
    else:
        ret_ctx.finish()
    ctx.join(ret_ctx)


@insn("E0")
def ifjmp(ctx: InsnContext):
    continuation = ctx.pop_continuation()
    cond = ctx.pop_int()
    ctx_jmp = ctx.branch(cond != 0)
    ctx_jmp.state.cc = continuation
    ctx.join(ctx_jmp)


@insn("ED4i")
def pushctr(ctx: InsnContext, i: int):
    if ctx.state.regs.get(i) is None:
        reg_val = Const(f"regs_c{i}", Cell)
        ctx.state.regs[i] = reg_val
    ctx.push_cell(ctx.state.regs[i])


@insn("ED5i")
def popctr(ctx: InsnContext, i: int):
    ctx.state.regs[i] = ctx.pop_cell()


@insn("F26_n")
def throwif(ctx: InsnContext, n: int):
    f = ctx.pop_int()
    throw_ctx = ctx.branch(f != 0)
    throw_ctx.state.stack = [StackEntry.int(0), StackEntry.int(n)]
    if throw_ctx.state.regs.get(2) is not None:
        throw_ctx.state.cc = throw_ctx.state.regs[2]
    else:
        throw_ctx.finish()
    ctx.join(throw_ctx)


@insn("F2A_n")
def throwifnot(ctx: InsnContext, n: int):
    f = ctx.pop_int()
    throw_ctx = ctx.branch(f == 0)
    throw_ctx.state.stack = [StackEntry.int(0), StackEntry.int(n)]
    if throw_ctx.state.regs.get(2) is not None:
        throw_ctx.state.cc = throw_ctx.state.regs[2]
    else:
        throw_ctx.finish()
    ctx.join(throw_ctx)


@insn("F800")
def accept(ctx: InsnContext):
    pass


@insn("F900")
def hashcu(ctx: InsnContext):
    ctx.push_int(ctx.pop_cell().reprhash())


@insn("F901")
def hashsu(ctx: InsnContext):
    ctx.push_int(ctx.pop_slice().reprhash())


@insn("F910")
def checksignu(ctx: InsnContext):
    k = ctx.pop_int()
    s = ctx.pop_slice()
    h = ctx.pop_int()
    ctx.push_int(CheckSignatureUInt(h, s.cell, k))


@insn("FB00")
def sendrawmsg(ctx: InsnContext):
    x = ctx.pop_int()
    c = ctx.pop_cell()
    actions = ctx.state.regs.get(5, [])
    actions.append((c, x))
    ctx.state.regs[5] = actions
