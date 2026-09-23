#!/usr/bin/env python3
"""Restamp MLVLG field descriptors from the current telemetry field table.

Channel identity, units, and MegaLogViewer scaling live in the header, so a
recorded log adopts corrected calibrations without rewriting its data blocks.
Field types and record layout are preserved; a channel that the current table
does not declare keeps its existing descriptor, and a channel whose name
differs from the current one only by the candidate marker takes its current
name.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import os
from pathlib import Path
import struct
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard import recording
from tools.logs import mlvlg

DEFAULT_PROFILE = "tuning"


@dataclass(frozen=True)
class FieldChange:
    index: int
    before: mlvlg.FieldSpec
    after: mlvlg.FieldSpec


@dataclass(frozen=True)
class RestampSummary:
    path: Path
    fields: int
    changed: tuple[FieldChange, ...]
    unmatched: tuple[str, ...]
    written: bool


def _stored_float(value: float) -> float:
    """Return the value as it survives the 32-bit descriptor encoding."""

    return struct.unpack(">f", struct.pack(">f", value))[0]


def match_key(name: str) -> str:
    """Return the identity a channel keeps across candidate-marker moves."""

    return recording.current_channel_name(name)


def current_bindings(
    profile: str = DEFAULT_PROFILE, schema_path: Path = recording.DEFAULT_SCHEMA
) -> dict[str, recording.FieldBinding]:
    return {
        match_key(binding.spec.name): binding
        for binding in recording.build_bindings(profile, schema_path)
    }


def restamp(
    path: Path,
    *,
    profile: str = DEFAULT_PROFILE,
    schema_path: Path = recording.DEFAULT_SCHEMA,
    dry_run: bool = False,
) -> RestampSummary:
    path = Path(path)
    mlvlg.validate_mlg(path)
    bindings = current_bindings(profile, schema_path)
    data = bytearray(path.read_bytes())
    field_count = struct.unpack(
        ">H", data[22 : mlvlg.MLG_HEADER_SIZE]
    )[0]
    fields = [
        mlvlg.decode_field(
            bytes(data[start : start + mlvlg.MLG_FIELD_SIZE])
        )
        for start in range(
            mlvlg.MLG_HEADER_SIZE,
            mlvlg.MLG_HEADER_SIZE + field_count * mlvlg.MLG_FIELD_SIZE,
            mlvlg.MLG_FIELD_SIZE,
        )
    ]
    targets = [bindings.get(match_key(field.name)) for field in fields]

    changed = []
    unmatched = []
    for index, (before, binding) in enumerate(zip(fields, targets)):
        start = mlvlg.MLG_HEADER_SIZE + index * mlvlg.MLG_FIELD_SIZE
        end = start + mlvlg.MLG_FIELD_SIZE
        if binding is None:
            unmatched.append(before.name)
            continue
        target = binding.spec
        after = replace(
            target,
            field_type=before.field_type,
            scale=_stored_float(target.scale),
            transform=_stored_float(target.transform),
        )
        if after == before:
            continue
        data[start:end] = mlvlg.encode_field(after)
        changed.append(FieldChange(index, before, after))

    written = bool(changed) and not dry_run
    if written:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            mlvlg.validate_mlg(temporary)
            os.replace(temporary, path)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise

    return RestampSummary(
        path=path,
        fields=field_count,
        changed=tuple(changed),
        unmatched=tuple(unmatched),
        written=written,
    )


def _format_change(change: FieldChange) -> str:
    before, after = change.before, change.after
    parts = []
    if before.name != after.name:
        parts.append(f"name {before.name!r} -> {after.name!r}")
    if before.units != after.units:
        parts.append(f"units {before.units!r} -> {after.units!r}")
    if before.scale != after.scale:
        parts.append(f"scale {before.scale:g} -> {after.scale:g}")
    if before.transform != after.transform:
        parts.append(f"transform {before.transform:g} -> {after.transform:g}")
    if before.digits != after.digits:
        parts.append(f"digits {before.digits} -> {after.digits}")
    if before.category != after.category:
        parts.append(f"category {before.category!r} -> {after.category!r}")
    if before.display_style != after.display_style:
        parts.append(
            f"style {before.display_style} -> {after.display_style}"
        )
    return f"  [{change.index:2d}] {after.name}: " + ", ".join(parts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path, help="MLVLG files")
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE,
        help="telemetry profile that declares the field table",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=recording.DEFAULT_SCHEMA,
        help="telemetry wire-schema JSON",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report descriptor changes without writing",
    )
    args = parser.parse_args(argv)

    try:
        for source in args.logs:
            summary = restamp(
                source,
                profile=args.profile,
                schema_path=args.schema,
                dry_run=args.dry_run,
            )
            state = "would update" if args.dry_run else "updated"
            if not summary.changed:
                state = "unchanged"
            print(
                f"{summary.path}: {state}, {len(summary.changed)} of "
                f"{summary.fields} descriptors"
            )
            for change in summary.changed:
                print(_format_change(change))
            if summary.unmatched:
                print(
                    "  undeclared channels kept as recorded: "
                    + ", ".join(summary.unmatched)
                )
    except (mlvlg.MlvlgError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
