"""Independent ordered physical operands and complete natural leaf result guards."""

from kb import test_contract

RAM_BASE=0x01000000

# Exact physical instruction operands, not inferred table or caller bindings.
ROM={157146: (157160, 4, 0), 157152: (157164, 4, 0)}
READ={}
WRITE={}
# Special-register pushes/restores have no GPR operand in the physical record.
FRAME={}
INFEASIBLE_INSTRUCTIONS=()
FIXED_BRANCHES={}

NATIVE_RAM_ROOTS=(('a4964e35d1c13a7650b5dbcf19a08cba46eb862a8fbc9fe91df2fb65c365dbe8', 4294908696, 16784152),)


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(observed,value,fixture):
    result=[]
    for site in value['path']:
        if site not in ROM:continue
        address,width,register=ROM[site]
        result.append(dict(site=site,mode='read',address=address,width_bytes=width,
            register=register,domain='rom',bytes=fixture[address:address+width].hex()))
    return result


def require(observed,result,value,fixture):
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the register overflow original changes complete independent instruction state')
    same(observed['exit'],value['exit'],'the register overflow original changes independent complete scalar register/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the register overflow original changes independent complete frame or arithmetic RAM state')
    same(result['accesses'],physical(observed,value,fixture),
        'the register overflow original changes ordered physical RAM/pool/configuration/stack address, width, register or byte effects')
    same(result['branches'],value['branches'],'the register overflow original changes an independent natural conditional/jump/return outcome')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the register overflow original changes a complete expected natural instruction path or byte')
    if result['calls']:raise ValueError('the register overflow original invents an outside call')
    trace=result.get('trace')
    if type(trace) is not list or tuple(row['site'] for row in trace)!=value['path']:
        raise ValueError('the register overflow original omits its complete natural instruction trace')
    delayed={row['site']+2 for row in value['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the register overflow original changes a conditional, jump or RTS delay slot')
    if (trace[-1]['next']!=observed['continuation'] or trace[-1]['after']['registers'][15]!=observed['sp']
            or tuple(trace[-1]['after']['registers'][:15])!=value['registers']
            or trace[-1]['after']['gbr']!=observed['context'][15] or trace[-1]['after']['macl']!=observed['context'][17]):
        raise ValueError('the register overflow original changes complete post-delay returned GPR/SP/GBR/MACL state')
    if any(site in result['code'] for site in INFEASIBLE_INSTRUCTIONS):
        raise ValueError('the register overflow original leaves its independent byte/word product width premise')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535)) for row in rows)
    if (not test_contract.exact(identities,NATIVE_RAM_ROOTS)
            or any(not row['owner'].endswith('/ram') or not 0xFFFF0000<=row['address']<=0xFFFFFFFF for row in rows)):
        raise ValueError('the register overflow substitutes a selected native RAM original or its exact simulator alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for original,native,alias in NATIVE_RAM_ROOTS for address in (native,alias)):
            raise ValueError('the register overflow physically accesses a selected native RAM datum root or its simulator alias')
        if event['domain']=='rom' and event['site'] not in ROM:
            raise ValueError('the register overflow substitutes an undeclared ROM source for its exact pool or configuration operand')
