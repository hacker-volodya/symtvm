import string

from bitarray.util import hex2ba, ba2int

from tvm_primitives import ConcreteSlice


class TvmInstruction:
    class ConstPattern:
        def __init__(self):
            self.val = ""

    class VarPattern:
        def __init__(self, var_name):
            self.var_name = var_name
            self.size = 0

    def __init__(self, handler, pattern):
        self.handler = handler
        self.pattern = pattern
        self.pattern_tokens = [TvmInstruction.ConstPattern()]
        for c in self.pattern:
            if c in string.digits + string.ascii_uppercase:
                if type(self.pattern_tokens[-1]) is TvmInstruction.VarPattern:
                    self.pattern_tokens.append(TvmInstruction.ConstPattern())
                self.pattern_tokens[-1].val += c
            elif c in string.ascii_lowercase:
                if type(self.pattern_tokens[-1]) is TvmInstruction.ConstPattern or self.pattern_tokens[-1].var_name != c:
                    self.pattern_tokens.append(TvmInstruction.VarPattern(c))
                self.pattern_tokens[-1].size += 1

    def try_decode(self, cc: ConcreteSlice):
        kwargs = {}
        preloaded_bits = 0
        try:
            for token in self.pattern_tokens:
                if type(token) is TvmInstruction.ConstPattern:
                    bits = cc.preload_bits(4 * len(token.val))
                    preloaded_bits += 4 * len(token.val)
                    if bits != hex2ba(token.val):
                        return None
                elif type(token) is TvmInstruction.VarPattern:
                    bits = cc.preload_bits(4 * token.size)
                    preloaded_bits += 4 * token.size
                    kwargs[token.var_name] = ba2int(bits, signed=True)
            cc.skip_bits(preloaded_bits)
            return kwargs
        except Exception as e:
            return None

    def __repr__(self):
        return f"{self.handler.__name__} <{self.pattern}>"
