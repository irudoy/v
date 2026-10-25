"""Input-only complete raw word products,signed counter and independent auxiliary gate."""
from kb import test_contract
from kb import aux_rate_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('word_2018', 8216, 2),
 ('word_201a', 8218, 2),
 ('word_201e', 8222, 2),
 ('word_235c', 9052, 2),
 ('byte_244f', 9295, 1),
 ('byte_24c0', 9408, 1),
 ('word_34e4', 13540, 2),
 ('word_34e6', 13542, 2),
 ('byte_4184', 16772, 1),
 ('byte_41a5', 16805, 1),
 ('byte_41bd', 16829, 1),
 ('byte_4251', 16977, 1),
 ('dword_9818', 38936, 4))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update(word_2018=200,word_201a=1000,word_201e=0xA5C3,word_235c=100,
    byte_24c0=4,byte_4251=0,byte_4184=0,byte_244f=32,byte_41a5=4,byte_41bd=0,
    word_34e4=0,word_34e6=0,dword_9818=0xA5C3D2E1,variant=7)
ENTRY_FIELDS={0x68D58:('byte_24c0','byte_4251','word_235c','word_2018','word_201a',
    'byte_4184','byte_244f','byte_41a5','byte_41bd','word_34e4','word_34e6')}
BYTE_VALUES=(0,1,2,3,4,7,8,15,16,20,31,32,63,64,127,128,129,254,255)
WORD_VALUES=(0,1,19,20,21,124,125,126,249,250,251,255,256,399,400,401,1000,3999,4000,4001,32767,32768,65534,65535)


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=0x68D58,kind=kind,**changes))
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
            add('complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-context',variant=variant)
    for profile in ({},{'word_34e4':20}):
        for field in ENTRY_FIELDS[0x68D58]:
            for value in (WORD_VALUES if WIDTHS[field]==16 else BYTE_VALUES):
                add('independent-active-counter-word-flag-and-real-auxiliary-gate-input',**dict(profile,**{field:value}))
    for first in WORD_VALUES:
        for second in WORD_VALUES:
            add('complete-unsigned-word-product-and-real-short-long-divider-boundary',word_235c=first,word_201a=second)
    for old in (0,1,124,125,126,32767,32768,65534,65535):
        for measured in (0,1,124,125,249,250,65535):
            add('sign-extended-saved-counter-two-dword-carriers-and-ordered-clamps',word_2018=old,word_201a=measured)
    for first in WORD_VALUES:
        for second in (0,19,20,21,32767,32768,65535):
            add('raw-sign-extended-first-auxiliary-word-and-unsigned-second-word',word_34e4=first,word_34e6=second)
    for initial in (0,1):
        for flag in (0,1):
            for blocker in (0,64):
                add('real-initialization-and-post-gate-publication-clear',byte_4251=initial,
                    word_34e4=20 if flag else 0,byte_4184=blocker)
    for name,address,width in RAM_FIELDS:
        for value in (0,(1<<(8*width))-1):add('complete-prior-RAM-preimage',**{name:value})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('an auxiliary rate input changes a complete raw byte,word,dword,register or SR width')


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
        raise ValueError('the auxiliary rate caller withdrawal original changes complete raw RAM, CPU or complete counter-rate/auxiliary-gate/divider/pool inputs')
