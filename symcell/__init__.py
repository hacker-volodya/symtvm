from z3 import DatatypeRef, LShR, UGT, ULT, BoolRef, If, BitVecRef, UGE, Not

from exceptions import CellUnderflow, OutOfRange, CellOverflow
from instructions.utils import recast_bitvec, cell_signext
from tvm_primitives import Cell, CellData, CellDataIndex, RefList, Int257, is_int_fits, CellHash


class SymCell:
    def __init__(self, cell: DatatypeRef, exception_cb=lambda exc, constrs: None):
        self.cell = cell
        self.exception_cb = exception_cb

    @classmethod
    def empty(cls, exception_cb=lambda exc, constrs: None):
        return cls(Cell.cell(CellData.cast(0), CellDataIndex.cast(0), RefList.ref0), exception_cb)

    def data_size(self):
        return Cell.data_len(self.cell)

    def ref_size(self):
        return If(RefList.is_ref0(Cell.refs(self.cell)), Int257.cast(0), Int257.cast(1))

    def data_overflow(self, numbits) -> BoolRef:
        return UGT(self.data_size(), CellData.size() - recast_bitvec(numbits, CellDataIndex))

    def data_underflow(self, numbits) -> BoolRef:
        return ULT(self.data_size(), recast_bitvec(numbits, CellDataIndex))

    def ref_overflow(self, numrefs) -> BoolRef:
        return UGT(self.ref_size(), 1 - numrefs)

    def ref_underflow(self, numrefs) -> BoolRef:
        return ULT(self.ref_size(), numrefs)

    def preload_bits(self, num, check_underflow=True):
        if check_underflow:
            self.exception_cb(CellUnderflow(), [self.data_underflow(num)])
        return LShR(Cell.data(self.cell), CellData.size() - recast_bitvec(num, CellData))

    def skip_bits(self, num, check_underflow=True):
        if check_underflow:
            self.exception_cb(CellUnderflow(), [self.data_underflow(num)])
        self.cell = Cell.cell(Cell.data(self.cell) << recast_bitvec(num, CellData), Cell.data_len(self.cell) - recast_bitvec(num, CellDataIndex), Cell.refs(self.cell))

    def load_bits(self, num, check_underflow=True):
        bits = self.preload_bits(num, check_underflow)
        self.skip_bits(num, check_underflow=False)
        return bits

    def preload_ref(self, check_underflow=True):
        if check_underflow:
            self.exception_cb(CellUnderflow(), [self.ref_underflow(1)])
        return SymCell(RefList.cell1(Cell.refs(self.cell)), self.exception_cb)

    def skip_ref(self, check_underflow=True):
        if check_underflow:
            self.exception_cb(CellUnderflow(), [self.ref_underflow(1)])
        self.cell = Cell.cell(Cell.data(self.cell), Cell.data_len(self.cell), RefList.ref0)

    def load_ref(self, check_underflow=True):
        ref = self.preload_ref(check_underflow)
        self.skip_ref(check_underflow=False)
        return ref

    def preload_int(self, numbits, check_underflow=True, signed=False):
        bits = self.preload_bits(numbits, check_underflow)
        if signed:
            bits = cell_signext(bits, numbits)
        return recast_bitvec(bits, Int257)

    def load_int(self, numbits, check_underflow=True, signed=False):
        ret = self.preload_int(numbits, check_underflow, signed)
        self.skip_bits(numbits, check_underflow=False)
        return ret

    def store_bits(self, bitvec: BitVecRef, numbits, check_overflow=True):
        if check_overflow:
            self.exception_cb(CellOverflow(), [self.data_overflow(numbits)])
        appendix_mask = (1 << recast_bitvec(numbits, CellData)) - 1
        sanitized_appendix = recast_bitvec(bitvec, CellData) & appendix_mask
        shift = CellData.size() - recast_bitvec(numbits, CellData) - recast_bitvec(self.data_size(), CellData)
        new_data = Cell.data(self.cell) | (sanitized_appendix << shift)
        self.cell = Cell.cell(new_data, Cell.data_len(self.cell) + recast_bitvec(numbits, CellDataIndex), Cell.refs(self.cell))

    def store_int(self, i: BitVecRef, numbits, check_overflow=True, check_range=True, signed=False):
        if check_range:
            self.exception_cb(OutOfRange(), [Not(is_int_fits(i, numbits)) if signed else UGE(i, 1 << numbits)])
        self.store_bits(i, numbits, check_overflow)

    def reprhash(self):
        return CellHash(self.cell)