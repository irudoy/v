"""Complete timing additive CPU/frame state, full local carrier and published R6/R2 flow."""
from kb import test_contract
from kb import timing_additive_candidate_contract as contract

RAM_BASE=0x01000000
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
INFEASIBLE_SITES={*range(0x21CEC,0x21D76,2),0x26D0A,0x26D0C}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={0x21CE4:'fallthrough',0x21CEA:'taken',0x26C7A:'fallthrough'}

def same(a,b,reason):
    if not test_contract.exact(a,b):raise ValueError(reason)

def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the timing additive entry changes complete independently reconstructed exit CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the timing additive entry changes complete frame or separate numerical RAM/publication equations')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the timing additive entry omits its complete natural instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the timing additive entry detaches its complete initial CPU from the immutable observed input')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the timing additive entry changes a complete stock instruction, feasible path or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the timing additive entry detaches intermediate complete CPU/frame control state')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},
        'the timing additive entry changes executed instruction identities')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the timing additive entry omits or invents a real control delay slot')
    literal=contract.LITERAL_OPERANDS
    actual=[]
    for event in result['accesses']:
        if event['domain']=='frame':continue
        if event['site'] in literal:
            at,width,register=literal[event['site']]
            same(event,dict(site=event['site'],mode='read',address=at,width_bytes=width,register=register,
                domain='rom',bytes=fixture[at:at+width].hex()),'the timing additive entry changes an exact PC literal operand')
        else:actual.append({key:event[key] for key in ('site','mode','address','width_bytes','register','domain','bytes')})
    same(actual,value['operands'],'the timing additive entry changes ordered actual ROM/RAM site, address, width, direction or complete bytes')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the timing additive entry invents or omits a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            (expected['site'],expected['target'],expected['return_address'],observed['sp']+expected['sp_delta']),
            'the timing additive entry changes a real helper target, continuation or exact call frame')
        entered=actual['entry']
        if (entered['sp']!=actual['sp'] or entered['pr']!=expected['return_address']
                or any(entered['registers'][register]!=raw for register,raw in expected['arguments'].items())):
            raise ValueError('the timing additive entry changes a separate actual post-delay arithmetic argument')
        start=next((i+2 for i in range(cursor,len(trace)-2) if trace[i]['site']==expected['site']),None)
        if start is None or trace[start]['site']!=expected['target']:
            raise ValueError('the timing additive entry replaces the real post-delay helper entry')
        before=trace[start]['before'];cursor=start
        same(tuple(entered[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
            'the timing additive entry detaches complete helper-entry CPU from its preceding delay slot')
        terminal=next((i for i in range(start,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches'])
            and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the timing additive entry omits a real natural helper return')
        returned=trace[terminal+1]['after']
        if (returned['registers'][15]!=actual['sp'] or returned['pr']!=expected['return_address']
                or any(returned['registers'][register]!=raw for register,raw in expected.get('returned',{}).items())):
            raise ValueError('the timing additive entry changes independent returned helper arithmetic, PR or SP')
    controls={(row['site'],row['target']) for row in result['branches'] if row['kind']=='jump'}
    if not set(value['tails'])<=controls:raise ValueError('the timing additive entry substitutes a real helper tail or delay-slot path')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind']!=FIXED_BRANCHES[row['site']]:
            raise ValueError('the timing additive entry forces an impossible caller-scoped branch outcome')
    if result['sp']!=observed['sp'] or result['pr']!=observed['continuation']:
        raise ValueError('the timing additive entry changes its complete natural outer return')
    if observed['entry']!=contract.ENTRY or trace[0]['site']!=contract.ENTRY:
        raise ValueError('the timing additive candidate changes its complete natural entry')
    if (result['gbr'],result['mach'],result['macl'])!=tuple(observed['context'][15:18]):
        raise ValueError('the timing additive candidate changes a preserved complete special register')
    if result['sr']&~0x301!=observed['sr_before']&~0x301:
        raise ValueError('the timing additive candidate changes preserved interrupt or other SR controls')
    def frame_event(site,mode,delta,raw,register=None,width=4):
        rows=[r for r in result['accesses'] if r['site']==site and r['domain']=='frame']
        same(rows,[dict(site=site,mode=mode,address=observed['sp']+delta,width_bytes=width,
            register=register,domain='frame',bytes=raw.to_bytes(width,'big').hex())],
            'the timing additive entry changes a complete outer saved word, local argument or restoration')
    frame_event(0x4BDC2,'write',-4,observed['context'][13],13)
    frame_event(0x4BDC4,'write',-8,observed['context'][14],14)
    frame_event(0x4BDC6,'write',-12,observed['continuation'])
    frame_event(0x4BDC8,'write',-16,observed['context'][17])
    frame_event(0x4BDCA,'write',-20,observed['context'][15])
    frame_event(0x4BEE6,'read',-20,observed['context'][15])
    frame_event(0x4BEE8,'read',-16,observed['context'][17])
    frame_event(0x4BEEA,'read',-12,observed['continuation'])
    frame_event(0x4BEEC,'read',-8,observed['context'][14],14)
    frame_event(0x4BEF0,'read',-4,observed['context'][13],13)
    if any(result['registers'][r]!=observed['context'][r] for r in range(8,15)):
        raise ValueError('the timing additive entry changes a complete preserved general register')
    if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'])!=(0x4BEEE,0x4BEF0,True):
        raise ValueError('the timing additive entry replaces its natural RTS-delay full R13 restore')
    def row(site):
        found=[r for r in trace if r['site']==site]
        if len(found)!=1:raise ValueError('the timing additive entry duplicates or omits a required quantity instruction')
        return found[0]
    start=trace.index(row(0x4BDCE));finish=trace.index(row(0x4BEE6))
    if (trace[start]['after']['gbr']!=RAM_BASE+0x128C
            or any(r['before']['gbr']!=RAM_BASE+0x128C for r in trace[start+1:finish+1])
            or trace[finish]['after']['gbr']!=observed['context'][15]):
        raise ValueError('the timing additive entry changes full GBR rebase, nested helper continuity or restore')
    if value['active']:
        frame_event(0x4BE48,'write',-22,value['inner_raw'],0,2)
        frame_event(0x26286,'read',-24,value['inner_argument'],5)
        prior_upper=observed['frame_before'][136:138]
        if (value['inner_argument'].to_bytes(4,'big')!=prior_upper+value['inner_raw'].to_bytes(2,'big')
                or row(0x26286)['after']['registers'][5]!=value['inner_argument']
                or row(0x26288)['before']['registers'][5]!=value['inner_argument']
                or row(0x26288)['after']['registers'][5]!=value['inner_raw']):
            raise ValueError('the timing additive entry substitutes a low16 scalar for the actual full local carrier')
        expected_load=value['inner_raw']-(65536 if value['inner_raw']&32768 else 0)
        if row(0x4BE48)['before']['registers'][0]!=(expected_load&0xFFFFFFFF):
            raise ValueError('the timing additive local write changes the actual sign-extending RAM word register')
        if (row(0x4BE5A)['before']['registers'][0]!=value['surface_return']
                or row(0x4BE5C)['after']['registers'][6]!=(value['surface_return']&65535)
                or row(0x4BE68)['before']['registers'][0]!=value['surface']):
            raise ValueError('the timing additive surface changes a complete returned register, unsigned extension or cap')
        if row(0x4BE82)['after']['registers'][1]!=value['product']:
            raise ValueError('the timing additive entry substitutes a product for its actual delayed helper argument')
        if (row(0x4BE90)['before']['registers'][6]!=value['candidate']
                or row(0x4BE90)['after']['registers'][0]!=value['candidate']
                or row(0x4BE92)['before']['registers'][0]!=value['candidate']
                or row(0x4BE94)['before']['registers'][6]!=value['candidate']
                or row(0x4BE96)['before']['registers'][6]!=value['candidate']
                or row(0x4BE96)['after']['registers'][2]!=value['candidate']):
            raise ValueError('the timing additive reader detaches publication from complete live R6/R2 continuity')
    if not value['alternate']:
        term=value['candidate'] if value['active'] else 0
        if (row(0x4BE9E)['before']['registers'][2]!=term
                or row(0x4BEA0)['before']['registers'][0]!=term
                or row(0x4BEA2)['before']['registers'][2]!=term
                or row(0x4BEA2)['after']['registers'][14]!=(value['composed']&0xFFFFFFFF)):
            raise ValueError('the timing additive compositor changes its actual active or explicit zero contribution')
    if row(0x4BEE2)['before']['registers'][2]!=(value['signed_value']&0xFFFFFFFF):
        raise ValueError('the timing additive output substitutes a matching byte for its full signed register')
    if any(r['mode']=='read' and r['address']==RAM_BASE+0x134A for r in result['accesses']):
        raise ValueError('the timing additive entry invents a physical134A read for its live-register quantity')
