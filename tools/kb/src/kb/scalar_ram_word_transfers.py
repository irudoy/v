"""Independent ordered physical operands and complete natural leaf result guards."""

from kb import test_contract

RAM_BASE=0x01000000

# Exact physical instruction operands, not inferred table or caller bindings.
ROM={451730: (452036, 4, 4),
 451732: (451810, 2, 0),
 451738: (452076, 4, 2),
 451740: (37832, 2, 6),
 451744: (452080, 4, 6),
 451758: (451816, 2, 6),
 484224: (484436, 4, 7),
 484226: (484424, 2, 0),
 484228: (484464, 4, 2),
 484232: (484426, 2, 0),
 484234: (484468, 4, 5),
 484242: (37032, 2, 0),
 484258: (37030, 2, 2),
 484272: (484424, 2, 0),
 831946: (832032, 4, 2),
 831980: (832012, 4, 2),
 831984: (831994, 2, 3)}
READ={451734: (5990, 1, 2), 484230: (15728, 2, 4), 484236: (13598, 2, 6), 831956: (10428, 2, 6)}
WRITE={451778: (4864, 2, 2), 484276: (15728, 2, 5), 831990: (14458, 2, 6)}
# Special-register pushes/restores have no GPR operand in the physical record.
FRAME={451728: ('write', 4, None, 17), 451782: ('read', 4, None, 17)}
INFEASIBLE_INSTRUCTIONS=(451774,)
FIXED_BRANCHES={451772: 'taken'}


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(observed,value,fixture):
    result=[]
    for site in value['path']:
        if site in FRAME:
            mode,depth,register,source=FRAME[site]
            address,width,domain=observed['sp']-depth,4,'frame'
            raw=observed['context'][source].to_bytes(4,'big')
        elif site in ROM:
            address,width,register=ROM[site];mode,domain='read','rom';raw=fixture[address:address+width]
        elif site in READ or site in WRITE:
            mode='read' if site in READ else 'write'
            offset,width,register=(READ if mode=='read' else WRITE)[site]
            if site in (0xCB1D4,0xCB1F6):offset+=2*value['tags']['index']
            address,domain=RAM_BASE+offset,'ram'
            memory=observed['memory_before'][0] if mode=='read' else value['ram']
            raw=memory[offset:offset+width]
        else:continue
        result.append(dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
    return result


def require(observed,result,value,fixture):
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the scalar RAM word original changes complete independent instruction state')
    same(observed['exit'],value['exit'],'the scalar RAM word original changes independent complete scalar register/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the scalar RAM word original changes independent complete frame or arithmetic RAM state')
    same(result['accesses'],physical(observed,value,fixture),
        'the scalar RAM word original changes ordered physical RAM/pool/configuration/stack address, width, register or byte effects')
    same(result['branches'],value['branches'],'the scalar RAM word original changes an independent natural conditional/jump/return outcome')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the scalar RAM word original changes a complete expected natural instruction path or byte')
    if result['calls']:raise ValueError('the scalar RAM word original invents an outside call')
    trace=result.get('trace')
    if type(trace) is not list or tuple(row['site'] for row in trace)!=value['path']:
        raise ValueError('the scalar RAM word original omits its complete natural instruction trace')
    delayed={row['site']+2 for row in value['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the scalar RAM word original changes a conditional, jump or RTS delay slot')
    if (trace[-1]['next']!=observed['continuation'] or trace[-1]['after']['registers'][15]!=observed['sp']
            or tuple(trace[-1]['after']['registers'][:15])!=value['registers']
            or trace[-1]['after']['gbr']!=observed['context'][15] or trace[-1]['after']['macl']!=observed['context'][17]):
        raise ValueError('the scalar RAM word original changes complete post-delay returned GPR/SP/GBR/MACL state')
    if any(site in result['code'] for site in INFEASIBLE_INSTRUCTIONS):
        raise ValueError('the scalar RAM word original leaves its independent byte/word product width premise')


SELECTED_ROOTS=(('3b093cf5dda17d51844bfd5eda0482f3f60aa8eeddab660f55294a3c42210bb7', 37932), ('6979d26a6b9ca01b5e4e3dab5f2ab1878c8b82e53c6a9163d129cb2ed4ae3a6b', 76140), ('3c0d93540474efe7370d42aa1e8fc82f40077e48751a9adbcb944ede4def1a06', 79144))

def require_no_selected_datum(result,rows):
    if tuple((r['original_claim_sha256'],r['address']) for r in rows)!=SELECTED_ROOTS:
        raise ValueError('the word original substitutes an exact selected ROM-reader identity')
    roots={r['address'] for r in rows}
    for event in result['accesses']:
        if any(event['address']<=root<event['address']+event['width_bytes'] for root in roots):
            raise ValueError('the scalar RAM word original physically accesses a selected unsupported ROM datum root')
        if event['domain']=='rom' and event['site'] not in ROM:
            raise ValueError('the scalar RAM word original substitutes an undeclared ROM source for an exact instruction pool or configuration byte')
