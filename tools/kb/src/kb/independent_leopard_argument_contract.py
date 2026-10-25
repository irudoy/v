"""Exact native disposition of the independent-leopard value argument."""

import json,tomllib
from pathlib import Path
from kb import test_contract
from kb.diagnostic_rom_contract import digest,canonical,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.independent-leopard-argument.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OWNER='fuzzy-giraffe/tbl'
TARGET='unsigned_divide/fn'
CALLER=0x5AC54
WRAPPER=0x26358
SITE=0x5AD62
DELAY=0x5AD64
ORIGINAL='08c132a3642b1b8b6d8249c6b6b3a5029876e3e64840b924d9762c32bb8e3ab9'
PROPOSED='5a80d091a1fe6c5dbcb63e06bfe10f62a7f3ce6f94f1d39c0cf8622ea5b3ac26'
FLAGS=('physical_reader_inference','scale_admission','hardware_qualification','natural_scheduling_inference',
       'universal_no_ROM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or value['id']!='jk08a-independent-leopard-argument' or value['layout']!='7mfk'
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] for key in FLAGS)
            or len(value['reference'])!=1):
        raise ValueError('the independent-leopard argument descriptor changes its exact admission boundary')
    row=value['reference'][0]
    keys={'id','address','owner','wrapper','caller','callsite','delay_slot','component',
          'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
          'original_ledger_json','proposed_ledger_json'}
    if set(row)!=keys or row['id']!='fuzzy-giraffe' or row['address']!=0x12522 or row['owner']!=OWNER:
        raise ValueError('the independent-leopard argument changes its exact owner')
    if not test_contract.exact((row['caller'],row['wrapper'],row['callsite'],row['delay_slot'],row['component'],
            row['original_claim_sha256'],row['proposed_claim_sha256']),
            (CALLER,WRAPPER,SITE,DELAY,'independent_leopard_paths',ORIGINAL,PROPOSED)):
        raise ValueError('the independent-leopard argument changes its exact caller, delay slot or identity')
    old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
    if (digest(old)!=ORIGINAL or digest(new)!=PROPOSED or old['type']!='reader' or old['to']!=TARGET
            or new['type']!='depends' or new['to']!=TARGET or new['roles']!=['arithmetic-argument']
            or new['props']['via']!=[str(SymbolKey('7mfk','fn',CALLER)),str(SymbolKey('7mfk','fn',WRAPPER))]
            or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
        raise ValueError('the independent-leopard argument replacement changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
