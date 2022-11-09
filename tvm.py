from tvm_primitives import *
from tvm_state import TvmState
from tvm_sym import step, run
import IPython


def test_tvm():
    cc = ConcreteSlice(tvm_valuetypes.deserialize_boc(open("simple-wallet.boc", "rb").read()))
    initial_state = TvmState.send_message(cc, Const('data', Cell), Const('body', Cell), Int257.cast(-1))
    succ = run(initial_state)
    IPython.embed()


if __name__ == '__main__':
    test_tvm()
