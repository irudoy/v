"""One exact retained pedal snapshot quantity relation and complete owning append."""
from copy import deepcopy
from pathlib import Path
import json,tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,plain
from kb.model import SymbolKey
DESCRIPTOR='defs/JK08A.pedal-snapshot-high-state-claims.toml'
MODE='pedal-snapshot-high-state-access'
PREFIX='pedal-snapshot-high-state-access-v1:jk08a:'
DECLARED={'schema': 1,
 'id': 'jk08a-pedal-snapshot-high-state-claims',
 'layout': '7mfk',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'One retained pedal quantity reader through the exact existing coherent history and full '
          'comparator; no instruction-level2672 read attribution to the comparator.',
 'native_function_publication': False,
 'native_geometry_publication': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'reference': [{'id': 'retained-2672-pedal-consumer',
                'address': 4294911602,
                'owner': 'pedal/ram',
                'function': 293462,
                'sites': [293546, 293780],
                'direction': 'reader',
                'source': 'kb/ram/pedal.toml',
                'component': 'pedal_snapshot_high_state_paths',
                'width_bytes': 2,
                'declared_width': 'unset',
                'declared_signed': 'unset',
                'original_claim_sha256': '93ee923889e9a6cf710b7da182de3b6da80f76d3a1d5d127fdab38b28d38de5a',
                'original_claim_json': '{"evidence":[],"layout":"7mfk","offset":null,"owner":"pedal/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/pedal.toml"],"stated":["7mfk"],"to":"remarkable-lynx/fn","type":"reader"}',
                'proposed_claim_sha256': '5e2608e1283fa2d3c27879a37a1243a9414331993dc488a8abdb68f62ce25ec7',
                'proposed_claim_json': '{"evidence":[{"at":"7mfk:00047aaa","key":"pedal-snapshot-high-state-access-v1:jk08a:retained-2672-pedal-consumer","kind":"indirect","mode":"pedal-snapshot-high-state-access","note":"Exact '
                                       'existing coherent history and complete pedal-state consumer with '
                                       'continuous actual RAM, independent physical/CPU/numerical checks and '
                                       'held-other source alternatives; all native facts and TEST positions '
                                       'remain '
                                       'fixed.","path":"defs/JK08A.pedal-snapshot-high-state-claims.toml","supports":"identity","value":{"actual_output":{"address":4294911082,"mask":128,"width_bytes":1},"complete_RAM_calibration_bound_continuity":true,"component":"pedal_snapshot_high_state_paths","consumer_entry":293462,"consumer_reads":[{"address":4294911598,"site":293546,"width_bytes":2},{"address":4294911598,"site":293780,"width_bytes":2}],"direction":"reader","existing_snapshot_entry_conditions_retained":true,"function":"7mfk:00047a56","hardware_qualification":false,"native_address":4294911602,"native_geometry_inference":false,"natural_caller_reachability":false,"natural_scheduling_inference":false,"original_claim_sha256":"93ee923889e9a6cf710b7da182de3b6da80f76d3a1d5d127fdab38b28d38de5a","owner":"pedal/ram","producer_entry":135076,"producer_parent":134654,"producer_store":{"address":4294911598,"site":135108,"width_bytes":2},"scale_admission":false,"scope":"exact-existing-prefix-pedal-state-quantity","source_read":{"address":4294911602,"site":135104,"width_bytes":2},"units_admission":false,"width_bytes":2}}],"layout":"7mfk","offset":null,"owner":"pedal/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/pedal.toml"],"stated":["7mfk"],"to":"remarkable-lynx/fn","type":"reader"}',
                'original_native_sha256': '5ef7a8a18157e748fed23eb2e741a81a22842d3008f17a1e52358933c3e7f9af',
                'original_native_json': '{"ledger":[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"coherent_snapshot/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"remarkable-lynx/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"accelerator_pedal_pair_selector/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2],"notes":[0],"order":216,"registry":"vars"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"coherent_snapshot/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"remarkable-lynx/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","reverse_relies":"structure","reverse_supports":"identity","supports":"identity","to":"accelerator_pedal_pair_selector/fn","type":"writer"}],"note":["This '
                                        'internal normalized count is not either individual sensor '
                                        'voltage."],"summary":"Current normalized dual-channel '
                                        'accelerator-pedal quantity. FUN 0006ec68 clamps two adjusted analog '
                                        'channels, selects their minimum with mode handling, optionally '
                                        'rate-limits it, and writes this word; scheduler 00020dfe snapshots '
                                        'it to '
                                        'ffff266e.","symbol":[{"address":"fffe96a0","evidence":[{"at":"1me3b:00020b30","kind":"l0","note":"Pedal '
                                        'activation source is recovered from target '
                                        'consumers","supports":"homology","to":"7mfk:ffff2672"}],"layout":"1me3b"},{"address":"fffe96c8","evidence":[{"at":"1nd:00020b12","kind":"l0","note":"Pedal '
                                        'activation source is recovered from target '
                                        'consumers","supports":"homology","to":"7mfk:ffff2672"}],"layout":"1nd"},{"address":"ffff2672","evidence":[{"at":"7mfk:00020fc0","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00020dfe","00047a56","0006ec68","ffff2672"],"span":1}},{"at":"7mfk:00020fc4","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00020dfe","00047a56","0006ec68","ffff2672"],"span":1}},{"at":"7mfk:0006ed6e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00020dfe","00047a56","0006ec68","ffff2672"],"span":1}}],"former":["abiding-cheetah/ram/7mfk-ffff2672"],"layout":"7mfk"},{"address":"ffff2702","evidence":[{"at":"jk00c:000211d0","kind":"literal-pool","supports":"homology","to":"7mfk:000211a0","value":"ffff2702"}],"layout":"jk00c"},{"address":"ffff2716","evidence":[{"at":"jk00d:000211d0","kind":"literal-pool","supports":"homology","to":"7mfk:000211a0","value":"ffff2716"}],"layout":"jk00d"},{"address":"ffff25d0","evidence":[{"at":"jk78c:0003d410","kind":"literal-pool","note":"Pedal '
                                        'activation source is recovered from target '
                                        'consumers","supports":"homology","to":"7mfk:00039cc4","value":"ffff25d0"}],"layout":"jk78c"}],"unit":"normalized '
                                        'ADC counts"}',
                'proposed_native_sha256': '1b682b80cf4fe458c532cfdc6a998e9f86ca3043f4987d3b881f464eaa27e0ba',
                'proposed_native_json': '{"ledger":[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"coherent_snapshot/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"remarkable-lynx/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"accelerator_pedal_pair_selector/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2],"notes":[0],"order":216,"registry":"vars"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"coherent_snapshot/fn","type":"reader"},{"evidence":[{"at":"7mfk:00047aaa","key":"pedal-snapshot-high-state-access-v1:jk08a:retained-2672-pedal-consumer","kind":"indirect","mode":"pedal-snapshot-high-state-access","note":"Exact '
                                        'existing coherent history and complete pedal-state consumer with '
                                        'continuous actual RAM, independent physical/CPU/numerical checks '
                                        'and held-other source alternatives; all native facts and TEST '
                                        'positions remain '
                                        'fixed.","path":"defs/JK08A.pedal-snapshot-high-state-claims.toml","supports":"identity","value":{"actual_output":{"address":4294911082,"mask":128,"width_bytes":1},"complete_RAM_calibration_bound_continuity":true,"component":"pedal_snapshot_high_state_paths","consumer_entry":293462,"consumer_reads":[{"address":4294911598,"site":293546,"width_bytes":2},{"address":4294911598,"site":293780,"width_bytes":2}],"direction":"reader","existing_snapshot_entry_conditions_retained":true,"function":"7mfk:00047a56","hardware_qualification":false,"native_address":4294911602,"native_geometry_inference":false,"natural_caller_reachability":false,"natural_scheduling_inference":false,"original_claim_sha256":"93ee923889e9a6cf710b7da182de3b6da80f76d3a1d5d127fdab38b28d38de5a","owner":"pedal/ram","producer_entry":135076,"producer_parent":134654,"producer_store":{"address":4294911598,"site":135108,"width_bytes":2},"scale_admission":false,"scope":"exact-existing-prefix-pedal-state-quantity","source_read":{"address":4294911602,"site":135104,"width_bytes":2},"units_admission":false,"width_bytes":2}}],"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"remarkable-lynx/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","reverse_relies":"structure","reverse_supports":"identity","supports":"identity","to":"accelerator_pedal_pair_selector/fn","type":"writer"}],"note":["This '
                                        'internal normalized count is not either individual sensor '
                                        'voltage."],"summary":"Current normalized dual-channel '
                                        'accelerator-pedal quantity. FUN 0006ec68 clamps two adjusted analog '
                                        'channels, selects their minimum with mode handling, optionally '
                                        'rate-limits it, and writes this word; scheduler 00020dfe snapshots '
                                        'it to '
                                        'ffff266e.","symbol":[{"address":"fffe96a0","evidence":[{"at":"1me3b:00020b30","kind":"l0","note":"Pedal '
                                        'activation source is recovered from target '
                                        'consumers","supports":"homology","to":"7mfk:ffff2672"}],"layout":"1me3b"},{"address":"fffe96c8","evidence":[{"at":"1nd:00020b12","kind":"l0","note":"Pedal '
                                        'activation source is recovered from target '
                                        'consumers","supports":"homology","to":"7mfk:ffff2672"}],"layout":"1nd"},{"address":"ffff2672","evidence":[{"at":"7mfk:00020fc0","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00020dfe","00047a56","0006ec68","ffff2672"],"span":1}},{"at":"7mfk:00020fc4","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00020dfe","00047a56","0006ec68","ffff2672"],"span":1}},{"at":"7mfk:0006ed6e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00020dfe","00047a56","0006ec68","ffff2672"],"span":1}}],"former":["abiding-cheetah/ram/7mfk-ffff2672"],"layout":"7mfk"},{"address":"ffff2702","evidence":[{"at":"jk00c:000211d0","kind":"literal-pool","supports":"homology","to":"7mfk:000211a0","value":"ffff2702"}],"layout":"jk00c"},{"address":"ffff2716","evidence":[{"at":"jk00d:000211d0","kind":"literal-pool","supports":"homology","to":"7mfk:000211a0","value":"ffff2716"}],"layout":"jk00d"},{"address":"ffff25d0","evidence":[{"at":"jk78c:0003d410","kind":"literal-pool","note":"Pedal '
                                        'activation source is recovered from target '
                                        'consumers","supports":"homology","to":"7mfk:00039cc4","value":"ffff25d0"}],"layout":"jk78c"}],"unit":"normalized '
                                        'ADC counts"}',
                'original_ledger_json': '[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"coherent_snapshot/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"remarkable-lynx/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"accelerator_pedal_pair_selector/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2],"notes":[0],"order":216,"registry":"vars"}]',
                'proposed_ledger_json': '[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"coherent_snapshot/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"remarkable-lynx/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"accelerator_pedal_pair_selector/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2],"notes":[0],"order":216,"registry":"vars"}]',
                'original_symbol_evidence_json': '[{"at":"7mfk:00020fc0","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00020dfe","00047a56","0006ec68","ffff2672"],"span":1}},{"at":"7mfk:00020fc4","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00020dfe","00047a56","0006ec68","ffff2672"],"span":1}},{"at":"7mfk:0006ed6e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00020dfe","00047a56","0006ec68","ffff2672"],"span":1}}]',
                'evidence_json': '{"at":"7mfk:00047aaa","key":"pedal-snapshot-high-state-access-v1:jk08a:retained-2672-pedal-consumer","kind":"indirect","mode":"pedal-snapshot-high-state-access","note":"Exact '
                                 'existing coherent history and complete pedal-state consumer with '
                                 'continuous actual RAM, independent physical/CPU/numerical checks and '
                                 'held-other source alternatives; all native facts and TEST positions remain '
                                 'fixed.","path":"defs/JK08A.pedal-snapshot-high-state-claims.toml","supports":"identity","value":{"actual_output":{"address":4294911082,"mask":128,"width_bytes":1},"complete_RAM_calibration_bound_continuity":true,"component":"pedal_snapshot_high_state_paths","consumer_entry":293462,"consumer_reads":[{"address":4294911598,"site":293546,"width_bytes":2},{"address":4294911598,"site":293780,"width_bytes":2}],"direction":"reader","existing_snapshot_entry_conditions_retained":true,"function":"7mfk:00047a56","hardware_qualification":false,"native_address":4294911602,"native_geometry_inference":false,"natural_caller_reachability":false,"natural_scheduling_inference":false,"original_claim_sha256":"93ee923889e9a6cf710b7da182de3b6da80f76d3a1d5d127fdab38b28d38de5a","owner":"pedal/ram","producer_entry":135076,"producer_parent":134654,"producer_store":{"address":4294911598,"site":135108,"width_bytes":2},"scale_admission":false,"scope":"exact-existing-prefix-pedal-state-quantity","source_read":{"address":4294911602,"site":135104,"width_bytes":2},"units_admission":false,"width_bytes":2}}'}],
 'retained_functions': [{'address': 293462,
                         'owner': 'remarkable-lynx/fn',
                         'source': 'kb/fn/remarkable-lynx.toml',
                         'native_sha256': '510a346535abe15a96e267dc439cc549115448c943212bb4b1c7b55465d2933c',
                         'native_json': '{"block":"pedal/block","ledger":[{"dependency":[{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"aloof-swine/tbl","type":"reader"},{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"capable-cassowary/ram","type":"reader"},{"end":"owner","relies":"structure","role":"selector","supports":"identity","to":"merciful-lionfish/ram","type":"selector"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"mini-kiwi/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7,8,9,10],"notes":[0],"order":141,"registry":"funcs"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"merciful-lionfish/ram","type":"selector"}],"note":["Scheduler '
                                        '00020dfe copies ffff246a to ffff246d once per cycle, closing '
                                        'activation/release hysteresis. The input producer traces to A/D '
                                        'channels AN10 and AN17. Exact diagnostic bindings identify the '
                                        'paired analog subsystem as accelerator-pedal sensors; no '
                                        'engine-speed path reaches this '
                                        'comparison."],"role":"monitor","summary":"Accelerator-pedal '
                                        'high-state comparator. It compares normalized dual-channel sample '
                                        'ffff266e with ROM16[00008fdc]=610 when previous-cycle state '
                                        'ffff246d bit 7 is clear and with ROM16[00008fde]=528 when that '
                                        'state is set. The result is written to current state ffff246a bit '
                                        '7.","symbol":[{"address":"00047a56","evidence":[{"at":"7mfk:00047b8a","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008fdc","00020dfe","00047a56","ffff246a","ffff246d","ffff266e"],"span":1}},{"at":"7mfk:00047b8e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008fdc","00020dfe","00047a56","ffff246a","ffff246d","ffff266e"],"span":1}},{"at":"7mfk:00047b94","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008fdc","00020dfe","00047a56","ffff246a","ffff246d","ffff266e"],"span":1}},{"at":"7mfk:00047b96","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00008fdc","00020dfe","00047a56","ffff246a","ffff246d","ffff266e"],"span":1}},{"at":"7mfk:00047b9a","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00008fdc","00020dfe","00047a56","ffff246a","ffff246d","ffff266e"],"span":1}},{"at":"7mfk:00047ba2","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008fdc","00020dfe","00047a56","ffff246a","ffff246d","ffff266e"],"span":1}},{"at":"7mfk:00047ba4","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008fdc","00020dfe","00047a56","ffff246a","ffff246d","ffff266e"],"span":1}},{"at":"7mfk:00047ba6","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00008fdc","00020dfe","00047a56","ffff246a","ffff246d","ffff266e"],"span":1}},{"at":"7mfk:00047bae","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008fdc","00020dfe","00047a56","ffff246a","ffff246d","ffff266e"],"span":1}},{"at":"7mfk:00047bb2","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008fdc","00020dfe","00047a56","ffff246a","ffff246d","ffff266e"],"span":1}},{"kind":"trace","relies":"structure","supports":"identity","to":"coherent_snapshot/fn/7mfk"}],"layout":"7mfk","name":"remarkable-lynx"}]}'}]}

IDENTITIES=(('retained-2672-pedal-consumer',
  4294911602,
  'pedal/ram',
  293462,
  (293546, 293780),
  'reader',
  'pedal_snapshot_high_state_paths',
  2,
  'unset',
  'unset',
  '93ee923889e9a6cf710b7da182de3b6da80f76d3a1d5d127fdab38b28d38de5a',
  '5e2608e1283fa2d3c27879a37a1243a9414331993dc488a8abdb68f62ce25ec7',
  '5ef7a8a18157e748fed23eb2e741a81a22842d3008f17a1e52358933c3e7f9af',
  '1b682b80cf4fe458c532cfdc6a998e9f86ca3043f4987d3b881f464eaa27e0ba'),)

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):raise ValueError('the quantity claim changes its exact retained native/function/type/evidence/TEST boundary')
    row=value['reference'][0];old=json.loads(row['original_claim_json']);new=json.loads(row['proposed_claim_json'])
    expected=deepcopy(old);expected['evidence'].append(item(row))
    before=json.loads(row['original_native_json']);after=deepcopy(before)
    links=[r for r in after['link'] if (r['type'],r['to'])==('reader','remarkable-lynx/fn')]
    if len(links)!=1:raise ValueError('the quantity claim loses its unique retained conditional reader')
    links[0].setdefault('evidence',[]).append(item(row))
    if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
            or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
            or not test_contract.exact(new,expected) or not test_contract.exact(after,json.loads(row['proposed_native_json']))):
        raise ValueError('the quantity claim changes more than its single exact owning append')
    return value

def item(row):return json.loads(row['evidence_json'])
def native_type(row,field):return None if row['declared_'+field]=='unset' else row['declared_'+field]
def symbol_key(row):return SymbolKey('7mfk','ram',row['address'])
def original(row,link):return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
def qualified(row,link):return test_contract.exact(canonical(link),json.loads(row['proposed_claim_json']))
def registered(item):return (item.get('mode')==MODE or item.get('path')==DESCRIPTOR or isinstance(item.get('key'),str) and item['key'].startswith(PREFIX))
def publication(link,evidence):
    return (registered(evidence) and sum(test_contract.exact(evidence,x) for x in link.evidence)==1
        and any(link.owner.key==r[2] and evidence.get('key')==PREFIX+r[0] and digest(canonical(link))==r[11] for r in IDENTITIES))
def operation(row):return dict(cmd='link',meaning=row['owner'],type='reader',to=json.loads(row['original_claim_json'])['to'],evidence=[item(row)])
def operations(ops,root):
    selected=[op for op in ops if any(registered(item) for item in op.get('evidence',()))]
    if not selected:return False
    if not test_contract.exact(selected,[operation(descriptor(root)['reference'][0])]):
        raise ValueError('the quantity attachment requires its one exact complete normal owning link operation')
    return True
def looks_like_access(link):
    return any(registered(e) for e in link.evidence) or (link.owner.key,link.type,link.to.key)==('pedal/ram','reader','remarkable-lynx/fn')
