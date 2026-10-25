"""Input-only complete three-mode state caller, raw byte axes and calibration cells."""
from kb import test_contract
from kb import state_surface_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('byte_1082', 4226, 1),
 ('byte_1083', 4227, 1),
 ('byte_11ae', 4526, 1),
 ('word_13dc', 5084, 2),
 ('word_13de', 5086, 2),
 ('byte_1861', 6241, 1),
 ('byte_1873', 6259, 1),
 ('byte_244f', 9295, 1),
 ('byte_2450', 9296, 1),
 ('byte_3373', 13171, 1),
 ('word_40c6', 16582, 2))
SURFACE_FIELDS=tuple(f'surface_value_{i}' for i in range(16))
SELECTION_FIELDS=tuple(f'selection_value_{i}' for i in range(16))
ROW_AXIS_FIELDS=tuple(f'row_axis_{i}' for i in range(4))
COL_AXIS_FIELDS=tuple(f'col_axis_{i}' for i in range(4))
CURVE_FIELDS=tuple(f'curve_value_{i}' for i in range(16))
SPLIT_FIELDS=tuple(f'split_value_{i}' for i in range(4))
CALIBRATION_FIELDS=(*SURFACE_FIELDS,*SELECTION_FIELDS,*ROW_AXIS_FIELDS,*COL_AXIS_FIELDS,*CURVE_FIELDS,*SPLIT_FIELDS)
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update(byte_1082=2,byte_1083=1,byte_11ae=96,word_13dc=0xA5C3,word_13de=0xC3A5,
    byte_1861=0xA5,byte_1873=0x5A,byte_244f=64,byte_2450=0,byte_3373=127,
    word_40c6=400,config_8b3f=0,config_8799=128,variant=7)
DEFAULTS.update({field:(i*15+7)&255 for i,field in enumerate(SURFACE_FIELDS)})
DEFAULTS.update({field:(i*17+3)&255 for i,field in enumerate(SELECTION_FIELDS)})
DEFAULTS.update({field:i*64 for i,field in enumerate(ROW_AXIS_FIELDS)})
DEFAULTS.update({field:i*64 for i,field in enumerate(COL_AXIS_FIELDS)})
DEFAULTS.update({field:(i*29+11)&255 for i,field in enumerate(CURVE_FIELDS)})
DEFAULTS.update({field:(i*61+17)&255 for i,field in enumerate(SPLIT_FIELDS)})
ENTRY_FIELDS={0x647E8:('config_8b3f','config_8799','byte_1082','byte_1083','byte_11ae',
    'byte_244f','byte_2450','byte_3373','word_40c6',*CALIBRATION_FIELDS)}
BYTE_VALUES=(0,1,2,3,4,7,8,15,16,17,31,32,63,64,96,127,128,129,191,192,223,224,254,255)
WORD_VALUES=(0,1,90,91,92,255,256,546,547,8192,32767,32768,65534,65535)


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=0x647E8,kind=kind,**changes))
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
            add('complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-and-local-carrier-preimage',variant=variant)
    profiles=({},dict(byte_244f=0,byte_2450=32),dict(byte_244f=1,byte_2450=0),dict(byte_244f=0,byte_2450=0))
    for profile in profiles:
        for field in ENTRY_FIELDS[0x647E8]:
            if field in CALIBRATION_FIELDS:continue
            for value in WORD_VALUES if WIDTHS[field]==16 else BYTE_VALUES:
                add('independent-mode-state-coordinate-scale-and-word-input',**dict(profile,**{field:value}))
    for config in (0,16,255):
        for first in (0,1,2,3,4,127,128,129,254,255):
            for second in (0,1,2,3,4,127,128,129,254,255):
                for flags,next_flags in ((0,0),(1,0),(64,0),(65,32),(0,32),(255,255)):
                    add('sign-extended-byte-unsigned-comparison-and-flag-precedence',config_8b3f=config,
                        byte_1082=first,byte_1083=second,byte_244f=flags,byte_2450=next_flags)
    for index,field in enumerate(SELECTION_FIELDS):
        for value in BYTE_VALUES:
            add('each-clipped-packed-selection-cell-and-full-local-word-carrier',byte_1082=index//4+1,
                byte_1083=index%4,**{field:value})
    for row in range(4):
        for col in range(4):
            profile=dict(byte_11ae=min(255,row*64+32),
                **{field:min(255,col*64+32) for field in SELECTION_FIELDS})
            for value in BYTE_VALUES:
                add('each-four-by-four-cell-and-both-interpolation-directions',
                    **dict(profile,**{SURFACE_FIELDS[row*4+col]:value}))
    for axis_fields,coordinate_field in ((ROW_AXIS_FIELDS,'byte_11ae'),(COL_AXIS_FIELDS,None)):
        for index,field in enumerate(axis_fields):
            for value in BYTE_VALUES:
                coordinate=min(255,index*64+32)
                profile={coordinate_field:coordinate} if coordinate_field else {name:coordinate for name in SELECTION_FIELDS}
                add('each-independent-raw-axis-cell-without-monotonicity-premise',**dict(profile,**{field:value}))
    for raw in BYTE_VALUES:
        add('complete-unordered-descending-and-repeated-axis-preimages',
            **{field:(i*73+raw)&255 for i,field in enumerate((*ROW_AXIS_FIELDS,*COL_AXIS_FIELDS))})
        for i,field in enumerate(SPLIT_FIELDS):
            add('each-split-byte-and-residual-product',byte_244f=0,byte_2450=32,
                byte_1083=i+1,byte_3373=255,**{field:raw})
        for i in range(4):
            add('each-split-residual-byte',byte_244f=0,byte_2450=32,byte_1083=i+1,
                byte_3373=255,**{CURVE_FIELDS[12+i]:raw})
            add('each-implicit-mode-state-product-byte',byte_244f=1,byte_2450=0,
                byte_1083=i+1,byte_3373=255,**{CURVE_FIELDS[8+i]:raw})
        for i in range(8):
            coordinate=min(255,i*32+16)
            source_word=((coordinate+32)*32768+0x2D0D)//0x2D0E
            add('each-implicit-eight-byte-cell-and-endpoint-promotion',byte_244f=1,
                byte_2450=0,word_40c6=source_word,**{CURVE_FIELDS[i]:raw})
    for desired in (0,1,31,32,33,63,64,127,128,191,192,223,224,225,254,255,256):
        boundary=((desired+32)*32768+0x2D0D)//0x2D0E
        for delta in (-1,0,1):
            add('full-unsigned-word-scaled-coordinate-clipping-and-eight-cell-boundary',
                byte_244f=1,byte_2450=0,word_40c6=max(0,min(65535,boundary+delta)))
    for name,address,width in RAM_FIELDS:
        for value in (0,(1<<(8*width))-1):add('complete-prior-RAM-publication-or-bypass-preimage',**{name:value})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a state surface input changes a complete raw byte,word,register,calibration or SR width')


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
        raise ValueError('the state surface caller withdrawal original changes complete raw RAM, CPU or complete state/surface/axis/implicit-curve/divider/pool inputs')
