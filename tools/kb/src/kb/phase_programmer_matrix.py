"""Input-only stock literals and explicit post-guard period/remainder contexts."""

from pathlib import Path
import re

from kb import phase_programmer_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
PERIODS=(0,1,9,10,255,256,8191,8192,8193,16389,25000,32767,32768,65534,65535)
REMAINDERS=(0,1,4,8,9,10,119,127,128,254,255)


def legacy_inputs(root):
    source=(Path(root)/contract.LEGACY_INPUTS).read_text()
    rows=[]
    for line in source.splitlines():
        match=re.match(r'^\{(0x[0-9a-f]+)U,(0x[0-9a-f]+)U,(0x[0-9a-f]+)U,(0x[0-9a-f]+)U,',line)
        if match:rows.append(tuple(int(value,16) for value in match.groups()))
    count=re.search(r'^#define OFFSET_CASE_COUNT (\d+)U$',source,re.M)
    if count is None or len(rows)!=int(count[1]) or int(count[1])!=14118:
        raise ValueError('the phase programmer lacks its complete literal input-only stock source')
    return tuple(rows)


def cases(declared,image,*,root):
    result=[]
    for period,remainder,variant,sr in legacy_inputs(root):
        result.append(dict(index=len(result),entry=0x2B6D4,period=period,remainder=remainder,
            variant=variant,sr=sr))
    for period in PERIODS:
        for remainder in REMAINDERS:
            for variant in (0,1):
                for sr in (0,1):
                    result.append(dict(index=len(result),entry=0x2B6D4,period=period,remainder=remainder,
                        variant=variant,sr=sr))
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+index*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for index in range(15)]
    return (*registers,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000)


def memory(case):
    result=bytearray([0xA5])*RAM_SIZE
    result[0x22BC:0x22BE]=case['period'].to_bytes(2,'big');result[0x193B]=case['remainder']
    result[0x16C2:0x16C4]=bytes.fromhex('1234');result[0x166C]=0xA5
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
        raise ValueError('the phase programmer changes its complete post-guard period, remainder, context or literal input')
