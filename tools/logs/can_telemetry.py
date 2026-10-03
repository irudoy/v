#!/usr/bin/env python3
"""Decode ordered custom CAN telemetry groups from a wire schema."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.logs import can_telemetry_schema

DEFAULT_SCHEMA = ROOT / "patches" / "can-telemetry-schema.json"
CANDUMP_COMPACT = re.compile(
    r"(?:^|\s)(?P<can_id>[0-9A-Fa-f]{3})#(?P<data>[0-9A-Fa-f]{16})(?:\s|$)"
)
# The producer keeps tick16 in RAM and resets it with the controller, so a run
# that follows a reset opens with small tick values. A decoder that joined the
# stream late can miss the first groups of that run, so the opening window is
# wider than one tick.
PRODUCER_RUN_TICK_MAX = 0x00FF
# The keys of the presentation of a field and of its live feed channel.
DASHBOARD_KEYS = frozenset({
    "label", "digits", "unit", "hexadecimal", "group", "panel", "panel_label",
    "order", "description", "feed",
})
FEED_KEYS = frozenset({"key", "name", "format", "minimum", "maximum", "step"})
FEED_KEY = re.compile(r"[a-z][a-z0-9_]*")
# The spelling of a scale unit on a display; a candidate conversion adds an
# asterisk.
DISPLAY_UNITS = {"percent": "%", "ratio": "", "count": "cnt"}


def is_producer_restart(previous_tick16, tick16):
    """Report whether a tick pair crosses a producer reset rather than a wrap.

    A 16-bit wrap keeps the forward distance small, while a reset drops the
    counter back to the opening window of a new run.
    """

    delta = (tick16 - previous_tick16) & 0xFFFF
    return delta >= 0x8000 and tick16 <= PRODUCER_RUN_TICK_MAX


class DecodeError(ValueError):
    """Raised when a selected wire profile or frame is invalid."""


@dataclass(frozen=True)
class Snapshot:
    tick16: int
    run: int
    unwrapped_tick: int
    sequence: int
    fields: dict[str, int]
    context_tag: int | None
    context_name: str | None
    schema_verified: bool
    timestamp: float | None
    # The profile ID the health context of this run verified, or None until
    # the run publishes the identity of the selected profile.
    profile_id: int | None = None


@dataclass(frozen=True)
class Layout:
    """Byte placement of the fields of one profile.

    ``fixed`` holds (field, page, offset) and ``contexts`` maps (page, tag)
    to the context name and its (field, offset) pairs.
    """

    fixed: tuple
    contexts: dict


def load_schema(path=DEFAULT_SCHEMA):
    """Load and validate a wire schema; see ``parse_schema``."""
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DecodeError(f"cannot load telemetry schema {path}: {error}") from error
    return parse_schema(raw)


def parse_schema(raw):
    """Validate a schema document and return it with its profiles by name.

    The key ``_layout`` of each profile holds the byte placement of its
    fields.
    """
    if not isinstance(raw, dict):
        raise DecodeError("telemetry schema root must be an object")
    protocol_version = raw.get("protocol_version")
    frame = raw.get("frame")
    profile_rows = raw.get("profiles")
    if (
        raw.get("schema_version") != 2
        or type(protocol_version) is not int
        or not 0 <= protocol_version <= 0xFF
        or raw.get("byte_order") != "big"
        or not isinstance(frame, dict)
        or frame.get("format") != "standard_11_bit_classical_can"
        or frame.get("dlc") != 8
        or not isinstance(profile_rows, list)
        or not profile_rows
    ):
        raise DecodeError("telemetry schema transport contract differs")

    profiles = {}
    profile_ids = set()
    for profile_index, source_profile in enumerate(profile_rows):
        profile = _parse_profile(
            source_profile, f"profile[{profile_index}]", protocol_version
        )
        if profile["name"] in profiles or profile["id"] in profile_ids:
            raise DecodeError(
                f"profile[{profile_index}] repeats a profile name or ID"
            )
        profile["_layout"] = _profile_layout(profile)
        profiles[profile["name"]] = profile
        profile_ids.add(profile["id"])
    return raw, profiles


def _parse_profile(source_profile, context, protocol_version):
    """Validate one profile object and return a copy with derived keys."""
    if not isinstance(source_profile, dict):
        raise DecodeError(f"{context} must be an object")
    name = source_profile.get("name")
    profile_id = source_profile.get("id")
    page_count = source_profile.get("page_count")
    fields = source_profile.get("fields")
    contexts = source_profile.get("contexts")
    try:
        crc16 = int(source_profile.get("crc16_ccitt_false"), 0)
    except (TypeError, ValueError) as error:
        raise DecodeError(f"{context} has an invalid CRC16") from error
    if (
        not isinstance(name, str)
        or not name
        or type(profile_id) is not int
        or not 0 <= profile_id <= 0xFF
        or type(page_count) is not int
        or not 1 <= page_count <= 16
        or not 0 <= crc16 <= 0xFFFF
        or not isinstance(fields, list)
        or not isinstance(contexts, list)
    ):
        raise DecodeError(f"{context} has an invalid identity")

    occupied = {}
    field_names = set()
    fixed_pages = set()
    for field_index, field in enumerate(fields):
        field_context = f"{context}.fields[{field_index}]"
        _validate_schema_field(field, field_context)
        page = field.get("page")
        offset = field.get("offset")
        width = field["width"]
        if (
            type(page) is not int
            or not 0 <= page < page_count
            or type(offset) is not int
            or not 1 <= offset <= 7
            or offset + width > 8
        ):
            raise DecodeError(f"{field_context} has invalid placement")
        if field["name"] in field_names:
            raise DecodeError(f"duplicate field name {field['name']!r}")
        field_names.add(field["name"])
        fixed_pages.add(page)
        for byte_offset in range(offset, offset + width):
            key = (page, byte_offset)
            if key in occupied:
                raise DecodeError(f"{field_context} overlaps {occupied[key]}")
            occupied[key] = field["name"]

    contexts_by_page = {}
    health_contexts = 0
    health = None
    for context_index, context_row in enumerate(contexts):
        row_context = f"{context}.contexts[{context_index}]"
        if not isinstance(context_row, dict):
            raise DecodeError(f"{row_context} must be an object")
        page = context_row.get("page")
        tag = context_row.get("tag")
        context_name = context_row.get("name")
        context_fields = context_row.get("fields")
        if (
            type(page) is not int
            or not 0 <= page < page_count
            or type(tag) is not int
            or not 0 <= tag <= 0xFF
            or not isinstance(context_name, str)
            or not context_name
            or not isinstance(context_fields, list)
            or not context_fields
        ):
            raise DecodeError(f"{row_context} has an invalid identity")
        page_rows = contexts_by_page.setdefault(page, {})
        if tag in page_rows:
            raise DecodeError(f"{row_context} duplicates page/tag identity")
        page_rows[tag] = context_row
        payload_width = 0
        for field_index, field in enumerate(context_fields):
            field_context = f"{row_context}.fields[{field_index}]"
            _validate_schema_field(field, field_context)
            if "page" in field or "offset" in field:
                raise DecodeError(
                    f"{field_context} must use sequential context placement"
                )
            if field["name"] in field_names:
                raise DecodeError(f"duplicate field name {field['name']!r}")
            field_names.add(field["name"])
            payload_width += field["width"]
        if payload_width != 6:
            raise DecodeError(f"{row_context} must fill six payload bytes")
        if context_name == "health":
            health_contexts += 1
            health = (page, tag)
            required_health = {
                "protocol_version", "profile_id", "profile_crc16"
            }
            if not required_health <= {
                field["name"] for field in context_fields
            }:
                raise DecodeError(f"{row_context} lacks schema identity fields")

    context_pages = set(contexts_by_page)
    if fixed_pages & context_pages:
        raise DecodeError(f"{context} mixes fixed and context page layouts")
    if fixed_pages | context_pages != set(range(page_count)):
        raise DecodeError(f"{context} does not define every page")
    for page in fixed_pages:
        missing = [
            offset for offset in range(1, 8)
            if (page, offset) not in occupied
        ]
        if missing:
            raise DecodeError(f"{context} page {page} lacks bytes {missing}")
    tag_sets = {tuple(sorted(rows)) for rows in contexts_by_page.values()}
    if contexts_by_page and len(tag_sets) != 1:
        raise DecodeError(f"{context} context pages use different tags")
    if not contexts_by_page or health_contexts != 1:
        raise DecodeError(f"{context} must define exactly one health context")
    if (
        can_telemetry_schema.profile_crc16(
            source_profile, protocol_version
        )
        != crc16
    ):
        raise DecodeError(f"{context} CRC16 does not match its wire contract")
    _validate_presentation(profile_fields(source_profile), context)

    profile = dict(source_profile)
    profile["_context_pages"] = tuple(sorted(context_pages))
    profile["_crc16"] = crc16
    profile["_health"] = health
    return profile


def _profile_layout(profile):
    fixed = tuple(
        (field, field["page"], field["offset"]) for field in profile["fields"]
    )
    contexts = {}
    for row in profile["contexts"]:
        placed = []
        offset = 2
        for field in row["fields"]:
            placed.append((field, offset))
            offset += field["width"]
        contexts[(row["page"], row["tag"])] = (row["name"], tuple(placed))
    return Layout(fixed, contexts)


def _validate_schema_field(field, context):
    if not isinstance(field, dict):
        raise DecodeError(f"{context} must be an object")
    name = field.get("name")
    width = field.get("width")
    signed = field.get("signed")
    scale = field.get("scale")
    if (
        not isinstance(name, str)
        or not name
        or type(width) is not int
        or not 1 <= width <= 4
        or type(signed) is not bool
        or not isinstance(scale, str)
        or not scale
    ):
        raise DecodeError(f"{context} has an invalid field contract")
    try:
        terms = can_telemetry_schema.scale_terms(scale)
    except ValueError as error:
        raise DecodeError(f"{context}: {error}") from error
    stated = {
        key: field[key]
        for key in ("conversion", "candidate", "unit", "values", "bits")
        if key in field
    }
    if stated != terms:
        raise DecodeError(
            f"{context} differs from the conversion, unit, values, or bits "
            "of its scale"
        )
    dashboard = field.get("dashboard")
    if dashboard is not None:
        _validate_dashboard(dashboard, terms, f"{context}.dashboard")


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _number(value):
    return type(value) in (int, float)


def _validate_dashboard(dashboard, terms, context):
    """Validate the presentation of one field against the terms of its
    scale: a scale that states a unit leaves the presentation none, and a
    feed channel publishes the value of a conversion."""
    if not isinstance(dashboard, dict) or not set(dashboard) <= DASHBOARD_KEYS:
        raise DecodeError(f"{context} must be an object of presentation keys")
    optional_text = ("unit", "panel", "panel_label", "description")
    if (
        not _text(dashboard.get("label"))
        or not _text(dashboard.get("group"))
        or type(dashboard.get("digits")) is not int
        or not 0 <= dashboard["digits"] <= 9
        or any(
            key in dashboard and not _text(dashboard[key])
            for key in optional_text
        )
        or type(dashboard.get("hexadecimal", False)) is not bool
        or ("order" in dashboard) != ("panel" in dashboard)
        or ("panel_label" in dashboard and "panel" not in dashboard)
        or ("order" in dashboard and type(dashboard["order"]) is not int)
    ):
        raise DecodeError(f"{context} has an invalid presentation")
    if "unit" in terms and "unit" in dashboard:
        raise DecodeError(f"{context} states a unit that the scale states")
    feed = dashboard.get("feed")
    if feed is None:
        return
    if "conversion" not in terms:
        raise DecodeError(
            f"{context}.feed publishes a field without a conversion"
        )
    if (
        not isinstance(feed, dict)
        or set(feed) != FEED_KEYS
        or not isinstance(feed["key"], str)
        or not FEED_KEY.fullmatch(feed["key"])
        or not _text(feed["name"])
        or not _text(feed["format"])
        or not all(
            _number(feed[key]) for key in ("minimum", "maximum", "step")
        )
        or not feed["minimum"] < feed["maximum"]
        or not feed["step"] > 0
    ):
        raise DecodeError(f"{context}.feed has an invalid feed channel")


def _validate_presentation(fields, context):
    """Require the channel labels and the feed keys and names of a profile to
    be unique."""
    seen = {"label": set(), "key": set(), "name": set()}
    for field in fields:
        dashboard = field.get("dashboard")
        if dashboard is None:
            continue
        feed = dashboard.get("feed")
        values = {"label": dashboard["label"]}
        if feed is not None:
            values.update(key=feed["key"], name=feed["name"])
        for key, value in values.items():
            if value in seen[key]:
                raise DecodeError(
                    f"{context} repeats the presentation {key} {value!r}"
                )
            seen[key].add(value)


def _decode_value(payload, field, *, offset=None):
    start = field["offset"] if offset is None else offset
    end = start + field["width"]
    if start < 0 or end > len(payload):
        raise DecodeError(f"field {field['name']} lies outside its frame")
    return int.from_bytes(
        payload[start:end], "big", signed=field["signed"]
    )


class Decoder:
    """Strictly assemble complete, ordered telemetry snapshot groups.

    The health context of a run verifies the protocol version, the profile
    ID, and the CRC16 of the selected profile; a group whose health context
    publishes another identity is dropped.
    """

    def __init__(self, profile, can_id=0x6F0, schema_path=DEFAULT_SCHEMA):
        self.schema, profiles = load_schema(schema_path)
        if profile not in profiles:
            raise DecodeError(f"unknown telemetry profile {profile!r}")
        if type(can_id) is not int or not 1 <= can_id <= 0x7FF:
            raise DecodeError("CAN ID must be a nonzero standard 11-bit ID")
        self.profile = profiles[profile]
        self.context_pages = self.profile["_context_pages"]
        self.can_id = can_id
        self.page_count = self.profile["page_count"]
        self._layout = self.profile["_layout"]
        self._health = self.profile["_health"]
        self._health_fields = self._layout.contexts[self._health][1]
        self.calibrations = calibrations(self.profile)
        self._pages = []
        self._sequence = None
        self._last_tick = None
        self._unwrapped_tick = None
        self._run = 0
        self._schema_verified = False
        self._seen_page_zero = False
        self.incomplete_groups = 0
        self.malformed_frames = 0
        self.schema_mismatches = 0
        self.completed_groups = 0
        self.producer_restarts = 0

    @property
    def schema_verified(self):
        return self._schema_verified

    def _discard(self):
        if self._pages:
            self.incomplete_groups += 1
        self._pages = []
        self._sequence = None

    def feed(self, can_id, payload, timestamp=None):
        """Consume one CAN frame and return a complete snapshot or ``None``."""
        if can_id != self.can_id:
            return None
        payload = bytes(payload)
        if len(payload) != 8:
            self.malformed_frames += 1
            self._discard()
            return None
        page = payload[0] & 0x0F
        sequence = payload[0] >> 4
        if page == 0:
            self._seen_page_zero = True
            self._discard()
            tick16 = int.from_bytes(payload[1:3], "big")
            if tick16 & 0x0F != sequence:
                self.malformed_frames += 1
                return None
            self._pages = [payload]
            self._sequence = sequence
        elif not self._seen_page_zero:
            # A capture or live connection may begin in the tail of a valid
            # group. Wait for page 0 before classifying ordering failures.
            return None
        elif (
            not self._pages
            or sequence != self._sequence
            or page != len(self._pages)
            or page >= self.page_count
        ):
            self.malformed_frames += 1
            self._discard()
            return None
        else:
            self._pages.append(payload)

        if len(self._pages) != self.page_count:
            return None
        pages = tuple(self._pages)
        self._pages = []
        self._sequence = None
        return self._decode_group(pages, timestamp)


    def _decode_group(self, pages, timestamp):
        tick16 = int.from_bytes(pages[0][1:3], "big")
        run = self._run
        if self._last_tick is None:
            unwrapped = tick16
        else:
            delta = (tick16 - self._last_tick) & 0xFFFF
            if delta == 0 or delta >= 0x8000:
                if not is_producer_restart(self._last_tick, tick16):
                    self.malformed_frames += 1
                    return None
                run = self._run + 1
                unwrapped = tick16
            else:
                unwrapped = self._unwrapped_tick + delta
        if run != self._run:
            # A new run republishes its identity on the next health context.
            self._schema_verified = False

        context_tags = {page: pages[page][1] for page in self.context_pages}
        if len(set(context_tags.values())) != 1:
            self.malformed_frames += 1
            return None
        context_tag = next(iter(context_tags.values()))
        health_page, health_tag = self._health
        if context_tag == health_tag:
            health = {
                field["name"]: _decode_value(
                    pages[health_page], field, offset=offset
                )
                for field, offset in self._health_fields
            }
            if (
                health["protocol_version"] != self.schema["protocol_version"]
                or health["profile_id"] != self.profile["id"]
                or health["profile_crc16"] != self.profile["_crc16"]
            ):
                self.schema_mismatches += 1
                self._schema_verified = False
                return None
            self._schema_verified = True

        values = {}
        for field, page, offset in self._layout.fixed:
            values[field["name"]] = _decode_value(
                pages[page], field, offset=offset
            )
        context_names = []
        for page in self.context_pages:
            context = self._layout.contexts.get((page, context_tag))
            if context is None:
                self.malformed_frames += 1
                return None
            name, placed = context
            context_names.append(name)
            for field, offset in placed:
                values[field["name"]] = _decode_value(
                    pages[page], field, offset=offset
                )
        context_name = " + ".join(context_names)

        if run != self._run:
            self._run = run
            self.producer_restarts += 1
        self._last_tick = tick16
        self._unwrapped_tick = unwrapped
        self.completed_groups += 1
        return Snapshot(
            tick16=tick16,
            run=run,
            unwrapped_tick=unwrapped,
            sequence=tick16 & 0x0F,
            fields=values,
            context_tag=context_tag,
            context_name=context_name,
            schema_verified=self._schema_verified,
            timestamp=timestamp,
            profile_id=self.profile["id"] if self._schema_verified else None,
        )


@dataclass(frozen=True)
class Calibration:
    """Affine conversion of one raw telemetry field to engineering units."""

    target: str
    factor: float = 1.0
    offset: float = 0.0

    def apply(self, raw):
        return raw * self.factor + self.offset


def engineering_key(name):
    """The key of the engineering value of a field: its name without the
    ``_raw`` suffix."""
    return name.removesuffix("_raw")


def profile_fields(profile):
    """The fixed fields and then the context fields of one profile."""
    return tuple(profile["fields"]) + tuple(
        field for context in profile["contexts"] for field in context["fields"]
    )


def calibrations(profile):
    """The calibration of every field whose scale states a conversion, by
    field name."""
    return {
        field["name"]: Calibration(
            engineering_key(field["name"]),
            field["conversion"]["factor"],
            field["conversion"]["offset"],
        )
        for field in profile_fields(profile)
        if "conversion" in field
    }


def display_unit(field):
    """The unit a display shows with the value of a field: the unit of its
    scale in display spelling with an asterisk for a candidate conversion,
    or else the unit of its presentation."""
    unit = DISPLAY_UNITS.get(field.get("unit", ""), field.get("unit", ""))
    if field.get("candidate"):
        unit += "*"
    return unit or field.get("dashboard", {}).get("unit", "")


def engineering_values(snapshot, calibrations):
    """The engineering value of every field of a verified snapshot whose
    scale states a conversion, by engineering key."""
    if not snapshot.schema_verified:
        raise DecodeError("wire schema is not verified for this snapshot")
    raw = snapshot.fields
    return {
        calibration.target: calibration.apply(raw[name])
        for name, calibration in calibrations.items()
        if name in raw
    }


def parse_candump_line(line):
    """Parse the compact ``ID#DATA`` form emitted by candump."""
    match = CANDUMP_COMPACT.search(line)
    if match is None:
        return None
    timestamp = None
    stripped = line.lstrip()
    if stripped.startswith("("):
        close = stripped.find(")")
        if close > 1:
            try:
                timestamp = float(stripped[1:close])
            except ValueError:
                timestamp = None
    return int(match.group("can_id"), 16), bytes.fromhex(match.group("data")), timestamp


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, help="candump log; default is stdin")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--profile", default="tuning")
    parser.add_argument("--can-id", type=lambda value: int(value, 0), default=0x6F0)
    args = parser.parse_args(argv)
    decoder = Decoder(args.profile, args.can_id, args.schema)
    source = args.input.open("r", encoding="utf-8") if args.input else sys.stdin
    try:
        for line in source:
            parsed = parse_candump_line(line)
            if parsed is None:
                continue
            snapshot = decoder.feed(*parsed)
            if snapshot is None:
                continue
            row = {
                "tick16": snapshot.tick16,
                "run": snapshot.run,
                "unwrapped_tick": snapshot.unwrapped_tick,
                "timestamp": snapshot.timestamp,
                "context_tag": snapshot.context_tag,
                "context_name": snapshot.context_name,
                "schema_verified": snapshot.schema_verified,
                "profile_id": snapshot.profile_id,
                **snapshot.fields,
            }
            if snapshot.schema_verified:
                row["engineering"] = engineering_values(
                    snapshot, decoder.calibrations
                )
            print(json.dumps(row, sort_keys=True, separators=(",", ":")))
    finally:
        if args.input:
            source.close()
    print(
        "CAN_TELEMETRY_DECODE"
        f" completed={decoder.completed_groups}"
        f" incomplete={decoder.incomplete_groups}"
        f" malformed={decoder.malformed_frames}"
        f" schema_mismatches={decoder.schema_mismatches}"
        f" producer_restarts={decoder.producer_restarts}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
