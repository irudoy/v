"""Complete timing-state CPU/frame/SR and actual engine-speed coordinate transfer admission."""
from kb import test_contract
from kb import engine_speed_curve_input_contract as contract

RAM_BASE=0x01000000
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
INFEASIBLE_SITES={
    *range(0x21BCC,0x21BD0,2),0x21BFE,0x21C00,*range(0x21C08,0x21CD6,2),
    *range(0x21CEC,0x21D76,2),*range(0x26A60,0x26A80,2),
    *range(0x26A9C,0x26AAA,2),0x26D0A,0x26D0C}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={
    0x21BC0:'fallthrough',0x21BCA:'taken',0x21BDC:'fallthrough',
    0x21BE4:'fallthrough',0x21BFC:'taken',
    0x21CE4:'fallthrough',0x21CEA:'taken',0x26A9A:'taken',0x26C7A:'fallthrough'}

def same(a,b,reason):
    if not test_contract.exact(a,b):raise ValueError(reason)

def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the engine-speed curve input entry changes complete independently reconstructed exit CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the engine-speed curve input entry changes complete frame or separate numerical RAM/publication equations')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the engine-speed curve input entry omits its complete natural instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the engine-speed curve input entry detaches its complete initial CPU from the immutable observed input')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the engine-speed curve input entry changes a complete stock instruction, feasible path or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the engine-speed curve input entry detaches intermediate complete CPU/frame control state')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},
        'the engine-speed curve input entry changes executed instruction identities')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the engine-speed curve input entry omits or invents a real control delay slot')
    literal=contract.LITERAL_OPERANDS
    actual=[]
    for event in result['accesses']:
        if event['domain']=='frame':continue
        if event['site'] in literal:
            at,width,register=literal[event['site']]
            same(event,dict(site=event['site'],mode='read',address=at,width_bytes=width,register=register,
                domain='rom',bytes=fixture[at:at+width].hex()),'the engine-speed curve input entry changes an exact PC literal operand')
        else:actual.append({key:event[key] for key in ('site','mode','address','width_bytes','register','domain','bytes')})
    same(actual,value['operands'],'the engine-speed curve input entry changes ordered actual ROM/RAM site, address, width, direction or complete bytes')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the engine-speed curve input entry invents or omits a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            (expected['site'],expected['target'],expected['return_address'],observed['sp']+expected['sp_delta']),
            'the engine-speed curve input entry changes a real helper target, continuation or exact call frame')
        entered=actual['entry']
        if (entered['sp']!=actual['sp'] or entered['pr']!=expected['return_address']
                or any(entered['registers'][register]!=raw for register,raw in expected['arguments'].items())):
            raise ValueError('the engine-speed curve input entry changes a separate actual post-delay arithmetic argument')
        start=next((i+2 for i in range(cursor,len(trace)-2) if trace[i]['site']==expected['site']),None)
        if start is None or trace[start]['site']!=expected['target']:
            raise ValueError('the engine-speed curve input entry replaces the real post-delay helper entry')
        before=trace[start]['before'];cursor=start
        same(tuple(entered[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
            'the engine-speed curve input entry detaches complete helper-entry CPU from its preceding delay slot')
        terminal=next((i for i in range(start,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches'])
            and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the engine-speed curve input entry omits a real natural helper return')
        returned=trace[terminal+1]['after']
        if (returned['registers'][15]!=actual['sp'] or returned['pr']!=expected['return_address']
                or any(returned['registers'][register]!=raw for register,raw in expected.get('returned',{}).items())):
            raise ValueError('the engine-speed curve input entry changes independent returned helper arithmetic, PR or SP')
    controls={(row['site'],row['target']) for row in result['branches'] if row['kind']=='jump'}
    if not set(value['tails'])<=controls:raise ValueError('the engine-speed curve input entry substitutes a real helper tail or delay-slot path')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind']!=FIXED_BRANCHES[row['site']]:
            raise ValueError('the engine-speed curve input entry forces an impossible caller-scoped branch outcome')
    if result['sp']!=observed['sp'] or result['pr']!=observed['continuation']:
        raise ValueError('the engine-speed curve input entry changes its complete natural outer return')
    if observed['entry']!=contract.ENTRY or trace[0]['site']!=contract.ENTRY:
        raise ValueError('the engine-speed curve input candidate changes its complete natural entry')
    if (result['gbr'],result['mach'],result['macl'])!=tuple(observed['context'][15:18]):
        raise ValueError('the engine-speed curve input candidate changes a preserved complete special register')
    if result['sr']&~0x301!=observed['sr_before']&~0x301:
        raise ValueError('the engine-speed curve input candidate changes preserved interrupt or other SR controls')
    def frame_event(site,mode,delta,raw,register=None,width=4):
        rows=[r for r in result['accesses'] if r['site']==site and r['domain']=='frame']
        same(rows,[dict(site=site,mode=mode,address=observed['sp']+delta,width_bytes=width,
            register=register,domain='frame',bytes=raw.to_bytes(width,'big').hex())],
            'the engine-speed curve input entry changes a complete outer saved word, local argument or restoration')
    for index,register in enumerate(range(9,15)):
        frame_event(0x4AFDC+index*2,'write',-4*(index+1),observed['context'][register],register)
    frame_event(0x4AFE8,'write',-28,observed['continuation'])
    frame_event(0x4AFEA,'write',-32,observed['context'][17])
    frame_event(0x4AFEC,'write',-36,observed['context'][15])
    frame_event(0x4B54A,'read',-36,observed['context'][15])
    frame_event(0x4B54C,'read',-32,observed['context'][17])
    frame_event(0x4B54E,'read',-28,observed['continuation'])
    for index,register in enumerate(range(14,8,-1)):
        site=0x4B55C if register==9 else 0x4B550+index*2
        frame_event(site,'read',-24+index*4,observed['context'][register],register)
    if any(result['registers'][r]!=observed['context'][r] for r in range(8,15)):
        raise ValueError('the speed-coordinate entry changes a complete preserved general register')
    if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'])!=(0x4B55A,0x4B55C,True):
        raise ValueError('the speed-coordinate entry replaces its natural RTS-delay full R9 restore')
    def row(site):
        rows=[r for r in trace if r['site']==site]
        if len(rows)!=1:
            raise ValueError('the speed-coordinate entry omits or duplicates a required root instruction')
        return rows[0]
    def sx(value,bits):
        return (value-(1<<bits) if value&(1<<(bits-1)) else value)&0xFFFFFFFF
    start=trace.index(row(0x4AFF0))
    finish=trace.index(row(0x4B54A))
    if (trace[start]['after']['gbr']!=RAM_BASE+0x128C
            or any(r['before']['gbr']!=RAM_BASE+0x128C for r in trace[start+1:finish+1])
            or trace[finish]['after']['gbr']!=observed['context'][15]):
        raise ValueError('the speed-coordinate entry changes full GBR rebase, helper continuity or restoration')
    for site,register in ((0x4B2D4,0),(0x4B2DE,0),(0x4B378,2)):
        event=row(site)
        if (event['after']['registers'][register]!=event['before']['sr']
                or event['after']['sr']!=event['before']['sr']):
            raise ValueError('the speed-coordinate entry masks or detaches a complete actual STC SR value')
    for site,register in ((0x4B2E6,0),(0x4B380,2)):
        event=row(site)
        if event['after']['sr']!=event['before']['registers'][register]&0x0FFF0FFF:
            raise ValueError('the speed-coordinate entry changes the actual architectural LDC SR operation')
    saved_I=row(0x4B2D4)['before']['sr']&0xF0
    current=row(0x4B378)['before']['sr']
    restored=row(0x4B380)['after']['sr']
    critical_start=trace.index(row(0x4B2E6))
    critical_end=trace.index(row(0x4B380))
    if (row(0x4B2E6)['after']['sr']&0xF0!=0xF0
            or any(r['before']['sr']&0xF0!=0xF0 for r in trace[critical_start+1:critical_end+1])
            or restored&0xF0!=saved_I or restored&~0xF0!=current&~0xF0):
        raise ValueError('the speed-coordinate entry detaches saved I or replaces current M/Q/T and other SR controls')
    selected={'first':(0x4B054,0x4B058,0x4B060),
              'second':(0x4B08A,0x4B08E,0x4B096),
              'third':(0x4B0B4,0x4B0B8,0x4B0BE)}
    if value['speed_branch'] in selected:
        load,call,extension=selected[value['speed_branch']]
        delay=call+2
        coordinate=value['speed_coordinate']
        if (row(load)['after']['registers'][2]!=sx(coordinate,8)
                or row(delay)['before']['registers'][2]!=sx(coordinate,8)
                or row(delay)['after']['registers'][5]!=coordinate
                or row(extension)['before']['registers'][0]!=value['speed_return']
                or row(extension)['after']['registers'][6]!=value['speed_byte']):
            raise ValueError('the speed reader detaches the actual signed RAM load, post-delay R5 or full curve return')
    elif (value['speed_branch']!='substitute'
            or row(0x4B0AC)['after']['registers'][6]!=value['speed_return']):
        raise ValueError('the speed substitute changes its actual complete sign-extending source register')
    expected_reads=1 if value['speed_branch'] in selected else 0
    reads=[r for r in result['accesses'] if r['mode']=='read' and r['address']==RAM_BASE+0x11B2]
    if len(reads)!=expected_reads or any(r['width_bytes']!=1 or r['register']!=2 for r in reads):
        raise ValueError('the speed association changes the exact conditional RAM11B2 footprint')
    if row(0x4B0D0)['before']['registers'][2]!=value['speed_register']&0xFFFFFFFF:
        raise ValueError('the speed reader substitutes a published byte for its complete centered source register')
    if value['hot']:
        frame_event(0x4B164,'write',-40,value['base_return']&255,0,1)
        if value['correction_path'] in ('hot-two-curves','hot-growth'):
            site=0x4B17E if value['correction_path']=='hot-two-curves' else 0x4B1C2
            frame_event(site,'read',-40,value['base_return']&255,0,1)
    if row(0x4B2D2)['before']['registers'][0]!=value['quantity']:
        raise ValueError('the speed-coordinate caller changes its actual full correction publication')
    if value['surfaces_enabled']:
        lookups=[r for r in value['lookups'] if r['kind']=='byte-surface']
        if len(lookups)!=2:
            raise ValueError('the speed-coordinate caller loses one complete surface input equation')
        actual=[r for r in result['accesses'] if r['site']==0x26156 and r['domain']=='frame']
        expected=[dict(site=0x26156,mode='read',address=observed['sp']-44,width_bytes=4,
            register=5,domain='frame',bytes=r['inner_argument'].to_bytes(4,'big').hex()) for r in lookups]
        same(actual,expected,'the speed-coordinate caller changes either actual full32 local carrier')
        for site,lookup in zip((0x4B396,0x4B3B8),lookups):
            frame_event(site,'write',-41,lookup['inner_raw'],0,1)
            if (lookup['inner_argument'].to_bytes(4,'big')!=observed['frame_before'][116:119]+bytes([lookup['inner_raw']])
                    or row(site)['before']['registers'][0]!=sx(lookup['inner_raw'],8)):
                raise ValueError('the speed-coordinate caller substitutes a byte for the complete original high24 carrier')
        loaded=[r for r in trace if r['site']==0x26156]
        extended=[r for r in trace if r['site']==0x26158]
        if len(loaded)!=2 or len(extended)!=2:
            raise ValueError('the speed-coordinate caller omits or duplicates its full32 argument promotion')
        for read,extension,lookup in zip(loaded,extended,lookups):
            if (read['after']['registers'][5]!=lookup['inner_argument']
                    or extension['before']['registers'][5]!=lookup['inner_argument']
                    or extension['after']['registers'][5]!=lookup['inner_raw']):
                raise ValueError('the speed-coordinate caller narrows the actual carrier before its stock EXTU.B')
        if (row(0x4B3A6)['before']['registers'][0]!=value['surface_results'][0]
                or row(0x4B3AC)['before']['registers'][2]!=value['surface_results'][0]
                or row(0x4B3C6)['before']['registers'][0]!=value['surface_results'][1]
                or row(0x4B3CA)['before']['registers'][6]!=value['surface_results'][1]):
            raise ValueError('the speed-coordinate caller changes complete surface-return publication registers')
    if (row(0x4B3F0)['before']['registers'][2]!=value['surface_term']&0xFFFFFFFF
            or row(0x4B418)['before']['registers'][2]!=value['factor']
            or row(0x4B4A0)['before']['registers'][0]!=value['addon']
            or row(0x4B4BC)['before']['registers'][4]!=value['addon']
            or row(0x4B546)['before']['registers'][2]!=value['signed_value']&0xFFFFFFFF):
        raise ValueError('the speed-coordinate caller replaces an actual full arithmetic or final publication register')
    published=value['speed_register']&255
    if row(0x4B4B0)['after']['registers'][7]!=sx(published,8):
        raise ValueError('the speed-coordinate caller detaches the final signed read of the actual1511 publication')
