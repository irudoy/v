import pytest

from patches import rom_address_profiles
from tools import rom_homology

@pytest.fixture(scope="module")
def profiles():
    return rom_address_profiles.validate_all_stock_profiles()


def test_registry_has_only_explicit_exact_profiles(profiles):
    assert set(profiles) == {"JK00C", "JK00D"}
    assert rom_address_profiles.profile_for_rom("jk00c") is profiles["JK00C"]
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
    for profile in profiles.values():
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


def test_dual_exhaust_and_nonuniform_telemetry_bindings_are_explicit(profiles):
    jk00d = profiles["JK00D"]
    jk00c = profiles["JK00C"]

    assert jk00d.map_family_by_key["exhaust_cvtc_target_even"] == 0xB7CE
    assert jk00d.map_family_by_key["exhaust_cvtc_target_odd"] == 0xB6CE
    assert jk00c.map_family_by_key["exhaust_cvtc_target_even"] == 0xB7BE
    assert jk00c.map_family_by_key["exhaust_cvtc_target_odd"] == 0xB6BE
    assert (
        jk00d.map_hook_by_key["exhaust_cvtc_target_lookup_odd"].replacement
        == 0xE1700
    )
    assert (
        jk00c.map_hook_by_key["exhaust_cvtc_target_lookup_odd"].replacement
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
    for profile in profiles.values():
        symbols = profile.can_symbol_by_key
        assert symbols["mailbox_index"] == 24
        assert symbols["mailbox_mask"] == 0x0100
        assert symbols["mailbox_data"] == 0xFFFFDC08
        assert symbols["mailbox_record_stock"] == 0x05000000
        assert symbols["occupied_mailbox_record_stock"] == 0x04000000
        assert profile.telemetry_completion_variant == "mailbox24-tail-chain"


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
