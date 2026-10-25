"""Exact conditional CVTC byte-result publication and complete native disposition."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import digest,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.cvtc-gain-output.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
FAMILY='cvtc-gain'
OWNER='curious-perch/ram'
TARGET='brilliant-ibis/fn'
ORIGINAL='cec5b97e2720bd806454629804b8da0bc2b992853dfbf7ee9fb67c8944fc9c0b'
PROPOSED='66919e81f22e84f81b0ff2ff6f41189720fc5e28548422c510f2355f4f64d99f'
ORIGINAL_NATIVE='8e26aa38619db5b250cfecc19e882ba76cbbbeb0ceb42661a34800740a18704a'
PROPOSED_NATIVE='1a5f4fc8d4607dd22790b26ad30fa4016469b9c11cd7bd912e1f96163e0b44b0'
FLAGS=('physical_reader_inference','scale_admission','units_admission','hardware_qualification',
    'natural_scheduling_inference','sensor_producer_admission','universal_no_RAM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-cvtc-gain-output'
            or value['layout']!='7mfk' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS)
            or type(value['reference']) is not list or len(value['reference'])!=1):
        raise ValueError('the CVTC result changes its exact conditional one-owner admission boundary')
    row=value['reference'][0]
    keys={'id','address','owner','target','caller','callsite','delay_slot','returned_site','store_site',
        'register','width_bytes','source_read','coordinate','curve','axis','component',
        'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
        'original_native_sha256','original_native_json','proposed_native_sha256','proposed_native_json',
        'original_ledger_json','proposed_ledger_json','original_symbol_evidence_json'}
    fields=('id','address','owner','target','caller','callsite','delay_slot','returned_site','store_site',
        'register','width_bytes','source_read','coordinate','curve','axis','component',
        'original_claim_sha256','proposed_claim_sha256','original_native_sha256','proposed_native_sha256')
    expected=('gain-byte',0xFFFF143A,OWNER,TARGET,0xC1DEC,0xC1ED4,0xC1ED6,0xC1ED8,0xC1EE2,
        0,1,0xC1ECE,0xFFFF2772,0x1205A,0x12850,'exhaust_cvtc_transition_paths',
        ORIGINAL,PROPOSED,ORIGINAL_NATIVE,PROPOSED_NATIVE)
    if set(row)!=keys or not test_contract.exact(tuple(row[key] for key in fields),expected):
        raise ValueError('the CVTC result changes its exact owner, real helper return, caller, input or byte store')
    old,new=(json.loads(row[key]) for key in ('original_claim_json','proposed_claim_json'))
    before,after=(json.loads(row[key]) for key in ('original_native_json','proposed_native_json'))
    if (digest(old)!=ORIGINAL or digest(new)!=PROPOSED or digest(before)!=ORIGINAL_NATIVE
            or digest(after)!=PROPOSED_NATIVE or old['owner']!=OWNER or old['to']!=TARGET
            or old['type']!='reader' or old['roles'] or old['evidence']
            or old['props']!=dict(layouts=['7mfk'],relies='level',supports='identity')
            or new['type']!='depends' or new['to']!=TARGET or new['roles']!=['arithmetic-output']
            or new['props']['via']!=[str(SymbolKey('7mfk','fn',0xC1DEC))]
            or set(new['props'])!=set(old['props'])|{'note','via'}
            or any(not test_contract.exact(new[key],old[key]) for key in
                ('owner','layout','slot','offset','sources','stated','evidence'))
            or any(not test_contract.exact(new['props'].get(key),item) for key,item in old['props'].items())
            or not test_contract.exact(json.loads(row['original_ledger_json']),before['ledger'])
            or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
        raise ValueError('the CVTC result changes another original claim property or retained ledger selector')
    from kb import calculation_dependency_contract as calculation
    evidence=calculation.item(dict(row,family=FAMILY,descriptor=DESCRIPTOR,
        operation_id=FAMILY+':gain-byte',role='arithmetic-output'))
    evidence['to']=evidence['to'].location
    expected_native=deepcopy(before)
    matches=[link for link in expected_native['link'] if link['type']=='reader' and link['to']==TARGET]
    if len(matches)!=1:raise ValueError('the CVTC result lacks its one complete original helper-reader relation')
    matches[0].update(type='depends',role='arithmetic-output',note=new['props']['note'],via=['7mfk:000c1dec'],evidence=[evidence])
    expected_native['ledger']=retired_ledger(row)
    if (not test_contract.exact(after,expected_native)
            or len(before['symbol'])!=1
            or not test_contract.exact(before['symbol'][0].get('evidence',[]),json.loads(row['original_symbol_evidence_json']))
            or any(key in before or any(key in symbol for symbol in before['symbol']) for key in ('width','signed'))):
        raise ValueError('the CVTC result changes another complete native fact, L0/TEST position or unset semantic type')
    return value
