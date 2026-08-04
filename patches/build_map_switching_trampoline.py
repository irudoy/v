#!/usr/bin/env python3
"""Build the JK08A minimal startup-trampoline hardware gate.

The source is locked to the successful marker-only hardware readback. The
output changes only the startup initializer pointer, a 12-byte transparent
tail trampoline, and checksum references. It writes no RAM and installs none
of the remaining map-switching hooks or payloads.
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
from patches import map_switching_assembly as assembly
from patches import map_switching_layout as layout_model


HARDWARE_READBACK_SHA256 = (
    "d5cb0000f77c8c1112d912474cbb471f78051805027e3358fbedc28cf1bf58b3"
)
ROM_SIZE = 0x100000
RESET_SELECTOR_LINE_START = 0x00008080
RESET_SELECTOR_LINE_END = 0x00008100
MARKER_LINE_START = 0x000D2280
MARKER_LINE_END = 0x000D2300
TRAMPOLINE_START = 0x000D22A0
TRAMPOLINE_END = 0x000D22AC
STOCK_INITIALIZER = 0x0002C648
TRAMPOLINE_SOURCE = Path(__file__).with_name(
    "map-switching-startup-trampoline.s"
)
TRAMPOLINE_BLOB = bytes.fromhex("d001402b000900000002c648")
TRAMPOLINE_SHA256 = (
    "5e3e791f1a0d302b905db989c9a646440a69fe531921a246a21f3082712eb603"
)


class TrampolineError(ValueError):
    """Raised when the source or trampoline output violates the gate."""


@dataclass(frozen=True)
class TrampolineResult:
    data: bytes
    source_sha256: str
    output_sha256: str
    trampoline_sha256: str
    changed_bytes: int
    hook_changed_bytes: int
    trampoline_changed_bytes: int
    checksum_changed_bytes: int
    permitted_write_bytes: int


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def default_output_path(source):
    source = Path(source)
    return source.with_name(
        f"{source.stem}-startup-trampoline-d22a0.bin"
    )


def _startup_hook(layout):
    hooks = {hook.key: hook for hook in layout.hooks}
    try:
        hook = hooks["startup_initializer"]
    except KeyError as error:
        raise TrampolineError("layout has no startup initializer hook") from error
    if (
        hook.address != 0x00027D28
        or hook.width != 4
        or hook.stock != STOCK_INITIALIZER
        or hook.replacement != TRAMPOLINE_START
    ):
        raise TrampolineError("layout startup initializer hook differs")
    return hook


def _require_trampoline_contract():
    if len(TRAMPOLINE_BLOB) != TRAMPOLINE_END - TRAMPOLINE_START:
        raise TrampolineError("trampoline blob length differs")
    if sha256(TRAMPOLINE_BLOB) != TRAMPOLINE_SHA256:
        raise TrampolineError("trampoline blob SHA-256 differs")
    try:
        parsed = assembly.parse_source(
            TRAMPOLINE_SOURCE,
            TRAMPOLINE_START,
            TRAMPOLINE_END,
        )
    except (OSError, ValueError) as error:
        raise TrampolineError(str(error)) from error
    expected_labels = {
        "startup_trampoline": TRAMPOLINE_START,
        "startup_stock_initializer": 0x000D22A8,
    }
    if parsed.labels != expected_labels:
        raise TrampolineError("trampoline source labels differ")
    expected_statements = (
        (
            0x000D22A0,
            "instruction",
            "mov.l @(startup_stock_initializer,pc),r0",
            2,
        ),
        (0x000D22A2, "instruction", "jmp @r0", 2),
        (0x000D22A4, "instruction", "nop", 2),
        (0x000D22A8, "long", "0x0002C648", 4),
    )
    actual_statements = tuple(
        (item.address, item.kind, item.text, item.size)
        for item in parsed.statements
    )
    if actual_statements != expected_statements:
        raise TrampolineError("trampoline source statements differ")
    return parsed


def _require_hooks(layout, data, context, startup_replaced):
    startup = _startup_hook(layout)
    for hook in layout.hooks:
        actual = int.from_bytes(
            data[hook.address : hook.address + hook.width],
            layout.byte_order,
        )
        expected = (
            startup.replacement
            if startup_replaced and hook.key == startup.key
            else hook.stock
        )
        if actual != expected:
            raise TrampolineError(
                f"{context}: {hook.key} at {hook.address:#x} is "
                f"{actual:#x}, expected {expected:#x}"
            )


def _require_stock_anchors(layout, data, context):
    for anchor in layout.anchors:
        actual = int.from_bytes(
            data[anchor.address : anchor.address + anchor.width],
            layout.byte_order,
        )
        if actual != anchor.value:
            raise TrampolineError(
                f"{context}: {anchor.key} at {anchor.address:#x} is "
                f"{actual:#x}, expected {anchor.value:#x}"
            )


def build_image(
    source,
    layout=None,
    source_name="<memory>",
    expected_source_sha256=HARDWARE_READBACK_SHA256,
):
    """Return a checked startup-trampoline image without writing a file."""
    layout = layout or layout_model.load_layout()
    source = bytes(source)
    source_digest = sha256(source)
    if source_digest != expected_source_sha256:
        raise TrampolineError(
            f"{source_name}: source sha256 is {source_digest}, expected "
            f"{expected_source_sha256}"
        )
    if len(source) != ROM_SIZE:
        raise TrampolineError(
            f"{source_name}: source has {len(source)} bytes, "
            f"expected {ROM_SIZE}"
        )
    _require_trampoline_contract()
    try:
        source_verification = checksums.require_valid(source, source_name)
    except checksums.ChecksumError as error:
        raise TrampolineError(str(error)) from error
    if source[RESET_SELECTOR_LINE_START:RESET_SELECTOR_LINE_END] != bytes(128):
        raise TrampolineError("source reset-selector line is not all zero")
    if source[MARKER_LINE_START:MARKER_LINE_END] != bytes(128):
        raise TrampolineError("source marker line is not all zero")
    _require_hooks(layout, source, source_name, startup_replaced=False)
    _require_stock_anchors(layout, source, source_name)

    startup = _startup_hook(layout)
    patched = bytearray(source)
    patched[
        startup.address : startup.address + startup.width
    ] = startup.replacement.to_bytes(startup.width, layout.byte_order)
    patched[TRAMPOLINE_START:TRAMPOLINE_END] = TRAMPOLINE_BLOB
    patched = checksums.recalculate(patched)
    try:
        output_verification = checksums.require_valid(
            patched, "startup-trampoline output"
        )
    except checksums.ChecksumError as error:
        raise TrampolineError(str(error)) from error

    if not source_verification.valid or not output_verification.valid:
        raise TrampolineError("internal checksum verification did not pass")
    if patched[TRAMPOLINE_START:TRAMPOLINE_END] != TRAMPOLINE_BLOB:
        raise TrampolineError("trampoline payload differs after checksums")
    if patched[MARKER_LINE_START:TRAMPOLINE_START] != bytes(
        TRAMPOLINE_START - MARKER_LINE_START
    ):
        raise TrampolineError("bytes before trampoline changed")
    if patched[TRAMPOLINE_END:MARKER_LINE_END] != bytes(
        MARKER_LINE_END - TRAMPOLINE_END
    ):
        raise TrampolineError("bytes after trampoline changed")
    _require_hooks(layout, patched, "startup-trampoline output", True)
    _require_stock_anchors(layout, patched, "startup-trampoline output")

    checksum_offsets = checksums.checksum_byte_offsets()
    hook_offsets = set(range(startup.address, startup.address + startup.width))
    trampoline_offsets = set(range(TRAMPOLINE_START, TRAMPOLINE_END))
    permitted = hook_offsets | trampoline_offsets | set(checksum_offsets)
    changed = {
        offset
        for offset, (before, after) in enumerate(zip(source, patched))
        if before != after
    }
    outside = changed - permitted
    if outside:
        raise TrampolineError(
            f"trampoline build changed undeclared byte at {min(outside):#x}"
        )

    return TrampolineResult(
        data=bytes(patched),
        source_sha256=source_digest,
        output_sha256=sha256(patched),
        trampoline_sha256=TRAMPOLINE_SHA256,
        changed_bytes=len(changed),
        hook_changed_bytes=sum(
            source[offset] != patched[offset] for offset in hook_offsets
        ),
        trampoline_changed_bytes=sum(
            source[offset] != patched[offset]
            for offset in trampoline_offsets
        ),
        checksum_changed_bytes=sum(
            source[offset] != patched[offset]
            for offset in checksum_offsets
        ),
        permitted_write_bytes=len(permitted),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input", type=Path, help="exact successful marker readback ROM"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="output path; defaults to INPUT-startup-trampoline-d22a0.bin",
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
    except (OSError, TrampolineError) as error:
        parser.error(str(error))

    print(
        f"status=PASS source={args.input} "
        f"source_sha256={result.source_sha256}"
    )
    print(
        f"startup_hook=0x27d28:{STOCK_INITIALIZER:#x}->{TRAMPOLINE_START:#x} "
        f"trampoline=[{TRAMPOLINE_START:#x},{TRAMPOLINE_END:#x}) "
        f"tail_jump={STOCK_INITIALIZER:#x}"
    )
    print(
        f"trampoline_sha256={result.trampoline_sha256} "
        f"output_sha256={result.output_sha256} "
        f"changed_bytes={result.changed_bytes} "
        f"hook_changed_bytes={result.hook_changed_bytes} "
        f"trampoline_changed_bytes={result.trampoline_changed_bytes} "
        f"checksum_changed_bytes={result.checksum_changed_bytes} "
        f"permitted_write_bytes={result.permitted_write_bytes}"
    )
    print("other_runtime_hooks=stock ram_writes=none checksums=PASS")

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
