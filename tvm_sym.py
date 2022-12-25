from instructions.insn_context import InsnContext
from instructions.utils import parse_instruction
from tvm_state import TvmState
from tvm_successors import Successors


def step(state: TvmState) -> Successors:
    successors = Successors()
    if state.cc.data_off == len(state.cc.data.data):
        successors.finish(state)
        return successors
    try:
        try:
            instruction = parse_instruction(state.cc)
        except Exception as e:
            raise Exception(f"Insn parsing error: {e}") from e
        try:
            args = instruction.try_decode(state.cc)
        except Exception as e:
            raise Exception(f"Insn decoding error: {e}") from e
        try:
            context = InsnContext(state)
            instruction.handler(context, **args)
            return context.finalize()
        except Exception as e:
            raise Exception(f"Insn execution error: {e}") from e
    except Exception as e:
        successors.err(state.error(state.copy(), e, []))
        return successors


def run(state: TvmState, stop_cond=lambda succ: len(succ.succeed) == 0) -> Successors:
    successors = Successors()
    successors.succeed = [state]
    while not stop_cond(successors):
        s = successors.succeed.pop(0)
        succ = step(s)
        successors.add_all(succ)
    return successors
