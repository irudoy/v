"""Explicit byte seeds and declared word-array patterns over complete RAM."""

RAM_BASE=0x01000000
RAM_SIZE=65536
SEEDS=(0,1,0x0100,0x0101,0x7F7F,0x8080,0x7FFF,0x8000,0xFFFF)


def cases(declared,image):
    result=[]
    for window in declared['window']:
        for seed in SEEDS:
            index=len(result)
            result.append(dict(index=index,entry=window['start'],parent=window['parent'],seed=seed,
                variant=index%4,sr=(index&1)|((index&15)<<4)|((index&3)<<8)))
    if any(window['start']==0x2093E for window in declared['window']):
        for value in (0,1,2,127,128,254,255):
            result.append(dict(index=len(result),entry=0x2093E,parent=0x208F8,seed=0xA5,
                variant=0,sr=0,holdoff=value))
    return tuple(result)


def context(declared,case):
    window=next(row for row in declared['window'] if row['start']==case['entry'])
    registers=[(0x1728394A+index*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for index in range(15)]
    return (*registers,window['gbr'],0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000)


def memory(case):
    from kb import counter_array_contract as contract
    result=bytearray([case['seed']&255])*RAM_SIZE
    for row in contract.ARRAYS:
        if row['width_bytes']==2:
            start=row['first']&65535
            result[start:start+2*row['count']]=case['seed'].to_bytes(2,'big')*row['count']
    if 'holdoff' in case:
        if case['entry']!=0x2093E or type(case['holdoff']) is not int or not 0<=case['holdoff']<=255:
            raise ValueError('the holdoff input changes its exact byte operand or bounded counter entry')
        result[0x25FF]=case['holdoff']
    return bytes(result)


def calibrations(declared):
    return {row['address']:(RAM_BASE+(row['value']&65535)).to_bytes(4,'big') for row in declared['pool']}


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=case['entry'] or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared))):
        raise ValueError('the counter-array original changes a complete explicit input or ROM pointer')
