"""Separate complete state transitions, byte interpolation and BFS window equations."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def linear(first,second,fraction):
    if any(type(v) is not int or not 0<=v<=65535 for v in (first,second,fraction)):
        raise ValueError('the word interpolation equation changes an unsigned operand width')
    magnitude=abs(second-first)*fraction//65536
    ascending=second>=first
    return dict(value=first+magnitude if ascending else first-magnitude,magnitude=magnitude,
        first=first,second=second,fraction=fraction,ascending=ascending)


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry!=0x3A750
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the BFS state caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the BFS state caller equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the BFS state caller equation loses one authoritative physical preimage')
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

    def implicit_curve(row):
        base,coordinate=r[4],r[5]&255
        if base!=0x12A3A:raise ValueError('the implicit curve changes its exact natural eight-byte root')
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


    def predicate(row):
        emit(0x25E20,0x25E28);r[1]=RAM_BASE+0x5718;r[0]=signed(r[4]&65535,16)&MASK
        invalid=r[0]==MASK;t(invalid);branch(0x25E26,invalid,0x25E3E)
        if invalid:emit(0x25E3E);r[2]=0
        else:
            emit(0x25E28,0x25E3E);r[6]=r[1];r[2]=r[0]
            r[2]=(r[2]*3)&MASK;r[6]=(r[6]+r[2])&MASK
            r[0]=load(0x25E32,r[6]-RAM_BASE+1,1,0)
            t(not bool(r[0]&128));r[0]=(sr&1)^1;r[2]=r[0]
            control(0x25E3A,'jump',0x25E40,True)
        emit(0x25E40,0x25E44);r[0]=r[2];control(0x25E40,'return',pr,True);returned(row,0x25E40)

    emit(0x3A750,0x3A762);push(0x3A750,pr);push(0x3A752,gbr)
    r[0]=RAM_BASE+0x39C4;gbr=r[0];stack-=8;r[0]=load(0x3A75A,0x39D0,4,0)
    first=r[0];t(not bool(first));branch(0x3A75E,bool(first),0x3A788,True);r[4]=r[0]
    action=None
    if first==0:
        emit(0x3A762,0x3A76A);r[6]=RAM_BASE+0x2458;r[0]=load(0x3A764,0x2462,1,0)
        active=bool(r[0]&1);t(not active);branch(0x3A768,not active,0x3A7B2)
        if not active:action='zero'
        else:
            emit(0x3A76A,0x3A776);r[7]=RAM_BASE+0x1072;r[4]=0x12A3A
            r[0]=load(0x3A76E,0x1077,1,0);r[2]=0x26370;r[5]=r[0]&255
            implicit_curve(call(0x3A772,0x26370))
            emit(0x3A776,0x3A788);r[2]=r[0];r[6]=RAM_BASE+0x1E60;r[0]=0x46
            r[5]=RAM_BASE+0x24F9;r[0]<<=2;put(0x3A780,0x1F78,1,2,r[2])
            r[0]=0x49;control(0x3A784,'jump',0x3A7A0,True);put(0x3A786,0x2542,1,2,r[2])
            action='one'
    else:
        emit(0x3A788,0x3A78E);r[0]=r[4];is_one=r[0]==1;t(is_one);branch(0x3A78C,not is_one,0x3A7A4)
        if is_one:
            emit(0x3A78E,0x3A796);r[6]=RAM_BASE+0x2458;r[0]=load(0x3A790,0x2462,1,0)
            active=bool(r[0]&1);t(not active);branch(0x3A794,not active,0x3A7B2)
            if not active:action='zero'
            else:
                emit(0x3A796,0x3A7A0);r[5]=RAM_BASE+0x24F9;r[0]=0x49
                r[2]=load(0x3A79A,0x2542,1,2);empty=not bool(r[2]);t(empty);branch(0x3A79E,empty,0x3A7B6)
                action='two' if empty else 'one'
        else:
            emit(0x3A7A4,0x3A7AA);r[0]=r[4];is_two=r[0]==2;t(is_two);branch(0x3A7A8,not is_two,0x3A7BC)
            if is_two:
                emit(0x3A7AA,0x3A7B2);r[6]=RAM_BASE+0x2458;r[0]=load(0x3A7AC,0x2462,1,0)
                active=bool(r[0]&1);t(not active);branch(0x3A7B0,active,0x3A7B6)
                action='two' if active else 'zero'
    if action is not None:
        if action=='one':
            emit(0x3A7A0,0x3A7A4);control(0x3A7A0,'jump',0x3A7B8,True);r[4]=1
        elif action=='zero':
            emit(0x3A7B2,0x3A7B6);control(0x3A7B2,'jump',0x3A7B8,True);r[4]=0
        else:emit(0x3A7B6);r[4]=2
        emit(0x3A7B8,0x3A7BC);r[0]=r[4];put(0x3A7BA,0x39D0,4,0,r[0])

    emit(0x3A7BC,0x3A7CA);r[7]=RAM_BASE+0x1072;r[6]=RAM_BASE+0x24B0
    r[0]=load(0x3A7C0,0x1079,1,0);r[5]=r[0]&255;r[0]=load(0x3A7C4,0x24BA,1,0)
    prior_hot=bool(r[0]&128);t(not prior_hot);branch(0x3A7C8,not prior_hot,0x3A7CC)
    if prior_hot:emit(0x3A7CA);r[5]=(r[5]+4)&MASK
    emit(0x3A7CC,0x3A7D6);r[6]=0x875C;r[2]=signed(read(0x3A7CE,0x875C,2,1),8)&MASK;r[2]&=255
    hot=r[5]>=r[2];t(hot);branch(0x3A7D4,hot,0x3A7DE)
    if hot:
        emit(0x3A7DE,0x3A7E4);r[6]=RAM_BASE+0x24B0;r[0]=load(0x3A7E0,0x24BA,1,0);r[0]|=128
    else:
        emit(0x3A7D6,0x3A7DE);r[6]=RAM_BASE+0x24B0;r[0]=load(0x3A7D8,0x24BA,1,0)
        control(0x3A7DA,'jump',0x3A7E4,True);r[0]&=127
    emit(0x3A7E4,0x3A7EE);put(0x3A7E4,0x24BA,1,0,r[0]);r[0]=load(0x3A7E6,0x39D4,4,0)
    prior_second=r[0];t(not bool(prior_second));branch(0x3A7EA,bool(prior_second),0x3A892,True);r[2]=r[0]

    def initial_window():
        emit(0x3A7EE,0x3A7F6);r[6]=RAM_BASE+0x2458;r[0]=load(0x3A7F0,0x2465,1,0)
        allow=bool(r[0]&64);t(not allow);branch(0x3A7F4,not allow,0x3A88C)
        if not allow:return 'clear'
        emit(0x3A7F6,0x3A7FC);r[0]=r[4];allow=r[0]==2;t(allow);branch(0x3A7FA,not allow,0x3A88C)
        if not allow:return 'clear'
        emit(0x3A7FC,0x3A804);r[6]=RAM_BASE+0x24B0;r[0]=load(0x3A7FE,0x24BA,1,0)
        allow=bool(r[0]&128);t(not allow);branch(0x3A802,not allow,0x3A88C)
        if not allow:return 'clear'
        emit(0x3A804,0x3A80C);r[6]=RAM_BASE+0x2458;r[0]=load(0x3A806,0x2459,1,0)
        allow=bool(r[0]&32);t(not allow);branch(0x3A80A,not allow,0x3A88C)
        if not allow:return 'clear'
        emit(0x3A80C,0x3A814);r[2]=0x25E20;r[4]=0x129;predicate(call(0x3A810,0x25E20))
        emit(0x3A814,0x3A818);blocked=bool(r[0]);t(not blocked);branch(0x3A816,blocked,0x3A88C)
        if blocked:return 'clear'
        emit(0x3A818,0x3A82A);r[2]=0x8AD9;r[6]=RAM_BASE+0x24B0
        r[4]=signed(read(0x3A81C,0x8AD9,4,1),8)&MASK;r[0]=load(0x3A81E,0x24B1,1,0)
        r[4]&=255;alternate=bool(r[0]&16);t(not alternate);r[7]=r[4]
        branch(0x3A826,alternate,0x3A872,True);r[7]=(r[7]<<8)&MASK
        if alternate:
            emit(0x3A872,0x3A87C);r[3]=RAM_BASE+0x1024;r[0]=load(0x3A874,0x1026,2,0);r[5]=r[0]&65535
            above=r[5]>=r[7];t(above);branch(0x3A87A,above,0x3A88C)
            if above:return 'clear'
            emit(0x3A87C,0x3A88C);r[3]=RAM_BASE+0x1048;r[4]=(r[4]<<8)&MASK;r[4]=(r[4]-r[5])&MASK
            r[0]=load(0x3A882,0x1062,2,0);r[6]=r[0]&65535;r[6]=(r[6]<<2)&MASK
            control(0x3A888,'jump',0x3A89E,True);t(signed(r[6])>signed(r[4]))
            return 'xor'
        emit(0x3A82A,0x3A84C);r[3]=RAM_BASE+0x1024;r[2]=r[4];r[1]=RAM_BASE+0x1048
        r[2]=(r[2]<<8)&MASK;r[0]=load(0x3A832,0x1026,2,0);r[5]=r[0]&65535
        r[0]=load(0x3A836,0x1062,2,0);above=signed(r[5])>=signed(r[2]);t(above)
        r[1]=r[0]&65535;r[0]=load(0x3A83C,0x1026,2,0);r[1]=(r[1]<<2)&MASK
        frame_access(0x3A840,'write',stack,4,1,r[1]);r[1]=r[0]&65535;r[1]=(r[1]+r[7])&MASK
        r[6]=frame_access(0x3A846,'read',stack,4,6);branch(0x3A848,not above,0x3A86A,True)
        frame_access(0x3A84A,'write',stack+4,4,1,r[1])
        if not above:
            emit(0x3A86A,0x3A870);t(r[1]>r[6]);control(0x3A86C,'jump',0x3A88E,True);r[2]=sr&1
            return 'common'
        emit(0x3A84C,0x3A850);greater=r[1]>r[6];t(greater);branch(0x3A84E,not greater,0x3A88C)
        if not greater:return 'clear'
        emit(0x3A850,0x3A866);r[3]=RAM_BASE+0x1048;r[4]=(r[4]<<8)&MASK;r[1]=RAM_BASE+0x1024
        r[0]=load(0x3A856,0x1062,2,0);r[5]=r[0]&65535;r[0]=load(0x3A85A,0x1026,2,0)
        r[5]=(r[5]<<2)&MASK;r[6]=r[0]&65535;r[6]=(r[6]-r[4])&MASK
        sufficient=signed(r[5])>=signed(r[6]);t(sufficient);branch(0x3A864,not sufficient,0x3A88C)
        if not sufficient:return 'clear'
        emit(0x3A866,0x3A86A);control(0x3A866,'jump',0x3A88E,True);r[2]=1
        return 'common'

    update_second=False
    if prior_second==0:
        flow=initial_window();update_second=True
        if flow=='clear':emit(0x3A88C);r[2]=0
        if flow in ('clear','common'):
            emit(0x3A88E,0x3A892);control(0x3A88E,'jump',0x3A8A4,True);r[0]=r[2]
        else:
            emit(0x3A89E,0x3A8A4);r[0]=(sr&1)^1;r[2]=r[0]
    else:
        emit(0x3A892,0x3A898);r[0]=r[2];is_one=r[0]==1;t(is_one);branch(0x3A896,not is_one,0x3A8A6)
        if is_one:
            emit(0x3A898,0x3A8A4);r[6]=RAM_BASE+0x2458;r[0]=load(0x3A89A,0x2459,1,0)
            t(not bool(r[0]&32));r[0]=(sr&1)^1;r[2]=r[0];update_second=True
    if update_second:emit(0x3A8A4);put(0x3A8A4,0x39D4,4,0,r[0])
    emit(0x3A8A6,0x3A8AA);nonzero=bool(r[2]);t(not nonzero);branch(0x3A8A8,nonzero,0x3A8B4)
    publish=False
    if not nonzero:
        emit(0x3A8AA,0x3A8B4);r[6]=r[5]=RAM_BASE+0x2458;r[0]=load(0x3A8AE,0x2461,1,0)
        control(0x3A8B0,'jump',0x3A8C2,True);r[0]&=0xDF;publish=True
    else:
        emit(0x3A8B4,0x3A8BA);r[0]=r[2];is_one=r[0]==1;t(is_one);branch(0x3A8B8,not is_one,0x3A8C4)
        if is_one:
            emit(0x3A8BA,0x3A8C2);r[6]=r[5]=RAM_BASE+0x2458;r[0]=load(0x3A8BE,0x2461,1,0)
            r[0]|=32;publish=True
    if publish:emit(0x3A8C2);put(0x3A8C2,0x2461,1,0,r[0])
    emit(0x3A8C4,0x3A8CE);stack+=8;gbr=pop(0x3A8C6);pr=pop(0x3A8C8)
    control(0x3A8CA,'return',pr,True)
    wide=quantities(memory,calibration)
    if bytes(ram)!=wide['memory']:raise ValueError('the complete scalar state disagrees with separate wide quantity equations')
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:value&MASK for i,value in enumerate(r)},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0],quantities=wide)

def quantities(memory,calibration):
    """Compute every publication with wide arithmetic and separately stated state transitions."""
    if type(memory) is not bytes or len(memory)!=65536:raise ValueError('the state quantity equations need complete RAM')
    def rom(address,size=1):
        rows=[(at,data) for at,data in calibration.items() if at<=address and address+size<=at+len(data)]
        if len(rows)!=1:raise ValueError('the state quantity equations lose one physical ROM operand')
        at,data=rows[0];return int.from_bytes(data[address-at:address-at+size],'big')
    def word(at):return int.from_bytes(memory[at:at+2],'big')
    first=int.from_bytes(memory[0x39D0:0x39D4],'big');second=int.from_bytes(memory[0x39D4:0x39D8],'big')
    result=bytearray(memory);lookup=None
    if first==0:
        if memory[0x2462]&1:
            coordinate=memory[0x1077];index=min(coordinate//32,7);fraction=(coordinate%32)*2048
            a=rom(0x12A3A+index)
            if index==7:lookup=a
            else:
                z=rom(0x12A3B+index);delta=abs(z-a)*fraction//65536
                lookup=a+delta if z>=a else a-delta
            result[0x1F78]=result[0x2542]=lookup;first=1
    elif first in (1,2):
        first=(2 if first==2 or memory[0x2542]==0 else 1) if memory[0x2462]&1 else 0
    result[0x39D0:0x39D4]=first.to_bytes(4,'big')
    hot=memory[0x1079]+(4 if memory[0x24BA]&128 else 0)>=rom(0x875C)
    result[0x24BA]=(memory[0x24BA]&127)|(128 if hot else 0)
    center=rom(0x8AD9)*256;coordinate=word(0x1026);width=word(0x1062)*4
    if second==0:
        eligible=(memory[0x2465]&64 and first==2 and hot and memory[0x2459]&32 and not memory[0x5A94]&128)
        if not eligible:second=0
        elif memory[0x24B1]&16:second=int(coordinate<center and width<=center-coordinate)
        elif coordinate<center:second=int(coordinate+center>width)
        else:second=int(coordinate+center>width and width>=coordinate-center)
    elif second==1:second=int(bool(memory[0x2459]&32))
    result[0x39D4:0x39D8]=second.to_bytes(4,'big')
    if second in (0,1):result[0x2461]=(memory[0x2461]&0xDF)|(32 if second else 0)
    return dict(memory=bytes(result),first_state=first,second_state=second,lookup=lookup,
        hot=hot,center=center,coordinate=coordinate,width=width)
