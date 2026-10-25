"""Independent ordered physical operands and complete natural leaf result guards."""

from kb import test_contract

RAM_BASE=0x01000000

# Exact physical instruction operands, not inferred table or caller bindings.
ROM={250974: (251172, 4, 6),
 250990: (251128, 4, 2),
 250992: (251120, 2, 0),
 251006: (251136, 4, 2),
 251012: (251128, 4, 7),
 251016: (251122, 2, 6),
 251038: (251122, 2, 2),
 279632: (279744, 4, 0),
 279636: (279748, 4, 10),
 279638: (279738, 2, 0),
 279640: (279752, 4, 1),
 279646: (279756, 4, 7),
 279654: (36082, 1, 0),
 279672: (279740, 2, 0),
 279686: (36081, 1, 2),
 478218: (478520, 4, 6),
 478226: (478536, 4, 6),
 478236: (478540, 4, 6),
 478244: (478500, 4, 2),
 478256: (478504, 4, 4),
 478258: (478286, 2, 0),
 478272: (478504, 4, 4),
 478274: (478290, 2, 0),
 478292: (478504, 4, 4),
 478296: (478492, 2, 0),
 478304: (478494, 2, 0),
 478324: (478504, 4, 4),
 478326: (478492, 2, 0),
 478330: (478496, 2, 0),
 489470: (489744, 4, 1),
 489472: (489596, 2, 0),
 489474: (489748, 4, 2),
 489478: (489598, 2, 0),
 489482: (489600, 2, 0),
 489486: (489602, 2, 0),
 489490: (33729, 1, 0),
 489496: (489752, 4, 2),
 489498: (489756, 4, 4),
 489500: (35269, 1, 0),
 489516: (489760, 4, 5),
 489524: (489604, 2, 0),
 489528: (489606, 2, 0),
 489530: (489760, 4, 5),
 489544: (489608, 2, 0),
 489556: (489604, 2, 0),
 489560: (489606, 2, 0),
 489572: (489610, 2, 0),
 489576: (489612, 2, 0),
 489580: (489614, 2, 0),
 489584: (489616, 2, 0),
 591860: (592476, 4, 6),
 591874: (592480, 4, 4),
 591878: (592170, 2, 2),
 591892: (592484, 4, 2),
 591904: (592480, 4, 5),
 591908: (592172, 2, 0),
 591920: (592174, 2, 2),
 591934: (592174, 2, 2),
 591936: (592480, 4, 5),
 591946: (592176, 2, 0),
 591956: (592480, 4, 2),
 591960: (592174, 2, 6),
 591962: (592480, 4, 5),
 591972: (592176, 2, 0),
 591978: (592484, 4, 2),
 591984: (592488, 4, 5),
 591988: (36378, 1, 6),
 591994: (592176, 2, 0)}
READ={250976: (16773, 1, 0),
 250984: (16767, 1, 0),
 250994: (16190, 1, 6),
 251020: ('candidate', 1, 5),
 251026: ('current', 1, 6),
 279642: (6488, 1, 2),
 279644: (4209, 1, 0),
 279662: (9425, 1, 0),
 279674: (6204, 1, 5),
 279684: (4209, 1, 0),
 279698: (4288, 4, 2),
 478220: (16766, 1, 0),
 478230: (9371, 1, 0),
 478238: (9311, 1, 0),
 478248: (9250, 2, 5),
 478262: (6376, 2, 2),
 478278: (6374, 2, 2),
 478302: (6376, 2, 6),
 478308: (6374, 2, 2),
 478328: (6376, 2, 2),
 489476: (13448, 2, 13),
 489480: (13452, 2, 7),
 489484: (13446, 2, 5),
 489488: (13450, 2, 14),
 489506: (16806, 1, 0),
 489522: (16738, 2, 13),
 489526: (13472, 2, 13),
 489532: (13512, 2, 7),
 489536: (16738, 2, 6),
 489546: (13468, 2, 5),
 489558: (13472, 2, 13),
 489562: (13512, 2, 2),
 591862: (8999, 1, 0),
 591886: ('request', 2, 2),
 591898: ('latch', 1, 6),
 591912: (5304, 1, 6),
 591948: (5360, 1, 6),
 591974: (5360, 1, 6),
 591996: (5360, 1, 2)}
WRITE={251042: ('current', 1, 5),
 279714: (9425, 1, 0),
 279726: (9425, 1, 0),
 478332: (6388, 2, 2),
 489574: (13440, 2, 13),
 489578: (13444, 2, 7),
 489582: (13438, 2, 5),
 489586: (13442, 2, 14),
 591928: ('delay', 1, 2),
 591942: ('delay', 1, 2),
 591954: (5360, 1, 6),
 591968: ('delay', 1, 6),
 591980: (5360, 1, 6),
 591992: ('latch', 1, 6),
 592002: (5360, 1, 2)}
# Special-register pushes/restores have no GPR operand in the physical record.
FRAME={279624: ('write', 4, 10, 10),
 279626: ('write', 8, 11, 11),
 279628: ('write', 12, 13, 13),
 279630: ('write', 16, None, 15),
 279728: ('read', 16, None, 15),
 279730: ('read', 12, 13, 13),
 279732: ('read', 8, 11, 11),
 279736: ('read', 4, 10, 10),
 478216: ('write', 4, None, 17),
 478336: ('read', 4, None, 17),
 489466: ('write', 4, 13, 13),
 489468: ('write', 8, 14, 14),
 489588: ('read', 8, 14, 14),
 489592: ('read', 4, 13, 13)}
INFEASIBLE_INSTRUCTIONS=()
FIXED_BRANCHES={}


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(observed,value,fixture):
    result=[];index=value['tags'].get('index')
    arrays={'candidate':(0x2838,1),'current':(0x3F4C,1),'request':(0x1AAC,2),
        'delay':(0x1930,1),'latch':(0x2568,1)}
    if index is not None and (type(index) is not int or not 0<=index<=255):
        raise ValueError('the independent physical address leaves the complete unsigned-byte index domain')
    def event(site,mode,address,width,register,domain,raw):
        result.append(dict(site=site,mode=mode,address=address,width_bytes=width,
            register=register,domain=domain,bytes=raw.hex()))
    for site in value['path']:
        if site==0x3D49C:
            event(site,'write',observed['sp']-4,4,5,'frame',value['tags']['candidate'].to_bytes(4,'big'))
            continue
        if site==0x444A8:
            event(site,'read',RAM_BASE+0x24D1,1,None,'ram',bytes((value['tags']['first_flags'],)))
            event(site,'write',RAM_BASE+0x24D1,1,None,'ram',value['ram'][0x24D1:0x24D2])
            continue
        if site in FRAME:
            mode,depth,register,source=FRAME[site];address,width,domain=observed['sp']-depth,4,'frame'
            raw=observed['context'][source].to_bytes(4,'big')
        elif site in ROM:
            address,width,register=ROM[site];mode,domain='read','rom';raw=fixture[address:address+width]
        elif site in READ or site in WRITE:
            mode='read' if site in READ else 'write'
            offset,width,register=(READ if mode=='read' else WRITE)[site]
            if type(offset) is str:
                base,stride=arrays[offset];offset=base+index*stride
            address,domain=RAM_BASE+offset,'ram'
            memory=observed['memory_before'][0] if mode=='read' else value['ram']
            raw=bytes((value['tags']['first_flags'],)) if site==0x444A2 else memory[offset:offset+width]
        else:continue
        event(site,mode,address,width,register,domain,raw)
    return result


def require(observed,result,value,fixture):
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the scalar RAM gated path original changes complete independent instruction state')
    same(observed['exit'],value['exit'],'the scalar RAM gated path original changes independent complete scalar register/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the scalar RAM gated path original changes independent complete frame or arithmetic RAM state')
    same(result['accesses'],physical(observed,value,fixture),
        'the scalar RAM gated path original changes ordered physical RAM/pool/configuration/stack address, width, register or byte effects')
    same(result['branches'],value['branches'],'the scalar RAM gated path original changes an independent natural conditional/jump/return outcome')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the scalar RAM gated path original changes a complete expected natural instruction path or byte')
    if result['calls']:raise ValueError('the scalar RAM gated path original invents an outside call')
    trace=result.get('trace')
    if type(trace) is not list or tuple(row['site'] for row in trace)!=value['path']:
        raise ValueError('the scalar RAM gated path original omits its complete natural instruction trace')
    delayed={row['site']+2 for row in value['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the scalar RAM gated path original changes a conditional, jump or RTS delay slot')
    if (trace[-1]['next']!=observed['continuation'] or trace[-1]['after']['registers'][15]!=observed['sp']
            or tuple(trace[-1]['after']['registers'][:15])!=value['registers']
            or trace[-1]['after']['gbr']!=observed['context'][15] or trace[-1]['after']['macl']!=observed['context'][17]):
        raise ValueError('the scalar RAM gated path original changes complete post-delay returned GPR/SP/GBR/MACL state')
    if any(site in result['code'] for site in INFEASIBLE_INSTRUCTIONS):
        raise ValueError('the scalar RAM gated path original leaves its independent byte/word product width premise')


def require_no_selected_datum(result,rows):
    roots={row['address'] for row in rows}
    for event in result['accesses']:
        if event['domain']=='rom' and any(event['address']<=root<event['address']+event['width_bytes'] for root in roots):
            raise ValueError('the scalar RAM gated path original physically accesses a selected unsupported ROM datum root')
        if event['domain']=='rom' and event['site'] not in ROM:
            raise ValueError('the scalar RAM gated path original substitutes an undeclared ROM source for an exact instruction pool or configuration byte')
