import unittest

from z3 import *

from symtvm.state.exit_codes import CellUnderflow
from symtvm.state.symcell import SymCell
from symtvm.state.types import Int257


class TestSymCell(unittest.TestCase):
    def setUp(self) -> None:
        self.exceptions = []

        def exc_handler(exc, constrs):
            self.exceptions.append((exc, constrs))

        def assertSymTrue(*args):
            s = Solver()
            s.add(Not(And(*args)))
            r = s.check()
            if r != unsat:
                print("PROBLEM EXPRESSION", args)
                print("EXAMPLE", s.model())
            self.assertTrue(r == unsat)

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
        cell = SymCell.empty()
        self.assertSymTrue(cell.ref_size() == 0)

    def test_unbound_cell_ref_size(self):
        cell = SymCell.unbound('x')
        self.assertSymTrue(cell.ref_size() >= 0, cell.ref_size() <= 4)


if __name__ == '__main__':
    unittest.main()
