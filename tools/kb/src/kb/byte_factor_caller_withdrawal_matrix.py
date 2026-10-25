"""Input-only complete signed-word difference, dual curves and partial products."""
from kb import test_contract
from kb import byte_factor_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('word_1024', 4132, 2),
 ('word_11bc', 4540, 2),
 ('word_15fc', 5628, 2),
 ('word_15fe', 5630, 2),
 ('byte_1657', 5719, 1),
 ('byte_1658', 5720, 1),
 ('byte_1659', 5721, 1),
 ('byte_2458', 9304, 1),
 ('byte_2478', 9336, 1))
CURVE_FIELDS=tuple(f'curve_value_{i}' for i in range(16))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update(word_1024=8192,word_11bc=128,word_15fc=1000,word_15fe=100,
    byte_1657=128,byte_1658=0xA5,byte_1659=0x5A,byte_2458=0,byte_2478=0,
    config_886b=128,config_886d=16,variant=7)
DEFAULTS.update({field:15+i*32 if i<8 else 255-(i-8)*31 for i,field in enumerate(CURVE_FIELDS)})
# The override's1657 read feeds only the same1657 publication. Its complete
# raw preimage and arithmetic remain bound;it is not an outside-input causal claim.
ENTRY_FIELDS={0x4BA48:('byte_2478','byte_2458','word_15fc','word_15fe','word_1024','word_11bc',
    'config_886b','config_886d',*CURVE_FIELDS)}
BYTE_VALUES=(0,1,2,3,4,7,8,15,16,17,31,32,63,64,96,127,128,129,191,192,223,224,254,255)
WORD_VALUES=(0,1,31,32,33,127,128,255,256,287,288,1023,1024,8192,32767,32768,32769,65534,65535)


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=0x4BA48,kind=kind,**changes))
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
            add('complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-context',variant=variant)
    for profile in ({},dict(byte_2478=2),dict(byte_2458=32)):
        for field in ENTRY_FIELDS[0x4BA48]:
            if field in CURVE_FIELDS:continue
            for value in WORD_VALUES if WIDTHS[field]==16 else BYTE_VALUES:
                add('independent-override-mode-signed-word-coordinate-or-percentage-input',**dict(profile,**{field:value}))
    for prior in BYTE_VALUES:
        for decrement in BYTE_VALUES:
            add('in-place-byte-override-clamp-with-complete-prior-publication',byte_2478=2,byte_1657=prior,config_886d=decrement)
    for first in WORD_VALUES:
        for second in WORD_VALUES:
            for mode in (0,32):add('full-unsigned-first-and-signed-second-word-difference',word_15fc=first,word_15fe=second,byte_2458=mode)
    for i,field in enumerate(CURVE_FIELDS):
        coordinate=min(255,(i%8)*32+16)
        profile=dict(word_11bc=coordinate+32) if i<8 else dict(word_1024=coordinate*128)
        for raw in BYTE_VALUES:add('each-independent-raw-curve-cell-and-direction',**dict(profile,**{field:raw}))
    for coordinate in (0,1,31,32,33,63,64,127,128,191,192,223,224,225,254,255):
        for delta in (-1,0,1):
            add('full-unsigned-first-coordinate-shift7-and-cap',word_1024=max(0,min(65535,coordinate*128+delta)))
            add('full-unsigned-second-coordinate-subtract32-and-cap',word_11bc=max(0,min(65535,coordinate+32+delta)))
    for first,second in ((0,0),(0,1),(0,32767),(0,32768),(65535,32768),(65535,65535),(65535,0)):
        for factor in (0,1,2,127,128,254,255):
            add('complete-low-high-partial-product-and-high-term-or-final-byte-cap',word_15fc=first,word_15fe=second,
                **{field:factor for field in CURVE_FIELDS})
            add('complete-percentage-mode-low32-product-logical-shift14-and-byte-cap',word_15fc=first,
                word_15fe=second,byte_2458=32,config_886b=factor)
    for name,address,width in RAM_FIELDS:
        for raw in (0,(1<<(width*8))-1):add('complete-prior-RAM-preimage',**{name:raw})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a byte factor input changes a complete raw byte,signed/unsigned word,curve,register or SR width')


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
        raise ValueError('the byte factor caller withdrawal original changes complete raw RAM, CPU or complete signed-word difference/dual-byte-factor/pool inputs')
