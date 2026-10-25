"""Independent ordered physical operands and complete natural leaf result guards."""

from kb import test_contract

RAM_BASE=0x01000000

# Exact physical instruction operands, not inferred table or caller bindings.
ROM={337824: (338276, 4, 0),
 337828: (338280, 4, 5),
 337838: (338276, 4, 4),
 337840: (338166, 2, 0),
 337852: (338168, 2, 0),
 337890: (338170, 2, 6),
 337916: (338276, 4, 4),
 337918: (338172, 2, 0),
 338180: (338276, 4, 5),
 338182: (338270, 2, 0),
 338186: (338272, 2, 0),
 338220: (338274, 2, 2),
 338242: (338300, 4, 6),
 338250: (338316, 4, 6),
 338252: (35648, 1, 0),
 338260: (338320, 4, 6),
 345166: (345556, 4, 6),
 345168: (345520, 4, 4),
 345170: (345298, 2, 0),
 345172: (35774, 1, 2),
 345178: (345300, 2, 0),
 345212: (345548, 4, 5),
 345214: (345302, 2, 0),
 345256: (345560, 4, 2),
 676486: (677072, 4, 6),
 676490: (676754, 2, 0),
 676496: (676756, 2, 0)}
READ={337830: (16772, 1, 0),
 337842: (5712, 2, 6),
 337844: (5696, 4, 0),
 337856: (5598, 1, 5),
 338184: (5386, 1, 2),
 338190: (6758, 2, 6),
 338244: (9309, 1, 0),
 345174: (12224, 1, 6),
 345184: (12225, 1, 6),
 345216: (4132, 2, 6),
 676494: (13194, 1, 2),
 676500: (12274, 1, 2)}
WRITE={337920: (6758, 2, 6), 338264: (8960, 2, 0), 345218: (13246, 1, 2), 345260: (16730, 2, 6)}
# Special-register pushes/restores have no GPR operand in the physical record.
FRAME={337820: ('write', 4, None, 17),
 337822: ('write', 8, None, 15),
 337922: ('read', 8, None, 15),
 337926: ('read', 4, None, 17),
 338178: ('write', 4, None, 17),
 338268: ('read', 4, None, 17),
 345164: ('write', 4, None, 17),
 345264: ('read', 4, None, 17),
 676484: ('write', 4, None, 17),
 676578: ('read', 4, None, 17)}
INFEASIBLE_INSTRUCTIONS=(338226, 345232)
FIXED_BRANCHES={338224: 'taken', 338238: 'fallthrough', 345230: 'taken'}


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
            address,domain=RAM_BASE+offset,'ram'
            memory=observed['memory_before'][0] if mode=='read' else value['ram']
            raw=memory[offset:offset+width]
        else:continue
        result.append(dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
    return result


def require(observed,result,value,fixture):
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the scalar RAM product original changes complete independent instruction state')
    same(observed['exit'],value['exit'],'the scalar RAM product original changes independent complete scalar register/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the scalar RAM product original changes independent complete frame or arithmetic RAM state')
    same(result['accesses'],physical(observed,value,fixture),
        'the scalar RAM product original changes ordered physical RAM/pool/configuration/stack address, width, register or byte effects')
    same(result['branches'],value['branches'],'the scalar RAM product original changes an independent natural conditional/jump/return outcome')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the scalar RAM product original changes a complete expected natural instruction path or byte')
    if result['calls']:raise ValueError('the scalar RAM product original invents an outside call')
    trace=result.get('trace')
    if type(trace) is not list or tuple(row['site'] for row in trace)!=value['path']:
        raise ValueError('the scalar RAM product original omits its complete natural instruction trace')
    delayed={row['site']+2 for row in value['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the scalar RAM product original changes a conditional, jump or RTS delay slot')
    if (trace[-1]['next']!=observed['continuation'] or trace[-1]['after']['registers'][15]!=observed['sp']
            or tuple(trace[-1]['after']['registers'][:15])!=value['registers']
            or trace[-1]['after']['gbr']!=observed['context'][15] or trace[-1]['after']['macl']!=observed['context'][17]):
        raise ValueError('the scalar RAM product original changes complete post-delay returned GPR/SP/GBR/MACL state')
    if any(site in result['code'] for site in INFEASIBLE_INSTRUCTIONS):
        raise ValueError('the scalar RAM product original leaves its independent byte/word product width premise')


def require_no_selected_datum(result,rows):
    roots={row['address'] for row in rows}
    for event in result['accesses']:
        if event['domain']=='rom' and any(event['address']<=root<event['address']+event['width_bytes'] for root in roots):
            raise ValueError('the scalar RAM product original physically accesses a selected unsupported ROM datum root')
        if event['domain']=='rom' and event['site'] not in ROM:
            raise ValueError('the scalar RAM product original substitutes an undeclared ROM source for an exact instruction pool or configuration byte')
