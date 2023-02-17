from itertools import chain, cycle

from symtvm.decoder.utils import parse_instruction
from symtvm.state.sym_state import TvmState
from symtvm.state.sym_state import TvmErrorState
from symtvm.transition.context import InsnContext
from symtvm.transition.successors import Successors


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


def run(state: TvmState, stop_cond=lambda succ: len(succ.succeed) == 0):
    successors = Successors()
    successors.succeed = [state]
    graph = []
    while not stop_cond(successors):
        s = successors.succeed.pop(0)
        from_state = s.copy()
        succ = step(s)
        for next_state, symbol in chain(
                zip(succ.succeed, cycle('s')),
                zip(succ.finished, cycle('f')),
                zip(succ.errored, cycle('e')),
                zip(succ.errored_unsat, cycle(['eu'])),
                zip(succ.unsat, cycle('u'))
        ):
            graph.append((from_state, next_state.copy() if type(next_state) != TvmErrorState else next_state, symbol))
        successors.add_all(succ)
    return successors, graph
