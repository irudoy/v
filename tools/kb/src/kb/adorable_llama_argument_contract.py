"""Exact native dispositions of the adorable-llama value arguments."""

import json,tomllib
from pathlib import Path
from kb import test_contract
from kb.diagnostic_rom_contract import digest,canonical,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.adorable-llama-argument.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
TARGET='pompous-firefly/fn'
CALLER=0x413CC
WRAPPER=0x26388
ROWS=(('adorable-llama', 75736, 'adorable-llama/tbl', 267914, 267916, '1b07a2ade5dc7afacbeeb87fbbed4c9e1204d9137ef2d1f6372909716f537e13', '969326b09ad7c8e647aa8a7ea3d649054b0994f51e29b8b259b8dd48c4ebdfc4'),)
FLAGS=('physical_reader_inference','scale_admission','hardware_qualification','natural_scheduling_inference',
       'universal_no_ROM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (not test_contract.exact(value.get('schema'),1) or set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or value['id']!='jk08a-adorable-llama-argument' or value['layout']!='7mfk'
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or len(value['reference'])!=len(ROWS)):
        raise ValueError('the adorable-llama argument descriptor changes its exact admission boundary')
    keys={'id','address','owner','wrapper','caller','callsite','delay_slot','component',
          'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
          'original_ledger_json','proposed_ledger_json'}
    via=[str(SymbolKey('7mfk','fn',CALLER)),str(SymbolKey('7mfk','fn',WRAPPER))]
    for row,expected in zip(value['reference'],ROWS):
        identity,address,owner,site,delay,original,proposed=expected
        if set(row)!=keys or row['id']!=identity or row['address']!=address or row['owner']!=owner:
            raise ValueError('the adorable-llama argument changes its exact owner')
        if not test_contract.exact((row['caller'],row['wrapper'],row['callsite'],row['delay_slot'],row['component'],
                row['original_claim_sha256'],row['proposed_claim_sha256']),
                (CALLER,WRAPPER,site,delay,'adorable_llama_paths',original,proposed)):
            raise ValueError('the adorable-llama argument changes its exact caller, delay slot or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        if (digest(old)!=original or digest(new)!=proposed or old['type']!='reader' or old['to']!=TARGET
                or new['type']!='depends' or new['to']!=TARGET or new['roles']!=['arithmetic-argument']
                or new['props']['via']!=via or new['sources']!=old['sources'] or new['stated']!=old['stated']
                or new['layout']!=old['layout'] or new['owner']!=old['owner']
                or new['slot'] is not None or new['offset'] is not None or new['evidence']!=old['evidence']
                or any(not test_contract.exact(new['props'].get(key),item) for key,item in old['props'].items())
                or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
            raise ValueError('the adorable-llama argument replacement changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
