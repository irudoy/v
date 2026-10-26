"""One retained helper writer and exact reuse of the complete stock reset closure."""
from pathlib import Path
from copy import deepcopy
import json,tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import digest
DESCRIPTOR='defs/JK08A.diagnostic-reset-helper-writer-claims.toml'
MODE='diagnostic-state-reset-writer-access'
PREFIX='diagnostic-state-reset-writer-access-v1:jk08a:'
DECLARED = {'schema': 1,
 'id': 'jk08a-diagnostic-reset-helper-writer-claims',
 'layout': '7mfk',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'One exact natural reset-helper byte-zero writer using the complete existing three-function '
          'reset capture and ordinary/native transport.',
 'core_descriptor': 'defs/JK08A.diagnostic-state-reset-writer-paths.toml',
 'preserved_parent_original_sha256': '939c9a3b6a4bbc89b4d0183a02aa6bcbe3024a8716b51676cd36dca5eb9e487a',
 'native_function_publication': False,
 'native_geometry_publication': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_caller_reachability': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'peripheral_side_effects_admission': False,
 'reference': [{'id': 'retained-2e76e-99c7-writer',
                'address': 4294941127,
                'owner': 'chocolate-civet/ram',
                'function': 190318,
                'sites': [190330],
                'direction': 'writer',
                'source': 'kb/ram/chocolate-civet.toml',
                'component': 'diagnostic_state_reset_writer_paths',
                'width_bytes': 1,
                'declared_width': 'unset',
                'declared_signed': 'unset',
                'original_claim_sha256': '8dec00dbb4e93fb0907e58c1a1a0dd41e845c8856a229170e4ac1a3ad399b3c2',
                'original_claim_json': '{"evidence":[],"layout":"7mfk","offset":null,"owner":"chocolate-civet/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/chocolate-civet.toml"],"stated":["7mfk"],"to":"cheerful-beluga/fn","type":"writer"}',
                'proposed_claim_sha256': '8315afd4b75754db4d8f38fc6fcf9b931616a85736a5418d6a6cb2fd126b11f7',
                'proposed_claim_json': '{"evidence":[{"at":"7mfk:0002e77a","key":"diagnostic-state-reset-writer-access-v1:jk08a:retained-2e76e-99c7-writer","kind":"indirect","mode":"diagnostic-state-reset-writer-access","note":"The '
                                       'complete existing diagnostic reset capture binds the exact '
                                       'FFFF99C7 byte-zero store in natural callee 2E76E. The full R7=0 '
                                       'carrier, fourth loop pointer/counter state, real caller/helper '
                                       'entry and return, separate physical ordinary/native snapshots and '
                                       'all raw target priors with other inputs fixed are required. The '
                                       'full owner, three functions, other relations, unset native type, '
                                       'bitfield unit, ledgers and TEST origins remain '
                                       'exact.","path":"defs/JK08A.diagnostic-reset-helper-writer-claims.toml","supports":"identity","value":{"actual_constant_write":{"address":4294941127,"counter_register":6,"counter_value":4,"full_register_value":0,"loop_count":4,"loop_start":4294941124,"pointer_register":5,"register":7,"site":190330,"value":0,"width_bytes":1,"zero_based_iteration":3},"complete_existing_root_and_callees":[190318,190490,841564],"complete_fixed_other_target_priors_both_later_gate_paths":true,"complete_full_R7_pointer_counter_and_helper_return":true,"complete_native_owner_function_TEST_ledger":true,"component":"diagnostic_state_reset_writer_paths","constant_requires_distinct_final_outputs":false,"direction":"writer","entry":190490,"exact_natural_call":{"delay_site":190502,"return_address":190504,"site":190500,"target":190318},"function":"7mfk:0002e76e","hardware_qualification":false,"native_address":4294941127,"native_geometry_inference":false,"native_signed":"unset","native_storage_width":"unset","native_unit":"bitfield","natural_caller_reachability":false,"natural_scheduling_inference":false,"no_withdrawal":true,"original_claim_sha256":"8dec00dbb4e93fb0907e58c1a1a0dd41e845c8856a229170e4ac1a3ad399b3c2","owner":"chocolate-civet/ram","peripheral_side_effects_admission":false,"preserved_parent_original_sha256":"939c9a3b6a4bbc89b4d0183a02aa6bcbe3024a8716b51676cd36dca5eb9e487a","scale_admission":false,"scope":"exact-diagnostic-reset-helper-writer","units_admission":false,"width_bytes":1}}],"layout":"7mfk","offset":null,"owner":"chocolate-civet/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/chocolate-civet.toml"],"stated":["7mfk"],"to":"cheerful-beluga/fn","type":"writer"}',
                'original_native_sha256': '18ac5e594afb6338067d192cb82666fb815fc392803e08bb4cc3596297f13a89',
                'original_native_json': '{"ledger":[{"dependency":[{"end":"owner","relies":"level","role":"consumer","supports":"identity","to":"muscular-lizard/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"cheerful-beluga/fn","type":"writer"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"nissan_service_30_output_control/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0],"notes":[0],"order":806,"registry":"vars"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"level","reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","supports":"identity","to":"muscular-lizard/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"cheerful-beluga/fn","type":"writer"},{"layouts":["7mfk"],"relies":"level","supports":"identity","to":"nissan_service_30_output_control/fn","type":"writer"}],"note":["The '
                                        'value bytes of the same requests are ffff9923 + n (ffff993c, '
                                        'ffff993d, ffff9940 for IOLIDs 0x19, 0x1a, '
                                        '0x1d)."],"summary":"Active-flag byte of service-0x30 Output '
                                        'Control IOLIDs 0x19..0x20 (array ffff99c4, bit n-1 of IOLID n): '
                                        'bit 0 is IOLID 0x19, bit 1 IOLID 0x1a, and bit 4 IOLID 0x1d. '
                                        'Handler 00030c4c maintains the array, FUN 0002e466 reads the byte '
                                        'at 0002e50e for the VTC active tests, and startup 0002e76e zeroes '
                                        'ffff99c4..ffff99d3.","symbol":[{"address":"ffff99c7","evidence":[{"at":"7mfk:0002e50e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0002e466","0002e76e","00030c4c","ffff99c7"],"span":1}}],"layout":"7mfk","name":"chocolate-civet"}],"unit":"bitfield"}',
                'proposed_native_sha256': 'c9f79d93e390e2d7a95efb69cdf1cc425e98a7aae4df5bdcdcb6e1c1fe03b7fa',
                'proposed_native_json': '{"ledger":[{"dependency":[{"end":"owner","relies":"level","role":"consumer","supports":"identity","to":"muscular-lizard/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"cheerful-beluga/fn","type":"writer"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"nissan_service_30_output_control/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0],"notes":[0],"order":806,"registry":"vars"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"level","reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","supports":"identity","to":"muscular-lizard/fn","type":"reader"},{"evidence":[{"at":"7mfk:0002e77a","key":"diagnostic-state-reset-writer-access-v1:jk08a:retained-2e76e-99c7-writer","kind":"indirect","mode":"diagnostic-state-reset-writer-access","note":"The '
                                        'complete existing diagnostic reset capture binds the exact '
                                        'FFFF99C7 byte-zero store in natural callee 2E76E. The full R7=0 '
                                        'carrier, fourth loop pointer/counter state, real caller/helper '
                                        'entry and return, separate physical ordinary/native snapshots and '
                                        'all raw target priors with other inputs fixed are required. The '
                                        'full owner, three functions, other relations, unset native type, '
                                        'bitfield unit, ledgers and TEST origins remain '
                                        'exact.","path":"defs/JK08A.diagnostic-reset-helper-writer-claims.toml","supports":"identity","value":{"actual_constant_write":{"address":4294941127,"counter_register":6,"counter_value":4,"full_register_value":0,"loop_count":4,"loop_start":4294941124,"pointer_register":5,"register":7,"site":190330,"value":0,"width_bytes":1,"zero_based_iteration":3},"complete_existing_root_and_callees":[190318,190490,841564],"complete_fixed_other_target_priors_both_later_gate_paths":true,"complete_full_R7_pointer_counter_and_helper_return":true,"complete_native_owner_function_TEST_ledger":true,"component":"diagnostic_state_reset_writer_paths","constant_requires_distinct_final_outputs":false,"direction":"writer","entry":190490,"exact_natural_call":{"delay_site":190502,"return_address":190504,"site":190500,"target":190318},"function":"7mfk:0002e76e","hardware_qualification":false,"native_address":4294941127,"native_geometry_inference":false,"native_signed":"unset","native_storage_width":"unset","native_unit":"bitfield","natural_caller_reachability":false,"natural_scheduling_inference":false,"no_withdrawal":true,"original_claim_sha256":"8dec00dbb4e93fb0907e58c1a1a0dd41e845c8856a229170e4ac1a3ad399b3c2","owner":"chocolate-civet/ram","peripheral_side_effects_admission":false,"preserved_parent_original_sha256":"939c9a3b6a4bbc89b4d0183a02aa6bcbe3024a8716b51676cd36dca5eb9e487a","scale_admission":false,"scope":"exact-diagnostic-reset-helper-writer","units_admission":false,"width_bytes":1}}],"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"cheerful-beluga/fn","type":"writer"},{"layouts":["7mfk"],"relies":"level","supports":"identity","to":"nissan_service_30_output_control/fn","type":"writer"}],"note":["The '
                                        'value bytes of the same requests are ffff9923 + n (ffff993c, '
                                        'ffff993d, ffff9940 for IOLIDs 0x19, 0x1a, '
                                        '0x1d)."],"summary":"Active-flag byte of service-0x30 Output '
                                        'Control IOLIDs 0x19..0x20 (array ffff99c4, bit n-1 of IOLID n): '
                                        'bit 0 is IOLID 0x19, bit 1 IOLID 0x1a, and bit 4 IOLID 0x1d. '
                                        'Handler 00030c4c maintains the array, FUN 0002e466 reads the byte '
                                        'at 0002e50e for the VTC active tests, and startup 0002e76e zeroes '
                                        'ffff99c4..ffff99d3.","symbol":[{"address":"ffff99c7","evidence":[{"at":"7mfk:0002e50e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0002e466","0002e76e","00030c4c","ffff99c7"],"span":1}}],"layout":"7mfk","name":"chocolate-civet"}],"unit":"bitfield"}',
                'original_ledger_json': '[{"dependency":[{"end":"owner","relies":"level","role":"consumer","supports":"identity","to":"muscular-lizard/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"cheerful-beluga/fn","type":"writer"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"nissan_service_30_output_control/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0],"notes":[0],"order":806,"registry":"vars"}]',
                'proposed_ledger_json': '[{"dependency":[{"end":"owner","relies":"level","role":"consumer","supports":"identity","to":"muscular-lizard/fn","type":"reader"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"cheerful-beluga/fn","type":"writer"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"nissan_service_30_output_control/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0],"notes":[0],"order":806,"registry":"vars"}]',
                'original_symbol_evidence_json': '[{"at":"7mfk:0002e50e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0002e466","0002e76e","00030c4c","ffff99c7"],"span":1}}]',
                'evidence_json': '{"at":"7mfk:0002e77a","key":"diagnostic-state-reset-writer-access-v1:jk08a:retained-2e76e-99c7-writer","kind":"indirect","mode":"diagnostic-state-reset-writer-access","note":"The '
                                 'complete existing diagnostic reset capture binds the exact FFFF99C7 '
                                 'byte-zero store in natural callee 2E76E. The full R7=0 carrier, fourth '
                                 'loop pointer/counter state, real caller/helper entry and return, '
                                 'separate physical ordinary/native snapshots and all raw target priors '
                                 'with other inputs fixed are required. The full owner, three functions, '
                                 'other relations, unset native type, bitfield unit, ledgers and TEST '
                                 'origins remain '
                                 'exact.","path":"defs/JK08A.diagnostic-reset-helper-writer-claims.toml","supports":"identity","value":{"actual_constant_write":{"address":4294941127,"counter_register":6,"counter_value":4,"full_register_value":0,"loop_count":4,"loop_start":4294941124,"pointer_register":5,"register":7,"site":190330,"value":0,"width_bytes":1,"zero_based_iteration":3},"complete_existing_root_and_callees":[190318,190490,841564],"complete_fixed_other_target_priors_both_later_gate_paths":true,"complete_full_R7_pointer_counter_and_helper_return":true,"complete_native_owner_function_TEST_ledger":true,"component":"diagnostic_state_reset_writer_paths","constant_requires_distinct_final_outputs":false,"direction":"writer","entry":190490,"exact_natural_call":{"delay_site":190502,"return_address":190504,"site":190500,"target":190318},"function":"7mfk:0002e76e","hardware_qualification":false,"native_address":4294941127,"native_geometry_inference":false,"native_signed":"unset","native_storage_width":"unset","native_unit":"bitfield","natural_caller_reachability":false,"natural_scheduling_inference":false,"no_withdrawal":true,"original_claim_sha256":"8dec00dbb4e93fb0907e58c1a1a0dd41e845c8856a229170e4ac1a3ad399b3c2","owner":"chocolate-civet/ram","peripheral_side_effects_admission":false,"preserved_parent_original_sha256":"939c9a3b6a4bbc89b4d0183a02aa6bcbe3024a8716b51676cd36dca5eb9e487a","scale_admission":false,"scope":"exact-diagnostic-reset-helper-writer","units_admission":false,"width_bytes":1}}'}],
 'retained_functions': [{'address': 190490,
                         'owner': 'amber-wildcat/fn',
                         'source': 'kb/fn/amber-wildcat.toml',
                         'native_sha256': '1d37bef268164f48790c6a2df1d5e6886ae43cf2177ee3cbde4c8df40f5afd78',
                         'native_json': '{"block":"work_support/block","ledger":[{"dependency":[{"end":"owner","link_role":"consumer","relies":"structure","role":"consumer","supports":"identity","to":"peach-guan/fn","type":"depends"},{"end":"owner","link_role":"consumer","relies":"structure","role":"consumer","supports":"identity","to":"refreshing-dinosaur/fn","type":"depends"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"nickel-fulmar/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"ruby-mouse/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],"notes":[0],"order":669,"registry":"funcs"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","role":"consumer","supports":"identity","to":"peach-guan/fn","type":"depends"},{"layouts":["7mfk"],"relies":"structure","role":"consumer","supports":"identity","to":"refreshing-dinosaur/fn","type":"depends"}],"note":["Transport '
                                        'state machine 0002ea0a calls it at 0002ec2a when transport state '
                                        'ffff821c is 8 and ffff8468 is neither 3 nor 4, and 000ca69c also '
                                        'calls it. Together with control 0xff, the reset ends an active '
                                        'work-support '
                                        'adjustment."],"role":"service","summary":"Diagnostic-state reset. '
                                        'It calls 0002e76e, which clears the service-0x30 state, zeroes '
                                        'service-0x3b flag bytes ffff99f4..ffff99f9, value slots '
                                        'ffff99dc..ffff99f3, and ffff99d8..ffff99d9, clears bits 6 and 7 '
                                        'of ffff9a6b, zeroes ffff8422, ffff8423, ffff8462, and ffff8463, '
                                        'clears ffff4198.bit4, calls 000cd75c with ffff40be, zeroes '
                                        'ffff40be, clears ffff41de.bit0 and bits 5 and 6 of ffff41a4, and '
                                        'zeroes '
                                        'ffff2985.","symbol":[{"address":"0002e81a","evidence":[{"at":"7mfk:0002e836","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e84a","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e85a","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e86e","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e874","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e876","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e87a","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e87c","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e880","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e884","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e890","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e894","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e898","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002e89e","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002ec1a","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"at":"7mfk:0002ec2a","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0002e76e","0002e81a","0002ea0a","000ca69c","000cd75c","ffff99dc","ffff99f4"],"span":1}},{"kind":"trace","relies":"structure","supports":"identity","to":"cheerful-beluga/fn/7mfk"},{"kind":"trace","relies":"structure","supports":"identity","to":"striped-tiger/fn/7mfk"}],"layout":"7mfk","name":"amber-wildcat"}]}'},
                        {'address': 190318,
                         'owner': 'cheerful-beluga/fn',
                         'source': 'kb/fn/cheerful-beluga.toml',
                         'native_sha256': '3f5aace80c6832abe2a60513c69cd9543117cdd4c7c76d3a93f012d6ae21360a',
                         'native_json': '{"symbol":[{"address":"0002e76e","evidence":[{"at":"7mfk:0002e76e","kind":"l0","supports":"identity"}],"layout":"7mfk","name":"cheerful-beluga"}]}'},
                        {'address': 841564,
                         'owner': 'striped-tiger/fn',
                         'source': 'kb/fn/striped-tiger.toml',
                         'native_sha256': '1bbfb92c7b65d3165026c5db68c90072a37573d25800b66e9fbd24f666d3f443',
                         'native_json': '{"block":"cvtc_exhaust/block","ledger":[{"dependency":[{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"enthusiastic-chicken/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"nice-bison/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"shaggy-nyala/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"uptight-nyala/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"vagabond-labradoodle/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3],"notes":[0],"order":612,"registry":"funcs"}],"level":"code","note":["Clearing '
                                        'ffff4251 bit 0 returns 000c2152 to the computed duty words; '
                                        'service-0xa0 request 3 selects the fixed 60/50 percent test '
                                        'fractions by setting the bit."],"role":"init","summary":"Exhaust '
                                        'duty reset, reached from initialization path 0002e81a and '
                                        'service-0xa0 handler 000306f8. It clears ffff4251 bit 0 at '
                                        '000cd76e and ffff41de bit 2 at 000cd772, zeroes checksum state '
                                        'ffff30f8, ffff3084, and ffff30b0, and programs both ATU-II '
                                        'channel-7 cycle pairs from ROM8[00008dfc]=33 and '
                                        'ROM8[00008dfd]=20.","symbol":[{"address":"000cd75c","evidence":[{"kind":"unbound-constant","supports":"identity","value":"00008dfc=33"},{"kind":"unbound-constant","supports":"identity","value":"00008dfd=20"},{"at":"7mfk:000cd76e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008dfc","00008dfd","000cd75c","ffff3084","ffff30b0","ffff30f8","ffff41de","ffff4251"],"span":1}},{"at":"7mfk:000cd772","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008dfc","00008dfd","000cd75c","ffff3084","ffff30b0","ffff30f8","ffff41de","ffff4251"],"span":1}}],"layout":"7mfk","name":"striped-tiger"}]}'}]}
IDENTITIES = (('retained-2e76e-99c7-writer',
  4294941127,
  'chocolate-civet/ram',
  190318,
  (190330,),
  'writer',
  'diagnostic_state_reset_writer_paths',
  1,
  'unset',
  'unset',
  '8dec00dbb4e93fb0907e58c1a1a0dd41e845c8856a229170e4ac1a3ad399b3c2',
  '8315afd4b75754db4d8f38fc6fcf9b931616a85736a5418d6a6cb2fd126b11f7',
  '18ac5e594afb6338067d192cb82666fb815fc392803e08bb4cc3596297f13a89',
  'c9f79d93e390e2d7a95efb69cdf1cc425e98a7aae4df5bdcdcb6e1c1fe03b7fa'),)
SOURCE_FILES=(DESCRIPTOR,'defs/JK08A.diagnostic-reset-helper-writer.md',
    'tools/kb/src/kb/diagnostic_reset_helper_writer_contract.py',
    'tools/kb/src/kb/diagnostic_reset_helper_writer_transfers.py',
    'tools/kb/src/kb/diagnostic_reset_helper_writer_capture_evidence.py',
    'tools/kb/tests/test_diagnostic_reset_helper_writer_contract.py',
    'tools/kb/tests/test_diagnostic_reset_helper_writer_capture_evidence.py',
    'tools/kb/tests/test_diagnostic_reset_helper_writer_access.py')

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):
        raise ValueError('the reset helper changes its exact native owner, complete functions or retained parent proof boundary')
    row=value['reference'][0];old=json.loads(row['original_claim_json']);new=deepcopy(old);new['evidence'].append(item(row))
    before=json.loads(row['original_native_json']);after=deepcopy(before)
    selected,=[link for link in after['link'] if (link['type'],link['to'])==('writer','cheerful-beluga/fn')]
    selected.setdefault('evidence',[]).append(item(row))
    if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
            or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
            or not test_contract.exact(new,json.loads(row['proposed_claim_json']))
            or not test_contract.exact(after,json.loads(row['proposed_native_json']))
            or not test_contract.exact(before['ledger'],after['ledger'])
            or before['unit']!='bitfield' or any('width' in symbol or 'signed' in symbol for symbol in before['symbol'])):
        raise ValueError('the reset helper changes more than its one exact identity-support append')
    for function in value['retained_functions']:
        if digest(json.loads(function['native_json']))!=function['native_sha256']:
            raise ValueError('the reset helper changes a complete retained function')
    return value

def item(row):return json.loads(row['evidence_json'])
