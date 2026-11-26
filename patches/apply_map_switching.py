#!/usr/bin/env python3
"""Add the validated five-slot runtime to a compatible 7MFKAVN86 ROM.

The input may contain calibration and configuration changes below 0x20000. Its
identity, checksum state, patch anchors, erased allocation, vector prefix, and
complete upper ROM partition must match the selected stock baseline. Existing
input bytes are preserved outside the declared map-switching and checksum write
sets.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from itertools import chain
import os
from pathlib import Path
import sys
import tempfile
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import jk08a_checksums as canonical_checksums
from patches import rom_checksums
from patches import map_switching_compose as composer
from patches import map_switching_layout as layout_model
from tools.mapkit import rom as romkit


DEFAULT_PAYLOADS = Path(__file__).with_name(
    "map-switching-payloads.toml"
)


class PatchError(ValueError):
    """Raised when input, payload, output, or preservation checks fail."""


@dataclass(frozen=True)
class PatchResult:
    data: bytes
    source_sha256: str
    output_sha256: str
    source_checksums: rom_checksums.ChecksumValues
    output_checksums: rom_checksums.ChecksumValues
    composition_changed_bytes: int
    final_changed_bytes: int
    permitted_write_bytes: int
    checksum_changed_bytes: int


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def md5(data):
    return hashlib.md5(data).hexdigest()


def default_output_path(source, suffix="map-switching"):
    source = Path(source)
    if source.resolve().is_relative_to((ROOT / "rom-images").resolve()):
        raise PatchError(
            "input is under rom-images; select an explicit --output outside "
            "the stock collection"
        )
    return source.with_name(f"{source.stem}-{suffix}.bin")


def load_payloads(layout=None, path=DEFAULT_PAYLOADS):
    """Read and SHA-validate the tracked raw machine-code payloads."""
    layout = layout or layout_model.load_layout()
    path = Path(path)
    with path.open("rb") as source:
        raw = tomllib.load(source)
    if raw.get("schema_version") != 1:
        raise PatchError(
            f"{path}: unsupported payload schema "
            f"{raw.get('schema_version')!r}"
        )
    units = raw.get("units")
    if not isinstance(units, dict):
        raise PatchError(f"{path}: missing [units] table")
    expected = set(layout.assembly_unit_by_key)
    actual = set(units)
    if actual != expected:
        raise PatchError(
            f"{path}: payload set differs; "
            f"missing={sorted(expected - actual)}; "
            f"extra={sorted(actual - expected)}"
        )
    result = {}
    for unit in layout.assembly_units:
        text = units[unit.key]
        if not isinstance(text, str):
            raise PatchError(f"{path}: {unit.key} payload is not text")
        try:
            blob = bytes.fromhex("".join(text.split()))
        except ValueError as error:
            raise PatchError(
                f"{path}: {unit.key} payload is not hexadecimal"
            ) from error
        try:
            result[unit.key] = layout_model.validate_assembled_blob(
                unit, blob
            )
        except ValueError as error:
            raise PatchError(f"{path}: {error}") from error
    return result


def load_blob_overrides(layout, arguments):
    overrides = {}
    for key, path in arguments:
        if key in overrides:
            raise PatchError(f"duplicate blob override for {key!r}")
        unit = layout.assembly_unit_by_key.get(key)
        if unit is None:
            raise PatchError(f"unknown assembly unit {key!r}")
        try:
            overrides[key] = layout_model.validate_assembled_blob(unit, path)
        except (OSError, ValueError) as error:
            raise PatchError(f"{path}: {error}") from error
    return overrides


def _final_write_offsets(layout, checksum_layout=None):
    checksum_layout = checksum_layout or canonical_checksums.LAYOUT
    composition_offsets = set(
        chain.from_iterable(
            range(region.start, region.end)
            for region in composer.composition_write_ranges(layout)
        )
    )
    return composition_offsets | set(
        rom_checksums.checksum_byte_offsets(checksum_layout)
    )


def _validate_slot_initialization(layout, source, patched):
    for family in layout.families:
        canonical = source[
            family.canonical_address :
            family.canonical_address + family.byte_length
        ]
        for address in family.copies:
            if patched[address : address + family.byte_length] != canonical:
                raise PatchError(
                    f"{family.key}: initialized map copy at "
                    f"{address:#x} differs from input Map 1"
                )


def _validate_preservation(
    layout, source, patched, checksum_layout
):
    permitted = _final_write_offsets(layout, checksum_layout)
    changed = {
        offset
        for offset, (before, after) in enumerate(zip(source, patched))
        if before != after
    }
    outside = changed - permitted
    if outside:
        raise PatchError(
            "final image changes undeclared input byte at "
            f"{min(outside):#x}"
        )
    return len(changed), len(permitted)


def patch_image(
    source,
    layout=None,
    blobs=None,
    source_name="<memory>",
    stock_image=None,
    checksum_layout=None,
    cruise_free_config=None,
):
    """Return a checked, self-consistent map-switching image."""
    layout = layout or layout_model.load_layout()
    checksum_layout = checksum_layout or canonical_checksums.LAYOUT
    source = bytes(source)
    image_rom = stock_image.rom if stock_image is not None else layout.rom
    image = romkit.Image(image_rom, source_name, source)
    try:
        source_verification = rom_checksums.require_valid(
            source, checksum_layout, source_name
        )
        layout_model.validate_compatible_image(
            layout, image, stock_image
        )
        composition = composer.compose(
            layout=layout,
            image=image,
            blobs=blobs or load_payloads(layout),
            source_policy="compatible",
            stock_image=stock_image,
            cruise_free_config=cruise_free_config,
        )
        patched = rom_checksums.recalculate(
            composition.data, checksum_layout
        )
        output_verification = rom_checksums.require_valid(
            patched, checksum_layout, "map-switching output"
        )
    except (rom_checksums.ChecksumError, ValueError) as error:
        raise PatchError(str(error)) from error

    _validate_slot_initialization(layout, source, patched)
    final_changed_bytes, permitted_write_bytes = _validate_preservation(
        layout, source, patched, checksum_layout
    )
    checksum_offsets = rom_checksums.checksum_byte_offsets(checksum_layout)
    checksum_changed_bytes = sum(
        source[offset] != patched[offset] for offset in checksum_offsets
    )
    return PatchResult(
        data=patched,
        source_sha256=sha256(source),
        output_sha256=sha256(patched),
        source_checksums=source_verification.stored,
        output_checksums=output_verification.stored,
        composition_changed_bytes=composition.changed_bytes,
        final_changed_bytes=final_changed_bytes,
        permitted_write_bytes=permitted_write_bytes,
        checksum_changed_bytes=checksum_changed_bytes,
    )


def _publish_artifacts(artifacts, rom_path, *, kind="output artifact"):
    """Stage and read back every missing file, then publish the ROM last."""
    def identical(path, content):
        try:
            current = path.read_bytes()
        except FileNotFoundError:
            return False
        if current != content:
            raise PatchError(f"existing {kind} differs: {path}")
        return True

    missing = {
        path: content for path, content in artifacts.items()
        if not identical(path, content)
    }
    staged = {}
    created = []
    try:
        for path, content in missing.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                dir=path.parent, prefix=f".{path.name}.", suffix=".tmp",
                delete=False,
            ) as output:
                staged[path] = Path(output.name)
                output.write(content)
                output.flush()
                os.fsync(output.fileno())
            if staged[path].read_bytes() != content:
                raise PatchError(f"staged output artifact differs: {path}")

        order = [path for path in staged if path != rom_path]
        if rom_path in staged:
            order.append(rom_path)
        for path in order:
            try:
                os.link(staged[path], path)
            except FileExistsError:
                if not identical(path, artifacts[path]):
                    raise PatchError(f"existing {kind} differs: {path}")
            else:
                created.append(path)
    except Exception:
        for path in reversed(created):
            try:
                current = path.lstat()
                original = staged[path].stat()
                if ((current.st_dev, current.st_ino)
                        == (original.st_dev, original.st_ino)
                        and path.read_bytes() == artifacts[path]):
                    path.unlink()
            except FileNotFoundError:
                pass
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)
    return tuple(created)


def write_output(path, image):
    """Create a complete output exclusively or accept an identical file."""
    path = Path(path)
    return bool(_publish_artifacts({path: image}, path, kind="output"))


def write_md5_sidecar(path, image):
    path = Path(path)
    sidecar = path.with_name(f"{path.name}.md5")
    content = f"{md5(image)} *{path.name}\n".encode("ascii")
    return bool(_publish_artifacts(
        {sidecar: content}, sidecar, kind="MD5 sidecar"
    ))


def write_output_with_md5(path, image):
    """Publish a complete ROM only after its MD5 sidecar is available."""
    path = Path(path)
    sidecar = path.with_name(f"{path.name}.md5")
    artifacts = {
        path: image,
        sidecar: f"{md5(image)} *{path.name}\n".encode("ascii"),
    }
    return path in _publish_artifacts(artifacts, path)


def _blob_argument(text):
    key, separator, value = text.partition("=")
    if not separator or not key or not value:
        raise argparse.ArgumentTypeError("expected KEY=PATH")
    return key, Path(value)


def _format_checksums(values):
    return ",".join(f"{name}={value:#x}" for name, value in values.items())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="compatible JK08A input ROM")
    parser.add_argument(
        "--output",
        type=Path,
        help="output path; defaults to INPUT-map-switching.bin",
    )
    parser.add_argument(
        "--payloads",
        type=Path,
        default=DEFAULT_PAYLOADS,
        help="tracked machine-code payload bundle",
    )
    parser.add_argument(
        "--blob",
        action="append",
        type=_blob_argument,
        default=[],
        metavar="KEY=PATH",
        help="optional independently rebuilt raw blob override",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="compose and verify without writing files",
    )
    args = parser.parse_args(argv)

    layout = layout_model.load_layout()
    try:
        source = args.input.read_bytes()
        blobs = load_payloads(layout, args.payloads)
        blobs.update(load_blob_overrides(layout, args.blob))
        result = patch_image(
            source,
            layout=layout,
            blobs=blobs,
            source_name=str(args.input),
        )
    except (OSError, PatchError) as error:
        parser.error(str(error))

    print(
        f"status=PASS rom={layout.rom} slots={layout.slot_count} "
        f"families={len(layout.families)}"
    )
    print(
        f"source={args.input} source_sha256={result.source_sha256}"
    )
    print(
        f"source_checksums={_format_checksums(result.source_checksums)}"
    )
    print(
        f"output_sha256={result.output_sha256} "
        f"output_checksums={_format_checksums(result.output_checksums)}"
    )
    print(
        f"composition_changed_bytes={result.composition_changed_bytes} "
        f"final_changed_bytes={result.final_changed_bytes} "
        f"permitted_write_bytes={result.permitted_write_bytes} "
        f"checksum_changed_bytes={result.checksum_changed_bytes}"
    )
    print(
        "feedback_frame_counts="
        f"{layout.feedback.default_on_frames},"
        f"{layout.feedback.default_off_frames} "
        f"feedback_state={layout.feedback.lamp_on_value}"
    )

    if args.verify_only:
        print("no ROM file was written")
        return 0

    try:
        output = args.output or default_output_path(args.input)
        if output.resolve() == args.input.resolve():
            parser.error("input and output paths must differ")
        created = write_output_with_md5(output, result.data)
    except (OSError, PatchError) as error:
        parser.error(str(error))
    print(f"output={output} status={'created' if created else 'already_exact'}")
    print(f"md5={md5(result.data)} sidecar={output.name}.md5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
