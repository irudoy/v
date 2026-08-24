from dataclasses import replace

import pytest

from patches import can_telemetry_assembly
from patches import map_switching_assembly
from patches import rolling_launch_assembly
from patches import runtime_targets
from tools.mapkit import vq37_native_fuel_cut


def test_runtime_registry_covers_all_supported_families():
    assert runtime_targets.SUPPORTED_ROMS == (
        "JK00A", "JK03A", "JK03B", "JK08A", "JK00C", "JK00D",
        "1ND0A", "1ND3B", "JK78C",
    )
    assert set(runtime_targets.load_payload_locks()) == {
        "JK00C", "JK00D", "1ND0A", "1ND3B", "JK78C"
    }
    for rom in runtime_targets.EXACT_ROMS:
        target = runtime_targets.load_runtime_target(rom)
        assert target.rom == rom
        assert target.family == runtime_targets.EXACT_FAMILY
        assert target.map_layout.variant == "single-exhaust"


@pytest.mark.parametrize("rom", runtime_targets.RELOCATED_8MFK_ROMS)
def test_relocated_8mfk_target_has_complete_projected_runtime(rom):
    target = runtime_targets.load_runtime_target(rom)
    profile = runtime_targets.rom_address_profiles.profile_for_rom(rom)

    assert target.family == runtime_targets.RELOCATED_8MFK_FAMILY
    assert target.stock_image.rom == rom
    assert target.map_layout.rom == rom
    assert target.map_layout.variant == "dual-exhaust"
    assert target.rolling_layout.variant == "relocated-8mfk"
    assert target.telemetry_layout.variant == "mailbox24-tail-chain"
    assert len(target.map_layout.families) == 13
    assert set(target.map_payloads) == {
        unit.key for unit in target.map_layout.assembly_units
    }
    assert set(target.rolling_payloads) == {
        unit.key for unit in target.rolling_layout.assembly_units
    }
    assert set(target.telemetry_payloads) == {
        unit.key for unit in target.telemetry_layout.assembly_units
    }

    odd = target.map_layout.family_by_key["exhaust_cvtc_target_odd"]
    assert odd.canonical_address == profile.map_family_by_key[
        "exhaust_cvtc_target_odd"
    ]
    assert odd.copies == profile.extra_exhaust_storage.copies
    assert odd.pointer_table == profile.extra_exhaust_storage.pointer_table
    assert target.telemetry_layout.mailbox_record_address == (
        profile.can_symbol_by_key["mailbox_record_address"]
    )


@pytest.mark.parametrize("rom", runtime_targets.RELOCATED_8MFK_ROMS)
def test_relocated_8mfk_sources_cover_alignment_and_tail_chain_variants(rom):
    target = runtime_targets.load_runtime_target(rom)
    limiter = target.map_layout.source_text_by_unit["limiter_commit"]
    completion = target.telemetry_layout.source_text_by_unit["completion"]
    fuel_tail = (
        target.map_layout.family_by_key["rev_limit_fuel_cut"]
        .canonical_address
        + 8
    )

    assert "mov #0xE,r1\nthrottle_copy_loop:\nmov.w @r5+,r2" in limiter
    assert "throttle_copy_loop:\nmov.l @r5+,r2" not in limiter
    assert f".long 0x{fuel_tail:08X}" in limiter
    assert "jmp @r0\nmov.l @r15+,r0" in completion

    map_parsed = map_switching_assembly.validate_assembly_sources(
        target.map_layout
    )
    rolling_parsed = rolling_launch_assembly.validate_assembly_sources(
        target.rolling_layout
    )
    telemetry_parsed = can_telemetry_assembly.validate_assembly_sources(
        target.telemetry_layout
    )
    assert map_switching_assembly.validate_instruction_semantics(
        target.map_layout, map_parsed, target.map_payloads
    ).instructions == 453
    assert rolling_launch_assembly.validate_instruction_semantics(
        target.rolling_layout, rolling_parsed, target.rolling_payloads
    ).instructions == 878
    assert can_telemetry_assembly.validate_instruction_semantics(
        target.telemetry_layout, telemetry_parsed, target.telemetry_payloads
    ).instructions == 617


@pytest.mark.parametrize("rom", runtime_targets.VQ37_RUNTIME_ROMS)
def test_vq37_target_has_complete_target_specific_runtime(rom):
    target = runtime_targets.load_runtime_target(rom)
    profile = runtime_targets.rom_address_profiles.profile_for_rom(rom)
    native = vq37_native_fuel_cut.load_registry()[rom]

    expected = (
        (runtime_targets.SH7059_1ND_FAMILY, "sh7059-1nd")
        if rom in runtime_targets.SH7059_1ND_ROMS
        else (runtime_targets.SH7058_JK78C_FAMILY, "sh7058-jk78")
    )
    assert (target.family, target.map_layout.variant) == expected
    assert target.rolling_layout.variant == "vq37-fuel-coordinator"
    assert target.rolling_layout.ram.state.size == 24
    assert set(target.rolling_layout.hook_by_key) == {
        "periodic_scheduler_index_0",
        "selector_arbitration",
        "startup_state_clear",
        "primary_ignition_command",
        "feedback_arbitration",
        "fuel_cut_coordinator",
    }
    assert set(target.rolling_payloads) == {
        unit.key for unit in target.rolling_layout.assembly_units
    }
    assert target.telemetry_layout.variant == "mailbox26-tail-chain"
    assert len(target.map_layout.families) == 14
    assert set(target.map_payloads) == {
        unit.key for unit in target.map_layout.assembly_units
    }
    assert set(target.telemetry_payloads) == {
        unit.key for unit in target.telemetry_layout.assembly_units
    }
    assert target.map_layout.family_by_key[
        "fuel_compensation_main_bank_2"
    ].canonical_address == profile.map_family_by_key[
        "fuel_compensation_main_bank_2"
    ]
    assert target.map_layout.family_by_key[
        "idle_ignition_timing_bank_2"
    ].adapter == "idle_ignition_bank_2_adapter"
    assert target.map_layout.family_by_key[
        "rev_limit_throttle_cut"
    ].runtime_shadow_address is None
    assert target.map_layout.family_by_key[
        "rev_limit_fuel_cut_caps"
    ].shadow_start == target.map_layout.ram.fuel_cut_shadow.start
    assert target.map_layout.family_by_key[
        "rev_limit_fuel_cut_caps"
    ].canonical_address == native.caps_address
    assert target.map_layout.family_by_key[
        "rev_limit_fuel_cut_curves"
    ].shadow_start == (
        target.map_layout.ram.fuel_cut_shadow.start + 4
    )
    assert target.map_layout.family_by_key[
        "rev_limit_fuel_cut_curves"
    ].canonical_address == native.curves_address
    coordinator = target.rolling_layout.hook_by_key[
        "fuel_cut_coordinator"
    ]
    assert coordinator.address == native.coordinator_pointer_site
    assert coordinator.stock == native.coordinator_address
    assert target.map_layout.ram.fuel_cut_shadow.size == 36
    assert target.rolling_layout.ram.fuel_shadow.size == 36
    assert target.map_layout.ram.throttle_shadow.start == 0xFFFF0C38


@pytest.mark.parametrize("rom", runtime_targets.VQ37_RUNTIME_ROMS)
def test_vq37_sources_encode_target_variants(rom):
    target = runtime_targets.load_runtime_target(rom)
    native = vq37_native_fuel_cut.load_registry()[rom]
    limiter = target.map_layout.source_text_by_unit["limiter_commit"]
    adapters = target.map_layout.source_text_by_unit["lookup_adapters"]
    completion = target.telemetry_layout.source_text_by_unit["completion"]
    tables = target.telemetry_layout.source_text_by_unit["tables"]
    rolling_engine = target.rolling_layout.source_text_by_unit["engine"]
    fuel_wrapper = target.rolling_layout.source_text_by_unit[
        "fuel_cut_wrapper"
    ]

    assert "fuel_cap_copy_loop" in limiter
    assert "fuel_curve_copy_loop" in limiter
    assert limiter.count("mov.w @r2+,r6") == 2
    assert limiter.count("mov.w @r2,r0") == 1
    assert ".long 0xFFFF0C10" in limiter
    assert ".long 0xFFFF0C14" in limiter
    assert ".long 0xFFFF0C38" in limiter
    assert "fuel_compensation_bank_2_base" in adapters
    assert "idle_ignition_bank_2_adapter" in adapters
    assert "jmp @r0\nmov.l @r15+,r0" in completion
    assert "0xFFFF0DE0, 0xFFFF0DE1" in tables
    assert "rl_apply_fuel_overlay" not in rolling_engine
    assert "mov.w r0,@(0x14,r5)" in rolling_engine
    assert "or 0x3F,r0" in fuel_wrapper
    assert f".long 0x{native.coordinator_address:08X}" in fuel_wrapper
    assert ".long 0x000A0000" not in fuel_wrapper

    map_parsed = map_switching_assembly.validate_assembly_sources(
        target.map_layout
    )
    telemetry_parsed = can_telemetry_assembly.validate_assembly_sources(
        target.telemetry_layout
    )
    rolling_parsed = rolling_launch_assembly.validate_assembly_sources(
        target.rolling_layout
    )
    assert map_switching_assembly.validate_instruction_semantics(
        target.map_layout, map_parsed, target.map_payloads
    ).instructions == 437
    assert can_telemetry_assembly.validate_instruction_semantics(
        target.telemetry_layout, telemetry_parsed, target.telemetry_payloads
    ).instructions == 617
    assert rolling_launch_assembly.validate_instruction_semantics(
        target.rolling_layout, rolling_parsed, target.rolling_payloads
    ).instructions == 872


def test_exact_code_1nd_targets_share_payloads_but_not_stage_hashes():
    locks = runtime_targets.load_payload_locks()
    zero = locks["1ND0A"]
    three = locks["1ND3B"]

    assert zero.map_payloads == three.map_payloads
    assert zero.rolling_payloads == three.rolling_payloads
    assert zero.rolling_payloads
    assert zero.telemetry_payloads == three.telemetry_payloads
    assert zero.map_stage_sha256 != three.map_stage_sha256
    assert zero.rolling_stage_sha256 != three.rolling_stage_sha256
    assert zero.telemetry_stage_sha256 != three.telemetry_stage_sha256


@pytest.mark.parametrize(
    ("rom", "wrapper_start", "reserve_start", "owned_end"),
    (
        ("JK78C", 0x0001FA00, 0x0001FA80, 0x00020000),
        ("1ND0A", 0x00135000, 0x00135080, 0x00136000),
        ("1ND3B", 0x00135000, 0x00135080, 0x00136000),
    ),
)
def test_vq37_reserve_starts_after_fuel_coordinator_wrapper(
    rom, wrapper_start, reserve_start, owned_end
):
    target = runtime_targets.load_runtime_target(rom)

    assert target.telemetry_layout.owned_rom.end == owned_end
    assert target.rolling_layout.assembly_unit_by_key[
        "fuel_cut_wrapper"
    ].span == runtime_targets.map_switching_layout.AddressRange(
        wrapper_start,
        wrapper_start + 0x80,
        "assembly.fuel_cut_wrapper",
    )
    assert target.telemetry_layout.reserved_rom.start == reserve_start
    assert target.telemetry_layout.reserved_rom.end == owned_end
    assert all(
        unit.span.end <= target.telemetry_layout.reserved_rom.start
        for unit in target.telemetry_layout.assembly_units
    )


def test_all_relocated_stage_hashes_recompose_exactly():
    targets = runtime_targets.validate_all_relocated_targets()

    assert set(targets) == set(runtime_targets.RELOCATED_ROMS)


def test_target_payload_tamper_is_rejected_by_unit_lock():
    target = runtime_targets.load_runtime_target("JK00C")
    unit = target.map_layout.assembly_units[0]
    payloads = dict(target.map_payloads)
    damaged = bytearray(payloads[unit.key])
    damaged[0] ^= 1
    payloads[unit.key] = bytes(damaged)
    parsed = map_switching_assembly.validate_assembly_sources(
        target.map_layout
    )

    with pytest.raises(ValueError, match="blob SHA-256"):
        map_switching_assembly.validate_instruction_semantics(
            target.map_layout, parsed, payloads
        )


def test_payload_lock_stock_identity_is_mandatory():
    locks = runtime_targets.load_payload_locks()["JK00D"]
    damaged = replace(locks, stock_sha256="0" * 64)

    with pytest.raises(
        runtime_targets.RuntimeTargetError,
        match="payload lock stock SHA-256 differs",
    ):
        runtime_targets.project_relocated_target("JK00D", damaged)


def test_projected_hook_must_remain_bound_to_profile():
    target = runtime_targets.load_runtime_target("JK00C")
    first = target.map_layout.hooks[0]
    damaged_layout = replace(
        target.map_layout,
        hooks=(replace(first, address=first.address + 4),)
        + target.map_layout.hooks[1:],
    )
    damaged = replace(target, map_layout=damaged_layout)
    locks = runtime_targets.load_payload_locks()["JK00C"]

    with pytest.raises(
        runtime_targets.RuntimeTargetError,
        match="projected map hooks differ",
    ):
        runtime_targets.validate_relocated_target(damaged, locks)
