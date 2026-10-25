"""One exact retained indexed reader and its owning identity append."""
from copy import deepcopy
from pathlib import Path
import json
import tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, plain
from kb.model import SymbolKey
DESCRIPTOR = 'defs/JK08A.channel-target-reader-claims.toml'
MODE = 'channel-target-reader-access'
PREFIX = 'channel-target-reader-access-v1:jk08a:'
DECLARED={'schema': 1,
 'id': 'jk08a-channel-target-reader-claims',
 'layout': '7mfk',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'One retained actual indexed word reader through its complete uint8-indexed natural leaf.',
 'native_function_publication': False,
 'native_geometry_publication': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'reference': [{'id': 'indexed-28be-reader',
                'address': 4294912190,
                'owner': 'throttle_target_channel_1/ram',
                'function': 831946,
                'sites': [831956],
                'direction': 'reader',
                'source': 'kb/ram/throttle_target_channel_1.toml',
                'component': 'channel_target_reader_paths',
                'width_bytes': 2,
                'declared_width': 16,
                'declared_signed': 'unset',
                'original_claim_sha256': '285cf25d5dc9e3c82ef1dd07662e419b9cf9ee2874326c2cdb4c30fda1455c73',
                'original_claim_json': '{"evidence":[],"layout":"7mfk","offset":null,"owner":"throttle_target_channel_1/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/throttle_target_channel_1.toml"],"stated":["7mfk"],"to":"throttle_target_scaler/fn","type":"reader"}',
                'proposed_claim_sha256': '400ba91413b1fdb99fbe78259eb31b06de070865a0104c3a0a23a758df80da49',
                'proposed_claim_json': '{"evidence":[{"at":"7mfk:000cb1d4","key":"channel-target-reader-access-v1:jk08a:indexed-28be-reader","kind":"indirect","mode":"channel-target-reader-access","note":"Exact '
                                       'executed complete uint8-indexed leaf reads the retained word and '
                                       'publishes its independently saturated live result; native facts and '
                                       'types remain '
                                       'fixed.","path":"defs/JK08A.channel-target-reader-claims.toml","supports":"identity","value":{"actual_read_site":831956,"actual_store_is_return_delay":true,"actual_store_site":831990,"component":"channel_target_reader_paths","direction":"reader","entry":831946,"function":"7mfk:000cb1ca","hardware_qualification":false,"index_bits":8,"index_stride":2,"native_address":4294912190,"native_array_base":4294912188,"native_geometry_inference":false,"native_output_base":4294916218,"natural_scheduling_inference":false,"original_claim_sha256":"285cf25d5dc9e3c82ef1dd07662e419b9cf9ee2874326c2cdb4c30fda1455c73","owner":"throttle_target_channel_1/ram","owner_selected_index":1,"real_return_site":831988,"scale_admission":false,"scope":"exact-uint8-indexed-channel-word-read","units_admission":false,"width_bytes":2}}],"layout":"7mfk","offset":null,"owner":"throttle_target_channel_1/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/throttle_target_channel_1.toml"],"stated":["7mfk"],"to":"throttle_target_scaler/fn","type":"reader"}',
                'original_native_sha256': 'bfbd739ae61700bc83c14d43782c100b6605b2b3dab3135a5ccbdfc34f9b2160',
                'original_native_json': '{"ledger":[{"dependency":[{"end":"owner","offset":2,"offset_text":"2","relies":"structure","role":"base","supports":"identity","to":"throttle_target_channel_0/ram","type":"base"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"throttle_target_scaler/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"channel_throttle_target_builder/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[1,2],"notes":[1],"order":718,"registry":"vars","storage_description":"raw '
                                        'target '
                                        'coordinate"}],"level":"code","link":[{"layouts":["7mfk"],"offset":2,"relies":"structure","supports":"identity","to":"throttle_target_channel_0/ram","type":"base"},{"layouts":["7mfk"],"reverse_relies":"level","reverse_supports":"identity","to":"rev_limit_throttle_cut/tbl","type":"lookup"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","to":"apricot-sidewinder/fn","type":"reader"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","to":"throttle_area_compositor/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"throttle_target_scaler/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"channel_throttle_target_builder/fn","type":"writer"}],"note":["The '
                                        'percentage is the throttle opening above the learned closed '
                                        'position of the throttle position sensor.","The words carry the '
                                        'coordinate scale of axis 000155a0, 34285/1114112 percent of '
                                        'throttle opening per count. Code channel-to-bank identity remains '
                                        'unverified."],"scale":"x*34285/1114112","summary":"Code-channel-1 '
                                        'uint16 throttle target written by 0006f48c after normal, mode, '
                                        'lower, upper, and DTC caps. It is the second element of the array '
                                        'based at '
                                        'ffff28bc.","symbol":[{"address":"fffeb80e","evidence":[{"at":"1me3b:fffeb80e","kind":"byte-identical","note":"Matched '
                                        '1ND consumer functions reference this cell at the same instruction '
                                        'ordinals","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff28be"}],"layout":"1me3b"},{"address":"fffeb6c6","evidence":[{"at":"1nd:fffeb6c6","kind":"byte-identical","note":"Homologous '
                                        'channel limiter writes channel one with a two-byte '
                                        'stride","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff28be"}],"layout":"1nd"},{"address":"ffff28be","evidence":[{"at":"7mfk:0006fd5a","kind":"l0","supports":"identity"},{"at":"7mfk:0006f668","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0006f48c","000cb1ca","ffff28bc","ffff28be"],"span":1}},{"at":"7mfk:000cb1d4","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0006f48c","000cb1ca","ffff28bc","ffff28be"],"span":1}}],"former":["mustard-coot/ram/7mfk-ffff28be"],"layout":"7mfk"},{"address":"ffff422c","evidence":[{"at":"jk00c:ffff422c","kind":"byte-identical","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff28be"}],"layout":"jk00c"},{"address":"ffff4240","evidence":[{"at":"jk00d:ffff4240","kind":"byte-identical","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff28be"}],"layout":"jk00d"},{"address":"ffff43da","evidence":[{"at":"jk78c:ffff43da","kind":"byte-identical","note":"Homologous '
                                        'channel limiter writes channel one with a two-byte '
                                        'stride","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff28be"}],"layout":"jk78c"}],"unit":"percent","width":16}',
                'proposed_native_sha256': '41865f258cc62b3f23a6b28afacbab4a98382becace3c25d02d9e9c6edd2b604',
                'proposed_native_json': '{"ledger":[{"dependency":[{"end":"owner","offset":2,"offset_text":"2","relies":"structure","role":"base","supports":"identity","to":"throttle_target_channel_0/ram","type":"base"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"throttle_target_scaler/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"channel_throttle_target_builder/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[1,2],"notes":[1],"order":718,"registry":"vars","storage_description":"raw '
                                        'target '
                                        'coordinate"}],"level":"code","link":[{"layouts":["7mfk"],"offset":2,"relies":"structure","supports":"identity","to":"throttle_target_channel_0/ram","type":"base"},{"layouts":["7mfk"],"reverse_relies":"level","reverse_supports":"identity","to":"rev_limit_throttle_cut/tbl","type":"lookup"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","to":"apricot-sidewinder/fn","type":"reader"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","to":"throttle_area_compositor/fn","type":"reader"},{"evidence":[{"at":"7mfk:000cb1d4","key":"channel-target-reader-access-v1:jk08a:indexed-28be-reader","kind":"indirect","mode":"channel-target-reader-access","note":"Exact '
                                        'executed complete uint8-indexed leaf reads the retained word and '
                                        'publishes its independently saturated live result; native facts and '
                                        'types remain '
                                        'fixed.","path":"defs/JK08A.channel-target-reader-claims.toml","supports":"identity","value":{"actual_read_site":831956,"actual_store_is_return_delay":true,"actual_store_site":831990,"component":"channel_target_reader_paths","direction":"reader","entry":831946,"function":"7mfk:000cb1ca","hardware_qualification":false,"index_bits":8,"index_stride":2,"native_address":4294912190,"native_array_base":4294912188,"native_geometry_inference":false,"native_output_base":4294916218,"natural_scheduling_inference":false,"original_claim_sha256":"285cf25d5dc9e3c82ef1dd07662e419b9cf9ee2874326c2cdb4c30fda1455c73","owner":"throttle_target_channel_1/ram","owner_selected_index":1,"real_return_site":831988,"scale_admission":false,"scope":"exact-uint8-indexed-channel-word-read","units_admission":false,"width_bytes":2}}],"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"throttle_target_scaler/fn","type":"reader"},{"evidence":[{"at":"7mfk:0006f668","key":"channel-target-builder-access-v1:jk08a:indexed-28be-writer","kind":"indirect","mode":"channel-target-builder-access","note":"Exact '
                                        'complete native index1 builder publishes its independently computed '
                                        'word through actual inverse lookups, ordered raw limits and '
                                        'fixed-record caps; all other native facts remain '
                                        'fixed.","path":"defs/JK08A.channel-target-builder-claims.toml","supports":"identity","value":{"actual_ROM_GBR":38260,"actual_array_base":4294912188,"actual_fixed_record_ids":[111,289,112,290],"actual_inverse_operands":{"axis":78338,"curve":87456},"actual_scratch_word":4294912248,"actual_store_site":456296,"actual_upper_word":4294915336,"complete_existing_reader_required_same_primary":true,"complete_natural_calls_returns_live_stores_CPU_frame_RAM_and_held_other_obligations":true,"component":"channel_target_builder_paths","direction":"writer","entry":455820,"function":"7mfk:0006f48c","hardware_qualification":false,"index_stride":2,"native_address":4294912190,"native_geometry_inference":false,"native_index_premise":{"low_byte":1,"register":4,"upper24_bits_independent":true},"natural_scheduling_inference":false,"original_claim_sha256":"16b88057bb8636545c9a5145d3be23e2d6178b964409f9e1e4f38120853a9458","owner":"throttle_target_channel_1/ram","physical_channel_to_bank_identity_admission":false,"scale_admission":false,"scope":"exact-channel-target-builder","units_admission":false,"width_bytes":2}}],"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"channel_throttle_target_builder/fn","type":"writer"}],"note":["The '
                                        'percentage is the throttle opening above the learned closed '
                                        'position of the throttle position sensor.","The words carry the '
                                        'coordinate scale of axis 000155a0, 34285/1114112 percent of '
                                        'throttle opening per count. Code channel-to-bank identity remains '
                                        'unverified."],"scale":"x*34285/1114112","summary":"Code-channel-1 '
                                        'uint16 throttle target written by 0006f48c after normal, mode, '
                                        'lower, upper, and DTC caps. It is the second element of the array '
                                        'based at '
                                        'ffff28bc.","symbol":[{"address":"fffeb80e","evidence":[{"at":"1me3b:fffeb80e","kind":"byte-identical","note":"Matched '
                                        '1ND consumer functions reference this cell at the same instruction '
                                        'ordinals","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff28be"}],"layout":"1me3b"},{"address":"fffeb6c6","evidence":[{"at":"1nd:fffeb6c6","kind":"byte-identical","note":"Homologous '
                                        'channel limiter writes channel one with a two-byte '
                                        'stride","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff28be"}],"layout":"1nd"},{"address":"ffff28be","evidence":[{"at":"7mfk:0006fd5a","kind":"l0","supports":"identity"},{"at":"7mfk:0006f668","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0006f48c","000cb1ca","ffff28bc","ffff28be"],"span":1}},{"at":"7mfk:000cb1d4","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0006f48c","000cb1ca","ffff28bc","ffff28be"],"span":1}}],"former":["mustard-coot/ram/7mfk-ffff28be"],"layout":"7mfk"},{"address":"ffff422c","evidence":[{"at":"jk00c:ffff422c","kind":"byte-identical","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff28be"}],"layout":"jk00c"},{"address":"ffff4240","evidence":[{"at":"jk00d:ffff4240","kind":"byte-identical","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff28be"}],"layout":"jk00d"},{"address":"ffff43da","evidence":[{"at":"jk78c:ffff43da","kind":"byte-identical","note":"Homologous '
                                        'channel limiter writes channel one with a two-byte '
                                        'stride","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff28be"}],"layout":"jk78c"}],"unit":"percent","width":16}',
                'original_ledger_json': '[{"dependency":[{"end":"owner","offset":2,"offset_text":"2","relies":"structure","role":"base","supports":"identity","to":"throttle_target_channel_0/ram","type":"base"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"throttle_target_scaler/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"channel_throttle_target_builder/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[1,2],"notes":[1],"order":718,"registry":"vars","storage_description":"raw '
                                        'target coordinate"}]',
                'proposed_ledger_json': '[{"dependency":[{"end":"owner","offset":2,"offset_text":"2","relies":"structure","role":"base","supports":"identity","to":"throttle_target_channel_0/ram","type":"base"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"throttle_target_scaler/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"channel_throttle_target_builder/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[1,2],"notes":[1],"order":718,"registry":"vars","storage_description":"raw '
                                        'target coordinate"}]',
                'original_symbol_evidence_json': '[{"at":"7mfk:0006fd5a","kind":"l0","supports":"identity"},{"at":"7mfk:0006f668","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0006f48c","000cb1ca","ffff28bc","ffff28be"],"span":1}},{"at":"7mfk:000cb1d4","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0006f48c","000cb1ca","ffff28bc","ffff28be"],"span":1}}]',
                'evidence_json': '{"at":"7mfk:000cb1d4","key":"channel-target-reader-access-v1:jk08a:indexed-28be-reader","kind":"indirect","mode":"channel-target-reader-access","note":"Exact '
                                 'executed complete uint8-indexed leaf reads the retained word and publishes '
                                 'its independently saturated live result; native facts and types remain '
                                 'fixed.","path":"defs/JK08A.channel-target-reader-claims.toml","supports":"identity","value":{"actual_read_site":831956,"actual_store_is_return_delay":true,"actual_store_site":831990,"component":"channel_target_reader_paths","direction":"reader","entry":831946,"function":"7mfk:000cb1ca","hardware_qualification":false,"index_bits":8,"index_stride":2,"native_address":4294912190,"native_array_base":4294912188,"native_geometry_inference":false,"native_output_base":4294916218,"natural_scheduling_inference":false,"original_claim_sha256":"285cf25d5dc9e3c82ef1dd07662e419b9cf9ee2874326c2cdb4c30fda1455c73","owner":"throttle_target_channel_1/ram","owner_selected_index":1,"real_return_site":831988,"scale_admission":false,"scope":"exact-uint8-indexed-channel-word-read","units_admission":false,"width_bytes":2}}'}],
 'retained_functions': [{'owner': 'throttle_target_scaler/fn',
                         'address': 831946,
                         'source': 'kb/fn/throttle_target_scaler.toml',
                         'native_json': '{"block":"throttle_servo/block","ledger":[{"fields":["name"],"order":157,"registry":"curated","title":true},{"dependency":[{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"throttle_target_channel_0/ram","type":"reader"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"polar-mastiff/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3],"notes":[0],"order":577,"registry":"funcs"}],"level":"code","note":["This '
                                        'is the exact bridge from channel target coordinates into the '
                                        'feedback-regulator domain."],"role":"driver","summary":"Per-channel '
                                        'target scaler. It writes sat_u16((ffff28bc+2*channel)*16+0x2000) to '
                                        'ffff387a/ffff387c.","symbol":[{"address":"000cb1ca","evidence":[{"at":"7mfk:000cb1d4","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000cb1ca","ffff28bc","ffff387a"],"span":1}},{"at":"7mfk:000cb1dc","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000cb1ca","ffff28bc","ffff387a"],"span":1}},{"at":"7mfk:000cb1e8","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000cb1ca","ffff28bc","ffff387a"],"span":1}},{"at":"7mfk:000cb1f4","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000cb1ca","ffff28bc","ffff387a"],"span":1}}],"layout":"7mfk"}],"title":"Scale '
                                        'one channel target into the regulator domain"}',
                         'native_sha256': '488d08c4c449345dfc0ffd36d3989687ac9830ad6cce522b2c85125d146b4316'}],
 'companion': {'id': 'indexed-28be-writer',
               'owner': 'throttle_target_channel_1/ram',
               'component': 'channel_target_builder_paths',
               'direction': 'writer',
               'function': 455820,
               'original_claim_sha256': '16b88057bb8636545c9a5145d3be23e2d6178b964409f9e1e4f38120853a9458',
               'original_claim_json': '{"evidence":[],"layout":"7mfk","offset":null,"owner":"throttle_target_channel_1/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/throttle_target_channel_1.toml"],"stated":["7mfk"],"to":"channel_throttle_target_builder/fn","type":"writer"}',
               'proposed_claim_sha256': 'aadbb54e399509647f9abcb294ddfad55727bb1435b202782d44ebb3d923df2f',
               'proposed_claim_json': '{"evidence":[{"at":"7mfk:0006f668","key":"channel-target-builder-access-v1:jk08a:indexed-28be-writer","kind":"indirect","mode":"channel-target-builder-access","note":"Exact '
                                      'complete native index1 builder publishes its independently computed '
                                      'word through actual inverse lookups, ordered raw limits and '
                                      'fixed-record caps; all other native facts remain '
                                      'fixed.","path":"defs/JK08A.channel-target-builder-claims.toml","supports":"identity","value":{"actual_ROM_GBR":38260,"actual_array_base":4294912188,"actual_fixed_record_ids":[111,289,112,290],"actual_inverse_operands":{"axis":78338,"curve":87456},"actual_scratch_word":4294912248,"actual_store_site":456296,"actual_upper_word":4294915336,"complete_existing_reader_required_same_primary":true,"complete_natural_calls_returns_live_stores_CPU_frame_RAM_and_held_other_obligations":true,"component":"channel_target_builder_paths","direction":"writer","entry":455820,"function":"7mfk:0006f48c","hardware_qualification":false,"index_stride":2,"native_address":4294912190,"native_geometry_inference":false,"native_index_premise":{"low_byte":1,"register":4,"upper24_bits_independent":true},"natural_scheduling_inference":false,"original_claim_sha256":"16b88057bb8636545c9a5145d3be23e2d6178b964409f9e1e4f38120853a9458","owner":"throttle_target_channel_1/ram","physical_channel_to_bank_identity_admission":false,"scale_admission":false,"scope":"exact-channel-target-builder","units_admission":false,"width_bytes":2}}],"layout":"7mfk","offset":null,"owner":"throttle_target_channel_1/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/throttle_target_channel_1.toml"],"stated":["7mfk"],"to":"channel_throttle_target_builder/fn","type":"writer"}',
               'evidence_json': '{"at":"7mfk:0006f668","key":"channel-target-builder-access-v1:jk08a:indexed-28be-writer","kind":"indirect","mode":"channel-target-builder-access","note":"Exact '
                                'complete native index1 builder publishes its independently computed word '
                                'through actual inverse lookups, ordered raw limits and fixed-record caps; '
                                'all other native facts remain '
                                'fixed.","path":"defs/JK08A.channel-target-builder-claims.toml","supports":"identity","value":{"actual_ROM_GBR":38260,"actual_array_base":4294912188,"actual_fixed_record_ids":[111,289,112,290],"actual_inverse_operands":{"axis":78338,"curve":87456},"actual_scratch_word":4294912248,"actual_store_site":456296,"actual_upper_word":4294915336,"complete_existing_reader_required_same_primary":true,"complete_natural_calls_returns_live_stores_CPU_frame_RAM_and_held_other_obligations":true,"component":"channel_target_builder_paths","direction":"writer","entry":455820,"function":"7mfk:0006f48c","hardware_qualification":false,"index_stride":2,"native_address":4294912190,"native_geometry_inference":false,"native_index_premise":{"low_byte":1,"register":4,"upper24_bits_independent":true},"natural_scheduling_inference":false,"original_claim_sha256":"16b88057bb8636545c9a5145d3be23e2d6178b964409f9e1e4f38120853a9458","owner":"throttle_target_channel_1/ram","physical_channel_to_bank_identity_admission":false,"scale_admission":false,"scope":"exact-channel-target-builder","units_admission":false,"width_bytes":2}}'}}
IDENTITIES=(('indexed-28be-reader',
  4294912190,
  'throttle_target_channel_1/ram',
  831946,
  (831956,),
  'reader',
  'channel_target_reader_paths',
  2,
  16,
  'unset',
  '285cf25d5dc9e3c82ef1dd07662e419b9cf9ee2874326c2cdb4c30fda1455c73',
  '400ba91413b1fdb99fbe78259eb31b06de070865a0104c3a0a23a758df80da49',
  'bfbd739ae61700bc83c14d43782c100b6605b2b3dab3135a5ccbdfc34f9b2160',
  '41865f258cc62b3f23a6b28afacbab4a98382becace3c25d02d9e9c6edd2b604'),)

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):
        raise ValueError('the indexed reader changes an exact retained owner, function, claim or finite companion')
    row=value['reference'][0];companion=value['companion']
    old=json.loads(row['original_claim_json']);new=json.loads(row['proposed_claim_json'])
    expected=deepcopy(old);expected['evidence'].append(item(row))
    companion_old=json.loads(companion['original_claim_json'])
    companion_new=json.loads(companion['proposed_claim_json'])
    companion_expected=deepcopy(companion_old)
    companion_expected['evidence'].append(item(companion))
    if ((companion['owner'],companion['direction'],companion['function'],companion['component'])!=
            ('throttle_target_channel_1/ram','writer',0x6F48C,'channel_target_builder_paths')
            or digest(companion_old)!=companion['original_claim_sha256']
            or digest(companion_new)!=companion['proposed_claim_sha256']
            or not test_contract.exact(companion_new,companion_expected)):
        raise ValueError('the indexed reader changes its one exact writer companion')
    before=json.loads(row['original_native_json']);after=deepcopy(before)
    for direction,target,evidence in (('reader','throttle_target_scaler/fn',item(row)),
                                      ('writer','channel_throttle_target_builder/fn',item(companion))):
        links=[link for link in after['link'] if (link['type'],link['to'])==(direction,target)]
        if len(links)!=1:
            raise ValueError('the indexed reader loses a unique retained shared-owner relation')
        links[0].setdefault('evidence',[]).append(evidence)
    if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
            or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
            or not test_contract.exact(new,expected) or not test_contract.exact(after,json.loads(row['proposed_native_json']))):
        raise ValueError('the indexed reader changes more than the two exact finite owner evidence appends')
    return value

def item(row):return json.loads(row['evidence_json'])
def native_type(row,field):return None if row['declared_'+field]=='unset' else row['declared_'+field]
def symbol_key(row):return SymbolKey('7mfk','ram',row['address'])
def original(row,link):return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
def qualified(row,link):return test_contract.exact(canonical(link),json.loads(row['proposed_claim_json']))
def registered(evidence):return (evidence.get('mode')==MODE or evidence.get('path')==DESCRIPTOR or isinstance(evidence.get('key'),str) and evidence['key'].startswith(PREFIX))
def publication(link,evidence):
    return (registered(evidence) and sum(test_contract.exact(evidence,value) for value in link.evidence)==1
        and any(link.owner.key==row[2] and evidence.get('key')==PREFIX+row[0] and digest(canonical(link))==row[11] for row in IDENTITIES))
def operation(row):
    old=json.loads(row['original_claim_json'])
    return dict(cmd='link',meaning=row['owner'],type=old['type'],to=old['to'],evidence=[item(row)])
def companion_operation(root):return operation(descriptor(root)['companion'])
def operations(ops,root):
    selected=[op for op in ops if any(registered(value) for value in op.get('evidence',()))]
    if not selected:return False
    value=descriptor(root);companion=operation(value['companion'])
    companion_evidence=item(value['companion'])
    peers=[op for op in ops if any(test_contract.exact(value,companion_evidence) for value in op.get('evidence',()))]
    if not test_contract.exact(selected,[operation(value['reference'][0])]) or not test_contract.exact(peers,[companion]):
        raise ValueError('the indexed reader attachment requires its exact operation and the one known writer companion')
    return True
def looks_like_access(link):
    return any(registered(value) for value in link.evidence) or (link.owner.key,link.type,link.to.key)==('throttle_target_channel_1/ram','reader','throttle_target_scaler/fn')
