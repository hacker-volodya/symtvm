import tvm_valuetypes


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
