"""Raw third-trim channel contexts, complete word/counter arrays and ROM controls."""
from copy import deepcopy
from kb import test_contract
from kb import third_trim_word_writer_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('flags_328a',0x328A,1),('flags_328b',0x328B,1),('flags_328e',0x328E,1),
 ('flags_28e4',0x28E4,1),('flags_28b4',0x28B4,1),('flags_328c',0x328C,1),('flags_3288',0x3288,1))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({row['name']:row['size']*8 for row in contract.DECLARED['control_blobs']})
WIDTHS['pattern']=8
ARRAYS={'context':(20,32),'prior_words':(256,16),'accumulators':(256,32)}
BYTE_VALUES=(0,1,2,3,4,7,15,31,32,63,64,127,128,129,254,255)
WORD_VALUES=(0,1,127,128,255,256,23039,23040,23041,25599,25600,25601,28159,28160,28161,32767,32768,65534,65535)
LONG_VALUES=(0,1,25599,25600,25601,25607,25608,25609,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFF00,0xFFFFFFFF)
DEFAULT_CONTEXT=[*((0x18765430+i*0x01030507)&0xFFFFFFFF for i in range(15)),
 0x12344321,0x13579BDF,0x2468ACE0,0,0xB6C70000]
DEFAULT_CONTEXT[4]=0
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update(context=DEFAULT_CONTEXT,prior_words=[0x6400]*256,accumulators=[0x6400]*256,
 pattern=0xA5,flags_328a=1,flags_328b=1,rom_8b2a=9,rom_8998=0x50,rom_86f7=4,
 rom_8997=0x50,rom_86f6=4,rom_82e5=110,rom_82e4=90,rom_86f5=8)

def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,*ARRAYS,'index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())):
        raise ValueError('the third-trim input changes a raw scalar or supplies a produced word')
    for name,(count,bits) in ARRAYS.items():
        values=case[name]
        if type(values) is not list or len(values)!=count or any(type(v) is not int or not 0<=v<(1<<bits) for v in values):
            raise ValueError('the third-trim input truncates a complete raw context or indexed memory array')
    if case['context'][18]&~0x3F1:
        raise ValueError('the third-trim input changes admitted complete I/M/Q/T controls')

def cases(source,image):
    rows=[]
    def add(kind,**changes):
        value=deepcopy(DEFAULTS);value.update(changes);value.update(index=len(rows),kind=kind);rows.append(value)
    add('complete-bank1-word-writer')
    add('complete-owned-stock-control-bytes',**{r['name']:int.from_bytes(image[r['address']:r['address']+r['size']],'big') for r in source['control_blobs']})
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
        for raw in BYTE_VALUES:add('raw-mask-input',**{field:raw})
    for row in source['control_blobs']:
        for raw in range(256):
            updates={row['name']:raw}
            if row['name']=='rom_8998':updates.update(flags_28e4=1,flags_28b4=0)
            elif row['name']=='rom_86f7':updates.update(flags_28e4=1,flags_28b4=1)
            elif row['name']=='rom_8997':updates.update(flags_28e4=0,flags_28b4=1)
            elif row['name']=='rom_86f5':
                counters=[0x6400]*256;counters[0]=25599
                updates.update(flags_328a=0,flags_328b=0,flags_328c=1,accumulators=counters)
            add('full-raw-ROM-control-in-actual-consuming-path',**updates)
    for channel in range(256):
        context=list(DEFAULT_CONTEXT);context[4]=0xABCD0000|channel
        mask=(channel+1)&255
        for shared in (False,True):
            mode=4 if shared else 0
            select=3 if shared else mask
            for first,second in ((0,0),(mask,0),(mask,mask),(0,mask)):
                add('complete-raw-channel-correction-and-shared-footprint',context=list(context),
                    rom_8b2a=mode,flags_328a=select,flags_328b=select,
                    flags_28e4=first,flags_28b4=second)
            add('complete-raw-channel-constant-fallback-footprint',context=list(context),rom_8b2a=mode,
                flags_328a=0,flags_328b=0,flags_328e=0,flags_328c=0,flags_3288=0)
            counters=[0x6400]*256;counters[channel]=25599
            add('complete-raw-channel-counter-and-mask-footprint',context=list(context),rom_8b2a=mode,
                flags_328a=0,flags_328b=0,flags_328e=0,flags_328c=mask,accumulators=counters)
        for high in (0,0x80000000):
            context=list(DEFAULT_CONTEXT);context[4]=high|channel
            add('independent-high24-entry-channel-bits',context=context)
    for shared in (False,True):
        for a in (0,1,2,3,255):
            for b in (0,1,2,3,255):
                for e in (0,1,2,3,255):
                    add('ordinary-or-shared-global-admission-predicates',rom_8b2a=4 if shared else 0,
                        flags_328a=a,flags_328b=b,flags_328e=e)
    for raw in WORD_VALUES:
        words=[0x6400]*256;words[0]=raw
        for first,second in ((0,0),(1,0),(1,1),(0,1)):
            add('independent-bank1-word-and-real-correction-direction',prior_words=words,
                flags_28e4=first,flags_28b4=second)
        add('unclipped-bank1-word-causal-alternative',prior_words=words,rom_82e4=0,rom_82e5=255)
    for lower,upper in ((0,255),(255,0),(0,0),(255,255),(90,110),(110,90),(128,127),(127,128)):
        add('unordered-raw-word-clamp-limits',rom_82e4=lower,rom_82e5=upper)
    for old in LONG_VALUES:
        for step in (0,1,4,8,127,128,254,255):
            counters=[0x6400]*256;counters[0]=old
            add('full-signed32-counter-neutral-crossing-and-raw-increment',flags_328a=0,flags_328b=0,
                flags_328c=1,rom_86f5=step,accumulators=counters)
            add('second-mask-counter-admission',flags_328a=0,flags_328b=0,flags_328c=0,flags_3288=1,
                rom_86f5=step,accumulators=counters)
    for prior in WORD_VALUES:
        words=[0x6400]*256;words[1]=prior
        for shared in (False,True):
            add('independent-sibling-word-in-ordinary-and-shared-mode',prior_words=words,rom_8b2a=4 if shared else 0,
                flags_328a=3 if shared else 1,flags_328b=3 if shared else 1)
    for pattern in (0,1,0x5A,0x80,0xFF):add('complete-unmodified-RAM-pattern',pattern=pattern)
    return tuple(rows)

def context(source,case):
    require_case(case);return tuple(case['context'])

def memory(case):
    require_case(case);out=bytearray([case['pattern']])*RAM_SIZE
    for name,at,width in RAM_FIELDS:out[at:at+width]=case[name].to_bytes(width,'big')
    for name,at,width in (('prior_words',0x2A24,2),('accumulators',0x3310,4)):
        for index,value in enumerate(case[name]):out[at+index*width:at+(index+1)*width]=value.to_bytes(width,'big')
    return bytes(out)

def input_calibrations(case):
    require_case(case)
    return {r['address']:case[r['name']].to_bytes(r['size'],'big') for r in contract.DECLARED['control_blobs']}

def calibrations(source,image,case):
    fixture,_=contract.fixture_for_case(source,image,case)
    return {r['address']:fixture[r['address']:r['address']+r['size']] for r in contract.CONTROLLED_CALIBRATION}

def require_input(source,image,case,observed):
    wanted=calibrations(source,image,case)
    if (observed['entry']!=contract.ENTRY or not test_contract.exact(observed['context'],context(source,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],wanted)
            or not test_contract.exact(observed['calibration_after'],wanted)):
        raise ValueError('the third-trim writer changes a complete immutable raw input or calibration')

def header(declared,image):
    source=declared['source'];cal,bound=contract.CONTROLLED_CALIBRATION,contract.BOUND_SPANS
    lines=['/* Complete raw inputs only; no supplied produced R2 or expected word. */',
        f'#define TRIM_CALIBRATION_SIZE {sum(r["size"] for r in cal)}U',
        f'#define TRIM_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        'static const struct span trim_calibration[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in cal)+'};',
        'static const struct span trim_bound[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in bound)+'};',
        'struct path_case { '+''.join('uint32_t '+name+';' for name,at,width in RAM_FIELDS)+
        'struct context context;uint16_t prior_words[256];uint32_t accumulators[256];'
        'uint8_t pattern,calibration[TRIM_CALIBRATION_SIZE]; };',
        'static const struct path_case trim_cases[] = {']
    for case in declared['cases']:
        raw=context(source,case)
        ctx='{{'+','.join(f'0x{v:x}U' for v in raw[:15])+'},'+','.join(f'0x{v:x}U' for v in raw[15:])+'}'
        mapping=calibrations(source,image,case);blob=b''.join(mapping[r['address']] for r in cal)
        arrays=','.join('{'+','.join(f'0x{v:x}U' for v in case[name])+'}' for name in ('prior_words','accumulators'))
        lines.append('{'+','.join(f'0x{case[name]:x}U' for name,at,width in RAM_FIELDS)+','+ctx+','+arrays+
            f',0x{case["pattern"]:02x}U,'+'{'+','.join(f'0x{v:02x}U' for v in blob)+'}},')
    return '\n'.join((*lines,'};','')).encode()
