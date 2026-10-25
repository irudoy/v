"""One exact retained primary ratio and state quantity relation and complete owning append."""
from copy import deepcopy
from pathlib import Path
import json,tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,plain
from kb.model import SymbolKey
DESCRIPTOR='defs/JK08A.ratio-state-quantity-claims.toml'
MODE='ratio-state-quantity-access'
PREFIX='ratio-state-quantity-access-v1:jk08a:'
DECLARED={'schema': 1,
 'id': 'jk08a-ratio-state-quantity-claims',
 'layout': '7mfk',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'One retained primary ratio and state quantity reader; no consumer instruction-level ROM-read '
          'attribution.',
 'native_function_publication': False,
 'native_geometry_publication': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'reference': [{'id': 'retained-15770-consumer',
                'address': 87920,
                'owner': 'vigilant-rat/tbl',
                'function': 484684,
                'sites': [484712],
                'direction': 'reader',
                'source': 'kb/tbl/vigilant-rat.toml',
                'component': 'ratio_state_quantity_paths',
                'width_bytes': 2,
                'declared_width': 'unset',
                'declared_signed': 'unset',
                'original_claim_sha256': '856f2bada9b060e1955f0cb21918ac97da02b238ab7aa2a020f889afabd6cdcc',
                'original_claim_json': '{"evidence":[],"layout":"7mfk","offset":null,"owner":"vigilant-rat/tbl","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/tbl/vigilant-rat.toml"],"stated":["7mfk"],"to":"spiritual-alligator/fn","type":"reader"}',
                'proposed_claim_sha256': 'b32bd55c64652aff626411b0b062d00136e7f63135ec86a68d789621b4a2bb60',
                'proposed_claim_json': '{"evidence":[{"at":"7mfk:00076568","key":"ratio-state-quantity-access-v1:jk08a:retained-15770-consumer","kind":"indirect","mode":"ratio-state-quantity-access","note":"Exact '
                                       'table-derived primary ratio publication and signed state consumer '
                                       'with complete actual RAM continuity; all native facts and semantic '
                                       'types remain '
                                       'fixed.","path":"defs/JK08A.ratio-state-quantity-claims.toml","supports":"identity","value":{"actual_outputs":[{"address":4294906970,"site":484788,"width_bytes":2},{"address":4294907772,"site":485162,"width_bytes":2}],"complete_RAM_calibration_bound_continuity":true,"component":"ratio_state_quantity_paths","consumer_entry":484684,"consumer_reads":[{"address":4294908322,"site":484712,"width_bytes":2}],"direction":"reader","function":"7mfk:0007654c","hardware_qualification":false,"native_address":87920,"native_geometry_inference":false,"natural_scheduling_inference":false,"original_claim_sha256":"856f2bada9b060e1955f0cb21918ac97da02b238ab7aa2a020f889afabd6cdcc","owner":"vigilant-rat/tbl","producer_entry":479604,"producer_store":{"address":4294908322,"site":479748,"width_bytes":2},"scale_admission":false,"scope":"exact-two-phase-ratio-state-quantity","units_admission":false,"width_bytes":2}}],"layout":"7mfk","offset":null,"owner":"vigilant-rat/tbl","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/tbl/vigilant-rat.toml"],"stated":["7mfk"],"to":"spiritual-alligator/fn","type":"reader"}',
                'original_native_sha256': '187a097b5649112113b22d3a986179eb02cba429e31dc3a16c20ebb8855621b2',
                'original_native_json': '{"access":"explicit","editor":{"category":"Internal '
                                        'Calculations","coarse":0.00976563,"emit":false,"fine":0.000976563,"format":"0.000000","name":"Protected '
                                        'Division Denominator - catalog torque-ratio scale '
                                        '(0x15770)","order":127},"ledger":[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"crouching-shrew/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"grinning-walrus/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"pedal_request_scaler/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"proficient-sunfish/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"spiritual-alligator/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"splendid-beaver/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"wine-collie/fn","type":"reader"}],"fields":["confidence","role","semantics","units","scale_expr","to_byte","scale_conf"],"identity":[0,1,2,3,4,5,6,7,8],"notes":[0],"order":311,"registry":"findings","scale":[9,10]}],"level":"candidate","link":[{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"crouching-shrew/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"grinning-walrus/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"pedal_request_scaler/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"proficient-sunfish/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"spiritual-alligator/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"splendid-beaver/fn","type":"reader"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","to":"striped-kakapo/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"wine-collie/fn","type":"reader"}],"note":["Range '
                                        '1024..1884, monotonic decrease toward 1024, an implicit normalized '
                                        'axis, and use of the result as a divisor are consistent with two '
                                        'catalog variants of Torque Converter Torque Ratio Table. Code '
                                        'proves the full chain to arithmetic consumption but does not '
                                        'identify the physical input ratio or consumer quantities, so the '
                                        'claim and scale remain candidate. The artifact has no separately '
                                        'addressable axis. Blocking condition: The trace stops at 00021bbc: '
                                        'consumers 00074b04, 00075306, 000718d8, 00071a10, 00071b7e, '
                                        '0007654c, and 000ceabc prove use of ffff19a2 as a zero-protected '
                                        'divisor, but the artifact does not link the numerators or division '
                                        'results to torque and torque-converter speeds. Physical semantics '
                                        'and multiplier 0.000976563 are confirmed only by the catalog. '
                                        'Promotion rejected: Attribution is supported by the machine chain: '
                                        '000751f6 loads address 00015770 into r4, 000751fc calls table '
                                        'wrapper 000263f4, 00075200 copies return value r0, and 00075204 '
                                        'writes a word to ffff19a2. The table-wrapper call and reads of '
                                        'adjacent uint16 cells at 00026aa0 and 00026aa2 confirm role=table. '
                                        'Disposition=consumer is supported by the structural set of seven '
                                        'ffff19a2 readers. The promoted semantics and its code evidence are '
                                        'disproven: the kernel listing ends immediately after reading two '
                                        'cells and does not show interpolation arithmetic through r0, while '
                                        'machine listings for the seven consumers are absent. Because of the '
                                        'nonstandard register contract, the shown C pseudocode does not '
                                        'reconstruct arguments to 00021bbc by itself. In five pseudocode '
                                        'listings, ffff19a2 appears only in a zero test, while in 00074b04 '
                                        'and 0007654c it appears in neither pseudocode nor expression '
                                        'tables. Those two functions show 000224fa before 00021bbc, so the '
                                        'artifact does not establish whether the divisor is the raw output, '
                                        'its shifted derivative, or another quantity. A complete machine '
                                        'trace for all seven consumers is absent. No separate scale or scale '
                                        'evidence is claimed. Result disposition: '
                                        'consumer."],"role":"table","scale":"x*0.000976563","scale_level":"candidate","summary":"The '
                                        'interpolated uint16 output is written to ffff19a2 and used as a '
                                        'zero-protected divisor for call 00021bbc in the seven shown '
                                        'consumers.","symbol":[{"address":"00015770","evidence":[{"at":"7mfk:00026aa0","kind":"unverified-site","supports":"identity"},{"at":"7mfk:00026aa2","kind":"unverified-site","supports":"identity"},{"at":"7mfk:000751f6","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00015770","00021bbc","000224fa","000263f4","000718d8","00071a10","00071b7e","00074b04","00075306","0007654c","000ceabc"],"span":1}},{"at":"7mfk:000751fc","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00015770","00021bbc","000224fa","000263f4","000718d8","00071a10","00071b7e","00074b04","00075306","0007654c","000ceabc"],"span":1}},{"at":"7mfk:00075200","key":"linked","kind":"l0-context","supports":"identity","value":{"named":["00015770","00021bbc","000224fa","000263f4","000718d8","00071a10","00071b7e","00074b04","00075306","0007654c","000ceabc"],"span":1}},{"at":"7mfk:00075204","key":"linked","kind":"l0-context","supports":"identity","value":{"named":["00015770","00021bbc","000224fa","000263f4","000718d8","00071a10","00071b7e","00074b04","00075306","0007654c","000ceabc"],"span":1}},{"kind":"trace","relies":"contract","supports":"identity","to":"pompous-firefly/fn/7mfk"},{"kind":"trace","relies":"contract","supports":"identity","to":"illustrious-vulture/fn/7mfk"},{"kind":"trace","relies":"structure","supports":"identity","to":"dramatic-okapi/fn/7mfk"},{"kind":"registry","supports":"scale","value":"Torque '
                                        'Converter Torque Ratio Table 2 scale '
                                        'x*0.000976563"},{"kind":"registry","supports":"scale","value":"Torque '
                                        'Converter Torque Ratio Table scale '
                                        'x*0.000976563"}],"layout":"7mfk","name":"vigilant-rat"},{"address":"00017c72","evidence":[{"at":"jk00c:000779a0","count":1,"kind":"call-ordinal","note":"reviewed '
                                        'JK08A-to-JK00D operands composed with unique JK00D-to-JK00C '
                                        'interpolation '
                                        'operands","supports":"homology","to":"7mfk:000751fc","value":1}],"layout":"jk00c","name":"intelligent-kangaroo"},{"address":"00017c92","evidence":[{"at":"jk00d:000779a0","count":1,"kind":"call-ordinal","note":"unique '
                                        'call-ordinal operands through reviewed interpolation-wrapper '
                                        'correspondence","supports":"homology","to":"7mfk:000751fc","value":1}],"layout":"jk00d","name":"gay-cow"}],"to_raw":"x/0.000976563","unit":"Torque '
                                        'Ratio"}',
                'proposed_native_sha256': '8910241e368a5bc0d0425a43f2573311adf76526b163f1990966413f631919ad',
                'proposed_native_json': '{"access":"explicit","editor":{"category":"Internal '
                                        'Calculations","coarse":0.00976563,"emit":false,"fine":0.000976563,"format":"0.000000","name":"Protected '
                                        'Division Denominator - catalog torque-ratio scale '
                                        '(0x15770)","order":127},"ledger":[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"crouching-shrew/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"grinning-walrus/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"pedal_request_scaler/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"proficient-sunfish/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"spiritual-alligator/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"splendid-beaver/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"wine-collie/fn","type":"reader"}],"fields":["confidence","role","semantics","units","scale_expr","to_byte","scale_conf"],"identity":[0,1,2,3,4,5,6,7,8],"notes":[0],"order":311,"registry":"findings","scale":[9,10]}],"level":"candidate","link":[{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"crouching-shrew/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"grinning-walrus/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"pedal_request_scaler/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"proficient-sunfish/fn","type":"reader"},{"evidence":[{"at":"7mfk:00076568","key":"ratio-state-quantity-access-v1:jk08a:retained-15770-consumer","kind":"indirect","mode":"ratio-state-quantity-access","note":"Exact '
                                        'table-derived primary ratio publication and signed state consumer '
                                        'with complete actual RAM continuity; all native facts and semantic '
                                        'types remain '
                                        'fixed.","path":"defs/JK08A.ratio-state-quantity-claims.toml","supports":"identity","value":{"actual_outputs":[{"address":4294906970,"site":484788,"width_bytes":2},{"address":4294907772,"site":485162,"width_bytes":2}],"complete_RAM_calibration_bound_continuity":true,"component":"ratio_state_quantity_paths","consumer_entry":484684,"consumer_reads":[{"address":4294908322,"site":484712,"width_bytes":2}],"direction":"reader","function":"7mfk:0007654c","hardware_qualification":false,"native_address":87920,"native_geometry_inference":false,"natural_scheduling_inference":false,"original_claim_sha256":"856f2bada9b060e1955f0cb21918ac97da02b238ab7aa2a020f889afabd6cdcc","owner":"vigilant-rat/tbl","producer_entry":479604,"producer_store":{"address":4294908322,"site":479748,"width_bytes":2},"scale_admission":false,"scope":"exact-two-phase-ratio-state-quantity","units_admission":false,"width_bytes":2}}],"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"spiritual-alligator/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"splendid-beaver/fn","type":"reader"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","to":"striped-kakapo/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"wine-collie/fn","type":"reader"}],"note":["Range '
                                        '1024..1884, monotonic decrease toward 1024, an implicit normalized '
                                        'axis, and use of the result as a divisor are consistent with two '
                                        'catalog variants of Torque Converter Torque Ratio Table. Code '
                                        'proves the full chain to arithmetic consumption but does not '
                                        'identify the physical input ratio or consumer quantities, so the '
                                        'claim and scale remain candidate. The artifact has no separately '
                                        'addressable axis. Blocking condition: The trace stops at 00021bbc: '
                                        'consumers 00074b04, 00075306, 000718d8, 00071a10, 00071b7e, '
                                        '0007654c, and 000ceabc prove use of ffff19a2 as a zero-protected '
                                        'divisor, but the artifact does not link the numerators or division '
                                        'results to torque and torque-converter speeds. Physical semantics '
                                        'and multiplier 0.000976563 are confirmed only by the catalog. '
                                        'Promotion rejected: Attribution is supported by the machine chain: '
                                        '000751f6 loads address 00015770 into r4, 000751fc calls table '
                                        'wrapper 000263f4, 00075200 copies return value r0, and 00075204 '
                                        'writes a word to ffff19a2. The table-wrapper call and reads of '
                                        'adjacent uint16 cells at 00026aa0 and 00026aa2 confirm role=table. '
                                        'Disposition=consumer is supported by the structural set of seven '
                                        'ffff19a2 readers. The promoted semantics and its code evidence are '
                                        'disproven: the kernel listing ends immediately after reading two '
                                        'cells and does not show interpolation arithmetic through r0, while '
                                        'machine listings for the seven consumers are absent. Because of the '
                                        'nonstandard register contract, the shown C pseudocode does not '
                                        'reconstruct arguments to 00021bbc by itself. In five pseudocode '
                                        'listings, ffff19a2 appears only in a zero test, while in 00074b04 '
                                        'and 0007654c it appears in neither pseudocode nor expression '
                                        'tables. Those two functions show 000224fa before 00021bbc, so the '
                                        'artifact does not establish whether the divisor is the raw output, '
                                        'its shifted derivative, or another quantity. A complete machine '
                                        'trace for all seven consumers is absent. No separate scale or scale '
                                        'evidence is claimed. Result disposition: '
                                        'consumer."],"role":"table","scale":"x*0.000976563","scale_level":"candidate","summary":"The '
                                        'interpolated uint16 output is written to ffff19a2 and used as a '
                                        'zero-protected divisor for call 00021bbc in the seven shown '
                                        'consumers.","symbol":[{"address":"00015770","evidence":[{"at":"7mfk:00026aa0","kind":"unverified-site","supports":"identity"},{"at":"7mfk:00026aa2","kind":"unverified-site","supports":"identity"},{"at":"7mfk:000751f6","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00015770","00021bbc","000224fa","000263f4","000718d8","00071a10","00071b7e","00074b04","00075306","0007654c","000ceabc"],"span":1}},{"at":"7mfk:000751fc","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00015770","00021bbc","000224fa","000263f4","000718d8","00071a10","00071b7e","00074b04","00075306","0007654c","000ceabc"],"span":1}},{"at":"7mfk:00075200","key":"linked","kind":"l0-context","supports":"identity","value":{"named":["00015770","00021bbc","000224fa","000263f4","000718d8","00071a10","00071b7e","00074b04","00075306","0007654c","000ceabc"],"span":1}},{"at":"7mfk:00075204","key":"linked","kind":"l0-context","supports":"identity","value":{"named":["00015770","00021bbc","000224fa","000263f4","000718d8","00071a10","00071b7e","00074b04","00075306","0007654c","000ceabc"],"span":1}},{"kind":"trace","relies":"contract","supports":"identity","to":"pompous-firefly/fn/7mfk"},{"kind":"trace","relies":"contract","supports":"identity","to":"illustrious-vulture/fn/7mfk"},{"kind":"trace","relies":"structure","supports":"identity","to":"dramatic-okapi/fn/7mfk"},{"kind":"registry","supports":"scale","value":"Torque '
                                        'Converter Torque Ratio Table 2 scale '
                                        'x*0.000976563"},{"kind":"registry","supports":"scale","value":"Torque '
                                        'Converter Torque Ratio Table scale '
                                        'x*0.000976563"}],"layout":"7mfk","name":"vigilant-rat"},{"address":"00017c72","evidence":[{"at":"jk00c:000779a0","count":1,"kind":"call-ordinal","note":"reviewed '
                                        'JK08A-to-JK00D operands composed with unique JK00D-to-JK00C '
                                        'interpolation '
                                        'operands","supports":"homology","to":"7mfk:000751fc","value":1}],"layout":"jk00c","name":"intelligent-kangaroo"},{"address":"00017c92","evidence":[{"at":"jk00d:000779a0","count":1,"kind":"call-ordinal","note":"unique '
                                        'call-ordinal operands through reviewed interpolation-wrapper '
                                        'correspondence","supports":"homology","to":"7mfk:000751fc","value":1}],"layout":"jk00d","name":"gay-cow"}],"to_raw":"x/0.000976563","unit":"Torque '
                                        'Ratio"}',
                'original_ledger_json': '[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"crouching-shrew/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"grinning-walrus/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"pedal_request_scaler/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"proficient-sunfish/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"spiritual-alligator/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"splendid-beaver/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"wine-collie/fn","type":"reader"}],"fields":["confidence","role","semantics","units","scale_expr","to_byte","scale_conf"],"identity":[0,1,2,3,4,5,6,7,8],"notes":[0],"order":311,"registry":"findings","scale":[9,10]}]',
                'proposed_ledger_json': '[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"crouching-shrew/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"grinning-walrus/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"pedal_request_scaler/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"proficient-sunfish/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"spiritual-alligator/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"splendid-beaver/fn","type":"reader"},{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"wine-collie/fn","type":"reader"}],"fields":["confidence","role","semantics","units","scale_expr","to_byte","scale_conf"],"identity":[0,1,2,3,4,5,6,7,8],"notes":[0],"order":311,"registry":"findings","scale":[9,10]}]',
                'original_symbol_evidence_json': '[{"at":"7mfk:00026aa0","kind":"unverified-site","supports":"identity"},{"at":"7mfk:00026aa2","kind":"unverified-site","supports":"identity"},{"at":"7mfk:000751f6","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00015770","00021bbc","000224fa","000263f4","000718d8","00071a10","00071b7e","00074b04","00075306","0007654c","000ceabc"],"span":1}},{"at":"7mfk:000751fc","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00015770","00021bbc","000224fa","000263f4","000718d8","00071a10","00071b7e","00074b04","00075306","0007654c","000ceabc"],"span":1}},{"at":"7mfk:00075200","key":"linked","kind":"l0-context","supports":"identity","value":{"named":["00015770","00021bbc","000224fa","000263f4","000718d8","00071a10","00071b7e","00074b04","00075306","0007654c","000ceabc"],"span":1}},{"at":"7mfk:00075204","key":"linked","kind":"l0-context","supports":"identity","value":{"named":["00015770","00021bbc","000224fa","000263f4","000718d8","00071a10","00071b7e","00074b04","00075306","0007654c","000ceabc"],"span":1}},{"kind":"trace","relies":"contract","supports":"identity","to":"pompous-firefly/fn/7mfk"},{"kind":"trace","relies":"contract","supports":"identity","to":"illustrious-vulture/fn/7mfk"},{"kind":"trace","relies":"structure","supports":"identity","to":"dramatic-okapi/fn/7mfk"},{"kind":"registry","supports":"scale","value":"Torque '
                                                 'Converter Torque Ratio Table 2 scale '
                                                 'x*0.000976563"},{"kind":"registry","supports":"scale","value":"Torque '
                                                 'Converter Torque Ratio Table scale x*0.000976563"}]',
                'evidence_json': '{"at":"7mfk:00076568","key":"ratio-state-quantity-access-v1:jk08a:retained-15770-consumer","kind":"indirect","mode":"ratio-state-quantity-access","note":"Exact '
                                 'table-derived primary ratio publication and signed state consumer with '
                                 'complete actual RAM continuity; all native facts and semantic types remain '
                                 'fixed.","path":"defs/JK08A.ratio-state-quantity-claims.toml","supports":"identity","value":{"actual_outputs":[{"address":4294906970,"site":484788,"width_bytes":2},{"address":4294907772,"site":485162,"width_bytes":2}],"complete_RAM_calibration_bound_continuity":true,"component":"ratio_state_quantity_paths","consumer_entry":484684,"consumer_reads":[{"address":4294908322,"site":484712,"width_bytes":2}],"direction":"reader","function":"7mfk:0007654c","hardware_qualification":false,"native_address":87920,"native_geometry_inference":false,"natural_scheduling_inference":false,"original_claim_sha256":"856f2bada9b060e1955f0cb21918ac97da02b238ab7aa2a020f889afabd6cdcc","owner":"vigilant-rat/tbl","producer_entry":479604,"producer_store":{"address":4294908322,"site":479748,"width_bytes":2},"scale_admission":false,"scope":"exact-two-phase-ratio-state-quantity","units_admission":false,"width_bytes":2}}'}],
 'retained_functions': [{'owner': 'striped-kakapo/fn',
                         'address': 479604,
                         'source': 'kb/fn/striped-kakapo.toml',
                         'native_json': '{"block":"torque_request/block","ledger":[{"dependency":[{"end":"owner","link_role":"consumer","relies":"structure","role":"consumer","supports":"identity","to":"pedal_request_scaler/fn","type":"depends"},{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"vigilant-rat/tbl","type":"reader"},{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"fragrant-hippo/ram","type":"reader"},{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"khaki-antelope/ram","type":"reader"},{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"wild-chinchilla/ram","type":"reader"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"artichoke-tarantula/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"lush-viper/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"warping-albatross/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7,8,9,10,11,12,13],"notes":[0],"order":689,"registry":"funcs"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","role":"consumer","supports":"identity","to":"pedal_request_scaler/fn","type":"depends"}],"note":["Entry '
                                        '10 of the 124-entry periodic table at 0002196c calls it; L0 records '
                                        'no direct caller. With ffff1702 in RPM/3.125 counts, '
                                        'floor(25*ffff1702/8) is the engine speed in RPM, so ffff17e2 is '
                                        '61440 times the smaller of ffff10d6 and ffff1582 per RPM. L0 '
                                        'records no writer of ffff10d6, and the physical quantities of both '
                                        'inputs and of the ratio are unresolved. Pedal-request scaler '
                                        '00075306 and the six other consumers that the 00015770 map row '
                                        'lists use ffff19a2 as a zero-protected '
                                        'divisor."],"role":"accessor","summary":"Primary torque-ratio lookup '
                                        'of the requested-torque conversion. While row coordinate ffff1702 '
                                        'is nonzero it writes ffff17e2=min(0xffff, floor(61440*min(ffff10d6, '
                                        'ffff1582)/floor(25*ffff1702/8))), otherwise 0xffff; it scales '
                                        'ffff17e2 by ROM16[0000920e]/32768 with saturation into ffff16b2 and '
                                        'writes lookup(00015770, ffff16b2) to '
                                        'ffff19a2.","symbol":[{"address":"00075174","evidence":[{"kind":"unbound-constant","supports":"identity","value":"0000920e=0x9719"},{"at":"7mfk:00021994","kind":"rom-bytes","supports":"identity","value":"00075174"},{"at":"7mfk:0007517e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000920e","00015770","00021994","00021ce0","000263f4","00075174","00075306","ffff10d6","ffff1582","ffff16b2","ffff1702","ffff17e2","ffff19a2"],"span":1}},{"at":"7mfk:0007518a","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000920e","00015770","00021994","00021ce0","000263f4","00075174","00075306","ffff10d6","ffff1582","ffff16b2","ffff1702","ffff17e2","ffff19a2"],"span":1}},{"at":"7mfk:00075190","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000920e","00015770","00021994","00021ce0","000263f4","00075174","00075306","ffff10d6","ffff1582","ffff16b2","ffff1702","ffff17e2","ffff19a2"],"span":1}},{"at":"7mfk:000751c0","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000920e","00015770","00021994","00021ce0","000263f4","00075174","00075306","ffff10d6","ffff1582","ffff16b2","ffff1702","ffff17e2","ffff19a2"],"span":1}},{"at":"7mfk:000751da","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000920e","00015770","00021994","00021ce0","000263f4","00075174","00075306","ffff10d6","ffff1582","ffff16b2","ffff1702","ffff17e2","ffff19a2"],"span":1}},{"at":"7mfk:000751dc","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000920e","00015770","00021994","00021ce0","000263f4","00075174","00075306","ffff10d6","ffff1582","ffff16b2","ffff1702","ffff17e2","ffff19a2"],"span":1}},{"at":"7mfk:000751f6","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000920e","00015770","00021994","00021ce0","000263f4","00075174","00075306","ffff10d6","ffff1582","ffff16b2","ffff1702","ffff17e2","ffff19a2"],"span":1}},{"at":"7mfk:000751fa","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000920e","00015770","00021994","00021ce0","000263f4","00075174","00075306","ffff10d6","ffff1582","ffff16b2","ffff1702","ffff17e2","ffff19a2"],"span":1}},{"at":"7mfk:000751fc","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000920e","00015770","00021994","00021ce0","000263f4","00075174","00075306","ffff10d6","ffff1582","ffff16b2","ffff1702","ffff17e2","ffff19a2"],"span":1}},{"at":"7mfk:00075204","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0000920e","00015770","00021994","00021ce0","000263f4","00075174","00075306","ffff10d6","ffff1582","ffff16b2","ffff1702","ffff17e2","ffff19a2"],"span":1}},{"kind":"trace","relies":"structure","supports":"identity","to":"unsigned_divide/fn/7mfk"},{"kind":"trace","relies":"structure","supports":"identity","to":"dramatic-okapi/fn/7mfk"}],"layout":"7mfk","name":"striped-kakapo"}]}',
                         'native_sha256': '6f0b58c8ff2007b5776aed4f6271c9a8a6b21f067c1613a871a4be2cfa65dc83'},
                        {'owner': 'spiritual-alligator/fn',
                         'address': 484684,
                         'source': 'kb/fn/spiritual-alligator.toml',
                         'native_json': '{"block":"torque_request/block","ledger":[{"dependency":[{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"apricot-angelfish/tbl","type":"reader"},{"end":"owner","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"resilient-mongoose/axis","type":"depends"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7],"notes":[0],"order":236,"registry":"funcs"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","role":"indexed_by","supports":"identity","to":"resilient-mongoose/axis","type":"depends"}],"note":["The '
                                        'map has code-level x-32768 scaling. The physical quantity of '
                                        'ffff1792 is unresolved."],"role":"accessor","summary":"Accessor for '
                                        '0x15276: interpolated uint16 M is converted as M-32768 and written '
                                        'to '
                                        'ffff1792.","symbol":[{"address":"0007654c","evidence":[{"at":"7mfk:000765b8","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00015276","00015286","000264cc","00026740","0007654c"],"span":1}},{"at":"7mfk:000765c2","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00015276","00015286","000264cc","00026740","0007654c"],"span":1}},{"at":"7mfk:000765c6","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00015276","00015286","000264cc","00026740","0007654c"],"span":1}},{"at":"7mfk:000765ca","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00015276","00015286","000264cc","00026740","0007654c"],"span":1}},{"at":"7mfk:000765ce","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00015276","00015286","000264cc","00026740","0007654c"],"span":1}},{"at":"7mfk:000765d0","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00015276","00015286","000264cc","00026740","0007654c"],"span":1}},{"kind":"trace","relies":"structure","supports":"identity","to":"jasmine-lizard/fn/7mfk"},{"kind":"trace","relies":"structure","supports":"identity","to":"didactic-civet/fn/7mfk"}],"layout":"7mfk","name":"spiritual-alligator"}]}',
                         'native_sha256': 'ccedefdc42206640021c9924de86758f8920efab53bdf7e5a8519a67b4f506da'}]}
IDENTITIES=(('retained-15770-consumer',
  87920,
  'vigilant-rat/tbl',
  484684,
  (484712,),
  'reader',
  'ratio_state_quantity_paths',
  2,
  'unset',
  'unset',
  '856f2bada9b060e1955f0cb21918ac97da02b238ab7aa2a020f889afabd6cdcc',
  'b32bd55c64652aff626411b0b062d00136e7f63135ec86a68d789621b4a2bb60',
  '187a097b5649112113b22d3a986179eb02cba429e31dc3a16c20ebb8855621b2',
  '8910241e368a5bc0d0425a43f2573311adf76526b163f1990966413f631919ad'),)
def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):raise ValueError('the quantity claim changes its exact retained native/function/type/evidence/TEST boundary')
    row=value['reference'][0];old=json.loads(row['original_claim_json']);new=json.loads(row['proposed_claim_json'])
    expected=deepcopy(old);expected['evidence'].append(item(row))
    before=json.loads(row['original_native_json']);after=deepcopy(before)
    links=[r for r in after['link'] if (r['type'],r['to'])==('reader','spiritual-alligator/fn')]
    if len(links)!=1:raise ValueError('the quantity claim loses its unique retained conditional reader')
    links[0].setdefault('evidence',[]).append(item(row))
    if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
            or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
            or not test_contract.exact(new,expected) or not test_contract.exact(after,json.loads(row['proposed_native_json']))):
        raise ValueError('the quantity claim changes more than its single exact owning append')
    return value

def item(row):return json.loads(row['evidence_json'])
def native_type(row,field):return None if row['declared_'+field]=='unset' else row['declared_'+field]
def symbol_key(row):return SymbolKey('7mfk','tbl',row['address'])
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
    return any(registered(e) for e in link.evidence) or (link.owner.key,link.type,link.to.key)==('vigilant-rat/tbl','reader','spiritual-alligator/fn')
