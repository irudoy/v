"""Separate mixed curve/surface/caller arithmetic with complete real helper and saved-state obligations."""

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
    if (type(coordinate) is not int or not 0<=coordinate<=65535 or len(knots)!=8
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
    if (type(entry) is not int or entry not in (0x3B498,0x41DB6,0x4BDC2,0x659AE)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the mixed curve caller equations need complete exact CPU/RAM/frame inputs')
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

    def axis(target,width,row):
        nonlocal pr
        base,coordinate=r[0],r[5];maximum=7*width;r[3]=r[4]
        if r[4]!=maximum:raise ValueError('the word-axis wrapper changes its actual complete axis extent')
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
                emit(target+14,target+18);last=index==7;t(last);branch(target+16,last,target+0x38)
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

    def unsigned_divide(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2]
        if divisor!=500000:raise ValueError('the mixed caller changes its exact unsigned publication divisor')
        saved=r[2]
        emit(0x21CE0,0x21CEC);push(0x21CE0,saved,2)
        branch(0x21CE4,False,0x21D6A);branch(0x21CEA,True,0x21D76)
        emit(0x21D76,0x21DC6);r[2]=pop(0x21DC4,2);r[0]=numerator//divisor;r[1]=None
        sr&=~0x301;sr_mask&=~0x101
        row.update(divisor=divisor,dividend=numerator,zero=False,large_divisor=True)
        control(0x21DC2,'return',pr,True);returned(row,0x21DC2)

    def shift7(row):
        raw=r[0];emit(0x224F8,0x22508);r[0]=(signed(raw)>>7)&MASK;t(bool(raw&64))
        control(0x22504,'return',pr,True);returned(row,0x22504)

    def byte_curve(row):
        nonlocal pr
        base,axis_base,coordinate=r[4:7]
        emit(0x26474,0x26482);push(0x26474,pr);push(0x26476,r[4],4)
        r[0]=r[5];r[5]=coordinate&255;r[7]=0x26944;r[4]=7
        nested=call(0x2647E,0x26944);pos=axis(0x26944,1,nested)
        emit(0x26482,0x26496);r[6]=pop(0x26482,6)+r[4]
        r[0]=signed(read(0x26486,r[6]+1,0,1),8)&MASK;r[2]=r[0]&255;r[3]=r[5]
        r[1]=signed(read(0x2648C,r[6],1,1),8)&MASK;pr=pop(0x2648E);r[6]=0x26740;r[0]=r[1]&255
        control(0x26492,'jump',0x26740,True);value=interpolation(0x26740,row)
        lookups.append(dict(pos,kind='byte-curve',base=base,axis=axis_base,coordinate=coordinate&255,**value))
        return value

    def implicit_curve(row):
        base,coordinate=r[4],r[5]&65535
        if not 0<=coordinate<0xF000:raise ValueError('the actual mixed caller leaves its proved implicit coordinate range')
        emit(0x263F4,0x26402);r[0]=0xF000;r[5]=coordinate;t(False);branch(0x263FA,False,0x26402)
        r[6]=0x26A64;r[3]=0;control(0x263FE,'jump',0x26A64,True)
        emit(0x26A64,0x26A9C);index,low=divmod(coordinate,4096);r[5]=index;r[3]=low*16;r[0]=0xF0
        t(False);branch(0x26A9A,False,0x26AAA)
        emit(0x26A9C,0x26AAA);t(False);r[5]*=2;r[4]+=r[5]
        r[1]=signed(read(0x26AA0,r[4],1),16)&MASK;r[0]=signed(read(0x26AA2,r[4]+2,0),16)&MASK
        r[2]=r[0]&65535;r[0]=r[1]&65535;control(0x26AA6,'jump',0x26AB4,True)
        emit(0x26AB4,0x26ABA);r[6]=0x26740;control(0x26AB6,'jump',0x26740,True)
        value=interpolation(0x26740,row)
        lookups.append(dict(kind='implicit-word',base=base,coordinate=coordinate,index=index,**value))
        return value

    def surface_kernel(row):
        nonlocal pr,macl
        table,row_offset,row_fraction,column_offset,column_fraction,stride=r[4],r[0],r[1],r[2],r[3],r[5]
        if stride!=8:raise ValueError('the real mixed word surface loses its exact eight-word stride')
        emit(0x26848,0x26864);push(0x26848,r[8],8);push(0x2684A,pr)
        r[7]=macl;macl=(r[5]&65535)*(r[0]&65535);r[4]+=r[2];r[0]=macl;macl=r[7]
        t(False);r[5]*=2;r[4]+=r[0];r[5]+=r[4];r[8]=r[1];r[7]=0x26740
        has_column=r[3]!=0;t(not has_column);branch(0x26862,not has_column,0x2688A)
        if has_column:
            emit(0x26864,0x2686E);r[1]=signed(read(0x26864,r[4],1),16)&MASK
            r[0]=signed(read(0x26866,r[4]+2,0),16)&MASK;r[2]=r[0]&65535;r[0]=r[1]&65535
            nested=call(0x2686A,0x26740);interpolation(0x26740,nested)
            emit(0x2686E,0x26872);has_row=r[8]!=0;t(not has_row);branch(0x26870,not has_row,0x2689A)
            if has_row:
                emit(0x26872,0x2687E);push(0x26872,r[0],0);r[1]=signed(read(0x26874,r[5],1),16)&MASK
                r[0]=signed(read(0x26876,r[5]+2,0),16)&MASK;r[2]=r[0]&65535;r[0]=r[1]&65535
                nested=call(0x2687A,0x26740);interpolation(0x26740,nested)
                emit(0x2687E,0x26886);r[2]=r[0];r[0]=pop(0x26880,0);r[3]=r[8]
                nested=call(0x26882,0x26740);interpolation(0x26740,nested)
                emit(0x26886,0x2688A);control(0x26886,'jump',0x2689A,True)
        else:
            emit(0x2688A,0x26890);has_row=r[8]!=0;t(not has_row)
            r[0]=signed(read(0x2688E,r[4],0),16)&MASK;branch(0x2688C,not has_row,0x2689A,True)
            if has_row:
                emit(0x26890,0x2689A);r[2]=signed(read(0x26890,r[5],2),16)&MASK
                r[0]&=65535;r[2]&=65535;r[3]=r[8]
                nested=call(0x26896,0x26740);interpolation(0x26740,nested)
        emit(0x2689A,0x268A0);pr=pop(0x2689A);r[8]=pop(0x2689E,8)
        control(0x2689C,'return',pr,True);returned(row,0x2689C)
        value=dict(kind='word-surface',base=table,row=row_offset//2,column=column_offset//2,
            row_fraction=row_fraction,column_fraction=column_fraction,value=r[0])
        lookups.append(value);return value

    def word_surface(row):
        nonlocal pr
        base,outer_axis,inner_axis,outer_coordinate=r[4:8]
        emit(0x26270,0x26280);push(0x26270,pr);push(0x26272,r[4],4)
        r[7]&=65535;r[0]=r[5];r[5]=r[7];r[7]=0x26984;r[4]=14
        nested=call(0x2627C,0x26984);outer=axis(0x26984,2,nested)
        emit(0x26280,0x2628E);push(0x26280,r[4],4);push(0x26282,r[5],5)
        r[0]=r[6];carrier=frame_access(0x26286,'read',stack+16,4,5);r[5]=carrier&65535;r[4]=14
        nested=call(0x2628A,0x26984);inner=axis(0x26984,2,nested)
        emit(0x2628E,0x262A0);r[1]=pop(0x2628E,1);r[0]=pop(0x26290,0)
        r[2]=r[4];r[3]=r[5];r[4]=pop(0x26296,4);pr=pop(0x26298);r[7]=0x26848;r[5]=8
        control(0x2629C,'jump',0x26848,True);value=surface_kernel(row)
        value.update(outer_axis=outer_axis,inner_axis=inner_axis,outer_coordinate=outer_coordinate&65535,
            inner_coordinate=carrier&65535,complete_inner_argument_word=carrier)
        return value

    if entry==0x3B498:
        emit(0x3B498,0x3B4C4);push(0x3B498,r[14],14);push(0x3B49A,pr);push(0x3B49C,macl);push(0x3B49E,gbr)
        r[0]=gbr=RAM_BASE+0x1114;stack-=4;r[0]=load(0x3B4A6,0x1170,1,0);r[7]=65535;r[6]=RAM_BASE+0x1E60
        frame_access(0x3B4AE,'write',stack,1,0,r[0]);r[2]=load(0x3B4B0,0x1E60,2,2);r[0]=load(0x3B4B2,0x114E,2,0)
        r[14]=r[2]&65535;r[5]=r[0]&65535;macl=r[14]*r[5];r[4]=macl>>9;t(bool(macl&256))
        above=r[4]>=65535;t(above);branch(0x3B4C2,not above,0x3B4C8)
        if above:emit(0x3B4C4,0x3B4C8);r[4]=65535;control(0x3B4C4,'jump',0x3B4D8,True)
        else:
            emit(0x3B4C8,0x3B4D8);r[0]=load(0x3B4C8,0x120E,2,0);r[2]=r[0]&65535
            macl=(r[2]*r[5])&MASK;r[5]=macl>>11;t(bool(macl&1024));r[4]=(r[4]+r[5])&MASK
        emit(0x3B4D8,0x3B4DC);above=r[4]>65535;t(above);branch(0x3B4DA,not above,0x3B4DE)
        if above:emit(0x3B4DC);r[4]=65535
        emit(0x3B4DE,0x3B4EC);r[6]=RAM_BASE+0x1E60;r[0]=r[4]&65535;put(0x3B4E2,0x1E62,2,0,r[0])
        r[6]=15360;high=r[0]>=15360;t(high);branch(0x3B4EA,high,0x3B4F4)
        if high:emit(0x3B4F4,0x3B4FE);r[2]=15360;r[5]=r[0]-r[2];r[4]=0x15022
        else:emit(0x3B4EC,0x3B4F4);r[5]=r[0]*4;r[4]=0x15042;control(0x3B4F0,'jump',0x3B4FE,True)
        emit(0x3B4FE,0x3B504);r[2]=0x263F4;r[5]&=65535;row=call(0x3B500,0x263F4);implicit_curve(row)
        emit(0x3B504,0x3B514);r[0]&=65535;r[6]=signed(frame_access(0x3B506,'read',stack,1,6),8)&MASK
        r[0]>>=8;put(0x3B50A,0x1170,1,0,r[0]);r[0]&=255;r[6]&=255;r[0]=(r[0]-r[6])&MASK
        put(0x3B512,0x1138,2,0,r[0]);output=r[0]&65535
        emit(0x3B514,0x3B520);stack+=4;gbr=pop(0x3B516);macl=pop(0x3B518);pr=pop(0x3B51A);r[14]=pop(0x3B51E,14)
        control(0x3B51C,'return',pr,True)
    elif entry==0x41DB6:
        emit(0x41DB6,0x41DC6);push(0x41DB6,pr);push(0x41DB8,gbr);r[0]=gbr=RAM_BASE+0x22F8
        r[6]=RAM_BASE+0x2464;r[0]=load(0x41DC0,0x2465,1,0);enabled=bool(r[0]&64);t(not enabled);branch(0x41DC4,enabled,0x41DD0)
        if not enabled:
            emit(0x41DC6,0x41DCC);r[0]=load(0x41DC6,0x2468,1,0);enabled=bool(r[0]&4);t(not enabled);branch(0x41DCA,enabled,0x41DD0)
        if not enabled:emit(0x41DCC,0x41DD0);r[0]=0xFFFFFF80;control(0x41DCC,'jump',0x41E36,True)
        else:
            emit(0x41DD0,0x41DFE);r[2]=RAM_BASE+0x128C;r[0]=0x4C6;r[6]=load(0x41DD4,0x1752,2,6)
            r[0]=0x4D9;r[6]&=65535;r[5]=load(0x41DDA,0x1765,1,5);r[0]=0x4D7;r[5]&=255
            r[7]=load(0x41DE0,0x1763,1,7);r[5]*=4;r[2]=RAM_BASE+0x1E60;r[6]+=r[5]
            r[0]=0x102;r[7]&=255;r[6]+=r[7];r[4]=load(0x41DEE,0x1F62,1,4);r[0]=0x272;r[4]&=255;r[6]+=r[4]
            r[4]=RAM_BASE+0x1FF4;zero=r[6]==0;t(zero);r[5]=r[6];branch(0x41DFA,zero,0x41E2C,True)
            if zero:
                emit(0x41E2C,0x41E34);r[2]=load(0x41E2C,0x2266,2,2);positive=signed(r[2])>=0;t(positive);r[0]=MASK
                branch(0x41E30,positive,0x41E36,True)
                if not positive:emit(0x41E34);r[0]=0
            else:
                emit(0x41DFE,0x41E10);r[6]=load(0x41DFE,0x2266,2,6);r[0]=r[5];r[2]=0x21BBC
                t(bool(r[6]&0x80000000));r[6]=(r[6]<<7)&MASK;r[1]=r[6]
                row=call(0x41E0C,0x21BBC);divide(row)
                emit(0x41E10,0x41E1E);r[5]=255;r[0]=(r[0]+128)&MASK;above=signed(r[0])>255;t(above);r[2]=r[0]
                branch(0x41E1A,not above,0x41E22,True)
                if above:emit(0x41E1E,0x41E22);r[6]=MASK;r[2]=255
                emit(0x41E22,0x41E26);positive=signed(r[2])>=0;t(positive);branch(0x41E24,positive,0x41E28)
                if not positive:emit(0x41E26);r[2]=0
                emit(0x41E28,0x41E2C);r[0]=r[2];control(0x41E28,'jump',0x41E36,True)
        emit(0x41E36,0x41E40);put(0x41E36,0x2315,1,0,r[0]);output=r[0]&255;gbr=pop(0x41E38);pr=pop(0x41E3A)
        control(0x41E3C,'return',pr,True)
    elif entry==0x4BDC2:
        emit(0x4BDC2,0x4BDDC);push(0x4BDC2,r[13],13);push(0x4BDC4,r[14],14);push(0x4BDC6,pr)
        push(0x4BDC8,macl);push(0x4BDCA,gbr);r[0]=gbr=RAM_BASE+0x128C;stack-=4
        r[6]=RAM_BASE+0x2458;r[7]=RAM_BASE+0x23BC;r[0]=load(0x4BDD6,0x2458,1,0)
        mode=bool(r[0]&32);t(not mode);branch(0x4BDDA,mode,0x4BEAA)
        if not mode:
            emit(0x4BDDC,0x4BE1A);r[0]=load(0x4BDDC,0x23BD,1,0);r[13]=RAM_BASE+0x128C;r[6]=r[0]&255
            r[0]=load(0x4BDE2,0x23C5,1,0);r[5]=r[0]&255;r[0]=0x35;r[2]=load(0x4BDE8,0x23F1,1,2)
            r[0]=load(0x4BDEA,0x12DC,1,0);r[2]=(r[2]+r[6])&MASK;r[4]=r[0]&255;r[0]=0x35E
            r[2]=(r[2]-r[5])&MASK;r[5]=load(0x4BDF4,0x15EA,1,5);r[2]=(r[2]-64)&MASK;r[0]=0x7F1
            r[2]=(r[2]-r[4])&MASK;r[5]&=255;r[6]=load(0x4BDFE,0x1A7D,1,6);r[2]=(r[2]-r[5])&MASK
            r[5]=RAM_BASE+0x2898;r[0]=0x20;r[14]=r[6]&255;r[6]=load(0x4BE08,0x28B8,2,6)
            r[0]=0x22;r[14]=(r[14]+r[2])&MASK;r[2]=load(0x4BE0E,0x28BA,2,2);r[6]&=65535;r[2]&=65535
            above=r[6]>r[2];t(above);r[14]=(r[14]-64)&MASK;branch(0x4BE16,not above,0x4BE1C,True)
            if above:emit(0x4BE1A);r[6]=r[2]
            emit(0x4BE1C,0x4BE26);r[5]=r[6];r[6]=RAM_BASE+0x41A9;r[0]=load(0x4BE20,0x41AB,1,0)
            enabled=bool(r[0]&64);t(not enabled);branch(0x4BE24,not enabled,0x4BE98)
            admitted=enabled
            if enabled:
                emit(0x4BE26,0x4BE32);r[6]=0x9012;r[5]&=65535;r[2]=signed(read(0x4BE2A,0x9012,2),16)&MASK;r[2]&=65535
                admitted=r[5]>=r[2];t(admitted);branch(0x4BE30,not admitted,0x4BE98)
            if admitted:
                emit(0x4BE32,0x4BE40);r[6]=RAM_BASE+0x1068;r[4]=0x11F02;r[0]=load(0x4BE36,0x106F,1,0)
                r[5]=0x11EEA;r[2]=0x26474;r[6]=r[0]&255;row=call(0x4BE3C,0x26474);byte_curve(row)
                emit(0x4BE40,0x4BE5A);r[7]=RAM_BASE+0x1024;put(0x4BE42,0x134C,1,0,r[0]);r[0]=load(0x4BE44,0x1024,2,0)
                r[7]=RAM_BASE+0x1094;frame_access(0x4BE48,'write',stack+2,2,0,r[0]);r[0]=0x36;r[3]=load(0x4BE4C,0x10CA,2,3)
                r[4]=0xC50E;r[5]=0x1461A;r[6]=0x1464A;r[2]=0x26270;r[7]=r[3]&65535
                row=call(0x4BE56,0x26270);word_surface(row)
                emit(0x4BE5A,0x4BE64);r[5]=255;r[6]=r[0]&65535;above=r[6]>255;t(above);branch(0x4BE62,above,0x4BE66)
                if not above:emit(0x4BE64);r[5]=r[6]
                emit(0x4BE66,0x4BE84);r[0]=r[5];put(0x4BE68,0x1348,1,0,r[0]);r[0]=0x674;r[6]=r[5]&255
                r[2]=load(0x4BE6E,0x1900,2,2);r[0]=load(0x4BE70,0x134C,1,0);r[3]=r[2]&65535;r[2]=r[0]&255
                r[0]=500000;macl=r[3]*r[2];r[2]=macl;macl=(r[2]*r[6])&MASK;r[6]=0x21CE0;r[1]=macl
                row=call(0x4BE80,0x21CE0);unsigned_divide(row)
                emit(0x4BE84,0x4BE8E);r[2]=255;above=r[0]>255;t(above);r[6]=r[0];branch(0x4BE8A,not above,0x4BE90,True)
                if above:emit(0x4BE8E);r[6]=r[2]
                emit(0x4BE90,0x4BE98);r[0]=r[6];put(0x4BE92,0x134A,1,0,r[0]);r[2]=r[6];control(0x4BE94,'jump',0x4BE9C,True)
            else:emit(0x4BE98,0x4BE9C);r[2]=r[0]=0
            emit(0x4BE9C,0x4BEAA);r[6]=RAM_BASE+0x24CE;r[2]&=255;put(0x4BEA0,0x12D4,1,0,r[0]);r[14]=(r[14]+r[2])&MASK
            r[0]=load(0x4BEA4,0x24D1,1,0);r[0]&=0xDF;control(0x4BEA6,'jump',0x4BEC6,True)
        else:
            emit(0x4BEAA,0x4BEC6);r[0]=load(0x4BEAA,0x23C5,1,0);r[13]=RAM_BASE+0x128C;r[5]=r[0]&255
            r[0]=0x7F1;r[6]=RAM_BASE+0x24CE;r[2]=load(0x4BEB4,0x1A7D,1,2);r[0]=0x32;r[4]=load(0x4BEB8,0x23EE,1,4)
            r[14]=r[2]&255;r[0]=load(0x4BEBC,0x24D1,1,0);r[4]=(r[4]-r[5])&MASK;r[14]=(r[14]+r[4]-64)&MASK;r[0]|=32
        emit(0x4BEC6,0x4BED0);r[14]=signed(r[14]&65535,16)&MASK;r[2]=0xFFFFFF80
        within=signed(r[14])>=-128;t(within);put(0x4BECE,0x24D1,1,0,r[0]);branch(0x4BECC,within,0x4BED4,True)
        if within:emit(0x4BED4);r[6]=signed(r[14]&65535,16)&MASK
        else:emit(0x4BED0,0x4BED4);r[6]=0xFFFFFF80;control(0x4BED0,'jump',0x4BED6,True)
        emit(0x4BED6,0x4BEDE);r[2]=signed(r[6]&65535,16)&MASK;r[6]=127;above=signed(r[2])>127;t(above);branch(0x4BEDC,not above,0x4BEE0)
        if above:emit(0x4BEDE);r[2]=127
        emit(0x4BEE0,0x4BEF2);r[0]=0x5A4;put(0x4BEE2,0x1830,1,2,r[2]);output=r[2]&255
        stack+=4;gbr=pop(0x4BEE6);macl=pop(0x4BEE8);pr=pop(0x4BEEA);r[14]=pop(0x4BEEC,14);r[13]=pop(0x4BEF0,13)
        control(0x4BEEE,'return',pr,True)
    else:
        emit(0x659AE,0x659D2);push(0x659AE,r[14],14);push(0x659B0,pr);push(0x659B2,macl);stack-=4
        r[14]=RAM_BASE+0x128C;r[0]=0x658;r[5]=0x87EE;r[2]=load(0x659BC,0x18E4,2,2)
        r[6]=signed(read(0x659BE,0x87EE,6,1),8)&MASK;r[5]=0xFFFFC000;r[2]=((r[2]&65535)+r[5])&MASK;r[6]&=255
        macl=(r[2]*r[6])&MASK;r[2]=macl;positive=signed(r[2])>=0;t(positive);branch(0x659D0,positive,0x659D4)
        if not positive:emit(0x659D2);r[2]=(r[2]+127)&MASK
        emit(0x659D4,0x659DA);r[6]=0x224F8;r[0]=r[2];row=call(0x659D6,0x224F8);shift7(row)
        emit(0x659DA,0x659E6);r[2]=16384;r[0]=(r[0]+16384)&MASK;above=signed(r[0])>16384;t(above);r[5]=r[0]
        branch(0x659E2,not above,0x659E8,True)
        if above:emit(0x659E6);r[5]=16384
        emit(0x659E8,0x659FE);r[6]=RAM_BASE+0x23BC;r[0]=0x4C;r[2]=load(0x659EC,0x2408,2,2)
        r[0]=0x63E;r[2]&=65535;r[6]=load(0x659F2,0x18CA,2,6);r[6]=(r[6]+r[2])&MASK
        macl=(r[6]*r[5])&MASK;r[7]=macl;positive=signed(r[7])>=0;t(positive);branch(0x659FC,positive,0x65A02)
        if not positive:emit(0x659FE,0x65A02);r[2]=16383;r[7]=(r[7]+r[2])&MASK
        emit(0x65A02,0x65A1C);r[0]=0x35F;r[5]=load(0x65A08,0x15EB,1,5);r[7],r[2]=extract14(r[7]);r[5]&=255;r[6]=128
        above=r[5]>128;t(above);frame_access(0x65A1A,'write',stack,4,7,r[7]);branch(0x65A18,not above,0x65A54,True)
        admitted=above
        if above:
            emit(0x65A1C,0x65A26);r[6]=RAM_BASE+0x2470;r[0]=21;r[0]=load(0x65A20,0x2485,1,0)
            admitted=(r[0]&32)==0;t(admitted);branch(0x65A24,not admitted,0x65A54)
        if admitted:
            emit(0x65A26,0x65A3E);r[6]=RAM_BASE+0x22DC;r[5]=signed(r[5]&65535,16)&MASK
            r[0]=load(0x65A2A,0x22E8,2,0);raw=r[0]&65535;r[6]=raw>>7;t(bool(raw&64));r[5]=(r[5]-r[6])&MASK
            r[6]=signed(r[5]&65535,16)&MASK;positive=signed(r[6])>=0;t(positive);branch(0x65A3C,positive,0x65A40)
            if not positive:emit(0x65A3E);r[6]=0
            emit(0x65A40,0x65A4A);r[4]=0x1245A;r[5]=0x11A55;r[2]=0x26474;r[6]&=255
            row=call(0x65A46,0x26474);byte_curve(row)
            emit(0x65A4A,0x65A54);r[2]=256;r[6]=r[0]&255;r[2]-=r[6];control(0x65A50,'jump',0x65A58,True)
        else:emit(0x65A54,0x65A58);r[2]=256
        emit(0x65A58,0x65A62);r[7]=frame_access(0x65A58,'read',stack,4,7);macl=(r[7]*r[2])&MASK;r[6]=macl
        positive=signed(r[6])>=0;t(positive);branch(0x65A60,positive,0x65A68)
        if not positive:emit(0x65A62,0x65A68);r[2]=255;r[6]=(r[6]+255)&MASK
        emit(0x65A68,0x65A7A);r[2]=r[6]>>8;r[6]=((r[2]<<16)|(r[2]>>16))&MASK
        r[2]=signed(r[6]&255,8)&MASK;r[6]=((r[6]>>16)|(r[2]<<16))&MASK;r[2]=0xFFFF8000
        within=signed(r[6])>=-32768;t(within);branch(0x65A78,within,0x65A7C)
        if not within:emit(0x65A7A);r[6]=r[2]
        emit(0x65A7C,0x65A82);r[2]=32767;above=signed(r[6])>32767;t(above);branch(0x65A80,above,0x65A84)
        if not above:emit(0x65A82);r[2]=r[6]
        emit(0x65A84,0x65A92);r[0]=0x640;put(0x65A86,0x18CC,2,2,r[2]);output=r[2]&65535
        stack+=4;macl=pop(0x65A8A);pr=pop(0x65A8C);r[14]=pop(0x65A90,14);control(0x65A8E,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:v&MASK for i,v in enumerate(r) if v is not None},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=output)
