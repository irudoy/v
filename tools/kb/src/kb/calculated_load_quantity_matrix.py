"""Input-only paired stock entries; the handoff byte is never a case result."""
from copy import deepcopy
from kb import test_contract
from kb import calculated_load_quantity_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('word_4524',0x4524,2),('byte_11b3',0x11B3,1),('word_1024',0x1024,2),
    ('byte_244f',0x244F,1),('byte_594e',0x594E,1),('byte_5735',0x5735,1),
    ('byte_594b',0x594B,1),('byte_5732',0x5732,1),('prior_329f',0x329F,1),
    ('prior_413e',0x413E,1),('prior_9818',0x9818,4))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS['control_870e']=8
ARRAYS={'axis':(16,8),'curve':(17,8),'load_curve':(16,16),
    'producer_context':(20,32),'consumer_context':(20,32)}

def initial_context(phase):
    return [*((0x18765430+i*0x01030507+phase*0x2030405)&0xFFFFFFFF for i in range(15)),
        0x12344321+phase,0x13579BDF+phase,0x2468ACE0+phase,0,0xB6C70000+phase]

DEFAULTS=dict(word_4524=0x5000,byte_11b3=0x50,word_1024=64,byte_244f=32,
    byte_594e=0,byte_5735=0,byte_594b=0,byte_5732=0,prior_329f=0xA5,
    prior_413e=0x5A,prior_9818=0xA5C3E187,control_870e=0x38,
    axis=[16*i for i in range(16)],curve=[128]*17,load_curve=[256]*16,
    producer_context=initial_context(0),consumer_context=initial_context(1))

def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,*ARRAYS,'index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())):
        raise ValueError('the paired quantity input changes its complete raw scalar shape or width')
    for name,(count,bits) in ARRAYS.items():
        values=case[name]
        if type(values) is not list or len(values)!=count or any(type(v) is not int or not 0<=v<(1<<bits) for v in values):
            raise ValueError('the paired quantity input changes a complete raw blob or independent context')
    if any(case[name][18]&~0x3F1 for name in ('producer_context','consumer_context')):
        raise ValueError('the paired quantity context changes the admitted complete I/M/Q/T input')

def cases(source,image):
    rows=[]
    def add(kind,**updates):
        case=deepcopy(DEFAULTS);case.update(updates);case.update(index=len(rows),kind=kind);rows.append(case)
    add('complete-two-phase-default')
    for phase in ('producer','consumer'):
        for register in range(20):
            values=(0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF) if register!=18 else (0,1,0xF0,0x100,0x200,0x301,0x3F1)
            for value in values:
                context=initial_context(0 if phase=='producer' else 1);context[register]=value
                add('complete-independent-phase-context',**{phase+'_context':context})
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):
                    context=initial_context(0 if phase=='producer' else 1);context[18]=qm|interrupt|t
                    add('complete-phase-QM-interrupt-T',**{phase+'_context':context})
    for coordinate in range(256):
        add('complete-producer-high-byte-coordinate',word_4524=coordinate<<8,
            curve=[16+12*i for i in range(17)],word_1024=16)
    for low in (0,1,127,128,254,255):add('ignored-sample-low-byte-preservation',word_4524=0x5000|low)
    for raw in (0,1,127,128,254,255):
        curve=[128]*17;curve[16]=raw
        add('physical-clamped-neighbor-with-zero-numerical-weight',curve=curve,word_4524=0xFF00)
    for index in range(16):
        for raw in (0,1,32,64,96,128,160,200,254,255):
            curve=[128]*17;curve[index]=raw
            add('exact-source-byte-causal-alternative',curve=curve,word_4524=(index*16)<<8)
        for raw in (128,256,512,0,1,65535):
            load=[256]*16;load[index]=raw
            add('exact-first-curve-word-causal-alternative',load_curve=load,byte_11b3=index*16)
    for coordinate in (0,1,15,16,17,79,80,81,127,128,129,239,240,241,254,255):
        for curve in ([15*i for i in range(17)],[255-15*i for i in range(17)],[0]*17,[1]*17,[255]*17):
            add('axis-and-interpolation-direction-boundaries',word_4524=coordinate<<8,curve=list(curve))
    for index in range(16):
        for raw in (0,1,63,64,127,128,239,240,254,255):
            axis=list(DEFAULTS['axis']);axis[index]=raw
            add('complete-raw-axis-byte',axis=axis,curve=[16+12*i for i in range(17)],
                word_4524=min(255,index*16+8)<<8,word_1024=16)
    for raw in range(256):
        add('complete-first-curve-coordinate',byte_11b3=raw,load_curve=[128+16*i for i in range(16)])
        add('complete-control-byte',control_870e=raw,curve=[64]*17)
    for field in ('byte_244f','byte_594e','byte_5735','byte_594b','byte_5732'):
        for raw in (0,1,31,32,33,63,64,65,96,127,128,255):
            add('exact-diagnostic-or-mode-gate',**{field:raw})
            if field in ('byte_594e','byte_5735'):add('mode-clear-diagnostic-gate',**{field:raw,'byte_244f':0})
    for field in ('prior_329f','prior_413e'):
        for raw in (0,1,127,128,254,255):add('real-publication-poison-invariance',**{field:raw})
    for word in (0,1,2,31,32,63,64,127,128,255,256,32767,32768,65535):
        for mode in (0x28,0x38):add('actual-first-and-second-division-widths',word_1024=word,control_870e=mode)
    for k in (0,1,16,32,64,128,200,255):
        for mode in (0x28,0x38):
            for divisor in (0,1,128,256,65535):
                add('real-K-zero-nonzero-and-first-divisor-fault',curve=[k]*17,
                    control_870e=mode,load_curve=[divisor]*16)
    return tuple(rows)

def context(source,case,phase):
    require_case(case)
    if type(phase) is not int or phase not in (0,1):raise ValueError('the quantity input changes its fixed phase identity')
    return tuple(case[('producer','consumer')[phase]+'_context'])

def memory(case):
    require_case(case);out=bytearray([0xA5])*RAM_SIZE
    for name,at,width in RAM_FIELDS:out[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(out)

def input_calibrations(case):
    require_case(case)
    return {0x870E:bytes((case['control_870e'],)),0x11B7B:bytes(case['axis']),
        0x129D2:bytes(case['curve']),0x1491A:b''.join(v.to_bytes(2,'big') for v in case['load_curve'])}

def calibrations(source,image,case):
    fixture,_=contract.fixture_for_case(source,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}

def require_input(source,image,case,observed,phase,previous=None):
    wanted=calibrations(source,image,case)
    if (observed['phase']!=phase or observed['entry']!=contract.ENTRIES[phase]
            or not test_contract.exact(observed['context'],context(source,case,phase))
            or not test_contract.exact(observed['calibration_before'],wanted)
            or not test_contract.exact(observed['calibration_after'],wanted)):
        raise ValueError('the quantity phase changes its complete immutable raw input or calibration')
    if phase==0:
        if previous is not None or observed['memory_before']!=(memory(case),):
            raise ValueError('the quantity producer changes its complete initial RAM')
    elif (previous is None or previous['phase']!=0 or previous['pair']!=observed['pair']
            or previous['memory_after']!=observed['memory_before']
            or not test_contract.exact(previous['calibration_after'],observed['calibration_before'])
            or previous['bound_after']!=observed['bound_before']):
        raise ValueError('the quantity consumer resets, substitutes or detaches the complete actual producer handoff')

def header(declared,image):
    source=declared['source'];cal=contract.CONTROLLED_CALIBRATION;bound=contract.BOUND_SPANS
    size=sum(r['size'] for r in cal)
    lines=['/* Raw paired inputs only; no K, quotient or expected output. */',
        f'#define QUANTITY_CALIBRATION_SIZE {size}U',
        f'#define QUANTITY_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        'static const struct span quantity_calibration[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in cal)+'};',
        'static const struct span quantity_bound[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in bound)+'};',
        'struct path_case { '+''.join('uint32_t '+name+';' for name,at,width in RAM_FIELDS)+
        'struct context contexts[2];uint8_t calibration[QUANTITY_CALIBRATION_SIZE]; };',
        'static const struct path_case quantity_cases[] = {']
    for case in declared['cases']:
        require_case(case);contexts=[]
        for phase in (0,1):
            raw=context(source,case,phase)
            contexts.append('{{'+','.join(f'0x{v:x}U' for v in raw[:15])+'},'+','.join(f'0x{v:x}U' for v in raw[15:])+'}')
        mapping=calibrations(source,image,case);blob=b''.join(mapping[r['address']] for r in cal)
        lines.append('{'+','.join(f'0x{case[name]:x}U' for name,at,width in RAM_FIELDS)+',{' +
            ','.join(contexts)+'},{'+','.join(f'0x{v:02x}U' for v in blob)+'}},')
    return '\n'.join((*lines,'};','')).encode()
