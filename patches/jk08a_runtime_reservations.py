#!/usr/bin/env python3
"""Validate exclusive active RAM and future growth budgets for JK08A."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import can_telemetry_compose
from patches import can_telemetry_layout
from patches import jk08a_checksums as checksums
from patches import map_switching_compose
from patches import map_switching_layout
from patches import rolling_launch_compose
from patches import rolling_launch_layout


DEFAULT_MANIFEST = Path(__file__).with_name(
    "jk08a-runtime-reservations.toml"
)
OWNERS = frozenset(("map_switching", "rolling_launch", "can_telemetry"))


@dataclass(frozen=True)
class Reservation:
    owner: str
    span: map_switching_layout.AddressRange
    purpose: str


@dataclass(frozen=True)
class Ledger:
    schema_version: int
    rom: str
    ram_proven_free: map_switching_layout.AddressRange
    active_ram: tuple[Reservation, ...]
    future_rom: tuple[Reservation, ...]
    future_ram: tuple[Reservation, ...]


def _require_exact_keys(table, expected, context):
    if not isinstance(table, dict) or set(table) != set(expected):
        actual = set(table) if isinstance(table, dict) else set()
        raise ValueError(
            f"{context}: fields differ; "
            f"missing={sorted(set(expected) - actual)}; "
            f"extra={sorted(actual - set(expected))}"
        )


def _reservations(rows, kind):
    result = []
    for index, row in enumerate(rows):
        context = f"{kind}[{index}]"
        _require_exact_keys(row, ("owner", "start", "end", "purpose"), context)
        if row["owner"] not in OWNERS:
            raise ValueError(f"{context}: unknown owner {row['owner']!r}")
        if not isinstance(row["purpose"], str) or not row["purpose"].strip():
            raise ValueError(f"{context}: purpose must be non-empty")
        result.append(Reservation(
            owner=row["owner"],
            span=map_switching_layout.AddressRange(
                row["start"], row["end"], f"{kind}.{row['owner']}"
            ),
            purpose=row["purpose"].strip(),
        ))
    return tuple(result)


def load_ledger(path=DEFAULT_MANIFEST):
    path = Path(path)
    with path.open("rb") as source:
        raw = tomllib.load(source)
    _require_exact_keys(
        raw,
        (
            "schema_version", "rom", "ram_proven_free_start",
            "ram_proven_free_end", "active_ram", "future_rom",
            "future_ram",
        ),
        path.name,
    )
    ledger = Ledger(
        schema_version=raw["schema_version"],
        rom=raw["rom"],
        ram_proven_free=map_switching_layout.AddressRange(
            raw["ram_proven_free_start"],
            raw["ram_proven_free_end"],
            "ram_proven_free",
        ),
        active_ram=_reservations(raw["active_ram"], "active_ram"),
        future_rom=_reservations(raw["future_rom"], "future_rom"),
        future_ram=_reservations(raw["future_ram"], "future_ram"),
    )
    validate_ledger(ledger)
    return ledger


def _require_owner_set(items, context):
    if {item.owner for item in items} != OWNERS:
        raise ValueError(f"{context}: every runtime must have reservations")


def _owner_spans(items, owner):
    return sorted(
        (item.span.start, item.span.end)
        for item in items if item.owner == owner
    )


def _require_disjoint(items, context):
    ordered = sorted(items, key=lambda item: item.span.start)
    for left, right in zip(ordered, ordered[1:]):
        if left.span.overlaps(right.span):
            raise ValueError(
                f"{context}: {left.owner} overlaps {right.owner}"
            )


def _rom_write_ranges(map_layout, launch_layout, telemetry_layout):
    return tuple(chain(
        map_switching_compose.composition_write_ranges(map_layout),
        rolling_launch_compose.composition_write_ranges(launch_layout),
        can_telemetry_compose.composition_write_ranges(telemetry_layout),
    ))


def validate_ledger(ledger):
    if ledger.schema_version != 1 or ledger.rom != "JK08A":
        raise ValueError("unsupported runtime reservation ledger")
    _require_owner_set(ledger.active_ram, "active RAM")
    _require_owner_set(ledger.future_rom, "future ROM")
    _require_owner_set(ledger.future_ram, "future RAM")
    _require_disjoint(ledger.active_ram, "active RAM")
    _require_disjoint(ledger.future_rom, "future ROM")
    _require_disjoint(ledger.future_ram, "future RAM")
    _require_disjoint(ledger.active_ram + ledger.future_ram, "all RAM")

    map_layout = map_switching_layout.load_layout()
    launch_layout = rolling_launch_layout.load_layout()
    telemetry_layout = can_telemetry_layout.load_layout()
    expected_active = {
        "map_switching": map_layout.ram.active_spans,
        "rolling_launch": launch_layout.ram.active_spans,
        "can_telemetry": (telemetry_layout.ram.active,),
    }
    for owner, spans in expected_active.items():
        expected = sorted((span.start, span.end) for span in spans)
        if _owner_spans(ledger.active_ram, owner) != expected:
            raise ValueError(f"{owner}: active RAM differs from its layout")

    if (
        ledger.ram_proven_free.start != 0xFFFF5D00
        or ledger.ram_proven_free.end != 0xFFFF7000
    ):
        raise ValueError("shared proven-free RAM boundary differs")
    for item in ledger.active_ram + ledger.future_ram:
        if not ledger.ram_proven_free.contains(item.span):
            raise ValueError(f"{item.owner}: RAM lies outside the free range")

    if _owner_spans(ledger.future_rom, "can_telemetry") != [(
        telemetry_layout.reserved_rom.start,
        telemetry_layout.reserved_rom.end,
    )]:
        raise ValueError("CAN telemetry ROM reserve differs from its layout")
    free_by_owner = {
        "map_switching": map_layout.free_rom,
        "rolling_launch": launch_layout.free_rom,
        "can_telemetry": telemetry_layout.free_rom,
    }
    writes = _rom_write_ranges(map_layout, launch_layout, telemetry_layout)
    checksum_offsets = set(checksums.checksum_byte_offsets())
    for item in ledger.future_rom:
        if not free_by_owner[item.owner].contains(item.span):
            raise ValueError(f"{item.owner}: ROM reserve lies outside free ROM")
        for write in writes:
            if item.span.overlaps(write):
                raise ValueError(
                    f"{item.owner}: ROM reserve overlaps active write {write.key}"
                )
        if checksum_offsets & set(range(item.span.start, item.span.end)):
            raise ValueError(f"{item.owner}: ROM reserve overlaps a checksum")

    # An ABI-only layout has no qualified complete composition to inspect.
    # Its ownership, bounds, write sets, and checksum exclusions remain checked.
    if not launch_layout.payloads_ready:
        return
    composition = can_telemetry_compose.compose().data
    for item in ledger.future_rom:
        actual = composition[item.span.start : item.span.end]
        if actual != bytes([0xFF]) * item.span.size:
            raise ValueError(f"{item.owner}: ROM reserve is not erased")


def main():
    ledger = load_ledger()
    print(
        "status=PASS"
        f" active_ram_bytes={sum(item.span.size for item in ledger.active_ram)}"
        f" future_rom_bytes={sum(item.span.size for item in ledger.future_rom)}"
        f" future_ram_bytes={sum(item.span.size for item in ledger.future_ram)}"
        f" owners={len(OWNERS)}"
    )


if __name__ == "__main__":
    main()
