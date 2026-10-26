"""Input-only full raw indices, sentinel, byte preimages and complete ordinary context."""
from kb import test_contract
from kb import diagnostic_record_highbit_clear_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RECORDS=contract.INDICES[:7]
RAM_FIELDS=tuple((f'record_{index:03x}_{member}',0x5718+3*index+member,1)
    for index in RECORDS for member in range(3))
WIDTHS={name:32 for name in REGISTERS}
WIDTHS.update({name:8 for name,offset,width in RAM_FIELDS})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,
    (0x12345678,0x87654321,0x80000000,0xFFFFFFFF,0,0xA5C37E91,0x10000,0x7FFFFFFF))})
for index in RECORDS:
    for member in range(3):DEFAULTS[f'record_{index:03x}_{member}']=(0x43+index*7+member*29)&255
DEFAULTS.update(variant=7)
BYTES=(0,1,15,16,17,31,63,127,128,129,239,240,254,255)


def selected_field(index):
    if index==0xFFFFFFFF:return None
    offset=(0x5718+3*index+1)&0xFFFFFFFF
    rows=[name for name,address,width in RAM_FIELDS if address==offset]
    if len(rows)!=1:raise ValueError('the explicit high-bit clear case lacks its exact input byte')
    return rows[0]


def cases(declared,image):
    values=[]
    def add(kind,**changes):values.append(dict(DEFAULTS,entry=contract.ENTRY,kind=kind,**changes))
    for index in contract.INDICES:
        if index==0xFFFFFFFF:
            for raw in range(256):add('inert-sentinel-complete-preimages',raw_r4=index,record_000_1=raw)
            continue
        field=selected_field(index)
        for raw in range(256):add('every-physical-selected-byte-preimage',**{'raw_r4':index,field:raw})
        for raw in (0,1,63,127,128,129,191,255):
            add('fixed-other-actual-byte-and-return-alternative',**{'raw_r4':index,field:raw})
        if index in RECORDS:
            for sibling in (0,2):
                for raw in BYTES:add('preserved-independent-record-sibling',**{'raw_r4':index,f'record_{index:03x}_{sibling}':raw})
    for register in REGISTERS:
        if register=='raw_r4':continue
        for raw in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
            for index in (0,0xFFFFFFFF):add('complete-raw-register-and-sentinel-width',**{register:raw,'raw_r4':index})
    for index in (0,0xAAAAAAAB,0xFFFFFFFF):
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):add('complete-QM-interrupt-T-context',raw_r4=index,initial_sr=qm|interrupt|t)
    for index in contract.INDICES:
        for variant in (0,1,127,128,254,255):add('complete-preserved-register-context',raw_r4=index,variant=variant)
        if index!=0xFFFFFFFF:
            # Every other complete input remains identical; actual common byte
            # values and returned R0 must accompany a changed selected index.
            changes={name:255 for name,offset,width in RAM_FIELDS}
            add('fixed-other-complete-index-selection',**changes,raw_r4=index)
    return tuple(dict(case,index=index) for index,case in enumerate(values))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry']!=contract.ENTRY
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1 or case['raw_r4'] not in contract.INDICES):
        raise ValueError('the high-bit clear input changes complete typed CPU, explicit full-R4 input or byte preimages')


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
        raise ValueError('the high-bit clear original changes complete actual raw CPU, byte preimages or immutable pool')
