"""Exact native dispositions of the three natural fine-gopher curves."""

import json,tomllib
from pathlib import Path
from kb import test_contract
from kb.diagnostic_rom_contract import plain,digest,canonical,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.fine-gopher-arguments.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ROWS=(('rare-groundhog',0x14F42,'rare-groundhog/tbl',0x264CC,0x6062C,0x60710,0x60712),
      ('ochre-tuna',0x14F52,'ochre-tuna/tbl',0x264CC,0x6062C,0x607B6,0x607B8),
      ('steady-beetle',0x15002,'steady-beetle/tbl',0x264CC,0x6062C,0x608C2,0x608C4))
ORIGINALS=('0802816efab791dc9628d684e8242ad4dd93bb30f11652870493199eb0336c88',
           '4a791359b5580126c4c6df9c1cfaced3ce3c51b7f8ecc4f2765876b589b53147',
           '3a41ee5da39614237a9eee1035313bc318b154eccdb10702ce3b348eeda904b5')
PROPOSED=('172723b188b9105e9293e5aeb036825da0f8af3618839ad95f328d7b77584ddb',
          'd7dfcfd30bcbaa2750e7b45338743b6d394a05d4a0e732141106833fba6aabc4',
          '48c8d7e6f0e1140e4e8eeda6d8b1035c9b63729592cdd2d4bcfef4267421b82f')
TARGET='unsigned_divide/fn'
FUNCTION=SymbolKey('7mfk','fn',0x21CE0)
ROLE='arithmetic-argument'
FLAGS=('physical_reader_inference','scale_admission','hardware_qualification','natural_scheduling_inference',
       'universal_no_ROM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-fine-gopher-arguments'
            or value['layout']!='7mfk' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(ROWS)):
        raise ValueError('the fine-gopher argument descriptor changes its exact image or admission boundary')
    keys={'id','address','owner','wrapper','caller','callsite','delay_slot','component','original_claim_sha256',
          'original_claim_json','proposed_claim_sha256','proposed_claim_json','original_ledger_json','proposed_ledger_json'}
    for row,expected,original,proposed in zip(value['reference'],ROWS,ORIGINALS,PROPOSED):
        key,address,owner,wrapper,caller,site,delay=expected
        if set(row)!=keys or not test_contract.exact(
                {name:row[name] for name in ('id','address','owner','wrapper','caller','callsite','delay_slot','component')},
                dict(id=key,address=address,owner=owner,wrapper=wrapper,caller=caller,callsite=site,delay_slot=delay,
                     component='fine_gopher_paths')):
            raise ValueError('a fine-gopher argument changes its exact owner, caller or delay slot')
        if row['original_claim_sha256']!=original or row['proposed_claim_sha256']!=proposed:
            raise ValueError('a fine-gopher argument changes its exact original or proposed identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        if digest(old)!=original or digest(new)!=proposed:
            raise ValueError('a fine-gopher argument canonical claim differs from its declared identity')
        if (old['owner']!=owner or old['to']!=TARGET or old['type']!='reader' or old['layout']!='7mfk'
                or old['slot'] is not None or old['offset'] is not None or old['roles']!=[] or old['evidence']!=[]
                or new['owner']!=owner or new['to']!=TARGET or new['type']!='depends' or new['layout']!='7mfk'
                or new['slot'] is not None or new['offset'] is not None or new['roles']!=[ROLE] or new['evidence']!=[]
                or new['sources']!=old['sources'] or new['stated']!=old['stated']
                or set(new['props'])!=set(old['props'])|{'via','note'}
                or any(not test_contract.exact(new['props'].get(name),item) for name,item in old['props'].items())
                or new['props']['via']!=[str(SymbolKey('7mfk','fn',at)) for at in (caller,wrapper)]
                or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
            raise ValueError('a fine-gopher argument replacement changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
