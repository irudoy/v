"""Separate complete byte-ratio producer,variable unsigned division and signed fallback."""
from kb import division_callees_semantics as division

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry not in (0x4AE6C,)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the byte ratio producer equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    unknown_frame=set();opaque_frame_sites=[]
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the byte ratio producer equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=None if raw is None else raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the byte ratio producer equation loses one authoritative physical preimage')
        at,data=spans[0];raw=data[address-at:address-at+width]
        event(site,'read',address,width,register,'rom',raw)
        return int.from_bytes(raw,'big')

    def frame_access(site,mode,address,width,register,value=None):
        at=160+address-sp
        positions=set(range(at,at+width))
        if mode=='write':
            if value is None:
                if (site,width,register)!=(0x22508,4,1):
                    raise ValueError('the byte-ratio equation introduces an undeclared unknown frame carrier')
                unknown_frame.update(positions)
            else:
                frame[at:at+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big');unknown_frame.difference_update(positions)
        if positions&unknown_frame:
            if (positions&unknown_frame)!=positions or (site,mode,width,register) not in ((0x22508,'write',4,1),(0x22518,'read',4,1)):
                raise ValueError('the byte-ratio equation broadens its exact saved post-DIV1 R1 carrier')
            opaque_frame_sites.append(site);event(site,mode,address,width,register,'frame',None);return None
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

    def divide(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2]
        if divisor!=5:raise ValueError('the byte-ratio fallback changes its exact signed divisor5')
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

    def unsigned_divider(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2]
        if not 0<divisor<=255*65535 or not 0<=numerator<=MASK:
            raise ValueError('the byte-ratio caller loses its complete positive unsigned product-divisor premise')
        saved_r2,saved_r3=r[2],r[3];large=divisor>65535;long_path=not large and numerator>=divisor*256
        emit(0x21CE0,0x21CEC);push(0x21CE0,saved_r2,2)
        branch(0x21CE4,False,0x21D6A);branch(0x21CEA,large,0x21D76)
        if large:
            emit(0x21D76,0x21DC6);pop(0x21DC4,2);terminal=0x21DC2
        else:
            emit(0x21CEC,0x21CF4);branch(0x21CF2,long_path,0x21D0C)
            if long_path:
                emit(0x21D0C,0x21D6A);push(0x21D0C,saved_r3,3)
                pop(0x21D64,3);pop(0x21D68,2);terminal=0x21D66
            else:
                emit(0x21CF4,0x21D0C);pop(0x21D06,2);terminal=0x21D08
        r[0]=numerator//divisor;r[1]=None;r[2],r[3]=saved_r2,saved_r3
        sr&=~0x301;sr_mask&=~0x101
        row.update(divisor=divisor,dividend=numerator,zero=False,large_divisor=large,long_path=long_path)
        control(terminal,'return',pr,True);returned(row,terminal)

    def signed_shift10(row):
        raw=r[0];saved_r1=r[1]
        emit(0x22508,0x2251A);push(0x22508,saved_r1,1)
        r[0]=(signed(raw)>>10)&MASK;t(bool(raw&(1<<9)));r[1]=pop(0x22518,1)
        control(0x22516,'return',pr,True);returned(row,0x22516)

    emit(0x4AE6C,0x4AE86);push(0x4AE6C,pr);push(0x4AE6E,macl)
    r[7]=RAM_BASE+0x128C;r[0]=0x52C;r[2]=load(0x4AE74,0x17B8,1,2)
    r[0]=0x250;r[5]=r[2]&255;r[2]=load(0x4AE7A,0x14DC,2,2);r[6]=r[2]&65535
    macl=(r[5]*r[6])&MASK;r[2]=macl;empty=r[2]==0;t(empty);branch(0x4AE84,empty,0x4AEC4)
    if not empty:
        emit(0x4AE86,0x4AEA8);r[6]=0x884D;r[0]=0x3A4
        r[4]=signed(read(0x4AE8A,0x884D,4,1),8)&MASK;r[4]&=255;r[6]=r[4]*120
        r[4]=load(0x4AE96,0x1630,2,4);r[0]=r[2];r[5]=r[4]&65535
        macl=(r[6]*r[5])&MASK;r[5]=0x21CE0;r[1]=macl
        row=call(0x4AEA4,0x21CE0);unsigned_divider(row)
        emit(0x4AEA8,0x4AEAC);control(0x4AEA8,'jump',0x4AEC8,True);r[5]=r[0]
    else:
        emit(0x4AEC4,0x4AEC8);r[2]=MASK;r[5]=65535
    emit(0x4AEC8,0x4AEE4);r[2]=0x8B6C;r[6]=signed(read(0x4AECA,0x8B6C,6,1),8)&MASK
    r[6]&=255;r[2]=r[6]*5;r[2]>>=1;r[2]=(r[2]+r[5])&MASK;r[6]=RAM_BASE+0x119C
    high=r[2]>=65536;t(high);branch(0x4AEE0,high,0x4AF00,True);r[0]=32
    if not high:
        emit(0x4AEE4,0x4AEFC);r[5]=load(0x4AEE4,0x11BC,2,5);r[6]=r[5]&65535
        macl=(r[2]*r[6])&MASK;r[1]=((macl>>10)*3)&MASK;r[6]=0x21CE0;r[0]=5
        row=call(0x4AEF8,0x21CE0);unsigned_divider(row)
        emit(0x4AEFC,0x4AF00);control(0x4AEFC,'jump',0x4AF1A,True)
    else:
        emit(0x4AF00,0x4AF0E);r[2]=load(0x4AF00,0x11BC,2,2);r[6]=0x22508
        r[5]=r[2]&65535;r[0]=((r[5]<<16)-r[5])&MASK
        row=call(0x4AF0A,0x22508);signed_shift10(row)
        emit(0x4AF0E,0x4AF1A);r[1]=(r[0]*3)&MASK;r[6]=0x21BBC;r[0]=5
        row=call(0x4AF16,0x21BBC);divide(row)
    emit(0x4AF1A,0x4AF24);r[6]=141;above=r[0]>r[6];t(above);branch(0x4AF20,above,0x4AF2A,True);r[2]=r[0]
    if not above:
        emit(0x4AF24,0x4AF2A);r[2]=(r[2]-14)&MASK;control(0x4AF26,'jump',0x4AF2C,True);r[6]=r[2]
    else:
        emit(0x4AF2A);r[6]=127
    emit(0x4AF2C,0x4AF38);r[2]=RAM_BASE+0x23BC;r[0]=53;macl=pop(0x4AF30);pr=pop(0x4AF32)
    put(0x4AF36,0x23F1,1,6,r[6]);control(0x4AF34,'return',pr,True)
    if unknown_frame:raise ValueError('the byte-ratio caller leaves an unknown final frame byte instead of its real signed-helper overwrite')
    return dict(opaque_frame_sites=tuple(opaque_frame_sites),ram=bytes(ram),frame=bytes(frame),known_registers={index:value&MASK for index,value in enumerate(r) if value is not None},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0])
