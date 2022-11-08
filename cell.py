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
Cell.declare('cell', ('data', CellData), ('len', CellDataIndex))
Cell = Cell.create()

Slice = Datatype('Slice')
Slice.declare('slice', ('cell', Cell), ('data_pos', CellDataIndex))
Slice = Slice.create()

Continuation = Datatype('Continuation')
Continuation.declare('Continuation', ('cell', Cell), ('data_pos', CellDataIndex))
Continuation = Continuation.create()

StackEntry = Datatype('StackEntry')
StackEntry.declare('int', ('int_val', Int257))
StackEntry.declare('cell', ('cell_val', Cell))
StackEntry.declare('tuple')
StackEntry.declare('null')
StackEntry.declare('slice', ('slice_val', Slice))
StackEntry.declare('builder', ('builder_val', Cell))
StackEntry.declare('continuation', ('continuation_val', Cell))
StackEntry = StackEntry.create()
