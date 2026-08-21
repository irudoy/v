from dataclasses import replace

import pytest

from patches import can_telemetry_assembly
from patches import map_switching_assembly
from patches import rolling_launch_assembly
from patches import runtime_targets


def test_runtime_registry_covers_both_supported_sh7058_families():
    assert runtime_targets.SUPPORTED_ROMS == (
        "JK00A", "JK03A", "JK03B", "JK08A", "JK00C", "JK00D"
    )
    assert set(runtime_targets.load_payload_locks()) == {"JK00C", "JK00D"}
    for rom in runtime_targets.EXACT_ROMS:
        target = runtime_targets.load_runtime_target(rom)
        assert target.rom == rom
        assert target.family == runtime_targets.EXACT_FAMILY
        assert target.map_layout.variant == "single-exhaust"


@pytest.mark.parametrize("rom", runtime_targets.RELOCATED_ROMS)
def test_relocated_target_has_complete_projected_runtime(rom):
    target = runtime_targets.load_runtime_target(rom)
    profile = runtime_targets.rom_address_profiles.profile_for_rom(rom)

    assert target.family == runtime_targets.RELOCATED_FAMILY
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


@pytest.mark.parametrize("rom", runtime_targets.RELOCATED_ROMS)
def test_relocated_sources_cover_alignment_and_tail_chain_variants(rom):
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
