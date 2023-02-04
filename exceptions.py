class VmError(RuntimeError):
    code = None

    def __str__(self):
        return f"{type(self).__name__} ({self.code})" + (f": {super().__str__()}" if super().__str__() else "")


class StackUnderflow(VmError):
    code = 2


class StackOverflow(VmError):
    code = 3


class IntegerOverflow(VmError):
    code = 4


class OutOfRange(VmError):
    code = 5


class InvalidOpcode(VmError):
    code = 6


class TypeCheckError(VmError):
    code = 7

    def __init__(self, expected, got):
        super(TypeCheckError, self).__init__(f"Expected {expected}, got {got.decl()}")
        self.expected = expected
        self.got = got


class CellOverflow(VmError):
    code = 8


class CellUnderflow(VmError):
    code = 9


class DictError(VmError):
    code = 10


class OutOfGas(VmError):
    code = -14
