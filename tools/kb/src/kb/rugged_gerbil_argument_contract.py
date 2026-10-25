"""Exact native dispositions of the rugged-gerbil value arguments."""

import json,tomllib
from pathlib import Path
from kb import test_contract
from kb.diagnostic_rom_contract import digest,canonical,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.rugged-gerbil-argument.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
TARGET='unsigned_divide/fn'
CALLER=0x8152A
WRAPPER=0x263F4
ROWS=(('rugged-gerbil',0x15022,'rugged-gerbil/tbl',0x8169A,0x8169C,
       'f1037864537f49062fcf0720b2b450191bb539a2c3c4f39f93cbd67501386474',
       '951893274bbef1f6f5c4eaf61a54750d30eaa18c25d59f9aba258fc6d556d54d'),)
FLAGS=('physical_reader_inference','scale_admission','hardware_qualification','natural_scheduling_inference',
       'universal_no_ROM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (not test_contract.exact(value.get('schema'),1) or set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or value['id']!='jk08a-rugged-gerbil-argument' or value['layout']!='7mfk'
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or len(value['reference'])!=len(ROWS)):
        raise ValueError('the rugged-gerbil argument descriptor changes its exact admission boundary')
    keys={'id','address','owner','wrapper','caller','callsite','delay_slot','component',
          'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
          'original_ledger_json','proposed_ledger_json'}
    via=[str(SymbolKey('7mfk','fn',CALLER)),str(SymbolKey('7mfk','fn',WRAPPER))]
    for row,expected in zip(value['reference'],ROWS):
        identity,address,owner,site,delay,original,proposed=expected
        if set(row)!=keys or row['id']!=identity or row['address']!=address or row['owner']!=owner:
            raise ValueError('the rugged-gerbil argument changes its exact owner')
        if not test_contract.exact((row['caller'],row['wrapper'],row['callsite'],row['delay_slot'],row['component'],
                row['original_claim_sha256'],row['proposed_claim_sha256']),
                (CALLER,WRAPPER,site,delay,'rugged_gerbil_paths',original,proposed)):
            raise ValueError('the rugged-gerbil argument changes its exact caller, delay slot or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        if (digest(old)!=original or digest(new)!=proposed or old['type']!='reader' or old['to']!=TARGET
                or new['type']!='depends' or new['to']!=TARGET or new['roles']!=['arithmetic-argument']
                or new['props']['via']!=via or new['sources']!=old['sources'] or new['stated']!=old['stated']
                or new['layout']!=old['layout'] or new['owner']!=old['owner']
                or new['slot'] is not None or new['offset'] is not None or new['evidence']!=old['evidence']
                or any(not test_contract.exact(new['props'].get(key),item) for key,item in old['props'].items())
                or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
            raise ValueError('the rugged-gerbil argument replacement changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
