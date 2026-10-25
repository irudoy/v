"""Complete per-phase CPU/frame state, exact physical quantity flow and real delayed calls."""
from kb import test_contract
from kb import transmission_candidate_boundary_contract as contract

RAM_BASE=0x01000000
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
INFEASIBLE_SITES=set()
FEASIBLE_SITES=EXACT_SITES
FIXED_BRANCHES={}

def same(a,b,reason):
    if not test_contract.exact(a,b):raise ValueError(reason)

def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the quantity phase changes complete independently reconstructed exit CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the quantity phase changes complete frame or separate numerical RAM/publication equations')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the quantity phase omits its complete natural instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the quantity phase detaches its complete initial CPU from the immutable observed input')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the quantity phase changes a complete stock instruction, feasible path or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the quantity phase detaches intermediate complete CPU/frame control state')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},
        'the quantity phase changes executed instruction identities')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the quantity phase omits or invents a real control delay slot')
    literal=contract.LITERAL_OPERANDS
    actual=[]
    for event in result['accesses']:
        if event['domain']=='frame':continue
        if event['site'] in literal:
            at,width,register=literal[event['site']]
            same(event,dict(site=event['site'],mode='read',address=at,width_bytes=width,register=register,
                domain='rom',bytes=fixture[at:at+width].hex()),'the quantity phase changes an exact PC literal operand')
        else:actual.append({key:event[key] for key in ('site','mode','address','width_bytes','register','domain','bytes')})
    same(actual,value['operands'],'the quantity phase changes ordered actual ROM/RAM site, address, width, direction or complete bytes')

    if result['calls']:raise ValueError('the transmission phases invent a helper call')
    phase=observed['phase']
    if phase not in (0,1) or trace[0]['site']!=contract.ENTRIES[phase]:
        raise ValueError('the transmission phase changes its complete natural entry')
    if result['sp']!=observed['sp'] or result['pr']!=observed['continuation']:
        raise ValueError('the transmission phase changes its complete natural return SP/PR')
    if (result['gbr'],result['mach'],result['macl'])!=tuple(observed['context'][15:18]):
        raise ValueError('the transmission phase changes preserved complete special registers')
    if result['sr']&~1!=observed['sr_before']&~1:
        raise ValueError('the transmission phase changes preserved I/M/Q or other SR bits')
    saved=(13,14) if phase==0 else tuple(range(8,15))
    push_sites=(0x777FA,0x777FC) if phase==0 else tuple(range(0x79030,0x7903E,2))
    pop_sites=(0x77874,0x77878) if phase==0 else (0x791FA,0x791FC,0x791FE,0x79200,0x79202,0x79204,0x79208)
    stack=observed['sp'];expected_frame=bytearray(observed['frame_before']);events=[]
    for site,register in zip(push_sites,saved):
        stack-=4;raw=observed['context'][register].to_bytes(4,'big');at=160+stack-observed['sp']
        expected_frame[at:at+4]=raw
        events.append(dict(site=site,mode='write',address=stack,width_bytes=4,register=register,domain='frame',bytes=raw.hex()))
    for site,register in zip(pop_sites,reversed(saved)):
        raw=observed['context'][register].to_bytes(4,'big')
        events.append(dict(site=site,mode='read',address=stack,width_bytes=4,register=register,domain='frame',bytes=raw.hex()));stack+=4
    same([event for event in result['accesses'] if event['domain']=='frame'],events,
        'the transmission phase changes complete ordered saved-register words or return-delay reload')
    if observed['frame_after']!=bytes(expected_frame) or any(result['registers'][i]!=observed['context'][i] for i in saved):
        raise ValueError('the transmission phase changes independently preserved complete frame/register preimages')
    terminal,delay=(0x77876,0x77878) if phase==0 else (0x79206,0x79208)
    if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'],trace[-1]['next'])!=(terminal,delay,True,observed['continuation']):
        raise ValueError('the transmission phase replaces its natural RTS-delay full register restore')
    stores=((0x77866,13,0x3480),(0x7786A,7,0x3484),(0x7786E,5,0x347E),(0x77872,14,0x3482)) if phase==0 else ((value['publication_site'],value['publication_register'],0x19C6),)
    for site,register,offset in stores:
        row,=[row for row in trace if row['site']==site]
        raw=int.from_bytes(value['memory'][offset:offset+2],'big')
        expected=(raw-65536 if raw&32768 else raw)&0xFFFFFFFF
        if row['before']['registers'][register]!=expected:
            raise ValueError('the transmission phase substitutes matching output bytes for the complete live signed publication register')

def require_handoff(completion,boundary,pvalue,cvalue):
    if (completion['phase']!=0 or boundary['phase']!=1 or completion['pair']!=boundary['pair']
            or completion['memory_after']!=boundary['memory_before']
            or not test_contract.exact(completion['calibration_after'],boundary['calibration_before'])
            or completion['bound_after']!=boundary['bound_before']):
        raise ValueError('the transmission handoff resets or detaches complete actual RAM/calibration/code continuity')
    for at,raw in pvalue['handoff'].items():
        wanted=raw.to_bytes(2,'big')
        if completion['memory_after'][0][at:at+2]!=wanted or boundary['memory_before'][0][at:at+2]!=wanted:
            raise ValueError('the transmission handoff changes a real complete completion word')
    for site,at in ((0x7914E,0x3484),(0x7915C,0x3480)):
        actual=[event for event in cvalue['operands'] if event['site']==site]
        wanted=pvalue['handoff'][at].to_bytes(2,'big').hex()
        if len(actual)!=1 or actual[0]['bytes']!=wanted or actual[0]['address']!=RAM_BASE+at:
            raise ValueError('the transmission boundary substitutes a scalar for an actual carried word read')
    if pvalue['shared_mode']!=cvalue['shared_mode']:
        raise ValueError('the transmission pair changes its shared physical83C1 mode between calls')
