"""Input-only complete mixed curves, word surface, raw RAM operands and CPU contexts."""
from kb import test_contract
from kb import mixed_curve_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('byte_1170', 4464, 1),
 ('byte_2465', 9317, 1),
 ('byte_2468', 9320, 1),
 ('byte_1765', 5989, 1),
 ('byte_1763', 5987, 1),
 ('byte_1f62', 8034, 1),
 ('byte_2315', 8981, 1),
 ('byte_2458', 9304, 1),
 ('byte_23bd', 9149, 1),
 ('byte_23c5', 9157, 1),
 ('byte_23f1', 9201, 1),
 ('byte_12dc', 4828, 1),
 ('byte_15ea', 5610, 1),
 ('byte_1a7d', 6781, 1),
 ('byte_41ab', 16811, 1),
 ('byte_106f', 4207, 1),
 ('byte_134c', 4940, 1),
 ('byte_1348', 4936, 1),
 ('byte_134a', 4938, 1),
 ('byte_12d4', 4820, 1),
 ('byte_24d1', 9425, 1),
 ('byte_23ee', 9198, 1),
 ('byte_1830', 6192, 1),
 ('byte_15eb', 5611, 1),
 ('byte_2485', 9349, 1),
 ('word_1e60', 7776, 2),
 ('word_114e', 4430, 2),
 ('word_120e', 4622, 2),
 ('word_1e62', 7778, 2),
 ('word_1138', 4408, 2),
 ('word_1752', 5970, 2),
 ('word_2266', 8806, 2),
 ('word_28b8', 10424, 2),
 ('word_28ba', 10426, 2),
 ('word_1024', 4132, 2),
 ('word_10ca', 4298, 2),
 ('word_1900', 6400, 2),
 ('word_18e4', 6372, 2),
 ('word_2408', 9224, 2),
 ('word_18ca', 6346, 2),
 ('word_22e8', 8936, 2),
 ('word_18cc', 6348, 2),
 ('previous_fault', 38936, 4))
SURFACE_FIELDS=tuple(f'surface_word_{i:02d}' for i in range(64))
IMPLICIT_FIELDS=tuple(f'implicit_word_{i:02d}' for i in range(30))
BYTE_CURVES={name:tuple(f'curve_{name}_{i:02d}' for i in range(9)) for name in ('timing','scale')}
AXIS_WIDTHS={'outer':2,'inner':2,'timing':1,'scale':1}
WIDTHS={n:w*8 for n,at,w in RAM_FIELDS}
WIDTHS.update({n:32 for n in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update({f'axis_{name}_style':8 for name in AXIS_WIDTHS})
WIDTHS.update({f'axis_{name}_seed':width*8 for name,width in AXIS_WIDTHS.items()})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={n:0 for n in WIDTHS}
DEFAULTS.update({n:v for n,v in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update({name:32+index//8+4*(index%8) for index,name in enumerate(SURFACE_FIELDS)})
DEFAULTS.update({name:1000+index*1500 for index,name in enumerate(IMPLICIT_FIELDS)})
DEFAULTS.update({name:64+index*8 for index,name in enumerate(BYTE_CURVES['timing'])})
DEFAULTS.update({name:16+index*4 for index,name in enumerate(BYTE_CURVES['scale'])})
DEFAULTS.update(threshold_word=5000,gain_byte=128,word_1e60=512,word_114e=5000,word_120e=0,
    byte_1170=80,word_1e62=0xA5C3,word_1138=0x5AC3,byte_2465=64,word_1752=512,
    byte_1765=10,byte_1763=2,byte_1f62=5,word_2266=100,byte_2315=0xA5,
    byte_23bd=97,byte_23c5=13,byte_23f1=9,byte_12dc=11,byte_15ea=5,byte_1a7d=72,byte_23ee=14,
    word_28b8=6000,word_28ba=7000,byte_41ab=64,byte_106f=120,word_1024=30000,word_10ca=30000,
    word_1900=2000,byte_134c=0x95,byte_1348=0x3D,byte_134a=0x67,byte_12d4=0xB3,byte_24d1=0xD3,byte_1830=0xCA,
    word_18e4=8192,word_2408=512,word_18ca=512,byte_15eb=200,word_22e8=10000,
    word_18cc=0xC3A5,previous_fault=0x13579BDF,variant=7)
for name in AXIS_WIDTHS:DEFAULTS[f'axis_{name}_style']=1
ENTRY_FIELDS={
    0x3B498:('word_1e60','word_114e','word_120e','byte_1170',*IMPLICIT_FIELDS),
    0x41DB6:('byte_2465','byte_2468','word_1752','byte_1765','byte_1763','byte_1f62','word_2266'),
    0x4BDC2:('byte_2458','byte_23bd','byte_23c5','byte_23f1','byte_12dc','byte_15ea','byte_1a7d',
        'word_28b8','word_28ba','byte_41ab','byte_106f','word_1024','word_10ca','word_1900','byte_23ee',
        'threshold_word','axis_outer','axis_inner','axis_timing',*SURFACE_FIELDS,*BYTE_CURVES['timing'][:8]),
    0x659AE:('word_18e4','word_2408','word_18ca','byte_15eb','byte_2485','word_22e8','gain_byte',
        'axis_scale',*BYTE_CURVES['scale'][:8])}
WORDS=(0,1,127,128,255,256,511,512,1023,1024,15359,15360,16383,16384,32767,32768,65534,65535)
BYTES=(0,1,2,15,16,31,32,63,64,127,128,129,254,255)


def input_blob(row,case,image):
    """Construct only raw eight-knot axes; no lookup or publication is evaluated."""
    name=row['name'].removeprefix('axis_')
    if name not in AXIS_WIDTHS or row['name']!='axis_'+name or row['size']!=8*AXIS_WIDTHS[name]:
        raise ValueError('the mixed-curve input constructor changes an exact complete raw axis blob')
    width=AXIS_WIDTHS[name];maximum=(1<<(width*8))-1;at=row['address']
    style,seed=case[f'axis_{name}_style'],case[f'axis_{name}_seed']
    if style==0:return image[at:at+row['size']]
    low=seed&7;step=(maximum-low)//7
    shapes={1:lambda i:low+i*step,2:lambda i:low+(i//2)*(maximum-low)//3,
        3:lambda i:(seed+(maximum//7)*i)&maximum,4:lambda i:maximum-low-i*step,
        5:lambda i:seed,6:lambda i:0 if i<7 else maximum}
    return b''.join(shapes[style](i).to_bytes(width,'big') for i in range(8))


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for entry in contract.ENTRIES:
        for register in REGISTERS:
            for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
                add(entry,'complete-raw-register-width',**{register:value})
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):add(entry,'complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
        for variant in (0,7,255):add(entry,'complete-preserved-register-context',variant=variant)
        for field in ENTRY_FIELDS[entry]:
            if field not in WIDTHS:continue
            for value in WORDS if WIDTHS[field]==16 else BYTES:
                add(entry,'independent-complete-RAM-or-configuration-input',**{field:value})
        for name,at,width in RAM_FIELDS:
            for value in (0,(1<<(8*width))-1):add(entry,'complete-prior-RAM-preimage',**{name:value})
    for first in WORDS:
        for second in WORDS:
            for third in (0,1,32768,65535):add(0x3B498,'word-product-shift-each-cap-and-implicit-domain',
                word_1e60=first,word_114e=second,word_120e=third)
    for index,field in enumerate(IMPLICIT_FIELDS):
        if index<14:
            coordinates=(15360+min(index,12)*4096,15360+min(index,12)*4096+512,
                min(65535,15360+min(index,12)*4096+1023))
        else:
            selected=min(index-14,14)
            coordinates=(selected*1024,selected*1024+512,selected*1024+1023)
        for coordinate in coordinates:
            for word in WORDS:add(0x3B498,'every-caller-reachable-implicit-physical-word',
                word_1e60=512,word_114e=coordinate,word_120e=0,**{field:word})
    for first in (0,64):
        for second in (0,4):
            for numerator in WORDS:add(0x41DB6,'each-independent-admission-byte-and-signed-numerator',
                byte_2465=first,byte_2468=second,word_2266=numerator)
    for denominator in WORDS:
        for signed_word in WORDS:
            for byte in (0,1,255):add(0x41DB6,'zero-word-large-positive-divisor-and-full-signed-numerator',
                word_1752=denominator,word_2266=signed_word,byte_1765=byte,byte_1763=byte,byte_1f62=byte)
    for mode in (0,32,255):
        for enabled in (0,64,255):
            for first in (0,4999,5000,5001,65535):
                for second in (0,4999,5000,5001,65535):add(0x4BDC2,'mode-enable-and-both-unsigned-threshold-orders',
                    byte_2458=mode,byte_41ab=enabled,word_28b8=first,word_28ba=second)
    for row in range(8):
        for column in range(8):
            fields=(SURFACE_FIELDS[row*8+column],)
            for field in fields:
                for word in WORDS:
                    add(0x4BDC2,'each-word-surface-cell-with-fixed-other-inputs',word_10ca=row*(65535//7),
                        word_1024=column*(65535//7),**{field:word})
    for name,width in AXIS_WIDTHS.items():
        entry=0x659AE if name=='scale' else 0x4BDC2
        for style in range(7):
            for seed in (0,1,1<<(width*8-1),(1<<(width*8))-1):
                add(entry,'independent-complete-physical-axis',**{f'axis_{name}_style':style,f'axis_{name}_seed':seed})
    for name,entry in (('timing',0x4BDC2),('scale',0x659AE)):
        for index,field in enumerate(BYTE_CURVES[name]):
            coordinate=min(index,7)*(255//7)
            for delta in (-1,0,1):
                raw=max(0,min(255,coordinate+delta))
                for byte in BYTES:
                    coordinate_input=dict(byte_106f=raw) if name=='timing' else dict(byte_15eb=255,word_22e8=(255-raw)*128)
                    add(entry,'each-semantic-byte-and-physical-read-neighbor',**coordinate_input,**{field:byte})
    for biased in WORDS:
        for gain in BYTES:
            for signed_word in (0,1,32767,32768,65535):add(0x659AE,'biased-word-byte-gain-signed-product-and-clamp',
                word_18e4=biased,gain_byte=gain,word_18ca=signed_word)
    for mode in (0,32):
        for source in BYTES:
            for shifted in (0,127,128,129,32640,32768,65535):add(0x659AE,'conditional-byte-curve-and-truncated-weight-product',
                byte_2485=mode,byte_15eb=source,word_22e8=shifted)
    for biased in (0,16384,65535):
        for gain in (0,128,255):
            for unsigned_word in (0,32768,65535):
                for signed_word in (0,32767,32768,65535):
                    for admitted_byte in (0,255):
                        for flag in (0,32):
                            add(0x659AE,'independent-products-weight-bypasses-and-both-signed16-clamp-boundaries',
                                word_18e4=biased,gain_byte=gain,word_2408=unsigned_word,
                                word_18ca=signed_word,byte_15eb=admitted_byte,byte_2485=flag)
    for outer in (0,1,32768,65535):
        for inner in (0,1,32768,65535):
            add(0x4BDC2,'independent-zero-fraction-and-full-surface-corner-paths',
                word_10ca=outer,word_1024=inner,axis_outer_style=1,axis_outer_seed=0,
                axis_inner_style=1,axis_inner_seed=0)
    return tuple(dict(row,index=i) for i,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[n]) is not int or not 0<=case[n]<(1<<bits) for n,bits in WIDTHS.items())
            or any(case[f'axis_{name}_style']>6 for name in AXIS_WIDTHS) or case['initial_sr']&~0x3F1):
        raise ValueError('a mixed curve input changes complete raw RAM,physical curve/surface/axis,register or SR widths')


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
        raise ValueError('the mixed curve caller withdrawal original changes complete raw RAM, CPU or complete mixed curve/surface/axis/scalar/pool inputs')
