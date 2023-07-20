import unittest
import importlib.resources

import tvm_valuetypes
from z3 import BitVec, Const

from symtvm.state.concreteslice import ConcreteSlice
from symtvm.state.exit_codes import OutOfRange, CellUnderflow
from symtvm.state.sym_state import TvmState
from symtvm.state.symcell import SymCell
from symtvm.state.types import Cell, Int257
from symtvm_tools.stepper import run

import symtvm.transition.cp0


class TestSymCell(unittest.TestCase):
    def test_simple_wallet(self):
        code = importlib.resources.read_binary("tests.test_contracts", "simple-wallet.boc")
        cc = ConcreteSlice(tvm_valuetypes.deserialize_boc(code))
        c4 = SymCell.empty()
        c4.store_bits(BitVec('seqno', 32), 32)
        c4.store_bits(BitVec('pubkey', 256), 256)
        initial_state = TvmState.send_message(cc, c4, Const('body', Cell), Int257.cast(-1))
        succ, graph = run(initial_state)
        print(succ)
        self.assertTrue(len(succ.errored) == 6)
        self.assertTrue(len(succ.finished) == 6)
        self.assertTrue(len(succ.errored_unsat) == 97)
        self.assertTrue(len(succ.unsat) == 0)
        self.assertTrue(len(succ.succeed) == 0)
        self.assertTrue(any([type(state.exception) == OutOfRange for state in succ.errored]))
        self.assertTrue(any([type(state.exception) == CellUnderflow for state in succ.errored]))

