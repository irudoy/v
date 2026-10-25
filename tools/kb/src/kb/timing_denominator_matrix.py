"""Typed natural-entry inputs for both denominator parents."""

RAM_BASE=0x01000000
RAM_SIZE=65536
KINDS=('parent-a','parent-b')
ENTRIES={'parent-a':0x7B2C8,'parent-b':0x7B3F4}
PATTERNS=('stock','zero','one','255','maximum','rising','falling','checker','curve-zero','curve-one')
PARENTS=(
    dict(kind='parent-a',surface=0xC98E,row_axis=0x13478,column_axis=0x13498,curve=0x14AFA,curve_axis=0x134B8),
    dict(kind='parent-b',surface=0x16948,row_axis=0x18846,column_axis=0x18866,curve=0x18DD6,curve_axis=0x18886),
)


def knots(image,address,count):
    return tuple(int.from_bytes(image[address+index*2:address+index*2+2],'big') for index in range(count))


def samples(values,maximum):
    points=[0,maximum,values[0],values[1],values[len(values)//2],values[-2],values[-1]]
    points.append(values[0]+1 if values[1]>values[0]+1 else (values[0]+values[1])//2)
    points.append(values[-2]+1 if values[-1]>values[-2]+1 else (values[-2]+values[-1])//2)
    return tuple(sorted({value for value in points if 0<=value<=maximum}))


def tables(pattern):
    if pattern=='stock':return None
    if pattern in ('zero','one','255','maximum'):
        value={'zero':0,'one':1,'255':255,'maximum':65535}[pattern]
        return (value,)*256,(value,)*8
    if pattern=='rising':
        return tuple(index*200 for index in range(256)),tuple(20+index*30 for index in range(8))
    if pattern=='falling':
        return tuple(65535-index*200 for index in range(256)),tuple(235-index*30 for index in range(8))
    if pattern=='checker':
        return (tuple(65535 if (index//16+index%16)&1 else 0 for index in range(256)),
            tuple(65535 if index&1 else 1 for index in range(8)))
    if pattern=='curve-zero':return (255,)*256,(0,)*8
    if pattern=='curve-one':return (255,)*256,(1,)*8
    raise ValueError('the denominator calibration input changes its declared pattern')


def cases(declared,image):
    result=[]
    def add(kind,pattern,row,column,curve,gate=1,override=0,high=0x7FFF,low=0x8000):
        index=len(result)
        result.append(dict(index=index,kind=kind,entry=ENTRIES[kind],pattern=pattern,row=row,column=column,
            curve=curve,gate=gate,override=override,high=high,low=low,variant=index%4,
            sr=(index&1)|((index&15)<<4)|((index&3)<<8)))
    for parent in PARENTS:
        row=knots(image,parent['row_axis'],16)
        column=knots(image,parent['column_axis'],16)
        curve=knots(image,parent['curve_axis'],8)
        row_samples,column_samples,curve_samples=samples(row,65535),samples(column,65535),samples(curve,65535)
        fixed_row,fixed_column,fixed_curve=row[len(row)//2],column[len(column)//2],curve[len(curve)//2]
        interior=((row[0],column[0]),(row[0]+1,column[0]),(row[0],column[0]+1),(row[0]+1,column[0]+1))
        for pattern in ('rising','falling','255'):
            for value in row_samples:add(parent['kind'],pattern,value,fixed_column,fixed_curve)
            for value in column_samples:add(parent['kind'],pattern,fixed_row,value,fixed_curve)
            for value in curve_samples:add(parent['kind'],pattern,fixed_row,fixed_column,value)
            for row_value,column_value in interior:
                add(parent['kind'],pattern,row_value,column_value,fixed_curve)
        for pattern in PATTERNS:
            add(parent['kind'],pattern,fixed_row,fixed_column,fixed_curve)
        for pattern in ('curve-zero','curve-one','255'):
            add(parent['kind'],pattern,100,100,100)
        for high,low in ((0x7FFF,0x8000),(0x8000,0x8000),(0x7FFF,0x7FFF)):
            add(parent['kind'],'curve-zero',100,100,100,high=high,low=low)
        for override in (0,0x10,0x20,0x30):
            add(parent['kind'],'curve-zero',100,100,100,override=override)
        add(parent['kind'],'255',fixed_row,fixed_column,fixed_curve,gate=0)
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+reg*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for reg in range(15)]
    return (*registers,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000|case['row'])


def calibration_spans(declared):
    return ((0xC98E,512),(0x13478,32),(0x13498,32),(0x14AFA,18),(0x134B8,16),
        (0x16948,512),(0x18846,32),(0x18866,32),(0x18DD6,18),(0x18886,16),(0x83C1,1))


def calibrations(declared,image,case):
    result={start:image[start:start+size] for start,size in calibration_spans(declared)}
    rendered=tables(case['pattern'])
    if rendered is not None:
        surface,curve=rendered
        for address in (0xC98E,0x16948):
            result[address]=b''.join(value.to_bytes(2,'big') for value in surface)
        for address in (0x14AFA,0x18DD6):
            result[address]=b''.join(value.to_bytes(2,'big') for value in curve)+image[address+16:address+18]
    result[0x83C1]=bytes([(image[0x83C1]&~2)|(2 if case['gate'] else 0)])
    return result


def memory(case):
    result=bytearray(RAM_SIZE)
    for address,value in ((0x412A,case['row']),(0x35CE,case['row']),(0x11B6,case['column']),(0x10BC,case['curve']),
            (0x4138,case['high']),(0x413A,case['low']),(0x35F0,case['low']),(0x243C,0x1357),(0x1D26,0x2468),
            (0x2C6C,0xA1B2),(0x2C6E,0xA3B4),(0x2CFE,0xA5B6),(0x35D2,0xB1B2),(0x35D0,0xB3B4),(0x35D8,0xB5B6)):
        result[address:address+2]=value.to_bytes(2,'big')
    result[0x41FB]=case['override'];result[0x4214]=case['override']
    result[0x2CFD]=0xA7;result[0x35D6]=0xB7
    result[0x9818:0x981C]=bytes.fromhex('a5c3d2e1')
    return bytes(result)


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=case['entry'] or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('the denominator original changes an explicit coordinate, gate, calibration or physical neighbor')
