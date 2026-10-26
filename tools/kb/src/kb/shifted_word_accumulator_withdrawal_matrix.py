"""Typed raw inputs for the natural gated shift loop and saturated word publication."""
from kb import test_contract
from kb import shifted_word_accumulator_withdrawal_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('gate',0x244F,1),('metric',0x338A,1),('word',0x1040,2),('prior',0x3334,2),('native_gate',0x84C3,1))
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update(factor=8,shift=8,threshold=8,variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update(gate=32,native_gate=64,metric=200,word=32768,prior=1000,
    factor=128,shift=8,threshold=17,variant=7)
DEFAULTS.update({name:value for name,value in zip(REGISTERS,
    (0x12345678,0x87654321,0x80000000,0x7FFFFFFF,0xFFFFFFFF,1,0x10000,0xFFFF))})
WORDS=(0,1,2,127,128,255,256,257,32767,32768,32769,65279,65280,65533,65534,65535)


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry']!=contract.ENTRY
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('the accumulator input changes an exact raw register, byte, word, native control or SR width')


def cases(declared,image):
    rows=[]
    def add(kind,**changes):
        rows.append(dict(DEFAULTS,**changes,entry=contract.ENTRY,kind=kind,index=len(rows)))
    for field in ('gate','native_gate','metric','factor','shift','threshold'):
        for value in range(256):add('complete-independent-byte-domain',**{field:value})
    for field in ('word','prior'):
        for value in WORDS:add('complete-word-boundaries',**{field:value})
    for metric,threshold in ((0,0),(0,1),(1,0),(17,17),(18,17),(254,255),(255,254)):
        add('strict-unsigned-metric-threshold-boundary',metric=metric,threshold=threshold)
    for word in WORDS:
        for factor in (0,1,127,128,254,255):
            for shift in (0,1,7,8,9,15,24,254,255):
                add('scale-shift-cap-and-word-saturation',word=word,factor=factor,shift=shift)
    for shift in range(256):
        add('zero-product-complete-finite-loop',word=0,shift=shift)
    for prior in (0,1,32767,65534,65535):
        for shift in (0,1,8,255):
            add('final-word-saturation-boundary',prior=prior,shift=shift,metric=255,threshold=0,word=65535,factor=255)
    for field in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
            add('complete-incoming-register-width',**{field:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-state',initial_sr=qm|interrupt|t)
    for variant in (0,1,255):add('complete-preserved-context',variant=variant)
    # Each pair changes one real active input while all other complete inputs remain fixed.
    for field,values in (('gate',(0,32)),('native_gate',(0,64)),('metric',(100,200)),
            ('word',(16384,32768)),('prior',(1000,1001)),('factor',(64,128)),
            ('shift',(0,8)),('threshold',(17,100))):
        for value in values:add('fixed-other-real-publication-pair',**{field:value})
    return tuple(rows)


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+i*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for i in range(15)]
    registers[:8]=[case[name] for name in REGISTERS]
    return (*registers,(0x456789AB+case['variant'])&0xFFFFFFFF,
        (0x13579BDF+case['variant'])&0xFFFFFFFF,(0x2468ACE0+case['variant'])&0xFFFFFFFF,
        case['initial_sr'],0xB6C70000)


def memory(case):
    require_case(case);raw=bytearray([0xA5])*RAM_SIZE
    for name,at,width in RAM_FIELDS:raw[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(raw)


def calibrations(declared,image,case):
    fixture,_=contract.fixture_for_case(declared,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}


def require_input(declared,image,case,observed):
    raw=memory(case);cal=calibrations(declared,image,case)
    if (not test_contract.exact(observed['entry'],contract.ENTRY)
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(raw,)
            or not test_contract.exact(observed['calibration_before'],cal)
            or not test_contract.exact(observed['calibration_after'],cal)
            or observed['native_before']!=raw[0x8400:0x8500]
            or observed['native_after']!=observed['native_before']):
        raise ValueError('the accumulator original changes a complete raw input, native control mirror or immutable calibration')


def header(declared,image):
    lines=['/* Complete typed invocation inputs. */',
        '#define ACCUMULATOR_CALIBRATION_SIZE '+str(sum(row['size'] for row in contract.CONTROLLED_CALIBRATION))+'U',
        '#define ACCUMULATOR_BOUND_SIZE '+str(sum(row['size'] for row in contract.BOUND_SPANS))+'U']
    for name,spans in (('ram_fields',[dict(address=at,size=width) for field,at,width in RAM_FIELDS]),
            ('calibration',contract.CONTROLLED_CALIBRATION),('bound',contract.BOUND_SPANS)):
        lines.append('static const struct span accumulator_'+name+'[] = {'+
            ','.join('{'+f'0x{row["address"]:x}U,{row["size"]}U'+'}' for row in spans)+'};')
    lines.extend(('struct path_case { uint8_t pattern; uint32_t ram[5]; struct context context;',
        '    uint8_t calibration[ACCUMULATOR_CALIBRATION_SIZE]; };',
        'static const struct path_case accumulator_cases[] = {'))
    for case in declared['cases']:
        require_case(case);registers=context(declared['source'],case)
        cal=calibrations(declared['source'],image,case)
        raw=b''.join(cal[row['address']] for row in contract.CONTROLLED_CALIBRATION)
        ram=','.join(f'0x{case[field]:x}U' for field,at,width in RAM_FIELDS)
        core=','.join(f'0x{value:x}U' for value in registers[:15]);tail=','.join(f'0x{value:x}U' for value in registers[15:])
        lines.append('    {0xa5U,{'+ram+'},{{'+core+'},'+tail+'},{'+','.join(f'0x{value:02x}U' for value in raw)+'}},')
    return '\n'.join((*lines,'};','')).encode()
