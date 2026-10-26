"""Complete caller/helper CPU carriers, ordered indexed reads, physical frame and natural calls."""
from kb import test_contract
from kb import diagnostic_record_composite_gate_contract as contract
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
FEASIBLE_SITES=EXACT_SITES
INFEASIBLE_SITES=set()
FIXED_BRANCHES={0x25A1A:'fallthrough',0x25A22:'fallthrough'}


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def require(observed,result,value,fixture):
    same(observed['exit'],(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        'the composite gate changes complete independently reconstructed exit CPU/SR')
    same(observed['exit'],value['exit'],'the composite gate changes separate complete short-circuit or predicate CPU equations')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)
            or observed['memory_after']!=observed['memory_before']):
        raise ValueError('the composite gate changes exact complete frame, read-only RAM or independent numerical state')
    same(result['accesses'],value['operands'],'the composite gate changes ordered exact PC, indexed-member or PR-frame operands')
    same(result['branches'],value['branches'],'the composite gate changes sentinel, short-circuit, call, jump or natural return outcomes')
    same(result['calls'],value['calls'],'the composite gate changes complete real pre-delay calls or post-delay helper entry CPU/PR/SP')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the composite gate changes an exact stock instruction or complete feasible closure')
    trace=result.get('trace')
    if type(trace) is not list or len(trace)!=len(value['steps']):
        raise ValueError('the composite gate omits or duplicates an ordered natural helper or caller instruction')
    for actual,expected in zip(trace,value['steps']):
        same({key:actual[key] for key in ('site','before','after','next','delay_slot','branches')},expected,
            'the composite gate changes independent complete intermediate CPU, branch, delay or continuation state')
        if actual['word']!=int.from_bytes(fixture[actual['site']:actual['site']+2],'big') or actual['bytes']!=fixture[actual['site']:actual['site']+2].hex():
            raise ValueError('the composite gate replaces an actual caller/helper instruction byte')
    if (result['sp'],result['pr'],result['gbr'],result['mach'],result['macl'])!=(observed['sp'],observed['continuation'],*observed['context'][15:18]):
        raise ValueError('the composite gate changes its complete natural outer return or special state')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind']!=FIXED_BRANCHES[row['site']]:
            raise ValueError('the composite gate makes either exact sentinel call report an active record')
