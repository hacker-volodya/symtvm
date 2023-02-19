from z3 import *

Int257 = BitVecSort(257)
CellDataIndex = BitVecSort(10)
CellData = BitVecSort(1023)
CellRefIndex = BitVecSort(2)

Cell = Datatype('Cell')
RefList = Datatype('RefList')
RefList.declare('ref0')
RefList.declare('ref1', ('cell1', Cell))
RefList.declare('ref2', ('cell1', Cell), ('cell2', Cell))
RefList.declare('ref3', ('cell1', Cell), ('cell2', Cell), ('cell3', Cell))
RefList.declare('ref4', ('cell1', Cell), ('cell2', Cell), ('cell3', Cell), ('cell4', Cell))
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