"""Raw optional timing surfaces, axes and ordinary/alternate controls with complete input state."""
from copy import deepcopy
from kb import test_contract
from kb import timing_additive_candidate_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('byte_2458',0x2458,1),('byte_23bd',0x23BD,1),('byte_23c5',0x23C5,1),
 ('byte_23f1',0x23F1,1),('byte_12dc',0x12DC,1),('byte_15ea',0x15EA,1),('byte_1a7d',0x1A7D,1),
 ('word_28b8',0x28B8,2),('word_28ba',0x28BA,2),('byte_41ab',0x41AB,1),
 ('byte_106f',0x106F,1),('word_1024',0x1024,2),('word_10ca',0x10CA,2),('word_1900',0x1900,2),
 ('byte_24d1',0x24D1,1),('byte_23ee',0x23EE,1),('prior_134c',0x134C,1),('prior_1348',0x1348,1),
 ('prior_134a',0x134A,1),('prior_12d4',0x12D4,1),('prior_1830',0x1830,1),('prior_9818',0x9818,4))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({row['name']:row['size']*8 for row in contract.DECLARED['control_blobs']})
WIDTHS['pattern']=8
ARRAYS={'context':(20,32),'source_surface':(64,16),'source_outer_axis':(8,16),
 'source_inner_axis':(8,16),'source_curve':(9,8),'source_byte_axis':(8,8)}
BYTE_VALUES=(0,1,2,15,31,32,33,63,64,65,99,100,101,126,127,128,129,254,255)
WORD_VALUES=(0,1,2,127,128,255,256,257,7349,7350,7351,8191,8192,8193,
 16383,16384,32767,32768,57344,65534,65535)
LONG_VALUES=(0,1,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFF)
DEFAULT_CONTEXT=[*((0x18765430+i*0x01030507)&0xFFFFFFFF for i in range(15)),
 0x12344321,0x13579BDF,0x2468ACE0,0,0xB6C70000]
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update(context=DEFAULT_CONTEXT,source_surface=[0]*64,
 source_outer_axis=[i*8192 for i in range(8)],source_inner_axis=[i*8192 for i in range(8)],
 source_curve=[255]*9,source_byte_axis=[i*32 for i in range(8)],
 pattern=0xA5,byte_1a7d=128,word_28b8=65535,word_28ba=65535,byte_41ab=64,word_1900=65535,
 rom_9012=7350,prior_134c=0xA5,prior_1348=0xB6,prior_134a=0xC7,prior_12d4=0xD8,
 prior_1830=0xE9,prior_9818=0xDEADBEEF)

def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,*ARRAYS,'index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())):
        raise ValueError('the timing additive input changes an exact raw scalar or supplies a live result')
    for name,(count,bits) in ARRAYS.items():
        values=case[name]
        if type(values) is not list or len(values)!=count or any(type(v) is not int or not 0<=v<(1<<bits) for v in values):
            raise ValueError('the timing additive input truncates a complete raw CPU, surface, physical curve or axis')
    if case['context'][18]&~0x3F1:
        raise ValueError('the timing additive input changes complete admitted I/M/Q/T controls')

def cases(source,image):
    rows=[]
    def add(kind,**changes):
        value=deepcopy(DEFAULTS);value.update(changes);value.update(index=len(rows),kind=kind);rows.append(value)
    add('complete-published-live-timing-additive-candidate')
    stock={row['name']:int.from_bytes(image[row['address']:row['address']+row['size']],'big') for row in source['control_blobs']}
    for name,address,count,width in (('source_surface',0xC50E,64,2),('source_outer_axis',0x1461A,8,2),
            ('source_inner_axis',0x1464A,8,2),('source_curve',0x11F02,9,1),('source_byte_axis',0x11EEA,8,1)):
        stock[name]=[int.from_bytes(image[address+i*width:address+(i+1)*width],'big') for i in range(count)]
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
    for threshold in WORD_VALUES:
        for smaller in sorted({max(0,threshold-1),threshold,min(65535,threshold+1)}):
            add('actual-unsigned-threshold-equality-and-smaller-word-inputs',rom_9012=threshold,
                word_28b8=smaller,word_28ba=65535)
            add('opposite-smaller-word-selection',rom_9012=threshold,word_28ba=smaller,word_28b8=65535)
    for index in range(64):
        for raw in (0,1,127,128,255,256,32768,65535):
            surface=[0]*64;surface[index]=raw
            add('held-other-physical-surface-word-and-actual-additive-result',source_surface=surface,
                word_10ca=(index//8)*8192,word_1024=(index%8)*8192)
    for index in range(9):
        for raw in (0,1,127,128,254,255):
            curve=[0]*9;curve[index]=raw
            add('held-other-active-curve-byte-or-ninth-physical-guard',source_curve=curve,
                source_surface=[255]*64,byte_106f=min(index,7)*32)
    word_patterns=([i*8192 for i in range(8)],[0]*8,[65535]*8,
        [65535-i*8192 for i in range(8)],[0,65535,0,32768,32767,1,65534,65535],
        [0,1,1,128,128,32768,65535,65535])
    directed_surfaces=([i*1000 for i in range(64)],[65535-i*1000 for i in range(64)])
    for outer_coordinate,inner_coordinate in ((0,0),(1,0),(0,1),(1,1),(8191,8191),
            (8192,8192),(8193,8193),(65535,0),(0,65535),(65535,65535)):
        for surface in directed_surfaces:
            add('all-four-actual-bilinear-kernel-fraction-paths',source_surface=list(surface),
                word_10ca=outer_coordinate,word_1024=inner_coordinate)
    for field,coordinate_field in (('source_outer_axis','word_10ca'),('source_inner_axis','word_1024')):
        for axis in word_patterns:
            coordinates=set(WORD_VALUES)
            for knot in axis:coordinates.update((max(0,knot-1),knot,min(65535,knot+1)))
            for coordinate in sorted(coordinates):
                for surface in directed_surfaces:
                    add('rightmost-unsigned-nonmonotonic-word-axis-and-actual-inner-stack-word',
                        source_surface=list(surface),**dict({'word_10ca':8193,'word_1024':8193},
                        **{field:list(axis),coordinate_field:coordinate}))
        for index in range(8):
            for raw in WORD_VALUES:
                axis=[i*8192 for i in range(8)];axis[index]=raw
                for coordinate in sorted({max(0,raw-1),raw,min(65535,raw+1)}):
                    add('independent-word-axis-knot-and-adjacent-coordinate',
                        **{field:axis,coordinate_field:coordinate})
    byte_patterns=([i*32 for i in range(8)],[0]*8,[255]*8,
        [255-i*32 for i in range(8)],[0,255,0,128,127,1,254,255],[0,1,1,128,128,254,255,255])
    for axis in byte_patterns:
        for coordinate in range(256):
            add('complete-byte-coordinate-and-rightmost-axis-curve',source_byte_axis=list(axis),
                source_curve=[i*31 for i in range(9)],byte_106f=coordinate)
            add('descending-physical-byte-curve',source_byte_axis=list(axis),
                source_curve=[255-i*31 for i in range(9)],byte_106f=coordinate)
    for surface in (0,1,127,128,254,255,256,32768,65535):
        for factor in (0,1,32767,32768,65535):
            for curve in (0,1,127,128,254,255):
                add('unsigned-product-wide-division-and-byte-cap',source_surface=[surface]*64,
                    source_curve=[curve]*9,word_1900=factor)
    for mode in (0,32):
        for first,subtract,correction,earlier,adjustment,base in ((0,0,0,0,0,128),
                (255,0,127,0,0,255),(0,255,128,255,255,0),(127,128,255,127,128,129)):
            add('normal-and-alternate-complete-signed-compositor-boundaries',byte_2458=mode,
                byte_23bd=first,byte_23c5=subtract,byte_23f1=correction,
                byte_12dc=earlier,byte_15ea=adjustment,byte_1a7d=base,byte_23ee=correction)
        for prior in BYTE_VALUES:
            add('independent-prior134A-on-active-or-alternate-path',byte_2458=mode,prior_134a=prior)
            add('independent-prior134A-on-disabled-term-path',byte_2458=mode,byte_41ab=0,prior_134a=prior)
    for raw in BYTE_VALUES:
        add('ninth-byte-zero-weight-actual-endpoint',source_curve=[0]*8+[raw],byte_106f=224)
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
    for name,address,width in (('source_surface',0xC50E,2),('source_outer_axis',0x1461A,2),
            ('source_inner_axis',0x1464A,2),('source_curve',0x11F02,1),('source_byte_axis',0x11EEA,1)):
        mapping[address]=b''.join(value.to_bytes(width,'big') for value in case[name])
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
        raise ValueError('the timing additive candidate changes a complete immutable raw input or calibration')

def header(declared,image):
    source=declared['source'];cal,bound=contract.CONTROLLED_CALIBRATION,contract.BOUND_SPANS
    lines=['/* Complete raw inputs only; no supplied live candidate or expected output. */',
        f'#define ADDITIVE_CALIBRATION_SIZE {sum(r["size"] for r in cal)}U',
        f'#define ADDITIVE_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        'static const struct span additive_calibration[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in cal)+'};',
        'static const struct span additive_bound[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in bound)+'};',
        'struct path_case { '+''.join('uint32_t '+name+';' for name,at,width in RAM_FIELDS)+
        'struct context context;uint8_t pattern,calibration[ADDITIVE_CALIBRATION_SIZE]; };',
        'static const struct path_case additive_cases[] = {']
    for case in declared['cases']:
        raw=context(source,case)
        ctx='{{'+','.join(f'0x{v:x}U' for v in raw[:15])+'},'+','.join(f'0x{v:x}U' for v in raw[15:])+'}'
        mapping=calibrations(source,image,case);blob=b''.join(mapping[row['address']] for row in cal)
        lines.append('{'+','.join(f'0x{case[name]:x}U' for name,at,width in RAM_FIELDS)+','+ctx+
            f',0x{case["pattern"]:02x}U,'+'{'+','.join(f'0x{v:02x}U' for v in blob)+'}},')
    return '\n'.join((*lines,'};','')).encode()
