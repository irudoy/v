"""Input-only complete direct word arithmetic and two raw word-curve lookups."""
from kb import test_contract
from kb import paired_word_curve_sum_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('word_120e', 4622, 2),
 ('word_1340', 4928, 2),
 ('word_183e', 6206, 2),
 ('word_19b2', 6578, 2),
 ('word_19b6', 6582, 2),
 ('byte_24ce', 9422, 1),
 ('byte_24d2', 9426, 1),
 ('word_28bc', 10428, 2),
 ('word_28be', 10430, 2),
 ('word_2a1c', 10780, 2))
CURVE_FIELDS=tuple(f'curve_word_{i:02d}' for i in range(33))
AXIS_FIELDS=tuple(f'axis_word_{i:02d}' for i in range(32))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update(word_120e=400,word_1340=500,word_183e=1000,word_19b2=0xA53C,word_19b6=0x3CA5,
    word_2a1c=200,byte_24ce=0,byte_24d2=1,word_28bc=1000,word_28be=10000,variant=7)
DEFAULTS.update({name:i*1800 for i,name in enumerate(CURVE_FIELDS)})
DEFAULTS.update({name:i*2048 for i,name in enumerate(AXIS_FIELDS)})
NORMAL_FIELDS=('word_183e','word_1340','word_120e','word_2a1c')
ENTRY_FIELDS={0x72C3C:(*NORMAL_FIELDS,'byte_24ce','byte_24d2','word_28bc','word_28be',*CURVE_FIELDS[:32],'axis_words')}
WORD_VALUES=(0,1,2,3,4,127,128,255,256,32767,32768,65533,65534,65535)
BYTE_VALUES=(0,1,2,3,4,5,7,8,127,128,129,254,255)
BASE_AXIS=tuple(i*2048 for i in range(32))


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=0x72C3C,kind=kind,**changes))
    def axis_changes(values):return dict(zip(AXIS_FIELDS,values))
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):add('complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-context',variant=variant)
    for field,address,width in RAM_FIELDS:
        for raw in WORD_VALUES if width==2 else BYTE_VALUES:
            profile=dict(byte_24d2=0,byte_24ce=0) if field in NORMAL_FIELDS else {}
            add('complete-independent-RAM-operand-or-prior-state',**dict(profile,**{field:raw}))
    for raw in BYTE_VALUES:
        add('alternate-mode-control-other-bit-clear',byte_24d2=0,byte_24ce=raw)
    for index,field in enumerate(CURVE_FIELDS):
        for raw in WORD_VALUES:
            add('each-independent-physical-curve-word',word_28bc=BASE_AXIS[min(index,31)],**{field:raw})
    for index,field in enumerate(AXIS_FIELDS):
        for raw in (0,1,32767,32768,65535):
            for coordinate in (max(0,BASE_AXIS[index]-1),min(65535,BASE_AXIS[index]+1)):
                add('independent-raw-axis-word-without-ordering-premise',word_28bc=coordinate,**{field:raw})
    patterns=(BASE_AXIS,tuple(65535-v for v in BASE_AXIS),tuple([1000]*32),
        tuple((i//2)*4096 for i in range(32)),tuple((i*7919)&65535 for i in range(32)))
    for knots in patterns:
        for coordinate in (0,1,999,1000,1001,32767,32768,63487,63488,63489,65534,65535):
            for target in ('word_28bc','word_28be'):
                add('complete-flat-duplicate-descending-and-nonmonotonic-axis',**dict(axis_changes(knots),**{target:coordinate}))
    for index in range(32):
        for delta in (-1,0,1,1024):
            coordinate=max(0,min(65535,BASE_AXIS[index]+delta))
            for target in ('word_28bc','word_28be'):
                add('each-knot-endpoint-neighbor-and-fraction-cell',**{target:coordinate})
    for first in (0,1,32767,65534,65535):
        for second in (0,1,32767,65534,65535):
            for subtract in (0,3,4,65532,65535):
                add('direct-floor-first-cap-and-second-cap-boundaries',byte_24d2=0,byte_24ce=0,
                    word_183e=first,word_1340=second,word_120e=subtract,word_2a1c=second)
    for raw in (0,1,32767,32768,65534,65535):
        add('two-real-curve-result-sum-cap',**{field:raw for field in CURVE_FIELDS})
    for first,second in ((0,65535),(65535,0),(32767,32768),(32768,32767)):
        add('both-interpolation-directions-full-word-domain',word_28bc=1024,word_28be=3072,
            **{field:(first if index%2==0 else second) for index,field in enumerate(CURVE_FIELDS)})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a paired word curve input changes a complete raw register,byte,word,knot,curve or SR width')


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+index*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for index in range(15)]
    registers[:8]=[case[name] for name in REGISTERS]
    return (*registers,(0x456789AB+case['variant'])&0xFFFFFFFF,
        (0x13579BDF+case['variant'])&0xFFFFFFFF,(0x2468ACE0+case['variant'])&0xFFFFFFFF,
        case['initial_sr'],0xB6C70000)


def memory(case):
    require_case(case);result=bytearray([0xA5])*RAM_SIZE
    for name,at,width in RAM_FIELDS:result[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(result)


def calibrations(declared,image,case):
    fixture,_=contract.fixture_for_case(declared,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}


def require_input(declared,image,case,observed):
    expected=calibrations(declared,image,case)
    if (not test_contract.exact(observed['entry'],case['entry'])
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],expected)
            or not test_contract.exact(observed['calibration_after'],expected)):
        raise ValueError('the paired word curve sum withdrawal original changes complete raw RAM, CPU or complete raw arithmetic/gate/paired-word-coordinate/curve/axis/pool inputs')
