"""Independent raw mask bytes and explicit bounded adjustment entry premises."""

from itertools import product

from kb import closed_loop_admission_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
FIELDS=('mask2c','mask2e','mask30','mask39')


def cases(declared,image):
    result=[];seen=set()
    def append(entry,values,variant,sr):
        identity=(entry,*values,variant,sr)
        if identity in seen:return
        seen.add(identity)
        result.append(dict(index=len(result),entry=entry,**dict(zip(FIELDS,values)),variant=variant,sr=sr))
    for entry in contract.ENTRIES:
        indices=(0,1,2) if entry==contract.ENTRIES[0] else (3,)
        for index in indices:
            for value in range(256):
                values=[0,0,0,0];values[index]=value
                for sr in (0,1):append(entry,values,0,sr)
        if entry==contract.ENTRIES[0]:
            for values in product(range(4),repeat=3):append(entry,(*values,0),0,0)
        for value in (0,1,2,3,0x7F,0x80,0xFF):
            for sr in (0,1):append(entry,(value,)*4,1,sr)
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+index*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for index in range(15)]
    if case['entry']==contract.ENTRIES[1]:registers[8:11]=(1,0,2)
    return (*registers,contract.INCOMING['gbr'],0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000)


def memory(case):
    result=bytearray([0xA5])*RAM_SIZE
    for row,field in zip(contract.DECODERS,FIELDS):result[row['input']&65535]=case[field]
    return bytes(result)


def calibrations(declared):
    return {row['address']:(RAM_BASE+(row['value']&65535) if row['address'] in contract.ALIASES else row['value'])
        .to_bytes(row['size'],'big') for row in contract.POOLS}


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=case['entry'] or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared))):
        raise ValueError('the admission decoder changes an exact raw byte, GBR, register premise or complete input')
