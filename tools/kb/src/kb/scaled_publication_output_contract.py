"""Exact native representations of two conditional arithmetic outputs."""

import json
from pathlib import Path
import tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.scaled-publication-outputs.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ROWS=(('first', 4294906384, 'jasper-taipan/ram', 'pompous-firefly/fn', 501138, 501636, 501638, 501652, 'signed', 'f5256752759284c2fd37d7926c4ebf672bea878ca5f15d5dda65bca240ab4ab6', 'c10f1e03863fc211203718fd15e556ec7179253e86ded14d7fec048d1a769eb5'), ('second', 4294906440, 'snobbish-bird/ram', 'unsigned_divide/fn', 501764, 502134, 502136, 502144, 'unsigned', '92bf91b5ce6edcf089184a5c65066fc7cccc5c607bfc3211d5c545df465757c2', '8249d2970b09d4243ae6219f5a8a769f461f07b32662f8cb56972de4b85bb45b'))
FLAGS=('physical_reader_inference', 'scale_admission', 'hardware_qualification', 'natural_scheduling_inference', 'universal_no_ROM_read', 'unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-scaled-publication-outputs'
            or value['layout']!='7mfk' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(ROWS)):
        raise ValueError('the arithmetic output descriptor changes its exact conditional scope')
    keys={'id','address','owner','target','caller','callsite','delay_slot','store_site','kind','component',
          'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
          'original_ledger_json','proposed_ledger_json'}
    for row,expected in zip(value['reference'],ROWS):
        key,address,owner,target,parent,site,delay,store,kind,original,proposed=expected
        if (set(row)!=keys or not test_contract.exact(tuple(row[name] for name in
                ('id','address','owner','target','caller','callsite','delay_slot','store_site','kind',
                 'original_claim_sha256','proposed_claim_sha256')),expected)
                or row['component']!='scaled_publication_paths'):
            raise ValueError('an arithmetic output changes its complete original identity, call or store')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        if (digest(old)!=original or digest(new)!=proposed or old['type']!='reader' or old['to']!=target
                or new['type']!='depends' or new['to']!=target or new['roles']!=['arithmetic-output']
                or new['props']['via']!=[str(SymbolKey('7mfk','fn',parent))]
                or any(not test_contract.exact(new[name],old[name]) for name in
                       ('owner','layout','slot','offset','sources','stated','evidence'))
                or any(not test_contract.exact(new['props'].get(name),item) for name,item in old['props'].items())
                or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
            raise ValueError('an arithmetic output changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
