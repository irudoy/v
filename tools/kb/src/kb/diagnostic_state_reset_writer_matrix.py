"""Input-only complete reset preimages and separate multi-bank native snapshots."""
from kb import test_contract
from kb import diagnostic_state_reset_writer_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
NATIVE_IO=contract.NATIVE_BANKS
NATIVE_SIZE=sum(size for start,size in NATIVE_IO)
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(
    ('byte_2b96',0x2B96,1),('byte_4232',0x4232,1),('byte_2985',0x2985,1),
    ('byte_4198',0x4198,1),('byte_40be',0x40BE,1),('byte_41de',0x41DE,1),
    ('byte_41a4',0x41A4,1),('byte_4251',0x4251,1),('byte_41f2',0x41F2,1),
    ('byte_41fc',0x41FC,1),('byte_41fe',0x41FE,1),('byte_41b9',0x41B9,1),
    ('byte_41ba',0x41BA,1),('byte_41bb',0x41BB,1),('byte_41e1',0x41E1,1),('byte_41f5',0x41F5,1),
    ('word_3084',0x3084,2),('word_30b0',0x30B0,2),('byte_3086',0x3086,1),
    ('word_3088',0x3088,2),('word_308a',0x308A,2),('word_30ac',0x30AC,2),
    ('word_30f2',0x30F2,2),('byte_30ae',0x30AE,1),('byte_30f4',0x30F4,1),('long_30f8',0x30F8,4),
    ('native_9a6b',0x9A6B,1),('prior_99de',0x99DE,1),
    *((f'native_word_{address:04x}',address,2) for address in range(0xF588,0xF598,2)))
READ_BYTES=('byte_4232','byte_4198','byte_40be','byte_41de','byte_41a4','byte_4251',
    'byte_41f2','byte_41fc','byte_41fe','byte_41b9','byte_41ba','byte_41bb','byte_41e1','byte_41f5','native_9a6b')
WIDTHS={name:32 for name in REGISTERS}
WIDTHS.update({name:width*8 for name,at,width in RAM_FIELDS})
WIDTHS.update(pattern=8,native_pattern_84=8,native_pattern_99=8,native_pattern_f5=8,
    raw_rom_8dfc=8,raw_rom_8dfd=8,initial_sr=10,variant=8)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,
    (0x12345678,0x87654321,0x80000000,0xFFFFFFFF,0xABCD1234,0x80010000,0x10000,0x7FFFFFFF))})
DEFAULTS.update({name:int.from_bytes(bytes([0xA5])*width,'big') for name,at,width in RAM_FIELDS})
DEFAULTS.update(pattern=0xA5,native_pattern_84=0x5C,native_pattern_99=0x6D,native_pattern_f5=0xB7,
    raw_rom_8dfc=33,raw_rom_8dfd=20,variant=7)


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','index','kind'}
            or type(case['entry']) is not int or case['entry']!=contract.ENTRY
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('the reset inputs change complete typed raw CPU, byte/word/native preimages or the exact root')


def cases(source,image):
    rows=[]
    def add(kind,**changes):rows.append(dict(DEFAULTS,entry=contract.ENTRY,kind=kind,**changes))
    for gate in (0,64):
        for prior in range(256):add('constant-zero-target-with-held-other-inputs',prior_99de=prior,byte_41e1=gate)
    for name in READ_BYTES:
        for raw in range(256):add('complete-each-raw-read-byte',**{name:raw})
    for name in ('raw_rom_8dfc','raw_rom_8dfd'):
        for raw in range(256):add('conditional-native-word-physical-ROM-preimage',byte_41e1=64,**{name:raw})
    for name in ('pattern','native_pattern_84','native_pattern_99','native_pattern_f5'):
        for raw in range(256):add('complete-raw-array-and-unused-canary-preimages',**{name:raw})
    for name,at,width in RAM_FIELDS:
        if width>1:
            values=(0,1,127,128,255,256,32767,32768,65535) if width==2 else (
                0,1,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFF)
            for raw in values:add('complete-independent-word-and-long-preimages',byte_41e1=64,**{name:raw})
    for name in REGISTERS:
        for raw in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
            add('complete-entry-register-carriers',**{name:raw})
    for qm in (0,256,512,768):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-preserved-SR-context',initial_sr=qm|interrupt|t,byte_41e1=64)
    for variant in (0,1,127,128,254,255):add('complete-caller-callee-R14-GBR-MACL-frame',variant=variant,byte_41e1=64)
    return tuple(dict(case,index=index) for index,case in enumerate(rows))


def context(source,case):
    require_case(case)
    registers=[(0x28765430+i*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for i in range(15)]
    registers[:8]=[case[name] for name in REGISTERS]
    return (*registers,(0x456789AB+case['variant'])&0xFFFFFFFF,
        (0x13579BDF+case['variant'])&0xFFFFFFFF,(0x2468ACE0+case['variant'])&0xFFFFFFFF,
        case['initial_sr'],0xB6C70000)


def memory(case):
    require_case(case);raw=bytearray([case['pattern']])*RAM_SIZE
    for (start,size),name in zip(NATIVE_IO,('native_pattern_84','native_pattern_99','native_pattern_f5')):
        offset=start&65535;raw[offset:offset+size]=bytes([case[name]])*size
    for name,at,width in RAM_FIELDS:raw[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(raw)


def native_bytes(memory):
    if type(memory) is not bytes or len(memory)!=RAM_SIZE:
        raise ValueError('the reset native view requires the complete logical RAM image')
    return b''.join(memory[start&65535:(start&65535)+size] for start,size in NATIVE_IO)


def logical(ordinary,native):
    if type(ordinary) is not bytes or len(ordinary)!=RAM_SIZE or type(native) is not bytes or len(native)!=NATIVE_SIZE:
        raise ValueError('the reset logical view omits a complete separate ordinary or native snapshot')
    raw=bytearray(ordinary);offset=0
    for start,size in NATIVE_IO:
        at=start&65535;raw[at:at+size]=native[offset:offset+size];offset+=size
    return bytes(raw)


def physical_ordinary(logical_after,ordinary_before):
    if any(type(value) is not bytes or len(value)!=RAM_SIZE for value in (logical_after,ordinary_before)):
        raise ValueError('the reset physical ordinary view omits a complete image')
    raw=bytearray(logical_after)
    for start,size in NATIVE_IO:
        at=start&65535;raw[at:at+size]=ordinary_before[at:at+size]
    return bytes(raw)


def calibrations(source,image,case):
    fixture,_=contract.fixture_for_case(source,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}


def require_input(source,image,case,observed):
    raw=memory(case);cal=calibrations(source,image,case)
    if (not test_contract.exact(observed['entry'],contract.ENTRY)
            or not test_contract.exact(observed['context'],context(source,case))
            or observed['memory_before']!=(raw,) or observed['native_before']!=native_bytes(raw)
            or not test_contract.exact(observed['calibration_before'],cal)
            or not test_contract.exact(observed['calibration_after'],cal)):
        raise ValueError('the reset original changes complete independent CPU, RAM, native banks or physical inputs')
    for start,size in NATIVE_IO:
        at=start&65535
        if observed['memory_after'][0][at:at+size]!=raw[at:at+size]:
            raise ValueError('the reset original overwrites actual ordinary shadows with native publications')
    writable={address for permission in contract.PERMISSIONS if 'write' in permission['modes']
        for address in range(permission['start'],permission['end'])}
    offset=0
    for start,size in NATIVE_IO:
        for index in range(size):
            if start+index not in writable and observed['native_after'][offset+index]!=observed['native_before'][offset+index]:
                raise ValueError('the reset original changes a complete unused native-bank preservation canary')
        offset+=size


def header(declared,image):
    lines=['/* Complete raw reset inputs and native-bank preimages; no expected outputs. */',
        '#define RESET_CALIBRATION_SIZE '+str(sum(row['size'] for row in contract.CONTROLLED_CALIBRATION))+'U',
        '#define RESET_BOUND_SIZE '+str(sum(row['size'] for row in contract.BOUND_SPANS))+'U',
        '#define RESET_NATIVE_SIZE '+str(NATIVE_SIZE)+'U']
    for name,spans in (('ram_fields',[dict(address=at,size=width) for field,at,width in RAM_FIELDS]),
            ('calibration',contract.CONTROLLED_CALIBRATION),('bound',contract.BOUND_SPANS),
            ('native',[dict(address=start,size=size) for start,size in NATIVE_IO])):
        lines.append('static const struct span reset_'+name+'[] = {'+
            ','.join('{'+f'0x{row["address"]:x}U,{row["size"]}U'+'}' for row in spans)+'};')
    lines.extend(('struct path_case { uint8_t pattern,native_fills[3]; uint32_t ram['+str(len(RAM_FIELDS))+'];',
        '    struct context context; uint8_t calibration[RESET_CALIBRATION_SIZE]; };',
        'static const struct path_case reset_cases[] = {'))
    for case in declared['cases']:
        require_case(case);registers=context(declared['source'],case);cal=calibrations(declared['source'],image,case)
        raw=b''.join(cal[row['address']] for row in contract.CONTROLLED_CALIBRATION)
        ram=','.join(f'0x{case[name]:x}U' for name,at,width in RAM_FIELDS)
        core=','.join(f'0x{value:x}U' for value in registers[:15]);tail=','.join(f'0x{value:x}U' for value in registers[15:])
        fills=','.join(f'0x{case[name]:x}U' for name in ('native_pattern_84','native_pattern_99','native_pattern_f5'))
        lines.append('    {'+f'0x{case["pattern"]:x}U,'+'{'+fills+'},{'+ram+'},{{'+core+'},'+tail+'},{'+
            ','.join(f'0x{value:02x}U' for value in raw)+'}},')
    return '\n'.join((*lines,'};','')).encode()
