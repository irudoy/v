"""Typed inputs for the natural independent-leopard loop."""

RAM_BASE=0x01000000
RAM_SIZE=65536
ENTRY=0x5AC54
PATTERNS=('stock','zero','rising','falling','constant','high')


def bytes_for(pattern):
    if pattern=='stock':return None
    if pattern=='zero':return (0,0,0,0)
    if pattern=='rising':return (0,40,80,120)
    if pattern=='falling':return (200,100,50,0)
    if pattern=='constant':return (100,100,100,100)
    if pattern=='high':return (255,255,255,255)
    raise ValueError('the independent-leopard calibration input changes its declared pattern')


def cases(declared,image):
    result=[]
    def add(pattern='stock',words=((1000,0),(200,800)),points=(0x88,0x20)):
        row=dict(index=len(result),entry=ENTRY,pattern=pattern,
            left=(words[0][0],words[1][0]),right=(words[0][1],words[1][1]),points=points,
            variant=len(result)%4,sr=(len(result)&1)|((len(result)&15)<<4)|((len(result)&3)<<8))
        result.append(row)
    for pattern in ('rising','falling','constant','zero','high'):
        add(pattern,((2000,100),(1500,50)),(0x88,0xB8))
    add('stock',((1000,100),(0,800)),(0x88,0x10))
    add('rising',((40000,0),(1000,0)),(0x88,0x68))
    add('falling',((0,40000),(500,500)),(0xD0,0))
    add('constant',((65535,0),(1,0)),(0xE8,0x67))
    add('high',((30000,0),(0,1000)),(0xC8,0xA0))
    add('stock')
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+reg*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for reg in range(15)]
    return (*registers,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000|case['points'][0])


def calibration_spans(declared):
    return ((0x12522,4),(0x12526,4))


def calibrations(declared,image,case):
    values=bytes_for(case['pattern'])
    primary=image[0x12522:0x12526] if values is None else bytes(values)
    return {0x12522:primary,0x12526:image[0x12526:0x1252A]}


def memory(case):
    result=bytearray(RAM_SIZE)
    for index in (0,1):
        result[0x288C+2*index:0x288E+2*index]=case['left'][index].to_bytes(2,'big')
        result[0x4020+2*index:0x4022+2*index]=case['right'][index].to_bytes(2,'big')
        result[0x3529+index]=case['points'][index]
    result[0x9818:0x981C]=bytes.fromhex('a5c3d2e1')
    return bytes(result)


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=ENTRY or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('the independent-leopard original changes an explicit word, byte coordinate or curve')
