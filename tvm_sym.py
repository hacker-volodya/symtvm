from instructions.utils import parse_instruction
from tvm_state import TvmState
from tvm_successors import Successors


def step(state: TvmState) -> Successors:
    successors = Successors()
    if state.cc.data_off == len(state.cc.data.data):
        successors.finish(state)
        return successors
    try:
        instruction = parse_instruction(state.cc)
    except Exception as e:
        successors.err(state.error(f"insn parsing err: {e}", []))
        return successors
    try:
        args = instruction.try_decode(state.cc)
    except Exception as e:
        successors.err(state.error(f"insn decoding err: {e}", []))
        return successors
    try:
        return instruction.handler(state, **args)
    except Exception as e:
        successors.err(state.error(f"insn execution error: {e}, {e!r}", []))
        return successors


def run(state: TvmState) -> Successors:
    queue = [state]
    successors = Successors()
    while len(queue) > 0:
        s = queue.pop()
        succ = step(s)
        queue += succ.succeed
        successors.finished += succ.finished
        successors.add_err(succ)
    return successors
