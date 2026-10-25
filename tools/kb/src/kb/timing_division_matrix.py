"""Explicit inputs for the timing compositor and natural helper closure."""

RAM_BASE=0x01000000
RAM_SIZE=65536
KINDS=('caller',)
ENTRY=0x4BDC2
PATTERNS=('stock','zero','one','254','255','256','maximum','rising','falling','checker','curve-zero','curve-one')
COMPOSITION=((0,0,0,0,0,128,0),(255,0,127,0,0,255,127),
             (0,255,128,255,255,0,128),(97,13,9,11,5,72,14))


def knots(image,address,count,width):
    return tuple(int.from_bytes(image[address+index*width:address+(index+1)*width],'big')
        for index in range(count))


def boundaries(values,maximum):
    return sorted({0,maximum,*(value+delta for value in values for delta in (-1,0,1)
        if 0<=value+delta<=maximum),*((first+second)//2 for first,second in zip(values,values[1:]))})


def cases(declared,image):
    outer,inner,curve=(knots(image,address,8,width) for address,width in
        ((0x1461A,2),(0x1464A,2),(0x11EEA,1)))
    coordinates={(x,inner[3],curve[3]) for x in boundaries(outer,65535)}
    coordinates.update((outer[3],y,curve[3]) for y in boundaries(inner,65535))
    coordinates.update((outer[3],inner[3],z) for z in boundaries(curve,255))
    coordinates.update((x,y,curve[3]) for x in outer for y in inner)
    coordinates.update((x,y,z) for x in (0,65535) for y in (0,65535) for z in (0,255))
    result=[]
    for pattern in PATTERNS:
        for outer_value,inner_value,curve_value in sorted(coordinates):
            index=len(result)
            result.append(dict(index=index,kind='caller',entry=ENTRY,pattern=pattern,
                outer=outer_value,inner=inner_value,curve=curve_value,mode=0,enabled=1,below=0,
                coefficient=(0,1,2000,65535)[index%4],composition=index%4,
                reverse_threshold=index%2,variant=index%4,sr=(index&1)|((index&15)<<4)|((index&3)<<8)))
    for mode,enabled,below in ((0,1,0),(0,1,1),(0,0,0),(32,1,0)):
        for composition in range(4):
            for coefficient in (0,1,2000,65535):
                index=len(result)
                result.append(dict(index=index,kind='caller',entry=ENTRY,pattern='255',
                    outer=outer[3],inner=inner[3],curve=curve[3],mode=mode,enabled=enabled,below=below,
                    coefficient=coefficient,composition=composition,reverse_threshold=index%2,
                    variant=index%4,sr=(index&1)|((index&15)<<4)|((index&3)<<8)))
    for pattern in ('one','255','curve-zero','curve-one'):
        index=len(result)
        result.append(dict(index=index,kind='caller',entry=ENTRY,pattern=pattern,
            outer=outer[3],inner=inner[3],curve=curve[3],mode=0,enabled=1,below=0,
            coefficient=65535,composition=0,reverse_threshold=0,variant=0,sr=0))
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+reg*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for reg in range(15)]
    return (*registers,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000|case['outer'])


def calibration_spans(declared):
    return ((0xC50E,128),(0x1461A,16),(0x1464A,16),(0x11F02,9),(0x11EEA,8),(0x9012,2))


def calibrations(declared,image,case):
    result={start:image[start:start+size] for start,size in calibration_spans(declared)}
    pattern=case['pattern']
    if pattern=='stock':return result
    if pattern in ('zero','one','254','255','256','maximum'):
        value={'zero':0,'one':1,'254':254,'255':255,'256':256,'maximum':65535}[pattern]
        surface=(value,)*64
        curve=(211 if pattern=='zero' else 255,)*8
    elif pattern in ('rising','falling'):
        surface=tuple(index*1024 for index in range(64))
        curve=tuple(17+index*23 for index in range(8))
        if pattern=='falling':
            surface=tuple(65535-value for value in surface)
            curve=tuple(255-value for value in curve)
    elif pattern=='checker':
        surface=tuple(65535 if (index//8+index%8)&1 else 0 for index in range(64))
        curve=tuple(255 if index&1 else 1 for index in range(8))
    elif pattern in ('curve-zero','curve-one'):
        surface=(255,)*64
        curve=(int(pattern=='curve-one'),)*8
    else:raise ValueError('the timing calibration input changes its declared pattern')
    result[0xC50E]=b''.join(value.to_bytes(2,'big') for value in surface)
    result[0x11F02]=bytes(curve)+image[0x11F0A:0x11F0B]
    return result


def memory(image,case):
    result=bytearray(RAM_SIZE)
    result[0x2458]=case['mode']
    result[0x41AB]=case['enabled']*64
    threshold=int.from_bytes(image[0x9012:0x9014],'big')
    if not 1<=threshold<65535:
        raise ValueError('the timing threshold matrix lacks its exact nonterminal stock threshold')
    first=threshold-1 if case['below'] else threshold
    second=min(first+1,65535)
    if case['reverse_threshold']:first,second=second,first
    result[0x28B8:0x28BA]=first.to_bytes(2,'big')
    result[0x28BA:0x28BC]=second.to_bytes(2,'big')
    result[0x106F]=case['curve']
    result[0x10CA:0x10CC]=case['outer'].to_bytes(2,'big')
    result[0x1024:0x1026]=case['inner'].to_bytes(2,'big')
    result[0x1900:0x1902]=case['coefficient'].to_bytes(2,'big')
    for address,value in zip((0x23BD,0x23C5,0x23F1,0x12DC,0x15EA,0x1A7D,0x23EE),
            COMPOSITION[case['composition']]):result[address]=value
    for address,value in ((0x1348,0x3D),(0x134A,0x67),(0x134C,0x95),(0x12D4,0xB3),
                          (0x1830,0xCA),(0x24D1,0xD3)):
        result[address]=value
    result[0x9818:0x981C]=bytes.fromhex('a5c3d2e1')
    return bytes(result)


def require_input(declared,image,case,observed):
    from kb import test_contract
    calibration=calibrations(declared,image,case)
    if (observed['entry']!=ENTRY or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(image,case),)
            or not test_contract.exact(observed['calibration_before'],calibration)
            or not test_contract.exact(observed['calibration_after'],calibration)):
        raise ValueError('the timing original changes its explicit context, RAM, axis, table or physical neighbor input')
