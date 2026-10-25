"""Complete event timing CPU/frame state, real helper calls and published live R6 flow."""
from kb import test_contract
from kb import event_timing_candidate_contract as contract

RAM_BASE=0x01000000
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
INFEASIBLE_SITES={0x4DB82,*range(0x21D6A,0x21DC6,2),0x26D0A,0x26D0C}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={0x4DB00:'fallthrough',0x4DB7E:'fallthrough',
    0x21CE4:'fallthrough',0x21CEA:'fallthrough',0x26C7A:'fallthrough'}

def same(a,b,reason):
    if not test_contract.exact(a,b):raise ValueError(reason)

def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the event timing entry changes complete independently reconstructed exit CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the event timing entry changes complete frame or separate numerical RAM/publication equations')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the event timing entry omits its complete natural instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the event timing entry detaches its complete initial CPU from the immutable observed input')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the event timing entry changes a complete stock instruction, feasible path or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the event timing entry detaches intermediate complete CPU/frame control state')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},
        'the event timing entry changes executed instruction identities')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the event timing entry omits or invents a real control delay slot')
    literal=contract.LITERAL_OPERANDS
    actual=[]
    for event in result['accesses']:
        if event['domain']=='frame':continue
        if event['site'] in literal:
            at,width,register=literal[event['site']]
            same(event,dict(site=event['site'],mode='read',address=at,width_bytes=width,register=register,
                domain='rom',bytes=fixture[at:at+width].hex()),'the event timing entry changes an exact PC literal operand')
        else:actual.append({key:event[key] for key in ('site','mode','address','width_bytes','register','domain','bytes')})
    same(actual,value['operands'],'the event timing entry changes ordered actual ROM/RAM site, address, width, direction or complete bytes')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the event timing entry invents or omits a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            (expected['site'],expected['target'],expected['return_address'],observed['sp']+expected['sp_delta']),
            'the event timing entry changes a real helper target, continuation or exact call frame')
        entered=actual['entry']
        if (entered['sp']!=actual['sp'] or entered['pr']!=expected['return_address']
                or any(entered['registers'][register]!=raw for register,raw in expected['arguments'].items())):
            raise ValueError('the event timing entry changes a separate actual post-delay arithmetic argument')
        start=next((i+2 for i in range(cursor,len(trace)-2) if trace[i]['site']==expected['site']),None)
        if start is None or trace[start]['site']!=expected['target']:
            raise ValueError('the event timing entry replaces the real post-delay helper entry')
        before=trace[start]['before'];cursor=start
        same(tuple(entered[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
            'the event timing entry detaches complete helper-entry CPU from its preceding delay slot')
        terminal=next((i for i in range(start,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches'])
            and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the event timing entry omits a real natural helper return')
        returned=trace[terminal+1]['after']
        if (returned['registers'][15]!=actual['sp'] or returned['pr']!=expected['return_address']
                or any(returned['registers'][register]!=raw for register,raw in expected.get('returned',{}).items())):
            raise ValueError('the event timing entry changes independent returned helper arithmetic, PR or SP')
    controls={(row['site'],row['target']) for row in result['branches'] if row['kind']=='jump'}
    if not set(value['tails'])<=controls:raise ValueError('the event timing entry substitutes a real helper tail or delay-slot path')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind']!=FIXED_BRANCHES[row['site']]:
            raise ValueError('the event timing entry forces an impossible caller-scoped branch outcome')
    if result['sp']!=observed['sp'] or result['pr']!=observed['continuation']:
        raise ValueError('the event timing entry changes its complete natural outer return')
    if observed['entry']!=contract.ENTRY or trace[0]['site']!=contract.ENTRY:
        raise ValueError('the event timing candidate changes its complete natural entry')
    if (result['gbr'],result['mach'],result['macl'])!=tuple(observed['context'][15:18]):
        raise ValueError('the event timing candidate changes a preserved complete special register')
    if result['sr']&~0x301!=observed['sr_before']&~0x301:
        raise ValueError('the event timing candidate changes preserved interrupt or other SR controls')
    def frame_event(site,mode,delta,raw,register=None):
        rows=[r for r in result['accesses'] if r['site']==site and r['domain']=='frame']
        same(rows,[dict(site=site,mode=mode,address=observed['sp']+delta,width_bytes=4,
            register=register,domain='frame',bytes=raw.to_bytes(4,'big').hex())],
            'the event timing entry changes a complete outer saved word or restoration')
    for site,register,delta in ((0x4D99C,12,-4),(0x4D99E,13,-8),(0x4D9A0,14,-12)):
        frame_event(site,'write',delta,observed['context'][register],register)
    frame_event(0x4D9A2,'write',-16,observed['continuation'])
    frame_event(0x4D9A4,'write',-20,observed['context'][17])
    frame_event(0x4D9A6,'write',-24,observed['context'][15])
    frame_event(0x4DB8E,'read',-24,observed['context'][15])
    frame_event(0x4DB90,'read',-20,observed['context'][17])
    frame_event(0x4DB92,'read',-16,observed['continuation'])
    for site,register,delta in ((0x4DB94,14,-12),(0x4DB96,13,-8),(0x4DB9A,12,-4)):
        frame_event(site,'read',delta,observed['context'][register],register)
    if any(result['registers'][r]!=observed['context'][r] for r in range(8,15)):
        raise ValueError('the event timing entry changes a complete preserved general register')
    if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'])!=(0x4DB98,0x4DB9A,True):
        raise ValueError('the event timing entry replaces its natural RTS-delay full R12 restore')
    def row(site):
        found=[r for r in trace if r['site']==site]
        if len(found)!=1:raise ValueError('the event timing entry duplicates or omits an actual quantity instruction')
        return found[0]
    start=trace.index(row(0x4D9AA));finish=trace.index(row(0x4DB8E))
    if (trace[start]['after']['gbr']!=RAM_BASE+0x1FF4
            or any(r['before']['gbr']!=RAM_BASE+0x1FF4 for r in trace[start+1:finish+1])
            or trace[finish]['after']['gbr']!=observed['context'][15]):
        raise ValueError('the event timing entry changes its full GBR rebase, nested helper continuity or restore')
    if value['active']:
        if (row(0x4DA8E)['before']['registers'][0]!=value['candidate']
                or row(0x4DA8E)['after']['registers'][6]!=value['candidate']
                or row(0x4DA90)['before']['registers'][0]!=value['candidate']):
            raise ValueError('the event timing quantity detaches its real returned map word from publication')
        for r in trace:
            if 0x4DA90<=r['site']<=0x4DAB6 and r['before']['registers'][6]!=value['candidate']:
                raise ValueError('the event timing reader substitutes prior2000 RAM for complete live R6 continuity')
        if (row(0x4DAB8)['before']['registers'][6]!=value['candidate']
                or row(0x4DAB8)['before']['registers'][2]!=value['coefficient']
                or row(0x4DAB8)['after']['macl']!=value['product']
                or row(0x4DAC0)['after']['registers'][1]!=value['product']
                or row(0x4DACA)['before']['registers'][0]!=value['quotient']):
            raise ValueError('the event timing reader changes complete real coefficient product or divisor100 flow')
        if (row(0x4DAD0)['after']['registers'][6]!=value['scaled']
                or row(0x4DAD4)['before']['registers'][0]!=value['scaled']):
            raise ValueError('the event timing reader changes its complete capped and stored1FF6 word')
    if row(0x4DB8C)['before']['registers'][6]!=(value['signed_value']&0xFFFFFFFF):
        raise ValueError('the event timing output substitutes a matching byte for its complete actual signed R6')
    if any(r['mode']=='read' and r['address']==RAM_BASE+0x2000 for r in result['accesses']):
        raise ValueError('the event timing entry invents a physical2000 RAM read for its live-register quantity')
