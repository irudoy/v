from dataclasses import replace

import pytest

from tools.diagnostics import sid22_inventory
from tools.diagnostics import tuning_signal_coverage


def test_catalog_covers_every_current_tuning_field():
    catalog = tuning_signal_coverage.load_catalog()
    owners = {
        field: signal.signal_id
        for signal in catalog.signals
        for field in signal.current_fields
    }
    assert owners["rpm_raw"] == "engine_speed"
    assert owners["front_oxygen_sensor_b1_raw"] == "front_heated_oxygen_sensors"
    assert owners["intake_cvtc_target_raw"] == "common_cvtc_targets"
    assert owners["exhaust_cvtc_target_raw"] == "common_cvtc_targets"
    assert owners["knock_count_latched"] == "knock_event_latches"


def test_catalog_separates_current_coverage_from_instrumentation():
    catalog = tuning_signal_coverage.load_catalog()
    assert catalog.by_id["pressure_context"].coverage == "rotating"
    assert catalog.by_id["throttle_request_path"].coverage == "fixed"
    assert catalog.by_id["commanded_mixture"].coverage == "unresolved"
    assert catalog.by_id["knock_margin"].coverage == "instrumentation"
    assert catalog.by_id["physical_spark_angle"].coverage == "external"


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
    assert report["signal_count"] == 36
    assert report["coverage"] == {
        "external": 1,
        "fixed": 19,
        "instrumentation": 1,
        "latched": 1,
        "rotating": 11,
        "stock-can": 1,
        "unresolved": 2,
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
