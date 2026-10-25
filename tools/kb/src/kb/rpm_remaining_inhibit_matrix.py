"""Explicit remaining-RPM caller inputs with a fixed quiet diagnostic premise."""

from copy import deepcopy

from kb import rpm_remaining_inhibit_contract as contract,test_contract

RAM_BASE=0x01000000
RAM_SIZE=65536
BYTE_INPUTS=(('stationary_flags',0x247F),('vehicle_state',0x110E),('stationary_gate',0x244F),
    ('source_flags',0x2458),('readiness_timer',0x258A),('qualifier',0x1071),('bypass_flags',0x245D),
    ('rpm50',0x11AE),('thermal_flags',0x41F2),('thermal_gate',0x41EE),('temperature_gate',0x4209),
    ('diagnostic_flags',0x5720),('diagnostic_count',0x571E),('sustained_flags',0x247C),('rpm25',0x11B3),('ceiling_flags',0x249C),
    ('request',0x2714),('can_flags',0x2488),('can_status',0x4189),('limit_status',0x4250))
WORD_INPUTS=(('rpm16',0x11BC),('readiness',0x16A6),('exposure',0x1932))
CALIBRATION_FIELDS=('stationary_cut','stationary_restore','ready_threshold','qualifier_floor',
    'diagnostic_mode','temperature_threshold','thermal_hysteresis','thermal_rpm_threshold',
    'disable_mask','exposure_base','sustained_cut','sustained_restore','exposure_factor',
    'ceiling_hysteresis','ceiling_floor')
FIELDS=(*(name for name,at in BYTE_INPUTS),*(name for name,at in WORD_INPUTS),
    *CALIBRATION_FIELDS,'variant','entry_sr')
STOCK_CURVE=(128,129,129,129,130,130,130,130,132,133,169,255,255,255,255,255)
DEFAULTS=dict(stationary_flags=8,vehicle_state=0,stationary_gate=4,source_flags=0,readiness_timer=1,
    qualifier=0,bypass_flags=0,rpm50=32,thermal_flags=8,thermal_gate=0,temperature_gate=0,
    diagnostic_flags=16,diagnostic_count=40,sustained_flags=0,rpm25=80,ceiling_flags=0,request=40,can_flags=0,
    can_status=0,limit_status=0,rpm16=232,readiness=381,exposure=24000,
    stationary_cut=36,stationary_restore=30,ready_threshold=381,qualifier_floor=0,
    diagnostic_mode=1,temperature_threshold=190,thermal_hysteresis=8,thermal_rpm_threshold=76,
    disable_mask=24,exposure_base=2000,sustained_cut=72,sustained_restore=60,exposure_factor=12,
    ceiling_hysteresis=6,ceiling_floor=36,variant=0,entry_sr=0,curve=list(STOCK_CURVE))


def cases(declared,image):
    result=[]
    def add(entry,tag,**changes):
        value=deepcopy(DEFAULTS);value.update(deepcopy(changes))
        result.append(dict(index=len(result),entry=entry,kind=tag,**value))
    for entry in contract.ENTRIES:
        for variant in (0,1):
            for sr in (0,1,0x301):add(entry,'complete-context',variant=variant,entry_sr=sr)
    for flags in range(256):
        add(0x4EDC6,'stationary-state',stationary_flags=flags)
        add(0x4EDC6,'thermal-state',thermal_flags=flags)
        add(0x4EDE4,'sustained-state',sustained_flags=flags,rpm25=66)
        add(0x4EE00,'ceiling-state',ceiling_flags=flags,rpm50=38)
    for value in (0,1,2,3,4,127,128,255):
        add(0x4EDC6,'stationary-input',vehicle_state=value)
        add(0x4EDC6,'stationary-input',stationary_gate=value)
        add(0x4EDC6,'source-gate',source_flags=value)
        add(0x4EDC6,'timer-input',readiness_timer=value)
        add(0x4EDC6,'readiness-qualifier',qualifier=value,qualifier_floor=128)
        add(0x4EDC6,'readiness-bypass',qualifier=0,qualifier_floor=128,bypass_flags=value)
        add(0x4EDC6,'thermal-diagnostic-flag',diagnostic_flags=value)
        add(0x4EDC6,'thermal-hysteresis',thermal_gate=value)
        add(0x4EDC6,'temperature-hysteresis',temperature_gate=value)
        add(0x4EE00,'CAN-status',can_status=value)
        add(0x4EE00,'CAN-status',limit_status=value)
        add(0x4EE00,'CAN-request',request=value)
    for value in (0,1,29,30,31,32,35,36,37,59,60,61,65,66,71,72,73,75,76,77,127,128,254,255):
        for flags in (8,0x28,0xFF):add(0x4EDC6,'stationary-RPM',rpm50=value,stationary_flags=flags)
        for flags in (0,0x80,0xFF):add(0x4EDE4,'sustained-RPM',rpm25=value,sustained_flags=flags)
        for flags in (0,0x80):add(0x4EE00,'ceiling-RPM',rpm50=value,ceiling_flags=flags)
        for flags in (0,8):add(0x4EDC6,'thermal-RPM',rpm25=value,thermal_gate=flags)
    for value in (0,1,380,381,382,32767,32768,65534,65535):
        add(0x4EDC6,'readiness-word',readiness=value)
        add(0x4EDC6,'readiness-threshold',ready_threshold=value)
    for value in (0,1,23999,24000,24001,32767,32768,65534,65535):
        add(0x4EDE4,'exposure-word',exposure=value)
    for first,second in ((0,0),(1,1),(255,1),(255,255),(256,255),(257,255),(258,255),(65535,255)):
        for exposure in (0,1,65534,65535):
            add(0x4EDE4,'saturated-exposure-threshold',exposure_base=first,
                exposure_factor=second,exposure=exposure)
    for mask in (0,24,127,128,152,255):
        add(0x4EDE4,'sustained-mask',disable_mask=mask)
        add(0x4EE00,'ceiling-mask',disable_mask=mask)
    for threshold in (0,1,127,128,255):
        add(0x4EDC6,'stationary-calibration',stationary_cut=threshold,rpm50=36)
        add(0x4EDC6,'stationary-calibration',stationary_restore=threshold,rpm50=32,stationary_flags=0x28)
        add(0x4EDC6,'thermal-calibration',temperature_threshold=threshold,qualifier=190)
        add(0x4EDC6,'thermal-calibration',thermal_rpm_threshold=threshold,rpm25=76)
        add(0x4EDC6,'thermal-calibration',thermal_hysteresis=threshold,rpm25=70,thermal_gate=8)
        add(0x4EE00,'ceiling-calibration',ceiling_floor=threshold,request=1)
        add(0x4EE00,'ceiling-calibration',ceiling_hysteresis=threshold,ceiling_flags=0x80)
    for mode in (0,1):
        for flags in (0,8,0x20,0x28,0xFF):add(0x4EDC6,'thermal-mode',diagnostic_mode=mode,thermal_flags=flags)
    for count in (40,255):add(0x4EDC6,'quiet-diagnostic-count',diagnostic_count=count)
    curves=(list(STOCK_CURVE),[0]*16,[255]*16,list(range(0,256,17)),list(range(255,-1,-17)),[0,255]*8)
    for curve in curves:
        for coordinate in range(256):
            add(0x4EDC6,'stationary-byte16-curve',curve=curve,readiness_timer=0,
                rpm16=160+coordinate*2,readiness=65535 if coordinate&1 else 0)
    for rpm in (0,1,158,159,160,161,162,669,670,671,32767,32768,65534,65535):
        for curve in ([0]*16,[128]*16,[255]*16):
            add(0x4EDC6,'stationary-signed-clamp',readiness_timer=0,rpm16=rpm,curve=curve)
    # Fixed-other alternatives bind the actual caller result, not a copied flag.
    for cut in (30,40):add(0x4EDC6,'positive-cut',rpm50=36,stationary_cut=cut)
    for restore in (30,40):add(0x4EDC6,'positive-restore',rpm50=36,
        stationary_flags=0x28,stationary_restore=restore)
    for flags in (8,0x28):add(0x4EDC6,'positive-stationary-state',rpm50=32,stationary_flags=flags)
    for flags in (0,8):add(0x4EDC6,'positive-thermal-state',thermal_flags=flags)
    for flags in (0,0x80):
        add(0x4EDE4,'positive-sustained-state',rpm25=66,sustained_flags=flags)
        add(0x4EE00,'positive-ceiling-state',rpm50=38,ceiling_flags=flags)
    return tuple(result)


def context(declared,case):
    variant=case['variant']
    if variant not in (0,1):raise ValueError('the remaining RPM input changes its complete context variant')
    registers=[(0x1728394A+index*0x110203+variant*0x1000101)&0xFFFFFFFF for index in range(15)]
    registers[0]=0;registers[14]=0x3E5F6A00
    return (*registers,contract.INCOMING_GBR,0x13579BDF,
        0x9274B6D8 if variant else 0x2468ACE0,case['entry_sr'],0xB6C70000)


def memory(case):
    result=bytearray([0xA5])*RAM_SIZE
    for name,at in BYTE_INPUTS:result[at]=case[name]
    for name,at in WORD_INPUTS:result[at:at+2]=case[name].to_bytes(2,'big')
    result[0x4184]=0xC0
    return bytes(result)


def calibrations(declared,image,case):
    return {0x85D9:bytes([case['stationary_cut'],case['stationary_restore']]),
        0x911C:case['ready_threshold'].to_bytes(2,'big'),0x8D0E:bytes([case['qualifier_floor']]),
        0x124D2:bytes(case['curve']),0x186C9:bytes([case['diagnostic_mode']]),
        0x8D15:bytes([case['temperature_threshold']]),0x8957:bytes([case['thermal_hysteresis']]),
        0x88ED:bytes([case['thermal_rpm_threshold']]),0x8B3F:bytes([case['disable_mask']]),
        0x90E0:case['exposure_base'].to_bytes(2,'big'),
        0x84DA:bytes([case['sustained_cut'],0x74,0x5C,case['sustained_restore'],case['exposure_factor']]),
        0x89FC:bytes([case['ceiling_hysteresis'],case['ceiling_floor']])}


def require_input(declared,image,case,observed):
    wanted=calibrations(declared,image,case)
    if (case['entry'] not in contract.ENTRIES or case['diagnostic_mode'] not in (0,1)
            or not 40<=case['diagnostic_count']<=255
            or observed['entry']!=case['entry']
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],wanted)
            or not test_contract.exact(observed['calibration_after'],wanted)):
        raise ValueError('the remaining RPM original changes complete explicit input or quiet diagnostic premises')
