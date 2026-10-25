"""Input-only complete state flags, signed ratio operands, counters and two raw byte curves."""
from kb import test_contract
from kb import state_ratio_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('word_1000', 4096, 2),
 ('byte_106f', 4207, 1),
 ('byte_1071', 4209, 1),
 ('byte_1082', 4226, 1),
 ('byte_1083', 4227, 1),
 ('byte_108a', 4234, 1),
 ('byte_10e4', 4324, 1),
 ('word_13dc', 5084, 2),
 ('word_13de', 5086, 2),
 ('byte_1553', 5459, 1),
 ('byte_1704', 5892, 1),
 ('word_176a', 5994, 2),
 ('word_1770', 6000, 2),
 ('word_1772', 6002, 2),
 ('word_1774', 6004, 2),
 ('word_1866', 6246, 2),
 ('word_1868', 6248, 2),
 ('byte_1873', 6259, 1),
 ('byte_1a1e', 6686, 1),
 ('byte_1bee', 7150, 1),
 ('byte_1c5c', 7260, 1),
 ('byte_1c5e', 7262, 1),
 ('byte_2326', 8998, 1),
 ('word_240e', 9230, 2),
 ('byte_244f', 9295, 1),
 ('byte_2450', 9296, 1),
 ('byte_2453', 9299, 1),
 ('byte_2454', 9300, 1),
 ('byte_246a', 9322, 1),
 ('byte_246b', 9323, 1),
 ('byte_246d', 9325, 1),
 ('byte_247b', 9339, 1),
 ('byte_247c', 9340, 1),
 ('byte_2482', 9346, 1),
 ('byte_248b', 9355, 1),
 ('byte_24a3', 9379, 1),
 ('byte_24a7', 9383, 1),
 ('byte_25ee', 9710, 1),
 ('byte_2772', 10098, 1),
 ('byte_3373', 13171, 1),
 ('byte_418e', 16782, 1),
 ('byte_41fa', 16890, 1),
 ('byte_4250', 16976, 1),
 ('byte_558a', 21898, 1),
 ('dword_9818', 38936, 4))
CURVE_FIELDS=tuple(f'curve_{curve}_{index}' for curve in ('first','second') for index in range(8))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update({f'curve_{curve}_{index}':(20+index*24 if curve=='first' else 40+index*20) for curve in ('first','second') for index in range(8)})
DEFAULTS.update(config_870c=128,config_8710=0,config_8b38=0,config_8b3f=0,
    config_8ea6=500,config_906c=30,config_9456=50,
    byte_2482=1,byte_247c=1,byte_4250=0,byte_418e=32,byte_246a=1,word_240e=1000,
    byte_24a3=0x95,word_1866=1800,word_1868=2400,byte_1873=70,byte_3373=90,
    byte_1082=10,byte_108a=100,byte_1083=200,word_13dc=100,word_13de=300,
    word_176a=1200,word_1770=1000,word_1772=100,word_1774=800,
    config_8b34=0,config_8b42=0,config_86f9=0,config_851d=220,
    config_8d2d=200,config_8d2e=20,config_8616=0,
    byte_246b=64,byte_248b=2,byte_41fa=0,byte_1071=100,byte_1c5c=200,byte_1c5e=30,
    byte_24a7=0,byte_247b=2,byte_2326=40,byte_1553=180,byte_1a1e=1,byte_25ee=0,
    byte_106f=96,byte_2772=60,byte_1704=5,byte_558a=190,word_1000=600,byte_10e4=8,
    byte_1bee=0xA3,dword_9818=0x13579BDF,variant=7)
ENTRY_FIELDS={
    0x64CB2:('config_870c','config_8710','config_8b38','config_8b3f','config_8ea6','config_906c','config_9456',
        'byte_2482','byte_247c','byte_4250','byte_418e','byte_246a','word_240e',
        'word_1866','word_1868','byte_1873','byte_3373','byte_1082','byte_108a','byte_1083',
        'word_13dc','word_13de','word_176a','word_1770','word_1772','word_1774',
        'byte_246d','byte_2454','byte_2450','byte_2453','byte_244f'),
    0xBDC66:('config_8b34','config_8b42','config_86f9','config_851d','config_8d2d','config_8d2e','config_8616',
        'word_1000','byte_10e4','byte_558a','byte_246b','byte_248b','byte_41fa',
        'byte_1071','byte_1c5c','byte_1c5e','byte_24a7','byte_247b','byte_2326','byte_1553',
        'byte_1a1e','byte_25ee','byte_106f','byte_2772','byte_1704',*CURVE_FIELDS)}
WORDS=(0,1,2,3,4,7,8,15,16,31,32,63,64,100,119,120,121,127,128,255,256,511,512,1023,1024,32767,32768,65534,65535)
BYTES=(0,1,2,3,4,8,15,16,20,31,32,63,64,127,128,129,180,200,223,224,225,254,255)
DWORDS=(0,1,127,128,255,256,32767,32768,65535,0x7FFFFFFF,0x80000000,0xFFFFFFFF)


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    def values(field):return DWORDS if WIDTHS[field]==32 else WORDS if WIDTHS[field]==16 else BYTES
    for entry in contract.ENTRIES:
        for register in REGISTERS:
            for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
                add(entry,'complete-raw-register-width',**{register:value})
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):add(entry,'complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
        for variant in (0,7,255):add(entry,'complete-preserved-register-context',variant=variant)
        for name,address,width in RAM_FIELDS:
            for value in (0,(1<<(8*width))-1):add(entry,'complete-prior-RAM-preimage',**{name:value})
    primary=dict(config_870c=128)
    alternate=dict(config_870c=0,byte_246a=0,config_8b3f=20)
    ramp=dict(config_870c=0,byte_246a=1,byte_246d=1,config_8b3f=0)
    direct=dict(config_870c=0,byte_246d=0,byte_246a=1)
    profiles=(primary,dict(primary,byte_418e=0),alternate,ramp,direct,
        dict(direct,config_8b3f=16,config_8710=64),dict(alternate,config_8b3f=0))
    for profile in profiles:
        for field in ENTRY_FIELDS[0x64CB2]:
            for value in values(field):
                changed=dict(profile);changed[field]=value
                add(0x64CB2,'independent-active-ratio-state-flag-and-calibration-input',**changed)
    for divisor in (0,1,2,127,128,255,256,32767,32768,65534,65535):
        for bias in (0,1,32767,32768,65535):
            add(0x64CB2,'signed-word-divisor-sign-normalization-shift-wrap-and-ratio-clamps',word_240e=divisor,config_8ea6=bias)
    for first in (0,1,32):
        for second in (0,1,32):
            add(0x64CB2,'distinct-alternate-two-stage-flag-gates',**dict(alternate,byte_2454=first,byte_2450=second))
    for flag in (0,1,64,65,128,255):
        add(0x64CB2,'distinct-direct-state-pair-gates',**dict(alternate,byte_2453=flag,byte_244f=flag))
    for held in (0,1,200,32767,32768,65535):
        for baseline in (0,1,200,32767,32768,65535):
            add(0x64CB2,'unsigned-variable-positive-divisor-and-full-product',
                **dict(alternate,word_176a=held,word_1772=baseline,word_1770=65535,word_1774=65535,config_9456=0,word_1868=65535))
    main=dict(config_8b34=0,byte_246b=64)
    curve=dict(main,byte_24a7=2,byte_247b=2,byte_1a1e=1,byte_25ee=0)
    special=dict(config_8b34=16,config_8b42=2,byte_10e4=8)
    alt_source=dict(config_8b34=16,config_8b42=3)
    profiles=(main,curve,dict(curve,config_8616=1),dict(main,byte_41fa=1),special,alt_source,
        dict(alt_source,config_86f9=2),dict(main,byte_246b=0,byte_248b=2,byte_41fa=1),
        dict(curve,byte_25ee=1))
    for profile in profiles:
        for field in ENTRY_FIELDS[0xBDC66]:
            if field.startswith('curve_'):continue
            for value in values(field):
                changed=dict(profile);changed[field]=value
                add(0xBDC66,'independent-active-byte-state-interpolation-counter-and-offset-input',**changed)
    for coordinate in (0,1,19,20,21,100,199,200,201,254,255):
        for high,low in ((200,20),(20,200),(100,100),(255,0),(1,0)):
            for first,second in ((0,255),(255,0),(0,0),(255,255),(128,127)):
                add(0xBDC66,'raw-ordered-or-reversed-transition-and-signed-difference',
                    **dict(main,byte_1071=coordinate,config_8d2d=high,config_8d2e=low,byte_1c5c=first,byte_1c5e=second))
    for mode in (0,1):
        for index in range(8):
            for neighbor in (0,1):
                coordinate=min(255,index*32+neighbor)
                for cell in range(8):
                    for value in (0,1,127,128,254,255):
                        changed=dict(curve,config_8616=mode,byte_106f=coordinate,byte_2772=index*20)
                        changed[f'curve_{"first" if mode else "second"}_{cell}']=value
                        add(0xBDC66,'independent-every-physical-byte-and-neighbor-or-signed-endpoint',**changed)
        for coordinate in (0,1,31,32,63,64,127,128,191,192,223,224,225,254,255):
            add(0xBDC66,'exact-implicit-coordinate-boundaries-and-endpoint-promotion',
                **dict(curve,config_8616=mode,byte_106f=coordinate,byte_2772=coordinate))
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a state ratio input changes a complete raw RAM,curve,configuration,register or SR width')


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
        raise ValueError('the state ratio caller withdrawal original changes complete raw RAM, CPU or complete state ratio/byte curve/scalar/pool inputs')
