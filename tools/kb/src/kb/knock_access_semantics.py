"""Separate integer knock equations over complete explicit observed inputs.

The bounded stock contracts describe software samples, signed order/sum,
gain saturation, unsigned interpolation and comparison. These equations do not
decode instructions or obtain expectations from the raw producer or its rows.
"""

MASK=0xFFFFFFFF
ARITHMETIC_SOURCES=('tools/kb/tests/knock_software_contract.py',
    'tools/kb/tests/test_knock_threshold_chain.py','tools/kb/tests/test_knock_comparison_chain.py')


def data(calibrations,address,width):
    for start,raw in calibrations.items():
        if start<=address and address+width<=start+len(raw):return raw[address-start:address-start+width]
    raise ValueError('a knock scalar lacks its exact observed calibration input')


def unsigned(memory,address,width):return int.from_bytes(memory[address:address+width],'big')


def put(memory,address,width,value):memory[address:address+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')


def signed(value):return value-0x100000000 if value&0x80000000 else value


def selected(before,calibrations):
    selector=data(calibrations,0x8B3D,1)[0]
    channel=before[0x2143] if selector&8 else before[0x11DE]
    if channel not in range(1,7):raise ValueError('a knock scalar leaves its explicit selected channel domain')
    return channel


def normalization(before,calibrations):
    channel=selected(before,calibrations);blocks=before[0x2154]
    multiplier=unsigned(before,0x2152,2);flag=before[0x87E1]
    bins=[unsigned(before,0x2132+2*index,2) for index in range(8)]
    quotients=[value*multiplier//(32*blocks) for value in bins] if blocks else [0]*8
    output=([min(65535,8*value) if flag else value&65535 for value in quotients]
            if blocks else [65535]*8)
    memory=bytearray(before)
    for index,value in enumerate(output):
        put(memory,0x20C2+2*index,2,value);put(memory,0x20D2+16*(channel-1)+2*index,2,value)
    return dict(memory=bytes(memory),channel=channel,blocks=blocks,multiplier=multiplier,flag=flag,
        bins=bins,quotients=quotients,words=output,output=output[0])


def metric(before,calibrations,scope):
    channel=selected(before,calibrations);memory=bytearray(before)
    mask=data(calibrations,0x8618,1)[0];count=data(calibrations,0x8870,1)[0]
    if count not in range(9) or scope not in (0,2):raise ValueError('a knock scalar changes its admitted metric domain')
    differences=[];ranked=[]
    if scope==0:
        differences=[unsigned(before,0x20C2+2*index,2)-unsigned(before,0x2178+16*(channel-1)+2*index,2)
                     for index in range(8)]
        ranked=sorted((value if not mask&(1<<index) else -0x80000000
                       for index,value in enumerate(differences)),reverse=True)
        total=sum(value for value in ranked[:count] if value!=-0x80000000)&MASK
        for index,value in enumerate(differences):put(memory,0x2158+4*index,4,value)
        put(memory,0x2274+4*(channel-1),4,total)
    else:total=unsigned(before,0x2274+4*(channel-1),4)
    factors=[data(calibrations,at,1)[0] for at in (0x86A7,0x8694,0x86AC)]
    gain=min(65535,factors[0]*factors[1]*factors[2]//128)
    value=signed(total);quotient=abs(value)*gain//16384
    scaled=min(quotient,0x7FFFFFFF) if value>=0 else -min(quotient,0x80000000)
    biased=(scaled+0x80000000)&MASK
    put(memory,0x21F8+4*(channel-1),4,scaled);put(memory,0x21D8+4*(channel-1),4,biased)
    return dict(memory=bytes(memory),channel=channel,mask=mask,count=count,differences=differences,
        ranked=ranked,total=total,factors=factors,gain=gain,quotient=quotient,
        scaled=scaled&MASK,biased=biased,output=biased)


def lookup(before,calibrations,comparison=False):
    channel=selected(before,calibrations);coordinate=unsigned(before,0x11F4,2)
    axis=[int.from_bytes(data(calibrations,0x15340+2*index,2),'big') for index in range(16)]
    if any(left>=right for left,right in zip(axis,axis[1:])):
        raise ValueError('a knock lookup leaves its explicit strictly increasing fixture axis')
    lower=max((index for index,value in enumerate(axis) if value<=coordinate),default=0)
    fraction=0 if coordinate<=axis[lower] or lower==15 else ((coordinate-axis[lower])*65536)//(axis[lower+1]-axis[lower])
    row=0x1108E+32*(channel-1)
    left,right=(int.from_bytes(data(calibrations,row+2*lower+offset,2),'big') for offset in (0,2))
    threshold=left+max(0,right-left)*fraction//65536-max(0,left-right)*fraction//65536
    memory=bytearray(before);put(memory,0x2144+2*(channel-1),2,threshold)
    exceeded=False
    if comparison:
        biased=unsigned(before,0x21D8+4*(channel-1),4)
        exceeded=biased>0x80000000+threshold
        memory[0x24C2]=(before[0x24C2]&0xBF)|(0x40 if exceeded else 0)
        memory[0x2150]=(before[0x2150]&(~(1<<(channel-1))&255))|((1<<(channel-1)) if exceeded else 0)
        if exceeded:memory[0x2142]=min(255,before[0x2142]+1)
    return dict(memory=bytes(memory),channel=channel,coordinate=coordinate,axis=axis,index=lower,
        fraction=fraction,row=row,left=left,right=right,threshold=threshold,exceeded=exceeded,output=threshold)


def expected(case,before,calibrations):
    if case['kind']=='normalization':return normalization(before,calibrations)
    if case['kind']=='metric':return metric(before,calibrations,case['scope'])
    if case['kind'] in ('threshold','comparison'):
        return lookup(before,calibrations,case['kind']=='comparison')
    raise ValueError('a knock scalar names another software stage')
