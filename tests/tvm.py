import unittest

from tonpy.tvm.tvm import TVM
from tonpy.types import Cell, CellSlice, CellBuilder, Stack, StackEntry, Continuation, VmDict
from tonpy.fift.fift import convert_assembler
import IPython


class TestTVM(unittest.TestCase):
    def setUp(self) -> None:
        def run_simple_code(code: str, stack=None):
            if stack is None:
                stack = []
            data = CellBuilder().end_cell()
            t = TVM(code=convert_assembler(code), data=data)
            t.set_stack(Stack(stack))
            final_stack = t.run(True)
            print(t.vm_steps_detailed)
            return t, final_stack

        self.run_simple_code = run_simple_code

    def test_empty_tvm(self):
        t, final_stack = self.run_simple_code("<{ }>c")

    def test_error(self):
        t, final_stack = self.run_simple_code("<{ ADD }>c")

    def test_add(self):
        t, final_stack = self.run_simple_code("<{ ADD }>c", [10, 20])
        IPython.embed()

if __name__ == '__main__':
    unittest.main()
