from typing import List, Optional, Union

from bitarray import bitarray
from z3 import BitVecRef, BitVecSortRef, Extract, ZeroExt

from symtvm.decoder.bit_utils import ba2hex
from symtvm.decoder.instruction import TvmInstruction
from symtvm.state.concreteslice import ConcreteSlice
from symtvm.state.types import CellData
from symtvm.transition.registry import INSTRUCTIONS


def parse_instruction(cc: ConcreteSlice) -> TvmInstruction:
    bits = 1
    get_ops_with_prefix = lambda bits: match_insn_prefix(cc.preload_bits(bits))
    while len(get_ops_with_prefix(bits)) > 1:
        bits += 1
    ops_list = get_ops_with_prefix(bits)
    if len(get_ops_with_prefix(bits)) == 0:
        raise RuntimeError(f"unknown instruction with prefix {ba2hex(cc.preload_bits(bits))}")
    if ops_list[0] != cc.preload_bits(len(ops_list[0])):
        raise RuntimeError(f"unknown instruction: matched prefix {ba2hex(cc.preload_bits(bits))} \
({INSTRUCTIONS[ops_list[0].to01()].handler.__name__}), got {ba2hex(cc.preload_bits(len(ops_list[0])))}")
    return INSTRUCTIONS[ops_list[0].to01()]


def disasm(cc: ConcreteSlice, mark_off: Optional[int] = None) -> str:
    cc = cc.copy()
    result = []
    try:
        while len(cc.data.data) > cc.data_off:
            insn = parse_instruction(cc)
            next_cc = cc.copy()
            args = insn.try_decode(next_cc)
            result.append(f"{'-> ' if cc.data_off == mark_off else ''}{cc.data_off}: {insn.handler.__name__} {args}")
            cc = next_cc
    except Exception as e:
        result.append(f"{'-> ' if cc.data_off == mark_off else ''}{cc.data_off}: (ERROR) {e}")
    return '\n'.join(result)


def match_insn_prefix(prefix: bitarray) -> List[bitarray]:
    return [bitarray(k) for k in INSTRUCTIONS.keys() if k.startswith(prefix.to01())]


def cell_signext(x: BitVecRef, numbits) -> BitVecRef:
    assert x.size() == CellData.size(), "Input must be CellData"
    shift = CellData.size() - numbits
    return x << shift >> shift


def recast_bitvec(source: Union[BitVecRef, int], target: BitVecSortRef) -> BitVecRef:
    if type(source) is int:
        return target.cast(source)
    if target.size() < source.size():
        return Extract(target.size() - 1, 0, source)
    elif target.size() > source.size():
        return ZeroExt(target.size() - source.size(), source)
    else:
        return source
