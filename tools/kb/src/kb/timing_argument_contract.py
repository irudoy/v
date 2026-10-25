"""Exact native representations of conditional arithmetic arguments."""

import json,tomllib
from kb import copy_evidence,test_contract
from kb.diagnostic_rom_contract import plain,digest,canonical,retired_ledger,native_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.timing-arguments.toml'
KEY='timing-argument-v1:jk08a-timing-callers'
PREFIX='timing-argument-'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ROWS=(('word-surface', 50446, 'fabulous-marmoset/tbl', 156272), ('byte-curve', 73474, 'charming-barracuda/tbl', 156788), ('tail-word-curve', 83914, 'indigo-fossa/tbl', 156876), ('tail-byte-curve', 73466, 'outrageous-bustard/tbl', 156788))
ORIGINALS=('35213c7b97eeee5f2a5d75c20d6eee5e8bab2beae882f4b97cff39eb46cb7539', '6784063a95462c327013e45d4a1cfce2a3669bce977be699827796b5cb49055f', 'dc009defbab5164ac4ca0fef08449641ff9b77a5fa2113307fc0b9b98f0821b5', '632ada197b3fbdc4a3f3348737ac25dc77a5671f1e95eea4e5eeba63f5a04fa7')
PROPOSED=('00cf4e3d0d70d9ee0708a81b36dd938301f23a0228b8ebf4a8becea05c1ab715', 'aa12876f528842df04eb5889e264638371cf82befda2ace14409941adc8a5040', '256e67176d2d5e7b24b98070caf0b55db40400b6c2fd720231cdc466d76691fd', '27e7c277e4b07d00b85ddfc4db89096e473950785410bf7d8b57b5ba10983bb9')
CALLERS={'word-surface': (310722, 310912, 310914, 'timing_division_paths'), 'byte-curve': (310722, 310912, 310914, 'timing_division_paths'), 'tail-word-curve': (307164, 308336, 308338, 'timing_tail_paths'), 'tail-byte-curve': (307164, 308336, 308338, 'timing_tail_paths')}
TARGET='unsigned_divide/fn'
FUNCTION=SymbolKey('7mfk','fn',0x21CE0)
ROLE='arithmetic-argument'
FLAGS=('physical_reader_inference','scale_admission','hardware_qualification','natural_scheduling_inference',
       'universal_no_ROM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads(copy_evidence._read(root,DESCRIPTOR).decode())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-timing-arguments'
            or value['layout']!='7mfk' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(ROWS)):
        raise ValueError('the timing argument descriptor changes its exact image or admission boundary')
    keys={'id','address','owner','wrapper','caller','callsite','delay_slot','component','original_claim_sha256','original_claim_json',
        'proposed_claim_sha256','proposed_claim_json','original_ledger_json','proposed_ledger_json'}
    for row,expected,original,proposed in zip(value['reference'],ROWS,ORIGINALS,PROPOSED):
        key,address,owner,wrapper=expected
        if (set(row)!=keys or not test_contract.exact({name:row[name] for name in ('id','address','owner','wrapper')},
                dict(id=key,address=address,owner=owner,wrapper=wrapper))
                or row['original_claim_sha256']!=original or row['proposed_claim_sha256']!=proposed):
            raise ValueError('a timing argument changes its exact owner, wrapper or original identity')
        if not test_contract.exact(tuple(row[name] for name in ('caller','callsite','delay_slot','component')),CALLERS[key]):
            raise ValueError('a timing argument changes its exact caller, delay slot or original component')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        if digest(old)!=original or digest(new)!=proposed:
            raise ValueError('a timing argument canonical claim differs from its complete declared identity')
        if (old['owner']!=owner or old['to']!=TARGET or old['type']!='reader' or old['layout']!='7mfk'
                or old['slot'] is not None or old['offset'] is not None or old['roles']!=[] or old['evidence']!=[]
                or new['owner']!=owner or new['to']!=TARGET or new['type']!='depends' or new['layout']!='7mfk'
                or new['slot'] is not None or new['offset'] is not None or new['roles']!=[ROLE] or new['evidence']!=[]
                or new['sources']!=old['sources'] or new['stated']!=old['stated']
                or set(new['props'])!=set(old['props'])|{'via','note'}
                or any(not test_contract.exact(new['props'].get(name),item) for name,item in old['props'].items())
                or new['props']['via']!=[str(SymbolKey('7mfk','fn',at)) for at in (row['caller'],wrapper)]
                or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
            raise ValueError('a timing argument replacement changes another original property or ledger selector')
    return value


def item(row):
    return dict(kind='indirect',mode='arithmetic-argument',key=KEY,path=DESCRIPTOR,
        at=f'7mfk:{row["address"]:08x}',to=FUNCTION,supports='identity',
        value=dict(owner=row['owner'],original_claim_sha256=row['original_claim_sha256'],
            caller=row['caller'],wrapper=row['wrapper'],callsite=row['callsite'],delay_slot=row['delay_slot'],
            scope='conditional-timing-argument',physical_reader_inference=False,scale_admission=False,
            natural_scheduling_inference=False,hardware_qualification=False))


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))


def dependency(row,link):
    expected=json.loads(row['proposed_claim_json']);expected['evidence']=[plain(item(row))]
    return test_contract.exact(canonical(link),expected)


def registered(evidence):
    return (evidence.get('mode')=='arithmetic-argument' or evidence.get('path')==DESCRIPTOR
        or isinstance(evidence.get('key'),str) and evidence['key'].startswith(PREFIX))


def looks_like_dependency(link):
    return (ROLE in link.roles or any(registered(item) for item in link.evidence)
        or any(link.owner.key==owner and link.type=='depends' and link.to.key==TARGET
               for key,address,owner,wrapper in ROWS))
