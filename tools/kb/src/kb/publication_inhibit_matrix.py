"""Explicit cached-gate and snapshot inputs; no expected driver outputs."""

RAM_BASE=0x01000000
RAM_SIZE=65536
KINDS=('cache','publish','snapshot')
PATTERNS=(('stock',0),('flat',0),('flat',1),('flat',128),('flat',200),('flat',255),
          ('rising',0),('falling',0))
RPM_VALUES=(0,95,96,97,127,159,160,161,223,224,225,287,288,289,350,351,352,65535)


def cases(declared,image):
    result=[]
    parent=0
    def add(pattern,flat,rpm,brake,fault,initial_mode=0,metadata=8,native_bit=0):
        nonlocal parent
        for stage,(kind,entry) in enumerate(zip(KINDS,declared['sequence'])):
            index=len(result)
            result.append(dict(index=index,parent=parent,stage=stage,kind=kind,entry=entry,
                pattern=pattern,flat=flat,rpm=rpm,brake=brake,fault=fault,
                initial_mode=initial_mode,metadata=metadata,native_bit=native_bit,
                variant=parent%4,sr=(index&1)|((index&15)<<4)|((index&3)<<8)))
        parent+=1
    for pattern,flat in PATTERNS:
        for rpm in RPM_VALUES:
            for brake in (0,128):
                for fault in (0,1):add(pattern,flat,rpm,brake,fault)
    for pattern,flat in PATTERNS:
        for brake in (0,128):add(pattern,flat,160,brake,1,initial_mode=32)
    for metadata,native_bit in ((0,0),(0,64),(8,64)):
        for brake in (0,128):add('flat',0,192,brake,1,metadata=metadata,native_bit=native_bit)
    return tuple(result)


def calibration_spans(declared):
    return ((0x1202E,4),)


def calibrations(declared,image,case):
    if case['pattern']=='stock':table=image[0x1202E:0x12032]
    elif case['pattern']=='flat':table=bytes([case['flat']])*4
    elif case['pattern']=='rising':table=bytes((0,1,128,255))
    elif case['pattern']=='falling':table=bytes((255,128,1,0))
    else:raise ValueError('the publication-inhibit input has an undeclared calibration pattern')
    return {0x1202E:table}


def context(declared,case):
    values=[(0x1728394A+reg*0x110203+case['variant']*0x1000101+case['stage']*0x01010101)&0xFFFFFFFF
        for reg in range(15)]
    if case['stage']==2:values[11]=0x22558
    return (*values,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000|case['rpm'])


def initial_memory(case):
    ram=bytearray(RAM_SIZE)
    ram[0x2459]=case['initial_mode']
    ram[0x2451]=case['brake']
    ram[0x257A]=173
    ram[0x4226]=case['metadata']
    ram[0x84C3]=case['native_bit']
    ram[0x24B8]=64
    ram[0x5718+3*0x14+1]=case['fault']*128
    ram[0x114A:0x114C]=case['rpm'].to_bytes(2,'big')
    ram[0x1E58:0x1E5A]=(0x1200).to_bytes(2,'big')
    for address in range(0x1F6E,0x1F78,2):
        ram[address:address+2]=min(case['rpm']+64,65535).to_bytes(2,'big')
    return bytes(ram)


def before(case,prior):
    if case['stage']==0:return initial_memory(case)
    if type(prior) is not bytes or len(prior)!=RAM_SIZE:
        raise ValueError('the publication-inhibit sequence lacks the previous actual complete RAM')
    memory=bytearray(prior)
    if case['stage']==1:memory[0x2459]|=32
    return bytes(memory)


def native_controls(memory):
    if type(memory) is not bytes or len(memory)!=RAM_SIZE:
        raise ValueError('the native publication-inhibit control view lacks its exact RAM input')
    return memory[0x8400:0x8500]
