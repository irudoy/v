"""Separate complete state-ratio, counter, byte transition and fixed-root lookup equations."""
from kb import division_callees_semantics as division
MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry not in (0x64CB2,0xBDC66)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the state ratio caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the state ratio caller equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the state ratio caller equation loses one authoritative physical preimage')
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

    def load(site,address,width,register):
        raw=bytes(ram[address:address+width]);event(site,'read',RAM_BASE+address,width,register,'ram',raw)
        value=int.from_bytes(raw,'big');return signed(value,width*8)&MASK if width<4 else value

    def put(site,address,width,register,value):
        ram[address:address+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big')
        event(site,'write',RAM_BASE+address,width,register,'ram',bytes(ram[address:address+width]))

    def signed_divider(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2];denominator=signed(divisor);dividend=signed(numerator)
        if denominator==0 or not -32768<=denominator<=32767:
            raise ValueError('the actual state-ratio signed helper loses its nonzero signed-word divisor')
        negative=bool((divisor^numerator)&0x80000000)
        long_path=abs(dividend)>=abs(denominator)*256
        saved_r2,saved_r3,saved_r4=r[2:5]
        emit(0x21BBC,0x21BC2);push(0x21BBC,saved_r2,2);t(False);branch(0x21BC0,False,0x21C70)
        emit(0x21BC2,0x21BCC);push(0x21BC2,saved_r3,3);t(denominator>0);branch(0x21BCA,denominator>0,0x21BD0)
        if denominator<0:emit(0x21BCC,0x21BD0)
        emit(0x21BD0,0x21BD4);t(dividend>0);branch(0x21BD2,dividend>0,0x21BD8)
        if dividend<=0:emit(0x21BD4,0x21BD8)
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
        row.update(divisor=divisor,dividend=numerator,long_path=long_path,quotient_sign_flag=negative)
        control(terminal,'return',pr,True);returned(row,terminal)

    def unsigned_divider(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2]
        if not 0<divisor<=65535 or not 0<=numerator<=MASK:
            raise ValueError('the actual state-ratio unsigned helper loses its positive bounded variable divisor')
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

    def byte_curve(row):
        base,coordinate=r[4],r[5]&255
        if base not in (0x12EFE,0x12F06):raise ValueError('the actual byte lookup changes one of its two exact roots')
        emit(0x26370,0x26378);r[0]=224;r[5]=coordinate;endpoint=coordinate>=224;t(endpoint)
        branch(0x26376,endpoint,0x2637E)
        if endpoint:
            emit(0x2637E,0x26382);r[0]=signed(read(0x26380,base+7,0,1),8)&MASK
            terminal=0x2637E;index=7;fraction=0
        else:
            emit(0x26378,0x2637E);r[6]=0x26A80;r[3]=0;control(0x2637A,'jump',0x26A80,True)
            emit(0x26A80,0x26A9C);index=coordinate//32;fraction=(coordinate%32)<<11
            r[5]=index;r[3]=fraction;r[0]=0;t(True);branch(0x26A9A,True,0x26AAA)
            emit(0x26AAA,0x26ABA);r[4]=base+index
            r[1]=signed(read(0x26AAC,r[4],1,1),8)&MASK
            r[0]=signed(read(0x26AAE,r[4]+1,0,1),8)&MASK
            r[2]=r[0]&255;r[0]=r[1]&255;r[6]=0x26740;control(0x26AB6,'jump',0x26740,True)
            first,second=r[0],r[2];ascending=second>=first;magnitude=abs(second-first)*fraction//65536
            emit(0x26740,0x26744);t(ascending);branch(0x26742,ascending,0x2675C)
            r[1]=macl
            if ascending:
                emit(0x2675C,0x2676E);r[2]=magnitude;r[0]=first+magnitude;terminal=0x2676A
            else:
                emit(0x26744,0x2675C);push(0x26744,first,0);pop(0x26752,2)
                r[2]=r[0]=first-magnitude;terminal=0x26758
        lookups.append(dict(base=base,coordinate=coordinate,index=index,fraction=fraction,
            endpoint=endpoint,raw_result=r[0],byte_value=r[0]&255))
        control(terminal,'return',pr,True);returned(row,terminal)

    def ratio_caller():
        nonlocal stack,gbr,macl,pr
        def publish6():
            emit(0x64E52,0x64E58);r[0]=0x5DA;put(0x64E56,0x1866,2,6,r[6])
            control(0x64E54,'jump',0x64FD6,True)
        def publish2(zero=False):
            if zero:emit(0x64FCE);r[2]=0
            emit(0x64FD0,0x64FD6);r[14]=RAM_BASE+0x128C;r[0]=0x5DA;put(0x64FD4,0x1866,2,2,r[2])
        emit(0x64CB2,0x64CC8);push(0x64CB2,r[14],14);push(0x64CB4,pr);push(0x64CB6,macl);push(0x64CB8,gbr)
        r[0]=gbr=RAM_BASE+0x128C;stack-=8;r[6]=0x870C;r[0]=signed(read(0x64CC2,0x870C,0,1),8)&MASK
        primary=bool(r[0]&128);t(not primary);branch(0x64CC6,not primary,0x64D9C)
        if primary:
            emit(0x64CC8,0x64CD2);r[5]=RAM_BASE+0x2470;r[0]=0x12;r[0]=load(0x64CCC,0x2482,1,0)
            both=bool(r[0]&1);t(not both);branch(0x64CD0,not both,0x64D08)
            if both:
                emit(0x64CD2,0x64CD8);r[0]=load(0x64CD2,0x247C,1,0);both=bool(r[0]&1)
                t(not both);branch(0x64CD6,not both,0x64D08)
            if both:
                emit(0x64CD8,0x64CE0);r[6]=RAM_BASE+0x424C;r[0]=load(0x64CDA,0x4250,1,0)
                both=(r[0]&128)==0;t(both);branch(0x64CDE,not both,0x64D08)
            if both:
                emit(0x64CE0,0x64CEE);r[4]=RAM_BASE+0x4188;r[6]=RAM_BASE+0x246A
                r[0]=load(0x64CE4,0x418E,1,0);r[2]=load(0x64CE6,0x246A,1,2)
                active=bool(r[0]&32);t(not active);r[7]=r[2]&255;branch(0x64CEA,active,0x64D00,True)
                if active:
                    emit(0x64D00,0x64D04);r[0]=r[7]|1
                else:
                    emit(0x64CEE,0x64D00);r[0]=0x33;r[0]=load(0x64CF0,0x24A3,1,0);r[0]&=0xBF;r[2]=r[0]
                    r[0]=0x33;put(0x64CF8,0x24A3,1,2,r[2]);r[0]=r[7]&0xFE
                    control(0x64CFC,'jump',0x64D04,True)
                emit(0x64D04,0x64D08);r[7]=r[0];control(0x64D04,'jump',0x64D1A,True)
            else:
                emit(0x64D08,0x64D1A);r[0]=0x33;r[6]=RAM_BASE+0x246A
                r[0]=load(0x64D0C,0x24A3,1,0)|0x40;r[2]=r[0];r[0]=0x33
                put(0x64D14,0x24A3,1,2,r[2]);r[0]=load(0x64D16,0x246A,1,0)&0xFE
            emit(0x64D1A,0x64D22);put(0x64D1A,0x246A,1,0,r[0]);r[0]=signed(r[0]&255,8)&MASK
            active=bool(r[0]&1);t(not active);branch(0x64D20,not active,0x64D70)
            if active:
                emit(0x64D22,0x64D2C);r[2]=RAM_BASE+0x23BC;r[0]=0x52;r[5]=load(0x64D26,0x240E,2,5)
                nonzero=r[5]!=0;t(not nonzero);branch(0x64D2A,nonzero,0x64D30)
                if not nonzero:
                    emit(0x64D2C,0x64D30);control(0x64D2C,'jump',0x64FCE,True);publish2(True);return
                emit(0x64D30,0x64D42);r[6]=0x8EA6;r[5]=signed(r[5]&65535,16)&MASK
                r[2]=signed(read(0x64D34,0x8EA6,2),16)&MASK;r[6]=(r[5]-r[2])&MASK;r[2]=0xFFFF8000
                within=signed(r[6])>=-32768;t(within);branch(0x64D40,within,0x64D44)
                if not within:emit(0x64D42);r[6]=r[2]
                emit(0x64D44,0x64D4A);r[2]=32767;above=signed(r[6])>32767;t(above);branch(0x64D48,not above,0x64D4C)
                if above:emit(0x64D4A);r[6]=r[2]
                emit(0x64D4C,0x64D58);r[1]=(r[6]<<16)&MASK;r[6]=0x21BBC;r[5]=signed(r[5]&65535,16)&MASK;r[0]=r[5]
                row=call(0x64D54,0x21BBC);signed_divider(row)
                emit(0x64D58,0x64D5E);positive=signed(r[0])>=0;t(positive);r[6]=r[0];branch(0x64D5A,positive,0x64D60,True)
                if not positive:emit(0x64D5E);r[6]=0
                emit(0x64D60,0x64D68);r[2]=65535;above=signed(r[6])>65535;t(above);branch(0x64D66,not above,0x64D6A)
                if above:emit(0x64D68);r[6]=r[2]
                emit(0x64D6A,0x64D70);r[14]=RAM_BASE+0x128C;control(0x64D6C,'jump',0x64E52,True);publish6();return
            emit(0x64D70,0x64D78);r[0]=0x33;r[0]=load(0x64D72,0x24A3,1,0);clear=(r[0]&64)==0
            t(clear);branch(0x64D76,clear,0x64D7C)
            if not clear:
                emit(0x64D78,0x64D7C);control(0x64D78,'jump',0x64FCE,True);publish2(True);return
            emit(0x64D7C,0x64D88);r[14]=RAM_BASE+0x128C;r[0]=0x5DA;r[6]=load(0x64D80,0x1866,2,6)&65535
            nonzero=r[6]!=0;t(not nonzero);branch(0x64D86,nonzero,0x64D8C)
            if not nonzero:
                emit(0x64D88,0x64D8C);control(0x64D88,'jump',0x64FD6,True);return
            emit(0x64D8C,0x64D98);r[5]=0x906C;r[2]=read(0x64D8E,0x906C,2);r[6]=(r[6]-r[2])&MASK
            positive=signed(r[6])>=0;t(positive);branch(0x64D96,positive,0x64E52)
            if not positive:
                emit(0x64D98,0x64D9C);r[6]=0;control(0x64D98,'jump',0x64E52,True)
            publish6();return
        emit(0x64D9C,0x64DA4);r[2]=0x8B38;r[0]=signed(read(0x64D9E,0x8B38,0,1),8)&MASK
        allowed=(r[0]&8)==0;t(allowed);branch(0x64DA2,allowed,0x64DA8)
        if not allowed:
            emit(0x64DA4,0x64DA8);control(0x64DA4,'jump',0x64FCE,True);publish2(True);return
        emit(0x64DA8,0x64DB6);r[4]=RAM_BASE+0x1082;r[5]=load(0x64DAA,0x1082,1,5)&255
        r[0]=load(0x64DAC,0x108A,1,0);r[2]=r[0]&255;above=r[5]>r[2];t(above);branch(0x64DB4,not above,0x64E00)
        if above:
            emit(0x64DB6,0x64DC4);r[14]=RAM_BASE+0x128C;r[2]=0;r[0]=0x5DA;put(0x64DBC,0x1866,2,2,0)
            r[0]=0x5DC;put(0x64DC2,0x1868,2,2,0);control(0x64DC0,'jump',0x64FD6,True);return
        emit(0x64E00,0x64E08);r[6]=RAM_BASE+0x246D;r[0]=load(0x64E02,0x246D,1,0)
        first=bool(r[0]&1);t(not first);branch(0x64E06,first,0x64E10);direct=False
        if not first:
            emit(0x64E08,0x64E10);r[6]=RAM_BASE+0x246A;r[0]=load(0x64E0A,0x246A,1,0)
            direct=bool(r[0]&1);t(not direct);branch(0x64E0E,direct,0x64E2C)
        if not direct:
            emit(0x64E10,0x64E18);r[6]=RAM_BASE+0x244C;r[0]=load(0x64E12,0x2454,1,0)
            first=bool(r[0]&32);t(not first);branch(0x64E16,first,0x64E1E)
            if not first:
                emit(0x64E18,0x64E1E);r[0]=load(0x64E18,0x2450,1,0);direct=bool(r[0]&32)
                t(not direct);branch(0x64E1C,direct,0x64E2C)
            if not direct:
                emit(0x64E1E,0x64E26);r[6]=RAM_BASE+0x244C;r[0]=load(0x64E20,0x2453,1,0)
                first=bool(r[0]&64);t(not first);branch(0x64E24,first,0x64E58)
                if not first:
                    emit(0x64E26,0x64E2C);r[0]=load(0x64E26,0x244F,1,0);direct=bool(r[0]&64)
                    t(not direct);branch(0x64E2A,not direct,0x64E58)
        if direct:
            emit(0x64E2C,0x64E34);r[3]=0x8B38;r[0]=signed(read(0x64E2E,0x8B3F,0,1),8)&MASK
            selected=bool(r[0]&16);t(not selected);branch(0x64E32,not selected,0x64E48)
            if selected:
                emit(0x64E34,0x64E3C);r[7]=0x8710;r[0]=signed(read(0x64E36,0x8710,0,1),8)&MASK
                selected=bool(r[0]&64);t(not selected);branch(0x64E3A,not selected,0x64E48)
            if selected:
                emit(0x64E3C,0x64E48);r[6]=RAM_BASE+0x28F8;r[0]=0xA7B;r[2]=load(0x64E40,0x3373,1,2)&255;r[2]<<=8
                control(0x64E44,'jump',0x64FD0,True);publish2();return
            emit(0x64E48,0x64E52);r[14]=RAM_BASE+0x128C;r[0]=0x5E7;r[2]=load(0x64E4C,0x1873,1,2);r[6]=(r[2]&255)<<8
            publish6();return
        emit(0x64E58,0x64E60);r[6]=RAM_BASE+0x246A;r[0]=load(0x64E5A,0x246A,1,0)
        ramp=bool(r[0]&1);t(not ramp);branch(0x64E5E,not ramp,0x64EE2)
        if ramp:
            emit(0x64E60,0x64E74);r[6]=RAM_BASE+0x28F8;r[0]=0xA7B;r[3]=0x8B38
            r[2]=load(0x64E66,0x3373,1,2);r[0]=signed(read(0x64E68,0x8B3F,0,1),8)&MASK
            r[6]=(r[2]&255)<<8;r[4]=r[6]&65535;selected=bool(r[0]&16);t(not selected)
            branch(0x64E70,not selected,0x64E82,True)
            if selected:
                emit(0x64E74,0x64E7C);r[7]=0x8710;r[0]=signed(read(0x64E76,0x8710,0,1),8)&MASK
                selected=bool(r[0]&64);t(not selected);branch(0x64E7A,not selected,0x64E82)
            if selected:
                emit(0x64E7C,0x64E82);r[14]=RAM_BASE+0x128C;control(0x64E7E,'jump',0x64EA4,True)
            else:
                emit(0x64E82,0x64E8E);r[14]=RAM_BASE+0x128C;r[0]=0x5DA;r[7]=load(0x64E86,0x1866,2,7);r[6]=r[7]&65535
                within=r[6]>=r[4];t(within);branch(0x64E8C,within,0x64E9E)
                if not within:
                    emit(0x64E8E,0x64E9C);r[0]=load(0x64E8E,0x13DE,2,0);r[2]=r[0]&65535;r[6]+=r[2];r[2]=65535
                    above=r[6]>r[2];t(above);branch(0x64E9A,not above,0x64E9E)
                    if above:emit(0x64E9C);r[6]=r[2]
                emit(0x64E9E,0x64EA2);above=r[6]>r[4];t(above);branch(0x64EA0,above,0x64EA4)
                if not above:emit(0x64EA2);r[4]=r[6]
            emit(0x64EA4,0x64EB2);r[0]=0x5DA;r[3]=RAM_BASE+0x1082;put(0x64EA8,0x1866,2,4,r[4])
            r[0]=load(0x64EAA,0x1083,1,0);r[2]=r[0]&255;above=r[2]>r[5];t(above);branch(0x64EB0,above,0x64EB6)
            if not above:
                emit(0x64EB2,0x64EB6);control(0x64EB2,'jump',0x64FD6,True);return
            emit(0x64EB6,0x64EBE);r[6]=RAM_BASE+0x244C;r[0]=load(0x64EB8,0x244F,1,0)
            blocked=bool(r[0]&1);t(not blocked);branch(0x64EBC,not blocked,0x64EC2)
            if blocked:
                emit(0x64EBE,0x64EC2);control(0x64EBE,'jump',0x64FD6,True);return
            emit(0x64EC2,0x64ED4);r[0]=0x4E4;r[2]=load(0x64EC4,0x1770,2,2);r[0]=0x4DE
            put(0x64EC8,0x176A,2,2,r[2]);r[0]=0x4E8;put(0x64ECC,0x1774,2,2,r[2]);r[0]=0x5DC
            put(0x64ED2,0x1868,2,4,r[4]);control(0x64ED0,'jump',0x64FD6,True);return
        emit(0x64EE2,0x64EF4);r[7]=RAM_BASE+0x2470;r[0]=0x33;r[4]=load(0x64EE6,0x24A3,1,4);r[0]=0x12
        r[0]=load(0x64EEA,0x2482,1,0);frame_access(0x64EEC,'write',stack+4,4,7,r[7])
        enabled=bool(r[0]&1);t(not enabled);frame_access(0x64EF2,'write',stack,1,4,r[4]);branch(0x64EF0,not enabled,0x64FBC,True)
        if enabled:
            emit(0x64EF4,0x64EFA);r[0]=load(0x64EF4,0x247C,1,0);enabled=bool(r[0]&1)
            t(not enabled);branch(0x64EF8,not enabled,0x64FBC)
        if enabled:
            emit(0x64EFA,0x64F02);r[6]=RAM_BASE+0x424C;r[0]=load(0x64EFC,0x4250,1,0)
            enabled=(r[0]&128)==0;t(enabled);branch(0x64F00,not enabled,0x64FBC)
        if not enabled:
            emit(0x64FBC,0x64FC8);r[14]=RAM_BASE+0x128C;r[2]=0;r[0]=0x5DA;put(0x64FC2,0x1866,2,2,0)
            r[0]=64;r[4]|=r[0]
        else:
            emit(0x64F02,0x64F0A);r[3]=0x8B38;r[0]=signed(read(0x64F04,0x8B3F,0,1),8)&MASK
            fraction_active=bool(r[0]&20);t(not fraction_active);branch(0x64F08,not fraction_active,0x64F96)
            if fraction_active:
                emit(0x64F0A,0x64F14);r[3]=RAM_BASE+0x1082;r[0]=load(0x64F0C,0x1083,1,0);r[6]=r[0]&255
                fraction_active=r[6]>r[5];t(fraction_active);branch(0x64F12,not fraction_active,0x64F96)
            if fraction_active:
                emit(0x64F14,0x64F20);r[14]=RAM_BASE+0x128C;r[0]=0x5DA;r[2]=load(0x64F18,0x1866,2,2);r[6]=r[2]&65535
                fraction_active=r[6]>0;t(fraction_active);branch(0x64F1E,not fraction_active,0x64F96)
            if fraction_active:
                emit(0x64F20,0x64F2A);r[0]=0x5DC;r[2]=load(0x64F22,0x1868,2,2);r[6]=r[2]&65535
                fraction_active=r[6]>0;t(fraction_active);branch(0x64F28,not fraction_active,0x64F96)
            store=True
            if fraction_active:
                emit(0x64F2A,0x64F3A);r[0]=0x4E8;r[2]=load(0x64F2C,0x1774,2,2);r[0]=0x4E4;r[6]=r[2]&65535
                r[5]=load(0x64F32,0x1770,2,5)&65535;above=r[6]>r[5];t(above);branch(0x64F38,not above,0x64F3E)
                if above:
                    emit(0x64F3A,0x64F3E);r[6]=r[5];control(0x64F3A,'jump',0x64F42,True)
                else:
                    emit(0x64F3E,0x64F42);r[0]=0x4E8;r[6]=load(0x64F40,0x1774,2,6)
                emit(0x64F42,0x64F62);r[0]=0x4E8;r[5]=r[6]&65535;put(0x64F46,0x1774,2,5,r[5]);r[0]=0x4E6
                r[2]=load(0x64F4A,0x1772,2,2);r[0]=0x4DE;r[4]=r[2]&65535;r[2]=0x9456
                r[6]=signed(read(0x64F52,0x9456,6),16)&MASK;r[2]=r[6]&65535;r[6]=r[4]+r[2]
                r[2]=load(0x64F5A,0x176A,2,2);r[4]=r[2]&65535;positive=r[4]>r[6];t(positive);branch(0x64F60,not positive,0x64F92)
                if positive:
                    emit(0x64F62,0x64F66);positive=r[5]>r[6];t(positive);branch(0x64F64,not positive,0x64F92)
                if positive:
                    emit(0x64F66,0x64F84);r[0]=0x5DC;r[2]=(r[5]-r[6])&MASK;r[4]=load(0x64F6C,0x1868,2,4)
                    r[0]=0x4DE;r[5]=r[4]&65535;macl=(r[5]*r[2])&MASK;r[5]=load(0x64F74,0x176A,2,5)
                    r[1]=macl;r[4]=r[5]&65535;r[5]=r[4]-r[6];r[6]=0x21CE0;r[0]=r[5]
                    row=call(0x64F80,0x21CE0);unsigned_divider(row)
                    emit(0x64F84,0x64F8E);r[2]=65535;above=r[0]>65535;t(above);r[6]=r[0];branch(0x64F8A,above,0x64FAE,True)
                    if not above:
                        emit(0x64F8E,0x64F92);r[2]=r[6];control(0x64F8E,'jump',0x64FAE,True)
                else:
                    emit(0x64F92,0x64F96);r[2]=0;control(0x64F92,'jump',0x64FAE,True)
            else:
                emit(0x64F96,0x64FA2);r[14]=RAM_BASE+0x128C;r[0]=0x5DA;r[6]=load(0x64F9A,0x1866,2,6);r[2]=r[6]&65535
                store=r[2]!=0;t(not store);branch(0x64FA0,not store,0x64FB2)
                if store:
                    emit(0x64FA2,0x64FAC);r[0]=load(0x64FA2,0x13DC,2,0);r[6]=r[0]&65535;r[2]=(r[2]-r[6])&MASK
                    positive=signed(r[2])>=0;t(positive);branch(0x64FAA,positive,0x64FAE)
                    if not positive:emit(0x64FAC);r[2]=0
            if store:
                emit(0x64FAE,0x64FB2);r[0]=0x5DA;put(0x64FB0,0x1866,2,2,r[2])
            emit(0x64FB2,0x64FBC);r[0]=signed(frame_access(0x64FB2,'read',stack,1,0),8)&MASK
            r[7]=frame_access(0x64FB4,'read',stack+4,4,7);r[0]&=0xBF;r[4]=r[0];control(0x64FB8,'jump',0x64FC8,True)
        emit(0x64FC8,0x64FCE);r[0]=0x33;put(0x64FCC,0x24A3,1,4,r[4]);control(0x64FCA,'jump',0x64FD6,True)

    def byte_caller():
        nonlocal stack,macl,pr
        def publish():
            emit(0xBDEC8,0xBDECC);r[5]=RAM_BASE+0x2324;put(0xBDECA,0x2326,1,0,r[0])
        emit(0xBDC66,0xBDC78);push(0xBDC66,r[13],13);push(0xBDC68,r[14],14);push(0xBDC6A,pr);push(0xBDC6C,macl)
        stack-=12;r[6]=0x8B34;r[0]=signed(read(0xBDC72,0x8B34,0,1),8)&MASK
        special=bool(r[0]&16);t(not special);branch(0xBDC76,not special,0xBDCDA)
        if special:
            emit(0xBDC78,0xBDC80);r[6]=0x8B42;r[0]=signed(read(0xBDC7A,0x8B42,0,1),8)&MASK
            special=bool(r[0]&2);t(not special);branch(0xBDC7E,not special,0xBDCDA)
        if special:
            emit(0xBDC80,0xBDC84);alternate=bool(r[0]&1);t(not alternate);branch(0xBDC82,alternate,0xBDCC4)
            if not alternate:
                emit(0xBDC84,0xBDC8E);r[6]=RAM_BASE+0x1094;r[0]=0x50;r[0]=load(0xBDC88,0x10E4,1,0)
                active=bool(r[0]&8);t(not active);branch(0xBDC8C,active,0xBDC92)
                if not active:
                    emit(0xBDC8E,0xBDC92);control(0xBDC8E,'jump',0xBDECC,True);return
                emit(0xBDC92,0xBDC9E);r[2]=RAM_BASE+0x1000;r[6]=load(0xBDC94,0x1000,2,6)&65535
                t(True);r[2]=r[6];branch(0xBDC9A,True,0xBDCA0,True)
                emit(0xBDCA0,0xBDCAC);t(bool(r[2]&1));r[2]>>=1;r[5]=MASK;t(bool(r[2]&1));r[2]>>=1;r[5]=255
                above=r[2]>255;t(above);branch(0xBDCAA,not above,0xBDCB0)
                if above:
                    emit(0xBDCAC,0xBDCB0);r[2]=r[5];control(0xBDCAC,'jump',0xBDCBC,True)
                else:
                    emit(0xBDCB0,0xBDCB6);t(True);r[2]=r[6];branch(0xBDCB2,True,0xBDCB8,True)
                    emit(0xBDCB8,0xBDCBC);t(bool(r[2]&1));r[2]>>=1;t(bool(r[2]&1));r[2]>>=1
                emit(0xBDCBC,0xBDCC4);r[5]=RAM_BASE+0x2324;r[0]=r[2];put(0xBDCC2,0x2326,1,0,r[0])
                control(0xBDCC0,'jump',0xBDECC,True);return
            emit(0xBDCC4,0xBDCCC);r[2]=0x86F9;r[0]=signed(read(0xBDCC6,0x86F9,0,1),8)&MASK
            selected=bool(r[0]&2);t(not selected);branch(0xBDCCA,not selected,0xBDCD2)
            if selected:
                emit(0xBDCCC,0xBDCD2);r[6]=0x851D;r[0]=signed(read(0xBDCD0,0x851D,0,1),8)&MASK
                control(0xBDCCE,'jump',0xBDEC8,True)
            else:
                emit(0xBDCD2,0xBDCDA);r[6]=RAM_BASE+0x4558;r[0]=0x1032;r[0]=load(0xBDCD8,0x558A,1,0)
                control(0xBDCD6,'jump',0xBDEC8,True)
            publish();return
        emit(0xBDCDA,0xBDCE2);r[6]=RAM_BASE+0x2468;r[0]=load(0xBDCDC,0x246B,1,0)
        active=bool(r[0]&64);t(not active);branch(0xBDCE0,active,0xBDD80)
        if not active:
            emit(0xBDCE2,0xBDCEC);r[6]=RAM_BASE+0x2468;r[0]=0x23;r[0]=load(0xBDCE6,0x248B,1,0)
            second=bool(r[0]&2);t(not second);branch(0xBDCEA,not second,0xBDCF6)
            if second:
                emit(0xBDCEC,0xBDCF6);r[6]=RAM_BASE+0x41A9;r[0]=0x51;r[0]=load(0xBDCF0,0x41FA,1,0)
                active=bool(r[0]&1);t(not active);branch(0xBDCF4,active,0xBDD80)
            if not active:
                emit(0xBDCF6,0xBDCFA);r[0]=0xFFFFFF80;control(0xBDCF6,'jump',0xBDEC8,True);publish();return
        emit(0xBDD80,0xBDD8E);r[14]=0x8D2D;r[0]=signed(read(0xBDD82,0x8D2E,0,1),8)&MASK
        r[2]=signed(read(0xBDD84,0x8D2D,2,1),8)&MASK;r[5]=r[0]&255;r[4]=r[2]&255
        nonsorted=r[5]>=r[4];t(nonsorted);branch(0xBDD8C,nonsorted,0xBDDE4)
        interpolate=False;use_first=False
        if not nonsorted:
            emit(0xBDD8E,0xBDD9C);r[2]=RAM_BASE+0x1068;r[0]=load(0xBDD90,0x1071,1,0)
            r[2]=signed(read(0xBDD92,0x8D2D,2,1),8)&MASK;r[4]=r[0]&255;r[7]=r[2]&255
            use_first=r[4]>r[7];t(use_first);branch(0xBDD9A,use_first,0xBDDEE)
            if not use_first:
                emit(0xBDD9C,0xBDDA0);interpolate=r[4]>r[5];t(interpolate);branch(0xBDD9E,not interpolate,0xBDDF6)
        else:
            emit(0xBDDE4,0xBDDEE);r[6]=RAM_BASE+0x1068;r[0]=load(0xBDDE6,0x1071,1,0);r[2]=r[0]&255
            use_first=r[2]>r[5];t(use_first);branch(0xBDDEC,not use_first,0xBDDF6)
        if interpolate:
            emit(0xBDDA0,0xBDDCE);r[13]=RAM_BASE+0x128C;r[0]=0x9D0;r[6]=load(0xBDDA4,0x1C5C,1,6)
            r[0]=0x9D2;r[6]&=255;r[7]=load(0xBDDAA,0x1C5E,1,7);r[1]=signed(r[7]&255,8)&MASK;r[2]=r[7]&255
            r[7]=r[5];frame_access(0xBDDB2,'write',stack+4,4,2,r[2]);r[3]=r[1]&255
            frame_access(0xBDDB6,'write',stack+8,4,3,r[3]);r[4]-=r[5];r[3]=r[2]
            r[2]=signed(read(0xBDDBC,0x8D2D,2,1),8)&MASK;r[6]=(r[6]-r[3])&MASK;macl=(r[6]*r[4])&MASK
            r[0]=(r[2]&255)-r[5];r[5]=0x21BBC;r[6]=macl;r[1]=r[6]
            row=call(0xBDDCA,0x21BBC);signed_divider(row)
            emit(0xBDDCE,0xBDDDC);r[6]=frame_access(0xBDDCE,'read',stack+8,4,6);r[0]=(r[0]+r[6])&MASK;r[2]=r[0];r[5]=255
            # The admitted bracket has low<coordinate<=high and two unsigned
            # byte endpoints. Truncation toward zero keeps the convex sum in0..255.
            above=signed(r[2])>255;t(above);branch(0xBDDDA,above,0xBDDDE)
            if not above:emit(0xBDDDC);r[5]=r[2]
            emit(0xBDDDE,0xBDDE4);r[2]=r[5];frame_access(0xBDDE2,'write',stack,4,5,r[5])
            control(0xBDDE0,'jump',0xBDE00,True)
        else:
            if use_first:
                emit(0xBDDEE,0xBDDF6);r[13]=RAM_BASE+0x128C;r[0]=0x9D0;r[2]=load(0xBDDF4,0x1C5C,1,2)
                control(0xBDDF2,'jump',0xBDDFC,True)
            else:
                emit(0xBDDF6,0xBDDFC);r[13]=RAM_BASE+0x128C;r[0]=0x9D2;r[2]=load(0xBDDFA,0x1C5E,1,2)
            emit(0xBDDFC,0xBDE00);r[2]&=255;frame_access(0xBDDFE,'write',stack,4,2,r[2])
        emit(0xBDE00,0xBDE0E);r[0]=0x962;r[5]=RAM_BASE+0x2468;put(0xBDE04,0x1BEE,1,2,r[2]);r[0]=0x3F
        r[0]=load(0xBDE08,0x24A7,1,0);gate=bool(r[0]&2);t(not gate);branch(0xBDE0C,not gate,0xBDE9C)
        if gate:
            emit(0xBDE0E,0xBDE1E);r[5]=RAM_BASE+0x2324;r[0]=load(0xBDE10,0x2326,1,0);r[4]=r[0]&255;r[0]=0x2C7
            r[5]=load(0xBDE16,0x1553,1,5)&255;gate=r[4]<r[5];t(not gate);branch(0xBDE1C,not gate,0xBDE9A)
            if gate:
                emit(0xBDE1E,0xBDE28);r[6]=RAM_BASE+0x2468;r[0]=0x13;r[0]=load(0xBDE22,0x247B,1,0)
                gate=bool(r[0]&2);t(not gate);branch(0xBDE26,not gate,0xBDE9A)
            if gate:
                emit(0xBDE28,0xBDE30);r[0]=0x792;r[2]=load(0xBDE2A,0x1A1E,1,2)
                gate=r[2]!=0;t(not gate);branch(0xBDE2E,not gate,0xBDE9A)
            if not gate:
                emit(0xBDE9A);frame_access(0xBDE9A,'write',stack,4,5,r[5])
            else:
                emit(0xBDE30,0xBDE3C);r[7]=RAM_BASE+0x256A;r[0]=132;r[2]=load(0xBDE36,0x25EE,1,2)
                hold=r[2]!=0;t(not hold);branch(0xBDE3A,hold,0xBDE96)
                if hold:
                    emit(0xBDE96,0xBDE9A);frame_access(0xBDE98,'write',stack,4,4,r[4]);control(0xBDE96,'jump',0xBDE9C,True)
                else:
                    emit(0xBDE3C,0xBDE4A);r[2]=r[4]+1;frame_access(0xBDE40,'write',stack,4,2,r[2]);r[2]=0x8616
                    r[0]=signed(read(0xBDE44,0x8616,0,1),8)&MASK;first_curve=bool(r[0]&1)
                    t(not first_curve);branch(0xBDE48,not first_curve,0xBDE78)
                    if first_curve:
                        emit(0xBDE4A,0xBDE62);r[2]=RAM_BASE+0x267A;r[0]=248;r[6]=load(0xBDE50,0x2772,1,6)
                        r[0]=20;r[5]=(r[6]&255)*32;r[6]=0x21BBC;t(False);r[1]=r[5]
                        row=call(0xBDE5E,0x21BBC);signed_divider(row)
                        emit(0xBDE62,0xBDE6C);r[5]=255;r[4]=r[0]&65535;above=r[4]>255;t(above);branch(0xBDE6A,not above,0xBDE6E)
                        if above:emit(0xBDE6C);r[4]=r[5]
                        emit(0xBDE6E,0xBDE78);r[5]=r[4]&255;r[4]=0x12EFE;r[6]=0x26370;control(0xBDE74,'jump',0xBDE82,True)
                    else:
                        emit(0xBDE78,0xBDE82);r[3]=RAM_BASE+0x1068;r[4]=0x12F06;r[0]=load(0xBDE7C,0x106F,1,0)
                        r[6]=0x26370;r[5]=r[0]&255
                    emit(0xBDE82,0xBDE86);row=call(0xBDE82,0x26370);byte_curve(row)
                    emit(0xBDE86,0xBDE96);r[5]=r[0];r[0]=0x792;r[7]=RAM_BASE+0x256A
                    put(0xBDE8C,0x1A1E,1,5,r[5]);r[0]=132;put(0xBDE94,0x25EE,1,5,r[5]);control(0xBDE92,'jump',0xBDE9C,True)
        emit(0xBDE9C,0xBDEA6);r[5]=RAM_BASE+0x41A9;r[0]=0x51;r[0]=load(0xBDEA0,0x41FA,1,0)
        offset=bool(r[0]&1);t(not offset);branch(0xBDEA4,not offset,0xBDEC6)
        if offset:
            emit(0xBDEA6,0xBDEB8);r[0]=0x478;r[5]=255;r[2]=frame_access(0xBDEAA,'read',stack,4,2)
            r[4]=load(0xBDEAE,0x1704,1,4);r[6]=(r[2]+r[4])&MASK
            above=signed(r[6])>255;t(above);branch(0xBDEB6,above,0xBDEBC)
            if not above:emit(0xBDEB8,0xBDEBC);r[2]=(r[2]+r[4])&MASK;r[5]=r[2]
            emit(0xBDEBC,0xBDEC2);positive=signed(r[5])>=0;t(positive);r[2]=r[5];branch(0xBDEBE,positive,0xBDEC4,True)
            if not positive:emit(0xBDEC2);r[2]=0
            emit(0xBDEC4);frame_access(0xBDEC4,'write',stack,4,2,r[2])
        emit(0xBDEC6);r[0]=frame_access(0xBDEC6,'read',stack,4,0);publish()

    if entry==0x64CB2:
        ratio_caller();emit(0x64FD6,0x64FE2);stack+=8;gbr=pop(0x64FD8);macl=pop(0x64FDA);pr=pop(0x64FDC);r[14]=pop(0x64FE0,14)
        control(0x64FDE,'return',pr,True)
        output=tuple(int.from_bytes(ram[at:at+2],'big') for at in (0x1866,0x1868,0x176A,0x1774))
    else:
        byte_caller();emit(0xBDECC,0xBDED8);stack+=12;macl=pop(0xBDECE);pr=pop(0xBDED0);r[14]=pop(0xBDED2,14);r[13]=pop(0xBDED6,13)
        control(0xBDED4,'return',pr,True)
        output=tuple(ram[at] for at in (0x2326,0x1BEE,0x1A1E,0x25EE))
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={index:value&MASK for index,value in enumerate(r) if value is not None},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=output)
