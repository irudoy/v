"""Separate guarded admission, wrapped products, signed quotient windows and exact saved carriers."""

from kb import division_callees_semantics as division

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry not in (0x532AE,0x74B68,0x75306)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the guarded quotient caller equations need complete exact CPU/RAM/frame inputs')
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

    def load(site,at,width,register):
        raw=bytes(ram[at:at+width]);event(site,'read',RAM_BASE+at,width,register,'ram',raw)
        value=int.from_bytes(raw,'big');return signed(value,width*8)&MASK if width<4 else value

    def put(site,at,width,register,value):
        ram[at:at+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')
        event(site,'write',RAM_BASE+at,width,register,'ram',bytes(ram[at:at+width]))

    def divide(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2]
        if not 0<=divisor<=0x7FFFFFFF:raise ValueError('the guarded callers lose the actual nonnegative signed divisor premise')
        saved_r2,saved_r3,saved_r4=r[2:5]
        emit(0x21BBC,0x21BC2);push(0x21BBC,saved_r2,2);t(divisor==0);branch(0x21BC0,divisor==0,0x21C70)
        if divisor==0:
            emit(0x21C70,0x21C7C);r[1]=RAM_BASE+0x9818;r[2]=0x44E;put(0x21C74,0x9818,4,2,r[2])
            r[0]=0;r[2]=pop(0x21C7A,2);terminal=0x21C78
            row.update(divisor=divisor,dividend=numerator,zero=True,large_divisor=False,long_path=False)
        else:
            negative=bool(numerator&0x80000000);large=divisor>65535;long_path=not large and abs(signed(numerator))>=divisor*256
            emit(0x21BC2,0x21BCC);push(0x21BC2,saved_r3,3);t(True);branch(0x21BCA,True,0x21BD0)
            emit(0x21BD0,0x21BD4);positive=signed(numerator)>0;t(positive);branch(0x21BD2,positive,0x21BD8)
            if not positive:emit(0x21BD4,0x21BD8)
            emit(0x21BD8,0x21BDE);branch(0x21BDC,large,0x21C7C)
            if large:
                emit(0x21C7C,0x21CCC);branch(0x21CCA,not negative,0x21CD0)
                if negative:emit(0x21CCC,0x21CD0)
                emit(0x21CD0,0x21CD6);pop(0x21CD0,3);pop(0x21CD4,2);terminal=0x21CD2
            else:
                emit(0x21BDE,0x21BE6);branch(0x21BE4,long_path,0x21C08)
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
            row.update(divisor=divisor,dividend=numerator,zero=False,large_divisor=large,long_path=long_path)
        control(terminal,'return',pr,True);returned(row,terminal)

    def extract14(value):
        # Two shifts, the self-borrow word and rotation retain the exact
        # signed carrier used by XTRCT rather than a widened ideal product.
        first=(value<<1)&MASK;carry=value>>31
        borrow_word=MASK if carry else 0
        second=(first<<1)&MASK;carry=first>>31
        rotated=((borrow_word<<1)|carry)&MASK;t(borrow_word>>31)
        return ((second>>16)|(rotated<<16))&MASK,rotated

    if entry==0x532AE:
        emit(0x532AE,0x532DA)
        for at,index in ((0x532AE,11),(0x532B0,12),(0x532B2,13),(0x532B4,14)):push(at,r[index],index)
        push(0x532B6,pr);push(0x532B8,macl);push(0x532BA,gbr);gbr=r[0]=RAM_BASE+0x128C;stack-=12
        r[2]=RAM_BASE+0x22F8;r[0]=22;r[12]=RAM_BASE+0x2470;r[5]=load(0x532C8,0x230E,1,5)
        r[0]=21;r[13]=load(0x532CC,0x2485,1,13);r[0]=r[13]&16;r[2]=r[0];r[0]=r[5]
        good=(r[0]&1)==0;t(good);branch(0x532D8,good,0x532DE)
        def admission(good):
            if not good:emit(0x532DA,0x532DE);control(0x532DA,'jump',0x533FC,True);return False
            emit(0x532DE,0x532E2);good=r[2]==0;t(good);branch(0x532E0,good,0x532E6)
            if not good:emit(0x532E2,0x532E6);control(0x532E2,'jump',0x533FC,True);return False
            emit(0x532E6,0x532F2);r[11]=RAM_BASE+0x128C;r[0]=0x38E;r[4]=load(0x532EA,0x161A,1,4);r[0]=r[4]
            clear=(r[0]&1)==0;t(clear);branch(0x532F0,clear,0x53304)
            if not clear:
                emit(0x532F2,0x53300);r[7]=RAM_BASE+0x22DC;r[0]=load(0x532F4,0x22E8,2,0)
                r[7]=16384;r[6]=r[0]&65535;above=r[6]>16384;t(above);branch(0x532FE,not above,0x53304)
                if above:emit(0x53300,0x53304);control(0x53300,'jump',0x533FC,True);return False
            emit(0x53304,0x5330A);r[0]=r[5];clear=(r[0]&2)==0;t(clear);branch(0x53308,not clear,0x533FC)
            if not clear:return False
            emit(0x5330A,0x53310);r[0]=r[4];clear=(r[0]&2)==0;t(clear);branch(0x5330E,clear,0x5331E)
            if not clear:
                emit(0x53310,0x5331E);r[7]=RAM_BASE+0x22DC;r[5]=16384;r[0]=load(0x53316,0x22E8,2,0)
                r[6]=r[0]&65535;above=r[6]>16384;t(above);branch(0x5331C,above,0x533FC)
                if above:return False
            return True
        main=admission(good)
        if main:
            emit(0x5331E,0x53324);r[0]=r[4];clear=(r[0]&1)==0;t(clear);branch(0x53322,clear,0x53342)
            subtract=False
            if not clear:
                emit(0x53324,0x5332A);r[0]=r[4];clear=(r[0]&2)==0;t(clear);branch(0x53328,clear,0x53342);subtract=not clear
            if subtract:
                emit(0x5332A,0x5333C);r[5]=0x9092;r[0]=load(0x5332C,0x1426,2,0)
                r[2]=signed(read(0x5332E,0x9092,2),16)&MASK;r[6]=r[0]&65535;r[2]&=65535
                r[6]=(r[6]-r[2])&MASK;nonnegative=signed(r[6])>=0;t(nonnegative);r[2]=r[6];branch(0x53338,nonnegative,0x5333E,True)
                if not nonnegative:emit(0x5333C);r[2]=0
                emit(0x5333E,0x53342);r[0]=r[2];put(0x53340,0x1426,2,0,r[0])
            emit(0x53342,0x5335E);r[0]=0x342;r[1]=0x7FFFFFFF;r[6]=load(0x53346,0x15CE,2,6)
            r[0]=load(0x53348,0x1426,2,0);r[2]=r[6]&65535;r[4]=r[0]&65535;r[0]=0x372;r[5]=r[4]
            r[6]=load(0x53352,0x15FE,2,6);r[0]=r[4];r[6]=(r[6]+r[2])&MASK;r[2]=0x21BBC
            frame_access(0x5335C,'write',stack,4,6,r[6]);row=call(0x5335A,0x21BBC);divide(row)
            emit(0x5335E,0x53364);r[6]=frame_access(0x5335E,'read',stack,4,6)
            above=signed(r[6])>signed(r[0]);t(above);branch(0x53362,not above,0x53390)
            multiply_first=False
            if above:
                emit(0x53364,0x5336C);r[0]=load(0x53364,0x1426,2,0);r[4]=r[0]&65535
                zero=r[4]==0;t(zero);branch(0x5336A,zero,0x53390);multiply_first=not zero
            if multiply_first:
                emit(0x5336C,0x5337C);r[0]=0x342;r[6]=load(0x5336E,0x15CE,2,6);r[0]=0x372;r[2]=r[6]&65535
                r[6]=load(0x53374,0x15FE,2,6);r[6]=(r[6]+r[2])&MASK;positive=signed(r[6])>=0;t(positive);branch(0x5337A,positive,0x53380)
                if not positive:emit(0x5337C,0x53380);r[2]=16383;r[6]=(r[6]+r[2])&MASK
                emit(0x53380,0x53390);r[6],r[2]=extract14(r[6]);macl=(r[6]*r[4])&MASK;r[2]=macl
                control(0x5338C,'jump',0x5349A,True)
            else:
                emit(0x53390,0x533A8);r[0]=load(0x53390,0x1426,2,0);r[4]=r[0]&65535;r[0]=0x342
                r[6]=load(0x53396,0x15CE,2,6);r[0]=0x372;r[6]&=65535;r[2]=load(0x5339C,0x15FE,2,2)
                r[2]=(r[2]+r[6])&MASK;macl=(r[4]*r[2])&MASK;r[6]=macl
                positive=signed(r[6])>=0;t(positive);branch(0x533A6,positive,0x533AC)
                if not positive:emit(0x533A8,0x533AC);r[2]=16383;r[6]=(r[6]+r[2])&MASK
                emit(0x533AC,0x533BA);r[6],r[2]=extract14(r[6]);r[2]=r[6];control(0x533B6,'jump',0x5349A,True)
        else:
            emit(0x533FC,0x53400);nonzero=r[2]!=0;t(not nonzero);branch(0x533FE,nonzero,0x53498)
            if not nonzero:
                emit(0x53400,0x53448);r[11]=RAM_BASE+0x128C;r[0]=0x375;r[5]=load(0x53404,0x1601,1,5)
                r[0]=0x353;r[5]&=255;r[4]=load(0x5340A,0x15DF,1,4);r[6]=r[5];r[0]=0x3D4;r[4]&=255
                r[2]=load(0x53412,0x1660,1,2);r[0]=0x3F4;t(r[2]>>31);r[2]=(r[2]<<1)&MASK;r[6]=(r[6]-r[2])&MASK
                macl=(r[6]*r[4])&MASK;r[4]=load(0x5341C,0x1680,1,4);r[0]=0x6B1;r[4]&=255;r[6]=RAM_BASE+0x28F8
                r[2]=load(0x53424,0x193D,1,2);r[14]=macl;r[2]&=255;r[0]=0x6F8;macl=r[4]*r[2]
                r[7]=load(0x5342E,0x2FF0,2,7);r[6]=(r[5]<<8)&MASK;r[2]=macl;r[7]&=65535
                r[6]=(r[6]-r[14])&MASK;r[2]=(r[2]+r[7])&MASK;t(r[2]>>31);r[2]=(r[2]<<1)&MASK
                r[6]=(r[6]+r[2])&MASK;positive=signed(r[6])>0;t(positive);r[2]=r[6]
                frame_access(0x53446,'write',stack+4,4,6,r[6]);branch(0x53444,positive,0x5344C,True)
                if not positive:emit(0x53448,0x5344C);r[2]=0;control(0x53448,'jump',0x5348C,True)
                else:
                    emit(0x5344C,0x5345C);r[0]=load(0x5344C,0x1426,2,0);r[6]=0x21BBC;r[5]=r[0]&65535;r[0]=r[2]
                    frame_access(0x53454,'write',stack+8,4,5,r[5]);r[5]=r[1]=0x3FC00000
                    row=call(0x53458,0x21BBC);divide(row)
                    emit(0x5345C,0x53462);r[2]=frame_access(0x5345C,'read',stack+8,4,2)
                    above=signed(r[2])>signed(r[0]);t(above);branch(0x53460,not above,0x53466)
                    if above:emit(0x53462,0x53466);r[2]=MASK;control(0x53462,'jump',0x5348C,True)
                    else:
                        emit(0x53466,0x53474);r[0]=load(0x53466,0x1426,2,0);r[2]=frame_access(0x53468,'read',stack+4,4,2)
                        r[5]=r[0]&65535;macl=(r[5]*r[2])&MASK;r[6]=macl;positive=signed(r[6])>=0;t(positive);branch(0x53472,positive,0x53478)
                        if not positive:emit(0x53474,0x53478);r[2]=0x3FFFFF;r[6]=(r[6]+r[2])&MASK
                        emit(0x53478,0x5348A);r[2]=((r[6]<<16)|(r[6]>>16))&MASK;r[2]=signed(r[2]&65535,16)&MASK
                        r[2]=((r[2]<<2)&MASK)>>8;r[5]=MASK;r[6]=signed(r[2]&65535,16)&MASK;r[2]=255
                        above=signed(r[6])>255;t(above);branch(0x53488,above,0x5348C)
                        if not above:emit(0x5348A);r[2]=r[6]
                emit(0x5348C,0x53498);r[0]=0x374;put(0x5348E,0x1600,1,2,r[2]);r[0]=16;r[13]|=r[0]
                r[0]=21;put(0x53496,0x2485,1,13,r[13])
            emit(0x53498);r[2]=0
        emit(0x5349A,0x534AE);r[0]=r[2];output=r[0];stack+=12;gbr=pop(0x5349E);macl=pop(0x534A0);pr=pop(0x534A2)
        for at,index in ((0x534A4,14),(0x534A6,13),(0x534A8,12),(0x534AC,11)):r[index]=pop(at,index)
        control(0x534AA,'return',pr,True)
    elif entry==0x74B68:
        emit(0x74B68,0x74B7A);push(0x74B68,pr);push(0x74B6A,gbr);r[0]=gbr=RAM_BASE+0x23BC;stack-=4
        r[6]=RAM_BASE+0x417E;r[0]=load(0x74B74,0x417E,1,0);blocked=bool(r[0]&8);t(not blocked);branch(0x74B78,blocked,0x74BFA)
        if not blocked:
            emit(0x74B7A,0x74B80);r[0]=load(0x74B7A,0x249B,1,0);blocked=bool(r[0]&1);t(not blocked);branch(0x74B7E,blocked,0x74BFA)
        if not blocked:
            emit(0x74B80,0x74B86);r[0]=load(0x74B80,0x245F,1,0);blocked=bool(r[0]&128);t(not blocked);branch(0x74B84,blocked,0x74BFA)
        if blocked:emit(0x74BFA);r[0]=0
        else:
            emit(0x74B86,0x74B9A);r[6]=RAM_BASE+0x24CE;r[5]=RAM_BASE+0x128C;r[0]=load(0x74B8A,0x24D2,1,0)
            decrement=(r[0]&64)==0;t(decrement);r[0]=load(0x74B8E,0x2422,2,0);r[6]=r[0]&65535;r[0]=0x56C
            r[2]=load(0x74B94,0x17F8,2,2)&65535;branch(0x74B96,decrement,0x74BEC,True)
            if decrement:
                emit(0x74BEC,0x74BF4);r[6]=(r[6]-r[2])&MASK;positive=signed(r[6])>=0;t(positive);r[2]=r[6];branch(0x74BF0,positive,0x74BF6,True)
                if not positive:emit(0x74BF4);r[2]=0
            else:
                emit(0x74B9A,0x74BAE);r[6]=(r[6]+r[2])&MASK;r[2]=RAM_BASE+0x120E
                frame_access(0x74B9E,'write',stack,4,6,r[6]);r[0]=load(0x74BA0,0x1210,2,0);r[2]=0x914E;r[5]=r[0]&65535
                r[7]=read(0x74BA6,0x914E,7);above=r[5]>r[7];t(above);branch(0x74BAC,above,0x74BB2)
                if not above:emit(0x74BAE,0x74BB2);r[2]=0;control(0x74BAE,'jump',0x74BD4,True)
                else:
                    emit(0x74BB2,0x74BBC);r[3]=0x914E;r[0]=signed(read(0x74BB4,0x9150,0),16)&MASK;r[4]=r[0]&65535
                    above=r[5]>=r[4];t(above);branch(0x74BBA,not above,0x74BC2)
                    if above:emit(0x74BBC,0x74BC2);r[6]=MASK;r[2]=65535;control(0x74BBE,'jump',0x74BD4,True)
                    else:
                        emit(0x74BC2,0x74BD4);r[5]-=r[7];r[6]=0x21BBC;r[1]=(r[5]*65535)&MASK;r[4]-=r[7];r[0]=r[4]
                        row=call(0x74BCE,0x21BBC);divide(row);r[2]=r[0]
                emit(0x74BD4,0x74BDA);r[6]=frame_access(0x74BD4,'read',stack,4,6);above=r[6]>=r[2];t(above);branch(0x74BD8,above,0x74BDE)
                if above:emit(0x74BDE);r[6]=frame_access(0x74BDE,'read',stack,4,6)
                else:emit(0x74BDA,0x74BDE);r[6]=r[2];control(0x74BDA,'jump',0x74BE0,True)
                emit(0x74BE0,0x74BE8);r[2]=65535;above=signed(r[6])>65535;t(above);branch(0x74BE6,above,0x74BF6)
                if not above:emit(0x74BE8,0x74BEC);r[2]=r[6];control(0x74BE8,'jump',0x74BF6,True)
            emit(0x74BF6,0x74BFA);r[0]=r[2];control(0x74BF6,'jump',0x74BFC,True)
        emit(0x74BFC,0x74C08);put(0x74BFC,0x2422,2,0,r[0]);output=r[0]&65535;stack+=4;gbr=pop(0x74C00);pr=pop(0x74C02)
        control(0x74C04,'return',pr,True)
    else:
        emit(0x75306,0x75316);push(0x75306,pr);push(0x75308,macl);r[7]=RAM_BASE+0x128C;r[0]=0x716
        r[6]=load(0x7530E,0x19A2,2,6)&65535;zero=r[6]==0;t(zero);branch(0x75314,zero,0x7538A)
        if not zero:
            emit(0x75316,0x75320);r[2]=RAM_BASE+0x23BC;r[0]=0x40;r[5]=load(0x7531A,0x23FC,2,5)
            zero=r[5]==0;t(zero);branch(0x7531E,zero,0x7538A)
        if zero:emit(0x7538A);r[2]=0
        else:
            emit(0x75320,0x7533A);r[5]=0x944E;r[0]=0x666;r[2]=signed(read(0x75324,0x944E,2),16)&MASK
            r[5]=load(0x75326,0x18F2,2,5);r[0]=r[6];r[2]&=65535;r[4]=0x21BBC;macl=(r[5]*r[2])&MASK;r[1]=macl
            row=call(0x75330,0x21BBC);divide(row);positive=signed(r[0])>=0;t(positive);r[6]=r[0];branch(0x75336,not positive,0x7534E,True)
            if positive:
                emit(0x7533A,0x75340);r[2]=0x1FFFFFF;above=signed(r[6])>r[2];t(above);branch(0x7533E,not above,0x7535C)
                if above:emit(0x75340,0x75344);r[6]=r[2];control(0x75340,'jump',0x7535C,True)
            else:
                emit(0x7534E,0x75358);r[2]=0xFE000000;within=signed(r[6])>=-33554432;t(within);branch(0x75356,not within,0x7535A)
                if within:emit(0x75358);r[2]=r[6]
                emit(0x7535A);r[6]=r[2]
            emit(0x7535C,0x75370);r[3]=RAM_BASE+0x23BC;r[0]=0x40;r[1]=(r[6]*64)&MASK
            r[5]=load(0x75364,0x23FC,2,5);r[4]=0x21BBC;r[0]=r[5]&65535
            row=call(0x7536C,0x21BBC);divide(row)
            emit(0x75370,0x75378);r[6]=32767;above=signed(r[0])>32767;t(above);r[2]=r[0];branch(0x75374,above,0x7537A,True)
            if not above:emit(0x75378);r[6]=r[2]
            emit(0x7537A,0x75382);r[2]=0xFFFF8000;within=signed(r[6])>=-32768;t(within);branch(0x75380,not within,0x75384)
            if within:emit(0x75382);r[2]=r[6]
            emit(0x75384,0x7538A);r[7]=RAM_BASE+0x128C;control(0x75386,'jump',0x7538C,True)
        emit(0x7538C,0x75396);r[0]=0x748;macl=pop(0x7538E);pr=pop(0x75390);put(0x75394,0x19D4,2,2,r[2]);output=r[2]&65535
        control(0x75392,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:v&MASK for i,v in enumerate(r) if v is not None},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=output)
