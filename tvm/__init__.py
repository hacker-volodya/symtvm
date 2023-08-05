import base64
import ctypes, os, json
from typing import List

# raw c caller

lib = ctypes.CDLL(os.path.dirname(__file__) + '/ton-blockchain/build/crypto/libvm-exec-lib.so')
lib.vm_exec.argtypes = (ctypes.c_int, ctypes.c_char_p)
lib.vm_exec.restype = ctypes.c_char_p

def _vm_exec(inp):
    global lib
    return lib.vm_exec(ctypes.c_int(len(inp)), inp.encode()).decode()

# json types

# export type TVMStackEntry =
#     | TVMStackEntryNull
#     | TVMStackEntryCell
#     | TVMStackEntryInt
#     | TVMStackEntryCellSlice
#     | TVMStackEntryTuple

class TVMStackEntry:
    def to_json(self):
        return self.__dict__

    @staticmethod
    def from_json(data: dict):
        return {
            "null": lambda d: TVMStackEntryNull(),
            "cell": lambda d: TVMStackEntryCell(d["value"]),
            "int": lambda d: TVMStackEntryInt(d["value"]),
            "cell_slice": lambda d: TVMStackEntryCellSlice(d["value"]),
            "tuple": lambda d: TVMStackEntryTuple([TVMStackEntry.from_json(x) for x in d["value"]]),
        }[data["type"]](data)

# export type TVMStackEntryNull = { type: 'null' }
class TVMStackEntryNull(TVMStackEntry):
    def __init__(self):
        self.type = "null"

# export type TVMStackEntryCell = { type: 'cell', value: string }
class TVMStackEntryCell(TVMStackEntry):
    def __init__(self, value: str):
        self.type = "cell"
        self.value = value

# export type TVMStackEntryInt = { type: 'int', value: string }
class TVMStackEntryInt(TVMStackEntry):
    def __init__(self, value: str):
        self.type = "int"
        self.value = value

# export type TVMStackEntryCellSlice = { type: 'cell_slice', value: string }
class TVMStackEntryCellSlice(TVMStackEntry):
    def __init__(self, value: str):
        self.type = "cell_slice"
        self.value = value

# export type TVMStackEntryTuple = { type: 'tuple', value: TVMStackEntry[] }
class TVMStackEntryTuple(TVMStackEntry):
    def __init__(self, value: List[TVMStackEntry]):
        self.type = "tuple"
        self.value = value

    def to_json(self):
        return {"type": "tuple", "value": [x.to_json() for x in self.value]}

# export type TVMExecutionResult =
#     | TVMExecutionResultOk
#     | TVMExecutionResultFail
class TVMExecutionResult:
    @staticmethod
    def from_json(data: dict):
        ok = data["ok"]
        del data["ok"]
        if ok:
            return TVMExecutionResultOk.from_json(data)
        else:
            return TVMExecutionResultFail.from_json(data)

    def __repr__(self):
        return f"{type(self)}: " + repr({k:(v.to_json() if getattr(v, "to_json", None) is not None else v) for k, v in self.__dict__.items()})

# export type TVMExecutionResultOk = {
#     ok: true,
#     exit_code: number,           // TVM Exit code
#     gas_consumed: number,
#     stack: TVMStack,            // TVM Resulting stack
#     data_cell: string           // base64 encoded BOC
#     action_list_cell: string    // base64 encoded BOC
#     logs: string
#     debugLogs: string[]
#     c7: TVMStackEntryTuple
# }
class TVMExecutionResultOk(TVMExecutionResult):
    def __init__(self, exit_code: int, gas_consumed: int, stack: List[TVMStackEntry], data_cell: str, action_list_cell: str, logs: str, debugLogs: List[str] = None):
        self.exit_code = exit_code
        self.gas_consumed = gas_consumed
        self.stack = stack
        self.data_cell = data_cell
        self.action_list_cell = action_list_cell
        self.logs = logs
        self.ok = True
        if debugLogs is None:
            debugLogs = []
        self.debugLogs = debugLogs

    @staticmethod
    def from_json(data: dict):
        data["stack"] = [TVMStackEntry.from_json(x) for x in data["stack"]]
        data["logs"] = base64.b64decode(data["logs"]).decode()
        return TVMExecutionResultOk(**data)

# export type TVMExecutionResultFail = {
#     ok: false,
#     error?: string
#     exit_code?: number,
#     logs?: string
#     debugLogs: string[]
#     c7: TVMStackEntryTuple
# }

class TVMExecutionResultFail(TVMExecutionResult):
    def __init__(self, error: str = None, exit_code: int = None, logs: str = None, debugLogs: List[str] = None, c7: TVMStackEntryTuple = None):
        self.error = error
        self.exit_code = exit_code
        self.logs = logs

        if debugLogs is None:
            debugLogs = []
        
        self.debugLogs = debugLogs
        self.c7 = c7
        self.ok = False
    
    @staticmethod
    def from_json(data: dict):
        if data.get("c7") is not None:
            data["c7"] = TVMStackEntry.from_json(data["c7"])
        if data.get("logs") is not None:
            data["logs"] = base64.b64decode(data["logs"]).decode()
        return TVMExecutionResultFail(**data)

# wrapper

# export type TVMExecuteConfig = {
#     debug: boolean
#     function_selector: number,
#     init_stack: TVMStack,
#     code: string,               // base64 encoded TVM fift assembly
#     data: string,               // base64 encoded boc(data_cell)
#     c7_register: TVMStackEntryTuple
#     gas_limit: number
#     gas_max: number
#     gas_credit: number
# }
def vm_exec(debug: bool, function_selector: int, init_stack: List[TVMStackEntry], code: str, data: str, c7_register: TVMStackEntryTuple, gas_limit: int, gas_max: int, gas_credit: int):
    config = json.dumps({"debug": debug, "function_selector": function_selector, "init_stack": [x.to_json() for x in init_stack], "code": code, "data": data, "c7_register": c7_register.to_json(), "gas_limit": gas_limit, "gas_max": gas_max, "gas_credit": gas_credit})
    result = json.loads(_vm_exec(config))
    return TVMExecutionResult.from_json(result)