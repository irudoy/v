"""One exact retained bank1 third-trim writer identity and complete native preservation."""
from copy import deepcopy
from pathlib import Path
import json,tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,plain
from kb.model import SymbolKey
DESCRIPTOR='defs/JK08A.third-trim-word-writer-claims.toml'
MODE='third-trim-word-writer-access'
PREFIX='third-trim-word-writer-access-v1:jk08a:'
DECLARED={'schema': 1,
 'id': 'jk08a-third-trim-word-writer-claims',
 'layout': '7mfk',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'One exact bank1/channel0 writer identity from complete5B534; all raw channel footprints preserve '
          'native width16, absent producer signedness, units, typed reader and other owner/function facts.',
 'native_function_publication': False,
 'native_geometry_publication': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_caller_reachability': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'reference': [{'id': 'retained-bank1-2a24-complete-writer',
                'address': 4294912548,
                'owner': 'astonishing-hoatzin/ram',
                'function': 374068,
                'sites': [374512],
                'direction': 'writer',
                'source': 'kb/ram/astonishing-hoatzin.toml',
                'component': 'third_trim_word_writer_paths',
                'width_bytes': 2,
                'declared_width': 16,
                'declared_signed': 'unset',
                'original_claim_sha256': '058492927bab2006d7003566c42d6b3afdd9d72a78f5fb8070f12848fff98780',
                'original_claim_json': '{"evidence":[],"layout":"7mfk","offset":null,"owner":"astonishing-hoatzin/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/astonishing-hoatzin.toml"],"stated":["7mfk"],"to":"true-quokka/fn","type":"writer"}',
                'proposed_claim_sha256': 'e628d065a7505f3cfd129a176daecf5b0a2798cf4d032b369bb585022356362f',
                'proposed_claim_json': '{"evidence":[{"at":"7mfk:0005b6f0","key":"third-trim-word-writer-access-v1:jk08a:retained-bank1-2a24-complete-writer","kind":"indirect","mode":"third-trim-word-writer-access","note":"Complete '
                                       'stock leaf execution binds the exact bank1 channel-zero word writer '
                                       'and actual full R2 store. All raw channels, signed32 accumulator '
                                       'paths and conditional shared-bank effects remain observed. Full '
                                       'native owner/function facts, storage width16, absent producer '
                                       'signedness, unit percent*256, typed reader, other writers and TEST '
                                       'positions stay '
                                       'fixed.","path":"defs/JK08A.third-trim-word-writer-claims.toml","supports":"identity","value":{"actual_accumulator":{"base":4294914832,"full_signed32":true,"neutral":25600,"read_site":374416,"stride":4,"width_bytes":4,"write_sites":[374456,374484]},"actual_indexed_write":{"base":4294912548,"register":2,"site":374512,"stride":2,"width_bytes":2},"actual_mask":"channel+1","actual_shared_write":{"address":4294912550,"copy_site":374514,"mode_ROM":35626,"mode_bit":2,"register":0,"site":374516,"width_bytes":2},"all_other_writers_and_native_TEST_positions_preserved":true,"causal_bank1_prior_word_and_accumulator_alternatives":true,"complete_natural_entry_RAM_frame_CPU":true,"component":"third_trim_word_writer_paths","direction":"writer","discarded_channel_high24_full_state_invariance":true,"entry":374068,"existing_unit":"percent*256","full_R2_not_only_low16_required":true,"function":"7mfk:0005b534","hardware_qualification":false,"identity_channel":0,"independent_ordinary_shared_sibling_modes":true,"native_address":4294912548,"native_geometry_inference":false,"native_producer_signedness":"unset","native_storage_width":16,"natural_caller_reachability":false,"natural_scheduling_inference":false,"no_other_channel_semantic_owner_inference":true,"no_stock_calls":true,"original_claim_sha256":"058492927bab2006d7003566c42d6b3afdd9d72a78f5fb8070f12848fff98780","owner":"astonishing-hoatzin/ram","raw_channel_from_full_R4_low8":true,"raw_channel_values":256,"scale_admission":false,"scope":"exact-bank1-third-trim-word-writer","typed_reader":"bank_base_pulse_builder/fn","units_admission":false,"width_bytes":2}}],"layout":"7mfk","offset":null,"owner":"astonishing-hoatzin/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/astonishing-hoatzin.toml"],"stated":["7mfk"],"to":"true-quokka/fn","type":"writer"}',
                'original_native_sha256': 'a5f765469581e39f17e656027d41d8e55d5664ba1c5c27ca9446c012fe3ae193',
                'original_native_json': '{"ledger":[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"bank_base_pulse_builder/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"dexterous-yak/fn","type":"writer"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"startup_initializer/fn","type":"writer"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"true-quokka/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5,6,7],"notes":[0],"order":908,"registry":"vars"}],"level":"code","link":[{"evidence":[{"at":"7mfk:0004eaf0","kind":"l0"},{"key":"test_bank_base_pulse_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_bank_base_pulse_chain.py"},{"key":"test_bank_base_pulse_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_bank_base_pulse_chain.py"},{"key":"Bounded '
                                        'bank base-pulse '
                                        'builder","kind":"spec","path":"defs/JK08A.fuel.md"}],"layouts":["7mfk"],"note":"b=0: '
                                        'E=RAM16[ffff2a24]. MOV.W/EXTU.W supplies an unsigned16 '
                                        'bounded-consumer context. Both banks, complete uint16 word '
                                        'boundaries and independent sibling words are executed; producer '
                                        'signedness, units, acquisition and physical meaning are '
                                        'unchanged.","relies":"structure","reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","supports":"identity","to":"bank_base_pulse_builder/fn","type":"reader","via":["bank_base_pulse_builder/fn"]},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"dexterous-yak/fn","type":"writer"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"startup_initializer/fn","type":"writer"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"true-quokka/fn","type":"writer"}],"note":["Stock '
                                        'bounds are 90 and 110 percent. When ROM8[0x8B2A] bit 2 is set both '
                                        'writers also copy the result to bank 2 word ffff2a26; stock value '
                                        '0x09 keeps the banks independent. The physical source of the '
                                        'correction is unresolved."],"summary":"Bank 1 word of the two-word '
                                        'third fuel-trim array in Q8.8 percent representation with neutral '
                                        '0x6400. Init routine 0002c648 and reset function 0005b708 store '
                                        '0x6400; FUN 0005b534 steps the word by ROM-defined increments, '
                                        'bounds it to ROM8[0x82E4] << 8..ROM8[0x82E5] << 8, and otherwise '
                                        'ramps accumulator ffff3310 toward 0x6400 by ROM8[0x86F5] per pass. '
                                        'FUN 0004ead4 adds the word to the short-term and long-term trims '
                                        'before scaling precursor '
                                        'ffff18c0.","symbol":[{"address":"ffff2a24","evidence":[{"at":"7mfk:000082e4","kind":"rom-bytes","supports":"identity","value":"0x5a"},{"at":"7mfk:000082e5","kind":"rom-bytes","supports":"identity","value":"0x6e"},{"at":"7mfk:000086f5","kind":"rom-bytes","supports":"identity","value":"0x08"},{"at":"7mfk:00008b2a","kind":"rom-bytes","supports":"identity","value":"0x09"},{"at":"7mfk:0002c976","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000082e4","000082e5","000086f5","00008b2a","0002c648","0004ead4","0005b534","0005b708","ffff2a24"],"span":1}},{"at":"7mfk:0005b5ae","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000082e4","000082e5","000086f5","00008b2a","0002c648","0004ead4","0005b534","0005b708","ffff2a24"],"span":1}},{"at":"7mfk:0005b6f0","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000082e4","000082e5","000086f5","00008b2a","0002c648","0004ead4","0005b534","0005b708","ffff2a24"],"span":1}},{"at":"7mfk:0005b77c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000082e4","000082e5","000086f5","00008b2a","0002c648","0004ead4","0005b534","0005b708","ffff2a24"],"span":1}},{"at":"7mfk:0004eaf0","kind":"l0"},{"key":"test_bank_base_pulse_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_bank_base_pulse_chain.py"},{"key":"test_bank_base_pulse_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_bank_base_pulse_chain.py"},{"key":"Bounded '
                                        'bank base-pulse '
                                        'builder","kind":"spec","path":"defs/JK08A.fuel.md"}],"layout":"7mfk","name":"astonishing-hoatzin","note":"The '
                                        'complete bank base-pulse entry consumes or publishes this raw16 '
                                        'word in its stated legal bank context. Its unsigned16 reader '
                                        'interpretation is explicit on typed reader/input/writer links; this '
                                        'storage-width fact does not change producer signedness, units, '
                                        'physical identity, other readers or '
                                        'layouts.","width":16}],"unit":"percent*256"}',
                'proposed_native_sha256': '22a7f8815819d1df81c897c0f3fc037193220e3e930747378e9ea71ae5a73c86',
                'proposed_native_json': '{"ledger":[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"bank_base_pulse_builder/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"dexterous-yak/fn","type":"writer"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"startup_initializer/fn","type":"writer"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"true-quokka/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5,6,7],"notes":[0],"order":908,"registry":"vars"}],"level":"code","link":[{"evidence":[{"at":"7mfk:0004eaf0","kind":"l0"},{"key":"test_bank_base_pulse_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_bank_base_pulse_chain.py"},{"key":"test_bank_base_pulse_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_bank_base_pulse_chain.py"},{"key":"Bounded '
                                        'bank base-pulse '
                                        'builder","kind":"spec","path":"defs/JK08A.fuel.md"}],"layouts":["7mfk"],"note":"b=0: '
                                        'E=RAM16[ffff2a24]. MOV.W/EXTU.W supplies an unsigned16 '
                                        'bounded-consumer context. Both banks, complete uint16 word '
                                        'boundaries and independent sibling words are executed; producer '
                                        'signedness, units, acquisition and physical meaning are '
                                        'unchanged.","relies":"structure","reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","supports":"identity","to":"bank_base_pulse_builder/fn","type":"reader","via":["bank_base_pulse_builder/fn"]},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"dexterous-yak/fn","type":"writer"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"startup_initializer/fn","type":"writer"},{"evidence":[{"at":"7mfk:0005b6f0","key":"third-trim-word-writer-access-v1:jk08a:retained-bank1-2a24-complete-writer","kind":"indirect","mode":"third-trim-word-writer-access","note":"Complete '
                                        'stock leaf execution binds the exact bank1 channel-zero word writer '
                                        'and actual full R2 store. All raw channels, signed32 accumulator '
                                        'paths and conditional shared-bank effects remain observed. Full '
                                        'native owner/function facts, storage width16, absent producer '
                                        'signedness, unit percent*256, typed reader, other writers and TEST '
                                        'positions stay '
                                        'fixed.","path":"defs/JK08A.third-trim-word-writer-claims.toml","supports":"identity","value":{"actual_accumulator":{"base":4294914832,"full_signed32":true,"neutral":25600,"read_site":374416,"stride":4,"width_bytes":4,"write_sites":[374456,374484]},"actual_indexed_write":{"base":4294912548,"register":2,"site":374512,"stride":2,"width_bytes":2},"actual_mask":"channel+1","actual_shared_write":{"address":4294912550,"copy_site":374514,"mode_ROM":35626,"mode_bit":2,"register":0,"site":374516,"width_bytes":2},"all_other_writers_and_native_TEST_positions_preserved":true,"causal_bank1_prior_word_and_accumulator_alternatives":true,"complete_natural_entry_RAM_frame_CPU":true,"component":"third_trim_word_writer_paths","direction":"writer","discarded_channel_high24_full_state_invariance":true,"entry":374068,"existing_unit":"percent*256","full_R2_not_only_low16_required":true,"function":"7mfk:0005b534","hardware_qualification":false,"identity_channel":0,"independent_ordinary_shared_sibling_modes":true,"native_address":4294912548,"native_geometry_inference":false,"native_producer_signedness":"unset","native_storage_width":16,"natural_caller_reachability":false,"natural_scheduling_inference":false,"no_other_channel_semantic_owner_inference":true,"no_stock_calls":true,"original_claim_sha256":"058492927bab2006d7003566c42d6b3afdd9d72a78f5fb8070f12848fff98780","owner":"astonishing-hoatzin/ram","raw_channel_from_full_R4_low8":true,"raw_channel_values":256,"scale_admission":false,"scope":"exact-bank1-third-trim-word-writer","typed_reader":"bank_base_pulse_builder/fn","units_admission":false,"width_bytes":2}}],"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"true-quokka/fn","type":"writer"}],"note":["Stock '
                                        'bounds are 90 and 110 percent. When ROM8[0x8B2A] bit 2 is set both '
                                        'writers also copy the result to bank 2 word ffff2a26; stock value '
                                        '0x09 keeps the banks independent. The physical source of the '
                                        'correction is unresolved."],"summary":"Bank 1 word of the two-word '
                                        'third fuel-trim array in Q8.8 percent representation with neutral '
                                        '0x6400. Init routine 0002c648 and reset function 0005b708 store '
                                        '0x6400; FUN 0005b534 steps the word by ROM-defined increments, '
                                        'bounds it to ROM8[0x82E4] << 8..ROM8[0x82E5] << 8, and otherwise '
                                        'ramps accumulator ffff3310 toward 0x6400 by ROM8[0x86F5] per pass. '
                                        'FUN 0004ead4 adds the word to the short-term and long-term trims '
                                        'before scaling precursor '
                                        'ffff18c0.","symbol":[{"address":"ffff2a24","evidence":[{"at":"7mfk:000082e4","kind":"rom-bytes","supports":"identity","value":"0x5a"},{"at":"7mfk:000082e5","kind":"rom-bytes","supports":"identity","value":"0x6e"},{"at":"7mfk:000086f5","kind":"rom-bytes","supports":"identity","value":"0x08"},{"at":"7mfk:00008b2a","kind":"rom-bytes","supports":"identity","value":"0x09"},{"at":"7mfk:0002c976","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000082e4","000082e5","000086f5","00008b2a","0002c648","0004ead4","0005b534","0005b708","ffff2a24"],"span":1}},{"at":"7mfk:0005b5ae","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000082e4","000082e5","000086f5","00008b2a","0002c648","0004ead4","0005b534","0005b708","ffff2a24"],"span":1}},{"at":"7mfk:0005b6f0","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000082e4","000082e5","000086f5","00008b2a","0002c648","0004ead4","0005b534","0005b708","ffff2a24"],"span":1}},{"at":"7mfk:0005b77c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000082e4","000082e5","000086f5","00008b2a","0002c648","0004ead4","0005b534","0005b708","ffff2a24"],"span":1}},{"at":"7mfk:0004eaf0","kind":"l0"},{"key":"test_bank_base_pulse_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_bank_base_pulse_chain.py"},{"key":"test_bank_base_pulse_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_bank_base_pulse_chain.py"},{"key":"Bounded '
                                        'bank base-pulse '
                                        'builder","kind":"spec","path":"defs/JK08A.fuel.md"}],"layout":"7mfk","name":"astonishing-hoatzin","note":"The '
                                        'complete bank base-pulse entry consumes or publishes this raw16 '
                                        'word in its stated legal bank context. Its unsigned16 reader '
                                        'interpretation is explicit on typed reader/input/writer links; this '
                                        'storage-width fact does not change producer signedness, units, '
                                        'physical identity, other readers or '
                                        'layouts.","width":16}],"unit":"percent*256"}',
                'original_ledger_json': '[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"bank_base_pulse_builder/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"dexterous-yak/fn","type":"writer"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"startup_initializer/fn","type":"writer"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"true-quokka/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5,6,7],"notes":[0],"order":908,"registry":"vars"}]',
                'proposed_ledger_json': '[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"bank_base_pulse_builder/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"dexterous-yak/fn","type":"writer"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"startup_initializer/fn","type":"writer"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"true-quokka/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5,6,7],"notes":[0],"order":908,"registry":"vars"}]',
                'original_symbol_evidence_json': '[{"at":"7mfk:000082e4","kind":"rom-bytes","supports":"identity","value":"0x5a"},{"at":"7mfk:000082e5","kind":"rom-bytes","supports":"identity","value":"0x6e"},{"at":"7mfk:000086f5","kind":"rom-bytes","supports":"identity","value":"0x08"},{"at":"7mfk:00008b2a","kind":"rom-bytes","supports":"identity","value":"0x09"},{"at":"7mfk:0002c976","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000082e4","000082e5","000086f5","00008b2a","0002c648","0004ead4","0005b534","0005b708","ffff2a24"],"span":1}},{"at":"7mfk:0005b5ae","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000082e4","000082e5","000086f5","00008b2a","0002c648","0004ead4","0005b534","0005b708","ffff2a24"],"span":1}},{"at":"7mfk:0005b6f0","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000082e4","000082e5","000086f5","00008b2a","0002c648","0004ead4","0005b534","0005b708","ffff2a24"],"span":1}},{"at":"7mfk:0005b77c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000082e4","000082e5","000086f5","00008b2a","0002c648","0004ead4","0005b534","0005b708","ffff2a24"],"span":1}},{"at":"7mfk:0004eaf0","kind":"l0"},{"key":"test_bank_base_pulse_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_bank_base_pulse_chain.py"},{"key":"test_bank_base_pulse_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_bank_base_pulse_chain.py"},{"key":"Bounded '
                                                 'bank base-pulse '
                                                 'builder","kind":"spec","path":"defs/JK08A.fuel.md"}]',
                'evidence_json': '{"at":"7mfk:0005b6f0","key":"third-trim-word-writer-access-v1:jk08a:retained-bank1-2a24-complete-writer","kind":"indirect","mode":"third-trim-word-writer-access","note":"Complete '
                                 'stock leaf execution binds the exact bank1 channel-zero word writer and '
                                 'actual full R2 store. All raw channels, signed32 accumulator paths and '
                                 'conditional shared-bank effects remain observed. Full native '
                                 'owner/function facts, storage width16, absent producer signedness, unit '
                                 'percent*256, typed reader, other writers and TEST positions stay '
                                 'fixed.","path":"defs/JK08A.third-trim-word-writer-claims.toml","supports":"identity","value":{"actual_accumulator":{"base":4294914832,"full_signed32":true,"neutral":25600,"read_site":374416,"stride":4,"width_bytes":4,"write_sites":[374456,374484]},"actual_indexed_write":{"base":4294912548,"register":2,"site":374512,"stride":2,"width_bytes":2},"actual_mask":"channel+1","actual_shared_write":{"address":4294912550,"copy_site":374514,"mode_ROM":35626,"mode_bit":2,"register":0,"site":374516,"width_bytes":2},"all_other_writers_and_native_TEST_positions_preserved":true,"causal_bank1_prior_word_and_accumulator_alternatives":true,"complete_natural_entry_RAM_frame_CPU":true,"component":"third_trim_word_writer_paths","direction":"writer","discarded_channel_high24_full_state_invariance":true,"entry":374068,"existing_unit":"percent*256","full_R2_not_only_low16_required":true,"function":"7mfk:0005b534","hardware_qualification":false,"identity_channel":0,"independent_ordinary_shared_sibling_modes":true,"native_address":4294912548,"native_geometry_inference":false,"native_producer_signedness":"unset","native_storage_width":16,"natural_caller_reachability":false,"natural_scheduling_inference":false,"no_other_channel_semantic_owner_inference":true,"no_stock_calls":true,"original_claim_sha256":"058492927bab2006d7003566c42d6b3afdd9d72a78f5fb8070f12848fff98780","owner":"astonishing-hoatzin/ram","raw_channel_from_full_R4_low8":true,"raw_channel_values":256,"scale_admission":false,"scope":"exact-bank1-third-trim-word-writer","typed_reader":"bank_base_pulse_builder/fn","units_admission":false,"width_bytes":2}}'}],
 'retained_functions': [{'address': 374068,
                         'owner': 'true-quokka/fn',
                         'source': 'kb/fn/true-quokka.toml',
                         'native_sha256': 'ff7e591e0cabf8c51f2c865b221f94850cc01ae1fc06025f1d69a0d18bacecaa',
                         'native_json': '{"symbol":[{"address":"0005b534","evidence":[{"at":"7mfk:0005b534","kind":"l0","supports":"identity"}],"layout":"7mfk","name":"true-quokka"}]}'}]}
IDENTITIES=(('retained-bank1-2a24-complete-writer',
  4294912548,
  'astonishing-hoatzin/ram',
  374068,
  (374512,),
  'writer',
  'third_trim_word_writer_paths',
  2,
  16,
  'unset',
  '058492927bab2006d7003566c42d6b3afdd9d72a78f5fb8070f12848fff98780',
  'e628d065a7505f3cfd129a176daecf5b0a2798cf4d032b369bb585022356362f',
  'a5f765469581e39f17e656027d41d8e55d5664ba1c5c27ca9446c012fe3ae193',
  '22a7f8815819d1df81c897c0f3fc037193220e3e930747378e9ea71ae5a73c86'),)

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):raise ValueError('the quantity claim changes its exact retained native/function/type/evidence/TEST boundary')
    row=value['reference'][0];old=json.loads(row['original_claim_json']);new=json.loads(row['proposed_claim_json'])
    expected=deepcopy(old);expected['evidence'].append(item(row))
    before=json.loads(row['original_native_json']);after=deepcopy(before)
    links=[r for r in after['link'] if (r['type'],r['to'])==('writer','true-quokka/fn')]
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
def operation(row):return dict(cmd='link',meaning=row['owner'],type='writer',to=json.loads(row['original_claim_json'])['to'],evidence=[item(row)])
def operations(ops,root):
    selected=[op for op in ops if any(registered(item) for item in op.get('evidence',()))]
    if not selected:return False
    if not test_contract.exact(selected,[operation(descriptor(root)['reference'][0])]):
        raise ValueError('the quantity attachment requires its one exact complete normal owning link operation')
    return True
def looks_like_access(link):
    return any(registered(e) for e in link.evidence) or (link.owner.key,link.type,link.to.key)==('astonishing-hoatzin/ram','writer','true-quokka/fn')
