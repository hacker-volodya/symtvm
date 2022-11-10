from tvm_state import TvmState, TvmErrorState


class Successors:
    def __init__(self):
        self.succeed = []
        self.errored = []
        self.finished = []

    def ok(self, state: TvmState):
        self.succeed.append(state)

    def err(self, state: TvmErrorState):
        self.errored.append(state)

    def finish(self, state: TvmState):
        self.finished.append(state)

    def add_err(self, successors: 'Successors'):
        self.errored += successors.errored

    def single_ok(self):
        assert len(self.succeed) == 1
        return self.succeed

    def __repr__(self):
        return f"{len(self.succeed)} succeed, {len(self.errored)} errored"