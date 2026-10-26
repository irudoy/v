"""Exact complete timer writer CPU/frame and separate physical ordinary/native effects."""
from kb import test_contract
from kb import indexed_timer_refresh_writer_contract as contract,indexed_timer_refresh_writer_matrix as matrix
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
FEASIBLE_SITES=EXACT_SITES
INFEASIBLE_SITES=set()
CONDITIONAL_SITES=(0x901A6,0x901AC,0x901B4,0x901BC,0x90208,0x90218)
FIXED_BRANCHES={}


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def require(observed,result,value,fixture):
    same(observed['exit'],(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        'the timer writer changes complete independently reconstructed exit CPU/SR')
    same(observed['exit'],value['exit'],'the timer writer changes separate complete numerical/state equations')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(value['ordinary_ram'],) or observed['native_after']!=value['native_after']
            or matrix.logical(observed['memory_after'][0],observed['native_after'])!=result['ram']
            or result['ram']!=value['ram']):
        raise ValueError('the timer writer changes full frame, actual ordinary bytes, actual native bytes or independent logical state')
    same(result['accesses'],value['operands'],'the timer writer changes ordered exact PC, ordinary/native byte or full stack operands')
    same(result['branches'],value['branches'],'the timer writer changes a complete natural conditional, jump, return or delay')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the timer writer changes exact complete executed stock instruction bytes')
    if result['calls']:raise ValueError('the complete timer leaf invents a helper or outside call')
    trace=result.get('trace')
    if type(trace) is not list or len(trace)!=len(value['steps']):
        raise ValueError('the timer writer omits or duplicates a complete natural instruction or real delay slot')
    for actual,expected in zip(trace,value['steps']):
        same({key:actual[key] for key in ('site','before','after','branches','delay_slot','next')},expected,
            'the timer writer changes independent complete intermediate CPU/GBR/SR/PR/SP or control state')
        if actual['word']!=int.from_bytes(fixture[actual['site']:actual['site']+2],'big') or actual['bytes']!=fixture[actual['site']:actual['site']+2].hex():
            raise ValueError('the timer writer substitutes a natural stock instruction')
    if (result['sp'],result['pr'],result['gbr'],result['mach'],result['macl'])!=(observed['sp'],observed['continuation'],*observed['context'][15:18]):
        raise ValueError('the timer writer changes natural outer stack/return or preserved complete special state')
    if result['registers'][14]!=observed['context'][14]:
        raise ValueError('the timer writer replaces the exact saved full R14 with its temporary index mask')
    native=[event for event in result['accesses'] if event['domain']=='native-control']
    expected_native=[event for event in value['operands'] if event['domain']=='native-control']
    same(native,expected_native,'the timer writer detaches real native850C/850D operands from the actual snapshot')
    if any(event['width_bytes']!=1 or event['address'] not in (0xFFFF850C,0xFFFF850D)
            or event['address']==0xFFFF850D and event['mode']!='read' for event in native):
        raise ValueError('the timer writer widens its exact native byte permissions')
    if value['native_reset_written']:
        section=[row for row in trace if 0x901D0<=row['site']<0x901EE]
        if any(row['after']['sr']&0xF0!=0xF0 for row in section):
            raise ValueError('the timer reset write leaves the actual interrupt-masked critical section')
        if len(value['critical_sr'])!=2 or value['critical_sr'][0][1]&0xF0!=0xF0:
            raise ValueError('the timer reset omits its complete independent SR save/restore sequence')
    if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'],trace[-1]['next'])!=(0x9024C,0x9024E,True,observed['continuation']):
        raise ValueError('the timer writer replaces the real RTS-delay full R14 restore')
