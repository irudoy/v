#!/usr/bin/env python3
"""Qualify one built image of one ROM for flashing.

The image qualifies when it is the deterministic build of the registered stock
image of its ROM at HEAD:

- its immutable bytes identify the requested ROM;
- every difference from stock lies inside the calibration ranges, builder
  write sets, or checksum fields, and the checksums are valid;
- it carries no runtime settings that the current profile cannot express, and
  a rebuild from the stock image with the settings and calibration that the
  image carries reproduces it byte for byte;
- the tracked worktree equals HEAD, and the `Verify` workflow of GitHub Actions
  has a green run of the exact HEAD commit. A running, failed, cancelled, or
  missing run refuses the image; runs of other commits do not count.

The command then runs the patch tests of the ROM and the GNU SH-2E gate
restricted to it. It prints its results and writes no tracked file.
"""

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import apply_calibration
from patches import build_rom
from patches import extract_calibration
from patches import rolling_launch
from patches import rom_checksums
from patches import runtime_targets

WORKFLOW = "Verify"
GATE = ROOT / "tools/sh-elf-run/run.sh"
# Patch tests of the builder, calibration transfer, checksums, runtime
# targets, and CAN telemetry; `--rom` deselects the cases of other ROMs.
TESTS = (
    "patches/tests/test_apply_calibration.py",
    "patches/tests/test_build_rom.py",
    "patches/tests/test_calibration_ranges.py",
    "patches/tests/test_can_telemetry.py",
    "patches/tests/test_extract_calibration.py",
    "patches/tests/test_extract_runtime_states.py",
    "patches/tests/test_rom_checksums.py",
    "patches/tests/test_runtime_endpoints.py",
    "patches/tests/test_runtime_targets.py",
    "patches/tests/test_telemetry_can_ids.py",
)


class PreflashError(Exception):
    """The image or the commit does not qualify for flashing."""


@dataclass(frozen=True)
class ImageReport:
    rom: str
    sha256: str
    stock_sha256: str
    runtime: str
    calibration_bytes: int


def _rebuild(stock, target, extraction):
    calibration = extraction.calibration
    states = dict(calibration.source)
    if states["map_switching"] == extract_calibration.ABSENT:
        data = bytearray(stock)
        for element in calibration.elements:
            data[element.address : element.end] = element.data
        return bytes(rom_checksums.recalculate(data, target.checksum_layout)), "absent"
    if states["rolling_launch"] not in ("current", extract_calibration.ABSENT) or (
        states["can_telemetry"] != "current"
    ):
        raise PreflashError(
            "image carries a historical runtime endpoint "
            f"(Rolling Launch {states['rolling_launch']}, CAN telemetry "
            f"{states['can_telemetry']}); rebuild it at HEAD"
        )
    profile = build_rom.Profile(
        name="image settings",
        rom=target.rom,
        calibration=extraction.rolling or rolling_launch.Calibration(),
        telemetry=extraction.telemetry,
        source="image",
        sha256=None,
    )
    try:
        fresh = build_rom.build_image(
            stock, rom=target.rom, profile=profile, source_name=f"{target.rom} stock"
        )
        data = apply_calibration.apply(
            fresh.data, calibration, source_name="rebuilt image"
        ).data
    except (build_rom.BuildError, apply_calibration.ApplicationError) as error:
        raise PreflashError(
            f"image does not rebuild from the {target.rom} stock image: {error}"
        ) from error
    return data, "current"


def check_image(data, rom):
    """Return the report of an image that rebuilds byte for byte at HEAD."""
    data = bytes(data)
    try:
        detected, _detection = build_rom.select_rom(data)
    except build_rom.BuildError as error:
        raise PreflashError(str(error)) from error
    if detected != rom:
        raise PreflashError(f"image identity is {detected}, not {rom}")
    try:
        extraction = extract_calibration.extract(data, rom=rom, source_name="image")
    except extract_calibration.ExtractionError as error:
        raise PreflashError(str(error)) from error
    if extraction.unexpressed:
        raise PreflashError(
            "image carries runtime settings that the current profile cannot express"
        )
    target = runtime_targets.load_runtime_target(rom)
    rebuilt, runtime = _rebuild(target.stock_image.data, target, extraction)
    if rebuilt != data:
        offset = next(
            index for index, pair in enumerate(zip(data, rebuilt)) if pair[0] != pair[1]
        )
        raise PreflashError(f"image differs from its rebuild at {offset:#x}")
    return ImageReport(
        rom=rom,
        sha256=hashlib.sha256(data).hexdigest(),
        stock_sha256=extraction.calibration.stock_sha256,
        runtime=runtime,
        calibration_bytes=sum(
            len(element.data) for element in extraction.calibration.elements
        ),
    )


def _output(command, runner):
    result = runner(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise PreflashError(
            f"{shlex.join(command)} failed: {result.stderr.strip() or result.returncode}"
        )
    return result.stdout


def head_commit(runner=subprocess.run):
    """Return HEAD when the tracked worktree equals it."""
    if _output(["git", "status", "--porcelain", "--untracked-files=no"], runner).strip():
        raise PreflashError("tracked files differ from HEAD; qualify a committed build")
    return _output(["git", "rev-parse", "HEAD"], runner).strip()


def green_run(commit, runner=subprocess.run):
    """Return the successful `Verify` run of exactly this commit."""
    runs = json.loads(_output([
        "gh", "run", "list", "--workflow", WORKFLOW, "--commit", commit,
        "--json", "databaseId,status,conclusion,url", "--limit", "20",
    ], runner))
    if not runs:
        raise PreflashError(f"commit {commit} has no {WORKFLOW} run")
    for run in runs:
        if run["status"] == "completed" and run["conclusion"] == "success":
            return run
    for run in runs:
        if run["status"] != "completed":
            raise PreflashError(
                f"the {WORKFLOW} run of commit {commit} has not finished: {run['url']}"
            )
    run = runs[0]
    raise PreflashError(
        f"the {WORKFLOW} run of commit {commit} concluded {run['conclusion']}: {run['url']}"
    )


def _execute(command, runner, failure):
    print("preflash: " + shlex.join(command), flush=True)
    if runner(command, cwd=ROOT, check=False).returncode != 0:
        raise PreflashError(failure)


def run_tests(rom, pytest, runner=subprocess.run):
    _execute([*pytest, "-q", "--rom", rom, *TESTS], runner, f"the patch tests of {rom} failed")


def run_gate(rom, runner=subprocess.run):
    _execute([str(GATE), "--rom", rom], runner, f"the GNU SH-2E gate of {rom} failed")


def main(argv=None, runner=subprocess.run):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("image", type=Path, help="built image to qualify")
    parser.add_argument("--rom", required=True, choices=runtime_targets.SUPPORTED_ROMS)
    parser.add_argument(
        "--pytest", default="uv run pytest", help="pytest command (default: %(default)s)"
    )
    args = parser.parse_args(argv)
    try:
        try:
            data = args.image.read_bytes()
        except OSError as error:
            raise PreflashError(f"cannot read {args.image}: {error}") from error
        report = check_image(data, args.rom)
        print(
            f"preflash: image rom={report.rom} sha256={report.sha256} "
            f"stock_sha256={report.stock_sha256} runtime={report.runtime} "
            f"calibration_bytes={report.calibration_bytes}",
            flush=True,
        )
        commit = head_commit(runner)
        run = green_run(commit, runner)
        print(f"preflash: commit {commit} {WORKFLOW} {run['url']}", flush=True)
        run_tests(args.rom, shlex.split(args.pytest), runner)
        run_gate(args.rom, runner)
    except PreflashError as error:
        print(f"PREFLASH status=REFUSE rom={args.rom} reason={error}", file=sys.stderr)
        return 1
    print(
        f"PREFLASH status=PASS rom={report.rom} image_sha256={report.sha256} "
        f"stock_sha256={report.stock_sha256} commit={commit} ci_run={run['url']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
