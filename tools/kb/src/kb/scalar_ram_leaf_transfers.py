"""Independent ordered physical operands and complete natural leaf result guards."""

from kb import test_contract

RAM_BASE=0x01000000

# Exact physical instruction operands, not inferred table or caller bindings.
ROM={
    0x3958A:(0x396F4,4,0),0x39590:(0x39708,4,2),
    0x39874:(0x399AC,4,2),0x39876:(0x398F4,2,0),0x3987A:(0x399C4,4,2),
    0x468B2:(0x46928,4,1),0x468B4:(0x46918,2,0),0x468B8:(0x4691A,2,0),
    0x468BE:(0x4691C,2,0),0x468C2:(0x4692C,4,5),0x468C8:(0x4691E,2,0),
    0x468D2:(0x46920,2,0),0x468DC:(0x46922,2,0),0x468E0:(0x46930,4,5),
    0x468E8:(0x870C,1,0),0x468F4:(0x46934,4,5),0x468F6:(0x46924,2,0),0x46910:(0x46926,2,0),
    0x4AB98:(0x4AD00,4,0),0x4ABC8:(0x4ACFC,4,5),0x4ABCA:(0x4ABD6,2,0),
    0x4AF3A:(0x4AFC4,4,0),0x4AF3E:(0x4AFC4,4,5),0x4AF40:(0x4AF8A,2,0),
    0x4AF42:(0x4AFD8,4,4),0x4AF4C:(0x4AF8C,2,0),0x4AF56:(0x8B3F,1,0),
    0x4AF6C:(0x4AF94,4,5),0x4AF82:(0x4AFD4,4,2),
    0x4BB6A:(0x4BC68,4,7),0x4BB6C:(0x4BC44,4,5),0x4BB74:(0x4BBA6,2,0),0x4BB9C:(0x4BC78,4,2),
    0x4C138:(0x4C1D8,4,0),0x4C13C:(0x4C1A8,4,6),0x4C13E:(0x4C1DC,4,5),
    0x4C150:(0x4C1E0,4,6),0x4C16C:(0x4C1A0,4,6),0x4C16E:(0x4C182,2,0),
    0x4C174:(0x4C1A0,4,6),0x4C176:(0x4C184,2,0),
    0x4E112:(0x4E1B0,4,1),0x4E114:(0x4E1B4,4,6),0x4E124:(0x4E1B8,4,5),
    0x4E126:(0x4E17C,2,0),0x4E152:(0x4E17C,2,0),0x4E156:(0x4E1BC,4,6),0x4E158:(0x8440,1,0),
    0x554B0:(0x555EC,4,0),0x554B4:(0x555C8,4,1),0x554B8:(0x554F6,2,0),0x554C4:(0x554F4,2,0),
    0x70D84:(0x70E30,4,0),0x70D94:(0x70E34,4,6),0x70D98:(0x70E2C,4,5),
    0x70D9C:(0x70E22,2,0),0x70DB8:(0x70E2C,4,5),0x70DBA:(0x70E24,2,0),
    0xA5530:(0xA5770,4,4),0xA553C:(0xA5774,4,6),0xA5544:(0xA5778,4,7),
    0xA5546:(0xA5650,2,0),0xA554A:(0xA5652,2,0)}
READ={
    0x3958E:(0x1187,1,0),0x39594:(0x1081,1,0),0x39878:(0x1F89,1,5),0x3987E:(0x107C,1,0),
    0x468B6:(0x1752,2,2),0x468BC:(0x1765,1,5),0x468C4:(0x1748,2,4),0x468CE:(0x15AC,1,7),
    0x468D6:(0x13F7,1,14),0x468DA:(0x1230,2,6),0x468E6:(0x170A,2,6),0x468F8:(0x1F62,1,2),
    0x4AB9C:(0x231A,2,0),0x4ABA0:(0x230C,2,0),0x4ABA8:(0x22E8,2,0),
    0x4AF44:(0x160F,1,0),0x4AF4E:(0x1610,1,0),0x4AF72:(0x11AF,1,2),
    0x4BB6E:(0x22FE,1,0),0x4BB70:(0x22F8,1,4),0x4BB78:(0x1657,1,2),
    0x4C140:(0x4184,1,0),0x4C148:(0x24D2,1,0),0x4C156:(0x1239,1,5),
    0x4C166:(0x2458,1,0),0x4C172:(0x1831,1,0),0x4C178:(0x1830,1,0),
    0x4E118:(0x248D,1,0),0x4E11E:(0x25FD,1,0),0x4E128:(0x1513,1,6),
    0x554BC:(0x15F8,4,2),0x554BE:(0x230C,2,0),0x554CA:(0x15DA,2,7),
    0x70D88:(0x2490,1,0),0x70D8E:(0x243A,2,0),0x70D9A:(0x25D6,1,2),0x70DA2:(0x19C0,2,2),0x70DA4:(0x243A,2,0),
    0xA5534:(0x4204,1,5),0xA553E:(0x244F,1,0),0xA5548:(0x3334,2,6),0xA554C:(0x32EE,2,2)}
WRITE={
    0x46912:(0x173A,2,2),0x4ABCC:(0x18E2,2,2),
    0x4AF4A:(0x12DE,1,0),0x4AF54:(0x12E0,1,0),0x4AF6E:(0x12DF,1,0),0x4AF84:(0x23BD,1,0),
    0x4BBA0:(0x23C5,1,0),0x4C152:(0x24D2,1,0),0x4C17A:(0x2404,1,0),
    0x4E154:(0x1513,1,2),0x4E15C:(0x25FD,1,0),0x554EA:(0x231A,2,0),
    0x70DB6:(0x2438,2,0),0x70DBC:(0x19C2,2,2),0xA555A:(0x4204,1,5)}
# Special-register pushes/restores have no GPR operand in the physical record.
FRAME={
    0x39588:('write',4,None,15),0x395AC:('read',4,None,15),
    0x468B0:('write',4,14,14),0x46916:('read',4,14,14),
    0x4AB94:('write',4,None,17),0x4AB96:('write',8,None,15),
    0x4ABCE:('read',8,None,15),0x4ABD2:('read',4,None,17),
    0x4AF38:('write',4,None,15),0x4AF88:('read',4,None,15),
    0x4C136:('write',4,None,15),0x4C17E:('read',4,None,15),
    0x554AE:('write',4,None,15),0x554EE:('read',4,None,15),
    0x70D82:('write',4,None,15),0x70DC0:('read',4,None,15)}
INFEASIBLE_INSTRUCTIONS=(0x4E142,0x4E144,0x4E150)
FIXED_BRANCHES={0x4E140:'taken',0x4E14E:'taken'}


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
    same(observed['exit'],expected,'the scalar RAM leaf original changes complete independent instruction state')
    same(observed['exit'],value['exit'],'the scalar RAM leaf original changes independent complete scalar register/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the scalar RAM leaf original changes independent complete frame or arithmetic RAM state')
    same(result['accesses'],physical(observed,value,fixture),
        'the scalar RAM leaf original changes ordered physical RAM/pool/configuration/stack address, width, register or byte effects')
    same(result['branches'],value['branches'],'the scalar RAM leaf original changes an independent natural conditional/jump/return outcome')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the scalar RAM leaf original changes a complete expected natural instruction path or byte')
    if result['calls']:raise ValueError('the scalar RAM leaf original invents an outside call')
    trace=result.get('trace')
    if type(trace) is not list or tuple(row['site'] for row in trace)!=value['path']:
        raise ValueError('the scalar RAM leaf original omits its complete natural instruction trace')
    delayed={row['site']+2 for row in value['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the scalar RAM leaf original changes a conditional, jump or RTS delay slot')
    if (trace[-1]['next']!=observed['continuation'] or trace[-1]['after']['registers'][15]!=observed['sp']
            or tuple(trace[-1]['after']['registers'][:15])!=value['registers']
            or trace[-1]['after']['gbr']!=observed['context'][15] or trace[-1]['after']['macl']!=observed['context'][17]):
        raise ValueError('the scalar RAM leaf original changes complete post-delay returned GPR/SP/GBR/MACL state')
    if any(site in result['code'] for site in INFEASIBLE_INSTRUCTIONS):
        raise ValueError('the scalar RAM leaf original leaves its independent signed-byte decay premise')


def require_no_selected_datum(result,rows):
    roots={row['address'] for row in rows}
    for event in result['accesses']:
        if event['domain']=='rom' and any(event['address']<=root<event['address']+event['width_bytes'] for root in roots):
            raise ValueError('the scalar RAM leaf original physically accesses a selected unsupported ROM datum root')
        if event['domain']=='rom' and event['site'] not in ROM:
            raise ValueError('the scalar RAM leaf original substitutes an undeclared ROM source for an exact instruction pool or configuration byte')
