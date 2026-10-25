"""Complete raw formal arguments, source arrays and controls for the upstream curve caller."""
from copy import deepcopy
from kb import test_contract,upstream_curve_coordinate_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('prior_3228',0x3228,4),('prior_9818',0x9818,4))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({r['name']:r['size']*8 for r in contract.DECLARED['control_blobs']})
WIDTHS['pattern']=8
ARRAYS={'context':(20,32),'source_curve':(9,16),'source_axis':(8,16),
    'output_curve':(17,16),'output_axis':(16,16)}
WORD_VALUES=(0,1,2,255,256,257,32767,32768,32769,65534,65535)
DEFAULT_CONTEXT=[*((0x18765430+i*0x01030507)&0xFFFFFFFF for i in range(15)),
    0x12344321,0x13579BDF,0x2468ACE0,0,0]
DEFAULT_CONTEXT[4:8]=[1000,0,0,0]
DEFAULTS=dict(prior_3228=0xA5B6C7D8,prior_9818=0xDEADBEEF,pattern=0xA5,
    context=DEFAULT_CONTEXT,source_curve=[0]*9,source_axis=[i*8192 for i in range(8)],
    output_curve=[0]*15+[255,0],output_axis=[i*4096 for i in range(14)]+[65335,65535],
    rom_8832=1,rom_8a30=1,rom_8a34=10,rom_8a35=10,rom_8a36=10)


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,*ARRAYS,'index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())):
        raise ValueError('the upstream-coordinate input changes a raw scalar or supplies a live result')
    for name,(count,bits) in ARRAYS.items():
        values=case[name]
        if (type(values) is not list or len(values)!=count
                or any(type(v) is not int or not 0<=v<(1<<bits) for v in values)):
            raise ValueError('the upstream-coordinate input truncates complete CPU, curve, guard or axis bytes')
    if case['context'][18]&~0x3F1:
        raise ValueError('the upstream-coordinate input changes admitted I/M/Q/T controls')


def raw_context(H=1000,selector=0,initial_long=0,local_byte=0,fifth_word=0):
    context=list(DEFAULT_CONTEXT)
    for at,value in ((4,H),(5,selector),(6,initial_long),(7,local_byte),(19,fifth_word)):
        context[at]=value&0xFFFFFFFF
    return context


def cases(source,image):
    rows=[]
    def add(kind,**changes):
        value=deepcopy(DEFAULTS);value.update(changes);value.update(index=len(rows),kind=kind);rows.append(value)
    add('complete-natural-upstream-coordinate-caller')
    stock={r['name']:int.from_bytes(image[r['address']:r['address']+r['size']],'big') for r in source['control_blobs']}
    for r in source['input_blobs']:
        stock[r['name']]=[int.from_bytes(image[i:i+2],'big') for i in range(r['address'],r['address']+r['size'],2)]
    add('complete-stock-calibration-input',**stock)
    for index in range(8):
        for value in (0,10000):
            curve=[0]*9;curve[index]=value
            add('source-word-real-coordinate-and-long-output-causality',source_curve=curve,
                context=raw_context(fifth_word=index*32))
    for high in (0,0x7FFFFF00,0x80000000,0xFFFFFF00):
        for low in range(256):
            add('full-fifth-word-and-complete-source-byte-domain',context=raw_context(fifth_word=high|low),
                source_curve=[0,65535,1,32768,32767,65534,255,65535,0])
    for local in (0,1,127,128,255):
        for adjusted in (-35269,-35268,-35267,-2501,-2500,-2499,0,30266,30267,30268):
            quotient=adjusted+local*50
            add('initial-signed-quotient-word-clamps-and-byte-extension',
                context=raw_context(initial_long=quotient*20000,local_byte=0xA5B60000|local))
    for raw in (0,1,19999,20000,20001,0x7FFFFFFF,0x80000000,0x80000001,0xFFFFFFFF):
        add('complete-initial-signed-long-boundaries',context=raw_context(initial_long=raw))
    for factor in (0,1,2,4,5,10,127,128,255):
        for word in (0,1,2500,13106,13107,13108,32767):
            add('full-B-product-shift-and-sentinel-before-word-extension',rom_8a30=factor,
                context=raw_context(initial_long=(word-2500)*20000),source_curve=[10000]*9)
    for H in (0,1,2,20,255,256,1000,32767,32768,65535):
        for value in WORD_VALUES:
            for factor in (0,1,2,127,128,255):
                add('conditional-ratio-division-bypass-negative-quotient-and-guard',
                    context=raw_context(H=0xA5B60000|H),source_curve=[value]*9,rom_8832=factor)
    for value,factor in ((65534,1),(65535,1),(32768,2),(32769,2)):
        add('exact-negative65535-quotient-guard-neighbors',context=raw_context(H=20),
            source_curve=[value]*9,rom_8832=factor)
    for knot in range(16):
        for coordinate in sorted({max(0,knot*4096-1),knot*4096,min(65535,knot*4096+1)}):
            add('full-consumer-word-coordinate-knot-boundaries',context=raw_context(H=20),
                source_curve=[65535-coordinate]*9,output_axis=[i*4096 for i in range(16)],
                output_curve=[0,65535,1,32768,32767,65534,255,256]*2+[0])
    for value in (0,1,254,255,256,32767,32768,65535):
        add('complete-consumer-return-before-inverse-weight-guard',output_curve=[value]*17,source_curve=[10000]*9)
    for name,count in (('source_axis',8),('output_axis',16)):
        for axis in ([0]*count,[65535]*count,[65535,32768,0,1,32767,65534,1,65535]*(count//8)):
            for word in (0,1,127,128,255):
                add('duplicate-nonmonotonic-and-exact-axis-boundaries',**{name:axis},
                    context=raw_context(H=20,fifth_word=word),source_curve=[65535-word*257]*9)
    for axis,fifth in (([255]+[65535]*7,1),([1]+[65281]*7,255)):
        add('source-positive-bracket-minimum-and-maximum-word-fractions',source_axis=axis,
            context=raw_context(H=20,fifth_word=fifth),source_curve=[0,65535]*4+[0])
    for value in (65534,1):
        add('consumer-positive-bracket-minimum-and-maximum-word-fractions',
            output_axis=[0]+[65535]*15,source_curve=[value]*9,context=raw_context(H=20),
            output_curve=[0,65535]*8+[0])
    for name,count in (('source_curve',9),('output_curve',17)):
        for curve in ([0]*count,[65535]*count,[65535 if i%2 else 0 for i in range(count)],
                      [0 if i%2 else 65535 for i in range(count)]):
            for raw in (0,1,31,32,33,223,224,255):
                add('both-interpolation-directions-and-full-word-returns',**{name:curve},
                    context=raw_context(H=20,fifth_word=raw))
    for name,count in (('source_curve',9),('output_curve',17)):
        for guard in WORD_VALUES:
            curve=list(DEFAULTS[name]);curve[-1]=guard
            add('physical-last-guard-zero-arithmetic-weight',**{name:curve},
                context=raw_context(fifth_word=224))
    for selector in range(256):
        add('complete-selector-byte-and-cap-four',context=raw_context(selector=0xA5B60000|selector),
            source_curve=[10000]*9)
    for selector,name in ((1,'rom_8a35'),(2,'rom_8a36'),(3,'rom_8a34')):
        for raw in range(256):
            add('full-signed-coefficient-load-and-actual-unsigned-extension',**{name:raw},
                context=raw_context(selector=selector),source_curve=[10000]*9)
    for prior in (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
        for value in (0,10000):add('overwritten-long-output-full-state-invariance',prior_3228=prior,source_curve=[value]*9)
    for field in range(20):
        values=(0,1,0xF0,0x101,0x201,0x301,0x3F1) if field==18 else (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF)
        for raw in values:
            context=list(DEFAULT_CONTEXT);context[field]=raw
            add('independent-complete-context-field',context=context,source_curve=[10000]*9)
    for pattern in (0,1,0x5A,0x80,0xFF):add('complete-unmodified-RAM-pattern',pattern=pattern)
    return tuple(rows)


def context(source,case):
    require_case(case)
    return tuple(case['context'])


def memory(case):
    require_case(case);out=bytearray([case['pattern']])*RAM_SIZE
    for name,at,width in RAM_FIELDS:out[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(out)


def input_calibrations(case):
    require_case(case)
    mapping={r['address']:case[r['name']].to_bytes(r['size'],'big') for r in contract.DECLARED['control_blobs']}
    for r in contract.DECLARED['input_blobs']:
        mapping[r['address']]=b''.join(v.to_bytes(2,'big') for v in case[r['name']])
    return mapping


def calibrations(source,image,case):
    fixture,_=contract.fixture_for_case(source,image,case)
    return {r['address']:fixture[r['address']:r['address']+r['size']] for r in contract.CONTROLLED_CALIBRATION}


def require_input(source,image,case,observed):
    wanted=calibrations(source,image,case)
    if (observed['entry']!=contract.ENTRY or not test_contract.exact(observed['context'],context(source,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],wanted)
            or not test_contract.exact(observed['calibration_after'],wanted)):
        raise ValueError('the upstream-coordinate entry changes complete immutable arguments, RAM or calibration')


def header(declared,image):
    source=declared['source'];cal,bound=contract.CONTROLLED_CALIBRATION,contract.BOUND_SPANS
    lines=['/* Complete raw formal arguments and ROM/RAM inputs only. */',
        f'#define UPSTREAM_CURVE_CALIBRATION_SIZE {sum(r["size"] for r in cal)}U',
        f'#define UPSTREAM_CURVE_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        'static const struct span upstream_curve_calibration[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in cal)+'};',
        'static const struct span upstream_curve_bound[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in bound)+'};',
        'struct path_case { '+''.join('uint32_t '+name+';' for name,at,width in RAM_FIELDS)+
        'struct context context;uint8_t pattern,calibration[UPSTREAM_CURVE_CALIBRATION_SIZE]; };',
        'static const struct path_case upstream_curve_cases[] = {']
    for case in declared['cases']:
        raw=context(source,case)
        ctx='{{'+','.join(f'0x{v:x}U' for v in raw[:15])+'},'+','.join(f'0x{v:x}U' for v in raw[15:])+'}'
        mapping=calibrations(source,image,case);blob=b''.join(mapping[row['address']] for row in cal)
        lines.append('{'+','.join(f'0x{case[name]:x}U' for name,at,width in RAM_FIELDS)+','+ctx+
            f',0x{case["pattern"]:02x}U,'+'{'+','.join(f'0x{v:02x}U' for v in blob)+'}},')
    return '\n'.join((*lines,'};','')).encode()
