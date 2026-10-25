"""One exact bare helper-reader disposition through the real coordinate call."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import digest
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.closed-loop-sample-argument.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
FAMILY='closed-loop-sample'
OWNER='placid-jackrabbit/ram'
TARGET='screeching-panther/fn'
ORIGINAL='f1396c2c91e34029ae10383d5ad32a5671db7d1ef3c7e2fbcc6def256b8b11dc'
PROPOSED='99cf8f379dae318eea43badfd3f29f9dee76d6ddf80d38f75c191a48df75265b'
ORIGINAL_NATIVE='c7f01e7f30744008d746b12bfabfcb1e0973964431ff8aab202bbac86afe34ce'
PROPOSED_NATIVE='336c71e193574cf3d777e1576b3e3b35811b9765dcbf10d9088bdf9aa0aa9d4d'
FLAGS=('physical_reader_inference','scale_admission','hardware_qualification',
    'natural_scheduling_inference','universal_no_RAM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1)
            or value['id']!='jk08a-closed-loop-sample-argument' or value['layout']!='7mfk'
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or type(value['reference']) is not list or len(value['reference'])!=1):
        raise ValueError('the coordinate sample argument changes its exact one-owner scope')
    row=value['reference'][0]
    keys={'id','address','owner','caller','target','source_read','callsite','delay_slot','register',
        'width_bytes','component','original_claim_sha256','original_claim_json',
        'proposed_claim_sha256','proposed_claim_json','original_ledger_json','proposed_ledger_json',
        'original_native_sha256','original_native_json','proposed_native_sha256','proposed_native_json'}
    fields=('id','address','owner','caller','target','source_read','callsite','delay_slot','register',
        'width_bytes','component','original_claim_sha256','proposed_claim_sha256',
        'original_native_sha256','proposed_native_sha256')
    expected=('sample-word',0xFFFF4524,OWNER,0x3EDB4,TARGET,0x3EE72,0x3EE7A,0x3EE7C,6,2,
        'closed_loop_coordinate_paths',ORIGINAL,PROPOSED,ORIGINAL_NATIVE,PROPOSED_NATIVE)
    if set(row)!=keys or not test_contract.exact(tuple(row[key] for key in fields),expected):
        raise ValueError('the coordinate sample argument changes its exact read, delay, register or owner')
    old,new=(json.loads(row[key]) for key in ('original_claim_json','proposed_claim_json'))
    old_native,new_native=(json.loads(row[key]) for key in ('original_native_json','proposed_native_json'))
    if (digest(old)!=ORIGINAL or digest(new)!=PROPOSED or digest(old_native)!=ORIGINAL_NATIVE
            or digest(new_native)!=PROPOSED_NATIVE or old['owner']!=OWNER or old['to']!=TARGET
            or old['type']!='reader' or old['roles']!=['indexed_by'] or old['evidence']!=[]
            or old['props']!=dict(layouts=['7mfk'],reverse_relies='structure',reverse_supports='identity')
            or new['type']!='depends' or new['to']!=TARGET or new['roles']!=['arithmetic-argument']
            or new['props']['via']!=[str(SymbolKey('7mfk','fn',0x3EDB4))]
            or new['props']['relies']!='structure' or new['props']['supports']!='identity'
            or set(new['props'])!=set(old['props'])|{'note','via','relies','supports'}
            or any(not test_contract.exact(new[key],old[key]) for key in
                ('owner','layout','slot','offset','sources','stated','evidence'))
            or any(not test_contract.exact(new['props'].get(key),item) for key,item in old['props'].items())
            or not test_contract.exact(json.loads(row['original_ledger_json']),old_native['ledger'])
            or not test_contract.exact(json.loads(row['proposed_ledger_json']),old_native['ledger'])):
        raise ValueError('the coordinate sample argument changes an original property or ledger value')
    from kb import calculation_dependency_contract as calculation
    item=calculation.item(dict(row,family=FAMILY,descriptor=DESCRIPTOR,
        operation_id=FAMILY+':sample-word',role='arithmetic-argument'))
    item['to']=item['to'].location
    expected_native=deepcopy(old_native)
    matches=[entry for entry in expected_native['link'] if entry['type']=='reader' and entry['to']==TARGET]
    if len(matches)!=1:
        raise ValueError('the coordinate sample argument lacks its one exact original native link')
    matches[0].update(type='depends',role='arithmetic-argument',relies='structure',supports='identity',
        note=new['props']['note'],via=['7mfk:0003edb4'],evidence=[item])
    if (not test_contract.exact(new_native,expected_native)
            or any(key in symbol for symbol in new_native['symbol'] for key in ('width','signed'))):
        raise ValueError('the coordinate sample argument changes another native relation, TEST attachment or semantic type')
    return value
