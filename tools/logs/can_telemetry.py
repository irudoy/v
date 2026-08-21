#!/usr/bin/env python3
"""Decode ordered JK08A custom CAN telemetry groups from candump text."""

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

from patches import can_telemetry_profile


DEFAULT_SCHEMA = ROOT / "patches" / "can-telemetry-schema.json"
CANDUMP_COMPACT = re.compile(
    r"(?:^|\s)(?P<can_id>[0-9A-Fa-f]{3})#(?P<data>[0-9A-Fa-f]{16})(?:\s|$)"
)


class DecodeError(ValueError):
    """Raised when a selected wire profile or frame is invalid."""


@dataclass(frozen=True)
class Snapshot:
    tick16: int
    unwrapped_tick: int
    sequence: int
    fields: dict[str, int]
    context_tag: int | None
    context_name: str | None
    schema_verified: bool
    timestamp: float | None


def _load_schema(path=DEFAULT_SCHEMA):
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DecodeError(f"cannot load telemetry schema {path}: {error}") from error
    manifest = can_telemetry_profile.load_manifest()
    try:
        profiles = {item["name"]: item for item in raw["profiles"]}
    except (KeyError, TypeError) as error:
        raise DecodeError("generated telemetry schema structure differs") from error
    if (
        raw.get("byte_order") != "big"
        or raw.get("frame", {}).get("dlc") != 8
        or set(profiles) != set(manifest.profile_by_name)
    ):
        raise DecodeError("generated telemetry schema identity differs")
    for name, spec in manifest.profile_by_name.items():
        generated = profiles[name]
        if (
            generated.get("id") != spec.profile_id
            or generated.get("page_count") != spec.page_count
            or generated.get("crc16_ccitt_false") != f"0x{spec.crc16:04X}"
        ):
            raise DecodeError(f"generated profile {name} differs from its source")
    return manifest, profiles


def _decode_value(payload, field, *, offset=None):
    start = field["offset"] if offset is None else offset
    end = start + field["width"]
    if start < 0 or end > len(payload):
        raise DecodeError(f"field {field['name']} lies outside its frame")
    return int.from_bytes(
        payload[start:end], "big", signed=field["signed"]
    )


class Decoder:
    """Strictly assemble complete, ordered telemetry snapshot groups."""

    def __init__(self, profile, can_id=0x6F0, schema_path=DEFAULT_SCHEMA):
        self.manifest, profiles = _load_schema(schema_path)
        if profile not in profiles:
            raise DecodeError(f"unknown telemetry profile {profile!r}")
        if type(can_id) is not int or not 1 <= can_id <= 0x7FF:
            raise DecodeError("CAN ID must be a nonzero standard 11-bit ID")
        self.profile = profiles[profile]
        self.can_id = can_id
        self.page_count = self.profile["page_count"]
        self._pages = []
        self._sequence = None
        self._last_tick = None
        self._unwrapped_tick = None
        self._schema_verified = False
        self._seen_page_zero = False
        self.incomplete_groups = 0
        self.malformed_frames = 0
        self.schema_mismatches = 0
        self.completed_groups = 0

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
        if self._last_tick is None:
            unwrapped = tick16
        else:
            delta = (tick16 - self._last_tick) & 0xFFFF
            if delta == 0 or delta >= 0x8000:
                self.malformed_frames += 1
                return None
            unwrapped = self._unwrapped_tick + delta

        values = {}
        for field in self.profile["fields"]:
            page = field["page"]
            if page >= len(pages):
                raise DecodeError(
                    f"field {field['name']} lies outside profile pages"
                )
            values[field["name"]] = _decode_value(pages[page], field)

        context_tags = {
            page: pages[page][1] for page in self.manifest.context_pages
        }
        if len(set(context_tags.values())) != 1:
            self.malformed_frames += 1
            return None
        context_tag = next(iter(context_tags.values()))
        contexts = {
            (item["page"], item["tag"]): item
            for item in self.profile["contexts"]
        }
        context_names = []
        for page in self.manifest.context_pages:
            context = contexts.get((page, context_tag))
            if context is None:
                self.malformed_frames += 1
                return None
            context_names.append(context["name"])
            offset = 2
            for field in context["fields"]:
                values[field["name"]] = _decode_value(
                    pages[page], field, offset=offset
                )
                offset += field["width"]
            if context["name"] == "health":
                expected = self.manifest.profile_by_name[self.profile["name"]]
                healthy = all((
                    values["protocol_version"]
                    == self.manifest.protocol_version,
                    values["profile_id"] == expected.profile_id,
                    values["profile_crc16"] == expected.crc16,
                ))
                if not healthy:
                    self.schema_mismatches += 1
                    self._schema_verified = False
                    return None
                self._schema_verified = True
        context_name = " + ".join(context_names)

        self._last_tick = tick16
        self._unwrapped_tick = unwrapped
        self.completed_groups += 1
        return Snapshot(
            tick16=tick16,
            unwrapped_tick=unwrapped,
            sequence=tick16 & 0x0F,
            fields=values,
            context_tag=context_tag,
            context_name=context_name,
            schema_verified=self._schema_verified,
            timestamp=timestamp,
        )


def engineering_values(snapshot):
    """Return only physical transforms explicitly declared by the schema."""
    if not snapshot.schema_verified:
        raise DecodeError("wire schema is not verified for this snapshot")
    raw = snapshot.fields
    result = {}
    direct = {
        "rpm_raw": ("rpm", 12.5),
        "maf_b1_raw": ("maf_b1_v", 1 / 200),
        "maf_b2_raw": ("maf_b2_v", 1 / 200),
        "maf_total_raw": ("maf_total_g_s", 1 / 100),
        "bfs_raw": ("bfs_ms", 1 / 2048),
        "af_state_factor_raw": ("af_state_factor", 1 / 16384),
        "intake_cvtc_duty_b1_raw": (
            "intake_cvtc_duty_b1_percent", 100 / 256
        ),
        "intake_cvtc_duty_b2_raw": (
            "intake_cvtc_duty_b2_percent", 100 / 256
        ),
        "engine_torque_state_raw": ("engine_torque_state_nm", 0.1),
        "intake_cvtc_duty_b1_word_raw": (
            "intake_cvtc_duty_b1_word_percent", 100 / 1024
        ),
        "intake_cvtc_duty_b2_word_raw": (
            "intake_cvtc_duty_b2_word_percent", 100 / 1024
        ),
        "exhaust_cvtc_duty_b1_word_raw": (
            "exhaust_cvtc_duty_b1_word_percent", 100 / 1024
        ),
        "exhaust_cvtc_duty_b2_word_raw": (
            "exhaust_cvtc_duty_b2_word_percent", 100 / 1024
        ),
        "battery_voltage_raw": ("battery_voltage_v", 0.08),
    }
    for name, (target, factor) in direct.items():
        if name in raw:
            result[target] = raw[name] * factor
    affine = {
        "intake_cvtc_actual_b1_raw": (
            "intake_cvtc_actual_b1_deg_ca", 0.5, -64
        ),
        "intake_cvtc_actual_b2_raw": (
            "intake_cvtc_actual_b2_deg_ca", 0.5, -64
        ),
        "exhaust_cvtc_actual_b1_raw": (
            "exhaust_cvtc_actual_b1_deg_ca", 0.5, -64
        ),
        "exhaust_cvtc_actual_b2_raw": (
            "exhaust_cvtc_actual_b2_deg_ca", 0.5, -64
        ),
        "intake_cvtc_target_raw": (
            "intake_cvtc_target_deg_ca", 0.5, -64
        ),
        "exhaust_cvtc_target_raw": (
            "exhaust_cvtc_target_deg_ca", 0.5, -64
        ),
        "calculated_load_raw": (
            "calculated_load_percent", 100 / 255, 0
        ),
        "stft_b1_raw": ("stft_b1_percent", 1 / 256, -100),
        "stft_b2_raw": ("stft_b2_percent", 1 / 256, -100),
        "ltft_b1_raw": ("ltft_b1_percent", 1 / 256, -100),
        "ltft_b2_raw": ("ltft_b2_percent", 1 / 256, -100),
    }
    for name, (target, factor, offset) in affine.items():
        if name in raw:
            result[target] = raw[name] * factor + offset
    for index in range(6):
        name = f"injection_{index}_raw"
        if name in raw:
            result[f"injection_{index}_ms"] = raw[name] / 100
    for name, target in (("coolant_raw", "coolant_deg_c"), ("iat_raw", "iat_deg_c")):
        if name in raw:
            result[target] = raw[name] - 50
    return result


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
    parser.add_argument("--profile", choices=("tuning",), default="tuning")
    parser.add_argument("--can-id", type=lambda value: int(value, 0), default=0x6F0)
    args = parser.parse_args(argv)
    decoder = Decoder(args.profile, args.can_id)
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
                "unwrapped_tick": snapshot.unwrapped_tick,
                "timestamp": snapshot.timestamp,
                "context_tag": snapshot.context_tag,
                "context_name": snapshot.context_name,
                "schema_verified": snapshot.schema_verified,
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
        f" schema_mismatches={decoder.schema_mismatches}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
