"""Complete per-phase CPU/frame state, exact physical quantity flow and real delayed calls."""
from kb import test_contract
from kb import coasting_term_quantity_contract as contract

RAM_BASE=0x01000000
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
INFEASIBLE_SITES={*range(0x26A60,0x26A80,2),*range(0x26A9C,0x26AAA,2),
    0x4717E,0x47180,0x47278,0x4727A}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={0x25E56:'fallthrough',0x25E5E:'fallthrough',0x4717C:'taken',
    0x26A9A:'taken',0x47276:'taken'}

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
        raise ValueError('the coasting phase changes its complete natural entry')
    if (result['gbr'],result['mach'],result['macl'])!=tuple(observed['context'][15:18]):
        raise ValueError('the coasting phase changes a preserved complete special register')
    if result['sr']&~1!=observed['sr_before']&~1:
        raise ValueError('the coasting phase changes preserved I/M/Q or other SR controls')
    def frame_event(site,mode,delta,raw,register=None):
        rows=[r for r in result['accesses'] if r['site']==site and r['domain']=='frame']
        same(rows,[dict(site=site,mode=mode,address=observed['sp']+delta,width_bytes=4,
            register=register,domain='frame',bytes=raw.to_bytes(4,'big').hex())],
            'the coasting phase changes an exact outer saved word or restoration')
    if phase==0:
        frame_event(0x2C626,'write',-4,observed['continuation'])
        frame_event(0x2C63E,'read',-4,observed['continuation'])
        if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'])!=(0x2C640,0x2C642,True):
            raise ValueError('the coasting producer replaces its natural RTS-delay second publication')
        for site,at in ((0x2C63C,0x1230),(0x2C642,0x126E)):
            row,=[row for row in trace if row['site']==site]
            if row['before']['registers'][6]!=value['value']:
                raise ValueError('the coasting producer substitutes matching bytes for its complete unsigned byte result')
    else:
        for site,delta,register in ((0x47120,-4,12),(0x47122,-8,13)):
            frame_event(site,'write',delta,observed['context'][register],register)
        frame_event(0x47124,'write',-12,observed['continuation'])
        frame_event(0x47126,'write',-16,observed['context'][15])
        frame_event(0x4735A,'read',-16,observed['context'][15])
        frame_event(0x4735C,'read',-12,observed['continuation'])
        frame_event(0x4735E,'read',-8,observed['context'][13],13)
        frame_event(0x47362,'read',-4,observed['context'][12],12)
        if any(result['registers'][r]!=observed['context'][r] for r in (12,13)):
            raise ValueError('the coasting consumer changes complete saved R12/R13')
        if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'])!=(0x47360,0x47362,True):
            raise ValueError('the coasting consumer replaces its real RTS-delay full R12 restore')
        row,=[r for r in trace if r['site']==0x47356]
        if row['before']['registers'][13]!=value['publication_register_value']:
            raise ValueError('the coasting consumer replaces its full live publication register with matching word bytes')
        sentinel=[c for c in result['calls'] if c['site']==0x47176]
        if sentinel and sentinel[0]['entry']['registers'][4]!=0xFFFFFFFF:
            raise ValueError('the coasting consumer changes its actual minus-one diagnostic sentinel')

def require_handoff(producer,consumer,pvalue,cvalue):
    if (producer['phase']!=0 or consumer['phase']!=1 or producer['pair']!=consumer['pair']
            or producer['memory_after']!=consumer['memory_before']
            or not test_contract.exact(producer['calibration_after'],consumer['calibration_before'])
            or producer['bound_after']!=consumer['bound_before']):
        raise ValueError('the coasting pair resets or detaches complete actual RAM/calibration/code continuity')
    for at,raw in pvalue['handoff'].items():
        wanted=raw.to_bytes(2,'big')
        if producer['memory_after'][0][at:at+2]!=wanted or consumer['memory_before'][0][at:at+2]!=wanted:
            raise ValueError('the coasting handoff changes either complete actual producer publication')
    reads=[r for r in cvalue['operands'] if r['address']==RAM_BASE+0x1230]
    expected=(0x4726E,0x47282) if cvalue['quantity'] is not None else ()
    if tuple(r['site'] for r in reads)!=expected or any(r['mode']!='read' or r['width_bytes']!=2
            or r['bytes']!=pvalue['value'].to_bytes(2,'big').hex() for r in reads):
        raise ValueError('the coasting consumer substitutes a synthetic quantity for an actual carried word read')
    if cvalue['source_word'] is not None and cvalue['source_word']!=pvalue['value']:
        raise ValueError('the coasting consumer detaches its actual source word from the complete producer')
