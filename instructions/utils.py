from instructions.instruction import TvmInstruction
from instructions.registry import INSTRUCTIONS
from tvm_primitives import ConcreteSlice


def parse_instruction(cc: ConcreteSlice) -> TvmInstruction:
    nibbles = 1
    preload_prefix = lambda nibbles: cc.preload_bits(4 * nibbles).tobytes().hex()[:nibbles].upper()
    while len(match_insn_prefix(preload_prefix(nibbles))) > 1:
        nibbles += 1
    if len(match_insn_prefix(preload_prefix(nibbles))) == 0:
        raise RuntimeError(f"unknown instruction with prefix {preload_prefix(nibbles)}")
    return INSTRUCTIONS[match_insn_prefix(preload_prefix(nibbles))[0]]


def disasm(cc: ConcreteSlice) -> str:
    cc = cc.copy()
    result = []
    try:
        while len(cc.data.data) > cc.data_off:
            insn = parse_instruction(cc)
            args = insn.try_decode(cc)
            assert args is not None, f"decode failed for insn {insn.handler.__name__}"
            result.append(f"{cc.data_off}: {insn.handler.__name__} {args}")
    except Exception as e:
        result.append(f"{cc.data_off}: (ERROR) {e}")
    return '\n'.join(result)


def match_insn_prefix(prefix):
    return [k for k in INSTRUCTIONS.keys() if k.startswith(prefix)]