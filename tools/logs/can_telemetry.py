#!/usr/bin/env python3
"""Decode ordered custom CAN telemetry groups from a wire schema."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import enum
import json
import math
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.logs import can_telemetry_schema

DEFAULT_SCHEMA = ROOT / "patches" / "can-telemetry-schema.json"
# The frozen host schemas of the historical telemetry endpoints that
# patches/can-telemetry-history.toml binds to their profile identities. A
# decoder accepts the identity of their profiles beside the current one.
HISTORICAL_SCHEMAS = (ROOT / "patches" / "can-telemetry-schema-profile9.json",)
# The command frames that install the dynamic page configurations on JK08A.
DEFAULT_CONFIGURATION_FRAMES = ROOT / "patches" / "can-telemetry-configurations.json"
CANDUMP_COMPACT = re.compile(
    r"(?:^|\s)(?P<can_id>[0-9A-Fa-f]{3})#(?P<data>[0-9A-Fa-f]{16})(?:\s|$)"
)
# The producer keeps tick16 in RAM and resets it with the controller, so a run
# that follows a reset opens with small tick values. A decoder that joined the
# stream late can miss the first groups of that run, so the opening window is
# wider than one tick.
PRODUCER_RUN_TICK_MAX = 0x00FF
# The producer advances tick16 once per 10.24 ms task tick while it streams
# and holds it while streaming is stopped, so the tick never advances faster
# than the receive time.
TICK_SECONDS = 0.01024
# A group whose tick16 falls back after a receive pause longer than this
# opens a new run; within it the group is a reordered or repeated one.
RESTART_GAP_SECONDS = 0.5
# The assumed largest host queue delay of a group: a forward tick step may
# exceed the elapsed receive time by it. Interface timestamps leave the queue
# delay out of the receive time. With host receive times, a longer delay of a
# group followed by lost groups reads as a new run.
QUEUE_TOLERANCE_SECONDS = 1.0
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


class TickStep(enum.Enum):
    """The relation of a group to the previous accepted group of a stream."""

    # The same run, `delta` ticks later.
    FORWARD = "forward"
    # The first group of a new producer run.
    RESTART = "restart"
    # A reordered or repeated group of the same run.
    STALE = "stale"


def tick_step(previous_tick16, tick16, elapsed=None):
    """Classify the tick16 of a group against the previous accepted group.

    ``elapsed`` is the receive time in seconds since that group, or None
    when the input carries no receive times.

    - A step back into the opening window `0..PRODUCER_RUN_TICK_MAX` opens a
      new run: a reset drops the counter there, while a 16-bit wrap keeps the
      forward distance small.
    - A step back after a receive pause longer than RESTART_GAP_SECONDS opens
      a new run whose first received group lies past the opening window;
      within that pause the group is stale. A repeated tick stays stale,
      since STOP holds the tick.
    - A step forward that the elapsed receive time cannot explain, more than
      (elapsed + QUEUE_TOLERANCE_SECONDS) / TICK_SECONDS + 1 ticks, opens a
      new run.

    A receive pause longer than the forward step of a new run cannot be told
    from a continuation of the old run, so such a step stays FORWARD.

    STOP holds the tick, so the next tick after a STOP pause of any length
    stays in the run. A receive loss while the stream runs lets the tick
    advance: after a loss of more than half the 16-bit tick period, about
    335.5 s, the step reads as a step back and opens a false new run, and
    after a loss of more than the full period, about 671 s, it reads as a
    forward step that drops whole periods from the unwrapped tick.
    """
    delta = (tick16 - previous_tick16) & 0xFFFF
    timed = (
        elapsed is not None
        and math.isfinite(elapsed)
        and elapsed >= 0
    )
    if delta >= 0x8000:
        if tick16 <= PRODUCER_RUN_TICK_MAX:
            return TickStep.RESTART
        if timed and elapsed > RESTART_GAP_SECONDS:
            return TickStep.RESTART
        return TickStep.STALE
    if delta == 0:
        return TickStep.STALE
    if timed and delta > (elapsed + QUEUE_TOLERANCE_SECONDS) / TICK_SECONDS + 1:
        return TickStep.RESTART
    return TickStep.FORWARD


def receive_gap(previous_time, time):
    """The receive time between two groups, or None without both times."""
    if previous_time is None or time is None:
        return None
    try:
        gap = float(time) - float(previous_time)
    except (TypeError, ValueError):
        return None
    return gap if math.isfinite(gap) else None


# Consecutive snapshots of a running stream arrive one tick apart within the
# jitter of the interface clock. The tick holds while streaming is stopped, so
# a longer step of recorded time between two snapshots is a stream pause.
STREAM_GAP_SECONDS = 0.1
STREAM_FLOOR_SECONDS = 1.0


def stream_pauses(ticks, times, tick_seconds):
    """Return the recorded pause time that precedes each snapshot.

    STOP holds the tick, so the tick times the snapshots of a running stream
    and does not count a pause. A recorded step longer than STREAM_GAP_SECONDS
    is a candidate. Host queueing only delays a frame, so the floor of recorded
    time less tick time near a candidate is the stream clock there: a pause
    raises it by its duration, while a host stall drained as a burst returns to
    the floor before it. The floor before a candidate spans
    STREAM_FLOOR_SECONDS of ticks, and the floor after it spans the recorded
    step plus STREAM_FLOOR_SECONDS, which reaches past the drained burst. A
    candidate whose floor rises by more than STREAM_GAP_SECONDS is a pause of
    that rise.
    """

    count = len(times)
    lag = [time - tick * tick_seconds for tick, time in zip(ticks, times)]
    candidates = [
        index
        for index in range(1, count)
        if times[index] - times[index - 1] > STREAM_GAP_SECONDS
    ]
    pauses = [0.0] * count
    stream_start = 0
    for position, start in enumerate(candidates):
        end = candidates[position + 1] if position + 1 < len(candidates) else count
        first = start - 1
        while (
            first > stream_start
            and (ticks[start - 1] - ticks[first - 1]) * tick_seconds
            <= STREAM_FLOOR_SECONDS
        ):
            first -= 1
        span = times[start] - times[start - 1] + STREAM_FLOOR_SECONDS
        last = start + 1
        while last < end and (ticks[last] - ticks[start]) * tick_seconds <= span:
            last += 1
        rise = min(lag[start:last]) - min(lag[first:start])
        if rise > STREAM_GAP_SECONDS:
            pauses[start] = rise
            stream_start = start
    return pauses


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
class DynamicLayout:
    """Byte placement of the dynamic page of one profile.

    ``default`` holds the (field, offset) pairs of configuration ID 0 and
    ``configurations`` maps every other ID to its groups of (field, offset)
    pairs. The data bytes after the last slot of a group are zero.
    """

    page: int
    configuration_offset: int
    default: tuple
    configurations: dict


@dataclass(frozen=True)
class Layout:
    """Byte placement of the fields of one profile.

    ``fixed`` holds (field, page, offset) and ``contexts`` maps (page, tag)
    to the context name and its (field, offset) pairs. The data bytes of a
    dynamic page belong to ``dynamic`` and not to ``fixed``.
    """

    fixed: tuple
    contexts: dict
    dynamic: DynamicLayout | None = None


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

    padding = source_profile.get("padding", [])
    if not isinstance(padding, list):
        raise DecodeError(f"{context} padding must be an array")
    context_padding = {}
    for index, row in enumerate(padding):
        if (not isinstance(row, dict) or not {"page", "offset", "width"} <= row.keys()
                or row.keys() - {"page", "offset", "width", "tag"}
                or any(type(row.get(key)) is not int for key in ("page", "offset", "width"))
                or not 0 <= row["page"] < page_count or not 1 <= row["width"] <= 7
                or not 1 <= row["offset"] or row["offset"] + row["width"] > 8):
            raise DecodeError(f"{context}.padding[{index}] has invalid placement")
        if "tag" in row:
            if type(row["tag"]) is not int or not 0 <= row["tag"] <= 0xFF or row["offset"] < 2:
                raise DecodeError(f"{context}.padding[{index}] has invalid context tag")
            context_padding.setdefault((row["page"], row["tag"]), []).append(row)
        else:
            page = row["page"]
            fixed_pages.add(page)
            for offset in range(row["offset"], row["offset"] + row["width"]):
                key = (page, offset)
                if key in occupied:
                    raise DecodeError(f"{context}.padding[{index}] overlaps {occupied[key]}")
                occupied[key] = "reserved zero"

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
        for pad in sorted(context_padding.pop((page, tag), []), key=lambda row: row["offset"]):
            if pad["offset"] != payload_width + 2:
                raise DecodeError(f"{row_context} padding must follow its fields")
            payload_width += pad["width"]
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

    if context_padding:
        raise DecodeError(f"{context} padding names an undefined context")
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
    dynamic = source_profile.get("dynamic")
    if dynamic is not None:
        # The data bytes of the dynamic page precede its configuration byte,
        # an unsigned byte field of the page.
        if (
            not isinstance(dynamic, dict)
            or dynamic.keys() != {"page", "data_bytes", "configuration_offset"}
            or any(type(value) is not int for value in dynamic.values())
            or dynamic["page"] not in fixed_pages
            or dynamic["configuration_offset"] != 7
            or dynamic["data_bytes"] != dynamic["configuration_offset"] - 1
        ):
            raise DecodeError(f"{context} has an invalid dynamic page")
        name = occupied.get((dynamic["page"], dynamic["configuration_offset"]))
        configuration = next(
            (field for field in fields if field["name"] == name), None
        )
        if (
            configuration is None
            or configuration["width"] != 1
            or configuration["signed"]
        ):
            raise DecodeError(
                f"{context} dynamic page lacks an unsigned configuration byte"
            )
    _validate_configurations(source_profile, dynamic, field_names, context)
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


def _validate_configurations(source_profile, dynamic, field_names, context):
    """Validate the slot fields and the configurations of a dynamic page:
    IDs 1..127 with one or two groups of known slots that fit its data
    bytes."""
    slot_fields = source_profile.get("dynamic_fields", [])
    configurations = source_profile.get("configurations", [])
    if not isinstance(slot_fields, list) or not isinstance(configurations, list):
        raise DecodeError(f"{context} dynamic fields and configurations must be arrays")
    if (slot_fields or configurations) and dynamic is None:
        raise DecodeError(f"{context} configures no dynamic page")
    widths = {}
    for index, field in enumerate(slot_fields):
        field_context = f"{context}.dynamic_fields[{index}]"
        _validate_schema_field(field, field_context)
        if "page" in field or "offset" in field:
            raise DecodeError(f"{field_context} must use sequential slot placement")
        if field["name"] in field_names:
            raise DecodeError(f"duplicate field name {field['name']!r}")
        field_names.add(field["name"])
        widths[field["name"]] = field["width"]
    identities = set()
    for index, row in enumerate(configurations):
        row_context = f"{context}.configurations[{index}]"
        groups = row.get("groups") if isinstance(row, dict) else None
        if (
            not isinstance(row, dict)
            or row.keys() != {"id", "name", "label", "groups"}
            or type(row["id"]) is not int
            or not 1 <= row["id"] <= 0x7F
            or not _text(row["name"])
            or not _text(row["label"])
            or not isinstance(groups, list)
            or not 1 <= len(groups) <= 2
        ):
            raise DecodeError(f"{row_context} has an invalid identity")
        if {row["id"], row["name"]} & identities:
            raise DecodeError(f"{row_context} repeats a configuration ID or name")
        identities |= {row["id"], row["name"]}
        for group in groups:
            if (
                not isinstance(group, list)
                or not group
                or not all(isinstance(name, str) for name in group)
                or len(set(group)) != len(group)
                or any(name not in widths for name in group)
                or sum(widths[name] for name in group) > dynamic["data_bytes"]
            ):
                raise DecodeError(
                    f"{row_context} has a group of unknown or repeated slots "
                    "or one wider than the data bytes"
                )


def _profile_layout(profile):
    dynamic = profile.get("dynamic")
    data_bytes = (
        set()
        if dynamic is None
        else {(dynamic["page"], offset) for offset in range(1, dynamic["configuration_offset"])}
    )
    fixed = tuple(
        (field, field["page"], field["offset"])
        for field in profile["fields"]
        if (field["page"], field["offset"]) not in data_bytes
    )
    contexts = {}
    for row in profile["contexts"]:
        contexts[(row["page"], row["tag"])] = (
            row["name"], _sequential(row["fields"], 2)
        )
    if dynamic is None:
        return Layout(fixed, contexts)
    slots = {field["name"]: field for field in profile.get("dynamic_fields", ())}
    default = tuple(
        (field, field["offset"])
        for field in sorted(profile["fields"], key=lambda item: item["offset"])
        if (field["page"], field["offset"]) in data_bytes
    )
    configurations = {
        row["id"]: tuple(
            _sequential([slots[name] for name in group], 1)
            for group in row["groups"]
        )
        for row in profile.get("configurations", ())
    }
    return Layout(fixed, contexts, DynamicLayout(
        dynamic["page"], dynamic["configuration_offset"], default, configurations
    ))


def _sequential(fields, offset):
    """(field, offset) pairs of fields placed one after another."""
    placed = []
    for field in fields:
        placed.append((field, offset))
        offset += field["width"]
    return tuple(placed)


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
        for key in ("conversion", "candidate", "unit", "values", "bits", "field")
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
    if ("unit" in terms or "unit" in terms.get("field", {})) and "unit" in dashboard:
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
    ID, and the CRC16 of the selected profile or of the same profile in a
    historical schema; a group whose health context publishes another
    identity is dropped. The verified identity selects the placement of the
    data bytes, while ``profile`` and ``calibrations`` stay those of the
    selected profile, whose fields the historical profiles share. The
    configuration byte of a dynamic page selects the placement of its data
    bytes; a configuration that the schema does not define as published
    leaves them undecoded.
    """

    def __init__(self, profile, can_id=0x6F0, schema_path=DEFAULT_SCHEMA,
                 historical_schemas=HISTORICAL_SCHEMAS):
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
        self._decoding = self.profile
        self._profiles = {self.expected_identity: self.profile}
        for path in historical_schemas:
            schema, others = load_schema(path)
            other = others.get(profile)
            if other is None:
                continue
            if (
                other["page_count"] != self.page_count
                or other["_context_pages"] != self.context_pages
                or other["_health"] != self._health
            ):
                raise DecodeError(
                    f"{path}: profile {profile!r} places its pages or health context apart"
                )
            identity = (schema["protocol_version"], other["id"], other["_crc16"])
            self._profiles.setdefault(identity, other)
        self._pages = []
        self._sequence = None
        self._last_tick = None
        # The receive time of the last accepted group, or None.
        self._last_time = None
        self._unwrapped_tick = None
        self._run = 0
        self._schema_verified = False
        self.reported_identity = None
        self._identity_run = 0
        self._seen_page_zero = False
        self.incomplete_groups = 0
        self.malformed_frames = 0
        self.schema_mismatches = 0
        self.completed_groups = 0
        self.producer_restarts = 0
        self.unknown_configurations = 0

    @property
    def schema_verified(self):
        return self._schema_verified

    @property
    def expected_identity(self):
        """The selected wire protocol version, profile ID and profile CRC16."""
        return (
            self.schema["protocol_version"], self.profile["id"],
            self.profile["_crc16"],
        )

    @property
    def accepted_identities(self):
        """The identities of the selected profile and its historical forms."""
        return frozenset(self._profiles)

    @property
    def pending_page_count(self):
        """Pages of an unfinished group at the current capture boundary."""
        return len(self._pages)

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
            step = tick_step(
                self._last_tick, tick16, receive_gap(self._last_time, timestamp)
            )
            if step is TickStep.STALE:
                self.malformed_frames += 1
                return None
            if step is TickStep.RESTART:
                run = self._run + 1
                unwrapped = tick16
            else:
                unwrapped = (
                    self._unwrapped_tick + ((tick16 - self._last_tick) & 0xFFFF)
                )
        if run != self._run:
            # A new run republishes its identity on the next health context.
            self._schema_verified = False
        if run != self._identity_run:
            self.reported_identity = None
            self._identity_run = run

        context_tags = {page: pages[page][1] for page in self.context_pages}
        if len(set(context_tags.values())) != 1:
            self.malformed_frames += 1
            return None
        context_tag = next(iter(context_tags.values()))
        for pad in self._decoding.get("padding", ()):
            if "tag" not in pad or pad["tag"] == context_tag:
                if any(pages[pad["page"]][pad["offset"]:pad["offset"] + pad["width"]]):
                    self.malformed_frames += 1
                    return None
        health_page, health_tag = self._health
        if context_tag == health_tag:
            health = {
                field["name"]: _decode_value(
                    pages[health_page], field, offset=offset
                )
                for field, offset in self._health_fields
            }
            self.reported_identity = (
                health["protocol_version"], health["profile_id"],
                health["profile_crc16"],
            )
            decoding = self._profiles.get(self.reported_identity)
            if decoding is None:
                self.schema_mismatches += 1
                self._schema_verified = False
                return None
            self._decoding = decoding
            self._layout = decoding["_layout"]
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
        if self._layout.dynamic is not None:
            self._decode_dynamic(pages, values)

        if run != self._run:
            self._run = run
            self.producer_restarts += 1
        self._last_tick = tick16
        self._last_time = timestamp
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
            profile_id=self._decoding["id"] if self._schema_verified else None,
        )


    def _decode_dynamic(self, pages, values):
        """Decode the data bytes of the dynamic page by the configuration
        and group of its configuration byte."""
        dynamic = self._layout.dynamic
        page = pages[dynamic.page]
        selector = page[dynamic.configuration_offset]
        configuration_id, group = selector & 0x7F, selector >> 7
        if configuration_id == 0:
            groups = (dynamic.default,)
        else:
            groups = dynamic.configurations.get(configuration_id, ())
        placed = groups[group] if group < len(groups) else None
        end = 1
        if placed:
            field, offset = placed[-1]
            end = offset + field["width"]
        if placed is None or any(page[end:dynamic.configuration_offset]):
            self.unknown_configurations += 1
            return
        for field, offset in placed:
            values[field["name"]] = _decode_value(page, field, offset=offset)


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
    """The fixed fields, the context fields, and then the slot fields of the
    dynamic page of one profile."""
    return (
        tuple(profile["fields"])
        + tuple(
            field
            for context in profile["contexts"]
            for field in context["fields"]
        )
        + tuple(profile.get("dynamic_fields", ()))
    )


def configuration_field(profile):
    """The name of the configuration byte of the dynamic page of a profile,
    or None."""
    dynamic = profile.get("dynamic")
    if dynamic is None:
        return None
    return next(
        field["name"]
        for field in profile["fields"]
        if (field["page"], field["offset"])
        == (dynamic["page"], dynamic["configuration_offset"])
    )


def dynamic_field_names(profile):
    """The names of the fields that the dynamic page of a profile carries in
    some configuration: the default fields of its data bytes and the slot
    fields."""
    dynamic = profile.get("dynamic")
    if dynamic is None:
        return frozenset()
    return frozenset(
        field["name"]
        for field in profile["fields"]
        if field["page"] == dynamic["page"]
        and field["offset"] < dynamic["configuration_offset"]
    ) | {field["name"] for field in profile.get("dynamic_fields", ())}


def configuration_labels(profile):
    """The label of every configuration of the dynamic page by ID, with the
    default configuration as ID 0."""
    if profile.get("dynamic") is None:
        return {}
    return {0: "Default"} | {
        row["id"]: row["label"] for row in profile.get("configurations", ())
    }


def configuration_group_counts(profile):
    """The group count of every configuration understood by a parsed profile."""
    dynamic = profile["_layout"].dynamic
    if dynamic is None:
        return {}
    return {0: 1, **{key: len(groups) for key, groups in dynamic.configurations.items()}}


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
        f" producer_restarts={decoder.producer_restarts}"
        f" unknown_configurations={decoder.unknown_configurations}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
