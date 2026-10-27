"""Local calibration files bound to one registered stock image.

A calibration file lists the bytes of the calibration ranges of an image that
differ from a fresh stock build: the stock bytes for the calibration window
and the Map 1 bytes that a fresh build copies into each Map 2 through Map 5
slot. Each element is a contiguous run inside one calibration range. The
optional ``[settings]`` table holds the SHA-256 of each Rolling Launch and CAN
telemetry configuration record of the source image. It is a check, not a
source: the settings themselves travel in a build profile.

Calibration files are local artifacts. They are written outside the
repository or to a path that Git ignores.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import tomllib

from patches import calibration_ranges
from patches import runtime_targets


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1
ROOT_KEYS = frozenset(
    ("schema_version", "rom", "stock_sha256", "source", "settings", "element")
)
SOURCE_KEYS = frozenset(
    ("sha256", "map_switching", "rolling_launch", "can_telemetry")
)
SETTING_COMPONENTS = ("rolling_launch", "can_telemetry")
ELEMENT_KEYS = frozenset(("address", "size", "data"))
SHA256 = re.compile(r"[0-9a-f]{64}")


class CalibrationFileError(ValueError):
    """Raised when a calibration file or its output path is invalid."""


@dataclass(frozen=True)
class Element:
    address: int
    data: bytes

    @property
    def end(self):
        return self.address + len(self.data)


@dataclass(frozen=True)
class CalibrationFile:
    rom: str
    stock_sha256: str
    source: tuple[tuple[str, str], ...]
    settings: tuple[tuple[str, str], ...]
    elements: tuple[Element, ...]


def require_local_path(path):
    """Refuse an output path that Git would track inside the repository."""
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT):
        return path
    result = subprocess.run(
        ["git", "-C", str(ROOT), "check-ignore", "-q", "--",
         str(path.relative_to(ROOT))],
        check=False,
        capture_output=True,
    )
    if result.returncode == 1:
        raise CalibrationFileError(
            f"{path}: local calibration artifacts must be outside the "
            "repository or in a path that Git ignores, such as tmp/"
        )
    if result.returncode != 0:
        raise CalibrationFileError(
            f"{path}: cannot check the Git ignore rules: "
            f"{result.stderr.decode(errors='replace').strip()}"
        )
    return path


def dumps(calibration):
    """Return the TOML text of a calibration file."""
    lines = [
        f"schema_version = {SCHEMA_VERSION}",
        f'rom = "{calibration.rom}"',
        f'stock_sha256 = "{calibration.stock_sha256}"',
        "",
        "[source]",
    ]
    lines += [f'{key} = "{value}"' for key, value in calibration.source]
    lines += ["", "[settings]"]
    lines += [f'{key} = "{value}"' for key, value in calibration.settings]
    for element in calibration.elements:
        lines += [
            "",
            "[[element]]",
            f"address = 0x{element.address:08X}",
            f"size = {len(element.data)}",
            f'data = "{element.data.hex()}"',
        ]
    return "\n".join(lines) + "\n"


def _require_keys(table, expected, context, optional=frozenset()):
    if not isinstance(table, dict):
        raise CalibrationFileError(f"{context}: expected a TOML table")
    missing = sorted(set(expected) - optional - set(table))
    extra = sorted(set(table) - set(expected))
    if missing or extra:
        raise CalibrationFileError(
            f"{context}: fields differ; missing={missing}; extra={extra}"
        )


def _require_sha256(value, context):
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise CalibrationFileError(f"{context}: expected a SHA-256 digest")
    return value


def loads(text, context):
    """Parse and validate a calibration file against its calibration ranges."""
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise CalibrationFileError(f"{context}: {error}") from error
    _require_keys(raw, ROOT_KEYS, context, optional=frozenset(("element",)))
    if type(raw["schema_version"]) is not int or raw["schema_version"] != SCHEMA_VERSION:
        raise CalibrationFileError(
            f"{context}: unsupported calibration schema {raw['schema_version']!r}"
        )
    rom = raw["rom"]
    if rom not in runtime_targets.SUPPORTED_ROMS:
        raise CalibrationFileError(f"{context}: unsupported ROM {rom!r}")
    stock_sha256 = _require_sha256(raw["stock_sha256"], f"{context}: stock_sha256")

    _require_keys(raw["source"], SOURCE_KEYS, f"{context} [source]")
    source = tuple(
        (key, raw["source"][key])
        for key in ("sha256", "map_switching", "rolling_launch", "can_telemetry")
    )
    _require_sha256(raw["source"]["sha256"], f"{context}: source.sha256")
    for key, value in source[1:]:
        if not isinstance(value, str) or not value:
            raise CalibrationFileError(f"{context}: source.{key} must be a string")

    _require_keys(
        raw["settings"],
        SETTING_COMPONENTS,
        f"{context} [settings]",
        optional=frozenset(SETTING_COMPONENTS),
    )
    settings = tuple(
        (key, _require_sha256(raw["settings"][key], f"{context}: settings.{key}"))
        for key in SETTING_COMPONENTS
        if key in raw["settings"]
    )

    ranges = calibration_ranges.load(rom)
    elements = []
    for index, item in enumerate(raw.get("element", [])):
        label = f"{context}: element {index}"
        _require_keys(item, ELEMENT_KEYS, label)
        address, size, data = item["address"], item["size"], item["data"]
        if type(address) is not int or type(size) is not int or size <= 0:
            raise CalibrationFileError(f"{label}: invalid address or size")
        try:
            data = bytes.fromhex(data) if isinstance(data, str) else None
        except ValueError:
            data = None
        if data is None or len(data) != size:
            raise CalibrationFileError(
                f"{label}: data must be {size} bytes of hexadecimal text"
            )
        element = Element(address, data)
        container = ranges.containing(address)
        if container is None or element.end > container.end:
            raise CalibrationFileError(
                f"{label} at {address:#x} is outside the calibration ranges "
                f"of {rom}"
            )
        if elements and element.address < elements[-1].end:
            raise CalibrationFileError(
                f"{label} at {address:#x} overlaps or precedes the previous element"
            )
        elements.append(element)
    return CalibrationFile(
        rom=rom,
        stock_sha256=stock_sha256,
        source=source,
        settings=settings,
        elements=tuple(elements),
    )


def load(path):
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise CalibrationFileError(f"{path}: cannot load calibration: {error}") from error
    return loads(text, str(path))
