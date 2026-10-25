"""Input-only conversion literals and explicit bounded conditioner alternatives."""

from pathlib import Path
import re

from kb import closed_loop_coordinate_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
INPUT_SOURCE='tools/sh-elf-run/stock-jk08a-closed-loop-conversion-cases.h'
FIELDS=('x1','x2','speed','sample','midpoint','upper','lower','speed_min',
        'coefficient_override','root_override','variant','sr')
DEFAULTS=dict(x1=1000,x2=2000,speed=6000,sample=0,midpoint=880,
    upper=65024,lower=51264,speed_min=5606,coefficient_override=256,
    root_override=256,variant=0,sr=0)
WORD_EDGES=(0,1,127,128,255,256,879,880,881,999,1000,1001,32767,32768,32769,
            51263,51264,51265,65023,65024,65025,65279,65280,65281,65534,65535)


def legacy_inputs(root):
    text=(Path(root)/INPUT_SOURCE).read_text()
    match=re.search(r'\bstatic const struct sample samples\[\]\s*=\s*\{(.*?)\n\};',text,re.S)
    if match is None:raise ValueError('the coordinate input source lacks its complete existing literal array')
    rows=[]
    for line in match[1].splitlines():
        if not line.strip():continue
        prefix=re.match(r'\s*\{((?:\s*(?:0x[0-9a-fA-F]+|[0-9]+)U\s*,){16})',line)
        if prefix is None:raise ValueError('a coordinate literal lacks its sixteen typed input-only columns')
        rows.append(tuple(int(item.strip().rstrip('U'),0) for item in prefix[1].rstrip(',').split(',')))
    if len(rows)!=4338:raise ValueError('the coordinate input source changes its existing literal input catalogue')
    return tuple(rows)


def cases(declared,image,*,root):
    result=[]
    def append(*,legacy_index=-1,**changes):
        row=dict(DEFAULTS);row.update(changes)
        result.append(dict(index=len(result),entry=contract.ENTRY,legacy_index=legacy_index,**row))
    for index,row in enumerate(legacy_inputs(root)):
        # Columns16 onward contain expected results and are never parsed or consumed.
        scale=1 if row[8]&8 else 2
        append(legacy_index=index,x1=(row[0]*scale)&65535,x2=(row[1]*scale)&65535,
            speed=row[2],sample=row[3],midpoint=row[11],coefficient_override=row[12],
            sr=row[15]|((index&3)<<8))
    for field in ('x1','x2','speed','sample','midpoint','upper','lower','speed_min'):
        for value in WORD_EDGES:
            for sr in (0,1):append(**{field:value,'sr':sr})
    for coefficient in (0,1,2,63,64,127,128,129,192,254,255,256):
        for x1,x2 in ((0,65535),(65535,0),(880,880),(1000,2000),(32767,32768)):
            for sr in (0,1,0x301):append(coefficient_override=coefficient,x1=x1,x2=x2,sr=sr)
    for sample in range(256):append(sample=sample<<8)
    for sample in (0,51264):append(sample=sample,coefficient_override=64)
    for root_value in (0,1,63,64,128,192,255):append(root_override=root_value)
    for upper in (999,1000,1001,65535):append(sample=1000,lower=0,upper=upper,coefficient_override=64)
    for lower in (999,1000,1001,65535):append(sample=1000,upper=65535,lower=lower,coefficient_override=64)
    for minimum in (5999,6000,6001):append(speed_min=minimum,coefficient_override=64)
    for midpoint in (0,879,880,881,1000,65535):append(midpoint=midpoint,coefficient_override=64)
    for x2 in (0,880,2000,32768,65535):
        append(x2=0xA5C30000|x2)
        append(x2=x2,variant=1,sr=0x301)
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+index*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for index in range(15)]
    registers[0]=case['x2']
    return (*registers,contract.INCOMING['gbr'],0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000)


def memory(case):
    data=bytearray([0xA5])*RAM_SIZE
    for at,key in ((0x8554,'x1'),(0x110A,'speed'),(0x4524,'sample')):
        data[at:at+2]=case[key].to_bytes(2,'big')
    data[0x9818:0x981C]=bytes.fromhex('a5c3d2e1')
    return bytes(data)


def calibrations(declared,image,case):
    result={row['address']:image[row['address']:row['address']+row['size']] for row in contract.pools()}
    for at,original in contract.ALIASES.items():result[at]=(RAM_BASE+(original&65535)).to_bytes(4,'big')
    result[0x8F98]=case['midpoint'].to_bytes(2,'big')
    result[0x9384]=case['upper'].to_bytes(2,'big')+case['lower'].to_bytes(2,'big')
    result[0x95C6]=case['speed_min'].to_bytes(2,'big')
    table=bytearray(result[0x12292])
    if case['coefficient_override']<256:table[:16]=bytes([case['coefficient_override']])*16
    if case['root_override']<256:table[0]=case['root_override']
    result[0x12292]=bytes(table)
    return result


def logical(observed):
    data=bytearray(observed['memory_after'][0]);start=contract.NATIVE_STORAGE['logical_offset']
    offset=contract.NATIVE_STORAGE['start']-contract.NATIVE_STORAGE['observed_start']
    data[start:start+20]=observed['native_after'][offset:offset+20]
    return bytes(data)


def require_input(declared,image,case,observed):
    from kb import test_contract
    expected=memory(case);native=expected[0x8500:0x8600]
    if (observed['entry']!=contract.ENTRY or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(expected,) or observed['native_before']!=native
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('the coordinate original changes an exact word, register, native workspace, calibration or complete input')
    if (observed['native_after'][:0x60]!=native[:0x60] or observed['native_after'][0x74:]!=native[0x74:]
            or observed['memory_after'][0][0x8560:0x8574]!=expected[0x8560:0x8574]):
        raise ValueError('the coordinate original changes native canaries or aliases native stores into independent raw RAM')
