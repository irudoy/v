"""Input-only complete paired flag and physical read/modify/write preimages."""
from kb import test_contract
from kb import paired_inhibit_writer_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('byte_3118', 12568, 1),
 ('byte_41bb', 16827, 1),
 ('byte_41c1', 16833, 1),
 ('byte_41c5', 16837, 1),
 ('byte_41cf', 16847, 1),
 ('byte_41d4', 16852, 1),
 ('byte_41d8', 16856, 1),
 ('byte_48c2', 18626, 1),
 ('byte_48c4', 18628, 1),
 ('byte_4a45', 19013, 1),
 ('byte_4a47', 19015, 1),
 ('word_4a70', 19056, 2),
 ('word_4a74', 19060, 2),
 ('byte_4ac6', 19142, 1),
 ('byte_4ac8', 19144, 1),
 ('byte_5737', 22327, 1),
 ('byte_5738', 22328, 1),
 ('byte_573a', 22330, 1),
 ('byte_573b', 22331, 1),
 ('byte_573d', 22333, 1),
 ('byte_573e', 22334, 1),
 ('byte_5740', 22336, 1),
 ('byte_5741', 22337, 1),
 ('byte_5743', 22339, 1),
 ('byte_5744', 22340, 1),
 ('byte_5746', 22342, 1),
 ('byte_5747', 22343, 1),
 ('byte_5749', 22345, 1),
 ('byte_574a', 22346, 1),
 ('byte_5b2a', 23338, 1),
 ('byte_5b2b', 23339, 1),
 ('byte_5b2c', 23340, 1),
 ('byte_5b33', 23347, 1))
OR_FIELDS=tuple(f'byte_{0x5718+offset:04x}' for offset in (0x1F,0x22,0x25,0x28,0x2B,0x2E,0x31))
AND_FIELDS=tuple(f'byte_{0x5718+offset:04x}' for offset in (0x20,0x23,0x26,0x29,0x2C,0x2F,0x32))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update({name:0xA1 for name in OR_FIELDS});DEFAULTS.update({name:0xE3 for name in AND_FIELDS})
DEFAULTS.update(byte_3118=1,config_885d=4,byte_41bb=0,byte_41c1=255,byte_41c5=32,
    byte_41cf=0,byte_41d4=255,byte_41d8=32,byte_48c2=0xA5,byte_48c4=0xC3,
    byte_4a45=0xA5,byte_4a47=0xC3,word_4a70=0xA5C3,word_4a74=0xC3A5,byte_4ac6=0xA5,byte_4ac8=0xC3,
    byte_5b2a=255,byte_5b2b=255,byte_5b2c=0,byte_5b33=42,variant=7)
ENTRY_FIELDS={0x7C8FA:('byte_41c5','byte_41cf','byte_5b2c','byte_5b33'),
    0x7C9A8:('byte_41d8','byte_41bb','byte_3118','config_885d','byte_5b2c','byte_5b33')}
BYTES=(0,1,2,3,4,7,8,15,16,31,32,63,64,127,128,129,254,255)
WORDS=(0,1,255,256,32767,32768,65534,65535)


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for entry in contract.ENTRIES:
        for register in REGISTERS:
            for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
                add(entry,'complete-raw-register-width',**{register:value})
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):add(entry,'complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
        for variant in (0,7,255):add(entry,'complete-preserved-register-context',variant=variant)
        for name,address,width in RAM_FIELDS:
            for value in (0,(1<<(8*width))-1):add(entry,'complete-prior-RAM-and-RMW-preimage',**{name:value})
        for field in ENTRY_FIELDS[entry]:
            for value in BYTES:add(entry,'independent-active-flag-threshold-and-helper-input',**{field:value})
        for flag in BYTES:
            for blocker in (0,8,255):
                add(entry,'independent-helper-low-nibble-and-blocker-branches',byte_5b33=flag,byte_5b2c=blocker)
        for field in (*OR_FIELDS,*AND_FIELDS,'byte_41d4','byte_5b2a','byte_5b2b','byte_41c1'):
            for value in BYTES:add(entry,'every-physical-RMW-before-byte-and-preserved-unmasked-bit',**{field:value})
    for coordinate in BYTES:
        for threshold in BYTES:
            add(0x7C9A8,'raw-sign-extended-byte-unsigned-threshold-comparison',byte_3118=coordinate,config_885d=threshold)
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a paired flag input changes a complete raw RAM,RMW,threshold,register or SR width')


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
        raise ValueError('the paired flag writer caller withdrawal original changes complete raw RAM, CPU or complete paired flag/RMW/threshold/pool inputs')
