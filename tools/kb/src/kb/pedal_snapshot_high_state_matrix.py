"""Input-only paired snapshot/comparator cases with complete raw RAM and both contexts."""
from copy import deepcopy
from kb import test_contract,coherent_copy_matrix as coherent
from kb import pedal_snapshot_high_state_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('word_2668',0x2668,2),('word_266a',0x266A,2),('word_2672',0x2672,2),
    ('word_2674',0x2674,2),('word_266c',0x266C,2),('word_266e',0x266E,2),('word_2670',0x2670,2),
    ('byte_110e',0x110E,1),('byte_245e',0x245E,1),('byte_24b6',0x24B6,1),
    ('byte_24b4',0x24B4,1),('byte_24e8',0x24E8,1),('byte_24d7',0x24D7,1),
    ('byte_2470',0x2470,1),('byte_246d',0x246D,1),('byte_246a',0x246A,1),
    ('byte_424f',0x424F,1),('record_0',0x5719,1),('byte_2471',0x2471,1),
    ('byte_11ae',0x11AE,1),('byte_10ec',0x10EC,1),('byte_4184',0x4184,1),
    ('byte_2559',0x2559,1),('byte_1071',0x1071,1),('word_1024',0x1024,2),
    ('byte_42b4',0x42B4,1),('byte_24c6',0x24C6,1),('word_1a42',0x1A42,2),
    ('neighbor_2676',0x2676,2),('neighbor_2678',0x2678,2))
WIDTHS={name:8*size for name,address,size in RAM_FIELDS}
WIDTHS.update({r['name']:8*r['size'] for r in contract.DECLARED['control_blobs']})
WORD_VALUES=(0,1,127,128,255,256,527,528,529,609,610,611,8191,8192,32767,32768,57343,57344,65534,65535)
DEFAULTS=dict(word_2668=0x1234,word_266a=0x5678,word_2672=610,word_2674=0xBEEF,
    word_266c=0x9ABC,word_266e=0xDEF0,word_2670=0x2468,byte_110e=0,byte_245e=0,
    byte_24b6=0,byte_24b4=0,byte_24e8=0,byte_24d7=0,byte_2470=0,byte_246d=0,
    byte_246a=0,byte_424f=0,record_0=0,byte_2471=0,byte_11ae=128,byte_10ec=32,
    byte_4184=0,byte_2559=0,byte_1071=0,word_1024=1000,byte_42b4=0,byte_24c6=0,
    word_1a42=0xAAAA,neighbor_2676=0x7654,neighbor_2678=0x3210,pattern=0xA5,
    snapshot_variant=0,snapshot_t=0,snapshot_block=bytes((3+i*17)&255 for i in range(260)),
    context=[0x18765430,0x19795937,0x1A7C5E3E,0x1B7F6345,0xAB123456,
             0x1D856D53,0x1E88725A,0x1F8B7761,0x208E7C68,0x2191816F,
             0x22948676,0x23978B7D,0x249A9084,0x259D958B,0x26A09A92,
             0x12345721,0x13579BDF,0x2468ACE0,0,0xB6C70000])
DEFAULTS.update({r['name']:int(r['stock_hex'],16) for r in contract.DECLARED['control_blobs']})
WINDOW=next(w for w in coherent.WINDOWS if w.entry==0x20FA4 and w.call==0x20FCC)


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'pattern','snapshot_variant','snapshot_t',
            'snapshot_block','threshold_curve','context','index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or type(case['pattern']) is not int or not 0<=case['pattern']<=255
            or type(case['snapshot_variant']) is not int or case['snapshot_variant'] not in (0,1)
            or type(case['snapshot_t']) is not int or case['snapshot_t'] not in (0,1)
            or type(case['snapshot_block']) is not bytes or len(case['snapshot_block'])!=260
            or type(case['threshold_curve']) is not bytes or len(case['threshold_curve'])!=16
            or any(type(case[name]) is not int or not 0<=case[name]<1<<bits for name,bits in WIDTHS.items())):
        raise ValueError('the paired pedal source changes complete typed input-only RAM/ROM state')
    if (type(case['context']) is not list or len(case['context'])!=20
            or any(type(v) is not int or not 0<=v<=0xFFFFFFFF for v in case['context'])
            or case['context'][18]&~0x3F1):
        raise ValueError('the paired pedal source changes complete independent comparator CPU/I/M/Q/T')


def snapshot_case(case):
    require_case(case)
    return dict(variant=case['snapshot_variant'],t=case['snapshot_t'])


def snapshot_context(case):
    value=snapshot_case(case)
    return (*coherent.incoming(WINDOW,value),*coherent.special(value),case['snapshot_t'])


def context(source,case):
    require_case(case);return tuple(case['context'])


def memory(case):
    require_case(case);out=bytearray([case['pattern']])*65536
    for name,address,size in RAM_FIELDS:out[address:address+size]=case[name].to_bytes(size,'big')
    out[0x277E:0x2882]=case['snapshot_block']
    return bytes(out)


def input_calibrations(case):
    require_case(case)
    return {**{r['address']:case[r['name']].to_bytes(r['size'],'big') for r in contract.DECLARED['control_blobs']},
            0x1473A:case['threshold_curve']}


def calibrations(source,image,case):
    fixture,_=contract.fixture_for_case(source,image,case)
    return {r['address']:fixture[r['address']:r['address']+r['size']] for r in contract.CONTROLLED_CALIBRATION}


def cases(source,image):
    defaults=deepcopy(DEFAULTS);defaults['threshold_curve']=image[0x1473A:0x1474A];rows=[]
    def add(kind,**changes):
        row=deepcopy(defaults);row.update(changes);row.update(index=len(rows),kind=kind);rows.append(row)
    add('complete-existing-prefix-and-natural-comparator')
    for raw in (0,527,528,529,609,610,611,65535):
        for previous in (0,128):
            add('held-other-real-pedal-word-to-actual-high-state',word_2672=raw,byte_246d=previous)
    for variant in (0,1):
        for t in (0,1):add('retained-existing-snapshot-entry-context',snapshot_variant=variant,snapshot_t=t)
    for register in range(20):
        values=(0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF)
        if register==18:values=(0,1,0xF0,0x100,0x200,0x301,0x3F1)
        for value in values:
            incoming=list(defaults['context']);incoming[register]=value
            add('independent-complete-comparator-context-field',context=incoming)
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):
                incoming=list(defaults['context']);incoming[18]=qm|interrupt|t
                add('complete-comparator-QM-interrupt-T',context=incoming)
    for name,address,size in RAM_FIELDS:
        for value in (range(256) if size==1 else WORD_VALUES):
            add('independent-actual-RAM-field',**{name:value})
    for lane in range(260):
        for value in (0,255):
            block=bytearray(defaults['snapshot_block']);block[lane]=value
            add('complete-existing-snapshot-block-physical-lane',snapshot_block=bytes(block))
    for row in contract.DECLARED['control_blobs']:
        for raw in (range(256) if row['size']==1 else WORD_VALUES):
            add('independent-actual-ROM-control',**{row['name']:raw})
    for mode in (0,128):
        for guard in (0,64):
            for old_high in (0,64):
                for timer in (0,1):
                    for previous in (0,2):
                        for raw in (0,528,610,65535):
                            add('pedal-mode-guard-hysteresis-and-timer',rom_870c=mode,byte_245e=guard,
                                byte_24b4=old_high,byte_24e8=timer,byte_24b6=previous,word_2672=raw)
    for mode in (0,128):
        for timer in (0,1):
            for state in (0,4):
                for inhibit in (0,8):
                    for record in (0,128):
                        for config in (0,128):
                            add('complete-request-timer-inhibit-record-and-configuration-precedence',rom_870c=mode,
                                byte_24d7=timer,byte_2470=state,byte_424f=inhibit,record_0=record,rom_8b3f=config)
    for cell in range(8):
        for raw in (0,65535):
            table=bytearray(defaults['threshold_curve']);table[2*cell:2*cell+2]=raw.to_bytes(2,'big')
            add('exact-physical-uniform-curve-word',rom_870c=128,byte_110e=4*cell,threshold_curve=bytes(table))
    for sample in (0,1,3,4,7,8,27,28,31,32,127,128,255):
        add('uniform-curve-knots-interiors-and-saturated-coordinate',rom_870c=128,byte_110e=sample)
    for mode in (0,4):
        for temperature in (0,1,29,30,123,124,125,133,134,135,255):
            for companion in (0,5,6,7,8,77,78,79,107,108,109,136,137,138,155,156,255):
                add('ordered-temperature-companion-status-branches',rom_870d=mode,
                    byte_11ae=temperature,byte_10ec=companion)
    add('temperature-later-upper-branch-with-independent-earlier-controls',rom_870d=4,
        rom_88b0=255,rom_8d97=255,byte_11ae=135,byte_10ec=138)
    add('retained-high-temperature-latch',byte_2471=64,rom_88b4=255)
    add('new-inhibit-flag-and-final-short-circuit-boundary',rom_8c74=0,rom_9536=0)
    add('retained-inhibit-flag-and-final-short-circuit-boundary',byte_2470=2,rom_8c75=0,rom_9536=0)
    for throttle in (0,1,127,128,253,254,255):
        for speed in (0,1,65534,65535):
            for initial in (0,2):
                add('complete-final-hysteresis-and-inhibit-precedence',byte_1071=throttle,
                    word_1024=speed,byte_2470=initial)
    for pattern in (0,1,0x5A,0x80,0xFF):add('complete-other-RAM-preservation',pattern=pattern)
    for row in rows:require_case(row)
    return tuple(rows)


def require_input(source,image,case,observed):
    wanted=calibrations(source,image,case)
    if (observed['snapshot_context']!=snapshot_context(case) or observed['context']!=context(source,case)
            or observed['memory_before']!=memory(case)
            or not test_contract.exact(observed['calibration_before'],wanted)
            or not test_contract.exact(observed['calibration_after'],wanted)):
        raise ValueError('the paired pedal source changes complete immutable physical inputs')


def header(declared,image):
    calibration=contract.CONTROLLED_CALIBRATION;bound=contract.BOUND_SPANS;blobs=[];indices={};rows=[]
    for case in declared['cases']:
        mapping=calibrations(declared['source'],image,case);blob=b''.join(mapping[r['address']] for r in calibration)
        if blob not in indices:indices[blob]=len(blobs);blobs.append(blob)
        legacy=snapshot_context(case);incoming=context(declared['source'],case)
        legacy_text='{{'+','.join(f'0x{v:x}U' for v in legacy[:15])+'},'+','.join(f'0x{v:x}U' for v in legacy[15:])+'}'
        incoming_text='{{'+','.join(f'0x{v:x}U' for v in incoming[:15])+'},'+','.join(f'0x{v:x}U' for v in incoming[15:])+'}'
        rows.append('{{'+','.join(f'0x{case[name]:x}U' for name,address,size in RAM_FIELDS)+'},{'+
            ','.join(f'0x{v:02x}U' for v in case['snapshot_block'])+'},'+legacy_text+','+incoming_text+
            f',0x{case["pattern"]:02x}U,{indices[blob]}U}},')
    spans=lambda values:','.join('{%dU,%dU}'%(r['address'],r['size']) for r in values)
    lines=['/* Complete paired inputs; no expected MCU output is supplied. */',
        f'#define PEDAL_CALIBRATION_SIZE {sum(r["size"] for r in calibration)}U',
        f'#define PEDAL_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        f'#define PEDAL_SNAPSHOT_ENTRY {contract.SNAPSHOT["entry"]}U',
        f'#define PEDAL_COMPARATOR_ENTRY {contract.ENTRY}U',
        'static const struct span pedal_calibration[] = {'+spans(calibration)+'};',
        'static const struct span pedal_bound[] = {'+spans(bound)+'};',
        'static const struct span pedal_ram_fields[] = {'+','.join('{%dU,%dU}'%(a,n) for name,a,n in RAM_FIELDS)+'};',
        'static const uint8_t pedal_calibration_blobs[][PEDAL_CALIBRATION_SIZE] = {']
    lines.extend('{'+','.join(f'0x{v:02x}U' for v in blob)+'},' for blob in blobs)
    lines.extend(('};',f'struct paired_case {{uint32_t ram[{len(RAM_FIELDS)}];uint8_t block[260];'
        'struct snapshot_context snapshot;struct context comparator;uint8_t pattern;uint32_t calibration_index;};',
        'static const struct paired_case pedal_cases[] = {',*rows,'};',''))
    return '\n'.join(lines).encode()
