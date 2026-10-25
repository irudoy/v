"""Input-only complete word products, signed gains, divisors, flags and blend preimages."""
from kb import test_contract
from kb import scaled_division_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('reciprocal_source', 5714, 2),
 ('reciprocal_gain', 5598, 1),
 ('previous_reciprocal_step', 4802, 2),
 ('previous_reciprocal_word', 5824, 2),
 ('first_source', 9212, 2),
 ('first_factor', 6562, 2),
 ('first_gain', 6586, 2),
 ('previous_first', 6376, 2),
 ('second_source', 7374, 2),
 ('second_factor', 7446, 2),
 ('second_gain', 7450, 2),
 ('previous_second', 7416, 2),
 ('flag_first', 9311, 1),
 ('flag_second', 16766, 1),
 ('flag_third', 9371, 1),
 ('blend_weight', 9250, 2),
 ('history_word', 7414, 2),
 ('previous_blend', 7424, 2),
 ('previous_fault', 38936, 4))
WIDTHS={n:w*8 for n,at,w in RAM_FIELDS}
WIDTHS.update({n:32 for n in REGISTERS})
WIDTHS.update(first_divisor=16,second_divisor=16,variant=8,initial_sr=10)
DEFAULTS={n:0 for n in WIDTHS}
DEFAULTS.update({n:v for n,v in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,0x9ABC,0x01000000))})
DEFAULTS.update(reciprocal_source=32768,reciprocal_gain=16,previous_reciprocal_step=0xA55A,
    previous_reciprocal_word=0x5AA5,first_source=1000,first_factor=1000,first_gain=64,
    previous_first=0xA55A,second_source=1000,second_factor=1000,second_gain=64,previous_second=0xA55A,
    blend_weight=32768,history_word=0xC000,previous_blend=0x5AA5,previous_fault=0x13579BDF,
    first_divisor=0x351E,second_divisor=0x351E,variant=7,initial_sr=0)
ENTRY_FIELDS={0x4E59C:('reciprocal_source','reciprocal_gain'),
    0x74B04:('first_source','first_factor','first_gain','first_divisor'),
    0x74478:('second_source','second_factor','second_gain','second_divisor',
        'flag_first','flag_second','flag_third','blend_weight','history_word')}
WORDS=(0,1,2,31,32,63,64,127,128,255,256,32767,32768,65534,65535)
BYTES=(0,1,2,31,32,64,127,128,254,255)
DIVISORS=(0,1,2,0x351E,65535)


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for word in (*WORDS,5461,5462,10922,10923,16383,16384):
        for gain in BYTES:add(0x4E59C,'unsigned-six-times-product-reciprocal-and-zero-fault',reciprocal_source=word,reciprocal_gain=gain)
    for entry,prefix in ((0x74B04,'first'),(0x74478,'second')):
        for source in WORDS:
            for factor in (0,1,2,32767,32768,65535):
                for gain in (0,1,32767,32768,65535):
                    for divisor in DIVISORS:
                        add(entry,'word-product-sign-wrap-shift-division-and-saturation',
                            **{prefix+'_source':source,prefix+'_factor':factor,prefix+'_gain':gain,prefix+'_divisor':divisor})
    for first in BYTES:
        for second in (0,8,255):
            for third in (0,1,255):
                add(0x74478,'complete-independent-flag-bytes',flag_first=first,flag_second=second,flag_third=third)
    for weight in WORDS:
        for history in WORDS:
            for gain in (0,32767,32768,65535):
                add(0x74478,'signed-history-blend-zero-full-or-interior-weight',blend_weight=weight,history_word=history,second_gain=gain)
    for entry in contract.ENTRIES:
        for register in REGISTERS:
            for value in (0,0x80000000,0xFFFFFFFF):add(entry,'complete-raw-register-context',**{register:value})
        for variant in (0,7,255):add(entry,'complete-preserved-register-context',variant=variant)
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):add(entry,'complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
        for name,at,width in RAM_FIELDS:
            if name.startswith('previous_'):
                for value in (0,(1<<(8*width))-1):add(entry,'complete-RAM-preimage',**{name:value})
    selected=(('reciprocal-zero-fault',0x4E59C,dict(reciprocal_source=0)),
        ('reciprocal-cap',0x4E59C,dict(reciprocal_source=5462,reciprocal_gain=1)),
        ('reciprocal-positive',0x4E59C,dict()),
        ('first-zero-fault',0x74B04,dict(first_divisor=0)),
        ('first-negative',0x74B04,dict(first_gain=65535)),
        ('first-repeat-long',0x74B04,dict(first_divisor=1000)),
        ('first-negative-long',0x74B04,dict(first_gain=65535,first_divisor=1)),
        ('first-high-cap',0x74B04,dict(first_source=32767,first_factor=64,first_gain=32767,first_divisor=1)),
        ('first-low-cap',0x74B04,dict(first_source=32767,first_factor=64,first_gain=32768,first_divisor=1)),
        ('second-zero-fault',0x74478,dict(second_divisor=0)),
        ('second-blend',0x74478,dict()),
        ('second-bypass',0x74478,dict(flag_first=128)),
        ('second-zero-weight',0x74478,dict(blend_weight=0)),
        ('second-full-weight',0x74478,dict(blend_weight=65535)))
    for kind,entry,changes in selected:add(entry,kind,**changes)
    return tuple(dict(row,index=i) for i,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[n]) is not int or not 0<=case[n]<(1<<bits) for n,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a scaled division caller input changes an exact RAM/divisor/raw-register width or SR context')


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
        raise ValueError('the scaled division caller withdrawal original changes complete raw RAM, CPU or word divisor/pool inputs')
