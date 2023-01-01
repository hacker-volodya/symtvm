import tvm_valuetypes
from z3 import *


def declare_list(sort):
    datatype = Datatype('List_of_%s' % sort.name())
    datatype.declare('cons', ('car', sort), ('cdr', datatype))
    datatype.declare('nil')
    return datatype.create()


Int257 = BitVecSort(257)
CellDataIndex = BitVecSort(10)
CellData = BitVecSort(1023)
CellRefIndex = BitVecSort(2)

Cell = Datatype('Cell')
RefList = Datatype('RefList')
RefList.declare('ref0')
RefList.declare('ref1', ('cell1', Cell))
Cell.declare('cell', ('data', CellData), ('data_len', CellDataIndex), ('refs', RefList))
Cell, RefList = CreateDatatypes(Cell, RefList)

StackEntry = Datatype('StackEntry')
StackEntry.declare('int', ('int_val', Int257))
StackEntry.declare('cell', ('cell_val', Cell))
StackEntry.declare('tuple')
StackEntry.declare('null')
StackEntry.declare('slice', ('slice_val', Cell))
StackEntry.declare('builder', ('builder_val', Cell))
StackEntry.declare('continuation', ('continuation_val', Cell))
StackEntry = StackEntry.create()

# input - cell to hash
# output - repr hash of cell
CellHash = Function("HASHCU", Cell, Int257)

# input - (1) hash, (2) signature, (3) public key
# output - -1 if valid, 0 otherwise
CheckSignatureUInt = Function("CHKSIGNU", Int257, Cell, Int257, Int257)


class ConcreteSlice(tvm_valuetypes.Cell):
    def __repr__(self):
        return "<Slice refs_num: %d, data: %s, refs_off: %d, data_off: %d>" % (
            len(self.refs), repr(self.data), self.refs_off, self.data_off)

    def __init__(self, cell):
        super().__init__()
        self.data = cell.data.copy()
        self.refs = cell.refs.copy()
        self.data_off = 0
        self.refs_off = 0

    def skip_ref(self):
        if len(self.refs) == self.refs_off:
            raise RuntimeError("cell underflow")
        self.refs_off += 1

    def skip_bits(self, num):
        if len(self.data.data) < self.data_off + num:
            raise RuntimeError("cell underflow")
        self.data_off += num

    def preload_ref(self):
        if len(self.refs) == self.refs_off:
            raise RuntimeError("cell underflow")
        return self.refs[self.refs_off]

    def preload_bits(self, num):
        if len(self.data.data) < self.data_off + num:
            raise RuntimeError("cell underflow")
        return self.data.data[self.data_off:self.data_off + num]

    def load_ref(self):
        ref = self.preload_ref()
        self.skip_ref()
        return ref

    def load_bits(self, num):
        bits = self.preload_bits(num)
        self.skip_bits(num)
        return bits

    def copy(self):
        new_instance = ConcreteSlice(super(ConcreteSlice, self).copy())
        new_instance.data_off = self.data_off
        new_instance.refs_off = self.refs_off
        return new_instance


def is_int_fits(i: BitVecRef, numbits: BitVecRef) -> BoolRef:
    sign_extension = i >> numbits
    # check if sign extension is 111..111 or 000..000
    return (sign_extension + 1) & sign_extension == 0
