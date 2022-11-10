from instructions.utils import parse_instruction
from tvm_state import TvmState
from tvm_successors import Successors


def step(state: TvmState) -> Successors:
    successors = Successors()
    try:
        instruction = parse_instruction(state.cc)
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
        s = queue.pop()
        succ = step(s)
        queue += succ.succeed
        successors.finished += succ.finished
        successors.add_err(succ)
    return successors
