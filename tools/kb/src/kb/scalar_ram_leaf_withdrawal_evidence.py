"""Selected ROM-root absence authorizes exact scalar RAM leaf withdrawals."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence,store,test_contract
from kb import scalar_ram_leaf_withdrawal_contract as contract
from kb import scalar_ram_leaf_capture_evidence as capture_consumer,scalar_ram_product_capture_evidence as product_consumer,scalar_ram_gated_capture_evidence as gated_consumer,rpm_ram_withdrawal_capture_evidence as rpm_ram_consumer,register_overflow_capture_evidence as overflow_consumer,scalar_ram_word_capture_evidence as word_consumer,rpm_state_withdrawal_capture_evidence as rpm_state_consumer,indexed_word_update_capture_evidence as indexed_word_consumer,division_caller_withdrawal_capture_evidence as division_caller_consumer,byte_curve_caller_withdrawal_capture_evidence as byte_curve_caller_consumer,word_interp_caller_withdrawal_capture_evidence as word_interp_caller_consumer,scaled_division_caller_withdrawal_capture_evidence as scaled_division_caller_consumer,curve_scale_caller_withdrawal_capture_evidence as curve_scale_caller_consumer,derivative_scale_caller_withdrawal_capture_evidence as derivative_scale_caller_consumer,guarded_quotient_caller_withdrawal_capture_evidence as guarded_quotient_caller_consumer,mixed_curve_caller_withdrawal_capture_evidence as mixed_curve_caller_consumer,timing_remainder_caller_withdrawal_capture_evidence as timing_remainder_caller_consumer,state_ratio_caller_withdrawal_capture_evidence as state_ratio_caller_consumer,dfco_state_caller_withdrawal_capture_evidence as dfco_state_caller_consumer,paired_inhibit_writer_withdrawal_capture_evidence as paired_inhibit_writer_consumer,threshold_window_reader_withdrawal_capture_evidence as threshold_window_reader_consumer,aux_rate_caller_withdrawal_capture_evidence as aux_rate_caller_consumer,paired_curve_normalization_withdrawal_capture_evidence as paired_curve_normalization_consumer,byte_ratio_producer_withdrawal_capture_evidence as byte_ratio_producer_consumer,state_surface_caller_withdrawal_capture_evidence as state_surface_caller_consumer,byte_factor_caller_withdrawal_capture_evidence as byte_factor_caller_consumer,byte_sum_caller_withdrawal_capture_evidence as byte_sum_caller_consumer
from kb.diagnostic_rom_contract import native_ledger
from kb.diagnostic_rom_evidence import dependency_state

COMPONENTS={'scalar_ram_leaf_paths':capture_consumer,'scalar_ram_product_paths':product_consumer,'scalar_ram_gated_paths':gated_consumer,'rpm_ram_withdrawal_paths':rpm_ram_consumer,'register_overflow_paths':overflow_consumer,'scalar_ram_word_paths':word_consumer,'rpm_state_withdrawal_paths':rpm_state_consumer,'indexed_word_update_paths':indexed_word_consumer,'division_caller_withdrawal_paths':division_caller_consumer,'byte_curve_caller_withdrawal_paths':byte_curve_caller_consumer,'word_interp_caller_withdrawal_paths':word_interp_caller_consumer,'scaled_division_caller_withdrawal_paths':scaled_division_caller_consumer,'curve_scale_caller_withdrawal_paths':curve_scale_caller_consumer,'derivative_scale_caller_withdrawal_paths':derivative_scale_caller_consumer,'guarded_quotient_caller_withdrawal_paths':guarded_quotient_caller_consumer,'mixed_curve_caller_withdrawal_paths':mixed_curve_caller_consumer,'timing_remainder_caller_withdrawal_paths':timing_remainder_caller_consumer,'state_ratio_caller_withdrawal_paths':state_ratio_caller_consumer,'dfco_state_caller_withdrawal_paths':dfco_state_caller_consumer,'paired_inhibit_writer_withdrawal_paths':paired_inhibit_writer_consumer,'threshold_window_reader_withdrawal_paths':threshold_window_reader_consumer,'aux_rate_caller_withdrawal_paths':aux_rate_caller_consumer,'paired_curve_normalization_withdrawal_paths':paired_curve_normalization_consumer,'byte_ratio_producer_withdrawal_paths':byte_ratio_producer_consumer,'state_surface_caller_withdrawal_paths':state_surface_caller_consumer,'byte_factor_caller_withdrawal_paths':byte_factor_caller_consumer,'byte_sum_caller_withdrawal_paths':byte_sum_caller_consumer}
COMPONENT_FLAGS={'scalar_ram_leaf_paths':'exact_scalar_ram_leaves','scalar_ram_product_paths':'exact_scalar_ram_products','scalar_ram_gated_paths':'exact_scalar_ram_gated_paths','rpm_ram_withdrawal_paths':'exact_rpm_ram_withdrawal_paths','register_overflow_paths':'exact_register_overflow_paths','scalar_ram_word_paths':'exact_scalar_ram_word_paths','rpm_state_withdrawal_paths':'exact_rpm_state_withdrawal_paths','indexed_word_update_paths':'exact_indexed_word_update_paths','division_caller_withdrawal_paths':'exact_division_caller_withdrawal_paths','byte_curve_caller_withdrawal_paths':'exact_byte_curve_caller_withdrawal_paths','word_interp_caller_withdrawal_paths':'exact_word_interp_caller_withdrawal_paths','scaled_division_caller_withdrawal_paths':'exact_scaled_division_caller_withdrawal_paths','curve_scale_caller_withdrawal_paths':'exact_curve_scale_caller_withdrawal_paths','derivative_scale_caller_withdrawal_paths':'exact_derivative_scale_caller_withdrawal_paths','guarded_quotient_caller_withdrawal_paths':'exact_guarded_quotient_caller_withdrawal_paths','mixed_curve_caller_withdrawal_paths':'exact_mixed_curve_caller_withdrawal_paths','timing_remainder_caller_withdrawal_paths':'exact_timing_remainder_caller_withdrawal_paths','state_ratio_caller_withdrawal_paths':'exact_state_ratio_caller_withdrawal_paths','dfco_state_caller_withdrawal_paths':'exact_dfco_state_caller_withdrawal_paths','paired_inhibit_writer_withdrawal_paths':'exact_paired_inhibit_writer_withdrawal_paths','threshold_window_reader_withdrawal_paths':'exact_threshold_window_reader_withdrawal_paths','aux_rate_caller_withdrawal_paths':'exact_aux_rate_caller_withdrawal_paths','paired_curve_normalization_withdrawal_paths':'exact_paired_curve_normalization_withdrawal_paths','byte_ratio_producer_withdrawal_paths':'exact_byte_ratio_producer_withdrawal_paths','state_surface_caller_withdrawal_paths':'exact_state_surface_caller_withdrawal_paths','byte_factor_caller_withdrawal_paths':'exact_byte_factor_caller_withdrawal_paths','byte_sum_caller_withdrawal_paths':'exact_byte_sum_caller_withdrawal_paths'}


def native_rows(model,phase=None):
    declared=contract.descriptor(model.root);rows=declared['reference'];phases=set();seen=set()
    for row in rows:
        symbol=model.symbols.get(contract.symbol_key(row))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or not test_contract.exact((symbol.value('width'),symbol.value('signed')),
                    (contract.native_type(row,'width'),contract.native_type(row,'signed')))
                or not test_contract.exact(contract.plain(symbol.evidence),json.loads(row['original_symbol_evidence_json']))):
            raise ValueError('the scalar RAM leaf withdrawal changes a retained exact symbol, type or original evidence position')
        if row['owner'] in seen:continue
        seen.add(row['owner'])
        # Use the normal owned-document loader, including the normal writer overlay.
        document=store.load(model.root,Path(row['source']),model.overlay)
        matches=[name for name in ('original','proposed')
            if test_contract.exact(document,json.loads(row[name+'_native_json']))]
        if len(matches)!=1:raise ValueError('the scalar RAM leaf withdrawal changes its complete native preimage or postimage')
        current=matches[0];phases.add(current)
        ledger=json.loads(row['original_ledger_json' if current=='original' else 'proposed_ledger_json'])
        if ledger is None:
            if any(f'{name}/{kind}'==row['owner'] for kind,name,_,_ in model.stash.get('ledger_rows',())):
                raise ValueError('the exact full native withdrawal image introduces an absent ledger binding')
        elif not test_contract.exact(native_ledger(model,row['owner']),ledger):
            raise ValueError('the scalar RAM leaf withdrawal changes a retained native ledger identity or selector position')
    if len(seen)!=96 or len(phases)!=1 or phase is not None and phases!={phase}:
        raise ValueError('the scalar RAM leaf withdrawal requires one complete exact126-claim phase')
    current=next(iter(phases))
    for row in rows:
        old=json.loads(row['original_claim_json'])
        related=[link for link in model.links if (link.owner.key,link.type,link.to.key,link.slot,link.offset)
            ==(row['owner'],old['type'],old['to'],old['slot'],old['offset'])]
        if (current=='original' and (len(related)!=1 or not contract.original(row,related[0]))
                or current=='proposed' and related):
            raise ValueError('the scalar RAM leaf withdrawal changes an exact before-present/after-absent relation')
    from kb.model import SymbolKey
    for row in declared['function']:
        symbol=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or not test_contract.exact(store.load(model.root,Path(row['source']),model.overlay),
                    contract.function_native_document(row,current))):
            raise ValueError('the scalar RAM leaf withdrawal changes a complete retained natural function or original TEST position')
        if row['owner'] in {pin[0] for pin in contract.FUNCTION_POSTIMAGE_IDENTITIES}:
            if not test_contract.exact(native_ledger(model,row['owner']),json.loads(row[current+'_ledger_json'])):
                raise ValueError('the paired writer changes an exact function-end native ledger selector position')
    return rows


def require_primary(model,record=None):
    rows=native_rows(model)
    if record is None:record=json.loads(copy_evidence._read(model.root,copy_evidence.RECEIPT))
    components={key:consumer.require_primary(model,record) for key,consumer in COMPONENTS.items()}
    if (any(result.get(COMPONENT_FLAGS[key]) is not True or result.get('no_selected_datum_access') is not True
            or result.get('native_identity_admission') is not False for key,result in components.items())
            or {row['component'] for row in rows}!=set(components)):
        raise ValueError('the scalar RAM leaf withdrawal lacks complete independent natural-path and no-datum-access admission')
    if any(components[key].get('no_selected_ram_datum_access') is not True
            for key in ('rpm_ram_withdrawal_paths','register_overflow_paths','rpm_state_withdrawal_paths','indexed_word_update_paths','division_caller_withdrawal_paths','byte_curve_caller_withdrawal_paths','word_interp_caller_withdrawal_paths','curve_scale_caller_withdrawal_paths','derivative_scale_caller_withdrawal_paths','guarded_quotient_caller_withdrawal_paths','mixed_curve_caller_withdrawal_paths','timing_remainder_caller_withdrawal_paths','dfco_state_caller_withdrawal_paths','paired_inhibit_writer_withdrawal_paths','threshold_window_reader_withdrawal_paths','byte_factor_caller_withdrawal_paths','byte_sum_caller_withdrawal_paths')):
        raise ValueError('the RAM-root withdrawal requires its own exact native-address/alias absence guard')
    if any(components[key].get('complete_direct_helpers_same_primary') is not True
            for key in ('division_caller_withdrawal_paths','byte_curve_caller_withdrawal_paths','scaled_division_caller_withdrawal_paths','curve_scale_caller_withdrawal_paths','derivative_scale_caller_withdrawal_paths','guarded_quotient_caller_withdrawal_paths','mixed_curve_caller_withdrawal_paths','timing_remainder_caller_withdrawal_paths','state_ratio_caller_withdrawal_paths','threshold_window_reader_withdrawal_paths','aux_rate_caller_withdrawal_paths','paired_curve_normalization_withdrawal_paths','byte_ratio_producer_withdrawal_paths','state_surface_caller_withdrawal_paths','byte_factor_caller_withdrawal_paths','byte_sum_caller_withdrawal_paths')):
        raise ValueError('the division caller withdrawal lacks the separate complete direct-helper original from the identical primary')
    if components['word_interp_caller_withdrawal_paths'].get('complete_timing_helpers_same_primary') is not True:
        raise ValueError('the word caller withdrawal lacks the unchanged complete timing-helper original from the identical primary')
    if components['scaled_division_caller_withdrawal_paths'].get('complete_register_helpers_same_primary') is not True:
        raise ValueError('the scaling caller lacks the unchanged complete register-only original from the identical primary')
    if components['curve_scale_caller_withdrawal_paths'].get('complete_curve_helpers_same_primary') is not True:
        raise ValueError('the curve-scale caller lacks the unchanged complete neighboring curve original from the identical primary')
    require_uptight_RAM3348_result(components['curve_scale_caller_withdrawal_paths'])
    if any(components['derivative_scale_caller_withdrawal_paths'].get(flag) is not True for flag in (
            'complete_timing_helpers_same_primary','complete_normalization_helpers_same_primary','complete_viridian_caller_same_primary')):
        raise ValueError('the derivative-scale callers lack unchanged complete timing, normalization or viridian originals from the identical primary')
    for path in (contract.DESCRIPTOR,'tools/kb/src/kb/scalar_ram_leaf_withdrawal_contract.py',
            'tools/kb/src/kb/scalar_ram_leaf_withdrawal_evidence.py','tools/kb/src/kb/scalar_ram_leaf_withdrawal_resolution.py'):
        if record['candidate']['producer_inputs'].get(path)!=hashlib.sha256(copy_evidence._read(model.root,path)).hexdigest():
            raise ValueError('the scalar RAM leaf withdrawal source differs from its complete original input snapshot')
    if any(components['mixed_curve_caller_withdrawal_paths'].get(flag) is not True for flag in (
            'complete_timing_helpers_same_primary','complete_implicit_caller_same_primary','complete_register_helpers_same_primary')):
        raise ValueError('the mixed curve withdrawal omits a full timing,implicit or register-helper original from the identical primary')
    if any(components['timing_remainder_caller_withdrawal_paths'].get(flag) is not True for flag in (
            'complete_timing_helpers_same_primary','complete_normalization_helpers_same_primary',
            'complete_viridian_caller_same_primary','complete_remainder_source_same_primary')):
        raise ValueError('the timing remainder withdrawal omits a complete preceding helper or real remainder source from the identical primary')
    if any(components['state_ratio_caller_withdrawal_paths'].get(flag) is not True for flag in (
            'complete_direct_helpers_same_primary','complete_previous_byte_curve_caller_same_primary',
            'complete_standard_implicit_byte_same_primary')):
        raise ValueError('the state ratio withdrawal omits a complete preceding helper,byte caller or standard implicit-byte original from the identical primary')
    if components['dfco_state_caller_withdrawal_paths'].get('complete_real_rotation_helper') is not True:
        raise ValueError('the DFCO withdrawal omits the complete real rotation helper from the identical primary')
    dfco=components['dfco_state_caller_withdrawal_paths']
    strict=[row['original_claim_sha256'] for row in rows if row['component']=='dfco_state_caller_withdrawal_paths'
        and row['function']==0x503E0 and row['id']!=contract.READER_ONLY_WITH_RETAINED_WRITER[0]]
    if (dfco.get('reader_only1939_retained_writer') is not True
            or dfco.get('prior1939_complete_state_independence') is not True
            or dfco.get('reader_only1939_original')!=contract.READER_ONLY_WITH_RETAINED_WRITER[1]
            or not test_contract.exact(dfco.get('strict_absence_originals'),strict)
            or not test_contract.exact(dfco.get('retained1939_write_sites'),[0x50574,0x50594])):
        raise ValueError('the DFCO reader-only withdrawal lacks exact direction,retained writes or complete prior-byte independence')
    require_restore16aa_result(dfco)

    if any(components['paired_inhibit_writer_withdrawal_paths'].get(flag) is not True for flag in (
            'complete_real_nibble_helper','entry_scoped_root_absence','complete_RMW_read_write_pairs')):
        raise ValueError('the paired writer withdrawal omits its exact entry scope,real helper or ordered physical RMW operands')
    if components['threshold_window_reader_withdrawal_paths'].get('complete_previous_byte_curve_caller_same_primary') is not True:
        raise ValueError('the threshold window omits the complete preceding signed-divider byte-caller original from the identical primary')
    if components['aux_rate_caller_withdrawal_paths'].get('complete_real_auxiliary_gate') is not True:
        raise ValueError('the auxiliary rate withdrawal omits the complete real8C3FA gate from the identical primary')
    if any(components['paired_curve_normalization_withdrawal_paths'].get(flag) is not True for flag in (
            'complete_previous_byte_curve_caller_same_primary','complete_previous_mixed_curve_caller_same_primary','complete_raw16_axis17_data')):
        raise ValueError('the paired curve normalization omits the complete unchanged byte and mixed curve originals from the identical primary')
    if any(components['byte_ratio_producer_withdrawal_paths'].get(flag) is not True for flag in (
            'complete_signed_shift10','complete_actual_post_DIV1_R1_carrier')):
        raise ValueError('the byte ratio producer omits the complete real signed shift or its exact actual saved post-DIV1 R1 frame continuity')
    if any(components['state_surface_caller_withdrawal_paths'].get(flag) is not True for flag in (
            'complete_local_word_argument','complete_three_state_modes')):
        raise ValueError('the state surface omits its exact complete local word carrier or three natural state modes')
    if any(components['byte_factor_caller_withdrawal_paths'].get(flag) is not True for flag in (
            'complete_signed_word_difference','complete_dual_byte_partial_product','complete_both_natural_curve_calls')):
        raise ValueError('the byte factor omits its complete signed-word difference,dual-byte partial products or both natural curve calls')
    if any(components['byte_sum_caller_withdrawal_paths'].get(flag) is not True for flag in (
            'complete_clipped_byte_coordinate','complete_unsigned_byte_minimum','complete_two_saturating_word_sums')):
        raise ValueError('the byte sum omits its complete clipped coordinate,byte minimum or two saturating word sums')
    return dict(scope='exact-scalar-ram-leaf-withdrawal',components=components,
        original_process_sha256=record['process_sha256'],native_model=record['native_model'],
        original_claims={row['id']:row['original_claim_sha256'] for row in rows},
        replacement_relation=False,native_identity_admission=False,scale_admission=False,
        units_admission=False,natural_caller_reachability=False,hardware_qualification=False)


def require_current(model):
    before=dependency_state(model);result=require_primary(model)
    if dependency_state(model)!=before:raise ValueError('the scalar RAM leaf withdrawal input or original changes during admission')
    return result


def failure(evidence,symbol=None,model=None,claim=None):
    return 'a scalar RAM leaf withdrawal grants no owning evidence or supported fact' if contract.registered(evidence) else None


def accepted(model,symbol,function,claim):return None


def link_failure(model,link):
    return 'the exact scalar RAM leaf physical access is unsupported and requires its complete withdrawal' if contract.looks_like_access(link) else None


def identity_only(symbol):return False


def require_uptight_RAM3348_result(result):
    original=result.get('uptight_RAM3348_original_stdout_sha256')
    if (result.get('complete_uptight_RAM3348_same_primary') is not True
            or result.get('uptight_RAM3348_withdrawal_original')!=contract.UPTIGHT_RAM3348_WITHDRAWAL[1]
            or type(original) is not str or len(original)!=64
            or any(character not in '0123456789abcdef' for character in original)
            or original!=result.get('curve_helper_original_stdout_sha256')):
        raise ValueError('the RAM3348 withdrawal lacks its complete exact uptight callee original from the identical primary')
    return True


def require_restore16aa_result(result):
    source=result.get('stdout_sha256')
    if (result.get('reader_only16aa_retained_writer') is not True
            or result.get('prior16aa_complete_state_independence') is not True
            or result.get('reader_only16aa_original')!=contract.RESTORE_READER_ONLY_WITH_RETAINED_WRITER[1]
            or not test_contract.exact(result.get('retained16aa_write_sites'),[0x501AE])
            or type(source) is not str or len(source)!=64 or any(c not in '0123456789abcdef' for c in source)):
        raise ValueError('the restore reader withdrawal lacks its exact same-primary original, retained writer or full prior state')
    return True
