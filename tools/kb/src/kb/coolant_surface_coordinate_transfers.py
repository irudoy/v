"""Complete coolant-coordinate caller CPU/frame and actual two-coordinate transfers."""
from kb import test_contract
from kb import coolant_surface_coordinate_contract as contract

RAM_BASE=0x01000000
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
INFEASIBLE_SITES=set(range(0x26AAA,0x26AB4,2))
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={0x26A9A:'fallthrough'}

def same(a,b,reason):
    if not test_contract.exact(a,b):raise ValueError(reason)

def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the coolant surface coordinate entry changes complete independently reconstructed exit CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the coolant surface coordinate entry changes complete frame or separate numerical RAM/publication equations')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the coolant surface coordinate entry omits its complete natural instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the coolant surface coordinate entry detaches its complete initial CPU from the immutable observed input')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the coolant surface coordinate entry changes a complete stock instruction, feasible path or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the coolant surface coordinate entry detaches intermediate complete CPU/frame control state')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},
        'the coolant surface coordinate entry changes executed instruction identities')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the coolant surface coordinate entry omits or invents a real control delay slot')
    literal=contract.LITERAL_OPERANDS
    actual=[]
    for event in result['accesses']:
        if event['domain']=='frame':continue
        if event['site'] in literal:
            at,width,register=literal[event['site']]
            same(event,dict(site=event['site'],mode='read',address=at,width_bytes=width,register=register,
                domain='rom',bytes=fixture[at:at+width].hex()),'the coolant surface coordinate entry changes an exact PC literal operand')
        else:actual.append({key:event[key] for key in ('site','mode','address','width_bytes','register','domain','bytes')})
    same(actual,value['operands'],'the coolant surface coordinate entry changes ordered actual ROM/RAM site, address, width, direction or complete bytes')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the coolant surface coordinate entry invents or omits a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            (expected['site'],expected['target'],expected['return_address'],observed['sp']+expected['sp_delta']),
            'the coolant surface coordinate entry changes a real helper target, continuation or exact call frame')
        entered=actual['entry']
        if (entered['sp']!=actual['sp'] or entered['pr']!=expected['return_address']
                or any(entered['registers'][register]!=raw for register,raw in expected['arguments'].items())):
            raise ValueError('the coolant surface coordinate entry changes a separate actual post-delay arithmetic argument')
        start=next((i+2 for i in range(cursor,len(trace)-2) if trace[i]['site']==expected['site']),None)
        if start is None or trace[start]['site']!=expected['target']:
            raise ValueError('the coolant surface coordinate entry replaces the real post-delay helper entry')
        before=trace[start]['before'];cursor=start
        same(tuple(entered[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
            'the coolant surface coordinate entry detaches complete helper-entry CPU from its preceding delay slot')
        terminal=next((i for i in range(start,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches'])
            and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the coolant surface coordinate entry omits a real natural helper return')
        returned=trace[terminal+1]['after']
        if (returned['registers'][15]!=actual['sp'] or returned['pr']!=expected['return_address']
                or any(returned['registers'][register]!=raw for register,raw in expected.get('returned',{}).items())):
            raise ValueError('the coolant surface coordinate entry changes independent returned helper arithmetic, PR or SP')
    controls={(row['site'],row['target']) for row in result['branches'] if row['kind']=='jump'}
    if not set(value['tails'])<=controls:raise ValueError('the coolant surface coordinate entry substitutes a real helper tail or delay-slot path')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind']!=FIXED_BRANCHES[row['site']]:
            raise ValueError('the coolant surface coordinate entry forces an impossible caller-scoped branch outcome')
    if result['sp']!=observed['sp'] or result['pr']!=observed['continuation']:
        raise ValueError('the coolant surface coordinate entry changes its complete natural outer return')
    if observed['entry']!=contract.ENTRY or trace[0]['site']!=contract.ENTRY:
        raise ValueError('the coolant surface coordinate candidate changes its complete natural entry')
    if (result['gbr'],result['mach'],result['macl'])!=tuple(observed['context'][15:18]):
        raise ValueError('the coolant-coordinate caller changes a preserved complete special register')
    if result['sr']&~1!=observed['sr_before']&~1:
        raise ValueError('the coolant-coordinate caller changes preserved I/M/Q or other SR controls')
    if any(result['registers'][r]!=observed['context'][r] for r in range(8,15)):
        raise ValueError('the coolant-coordinate caller changes a complete preserved general register')
    def frame_event(site,mode,delta,raw,register=None,width=4):
        rows=[r for r in result['accesses'] if r['site']==site and r['domain']=='frame']
        same(rows,[dict(site=site,mode=mode,address=observed['sp']+delta,width_bytes=width,
            register=register,domain='frame',bytes=raw.to_bytes(width,'big').hex())],
            'the coolant-coordinate caller changes a complete outer or helper saved word')
    for site,mode,delta,raw,register in (
        (0x52576,'write',-4,observed['context'][14],14),
        (0x52578,'write',-8,observed['continuation'],None),
        (0x5257A,'write',-12,observed['context'][17],None),
        (0x5257C,'write',-16,observed['context'][15],None),
        (0x525CE,'read',-16,observed['context'][15],None),
        (0x525D0,'read',-12,observed['context'][17],None),
        (0x525D2,'read',-8,observed['continuation'],None),
        (0x525D6,'read',-4,observed['context'][14],14),
        (0x26040,'write',-20,0x52590,None),(0x26042,'write',-24,observed['context'][8],8),
        (0x26044,'write',-28,0xA8EA,4),(0x2605E,'read',-28,0xA8EA,4),
        (0x2606E,'read',-24,observed['context'][8],8),(0x26070,'read',-20,0x52590,None),
        (0x26770,'write',-20,observed['context'][8],8),(0x26772,'write',-24,0x52590,None),
        (0x267C0,'read',-24,0x52590,None),(0x267C4,'read',-20,observed['context'][8],8)):
        frame_event(site,mode,delta,raw,register)
    if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'])!=(0x525D4,0x525D6,True):
        raise ValueError('the coolant-coordinate caller replaces its natural RTS-delay full R14 restore')
    def row(site):
        rows=[r for r in trace if r['site']==site]
        if len(rows)!=1:raise ValueError('the coolant-coordinate caller omits or duplicates a required root instruction')
        return rows[0]
    def sx(raw,bits):return (raw-(1<<bits) if raw&(1<<(bits-1)) else raw)&0xFFFFFFFF
    first,last=trace.index(row(0x52580)),trace.index(row(0x525CE))
    if (trace[first]['after']['gbr']!=RAM_BASE+0x1068
            or any(r['before']['gbr']!=RAM_BASE+0x1068 for r in trace[first+1:last+1])
            or trace[last]['after']['gbr']!=observed['context'][15]):
        raise ValueError('the coolant-coordinate caller changes its full GBR rebase or restoration')
    coolant,inner=value['coolant_coordinate'],value['inner_coordinate']
    if (row(0x52582)['after']['registers'][0]!=sx(coolant,8)
            or row(0x52586)['before']['registers'][0]!=sx(coolant,8)
            or row(0x52586)['after']['registers'][5]!=coolant
            or row(0x52588)['after']['registers'][0]!=sx(inner,8)
            or row(0x5258E)['before']['registers'][0]!=sx(inner,8)
            or row(0x5258E)['after']['registers'][6]!=inner
            or row(0x26046)['after']['registers'][3]!=inner
            or row(0x2604A)['after']['registers'][4]!=coolant):
        raise ValueError('the coolant-coordinate caller detaches a complete signed load or actual unsigned R5/R6 argument')
    entered=row(0x26770)['before']
    same(tuple(entered['registers'][:6]),
        (value['row'],value['row_fraction'],value['column'],value['column_fraction'],0xA8EA,8),
        'the implicit surface tail changes a complete row, column, clamped fraction, base or stride')
    if entered['registers'][15]!=observed['sp']-16 or entered['pr']!=0x52590:
        raise ValueError('the implicit surface tail detaches its real restored wrapper SP/PR')
    if (row(0x52590)['before']['registers'][0]!=value['surface_return']
            or row(0x52590)['after']['registers'][14]!=value['surface_value']):
        raise ValueError('the coolant-coordinate caller substitutes an unsigned byte for its complete actual surface return')
    if (row(0x52592)['after']['registers'][0]!=sx(value['word_input'],16)
            or row(0x52596)['after']['registers'][2]!=value['word_input']
            or row(0x5259C)['after']['registers'][2]!=value['scaled_coordinate']
            or row(0x525A0)['before']['registers'][2]!=value['scaled_coordinate']
            or row(0x525AC)['after']['registers'][5]!=value['word_coordinate']
            or row(0x525AE)['before']['registers'][0]!=value['word_return']
            or row(0x525AE)['after']['registers'][2]!=value['word_value']):
        raise ValueError('the coolant-coordinate caller changes a full word load, shift, coordinate cap or signed return')
    if value['word_coordinate']<57344:
        kernel=row(0x26A60)['before']['registers']
        same((kernel[0],kernel[3],kernel[4],kernel[5]),(57344,0,0x14ED2,value['word_coordinate']),
            'the word tail changes its real entry bounds, zero fraction carrier or coordinate')
        if (row(0x26A94)['after']['registers'][3]!=value['lookups'][1]['fraction']
                or row(0x26A94)['after']['registers'][5]!=value['lookups'][1]['index']):
            raise ValueError('the word tail replaces its actual full fraction or shifted cell index')
    if (row(0x525B0)['before']['registers'][2]!=value['word_value']
            or row(0x525B0)['before']['registers'][14]!=value['surface_value']
            or row(0x525B0)['after']['macl']!=value['product']
            or row(0x525C0)['before']['registers'][6]!=value['shifted']
            or row(0x525CC)['before']['registers'][2]!=value['value']
            or row(0x525CC)['before']['registers'][6]!=RAM_BASE+0x128C
            or row(0x525CC)['before']['registers'][0]!=0x3C6):
        raise ValueError('the coolant-coordinate caller changes complete live product, shift, cap or publication registers')
    if any(r['mode']=='read' and r['address']<RAM_BASE+0x1654 and r['address']+r['width_bytes']>RAM_BASE+0x1652
            for r in result['accesses']):
        raise ValueError('the coolant-coordinate caller consumes prior1652 instead of its complete actual inputs')
