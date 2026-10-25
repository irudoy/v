"""Exact native disposition of the signed-curve value argument."""

import json,tomllib
from pathlib import Path
from kb import test_contract
from kb.diagnostic_rom_contract import digest,canonical,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.signed-curve-argument.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OWNER='vagabond-seagull/tbl'
TARGET='pompous-firefly/fn'
CALLS=(0x7B150,0x7B168,0x7B180)
DELAYS=(0x7B152,0x7B16A,0x7B182)
FLAGS=('physical_reader_inference','scale_admission','hardware_qualification','natural_scheduling_inference',
       'universal_no_ROM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or value['id']!='jk08a-signed-curve-argument' or value['layout']!='7mfk'
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] for key in FLAGS)
            or len(value['reference'])!=1):
        raise ValueError('the signed-curve argument descriptor changes its exact admission boundary')
    row=value['reference'][0]
    keys={'id','address','owner','wrapper','caller','callsites','delay_slots','component','target',
          'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
          'original_ledger_json','proposed_ledger_json'}
    if set(row)!=keys or row['id']!='signed-curve' or row['address']!=0x18DE6 or row['owner']!=OWNER:
        raise ValueError('the signed-curve argument changes its exact owner')
    if not test_contract.exact((row['caller'],row['wrapper'],tuple(row['callsites']),tuple(row['delay_slots']),row['component'],row['target']),
            (0x7B0A0,0x266E8,CALLS,DELAYS,'signed_curve_paths',TARGET)):
        raise ValueError('the signed-curve argument changes its exact caller, delay slots or callee')
    old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
    if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
            or old['type']!='reader' or old['to']!=TARGET or new['type']!='depends' or new['to']!=TARGET
            or new['roles']!=['arithmetic-argument']
            or new['props']['via']!=[str(SymbolKey('7mfk','fn',0x7B0A0)),str(SymbolKey('7mfk','fn',0x266E8))]
            or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
        raise ValueError('the signed-curve argument replacement changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
