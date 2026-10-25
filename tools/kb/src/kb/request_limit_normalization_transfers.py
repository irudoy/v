"""Actual endpoint operands, positive divisions, live limits and complete caller state."""
from kb import test_contract
from kb import request_limit_normalization_contract as contract, request_limit_normalization_semantics as numeric

MASK=0xFFFFFFFF
EXACT_SITES={at for first,last in contract.SPANS for at in range(first,last,2)}
# Both caller divisors are positive. Signed division receives a nonnegative
# numerator and a divisor fitting uint16; its other entries remain separate
# complete-primary helper obligations.
INFEASIBLE_SITES={0x26D0A,0x26D0C,0x21BCC,0x21BCE,0x21BFE,0x21C00,0x21C64,0x21C66,
                 *range(0x21C70,0x21C7C,2),*range(0x21C7C,0x21CD6,2)}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
FIXED_BRANCHES={0x26C7A:'fallthrough',0x21BC0:'fallthrough',0x21BCA:'taken',0x21BDC:'fallthrough',
                0x21BFC:'taken',0x21C62:'taken'}
CALL_TARGETS={0x7AE94:0x7AF78,0x7AF98:0x264F8,0x7AFAA:0x264F8,0x26502:0x26984,0x269AA:0x26C78,
              0x7AFFA:0x21BBC,0x7B010:0x21BBC,0x7B026:0x21BBC}
STACK_DELTAS={0x7AE94:-32,0x7AF98:-64,0x7AFAA:-64,0x26502:-72,0x7AFFA:-64,0x7B010:-64,0x7B026:-64}
TABLE_SITES={0x2650A,0x26510}
AXIS_SITES={0x26986,0x2699C,0x2699E}

def same(actual,wanted,reason):
    if not test_contract.exact(actual,wanted):raise ValueError(reason)

def ram_event(site,mode,at,width,register,raw):
    return dict(site=site,mode=mode,address=0x01000000+at,width_bytes=width,register=register,domain='ram',bytes=raw.hex())

def ram_operands(memory,value):
    word=lambda n:(n&65535).to_bytes(2,'big')
    rows=[ram_event(0x7AF8E,'read',0x113C,2,7,memory[0x113C:0x113E]),
          ram_event(0x7AFA0,'read',0x113C,2,7,memory[0x113C:0x113E])]
    for site,at in ((0x7AFB4,0x338C),(0x7AFC6,0x338E),(0x7AFD6,0x3396)):
        rows.append(ram_event(site,'read',at,2,5,memory[at:at+2]))
    sites=(0x7B00E,0x7B024,0x7B040) if value['span'] else (0x7B038,0x7B03C,0x7B040)
    for site,at,raw in zip(sites,(0x3478,0x347A,0x347C),value['normalized']):rows.append(ram_event(site,'write',at,2,2,word(raw)))
    rows.extend([ram_event(0x7AE98,'read',0x2A7A,2,0,memory[0x2A7A:0x2A7C]),
        ram_event(0x7AEA2,'read',0x3478,2,6,word(value['normalized'][0])),
        ram_event(0x7AEAA,'read',0x41FB,1,14,memory[0x41FB:0x41FC]),
        ram_event(0x7AEAC,'read',0x424F,1,0,memory[0x424F:0x4250]),
        ram_event(0x7AEBA,'read',0x347A,2,5,word(value['normalized'][1])),
        ram_event(0x7AEC8,'read',0x347C,2,5,word(value['normalized'][2])),
        ram_event(0x7AED6,'read',0x41F3,1,0,memory[0x41F3:0x41F4])])
    if value['override']:rows.append(ram_event(0x7AEE4,'read',0x3026,2,4,memory[0x3026:0x3028]))
    rows.extend([ram_event(0x7AEF8,'write',0x41FB,1,14,bytes([value['first_status']])),
        ram_event(0x7AEFC,'read',0x41FB,1,0,bytes([value['first_status']])),
        ram_event(0x7AF0C,'write',0x41FB,1,2,bytes([value['second_status']]))])
    if value['mode_set']:rows.append(ram_event(0x7AF2A,'write',0x424F,1,0,bytes([value['request_status']])))
    else:
        rows.extend([ram_event(0x7AF30,'read',0x249B,1,0,memory[0x249B:0x249C]),
            ram_event(0x7AF3E,'write',0x424F,1,0,bytes([value['request_status']])),
            ram_event(0x7AF40,'read',0x10AE,2,0,memory[0x10AE:0x10B0]),
            ram_event(0x7AF4A,'read',0x2712,2,5,memory[0x2712:0x2714])])
    rows.append(ram_event(0x7AF5A,'write',0x412A,2,0,word(value['output'])))
    return rows

def require(observed,result,value,fixture):
    same(observed['exit'],(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
         'the normalization changes complete independently reconstructed exit CPU/SR')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the normalization changes a complete frame, unrelated RAM or independent numerical publication')
    if (result['sp']!=observed['sp'] or result['pr']!=observed['continuation'] or result['gbr']!=observed['context'][15]
            or result['mach']!=observed['context'][16] or result['macl']!=observed['context'][17]
            or tuple(result['registers'][8:15])!=observed['context'][8:15]):
        raise ValueError('the normalization changes a retained outer register, MACL, GBR or natural return')
    if (result['registers'][0]!=value['output'] or result['registers'][4]!=value['output'] or result['registers'][6]!=0x01004124):
        raise ValueError('the normalization changes its independently transformed final live operands')
    trace=result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site']!=contract.ENTRY:
        raise ValueError('the normalization lacks its complete natural entry trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
         ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
         'the normalization detaches complete initial CPU from immutable inputs')
    for index,row in enumerate(trace):
        destination=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=destination
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the normalization changes a complete actual instruction or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the normalization detaches complete intermediate CPU')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
         'the normalization changes exact executed instruction identities')
    if {row['site'] for row in trace if row['delay_slot']}!={row['site']+2 for row in result['branches'] if row['delay']}:
        raise ValueError('the normalization omits or invents a real delay slot')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind']!=FIXED_BRANCHES[row['site']]:
            raise ValueError('the normalization reaches an impossible positive-divisor or numerator-sign path')
    same([row for row in result['accesses'] if row['domain']=='ram'],ram_operands(observed['memory_before'][0],value),
         'the normalization changes ordered physical RAM operands or word/flag bytes')
    mode_reads=[]
    for event in result['accesses']:
        site,address,width=event['site'],event['address'],event['width_bytes']
        if event['domain'] in ('frame','ram'):continue
        if site in contract.LITERAL_OPERANDS:
            at,size,register=contract.LITERAL_OPERANDS[site]
            same(event,dict(site=site,mode='read',address=at,width_bytes=size,register=register,domain='rom',bytes=fixture[at:at+size].hex()),
                 'the normalization changes an exact PC literal operand')
        elif site==0x7AF0E:
            mode_reads.append(event)
            same(event,dict(site=site,mode='read',address=0x83C1,width_bytes=1,register=0,domain='rom',bytes=observed['calibration_before'][0x83C1].hex()),
                 'the normalization replaces its actual final-mode ROM byte')
        elif (site not in TABLE_SITES|AXIS_SITES or event['domain']!='rom' or event['mode']!='read' or width!=2
                or not (0x154C0<=address<=0x15500 or 0x14BAA<=address<0x14BCA)
                or event['bytes']!=fixture[address:address+2].hex()):
            raise ValueError('the normalization accesses an undeclared curve, axis or memory domain')
    if len(mode_reads)!=1:raise ValueError('the normalization omits or repeats its actual final-mode ROM operand')
    call_spans=[];cursor=0
    for call in result['calls']:
        site=call['site']
        if call['target']!=CALL_TARGETS.get(site) or call['return_address']!=site+4:
            raise ValueError('the normalization changes an actual helper call or continuation')
        if site in STACK_DELTAS and call['sp']!=observed['sp']+STACK_DELTAS[site]:
            raise ValueError('the normalization changes a natural nested stack frame')
        start=next((i+2 for i in range(cursor,len(trace)-2) if trace[i]['site']==site),None)
        if start is None or trace[start]['site']!=call['target']:raise ValueError('the normalization replaces a real post-delay helper entry')
        cursor=start;before=trace[start]['before']
        same(tuple(call['entry'][k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
             (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
             'the normalization detaches complete actual post-delay arguments')
        terminal=next((i for i in range(start,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches']) and trace[i+1]['next']==site+4),None)
        if terminal is None:raise ValueError('the normalization omits a complete actual helper return')
        returned=trace[terminal+1]['after']
        if returned['registers'][15]!=call['sp'] or returned['pr']!=site+4:raise ValueError('the normalization changes helper return SP/PR')
        call_spans.append((call,start,terminal+1,returned))
        if call['target'] in (0x26C78,0x21BBC):
            divisor,dividend=call['entry']['registers'][:2]
            limit=0x100000000 if call['target']==0x26C78 else 0x80000000
            if (not 0<divisor<=65535 or not 0<=dividend<limit or returned['registers'][0]!=dividend//divisor):
                raise ValueError('the normalization changes an independent actual positive division return')
            if call['target']==0x26C78 and (dividend&65535 or dividend//divisor>65535):
                raise ValueError('the normalization changes an unsigned axis numerator or fractional quotient')
    for site,address,key in ((0x7AF98,0x154E0,'lower'),(0x7AFAA,0x154C0,'upper')):
        selected=[row for row in call_spans if row[0]['site']==site]
        if len(selected)!=1:raise ValueError('the normalization omits or repeats a full endpoint curve invocation')
        call,start,end,returned=selected[0];curve=value[key]
        same(tuple(call['entry']['registers'][4:7]),(address,0x14BAA,value['coordinate']),
             'the normalization changes an actual curve/axis/coordinate register')
        if returned['registers'][0]!=curve['value']:raise ValueError('the normalization substitutes a scalar for the actual curve return')
        local=trace[start:end+1]
        reads=[event for row in local for event in row['accesses'] if event['site'] in TABLE_SITES]
        expected=[dict(site=site_read,mode='read',address=address+2*cell,width_bytes=2,register=register,domain='rom',
            bytes=fixture[address+2*cell:address+2*cell+2].hex())
            for site_read,cell,register in ((0x2650A,curve['index']+1,0),(0x26510,curve['index'],1))]
        same(reads,expected,'the normalization changes either real curve word, unconditional neighbor, order or byte width')
        tails=[row for row in local if row['site']==0x26518]
        if (len(tails)!=1 or not tails[0]['delay_slot'] or tails[0]['next']!=0x26740
                or tails[0]['after']['registers'][15]!=call['sp'] or tails[0]['after']['pr']!=site+4):
            raise ValueError('the normalization replaces the actual restored-PR curve tail')
        tail=tails[0]['after']['registers']
        if (tail[0],tail[2],tail[3])!=(curve['first'],curve['second'],curve['fraction']):
            raise ValueError('the normalization changes actual full directed-word operands')
        axes=[row for row in call_spans if row[0]['site']==0x26502 and start<=row[1]<=end]
        if len(axes)!=1:raise ValueError('the normalization omits its actual complete axis invocation')
        axis_call,a,b,axis_return=axes[0];registers=axis_call['entry']['registers']
        if ((registers[0],registers[4],registers[5])!=(0x14BAA,30,value['coordinate'])
                or (axis_return['registers'][4],axis_return['registers'][5])!=(2*curve['index'],curve['fraction'])):
            raise ValueError('the normalization changes a real axis argument, lower knot or fraction')
        axis_reads=[event for row in trace[a:b+1] for event in row['accesses'] if event['domain']=='rom' and 0x14BAA<=event['address']<0x14BCA]
        expected=[dict(site=0x26986,mode='read',address=0x14BAA+2*knot,width_bytes=2,register=1,domain='rom',
            bytes=fixture[0x14BAA+2*knot:0x14BAA+2*knot+2].hex()) for knot in range(15,curve['index']-1,-1)]
        if curve['fraction']:
            expected.extend(dict(site=site_read,mode='read',address=0x14BAA+2*knot,width_bytes=2,register=register,domain='rom',
                bytes=fixture[0x14BAA+2*knot:0x14BAA+2*knot+2].hex())
                for site_read,knot,register in ((0x2699C,curve['index'],1),(0x2699E,curve['index']+1,0)))
        same(axis_reads,expected,'the normalization changes complete backwards axis or positive fractional neighbor reads')
    divisions=[row for row in call_spans if row[0]['target']==0x21BBC]
    if len(divisions)!=(3 if value['span'] else 0):raise ValueError('the normalization invents or removes a real zero-span division')
    for (call,start,end,returned),site,base in zip(divisions,(0x7AFFA,0x7B010,0x7B026),value['bases']):
        if (call['site'],*call['entry']['registers'][:2])!=(site,value['span'],base*800):
            raise ValueError('the normalization substitutes an arithmetic result for a live multiplied numerator or span')
    stores=([0x7B00E,0x7B024,0x7B040] if value['span'] else [0x7B038,0x7B03C,0x7B040])+[0x7AEF8,0x7AF0C,0x7AF2A if value['mode_set'] else 0x7AF3E,0x7AF5A]
    operands=list(zip(stores,([2]*3+[14,2,0,0]),[*value['normalized'],value['first_status'],value['second_status'],value['request_status'],value['output']]))
    for site,register,wanted in operands:
        selected=[row for row in trace if row['site']==site]
        if len(selected)!=1 or selected[0]['before']['registers'][register]!=wanted:
            raise ValueError('the normalization substitutes matching bytes for a real transformed live store register')
