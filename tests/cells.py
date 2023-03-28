import unittest

from z3 import Solver, unsat, Not

from symtvm.state.exit_codes import CellUnderflow
from symtvm.state.symcell import SymCell


class TestSum(unittest.TestCase):
    def test_cell_ref_underflow(self):
        exceptions = []

        def exc_handler(exc, constrs, exceptions=exceptions):
            exceptions.append((exc, constrs))

        cell = SymCell.empty(exc_handler)
        solver = Solver()
        non_existent_ref = cell.load_ref()
        self.assertTrue(type(exceptions[0][0]) is CellUnderflow)
        solver.add(*[Not(x) for x in exceptions[0][1]])
        self.assertTrue(solver.check() == unsat)


if __name__ == '__main__':
    unittest.main()
