"""Input-only full byte domains for the natural actuator-mask caller and children."""
from kb import test_contract
from kb import actuator_mask_base_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('byte_10e4', 4324, 1),
 ('byte_110e', 4366, 1),
 ('byte_11b3', 4531, 1),
 ('byte_586c', 22636, 1),
 ('byte_5a82', 23170, 1))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update(byte_586c=0x80,byte_5a82=0,byte_11b3=44,byte_110e=10,byte_10e4=4,variant=7)
ENTRY_FIELDS={0x5096C:('byte_586c','byte_5a82','byte_11b3','byte_110e','byte_10e4')}


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=0x5096C,kind=kind,**changes))
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
            add('complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-context',variant=variant)
    for raw in range(256):
        add('first-fixed-record-byte1-bit7-entire-raw-byte',byte_586c=raw,byte_5a82=0)
        add('second-fixed-record-byte1-bit7-entire-raw-byte',byte_586c=0,byte_5a82=raw)
        add('unsigned-staged-mask-entire-raw-byte-and-thresholds43-through48',byte_11b3=raw,byte_110e=3)
        add('low-speed-entire-byte-including-signed-load-boundary',byte_110e=raw,byte_10e4=4)
        add('state-bit2-entire-raw-byte-with-admitted-low-speed',byte_110e=0,byte_10e4=raw)
    for first in (0,1,127,128,129,255):
        for second in (0,1,127,128,129,255):
            add('ordered-short-circuit-fixed-record-ids71-and123',byte_586c=first,byte_5a82=second)
    for staged in (0,42,43,44,45,46,47,48,49,127,128,255):
        for speed in (0,1,2,3,127,128,255):
            for state in (0,1,3,4,5,127,128,255):
                add('local-byte-staged-mask-OR-low-speed-mask-full-boundaries',byte_11b3=staged,byte_110e=speed,byte_10e4=state)
    for name,address,width in RAM_FIELDS:
        for raw in (0,255):add('complete-independent-RAM-preimage',**{name:raw})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('an actuator mask input changes a complete raw byte,register or SR width')


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
        raise ValueError('the actuator mask base withdrawal original changes complete raw RAM, CPU or complete fixed-record flags/staged mask/low-speed mask/pool inputs')
