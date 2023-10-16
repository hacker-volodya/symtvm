class VmExitStatus(RuntimeError):
    code = None

    def __str__(self):
        return f"{type(self).__name__} ({self.code})" + (f": {super().__str__()}" if super().__str__() else "")


class NormalTermination(VmExitStatus):
    code = 0


class AlternativeTermination(VmExitStatus):
    code = 1


class StackUnderflow(VmExitStatus):
    code = 2


class StackOverflow(VmExitStatus):
    code = 3


class IntegerOverflow(VmExitStatus):
    code = 4


class OutOfRange(VmExitStatus):
    code = 5


class InvalidOpcode(VmExitStatus):
    code = 6


class TypeCheckError(VmExitStatus):
    code = 7

    def __init__(self, expected, got):
        super(TypeCheckError, self).__init__(f"Expected {expected}, got {got.decl()}")
        self.expected = expected
        self.got = got


class CellOverflow(VmExitStatus):
    code = 8


class CellUnderflow(VmExitStatus):
    code = 9


class DictError(VmExitStatus):
    code = 10


class UnknownError(VmExitStatus):
    code = 11


class FatalError(VmExitStatus):
    code = 12


class OutOfGas(VmExitStatus):
    code = -14
