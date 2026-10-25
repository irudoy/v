"""Separate byte-curve, saturated coordinate and exact transfer equations."""

from kb import closed_loop_coordinate_contract as contract,closed_loop_coordinate_matrix as matrix
from kb import test_contract

MASK=0xFFFFFFFF


def signed16(value):
    value&=65535
    return value-65536 if value&32768 else value


def clamp16(value):
    return max(-32768,min(32767,value))


def trunc0(numerator,denominator):
    if denominator<=0:raise ValueError('the coordinate signed division requires its actual positive byte coefficient')
    magnitude=abs(numerator)//denominator
    return -magnitude if numerator<0 else magnitude


def curve(calibration,sample):
    points=calibration[0x11B47][:16];table=calibration[0x12292];coordinate=sample>>8
    searched=[];index=15
    while True:
        searched.append(index)
        if coordinate>=points[index] or index==0:break
        index-=1
    interior=points[index]<coordinate and index<15
    fraction=65536*(coordinate-points[index])//(points[index+1]-points[index]) if interior else 0
    left,right=table[index],table[index+1]
    change=abs(right-left)*fraction//65536
    return dict(coordinate=coordinate,index=index,searched=searched,interior=interior,
        fraction=fraction,left=left,right=right,coefficient=left+change if right>=left else left-change)


def scalar(case,calibration):
    coefficient=curve(calibration,case['sample'])
    c=coefficient['coefficient'];h=case['midpoint'];x=(case['x1'],case['x2']&65535)
    differences=tuple(value-h for value in x);bounded=tuple(clamp16(value) for value in differences)
    quotients=tuple(trunc0(128*value,c) for value in bounded) if c else ()
    scaled=tuple(clamp16(value) for value in quotients) if c else tuple(
        -32768 if value<0 else 32767 for value in bounded)
    candidates=tuple(h+value for value in scaled)
    admitted=(case['speed']<65280 and case['speed']>case['speed_min']
        and (case['sample']>case['upper'] or case['sample']<case['lower']) and c>0)
    output=tuple(max(0,value)&65535 for value in candidates) if admitted else x
    return dict(curve=coefficient,coefficient=c,differences=differences,bounded=bounded,
        quotients=quotients,scaled=scaled,candidates=candidates,admitted=admitted,output=output,
        register=max(0,candidates[1])&MASK if admitted else signed16(x[1])&MASK,
        native_quotient=quotients[1] if c else differences[1])


def expected_memory(case,before,value):
    memory=bytearray(before)
    def put(at,width,data):memory[at:at+width]=(data&((1<<(8*width))-1)).to_bytes(width,'big')
    put(0x8556,2,case['x2']);put(0x8558,2,value['output'][0]);put(0x855A,2,value['output'][1])
    put(0x855F,1,value['coefficient']);put(0x2F8E,1,value['coefficient'])
    put(0x8560,4,value['candidates'][0]);put(0x8564,4,value['candidates'][1])
    put(0x8568,4,value['native_quotient'])
    for at,data in zip((0x856C,0x856E),value['scaled']):put(at,2,data)
    for at,data in zip((0x8570,0x8572),value['bounded']):put(at,2,data)
    return bytes(memory)


def physical(case,observed,value):
    memory=bytearray(observed['memory_before'][0]);calibration=observed['calibration_before'];rows=[]
    def emit(site,mode,address,width,data=None):
        if 0x01000000<=address<=0x01010000-width:offset=address-0x01000000
        elif 0xFFFF8560<=address<=0xFFFF8574-width:offset=address&65535
        else:offset=None
        if mode=='write':
            if offset is None:raise ValueError('the coordinate transfer writes outside its exact RAM or native workspace')
            raw=(data&((1<<(width*8))-1)).to_bytes(width,'big');memory[offset:offset+width]=raw
        elif offset is not None:raw=bytes(memory[offset:offset+width])
        else:
            matches=[data[address-start:address-start+width] for start,data in calibration.items()
                     if start<=address and address+width<=start+len(data)]
            if len(matches)!=1:raise ValueError('the coordinate transfer reads outside its exact calibration or literal spans')
            raw=matches[0]
        rows.append((site,mode,address,width,raw.hex()))
    def read(site,address,width):emit(site,'read',address,width)
    def write(site,address,width,data):emit(site,'write',address,width,data)
    write(0x3EE60,0x01008556,2,case['x2'])
    read(0x3EE66,0x3F034,4);read(0x3EE68,0x3F038,4)
    read(0x3EE6A,0x0100110A,2);read(0x3EE6C,0x3F03C,4)
    read(0x3EE72,0x01004524,2);read(0x3EE78,0x3F040,4)
    for site,address,width in ((0x3EF86,0x3F002,2),(0x3EF9A,0x3F058,4),
            (0x3EF9E,0x3F05C,4),(0x3EFA0,0x3F060,4),(0x3EFA4,0x3F028,4),
            (0x264A8,0x264C8,4)):read(site,address,width)
    curve_value=value['curve'];index=curve_value['index']
    for offset in curve_value['searched']:read(0x26946,0x11B47+offset,1)
    if curve_value['interior']:
        read(0x2695C,0x11B47+index,1);read(0x2695E,0x11B48+index,1);read(0x26966,0x26980,4)
    read(0x264B2,0x12293+index,1);read(0x264B8,0x12292+index,1);read(0x264BC,0x264C4,4)
    read(0x3EFAC,0x3F004,2);read(0x3EFAE,0x3F006,2)
    write(0x3EFB0,0x01002F8E,1,value['coefficient']);write(0x3EFB4,0x0100855F,1,value['coefficient'])
    read(0x3EFB6,0x3F064,4);read(0x3EFB8,0x01008554,2);read(0x3EFBA,0x8F98,2)
    write(0x3EFDC,0xFFFF8570,2,value['bounded'][0]);read(0x3EFDE,0x01008556,2)
    read(0x3EFE0,0x3F006,2);write(0x3EFEC,0xFFFF8568,4,value['differences'][1])
    write(0x3F070,0xFFFF8572,2,value['bounded'][1]);read(0x3F072,0x3F176,2)
    read(0x3F074,0x01002F8E,1);read(0x3F076,0xFFFF8570,2)
    if value['coefficient']:
        q=value['quotients'][0];read(0x3F088,0x3F17C,4);read(0x3F094,0x3F178,2)
        write(0x3F09C,0xFFFF8568,4,q)
        if q<=32767:
            read(0x3F0A4,0xFFFF8568,4)
            if q>=-32768:read(0x3F0AC,0xFFFF8568,4)
    elif value['bounded'][0]>=0:read(0x3F0C0,0x3F178,2)
    write(0x3F0C4,0xFFFF856C,2,value['scaled'][0])
    if value['coefficient']:
        q=value['quotients'][1];read(0x3F0D0,0x3F17C,4);read(0x3F0DE,0x3F178,2)
        write(0x3F0E6,0xFFFF8568,4,q)
    elif value['bounded'][1]>=0:read(0x3F104,0x3F178,2)
    write(0x3F106,0xFFFF856E,2,value['scaled'][1]);read(0x3F10A,0xFFFF856C,2)
    read(0x3F10C,0x3F180,4);write(0x3F110,0xFFFF8560,4,value['candidates'][0])
    read(0x3F114,0xFFFF856E,2);write(0x3F11E,0xFFFF8564,4,value['candidates'][1])
    if case['speed']<65280:
        read(0x3F120,0x3F184,4);read(0x3F122,0x95C6,2)
        if case['speed']>case['speed_min']:
            read(0x3F12A,0x3F188,4);read(0x3F12C,0x9384,2)
            if case['sample']<=case['upper']:read(0x3F134,0x9386,2)
    if value['admitted']:
        read(0x3F140,0xFFFF8560,4);write(0x3F14E,0x01008558,2,value['output'][0])
    else:
        write(0x3F15A,0x01008558,2,value['output'][0]);read(0x3F15C,0x01008556,2)
    write(0x3F15E,0x0100855A,2,value['output'][1])
    return rows,bytes(memory)


def require_calls(case,observed,result,value):
    sp=observed['sp'];wanted=[(0x3EE7A,0x3EF74,0x3EE7E,sp),
        (0x3EFA6,0x264A0,0x3EFAA,(sp-52)&MASK),(0x264AA,0x26944,0x264AE,(sp-60)&MASK)]
    curve_value=value['curve'];returns=[]
    if curve_value['interior']:
        wanted.append((0x2696A,0x26C78,0x2696E,(sp-64)&MASK));returns.append((0x26D06,0x2696E))
    returns.append((0x26970 if curve_value['interior'] else 0x2697C,0x264AE))
    returns.append((0x2676A if curve_value['right']>=curve_value['left'] else 0x26758,0x3EFAA))
    if value['coefficient']:
        wanted.extend([(0x3F090,0x21BBC,0x3F094,(sp-52)&MASK),(0x3F0DA,0x21BBC,0x3F0DE,(sp-52)&MASK)])
        for index,target in enumerate((0x3F094,0x3F0DE)):
            site=0x21C04 if abs(128*value['bounded'][index])<value['coefficient']*256 else 0x21C6C
            returns.append((site,target))
    returns.extend([(0x3F172,0x3EE7E),(0x3EE82,observed['continuation'])])
    actual=[tuple(row[key] for key in ('site','target','return_address','sp')) for row in result['calls']]
    if not test_contract.exact(actual,wanted):raise ValueError('the coordinate original changes its exact real caller/helper sequence')
    first=result['calls'][0]['entry'];registers=first['registers']
    if ((registers[4],registers[5],registers[6],registers[7])!=(0x01008554,
            signed16(case['speed'])&MASK,signed16(case['sample'])&MASK,0x01008558)
            or (first['sp'],first['pr'],first['gbr'])!=(sp,0x3EE7E,0x01008544)):
        raise ValueError('the coordinate original changes its actual post-delay source arguments or caller frame')
    for row in result['calls'][1:]:
        entry=row['entry'];r=entry['registers']
        if (entry['sp'],entry['pr'],entry['gbr'])!=(row['sp'],row['return_address'],0xFFFF8560):
            raise ValueError('a coordinate helper changes its exact native GBR, PR or call frame')
        if row['site']==0x3EFA6 and (r[4],r[5],r[6],r[7])!=(0x12292,0x11B47,case['sample']>>8,0x01008558):
            raise ValueError('the coefficient lookup changes its exact real table, axis, high-byte coordinate or pointer')
        if row['site']==0x264AA and (r[0],r[4],r[5])!=(0x11B47,15,case['sample']>>8):
            raise ValueError('the byte axis lookup changes its actual post-delay bound or input')
        if row['site']==0x2696A:
            points=observed['calibration_before'][0x11B47];index=curve_value['index']
            if (r[0],r[1])!=(points[index+1]-points[index],65536*((case['sample']>>8)-points[index])):
                raise ValueError('the axis fraction changes its real post-delay unsigned division operands')
        if row['site'] in (0x3F090,0x3F0DA):
            index=int(row['site']==0x3F0DA)
            if (r[0],r[1])!=(value['coefficient'],(128*value['bounded'][index])&MASK):
                raise ValueError('the coordinate scale changes its real post-delay signed division operands')
    actual_returns=[(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']
    if not test_contract.exact(actual_returns,returns):
        raise ValueError('the coordinate original changes a natural helper, conditioner or separate observing return')


def evaluate(case,observed,result):
    value=scalar(case,observed['calibration_before'])
    expected=expected_memory(case,observed['memory_before'][0],value)
    raw=bytearray(expected);raw[0x8560:0x8574]=observed['memory_before'][0][0x8560:0x8574]
    native=bytearray(observed['native_before']);native[0x60:0x74]=expected[0x8560:0x8574]
    if (matrix.logical(observed)!=expected or observed['memory_after']!=(bytes(raw),)
            or observed['native_after']!=bytes(native) or result['registers'][0]!=value['register']
            or (result['gbr'],result['mach'],result['macl'])!=tuple(observed['context'][index] for index in (15,16,17))):
        raise ValueError('the coordinate original differs from separate saturation, division, admission or full native/RAM equations')
    wanted,memory=physical(case,observed,value)
    actual=[tuple(row[key] for key in ('site','mode','address','width_bytes','bytes'))
        for row in result['accesses'] if row['domain']!='frame']
    if not test_contract.exact(actual,wanted) or memory!=expected:
        raise ValueError('the coordinate original changes an exact root/gate/RAM/native transfer, width, value or order')
    require_calls(case,observed,result,value)
    return dict(index=case['index'],output=list(value['output']),coefficient=value['coefficient'],
        admitted=value['admitted'],accesses=actual,exact_coordinate_accesses=True,
        native_geometry_inference=False,natural_caller_reachability=False,
        helper_parameter_reader_admission=False,full_conversion_admission=False,
        scale_admission=False,units_admission=False,hardware_qualification=False)
