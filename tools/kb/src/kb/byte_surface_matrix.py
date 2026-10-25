"""Explicit bounded invocation and calibration inputs for byte-surface captures.

This module generates inputs only. Independent numeric/state equations own
expected outputs; original execution and native fact admission remain separate.
"""

from kb import byte_surface_contract as contract, test_contract

MASK = 0xFFFFFFFF
RAM_BASE = 0x01000000
RAM_SIZE = 65536
KINDS = ('caller','wrapper','axis','surface','linear','divider')
COORDINATES = (0,1,16,31,32,63,64,127,128,254,255)
FRACTIONS = (0,1,32768,65535)


def calibration_spans(declared):
    result=[]
    for row in declared['surface']:
        result.append((row['table'],row['rows']*row['cols']))
    for row in declared['surface']:
        result.extend(((row['row_axis'],row['rows']),(row['col_axis'],row['cols'])))
    result.append((declared['selection']['ROM_configuration'],1))
    return tuple(dict.fromkeys(result))


def calibrations(declared,image,case):
    result={start:bytes(image[start:start+size]) for start,size in calibration_spans(declared)}
    pattern=case['pattern']
    if pattern not in range(10):
        raise ValueError('the byte-surface input selects an undeclared calibration pattern')
    for row in declared['surface']:
        address,size=row['table'],row['rows']*row['cols']
        if pattern==0:
            continue
        if pattern in (1,2,3,6,7,8,9):
            if pattern>=8:
                value=(150 if pattern==8 else 151) if address==0xB2FA else (160 if pattern==8 else 180) if address==0xB33A else 128
            elif pattern>=6:
                value=(0 if pattern==6 else 255) if address==0xB33A else 128
            elif pattern==3:value=128
            elif address==0xB2FA:value=128 if pattern==1 else 127
            elif address==0xB33A:value=0 if pattern==1 else 255
            else:value=255 if pattern==1 else 0
            result[address]=bytes([value])*size
        else:
            values=bytes((index*37+19)&255 for index in range(size))
            result[address]=values if pattern==4 else bytes(255-value for value in values)
    if case['configuration'] not in (0,1,2):
        raise ValueError('the byte-surface input has no exact stock or synthetic configuration selector')
    if case['configuration']!=2:
        address=declared['selection']['ROM_configuration']
        result[address]=bytes([(image[address]&~1)|case['configuration']])
    return result


def cases(declared,image):
    """Fixed typed roles; stock knots and full cell locations determine inputs."""
    result=[]
    def add(kind,entry,**values):
        index=len(result)
        case=dict(index=index,kind=kind,entry=entry,table=0xB2FA,row=0,col=0,
            pattern=0,configuration=2,force=0,correction=0,row_index=0,col_index=0,
            row_fraction=0,col_fraction=0,first=0,second=0,divisor=1,dividend=0,
            axis=0x12EC2,axis_max=7,variant=index%6,bridge=0,bridge_selected=0,
            sr=(index&1)|((index&15)<<4)|((index&3)<<8))
        case.update(values)
        if kind not in KINDS:
            raise ValueError('the byte-surface input requires an explicit invocation role')
        result.append(case)
    pairs=tuple(dict.fromkeys((*((value,value) for value in COORDINATES),
        *((value,255-value) for value in COORDINATES),(0,255),(255,0))))
    for pattern in range(8):
        for force,configuration,correction in ((0,2,0),(8,2,0),(0,2,64),(8,2,64),(8,0,64),(0,0,0)):
            for row,col in pairs:
                add('caller',0xBFDC0,row=row,col=col,pattern=pattern,force=force,
                    configuration=configuration,correction=correction)
    for pattern in (8,9):
        for selected in (0,1):
            add('caller',0xBFDC0,row=0,col=0,pattern=pattern,force=0,configuration=2,
                correction=0,bridge=1,bridge_selected=selected)
    for surface in declared['surface']:
        size=surface['rows']
        entry={4:0x26084,8:0x26140,16:0x261B8}[size]
        rows=image[surface['row_axis']:surface['row_axis']+size]
        cols=image[surface['col_axis']:surface['col_axis']+size]
        for row in rows:
            for col in cols:
                add('wrapper',entry,table=surface['table'],row=row,col=col,pattern=4)
        for pattern in (0,5):
            for row,col in pairs:
                add('wrapper',entry,table=surface['table'],row=row,col=col,pattern=pattern)
        for axis in (surface['row_axis'],surface['col_axis']):
            knots=image[axis:axis+size]
            values=tuple(sorted({0,255,*(value+delta for value in knots for delta in (-1,0,1)
                                         if 0<=value+delta<=255)}))
            for value in values:
                add('axis',0x26944,table=surface['table'],row=value,axis=axis,axis_max=size-1)
        for row_index,col_index in ((0,0),(size-2,size-2),(size-1,size-1)):
            for row_fraction in FRACTIONS if row_index<size-1 else (0,):
                for col_fraction in FRACTIONS if col_index<size-1 else (0,):
                    add('surface',0x26770,table=surface['table'],pattern=5,row_index=row_index,
                        col_index=col_index,row_fraction=row_fraction,col_fraction=col_fraction)
    for first,second in ((0,0),(0,255),(255,0),(127,128),(128,127),(255,255)):
        for fraction in FRACTIONS:
            add('linear',0x26740,first=first,second=second,col_fraction=fraction)
    for divisor in (0,1,2,255,65535,0x80000000,0xFFFFFFFF):
        for dividend in (0,1,255,65535,0x80000000,0xFFFFFFFF):
            add('divider',0x26C78,divisor=divisor,dividend=dividend)
    return tuple(result)


def context(declared,case):
    values=[(0x1728394A+register*0x110203+case['variant']*0x1000101)&MASK for register in range(15)]
    table=next(row for row in declared['surface'] if row['table']==case['table'])
    if case['kind']=='wrapper':
        values[4:8]=[table['table'],table['row_axis'],table['col_axis'],0xA1B20000|case['row']]
    elif case['kind']=='axis':
        values[0],values[4],values[5]=case['axis'],case['axis_max'],case['row']
    elif case['kind']=='surface':
        values[0:6]=[case['row_index'],case['row_fraction'],case['col_index'],case['col_fraction'],
                     table['table'],table['cols']]
    elif case['kind']=='linear':
        values[0],values[2],values[3]=case['first'],case['second'],case['col_fraction']
    elif case['kind']=='divider':
        values[0],values[1]=case['divisor'],case['dividend']
    return (*values,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000|case['col'])


def memory(case):
    ram=bytearray(RAM_SIZE) if case['bridge'] else bytearray([(0x5D+case['variant']*37)&255])*RAM_SIZE
    if case['bridge']:
        ram[0x248B]=5
        ram[0x1284]=1
        ram[0x1C90]=255
        ram[0x2327]=91
        ram[0x1071]=0 if case['bridge_selected']==0 else 255
    for offset,value in ((0x11AE,case['row']),(0x102C,case['col']),
                         (0x2468,case['force']),(0x2466,case['correction'])):
        if type(value) is not int or not 0<=value<=255:
            raise ValueError('the byte-surface input changes an explicit source-byte width')
        ram[offset]=value
    return bytes(ram)


def require_input(declared,image,case,observed):
    expected=context(declared,case)
    if (observed['entry']!=case['entry'] or not test_contract.exact(observed['context'],expected)
            or observed['memory_before']!=(memory(case),)
            or observed['calibration_before']!=calibrations(declared,image,case)
            or observed['calibration_after']!=observed['calibration_before']):
        raise ValueError('the byte-surface actual input, const context, calibration or read-only neighbor changes')
