from symcell import SymCell
from tvm_primitives import *
from tvm_state import TvmState
from tvm_sym import step, run
import instructions.impl
from instructions.utils import disasm
from cfg import build_graph
import IPython


def test_tvm():
    cc = ConcreteSlice(tvm_valuetypes.deserialize_boc(open("simple-wallet.boc", "rb").read()))
    c4 = SymCell.empty()
    c4.store_bits(BitVec('seqno', 32), 32)
    c4.store_bits(BitVec('pubkey', 256), 256)
    initial_state = TvmState.send_message(cc, c4, Const('body', Cell), Int257.cast(-1))
    succ, graph = run(initial_state)
    IPython.embed()


if __name__ == '__main__':
    test_tvm()
