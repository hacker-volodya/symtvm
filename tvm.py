from tvm_primitives import *
from tvm_state import TvmState
from tvm_sym import step, run
import instructions.impl
from instructions.utils import disasm
import IPython


def test_tvm():
    cc = ConcreteSlice(tvm_valuetypes.deserialize_boc(open("simple-wallet.boc", "rb").read()))
    data = CellData.cast(Concat(BitVec('seqno', 32), BitVec('pubkey', 256), BitVec('empty', 1023 - 32 - 256)))
    c4 = Cell.cell(data, CellDataIndex.cast(32 + 256))
    initial_state = TvmState.send_message(cc, c4, Const('body', Cell), Int257.cast(-1))
    succ = run(initial_state)
    IPython.embed()


if __name__ == '__main__':
    test_tvm()
