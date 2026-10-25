"""Input-only complete timing flags, history, pulse maxima and raw quotient/remainder operands."""
from kb import test_contract
from kb import timing_remainder_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('byte_24c5', 9413, 1),
 ('byte_24cb', 9419, 1),
 ('byte_11f9', 4601, 1),
 ('byte_11fa', 4602, 1),
 ('byte_22fa', 8954, 1),
 ('byte_24c2', 9410, 1),
 ('byte_2378', 9080, 1),
 ('byte_229d', 8861, 1),
 ('byte_24c0', 9408, 1),
 ('byte_25fc', 9724, 1),
 ('byte_24cc', 9420, 1),
 ('byte_2459', 9305, 1),
 ('byte_226c', 8812, 1),
 ('byte_40e7', 16615, 1),
 ('byte_2356', 9046, 1),
 ('byte_12d6', 4822, 1),
 ('byte_4184', 16772, 1),
 ('byte_24c9', 9417, 1),
 ('byte_4251', 16977, 1),
 ('byte_23bf', 9151, 1),
 ('byte_23f0', 9200, 1),
 ('word_11d6', 4566, 2),
 ('word_11d8', 4568, 2),
 ('word_23c2', 9154, 2),
 ('word_237e', 9086, 2),
 ('word_2000', 8192, 2),
 ('word_1ff6', 8182, 2),
 ('word_10ca', 4298, 2),
 ('word_11bc', 4540, 2),
 ('word_23d4', 9172, 2),
 ('word_23d6', 9174, 2),
 ('word_23d8', 9176, 2),
 ('word_23da', 9178, 2),
 ('word_23dc', 9180, 2),
 ('word_23de', 9182, 2),
 ('word_241c', 9244, 2),
 ('word_192e', 6446, 2),
 ('history_word', 8184, 4),
 ('previous_fault', 38936, 4))
CURVE_FIELDS=tuple(f'curve_word_{index:02d}' for index in range(9))
MAXIMUM_FIELDS=tuple(f'word_{address:04x}' for address in range(0x23D4,0x23E0,2))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(axis_style=8,axis_seed=16,variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update({name:200+index*16 for index,name in enumerate(CURVE_FIELDS)})
DEFAULTS.update({name:7000+index*100 for index,name in enumerate(MAXIMUM_FIELDS)})
DEFAULTS.update(mode_flag=32,counter_reload=10,remainder_offset=30,first_gain=80,second_gain=100,
    byte_24c5=32,byte_24cb=0,byte_11f9=12,byte_11fa=20,byte_22fa=5,word_23c2=2048,
    byte_24c2=0,byte_2378=40,byte_229d=30,byte_24c0=64,byte_25fc=0,byte_24cc=0,
    word_237e=30000,byte_2459=0,byte_226c=0xA5,byte_40e7=0,byte_2356=10,byte_12d6=0xC3,
    word_11d6=0xA5C3,word_11d8=0xC3A5,word_2000=0xAA55,word_1ff6=0x55AA,history_word=300,
    byte_4184=0,word_10ca=30000,word_11bc=32000,word_241c=4000,word_192e=600,byte_24c9=0,
    byte_4251=0,byte_23bf=0xA3,byte_23f0=0xC5,previous_fault=0x13579BDF,axis_style=1,axis_seed=0,variant=7)
ENTRY_FIELDS={
    0x4D99C:('mode_flag','counter_reload','byte_24c5','byte_24cb','byte_11f9','byte_11fa','byte_22fa',
        'word_23c2','byte_24c2','byte_2378','byte_229d','byte_24c0','byte_25fc','byte_24cc','word_237e',
        'byte_2459','first_gain','second_gain','history_word','byte_40e7','byte_2356','axis_words',*CURVE_FIELDS[:8]),
    0x521A8:('byte_4184','word_10ca','word_11bc',*MAXIMUM_FIELDS,'word_241c','word_192e',
        'byte_24c9','remainder_offset','byte_4251')}
WORDS=(0,1,2,3,4,7,8,15,16,31,32,63,64,100,119,120,121,127,128,255,256,511,512,1023,1024,32767,32768,65534,65535)
BYTES=(0,1,2,3,4,15,16,31,32,63,64,127,128,129,254,255)
DWORDS=(0,1,127,128,255,256,299,300,301,1024,32767,32768,65535,0x7FFFFFFF,0x80000000,0xFFFFFFFF)


def input_blob(row,case,image):
    """Construct eight raw word knots without evaluating the curve or a publication."""
    if row!=dict(name='axis_words',address=0x13C48,size=16):
        raise ValueError('the timing remainder input constructor changes its complete physical axis')
    style,seed=case['axis_style'],case['axis_seed']
    if style==0:return image[row['address']:row['address']+row['size']]
    low=seed&7;step=(65535-low)//7
    shapes={1:lambda index:low+index*step,2:lambda index:low+(index//2)*(65535-low)//3,
        3:lambda index:(seed+(65535//7)*index)&65535,4:lambda index:65535-low-index*step,
        5:lambda index:seed,6:lambda index:0 if index<7 else 65535}
    return b''.join(shapes[style](index).to_bytes(2,'big') for index in range(8))


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    def values(field):return DWORDS if WIDTHS[field]==32 else WORDS if WIDTHS[field]==16 else BYTES
    for entry in contract.ENTRIES:
        for register in REGISTERS:
            for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
                add(entry,'complete-raw-register-width',**{register:value})
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):add(entry,'complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
        for variant in (0,7,255):add(entry,'complete-preserved-register-context',variant=variant)
        for name,address,width in RAM_FIELDS:
            for value in (0,(1<<(8*width))-1):add(entry,'complete-prior-RAM-preimage',**{name:value})
        for field in ENTRY_FIELDS[entry]:
            if field not in WIDTHS:continue
            for value in values(field):add(entry,'independent-complete-source-input',**{field:value})
    profiles=(dict(),dict(byte_24c5=0),dict(mode_flag=0),dict(byte_2459=32),dict(history_word=0),dict(history_word=64),
        dict(counter_reload=0,byte_24c0=0,first_gain=0,second_gain=0),
        dict(mode_flag=0,counter_reload=0,byte_24c0=0,first_gain=0,second_gain=0),
        dict(byte_24c2=1,byte_25fc=0),dict(byte_24c0=64,byte_25fc=1),
        dict(counter_reload=0,byte_24c0=0,byte_40e7=20,first_gain=0,second_gain=0))
    for profile in profiles:
        for field in ENTRY_FIELDS[0x4D99C]:
            if field not in WIDTHS:continue
            for value in values(field):
                changed=dict(profile);changed[field]=value
                add(0x4D99C,'independent-active-branch-source-alternative',**changed)
    for style in range(7):
        for seed in (0,1,32768,65535):
            for coordinate in (0,1,32767,32768,65534,65535):
                add(0x4D99C,'full-physical-axis-order-duplicates-floor-and-endpoint',axis_style=style,axis_seed=seed,word_237e=coordinate)
    for index,field in enumerate(CURVE_FIELDS):
        for coordinate in ((min(index,7)*65535)//7,min(65535,(min(index,7)*65535)//7+1)):
            for value in WORDS:add(0x4D99C,'every-curve-word-and-read-neighbor-with-fixed-other-inputs',word_237e=coordinate,**{field:value})
    for mode in (0,32):
        for first in (0,32):
            for second in (0,4):
                for old_byte in (0,127,128,255):
                    for other_byte in (0,127,128,255):
                        add(0x4D99C,'independent-signed-byte-negation-word-difference-and-caps',mode_flag=mode,
                            byte_24c5=first,byte_24cb=second,byte_11f9=old_byte,byte_11fa=other_byte)
    for flag in (0,1,2,3,255):
        for counter in (0,1,127,128,255):
            for history in DWORDS:
                add(0x4D99C,'complete-counter-history-raw32-and-signed-word-reload-lineage',byte_24c2=flag,byte_25fc=counter,history_word=history)
    pulse_profiles=(dict(),dict(byte_4184=64),dict(byte_24c9=32),dict(byte_4184=64,byte_24c9=32),
        dict(word_10ca=0,word_11bc=65535,word_241c=0,**{field:10 for field in MAXIMUM_FIELDS}))
    for profile in pulse_profiles:
        for field in ENTRY_FIELDS[0x521A8]:
            for value in values(field):
                changed=dict(profile);changed[field]=value
                add(0x521A8,'independent-active-pulse-selector-and-offset-source-alternative',**changed)
    for selected in (0,64):
        for speed in WORDS:
            for largest in (0,1,255,256,32767,32768,65535):
                add(0x521A8,'raw-selected-coordinate-wrapped-transform-and-six-word-maximum',byte_4184=selected,
                    word_10ca=speed,word_11bc=speed,word_241c=largest,**{field:largest for field in MAXIMUM_FIELDS})
    for field in (*MAXIMUM_FIELDS,'word_241c'):
        for value in WORDS:
            add(0x521A8,'each-independent-six-word-or-separate-maximum-input',
                **{name:(value if name==field else 0) for name in (*MAXIMUM_FIELDS,'word_241c')})
    for word in WORDS:
        for mode in (0,32):
            for offset in BYTES:
                for override in (0,1):add(0x521A8,'raw-numerator-offset-floor-both-real-quotient-and-remainder-calls',
                    word_192e=word,byte_24c9=mode,remainder_offset=offset,byte_4251=override)
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['axis_style']>6 or case['initial_sr']&~0x3F1):
        raise ValueError('a timing remainder input changes a complete raw RAM,curve,axis,configuration,register or SR width')


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
        raise ValueError('the timing remainder caller withdrawal original changes complete raw RAM, CPU or complete timing curve/axis/scalar/pool inputs')
