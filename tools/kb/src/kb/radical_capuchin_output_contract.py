"""Exact threshold-output disposition; no table-to-divider-argument inference."""

import json
from pathlib import Path
import tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.radical-capuchin-output.toml'
ORIGINAL='a58bcad0795d1e7847fd8fe8b0a5aa7c62ea4b2e303aadf3fd0c9dd9bc38d857'
PROPOSED='b1c21f72041078046a8b460f855ce30897005d0f414d267cdf70bf084f0b36f3'
OWNER='radical-capuchin/tbl'
TARGET='sage-chamois/ram'
FLAGS=('physical_reader_inference','table_divider_argument_inference','scale_admission',
       'hardware_qualification','natural_scheduling_inference','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-radical-capuchin-output'
            or value['layout']!='7mfk'
            or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=1):
        raise ValueError('the comparison output changes its exact native scope')
    row=value['reference'][0]
    keys={'id','address','owner','RAM_address','RAM_owner','RAM_width','wrapper','caller','callsite',
          'delay_slot','comparison_site','store_site','component','original_claim_sha256','original_claim_json',
          'proposed_claim_sha256','proposed_claim_json','original_ledger_json','proposed_ledger_json'}
    if (set(row)!=keys or not test_contract.exact(tuple(row[key] for key in
            ('id','address','owner','RAM_address','RAM_owner','RAM_width','wrapper','caller','callsite',
             'delay_slot','comparison_site','store_site','component')),
            ('radical-capuchin',0x12362,OWNER,0xFFFF8CB4,TARGET,32,0x26474,0x60FB4,0x61626,0x61628,
             0x6162A,0x6162E,'radical_capuchin_paths'))
            or row['original_claim_sha256']!=ORIGINAL or row['proposed_claim_sha256']!=PROPOSED):
        raise ValueError('the comparison output changes its exact source, output, comparison or call')
    old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
    if (digest(old)!=ORIGINAL or digest(new)!=PROPOSED or old['owner']!=OWNER
            or old['to']!='pompous-firefly/fn' or old['type']!='reader'
            or new['to']!=TARGET or new['type']!='depends' or new['roles']!=['comparison-output']
            or any(not test_contract.exact(new[key],old[key]) for key in
                   ('owner','layout','slot','offset','sources','stated','evidence'))
            or set(new['props'])!=set(old['props'])|{'via','note'}
            or any(not test_contract.exact(new['props'].get(key),item) for key,item in old['props'].items())
            or new['props']['via']!=[str(SymbolKey('7mfk','fn',at)) for at in (0x60FB4,0x26474,0x21BBC)]
            or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
        raise ValueError('the comparison output changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
