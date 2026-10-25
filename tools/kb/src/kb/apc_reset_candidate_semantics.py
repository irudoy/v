"""Independent bounded APC arithmetic, exact physical operands and published live candidate."""
from kb.division_callees_semantics import quotient
RAM_BASE=0x01000000
MASK=0xFFFFFFFF

def signed(raw,bits=32):return raw-(1<<bits) if raw&(1<<(bits-1)) else raw

def evaluate(memory,calibration):
    if type(memory) is not bytes or len(memory)!=65536:
        raise ValueError('the APC candidate equations need complete exact incoming RAM')
    after=bytearray(memory);operands=[];calls=[];tails=[];curves=[]
    def rom(address,width=1):
        spans=[(at,raw) for at,raw in calibration.items() if at<=address and address+width<=at+len(raw)]
        if len(spans)!=1:raise ValueError('the APC candidate equation loses an authoritative full physical ROM span')
        at,raw=spans[0]
        if type(raw) is not bytes:raise ValueError('the APC candidate equation replaces immutable calibration bytes')
        return raw[address-at:address-at+width]
    def read(site,address,width,register,domain='ram'):
        raw=bytes(after[address:address+width]) if domain=='ram' else rom(address,width)
        operands.append(dict(site=site,mode='read',address=RAM_BASE+address if domain=='ram' else address,
            width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
        return int.from_bytes(raw,'big')
    def write(site,address,width,value,register):
        raw=(value&((1<<(width*8))-1)).to_bytes(width,'big');after[address:address+width]=raw
        operands.append(dict(site=site,mode='write',address=RAM_BASE+address,width_bytes=width,
            register=register,domain='ram',bytes=raw.hex()))
    def call(site,target,arguments,returned):
        row=dict(site=site,target=target,return_address=site+4,arguments=arguments,sp_delta=-32,returned=returned)
        calls.append(row)
    def curve(site,base,coordinate):
        index=min(coordinate//32,7)
        # Append the parent before describing its real tail's physical operands.
        row=dict(site=site,target=0x26370,return_address=site+4,arguments={4:base,5:coordinate},sp_delta=-32)
        calls.append(row)
        if index==7:
            value=read(0x26380,base+7,1,0,'rom');returned=signed(value,8)&MASK;fraction=0
        else:
            fraction=(coordinate%32)*2048
            first=read(0x26AAC,base+index,1,1,'rom');second=read(0x26AAE,base+index+1,1,0,'rom')
            delta=abs(second-first)*fraction//65536
            value=first+delta if second>=first else first-delta;returned=value
            tails.extend(((0x2637A,0x26A80),(0x26AB6,0x26740)))
        row['returned']={0:returned}
        curves.append(dict(base=base,coordinate=coordinate,index=index,fraction=fraction,value=value,
            return_register_value=returned))
        return value
    alternate=bool(read(0x4C1F6,0x4184,1,0)&64)
    if alternate:
        coefficient=read(0x4C204,0x8520,1,0,'rom')*8
        offset=read(0x4C206,0x8291,1,13,'rom')
        coordinate=min(255,read(0x4C20E,0x10CA,2,5)//4)
    else:
        coefficient=read(0x4C240,0x851F,1,5,'rom')*3
        offset=read(0x4C242,0x828A,1,13,'rom')
        coordinate=read(0x4C24E,0x11AE,1,4)
    upper=read(0x4C250,0x8522,1,0,'rom')
    lower=read(0x4C25C,0x8523,1,0,'rom')
    coordinate=max(lower,min(coordinate,upper))
    write(0x4C272,0x144C,1,coordinate,5)
    speed=read(0x4C276,0x1108,1,7)
    minimum_speed=read(0x4C278,0x8525,1,0,'rom')
    if speed<minimum_speed:speed=read(0x4C282,0x8525,1,0,'rom')
    write(0x4C292,0x1450,1,speed,4)
    if speed:
        multiplier=read(0x4C296,0x8524,1,0,'rom')
        reference=read(0x4C2AA,0x959A,2,6,'rom')
        denominator=speed*speed;numerator=6*reference*coordinate
        divided=quotient('unsigned',denominator,numerator)
        call(0x4C2BA,0x21CE0,{0:denominator,1:numerator},{0:divided})
        staged=(divided+6*multiplier*coordinate)&MASK
        if alternate:
            factor=read(0x4C2C8,0x8521,1,0,'rom')
            staged=(((staged*factor)&MASK)*10&MASK)>>8
    else:
        multiplier=read(0x4C2DC,0x8524,1,0,'rom')
        staged=(6*coordinate*(65535+multiplier))&MASK
    staged=(staged+offset)&MASK
    upper=read(0x4C2FA,0x8B87,1,6,'rom')
    lower=read(0x4C304,0x8B88,1,0,'rom')
    staged=max(lower,min(staged,upper))
    write(0x4C314,0x1874,1,staged,6)
    actual_coordinate=read(0x4C31C,0x144C,1,5)
    first=curve(0x4C31E,0x1208E,actual_coordinate);write(0x4C328,0x144D,1,first,2)
    actual_speed=read(0x4C330,0x1450,1,2)
    second=curve(0x4C332,0x12096,actual_speed);write(0x4C33C,0x1451,1,second,2)
    carried_first=read(0x4C340,0x144D,1,6)
    numerator=coefficient*carried_first*second;denominator=0x14000
    if not 0<=numerator<0x80000000:
        raise ValueError('the APC candidate changes its actual nonnegative signed-division premise')
    divided=quotient('signed',denominator,numerator)
    call(0x4C34E,0x21BBC,{0:denominator,1:numerator},{0:divided})
    candidate=min(255,divided)
    write(0x4C36C,0x1875,1,candidate,5)
    staged_again=read(0x4C370,0x1874,1,4)
    selected=min(candidate,staged_again)
    write(0x4C380,0x2406,1,selected,6)
    diagnostic=read(0x4C384,0x4251,1,0)&1
    output=24 if diagnostic else selected
    if diagnostic:write(0x4C38E,0x2406,1,24,2)
    if any(row['mode']=='read' and row['address']==RAM_BASE+0x1875 for row in operands):
        raise ValueError('the APC candidate invents a physical read in place of the actual live R5')
    return dict(memory=bytes(after),operands=operands,calls=calls,tails=tails,curves=curves,alternate=alternate,
        coefficient=coefficient,coordinate=coordinate,speed=speed,staged=staged,candidate=candidate,
        selected=selected,value=output,diagnostic=bool(diagnostic),candidate_dividend=numerator,
        candidate_divisor=denominator,live_candidate_register=5)
