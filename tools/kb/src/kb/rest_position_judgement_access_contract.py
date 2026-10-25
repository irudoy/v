"""One exact retained native bank1 byte judgement quantity relation and complete owning append."""
from copy import deepcopy
from pathlib import Path
import json,tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,plain
from kb.model import SymbolKey
DESCRIPTOR='defs/JK08A.rest-position-judgement-claims.toml'
MODE='rest-position-judgement-access'
PREFIX='rest-position-judgement-access-v1:jk08a:'
DECLARED={'schema': 1,
 'id': 'jk08a-rest-position-judgement-claims',
 'layout': '7mfk',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'One retained complete native-bank1 RAM byte reader; no other-bank, physical-unit or '
          'source-producer inference.',
 'native_function_publication': False,
 'native_geometry_publication': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'reference': [{'id': 'retained-ffff16bb-consumer',
                'address': 4294907579,
                'owner': 'benevolent-rat/ram',
                'function': 590422,
                'sites': [590604, 590762],
                'direction': 'reader',
                'source': 'kb/ram/benevolent-rat.toml',
                'component': 'rest_position_judgement_paths',
                'width_bytes': 1,
                'declared_width': 'unset',
                'declared_signed': 'unset',
                'original_claim_sha256': '57bca775fc10e8bc38acbca98a6abd80b96634369755e7f4aa942f884ea2eab7',
                'original_claim_json': '{"evidence":[],"layout":"7mfk","offset":null,"owner":"benevolent-rat/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/benevolent-rat.toml"],"stated":["7mfk"],"to":"apricot-echidna/fn","type":"reader"}',
                'proposed_claim_sha256': 'c795909b355ef4c580190d913aaeeb25b7c14d15154ca42032e5c55e5eec3f3d',
                'proposed_claim_json': '{"evidence":[{"at":"7mfk:0009030c","key":"rest-position-judgement-access-v1:jk08a:retained-ffff16bb-consumer","kind":"indirect","mode":"rest-position-judgement-access","note":"Exact '
                                       'complete bank-index1 measured-byte judgement and actual fault '
                                       'publications; full native owner/function facts and semantic types '
                                       'remain '
                                       'fixed.","path":"defs/JK08A.rest-position-judgement-claims.toml","supports":"identity","value":{"actual_fault_publications":[{"address":4294915467,"sites":[590656,590812],"width_bytes":1},{"address":4294915458,"sites":[590684,590910],"width_bytes":1}],"actual_permits_counters_threshold_equalities_and_four_timer_gates":true,"actual_reads":[{"address":4294907579,"site":590604,"width_bytes":1},{"address":4294907579,"site":590762,"width_bytes":1}],"complete_CPU_SR_GBR_PR_SP_ABI_frame_RAM_and_bound_obligations":true,"component":"rest_position_judgement_paths","direction":"reader","entry":590422,"function":"7mfk:00090256","hardware_qualification":false,"native_address":4294907579,"native_bank_general_identity_admission":false,"native_geometry_inference":false,"native_index_premise":{"complete_raw_value":1,"register":4},"natural_scheduling_inference":false,"original_claim_sha256":"57bca775fc10e8bc38acbca98a6abd80b96634369755e7f4aa942f884ea2eab7","owner":"benevolent-rat/ram","scale_admission":false,"scope":"exact-rest-position-judgement","units_admission":false,"width_bytes":1}}],"layout":"7mfk","offset":null,"owner":"benevolent-rat/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/benevolent-rat.toml"],"stated":["7mfk"],"to":"apricot-echidna/fn","type":"reader"}',
                'original_native_sha256': 'beef95754e1936857c11741ec340847ad7988e2197ec31e829da29c56a967bda',
                'original_native_json': '{"ledger":[{"dependency":[{"end":"owner","offset":1071,"offset_text":"1071","relies":"structure","role":"base","supports":"identity","to":"outstanding-marmot/ram","type":"base"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"apricot-echidna/fn","type":"reader"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"exhaust_cvtc_target/ram","type":"input"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"fat-dogfish/ram","type":"input"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"paper-hippo/fn","type":"writer"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"unselfish-hawk/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4],"notes":[0],"order":778,"registry":"vars"}],"level":"code","link":[{"layouts":["7mfk"],"offset":1071,"relies":"structure","supports":"identity","to":"outstanding-marmot/ram","type":"base"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"exhaust_cvtc_target/ram","type":"input"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"fat-dogfish/ram","type":"input"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"apricot-echidna/fn","type":"reader"},{"layouts":["7mfk"],"relies":"level","supports":"identity","to":"paper-hippo/fn","type":"writer"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"unselfish-hawk/fn","type":"writer"}],"note":["Source '
                                        'byte ffff11c9 has no direct writer in the export; its physical '
                                        'meaning is unresolved."],"summary":"Bank-2 exhaust-VTC '
                                        'rest-position byte. FUN 0008f168 writes '
                                        'clamp_u8(ffff11c9-ROM8[0000831e]+128) at 0008f524; FUN 00090256 '
                                        'reads it with bank index 1 for the P0024 rest-position judgement. '
                                        'Initializer FUN 0007f30c writes its reset '
                                        'value.","symbol":[{"address":"ffff16bb","evidence":[{"kind":"unbound-constant","supports":"identity","value":"0000831e=88"},{"kind":"unbound-constant","supports":"identity","value":"00008951=34"},{"kind":"unbound-constant","supports":"identity","value":"00008952=34"},{"at":"7mfk:0008f524","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000831e","00008951","00008952","0007f30c","0008f168","00090256","ffff11c9","ffff128c","ffff16bb","ffff2327"],"span":1}},{"at":"7mfk:0009030c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000831e","00008951","00008952","0007f30c","0008f168","00090256","ffff11c9","ffff128c","ffff16bb","ffff2327"],"span":1}}],"layout":"7mfk","name":"benevolent-rat"}],"unit":"centered_u8"}',
                'proposed_native_sha256': 'add8c4871504dcafbcab021047ab253da2750caa7da71a25741df26039fe79f5',
                'proposed_native_json': '{"ledger":[{"dependency":[{"end":"owner","offset":1071,"offset_text":"1071","relies":"structure","role":"base","supports":"identity","to":"outstanding-marmot/ram","type":"base"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"apricot-echidna/fn","type":"reader"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"exhaust_cvtc_target/ram","type":"input"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"fat-dogfish/ram","type":"input"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"paper-hippo/fn","type":"writer"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"unselfish-hawk/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4],"notes":[0],"order":778,"registry":"vars"}],"level":"code","link":[{"layouts":["7mfk"],"offset":1071,"relies":"structure","supports":"identity","to":"outstanding-marmot/ram","type":"base"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"exhaust_cvtc_target/ram","type":"input"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"fat-dogfish/ram","type":"input"},{"evidence":[{"at":"7mfk:0009030c","key":"rest-position-judgement-access-v1:jk08a:retained-ffff16bb-consumer","kind":"indirect","mode":"rest-position-judgement-access","note":"Exact '
                                        'complete bank-index1 measured-byte judgement and actual fault '
                                        'publications; full native owner/function facts and semantic types '
                                        'remain '
                                        'fixed.","path":"defs/JK08A.rest-position-judgement-claims.toml","supports":"identity","value":{"actual_fault_publications":[{"address":4294915467,"sites":[590656,590812],"width_bytes":1},{"address":4294915458,"sites":[590684,590910],"width_bytes":1}],"actual_permits_counters_threshold_equalities_and_four_timer_gates":true,"actual_reads":[{"address":4294907579,"site":590604,"width_bytes":1},{"address":4294907579,"site":590762,"width_bytes":1}],"complete_CPU_SR_GBR_PR_SP_ABI_frame_RAM_and_bound_obligations":true,"component":"rest_position_judgement_paths","direction":"reader","entry":590422,"function":"7mfk:00090256","hardware_qualification":false,"native_address":4294907579,"native_bank_general_identity_admission":false,"native_geometry_inference":false,"native_index_premise":{"complete_raw_value":1,"register":4},"natural_scheduling_inference":false,"original_claim_sha256":"57bca775fc10e8bc38acbca98a6abd80b96634369755e7f4aa942f884ea2eab7","owner":"benevolent-rat/ram","scale_admission":false,"scope":"exact-rest-position-judgement","units_admission":false,"width_bytes":1}}],"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"apricot-echidna/fn","type":"reader"},{"layouts":["7mfk"],"relies":"level","supports":"identity","to":"paper-hippo/fn","type":"writer"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"unselfish-hawk/fn","type":"writer"}],"note":["Source '
                                        'byte ffff11c9 has no direct writer in the export; its physical '
                                        'meaning is unresolved."],"summary":"Bank-2 exhaust-VTC '
                                        'rest-position byte. FUN 0008f168 writes '
                                        'clamp_u8(ffff11c9-ROM8[0000831e]+128) at 0008f524; FUN 00090256 '
                                        'reads it with bank index 1 for the P0024 rest-position judgement. '
                                        'Initializer FUN 0007f30c writes its reset '
                                        'value.","symbol":[{"address":"ffff16bb","evidence":[{"kind":"unbound-constant","supports":"identity","value":"0000831e=88"},{"kind":"unbound-constant","supports":"identity","value":"00008951=34"},{"kind":"unbound-constant","supports":"identity","value":"00008952=34"},{"at":"7mfk:0008f524","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000831e","00008951","00008952","0007f30c","0008f168","00090256","ffff11c9","ffff128c","ffff16bb","ffff2327"],"span":1}},{"at":"7mfk:0009030c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000831e","00008951","00008952","0007f30c","0008f168","00090256","ffff11c9","ffff128c","ffff16bb","ffff2327"],"span":1}}],"layout":"7mfk","name":"benevolent-rat"}],"unit":"centered_u8"}',
                'original_ledger_json': '[{"dependency":[{"end":"owner","offset":1071,"offset_text":"1071","relies":"structure","role":"base","supports":"identity","to":"outstanding-marmot/ram","type":"base"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"apricot-echidna/fn","type":"reader"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"exhaust_cvtc_target/ram","type":"input"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"fat-dogfish/ram","type":"input"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"paper-hippo/fn","type":"writer"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"unselfish-hawk/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4],"notes":[0],"order":778,"registry":"vars"}]',
                'proposed_ledger_json': '[{"dependency":[{"end":"owner","offset":1071,"offset_text":"1071","relies":"structure","role":"base","supports":"identity","to":"outstanding-marmot/ram","type":"base"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"apricot-echidna/fn","type":"reader"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"exhaust_cvtc_target/ram","type":"input"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"fat-dogfish/ram","type":"input"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"paper-hippo/fn","type":"writer"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"unselfish-hawk/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4],"notes":[0],"order":778,"registry":"vars"}]',
                'original_symbol_evidence_json': '[{"kind":"unbound-constant","supports":"identity","value":"0000831e=88"},{"kind":"unbound-constant","supports":"identity","value":"00008951=34"},{"kind":"unbound-constant","supports":"identity","value":"00008952=34"},{"at":"7mfk:0008f524","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000831e","00008951","00008952","0007f30c","0008f168","00090256","ffff11c9","ffff128c","ffff16bb","ffff2327"],"span":1}},{"at":"7mfk:0009030c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000831e","00008951","00008952","0007f30c","0008f168","00090256","ffff11c9","ffff128c","ffff16bb","ffff2327"],"span":1}}]',
                'evidence_json': '{"at":"7mfk:0009030c","key":"rest-position-judgement-access-v1:jk08a:retained-ffff16bb-consumer","kind":"indirect","mode":"rest-position-judgement-access","note":"Exact '
                                 'complete bank-index1 measured-byte judgement and actual fault '
                                 'publications; full native owner/function facts and semantic types remain '
                                 'fixed.","path":"defs/JK08A.rest-position-judgement-claims.toml","supports":"identity","value":{"actual_fault_publications":[{"address":4294915467,"sites":[590656,590812],"width_bytes":1},{"address":4294915458,"sites":[590684,590910],"width_bytes":1}],"actual_permits_counters_threshold_equalities_and_four_timer_gates":true,"actual_reads":[{"address":4294907579,"site":590604,"width_bytes":1},{"address":4294907579,"site":590762,"width_bytes":1}],"complete_CPU_SR_GBR_PR_SP_ABI_frame_RAM_and_bound_obligations":true,"component":"rest_position_judgement_paths","direction":"reader","entry":590422,"function":"7mfk:00090256","hardware_qualification":false,"native_address":4294907579,"native_bank_general_identity_admission":false,"native_geometry_inference":false,"native_index_premise":{"complete_raw_value":1,"register":4},"natural_scheduling_inference":false,"original_claim_sha256":"57bca775fc10e8bc38acbca98a6abd80b96634369755e7f4aa942f884ea2eab7","owner":"benevolent-rat/ram","scale_admission":false,"scope":"exact-rest-position-judgement","units_admission":false,"width_bytes":1}}'}],
 'retained_functions': [{'owner': 'apricot-echidna/fn',
                         'address': 590422,
                         'source': 'kb/fn/apricot-echidna.toml',
                         'native_json': '{"symbol":[{"address":"00090256","evidence":[{"at":"7mfk:00090256","kind":"l0","supports":"identity"}],"layout":"7mfk","name":"apricot-echidna"}]}',
                         'native_sha256': '34e01fd7ad033e166b7527f7d598d7cc032e79b1a533fa122eb85f39b5b8acd3'}]}
IDENTITIES=(('retained-ffff16bb-consumer',
  4294907579,
  'benevolent-rat/ram',
  590422,
  (590604, 590762),
  'reader',
  'rest_position_judgement_paths',
  1,
  'unset',
  'unset',
  '57bca775fc10e8bc38acbca98a6abd80b96634369755e7f4aa942f884ea2eab7',
  'c795909b355ef4c580190d913aaeeb25b7c14d15154ca42032e5c55e5eec3f3d',
  'beef95754e1936857c11741ec340847ad7988e2197ec31e829da29c56a967bda',
  'add8c4871504dcafbcab021047ab253da2750caa7da71a25741df26039fe79f5'),)
def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):raise ValueError('the quantity claim changes its exact retained native/function/type/evidence/TEST boundary')
    row=value['reference'][0];old=json.loads(row['original_claim_json']);new=json.loads(row['proposed_claim_json'])
    expected=deepcopy(old);expected['evidence'].append(item(row))
    before=json.loads(row['original_native_json']);after=deepcopy(before)
    links=[r for r in after['link'] if (r['type'],r['to'])==('reader','apricot-echidna/fn')]
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
    return any(registered(e) for e in link.evidence) or (link.owner.key,link.type,link.to.key)==('benevolent-rat/ram','reader','apricot-echidna/fn')
