#!/usr/bin/env python3
"""Build the JK08A minimal startup selector-initialization hardware gate.

The source is locked to the successful startup-trampoline hardware readback.
The output preserves the existing startup hook, replaces the transparent tail
trampoline with a wrapper that writes Map 1 to the reserved selector byte, and
recalculates checksum references. It installs no limiter, lookup, selector-host,
calibration, or CAN-feedback behavior.
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
from patches import build_map_switching_trampoline as trampoline
from patches import jk08a_checksums as checksums
from patches import map_switching_assembly as assembly
from patches import map_switching_layout as layout_model


HARDWARE_READBACK_SHA256 = (
    "6b1df699f614151a7ddd09595671de021b7131d5524b16d1f27a9fed888abc55"
)
ROM_SIZE = 0x100000
RESET_SELECTOR_LINE_START = 0x00008080
RESET_SELECTOR_LINE_END = 0x00008100
MARKER_LINE_START = 0x000D2280
MARKER_LINE_END = 0x000D2300
SELECTOR_INIT_START = 0x000D22A0
SELECTOR_INIT_END = 0x000D22BC
STOCK_INITIALIZER = 0x0002C648
SELECTOR_STATE = 0xFFFF5D00
SELECTOR_INIT_SOURCE = Path(__file__).with_name(
    "map-switching-startup-selector-init.s"
)
SELECTOR_INIT_BLOB = bytes.fromhex(
    "4f22d105e0002100d002400b00094f26000b00090002c648ffff5d00"
)
SELECTOR_INIT_SHA256 = (
    "906991815705fe9a0b91d3817fab1a59d4664e3f04ad126820d969e47d7f5612"
)


class SelectorInitError(ValueError):
    """Raised when the source or selector-init output violates the gate."""


@dataclass(frozen=True)
class SelectorInitResult:
    data: bytes
    source_sha256: str
    output_sha256: str
    selector_init_sha256: str
    changed_bytes: int
    selector_init_changed_bytes: int
    checksum_changed_bytes: int
    permitted_write_bytes: int


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def default_output_path(source):
    source = Path(source)
    return source.with_name(
        f"{source.stem}-startup-selector-init-d22a0.bin"
    )


def _startup_hook(layout):
    hooks = {hook.key: hook for hook in layout.hooks}
    try:
        hook = hooks["startup_initializer"]
    except KeyError as error:
        raise SelectorInitError(
            "layout has no startup initializer hook"
        ) from error
    if (
        hook.address != 0x00027D28
        or hook.width != 4
        or hook.stock != STOCK_INITIALIZER
        or hook.replacement != SELECTOR_INIT_START
    ):
        raise SelectorInitError("layout startup initializer hook differs")
    return hook


def _require_selector_init_contract():
    if len(SELECTOR_INIT_BLOB) != SELECTOR_INIT_END - SELECTOR_INIT_START:
        raise SelectorInitError("selector-init blob length differs")
    if sha256(SELECTOR_INIT_BLOB) != SELECTOR_INIT_SHA256:
        raise SelectorInitError("selector-init blob SHA-256 differs")
    try:
        parsed = assembly.parse_source(
            SELECTOR_INIT_SOURCE,
            SELECTOR_INIT_START,
            SELECTOR_INIT_END,
        )
    except (OSError, ValueError) as error:
        raise SelectorInitError(str(error)) from error
    expected_labels = {
        "startup_selector_init": SELECTOR_INIT_START,
        "startup_stock_initializer": 0x000D22B4,
        "startup_selector_state": 0x000D22B8,
    }
    if parsed.labels != expected_labels:
        raise SelectorInitError("selector-init source labels differ")
    expected_statements = (
        (0x000D22A0, "instruction", "sts.l pr,@-r15", 2),
        (
            0x000D22A2,
            "instruction",
            "mov.l @(startup_selector_state,pc),r1",
            2,
        ),
        (0x000D22A4, "instruction", "mov #0x0,r0", 2),
        (0x000D22A6, "instruction", "mov.b r0,@r1", 2),
        (
            0x000D22A8,
            "instruction",
            "mov.l @(startup_stock_initializer,pc),r0",
            2,
        ),
        (0x000D22AA, "instruction", "jsr @r0", 2),
        (0x000D22AC, "instruction", "nop", 2),
        (0x000D22AE, "instruction", "lds.l @r15+,pr", 2),
        (0x000D22B0, "instruction", "rts", 2),
        (0x000D22B2, "instruction", "nop", 2),
        (0x000D22B4, "long", "0x0002C648", 4),
        (0x000D22B8, "long", "0xFFFF5D00", 4),
    )
    actual_statements = tuple(
        (item.address, item.kind, item.text, item.size)
        for item in parsed.statements
    )
    if actual_statements != expected_statements:
        raise SelectorInitError("selector-init source statements differ")
    return parsed


def _require_hooks(layout, data, context):
    startup = _startup_hook(layout)
    for hook in layout.hooks:
        actual = int.from_bytes(
            data[hook.address : hook.address + hook.width],
            layout.byte_order,
        )
        expected = startup.replacement if hook.key == startup.key else hook.stock
        if actual != expected:
            raise SelectorInitError(
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
            raise SelectorInitError(
                f"{context}: {anchor.key} at {anchor.address:#x} is "
                f"{actual:#x}, expected {anchor.value:#x}"
            )


def _require_source_payload(source):
    if source[MARKER_LINE_START:SELECTOR_INIT_START] != bytes(
        SELECTOR_INIT_START - MARKER_LINE_START
    ):
        raise SelectorInitError("source bytes before trampoline are not zero")
    if (
        source[trampoline.TRAMPOLINE_START:trampoline.TRAMPOLINE_END]
        != trampoline.TRAMPOLINE_BLOB
    ):
        raise SelectorInitError("source trampoline payload differs")
    if source[trampoline.TRAMPOLINE_END:MARKER_LINE_END] != bytes(
        MARKER_LINE_END - trampoline.TRAMPOLINE_END
    ):
        raise SelectorInitError("source bytes after trampoline are not zero")


def build_image(
    source,
    layout=None,
    source_name="<memory>",
    expected_source_sha256=HARDWARE_READBACK_SHA256,
):
    """Return a checked startup selector-init image without writing a file."""
    layout = layout or layout_model.load_layout()
    source = bytes(source)
    source_digest = sha256(source)
    if source_digest != expected_source_sha256:
        raise SelectorInitError(
            f"{source_name}: source sha256 is {source_digest}, expected "
            f"{expected_source_sha256}"
        )
    if len(source) != ROM_SIZE:
        raise SelectorInitError(
            f"{source_name}: source has {len(source)} bytes, expected {ROM_SIZE}"
        )
    _require_selector_init_contract()
    try:
        source_verification = checksums.require_valid(source, source_name)
    except checksums.ChecksumError as error:
        raise SelectorInitError(str(error)) from error
    if source[RESET_SELECTOR_LINE_START:RESET_SELECTOR_LINE_END] != bytes(128):
        raise SelectorInitError("source reset-selector line is not all zero")
    _require_source_payload(source)
    _require_hooks(layout, source, source_name)
    _require_stock_anchors(layout, source, source_name)

    patched = bytearray(source)
    patched[SELECTOR_INIT_START:SELECTOR_INIT_END] = SELECTOR_INIT_BLOB
    patched = checksums.recalculate(patched)
    try:
        output_verification = checksums.require_valid(
            patched, "startup selector-init output"
        )
    except checksums.ChecksumError as error:
        raise SelectorInitError(str(error)) from error

    if not source_verification.valid or not output_verification.valid:
        raise SelectorInitError("internal checksum verification did not pass")
    if patched[SELECTOR_INIT_START:SELECTOR_INIT_END] != SELECTOR_INIT_BLOB:
        raise SelectorInitError("selector-init payload differs after checksums")
    if patched[MARKER_LINE_START:SELECTOR_INIT_START] != bytes(
        SELECTOR_INIT_START - MARKER_LINE_START
    ):
        raise SelectorInitError("bytes before selector-init changed")
    if patched[SELECTOR_INIT_END:MARKER_LINE_END] != bytes(
        MARKER_LINE_END - SELECTOR_INIT_END
    ):
        raise SelectorInitError("bytes after selector-init changed")
    _require_hooks(layout, patched, "startup selector-init output")
    _require_stock_anchors(layout, patched, "startup selector-init output")

    checksum_offsets = checksums.checksum_byte_offsets()
    selector_init_offsets = set(
        range(SELECTOR_INIT_START, SELECTOR_INIT_END)
    )
    permitted = selector_init_offsets | set(checksum_offsets)
    changed = {
        offset
        for offset, (before, after) in enumerate(zip(source, patched))
        if before != after
    }
    outside = changed - permitted
    if outside:
        raise SelectorInitError(
            f"selector-init build changed undeclared byte at {min(outside):#x}"
        )

    return SelectorInitResult(
        data=bytes(patched),
        source_sha256=source_digest,
        output_sha256=sha256(patched),
        selector_init_sha256=SELECTOR_INIT_SHA256,
        changed_bytes=len(changed),
        selector_init_changed_bytes=sum(
            source[offset] != patched[offset]
            for offset in selector_init_offsets
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
        "input", type=Path, help="exact successful trampoline readback ROM"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="output path; defaults to INPUT-startup-selector-init-d22a0.bin",
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
    except (OSError, SelectorInitError) as error:
        parser.error(str(error))

    print(
        f"status=PASS source={args.input} "
        f"source_sha256={result.source_sha256}"
    )
    print(
        "startup_hook=preserved:0x27d28->0xd22a0 "
        f"selector_init=[{SELECTOR_INIT_START:#x},{SELECTOR_INIT_END:#x}) "
        f"stock_initializer={STOCK_INITIALIZER:#x} "
        f"selector_write={SELECTOR_STATE:#x}:byte=0"
    )
    print(
        f"selector_init_sha256={result.selector_init_sha256} "
        f"output_sha256={result.output_sha256} "
        f"changed_bytes={result.changed_bytes} "
        f"selector_init_changed_bytes={result.selector_init_changed_bytes} "
        f"checksum_changed_bytes={result.checksum_changed_bytes} "
        f"permitted_write_bytes={result.permitted_write_bytes}"
    )
    print(
        "other_runtime_hooks=stock limiter=absent selector_host=absent "
        "lookup_adapters=absent can_feedback=absent checksums=PASS"
    )

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
