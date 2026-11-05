#!/usr/bin/env python3
"""Copy the calibration of one map into other maps of a Map Switching image.

For every Map Switching family of the layout of the ROM, the command copies
the slot of the source map over the slot of each target map: Map 1 is the
canonical stock table and Maps 2 through 5 are its copies. It then
recalculates the checksum fields. Every changed byte must lie in a target
slot or a checksum field, and the result must remain an extraction input that
a build of the registered stock image followed by its calibration reproduces
byte for byte. The Rolling Launch flash gates and the commit and CI
qualification remain the responsibility of make preflash. The input is never
overwritten.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import apply_map_switching
from patches import build_rom
from patches import calibration_file
from patches import extract_calibration
from patches import preflash
from patches import rom_checksums
from patches import runtime_targets


class CopyError(ValueError):
    """The maps cannot be copied without changing other facts."""


@dataclass(frozen=True)
class CopyReport:
    """The result of a copy: the families whose target slots changed and
    the number of changed bytes outside the checksum fields."""

    rom: str
    source_map: int
    target_maps: tuple[int, ...]
    families: tuple[str, ...]
    changed_bytes: int
    runtime: str


def target_maps(slot_count, source_map, selected=None):
    """Return the one-based target maps: `selected`, or every other map."""
    maps = range(1, slot_count + 1)
    if source_map not in maps:
        raise CopyError(f"source map {source_map} is not in 1..{slot_count}")
    if selected is None:
        return tuple(index for index in maps if index != source_map)
    selected = tuple(selected)
    if not selected:
        raise CopyError("no target map")
    for index in selected:
        if index not in maps:
            raise CopyError(f"target map {index} is not in 1..{slot_count}")
    if len(set(selected)) != len(selected):
        raise CopyError("target maps repeat")
    if source_map in selected:
        raise CopyError(f"map {source_map} is both the source and a target")
    return tuple(sorted(selected))


def slot_range(family, index):
    """Return the address range of the one-based map `index` of `family`."""
    start = family.slot_address(index - 1)
    return start, start + family.byte_length


def copy_slots(data, layout, source_map, maps):
    """Return `data` with the source slot of every family over each target."""
    data = bytearray(data)
    for family in layout.families:
        start, end = slot_range(family, source_map)
        table = bytes(data[start:end])
        for index in maps:
            start, end = slot_range(family, index)
            data[start:end] = table
    return bytes(data)


def _require_rebuild(data, rom, target):
    """Return the runtime state of an extraction input that rebuilds."""
    extraction = extract_calibration.extract(data, rom=rom, source_name="output")
    if extraction.unexpressed:
        raise CopyError(
            "image carries runtime settings that the current profile cannot express"
        )
    rebuilt, runtime = preflash._rebuild(target.stock_image.data, target, extraction)
    if rebuilt != data:
        offset = next(
            index for index, pair in enumerate(zip(data, rebuilt)) if pair[0] != pair[1]
        )
        raise CopyError(f"image differs from its rebuild at {offset:#x}")
    return runtime


def copy_image(source, source_map, maps=None):
    """Return the copied image and its CopyReport."""
    source = bytes(source)
    try:
        rom, _ = build_rom.select_rom(source)
        target = runtime_targets.load_runtime_target(rom)
        extraction = extract_calibration.extract(source, rom=rom, source_name="input")
        state = dict(extraction.calibration.source)["map_switching"]
        if state != "current":
            raise CopyError(
                f"image carries Map Switching state {state!r}; copying maps "
                "requires the current runtime"
            )
        layout = target.map_layout
        maps = target_maps(layout.slot_count, source_map, maps)
        data = rom_checksums.recalculate(
            copy_slots(source, layout, source_map, maps), target.checksum_layout
        )
        data = bytes(data)
        allowed = {
            offset
            for family in layout.families
            for index in maps
            for offset in range(*slot_range(family, index))
        }
        checksum = set(rom_checksums.checksum_byte_offsets(target.checksum_layout))
        changed = {
            index for index, pair in enumerate(zip(source, data)) if pair[0] != pair[1]
        }
        outside = changed - allowed - checksum
        if outside:
            raise CopyError(
                f"changed byte {min(outside):#x} lies outside the target slots"
            )
        families = tuple(
            family.key
            for family in layout.families
            if any(
                source[start:end] != data[start:end]
                for start, end in (slot_range(family, index) for index in maps)
            )
        )
        runtime = _require_rebuild(data, rom, target)
    except (
        build_rom.BuildError,
        extract_calibration.ExtractionError,
        preflash.PreflashError,
        runtime_targets.RuntimeTargetError,
        ValueError,
    ) as error:
        if isinstance(error, CopyError):
            raise
        raise CopyError(str(error)) from error
    return data, CopyReport(
        rom=rom,
        source_map=source_map,
        target_maps=maps,
        families=families,
        changed_bytes=len(changed - checksum),
        runtime=runtime,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--source-map", type=int, required=True,
                        help="one-based map whose slots are copied")
    parser.add_argument("--target-maps", type=int, nargs="+",
                        help="one-based maps to overwrite; defaults to every other map")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        output = calibration_file.require_local_path(args.output)
        if output == args.input.resolve():
            raise CopyError("input and output paths must differ")
        source = args.input.read_bytes()
        data, report = copy_image(source, args.source_map, args.target_maps)
        digest = hashlib.sha256(data).hexdigest()
        manifest = dict(
            schema_version=1, tool="patches/copy_map_slot.py", rom=report.rom,
            source_map=report.source_map, target_maps=list(report.target_maps),
            families=list(report.families), changed_bytes=report.changed_bytes,
            input=str(args.input), input_sha256=hashlib.sha256(source).hexdigest(),
            output=str(output), output_sha256=digest, hardware_status="UNTESTED",
        )
        artifacts = {
            output: data,
            Path(str(output) + ".sha256"): f"{digest} *{output.name}\n".encode(),
            Path(str(output) + ".md5"): f"{hashlib.md5(data).hexdigest()} *{output.name}\n".encode(),
            Path(str(output) + ".manifest.json"): (json.dumps(manifest, indent=2) + "\n").encode(),
        }
        apply_map_switching._publish_artifacts(artifacts, output)
    except (OSError, CopyError, calibration_file.CalibrationFileError,
            apply_map_switching.PatchError) as error:
        parser.error(str(error))
    print(
        f"status=PASS rom={report.rom} source_map={report.source_map} "
        f"target_maps={','.join(map(str, report.target_maps))} "
        f"families={len(report.families)} changed_bytes={report.changed_bytes} "
        f"output={output} sha256={digest} hardware_status=UNTESTED"
    )
    for key in report.families:
        print(f"family={key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
