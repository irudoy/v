"""Input-only complete timer/state preimages and separate native85 observation boundary."""
from kb import test_contract
from kb import indexed_timer_refresh_writer_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
NATIVE_START=0xFFFF8500
NATIVE_SIZE=256
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('judged',0x3581,1),('other_arm',0x4178,1),('arm',0x4179,1),
    ('native_reset',0x850C,1),('native_indicator',0x850D,1),('timer_wrapped',0x43B7,1),
    *((f'timer_{index:03d}',0x43B8+index,1) for index in range(256)))
WIDTHS={name:32 for name in REGISTERS};WIDTHS.update({name:8 for name,at,width in RAM_FIELDS})
WIDTHS.update(reload=8,initial_sr=10,variant=8)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,
    (0x12345678,0x87654321,0x80000000,0xFFFFFFFF,6,1,0x10000,0x7FFFFFFF))})
DEFAULTS.update({name:37 for name,at,width in RAM_FIELDS if name.startswith('timer_')})
DEFAULTS.update(judged=0,arm=0xA0,other_arm=0xA0,native_reset=0,native_indicator=0,reload=100,variant=7)


def timer_field(index):return 'timer_wrapped' if index==0xFFFFFFFF else f'timer_{index:03d}'


def cases(declared,image):
    rows=[]
    def add(kind,**changes):rows.append(dict(DEFAULTS,entry=contract.ENTRY,kind=kind,**changes))
    for index in contract.INDICES:
        for enable in (0,1):
            for indicator in (0,16,48):
                for timer in (0,37):
                    add('complete-explicit-index-and-enable-paths',raw_r4=index,raw_r5=enable,native_indicator=indicator,
                        **{timer_field(index):timer})
    for judged in (0,7):
        for enable in (0,1):
            for arm in (0,7):
                for other in (0,7):
                    for indicator in (0,16,32,48,255):
                        for timer in (0,1,37,255):
                            add('independent-judged-arm-native-indicator-and-expiry-gates',judged=judged,raw_r5=enable,
                                arm=arm,other_arm=other,native_indicator=indicator,timer_006=timer)
    for name in ('judged','arm','other_arm','native_reset','native_indicator'):
        for raw in range(256):add('complete-each-raw-control-byte',**{name:raw,'timer_006':0})
    for raw in range(256):add('exact-owner-positive-reload-byte',raw_r5=0,reload=raw)
    for index in contract.INDICES:
        for raw in (0,1,127,128,255):
            add('complete-indexed-timer-preimages',raw_r4=index,native_indicator=48,**{timer_field(index):raw})
    for raw in range(256):add('complete-exact-owner-timer-byte',native_indicator=48,timer_006=raw)
    for register in REGISTERS:
        if register=='raw_r4':continue
        for raw in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
            add('complete-raw-register-width',**{register:raw})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-critical-SR-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,1,127,128,254,255):add('complete-preserved-R14-GBR-and-frame-context',variant=variant)
    return tuple(dict(case,index=index) for index,case in enumerate(rows))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry']!=contract.ENTRY
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['raw_r4'] not in contract.INDICES or case['initial_sr']&~0x3F1):
        raise ValueError('the timer input changes a complete raw CPU, native control, explicit index or byte preimage')


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+i*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for i in range(15)]
    registers[:8]=[case[name] for name in REGISTERS]
    return (*registers,(0x456789AB+case['variant'])&0xFFFFFFFF,
        (0x13579BDF+case['variant'])&0xFFFFFFFF,(0x2468ACE0+case['variant'])&0xFFFFFFFF,
        case['initial_sr'],0xB6C70000)


def memory(case):
    require_case(case);raw=bytearray([0xA5])*RAM_SIZE
    for name,at,width in RAM_FIELDS:raw[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(raw)


def calibrations(declared,image,case):
    fixture,_=contract.fixture_for_case(declared,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}


def logical(ordinary,native):
    if type(ordinary) is not bytes or len(ordinary)!=RAM_SIZE or type(native) is not bytes or len(native)!=NATIVE_SIZE:
        raise ValueError('the timer logical view truncates complete separate ordinary or native snapshots')
    result=bytearray(ordinary);result[0x8500:0x8600]=native;return bytes(result)


def require_input(declared,image,case,observed):
    raw=memory(case);cal=calibrations(declared,image,case)
    if (not test_contract.exact(observed['entry'],contract.ENTRY)
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(raw,)
            or not test_contract.exact(observed['calibration_before'],cal)
            or not test_contract.exact(observed['calibration_after'],cal)
            or observed['native_before']!=raw[0x8500:0x8600]):
        raise ValueError('the timer original changes complete raw CPU, RAM, native85 snapshot or immutable physical inputs')
    if observed['memory_after'][0][0x8500:0x8600]!=raw[0x8500:0x8600]:
        raise ValueError('the timer original replaces actual ordinary shadow bytes with native writes')
    for at in range(256):
        if at!=12 and observed['native_after'][at]!=observed['native_before'][at]:
            raise ValueError('the timer original changes a read-only native indicator or unused complete native canary')


def header(declared,image):
    lines=['/* Complete typed timer/control invocation inputs; no expected outputs. */',
        '#define TIMER_CALIBRATION_SIZE '+str(sum(row['size'] for row in contract.CONTROLLED_CALIBRATION))+'U',
        '#define TIMER_BOUND_SIZE '+str(sum(row['size'] for row in contract.BOUND_SPANS))+'U']
    for name,spans in (('ram_fields',[dict(address=at,size=width) for field,at,width in RAM_FIELDS]),
            ('calibration',contract.CONTROLLED_CALIBRATION),('bound',contract.BOUND_SPANS)):
        lines.append('static const struct span timer_'+name+'[] = {'+
            ','.join('{'+f'0x{row["address"]:x}U,{row["size"]}U'+'}' for row in spans)+'};')
    lines.extend(('struct path_case { uint8_t pattern; uint32_t ram['+str(len(RAM_FIELDS))+']; struct context context;',
        '    uint8_t calibration[TIMER_CALIBRATION_SIZE]; };','static const struct path_case timer_cases[] = {'))
    for case in declared['cases']:
        require_case(case);registers=context(declared['source'],case);cal=calibrations(declared['source'],image,case)
        raw=b''.join(cal[row['address']] for row in contract.CONTROLLED_CALIBRATION)
        ram=','.join(f'0x{case[field]:x}U' for field,at,width in RAM_FIELDS)
        core=','.join(f'0x{value:x}U' for value in registers[:15]);tail=','.join(f'0x{value:x}U' for value in registers[15:])
        lines.append('    {0xa5U,{'+ram+'},{{'+core+'},'+tail+'},{'+','.join(f'0x{value:02x}U' for value in raw)+'}},')
    return '\n'.join((*lines,'};','')).encode()
