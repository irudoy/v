"""Raw event timing words, backward axis and flags with independent complete input state."""
from copy import deepcopy
from kb import test_contract
from kb import event_timing_candidate_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('byte_24c5',0x24C5,1),('byte_24cb',0x24CB,1),('byte_11f9',0x11F9,1),
 ('byte_11fa',0x11FA,1),('word_23c2',0x23C2,2),('byte_22fa',0x22FA,1),
 ('byte_24cc',0x24CC,1),('byte_24c2',0x24C2,1),('byte_2378',0x2378,1),('byte_24c0',0x24C0,1),
 ('byte_229d',0x229D,1),('byte_25fc',0x25FC,1),('word_237e',0x237E,2),
 ('byte_2459',0x2459,1),('byte_40e7',0x40E7,1),('byte_2356',0x2356,1),
 ('prior_11d6',0x11D6,2),('prior_11d8',0x11D8,2),('prior_2000',0x2000,2),
 ('prior_1ff6',0x1FF6,2),('prior_1ff8',0x1FF8,4),('prior_226c',0x226C,1),
 ('prior_12d6',0x12D6,1),('prior_9818',0x9818,4))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({row['name']:row['size']*8 for row in contract.DECLARED['control_blobs']})
WIDTHS['pattern']=8
ARRAYS={'context':(20,32),'source_words':(9,16),'source_axis':(8,16)}
BYTE_VALUES=(0,1,2,3,4,15,31,32,33,63,64,65,99,100,101,126,127,128,129,254,255)
WORD_VALUES=(0,1,2,99,100,127,128,255,256,257,8191,8192,8193,25700,25701,32767,32768,57344,65534,65535)
LONG_VALUES=(0,1,127,128,255,256,32767,32768,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFF)
DEFAULT_CONTEXT=[*((0x18765430+i*0x01030507)&0xFFFFFFFF for i in range(15)),
 0x12344321,0x13579BDF,0x2468ACE0,0,0xB6C70000]
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update(context=DEFAULT_CONTEXT,source_words=[0]*9,source_axis=[i*8192 for i in range(8)],
 pattern=0xA5,rom_8710=0x7C,rom_8290=0,rom_8a3c=100,rom_8a3d=100,
 prior_11d6=0xABCD,prior_11d8=0x1234,prior_2000=0xA5C7,prior_1ff6=0xD8E9,
 prior_226c=0x5A,prior_12d6=0x6B,prior_9818=0xDEADBEEF)

def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,*ARRAYS,'index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())):
        raise ValueError('the event timing input changes an exact raw scalar or supplies a live result')
    for name,(count,bits) in ARRAYS.items():
        values=case[name]
        if type(values) is not list or len(values)!=count or any(type(v) is not int or not 0<=v<(1<<bits) for v in values):
            raise ValueError('the event timing input truncates a complete raw context, physical map or axis')
    if case['context'][18]&~0x3F1:
        raise ValueError('the event timing input changes admitted complete I/M/Q/T controls')

def cases(source,image):
    rows=[]
    def add(kind,**changes):
        value=deepcopy(DEFAULTS);value.update(changes);value.update(index=len(rows),kind=kind);rows.append(value)
    add('complete-published-live-event-timing-candidate')
    stock={row['name']:int.from_bytes(image[row['address']:row['address']+row['size']],'big') for row in source['control_blobs']}
    stock['source_words']=[int.from_bytes(image[0x147DA+2*i:0x147DC+2*i],'big') for i in range(9)]
    stock['source_axis']=[int.from_bytes(image[0x13C48+2*i:0x13C4A+2*i],'big') for i in range(8)]
    add('complete-owned-stock-calibration-bytes',**stock)
    for register in range(20):
        values=(0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF) if register!=18 else (0,1,0xF0,0x100,0x200,0x301,0x3F1)
        for raw in values:
            context=list(DEFAULT_CONTEXT);context[register]=raw
            add('independent-complete-CPU-context-field',context=context)
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):
                context=list(DEFAULT_CONTEXT);context[18]=qm|interrupt|t
                add('complete-QM-interrupt-T-context',context=context)
    for field,at,width in RAM_FIELDS:
        for raw in BYTE_VALUES if width==1 else WORD_VALUES if width==2 else LONG_VALUES:
            add('raw-input-and-independent-prior-publication',**{field:raw})
    for row in source['control_blobs']:
        for raw in range(256):
            add('complete-raw-ROM-byte-parameter',**{row['name']:raw})
            if row['name']=='rom_8a3c':add('alternate-coefficient-raw-byte',byte_2459=32,**{row['name']:raw})
    for index in range(9):
        for raw in (0,1,127,128,255,256,32767,32768,65534,65535):
            words=[0]*9;words[index]=raw
            add('held-other-active-word-or-physical-endpoint-guard',source_words=words,
                word_237e=min(index,7)*8192)
    patterns=([i*8192 for i in range(8)],[0]*8,[65535]*8,
        [65535-i*8192 for i in range(8)],[0,65535,0,32768,32767,1,65534,65535],
        [0,1,1,128,128,32768,65535,65535])
    for axis in patterns:
        coordinates=set(WORD_VALUES)
        for knot in axis:coordinates.update((max(0,knot-1),knot,min(65535,knot+1)))
        for coordinate in sorted(coordinates):
            add('rightmost-unsigned-axis-and-directed-word-fraction',source_axis=list(axis),
                word_237e=coordinate,source_words=[min(65535,i*8191) for i in range(9)])
            add('descending-physical-word-interpolation',source_axis=list(axis),
                word_237e=coordinate,source_words=[max(0,65535-i*8191) for i in range(9)])
    for index in range(8):
        for raw in WORD_VALUES:
            axis=[i*8192 for i in range(8)];axis[index]=raw
            for coordinate in sorted({max(0,raw-1),raw,min(65535,raw+1)}):
                add('independent-axis-knot-equality-and-adjacent-brackets',source_axis=axis,
                    word_237e=coordinate,source_words=[100*i for i in range(9)])
    for raw in WORD_VALUES:
        for coefficient in (0,1,99,100,101,255):
            add('coefficient-product-division-and-uint16-cap-boundaries',source_words=[raw]*9,
                rom_8a3d=coefficient)
            add('alternate-coefficient-product-division-and-uint16-cap',source_words=[raw]*9,
                rom_8a3c=coefficient,byte_2459=32)
    for knock in (0,32):
        for gate5,gateb in ((0,0),(32,0),(0,4),(32,4)):
            for first,second,prior,high in ((0,0,0,0),(127,128,255,255),(128,127,127,128),
                    (255,1,128,1),(1,255,0,0)):
                add('actual-ordinary-and-knock-signed-boundaries',rom_8710=knock,
                    byte_24c5=gate5,byte_24cb=gateb,byte_11f9=first,byte_11fa=second,
                    byte_22fa=prior,word_23c2=high*256)
    for timer in (0,1,127,128,255):
        for flags in (0,1,2,3,128,129,130,255):
            for previous in (0,1,127,128,0xFFFFFFFF,0x80000000,0x7FFFFFFF):
                add('whole-counter-equality-and-natural-slew-activation',rom_8290=timer,
                    byte_24c2=flags,byte_24c0=64,prior_1ff8=previous,byte_229d=0,byte_25fc=0)
    for previous in LONG_VALUES:
        for target in (0,1,127,128,255):
            for timer in (0,1,255):
                add('natural-full32-counter-versus-sign8-target-and-sign16-step',rom_8290=1,
                    byte_24c0=64,byte_24c2=0,prior_1ff8=previous,byte_229d=target,byte_25fc=timer)
    for limit in (0,1,127,128,255):
        for flags in (0,2):
            for first,correction,target in ((0,0,0),(127,128,255),(128,127,127),(255,1,128)):
                add('actual-native-RAM-limit-and-final-signed-byte-clamps',byte_40e7=limit,
                    byte_24c2=flags,byte_11f9=first,byte_2356=correction,byte_2378=target)
    for target in (0,1,127,128,255):
        add('actual-override-bypass-preserves-map-and-intermediate-priors',byte_24cc=2,byte_2378=target)
    for raw in WORD_VALUES:
        words=[0]*8+[raw]
        add('ninth-physical-word-output-invariance-at-last-knot',source_words=words,word_237e=57344)
    for pattern in (0,1,0x5A,0x80,0xFF):add('complete-unmodified-RAM-pattern',pattern=pattern)
    return tuple(rows)

def context(source,case):
    require_case(case);return tuple(case['context'])

def memory(case):
    require_case(case);out=bytearray([case['pattern']])*RAM_SIZE
    for name,at,width in RAM_FIELDS:out[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(out)

def input_calibrations(case):
    require_case(case)
    mapping={row['address']:case[row['name']].to_bytes(row['size'],'big') for row in contract.DECLARED['control_blobs']}
    mapping[0x147DA]=b''.join(value.to_bytes(2,'big') for value in case['source_words'])
    mapping[0x13C48]=b''.join(value.to_bytes(2,'big') for value in case['source_axis'])
    return mapping

def calibrations(source,image,case):
    fixture,_=contract.fixture_for_case(source,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}

def require_input(source,image,case,observed):
    wanted=calibrations(source,image,case)
    if (observed['entry']!=contract.ENTRY or not test_contract.exact(observed['context'],context(source,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],wanted)
            or not test_contract.exact(observed['calibration_after'],wanted)):
        raise ValueError('the event timing candidate changes a complete immutable raw input or calibration')

def header(declared,image):
    source=declared['source'];cal,bound=contract.CONTROLLED_CALIBRATION,contract.BOUND_SPANS
    lines=['/* Complete raw inputs only; no supplied live candidate or expected output. */',
        f'#define EVENT_CALIBRATION_SIZE {sum(r["size"] for r in cal)}U',
        f'#define EVENT_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        'static const struct span event_calibration[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in cal)+'};',
        'static const struct span event_bound[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in bound)+'};',
        'struct path_case { '+''.join('uint32_t '+name+';' for name,at,width in RAM_FIELDS)+
        'struct context context;uint8_t pattern,calibration[EVENT_CALIBRATION_SIZE]; };',
        'static const struct path_case event_cases[] = {']
    for case in declared['cases']:
        raw=context(source,case)
        ctx='{{'+','.join(f'0x{v:x}U' for v in raw[:15])+'},'+','.join(f'0x{v:x}U' for v in raw[15:])+'}'
        mapping=calibrations(source,image,case);blob=b''.join(mapping[row['address']] for row in cal)
        lines.append('{'+','.join(f'0x{case[name]:x}U' for name,at,width in RAM_FIELDS)+','+ctx+
            f',0x{case["pattern"]:02x}U,'+'{'+','.join(f'0x{v:02x}U' for v in blob)+'}},')
    return '\n'.join((*lines,'};','')).encode()
