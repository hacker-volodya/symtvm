from z3 import unsat

from tvm_state import TvmState, TvmErrorState


class Successors:
    def __init__(self):
        self.succeed = []
        self.errored = []
        self.errored_unsat = []
        self.finished = []
        self.unsat = []

    def ok(self, state: TvmState):
        self.succeed.append(state)

    def err(self, state: TvmErrorState):
        if state.solver.check() == unsat:
            self.errored_unsat.append(state)
        else:
            self.errored.append(state)

    def finish(self, state: TvmState):
        self.finished.append(state)

    def add_unsat(self, state: TvmState):
        self.unsat.append(state)

    def add_all(self, successors: 'Successors'):
        self.succeed += successors.succeed
        self.errored += successors.errored
        self.finished += successors.finished
        self.errored_unsat += successors.errored_unsat
        self.unsat += successors.unsat

    def single_ok(self):
        assert len(self.succeed) == 1
        return self.succeed

    def __repr__(self):
        r = []
        for k, v in self.__dict__.items():
            r.append(f"{len(v)} {k}")
        return ", ".join(r)
