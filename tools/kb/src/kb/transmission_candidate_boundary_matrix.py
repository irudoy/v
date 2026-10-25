"""Input-only full signed candidates, coupled ROM modes and independent paired CPU contexts."""
from copy import deepcopy
from kb import test_contract
from kb import transmission_candidate_boundary_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('word_4162', 16738, 2),
 ('byte_41a6', 16806, 1),
 ('word_3488', 13448, 2),
 ('word_348c', 13452, 2),
 ('word_3486', 13446, 2),
 ('word_348a', 13450, 2),
 ('word_34a0', 13472, 2),
 ('word_34c8', 13512, 2),
 ('word_349c', 13468, 2),
 ('prior_347e', 13438, 2),
 ('prior_3480', 13440, 2),
 ('prior_3482', 13442, 2),
 ('prior_3484', 13444, 2),
 ('byte_41bb', 16827, 1),
 ('byte_4253', 16979, 1),
 ('word_2438', 9272, 2),
 ('word_19c2', 6594, 2),
 ('word_34ca', 13514, 2),
 ('word_34b8', 13496, 2),
 ('word_34ba', 13498, 2),
 ('word_34b4', 13492, 2),
 ('prior_34a4', 13476, 2),
 ('prior_2434', 9268, 2),
 ('prior_19cc', 6604, 2),
 ('word_413a', 16698, 2),
 ('word_4138', 16696, 2),
 ('word_349a', 13466, 2),
 ('prior_19c6', 6598, 2),
 ('prior_415e', 16734, 2),
 ('prior_4160', 16736, 2))

WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update(rom_83c1=8,rom_89c5=8,rom_8b38=8)
ARRAYS={'completion_context':(20,32),'boundary_context':(20,32)}
WORD_VALUES=(0,1,2,127,128,255,256,511,512,8191,8192,16383,16384,32766,32767,32768,32769,65534,65535)
BYTE_VALUES=(0,1,2,3,7,8,9,15,16,31,32,33,63,64,127,128,129,254,255)

def initial_context(phase):
    return [*((0x18765430+i*0x01030507+phase*0x2030405)&0xFFFFFFFF for i in range(15)),
        0x12344321+phase,0x13579BDF+phase,0x2468ACE0+phase,0,0xB6C70000+phase]
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update(word_4162=1000,byte_41a6=8,word_3488=32767,word_348c=32767,
    word_3486=32768,word_348a=32767,word_34a0=0,word_34c8=32767,word_349c=0,
    prior_347e=0xA55A,prior_3480=0x5AA5,prior_3482=0xB6C7,prior_3484=0xC7D8,
    byte_41bb=0xA5,byte_4253=0xA5,word_2438=32768,word_19c2=32767,
    word_34ca=0,word_34b8=32767,word_34ba=32767,word_34b4=32767,word_413a=32768,
    word_4138=32767,word_349a=32768,prior_19c6=0x1234,rom_83c1=0,rom_89c5=1,rom_8b38=0,
    completion_context=initial_context(0),boundary_context=initial_context(1))

def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,*ARRAYS,'index','kind'}
            or type(case['index']) is not int or case['index']<0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())):
        raise ValueError('the candidate input changes a complete raw scalar or supplies an intermediate result')
    for name,(count,bits) in ARRAYS.items():
        values=case[name]
        if type(values) is not list or len(values)!=count or any(type(v) is not int or not 0<=v<(1<<bits) for v in values):
            raise ValueError('the candidate input changes a complete independent phase context')
        if values[18]&~0x3F1:raise ValueError('the candidate context changes its admitted complete I/M/Q/T controls')

def cases(source,image):
    rows=[]
    def add(kind,**changes):
        value=deepcopy(DEFAULTS);value.update(changes);value.update(index=len(rows),kind=kind);rows.append(value)
    add('complete-candidate-transfer-default')
    for phase in (0,1):
        field=contract.PHASES[phase]+'_context'
        for register in range(20):
            values=(0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF) if register!=18 else (0,1,0xF0,0x100,0x200,0x301,0x3F1)
            for raw in values:
                context=initial_context(phase);context[register]=raw;add('complete-independent-phase-CPU-field',**{field:context})
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):
                    context=initial_context(phase);context[18]=qm|interrupt|t
                    add('complete-phase-QM-interrupt-T',**{field:context})
    for name,at,width in RAM_FIELDS:
        for raw in BYTE_VALUES if width==1 else WORD_VALUES:
            add('complete-independent-raw-input-and-prior-output',**{name:raw})
            if width==2:
                add('complete-signed-clamp-order',**dict(dict(word_2438=1000,word_19c2=64536,rom_8b38=3),**{name:raw}))
    for field in ('rom_83c1','rom_89c5','rom_8b38'):
        for raw in range(256):add('complete-coupled-raw-ROM-mode',**{field:raw})
    for first in (0,1,0x20,0x21):
        for second in (0,1):
            for flags in (0,8):
                for a,z in ((0,32767),(32767,0),(32768,65535),(65535,32768)):
                    add('full-completion-bypass-and-signed-lower-selection',rom_83c1=first,rom_89c5=second,
                        byte_41a6=flags,word_348c=a,word_34c8=z,word_4162=a)
    for request in (32768,65535,0,1,32767):
        for duplicated in (32768,65535,0,1,32767):
            for control in (0,1,2,3):
                add('actual-duplicated-selection-and-signed-mode-bounds',word_2438=request,word_19c2=duplicated,rom_8b38=control)
    for field in ('word_34b8','word_34ba','word_34b4','word_4138','word_413a','word_349a'):
        for low,high in ((32768,32767),(32767,32768),(65535,0),(0,65535),(0,0)):
            add('unordered-independent-signed-candidate-limits',word_2438=0,word_19c2=0,
                **{field:low,'word_4162':high})
    for raw in WORD_VALUES:add('held-other-native-candidate-word-changes-actual-final-publication',word_4162=raw)
    return tuple(rows)

def context(source,case,phase):
    require_case(case)
    if type(phase) is not int or phase not in (0,1):raise ValueError('the quantity input changes its fixed phase identity')
    return tuple(case[('completion','boundary')[phase]+'_context'])

def memory(case):
    require_case(case);out=bytearray([0xA5])*RAM_SIZE
    for name,at,width in RAM_FIELDS:out[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(out)

def input_calibrations(case):
    require_case(case)
    return {0x83C1:bytes([case['rom_83c1']]),0x89C5:bytes([case['rom_89c5']]),0x8B38:bytes([case['rom_8b38']])}

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
    lines=['/* Raw paired inputs only; no supplied intermediate bound or expected output. */',
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
