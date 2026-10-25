"""Raw shared curve bytes, wrapped inputs, indexed channels and independent paired contexts."""
from copy import deepcopy
from kb import test_contract
from kb import centered_channel_duty_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(
    ('byte_2326',0x2326,1),('byte_248e',0x248E,1),('byte_24a7',0x24A7,1),
    ('prior_1a59',0x1A59,1),('word_2608',0x2608,2),
    ('word_1afc',0x1AFC,4),('word_1b00',0x1B00,4),('prior_16e8',0x16E8,4),
    ('prior_16ec',0x16EC,4),('byte_2772',0x2772,1),('byte_106f',0x106F,1),
    ('prior_1a7b',0x1A7B,1),('prior_1a7c',0x1A7C,1),
    ('prior_1a9c',0x1A9C,4),('prior_1aa0',0x1AA0,4),
    ('byte_28c2',0x28C2,1),('byte_246b',0x246B,1),('byte_248b',0x248B,1),
    ('byte_41fa',0x41FA,1),('byte_1108',0x1108,1),
    ('prior_2440',0x2440,1),('prior_2441',0x2441,1),('prior_9818',0x9818,4))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({row['name']:8 for row in contract.DECLARED['control_blobs']})
ARRAYS={'producer_context':(20,32),'consumer_context':(20,32),'implicit_curves':(16,8),
    'explicit_curves':(17,8),'explicit_axis':(8,8)}
BYTE_VALUES=(0,1,2,3,4,7,8,15,16,31,32,33,63,64,65,95,96,97,127,128,129,149,150,151,191,192,193,223,224,225,254,255)
WORD_VALUES=(0,1,127,128,255,256,257,32767,32768,65534,65535)
LONG_VALUES=(0,1,127,128,255,256,65535,65536,0x7FFFFF,0x800000,0x800001,0x8000FF,
    0x800100,0xFFFFFE,0xFFFFFF,0x1000000,0x17FFFFF,0x7FFFFFFF,0x80000000,0xFFFFFFFF)

def initial_context(phase):
    values=[*((0x18765430+i*0x01030507+phase*0x2030405)&0xFFFFFFFF for i in range(15)),
        0x12344321+phase,0x13579BDF+phase,0x2468ACE0+phase,0,0xB6C70000+phase]
    if phase==1:values[4]=0
    return values
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update(word_1afc=0x800000,word_1b00=0x800000,byte_246b=64,byte_1108=150,
    prior_16e8=0xA5A55A5A,prior_16ec=0x5A5AA5A5,prior_1a9c=0xB6C7D8E9,prior_1aa0=0xC7D8E9FA,
    prior_1a7b=0xA5,prior_1a7c=0x5A,prior_2440=0xB6,prior_2441=0xC7,prior_9818=0xDEADBEEF,
    rom_8615=0,rom_8616=0,rom_86b7=255,rom_86b8=242,rom_86b9=98,rom_86bd=50,
    rom_882f=0,rom_8830=0,rom_8dd8=128,
    producer_context=initial_context(0),consumer_context=initial_context(1),
    implicit_curves=[128]*16,explicit_curves=[128]*17,explicit_axis=list(range(0,256,32)))

def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,*ARRAYS,'index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())):
        raise ValueError('the centered duty input changes an exact raw scalar or supplies an intermediate result')
    for name,(count,bits) in ARRAYS.items():
        values=case[name]
        if type(values) is not list or len(values)!=count or any(type(v) is not int or not 0<=v<(1<<bits) for v in values):
            raise ValueError('the centered duty input changes a full independent context or exact shared physical curve span')
        if name.endswith('_context') and values[18]&~0x3F1:
            raise ValueError('the centered duty input changes its admitted complete I/M/Q/T context controls')

def cases(source,image):
    rows=[]
    def add(kind,**changes):
        value=deepcopy(DEFAULTS);value.update(changes);value.update(index=len(rows),kind=kind);rows.append(value)
    def channel(value):
        context=initial_context(1);context[4]=value;return context
    add('complete-centered-producer-and-indexed-consumer')
    stock={row['name']:image[row['address']] for row in source['control_blobs']}
    stock.update({row['name']:list(image[row['address']:row['address']+row['size']]) for row in source['input_blobs']})
    for selected in (0,1):add('complete-owned-stock-ROM-inputs',consumer_context=channel(selected),**stock)
    for phase in (0,1):
        field=contract.PHASES[phase]+'_context'
        for register in range(20):
            values=(0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF) if register!=18 else (0,1,0xF0,0x100,0x200,0x301,0x3F1)
            for raw in values:
                context=initial_context(phase);context[register]=raw;add('independent-complete-phase-CPU-field',**{field:context})
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):
                    context=initial_context(phase);context[18]=qm|interrupt|t
                    add('complete-phase-QM-interrupt-T',**{field:context})
    for selected in range(256):
        add('complete-uint8-indexed-channel',consumer_context=channel(selected))
    for name,at,width in RAM_FIELDS:
        for raw in BYTE_VALUES if width==1 else WORD_VALUES if width==2 else LONG_VALUES:
            for selected in (0,1):
                add('raw-input-and-overwritten-prior-publication',consumer_context=channel(selected),**{name:raw})
    for name in (key for key in WIDTHS if key.startswith('rom_')):
        for raw in range(256):
            add('raw-ROM-mode-override-coefficient',**{name:raw})
    for coordinate in range(256):
        for values in (list(range(16)),list(reversed(range(16)))):
            add('full-implicit-coordinate-and-directed-interpolation',byte_106f=coordinate,implicit_curves=values)
        for values in (list(range(17)),list(reversed(range(17)))):
            add('full-explicit-coordinate-and-directed-interpolation',rom_8616=1,byte_2772=coordinate,explicit_curves=values)
    for field in ('implicit_curves','explicit_curves'):
        for index in range(ARRAYS[field][0]):
            selected=min(index//8,1);local=min(index%8,7)
            coordinates=sorted({max(0,local*32-1),local*32,min(255,local*32+1),255 if index in (8,16) else local*32})
            for raw in (0,1,127,128,254,255):
                values=deepcopy(DEFAULTS[field]);values[index]=raw
                for coordinate in coordinates:
                    add('each-physical-cell-at-its-knot-and-adjacent-fractions',rom_8616=int(field=='explicit_curves'),
                        byte_106f=coordinate,byte_2772=coordinate,consumer_context=channel(selected),**{field:values})
    for index in range(8):
        for raw in BYTE_VALUES:
            values=deepcopy(DEFAULTS['explicit_axis']);values[index]=raw
            for coordinate in sorted({max(0,raw-1),raw,min(255,raw+1),index*32}):
                add('each-raw-axis-byte-and-rightmost-bracket-boundary',rom_8616=1,byte_2772=coordinate,explicit_axis=values)
    for selected in (0,1):
        for index in range(8):
            for raw in (0,1,127,128,254,255):
                values=[0]*16;values[selected*8+index]=raw
                add('held-other-source-cell-changes-actual-composite-and-final-duty',
                    implicit_curves=values,byte_106f=index*32,consumer_context=channel(selected))
    for selected in (0,1):
        for mode in (0,128):
            for sample in (0,127,128,129,254,255):
                for lower,upper in ((0,0),(0,127),(127,0),(127,127),(128,128),(255,255)):
                    for flags,counter in ((0,0),(0,1),(64,0),(64,1),(255,65535)):
                        add('complete-low-high-override-threshold-latch-counter-paths',
                            rom_8615=mode,byte_2326=sample,rom_8830=lower,rom_86b9=upper,
                            byte_248e=flags,word_2608=counter,consumer_context=channel(selected))
        for divisor in (0,1,2,127,128,129,254,255):
            field=('word_1afc','word_1b00')[selected]
            for raw in LONG_VALUES:
                add('independent-wrapped-signed-dividend-and-zero-fault-boundaries',
                    rom_8dd8=divisor,consumer_context=channel(selected),**{field:raw})
        for forced in (0,1,2,3,255):
            for enable in (0,64):
                for request in (0,2):
                    for condition in (0,1):
                        add('full-indexed-forced-enable-and-request-branches',byte_28c2=forced,
                            byte_246b=enable,byte_248b=request,byte_41fa=condition,consumer_context=channel(selected))
    return tuple(rows)

def context(source,case,phase):
    require_case(case)
    if type(phase) is not int or phase not in (0,1):raise ValueError('the quantity input changes its fixed phase identity')
    return tuple(case[contract.PHASES[phase]+'_context'])

def memory(case):
    require_case(case);out=bytearray([0xA5])*RAM_SIZE
    for name,at,width in RAM_FIELDS:out[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(out)

def input_calibrations(case):
    require_case(case)
    values={row['address']:bytes([case[row['name']]]) for row in contract.DECLARED['control_blobs']}
    values.update({row['address']:bytes(case[row['name']]) for row in contract.DECLARED['input_blobs']})
    return values

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
    lines=['/* Raw paired inputs only; no supplied intermediate quantity or expected output. */',
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
