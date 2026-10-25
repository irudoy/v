"""Input-only complete natural helper contexts and register-boundary alternatives."""

from kb import test_contract
from kb import register_only_helpers_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{index}' for index in range(8))
DEFAULTS={**{name:value for name,value in zip(REGISTERS,(
    0x12345678,0x87654321,0x87654321,0x00008000,0x1234,0x5678,0x9ABC,0x01000000))},
    'variant':7,'initial_sr':0}
BOUNDARIES=(0,1,31,32,63,64,127,128,255,256,1023,1024,2047,2048,
    0x7FFFFFFF,0x80000000,0xFFFFFFFF)


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for entry in contract.ENTRIES:
        for name in REGISTERS:
            for value in BOUNDARIES:add(entry,'register-boundary',**{name:value})
        for variant in (0,7,255):
            for sr in (0,1,0x3F0,0x3F1):add(entry,'complete-context',variant=variant,initial_sr=sr)
    for left in (0,1,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
        for right in (0,1,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
            for fraction in (0,1,32768,65535,65536,0xFFFFFFFF):
                add(0x26740,'interpolation-wrap',raw_r0=left,raw_r2=right,raw_r3=fraction)
    for left in (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
        for right in (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
            for subtract in (0,1,0x80000000,0xFFFFFFFF):
                for flag in (0,1,0x100,0x101,0xFFFFFFFF):
                    add(0x259D0,'conditional-compare-wrap',raw_r4=left,raw_r5=right,raw_r6=subtract,raw_r7=flag)
    for entry in (0x224F8,0x224FA,0x2251C):
        for value in (0,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
            add(entry,'positive-shift',raw_r0=value)
    for name in ('raw_r4','raw_r5','raw_r6'):
        for value in (0,1,2,32,63,64,0xFFFFFFFF):
            seed=dict(raw_r4=0,raw_r5=0,raw_r6=0);seed[name]=value
            add(0x50A4C,'positive-mask-'+name,**seed)
    for name in ('raw_r4','raw_r5','raw_r6'):
        for value in (0,1,2):
            seed=dict(raw_r4=1,raw_r5=0,raw_r6=0,raw_r7=1);seed[name]=value
            add(0x259D0,'positive-compare-'+name,**seed)
    for value in (0,1,0x100,0x101):
        add(0x259D0,'positive-compare-raw_r7',raw_r4=1,raw_r5=0,raw_r6=1,raw_r7=value)
    for name in ('raw_r0','raw_r2','raw_r3'):
        for value in (0,1,32768,65535,65536,0xFFFFFFFF):
            seed=dict(raw_r0=0,raw_r2=65536,raw_r3=32768);seed[name]=value
            add(0x26740,'positive-interpolation-'+name,**seed)
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*DEFAULTS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<=0xFFFFFFFF for name in REGISTERS)
            or type(case['variant']) is not int or not 0<=case['variant']<=255
            or type(case['initial_sr']) is not int or case['initial_sr'] not in (0,1,0x3F0,0x3F1)):
        raise ValueError('a register-only input changes its exact natural entry, complete argument or SR domain')


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+index*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for index in range(15)]
    registers[:8]=[case[name] for name in REGISTERS]
    return (*registers,(0x456789AB+case['variant'])&0xFFFFFFFF,
        (0x13579BDF+case['variant'])&0xFFFFFFFF,(0x2468ACE0+case['variant'])&0xFFFFFFFF,
        case['initial_sr'],0xB6C70000)


def memory(case):
    require_case(case)
    return bytes([0xA5])*RAM_SIZE


def calibrations(declared,image,case):
    require_case(case)
    return {row['address']:image[row['address']:row['address']+row['size']] for row in contract.OBSERVED_SPANS}


def require_input(declared,image,case,observed):
    if (not test_contract.exact(observed['entry'],case['entry'])
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('the register-only original changes a complete CPU, RAM or read-only code input')
