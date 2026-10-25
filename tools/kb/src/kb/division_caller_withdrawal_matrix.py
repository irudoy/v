"""Input-only complete bounded-divisor callers, signed raw argument and SR contexts."""
from kb import test_contract
from kb import division_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('source_level', 4531, 1),
 ('factor', 5990, 1),
 ('previous_first', 4128, 1),
 ('previous_second', 4494, 1),
 ('previous_scaled', 8070, 1),
 ('previous_clamped', 13312, 4),
 ('previous_fault', 38936, 4))
WIDTHS={n:w*8 for n,at,w in RAM_FIELDS}
WIDTHS.update({n:32 for n in REGISTERS})
WIDTHS.update(enable_mask=8,factor_first=8,factor_second=8,variant=8,initial_sr=10)
DEFAULTS={n:0 for n in WIDTHS}
DEFAULTS.update({n:v for n,v in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,0x9ABC,0x01000000))})
DEFAULTS.update(source_level=50,factor=60,previous_first=0xA5,previous_second=0x5A,
    previous_scaled=0xA5,previous_clamped=0xA5A55A5A,previous_fault=0x13579BDF,
    enable_mask=8,factor_first=50,factor_second=60,variant=7,initial_sr=0)
ENTRY_FIELDS={0x3A254:('raw_r4','enable_mask'),0x6E442:('source_level','factor'),
    0xB7C84:('raw_r4','factor_first','factor_second')}
BYTE_BOUNDARIES=(0,1,2,4,8,31,32,64,127,128,254,255)
SIGNED_ARGUMENTS=(0,1,19,20,21,5099,5100,5119,5120,65535,107349,107350,107351,
    0x7FFFFFFF,0x80000000,(-107351)&0xFFFFFFFF,(-107350)&0xFFFFFFFF,
    (-107349)&0xFFFFFFFF,(-1)&0xFFFFFFFF)


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for enable in BYTE_BOUNDARIES:
        for argument in SIGNED_ARGUMENTS:add(0x3A254,'enabled-word-quotient-clamp',enable_mask=enable,raw_r4=argument)
    for high in (0,0x12340000,0x80000000,0xFFFF0000):
        for low in (0,1,19,20,5099,5100,5119,5120,65535):
            add(0x3A254,'raw-register-to-unsigned-word',raw_r4=high|low)
    for level in range(256):
        for factor in (0,1,127,128,255):add(0x6E442,'every-source-byte-and-factor-sign-boundary',source_level=level,factor=factor)
    for first in BYTE_BOUNDARIES:
        for second in BYTE_BOUNDARIES:
            for argument in (0,1,0xFFFFFFFF,107350,(-107350)&0xFFFFFFFF):
                add(0xB7C84,'byte-product-zero-cap-signed-output',raw_r4=argument,factor_first=first,factor_second=second)
    for argument in SIGNED_ARGUMENTS:
        for first,second in ((0,1),(1,0),(1,1),(50,60),(127,128),(255,255)):
            add(0xB7C84,'signed-input-product-and-result-clamps',raw_r4=argument,factor_first=first,factor_second=second)
    for entry in contract.ENTRIES:
        for register in REGISTERS:
            for word in (0,0x80000000,0xFFFFFFFF):add(entry,'complete-raw-register-context',**{register:word})
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):add(entry,'complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
        for variant in (0,7,255):add(entry,'complete-unused-register-context',variant=variant)
    for sr in (0,1,0x300,0x301):
        add(0x3A254,'disabled-complete-context',initial_sr=sr,enable_mask=0)
        add(0x6E442,'zero-level-complete-context',initial_sr=sr,source_level=0)
        add(0xB7C84,'zero-product-negative-context',initial_sr=sr,factor_first=0,raw_r4=0xFFFFFFFF)
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
        raise ValueError('a division caller input changes raw argument, RAM/configuration width, SR context or exact natural entry')


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
        raise ValueError('the division caller withdrawal original changes complete raw RAM, CPU or byte/word configuration/pool inputs')
