"""Independent flag, signed blend, bound and full byte-index scalar equations."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def control_path(entry,controls,continuation):
    path=[];branches=[];pc=entry
    while pc!=continuation:
        if len(path)>=96:raise ValueError('the gated scalar equations leave their finite natural path')
        path.append(pc)
        if pc not in controls:pc+=2;continue
        kind,target,delay=controls[pc];branches.append(dict(site=pc,target=target,kind=kind,delay=delay))
        if delay:path.append(pc+2)
        pc=target
    return tuple(path),branches


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(memory) is not bytes or len(memory)!=65536 or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(value) is not int or not 0<=value<=MASK for value in context)
            or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the gated scalar equations require complete exact CPU, RAM, SR and frame inputs')
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
    def saved(value,depth=4):frame[160-depth:164-depth]=(value&MASK).to_bytes(4,'big')
    if entry==0x3D45C:
        index=context[4]&255;high=bool(u(0x4185)&64);low=bool(u(0x417F)&32)
        ready=bool((index+1)&u(0x3F3E));candidate=u(0x2838+index);current=u(0x3F4C+index)
        register(4,index);register(6,RAM_BASE+0x417F);register(0,s(0x4185));t=not high
        if not high:
            register(0,s(0x417F));t=not low
            if not low:
                register(0,0x57A);register(2,index+1);register(6,u(0x3F3E));t=not ready
                if ready:
                    register(0,index);register(5,candidate);register(6,current);saved(candidate)
                    register(2,RAM_BASE+0x3F4C);register(7,RAM_BASE+0x39C4);t=candidate>=current
                    if candidate<current:
                        register(2,0x588);register(7,RAM_BASE+0x3F4C);put(0x3F4C+index,candidate)
        branch(0x3D464,high,0x3D4A4,True);branch(0x3D46C,low,0x3D4A4)
        branch(0x3D47C,not ready,0x3D4A4);branch(0x3D49A,candidate>=current,0x3D4A4,True)
        returns(0x3D4A4);tags.update(index=index,high=high,low=low,ready=ready,candidate=candidate,current=current)
    elif entry==0x44448:
        for value,depth in ((context[10],4),(context[11],8),(context[13],12),(context[15],16)):saved(value,depth)
        state=u(0x1071);mode=u(0x183C);gain=u(0x1958);load=u(0x10C0,4);flags=u(0x24D1)
        low=calibration[0x8CF1][0];high=calibration[0x8CF2][0]
        below_high=state<high;mode_one=mode==1;below_low=state<low
        middle=below_low or mode!=0 or load<=gain*10
        register(1,RAM_BASE+0x1068);register(2,gain);register(4,s(0x24D1));register(6,s(0x1071));register(7,0x8CF1)
        if below_high or mode_one:
            output=flags&0xE7;register(0,output);t=mode_one if not below_high else False
            if not below_high:register(5,mode)
        else:
            register(5,mode);register(2,signed(low,8))
            if not below_low and mode==0:register(2,load)
            t=not middle
            if middle:
                output=(flags|8)&0xEF;register(0,3)
            else:output=flags|0x18;register(0,s(0x24D1)|0x18)
        put(0x24D1,output)
        branch(0x44474,below_high,0x444AA,True);branch(0x44482,mode_one,0x444AA)
        branch(0x4448A,below_low,0x4449E);branch(0x4448E,mode!=0,0x4449E)
        branch(0x44496,load<=gain*10,0x4449E)
        jump(0x4449A,0x444AE);jump(0x444A6,0x444B0);returns(0x444B6)
        tags.update(state=state,mode=mode,gain=gain,load=load,flags=flags,below_high=below_high,
            mode_one=mode_one,below_low=below_low,middle=middle,first_flags=(flags|8)&255,output=output)
    elif entry==0x74C08:
        saved(context[17]);primary=bool(u(0x417E)&8);secondary=bool(u(0x249B)&1);status=bool(u(0x245F)&128)
        fallback=primary or secondary or status;weight=u(0x2422,2);first=s(0x18E8,2);second=s(0x18E6,2)
        register(6,RAM_BASE+(0x417E if primary else 0x2470 if secondary else 0x245C))
        register(4,RAM_BASE+0x128C)
        if fallback:output=first;t=False
        else:
            register(5,weight)
            if weight==0:output=first;t=True
            elif weight==65535:output=second;register(6,65535);t=True
            else:
                total=(65536-weight)*first+weight*second
                output=total>>16;register(6,total);t=False
        register(2,output);register(0,0x668);put(0x18F4,output,2)
        branch(0x74C10,primary,0x74C74);branch(0x74C1A,secondary,0x74C74);branch(0x74C22,status,0x74C74)
        branch(0x74C2E,weight!=0,0x74C38);jump(0x74C34,0x74C7A)
        branch(0x74C3E,weight!=65535,0x74C54);jump(0x74C44,0x74C7A)
        jump(0x74C70,0x74C7A);returns(0x74C7E)
        tags.update(primary=primary,secondary=secondary,status=status,fallback=fallback,
            weight=weight,first=first,second=second,output=output)
    elif entry==0x777FA:
        saved(context[13]);saved(context[14],8)
        primary=bool(calibration[0x83C1][0]&1);external=bool(calibration[0x89C5][0]&1);flags=bool(u(0x41A6)&8)
        first=s(0x3488,2);upper=s(0x348C,2);third=s(0x3486,2);fourth=s(0x348A,2)
        cap=s(0x34C8,2);other=s(0x4162,2)
        register(1,RAM_BASE+0x28F8);register(2,0x83C1);t=False
        if not primary:
            register(2,0x89C5);register(4,RAM_BASE+0x41A5);register(6,int(external))
            first=first if external else s(0x34A0,2)
            if flags:
                if external:first=other
                upper=min(other,cap);third=fourth=s(0x349C,2);register(6,other);t=other>cap
            else:
                upper=min(upper,cap);register(2,upper);t=s(0x348C,2)>cap
        register(0,0xB8A);register(5,third);register(7,upper)
        put(0x3480,first,2);put(0x3484,upper,2);put(0x347E,third,2);put(0x3482,fourth,2)
        branch(0x77816,primary,0x77864);branch(0x77826,not flags,0x77850)
        branch(0x7782A,not external,0x77834);jump(0x77830,0x77838)
        branch(0x77844,other>cap,0x77848);jump(0x7784C,0x77864)
        branch(0x77852,external,0x77858);branch(0x7785E,s(0x348C,2)>cap,0x77862)
        returns(0x77876);tags.update(primary=primary,external=external,flags=flags,first=first,
            upper=upper,third=third,fourth=fourth,cap=cap,other=other)
    elif entry==0x907E8:
        active=bool(context[4]&255);index=context[5]&255;mode=u(0x2327);request=u(0x1AAC+index*2,2)
        latch=u(0x2568+index);ready=bool((index+1)&u(0x14B8));flags=u(0x14F0)
        reset=not active or mode!=128 or request!=0;set_flag=not reset and not latch and not ready
        register(4,context[4]&255);register(1,index);register(7,index+1)
        if active and mode==128:register(4,RAM_BASE+0x128C)
        if reset:
            put(0x1930+index,0);put(0x14F0,flags&~(index+1));put(0x2568+index,calibration[0x8E1A][0])
            register(0,index);register(2,RAM_BASE+0x2568);register(5,0x8E1A)
            register(6,signed(calibration[0x8E1A][0],8));t=not active
        elif set_flag:
            put(0x14F0,flags|(index+1));register(0,0x264);register(2,s(0x14F0)|(index+1))
            register(5,RAM_BASE+0x128C);register(6,u(0x14B8));t=True
        else:
            put(0x1930+index,0);put(0x14F0,flags&~(index+1))
            register(0,0x264);register(2,~(index+1));register(4,RAM_BASE+0x1930)
            register(5,RAM_BASE+0x128C);register(6,s(0x14F0)&~(index+1));t=False
        branch(0x907F0,not active,0x90854,True);branch(0x90800,mode!=128,0x90854)
        branch(0x90812,request!=0,0x90854);branch(0x9081E,latch!=0,0x9083E)
        branch(0x9082E,not ready,0x9087A);jump(0x9083A,0x9084A)
        returns(0x90850,0x90876,0x90880)
        tags.update(active=active,index=index,mode=mode,request=request,latch=latch,ready=ready,
            flags=flags,reset=reset,set_flag=set_flag)
    else:raise ValueError('the gated scalar equations name an undeclared natural entry')
    sr=(sr_before&~1)|int(t);path,branches=control_path(entry,controls,continuation)
    return dict(entry=entry,registers=tuple(registers),sr=sr,gbr=context[15],mach=context[16],macl=context[17],
        pr=continuation,sp=sp,frame=bytes(frame),ram=bytes(ram),path=path,branches=branches,tags=tags,
        exit=(sr,continuation,context[17],context[16],context[15],*reversed(registers)))
