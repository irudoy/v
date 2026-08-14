#!/usr/bin/env python3
"""Validate and generate the fixed JK08A CAN telemetry wire contract."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import tomllib


DEFAULT_SOURCE = Path(__file__).with_name("can-telemetry-profile.toml")
DEFAULT_TABLES = Path(__file__).with_name("can-telemetry-tables.s")
DEFAULT_SCHEMA = Path(__file__).with_name("can-telemetry-schema.json")
PROFILE_NAMES = ("core32", "wide54")


@dataclass(frozen=True)
class Field:
    name: str
    page: int | None
    offset: int | None
    width: int
    source: int
    profiles: tuple[str, ...]
    kind: str
    signed: bool
    scale: str

    @property
    def byte_sources(self):
        return tuple(self.source + index for index in range(self.width))


@dataclass(frozen=True)
class Context:
    tag: int
    name: str
    fields: tuple[Field, ...]

    @property
    def byte_sources(self):
        return tuple(
            address
            for field in self.fields
            for address in field.byte_sources
        )


@dataclass(frozen=True)
class Profile:
    name: str
    profile_id: int
    page_count: int
    crc16: int


@dataclass(frozen=True)
class Manifest:
    schema_version: int
    rom: str
    protocol_version: int
    byte_order: str
    mailbox: int
    candidate_can_id: int
    candidate_tick_divisor: int
    base_tick_numerator: int
    pphi_candidate_hz: int
    table_address: int
    table_end: int
    configuration_address: int
    state_address: int
    profiles: tuple[Profile, ...]
    fields: tuple[Field, ...]
    contexts: tuple[Context, ...]

    @property
    def profile_by_name(self):
        return {item.name: item for item in self.profiles}

    @property
    def profile_by_id(self):
        return {item.profile_id: item for item in self.profiles}

    @property
    def page_sources(self):
        slots = {(page, offset): None for page in range(7) for offset in range(1, 8)}
        for field in self.fields:
            if field.page is None or field.offset is None:
                continue
            for index, address in enumerate(field.byte_sources):
                slots[(field.page, field.offset + index)] = address
        return tuple(slots[(page, offset)] for page in range(7) for offset in range(1, 8))


def crc16_ccitt_false(data):
    value = 0xFFFF
    for byte in bytes(data):
        value ^= byte << 8
        for _ in range(8):
            value = ((value << 1) ^ 0x1021) & 0xFFFF if value & 0x8000 else (value << 1) & 0xFFFF
    return value


def _require_keys(table, required, optional, context):
    if not isinstance(table, dict):
        raise ValueError(f"{context}: expected a TOML table")
    actual = set(table)
    required = set(required)
    allowed = required | set(optional)
    if not required <= actual or not actual <= allowed:
        raise ValueError(
            f"{context}: fields differ; missing={sorted(required - actual)}; "
            f"extra={sorted(actual - allowed)}"
        )


def _parse_field(raw, *, context, page_field):
    required = {
        "name", "width", "source", "kind", "signed", "scale"
    }
    if page_field:
        required |= {"page", "offset", "profiles"}
    _require_keys(raw, required, (), context)
    field = Field(
        name=raw["name"],
        page=raw.get("page"),
        offset=raw.get("offset"),
        width=raw["width"],
        source=raw["source"],
        profiles=tuple(raw.get("profiles", ("wide54",))),
        kind=raw["kind"],
        signed=raw["signed"],
        scale=raw["scale"],
    )
    if (
        not isinstance(field.name, str)
        or not field.name
        or type(field.width) is not int
        or not 1 <= field.width <= 4
        or type(field.source) is not int
        or type(field.signed) is not bool
        or not isinstance(field.scale, str)
        or not field.scale
        or field.kind not in {
            "ecu_ram", "telemetry_state", "rom_configuration"
        }
    ):
        raise ValueError(f"{context}: invalid field contract")
    if field.kind == "ecu_ram" and not (
        0xFFFF1000 <= field.source
        and field.source + field.width <= 0xFFFF5D00
    ):
        raise ValueError(f"{context}: ECU RAM source is outside the safe application range")
    if field.kind == "telemetry_state" and not (
        0xFFFF5E00 <= field.source
        and field.source + field.width <= 0xFFFF5E20
    ):
        raise ValueError(f"{context}: telemetry source is outside state RAM")
    if page_field:
        if (
            type(field.page) is not int
            or not 0 <= field.page <= 6
            or type(field.offset) is not int
            or not 1 <= field.offset <= 7
            or field.offset + field.width > 8
            or not field.profiles
            or any(name not in PROFILE_NAMES for name in field.profiles)
        ):
            raise ValueError(f"{context}: invalid page placement")
    return field


def _canonical_profile(raw, fields, contexts, protocol_version):
    selected = []
    for field in fields:
        if raw["name"] not in field.profiles:
            continue
        selected.append({
            "name": field.name,
            "page": field.page,
            "offset": field.offset,
            "width": field.width,
            "source": f"0x{field.source:08X}",
            "kind": field.kind,
            "signed": field.signed,
            "scale": field.scale,
        })
    context_rows = []
    if raw["page_count"] == 8:
        for context in contexts:
            context_rows.append({
                "tag": context.tag,
                "name": context.name,
                "fields": [
                    {
                        "name": field.name,
                        "width": field.width,
                        "source": f"0x{field.source:08X}",
                        "kind": field.kind,
                        "signed": field.signed,
                        "scale": field.scale,
                    }
                    for field in context.fields
                ],
            })
    return {
        "protocol_version": protocol_version,
        "name": raw["name"],
        "id": raw["id"],
        "page_count": raw["page_count"],
        "fields": selected,
        "contexts": context_rows,
    }


def load_manifest(path=DEFAULT_SOURCE):
    path = Path(path)
    with path.open("rb") as source:
        raw = tomllib.load(source)
    root_keys = {
        "schema_version", "rom", "protocol_version", "byte_order",
        "mailbox", "candidate_can_id", "candidate_tick_divisor",
        "base_tick_numerator", "pphi_candidate_hz", "table_address",
        "table_end", "configuration_address", "state_address", "profile",
        "field", "context",
    }
    _require_keys(raw, root_keys, (), path.name)
    if (
        raw["schema_version"] != 1
        or raw["rom"] != "JK08A"
        or raw["protocol_version"] != 1
        or raw["byte_order"] != "big"
        or raw["mailbox"] != 26
        or not 1 <= raw["candidate_can_id"] <= 0x7FF
        or not 1 <= raw["candidate_tick_divisor"] <= 0xFF
        or raw["base_tick_numerator"] != 204800
        or raw["pphi_candidate_hz"] <= 0
        or raw["table_address"] != 0x000D4C00
        or raw["table_end"] != 0x000D4E00
        or raw["configuration_address"] != 0x000D4E00
        or raw["state_address"] != 0xFFFF5E00
    ):
        raise ValueError(f"{path.name}: fixed transport contract differs")

    fields = tuple(
        _parse_field(item, context=f"field[{index}]", page_field=True)
        for index, item in enumerate(raw["field"])
    )
    if len({field.name for field in fields}) != len(fields):
        raise ValueError("field names are not unique")

    contexts = []
    for index, item in enumerate(raw["context"]):
        _require_keys(item, {"tag", "name", "field"}, (), f"context[{index}]")
        context_fields = tuple(
            _parse_field(
                field,
                context=f"context[{index}].field[{field_index}]",
                page_field=False,
            )
            for field_index, field in enumerate(item["field"])
        )
        context = Context(item["tag"], item["name"], context_fields)
        if (
            type(context.tag) is not int
            or not isinstance(context.name, str)
            or not context.name
            or len(context.byte_sources) != 6
        ):
            raise ValueError(f"context[{index}]: invalid context contract")
        for field in context.fields:
            if field.kind == "rom_configuration" and not (
                raw["configuration_address"] <= field.source
                and field.source + field.width
                <= raw["configuration_address"] + 16
            ):
                raise ValueError(f"context[{index}]: ROM source lies outside configuration")
        contexts.append(context)
    contexts = tuple(contexts)
    if tuple(item.tag for item in contexts) != (0, 1, 2, 3):
        raise ValueError("context tags must be exactly 0 through 3")

    profile_raw = raw["profile"]
    if tuple(item.get("name") for item in profile_raw) != PROFILE_NAMES:
        raise ValueError("profile names or order differ")
    expected_profiles = (("core32", 1, 5), ("wide54", 2, 8))
    profiles = []
    for index, (item, expected) in enumerate(zip(profile_raw, expected_profiles)):
        _require_keys(item, {"name", "id", "page_count"}, (), f"profile[{index}]")
        if (item["name"], item["id"], item["page_count"]) != expected:
            raise ValueError(f"profile[{index}]: identity differs")
        canonical = _canonical_profile(item, fields, contexts, raw["protocol_version"])
        encoded = json.dumps(
            canonical, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        profiles.append(Profile(item["name"], item["id"], item["page_count"], crc16_ccitt_false(encoded)))
    profiles = tuple(profiles)

    manifest = Manifest(
        schema_version=raw["schema_version"],
        rom=raw["rom"],
        protocol_version=raw["protocol_version"],
        byte_order=raw["byte_order"],
        mailbox=raw["mailbox"],
        candidate_can_id=raw["candidate_can_id"],
        candidate_tick_divisor=raw["candidate_tick_divisor"],
        base_tick_numerator=raw["base_tick_numerator"],
        pphi_candidate_hz=raw["pphi_candidate_hz"],
        table_address=raw["table_address"],
        table_end=raw["table_end"],
        configuration_address=raw["configuration_address"],
        state_address=raw["state_address"],
        profiles=profiles,
        fields=fields,
        contexts=contexts,
    )
    _validate_coverage(manifest)
    return manifest


def _validate_coverage(manifest):
    occupied = {}
    for field in manifest.fields:
        for index in range(field.width):
            key = (field.page, field.offset + index)
            if key in occupied:
                raise ValueError(f"page byte {key} is assigned more than once")
            occupied[key] = field.name
    for page in range(7):
        missing = [offset for offset in range(1, 8) if (page, offset) not in occupied]
        if missing:
            raise ValueError(f"page {page} lacks source bytes {missing}")
    for field in manifest.fields:
        for profile_name in field.profiles:
            page_count = manifest.profile_by_name[profile_name].page_count
            if field.page >= page_count and not (
                profile_name == "wide54" and field.page <= 6
            ):
                raise ValueError(f"{field.name}: field lies outside profile {profile_name}")
    if len(manifest.page_sources) != 49 or any(
        item is None for item in manifest.page_sources
    ):
        raise ValueError("fixed page pointer table is incomplete")


def render_tables(manifest):
    lines = [
        "// Generated from can-telemetry-profile.toml. Do not edit.",
        "// The capture loop consumes 49 fixed page-byte pointers followed by",
        "// four six-byte context pointer groups.",
        "",
        f".org 0x{manifest.table_address:08X}",
        "telemetry_page_source_table:",
    ]
    for page in range(7):
        start = page * 7
        values = manifest.page_sources[start : start + 7]
        lines.append(".long " + ", ".join(f"0x{value:08X}" for value in values))
    lines.extend(("", "telemetry_context_source_table:"))
    for context in manifest.contexts:
        lines.append(".long " + ", ".join(f"0x{value:08X}" for value in context.byte_sources))
    return "\n".join(lines) + "\n"


def _field_json(field):
    result = {
        "name": field.name,
        "width": field.width,
        "source": f"0x{field.source:08X}",
        "kind": field.kind,
        "signed": field.signed,
        "scale": field.scale,
    }
    if field.page is not None:
        result["page"] = field.page
        result["offset"] = field.offset
    return result


def render_schema(manifest):
    document = {
        "schema_version": manifest.schema_version,
        "rom": manifest.rom,
        "protocol_version": manifest.protocol_version,
        "byte_order": manifest.byte_order,
        "frame": {
            "format": "standard_11_bit_classical_can",
            "dlc": 8,
            "mailbox": manifest.mailbox,
            "candidate_can_id": f"0x{manifest.candidate_can_id:03X}",
            "header": "((tick16 & 0x1f) << 3) | page_id",
        },
        "profiles": [
            {
                "name": profile.name,
                "id": profile.profile_id,
                "page_count": profile.page_count,
                "crc16_ccitt_false": f"0x{profile.crc16:04X}",
                "fields": [
                    _field_json(field)
                    for field in manifest.fields
                    if profile.name in field.profiles
                ],
                "contexts": [
                    {
                        "tag": context.tag,
                        "name": context.name,
                        "fields": [_field_json(field) for field in context.fields],
                    }
                    for context in manifest.contexts
                ] if profile.page_count == 8 else [],
            }
            for profile in manifest.profiles
        ],
    }
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def generate(source=DEFAULT_SOURCE, tables=DEFAULT_TABLES, schema=DEFAULT_SCHEMA, *, check=False):
    manifest = load_manifest(source)
    outputs = {
        Path(tables): render_tables(manifest),
        Path(schema): render_schema(manifest),
    }
    stale = []
    for path, content in outputs.items():
        if check:
            try:
                actual = path.read_text(encoding="utf-8")
            except OSError:
                actual = None
            if actual != content:
                stale.append(path)
        else:
            path.write_text(content, encoding="utf-8")
    if stale:
        raise ValueError(
            "generated telemetry artifacts are stale: "
            + ", ".join(str(path) for path in stale)
        )
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--tables", type=Path, default=DEFAULT_TABLES)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    manifest = generate(args.source, args.tables, args.schema, check=args.check)
    print(
        "status=PASS"
        f" profiles={len(manifest.profiles)}"
        f" fields={len(manifest.fields)}"
        f" contexts={len(manifest.contexts)}"
        f" table_bytes={49 * 4 + 24 * 4}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
