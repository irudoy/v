"""Explicit bounded-entry inputs and calibration variants for the timing tail."""

from kb import timing_division_matrix as inputs

RAM_BASE=0x01000000
RAM_SIZE=65536
ENTRY=0x4B3F2
KINDS=('tail',)
PATTERNS=inputs.PATTERNS


def cases(declared,image):
    word=inputs.knots(image,0x1460A,8,2);byte=inputs.knots(image,0x11EEA,8,1)
    coordinates={(x,byte[3]) for x in inputs.boundaries(word,65535)}
    coordinates.update((word[3],y) for y in inputs.boundaries(byte,255))
    coordinates.update((x,y) for x in word for y in byte)
    coordinates.update((x,y) for x in (0,65535) for y in (0,255))
    result=[]
    def add(pattern,coordinate,curve,minimum=9350,enabled=1,reverse=0,variant=None):
        index=len(result)
        result.append(dict(index=index,kind='tail',entry=ENTRY,pattern=pattern,
            coordinate=coordinate,curve=curve,minimum=minimum,enabled=enabled,reverse_threshold=reverse,
            variant=index%4 if variant is None else variant,sr=(index&1)|((index&15)<<4)|((index&3)<<8)))
    for pattern in PATTERNS:
        for coordinate,curve in sorted(coordinates):add(pattern,coordinate,curve,reverse=len(result)%2)
    for enabled in (0,1):
        for minimum in (0,7349,7350,7351,9350,65535):
            for reverse in (0,1):add('255',word[3],byte[3],minimum,enabled,reverse)
    for pattern in ('one','255','curve-zero','curve-one'):add(pattern,word[3],byte[3],variant=0)
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+reg*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for reg in range(15)]
    registers[9],registers[10],registers[13]=RAM_BASE+0x1068,RAM_BASE+0x128C,RAM_BASE+0x41A9
    return (*registers,RAM_BASE+0x128C,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000|case['coordinate'])


def calibration_spans(declared):
    return ((0x11EFA,9),(0x147CA,18),(0x1460A,16),(0x11EEA,8),(0x9010,2))


def calibrations(declared,image,case):
    result={start:image[start:start+size] for start,size in calibration_spans(declared)}
    pattern=case['pattern']
    if pattern=='stock':return result
    if pattern in ('zero','one','254','255','256','maximum'):
        word={'zero':0,'one':1,'254':254,'255':255,'256':256,'maximum':65535}[pattern]
        words=(word,)*8;bytes_=(211 if pattern=='zero' else 255,)*8
    elif pattern in ('rising','falling'):
        words=tuple(index*8192 for index in range(8));bytes_=tuple(17+index*23 for index in range(8))
        if pattern=='falling':words=tuple(65535-value for value in words);bytes_=tuple(255-value for value in bytes_)
    elif pattern=='checker':
        words=tuple(65535 if index&1 else 0 for index in range(8));bytes_=tuple(255 if index&1 else 1 for index in range(8))
    elif pattern in ('curve-zero','curve-one'):
        words=(255,)*8;bytes_=(int(pattern=='curve-one'),)*8
    else:raise ValueError('the timing-tail calibration input changes its declared pattern')
    result[0x11EFA]=bytes(bytes_)+image[0x11F02:0x11F03]
    result[0x147CA]=b''.join(value.to_bytes(2,'big') for value in words)+image[0x147DA:0x147DC]
    return result


def memory(case):
    ram=bytearray(RAM_SIZE);ram[0x106F]=case['curve'];ram[0x41AB]=case['enabled']*64
    ram[0x10CA:0x10CC]=case['coordinate'].to_bytes(2,'big')
    first,second=case['minimum'],min(case['minimum']+1,65535)
    if case['reverse_threshold']:first,second=second,first
    ram[0x28B8:0x28BA]=first.to_bytes(2,'big');ram[0x28BA:0x28BC]=second.to_bytes(2,'big')
    ram[0x1900:0x1902]=bytes.fromhex('a3b4')
    for address,value in ((0x1347,0x3D),(0x1349,0x67),(0x134B,0x95),(0x12D5,0xB3)):
        ram[address]=value
    ram[0x9818:0x981C]=bytes.fromhex('a5c3d2e1')
    return bytes(ram)


def require_input(declared,image,case,observed):
    from kb import test_contract
    calibration=calibrations(declared,image,case)
    if (observed['entry']!=ENTRY or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibration)
            or not test_contract.exact(observed['calibration_after'],calibration)):
        raise ValueError('the timing-tail original changes an explicit base register, RAM, axis, table or physical neighbor')
