class array(list):
    def __init__(self, data=None):
        if data is None: data = []
        super().__init__(data)
        
    def tolist(self):
        return list(self)

ndarray = array

def matrix(data=None):
    return array(data)

# Type stubs for openpyxl and library compatibility
class number: pass
class integer(number): pass
class floating(number): pass
class complexfloating(number): pass

int8 = int16 = int32 = int64 = short = int_ = longlong = intc = intp = integer
uint8 = uint16 = uint32 = uint64 = ushort = ubyte = uint = ulonglong = uintc = uintp = integer
float16 = float32 = float64 = float_ = double = half = single = longdouble = floating
complex64 = complex128 = complex_ = csingle = cdouble = clongdouble = complexfloating
bool_ = bool
