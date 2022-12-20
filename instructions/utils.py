from typing import List, Optional

from bitarray import bitarray

from instructions.bit_utils import ba2hex
from instructions.instruction import TvmInstruction
from instructions.registry import INSTRUCTIONS
from tvm_primitives import ConcreteSlice


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
            args = insn.try_decode(cc)
            result.append(f"{'-> ' if cc.data_off == mark_off else ''}{cc.data_off}: {insn.handler.__name__} {args}")
    except Exception as e:
        result.append(f"{'-> ' if cc.data_off == mark_off else ''}{cc.data_off}: (ERROR) {e}")
    return '\n'.join(result)


def match_insn_prefix(prefix: bitarray) -> List[bitarray]:
    return [bitarray(k) for k in INSTRUCTIONS.keys() if k.startswith(prefix.to01())]