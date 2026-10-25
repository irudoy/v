"""Input-only complete product/truncation/carry/saturation contexts."""

from kb import test_contract
from kb import scalar_ram_product_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
REGISTERS=tuple(f'raw_r{index}' for index in range(8))
RAM_FIELDS=(('previous_long', 5696, 4),
 ('target_word', 5712, 2),
 ('error_gain', 5598, 1),
 ('error_flags', 16772, 1),
 ('additive_gain', 5386, 1),
 ('signed_term', 6758, 2),
 ('bypass_flags', 9309, 1),
 ('product_a', 12224, 1),
 ('product_b', 12225, 1),
 ('pulse_word', 4132, 2),
 ('blend_a', 13194, 1),
 ('blend_b', 12274, 1))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update(product_factor=8,bypass_configuration=8,variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({name:value for name,value in zip(REGISTERS,(
    0x12345678,0x87654321,0x87654321,0x00008000,32768,32768,0x9ABC,0x01000000))})
DEFAULTS.update(previous_long=0,target_word=1000,error_gain=64,error_flags=0,
    additive_gain=128,signed_term=1024,bypass_flags=0,product_a=128,product_b=64,
    pulse_word=32000,blend_a=64,blend_b=128,product_factor=89,bypass_configuration=0,variant=7,initial_sr=0)
ENTRY_FIELDS={0x5279C:('previous_long','target_word','error_gain','error_flags'),
    0x52902:('additive_gain','signed_term','bypass_flags','bypass_configuration'),
    0x5444C:('product_a','product_b','pulse_word','product_factor'),
    0xA5284:('raw_r4','raw_r5','blend_a','blend_b')}
BOUNDARIES={8:(0,1,2,4,31,32,63,64,127,128,254,255),
    16:(0,1,31,32,255,256,32767,32768,65534,65535),
    32:(0,1,255,256,32767,32768,65535,0x7FFFFFFF,0x80000000,0xAAAA0001,0xFFFF0000,0xFFFFFFFF)}


def cases(declared,image):
    inputs=[]
    def add(entry,kind,**changes):inputs.append(dict(DEFAULTS,entry=entry,kind=kind,**changes))
    for entry in contract.ENTRIES:
        for name in ENTRY_FIELDS[entry]:
            for value in BOUNDARIES[WIDTHS[name]]:add(entry,'raw-boundary-'+name,**{name:value})
        for name in REGISTERS:
            for value in (0,0x80000000,0xFFFFFFFF):add(entry,'complete-register-context',**{name:value})
        for variant in (0,7,255):
            for sr in (0,1,0x3F0,0x3F1):add(entry,'complete-SR-context',variant=variant,initial_sr=sr)
    for target in (0,1,255,32768,65535):
        for previous in (0,1,255,256,0x7FFFFFFF,0x80000000,0xFFFF0000,0xFFFFFFFF):
            for gain in (0,1,31,128,255):
                add(0x5279C,'signed-error-truncation-wrap',target_word=target,previous_long=previous,error_gain=gain)
    for gain in (0,1,31,32,127,128,254,255):
        for term in (0,1,31,32,127,128,255,256,32767,32768,65504,65535):
            for flags in (0,32):
                for configuration in (0,4):
                    add(0x52902,'signed-additive-bypass',additive_gain=gain,signed_term=term,
                        bypass_flags=flags,bypass_configuration=configuration)
    for a in (0,1,63,127,128,254,255):
        for b in (0,1,63,127,128,254,255):
            for factor in (0,1,63,89,127,128,255):
                add(0x5444C,'byte-product-cap',product_a=a,product_b=b,product_factor=factor)
    for a in (0,1,128,255):
        for b in (0,1,128,255):
            for word in (0,1,31,32,8191,8192,32767,65535):
                add(0x5444C,'pulse-product-cap',product_a=a,product_b=b,pulse_word=word,product_factor=255)
    for first in (0,1,32767,32768,65535,0xAAAAFFFF,0xFFFF0000):
        for weight in (0,1,32767,32768,65535,0xAAAAFFFF,0xFFFF0000):
            for a in (0,1,64,128,255):
                for b in (0,1,64,128,255):
                    add(0xA5284,'low16-product-highcarry-cap',raw_r4=first,raw_r5=weight,blend_a=a,blend_b=b)
    for name,changes in (('bypass_configuration',dict(bypass_flags=32)),
            ('bypass_flags',dict(bypass_configuration=4))):
        for value in BOUNDARIES[8]:add(0x52902,'fixed-other-positive-'+name,**changes,**{name:value})
    return tuple(dict(row,index=index) for index,row in enumerate(inputs))


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry'] not in contract.ENTRIES
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr'] not in (0,1,0x3F0,0x3F1)):
        raise ValueError('a scalar RAM product input changes an exact natural entry, raw width, context or SR domain')


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
        raise ValueError('the scalar RAM product original changes complete raw RAM, context or configuration/pool inputs')
