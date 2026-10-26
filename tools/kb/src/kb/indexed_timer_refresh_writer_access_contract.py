"""One exact indexed timer writer identity and complete retained native facts."""
from copy import deepcopy
from pathlib import Path
import json,tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,plain
from kb.model import SymbolKey
DESCRIPTOR='defs/JK08A.indexed-timer-refresh-writer-claims.toml'
MODE='indexed-timer-refresh-writer-access'
PREFIX='indexed-timer-refresh-writer-access-v1:jk08a:'
DECLARED = {'schema': 1,
 'id': 'jk08a-indexed-timer-refresh-writer-claims',
 'layout': '7mfk',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'One exact indexed43BE timer writer identity from full9018C. Complete original owner/function, '
          'unset native type, existing unit, other writers and both ledger/TEST positions remain exact.',
 'native_function_publication': False,
 'native_geometry_publication': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_caller_reachability': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'reference': [{'id': 'retained-9018c-43be-writer',
                'address': 4294919102,
                'owner': 'silent-elephant/ram',
                'function': 590220,
                'sites': [590398],
                'direction': 'writer',
                'source': 'kb/ram/silent-elephant.toml',
                'component': 'indexed_timer_refresh_writer_paths',
                'width_bytes': 1,
                'declared_width': 'unset',
                'declared_signed': 'unset',
                'original_claim_sha256': 'a4d8fa46eb520c07e6ddda8e50c5f471654b0caf8ae461f2809fc46bc49b89ba',
                'original_claim_json': '{"evidence":[],"layout":"7mfk","offset":null,"owner":"silent-elephant/ram","props":{"layouts":["7mfk"],"relies":"level","reverse_relies":"structure","reverse_supports":"identity","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/silent-elephant.toml"],"stated":["7mfk"],"to":"satisfied-myna/fn","type":"writer"}',
                'proposed_claim_sha256': '0166a6033839557df28851edf9302f44c66c29f77082669967a42be7ccd7a57c',
                'proposed_claim_json': '{"evidence":[{"at":"7mfk:0009023e","key":"indexed-timer-refresh-writer-access-v1:jk08a:retained-9018c-43be-writer","kind":"indirect","mode":"indexed-timer-refresh-writer-access","note":"Complete '
                                       'stock 9018C observations bind the exact43BE byte reload at fullR4=6 '
                                       'through the real BRA delay slot,including full nonzeroR5 paths, '
                                       'native850C read/write,850D read, SR interrupt masking, separate '
                                       'ordinary/native snapshots and actual positive reload alternatives. '
                                       'Native timer width/signedness, unit, all other relations, full '
                                       'function and both ledger/TEST ends remain '
                                       'exact.","path":"defs/JK08A.indexed-timer-refresh-writer-claims.toml","supports":"identity","value":{"actual_fixed_other_43BE_reload_alternatives":true,"actual_indexed_write":{"address":4294919102,"base":4294919096,"exact_full_R4":6,"raw_ROM_source":36387,"register":6,"site":590398,"width_bytes":1},"actual_native_OR80_alternatives":true,"all_zero_nonzero_R5_paths":true,"complete_native_owner_function_TEST_ledger":true,"component":"indexed_timer_refresh_writer_paths","direction":"writer","entry":590220,"full_actual_SR_and_R14_GBR_frame":true,"function":"7mfk:0009018c","hardware_qualification":false,"mask_equation":"u32(R4+1)","native_address":4294919102,"native_control":{"read_only":4294935821,"read_write":4294935820,"sites":[590298,590302,590332],"window_size":256,"window_start":4294935808},"native_geometry_inference":false,"native_signed":"unset","native_storage_width":"unset","natural_caller_reachability":false,"natural_scheduling_inference":false,"no_bank_mapping_or_other_timer_owner_inference":true,"original_claim_sha256":"a4d8fa46eb520c07e6ddda8e50c5f471654b0caf8ae461f2809fc46bc49b89ba","owner":"silent-elephant/ram","scale_admission":false,"scope":"exact-indexed-timer-refresh-writer","separate_actual_native_and_ordinary_state":true,"units_admission":false,"width_bytes":1}}],"layout":"7mfk","offset":null,"owner":"silent-elephant/ram","props":{"layouts":["7mfk"],"relies":"level","reverse_relies":"structure","reverse_supports":"identity","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/silent-elephant.toml"],"stated":["7mfk"],"to":"satisfied-myna/fn","type":"writer"}',
                'original_native_sha256': '81f3ef6c222c43591059c2a98cc0813cd7a731846a5ef1641e2f5e07a89587b2',
                'original_native_json': '{"ledger":[{"dependency":[{"end":"owner","relies":"level","role":"consumer","supports":"identity","to":"quartz-trogon/fn","type":"reader"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"chestnut-robin/ram","type":"input"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"quartz-trogon/fn","type":"writer"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"satisfied-myna/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4],"notes":[0],"order":830,"registry":"vars"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"chestnut-robin/ram","type":"input"},{"layouts":["7mfk"],"relies":"level","supports":"identity","to":"quartz-trogon/fn","type":"reader"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","to":"periodic_tick_isr/fn","type":"writer"},{"layouts":["7mfk"],"relies":"level","reverse_relies":"structure","reverse_supports":"identity","supports":"identity","to":"quartz-trogon/fn","type":"writer"},{"layouts":["7mfk"],"relies":"level","reverse_relies":"structure","reverse_supports":"identity","supports":"identity","to":"satisfied-myna/fn","type":"writer"}],"note":["The '
                                        'timer lies in the 102.4 ms byte block ffff42d3..ffff43c6 of '
                                        'base-tick handler 0002040c, so the reload of 100 is 10.24 '
                                        's."],"summary":"Per-bank judgement timer of the exhaust-VTC '
                                        'position-sensor monitors (ffff43be + b). FUN 00090086 reloads it '
                                        'with ROM8[00008e23]=100 at 0009016a and 0009017a while indicator '
                                        'ffff850d bit 6 + b is clear or its enable is clear, reads it at '
                                        '0009010e, and sets judged latch ffff3580 bit b at 0009011c when it '
                                        'has reached zero with the indicator set; FUN 0009018c applies the '
                                        'same rules with ffff850d bit 4 + b and '
                                        'ffff3581.","symbol":[{"address":"ffff43be","evidence":[{"kind":"unbound-constant","supports":"identity","value":"00008e23=100"},{"at":"7mfk:0009010e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008e23","00090086","0009018c","ffff43be","ffff850d"],"span":1}},{"at":"7mfk:0009011c","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00008e23","00090086","0009018c","ffff43be","ffff850d"],"span":1}},{"at":"7mfk:0009016a","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00008e23","00090086","0009018c","ffff43be","ffff850d"],"span":1}},{"at":"7mfk:0009017a","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008e23","00090086","0009018c","ffff43be","ffff850d"],"span":1}}],"layout":"7mfk","name":"silent-elephant"}],"unit":"102.4 '
                                        'ms counts"}',
                'proposed_native_sha256': '1927a9e1b03f3ac20a23d875f280cc614396158f7e1ee3edb01053313048db1c',
                'proposed_native_json': '{"ledger":[{"dependency":[{"end":"owner","relies":"level","role":"consumer","supports":"identity","to":"quartz-trogon/fn","type":"reader"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"chestnut-robin/ram","type":"input"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"quartz-trogon/fn","type":"writer"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"satisfied-myna/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4],"notes":[0],"order":830,"registry":"vars"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"chestnut-robin/ram","type":"input"},{"layouts":["7mfk"],"relies":"level","supports":"identity","to":"quartz-trogon/fn","type":"reader"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","to":"periodic_tick_isr/fn","type":"writer"},{"layouts":["7mfk"],"relies":"level","reverse_relies":"structure","reverse_supports":"identity","supports":"identity","to":"quartz-trogon/fn","type":"writer"},{"evidence":[{"at":"7mfk:0009023e","key":"indexed-timer-refresh-writer-access-v1:jk08a:retained-9018c-43be-writer","kind":"indirect","mode":"indexed-timer-refresh-writer-access","note":"Complete '
                                        'stock 9018C observations bind the exact43BE byte reload at fullR4=6 '
                                        'through the real BRA delay slot,including full nonzeroR5 paths, '
                                        'native850C read/write,850D read, SR interrupt masking, separate '
                                        'ordinary/native snapshots and actual positive reload alternatives. '
                                        'Native timer width/signedness, unit, all other relations, full '
                                        'function and both ledger/TEST ends remain '
                                        'exact.","path":"defs/JK08A.indexed-timer-refresh-writer-claims.toml","supports":"identity","value":{"actual_fixed_other_43BE_reload_alternatives":true,"actual_indexed_write":{"address":4294919102,"base":4294919096,"exact_full_R4":6,"raw_ROM_source":36387,"register":6,"site":590398,"width_bytes":1},"actual_native_OR80_alternatives":true,"all_zero_nonzero_R5_paths":true,"complete_native_owner_function_TEST_ledger":true,"component":"indexed_timer_refresh_writer_paths","direction":"writer","entry":590220,"full_actual_SR_and_R14_GBR_frame":true,"function":"7mfk:0009018c","hardware_qualification":false,"mask_equation":"u32(R4+1)","native_address":4294919102,"native_control":{"read_only":4294935821,"read_write":4294935820,"sites":[590298,590302,590332],"window_size":256,"window_start":4294935808},"native_geometry_inference":false,"native_signed":"unset","native_storage_width":"unset","natural_caller_reachability":false,"natural_scheduling_inference":false,"no_bank_mapping_or_other_timer_owner_inference":true,"original_claim_sha256":"a4d8fa46eb520c07e6ddda8e50c5f471654b0caf8ae461f2809fc46bc49b89ba","owner":"silent-elephant/ram","scale_admission":false,"scope":"exact-indexed-timer-refresh-writer","separate_actual_native_and_ordinary_state":true,"units_admission":false,"width_bytes":1}}],"layouts":["7mfk"],"relies":"level","reverse_relies":"structure","reverse_supports":"identity","supports":"identity","to":"satisfied-myna/fn","type":"writer"}],"note":["The '
                                        'timer lies in the 102.4 ms byte block ffff42d3..ffff43c6 of '
                                        'base-tick handler 0002040c, so the reload of 100 is 10.24 '
                                        's."],"summary":"Per-bank judgement timer of the exhaust-VTC '
                                        'position-sensor monitors (ffff43be + b). FUN 00090086 reloads it '
                                        'with ROM8[00008e23]=100 at 0009016a and 0009017a while indicator '
                                        'ffff850d bit 6 + b is clear or its enable is clear, reads it at '
                                        '0009010e, and sets judged latch ffff3580 bit b at 0009011c when it '
                                        'has reached zero with the indicator set; FUN 0009018c applies the '
                                        'same rules with ffff850d bit 4 + b and '
                                        'ffff3581.","symbol":[{"address":"ffff43be","evidence":[{"kind":"unbound-constant","supports":"identity","value":"00008e23=100"},{"at":"7mfk:0009010e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008e23","00090086","0009018c","ffff43be","ffff850d"],"span":1}},{"at":"7mfk:0009011c","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00008e23","00090086","0009018c","ffff43be","ffff850d"],"span":1}},{"at":"7mfk:0009016a","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00008e23","00090086","0009018c","ffff43be","ffff850d"],"span":1}},{"at":"7mfk:0009017a","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008e23","00090086","0009018c","ffff43be","ffff850d"],"span":1}}],"layout":"7mfk","name":"silent-elephant"}],"unit":"102.4 '
                                        'ms counts"}',
                'original_ledger_json': '[{"dependency":[{"end":"owner","relies":"level","role":"consumer","supports":"identity","to":"quartz-trogon/fn","type":"reader"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"chestnut-robin/ram","type":"input"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"quartz-trogon/fn","type":"writer"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"satisfied-myna/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4],"notes":[0],"order":830,"registry":"vars"}]',
                'proposed_ledger_json': '[{"dependency":[{"end":"owner","relies":"level","role":"consumer","supports":"identity","to":"quartz-trogon/fn","type":"reader"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"chestnut-robin/ram","type":"input"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"quartz-trogon/fn","type":"writer"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"satisfied-myna/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4],"notes":[0],"order":830,"registry":"vars"}]',
                'original_symbol_evidence_json': '[{"kind":"unbound-constant","supports":"identity","value":"00008e23=100"},{"at":"7mfk:0009010e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008e23","00090086","0009018c","ffff43be","ffff850d"],"span":1}},{"at":"7mfk:0009011c","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00008e23","00090086","0009018c","ffff43be","ffff850d"],"span":1}},{"at":"7mfk:0009016a","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00008e23","00090086","0009018c","ffff43be","ffff850d"],"span":1}},{"at":"7mfk:0009017a","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008e23","00090086","0009018c","ffff43be","ffff850d"],"span":1}}]',
                'evidence_json': '{"at":"7mfk:0009023e","key":"indexed-timer-refresh-writer-access-v1:jk08a:retained-9018c-43be-writer","kind":"indirect","mode":"indexed-timer-refresh-writer-access","note":"Complete '
                                 'stock 9018C observations bind the exact43BE byte reload at fullR4=6 '
                                 'through the real BRA delay slot,including full nonzeroR5 paths, native850C '
                                 'read/write,850D read, SR interrupt masking, separate ordinary/native '
                                 'snapshots and actual positive reload alternatives. Native timer '
                                 'width/signedness, unit, all other relations, full function and both '
                                 'ledger/TEST ends remain '
                                 'exact.","path":"defs/JK08A.indexed-timer-refresh-writer-claims.toml","supports":"identity","value":{"actual_fixed_other_43BE_reload_alternatives":true,"actual_indexed_write":{"address":4294919102,"base":4294919096,"exact_full_R4":6,"raw_ROM_source":36387,"register":6,"site":590398,"width_bytes":1},"actual_native_OR80_alternatives":true,"all_zero_nonzero_R5_paths":true,"complete_native_owner_function_TEST_ledger":true,"component":"indexed_timer_refresh_writer_paths","direction":"writer","entry":590220,"full_actual_SR_and_R14_GBR_frame":true,"function":"7mfk:0009018c","hardware_qualification":false,"mask_equation":"u32(R4+1)","native_address":4294919102,"native_control":{"read_only":4294935821,"read_write":4294935820,"sites":[590298,590302,590332],"window_size":256,"window_start":4294935808},"native_geometry_inference":false,"native_signed":"unset","native_storage_width":"unset","natural_caller_reachability":false,"natural_scheduling_inference":false,"no_bank_mapping_or_other_timer_owner_inference":true,"original_claim_sha256":"a4d8fa46eb520c07e6ddda8e50c5f471654b0caf8ae461f2809fc46bc49b89ba","owner":"silent-elephant/ram","scale_admission":false,"scope":"exact-indexed-timer-refresh-writer","separate_actual_native_and_ordinary_state":true,"units_admission":false,"width_bytes":1}}'}],
 'retained_functions': [{'address': 590220,
                         'owner': 'satisfied-myna/fn',
                         'source': 'kb/fn/satisfied-myna.toml',
                         'native_sha256': 'a2fabddc3b26a685ede644f6109b88daea53c2d520df295081933872cd09fa3f',
                         'native_json': '{"block":"vtc_monitors/block","ledger":[{"dependency":[{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"chestnut-robin/ram","type":"reader"},{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"great-owl/ram","type":"reader"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"enigmatic-oyster/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"imperial-beagle/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"real-vulture/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"silent-elephant/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6],"notes":[0],"order":610,"registry":"funcs"}],"level":"code","note":["The '
                                        'arm bit reaches capture handler 000c2c58 and monitor 000c22dc '
                                        'through scheduler copy ffff4121. Timer ffff43be + b lies in the '
                                        '102.4 ms block of base-tick handler 0002040c, so the reload of 100 '
                                        'is 10.24 s."],"role":"monitor","summary":"Exhaust-VTC '
                                        'position-sensor monitor, path B (extra-edge), called from 0008f168 '
                                        'with the bank in r4 and the enable in r5. It sets or clears bit b '
                                        'of arm byte ffff4179 at 000901d8, 000901fa, 0009022c, and 00090246 '
                                        'by the rules of 00090086, raises reset request ffff850c bit 7 at '
                                        '000901de when both arm bytes were clear for the bank, reloads timer '
                                        'ffff43be + b with ROM8[00008e23]=100 while indicator ffff850d bit 4 '
                                        '+ b is clear or the enable is clear, and sets judged latch ffff3581 '
                                        'bit b at 00090222 when the indicator is set and the timer has '
                                        'expired.","symbol":[{"address":"0009018c","evidence":[{"kind":"unbound-constant","supports":"identity","value":"00008e23=100"},{"at":"7mfk:000901d8","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008e23","0009018c","ffff3581","ffff4178","ffff4179","ffff43be","ffff850c","ffff850d"],"span":1}},{"at":"7mfk:000901de","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008e23","0009018c","ffff3581","ffff4178","ffff4179","ffff43be","ffff850c","ffff850d"],"span":1}},{"at":"7mfk:000901fa","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008e23","0009018c","ffff3581","ffff4178","ffff4179","ffff43be","ffff850c","ffff850d"],"span":1}},{"at":"7mfk:00090222","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008e23","0009018c","ffff3581","ffff4178","ffff4179","ffff43be","ffff850c","ffff850d"],"span":1}},{"at":"7mfk:0009022c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008e23","0009018c","ffff3581","ffff4178","ffff4179","ffff43be","ffff850c","ffff850d"],"span":1}},{"at":"7mfk:00090246","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008e23","0009018c","ffff3581","ffff4178","ffff4179","ffff43be","ffff850c","ffff850d"],"span":1}}],"layout":"7mfk","name":"satisfied-myna"}]}'}]}
IDENTITIES = (('retained-9018c-43be-writer',
  4294919102,
  'silent-elephant/ram',
  590220,
  (590398,),
  'writer',
  'indexed_timer_refresh_writer_paths',
  1,
  'unset',
  'unset',
  'a4d8fa46eb520c07e6ddda8e50c5f471654b0caf8ae461f2809fc46bc49b89ba',
  '0166a6033839557df28851edf9302f44c66c29f77082669967a42be7ccd7a57c',
  '81f3ef6c222c43591059c2a98cc0813cd7a731846a5ef1641e2f5e07a89587b2',
  '1927a9e1b03f3ac20a23d875f280cc614396158f7e1ee3edb01053313048db1c'),)

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):raise ValueError('the timer writer claim changes its exact retained native/function/type/evidence/TEST boundary')
    row=value['reference'][0];old=json.loads(row['original_claim_json']);new=json.loads(row['proposed_claim_json'])
    expected=deepcopy(old);expected['evidence'].append(item(row))
    before=json.loads(row['original_native_json']);after=deepcopy(before)
    links=[r for r in after['link'] if (r['type'],r['to'])==('writer','satisfied-myna/fn')]
    if len(links)!=1:raise ValueError('the timer writer claim loses its unique retained indexed writer')
    links[0].setdefault('evidence',[]).append(item(row))
    if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
            or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
            or not test_contract.exact(new,expected) or not test_contract.exact(after,json.loads(row['proposed_native_json']))):
        raise ValueError('the timer writer claim changes more than its single exact owning append')
    for retained in value['retained_functions']:
        if digest(json.loads(retained['native_json']))!=retained['native_sha256']:
            raise ValueError('the timer writer claim changes its complete retained function digest')
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
        raise ValueError('the timer writer attachment requires its one exact complete normal owning link operation')
    return True
def looks_like_access(link):
    return any(registered(e) for e in link.evidence) or (link.owner.key,link.type,link.to.key)==('silent-elephant/ram','writer','satisfied-myna/fn')
