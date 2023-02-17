import bitarray
from bitarray.util import hex2ba as orig_hex2ba


def hex2ba(hex_str: str) -> bitarray.bitarray:
    ba = orig_hex2ba(hex_str.rstrip("_"))
    if hex_str.endswith("_"):
        while ba.pop() != 1:
            pass
    return ba


def ba2hex(ba: bitarray.bitarray):
    ba_bytes = bytearray(ba.tobytes())
    if len(ba) % 4 != 0:
        ba_bytes[-1] = ba_bytes[-1] | (1 << (7 - len(ba) % 8))
    hex_str = ba_bytes.hex()
    if len(ba) % 8 < 4:
        hex_str = hex_str[:-1]
    if len(ba) % 4 != 0:
        hex_str += "_"
    return hex_str
