"""Finite exact natural caller operands, helper carriers and complete state continuity."""
from kb import test_contract
from kb import map_bias_division_caller_withdrawal_contract as contract

OPERANDS={138464: ('write', 4, 2, 'pre', 15, 0, 0),
 138502: ('read', 4, 2, 'post', 15, 0, 0),
 138508: ('write', 4, 3, 'pre', 15, 0, 0),
 138596: ('read', 4, 3, 'post', 15, 0, 0),
 138600: ('read', 4, 2, 'post', 15, 0, 0),
 138602: ('read', 4, 1, 'fixed', 138696, 0, 0),
 138604: ('read', 4, 2, 'fixed', 138700, 0, 0),
 138606: ('write', 4, 2, 'base', 1, 0, 0),
 138612: ('read', 4, 2, 'post', 15, 0, 0),
 138692: ('read', 4, 2, 'post', 15, 0, 0),
 156384: ('write', 4, 'pr', 'pre', 15, 0, 0),
 156386: ('write', 4, 4, 'pre', 15, 0, 0),
 156394: ('read', 4, 7, 'fixed', 156440, 0, 0),
 156400: ('write', 4, 5, 'pre', 15, 0, 0),
 156402: ('write', 4, 4, 'pre', 15, 0, 0),
 156406: ('read', 4, 5, 'offset', 15, 16, 0),
 156410: ('read', 4, 7, 'fixed', 156444, 0, 0),
 156416: ('read', 4, 0, 'post', 15, 0, 0),
 156418: ('read', 4, 1, 'post', 15, 0, 0),
 156426: ('read', 4, 4, 'post', 15, 0, 0),
 156428: ('read', 4, 'pr', 'post', 15, 0, 0),
 156430: ('read', 4, 7, 'fixed', 156436, 0, 0),
 157508: ('write', 4, 0, 'pre', 15, 0, 0),
 157522: ('read', 4, 2, 'post', 15, 0, 0),
 157768: ('write', 4, 8, 'pre', 15, 0, 0),
 157770: ('write', 4, 'pr', 'pre', 15, 0, 0),
 157790: ('read', 4, 7, 'fixed', 157856, 0, 0),
 157796: ('read', 2, 1, 'base', 4, 0, 0),
 157798: ('read', 2, 0, 'offset', 4, 2, 0),
 157810: ('write', 4, 0, 'pre', 15, 0, 0),
 157812: ('read', 2, 1, 'base', 5, 0, 0),
 157814: ('read', 2, 0, 'offset', 5, 2, 0),
 157824: ('read', 4, 0, 'post', 15, 0, 0),
 157838: ('read', 2, 0, 'base', 4, 0, 0),
 157840: ('read', 2, 2, 'base', 5, 0, 0),
 157850: ('read', 4, 'pr', 'post', 15, 0, 0),
 157854: ('read', 4, 8, 'post', 15, 0, 0),
 158086: ('read', 2, 1, 'indexed', 4, 0, 0),
 158108: ('read', 2, 1, 'base', 0, 0, 0),
 158110: ('read', 2, 0, 'offset', 0, 2, 0),
 158116: ('write', 4, 'pr', 'pre', 15, 0, 0),
 158118: ('read', 4, 2, 'fixed', 158144, 0, 0),
 158126: ('read', 4, 'pr', 'post', 15, 0, 0),
 158222: ('read', 1, 1, 'indexed', 4, 0, 0),
 158250: ('read', 1, 1, 'base', 3, 0, 0),
 158252: ('read', 1, 0, 'offset', 3, 1, 0),
 158266: ('write', 4, 'pr', 'pre', 15, 0, 0),
 158268: ('read', 4, 2, 'fixed', 158296, 0, 0),
 158276: ('read', 4, 'pr', 'post', 15, 0, 0),
 158844: ('write', 4, 2, 'pre', 15, 0, 0),
 158980: ('read', 4, 2, 'post', 15, 0, 0),
 459462: ('write', 4, 12, 'pre', 15, 0, 0),
 459464: ('write', 4, 13, 'pre', 15, 0, 0),
 459466: ('write', 4, 14, 'pre', 15, 0, 0),
 459468: ('write', 4, 'pr', 'pre', 15, 0, 0),
 459470: ('write', 4, 'gbr', 'pre', 15, 0, 0),
 459472: ('read', 4, 0, 'fixed', 459952, 0, 0),
 459478: ('read', 4, 12, 'fixed', 459952, 0, 0),
 459480: ('read', 2, 0, 'fixed', 459770, 0, 0),
 459482: ('read', 1, 6, 'indexed', 12, 0, 0),
 459484: ('read', 2, 0, 'fixed', 459772, 0, 0),
 459486: ('read', 1, 2, 'indexed', 12, 0, 0),
 459488: ('read', 2, 0, 'fixed', 459774, 0, 0),
 459494: ('read', 2, 2, 'indexed', 12, 0, 0),
 459498: ('read', 4, 13, 'fixed', 459956, 0, 0),
 459504: ('read', 2, 2, 'indexed', 12, 0, 0),
 459518: ('read', 4, 13, 'fixed', 459956, 0, 0),
 459524: ('read', 2, 2, 'indexed', 12, 0, 0),
 459542: ('write', 2, 0, 'offset', 'gbr', 414, 0),
 459546: ('write', 2, 0, 'offset', 15, 2, 0),
 459548: ('read', 2, 0, 'fixed', 459776, 0, 0),
 459550: ('read', 4, 4, 'fixed', 459960, 0, 0),
 459552: ('read', 2, 14, 'indexed', 12, 0, 0),
 459554: ('read', 4, 5, 'fixed', 459964, 0, 0),
 459556: ('read', 4, 6, 'fixed', 459968, 0, 0),
 459558: ('read', 4, 2, 'fixed', 459972, 0, 0),
 459588: ('read', 2, 0, 'fixed', 459778, 0, 0),
 459592: ('write', 2, 2, 'indexed', 12, 0, 0),
 459610: ('read', 4, 6, 'fixed', 459976, 0, 0),
 459616: ('read', 2, 4, 'indexed', 6, 0, 0),
 459618: ('read', 4, 6, 'fixed', 459980, 0, 0),
 459640: ('read', 2, 0, 'fixed', 459774, 0, 0),
 459642: ('write', 2, 2, 'indexed', 12, 0, 0),
 459646: ('read', 4, 'gbr', 'post', 15, 0, 0),
 459648: ('read', 4, 'pr', 'post', 15, 0, 0),
 459650: ('read', 4, 14, 'post', 15, 0, 0),
 459652: ('read', 4, 13, 'post', 15, 0, 0),
 459656: ('read', 4, 12, 'post', 15, 0, 0)}

EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
# The exact fifth word is FFFF, so26984 returns its last offset with fraction0.
# The minimum biased caller term is10; its final divisor is always5..32762.
# The complete bodies retain their uncalled sibling/fault instructions.
INFEASIBLE_SITES=(set(range(0x26996,0x269BC,2))|set(range(0x26864,0x2688A,2))
    |set(range(0x21D6A,0x21DC6,2))|{0x26D0A,0x26D0C,0x70352,0x70354})
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={0x26990:'fallthrough',0x26994:'taken',0x26862:'taken',
    0x26C7A:'fallthrough',0x21CE4:'fallthrough',0x21CEA:'fallthrough',0x70350:'taken'}
ORIGINAL='4ab4eef347a3af18890ac2e967e38f483d8b48d5322c8cebffc136692bf01688'
NATIVE_ROOTS=((ORIGINAL,0x942C,None),)


def same(actual,wanted,reason):
    if not test_contract.exact(actual,wanted):raise ValueError(reason)


def require_physical_carriers(observed,result,fixture):
    """Check fixed domain operand declarations against live carriers and original bytes."""
    memory=bytearray(observed['memory_before'][0]);frame=bytearray(observed['frame_before']);all_events=[]
    sp=observed['sp']
    for row in result['trace']:
        rule=OPERANDS.get(row['site']);events=[]
        if rule is not None:
            mode,width,register,form,base,offset,immediate=rule;before=row['before'];after=row['after']
            if form=='fixed':address=base
            else:
                address=before['gbr'] if base=='gbr' else before['registers'][base]
                address=(address+(before['registers'][0] if form=='indexed' else -width if form=='pre' else offset))&0xFFFFFFFF
            if address%width:raise ValueError('the map-bias caller physical operand loses its natural alignment')
            if 0x01000000<=address<=0x01010000-width:
                data,at,domain=memory,address-0x01000000,'ram'
            elif sp-160<=address<=sp+32-width:data,at,domain=frame,address-sp+160,'frame'
            elif 0<=address<=len(fixture)-width:data,at,domain=fixture,address,'rom'
            else:raise ValueError('the map-bias caller physical operand leaves complete declared ROM,RAM or frame storage')
            def event(direction,raw):
                events.append(dict(site=row['site'],mode=direction,address=address,width_bytes=width,
                    register=register if type(register) is int else None,domain=domain,bytes=raw.hex()))
            incoming=bytes(data[at:at+width])
            if mode in ('read','and','or','tst'):event('read',incoming)
            if mode=='read':
                value=int.from_bytes(incoming,'big')
                if width<4 and value&(1<<(width*8-1)):value|=0xFFFFFFFF^((1<<(width*8))-1)
                actual=after['registers'][register] if type(register) is int else after[register]
                if actual!=value:raise ValueError('the map-bias caller physical load changes the complete live destination carrier')
            elif mode in ('write','and','or'):
                if domain=='rom':raise ValueError('the map-bias caller natural closure writes a bound ROM operand')
                if mode=='write':value=before['registers'][register] if type(register) is int else before[register]
                else:
                    value=int.from_bytes(incoming,'big');value=value&immediate if mode=='and' else value|immediate
                raw=(value&((1<<(width*8))-1)).to_bytes(width,'big');data[at:at+width]=raw;event('write',raw)
        same(row['accesses'],events,'the map-bias caller closure changes a complete declared physical site,address,mode,width,register or byte')
        all_events.extend(events)
    same(result['accesses'],all_events,'the map-bias caller closure omits or invents an ordered physical operand')
    same((result['ram'],result['frame']),(bytes(memory),bytes(frame)),
        'the map-bias caller complete physical carrier projection changes final RAM or frame bytes')


def call_span(trace,call,cursor=0):
    start=next((i for i in range(cursor,len(trace)) if trace[i]['site']==call['site']),None)
    if start is None or start+2>=len(trace) or trace[start+2]['site']!=call['target']:
        raise ValueError('the map-bias caller loses a natural call delay slot or exact real target')
    after=start+2
    terminal=next((i for i in range(after,len(trace)-1) if trace[i]['word']==0x000B
        and trace[i+1]['next']==call['return_address']),None)
    if terminal is None:raise ValueError('the map-bias caller lacks an exact natural post-delay callee return')
    return after,terminal+1


def require(observed,result,value,fixture):
    same(observed['exit'],(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        'the map-bias caller changes complete independently reconstructed exit CPU/SR state')
    same((observed['frame_after'],observed['memory_after']),(result['frame'],(result['ram'],)),
        'the map-bias caller changes complete reconstructed frame or ordinary RAM')
    same((result['frame'],result['ram']),(value['frame'],value['ram']),
        'the map-bias caller changes separate complete frame or numerical RAM equations')
    if any(result['registers'][index]!=raw for index,raw in value['known_registers'].items()):
        raise ValueError('the map-bias caller changes an independently composed complete returned carrier')
    if (result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']
            or any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp'))):
        raise ValueError('the map-bias caller changes independent SR,frame or special-register return equations')
    same([row for row in result['accesses'] if row['domain']=='ram' and row['mode']=='write'],value['writes'],
        'the map-bias caller changes an independent ordered physical store,carrier,width or actual byte')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the map-bias caller omits its complete instruction trace')
    require_physical_carriers(observed,result,fixture)
    initial=trace[0]['before']
    same(tuple(initial[key] for key in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the map-bias caller detaches its complete natural instruction entry state')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the map-bias caller changes a feasible exact instruction,path or natural continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],
            'the map-bias caller detaches complete intermediate CPU/SR state')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the map-bias caller changes an exact executed stock instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the map-bias caller loses a real call,branch,tail jump or return delay slot')
    roots=[call for call in result['calls'] if 0x702C6<=call['site']<0x7038A]
    expected=([(0x702F4,0x22590)] if value['same_mode'] else [])+[
        (0x70328,0x262E0),(0x7035E,0x22590),(0x70368,0x21CE0)]
    same([(row['site'],row['target']) for row in roots],expected,
        'the map-bias caller changes its complete independently selected root call order')
    if any(call['sp']!=observed['sp']-24 for call in roots):
        raise ValueError('the map-bias caller changes its actual local fifth-word or callee stack position')
    allowed=set(expected)|{(0x262EC,0x26A0C),(0x262FC,0x26984)}
    if value['lookup']['axis']['division'] is not None:allowed.add((0x26A40,0x26C78))
    if value['lookup']['axis']['fraction']:allowed.add((0x26896,0x26740))
    calls={}
    for call in result['calls']:
        key=call['site'],call['target']
        if key not in allowed or key in calls:raise ValueError('the map-bias caller adds,duplicates or substitutes a natural helper')
        start,end=call_span(trace,call);entered=trace[start]['before'];returned=trace[end]['after']
        same(tuple(call['entry'][key] for key in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the map-bias caller changes complete actual post-delay helper entry state')
        if (returned['registers'][15]!=call['sp'] or returned['pr']!=call['return_address']
                or call['return_address']!=call['site']+4):
            raise ValueError('the map-bias helper changes a natural post-delay SP,PR or return')
        calls[key]=(call,start,end,returned)
    if set(calls)!=allowed:raise ValueError('the map-bias caller omits a separately required real helper call')
    for site,argument,answer in ([(0x702F4,(value['prior']-value['other'])&0xFFFFFFFF,value['first_term'])]
            if value['same_mode'] else [])+[(0x7035E,value['signed_source']&0xFFFFFFFF,value['magnitude'])]:
        call,start,end,returned=calls[site,0x22590]
        if call['entry']['registers'][4]!=argument or (returned['registers'][0],returned['registers'][4])!=(answer,answer):
            raise ValueError('the map-bias caller replaces an exact bounded signed-word/difference helper with a supplied scalar')
    call,start,end,returned=calls[0x70328,0x262E0]
    if (call['entry']['registers'][4:8]!=(0xE98E,0x11D0C,0x14114,value['query'])
            or returned['registers'][0]!=value['lookup']['raw_return']):
        raise ValueError('the map-bias lookup changes its actual table,axes,coordinate or complete returned word carrier')
    stack=next((row for row in trace[:start] if row['site']==0x7031A),None)
    if stack is None or stack['accesses']!=[dict(site=0x7031A,mode='write',address=call['sp']+2,
            width_bytes=2,register=0,domain='frame',bytes='ffff')]:
        raise ValueError('the map-bias lookup loses the actual complete parent fifth-word store')
    tail=next((index for index,row in enumerate(trace) if row['site']==0x26310),None)
    if (tail is None or tail+1>=len(trace) or trace[tail]['next']!=0x26312
            or trace[tail+1]['site']!=0x26312 or trace[tail+1]['delay_slot'] is not True
            or trace[tail+1]['next']!=0x26848):
        raise ValueError('the map-bias wrapper omits its original natural tail jump')
    call,start,end,returned=calls[0x262EC,0x26A0C]
    regs=call['entry']['registers'];axis=value['lookup']['axis']
    if (regs[0],regs[4],regs[5])!=(0x11D0C,15,value['query']) or (returned['registers'][4],returned['registers'][5])!=(axis['index'],axis['fraction']):
        raise ValueError('the map-bias first axis changes its exact raw shifted-byte search or fraction return')
    call,start,end,returned=calls[0x262FC,0x26984]
    regs=call['entry']['registers']
    if (regs[0],regs[4],regs[5])!=(0x14114,30,0xFFFF) or (returned['registers'][4],returned['registers'][5])!=(30,0):
        raise ValueError('the map-bias second axis changes the exact live FFFF premise or last-word return')
    if axis['division'] is not None:
        call,start,end,returned=calls[0x26A40,0x26C78];regs=call['entry']['registers'];division=axis['division']
        if tuple(regs[:2])!=(division['denominator'],division['numerator']) or returned['registers'][0]!=axis['fraction']:
            raise ValueError('the map-bias caller changes its actual positive local fractional division')
    if axis['fraction']:
        call,start,end,returned=calls[0x26896,0x26740];regs=call['entry']['registers']
        if (regs[0],regs[2],regs[3])!=(value['lookup']['low'],value['lookup']['high'],axis['fraction']) or returned['registers'][0]!=value['lookup']['value']:
            raise ValueError('the map-bias caller changes its actual neighbor interpolation carriers or returned result')
    call,start,end,returned=calls[0x70368,0x21CE0]
    if tuple(call['entry']['registers'][:2])!=(value['denominator'],value['numerator']) or returned['registers'][0]!=value['quotient']:
        raise ValueError('the map-bias caller changes its actual positive unsigned division or full returned quotient')
    if (trace[-1]['next']!=observed['continuation'] or result['sp']!=observed['sp']
            or result['pr']!=observed['continuation'] or result['gbr']!=observed['context'][15]):
        raise ValueError('the map-bias caller changes its complete natural post-delay return')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],row['owner'],row['function']) for row in rows)
    same(identities,((ORIGINAL,0x942C,'rev_limit_throttle_cut/tbl',0x702C6),),
        'the map-bias caller substitutes its one exact selected direct-reader original')
    if any(row['address']<0x942E and 0x942C<row['address']+row['width_bytes'] for row in result['accesses']):
        raise ValueError('the map-bias caller physically overlaps either byte of the selected scalar')
