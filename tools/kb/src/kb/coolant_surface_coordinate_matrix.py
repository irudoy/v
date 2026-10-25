"""Raw complete inputs for the actual coolant-coordinate caller and both lookups."""
from copy import deepcopy
from kb import coolant_surface_coordinate_contract as contract,test_contract

RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('coolant_snapshot',0x106F,1),('inner_snapshot',0x10F0,1),
    ('word_1222',0x1222,2),('prior_1652',0x1652,2))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}|{'pattern':8}
ARRAYS={'context':(20,32),'surface':(64,8),'word_curve':(8,16)}
BYTE_VALUES=(0,1,2,15,16,31,32,33,63,64,65,127,128,129,223,224,225,254,255)
WORD_VALUES=(0,1,255,256,257,511,512,513,1023,1024,1025,1791,1792,1793,
    2047,2048,2049,32767,32768,32769,65534,65535)
DEFAULT_CONTEXT=[*((0x18765430+i*0x01030507)&0xFFFFFFFF for i in range(15)),
    0x12344321,0x13579BDF,0x2468ACE0,0,0xB6C70000]
DEFAULTS=dict(coolant_snapshot=0,inner_snapshot=0,word_1222=0,prior_1652=0xA5B6,
    pattern=0xA5,context=DEFAULT_CONTEXT,surface=[128+row*8+column for row in range(8) for column in range(8)],
    word_curve=[128]*8)


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,*ARRAYS,'index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())):
        raise ValueError('the coolant-coordinate input changes a raw scalar or supplies a live result')
    for name,(count,bits) in ARRAYS.items():
        values=case[name]
        if (type(values) is not list or len(values)!=count
                or any(type(v) is not int or not 0<=v<(1<<bits) for v in values)):
            raise ValueError('the coolant-coordinate input truncates a complete CPU, surface or word curve')
    if case['context'][18]&~0x3F1:
        raise ValueError('the coolant-coordinate input changes admitted I/M/Q/T controls')


def cases(source,image):
    rows=[]
    def add(kind,**changes):
        value=deepcopy(DEFAULTS);value.update(changes);value.update(index=len(rows),kind=kind);rows.append(value)
    add('complete-natural-coolant-coordinate-caller')
    stock={}
    for r in source['input_blobs']:
        width=ARRAYS[r['name']][1]//8
        stock[r['name']]=[int.from_bytes(image[i:i+width],'big') for i in range(r['address'],r['address']+r['size'],width)]
    add('complete-stock-calibration-input',**stock)
    for raw in range(256):
        for fixed in (0,1,32,223,224,255):
            add('complete-coolant-byte-domain',coolant_snapshot=raw,inner_snapshot=fixed)
            add('complete-inner-byte-domain',coolant_snapshot=fixed,inner_snapshot=raw)
    for raw in WORD_VALUES:
        for coefficient in (0,1,127,128,129,255):
            add('word-source-extension-shift-cap-and-output',word_1222=raw,surface=[coefficient]*64,
                word_curve=[65535]*8)
    for knot in range(8):
        for raw in sorted({max(0,knot*256-1),knot*256,min(65535,knot*256+1)}):
            add('word-implicit-knot-and-endpoint',word_1222=raw,
                word_curve=[0,65535,1,32768,32767,65534,255,65535])
    for raw in (0,1,32767,32768,32769,65535):
        for coordinate in (0,1,255,256,1791,1792,2047,2048,65535):
            add('full-signed-word-return-before-extension',word_1222=coordinate,word_curve=[raw]*8)
    surfaces=([0]*64,[1]*64,[127]*64,[128]*64,[255]*64,
        [255 if i%2 else 0 for i in range(64)],[0 if i%2 else 255 for i in range(64)],
        [255-row*16-column for row in range(8) for column in range(8)])
    for surface in surfaces:
        for outer in (0,1,31,32,33,223,224,255):
            for inner in (0,1,31,32,33,223,224,255):
                add('all-bilinear-directions-fraction-modes-and-full-returns',surface=surface,
                    coolant_snapshot=outer,inner_snapshot=inner)
    for index in range(64):
        for raw in (0,255):
            surface=[128]*64;surface[index]=raw
            add('physical-surface-cell-publication',surface=surface,
                coolant_snapshot=(index//8)*32,inner_snapshot=(index%8)*32)
    for prior in (0,1,32767,32768,65535):
        for raw in (0,32,224,255):
            add('overwritten-output-full-state-invariance',prior_1652=prior,coolant_snapshot=raw)
    for field in range(20):
        values=(0,1,0xF0,0x101,0x201,0x301,0x3F1) if field==18 else (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF)
        for raw in values:
            context=list(DEFAULT_CONTEXT);context[field]=raw
            add('independent-complete-context-field',context=context,coolant_snapshot=223,inner_snapshot=223,
                word_1222=1791)
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
    require_case(case);mapping={}
    for r in contract.DECLARED['input_blobs']:
        width=ARRAYS[r['name']][1]//8
        mapping[r['address']]=b''.join(v.to_bytes(width,'big') for v in case[r['name']])
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
        raise ValueError('the coolant-coordinate entry changes complete immutable inputs or calibration')


def header(declared,image):
    source=declared['source'];cal,bound=contract.CONTROLLED_CALIBRATION,contract.BOUND_SPANS
    lines=['/* Complete raw inputs only; no supplied live coordinate or expected output. */',
        f'#define COOLANT_SURFACE_CALIBRATION_SIZE {sum(r["size"] for r in cal)}U',
        f'#define COOLANT_SURFACE_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        'static const struct span coolant_surface_calibration[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in cal)+'};',
        'static const struct span coolant_surface_bound[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in bound)+'};',
        'struct path_case { '+''.join('uint32_t '+name+';' for name,at,width in RAM_FIELDS)+
        'struct context context;uint8_t pattern,calibration[COOLANT_SURFACE_CALIBRATION_SIZE]; };',
        'static const struct path_case coolant_surface_cases[] = {']
    for case in declared['cases']:
        raw=context(source,case)
        ctx='{{'+','.join(f'0x{v:x}U' for v in raw[:15])+'},'+','.join(f'0x{v:x}U' for v in raw[15:])+'}'
        mapping=calibrations(source,image,case);blob=b''.join(mapping[row['address']] for row in cal)
        lines.append('{'+','.join(f'0x{case[name]:x}U' for name,at,width in RAM_FIELDS)+','+ctx+
            f',0x{case["pattern"]:02x}U,'+'{'+','.join(f'0x{v:02x}U' for v in blob)+'}},')
    return '\n'.join((*lines,'};','')).encode()
