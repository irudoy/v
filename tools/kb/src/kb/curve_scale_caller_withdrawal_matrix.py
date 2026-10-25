"""Input-only complete 32-knot curve, raw signed dividend and low-byte bias preimages."""
from kb import test_contract
from kb import curve_scale_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('previous_scaled', 11528, 4), ('previous_fault', 38936, 4))
CURVE_FIELDS=tuple(f'curve_word_{i:02d}' for i in range(33))
WIDTHS={n:w*8 for n,at,w in RAM_FIELDS}
WIDTHS.update({n:32 for n in REGISTERS})
WIDTHS.update({n:16 for n in CURVE_FIELDS})
WIDTHS.update(gain=8,axis_style=8,axis_seed=16,variant=8,initial_sr=10)
DEFAULTS={n:0 for n in WIDTHS}
DEFAULTS.update({n:v for n,v in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,30000,50000000,16,0x01000000))})
DEFAULTS.update({n:1000+i*1000 for i,n in enumerate(CURVE_FIELDS)})
DEFAULTS.update(gain=64,axis_style=1,previous_scaled=0xA5C35AE1,previous_fault=0x13579BDF,variant=7)
ENTRY_FIELDS={0xB7768:('raw_r4','raw_r5','raw_r6','gain','axis_words',*CURVE_FIELDS[:32])}
WORDS=(0,1,127,128,32767,32768,65534,65535)
BYTES=(0,1,2,31,32,64,127,128,254,255)


def input_blob(row,case,image):
    """Construct raw axis words only; no lookup or output equation is used."""
    if row['name']!='axis_words' or row['size']!=64:
        raise ValueError('the curve-scale input constructor changes its exact complete axis blob')
    at=row['address'];style,seed=case['axis_style'],case['axis_seed']
    if style==0:return image[at:at+64]
    low=seed&31;step=(65535-low)//31
    shapes={1:lambda i:low+i*step,2:lambda i:low+(i//2)*(65535-low)//15,
        3:lambda i:(seed+8191*i)&65535,4:lambda i:65535-low-i*step,
        5:lambda i:seed,6:lambda i:0 if i<31 else 65535}
    return b''.join(shapes[style](i).to_bytes(2,'big') for i in range(32))


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=0xB7768,kind=kind,**changes))
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):add('complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-context',variant=variant)
    for name,at,width in RAM_FIELDS:
        for value in (0,(1<<(8*width))-1):add('complete-prior-RAM-preimage',**{name:value})
    for edge in (-37769,-37768,-5001,-5000,-4999,0,27767,27768):
        for bias in (0,1,127,128,255):
            for delta in (-1,0,1):add('signed-quotient-bias-saturation-boundaries',raw_r5=((edge+100*bias)*10000+delta)&0xFFFFFFFF,raw_r6=bias)
    for gain in BYTES:
        for dividend in (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF,50000000):
            for bias in (0,16,255):add('raw-signed-dividend-byte-bias-and-independent-gain',gain=gain,raw_r5=dividend,raw_r6=bias)
    axis=next(row for row in contract.INPUT_BLOBS if row['name']=='axis_words')
    for style in range(7):
        for seed in (0,1,32768,65535):add('independent-complete-axis-preimage',axis_style=style,axis_seed=seed)
        raw=input_blob(axis,dict(DEFAULTS,axis_style=style),image)
        for offset in range(0,64,2):
            knot=int.from_bytes(raw[offset:offset+2],'big')
            for delta in (-1,0,1):add('every-physical-axis-knot-and-neighbor',axis_style=style,raw_r4=max(0,min(65535,knot+delta)))
    for index,field in enumerate(CURVE_FIELDS):
        for word in WORDS:add('independent-physical-curve-cell-and-read-neighbor',raw_r4=min(index,31)*(65535//31),**{field:word})
    shapes=(tuple(1000+i*1000 for i in range(33)),tuple(65535-i*1023 for i in range(33)),
        (32000,)*33,tuple(65535 if i&1 else 0 for i in range(33)))
    for shape in shapes:
        for coordinate in WORDS:add('ascending-descending-flat-alternating-word-curves',raw_r4=coordinate,**dict(zip(CURVE_FIELDS,shape)))
    selected=(('curve-interior',dict()),
        ('curve-descending',dict(curve_word_14=65535,curve_word_15=0)),
        ('axis-floor',dict(axis_style=5,axis_seed=65535,raw_r4=0)),
        ('axis-endpoint',dict(axis_style=5,axis_seed=0,raw_r4=65535)),
        ('upper-saturation',dict(raw_r5=0x7FFFFFFF,raw_r6=0)),
        ('lower-saturation',dict(raw_r5=0x80000000,raw_r6=255)),
        ('nonnegative-floor',dict(raw_r5=(-60000000)&0xFFFFFFFF,raw_r6=0)),
        ('gain-zero',dict(gain=0)))
    for kind,changes in selected:add(kind,**changes)
    return tuple(dict(row,index=i) for i,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry']!=0xB7768
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[n]) is not int or not 0<=case[n]<(1<<bits) for n,bits in WIDTHS.items())
            or case['axis_style']>6 or case['initial_sr']&~0x3F1):
        raise ValueError('a curve-scale caller input changes raw width, physical curve/axis preimage, style or SR context')


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
        raise ValueError('the curve scale caller withdrawal original changes complete raw RAM, CPU or complete curve/axis/gain/pool inputs')
