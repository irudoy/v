"""Input-only paired 8/16-knot curves, full raw registers and independent incoming stack word."""
from kb import test_contract
from kb import derivative_scale_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('previous_first', 12184, 4), ('previous_second', 12840, 4), ('previous_fault', 38936, 4))
CURVES={'first':17,'middle':9,'last':17}
AXES={'first':16,'middle':8,'last':16}
CURVE_FIELDS={name:tuple(f'curve_{name}_{i:02d}' for i in range(count)) for name,count in CURVES.items()}
WIDTHS={n:w*8 for n,at,w in RAM_FIELDS}
WIDTHS.update({n:32 for n in (*REGISTERS,'stack_argument')})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update({f'axis_{name}_style':8 for name in AXES})
WIDTHS.update({f'axis_{name}_seed':16 for name in AXES})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={n:0 for n in WIDTHS}
DEFAULTS.update({n:v for n,v in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
for name,fields in CURVE_FIELDS.items():DEFAULTS.update({n:16+i*7 for i,n in enumerate(fields)})
DEFAULTS.update(threshold_word=1500,ratio_gain_first=32,ratio_gain_second=64,negative_gain_first=16,
    negative_gain_second=16,ratio_gain_middle=32,selector_gain_last=70,selector_gain_second=30,
    selector_gain_third=50,stack_argument=0xB6C70080,previous_first=0xA5C35AE1,
    previous_second=0x5AC3E1A5,previous_fault=0x13579BDF,variant=7)
for name in AXES:DEFAULTS[f'axis_{name}_style']=1
ENTRY_FIELDS={0xB78DA:('raw_r4','raw_r5','raw_r6','raw_r7','threshold_word','ratio_gain_first',
    'ratio_gain_second','negative_gain_first','axis_first',*CURVE_FIELDS['first'][:16]),
    0xB7A3C:('raw_r4','raw_r5','raw_r6','raw_r7','stack_argument','ratio_gain_middle',
    'negative_gain_second','selector_gain_last','selector_gain_second','selector_gain_third',
    'axis_middle','axis_last',*CURVE_FIELDS['middle'][:8],*CURVE_FIELDS['last'][:16])}
WORDS=(0,1,127,128,254,255,256,32767,32768,65534,65535)
BYTES=(0,1,2,3,31,32,64,127,128,254,255)


def input_blob(row,case,image):
    """Construct only raw axis words, without a lookup or publication equation."""
    name=row['name'].removeprefix('axis_')
    if name not in AXES or row['name']!='axis_'+name or row['size']!=AXES[name]*2:
        raise ValueError('the derivative-scale input constructor changes an exact complete axis blob')
    count=AXES[name];at=row['address'];style,seed=case[f'axis_{name}_style'],case[f'axis_{name}_seed']
    if style==0:return image[at:at+row['size']]
    low=seed&31;step=(65535-low)//(count-1)
    shapes={1:lambda i:low+i*step,2:lambda i:low+(i//2)*(65535-low)//(count//2-1),
        3:lambda i:(seed+8191*i)&65535,4:lambda i:65535-low-i*step,
        5:lambda i:seed,6:lambda i:0 if i<count-1 else 65535}
    return b''.join(shapes[style](i).to_bytes(2,'big') for i in range(count))


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for entry in contract.ENTRIES:
        for register in (*REGISTERS,'stack_argument'):
            for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
                add(entry,'complete-raw-register-and-stack-word-width',**{register:value})
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):add(entry,'complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
        for variant in (0,7,255):add(entry,'complete-preserved-register-context',variant=variant)
        for name,at,width in RAM_FIELDS:
            for value in (0,(1<<(8*width))-1):add(entry,'complete-prior-RAM-preimage',**{name:value})
        bias_name='raw_r5' if entry==0xB78DA else 'raw_r7'
        for edge in (-35269,-35268,-2501,-2500,-2499,0,30267,30268):
            for bias in (0,1,127,128,255):
                for delta in (-1,0,1):add(entry,'signed-quotient-bias-saturation-boundaries',
                    raw_r6=((edge+50*bias)*20000+delta)&0xFFFFFFFF,**{bias_name:bias})
        divisor_name='raw_r7' if entry==0xB78DA else 'raw_r4'
        for divisor in WORDS:
            for gain in BYTES:
                for dividend in (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF,100000000):
                    add(entry,'word-divisor-zero-bypass-and-raw-signed-dividend',raw_r6=dividend,
                        **{divisor_name:divisor,'negative_gain_first' if entry==0xB78DA else 'negative_gain_second':gain})
        for name in ENTRY_FIELDS[entry]:
            if name in WIDTHS and name not in REGISTERS and name!='stack_argument':
                for value in WORDS if WIDTHS[name]==16 else BYTES:
                    add(entry,'independent-physical-calibration-input',**{name:value})
        for selector in (0,1,2,3,4,127,128,254,255,0x100,0xFFFFFFFF):
            add(entry,'raw-selector-byte-and-capped-gain',**{'raw_r4' if entry==0xB78DA else 'raw_r5':selector})
        for bias in (0,1,127,128,255,0x100,0xFFFFFFFF):
            add(entry,'raw-bias-byte-upper-bits',**{bias_name:bias})
    for fifth in (0,1,2,63,64,127,128,254,255,0x100,0x12345678,0xFFFFFFFF):
        add(0xB7A3C,'independent-full-incoming-fifth-word-and-low-byte',stack_argument=fifth)
    for selector in (0,3):
        for gain in BYTES:
            add(0xB78DA,'each-selector-physical-gain-alternative',raw_r4=selector,
                **{'ratio_gain_first' if selector==0 else 'ratio_gain_second':gain})
    for selector,field in ((1,'selector_gain_second'),(2,'selector_gain_third'),(3,'selector_gain_last')):
        for gain in BYTES:add(0xB7A3C,'each-capped-selector-gain-alternative',raw_r5=selector,**{field:gain})
    first_axis=next(row for row in contract.INPUT_BLOBS if row['name']=='axis_first')
    for style in range(7):
        raw=input_blob(first_axis,dict(DEFAULTS,axis_first_style=style),image)
        for index in range(16):
            knot=int.from_bytes(raw[index*2:index*2+2],'big')
            for delta in (-1,0,1):
                threshold=65535-max(0,min(65535,knot+delta))
                for field in CURVE_FIELDS['first'][index:index+2]:
                    for word in WORDS:
                        add(0xB78DA,'first-curve-every-knot-neighbor-and-independent-cell',
                            raw_r7=20,negative_gain_first=1,threshold_word=threshold,axis_first_style=style,**{field:word})
    for index in range(8):
        for fifth in (max(0,index*255//7-1),index*255//7,min(255,index*255//7+1)):
            for field in CURVE_FIELDS['middle'][index:index+2]:
                for word in WORDS:
                    add(0xB7A3C,'middle-curve-byte-coordinate-knot-neighbor-and-independent-cell',
                        stack_argument=0xB6C70000|fifth,**{field:word})
    last_axis=next(row for row in contract.INPUT_BLOBS if row['name']=='axis_last')
    for style in range(7):
        raw=input_blob(last_axis,dict(DEFAULTS,axis_last_style=style),image)
        for index in range(16):
            knot=int.from_bytes(raw[index*2:index*2+2],'big')
            for delta in (-1,0,1):
                carrier=65535-max(0,min(65535,knot+delta))
                for field in CURVE_FIELDS['last'][index:index+2]:
                    for word in WORDS:
                        add(0xB7A3C,'last-curve-every-knot-neighbor-and-independent-cell',
                            raw_r4=20,negative_gain_second=1,axis_last_style=style,
                            **dict.fromkeys(CURVE_FIELDS['middle'],carrier),**{field:word})
    for name,count in AXES.items():
        entry=0xB78DA if name=='first' else 0xB7A3C
        for style in range(7):
            for seed in (0,1,32768,65535):
                add(entry,'independent-complete-physical-axis',**{f'axis_{name}_style':style,f'axis_{name}_seed':seed})
        for index,field in enumerate(CURVE_FIELDS[name]):
            for word in WORDS:
                add(entry,'every-physical-curve-cell-and-read-neighbor',**{field:word})
        shapes=(tuple(1+i*7 for i in range(count+1)),tuple(65535-i*1023 for i in range(count+1)),
            (128,)*(count+1),tuple(65535 if i&1 else 0 for i in range(count+1)))
        for shape in shapes:
            for style in range(7):add(entry,'ascending-descending-flat-alternating-curves',
                **dict(zip(CURVE_FIELDS[name],shape)),**{f'axis_{name}_style':style})
        for constant in (0,1,254,255,256,32768,65535):
            add(entry,'independent-curve-domain-boundary',**dict.fromkeys(CURVE_FIELDS[name],constant))
    return tuple(dict(row,index=i) for i,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[n]) is not int or not 0<=case[n]<(1<<bits) for n,bits in WIDTHS.items())
            or any(case[f'axis_{name}_style']>6 for name in AXES) or case['initial_sr']&~0x3F1):
        raise ValueError('a derivative-scale input changes raw width, full fifth stack word, physical curves/axes or SR context')


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+index*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for index in range(15)]
    registers[:8]=[case[name] for name in REGISTERS]
    return (*registers,(0x456789AB+case['variant'])&0xFFFFFFFF,
        (0x13579BDF+case['variant'])&0xFFFFFFFF,(0x2468ACE0+case['variant'])&0xFFFFFFFF,
        case['initial_sr'],case['stack_argument'])


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
        raise ValueError('the derivative scale caller withdrawal original changes complete raw RAM, CPU or complete curve/axis/gain/pool inputs')
