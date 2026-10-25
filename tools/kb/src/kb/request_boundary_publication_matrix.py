"""Raw complete dispatcher inputs and held-other signed-bound alternatives."""
from copy import deepcopy
from kb import test_contract
from kb import request_boundary_publication_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('byte_106f',0x106F,1),('byte_11ae',0x11AE,1),('byte_11b2',0x11B2,1),
    ('byte_1864',0x1864,1),('byte_186b',0x186B,1),('word_19c2',0x19C2,2),
    ('word_19c6',0x19C6,2),('word_19cc',0x19CC,2),('word_2434',0x2434,2),
    ('word_2438',0x2438,2),('byte_244f',0x244F,1),('byte_289c',0x289C,1),
    ('byte_28cc',0x28CC,1),('byte_2ec3',0x2EC3,1),('byte_2ece',0x2ECE,1),
    ('byte_3368',0x3368,1),('byte_3369',0x3369,1),('byte_336a',0x336A,1),
    ('byte_336b',0x336B,1),('word_3446',0x3446,2),('byte_3448',0x3448,1),
    ('byte_3449',0x3449,1),('word_347e',0x347E,2),('word_3480',0x3480,2),
    ('word_3482',0x3482,2),('word_3484',0x3484,2),('word_349a',0x349A,2),
    ('word_34a4',0x34A4,2),('word_34b4',0x34B4,2),('word_34b8',0x34B8,2),
    ('word_34ba',0x34BA,2),('word_34ca',0x34CA,2),('byte_351b',0x351B,1),
    ('byte_351c',0x351C,1),('word_40c6',0x40C6,2),('word_4138',0x4138,2),
    ('word_413a',0x413A,2),('word_415e',0x415E,2),('word_4160',0x4160,2),
    ('byte_4184',0x4184,1),('byte_41bb',0x41BB,1),('byte_41e1',0x41E1,1),
    ('byte_4204',0x4204,1),('byte_420a',0x420A,1),('byte_420b',0x420B,1),
    ('byte_4253',0x4253,1),('byte_43e9',0x43E9,1),('prior_fault',0x9818,4))
CONTROL_FIELDS=(('mode_8b38',0x8B38),('mode_83c1',0x83C1),('limit_88c2',0x88C2),
    ('counter_8cab',0x8CAB),('limit_8868',0x8868),('limit_884a',0x884A),('reload_8423',0x8423))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({name:8 for name,at in CONTROL_FIELDS})
ARRAYS={'curve_12e1a':16,'row_axis':4,'column_axis':4,'grid_aafa':16,'grid_aaea':16,'thresholds_8d36':5}
BYTE_VALUES=(0,1,2,3,4,6,7,9,10,15,16,17,31,32,63,64,127,128,129,239,240,241,254,255)
WORD_VALUES=(0,1,2,99,100,101,1999,2000,2001,0x7FFF,0x8000,0x8001,0xFFFE,0xFFFF)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update(word_19c2=300,word_2438=200,word_34ca=(-50)&65535,word_34b8=1000,
    word_34ba=800,word_34b4=700,word_3482=0,word_347e=1200,word_3484=0,word_3480=1200,
    word_413a=(-200)&65535,word_4138=2000,word_349a=0,word_19c6=0xA55A,
    word_19cc=0x5AA5,word_34a4=0x5555,word_2434=0xAAAA,word_415e=0x55AA,word_4160=0xAA55,
    byte_1864=32,byte_186b=47,byte_106f=80,byte_11b2=64,byte_11ae=64,word_40c6=256,
    byte_4184=0,byte_244f=0,byte_2ec3=3,byte_41e1=1,byte_3448=7,word_3446=20,
    byte_28cc=1,byte_43e9=2,byte_41bb=0xA5,byte_4253=0xA5,prior_fault=0xA5C3E187,
    mode_8b38=0,mode_83c1=0,limit_88c2=15,counter_8cab=100,limit_8868=9,limit_884a=15,reload_8423=100,
    curve_12e1a=[64+4*i for i in range(16)],row_axis=[0,64,128,192],column_axis=[0,64,128,192],
    grid_aafa=[10+i for i in range(16)],grid_aaea=[20+i for i in range(16)],thresholds_8d36=[24,24,0,0,10],
    context=[*((0x18765430+i*0x01030507)&0xFFFFFFFF for i in range(15)),
        0x12344321,0x13579BDF,0x2468ACE0,0,0xB6C70000])

def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,*ARRAYS,'context','index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())):
        raise ValueError('the request input changes a complete raw scalar shape or width')
    for name,count in (*ARRAYS.items(),('context',20)):
        values=case[name];limit=0x100000000 if name=='context' else 256
        if type(values) is not list or len(values)!=count or any(type(v) is not int or not 0<=v<limit for v in values):
            raise ValueError('the request input changes a complete raw array or context')
    if case['context'][18]&~0x3F1:
        raise ValueError('the request input changes the admitted complete I/M/Q/T input')

def cases(source,image):
    rows=[]
    def add(kind,**changes):
        value=deepcopy(DEFAULTS);value.update(changes);value.update(index=len(rows),kind=kind);rows.append(value)
    add('complete-natural-dispatcher-default')
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
    for field,at,width in RAM_FIELDS:
        values=BYTE_VALUES if width==1 else WORD_VALUES if width==2 else (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF)
        for raw in values:add('independent-physical-RAM-input-or-prior-state',**{field:raw})
    for field,at in CONTROL_FIELDS:
        for raw in range(256):add('complete-raw-configuration-byte',**{field:raw})
    grid_profile=dict(byte_4184=128,byte_244f=32,byte_41e1=1,word_3446=0,byte_2ec3=3)
    for field,count in ARRAYS.items():
        for index in range(count):
            for raw in (0,1,63,64,127,128,192,254,255):
                values=list(DEFAULTS[field]);values[index]=raw
                profile={}
                if field in ('grid_aafa','grid_aaea'):
                    profile=dict(grid_profile,byte_11ae=(index//4)*64,word_40c6=(index%4)*256)
                elif field in ('row_axis','column_axis'):
                    profile=dict(grid_profile)
                    profile['byte_11ae' if field=='row_axis' else 'word_40c6']=min(255,index*64+1)*(1 if field=='row_axis' else 4)
                elif field=='curve_12e1a':profile['byte_106f']=index*16
                add('independent-full-calibration-array-byte',**dict(profile,**{field:values}))
    for raw in range(256):
        add('complete-real-byte-curve-coordinate',byte_106f=raw)
        add('complete-real-lower-knot-row-coordinate',**dict(grid_profile,byte_11ae=raw))
        add('complete-real-lower-knot-stack-column-coordinate',**dict(grid_profile,word_40c6=raw*4))
    # These cases isolate every numerical19C6 input while retaining the
    # complete actual first-stage inputs and observer context.
    isolated=dict(word_2438=2000,word_19c2=3000,word_34ca=(-1000)&65535,
        word_34b8=32767,word_34ba=32767,word_34b4=32767,word_3482=0,word_347e=32767,
        word_3484=32768,word_3480=32767,word_413a=32768,word_4138=32767,word_349a=32768,
        mode_8b38=0,mode_83c1=1)
    profiles={
        'word_2438':{},'word_34ba':{},'word_34b4':{},
        'word_3484':dict(word_2438=(-2000)&65535),
        'word_3480':{},'word_413a':dict(word_2438=0),
        'word_4138':{},'word_349a':dict(word_3480=100,mode_83c1=0),
        'word_34ca':dict(word_2438=(-2000)&65535,mode_8b38=1),
    }
    for field,profile in profiles.items():
        for raw in (-32768,-3000,-2000,-1001,-1000,-999,-1,0,1,99,100,101,999,1000,1001,1999,2000,2001,3000,32767):
            add('held-other-actual-signed-word-publication',**dict(isolated,**profile,**{field:raw&65535}))
    for raw in (0,1,2,3,32,33,255):
        add('held-other-mode-bit0-with-negative-selected-request',**dict(isolated,
            word_2438=(-2000)&65535,mode_8b38=raw))
        add('held-other-direct-versus-minimum-actual-store',**dict(isolated,
            word_3480=100,word_349a=1000,mode_83c1=raw))
    for low,high in ((-32768,32767),(-200,2000),(2000,-200),(0,0),(32767,-32768)):
        for selected in (-32768,-2001,-2000,-201,-200,-1,0,1,1999,2000,2001,32767):
            for mode in (0,1,2,3,32,33,255):
                add('ordered-signed-bounds-including-reversed-limits',word_413a=low&65535,
                    word_4138=high&65535,word_2438=selected&65535,mode_83c1=mode)
    for mode in (0,1,2,3,64,128,192,255):
        for stop in (0,1,2,32,34,255):
            for state in (0,1,3,128,255):
                add('complete-first-stage-real-disable-reset-and-latch',byte_4184=mode,byte_244f=stop,byte_41e1=state)
    for control in (0,1,2,3):
        for elapsed in (0,1,99,100,101,254,255):
            for counter in (0,1,19,20,21,65534,65535):
                add('actual-counter-increment-saturation-and-reset',mode_8b38=control,
                    byte_3448=elapsed,word_3446=counter,byte_4184=128,byte_244f=32)
    return tuple(rows)

def context(source,case):
    require_case(case);return tuple(case['context'])

def memory(case):
    require_case(case);out=bytearray([0xA5])*RAM_SIZE
    for name,at,width in RAM_FIELDS:out[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(out)

def input_calibrations(case):
    require_case(case)
    mapping={row['address']:bytes(case[row['name']]) for row in contract.DECLARED['input_blobs']}
    mapping.update({at:bytes((case[name],)) for name,at in CONTROL_FIELDS})
    mapping[0x8D36]=bytes(case['thresholds_8d36'])
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
        raise ValueError('the request observation changes its complete immutable raw input or calibration')

def header(declared,image):
    source=declared['source'];cal=contract.CONTROLLED_CALIBRATION;bound=contract.BOUND_SPANS
    lines=['/* Complete raw inputs for one natural stock dispatcher entry. */',
        f'#define REQUEST_CALIBRATION_SIZE {sum(r["size"] for r in cal)}U',
        f'#define REQUEST_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        'static const struct span request_calibration[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in cal)+'};',
        'static const struct span request_bound[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in bound)+'};',
        'static const struct span request_ram_fields[] = {'+','.join('{%dU,%dU}'%(at,width) for name,at,width in RAM_FIELDS)+'};',
        f'struct path_case {{ uint32_t ram[{len(RAM_FIELDS)}];struct context context;uint8_t calibration[REQUEST_CALIBRATION_SIZE]; }};',
        'static const struct path_case request_cases[] = {']
    for case in declared['cases']:
        raw=context(source,case);ctx='{{'+','.join(f'0x{v:x}U' for v in raw[:15])+'},'+','.join(f'0x{v:x}U' for v in raw[15:])+'}'
        mapping=calibrations(source,image,case);blob=b''.join(mapping[r['address']] for r in cal)
        lines.append('{{'+','.join(f'0x{case[name]:x}U' for name,at,width in RAM_FIELDS)+'},'+ctx+',{' +
            ','.join(f'0x{v:02x}U' for v in blob)+'}},')
    return '\n'.join((*lines,'};','')).encode()
