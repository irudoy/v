"""Input-only complete raw unsigned products,variable division and signed fallback."""
from kb import test_contract
from kb import byte_ratio_producer_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('word_11bc', 4540, 2),
 ('word_14dc', 5340, 2),
 ('word_1630', 5680, 2),
 ('byte_17b8', 6072, 1),
 ('byte_23f1', 9201, 1),
 ('dword_9818', 38936, 4))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update(byte_17b8=1,word_14dc=256,word_1630=1,word_11bc=1024,byte_23f1=0xA5,
    config_884d=1,config_8b6c=6,dword_9818=0xA5C3D2E1,variant=7)
ENTRY_FIELDS={0x4AE6C:('byte_17b8','word_14dc','word_1630','word_11bc','config_884d','config_8b6c')}
BYTE_VALUES=(0,1,2,3,4,5,6,7,8,15,16,20,31,32,63,64,127,128,129,141,142,254,255)
WORD_VALUES=(0,1,2,3,4,5,6,7,8,15,16,127,128,255,256,257,546,1023,1024,1025,
    8192,8738,32767,32768,32769,65527,65528,65529,65530,65531,65532,65533,65534,65535)


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=0x4AE6C,kind=kind,**changes))
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
            add('complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-context',variant=variant)
    for profile in ({},dict(byte_17b8=0,config_8b6c=1,word_11bc=1),dict(byte_17b8=1,word_14dc=1,word_1630=1)):
        for field in ENTRY_FIELDS[0x4AE6C]:
            for value in (WORD_VALUES if WIDTHS[field]==16 else BYTE_VALUES):
                add('independent-unsigned-byte-word-product-ratio-or-offset-input',**dict(profile,**{field:value}))
    for byte in (0,1,2,127,128,255):
        for word in (0,1,255,256,257,32767,32768,65535):
            for numerator_word in (0,1,32768,65535):
                add('full-variable-divisor-short-long-and-word-large-boundaries',byte_17b8=byte,
                    word_14dc=word,word_1630=numerator_word,config_884d=255)
    for zero_byte,zero_word in ((0,0),(0,65535),(255,0)):
        for offset in (0,1,2,6,7,255):
            add('zero-product-sentinel-and-ratio-offset65536-boundary',byte_17b8=zero_byte,
                word_14dc=zero_word,config_8b6c=offset,word_11bc=1)
    add('exact-65535-ratio-boundary',byte_17b8=1,word_14dc=16,word_1630=8738,config_884d=1,config_8b6c=0)
    add('exact-65536-ratio-boundary',byte_17b8=1,word_14dc=15,word_1630=8192,config_884d=1,config_8b6c=0)
    for word in WORD_VALUES:
        add('full-signed-shift-and-three-times-fallback-ratio',byte_17b8=0,config_8b6c=1,word_11bc=word)
        for offset in (0,1,2,5,6,7,31,63,127,255):
            add('low-ratio-unsigned-product-shift-and-final-byte-underflow-or-cap',
                word_1630=0,word_11bc=word,config_8b6c=offset)
    for name,address,width in RAM_FIELDS:
        for value in (0,(1<<(8*width))-1):add('complete-prior-RAM-preimage',**{name:value})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a byte ratio input changes a complete raw byte,word,dword,register,configuration or SR width')


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
        raise ValueError('the byte ratio producer withdrawal original changes complete raw RAM, CPU or complete unsigned-product/ratio/signed-shift/divider/pool inputs')
