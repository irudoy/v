"""Independent truncation, byte-product and full-carry scalar equations."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def truncate(value,divisor):return value//divisor if value>=0 else -((-value)//divisor)


def control_path(entry,controls,continuation):
    path=[];branches=[];pc=entry
    while pc!=continuation:
        if len(path)>=64:raise ValueError('the scalar product equations leave their finite natural path')
        path.append(pc)
        if pc not in controls:pc+=2;continue
        kind,target,delay=controls[pc]
        branches.append(dict(site=pc,target=target,kind=kind,delay=delay))
        if delay:path.append(pc+2)
        pc=target
    return tuple(path),branches


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(memory) is not bytes or len(memory)!=65536 or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(value) is not int or not 0<=value<=MASK for value in context)
            or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the scalar product equations require complete exact CPU, RAM, SR and frame inputs')
    registers=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before);controls={};tags={}
    def u(at,width=1):return int.from_bytes(memory[at:at+width],'big')
    def put(at,value,width=1):ram[at:at+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')
    def register(index,value):registers[index]=value&MASK
    def branch(site,taken,target,delay=False):
        controls[site]=('taken' if taken else 'fallthrough',target if taken else site+(4 if delay else 2),delay)
    def jump(site,target):controls[site]=('jump',target,True)
    def returns(site):controls[site]=('return',continuation,True)
    def saved(value,depth=4):frame[160-depth:164-depth]=value.to_bytes(4,'big')
    saved(context[17])
    if entry==0x5279C:
        saved(context[15],8);disabled=bool(u(0x4184)&64)
        difference=signed(((u(0x1650,2)<<8)-u(0x1640,4))&MASK,32)
        delta=truncate(difference,256);gain=u(0x15DE);product=delta*gain
        quotient=truncate(product,32);upper=min(quotient,32767);output=0 if disabled else max(upper,-32768)
        register(0,0x7DA);register(4,RAM_BASE+0x128C);register(6,output)
        register(5,RAM_BASE+0x4184 if disabled else gain)
        if not disabled:register(2,-32768)
        put(0x1A66,output,2);t=False if disabled else upper>=-32768
        branch(0x527AA,disabled,0x527FC,True);branch(0x527C2,difference>=0,0x527CC,True)
        branch(0x527DC,product>=0,0x527E0);branch(0x527EE,quotient>32767,0x527F2)
        branch(0x527F8,upper>=-32768,0x527FC);returns(0x52804)
        tags.update(disabled=disabled,difference=difference,delta=delta,product=product,quotient=quotient,output=output)
    elif entry==0x52902:
        product=u(0x150A)*signed(u(0x1A66,2),16);quotient=truncate(product,256)
        flags=bool(u(0x245D)&32);configuration=bool(calibration[0x8B40][0]&4)
        output=0 if flags and configuration else max(-32768,min(quotient,32767))
        adjusted=(product+(255 if product<0 else 0))&MASK
        register(2,32767 if quotient>=0 else signed((adjusted>>24)&255,8))
        register(0,output);register(5,output);register(6,RAM_BASE+0x22F8);put(0x2300,output,2)
        t=not flags or not configuration
        branch(0x52916,product>=0,0x5291E);branch(0x5292A,quotient<0,0x52938)
        branch(0x52930,quotient<=32767,0x52934);jump(0x52934,0x52942)
        branch(0x5293E,quotient<-32768,0x52942)
        branch(0x52948,not flags,0x52954);branch(0x52950,not configuration,0x52954);returns(0x5295A)
        tags.update(product=product,quotient=quotient,flags=flags,configuration=configuration,output=output)
    elif entry==0x5444C:
        product=u(0x2FC0)*u(0x2FC1)*calibration[0x8BBE][0]
        first_raw=product>>14;first=min(first_raw,255)
        second_product=first*u(0x1024,2);second_raw=second_product>>5;output=min(second_raw,65535)
        put(0x33BE,first);put(0x415A,output,2)
        register(0,0x36);register(2,RAM_BASE+0x4124);register(4,RAM_BASE+0x28F8)
        register(5,RAM_BASE+0x1024);register(6,output);t=second_raw>65535
        branch(0x54478,first_raw>255,0x5447C);branch(0x5448E,True,0x54492)
        branch(0x544A2,second_raw<=65535,0x544A6);returns(0x544AE)
        tags.update(product=product,first_raw=first_raw,first=first,second_product=second_product,
            second_raw=second_raw,output=output)
    elif entry==0xA5284:
        first=context[4]&65535;weight=context[5]&65535
        product=weight*u(0x338A)*u(0x2FF2);high=product>=0x80000000
        forward=MASK if high else 2*product;retained=(65536-weight)*first
        carry=int((forward&65535)+(retained&65535)>=65536)
        total=(forward+retained)>>16;output=min(total,65535)
        register(0,output);register(2,MASK if total>65535 else total);register(4,total)
        register(5,retained>>16);register(6,carry);register(7,65535);t=total>65535
        branch(0xA52A8,not high,0xA52AE);jump(0xA52AA,0xA52B0)
        branch(0xA52D8,total<=65535,0xA52DE,True);returns(0xA52E0)
        tags.update(first=first,weight=weight,product=product,high=high,forward=forward,
            retained=retained,carry=carry,total=total,output=output)
    else:raise ValueError('the scalar product equations name an undeclared natural entry')
    sr=(sr_before&~1)|int(t);path,branches=control_path(entry,controls,continuation)
    return dict(entry=entry,registers=tuple(registers),sr=sr,gbr=context[15],mach=context[16],macl=context[17],
        pr=continuation,sp=sp,frame=bytes(frame),ram=bytes(ram),path=path,branches=branches,tags=tags,
        exit=(sr,continuation,context[17],context[16],context[15],*reversed(registers)))
