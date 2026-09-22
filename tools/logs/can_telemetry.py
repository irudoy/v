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
    # The profile ID the health context identified for this run, or None
    # while the run has not published an ID the schema declares.
    profile_id: int | None = None


@dataclass(frozen=True)
class Layout:
    """Byte placement of the fields one decoder state reads.

    ``fixed`` holds (field, page, offset) and ``contexts`` maps (page, tag)
    to the context name and its (field, offset) pairs. The layout of an
    identified profile ID reads every field of that ID; the common layout
    reads only the fields that every ID of the profile places, sizes, signs,
    and names identically.
    """

    profile_id: int | None
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
    """Validate a schema document and return it with its current profiles.

    The result maps each profile name to its current profile. The key
    ``_versions`` of a current profile maps every profile ID of that name,
    the current one and each retired one, to its validated profile, and
    ``_common`` holds the layout the IDs share.
    """
    if not isinstance(raw, dict):
        raise DecodeError("telemetry schema root must be an object")
    protocol_version = raw.get("protocol_version")
    frame = raw.get("frame")
    profile_rows = raw.get("profiles")
    retired_rows = raw.get("retired_profiles", [])
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
        or not isinstance(retired_rows, list)
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
        profile["_versions"] = {profile["id"]: profile}
        profiles[profile["name"]] = profile
        profile_ids.add(profile["id"])
    for retired_index, source_profile in enumerate(retired_rows):
        context = f"retired_profile[{retired_index}]"
        profile = _parse_profile(source_profile, context, protocol_version)
        current = profiles.get(profile["name"])
        if current is None or profile["id"] in profile_ids:
            raise DecodeError(
                f"{context} must retire an unused ID of a current profile"
            )
        _require_compatible_version(current, profile, context)
        current["_versions"][profile["id"]] = profile
        profile_ids.add(profile["id"])
    for profile in profiles.values():
        for version in profile["_versions"].values():
            version["_layout"] = _profile_layout(version)
        profile["_common"] = _common_layout(profile["_versions"].values())
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

    profile = dict(source_profile)
    profile["_context_pages"] = tuple(sorted(context_pages))
    profile["_crc16"] = crc16
    profile["_health"] = health
    return profile


def _require_compatible_version(current, retired, context):
    """Require a retired ID to be framed and identified like the current one.

    A decoder assembles a group before its health context names the profile
    ID, so every ID of one profile shares the page count, the context pages
    and tags, and the health context in place and layout.
    """
    if (
        retired["id"] >= current["id"]
        or retired["page_count"] != current["page_count"]
        or retired["_context_pages"] != current["_context_pages"]
        or retired["_health"] != current["_health"]
        or {(row["page"], row["tag"]) for row in retired["contexts"]}
        != {(row["page"], row["tag"]) for row in current["contexts"]}
        or _health_fields(retired) != _health_fields(current)
    ):
        raise DecodeError(
            f"{context} differs from the current profile in framing or health"
        )


def _health_fields(profile):
    page, tag = profile["_health"]
    (row,) = (
        item for item in profile["contexts"]
        if (item["page"], item["tag"]) == (page, tag)
    )
    return [
        (field["name"], field["width"], field["signed"])
        for field in row["fields"]
    ]


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
    return Layout(profile["id"], fixed, contexts)


def _slot(field, page, offset):
    return (field["name"], page, offset, field["width"], field["signed"])


def _common_layout(versions):
    """Return the layout of the fields every profile ID places identically."""
    layouts = [version["_layout"] for version in versions]
    first, others = layouts[0], layouts[1:]
    fixed = tuple(
        item for item in first.fixed
        if all(
            _slot(*item) in {_slot(*other) for other in layout.fixed}
            for layout in others
        )
    )
    contexts = {}
    for key, (name, placed) in first.contexts.items():
        page = key[0]
        shared = tuple(
            (field, offset) for field, offset in placed
            if all(
                _slot(field, page, offset)
                in {
                    _slot(other, page, other_offset)
                    for other, other_offset in layout.contexts[key][1]
                }
                for layout in others
            )
        )
        same_name = all(layout.contexts[key][0] == name for layout in others)
        contexts[key] = (name if same_name else None, shared)
    return Layout(None, fixed, contexts)


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

    A profile name covers its current ID and every retired ID of the schema.
    The health context of a run names the ID, and the decoder then reads the
    layout of that ID; until then it reads only the fields all IDs share.
    """

    def __init__(self, profile, can_id=0x6F0, schema_path=DEFAULT_SCHEMA):
        self.schema, profiles = load_schema(schema_path)
        if profile not in profiles:
            raise DecodeError(f"unknown telemetry profile {profile!r}")
        if type(can_id) is not int or not 1 <= can_id <= 0x7FF:
            raise DecodeError("CAN ID must be a nonzero standard 11-bit ID")
        self.profile = profiles[profile]
        self.versions = self.profile["_versions"]
        self.context_pages = self.profile["_context_pages"]
        self.can_id = can_id
        self.page_count = self.profile["page_count"]
        self._health = self.profile["_health"]
        self._health_fields = self.profile["_layout"].contexts[self._health][1]
        self._pages = []
        self._sequence = None
        self._last_tick = None
        self._unwrapped_tick = None
        self._run = 0
        self._schema_verified = False
        self._active = None
        self._seen_page_zero = False
        self.incomplete_groups = 0
        self.malformed_frames = 0
        self.schema_mismatches = 0
        self.completed_groups = 0
        self.producer_restarts = 0

    @property
    def schema_verified(self):
        return self._schema_verified

    @property
    def active_profile(self):
        """Return the profile the current run identified, or None."""
        return self._active

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
            self._active = None

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
            version = self.versions.get(health["profile_id"])
            if (
                health["protocol_version"] != self.schema["protocol_version"]
                or version is None
                or health["profile_crc16"] != version["_crc16"]
            ):
                self.schema_mismatches += 1
                self._schema_verified = False
                self._active = None
                return None
            self._active = version
            self._schema_verified = True
        layout = (
            self.profile["_common"]
            if self._active is None
            else self._active["_layout"]
        )

        values = {}
        for field, page, offset in layout.fixed:
            values[field["name"]] = _decode_value(
                pages[page], field, offset=offset
            )
        context_names = []
        for page in self.context_pages:
            context = layout.contexts.get((page, context_tag))
            if context is None:
                self.malformed_frames += 1
                return None
            name, placed = context
            context_names.append(name)
            for field, offset in placed:
                values[field["name"]] = _decode_value(
                    pages[page], field, offset=offset
                )
        context_name = (
            None if None in context_names else " + ".join(context_names)
        )

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
            profile_id=None if self._active is None else self._active["id"],
        )


@dataclass(frozen=True)
class Calibration:
    """Affine conversion of one raw telemetry field to engineering units.

    A nonzero ``signed_bits`` first reads the raw value as a two's complement
    integer of that width. It serves a producer value that is signed while
    its wire slot is declared unsigned, and it leaves a value that is already
    negative unchanged.
    """

    target: str
    factor: float = 1.0
    offset: float = 0.0
    signed_bits: int = 0

    def signed(self, raw):
        if self.signed_bits and raw >= 1 << (self.signed_bits - 1):
            return raw - (1 << self.signed_bits)
        return raw

    def apply(self, raw):
        return self.signed(raw) * self.factor + self.offset


RAW_CALIBRATIONS = {
    "rpm_raw": Calibration("rpm", 12.5),
    "maf_b1_raw": Calibration("maf_b1_v", 1 / 200),
    "maf_b2_raw": Calibration("maf_b2_v", 1 / 200),
    "maf_total_raw": Calibration("maf_total_g_s", 1 / 100),
    "bfs_raw": Calibration("bfs_ms", 1 / 2048),
    "af_state_factor_raw": Calibration("af_state_factor", 1 / 16384),
    "intake_cvtc_duty_b1_raw": Calibration(
        "intake_cvtc_duty_b1_percent", 39 / 100
    ),
    "intake_cvtc_duty_b2_raw": Calibration(
        "intake_cvtc_duty_b2_percent", 39 / 100
    ),
    "engine_torque_state_raw": Calibration("engine_torque_state_nm", 0.1),
    "injection_end_angle_raw": Calibration("injection_end_angle_deg", 2, -590),
    "intake_cvtc_duty_command_b1_raw": Calibration(
        "intake_cvtc_duty_command_b1_percent", 39 / 100
    ),
    "intake_cvtc_duty_command_b2_raw": Calibration(
        "intake_cvtc_duty_command_b2_percent", 39 / 100
    ),
    "exhaust_cvtc_duty_b1_word_raw": Calibration(
        "exhaust_cvtc_duty_b1_word_percent", 100 / 1024
    ),
    "exhaust_cvtc_duty_b2_word_raw": Calibration(
        "exhaust_cvtc_duty_b2_word_percent", 100 / 1024
    ),
    "battery_voltage_raw": Calibration("battery_voltage_v", 0.08),
    "intake_cvtc_actual_b1_raw": Calibration(
        "intake_cvtc_actual_b1_deg_ca", 0.5, -64
    ),
    "intake_cvtc_actual_b2_raw": Calibration(
        "intake_cvtc_actual_b2_deg_ca", 0.5, -64
    ),
    "exhaust_cvtc_actual_b1_raw": Calibration(
        "exhaust_cvtc_actual_b1_deg_ca", 0.5, -64
    ),
    "exhaust_cvtc_actual_b2_raw": Calibration(
        "exhaust_cvtc_actual_b2_deg_ca", 0.5, -64
    ),
    "intake_cvtc_target_raw": Calibration(
        "intake_cvtc_target_deg_ca", 0.5, -64
    ),
    "exhaust_cvtc_target_raw": Calibration(
        "exhaust_cvtc_target_deg_ca", 0.5, -64
    ),
    "calculated_load_raw": Calibration("calculated_load_percent", 100 / 255),
    "normalized_load_raw": Calibration("normalized_load_percent", 100 / 128),
    "stft_b1_raw": Calibration("stft_b1_percent", 1 / 256, -100),
    "stft_b2_raw": Calibration("stft_b2_percent", 1 / 256, -100),
    "ltft_b1_raw": Calibration("ltft_b1_percent", 1 / 256, -100),
    "ltft_b2_raw": Calibration("ltft_b2_percent", 1 / 256, -100),
    "ltft_learned_b1_raw": Calibration(
        "ltft_learned_b1_percent", 1 / 256, -100
    ),
    "ltft_adjustment_b1_raw": Calibration(
        "ltft_adjustment_b1_percent", 1 / 256, -100
    ),
    "coolant_raw": Calibration("coolant_deg_c", 1.0, -50),
    "iat_raw": Calibration("iat_deg_c", 1.0, -50),
}
RAW_CALIBRATIONS.update(
    {
        f"injection_{index}_raw": Calibration(f"injection_{index}_ms", 1 / 100)
        for index in range(6)
    }
)


def engineering_values(snapshot):
    """Return only physical transforms explicitly declared by the schema."""
    if not snapshot.schema_verified:
        raise DecodeError("wire schema is not verified for this snapshot")
    raw = snapshot.fields
    return {
        calibration.target: calibration.apply(raw[name])
        for name, calibration in RAW_CALIBRATIONS.items()
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
                row.update(engineering_values(snapshot))
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
