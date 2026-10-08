"""Natural coefficient selection with the independently executed byte lookup model."""
from stock_injection_end_angle_model import State

MASK=0xffffffff
STOCK=(70,70,72,74,77,84,93,102)

def case(index,normalized,term,table=STOCK,variant=None,entry_sr=None):
    assert 0<=normalized<=255 and -32768<=term<=32767
    assert len(table)==8 and all(0<=value<=255 for value in table)
    variant=index&1 if variant is None else variant
    entry_sr=(index&1)|(((index>>1)&15)<<4)|((index&3)<<8) if entry_sr is None else entry_sr
    assert variant in (0,1) and entry_sr&~0x3f1==0
    incoming=[((0x1728394a+r*0x110203) if variant==0 else
               (0x81234567+r*0x1020305))&MASK for r in range(15)]
    macl=0x9274b6d8 if variant else 0x2468ace0
    state=State(incoming,macl,entry_sr)
    state.r[2]=0x26370;state.r[4]=0x12176;state.r[6]=128
    x=min(255,2*normalized)
    value=state.implicit(table,0x12176,x,156)
    coefficient=value//2 if term<0 else 64
    state.r[0],state.r[2],state.r[5],state.r[6]=0x27e,term&MASK,0x0100128c,coefficient
    state.t(term>=0)
    index_in_curve=min(7,x//32)
    if x>=224:
        independent_value=table[7]
    else:
        left,right=table[index_in_curve:index_in_curve+2]
        fraction=(x%32)*2048
        delta=abs(right-left)*fraction//65536
        independent_value=left+delta if right>=left else left-delta
    assert value==independent_value and state.macl==macl
    return {'normalized':normalized,'term':term,'table':tuple(table),'variant':variant,
        'entry_sr':entry_sr,'coordinate':x,'cell_index':index_in_curve,'lookup':value,
        'coefficient':coefficient,'incoming':incoming,'expected':state.r,
        'expected_sr':state.sr,'frame_writes':state.frame}

def matrix():
    rows=[]
    def add(**values):rows.append(case(len(rows),**values))
    for normalized in (0,127,128,255):
        for term in (-32768,-1,0,32767):add(normalized=normalized,term=term)
    for normalized in range(256):
        for term in (-32768,-32767,-1,0,1,127,255,32767):
            for variant in range(2):add(normalized=normalized,term=term,variant=variant)
    tables=((0,)*8,(255,)*8,tuple(range(0,256,32)),tuple(reversed(range(0,256,32))),
            (255,0,255,0,255,0,255,0))
    for table in tables:
        for normalized in range(256):
            for term in (-1,0):add(normalized=normalized,term=term,table=table)
    for cell in range(8):
        for value in (0,1,127,128,254,255):
            table=list(STOCK);table[cell]=value
            for normalized in (0,15,16,31,32,111,112,255):
                for term in (-32768,32767):add(normalized=normalized,term=term,table=tuple(table))
    return rows

if __name__=='__main__':
    rows=matrix();assert len(rows)==7440
    assert {row['expected_sr']&1 for row in rows}=={0,1}
    assert any(row['frame_writes'] for row in rows)
    print(f'PREPARED_TRANSIENT_COEFFICIENT cases={len(rows)} gnu_executed=0 accepted_points=0')
