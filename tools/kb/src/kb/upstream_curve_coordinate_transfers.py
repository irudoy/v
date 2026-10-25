"""Complete upstream-curve caller state, actual source/argument path and natural frames."""
from kb import test_contract
from kb import upstream_curve_coordinate_contract as contract

RAM_BASE=0x01000000
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
INFEASIBLE_SITES={0x21BCC,0x21BCE,*range(0x21C70,0x21CD6,2),
    *range(0x21D6A,0x21DC6,2),0x26D0A,0x26D0C}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={0x21BC0:'fallthrough',0x21BCA:'taken',0x21BDC:'fallthrough',
    0x21CE4:'fallthrough',0x21CEA:'fallthrough',0x26C7A:'fallthrough',0xB7B4A:'fallthrough'}

def same(a,b,reason):
    if not test_contract.exact(a,b):raise ValueError(reason)

def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the upstream curve coordinate entry changes complete independently reconstructed exit CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the upstream curve coordinate entry changes complete frame or separate numerical RAM/publication equations')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the upstream curve coordinate entry omits its complete natural instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the upstream curve coordinate entry detaches its complete initial CPU from the immutable observed input')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the upstream curve coordinate entry changes a complete stock instruction, feasible path or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the upstream curve coordinate entry detaches intermediate complete CPU/frame control state')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},
        'the upstream curve coordinate entry changes executed instruction identities')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the upstream curve coordinate entry omits or invents a real control delay slot')
    literal=contract.LITERAL_OPERANDS
    actual=[]
    for event in result['accesses']:
        if event['domain']=='frame':continue
        if event['site'] in literal:
            at,width,register=literal[event['site']]
            same(event,dict(site=event['site'],mode='read',address=at,width_bytes=width,register=register,
                domain='rom',bytes=fixture[at:at+width].hex()),'the upstream curve coordinate entry changes an exact PC literal operand')
        else:actual.append({key:event[key] for key in ('site','mode','address','width_bytes','register','domain','bytes')})
    same(actual,value['operands'],'the upstream curve coordinate entry changes ordered actual ROM/RAM site, address, width, direction or complete bytes')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the upstream curve coordinate entry invents or omits a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            (expected['site'],expected['target'],expected['return_address'],observed['sp']+expected['sp_delta']),
            'the upstream curve coordinate entry changes a real helper target, continuation or exact call frame')
        entered=actual['entry']
        if (entered['sp']!=actual['sp'] or entered['pr']!=expected['return_address']
                or any(entered['registers'][register]!=raw for register,raw in expected['arguments'].items())):
            raise ValueError('the upstream curve coordinate entry changes a separate actual post-delay arithmetic argument')
        start=next((i+2 for i in range(cursor,len(trace)-2) if trace[i]['site']==expected['site']),None)
        if start is None or trace[start]['site']!=expected['target']:
            raise ValueError('the upstream curve coordinate entry replaces the real post-delay helper entry')
        before=trace[start]['before'];cursor=start
        same(tuple(entered[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
            'the upstream curve coordinate entry detaches complete helper-entry CPU from its preceding delay slot')
        terminal=next((i for i in range(start,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches'])
            and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the upstream curve coordinate entry omits a real natural helper return')
        returned=trace[terminal+1]['after']
        if (returned['registers'][15]!=actual['sp'] or returned['pr']!=expected['return_address']
                or any(returned['registers'][register]!=raw for register,raw in expected.get('returned',{}).items())):
            raise ValueError('the upstream curve coordinate entry changes independent returned helper arithmetic, PR or SP')
    controls={(row['site'],row['target']) for row in result['branches'] if row['kind']=='jump'}
    if not set(value['tails'])<=controls:raise ValueError('the upstream curve coordinate entry substitutes a real helper tail or delay-slot path')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind']!=FIXED_BRANCHES[row['site']]:
            raise ValueError('the upstream curve coordinate entry forces an impossible caller-scoped branch outcome')
    if result['sp']!=observed['sp'] or result['pr']!=observed['continuation']:
        raise ValueError('the upstream curve coordinate entry changes its complete natural outer return')
    if observed['entry']!=contract.ENTRY or trace[0]['site']!=contract.ENTRY:
        raise ValueError('the upstream curve coordinate candidate changes its complete natural entry')
    if (result['gbr'],result['mach'],result['macl'])!=tuple(observed['context'][15:18]):
        raise ValueError('the upstream-coordinate caller changes preserved complete special registers')
    if result['sr']&~0x301!=observed['sr_before']&~0x301:
        raise ValueError('the upstream-coordinate caller changes preserved I or other SR controls')
    if any(result['registers'][r]!=observed['context'][r] for r in range(8,15)):
        raise ValueError('the upstream-coordinate caller changes a complete preserved general register')
    def frame_event(site,mode,delta,raw,register=None,width=4):
        rows=[r for r in result['accesses'] if r['site']==site and r['domain']=='frame']
        same(rows,[dict(site=site,mode=mode,address=observed['sp']+delta,width_bytes=width,
            register=register,domain='frame',bytes=raw.to_bytes(width,'big').hex())],
            'the upstream-coordinate caller changes a complete saved word, fifth argument or local byte')
    for index,register in enumerate(range(11,15)):
        frame_event(0xB7A3C+index*2,'write',-4*(index+1),observed['context'][register],register)
    frame_event(0xB7A44,'write',-20,observed['continuation'])
    frame_event(0xB7A46,'write',-24,observed['context'][17])
    frame_event(0xB7A48,'write',-28,observed['context'][15])
    frame_event(0xB7B88,'read',-28,observed['context'][15])
    frame_event(0xB7B8A,'read',-24,observed['context'][17])
    frame_event(0xB7B8C,'read',-20,observed['continuation'])
    for index,register in enumerate(range(14,10,-1)):
        site=0xB7B96 if register==11 else 0xB7B8E+index*2
        frame_event(site,'read',-16+index*4,observed['context'][register],register)
    frame_event(0xB7A54,'write',-29,value['local_byte'],0,1)
    frame_event(0xB7A58,'read',0,value['fifth_word'],6,4)
    frame_event(0xB7A5E,'write',3,value['fifth_word']&255,6,1)
    frame_event(0xB7A68,'read',-29,value['local_byte'],0,1)
    frame_event(0xB7A9E,'read',3,value['fifth_word']&255,6,1)
    for entry,base,continuation in ((0x264CC,0x14E42,0xB7AB0),(0x264F8,0x151F2,0xB7B18)):
        frame_event(entry,'write',-36,continuation)
        frame_event(entry+2,'write',-40,base,4)
        frame_event(entry+14,'read',-40,base,6)
        frame_event(entry+26,'read',-36,continuation)
    if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'])!=(0xB7B94,0xB7B96,True):
        raise ValueError('the upstream-coordinate caller replaces its natural RTS-delay full R11 restore')
    def row(site):
        rows=[r for r in trace if r['site']==site]
        if len(rows)!=1:raise ValueError('the upstream-coordinate caller omits or duplicates a required root instruction')
        return rows[0]
    def sx(raw,bits):return (raw-(1<<bits) if raw&(1<<(bits-1)) else raw)&0xFFFFFFFF
    first,last=trace.index(row(0xB7A4C)),trace.index(row(0xB7B88))
    if (trace[first]['after']['gbr']!=0x8A30
            or any(r['before']['gbr']!=0x8A30 for r in trace[first+1:last+1])
            or trace[last]['after']['gbr']!=observed['context'][15]):
        raise ValueError('the upstream-coordinate caller changes its complete ROM GBR rebase or restoration')
    if (row(0xB7A50)['after']['registers'][1]!=observed['context'][6]
            or row(0xB7A54)['before']['registers'][0]!=observed['context'][7]
            or row(0xB7A58)['after']['registers'][6]!=value['fifth_word']
            or row(0xB7A5E)['before']['registers'][6]!=value['fifth_word']
            or observed['frame_before'][160:164]!=value['fifth_word'].to_bytes(4,'big')
            or observed['frame_after'][160:164]!=observed['frame_before'][160:164]):
        raise ValueError('the upstream-coordinate caller narrows or detaches a complete raw argument or original high24 carrier')
    if (row(0xB7A66)['before']['registers'][0]!=value['initial_quotient']&0xFFFFFFFF
            or row(0xB7A68)['after']['registers'][0]!=sx(value['local_byte'],8)
            or row(0xB7A6E)['before']['registers'][2]!=sx(value['local_byte'],8)
            or row(0xB7A6E)['after']['registers'][2]!=value['local_byte']
            or row(0xB7A76)['before']['registers'][5]!=value['adjusted']&0xFFFFFFFF
            or row(0xB7A94)['before']['registers'][2]!=value['initial_word']&0xFFFFFFFF
            or row(0xB7A94)['after']['registers'][5]!=value['narrowed']&0xFFFFFFFF
            or row(0xB7AA2)['before']['registers'][5]!=value['nonnegative']
            or row(0xB7AA2)['after']['registers'][14]!=value['nonnegative']):
        raise ValueError('the upstream-coordinate caller changes complete initial quotient, byte extension, signed clamps or live R14')
    fifth=value['fifth_word']&255
    if (row(0xB7A9E)['after']['registers'][6]!=sx(fifth,8)
            or row(0xB7AA4)['after']['registers'][6]!=fifth
            or row(0xB7AA8)['after']['registers'][6]!=value['source_coordinate']
            or row(0xB7AAE)['before']['registers'][6]!=value['source_coordinate']
            or row(0xB7AAE)['after']['registers'][6]!=value['source_coordinate']
            or row(0xB7AB0)['before']['registers'][0]!=value['source_return']
            or row(0xB7AB0)['after']['registers'][2]!=value['source_return']
            or row(0xB7ACA)['before']['registers'][2]!=value['source_return']
            or row(0xB7ACA)['after']['registers'][6]!=value['source_value']):
        raise ValueError('the upstream-coordinate caller detaches its real source coordinate or complete returned source value')
    curves=[r for r in value['lookups'] if r['kind']=='explicit-word-curve']
    if len(curves)!=2:raise ValueError('the upstream-coordinate caller omits a complete source or consumer lookup')
    for lookup in curves:
        entry=lookup['entry']
        if (row(entry+18)['after']['registers'][0]!=sx(lookup['second'],16)
                or row(entry+20)['before']['registers'][0]!=sx(lookup['second'],16)
                or row(entry+20)['after']['registers'][2]!=lookup['second']
                or row(entry+24)['after']['registers'][1]!=sx(lookup['first'],16)
                or row(entry+32)['before']['registers'][1]!=sx(lookup['first'],16)
                or row(entry+32)['after']['registers'][0]!=lookup['first']):
            raise ValueError('an upstream-coordinate lookup narrows either physical word before its real extension')
        index=trace.index(row(entry+30))+2
        if trace[index]['site']!=0x26740:raise ValueError('an upstream-coordinate lookup replaces its natural tail')
        entered=trace[index]['before']
        same((entered['registers'][0],entered['registers'][2],entered['registers'][3],
                entered['registers'][15],entered['pr']),
            (lookup['first'],lookup['second'],lookup['fraction'],observed['sp']-32,
                0xB7AB0 if entry==0x264CC else 0xB7B18),
            'an upstream-coordinate lookup detaches full tail arguments, SP or real continuation')
    if (row(0xB7AB6)['after']['registers'][12]!=sx(value['first_factor'],8)
            or row(0xB7AB8)['after']['registers'][6]!=value['first_factor']
            or row(0xB7ABA)['after']['macl']!=value['full_initial_product']
            or row(0xB7AC8)['after']['registers'][12]!=value['full_B']
            or row(0xB7B5E)['before']['registers'][12]!=value['full_B']
            or row(0xB7B5E)['after']['registers'][12]!=value['B']):
        raise ValueError('the upstream-coordinate caller substitutes a narrowed B word for its complete product, shift or sentinel')
    if (row(0xB7ACE)['before']['registers'][13]!=observed['context'][4]
            or row(0xB7ACE)['after']['registers'][13]!=value['H']
            or row(0xB7AD2)['after']['registers'][5]!=sx(value['ratio_factor'],8)
            or row(0xB7AD4)['before']['registers'][6]!=value['source_value']
            or row(0xB7AD4)['after']['registers'][2]!=(-value['source_value'])&0xFFFFFFFF
            or row(0xB7AD6)['after']['registers'][5]!=value['ratio_factor']
            or row(0xB7AD8)['after']['macl']!=value['ratio_product']
            or row(0xB7ADC)['after']['registers'][6]!=value['ratio_product']):
        raise ValueError('the upstream-coordinate caller detaches actual source/H extensions or its complete negative product')
    if value['H']:
        if (row(0xB7AE6)['after']['registers'][1]!=(value['ratio_product']*20)&0xFFFFFFFF
                or row(0xB7AEE)['before']['registers'][0]!=value['ratio_quotient']&0xFFFFFFFF):
            raise ValueError('the upstream-coordinate caller changes the real conditional signed division product or full quotient')
    if (row(0xB7B16)['before']['registers'][6]!=value['coordinate_before_extension']&0xFFFFFFFF
            or row(0xB7B16)['after']['registers'][6]!=value['consumer_coordinate']
            or row(0xB7B18)['before']['registers'][0]!=value['consumer_return']
            or row(0xB7B18)['after']['registers'][2]!=value['consumer_value']
            or row(0xB7B2C)['before']['registers'][5]!=value['full_inverse_weight']&0xFFFFFFFF
            or row(0xB7B3C)['before']['registers'][0]!=value['selector']
            or row(0xB7B62)['after']['registers'][5]!=value['inverse_weight']
            or row(0xB7B6E)['before']['registers'][14]!=value['full_coefficient']&0xFFFFFFFF
            or row(0xB7B6E)['after']['registers'][14]!=value['coefficient']):
        raise ValueError('the upstream-coordinate caller changes its actual derived delay-R6, full consumer return, weight or coefficient')
    if (row(0xB7B64)['after']['macl']!=value['first_product']
            or row(0xB7B70)['before']['registers'][0]!=value['first_quotient']
            or row(0xB7B74)['after']['macl']!=value['second_product']
            or row(0xB7B7C)['before']['registers'][0]!=value['second_quotient']
            or row(0xB7B7C)['after']['macl']!=value['value']
            or row(0xB7B84)['before']['registers'][2]!=value['value']
            or row(0xB7B84)['before']['registers'][6]!=RAM_BASE+0x28F8
            or row(0xB7B84)['before']['registers'][0]!=0x930):
        raise ValueError('the upstream-coordinate caller replaces an actual unsigned division, full final product or long publication register')
    if any(r['mode']=='read' and r['address']<RAM_BASE+0x322C and r['address']+r['width_bytes']>RAM_BASE+0x3228
            for r in result['accesses']):
        raise ValueError('the upstream-coordinate caller reads a cached output instead of its actual derived path')
