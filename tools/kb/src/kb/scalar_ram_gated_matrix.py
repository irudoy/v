"""Complete input-only flag, signed blend, bound and indexed byte contexts."""

from kb import test_contract
from kb import scalar_ram_gated_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{index}' for index in range(8))
FIXED_RAM_FIELDS=(('gate_high', 16773, 1),
 ('gate_low', 16767, 1),
 ('ready_mask', 16190, 1),
 ('status_mode', 6204, 1),
 ('status_gain', 6488, 1),
 ('status_load', 4288, 4),
 ('status_state', 4209, 1),
 ('status_flags', 9425, 1),
 ('blend_primary', 16766, 1),
 ('blend_secondary', 9371, 1),
 ('blend_status', 9311, 1),
 ('blend_weight', 9250, 2),
 ('blend_first', 6376, 2),
 ('blend_second', 6374, 2),
 ('bound_first', 13448, 2),
 ('bound_upper', 13452, 2),
 ('bound_third', 13446, 2),
 ('bound_fourth', 13450, 2),
 ('bound_alternate', 13468, 2),
 ('bound_default', 13472, 2),
 ('bound_cap', 13512, 2),
 ('bound_external', 16738, 2),
 ('bound_flags', 16806, 1),
 ('reset_mode', 8999, 1),
 ('reset_ready', 5304, 1),
 ('reset_flags', 5360, 1))
INDEXED_ARRAYS=(('candidate', 10296, 1),
 ('current', 16204, 1),
 ('request', 6828, 2),
 ('delay', 6448, 1),
 ('latch', 9576, 1))
INDEXED_ALIASES={('delay', 40): 'status_gain'}
RAM_FIELDS=(*FIXED_RAM_FIELDS,*(
    (f'{name}_{index:03d}',at+index*width,width) for name,at,width in INDEXED_ARRAYS for index in range(256)
    if (name,index) not in INDEXED_ALIASES))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(
    0x12345678,0x87654321,0x87654321,0x00008000,1,0,0x9ABC,0x01000000))})
DEFAULTS.update(gate_high=0,gate_low=0,ready_mask=255,status_mode=0,status_gain=5,status_load=20,
    status_state=15,status_flags=0xA5,status_threshold_low=10,status_threshold_high=20,
    blend_primary=0,blend_secondary=0,blend_status=0,blend_weight=32768,blend_first=100,blend_second=200,
    bound_first=100,bound_upper=400,bound_third=200,bound_fourth=300,bound_alternate=900,
    bound_default=700,bound_cap=500,bound_external=600,bound_flags=0,bound_configuration=0,
    bound_external_configuration=0,reset_mode=128,reset_ready=255,reset_flags=0x5A,
    reset_configuration=10,variant=7,initial_sr=0)
ARRAY_DEFAULTS=dict(candidate=10,current=20,request=0,delay=17,latch=0)
for name,at,width in INDEXED_ARRAYS:
    for index in range(256):
        if (name,index) not in INDEXED_ALIASES:DEFAULTS[f'{name}_{index:03d}']=ARRAY_DEFAULTS[name]
ENTRY_FIELDS={0x3D45C:('raw_r4','gate_high','gate_low','ready_mask','candidate','current'),
    0x44448:('status_mode','status_gain','status_load','status_state','status_flags',
        'status_threshold_low','status_threshold_high'),
    0x74C08:('blend_primary','blend_secondary','blend_status','blend_weight','blend_first','blend_second'),
    0x777FA:('bound_first','bound_upper','bound_third','bound_fourth','bound_alternate',
        'bound_default','bound_cap','bound_external','bound_flags','bound_configuration','bound_external_configuration'),
    0x907E8:('raw_r4','raw_r5','reset_mode','reset_ready','reset_flags','reset_configuration','request','latch')}
DOMAIN_WIDTHS=dict(WIDTHS,**{name:8*width for name,at,width in INDEXED_ARRAYS})
BOUNDARIES={8:(0,1,2,4,8,16,31,32,63,64,127,128,254,255),
    16:(0,1,127,128,255,256,32767,32768,65534,65535),
    32:(0,1,255,256,32767,32768,65535,0x7FFFFFFF,0x80000000,0xAAAA0001,0xFFFF0000,0xFFFFFFFF)}


def selected_index(entry,inputs):return inputs['raw_r4' if entry==0x3D45C else 'raw_r5']&255


def indexed_field(name,index):return INDEXED_ALIASES.get((name,index),f'{name}_{index:03d}')


def cases(declared,image):
    inputs=[];arrays={name for name,at,width in INDEXED_ARRAYS}
    def add(entry,kind,**changes):
        held=dict(DEFAULTS);held.update({name:value for name,value in changes.items() if name not in arrays})
        index=selected_index(entry,held)
        for name,value in changes.items():
            if name in arrays:
                field=indexed_field(name,index)
                if field in changes and changes[field]!=value:
                    raise ValueError('an indexed input disagrees with the same authoritative physical byte')
                held[field]=value
        inputs.append(dict(held,entry=entry,kind=kind))
    for entry in contract.ENTRIES:
        for name in ENTRY_FIELDS[entry]:
            for value in BOUNDARIES[DOMAIN_WIDTHS[name]]:add(entry,'raw-boundary-'+name,**{name:value})
        for name in REGISTERS:
            for value in (0,0x80000000,0xFFFFFFFF):add(entry,'complete-register-context',**{name:value})
        for variant in (0,7,255):
            for sr in (0,1,0x3F0,0x3F1):add(entry,'complete-SR-context',variant=variant,initial_sr=sr)
    for index in range(256):
        add(0x3D45C,'complete-byte-index-domain',raw_r4=index)
        add(0x907E8,'complete-byte-index-domain-active',raw_r5=index)
        add(0x907E8,'complete-byte-index-domain-reset',raw_r4=0,raw_r5=index)
    for flags in (0,64):
        for low in (0,32):
            for mask in (0,1,127,128,255):
                for candidate in (0,10,127,128,255):
                    for current in (0,20,127,128,255):
                        add(0x3D45C,'gated-indexed-minimum',gate_high=flags,gate_low=low,ready_mask=mask,
                            candidate=candidate,current=current)
    for mode in (0,1,2,255):
        for state in (0,9,10,15,19,20,127,128,255):
            for load in (0,49,50,51,0x7FFFFFFF,0xFFFFFFFF):
                add(0x44448,'status-gate-and-signed-byte-carriers',status_mode=mode,status_state=state,status_load=load)
    for weight in BOUNDARIES[16]:
        for first in (0,1,32767,32768,65535):
            for second in (0,1,32767,32768,65535):
                add(0x74C08,'signed-blend-wrap-and-endpoints',blend_weight=weight,blend_first=first,blend_second=second)
    for primary in (0,1):
        for external in (0,1):
            for flags in (0,8):
                for upper in (0,32767,32768,65535):
                    for cap in (0,32767,32768,65535):
                        add(0x777FA,'bound-selection-and-signed-minimum',bound_configuration=primary,
                            bound_external_configuration=external,bound_flags=flags,bound_upper=upper,bound_cap=cap)
    for active in (0,1):
        for mode in (0,127,128,255):
            for request in (0,1,32768,65535):
                for latch in (0,1,128,255):
                    for ready in (0,1,255):
                        add(0x907E8,'indexed-reset-and-delayed-flag-publication',raw_r4=active,
                            reset_mode=mode,request=request,latch=latch,reset_ready=ready)
    positives=(
        (0x44448,'status_gain',dict(status_state=127,status_load=51)),
        (0x44448,'status_threshold_low',dict(status_state=127,status_load=51)),
        (0x777FA,'bound_first',dict(bound_configuration=1)),
        (0x777FA,'bound_alternate',dict(bound_flags=8)),
        (0x777FA,'bound_cap',dict(bound_upper=65535)),
        (0x777FA,'bound_external',dict(bound_flags=8,bound_external_configuration=1)),
        (0x907E8,'latch',dict(reset_ready=0)),
        (0x907E8,'reset_configuration',dict(raw_r4=0)))
    for entry,name,changes in positives:
        for value in BOUNDARIES[DOMAIN_WIDTHS[name]]:add(entry,'fixed-other-positive-'+name,**changes,**{name:value})
    add(0x44448,'ordered-flag-read-modify-write',status_state=127,status_mode=2,status_flags=255,status_load=51)
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr'] not in (0,1,0x3F0,0x3F1)):
        raise ValueError('a scalar gated input changes an exact entry, raw width, independent indexed byte or complete context')


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
        raise ValueError('the scalar gated original changes complete raw indexed RAM, CPU or configuration/pool preimages')
