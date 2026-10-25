"""Independent arithmetic, complete register/frame and natural-control equations."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def control_path(entry,controls,continuation):
    path=[];branches=[];pc=entry
    while pc!=continuation:
        if len(path)>=128:raise ValueError('the scalar leaf equations leave their finite natural path')
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
        raise ValueError('the scalar RAM equations require complete exact input CPU, RAM, SR and frame state')
    registers=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before);controls={};tags={}
    def u(at,width=1):return int.from_bytes(memory[at:at+width],'big')
    def s(at,width=1):return signed(u(at,width),width*8)
    def put(at,value,width=1):ram[at:at+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')
    def register(index,value):registers[index]=value&MASK
    def branch(site,taken,target,delay=False):
        controls[site]=('taken' if taken else 'fallthrough',target if taken else site+(4 if delay else 2),delay)
    def jump(site,target):controls[site]=('jump',target,True)
    def returns(*sites):
        for site in sites:controls[site]=('return',continuation,True)
    def saved(value,depth=4):frame[160-depth:164-depth]=value.to_bytes(4,'big')
    if entry==0x259BE:
        flag=context[7]&255;difference=(context[4]-(context[6] if not flag else 0))&MASK
        selected=signed(difference,32)>signed(context[5],32)
        register(7,flag);register(2,int(selected));register(0,int(selected));t=selected
        branch(0x259C2,bool(flag),0x259C8,True);returns(0x259CC)
        tags.update(flag=flag,difference=difference,selected=selected)
    elif entry in (0x39588,0x39874):
        first,second=(0x1187,0x1081) if entry==0x39588 else (0x1F89,0x107C)
        current,target=u(first),u(second)
        above=current>target;near=current+2>target
        output=current if above else target if near else current+2
        register(0,output);register(4,output);register(5,current if above or near else current+2)
        register(2,RAM_BASE+0x107A if above else current+2);t=near
        if entry==0x39588:
            saved(context[15]);branch(0x3959A,above,0x395A6);branch(0x395A2,near,0x395A8);returns(0x395AA)
        else:
            branch(0x39884,above,0x39890);branch(0x3988C,near,0x39892);returns(0x39892)
        tags.update(current=current,target=target,above=above,near=near,output=output)
    elif entry==0x468B0:
        optional=bool(calibration[0x870C][0]&128)
        total=u(0x1752,2)+4*u(0x1765)+u(0x1748,2)+s(0x1230,2)+u(0x15AC)+u(0x13F7)+s(0x170A,2)
        if optional:total+=u(0x1F62)
        lower=max(total,0);output=min(lower,65535);put(0x173A,output,2);saved(context[14])
        register(0,0x4AE);register(1,RAM_BASE+0x128C);register(2,output);register(4,u(0x1748,2))
        register(5,RAM_BASE+0x1E60 if optional else 0x870C);register(6,65535);register(7,u(0x15AC))
        t=lower>65535
        branch(0x468F0,not optional,0x468FE,True);branch(0x46900,total>=0,0x46906,True)
        branch(0x4690C,lower<=65535,0x46910);returns(0x46914)
        tags.update(optional=optional,total=total,lower=lower,output=output)
    elif entry==0x4AB94:
        current,baseline,gain=u(0x231A,2),u(0x230C,2),u(0x22E8,2)
        active=current>=baseline;raw=((current-baseline)*gain)>>14 if active else 0
        output=min(raw,65535);put(0x18E2,output,2)
        saved(context[17]);saved(context[15],8)
        register(0,0x656);register(2,output);register(4,baseline);register(5,RAM_BASE+0x128C)
        if active:register(6,65535)
        t=active and raw>65535
        branch(0x4ABA6,not active,0x4ABC6);branch(0x4ABC0,raw<=65535,0x4ABC8)
        jump(0x4ABC2,0x4ABC8);returns(0x4ABD0)
        tags.update(active=active,raw=raw,output=output)
    elif entry==0x4AF38:
        first,second,offset=u(0x160F)&127,u(0x1610)&127,u(0x11AF)
        enabled=bool(calibration[0x8B3F][0]&2);difference=second-first;remaining=first-offset
        middle=max(difference,0) if enabled else 0;output=max(remaining,0)
        put(0x12DE,first);put(0x12E0,second);put(0x12DF,middle);put(0x23BD,output);saved(context[15])
        register(0,output);register(2,RAM_BASE+0x23BC);register(4,0x8B3F);register(5,RAM_BASE+0x119C)
        register(6,remaining);t=remaining>=0
        branch(0x4AF5A,not enabled,0x4AF6A);branch(0x4AF62,difference>=0,0x4AF66)
        jump(0x4AF66,0x4AF6C);branch(0x4AF7C,remaining>=0,0x4AF80);returns(0x4AF86)
        tags.update(enabled=enabled,difference=difference,remaining=remaining,middle=middle,output=output)
    elif entry==0x4BB6A:
        raw=u(0x22FE)+u(0x22F8)-(u(0x1657)>>4);lower=max(raw,0);output=min(lower,255)
        put(0x23C5,output);register(0,output);register(2,RAM_BASE+0x23BC);register(4,u(0x22F8))
        register(5,u(0x1657)>>4);register(6,255);register(7,RAM_BASE+0x22F8);t=lower>255
        branch(0x4BB8A,raw>=0,0x4BB8E);branch(0x4BB96,lower<=255,0x4BB9A);returns(0x4BB9E)
        tags.update(raw=raw,lower=lower,output=output)
    elif entry==0x4C136:
        flag=bool(u(0x4184)&64);mode=u(0x1239);quiet=not bool(u(0x2458)&32)
        primary=mode in (1,2) or not flag and quiet
        selected=0x1830 if primary else 0x1831;output=u(selected)
        put(0x24D2,u(0x24D2)|2 if flag else u(0x24D2)&0xFD);put(0x2404,output);saved(context[15])
        register(0,s(selected));register(2,64 if flag else 0);register(5,s(0x1239));register(6,RAM_BASE+0x128C)
        t=primary
        branch(0x4C14A,flag,0x4C150,True);branch(0x4C15C,mode==1,0x4C174)
        branch(0x4C160,mode==2,0x4C174);branch(0x4C164,flag,0x4C16C)
        branch(0x4C16A,quiet,0x4C174);jump(0x4C170,0x4C17A);returns(0x4C17C)
        tags.update(flag=flag,mode=mode,quiet=quiet,primary=primary,selected=selected,output=output)
    elif entry==0x4E112:
        enabled=bool(u(0x248D)&16);latched=u(0x25FD);old=s(0x1513)
        retained=enabled and latched!=0;decay=old-1 if old>0 else old+1 if old<0 else 0
        register(1,RAM_BASE+0x25FB)
        if retained:
            register(0,s(0x25FD));register(6,RAM_BASE+0x2470);t=False
        else:
            output=calibration[0x8440][0];put(0x25FD,output)
            register(0,signed(output,8));register(6,0x8440);t=True
            if enabled:
                put(0x1513,decay);register(2,decay);register(5,RAM_BASE+0x128C)
        branch(0x4E11C,not enabled,0x4E156);branch(0x4E122,latched!=0,0x4E15E)
        branch(0x4E12E,old<=0,0x4E134);jump(0x4E130,0x4E13A)
        branch(0x4E136,old>=0,0x4E13A);branch(0x4E140,True,0x4E146)
        jump(0x4E142,0x4E148);branch(0x4E14E,True,0x4E152);returns(0x4E15A,0x4E15E)
        tags.update(enabled=enabled,latched=latched,retained=retained,old=old,decay=decay)
    elif entry==0x554AE:
        base=(u(0x15F8,4)+0x4000)&MASK;total=(base+u(0x230C,2)+u(0x15DA,2))&MASK
        total_signed=signed(total,32);high=total_signed>65535;output=max(0,min(total_signed,65535))
        put(0x231A,output,2);saved(context[15]);register(0,output);register(1,RAM_BASE+0x128C)
        register(2,output);register(4,u(0x230C,2));register(5,base if high else total)
        register(6,65535);register(7,u(0x15DA,2));t=total_signed>=0
        branch(0x554D6,not high,0x554DC);jump(0x554D8,0x554E2)
        branch(0x554E4,total_signed>=0,0x554E8);returns(0x554EC)
        tags.update(base=base,total=total,total_signed=total_signed,high=high,output=output)
    elif entry==0x70D82:
        enabled=bool(u(0x2490)&2);state=u(0x25D6);candidate=s(0x19C0,2);primary=s(0x243A,2)
        chosen=primary if not enabled else candidate if state else min(primary,candidate)
        put(0x2438,chosen,2);put(0x19C2,chosen,2);saved(context[15])
        register(0,0x736);register(2,chosen);register(5,RAM_BASE+0x128C)
        if enabled:register(6,RAM_BASE+0x256A if state else chosen)
        t=True if not enabled else False if state else primary>candidate
        branch(0x70D8C,enabled,0x70D94);jump(0x70D90,0x70DB6)
        branch(0x70DA0,state!=0,0x70DB4,True);branch(0x70DA8,primary<=candidate,0x70DAE,True)
        jump(0x70DB0,0x70DB6);returns(0x70DBE)
        tags.update(enabled=enabled,state=state,candidate=candidate,primary=primary,chosen=chosen)
    elif entry==0xA5530:
        flags,gate=u(0x4204),u(0x244F);current,threshold=u(0x3334,2),u(0x32EE,2)
        first=bool(flags&8);second=bool(gate&32);high=current>threshold
        register(4,RAM_BASE+0x41A9);register(5,s(0x4204))
        if first:register(0,s(0x4204));t=False
        elif not second:register(0,s(0x244F));register(6,RAM_BASE+0x244F);t=True
        else:
            register(2,s(0x32EE,2));register(6,s(0x3334,2));register(7,RAM_BASE+0x28F8);t=high
            register(0,0x5B if high else 0x9F6)
            if high:register(5,s(0x4204)|8);put(0x4204,flags|8)
        branch(0xA553A,first,0xA555C);branch(0xA5542,not second,0xA555C)
        branch(0xA5550,not high,0xA555C);returns(0xA5558,0xA555C)
        tags.update(first=first,second=second,high=high,current=current,threshold=threshold)
    else:raise ValueError('the scalar RAM equations name an undeclared natural leaf entry')
    sr=(sr_before&~1)|int(t);path,branches=control_path(entry,controls,continuation)
    return dict(entry=entry,registers=tuple(registers),sr=sr,gbr=context[15],mach=context[16],macl=context[17],
        pr=continuation,sp=sp,frame=bytes(frame),ram=bytes(ram),path=path,branches=branches,tags=tags,
        exit=(sr,continuation,context[17],context[16],context[15],*reversed(registers)))
