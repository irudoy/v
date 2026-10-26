"""Input-only complete DFCO state flags,counters,raw frame carriers and indexed bytes."""
from kb import test_contract
from kb import dfco_state_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
STATE_RAM_FIELDS=(('byte_106a', 4202, 1),
 ('byte_110e', 4366, 1),
 ('byte_11b3', 4531, 1),
 ('word_11b6', 4534, 2),
 ('byte_14c1', 5313, 1),
 ('byte_14c4', 5316, 1),
 ('byte_1517', 5399, 1),
 ('byte_153c', 5436, 1),
 ('byte_17bd', 6077, 1),
 ('byte_1936', 6454, 1),
 ('byte_1937', 6455, 1),
 ('byte_1938', 6456, 1),
 ('byte_1939', 6457, 1),
 ('byte_193a', 6458, 1),
 ('byte_2458', 9304, 1),
 ('byte_2468', 9320, 1),
 ('byte_248f', 9359, 1),
 ('byte_249f', 9375, 1),
 ('byte_24cf', 9423, 1),
 ('byte_251b', 9499, 1),
 ('byte_2571', 9585, 1),
 ('byte_2572', 9586, 1),
 ('byte_2573', 9587, 1),
 ('byte_259c', 9628, 1),
 ('byte_4250', 16976, 1))
RAM_FIELDS=(('byte_106a', 4202, 1),
 ('byte_110e', 4366, 1),
 ('byte_11b3', 4531, 1),
 ('word_11b6', 4534, 2),
 ('byte_14c1', 5313, 1),
 ('byte_14c4', 5316, 1),
 ('byte_1517', 5399, 1),
 ('byte_153c', 5436, 1),
 ('byte_17bd', 6077, 1),
 ('byte_1936', 6454, 1),
 ('byte_1937', 6455, 1),
 ('byte_1938', 6456, 1),
 ('byte_1939', 6457, 1),
 ('byte_193a', 6458, 1),
 ('byte_2458', 9304, 1),
 ('byte_2468', 9320, 1),
 ('byte_248f', 9359, 1),
 ('byte_249f', 9375, 1),
 ('byte_24cf', 9423, 1),
 ('byte_251b', 9499, 1),
 ('byte_2571', 9585, 1),
 ('byte_2572', 9586, 1),
 ('byte_2573', 9587, 1),
 ('byte_259c', 9628, 1),
 ('byte_4250', 16976, 1),
 ('byte_106f', 4207, 1),
 ('byte_1083', 4227, 1),
 ('byte_14ec', 5356, 1),
 ('byte_16aa', 5802, 1),
 ('byte_1778', 6008, 1),
 ('byte_2450', 9296, 1),
 ('byte_245d', 9309, 1),
 ('byte_249d', 9373, 1),
 ('byte_2978', 10616, 1),
 ('byte_41d0', 16848, 1),
 ('byte_41d1', 16849, 1),
 ('byte_48e1', 18657, 1),
 ('byte_5a95', 23189, 1),
 ('byte_5a98', 23192, 1))
STATE_FIELDS=tuple(f'state_byte_{index:03d}' for index in range(256))
DELAY_FIELDS=tuple(f'delay_byte_{address:05x}' for address in range(0x1269A,0x126A0))
WIDTHS={name:width*8 for name,address,width in STATE_RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.STATE_CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
STATE_WIDTHS=dict(WIDTHS)
WIDTHS.update({name:width*8 for name,address,width in RAM_FIELDS if name not in WIDTHS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION if row['field'] not in WIDTHS})
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,0,1,0x01020304,8))})
DEFAULTS.update({name:(index*17+3)&255 for index,name in enumerate(STATE_FIELDS)})
DEFAULTS.update({name:5+index*3 for index,name in enumerate(DELAY_FIELDS)})
DEFAULTS.update(byte_106a=20,byte_110e=20,byte_11b3=30,word_11b6=150,
    byte_14c1=3,byte_14c4=0xA5,byte_1517=10,byte_153c=255,byte_17bd=255,
    byte_1936=1,byte_1937=2,byte_1938=3,byte_1939=0xA5,byte_193a=255,
    byte_2458=0,byte_2468=0,byte_248f=0xA5,byte_249f=0,byte_24cf=16,byte_251b=0xA5,
    byte_2571=1,byte_2572=1,byte_2573=1,byte_259c=0,byte_4250=0,
    config_85f6=20,config_8711=2,config_8a40=10,config_8b3f=0,
    config_8c1a=20,config_8c1b=5,config_8c1c=5,config_8c1d=10,config_8c1e=200,variant=7)

STATE_DEFAULTS={name:DEFAULTS[name] for name in STATE_WIDTHS}
DEFAULTS.update({'byte_106f': 165,
 'byte_1083': 165,
 'byte_14ec': 165,
 'byte_16aa': 165,
 'byte_1778': 165,
 'byte_2450': 165,
 'byte_245d': 165,
 'byte_249d': 165,
 'byte_2978': 165,
 'byte_41d0': 165,
 'byte_41d1': 165,
 'byte_48e1': 165,
 'byte_5a95': 165,
 'byte_5a98': 165,
 'config_84e8': 24,
 'config_85fa': 4,
 'config_85fc': 10,
 'config_870c': 68,
 'config_8a2f': 120,
 'config_8a3a': 42,
 'config_8a3b': 72,
 'config_8a3c': 100,
 'config_8a3d': 100,
 'config_8a3e': 64,
 'config_8a3f': 48})
DEFAULTS.update({name:0xA5 for name in ('restore_byte_12818', 'restore_byte_12819', 'restore_byte_1281a', 'restore_byte_1281b', 'restore_byte_1281c', 'restore_byte_1281d', 'restore_byte_1281e', 'restore_byte_1281f', 'restore_byte_12820', 'restore_byte_12821', 'restore_byte_12822', 'restore_byte_12823', 'restore_byte_12824', 'restore_byte_12825', 'restore_byte_12826', 'restore_byte_12827', 'restore_byte_1298c', 'restore_byte_1298d', 'restore_byte_1298e', 'restore_byte_1298f', 'restore_byte_12990', 'restore_byte_12991', 'restore_byte_12992', 'restore_byte_12993', 'restore_byte_12994', 'restore_byte_12995', 'restore_byte_12996', 'restore_byte_12997', 'restore_byte_12998', 'restore_byte_12999', 'restore_byte_1299a', 'restore_byte_1299b', 'restore_byte_11cb5', 'restore_byte_11cb6', 'restore_byte_11cb7', 'restore_byte_11cb8', 'restore_byte_1299c', 'restore_byte_1299d', 'restore_byte_1299e', 'restore_byte_1299f')})

ENTRY_FIELDS={0x503E0:('raw_r4','raw_r5','raw_r6','raw_r7','byte_106a','byte_110e','byte_11b3','word_11b6',
    'byte_14c1','byte_1517','byte_1936','byte_1937','byte_1938','byte_193a','byte_2458','byte_2468',
    'byte_249f','byte_24cf','byte_2571','byte_2572','byte_2573','byte_259c','byte_4250',
    'config_85f6','config_8711','config_8a40','config_8b3f','config_8c1a','config_8c1b',
    'config_8c1c','config_8c1d','config_8c1e',*DELAY_FIELDS,*STATE_FIELDS)}
WORDS=(0,1,2,3,4,7,8,15,16,31,32,63,64,100,119,120,121,127,128,255,256,511,512,1023,1024,32767,32768,65534,65535)
BYTES=(0,1,2,3,4,5,6,7,8,10,15,16,20,31,32,63,64,127,128,129,200,254,255)
DWORDS=(0,1,2,3,4,6,7,255,256,0x00000100,0x00010000,0x01000000,0x80000000,0xFFFFFFFF)


def cases(declared,image):
    inputs=[];entry=0x503E0
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    def values(field):return DWORDS if WIDTHS[field]==32 else WORDS if WIDTHS[field]==16 else BYTES
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
            add('complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-context',variant=variant)
    for name,address,width in STATE_RAM_FIELDS:
        for value in (0,(1<<(8*width))-1):add('complete-prior-RAM-preimage',**{name:value})
    hold=dict(raw_r4=0,raw_r5=0,byte_193a=255)
    zero_table={name:0 for name in STATE_FIELDS}
    profiles=(dict(),dict(config_8b3f=128),dict(config_8711=0),
        dict(hold,byte_14c1=0,byte_193a=1),dict(hold,byte_14c1=1),
        dict(hold,byte_14c1=2),dict(hold,byte_14c1=4),
        dict(byte_14c1=4,byte_2458=32),
        dict(hold,byte_14c1=0,byte_1937=0,byte_249f=32,**zero_table),
        dict(config_8b3f=0,byte_1517=0),dict(config_8b3f=0,byte_1517=255))
    scalar_fields=tuple(name for name in ENTRY_FIELDS[entry] if name not in STATE_FIELDS)
    for profile in profiles:
        for field in scalar_fields:
            for value in values(field):
                changed=dict(profile);changed[field]=value
                add('independent-active-state-counter-threshold-frame-and-flag-input',**changed)
    for state in range(256):
        profile=dict(hold,byte_14c1=state,byte_1937=0,byte_2571=1,byte_2572=1,byte_2573=1)
        add('every-raw-unsigned-state-byte-and-complete-indexed-preimage',**profile)
        for value in (0,1,127,128,254,255):
            add('independent-each-physical-indexed-state-byte',**dict(profile,**{STATE_FIELDS[state]:value}))
    for mask in BYTES:
        for count in (0,1,2,3,4,5,6,7,127,128,255):
            add('real-rotation-loop-mask-unsigned-count-and-six-call-bound',**dict(hold,byte_14c1=0,byte_1936=mask,byte_1937=count))
    for state in (0,1,2,3,4,5,127,128,255):
        for first in (0,1,2,255):
            for second in (0,1,2,255):
                add('raw-state-and-independent-three-stage-counter-expiry',**dict(hold,byte_14c1=state,
                    byte_2571=first,byte_2572=second,byte_2573=first))
    for raw in (0,1,0x01000000,0x00010000,0x00000100,0x00000001,0x12345678,0x80000000,0xFFFFFFFF):
        for state in (0,1):
            add('full-R6-word-write-overwritten-by-real-local-dword-before-byte-reloads',
                raw_r4=1,raw_r5=0,raw_r6=raw,byte_14c1=state,byte_2571=0,byte_2572=0)
    for profile in (dict(byte_2468=64),dict(),dict(byte_11b3=255)):
        for prior in range(256):
            add('unread1939-prior-and-retained-writes',**dict(profile,byte_1939=prior))
    inputs.extend(restore_cases(declared,image))
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a DFCO state input changes a complete raw table,delay,RAM,configuration,register or SR width')


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
        raise ValueError('the DFCO state caller withdrawal original changes complete raw RAM, CPU or complete DFCO state/delay/table/scalar/pool inputs')


RESTORE_RAM_FIELDS=tuple((f'byte_{at:04x}',at,1) for at in
    (0x106A,0x106F,0x1083,0x110E,0x11B3,0x14EC,0x16AA,0x1778,0x2450,0x2458,0x245D,
     0x2468,0x249D,0x24CF,0x2978,0x41D0,0x41D1,0x4250,0x48E1,0x5A95,0x5A98))
RESTORE_CURVE_FIELDS={address:tuple(f'restore_byte_{address+index:05x}' for index in range(16))
    for address in (0x12818,0x1298C)}
RESTORE_SPEED_FIELDS=tuple(f'restore_byte_{0x11CB5+index:05x}' for index in range(4))
RESTORE_FLOOR_FIELDS=tuple(f'restore_byte_{0x1299C+index:05x}' for index in range(4))
RESTORE_DEFAULTS=dict(DEFAULTS,byte_106a=20,byte_106f=80,byte_1083=2,byte_110e=20,byte_11b3=60,
    byte_14ec=0xA5,byte_16aa=0xA5,byte_1778=0xA5,byte_2450=0,byte_2458=32,byte_245d=0,
    byte_2468=0,byte_249d=0,byte_24cf=16,byte_2978=0,byte_41d0=0,byte_41d1=0,
    byte_4250=0,byte_48e1=0,byte_5a95=0,byte_5a98=0,config_870c=0,config_8b3f=0)
for address,start in ((0x12818,48),(0x1298C,32)):
    RESTORE_DEFAULTS.update({name:start+8*index for index,name in enumerate(RESTORE_CURVE_FIELDS[address])})
RESTORE_DEFAULTS.update(zip(RESTORE_SPEED_FIELDS,(4,8,12,32)))
RESTORE_DEFAULTS.update(zip(RESTORE_FLOOR_FIELDS,(36,48,54,62)))
RESTORE_PRIOR_PROFILES=(dict(byte_5a95=32),dict(byte_5a98=32),dict(),dict(byte_4250=128))


def restore_cases(declared,image):
    """Raw independent knobs and held-other domains; no expected value or path selects a case."""
    inputs=[]
    def add(kind,**changes):inputs.append(dict(RESTORE_DEFAULTS,entry=0x50018,kind=kind,**changes))
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
            add('restore-complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('restore-complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('restore-complete-preserved-register-context',variant=variant)
    for name,address,width in RAM_FIELDS:
        for value in (0,255 if width==1 else 65535):add('restore-complete-prior-RAM-preimage',**{name:value})
    gates=(dict(),dict(byte_5a95=32),dict(byte_4250=64),dict(byte_5a98=32),dict(byte_41d1=128),
        dict(byte_41d1=4),dict(byte_41d0=1),dict(byte_41d1=1),dict(byte_48e1=1),dict(byte_245d=2))
    for gate in gates:
        add('restore-each-independent-lookup-or-fallback-gate',**gate)
    profiles=(dict(),dict(byte_2468=64),dict(byte_2458=0),dict(byte_2458=160),dict(byte_24cf=0),
        dict(byte_4250=128),dict(config_870c=128),dict(config_8b3f=128),dict(byte_1083=0),
        dict(byte_2458=160,byte_1083=0),dict(config_870c=128,config_8b3f=128))
    scalar_fields=tuple(name for name,at,width in RESTORE_RAM_FIELDS if name not in ('byte_14ec','byte_16aa','byte_1778'))
    scalar_fields+=tuple(row['field'] for row in contract.CONFIGURATION if row['field'].startswith('config_')
        and row['address'] in (0x84E8,0x85FA,0x85FC,0x870C,0x8A2F,0x8A3A,0x8A3B,0x8A3E,0x8A3F,0x8B3F))
    for profile in profiles:
        for field in scalar_fields:
            for value in (0,1,2,31,32,63,64,127,128,254,255):
                add('restore-independent-state-threshold-and-flag-input',**dict(profile,**{field:value}))
    for style in ('rising','falling','alternating'):
        fields={name:(32+8*index if style=='rising' else 224-8*index if style=='falling' else 0 if index&1 else 255)
            for names in RESTORE_CURVE_FIELDS.values() for index,name in enumerate(names)}
        for coordinate in range(256):
            add('restore-complete-coordinate-and-curve-direction',byte_106f=coordinate,**fields)
    for address,fields in RESTORE_CURVE_FIELDS.items():
        for index,field in enumerate(fields):
            for value in (0,1,127,128,254,255):
                add('restore-each-independent-physical-curve-byte',byte_106f=min(255,index*16+8),**{field:value})
    for field in RESTORE_SPEED_FIELDS:
        for value in (0,1,31,32,127,128,254,255):
            floors=dict(zip(RESTORE_FLOOR_FIELDS,(40,80,120,160)))
            zero_curves={name:0 for fields in RESTORE_CURVE_FIELDS.values() for name in fields}
            add('restore-each-independent-speed-threshold-byte',**dict(zero_curves,**floors,**{field:value}))
    for index,field in enumerate(RESTORE_FLOOR_FIELDS):
        for value in (0,1,31,32,127,128,254,255):
            add('restore-each-independent-speed-floor-byte',byte_106a=(0,4,8,12)[index],**{field:value})
    for offset in range(256):
        add('restore-complete-offset-saturation-boundaries',byte_4250=128,config_84e8=offset)
    zero_curves={name:0 for fields in RESTORE_CURVE_FIELDS.values() for name in fields}
    zero_floors={name:0 for name in RESTORE_FLOOR_FIELDS}
    split_curves={name:(120 if address==0x1298C else 60) for address,fields in RESTORE_CURVE_FIELDS.items() for name in fields}
    tail_profiles=(dict(byte_110e=0,**split_curves),dict(config_870c=128,config_8b3f=128,**split_curves),
        dict(config_8b3f=128,**split_curves),dict(config_8b3f=128,byte_2450=64),
        dict(byte_2458=160,byte_24cf=0),dict(byte_2458=160,config_870c=128),
        dict(byte_2458=160,byte_2978=128),dict(byte_2458=160,config_85fc=128))
    for profile in tail_profiles:
        for rpm in (0,1,31,32,42,43,60,62,63,64,72,73,88,89,120,121,127,128,254,255):
            add('restore-complete-classifier-threshold-and-mode-boundaries',**dict(profile,byte_11b3=rpm))
    for coordinate in range(256):
        add('restore-complete-speed-index-output-alternatives',**dict(zero_curves,
            **dict(zip(RESTORE_FLOOR_FIELDS,(40,80,120,160))),byte_106a=coordinate))
    for profile in RESTORE_PRIOR_PROFILES:
        for prior in range(256):
            add('restore-unread16aa-prior-and-retained-writer',**dict(profile,byte_16aa=prior))
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


ENTRY_FIELDS[0x50018]=('byte_106a','byte_106f','byte_5a95','byte_5a98','byte_4250',
    'config_84e8','config_8a3e','config_8a3f',*RESTORE_SPEED_FIELDS[:3],*RESTORE_FLOOR_FIELDS,
    *(name for fields in RESTORE_CURVE_FIELDS.values() for name in fields))
