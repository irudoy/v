"""Typed inputs for the natural uptight-duck entry."""

RAM_BASE=0x01000000
RAM_SIZE=65536
ENTRY=0xB784E
POINTER=0x01003000
PATTERNS=('stock','zero','rising','last','constant')


def table(pattern):
    if pattern=='stock':return None
    if pattern=='zero':return (0,)*32
    if pattern=='rising':return tuple(index*20 for index in range(32))
    if pattern=='last':return (0,)*31+(4000,)
    if pattern=='constant':return (1000,)*32
    raise ValueError('the uptight-duck calibration input changes its declared pattern')


def axis(pattern):
    if pattern=='stock':return None
    if pattern=='strict':return tuple(index*100 for index in range(32))
    if pattern=='high':return tuple(10+index*100 for index in range(32))
    raise ValueError('the uptight-duck axis input changes its declared pattern')


def cases(declared,image):
    result=[]
    def add(pattern='stock', axis_pattern='stock', coordinate=0, dividend=0, threshold=0, side='stock'):
        result.append(dict(index=len(result), entry=ENTRY, pattern=pattern, axis=axis_pattern, side=side,
            coordinate=coordinate, dividend=dividend&0xFFFFFFFF, threshold=threshold,
            variant=len(result)%4, sr=(len(result)&1)|((len(result)&15)<<4)|((len(result)&3)<<8)))
    for pattern in ('last','rising','constant','zero'):
        add(pattern, 'strict', 150, 5*0xF4240)
    add('stock', 'stock', 0, 0)
    add('stock', 'stock', 1000, 0xFFFFFFFF)
    add('last', 'strict', 0, 0, 150)
    add('constant', 'high', 0, 0)
    add('rising', 'strict', 3100, 50*0xF4240, 0)
    add('last', 'strict', 50, 0xF4240)
    add('stock', 'stock', 0, 0, side='last')
    return tuple(result)


def context(declared, case):
    registers=[(0x1728394A+reg*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for reg in range(15)]
    registers[4]=case['dividend']
    registers[5]=case['coordinate']
    registers[6]=POINTER
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000|case['coordinate'])


def calibration_spans(declared):
    return ((0x15BF0,66),(0x15C40,64),(0x15C80,66),(0x13CA8,64),(0x8C8C,1))


def calibrations(declared, image, case):
    def pack(address, size, values):
        base=image[address:address+size]
        if values is None:return base
        head=b''.join(value.to_bytes(2,'big') for value in values)
        return head if size==len(head) else head+base[len(head):]
    return {0x15BF0:pack(0x15BF0,66,table(case['side'])), 0x15C40:pack(0x15C40,64,None),
        0x15C80:pack(0x15C80,66,table(case['pattern'])), 0x13CA8:pack(0x13CA8,64,axis(case['axis'])),
        0x8C8C:bytes([case['threshold']&255])}


def memory(case):
    result=bytearray(RAM_SIZE)
    result[0x9818:0x981C]=bytes.fromhex('a5c3d2e1')
    return bytes(result)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry']!=ENTRY or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the uptight-duck original changes an explicit dividend, coordinate, curve or axis')
