"""Complete natural scope, exact published counts and input-only source refusals."""
from copy import deepcopy
import hashlib,re
import pytest
from kb import repo
from kb import bfs_state_caller_withdrawal_contract as contract
from kb import bfs_state_caller_withdrawal_matrix as matrix

def case():
    return dict(deepcopy(matrix.DEFAULTS),index=0,kind='controlled-source')

def test_published_counts_and_natural_paths_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT)
    actual=(sum((row['end']-row['start'])//2 for row in source['unit']['code']),
        len(source['stock_entry_paths']),len(source['unit']['code']),len(source['unit']['pools']),
        len(source['unit']['aliases']),len(source['controlled_calibration']))
    text=(repo.ROOT/'defs/JK08A.bfs-state-caller-withdrawal-paths.md').read_text()
    match=re.search(r'binds (\d+) stock instructions in (\d+) actual entry paths and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans',text)
    assert match is not None and tuple(map(int,match.groups()))==actual==(285,5,6,18,9,21)
    assert source['entries']==[0x3A750] and source['stock_entry_paths']==[0x25E20,0x26370,0x26740,0x26A80,0x3A750]
    assert set(contract.FUNCTIONS)=={0x25E20,0x26370,0x26740,0x26A60,0x3A750}
    assert int(re.search(r'all (\d+) physical bytes',text)[1])==source['selected']['physical_interval_bytes']==16
    assert int(re.search(r'(\d+)-byte frame',text)[1])==source['frame_bytes']==192
    assert int(re.search(r'complete (\d+)-byte RAM',text)[1])==matrix.RAM_SIZE==65536
    assert source['actual_curve']['active_bytes']==8
    assert int(re.search(r'The (\d+) preceding parent instructions',text)[1])==len(range(0x26A60,0x26A80,2))==16
    assert int(re.search(r'(\d+) held-other',text)[1])==len(matrix.CAUSAL_CONFIGURATION)+3==13
    assert source['preserved_quantity_reads']==[0xFFFF1062,0xFFFF1026]
    assert source['preserved_function_dependency']=='tall-quoll/ram'
    assert source['selected']['semantic_width']==source['selected']['semantic_signed']=='unset'

def test_fixture_changes_only_exact_pointer_aliases_and_preserves_full_stock_instructions():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert {i for i,(a,z) in enumerate(zip(image,fixture)) if a!=z}<={i for row in aliases for i in range(row['address'],row['address']+4)}
    for row in source['unit']['code']:assert image[row['start']:row['end']]==fixture[row['start']:row['end']]
    changed=bytearray(image);changed[0x3A750]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(changed))

@pytest.mark.parametrize('fault',('bool-byte','wide-word','wide-state','short-context','bad-SR','wide-curve','supplied-output'))
def test_raw_inputs_refuse_truncation_or_result_columns(fault):
    value=case()
    if fault=='bool-byte':value['record129']=True
    elif fault=='wide-word':value['word_1062']=65536
    elif fault=='wide-state':value['state_39d0']=0x100000000
    elif fault=='short-context':value['context'].pop()
    elif fault=='bad-SR':value['context'][18]=2
    elif fault=='wide-curve':value['curve_7']=256
    else:value['expected_state']=1
    with pytest.raises(ValueError):matrix.require_case(value)

def test_header_keeps_full_context_and_has_no_expected_publications():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    raw=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context context' in raw and 'uint8_t pattern' in raw
    assert '\\n' not in raw and '\n' in raw
    assert all(name not in raw for name in ('expected_state','computed_output','supplied_result'))
    assert len(matrix.CAUSAL_CONFIGURATION)+3==13
    for name,wanted in source['reused_source_sha256'].items():
        assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest()==wanted


def test_shared_owning_publication_reads_current_execution_descriptor_and_registry():
    import json
    from kb import scalar_ram_leaf_withdrawal_contract as withdrawal
    from kb import scalar_ram_leaf_withdrawal_evidence as family,ordinary_access_registry as registry
    declared=withdrawal.descriptor(repo.ROOT)
    text=' '.join((repo.ROOT/'defs/JK08A.bfs-state-caller-withdrawal-paths.md').read_text().split())
    owners={row['owner']:row for row in declared['reference']}
    datum=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']) or ())-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']) or ()) for row in owners.values())
    functions=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    readers=sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])
    for phrase in (f"{len(declared['reference'])} exact access originals",f'{readers} readers and eleven',
            f'{len(owners)} complete datum owners',f"{len(declared['function'])} complete functions",
            f'{datum+functions} matching ledger selectors',f'{datum} datum-end selectors and {functions} function-end selectors',
            f'{len(registry.FAMILIES)} families and {len(registry.captures())} captures'):
        assert phrase in text
    assert len(withdrawal.ORIGINAL_LINK_TYPES)==11
    assert len(family.COMPONENTS)==33 and 'Thirty-three independent components' in text
    assert len(withdrawal.FUNCTION_POSTIMAGE_IDENTITIES)==5 and len(withdrawal.FUNCTION_POSTIMAGE_CLAIMS)==8
    assert withdrawal.digest(withdrawal.remaining_callers_prior_current_rows(declared,129))==withdrawal.PRIOR_REMAINING_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:70])==withdrawal.PRIOR_REMAINING_CALLER_FUNCTION_SHA256
