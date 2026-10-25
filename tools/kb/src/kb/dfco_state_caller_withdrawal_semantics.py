"""Separate DFCO state,restore threshold,indexed byte,saved frame and real helper equations."""
from kb.arrogant_catfish_semantics import curve as byte_curve_equation

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry not in (0x503E0,0x50018)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the DFCO state caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the DFCO state caller equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the DFCO state caller equation loses one authoritative physical preimage')
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

    def byte(site,address,register):return signed(read(site,address,register,1),8)&MASK

    def rotation(row):
        emit(0x50766,0x5076E);incoming=r[4]&255;r[0]=incoming;r[2]=0;t(incoming==1)
        branch(0x5076A,incoming==1,0x50796,True)
        if incoming==1:
            emit(0x50796);r[2]=2
        else:
            matched=False
            for site,number,target,next_mask in ((0x5076E,2,0x50792,4),(0x50772,4,0x5078E,8),
                    (0x50776,8,0x5078A,16),(0x5077A,16,0x50786,32)):
                emit(site,site+4);equal=incoming==number;t(equal);branch(site+2,equal,target)
                if equal:
                    emit(target,target+4);r[2]=next_mask;control(target,'jump',0x50798,True);matched=True;break
            if not matched:
                emit(0x5077E,0x50782);equal=incoming==32;t(equal);branch(0x50780,not equal,0x50798)
                if equal:
                    emit(0x50782,0x50786);r[2]=1;control(0x50782,'jump',0x50798,True)
        emit(0x50798,0x5079C);r[0]=r[2]&255
        control(0x50798,'return',pr,True);returned(row,0x50798)

    def clear_counts(first):
        emit(first,first+16);r[0]=0x6AE;r[2]=MASK;put(first+4,0x193A,1,2,r[2])
        r[2]=0;r[0]=0x6AC;put(first+10,0x1938,1,2,0);r[0]=0x6AB;put(first+14,0x1937,1,2,0)

    def ordinary_clear_counts():
        emit(0x5059E,0x505AE);r[0]=0x6AE;r[2]=MASK;put(0x505A2,0x193A,1,2,r[2]);r[2]=0
        r[0]=0x6AC;put(0x505A8,0x1938,1,2,0);r[0]=0x6AB;put(0x505AC,0x1937,1,2,0)

    def state_transition():
        nonlocal macl
        emit(0x50418,0x5041E);r[0]=r[11];four=r[0]==4;t(four);branch(0x5041C,not four,0x50436)
        if four:
            emit(0x5041E,0x50426);r[5]=RAM_BASE+0x2458;r[0]=load(0x50420,0x2458,1,0)
            cutoff=bool(r[0]&32);t(not cutoff);branch(0x50424,not cutoff,0x50436)
            if cutoff:
                emit(0x50426,0x50432);r[2]=RAM_BASE+0x1068;r[3]=0x8A40
                r[0]=load(0x5042A,0x106A,1,0);r[2]=byte(0x5042C,0x8A40,2)
                cutoff=r[0]>=r[2];t(cutoff);branch(0x50430,not cutoff,0x50436)
                if cutoff:
                    emit(0x50432,0x50436);control(0x50432,'jump',0x505F4,True);emit(0x505F4);r[11]=0;return False
        emit(0x50436,0x5043C);r[5]=2;later=r[11]>2;t(later);branch(0x5043A,later,0x504CA)
        if not later:
            emit(0x5043C,0x50440);active=r[12]!=0;t(not active);branch(0x5043E,not active,0x50484)
            if active:
                emit(0x50440,0x50444);r[11]=0;control(0x50440,'jump',0x50498,True)
            else:
                emit(0x50484,0x50488);active=r[4]!=0;t(not active);branch(0x50486,not active,0x50498)
                if active:
                    emit(0x50488,0x5048C);zero=r[11]==0;t(zero);branch(0x5048A,not zero,0x50498)
                    if zero:
                        emit(0x5048C,0x50498);r[5]=stack+2;r[0]=signed(frame_access(0x50490,'read',stack+2,1,0),8)&MASK
                        r[11]=1;r[4]=RAM_BASE+0x256A;put(0x50496,0x2571,1,0,r[0])
            emit(0x50498,0x504A0);r[11]&=255;r[0]=r[11];one=r[0]==1;t(one);branch(0x5049E,not one,0x504B2)
            if one:
                emit(0x504A0,0x504A8);r[4]=RAM_BASE+0x256A;r[0]=load(0x504A2,0x2571,1,0)
                zero=r[0]==0;t(zero);branch(0x504A6,not zero,0x504B2)
                if zero:
                    emit(0x504A8,0x504B2);r[5]=stack+2;r[0]=signed(frame_access(0x504AC,'read',stack+3,1,0),8)&MASK
                    r[11]=2;put(0x504B0,0x2572,1,0,r[0])
            emit(0x504B2,0x504BA);r[11]&=255;r[0]=r[11];two=r[0]==2;t(two);branch(0x504B8,two,0x504BE)
            if not two:
                emit(0x504BA,0x504BE);control(0x504BA,'jump',0x505AE,True);return True
            emit(0x504BE,0x504C6);r[4]=RAM_BASE+0x256A;r[0]=load(0x504C0,0x2572,1,0)
            zero=r[0]==0;t(zero);branch(0x504C4,not zero,0x505AE)
            if zero:
                emit(0x504C6,0x504CA);r[11]=3;control(0x504C6,'jump',0x505AE,True)
            return True
        emit(0x504CA,0x504CE);first=r[4]!=0;t(not first);branch(0x504CC,not first,0x504D6)
        if first:
            emit(0x504CE,0x504D2);second=r[12]!=0;t(not second);branch(0x504D0,second,0x504D6)
            if not second:
                emit(0x504D2,0x504D6);r[11]=3;control(0x504D2,'jump',0x5059E,True);ordinary_clear_counts();return True
        emit(0x504D6,0x504DA);active=r[12]!=0;t(not active);branch(0x504D8,not active,0x505AE)
        if not active:return True
        emit(0x504DA,0x504E0);r[0]=r[11];three=r[0]==3;t(three);branch(0x504DE,not three,0x505AE)
        if not three:return True
        emit(0x504E0,0x504E8);r[5]=RAM_BASE+0x2458;r[0]=load(0x504E2,0x2458,1,0)
        bypass=bool(r[0]&32);t(not bypass);branch(0x504E6,bypass,0x50596)
        if not bypass:
            emit(0x504E8,0x504F0);r[2]=0x8711;r[0]=byte(0x504EA,0x8711,0)
            active=bool(r[0]&2);t(not active);branch(0x504EE,active,0x50500)
            if not active:
                emit(0x504F0,0x504F8);r[5]=0x8B3F;r[0]=byte(0x504F2,0x8B3F,0)
                bypass=bool(r[0]&128);t(not bypass);branch(0x504F6,bypass,0x50596)
                if not bypass:
                    emit(0x504F8,0x50500);r[5]=RAM_BASE+0x24CE;r[0]=load(0x504FA,0x24CF,1,0)
                    bypass=(r[0]&16)==0;t(bypass);branch(0x504FE,bypass,0x50596)
        if bypass:
            emit(0x50596,0x5059E);r[4]=RAM_BASE+0x256A;r[0]=r[7];r[11]=4;put(0x5059C,0x2573,1,0,r[0])
            ordinary_clear_counts();return True
        emit(0x50500,0x50510);r[2]=RAM_BASE+0x119C;r[0]=0x17;r[4]=0x8C1A
        r[5]=load(0x50506,0x11B3,1,5);r[0]=byte(0x50508,0x8C1E,0)
        above=r[5]>r[0];t(above);r[11]=0;branch(0x5050C,above,0x5058E,True)
        if above:
            emit(0x5058E,0x50596);r[0]=0x6AD;r[2]=10;put(0x50594,0x1939,1,2,10)
            control(0x50592,'jump',0x5059E,True);ordinary_clear_counts();return True
        emit(0x50510,0x50518);r[5]=0x8B3F;r[0]=byte(0x50512,0x8B3F,0)
        product=bool(r[0]&128);t(not product);branch(0x50516,not product,0x5054A)
        index=0
        if product:
            emit(0x50518,0x50534);r[3]=RAM_BASE+0x119C;r[2]=RAM_BASE+0x1094;r[0]=load(0x5051C,0x11B6,2,0)
            r[1]=0x8C1A;r[4]=r[0]&65535;r[0]=0x7A;r[7]=load(0x50524,0x110E,1,7);r[0]=byte(0x50526,0x8C1D,0)
            r[7]&=255;r[2]=r[0]&255;macl=r[7]*r[2];r[2]=macl;above=r[4]>r[2];t(above);branch(0x50532,not above,0x5056E)
            if not above:index=2
            else:
                emit(0x50534,0x50546);r[3]=RAM_BASE+0x119C;r[0]=load(0x50536,0x11B6,2,0);r[4]=r[0]&65535
                r[0]=byte(0x5053A,0x8C1C,0);r[2]=r[0]&255;macl=r[7]*r[2];r[2]=macl;above=r[4]>r[2];t(above);branch(0x50544,not above,0x5056A)
                if not above:index=1
                else:emit(0x50546,0x5054A);control(0x50546,'jump',0x50570,True)
        else:
            emit(0x5054A,0x50552);r[0]=0x28B;r[3]=0x8C1A;control(0x5054E,'jump',0x50554,True)
            emit(0x50554,0x50560);r[4]=load(0x50554,0x1517,1,4)&255;r[2]=byte(0x50556,0x8C1A,2)&255
            above=r[4]>=r[2];t(above);branch(0x5055E,above,0x5056E)
            if above:index=2
            else:
                emit(0x50560,0x5056A);r[3]=0x8C1A;r[0]=byte(0x50562,0x8C1B,0);r[2]=r[0]&255
                above=r[4]>=r[2];t(above);branch(0x50568,not above,0x50570)
                if above:index=1
        if index==1:
            emit(0x5056A,0x5056E);r[6]=1;control(0x5056A,'jump',0x50570,True)
        elif index==2:emit(0x5056E);r[6]=2
        emit(0x50570,0x5058E);r[0]=0x6AD;r[5]=0x1269D;put(0x50574,0x1939,1,6,r[6]);r[6]&=255;r[0]=r[6]
        r[2]=byte(0x5057A,0x1269D+r[6],2);r[0]=0x6AE;r[5]=0x1269A;put(0x50580,0x193A,1,2,r[2]);r[0]=r[6]
        r[2]=byte(0x50584,0x1269A+r[6],2);r[6]=MASK;r[0]=0x6AC;put(0x5058C,0x1938,1,2,r[2]);control(0x5058A,'jump',0x505AE,True)
        return True

    def restore():
        nonlocal gbr,pr,stack

        def diagnostic(row):
            emit(0x25C36,0x25C3E);r[1]=RAM_BASE+0x5718;r[0]=signed(r[4]&65535,16)&MASK
            sentinel=r[0]==MASK;t(sentinel);branch(0x25C3C,sentinel,0x25C54)
            if sentinel:
                emit(0x25C54);r[2]=0
            else:
                emit(0x25C3E,0x25C54);r[6]=r[1];r[2]=(r[0]*3)&MASK;r[6]=(r[6]+r[2])&MASK
                r[0]=load(0x25C48,(r[6]-RAM_BASE+2)&65535,1,0)
                t(not r[0]&32);r[0]=int(bool(sr&1))^1;r[2]=r[0]&255
                control(0x25C50,'jump',0x25C56,True)
            emit(0x25C56,0x25C5A);r[0]=r[2];control(0x25C56,'return',pr,True);returned(row,0x25C56)

        def curve(row):
            base,coordinate=r[4],r[5]&255
            spans=[(at,data) for at,data in calibration.items() if at<=base and base+16<=at+len(data)]
            if len(spans)!=1:raise ValueError('the restore lookup loses its complete sixteen-byte physical input')
            at,data=spans[0];raw=data[base-at:base-at+16];value=byte_curve_equation(raw,coordinate)
            emit(0x26388,0x26390);r[0]=240;r[5]=coordinate;endpoint=coordinate>=240;t(endpoint)
            branch(0x2638E,endpoint,0x26396)
            if endpoint:
                emit(0x26396,0x2639A);r[0]=signed(read(0x26398,base+15,0,1),8)&MASK
                control(0x26396,'return',pr,True);returned(row,0x26396)
                lookups.append(dict(value,site=row['site'],base=base,index=15,fraction=0,endpoint=True))
                return
            emit(0x26390,0x26396);r[6]=0x26A84;r[3]=0;control(0x26392,'jump',0x26A84,True)
            emit(0x26A84,0x26A9C);index,remainder=divmod(coordinate,16)
            r[5]=index;r[3]=remainder<<12;r[0]=0;t(True);branch(0x26A9A,True,0x26AAA)
            emit(0x26AAA,0x26ABA);r[4]=base+index
            r[1]=signed(read(0x26AAC,r[4],1,1),8)&MASK
            r[0]=signed(read(0x26AAE,r[4]+1,0,1),8)&MASK;r[2]=r[0]&255;r[0]=r[1]&255;r[6]=0x26740
            control(0x26AB6,'jump',0x26740,True)
            first,second=raw[index:index+2];ascending=second>=first;magnitude=abs(second-first)*remainder//16
            emit(0x26740,0x26744);t(ascending);branch(0x26742,ascending,0x2675C)
            if ascending:
                emit(0x2675C,0x2676E);r[1]=macl;r[2]=magnitude;r[0]=value['value'];terminal=0x2676A
            else:
                emit(0x26744,0x2675C);push(0x26744,first,0);r[1]=macl;pop(0x26752,2)
                r[2]=r[0]=value['value'];terminal=0x26758
            control(terminal,'return',pr,True);returned(row,terminal)
            lookups.append(dict(value,site=row['site'],base=base,index=index,fraction=remainder<<12,
                endpoint=False,ascending=ascending,magnitude=magnitude))

        def jump(site,target):
            emit(site,site+4);control(site,'jump',target,True)

        def gates():
            emit(0x50046,0x5004A);zero=r[0]==0;t(zero);branch(0x50048,zero,0x5004E)
            if not zero:jump(0x5004A,0x5017A);return False
            emit(0x5004E,0x50056);r[5]=RAM_BASE+0x424C;r[0]=load(0x50050,0x4250,1,0)
            zero=not r[0]&64;t(zero);branch(0x50054,zero,0x5005A)
            if not zero:jump(0x50056,0x5017A);return False
            emit(0x5005A,0x50062);r[6]=0x25C36;r[4]=0x012A;row=call(0x5005E,0x25C36);diagnostic(row)
            emit(0x50062,0x50066);zero=r[0]==0;t(zero);branch(0x50064,zero,0x5006A)
            if not zero:jump(0x50066,0x5017A);return False
            emit(0x5006A,0x50076);r[5]=RAM_BASE+0x41A9;r[0]=40;r[2]=load(0x5006E,0x41D1,1,2);r[0]=r[2]
            zero=not r[0]&128;t(zero);branch(0x50074,zero,0x5007A)
            if not zero:jump(0x50076,0x5017A);return False
            emit(0x5007A,0x50080);r[0]=r[2];zero=not r[0]&4;t(zero);branch(0x5007E,zero,0x50084)
            if not zero:jump(0x50080,0x5017A);return False
            emit(0x50084,0x5008C);r[0]=39;r[0]=load(0x50086,0x41D0,1,0)
            zero=not r[0]&1;t(zero);branch(0x5008A,not zero,0x5017A)
            if not zero:return False
            emit(0x5008C,0x50092);r[0]=r[2];zero=not r[0]&1;t(zero);branch(0x50090,not zero,0x5017A)
            if not zero:return False
            emit(0x50092,0x5009C);r[6]=RAM_BASE+0x4558;r[0]=0x389;r[2]=load(0x50096,0x48E1,1,2)
            zero=r[2]==0;t(zero);branch(0x5009A,not zero,0x5017A)
            if not zero:return False
            emit(0x5009C,0x500A4);r[6]=RAM_BASE+0x245C;r[0]=load(0x5009E,0x245D,1,0)
            zero=not r[0]&2;t(zero);branch(0x500A2,not zero,0x5017A)
            return zero

        def threshold_lookups():
            emit(0x500A4,0x500B0);r[3]=RAM_BASE+0x1068;r[4]=0x1298C
            r[0]=load(0x500A8,0x106F,1,0);r[6]=0x26388;r[5]=r[0]&255;row=call(0x500AC,0x26388);curve(row)
            emit(0x500B0,0x500C0);r[1]=RAM_BASE+0x1068;r[2]=r[0]&255;r[4]=0x12818
            r[0]=load(0x500B6,0x106F,1,0);r[6]=0x26388;r[5]=r[0]&255
            frame_access(0x500BE,'write',stack+4,4,2,r[2]);row=call(0x500BC,0x26388);curve(row)
            emit(0x500C0,0x500CC);r[6]=RAM_BASE+0x424C;r[2]=r[0]&255
            frame_access(0x500C4,'write',stack+8,4,2,r[2]);r[0]=load(0x500C6,0x4250,1,0)
            offset=bool(r[0]&128);t(not offset);branch(0x500CA,not offset,0x5010C)
            if offset:
                emit(0x500CC,0x500DE);r[2]=0x84E8;r[6]=255;r[5]=frame_access(0x500D0,'read',stack+4,4,5)
                r[4]=byte(0x500D4,0x84E8,4)&255;r[5]+=r[4];above=r[5]>255;t(above);branch(0x500DC,not above,0x500E2)
                if above:jump(0x500DE,0x500E6);r[2]=r[6]
                else:emit(0x500E2,0x500E6);r[2]=frame_access(0x500E2,'read',stack+4,4,2)+r[4]
                emit(0x500E6,0x500F0);r[3]=frame_access(0x500E6,'read',stack+8,4,3)+r[4]
                above=r[3]>255;t(above);branch(0x500EC,not above,0x500F4,True)
                frame_access(0x500EE,'write',stack+4,4,2,r[2])
                if above:jump(0x500F0,0x500F8);r[2]=r[6]
                else:emit(0x500F4,0x500F8);r[2]=frame_access(0x500F4,'read',stack+8,4,2)+r[4]
                emit(0x500F8,0x50102);frame_access(0x500F8,'write',stack+8,4,2,r[2]);r[2]=r[13]+r[4]
                above=r[2]>255;t(above);branch(0x50100,not above,0x50106)
                if above:jump(0x50102,0x5010A);r[2]=r[6]
                else:emit(0x50106,0x5010A);r[13]+=r[4];r[2]=r[13]
                emit(0x5010A);r[13]=r[2]
            emit(0x5010C,0x5011E);r[3]=RAM_BASE+0x1068;r[1]=0x11CB5;r[0]=load(0x50110,0x106A,1,0)
            r[2]=byte(0x50112,0x11CB5,2);r[4]=r[0]&255;r[2]&=255
            inside=r[4]>=r[2];t(inside);branch(0x5011A,not inside,0x50138,True);r[5]=0
            if inside:
                emit(0x5011E);r[14]=3
                while True:
                    emit(0x50120,0x50126);r[5]&=255;complete=r[5]>=r[14];t(complete);branch(0x50124,complete,0x50138)
                    if complete:break
                    emit(0x50126,0x50138);r[5]=(r[5]+1)&255;r[3]=0x11CB5;r[0]=r[5]
                    r[2]=byte(0x5012E,0x11CB5+r[0],2);r[4]&=255;r[2]&=255
                    inside=r[4]>=r[2];t(inside);branch(0x50136,inside,0x50120)
                    if not inside:break
            emit(0x50138,0x50146);r[6]=0x1299C;r[0]=r[5]&255;r[5]=frame_access(0x5013C,'read',stack+4,4,5)
            r[2]=byte(0x5013E,0x1299C+r[0],2);r[6]=r[2]&255;above=r[5]>=r[6];t(above);branch(0x50144,above,0x50152)
            if above:emit(0x50152);r[4]=frame_access(0x50152,'read',stack+4,4,4)
            else:jump(0x50146,0x50154);r[4]=r[6]
            emit(0x50154,0x5015A);r[2]=frame_access(0x50154,'read',stack+8,4,2)
            above=r[2]>=r[6];t(above);branch(0x50158,not above,0x5015C)
            if above:emit(0x5015A);r[6]=r[2]
            emit(0x5015C,0x50166);r[14]=r[6];r[6]=RAM_BASE+0x24CE;r[0]=load(0x50160,0x24CF,1,0)
            skip=bool(r[0]&16);t(not skip);branch(0x50164,skip,0x501A4)
            if skip:return
            emit(0x50166,0x5016E);r[0]=byte(0x50166,0x8A3F,0);r[6]=r[0]&255
            above=r[4]>=r[6];t(above);branch(0x5016C,above,0x50170)
            if not above:emit(0x5016E);r[4]=r[6]
            emit(0x50170,0x50174);above=r[14]>=r[6];t(above);branch(0x50172,not above,0x50176)
            if above:emit(0x50174);r[6]=r[14]
            jump(0x50176,0x501A4);r[14]=r[6]

        def fallback():
            emit(0x5017A,0x50188);r[0]=byte(0x5017A,0x8A3E,0);r[6]=RAM_BASE+0x424C;r[14]=r[0]&255
            r[0]=load(0x50180,0x4250,1,0);offset=bool(r[0]&128);t(not offset);branch(0x50184,not offset,0x501A4,True);r[4]=r[14]
            if not offset:return
            emit(0x50188,0x5019A);r[2]=0x84E8;r[6]=255;r[5]=byte(0x5018E,0x84E8,5)&255
            r[2]=r[13]+r[5];above=r[2]>255;t(above);branch(0x50198,not above,0x5019E)
            if above:jump(0x5019A,0x501A2);r[2]=r[6]
            else:emit(0x5019E,0x501A2);r[13]+=r[5];r[2]=r[13]
            emit(0x501A2);r[13]=r[2]

        def rpm_pair(first,first_register,second_site,second_register,last_jump):
            emit(first,first+8);r[0]=load(first,0x11B3,1,0);r[6]=r[0]&255
            above=r[6]>r[first_register];t(above);branch(first+6,not above,0x50360)
            if not above:return 3
            emit(second_site,second_site+4);above=r[6]>r[second_register];t(above);branch(second_site+2,not above,0x50360)
            if not above:return 3
            jump(last_jump,0x50378);return 0

        def common_flags(first):
            delay=first+6;target=0x5031E if first==0x50308 else 0x5035A
            emit(first,first+8);r[0]=r[2];high=bool(r[0]&128);t(not high)
            branch(first+4,not high,target,True);r[0]=load(delay,0x11B3,1,0)
            if high:
                emit(first+8,first+14);r[6]=r[0]&255;above=r[6]>r[13];t(above);branch(first+12,not above,0x50360)
                if not above:return 3
                emit(first+14,first+18);above=r[6]>r[14];t(above);branch(first+16,not above,0x50360)
                if not above:return 3
                jump(first+18,0x50378);return 0
            emit(target,target+6);r[2]=r[0]&255;above=r[2]>r[14];t(above)
            if first==0x50308:
                branch(target+4,not above,0x50360)
                if not above:return 3
                jump(0x50324,0x50378);return 0
            branch(target+4,above,0x50378)
            return 0 if above else 3

        def classification():
            emit(0x501BA,0x501C4);r[6]=RAM_BASE+0x244C;r[0]=load(0x501BC,0x2458,1,0)
            active=bool(r[0]&32);t(not active);branch(0x501C0,active,0x501C8,True);r[2]=r[0]
            if not active:jump(0x501C4,0x50366);return 1
            emit(0x501C8,0x501D4);r[5]=RAM_BASE+0x1094;r[0]=0x7A;r[6]=load(0x501CC,0x110E,1,6);r[5]=r[6]&255
            fast=r[5]>=r[12];t(fast);branch(0x501D2,fast,0x501EC)
            if not fast:
                emit(0x501D4,0x501DC);r[0]=load(0x501D4,0x11B3,1,0);r[6]=r[0]&255
                above=r[6]>r[14];t(above);branch(0x501DA,above,0x501E0)
                if not above:jump(0x501DC,0x50360);return 3
                emit(0x501E0,0x501E4);above=r[6]>r[4];t(above);branch(0x501E2,above,0x501E8)
                if not above:jump(0x501E4,0x50340);return 2
                jump(0x501E8,0x50378);return 0
            emit(0x501EC,0x501FC);r[6]=0x8B3F;r[0]=byte(0x501EE,0x8B3F,0)&128;r[6]=0x870C;r[5]=r[0]
            r[0]=byte(0x501F6,0x870C,0);alternate=bool(r[0]&128);t(not alternate);branch(0x501FA,not alternate,0x50200)
            if alternate:
                jump(0x501FC,0x50328)
                emit(0x50328,0x5032C);zero=r[5]==0;t(zero);branch(0x5032A,zero,0x50344)
                if not zero:
                    emit(0x5032C,0x50334);r[5]=RAM_BASE+0x244C;r[0]=load(0x5032E,0x2450,1,0)
                    skip=bool(r[0]&64);t(not skip);branch(0x50332,skip,0x50344)
                    if not skip:
                        emit(0x50334,0x5033C);r[0]=load(0x50334,0x11B3,1,0);r[6]=r[0]&255
                        above=r[6]>r[14];t(above);branch(0x5033A,not above,0x50360)
                        if not above:return 3
                        emit(0x5033C,0x50340);above=r[6]>r[4];t(above);branch(0x5033E,above,0x50378)
                        return 0 if above else 2
                return common_flags(0x50344)
            emit(0x50200,0x50204);zero=r[5]==0;t(zero);branch(0x50202,zero,0x50208)
            common=not zero
            if common:jump(0x50204,0x502EC)
            else:
                emit(0x50208,0x50210);r[7]=RAM_BASE+0x24CE;r[0]=load(0x5020A,0x24CF,1,0)
                common=not r[0]&16;t(common);branch(0x5020E,common,0x502EC)
            if common:
                emit(0x502EC,0x502F0);zero=r[5]==0;t(zero);branch(0x502EE,zero,0x50308)
                if not zero:
                    emit(0x502F0,0x502F8);r[5]=RAM_BASE+0x244C;r[0]=load(0x502F2,0x2450,1,0)
                    skip=bool(r[0]&64);t(not skip);branch(0x502F6,skip,0x50308)
                    if not skip:
                        emit(0x502F8,0x50300);r[0]=load(0x502F8,0x11B3,1,0);r[6]=r[0]&255
                        above=r[6]>r[14];t(above);branch(0x502FE,not above,0x50360)
                        if not above:return 3
                        emit(0x50300,0x50304);above=r[6]>r[4];t(above);branch(0x50302,not above,0x50340)
                        if not above:return 2
                        jump(0x50304,0x50378);return 0
                return common_flags(0x50308)
            emit(0x50210,0x50216);r[0]=r[2];high=bool(r[0]&128);t(not high);branch(0x50214,high,0x50284)
            if not high:
                emit(0x50216,0x5021E);r[0]=load(0x50216,0x11B3,1,0);r[6]=r[0]&255
                above=r[6]>r[14];t(above);branch(0x5021C,above,0x50222)
                if not above:jump(0x5021E,0x50360);return 3
                jump(0x50222,0x50378);return 0
            emit(0x50284,0x5028C);r[6]=RAM_BASE+0x1082;r[0]=load(0x50286,0x1083,1,0)
            two=r[0]==2;t(two);branch(0x5028A,two,0x5029C)
            if not two:return rpm_pair(0x5028C,13,0x50294,14,0x50298)
            emit(0x5029C,0x502AA);r[3]=RAM_BASE+0x1094;r[0]=0x7A;r[5]=0x85FC
            r[6]=load(0x502A2,0x110E,1,6);r[2]=byte(0x502A4,0x85FC,2)
            fast=r[6]>=r[2];t(fast);branch(0x502A8,fast,0x502BA)
            if not fast:return rpm_pair(0x502AA,13,0x502B2,14,0x502B6)
            emit(0x502BA,0x502CC);r[2]=RAM_BASE+0x28F8;r[0]=128;r[5]=0x8A2F
            r[6]=load(0x502C2,0x2978,1,6);r[2]=byte(0x502C4,0x8A2F,2)
            above=r[6]>r[2];t(above);branch(0x502C8,above,0x502DE,True);r[0]=load(0x502CA,0x11B3,1,0)
            if above:
                emit(0x502DE,0x502E4);r[6]=r[0]&255;above=r[6]>r[13];t(above);branch(0x502E2,not above,0x50360)
                if not above:return 3
                emit(0x502E4,0x502E8);above=r[6]>r[14];t(above);branch(0x502E6,not above,0x50360)
                if not above:return 3
                jump(0x502E8,0x50378);return 0
            emit(0x502CC,0x502D6);r[5]=r[0]&255;r[0]=byte(0x502CE,0x8A3B,0);r[2]=r[0]&255
            above=r[5]>r[2];t(above);branch(0x502D4,not above,0x50360)
            if not above:return 3
            emit(0x502D6,0x502DA);above=r[5]>r[14];t(above);branch(0x502D8,not above,0x50360)
            if not above:return 3
            jump(0x502DA,0x50378);return 0

        emit(0x50018,0x50046)
        for site,index in ((0x50018,11),(0x5001A,12),(0x5001C,13),(0x5001E,14)):push(site,r[index],index)
        push(0x50020,pr);push(0x50022,gbr);r[0]=RAM_BASE+0x119C;gbr=r[0];stack-=12
        r[11]=0x8A3A;r[7]=0;r[6]=0x85FA;r[2]=byte(0x50030,0x8A3A,2)
        frame_access(0x50032,'write',stack,4,7,0);r[13]=r[2]&255;r[2]=byte(0x50036,0x85FA,2)
        r[7]=RAM_BASE+0x128C;r[0]=0x260;r[12]=r[2]&255;r[6]=0x25C36;r[4]=0x0129
        put(0x50044,0x14EC,1,12,r[12]);row=call(0x50042,0x25C36);diagnostic(row)
        if gates():threshold_lookups()
        else:fallback()
        emit(0x501A4,0x501B6);r[7]=RAM_BASE+0x128C;r[0]=0x4EC;r[6]=RAM_BASE+0x2468
        put(0x501AA,0x1778,1,4,r[4]);r[0]=0x41E;put(0x501AE,0x16AA,1,14,r[14]);r[0]=load(0x501B0,0x2468,1,0)
        bypass=bool(r[0]&64);t(not bypass);branch(0x501B4,not bypass,0x501BA)
        set_flag=bypass
        if bypass:jump(0x501B6,0x5036A)
        else:
            outcome=classification()
            if outcome in (2,3):
                if outcome==2:jump(0x50340,0x50362);r[7]=2
                else:emit(0x50360);r[7]=3
                jump(0x50362,0x50378);frame_access(0x50364,'write',stack,4,7,r[7])
            elif outcome==1:
                emit(0x50366,0x5036A);r[7]=1;frame_access(0x50368,'write',stack,4,7,r[7]);set_flag=True
        if set_flag:
            emit(0x5036A,0x50378);r[6]=RAM_BASE+0x2470;r[0]=0x2D;r[0]=load(0x5036E,0x249D,1,0)|128
            r[2]=r[0];r[0]=0x2D;put(0x50376,0x249D,1,2,r[2])
        emit(0x50378,0x5038A);r[0]=frame_access(0x50378,'read',stack,4,0);stack+=12
        gbr=pop(0x5037C);pr=pop(0x5037E)
        for site,index in ((0x50380,14),(0x50382,13),(0x50384,12),(0x50388,11)):r[index]=pop(site,index)
        control(0x50386,'return',pr,True)
        return dict(ram=bytes(ram),frame=bytes(frame),known_registers={index:value&MASK for index,value in enumerate(r)},
            path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,rotations=0,
            sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0])

    if entry==0x50018:return restore()

    emit(0x503E0,0x50400)
    for site,index in ((0x503E0,9),(0x503E2,10),(0x503E4,11),(0x503E6,12),(0x503E8,13),(0x503EA,14)):push(site,r[index],index)
    push(0x503EC,pr);push(0x503EE,macl);stack-=4;r[0]=r[6];frame_access(0x503F4,'write',stack+2,2,0,r[0])
    r[9]=RAM_BASE+0x128C;r[0]=0x235;r[10]=RAM_BASE+0x2468;r[12]=r[5];control(0x503FC,'jump',0x50402,True)
    emit(0x50402,0x50414);r[2]=load(0x50402,0x14C1,1,2);r[0]=load(0x50404,0x2468,1,0)
    frame_access(0x50406,'write',stack,4,6,r[6]);r[6]=0;r[11]=r[2]&255;r[13]=r[14]=0
    bypass=bool(r[0]&64);t(not bypass);branch(0x50410,not bypass,0x50418,True)
    if bypass:
        emit(0x50414,0x50418);control(0x50414,'jump',0x505F4,True);emit(0x505F4);r[11]=0;tail=False
    else:tail=state_transition()
    if tail:
        emit(0x505AE,0x505B6);r[11]&=255;r[0]=r[11];four=r[0]==4;t(four);branch(0x505B4,not four,0x505C0)
        if four:
            emit(0x505B6,0x505BE);r[4]=RAM_BASE+0x256A;r[0]=load(0x505B8,0x2573,1,0)
            zero=r[0]==0;t(zero);branch(0x505BC,not zero,0x505C0)
            if zero:emit(0x505BE);r[11]=0
        emit(0x505C0,0x505CE);r[0]=0x6AE;r[4]=255;r[5]=load(0x505C6,0x193A,1,5)&255
        sentinel=r[5]==255;t(sentinel);branch(0x505CC,sentinel,0x505F6)
        if not sentinel:
            emit(0x505CE,0x505D4);r[6]&=255;fresh=r[6]==255;t(fresh);branch(0x505D2,fresh,0x505DE)
            if not fresh:
                emit(0x505D4,0x505D8);zero=r[5]==0;t(zero);branch(0x505D6,zero,0x505DE)
                if not zero:
                    emit(0x505D8,0x505DE);r[5]=(r[5]-1)&255;put(0x505DC,0x193A,1,5,r[5])
            emit(0x505DE,0x505E4);r[5]&=255;zero=r[5]==0;t(zero);branch(0x505E2,not zero,0x505F6)
            if zero:
                emit(0x505E4,0x505F4);r[0]=0x6AE;r[2]=MASK;put(0x505E8,0x193A,1,2,r[2]);r[0]=0x6AC
                r[2]=load(0x505EC,0x1938,1,2);r[0]=0x6AB;put(0x505F2,0x1937,1,2,r[2]);control(0x505F0,'jump',0x505F6,True)
    emit(0x505F6,0x505FE);r[6]=RAM_BASE+0x424C;r[0]=load(0x505F8,0x4250,1,0)
    reset=bool(r[0]&128);t(not reset);branch(0x505FC,not reset,0x5060E)
    if reset:clear_counts(0x505FE)
    emit(0x5060E,0x50618);r[4]=RAM_BASE+0x256A;r[0]=0x32;r[2]=load(0x50612,0x259C,1,2)
    reset=r[2]!=0;t(not reset);branch(0x50616,not reset,0x50628)
    if reset:clear_counts(0x50618)
    emit(0x50628,0x50632);r[0]=0x235;r[12]=6;put(0x5062C,0x14C1,1,11,r[11]);r[0]=0x6AA;r[4]=load(0x50630,0x1936,1,4)
    rotations=0
    while True:
        emit(0x50632,0x5063E);r[0]=0x6AB;r[13]&=255;r[2]=load(0x50636,0x1937,1,2);r[5]=r[2]&255
        complete=r[13]>=r[5];t(complete);branch(0x5063C,complete,0x5064E)
        if complete:break
        emit(0x5063E,0x50646);r[13]=(r[13]+1)&255;r[4]&=255
        row=call(0x50642,0x50766);rotation(row);rotations+=1
        emit(0x50646,0x5064E);complete=r[13]>=6;t(complete);r[4]=r[0];r[14]|=r[0]
        branch(0x5064A,not complete,0x50632,True)
        if complete:break
    if rotations>6:raise ValueError('the real DFCO loop leaves its exact six-call counter bound')
    emit(0x5064E,0x5066A);r[0]=0x235;r[2]=0x2371C;r[6]=load(0x50652,0x14C1,1,6);r[13]=RAM_BASE+0x2470;r[0]=r[6]&255
    r[6]=byte(0x50658,0x2371C+r[0],6);r[0]=0x2F;r[4]=load(0x5065C,0x249F,1,4);r[2]=(r[6]|r[14])&MASK
    r[5]=r[2]&255;active=r[5]!=0;t(not active);r[2]=r[4]&255;branch(0x50666,active,0x506FC,True)
    if not active:
        emit(0x5066A,0x50670);r[0]=load(0x5066A,0x2468,1,0);blocked=bool(r[0]&64);t(not blocked);branch(0x5066E,blocked,0x506A4)
        if not blocked:
            emit(0x50670,0x50676);r[0]=r[2];flag=bool(r[0]&32);t(not flag);branch(0x50674,not flag,0x506A4)
            if flag:
                emit(0x50676,0x5067E);r[7]=RAM_BASE+0x2458;r[0]=load(0x50678,0x2458,1,0)
                first=bool(r[0]&32);t(not first);branch(0x5067C,not first,0x50698)
                if first:
                    emit(0x5067E,0x5068C);r[0]=r[2]|128;r[2]=r[0];r[0]=0x2F;put(0x50686,0x249F,1,2,r[2]);r[4]=signed(r[2]&255,8)&MASK
                    control(0x50688,'jump',0x506A4,True)
                else:
                    emit(0x50698,0x506A4);r[0]=0x1F;r[0]=load(0x5069A,0x248F,1,0)|64;r[2]=r[0];r[0]=0x1F;put(0x506A2,0x248F,1,2,r[2])
        emit(0x506A4,0x506AE);r[0]=0x238;r[2]=0;r[5]=0x85F6;put(0x506AC,0x14C4,1,2,0);control(0x506AA,'jump',0x506E8,True)
        emit(0x506E8,0x506FC);r[0]=r[4]&0xDF;r[2]=r[0];r[0]=0x2F;put(0x506F0,0x249F,1,2,r[2]);r[0]=0x22
        r[2]=byte(0x506F4,0x85F6,2);r[5]=RAM_BASE+0x24F9;put(0x506FA,0x251B,1,2,r[2]);control(0x506F8,'jump',0x5074E,True)
    else:
        emit(0x506FC,0x50702);r[0]=r[2];flag=bool(r[0]&32);t(not flag);branch(0x50700,flag,0x50730)
        if not flag:
            emit(0x50702,0x50730);r[3]=RAM_BASE+0x1094;r[0]=0x7A;r[1]=0xFFFFFFFE;r[5]=load(0x50708,0x110E,1,5);r[3]=0xFFFFFFFD
            r[0]=0x238;put(0x5070E,0x14C4,1,5,r[5]);r[0]=0x2B0;r[7]=load(0x50712,0x153C,1,7);r[0]=0x531
            r[7]&=255;r[4]=load(0x50718,0x17BD,1,4);r[7]&=r[1];r[5]=r[7]&255;r[0]=0x2B0;r[4]&=255;r[4]&=r[1];r[5]&=r[3]
            put(0x50726,0x153C,1,5,r[5]);r[5]=r[4]&255;r[0]=0x531;r[5]&=r[3];put(0x5072E,0x17BD,1,5,r[5])
        emit(0x50730,0x5074E);r[0]=32;r[2]|=r[0];r[0]=0x2F;put(0x50736,0x249F,1,2,r[2])
        r[0]=signed(r[2]&255,8)&MASK;r[0]&=0x7F;r[2]=r[0];r[0]=0x2F;put(0x50740,0x249F,1,2,r[2]);r[0]=0x1F
        r[0]=load(0x50744,0x248F,1,0)&0xBF;r[2]=r[0];r[0]=0x1F;put(0x5074C,0x248F,1,2,r[2])
    emit(0x5074E,0x50766);r[6]=(r[6]|r[14])&MASK;r[0]=r[6]&255;stack+=4;macl=pop(0x50754);pr=pop(0x50756)
    for site,index in ((0x50758,14),(0x5075A,13),(0x5075C,12),(0x5075E,11),(0x50760,10),(0x50764,9)):r[index]=pop(site,index)
    control(0x50762,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={index:value&MASK for index,value in enumerate(r)},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,rotations=rotations,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0])
