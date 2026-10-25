"""Complete third-trim leaf CPU/frame state, indexed word and shared-bank effects."""
from kb import test_contract
from kb import third_trim_word_writer_contract as contract

RAM_BASE=0x01000000
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
INFEASIBLE_SITES=set()
FEASIBLE_SITES=EXACT_SITES
FIXED_BRANCHES={}

def same(a,b,reason):
    if not test_contract.exact(a,b):raise ValueError(reason)

def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the third-trim entry changes complete independently reconstructed exit CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the third-trim entry changes complete frame or separate numerical RAM/publication equations')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the third-trim entry omits its complete natural instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the third-trim entry detaches its complete initial CPU from the immutable observed input')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the third-trim entry changes a complete stock instruction, feasible path or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the third-trim entry detaches intermediate complete CPU/frame control state')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},
        'the third-trim entry changes executed instruction identities')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the third-trim entry omits or invents a real control delay slot')
    literal=contract.LITERAL_OPERANDS
    actual=[]
    for event in result['accesses']:
        if event['domain']=='frame':continue
        if event['site'] in literal:
            at,width,register=literal[event['site']]
            same(event,dict(site=event['site'],mode='read',address=at,width_bytes=width,register=register,
                domain='rom',bytes=fixture[at:at+width].hex()),'the third-trim entry changes an exact PC literal operand')
        else:actual.append({key:event[key] for key in ('site','mode','address','width_bytes','register','domain','bytes')})
    same(actual,value['operands'],'the third-trim entry changes ordered actual ROM/RAM site, address, width, direction or complete bytes')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the third-trim entry invents or omits a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            (expected['site'],expected['target'],expected['return_address'],observed['sp']+expected['sp_delta']),
            'the third-trim entry changes a real helper target, continuation or exact call frame')
        entered=actual['entry']
        if (entered['sp']!=actual['sp'] or entered['pr']!=expected['return_address']
                or any(entered['registers'][register]!=raw for register,raw in expected['arguments'].items())):
            raise ValueError('the third-trim entry changes a separate actual post-delay arithmetic argument')
        start=next((i+2 for i in range(cursor,len(trace)-2) if trace[i]['site']==expected['site']),None)
        if start is None or trace[start]['site']!=expected['target']:
            raise ValueError('the third-trim entry replaces the real post-delay helper entry')
        before=trace[start]['before'];cursor=start
        same(tuple(entered[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
            'the third-trim entry detaches complete helper-entry CPU from its preceding delay slot')
        terminal=next((i for i in range(start,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches'])
            and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the third-trim entry omits a real natural helper return')
        returned=trace[terminal+1]['after']
        if (returned['registers'][15]!=actual['sp'] or returned['pr']!=expected['return_address']
                or any(returned['registers'][register]!=raw for register,raw in expected.get('returned',{}).items())):
            raise ValueError('the third-trim entry changes independent returned helper arithmetic, PR or SP')
    controls={(row['site'],row['target']) for row in result['branches'] if row['kind']=='jump'}
    if not set(value['tails'])<=controls:raise ValueError('the third-trim entry substitutes a real helper tail or delay-slot path')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind']!=FIXED_BRANCHES[row['site']]:
            raise ValueError('the third-trim entry forces an impossible caller-scoped branch outcome')
    if result['sp']!=observed['sp'] or result['pr']!=observed['continuation']:
        raise ValueError('the third-trim entry changes its complete natural outer return')
    if observed['entry']!=contract.ENTRY or trace[0]['site']!=contract.ENTRY:
        raise ValueError('the third-trim word writer changes its complete natural entry')
    if (result['gbr'],result['mach'],result['macl'])!=tuple(observed['context'][15:18]):
        raise ValueError('the third-trim word writer changes a preserved complete special register')
    if result['sr']&~0x301!=observed['sr_before']&~0x301:
        raise ValueError('the third-trim word writer changes preserved interrupt or other SR controls')
    def frame_event(site,mode,delta,raw,register):
        rows=[r for r in result['accesses'] if r['site']==site and r['domain']=='frame']
        same(rows,[dict(site=site,mode=mode,address=observed['sp']+delta,width_bytes=4,
            register=register,domain='frame',bytes=raw.to_bytes(4,'big').hex())],
            'the third-trim leaf changes a complete outer saved register word or restoration')
    for site,register in zip(range(0x5B534,0x5B540,2),range(9,15)):
        frame_event(site,'write',-(register-8)*4,observed['context'][register],register)
    for site,register in zip((0x5B6F6,0x5B6F8,0x5B6FA,0x5B6FC,0x5B6FE,0x5B702),(14,13,12,11,10,9)):
        frame_event(site,'read',-(register-8)*4,observed['context'][register],register)
    if any(result['registers'][r]!=observed['context'][r] for r in range(8,15)):
        raise ValueError('the third-trim leaf changes a complete preserved general register')
    if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'])!=(0x5B700,0x5B702,True):
        raise ValueError('the third-trim leaf replaces its natural RTS-delay full R9 restore')
    if result['calls'] or value['calls'] or any(r['kind']=='call' for r in result['branches']):
        raise ValueError('the complete third-trim leaf invents a stock call or substituted helper')
    expected_sr=(observed['sr_before']&~1)|int(not value['shared'])
    if result['sr']!=expected_sr:
        raise ValueError('the third-trim leaf changes preserved complete SR/M/Q or its actual final mode T')
    def row(site):
        found=[r for r in trace if r['site']==site]
        if len(found)!=1:raise ValueError('the third-trim leaf duplicates or omits a required writer instruction')
        return found[0]
    if (value['channel']!=(observed['context'][4]&255) or value['mask']!=value['channel']+1
            or row(0x5B54A)['after']['registers'][4]!=value['channel']
            or row(0x5B54C)['after']['registers'][4]!=value['mask']):
        raise ValueError('the third-trim entry changes its actual low8 channel or channel-plus-one mask')
    write=row(0x5B6F0)
    if (write['before']['registers'][0]!=value['channel']*2
            or write['before']['registers'][11]!=RAM_BASE+0x2A24
            or write['before']['registers'][2]!=value['full_word_register']
            or result['registers'][2]!=value['full_word_register']):
        raise ValueError('the third-trim writer substitutes matching low16 bytes for the full indexed R2 store')
    if value['shared']:
        if (row(0x5B6F2)['before']['registers'][2]!=value['full_word_register']
                or row(0x5B6F2)['after']['registers'][0]!=value['full_word_register']
                or row(0x5B6F4)['before']['registers'][0]!=value['full_word_register']):
            raise ValueError('the third-trim shared writer detaches the complete R2-to-R0 copy')
    elif any(r['site'] in (0x5B6F2,0x5B6F4) for r in trace):
        raise ValueError('the ordinary third-trim mode invents a shared-bank write')
    expected_r0=value['full_word_register'] if value['shared'] else value['channel']*2
    if result['registers'][0]!=expected_r0:
        raise ValueError('the third-trim leaf changes its complete returned R0')
    if value['ramp']:
        old=value['accumulator_before']
        below_neutral=old>=0x80000000 or old<0x6400
        event_site=0x5B6B8 if below_neutral else 0x5B6D4
        if row(event_site)['before']['registers'][7]!=value['accumulator']:
            raise ValueError('the third-trim counter write loses its full signed32 converging register')
