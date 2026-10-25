"""Explicit typed cases for native TEST qualification, without execution or admission."""

from kb import test_contract

SELECTORS = (
    'patches/tests/test_rom_address_profiles.py::test_1me3b_unreferenced_ignition_routine_is_bound_to_the_image',
    'tools/kb/tests/test_airflow_adc.py::test_maf_adc_unsigned_word_sources_and_shifts_match_stock',
    'tools/kb/tests/test_airflow_aggregate.py::test_combined_maf_longword_wrap_signed_correction_unsigned_addition_and_zero_clamp_match_stock',
    'tools/kb/tests/test_airflow_bfs_base.py::test_primary_bfs_speed_selection_split_product_unsigned_divisions_and_q7_store_match_stock',
    'tools/kb/tests/test_airflow_bfs_limit.py::test_bfs_limit_signed_correction_byte_interpolation_diagnostic_bypass_and_word_store_match_stock',
    'tools/kb/tests/test_airflow_bfs_rate.py::test_bfs_rate_sum_difference_latch_timers_correction_blend_and_query_match_stock',
    'tools/kb/tests/test_airflow_compensation.py::test_maf_initialization_previous_word_numerator_and_wrap_match_stock',
    'tools/kb/tests/test_airflow_contribution.py::test_maf_contribution_modes_signed_rounding_state_caps_and_natural_return_match_stock',
    'tools/kb/tests/test_airflow_filter.py::test_maf_working_copy_mode_previous_word_weight_and_anti_stall_match_stock',
    'tools/kb/tests/test_airflow_fuel_compensation.py::test_fuel_compensation_axes_interpolation_selectors_bypass_and_store_match_stock',
    'tools/kb/tests/test_airflow_scaling.py::test_maf_scaling_guard_and_order_match_stock',
    'tools/kb/tests/test_airflow_transfer.py::test_maf_coordinate_word_curve_and_both_publications_match_stock',
    'tools/kb/tests/test_bank_base_pulse_chain.py::test_bank_base_pulse_chain_owner_contract',
    'tools/kb/tests/test_bank_base_pulse_chain.py::test_bank_base_pulse_registered_stock_contract',
    'tools/kb/tests/test_battery_scaling.py::test_battery_shift_byte_truncation_guard_calls_and_cap_match_stock',
    'tools/kb/tests/test_channel_pulse_chain.py::test_channel_pulse_chain_owner_contract',
    'tools/kb/tests/test_channel_pulse_chain.py::test_channel_pulse_registered_stock_contract',
    'tools/kb/tests/test_closed_loop_adjustment_chain.py::test_adjustment_owner_contract',
    'tools/kb/tests/test_closed_loop_adjustment_chain.py::test_registered_adjustment_stock_contract',
    'tools/kb/tests/test_closed_loop_conversion_chain.py::test_conversion_owner_contract',
    'tools/kb/tests/test_closed_loop_conversion_chain.py::test_registered_conversion_stock_contract',
    'tools/kb/tests/test_closed_loop_feedback_chain.py::test_feedback_owner_contract',
    'tools/kb/tests/test_closed_loop_feedback_chain.py::test_registered_feedback_stock_contract',
    'tools/kb/tests/test_closed_loop_indexed_byte.py::test_closed_loop_indexed_byte_placement',
    'tools/kb/tests/test_closed_loop_publication_chain.py::test_grid_learning_owner_contract',
    'tools/kb/tests/test_closed_loop_publication_chain.py::test_grid_selection_owner_contract',
    'tools/kb/tests/test_closed_loop_publication_chain.py::test_registered_closed_loop_stock_contract',
    'tools/kb/tests/test_closed_loop_publication_chain.py::test_stft_owner_contract',
    'tools/kb/tests/test_connected_injection_chain.py::test_connected_injection_owner_contract',
    'tools/kb/tests/test_connected_injection_chain.py::test_connected_stock_regions_contract',
    'tools/kb/tests/test_engine_speed_axes.py::test_rpm_axis_arguments_widths_and_fraction_scaling_match_stock',
    'tools/kb/tests/test_engine_speed_byte_tables.py::test_last_rpm_byte_inputs_and_cvtc_load_selection_match_stock',
    'tools/kb/tests/test_engine_speed_conditions.py::test_rpm_override_masks_branches_and_operands_match_stock',
    'tools/kb/tests/test_engine_speed_crank_capture.py::test_osbr1_word_capture_first_sample_and_interval_match_stock',
    'tools/kb/tests/test_engine_speed_division.py::test_rpm_division_modes_zero_and_saturation_match_stock',
    'tools/kb/tests/test_engine_speed_drop.py::test_rpm_drop_modes_rising_branch_and_operands_match_stock',
    'tools/kb/tests/test_engine_speed_event_interval.py::test_event_interval_modes_wrap_holdoff_and_calls_match_stock',
    'tools/kb/tests/test_engine_speed_median.py::test_rpm_median_history_modes_and_zero_period_match_stock',
    'tools/kb/tests/test_engine_speed_scaling.py::test_rpm_snapshot_dispatch_and_all_fourteen_words_match_stock',
    'tools/kb/tests/test_engine_speed_tooth_normalization.py::test_tooth_normalization_sync_multiplier_and_fallback_match_stock',
    'tools/kb/tests/test_fuel_cut_consumer_chain.py::test_fuel_cut_consumer_owner_contract',
    'tools/kb/tests/test_fuel_cut_consumer_chain.py::test_fuel_cut_consumer_registered_stock_contract',
    'tools/kb/tests/test_fuel_upstream_chain.py::test_fuel_upstream_owner_contract',
    'tools/kb/tests/test_fuel_upstream_chain.py::test_fuel_upstream_stock_regions_contract',
    'tools/kb/tests/test_ici0a_ratio_chain.py::test_ici0a_ratio_chain_owner_contract',
    'tools/kb/tests/test_indexed_input_word.py::test_indexed_input_word_path',
    'tools/kb/tests/test_injection_catchup_chain.py::test_injection_catchup_owner_contract',
    'tools/kb/tests/test_injection_catchup_chain.py::test_injection_catchup_registered_stock_contract',
    'tools/kb/tests/test_injection_count_chain.py::test_injection_count_owner_contract',
    'tools/kb/tests/test_injection_count_chain.py::test_injection_count_registered_stock_contract',
    'tools/kb/tests/test_injection_dispatch_chain.py::test_injection_dispatch_owner_contract',
    'tools/kb/tests/test_injection_dispatch_chain.py::test_injection_dispatch_registered_stock_contract',
    'tools/kb/tests/test_injection_prologue_chain.py::test_injection_prologue_owner_contract',
    'tools/kb/tests/test_injection_prologue_chain.py::test_injection_prologue_registered_stock_contract',
    'tools/kb/tests/test_injection_sequencing_chain.py::test_injection_sequencing_owner_contract',
    'tools/kb/tests/test_injection_sequencing_chain.py::test_injection_sequencing_registered_stock_contract',
    'tools/kb/tests/test_injection_slot_chain.py::test_injection_slot_chain_owner_contract',
    'tools/kb/tests/test_injection_slot_chain.py::test_injection_slot_registered_stock_contract',
    'tools/kb/tests/test_injection_snapshot_chain.py::test_injection_snapshot_chain_owner_contract',
    'tools/kb/tests/test_injection_snapshot_chain.py::test_injection_snapshot_registered_stock_contract',
    'tools/kb/tests/test_injection_start_delay_chain.py::test_injection_start_delay_chain_owner_contract',
    'tools/kb/tests/test_injection_start_delay_chain.py::test_injection_start_delay_registered_stock_contract',
    'tools/kb/tests/test_knock_comparison_chain.py::test_knock_comparison_chain_owner_contract',
    'tools/kb/tests/test_knock_comparison_chain.py::test_knock_comparison_registered_stock_contract',
    'tools/kb/tests/test_knock_event_publication_chain.py::test_knock_event_publication_chain_owner_contract',
    'tools/kb/tests/test_knock_event_publication_chain.py::test_knock_event_publication_registered_stock_contract',
    'tools/kb/tests/test_knock_event_retard_chain.py::test_knock_event_retard_chain_owner_contract',
    'tools/kb/tests/test_knock_event_retard_chain.py::test_knock_event_retard_registered_stock_contract',
    'tools/kb/tests/test_knock_integration_chain.py::test_knock_integration_chain_owner_contract',
    'tools/kb/tests/test_knock_integration_chain.py::test_knock_integration_registered_stock_contract',
    'tools/kb/tests/test_knock_metric_chain.py::test_knock_metric_chain_owner_contract',
    'tools/kb/tests/test_knock_metric_chain.py::test_knock_metric_registered_stock_contract',
    'tools/kb/tests/test_knock_normalization_chain.py::test_knock_normalization_chain_owner_contract',
    'tools/kb/tests/test_knock_normalization_chain.py::test_knock_normalization_registered_stock_contract',
    'tools/kb/tests/test_knock_reference_learning_chain.py::test_knock_reference_learning_chain_owner_contract',
    'tools/kb/tests/test_knock_reference_learning_chain.py::test_knock_reference_learning_registered_stock_contract',
    'tools/kb/tests/test_knock_state_selection_chain.py::test_knock_state_selection_chain_owner_contract',
    'tools/kb/tests/test_knock_state_selection_chain.py::test_knock_state_selection_registered_stock_contract',
    'tools/kb/tests/test_knock_target_homology.py::test_knock_target_homology_exact_registered_rom_contract',
    'tools/kb/tests/test_knock_target_homology.py::test_knock_target_homology_owner_contract',
    'tools/kb/tests/test_knock_threshold_chain.py::test_knock_threshold_chain_owner_contract',
    'tools/kb/tests/test_knock_threshold_chain.py::test_knock_threshold_registered_stock_contract',
    'tools/kb/tests/test_knock_timing_byte_chain.py::test_knock_timing_byte_chain_owner_contract',
    'tools/kb/tests/test_knock_timing_byte_chain.py::test_knock_timing_byte_registered_stock_contract',
    'tools/kb/tests/test_load_normalization.py::test_normalized_bfs_cached_word_division_byte_cap_and_store_match_stock',
    'tools/kb/tests/test_load_snapshot.py::test_load_snapshot_history_length_dispatch_delay_load_and_all_seven_word_stores_match_stock',
    'tools/kb/tests/test_ltft_publication_chain.py::test_ltft_publication_chain_owner_contract',
    'tools/kb/tests/test_ltft_publication_chain.py::test_ltft_publication_registered_stock_contract',
    'tools/kb/tests/test_maf_indexed_output_byte.py::test_maf_indexed_output_byte_placement',
    'tools/kb/tests/test_main_rpm_fuel_cut_chain.py::test_main_rpm_fuel_cut_owner_contract',
    'tools/kb/tests/test_main_rpm_fuel_cut_chain.py::test_main_rpm_fuel_cut_registered_stock_contract',
    'tools/kb/tests/test_ram_structure.py::test_indexed_mode_byte_paths',
    'tools/kb/tests/test_ram_structure.py::test_indexed_state_longword_path',
    'tools/kb/tests/test_ram_structure.py::test_indexed_word_copy_path',
    'tools/kb/tests/test_ram_structure.py::test_injection_precursor_path',
    'tools/kb/tests/test_ram_structure.py::test_maf_extension_record_path',
    'tools/kb/tests/test_ram_structure.py::test_maf_indexed_state_path',
    'tools/kb/tests/test_ram_structure.py::test_snapshot_destination_path',
    'tools/kb/tests/test_ram_structure.py::test_snapshot_source_and_decoder_path',
    'tools/kb/tests/test_throttle_correlation_indexed_inputs.py::test_throttle_correlation_274a_word_placement',
    'tools/kb/tests/test_throttle_correlation_indexed_inputs.py::test_throttle_correlation_2752_word_placement',
    'tools/kb/tests/test_throttle_correlation_indexed_inputs.py::test_throttle_correlation_275a_word_placement',
    'tools/kb/tests/test_throttle_correlation_indexed_inputs.py::test_throttle_correlation_input_byte_placement',
    'tools/kb/tests/test_vehicle_speed_fuel_cut_chain.py::test_vehicle_speed_fuel_cut_owner_contract',
    'tools/kb/tests/test_vehicle_speed_fuel_cut_chain.py::test_vehicle_speed_fuel_cut_registered_stock_contract',
    'tools/mapkit/tests/test_candidate_identity_paths.py::test_09eca_q8_progress_and_saturation',
    'tools/mapkit/tests/test_candidate_identity_paths.py::test_12918_selected_internal_floor',
    'tools/mapkit/tests/test_candidate_identity_paths.py::test_1295c_branch_local_upper_clamp',
    'tools/mapkit/tests/test_candidate_identity_paths.py::test_12e52_strict_upper_load_bound',
    'tools/mapkit/tests/test_candidate_identity_paths.py::test_14982_event_counter_threshold',
    'tools/mapkit/tests/test_candidate_identity_paths.py::test_14e52_signed_q16_progress',
    'tools/mapkit/tests/test_candidate_identity_paths.py::test_749bc_direct_lookup_and_arbitration',
    'tools/mapkit/tests/test_candidate_identity_paths.py::test_c98e_signed_correction_and_stock_gate',
    'tools/mapkit/tests/test_ici0a_ratio_path.py::test_ici0a_ratio_cell_path',
    'tools/mapkit/tests/test_ici0a_ratio_path.py::test_ici0a_ratio_numeric_contract',
    'tools/mapkit/tests/test_lavender_scale.py::test_lavender_nominal_initialized_scale',
    'tools/mapkit/tests/test_local_count_scales.py::test_1295c_local_bound_scale',
    'tools/mapkit/tests/test_local_count_scales.py::test_c98e_centered_word_scale',
    'tools/mapkit/tests/test_rpm_axis_scale.py::test_banana_shark_nominal_rpm_scale',
    'tools/mapkit/tests/test_rpm_axis_scale.py::test_dashing_whippet_nominal_rpm_scale',
    'tools/mapkit/tests/test_rpm_axis_scale.py::test_resilient_eagle_nominal_rpm_scale',
    'tools/mapkit/tests/test_rpm_axis_scale.py::test_vegan_fulmar_nominal_rpm_scale',
    'tools/mapkit/tests/test_vq37_command_count_scales.py::test_vvel_command_shaft_angle_scale',
    'tools/mapkit/tests/test_vq37_command_count_scales.py::test_vvel_command_shaft_angle_second_scale',
    'tools/mapkit/tests/test_vq37_intake_duty_scheme.py::test_cell_scale_bounds_the_programmed_duty',
    'tools/mapkit/tests/test_vq37_ramp_delay_scale.py::test_ramp_delay_local_count_scale',
    'tools/mapkit/tests/test_vq37_running_rpm_scale.py::test_intake_cvtc_target_running_nominal_rpm_scale',
    'tools/mapkit/tests/test_vq37_running_rpm_scale.py::test_vvel_duration_running_nominal_rpm_scale',
    'tools/mapkit/tests/test_vq37_timing_state_scale.py::test_timing_state_addend_alternate_scale',
    'tools/mapkit/tests/test_vvel_cold_axis_scale.py::test_vvel_cold_axis_pid05_code_domain',
    'tools/mapkit/tests/test_vvel_temperature_axis_scale.py::test_vvel_duration_startup_axis_nominal_temperature',
    'tools/mapkit/tests/test_vvel_temperature_axis_scale.py::test_vvel_duration_startup_blend_axis_nominal_temperature',
    'tools/mapkit/tests/test_vvel_temperature_axis_scale.py::test_vvel_duration_throttled_ramp_delay_axis_nominal_temperature',
)

ROM_IMAGES = ('JK00A', 'JK03A', 'JK03B', 'JK08A')
VQ37_IMAGES = ('JK78C', '1ND0A', '1ND3B', '1ME3B')

# Module-scoped fixture parameters are actual callspec values, not image bytes.
IMAGE_FIXTURES = {
    'tools/mapkit/tests/test_ici0a_ratio_path.py': ROM_IMAGES,
    'tools/mapkit/tests/test_lavender_scale.py': (*ROM_IMAGES, 'JK00C', 'JK00D'),
    'tools/mapkit/tests/test_local_count_scales.py': ROM_IMAGES,
    'tools/mapkit/tests/test_rpm_axis_scale.py': ROM_IMAGES,
    'tools/mapkit/tests/test_vq37_command_count_scales.py': VQ37_IMAGES,
    'tools/mapkit/tests/test_vq37_running_rpm_scale.py': VQ37_IMAGES,
    'tools/mapkit/tests/test_vq37_timing_state_scale.py': VQ37_IMAGES,
    'tools/mapkit/tests/test_vvel_cold_axis_scale.py': VQ37_IMAGES,
    'tools/mapkit/tests/test_vvel_temperature_axis_scale.py': VQ37_IMAGES,
}

ROM_SELECTORS = (
    'tools/kb/tests/test_closed_loop_indexed_byte.py::test_closed_loop_indexed_byte_placement',
    'tools/kb/tests/test_indexed_input_word.py::test_indexed_input_word_path',
    'tools/kb/tests/test_maf_indexed_output_byte.py::test_maf_indexed_output_byte_placement',
    'tools/kb/tests/test_ram_structure.py::test_indexed_mode_byte_paths',
    'tools/kb/tests/test_ram_structure.py::test_indexed_state_longword_path',
    'tools/kb/tests/test_ram_structure.py::test_indexed_word_copy_path',
    'tools/kb/tests/test_ram_structure.py::test_injection_precursor_path',
    'tools/kb/tests/test_ram_structure.py::test_maf_extension_record_path',
    'tools/kb/tests/test_ram_structure.py::test_maf_indexed_state_path',
    'tools/kb/tests/test_ram_structure.py::test_snapshot_destination_path',
    'tools/kb/tests/test_ram_structure.py::test_snapshot_source_and_decoder_path',
    'tools/kb/tests/test_throttle_correlation_indexed_inputs.py::test_throttle_correlation_274a_word_placement',
    'tools/kb/tests/test_throttle_correlation_indexed_inputs.py::test_throttle_correlation_2752_word_placement',
    'tools/kb/tests/test_throttle_correlation_indexed_inputs.py::test_throttle_correlation_275a_word_placement',
    'tools/kb/tests/test_throttle_correlation_indexed_inputs.py::test_throttle_correlation_input_byte_placement',
)

FUNCTION_PARAMETERS = {
    **{selector: ('rom', ROM_IMAGES) for selector in ROM_SELECTORS},
    'tools/kb/tests/test_closed_loop_publication_chain.py::test_registered_closed_loop_stock_contract':
        ('packet', ('stft', 'selection', 'learning')),
    'tools/kb/tests/test_injection_sequencing_chain.py::test_injection_sequencing_registered_stock_contract':
        ('scope', ('pending', 'reciprocal', 'tooth', 'offset')),
    'tools/mapkit/tests/test_vq37_ramp_delay_scale.py::test_ramp_delay_local_count_scale':
        ('raw', tuple(range(256))),
}

UNPARAMETRIZED_IMAGE_SELECTORS = (
    'tools/mapkit/tests/test_vvel_temperature_axis_scale.py::test_vvel_duration_startup_blend_axis_nominal_temperature',
    'tools/mapkit/tests/test_vvel_temperature_axis_scale.py::test_vvel_duration_throttled_ramp_delay_axis_nominal_temperature',
)


def _case(selector, parameters, suffix):
    nodeid = selector + ('[' + suffix + ']' if suffix is not None else '')
    return test_contract.Case(nodeid, parameters)


def cases(selector):
    """Require a declared selector; no discovery or parameter-name inference."""
    if type(selector) is not str or selector not in SELECTORS:
        raise ValueError('the TEST selector has no explicit typed case declaration')
    path = selector.split('::', 1)[0]
    image_parameters = IMAGE_FIXTURES.get(path)
    if selector in UNPARAMETRIZED_IMAGE_SELECTORS:
        image_parameters = None
    function_parameters = FUNCTION_PARAMETERS.get(selector)
    if image_parameters is not None and function_parameters is not None:
        raise ValueError('the TEST selector requires an explicit combined parameter declaration')
    if image_parameters is not None:
        return tuple(_case(selector, {'image': value}, value) for value in image_parameters)
    if function_parameters is not None:
        name, values = function_parameters
        return tuple(_case(selector, {name: value}, str(value)) for value in values)
    return (_case(selector, {}, None),)


def ordered():
    """Declare module-fixture grouping before the actual pytest collector runs."""
    files = {}
    for selector in SELECTORS:
        files.setdefault(selector.split('::', 1)[0], []).append(selector)
    result = []
    for path, selectors in files.items():
        if path in IMAGE_FIXTURES:
            for image in IMAGE_FIXTURES[path]:
                for selector in selectors:
                    if selector not in UNPARAMETRIZED_IMAGE_SELECTORS:
                        result.append(_case(selector, {'image': image}, image))
            for selector in selectors:
                if selector in UNPARAMETRIZED_IMAGE_SELECTORS:
                    result.extend(cases(selector))
        else:
            for selector in selectors:
                result.extend(cases(selector))
    return tuple(result)


def contract(name, selectors):
    """Joint profiles retain the explicitly declared global execution order."""
    if (type(selectors) is not tuple or not selectors
            or len(set(selectors)) != len(selectors)
            or any(selector not in SELECTORS for selector in selectors)):
        raise ValueError('a TEST contract requires explicit unique declared selectors')
    selected = set(selectors)
    values = tuple(case for case in ordered() if case.nodeid.split('[', 1)[0] in selected)
    return test_contract.Contract(name, values)
