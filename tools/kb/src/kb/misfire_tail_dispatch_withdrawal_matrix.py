"""Input-only complete natural hysteresis, counters and real tail dispatch."""
from kb import test_contract
from kb import misfire_tail_dispatch_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('byte_11b2', 4530, 1),
 ('byte_24c4', 9412, 1),
 ('byte_3834', 14388, 1),
 ('byte_4096', 16534, 1),
 ('word_409e', 16542, 2),
 ('word_40a0', 16544, 2),
 ('word_40a2', 16546, 2),
 ('byte_41d2', 16850, 1),
 ('byte_4241', 16961, 1),
 ('byte_4251', 16977, 1),
 ('byte_444c', 17484, 1),
 ('byte_444d', 17485, 1))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update(byte_11b2=31,byte_24c4=128,byte_4096=7,
    word_409e=199,word_40a0=999,word_40a2=199,byte_4241=0,byte_4251=128,
    byte_41d2=3,byte_3834=31,byte_444d=0,byte_444c=0,
    config_8bda=32,config_186ce=128,config_8354=1,config_8656=1,variant=7)
# The flag preimage has a full preservation obligation. Its retained bits
# receive no numerical-causality credit. The byte counter has an explicitly
# transformed same-address publication obligation, never input-echo credit.
ENTRY_FIELDS={0x7C494:(*[name for name,address,width in RAM_FIELDS if name!='byte_4241'],
    *[row['field'] for row in contract.CONFIGURATION])}
BYTE_VALUES=(0,1,2,3,4,7,8,15,16,30,31,32,33,63,64,65,126,127,128,129,251,252,253,254,255)
WORD_VALUES=(0,1,2,199,200,201,999,1000,1001,32767,32768,50999,51000,51001,65534,65535)


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=0x7C494,kind=kind,**changes))
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):add('complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-context',variant=variant)
    for field,address,width in RAM_FIELDS:
        for raw in WORD_VALUES if width==2 else BYTE_VALUES:
            profile=dict(byte_11b2=255) if field=='byte_4096' else {}
            if field=='word_409e':profile['word_40a0']=1000
            elif field in ('word_40a0','word_40a2'):profile['word_409e']=200
            elif field=='byte_444d':profile.update(word_409e=200,word_40a0=1000)
            elif field=='byte_444c':profile['word_40a2']=200
            add('complete-independent-RAM-control-operand-or-prior-state',**dict(profile,**{field:raw}))
    for row in contract.CONFIGURATION:
        for raw in range(256):add('each-complete-raw-configuration-byte',**{row['field']:raw})
    for previous in (0,1,127,128,129,255):
        for coordinate in (0,1,27,28,29,30,31,32,33,251,252,253,254,255):
            for threshold in (0,1,31,32,33,254,255):
                add('independent-hysteresis-promotion-and-comparison',byte_24c4=previous,byte_11b2=coordinate,config_8bda=threshold)
    for count in BYTE_VALUES:
        add('actual-byte-counter-increment-or-saturated-signed-return',byte_11b2=255,byte_4096=count)
        add('actual-byte-counter-reset-path',byte_11b2=0,byte_24c4=0,byte_4096=count)
    for prior in (0,128,255):
        for coordinate in (0,255):
            for count in (0,254,255):
                for mode in (0,127,128,255):
                    add('actual-tail-disabled-or-enabled-complete-callee-return',byte_24c4=prior,
                        byte_11b2=coordinate,byte_4096=count,config_186ce=mode)
    for factor in (0,1,2,127,128,254,255):
        for field,configuration in (('word_409e','config_8354'),('word_40a2','config_8656')):
            for count in (max(0,200*factor-1),200*factor,min(65535,200*factor+1),32767,32768,65535):
                add('complete-word-threshold-product-and-signed-local-preimage',**{field:count,configuration:factor})
    for first,second,third in ((199,999,199),(200,1000,200),(201,1001,201),(65535,65535,65535),(0,0,0)):
        for flags in (0,1,31,32,64,128,224,255):
            add('three-distinct-threshold-flags-and-ordered-word-updates',word_409e=first,word_40a0=second,word_40a2=third,byte_4241=flags)
    for speed in (0,1,30,31,32,127,128,129,254,255):
        for first_stop in (0,1,128,255):
            for third_stop in (0,1,128,255):
                add('sign-extended-byte-before-unsigned-speed-and-independent-stops',byte_3834=speed,byte_444d=first_stop,byte_444c=third_stop)
    for modes in (0,1,127,128,129,255):
        for prerequisites in (0,1,2,3,127,128,255):
            add('complete-mode-prerequisite-reset-chain',byte_4251=modes,byte_41d2=prerequisites)
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a misfire tail input changes a complete raw register, byte, word, configuration or SR width')


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
        raise ValueError('the misfire tail dispatch withdrawal original changes complete raw RAM, CPU or complete raw hysteresis/byte-counter/word-counter/flag/tail/frame/pool inputs')
