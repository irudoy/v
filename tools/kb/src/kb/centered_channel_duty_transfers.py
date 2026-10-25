"""Complete per-phase CPU/frame state, exact physical quantity flow and real delayed calls."""
from kb import test_contract
from kb import centered_channel_duty_contract as contract

RAM_BASE=0x01000000
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
INFEASIBLE_SITES={*range(0x26A60,0x26A80,2),*range(0x26A9C,0x26AAA,2),
    0x21BCC,0x21BCE,*range(0x21C7C,0x21CD6,2),*range(0x21D76,0x21DC6,2),0x26D0A,0x26D0C}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={0x26A9A:'taken',0x21BCA:'taken',0x21BDC:'fallthrough',
    0x21CEA:'fallthrough',0x26C7A:'fallthrough',0xBE65E:'fallthrough'}

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
    if len(result['calls'])!=len(value['calls']):raise ValueError('the quantity phase invents or omits a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            (expected['site'],expected['target'],expected['return_address'],observed['sp']+expected['sp_delta']),
            'the quantity phase changes a real helper target, continuation or exact call frame')
        entered=actual['entry']
        if (entered['sp']!=actual['sp'] or entered['pr']!=expected['return_address']
                or any(entered['registers'][register]!=raw for register,raw in expected['arguments'].items())):
            raise ValueError('the quantity phase changes a separate actual post-delay arithmetic argument')
        start=next((i+2 for i in range(cursor,len(trace)-2) if trace[i]['site']==expected['site']),None)
        if start is None or trace[start]['site']!=expected['target']:
            raise ValueError('the quantity phase replaces the real post-delay helper entry')
        before=trace[start]['before'];cursor=start
        same(tuple(entered[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
            'the quantity phase detaches complete helper-entry CPU from its preceding delay slot')
        terminal=next((i for i in range(start,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches'])
            and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the quantity phase omits a real natural helper return')
        returned=trace[terminal+1]['after']
        if (returned['registers'][15]!=actual['sp'] or returned['pr']!=expected['return_address']
                or any(returned['registers'][register]!=raw for register,raw in expected.get('returned',{}).items())):
            raise ValueError('the quantity phase changes independent returned helper arithmetic, PR or SP')
    controls={(row['site'],row['target']) for row in result['branches'] if row['kind']=='jump'}
    if not set(value['tails'])<=controls:raise ValueError('the quantity phase substitutes a real helper tail or delay-slot path')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind']!=FIXED_BRANCHES[row['site']]:
            raise ValueError('the quantity phase forces an impossible caller-scoped branch outcome')
    if result['sp']!=observed['sp'] or result['pr']!=observed['continuation']:
        raise ValueError('the quantity phase changes its complete natural outer return')
    phase=observed['phase']
    if phase not in (0,1) or trace[0]['site']!=contract.ENTRIES[phase]:
        raise ValueError('the centered duty phase changes its complete natural entry')
    if (result['gbr'],result['mach'],result['macl'])!=tuple(observed['context'][15:18]):
        raise ValueError('the centered duty phase changes a preserved complete special register')
    if result['sr']&~0x301!=observed['sr_before']&~0x301:
        raise ValueError('the centered duty phase changes preserved interrupt or other SR controls')
    def frame_event(site,mode,delta,raw,register=None):
        rows=[r for r in result['accesses'] if r['site']==site and r['domain']=='frame']
        same(rows,[dict(site=site,mode=mode,address=observed['sp']+delta,width_bytes=4,
            register=register,domain='frame',bytes=raw.to_bytes(4,'big').hex())],
            'the centered duty phase changes an exact complete outer saved word or restoration')
    def full_store(site,register,raw):
        row,=[r for r in trace if r['site']==site]
        if row['before']['registers'][register]!=raw:
            raise ValueError('the centered duty phase substitutes matching bytes for a complete live publication register')
    if phase==0:
        for site,register in zip(range(0xBE5BC,0xBE5C6,2),range(10,15)):
            frame_event(site,'write',-(register-9)*4,observed['context'][register],register)
        frame_event(0xBE5C6,'write',-24,observed['continuation'])
        frame_event(0xBE806,'read',-24,observed['continuation'])
        for site,register in zip((0xBE808,0xBE80A,0xBE80C,0xBE80E,0xBE812),(14,13,12,11,10)):
            frame_event(site,'read',-(register-9)*4,observed['context'][register],register)
        if any(result['registers'][r]!=observed['context'][r] for r in range(10,15)):
            raise ValueError('the centered producer changes a complete saved general register')
        if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'])!=(0xBE810,0xBE812,True):
            raise ValueError('the centered producer replaces its natural RTS-delay R10 restore')
        if value['composites_published']:
            for site,at,register in ((0xBE6E0,0x16E8,2),(0xBE714,0x16EC,2),
                    (0xBE7B6,0x1A9C,2),(0xBE804,0x1AA0,7)):
                full_store(site,register,int.from_bytes(value['memory'][at:at+4],'big'))
            for site,curve in zip((0xBE798,0xBE7E8),value['curves']):
                full_store(site,2,curve['return_register_value'])
    else:
        frame_event(0xBE814,'write',-4,observed['context'][13],13)
        frame_event(0xBE816,'write',-8,observed['continuation'])
        frame_event(0xBE818,'write',-12,observed['context'][17])
        frame_event(0xBE81A,'write',-16,observed['context'][15])
        frame_event(0xBE8E0,'read',-16,observed['context'][15])
        frame_event(0xBE8E2,'read',-12,observed['context'][17])
        frame_event(0xBE8E4,'read',-8,observed['continuation'])
        frame_event(0xBE8E8,'read',-4,observed['context'][13],13)
        if result['registers'][13]!=observed['context'][13]:
            raise ValueError('the indexed duty consumer changes its complete saved R13')
        if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'])!=(0xBE8E6,0xBE8E8,True):
            raise ValueError('the indexed duty consumer replaces its natural RTS-delay R13 restore')
        full_store(0xBE8DC,6,value['publication_register_value'])

def require_handoff(producer,consumer,pvalue,cvalue):
    if (producer['phase']!=0 or consumer['phase']!=1 or producer['pair']!=consumer['pair']
            or producer['memory_after']!=consumer['memory_before']
            or not test_contract.exact(producer['calibration_after'],consumer['calibration_before'])
            or producer['bound_after']!=consumer['bound_before']):
        raise ValueError('the centered duty pair resets or detaches complete actual RAM/calibration/code continuity')
    for at,raw in pvalue['handoff'].items():
        wanted=raw.to_bytes(4,'big')
        if producer['memory_after'][0][at:at+4]!=wanted or consumer['memory_before'][0][at:at+4]!=wanted:
            raise ValueError('the centered duty handoff changes either complete actual producer quantity word')
    reads=[r for r in cvalue['operands'] if r['site']==0xBE886]
    if cvalue['mode']=='calculated':
        at=0x1A9C+cvalue['channel']*4
        wanted=producer['memory_after'][0][at:at+4]
        if (len(reads)!=1 or reads[0]['mode']!='read' or reads[0]['width_bytes']!=4
                or reads[0]['address']!=RAM_BASE+at or reads[0]['bytes']!=wanted.hex()
                or cvalue['handoff']!=int.from_bytes(wanted,'big')):
            raise ValueError('the indexed duty consumer substitutes a synthetic scalar or another channel for actual carried bytes')
    elif reads or cvalue['handoff'] is not None:
        raise ValueError('the indexed duty override invents a carried quantity read')
