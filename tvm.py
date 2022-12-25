from tvm_primitives import *
from tvm_state import TvmState
from tvm_sym import step, run
import instructions.impl
from instructions.utils import disasm
import IPython


def test_tvm():
    cc = ConcreteSlice(tvm_valuetypes.deserialize_boc(open("simple-wallet.boc", "rb").read()))
    data = CellData.cast(Concat(BitVec('seqno', 32), BitVec('pubkey', 256), BitVec('empty', 1023 - 32 - 256)))
    c4 = Cell.cell(data, CellDataIndex.cast(32 + 256), Cell.refs(symcell_empty()))
    initial_state = TvmState.send_message(cc, c4, Const('body', Cell), Int257.cast(-1))
    succ = run(initial_state, lambda succ: any(s.cc.data_off == 224 for s in succ.succeed))
    IPython.embed()


if __name__ == '__main__':
    test_tvm()
