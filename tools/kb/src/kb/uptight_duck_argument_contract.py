"""Exact native disposition of the uptight-duck publication."""

import json,tomllib
from pathlib import Path
from kb import test_contract
from kb.diagnostic_rom_contract import digest,canonical,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.uptight-duck-argument.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OWNER='blond-panther/tbl'
TARGET='pompous-firefly/fn'
CALLER=0xB784E
WRAPPER=0x26524
SITE=0xB7892
DELAY=0xB7894
ORIGINAL='2d7b312e121db61661500de403724e6f1819cb75161bdd58a0ca8121adced08a'
PROPOSED='a1d8bba4066d78f247e88e99810bb30c1352b75a5c12ce78e9a9e05553852498'
ROLE='conditional-publication'
FLAGS=('physical_reader_inference','scale_admission','hardware_qualification','natural_scheduling_inference',
       'universal_no_ROM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or value['id']!='jk08a-uptight-duck-argument' or value['layout']!='7mfk'
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] for key in FLAGS)
            or len(value['reference'])!=1):
        raise ValueError('the uptight-duck argument descriptor changes its exact admission boundary')
    row=value['reference'][0]
    keys={'id','address','owner','wrapper','caller','callsite','delay_slot','component',
          'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
          'original_ledger_json','proposed_ledger_json'}
    if set(row)!=keys or row['id']!='blond-panther' or row['address']!=0x15C80 or row['owner']!=OWNER:
        raise ValueError('the uptight-duck argument changes its exact owner')
    if not test_contract.exact((row['caller'],row['wrapper'],row['callsite'],row['delay_slot'],row['component'],
            row['original_claim_sha256'],row['proposed_claim_sha256']),
            (CALLER,WRAPPER,SITE,DELAY,'uptight_duck_paths',ORIGINAL,PROPOSED)):
        raise ValueError('the uptight-duck argument changes its exact caller, delay slot or identity')
    old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
    if (digest(old)!=ORIGINAL or digest(new)!=PROPOSED or old['type']!='reader' or old['to']!=TARGET
            or new['type']!='depends' or new['to']!=TARGET or new['roles']!=[ROLE]
            or new['props']['via']!=[str(SymbolKey('7mfk','fn',CALLER)),str(SymbolKey('7mfk','fn',WRAPPER))]
            or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
        raise ValueError('the uptight-duck argument replacement changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
