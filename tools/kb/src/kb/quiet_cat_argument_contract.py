"""Exact native dispositions of the quiet-cat value arguments."""

import json,tomllib
from pathlib import Path
from kb import test_contract
from kb.diagnostic_rom_contract import digest,canonical,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.quiet-cat-argument.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
TARGET='pompous-firefly/fn'
CALLER=0xBE32A
WRAPPER=0x26474
SITE=0xBE41E
DELAY=0xBE420
ROWS=(('belligerent-potoo',0x123EA,'belligerent-potoo/tbl',
       'aa532916bff8865d5a53d99b38677467c90b047748d1f2b0fd01c53bc920d464',
       '7e4ba08c38431dede818b43c7b53d2959bef063ad5e1475dcf02752a88e3a491'),
      ('red-bullmastiff',0x12412,'red-bullmastiff/tbl',
       '5fe1a1f3a93cc936590de0f3ff67df7b18f94137dc663ef31c514559f7c22991',
       '3534db4cd5ece066f3bddcc6b5ff1ed5190ff869ab36f19693ddf7275f67702c'))
FLAGS=('physical_reader_inference','scale_admission','hardware_qualification','natural_scheduling_inference',
       'universal_no_ROM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or value['id']!='jk08a-quiet-cat-argument' or value['layout']!='7mfk'
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] for key in FLAGS)
            or len(value['reference'])!=len(ROWS)):
        raise ValueError('the quiet-cat argument descriptor changes its exact admission boundary')
    keys={'id','address','owner','wrapper','caller','callsite','delay_slot','component',
          'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
          'original_ledger_json','proposed_ledger_json'}
    via=[str(SymbolKey('7mfk','fn',CALLER)),str(SymbolKey('7mfk','fn',WRAPPER))]
    for row,expected in zip(value['reference'],ROWS):
        identity,address,owner,original,proposed=expected
        if set(row)!=keys or row['id']!=identity or row['address']!=address or row['owner']!=owner:
            raise ValueError('the quiet-cat argument changes its exact owner')
        if not test_contract.exact((row['caller'],row['wrapper'],row['callsite'],row['delay_slot'],row['component'],
                row['original_claim_sha256'],row['proposed_claim_sha256']),
                (CALLER,WRAPPER,SITE,DELAY,'quiet_cat_paths',original,proposed)):
            raise ValueError('the quiet-cat argument changes its exact caller, delay slot or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        if (digest(old)!=original or digest(new)!=proposed or old['type']!='reader' or old['to']!=TARGET
                or new['type']!='depends' or new['to']!=TARGET or new['roles']!=['arithmetic-argument']
                or new['props']['via']!=via
                or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
            raise ValueError('the quiet-cat argument replacement changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
