from typing import Dict, Callable, Any

from symtvm.decoder.bit_utils import hex2ba
from symtvm.decoder.instruction import TvmInstruction
from symtvm.state.concreteslice import ConcreteSlice

INSTRUCTIONS: Dict[str, TvmInstruction] = {}


def insn(pattern: str, custom_decoders: Dict[str, Callable[[ConcreteSlice, Dict[str, Any], int], Any]] = None):
    def func_wrapper(func, pattern=pattern, custom_decoders=custom_decoders):
        i = TvmInstruction(func, pattern, custom_decoders)
        INSTRUCTIONS[hex2ba(i.pattern_tokens[0].val).to01()] = i
        return func

    return func_wrapper
