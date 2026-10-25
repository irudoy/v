"""Explicit complete-RAM seeds and incoming registers for exact clear paths."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536


def cases(declared,image):
    result=[]
    for window in declared['window']:
        for seed in (0x25,0xA5,0xFF):
            index=len(result)
            result.append(dict(index=index,entry=window['start'],parent=window['parent'],seed=seed,
                variant=index%4,sr=(index&1)|((index&15)<<4)|((index&3)<<8)))
    return tuple(result)


def context(declared,case):
    window=next(row for row in declared['window'] if row['start']==case['entry'])
    registers=[(0x1728394A+index*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for index in range(15)]
    return (*registers,window['gbr'],0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000)


def memory(case):
    return bytes([case['seed']])*RAM_SIZE


def calibrations(declared):
    from kb import ram_initialization_contract as contract
    return {row['address']:((RAM_BASE+(row['value']&65535))
            if row['address'] in contract.ALIASES else row['value']).to_bytes(4,'big')
            for row in declared['pool']}


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=case['entry']
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared))):
        raise ValueError('the RAM initialization original changes an explicit complete input or ROM descriptor')
