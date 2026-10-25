"""Input-only full guarded RAM arithmetic, signed operands, thresholds and CPU preimages."""
from kb import test_contract
from kb import guarded_quotient_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
RAM_FIELDS=(('byte_230e', 8974, 1),
 ('byte_2485', 9349, 1),
 ('byte_161a', 5658, 1),
 ('byte_1601', 5633, 1),
 ('byte_15df', 5599, 1),
 ('byte_1660', 5728, 1),
 ('byte_1680', 5760, 1),
 ('byte_193d', 6461, 1),
 ('byte_1600', 5632, 1),
 ('byte_417e', 16766, 1),
 ('byte_249b', 9371, 1),
 ('byte_245f', 9311, 1),
 ('byte_24d2', 9426, 1),
 ('word_22e8', 8936, 2),
 ('word_1426', 5158, 2),
 ('word_15ce', 5582, 2),
 ('word_15fe', 5630, 2),
 ('word_2ff0', 12272, 2),
 ('word_2422', 9250, 2),
 ('word_17f8', 6136, 2),
 ('word_1210', 4624, 2),
 ('word_19a2', 6562, 2),
 ('word_23fc', 9212, 2),
 ('word_18f2', 6386, 2),
 ('word_19d4', 6612, 2),
 ('previous_fault', 38936, 4))
WIDTHS={n:w*8 for n,at,w in RAM_FIELDS}
WIDTHS.update({n:32 for n in REGISTERS})
WIDTHS.update({row['field']:row['size']*8 for row in contract.CONFIGURATION})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={n:0 for n in WIDTHS}
DEFAULTS.update({n:v for n,v in zip(REGISTERS,(0x12345678,0x87654321,0x87654321,0x8000,1000,1,100000000,8))})
DEFAULTS.update(byte_161a=3,word_22e8=1,word_1426=1000,word_15ce=100,word_15fe=10,
    byte_1601=64,byte_15df=8,byte_1660=1,byte_1680=32,byte_193d=4,word_2ff0=1000,
    byte_24d2=64,word_2422=100,word_17f8=25,word_1210=200,word_19a2=1000,
    word_23fc=1000,word_18f2=1000,word_9092=100,word_914e=100,word_9150=300,
    word_944e=1000,word_19d4=0xABCD,byte_1600=0xA5,previous_fault=0x13579BDF,variant=7)
ENTRY_FIELDS={0x532AE:('byte_230e','byte_2485','byte_161a','word_22e8','word_1426','word_15ce','word_15fe',
    'byte_1601','byte_15df','byte_1660','byte_1680','byte_193d','word_2ff0','word_9092'),
    0x74B68:('byte_417e','byte_249b','byte_245f','byte_24d2','word_2422','word_17f8','word_1210','word_914e','word_9150'),
    0x75306:('word_19a2','word_23fc','word_18f2','word_944e')}
WORDS=(0,1,2,127,128,254,255,256,16383,16384,16385,32767,32768,65534,65535)
BYTES=(0,1,2,3,4,8,15,16,31,32,64,127,128,254,255)


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for entry in contract.ENTRIES:
        for register in REGISTERS:
            for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
                add(entry,'complete-raw-register-width',**{register:value})
        for qm in (0,0x100,0x200,0x300):
            for interrupt in range(0,256,16):
                for t in (0,1):add(entry,'complete-QM-interrupt-T-context',initial_sr=qm|interrupt|t)
        for variant in (0,7,255):add(entry,'complete-preserved-register-context',variant=variant)
        for field in ENTRY_FIELDS[entry]:
            for value in WORDS if WIDTHS[field]==16 else BYTES:
                add(entry,'independent-complete-RAM-or-calibration-input',**{field:value})
        for name,at,width in RAM_FIELDS:
            for value in (0,(1<<(8*width))-1):add(entry,'complete-prior-RAM-preimage',**{name:value})
    for first in (0,1,2,3,255):
        for second in (0,16,255):
            for flags in (0,1,2,3,255):
                for word in (0,16383,16384,16385,65535):
                    add(0x532AE,'every-admission-flag-and-ordered-word-boundary',
                        byte_230e=first,byte_2485=second,byte_161a=flags,word_22e8=word)
    for divisor in WORDS:
        for first in WORDS:
            for second in (0,1,32767,32768,65535):
                add(0x532AE,'raw-word-divisor-signed-word-sum-and-saved-carrier',
                    word_1426=divisor,word_15ce=first,word_15fe=second)
    for field in ENTRY_FIELDS[0x532AE]:
        for value in WORDS if WIDTHS[field]==16 else BYTES:
            add(0x532AE,'independent-full-fallback-source-alternative',byte_230e=1,
                **({field:value} if field!='byte_230e' else dict(byte_2485=value)))
    for signed_byte in BYTES:
        for first in (0,1,127,128,255):
            for second in (0,1,127,128,255):
                add(0x532AE,'signed-byte-product-full-borrow-and-extract-preimage',byte_230e=1,
                    byte_1660=signed_byte,byte_1601=first,byte_15df=second)
    for weight in WORDS:
        for delta in WORDS:
            for flag in (0,64):
                add(0x74B68,'word-increment-decrement-floor-and-cap',word_2422=weight,word_17f8=delta,byte_24d2=flag)
    for low,high in ((0,0),(0,1),(0,65535),(1,65535),(32767,32768),(32768,65535),(65535,0),(65535,65535),(100,300)):
        for raw in WORDS:
            for delta in (-1,0,1):
                add(0x74B68,'ordered-threshold-window-and-signed-fraction-wrap',word_914e=low,word_9150=high,
                    word_1210=max(0,min(65535,raw+delta)))
        for point in (low,high):
            for delta in (-1,0,1):add(0x74B68,'each-actual-window-edge-neighbor',word_914e=low,word_9150=high,
                word_1210=max(0,min(65535,point+delta)))
    for divisor in WORDS:
        for signed_word in WORDS:
            for gain in (0,1,32767,32768,65535):
                add(0x75306,'first-signed-divisor-signed-product-and-wide-cap',word_19a2=divisor,
                    word_18f2=signed_word,word_944e=gain)
    for divisor in WORDS:
        for signed_word in WORDS:
            for first in (1,255,32768,65535):
                add(0x75306,'second-nonzero-divisor-and-signed16-publication-cap',word_23fc=divisor,
                    word_18f2=signed_word,word_19a2=first)
    return tuple(dict(row,index=i) for i,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[n]) is not int or not 0<=case[n]<(1<<bits) for n,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('a guarded quotient input changes a complete raw RAM,scalar calibration,register or SR width')


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
        raise ValueError('the guarded quotient caller withdrawal original changes complete raw RAM, CPU or complete scalar configuration/pool inputs')
