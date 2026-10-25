"""Explicit sequenced ignition inputs; raw execution and outputs are separate."""

from kb import ignition_diagnostic_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
KINDS=('event','coordinate','command')
FLAT_VALUES=(0,1,4,7,8,255,65535)


def cases(declared,image):
    knots=tuple(int.from_bytes(image[0x13C48+offset:0x13C4A+offset],'big') for offset in range(0,16,2))
    coordinates=sorted({0,65535,*(value+delta for value in knots for delta in (-1,0,1) if 0<=value+delta<=65535),
        *((first+second)//2 for first,second in zip(knots,knots[1:]))})
    result=[]
    parent=0
    for pattern,flat in (('stock',0),*(('flat',value) for value in FLAT_VALUES),('rising',0),('falling',0)):
        for coordinate in coordinates:
            for bypass in (0,1):
                for upstream in (0,1):
                    for override in (0,1):
                        for stage,(kind,entry) in enumerate(zip(KINDS,contract.SEQUENCE)):
                            index=len(result)
                            result.append(dict(index=index,parent=parent,stage=stage,kind=kind,entry=entry,
                                pattern=pattern,flat=flat,coordinate=coordinate,bypass=bypass,
                                upstream=upstream,override=override,variant=parent%4,
                                sr=(index&1)|((index&15)<<4)|((index&3)<<8)))
                        parent+=1
    return tuple(result)


def calibration_spans(declared):
    return ((0x147DA,18),(0x13C48,16))


def calibrations(declared,image,case):
    table=bytearray(image[0x147DA:0x147EC])
    if case['pattern']=='flat':values=(case['flat'],)*8
    elif case['pattern']=='rising':values=tuple(range(8))
    elif case['pattern']=='falling':values=tuple(range(7,-1,-1))
    elif case['pattern']=='stock':values=None
    else:raise ValueError('the ignition diagnostic input has another declared calibration role')
    if values is not None:
        table[:16]=b''.join(value.to_bytes(2,'big') for value in values)
    # The neighboring operand stays stock even when all semantic table cells change.
    return {0x147DA:bytes(table),0x13C48:image[0x13C48:0x13C58]}


def context(declared,case):
    values=[(0x1728394A+reg*0x110203+case['variant']*0x1000101+case['stage']*0x01010101)&0xFFFFFFFF
            for reg in range(15)]
    return (*values,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000|case['coordinate'])


def initial_memory(case):
    ram=bytearray(RAM_SIZE)
    ram[0x24C0]=128
    ram[0x24CC]=case['bypass']*2
    ram[0x244F]=case['upstream']*32
    ram[0x4251]=case['override']
    ram[0x237E:0x2380]=case['coordinate'].to_bytes(2,'big')
    return bytes(ram)


def native_controls(memory):
    if type(memory) is not bytes or len(memory)!=RAM_SIZE:
        raise ValueError('the native ignition control view lacks its exact full RAM input')
    return memory[0x9900:0x9A00]
