"""Exact comparator CPU, physical operands, local state, real helpers and live publications."""
from kb import test_contract
from kb import pedal_snapshot_high_state_contract as contract
RAM_BASE=0x01000000
MASK=0xFFFFFFFF
EXACT_SITES={at for a,b in contract.SPANS for at in range(a,b,2)}
FEASIBLE_SITES=EXACT_SITES-set(contract.DECLARED['caller_scoped_infeasible_sites'])
FIXED_BRANCHES={int(site):value for site,value in contract.DECLARED['caller_scoped_fixed_branches'].items()}
RAM_READS={155186: (22297, 1, 0),
 293498: (4366, 1, 2),
 293532: (9398, 1, 0),
 293536: (9310, 1, 0),
 293544: (9396, 1, 0),
 293546: (9838, 2, 14),
 293560: (6722, 2, 6),
 293572: (9396, 1, None),
 293574: (9396, 1, None),
 293576: (9396, 1, 0),
 293582: (9448, 1, 0),
 293606: (9431, 1, 0),
 293612: (9328, 1, 0),
 293620: (16975, 1, 0),
 293644: (9328, 1, 0),
 293662: (9310, 1, 0),
 293668: (9398, 1, 0),
 293768: (9398, 1, 0),
 293774: (9325, 1, 0),
 293780: (9838, 2, 6),
 293806: (9322, 1, None),
 293810: (9322, 1, None),
 293812: (9322, 1, 0),
 293824: (4366, 1, 6),
 293828: (9448, 1, 0),
 293872: (9431, 1, 0),
 293878: (9328, 1, 0),
 293886: (16975, 1, 0),
 293902: (9328, 1, 0),
 293906: (9398, 1, 0),
 293936: (9328, 1, None),
 293938: (9329, 1, 0),
 293952: (4526, 1, 4),
 293994: (4332, 1, 5),
 294130: (9322, 1, None),
 294134: (9322, 1, None),
 294138: (16772, 1, 0),
 294158: (9561, 1, 0),
 294194: (4526, 1, 5),
 294312: (4526, 1, 4),
 294328: (9328, 1, 0),
 294346: (9329, 1, 0),
 294356: (4209, 1, 0),
 294372: (4209, 1, 0),
 294384: (9329, 1, None),
 294388: (9329, 1, None),
 294390: (9328, 1, 0),
 294400: (4209, 1, 0),
 294418: (4132, 2, 6),
 294432: (4526, 1, 4),
 294444: (17076, 1, 2),
 294472: (4132, 2, 6),
 294486: (4526, 1, 4),
 294518: (9322, 1, 0),
 294530: (9329, 1, 0),
 294558: (9414, 1, None),
 294562: (9414, 1, None)}
STORES={293530: (6722, 2, 6),
 293572: (9396, 1, None),
 293574: (9396, 1, None),
 293598: (9448, 1, 0),
 293604: (9398, 1, 0),
 293806: (9322, 1, None),
 293810: (9322, 1, None),
 293864: (9448, 1, 0),
 293870: (9398, 1, 0),
 293916: (9431, 1, 0),
 293932: (9328, 1, 0),
 293936: (9328, 1, None),
 294130: (9322, 1, None),
 294134: (9322, 1, None),
 294152: (9561, 1, 0),
 294174: (9329, 1, 0),
 294324: (9329, 1, 0),
 294344: (9328, 1, 0),
 294384: (9329, 1, None),
 294388: (9329, 1, None),
 294458: (9328, 1, 0),
 294500: (9328, 1, 0),
 294510: (17076, 1, 2),
 294558: (9414, 1, None),
 294562: (9414, 1, None)}
ROM_READS={293482: (34572, 1, 0),
 293596: (35819, 1, 0),
 293638: (35647, 1, 0),
 293650: (35647, 1, 0),
 293656: (34572, 1, 0),
 293784: (36830, 2, 2),
 293796: (36828, 2, 2),
 293826: (36277, 1, 2),
 293862: (35819, 1, 0),
 293914: (33778, 1, 0),
 293946: (34573, 1, 0),
 293960: (34963, 1, 0),
 293968: (34962, 1, 0),
 293982: (34992, 1, 2),
 294000: (35236, 1, 2),
 294010: (36248, 1, 2),
 294020: (34994, 1, 2),
 294030: (36247, 1, 2),
 294040: (34962, 1, 0),
 294050: (35237, 1, 2),
 294058: (34963, 1, 0),
 294074: (36249, 1, 2),
 294084: (36251, 1, 2),
 294092: (34964, 1, 0),
 294108: (36250, 1, 2),
 294118: (36249, 1, 2),
 294150: (35821, 1, 0),
 294196: (34996, 1, 2),
 294314: (34993, 1, 2),
 294358: (36038, 1, 2),
 294374: (36037, 1, 2),
 294408: (35956, 1, 2),
 294422: (38198, 2, 2),
 294434: (34961, 1, 2),
 294462: (35957, 1, 2),
 294476: (38198, 2, 2),
 294488: (34961, 1, 2),
 294506: (35818, 1, 2)}


def same(actual,wanted,reason):
    if not test_contract.exact(actual,wanted):raise ValueError(reason)


def event(site,mode,address,width,register,domain,raw):
    return dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex())


def require(observed,result,value,fixture):
    same(observed['exit'],(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
         'the pedal comparator changes complete independent exit CPU/SR')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the pedal comparator changes complete frame, numerical publications or unrelated RAM')
    if (result['sp']!=observed['sp'] or result['pr']!=observed['continuation'] or result['registers'][0]!=0x6A
            or (result['gbr'],result['mach'],result['macl'])!=observed['context'][15:18]
            or tuple(result['registers'][8:15])!=observed['context'][8:15]):
        raise ValueError('the pedal comparator changes retained CPU, final offset or natural return')
    trace=result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site']!=contract.ENTRY:
        raise ValueError('the pedal comparator lacks complete natural entry trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
         ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
         'the pedal comparator detaches complete initial CPU from raw inputs')
    for index,row in enumerate(trace):
        destination=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        before_gbr=observed['context'][15] if (0x47A56<=row['site']<=0x47A64 or 0x47EA8<=row['site']<=0x47EB2) else RAM_BASE+0x245C
        if (row['site'] not in FEASIBLE_SITES or row['next']!=destination
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex() or row['before']['gbr']!=before_gbr):
            raise ValueError('the pedal comparator changes exact code, natural GBR or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the pedal comparator detaches intermediate CPU')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},'the pedal comparator changes executed words')
    if {r['site'] for r in trace if r['delay_slot']}!={r['site']+2 for r in result['branches'] if r['delay']}:
        raise ValueError('the pedal comparator omits or invents a real delay slot')
    for branch in result['branches']:
        if branch['site'] in FIXED_BRANCHES and branch['kind']!=FIXED_BRANCHES[branch['site']]:
            raise ValueError('the pedal comparator reaches an impossible immutable-control or fixed-argument path')
    memory=bytearray(observed['memory_before'][0]);writes=[];curve_reads=[]
    for operand in result['accesses']:
        site=operand['site']
        if operand['domain']=='ram':
            if operand['mode']=='read':
                if site not in RAM_READS:raise ValueError('the pedal comparator introduces an undeclared native read')
                at,width,register=RAM_READS[site]
                same(operand,event(site,'read',RAM_BASE+at,width,register,'ram',memory[at:at+width]),
                     'the pedal comparator changes actual RAM widths, addresses, values or registers')
            else:
                position=len(writes)
                if position>=len(value['publications']):raise ValueError('the pedal comparator adds an unrelated RAM write')
                pub=value['publications'][position]
                if pub['site'] not in STORES:raise ValueError('the pedal comparator numerical source substitutes a publication')
                at,width,register=STORES[pub['site']]
                if (at,width)!=(pub['address'],pub['size']):raise ValueError('the pedal comparator changes a physical numerical publication')
                raw=pub['value'].to_bytes(width,'big')
                same(operand,event(pub['site'],'write',RAM_BASE+at,width,register,'ram',raw),
                     'the pedal comparator changes ordered independent real publications')
                memory[at:at+width]=raw;writes.append(operand)
        elif operand['domain']=='rom':
            if site in contract.LITERAL_OPERANDS:
                at,width,register=contract.LITERAL_OPERANDS[site]
                same(operand,event(site,'read',at,width,register,'rom',fixture[at:at+width]),'the pedal comparator changes a PC literal')
            elif site in ROM_READS:
                at,width,register=ROM_READS[site]
                same(operand,event(site,'read',at,width,register,'rom',fixture[at:at+width]),'the pedal comparator changes an actual raw ROM control')
            elif site in (0x263E8,0x26AA0,0x26AA2):curve_reads.append(operand)
            else:raise ValueError('the pedal comparator introduces another ROM operand')
        elif operand['domain']!='frame':raise ValueError('the pedal comparator introduces another storage domain')
    if len(writes)!=len(value['publications']) or bytes(memory)!=value['memory']:
        raise ValueError('the pedal comparator omits an independent complete RAM publication')
    expected=[]
    if value['curve'] is not None:
        index=value['curve']['index'];at=0x1473A+2*index
        if index==7:expected.append(event(0x263E8,'read',at,2,0,'rom',fixture[at:at+2]))
        else:expected.extend((event(0x26AA0,'read',at,2,1,'rom',fixture[at:at+2]),
                              event(0x26AA2,'read',at+2,2,0,'rom',fixture[at+2:at+4])))
    same(curve_reads,expected,'the pedal comparator changes complete ordered physical uniform-curve words')
    local_base=observed['sp']-28
    actual=[(r['site'],r['mode'],r['address']-local_base,r['width_bytes'],int(r['bytes'],16))
        for r in result['accesses'] if r['domain']=='frame' and local_base<=r['address']
        and r['address']+r['width_bytes']<=local_base+4]
    same(actual,[(r['site'],r['mode'],0,1,r['value']) for r in value['locals']],
         'the pedal comparator changes its actual local request byte or conditional accesses')
    calls=[]
    if value['curve_mode']:calls.append(0x47A90)
    if value['diagnostic'] is not None:calls.append(0x47AFC if value['curve_mode'] else 0x47C06)
    same([r['site'] for r in result['calls']],calls,'the pedal comparator changes actual helper order')
    for call in result['calls']:
        site=call['site'];target=0x263D8 if site==0x47A90 else 0x25E20
        if call['target']!=target or call['sp']!=observed['sp']-28 or call['return_address']!=site+4:
            raise ValueError('the pedal comparator changes a real helper target, SP or PR')
        first=next((i+2 for i in range(len(trace)-2) if trace[i]['site']==site),None)
        if first is None or trace[first]['site']!=target:raise ValueError('the pedal comparator replaces a real post-delay entry')
        before=trace[first]['before']
        same(tuple(call['entry'][k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
             (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
             'the pedal comparator detaches complete real helper operands')
        terminal=next((i for i in range(first,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches'])
            and trace[i+1]['next']==site+4),None)
        if terminal is None:raise ValueError('the pedal comparator omits a natural helper return')
        returned=trace[terminal+1]['after'];registers=call['entry']['registers']
        if returned['registers'][15]!=call['sp'] or returned['pr']!=site+4:
            raise ValueError('the pedal comparator changes helper return SP/PR')
        if target==0x263D8:
            coordinate=min(65535,observed['memory_before'][0][0x110E]<<11)
            if registers[4:6]!=(0x1473A,coordinate) or returned['registers'][0]!=(value['curve']['returned']&MASK):
                raise ValueError('the pedal comparator substitutes a live uniform-curve argument or signed return')
        elif registers[4]!=0 or returned['registers'][0]!=int(value['diagnostic']):
            raise ValueError('the pedal comparator substitutes its actual fixed diagnostic record or predicate')
    jumps=[(r['site'],r['target']) for r in result['branches'] if r['kind']=='jump']
    expected_jumps=[] if value['curve'] is None or value['curve']['index']==7 else [(0x263E2,0x26A60),(0x26AB6,0x26740)]
    same(jumps,expected_jumps,'the pedal comparator changes real uniform-kernel tail transfers')
    if value['curve'] is not None:
        store=next(r for r in trace if r['site']==0x47A9A)
        if store['before']['registers'][6]!=(value['curve']['returned']&MASK):
            raise ValueError('the pedal comparator substitutes matching low words for the complete live curve store')
