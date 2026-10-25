"""Explicit input-only contexts for the bounded vehicle/main contributor sequence."""

from kb import rpm_inhibit_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
KINDS=('contributors','maf-summary','shared-status','composite-status')
ENTRIES={'contributors':contract.ENTRY,'maf-summary':0x4EDD2,'shared-status':0x4EDF8,
    'composite-status':0x4EDEA}
FIELDS=('entry','rpm','speed','main_flags','vehicle_flags','vehicle_control','main_delay','vehicle_delay',
    'selector','condition1','condition2','condition3','config','t0','t1','t2','t3','t4','t5',
    'main_reload','vehicle_reload','speed_on','speed_off',
    'summary_flags','shared_status','summary_rpm','low_flags','high_flags','seed_flags','low_rpm',
    'low_gate1','low_gate2','high_gate1','high_gate2','hysteresis',
    'c0','c1','c2','c3','c4','c5','c6','c7','prior14','prior2','prior','variant','sr')
DEFAULTS=dict(rpm=600,speed=91,main_flags=0,vehicle_flags=0,vehicle_control=0,main_delay=0,vehicle_delay=0,
    selector=0,condition1=2,condition2=0,condition3=4,config=0x63,t0=612,t1=596,t2=596,t3=368,t4=0,t5=0,
    main_reload=0,vehicle_reload=0,speed_on=93,speed_off=91,
    summary_flags=0,shared_status=0,summary_rpm=192,
    low_flags=0,high_flags=0,seed_flags=0,low_rpm=0,low_gate1=0,low_gate2=0,
    high_gate1=0,high_gate2=0,hysteresis=16,c0=255,c1=255,c2=255,c3=255,c4=255,c5=255,c6=255,c7=255,
    prior14=0,prior2=0,prior=0,variant=0,sr=0)


def cases(declared,image):
    result=[]
    def add(kind='contributors',**changes):
        row=dict(DEFAULTS);row.update(changes)
        result.append(dict(index=len(result),kind=kind,entry=ENTRIES[kind],**row))
    for flags in range(256):
        add(main_flags=flags)
        add(vehicle_flags=flags,speed=92)
    for control in range(256):
        for flags in (0,1):add(vehicle_control=control,vehicle_flags=flags,speed=93)
    for speed in range(256):
        for flags in (0,1):add(speed=speed,vehicle_flags=flags)
    for selector in (0,0x10):
        for flags in (0,2,4,6,255):
            for rpm in (0,1,367,368,369,595,596,597,599,600,611,612,613,32768,65535):
                add(selector=selector,main_flags=flags,rpm=rpm)
    for config in (0,0x63,0x80,0xE3,0xFF):
        for bits in range(8):
            for selector in (0,0x10):
                for flags in (0,4):
                    add(config=config,condition1=2 if bits&1 else 0,condition2=32 if bits&2 else 0,
                        condition3=4 if bits&4 else 0,selector=selector,main_flags=flags,rpm=100)
    for count in range(256):
        add(main_delay=count,main_flags=2,rpm=612)
        add(vehicle_delay=count,vehicle_control=0x80,speed=93)
    for count in (0,1,2,255):
        add(main_reload=count,rpm=612)
        add(vehicle_reload=count,speed=93)
    for threshold in (0,599,600,601,612,65535):add(t0=threshold)
    for flags in (0,4):add(main_flags=flags)
    for flags in (0,32):add(config=0xE3,condition2=flags,rpm=100)
    for flags in (0,1):add(vehicle_flags=flags,speed=91)
    for prior in (0,1,0x80000000,0xFFFFFFFF):add(prior=prior,vehicle_flags=1,speed=91)
    for variant in range(4):
        for sr in (0,1,0x100,0x101,0x200,0x201,0x300,0x301):
            for prior in (0,1,0x80000000,0xFFFFFFFF):add(variant=variant,sr=sr,prior=prior)
    for flags in range(256):
        add('maf-summary',summary_flags=flags)
        add('shared-status',shared_status=flags)
    for rpm in range(256):add('maf-summary',summary_flags=128,summary_rpm=rpm)
    for kind in ('maf-summary','shared-status'):
        for prior in (0,1,0x80000000,0xFFFFFFFF):
            for prior2 in (0,1,0x80000000,0xFFFFFFFF):
                for prior14 in (0,1,0x80000000,0xFFFFFFFF):
                    add(kind,summary_flags=128,shared_status=2,prior=prior,prior2=prior2,prior14=prior14)
        for variant in range(4):
            for sr in (0,1,0x100,0x101,0x200,0x201,0x300,0x301):
                add(kind,summary_flags=128,shared_status=2,variant=variant,sr=sr,
                    prior=0x80000000,prior2=1,prior14=0x40000000)
    add('composite-status')
    for flags in range(256):
        add('composite-status',low_flags=flags,low_rpm=68,low_gate1=64,low_gate2=32)
        add('composite-status',high_flags=flags,rpm=500,high_gate1=4)
        add('composite-status',seed_flags=flags)
    for rpm in range(256):
        for flags in (0,1):
            add('composite-status',low_rpm=rpm,low_flags=flags,low_gate1=64,low_gate2=32)
    for speed in range(256):
        for table in ((0,32,64,96,128,160,192,255),(255,192,160,128,96,64,32,0),(128,)*8):
            add('composite-status',speed=speed,high_gate1=4,
                **{'c'+str(index):value for index,value in enumerate(table)})
    for flags in (0,4):
        for rpm in (0,1,499,500,509,510,511,32768,65535):
            for hysteresis in (0,1,16,65535):
                add('composite-status',high_flags=flags,rpm=rpm,hysteresis=hysteresis,high_gate1=4)
    for bits in range(16):
        for active in (0,1):
            add('composite-status',low_gate1=64 if bits&1 else 0,low_gate2=32 if bits&2 else 0,
                high_gate1=4 if bits&4 else 0,high_gate2=1 if bits&8 else 0,
                low_rpm=72 if active else 0,rpm=510 if active else 0)
    for variant in range(4):
        for sr in (0,1,0x100,0x101,0x200,0x201,0x300,0x301):
            for prior2 in (0,1,0x80000000,0xFFFFFFFF):
                add('composite-status',variant=variant,sr=sr,prior=0x80000000,
                    prior2=prior2,prior14=0x40000000)
    for prior in (0,1,0x80000000,0xFFFFFFFF):
        for prior2 in (0,1,0x80000000,0xFFFFFFFF):
            for prior14 in (0,1,0x80000000,0xFFFFFFFF):
                add('composite-status',prior=prior,prior2=prior2,prior14=prior14)
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+index*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for index in range(15)]
    registers[0]=case['prior']
    if case['kind']!='contributors':
        registers[2]=case['prior2'];registers[14]=case['prior14']
    return (*registers,contract.INCOMING_GBR,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000)


def memory(case):
    data=bytearray([0xA5])*RAM_SIZE
    data[0x11BC:0x11BE]=case['rpm'].to_bytes(2,'big')
    for at,key in ((0x110E,'speed'),(0x2497,'main_flags'),(0x24A6,'vehicle_flags'),
            (0x24A7,'vehicle_control'),(0x24F1,'main_delay'),(0x24F6,'vehicle_delay'),
            (0x2468,'selector'),(0x2499,'condition1'),(0x2494,'condition2'),(0x244F,'condition3')):
        data[at]=case[key]
    if case['kind']=='maf-summary':data[0x2448]=case['summary_flags'];data[0x11B2]=case['summary_rpm']
    elif case['kind']=='shared-status':data[0x418C]=case['shared_status']
    elif case['kind']=='composite-status':
        for at,key in ((0x2489,'low_flags'),(0x249F,'high_flags'),(0x41EA,'seed_flags'),
                (0x11B3,'low_rpm'),(0x245D,'low_gate1'),(0x2458,'low_gate2'),
                (0x24CE,'high_gate1'),(0x24D2,'high_gate2')):data[at]=case[key]
    data[0x9818:0x981C]=bytes.fromhex('a5c3d2e1')
    return bytes(data)


def calibration_spans(declared):
    return tuple((row['address'],row['size']) for row in contract.CALIBRATIONS)


def calibrations(declared,image,case):
    result={row['address']:image[row['address']:row['address']+row['size']] for row in contract.CALIBRATIONS}
    for at,key in ((0x8B38,'config'),(0x8C69,'main_reload'),(0x8CAF,'vehicle_reload'),
            (0x8DB7,'speed_on'),(0x8DC3,'speed_off')):result[at]=bytes([case[key]])
    result[0x934E]=b''.join(case['t'+str(index)].to_bytes(2,'big') for index in range(6))
    if case['kind']=='composite-status':
        result[0x9462]=case['hysteresis'].to_bytes(2,'big')
        result[0x12A32]=bytes(case['c'+str(index)] for index in range(8))
    return result


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=ENTRIES.get(case['kind']) or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('the RPM contributor original changes its complete explicit source, status, context or calibration input')
