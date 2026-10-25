"""Raw APC controls and curve bytes with independent full CPU and overwritten-prior inputs."""
from copy import deepcopy
from kb import test_contract
from kb import apc_reset_candidate_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('byte_4184',0x4184,1),('word_10ca',0x10CA,2),('byte_11ae',0x11AE,1),('byte_1108',0x1108,1),
    ('prior_144c',0x144C,1),('prior_1450',0x1450,1),('prior_1874',0x1874,1),
    ('prior_144d',0x144D,1),('prior_1451',0x1451,1),('prior_1875',0x1875,1),
    ('prior_2406',0x2406,1),('byte_4251',0x4251,1),('prior_9818',0x9818,4))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({row['name']:row['size']*8 for row in contract.DECLARED['control_blobs']})
WIDTHS['pattern']=8
ARRAYS={'context':(20,32),'source_curves':(16,8)}
BYTE_VALUES=(0,1,2,3,4,6,7,8,9,15,16,31,32,33,63,64,65,113,114,115,127,128,129,159,160,161,223,224,225,254,255)
WORD_VALUES=(0,1,3,4,127,128,255,256,1023,1024,1025,32767,32768,65534,65535)
LONG_VALUES=(0,1,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFF)
DEFAULT_CONTEXT=[*((0x18765430+i*0x01030507)&0xFFFFFFFF for i in range(15)),
    0x12344321,0x13579BDF,0x2468ACE0,0,0xB6C70000]
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update(context=DEFAULT_CONTEXT,source_curves=[1]*8+[255]*8,pattern=0xA5,
    byte_11ae=64,byte_1108=64,word_10ca=4095,prior_1875=0xA5,prior_2406=0xB6,
    prior_144c=0xC7,prior_1450=0xD8,prior_1874=0xE9,prior_144d=0x5A,prior_1451=0x6B,prior_9818=0xDEADBEEF,
    rom_8291=15,rom_828a=4,rom_851f=150,rom_8520=198,rom_8521=36,rom_8522=160,rom_8523=8,
    rom_8524=0,rom_8525=1,rom_8b87=114,rom_8b88=6,rom_959a=0x1700)

def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,*ARRAYS,'index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())):
        raise ValueError('the APC candidate input changes an exact raw scalar or supplies a live result')
    for name,(count,bits) in ARRAYS.items():
        values=case[name]
        if type(values) is not list or len(values)!=count or any(type(v) is not int or not 0<=v<(1<<bits) for v in values):
            raise ValueError('the APC candidate input truncates a complete raw context or physical curve span')
    if case['context'][18]&~0x3F1:
        raise ValueError('the APC candidate input changes the admitted complete I/M/Q/T context controls')

def cases(source,image):
    rows=[]
    def add(kind,**changes):
        value=deepcopy(DEFAULTS);value.update(changes);value.update(index=len(rows),kind=kind);rows.append(value)
    add('complete-published-and-live-APC-candidate')
    stock={row['name']:int.from_bytes(image[row['address']:row['address']+row['size']],'big') for row in source['control_blobs']}
    stock['source_curves']=list(image[0x1208E:0x1209E])
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
            add('raw-input-and-overwritten-prior-publication',**{field:raw})
            if field=='word_10ca':add('alternate-unsigned-word-quarter-boundaries',byte_4184=64,word_10ca=raw)
    for row in source['control_blobs']:
        for raw in range(256) if row['size']==1 else WORD_VALUES:
            add('raw-byte-mode-clamp-factor-and-word-reference',**{row['name']:raw})
            if row['name'] in ('rom_8291','rom_8520','rom_8521'):
                add('alternate-mode-raw-parameter-and-wrapped-product',byte_4184=64,**{row['name']:raw})
    for coordinate in range(256):
        for values in (list(range(8)),list(reversed(range(8)))):
            add('full-first-curve-coordinate-and-directed-fraction',rom_8522=255,rom_8523=0,
                byte_11ae=coordinate,source_curves=values+[255]*8)
            add('full-second-curve-coordinate-and-directed-fraction',rom_8525=0,byte_1108=coordinate,
                source_curves=[255]*8+values)
    for which in (0,1):
        for index in range(8):
            for raw in (0,1,127,128,254,255):
                values=[0]*8+[255]*8 if which==0 else [255]*8+[0]*8
                values[which*8+index]=raw
                for coordinate in sorted({max(0,index*32-1),index*32,min(255,index*32+1)}):
                    add('held-other-real-curve-candidate-and-final-publication',source_curves=values,
                        rom_8522=255,rom_8523=0,rom_8525=0,rom_8b87=255,rom_8b88=255,
                        byte_11ae=coordinate if which==0 else 32,byte_1108=32 if which==0 else coordinate)
    for mode in (0,64):
        for speed in BYTE_VALUES:
            for floor in (0,1,127,128,255):
                add('actual-zero-and-positive-speed-paths',byte_4184=mode,byte_1108=speed,rom_8525=floor)
        for coordinate in (0,1,255):
            for speed in (0,1,2,255):
                for factor in (0,1,127,128,254,255):
                    add('prestage-wrap-zero-speed-and-independent-mode-paths',byte_4184=mode,
                        byte_11ae=coordinate,word_10ca=coordinate*4,byte_1108=speed,rom_8525=0,
                        rom_8521=factor,rom_8524=255,rom_959a=65535)
        for lower,upper in ((0,255),(255,0),(0,0),(255,255),(128,127),(127,128)):
            add('unordered-first-coordinate-and-output-clamp-limits',byte_4184=mode,rom_8522=upper,rom_8523=lower)
            add('unordered-final-prestage-clamp-limits',byte_4184=mode,rom_8b87=upper,rom_8b88=lower)
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
    mapping[0x1208E]=bytes(case['source_curves']);return mapping

def calibrations(source,image,case):
    fixture,_=contract.fixture_for_case(source,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}

def require_input(source,image,case,observed):
    wanted=calibrations(source,image,case)
    if (observed['entry']!=contract.ENTRY or not test_contract.exact(observed['context'],context(source,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],wanted)
            or not test_contract.exact(observed['calibration_after'],wanted)):
        raise ValueError('the APC candidate changes a complete immutable raw input or calibration')

def header(declared,image):
    source=declared['source'];cal,bound=contract.CONTROLLED_CALIBRATION,contract.BOUND_SPANS
    lines=['/* Complete raw inputs only; no supplied live candidate or expected output. */',
        f'#define APC_CALIBRATION_SIZE {sum(r["size"] for r in cal)}U',
        f'#define APC_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        'static const struct span apc_calibration[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in cal)+'};',
        'static const struct span apc_bound[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in bound)+'};',
        'struct path_case { '+''.join('uint32_t '+name+';' for name,at,width in RAM_FIELDS)+
        'struct context context;uint8_t pattern,calibration[APC_CALIBRATION_SIZE]; };',
        'static const struct path_case apc_cases[] = {']
    for case in declared['cases']:
        raw=context(source,case)
        ctx='{{'+','.join(f'0x{v:x}U' for v in raw[:15])+'},'+','.join(f'0x{v:x}U' for v in raw[15:])+'}'
        mapping=calibrations(source,image,case);blob=b''.join(mapping[row['address']] for row in cal)
        lines.append('{'+','.join(f'0x{case[name]:x}U' for name,at,width in RAM_FIELDS)+','+ctx+
            f',0x{case["pattern"]:02x}U,'+'{'+','.join(f'0x{v:02x}U' for v in blob)+'}},')
    return '\n'.join((*lines,'};','')).encode()
