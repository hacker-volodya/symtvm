from typing import Dict, Callable, Any

from instructions.instruction import TvmInstruction
from tvm_primitives import ConcreteSlice

INSTRUCTIONS: Dict[str, TvmInstruction] = {}


def insn(pattern: str, custom_decoders: Dict[str, Callable[[ConcreteSlice, Dict[str, Any], int], Any]] = None):
    def func_wrapper(func, pattern=pattern, custom_decoders=custom_decoders):
        i = TvmInstruction(func, pattern, custom_decoders)
        INSTRUCTIONS[i.pattern_tokens[0].val] = i
        return func

    return func_wrapper
