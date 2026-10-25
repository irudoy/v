"""Input-only complete contexts, raw RAM and explicit configuration alternatives."""

from kb import test_contract
from kb import scalar_ram_leaf_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{index}' for index in range(8))
RAM_FIELDS=(('slew_a_current', 4487, 1),
 ('slew_a_target', 4225, 1),
 ('slew_b_current', 8073, 1),
 ('slew_b_target', 4220, 1),
 ('sum_word_a', 5970, 2),
 ('sum_byte_a', 5989, 1),
 ('sum_word_b', 5960, 2),
 ('sum_signed_a', 4656, 2),
 ('sum_byte_b', 5548, 1),
 ('sum_byte_c', 5111, 1),
 ('sum_signed_b', 5898, 2),
 ('sum_optional', 8034, 1),
 ('state_231a', 8986, 2),
 ('word_230c', 8972, 2),
 ('product_gain', 8936, 2),
 ('timing_first', 5647, 1),
 ('timing_second', 5648, 1),
 ('timing_offset', 4527, 1),
 ('combine_first', 8958, 1),
 ('combine_second', 8952, 1),
 ('combine_trim', 5719, 1),
 ('latch_flags', 16772, 1),
 ('latch_flag_state', 9426, 1),
 ('latch_mode', 4665, 1),
 ('latch_status', 9304, 1),
 ('latch_primary', 6192, 1),
 ('latch_alternate', 6193, 1),
 ('decay_flags', 9357, 1),
 ('decay_latched', 9725, 1),
 ('decay_state', 5395, 1),
 ('accumulator_delta', 5624, 4),
 ('accumulator_correction', 5594, 2),
 ('selector_flags', 9360, 1),
 ('selector_state', 9686, 1),
 ('selector_candidate', 6592, 2),
 ('selector_primary', 9274, 2),
 ('limit_flags', 16900, 1),
 ('limit_gate', 9295, 1),
 ('limit_current', 13108, 2),
 ('limit_threshold', 13038, 2))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update(sum_configuration=8,timing_configuration=8,decay_configuration=8,variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(
    0x12345678,0x87654321,0x87654321,0x00008000,0x1234,0x5678,0x9ABC,0x01000000))})
DEFAULTS.update(slew_a_current=30,slew_a_target=60,slew_b_current=30,slew_b_target=60,
    sum_word_a=100,sum_word_b=200,sum_byte_a=10,sum_byte_b=20,sum_byte_c=30,sum_optional=7,
    state_231a=512,word_230c=128,product_gain=16384,timing_first=30,timing_second=60,timing_offset=10,
    combine_first=50,combine_second=60,combine_trim=32,latch_flags=64,latch_flag_state=0xA5,
    latch_mode=3,latch_status=32,latch_primary=10,latch_alternate=20,decay_flags=16,decay_latched=0,
    decay_state=10,accumulator_delta=0xFFFFC000,accumulator_correction=256,
    selector_flags=2,selector_state=0,selector_candidate=50,selector_primary=100,
    limit_flags=0,limit_gate=32,limit_current=200,limit_threshold=100,
    sum_configuration=128,timing_configuration=2,decay_configuration=10,variant=7,initial_sr=0)
ENTRY_FIELDS={
    0x259BE:('raw_r4','raw_r5','raw_r6','raw_r7'),
    0x39588:('slew_a_current','slew_a_target'),0x39874:('slew_b_current','slew_b_target'),
    0x468B0:('sum_word_a','sum_word_b','sum_byte_a','sum_byte_b','sum_byte_c','sum_signed_a','sum_signed_b','sum_optional','sum_configuration'),
    0x4AB94:('state_231a','word_230c','product_gain'),
    0x4AF38:('timing_first','timing_second','timing_offset','timing_configuration'),
    0x4BB6A:('combine_first','combine_second','combine_trim'),
    0x4C136:('latch_flags','latch_flag_state','latch_mode','latch_status','latch_primary','latch_alternate'),
    0x4E112:('decay_flags','decay_latched','decay_state','decay_configuration'),
    0x554AE:('accumulator_delta','word_230c','accumulator_correction'),
    0x70D82:('selector_flags','selector_state','selector_candidate','selector_primary'),
    0xA5530:('limit_flags','limit_gate','limit_current','limit_threshold')}
BOUNDARIES={8:(0,1,2,4,7,8,15,16,31,32,63,64,127,128,254,255),
    16:(0,1,2,15,16,255,256,1023,16383,16384,32767,32768,65534,65535),
    32:(0,1,0x3FFF,0x4000,0x7FFF,0x8000,0x7FFEFFFF,0x7FFFFFFF,0x80000000,0x80003FFF,0xFFFFBFFF,0xFFFFC000,0xFFFFFFFF)}


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for entry in contract.ENTRIES:
        for name in ENTRY_FIELDS[entry]:
            for value in BOUNDARIES[WIDTHS[name]]:add(entry,'raw-boundary-'+name,**{name:value})
        for name in REGISTERS:
            for value in (0,0x80000000,0xFFFFFFFF):add(entry,'full-register-context',**{name:value})
        for variant in (0,7,255):
            for sr in (0,1,0x3F0,0x3F1):add(entry,'complete-SR-context',variant=variant,initial_sr=sr)
    for entry,prefix in ((0x39588,'slew_a'),(0x39874,'slew_b')):
        for left in (0,1,2,3,127,128,253,254,255):
            for right in (0,1,2,3,127,128,253,254,255):
                add(entry,'slew-interval',**{prefix+'_current':left,prefix+'_target':right})
    for left in (0,1,16383,16384,32767,65535):
        for right in (0,1,16383,16384,32767,65535):
            for gain in (0,1,16383,16384,32767,65535):
                add(0x4AB94,'product-wrap-cap',state_231a=left,word_230c=right,product_gain=gain)
    for flag in (0,128,255):
        for left in (0,32767,32768,65535):
            for right in (0,32767,32768,65535):
                add(0x468B0,'sum-signed-cap',sum_configuration=flag,sum_signed_a=left,sum_signed_b=right)
    for first in (0,30,127,128,255):
        for second in (0,60,127,128,255):
            for flag in (0,2,255):add(0x4AF38,'timing-interval',timing_first=first,timing_second=second,timing_configuration=flag)
    for first in (0,1,127,255):
        for second in (0,1,127,255):
            for trim in (0,1,127,255):add(0x4BB6A,'combine-cap',combine_first=first,combine_second=second,combine_trim=trim)
    for mode in (0,1,2,3,255):
        for flag in (0,64):
            for status in (0,32):add(0x4C136,'latch-selection',latch_mode=mode,latch_flags=flag,latch_status=status)
    for flag in (0,16):
        for latched in (0,1,128,255):
            for state in (0,1,2,127,128,129,254,255):
                add(0x4E112,'signed-byte-decay',decay_flags=flag,decay_latched=latched,decay_state=state)
    for delta in BOUNDARIES[32]:
        for word in (0,1,32767,65535):
            add(0x554AE,'accumulator-signed-wrap',accumulator_delta=delta,word_230c=word,accumulator_correction=word)
    for flag in (0,2):
        for state in (0,1):
            for candidate in (0,1,32767,32768,65535):
                for primary in (0,1,32767,32768,65535):
                    add(0x70D82,'signed-selector',selector_flags=flag,selector_state=state,
                        selector_candidate=candidate,selector_primary=primary)
    for flags in (0,8,128):
        for gate in (0,32,128,160):
            for current in (0,1,32767,32768,65535):
                for threshold in (0,1,32767,32768,65535):
                    add(0xA5530,'unsigned-limit-latch',limit_flags=flags,limit_gate=gate,
                        limit_current=current,limit_threshold=threshold)
    for left in (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
        for right in (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
            for subtract in (0,1,0x80000000,0xFFFFFFFF):
                for flag in (0,1,0x100,0x101,0xFFFFFFFF):
                    add(0x259BE,'signed-conditional-compare',raw_r4=left,raw_r5=right,raw_r6=subtract,raw_r7=flag)
    for name,changes in (
            ('latch_primary',dict(latch_mode=1)),('latch_alternate',dict(latch_mode=3,latch_flags=64)),
            ('latch_status',dict(latch_mode=3,latch_flags=0)),
            ('selector_state',dict(selector_candidate=150,selector_primary=100))):
        for value in BOUNDARIES[WIDTHS[name]]:
            add(0x4C136 if name.startswith('latch_') else 0x70D82,'fixed-other-positive-'+name,**changes,**{name:value})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr'] not in (0,1,0x3F0,0x3F1)):
        raise ValueError('a scalar RAM leaf input changes its exact entry, complete raw field width, context or SR domain')


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
        raise ValueError('the scalar RAM leaf original changes complete raw RAM, context or configuration/pool inputs')
