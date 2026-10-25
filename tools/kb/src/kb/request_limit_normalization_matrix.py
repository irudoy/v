"""Complete raw request-limit inputs, all real modes and held-other endpoint words."""
from copy import deepcopy
from kb import test_contract
from kb import request_limit_normalization_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('word_113c', 4412, 2),
 ('word_338c', 13196, 2),
 ('word_338e', 13198, 2),
 ('word_3396', 13206, 2),
 ('word_2a7a', 10874, 2),
 ('word_3026', 12326, 2),
 ('prior_3478', 13432, 2),
 ('prior_347a', 13434, 2),
 ('prior_347c', 13436, 2),
 ('prior_412a', 16682, 2),
 ('byte_41f3', 16883, 1),
 ('byte_41fb', 16891, 1),
 ('byte_424f', 16975, 1),
 ('byte_249b', 9371, 1),
 ('word_10ae', 4270, 2),
 ('word_2712', 10002, 2))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update(mode_83c1=8,lower_guard=16)
ARRAYS=dict(upper=16,lower=16,axis=16)
WORD_VALUES=(0,1,799,800,801,999,1000,1001,32767,32768,53499,53500,53501,65534,65535)
DEFAULTS={'word_113c': 1000,
 'word_338c': 48768,
 'word_338e': 48768,
 'word_3396': 48768,
 'word_2a7a': 0,
 'word_3026': 123,
 'prior_3478': 42330,
 'prior_347a': 23205,
 'prior_347c': 51966,
 'prior_412a': 48879,
 'byte_41f3': 0,
 'byte_41fb': 165,
 'byte_424f': 214,
 'byte_249b': 0,
 'word_10ae': 1234,
 'word_2712': 2000,
 'mode_83c1': 46,
 'lower_guard': 0,
 'pattern': 165,
 'upper': [32000,
           32000,
           32000,
           32000,
           32000,
           32000,
           32000,
           32000,
           32000,
           32000,
           32000,
           32000,
           32000,
           32000,
           32000,
           32000],
 'lower': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 'axis': [1000,
          4500,
          8000,
          11500,
          15000,
          18500,
          22000,
          25500,
          29000,
          32500,
          36000,
          39500,
          43000,
          46500,
          50000,
          53500],
 'context': [410407984,
             427383095,
             444358206,
             461333317,
             478308428,
             495283539,
             512258650,
             529233761,
             546208872,
             563183983,
             580159094,
             597134205,
             614109316,
             631084427,
             648059538,
             305414945,
             324508639,
             610839776,
             0,
             3066494976]}

def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS, *ARRAYS, 'context', 'pattern', 'index', 'kind'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or type(case['pattern']) is not int or not 0 <= case['pattern'] <= 255
            or any(type(case[name]) is not int or not 0 <= case[name] < (1 << bits) for name, bits in WIDTHS.items())):
        raise ValueError('the request limit normalization changes a complete typed raw scalar input')
    for name, count in (*ARRAYS.items(), ('context', 20)):
        values = case[name]
        limit = 0x100000000 if name == 'context' else 65536
        if type(values) is not list or len(values) != count or any(type(value) is not int or not 0 <= value < limit for value in values):
            raise ValueError('the request limit normalization truncates a complete word array or incoming context')
    if case['context'][18] & ~0x3F1:
        raise ValueError('the request limit normalization changes the admitted complete I/M/Q/T input')

def cases(source,image):
    rows=[]
    def add(kind,**changes):
        value=deepcopy(DEFAULTS);value.update(changes);value.update(index=len(rows),kind=kind);rows.append(value)
    add('complete-natural-normalization-clamp-and-state')
    add('stock-zero-curves-and-clear-ROM-mode',upper=[0]*16,lower=[0]*16,mode_83c1=0x2C)
    for register in range(20):
        values=(0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF) if register!=18 else (0,1,0xF0,0x100,0x200,0x301,0x3F1)
        for raw in values:
            context=list(DEFAULTS['context']);context[register]=raw
            add('independent-complete-context-field',context=context)
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):
                context=list(DEFAULTS['context']);context[18]=qm|interrupt|t
                add('complete-QM-interrupt-T-context',context=context)
    for name,at,width in RAM_FIELDS:
        for raw in (range(256) if width==1 else WORD_VALUES):add('independent-physical-RAM-word-or-byte',**{name:raw})
    for raw in range(256):add('actual-ROM-mode-byte-and-both-complete-final-paths',mode_83c1=raw)
    for name in ('upper','lower'):
        for cell in range(16):
            for raw in ((16000,32000) if name=='upper' else (0,8000)):
                values=list(DEFAULTS[name]);values[cell]=raw
                signed=-24768 if name=='upper' else -16768
                add('held-other-one-actual-endpoint-word',**{name:values,'word_113c':DEFAULTS['axis'][cell],
                    'word_338c':signed&65535,'word_338e':signed&65535,'word_3396':signed&65535})
    for lower,upper in ((0,0),(8000,0),(32000,32000),(0,1),(0,255),(0,256),(0,257),(0,65535),(32767,32768)):
        for raw in (0,1,799,800,32767,32768,65534,65535):
            add('real-zero-or-positive-span-and-signed-input-boundary',lower=[lower]*16,upper=[upper]*16,
                word_338c=raw,word_338e=raw,word_3396=raw)
    for a,b,c in ((0,0,0),(400,200,600),(200,400,600),(400,600,200),(600,400,800),(800,800,800),(200,200,200)):
        for requested in (0,100,200,400,600,800,65535):
            add('actual-ordered-minimum-maximum-clamp-and-equality',word_338c=(a*40+32768)&65535,
                word_338e=(b*40+32768)&65535,word_3396=(c*40+32768)&65535,word_2a7a=requested)
    for mode in (0x2C,0x2E):
        for override in (0,1):
            for word in (0,1,799,800,801,32767,32768,65535):
                add('actual-override-zero-and800-status-bounds-and-final-mode',mode_83c1=mode,byte_41f3=override,word_3026=word)
    for first,second in ((0,0),(0,65535),(65535,0),(799,800),(800,799),(65535,65535)):
        add('stock-clear-mode-real-alternate-maximum-order-and-equality',mode_83c1=0x2C,word_10ae=first,word_2712=second)
    for coordinate in (0,999,1000,1001,2750,32767,32768,53499,53500,53501,65535):
        add('actual-axis-word-coordinate-boundary',word_113c=coordinate)
    for cell in range(16):
        for raw in (0,1,32767,65535):
            values=list(DEFAULTS['axis']);values[cell]=raw
            add('complete-physical-axis-word-alternative',axis=values,word_113c=12001)
    for cell in range(15):
        add('real-positive-axis-fraction-and-directed-word-interpolation',word_113c=DEFAULTS['axis'][cell]+1750,
            upper=[50000-i*1500 for i in range(16)],lower=[i*500 for i in range(16)])
    for raw in (0,1,32767,32768,65535):
        add('actual-lower-last-zero-fraction-neighbor-word',word_113c=65535,lower_guard=raw)
    for pattern in (0,1,0x5A,0x80,0xFF):add('complete-other-RAM-pattern',pattern=pattern)
    return tuple(rows)

def context(source, case):
    require_case(case)
    return tuple(case['context'])

def memory(case):
    require_case(case)
    out = bytearray([case['pattern']]) * RAM_SIZE
    for name, at, width in RAM_FIELDS:
        out[at:at+width] = case[name].to_bytes(width, 'big')
    return bytes(out)

def input_calibrations(case):
    require_case(case)
    out={row['address']:b''.join(word.to_bytes(2,'big') for word in case[row['name']]) for row in contract.DECLARED['input_blobs']}
    out[0x83C1]=bytes([case['mode_83c1']]);out[0x15500]=case['lower_guard'].to_bytes(2,'big')
    return out

def calibrations(source, image, case):
    fixture, _ = contract.fixture_for_case(source, image, case)
    return {row['address']: fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}

def require_input(source, image, case, observed):
    wanted = calibrations(source, image, case)
    if (observed['entry'] != contract.ENTRY or not test_contract.exact(observed['context'], context(source, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], wanted)
            or not test_contract.exact(observed['calibration_after'], wanted)):
        raise ValueError('the request limit normalization changes a complete immutable input or controlled calibration')

def header(declared, image):
    source, cal, bound = declared['source'], contract.CONTROLLED_CALIBRATION, contract.BOUND_SPANS
    lines = ['/* Complete raw inputs for the full natural endpoint normalizer and boundary caller. */',
             f'#define ENDPOINT_CALIBRATION_SIZE {sum(row["size"] for row in cal)}U',
             f'#define ENDPOINT_BOUND_SIZE {sum(row["size"] for row in bound)}U',
             'static const struct span endpoint_calibration[] = {' + ','.join('{%dU,%dU}' % (row['address'], row['size']) for row in cal) + '};',
             'static const struct span endpoint_bound[] = {' + ','.join('{%dU,%dU}' % (row['address'], row['size']) for row in bound) + '};',
             'static const struct span endpoint_ram_fields[] = {' + ','.join('{%dU,%dU}' % (at, width) for name, at, width in RAM_FIELDS) + '};',
             f'struct path_case {{ uint32_t ram[{len(RAM_FIELDS)}];struct context context;uint8_t pattern,calibration[ENDPOINT_CALIBRATION_SIZE]; }};',
             'static const struct path_case endpoint_cases[] = {']
    for case in declared['cases']:
        raw = context(source, case)
        ctx = '{{' + ','.join(f'0x{value:x}U' for value in raw[:15]) + '},' + ','.join(f'0x{value:x}U' for value in raw[15:]) + '}'
        mapping = calibrations(source, image, case)
        blob = b''.join(mapping[row['address']] for row in cal)
        lines.append('{{' + ','.join(f'0x{case[name]:x}U' for name, at, width in RAM_FIELDS) + '},' + ctx +
                     f',0x{case["pattern"]:02x}U,{{' + ','.join(f'0x{value:02x}U' for value in blob) + '}},')
    return '\n'.join((*lines, '};', '')).encode()

