from tvm_insns import match_insn_prefix, INSTRUCTIONS
from tvm_state import TvmState
from tvm_successors import Successors


def step(state: TvmState) -> Successors:
    successors = Successors()
    try:
        nibbles = 1
        preload_prefix = lambda nibbles: state.cc.preload_bits(4 * nibbles).tobytes().hex()[:nibbles].upper()
        while len(match_insn_prefix(preload_prefix(nibbles))) > 1:
            nibbles += 1
        if len(match_insn_prefix(preload_prefix(nibbles))) == 0:
            raise RuntimeError(f"unknown instruction with prefix {preload_prefix(nibbles)}")
        instruction = INSTRUCTIONS[match_insn_prefix(preload_prefix(nibbles))[0]]
    except Exception as e:
        successors.err(state.error(f"insn parsing err: {e}", []))
        return successors
    args = instruction.try_decode(state.cc)
    if args is None:
        successors.err(state.error(f"insn decoding err", []))
        return successors
    try:
        return instruction.handler(state, **args)
    except Exception as e:
        successors.err(state.error(f"insn execution error: {e}", []))
        return successors


def run(state: TvmState) -> Successors:
    queue = [state]
    successors = Successors()
    while len(queue) > 0:
        succ = step(queue.pop())
        queue += succ.succeed
        successors.finished += succ.finished
        successors.add_err(succ)
    return successors
