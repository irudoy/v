"""Input-only full natural state, actual eight-byte curve and complete raw CPU context."""
from copy import deepcopy
from kb import test_contract
from kb import bfs_state_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('word_1026',0x1026,2),('word_1062',0x1062,2),
    ('byte_1077',0x1077,1),('byte_1079',0x1079,1),('prior_1f78',0x1F78,1),
    ('byte_2459',0x2459,1),('byte_2461',0x2461,1),('byte_2462',0x2462,1),
    ('byte_2465',0x2465,1),('byte_24b1',0x24B1,1),('byte_24ba',0x24BA,1),
    ('byte_2542',0x2542,1),('state_39d0',0x39D0,4),('state_39d4',0x39D4,4),
    ('record129',0x5A94,1))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update(rom_875c=8,rom_8ad9=8,**{f'curve_{index}':8 for index in range(8)})
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update(word_1026=9000,word_1062=2000,byte_1077=64,byte_1079=100,
    prior_1f78=0xA5,byte_2459=32,byte_2461=0xA5,byte_2462=1,byte_2465=64,
    byte_24b1=0,byte_24ba=128,byte_2542=1,state_39d0=2,state_39d4=0,record129=0,
    rom_875c=0,rom_8ad9=32,pattern=0xA5,
    context=[*((0x18765430+i*0x01030507)&0xFFFFFFFF for i in range(15)),
        0x12344321,0x13579BDF,0x2468ACE0,0,0xB6C70000])
DEFAULTS.update({f'curve_{i}':value for i,value in enumerate((0,32,64,96,128,160,192,255))})
ENTRY_FIELDS={0x3A750:('byte_1077','word_1026','word_1062','rom_875c','rom_8ad9',
    *(f'curve_{i}' for i in range(8)))}
CAUSAL_CONFIGURATION={row['field']:(row['address'],row['size']) for row in contract.CONFIGURATION}
CAUSAL_CONFIGURATION.update({f'curve_{i}':(0x12A3A+i,1) for i in range(8)})
REGISTERS=()
BYTE_VALUES=(0,1,2,3,7,15,16,31,32,33,63,64,65,95,96,100,127,128,129,223,224,225,254,255)
WORD_VALUES=(0,1,31,32,127,128,255,256,8191,8192,8193,16383,16384,32767,32768,65534,65535)
LONG_VALUES=(0,1,2,3,127,128,255,256,32767,32768,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFF)

def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'context','pattern','index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or type(case['pattern']) is not int or not 0<=case['pattern']<=255
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())):
        raise ValueError('the BFS state input changes a complete scalar width or introduces a result column')
    context=case['context']
    if (type(context) is not list or len(context)!=20
            or any(type(v) is not int or not 0<=v<=0xFFFFFFFF for v in context)
            or context[18]&~0x3F1):
        raise ValueError('the BFS state input changes its complete20-field CPU/SR context')

def cases(source,image):
    rows=[]
    def add(kind,**updates):
        value=deepcopy(DEFAULTS);value.update(updates);value.update(index=len(rows),kind=kind);rows.append(value)
    add('complete-natural-state-caller')
    for field,at,width in RAM_FIELDS:
        for raw in BYTE_VALUES if width==1 else WORD_VALUES if width==2 else LONG_VALUES:
            add('complete-raw-gate-quantity-output-and-prior-state',**{field:raw})
    for register in range(20):
        for raw in ((0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF) if register!=18 else (0,1,0xF0,0x100,0x200,0x301,0x3F1)):
            context=list(DEFAULTS['context']);context[register]=raw;add('complete-independent-CPU-input',context=context)
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):
                context=list(DEFAULTS['context']);context[18]=qm|interrupt|t
                add('complete-QM-interrupt-T-input',context=context)
    for pattern in (0,1,0x55,0xA5,255):add('complete-unrelated-RAM-preimage',pattern=pattern)
    for first in (0,1,2,3,0x80000000,0xFFFFFFFF):
        for enable in (0,1,128,255):
            for pending in (0,1,128,255):add('first-state-machine-and-initialization-publications',state_39d0=first,byte_2462=enable,byte_2542=pending)
    shapes=((0,32,64,96,128,160,192,255),(255,223,191,159,127,95,63,0),(128,)*8)
    for curve in shapes:
        fields={f'curve_{i}':raw for i,raw in enumerate(curve)}
        for coordinate in range(256):add('full-byte-coordinate-real-tails-and-interpolation',state_39d0=0,byte_2462=1,byte_1077=coordinate,**fields)
    for i in range(8):
        for raw in (0,1,127,128,255):
            add('held-other-each-active-curve-cell',state_39d0=0,byte_1077=32*i,**{f'curve_{i}':raw})
    for raw in range(256):
        add('held-other-full-raw-temperature-threshold',rom_875c=raw)
        add('held-other-full-raw-BFS-window-center',rom_8ad9=raw)
        add('complete-record129-byte',record129=raw)
    for mode in (0,16):
        for center in (0,1,32,127,128,255):
            raw_center=center*256
            for delta in (-32769,-257,-256,-129,-128,-1,0,1,127,128,255,256,32767):
                coordinate=max(0,min(65535,raw_center+delta))
                for width in (0,1,31,32,2000,16383,16384,32767,32768,65535):
                    add('independent-full-BFS-quantity-window-boundary',byte_24b1=mode,rom_8ad9=center,
                        word_1026=coordinate,word_1062=width)
    for previous in (0,1,127,128,254,255):
        for temperature in (0,1,127,128,251,252,253,254,255):
            for threshold in (0,1,127,128,254,255):
                add('actual-byte-hysteresis-unwrapped-four-increment',byte_24ba=previous,
                    byte_1079=temperature,rom_875c=threshold)
    return tuple(rows)

def context(source,case):
    require_case(case);return tuple(case['context'])

def memory(case):
    require_case(case);out=bytearray([case['pattern']])*RAM_SIZE
    for name,at,width in RAM_FIELDS:out[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(out)

def input_calibrations(case):
    require_case(case)
    return {0x12A3A:bytes(case[f'curve_{i}'] for i in range(8)),0x875C:bytes([case['rom_875c']]),0x8AD9:bytes([case['rom_8ad9']])}

def calibrations(source,image,case):
    fixture,_=contract.fixture_for_case(source,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}

def require_input(source,image,case,observed):
    wanted=calibrations(source,image,case)
    if (observed['entry']!=contract.ENTRY or not test_contract.exact(observed['context'],context(source,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],wanted)
            or not test_contract.exact(observed['calibration_after'],wanted)):
        raise ValueError('the BFS state caller changes a complete raw input, pointer or immutable calibration')

def header(declared, image):
    source, cal, bound = declared['source'], contract.CONTROLLED_CALIBRATION, contract.BOUND_SPANS
    lines = ['/* Complete raw inputs for the full natural BFS state caller and real helpers. */',
             f'#define BFS_STATE_CALIBRATION_SIZE {sum(row["size"] for row in cal)}U',
             f'#define BFS_STATE_BOUND_SIZE {sum(row["size"] for row in bound)}U',
             'static const struct span bfs_state_calibration[] = {' + ','.join('{%dU,%dU}' % (row['address'], row['size']) for row in cal) + '};',
             'static const struct span bfs_state_bound[] = {' + ','.join('{%dU,%dU}' % (row['address'], row['size']) for row in bound) + '};',
             'static const struct span bfs_state_ram_fields[] = {' + ','.join('{%dU,%dU}' % (at, width) for name, at, width in RAM_FIELDS) + '};',
             f'struct path_case {{ uint32_t ram[{len(RAM_FIELDS)}];struct context context;uint8_t pattern,calibration[BFS_STATE_CALIBRATION_SIZE]; }};',
             'static const struct path_case bfs_state_cases[] = {']
    for case in declared['cases']:
        raw = context(source, case)
        ctx = '{{' + ','.join(f'0x{value:x}U' for value in raw[:15]) + '},' + ','.join(f'0x{value:x}U' for value in raw[15:]) + '}'
        mapping = calibrations(source, image, case)
        blob = b''.join(mapping[row['address']] for row in cal)
        lines.append('{{' + ','.join(f'0x{case[name]:x}U' for name, at, width in RAM_FIELDS) + '},' + ctx +
                     f',0x{case["pattern"]:02x}U,{{' + ','.join(f'0x{value:02x}U' for value in blob) + '}},')
    return '\n'.join((*lines, '};', '')).encode()

