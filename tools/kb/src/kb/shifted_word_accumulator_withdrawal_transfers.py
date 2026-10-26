"""Exact natural accumulator operands, loop controls, native gate and returned state."""
from kb import test_contract
from kb import shifted_word_accumulator_withdrawal_contract as contract

ROM={0xA539A:(0xA54F8,4,6),0xA53A2:(0xA54C0,2,6),0xA53AA:(0xA54D0,4,2),
    0xA53AC:(0xA54C2,2,0),0xA53B0:(0xA54FC,4,2),0xA53BC:(0xA5500,4,6),
    0xA53BE:(0xA5504,4,2),0xA53DA:(0xA5508,4,2),0xA5402:(0xA550C,4,5),
    0xA540E:(0xA54D0,4,3),0xA5412:(0xA54C4,2,0),0xA5426:(0xA54D0,4,3),
    0xA5428:(0xA54C4,2,0),0xA5430:(0xA54D0,4,3),0xA5434:(0xA54C4,2,0)}
FEASIBLE_SITES=set(range(0xA5398,0xA543C,2))-{0xA53D6}
FIXED_BRANCHES={0xA53D4:'taken'}
CONDITIONAL_SITES=(0xA53A0,0xA53A8,0xA53BA,0xA53D4,0xA53E6,0xA53F8,0xA53FC,0xA5400,0xA5422)


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(value,fixture):
    result=[]
    for index,site in enumerate(value['path']):
        if index in value['events']:result.append(value['events'][index])
        elif site in ROM:
            address,width,register=ROM[site]
            result.append(dict(site=site,mode='read',address=address,width_bytes=width,register=register,
                domain='rom',bytes=fixture[address:address+width].hex()))
    return result


def require(observed,result,value,fixture):
    wanted=(value['sr'],value['pr'],value['macl'],value['mach'],value['gbr'],*reversed(value['registers']))
    same(observed['exit'],wanted,'the accumulator original changes complete independently composed exit CPU/SR state')
    same((result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),wanted,
        'the accumulator instruction oracle disagrees with the independent complete CPU/SR equations')
    same((observed['frame_after'],observed['memory_after'],result['frame'],result['ram'],result['sp']),
        (value['frame'],(value['ram'],),value['frame'],value['ram'],value['sp']),
        'the accumulator changes complete independent RAM, saved MACL frame bytes or restored SP')
    same(result['accesses'],physical(value,fixture),
        'the accumulator changes an independently composed physical site, mode, width, register, address or operand byte')
    same(result['branches'],value['controls'],'the accumulator changes an independent real gate, finite shift loop or delay slot')
    same(result['calls'],[],'the complete natural accumulator invents a helper or scheduler call')
    trace=result.get('trace')
    if type(trace) is not list or not trace:
        raise ValueError('the accumulator lacks its complete natural instruction trace')
    same(tuple(row['site'] for row in trace),value['path'],'the accumulator changes an independent complete instruction path')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the accumulator changes an exact executed instruction byte')
    initial=trace[0]['before']
    same(tuple(initial[key] for key in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the accumulator trace changes its complete natural incoming CPU state')
    delayed={row['site']+2 for row in value['controls'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the accumulator loses a natural taken/fallthrough loop or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the accumulator changes its feasible exact instruction stream or natural continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],'the accumulator detaches complete intermediate CPU state from its next instruction')
    last=trace[-1]['after']
    same((tuple(last['registers'][:15]),last['registers'][15],last['gbr'],last['mach'],last['macl'],last['sr'],last['pr']),
        (value['registers'],value['sp'],value['gbr'],value['mach'],value['macl'],value['sr'],value['pr']),
        'the accumulator changes its complete natural post-delay returned state')
    allowed_rom={(at,width) for at,width,register in ROM.values()}|{(0x83EC,1),(0x8A0D,1),(0x8CBA,1)}
    for event in result['accesses']:
        if event['domain']=='rom' and (event['address'],event['width_bytes']) not in allowed_rom:
            raise ValueError('the accumulator adds a direct ROM input outside its complete physical source set')
        if any(event['address']<=row['address']<event['address']+event['width_bytes'] for row in contract.DECLARED['selected']):
            raise ValueError('the accumulator directly accesses a selected native surface root')
