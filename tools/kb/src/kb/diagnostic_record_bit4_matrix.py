"""Input-only explicit record indices, complete byte preimages and ordinary CPU context."""
from kb import test_contract
from kb import diagnostic_record_bit4_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=tuple((f'record_{index:03x}_{member}',0x5718+3*index+member,1)
    for index in contract.INDICES for member in range(3))+(('prior_508c',0x508C,1),)
WIDTHS={name:32 for name in REGISTERS}
WIDTHS.update({name:8 for name,offset,width in RAM_FIELDS})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,
    (0x12345678,0x87654321,0x80000000,0xFFFFFFFF,0,0xA5C37E91,0x10000,0x7FFFFFFF))})
for index in contract.INDICES:
    for member in range(3):DEFAULTS[f'record_{index:03x}_{member}']=(0x43+index*7+member*29)&255
DEFAULTS.update(prior_508c=0xA5,variant=7)
BYTES=(0,1,15,16,17,31,63,127,128,129,239,240,254,255)


def cases(declared,image):
    values=[]
    def add(kind,**changes):values.append(dict(DEFAULTS,entry=contract.ENTRY,kind=kind,**changes))
    for index in contract.INDICES:
        field=f'record_{index:03x}_2'
        for raw in range(256):add('every-selected-byte-preimage',**{'raw_r4':index,field:raw})
        for sibling in (0,1):
            for raw in BYTES:add('independent-preserved-record-siblings',**{'raw_r4':index,f'record_{index:03x}_{sibling}':raw})
    for register in REGISTERS:
        if register=='raw_r4':continue
        for raw in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
            add('complete-raw-register-width',**{register:raw})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for raw in range(256):add('complete-delay-store-preimage',prior_508c=raw)
    for variant in (0,1,127,128,254,255):add('complete-preserved-register-context',variant=variant)
    # Identical complete RAM and CPU inputs except R4 retain actual differences
    # at common RAM bytes; a changed write-set alone supplies no causal credit.
    for index in contract.INDICES:
        changes={f'record_{other:03x}_2':0 for other in contract.INDICES}
        add('independent-full-R4-record-selection',**changes,raw_r4=index)
    return tuple(dict(case,index=index) for index,case in enumerate(values))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry']!=contract.ENTRY
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1 or case['raw_r4'] not in contract.INDICES):
        raise ValueError('the bit4 input changes its complete typed CPU, explicit full-R4 index or RAM preimage')


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+i*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for i in range(15)]
    registers[:8]=[case[name] for name in REGISTERS]
    return (*registers,(0x456789AB+case['variant'])&0xFFFFFFFF,
        (0x13579BDF+case['variant'])&0xFFFFFFFF,(0x2468ACE0+case['variant'])&0xFFFFFFFF,
        case['initial_sr'],0xB6C70000)


def memory(case):
    require_case(case);result=bytearray([0xA5])*RAM_SIZE
    for name,at,width in RAM_FIELDS:result[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(result)


def calibrations(declared,image,case):
    fixture,_=contract.fixture_for_case(declared,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}


def require_input(declared,image,case,observed):
    expected=calibrations(declared,image,case)
    if (not test_contract.exact(observed['entry'],case['entry'])
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],expected)
            or not test_contract.exact(observed['calibration_after'],expected)):
        raise ValueError('the bit4 writer changes complete actual raw CPU, record preimages, flag preimage or immutable pools')
