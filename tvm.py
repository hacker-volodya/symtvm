import importlib.resources

import IPython
import tvm_valuetypes
from z3 import BitVec, Const

from symtvm.state.concreteslice import ConcreteSlice
from symtvm.state.sym_state import TvmState
from symtvm.state.symcell import SymCell
from symtvm.state.types import Int257, Cell
from symtvm_tools.stepper import run
import symtvm.transition.cp0


def test_tvm():
    code = importlib.resources.read_binary("tests.test_contracts", "simple-wallet.boc")
    cc = ConcreteSlice(tvm_valuetypes.deserialize_boc(code))
    c4 = SymCell.empty()
    c4.store_bits(BitVec('seqno', 32), 32)
    c4.store_bits(BitVec('pubkey', 256), 256)
    initial_state = TvmState.send_message(cc, c4, Const('body', Cell), Int257.cast(-1))
    succ, graph = run(initial_state)
    IPython.embed()


if __name__ == '__main__':
    test_tvm()
