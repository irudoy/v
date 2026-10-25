"""One exact retained published APC candidate quantity and complete native preservation."""
from copy import deepcopy
from pathlib import Path
import json,tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,plain
from kb.model import SymbolKey
DESCRIPTOR='defs/JK08A.apc-reset-candidate-claims.toml'
MODE='apc-reset-candidate-access'
PREFIX='apc-reset-candidate-access-v1:jk08a:'
DECLARED={'schema': 1,
 'id': 'jk08a-apc-reset-candidate-claims',
 'layout': '7mfk',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'One exact retained1875 quantity reader through its real publication and subsequent complete '
          'liveR5 consumption; original writer and all native facts stay fixed.',
 'native_function_publication': False,
 'native_geometry_publication': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_caller_reachability': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'reference': [{'id': 'retained-1875-published-live-candidate-reader',
                'address': 4294908021,
                'owner': 'chubby-lobster/ram',
                'function': 311780,
                'sites': [312180],
                'direction': 'reader',
                'source': 'kb/ram/chubby-lobster.toml',
                'component': 'apc_reset_candidate_paths',
                'width_bytes': 1,
                'declared_width': 'unset',
                'declared_signed': 'unset',
                'original_claim_sha256': 'b7129a622e276420fd2cd5b784fbc324cde6583c87fd7999bea65aa5dbc68c40',
                'original_claim_json': '{"evidence":[],"layout":"7mfk","offset":null,"owner":"chubby-lobster/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/chubby-lobster.toml"],"stated":["7mfk"],"to":"apc_reset_offset_source_builder/fn","type":"reader"}',
                'proposed_claim_sha256': '0a82db12ffcebf6bb0f2f7dcd5e7323be887908b75265ad6f9cfdd3cf60d2240',
                'proposed_claim_json': '{"evidence":[{"at":"7mfk:0004c374","key":"apc-reset-candidate-access-v1:jk08a:retained-1875-published-live-candidate-reader","kind":"indirect","mode":"apc-reset-candidate-access","note":"Exact '
                                       'complete stock candidate publication and subsequent live-register '
                                       'consumption reach the actual output; the retained reader association '
                                       'does not assert a physical read of prior1875 RAM. Full native facts, '
                                       'types and TEST positions remain '
                                       'fixed.","path":"defs/JK08A.apc-reset-candidate-claims.toml","supports":"identity","value":{"actual_output":{"address":4294910982,"diagnostic_override_site":312206,"diagnostic_value":24,"register":6,"site":312192,"width_bytes":1},"actual_publication":{"address":4294908021,"register":5,"site":312172,"width_bytes":1},"complete_natural_entry_RAM_frame_CPU_and_real_calls":true,"component":"apc_reset_candidate_paths","direction":"reader","entry":311780,"function":"7mfk:0004c1e4","hardware_qualification":false,"live_consumption":{"comparison_address":4294908020,"comparison_read":312176,"lower_selection":312184,"output_copy":312186,"register":5,"sites":[312174,312176,312178,312180,312182]},"native_address":4294908021,"native_geometry_inference":false,"natural_caller_reachability":false,"natural_scheduling_inference":false,"original_claim_sha256":"b7129a622e276420fd2cd5b784fbc324cde6583c87fd7999bea65aa5dbc68c40","overwritten_prior1875_full_state_invariance":true,"owner":"chubby-lobster/ram","prior1875_physical_read":false,"scale_admission":false,"scope":"exact-published-live-register-apc-candidate","units_admission":false,"width_bytes":1}}],"layout":"7mfk","offset":null,"owner":"chubby-lobster/ram","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/ram/chubby-lobster.toml"],"stated":["7mfk"],"to":"apc_reset_offset_source_builder/fn","type":"reader"}',
                'original_native_sha256': '3fd13c09b90f15e127497f47376b249c75628586437449a8f7feb2abe4282685',
                'original_native_json': '{"ledger":[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"apc_reset_offset_source_builder/fn","type":"reader"},{"end":"owner","relies":"structure","role":"from_map","supports":"identity","to":"huge-pelican/tbl","type":"input"},{"end":"owner","relies":"structure","role":"from_map","supports":"identity","to":"prophetic-jacamar/tbl","type":"input"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"apc_reset_offset_source_builder/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5],"notes":[0],"order":644,"registry":"vars"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"huge-pelican/tbl","type":"input"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"prophetic-jacamar/tbl","type":"input"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"apc_reset_offset_source_builder/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","reverse_relies":"structure","reverse_supports":"identity","supports":"identity","to":"apc_reset_offset_source_builder/fn","type":"writer"}],"note":["The '
                                        'exact physical quantity and map engineering scales remain '
                                        'unresolved."],"summary":"Map-derived APC reset-offset candidate '
                                        'written by 0004c1e4 after a capped product of lookup outputs from '
                                        '0x1208e and 0x12096. The same function limits it to uint8 and '
                                        'compares it with '
                                        'ffff1874.","symbol":[{"address":"ffff1875","evidence":[{"at":"7mfk:0004c312","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c326","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c34c","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c356","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c36c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c374","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}}],"layout":"7mfk","name":"chubby-lobster"}],"unit":"raw '
                                        'command count"}',
                'proposed_native_sha256': 'f09bee1f469baf960167847d8002d659051d2afbbdd0e46837f3e49317690996',
                'proposed_native_json': '{"ledger":[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"apc_reset_offset_source_builder/fn","type":"reader"},{"end":"owner","relies":"structure","role":"from_map","supports":"identity","to":"huge-pelican/tbl","type":"input"},{"end":"owner","relies":"structure","role":"from_map","supports":"identity","to":"prophetic-jacamar/tbl","type":"input"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"apc_reset_offset_source_builder/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5],"notes":[0],"order":644,"registry":"vars"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"huge-pelican/tbl","type":"input"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"prophetic-jacamar/tbl","type":"input"},{"evidence":[{"at":"7mfk:0004c374","key":"apc-reset-candidate-access-v1:jk08a:retained-1875-published-live-candidate-reader","kind":"indirect","mode":"apc-reset-candidate-access","note":"Exact '
                                        'complete stock candidate publication and subsequent live-register '
                                        'consumption reach the actual output; the retained reader '
                                        'association does not assert a physical read of prior1875 RAM. Full '
                                        'native facts, types and TEST positions remain '
                                        'fixed.","path":"defs/JK08A.apc-reset-candidate-claims.toml","supports":"identity","value":{"actual_output":{"address":4294910982,"diagnostic_override_site":312206,"diagnostic_value":24,"register":6,"site":312192,"width_bytes":1},"actual_publication":{"address":4294908021,"register":5,"site":312172,"width_bytes":1},"complete_natural_entry_RAM_frame_CPU_and_real_calls":true,"component":"apc_reset_candidate_paths","direction":"reader","entry":311780,"function":"7mfk:0004c1e4","hardware_qualification":false,"live_consumption":{"comparison_address":4294908020,"comparison_read":312176,"lower_selection":312184,"output_copy":312186,"register":5,"sites":[312174,312176,312178,312180,312182]},"native_address":4294908021,"native_geometry_inference":false,"natural_caller_reachability":false,"natural_scheduling_inference":false,"original_claim_sha256":"b7129a622e276420fd2cd5b784fbc324cde6583c87fd7999bea65aa5dbc68c40","overwritten_prior1875_full_state_invariance":true,"owner":"chubby-lobster/ram","prior1875_physical_read":false,"scale_admission":false,"scope":"exact-published-live-register-apc-candidate","units_admission":false,"width_bytes":1}}],"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"apc_reset_offset_source_builder/fn","type":"reader"},{"layouts":["7mfk"],"relies":"structure","reverse_relies":"structure","reverse_supports":"identity","supports":"identity","to":"apc_reset_offset_source_builder/fn","type":"writer"}],"note":["The '
                                        'exact physical quantity and map engineering scales remain '
                                        'unresolved."],"summary":"Map-derived APC reset-offset candidate '
                                        'written by 0004c1e4 after a capped product of lookup outputs from '
                                        '0x1208e and 0x12096. The same function limits it to uint8 and '
                                        'compares it with '
                                        'ffff1874.","symbol":[{"address":"ffff1875","evidence":[{"at":"7mfk:0004c312","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c326","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c34c","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c356","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c36c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c374","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}}],"layout":"7mfk","name":"chubby-lobster"}],"unit":"raw '
                                        'command count"}',
                'original_ledger_json': '[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"apc_reset_offset_source_builder/fn","type":"reader"},{"end":"owner","relies":"structure","role":"from_map","supports":"identity","to":"huge-pelican/tbl","type":"input"},{"end":"owner","relies":"structure","role":"from_map","supports":"identity","to":"prophetic-jacamar/tbl","type":"input"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"apc_reset_offset_source_builder/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5],"notes":[0],"order":644,"registry":"vars"}]',
                'proposed_ledger_json': '[{"dependency":[{"end":"owner","relies":"structure","role":"consumer","supports":"identity","to":"apc_reset_offset_source_builder/fn","type":"reader"},{"end":"owner","relies":"structure","role":"from_map","supports":"identity","to":"huge-pelican/tbl","type":"input"},{"end":"owner","relies":"structure","role":"from_map","supports":"identity","to":"prophetic-jacamar/tbl","type":"input"},{"end":"owner","relies":"structure","role":"writes","supports":"identity","to":"apc_reset_offset_source_builder/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5],"notes":[0],"order":644,"registry":"vars"}]',
                'original_symbol_evidence_json': '[{"at":"7mfk:0004c312","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c326","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c34c","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c356","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c36c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}},{"at":"7mfk:0004c374","key":"body","kind":"l0-context","supports":"identity","value":{"named":["0001208e","00012096","0004c1e4","ffff1875"],"span":1}}]',
                'evidence_json': '{"at":"7mfk:0004c374","key":"apc-reset-candidate-access-v1:jk08a:retained-1875-published-live-candidate-reader","kind":"indirect","mode":"apc-reset-candidate-access","note":"Exact '
                                 'complete stock candidate publication and subsequent live-register '
                                 'consumption reach the actual output; the retained reader association does '
                                 'not assert a physical read of prior1875 RAM. Full native facts, types and '
                                 'TEST positions remain '
                                 'fixed.","path":"defs/JK08A.apc-reset-candidate-claims.toml","supports":"identity","value":{"actual_output":{"address":4294910982,"diagnostic_override_site":312206,"diagnostic_value":24,"register":6,"site":312192,"width_bytes":1},"actual_publication":{"address":4294908021,"register":5,"site":312172,"width_bytes":1},"complete_natural_entry_RAM_frame_CPU_and_real_calls":true,"component":"apc_reset_candidate_paths","direction":"reader","entry":311780,"function":"7mfk:0004c1e4","hardware_qualification":false,"live_consumption":{"comparison_address":4294908020,"comparison_read":312176,"lower_selection":312184,"output_copy":312186,"register":5,"sites":[312174,312176,312178,312180,312182]},"native_address":4294908021,"native_geometry_inference":false,"natural_caller_reachability":false,"natural_scheduling_inference":false,"original_claim_sha256":"b7129a622e276420fd2cd5b784fbc324cde6583c87fd7999bea65aa5dbc68c40","overwritten_prior1875_full_state_invariance":true,"owner":"chubby-lobster/ram","prior1875_physical_read":false,"scale_admission":false,"scope":"exact-published-live-register-apc-candidate","units_admission":false,"width_bytes":1}}'}],
 'retained_functions': [{'address': 311780,
                         'owner': 'apc_reset_offset_source_builder/fn',
                         'source': 'kb/fn/apc_reset_offset_source_builder.toml',
                         'native_sha256': 'ec75c3ccb71556e212b011103f4e63a8fc7f1225018fe06c25651a245aaaff40',
                         'native_json': '{"block":"ignition_output/block","ledger":[{"fields":["name"],"order":106,"registry":"curated","title":true},{"dependency":[{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"huge-pelican/tbl","type":"reader"},{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"prophetic-jacamar/tbl","type":"reader"},{"end":"owner","relies":"level","role":"selector","supports":"identity","to":"futuristic-chinchilla/ram","type":"selector"},{"end":"owner","relies":"structure","role":"selector","supports":"identity","to":"shaggy-nyala/ram","type":"selector"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"agate-ape/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"chubby-lobster/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"cuddly-crow/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"horned-turkey/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"olivine-tiger/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7,8,9],"notes":[0],"order":152,"registry":"funcs"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"level","supports":"identity","to":"futuristic-chinchilla/ram","type":"selector"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"shaggy-nyala/ram","type":"selector"}],"note":["Periodic '
                                        'dispatcher 00020dfe copies ffff2406 to actuator-facing snapshot '
                                        'ffff237a. The arithmetic and 0..114 output bound are exact; the '
                                        'physical dwell meaning remains '
                                        'unverified."],"role":"accessor","summary":"APC reset-offset source '
                                        'builder. It bounds ffff1874 to 6..114 with ROM8[0x8b88] and '
                                        'ROM8[0x8b87], calculates and caps map-derived byte ffff1875, and '
                                        'writes ffff2406=min(ffff1874,ffff1875). Diagnostic state '
                                        'ffff4251.bit0 instead forces '
                                        'ffff2406=24.","symbol":[{"address":"0004c1e4","evidence":[{"at":"7mfk:00008b87","kind":"rom-bytes","supports":"identity","value":"0x72"},{"at":"7mfk:00008b88","kind":"rom-bytes","supports":"identity","value":"0x06"},{"at":"7mfk:0004c2f4","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008b87","00008b88","0001208e","00012096","0004c1e4","ffff144d","ffff1451","ffff1874","ffff1875","ffff2406","ffff4184","ffff4251"],"span":1}},{"at":"7mfk:0004c304","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008b87","00008b88","0001208e","00012096","0004c1e4","ffff144d","ffff1451","ffff1874","ffff1875","ffff2406","ffff4184","ffff4251"],"span":1}},{"at":"7mfk:0004c30e","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00008b87","00008b88","0001208e","00012096","0004c1e4","ffff144d","ffff1451","ffff1874","ffff1875","ffff2406","ffff4184","ffff4251"],"span":1}},{"at":"7mfk:0004c36c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008b87","00008b88","0001208e","00012096","0004c1e4","ffff144d","ffff1451","ffff1874","ffff1875","ffff2406","ffff4184","ffff4251"],"span":1}},{"at":"7mfk:0004c370","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008b87","00008b88","0001208e","00012096","0004c1e4","ffff144d","ffff1451","ffff1874","ffff1875","ffff2406","ffff4184","ffff4251"],"span":1}},{"at":"7mfk:0004c37a","key":"body","kind":"l0-context","supports":"identity","value":{"named":["00008b87","00008b88","0001208e","00012096","0004c1e4","ffff144d","ffff1451","ffff1874","ffff1875","ffff2406","ffff4184","ffff4251"],"span":1}},{"at":"7mfk:0004c380","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008b87","00008b88","0001208e","00012096","0004c1e4","ffff144d","ffff1451","ffff1874","ffff1875","ffff2406","ffff4184","ffff4251"],"span":1}},{"at":"7mfk:0004c38e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["00008b87","00008b88","0001208e","00012096","0004c1e4","ffff144d","ffff1451","ffff1874","ffff1875","ffff2406","ffff4184","ffff4251"],"span":1}}],"layout":"7mfk"}],"title":"Build '
                                        'the bounded source for the APC reset-edge command offset"}'}]}
IDENTITIES=(('retained-1875-published-live-candidate-reader',
  4294908021,
  'chubby-lobster/ram',
  311780,
  (312180,),
  'reader',
  'apc_reset_candidate_paths',
  1,
  'unset',
  'unset',
  'b7129a622e276420fd2cd5b784fbc324cde6583c87fd7999bea65aa5dbc68c40',
  '0a82db12ffcebf6bb0f2f7dcd5e7323be887908b75265ad6f9cfdd3cf60d2240',
  '3fd13c09b90f15e127497f47376b249c75628586437449a8f7feb2abe4282685',
  'f09bee1f469baf960167847d8002d659051d2afbbdd0e46837f3e49317690996'),)

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):raise ValueError('the quantity claim changes its exact retained native/function/type/evidence/TEST boundary')
    row=value['reference'][0];old=json.loads(row['original_claim_json']);new=json.loads(row['proposed_claim_json'])
    expected=deepcopy(old);expected['evidence'].append(item(row))
    before=json.loads(row['original_native_json']);after=deepcopy(before)
    links=[r for r in after['link'] if (r['type'],r['to'])==('reader','apc_reset_offset_source_builder/fn')]
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
    return any(registered(e) for e in link.evidence) or (link.owner.key,link.type,link.to.key)==('chubby-lobster/ram','reader','apc_reset_offset_source_builder/fn')
