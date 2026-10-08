"""Independent composition of the two actual bounded caller BSR sequences."""
import stock_transient_coefficient_model as coefficient
import stock_transient_additive_model as additive

MASK=0xffffffff

def matrix():
    rows=[]
    for first in coefficient.matrix():
        for flags,calibration in ((0,0),(0,4),(32,0),(32,4),(255,255),(223,251)):
            second=additive.case(first['coefficient'],first['term'],flags,calibration,
                first['variant'],first['expected_sr'],incoming=first['expected'])
            assert second['incoming']==first['expected']
            row={**first,'flags':flags,'calibration':calibration,'output':second['output'],
                'expected':second['expected'],'expected_t':second['expected_t']}
            frame=dict(first['frame_writes'])
            macl=0x9274b6d8 if first['variant'] else 0x2468ace0
            for i,byte in enumerate(macl.to_bytes(4,'big')):frame[156+i]=byte
            row['frame_writes']=frame
            # The simulator boundary restores PR from observer-owned SP+24.
            # Its declared R11 scratch is checked against the actual continuation.
            row['expected'][11]=0
            rows.append(row)
    assert len(rows)==44640
    return rows

if __name__=='__main__':
    rows=matrix()
    assert {row['expected_t'] for row in rows}=={0,1}
    assert any(row['output']&32768 for row in rows)
    print(f'PREPARED_TRANSIENT_PAIR cases={len(rows)} callers=2 gnu_executed=0 accepted_points=0')
