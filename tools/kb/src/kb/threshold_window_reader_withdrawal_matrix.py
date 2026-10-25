"""Input-only complete raw coordinate window,byte ratio and independent flag preimages."""
from kb import test_contract
from kb import threshold_window_reader_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('word_11bc', 4540, 2),
 ('byte_3fa4', 16292, 1),
 ('byte_413e', 16702, 1),
 ('byte_41d2', 16850, 1),
 ('byte_4251', 16977, 1),
 ('dword_9818', 38936, 4))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,100,100,100,8))})
DEFAULTS.update(byte_4251=128,byte_41d2=3,word_11bc=100,byte_413e=100,byte_3fa4=100,dword_9818=0xA5C3D2E1,variant=7)
ENTRY_FIELDS={0x847DC:('raw_r4','raw_r5','raw_r6','byte_4251','byte_41d2','word_11bc','byte_413e','byte_3fa4')}
BYTE_VALUES=(0,1,2,3,4,7,8,15,31,32,63,64,79,80,81,99,100,101,109,110,111,119,120,121,127,128,129,195,204,205,212,213,214,215,254,255)
WORD_VALUES=(0,1,29,30,31,69,70,99,100,129,130,195,224,225,254,255,256,32767,32768,65535)


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=0x847DC,kind=kind,**changes))
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
            add('complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-context',variant=variant)
    for field in ENTRY_FIELDS[0x847DC]:
        values=WORD_VALUES if field in ('raw_r4','word_11bc') else BYTE_VALUES
        for value in values:add('independent-active-coordinate-flag-ratio-and-split-input',**{field:value})
    for coordinate in (0,1,29,30,31,224,225,226,254,255,256,284,285,286,65535):
        for measured in WORD_VALUES:
            add('raw-low-word-coordinate-and-complete-unsigned-measured-window',raw_r4=0xA5C30000|coordinate,word_11bc=measured)
    for source in (0,1,2,3,79,80,100,109,110,111,127,128,212,213,214,215,254,255):
        for measured in BYTE_VALUES:
            add('two-real-divider-byte-numerators-short-long-and-separate-local-reloads',raw_r5=0xB6D40000|source,byte_413e=measured)
    for incoming in (0,1,109,110,111,127,128,255):
        for held in (0,1,109,110,111,127,128,255):
            add('independent110-split-and-held-byte-agreement',raw_r6=0xC7E50000|incoming,byte_3fa4=held)
    for name,address,width in RAM_FIELDS:
        for value in (0,(1<<(8*width))-1):add('complete-prior-RAM-preimage',**{name:value})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a threshold-window input changes a complete raw coordinate,byte,word,register or SR width')


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
        raise ValueError('the threshold window reader caller withdrawal original changes complete raw RAM, CPU or complete threshold-window/divider/pool inputs')
