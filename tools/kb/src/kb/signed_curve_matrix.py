"""Typed inputs for the natural signed-curve entry."""

RAM_BASE=0x01000000
RAM_SIZE=65536
ENTRY=0x7B0A0
PATTERNS=('stock','zero','rising','constant')


def knots(image):
    return tuple(int.from_bytes(image[0x18E26+index*2:0x18E28+index*2],'big') for index in range(16))


def samples(values):
    points=[0,65535,values[0],values[1],values[4],values[8],values[-2],values[-1],values[0]+1,values[-2]+1]
    return tuple(sorted({value for value in points if 0<=value<=65535}))


def words(pattern):
    if pattern=='stock':return None
    if pattern=='zero':return (0,)*16
    if pattern=='rising':return tuple(index*200 for index in range(16))
    if pattern=='constant':return (2000,)*16
    raise ValueError('the signed-curve calibration input changes its declared pattern')


def cases(declared,image):
    result=[]
    row=knots(image)
    def add(second,first,coordinate,mode=0,gate=1,side=0,high=0x1F,low=0xFF,flag=0x3C):
        index=len(result)
        result.append(dict(index=index,entry=ENTRY,second=second,first=first,coordinate=coordinate,
            mode=mode,gate=gate,side=side,high=high|mode,low=low,flag=flag,variant=index%4,
            sr=(index&1)|((index&15)<<4)|((index&3)<<8)))
    for coordinate in samples(row):
        add('rising','zero',coordinate)
        add('constant','zero',coordinate)
        add('zero','zero',coordinate)
    for mode in (0,0x40):
        for gate in (0,1):
            for side in (0,2):
                add('constant','zero',row[4],mode,gate,side)
                add('zero','rising',row[4],mode,gate,side)
    add('stock','stock',row[3])
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+reg*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for reg in range(15)]
    return (*registers,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000|case['coordinate'])


def calibration_spans(declared):
    return ((0x18DE6,34),(0x18E06,34),(0x18E26,32),(0x83C1,1))


def calibrations(declared,image,case):
    second=words(case['second']);first=words(case['first'])
    second_bytes=image[0x18DE6:0x18DE6+32] if second is None else b''.join(value.to_bytes(2,'big') for value in second)
    first_bytes=image[0x18E06:0x18E06+32] if first is None else b''.join(value.to_bytes(2,'big') for value in first)
    axis=image[0x18E26:0x18E26+32]
    return {0x18DE6:second_bytes+first_bytes[:2],0x18E06:first_bytes+axis[:2],0x18E26:axis,
        0x83C1:bytes([(image[0x83C1]&~2)|(2 if case['gate'] else 0)])}


def memory(case):
    result=bytearray(RAM_SIZE)
    result[0x10BC:0x10BE]=case['coordinate'].to_bytes(2,'big')
    result[0x4214]=case['high']
    result[0x4213]=case['low']
    result[0x4255]=case['flag']
    result[0x249B]=case['side']
    result[0x9818:0x981C]=bytes.fromhex('a5c3d2e1')
    for address,value in ((0x338C,0x8300),(0x338E,0x8200),(0x3396,0x8100),(0x35EA,400),(0x35CE,1),(0x2A7A,40),(0x2712,77)):
        result[address:address+2]=value.to_bytes(2,'big')
    return bytes(result)


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=ENTRY or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('the signed-curve original changes an explicit coordinate, gate, curve or physical neighbor')
