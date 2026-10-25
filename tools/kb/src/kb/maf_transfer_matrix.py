"""Explicit two-channel ADC16 inputs and independent curve-root alternatives."""

from kb import maf_transfer_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
ADCS=(0,1,15,16,31,63,64,255,256,1007,1008,1023,1024,2047,4095,4096,65535)


def cases(declared,image):
    result=[]
    for adc in ADCS:
        for first,second in ((adc,0),(0,adc),(adc,adc)):
            for profile in (0,5):
                for variant in (0,1):
                    for sr in (0,1):
                        result.append(dict(index=len(result),entry=0x3A922,adc1=first,adc2=second,
                            profile=profile,variant=variant,sr=sr))
    for profile in range(5):
        for variant in (0,1):
            for sr in (0,1):
                result.append(dict(index=len(result),entry=0x3A922,adc1=0,adc2=0,
                    profile=profile,variant=variant,sr=sr))
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+index*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for index in range(15)]
    registers[14]=RAM_BASE+0x1E1C
    return (*registers,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000)


def memory(case):
    result=bytearray([0xA5])*RAM_SIZE
    result[0x1E48:0x1E4A]=case['adc1'].to_bytes(2,'big')
    result[0x1E4A:0x1E4C]=case['adc2'].to_bytes(2,'big')
    return bytes(result)


def calibrations(declared,image,case):
    result={row['address']:bytes(image[row['address']:row['address']+row['size']]) for row in contract.POOLS}
    pointers=bytearray(result[0x3AB60]);pointers[8:12]=bytes.fromhex('01001048');result[0x3AB60]=bytes(pointers)
    curves=bytearray(result[0x141F4]);profile=case['profile']
    if profile in (1,2,3,4):
        at=0 if profile in (1,2) else 128
        curves[at:at+2]=(1000 if profile in (1,3) else 1500).to_bytes(2,'big')
    elif profile==5:
        for channel in (0,1):
            for cell in range(64):
                at=128*channel+2*cell;curves[at:at+2]=(60000-500*cell).to_bytes(2,'big')
    elif profile!=0:raise ValueError('the MAF curve capture changes an explicit calibration role')
    result[0x141F4]=bytes(curves)
    return result


def require_input(declared,image,case,observed):
    from kb import test_contract
    wanted=calibrations(declared,image,case)
    if (observed['entry']!=case['entry'] or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],wanted)
            or not test_contract.exact(observed['calibration_after'],wanted)):
        raise ValueError('the MAF curve slice changes a complete ADC16, R14, memory or ROM input')
