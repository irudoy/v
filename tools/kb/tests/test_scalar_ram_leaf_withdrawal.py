"""Exact native removal, original TEST context, writer and no-donation refusals."""

from copy import deepcopy
from dataclasses import replace
import json
import hashlib
from pathlib import Path
import tomllib
from types import SimpleNamespace

import pytest

from kb import compile,copy_evidence,levels,match,reconciliation,repo,store,test_contract,test_origins,write
from kb import ordinary_access_registry as registry
from kb import scalar_ram_leaf_withdrawal_contract as contract,scalar_ram_leaf_withdrawal_evidence as proof
from kb import scalar_ram_leaf_withdrawal_resolution as resolution
from kb.repo import KbError

LEGACY_WRITER_IDS={'00052034-ffff120e-withdraw','0006e3d8-ffff1300-withdraw','0006e3d8-ffff1f86-withdraw'}


@pytest.fixture(scope='module')
def models():
    declared=contract.descriptor(repo.ROOT);rows=declared['reference']
    overlays={phase:{Path(row['source']):store.render(row['owner'].rsplit('/',1)[1],
        json.loads(row[phase+'_native_json'])) for row in rows} for phase in ('original','proposed')}
    functions={phase:{Path(row['source']):store.render('fn',contract.function_native_document(row,phase))
        for row in declared['function']} for phase in ('original','proposed')}
    return rows,compile.build(repo.ROOT,{**functions['original'],**overlays['original']}),compile.build(repo.ROOT,{**functions['proposed'],**overlays['proposed']})


def test_exact_withdrawals_retain_all_complete_native_owners_and_test_positions(models):
    rows,before,after=models
    assert len(rows)==132 and len({row['owner'] for row in rows})==100
    assert proof.native_rows(before,'original')==proof.native_rows(after,'proposed')==rows
    assert {key:value.packet() for key,value in test_origins.index(before).items()}=={
        key:value.packet() for key,value in test_origins.index(after).items()}
    for row in rows:
        assert 'proposed_claim_json' not in row and 'evidence_json' not in row
        assert json.loads(row['original_claim_json'])['evidence']==[]
        old,new=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        assert old['symbol']==new['symbol']
        assert {key:value for key,value in old.items() if key not in ('link','ledger')}=={
            key:value for key,value in new.items() if key not in ('link','ledger')}


def test_existing_unlink_writer_produces_exact_grouped_native_postimages_without_replacement(models):
    rows,model,_=models;owners={meaning.key:meaning for meaning in model.meanings}
    documents={row['owner']:json.loads(row['original_native_json']) for row in rows}
    function_rows=contract.descriptor(repo.ROOT)['function']
    documents.update({row['owner']:contract.function_native_document(row,'original') for row in function_rows})
    change=object.__new__(write.Change);change.model,change.lines=model,[]
    change._ends=lambda op:(owners[op['meaning']],owners[op['to']],op['type'])
    change._held=lambda meaning:documents.get(meaning.key)
    for row in rows:change.unlink(contract.operation(row))
    assert all(test_contract.exact(tomllib.loads(store.render(row['owner'].rsplit('/',1)[1],documents[row['owner']])),
        json.loads(row['proposed_native_json'])) for row in rows)
    assert all(test_contract.exact(tomllib.loads(store.render('fn',documents[row['owner']])),
        contract.function_native_document(row,'proposed')) for row in function_rows)
    assert all(line.startswith('unlink ') for line in change.lines) and len(change.lines)==132


def test_joint_publication_permits_only_selected_links_and_matching_ledger_selectors(models,monkeypatch):
    rows,before,after=models;after=deepcopy(after)
    monkeypatch.setattr(proof,'require_current',lambda model:dict(controlled_only=True))
    selected={('access',contract.symbol_key(row).key,row['original_claim_sha256']) for row in rows}
    reviews=before.config['reconciliation']['review']
    assert len([row for row in reviews if reconciliation.difference_key(row) in selected])==132
    after.config['reconciliation']['review']=[row for row in reviews if reconciliation.difference_key(row) not in selected]
    expected=resolution.publication_expected(before,after,write.publication_view(before))
    assert test_contract.exact(expected,write.publication_view(after))
    ops=[contract.operation(row) for row in rows]
    write.require_metadata_only(before,after,ops,SimpleNamespace(width_resolutions={}),{})
    assert all(resolution.retires(before,after,json.loads(row['original_claim_json'])) for row in rows)


@pytest.mark.parametrize('fault',('extra-review','changed-review','missing-admission'))
def test_review_retirement_requires_only_the_exact_originals_and_complete_admission(models,monkeypatch,fault):
    rows,before,after=models;after=deepcopy(after)
    selected={('access',contract.symbol_key(row).key,row['original_claim_sha256']) for row in rows}
    after.config['reconciliation']['review']=[deepcopy(row) for row in before.config['reconciliation']['review']
        if reconciliation.difference_key(row) not in selected]
    def current(model):
        if fault=='missing-admission':raise ValueError('controlled missing complete original')
        return dict(controlled_only=True)
    monkeypatch.setattr(proof,'require_current',current)
    if fault=='extra-review':after.config['reconciliation']['review'].pop()
    elif fault=='changed-review':after.config['reconciliation']['review'][0]['reason']='unregistered'
    with pytest.raises(KbError):write.require_metadata_only(before,after,[contract.operation(row) for row in rows],
        SimpleNamespace(width_resolutions={}),{})


@pytest.mark.parametrize('fault',('partial','duplicate','owner','type','target','keys','evidence','extra'))
def test_preflight_rejects_partial_changed_broader_or_unmatched_withdrawals(fault):
    rows=contract.descriptor(repo.ROOT)['reference'];ops=[contract.operation(row) for row in rows]
    if fault=='partial':ops.pop()
    elif fault=='duplicate':ops[-1]=deepcopy(ops[0])
    elif fault=='owner':ops[0]['meaning']='other/tbl'
    elif fault=='type':ops[0]['type']='writer'
    elif fault=='target':ops[0]['to']='other/fn'
    elif fault=='keys':ops[0]['keys']={'slot':'unregistered'}
    elif fault=='evidence':ops[0]['evidence']=[dict(kind='indirect',mode=contract.MODE)]
    else:ops.append(dict(cmd='unlink',meaning=rows[0]['owner'],type='reader',to='other/fn'))
    with pytest.raises(KbError):write.require_publication_operations(ops)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_withdrawal_descriptor_refuses_identity_scale_replacement_or_publication_flags(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();assert flag+' = false' in text
    path.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('field',('original_claim_sha256','original_native_sha256','proposed_native_sha256'))
def test_withdrawal_descriptor_pins_each_complete_original_and_native_image(tmp_path,field):
    row=contract.descriptor(repo.ROOT)['reference'][0]
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text()
    path.write_text(text.replace(field+' = "'+row[field]+'"',field+' = "'+'0'*64+'"',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('component,flag',(
    ('scalar_ram_leaf_paths','exact_scalar_ram_leaves'),('scalar_ram_product_paths','exact_scalar_ram_products'),
    ('scalar_ram_leaf_paths','no_selected_datum_access'),('scalar_ram_product_paths','no_selected_datum_access'),
    ('scalar_ram_leaf_paths','native_identity_admission'),('scalar_ram_product_paths','native_identity_admission'),('scalar_ram_gated_paths','exact_scalar_ram_gated_paths'),
    ('scalar_ram_gated_paths','no_selected_datum_access'),('scalar_ram_gated_paths','native_identity_admission'),('rpm_ram_withdrawal_paths','exact_rpm_ram_withdrawal_paths'),
    ('rpm_ram_withdrawal_paths','no_selected_datum_access'),('rpm_ram_withdrawal_paths','no_selected_ram_datum_access'),
    ('rpm_ram_withdrawal_paths','native_identity_admission'),('register_overflow_paths','exact_register_overflow_paths'),
    ('register_overflow_paths','no_selected_datum_access'),('register_overflow_paths','no_selected_ram_datum_access'),
    ('register_overflow_paths','native_identity_admission'),('scalar_ram_word_paths','exact_scalar_ram_word_paths'),
    ('scalar_ram_word_paths','no_selected_datum_access'),('scalar_ram_word_paths','native_identity_admission'),('rpm_state_withdrawal_paths','exact_rpm_state_withdrawal_paths'),
    ('rpm_state_withdrawal_paths','no_selected_datum_access'),('rpm_state_withdrawal_paths','no_selected_ram_datum_access'),
    ('rpm_state_withdrawal_paths','native_identity_admission'),('indexed_word_update_paths','exact_indexed_word_update_paths'),
    ('indexed_word_update_paths','no_selected_datum_access'),('indexed_word_update_paths','no_selected_ram_datum_access'),
    ('indexed_word_update_paths','native_identity_admission'),('division_caller_withdrawal_paths','exact_division_caller_withdrawal_paths'),
    ('division_caller_withdrawal_paths','no_selected_datum_access'),('division_caller_withdrawal_paths','no_selected_ram_datum_access'),
    ('division_caller_withdrawal_paths','native_identity_admission'),('division_caller_withdrawal_paths','complete_direct_helpers_same_primary'),('byte_curve_caller_withdrawal_paths','exact_byte_curve_caller_withdrawal_paths'),
    ('byte_curve_caller_withdrawal_paths','no_selected_datum_access'),('byte_curve_caller_withdrawal_paths','no_selected_ram_datum_access'),
    ('byte_curve_caller_withdrawal_paths','native_identity_admission'),('byte_curve_caller_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('word_interp_caller_withdrawal_paths','exact_word_interp_caller_withdrawal_paths'),
    ('word_interp_caller_withdrawal_paths','no_selected_datum_access'),('word_interp_caller_withdrawal_paths','no_selected_ram_datum_access'),
    ('word_interp_caller_withdrawal_paths','native_identity_admission'),('word_interp_caller_withdrawal_paths','complete_timing_helpers_same_primary'),
    ('scaled_division_caller_withdrawal_paths','exact_scaled_division_caller_withdrawal_paths'),
    ('scaled_division_caller_withdrawal_paths','no_selected_datum_access'),('scaled_division_caller_withdrawal_paths','native_identity_admission'),
    ('scaled_division_caller_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('scaled_division_caller_withdrawal_paths','complete_register_helpers_same_primary'),
    ('curve_scale_caller_withdrawal_paths','exact_curve_scale_caller_withdrawal_paths'),
    ('curve_scale_caller_withdrawal_paths','no_selected_datum_access'),('curve_scale_caller_withdrawal_paths','no_selected_ram_datum_access'),
    ('curve_scale_caller_withdrawal_paths','native_identity_admission'),('curve_scale_caller_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('curve_scale_caller_withdrawal_paths','complete_curve_helpers_same_primary'),
    ('curve_scale_caller_withdrawal_paths','complete_uptight_RAM3348_same_primary'),
    ('curve_scale_caller_withdrawal_paths','uptight_RAM3348_withdrawal_original'),
    ('curve_scale_caller_withdrawal_paths','uptight_RAM3348_original_stdout_sha256'),
    ('curve_scale_caller_withdrawal_paths','curve_helper_original_stdout_sha256'),
    ('derivative_scale_caller_withdrawal_paths','exact_derivative_scale_caller_withdrawal_paths'),
    ('derivative_scale_caller_withdrawal_paths','no_selected_datum_access'),('derivative_scale_caller_withdrawal_paths','no_selected_ram_datum_access'),
    ('derivative_scale_caller_withdrawal_paths','native_identity_admission'),('derivative_scale_caller_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('derivative_scale_caller_withdrawal_paths','complete_timing_helpers_same_primary'),('derivative_scale_caller_withdrawal_paths','complete_normalization_helpers_same_primary'),
    ('derivative_scale_caller_withdrawal_paths','complete_viridian_caller_same_primary'),
    ('guarded_quotient_caller_withdrawal_paths','exact_guarded_quotient_caller_withdrawal_paths'),
    ('guarded_quotient_caller_withdrawal_paths','no_selected_datum_access'),('guarded_quotient_caller_withdrawal_paths','no_selected_ram_datum_access'),
    ('guarded_quotient_caller_withdrawal_paths','native_identity_admission'),('guarded_quotient_caller_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('mixed_curve_caller_withdrawal_paths','exact_mixed_curve_caller_withdrawal_paths'),
    ('mixed_curve_caller_withdrawal_paths','no_selected_datum_access'),('mixed_curve_caller_withdrawal_paths','no_selected_ram_datum_access'),
    ('mixed_curve_caller_withdrawal_paths','native_identity_admission'),('mixed_curve_caller_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('mixed_curve_caller_withdrawal_paths','complete_timing_helpers_same_primary'),('mixed_curve_caller_withdrawal_paths','complete_implicit_caller_same_primary'),
    ('mixed_curve_caller_withdrawal_paths','complete_register_helpers_same_primary'),
    ('timing_remainder_caller_withdrawal_paths','exact_timing_remainder_caller_withdrawal_paths'),
    ('timing_remainder_caller_withdrawal_paths','no_selected_datum_access'),('timing_remainder_caller_withdrawal_paths','no_selected_ram_datum_access'),
    ('timing_remainder_caller_withdrawal_paths','native_identity_admission'),('timing_remainder_caller_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('timing_remainder_caller_withdrawal_paths','complete_timing_helpers_same_primary'),('timing_remainder_caller_withdrawal_paths','complete_normalization_helpers_same_primary'),
    ('timing_remainder_caller_withdrawal_paths','complete_viridian_caller_same_primary'),('timing_remainder_caller_withdrawal_paths','complete_remainder_source_same_primary'),
    ('state_ratio_caller_withdrawal_paths','exact_state_ratio_caller_withdrawal_paths'),
    ('state_ratio_caller_withdrawal_paths','no_selected_datum_access'),('state_ratio_caller_withdrawal_paths','native_identity_admission'),
    ('state_ratio_caller_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('state_ratio_caller_withdrawal_paths','complete_previous_byte_curve_caller_same_primary'),
    ('state_ratio_caller_withdrawal_paths','complete_standard_implicit_byte_same_primary'),
    ('dfco_state_caller_withdrawal_paths','exact_dfco_state_caller_withdrawal_paths'),
    ('dfco_state_caller_withdrawal_paths','no_selected_datum_access'),('dfco_state_caller_withdrawal_paths','no_selected_ram_datum_access'),
    ('dfco_state_caller_withdrawal_paths','native_identity_admission'),('dfco_state_caller_withdrawal_paths','complete_real_rotation_helper'),
    *[('dfco_state_caller_withdrawal_paths',key) for key in ('reader_only1939_retained_writer',
        'prior1939_complete_state_independence','reader_only1939_original','strict_absence_originals','retained1939_write_sites')],
    ('paired_inhibit_writer_withdrawal_paths','exact_paired_inhibit_writer_withdrawal_paths'),
    ('paired_inhibit_writer_withdrawal_paths','no_selected_datum_access'),('paired_inhibit_writer_withdrawal_paths','no_selected_ram_datum_access'),
    ('paired_inhibit_writer_withdrawal_paths','native_identity_admission'),('paired_inhibit_writer_withdrawal_paths','complete_real_nibble_helper'),
    ('paired_inhibit_writer_withdrawal_paths','entry_scoped_root_absence'),('paired_inhibit_writer_withdrawal_paths','complete_RMW_read_write_pairs'),
    ('threshold_window_reader_withdrawal_paths','exact_threshold_window_reader_withdrawal_paths'),
    ('threshold_window_reader_withdrawal_paths','no_selected_datum_access'),('threshold_window_reader_withdrawal_paths','no_selected_ram_datum_access'),
    ('threshold_window_reader_withdrawal_paths','native_identity_admission'),('threshold_window_reader_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('threshold_window_reader_withdrawal_paths','complete_previous_byte_curve_caller_same_primary'),
    ('aux_rate_caller_withdrawal_paths','exact_aux_rate_caller_withdrawal_paths'),
    ('aux_rate_caller_withdrawal_paths','no_selected_datum_access'),('aux_rate_caller_withdrawal_paths','native_identity_admission'),
    ('aux_rate_caller_withdrawal_paths','complete_direct_helpers_same_primary'),('aux_rate_caller_withdrawal_paths','complete_real_auxiliary_gate'),
    ('paired_curve_normalization_withdrawal_paths','exact_paired_curve_normalization_withdrawal_paths'),
    ('paired_curve_normalization_withdrawal_paths','no_selected_datum_access'),('paired_curve_normalization_withdrawal_paths','native_identity_admission'),
    ('paired_curve_normalization_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('paired_curve_normalization_withdrawal_paths','complete_previous_byte_curve_caller_same_primary'),
    ('paired_curve_normalization_withdrawal_paths','complete_previous_mixed_curve_caller_same_primary'),
    ('paired_curve_normalization_withdrawal_paths','complete_raw16_axis17_data'),
    ('byte_ratio_producer_withdrawal_paths','exact_byte_ratio_producer_withdrawal_paths'),
    ('byte_ratio_producer_withdrawal_paths','no_selected_datum_access'),('byte_ratio_producer_withdrawal_paths','native_identity_admission'),
    ('byte_ratio_producer_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('byte_ratio_producer_withdrawal_paths','complete_signed_shift10'),('byte_ratio_producer_withdrawal_paths','complete_actual_post_DIV1_R1_carrier'),
    ('state_surface_caller_withdrawal_paths','exact_state_surface_caller_withdrawal_paths'),
    ('state_surface_caller_withdrawal_paths','no_selected_datum_access'),('state_surface_caller_withdrawal_paths','native_identity_admission'),
    ('state_surface_caller_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('state_surface_caller_withdrawal_paths','complete_local_word_argument'),('state_surface_caller_withdrawal_paths','complete_three_state_modes'),
    ('byte_factor_caller_withdrawal_paths','exact_byte_factor_caller_withdrawal_paths'),
    ('byte_factor_caller_withdrawal_paths','no_selected_datum_access'),('byte_factor_caller_withdrawal_paths','no_selected_ram_datum_access'),
    ('byte_factor_caller_withdrawal_paths','native_identity_admission'),('byte_factor_caller_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('byte_factor_caller_withdrawal_paths','complete_signed_word_difference'),('byte_factor_caller_withdrawal_paths','complete_dual_byte_partial_product'),
    ('byte_factor_caller_withdrawal_paths','complete_both_natural_curve_calls'),
    ('byte_sum_caller_withdrawal_paths','exact_byte_sum_caller_withdrawal_paths'),
    ('byte_sum_caller_withdrawal_paths','no_selected_datum_access'),('byte_sum_caller_withdrawal_paths','no_selected_ram_datum_access'),
    ('byte_sum_caller_withdrawal_paths','native_identity_admission'),('byte_sum_caller_withdrawal_paths','complete_direct_helpers_same_primary'),
    ('byte_sum_caller_withdrawal_paths','complete_clipped_byte_coordinate'),('byte_sum_caller_withdrawal_paths','complete_unsigned_byte_minimum'),
    ('byte_sum_caller_withdrawal_paths','complete_two_saturating_word_sums'),('clamp_latch_caller_withdrawal_paths', 'exact_clamp_latch_caller_withdrawal_paths'),('clamp_latch_caller_withdrawal_paths', 'no_selected_datum_access'),('clamp_latch_caller_withdrawal_paths', 'native_identity_admission'),('clamp_latch_caller_withdrawal_paths', 'complete_actual_absolute_calls'),('clamp_latch_caller_withdrawal_paths', 'complete_unordered_byte_clamp'),('clamp_latch_caller_withdrawal_paths', 'complete_latch_and_word_refresh'),('clamp_latch_caller_withdrawal_paths', 'complete_selected_table_interval_absence'),('clamp_latch_caller_withdrawal_paths', 'derived_RAM_and_producer_dependencies_preserved'),('clamp_latch_caller_withdrawal_paths', 'native_bindings'),('paired_word_curve_sum_withdrawal_paths', 'exact_paired_word_curve_sum_withdrawal_paths'),('paired_word_curve_sum_withdrawal_paths', 'no_selected_datum_access'),('paired_word_curve_sum_withdrawal_paths', 'native_identity_admission'),('paired_word_curve_sum_withdrawal_paths', 'complete_actual_paired_word_curve_calls'),('paired_word_curve_sum_withdrawal_paths', 'complete_raw_axis_and_curve'),('paired_word_curve_sum_withdrawal_paths', 'complete_two_saturated_word_publications'),('paired_word_curve_sum_withdrawal_paths', 'complete_local_word_carrier'),('paired_word_curve_sum_withdrawal_paths', 'complete_selected_scalar_interval_absence'),('paired_word_curve_sum_withdrawal_paths', 'derived_request_and_area_dependencies_preserved'),('paired_word_curve_sum_withdrawal_paths', 'complete_direct_helpers_same_primary'),('paired_word_curve_sum_withdrawal_paths', 'native_bindings'),
    ('misfire_tail_dispatch_withdrawal_paths', 'exact_misfire_tail_dispatch_withdrawal_paths'),
    ('misfire_tail_dispatch_withdrawal_paths', 'no_selected_datum_access'),
    ('misfire_tail_dispatch_withdrawal_paths', 'native_identity_admission'),
    ('misfire_tail_dispatch_withdrawal_paths', 'complete_actual_dispatch_BSR_and_tail'),
    ('misfire_tail_dispatch_withdrawal_paths', 'complete_hysteresis_and_byte_counter'),
    ('misfire_tail_dispatch_withdrawal_paths', 'complete_thresholded_word_counters'),
    ('misfire_tail_dispatch_withdrawal_paths', 'complete_PR_MACL_and_distinct_local_carriers'),
    ('misfire_tail_dispatch_withdrawal_paths', 'complete_selected_native_RAM_root_absence'),
    ('misfire_tail_dispatch_withdrawal_paths', 'scheduler_cadence_and_transitive_dependencies_preserved'),
    ('misfire_tail_dispatch_withdrawal_paths', 'native_bindings'),
    ('endpoint_normalizer_writer_withdrawal_paths', 'exact_endpoint_normalizer_writer_withdrawal_paths'),
    ('endpoint_normalizer_writer_withdrawal_paths', 'no_selected_datum_access'),
    ('endpoint_normalizer_writer_withdrawal_paths', 'native_identity_admission'),
    ('endpoint_normalizer_writer_withdrawal_paths', 'no_selected_ram_datum_access'),
    ('endpoint_normalizer_writer_withdrawal_paths', 'entry_scoped_root_absence'),
    ('endpoint_normalizer_writer_withdrawal_paths', 'complete_natural_calls_live_stores_CPU_frame_and_RAM'),
    ('endpoint_normalizer_writer_withdrawal_paths', 'complete_actual_normalization_and_three_computed_words'),
    ('endpoint_normalizer_writer_withdrawal_paths', 'complete_direct_helpers_same_primary'),
    ('endpoint_normalizer_writer_withdrawal_paths', 'complete_existing_normalization_same_primary'),
    ('endpoint_normalizer_writer_withdrawal_paths', 'native_bindings'),
    ('bfs_state_caller_withdrawal_paths', 'exact_bfs_state_caller_withdrawal_paths'),
    ('bfs_state_caller_withdrawal_paths', 'no_selected_datum_access'),
    ('bfs_state_caller_withdrawal_paths', 'native_identity_admission'),
    ('bfs_state_caller_withdrawal_paths', 'complete_selected_table_interval_absence'),
    ('bfs_state_caller_withdrawal_paths', 'derived_RAM_and_producer_dependencies_preserved'),
    ('bfs_state_caller_withdrawal_paths', 'complete_state_transitions_and_quantity_window'),
    ('bfs_state_caller_withdrawal_paths', 'complete_natural_calls_live_stores_CPU_frame_and_RAM'),
    ('bfs_state_caller_withdrawal_paths', 'complete_direct_helpers_same_primary'),
    ('bfs_state_caller_withdrawal_paths', 'complete_existing_byte_factor_original_same_primary'),
    ('bfs_state_caller_withdrawal_paths', 'native_bindings')))
def test_joint_withdrawal_requires_both_independent_components_and_all_domain_flags(models,monkeypatch,component,flag):
    _,before,_=models
    for key,consumer in proof.COMPONENTS.items():
        result={proof.COMPONENT_FLAGS[key]:True,'no_selected_datum_access':True,'native_identity_admission':False}
        if key in ('rpm_ram_withdrawal_paths','register_overflow_paths','rpm_state_withdrawal_paths','indexed_word_update_paths','division_caller_withdrawal_paths','byte_curve_caller_withdrawal_paths','word_interp_caller_withdrawal_paths','curve_scale_caller_withdrawal_paths','derivative_scale_caller_withdrawal_paths','guarded_quotient_caller_withdrawal_paths','mixed_curve_caller_withdrawal_paths','timing_remainder_caller_withdrawal_paths','dfco_state_caller_withdrawal_paths','paired_inhibit_writer_withdrawal_paths','threshold_window_reader_withdrawal_paths','byte_factor_caller_withdrawal_paths','byte_sum_caller_withdrawal_paths'):result['no_selected_ram_datum_access']=True
        if key in ('division_caller_withdrawal_paths','byte_curve_caller_withdrawal_paths','scaled_division_caller_withdrawal_paths','curve_scale_caller_withdrawal_paths','derivative_scale_caller_withdrawal_paths','guarded_quotient_caller_withdrawal_paths','mixed_curve_caller_withdrawal_paths','timing_remainder_caller_withdrawal_paths','state_ratio_caller_withdrawal_paths','threshold_window_reader_withdrawal_paths','aux_rate_caller_withdrawal_paths','paired_curve_normalization_withdrawal_paths','byte_ratio_producer_withdrawal_paths','state_surface_caller_withdrawal_paths','byte_factor_caller_withdrawal_paths','byte_sum_caller_withdrawal_paths'):result['complete_direct_helpers_same_primary']=True
        if key=='word_interp_caller_withdrawal_paths':result['complete_timing_helpers_same_primary']=True
        if key=='scaled_division_caller_withdrawal_paths':result['complete_register_helpers_same_primary']=True
        if key=='curve_scale_caller_withdrawal_paths':result.update(complete_curve_helpers_same_primary=True,**uptight_RAM3348_flags())
        if key=='derivative_scale_caller_withdrawal_paths':
            result.update(complete_timing_helpers_same_primary=True,complete_normalization_helpers_same_primary=True,complete_viridian_caller_same_primary=True)
        if key=='mixed_curve_caller_withdrawal_paths':
            result.update(complete_timing_helpers_same_primary=True,complete_implicit_caller_same_primary=True,complete_register_helpers_same_primary=True)
        if key=='timing_remainder_caller_withdrawal_paths':
            result.update(complete_timing_helpers_same_primary=True,complete_normalization_helpers_same_primary=True,complete_viridian_caller_same_primary=True,complete_remainder_source_same_primary=True)
        if key=='state_ratio_caller_withdrawal_paths':
            result.update(complete_previous_byte_curve_caller_same_primary=True,complete_standard_implicit_byte_same_primary=True)
        if key=='dfco_state_caller_withdrawal_paths':result.update(complete_real_rotation_helper=True,**dfco_direction_flags())
        if key=='paired_inhibit_writer_withdrawal_paths':result.update(complete_real_nibble_helper=True,entry_scoped_root_absence=True,complete_RMW_read_write_pairs=True)
        if key=='threshold_window_reader_withdrawal_paths':result['complete_previous_byte_curve_caller_same_primary']=True
        if key=='aux_rate_caller_withdrawal_paths':result['complete_real_auxiliary_gate']=True
        if key=='paired_curve_normalization_withdrawal_paths':result.update(complete_previous_byte_curve_caller_same_primary=True,complete_previous_mixed_curve_caller_same_primary=True,complete_raw16_axis17_data=True)
        if key=='byte_ratio_producer_withdrawal_paths':result.update(complete_signed_shift10=True,complete_actual_post_DIV1_R1_carrier=True)
        if key=='state_surface_caller_withdrawal_paths':result.update(complete_local_word_argument=True,complete_three_state_modes=True)
        if key=='byte_factor_caller_withdrawal_paths':result.update(complete_signed_word_difference=True,complete_dual_byte_partial_product=True,complete_both_natural_curve_calls=True)
        if key=='byte_sum_caller_withdrawal_paths':result.update(complete_clipped_byte_coordinate=True,complete_unsigned_byte_minimum=True,complete_two_saturating_word_sums=True)
        if key=='clamp_latch_caller_withdrawal_paths':result.update(clamp_latch_flags())
        if key=='paired_word_curve_sum_withdrawal_paths':result.update(paired_word_sum_flags())
        if key in proof.REMAINING_CALLER_FLAGS:result.update(remaining_caller_flags(key))
        if key==component:result[flag]=not result[flag]
        monkeypatch.setattr(consumer,'require_primary',lambda *args,result=result:result)
    with pytest.raises(ValueError):proof.require_primary(before,controlled_primary())


def controlled_primary():
    paths=(contract.DESCRIPTOR,'tools/kb/src/kb/scalar_ram_leaf_withdrawal_contract.py',
        'tools/kb/src/kb/scalar_ram_leaf_withdrawal_evidence.py','tools/kb/src/kb/scalar_ram_leaf_withdrawal_resolution.py')
    return dict(candidate=dict(producer_inputs={path:hashlib.sha256((repo.ROOT/path).read_bytes()).hexdigest()
        for path in paths}),process_sha256='controlled-original',native_model='controlled-native')


def test_joint_admission_calls_each_independent_component_with_the_identical_primary_record(models,monkeypatch):
    _,before,_=models;record=controlled_primary();seen=[]
    for key,consumer in proof.COMPONENTS.items():
        def require(model,actual,key=key):
            assert model is before and actual is record;seen.append(key)
            return dict({proof.COMPONENT_FLAGS[key]:True,'no_selected_datum_access':True,
                'no_selected_ram_datum_access':True,'native_identity_admission':False,'complete_direct_helpers_same_primary':True,'complete_timing_helpers_same_primary':True,'complete_register_helpers_same_primary':True,'complete_curve_helpers_same_primary':True,'complete_normalization_helpers_same_primary':True,'complete_viridian_caller_same_primary':True,'complete_implicit_caller_same_primary':True,'complete_remainder_source_same_primary':True,'complete_previous_byte_curve_caller_same_primary':True,'complete_standard_implicit_byte_same_primary':True,'complete_real_rotation_helper':True,'complete_real_nibble_helper':True,'entry_scoped_root_absence':True,'complete_RMW_read_write_pairs':True,'complete_real_auxiliary_gate':True,'complete_previous_mixed_curve_caller_same_primary':True,'complete_raw16_axis17_data':True,'complete_signed_shift10':True,'complete_actual_post_DIV1_R1_carrier':True,'complete_local_word_argument':True,'complete_three_state_modes':True,'complete_signed_word_difference':True,'complete_dual_byte_partial_product':True,'complete_both_natural_curve_calls':True,'complete_clipped_byte_coordinate':True,'complete_unsigned_byte_minimum':True,'complete_two_saturating_word_sums':True},**(dfco_direction_flags() if key=='dfco_state_caller_withdrawal_paths' else {}),**(uptight_RAM3348_flags() if key=='curve_scale_caller_withdrawal_paths' else {}),**(clamp_latch_flags() if key=='clamp_latch_caller_withdrawal_paths' else {}),**(paired_word_sum_flags() if key=='paired_word_curve_sum_withdrawal_paths' else {}),**(remaining_caller_flags(key) if key in proof.REMAINING_CALLER_FLAGS else {}))
        monkeypatch.setattr(consumer,'require_primary',require)
    result=proof.require_primary(before,record)
    assert set(seen)==set(proof.COMPONENTS)=={'scalar_ram_leaf_paths','scalar_ram_product_paths','scalar_ram_gated_paths','rpm_ram_withdrawal_paths','register_overflow_paths','scalar_ram_word_paths','rpm_state_withdrawal_paths','indexed_word_update_paths','division_caller_withdrawal_paths','byte_curve_caller_withdrawal_paths','word_interp_caller_withdrawal_paths','scaled_division_caller_withdrawal_paths','curve_scale_caller_withdrawal_paths','derivative_scale_caller_withdrawal_paths','guarded_quotient_caller_withdrawal_paths','mixed_curve_caller_withdrawal_paths','timing_remainder_caller_withdrawal_paths','state_ratio_caller_withdrawal_paths','dfco_state_caller_withdrawal_paths','paired_inhibit_writer_withdrawal_paths','threshold_window_reader_withdrawal_paths','aux_rate_caller_withdrawal_paths','paired_curve_normalization_withdrawal_paths','byte_ratio_producer_withdrawal_paths','state_surface_caller_withdrawal_paths','byte_factor_caller_withdrawal_paths','byte_sum_caller_withdrawal_paths','clamp_latch_caller_withdrawal_paths','paired_word_curve_sum_withdrawal_paths','misfire_tail_dispatch_withdrawal_paths','endpoint_normalizer_writer_withdrawal_paths','bfs_state_caller_withdrawal_paths'}
    assert len(seen)==32 and len(result['original_claims'])==132


def test_changed_existing_physical_namespace_cannot_be_hidden_by_withdrawal_admission(models,monkeypatch):
    _,before,after=models
    monkeypatch.setattr(copy_evidence,'scope_digest',lambda model:'before' if model is before else 'after')
    monkeypatch.setattr(proof,'require_current',lambda model:dict(controlled_only=True))
    with pytest.raises(ValueError):resolution.require_transition(before,after)


@pytest.mark.parametrize('fault',('property','type','link-order','other-link','ledger-field','ledger-identity','ledger-note','selector'))
def test_full_native_postimage_refuses_any_unrelated_value_or_position(models,monkeypatch,fault):
    rows,_,after=models
    row=next(row for row in rows if len(json.loads(row['proposed_native_json']).get('link',()))>=2
        and any(marker.get('dependency') for marker in (json.loads(row['proposed_ledger_json']) or ())))
    changed=json.loads(row['proposed_native_json'])
    if fault=='property':changed['unit']='unregistered'
    elif fault=='type':changed['width']='unregistered'
    elif fault=='link-order':changed['link'].reverse()
    elif fault=='other-link':changed['link'].pop()
    elif fault=='ledger-field':changed['ledger'][0].setdefault('fields',[]).append('other')
    elif fault=='ledger-identity':changed['ledger'][0].setdefault('identity',[]).append(999)
    elif fault=='ledger-note':changed['ledger'][0].setdefault('notes',[]).append(999)
    else:next(marker for marker in changed['ledger'] if marker.get('dependency'))['dependency'].pop()
    load=store.load
    monkeypatch.setattr(store,'load',lambda root,path,overlay=None:deepcopy(changed)
        if str(path)==row['source'] else load(root,path,overlay))
    with pytest.raises(ValueError):proof.native_rows(after,'proposed')


@pytest.mark.parametrize('fault',('property','TEST','TEST-order','function-owner'))
def test_every_complete_function_and_original_TEST_position_remain_exact(models,monkeypatch,fault):
    _,_,after=models
    row=next(row for row in contract.descriptor(repo.ROOT)['function'] if row['owner']=='fuel_base_accumulator/fn')
    changed=json.loads(row['original_native_json'])
    def corrupt(value):
        if isinstance(value,dict):
            evidence=value.get('evidence')
            if isinstance(evidence,list) and any(item.get('kind')=='test' for item in evidence):
                if fault=='TEST':evidence.pop(next(index for index,item in enumerate(evidence) if item.get('kind')=='test'))
                else:evidence.reverse()
                return True
            return any(corrupt(item) for item in value.values())
        if isinstance(value,list):return any(corrupt(item) for item in value)
        return False
    if fault=='property':changed['summary']='unregistered'
    elif fault=='function-owner':changed['role']='unregistered'
    else:assert corrupt(changed)
    load=store.load
    monkeypatch.setattr(store,'load',lambda root,path,overlay=None:deepcopy(changed)
        if str(path)==row['source'] else load(root,path,overlay))
    with pytest.raises(ValueError):proof.native_rows(after,'proposed')


@pytest.mark.parametrize('field,value',(('mode','base'),('key',contract.PREFIX+'other'),('supports','identity'),('supports','scale')))
def test_reserved_withdrawal_namespace_cannot_donate_any_owning_fact(models,monkeypatch,field,value):
    rows,before,_=models;row=rows[0];symbol=before.symbols[contract.symbol_key(row)]
    function=next(member for member in before.symbols.values() if member.kind=='fn' and member.address==row['function'])
    item=dict(kind='indirect',mode=contract.MODE,path=contract.DESCRIPTOR,key=contract.PREFIX+row['id']);item[field]=value
    monkeypatch.setattr(proof,'accepted',lambda *args:pytest.fail('withdrawal reaches owning admission'))
    assert copy_evidence.failure(item,symbol,before,'identity') is not None
    assert match.rank(item,symbol,before,'identity')==-1
    claim=json.loads(row['original_claim_json']);claim['evidence']=[item]
    assert copy_evidence.accepted(before,symbol,function,claim) is None
    assert contract.publication(None,item) is False and registry.publication(None,item) is False
    assert proof.identity_only(symbol) is False


def test_withdrawal_registration_cannot_enable_direct_owning_or_owner_fallback(monkeypatch):
    family=next(row for row in registry.FAMILIES if row.mode==contract.MODE)
    assert family.mode==contract.MODE and not family.direct_owning and not family.owner_fallback
    for field in ('direct_owning','owner_fallback'):
        monkeypatch.setattr(registry,'FAMILIES',tuple(replace(row,**{field:True}) if row is family else row
            for row in registry.FAMILIES))
        with pytest.raises(ValueError):registry.families()
        monkeypatch.undo()


def test_reuse_description_exposes_withdrawal_without_inventing_a_proposed_claim_or_evidence():
    from kb import proof_reuse
    selected=[row for row in proof_reuse.index(repo.ROOT)['references'] if row['family']==contract.MODE]
    assert len(selected)==132
    assert {row['original'] for row in selected}=={row[10] for row in contract.IDENTITIES}
    assert all(row['disposition']=='withdrawal' and row['evidence'] is None and row['width'] is None
        and row['source_prepared'] is True and row['accepted'] is False for row in selected)


def test_withdrawal_never_donates_owning_scale_or_reverse_identity_through_level_collection(models,monkeypatch):
    rows,model,_=models;row=next(row for row in rows if row['owner']=='poetic-sidewinder/tbl')
    link=next(link for link in model.links if contract.original(row,link))
    own=levels.Claim('controlled','owner','identity','code')
    scale=levels.Claim('controlled','scale','scale','code');reverse=levels.Claim('controlled','fn','identity','code')
    collector=object.__new__(levels._Collector);collector.model,collector.pointed,collector.symbols=model,set(),{}
    collector.meanings={(id(link.owner),'identity'):own,(id(link.owner),'scale'):scale,(id(link.to),'identity'):reverse}
    monkeypatch.setattr(proof,'link_failure',lambda *args:None)
    collector._link(link)
    assert own.items==[] and len(own.deps)==1 and own.deps[0].lacks
    assert scale.items==scale.deps==reverse.items==reverse.deps==[]


def test_prior_nineteen_full_records_and_twelve_functions_retain_their_exact_boundary():
    declared=contract.descriptor(repo.ROOT)
    assert len(declared['reference'])==132 and len(declared['function'])==73
    assert {row['component'] for row in declared['reference'][:19]}=={'scalar_ram_leaf_paths'}
    assert {row['component'] for row in declared['reference'][19:26]}=={'scalar_ram_product_paths'}
    contract.require_prior_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('fault',('original-json','source','type','component','row-order','function-json','function-order'))
def test_prior_boundary_rejects_full_original_field_and_position_substitution(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][0]
    if fault=='original-json':row['original_claim_json']=row['original_claim_json']+' '
    elif fault=='source':row['source']='other.toml'
    elif fault=='type':row['declared_width']='word'
    elif fault=='component':row['component']='scalar_ram_product_paths'
    elif fault=='row-order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_FILES_SHA256))
def test_prior_fixture_input_scalar_physical_producer_and_generated_sources_remain_byte_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_boundary(repo.ROOT,declared)


def test_shared_owner_postimages_remove_only_the_new_reader_and_exact_matching_selector():
    rows=contract.descriptor(repo.ROOT)['reference']
    shared={'tuscan-porcupine/tbl','soft-pronghorn/tbl'}
    assert {row['owner'] for row in rows[:19]}&{row['owner'] for row in rows[19:26]}==shared
    for owner in shared:
        old=next(row for row in rows[:19] if row['owner']==owner)
        new=next(row for row in rows[19:26] if row['owner']==owner)
        assert old['original_native_json']==new['original_native_json']
        assert old['proposed_native_json']==new['proposed_native_json']
        before=json.loads(old['original_native_json']);after=json.loads(old['proposed_native_json'])
        selected=[row for row in rows if row['owner']==owner]
        assert len(selected)==2
        expected=deepcopy(before)
        for row in selected:
            original=json.loads(row['original_claim_json'])
            expected['link']=[link for link in expected['link'] if not (
                link['type']==original['type'] and link['to']==original['to'])]
            for marker in expected.get('ledger',()):
                if 'dependency' in marker:
                    marker['dependency']=[item for item in marker['dependency'] if not contract.selector(row,owner,item)]
                    if not marker['dependency']:marker.pop('dependency')
        if not expected.get('link'):expected.pop('link',None)
        assert expected==after


def test_complete_prior_twenty_six_records_and_sixteen_functions_retain_their_exact_boundary():
    declared=contract.descriptor(repo.ROOT)
    assert len(declared['reference'])==132 and len(declared['function'])==73
    contract.require_prior_joint_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('fault',('original-json','source','type','component','row-order','function-json','function-order'))
def test_prior_joint_boundary_rejects_original_record_and_function_substitution(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][20]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='source':row['source']='other.toml'
    elif fault=='type':row['declared_signed']='signed'
    elif fault=='component':row['component']='scalar_ram_gated_paths'
    elif fault=='row-order':declared['reference'][20],declared['reference'][21]=declared['reference'][21],declared['reference'][20]
    elif fault=='function-json':declared['function'][14]['original_native_json']+=' '
    else:declared['function'][14],declared['function'][15]=declared['function'][15],declared['function'][14]
    with pytest.raises(ValueError):contract.require_prior_joint_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_PRODUCT_FILES_SHA256))
def test_prior_product_fixture_input_scalar_physical_producer_and_generated_sources_remain_byte_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_joint_boundary(repo.ROOT,declared)


def test_gated_shared_owner_delta_is_exactly_the_additional_selected_reader_and_selector():
    rows=contract.descriptor(repo.ROOT)['reference']
    shared={'cautious-iguana/tbl','rev_limit_throttle_cut/tbl'}
    assert {row['owner'] for row in rows[:26]}&{row['owner'] for row in rows[26:31]}==shared
    for owner in shared:
        selected=[row for row in rows if row['owner']==owner]
        assert len([row for row in selected if row['component']=='scalar_ram_gated_paths'])==1
        before=json.loads(selected[0]['original_native_json']);expected=deepcopy(before)
        for row in selected:
            old=json.loads(row['original_claim_json'])
            expected['link']=[link for link in expected['link'] if not (link['type']==old['type'] and link['to']==old['to'])]
            for marker in expected.get('ledger',()):
                if 'dependency' in marker:
                    marker['dependency']=[item for item in marker['dependency'] if not contract.selector(row,owner,item)]
                    if not marker['dependency']:marker.pop('dependency')
        if not expected.get('link'):expected.pop('link',None)
        assert all(expected==json.loads(row['proposed_native_json']) for row in selected)


def test_complete_prior_thirty_one_records_and_twenty_one_functions_remain_directly_exact():
    declared=contract.descriptor(repo.ROOT)
    assert len(declared['reference'])==132 and len(declared['function'])==73
    contract.require_prior_gated_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('fault',('original-json','proposed-json','source','row-order','function-json','function-order'))
def test_prior_gated_full_record_boundary_cannot_change_any_field_or_position(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][28]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='source':row['source']='other.toml'
    elif fault=='row-order':declared['reference'][28],declared['reference'][29]=declared['reference'][29],declared['reference'][28]
    elif fault=='function-json':declared['function'][19]['original_native_json']+=' '
    else:declared['function'][19],declared['function'][20]=declared['function'][20],declared['function'][19]
    with pytest.raises(ValueError):contract.require_prior_gated_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_GATED_FILES_SHA256))
def test_prior_gated_fixture_matrix_scalar_physical_producer_and_generated_sources_are_byte_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_gated_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('row',contract.RELATED_OWNER_INPUTS)
def test_complete_counter_and_MAF_source_references_cannot_change(monkeypatch,row):
    declared=contract.descriptor(repo.ROOT);name=row[0];read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_gated_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('roles',([],['reader'],['indexed_by','reader']))
def test_selected_indexed_by_original_cannot_be_replaced_by_another_role(tmp_path,roles):
    from kb.diagnostic_rom_contract import digest
    declared=deepcopy(contract.descriptor(repo.ROOT))
    row=next(row for row in declared['reference'] if row['id']=='0004f958-ffff11ae-withdraw')
    old=json.loads(row['original_claim_json']);old['roles']=roles
    assert digest(old)!=row['original_claim_sha256']
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text()
    text=text.replace('original_claim_json = '+json.dumps(row['original_claim_json']),
        'original_claim_json = '+json.dumps(json.dumps(old,sort_keys=True,separators=(',',':'),ensure_ascii=True)),1)
    path.write_text(text)
    with pytest.raises(ValueError,match='original|native content'):contract.descriptor(tmp_path)


def test_complete_prior_thirty_four_records_and_twenty_four_functions_remain_exact():
    declared=contract.descriptor(repo.ROOT)
    assert len(declared['reference'])==132 and len(declared['function'])==73
    contract.require_prior_rpm_ram_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('fault',('original-json','proposed-json','role','row-order','function-json','function-order'))
def test_prior_RPM_RAM_full_record_and_original_role_boundary_cannot_change(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][31]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='role':
        old=json.loads(row['original_claim_json']);old['roles']=[];row['original_claim_json']=json.dumps(old)
    elif fault=='row-order':declared['reference'][31],declared['reference'][32]=declared['reference'][32],declared['reference'][31]
    elif fault=='function-json':declared['function'][22]['original_native_json']+=' '
    else:declared['function'][22],declared['function'][23]=declared['function'][23],declared['function'][22]
    with pytest.raises(ValueError):contract.require_prior_rpm_ram_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_RPM_RAM_FILES_SHA256))
def test_prior_RPM_RAM_fixture_input_scalar_physical_producer_and_generated_sources_are_byte_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_rpm_ram_boundary(repo.ROOT,declared)


def test_complete_prior_thirty_five_records_and_twenty_five_functions_retain_exact_prefix_images():
    declared=contract.descriptor(repo.ROOT)
    assert len(declared['reference'])==132 and len(declared['function'])==73
    contract.require_prior_overflow_boundary(repo.ROOT,declared)
    prior=contract.prior_reference_rows(declared,35)
    assert contract.digest(prior)==contract.PRIOR_OVERFLOW_REFERENCE_SHA256
    changed={r['owner'] for r,old in zip(declared['reference'],prior) if r!=old}
    assert changed=={'rev_limit_throttle_cut/tbl','tough-earwig/ram','opal-camel/tbl','complex-condor/tbl','garrulous-civet/tbl','idle_ignition_timing/tbl'}


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','row-order','function-json','function-order'))
def test_word_extension_preserves_full_prior_records_beyond_the_single_shared_delta(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][0]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault=='row-order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_overflow_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_OVERFLOW_FILES_SHA256))
def test_preceding_overflow_domain_and_generated_sources_retain_exact_bytes(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_prior_overflow_boundary(repo.ROOT,declared)


def test_explicit_gated_shift_source_repair_reconstructs_the_exact_legacy_frozen_bytes():
    repair=contract.GATED_ASSEMBLY_SOURCE_REPAIR
    current=(repo.ROOT/repair['path']).read_bytes()
    previous=contract.prior_gated_source_bytes(repo.ROOT,repair['path'])
    assert hashlib.sha256(current).hexdigest()==repair['after_sha256']
    assert hashlib.sha256(previous).hexdigest()==repair['before_sha256']==contract.PRIOR_GATED_FILES_SHA256[repair['path']]
    assert current!=previous and repair['instruction_words_changed'] is False
    assert current.count(b'L_00044468:\n    shll2 r11')==1
    assert current.count(b'L_00074c5a:\n    shll16 r2')==1


@pytest.mark.parametrize('fault',('other-byte','missing-site','wrong-shift'))
def test_explicit_gated_source_correction_admits_no_other_assembly_change(monkeypatch,fault):
    name=contract.GATED_ASSEMBLY_SOURCE_REPAIR['path'];read=Path.read_bytes
    raw=read(repo.ROOT/name)
    changed=raw+b'\n' if fault=='other-byte' else raw.replace(b'L_00044468:',b'L_00044466:') if fault=='missing-site' else raw.replace(b'shll2 r11',b'shll8 r11')
    monkeypatch.setattr(Path,'read_bytes',lambda p:changed if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.prior_gated_source_bytes(repo.ROOT,name)


def test_RPM_state_extension_preserves_complete_prior_word_source_and_three_exact_indexed_roles():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_word_boundary(repo.ROOT,declared)
    assert len(declared['reference'])==132 and len(declared['function'])==73
    rows=[r for r in declared['reference'] if r['component']=='rpm_state_withdrawal_paths']
    assert len(rows)==2 and all(json.loads(r['original_claim_json'])['roles']==['indexed_by'] for r in rows)
    assert set(contract.NATIVE_LINK_ROLES)=={'0004f958-ffff11ae-withdraw','0004f7e0-ffff11ae-withdraw','0004f9c4-ffff11ae-withdraw','0003a254-ffff115e-withdraw','000b7c84-ffff33fc-withdraw',
        '000b7b98-ffff1024-withdraw','000b7b98-ffff11bc-withdraw','00072f1e-ffff1d10-withdraw',
        '000b7768-ffff2733-withdraw','000b7768-ffff3348-withdraw','000b78da-ffff110e-withdraw','000b7a3c-ffff110e-withdraw','000b78da-ffff2733-withdraw','000b7a3c-ffff2733-withdraw','000b78da-ffff3348-withdraw','000b7a3c-ffff3348-withdraw','000b78da-ffff35a0-withdraw','000b7a3c-ffff35b6-withdraw','000b784e-ffff3348-withdraw'}
    previous=contract.prior_reference_rows(declared,38)
    assert contract.digest(previous)==contract.PRIOR_WORD_REFERENCE_SHA256
    assert {r['owner'] for r,old in zip(declared['reference'],previous) if r!=old}=={'tough-earwig/ram','scrupulous-yak/tbl','opal-camel/tbl','complex-condor/tbl','garrulous-civet/tbl','idle_ignition_timing/tbl'}


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','role','order','function-json'))
def test_prior_word_full_source_boundary_and_unrelated_roles_cannot_change(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][0]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault=='role':
        old=json.loads(row['original_claim_json']);old['roles']=['indexed_by'];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    else:declared['function'][0]['original_native_json']+=' '
    with pytest.raises(ValueError):contract.require_prior_word_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_WORD_FILES_SHA256))
def test_prior_word_fixture_matrix_scalar_physical_and_generated_sources_remain_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_prior_word_boundary(repo.ROOT,declared)


def test_exact_single_writer_extension_preserves_all_forty_complete_reader_originals_and_thirty_functions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_rpm_state_boundary(repo.ROOT,declared)
    assert contract.digest(contract.prior_reference_rows(declared,40))==contract.PRIOR_RPM_STATE_REFERENCE_SHA256
    assert contract.digest(declared['function'][:30])==contract.PRIOR_RPM_STATE_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    prior,current=declared['reference'][:40],declared['reference'][40]
    assert all(json.loads(row['original_claim_json'])['type']=='reader' for row in prior)
    assert current['id']=='00052034-ffff120e-withdraw' and current['component']=='indexed_word_update_paths'
    assert contract.ORIGINAL_LINK_TYPES[current['id']]=='writer'
    assert set(contract.ORIGINAL_LINK_TYPES)&LEGACY_WRITER_IDS=={'00052034-ffff120e-withdraw','0006e3d8-ffff1300-withdraw','0006e3d8-ffff1f86-withdraw'}
    assert json.loads(current['original_claim_json'])['type']=='writer'
    assert current['original_claim_sha256']=='8173eb6cb77ae22dd0fa72ea3bc4cdb758d15cd421cfac9f79cacfa10055387d'
    assert contract.operation(current)['type']=='writer'


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','order','function-json','function-order'))
def test_exact_prior_forty_record_boundary_refuses_any_type_native_or_order_change(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][0]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault=='type':
        old=json.loads(row['original_claim_json']);old['type']='writer';row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_rpm_state_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_RPM_STATE_FILES_SHA256))
def test_prior_RPM_state_fixture_input_scalar_physical_and_generated_sources_remain_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_prior_rpm_state_boundary(repo.ROOT,declared)


def test_division_callers_preserve_full_prior_forty_one_and_only_exact_shared_reader_delta():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_indexed_word_boundary(repo.ROOT,declared)
    previous=contract.prior_reference_rows(declared,41)
    assert contract.digest(previous)==contract.PRIOR_INDEXED_WORD_REFERENCE_SHA256
    assert contract.digest(declared['function'][:31])==contract.PRIOR_INDEXED_WORD_FUNCTION_SHA256
    assert {r['owner'] for r,old in zip(declared['reference'],previous) if r!=old}=={'scrupulous-yak/tbl','opal-camel/tbl','complex-condor/tbl','garrulous-civet/tbl','idle_ignition_timing/tbl'}
    assert len(declared['reference'])==132 and len(declared['function'])==73
    assert {key:value for key,value in contract.ORIGINAL_LINK_TYPES.items() if key in LEGACY_WRITER_IDS}=={'00052034-ffff120e-withdraw':'writer','0006e3d8-ffff1300-withdraw':'writer','0006e3d8-ffff1f86-withdraw':'writer'}


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','role','order','function-json'))
def test_division_full_prior_records_cannot_change_outside_the_exact_reconstructed_shared_delta(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][0]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role'):
        old=json.loads(row['original_claim_json']);old['type' if fault=='type' else 'roles']='writer' if fault=='type' else ['indexed_by'];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    else:declared['function'][0]['original_native_json']+=' '
    with pytest.raises(ValueError):contract.require_prior_indexed_word_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_INDEXED_WORD_FILES_SHA256))
def test_prior_indexed_word_fixture_input_equations_physical_and_generated_bytes_remain_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_prior_indexed_word_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('phase',('original','proposed'))
def test_exact_absent_native_ledger_cannot_be_replaced_by_empty_or_unrelated_binding(models,phase):
    rows,before,after=models;model=deepcopy(before if phase=='original' else after)
    row=next(row for row in rows if row['owner']=='tacky-barnacle/ram')
    assert json.loads(row['original_ledger_json']) is None and json.loads(row['proposed_ledger_json']) is None
    assert 'ledger' not in json.loads(row['original_native_json'])
    assert not any(f'{name}/{kind}'==row['owner'] for kind,name,_,_ in model.stash.get('ledger_rows',()))
    model.stash.setdefault('ledger_rows',[]).append(('ram','tacky-barnacle',[],row['source']))
    with pytest.raises(ValueError):proof.native_rows(model,phase)


def test_byte_curve_boundary_retains_all_forty_four_full_originals_and_thirty_four_functions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_division_caller_boundary(repo.ROOT,declared)
    assert contract.digest(contract.prior_reference_rows(declared,44))==contract.PRIOR_DIVISION_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:34])==contract.PRIOR_DIVISION_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    rows=declared['reference'][44:49]
    assert {r['component'] for r in rows}=={'byte_curve_caller_withdrawal_paths'}
    assert [(r['id'],json.loads(r['original_claim_json'])['type']) for r in rows]==[
        ('0006e3d8-ffff1300-withdraw','writer'),('0006e3d8-ffff1f86-withdraw','writer'),
        ('0002c59c-ffff2451-withdraw','reader'),('0002c59c-ffff4185-withdraw','reader'),
        ('0002c59c-ffff84c0-withdraw','reader')]
    assert {key:value for key,value in contract.ORIGINAL_LINK_TYPES.items() if key in LEGACY_WRITER_IDS}=={'00052034-ffff120e-withdraw':'writer',
        '0006e3d8-ffff1300-withdraw':'writer','0006e3d8-ffff1f86-withdraw':'writer'}
    assert all(json.loads(r['original_claim_json'])['roles']==[] for r in rows)


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','order','function-json','function-order'))
def test_byte_curve_full_prior_boundary_refuses_changed_type_owner_position_or_native_image(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][0]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault=='type':
        old=json.loads(row['original_claim_json']);old['type']='writer';row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_division_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_DIVISION_CALLER_FILES_SHA256))
def test_all_prior_division_caller_fixture_input_scalar_physical_producer_and_generated_bytes_remain_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_prior_division_caller_boundary(repo.ROOT,declared)


def test_word_caller_boundary_retains_all_forty_nine_full_originals_and_thirty_six_functions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_byte_curve_caller_boundary(repo.ROOT,declared)
    assert contract.digest(contract.prior_reference_rows(declared,49))==contract.PRIOR_BYTE_CURVE_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:36])==contract.PRIOR_BYTE_CURVE_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    rows=declared['reference'][49:54]
    assert {r['component'] for r in rows}=={'word_interp_caller_withdrawal_paths'}
    assert [r['id'] for r in rows]==['00072f1e-000175c8-withdraw','000b7b98-ffff1024-withdraw',
        '000b7b98-ffff11bc-withdraw','00072f1e-ffff1d10-withdraw','00072f1e-ffff35fe-withdraw']
    assert all(json.loads(r['original_claim_json'])['type']=='reader' for r in rows)
    assert [json.loads(r['original_claim_json'])['roles'] for r in rows]==[[],['indexed_by'],['indexed_by'],['indexed_by'],[]]
    assert {key:value for key,value in contract.ORIGINAL_LINK_TYPES.items() if key in LEGACY_WRITER_IDS}=={'00052034-ffff120e-withdraw':'writer',
        '0006e3d8-ffff1300-withdraw':'writer','0006e3d8-ffff1f86-withdraw':'writer'}
    assert [contract.native_type(r,'width') for r in rows]==[None,16,16,None,None]
    assert [contract.native_type(r,'signed') for r in rows]==[None,False,False,None,None]


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','order','function-json','function-order'))
def test_word_caller_prior_boundary_refuses_changed_type_owner_position_or_native_image(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][0]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault=='type':
        old=json.loads(row['original_claim_json']);old['type']='writer';row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_byte_curve_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256))
def test_all_prior_byte_curve_caller_fixture_input_scalar_physical_producer_and_generated_bytes_remain_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_prior_byte_curve_caller_boundary(repo.ROOT,declared)


def test_scaled_callers_retain_every_full_prior54_record_and_all38_functions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_word_interp_caller_boundary(repo.ROOT,declared)
    prior=contract.prior_reference_rows(declared,54)
    assert contract.digest(prior)==contract.PRIOR_WORD_INTERP_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:38])==contract.PRIOR_WORD_INTERP_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    rows=declared['reference'][54:57]
    assert [row['id'] for row in rows]==['0004e59c-00012432-withdraw','00074b04-00015770-withdraw','00074478-00019190-withdraw']
    assert all(row['component']=='scaled_division_caller_withdrawal_paths' and json.loads(row['original_claim_json'])['type']=='reader' for row in rows)
    changed=set()
    for old,current in zip(prior,declared['reference'][:54]):
        held=deepcopy(old)
        for key in ('proposed_native_json','proposed_native_sha256','proposed_ledger_json'):held[key]=current[key]
        assert held==current
        if old!=current:changed.add(old['owner'])
    assert changed=={'kind-kittiwake/tbl','opal-camel/tbl','complex-condor/tbl','garrulous-civet/tbl','idle_ignition_timing/tbl'}


def test_shared_kind_kittiwake_changes_only_the_additional_exact_reader_and_selector():
    declared=contract.descriptor(repo.ROOT);owner='kind-kittiwake/tbl'
    prior=next(row for row in contract.prior_reference_rows(declared,54) if row['owner']==owner)
    current=next(row for row in declared['reference'][54:] if row['owner']==owner)
    document=json.loads(prior['proposed_native_json']);old=json.loads(current['original_claim_json'])
    links=[i for i,item in enumerate(document['link']) if item['type']==old['type'] and item['to']==old['to']]
    assert len(links)==1;document['link'].pop(links[0]);removed=[]
    for marker in document.get('ledger',()):
        if 'dependency' in marker:
            removed.extend(item for item in marker['dependency'] if contract.selector(current,owner,item))
            marker['dependency']=[item for item in marker['dependency'] if not contract.selector(current,owner,item)]
            if not marker['dependency']:marker.pop('dependency')
    if not document.get('link'):document.pop('link',None)
    assert len(removed)==1 and document==json.loads(current['proposed_native_json'])


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','order','function-json','function-order'))
def test_scaling_caller_full_prior_boundary_refuses_changed_record_or_current_image(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][0]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault=='type':
        old=json.loads(row['original_claim_json']);old['type']='writer';row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_word_interp_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_WORD_INTERP_CALLER_FILES_SHA256))
def test_all_prior_word_caller_fixture_input_equation_transfer_producer_and_generated_bytes_are_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_prior_word_interp_caller_boundary(repo.ROOT,declared)


def test_curve_scale_retains_all57_full_records_current_postimages_and41_functions_directly():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_scaled_division_boundary(repo.ROOT,declared)
    assert contract.digest(contract.prior_reference_rows(declared,57))==contract.PRIOR_SCALED_DIVISION_REFERENCE_SHA256
    assert contract.digest(declared['function'][:41])==contract.PRIOR_SCALED_DIVISION_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    rows=declared['reference'][57:60]
    assert [row['id'] for row in rows]==['000b7768-00015c40-withdraw','000b7768-ffff2733-withdraw','000b7768-ffff3348-withdraw']
    assert [json.loads(row['original_claim_json'])['roles'] for row in rows]==[[],['indexed_by'],['indexed_by']]
    assert all(row['component']=='curve_scale_caller_withdrawal_paths' and json.loads(row['original_claim_json'])['type']=='reader' for row in rows)
    assert all(contract.native_type(row,'width') is None and contract.native_type(row,'signed') is None for row in rows)
    assert len(contract.ORIGINAL_LINK_TYPES)==11 and len(contract.NATIVE_LINK_ROLES)==19


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','order','function-json','function-order'))
def test_curve_scale_full_prior_boundary_refuses_changed_native_record_or_position(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][0]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault=='type':
        old=json.loads(row['original_claim_json']);old['type']='writer';row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_scaled_division_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_SCALED_DIVISION_FILES_SHA256))
def test_all_previous_scaling_division_fixture_input_equation_transfer_producer_and_generated_bytes_remain_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_prior_scaled_division_boundary(repo.ROOT,declared)


def test_derivative_callers_retain_every_full_prior60_record_and42_functions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_curve_scale_caller_boundary(repo.ROOT,declared)
    previous=contract.prior_reference_rows(declared,60)
    assert contract.digest(previous)==contract.PRIOR_CURVE_SCALE_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:42])==contract.PRIOR_CURVE_SCALE_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    assert {r['owner'] for r,old in zip(declared['reference'],previous) if r!=old}=={'perky-agama/ram','ruddy-anaconda/ram','opal-camel/tbl','vigilant-rat/tbl','complex-condor/tbl','garrulous-civet/tbl','idle_ignition_timing/tbl'}
    for old,current in zip(previous,declared['reference'][:60]):
        expected=deepcopy(old)
        for key in ('proposed_native_json','proposed_native_sha256','proposed_ledger_json'):expected[key]=current[key]
        assert current==expected
    rows=declared['reference'][60:71]
    assert len(rows)==11 and all(row['component']=='derivative_scale_caller_withdrawal_paths' for row in rows)
    assert all(json.loads(row['original_claim_json'])['type']=='reader' for row in rows)
    assert sum(json.loads(row['original_claim_json'])['roles']==['indexed_by'] for row in rows)==8
    assert len(contract.ORIGINAL_LINK_TYPES)==11 and len(contract.NATIVE_LINK_ROLES)==19


@pytest.mark.parametrize('owner',('perky-agama/ram','ruddy-anaconda/ram'))
def test_shared_owner_changes_only_two_additional_exact_readers_and_their_two_selectors(owner):
    declared=contract.descriptor(repo.ROOT)
    prior=next(row for row in contract.prior_reference_rows(declared,60) if row['owner']==owner)
    historical=contract.uptight_RAM3348_prior_current_rows(declared,124)
    rows=[row for row in historical[60:] if row['owner']==owner]
    assert len(rows)==2 and {row['function'] for row in rows}=={0xB78DA,0xB7A3C}
    document=json.loads(prior['proposed_native_json']);removed=[]
    for row in rows:
        old=json.loads(row['original_claim_json'])
        found=[i for i,item in enumerate(document['link']) if item['type']==old['type'] and item['to']==old['to']]
        assert len(found)==1;link=document['link'].pop(found[0])
        assert link['type']=='reader' and link['role']=='indexed_by' and link.get('evidence',[])==[]
        for marker in document.get('ledger',()):
            if 'dependency' in marker:
                removed.extend(item for item in marker['dependency'] if contract.selector(row,owner,item))
                marker['dependency']=[item for item in marker['dependency'] if not contract.selector(row,owner,item)]
                if not marker['dependency']:marker.pop('dependency')
    if not document.get('link'):document.pop('link',None)
    assert len(removed)==2 and all(document==json.loads(row['proposed_native_json']) for row in rows)


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','role','order','function-json','function-order'))
def test_complete_prior60_and_current_full_postimages_refuse_ignored_fields_or_relaxed_owner_exceptions(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][58]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role'):
        old=json.loads(row['original_claim_json']);old['type' if fault=='type' else 'roles']='writer' if fault=='type' else [];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][58],declared['reference'][59]=declared['reference'][59],declared['reference'][58]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_curve_scale_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256))
def test_complete_preceding_curve_scale_fixture_input_equation_transfer_producer_and_generated_sources_remain_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_prior_curve_scale_caller_boundary(repo.ROOT,declared)


def test_guarded_callers_preserve_every_full_prior71_record_and44_functions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_derivative_scale_caller_boundary(repo.ROOT,declared)
    historical=contract.uptight_RAM3348_prior_current_rows(declared,124)
    previous=contract.prior_reference_rows(declared,71)
    assert contract.digest(previous)==contract.PRIOR_DERIVATIVE_SCALE_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:44])==contract.PRIOR_DERIVATIVE_SCALE_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    assert {r['owner'] for r,old in zip(historical,previous) if r!=old}=={'opal-camel/tbl','vigilant-rat/tbl','complex-condor/tbl','garrulous-civet/tbl','idle_ignition_timing/tbl'}
    for old,current in zip(previous,historical[:71]):
        expected=deepcopy(old)
        for key in ('proposed_native_json','proposed_native_sha256','proposed_ledger_json'):expected[key]=current[key]
        assert current==expected
    rows=declared['reference'][71:79]
    assert len(rows)==8 and all(row['component']=='guarded_quotient_caller_withdrawal_paths' for row in rows)
    assert all(json.loads(row['original_claim_json'])['type']=='reader' and json.loads(row['original_claim_json'])['roles']==[] for row in rows)
    assert len(contract.ORIGINAL_LINK_TYPES)==11 and len(contract.NATIVE_LINK_ROLES)==19


@pytest.mark.parametrize('owner',('opal-camel/tbl','vigilant-rat/tbl'))
def test_each_guarded_shared_owner_removes_only_one_additional_reader_and_matching_selector(owner):
    declared=contract.descriptor(repo.ROOT)
    prior=next(row for row in contract.prior_reference_rows(declared,71) if row['owner']==owner)
    rows=[row for row in declared['reference'][71:79] if row['owner']==owner]
    assert len(rows)==1;row=rows[0];old=json.loads(row['original_claim_json']);document=json.loads(prior['proposed_native_json'])
    found=[i for i,item in enumerate(document['link']) if item['type']==old['type'] and item['to']==old['to']]
    assert len(found)==1;removed_link=document['link'].pop(found[0]);removed=[]
    assert removed_link['type']=='reader' and 'role' not in removed_link and removed_link.get('evidence',[])==[]
    for marker in document.get('ledger',()):
        if 'dependency' in marker:
            removed.extend(item for item in marker['dependency'] if contract.selector(row,owner,item))
            marker['dependency']=[item for item in marker['dependency'] if not contract.selector(row,owner,item)]
            if not marker['dependency']:marker.pop('dependency')
    if not document.get('link'):document.pop('link',None)
    assert len(removed)==1 and document==json.loads(row['proposed_native_json'])


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','role','order','function-json','function-order'))
def test_full_prior71_and_current_postimages_refuse_ignored_fields_or_broad_owner_exceptions(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=next(r for r in declared['reference'][:71] if r['owner']=='opal-camel/tbl')
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role'):
        old=json.loads(row['original_claim_json']);old['type' if fault=='type' else 'roles']='writer' if fault=='type' else ['indexed_by'];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_derivative_scale_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256))
def test_all_preceding_derivative_fixture_input_equation_transfer_producer_and_generated_bytes_are_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_prior_derivative_scale_caller_boundary(repo.ROOT,declared)


def test_mixed_callers_preserve_every_full_prior79_record_and47_functions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_guarded_quotient_caller_boundary(repo.ROOT,declared)
    historical=contract.uptight_RAM3348_prior_current_rows(declared,124)
    previous=contract.prior_reference_rows(declared,79)
    assert contract.digest(previous)==contract.PRIOR_GUARDED_QUOTIENT_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:47])==contract.PRIOR_GUARDED_QUOTIENT_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    assert {r['owner'] for r,old in zip(historical,previous) if r!=old}=={
        'complex-condor/tbl','garrulous-civet/tbl','idle_ignition_timing/tbl'}
    for old,current in zip(previous,historical[:79]):
        expected=deepcopy(old)
        for key in ('proposed_native_json','proposed_native_sha256','proposed_ledger_json'):expected[key]=current[key]
        assert current==expected
    rows=declared['reference'][79:87]
    assert len(rows)==8 and all(row['component']=='mixed_curve_caller_withdrawal_paths' for row in rows)
    assert all(json.loads(row['original_claim_json'])['type']=='reader' and json.loads(row['original_claim_json'])['roles']==[] for row in rows)
    assert len(contract.ORIGINAL_LINK_TYPES)==11 and len(contract.NATIVE_LINK_ROLES)==19
    assert not any(row['original_claim_sha256']=='8c93e593a4428c3b7195cbb174725161a8ac0b87b75ac385bf4de135d7bde09b' for row in declared['reference'])


@pytest.mark.parametrize('owner',('complex-condor/tbl','garrulous-civet/tbl','idle_ignition_timing/tbl'))
def test_each_mixed_shared_owner_removes_only_one_additional_reader_and_matching_selector(owner):
    declared=contract.descriptor(repo.ROOT)
    prior=next(row for row in contract.prior_reference_rows(declared,79) if row['owner']==owner)
    rows=[row for row in declared['reference'][79:87] if row['owner']==owner]
    assert len(rows)==1;row=rows[0];old=json.loads(row['original_claim_json']);document=json.loads(prior['proposed_native_json'])
    found=[i for i,item in enumerate(document['link']) if item['type']==old['type'] and item['to']==old['to']]
    assert len(found)==1;removed_link=document['link'].pop(found[0]);removed=[]
    assert removed_link['type']=='reader' and 'role' not in removed_link and removed_link.get('evidence',[])==[]
    assert {k:v for k,v in removed_link.items() if k not in ('type','to','evidence')}==old['props']
    for marker in document.get('ledger',()):
        if 'dependency' in marker:
            removed.extend(item for item in marker['dependency'] if contract.selector(row,owner,item))
            marker['dependency']=[item for item in marker['dependency'] if not contract.selector(row,owner,item)]
            if not marker['dependency']:marker.pop('dependency')
    if not document.get('link'):document.pop('link',None)
    assert len(removed)==1 and document==json.loads(row['proposed_native_json'])


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','role','order','function-json','function-order'))
def test_full_prior79_and_current_postimages_refuse_ignored_fields_or_broad_owner_exceptions(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=next(r for r in declared['reference'][:79] if r['owner']=='complex-condor/tbl')
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role'):
        old=json.loads(row['original_claim_json']);old['type' if fault=='type' else 'roles']='writer' if fault=='type' else ['indexed_by'];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_guarded_quotient_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256))
def test_all_preceding_guarded_fixture_input_equation_transfer_producer_and_generated_bytes_are_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_prior_guarded_quotient_caller_boundary(repo.ROOT,declared)


def test_timing_remainder_callers_preserve_every_full_prior87_record_and51_functions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_mixed_curve_caller_boundary(repo.ROOT,declared)
    previous=contract.prior_reference_rows(declared,87)
    assert contract.paired_curve_prefix_digest(declared,87)==contract.digest(previous)
    assert contract.digest(previous)==contract.PRIOR_MIXED_CURVE_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:51])==contract.PRIOR_MIXED_CURVE_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    rows=declared['reference'][87:92]
    assert len(rows)==5 and all(row['component']=='timing_remainder_caller_withdrawal_paths' for row in rows)
    assert all(json.loads(row['original_claim_json'])['type']=='reader' and json.loads(row['original_claim_json'])['roles']==[] for row in rows)
    assert [json.loads(row['original_claim_json'])['props']['supports'] for row in rows]==['identity','identity','scale','scale','identity']
    assert not ({row['owner'] for row in rows}&{row['owner'] for row in declared['reference'][:87]})
    assert len(contract.ORIGINAL_LINK_TYPES)==11 and len(contract.NATIVE_LINK_ROLES)==19
    assert not any(row['original_claim_sha256']=='1bedae1cd4278ff4c6f33558fe50ad44f2d58390327a2d716f0c58bcc4925f40' for row in declared['reference'])


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','role','order','function-json','function-order'))
def test_full_prior87_and_current_complete_postimages_refuse_ignored_fields_or_type_substitution(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][79]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role'):
        old=json.loads(row['original_claim_json']);old['type' if fault=='type' else 'roles']='writer' if fault=='type' else ['indexed_by'];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_mixed_curve_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_MIXED_CURVE_CALLER_FILES_SHA256))
def test_all_preceding_mixed_fixture_input_equation_transfer_producer_and_generated_bytes_are_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_mixed_curve_caller_boundary(repo.ROOT,declared)


def test_state_ratio_callers_preserve_every_full_prior92_record_and53_functions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_timing_remainder_caller_boundary(repo.ROOT,declared)
    previous=contract.prior_reference_rows(declared,92)
    assert contract.paired_curve_prefix_digest(declared,92)==contract.digest(previous)
    assert contract.digest(previous)==contract.PRIOR_TIMING_REMAINDER_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:53])==contract.PRIOR_TIMING_REMAINDER_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    rows=declared['reference'][92:100]
    assert len(rows)==8 and all(row['component']=='state_ratio_caller_withdrawal_paths' for row in rows)
    assert all(json.loads(row['original_claim_json'])['type']=='reader' and json.loads(row['original_claim_json'])['roles']==[] for row in rows)
    for row in rows[:3]:
        props=json.loads(row['original_claim_json'])['props']
        assert props==dict(layouts=['7mfk'],relies='structure',reverse_relies='structure',reverse_supports='identity',supports=['identity','scale'])
    assert [json.loads(row['original_claim_json'])['props']['supports'] for row in rows[3:]]==['identity']*5
    assert not ({row['owner'] for row in rows}&{row['owner'] for row in declared['reference'][:92]})
    assert len(contract.ORIGINAL_LINK_TYPES)==11 and len(contract.NATIVE_LINK_ROLES)==19
    assert all(row['owner'].endswith('/tbl') for row in rows)


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','role','order','function-json','function-order','reverse-props','supports-array'))
def test_full_prior92_and_current_complete_postimages_refuse_ignored_fields_or_property_substitution(monkeypatch,fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][87]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role'):
        old=json.loads(row['original_claim_json']);old['type' if fault=='type' else 'roles']='writer' if fault=='type' else ['indexed_by'];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    elif fault=='function-order':declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    else:
        row=declared['reference'][92];old=json.loads(row['original_claim_json'])
        if fault=='reverse-props':old['props'].pop('reverse_supports')
        else:old['props']['supports']='identity'
        row['original_claim_json']=json.dumps(old)
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:declared)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256))
def test_all_preceding_timing_remainder_fixture_input_equation_transfer_producer_and_generated_bytes_are_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_timing_remainder_caller_boundary(repo.ROOT,declared)


def test_DFCO_state_caller_preserves_every_full_prior100_record_and55_functions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_state_ratio_caller_boundary(repo.ROOT,declared)
    previous=contract.prior_reference_rows(declared,100)
    assert contract.paired_curve_prefix_digest(declared,100)==contract.digest(previous)
    assert contract.digest(previous)==contract.PRIOR_STATE_RATIO_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:55])==contract.PRIOR_STATE_RATIO_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    rows=declared['reference'][100:107]
    assert len(rows)==7 and all(row['component']=='dfco_state_caller_withdrawal_paths' for row in rows)
    assert all(json.loads(row['original_claim_json'])['type']=='reader' and json.loads(row['original_claim_json'])['roles']==[] for row in rows)
    assert [json.loads(row['original_claim_json'])['props']['supports'] for row in rows]==['identity']*7
    assert not ({row['owner'] for row in rows}&{row['owner'] for row in declared['reference'][:100]})
    assert len(contract.ORIGINAL_LINK_TYPES)==11 and len(contract.NATIVE_LINK_ROLES)==19
    assert [row['address'] for row in rows[-2:]]==[0xFFFF14BD,0xFFFF14BE]
    assert not any(row['original_claim_sha256']=='1f4d2097a3f3458effbf6627988f7ca56994e2ac95e3acc84ff759a7a665c531' for row in rows)


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','role','order','function-json','function-order'))
def test_full_prior100_and_current_complete_images_refuse_ignored_fields_or_type_substitution(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][92]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role'):
        old=json.loads(row['original_claim_json']);old['type' if fault=='type' else 'roles']='writer' if fault=='type' else ['indexed_by'];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_state_ratio_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_STATE_RATIO_CALLER_FILES_SHA256))
def test_all_preceding_state_ratio_fixture_input_equation_transfer_producer_and_generated_bytes_are_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_state_ratio_caller_boundary(repo.ROOT,declared)


def test_paired_writer_preserves_full_prior107_original_records_and56_functions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_DFCO_state_caller_boundary(repo.ROOT,declared)
    previous=contract.prior_reference_rows(declared,107)
    assert contract.paired_curve_prefix_digest(declared,107)==contract.digest(previous)
    assert contract.digest(previous)==contract.PRIOR_DFCO_STATE_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:56])==contract.PRIOR_DFCO_STATE_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    rows=declared['reference'][107:112]
    assert len(rows)==5 and all(row['component']=='paired_inhibit_writer_withdrawal_paths' for row in rows)
    assert all(json.loads(row['original_claim_json'])['type']=='writer' and json.loads(row['original_claim_json'])['roles']==[] for row in rows)
    assert not ({row['owner'] for row in rows}&{row['owner'] for row in declared['reference'][:107]})
    assert contract.ORIGINAL_LINK_TYPES==dict.fromkeys((*sorted(LEGACY_WRITER_IDS),
        '0007c9a8-ffff4a45-withdraw','0007c9a8-ffff4a70-withdraw','0007c9a8-ffff4ac6-withdraw',
        '0007c8fa-ffff5718-withdraw','0007c9a8-ffff5718-withdraw','0004ba48-ffff23c5-withdraw','000464de-ffff1693-withdraw'),'writer')
    assert len(contract.NATIVE_LINK_ROLES)==19
    props=[json.loads(row['original_claim_json'])['props'] for row in rows]
    assert props[:3]==[dict(layouts=['7mfk'],reverse_relies='level',reverse_supports='identity')]*3
    assert props[3:]==[dict(layouts=['7mfk'],reverse_relies='structure',reverse_supports='identity')]*2
    assert all('relies' not in row and 'supports' not in row for row in props)


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','role','order','function-json','function-order'))
def test_full_prior107_and56_function_prefix_refuses_any_ignored_field_or_position(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][100]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role'):
        old=json.loads(row['original_claim_json']);old['type' if fault=='type' else 'roles']='writer' if fault=='type' else ['indexed_by'];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_DFCO_state_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_DFCO_STATE_CALLER_FILES_SHA256))
def test_all_preceding_DFCO_fixture_input_equation_transfer_producer_and_generated_bytes_are_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_DFCO_state_caller_boundary(repo.ROOT,declared)


def test_exact_two_function_postimages_remove_five_reverse_selectors_and_keep_all_other_native_fields():
    declared=contract.descriptor(repo.ROOT);contract.require_function_postimages(declared)
    functions=declared['function'][56:58];assert len(functions)==2;removed=0
    claims=declared['reference'][107:112]
    for row in functions:
        before=contract.function_native_document(row,'original');after=contract.function_native_document(row,'proposed')
        assert {k:v for k,v in before.items() if k!='ledger'}=={k:v for k,v in after.items() if k!='ledger'}
        assert before['ledger']==json.loads(row['original_ledger_json'])
        assert after['ledger']==json.loads(row['proposed_ledger_json'])
        expected=deepcopy(before)
        for marker in expected.get('ledger',()):
            old=marker.get('dependency',[])
            kept=[item for item in old if not any(contract.selector(claim,row['owner'],item) for claim in claims)]
            removed+=len(old)-len(kept)
            if 'dependency' in marker:marker['dependency']=kept
        assert expected==after
    assert removed==5


@pytest.mark.parametrize('index',(56,57))
@pytest.mark.parametrize('fault',('before-json','after-json','before-ledger','after-ledger','before-sha','after-sha',
    'owner','function','source','missing-field','extra-field','another-selector','TEST-position','symbol','note','identity'))
def test_two_function_transition_has_no_generic_owner_or_ignored_field_exception(monkeypatch,index,fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['function'][index]
    keys={'before-json':'original_native_json','after-json':'proposed_native_json','before-ledger':'original_ledger_json',
        'after-ledger':'proposed_ledger_json','before-sha':'original_native_sha256','after-sha':'proposed_native_sha256'}
    if fault in keys:row[keys[fault]]+=' '
    elif fault=='owner':row['owner']='other/fn'
    elif fault=='function':row['function']+=2
    elif fault=='source':row['source']='other.toml'
    elif fault=='missing-field':row.pop('proposed_ledger_json')
    elif fault=='extra-field':row['extra']=True
    else:
        document=json.loads(row['proposed_native_json'])
        if fault=='another-selector':next(marker for marker in document['ledger'] if marker.get('dependency'))['dependency'].pop()
        elif fault=='TEST-position':document.setdefault('evidence',[]).append(dict(type='TEST',position='other'))
        elif fault=='symbol':document['symbol'].reverse();document['symbol'].append(deepcopy(document['symbol'][0]))
        elif fault=='note':document['ledger'][0].setdefault('notes',[]).append('other')
        else:document['ledger'][0].setdefault('identity',[]).append(999)
        row['proposed_native_json']=json.dumps(document,sort_keys=True,separators=(',',':'))
        row['proposed_native_sha256']=contract.digest(document)
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:declared)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


@pytest.mark.parametrize('phase',('original','proposed'))
def test_function_native_phase_cannot_mix_original_and_proposed_ledgers(models,monkeypatch,phase):
    _,before,after=models;model=before if phase=='original' else after
    row=contract.descriptor(repo.ROOT)['function'][56];changed=contract.function_native_document(row,'proposed' if phase=='original' else 'original')
    load=store.load
    monkeypatch.setattr(store,'load',lambda root,path,overlay=None:deepcopy(changed) if str(path)==row['source'] else load(root,path,overlay))
    with pytest.raises(ValueError):proof.native_rows(model,phase)


@pytest.mark.parametrize('phase',('before','after','',None,True))
def test_function_native_phase_requires_exact_original_or_proposed(phase):
    row=contract.descriptor(repo.ROOT)['function'][56]
    with pytest.raises(ValueError):contract.function_native_document(row,phase)


def test_threshold_window_retains_full112_prefix_and58_function_records_including_both_postimages():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_paired_inhibit_writer_boundary(repo.ROOT,declared)
    historical=contract.uptight_RAM3348_prior_current_rows(declared,124)
    prior=contract.prior_reference_rows(declared,112)
    assert contract.digest(prior)==contract.PRIOR_PAIRED_INHIBIT_WRITER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:58])==contract.PRIOR_PAIRED_INHIBIT_WRITER_FUNCTION_SHA256
    assert contract.paired_curve_prefix_digest(declared,107)==contract.digest(prior[:107])
    changed={old['owner'] for old,current in zip(prior,historical) if old!=current}
    assert changed=={'rampant-lobster/ram','realistic-capybara/ram','neon-seagull/ram'}
    for old,current in zip(prior,historical):
        expected=deepcopy(old)
        for field in ('proposed_native_json','proposed_native_sha256','proposed_ledger_json'):expected[field]=current[field]
        assert expected==current
    assert len(declared['reference'])==132 and len(declared['function'])==73
    rows=declared['reference'][112:115]
    assert len(rows)==3 and all(row['component']=='threshold_window_reader_withdrawal_paths' for row in rows)
    assert all(json.loads(row['original_claim_json'])['type']=='reader' and json.loads(row['original_claim_json'])['roles']==[] for row in rows)
    assert [json.loads(row['original_claim_json'])['props'] for row in rows]==[dict(layouts=['7mfk'],relies='level',supports='identity')]*3
    assert len(contract.ORIGINAL_LINK_TYPES)==11 and len(contract.NATIVE_LINK_ROLES)==19
    assert all(row['declared_width']==row['declared_signed']=='unset' for row in rows)


def test_only_three_exact_reader_links_and_selectors_extend_the_previous_full_shared_owner_postimages():
    declared=contract.descriptor(repo.ROOT);prior=contract.prior_reference_rows(declared,112)
    removed=0
    for row in declared['reference'][112:115]:
        previous=next(old for old in prior if old['owner']==row['owner']);document=json.loads(previous['proposed_native_json'])
        claim=json.loads(row['original_claim_json'])
        indices=[index for index,link in enumerate(document['link']) if link['type']==claim['type'] and link['to']==claim['to']]
        assert len(indices)==1;link=document['link'].pop(indices[0]);assert link['type']=='reader' and link['to']=='devout-avocet/fn'
        for marker in document.get('ledger',()):
            if 'dependency' not in marker:continue
            held=marker['dependency'];kept=[item for item in held if not contract.selector(row,row['owner'],item)]
            removed+=len(held)-len(kept);marker['dependency']=kept
            if not kept:marker.pop('dependency')
        if not document.get('link'):document.pop('link',None)
        assert document==json.loads(row['proposed_native_json'])
        assert contract.digest(document)==row['proposed_native_sha256']
    assert removed==3


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','role','order','function-json','function-order','direct-props','inferred-width','function-postimage'))
def test_full112_shared_prefix_and_new_originals_refuse_ignored_fields_or_inferred_native_facts(monkeypatch,fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][112]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role','direct-props'):
        old=json.loads(row['original_claim_json'])
        if fault=='type':old['type']='writer'
        elif fault=='role':old['roles']=['indexed_by']
        else:old['props']['supports']=['identity']
        row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][107],declared['reference'][108]=declared['reference'][108],declared['reference'][107]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    elif fault=='function-order':declared['function'][56],declared['function'][57]=declared['function'][57],declared['function'][56]
    elif fault=='function-postimage':declared['function'][56]['proposed_native_json']+=' '
    else:row['declared_width']=8
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:declared)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_PAIRED_INHIBIT_WRITER_FILES_SHA256))
def test_all_preceding_paired_fixture_input_equation_transfer_producer_and_generated_bytes_are_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_paired_inhibit_writer_boundary(repo.ROOT,declared)


def test_auxiliary_rate_retains_every_full115_original_and59_full_function_records():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_threshold_window_reader_boundary(repo.ROOT,declared)
    previous=contract.prior_reference_rows(declared,115)
    assert contract.paired_curve_prefix_digest(declared,115)==contract.digest(previous)
    assert contract.digest(previous)==contract.PRIOR_THRESHOLD_WINDOW_READER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:59])==contract.PRIOR_THRESHOLD_WINDOW_READER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    rows=declared['reference'][115:116];assert len(rows)==1
    row=rows[0];old=json.loads(row['original_claim_json'])
    assert row['component']=='aux_rate_caller_withdrawal_paths' and row['owner']=='athletic-swallow/tbl'
    assert row['address']==0x120CE and row['function']==0x68D58
    assert old['type']=='reader' and old['roles']==[] and old['evidence']==[]
    assert old['props']==dict(layouts=['7mfk'],relies='structure',supports='identity')
    assert row['owner'] not in {prior['owner'] for prior in declared['reference'][:115]}
    assert len(contract.ORIGINAL_LINK_TYPES)==11 and len(contract.NATIVE_LINK_ROLES)==19
    assert contract.FUNCTION_POSTIMAGE_IDENTITIES and len(contract.FUNCTION_POSTIMAGE_IDENTITIES)==5


@pytest.mark.parametrize('fault',('original-json','proposed-json','ledger-json','type','role','order','function-json','function-order','paired-function-postimage'))
def test_full115_native_current_images_and59_function_prefix_refuse_any_ignored_field_or_position(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][112]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='proposed-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role'):
        old=json.loads(row['original_claim_json']);old['type' if fault=='type' else 'roles']='writer' if fault=='type' else ['indexed_by'];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    elif fault=='paired-function-postimage':declared['function'][56]['proposed_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_threshold_window_reader_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_THRESHOLD_WINDOW_READER_FILES_SHA256))
def test_all_preceding_threshold_window_fixture_inputs_equations_transfers_producer_and_generated_bytes_are_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_threshold_window_reader_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('count,pin',((87,'PRIOR_MIXED_CURVE_CALLER_REFERENCE_SHA256'),
    (92,'PRIOR_TIMING_REMAINDER_CALLER_REFERENCE_SHA256'),(100,'PRIOR_STATE_RATIO_CALLER_REFERENCE_SHA256'),
    (107,'PRIOR_DFCO_STATE_CALLER_REFERENCE_SHA256'),(115,'PRIOR_THRESHOLD_WINDOW_READER_REFERENCE_SHA256'),
    (116,'PRIOR_AUX_RATE_CALLER_REFERENCE_SHA256')))
def test_paired_curve_preserves_every_full_prefix_with_only_two_exact_shared_reader_deltas(count,pin):
    declared=contract.descriptor(repo.ROOT);previous=contract.prior_reference_rows(declared,count)
    historical=contract.uptight_RAM3348_prior_current_rows(declared,124)
    assert contract.paired_curve_prefix_digest(declared,count)==contract.digest(previous)==getattr(contract,pin)
    changed=[index for index,(old,new) in enumerate(zip(previous,historical[:count])) if old!=new]
    assert changed==([79,99] if count>99 else [79])
    old,new=previous[79],declared['reference'][79]
    postimage={'proposed_native_json','proposed_native_sha256','proposed_ledger_json'}
    assert {key:value for key,value in old.items() if key not in postimage}=={key:value for key,value in new.items() if key not in postimage}
    before,after=(json.loads(row['proposed_native_json']) for row in (old,new))
    selected=[json.loads(row['original_claim_json']) for row in declared['reference'][116:118]]
    expected=deepcopy(before)
    for claim in selected:
        matches=[item for item in expected['link'] if (item['type'],item['to'])==(claim['type'],claim['to'])]
        assert len(matches)==1 and claim['type']=='reader' and claim['roles']==[] and claim['evidence']==[]
        expected['link'].remove(matches[0])
    for marker in expected['ledger']:
        if 'dependency' in marker:
            marker['dependency']=[item for item in marker['dependency'] if not any(
                item.get('end')=='owner' and item.get('type')==claim['type'] and item.get('to')==claim['to'] for claim in selected)]
            if not marker['dependency']:marker.pop('dependency')
    if not expected.get('link'):expected.pop('link',None)
    assert test_contract.exact(expected,after)


def test_paired_curve_retains_all_sixty_full_functions_and_both_exact_prior_function_transitions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_aux_rate_caller_boundary(repo.ROOT,declared)
    assert contract.digest(declared['function'][:60])==contract.PRIOR_AUX_RATE_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    assert [(row['owner'],row['function']) for row in declared['function'][60:62]]==[
        ('vigorous-saluki/fn',0x655B4),('silky-vulture/fn',0x65B08)]
    assert all('proposed_native_json' not in row for row in declared['function'][60:64])
    contract.require_function_postimages(declared)
    assert len(contract.FUNCTION_POSTIMAGE_IDENTITIES)==5 and len(contract.FUNCTION_POSTIMAGE_CLAIMS)==8
    assert len(contract.ORIGINAL_LINK_TYPES)==11 and len(contract.NATIVE_LINK_ROLES)==19


@pytest.mark.parametrize('fault',('claim-id','claim-type','claim-role','claim-evidence','claim-function',
    'extra-claim','prefix-order','shared-source','shared-original','current-json','current-ledger','extra-field',
    'extra-link','TEST','selector-order','selector-extent','function-json','function-order','paired-function-postimage'))
def test_paired_curve_exact_shared_transition_refuses_every_additional_field_scope_or_position(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][79];claim=declared['reference'][116]
    if fault=='claim-id':claim['id']='unregistered'
    elif fault=='claim-function':claim['function']+=2
    elif fault in ('claim-type','claim-role','claim-evidence'):
        old=json.loads(claim['original_claim_json'])
        old[{'claim-type':'type','claim-role':'roles','claim-evidence':'evidence'}[fault]]={'claim-type':'writer','claim-role':['indexed_by'],'claim-evidence':[dict(kind='indirect')]}[fault]
        claim['original_claim_json']=json.dumps(old)
    elif fault=='extra-claim':declared['reference'].append(deepcopy(claim))
    elif fault=='prefix-order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='shared-source':row['source']='unregistered'
    elif fault=='shared-original':row['original_native_json']+=' '
    elif fault=='current-json':row['proposed_native_json']+=' '
    elif fault=='current-ledger':row['proposed_ledger_json']+=' '
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    elif fault=='function-order':declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    elif fault=='paired-function-postimage':declared['function'][56]['proposed_native_json']+=' '
    else:
        document=json.loads(row['proposed_native_json'])
        if fault=='extra-field':document['unit']='unregistered'
        elif fault=='extra-link':document.setdefault('link',[]).append(dict(type='reader',to='unregistered/fn'))
        elif fault=='TEST':document['TEST']=[dict(unregistered=True)]
        elif fault=='selector-order':
            marker=next(marker for marker in document['ledger'] if len(marker.get('dependency',()))>1);marker['dependency'].reverse()
        else:next(marker for marker in document['ledger'] if marker.get('dependency'))['dependency'].pop()
        row.update(proposed_native_json=json.dumps(document,sort_keys=True,separators=(',',':'),ensure_ascii=True),
            proposed_native_sha256=contract.digest(document),
            proposed_ledger_json=json.dumps(document.get('ledger'),sort_keys=True,separators=(',',':'),ensure_ascii=True))
    with pytest.raises(ValueError):contract.require_prior_aux_rate_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_AUX_RATE_CALLER_FILES_SHA256))
def test_complete_preceding_auxiliary_rate_domain_sources_remain_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_aux_rate_caller_boundary(repo.ROOT,declared)


def test_byte_ratio_retains_all_full118_current_records_and62_full_function_records():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_paired_curve_normalization_boundary(repo.ROOT,declared)
    historical=contract.uptight_RAM3348_prior_current_rows(declared,124)
    previous=contract.prior_reference_rows(declared,118)
    assert contract.state_surface_current_prefix(previous,declared)==historical[:118]
    assert contract.digest(previous)==contract.PRIOR_PAIRED_CURVE_NORMALIZATION_REFERENCE_SHA256
    assert contract.digest(declared['function'][:62])==contract.PRIOR_PAIRED_CURVE_NORMALIZATION_FUNCTION_SHA256
    row=declared['reference'][118];old=json.loads(row['original_claim_json'])
    assert row['component']=='byte_ratio_producer_withdrawal_paths' and row['owner']=='dramatic-foxhound/tbl'
    assert row['address']==0x12006 and row['function']==0x4AE6C
    assert old['type']=='reader' and old['roles']==[] and old['evidence']==[]
    assert old['props']==dict(layouts=['7mfk'],relies='structure',supports='identity')
    assert row['owner'] not in {prior['owner'] for prior in declared['reference'][:118]}
    assert len(contract.ORIGINAL_LINK_TYPES)==11 and len(contract.NATIVE_LINK_ROLES)==19
    assert len(contract.FUNCTION_POSTIMAGE_IDENTITIES)==5 and len(contract.FUNCTION_POSTIMAGE_CLAIMS)==8
    assert len(declared['reference'])==132 and len(declared['function'])==73


@pytest.mark.parametrize('fault',('original-json','current-json','ledger-json','type','role','order','shared-pair-image',
    'function-json','function-order','paired-function-postimage'))
def test_byte_ratio_prior118_full_images_and62_functions_refuse_ignored_fields_or_positions(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][116]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='current-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role'):
        old=json.loads(row['original_claim_json']);old['type' if fault=='type' else 'roles']='writer' if fault=='type' else ['indexed_by'];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='shared-pair-image':declared['reference'][79]['proposed_native_json']+=' '
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    elif fault=='paired-function-postimage':declared['function'][56]['proposed_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_paired_curve_normalization_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_PAIRED_CURVE_NORMALIZATION_FILES_SHA256))
def test_preceding_paired_curve_domain_and_generated_source_bytes_remain_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_paired_curve_normalization_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('fault',('property','TEST','TEST-order'))
def test_complete_byte_ratio_function_document_and_TEST_positions_remain_exact(models,monkeypatch,fault):
    _,_,after=models;row=contract.descriptor(repo.ROOT)['function'][62]
    assert row['owner']=='energetic-honeybee/fn' and row['function']==0x4AE6C
    changed=json.loads(row['original_native_json'])
    if fault=='property':changed['summary']='unregistered'
    elif fault=='TEST':changed['evidence']=[dict(kind='TEST',value='unregistered')]
    else:changed['ledger']=[dict(order=-1,registry='funcs',notes=[1,0])]
    load=store.load
    monkeypatch.setattr(store,'load',lambda root,path,overlay=None:deepcopy(changed) if str(path)==row['source'] else load(root,path,overlay))
    with pytest.raises(ValueError):proof.native_rows(after,'proposed')


def test_state_surface_retains_full119_core_records_and63_complete_functions():
    declared=contract.descriptor(repo.ROOT);previous=contract.prior_reference_rows(declared,119)
    historical=contract.uptight_RAM3348_prior_current_rows(declared,124)
    assert contract.state_surface_prefix_digest(declared,119)==contract.digest(previous)==contract.PRIOR_BYTE_RATIO_PRODUCER_REFERENCE_SHA256
    assert [i for i,(old,new) in enumerate(zip(previous,historical[:119])) if old!=new]==[99]
    old,new=previous[99],declared['reference'][99]
    postimage={'proposed_native_json','proposed_native_sha256','proposed_ledger_json'}
    assert {key:value for key,value in old.items() if key not in postimage}=={key:value for key,value in new.items() if key not in postimage}
    assert contract.digest(declared['function'][:63])==contract.PRIOR_BYTE_RATIO_PRODUCER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    assert declared['reference'][79]==previous[79]
    assert len(contract.FUNCTION_POSTIMAGE_IDENTITIES)==5 and len(contract.FUNCTION_POSTIMAGE_CLAIMS)==8
    contract.require_function_postimages(declared)
    assert len(contract.ORIGINAL_LINK_TYPES)==11 and len(contract.NATIVE_LINK_ROLES)==19
    row=declared['reference'][119];claim=json.loads(row['original_claim_json'])
    assert (row['owner'],row['address'],row['function'])==('quick-basilisk/tbl',0x12B52,0x647E8)
    assert row['original_claim_sha256']=='0057fd6cb20fac880f590fbd89fccd80768695872bed9c47fa438877314cec2b'
    assert claim['type']=='reader' and claim['roles']==[] and claim['evidence']==[]
    assert claim['props']==dict(layouts=['7mfk'],relies='structure',supports='identity')
    assert declared['function'][63]['owner']=='spotted-zebra/fn' and declared['function'][63]['function']==0x647E8
    assert 'proposed_native_json' not in declared['function'][63]


def test_state_surface_shared_owner_changes_only_one_exact_link_and_owner_end_selector():
    declared=contract.descriptor(repo.ROOT);previous=contract.prior_reference_rows(declared,119)
    before=json.loads(previous[99]['proposed_native_json']);after=json.loads(declared['reference'][99]['proposed_native_json'])
    row=declared['reference'][119];claim=json.loads(row['original_claim_json']);expected=deepcopy(before)
    links=[item for item in expected['link'] if (item['type'],item['to'])==(claim['type'],claim['to'])]
    assert len(links)==1;expected['link'].remove(links[0]);selected=0
    for marker in expected.get('ledger',()):
        if 'dependency' not in marker:continue
        held=marker['dependency'];chosen=[item for item in held if contract.selector(row,row['owner'],item)]
        selected+=len(chosen);marker['dependency']=[item for item in held if item not in chosen]
        if not marker['dependency']:marker.pop('dependency')
    if not expected.get('link'):expected.pop('link',None)
    assert selected==1 and test_contract.exact(expected,after)


@pytest.mark.parametrize('count,pin',((87,'PRIOR_MIXED_CURVE_CALLER_REFERENCE_SHA256'),
    (92,'PRIOR_TIMING_REMAINDER_CALLER_REFERENCE_SHA256'),(100,'PRIOR_STATE_RATIO_CALLER_REFERENCE_SHA256'),
    (107,'PRIOR_DFCO_STATE_CALLER_REFERENCE_SHA256'),(115,'PRIOR_THRESHOLD_WINDOW_READER_REFERENCE_SHA256'),
    (116,'PRIOR_AUX_RATE_CALLER_REFERENCE_SHA256')))
def test_state_surface_retains_both_separately_bounded_shared_owner_deltas_in_complete_old_prefixes(count,pin):
    declared=contract.descriptor(repo.ROOT);previous=contract.prior_reference_rows(declared,count)
    historical=contract.uptight_RAM3348_prior_current_rows(declared,124)
    assert contract.paired_curve_prefix_digest(declared,count)==contract.digest(previous)==getattr(contract,pin)
    assert [i for i,(old,new) in enumerate(zip(previous,historical[:count])) if old!=new]==([79,99] if count>99 else [79])
    for index in ((79,99) if count>99 else (79,)):
        old,new=previous[index],declared['reference'][index]
        omitted={'proposed_native_json','proposed_native_sha256','proposed_ledger_json'}
        assert {key:value for key,value in old.items() if key not in omitted}=={key:value for key,value in new.items() if key not in omitted}


@pytest.mark.parametrize('count,pin',((118,'PRIOR_PAIRED_CURVE_NORMALIZATION_REFERENCE_SHA256'),
    (119,'PRIOR_BYTE_RATIO_PRODUCER_REFERENCE_SHA256')))
def test_state_surface_retains_complete_current_prefixes_with_only_one_exact_new_delta(count,pin):
    declared=contract.descriptor(repo.ROOT);previous=contract.prior_reference_rows(declared,count)
    historical=contract.uptight_RAM3348_prior_current_rows(declared,124)
    assert contract.state_surface_prefix_digest(declared,count)==contract.digest(previous)==getattr(contract,pin)
    assert [i for i,(old,new) in enumerate(zip(previous,historical[:count])) if old!=new]==[99]


@pytest.mark.parametrize('fault',('claim-id','claim-owner','claim-function','claim-type','claim-role','claim-evidence',
    'claim-json','extra-claim','prefix-order','shared-source','shared-original','current-json','current-ledger',
    'extra-field','extra-link','TEST','selector-order','selector-extent','other-row','paired-row79',
    'function-json','function-order','paired-function-postimage'))
def test_state_surface_exact_current_transition_refuses_ignored_fields_types_roles_scope_and_positions(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][99];claim=declared['reference'][119]
    if fault=='claim-id':claim['id']='unregistered'
    elif fault=='claim-owner':claim['owner']='unregistered/tbl'
    elif fault=='claim-function':claim['function']+=2
    elif fault in ('claim-type','claim-role','claim-evidence'):
        old=json.loads(claim['original_claim_json']);key={'claim-type':'type','claim-role':'roles','claim-evidence':'evidence'}[fault]
        old[key]={'claim-type':'writer','claim-role':['indexed_by'],'claim-evidence':[dict(kind='indirect')]}[fault]
        claim['original_claim_json']=json.dumps(old)
    elif fault=='claim-json':claim['original_claim_json']+=' '
    elif fault=='extra-claim':declared['reference'].append(deepcopy(claim))
    elif fault=='prefix-order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='shared-source':row['source']='unregistered'
    elif fault=='shared-original':row['original_native_json']+=' '
    elif fault=='current-json':row['proposed_native_json']+=' '
    elif fault=='current-ledger':row['proposed_ledger_json']+=' '
    elif fault=='other-row':declared['reference'][10]['proposed_native_json']+=' '
    elif fault=='paired-row79':declared['reference'][79]['proposed_native_json']+=' '
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    elif fault=='function-order':declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    elif fault=='paired-function-postimage':declared['function'][56]['proposed_native_json']+=' '
    else:
        document=json.loads(row['proposed_native_json'])
        if fault=='extra-field':document['unit']='unregistered'
        elif fault=='extra-link':document.setdefault('link',[]).append(dict(type='reader',to='unregistered/fn'))
        elif fault=='TEST':document['TEST']=[dict(unregistered=True)]
        elif fault=='selector-order':next(marker for marker in document['ledger'] if len(marker.get('dependency',()))>1)['dependency'].reverse()
        else:next(marker for marker in document['ledger'] if marker.get('dependency'))['dependency'].pop()
        row.update(proposed_native_json=json.dumps(document,sort_keys=True,separators=(',',':'),ensure_ascii=True),
            proposed_native_sha256=contract.digest(document),
            proposed_ledger_json=json.dumps(document.get('ledger'),sort_keys=True,separators=(',',':'),ensure_ascii=True))
    with pytest.raises(ValueError):contract.require_prior_byte_ratio_producer_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_BYTE_RATIO_PRODUCER_FILES_SHA256))
def test_every_complete_byte_ratio_source_and_generated_output_remains_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_byte_ratio_producer_boundary(repo.ROOT,declared)


def test_state_surface_adds_two_exact_reader_originals_and_one_complete_new_owner_without_function_selectors():
    declared=contract.descriptor(repo.ROOT);additional=contract.state_surface_additional_rows(declared)
    assert [(row['owner'],row['address'],row['function'],row['original_claim_sha256']) for row in additional]==[
        ('quick-basilisk/tbl',0x12B52,0x647E8,'0057fd6cb20fac880f590fbd89fccd80768695872bed9c47fa438877314cec2b'),
        ('mindful-pogona/tbl',0x12B5A,0x647E8,'55e5ca11aa978e3f61c1f44e450f5acc3fce0638cb0f1fdc434a77b0794c6eef')]
    assert additional[1]['owner'] not in {row['owner'] for row in declared['reference'][:119]}
    function=declared['function'][63];document=json.loads(function['original_native_json'])
    assert function['owner']=='spotted-zebra/fn' and 'proposed_native_json' not in function
    assert not [item for marker in document.get('ledger',()) for item in marker.get('dependency',())
        if item.get('end')=='to' and item.get('type')=='reader' and item.get('to') in {row['owner'] for row in additional}]
    assert len({row['owner'] for row in declared['reference'][:121]})==92
    assert declared['reference'][9]==contract.prior_reference_rows(declared,119)[9]


def test_byte_factor_retains_all121_full_current_records_and64_complete_functions():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_state_surface_caller_boundary(repo.ROOT,declared)
    historical=contract.uptight_RAM3348_prior_current_rows(declared,124)
    previous=contract.prior_reference_rows(declared,121)
    assert previous==historical[:121]
    assert contract.digest(previous)==contract.PRIOR_STATE_SURFACE_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:64])==contract.PRIOR_STATE_SURFACE_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    row=declared['reference'][121];old=json.loads(row['original_claim_json'])
    assert (row['owner'],row['address'],row['function'])==('purple-chihuahua/ram',0xFFFF23C5,0x4BA48)
    assert row['original_claim_sha256']=='47c4932e2c5dbceeaa8d0d301089b790354738e4ef80dfa93ebb005beb915442'
    assert old['type']=='writer' and old['roles']==[] and old['evidence']==[]
    assert old['props']==dict(layouts=['7mfk'],reverse_relies='structure',reverse_supports='identity')
    assert row['owner'] not in {held['owner'] for held in previous}
    assert row['original_ledger_json']==row['proposed_ledger_json']
    assert contract.ORIGINAL_LINK_TYPES[row['id']]=='writer' and len(contract.ORIGINAL_LINK_TYPES)==11
    assert len(contract.NATIVE_LINK_ROLES)==19


def test_byte_factor_complete_function_transition_removes_only_one_exact_reverse_writer_selector():
    declared=contract.descriptor(repo.ROOT);contract.require_function_postimages(declared)
    row=declared['function'][64];claim=declared['reference'][121]
    assert row['owner']=='charming-warthog/fn' and row['function']==0x4BA48
    before=contract.function_native_document(row,'original');after=contract.function_native_document(row,'proposed')
    assert {k:v for k,v in before.items() if k!='ledger'}=={k:v for k,v in after.items() if k!='ledger'}
    expected=deepcopy(before);removed=[]
    for marker in expected['ledger']:
        if 'dependency' not in marker:continue
        chosen=[item for item in marker['dependency'] if contract.selector(claim,row['owner'],item)]
        removed.extend(chosen);marker['dependency']=[item for item in marker['dependency'] if item not in chosen]
        if not marker['dependency']:marker.pop('dependency')
    assert removed==[dict(role='writes',to='purple-chihuahua/ram',type='writer',end='to',relies='structure',supports='identity')]
    assert test_contract.exact(expected,after)
    assert len(contract.FUNCTION_POSTIMAGE_IDENTITIES)==5 and len(contract.FUNCTION_POSTIMAGE_CLAIMS)==8


@pytest.mark.parametrize('fault',('original-json','current-json','ledger-json','type','role','order','row79','row99',
    'function-json','function-order','prior-function-postimage'))
def test_byte_factor_full_prior121_and64_functions_refuse_any_ignored_field_or_position(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][119]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='current-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role'):
        old=json.loads(row['original_claim_json']);old['type' if fault=='type' else 'roles']='writer' if fault=='type' else ['indexed_by'];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault in ('row79','row99'):declared['reference'][int(fault[3:])]['proposed_native_json']+=' '
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    elif fault=='prior-function-postimage':declared['function'][56]['proposed_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_state_surface_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_STATE_SURFACE_CALLER_FILES_SHA256))
def test_each_complete_prior_state_surface_source_and_generated_output_is_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_state_surface_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('fault',('before-json','after-json','before-ledger','after-ledger','before-sha','after-sha',
    'owner','function','source','missing-field','extra-field','another-selector','TEST-position','symbol','note','identity'))
@pytest.mark.parametrize('index',(64,65))
def test_additional_full_function_postimages_have_no_ignored_field_or_generic_owner_exception(fault,index):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['function'][index]
    keys={'before-json':'original_native_json','after-json':'proposed_native_json','before-ledger':'original_ledger_json',
        'after-ledger':'proposed_ledger_json','before-sha':'original_native_sha256','after-sha':'proposed_native_sha256'}
    if fault in keys:row[keys[fault]]+=' '
    elif fault=='owner':row['owner']='other/fn'
    elif fault=='function':row['function']+=2
    elif fault=='source':row['source']='other.toml'
    elif fault=='missing-field':row.pop('proposed_ledger_json')
    elif fault=='extra-field':row['extra']=True
    else:
        document=json.loads(row['proposed_native_json'])
        if fault=='another-selector':next(marker for marker in document['ledger'] if marker.get('dependency'))['dependency'].pop()
        elif fault=='TEST-position':document.setdefault('evidence',[]).append(dict(type='TEST',position='other'))
        elif fault=='symbol':document['symbol'].append(deepcopy(document['symbol'][0]))
        elif fault=='note':document['ledger'][0].setdefault('notes',[]).append('other')
        else:document['ledger'][0].setdefault('identity',[]).append(999)
        row['proposed_native_json']=json.dumps(document,sort_keys=True,separators=(',',':'))
        row['proposed_native_sha256']=contract.digest(document)
    with pytest.raises((ValueError,KeyError)):contract.require_function_postimages(declared)


def test_byte_sum_retains_all122_full_current_records_and65_complete_function_records():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_byte_factor_caller_boundary(repo.ROOT,declared)
    historical=contract.uptight_RAM3348_prior_current_rows(declared,124)
    previous=contract.prior_reference_rows(declared,122)
    assert historical[:122]==previous
    assert contract.digest(previous)==contract.PRIOR_BYTE_FACTOR_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:65])==contract.PRIOR_BYTE_FACTOR_CALLER_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    row=declared['reference'][122];old=json.loads(row['original_claim_json'])
    assert (row['owner'],row['address'],row['function'])==('urban-ibex/ram',0xFFFF1693,0x464DE)
    assert row['original_claim_sha256']=='1dacd2a5176d35d9dc687370413cd3502b32f21417e16988f0948a9587b9d970'
    assert old['type']=='writer' and old['roles']==[] and old['evidence']==[]
    assert old['props']==dict(layouts=['7mfk'],reverse_relies='structure',reverse_supports='identity')
    assert row['original_ledger_json']==row['proposed_ledger_json']=='null'
    assert 'ledger' not in json.loads(row['original_native_json']) and 'ledger' not in json.loads(row['proposed_native_json'])
    assert row['owner'] not in {held['owner'] for held in previous}
    assert contract.ORIGINAL_LINK_TYPES[row['id']]=='writer' and len(contract.ORIGINAL_LINK_TYPES)==11
    assert len(contract.NATIVE_LINK_ROLES)==19


def test_byte_sum_complete_function_transition_removes_one_exact_reverse_writer_and_preserves_all_other_selectors():
    declared=contract.descriptor(repo.ROOT);contract.require_function_postimages(declared)
    row=declared['function'][65];claim=declared['reference'][122]
    assert row['owner']=='cherubic-salamander/fn' and row['function']==0x464DE
    before=contract.function_native_document(row,'original');after=contract.function_native_document(row,'proposed')
    assert {k:v for k,v in before.items() if k!='ledger'}=={k:v for k,v in after.items() if k!='ledger'}
    expected=deepcopy(before);removed=[]
    for marker in expected.get('ledger',()):
        if 'dependency' not in marker:continue
        held=marker['dependency'];chosen=[item for item in held if contract.selector(claim,row['owner'],item)]
        removed.extend(chosen);marker['dependency']=[item for item in held if item not in chosen]
        if not marker['dependency']:marker.pop('dependency')
    assert removed==[dict(role='writes',to='urban-ibex/ram',type='writer',end='to',relies='structure',supports='identity')]
    assert test_contract.exact(expected,after)
    assert len(contract.FUNCTION_POSTIMAGE_IDENTITIES)==5 and len(contract.FUNCTION_POSTIMAGE_CLAIMS)==8


@pytest.mark.parametrize('fault',('original-json','current-json','ledger-json','type','role','order','row79','row99',
    'function-json','function-order','paired-function-postimage','byte-factor-function-postimage'))
def test_byte_sum_prior122_and65_full_function_boundary_refuses_any_ignored_field_or_position(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][121]
    if fault=='original-json':row['original_claim_json']+=' '
    elif fault=='current-json':row['proposed_native_json']+=' '
    elif fault=='ledger-json':row['proposed_ledger_json']+=' '
    elif fault in ('type','role'):
        old=json.loads(row['original_claim_json']);old['type' if fault=='type' else 'roles']='reader' if fault=='type' else ['indexed_by'];row['original_claim_json']=json.dumps(old)
    elif fault=='order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault in ('row79','row99'):declared['reference'][int(fault[3:])]['proposed_native_json']+=' '
    elif fault=='function-json':declared['function'][0]['original_native_json']+=' '
    elif fault in ('paired-function-postimage','byte-factor-function-postimage'):declared['function'][56 if fault.startswith('paired') else 64]['proposed_native_json']+=' '
    else:declared['function'][0],declared['function'][1]=declared['function'][1],declared['function'][0]
    with pytest.raises(ValueError):contract.require_prior_byte_factor_caller_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('name',tuple(contract.PRIOR_BYTE_FACTOR_CALLER_FILES_SHA256))
def test_each_complete_prior_byte_factor_source_and_generated_output_remains_exact(monkeypatch,name):
    declared=contract.descriptor(repo.ROOT);read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_prior_byte_factor_caller_boundary(repo.ROOT,declared)


def test_reader_direction_retains_all123_preceding_records_and66_complete_functions():
    declared=contract.descriptor(repo.ROOT)
    assert len(declared['reference'])==132 and len(declared['function'])==73
    assert contract.digest(contract.prior_reference_rows(declared,123))==contract.PRIOR_READER_DIRECTION_REFERENCE_SHA256
    assert contract.digest(declared['function'][:66])==contract.PRIOR_READER_DIRECTION_FUNCTION_SHA256
    row=declared['reference'][123]
    assert tuple(row[key] for key in ('id','original_claim_sha256','address','function'))==contract.READER_ONLY_WITH_RETAINED_WRITER
    assert row['component']=='dfco_state_caller_withdrawal_paths'
    assert row['owner']=='piquant-lemur/ram' and row['declared_width']==row['declared_signed']=='unset'
    before,after=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
    expected=deepcopy(before)
    expected['link']=[r for r in expected['link'] if (r['type'],r['to'])!=('reader','dfco_state_machine/fn')]
    for marker in expected['ledger']:
        marker['dependency']=[r for r in marker['dependency'] if not contract.selector(row,row['owner'],r)]
        if not marker['dependency']:marker.pop('dependency')
    assert expected==after
    assert [r for r in before['link'] if r['type']=='writer']==after['link']
    assert before['unit']==after['unit']=='enum_u8'
    assert json.loads(row['original_claim_json'])['evidence']==[]
    assert json.loads(row['original_symbol_evidence_json'])==next(r for r in after['symbol'] if r['layout']=='7mfk')['evidence']
    target,=[r for r in declared['function'] if r['owner']=='dfco_state_machine/fn']
    assert not any(r['type']=='reader' and r.get('to')=='piquant-lemur/ram'
        for marker in json.loads(target['original_native_json'])['ledger'] for r in marker.get('dependency',()))


@pytest.mark.parametrize('fault',('prior-row','prior-order','function','identity','writer','unit'))
def test_reader_direction_boundary_refuses_donation_from_another_scope(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][123]
    if fault=='prior-row':declared['reference'][0]['proposed_native_json']+=' '
    elif fault=='prior-order':declared['reference'][0],declared['reference'][1]=declared['reference'][1],declared['reference'][0]
    elif fault=='function':declared['function'][0]['original_native_json']+=' '
    elif fault=='identity':row['original_claim_sha256']='0'*64
    else:
        after=json.loads(row['proposed_native_json'])
        if fault=='writer':after['link']=[]
        else:after['unit']='unproved unit'
        row['proposed_native_json']=json.dumps(after)
    with pytest.raises(ValueError):contract.require_prior_reader_direction_boundary(declared)



def dfco_direction_flags():
    rows=contract.descriptor(repo.ROOT)['reference']
    return dict(reader_only1939_retained_writer=True,prior1939_complete_state_independence=True,
        reader_only1939_original=contract.READER_ONLY_WITH_RETAINED_WRITER[1],
        strict_absence_originals=[r['original_claim_sha256'] for r in rows
            if r['component']=='dfco_state_caller_withdrawal_paths' and r['function']==0x503E0 and r['id']!=contract.READER_ONLY_WITH_RETAINED_WRITER[0]],
        retained1939_write_sites=[0x50574,0x50594],reader_only16aa_retained_writer=True,
        prior16aa_complete_state_independence=True,
        reader_only16aa_original=contract.RESTORE_READER_ONLY_WITH_RETAINED_WRITER[1],
        retained16aa_write_sites=[0x501AE],stdout_sha256='b'*64,
        reader_only1778_retained_writer=True,prior1778_complete_state_independence=True,
        reader_only1778_original=contract.RESTORE1778_READER_ONLY_WITH_RETAINED_WRITER[1],
        retained1778_write_sites=[0x501AA])


def uptight_RAM3348_flags():
    return dict(complete_uptight_RAM3348_same_primary=True,
        uptight_RAM3348_withdrawal_original=contract.UPTIGHT_RAM3348_WITHDRAWAL[1],
        uptight_RAM3348_original_stdout_sha256='a'*64,curve_helper_original_stdout_sha256='a'*64)


def test_uptight_RAM3348_preserves_complete_prior124_records_and66_functions_and_one_joint_owner():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_uptight_RAM3348_boundary(declared)
    assert len(declared['reference'])==132 and len(declared['function'])==73
    assert contract.digest(contract.prior_reference_rows(declared,124))==contract.PRIOR_UPTIGHT_RAM3348_REFERENCE_SHA256
    assert contract.digest(declared['function'][:66])==contract.PRIOR_UPTIGHT_RAM3348_FUNCTION_SHA256
    row=declared['reference'][124]
    assert tuple(row[key] for key in ('id','original_claim_sha256','address','function','component'))==contract.UPTIGHT_RAM3348_WITHDRAWAL
    shared=[r for r in declared['reference'] if r['owner']==row['owner']]
    assert [r['function'] for r in shared]==[0xB7768,0xB78DA,0xB7A3C,0xB784E]
    before,after=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
    assert all(json.loads(r['original_native_json'])==before and json.loads(r['proposed_native_json'])==after for r in shared)
    expected=deepcopy(before)
    for claim in shared:
        old=json.loads(claim['original_claim_json'])
        expected['link']=[link for link in expected['link'] if (link['type'],link['to'])!=(old['type'],old['to'])]
        for marker in expected['ledger']:
            if 'dependency' in marker:
                marker['dependency']=[item for item in marker['dependency'] if not contract.selector(claim,row['owner'],item)]
                if not marker['dependency']:marker.pop('dependency')
    assert after==expected and after['symbol']==before['symbol'] and after['unit']==before['unit']
    assert [link for link in before['link'] if link['type']=='writer']==[link for link in after['link'] if link['type']=='writer']
    function=declared['function'][66];first,last=(contract.function_native_document(function,phase) for phase in ('original','proposed'))
    assert function['owner']=='uptight-duck/fn' and first['symbol']==last['symbol']
    expected=deepcopy(first);removed=[]
    for marker in expected['ledger']:
        items=marker.get('dependency',[]);removed.extend(item for item in items if contract.selector(row,function['owner'],item))
        marker['dependency']=[item for item in items if not contract.selector(row,function['owner'],item)]
    assert last==expected and len(removed)==1 and removed[0]['to']=='ruddy-anaconda/ram'
    assert any(item.get('to')=='rpm/ram' for marker in last['ledger'] for item in marker.get('dependency',()))


@pytest.mark.parametrize('fault',('prefix-row','prefix-order','prefix-function','shared-after','shared-before','original','component'))
def test_uptight_RAM3348_boundary_refuses_partial_old_images_or_donation_from_other_originals(fault):
    value=deepcopy(contract.descriptor(repo.ROOT));row=value['reference'][124]
    if fault=='prefix-row':value['reference'][0]['original_native_json']+=' '
    elif fault=='prefix-order':value['reference'][0],value['reference'][1]=value['reference'][1],value['reference'][0]
    elif fault=='prefix-function':value['function'][0]['original_native_json']+=' '
    elif fault in ('shared-after','shared-before'):row['proposed_native_json' if fault=='shared-after' else 'original_native_json']+=' '
    elif fault=='original':row['original_claim_sha256']='0'*64
    else:row['component']='uptight_duck_paths'
    with pytest.raises(ValueError):contract.require_prior_uptight_RAM3348_boundary(value)


@pytest.mark.parametrize('fault',('json','unit','ledger','evidence','other-selector','identity'))
def test_full_uptight_function_postimage_refuses_other_fields_or_original_evidence_changes(fault):
    value=deepcopy(contract.descriptor(repo.ROOT));row=value['function'][66]
    if fault=='json':row['proposed_native_json']+=' '
    elif fault=='identity':row['original_native_sha256']='0'*64
    else:
        document=json.loads(row['proposed_native_json'])
        if fault=='unit':document['unit']='unregistered'
        elif fault=='ledger':document['ledger'][0]['fields'].reverse()
        elif fault=='evidence':document['symbol'][0]['evidence']=[]
        else:document['ledger'][0]['dependency'].pop()
        row['proposed_native_json']=json.dumps(document)
    with pytest.raises(ValueError):contract.require_function_postimages(value)


@pytest.mark.parametrize('field',tuple(uptight_RAM3348_flags()))
def test_uptight_RAM3348_owning_binding_requires_exact_same_primary_result_and_original(field):
    value=uptight_RAM3348_flags();assert proof.require_uptight_RAM3348_result(value) is True
    value[field]=False if type(value[field]) is bool else '0'*64
    with pytest.raises(ValueError):proof.require_uptight_RAM3348_result(value)


def test_uptight_historical_current_prefix_restores_only_three_pinned_postimage_fields():
    value=contract.descriptor(repo.ROOT)
    fields=('proposed_native_json','proposed_native_sha256','proposed_ledger_json')
    for count in (71,79,87,92,100,107,112,115,116,118,119,121,122):
        previous=contract.uptight_RAM3348_prior_current_rows(value,count);changed=[]
        for old,current in zip(previous,value['reference'][:count]):
            if old==current:continue
            assert old['id'] in contract.UPTIGHT_RAM3348_PRIOR_SHARED_IDS
            assert {key:item for key,item in old.items() if key not in fields}=={
                key:item for key,item in current.items() if key not in fields}
            assert tuple(old[key] for key in fields)==contract.UPTIGHT_RAM3348_PRIOR_SHARED_POSTIMAGE
            changed.append(old['id'])
        assert tuple(changed)==contract.UPTIGHT_RAM3348_PRIOR_SHARED_IDS


@pytest.mark.parametrize('count',(87,119,121,122))
@pytest.mark.parametrize('field',('proposed_native_json','proposed_native_sha256','proposed_ledger_json'))
def test_historical_postimage_restoration_requires_the_complete_current_shared_owner_first(count,field):
    value=deepcopy(contract.descriptor(repo.ROOT))
    row=next(r for r in value['reference'] if r['id']==contract.UPTIGHT_RAM3348_PRIOR_SHARED_IDS[0])
    row[field]+=' '
    with pytest.raises(ValueError):contract.uptight_RAM3348_prior_current_rows(value,count)



def test_restore16aa_preserves_all125_prior_records_and67_functions_and_the_actual_native_writer():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_restore16aa_boundary(declared)
    assert len(declared['reference'])==132 and len(declared['function'])==73
    assert contract.digest(contract.paired_word_sum_prior_current_rows(declared,125))==contract.PRIOR_RESTORE16AA_REFERENCE_SHA256
    assert contract.digest(declared['function'][:67])==contract.PRIOR_RESTORE16AA_FUNCTION_SHA256
    row=declared['reference'][125]
    before,after=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
    assert before['unit']==after['unit']=='RPM/25' and row['declared_width']==row['declared_signed']=='unset'
    expected=deepcopy(before)
    expected['link']=[link for link in expected['link'] if (link['type'],link['to'])!=('reader','dfco_restore_classify/fn')]
    for marker in expected['ledger']:
        marker['dependency']=[item for item in marker['dependency'] if not contract.selector(row,row['owner'],item)]
    assert after==expected and after['symbol']==before['symbol']
    function=declared['function'][67]
    assert set(function)=={'owner','function','source','original_native_sha256','original_native_json'}
    assert json.loads(function['original_native_json'])['ledger'][1]['dependency'][-1]['type']=='writer'


@pytest.mark.parametrize('fault',('prior-record','prior-function','original','writer','unit','width','signed','function-scope'))
def test_restore16aa_owning_boundary_refuses_donation_or_semantic_type_inference(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][125]
    if fault=='prior-record':declared['reference'][0]['source']+='-changed'
    elif fault=='prior-function':declared['function'][0]['source']+='-changed'
    elif fault=='original':row['original_claim_sha256']='0'*64
    elif fault in ('writer','unit'):
        native=json.loads(row['proposed_native_json'])
        if fault=='writer':native['link']=[link for link in native['link'] if link['type']!='writer']
        else:native['unit']='changed'
        row['proposed_native_json']=json.dumps(native)
    elif fault=='width':row['declared_width']=8
    elif fault=='signed':row['declared_signed']=False
    elif fault=='function-scope':declared['function'][67]['owner']='another/fn'
    with pytest.raises(ValueError):contract.require_prior_restore16aa_boundary(declared)


@pytest.mark.parametrize('field',('reader_only16aa_retained_writer','prior16aa_complete_state_independence',
    'reader_only16aa_original','retained16aa_write_sites','stdout_sha256'))
def test_restore16aa_owning_binding_requires_the_exact_primary_direction_and_full_state(field):
    result=dict(reader_only16aa_retained_writer=True,prior16aa_complete_state_independence=True,
        reader_only16aa_original=contract.RESTORE_READER_ONLY_WITH_RETAINED_WRITER[1],
        retained16aa_write_sites=[0x501AE],stdout_sha256='1'*64)
    assert proof.require_restore16aa_result(result) is True
    result.pop(field)
    with pytest.raises(ValueError):proof.require_restore16aa_result(result)



def test_restore1778_preserves_all126_records_and_all68_functions_and_actual_writer():
    declared=contract.descriptor(repo.ROOT);contract.require_prior_restore1778_boundary(declared)
    assert len(declared['reference'])==132 and len(declared['function'])==73
    assert contract.digest(contract.paired_word_sum_prior_current_rows(declared,126))==contract.PRIOR_RESTORE1778_REFERENCE_SHA256
    assert contract.digest(declared['function'][:68])==contract.PRIOR_RESTORE1778_FUNCTION_SHA256
    row=declared['reference'][126];before,after=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
    assert before['unit']==after['unit']=='RPM/25' and row['declared_width']==row['declared_signed']=='unset'
    expected=deepcopy(before)
    expected['link']=[link for link in expected['link'] if (link['type'],link['to'])!=('reader','dfco_restore_classify/fn')]
    for marker in expected['ledger']:
        marker['dependency']=[item for item in marker['dependency'] if not contract.selector(row,row['owner'],item)]
    assert after==expected and after['symbol']==before['symbol']


@pytest.mark.parametrize('fault',('prior-record','function','original','writer','unit','width','signed'))
def test_restore1778_owning_boundary_refuses_other_records_writer_or_semantic_type_changes(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT));row=declared['reference'][126]
    if fault=='prior-record':declared['reference'][0]['source']+='-changed'
    elif fault=='function':declared['function'][67]['source']+='-changed'
    elif fault=='original':row['original_claim_sha256']='0'*64
    elif fault in ('writer','unit'):
        native=json.loads(row['proposed_native_json'])
        if fault=='writer':native['link']=[link for link in native['link'] if link['type']!='writer']
        else:native['unit']='changed'
        row['proposed_native_json']=json.dumps(native)
    elif fault=='width':row['declared_width']=8
    elif fault=='signed':row['declared_signed']=False
    with pytest.raises(ValueError):contract.require_prior_restore1778_boundary(declared)


@pytest.mark.parametrize('field',('reader_only1778_retained_writer','prior1778_complete_state_independence',
    'reader_only1778_original','retained1778_write_sites','stdout_sha256'))
def test_restore1778_owning_binding_requires_its_exact_primary_original_and_full_state(field):
    result=dict(reader_only1778_retained_writer=True,prior1778_complete_state_independence=True,
        reader_only1778_original=contract.RESTORE1778_READER_ONLY_WITH_RETAINED_WRITER[1],
        retained1778_write_sites=[0x501AA],stdout_sha256='1'*64)
    assert proof.require_restore1778_result(result) is True
    result.pop(field)
    with pytest.raises(ValueError):proof.require_restore1778_result(result)


def test_independent_clamp_latch_direct_reader_delta_retains_full_table_and_function_contexts():
    value=contract.descriptor(repo.ROOT)
    rows=[row for row in value['reference'] if row['component']=='clamp_latch_caller_withdrawal_paths']
    assert len(rows)==1;row=rows[0]
    assert row['original_claim_sha256']=='4193a93d663def7a0f8c62b6519e3909b5ae7523997ae08977dd9f3cbdb32951'
    assert row['owner']=='nice-coucal/tbl' and row['function']==0x39316 and row['address']==0x15630
    assert row['declared_width']==row['declared_signed']=='unset'
    before,after=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
    claim=json.loads(row['original_claim_json']);expected=deepcopy(before)
    joint=[item for item in value['reference'] if item['owner']==row['owner']]
    assert {item['component'] for item in joint}=={'clamp_latch_caller_withdrawal_paths','bfs_state_caller_withdrawal_paths'}
    removed=0
    for selected_row in joint:
        original=json.loads(selected_row['original_claim_json'])
        selected=[link for link in expected['link'] if (link['type'],link['to'])==(original['type'],original['to'])]
        assert len(selected)==1;expected['link'].remove(selected[0])
        for marker in expected.get('ledger',()):
            held=marker.get('dependency',[]);marker['dependency']=[item for item in held if not contract.selector(selected_row,row['owner'],item)]
            removed+=len(held)-len(marker['dependency'])
            if not marker['dependency']:marker.pop('dependency')
    assert removed==2 and expected==after
    function=next(item for item in value['function'] if item['function']==0x39316)
    assert contract.function_native_document(function,'proposed')==json.loads(function['original_native_json'])
    assert not any(contract.selector(row,function['owner'],item) for marker in json.loads(function['original_native_json'])['ledger'] for item in marker.get('dependency',()))


@pytest.mark.parametrize('fault',('summary','scale','unit','note','TEST','link-order','foreign-link','selector-order','new-field'))
def test_full_independent_table_owner_guard_refuses_any_unrelated_native_change(monkeypatch,fault):
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    value=contract.descriptor(repo.ROOT);row=next(item for item in value['reference'] if item['component']=='clamp_latch_caller_withdrawal_paths')
    model=compile.build(repo.ROOT);original=family.store.load
    def changed(root,path,overlay=None):
        document=original(root,path,overlay)
        if str(path)!=row['source']:return document
        document=deepcopy(document)
        if fault in ('summary','scale','unit'):document[fault]=str(document.get(fault,''))+'changed'
        elif fault=='note':document.setdefault('note',[]).append('changed')
        elif fault=='TEST':document['symbol'][0].setdefault('evidence',[]).append({'kind':'test','path':'changed','key':'changed'})
        elif fault=='link-order':document['link'].reverse()
        elif fault=='foreign-link':document['link'].pop(0)
        elif fault=='selector-order':document['ledger'][0]['dependency'].reverse()
        else:document['unexpected']=True
        return document
    monkeypatch.setattr(family.store,'load',changed)
    with pytest.raises(ValueError):family.native_rows(model,'original')


@pytest.mark.parametrize('fault',('summary','role','block','symbol','TEST','selector','selector-order','new-field'))
def test_full_independent_function_guard_keeps_all_downstream_RAM_and_source_contexts(monkeypatch,fault):
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    value=contract.descriptor(repo.ROOT);row=next(item for item in value['function'] if item['function']==0x39316)
    model=compile.build(repo.ROOT);original=family.store.load
    def changed(root,path,overlay=None):
        document=original(root,path,overlay)
        if str(path)!=row['source']:return document
        document=deepcopy(document)
        if fault in ('summary','role','block'):document[fault]=str(document.get(fault,''))+'changed'
        elif fault=='symbol':document['symbol'][0]['name']='changed'
        elif fault=='TEST':document['symbol'][0].setdefault('evidence',[]).append({'kind':'test','path':'changed','key':'changed'})
        elif fault=='selector':document['ledger'][0]['dependency'].pop()
        elif fault=='selector-order':document['ledger'][0]['dependency'].reverse()
        else:document['unexpected']=True
        return document
    monkeypatch.setattr(family.store,'load',changed)
    with pytest.raises(ValueError):family.native_rows(model,'original')


def test_paired_word_curve_direct_reader_delta_keeps_exact_shared_owner_and_complete_function():
    value=contract.descriptor(repo.ROOT)
    rows=[row for row in value['reference'] if row['component']=='paired_word_curve_sum_withdrawal_paths']
    assert len(rows)==1;row=rows[0]
    assert row['original_claim_sha256']=='782329298a209bf40a282b98cc45b4be8e5a2ac28662ac911cedf461f885ba0b'
    assert (row['owner'],row['address'],row['function'])==('rev_limit_throttle_cut/tbl',0x942C,0x72C3C)
    assert row['declared_width']==row['declared_signed']=='unset'
    claim=json.loads(row['original_claim_json'])
    assert claim['type']=='reader' and claim['to']=='throttle_area_compositor/fn'
    assert claim['props']=={'layouts':['7mfk'],'relies':'level','supports':'identity'}
    assert claim['roles']==claim['evidence']==[] and claim['slot'] is claim['offset'] is None
    before,after=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
    assert before['cols']==1 and before['storage']=='uint16'
    joint=[item for item in value['reference'] if item['owner']==row['owner']]
    assert {item['id'] for item in joint}=={
        '00070d82-0000942c-withdraw','000777fa-0000942c-withdraw',
        '000cb1ca-0000942c-withdraw','00072c3c-0000942c-withdraw'}
    expected=deepcopy(before);removed=0
    for item in joint:
        original=json.loads(item['original_claim_json'])
        selected=[link for link in expected['link'] if (link['type'],link['to'])==(original['type'],original['to'])]
        assert len(selected)==1;expected['link'].remove(selected[0])
        for marker in expected.get('ledger',()):
            held=marker.get('dependency',[])
            marker['dependency']=[dependency for dependency in held if not contract.selector(item,row['owner'],dependency)]
            removed+=len(held)-len(marker['dependency'])
            if not marker['dependency']:marker.pop('dependency')
    assert removed==4 and expected==after
    assert all(item['original_native_json']==row['original_native_json'] and item['proposed_native_json']==row['proposed_native_json']
        and item['proposed_native_sha256']==row['proposed_native_sha256'] for item in joint)
    function=next(item for item in value['function'] if item['function']==0x72C3C)
    assert contract.function_native_document(function,'proposed')==json.loads(function['original_native_json'])
    assert not any(contract.selector(row,function['owner'],item)
        for marker in json.loads(function['original_native_json'])['ledger'] for item in marker.get('dependency',()))


def test_three_existing_shared_owner_records_change_only_their_exact_proposed_image_fields():
    value=contract.descriptor(repo.ROOT)
    fields={'proposed_native_json','proposed_native_sha256','proposed_ledger_json'}
    pins={'00070d82-0000942c-withdraw': 'e7e8a2d89d6d8ba7b199e49d9c3c90623adfa064f26455419e3c414551dede8c', '000777fa-0000942c-withdraw': '2644c3dbecf557075d7613141569791caa9e090932649aa0eb31a9d112541c40', '000cb1ca-0000942c-withdraw': '5311172792324cc13c1e733db7375dffeb0ecc945f110a68b5ced3b7b5a6f0cc'}
    rows={row['id']:row for row in value['reference'] if row['id'] in pins}
    assert rows.keys()==pins.keys()
    for identity,row in rows.items():
        held={key:item for key,item in row.items() if key not in fields}
        raw=json.dumps(held,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
        assert hashlib.sha256(raw).hexdigest()==pins[identity]


@pytest.mark.parametrize('fault',('summary','scale','unit','note','TEST','link-order','foreign-link','selector-order','new-field'))
def test_full_shared_scalar_owner_guard_refuses_any_unrelated_native_change(monkeypatch,fault):
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    value=contract.descriptor(repo.ROOT);row=next(item for item in value['reference'] if item['component']=='paired_word_curve_sum_withdrawal_paths')
    model=compile.build(repo.ROOT);original=family.store.load
    def changed(root,path,overlay=None):
        document=original(root,path,overlay)
        if str(path)!=row['source']:return document
        document=deepcopy(document)
        if fault in ('summary','scale','unit'):document[fault]=str(document.get(fault,''))+'changed'
        elif fault=='note':document.setdefault('note',[]).append('changed')
        elif fault=='TEST':document['symbol'][0].setdefault('evidence',[]).append({'kind':'test','path':'changed','key':'changed'})
        elif fault=='link-order':document['link'].reverse()
        elif fault=='foreign-link':document['link'].pop(0)
        elif fault=='selector-order':document['ledger'][0]['dependency'].reverse()
        else:document['unexpected']=True
        return document
    monkeypatch.setattr(family.store,'load',changed)
    with pytest.raises(ValueError):family.native_rows(model,'original')


@pytest.mark.parametrize('fault',('summary','role','block','symbol','TEST','selector','selector-order','new-field'))
def test_full_complete_function_guard_keeps_all_downstream_RAM_and_source_contexts(monkeypatch,fault):
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    value=contract.descriptor(repo.ROOT);row=next(item for item in value['function'] if item['function']==0x72C3C)
    model=compile.build(repo.ROOT);original=family.store.load
    def changed(root,path,overlay=None):
        document=original(root,path,overlay)
        if str(path)!=row['source']:return document
        document=deepcopy(document)
        if fault in ('summary','role','block'):document[fault]=str(document.get(fault,''))+'changed'
        elif fault=='symbol':document['symbol'][0]['name']='changed'
        elif fault=='TEST':document['symbol'][0].setdefault('evidence',[]).append({'kind':'test','path':'changed','key':'changed'})
        elif fault=='selector':document['ledger'][0]['dependency'].pop()
        elif fault=='selector-order':document['ledger'][0]['dependency'].reverse()
        else:document['unexpected']=True
        return document
    monkeypatch.setattr(family.store,'load',changed)
    with pytest.raises(ValueError):family.native_rows(model,'original')


def clamp_latch_flags():
    return dict(complete_actual_absolute_calls=True,complete_unordered_byte_clamp=True,
        complete_latch_and_word_refresh=True,complete_selected_table_interval_absence=True,
        derived_RAM_and_producer_dependencies_preserved=True,
        native_bindings=[dict(meaning='nice-coucal/tbl',function_meaning='nostalgic-sturgeon/fn',
            original_claim_sha256=contract.CLAMP_LATCH_WITHDRAWAL[1])])


def paired_word_sum_flags():
    return dict(complete_actual_paired_word_curve_calls=True,complete_raw_axis_and_curve=True,
        complete_two_saturated_word_publications=True,complete_local_word_carrier=True,
        complete_selected_scalar_interval_absence=True,derived_request_and_area_dependencies_preserved=True,
        complete_direct_helpers_same_primary=True,
        native_bindings=[dict(meaning='rev_limit_throttle_cut/tbl',function_meaning='throttle_area_compositor/fn',
            original_claim_sha256=contract.PAIRED_WORD_SUM_WITHDRAWAL[1])])


def test_clamp_and_paired_word_package_preserves_all127_prior_records_and68_functions():
    declared=contract.descriptor(repo.ROOT)
    contract.require_clamp_latch_and_paired_word_boundary(repo.ROOT,declared)
    assert contract.digest(contract.paired_word_sum_prior_current_rows(declared,127))==contract.PRIOR_CLAMP_PAIRED_REFERENCE_SHA256
    assert contract.digest(declared['function'][:68])==contract.PRIOR_CLAMP_PAIRED_FUNCTION_SHA256
    assert len(declared['reference'])==132 and len(declared['function'])==73
    assert proof.require_clamp_latch_result(clamp_latch_flags()) is True
    assert proof.require_paired_word_sum_result(paired_word_sum_flags()) is True


@pytest.mark.parametrize('fault',('prior-record','prior-function','new-function','clamp-original','paired-original',
    'clamp-width','paired-signed','shared-postimage','one-shared-record','clamp-producer'))
def test_clamp_and_paired_word_package_refuses_changed_full_native_boundaries(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT))
    if fault=='prior-record':declared['reference'][4]['source']+='-changed'
    elif fault=='prior-function':declared['function'][67]['source']+='-changed'
    elif fault=='new-function':declared['function'][69]['source']+='-changed'
    elif fault=='clamp-original':declared['reference'][127]['original_claim_sha256']='0'*64
    elif fault=='paired-original':declared['reference'][128]['original_claim_sha256']='0'*64
    elif fault=='clamp-width':declared['reference'][127]['declared_width']=16
    elif fault=='paired-signed':declared['reference'][128]['declared_signed']=False
    elif fault=='one-shared-record':
        row=next(row for row in declared['reference'] if row['id']==contract.PAIRED_WORD_SUM_PRIOR_SHARED_IDS[0])
        row['proposed_native_sha256']='0'*64
    elif fault=='shared-postimage':
        for row in declared['reference']:
            if row['owner']=='rev_limit_throttle_cut/tbl':row['proposed_native_sha256']='0'*64
    else:
        row=declared['reference'][127];native=json.loads(row['proposed_native_json'])
        native['link']=[link for link in native['link'] if link['to']!='base_fuel_schedule_producer/fn']
        row['proposed_native_json']=json.dumps(native)
    with pytest.raises(ValueError):contract.require_clamp_latch_and_paired_word_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('helper,require',((clamp_latch_flags,proof.require_clamp_latch_result),
    (paired_word_sum_flags,proof.require_paired_word_sum_result)))
@pytest.mark.parametrize('fault',('missing','extra','owner','function','original'))
def test_independent_caller_owning_binding_refuses_other_native_identity(helper,require,fault):
    result=helper()
    if fault=='missing':result['native_bindings']=[]
    elif fault=='extra':result['native_bindings'].append(deepcopy(result['native_bindings'][0]))
    else:
        field={'owner':'meaning','function':'function_meaning','original':'original_claim_sha256'}[fault]
        result['native_bindings'][0][field]='changed'
    with pytest.raises(ValueError):require(result)


def test_misfire_tail_direct_reader_delta_preserves_scheduler_context_and_full_function():
    value=contract.descriptor(repo.ROOT)
    rows=[row for row in value['reference'] if row['component']=='misfire_tail_dispatch_withdrawal_paths']
    assert len(rows)==1;row=rows[0]
    assert row['original_claim_sha256']=='02d868473e3c258ee4fe81777aea05a65bd44e0a57d0e64ef658d8f3949df311'
    assert (row['owner'],row['address'],row['function'])==('antique-hawk/ram',0xFFFF84BA,0x7C494)
    assert row['declared_width']==row['declared_signed']=='unset'
    before,after=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
    claim=json.loads(row['original_claim_json']);expected=deepcopy(before)
    assert claim['props']=={'layouts':['7mfk'],'relies':'structure','supports':'identity'}
    assert claim['roles']==claim['evidence']==[] and claim['slot'] is claim['offset'] is None
    selected=[link for link in expected['link'] if (link['type'],link['to'])==('reader','nebulous-toucanet/fn')]
    assert len(selected)==1;expected['link'].remove(selected[0]);removed=0
    for marker in expected.get('ledger',()):
        held=marker.get('dependency',[])
        marker['dependency']=[item for item in held if not contract.selector(row,row['owner'],item)]
        removed+=len(held)-len(marker['dependency'])
        if not marker['dependency']:marker.pop('dependency')
    assert removed==1 and expected==after
    assert before['summary']==after['summary'] and before['note']==after['note']
    assert before['symbol']==after['symbol']
    assert {(link['type'],link['to']) for link in after['link']}=={('reader','black-kudu/fn'),('writer','gentle-bat/fn')}
    assert next(link for link in after['link'] if link['type']=='reader')['role']=='indexed_by'
    function=next(item for item in value['function'] if item['function']==0x7C494)
    assert contract.function_native_document(function,'proposed')==json.loads(function['original_native_json'])
    assert not any(contract.selector(row,function['owner'],item)
        for marker in json.loads(function['original_native_json'])['ledger'] for item in marker.get('dependency',()))


@pytest.mark.parametrize('fault',('summary','scale','unit','note','TEST','link-order','foreign-link','selector-order','new-field'))
def test_full_scheduler_owner_guard_refuses_any_unrelated_native_change(monkeypatch,fault):
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    value=contract.descriptor(repo.ROOT);row=next(item for item in value['reference'] if item['component']=='misfire_tail_dispatch_withdrawal_paths')
    model=compile.build(repo.ROOT);original=family.store.load
    def changed(root,path,overlay=None):
        document=original(root,path,overlay)
        if str(path)!=row['source']:return document
        document=deepcopy(document)
        if fault in ('summary','scale','unit'):document[fault]=str(document.get(fault,''))+'changed'
        elif fault=='note':document.setdefault('note',[]).append('changed')
        elif fault=='TEST':document['symbol'][0].setdefault('evidence',[]).append({'kind':'test','path':'changed','key':'changed'})
        elif fault=='link-order':document['link'].reverse()
        elif fault=='foreign-link':document['link'].pop(0)
        elif fault=='selector-order':document['ledger'][0]['dependency'].reverse()
        else:document['unexpected']=True
        return document
    monkeypatch.setattr(family.store,'load',changed)
    with pytest.raises(ValueError):family.native_rows(model,'original')


@pytest.mark.parametrize('fault',('summary','role','block','symbol','TEST','selector','selector-order','new-field'))
def test_full_full_dispatch_function_guard_keeps_all_downstream_RAM_and_source_contexts(monkeypatch,fault):
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    value=contract.descriptor(repo.ROOT);row=next(item for item in value['function'] if item['function']==0x7C494)
    model=compile.build(repo.ROOT);original=family.store.load
    def changed(root,path,overlay=None):
        document=original(root,path,overlay)
        if str(path)!=row['source']:return document
        document=deepcopy(document)
        if fault in ('summary','role','block'):document[fault]=str(document.get(fault,''))+'changed'
        elif fault=='symbol':document['symbol'][0]['name']='changed'
        elif fault=='TEST':document['symbol'][0].setdefault('evidence',[]).append({'kind':'test','path':'changed','key':'changed'})
        elif fault=='selector':document['ledger'][0]['dependency'].pop()
        elif fault=='selector-order':document['ledger'][0]['dependency'].reverse()
        else:document['unexpected']=True
        return document
    monkeypatch.setattr(family.store,'load',changed)
    with pytest.raises(ValueError):family.native_rows(model,'original')


def remaining_caller_flags(component):
    pinned=contract.REMAINING_STANDALONE_CALLERS[component]
    result={flag:True for flag in proof.REMAINING_CALLER_FLAGS[component]}
    if component in ('endpoint_normalizer_writer_withdrawal_paths','bfs_state_caller_withdrawal_paths'):
        result['native_bindings']=dict(original_claim_sha256=pinned[1],owner=pinned[4],
            entry=f'7mfk:{pinned[3]:08x}',native_width=None,native_signed=None,scope='whole-datum-absence')
    else:
        result['native_bindings']=[dict(meaning=pinned[4],function_meaning=pinned[5],original_claim_sha256=pinned[1])]
    return result


def test_remaining_callers_preserve_complete129_reference_and70_function_boundaries():
    declared=contract.descriptor(repo.ROOT)
    contract.require_remaining_standalone_callers_boundary(repo.ROOT,declared)
    assert contract.digest(contract.remaining_callers_prior_current_rows(declared,129))==contract.PRIOR_REMAINING_CALLER_REFERENCE_SHA256
    assert contract.digest(declared['function'][:70])==contract.PRIOR_REMAINING_CALLER_FUNCTION_SHA256
    for component in proof.REMAINING_CALLER_FLAGS:
        assert proof.require_remaining_caller_result(component,remaining_caller_flags(component)) is True


@pytest.mark.parametrize('component',tuple(proof.REMAINING_CALLER_FLAGS))
@pytest.mark.parametrize('fault',('missing','extra','owner','function','original'))
def test_remaining_caller_owning_refuses_missing_or_substituted_native_binding(component,fault):
    result=remaining_caller_flags(component)
    if component in ('endpoint_normalizer_writer_withdrawal_paths','bfs_state_caller_withdrawal_paths'):
        if fault=='missing':result['native_bindings']=None
        elif fault=='extra':result['native_bindings']['extra']=True
        else:result['native_bindings'][{'owner':'owner','function':'entry','original':'original_claim_sha256'}[fault]]='changed'
    elif fault=='missing':result['native_bindings']=[]
    elif fault=='extra':result['native_bindings'].append(deepcopy(result['native_bindings'][0]))
    else:result['native_bindings'][0][{'owner':'meaning','function':'function_meaning','original':'original_claim_sha256'}[fault]]='changed'
    with pytest.raises(ValueError):proof.require_remaining_caller_result(component,result)


@pytest.mark.parametrize('fault',('prior-record','prior-function','new-function','original','direction','width','shared-clamp'))
def test_remaining_callers_refuse_broadened_or_changed_complete_native_snapshots(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT))
    if fault=='prior-record':declared['reference'][126]['source']+='-changed'
    elif fault=='prior-function':declared['function'][69]['source']+='-changed'
    elif fault=='new-function':declared['function'][72]['source']+='-changed'
    elif fault=='original':declared['reference'][129]['original_claim_sha256']='0'*64
    elif fault=='direction':declared['reference'][130]['original_claim_json']='{}'
    elif fault=='width':declared['reference'][131]['declared_width']=16
    else:declared['reference'][127]['proposed_native_sha256']='0'*64
    with pytest.raises(ValueError):contract.require_remaining_standalone_callers_boundary(repo.ROOT,declared)


@pytest.mark.parametrize('component',('endpoint_normalizer_writer_withdrawal_paths','bfs_state_caller_withdrawal_paths'))
def test_endpoint_and_BFS_owning_binding_consumes_the_unchanged_component_producer_schema(component):
    consumer=proof.COMPONENTS[component]
    model=SimpleNamespace(root=repo.ROOT,functions={'7mfk':consumer.contract.FUNCTIONS})
    result=remaining_caller_flags(component)
    result['native_bindings']=consumer.native_bindings(model)
    assert type(result['native_bindings']) is dict
    assert proof.require_remaining_caller_result(component,result) is True


@pytest.mark.parametrize('field,value',(('native_width',8),('native_width',False),
    ('native_signed',False),('native_signed',0),('scope','writer-only'),('entry',0x7AF78)))
@pytest.mark.parametrize('component',('endpoint_normalizer_writer_withdrawal_paths','bfs_state_caller_withdrawal_paths'))
def test_endpoint_and_BFS_owning_binding_refuses_changed_scope_native_type_or_entry_representation(component,field,value):
    result=remaining_caller_flags(component)
    result['native_bindings'][field]=value
    with pytest.raises(ValueError):
        proof.require_remaining_caller_result(component,result)


@pytest.mark.parametrize('field',('original_claim_sha256','owner','entry','native_width','native_signed','scope'))
@pytest.mark.parametrize('component',('endpoint_normalizer_writer_withdrawal_paths','bfs_state_caller_withdrawal_paths'))
def test_endpoint_and_BFS_owning_binding_refuses_an_omitted_component_binding_field(component,field):
    result=remaining_caller_flags(component)
    result['native_bindings'].pop(field)
    with pytest.raises(ValueError):
        proof.require_remaining_caller_result(component,result)


@pytest.mark.parametrize('form',('empty-list','matching-dictionary-list','generic-list'))
@pytest.mark.parametrize('component',('endpoint_normalizer_writer_withdrawal_paths','bfs_state_caller_withdrawal_paths'))
def test_endpoint_and_BFS_owning_binding_refuses_a_substituted_generic_list_schema(component,form):
    result=remaining_caller_flags(component)
    binding=result['native_bindings']
    result['native_bindings']=[] if form=='empty-list' else [binding] if form=='matching-dictionary-list' else [dict(
        meaning=binding['owner'],function_meaning='aromatic-coua/fn',original_claim_sha256=binding['original_claim_sha256'])]
    with pytest.raises(ValueError):
        proof.require_remaining_caller_result(component,result)



def test_current_withdrawal_scope_binds_exact_reference_and_direction_counts():
    declared=contract.descriptor(repo.ROOT);scope=' '.join(declared['scope'].split())
    readers=sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])
    writers=sum(json.loads(row['original_claim_json'])['type']=='writer' for row in declared['reference'])
    assert f"Exactly {len(declared['reference'])} unsupported physical-access withdrawals" in scope
    assert readers==121 and writers==len(contract.ORIGINAL_LINK_TYPES)==11
    assert f'{readers} readers and eleven individually pinned writers' in scope
