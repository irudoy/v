#!/usr/bin/env python3
"""Build the JK08A marker-only image for the map-switching flash gate.

The source is locked to the known working tuned ROM. The output changes one
complete 128-byte erased ROM line and the checksum references only. It installs
no hook, pointer table, calibration copy, or executable payload.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import apply_map_switching as file_writer
from patches import jk08a_checksums as checksums
from patches import map_switching_layout as layout_model
from tools.mapkit import rom as romkit


WORKING_BASE_SHA256 = (
    "1bf9978ba1d870216bd85ff69aed25243a77f186231718dcfffd9bb411529471"
)
MARKER_START = 0x000D2280
MARKER_END = 0x000D2300
MARKER_BYTES = bytes(MARKER_END - MARKER_START)


class MarkerError(ValueError):
    """Raised when the source or marker-only output violates the gate."""


@dataclass(frozen=True)
class MarkerResult:
    data: bytes
    source_sha256: str
    output_sha256: str
    marker_sha256: str
    changed_bytes: int
    marker_changed_bytes: int
    checksum_changed_bytes: int
    permitted_write_bytes: int


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def default_output_path(source):
    source = Path(source)
    return source.with_name(f"{source.stem}-marker-only-d2280.bin")


def _require_stock_hooks(layout, data, context):
    for hook in layout.hooks:
        actual = int.from_bytes(
            data[hook.address : hook.address + hook.width],
            layout.byte_order,
        )
        if actual != hook.stock:
            raise MarkerError(
                f"{context}: {hook.key} at {hook.address:#x} is "
                f"{actual:#x}, expected stock {hook.stock:#x}"
            )


def build_image(
    source,
    layout=None,
    source_name="<memory>",
    expected_source_sha256=WORKING_BASE_SHA256,
):
    """Return a checked marker-only image without writing a file."""
    layout = layout or layout_model.load_layout()
    source = bytes(source)
    source_digest = sha256(source)
    if source_digest != expected_source_sha256:
        raise MarkerError(
            f"{source_name}: source sha256 is {source_digest}, expected "
            f"{expected_source_sha256}"
        )

    marker_range = layout_model.AddressRange(
        MARKER_START, MARKER_END, "marker_only_line"
    )
    if marker_range.size != 128 or MARKER_START % 128:
        raise MarkerError("marker range is not one aligned 128-byte line")
    if not layout.claimed_rom.contains(marker_range):
        raise MarkerError("marker range is outside the audited allocation")
    if len(MARKER_BYTES) != marker_range.size or any(MARKER_BYTES):
        raise MarkerError("marker payload must be exactly 128 zero bytes")

    try:
        source_verification = checksums.require_valid(source, source_name)
        image = romkit.Image(layout.rom, source_name, source)
        layout_model.validate_compatible_image(layout, image)
    except (checksums.ChecksumError, ValueError) as error:
        if isinstance(error, MarkerError):
            raise
        raise MarkerError(str(error)) from error

    if source[MARKER_START:MARKER_END] != b"\xff" * marker_range.size:
        raise MarkerError("source marker line is not completely erased")
    _require_stock_hooks(layout, source, source_name)

    marked = bytearray(source)
    marked[MARKER_START:MARKER_END] = MARKER_BYTES
    marked = checksums.recalculate(marked)
    try:
        output_verification = checksums.require_valid(
            marked, "marker-only output"
        )
    except checksums.ChecksumError as error:
        raise MarkerError(str(error)) from error

    if not source_verification.valid or not output_verification.valid:
        raise MarkerError("internal checksum verification did not pass")
    if marked[MARKER_START:MARKER_END] != MARKER_BYTES:
        raise MarkerError("marker payload differs after checksum recalculation")
    _require_stock_hooks(layout, marked, "marker-only output")

    checksum_offsets = checksums.checksum_byte_offsets()
    permitted = set(range(MARKER_START, MARKER_END)) | set(checksum_offsets)
    changed = {
        offset
        for offset, (before, after) in enumerate(zip(source, marked))
        if before != after
    }
    outside = changed - permitted
    if outside:
        raise MarkerError(
            f"marker build changed undeclared byte at {min(outside):#x}"
        )
    marker_changed = sum(
        source[offset] != marked[offset]
        for offset in range(MARKER_START, MARKER_END)
    )
    if marker_changed != marker_range.size:
        raise MarkerError(
            f"marker changed {marker_changed} bytes, expected {marker_range.size}"
        )

    return MarkerResult(
        data=bytes(marked),
        source_sha256=source_digest,
        output_sha256=sha256(marked),
        marker_sha256=sha256(MARKER_BYTES),
        changed_bytes=len(changed),
        marker_changed_bytes=marker_changed,
        checksum_changed_bytes=sum(
            source[offset] != marked[offset] for offset in checksum_offsets
        ),
        permitted_write_bytes=len(permitted),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="exact working base ROM")
    parser.add_argument(
        "--output",
        type=Path,
        help="output path; defaults to INPUT-marker-only-d2280.bin",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="build and verify in memory without writing files",
    )
    args = parser.parse_args(argv)

    try:
        source = args.input.read_bytes()
        result = build_image(source, source_name=str(args.input))
    except (OSError, MarkerError) as error:
        parser.error(str(error))

    print(
        f"status=PASS source={args.input} "
        f"source_sha256={result.source_sha256}"
    )
    print(
        f"marker=[{MARKER_START:#x},{MARKER_END:#x}) "
        f"marker_fill=0x00 marker_sha256={result.marker_sha256}"
    )
    print(
        f"output_sha256={result.output_sha256} "
        f"changed_bytes={result.changed_bytes} "
        f"marker_changed_bytes={result.marker_changed_bytes} "
        f"checksum_changed_bytes={result.checksum_changed_bytes} "
        f"permitted_write_bytes={result.permitted_write_bytes}"
    )
    print("runtime_hooks=stock checksums=PASS")

    if args.verify_only:
        print("no ROM file was written")
        return 0

    output = args.output or default_output_path(args.input)
    if output.resolve() == args.input.resolve():
        parser.error("input and output paths must differ")
    try:
        created = file_writer.write_output(output, result.data)
        file_writer.write_md5_sidecar(output, result.data)
    except (OSError, file_writer.PatchError) as error:
        parser.error(str(error))
    print(f"output={output} status={'created' if created else 'already_exact'}")
    print(f"md5={file_writer.md5(result.data)} sidecar={output.name}.md5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
