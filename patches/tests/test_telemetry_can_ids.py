"""Reject stock HCAN1 and diagnostic ID collisions before image output."""

from dataclasses import replace

import pytest

from patches import build_rom, can_telemetry, can_telemetry_compose, rom_checksums, runtime_targets


@pytest.fixture(scope="module", params=runtime_targets.SUPPORTED_ROMS)
def target(request):
    return runtime_targets.load_runtime_target(request.param)


def build(target, can_id, *, enabled=True):
    profile = replace(
        build_rom.builtin_profile(target.family),
        telemetry=can_telemetry.Configuration(enabled=enabled, can_id=can_id),
    )
    return build_rom.build_image(target.stock_image.data, rom=target.rom, profile=profile)


@pytest.mark.parametrize("role,can_id", (("data", 0x180), ("control", 0x17F)))
def test_builder_rejects_stock_transmit_id_on_every_rom(target, role, can_id):
    with pytest.raises(build_rom.BuildError) as caught:
        build(target, can_id)
    assert f"telemetry {role} CAN ID 0x180" in str(caught.value)
    assert "stock HCAN1 mailbox 8 (TX," in str(caught.value)


@pytest.mark.parametrize("role,can_id", (("data", 0x700), ("control", 0x6FF)))
def test_builder_reserves_diagnostic_range_on_every_rom(target, role, can_id):
    with pytest.raises(build_rom.BuildError) as caught:
        build(target, can_id)
    assert f"telemetry {role} CAN ID 0x700" in str(caught.value)
    assert "reserved diagnostic range" in str(caught.value)


def test_highest_permitted_pair_builds_on_every_rom(target):
    result = build(target, 0x6FE)
    assert result.profile.telemetry.can_id == 0x6FE
    assert result.profile.telemetry.control_can_id == 0x6FF
    assert rom_checksums.verify(result.data, target.checksum_layout).valid
    assert target.telemetry_layout.control_mailbox == (
        22 if target.rom == "1ME3B" else 31
    )
    if target.rom == "1ME3B":
        assert target.stock_image.data[0x9820:0x9824] == bytes.fromhex("05000000")
        assert result.data[0x9820:0x9824] == bytes.fromhex("05000000")
        assert result.data[0x9844:0x9848] == bytes.fromhex("01085240")
    if target.rom == "1EK7A":
        assert target.stock_image.data[0x99BC:0x99C0] == bytes.fromhex("05000000")
        assert result.data[0x99BC:0x99C0] == bytes.fromhex("05000000")


@pytest.mark.parametrize("rom,identifier,mailbox,direction", (
    ("JK08A", 0x245, 16, "RX"),
    ("JK78C", 0x245, 4, "RX"),
    ("1ND0A", 0x551, 1, "TX"),
    ("1ND3B", 0x551, 1, "TX"),
    ("1ME3B", 0x239, 1, "TX"),
    ("1ME3B", 0x292, 31, "RX"),
    ("1EK7A", 0x245, 4, "RX"),
    ("1EK7A", 0x6E2, 1, "TX"),
))
@pytest.mark.parametrize("role", ("data", "control"))
def test_receive_and_extended_records_reject_both_ids(rom, identifier, mailbox, direction, role):
    target = runtime_targets.load_runtime_target(rom)
    can_id = identifier if role == "data" else identifier - 1
    with pytest.raises(build_rom.BuildError) as caught:
        build(target, can_id)
    assert f"telemetry {role} CAN ID {identifier:#05x}" in str(caught.value)
    assert f"stock HCAN1 mailbox {mailbox} ({direction}," in str(caught.value)


@pytest.mark.slow
def test_inactive_ids_are_image_local_within_an_exact_code_family():
    result = build(runtime_targets.load_runtime_target("JK00A"), 0x239)
    assert result.profile.telemetry.can_id == 0x239
    with pytest.raises(build_rom.BuildError, match="stock HCAN1 mailbox 1"):
        build(runtime_targets.load_runtime_target("JK08A"), 0x239)


@pytest.mark.parametrize("can_id", (0x180, 0x17F))
def test_disabled_startup_does_not_allow_a_later_collision(can_id):
    with pytest.raises(build_rom.BuildError, match="stock HCAN1 mailbox 8"):
        build(runtime_targets.load_runtime_target("JK08A"), can_id, enabled=False)


@pytest.fixture(scope="module")
def canonical_base():
    return can_telemetry_compose.build_base_composition()


@pytest.mark.parametrize("can_id", (0x180, 0x17F))
@pytest.mark.parametrize("encoded", (False, True))
def test_composition_checks_model_and_encoded_configuration(canonical_base, can_id, encoded):
    configuration = can_telemetry.Configuration(can_id=can_id)
    if encoded:
        configuration = configuration.to_bytes()
    with pytest.raises(ValueError, match="stock HCAN1 mailbox 8"):
        can_telemetry_compose.compose(base=canonical_base, configuration=configuration)


@pytest.mark.parametrize("can_id", (0x7D0, 0x7DF, 0x7E0, 0x7E8))
def test_composition_reserves_direct_diagnostic_ids(canonical_base, can_id):
    with pytest.raises(ValueError, match="reserved diagnostic range"):
        can_telemetry_compose.compose(
            base=canonical_base, configuration=can_telemetry.Configuration(can_id=can_id)
        )


def test_unreviewed_layout_and_record_type_fail_closed():
    target = runtime_targets.load_runtime_target("JK08A")
    layout = target.telemetry_layout
    with pytest.raises(ValueError, match="format has not been reviewed"):
        can_telemetry_compose._validated_configuration(
            None, layout=replace(layout, rom="UNREVIEWED"), base=target.stock_image.data
        )
    source = bytearray(target.stock_image.data)
    source[layout.mailbox_record_address - 25 * 4] = 0xA3
    with pytest.raises(ValueError, match="unreviewed stock HCAN1 record type"):
        can_telemetry_compose._validated_configuration(None, layout=layout, base=source)
