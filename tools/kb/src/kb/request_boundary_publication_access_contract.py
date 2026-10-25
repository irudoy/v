"""One exact retained delegated writer and its owning identity append."""
from copy import deepcopy
from pathlib import Path
import json,tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,plain
from kb.model import SymbolKey
DESCRIPTOR='defs/JK08A.request-boundary-publication-claims.toml'
MODE='request-boundary-publication-access'
PREFIX='request-boundary-publication-access-v1:jk08a:'
DECLARED={'schema': 1,
 'id': 'jk08a-request-boundary-publication-claims',
 'layout': '7mfk',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'One retained actual delegated word writer through its complete natural dispatcher.',
 'native_function_publication': False,
 'native_geometry_publication': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'reference': [{'id': 'delegated-19c6-writer',
                'address': 4294908358,
                'owner': 'throttle_request_bounded/ram',
                'function': 499160,
                'sites': [496040, 496050],
                'direction': 'writer',
                'source': 'kb/ram/throttle_request_bounded.toml',
                'component': 'request_boundary_publication_paths',
                'width_bytes': 2,
                'declared_width': 16,
                'declared_signed': 'unset',
                'original_claim_sha256': '5c055da500054f344db4f5900a11104adab441204d39be660269dfd02f3614b1',
                'original_claim_json': '{"evidence":[],"layout":"7mfk","offset":null,"owner":"throttle_request_bounded/ram","props":{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/throttle_request_bounded.toml"],"stated":["7mfk"],"to":"request_boundary_dispatch/fn","type":"writer"}',
                'proposed_claim_sha256': 'c99295a19bb4c8750c68686ce7bf424d772248124ab0bd65db702face3621274',
                'proposed_claim_json': '{"evidence":[{"at":"7mfk:00079dd8","key":"request-boundary-publication-access-v1:jk08a:delegated-19c6-writer","kind":"indirect","mode":"request-boundary-publication-access","note":"Exact '
                                       'executed complete dispatcher and live signed-bound word publication; '
                                       'native types and all retained facts remain '
                                       'fixed.","path":"defs/JK08A.request-boundary-publication-claims.toml","supports":"identity","value":{"actual_store_sites":[496040,496050],"actual_writer":495664,"component":"request_boundary_publication_paths","direction":"writer","entry":499160,"function":"7mfk:00079dd8","hardware_qualification":false,"native_address":4294908358,"native_geometry_inference":false,"natural_scheduling_inference":false,"original_claim_sha256":"5c055da500054f344db4f5900a11104adab441204d39be660269dfd02f3614b1","owner":"throttle_request_bounded/ram","real_call":{"return_address":499166,"site":499162,"target":497616},"real_tail":{"PR_restore_delay":499170,"site":499168,"target":495664},"scale_admission":false,"scope":"exact-delegated-request-publication","units_admission":false,"width_bytes":2}}],"layout":"7mfk","offset":null,"owner":"throttle_request_bounded/ram","props":{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/throttle_request_bounded.toml"],"stated":["7mfk"],"to":"request_boundary_dispatch/fn","type":"writer"}',
                'original_native_sha256': 'a4262424b9ff24dfc559411564814210ada40f59f9e8e6c9e51fd42de5e17181',
                'original_native_json': '{"ledger":[{"dependency":[{"end":"owner","relies":"level","role":"consumer","supports":"identity","to":"primary_request_inverse_lookup/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"request_coordinate_coordinator/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"strange-angelfish/fn","type":"reader"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"signed_request_boundary/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5,6],"notes":[1],"order":111,"registry":"vars","storage_description":"signed '
                                        'internal '
                                        'request"}],"level":"code","link":[{"layouts":["7mfk"],"reverse_relies":"level","reverse_supports":"identity","to":"rev_limit_throttle_cut/tbl","type":"lookup"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","to":"ginger-hedgehog/fn","type":"reader"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","to":"peach-bullfrog/fn","type":"reader"},{"layouts":["7mfk"],"relies":"level","reverse_relies":"level","reverse_supports":"identity","role":"indexed_by","supports":"identity","to":"primary_request_inverse_lookup/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"request_coordinate_coordinator/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","supports":"identity","to":"strange-angelfish/fn","type":"reader"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","to":"request_boundary_dispatch/fn","type":"writer"},{"layouts":["7mfk"],"relies":"level","reverse_relies":"structure","reverse_supports":"identity","supports":"identity","to":"signed_request_boundary/fn","type":"writer"}],"note":["A '
                                        'final bounded signed internal request used as the inverse '
                                        'torque-surface input. Engineering conversion is unestablished. '
                                        'Retained hypothesis: Candidate requested torque at x*0.1 Nm, '
                                        'dependent on the unresolved physical conversion of the internal '
                                        'torque domain. Requested torque is not actual torque. The hardware '
                                        'actuator and bank boundaries remain explicit. Unverified '
                                        'propositions: The signed request has a confirmed x*0.1 Nm physical '
                                        'scale. A requested raw-domain torque value is a measured delivered '
                                        'engine torque. The code path proves physical throttle movement, '
                                        'motor polarity, channel-to-bank identity, or ECM terminal '
                                        'assignment. The proposed physical multiplier is validated on each '
                                        'homologous layout. Source references: '
                                        'defs/JK08A.throttle-control.md:3-17, '
                                        'defs/JK08A.throttle-control.md:304-330, '
                                        'defs/JK08A.throttle-control.md:400-431, defs/JK08A.can.md:232-236, '
                                        'defs/JK08A.tuning-telemetry.md:107-113.","The continuous 0x942c '
                                        'path continues through ffff198a, ffff183e, ffff19b2, per-channel '
                                        'targets, the feedback regulator, and ATU-II BFR6A-D. It remains '
                                        'separate from fuel mask ffff22e0; physical plate motion, '
                                        'channel-to-bank identity, and ECM terminals require hardware '
                                        'evidence."],"summary":"Shared signed request coordinate written by '
                                        'FUN 00079030 in periodic-table index-21 dispatcher 00079dd8 after '
                                        'applying mode-controlled bounds to duplicated selection '
                                        'ffff2438/ffff19c2. Index-22 FUN 00073432 adds numeric bias 0x8000, '
                                        'inverse-searches the current-RPM 0xe98e row, and writes '
                                        'stock-active coordinate '
                                        'ffff198a.","symbol":[{"address":"fffe941e","evidence":[{"at":"1me3b:fffe941e","kind":"byte-identical","note":"Matched '
                                        '1ND consumer functions reference this cell at the same instruction '
                                        'ordinals","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff19c6"}],"layout":"1me3b"},{"address":"fffe944e","evidence":[{"at":"1nd:fffe944e","kind":"byte-identical","note":"Three-generation '
                                        'homologous fail-safe branch reads this bounded '
                                        'request","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff19c6"}],"layout":"1nd"},{"address":"ffff19c6","evidence":[{"at":"7mfk:000734a8","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"at":"7mfk:000734f4","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"at":"7mfk:000735ca","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"at":"7mfk:000791a8","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"at":"7mfk:000791b2","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"kind":"trace","relies":"structure","supports":"identity","to":"request_coordinate_coordinator/fn/7mfk"},{"kind":"trace","relies":"structure","supports":"identity","to":"request_boundary_dispatch/fn/7mfk"}],"former":["cherry-goat/ram/7mfk-ffff19c6"],"layout":"7mfk"},{"address":"ffff1a24","evidence":[{"at":"jk00c:00075b2c","count":1,"kind":"masked-match","supports":"homology","to":"7mfk:00073390","value":153}],"layout":"jk00c"},{"address":"ffff1a2a","evidence":[{"at":"jk00d:00075b2c","count":1,"kind":"masked-match","supports":"homology","to":"7mfk:00073390","value":153}],"layout":"jk00d"},{"address":"ffff19b0","evidence":[{"at":"jk78c:00092faa","count":1,"kind":"masked-match","note":"Three-generation '
                                        'homologous fail-safe branch reads this bounded '
                                        'request","supports":"homology","to":"7mfk:0007378a","value":52}],"layout":"jk78c"}],"width":16}',
                'proposed_native_sha256': '6932de17f48c4b0ff58a07e73ecef4436ec04de472c3cc6cbdf5df26b5f5ef46',
                'proposed_native_json': '{"ledger":[{"dependency":[{"end":"owner","relies":"level","role":"consumer","supports":"identity","to":"primary_request_inverse_lookup/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"request_coordinate_coordinator/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"strange-angelfish/fn","type":"reader"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"signed_request_boundary/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5,6],"notes":[1],"order":111,"registry":"vars","storage_description":"signed '
                                        'internal '
                                        'request"}],"level":"code","link":[{"layouts":["7mfk"],"reverse_relies":"level","reverse_supports":"identity","to":"rev_limit_throttle_cut/tbl","type":"lookup"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","to":"ginger-hedgehog/fn","type":"reader"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","to":"peach-bullfrog/fn","type":"reader"},{"layouts":["7mfk"],"relies":"level","reverse_relies":"level","reverse_supports":"identity","role":"indexed_by","supports":"identity","to":"primary_request_inverse_lookup/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"request_coordinate_coordinator/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","supports":"identity","to":"strange-angelfish/fn","type":"reader"},{"evidence":[{"at":"7mfk:00079dd8","key":"request-boundary-publication-access-v1:jk08a:delegated-19c6-writer","kind":"indirect","mode":"request-boundary-publication-access","note":"Exact '
                                        'executed complete dispatcher and live signed-bound word '
                                        'publication; native types and all retained facts remain '
                                        'fixed.","path":"defs/JK08A.request-boundary-publication-claims.toml","supports":"identity","value":{"actual_store_sites":[496040,496050],"actual_writer":495664,"component":"request_boundary_publication_paths","direction":"writer","entry":499160,"function":"7mfk:00079dd8","hardware_qualification":false,"native_address":4294908358,"native_geometry_inference":false,"natural_scheduling_inference":false,"original_claim_sha256":"5c055da500054f344db4f5900a11104adab441204d39be660269dfd02f3614b1","owner":"throttle_request_bounded/ram","real_call":{"return_address":499166,"site":499162,"target":497616},"real_tail":{"PR_restore_delay":499170,"site":499168,"target":495664},"scale_admission":false,"scope":"exact-delegated-request-publication","units_admission":false,"width_bytes":2}}],"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","to":"request_boundary_dispatch/fn","type":"writer"},{"layouts":["7mfk"],"relies":"level","reverse_relies":"structure","reverse_supports":"identity","supports":"identity","to":"signed_request_boundary/fn","type":"writer"}],"note":["A '
                                        'final bounded signed internal request used as the inverse '
                                        'torque-surface input. Engineering conversion is unestablished. '
                                        'Retained hypothesis: Candidate requested torque at x*0.1 Nm, '
                                        'dependent on the unresolved physical conversion of the internal '
                                        'torque domain. Requested torque is not actual torque. The hardware '
                                        'actuator and bank boundaries remain explicit. Unverified '
                                        'propositions: The signed request has a confirmed x*0.1 Nm physical '
                                        'scale. A requested raw-domain torque value is a measured delivered '
                                        'engine torque. The code path proves physical throttle movement, '
                                        'motor polarity, channel-to-bank identity, or ECM terminal '
                                        'assignment. The proposed physical multiplier is validated on each '
                                        'homologous layout. Source references: '
                                        'defs/JK08A.throttle-control.md:3-17, '
                                        'defs/JK08A.throttle-control.md:304-330, '
                                        'defs/JK08A.throttle-control.md:400-431, defs/JK08A.can.md:232-236, '
                                        'defs/JK08A.tuning-telemetry.md:107-113.","The continuous 0x942c '
                                        'path continues through ffff198a, ffff183e, ffff19b2, per-channel '
                                        'targets, the feedback regulator, and ATU-II BFR6A-D. It remains '
                                        'separate from fuel mask ffff22e0; physical plate motion, '
                                        'channel-to-bank identity, and ECM terminals require hardware '
                                        'evidence."],"summary":"Shared signed request coordinate written by '
                                        'FUN 00079030 in periodic-table index-21 dispatcher 00079dd8 after '
                                        'applying mode-controlled bounds to duplicated selection '
                                        'ffff2438/ffff19c2. Index-22 FUN 00073432 adds numeric bias 0x8000, '
                                        'inverse-searches the current-RPM 0xe98e row, and writes '
                                        'stock-active coordinate '
                                        'ffff198a.","symbol":[{"address":"fffe941e","evidence":[{"at":"1me3b:fffe941e","kind":"byte-identical","note":"Matched '
                                        '1ND consumer functions reference this cell at the same instruction '
                                        'ordinals","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff19c6"}],"layout":"1me3b"},{"address":"fffe944e","evidence":[{"at":"1nd:fffe944e","kind":"byte-identical","note":"Three-generation '
                                        'homologous fail-safe branch reads this bounded '
                                        'request","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","supports":"homology","to":"7mfk:ffff19c6"}],"layout":"1nd"},{"address":"ffff19c6","evidence":[{"at":"7mfk:000734a8","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"at":"7mfk:000734f4","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"at":"7mfk:000735ca","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"at":"7mfk:000791a8","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"at":"7mfk:000791b2","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"kind":"trace","relies":"structure","supports":"identity","to":"request_coordinate_coordinator/fn/7mfk"},{"kind":"trace","relies":"structure","supports":"identity","to":"request_boundary_dispatch/fn/7mfk"}],"former":["cherry-goat/ram/7mfk-ffff19c6"],"layout":"7mfk"},{"address":"ffff1a24","evidence":[{"at":"jk00c:00075b2c","count":1,"kind":"masked-match","supports":"homology","to":"7mfk:00073390","value":153}],"layout":"jk00c"},{"address":"ffff1a2a","evidence":[{"at":"jk00d:00075b2c","count":1,"kind":"masked-match","supports":"homology","to":"7mfk:00073390","value":153}],"layout":"jk00d"},{"address":"ffff19b0","evidence":[{"at":"jk78c:00092faa","count":1,"kind":"masked-match","note":"Three-generation '
                                        'homologous fail-safe branch reads this bounded '
                                        'request","supports":"homology","to":"7mfk:0007378a","value":52}],"layout":"jk78c"}],"width":16}',
                'original_ledger_json': '[{"dependency":[{"end":"owner","relies":"level","role":"consumer","supports":"identity","to":"primary_request_inverse_lookup/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"request_coordinate_coordinator/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"strange-angelfish/fn","type":"reader"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"signed_request_boundary/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5,6],"notes":[1],"order":111,"registry":"vars","storage_description":"signed '
                                        'internal request"}]',
                'proposed_ledger_json': '[{"dependency":[{"end":"owner","relies":"level","role":"consumer","supports":"identity","to":"primary_request_inverse_lookup/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"request_coordinate_coordinator/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"strange-angelfish/fn","type":"reader"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"signed_request_boundary/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5,6],"notes":[1],"order":111,"registry":"vars","storage_description":"signed '
                                        'internal request"}]',
                'original_symbol_evidence_json': '[{"at":"7mfk:000734a8","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"at":"7mfk:000734f4","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"at":"7mfk:000735ca","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"at":"7mfk:000791a8","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"at":"7mfk:000791b2","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000730fc","00073432","00073628","00079030","00079dd8","ffff19c6"],"span":1}},{"kind":"trace","relies":"structure","supports":"identity","to":"request_coordinate_coordinator/fn/7mfk"},{"kind":"trace","relies":"structure","supports":"identity","to":"request_boundary_dispatch/fn/7mfk"}]',
                'evidence_json': '{"at":"7mfk:00079dd8","key":"request-boundary-publication-access-v1:jk08a:delegated-19c6-writer","kind":"indirect","mode":"request-boundary-publication-access","note":"Exact '
                                 'executed complete dispatcher and live signed-bound word publication; '
                                 'native types and all retained facts remain '
                                 'fixed.","path":"defs/JK08A.request-boundary-publication-claims.toml","supports":"identity","value":{"actual_store_sites":[496040,496050],"actual_writer":495664,"component":"request_boundary_publication_paths","direction":"writer","entry":499160,"function":"7mfk:00079dd8","hardware_qualification":false,"native_address":4294908358,"native_geometry_inference":false,"natural_scheduling_inference":false,"original_claim_sha256":"5c055da500054f344db4f5900a11104adab441204d39be660269dfd02f3614b1","owner":"throttle_request_bounded/ram","real_call":{"return_address":499166,"site":499162,"target":497616},"real_tail":{"PR_restore_delay":499170,"site":499168,"target":495664},"scale_admission":false,"scope":"exact-delegated-request-publication","units_admission":false,"width_bytes":2}}'}],
 'retained_functions': [{'owner': 'request_boundary_dispatch/fn',
                         'address': 499160,
                         'source': 'kb/fn/request_boundary_dispatch.toml',
                         'native_json': '{"block":"torque_request/block","ledger":[{"fields":["name"],"order":131,"registry":"curated","title":true},{"dependency":[{"end":"owner","link_role":"consumer","relies":"structure","role":"consumer","supports":"identity","to":"acoustic-spaniel/fn","type":"depends"},{"end":"owner","link_role":"consumer","relies":"structure","role":"consumer","supports":"identity","to":"signed_request_boundary/fn","type":"depends"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"throttle_request_bounded/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1],"notes":[0],"order":520,"registry":"funcs"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","role":"consumer","supports":"identity","to":"acoustic-spaniel/fn","type":"depends"},{"layouts":["7mfk"],"relies":"structure","role":"consumer","supports":"identity","to":"signed_request_boundary/fn","type":"depends"}],"note":["This '
                                        'is the scheduling bridge from the selected signed limit to '
                                        'downstream inverse-coordinate '
                                        'calculations."],"role":"dispatch","summary":"Periodic-table '
                                        'index-21 request-boundary coordinator. It calls 000797d0 and then '
                                        'signed boundary stage 00079030, which publishes shared request '
                                        'coordinate ffff19c6 before index-22 '
                                        'consumers.","symbol":[{"address":"00079dd8","evidence":[{"at":"7mfk:000219c4","kind":"rom-bytes","supports":"identity","value":"00079dd8"},{"kind":"trace","relies":"structure","supports":"identity","to":"coherent_snapshot/fn/7mfk"}],"layout":"7mfk"}],"title":"Run '
                                        'the periodic signed request-boundary stages"}',
                         'native_sha256': '32349ed4d9a59cf093cfcf0b4e56b6fb9ecb8bd14afa3a31f5b0b6ff096a732e'},
                        {'owner': 'acoustic-spaniel/fn',
                         'address': 497616,
                         'source': 'kb/fn/acoustic-spaniel.toml',
                         'native_json': '{"symbol":[{"address":"000797d0","evidence":[{"at":"7mfk:000797d0","kind":"l0","supports":"identity"}],"layout":"7mfk","name":"acoustic-spaniel"}]}',
                         'native_sha256': '8744a0def48ac695b1e9779c18db03ed49bf0692a4c22cd21f2083ac6bdccffe'},
                        {'owner': 'signed_request_boundary/fn',
                         'address': 495664,
                         'source': 'kb/fn/signed_request_boundary.toml',
                         'native_json': '{"block":"torque_request/block","ledger":[{"fields":["name"],"order":132,"registry":"curated","title":true},{"dependency":[{"end":"owner","link_role":"consumer","relies":"structure","role":"consumer","supports":"identity","to":"adorable-shrew/ram","type":"depends"},{"end":"owner","link_role":"consumer","relies":"structure","role":"consumer","supports":"identity","to":"elegant-marmoset/ram","type":"depends"},{"end":"owner","link_role":"consumer","relies":"level","role":"consumer","supports":"identity","to":"primary_request_inverse_lookup/fn","type":"depends"},{"end":"owner","link_role":"consumer","relies":"structure","role":"consumer","supports":"identity","to":"strange-angelfish/fn","type":"depends"},{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"amber-urchin/ram","type":"reader"},{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"outstanding-badger/ram","type":"reader"},{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"spicy-smilodon/ram","type":"reader"},{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"wakeful-lemur/ram","type":"reader"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"holistic-doberman/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"throttle_request_bounded/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7,8,9,10,11],"notes":[0],"order":239,"registry":"funcs"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","role":"consumer","supports":"identity","to":"adorable-shrew/ram","type":"depends"},{"layouts":["7mfk"],"relies":"structure","role":"consumer","supports":"identity","to":"elegant-marmoset/ram","type":"depends"},{"layouts":["7mfk"],"relies":"level","role":"consumer","supports":"identity","to":"primary_request_inverse_lookup/fn","type":"depends"},{"layouts":["7mfk"],"relies":"structure","role":"consumer","supports":"identity","to":"strange-angelfish/fn","type":"depends"}],"note":["This '
                                        'closes the signed-request boundary before stock-active inverse '
                                        'coordinate ffff198a. ffff4162 can reach this function only through '
                                        'ffff3480/ffff3484 while ffff41a6.bit3 is set; the selected '
                                        'stock-lifecycle path clears that bit before publication. Exact code '
                                        'continues through ffff183e, ffff19b2, per-channel targets, the '
                                        'regulator, and ATU-II BFR6A-D; physical scale, plate response, bank '
                                        'identity, and ECM terminals require hardware evidence. The function '
                                        'also writes ffff415e and ffff4160, the limited and pre-limiter '
                                        'requests clamped to [ffff413a, ffff4138]; CAN packer 00079e70 '
                                        'scales their scheduler latches exactly as net engine torque, which '
                                        'places this request coordinate in the torque '
                                        'domain."],"role":"driver","summary":"Signed request-boundary stage '
                                        'reached by periodic-table index-21 dispatcher 00079dd8. It reads '
                                        'duplicated controller selection ffff2438/ffff19c2, applies '
                                        'mode-controlled lower and upper bounds from several independent '
                                        'signed candidates, including transmission-completion bounds '
                                        'ffff347e, ffff3480, ffff3482, and ffff3484, and writes bounded '
                                        'outputs including ffff19cc and ffff19c6. FUN 00073432 and FUN '
                                        '00073628 consume ffff19c6 in downstream interpolation '
                                        'branches.","symbol":[{"address":"00079030","evidence":[{"at":"7mfk:000219c4","kind":"rom-bytes","supports":"identity","value":"00079dd8"},{"at":"7mfk:0007904e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000219c4","00073432","00073628","00079030","00079dd8","ffff19c2","ffff19c6","ffff19cc","ffff2438","ffff347e","ffff3480","ffff3482","ffff3484"],"span":1}},{"at":"7mfk:00079054","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000219c4","00073432","00073628","00079030","00079dd8","ffff19c2","ffff19c6","ffff19cc","ffff2438","ffff347e","ffff3480","ffff3482","ffff3484"],"span":1}},{"at":"7mfk:000790ee","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000219c4","00073432","00073628","00079030","00079dd8","ffff19c2","ffff19c6","ffff19cc","ffff2438","ffff347e","ffff3480","ffff3482","ffff3484"],"span":1}},{"at":"7mfk:00079114","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000219c4","00073432","00073628","00079030","00079dd8","ffff19c2","ffff19c6","ffff19cc","ffff2438","ffff347e","ffff3480","ffff3482","ffff3484"],"span":1}},{"at":"7mfk:00079122","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000219c4","00073432","00073628","00079030","00079dd8","ffff19c2","ffff19c6","ffff19cc","ffff2438","ffff347e","ffff3480","ffff3482","ffff3484"],"span":1}},{"at":"7mfk:0007914a","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000219c4","00073432","00073628","00079030","00079dd8","ffff19c2","ffff19c6","ffff19cc","ffff2438","ffff347e","ffff3480","ffff3482","ffff3484"],"span":1}},{"at":"7mfk:0007914e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000219c4","00073432","00073628","00079030","00079dd8","ffff19c2","ffff19c6","ffff19cc","ffff2438","ffff347e","ffff3480","ffff3482","ffff3484"],"span":1}},{"at":"7mfk:0007915c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000219c4","00073432","00073628","00079030","00079dd8","ffff19c2","ffff19c6","ffff19cc","ffff2438","ffff347e","ffff3480","ffff3482","ffff3484"],"span":1}},{"at":"7mfk:000791a8","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000219c4","00073432","00073628","00079030","00079dd8","ffff19c2","ffff19c6","ffff19cc","ffff2438","ffff347e","ffff3480","ffff3482","ffff3484"],"span":1}},{"at":"7mfk:000791b2","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000219c4","00073432","00073628","00079030","00079dd8","ffff19c2","ffff19c6","ffff19cc","ffff2438","ffff347e","ffff3480","ffff3482","ffff3484"],"span":1}},{"kind":"trace","relies":"structure","supports":"identity","to":"request_boundary_dispatch/fn/7mfk"}],"layout":"7mfk"}],"title":"Apply '
                                        'signed request bounds and publish the shared coordinate"}',
                         'native_sha256': '8382c1a591976904d84537ea7af615dc38c689cf401e566c3b6d239c60561fe5'}]}
IDENTITIES=(('delegated-19c6-writer',
  4294908358,
  'throttle_request_bounded/ram',
  499160,
  (496040, 496050),
  'writer',
  'request_boundary_publication_paths',
  2,
  16,
  'unset',
  '5c055da500054f344db4f5900a11104adab441204d39be660269dfd02f3614b1',
  'c99295a19bb4c8750c68686ce7bf424d772248124ab0bd65db702face3621274',
  'a4262424b9ff24dfc559411564814210ada40f59f9e8e6c9e51fd42de5e17181',
  '6932de17f48c4b0ff58a07e73ecef4436ec04de472c3cc6cbdf5df26b5f5ef46'),)

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):raise ValueError('the delegated writer claim changes its exact retained native/function/type/evidence/TEST boundary')
    row=value['reference'][0];old=json.loads(row['original_claim_json']);new=json.loads(row['proposed_claim_json'])
    expected=deepcopy(old);expected['evidence'].append(item(row))
    before=json.loads(row['original_native_json']);after=deepcopy(before)
    links=[r for r in after['link'] if (r['type'],r['to'])==('writer','request_boundary_dispatch/fn')]
    if len(links)!=1:raise ValueError('the delegated writer claim loses its unique retained delegated writer')
    links[0].setdefault('evidence',[]).append(item(row))
    if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
            or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
            or not test_contract.exact(new,expected) or not test_contract.exact(after,json.loads(row['proposed_native_json']))):
        raise ValueError('the delegated writer claim changes more than its single exact owning append')
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
        raise ValueError('the delegated writer attachment requires its one exact complete normal owning link operation')
    return True
def looks_like_access(link):
    return any(registered(e) for e in link.evidence) or (link.owner.key,link.type,link.to.key)==('throttle_request_bounded/ram','writer','request_boundary_dispatch/fn')
