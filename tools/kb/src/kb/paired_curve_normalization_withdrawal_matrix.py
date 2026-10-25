"""Input-only complete raw paired curve normalization and physical endpoint lookahead."""
from kb import test_contract
from kb import paired_curve_normalization_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('word_119e', 4510, 2),
 ('word_11a0', 4512, 2),
 ('byte_11a2', 4514, 1),
 ('byte_11c1', 4545, 1),
 ('byte_11c2', 4546, 1),
 ('byte_12df', 4831, 1),
 ('byte_15ea', 5610, 1),
 ('word_18cc', 6348, 2),
 ('word_18ce', 6350, 2),
 ('word_18d4', 6356, 2),
 ('byte_23e2', 9186, 1),
 ('byte_23f1', 9201, 1),
 ('byte_2404', 9220, 1),
 ('byte_413f', 16703, 1),
 ('dword_9818', 38936, 4))
AXIS_FIELDS=tuple(f'curve_axis_{i}' for i in range(16))
VALUE_FIELDS=tuple(f'curve_value_{i}' for i in range(17))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update(word_119e=101,word_11a0=100,byte_11a2=10,byte_11c1=20,byte_11c2=20,
    byte_12df=10,byte_15ea=0,word_18cc=1000,word_18ce=0xA5C3,word_18d4=0xC3A5,
    byte_23e2=246,byte_23f1=100,byte_2404=0,byte_413f=20,dword_9818=0xA5C3D2E1,
    config_8710=0,variant=7)
DEFAULTS.update({field:i*16 for i,field in enumerate(AXIS_FIELDS)})
DEFAULTS.update({field:i*15 for i,field in enumerate(VALUE_FIELDS)})
ENTRY_FIELDS={0x655B4:('config_8710','byte_12df','byte_23f1','byte_2404','byte_15ea','byte_11c2',
    'word_11a0','word_119e','byte_23e2','byte_413f','word_18cc','word_18ce',*AXIS_FIELDS,*VALUE_FIELDS[:16]),
    0x65B08:('config_8710','byte_12df','byte_23f1','byte_2404','byte_15ea','byte_11c1',
    'byte_11a2','word_18cc',*AXIS_FIELDS,*VALUE_FIELDS[:16])}
BYTE_VALUES=(0,1,2,3,4,7,8,15,16,17,20,31,32,63,64,100,101,127,128,129,240,254,255)
WORD_VALUES=(0,1,127,128,255,256,1000,32767,32768,65534,65535)


def curve_profile(first):
    delta=255-first;extra=min(delta,127);unsigned=delta-extra;base=first+unsigned
    return dict(config_8710=0,byte_23f1=127,byte_2404=(127-base)&255,byte_12df=unsigned,
        byte_15ea=0,byte_11c1=extra,byte_11c2=extra,word_18cc=1000)


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for entry in contract.ENTRIES:
        for register in REGISTERS:
            for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
                add(entry,'complete-raw-register-width',**{register:value})
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):add(entry,'complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
        for variant in (0,7,255):add(entry,'complete-preserved-register-context',variant=variant)
        profiles=({},dict(config_8710=32),dict(config_8710=32,word_11a0=100,word_119e=100))
        for profile in profiles:
            for field in ENTRY_FIELDS[entry]:
                if field in (*AXIS_FIELDS,*VALUE_FIELDS):continue
                for value in (WORD_VALUES if WIDTHS[field]==16 else BYTE_VALUES):
                    add(entry,'independent-active-flag-signed-byte-word-and-normalization-input',**dict(profile,**{field:value}))
        for i in range(16):
            profile=curve_profile(0 if i==15 else i*16+8)
            for field in (AXIS_FIELDS[i],VALUE_FIELDS[i]):
                for value in BYTE_VALUES:
                    add(entry,'each-physical-axis-and-influential-data-byte-with-fixed-other-inputs',**dict(profile,**{field:value}))
        for coordinate in BYTE_VALUES:
            profile=curve_profile(coordinate)
            add(entry,'full-byte-coordinate-and-natural-descending-axis-scan',**profile)
        for raw in BYTE_VALUES:
            add(entry,'complete-unordered-raw-axis-and-byte-data-preimages',**dict(curve_profile(120),
                **{field:(i*73+raw)&255 for i,field in enumerate(AXIS_FIELDS)},
                **{field:(i*91+raw)&255 for i,field in enumerate(VALUE_FIELDS)}))
            add(entry,'physical-lookahead16-remains-bound-without-numerical-causality-admission',
                **dict(curve_profile(0),curve_value_16=raw))
        for word in WORD_VALUES:
            for active in (0,32):
                add(entry,'complete-signed-word-product-and-variable-positive-divider-boundary',word_18cc=word,config_8710=active)
        for word in WORD_VALUES:
            add(entry,'real-positive-and-negative-ratio-saturation-with-unit-divisor',
                **dict(curve_profile(0),word_18cc=word,curve_value_0=255,curve_value_15=0))
        for field,address,width in RAM_FIELDS:
            for raw in (0,(1<<(8*width))-1):add(entry,'complete-prior-RAM-preimage',**{field:raw})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a paired curve input changes a complete raw byte,word,dword,register,axis,data or SR width')


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
        raise ValueError('the paired curve normalization caller withdrawal original changes complete raw RAM, CPU or complete paired curve/axis/lookahead/divider/pool inputs')
