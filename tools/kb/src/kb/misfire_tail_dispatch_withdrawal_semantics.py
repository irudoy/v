"""Separate hysteresis, threshold, counter and real-tail state equations."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose complete real leaf paths without decoding instructions."""
    if (type(entry) is not int or entry!=0x7C494
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(value) is not int or not 0<=value<=MASK for value in context)):
        raise ValueError('the misfire tail equations require complete CPU, RAM and frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];locals_saved=[]
    stack=sp;pr=continuation;sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the misfire tail equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex())

    def read(site,address,register,width=1):
        spans=[(first,data) for first,data in calibration.items() if first<=address and address+width<=first+len(data)]
        if len(spans)!=1:raise ValueError('the misfire tail equation loses a unique exact calibration preimage')
        first,data=spans[0];raw=data[address-first:address-first+width]
        event(site,'read',address,width,register,'rom',raw)
        return int.from_bytes(raw,'big')

    def frame_access(site,mode,address,width,register,value=None):
        offset=160+address-sp
        if mode=='write':frame[offset:offset+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big')
        raw=bytes(frame[offset:offset+width]);event(site,mode,address,width,register,'frame',raw)
        return int.from_bytes(raw,'big')

    def push(site,value,register=None):
        nonlocal stack
        stack-=4;frame_access(site,'write',stack,4,register,value)

    def pop(site,register=None):
        nonlocal stack
        value=frame_access(site,'read',stack,4,register);stack+=4;return value

    def load(site,address,width,register):
        raw=bytes(ram[address:address+width]);event(site,'read',RAM_BASE+address,width,register,'ram',raw)
        return signed(int.from_bytes(raw,'big'),width*8)&MASK

    def put(site,address,width,register,value):
        ram[address:address+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big')
        event(site,'write',RAM_BASE+address,width,register,'ram',bytes(ram[address:address+width]))

    def t(value):
        nonlocal sr
        sr=(sr&~1)|int(bool(value))

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

    def hysteresis(row):
        emit(0x7C4E0,0x7C4F4)
        r[1]=RAM_BASE+0x4094;r[4]=RAM_BASE+0x24C4;r[0]=0x16;r[2]=RAM_BASE+0x119C
        r[5]=load(0x7C4E8,0x24C4,1,5);r[6]=load(0x7C4EA,0x11B2,1,6);r[0]=r[5]
        old_set=bool(r[0]&128);t(not old_set);branch(0x7C4F0,not old_set,0x7C4F6,True)
        r[6]&=255
        if old_set:emit(0x7C4F4);r[6]+=4
        emit(0x7C4F6,0x7C504);r[7]=0x8BDA;r[0]=r[5]
        threshold=read(0x7C4FA,0x8BDA,2);r[2]=threshold
        admitted=r[6]>=threshold;t(admitted);branch(0x7C500,admitted,0x7C506,True);r[0]|=128
        if not admitted:emit(0x7C504);r[0]&=127
        emit(0x7C506,0x7C50E);put(0x7C506,0x24C4,1,0,r[0]);r[0]=signed(r[0]&255,8)&MASK
        clear=not bool(r[0]&128);t(clear);branch(0x7C50C,clear,0x7C520)
        if clear:
            emit(0x7C520,0x7C526);r[0]=0;put(0x7C524,0x4096,1,0,r[0])
            control(0x7C522,'return',pr,True);returned(row,0x7C522)
        else:
            emit(0x7C50E,0x7C51A);r[0]=load(0x7C50E,0x4096,1,0);r[5]=255;r[6]=r[0]&255
            full=r[6]>=255;t(full);branch(0x7C518,full,0x7C526)
            if full:
                emit(0x7C526,0x7C52A);control(0x7C526,'return',pr,True);returned(row,0x7C526)
            else:
                emit(0x7C51A,0x7C520);r[6]+=1;r[0]=r[6];control(0x7C51C,'jump',0x7C522,True)
                emit(0x7C522,0x7C526);put(0x7C524,0x4096,1,0,r[0])
                control(0x7C522,'return',pr,True);returned(row,0x7C522)
        lookups.append(dict(kind='hysteresis-and-saturated-byte-counter',old_set=old_set,
            promoted_coordinate=(memory[0x11B2]+(4 if old_set else 0)),threshold=threshold,
            admitted=admitted,counter=ram[0x4096],returned_R0=r[0]))

    def tail_window():
        nonlocal macl
        emit(0x872DE,0x872F4);r[5]=0x8354;r[4]=200
        r[0]=load(0x872E4,0x409E,2,0);r[2]=read(0x872E6,0x8354,2);r[6]=r[0]&65535
        macl=r[2]*200;r[2]=macl;first_threshold=macl
        reset=r[6]>=r[2];t(reset);branch(0x872F2,not reset,0x87302)
        if reset:
            emit(0x872F4,0x87302);r[6]=RAM_BASE+0x4240;r[0]=0;put(0x872F8,0x409E,2,0,0)
            r[0]=load(0x872FA,0x4241,1,0);r[5]=RAM_BASE+0x4240;r[0]|=32;put(0x87300,0x4241,1,0,r[0])
        lookups.append(dict(kind='first-word-threshold',threshold=first_threshold,reset=reset))
        emit(0x87302,0x8730C);r[0]=load(0x87302,0x40A0,2,0);r[6]=1000;r[2]=r[0]&65535
        reset=r[2]>=r[6];t(reset);branch(0x8730A,not reset,0x8731A)
        if reset:
            emit(0x8730C,0x8731A);r[6]=RAM_BASE+0x4240;r[0]=0;put(0x87310,0x40A0,2,0,0)
            r[0]=load(0x87312,0x4241,1,0);r[5]=RAM_BASE+0x4240;r[0]|=128;put(0x87318,0x4241,1,0,r[0])
        lookups.append(dict(kind='second-word-threshold',threshold=1000,reset=reset))
        emit(0x8731A,0x8732C);r[5]=0x8656;r[0]=load(0x8731C,0x40A2,2,0)
        r[2]=read(0x8731E,0x8656,2);r[7]=r[0]&65535;macl=r[2]*200;r[2]=macl;third_threshold=macl
        reset=r[7]>=r[2];t(reset);branch(0x8732A,not reset,0x8733C)
        if reset:
            emit(0x8732C,0x8733C);r[6]=RAM_BASE+0x4240;r[7]=r[0]=0;put(0x87332,0x40A2,2,0,0)
            r[0]=load(0x87334,0x4241,1,0);r[5]=RAM_BASE+0x4240;r[0]|=64;put(0x8733A,0x4241,1,0,r[0])
        lookups.append(dict(kind='third-word-threshold',threshold=third_threshold,reset=reset))
        emit(0x8733C,0x87346);r[6]=RAM_BASE+0x4240;r[0]=0x11;r[0]=load(0x87340,0x4251,1,0)
        reset_all=not bool(r[0]&128);t(reset_all);branch(0x87344,reset_all,0x87390)
        if not reset_all:
            emit(0x87346,0x87350);r[6]=RAM_BASE+0x41A9;r[0]=0x29;r[0]=load(0x8734A,0x41D2,1,0)
            reset_all=not bool(r[0]&2);t(reset_all);branch(0x8734E,reset_all,0x87390)
        if not reset_all:
            emit(0x87350,0x87354);reset_all=not bool(r[0]&1);t(reset_all);branch(0x87352,reset_all,0x87390)
        if reset_all:
            emit(0x87390,0x87398);r[0]=0
            put(0x87392,0x409E,2,0,0);put(0x87394,0x40A0,2,0,0);put(0x87396,0x40A2,2,0,0)
            return
        emit(0x87354,0x87362);r[6]=RAM_BASE+0x36D8;r[0]=0x15C;r[2]=load(0x8735A,0x3834,1,2);r[6]=31
        enough=r[2]>=r[6];t(enough);branch(0x87360,not enough,0x87398)
        lookups.append(dict(kind='sign-extended-byte-unsigned-comparison',raw=ram[0x3834],
            full_register=r[2],threshold=31,admitted=enough))
        if not enough:return
        emit(0x87362,0x8736E);r[6]=RAM_BASE+0x43C7;r[0]=0x86;r[2]=load(0x87368,0x444D,1,2)
        blocked=bool(r[2]);t(not blocked);branch(0x8736C,blocked,0x8737E)
        if not blocked:
            emit(0x8736E,0x8737E)
            r[0]=load(0x8736E,0x409E,2,0);locals_saved.append((0x87370,stack,r[0]))
            frame_access(0x87370,'write',stack,4,0,r[0]);r[0]=(r[0]+1)&MASK;put(0x87374,0x409E,2,0,r[0])
            r[0]=load(0x87376,0x40A0,2,0);locals_saved.append((0x87378,stack+4,r[0]))
            frame_access(0x87378,'write',stack+4,4,0,r[0]);r[0]=(r[0]+1)&MASK;put(0x8737C,0x40A0,2,0,r[0])
        emit(0x8737E,0x8738A);r[6]=RAM_BASE+0x43C7;r[0]=0x85;r[2]=load(0x87384,0x444C,1,2)
        blocked=bool(r[2]);t(not blocked);branch(0x87388,blocked,0x87398)
        if not blocked:
            emit(0x8738A,0x87390);r[7]=(r[7]+1)&MASK;r[0]=r[7];control(0x8738C,'jump',0x87396,True)
            emit(0x87396);put(0x87396,0x40A2,2,0,r[0])

    emit(0x7C494,0x7C49A);push(0x7C494,pr);hysteresis(call(0x7C496,0x7C4E0))
    emit(0x7C49A,0x7C4A0);r[2]=0x872D0;pr=pop(0x7C49E);control(0x7C49C,'jump',0x872D0,True)
    emit(0x872D0,0x872DE);push(0x872D0,macl);r[1]=RAM_BASE+0x4094;stack-=8;r[6]=0x186C8
    r[0]=signed(read(0x872D8,0x186CE,0),8)&MASK;disabled=not bool(r[0]&128)
    t(disabled);branch(0x872DC,disabled,0x87398)
    if not disabled:tail_window()
    emit(0x87398,0x8739E);stack+=8;macl=pop(0x8739C);control(0x8739A,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={index:value&MASK for index,value in enumerate(r)},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        local_counter_preimages=tuple(locals_saved),sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,
        mach=context[16],macl=macl,output=r[0],tail_disabled=disabled,
        byte_counter=ram[0x4096],word_counters=tuple(int.from_bytes(ram[at:at+2],'big') for at in (0x409E,0x40A0,0x40A2)),
        preincrement_word_overflow_excluded_by_exact_raw_threshold_bounds=True)
