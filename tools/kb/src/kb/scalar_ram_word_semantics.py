"""Independent complete word-product, signed-rate and byte-channel equations."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def control_path(entry,controls,continuation):
    path=[];branches=[];pc=entry
    while pc!=continuation:
        if len(path)>=78:raise ValueError('the word equations leave the complete finite natural entries')
        path.append(pc)
        if pc not in controls:pc+=2;continue
        kind,target,delay=controls[pc];branches.append(dict(site=pc,target=target,kind=kind,delay=delay))
        if delay:path.append(pc+2)
        pc=target
    return tuple(path),branches


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(memory) is not bytes or len(memory)!=65536 or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)
            or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the word equations require complete raw CPU, RAM, SR and frame inputs')
    registers=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before);controls={}
    def u(at,width=2):return int.from_bytes(memory[at:at+width],'big')
    def c(at,width=2):
        rows=[blob[at-first:at-first+width] for first,blob in calibration.items()
            if first<=at and at+width<=first+len(blob)]
        if len(rows)!=1:raise ValueError('the word equations omit or alias a complete immutable constant')
        return int.from_bytes(rows[0],'big')
    def reg(index,value):registers[index]=value&MASK
    def put(at,value):ram[at:at+2]=(value&65535).to_bytes(2,'big')
    def branch(site,taken,target,delay=False):
        controls[site]=('taken' if taken else 'fallthrough',target if taken else site+(4 if delay else 2),delay)
    def jump(site,target):controls[site]=('jump',target,True)
    if entry==0x6E490:
        load=u(0x1766,1);factor=c(0x93C8);cap=c(0x6E5F0,4);scale=signed(c(0x6E4E8),16)
        product=(load*factor*4)&MASK;selected=min(product,cap)
        output=((selected*scale)&MASK)>>16;put(0x1300,output)
        frame[156:160]=context[17].to_bytes(4,'big')
        reg(0,0x74);reg(2,output);reg(4,RAM_BASE+0x128C);reg(5,load);reg(6,65535)
        branch(0x6E4AA,product<=cap,0x6E4AE);branch(0x6E4BC,True,0x6E4C0)
        controls[0x6E4C4]=('return',continuation,True);t=False
        tags=dict(load=load,factor=factor,scale=scale,cap=cap,product=product,selected=selected,output=output)
    elif entry==0x76380:
        current=signed(u(0x3D70),16);target=signed(u(0x351E),16);rising=target>current
        rate=c(0x90A8 if rising else 0x90A6)
        adjusted=current+rate if rising else current-rate
        output=min(adjusted,target) if rising else max(adjusted,target)
        put(0x3D70,output)
        reg(0,0x3AC);reg(2,rate);reg(4,adjusted);reg(5,output);reg(6,target);reg(7,RAM_BASE+0x39C4)
        branch(0x76390,not rising,0x763A2)
        branch(0x7639A,adjusted<=target,0x763B0,True);jump(0x7639E,0x763B0)
        branch(0x763AA,adjusted>=target,0x763B0,True)
        controls[0x763B2]=('return',continuation,True)
        t=adjusted>target if rising else adjusted>=target
        tags=dict(current=current,target=target,rising=rising,rate=rate,adjusted=adjusted,output=output&65535)
    elif entry==0xCB1CA:
        index=context[4]&255;source=u(0x28BC+2*index);candidate=source*16+0x2000
        output=min(candidate,65535);put(0x387A+2*index,output)
        reg(0,2*index);reg(2,RAM_BASE+0x387A);reg(3,0x1A2);reg(5,2*index);reg(6,output)
        t=candidate>65535;branch(0xCB1E8,t,0xCB1EC)
        controls[0xCB1F4]=('return',continuation,True)
        tags=dict(index=index,source=source,candidate=candidate,output=output)
    else:raise ValueError('the word equations name another natural entry')
    sr=(sr_before&~1)|int(t);path,branches=control_path(entry,controls,continuation)
    return dict(entry=entry,registers=tuple(registers),sr=sr,gbr=context[15],mach=context[16],macl=context[17],
        pr=continuation,sp=sp,frame=bytes(frame),ram=bytes(ram),path=path,branches=branches,tags=tags,
        exit=(sr,continuation,context[17],context[16],context[15],*reversed(registers)))
