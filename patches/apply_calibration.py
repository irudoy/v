#!/usr/bin/env python3
"""Apply a local calibration file over a fresh stock build.

The input must be byte-identical to a build of the registered stock image of
the calibration file with the settings that its configuration records hold;
the command rebuilds that image in memory and compares every byte. Each
configuration record that the calibration file binds must hold the extracted
settings unless ``--replace-settings`` explicitly replaces them, so a transfer
cannot fall back to the built-in profile unnoticed. The command writes the
calibration elements, derives the Rolling Launch efficiency words from the
resulting F table, and recalculates every checksum. It requires every difference
from the build to lie in calibration ranges, derived efficiency words or
checksum fields, and the output to remain a valid extraction input.

One successful run creates the ROM and its SHA-256, MD5, and JSON manifest
sidecars without overwriting existing files. Outputs must lie outside the
repository or in a path that Git ignores.
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
from patches import calibration_ranges
from patches import can_telemetry
from patches import extract_calibration
from patches import rolling_launch
from patches import rom_checksums
from patches import runtime_targets


MANIFEST_SCHEMA_VERSION = 1
TOOL_NAME = "patches/apply_calibration.py"


class ApplicationError(ValueError):
    """Raised when a calibration cannot be applied to an input image."""


@dataclass(frozen=True)
class Application:
    data: bytes
    rom: str
    calibration: calibration_file.CalibrationFile
    settings: tuple[tuple[str, str], ...]
    input_sha256: str
    input_checksums: dict[str, int]
    output_checksums: dict[str, int]
    changed_bytes: int
    checksum_changed_bytes: int


def sha256(data):
    return hashlib.sha256(bytes(data)).hexdigest()


def md5(data):
    return hashlib.md5(bytes(data)).hexdigest()


def _records(target, data):
    telemetry = target.telemetry_layout.configuration
    records = {"can_telemetry": bytes(data[telemetry.start : telemetry.end])}
    if target.rolling_layout is not None:
        rolling = target.rolling_layout.configuration
        records["rolling_launch"] = bytes(data[rolling.start : rolling.end])
    return records


def _require_fresh_build(source, target, rom, source_name):
    """Rebuild the stock image with the settings of ``source`` and require
    the same bytes."""
    records = _records(target, source)
    try:
        calibration = (
            rolling_launch.Calibration.from_bytes(records["rolling_launch"])
            if "rolling_launch" in records
            else rolling_launch.Calibration()
        )
        telemetry = can_telemetry.Configuration.from_bytes(records["can_telemetry"])
    except (TypeError, ValueError) as error:
        raise ApplicationError(
            f"{source_name}: is not a fresh build of the {rom} stock image: "
            f"{error}"
        ) from error
    if not calibration.is_valid() or not telemetry.is_valid():
        raise ApplicationError(
            f"{source_name}: is not a fresh build of the {rom} stock image: "
            "its configuration records are not current settings"
        )
    profile = build_rom.Profile(
        name="input settings",
        rom=rom,
        calibration=calibration,
        telemetry=telemetry,
        source=source_name,
        sha256=None,
    )
    try:
        fresh = build_rom.build_image(
            target.stock_image.data, rom=rom, profile=profile,
            source_name=f"{rom} stock",
        ).data
    except build_rom.BuildError as error:
        raise ApplicationError(
            f"{source_name}: is not a fresh build of the {rom} stock image: "
            f"{error}"
        ) from error
    if fresh != source:
        differences = [
            offset for offset, (actual, expected) in enumerate(zip(source, fresh))
            if actual != expected
        ]
        checksum_offsets = rom_checksums.checksum_byte_offsets(target.checksum_layout)
        # Checksum fields only follow the edit that made the difference.
        first = next(
            (offset for offset in differences if offset not in checksum_offsets),
            differences[0],
        )
        raise ApplicationError(
            f"{source_name}: is not a fresh build of the {rom} stock image; "
            f"first difference at {first:#x}"
        )
    return records


def _require_misfire_calibration(target, data):
    """Refuse a misfire-latch calibration equal to the spark-cut marker."""
    layout = target.rolling_layout
    if (
        layout is not None
        and layout.hold_actuator
        and data[rolling_launch.MISFIRE_CALIBRATION_ADDRESS]
        == rolling_launch.MISFIRE_MARKER
    ):
        raise ApplicationError(
            f"calibration byte {rolling_launch.MISFIRE_CALIBRATION_ADDRESS:#x} "
            f"equals the Rolling Launch misfire marker "
            f"{rolling_launch.MISFIRE_MARKER:#04x}"
        )


def apply(source, calibration, *, replace_settings=False, source_name="<memory>"):
    """Apply ``calibration`` over the fresh build ``source`` in memory."""
    source = bytes(source)
    rom = calibration.rom
    try:
        selected, _detection = build_rom.select_rom(source)
    except build_rom.BuildError as error:
        raise ApplicationError(str(error)) from error
    if selected != rom:
        raise ApplicationError(
            f"{source_name}: is a {selected} image; the calibration file "
            f"belongs to {rom}"
        )
    target = runtime_targets.load_runtime_target(rom)
    if sha256(target.stock_image.data) != calibration.stock_sha256:
        raise ApplicationError(
            f"calibration file binds stock SHA-256 {calibration.stock_sha256}; "
            f"the registered {rom} stock image differs"
        )
    try:
        input_checksums = rom_checksums.require_valid(
            source, target.checksum_layout, source_name
        ).stored
    except rom_checksums.ChecksumError as error:
        raise ApplicationError(str(error)) from error
    records = _require_fresh_build(source, target, rom, source_name)

    settings = []
    differing = []
    for component, digest in calibration.settings:
        if sha256(records[component]) == digest:
            settings.append((component, "matched"))
        else:
            differing.append(component)
            settings.append((component, "replaced"))
    if differing and not replace_settings:
        raise ApplicationError(
            f"{source_name}: build settings differ from the extracted "
            f"settings: {', '.join(differing)}; build with the extracted "
            "profile or pass --replace-settings to replace them"
        )

    data = bytearray(source)
    for element in calibration.elements:
        data[element.address : element.end] = element.data
    efficiency_offsets = set()
    if target.rolling_layout is not None:
        span = target.rolling_layout.configuration
        rolling = rolling_launch.Calibration.from_bytes(records["rolling_launch"])
        try:
            resolved = build_rom.resolve_trim_efficiency(rolling, data).to_bytes()
        except build_rom.BuildError as error:
            raise ApplicationError(str(error)) from error
        for index in range(rolling_launch.SLOT_COUNT):
            relative = rolling_launch.SLOT_OFFSET + index * 6 + 4
            data[span.start + relative:span.start + relative + 2] = resolved[relative:relative + 2]
            efficiency_offsets.update((span.start + relative, span.start + relative + 1))
    data = bytes(rom_checksums.recalculate(data, target.checksum_layout))
    try:
        output_checksums = rom_checksums.require_valid(
            data, target.checksum_layout, "calibrated output"
        ).stored
    except rom_checksums.ChecksumError as error:
        raise ApplicationError(str(error)) from error

    ranges = calibration_ranges.load(rom)
    permitted = ranges.offsets() | ranges.checksum_offsets | efficiency_offsets
    changed = {
        offset for offset, (before, after) in enumerate(zip(source, data))
        if before != after
    }
    outside = changed - permitted
    if outside:
        raise ApplicationError(
            f"calibrated output changes byte {min(outside):#x} outside the "
            "calibration ranges and checksum fields"
        )
    try:
        extract_calibration.extract(data, rom=rom, source_name="calibrated output")
    except extract_calibration.ExtractionError as error:
        raise ApplicationError(str(error)) from error
    _require_misfire_calibration(target, data)

    return Application(
        data=data,
        rom=rom,
        calibration=calibration,
        settings=tuple(settings),
        input_sha256=sha256(source),
        input_checksums=dict(input_checksums.items()),
        output_checksums=dict(output_checksums.items()),
        changed_bytes=len(changed),
        checksum_changed_bytes=len(changed & ranges.checksum_offsets),
    )


def manifest_data(result, input_path, calibration_path, calibration_sha256, output_path):
    """Return the deterministic JSON manifest payload for one output."""
    calibration = result.calibration
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "rom": result.rom,
        "input": {
            "path": str(Path(input_path).resolve()),
            "sha256": result.input_sha256,
            "checksums": result.input_checksums,
        },
        "calibration": {
            "path": str(Path(calibration_path).resolve()),
            "sha256": calibration_sha256,
            "stock_sha256": calibration.stock_sha256,
            "source": dict(calibration.source),
            "element_count": len(calibration.elements),
            "byte_count": sum(len(item.data) for item in calibration.elements),
            "settings": dict(result.settings),
        },
        "output": {
            "path": str(Path(output_path).resolve()),
            "sha256": sha256(result.data),
            "md5": md5(result.data),
            "checksums": result.output_checksums,
            "changed_bytes": result.changed_bytes,
            "checksum_changed_bytes": result.checksum_changed_bytes,
            "hardware_status": "UNTESTED",
        },
    }


def artifact_contents(result, input_path, calibration_path, calibration_sha256, output_path):
    output_path = Path(output_path)
    manifest = json.dumps(
        manifest_data(
            result, input_path, calibration_path, calibration_sha256, output_path
        ),
        indent=2,
        sort_keys=True,
    ) + "\n"
    return {
        output_path: result.data,
        output_path.with_name(f"{output_path.name}.sha256"): (
            f"{sha256(result.data)} *{output_path.name}\n".encode("ascii")
        ),
        output_path.with_name(f"{output_path.name}.md5"): (
            f"{md5(result.data)} *{output_path.name}\n".encode("ascii")
        ),
        output_path.with_name(f"{output_path.name}.manifest.json"): (
            manifest.encode("utf-8")
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="fresh build of a stock image")
    parser.add_argument(
        "--calibration", type=Path, required=True, help="local calibration file"
    )
    parser.add_argument("--output", type=Path, required=True, help="output ROM path")
    parser.add_argument(
        "--replace-settings",
        action="store_true",
        help="accept build settings that differ from the extracted settings",
    )
    args = parser.parse_args(argv)

    try:
        output_path = calibration_file.require_local_path(args.output)
        if output_path == args.input.resolve():
            parser.error("input and output paths must differ")
        source = args.input.read_bytes()
        calibration_bytes = args.calibration.read_bytes()
        calibration = calibration_file.loads(
            calibration_bytes.decode("utf-8"), str(args.calibration)
        )
        result = apply(
            source,
            calibration,
            replace_settings=args.replace_settings,
            source_name=str(args.input),
        )
        artifacts = artifact_contents(
            result, args.input, args.calibration, sha256(calibration_bytes),
            output_path,
        )
        created = apply_map_switching._publish_artifacts(artifacts, output_path)
    except (
        OSError,
        UnicodeError,
        ApplicationError,
        calibration_file.CalibrationFileError,
        apply_map_switching.PatchError,
    ) as error:
        parser.error(str(error))

    print(f"status=PASS rom={result.rom} input={args.input} input_sha256={result.input_sha256}")
    print(
        f"calibration={args.calibration} elements={len(calibration.elements)} "
        f"settings={','.join(f'{key}:{value}' for key, value in result.settings) or 'none'}"
    )
    print(
        f"output={output_path} status={'created' if created else 'already_exact'} "
        f"sha256={sha256(result.data)} changed_bytes={result.changed_bytes} "
        f"checksum_changed_bytes={result.checksum_changed_bytes}"
    )
    print(f"manifest={output_path.name}.manifest.json hardware_status=UNTESTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
