"""Complete natural-entry CPU/frame state, exact physical quantity flow and real delayed calls."""
from kb import test_contract
from kb import apc_reset_candidate_contract as contract

RAM_BASE=0x01000000
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
INFEASIBLE_SITES={0x4C21E,0x4C232,0x21BCC,0x21BCE,*range(0x21BDE,0x21C7C,2),
    0x21CCC,0x21CCE,*range(0x21D6A,0x21DC6,2),*range(0x26A60,0x26A80,2),*range(0x26A9C,0x26AAA,2)}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={0x4C21A:'taken',0x4C22E:'taken',0x21BC0:'fallthrough',0x21BCA:'taken',
    0x21BDC:'taken',0x21CCA:'taken',0x21CE4:'fallthrough',0x21CEA:'fallthrough',0x26A9A:'taken'}

def same(a,b,reason):
    if not test_contract.exact(a,b):raise ValueError(reason)

def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the APC entry changes complete independently reconstructed exit CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the APC entry changes complete frame or separate numerical RAM/publication equations')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the APC entry omits its complete natural instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the APC entry detaches its complete initial CPU from the immutable observed input')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the APC entry changes a complete stock instruction, feasible path or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the APC entry detaches intermediate complete CPU/frame control state')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},
        'the APC entry changes executed instruction identities')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the APC entry omits or invents a real control delay slot')
    literal=contract.LITERAL_OPERANDS
    actual=[]
    for event in result['accesses']:
        if event['domain']=='frame':continue
        if event['site'] in literal:
            at,width,register=literal[event['site']]
            same(event,dict(site=event['site'],mode='read',address=at,width_bytes=width,register=register,
                domain='rom',bytes=fixture[at:at+width].hex()),'the APC entry changes an exact PC literal operand')
        else:actual.append({key:event[key] for key in ('site','mode','address','width_bytes','register','domain','bytes')})
    same(actual,value['operands'],'the APC entry changes ordered actual ROM/RAM site, address, width, direction or complete bytes')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the APC entry invents or omits a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            (expected['site'],expected['target'],expected['return_address'],observed['sp']+expected['sp_delta']),
            'the APC entry changes a real helper target, continuation or exact call frame')
        entered=actual['entry']
        if (entered['sp']!=actual['sp'] or entered['pr']!=expected['return_address']
                or any(entered['registers'][register]!=raw for register,raw in expected['arguments'].items())):
            raise ValueError('the APC entry changes a separate actual post-delay arithmetic argument')
        start=next((i+2 for i in range(cursor,len(trace)-2) if trace[i]['site']==expected['site']),None)
        if start is None or trace[start]['site']!=expected['target']:
            raise ValueError('the APC entry replaces the real post-delay helper entry')
        before=trace[start]['before'];cursor=start
        same(tuple(entered[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
            'the APC entry detaches complete helper-entry CPU from its preceding delay slot')
        terminal=next((i for i in range(start,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches'])
            and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the APC entry omits a real natural helper return')
        returned=trace[terminal+1]['after']
        if (returned['registers'][15]!=actual['sp'] or returned['pr']!=expected['return_address']
                or any(returned['registers'][register]!=raw for register,raw in expected.get('returned',{}).items())):
            raise ValueError('the APC entry changes independent returned helper arithmetic, PR or SP')
    controls={(row['site'],row['target']) for row in result['branches'] if row['kind']=='jump'}
    if not set(value['tails'])<=controls:raise ValueError('the APC entry substitutes a real helper tail or delay-slot path')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind']!=FIXED_BRANCHES[row['site']]:
            raise ValueError('the APC entry forces an impossible caller-scoped branch outcome')
    if result['sp']!=observed['sp'] or result['pr']!=observed['continuation']:
        raise ValueError('the APC entry changes its complete natural outer return')
    if observed['entry']!=contract.ENTRY or trace[0]['site']!=contract.ENTRY:
        raise ValueError('the APC candidate changes its complete natural entry')
    if (result['gbr'],result['mach'],result['macl'])!=tuple(observed['context'][15:18]):
        raise ValueError('the APC candidate changes a preserved complete special register')
    if result['sr']&~0x301!=observed['sr_before']&~0x301:
        raise ValueError('the APC candidate changes preserved interrupt or other SR controls')
    def frame_event(site,mode,delta,raw,register=None):
        rows=[r for r in result['accesses'] if r['site']==site and r['domain']=='frame']
        same(rows,[dict(site=site,mode=mode,address=observed['sp']+delta,width_bytes=4,
            register=register,domain='frame',bytes=raw.to_bytes(4,'big').hex())],
            'the APC candidate changes a complete outer saved word or restoration')
    for site,register in zip(range(0x4C1E4,0x4C1EE,2),range(10,15)):
        frame_event(site,'write',-(register-9)*4,observed['context'][register],register)
    frame_event(0x4C1EE,'write',-24,observed['continuation'])
    frame_event(0x4C1F0,'write',-28,observed['context'][17])
    frame_event(0x4C392,'read',-28,observed['context'][17])
    frame_event(0x4C394,'read',-24,observed['continuation'])
    for site,register in zip((0x4C396,0x4C398,0x4C39A,0x4C39C,0x4C3A0),(14,13,12,11,10)):
        frame_event(site,'read',-(register-9)*4,observed['context'][register],register)
    if any(result['registers'][r]!=observed['context'][r] for r in range(8,15)):
        raise ValueError('the APC candidate changes a complete preserved general register')
    if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'])!=(0x4C39E,0x4C3A0,True):
        raise ValueError('the APC candidate replaces its natural RTS-delay full R10 restore')
    def row(site):
        found=[r for r in trace if r['site']==site]
        if len(found)!=1:raise ValueError('the APC candidate duplicates or omits an actual publication or live-consumption instruction')
        return found[0]
    for site,curve in zip((0x4C328,0x4C33C),value['curves']):
        if row(site)['before']['registers'][2]!=curve['return_register_value']:
            raise ValueError('the APC curve publication loses the complete returned byte/sign-extension register')
    if row(0x4C346)['before']['registers'][12]!=value['coefficient']:
        raise ValueError('the APC candidate changes its complete independent mode coefficient')
    for site in (0x4C36C,0x4C36E,0x4C370,0x4C372,0x4C374,0x4C376):
        if row(site)['before']['registers'][5]!=value['candidate']:
            raise ValueError('the APC reader substitutes prior RAM or matching bytes for complete live R5 continuity')
    if row(0x4C374)['before']['registers'][4]!=value['staged']:
        raise ValueError('the APC comparison changes the actual separately published and read1874 byte')
    if (row(0x4C37A)['before']['registers'][5]!=value['selected']
            or row(0x4C37A)['after']['registers'][6]!=value['selected']
            or row(0x4C380)['before']['registers'][6]!=value['selected']):
        raise ValueError('the APC candidate detaches its actual minimum from the complete output register')
    if value['diagnostic'] and row(0x4C38E)['before']['registers'][2]!=24:
        raise ValueError('the APC diagnostic override replaces its complete constant source register')
    if any(r['mode']=='read' and r['address']==RAM_BASE+0x1875 for r in result['accesses']):
        raise ValueError('the APC candidate invents a physical1875 RAM read for its live-register quantity')
