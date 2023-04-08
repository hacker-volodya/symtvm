import unittest

from z3 import *

from symtvm.state.exit_codes import CellUnderflow
from symtvm.state.symcell import SymCell


class TestSymCell(unittest.TestCase):
    def setUp(self) -> None:
        self.exceptions = []

        def exc_handler(exc, constrs):
            self.exceptions.append((exc, constrs))

        def assertSymTrue(*args):
            self.assertTrue(is_true(simplify(And(*args))))

        self.exc_handler = exc_handler
        self.assertSymTrue = assertSymTrue

    def test_cell_ref_underflow(self):
        cell = SymCell.empty(self.exc_handler)
        non_existent_ref = cell.load_ref()

        # assert CellUnderflow is possible
        self.assertTrue(type(self.exceptions[0][0]) is CellUnderflow)

        # assert CellUnderflow always happens
        self.assertSymTrue(*self.exceptions[0][1])

    def test_empty_cell_ref_size_is_zero(self):
        cell = SymCell.empty(self.exc_handler)
        self.assertSymTrue(cell.ref_size() == 0)


if __name__ == '__main__':
    unittest.main()
