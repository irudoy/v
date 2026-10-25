"""Input-only constant-root byte curves, caller modes and complete raw CPU/RAM/SR preimages."""
from kb import test_contract
from kb import byte_curve_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('coordinate_first', 4215, 1),
 ('coordinate_second', 4207, 1),
 ('mode', 9295, 1),
 ('denominator', 5809, 1),
 ('gain', 5806, 1),
 ('previous_first', 7972, 1),
 ('previous_first_word', 7764, 2),
 ('previous_second', 5990, 1),
 ('previous_fault', 38936, 4))
CURVE_FIELDS={name:tuple(f'curve_{name}_{i}' for i in range(8)) for name in ('first','second')}
WIDTHS={n:w*8 for n,at,w in RAM_FIELDS}
WIDTHS.update({n:32 for n in REGISTERS})
WIDTHS.update({n:8 for names in CURVE_FIELDS.values() for n in names})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={n:0 for n in WIDTHS}
DEFAULTS.update({n:v for n,v in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,0x9ABC,0x01000000))})
DEFAULTS.update({name:i*32 for names in CURVE_FIELDS.values() for i,name in enumerate(names)})
DEFAULTS.update(coordinate_first=64,coordinate_second=64,mode=2,denominator=32,gain=64,
    previous_first=0xA5,previous_first_word=0x5A5A,previous_second=0xA5,
    previous_fault=0x13579BDF,variant=7,initial_sr=0)
ENTRY_FIELDS={0x2C59C:('coordinate_first',*CURVE_FIELDS['first']),
    0x6E3D8:('coordinate_second','mode','denominator','gain',*CURVE_FIELDS['second'])}
BYTE_BOUNDARIES=(0,1,2,4,8,31,32,64,127,128,224,255)
SHAPES=((0,32,64,96,128,160,192,224),(255,223,191,159,127,95,63,31),
    (127,)*8,(0,255,0,255,0,255,0,255))


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for entry,name,coordinate in ((0x2C59C,'first','coordinate_first'),(0x6E3D8,'second','coordinate_second')):
        for shape in SHAPES:
            table=dict(zip(CURVE_FIELDS[name],shape))
            for value in range(256):add(entry,'all-byte-coordinates-and-real-segment-directions',**{coordinate:value,**table})
        for index,field in enumerate(CURVE_FIELDS[name]):
            for value in (0,1,127,128,254,255):
                add(entry,'independent-curve-cell-at-exact-knot',**{coordinate:32*index,field:value})
        for register in REGISTERS:
            for value in (0,0x80000000,0xFFFFFFFF):add(entry,'complete-raw-register-context',**{register:value})
        for variant in (0,7,255):add(entry,'complete-unused-register-context',variant=variant)
    for coordinate in BYTE_BOUNDARIES:
        for gain in BYTE_BOUNDARIES:
            for denominator in BYTE_BOUNDARIES:
                add(0x6E3D8,'scaled-byte-curve-positive-divisor-or-zero-bypass',mode=0,
                    coordinate_second=coordinate,gain=gain,denominator=denominator)
    for shape in SHAPES:
        table=dict(zip(CURVE_FIELDS['second'],shape))
        for coordinate in (0,1,31,32,127,223,224,255):
            for gain in (0,64,255):
                for denominator in (1,32,255):
                    add(0x6E3D8,'scaled-direction-and-intermediate-frame-overwrite',mode=0,
                        coordinate_second=coordinate,gain=gain,denominator=denominator,**table)
    for mode in BYTE_BOUNDARIES:
        for coordinate in (0,31,32,223,224,255):add(0x6E3D8,'full-mode-byte-and-endpoint-sign',mode=mode,coordinate_second=coordinate)
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):
                sr=qm|interrupt|t
                add(0x2C59C,'complete-QM-interrupt-T-context',initial_sr=sr)
                add(0x6E3D8,'complete-QM-interrupt-T-direct',initial_sr=sr)
                add(0x6E3D8,'complete-QM-interrupt-T-scaled',initial_sr=sr,mode=0)
                add(0x6E3D8,'complete-QM-interrupt-T-zero-bypass',initial_sr=sr,mode=0,denominator=0)
    for entry in contract.ENTRIES:
        for name,at,width in RAM_FIELDS:
            if not name.startswith('previous_'):continue
            for value in (0,(1<<(8*width))-1):add(entry,'complete-prior-RAM-preimage',**{name:value})
    return tuple(dict(row,index=i) for i,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[n]) is not int or not 0<=case[n]<(1<<bits) for n,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a byte-curve caller input changes its exact raw width, curve cell, SR context or natural constant-root entry')


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
        raise ValueError('the byte curve caller withdrawal original changes complete raw RAM, CPU or byte/word configuration/pool inputs')
