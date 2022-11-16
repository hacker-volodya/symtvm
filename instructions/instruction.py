import string

from bitarray.util import ba2int

from instructions.bit_utils import hex2ba
from tvm_primitives import ConcreteSlice


class TvmInstruction:
    class ConstPattern:
        def __init__(self):
            self.val = ""

    class VarPattern:
        def __init__(self, var_name):
            self.var_name = var_name
            self.size = 0

    def __init__(self, handler, pattern, custom_decoders=None):
        if custom_decoders is None:
            custom_decoders = {}
        self.custom_decoders = custom_decoders
        self.handler = handler
        self.pattern = pattern
        self.pattern_tokens = [TvmInstruction.ConstPattern()]
        for c in self.pattern:
            if c in string.digits + string.ascii_uppercase + "_":
                if type(self.pattern_tokens[-1]) is TvmInstruction.VarPattern:
                    self.pattern_tokens.append(TvmInstruction.ConstPattern())
                self.pattern_tokens[-1].val += c
            elif c in string.ascii_lowercase:
                if type(self.pattern_tokens[-1]) is TvmInstruction.ConstPattern or \
                        self.pattern_tokens[-1].var_name != c:
                    self.pattern_tokens.append(TvmInstruction.VarPattern(c))
                self.pattern_tokens[-1].size += 1

    def try_decode(self, cc: ConcreteSlice):
        kwargs = {}
        rem = 0
        for token in self.pattern_tokens:
            if type(token) is TvmInstruction.ConstPattern:
                const = hex2ba(token.val)
                bits = cc.load_bits(len(const))
                if bits != const:
                    return None
                rem = (4 - len(const) % 4) % 4
            elif type(token) is TvmInstruction.VarPattern:
                if self.custom_decoders.get(token.var_name) is not None:
                    kwargs[token.var_name] = self.custom_decoders[token.var_name](cc, kwargs, rem + 4 * token.size)
                else:
                    bits = cc.load_bits(rem + 4 * token.size)
                    kwargs[token.var_name] = ba2int(bits, signed=True)
                rem = 0
        return kwargs

    def __repr__(self):
        return f"{self.handler.__name__} <{self.pattern}>"
