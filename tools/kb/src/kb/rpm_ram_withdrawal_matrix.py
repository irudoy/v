"""Input-only complete natural RPM helper context and controlled byte/word sources."""

from kb import test_contract
from kb import rpm_ram_withdrawal_path_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{index}' for index in range(8))
RAM_FIELDS=(('maf_fault_flags', 9288, 1),
 ('maf_rpm', 4530, 1),
 ('sustained_flags', 9340, 1),
 ('exposure', 6450, 2),
 ('sustained_rpm', 4531, 1),
 ('delay_limit_flags', 16976, 1),
 ('delay_source_flags', 9304, 1),
 ('delay_state', 4202, 1))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:8*row['size'] for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(
    0x12345678,0x87654321,0x87654321,0x00008000,1,0x8000,0x9ABC,0x01000000))})
DEFAULTS.update(maf_fault_flags=128,maf_rpm=200,sustained_flags=0,exposure=24000,sustained_rpm=80,
    disable_mask=24,exposure_base=2000,sustained_cut=72,sustained_restore=60,exposure_factor=12,
    delay_limit_flags=0,delay_source_flags=0,delay_state=5,delay_threshold=4,delay_configuration=0,
    delay_00=10,delay_01=20,delay_11=30,delay_12=40,delay_13=50,variant=7,initial_sr=0)
ENTRY_FIELDS={0x4F736:('maf_fault_flags','maf_rpm'),
    0x4F958:('sustained_flags','exposure','sustained_rpm','disable_mask','exposure_base',
        'sustained_cut','sustained_restore','exposure_factor'),
    0x5038A:('raw_r4','delay_limit_flags','delay_source_flags','delay_state','delay_threshold',
        'delay_configuration','delay_00','delay_01','delay_11','delay_12','delay_13')}
BOUNDARIES={8:(0,1,2,4,8,31,32,63,64,127,128,191,192,254,255),
    16:(0,1,31,32,255,256,32767,32768,65534,65535),
    32:(0,1,2,255,256,32767,32768,65535,0x7FFFFFFF,0x80000000,0xAAAA0001,0xFFFF0000,0xFFFFFFFF)}


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for entry in contract.ENTRIES:
        for name in ENTRY_FIELDS[entry]:
            for value in BOUNDARIES[WIDTHS[name]]:add(entry,'raw-boundary-'+name,**{name:value})
        for name in REGISTERS:
            for value in (0,0x80000000,0xFFFFFFFF):add(entry,'complete-register-context',**{name:value})
        for variant in (0,7,255):
            for sr in (0,1,0x3F0,0x3F1):add(entry,'complete-SR-context',variant=variant,initial_sr=sr)
    for flags in (0,1,127,128,255):
        for rpm in (0,1,127,128,191,192,193,255):
            add(0x4F736,'MAF-summary-signed-load-unsigned-compare',maf_fault_flags=flags,maf_rpm=rpm)
    for base in (0,1,255,256,32767,32768,65535):
        for factor in (0,1,12,127,128,255):
            for exposure in (0,1,23999,24000,24001,32768,65535):
                add(0x4F958,'unsigned-word-product-cap',exposure_base=base,exposure_factor=factor,exposure=exposure)
    for flags in (0,127,128,255):
        for rpm in (0,59,60,61,66,71,72,73,127,128,255):
            for disabled in (0,128):
                add(0x4F958,'sustained-state-retain-set-clear',sustained_flags=flags,sustained_rpm=rpm,disable_mask=disabled)
    for argument in (0,1,2,3,255,0x80000000,0xFFFFFFFF):
        for limit in (0,128):
            for flags in (0,32):
                for state in (0,3,4,5,127,128,255):
                    for configuration in (0,128):
                        add(0x5038A,'delay-gates-full-argument-and-configuration',raw_r4=argument,
                            delay_limit_flags=limit,delay_source_flags=flags,delay_state=state,delay_configuration=configuration)
    positives=(
        (0x4F958,'sustained_flags',dict(sustained_rpm=66)),
        (0x5038A,'delay_state',dict(delay_source_flags=32)),
        (0x5038A,'delay_threshold',dict(delay_source_flags=32)),
        (0x5038A,'delay_configuration',dict(raw_r4=2)),
        (0x5038A,'delay_00',dict(raw_r4=2,delay_configuration=128)),
        (0x5038A,'delay_01',dict(raw_r4=2,delay_configuration=0)),
        (0x5038A,'delay_12',dict(raw_r4=0,delay_configuration=128)),
        (0x5038A,'delay_13',dict(raw_r4=0,delay_configuration=0)))
    for entry,name,changes in positives:
        for value in BOUNDARIES[WIDTHS[name]]:add(entry,'fixed-other-positive-'+name,**changes,**{name:value})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr'] not in (0,1,0x3F0,0x3F1)):
        raise ValueError('an RPM withdrawal input changes a complete raw width, entry, argument, configuration or SR context')


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
        raise ValueError('the RPM withdrawal original changes complete raw RAM, CPU or byte/word configuration/pool inputs')
