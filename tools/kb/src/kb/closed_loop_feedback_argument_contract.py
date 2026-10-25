"""Three exact feedback value arguments with complete native/type/TEST preservation."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import digest
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.closed-loop-feedback-arguments.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
FAMILY='closed-loop-feedback'
TARGET='funky-toucanet/fn'
IDENTITIES = (('0005d6ae-ffff106e-reader',
  4294905966,
  'fuzzy-mouse/ram',
  380634,
  {'kind': 'stack', 'argument': 5, 'byte_offset': 3},
  1,
  'unset',
  'unset',
  '928c9951f1e5672688735f3989b21f2d9e03f7fb9185feaa3ca5ac87e47d1aa1',
  'ca5ace58fb88dc646fe213391ee0e5b3c43ab07d41631baec9911c32941b88b5',
  '669cb96b0162b60f21704fec5508ed0af0d3171a6ae43f00c57c6c7dcac2684b',
  '60aa68a248aa89641cf0266449b2926c352c6953913bb5156a88ccd3463327cb'),
 ('0005d6ae-ffff1071-reader',
  4294905969,
  'raspberry-dragon/ram',
  380658,
  {'kind': 'register', 'register': 5, 'argument': 2},
  1,
  'unset',
  'unset',
  'cc89127e93f9180455c1eef41565c5de0e6e81fd5ed018014e7da76e51dfffb2',
  '123f14c7ddfee1141e4d0ac1792ecc9692e436dbed5fb576d6097ec8a426104c',
  '921df104c305ce17f62bf1d836a56ed0be2886e1a2063dc3c2fd82f98939a630',
  '0c17f6b146f96815e91466a7633d5805de6aca4b12c102102ad3b7c2a0162085'),
 ('0005d6ae-ffff11bc-reader',
  4294906300,
  'rpm/ram',
  380646,
  {'kind': 'register', 'register': 7, 'argument': 4},
  2,
  16,
  False,
  '36fbbc963182a1490e03dfe07e009022ca5bd60284c6d02b75633f7b1f8ba0c8',
  'c9a92fbd586d2073961b49ea17101672dadf6d601287da53542a9d90a2183db3',
  'ea849a7c8cdca9854eeb0d3b4b77d7e3a743ed631755053f815a1677c5c4d547',
  '6368f1c92e5a90f14aa0b5d09372047f8a2328d93fd3f7629be22ce27cbc0993'))
FLAGS = ('physical_reader_inference', 'scale_admission', 'units_admission', 'hardware_qualification', 'natural_scheduling_inference', 'universal_no_RAM_read', 'unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-closed-loop-feedback-arguments'
            or value['layout']!='7mfk' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS)
            or type(value['reference']) is not list or len(value['reference'])!=3):
        raise ValueError('the feedback arguments change their exact source or three-owner scope')
    keys={'id','address','owner','function','caller','target','source_read','callsite','delay_slot','location',
        'sites','direction','source','component','width_bytes','declared_width','declared_signed',
        'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
        'original_native_sha256','original_native_json','proposed_native_sha256','proposed_native_json',
        'original_ledger_json','proposed_ledger_json','original_symbol_evidence_json','evidence_json'}
    fields=('id','address','owner','source_read','location','width_bytes','declared_width','declared_signed',
        'original_claim_sha256','proposed_claim_sha256','original_native_sha256','proposed_native_sha256')
    for row,identity in zip(value['reference'],IDENTITIES):
        if (set(row)!=keys or not test_contract.exact(tuple(row[key] for key in fields),identity)
                or not test_contract.exact((row['function'],row['caller'],row['target'],row['callsite'],row['delay_slot'],
                    row['component'],row['direction'],row['sites']),
                    (0x5D6AE,0x5CBEC,TARGET,0x5CEF8,0x5CEFA,'closed_loop_feedback_paths','reader',[row['source_read']]))):
            raise ValueError('a feedback argument changes its exact caller, carrier, phase, owner or identity')
        old,new=(json.loads(row[key]) for key in ('original_claim_json','proposed_claim_json'))
        before,after=(json.loads(row[key]) for key in ('original_native_json','proposed_native_json'))
        if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
                or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
                or old['owner']!=row['owner'] or old['to']!=TARGET or old['type']!='reader'
                or old['roles']!=['indexed_by'] or old['evidence']!=[]
                or old['props']!=dict(layouts=['7mfk'],reverse_relies='structure',reverse_supports='identity')
                or new['type']!='depends' or new['to']!=TARGET or new['roles']!=['arithmetic-argument']
                or new['props']['via']!=[str(SymbolKey('7mfk','fn',0x5CBEC))]
                or new['props']['relies']!='structure' or new['props']['supports']!='identity'
                or set(new['props'])!=set(old['props'])|{'note','via','relies','supports'}
                or any(not test_contract.exact(new[key],old[key]) for key in ('owner','layout','slot','offset','sources','stated','evidence'))
                or any(not test_contract.exact(new['props'].get(key),item) for key,item in old['props'].items())
                or not test_contract.exact(json.loads(row['original_ledger_json']),before.get('ledger'))
                or not test_contract.exact(json.loads(row['proposed_ledger_json']),before.get('ledger'))):
            raise ValueError('a feedback argument changes an original property, relation class or ledger position')
        from kb import calculation_dependency_contract as calculation
        item=calculation.item(dict(row,family=FAMILY,descriptor=DESCRIPTOR,
            operation_id=FAMILY+':'+row['id'],role='arithmetic-argument'))
        item['to']=item['to'].location
        if not test_contract.exact(item,json.loads(row['evidence_json'])):
            raise ValueError('a feedback argument changes its exact reserved evidence item')
        expected=deepcopy(before)
        matches=[link for link in expected['link'] if link['type']=='reader' and link['to']==TARGET]
        if len(matches)!=1:raise ValueError('a feedback argument lacks its one complete original native relation')
        matches[0].update(type='depends',role='arithmetic-argument',relies='structure',supports='identity',
            note=new['props']['note'],via=['7mfk:0005cbec'],evidence=[item])
        symbol=next(symbol for symbol in before['symbol'] if symbol['layout']=='7mfk' and int(symbol['address'],16)==row['address'])
        width=None if row['declared_width']=='unset' else row['declared_width']
        signed=None if row['declared_signed']=='unset' else row['declared_signed']
        if (not test_contract.exact(after,expected)
                or not test_contract.exact((symbol.get('width'),symbol.get('signed')),(width,signed))
                or not test_contract.exact(symbol.get('evidence',[]),json.loads(row['original_symbol_evidence_json']))):
            raise ValueError('a feedback argument changes another native fact, semantic type, TEST attachment or evidence position')
    return value
