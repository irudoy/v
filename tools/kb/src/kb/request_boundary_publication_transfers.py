"""Complete state, real delayed entries and independently ordered writer operands."""
from kb import test_contract
from kb import request_boundary_publication_contract as contract
from kb import request_boundary_publication_semantics as numeric
from kb.byte_surface_semantics import axis_position

MASK=0xFFFFFFFF
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
# Only26388 enters26A84. Its F0 selector takes the byte arm. All three
# signed-divider call sites have positive constant divisors and nonnegative
# bounded dividends; their negative/zero/large-divisor paths are excluded.
INFEASIBLE_SITES={*range(0x26A60,0x26A84,2),*range(0x26A9C,0x26AAA,2),
    0x21BCC,0x21BCE,0x21BFE,0x21C00,0x21C64,0x21C66,*range(0x21C70,0x21CD6,2),
    0x26D0A,0x26D0C,0x79668,0x79680,0x796B4,0x796CA}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={0x21BC0:'fallthrough',0x21BCA:'taken',0x21BDC:'fallthrough',
    0x21BFC:'taken',0x21C62:'taken',0x26A9A:'taken',0x26C7A:'fallthrough',
    0x79664:'taken',0x7967C:'taken',0x796B0:'taken',0x796C8:'taken'}
CALL_TARGETS={0x79DDA:0x797D0,0x797D2:0x79358,0x797D6:0x793D2,
    0x793AE:0x21BBC,0x793F2:0x26388,0x79420:0x259D0,0x79450:0x259D0,
    0x7947A:0x259D0,0x794B4:0x259D0,0x7969C:0x260BC,0x796E6:0x260BC,
    0x79728:0x21BBC,0x7977A:0x21BBC,0x260C8:0x26944,0x260D6:0x26944,0x2696A:0x26C78}
FIXED_STACK_DELTAS={0x79DDA:-4,0x797D2:-8,0x797D6:-8,0x793AE:-16,
    0x793F2:-68,0x79420:-68,0x79450:-68,0x7947A:-68,0x794B4:-68,
    0x7969C:-48,0x796E6:-48,0x79728:-48,0x7977A:-48,0x260C8:-56,0x260D6:-64}

def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)

def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the request original changes complete independently reconstructed exit CPU/SR')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the request original changes complete frame/RAM or independent complete stage equations')
    if value['fault']!=observed['memory_before'][0][0x9818:0x981C]:
        raise ValueError('the positive constant-divisor dispatcher changes its retained fault dword')
    trace=result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site']!=contract.ENTRY:
        raise ValueError('the request original lacks its complete natural dispatcher trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the request trace detaches its complete CPU from the immutable incoming context')
    for index,row in enumerate(trace):
        destination=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=destination
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the request original changes a complete instruction, caller-scoped path or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the request trace detaches an intermediate complete CPU state')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the request trace changes its complete executed instruction identities')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the request original omits or invents a real delay slot')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind']!=FIXED_BRANCHES[row['site']]:
            raise ValueError('the request original forces an impossible caller-scoped branch outcome')
    actual_boundary=[]
    calibration=observed['calibration_before']
    physical=getattr(contract,'PHYSICAL_OPERANDS',None)
    if type(physical) is not dict:raise ValueError('the request source omits its independently declared physical operands')
    for event in result['accesses']:
        site=event['site'];address=event['address'];width=event['width_bytes']
        if event['domain']=='frame':continue
        if site in contract.LITERAL_OPERANDS:
            at,size,register=contract.LITERAL_OPERANDS[site]
            same(event,dict(site=site,mode='read',address=at,width_bytes=size,register=register,domain='rom',
                bytes=fixture[at:at+size].hex()),'the request original changes an exact PC literal operand')
        elif site in physical:
            mode,at,size,register=physical[site]
            same(tuple(event[k] for k in ('mode','address','width_bytes','register','domain')),
                (mode,at,size,register,'ram'),'the request original changes a physical RAM site, address, width or register')
        else:
            if event['domain']!='rom' or event['mode']!='read' or not any(
                    at<=address and address+width<=at+len(raw) for at,raw in calibration.items()):
                raise ValueError('the request original accesses undeclared data outside its complete literal/RAM/calibration boundary')
            if event['bytes']!=fixture[address:address+width].hex():
                raise ValueError('the request original substitutes physical calibration bytes')
        if 0x79030<=site<0x7920A and site not in contract.LITERAL_OPERANDS:
            actual_boundary.append(event)
    same(actual_boundary,value['operands'],'the request original changes ordered independent signed-bound physical operands')
    expected=numeric.call_values(observed['memory_before'][0],calibration,value)
    ordinary=[call for call in result['calls'] if call['site'] in expected]
    if {call['site'] for call in ordinary}!=set(expected) or len(ordinary)!=len(expected):
        raise ValueError('the request original omits or duplicates a separate numerical natural helper call')
    cursor=0
    for call in result['calls']:
        site=call['site'];target=CALL_TARGETS.get(site)
        if target is None or call['target']!=target or call['return_address']!=site+4:
            raise ValueError('the request original changes a real helper call, target or continuation')
        if site in FIXED_STACK_DELTAS and call['sp']!=observed['sp']+FIXED_STACK_DELTAS[site]:
            raise ValueError('the request original changes a natural nested call frame')
        start=next((i+2 for i in range(cursor,len(trace)-2) if trace[i]['site']==site),None)
        if start is None or trace[start]['site']!=target:
            raise ValueError('the request original replaces its real post-delay helper entry')
        before=trace[start]['before'];cursor=start
        same(tuple(call['entry'][k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
            'the request original detaches complete helper-entry state from the real delay slot')
        if call['entry']['sp']!=call['sp'] or call['entry']['pr']!=site+4:
            raise ValueError('the request original changes actual delayed-entry SP or PR')
        terminal=next((i for i in range(start,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches'])
            and trace[i+1]['next']==site+4),None)
        if terminal is None:raise ValueError('the request original omits a real natural helper return')
        returned=trace[terminal+1]['after']
        if returned['registers'][15]!=call['sp'] or returned['pr']!=site+4:
            raise ValueError('the request original changes complete natural helper return SP or PR')
        if site in expected:
            independent=expected[site]
            if (independent['target']!=target
                    or any(call['entry']['registers'][register]!=(raw&MASK) for register,raw in independent['arguments'].items())
                    or any(returned['registers'][register]!=(raw&MASK) for register,raw in independent['returned'].items())):
                raise ValueError('the request original changes independent actual post-delay arguments or returned arithmetic')
        if target==0x26C78:
            divisor,dividend=call['entry']['registers'][:2]
            if not 0<divisor<=255 or dividend>0xFF0000 or returned['registers'][0]!=dividend//divisor:
                raise ValueError('the request axis call changes its actual positive independent division')
        elif target==0x26944:
            axis_address=0x12FEE if site==0x260C8 else 0x12FF2
            coordinate=observed['memory_before'][0][0x11AE] if site==0x260C8 else min(
                int.from_bytes(observed['memory_before'][0][0x40C6:0x40C8],'big')>>2,255)
            index,fraction=axis_position(calibration[axis_address],coordinate)
            if (call['entry']['registers'][0]!=axis_address or call['entry']['registers'][4]!=3
                    or call['entry']['registers'][5]!=coordinate
                    or returned['registers'][4]!=index or returned['registers'][5]!=fraction):
                raise ValueError('the request original changes a real lower-knot axis argument or independent return')
    # All three non-call tails retain the actual stack and PR state.
    by_site={row['site']:row for row in trace}
    for site,slot,target,delta,pr in ((0x797DA,0x797DC,0x79538,-4,0x79DDE),
            (0x79DE0,0x79DE2,0x79030,0,observed['continuation'])):
        branch=by_site.get(site);delay=by_site.get(slot)
        if (branch is None or delay is None or not delay['delay_slot'] or delay['next']!=target
                or delay['after']['registers'][15]!=observed['sp']+delta or delay['after']['pr']!=pr):
            raise ValueError('the request original replaces its actual staged tail or PR-restoring delay slot')
    publications=[event for event in result['accesses'] if event['site'] in (0x791A8,0x791B2)]
    if len(publications)!=1 or publications[0]['site']!=value['publication_site']:
        raise ValueError('the request original invents or omits its one actual retained word publication')
    actual_word=int.from_bytes(observed['memory_after'][0][0x19C6:0x19C8],'big')
    if (value['value']!=actual_word or value['value']!=(value['signed_value']&65535)
            or publications[0]['bytes']!=actual_word.to_bytes(2,'big').hex()):
        raise ValueError('the request original substitutes an independent scalar for the actual transformed word bytes')
    store=by_site[value['publication_site']]
    if store['before']['registers'][value['publication_register']]!=(value['signed_value']&MASK):
        raise ValueError('the request original substitutes matching bytes for its independently transformed live register')
    if result['sp']!=observed['sp'] or result['pr']!=observed['continuation']:
        raise ValueError('the request original changes its natural outer return')

CONDITIONAL_SITES=(138176, 138186, 138194, 138204, 138212, 138236, 138338, 138442, 154068, 156558, 157506, 158028, 158032, 158036, 158072, 158362, 158842, 495704, 495736, 495752, 495760, 495782, 495794, 495800, 495816, 495834, 495842, 495860, 495896, 495910, 495922, 495932, 495954, 495968, 495982, 495996, 496012, 496022, 496034, 496056, 496066, 496080, 496098, 496112, 496496, 496512, 496522, 496542, 496688, 496736, 496778, 496842, 496854, 496862, 496876, 496882, 496890, 496896, 496910, 496990, 497008, 497016, 497030, 497046, 497052, 497070, 497172, 497176, 497186, 497204, 497214, 497226, 497234, 497252, 497268, 497276, 497328, 497344, 497352, 497408, 497464, 497478, 497490, 497552, 497556, 497570, 497580)
