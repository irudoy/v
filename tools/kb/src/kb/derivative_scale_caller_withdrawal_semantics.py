"""Separate paired8/16-knot curves, signed scaling, explicit zero bypass and chained unsigned quotients."""

from kb import division_callees_semantics as division

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def words(raw,count):
    if type(raw) is not bytes or len(raw)!=2*count:
        raise ValueError('the word interpolation equation changes an exact physical calibration extent')
    return tuple(int.from_bytes(raw[i:i+2],'big') for i in range(0,len(raw),2))


def position(knots,coordinate):
    """Select the rightmost qualifying knot without a monotonicity premise."""
    if (type(coordinate) is not int or not 0<=coordinate<=65535 or len(knots) not in (8,16)
            or any(type(knot) is not int or not 0<=knot<=65535 for knot in knots)):
        raise ValueError('the backward word-axis equation changes an unsigned coordinate or physical word')
    scanned=[]
    for index in range(len(knots)-1,-1,-1):
        scanned.append(index)
        if coordinate==knots[index] or coordinate>knots[index] and index==len(knots)-1:
            return dict(index=index,fraction=0,scanned=tuple(scanned),bracket=False)
        if coordinate>knots[index]:
            denominator=knots[index+1]-knots[index]
            if denominator<=0 or not knots[index]<coordinate<knots[index+1]:
                raise ValueError('the rightmost word-axis bracket loses its positive actual divisor')
            numerator=(coordinate-knots[index])*65536
            return dict(index=index,fraction=numerator//denominator,scanned=tuple(scanned),
                bracket=True,denominator=denominator,numerator=numerator)
    return dict(index=0,fraction=0,scanned=tuple(scanned),bracket=False)


def linear(first,second,fraction):
    if any(type(v) is not int or not 0<=v<=65535 for v in (first,second,fraction)):
        raise ValueError('the word interpolation equation changes an unsigned operand width')
    magnitude=abs(second-first)*fraction//65536
    ascending=second>=first
    return dict(value=first+magnitude if ascending else first-magnitude,magnitude=magnitude,
        first=first,second=second,fraction=fraction,ascending=ascending)


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry not in (0xB78DA,0xB7A3C)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the derivative-scale caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the word caller equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the word caller equation loses one authoritative physical preimage')
        at,data=spans[0];raw=data[address-at:address-at+width]
        event(site,'read',address,width,register,'rom',raw)
        return int.from_bytes(raw,'big')

    def frame_access(site,mode,address,width,register,value=None):
        at=160+address-sp
        if mode=='write':frame[at:at+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big')
        raw=bytes(frame[at:at+width]);event(site,mode,address,width,register,'frame',raw)
        return int.from_bytes(raw,'big')

    def push(site,value,register=None):
        nonlocal stack
        stack-=4;frame_access(site,'write',stack,4,register,value)

    def pop(site,register=None):
        nonlocal stack
        value=frame_access(site,'read',stack,4,register);stack+=4;return value

    def t(value):
        nonlocal sr,sr_mask
        sr=(sr&~1)|int(bool(value));sr_mask|=1

    def control(site,kind,target,delay=False):controls.append(dict(site=site,kind=kind,target=target,delay=delay))

    def branch(site,taken,target,delay=False):
        control(site,'taken' if taken else 'fallthrough',target if taken else site+(4 if delay else 2),delay)

    def call(site,target):
        nonlocal pr
        row=dict(site=site,target=target,return_address=site+4,sp=stack,registers=tuple(r),
            gbr=gbr,mach=context[16],macl=macl,sr=sr,sr_mask=sr_mask)
        calls.append(row);pr=site+4;control(site,'call',target,True);return row

    def returned(row,site):
        row.update(return_site=site,return_registers=tuple(r),return_sr=sr,return_sr_mask=sr_mask,
            return_gbr=gbr,return_mach=context[16],return_macl=macl)

    def fraction(target,row):
        nonlocal sr,sr_mask
        divisor,numerator=r[0],r[1]
        if not 0<divisor<=65535 or not 0<=numerator<divisor*65536:
            raise ValueError('the natural word-axis caller loses its positive bounded division premise')
        emit(target,target+6);t(False);branch(target+2,False,target+0x92)
        push(target+4,r[2],2)
        emit(target+6,target+0x92)
        r[0]=r[1]=numerator//divisor
        r[2]=pop(target+0x8C,2)
        sr&=~0x301;sr_mask&=~0x101
        control(target+0x8E,'return',pr,True);returned(row,target+0x8E)

    def axis(target,count,row):
        nonlocal pr
        base,coordinate=r[0],r[5];maximum=2*(count-1);r[3]=r[4]
        if r[4]!=maximum:raise ValueError('the word-axis wrapper changes its actual complete axis extent')
        source=next(data for at,data in calibration.items() if at==base)
        pos=position(words(source,count),coordinate);lookups.append(dict(kind='axis',target=target,base=base,**pos))
        emit(target)
        for index in pos['scanned']:
            emit(target+2,target+10);r[1]=read(target+2,base+2*index,1)
            equal=coordinate==r[1];t(equal);branch(target+8,equal,target+0x38)
            r[4]=2*index
            if equal:break
            emit(target+10,target+14);higher=coordinate>r[1];t(higher);branch(target+12,not higher,target+0x30)
            if higher:
                emit(target+14,target+18);last=index==count-1;t(last);branch(target+16,last,target+0x38)
                if last:break
                emit(target+18,target+42)
                r[5]=pos['numerator'];r[1]=read(target+24,base+2*index,1)
                next_word=read(target+26,base+2*index+2,0)
                r[0]=next_word-r[1];r[2]=0x26C78
                push(target+32,pr);r[1]=r[5]
                nested=call(target+38,r[2]);fraction(r[2],nested)
                emit(target+42,target+48);pr=pop(target+42)
                r[5]=r[0];control(target+44,'return',pr,True);returned(row,target+44)
                return pos
            emit(target+48,target+54);r[4]-=2;t(r[4]>=0);branch(target+52,r[4]>=0,target+2)
            if r[4]<0:emit(target+54);r[4]=0
        emit(target+56,target+60);r[5]=0;control(target+56,'return',pr,True);returned(row,target+56)
        return pos

    def interpolation(target,row=None):
        nonlocal macl
        value=linear(r[0],r[2],r[3]);t(value['ascending'])
        emit(target,target+4);branch(target+2,value['ascending'],target+28)
        if value['ascending']:
            emit(target+28,target+46);r[1]=macl;r[2]=value['magnitude'];r[0]=value['value']
            terminal=target+42
        else:
            emit(target+4,target+28);push(target+4,r[0],0)
            r[1]=macl;pop(target+18,2);r[2]=r[0]=value['value'];terminal=target+24
        control(terminal,'return',pr,True)
        if row is not None:returned(row,terminal)
        return value

    def curve(target,count,row):
        nonlocal pr
        base,axis_base,coordinate=r[4:7]
        emit(target,target+14);push(target,pr);push(target+2,r[4],4)
        r[0]=r[5];r[5]=coordinate&65535;r[7]=0x26984;r[4]=2*(count-1)
        nested=call(target+10,0x26984);pos=axis(0x26984,count,nested)
        emit(target+14,target+34);r[6]=pop(target+14,6)+r[4]
        r[0]=signed(read(target+18,r[6]+2,0),16)&MASK;r[2]=r[0]&65535;r[3]=r[5]
        r[1]=signed(read(target+24,r[6],1),16)&MASK;pr=pop(target+26)
        r[6]=0x26740;r[0]=r[1]&65535;control(target+30,'jump',0x26740,True)
        value=interpolation(0x26740,row)
        lookups.append(dict(pos,kind='curve',base=base,axis=axis_base,coordinate=coordinate,**value))
        return value

    def signed_divider(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2];negative=bool(numerator&0x80000000)
        if not 0<divisor<=65535:raise ValueError('the derivative-scale signed helper loses its actual positive word divisor')
        long_path=abs(signed(numerator))>=divisor*256
        saved_r2,saved_r3,saved_r4=r[2],r[3],r[4]
        emit(0x21BBC,0x21BC2);push(0x21BBC,saved_r2,2);t(False);branch(0x21BC0,False,0x21C70)
        emit(0x21BC2,0x21BCC);push(0x21BC2,saved_r3,3);t(True);branch(0x21BCA,True,0x21BD0)
        emit(0x21BD0,0x21BD4);positive=signed(numerator)>0;t(positive);branch(0x21BD2,positive,0x21BD8)
        if not positive:emit(0x21BD4,0x21BD8)
        emit(0x21BD8,0x21BE6);branch(0x21BDC,False,0x21C7C);branch(0x21BE4,long_path,0x21C08)
        if long_path:
            emit(0x21C08,0x21C64);push(0x21C08,saved_r4,4);branch(0x21C62,not negative,0x21C68)
            if negative:emit(0x21C64,0x21C68)
            emit(0x21C68,0x21C70);pop(0x21C68,4);pop(0x21C6A,3);pop(0x21C6E,2);terminal=0x21C6C
        else:
            emit(0x21BE6,0x21BFE);branch(0x21BFC,not negative,0x21C02)
            if negative:emit(0x21BFE,0x21C02)
            emit(0x21C02,0x21C08);pop(0x21C02,3);pop(0x21C06,2);terminal=0x21C04
        r[0]=division.quotient('signed',divisor,numerator);r[1]=None
        r[2],r[3],r[4]=saved_r2,saved_r3,saved_r4
        sr&=~0x301;sr_mask&=~0x100;t(negative)
        row.update(divisor=divisor,dividend=numerator,long_path=long_path)
        control(terminal,'return',pr,True);returned(row,terminal)

    def unsigned_divider(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2]
        if divisor not in (255,250,2500):raise ValueError('the derivative-scale unsigned helper changes an actual fixed divisor')
        long_path=numerator>=divisor*256;saved_r2,saved_r3=r[2],r[3]
        emit(0x21CE0,0x21CF4);push(0x21CE0,saved_r2,2)
        branch(0x21CE4,False,0x21D6A);branch(0x21CEA,False,0x21D76);branch(0x21CF2,long_path,0x21D0C)
        if long_path:
            emit(0x21D0C,0x21D6A);push(0x21D0C,saved_r3,3)
            pop(0x21D64,3);pop(0x21D68,2);terminal=0x21D66
        else:
            emit(0x21CF4,0x21D0C);pop(0x21D06,2);terminal=0x21D08
        r[0]=numerator//divisor;r[1]=None;r[2],r[3]=saved_r2,saved_r3
        sr&=~0x301;sr_mask&=~0x101
        row.update(divisor=divisor,dividend=numerator,long_path=long_path)
        control(terminal,'return',pr,True);returned(row,terminal)

    if entry==0xB78DA:
        emit(0xB78DA,0xB78F4)
        push(0xB78DA,r[13],13);push(0xB78DC,r[14],14);push(0xB78DE,pr);push(0xB78E0,macl);stack-=4
        r[14]=r[4];r[0]=r[5];frame_access(0xB78E8,'write',stack+3,1,0,r[0]);r[13]=r[7]
        r[4]=0x21BBC;r[0]=20000;r[1]=r[6];row=call(0xB78F0,0x21BBC);signed_divider(row)
        emit(0xB78F4,0xB7908);r[6]=r[0]
        bias=frame_access(0xB78F6,'read',stack+3,1,0);r[0]=signed(bias,8)&MASK;r[5]=50;r[2]=bias
        macl=bias*50;r[2]=macl;r[6]=(r[6]-r[2])&MASK;candidate=signed(r[6]);r[2]=30267
        above=candidate>30267;t(above);branch(0xB7906,not above,0xB790E)
        if above:
            emit(0xB7908,0xB790E);r[6]=32767;control(0xB790A,'jump',0xB791E,True)
        else:
            emit(0xB790E,0xB7914);r[2]=0xFFFF763C;within=candidate>=-35268;t(within);branch(0xB7912,within,0xB791A)
            if within:emit(0xB791A,0xB791E);r[5]=2500;r[6]=(r[6]+2500)&MASK
            else:emit(0xB7914,0xB791A);r[6]=0xFFFF8000;control(0xB7916,'jump',0xB791E,True)
        emit(0xB791E,0xB7924);r[2]=signed(r[6]&65535,16)&MASK;nonnegative=signed(r[2])>=0;t(nonnegative)
        branch(0xB7922,nonnegative,0xB7926)
        if not nonnegative:emit(0xB7924);r[2]=0
        emit(0xB7926,0xB7932);r[6]=r[2];r[14]&=255;r[2]=2;r[4]=0x86D2
        high_selector=r[14]>2;t(high_selector);branch(0xB7930,high_selector,0xB7936)
        if high_selector:
            emit(0xB7936,0xB793A);r[0]=signed(read(0xB7936,0x86D3,0,1),8)&MASK;r[2]=r[0]
        else:
            emit(0xB7932,0xB7936);r[2]=signed(read(0xB7934,0x86D2,2,1),8)&MASK;control(0xB7932,'jump',0xB793A,True)
        emit(0xB793A,0xB7948);r[6]&=65535;r[2]&=255;macl=r[6]*r[2];r[6]=131070;r[2]=macl
        above=r[2]>131070;t(above);branch(0xB7946,not above,0xB79AC)
        if above:emit(0xB7948,0xB794C);r[2]=MASK;control(0xB7948,'jump',0xB79AE,True)
        else:emit(0xB79AC);t(r[2]&1);r[2]>>=1
        emit(0xB79AE,0xB79C8);r[14]=r[2];r[2]=0x9292;r[13]&=65535
        r[6]=signed(read(0xB79B4,0x9292,6),16)&MASK;t(r[13]==0);r[2]=0x8819;r[6]&=65535
        r[5]=signed(read(0xB79BC,0x8819,5,1),8)&MASK;r[2]=(-r[6])&MASK;r[5]&=255
        macl=(r[2]*r[5])&MASK;r[6]=macl;zero=r[13]==0;branch(0xB79C4,zero,0xB79E4,True)
        if not zero:
            emit(0xB79C8,0xB79D6);r[1]=(r[6]*20)&MASK;r[4]=0x21BBC;r[0]=r[13]
            row=call(0xB79D2,0x21BBC);signed_divider(row)
            emit(0xB79D6,0xB79DE);r[2]=0xFFFF0001;within=signed(r[0])>=-65535;t(within);r[6]=r[0]
            branch(0xB79DA,not within,0xB79EA,True)
            if within:emit(0xB79DE,0xB79E4);r[2]=MASK;r[6]=(r[6]-1)&MASK;control(0xB79E0,'jump',0xB79EC,True)
            else:emit(0xB79EA);r[6]=0
        else:
            emit(0xB79E4,0xB79EA);positive=signed(r[6])>=0;t(positive);r[6]=MASK;branch(0xB79E6,positive,0xB79EC,True)
            if not positive:emit(0xB79EA);r[6]=0
        emit(0xB79EC,0xB79F6);r[4]=0x14CCA;r[5]=0x13B38;r[2]=0x264F8;r[6]&=65535
        row=call(0xB79F2,0x264F8);lookup=curve(0x264F8,16,row)
        emit(0xB79F6,0xB7A00);r[2]=r[0]&65535;r[6]=(-r[2])&MASK;r[2]=0xFFFFFF01
        within=signed(r[6])>=-255;t(within);branch(0xB79FE,within,0xB7A04)
        if within:emit(0xB7A04,0xB7A08);r[2]=MASK;r[6]=(r[6]-1)&MASK
        else:emit(0xB7A00,0xB7A04);r[6]=0;control(0xB7A00,'jump',0xB7A08,True)
        emit(0xB7A08,0xB7A1C);r[14]&=65535;r[5]=0x21CE0;r[6]&=255;macl=r[6]*r[14]
        r[14]=250;r[1]=macl;r[0]=255;row=call(0xB7A18,0x21CE0);unsigned_divider(row)
        emit(0xB7A1C,0xB7A28);r[2]=r[0]&65535;r[5]=0x21CE0;macl=r[13]*r[2];r[0]=r[14];r[1]=macl
        row=call(0xB7A24,0x21CE0);unsigned_divider(row)
        emit(0xB7A28,0xB7A30);r[2]=r[0];r[6]=RAM_BASE+0x28F8;r[0]=0x6A0;output=r[2]
        ram[0x2F98:0x2F9C]=output.to_bytes(4,'big');event(0xB7A2E,'write',RAM_BASE+0x2F98,4,2,'ram',bytes(ram[0x2F98:0x2F9C]))
        emit(0xB7A30,0xB7A3C);stack+=4;macl=pop(0xB7A32);pr=pop(0xB7A34);r[14]=pop(0xB7A36,14);r[13]=pop(0xB7A3A,13)
        control(0xB7A38,'return',pr,True)
    else:
        emit(0xB7A3C,0xB7A66)
        for at,index in ((0xB7A3C,11),(0xB7A3E,12),(0xB7A40,13),(0xB7A42,14)):push(at,r[index],index)
        push(0xB7A44,pr);push(0xB7A46,macl);push(0xB7A48,gbr);r[0]=gbr=0x8A30;stack-=4
        r[1]=r[6];r[0]=r[7];frame_access(0xB7A54,'write',stack+3,1,0,r[0]);r[13]=r[4]
        r[6]=frame_access(0xB7A58,'read',stack+32,4,6);r[7]=0x21BBC;r[0]=35
        frame_access(0xB7A5E,'write',stack+35,1,6,r[6]);r[0]=20000;r[11]=r[5]
        row=call(0xB7A62,0x21BBC);signed_divider(row)
        emit(0xB7A66,0xB7A7C);r[5]=r[0];bias=frame_access(0xB7A68,'read',stack+3,1,0)
        r[0]=signed(bias,8)&MASK;r[6]=50;r[2]=bias;macl=bias*50;r[2]=macl;r[5]=(r[5]-r[2])&MASK
        candidate=signed(r[5]);r[2]=30267;above=candidate>30267;t(above);branch(0xB7A7A,not above,0xB7A82)
        if above:emit(0xB7A7C,0xB7A82);r[2]=32767;control(0xB7A7E,'jump',0xB7A94,True)
        else:
            emit(0xB7A82,0xB7A88);r[2]=0xFFFF763C;within=candidate>=-35268;t(within);branch(0xB7A86,within,0xB7A8E)
            if within:emit(0xB7A8E,0xB7A94);r[6]=2500;r[5]=(r[5]+2500)&MASK;r[2]=r[5]
            else:emit(0xB7A88,0xB7A8E);r[2]=0xFFFF8000;control(0xB7A8A,'jump',0xB7A94,True)
        emit(0xB7A94,0xB7A9A);r[5]=signed(r[2]&65535,16)&MASK;nonnegative=signed(r[5])>=0;t(nonnegative)
        branch(0xB7A98,nonnegative,0xB7A9C)
        if not nonnegative:emit(0xB7A9A);r[5]=0
        emit(0xB7A9C,0xB7AB0);r[0]=35;r[6]=signed(frame_access(0xB7A9E,'read',stack+35,1,6),8)&MASK
        r[4]=0x14E42;r[14]=r[5]&65535;r[6]=(r[6]&255)<<8;r[5]=0x13BB8;r[2]=0x264CC
        row=call(0xB7AAC,0x264CC);lookup=curve(0x264CC,8,row)
        emit(0xB7AB0,0xB7AC2);r[2]=r[0];r[0]=signed(read(0xB7AB2,0x8A30,0,1),8)&MASK;r[5]=131070
        r[12]=r[0];r[6]=r[12]&255;macl=r[14]*r[6];r[6]=macl;above=r[6]>131070;t(above);branch(0xB7AC0,not above,0xB7AC6)
        if above:emit(0xB7AC2,0xB7AC6);r[6]=MASK;control(0xB7AC2,'jump',0xB7AC8,True)
        else:emit(0xB7AC6);t(r[6]&1);r[6]>>=1
        emit(0xB7AC8,0xB7ADE);r[12]=r[6];r[6]=r[2]&65535;r[2]=0x8832;r[13]&=65535;t(r[13]==0)
        r[5]=signed(read(0xB7AD2,0x8832,5,1),8)&MASK;r[2]=(-r[6])&MASK;r[5]&=255;macl=(r[2]*r[5])&MASK;r[6]=macl
        zero=r[13]==0;branch(0xB7ADA,zero,0xB7B06,True)
        if not zero:
            emit(0xB7ADE,0xB7AEC);r[1]=(r[6]*20)&MASK;r[7]=0x21BBC;r[0]=r[13]
            row=call(0xB7AE8,0x21BBC);signed_divider(row)
            emit(0xB7AEC,0xB7AF4);r[2]=0xFFFF0001;within=signed(r[0])>=-65535;t(within);r[6]=r[0]
            branch(0xB7AF0,not within,0xB7B0C,True)
            if within:emit(0xB7AF4,0xB7AFA);r[2]=MASK;r[6]=(r[6]-1)&MASK;control(0xB7AF6,'jump',0xB7B0E,True)
            else:emit(0xB7B0C);r[6]=0
        else:
            emit(0xB7B06,0xB7B0C);positive=signed(r[6])>=0;t(positive);r[6]=MASK;branch(0xB7B08,positive,0xB7B0E,True)
            if not positive:emit(0xB7B0C);r[6]=0
        emit(0xB7B0E,0xB7B18);r[4]=0x151F2;r[5]=0x13BF8;r[2]=0x264F8;r[6]&=65535
        row=call(0xB7B14,0x264F8);second=curve(0x264F8,16,row)
        emit(0xB7B18,0xB7B22);r[2]=r[0]&65535;r[6]=(-r[2])&MASK;r[2]=0xFFFFFF01
        within=signed(r[6])>=-255;t(within);branch(0xB7B20,within,0xB7B26)
        if within:emit(0xB7B26,0xB7B2C);r[2]=MASK;r[6]=(r[6]-1)&MASK;r[5]=r[6]
        else:emit(0xB7B22,0xB7B26);r[5]=0;control(0xB7B22,'jump',0xB7B2C,True)
        emit(0xB7B2C,0xB7B38);r[11]=(r[11]&255)+1;r[2]=r[11]&65535;r[4]=4
        above=r[2]>4;t(above);branch(0xB7B36,not above,0xB7B3A)
        if above:emit(0xB7B38);r[2]=4
        emit(0xB7B3A,0xB7B40);r[0]=r[2]&255;selector=r[0];t(selector==1);branch(0xB7B3E,selector==1,0xB7B5C)
        if selector==1:emit(0xB7B5C);r[14]=10
        else:
            emit(0xB7B40,0xB7B44);t(selector==2);branch(0xB7B42,selector==2,0xB7B56)
            if selector==2:
                emit(0xB7B56,0xB7B5C);r[0]=signed(read(0xB7B56,0x8A35,0,1),8)&MASK;r[14]=r[0];control(0xB7B58,'jump',0xB7B5E,True)
            else:
                emit(0xB7B44,0xB7B48);t(selector==3);branch(0xB7B46,selector==3,0xB7B52)
                if selector==3:
                    emit(0xB7B52,0xB7B56);r[0]=signed(read(0xB7B54,0x8A36,0,1),8)&MASK;control(0xB7B52,'jump',0xB7B58,True)
                    emit(0xB7B58,0xB7B5C);r[14]=r[0];control(0xB7B58,'jump',0xB7B5E,True)
                else:
                    emit(0xB7B48,0xB7B52);t(True);branch(0xB7B4A,False,0xB7B5E)
                    r[0]=signed(read(0xB7B4C,0x8A34,0,1),8)&MASK;r[14]=r[0];control(0xB7B4E,'jump',0xB7B5E,True)
        emit(0xB7B5E,0xB7B70);r[12]&=65535;r[6]=0x21CE0;r[5]&=255;macl=r[5]*r[12]
        r[2]=MASK;r[0]=255;r[1]=macl;r[14]&=255;row=call(0xB7B6C,0x21CE0);unsigned_divider(row)
        emit(0xB7B70,0xB7B7C);r[2]=r[0]&65535;r[6]=0x21CE0;macl=r[13]*r[2];r[0]=2500;r[1]=macl
        row=call(0xB7B78,0x21CE0);unsigned_divider(row)
        emit(0xB7B7C,0xB7B86);macl=(r[0]*r[14])&MASK;r[6]=RAM_BASE+0x28F8;r[0]=0x930;r[2]=macl;output=r[2]
        ram[0x3228:0x322C]=output.to_bytes(4,'big');event(0xB7B84,'write',RAM_BASE+0x3228,4,2,'ram',bytes(ram[0x3228:0x322C]))
        emit(0xB7B86,0xB7B98);stack+=4;gbr=pop(0xB7B88);macl=pop(0xB7B8A);pr=pop(0xB7B8C)
        for at,index in ((0xB7B8E,14),(0xB7B90,13),(0xB7B92,12),(0xB7B96,11)):r[index]=pop(at,index)
        control(0xB7B94,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:v&MASK for i,v in enumerate(r) if v is not None},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=output,
        byte_bias=bias,candidate=candidate,nonnegative=nonnegative)
