"""Separate three-mode state caller arithmetic and complete real surface/implicit-curve physical paths."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def position(knots,coordinate):
    """Select the rightmost qualifying byte knot without a monotonicity premise."""
    if (type(coordinate) is not int or not 0<=coordinate<=255 or len(knots)!=4
            or any(type(knot) is not int or not 0<=knot<=255 for knot in knots)):
        raise ValueError('the backward byte-axis equation changes an unsigned coordinate or physical byte')
    scanned=[]
    for index in range(len(knots)-1,-1,-1):
        scanned.append(index)
        if coordinate==knots[index] or coordinate>knots[index] and index==len(knots)-1:
            return dict(index=index,fraction=0,scanned=tuple(scanned),bracket=False)
        if coordinate>knots[index]:
            denominator=knots[index+1]-knots[index]
            if denominator<=0 or not knots[index]<coordinate<knots[index+1]:
                raise ValueError('the rightmost byte-axis bracket loses its positive actual divisor')
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
    if (type(entry) is not int or entry!=0x647E8
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the state surface caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the state surface caller equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the state surface caller equation loses one authoritative physical preimage')
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
            raise ValueError('the natural byte-axis caller loses its positive bounded division premise')
        emit(target,target+6);t(False);branch(target+2,False,target+0x92)
        push(target+4,r[2],2)
        emit(target+6,target+0x92)
        r[0]=r[1]=numerator//divisor
        r[2]=pop(target+0x8C,2)
        sr&=~0x301;sr_mask&=~0x101
        control(target+0x8E,'return',pr,True);returned(row,target+0x8E)

    def axis(target,width,row):
        nonlocal pr
        base,coordinate=r[0],r[5];maximum=3*width;r[3]=r[4]
        if width!=1 or r[4]!=maximum:raise ValueError('the byte-axis wrapper changes its actual complete axis extent')
        source=next(data for at,data in calibration.items() if at==base)
        pos=position(tuple(int.from_bytes(source[i:i+width],'big') for i in range(0,len(source),width)),coordinate);lookups.append(dict(kind='axis',target=target,base=base,**pos))
        emit(target)
        for index in pos['scanned']:
            emit(target+2,target+10);r[1]=read(target+2,base+width*index,1,width)
            equal=coordinate==r[1];t(equal);branch(target+8,equal,target+0x38)
            r[4]=width*index
            if equal:break
            emit(target+10,target+14);higher=coordinate>r[1];t(higher);branch(target+12,not higher,target+0x30)
            if higher:
                emit(target+14,target+18);last=index==3;t(last);branch(target+16,last,target+0x38)
                if last:break
                emit(target+18,target+42)
                r[5]=pos['numerator'];r[1]=read(target+24,base+width*index,1,width)
                next_word=read(target+26,base+width*index+width,0,width)
                r[0]=next_word-r[1];r[2]=0x26C78
                push(target+32,pr);r[1]=r[5]
                nested=call(target+38,r[2]);fraction(r[2],nested)
                emit(target+42,target+48);pr=pop(target+42)
                r[5]=r[0];control(target+44,'return',pr,True);returned(row,target+44)
                return pos
            emit(target+48,target+54);r[4]-=width;t(r[4]>=0);branch(target+52,r[4]>=0,target+2)
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

    def load(site,at,width,register):
        raw=bytes(ram[at:at+width]);event(site,'read',RAM_BASE+at,width,register,'ram',raw)
        value=int.from_bytes(raw,'big');return signed(value,width*8)&MASK if width<4 else value

    def put(site,at,width,register,value):
        ram[at:at+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')
        event(site,'write',RAM_BASE+at,width,register,'ram',bytes(ram[at:at+width]))

    def surface(row):
        nonlocal pr,macl
        emit(0x26770,0x2678A);push(0x26770,r[8],8);push(0x26772,pr)
        r[7]=macl;product=(r[5]&65535)*(r[0]&65535);r[4]=(r[4]+r[2]+product)&MASK
        r[0]=product;r[5]=(r[5]+r[4])&MASK;r[8]=r[1];r[7]=0x26740
        no_col_fraction=r[3]==0;t(no_col_fraction);branch(0x26788,no_col_fraction,0x267B0)
        if not no_col_fraction:
            emit(0x2678A,0x26794)
            r[1]=signed(read(0x2678A,r[4],1,1),8)&MASK
            r[0]=signed(read(0x2678C,r[4]+1,0,1),8)&MASK;r[2]=r[0]&255;r[0]=r[1]&255
            nested=call(0x26790,0x26740);first=interpolation(0x26740,nested)
            emit(0x26794,0x26798);no_row_fraction=r[8]==0;t(no_row_fraction)
            branch(0x26796,no_row_fraction,0x267C0)
            if not no_row_fraction:
                emit(0x26798,0x267A4);push(0x26798,r[0],0)
                r[1]=signed(read(0x2679A,r[5],1,1),8)&MASK
                r[0]=signed(read(0x2679C,r[5]+1,0,1),8)&MASK;r[2]=r[0]&255;r[0]=r[1]&255
                nested=call(0x267A0,0x26740);interpolation(0x26740,nested)
                emit(0x267A4,0x267AC);r[2]=r[0];r[0]=pop(0x267A6,0);r[3]=r[8]
                nested=call(0x267A8,0x26740);interpolation(0x26740,nested)
                emit(0x267AC,0x267B0);control(0x267AC,'jump',0x267C0,True)
        else:
            emit(0x267B0,0x267B6);no_row_fraction=r[8]==0;t(no_row_fraction)
            branch(0x267B2,no_row_fraction,0x267C0,True)
            r[0]=signed(read(0x267B4,r[4],0,1),8)&MASK
            if not no_row_fraction:
                emit(0x267B6,0x267C0);r[2]=signed(read(0x267B6,r[5],2,1),8)&MASK
                r[0]&=255;r[2]&=255;r[3]=r[8]
                nested=call(0x267BC,0x26740);interpolation(0x26740,nested)
        emit(0x267C0,0x267C6);pr=pop(0x267C0);r[8]=pop(0x267C4,8)
        control(0x267C2,'return',pr,True);returned(row,0x267C2)

    def byte_surface(row):
        nonlocal pr
        if (r[4],r[5],r[6])!=(0xB5FA,0x11FE2,0x11FDE):
            raise ValueError('the state surface wrapper changes its exact data or axis roots')
        emit(0x26084,0x26094);push(0x26084,pr);push(0x26086,r[4],4)
        r[7]&=255;r[0]=r[5];r[5]=r[7];r[7]=0x26944;r[4]=3
        nested=call(0x26090,0x26944);first=axis(0x26944,1,nested)
        emit(0x26094,0x260A2);push(0x26094,r[4],4);push(0x26096,r[5],5)
        r[0]=r[6];r[5]=frame_access(0x2609A,'read',stack+16,4,5)&255;r[4]=3
        nested=call(0x2609E,0x26944);second=axis(0x26944,1,nested)
        emit(0x260A2,0x260B4);r[1]=pop(0x260A2,1);r[0]=pop(0x260A4,0)
        r[2]=r[4];r[3]=r[5];r[4]=pop(0x260AA,4);pr=pop(0x260AC);r[7]=0x26770;r[5]=4
        control(0x260B0,'jump',0x26770,True);surface(row)
        lookups.append(dict(kind='four-row-surface',row=first,col=second,value=r[0]&255))

    def implicit_curve(row):
        base,coordinate=r[4],r[5]&255
        if base!=0x11FE6:raise ValueError('the implicit curve changes its exact natural eight-byte root')
        emit(0x26370,0x26378);r[0]=224;r[5]=coordinate;endpoint=coordinate>=224;t(endpoint)
        branch(0x26376,endpoint,0x2637E)
        if endpoint:
            emit(0x2637E,0x26382);r[0]=signed(read(0x26380,base+7,0,1),8)&MASK
            control(0x2637E,'return',pr,True);returned(row,0x2637E)
            lookups.append(dict(kind='implicit-byte-curve',index=7,fraction=0,endpoint=True,value=r[0]&255))
        else:
            emit(0x26378,0x2637E);r[6]=0x26A80;r[3]=0;control(0x2637A,'jump',0x26A80,True)
            emit(0x26A80,0x26A9C);index,remainder=divmod(coordinate,32)
            r[5]=index;r[3]=remainder<<11;r[0]=0;t(True);branch(0x26A9A,True,0x26AAA)
            emit(0x26AAA,0x26ABA);r[4]=base+index
            r[1]=signed(read(0x26AAC,r[4],1,1),8)&MASK
            r[0]=signed(read(0x26AAE,r[4]+1,0,1),8)&MASK;r[2]=r[0]&255;r[0]=r[1]&255;r[6]=0x26740
            control(0x26AB6,'jump',0x26740,True);value=interpolation(0x26740,row)
            lookups.append(dict(kind='implicit-byte-curve',index=index,fraction=remainder<<11,endpoint=False,**value))

    def first_mode():
        nonlocal macl
        emit(0x6481A,0x64836);r[13]=RAM_BASE+0x28F8;r[5]=3;r[0]=0xA7B;r[14]=RAM_BASE+0x128C
        r[2]=load(0x64822,0x3373,1,2);r[0]=0x5E7;put(0x64826,0x1873,1,2,r[2])
        r[2]=MASK;r[0]=0x152;put(0x6482C,0x13DE,2,2,r[2]);r[0]=load(0x6482E,0x1083,1,0)
        r[2]=r[0]&255;above=r[2]>3;t(above);branch(0x64834,not above,0x64838)
        if above:emit(0x64836);r[2]=3
        emit(0x64838,0x64844);r[0]=load(0x64838,0x1082,1,0);r[4]=r[2];r[5]=1;r[2]=r[0]&255
        inside=r[2]>=1;t(inside);branch(0x64842,inside,0x64846)
        if not inside:emit(0x64844);r[2]=1
        emit(0x64846,0x6484E);r[2]&=255;r[5]=4;above=r[2]>4;t(above);branch(0x6484C,not above,0x64850)
        if above:emit(0x6484E);r[2]=4
        emit(0x64850,0x6487A);r[0]=(r[2]&255)*4;r[5]=0xB60A;r[7]=RAM_BASE+0x119C
        r[4]&=255;r[2]=0x26084;r[5]-=4;r[0]+=r[4];r[4]=0xB5FA
        r[6]=signed(read(0x64862,r[5]+r[0],6,1),8)&MASK;r[0]=0x5D5;r[5]=0x11FE2
        put(0x64868,0x1861,1,6,r[6]);r[0]=r[6];frame_access(0x6486C,'write',stack+3,1,0,r[0])
        r[0]=0x12;r[6]=load(0x64870,0x11AE,1,6);r[7]=r[6]&255;r[6]=0x11FDE
        row=call(0x64876,0x26084);byte_surface(row)
        emit(0x6487A,0x64886);r[2]=r[0]&255;r[0]=0xA7B;r[5]=load(0x6487E,0x3373,1,5);r[6]=r[5]&255
        macl=(r[2]&65535)*(r[6]&65535);control(0x64882,'jump',0x649FE,True)

    def second_mode():
        nonlocal macl
        emit(0x6490A,0x64914);r[0]=load(0x6490A,0x1083,1,0);r[5]=1;r[2]=r[0]&255
        inside=r[2]>=1;t(inside);branch(0x64912,inside,0x64916)
        if not inside:emit(0x64914);r[2]=1
        emit(0x64916,0x6491E);r[2]&=255;r[5]=4;above=r[2]>4;t(above);branch(0x6491C,not above,0x64920)
        if above:emit(0x6491E);r[2]=4
        emit(0x64920,0x6493E);r[2]=(r[2]-1)&255;r[6]=0x12B62;r[4]=r[2];r[13]=RAM_BASE+0x28F8;r[0]=r[4]
        r[2]=signed(read(0x6492C,r[6]+r[0],2,1),8)&MASK;r[0]=0xA7B;r[6]=r[2]&255
        r[7]=load(0x64932,0x3373,1,7)&255;macl=(r[6]*r[7])&MASK;r[2]=macl
        nonnegative=signed(r[2])>=0;t(nonnegative);branch(0x6493C,nonnegative,0x64944)
        if not nonnegative:raise ValueError('two unsigned bytes exceed their exact65025 product bound')
        emit(0x64944,0x64960);r[6]=r[2]>>8;r[5]=((r[6]&65535)<<16)|(r[6]>>16)
        r[14]=RAM_BASE+0x128C;r[6]=signed(r[5]&255,8)&MASK;r[0]=0x5E7
        r[5]=((r[5]>>16)|(r[6]<<16))&MASK;r[6]=r[7];put(0x64954,0x1873,1,5,r[5])
        r[5]&=255;r[6]=(r[6]-r[5])&MASK;r[2]=signed(r[6]&65535,16)&MASK
        nonnegative=signed(r[2])>=0;t(nonnegative);branch(0x6495E,nonnegative,0x64962)
        if not nonnegative:raise ValueError('floor(unsigned-byte*unsigned-byte/256) exceeds its unsigned-byte multiplicand')
        emit(0x64962,0x64980);r[6]=r[2];r[2]=0x11FE6;r[0]=r[4];r[2]+=12
        r[5]=signed(read(0x6496A,r[2]+r[0],5,1),8)&MASK;r[0]=0x152;r[5]&=255
        macl=(r[5]&65535)*(r[6]&65535);r[6]=0x8799;r[2]=macl;put(0x64976,0x13DE,2,2,r[2])
        r[2]=signed(read(0x64978,0x8799,2,1),8)&MASK;r[6]=r[2]&255
        macl=(r[7]&65535)*(r[6]&65535);control(0x6497C,'jump',0x649FE,True)

    def third_mode():
        nonlocal macl
        emit(0x6498C,0x6499E);r[14]=RAM_BASE+0x128C;r[2]=0;r[0]=0x5E7;r[5]=1
        put(0x64994,0x1873,1,2,r[2]);r[0]=load(0x64996,0x1083,1,0);r[2]=r[0]&255
        inside=r[2]>=1;t(inside);branch(0x6499C,inside,0x649A0)
        if not inside:emit(0x6499E);r[2]=1
        emit(0x649A0,0x649A8);r[2]&=255;r[5]=4;above=r[2]>4;t(above);branch(0x649A6,not above,0x649AA)
        if above:emit(0x649A8);r[2]=4
        emit(0x649AA,0x649E2);r[4]=0x11FE6;r[0]=r[2]&255;r[13]=RAM_BASE+0x28F8;r[2]=r[4]+7
        r[6]=signed(read(0x649B4,r[2]+r[0],6,1),8)&MASK;r[0]=0xA7B;r[2]=r[6]&255
        r[6]=load(0x649BA,0x3373,1,6);r[0]=0x152;r[5]=r[6]&255;r[6]=RAM_BASE+0x40C6
        macl=(r[2]&65535)*(r[5]&65535);r[2]=macl;put(0x649C6,0x13DE,2,2,r[2])
        r[2]=load(0x649C8,0x40C6,2,2);r[6]=r[2]&65535;r[2]=0x2D0E
        macl=(r[6]*r[2])&MASK;r[5]=((macl>>15)-32)&MASK
        nonnegative=signed(r[5])>=0;t(nonnegative);branch(0x649E0,nonnegative,0x649E4)
        if not nonnegative:emit(0x649E2);r[5]=0
        emit(0x649E4,0x649EC);r[6]=255;above=signed(r[5])>255;t(above);branch(0x649EA,not above,0x649EE)
        if above:emit(0x649EC);r[5]=r[6]
        emit(0x649EE,0x649F4);r[2]=0x26370;r[5]&=255
        row=call(0x649F0,0x26370);implicit_curve(row)
        emit(0x649F4,0x649FE);r[2]=r[0]&255;r[0]=0xA7B;r[6]=load(0x649F8,0x3373,1,6);r[5]=r[6]&255
        macl=(r[2]&65535)*(r[5]&65535)

    emit(0x647E8,0x64804);push(0x647E8,r[13],13);push(0x647EA,r[14],14)
    push(0x647EC,pr);push(0x647EE,macl);push(0x647F0,gbr)
    r[0]=gbr=RAM_BASE+0x1082;stack-=4;r[2]=0x8B3F
    r[0]=signed(read(0x647FA,0x8B3F,0,1),8)&MASK;r[0]&=16;configured=bool(r[0]);t(not configured)
    branch(0x64800,not configured,0x6480E,True);r[5]=r[0];first=False
    if configured:
        emit(0x64804,0x6480E);r[0]=load(0x64804,0x1083,1,0);r[6]=r[0];r[0]=load(0x64808,0x1082,1,0)
        higher_or_equal=r[6]>=r[0];t(higher_or_equal);branch(0x6480C,not higher_or_equal,0x6481A)
        first=not higher_or_equal
    if not first:
        emit(0x6480E,0x64812);t(r[5]==0);branch(0x64810,r[5]!=0,0x648F0)
        if not configured:
            emit(0x64812,0x6481A);r[6]=RAM_BASE+0x244F;r[0]=load(0x64814,0x244F,1,0)
            first=bool(r[0]&64);t(not first);branch(0x64818,not first,0x648F0)
    mode='bypass'
    if first:
        mode='surface';first_mode()
    else:
        emit(0x648F0,0x648F4);t(r[5]==0);branch(0x648F2,r[5]==0,0x648FE);second=False
        if configured:
            emit(0x648F4,0x648FE);r[0]=load(0x648F4,0x1083,1,0);r[6]=r[0];r[0]=load(0x648F8,0x1082,1,0)
            second=r[6]>r[0];t(second);branch(0x648FC,second,0x6490A)
        if not second:
            emit(0x648FE,0x64902);t(r[5]==0);branch(0x64900,r[5]!=0,0x64980)
            if not configured:
                emit(0x64902,0x6490A);r[6]=RAM_BASE+0x244F;r[0]=load(0x64904,0x2450,1,0)
                second=bool(r[0]&32);t(not second);branch(0x64908,not second,0x64980)
        if second:
            mode='split';second_mode()
        else:
            emit(0x64980,0x64984);t(r[5]==0);branch(0x64982,r[5]!=0,0x64A06)
            if r[5]==0:
                emit(0x64984,0x6498C);r[6]=RAM_BASE+0x244F;r[0]=load(0x64986,0x244F,1,0)
                admitted=bool(r[0]&1);t(not admitted);branch(0x6498A,not admitted,0x64A06)
                if admitted:mode='implicit';third_mode()
    if mode!='bypass':
        emit(0x649FE,0x64A06);r[2]=macl;r[0]=0x150;put(0x64A04,0x13DC,2,2,r[2])
    emit(0x64A06,0x64A14);stack+=4;gbr=pop(0x64A08);macl=pop(0x64A0A);pr=pop(0x64A0C)
    r[14]=pop(0x64A0E,14);r[13]=pop(0x64A12,13);control(0x64A10,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:value&MASK for i,value in enumerate(r)},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,mode=mode,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0])
