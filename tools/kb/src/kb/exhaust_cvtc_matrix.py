"""Input-only natural bank2 CVTC contexts, boundaries and fixed-other alternatives."""

from kb import test_contract
from kb import exhaust_cvtc_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
DEFAULTS=dict(raw_r4=0xA5C30001,mode=1,flags=5,previous_mask=2,current_mask=0,
    current=512,lag=256,error=1000,term_a=32768,term_b=32768,accumulator=0x09000000,
    payload=0x01000000,battery=150,coordinate=120,configuration=8,coefficient=8866,
    decay=10,curve_kind=0,variant=7,initial_sr=0)
RAM_FIELDS=(('mode',0x1B1D,1),('flags',0x248B,1),('previous_mask',0x1246,1),
    ('current_mask',0x1284,1),('current',0x1AAE,2),('lag',0x1AB6,2),('error',0x1B1A,2),
    ('term_a',0x1A88,2),('term_b',0x1A9A,2),('accumulator',0x1A94,4),('payload',0x1AA8,4),
    ('battery',0x1108,1),('coordinate',0x2772,1))
CURVES=(bytes((102,102,102,106,113,123,128,128,128)),
    bytes((255,224,192,160,128,96,64,32,0)),bytes((0,32,64,96,128,160,192,224,255)),
    bytes(9),bytes([255])*9)


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for mode in (0,1,2,128,255):
        for flags in (0,1,4,5):
            for previous in (0,2):
                for current in (0,1,1024):
                    add(0xC1DEC,'state-transition',mode=mode,flags=flags,previous_mask=previous,current=current)
    for coordinate in (0,49,50,51,89,90,91,99,100,101,109,110,111,119,120,121,
            129,130,131,134,135,136,169,170,171,255):
        for curve in range(len(CURVES)):
            add(0xC1DEC,'curve-boundary',coordinate=coordinate,curve_kind=curve)
    for error in (0,1,7,255,256,1024,32767,32768,65535):
        for coefficient in (0,1,625,8866,32768,65535):
            add(0xC1DEC,'error-product',error=error,coefficient=coefficient)
    for term_a in (0,1,32767,32768,65535):
        for term_b in (0,32768,65535):
            for accumulator in (0,0x07FFFFFF,0x08000000,0x08000001,0x0C000000,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
                add(0xC1DEC,'alternate-wrap',configuration=0,term_a=term_a,term_b=term_b,accumulator=accumulator)
    for mode in (0,1,2,128,255):
        for current in (0,1,25,26,1024,1025,65535):
            for lag in (0,1,25,26,1024,65535):
                for previous,current_mask in ((0,0),(0,2),(2,0),(2,2)):
                    add(0xC2040,'duty-transition',mode=mode,current=current,lag=lag,
                        previous_mask=previous,current_mask=current_mask)
    for payload in (0,1,255,256,65535,65536,0x00FFFFFF,0x01000000,0x04000000,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
        for battery in (1,2,149,150,151,255):
            add(0xC2040,'request-division',payload=payload,battery=battery)
    for decay in (0,1,10,127,128,254,255):
        add(0xC2040,'decay-boundary',mode=2,previous_mask=0,decay=decay,current=65535,lag=65535)
    for entry in contract.ENTRIES:
        for sr in (0,1,0x3F0,0x3F1):
            for variant in (0,7,255):
                add(entry,'complete-context',initial_sr=sr,variant=variant,raw_r4=(0xFFFF0001 if variant else 1))
    # Each positive family changes one complete physical input with all others fixed.
    for mode in (0,1,2):
        add(0xC1DEC,'positive-state-reader',mode=mode,flags=1)
        add(0xC2040,'positive-mode-duty',mode=mode)
    for flags in (0,5):add(0xC1DEC,'positive-mode-store',mode=0,flags=flags)
    for current in (0,512):
        add(0xC1DEC,'positive-current-state',mode=2,flags=1,previous_mask=0,current=current)
        add(0xC2040,'positive-lag-store',current=current,previous_mask=0,current_mask=2)
    for error in (0,1000,65535):add(0xC1DEC,'positive-error-payload',error=error)
    for lag in (0,256,65535):add(0xC2040,'positive-lag-duty',mode=2,previous_mask=0,lag=lag)
    for payload in (0,0x01000000,0x04000000):add(0xC2040,'positive-payload-duty',payload=payload)
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*DEFAULTS,'entry','kind','index'}
            or case['entry'] not in contract.ENTRIES or type(case['entry']) is not int
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int for name in DEFAULTS)
            or not 0<=case['raw_r4']<=0xFFFFFFFF or case['raw_r4']&255!=1
            or case['battery']==0 or case['curve_kind'] not in range(len(CURVES))
            or case['initial_sr'] not in (0,1,0x3F0,0x3F1)):
        raise ValueError('the CVTC input leaves its explicit natural bank2 or nonzero-divisor premises')
    for name,offset,width in RAM_FIELDS:
        if not 0<=case[name]<(1<<(width*8)):raise ValueError('a CVTC physical input changes its exact raw width')
    if (any(not 0<=case[key]<=255 for key in ('configuration','decay','variant'))
            or not 0<=case['coefficient']<=65535):
        raise ValueError('a CVTC calibration input changes its byte or word domain')


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+index*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for index in range(15)]
    registers[4]=case['raw_r4']
    return (*registers,0x456789AB,0x13579BDF,0x2468ACE0,case['initial_sr'],0xB6C70000)


def memory(case):
    require_case(case);result=bytearray([0xA5])*RAM_SIZE
    for name,offset,width in RAM_FIELDS:result[offset:offset+width]=case[name].to_bytes(width,'big')
    return bytes(result)


def calibrations(declared,image,case):
    require_case(case)
    result={row['address']:image[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}
    for row in contract.UNIT['aliases']:
        at=row['address'];data=bytearray(result[at]);data[:4]=row['alias'].to_bytes(4,'big');result[at]=bytes(data)
    result[0x8615]=bytes((case['configuration'],));result[0x8DE1]=bytes((case['decay'],))
    result[0x9212]=image[0x9212:0x9214]+case['coefficient'].to_bytes(2,'big')
    result[0x1205A]=CURVES[case['curve_kind']]
    return result


def require_input(declared,image,case,observed):
    if (not test_contract.exact(observed['entry'],case['entry'])
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('the CVTC original changes a complete bank2 CPU, RAM or calibration input')
