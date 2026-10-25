"""Separate complete threshold-window caller,real division and ordered local byte/dword lineage."""
from kb import division_callees_semantics as division
MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry not in (0x847DC,)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the threshold window reader caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the threshold window reader caller equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the threshold window reader caller equation loses one authoritative physical preimage')
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
            raise ValueError('the actual threshold-window signed helper loses its nonzero signed-word divisor')
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

    def natural_caller():
        nonlocal stack,gbr
        emit(0x847DC,0x847F8)
        push(0x847DC,r[12],12);push(0x847DE,r[13],13);push(0x847E0,pr);push(0x847E2,gbr)
        r[0]=gbr=RAM_BASE+0x4124;stack-=12;r[12]=r[6];r[6]=RAM_BASE+0x424C;r[0]=r[5]
        frame_access(0x847F0,'write',stack+3,1,0,r[0]);r[0]=load(0x847F2,0x4251,1,0)
        active=bool(r[0]&128);t(not active);branch(0x847F6,not active,0x84890)
        if not active:return False
        emit(0x847F8,0x84800);r[0]=load(0x847F8,0x41D2,1,0);active=bool(r[0]&2);t(not active)
        branch(0x847FC,not active,0x84890,True);r[2]=r[0]
        if not active:return False
        emit(0x84800,0x84806);r[0]=r[2];active=bool(r[0]&1);t(not active);branch(0x84804,not active,0x84890)
        if not active:return False
        emit(0x84806,0x84818);r[2]=RAM_BASE+0x119C;r[0]=32;r[13]=r[4]&65535
        r[5]=load(0x8480C,0x11BC,2,5);r[2]=(r[13]-30)&MASK
        nonnegative=signed(r[2])>=0;t(nonnegative);branch(0x84814,nonnegative,0x8481A,True);r[5]&=65535
        if not nonnegative:emit(0x84818);r[2]=0
        emit(0x8481A,0x8481E);inside=r[5]>=r[2];t(inside);branch(0x8481C,not inside,0x84890)
        if not inside:return False
        emit(0x8481E,0x8482A);r[6]=255;r[13]=(r[13]+30)&MASK
        capped=r[13]>r[6];t(capped);branch(0x84826,not capped,0x8482C,True);r[2]=r[13]
        if capped:emit(0x8482A);r[2]=r[6]
        emit(0x8482C,0x84830);outside=r[5]>=r[2];t(outside);branch(0x8482E,outside,0x84890)
        if outside:return False
        emit(0x84830,0x84844);r[0]=load(0x84830,0x413E,1,0);r[6]=0x21BBC;r[2]=r[0]&255
        r[0]=signed(frame_access(0x84836,'read',stack+3,1,0),8)&MASK
        frame_access(0x84838,'write',stack+8,4,2,r[2]);r[1]=(r[0]&255)*8;r[0]=10
        row=call(0x84840,0x21BBC);signed_divider(row)
        emit(0x84844,0x8484A);r[6]=frame_access(0x84844,'read',stack+8,4,6)
        inside=signed(r[6])>=signed(r[0]);t(inside);branch(0x84848,not inside,0x84890)
        if not inside:return False
        emit(0x8484A,0x84862);r[0]=load(0x8484A,0x413E,1,0);r[6]=0x21BBC;r[2]=r[0]&255
        r[0]=signed(frame_access(0x84850,'read',stack+3,1,0),8)&MASK
        frame_access(0x84852,'write',stack+4,4,2,r[2]);r[4]=r[0]&255;r[1]=r[4]*12;r[0]=10
        row=call(0x8485E,0x21BBC);signed_divider(row)
        emit(0x84862,0x84868);r[6]=frame_access(0x84862,'read',stack+4,4,6)
        outside=signed(r[6])>=signed(r[0]);t(outside);branch(0x84866,outside,0x84890)
        if outside:return False
        emit(0x84868,0x84870);r[12]&=255;r[6]=110;high=r[12]>=r[6];t(high);branch(0x8486E,not high,0x8487C)
        if high:
            emit(0x84870,0x8487C);r[5]=RAM_BASE+0x39C4;r[0]=0x5E0;r[2]=load(0x84874,0x3FA4,1,2)&255
            held_high=r[2]>=r[6];t(held_high);branch(0x8487A,held_high,0x8488C)
            if held_high:return True
        emit(0x8487C,0x84880);t(high);branch(0x8487E,high,0x84890)
        if high:return False
        emit(0x84880,0x8488C);r[5]=RAM_BASE+0x39C4;r[0]=0x5E0;r[2]=load(0x84884,0x3FA4,1,2)
        r[5]=r[2]&255;held_high=r[5]>=r[6];t(held_high);branch(0x8488A,held_high,0x84890)
        return not held_high

    passed=natural_caller()
    if passed:
        emit(0x8488C,0x84890);control(0x8488C,'jump',0x84892,True);r[0]=1
    else:emit(0x84890);r[0]=0
    emit(0x84892,0x8489E);stack+=12;gbr=pop(0x84894);pr=pop(0x84896)
    r[13]=pop(0x84898,13);r[12]=pop(0x8489C,12);control(0x8489A,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={index:value&MASK for index,value in enumerate(r) if value is not None},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0])
