"""Raw byte curves, exact flags and thresholds with independent complete phase contexts."""
from copy import deepcopy
from kb import test_contract
from kb import coasting_term_quantity_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(
    ('byte_1077',0x1077,1),('prior_1230',0x1230,2),('prior_126e',0x126E,2),
    ('prior_13ea',0x13EA,2),('byte_2458',0x2458,1),('byte_244f',0x244F,1),
    ('byte_110e',0x110E,1),('byte_4197',0x4197,1),('byte_106a',0x106A,1),
    ('byte_2473',0x2473,1),('byte_2466',0x2466,1),('byte_24a0',0x24A0,1),
    ('prior_1a7a',0x1A7A,1),('byte_11b2',0x11B2,1),('byte_22e4',0x22E4,1),
    ('byte_1071',0x1071,1),('word_1748',0x1748,2),('byte_2465',0x2465,1),
    *((f'diagnostic_{index}',0x5719+3*index,1) for index in (20,71,72,73,74,75,76,138,139,140)))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({f'rom_{address:04x}':8 for address in
    (0x8252,0x84D8,0x84D9,0x86FD,0x870C,0x8760,0x8761,0x8762,0x8763,0x8764,0x8765,0x8766)})
ARRAYS={'producer_context':(20,32),'consumer_context':(20,32),'source_curve':(8,8),'coasting_curve':(16,8)}
WORD_VALUES=(0,1,127,128,255,256,257,32766,32767,32768,32769,65280,65534,65535)
BYTE_VALUES=(0,1,2,3,4,5,6,7,8,12,13,14,15,16,25,26,27,31,32,33,59,60,61,62,63,64,65,124,125,126,127,128,129,144,145,146,223,224,225,254,255)

def initial_context(phase):
    return [*((0x18765430+i*0x01030507+phase*0x2030405)&0xFFFFFFFF for i in range(15)),
        0x12344321+phase,0x13579BDF+phase,0x2468ACE0+phase,0,0xB6C70000+phase]

DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update(prior_1230=0xA55A,prior_126e=0x5AA5,prior_1a7a=0xA5,
    byte_2458=32,byte_110e=64,byte_2466=128,byte_11b2=255,byte_1071=128,
    rom_8252=0,rom_84d8=255,rom_84d9=255,rom_86fd=13,rom_870c=68,
    rom_8760=26,rom_8761=13,rom_8762=62,rom_8763=6,rom_8764=145,rom_8765=125,rom_8766=15,
    producer_context=initial_context(0),consumer_context=initial_context(1),
    source_curve=list(range(1,9)),coasting_curve=[255]*16)

def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,*ARRAYS,'index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())):
        raise ValueError('the coasting input changes a complete raw scalar or supplies an intermediate quantity')
    for name,(count,bits) in ARRAYS.items():
        values=case[name]
        if type(values) is not list or len(values)!=count or any(type(v) is not int or not 0<=v<(1<<bits) for v in values):
            raise ValueError('the coasting input changes an exact independent raw curve or phase context')
        if name.endswith('_context') and values[18]&~0x3F1:
            raise ValueError('the coasting context changes its admitted complete I/M/Q/T controls')

def cases(source,image):
    rows=[]
    def add(kind,**changes):
        value=deepcopy(DEFAULTS);value.update(changes);value.update(index=len(rows),kind=kind);rows.append(value)
    add('actual-table-producer-and-complete-coasting-consumer')
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
    for field,at,width in RAM_FIELDS:
        for raw in BYTE_VALUES if width==1 else WORD_VALUES:
            add('independent-raw-input-or-overwritten-prior-output',**{field:raw})
    for field in (name for name in WIDTHS if name.startswith('rom_')):
        for raw in range(256):add('complete-raw-ROM-threshold-or-mode',**{field:raw})
    for coordinate in range(256):
        for values in ([0]*8,[255]*8,list(range(8)),list(reversed(range(8))),[0,255]*4,[255,0]*4):
            add('full-eight-byte-coordinate-directed-interpolation',byte_1077=coordinate,source_curve=values)
        for values in ([0]*16,[255]*16,list(range(16)),list(reversed(range(16))),[0,255]*8,[255,0]*8):
            add('full-consumer-byte-coordinate-directed-interpolation',byte_110e=coordinate,coasting_curve=values,
                rom_86fd=0,rom_8761=0,rom_8766=0,byte_2473=4)
    for index in range(8):
        for value in (0,1,127,128,254,255):
            curve=[0]*8;curve[index]=value
            add('held-other-source-cell-changes-actual-handoff-and-final-13ea',
                source_curve=curve,byte_1077=index*32,prior_13ea=0,word_1748=0)
    for index in range(16):
        for value in (0,1,127,128,254,255):
            curve=[255]*16;curve[index]=value
            add('held-other-consumer-cell-changes-actual-final-13ea',
                source_curve=[255]*8,coasting_curve=curve,byte_110e=index*4,rom_86fd=0,
                rom_8761=0,rom_8766=0,byte_2473=4,prior_13ea=0)
    for corrected in (0,128):
        for enabled in (0,128):
            for flags in (32,160):
                for speed in BYTE_VALUES:
                    for correction in (0,1,127,128,255):
                        add('correction-enable-signed-byte-and-saturation-boundaries',rom_870c=corrected,
                            byte_2466=enabled,byte_2458=flags,byte_110e=speed,rom_8252=correction)
    for active in (0,4):
        for decaying in (0,1):
            for prior in WORD_VALUES:
                for additive in WORD_VALUES:
                    add('coasting-latch-decay-and-full-unsigned-additive-boundaries',
                        byte_2473=active,byte_24a0=decaying,prior_13ea=prior,word_1748=additive)
    for field in ('byte_11b2','byte_22e4','byte_1071','byte_2465','byte_110e','rom_8760','rom_8761','rom_8764','rom_8765','rom_8766'):
        for raw in BYTE_VALUES:
            add('established-latch-maintenance-loss-and-real-decay',**dict({'byte_2473':4,'prior_13ea':1000},**{field:raw}))
    for field in ('rom_84d8','rom_84d9'):
        for raw in BYTE_VALUES:
            for prior in WORD_VALUES:
                for cap in (0,1,127,255):
                    add('exact-rise-cap-and-zero-decay-boundaries',**{field:raw,'prior_13ea':prior,
                        'source_curve':[cap]*8,'coasting_curve':[cap]*16,'byte_2473':4,'byte_24a0':int(field=='rom_84d8')})
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
