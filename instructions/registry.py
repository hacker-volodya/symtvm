from typing import Dict

from instructions.instruction import TvmInstruction

INSTRUCTIONS: Dict[str, TvmInstruction] = {}


def insn(pattern):
    def func_wrapper(func, pattern=pattern):
        i = TvmInstruction(func, pattern)
        INSTRUCTIONS[i.pattern_tokens[0].val] = i
        return func

    return func_wrapper
