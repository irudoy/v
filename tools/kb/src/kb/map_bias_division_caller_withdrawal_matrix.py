"""Input-only raw caller registers, stored words, byte controls, axes and map words."""
from kb import test_contract
from kb import map_bias_division_caller_withdrawal_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('word_142a',0x142A,2),('word_1702',0x1702,2),('word_1878',0x1878,2),
    ('byte_1880',0x1880,1),('word_188c',0x188C,2),('byte_18b4',0x18B4,1),
    ('word_19c4',0x19C4,2),('word_243a',0x243A,2),('dword_9818',0x9818,4))
MAP_FIELDS=tuple(f'map_word_{i:03d}' for i in range(256))
BYTE_AXIS_FIELDS=tuple(f'axis_byte_{i:02d}' for i in range(16))
WORD_AXIS_FIELDS=tuple(f'axis_word_{i:02d}' for i in range(16))
WIDTHS={name:32 for name in REGISTERS}
WIDTHS.update({name:size*8 for name,at,size in RAM_FIELDS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,
    (0x12345678,0x87654321,0xA53C5AC3,0xFFFFFFFF,0x80000000,0x10000,0x7FFFFFFF,0x3CA55AC3))})
DEFAULTS.update(word_142a=0xA55A,word_1702=128,word_1878=1000,word_188c=400,
    byte_1880=0,byte_18b4=0,word_19c4=0x55AA,word_243a=5000,dword_9818=0x3CA55AC3,
    selected_scalar_word_942c=0x1357,variant=7)
DEFAULTS.update({name:0x800A for name in MAP_FIELDS})
DEFAULTS.update({name:i*16 for i,name in enumerate(BYTE_AXIS_FIELDS)})
DEFAULTS.update({name:i*4096 for i,name in enumerate(WORD_AXIS_FIELDS)})
WORD_VALUES=(0,1,2,3,4,5,9,10,127,128,255,256,32767,32768,65534,65535)
BYTE_VALUES=(0,1,2,7,15,16,127,128,129,254,255)
ENTRY_FIELDS={0x702C6:('word_1878','word_188c','byte_1880','byte_18b4','word_1702','word_243a',
    'map_words','axis_bytes')}


def cases(declared,image):
    rows=[]
    def add(kind,**changes):rows.append(dict(DEFAULTS,entry=0x702C6,kind=kind,**changes))
    stock={row['field']:int.from_bytes(image[row['address']:row['address']+row['size']],'big')
        for row in contract.CONFIGURATION}
    add('owned-stock-calibration',**stock)
    for field in REGISTERS:
        for raw in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
            add('complete-raw-register-width',**{field:raw})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-context',variant=variant)
    for field,at,size in RAM_FIELDS:
        values=BYTE_VALUES if size==1 else WORD_VALUES if size==2 else (0,1,0xFFFF,0x10000,0x80000000,0xFFFFFFFF)
        for raw in values:add('complete-independent-RAM-operand-or-prior',**{field:raw})
    for first,second in ((0,0),(1,1),(127,127),(128,128),(255,255),(0,1),(1,0),(127,128),(128,255)):
        add('complete-signed-byte-equality-controls',byte_1880=first,byte_18b4=second)
    for first in (0,1,32767,32768,65534,65535):
        for second in (0,1,32767,32768,65534,65535):
            add('real-signed-difference-and-absolute-helper',word_1878=first,word_188c=second)
            add('real-unsigned-word-sum-and-first-saturation',byte_18b4=1,word_1878=first,word_188c=second)
    for index in range(16):
        knot=index*256
        for delta in (-1,0,1,127,128,255):
            coordinate=max(0,min(65535,knot+delta))
            add('each-first-axis-knot-neighbor-and-interior',word_1702=coordinate)
        for raw in (0,1,127,128,254,255):
            add('independent-byte-axis-without-ordering-premise',word_1702=knot+1,
                **{BYTE_AXIS_FIELDS[index]:raw})
        for raw in (0,1,32767,32768,65534,65535):
            add('independent-word-axis-and-exact-FFFF-fifth',**{WORD_AXIS_FIELDS[index]:raw})
        for raw in WORD_VALUES:
            add('each-actually-reachable-map-word',word_1702=knot,**{MAP_FIELDS[index*16+15]:raw})
    patterns=(tuple(i*16 for i in range(16)),tuple(255-i*16 for i in range(16)),
        tuple([64]*16),tuple((i//2)*32 for i in range(16)),tuple((i*79)&255 for i in range(16)))
    for axis in patterns:
        for coordinate in (0,1,15,16,17,1023,1024,1025,2047,2048,2049,3839,3840,3841,65534,65535):
            add('complete-flat-duplicate-descending-nonmonotonic-byte-axis',word_1702=coordinate,
                **dict(zip(BYTE_AXIS_FIELDS,axis)))
    for index in range(15):
        for first,second in ((0,65535),(65535,0),(32767,32768),(32768,32767)):
            add('both-interpolation-directions-and-full-word-carriers',word_1702=index*256+128,
                **{MAP_FIELDS[index*16+15]:first,MAP_FIELDS[(index+1)*16+15]:second})
    for raw in (0,0x7FFF,0x8000,0x8009,0x800A,0x800B,0xFFFF):
        for source in (0,1,2,127,128,255,256,32767,32768,65535):
            add('map-bias-minimum-positive-divisor-quotient-and-final-cap',word_243a=source,
                **{field:raw for field in MAP_FIELDS})
    for raw in (0,1,0x7FFF,0x8000,0xFFFE,0xFFFF):
        for second in (0,1):
            add('selected-two-byte-scalar-prior-only',selected_scalar_word_942c=raw,byte_18b4=second)
    nonflat={field:0x800A+(index//16)*1024 for index,field in enumerate(MAP_FIELDS)}
    for coordinate in (0,1,127,128,255,256,257,3839,3840,65535):
        add('actual-coordinate-alternatives-fixed-other',word_1702=coordinate,**nonflat)
    for axis in patterns:
        add('actual-byte-axis-alternatives-fixed-other',word_1702=128,
            **dict(nonflat,**dict(zip(BYTE_AXIS_FIELDS,axis))))
    return tuple(dict(row,index=index) for index,row in enumerate(rows))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry']!=0x702C6
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a map-bias caller input changes a raw register,byte,word,dword,axis,calibration or full SR width')


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+index*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for index in range(15)]
    registers[:8]=[case[name] for name in REGISTERS]
    return (*registers,(0x456789AB+case['variant'])&0xFFFFFFFF,
        (0x13579BDF+case['variant'])&0xFFFFFFFF,(0x2468ACE0+case['variant'])&0xFFFFFFFF,
        case['initial_sr'],0xB6C70000)


def memory(case):
    require_case(case);ram=bytearray([0xA5])*RAM_SIZE
    for name,at,size in RAM_FIELDS:ram[at:at+size]=case[name].to_bytes(size,'big')
    return bytes(ram)


def calibrations(declared,image,case):
    fixture,_=contract.fixture_for_case(declared,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}


def require_input(declared,image,case,observed):
    inputs=calibrations(declared,image,case)
    if (not test_contract.exact(observed['entry'],case['entry'])
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],inputs)
            or not test_contract.exact(observed['calibration_after'],inputs)):
        raise ValueError('the map-bias caller original changes complete raw RAM,CPU,axes,map,selected prior or stock literal inputs')
