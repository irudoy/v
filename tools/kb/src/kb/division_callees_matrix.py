"""Direct division ABI inputs; caller provenance and datum semantics are separate."""

RAM_BASE=0x01000000
RAM_SIZE=65536
KINDS=('signed','unsigned')
ENTRIES=(0x21BBC,0x21CE0)
WORDS=(0,1,2,127,128,255,256,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFF)


def cases(declared,image):
    result=[]
    for kind,entry in zip(KINDS,ENTRIES):
        for divisor in WORDS:
            for dividend in WORDS:
                for initial in (0,1,0x100,0x101,0x200,0x201,0x300,0x301):
                    for previous in (0,0x044E,0xA5C3D2E1):
                        index=len(result)
                        result.append(dict(index=index,kind=kind,entry=entry,divisor=divisor,
                            dividend=dividend,previous_fault=previous,variant=index%4,
                            sr=initial|((index&15)<<4)))
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+reg*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for reg in range(15)]
    registers[0],registers[1]=case['divisor'],case['dividend']
    return (*registers,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000|(case['divisor']&65535))


def memory(case):
    result=bytearray([(0x5D+case['variant']*37)&255])*RAM_SIZE
    result[0x9818:0x981C]=case['previous_fault'].to_bytes(4,'big')
    return bytes(result)


def calibration_spans(declared):
    return ()


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=case['entry'] or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or observed['calibration_before']!={} or observed['calibration_after']!={}):
        raise ValueError('the division callee original changes its exact ABI, initial SR or prior fault-word input')
