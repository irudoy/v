from dataclasses import replace

import pytest

from patches import can_telemetry_profile
from tools.diagnostics import sid22_inventory
from tools.diagnostics import tuning_signal_coverage


def test_catalog_covers_every_current_tuning_field():
    catalog = tuning_signal_coverage.load_catalog()
    owners = {
        field: signal.signal_id
        for signal in catalog.signals
        for field in signal.current_fields
    }
    assert owners["request_flow_raw"] == "requested_torque_column"
    assert owners["alpha_n_flow_raw"] == "fuel_compensation_column"
    assert owners["normalized_load_raw"] == "normalized_load"
    assert owners["intake_cvtc_target_raw"] == "common_cvtc_targets"
    assert owners["exhaust_cvtc_target_raw"] == "common_cvtc_targets"
    assert owners["knock_count_latched"] == "knock_event_latches"


def test_catalog_separates_stream_coverage_from_external_measurement():
    catalog = tuning_signal_coverage.load_catalog()
    assert catalog.by_id["pressure_context"].coverage == "absent"
    assert catalog.by_id["front_heated_oxygen_sensors"].coverage == "absent"
    assert catalog.by_id["throttle_request_path"].coverage == "fixed"
    assert catalog.by_id["commanded_mixture"].coverage == "rotating"
    assert catalog.by_id["knock_margin"].coverage == "rotating"
    assert catalog.by_id["knock_margin"].current_fields == tuple(
        f"knock_margin_min_ch{channel}_raw" for channel in range(1, 7)
    )
    assert catalog.by_id["physical_spark_angle"].coverage == "external"


def test_catalog_signals_outside_the_stream_share_no_source_with_it():
    catalog = tuning_signal_coverage.load_catalog()
    manifest = can_telemetry_profile.load_manifest()
    streamed = {field.source for field in manifest.fields} | {
        field.source for context in manifest.contexts for field in context.fields
    }
    for signal_id, coverage in (
        ("engine_speed", "stock-can"),
        ("ignition_control_state", "absent"),
    ):
        signal = catalog.by_id[signal_id]
        assert signal.coverage == coverage
        assert signal.current_fields == ()
        assert streamed.isdisjoint(signal.sources)


def test_catalog_did_bindings_include_high_value_gaps():
    catalog = tuning_signal_coverage.load_catalog()
    assert catalog.by_id["front_af_sensor_words"].dids == (0x1225, 0x1226)
    assert catalog.by_id["exhaust_cvtc_actual"].dids == (0x1164, 0x1165)
    assert catalog.by_id["high_resolution_cvtc_duty"].dids == (
        0x122D,
        0x122E,
        0x122F,
        0x1230,
    )


def test_summary_has_stable_coverage_counts():
    report = tuning_signal_coverage.summary(tuning_signal_coverage.load_catalog())
    assert report["signal_count"] == 41
    assert report["rotating_rate_hz"] == 19.53125
    assert report["coverage"] == {
        "absent": 5,
        "external": 1,
        "fixed": 19,
        "latched": 1,
        "rotating": 13,
        "stock-can": 2,
    }


def test_did_validation_requires_the_complete_sequential_source_width():
    catalog = tuning_signal_coverage.load_catalog()
    signal = replace(
        catalog.by_id["engine_speed"],
        sources=(0xFFFF11F4,),
        widths=(1,),
    )
    narrowed = replace(catalog, signals=(signal,))
    inventory = (
        next(
            entry
            for entry in sid22_inventory.read_inventory()
            if entry.did == 0x1201
        ),
    )

    with pytest.raises(ValueError, match="sources lie outside"):
        tuning_signal_coverage._validate_dids(narrowed, inventory)


def test_did_validation_requires_every_paired_source():
    catalog = tuning_signal_coverage.load_catalog()
    signal = replace(
        catalog.by_id["engine_speed"],
        sources=(0xFFFF3342,),
        widths=(1,),
        dids=(0x1302,),
    )
    paired = replace(catalog, signals=(signal,))
    inventory = (
        next(
            entry
            for entry in sid22_inventory.read_inventory()
            if entry.did == 0x1302
        ),
    )

    with pytest.raises(ValueError, match="sources lie outside"):
        tuning_signal_coverage._validate_dids(paired, inventory)
