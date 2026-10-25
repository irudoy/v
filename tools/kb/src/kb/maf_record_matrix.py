"""Explicit record-byte inputs, full helper indices and caller GBR premise."""

from kb import maf_record_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536


def cases(declared,image):
    result=[]
    for entry in (0x25E20,0x3C3C6):
        for flags in range(256):
            for status in ((0x36,) if entry==0x25E20 else (0,0x7F,0x80,0xFF)):
                for sr in (0,1):
                    result.append(dict(index=len(result),entry=entry,argument=0x129,
                        flags=flags,status=status,variant=0,sr=sr))
        for flags in (0,0x7F,0x80,0xFF):
            for status in (0,0x7F,0x80,0xFF):
                for sr in (0,1):
                    result.append(dict(index=len(result),entry=entry,argument=0x129,
                        flags=flags,status=status,variant=1,sr=sr))
    for argument in (0xA5C30129,0xFFFFFFFF):
        for flags in (0,0x7F,0x80,0xFF):
            for sr in (0,1):
                result.append(dict(index=len(result),entry=0x25E20,argument=argument,
                    flags=flags,status=0x36,variant=0,sr=sr))
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+index*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for index in range(15)]
    if case['entry']==0x25E20:registers[4]=case['argument']
    gbr=RAM_BASE+0x2449 if case['entry']==0x3C3C6 else 0x12344321
    return (*registers,gbr,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000)


def memory(case):
    result=bytearray([0xA5])*RAM_SIZE
    result[0x5A93:0x5A96]=bytes((0x36,case['flags'],0xA7));result[0x2449]=case['status']
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
        raise ValueError('the MAF record reader changes an exact member, sibling, index, GBR, status or complete input')
