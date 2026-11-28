"""Package 3 unit tests for relocated cruise-free map switching and EEPROM."""

from __future__ import annotations

from dataclasses import replace

import pytest

from patches import build_rom
from patches import extract_calibration
from patches import map_switching_assembly
from patches import map_switching_cruise_free as cf_model
from patches import map_switching_eeprom as ee_model
from patches import rom_address_profiles
from patches import runtime_targets


EXPECTED_P3_MATRIX = {
    "JK00C": (0x000E2800, 0x000E3000, 0x000E3900, 0x00028994, 0x0002D2B4, 0xFFFF6300, 0xFFFF6320),
    "JK00D": (0x000E2800, 0x000E3000, 0x000E3900, 0x00028994, 0x0002D2B4, 0xFFFF6300, 0xFFFF6320),
    "JK78C": (0x000FEC00, 0x000FF780, 0x000FFF80, 0x0002A6FC, 0x0002F596, 0xFFFF0F20, 0xFFFF0F40),
    "1ND0A": (0x00136000, 0x00136800, 0x00137100, 0x0002B398, 0x00030810, 0xFFFF0F60, 0xFFFF0F80),
    "1ND3B": (0x00136000, 0x00136800, 0x00137100, 0x0002B398, 0x00030810, 0xFFFF0F60, 0xFFFF0F80),
    "1ME3B": (0x0013F000, 0x0013F800, 0x00140100, 0x0002E18C, 0x0003357C, 0xFFFF0F00, 0xFFFF0F20),
    "1EK7A": (0x00166000, 0x00166800, 0x00167100, 0x0002EE94, 0x000342C0, 0xFFFF5900, 0xFFFF5920),
}


@pytest.mark.parametrize("rom", runtime_targets.RELOCATED_ROMS)
def test_package3_no_thunk_layout_and_hooks_match_matrix(rom):
    c_start, e_start, e_end, hook_addr, hook_stock, cr_start, er_start = (
        EXPECTED_P3_MATRIX[rom]
    )
    target = runtime_targets.load_runtime_target(rom)
    layout = target.map_layout
    cf = layout.cruise_free
    ee = layout.eeprom_persistence
    code = layout.code_region_by_key
    hooks = {h.key: h for h in layout.hooks}

    assert cf is not None and ee is not None
    assert cf.config.start == c_start and cf.config.end == c_start + 0x20
    assert ee.config.start == e_start and ee.config.end == e_start + 0x10
    assert cf.ram.start == cr_start and cf.ram.size == 32
    assert ee.ram.start == er_start and ee.ram.size == 64
    assert layout.ram.extension.start == cr_start
    assert layout.ram.extension.end == er_start + 64
    assert layout.claimed_rom_extensions[0].start == c_start
    assert layout.claimed_rom_extensions[0].end == c_start + 0x800
    assert layout.claimed_rom_extensions[1].start == e_start
    assert layout.claimed_rom_extensions[1].end == e_end

    # Direct startup_wrapper in C+0x5C0..C+0x620 and cruise_free_menu in C+0x620..C+0x800 (no thunk).
    sw = code["startup_wrapper"]
    assert sw.entry == c_start + 0x5C0
    assert sw.span.start == c_start + 0x5C0
    assert sw.span.end == c_start + 0x620
    menu = code["cruise_free_menu"]
    assert menu.entry == c_start + 0x620
    assert menu.span.start == c_start + 0x620
    assert menu.span.end == c_start + 0x800
    assert hooks["startup_initializer"].address == hook_addr
    assert hooks["startup_initializer"].stock == hook_stock
    assert hooks["startup_initializer"].replacement == sw.entry
    # CAN startup wrapper chains directly into the relocated startup_wrapper.
    can_startup = target.telemetry_layout.hook_by_key["startup_state_clear"]
    assert can_startup.stock == sw.entry

    assert hooks["stationary_rx_dispatch"].replacement == c_start + 0x40
    assert hooks["tach_180_serializer"].replacement == c_start + 0x4A0
    assert hooks["tach_1f9_serializer"].replacement == c_start + 0x4C0
    assert hooks["eeprom_periodic_task"].replacement == e_start + 0x1A0
    assert code["eeprom_boot_restore"].entry == e_start + 0x10


@pytest.mark.parametrize(
    ("rom", "expected_status", "expected_mil"),
    (
        ("JK00C", 0xFFFF3C16, 0xFFFF3C14),
        ("JK00D", 0xFFFF3C2A, 0xFFFF3C28),
    ),
)
def test_8mfk_feedback_uses_fixed_0x2a_payload_offset_and_preserving_mil(
    rom, expected_status, expected_mil
):
    target = runtime_targets.load_runtime_target(rom)
    fb = target.map_layout.feedback
    assert fb.payload_offset == 0x2A
    assert fb.status_byte_address == expected_status
    assert target.map_layout.cruise_free.mil_byte_address == expected_mil

    engine_src = target.map_layout.source_text_by_unit["cruise_feedback_engine"]
    assert "or 0x20,r0" in engine_src
    assert "and 0xDF,r0" not in engine_src


def test_relocated_feedback_validator_rejects_stock_clearing_mil_block():
    target = runtime_targets.load_runtime_target("JK78C")
    layout = target.map_layout
    engine_src = layout.source_text_by_unit["cruise_feedback_engine"]
    bad_src = engine_src.replace(
        "or 0x20,r0\n",
        "and 0xDF,r0\nmov #0x20,r0\n",
        1,
    )
    bad_sources = tuple(
        (key, bad_src if key == "cruise_feedback_engine" else text)
        for key, text in layout.source_texts
    )
    bad_units = tuple(
        replace(unit, instruction_count=unit.instruction_count + 1)
        if unit.key == "cruise_feedback_engine"
        else unit
        for unit in layout.assembly_units
    )
    bad_layout = replace(
        layout, source_texts=bad_sources, assembly_units=bad_units
    )
    with pytest.raises(ValueError, match="MIL mask handling differs"):
        map_switching_assembly.validate_assembly_sources(bad_layout)


def test_stock_profile_rejects_warm_pr_substituted_for_cold_pr():
    profile = rom_address_profiles.profile_for_rom("JK78C")
    stock = runtime_targets.load_runtime_target("JK78C").stock_image.data
    bad_ee = replace(
        profile.eeprom_persistence,
        startup_cold_return_pc=profile.eeprom_persistence.startup_warm_return_pc,
    )
    bad_profile = replace(profile, eeprom_persistence=bad_ee)
    with pytest.raises(
        rom_address_profiles.AddressProfileError,
        match="startup_cold_return_pc must differ",
    ):
        rom_address_profiles.validate_stock_profile(bad_profile, stock)


def test_stock_profile_rejects_unaligned_word_rpm_coarse():
    profile = rom_address_profiles.profile_for_rom("1ND0A")
    stock = runtime_targets.load_runtime_target("1ND0A").stock_image.data
    bad_symbols = tuple(
        (key, address | 1) if key == "rpm_coarse_address" else (key, address)
        for key, address in profile.map_symbols
    )
    bad_profile = replace(profile, map_symbols=bad_symbols)
    with pytest.raises(
        rom_address_profiles.AddressProfileError,
        match="not 2-byte aligned",
    ):
        rom_address_profiles.validate_stock_profile(bad_profile, stock)


@pytest.mark.parametrize("rom", ("JK00C", "JK78C", "1ND0A", "1ME3B", "1EK7A"))
def test_package3_build_and_extract_round_trips_custom_configs(rom):
    target = runtime_targets.load_runtime_target(rom)
    profile = build_rom.builtin_profile(target.family)
    custom_cf = cf_model.CruiseFreeConfig(
        flags=(
            cf_model.FLAG_CRUISE_FREE_ENABLED
            | cf_model.FLAG_TACH_ALLOWED
            | cf_model.FLAG_MIL_ENABLED
        ),
        cancel_hold_ticks=15,
        menu_timeout_ticks=400,
        debounce_ticks=3,
    )
    custom_ee = ee_model.EepromPersistenceConfig(
        flags=ee_model.EEPROM_FLAG_ENABLED,
        write_delay_ticks=120,
        wip_timeout_ticks=15,
        max_retries_per_slot=4,
    )
    custom_profile = replace(
        profile,
        map_switching=custom_cf,
        map_switching_eeprom=custom_ee,
        map_switching_explicit=True,
        map_switching_eeprom_explicit=True,
    )
    built = build_rom.build_image(
        target.stock_image.data, rom=rom, profile=custom_profile
    )
    extracted = extract_calibration.extract(built.data, rom=rom)
    assert extracted.map_switching == custom_cf
    assert extracted.map_switching_eeprom == custom_ee
