"""Input-only complete raw32 operands, minimum-word boundaries and CPU context."""

from kb import test_contract
from kb import register_overflow_path_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{index}' for index in range(8))
RAM_FIELDS=()
WIDTHS={name:32 for name in REGISTERS}
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(
    0x12345678,0x87654321,0x87654321,0x00008000,1,1,0x9ABC,0x01000000))})
DEFAULTS.update(variant=7,initial_sr=0)
ENTRY_FIELDS={0x265C4:('raw_r4','raw_r5')}
BOUNDARIES=(0,1,2,65535,65536,0x3FFFFFFF,0x40000000,0x7FFFFFFE,0x7FFFFFFF,
    0x80000000,0x80000001,0xBFFFFFFF,0xC0000000,0xFFFF0000,0xFFFFFFFE,0xFFFFFFFF)


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=0x265C4,kind=kind,**changes))
    for first in BOUNDARIES:
        for second in BOUNDARIES:add('raw32-sign-wrap-overflow',raw_r4=first,raw_r5=second)
    paths=((0,1),(0x7FFFFFFF,1),(0,0xFFFFFFFF),(0x80000000,0xFFFFFFFF),
        (0,0x80000000),(1,0x80000000),(0xFFFFFFFF,0x80000000),(0x80000000,0x80000000))
    for first,second in paths:
        for variant in (0,7,255):
            for sr in (0,1,0x3F0,0x3F1):
                add('all-natural-return-and-SR-contexts',raw_r4=first,raw_r5=second,variant=variant,initial_sr=sr)
    for name in REGISTERS:
        for value in (0,0x80000000,0xFFFFFFFF):add('complete-register-context',**{name:value})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry']!=0x265C4
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr'] not in (0,1,0x3F0,0x3F1)):
        raise ValueError('a register overflow input changes an exact raw32 operand, context, SR or natural entry')


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+index*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for index in range(15)]
    registers[:8]=[case[name] for name in REGISTERS]
    return (*registers,(0x456789AB+case['variant'])&0xFFFFFFFF,
        (0x13579BDF+case['variant'])&0xFFFFFFFF,(0x2468ACE0+case['variant'])&0xFFFFFFFF,
        case['initial_sr'],0xB6C70000)


def memory(case):
    require_case(case);return bytes([0xA5])*RAM_SIZE


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
        raise ValueError('the register overflow original changes complete raw CPU, RAM or immutable constant inputs')
