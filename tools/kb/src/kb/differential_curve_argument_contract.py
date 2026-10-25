"""Exact native representations of the sequenced differential_curve arguments."""

import json
from pathlib import Path
import tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.differential-curve-arguments.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ROWS=(('first', 75576, 'unique-spider/tbl', '4fda54cceb753487c11ce575eb109b5923822781ea4392537a43c816385bd1c5', '1ea0b2b7c9376ced38fc1ffcbe8e99006b79488c7c14b52c0d1cd887baabd47b'), ('second', 75592, 'dexterous-bobcat/tbl', '16d40e47867f403fba1e7b783da1dbac40f08c380e7f44f29ba8d43c5a5cdc88', '06a1aa016ccf95fe50ce674589e646d6f40db1addacf83a98b21a025ff640f34'))
FLAGS=('physical_reader_inference', 'scale_admission', 'hardware_qualification', 'natural_scheduling_inference', 'universal_no_ROM_read', 'unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-differential-curve-arguments'
            or value['layout']!='7mfk' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(ROWS)):
        raise ValueError('the differential_curve argument descriptor changes its exact conditional scope')
    keys={'id','address','owner','target','caller','wrapper','callsite','delay_slot','component',
          'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
          'original_ledger_json','proposed_ledger_json'}
    for row,expected in zip(value['reference'],ROWS):
        key,address,owner,original,proposed=expected
        if (set(row)!=keys or not test_contract.exact(tuple(row[name] for name in
                ('id','address','owner','original_claim_sha256','proposed_claim_sha256')),expected)
                or not test_contract.exact(tuple(row[name] for name in
                    ('target','caller','wrapper','callsite','delay_slot','component')),
                    ('pompous-firefly/fn',0x44910,0x26388,0x44A9C,0x44A9E,'differential_curve_paths'))):
            raise ValueError('a differential_curve argument changes its exact source, call or delay slot')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        if (digest(old)!=original or digest(new)!=proposed or old['type']!='reader' or old['to']!='pompous-firefly/fn'
                or new['type']!='depends' or new['to']!=old['to'] or new['roles']!=['arithmetic-argument']
                or new['props']['via']!=[str(SymbolKey('7mfk','fn',at)) for at in (0x44910,0x26388)]
                or any(not test_contract.exact(new[name],old[name]) for name in
                       ('owner','layout','slot','offset','sources','stated','evidence'))
                or any(not test_contract.exact(new['props'].get(name),item) for name,item in old['props'].items())
                or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
            raise ValueError('a differential_curve argument changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
