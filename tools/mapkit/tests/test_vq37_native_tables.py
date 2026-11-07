import hashlib

import pytest

from tools.mapkit import emit_def
from tools.mapkit import rom as romkit
from tools.mapkit import vq37_native_tables


TARGETS = ("JK78C", "1ND0A", "1ND3B", "1ME3B")
SELECTOR_ROLES = {
    "fuel_compensation_alternate",
    "fuel_compensation_coefficient_curve",
    "timing_state_addend_alternate",
}
FUEL_TABLE_ROLES = {
    "fuel_composite_additional_surface",
    "transient_fuel_additional_surface",
    "fuel_four_factor_surface",
}
FUEL_AXIS_ROLES = {
    "fuel_compensation_coefficient_axis",
    "fuel_composite_surface_x_axis",
    "fuel_composite_surface_y_axis",
    "transient_fuel_multiplier_x_axis",
    "transient_fuel_multiplier_y_axis",
    "fuel_four_factor_surface_x_axis",
    "fuel_four_factor_surface_y_axis",
}
VVEL_TABLE_ROLES = {
    "vvel_duration_running",
    "vvel_duration_throttled",
    "vvel_duration_hot_intake_idle",
    "vvel_duration_hot_intake_idle_knock",
    "vvel_duration_hot_intake_idle_floor",
    "vvel_duration_hot_intake_idle_knock_floor",
    "vvel_duration_mode_14",
    "vvel_duration_cold",
    "vvel_duration_startup",
    "vvel_duration_model_hot_intake_idle",
    "vvel_duration_model_hot_intake_idle_knock",
    "vvel_duration_throttled_ramp_delay",
    "vvel_duration_startup_blend",
    "intake_cvtc_target_running",
    "intake_cvtc_target_throttled",
    "intake_cvtc_target_cold",
    "vvel_command_shaft_angle",
    "vvel_shaft_angle_limit_engine_speed",
    "vvel_shaft_angle_limit_cvtc",
    "vvel_shaft_angle_monitor_floor_a",
    "vvel_shaft_angle_monitor_floor_b",
    "vvel_command_shaft_angle_second",
    "vvel_shaft_angle_monitor_floor_a_second",
    "vvel_shaft_angle_monitor_floor_b_second",
    "vvel_duration_characteristic",
    "vvel_idle_model_duration_floor",
    "vvel_idle_model_floor_hold_passes",
    "vvel_idle_model_floor_release_step",
    "vvel_idle_model_high_load_duration",
    "vvel_idle_model_high_load_phase",
    "vvel_idle_model_high_load_blend_start",
    "vvel_idle_model_high_load_blend_end",
    "vvel_idle_model_duration",
    "vvel_idle_model_phase",
    "vvel_hot_intake_threshold",
    "vvel_hot_intake_threshold_knock",
    "vvel_duration_model_running",
    "intake_cvtc_model_running",
    "intake_cvtc_model_default",
}
VVEL_AXIS_ROLES = {
    "vvel_duration_running_axis",
    "vvel_duration_throttled_axis",
    "vvel_duration_hot_intake_idle_axis_x",
    "vvel_duration_hot_intake_idle_axis_y",
    "vvel_duration_hot_intake_idle_floor_axis",
    "vvel_cold_axis",
    "vvel_duration_startup_axis",
    "vvel_duration_model_hot_intake_idle_axis_x",
    "vvel_duration_model_hot_intake_idle_axis_y",
    "vvel_duration_throttled_ramp_delay_axis",
    "vvel_duration_startup_blend_axis",
    "intake_cvtc_target_running_axis",
    "intake_cvtc_target_throttled_axis_x",
    "intake_cvtc_target_throttled_axis_y",
    "vvel_shaft_angle_axis",
    "vvel_shaft_angle_limit_engine_speed_axis",
    "vvel_shaft_angle_limit_cvtc_axis",
    "vvel_shaft_angle_monitor_floor_a_axis",
    "vvel_shaft_angle_monitor_floor_b_axis",
    "vvel_shaft_angle_second_axis",
    "vvel_shaft_angle_monitor_floor_a_second_axis",
    "vvel_shaft_angle_monitor_floor_b_second_axis",
    "vvel_duration_characteristic_axis",
    "vvel_idle_model_duration_floor_axis",
    "vvel_idle_model_margin_axis",
    "vvel_idle_model_high_load_duration_axis",
    "vvel_idle_model_high_load_phase_axis",
    "vvel_idle_model_high_load_blend_axis",
    "vvel_idle_model_axis_x",
    "vvel_idle_model_axis_y",
    "vvel_hot_intake_threshold_axis",
    "vvel_duration_model_running_axis_y",
}
# The executed surfaces of the mode-selected half of the ignition coordinator.
IGNITION_PAIR_ROLES = {
    "ignition_surface_hot",
    "ignition_surface_cold",
}
# JK78C selects between the pair by coolant temperature and carries no
# state-code dispatch, so the 8x8 surfaces and their axes exist on 1ND and
# 1ME3B only.
IGNITION_STATE_TABLE_ROLES = {
    "ignition_surface_state_3",
    "ignition_surface_state_4",
    "ignition_surface_state_5",
    "ignition_surface_state_6_7",
}
IGNITION_STATE_AXIS_ROLES = {
    "ignition_state_surface_axis_x",
    "ignition_state_surface_axis_y",
}
IGNITION_STATE_ROLES = IGNITION_STATE_TABLE_ROLES | IGNITION_STATE_AXIS_ROLES
IGNITION_TABLE_ROLES = IGNITION_PAIR_ROLES | IGNITION_STATE_TABLE_ROLES
CVTC_TABLE_ROLES = {
    "intake_cvtc_duty_hold",
    "intake_cvtc_duty_offset",
    "intake_cvtc_duty_error_divisor_positive",
    "intake_cvtc_duty_error_divisor_negative",
    "intake_cvtc_duty_filter_positive",
    "intake_cvtc_duty_filter_negative",
    "intake_cvtc_duty_feedback_upper",
    "intake_cvtc_duty_feedback_lower",
    "intake_cvtc_settle_count",
    "intake_cvtc_target_limit",
}
CVTC_AXIS_ROLES = {
    "intake_cvtc_duty_axis_x",
    "intake_cvtc_duty_axis_y",
    "intake_cvtc_settle_count_axis",
    "intake_cvtc_target_limit_axis",
}
# The end-of-injection writer reads word curves on an explicit engine-speed
# axis where JK08A reads byte curves on an implicit axis.
INJECTION_TABLE_ROLES = {
    "injection_end_angle_base",
    "injection_end_angle_conditional",
}
INJECTION_AXIS_ROLES = {"injection_end_angle_axis"}
# The request transition conditioner reads its calibration through its own
# literal pool on every target.
CONDITIONER_TABLE_ROLES = {
    "request_transition_input_byte_threshold",
    "request_transition_word_gate_threshold",
    "request_transition_hold_reload",
    "request_transition_duration_table",
    "request_transition_offset_surface",
    "request_transition_reference_multiplier",
    "request_transition_reference_floor",
    "request_transition_rate_special_branch",
    "request_transition_rate_state_a_above_b",
    "request_transition_rate_other_state_relation",
    "request_transition_error_correction_gain",
    "request_transition_error_correction_limit",
    "request_transition_recovery_decrement",
}
CONDITIONER_AXIS_ROLES = {
    "request_transition_rate_coordinate_axis",
    "request_transition_rate_state_axis",
}
CONDITIONER = {"JK78C": 0x96CE0, "1ND0A": 0xABC6E, "1ND3B": 0xABC6E, "1ME3B": 0xB2F2C}
# The conditioner reaches its scalar constants through the base literal of
# their constant block.
CONDITIONER_BASE_OFFSETS = {
    "request_transition_hold_reload": 0x2,
    "request_transition_word_gate_threshold": 0x6,
    "request_transition_error_correction_gain": 0x8,
    "request_transition_error_correction_limit": 0xA,
    "request_transition_reference_floor": 0x10,
}
# The rotational-speed request limiter reads its oil-temperature threshold
# curve and the shared oil-thermistor code axis through its literal pool.
LIMITER_TABLE_ROLES = {"speed_limiter_state_threshold_curve"}
LIMITER_AXIS_ROLES = {"oil_thermistor_code_axis"}
LIMITER = {"JK78C": 0x94D6C, "1ND0A": 0xA8F02, "1ND3B": 0xA8F02, "1ME3B": 0xAFE8C}
LIMITER_SITES = {
    "JK78C": (0x95054, 0x95058),
    "1ND0A": (0xA91DC, 0xA91D4),
    "1ND3B": (0xA91DC, 0xA91D4),
    "1ME3B": (0xB0064, 0xB006C),
}
# On JK78C the fuel-cut state machine and the two-stage limit builder also
# load the axis through their own literal pools.
LIMITER_AXIS_OTHER_BINDINGS = {"JK78C": {(0x6B074, 0x6AEB8, 0), (0x925DC, 0x9248A, 0)}}
# The float ignition model: the producer tree and its consumer read every
# role through literal-pool words. JK78C reads twelve roles through a base
# literal that the reader displaces; 1ND and 1ME3B load every role directly.
FLOAT_MODEL_TABLE_ROLES = {
    "timing_float_absolute_response_curve",
    "timing_float_affine_base_surface",
    "timing_float_affine_factor_curve",
    "timing_float_affine_gain_surface",
    "timing_float_attenuation_factor_a",
    "timing_float_attenuation_factor_b",
    "timing_float_base_coefficient_curve",
    "timing_float_bounded_ratio_curve",
    "timing_float_branch_multiplier_curve",
    "timing_float_conditional_multiplier_curve",
    "timing_float_denominator_gain_curve",
    "timing_float_difference_product_auxiliary_factor",
    "timing_float_difference_product_factor_curve",
    "timing_float_difference_product_word_factor",
    "timing_float_input_weight_curve",
    "timing_float_low_branch_response_curve",
    "timing_float_multi_product_auxiliary_factor",
    "timing_float_multi_product_coordinate_a_curve",
    "timing_float_multi_product_coordinate_b_curve",
    "timing_float_multi_product_difference_curve",
    "timing_float_multi_product_word_factor",
    "timing_float_normalized_multiplier_curve",
    "timing_float_product_coefficient_curve",
    "timing_float_product_factor_curve",
    "timing_float_ratio_numerator_curve",
    "timing_float_ratio_output_curve",
    "timing_float_ratio_parameter_surface",
    "timing_float_ratio_response_surface",
    "timing_float_scale_coefficient_curve",
}
FLOAT_MODEL_AXIS_ROLES = {
    "timing_float_absolute_response_axis",
    "timing_float_affine_factor_axis",
    "timing_float_affine_pair_axis_x",
    "timing_float_affine_pair_axis_y",
    "timing_float_attenuation_axis_a",
    "timing_float_attenuation_axis_b",
    "timing_float_auxiliary_input_axis",
    "timing_float_base_coefficient_axis",
    "timing_float_bounded_ratio_axis",
    "timing_float_branch_coefficient_axis",
    "timing_float_conditional_multiplier_axis",
    "timing_float_denominator_gain_axis",
    "timing_float_difference_product_factor_axis",
    "timing_float_difference_product_word_axis",
    "timing_float_input_weight_axis",
    "timing_float_low_branch_axis",
    "timing_float_multi_product_coordinate_a_axis",
    "timing_float_multi_product_coordinate_b_axis",
    "timing_float_multi_product_difference_axis",
    "timing_float_multi_product_word_factor_axis",
    "timing_float_normalized_multiplier_axis",
    "timing_float_product_coefficient_axis",
    "timing_float_product_factor_axis",
    "timing_float_ratio_output_axis",
    "timing_float_ratio_parameter_axis_x",
    "timing_float_ratio_parameter_axis_y",
    "timing_float_ratio_response_axis_x",
    "timing_float_ratio_response_axis_y",
}
FLOAT_MODEL_ROLES = FLOAT_MODEL_TABLE_ROLES | FLOAT_MODEL_AXIS_ROLES
# The reader entries of each layout; the target trees inline seven JK78C readers.
FLOAT_MODEL_READERS = {
    "JK78C": {
        0x57D88, 0x57E46, 0x5803E, 0x580F2, 0x58286, 0x584BC, 0x5860C, 0x589E8, 0x58AE8,
        0x58EBA, 0x58F6A, 0x58F94, 0x59110, 0x59204, 0x593E8, 0x59498, 0x59620, 0x596D8,
        0x5974A, 0x5995C,
    },
    "1ND0A": {
        0x60756, 0x61076, 0x61120, 0x612FE, 0x613EC, 0x61550, 0x6181A, 0x61B28, 0x61EA6,
        0x61F3A, 0x62020, 0x62194, 0x622B0, 0x62390, 0x62576,
    },
    "1ME3B": {
        0x6452E, 0x64E62, 0x64F0C, 0x650EA, 0x651D8, 0x6533C, 0x6560A, 0x65918, 0x65C96,
        0x65D2A, 0x65E10, 0x65F84, 0x660A0, 0x66180, 0x66366,
    },
}
FLOAT_MODEL_READERS["1ND3B"] = FLOAT_MODEL_READERS["1ND0A"]
# JK78C role -> (base literal word, displacement).
FLOAT_MODEL_BASE_LITERALS = {
    "timing_float_attenuation_axis_b": (0x59598, 16),
    "timing_float_attenuation_factor_a": (0x5930C, 128),
    "timing_float_attenuation_factor_b": (0x5930C, 144),
    "timing_float_denominator_gain_axis": (0x59018, 484),
    "timing_float_difference_product_auxiliary_factor": (0x598D8, 128),
    "timing_float_difference_product_word_factor": (0x598D8, 64),
    "timing_float_multi_product_auxiliary_factor": (0x59B00, 160),
    "timing_float_multi_product_coordinate_a_curve": (0x59B00, 96),
    "timing_float_multi_product_coordinate_b_curve": (0x59B00, 32),
    "timing_float_multi_product_word_factor": (0x59B00, 64),
    "timing_float_product_factor_curve": (0x5930C, 64),
    "timing_float_ratio_numerator_curve": (0x59018, 176),
}
ROLES = (
    SELECTOR_ROLES
    | FUEL_TABLE_ROLES
    | FUEL_AXIS_ROLES
    | VVEL_TABLE_ROLES
    | VVEL_AXIS_ROLES
    | IGNITION_TABLE_ROLES
    | IGNITION_STATE_AXIS_ROLES
    | CVTC_TABLE_ROLES
    | CVTC_AXIS_ROLES
    | INJECTION_TABLE_ROLES
    | INJECTION_AXIS_ROLES
    | CONDITIONER_TABLE_ROLES
    | CONDITIONER_AXIS_ROLES
    | LIMITER_TABLE_ROLES
    | LIMITER_AXIS_ROLES
    | FLOAT_MODEL_ROLES
)
# The stepped approach to the throttled duration and the start-up blend target
# exist only in the 1ME3B resolver.
ONE_ME3B_ONLY_ROLES = {
    "vvel_duration_throttled_ramp_delay",
    "vvel_duration_throttled_ramp_delay_axis",
    "vvel_duration_startup_blend",
    "vvel_duration_startup_blend_axis",
}
# The 1ND state-code dispatcher reads the resolver surfaces in place of a
# separate hot-intake idle pair.
STATE_WORD_PAIR_ROLES = {
    "vvel_duration_model_hot_intake_idle",
    "vvel_duration_model_hot_intake_idle_knock",
    "vvel_duration_model_hot_intake_idle_axis_x",
    "vvel_duration_model_hot_intake_idle_axis_y",
}
ABSENT = {
    "JK78C": {"vvel_duration_mode_14"} | ONE_ME3B_ONLY_ROLES | IGNITION_STATE_ROLES,
    "1ND0A": {
        "vvel_duration_hot_intake_idle_floor",
        "vvel_duration_hot_intake_idle_knock_floor",
        "vvel_duration_hot_intake_idle_floor_axis",
    } | STATE_WORD_PAIR_ROLES | ONE_ME3B_ONLY_ROLES,
    "1ME3B": {"vvel_duration_mode_14"},
}
ABSENT["1ND3B"] = ABSENT["1ND0A"]


def _projected_axes(target):
    """Stub the canonical axes that the projection supplies before the registry runs."""
    native = {axis.address for axis in target.axes}
    return {
        f"{address:08x}": {}
        for table in target.tables
        for address in table.axis_x + table.axis_y
        if address not in native
    }


def _registry_text():
    with open(vq37_native_tables.DEFAULT_REGISTRY, encoding="utf-8") as handle:
        return handle.read()


def _edited_registry(tmp_path, old, new):
    text = _registry_text()
    assert text.count(old) == 1
    path = tmp_path / "native.toml"
    path.write_text(text.replace(old, new), encoding="utf-8")
    return path


def test_registry_requires_the_complete_vq37_target_set(tmp_path):
    path = tmp_path / "native.toml"
    path.write_text(
        "schema_version = 4\n[target.JK78C]\n",
        encoding="utf-8",
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="target set differs",
    ):
        vq37_native_tables.load_registry(path)


def test_registry_declares_every_role_on_every_target():
    registry = vq37_native_tables.load_registry()

    assert set(registry) == set(TARGETS)
    for rom in TARGETS:
        target = registry[rom]
        tables = {table.identifier for table in target.tables}
        axes = {axis.identifier for axis in target.axes}

        assert tables <= (
            SELECTOR_ROLES | FUEL_TABLE_ROLES | VVEL_TABLE_ROLES
            | IGNITION_TABLE_ROLES | CVTC_TABLE_ROLES | INJECTION_TABLE_ROLES
            | CONDITIONER_TABLE_ROLES | LIMITER_TABLE_ROLES | FLOAT_MODEL_TABLE_ROLES
        )
        assert axes <= (
            FUEL_AXIS_ROLES | VVEL_AXIS_ROLES | IGNITION_STATE_AXIS_ROLES
            | CVTC_AXIS_ROLES | INJECTION_AXIS_ROLES | CONDITIONER_AXIS_ROLES
            | LIMITER_AXIS_ROLES | FLOAT_MODEL_AXIS_ROLES
        )
        assert set(target.absent) == ABSENT[rom]
        assert tables | axes | set(target.absent) == ROLES
        for reason in target.absent.values():
            assert reason.strip()


def test_registry_binds_exact_stock_values_and_accessor_literals():
    registry = vq37_native_tables.load_registry()

    for rom in TARGETS:
        target = registry[rom]
        image = romkit.load(rom)

        assert hashlib.sha256(image.data).hexdigest() == target.stock_sha256
        entities = [
            (table.address, table.width * table.height, table.storagetype,
             table.values_sha256, table.pointer_bindings)
            for table in target.tables
        ] + [
            (axis.address, axis.length, axis.storagetype,
             axis.values_sha256, axis.pointer_bindings)
            for axis in target.axes
        ]
        for address, length, storagetype, values_sha256, bindings in entities:
            element = romkit.ELEM[storagetype]
            block = image.data[address : address + length * element]

            assert hashlib.sha256(block).hexdigest() == values_sha256
            assert bindings
            for pointer in bindings:
                stored = int.from_bytes(
                    image.data[pointer.site : pointer.site + 4], "big"
                )

                assert stored + pointer.offset == address
                assert pointer.accessor < pointer.site


def test_registry_shares_the_1nd_layout_between_1nd0a_and_1nd3b():
    registry = vq37_native_tables.load_registry()
    layouts = {}
    for rom in ("1ND0A", "1ND3B"):
        target = registry[rom]
        layouts[rom] = (
            {(t.identifier, t.address, t.pointer_bindings) for t in target.tables},
            {(a.identifier, a.address, a.pointer_bindings) for a in target.axes},
        )

    assert layouts["1ND0A"] == layouts["1ND3B"]
    assert registry["1ND0A"].stock_sha256 != registry["1ND3B"].stock_sha256


def test_registry_displaces_only_the_1me3b_conditioner_constants():
    registry = vq37_native_tables.load_registry()
    target = registry["1ME3B"]
    reference = registry["JK78C"]

    identifiers = {e.identifier for e in (*target.tables, *target.axes)}
    assert identifiers == {
        e.identifier for e in (*reference.tables, *reference.axes)
    } | ONE_ME3B_ONLY_ROLES | IGNITION_STATE_ROLES
    assert {
        entity.identifier: pointer.offset
        for entity in (*target.tables, *target.axes)
        for pointer in entity.pointer_bindings
        if pointer.offset
    } == CONDITIONER_BASE_OFFSETS
    floors = {
        t.identifier: t
        for t in target.tables
        if t.identifier.startswith("vvel_duration_hot_intake_idle")
        and t.identifier.endswith("_floor")
    }
    assert {t.address for t in floors.values()} == {0x165DC, 0x165EC}
    assert all(t.axis_x == (0x165CC,) for t in floors.values())


def test_registry_publishes_the_conditioner_calibration_through_its_pool():
    gears = tuple(range(8))
    for rom, target in vq37_native_tables.load_registry().items():
        tables = {t.identifier: t for t in target.tables
                  if t.identifier in CONDITIONER_TABLE_ROLES}
        axes = {a.identifier: a for a in target.axes
                if a.identifier in CONDITIONER_AXIS_ROLES}

        assert set(tables) == CONDITIONER_TABLE_ROLES, rom
        assert set(axes) == CONDITIONER_AXIS_ROLES, rom
        for entity in (*tables.values(), *axes.values()):
            assert {p.accessor for p in entity.pointer_bindings} == {CONDITIONER[rom]}
            assert entity.scale_conf is None
        # Gear-index coordinates select the grid points of both 8x8 surfaces.
        for role in ("request_transition_duration_table",
                     "request_transition_offset_surface"):
            table = tables[role]
            assert (table.width, table.height) == (8, 8)
            assert (table.static_axis_x_name, table.static_axis_x) == (
                "Current Gear Index", gears)
            assert (table.static_axis_y_name, table.static_axis_y) == (
                "Target Gear Index", gears)
        rates = {role: t for role, t in tables.items() if "_rate_" in role}
        assert {(t.axis_x, t.axis_y) for t in rates.values()} == {(
            (axes["request_transition_rate_coordinate_axis"].address,),
            (axes["request_transition_rate_state_axis"].address,),
        )}
        # Only the gate thresholds may hold all one bits: 0xFF and 0xFFFF on
        # JK78C and 1ND3B keep both hysteretic gates clear.
        assert {role for role, t in tables.items() if t.constant_content} == {
            "request_transition_input_byte_threshold",
            "request_transition_word_gate_threshold",
        }


def test_registry_publishes_the_limiter_threshold_curve_through_its_pool():
    for rom, target in vq37_native_tables.load_registry().items():
        tables = {t.identifier: t for t in target.tables
                  if t.identifier in LIMITER_TABLE_ROLES}
        axes = {a.identifier: a for a in target.axes
                if a.identifier in LIMITER_AXIS_ROLES}

        assert set(tables) == LIMITER_TABLE_ROLES, rom
        assert set(axes) == LIMITER_AXIS_ROLES, rom
        curve = tables["speed_limiter_state_threshold_curve"]
        axis = axes["oil_thermistor_code_axis"]
        curve_site, axis_site = LIMITER_SITES[rom]
        assert {(p.site, p.accessor, p.offset) for p in curve.pointer_bindings} == {
            (curve_site, LIMITER[rom], 0)}
        assert {(p.site, p.accessor, p.offset) for p in axis.pointer_bindings} == {
            (axis_site, LIMITER[rom], 0)} | LIMITER_AXIS_OTHER_BINDINGS.get(rom, set())
        assert (curve.width, curve.height, curve.axis_x) == (8, 1, (axis.address,))
        # The curve lowers the base threshold, whose RPM scale it takes as a
        # candidate; the axis shows stored oil-thermistor codes.
        assert (curve.units, curve.scale_expr, curve.scale_conf) == (
            "RPM", "x*0.78125", "candidate")
        assert axis.scale_conf is None


def test_registry_publishes_the_float_model_through_its_pools():
    for rom, target in vq37_native_tables.load_registry().items():
        tables = {t.identifier: t for t in target.tables
                  if t.identifier in FLOAT_MODEL_TABLE_ROLES}
        axes = {a.identifier: a for a in target.axes
                if a.identifier in FLOAT_MODEL_AXIS_ROLES}

        assert set(tables) == FLOAT_MODEL_TABLE_ROLES, rom
        assert set(axes) == FLOAT_MODEL_AXIS_ROLES, rom
        displaced = {}
        for name, entity in {**tables, **axes}.items():
            assert {p.accessor for p in entity.pointer_bindings} <= FLOAT_MODEL_READERS[rom]
            displaced.update({name: (p.site, p.offset)
                              for p in entity.pointer_bindings if p.offset})
        assert displaced == (FLOAT_MODEL_BASE_LITERALS if rom == "JK78C" else {}), rom
        assert sorted(t.order for t in tables.values()) == list(range(3100, 3129))
        assert {t.category for t in tables.values()} == {
            "Ignition / Timing Model Corrections"}
        # The difference-product factor holds one stored value in every cell.
        curve = tables["timing_float_difference_product_factor_curve"]
        data = romkit.load(rom).data[curve.address : curve.address + 2 * curve.width]
        assert curve.height == 1
        assert {int.from_bytes(data[i : i + 2], "big") for i in range(0, len(data), 2)} == {
            21739}


def test_registry_rejects_a_missing_role_declaration(tmp_path):
    path = _edited_registry(
        tmp_path,
        '\nvvel_duration_mode_14 = "The JK78C resolver',
        '\nvvel_duration_mode_14_removed = "The JK78C resolver',
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="roles differ; missing=\\['vvel_duration_mode_14'\\]",
    ):
        vq37_native_tables.load_registry(path)


def test_registry_rejects_an_absent_role_that_is_present(tmp_path):
    path = _edited_registry(
        tmp_path,
        "[target.JK78C.absent]\n",
        "[target.JK78C.absent]\nvvel_duration_running = \"stated\"\n",
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="absent roles are present",
    ):
        vq37_native_tables.load_registry(path)


def test_registry_rejects_a_curve_with_a_second_axis(tmp_path):
    path = _edited_registry(
        tmp_path,
        "axis_x = 0x00016CA4\nname = \"VVEL Duration Target - Running\"",
        "axis_x = 0x00016CA4\naxis_y = 0x00016C84\n"
        "name = \"VVEL Duration Target - Running\"",
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="one-dimensional table declares axis_y",
    ):
        vq37_native_tables.load_registry(path)


def test_registry_rejects_a_negative_pointer_offset(tmp_path):
    path = _edited_registry(
        tmp_path,
        "{ site = 0x00056678, accessor = 0x000564A4, offset = 0x10 }",
        "{ site = 0x00056678, accessor = 0x000564A4, offset = -16 }",
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="offset is invalid",
    ):
        vq37_native_tables.load_registry(path)


def test_registry_masks_only_the_ignition_timing_field():
    for rom, target in vq37_native_tables.load_registry().items():
        for table in target.tables:
            expected = "7F" if table.identifier in IGNITION_TABLE_ROLES else ""
            assert table.mask == expected, (rom, table.identifier)


@pytest.mark.parametrize(
    ("mask", "message"),
    [
        ("7G", "is not a hexadecimal string"),
        ("00", "is not a contiguous partial bit field of uint8"),
        ("FF", "is not a contiguous partial bit field of uint8"),
        ("5A", "is not a contiguous partial bit field of uint8"),
    ],
)
def test_registry_rejects_an_invalid_table_mask(tmp_path, mask, message):
    path = _edited_registry(
        tmp_path,
        'mask = "7F"\nname = "Ignition Timing Surface - Hot Coolant"',
        f'mask = "{mask}"\nname = "Ignition Timing Surface - Hot Coolant"',
    )

    with pytest.raises(vq37_native_tables.NativeTableError, match=message):
        vq37_native_tables.load_registry(path)


def _table_row(width, height, **labels):
    """A complete registry table row of the given geometry and axis keys."""
    return {
        "id": "static_axis_probe", "address": 0x9000, "width": width,
        "height": height, "storagetype": "uint8", "values_sha256": "0" * 64,
        "pointer_bindings": [{"site": 0x96F64, "accessor": 0x96CE0}],
        "name": "Static Axis Probe", "category": "Probe", "order": 1,
        "format": "0", "fine": 1, "coarse": 10, "confidence": "code",
        "semantics": "Probe semantics.", "note": "Probe note.", **labels,
    }


def test_registry_labels_a_2d_table_without_graph_axes_by_static_axes():
    table = vq37_native_tables._parse_table(_table_row(
        2, 3,
        static_axis_x_name="Column", static_axis_x=[0, 1],
        static_axis_y_name="Row", static_axis_y=["low", "middle", "high"],
    ), "probe")
    presentation = vq37_native_tables._presentation(table)

    assert (table.static_axis_x, table.static_axis_y) == ((0, 1), ("low", "middle", "high"))
    assert {key: presentation[key] for key in (
        "static_axis_x_name", "static_axis_x", "static_axis_y_name", "static_axis_y"
    )} == {
        "static_axis_x_name": "Column", "static_axis_x": [0, 1],
        "static_axis_y_name": "Row", "static_axis_y": ["low", "middle", "high"],
    }
    assert "static_axis" not in presentation
    model = vq37_native_tables._model(table, "Probe note.")
    assert emit_def.definition_failure(model, {}, presentation) is None
    xml = "\n".join(emit_def.table_axes_xml(model, presentation, {}, {}))
    assert 'type="Static X Axis" name="Column" sizex="2"' in xml
    assert 'type="Static Y Axis" name="Row" sizey="3"' in xml


def test_registry_labels_a_scalar_by_one_text_label():
    table = vq37_native_tables._parse_table(
        _table_row(1, 1, static_axis_name="Threshold", static_axis=["byte gate"]),
        "probe",
    )

    assert vq37_native_tables._presentation(table)["static_axis"] == ["byte gate"]


@pytest.mark.parametrize(
    ("width", "height", "labels", "message"),
    [
        (2, 2, {}, "no axis is declared"),
        (2, 2, {"static_axis_x_name": "X", "static_axis_x": [0, 1]},
         "static axis pair is incomplete"),
        (2, 2, {"static_axis_name": "X", "static_axis": [0, 1]},
         "two-dimensional table declares static_axis"),
        (2, 1, {"static_axis_x_name": "X", "static_axis_x": [0, 1]},
         "one-dimensional table declares static_axis_x"),
        (2, 2, {"static_axis_x": [0, 1], "static_axis_y_name": "Y",
                "static_axis_y": [0, 1]}, "static_axis_x declaration is incomplete"),
        (2, 2, {"static_axis_x_name": "X", "static_axis_x": [0, 1, 2],
                "static_axis_y_name": "Y", "static_axis_y": [0, 1]},
         "expected 2 integers or 2 labels"),
        (2, 2, {"static_axis_x_name": "X", "static_axis_x": [0, "one"],
                "static_axis_y_name": "Y", "static_axis_y": [0, 1]},
         "expected 2 integers or 2 labels"),
        (2, 2, {"static_axis_x_name": "X", "static_axis_x": [0, 1],
                "static_axis_y_name": "Y", "static_axis_y": [1, 0]},
         "static_axis_y is not monotone"),
        (2, 2, {"axis_x": 0x13000, "axis_y": 0x13010, "static_axis_x_name": "X",
                "static_axis_x": [0, 1], "static_axis_y_name": "Y",
                "static_axis_y": [0, 1]}, "static axis overlaps a graph axis"),
    ],
)
def test_registry_rejects_an_invalid_static_axis(width, height, labels, message):
    with pytest.raises(vq37_native_tables.NativeTableError, match=message):
        vq37_native_tables._parse_table(_table_row(width, height, **labels), "probe")


def test_registry_accepts_an_all_ones_block_only_as_reviewed_constant_content():
    # The stock JK78C input byte gate threshold holds 0xFF.
    image = romkit.load("JK78C")
    digest = hashlib.sha256(image.data[0x8935:0x8936]).hexdigest()
    arguments = ("JK78C", image, "00008935", 0x8935, 1, "uint8", digest)

    with pytest.raises(vq37_native_tables.NativeTableError, match="00008935 is erased"):
        vq37_native_tables._verify_block(*arguments)
    assert list(vq37_native_tables._verify_block(*arguments, True)) == [0xFF]


def test_registry_reads_constant_content_as_a_true_flag():
    row = _table_row(1, 1, static_axis_name="Constant", static_axis=["probe"])
    assert vq37_native_tables._parse_table(row, "probe").constant_content is False
    marked = vq37_native_tables._parse_table({**row, "constant_content": True}, "probe")
    assert marked.constant_content is True

    with pytest.raises(
        vq37_native_tables.NativeTableError, match="constant_content must be true"
    ):
        vq37_native_tables._parse_table({**row, "constant_content": False}, "probe")


def test_apply_target_publishes_every_registered_table_and_axis():
    for rom in TARGETS:
        target = vq37_native_tables.load_registry()[rom]
        image = romkit.load(rom)
        projected = _projected_axes(target)
        maps, axes, overrides = vq37_native_tables.apply_target(
            rom, {}, projected, {"table": {}}, image
        )
        table_keys = {f"{table.address:08x}" for table in target.tables}
        axis_keys = {f"{axis.address:08x}" for axis in target.axes}

        assert set(maps) == table_keys
        assert set(overrides["table"]) == table_keys
        assert set(axes) == axis_keys | set(projected)
        assert set(overrides["axis"]) == axis_keys
        for table in target.tables:
            key = f"{table.address:08x}"
            model = maps[key]

            assert model["width"] == table.width
            assert model["dims"] == (2 if table.height > 1 else 1)
            assert model["storagetype"] == table.storagetype
            assert model["confidence"] == table.confidence
            assert model["scale_conf"] == table.scale_conf
            assert model["note"].startswith(
                f"Exact {rom} target-native table at {table.address:#x}"
            )
            expected_name = table.name if table.scale_conf in {"code", "candidate"} else table.name + " [stored count]"
            assert overrides["table"][key]["name"] == expected_name
            assert overrides["table"][key]["emit"] is True
            assert overrides["table"][key].get("mask", "") == table.mask
            assert model["accessors"] == sorted({
                f"{pointer.accessor:08x}"
                for pointer in table.pointer_bindings
            })
            for axis_key in model["axis_x"] + model["axis_y"]:
                assert axis_key in axes
        for axis in target.axes:
            key = f"{axis.address:08x}"
            model = axes[key]

            assert model["kind"] == axis.kind
            assert model["len"] == axis.length
            assert len(model["values"]) == axis.length
            assert model["values"] == sorted(model["values"])
            assert model["confidence"] == axis.confidence
            established_view = axis.scale_conf in {"code", "candidate"}
            assert model["scale_expr"] == (axis.scale_expr if established_view else "x")
            assert model["scale_evidence"] == ("registry:target-native" if established_view else "")
            assert model["note"].startswith(
                f"Exact {rom} target-native axis at {axis.address:#x}"
            )
            expected = {
                "name": axis.name,
                "format": axis.format,
                "fine": axis.fine,
                "coarse": axis.coarse,
            }
            if not established_view:
                expected = {"name": axis.name.split(" [")[0] + " [stored count]",
                            "format": "0", "fine": 1, "coarse": 10}
            assert overrides["axis"][key] == expected


def test_apply_target_describes_a_displaced_base_literal():
    rom = "JK78C"
    target = vq37_native_tables.load_registry()[rom]
    image = romkit.load(rom)
    maps, axes, _overrides = vq37_native_tables.apply_target(
        rom, {}, _projected_axes(target), {"table": {}}, image
    )
    floor = maps["0001600a"]
    rpm_axis = axes["000160ca"]

    assert floor["axis_x"] == ["00015ffa"]
    assert "through literal 0x56678 + 0x10" in floor["note"]
    assert "through literal 0x56678 + 0xd0" in rpm_axis["note"]
    assert rpm_axis["values"] == [128, 192, 256, 320, 384, 448, 512, 640]


# The base curve, the conditional curve, their axis and the writer of each
# target; 1ND3B shares the 1ND0A layout.
END_OF_INJECTION = {
    "JK78C": (0x15F22, 0x15F42, 0x15F32, 0x730CC),
    "1ND0A": (0x16540, 0x16560, 0x16550, 0x7F4E0),
    "1ND3B": (0x16540, 0x16560, 0x16550, 0x7F4E0),
    "1ME3B": (0x164E4, 0x16504, 0x164F4, 0x841B4),
}
# The stock cell words of the base and the conditional curve, the same on
# every target.
END_OF_INJECTION_CELLS = (
    [133] * 8,
    [175, 133, 133, 155, 155, 150, 140, 138],
)


@pytest.mark.parametrize("rom", sorted(END_OF_INJECTION))
def test_apply_target_publishes_the_end_of_injection_word_curves(rom):
    base, conditional, axis, writer = END_OF_INJECTION[rom]
    target = vq37_native_tables.load_registry()[rom]
    image = romkit.load(rom)
    maps, axes, overrides = vq37_native_tables.apply_target(
        rom, {}, _projected_axes(target), {"table": {}}, image
    )

    def words(start):
        return [
            int.from_bytes(image.data[address : address + 2], "big")
            for address in range(start, start + 16, 2)
        ]

    for address, cells in zip((base, conditional), END_OF_INJECTION_CELLS):
        key = f"{address:08x}"
        model = maps[key]

        assert (model["storagetype"], model["width"], model["dims"]) == ("uint16", 8, 1)
        assert model["axis_x"] == [f"{axis:08x}"]
        assert model["accessors"] == [f"{writer:08x}"]
        assert model["scale_expr"] == "x*4-590"
        assert overrides["table"][key]["category"] == "Fuelling / Injection"
        assert words(int(model["addr"], 16)) == cells
    assert axes[f"{axis:08x}"]["values"] == words(axis)
    assert axes[f"{axis:08x}"]["scale_expr"] == "x*12.5"


def test_apply_target_rejects_a_byte_projection_of_an_end_of_injection_curve():
    # An address-only relocation of the JK08A byte curve 00012302 would place
    # a byte table on the word curve of the native registry.
    rom = "JK78C"
    target = vq37_native_tables.load_registry()[rom]
    image = romkit.load(rom)
    occupied = {"00015f22": {"storagetype": "uint8", "width": 8, "dims": 1}}

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="native table 00015f22 collides with the projection",
    ):
        vq37_native_tables.apply_target(
            rom, occupied, _projected_axes(target), {"table": {}}, image
        )


def test_apply_target_rejects_an_unprojected_axis():
    rom = "JK78C"
    image = romkit.load(rom)

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="unprojected axis",
    ):
        vq37_native_tables.apply_target(rom, {}, {}, {"table": {}}, image)


def test_apply_target_rejects_a_projection_collision():
    rom = "JK78C"
    target = vq37_native_tables.load_registry()[rom]
    image = romkit.load(rom)
    occupied = {f"{target.tables[0].address:08x}": {}}

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="collides with the projection",
    ):
        vq37_native_tables.apply_target(
            rom, occupied, _projected_axes(target), {"table": {}}, image
        )


def test_apply_target_rejects_a_repeated_table_name():
    rom = "JK78C"
    target = vq37_native_tables.load_registry()[rom]
    image = romkit.load(rom)
    name = target.tables[0].name
    if target.tables[0].scale_conf not in {"code", "candidate"}:
        name += " [stored count]"
    projected = {"table": {"0000ffff": {"name": name}}}

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="repeats the table name",
    ):
        vq37_native_tables.apply_target(
            rom, {}, _projected_axes(target), projected, image
        )


def test_apply_target_rejects_a_native_axis_collision():
    rom = "JK78C"
    target = vq37_native_tables.load_registry()[rom]
    image = romkit.load(rom)
    axes = _projected_axes(target)
    axes[f"{target.axes[0].address:08x}"] = {}

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="native axis .* collides with the projection",
    ):
        vq37_native_tables.apply_target(rom, {}, axes, {"table": {}}, image)


def test_apply_target_rejects_a_displaced_pointer_that_misses():
    rom = "JK78C"
    image = romkit.load(rom)
    binding = vq37_native_tables.PointerBinding(
        site=0x56678, accessor=0x564A4, offset=0x12
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="pointer at 0x56678 is 0x15ffa \\+ 0x12, expected 0x1600a",
    ):
        vq37_native_tables._verify_bindings(rom, image, 0x1600A, [binding])


def test_apply_target_rejects_a_foreign_image():
    target = vq37_native_tables.load_registry()["JK78C"]

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="native table target is JK78C",
    ):
        vq37_native_tables.apply_target(
            "JK78C", {}, _projected_axes(target), {"table": {}},
            romkit.load("1ND0A"),
        )


def test_apply_target_ignores_a_rom_without_native_tables():
    maps, axes, overrides = vq37_native_tables.apply_target(
        "JK08A", {}, {}, {"table": {}}, romkit.load("JK08A")
    )

    assert maps == {}
    assert axes == {}
    assert overrides == {"table": {}}
