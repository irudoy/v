"""Separate five-instruction CPU/SR equations and exact empty physical stream."""

from kb import test_contract

RAM_BASE=0x01000000
NATIVE_RAM_ROOTS=(('782dacc59731fbc23c8a52ec82e8f9cc0468235c9826a1eee5214cbe5d571417',0xFFFF2C1C,0x01002C1C),)
WORDS={0x22590:0x4415,0x22592:0x8900,0x22594:0x644B,0x22596:0x000B,0x22598:0x6043}


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def require(observed,result,value,fixture):
    same(observed['exit'],(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        'the signed-magnitude original changes its complete reconstructed exit CPU/SR state')
    same(observed['exit'],value['exit'],'the signed-magnitude original changes independent full raw32 return equations')
    same((observed['frame_after'],observed['memory_after']),(value['frame'],(value['ram'],)),
        'the signed-magnitude original changes complete unchanged frame or ordinary RAM')
    same((result['frame'],result['ram']),(value['frame'],value['ram']),
        'the signed-magnitude reconstruction changes complete unchanged frame or ordinary RAM')
    if result['accesses'] or result['calls']:
        raise ValueError('the signed-magnitude helper invents a physical operand or outside call')
    same(result['branches'],value['branches'],'the signed-magnitude helper changes a natural branch or delayed return')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the signed-magnitude helper changes exact executed code bytes or either natural path')
    trace=result.get('trace')
    if type(trace) is not list or tuple(row['site'] for row in trace)!=value['path']:
        raise ValueError('the signed-magnitude helper omits a complete natural instruction trace')
    current=dict(registers=(*observed['context'][:15],observed['sp']),gbr=observed['context'][15],
        mach=observed['context'][16],macl=observed['context'][17],sr=observed['sr_before'],pr=observed['continuation'])
    for index,row in enumerate(trace):
        site=row['site'];same(row['before'],current,'the signed-magnitude helper detaches an independent full incoming instruction state')
        after=dict(current);registers=list(current['registers'])
        if site==0x22590:
            after['sr']=(current['sr']&~1)|int(0<registers[4]<0x80000000)
        elif site==0x22594:registers[4]=(0-registers[4])&0xFFFFFFFF
        elif site==0x22598:registers[0]=registers[4]
        after['registers']=tuple(registers)
        same(row['after'],after,'the signed-magnitude helper changes independent intermediate raw32 GPR/SR/special-register equations')
        expected_branches=([value['branches'][0]] if site==0x22592 else
            [value['branches'][1]] if site==0x22596 else [])
        same(row['branches'],expected_branches,'the signed-magnitude helper changes an exact per-instruction branch or return record')
        expected_next=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['index']!=index or row['word']!=WORDS[site] or row['bytes']!=fixture[site:site+2].hex()
                or row['word']!=int.from_bytes(fixture[site:site+2],'big') or row['next']!=expected_next
                or row['delay_slot'] is not (site==0x22598) or row['accesses'] or row['calls']):
            raise ValueError('the signed-magnitude helper changes an instruction, empty physical stream, path or RTS delay slot')
        current=after
    same(current,dict(registers=(*value['registers'],observed['sp']),gbr=value['gbr'],mach=value['mach'],
        macl=value['macl'],sr=value['sr'],pr=value['pr']),
        'the signed-magnitude helper loses the complete post-delay return state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],RAM_BASE+(row['address']&65535)) for row in rows)
    same(identities,NATIVE_RAM_ROOTS,'the signed-magnitude helper substitutes an exact native root or simulator alias')
    if any(row['owner']!='wandering-grasshopper/ram' or row['function']!=0x22590 for row in rows):
        raise ValueError('the signed-magnitude helper substitutes its exact selected native owner or natural function')
    if result['accesses']:
        raise ValueError('the signed-magnitude helper performs a physical ROM, RAM, stack or selected-root operand')

INFEASIBLE_INSTRUCTIONS=()
FIXED_BRANCHES={}
