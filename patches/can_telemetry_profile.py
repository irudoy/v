#!/usr/bin/env python3
"""Validate the exact producer binding and generate neutral wire artifacts
and the slot tables of the specification."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field as dataclass_field
import json
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.logs import can_telemetry
from tools.logs import can_telemetry_schema


DEFAULT_SOURCE = Path(__file__).with_name("can-telemetry-profile.toml")
DEFAULT_TABLES = Path(__file__).with_name("can-telemetry-tables.s")
DEFAULT_SCHEMA = Path(__file__).with_name("can-telemetry-schema.json")
DEFAULT_IDENTITY = Path(__file__).with_name("can-telemetry-identity.h")
DEFAULT_SPECIFICATION = Path(__file__).with_name("can-telemetry.md")
# The marked section of the specification that holds the slot tables.
SPECIFICATION_SECTION = "telemetry-slots"
GENERATE_COMMAND = "uv run python patches/can_telemetry_profile.py"
RESERVATIONS = Path(__file__).with_name("jk08a-runtime-reservations.toml")
PROFILE_NAMES = ("tuning",)
# Runtime state fields read the active RAM of these runtimes.
RUNTIME_STATE_OWNERS = ("map_switching", "rolling_launch")
# Sources outside the active runtime RAM, by producer storage kind.
SOURCE_LABELS = {"ecu_ram": "ECU RAM", "rom_configuration": "ROM configuration"}


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
    # The host presentation of [field.dashboard], which the host schema
    # carries and the wire identity leaves out.
    dashboard: dict | None = dataclass_field(default=None, compare=False)

    @property
    def byte_sources(self):
        return tuple(self.source + index for index in range(self.width))


@dataclass(frozen=True)
class Context:
    page: int
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
    pphi_hz: int
    fixed_page_count: int
    context_pages: tuple[int, ...]
    context_count: int
    header_sequence_bits: int
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
        slots = {
            (page, offset): None
            for page in range(self.fixed_page_count)
            for offset in range(1, 8)
        }
        for field in self.fields:
            if field.page is None or field.offset is None:
                continue
            for index, address in enumerate(field.byte_sources):
                slots[(field.page, field.offset + index)] = address
        return tuple(
            slots[(page, offset)]
            for page in range(self.fixed_page_count)
            for offset in range(1, 8)
        )

    @property
    def contexts_by_page(self):
        return {
            page: tuple(item for item in self.contexts if item.page == page)
            for page in self.context_pages
        }


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


def _active_ram(path=RESERVATIONS):
    """Return (owner, start, end) of every active runtime RAM allocation."""
    with Path(path).open("rb") as source:
        ledger = tomllib.load(source)
    return tuple(
        (row["owner"], row["start"], row["end"]) for row in ledger["active_ram"]
    )


def _runtime_state_spans(path=RESERVATIONS):
    """Return the active RAM spans of the runtimes a state field may read."""
    spans = tuple(
        (start, end)
        for owner, start, end in _active_ram(path)
        if owner in RUNTIME_STATE_OWNERS
    )
    if len(spans) != len(RUNTIME_STATE_OWNERS):
        raise ValueError(f"{Path(path).name}: runtime state spans differ")
    return spans


def _parse_field(raw, *, context, page_field, runtime_spans=()):
    required = {
        "name", "width", "source", "kind", "signed", "scale"
    }
    if page_field:
        required |= {"page", "offset", "profiles"}
    _require_keys(raw, required, ("dashboard",), context)
    field = Field(
        name=raw["name"],
        page=raw.get("page"),
        offset=raw.get("offset"),
        width=raw["width"],
        source=raw["source"],
        profiles=tuple(raw.get("profiles", ("tuning",))),
        kind=raw["kind"],
        signed=raw["signed"],
        scale=raw["scale"],
        dashboard=raw.get("dashboard"),
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
            "ecu_ram", "telemetry_state", "runtime_state", "rom_configuration"
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
    if field.kind == "runtime_state" and not any(
        start <= field.source and field.source + field.width <= end
        for start, end in runtime_spans
    ):
        raise ValueError(
            f"{context}: runtime state source is outside the active runtime RAM"
        )
    if page_field:
        if (
            type(field.page) is not int
            or not 0 <= field.page <= 8
            or type(field.offset) is not int
            or not 1 <= field.offset <= 7
            or field.offset + field.width > 8
            or not field.profiles
            or any(name not in PROFILE_NAMES for name in field.profiles)
        ):
            raise ValueError(f"{context}: invalid page placement")
    return field


def _canonical_profile(raw, fields, contexts, protocol_version):
    """Return the wire-layout identity document covered by the profile CRC.

    The document holds what decides the byte placement of a value: protocol
    version, profile ID, page count, the page, offset, width, and signedness of
    every fixed field, and the page, tag, and ordered widths and signedness of
    every context. Field names, context names, scale strings, and producer
    addresses stay outside, so a renamed field or a restated scale keeps the
    CRC. A slot that carries a different quantity takes a new profile ID.
    """
    selected = sorted(
        (
            {
                "page": field.page,
                "offset": field.offset,
                "width": field.width,
                "signed": field.signed,
            }
            for field in fields
            if raw["name"] in field.profiles
        ),
        key=lambda item: (item["page"], item["offset"]),
    )
    context_rows = [
        {
            "page": context.page,
            "tag": context.tag,
            "fields": [
                {"width": field.width, "signed": field.signed}
                for field in context.fields
            ],
        }
        for context in contexts
    ]
    return {
        "protocol_version": protocol_version,
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
        "base_tick_numerator", "pphi_hz", "fixed_page_count",
        "context_pages", "context_count", "header_sequence_bits", "table_address",
        "table_end", "configuration_address", "state_address", "profile",
        "field", "context",
    }
    _require_keys(raw, root_keys, (), path.name)
    if (
        raw["schema_version"] != 2
        or raw["rom"] != "JK08A"
        or raw["protocol_version"] != 2
        or raw["byte_order"] != "big"
        or raw["mailbox"] != 26
        or not 1 <= raw["candidate_can_id"] <= 0x7FE
        or not 1 <= raw["candidate_tick_divisor"] <= 0xFF
        or raw["base_tick_numerator"] != 204800
        or raw["pphi_hz"] != 20_000_000
        or raw["fixed_page_count"] != 9
        or raw["context_pages"] != [9, 10]
        or raw["context_count"] != 5
        or raw["header_sequence_bits"] != 4
        or raw["table_address"] != 0x000D4C00
        or raw["table_end"] != 0x000D4E00
        or raw["configuration_address"] != 0x000D4E00
        or raw["state_address"] != 0xFFFF5E00
    ):
        raise ValueError(f"{path.name}: fixed transport contract differs")

    runtime_spans = _runtime_state_spans()
    fields = tuple(
        _parse_field(
            item,
            context=f"field[{index}]",
            page_field=True,
            runtime_spans=runtime_spans,
        )
        for index, item in enumerate(raw["field"])
    )
    if len({field.name for field in fields}) != len(fields):
        raise ValueError("field names are not unique")

    contexts = []
    for index, item in enumerate(raw["context"]):
        _require_keys(
            item, {"page", "tag", "name", "field"}, (),
            f"context[{index}]",
        )
        context_fields = tuple(
            _parse_field(
                field,
                context=f"context[{index}].field[{field_index}]",
                page_field=False,
                runtime_spans=runtime_spans,
            )
            for field_index, field in enumerate(item["field"])
        )
        context = Context(
            item["page"], item["tag"], item["name"], context_fields
        )
        if (
            type(context.page) is not int
            or context.page not in raw["context_pages"]
            or type(context.tag) is not int
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
    wire_names = [field.name for field in fields]
    wire_names.extend(
        field.name for context in contexts for field in context.fields
    )
    if len(set(wire_names)) != len(wire_names):
        raise ValueError("fixed and context field names are not globally unique")
    expected_context_identity = tuple(
        (page, tag)
        for page in raw["context_pages"]
        for tag in range(raw["context_count"])
    )
    if tuple((item.page, item.tag) for item in contexts) != expected_context_identity:
        raise ValueError(
            "context pages and tags must be ordered as two complete 0 through 4 sets"
        )

    profile_raw = raw["profile"]
    if tuple(item.get("name") for item in profile_raw) != PROFILE_NAMES:
        raise ValueError("profile names or order differ")
    page_count = raw["fixed_page_count"] + len(raw["context_pages"])
    profiles = []
    for index, item in enumerate(profile_raw):
        _require_keys(item, {"name", "id", "page_count"}, (), f"profile[{index}]")
        # The configuration guards compare the sign-extended configuration
        # byte with a signed 8-bit immediate, and the capture always builds
        # every fixed and context page.
        if type(item["id"]) is not int or not 1 <= item["id"] <= 0x7F:
            raise ValueError(f"profile[{index}]: ID is not 1 through 0x7F")
        if item["page_count"] != page_count:
            raise ValueError(
                f"profile[{index}]: page count is not {page_count}, the "
                "fixed and context pages the capture builds"
            )
        canonical = _canonical_profile(item, fields, contexts, raw["protocol_version"])
        encoded = json.dumps(
            canonical, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        profiles.append(Profile(
            item["name"],
            item["id"],
            item["page_count"],
            can_telemetry_schema.crc16_ccitt_false(encoded),
        ))
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
        pphi_hz=raw["pphi_hz"],
        fixed_page_count=raw["fixed_page_count"],
        context_pages=tuple(raw["context_pages"]),
        context_count=raw["context_count"],
        header_sequence_bits=raw["header_sequence_bits"],
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
    for page in range(manifest.fixed_page_count):
        missing = [offset for offset in range(1, 8) if (page, offset) not in occupied]
        if missing:
            raise ValueError(f"page {page} lacks source bytes {missing}")
    for field in manifest.fields:
        for profile_name in field.profiles:
            page_count = manifest.profile_by_name[profile_name].page_count
            if field.page >= page_count:
                raise ValueError(f"{field.name}: field lies outside profile {profile_name}")
    if len(manifest.page_sources) != manifest.fixed_page_count * 7 or any(
        item is None for item in manifest.page_sources
    ):
        raise ValueError("fixed page pointer table is incomplete")


def render_tables(manifest):
    lines = [
        "// Generated from can-telemetry-profile.toml. Do not edit.",
        "// The capture loop consumes 63 fixed page-byte pointers followed by",
        "// two sets of five six-byte context pointer groups.",
        "",
        f".org 0x{manifest.table_address:08X}",
        "telemetry_page_source_table:",
    ]
    for page in range(manifest.fixed_page_count):
        start = page * 7
        values = manifest.page_sources[start : start + 7]
        lines.append(".long " + ", ".join(f"0x{value:08X}" for value in values))
    for page in manifest.context_pages:
        lines.extend(("", f"telemetry_context_page_{page}_source_table:"))
        for context in manifest.contexts_by_page[page]:
            lines.append(
                ".long "
                + ", ".join(
                    f"0x{value:08X}" for value in context.byte_sources
                )
            )
    return "\n".join(lines) + "\n"


def _field_json(field):
    """The host contract of a field: its wire placement, its scale with the
    conversion, unit, candidate flag, values, or named bits that the scale
    states, and its presentation."""
    try:
        terms = can_telemetry_schema.scale_terms(field.scale)
    except ValueError as error:
        raise ValueError(f"{field.name}: {error}") from error
    result = {
        "name": field.name,
        "width": field.width,
        "signed": field.signed,
        "scale": field.scale,
        **terms,
    }
    if field.dashboard is not None:
        result["dashboard"] = field.dashboard
    if field.page is not None:
        result["page"] = field.page
        result["offset"] = field.offset
    return result


def render_schema(manifest):
    document = {
        "schema_version": manifest.schema_version,
        "protocol_version": manifest.protocol_version,
        "byte_order": manifest.byte_order,
        "frame": {
            "format": "standard_11_bit_classical_can",
            "dlc": 8,
            "default_can_id": f"0x{manifest.candidate_can_id:03X}",
            "header": "((tick16 & 0x0f) << 4) | page_id",
        },
        "control": {
            "format": "standard_11_bit_classical_can",
            "dlc": 8,
            "can_id": "data_can_id + 1",
            "maximum_data_can_id": "0x7FE",
            "commands": {
                "start": "54454C320201B632",
                "stop": "54454C320200A613",
            },
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
                        "page": context.page,
                        "tag": context.tag,
                        "name": context.name,
                        "fields": [_field_json(field) for field in context.fields],
                    }
                    for context in manifest.contexts
                ],
            }
            for profile in manifest.profiles
        ],
    }
    try:
        can_telemetry.parse_schema(document)
    except can_telemetry.DecodeError as error:
        raise ValueError(f"the host rejects the rendered schema: {error}") from error
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def render_identity(manifest):
    """Render the header of the wire identity that the configuration guards
    of the capture and control units compare and the harness installs."""
    from patches import can_telemetry

    if len(manifest.profiles) != 1:
        raise ValueError("the configuration guards admit exactly one profile")
    (profile,) = manifest.profiles
    record = can_telemetry.Configuration(
        enabled=True,
        can_id=manifest.candidate_can_id,
        profile=profile.name,
        tick_divisor=manifest.candidate_tick_divisor,
    ).to_bytes(manifest)
    lines = [
        "// Generated from can-telemetry-profile.toml. Do not edit.",
        f"// Wire identity of the {profile.name} profile. The configuration guards of",
        "// can-telemetry-capture.s and can-telemetry-control.s compare the ROM",
        "// configuration record with the integer symbols, and the executable",
        "// harness installs TELEMETRY_CONFIGURATION, the enabled record of the",
        "// candidate CAN ID and tick divisor.",
        "",
        f"#define TELEMETRY_PROFILE_ID 0x{profile.profile_id:02X}",
        f"#define TELEMETRY_PAGE_COUNT 0x{profile.page_count:02X}",
        f"#define TELEMETRY_PROFILE_CRC 0x{profile.crc16:04X}",
        "#define TELEMETRY_CONFIGURATION { "
        + ", ".join(f"0x{value:02X}" for value in record)
        + " }",
    ]
    return "\n".join(lines) + "\n"


def _source_label(field, allocations):
    """The storage that the producer copies a field from: the ECU RAM, the
    active RAM allocation of its runtime, or the ROM configuration."""
    if field.kind in SOURCE_LABELS:
        where = SOURCE_LABELS[field.kind]
    else:
        owners = [
            owner
            for owner, start, end in allocations
            if start <= field.source and field.source + field.width <= end
        ]
        if len(owners) != 1:
            raise ValueError(
                f"{field.name}: source lies in no single active RAM allocation"
            )
        where = f"`{owners[0]}` RAM"
    return f"{where} `0x{field.source:08X}`"


def _slot_cells(field, first_byte, allocations):
    last_byte = first_byte + field.width - 1
    return (
        str(first_byte) if last_byte == first_byte else f"{first_byte}..{last_byte}",
        f"`{field.name}`",
        f"{'s' if field.signed else 'u'}{8 * field.width}",
        _source_label(field, allocations),
        field.scale.replace("|", "\\|"),
    )


def _table_row(cells):
    return "| " + " | ".join(cells) + " |"


def render_specification(manifest, reservations=RESERVATIONS):
    """Render the slot tables of the specification: the byte placement,
    type, exact JK08A source, and scale of every fixed and context field."""
    allocations = _active_ram(reservations)
    lines = [
        "",
        f"Fixed pages 0 through {manifest.fixed_page_count - 1}, bytes 1..7:",
        "",
        "| Page | Bytes | Field | Type | Source | Scale |",
        "| ---: | ---: | --- | --- | --- | --- |",
    ]
    for field in sorted(manifest.fields, key=lambda item: (item.page, item.offset)):
        lines.append(_table_row(
            (str(field.page), *_slot_cells(field, field.offset, allocations))
        ))
    pages = " and ".join(str(page) for page in manifest.context_pages)
    lines.extend((
        "",
        f"Context pages {pages}, bytes 2..7 after the tag in byte 1:",
        "",
        "| Tag | Page | Context | Bytes | Field | Type | Source | Scale |",
        "| ---: | ---: | --- | ---: | --- | --- | --- | --- |",
    ))
    for context in sorted(manifest.contexts, key=lambda item: (item.tag, item.page)):
        first_byte = 2
        for field in context.fields:
            lines.append(_table_row((
                str(context.tag),
                str(context.page),
                f"`{context.name}`",
                *_slot_cells(field, first_byte, allocations),
            )))
            first_byte += field.width
    lines.append("")
    return "\n".join(lines)


def specification_text(manifest, text, reservations=RESERVATIONS):
    """Return `text` with its marked slot section rendered from the manifest."""
    begin = f"<!-- {SPECIFICATION_SECTION}:begin -->"
    end = f"<!-- {SPECIFICATION_SECTION}:end -->"
    start, stop = text.find(begin), text.find(end)
    if start < 0 or stop < start:
        raise ValueError(f"the specification has no markers {begin} {end}")
    start += len(begin)
    return text[:start] + render_specification(manifest, reservations) + text[stop:]


def generate(
    source=DEFAULT_SOURCE,
    tables=DEFAULT_TABLES,
    schema=DEFAULT_SCHEMA,
    identity=DEFAULT_IDENTITY,
    specification=None,
    *,
    check=False,
):
    """Write or check the wire artifacts and, when `specification` names
    it, the slot section of the specification. The assembly gate checks the
    wire artifacts alone; the command line includes the specification."""
    manifest = load_manifest(source)
    outputs = {
        Path(tables): render_tables(manifest),
        Path(schema): render_schema(manifest),
        Path(identity): render_identity(manifest),
    }
    if specification is not None:
        outputs[Path(specification)] = specification_text(
            manifest, Path(specification).read_text(encoding="utf-8")
        )
    stale = []
    for path, content in outputs.items():
        if check:
            try:
                actual = path.read_bytes()
            except OSError:
                actual = None
            if actual != content.encode("utf-8"):
                stale.append(path)
        else:
            path.write_text(content, encoding="utf-8")
    if stale:
        raise ValueError(
            "generated telemetry artifacts are stale: "
            + ", ".join(str(path) for path in stale)
            + f"; regenerate them with {GENERATE_COMMAND}"
        )
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--tables", type=Path, default=DEFAULT_TABLES)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--identity", type=Path, default=DEFAULT_IDENTITY)
    parser.add_argument(
        "--specification", type=Path, default=DEFAULT_SPECIFICATION
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    manifest = generate(
        args.source,
        args.tables,
        args.schema,
        args.identity,
        args.specification,
        check=args.check,
    )
    print(
        "status=PASS"
        f" profiles={len(manifest.profiles)}"
        f" fields={len(manifest.fields)}"
        f" contexts={len(manifest.contexts)}"
        f" table_bytes={len(manifest.page_sources) * 4 + len(manifest.contexts) * 24}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
