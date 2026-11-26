from dataclasses import replace
import copy
import re
import subprocess
import sys

import pytest

from patches import can_telemetry_assembly
from patches import map_switching_assembly
from patches import rolling_launch
from patches import runtime_targets
from patches import runtime_bindings
from tools.mapkit import vq37_native_fuel_cut


FUSED_IGNITION_ROMS = (
    runtime_targets.SH7059_1ME3B_ROMS + runtime_targets.SH7059_1EK7A_ROMS
)
SH7059_ROMS = runtime_targets.SH7059_1ND_ROMS + FUSED_IGNITION_ROMS


def test_the_module_reads_numeric_bindings_without_kb_or_site_packages():
    # The firmware gate imports the module with the python3 of its container,
    # which has no site packages.
    probe = (
        "import sys\n"
        "class NoKnowledgeImports:\n"
        "    def find_spec(self, fullname, path=None, target=None):\n"
        "        if fullname == 'kb' or fullname.startswith('kb.'):\n"
        "            raise AssertionError('patch reader imports ' + fullname)\n"
        "sys.meta_path.insert(0, NoKnowledgeImports())\n"
        "sys.path.insert(0, sys.argv[1])\n"
        "from patches import runtime_targets\n"
        "runtime_targets.canonical_symbols('can_telemetry')\n"
        "runtime_targets.map_hook_keys('JK00C')\n"
        "runtime_targets.ignition_state_template()\n"
        "runtime_targets.load_payload_locks()\n"
        "for rom in runtime_targets.EXACT_ROMS:\n"
        "    runtime_targets.load_runtime_target(rom)\n"
        "assert not any(name == 'kb' or name.startswith('kb.') for name in sys.modules)\n"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", probe, str(runtime_targets.ROOT)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_the_canonical_numbers_are_those_of_the_7mfk_symbols():
    # The canonical sources and the reference contract of the JK08A runtime
    # test the named bits of 7mfk.
    assert runtime_targets.CANONICAL_ASCD_MAIN_MASK == (
        runtime_targets.ascd_main_mask("7mfk")
    )
    assert rolling_launch.MAIN_PRESSED_MASK == (
        runtime_targets.ascd_main_mask("7mfk")
    )
    assert runtime_targets.bit_moves("7mfk") == ()


@pytest.mark.parametrize(
    "damage",
    ("schema", "bit", "field_bit", "wire_bit", "image", "feature", "hook"),
)
def test_runtime_bindings_reject_malformed_machine_inputs(tmp_path, monkeypatch, damage):
    document = copy.deepcopy(runtime_bindings.load())
    if damage == "schema":
        document["schema_version"] = True
    elif damage == "bit":
        document["layouts"]["7mfk"]["ascd_main_bit"] = 8
    elif damage == "field_bit":
        document["layouts"]["1nd"]["field_bits"]["knock_surface_state"] = 8
    elif damage == "wire_bit":
        document["layouts"]["7mfk"]["field_bits"].pop("knock_surface_state")
    elif damage == "image":
        document["images"]["JK08A"] = "missing"
    elif damage == "feature":
        document["canonical_symbols"].pop("rolling_launch")
    else:
        document["map_hook_keys"]["7mfk"] = {"not-an-address": "lookup"}
    path = tmp_path / "bindings.toml"
    path.write_text("")
    monkeypatch.setattr(runtime_bindings.tomllib, "load", lambda source: document)
    with pytest.raises(runtime_bindings.RuntimeBindingsError):
        runtime_bindings.load(path)


def test_runtime_binding_reads_keep_the_cached_machine_input_unchanged():
    original = runtime_bindings.layout("7mfk")
    changed = runtime_bindings.layout("7mfk")
    changed["ascd_main_bit"] = 0
    changed["field_bits"].clear()
    assert runtime_bindings.layout("7mfk") == original
    symbols = runtime_bindings.canonical_symbols("can_telemetry")
    symbols.clear()
    assert runtime_bindings.canonical_symbols("can_telemetry")


def test_the_ignition_state_template_names_the_adapter_source_numbers():
    source = (
        runtime_targets.ROOT
        / "patches"
        / runtime_targets.IGNITION_STATE_ADAPTER_SOURCE
    ).read_text(encoding="utf-8")
    numbers = {
        int(item, 16) for item in runtime_targets.NUMBER_RE.findall(source)
    }
    template = runtime_targets.ignition_state_template()
    assert set(template) == set(runtime_targets.IGNITION_STATE_FAMILY_NAMES)
    for table, pointers in template.values():
        assert {table, pointers} <= numbers
    assert runtime_targets.IGNITION_STATE_TEMPLATE_LOOKUP in numbers


def test_runtime_registry_covers_all_supported_families():
    assert runtime_targets.SUPPORTED_ROMS == (
        "JK00A", "JK03A", "JK03B", "JK08A", "JK00C", "JK00D",
        "1ND0A", "1ND3B", "1ME3B", "1EK7A", "JK78C",
    )
    assert set(runtime_targets.load_payload_locks()) == {
        "JK00C", "JK00D", "1ND0A", "1ND3B", "1ME3B", "1EK7A", "JK78C"
    }
    for rom in runtime_targets.EXACT_ROMS:
        target = runtime_targets.load_runtime_target(rom)
        assert target.rom == rom
        assert target.family == runtime_targets.EXACT_FAMILY
        assert target.map_layout.variant == "single-cvtc"


@pytest.mark.parametrize("rom", runtime_targets.SUPPORTED_ROMS)
def test_only_exact_targets_carry_the_schema6_executable_payloads(rom):
    target = runtime_targets.load_runtime_target(rom)
    assert target.rom == rom
    if rom in runtime_targets.EXACT_ROMS:
        layout = target.rolling_layout
        assert layout is not None
        assert layout.payloads_ready
        assert set(target.rolling_payloads) == set(
            layout.assembly_unit_by_key
        )
    else:
        assert target.rolling_layout is None
        assert not target.rolling_payloads


@pytest.mark.parametrize("rom", runtime_targets.RELOCATED_8MFK_ROMS)
def test_relocated_8mfk_target_has_complete_projected_runtime(rom):
    target = runtime_targets.load_runtime_target(rom)
    profile = runtime_targets.rom_address_profiles.profile_for_rom(rom)

    assert target.family == runtime_targets.RELOCATED_8MFK_FAMILY
    assert target.stock_image.rom == rom
    assert target.map_layout.rom == rom
    assert target.map_layout.variant == "dual-cvtc"
    assert target.rolling_layout is None
    assert not target.rolling_payloads
    assert target.telemetry_layout.variant == "mailbox26-tail-chain"
    assert len(target.map_layout.families) == 13
    assert set(target.map_payloads) == {
        unit.key for unit in target.map_layout.assembly_units
    }
    assert set(target.telemetry_payloads) == {
        unit.key for unit in target.telemetry_layout.assembly_units
    }

    exhaust = target.map_layout.family_by_key["exhaust_cvtc_target"]
    assert exhaust.canonical_address == profile.map_family_by_key[
        "exhaust_cvtc_target"
    ]
    assert exhaust.copies == profile.extra_cvtc_storage.copies
    assert exhaust.pointer_table == profile.extra_cvtc_storage.pointer_table
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
    telemetry_parsed = can_telemetry_assembly.validate_assembly_sources(
        target.telemetry_layout
    )
    assert map_switching_assembly.validate_instruction_semantics(
        target.map_layout, map_parsed, target.map_payloads
    ).instructions == 1896
    assert can_telemetry_assembly.validate_instruction_semantics(
        target.telemetry_layout, telemetry_parsed, target.telemetry_payloads
    ).instructions == 1038


@pytest.mark.parametrize("rom", runtime_targets.VQ37_RUNTIME_ROMS)
def test_vq37_target_has_complete_target_specific_runtime(rom):
    target = runtime_targets.load_runtime_target(rom)
    profile = runtime_targets.rom_address_profiles.profile_for_rom(rom)
    native = vq37_native_fuel_cut.load_registry()[rom]

    expected = (
        (runtime_targets.SH7059_1ND_FAMILY, "sh7059-1nd")
        if rom in runtime_targets.SH7059_1ND_ROMS
        else (runtime_targets.SH7059_1ME3B_FAMILY, "sh7059-1me3b")
        if rom in runtime_targets.SH7059_1ME3B_ROMS
        else (runtime_targets.SH7059_1EK7A_FAMILY, "sh7059-1ek7a")
        if rom in runtime_targets.SH7059_1EK7A_ROMS
        else (runtime_targets.SH7058_JK78C_FAMILY, "sh7058-jk78")
    )
    assert (target.family, target.map_layout.variant) == expected
    assert target.rolling_layout is None
    assert not target.rolling_payloads
    assert target.telemetry_layout.variant == "mailbox26-tail-chain"
    assert len(target.map_layout.families) == (
        18 if rom in SH7059_ROMS else 14
    )
    assert set(target.map_payloads) == {
        unit.key for unit in target.map_layout.assembly_units
    }
    assert set(target.telemetry_payloads) == {
        unit.key for unit in target.telemetry_layout.assembly_units
    }
    assert target.map_layout.family_by_key[
        "fuel_compensation_main_alternate"
    ].canonical_address == profile.map_family_by_key[
        "fuel_compensation_main_alternate"
    ]
    assert target.map_layout.family_by_key[
        "idle_ignition_timing_alternate"
    ].adapter == "idle_ignition_pool_2_adapter"
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
    assert target.map_layout.ram.fuel_cut_shadow.size == 36
    assert target.map_layout.ram.throttle_shadow.start == profile.injected_ram.start + 0x38


@pytest.mark.parametrize("rom", runtime_targets.VQ37_RUNTIME_ROMS)
def test_vq37_sources_encode_target_variants(rom):
    target = runtime_targets.load_runtime_target(rom)
    profile = runtime_targets.rom_address_profiles.profile_for_rom(rom)
    limiter = target.map_layout.source_text_by_unit["limiter_commit"]
    adapters = target.map_layout.source_text_by_unit["lookup_adapters"]
    completion = target.telemetry_layout.source_text_by_unit["completion"]
    tables = target.telemetry_layout.source_text_by_unit["tables"]

    assert "fuel_cap_copy_loop" in limiter
    assert "fuel_curve_copy_loop" in limiter
    assert limiter.count("mov.w @r2+,r6") == 2
    assert limiter.count("mov.w @r2,r0") == 1
    for offset in (0x10, 0x14, 0x38):
        assert f".long 0x{profile.injected_ram.start + offset:08X}" in limiter
    assert "fuel_compensation_alternate_base" in adapters
    assert "idle_ignition_pool_2_adapter" in adapters
    assert "jmp @r0\nmov.l @r15+,r0" in completion
    pointers = {int(word, 16) for word in re.findall(r"0x[0-9A-F]{8}", tables)}
    assert set(profile.telemetry_source_by_name.values()) <= pointers
    zero = profile.telemetry_zero_source
    assert (zero is None) == (not profile.telemetry_unavailable)
    assert zero is None or zero in pointers

    map_parsed = map_switching_assembly.validate_assembly_sources(
        target.map_layout
    )
    telemetry_parsed = can_telemetry_assembly.validate_assembly_sources(
        target.telemetry_layout
    )
    # The SH7059 layouts add the 30-instruction state-code ignition adapter.
    has_state_adapter = rom in SH7059_ROMS
    assert (
        "ignition_state_adapter" in target.map_layout.source_text_by_unit
    ) == has_state_adapter
    assert map_switching_assembly.validate_instruction_semantics(
        target.map_layout, map_parsed, target.map_payloads
    ).instructions == (1910 if has_state_adapter else 1880)
    # The capture adds the instructions that move the one-bit fields into
    # their wire bits: two that set the base register, three that test the
    # dynamic page configuration, and per move a load, a mask, the shifts,
    # and a store.
    assert can_telemetry_assembly.validate_instruction_semantics(
        target.telemetry_layout, telemetry_parsed, target.telemetry_payloads
    ).instructions == 1038 + {"1ME3B": 13, "1EK7A": 15, "JK78C": 15}.get(rom, 16)


def test_exact_code_1nd_targets_share_payloads_but_not_stage_hashes():
    locks = runtime_targets.load_payload_locks()
    zero = locks["1ND0A"]
    three = locks["1ND3B"]

    assert zero.map_payloads == three.map_payloads
    assert not zero.rolling_payloads and not three.rolling_payloads
    assert zero.telemetry_payloads == three.telemetry_payloads
    assert zero.map_stage_sha256 != three.map_stage_sha256
    assert zero.rolling_stage_sha256 == zero.map_stage_sha256
    assert three.rolling_stage_sha256 == three.map_stage_sha256
    assert zero.telemetry_stage_sha256 != three.telemetry_stage_sha256


@pytest.mark.parametrize(
    ("rom", "reserve_start", "owned_end"),
    (
        ("JK78C", 0x0001FA80, 0x00020000),
        ("1ND0A", 0x00135580, 0x00136000),
        ("1ND3B", 0x00135580, 0x00136000),
        ("1ME3B", 0x0013E580, 0x0013F000),
        ("1EK7A", 0x00165580, 0x00166000),
    ),
)
def test_vq37_reserve_starts_after_the_last_injected_block(
    rom, reserve_start, owned_end
):
    target = runtime_targets.load_runtime_target(rom)

    assert target.telemetry_layout.owned_rom.end == owned_end
    assert target.telemetry_layout.reserved_rom.start == reserve_start
    assert target.telemetry_layout.reserved_rom.end == owned_end
    assert all(
        unit.span.end <= target.telemetry_layout.reserved_rom.start
        for unit in target.telemetry_layout.assembly_units
    )


@pytest.mark.slow
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


@pytest.mark.parametrize("rom", runtime_targets.VQ37_RUNTIME_ROMS)
def test_vq37_ignition_families_are_the_executed_coordinator_half(rom):
    target = runtime_targets.load_runtime_target(rom)
    symbols = runtime_targets.rom_address_profiles.profile_for_rom(
        rom
    ).map_symbol_by_key
    families = target.map_layout.family_by_key
    expected = (
        (0x0000A410, 0x0000A510)
        if rom in runtime_targets.SH7059_1ND_ROMS
        else (0x0000A344, 0x0000A444)
        if rom in runtime_targets.SH7059_1ME3B_ROMS
        else (0x0000A3FC, 0x0000A4FC)
        if rom in runtime_targets.SH7059_1EK7A_ROMS
        else (0x0000A10A, 0x0000A20A)
    )

    assert "high_octane_timing_state" not in families
    assert "high_detonation_timing_state" not in families
    hot = families["ignition_surface_hot"]
    cold = families["ignition_surface_cold"]
    assert (hot.canonical_address, cold.canonical_address) == expected
    assert (hot.name, cold.name) == (
        "Ignition Timing Surface - Hot",
        "Ignition Timing Surface - Cold",
    )
    assert (hot.adapter, cold.adapter) == (
        "ignition_adapter", "ignition_adapter"
    )
    assert hot.byte_length == cold.byte_length == 256
    data = target.stock_image.data
    if rom in FUSED_IGNITION_ROMS:
        # Bit 3 of the fused coordinator's configuration selects state dispatch.
        assert data[symbols["ignition_coordinator_config_byte"]] & 0x08
        assert not any(key.startswith("ignition_gated_") for key in symbols)
        return
    assert data[symbols["ignition_coordinator_config_byte"]] & 0x20
    gated = [
        symbols[f"ignition_gated_surface_{index}"] for index in (1, 2, 3)
    ]
    assert not set(gated) & {
        family.canonical_address for family in target.map_layout.families
    }
    assert len({bytes(data[base:base + 256]) for base in gated}) == 1


def _with_stock_byte(target, address, value):
    data = bytearray(target.stock_image.data)
    data[address] = value
    stock = target.stock_image
    return replace(
        target,
        stock_image=type(stock)(stock.rom, stock.path, bytes(data)),
    )


@pytest.mark.parametrize("rom", ("JK78C", "1ND0A"))
def test_vq37_ignition_binding_requires_the_executed_half(rom):
    target = runtime_targets.load_runtime_target(rom)
    profile = runtime_targets.rom_address_profiles.profile_for_rom(rom)
    address = profile.map_symbol_by_key["ignition_coordinator_config_byte"]
    damaged = _with_stock_byte(
        target, address, target.stock_image.data[address] & ~0x20
    )

    runtime_targets._validate_vq37_ignition_halves(target, profile)
    with pytest.raises(
        runtime_targets.RuntimeTargetError,
        match="gates the mode-selected ignition half off",
    ):
        runtime_targets._validate_vq37_ignition_halves(damaged, profile)


@pytest.mark.parametrize("rom", ("JK78C", "1ND0A"))
def test_vq37_ignition_binding_requires_equal_gated_surfaces(rom):
    target = runtime_targets.load_runtime_target(rom)
    profile = runtime_targets.rom_address_profiles.profile_for_rom(rom)
    address = profile.map_symbol_by_key["ignition_gated_surface_2"] + 17
    damaged = _with_stock_byte(
        target, address, target.stock_image.data[address] ^ 0x01
    )

    with pytest.raises(
        runtime_targets.RuntimeTargetError,
        match="gated ignition surfaces differ in the stock image",
    ):
        runtime_targets._validate_vq37_ignition_halves(damaged, profile)


def test_vq37_gated_ignition_surface_must_stay_outside_the_families():
    target = runtime_targets.load_runtime_target("JK78C")
    profile = runtime_targets.rom_address_profiles.profile_for_rom("JK78C")
    gated = profile.map_symbol_by_key["ignition_gated_surface_3"]
    families = tuple(
        replace(family, canonical_address=gated)
        if family.key == "ignition_surface_cold"
        else family
        for family in target.map_layout.families
    )
    damaged = replace(
        target, map_layout=replace(target.map_layout, families=families)
    )

    with pytest.raises(
        runtime_targets.RuntimeTargetError,
        match="a gated ignition surface is a map family",
    ):
        runtime_targets._validate_vq37_ignition_halves(damaged, profile)


@pytest.mark.parametrize("rom", SH7059_ROMS)
def test_sh7059_state_code_ignition_families_use_their_own_adapter(rom):
    target = runtime_targets.load_runtime_target(rom)
    profile = runtime_targets.rom_address_profiles.profile_for_rom(rom)
    storage = profile.ignition_state_storage
    families = target.map_layout.family_by_key
    code = target.map_layout.code_region_by_key
    expected = (
        {
            "ignition_surface_state_3": 0x0000A544,
            "ignition_surface_state_4": 0x0000A644,
            "ignition_surface_state_5": 0x0000A5C4,
            "ignition_surface_state_6_7": 0x0000A604,
        }
        if rom in runtime_targets.SH7059_1ME3B_ROMS
        else {
            "ignition_surface_state_3": 0x0000A5FC,
            "ignition_surface_state_4": 0x0000A6FC,
            "ignition_surface_state_5": 0x0000A67C,
            "ignition_surface_state_6_7": 0x0000A6BC,
        }
        if rom in runtime_targets.SH7059_1EK7A_ROMS
        else {
            "ignition_surface_state_3": 0x0000A610,
            "ignition_surface_state_4": 0x0000A710,
            "ignition_surface_state_5": 0x0000A690,
            "ignition_surface_state_6_7": 0x0000A6D0,
        }
    )

    assert tuple(item.key for item in storage.families) == tuple(expected)
    for item in storage.families:
        family = families[item.key]
        assert family.canonical_address == expected[item.key]
        assert (family.width, family.height, family.byte_length) == (8, 8, 64)
        assert family.adapter == "ignition_state_adapter"
        assert family.copies == item.copies
        assert family.pointer_table == item.pointer_table
    hook = next(
        item for item in target.map_layout.hooks
        if item.key == "ignition_state_lookup"
    )
    assert (hook.address, hook.stock) == (
        (0x00079994, 0x000293D8)
        if rom in runtime_targets.SH7059_1ME3B_ROMS
        else (0x0007B07C, 0x00029F6C)
        if rom in runtime_targets.SH7059_1EK7A_ROMS
        else (0x00074FB0, 0x000285B4)
    )
    assert hook.replacement == code["ignition_state_adapter"].entry
    assert code["ignition_state_adapter"].span.start == (
        runtime_targets.rom_address_profiles.IGNITION_STATE_ADAPTER_CANONICAL
        + profile.rom_delta
    )
    assert target.telemetry_layout.reserved_rom.start == max(
        item.end for item in storage.ranges
    )
    runtime_targets._validate_ignition_state_pool(target, profile)


def test_jk78c_has_no_state_code_ignition_families():
    target = runtime_targets.load_runtime_target("JK78C")
    profile = runtime_targets.rom_address_profiles.profile_for_rom("JK78C")

    assert profile.ignition_state_storage is None
    assert "ignition_state_lookup" not in {
        item.key for item in target.map_layout.hooks
    }
    assert "ignition_state_adapter" not in target.map_layout.code_region_by_key
    assert not any(
        family.key.startswith("ignition_surface_state_")
        for family in target.map_layout.families
    )


def test_1nd_state_code_ignition_base_must_stay_in_the_hooked_pool():
    target = runtime_targets.load_runtime_target("1ND0A")
    profile = runtime_targets.rom_address_profiles.profile_for_rom("1ND0A")
    # The second lookup literal pool names the reference surface 0x0000A650;
    # one byte turns it into a second literal of the state code 3 base.
    assert target.stock_image.data[0x0007556C:0x00075570] == bytes.fromhex(
        "0000a650"
    )
    damaged = _with_stock_byte(target, 0x0007556F, 0x10)

    with pytest.raises(
        runtime_targets.RuntimeTargetError,
        match="table base is not a single literal of the hooked lookup pool",
    ):
        runtime_targets._validate_ignition_state_pool(damaged, profile)


def test_1nd_state_code_ignition_hook_must_hold_the_stock_lookup():
    target = runtime_targets.load_runtime_target("1ND0A")
    profile = runtime_targets.rom_address_profiles.profile_for_rom("1ND0A")
    damaged = _with_stock_byte(target, 0x00074FB3, 0xB5)

    with pytest.raises(
        runtime_targets.RuntimeTargetError,
        match="ignition state lookup literal differs",
    ):
        runtime_targets._validate_ignition_state_pool(damaged, profile)



def test_1me3b_binds_only_the_live_coordinator_literals():
    target = runtime_targets.load_runtime_target("1ME3B")
    profile = runtime_targets.rom_address_profiles.profile_for_rom("1ME3B")
    data = bytes(target.stock_image.data)
    routine = profile.ignition_unreferenced_routine

    assert (routine.start, routine.end) == (0x000791A4, 0x000797CC)
    assert {
        item.key for item in target.map_layout.hooks
        if item.key.startswith("ignition_lookup_")
    } == {f"ignition_lookup_{index}" for index in range(1, 6)}
    lookup = profile.map_symbol_by_key["ignition_lookup"]
    # The original selector remains stable for native TEST attachment identity.
    # Every aligned stock pointer requires a hook, including the earlier pools.
    assert runtime_targets._aligned_literal_sites(data, lookup) == [
        0x00079420, 0x000796F4, 0x000799A4, 0x00079CAC, 0x00079E24,
    ]
    assert {hook.address for hook in profile.map_hooks
            if hook.key.startswith("ignition_lookup_")} == {
        0x00079420, 0x000796F4, 0x000799A4, 0x00079CAC, 0x00079E24,
    }
    assert {profile.map_hook_by_key[key].address for key in (
        "ignition_state_lookup", "ignition_state_lookup_earlier"
    )} == {0x00079404, 0x00079994}
    runtime_targets._validate_state_dispatch_coordinator(target, profile)
    runtime_targets._validate_ignition_state_pool(target, profile)


def test_1me3b_ignition_binding_requires_the_state_code_dispatch():
    target = runtime_targets.load_runtime_target("1ME3B")
    profile = runtime_targets.rom_address_profiles.profile_for_rom("1ME3B")
    address = profile.map_symbol_by_key["ignition_coordinator_config_byte"]
    damaged = _with_stock_byte(
        target, address, target.stock_image.data[address] & ~0x08
    )

    with pytest.raises(
        runtime_targets.RuntimeTargetError,
        match="gates the state-code ignition dispatch off",
    ):
        runtime_targets._validate_state_dispatch_coordinator(damaged, profile)


def test_1me3b_live_ignition_lookup_literal_must_be_hooked():
    target = runtime_targets.load_runtime_target("1ME3B")
    profile = runtime_targets.rom_address_profiles.profile_for_rom("1ME3B")
    # Literal 0x00079E40 names the 8x8 lookup 0x000293D8 of the
    # reference surface; one word turns it into an unhooked 16x16 literal.
    assert target.stock_image.data[0x00079E40:0x00079E44] == bytes.fromhex(
        "000293d8"
    )
    damaged = _with_stock_byte(target, 0x00079E42, 0x9B)
    damaged = _with_stock_byte(damaged, 0x00079E43, 0xA8)

    with pytest.raises(
        runtime_targets.RuntimeTargetError,
        match="16x16 ignition lookup literals differ",
    ):
        runtime_targets._validate_state_dispatch_coordinator(damaged, profile)


def test_1me3b_state_code_ignition_base_must_stay_in_the_hooked_pool():
    target = runtime_targets.load_runtime_target("1ME3B")
    profile = runtime_targets.rom_address_profiles.profile_for_rom("1ME3B")
    # The reference base precedes an unhooked 8x8 literal. A state-family
    # base at that site requires a positive consumer through a declared hook.
    assert target.stock_image.data[0x00079E3C:0x00079E40] == bytes.fromhex(
        "0000a584"
    )
    damaged = _with_stock_byte(target, 0x00079E3F, 0x44)

    with pytest.raises(
        runtime_targets.RuntimeTargetError,
        match="state-family consumer bypasses its declared lookup hook",
    ):
        runtime_targets._validate_ignition_state_pool(damaged, profile)


@pytest.mark.parametrize(
    ("rom", "mask"),
    (
        ("JK00C", 0x80),
        ("JK00D", 0x80),
        ("JK78C", 0x10),
        ("1ND0A", 0x20),
        ("1ND3B", 0x20),
        ("1ME3B", 0x02),
        ("1EK7A", 0x80),
    ),
)
def test_the_sources_test_the_ascd_main_bit_of_the_target(rom, mask):
    target = runtime_targets.load_runtime_target(rom)
    host = target.map_layout.source_text_by_unit["selector_host"]

    assert runtime_targets.ascd_main_mask(
        runtime_targets.runtime_bindings.layout_of(rom)
    ) == mask
    assert runtime_targets.ascd_main_mask("7mfk") == 0x80
    assert host.count(
        f"mov.b @r1,r0\ntst 0x{mask:02X},r0\nbf host_abort_selector\n"
    ) == 1


LTFT_NEUTRAL = "ltft_publication_neutral_control_raw"


@pytest.mark.parametrize(
    ("rom", "moves"),
    (
        ("JK08A", ()),
        ("JK00C", ()),
        ("JK00D", ()),
        ("JK78C", ((LTFT_NEUTRAL, 27, 6, 0, 31),
                   ("knock_branch_state_raw", 34, 6, 7, None))),
        ("1ND0A", ((LTFT_NEUTRAL, 27, 7, 0, 31),
                   ("knock_branch_state_raw", 34, 6, 7, None))),
        ("1ND3B", ((LTFT_NEUTRAL, 27, 7, 0, 31),
                   ("knock_branch_state_raw", 34, 6, 7, None))),
        ("1ME3B", ((LTFT_NEUTRAL, 27, 2, 0, 31),
                   ("knock_surface_state", 37, 7, 6, None))),
        ("1EK7A", ((LTFT_NEUTRAL, 27, 5, 0, 31),
                   ("knock_surface_state", 37, 7, 6, None))),
    ),
)
def test_the_capture_moves_the_one_bit_fields_of_the_target(rom, moves):
    # The wire carries the bit of 7mfk of each one-bit field: bank byte 27 of
    # the dynamic page default row, guarded by configuration byte 31, and
    # bank bytes 34 and 37 of fixed page 4.
    found = runtime_targets.bit_moves(
        runtime_targets.runtime_bindings.layout_of(rom)
    )
    assert tuple(
        (move.field, move.byte, move.source, move.wire, move.configuration)
        for move in found
    ) == moves


def test_the_capture_moves_the_bits_once_the_fixed_pages_are_copied():
    # The fixed page loop leaves r4 at bank byte 72; the moves follow it and
    # precede the context pages. A dynamic page field moves only while the
    # configuration byte is 0.
    loop_end = runtime_targets.FIXED_PAGE_LOOP_END
    after = "\nmov.b @(0x9,r3),r0\n"
    canonical = (
        runtime_targets.ROOT / "patches" / "can-telemetry-capture.s"
    ).read_text(encoding="utf-8")
    moves = (
        "// Move the bits of the one-bit fields into their wire bits.\n"
        "mov r4,r1\nadd -0x2D,r1\n"
        f"// Move bit 2 of {LTFT_NEUTRAL} into wire bit 0 while the dynamic "
        "page carries its default row.\n"
        "mov.b @(0x4,r1),r0\ntst r0,r0\n"
        f"bf telemetry_bit_move_{LTFT_NEUTRAL}_done\n"
        "mov.b @(0x0,r1),r0\nand 0x04,r0\nshlr2 r0\nmov.b r0,@(0x0,r1)\n"
        f"telemetry_bit_move_{LTFT_NEUTRAL}_done:\n"
        "// Move bit 7 of knock_surface_state into wire bit 6.\n"
        "mov.b @(0xA,r1),r0\nand 0x80,r0\nshlr r0\nmov.b r0,@(0xA,r1)\n"
    )

    assert canonical.count(loop_end + after) == 1
    capture = runtime_targets.load_runtime_target(
        "1ME3B"
    ).telemetry_layout.source_text_by_unit["capture"]
    assert capture.count(loop_end + moves + after) == 1
    unmoved = runtime_targets.load_runtime_target(
        "JK00C"
    ).telemetry_layout.source_text_by_unit["capture"]
    assert unmoved.count(loop_end + after) == 1
    assert "telemetry_bit_move" not in unmoved
    for rom in ("JK78C", "1ND0A"):
        capture = runtime_targets.load_runtime_target(
            rom
        ).telemetry_layout.source_text_by_unit["capture"]
        assert capture.count(
            loop_end + "// Move the bits of the one-bit fields"
        ) == 1
        assert capture.count("shll r0\nmov.b r0,@(0x7,r1)\n" + after) == 1


def test_a_bit_move_out_of_reach_of_the_base_register_is_refused(monkeypatch):
    far = runtime_targets.BitMove("far", 2, 7, 6, None)
    near = runtime_targets.BitMove("near", 37, 7, 6, None)
    monkeypatch.setattr(
        runtime_targets, "bit_moves", lambda layout: (far, near)
    )
    profile = runtime_targets.rom_address_profiles.profile_for_rom("1ME3B")
    with pytest.raises(runtime_targets.RuntimeTargetError, match="out of reach"):
        runtime_targets._move_field_bits(
            runtime_targets.FIXED_PAGE_LOOP_END, profile
        )

