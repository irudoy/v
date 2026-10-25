"""Separate wrapped products, arithmetic shift, reciprocal, saturation and signed blend equations."""
from kb import division_callees_semantics as division

MASK=0xFFFFFFFF
RAM_BASE=0x01000000
CALLER_SPANS=((0x4E59C,0x4E604),(0x74478,0x7452C),(0x74B04,0x74B68))


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def swapped(value):return ((value<<16)|(value>>16))&MASK


def product_shift(first,second):
    if any(type(v) is not int or not 0<=v<=65535 for v in (first,second)):
        raise ValueError('the scaled product equation changes an unsigned input word')
    product=(first*second)&MASK
    return dict(product=product,value=(signed(product)>>6)&MASK,t=bool(product&32))


def blend(current,history,weight):
    if (type(current) is not int or not -32768<=current<=32767
            or any(type(v) is not int or not 0<=v<=65535 for v in (history,weight))):
        raise ValueError('the signed blend equation changes a complete bounded operand')
    if weight==0:return current&MASK
    if weight==65535:return signed(history,16)&MASK
    total=(current*(65536-weight)+signed(history,16)*weight)&MASK
    return swapped(total)


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose caller equations; the independent instruction oracle executes every helper byte."""
    if (type(entry) is not int or entry not in (0x4E59C,0x74478,0x74B04)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the scaled division equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    events={};controls={};calls=[];gbr=context[15];macl=context[17]
    sr=sr_before;sr_mask=MASK;depth=0

    def reg(index,value):r[index]=value&MASK
    def t(value):
        nonlocal sr,sr_mask
        sr=(sr&~1)|int(bool(value));sr_mask|=1
    def event(site,mode,address,width,register,domain,raw):
        return dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex())
    def read(site,at,width,register):
        raw=bytes(ram[at:at+width]);events[site]=event(site,'read',RAM_BASE+at,width,register,'ram',raw)
        return int.from_bytes(raw,'big')
    def rom(site,at,register):
        raw=calibration[at]
        if len(raw)!=2:raise ValueError('the scaled division loses an exact controlled word divisor')
        events[site]=event(site,'read',at,2,register,'rom',raw)
        return int.from_bytes(raw,'big')
    def put(site,at,width,register,value):
        raw=(value&((1<<(8*width))-1)).to_bytes(width,'big');ram[at:at+width]=raw
        events[site]=event(site,'write',RAM_BASE+at,width,register,'ram',raw)
    def frame_event(site,mode,at_depth,register,value,*,destination=None):
        at=160-at_depth;raw=(value&MASK).to_bytes(4,'big')
        if mode=='write':frame[at:at+4]=raw
        elif bytes(frame[at:at+4])!=raw:raise ValueError('the caller equation loses an ordered intermediate saved frame value')
        item=event(site,mode,sp-at_depth,4,register,'frame',raw)
        if destination is None:events[site]=item
        else:destination.append(item)
    def push(site,value,register=None):
        nonlocal depth
        depth+=4;frame_event(site,'write',depth,register,value)
    def pop(site,value,register=None):
        nonlocal depth
        frame_event(site,'read',depth,register,value);depth-=4;return value
    def branch(site,taken,target,delay=False):
        controls[site]=dict(site=site,kind='taken' if taken else 'fallthrough',
            target=target if taken else site+(4 if delay else 2),delay=delay)
    def jump(site,target):controls[site]=dict(site=site,kind='jump',target=target,delay=True)
    def call(site,target):
        if any(value is None for value in r):raise ValueError('a caller supplies an unresolved complete helper argument state')
        row=dict(site=site,target=target,return_address=site+4,sp=sp-depth,registers=tuple(r),
            gbr=gbr,mach=context[16],macl=macl,sr=sr,sr_mask=sr_mask,physical=[])
        calls.append(row);controls[site]=dict(site=site,kind='call',target=target,delay=True);return row
    def returned(row,site):
        row.update(return_site=site,return_registers=tuple(r),return_sr=sr,return_sr_mask=sr_mask,
            return_gbr=gbr,return_mach=context[16],return_macl=macl)
    def shift(site):
        raw=r[0];row=call(site,0x224FA);reg(0,signed(raw)>>6);t(bool(raw&32));returned(row,0x22504)
    def divide(site):
        nonlocal sr,sr_mask
        divisor,dividend=r[:2];row=call(site,0x21BBC);physical=row['physical']
        if not 0<=divisor<=65535:raise ValueError('the scaled caller changes its actual unsigned word divisor')
        row.update(divisor=divisor,dividend=dividend,zero=divisor==0,
            long_path=divisor!=0 and abs(signed(dividend))>=divisor*256)
        frame_event(0x21BBC,'write',depth+4,2,r[2],destination=physical)
        if divisor==0:
            physical.extend((event(0x21C70,'read',0x21CD8,4,1,'rom',(RAM_BASE+0x9818).to_bytes(4,'big')),
                event(0x21C72,'read',0x21CDC,4,2,'rom',(0x44E).to_bytes(4,'big'))))
            ram[0x9818:0x981C]=(0x44E).to_bytes(4,'big')
            physical.append(event(0x21C74,'write',RAM_BASE+0x9818,4,2,'ram',bytes(ram[0x9818:0x981C])))
            frame_event(0x21C7A,'read',depth+4,2,r[2],destination=physical)
            r[0]=0;r[1]=RAM_BASE+0x9818;t(True);terminal=0x21C78
        else:
            frame_event(0x21BC2,'write',depth+8,3,r[3],destination=physical)
            if row['long_path']:
                frame_event(0x21C08,'write',depth+12,4,r[4],destination=physical)
                frame_event(0x21C68,'read',depth+12,4,r[4],destination=physical)
                frame_event(0x21C6A,'read',depth+8,3,r[3],destination=physical)
                frame_event(0x21C6E,'read',depth+4,2,r[2],destination=physical);terminal=0x21C6C
            else:
                frame_event(0x21C02,'read',depth+8,3,r[3],destination=physical)
                frame_event(0x21C06,'read',depth+4,2,r[2],destination=physical);terminal=0x21C04
            r[0]=division.quotient('signed',divisor,dividend);r[1]=None
            sr&=~0x301;sr_mask&=~0x100;t(signed(dividend)<0)
        returned(row,terminal)
        return signed(r[0])

    if entry==0x4E59C:
        push(0x4E59C,continuation);push(0x4E59E,context[17]);push(0x4E5A0,context[15])
        gbr=RAM_BASE+0x128C;r[4]=gbr;r[5]=65535
        source=read(0x4E5AE,0x1652,2,6);gain=read(0x4E5B4,0x15DE,1,2)
        macl=source*gain;denominator=(6*macl)>>15;r[6]=macl;r[2]=denominator
        t(False);branch(0x4E5D0,True,0x4E5D4)
        r[6]=0x21BBC;r[1]=65536;r[0]=denominator
        put(0x4E5DA,0x12C2,2,0,denominator)
        quotient=divide(0x4E5DE)
        r[6]=256;r[5]=65535;reg(0,quotient+256)
        above=r[0]>65535;t(above);branch(0x4E5EE,not above,0x4E5F4,True)
        r[2]=65535 if above else r[0];r[4]=RAM_BASE+0x128C;r[0]=0x434
        output=r[2];put(0x4E5F8,0x16C0,2,2,output)
        gbr=pop(0x4E5FA,context[15]);macl=pop(0x4E5FC,context[17]);pop(0x4E5FE,continuation)
        terminal=0x4E600
    elif entry==0x74B04:
        push(0x74B04,r[13],13);push(0x74B06,r[14],14);push(0x74B08,continuation);push(0x74B0A,macl);depth+=4
        r[2]=RAM_BASE+0x23BC;r[14]=RAM_BASE+0x128C
        source=read(0x74B14,0x23FC,2,6);factor=read(0x74B1C,0x19A2,2,2)
        r[13]=0x944E;macl=(source*factor)&MASK;r[6]=0x224FA;r[0]=macl;r[2]=factor
        shift(0x74B24);r[2]=r[0];r[0]=0x72E
        divisor=rom(0x74B2C,0x944E,5);reg(5,signed(divisor,16))
        reg(6,signed(read(0x74B2E,0x19BA,2,6),16));r[7]=0x21BBC;r[0]=divisor
        macl=(r[2]*r[6])&MASK;r[1]=macl
        frame_event(0x74B3A,'write',depth,1,r[1]);saved_dividend=r[1]
        candidate=divide(0x74B38);r[4]=32767;above=candidate>32767;t(above);branch(0x74B40,above,0x74B4E)
        if not above:
            divisor=rom(0x74B42,0x944E,5);reg(5,signed(divisor,16));r[1]=saved_dividend
            frame_event(0x74B44,'read',depth,1,saved_dividend);r[7]=0x21BBC;r[0]=divisor
            candidate=divide(0x74B48);r[4]=r[0]
        reg(2,-32768);within=signed(r[4])>=-32768;t(within);branch(0x74B54,not within,0x74B58)
        if within:r[2]=r[4]
        r[0]=0x65C;output=r[2]&65535;put(0x74B5A,0x18E8,2,2,r[2])
        depth-=4;macl=pop(0x74B5E,context[17]);pop(0x74B60,continuation)
        r[14]=pop(0x74B62,context[14],14);r[13]=pop(0x74B66,context[13],13);terminal=0x74B64
    else:
        push(0x74478,r[14],14);push(0x7447A,continuation);push(0x7447C,macl);r[14]=RAM_BASE+0x128C
        source=read(0x74482,0x1CCE,2,6);factor=read(0x74488,0x1D16,2,2)
        r[6]=0x224FA;r[2]=factor;macl=(source*factor)&MASK;r[0]=macl
        shift(0x74490);r[2]=r[0];r[0]=0xA8E;r[5]=0x16316
        reg(6,signed(read(0x7449A,0x1D1A,2,6),16));macl=(r[2]*r[6])&MASK
        divisor=rom(0x7449E,0x16316,6);reg(6,signed(divisor,16));r[5]=0x21BBC;r[1]=macl;r[0]=divisor
        candidate=divide(0x744A4);r[6]=32767;above=candidate>32767;t(above);branch(0x744AC,not above,0x744B2,True)
        reg(2,32767 if above else candidate);reg(6,-32768);within=signed(r[2])>=-32768;t(within);branch(0x744B8,within,0x744BC)
        if not within:r[2]=r[6]
        r[0]=0xA6C;reg(4,signed(r[2]&65535,16));r[6]=RAM_BASE+0x245C
        put(0x744C2,0x1CF8,2,4,r[4])
        flag_first=read(0x744C4,0x245F,1,0);r[6]=RAM_BASE+0x417E;r[5]=int(bool(flag_first&128))
        flag_second=read(0x744D0,0x417E,1,0);r[2]=RAM_BASE+0x2470;r[5]|=int(bool(flag_second&8))
        flag_third=read(0x744DE,0x249B,1,0);r[0]=flag_third&1;r[5]|=r[0];r[5]&=255
        bypass=bool(r[5]);t(not bypass);branch(0x744E8,not bypass,0x744F0)
        if bypass:
            r[0]=0xA74;put(0x744EE,0x1D00,2,4,r[4]);jump(0x744EC,0x74524)
        else:
            r[2]=RAM_BASE+0x23BC;r[0]=0x66;r[5]=read(0x744F4,0x2422,2,5)
            t(r[5]==0);branch(0x744FA,r[5]==0,0x74520)
            if r[5]:
                r[6]=65535;t(r[5]==65535);branch(0x74502,r[5]!=65535,0x7450A)
                r[0]=0xA6A
                if r[5]==65535:
                    reg(4,signed(read(0x74508,0x1CF6,2,4),16));jump(0x74506,0x74520)
                else:
                    r[2]=65536-r[5];macl=(r[4]*r[2])&MASK
                    history=read(0x74514,0x1CF6,2,2);reg(2,signed(history,16));r[6]=macl
                    macl=(r[2]*r[5])&MASK;r[2]=macl;r[6]=(r[6]+r[2])&MASK;r[4]=swapped(r[6])
            r[0]=0xA74;put(0x74522,0x1D00,2,4,r[4])
        output=r[4]&65535;macl=pop(0x74524,context[17]);pop(0x74526,continuation)
        r[14]=pop(0x7452A,context[14],14);terminal=0x74528
    controls[terminal]=dict(site=terminal,kind='return',target=continuation,delay=True)
    path=[];branches=[];pc=entry
    while pc!=continuation:
        if len(path)>192:raise ValueError('the scaled division caller leaves its finite natural source path')
        path.append(pc);control=controls.get(pc)
        if control is None:pc+=2;continue
        branches.append(control)
        if control['delay']:path.append(pc+2)
        pc=pc+4 if control['kind']=='call' else control['target']
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:value for i,value in enumerate(r) if value is not None},
        sr=sr,sr_mask=sr_mask,gbr=gbr,mach=context[16],macl=macl,sp=sp-depth,pr=continuation,
        events=events,calls=calls,caller_path=tuple(path),caller_branches=branches,output=output)
