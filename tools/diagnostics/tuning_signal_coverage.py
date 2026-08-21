#!/usr/bin/env python3
"""Validate and summarize JK08A tuning-signal observation coverage."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import can_telemetry_profile
from tools.diagnostics import sid22_inventory


DEFAULT_SOURCE = ROOT / "defs" / "JK08A.tuning-signals.toml"
ALLOWED_PRIORITIES = {"core", "high", "medium", "research"}
ALLOWED_COVERAGE = {
    "fixed",
    "rotating",
    "latched",
    "stock-can",
    "absent",
    "unresolved",
    "instrumentation",
    "external",
}
ALLOWED_EVIDENCE = {
    "exact-code",
    "exact-code+homologous-diagnostic",
    "patch-design",
    "passive-can",
    "research-requirement",
    "measurement-requirement",
}
SIGNAL_ID = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True)
class Signal:
    signal_id: str
    domain: str
    label: str
    priority: str
    coverage: str
    current_fields: tuple[str, ...]
    sources: tuple[int, ...]
    widths: tuple[int, ...]
    dids: tuple[int, ...]
    evidence: str
    note: str

    @property
    def source_ranges(self) -> tuple[range, ...]:
        return tuple(
            range(source, source + width)
            for source, width in zip(self.sources, self.widths)
        )

    def contains_range(self, source: int, width: int) -> bool:
        requested = set(range(source, source + width))
        return any(requested <= set(available) for available in self.source_ranges)

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.signal_id,
            "domain": self.domain,
            "label": self.label,
            "priority": self.priority,
            "coverage": self.coverage,
            "current_fields": list(self.current_fields),
            "sources": [f"0x{source:08X}" for source in self.sources],
            "widths": list(self.widths),
            "dids": [f"0x{did:04X}" for did in self.dids],
            "evidence": self.evidence,
            "note": self.note,
        }


@dataclass(frozen=True)
class Catalog:
    schema_version: int
    rom: str
    telemetry_profile: str
    full_rate_hz: float
    rotating_divisor: int
    signals: tuple[Signal, ...]

    @property
    def by_id(self) -> dict[str, Signal]:
        return {signal.signal_id: signal for signal in self.signals}


def _require_keys(table, required, context):
    if not isinstance(table, dict):
        raise ValueError(f"{context}: expected a TOML table")
    required = set(required)
    actual = set(table)
    if actual != required:
        raise ValueError(
            f"{context}: fields differ; missing={sorted(required - actual)}; "
            f"extra={sorted(actual - required)}"
        )


def _parse_signal(raw, index):
    context = f"signal[{index}]"
    _require_keys(
        raw,
        {
            "id",
            "domain",
            "label",
            "priority",
            "coverage",
            "current_fields",
            "sources",
            "widths",
            "dids",
            "evidence",
            "note",
        },
        context,
    )
    signal = Signal(
        signal_id=raw["id"],
        domain=raw["domain"],
        label=raw["label"],
        priority=raw["priority"],
        coverage=raw["coverage"],
        current_fields=tuple(raw["current_fields"]),
        sources=tuple(raw["sources"]),
        widths=tuple(raw["widths"]),
        dids=tuple(raw["dids"]),
        evidence=raw["evidence"],
        note=raw["note"],
    )
    if not isinstance(signal.signal_id, str) or not SIGNAL_ID.fullmatch(
        signal.signal_id
    ):
        raise ValueError(f"{context}: invalid signal id")
    if any(
        not isinstance(value, str) or not value
        for value in (signal.domain, signal.label, signal.note)
    ):
        raise ValueError(f"{context}: text fields must be nonempty strings")
    if signal.priority not in ALLOWED_PRIORITIES:
        raise ValueError(f"{context}: invalid priority {signal.priority!r}")
    if signal.coverage not in ALLOWED_COVERAGE:
        raise ValueError(f"{context}: invalid coverage {signal.coverage!r}")
    if signal.evidence not in ALLOWED_EVIDENCE:
        raise ValueError(f"{context}: invalid evidence {signal.evidence!r}")
    if len(signal.sources) != len(signal.widths):
        raise ValueError(f"{context}: sources and widths differ")
    if any(type(source) is not int for source in signal.sources):
        raise ValueError(f"{context}: source addresses must be integers")
    if any(type(width) is not int or not 1 <= width <= 4 for width in signal.widths):
        raise ValueError(f"{context}: source widths must be 1 through 4")
    if any(type(did) is not int or not 0 <= did <= 0xFFFF for did in signal.dids):
        raise ValueError(f"{context}: DIDs must be uint16 values")
    if len(set(signal.current_fields)) != len(signal.current_fields):
        raise ValueError(f"{context}: duplicate current fields")
    if len(set(signal.dids)) != len(signal.dids):
        raise ValueError(f"{context}: duplicate DIDs")
    return signal


def _validate_profile_coverage(catalog, manifest):
    fixed = {field.name: field for field in manifest.fields}
    rotating = {
        field.name: field
        for context in manifest.contexts
        for field in context.fields
    }
    all_fields = fixed | rotating
    owners = {}
    for signal in catalog.signals:
        for name in signal.current_fields:
            if name not in all_fields:
                raise ValueError(
                    f"{signal.signal_id}: unknown current telemetry field {name!r}"
                )
            if name in owners:
                raise ValueError(
                    f"telemetry field {name!r} belongs to both "
                    f"{owners[name]} and {signal.signal_id}"
                )
            owners[name] = signal.signal_id
            field = all_fields[name]
            if not signal.contains_range(field.source, field.width):
                raise ValueError(
                    f"{signal.signal_id}: field {name!r} lies outside declared sources"
                )
            if signal.coverage in {"fixed", "latched"} and name not in fixed:
                raise ValueError(f"{signal.signal_id}: {name!r} is not fixed-rate")
            if signal.coverage == "rotating" and name not in rotating:
                raise ValueError(f"{signal.signal_id}: {name!r} is not rotating")

    tuning_fields = {
        field.name
        for field in manifest.fields
        if field.kind == "ecu_ram"
    } | {
        field.name
        for context in manifest.contexts
        for field in context.fields
        if field.kind == "ecu_ram"
    } | {"knock_count_latched", "knock_channel_mask_latched"}
    missing = sorted(tuning_fields - set(owners))
    if missing:
        raise ValueError(f"current tuning fields lack catalog owners: {missing}")

    for signal in catalog.signals:
        if signal.coverage in {"fixed", "rotating", "latched"}:
            if not signal.current_fields:
                raise ValueError(f"{signal.signal_id}: covered signal has no fields")
        elif signal.current_fields:
            raise ValueError(
                f"{signal.signal_id}: {signal.coverage} signal has current fields"
            )


def _validate_dids(catalog, inventory):
    by_did = {entry.did: entry for entry in inventory}
    owners = {}
    for signal in catalog.signals:
        for did in signal.dids:
            if did not in by_did:
                raise ValueError(f"{signal.signal_id}: DID 0x{did:04X} is not declared")
            if did in owners:
                raise ValueError(
                    f"DID 0x{did:04X} belongs to both {owners[did]} and "
                    f"{signal.signal_id}"
                )
            owners[did] = signal.signal_id
            entry = by_did[did]
            if entry.source_layout == "dynamic":
                continue
            if entry.source_layout == "sequential":
                sources_match = (
                    len(entry.sources) == 1
                    and signal.contains_range(entry.sources[0], entry.width)
                )
            else:
                sources_match = len(entry.sources) == entry.width and all(
                    signal.contains_range(source, 1) for source in entry.sources
                )
            if not sources_match:
                raise ValueError(
                    f"{signal.signal_id}: DID 0x{did:04X} sources lie outside "
                    "the declared signal ranges"
                )


def load_catalog(path=DEFAULT_SOURCE):
    path = Path(path)
    with path.open("rb") as source:
        raw = tomllib.load(source)
    _require_keys(
        raw,
        {
            "schema_version",
            "rom",
            "telemetry_profile",
            "full_rate_hz",
            "rotating_divisor",
            "signal",
        },
        path.name,
    )
    if (
        raw["schema_version"] != 1
        or raw["rom"] != "JK08A"
        or raw["telemetry_profile"] != "tuning"
        or raw["full_rate_hz"] != 97.65625
        or raw["rotating_divisor"] != 4
    ):
        raise ValueError(f"{path.name}: fixed catalog contract differs")
    signals = tuple(
        _parse_signal(item, index) for index, item in enumerate(raw["signal"])
    )
    if len({signal.signal_id for signal in signals}) != len(signals):
        raise ValueError("signal ids are not unique")
    catalog = Catalog(
        schema_version=raw["schema_version"],
        rom=raw["rom"],
        telemetry_profile=raw["telemetry_profile"],
        full_rate_hz=raw["full_rate_hz"],
        rotating_divisor=raw["rotating_divisor"],
        signals=signals,
    )
    manifest = can_telemetry_profile.load_manifest()
    _validate_profile_coverage(catalog, manifest)
    _validate_dids(catalog, sid22_inventory.read_inventory())
    return catalog


def summary(catalog):
    coverage = Counter(signal.coverage for signal in catalog.signals)
    priority = Counter(signal.priority for signal in catalog.signals)
    missing = tuple(
        signal
        for signal in catalog.signals
        if signal.coverage in {
            "absent",
            "unresolved",
            "instrumentation",
            "external",
        }
    )
    return {
        "rom": catalog.rom,
        "profile": catalog.telemetry_profile,
        "full_rate_hz": catalog.full_rate_hz,
        "rotating_rate_hz": catalog.full_rate_hz / catalog.rotating_divisor,
        "signal_count": len(catalog.signals),
        "coverage": dict(sorted(coverage.items())),
        "priority": dict(sorted(priority.items())),
        "gaps": [signal.as_dict() for signal in missing],
    }


def render_markdown(catalog):
    report = summary(catalog)
    lines = [
        f"JK08A {report['profile']} tuning-signal coverage",
        f"Fixed rate: {report['full_rate_hz']:.5f} Hz",
        f"Rotating rate: {report['rotating_rate_hz']:.8f} Hz",
        f"Catalog signals: {report['signal_count']}",
        "",
        "Coverage counts:",
    ]
    for key, value in report["coverage"].items():
        lines.append(f"  {key}: {value}")
    lines.extend(("", "Open gaps:", ""))
    for signal in report["gaps"]:
        sources = ", ".join(signal["sources"]) or "none"
        dids = ", ".join(signal["dids"]) or "none"
        lines.append(
            f"- {signal['id']} [{signal['priority']}/{signal['coverage']}]: "
            f"sources={sources}; DIDs={dids}"
        )
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate and summarize JK08A tuning-signal coverage"
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(args.source)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.format == "json":
        json.dump(summary(catalog), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_markdown(catalog))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
