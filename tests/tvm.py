import unittest

from tvm import *
from tvm_valuetypes import Cell
import base64


class TestTVM(unittest.TestCase):
    def setUp(self) -> None:
        def run_simple_code(code_bytes: bytes):
            data = Cell()
            c = Cell()
            c.data.put_bytes(code_bytes)
            result = vm_exec(True, 0, [], base64.b64encode(c.serialize_boc()).decode(), base64.b64encode(data.serialize_boc()).decode(), TVMStackEntryTuple([]), 100000, 100000, 100000)
            print(repr(result))
            print("-------------------------------")
            print(result.logs)
            print("-------------------------------")
            return result

        self.run_simple_code = run_simple_code

    def test_empty_tvm(self):
        result = self.run_simple_code(b"")
        self.assertTrue(isinstance(result, TVMExecutionResultOk))
        self.assertTrue(result.exit_code == 0)

    def test_error(self):
        result = self.run_simple_code(bytes.fromhex("A0"))
        self.assertTrue(isinstance(result, TVMExecutionResultFail))
        self.assertTrue(result.exit_code == 2)

if __name__ == '__main__':
    unittest.main()
