#!/usr/bin/env python3
"""Derive the byte locks of the canonical CAN telemetry layout from its payloads.

The layout locks every assembly unit by the SHA-256 of its fill-aware blob,
its instruction count and its data-byte count, and locks the default
composition by its SHA-256. Every value follows from the unit sources, the
assembled blobs and the Rolling Launch base, so an intentional source change
derives its locks instead of computing them by hand. Rendering rewrites only
these values in the layout text and keeps every other byte of the file.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
from pathlib import Path
import re
import sys
import tempfile
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import can_telemetry_compose
from patches import can_telemetry_layout
from patches import map_switching_assembly as common


ZERO_SHA256 = "0" * 64
COMPOSITION_FIELD = "expected_composition_sha256"
UNIT_FIELDS = ("expected_sha256", "instruction_count", "data_bytes")
SHA256_VALUE = r'"[0-9a-f]{64}"'
COUNT_VALUE = r"[0-9]+"
_FIELD_VALUES = {
    COMPOSITION_FIELD: SHA256_VALUE,
    "expected_sha256": SHA256_VALUE,
    "instruction_count": COUNT_VALUE,
    "data_bytes": COUNT_VALUE,
}
_TABLE_RE = re.compile(r"\s*(\[\[?)\s*([A-Za-z0-9_.]+)\s*\]\]?\s*(?:#.*)?")
_FIELD_RE = re.compile(r"(\s*([A-Za-z0-9_]+)\s*=\s*)(.*?)(\s*(?:#.*)?)")
_UNIT_KEY_RE = re.compile(r'\s*key\s*=\s*"([^"]+)"\s*(?:#.*)?')


class LockError(ValueError):
    """Raised when telemetry locks cannot be derived or rendered."""


@dataclass(frozen=True)
class UnitLock:
    key: str
    expected_sha256: str
    instruction_count: int
    data_bytes: int


@dataclass(frozen=True)
class Locks:
    units: tuple[UnitLock, ...]
    expected_composition_sha256: str

    @property
    def unit_by_key(self):
        return {item.key: item for item in self.units}


def sha256(data):
    return hashlib.sha256(bytes(data)).hexdigest()


def locks_of(layout):
    """Return the locks that ``layout`` declares."""
    return Locks(
        units=tuple(
            UnitLock(
                key=unit.key,
                expected_sha256=unit.expected_sha256,
                instruction_count=unit.instruction_count,
                data_bytes=unit.data_bytes,
            )
            for unit in layout.assembly_units
        ),
        expected_composition_sha256=layout.expected_composition_sha256,
    )


def apply(layout, locks):
    """Return ``layout`` with every lock value taken from ``locks``."""
    by_key = locks.unit_by_key
    if set(by_key) != set(layout.assembly_unit_by_key) or len(by_key) != len(locks.units):
        raise LockError(
            f"lock units {sorted(by_key)} differ from the layout units "
            f"{sorted(layout.assembly_unit_by_key)}"
        )
    return replace(
        layout,
        assembly_units=tuple(
            replace(
                unit,
                expected_sha256=by_key[unit.key].expected_sha256,
                instruction_count=by_key[unit.key].instruction_count,
                data_bytes=by_key[unit.key].data_bytes,
            )
            for unit in layout.assembly_units
        ),
        expected_composition_sha256=locks.expected_composition_sha256,
    )


def counted(layout):
    """Return ``layout`` with the instruction and data-byte counts of each
    unit taken from its source, before any source validator compares them."""
    source_dir = can_telemetry_layout.DEFAULT_MANIFEST.parent
    source_texts = layout.source_text_by_unit
    units = []
    for unit in layout.assembly_units:
        source_path = source_dir / unit.source
        source = source_texts.get(unit.key)
        if source is None:
            source = source_path.read_text(encoding="utf-8")
        parsed = common.parse_source_text(
            source, source_path, unit.span.start, unit.span.end
        )
        units.append(replace(
            unit,
            instruction_count=parsed.instruction_count,
            data_bytes=parsed.data_bytes,
        ))
    return replace(layout, assembly_units=tuple(units))


def derive(layout, parsed_by_unit, blobs, base=None):
    """Derive the locks of independently assembled ``blobs``.

    ``parsed_by_unit`` holds the validated unit sources. The composition lock
    is the SHA-256 of the default composition over ``base``, which defaults to
    the tracked Rolling Launch composition.
    """
    expected = set(layout.assembly_unit_by_key)
    for name, values in (("blob", blobs), ("parsed source", parsed_by_unit)):
        if set(values) != expected:
            raise LockError(
                f"{name} set differs; missing={sorted(expected - set(values))}; "
                f"extra={sorted(set(values) - expected)}"
            )
    units = []
    for unit in layout.assembly_units:
        blob = bytes(blobs[unit.key])
        if len(blob) != unit.span.size:
            raise LockError(
                f"{unit.key}: blob has {len(blob)} bytes, expected {unit.span.size}"
            )
        parsed = parsed_by_unit[unit.key]
        units.append(UnitLock(
            key=unit.key,
            expected_sha256=sha256(blob),
            instruction_count=parsed.instruction_count,
            data_bytes=parsed.data_bytes,
        ))
    unit_locked = apply(layout, Locks(tuple(units), ZERO_SHA256))
    # A zero composition lock leaves the default composition unchecked, so
    # compose validates the sources, instructions and write set alone.
    composition = can_telemetry_compose.compose(
        layout=unit_locked, base=base, blobs=blobs
    )
    return Locks(tuple(units), composition.sha256)


def changes(layout, locks):
    """Return ``(field, declared, derived)`` for each lock that differs."""
    result = []
    declared = locks_of(layout)
    for unit in declared.units:
        derived = locks.unit_by_key[unit.key]
        for field in UNIT_FIELDS:
            before = getattr(unit, field)
            after = getattr(derived, field)
            if before != after:
                result.append((f"{unit.key}.{field}", before, after))
    if declared.expected_composition_sha256 != locks.expected_composition_sha256:
        result.append((
            COMPOSITION_FIELD,
            declared.expected_composition_sha256,
            locks.expected_composition_sha256,
        ))
    return tuple(result)


def _encoded(field, value):
    return f'"{value}"' if _FIELD_VALUES[field] == SHA256_VALUE else str(value)


def _rewrite(line, field, value, context):
    match = _FIELD_RE.fullmatch(line)
    if not re.fullmatch(_FIELD_VALUES[field], match.group(3)):
        raise LockError(f"{context}: {field} is not a literal lock value")
    return match.group(1) + _encoded(field, value) + match.group(4)


def render(text, locks, context="can-telemetry-layout.toml"):
    """Return the layout ``text`` with every lock value from ``locks``.

    Each lock field must occur exactly once in its table; every other byte of
    the text is kept.
    """
    by_key = locks.unit_by_key
    lines = text.splitlines(keepends=True)
    output = []
    table = None
    unit = None
    seen = {}
    for number, raw in enumerate(lines, 1):
        body = raw.rstrip("\r\n")
        ending = raw[len(body):]
        header = _TABLE_RE.fullmatch(body)
        if header:
            table = (
                header.group(2) if header.group(1) == "[[" else f"[{header.group(2)}]"
            )
            unit = None
            output.append(raw)
            continue
        if table == "assembly_unit":
            key = _UNIT_KEY_RE.fullmatch(body)
            if key:
                unit = key.group(1)
                if unit not in by_key:
                    raise LockError(f"{context}:{number}: unit {unit!r} has no lock")
                if unit in seen:
                    raise LockError(f"{context}:{number}: unit {unit!r} is declared twice")
                seen[unit] = set()
                output.append(raw)
                continue
        field = _FIELD_RE.fullmatch(body)
        name = field.group(2) if field else None
        if table is None and name == COMPOSITION_FIELD:
            if COMPOSITION_FIELD in seen.setdefault(None, set()):
                raise LockError(f"{context}:{number}: {name} is declared twice")
            seen[None].add(name)
            body = _rewrite(body, name, locks.expected_composition_sha256, f"{context}:{number}")
        elif table == "assembly_unit" and name in UNIT_FIELDS:
            if unit is None:
                raise LockError(
                    f"{context}:{number}: {name} precedes the unit key"
                )
            if name in seen[unit]:
                raise LockError(f"{context}:{number}: {unit}.{name} is declared twice")
            seen[unit].add(name)
            body = _rewrite(
                body, name, getattr(by_key[unit], name), f"{context}:{number}"
            )
        output.append(body + ending)
    if COMPOSITION_FIELD not in seen.get(None, ()):
        raise LockError(f"{context}: {COMPOSITION_FIELD} is not declared")
    missing_units = sorted(set(by_key) - set(seen) - {None})
    if missing_units:
        raise LockError(f"{context}: locked units {missing_units} are not declared")
    for key, fields in seen.items():
        if key is not None and fields != set(UNIT_FIELDS):
            raise LockError(
                f"{context}: unit {key!r} lacks {sorted(set(UNIT_FIELDS) - fields)}"
            )
    rendered = "".join(output)
    _require_lock_fields_only(text, rendered, locks, context)
    return rendered


def _require_lock_fields_only(text, rendered, locks, context):
    """Require the parsed tables to differ in the lock values alone."""
    expected = tomllib.loads(text)
    expected[COMPOSITION_FIELD] = locks.expected_composition_sha256
    for item in expected["assembly_unit"]:
        lock = locks.unit_by_key[item["key"]]
        for field in UNIT_FIELDS:
            item[field] = getattr(lock, field)
    if tomllib.loads(rendered) != expected:
        raise LockError(f"{context}: rendering changes fields other than the locks")


def load_text(text, name=can_telemetry_layout.DEFAULT_MANIFEST.name):
    """Load and validate a layout from ``text``."""
    with tempfile.TemporaryDirectory(prefix="vq-telemetry-locks-") as directory:
        path = Path(directory) / name
        path.write_text(text, encoding="utf-8")
        return can_telemetry_layout.load_layout(path)
