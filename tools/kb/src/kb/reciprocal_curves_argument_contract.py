"""Exact native dispositions of the reciprocal-curves value arguments."""

import json,tomllib
from pathlib import Path
from kb import test_contract
from kb.diagnostic_rom_contract import digest,canonical,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.reciprocal-curves-arguments.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
TARGET='pompous-firefly/fn'
CALLER=0x69374
WRAPPER=0x264CC
ROWS=(('first', 145348, 'peach-skunk/tbl', 431652, 431654, '87c3b21c57403c559bb402adca4c55fa875d4b3c0df5d8e54d77f6e74f1771d4', '20bbdb6d0d7175203bee36abfffdd24622739607e606de9f6b704d016d5627b3'), ('second', 145412, 'strange-sturgeon/tbl', 431816, 431818, '9779853b6b81cad9c9e9ded0f938311affce3e5921aa68d501b60222a9f112ad', '8ae07275121c595f890b0842dd8b6c060d014371e4f45ac305e9f70d0d700e1c'))
FLAGS=('physical_reader_inference','scale_admission','hardware_qualification','natural_scheduling_inference',
       'universal_no_ROM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (not test_contract.exact(value.get('schema'),1) or set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or value['id']!='jk08a-reciprocal-curves-arguments' or value['layout']!='7mfk'
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or len(value['reference'])!=len(ROWS)):
        raise ValueError('the reciprocal-curves argument descriptor changes its exact admission boundary')
    keys={'id','address','owner','wrapper','caller','callsite','delay_slot','component',
          'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
          'original_ledger_json','proposed_ledger_json'}
    via=[str(SymbolKey('7mfk','fn',CALLER)),str(SymbolKey('7mfk','fn',WRAPPER))]
    for row,expected in zip(value['reference'],ROWS):
        identity,address,owner,site,delay,original,proposed=expected
        if set(row)!=keys or row['id']!=identity or row['address']!=address or row['owner']!=owner:
            raise ValueError('the reciprocal-curves argument changes its exact owner')
        if not test_contract.exact((row['caller'],row['wrapper'],row['callsite'],row['delay_slot'],row['component'],
                row['original_claim_sha256'],row['proposed_claim_sha256']),
                (CALLER,WRAPPER,site,delay,'reciprocal_curves_paths',original,proposed)):
            raise ValueError('the reciprocal-curves argument changes its exact caller, delay slot or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        if (digest(old)!=original or digest(new)!=proposed or old['type']!='reader' or old['to']!=TARGET
                or new['type']!='depends' or new['to']!=TARGET or new['roles']!=['arithmetic-argument']
                or new['props']['via']!=via
                or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
            raise ValueError('the reciprocal-curves argument replacement changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
