"""Typed inputs for conditional exhaust-target paths; no expected C outputs."""

from kb import test_contract

RAM_BASE=0x01000000
RAM_SIZE=65536
KINDS=('conditioned','hysteresis')
VALUES=(144,145,150,151,160,180,189)


def cases(declared,image):
    result=[]
    def add(kind,entry,**values):
        index=len(result)
        row=dict(index=index,kind=kind,entry=entry,selected=0,value=144,mode=0,
                 first=0,second=0,margin=0,latched=0,variant=index%4,
                 sr=(index&1)|((index&15)<<4)|((index&3)<<8))
        row.update(values)
        row.setdefault('bridge',0)
        row.setdefault('cold',row['value'] if row['selected']==0 else 173)
        row.setdefault('main',row['value'] if row['selected']==1 else 167)
        result.append(row)
    for selected in (0,1):
        for mode in (0,1,2):
            for value in VALUES:
                add('conditioned',0xBFE88,selected=selected,value=value,mode=mode)
    for cold,main in ((150,160),(151,180)):
        for selected in (0,1):
            add('conditioned',0xBFE88,selected=selected,value=cold if selected==0 else main,
                mode=0,bridge=1,cold=cold,main=main)
    for first,second,margin in ((0,0,0),(0,1,1),(1,0,0),(127,127,1),
                                (128,127,2),(255,255,255),(255,0,1)):
        for latched in (0,1,128,255):
            add('hysteresis',0x259D0,first=first,second=second,margin=margin,latched=latched)
    return tuple(result)


def context(declared,case):
    values=[(0x1728394A+reg*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for reg in range(15)]
    if case['kind']=='hysteresis':
        values[4:8]=[case['first'],case['second'],case['margin'],case['latched']]
    return (*values,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000|case['value'])


def memory(case):
    ram=bytearray(RAM_SIZE)
    # These are explicit test premises, not deductions about a natural caller.
    ram[0x248B]=(5 if case['mode']==0 else 0 if case['mode']==1 else 1)
    ram[0x1284]=1
    ram[0x1C90]=255
    ram[0x2327]=91
    ram[0x1071]=0 if case['selected']==0 else 255
    ram[0x1C5F]=case['cold']
    ram[0x1C5D]=case['main']
    return bytes(ram)


def require_input(declared,image,case,observed):
    if (observed['entry']!=case['entry']
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or observed['calibration_before']!={} or observed['calibration_after']!={}):
        raise ValueError('the exhaust-target original changes its explicit mode, source, register or calibration premises')


def calibration_spans(declared):
    return ()
