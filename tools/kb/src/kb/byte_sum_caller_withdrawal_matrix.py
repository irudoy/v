"""Input-only complete byte curve, minimum and two unsigned saturating sums."""
from kb import test_contract
from kb import byte_sum_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('byte_1716', 5910, 1),
 ('word_173c', 5948, 2),
 ('word_173e', 5950, 2),
 ('byte_1740', 5952, 1),
 ('byte_1741', 5953, 1),
 ('byte_1742', 5954, 1),
 ('word_1748', 5960, 2),
 ('word_174c', 5964, 2),
 ('byte_174f', 5967, 1),
 ('byte_22e4', 8932, 1))
CURVE_FIELDS=tuple(f'curve_value_{i}' for i in range(8))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update(byte_22e4=64,byte_1716=0xA5,byte_1740=100,byte_1741=100,byte_1742=50,
    byte_174f=200,word_173c=0xA5C3,word_173e=0xC3A5,word_1748=0x5AA5,word_174c=1000,variant=7)
DEFAULTS.update({field:15+i*32 for i,field in enumerate(CURVE_FIELDS)})
ENTRY_FIELDS={0x464DE:('byte_22e4','byte_1741','byte_174f','byte_1742','word_174c','byte_1740',*CURVE_FIELDS)}
BYTE_VALUES=(0,1,2,3,4,7,8,15,16,17,31,32,39,40,41,47,48,63,64,95,96,103,104,127,128,129,223,224,254,255)
WORD_VALUES=(0,1,127,128,255,256,32767,32768,65000,65279,65280,65533,65534,65535)


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=0x464DE,kind=kind,**changes))
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
            add('complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-context',variant=variant)
    for field in ENTRY_FIELDS[0x464DE]:
        if field in CURVE_FIELDS:continue
        for raw in WORD_VALUES if WIDTHS[field]==16 else BYTE_VALUES:
            add('independent-raw-coordinate-byte-summand-or-full-word-preimage',**{field:raw})
    for i,field in enumerate(CURVE_FIELDS):
        for raw in BYTE_VALUES:
            add('each-independent-raw-eight-cell-value-and-signed-endpoint',byte_22e4=40+8*i+4,**{field:raw})
    for raw in BYTE_VALUES:add('complete-byte-coordinate-lower40-upper104-and-endpoint96-boundaries',byte_22e4=raw)
    for limit in (0,1,127,128,254,255):
        for summand in (0,1,127,128,254,255):
            for delta in (-1,0,1):
                add('full-byte-minimum-and-first-word-saturation-boundary',byte_1741=summand,byte_1742=limit,
                    word_174c=max(0,min(65535,65535-summand-limit+delta)),**{field:255 for field in CURVE_FIELDS})
                add('full-unsigned-second-word-saturation-boundary',byte_1741=0,byte_1742=0,byte_1740=limit,
                    word_174c=max(0,min(65535,65535-limit+delta)))
    for first in (0,1,127,128,254,255):
        for limit in (0,1,127,128,254,255):
            add('full-independent-byte-minimum-and-separate-unclipped-three-byte-sum',byte_1741=255,
                byte_174f=255,byte_1742=first,**{field:limit for field in CURVE_FIELDS})
    for name,address,width in RAM_FIELDS:
        for raw in (0,(1<<(8*width))-1):add('complete-prior-RAM-preimage',**{name:raw})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a byte sum input changes a complete raw byte,word,curve,register or SR width')


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
        raise ValueError('the byte sum caller withdrawal original changes complete raw RAM, CPU or complete clipped-byte coordinate/curve/minimum/saturating-sum/pool inputs')
