from bitarray.util import ba2int


def load_int(cc, args, bitsize):
    return ba2int(cc.load_bits(bitsize), signed=True)


def load_uint(cc, args, bitsize):
    return ba2int(cc.load_bits(bitsize), signed=False)