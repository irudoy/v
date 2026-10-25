"""Input-only complete natural monitor gates,absolute operands and unordered clamp."""
from kb import test_contract
from kb import clamp_latch_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('word_1026', 4134, 2),
 ('word_1062', 4194, 2),
 ('word_117e', 4478, 2),
 ('byte_11ea', 4586, 1),
 ('word_1ee2', 7906, 2),
 ('word_1fa4', 8100, 2),
 ('byte_22e4', 8932, 1),
 ('byte_2449', 9289, 1),
 ('byte_2451', 9297, 1),
 ('byte_2459', 9305, 1),
 ('byte_25d3', 9683, 1),
 ('byte_4185', 16773, 1),
 ('byte_422f', 16943, 1),
 ('byte_4250', 16976, 1),
 ('byte_55e6', 21990, 1))
WIDTHS={name:width*8 for name,address,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update(word_1026=0xA53C,word_1062=25,word_117e=0,byte_11ea=100,word_1ee2=1,word_1fa4=100,
    byte_22e4=100,byte_2449=0,byte_2451=32,byte_2459=32,byte_25d3=0,byte_4185=128,byte_422f=0xA0,
    byte_4250=0,byte_55e6=100,config_8692=0,config_8693=255,config_8b7e=64,variant=7)
# Complete control and prior-state fields remain in every physical/equation
# observation. Numerical alternatives bind actual separate clamp summand,
# lower/upper configuration and refreshed-word publications explicitly.
ENTRY_FIELDS={0x39316:('word_1ee2','config_8692','config_8693','word_1026')}
BYTE_VALUES=(0,1,2,3,4,7,8,9,10,11,15,16,17,31,32,33,63,64,65,95,100,127,128,129,223,224,254,255)
WORD_VALUES=(0,1,2,3,31,32,100,127,128,129,255,256,16383,16384,32767,32768,65407,65408,65534,65535)


def cases(declared,image):
    inputs=[]
    def add(kind,**changes):inputs.append(dict(DEFAULTS,entry=0x39316,kind=kind,**changes))
    for register in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):add('complete-raw-register-width',**{register:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
    for variant in (0,7,255):add('complete-preserved-register-context',variant=variant)
    for field,address,width in RAM_FIELDS:
        for raw in WORD_VALUES if width==2 else BYTE_VALUES:
            add('complete-raw-control-operand-or-prior-state-width',**{field:raw})
    for raw in range(256):
        add('raw-independent-lower-clamp-byte',config_8692=raw)
        add('raw-independent-upper-clamp-byte',config_8693=raw)
        add('real-ROM-byte-copy-mode',byte_2459=0,config_8b7e=raw)
    for difference in (-255,-128,-11,-10,-9,-1,0,1,9,10,11,127,255):
        first=max(0,difference);second=max(0,-difference)
        add('actual-byte-absolute-difference-and-ten-boundary',byte_11ea=first,byte_22e4=second)
    for source in (0,1,25,16383,16384,32767,32768,65535):
        for difference in (-129,-128,-127,-1,0,1,127,128,129):
            previous=source*4-difference
            if 0<=previous<=65535:
                add('actual-full-word-shift2-absolute-difference-and128-boundary',word_1062=source,word_1fa4=previous)
    for state in (0,1,127,128,254,255):
        for summand in (0,1,32767,32768,65535):
            for lower,upper in ((0,255),(127,128),(128,127),(200,100),(255,0),(0,0),(255,255)):
                add('signed-word-addend-and-unordered-byte-clamp',byte_55e6=state,word_1ee2=summand,config_8692=lower,config_8693=upper)
    for state in (0,1,127,128,254,255):
        for tolerance in (max(0,state-1),state,min(65535,state+1),32767,65535):
            add('alternate-unsigned-word-versus-byte-admission',byte_2459=0,byte_55e6=state,word_117e=tolerance)
    for state in BYTE_VALUES:add('complete-latch-byte-preimage',byte_422f=state)
    for raw in WORD_VALUES:add('complete-signed-load-word-refresh-physical-bits',word_1026=raw)
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a clamp latch input changes a complete raw register,byte,word,configuration or SR width')


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+index*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for index in range(15)]
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
        raise ValueError('the clamp latch caller withdrawal original changes complete raw RAM, CPU or complete raw gate/absolute-difference/unordered-clamp/latch/refresh/pool inputs')
