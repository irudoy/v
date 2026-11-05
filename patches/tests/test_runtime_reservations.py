from dataclasses import replace
from types import SimpleNamespace

import pytest

from patches import jk08a_runtime_reservations as reservations
from patches import rolling_launch_layout


@pytest.fixture
def ledger():
    return reservations.load_ledger()


def test_abi_only_ledger_checks_both_rolling_launch_state_spans(monkeypatch):
    def no_composition():
        pytest.fail("an ABI-only layout has no complete executable composition")

    monkeypatch.setattr(reservations.can_telemetry_compose, "compose", no_composition)
    actual = reservations.load_ledger()
    assert sorted(
        (item.span.start, item.span.end)
        for item in actual.active_ram if item.owner == "rolling_launch"
    ) == [(0xFFFF5D40, 0xFFFF5D6C), (0xFFFF6100, 0xFFFF6120)]
    reservations.validate_ledger(replace(
        actual, active_ram=tuple(reversed(actual.active_ram)),
        future_ram=tuple(reversed(actual.future_ram)),
        future_rom=tuple(reversed(actual.future_rom)),
    ))


@pytest.mark.parametrize("kind", ("active_ram", "future_rom", "future_ram"))
@pytest.mark.parametrize("owner", sorted(reservations.OWNERS))
def test_each_reservation_group_requires_every_owner(ledger, kind, owner):
    rows = tuple(item for item in getattr(ledger, kind) if item.owner != owner)
    with pytest.raises(ValueError, match="every runtime"):
        reservations.validate_ledger(replace(ledger, **{kind: rows}))


def test_active_state_cannot_omit_the_extension(ledger):
    rows = tuple(item for item in ledger.active_ram if item.span.start != 0xFFFF6100)
    with pytest.raises(ValueError, match="rolling_launch: active RAM differs"):
        reservations.validate_ledger(replace(ledger, active_ram=rows))


def test_same_owner_active_and_future_spans_cannot_overlap(ledger):
    rows = tuple(
        replace(item, span=replace(item.span, start=0xFFFF6110))
        if item.span.start == 0xFFFF6120 else item
        for item in ledger.future_ram
    )
    with pytest.raises(ValueError, match="all RAM: rolling_launch overlaps rolling_launch"):
        reservations.validate_ledger(replace(ledger, future_ram=rows))


def test_ram_reserve_must_stay_inside_proven_free_space(ledger):
    rows = tuple(
        replace(item, span=replace(item.span, end=0xFFFF7001))
        if item.span.end == 0xFFFF6200 else item
        for item in ledger.future_ram
    )
    with pytest.raises(ValueError, match="RAM lies outside the free range"):
        reservations.validate_ledger(replace(ledger, future_ram=rows))


def test_additional_can_rom_span_cannot_hide_behind_the_declared_reserve(ledger):
    original = next(item for item in ledger.future_rom if item.owner == "can_telemetry")
    extra = replace(original, span=replace(original.span, start=0xD6000, end=0xD6010))
    with pytest.raises(ValueError, match="CAN telemetry ROM reserve differs"):
        reservations.validate_ledger(replace(ledger, future_rom=(extra,) + ledger.future_rom))


@pytest.mark.parametrize("start,end,message", (
    (0, 4, "ROM reserve lies outside free ROM"),
    (0xD6320, 0xD6800, "ROM reserve overlaps active write"),
))
def test_abi_only_layout_still_checks_rom_bounds_and_writes(ledger, start, end, message):
    rows = tuple(
        replace(item, span=replace(item.span, start=start, end=end))
        if item.owner == "rolling_launch" else item
        for item in ledger.future_rom
    )
    with pytest.raises(ValueError, match=message):
        reservations.validate_ledger(replace(ledger, future_rom=rows))


def test_abi_only_layout_still_excludes_checksum_bytes(ledger, monkeypatch):
    monkeypatch.setattr(reservations.checksums, "checksum_byte_offsets", lambda: (0xD6780,))
    with pytest.raises(ValueError, match="ROM reserve overlaps a checksum"):
        reservations.validate_ledger(ledger)


@pytest.mark.parametrize("erased", (True, False))
def test_ready_layout_still_checks_the_complete_composition(ledger, monkeypatch, erased):
    layout = replace(rolling_launch_layout.load_layout(), payloads_ready=True)
    monkeypatch.setattr(reservations.rolling_launch_layout, "load_layout", lambda: layout)
    data = bytearray(b"\xff" * 0x100000)
    if not erased:
        data[ledger.future_rom[0].span.start] = 0
    calls = []

    def composition():
        calls.append(True)
        return SimpleNamespace(data=data)

    monkeypatch.setattr(reservations.can_telemetry_compose, "compose", composition)
    if erased:
        reservations.validate_ledger(ledger)
    else:
        with pytest.raises(ValueError, match="ROM reserve is not erased"):
            reservations.validate_ledger(ledger)
    assert calls == [True]
