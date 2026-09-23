from dataclasses import replace

import pytest

from patches import rom_address_profiles
from tools import rom_homology

@pytest.fixture(scope="module")
def profiles():
    return rom_address_profiles.validate_all_stock_profiles()


def test_registry_has_only_explicit_exact_profiles(profiles):
    assert set(profiles) == {
        "JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B", "1ME3B"
    }
    assert rom_address_profiles.profile_for_rom("jk00c") is profiles["JK00C"]
    assert rom_address_profiles.profile_for_rom("jk78c") is profiles["JK78C"]
    with pytest.raises(
        rom_address_profiles.AddressProfileError,
        match="exact ROM label is required",
    ):
        rom_address_profiles.profile_for_rom("")
    with pytest.raises(
        rom_address_profiles.AddressProfileError,
        match="no runtime address profile",
    ):
        rom_address_profiles.profile_for_rom("JK08A")


def test_common_rebase_preserves_full_runtime_alignment(profiles):
    for rom in ("JK00C", "JK00D"):
        profile = profiles[rom]
        assert profile.rom_delta == 0xC700
        assert profile.ram_delta == 0x300
        assert profile.free_rom == rom_address_profiles.AddressRange(
            0xDE800, 0xE2700
        )
        assert profile.injected_rom == rom_address_profiles.AddressRange(
            0xDE808, 0xE2700
        )
        assert profile.free_ram == rom_address_profiles.AddressRange(
            0xFFFF6000, 0xFFFF6600
        )
        assert profile.injected_ram == rom_address_profiles.AddressRange(
            0xFFFF6000, 0xFFFF6300
        )


def test_dual_cvtc_and_nonuniform_telemetry_bindings_are_explicit(profiles):
    jk00d = profiles["JK00D"]
    jk00c = profiles["JK00C"]

    assert jk00d.map_family_by_key["intake_cvtc_target"] == 0xB7CE
    assert jk00d.map_family_by_key["exhaust_cvtc_target"] == 0xB6CE
    assert jk00c.map_family_by_key["intake_cvtc_target"] == 0xB7BE
    assert jk00c.map_family_by_key["exhaust_cvtc_target"] == 0xB6BE
    assert (
        jk00d.map_hook_by_key["exhaust_cvtc_target_lookup"].replacement
        == 0xE1700
    )
    assert (
        jk00c.map_hook_by_key["exhaust_cvtc_target_lookup"].replacement
        == 0xE1700
    )

    assert jk00d.telemetry_source_by_name["iat_raw"] == 0xFFFF28EA
    assert jk00c.telemetry_source_by_name["iat_raw"] == 0xFFFF28D6
    assert (
        jk00d.telemetry_source_by_name["throttle_target_channel_0_raw"]
        == 0xFFFF423E
    )
    assert (
        jk00c.telemetry_source_by_name["throttle_target_channel_0_raw"]
        == 0xFFFF422A
    )


def test_mailbox_24_is_selected_and_occupied_mailbox_26_is_preserved(profiles):
    for rom in ("JK00C", "JK00D"):
        profile = profiles[rom]
        symbols = profile.can_symbol_by_key
        assert symbols["mailbox_index"] == 24
        assert symbols["mailbox_mask"] == 0x0100
        assert symbols["mailbox_data"] == 0xFFFFDC08
        assert symbols["mailbox_record_stock"] == 0x05000000
        assert symbols["occupied_mailbox_record_stock"] == 0x04000000
        assert profile.telemetry_completion_variant == "mailbox24-tail-chain"


def test_1nd_profiles_share_exact_code_and_complete_runtime_capabilities(profiles):
    one = profiles["1ND0A"]
    three = profiles["1ND3B"]

    assert three == replace(one, rom="1ND3B")
    assert one.family == "sh7059_1nd"
    assert one.rom_size == 0x180000
    assert one.rom_delta == 0x60000
    assert one.ram_delta == -0x5100
    assert one.injected_rom == rom_address_profiles.AddressRange(
        0x132108, 0x136000
    )
    assert one.injected_ram == rom_address_profiles.AddressRange(
        0xFFFF0C00, 0xFFFF0F00
    )
    assert one.enabled_capabilities == {
        "map_switching", "rolling_launch", "can_telemetry"
    }
    assert set(one.rolling_hook_by_key) == (
        rom_address_profiles.VQ37_ROLLING_HOOK_KEYS
    )
    assert len(one.rolling_diagnostics) == 9
    assert one.rolling_symbol_by_key["periodic_task_slot"] == 0x0002205C
    assert one.rolling_symbol_by_key["periodic_task_table"] == 0x00022058
    assert one.rolling_symbol_by_key["vehicle_speed"] == 0xFFFE8104
    assert one.rolling_symbol_by_key["fuel_cut_coordinator"] == 0x000760CC
    assert one.telemetry_unavailable == (
        "alpha_n_flow_raw",
        "intake_cvtc_duty_command_b1_raw",
        "intake_cvtc_duty_command_b2_raw",
        "knock_timing_state_raw",
        "normalized_load_raw",
        "request_flow_raw",
    )
    assert "knock_timing_state_raw" not in one.telemetry_source_by_name
    assert "normalized_load_raw" not in one.telemetry_source_by_name
    assert one.telemetry_zero_source == 0xFFFF0DE0


def test_1nd_uses_physical_mailbox_26_and_type_a3_feedback(profiles):
    for rom in ("1ND0A", "1ND3B"):
        profile = profiles[rom]
        symbols = profile.can_symbol_by_key
        assert symbols["mailbox_index"] == 26
        assert symbols["mailbox_mask"] == 0x0400
        assert symbols["mailbox_data"] == 0xFFFFDC48
        assert symbols["feedback_config_record_value"] == 0xA308AA20
        assert symbols["feedback_payload_base_literal"] == 0x116EAC
        assert symbols["feedback_payload_offset"] == 0x142
        assert profile.telemetry_completion_variant == "mailbox26-tail-chain"


def test_stock_hook_mutation_is_rejected(profiles):
    images = rom_homology.load_images()
    profile = profiles["JK00D"]
    hook = profile.map_hook_by_key["selector_host_call"]
    changed = bytearray(images["JK00D"].data)
    changed[hook.address] ^= 0x01
    with pytest.raises(
        rom_address_profiles.AddressProfileError,
        match="selector_host_call: stock is",
    ):
        rom_address_profiles.validate_stock_profile(profile, changed)


def test_free_rom_mutation_is_rejected(profiles):
    images = rom_homology.load_images()
    profile = profiles["JK00C"]
    changed = bytearray(images["JK00C"].data)
    changed[profile.free_rom.start] = 0x00
    with pytest.raises(
        rom_address_profiles.AddressProfileError,
        match="audited free ROM is occupied",
    ):
        rom_address_profiles.validate_stock_profile(profile, changed)


def test_mailbox_variant_cannot_silently_revert_to_jk08a(tmp_path):
    source = rom_address_profiles.DEFAULT_REGISTRY.read_text(encoding="utf-8")
    changed = source.replace("mailbox_index = 24", "mailbox_index = 26", 1)
    registry = tmp_path / "profiles.toml"
    registry.write_text(changed, encoding="utf-8")
    with pytest.raises(
        rom_address_profiles.AddressProfileError,
        match="mailbox contract differs",
    ):
        rom_address_profiles.load_registry(registry)


def test_1nd_ignition_state_storage_follows_the_fuel_cut_wrapper(profiles):
    one = profiles["1ND0A"]
    storage = one.ignition_state_storage

    assert profiles["JK78C"].ignition_state_storage is None
    assert "ignition_state_lookup" not in profiles["JK78C"].map_hook_by_key
    assert storage.adapter == rom_address_profiles.AddressRange(
        0x135080, 0x135100
    )
    assert tuple(item.key for item in storage.families) == (
        rom_address_profiles.IGNITION_STATE_FAMILY_KEYS
    )
    assert [item.pointer_table for item in storage.families] == [
        0x135100, 0x135114, 0x135128, 0x13513C
    ]
    assert storage.family_by_key["ignition_surface_state_3"].copies == (
        0x135180, 0x1351C0, 0x135200, 0x135240
    )
    assert max(item.end for item in storage.ranges) == 0x135580
    hook = one.map_hook_by_key["ignition_state_lookup"]
    assert (hook.address, hook.stock, hook.replacement) == (
        0x00074FB0, 0x000285B4, storage.adapter.start
    )


@pytest.mark.parametrize(
    ("old", "new", "message"),
    (
        (
            "pointer_table = 0x00135114",
            "pointer_table = 0x00135104",
            "ignition state storage overlaps",
        ),
        (
            "copies = [0x00135480, 0x001354C0, 0x00135500, 0x00135540]",
            "copies = [0x00135480, 0x001354C0, 0x00135500, 0x00136000]",
            "ignition state storage lies outside injected ROM",
        ),
        (
            "copies = [0x00135180, 0x001351C0, 0x00135200, 0x00135240]",
            "copies = [0x00135180, 0x001351C0, 0x00135200, 0x00135244]",
            "copies must be 64-byte aligned",
        ),
    ),
)
def test_1nd_ignition_state_storage_mutation_is_rejected(
    tmp_path, old, new, message
):
    source = rom_address_profiles.DEFAULT_REGISTRY.read_text(encoding="utf-8")
    assert source.count(old) == 1
    registry = tmp_path / "profiles.toml"
    registry.write_text(source.replace(old, new), encoding="utf-8")
    with pytest.raises(
        rom_address_profiles.AddressProfileError, match=message
    ):
        rom_address_profiles.load_registry(registry)


def test_1me3b_unreferenced_ignition_routine_is_bound_to_the_image(profiles):
    images = rom_homology.load_images()
    profile = profiles["1ME3B"]
    routine = profile.ignition_unreferenced_routine

    assert profile.ascd_enabled_mask == 0x08
    assert (routine.start, routine.end) == (0x000791A4, 0x000797CC)
    assert profiles["1ND0A"].ignition_unreferenced_routine is None
    assert profiles["1ND0A"].ascd_enabled_mask == 0x80

    pointed = bytearray(images["1ME3B"].data)
    pointed[0x00100000:0x00100004] = (routine.start + 0x40).to_bytes(4, "big")
    with pytest.raises(
        rom_address_profiles.AddressProfileError,
        match="points into the unreferenced ignition routine",
    ):
        rom_address_profiles.validate_stock_profile(profile, pointed)

    # bra with displacement 0x10 at 0x00079180 targets the routine entry.
    branched = bytearray(images["1ME3B"].data)
    branched[0x00079180:0x00079182] = bytes.fromhex("a010")
    with pytest.raises(
        rom_address_profiles.AddressProfileError,
        match="enters the unreferenced ignition routine",
    ):
        rom_address_profiles.validate_stock_profile(profile, branched)
