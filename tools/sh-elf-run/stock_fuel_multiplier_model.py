"""Independent multiplier arithmetic with complete branch-context observations."""
MASK=0xffffffff
BYTE_INPUTS=(('special',0x4184),('aggregate',0x22e0),('other_mask',0x22ee),
             ('special_gate',0x4186),('control',0x2468),('floor_flags',0x246c),
             ('previous_flags',0x246f),('transition_flags',0x24a2),('selector',0x2473),('tick',0x84c3))
WORD_INPUTS=(('base',0x231a),('conditional',0x240a),('mixture',0x22e8),
             ('floor',0x15cc),('mode',0x1414),('old',0x22f4))
CALIBRATIONS=(('special_gain',0x838e,1),('transition_rates',0x840d,6),
              ('rates',0x84e6,2),('cap',0x8b9d,1))
DEFAULTS={'base':16384,'conditional':0,'mixture':16384,'floor':16384,'old':16384,
          'special':0,'aggregate':0,'other_mask':0,'special_gate':0,'control':0,'mode':0x8000,
          'floor_flags':0,'previous_flags':0,'transition_flags':0,'selector':0,'tick':0x80,
          'special_gain':64,'transition_rates':(0,0,0,3,3,0),'rates':(255,255),'cap':254}
def signed(value,bits):
    value&=(1<<bits)-1;return value-(1<<bits) if value&(1<<(bits-1)) else value
def sx(value,bits):return signed(value,bits)&MASK

def arithmetic(v):
    q=min(65535,v['base']+v['conditional'])*v['mixture']//16384
    floor_selected=q<v['floor']
    flags=(v['floor_flags']|16) if floor_selected else (v['floor_flags']&239)
    if v['special']&64:
        target=min(65535,q*v['special_gain']//64);flags=v['floor_flags']
    else:target=v['floor'] if floor_selected else min(65535,q)
    phase=v['transition_flags']
    eligible=(v['other_mask']!=63 and v['aggregate']!=63 and not v['special_gate']&64
              and not v['special']&64 and not v['control']&8 and v['mode']==0x8000)
    if eligible:
        target=min(target,v['cap']*256)
        if bool(v['previous_flags']&16)!=bool(flags&16):phase|=64
        if not phase&64:
            delta=target-v['old']
            if delta>=0:target=min(target,min(65535,v['old']+v['rates'][0]*64))
            else:target=max(target,max(0,v['old']-v['rates'][1]*64))
        elif not v['tick']&128:target=v['old']
        elif flags&16:
            bound=v['old']+v['transition_rates'][5]*16
            if bound<target:target=min(65535,bound)
            else:phase&=191
        else:
            step=v['transition_rates'][1 if v['selector']&64 else 0]*16
            bound=v['old']-step
            if bound>target:target=max(0,bound)
            else:phase&=191
    return {'snapshot':target,'output':0 if v['aggregate']==63 else target,
            'updated_floor':flags,'updated_phase':phase,'eligible':eligible,'floor_selected':floor_selected}

def case(index,variant=None,entry_sr=None,**values):
    v={**DEFAULTS,**values}
    assert set(v)==set(DEFAULTS)
    for name,_ in BYTE_INPUTS:assert 0<=v[name]<=255
    for name,_ in WORD_INPUTS:assert 0<=v[name]<=65535
    assert 0<=v['cap']<=255 and 0<=v['special_gain']<=255
    assert len(v['transition_rates'])==6 and len(v['rates'])==2
    assert all(0<=x<=255 for x in (*v['transition_rates'],*v['rates']))
    variant=index&1 if variant is None else variant
    entry_sr=(index&1)|(((index>>1)&15)<<4)|((index&3)<<8) if entry_sr is None else entry_sr
    assert variant in (0,1) and not entry_sr&~0x3f1
    incoming=[((0x1728394a+r*0x110203) if variant==0 else (0x81234567+r*0x1020305))&MASK for r in range(15)]
    r=incoming.copy();frame={}
    def byte(at,value):frame[at]=value&255
    def word(at,value):
        for i,b in enumerate((value&MASK).to_bytes(4,'big')):frame[at+i]=b
    word(156,incoming[13]);word(152,incoming[14])
    word(148,0x9274b6d8 if variant else 0x2468ace0)
    word(144,0x01004567 if variant else 0x01003579)
    summed=v['base']+v['conditional'];r[2]=min(65535,summed)
    product=r[2]*v['mixture'];r[4]=product//16384;r[6]=v['special']&64
    if r[6]:
        r[2]=(r[4]*v['special_gain'])//4;r[5]=r[2]//16
        if r[5]<=65535:r[2]//=16;r[4]=r[2]
        else:r[4]=65535
        updated_floor=v['floor_flags']
    else:
        r[1]=0x0100128c;r[7]=0x01002468;r[5]=v['floor'];r[2]=sx(v['floor_flags'],8)
        if r[4]>=r[5]:r[4]=min(65535,r[4]);updated_floor=v['floor_flags']&239
        else:r[4]=sx(v['floor'],16);updated_floor=v['floor_flags']|16
    mode_ok=False
    if v['other_mask']!=63 and v['aggregate']!=63 and not v['special_gate']&64 and not r[6]:
        r[6]=0x01002468;word(136,r[6])
        if not v['control']&8:
            r[6]=0x8000;r[2]=v['mode'];mode_ok=r[2]==r[6]
    updated_phase=v['transition_flags'];eligible=mode_ok
    if eligible:
        r[4]&=65535;r[2]=sx(v['cap'],8);r[5]=sx(updated_phase,8);r[6]=v['cap']*256
        r[4]=min(r[4],r[6]);byte(128,r[5])
        r[7]=int(bool(v['previous_flags']&16));r[6]=int(bool(updated_floor&16));byte(132,updated_floor)
        if r[7]!=r[6]:
            r[2]=0x01002468;r[5]|=64;updated_phase=r[5]&255;r[2]=sx(r[5],8)
            byte(128,r[2])
        byte(140,updated_phase)
        if not updated_phase&64:
            target=r[4];difference=target-v['old'];r[5]=difference&MASK
            if difference>=0:
                r[6]=0x84e6;r[2]=v['rates'][0]*64
                if difference>r[2]:
                    r[5]=MASK;r[4]=65535;r[6]=v['old']+r[2]
                    if r[6]<=65535:r[4]=(sx(v['old'],16)+r[2])&MASK
            else:
                r[6]=0x84e7;r[2]=sx(v['rates'][1],8);r[7]=v['rates'][1]*64;r[2]=-difference
                if -difference>r[7]:
                    r[6]=v['old'];r[4]=max(0,v['old']-r[7])
        else:
            r[6]=0x7a00
            if not v['tick']&128:r[4]=sx(v['old'],16)
            elif updated_floor&16:
                r[5]=0x840d;r[4]&=65535;r[6]=v['transition_rates'][5]*16;r[7]=v['old'];r[2]=r[7]+r[6]
                if r[2]<r[4]:
                    r[5]=MASK;r[4]=65535
                    if r[2]<=65535:r[7]+=r[6];r[4]=r[7]
                else:
                    updated_phase&=191;byte(140,updated_phase);r[6]=0x01002468;r[2]=sx(updated_phase,8)
            else:
                r[6]=0x01002468;r[5]=0x840d
                if v['selector']&64:r[5]=v['transition_rates'][1]
                else:r[2]=sx(v['transition_rates'][0],8);r[5]=v['transition_rates'][0]
                r[5]*=16;r[7]=v['old'];r[2]=(r[7]-r[5])&MASK;r[4]&=65535
                if signed(r[2],32)>r[4]:
                    if r[7]<r[5]:r[4]=0
                    else:r[7]-=r[5];r[4]=r[7]
                else:
                    updated_phase&=191;byte(140,updated_phase);r[6]=0x01002468;r[2]=sx(updated_phase,8)
    snapshot=r[4]&65535;r[1]=0x0100128c
    if v['aggregate']==63:r[4]=0
    r[0]=r[4]
    independent=arithmetic(v)
    assert snapshot==independent['snapshot'] and (r[0]&65535)==independent['output']
    assert updated_floor==independent['updated_floor'] and updated_phase==independent['updated_phase']
    assert eligible==independent['eligible']
    return {**v,**independent,'variant':variant,'entry_sr':entry_sr,'expected_t':int(v['aggregate']==63),
            'incoming':incoming,'expected':r,'frame_writes':frame}

def matrix():
    rows=[]
    def add(**values):rows.append(case(len(rows),**values))
    early=(
        {},{'aggregate':63},{'other_mask':63},{'special':64},{'special_gate':64},{'control':8},{'mode':0},
        {'base':0,'floor':0,'old':65535},{'base':65535,'floor':0,'old':0},
        {'base':1,'floor':32768,'tick':0},{'transition_flags':64,'tick':0},
        {'base':0,'floor':0,'old':1000,'transition_flags':64,'transition_rates':(5,10,0,0,0,20)},
        {'base':0,'floor':0,'old':1000,'transition_flags':64,'selector':64,'transition_rates':(5,10,0,0,0,20)},
        {'base':0,'floor':1000,'old':0,'previous_flags':0,'transition_rates':(5,10,0,0,0,20)},
        {'base':65535,'floor':0,'old':32768,'rates':(1,1)},
        {'base':65535,'floor':65535,'old':65535,'transition_flags':64,'transition_rates':(255,255,0,0,0,255)})
    for values in early:add(**values)
    for base in range(65536):add(base=base,floor=0,mode=0)
    boundaries=(0,1,63,64,255,256,16383,16384,32767,32768,65534,65535)
    for base in boundaries:
        for mixture in boundaries:
            for conditional in (0,1,32768,65535):
                for special in (0,64):add(base=base,mixture=mixture,conditional=conditional,special=special,
                                        floor=32768,old=32768,special_gain=255)
    for floor in boundaries:
        for old in boundaries:
            for phase in (0,64,128,255):
                for rates in ((0,0),(1,1),(255,255)):
                    for base in (0,65535):add(floor=floor,old=old,transition_flags=phase,rates=rates,base=base,
                                            transition_rates=(0,255,0,0,0,255),selector=64)
    for field,_ in BYTE_INPUTS:
        for value in range(256):
            for base in (0,65535):add(**{field:value,'base':base,'floor':32768,'old':32767})
    for cap in range(256):
        for special_gain in (0,1,63,64,65,127,128,255):add(base=65535,mixture=65535,cap=cap,special_gain=special_gain,
                                                                      special=64 if special_gain&1 else 0)
    return rows

if __name__=='__main__':
    rows=matrix();print('PREPARED_MULTIPLIER_NUMERIC cases='+str(len(rows))+' gnu_executed=0 accepted_points=0')
