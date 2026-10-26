"""Input-only full raw32 carriers, signed boundaries and unrelated RAM priors."""

from kb import test_contract
from kb import signed_abs_register_helper_withdrawal_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
ENTRY=0x22590
REGISTERS=tuple(f'raw_r{index}' for index in range(8))
RAM_FIELDS=tuple((f'raw_control_byte_{index}',0x2C1C+index,1) for index in range(4))
WIDTHS={name:32 for name in REGISTERS}
WIDTHS.update({name:8 for name,address,width in RAM_FIELDS})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,
    (0x12345678,0x87654321,0xCAFEBABE,0xDEADBEEF,1,0xAABBCCDD,0x01000000,0x9ABC))})
DEFAULTS.update({name:0xA5 for name,address,width in RAM_FIELDS})
DEFAULTS.update(variant=7,initial_sr=0)
ENTRY_FIELDS={ENTRY:('raw_r4',)}
ARGUMENT_BOUNDARIES=(0,1,2,0x7F,0x80,0xFF,0x100,0x7FFF,0x8000,0xFFFF,
    0x10000,0x10001,0x7FFFFF,0x800000,0xFFFFFF,0x1000000,0x01002C1C,0xFFFF2C1C,
    0x55555555,0x7FFFFFFE,0x7FFFFFFF,0x80000000,0x80000001,0xAAAAAAAA,
    0xFFFF0000,0xFFFFFFFE,0xFFFFFFFF)


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):
        row=dict(DEFAULTS,entry=ENTRY,kind=kind);row.update(changes);inputs.append(row)
    for raw in ARGUMENT_BOUNDARIES:add('full-raw32-signed-boundary',raw_r4=raw)
    for raw in (0,1,0x80000000,0xFFFFFFFF):
        for variant in (0,7,255):
            for sr in (0,1,0x3F0,0x3F1):
                add('complete-return-and-SR-context',raw_r4=raw,variant=variant,initial_sr=sr)
    for name,address,width in RAM_FIELDS:
        for raw in (0,1,0x7F,0x80,0xFF):
            for argument in (0,1,0x80000000):
                add('selected-raw-byte-prior-only',raw_r4=argument,**{name:raw})
    for name in REGISTERS:
        for raw in (0,0x80000000,0xFFFFFFFF):add('complete-register-context',**{name:raw})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry']!=ENTRY
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr'] not in (0,1,0x3F0,0x3F1)):
        raise ValueError('a signed-magnitude input changes an exact raw32 carrier, raw byte, SR or natural entry')


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+index*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for index in range(15)]
    registers[:8]=[case[name] for name in REGISTERS]
    return (*registers,(0x456789AB+case['variant'])&0xFFFFFFFF,
        (0x13579BDF+case['variant'])&0xFFFFFFFF,(0x2468ACE0+case['variant'])&0xFFFFFFFF,
        case['initial_sr'],0xB6C70000)


def memory(case):
    require_case(case);raw=bytearray([0xA5])*RAM_SIZE
    for name,address,width in RAM_FIELDS:raw[address]=case[name]
    return bytes(raw)


def calibrations(declared,image,case):
    fixture,_=contract.fixture_for_case(declared,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.READONLY_OBSERVATION}


def require_input(declared,image,case,observed):
    expected=calibrations(declared,image,case)
    if (not test_contract.exact(observed['entry'],case['entry'])
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],expected)
            or not test_contract.exact(observed['calibration_after'],expected)):
        raise ValueError('the signed-magnitude original changes complete raw CPU/RAM or immutable code observations')
