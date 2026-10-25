"""Complete per-phase CPU/frame state, exact physical quantity flow and real delayed calls."""
from kb import test_contract
from kb import calculated_load_quantity_contract as contract

RAM_BASE=0x01000000
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
INFEASIBLE_SITES={0x26A60,0x26A62,*range(0x26AAA,0x26AB4,2),*range(0x21D76,0x21DC6,2),0x26D0A,0x26D0C}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={0x808C4:'fallthrough',0x26A9A:'fallthrough',0x21CEA:'fallthrough',0x26C7A:'fallthrough'}

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
    if observed['phase']==0:
        store=[row for row in result['accesses'] if row['site']==0xB999A]
        if (len(store)!=1 or trace[-1]['site']!=0xB999A or not trace[-1]['delay_slot']
                or trace[-2]['site']!=0xB9998 or trace[-1]['after']['pr']!=observed['continuation']):
            raise ValueError('the quantity producer replaces its real RTS-delay byte publication')
    else:
        if result['registers'][14]!=observed['context'][14]:raise ValueError('the quantity consumer loses its complete saved R14')
        if any(c['site']==0x808BE for c in result['calls']):
            sentinel=next(c for c in result['calls'] if c['site']==0x808BE)
            if sentinel['entry']['registers'][4]!=0xFFFFFFFF:
                raise ValueError('the quantity consumer replaces its actual minus-one sentinel with an unsigned byte')

def require_handoff(producer,consumer,producer_value,consumer_value):
    if (producer['phase']!=0 or consumer['phase']!=1 or producer['pair']!=consumer['pair']
            or producer['memory_after']!=consumer['memory_before']
            or not test_contract.exact(producer['calibration_after'],consumer['calibration_before'])
            or producer['bound_after']!=consumer['bound_before']):
        raise ValueError('the quantity handoff changes phase identity or complete actual RAM/calibration/bound continuity')
    published=producer['memory_after'][0][0x329F]
    if published!=producer_value['value'] or consumer['memory_before'][0][0x329F]!=published:
        raise ValueError('the quantity handoff substitutes a synthetic K or detaches actual producer bytes')
    if consumer_value['K'] is not None and consumer_value['K']!=published:
        raise ValueError('the quantity consumer substitutes a matching scalar for its actual carried read')
