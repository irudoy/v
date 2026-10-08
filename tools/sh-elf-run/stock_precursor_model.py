"""Independent full-width precursor arithmetic with real-call boundary observations."""
MASK=0xffffffff
BYTE_INPUTS=(('source_flags',0x245d),('cap_flags',0x24d2),('output_flags',0x24a1))
WORD_INPUTS=(('bfs',0x1024),('alternate_bfs',0x123e),('speed',0x11bc),('cap_floor',0x34f6),
             ('multiplier',0x22e6),('transient_raw',0x2300),('gain',0x165e),('bank0',0x40b6),('bank1',0x40b8))
CALIBRATIONS=(('cap_numerator',0x96e0,4),('pulse_floor',0x94e8,2))
DEFAULTS={'source_flags':0,'cap_flags':0,'output_flags':0,'bfs':32768,'alternate_bfs':65535,
          'speed':1000,'cap_floor':1024,'multiplier':16384,'transient_raw':0,'gain':16384,
          'bank0':25600,'bank1':25600,'cap_numerator':0x12c000,'pulse_floor':170}
def signed(value,bits):
    value&=(1<<bits)-1;return value-(1<<bits) if value&(1<<(bits-1)) else value
def fixed(value,gain):
    assert -(1<<31)<=value<(1<<31) and 0<=gain<=65535
    magnitude=abs(value)*gain//16384
    return -magnitude if value<0 else magnitude
def arithmetic(v):
    selected=v['alternate_bfs'] if v['source_flags']&32 else v['bfs']
    cap_quotient=None
    if v['cap_flags']&1:
        cap_quotient=v['cap_numerator']//v['speed'] if v['speed'] else MASK
        selected=min(selected,max(v['cap_floor'],cap_quotient))
    h=(selected*v['multiplier']&MASK)//131072
    term=signed(v['transient_raw'],16)
    numerators=[h*v[key]&MASK for key in ('bank0','bank1')]
    quotients=[n//25600 for n in numerators]
    bank_unclamped=[fixed(q+term,v['gain']) for q in quotients]
    banks=[max(v['pulse_floor'],max(0,min(65535,q))) for q in bank_unclamped]
    common_raw=fixed(h+term,v['gain']);common_clamp=max(0,min(65535,common_raw))
    flag_set=common_clamp<=v['pulse_floor']
    common=max(v['pulse_floor'],common_clamp)
    updated_flags=(v['output_flags']|1) if flag_set else (v['output_flags']&254)
    return {'selected_bfs':selected,'cap_quotient':cap_quotient,'h':h,'transient':term,
            'bank_numerators':numerators,'bank_quotients':quotients,'bank_unclamped':bank_unclamped,
            'bank0_output':banks[0],'bank1_output':banks[1],'common_raw':common_raw,'common_output':common,
            'updated_flags':updated_flags,'expected_t':int(not flag_set)}

def case(index,variant=None,entry_sr=None,**values):
    v={**DEFAULTS,**values};assert set(v)==set(DEFAULTS)
    for name,_ in BYTE_INPUTS:assert 0<=v[name]<=255
    for name,_ in WORD_INPUTS:assert 0<=v[name]<=65535
    assert 0<=v['cap_numerator']<=MASK and 0<=v['pulse_floor']<=65535
    variant=index&1 if variant is None else variant
    entry_sr=(index&1)|(((index>>1)&15)<<4)|((index&3)<<8) if entry_sr is None else entry_sr
    assert variant in (0,1) and not entry_sr&~0x3f1
    incoming=[((0x1728394a+r*0x110203) if variant==0 else (0x81234567+r*0x1020305))&MASK for r in range(15)]
    macl=0x9274b6d8 if variant else 0x2468ace0;gbr=0x01004567 if variant else 0x01003579
    independent=arithmetic(v);r=incoming.copy();frame={}
    def word(at,value):
        for i,b in enumerate((value&MASK).to_bytes(4,'big')):frame[at+i]=b
    for i in range(7):word(156-4*i,incoming[8+i])
    word(124,macl);word(120,gbr)
    # The actual outer PR word at 128 is bound to the observed continuation.
    if independent['cap_quotient'] is not None and v['speed'] and independent['cap_quotient']>=256:
        word(108,incoming[3])
    for quotient in independent['bank_quotients']:
        if quotient>=256:word(108,0x010022dc)
    # The final multiply saves the second bank product and restores MACL.
    word(112,independent['bank_numerators'][1]);word(116,independent['common_output'])
    common_argument=independent['h']+independent['transient']
    absolute=abs(common_argument);partial=(absolute&65535)*v['gain']
    upper=(absolute>>16)*v['gain']+(partial>>16)
    shifted=(upper<<2)|((partial&65535)>>14)
    result=-shifted if common_argument<0 else shifted
    assert result==independent['common_raw']
    rotated=((partial&65535)<<16)|(partial>>16)
    r[0]=0x5ea;r[1]=(rotated<<2)&MASK;r[2]=partial>>16
    r[3]=0x0100128c;r[4]=v['pulse_floor'];r[5]=signed(v['output_flags'],8)&MASK
    r[6]=independent['common_output'];r[7]=0x2657c
    sr=(entry_sr&~0x301)|((1-(independent['bank_quotients'][1]&1))<<8)|independent['expected_t']
    assert independent['h']<=32767 and all(n<1<<31 for n in independent['bank_numerators'])
    return {**v,**independent,'variant':variant,'entry_sr':entry_sr,'expected_sr':sr,
            'incoming':incoming,'expected':r,'frame_writes':frame}

def matrix():
    rows=[]
    def add(**values):rows.append(case(len(rows),**values))
    early=(
        {},{'source_flags':32},{'cap_flags':1,'speed':0},{'cap_flags':1,'speed':1},
        {'cap_flags':1,'cap_numerator':0,'cap_floor':0},{'cap_flags':1,'cap_numerator':MASK,'speed':65535},
        {'bfs':0,'transient_raw':0x8000},{'bfs':65535,'multiplier':65535,'gain':65535},
        {'transient_raw':65535},{'transient_raw':32767,'pulse_floor':65535},
        {'bank0':0,'bank1':65535},{'bank0':65535,'bank1':0},
        {'gain':0,'pulse_floor':0},{'gain':65535,'transient_raw':0x8000},
        {'bfs':65535,'multiplier':65535,'bank0':1,'bank1':255,'pulse_floor':0},
        {'source_flags':255,'cap_flags':255,'output_flags':255,'speed':255})
    for values in early:add(**values)
    for bfs in range(65536):add(bfs=bfs)
    bounds=(0,1,63,64,255,256,16383,16384,32767,32768,65534,65535)
    for bfs in bounds:
        for multiplier in bounds:
            for gain in bounds:
                for term in (0,32767,32768,65535):add(bfs=bfs,multiplier=multiplier,gain=gain,transient_raw=term)
    for bank0 in (0,1,255,256,25600,65535):
        for bank1 in (0,1,255,256,25600,65535):
            for bfs in (0,1,32768,65535):
                for multiplier in (0,1,16384,65535):
                    for gain in (0,1,16384,65535):add(bfs=bfs,multiplier=multiplier,gain=gain,bank0=bank0,bank1=bank1)
    for field,_ in BYTE_INPUTS:
        for value in range(256):
            for term in (0,32767,32768,65535):add(**{field:value,'transient_raw':term})
    for numerator in (0,1,255,256,65535,65536,0x7fffffff,0x80000000,MASK):
        for speed in bounds:
            for floor in (0,1,32768,65535):add(cap_flags=1,cap_numerator=numerator,speed=speed,cap_floor=floor)
    return rows

if __name__=='__main__':
    rows=matrix();print('PREPARED_PRECURSOR_NUMERIC cases='+str(len(rows))+' gnu_executed=0 accepted_points=0')
