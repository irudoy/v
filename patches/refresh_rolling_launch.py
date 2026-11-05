#!/usr/bin/env python3
"""Derive Rolling Launch slot efficiencies after calibration-editor changes.

Only the derived efficiency words and checksum fields are rewritten. The
result must pass the preflash image rebuild check; commit and CI qualification
remain the responsibility of make preflash. The input is never overwritten.
"""

from __future__ import annotations

import argparse
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
from patches import preflash
from patches import rolling_launch
from patches import rom_checksums
from patches import runtime_targets


class RefreshError(ValueError):
    """The image cannot be normalized without changing independent facts."""


def refresh(source):
    source = bytes(source)
    try:
        rom, _ = build_rom.select_rom(source)
        target = runtime_targets.load_runtime_target(rom)
        if target.rolling_layout is None:
            raise RefreshError(f"{rom} has no Rolling Launch configuration")
        span = target.rolling_layout.configuration
        calibration = rolling_launch.Calibration.from_bytes(source[span.start:span.end])
        resolved = build_rom.resolve_trim_efficiency(calibration, source)
        if not resolved.is_valid():
            raise RefreshError("Rolling Launch settings are invalid after deriving efficiency")
        encoded = resolved.to_bytes()
        data = bytearray(source)
        for index in range(rolling_launch.SLOT_COUNT):
            relative = rolling_launch.SLOT_OFFSET + index * 6 + 4
            data[span.start + relative:span.start + relative + 2] = encoded[relative:relative + 2]
        data = bytes(rom_checksums.recalculate(data, target.checksum_layout))
        # Reject unknown payloads, partial runtimes, illegal calibration writes,
        # and an image that a stock build plus calibration cannot reproduce.
        report = preflash.check_image(data, rom)
    except (build_rom.BuildError, preflash.PreflashError, ValueError) as error:
        raise RefreshError(str(error)) from error
    return data, report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        output = calibration_file.require_local_path(args.output)
        if output == args.input.resolve():
            raise RefreshError("input and output paths must differ")
        source = args.input.read_bytes()
        data, report = refresh(source)
        digest = hashlib.sha256(data).hexdigest()
        manifest = dict(
            schema_version=1, tool="patches/refresh_rolling_launch.py", rom=report.rom,
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
    except (OSError, RefreshError, calibration_file.CalibrationFileError,
            apply_map_switching.PatchError) as error:
        parser.error(str(error))
    print(f"status=PASS rom={report.rom} output={output} sha256={digest} hardware_status=UNTESTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
