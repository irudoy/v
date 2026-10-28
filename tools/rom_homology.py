#!/usr/bin/env python3
"""Measure exact and address-independent similarity across stock flash ROMs."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import dataclass
import hashlib
import io
from pathlib import Path
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
ROM_DIR = ROOT / "rom-images"
IMAGE_REGISTRY = ROM_DIR / "roms.csv"
HOMOLOGY_REGISTRY = ROM_DIR / "homology.toml"
DEFAULT_OUTPUT = ROM_DIR / "homology.csv"
RANGE_RE = re.compile(r"0x([0-9a-fA-F]+):0x([0-9a-fA-F]+)")
LAYOUT_RE = re.compile(r"[0-9a-z]{2,8}")

# Every image carries the calibration string plus two fixed identity blocks,
# each introduced by a literal marker and holding an eleven-byte software
# string nine bytes in. An unpopulated block carries erased flash instead.
CALIBRATION_OFFSET = 0x008204
IDENTITY_WIDTH = 11
IDENTITY_BLOCKS = ((0x006F00, b"12345", 0x006F09), (0x007000, b"000000", 0x007009))


class HomologyError(ValueError):
    """Raised when ROM evidence or a homology declaration is inconsistent."""


@dataclass(frozen=True)
class Settings:
    code_start: int
    window_size: int
    source_stride: int
    target_stride: int
    page_size: int
    min_distinct_bytes: int
    max_dominant_fraction: float


@dataclass(frozen=True)
class Image:
    label: str
    path: Path
    registry_path: str
    sha256: str
    data: bytes


@dataclass(frozen=True)
class PairMetrics:
    left: str
    right: str
    left_size: int
    right_size: int
    compared_bytes: int
    same_offset_bytes: int
    differing_bytes: int
    differing_runs: int
    first_diff: int | None
    last_diff: int | None
    tail_bytes: int
    exact_pages: int
    compared_pages: int
    left_code_windows: int
    left_windows_found_in_right: int
    right_code_windows: int
    right_windows_found_in_left: int


CSV_FIELDS = (
    "left",
    "right",
    "left_size",
    "right_size",
    "compared_bytes",
    "same_offset_bytes",
    "same_offset_ratio",
    "differing_bytes",
    "differing_runs",
    "first_diff",
    "last_diff",
    "tail_bytes",
    "exact_pages",
    "compared_pages",
    "exact_page_ratio",
    "left_code_windows",
    "left_windows_found_in_right",
    "left_to_right_window_ratio",
    "right_code_windows",
    "right_windows_found_in_left",
    "right_to_left_window_ratio",
    "symmetric_window_ratio",
)


def _rom_label(registry_path: str) -> str:
    name = Path(registry_path).name
    if not name.endswith("-stock.bin"):
        raise HomologyError(f"{registry_path}: not a stock flash image")
    token = name.split("-", 1)[0]
    if not token.startswith("1") or len(token) == 1:
        raise HomologyError(f"{registry_path}: cannot derive the ROM label")
    return token[1:]


def load_images(path: Path = IMAGE_REGISTRY) -> dict[str, Image]:
    path = Path(path)
    try:
        with path.open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
    except OSError as error:
        raise HomologyError(f"image registry not found: {path}") from error

    images = {}
    for row in rows:
        registry_path = row.get("path", "")
        if not registry_path.endswith("-stock.bin"):
            continue
        label = _rom_label(registry_path)
        if label in images:
            raise HomologyError(f"{path}: duplicate stock ROM label {label}")
        image_path = path.parent / registry_path
        try:
            data = image_path.read_bytes()
        except OSError as error:
            raise HomologyError(f"stock ROM not found: {image_path}") from error
        actual = hashlib.sha256(data).hexdigest()
        expected = row.get("sha256", "")
        if actual != expected:
            raise HomologyError(
                f"{image_path}: SHA-256 is {actual}, expected {expected}"
            )
        images[label] = Image(
            label=label,
            path=image_path,
            registry_path=registry_path,
            sha256=actual,
            data=data,
        )
    if not images:
        raise HomologyError(f"{path}: no stock flash images")
    return images


def load_homology(path: Path = HOMOLOGY_REGISTRY):
    path = Path(path)
    try:
        with path.open("rb") as source:
            document = tomllib.load(source)
    except OSError as error:
        raise HomologyError(f"homology registry not found: {path}") from error
    if document.get("schema_version") != 1:
        raise HomologyError(f"{path}: unsupported schema_version")
    raw = document.get("analysis")
    if not isinstance(raw, dict):
        raise HomologyError(f"{path}: missing [analysis]")
    required = {
        "code_start",
        "window_size",
        "source_stride",
        "target_stride",
        "page_size",
        "min_distinct_bytes",
        "max_dominant_fraction",
    }
    if set(raw) != required:
        raise HomologyError(
            f"{path}: [analysis] fields differ; "
            f"missing={sorted(required - set(raw))}; "
            f"extra={sorted(set(raw) - required)}"
        )
    settings = Settings(**raw)
    if (
        settings.code_start < 0
        or settings.window_size <= 0
        or settings.source_stride <= 0
        or settings.target_stride <= 0
        or settings.page_size <= 0
        or not 1 <= settings.min_distinct_bytes <= 256
        or not 0 < settings.max_dominant_fraction <= 1
    ):
        raise HomologyError(f"{path}: invalid analysis settings")
    families = document.get("family")
    if not isinstance(families, dict) or not families:
        raise HomologyError(f"{path}: no [family.*] declarations")
    return settings, families, document.get("relationship", [])


def _parse_range(value: str, context: str) -> tuple[int, int]:
    match = RANGE_RE.fullmatch(value)
    if not match:
        raise HomologyError(f"{context}: invalid range {value!r}")
    start, end = (int(item, 16) for item in match.groups())
    if start >= end:
        raise HomologyError(f"{context}: empty range {value}")
    return start, end


def validate_layouts(row, context, seen):
    """Hold the layouts of a family to its members and its inheritance.

    A family that inherits addresses has one layout whose L0 image is the
    canonical member; every other family has one layout per member.
    """
    layouts = row["layouts"]
    if not isinstance(layouts, dict) or not layouts:
        raise HomologyError(f"{context}: layouts must be a nonempty inline table")
    for layout, image in layouts.items():
        if not LAYOUT_RE.fullmatch(layout):
            raise HomologyError(f"{context}: invalid layout id {layout!r}")
        if layout in seen:
            raise HomologyError(f"{context}: layout {layout} is declared twice")
        seen.add(layout)
        if image not in row["members"]:
            raise HomologyError(f"{context}: layout {layout} image {image} is not a member")
    images = list(layouts.values())
    if row["same_address_inheritance"]:
        if images != [row["canonical"]]:
            raise HomologyError(
                f"{context}: an inheriting family has one layout of its canonical ROM"
            )
    elif sorted(images) != sorted(row["members"]):
        raise HomologyError(f"{context}: every member needs its own layout")


def validate_families(images, families, path: Path = HOMOLOGY_REGISTRY):
    declared = []
    allowed_kinds = {"exact-code", "near-code", "distinct-code"}
    required = {
        "kind",
        "members",
        "canonical",
        "mcu",
        "flash_size",
        "software_ids",
        "same_address_inheritance",
        "layouts",
        "evidence",
    }
    optional = {"calibration_region", "exact_ranges"}
    layout_ids = set()
    for key, row in families.items():
        context = f"{path} [family.{key}]"
        if not isinstance(row, dict):
            raise HomologyError(f"{context}: expected a table")
        unknown = set(row) - required - optional
        missing = required - set(row)
        if missing or unknown:
            raise HomologyError(
                f"{context}: fields differ; missing={sorted(missing)}; "
                f"extra={sorted(unknown)}"
            )
        if row["kind"] not in allowed_kinds:
            raise HomologyError(f"{context}: unsupported kind {row['kind']!r}")
        members = row["members"]
        if not isinstance(members, list) or not members or len(set(members)) != len(members):
            raise HomologyError(f"{context}: members must be a unique nonempty array")
        missing_images = sorted(set(members) - set(images))
        if missing_images:
            raise HomologyError(f"{context}: unknown members {missing_images}")
        if row["canonical"] not in members:
            raise HomologyError(f"{context}: canonical ROM is not a member")
        if (
            not isinstance(row["mcu"], str)
            or not row["mcu"].strip()
            or type(row["flash_size"]) is not int
            or not isinstance(row["software_ids"], list)
            or any(
                not isinstance(item, str) or not item.strip()
                for item in row["software_ids"]
            )
            or type(row["same_address_inheritance"]) is not bool
            or not isinstance(row["evidence"], str)
            or not row["evidence"].strip()
        ):
            raise HomologyError(f"{context}: invalid family metadata")
        if any(len(images[item].data) != row["flash_size"] for item in members):
            raise HomologyError(f"{context}: member size differs from flash_size")
        declared.extend(members)
        validate_layouts(row, context, layout_ids)

        exact_ranges = row.get("exact_ranges", [])
        calibration_region = row.get("calibration_region")
        if row["kind"] == "exact-code":
            if not exact_ranges or not calibration_region:
                raise HomologyError(
                    f"{context}: exact-code families require exact_ranges and "
                    "calibration_region"
                )
            canonical = images[row["canonical"]].data
            parsed = [
                _parse_range(value, f"{context}.exact_ranges")
                for value in exact_ranges
            ]
            if parsed != sorted(parsed) or any(
                left[1] > right[0] for left, right in zip(parsed, parsed[1:])
            ):
                raise HomologyError(f"{context}: exact_ranges overlap or are unordered")
            _parse_range(calibration_region, f"{context}.calibration_region")
            for member in members:
                target = images[member].data
                for start, end in parsed:
                    if end > len(target) or target[start:end] != canonical[start:end]:
                        raise HomologyError(
                            f"{context}: {member} differs from {row['canonical']} "
                            f"in declared exact range 0x{start:06x}:0x{end:06x}"
                        )
        elif exact_ranges or calibration_region:
            raise HomologyError(
                f"{context}: only exact-code families may declare exact ranges"
            )

    if len(declared) != len(set(declared)):
        raise HomologyError(f"{path}: a ROM belongs to more than one family")
    if set(declared) != set(images):
        raise HomologyError(
            f"{path}: family coverage differs; "
            f"missing={sorted(set(images) - set(declared))}; "
            f"extra={sorted(set(declared) - set(images))}"
        )


def read_identity(data: bytes) -> tuple[str, tuple[str, ...]]:
    """Return the calibration string and the software string of each block."""

    calibration = data[
        CALIBRATION_OFFSET : CALIBRATION_OFFSET + IDENTITY_WIDTH
    ].decode("ascii", "replace")
    blocks = []
    for marker_offset, marker, offset in IDENTITY_BLOCKS:
        if data[marker_offset : marker_offset + len(marker)] != marker:
            blocks.append("")
            continue
        field = data[offset : offset + IDENTITY_WIDTH].split(b"\x00", 1)[0]
        blocks.append(field.decode("ascii", "replace").strip())
    return calibration.strip(), tuple(blocks)


def validate_software_ids(images, families, path: Path = HOMOLOGY_REGISTRY):
    """Bind every declared family identifier to a string inside a member image."""

    for key, row in families.items():
        context = f"{path} [family.{key}]"
        declared = row["software_ids"]
        if not declared:
            raise HomologyError(
                f"{context}: software_ids must name at least one identifier"
            )
        carried = {
            member: {block for block in read_identity(images[member].data)[1] if block}
            for member in row["members"]
        }
        unseen = sorted(
            value
            for value in declared
            if not any(value in found for found in carried.values())
        )
        if unseen:
            raise HomologyError(f"{context}: no member image carries {unseen}")
        unnamed = sorted(
            member for member, found in carried.items() if not found & set(declared)
        )
        if unnamed:
            raise HomologyError(
                f"{context}: members {unnamed} carry no declared identifier"
            )


def validate_relationships(families, relationships, path: Path = HOMOLOGY_REGISTRY):
    if not isinstance(relationships, list):
        raise HomologyError(f"{path}: relationship must be an array of tables")
    required = {
        "left_family",
        "right_family",
        "kind",
        "direct_address_inheritance",
        "evidence",
    }
    seen = set()
    for index, row in enumerate(relationships):
        context = f"{path} [[relationship]] #{index + 1}"
        if not isinstance(row, dict) or set(row) != required:
            actual = set(row) if isinstance(row, dict) else set()
            raise HomologyError(
                f"{context}: fields differ; missing={sorted(required - actual)}; "
                f"extra={sorted(actual - required)}"
            )
        left, right = row["left_family"], row["right_family"]
        if left not in families or right not in families or left == right:
            raise HomologyError(f"{context}: invalid family references")
        key = tuple(sorted((left, right)))
        if key in seen:
            raise HomologyError(f"{context}: duplicate family relationship")
        seen.add(key)
        if (
            not isinstance(row["kind"], str)
            or not row["kind"].strip()
            or type(row["direct_address_inheritance"]) is not bool
            or not isinstance(row["evidence"], str)
            or not row["evidence"].strip()
        ):
            raise HomologyError(f"{context}: invalid relationship metadata")


def _meaningful(block: bytes, settings: Settings) -> bool:
    counts = Counter(block)
    return (
        len(counts) >= settings.min_distinct_bytes
        and max(counts.values()) / len(block) < settings.max_dominant_fraction
    )


def source_windows(data: bytes, settings: Settings) -> tuple[bytes, ...]:
    width = settings.window_size
    return tuple(
        block
        for start in range(
            settings.code_start,
            len(data) - width + 1,
            settings.source_stride,
        )
        if _meaningful((block := data[start : start + width]), settings)
    )


def target_window_index(data: bytes, settings: Settings) -> set[bytes]:
    width = settings.window_size
    return {
        data[start : start + width]
        for start in range(
            settings.code_start,
            len(data) - width + 1,
            settings.target_stride,
        )
    }


def _offset_metrics(left: bytes, right: bytes, page_size: int):
    compared = min(len(left), len(right))
    same = 0
    differing = 0
    runs = 0
    first = None
    last = None
    previous_diff = -2
    for offset, (left_byte, right_byte) in enumerate(zip(left, right)):
        if left_byte == right_byte:
            same += 1
            continue
        differing += 1
        if offset != previous_diff + 1:
            runs += 1
        if first is None:
            first = offset
        last = offset
        previous_diff = offset
    pages = compared // page_size
    exact_pages = sum(
        left[start : start + page_size] == right[start : start + page_size]
        for start in range(0, pages * page_size, page_size)
    )
    return compared, same, differing, runs, first, last, pages, exact_pages


def measure_pairs(images: dict[str, Image], settings: Settings) -> list[PairMetrics]:
    labels = sorted(images)
    source = {
        label: source_windows(images[label].data, settings)
        for label in labels
    }
    directional = {}
    for target_label in labels:
        index = target_window_index(images[target_label].data, settings)
        for source_label in labels:
            directional[source_label, target_label] = sum(
                block in index for block in source[source_label]
            )

    rows = []
    for left_index, left_label in enumerate(labels):
        for right_label in labels[left_index + 1 :]:
            left = images[left_label].data
            right = images[right_label].data
            (
                compared,
                same,
                differing,
                runs,
                first,
                last,
                pages,
                exact_pages,
            ) = _offset_metrics(left, right, settings.page_size)
            rows.append(
                PairMetrics(
                    left=left_label,
                    right=right_label,
                    left_size=len(left),
                    right_size=len(right),
                    compared_bytes=compared,
                    same_offset_bytes=same,
                    differing_bytes=differing,
                    differing_runs=runs,
                    first_diff=first,
                    last_diff=last,
                    tail_bytes=abs(len(left) - len(right)),
                    exact_pages=exact_pages,
                    compared_pages=pages,
                    left_code_windows=len(source[left_label]),
                    left_windows_found_in_right=directional[left_label, right_label],
                    right_code_windows=len(source[right_label]),
                    right_windows_found_in_left=directional[right_label, left_label],
                )
            )
    return rows


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _hex_or_empty(value: int | None) -> str:
    return "" if value is None else f"0x{value:06x}"


def render_csv(rows: list[PairMetrics]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        left_ratio = _ratio(
            row.left_windows_found_in_right, row.left_code_windows
        )
        right_ratio = _ratio(
            row.right_windows_found_in_left, row.right_code_windows
        )
        writer.writerow(
            {
                "left": row.left,
                "right": row.right,
                "left_size": row.left_size,
                "right_size": row.right_size,
                "compared_bytes": row.compared_bytes,
                "same_offset_bytes": row.same_offset_bytes,
                "same_offset_ratio": f"{_ratio(row.same_offset_bytes, row.compared_bytes):.6f}",
                "differing_bytes": row.differing_bytes,
                "differing_runs": row.differing_runs,
                "first_diff": _hex_or_empty(row.first_diff),
                "last_diff": _hex_or_empty(row.last_diff),
                "tail_bytes": row.tail_bytes,
                "exact_pages": row.exact_pages,
                "compared_pages": row.compared_pages,
                "exact_page_ratio": f"{_ratio(row.exact_pages, row.compared_pages):.6f}",
                "left_code_windows": row.left_code_windows,
                "left_windows_found_in_right": row.left_windows_found_in_right,
                "left_to_right_window_ratio": f"{left_ratio:.6f}",
                "right_code_windows": row.right_code_windows,
                "right_windows_found_in_left": row.right_windows_found_in_left,
                "right_to_left_window_ratio": f"{right_ratio:.6f}",
                "symmetric_window_ratio": f"{min(left_ratio, right_ratio):.6f}",
            }
        )
    return output.getvalue()


def build_report():
    images = load_images()
    settings, families, relationships = load_homology()
    validate_families(images, families)
    validate_software_ids(images, families)
    validate_relationships(families, relationships)
    return render_csv(measure_pairs(images, settings))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="output CSV path",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that the output already matches the measured report",
    )
    args = parser.parse_args(argv)
    try:
        report = build_report()
        if args.check:
            try:
                current = args.output.read_bytes()
            except OSError as error:
                raise HomologyError(f"report not found: {args.output}") from error
            if current != report.encode("utf-8"):
                raise HomologyError(
                    f"{args.output}: report is stale; regenerate with "
                    f"{Path(__file__).relative_to(ROOT)}"
                )
            print(f"status=PASS report={args.output} pairs={report.count(chr(10)) - 1}")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report, encoding="utf-8")
            print(f"status=WROTE report={args.output} pairs={report.count(chr(10)) - 1}")
    except HomologyError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
