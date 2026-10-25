"""Input-only complete DFCO state flags,counters,raw frame carriers and indexed bytes."""
from kb import test_contract
from kb import dfco_state_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
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
 ('byte_4250', 16976, 1))
STATE_FIELDS=tuple(f'state_byte_{index:03d}' for index in range(256))
DELAY_FIELDS=tuple(f'delay_byte_{address:05x}' for address in range(0x1269A,0x126A0))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
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
    for name,address,width in RAM_FIELDS:
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
