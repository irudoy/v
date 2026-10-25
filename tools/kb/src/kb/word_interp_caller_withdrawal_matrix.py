"""Input-only word surfaces, exact axes and one physical 65-word curve union."""
from kb import test_contract
from kb import word_interp_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('source_value', 7432, 4), ('previous_curve', 7442, 2), ('previous_surface', 11524, 4))
CURVE_FIELDS=tuple(f'curve_word_{i:03d}' for i in range(65))
DATA_NAMES=('surface','surface_row_axis','surface_column_axis','curve_low_axis','curve_high_axis')
WIDTHS={n:w*8 for n,at,w in RAM_FIELDS}
WIDTHS.update({n:32 for n in REGISTERS})
WIDTHS.update({n:16 for n in CURVE_FIELDS})
WIDTHS.update({n+'_style':8 for n in DATA_NAMES})
WIDTHS.update({n+'_seed':16 for n in DATA_NAMES})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={n:0 for n in WIDTHS}
DEFAULTS.update({n:v for n,v in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,30000,0,30000,17))})
DEFAULTS.update({n:(i*1023)&65535 for i,n in enumerate(CURVE_FIELDS)})
DEFAULTS.update({n+'_style':1 for n in DATA_NAMES})
DEFAULTS.update(source_value=30000,previous_curve=0xA55A,previous_surface=0xA5C35AE1,variant=7)
ENTRY_FIELDS={0x72F1E:('source_value','curve_low_axis','curve_high_axis',*CURVE_FIELDS[:64]),
    0xB7B98:('raw_r4','raw_r5','raw_r6','raw_r7','surface','surface_row_axis','surface_column_axis')}
WORD_BOUNDARIES=(0,1,0x7FFF,0x8000,0xFFFE,0xFFFF)
SOURCE_BOUNDARIES=(0,1,0x7FFF,0x8000,0xFFFF,0x10000,0xFFFF0,0xFFFFF,0x100000,0x7FFFFFFF,0x80000000,0xFFFFFFFF)


def input_blob(row,case,image):
    """Construct calibration preimages only; no lookup or returned-value equation is used."""
    name,at,size=row['name'],row['address'],row['size'];count=size//2
    style,seed=case[name+'_style'],case[name+'_seed']
    if style==0:return image[at:at+size]
    if name=='surface':
        shapes={1:lambda i:(seed+257*i)&65535,2:lambda i:(65535-seed-257*i)&65535,
            3:lambda i:seed if i&1 else 65535-seed,4:lambda i:seed,
            5:lambda i:(seed+4093*(i//16)+8191*(i%16))&65535,6:lambda i:65535 if i==seed%count else 0}
    else:
        low=seed&31;step=(65535-low)//(count-1)
        shapes={1:lambda i:low+i*step,2:lambda i:low+(i//2)*(65535-low)//(count//2-1),
            3:lambda i:(seed+8191*i)&65535,4:lambda i:65535-low-i*step,
            5:lambda i:seed,6:lambda i:0 if i<count-1 else 65535}
    return b''.join(shapes[style](i).to_bytes(2,'big') for i in range(count))


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for entry in contract.ENTRIES:
        for register in REGISTERS:
            for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
                add(entry,'complete-raw-register-width',**{register:value})
        for variant in (0,7,255):add(entry,'complete-preserved-register-context',variant=variant)
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):add(entry,'complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
        for name,at,width in RAM_FIELDS:
            if name.startswith('previous_'):
                for value in (0,(1<<(width*8))-1):add(entry,'complete-RAM-preimage',**{name:value})
    for source in SOURCE_BOUNDARIES:add(0x72F1E,'unsigned-source-selection-shift-and-clamps',source_value=source)
    for name in DATA_NAMES:
        entry=0xB7B98 if name.startswith('surface') else 0x72F1E
        for style in range(7):
            for seed in (0,1,0x8000,65535):
                changes={name+'_style':style,name+'_seed':seed}
                if name=='curve_high_axis':changes.update(curve_low_axis_style=5,curve_low_axis_seed=0,source_value=0x80001)
                add(entry,'independent-complete-physical-calibration',**changes)
    for row in contract.INPUT_BLOBS:
        name=row['name']
        if name=='curve_words' or name=='surface':continue
        for style in (0,1,2,3,4,5,6):
            seed=0
            sample=dict(DEFAULTS,**{name+'_style':style,name+'_seed':seed})
            raw=input_blob(row,sample,image)
            knots=tuple(int.from_bytes(raw[i:i+2],'big') for i in range(0,len(raw),2))
            for knot in knots:
                for delta in (-1,0,1):
                    coordinate=max(0,min(65535,knot+delta));changes={name+'_style':style}
                    if name.startswith('surface'):
                        changes['raw_r6' if name=='surface_row_axis' else 'raw_r4']=coordinate
                        add(0xB7B98,'every-physical-axis-knot-and-neighbor',**changes)
                    elif name=='curve_low_axis':
                        changes['source_value']=coordinate
                        add(0x72F1E,'every-low-curve-axis-knot-and-neighbor',**changes)
                    else:
                        changes.update(curve_low_axis_style=5,curve_low_axis_seed=0,source_value=(coordinate<<4)|1)
                        add(0x72F1E,'every-high-curve-axis-knot-and-neighbor',**changes)
    for index,field in enumerate(CURVE_FIELDS):
        high=index<32;local=index if high else min(index-32,31)
        changes=dict(source_value=(local*(65535//31)<<4)|1,curve_low_axis_style=5,curve_low_axis_seed=0) if high else dict(source_value=local*(65535//31))
        for value in WORD_BOUNDARIES:add(0x72F1E,'physical-union-cell-and-shared-neighbor',**changes,**{field:value})
    for flag in (0,1,2,127,128,255,256,0x80000000,0xFFFFFFFF):
        for scale in (0,1,127,128,255,256,0xFFFFFFFF):
            add(0xB7B98,'flag-byte-and-scale-byte-truncation',raw_r5=flag,raw_r7=scale)
    for row in (0,1,0x7FFF,0x8000,0xFFFF):
        for column in (0,1,0x7FFF,0x8000,0xFFFF):
            for style in (1,2,3,4,5,6):add(0xB7B98,'surface-direction-and-zero-fraction-paths',raw_r6=row,raw_r4=column,surface_style=style)
    selected=(('curve-low-zero',0x72F1E,dict(source_value=0)),
        ('curve-low-interior',0x72F1E,dict(source_value=30000)),
        ('curve-high-interior',0x72F1E,dict(source_value=0x80001,curve_low_axis_style=5,curve_low_axis_seed=0)),
        ('curve-high-clamp',0x72F1E,dict(source_value=0xFFFFFFFF)),
        ('curve-low-floor',0x72F1E,dict(source_value=0,curve_low_axis_style=5,curve_low_axis_seed=65535)),
        ('curve-high-floor',0x72F1E,dict(source_value=0x80001,curve_low_axis_style=5,curve_low_axis_seed=0,
            curve_high_axis_style=5,curve_high_axis_seed=65535)),
        ('surface-interior',0xB7B98,dict()),
        ('surface-descending',0xB7B98,dict(surface_style=2)),
        ('surface-flat-signed-return',0xB7B98,dict(raw_r4=0,raw_r6=0,surface_style=4,surface_seed=65535)),
        ('surface-flag',0xB7B98,dict(raw_r5=1)))
    for kind,entry,changes in selected:add(entry,kind,**changes)
    return tuple(dict(row,index=i) for i,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[n]) is not int or not 0<=case[n]<(1<<bits) for n,bits in WIDTHS.items())
            or any(case[n+'_style']>6 for n in DATA_NAMES) or case['initial_sr']&~0x3F1):
        raise ValueError('a word interpolation caller input changes an exact raw width, physical curve union, calibration style or SR context')


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+index*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for index in range(15)]
    registers[:8]=[case[name] for name in REGISTERS]
    return (*registers,(0x456789AB+case['variant'])&0xFFFFFFFF,
        (0x13579BDF+case['variant'])&0xFFFFFFFF,(0x2468ACE0+case['variant'])&0xFFFFFFFF,
        case['initial_sr'],0xB6C70000)


def memory(case):
    require_case(case);result=bytearray([0xA5])*RAM_SIZE
    for name,at,width in RAM_FIELDS:result[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(result)


def calibrations(declared,image,case):
    fixture,_=contract.fixture_for_case(declared,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}


def require_input(declared,image,case,observed):
    expected=calibrations(declared,image,case)
    if (not test_contract.exact(observed['entry'],case['entry'])
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],expected)
            or not test_contract.exact(observed['calibration_after'],expected)):
        raise ValueError('the word interpolation caller withdrawal original changes complete raw RAM, CPU or word/axis configuration/pool inputs')
