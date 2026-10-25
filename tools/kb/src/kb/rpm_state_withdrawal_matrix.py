"""Input-only complete natural RPM exposure and transition-window contexts."""
from kb import test_contract
from kb import rpm_state_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('exposure', 6450, 2),
 ('source_flags', 9304, 1),
 ('reset_flags', 9295, 1),
 ('limit_flags', 16976, 1),
 ('configuration_state', 9423, 1),
 ('mode_flags', 16852, 1),
 ('boundary_state', 4366, 1),
 ('rpm', 4531, 1),
 ('transition_latch', 9367, 1),
 ('transition_clock', 5776, 1),
 ('edge_flags', 9299, 1),
 ('transition_flags', 9309, 1),
 ('warm_state', 4209, 1))
WIDTHS={n:w*8 for n,at,w in RAM_FIELDS}
WIDTHS.update({n:32 for n in REGISTERS})
WIDTHS.update({r['field']:r['size']*8 for r in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={n:0 for n in WIDTHS}
DEFAULTS.update({n:v for n,v in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,32768,32768,0x9ABC,0x01000000))})
DEFAULTS.update(exposure=500,boundary_state=3,rpm=100,transition_clock=5,warm_state=90,
    exposure_base=100,boundary_threshold=4,upper_rpm=116,lower_rpm=92,exposure_step=12,gate_configuration=1,
    restore_rpm=88,restore_count=150,entry_rpm=80,warm_threshold=85,entry_boundary=4,entry_count=60,variant=7,initial_sr=0)
ENTRY_FIELDS={0x4F7E0:('exposure','source_flags','reset_flags','limit_flags','configuration_state','mode_flags','boundary_state','rpm','disable_mask','exposure_base','boundary_threshold','upper_rpm','lower_rpm','exposure_step','gate_configuration'),
    0x4F9C4:('transition_latch','transition_clock','reset_flags','edge_flags','transition_flags','mode_flags','rpm','warm_state','boundary_state','disable_mask','restore_rpm','restore_count','entry_rpm','warm_threshold','entry_boundary','entry_count')}
BOUNDARIES={8:(0,1,2,4,8,12,31,32,64,80,88,92,100,108,116,127,128,150,254,255),
    16:(0,1,11,12,255,256,1199,1200,1201,32767,32768,65534,65535),
    32:(0,1,255,256,32767,32768,65535,0x7FFFFFFF,0x80000000,0xFFFFFFFF)}


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for entry,names in ENTRY_FIELDS.items():
        for name in names:
            for value in BOUNDARIES[WIDTHS[name]]:add(entry,'raw-width-sign-boundary-'+name,**{name:value})
        for name in REGISTERS:
            for value in (0,0x80000000,0xFFFFFFFF):add(entry,'complete-register-context',**{name:value})
        for variant in (0,7,255):
            for sr in (0,1,0x3F0,0x3F1):add(entry,'complete-SR-context',variant=variant,initial_sr=sr)
    for exposure in (0,1,11,12,1199,1200,1201,65535):
        for base in (0,1,100,65535):
            for step in (0,1,12,128,255):
                add(0x4F7E0,'exposure-product-increment-and-cap',exposure=exposure,exposure_base=base,exposure_step=step)
                add(0x4F7E0,'exposure-decrement-and-zero-floor',exposure=exposure,exposure_base=base,exposure_step=step,boundary_state=5)
    for name in ('reset_flags','limit_flags','configuration_state','mode_flags'):
        for value in BOUNDARIES[8]:
            add(0x4F7E0,'inhibit-set-status-reset-'+name,**{name:value},exposure=500)
            add(0x4F7E0,'inhibit-clear-status-retain-'+name,**{name:value},exposure=2000)
    for clock in (0,1,59,60,127,128,149,150,254,255):
        for latch in (0,1,127,128,255):
            for rpm in (0,80,88,100,127,128,255):
                add(0x4F9C4,'clock-latch-restore-byte-sign',transition_clock=clock,transition_latch=latch,rpm=rpm)
    for name in ('reset_flags','edge_flags','transition_flags','mode_flags'):
        for value in BOUNDARIES[8]:
            add(0x4F9C4,'transition-priority-status-'+name,**{name:value},transition_latch=128)
    for name in ('upper_rpm','lower_rpm','boundary_threshold','boundary_state'):
        for value in BOUNDARIES[8]:
            add(0x4F7E0,'fixed-other-byte-comparison-'+name,**{name:value})
            add(0x4F7E0,'fixed-other-inhibit-clear-invalid-'+name,**{name:value},exposure=2000)
    for name in ('restore_rpm','restore_count'):
        for value in BOUNDARIES[8]:
            add(0x4F9C4,'fixed-other-active-restore-'+name,**{name:value},transition_latch=128)
    return tuple(dict(row,index=i) for i,row in enumerate(inputs))


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
