"""Explicit pointer pairs, normalizer state and full splitter R4 inputs."""

RAM_BASE=0x01000000
RAM_SIZE=65536
COUNTS=(*range(26),0x7FFF,0x8000,0xFFFF)
REMAINDERS=(0,1,0x7F,0x80,0xF5,0xFF)
PHASES=(0,4,9,0xFF)
SPLIT_ARGUMENTS=(*range(256),0x100,0xFFFF,0x10000,0x7FFFFFFF,0x80000000,0xFFFFFFFF,0xA5C300FF)


def cases(declared,image):
    result=[]
    for pair_index,pair in enumerate(declared['pair']):
        for phase in PHASES:
            for count in COUNTS:
                for remainder in REMAINDERS:
                    result.append(dict(index=len(result),entry=0x28DC8,pair=pair_index,
                        word=pair['word'],byte=pair['byte'],phase=phase,count=count,remainder=remainder,argument=0,
                        variant=pair_index,sr=(phase&1)|((phase&15)<<4)|((pair_index&3)<<8)))
    for pair_index,pair in enumerate(declared['pair']):
        for argument in SPLIT_ARGUMENTS:
            for variant in (0,1):
                for sr in (0,1):
                    result.append(dict(index=len(result),entry=0x28E7C,pair=pair_index,
                        word=pair['word'],byte=pair['byte'],phase=0,count=0x1234,remainder=0xA5,
                        argument=argument,variant=variant,sr=sr))
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+index*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for index in range(15)]
    if case['entry']==0x28E7C:
        registers[4]=case['argument'];registers[5]=RAM_BASE+(case['word']&65535)
        registers[6]=RAM_BASE+(case['byte']&65535)
    else:
        registers[4]=RAM_BASE+(case['word']&65535)
        registers[5]=RAM_BASE+(case['byte']&65535)
    return (*registers,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000)


def memory(case):
    result=bytearray([0xA5])*RAM_SIZE
    at=case['word']&65535;result[at:at+2]=case['count'].to_bytes(2,'big')
    result[case['byte']&65535]=case['remainder'];result[0x13B2]=case['phase']
    return bytes(result)


def calibrations(declared):
    return {0x28E9E:bytes.fromhex('0126'),0x29020:bytes.fromhex('0100128c'),0x28EA0:bytes.fromhex('199a')}


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=case['entry'] or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared))):
        raise ValueError('the phase normalizer changes a complete pointer, phase, datum or ROM literal input')
