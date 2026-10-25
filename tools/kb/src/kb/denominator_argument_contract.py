"""Exact native dispositions of the two natural denominator curves."""

import json,tomllib
from pathlib import Path
from kb import test_contract
from kb.diagnostic_rom_contract import plain,digest,canonical,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.denominator-arguments.toml'
KEY='denominator-argument-v1:jk08a-natural-entries'
PREFIX='denominator-argument-'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ROWS=(('parent-a-curve',0x14AFA,'unnatural-petrel/tbl',0x264CC),
      ('parent-b-curve',0x18DD6,'micro-penguin/tbl',0x266BC))
ORIGINALS=('80cbf8f621c94122ed3b5f0dff31b9533041a5f2ace6551b374e9b0be836b84c',
           '7cda92c8a519a4609170e0a85cafadace5a46e9aee8956d59d4cd6165affa0a0')
PROPOSED=('36ff58c98699ee808ad63c667c11a85fd972590f4bb67abdad06a1558b34f0c3',
          '1fcec83e94754bd1cc5f4b27230e83abefd0d78e24a3a2bdd2cb5c145c25a036')
CALLERS={'parent-a-curve':(0x7B2C8,0x7B32E,0x7B330,'timing_denominator_paths'),
         'parent-b-curve':(0x7B3F4,0x7B482,0x7B484,'timing_denominator_paths')}
TARGET='unsigned_divide/fn'
FUNCTION=SymbolKey('7mfk','fn',0x21CE0)
ROLE='arithmetic-argument'
FLAGS=('physical_reader_inference','scale_admission','hardware_qualification','natural_scheduling_inference',
       'universal_no_ROM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-denominator-arguments'
            or value['layout']!='7mfk' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(ROWS)):
        raise ValueError('the denominator argument descriptor changes its exact image or admission boundary')
    keys={'id','address','owner','wrapper','caller','callsite','delay_slot','component','original_claim_sha256',
          'original_claim_json','proposed_claim_sha256','proposed_claim_json','original_ledger_json','proposed_ledger_json'}
    for row,expected,original,proposed in zip(value['reference'],ROWS,ORIGINALS,PROPOSED):
        key,address,owner,wrapper=expected
        if set(row)!=keys or not test_contract.exact({name:row[name] for name in ('id','address','owner','wrapper')},
                dict(id=key,address=address,owner=owner,wrapper=wrapper)):
            raise ValueError('a denominator argument changes its exact owner or wrapper')
        if row['original_claim_sha256']!=original or row['proposed_claim_sha256']!=proposed:
            raise ValueError('a denominator argument changes its exact original or proposed identity')
        if not test_contract.exact(tuple(row[name] for name in ('caller','callsite','delay_slot','component')),CALLERS[key]):
            raise ValueError('a denominator argument changes its exact caller, delay slot or component')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        if digest(old)!=original or digest(new)!=proposed:
            raise ValueError('a denominator argument canonical claim differs from its declared identity')
        if (old['owner']!=owner or old['to']!=TARGET or old['type']!='reader' or old['layout']!='7mfk'
                or old['slot'] is not None or old['offset'] is not None or old['roles']!=[] or old['evidence']!=[]
                or new['owner']!=owner or new['to']!=TARGET or new['type']!='depends' or new['layout']!='7mfk'
                or new['slot'] is not None or new['offset'] is not None or new['roles']!=[ROLE] or new['evidence']!=[]
                or new['sources']!=old['sources'] or new['stated']!=old['stated']
                or set(new['props'])!=set(old['props'])|{'via','note'}
                or any(not test_contract.exact(new['props'].get(name),item) for name,item in old['props'].items())
                or new['props']['via']!=[str(SymbolKey('7mfk','fn',at)) for at in (row['caller'],wrapper)]
                or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
            raise ValueError('a denominator argument replacement changes another original property or ledger selector')
    return value


def item(row):
    return dict(kind='indirect',mode='arithmetic-argument',key=KEY,path=DESCRIPTOR,
        at=f'7mfk:{row["address"]:08x}',to=FUNCTION,supports='identity',
        value=dict(owner=row['owner'],original_claim_sha256=row['original_claim_sha256'],
            caller=row['caller'],wrapper=row['wrapper'],callsite=row['callsite'],delay_slot=row['delay_slot'],
            scope='natural-denominator-argument',physical_reader_inference=False,scale_admission=False,
            natural_scheduling_inference=False,hardware_qualification=False))


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))


def dependency(row,link):
    expected=json.loads(row['proposed_claim_json']);expected['evidence']=[plain(item(row))]
    return test_contract.exact(canonical(link),expected)
