"""Typed inputs for the natural fine-gopher entry."""

RAM_BASE=0x01000000
RAM_SIZE=65536
ENTRY=0x6062C
PATTERNS=('stock','zero','rising','constant','high')
GBR_BASE=0xFFFF8C00
GBR_SIZE=256
BLOCK_BASE=0xFFFF9900
BLOCK_SIZE=512


def words(pattern):
    if pattern=='stock':return None
    if pattern=='zero':return (0,)*8
    if pattern=='rising':return tuple(index*200 for index in range(8))
    if pattern=='constant':return (1000,)*8
    if pattern=='high':return (4000,)*8
    raise ValueError('the fine-gopher calibration input changes its declared pattern')


def pack(image,address,size,pattern):
    base=image[address:address+size]
    values=words(pattern)
    if values is None:return base
    head=b''.join(value.to_bytes(2,'big') for value in values)
    return head if size==16 else head+base[16:]


def cases(declared,image):
    result=[]
    def add(**fields):
        row=dict(curve_c='stock',curve_d='stock',curve_a='stock',curve_b='stock',curve_e='stock',
            coordinate=56,byte_coordinate=52,gate=0,left=0,right=0,word_a=0x100,word_b=0x100,
            divisor=0x4E20,rom_ec=0x1B5,rom_66=0,block0=0,block8=0,blockc=0,block10=0,block14=0,
            block18=0,block1a=0,block1c=0,block20=0,block24=0,port=0)
        row.update(fields)
        row.update(index=len(result),entry=ENTRY,variant=len(result)%4,
            sr=(len(result)&1)|((len(result)&15)<<4)|((len(result)&3)<<8))
        result.append(row)
    for pattern in ('rising','constant','zero'):
        add(curve_a=pattern,word_a=65535,word_b=129)
    for pattern in ('rising','constant'):
        add(curve_b=pattern,word_a=65535,word_b=129)
    for pattern in ('rising','constant','zero'):
        add(curve_e=pattern)
    add(word_a=65535,word_b=129)
    add(gate=1,block24=1)
    add(block24=1)
    add(block20=1,block1c=0,rom_66=100)
    add(block20=1,block0=5)
    add(block20=1)
    add(block0=1,block10=0xFFFFFFFF,block1a=1,block8=0xFFFFFFFF,block18=1)
    add(block0=1,block10=10,block1a=1,block8=10,block18=1)
    add(block14=7)
    add(divisor=0,curve_e='constant')
    add(divisor=1,curve_e='constant',byte_coordinate=70)
    add(curve_e='zero')
    add(blockc=3,byte_coordinate=70)
    add(rom_ec=0,byte_coordinate=70)
    add(rom_ec=1,byte_coordinate=70)
    add(rom_ec=0x1B5,byte_coordinate=70)
    add(left=0x7F,right=0x80)
    add(left=0x80,right=0x7F)
    add(left=0,right=10)
    add(left=10,right=0)
    add(word_a=65535,word_b=65535,curve_c='high',curve_a='high',curve_d='high',curve_b='high')
    add(word_a=1,word_b=1,curve_c='zero',curve_d='zero',curve_a='zero',curve_b='zero')
    add(gate=1,block0=1,block20=1,port=0xFF,left=20,right=4,word_a=65535,word_b=129,
        curve_a='constant',curve_b='rising',curve_e='rising')
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+reg*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for reg in range(15)]
    return (*registers,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000|case['coordinate'])


def calibration_spans(declared):
    return ((0x1453A,16),(0x1454A,18),(0x14F42,16),(0x14F52,18),(0x15002,16),(0x15012,18),
            (0x13C38,16),(0x13C58,16),(0x13BD8,16),(0x13BE8,16),(0x93E8,2),(0x93EC,2),(0x9066,2))


def calibrations(declared,image,case):
    rows=((0x1453A,16,'curve_c'),(0x1454A,18,'curve_d'),(0x14F42,16,'curve_a'),(0x14F52,18,'curve_b'),
          (0x15002,16,'curve_e'),(0x15012,18,None),(0x13C38,16,None),(0x13C58,16,None),
          (0x13BD8,16,None),(0x13BE8,16,None))
    result={address:pack(image,address,size,'stock' if key is None else case[key]) for address,size,key in rows}
    result[0x93E8]=case['divisor'].to_bytes(2,'big')
    result[0x93EC]=case['rom_ec'].to_bytes(2,'big')
    result[0x9066]=case['rom_66'].to_bytes(2,'big')
    return result


def memory(case):
    result=bytearray(RAM_SIZE)
    result[0x4185]=0x40 if case['gate'] else 0
    result[0x11D4]=case['left']
    result[0x2365]=case['right']
    result[0x11F4:0x11F6]=case['coordinate'].to_bytes(2,'big')
    result[0x1076]=case['byte_coordinate']
    result[0x1026:0x1028]=case['word_a'].to_bytes(2,'big')
    result[0x22E6:0x22E8]=case['word_b'].to_bytes(2,'big')
    result[0x423E]=case['port']
    result[0x9818:0x981C]=bytes.fromhex('a5c3d2e1')
    base=0x99FC
    for offset,key,width in ((0,'block0',4),(8,'block8',4),(0xC,'blockc',4),(0x10,'block10',4),(0x14,'block14',4),
                             (0x18,'block18',2),(0x1A,'block1a',2),(0x1C,'block1c',2),(0x20,'block20',4),(0x24,'block24',4)):
        result[base+offset:base+offset+width]=(case[key]&((1<<(8*width))-1)).to_bytes(width,'big')
    return bytes(result)


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=ENTRY or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('the fine-gopher original changes an explicit coordinate, gate, curve or divisor word')
