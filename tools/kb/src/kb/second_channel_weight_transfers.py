"""Complete second-channel CPU/frame state and published full-R5 weight continuity."""
from kb import test_contract
from kb import second_channel_weight_contract as contract

RAM_BASE=0x01000000
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
INFEASIBLE_SITES={*range(0x21D76,0x21DC6,2),0x26DA2,0x26DA4}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={0x21CEA:'fallthrough',0x26D12:'fallthrough'}

def same(a,b,reason):
    if not test_contract.exact(a,b):raise ValueError(reason)

def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the second-channel weight entry changes complete independently reconstructed exit CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the second-channel weight entry changes complete frame or separate numerical RAM/publication equations')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the second-channel weight entry omits its complete natural instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the second-channel weight entry detaches its complete initial CPU from the immutable observed input')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the second-channel weight entry changes a complete stock instruction, feasible path or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the second-channel weight entry detaches intermediate complete CPU/frame control state')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},
        'the second-channel weight entry changes executed instruction identities')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the second-channel weight entry omits or invents a real control delay slot')
    literal=contract.LITERAL_OPERANDS
    actual=[]
    for event in result['accesses']:
        if event['domain']=='frame':continue
        if event['site'] in literal:
            at,width,register=literal[event['site']]
            same(event,dict(site=event['site'],mode='read',address=at,width_bytes=width,register=register,
                domain='rom',bytes=fixture[at:at+width].hex()),'the second-channel weight entry changes an exact PC literal operand')
        else:actual.append({key:event[key] for key in ('site','mode','address','width_bytes','register','domain','bytes')})
    same(actual,value['operands'],'the second-channel weight entry changes ordered actual ROM/RAM site, address, width, direction or complete bytes')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the second-channel weight entry invents or omits a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            (expected['site'],expected['target'],expected['return_address'],observed['sp']+expected['sp_delta']),
            'the second-channel weight entry changes a real helper target, continuation or exact call frame')
        entered=actual['entry']
        if (entered['sp']!=actual['sp'] or entered['pr']!=expected['return_address']
                or any(entered['registers'][register]!=raw for register,raw in expected['arguments'].items())):
            raise ValueError('the second-channel weight entry changes a separate actual post-delay arithmetic argument')
        start=next((i+2 for i in range(cursor,len(trace)-2) if trace[i]['site']==expected['site']),None)
        if start is None or trace[start]['site']!=expected['target']:
            raise ValueError('the second-channel weight entry replaces the real post-delay helper entry')
        before=trace[start]['before'];cursor=start
        same(tuple(entered[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
            'the second-channel weight entry detaches complete helper-entry CPU from its preceding delay slot')
        terminal=next((i for i in range(start,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches'])
            and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the second-channel weight entry omits a real natural helper return')
        returned=trace[terminal+1]['after']
        if (returned['registers'][15]!=actual['sp'] or returned['pr']!=expected['return_address']
                or any(returned['registers'][register]!=raw for register,raw in expected.get('returned',{}).items())):
            raise ValueError('the second-channel weight entry changes independent returned helper arithmetic, PR or SP')
    controls={(row['site'],row['target']) for row in result['branches'] if row['kind']=='jump'}
    if not set(value['tails'])<=controls:raise ValueError('the second-channel weight entry substitutes a real helper tail or delay-slot path')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind']!=FIXED_BRANCHES[row['site']]:
            raise ValueError('the second-channel weight entry forces an impossible caller-scoped branch outcome')
    if result['sp']!=observed['sp'] or result['pr']!=observed['continuation']:
        raise ValueError('the second-channel weight entry changes its complete natural outer return')
    if observed['entry']!=contract.ENTRY or trace[0]['site']!=contract.ENTRY:
        raise ValueError('the second-channel weight candidate changes its complete natural entry')
    if (result['gbr'],result['mach'],result['macl'])!=tuple(observed['context'][15:18]):
        raise ValueError('the second-channel weight candidate changes a preserved complete special register')
    if result['sr']&~0x301!=observed['sr_before']&~0x301:
        raise ValueError('the second-channel weight candidate changes preserved interrupt or other SR controls')
    def frame_event(site,mode,delta,raw,register=None,width=4):
        rows=[r for r in result['accesses'] if r['site']==site and r['domain']=='frame']
        same(rows,[dict(site=site,mode=mode,address=observed['sp']+delta,width_bytes=width,
            register=register,domain='frame',bytes=raw.to_bytes(width,'big').hex())],
            'the second-channel weight entry changes a complete outer saved word, local argument or restoration')
    for index,register in enumerate(range(8,15)):
        frame_event(0x7A804+index*2,'write',-4*(index+1),observed['context'][register],register)
    frame_event(0x7A812,'write',-32,observed['continuation'])
    frame_event(0x7A814,'write',-36,observed['context'][17])
    frame_event(0x7A984,'read',-36,observed['context'][17])
    frame_event(0x7A986,'read',-32,observed['continuation'])
    for index,register in enumerate(range(14,7,-1)):
        site=0x7A996 if register==8 else 0x7A988+index*2
        frame_event(site,'read',-28+index*4,observed['context'][register],register)
    if any(result['registers'][r]!=observed['context'][r] for r in range(8,15)):
        raise ValueError('the second-channel entry changes a complete preserved general register')
    if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'])!=(0x7A994,0x7A996,True):
        raise ValueError('the second-channel entry replaces its natural RTS-delay full R8 restore')
    def row(site):
        found=[r for r in trace if r['site']==site]
        if len(found)!=1:
            raise ValueError('the second-channel entry duplicates or omits a required quantity instruction')
        return found[0]
    if not value['substitute']:
        frame_event(0x7A878,'write',-38,value['inner_raw'],0,2)
        frame_event(0x26606,'read',-40,value['inner_argument'],5)
        high=observed['frame_before'][120:122]
        if (value['inner_argument'].to_bytes(4,'big')!=high+value['inner_raw'].to_bytes(2,'big')
                or row(0x7A878)['before']['registers'][0]!=value['inner_raw']
                or row(0x26606)['after']['registers'][5]!=value['inner_argument']
                or row(0x26608)['before']['registers'][5]!=value['inner_argument']
                or row(0x26608)['after']['registers'][5]!=value['inner_raw']):
            raise ValueError('the second-channel entry substitutes a scalar for its full32 original local carrier')
        if (row(0x7A886)['before']['registers'][0]!=value['surface_return']
                or row(0x7A886)['after']['registers'][5]!=value['surface_return']):
            raise ValueError('the second-channel weight detaches the complete actual surface return')
    elif row(0x7A864)['after']['registers'][5]!=value['weight_return']:
        raise ValueError('the second-channel substitute changes its sign-extending raw word register')
    if (row(0x7A88C)['before']['registers'][5]!=value['weight_return']
            or row(0x7A88E)['before']['registers'][5]!=value['weight_return']
            or row(0x7A88E)['after']['registers'][5]!=value['weight']
            or row(0x7A890)['before']['registers'][5]!=value['weight']
            or row(0x7A890)['after']['registers'][2]!=value['complement']):
        raise ValueError('the second-channel reader detaches actual35F4 from full pre/post-extension R5')
    if (row(0x7A892)['before']['registers'][13]!=value['first_curve']
            or row(0x7A892)['before']['registers'][2]!=value['complement']
            or row(0x7A892)['after']['macl']!=value['first_product']
            or row(0x7A896)['after']['registers'][6]!=value['first_product']
            or row(0x7A898)['before']['registers'][14]!=value['second_curve']
            or row(0x7A898)['before']['registers'][5]!=value['weight']
            or row(0x7A898)['after']['macl']!=value['second_product']
            or row(0x7A89A)['after']['registers'][5]!=value['second_product']):
        raise ValueError('the second-channel blend changes complete wrapped products or actual operands')
    if value['sum_taken']:
        if row(0x7A8AA)['after']['registers'][5]!=value['summed']:
            raise ValueError('the second-channel blend changes its guarded wrapped32 sum')
    elif row(0x7A8A8)['after']['registers'][6]!=0:
        raise ValueError('the second-channel blend loses its actual zero-result delay slot')
    if (row(0x7A8B8)['before']['registers'][6]!=value['shifted']
            or row(0x7A8C8)['before']['registers'][2]!=value['blended']
            or row(0x7A8D6)['before']['registers'][2]!=value['common_curve']):
        raise ValueError('the second-channel blend substitutes narrow publications for full result registers')
    if (row(0x7A90A)['before']['registers'][14]!=value['selected']
            or row(0x7A90A)['before']['registers'][0]!=value['quotient']):
        raise ValueError('the second-channel guard narrows R14 or changes the actual first quotient')
    if not value['overflow']:
        if (row(0x7A926)['after']['macl']!=value['scaled_product']
                or row(0x7A934)['after']['registers'][6]!=(value['scaled_product']>>15)):
            raise ValueError('the second-channel scale changes its actual product or logical shift')
    if (row(0x7A93E)['before']['registers'][14]!=value['scaled']
            or row(0x7A950)['before']['registers'][14]!=value['chosen']
            or row(0x7A950)['before']['registers'][6]!=value['limit']
            or row(0x7A956)['after']['registers'][5]!=value['limited']):
        raise ValueError('the second-channel output changes coordinate replacement or the full unsigned cap')
    if (row(0x7A96C)['before']['registers'][5]!=value['output']
            or row(0x7A96C)['after']['macl']!=value['product']
            or row(0x7A970)['after']['registers'][6]!=800
            or row(0x7A972)['before']['registers'][5]!=value['output']
            or row(0x7A978)['after']['registers'][1]!=value['product']
            or row(0x7A97C)['after']['registers'][2]!=value['value']
            or row(0x7A980)['before']['registers'][2]!=value['value']):
        raise ValueError('the second-channel output detaches full R5, divisor800, multiplier727 or final R2')
    if any(r['mode']=='read' and r['address']==RAM_BASE+0x35F4 for r in result['accesses']):
        raise ValueError('the second-channel entry invents a physical prior35F4 read')
