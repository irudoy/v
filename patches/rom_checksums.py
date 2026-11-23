#!/usr/bin/env python3
"""Calculate and verify registered ROM checksum layouts."""

from __future__ import annotations

from array import array
from dataclasses import dataclass, fields, replace
from functools import lru_cache, reduce
from hashlib import sha256
from operator import xor
from pathlib import Path
import re
import sys
import tomllib


DEFAULT_REGISTRY = Path(__file__).with_name("checksum-layouts.toml")
LAYOUT_FIELDS = frozenset(
    {
        "roms",
        "rom_size",
        "recalculation_order",
        "sum16",
        "runtime32",
        "evidence",
    }
)
SUM16_FIELDS = frozenset({"key", "field", "start", "end", "exclusions"})
RUNTIME32_FIELDS = frozenset(
    {"key", "xor_field", "sum_field", "start", "end", "exclusions"}
)
VALUE_FIELDS = (
    "sum16_a",
    "sum16_b",
    "runtime_a_xor",
    "runtime_a_sum",
    "runtime_b_sum",
    "runtime_b_xor",
)


class ChecksumError(ValueError):
    """Raised when a checksum layout or ROM does not satisfy its contract."""


@dataclass(frozen=True)
class Sum16Domain:
    key: str
    field: int
    start: int
    end: int
    exclusions: frozenset[int]


@dataclass(frozen=True)
class Runtime32Domain:
    key: str
    xor_field: int
    sum_field: int
    start: int
    end: int
    exclusions: frozenset[int]


@dataclass(frozen=True)
class BuildStockPrefix:
    end: int
    sha256: str
    retained_sum16: str


@dataclass(frozen=True)
class ChecksumLayout:
    key: str
    roms: tuple[str, ...]
    rom_size: int
    sum16_domains: tuple[Sum16Domain, ...]
    runtime32_domains: tuple[Runtime32Domain, ...]
    recalculation_order: tuple[str, ...]
    evidence: str
    build_stock_prefix: BuildStockPrefix | None = None

    def _sum16(self, key):
        for domain in self.sum16_domains:
            if domain.key == key:
                return domain
        raise AttributeError(f"checksum layout {self.key} has no {key} domain")

    def _runtime32(self, key):
        for domain in self.runtime32_domains:
            if domain.key == key:
                return domain
        raise AttributeError(f"checksum layout {self.key} has no {key} domain")

    @property
    def sum16_a_field(self):
        return self._sum16("sum16_a").field

    @property
    def sum16_a_start(self):
        return self._sum16("sum16_a").start

    @property
    def sum16_a_end(self):
        return self._sum16("sum16_a").end

    @property
    def sum16_b_field(self):
        return self._sum16("sum16_b").field

    @property
    def sum16_b_start(self):
        return self._sum16("sum16_b").start

    @property
    def sum16_b_end(self):
        return self._sum16("sum16_b").end

    @property
    def runtime_a_xor_field(self):
        return self._runtime32("runtime_a").xor_field

    @property
    def runtime_a_sum_field(self):
        return self._runtime32("runtime_a").sum_field

    @property
    def runtime_a_start(self):
        return self._runtime32("runtime_a").start

    @property
    def runtime_a_end(self):
        return self._runtime32("runtime_a").end

    @property
    def runtime_a_exclusions(self):
        return self._runtime32("runtime_a").exclusions

    @property
    def runtime_b_xor_field(self):
        return self._runtime32("runtime_b").xor_field

    @property
    def runtime_b_sum_field(self):
        return self._runtime32("runtime_b").sum_field

    @property
    def runtime_b_start(self):
        return self._runtime32("runtime_b").start

    @property
    def runtime_b_end(self):
        return self._runtime32("runtime_b").end

    @property
    def runtime_b_exclusions(self):
        return self._runtime32("runtime_b").exclusions

    @property
    def checksum_fields(self):
        return tuple(
            (domain.key, domain.field, 2)
            for domain in self.sum16_domains
        ) + tuple(
            field
            for domain in self.runtime32_domains
            for field in (
                (f"{domain.key}_sum", domain.sum_field, 4),
                (f"{domain.key}_xor", domain.xor_field, 4),
            )
        )

    @property
    def domains(self):
        return self.sum16_domains + self.runtime32_domains


@dataclass(frozen=True)
class ChecksumValues:
    sum16_a: int | None = None
    sum16_b: int | None = None
    runtime_a_xor: int | None = None
    runtime_a_sum: int | None = None
    runtime_b_sum: int | None = None
    runtime_b_xor: int | None = None
    extra: tuple[tuple[str, int], ...] = ()

    def items(self):
        standard = tuple(
            (field.name, getattr(self, field.name))
            for field in fields(self)
            if field.name != "extra" and getattr(self, field.name) is not None
        )
        return standard + self.extra

    def __getattr__(self, name):
        for key, value in self.extra:
            if key == name:
                return value
        raise AttributeError(name)


@dataclass(frozen=True)
class ChecksumVerification:
    stored: ChecksumValues
    calculated: ChecksumValues
    retained: tuple[str, ...] = ()

    @property
    def mismatches(self):
        return tuple(
            name
            for name, value in self.stored.items()
            if name not in self.retained and value != getattr(self.calculated, name)
        )

    @property
    def valid(self):
        return not self.mismatches


def _require_int(row, key, context):
    value = row[key]
    if type(value) is not int or value < 0:
        raise ChecksumError(f"{context}.{key} must be a nonnegative integer")
    return value


def _validate_range(start, end, alignment, limit, context):
    if start >= end or start % alignment or end % alignment or end > limit:
        raise ChecksumError(
            f"{context} must be a nonempty {alignment}-byte-aligned range "
            f"inside 0x0..{limit:#x}"
        )


def _validate_key(value, context):
    if (
        not isinstance(value, str)
        or not value
        or not value[0].isalpha()
        or not value.replace("_", "").isalnum()
        or value.lower() != value
    ):
        raise ChecksumError(f"{context}.key must be a lowercase identifier")
    return value


def _parse_exclusions(row, start, end, alignment, context):
    raw = row["exclusions"]
    if (
        not isinstance(raw, list)
        or len(raw) != len(set(raw))
        or any(type(value) is not int for value in raw)
    ):
        raise ChecksumError(f"{context}.exclusions must be a unique integer array")
    if any(value % alignment or not start <= value < end for value in raw):
        raise ChecksumError(
            f"{context}.exclusions contains an unaligned or out-of-range value"
        )
    return frozenset(raw)


def _parse_domain_rows(raw, fields, context):
    if not isinstance(raw, list) or not raw:
        raise ChecksumError(f"{context} must be a nonempty array of tables")
    for index, row in enumerate(raw, 1):
        row_context = f"{context}[{index}]"
        if not isinstance(row, dict) or set(row) != fields:
            actual = set(row) if isinstance(row, dict) else set()
            raise ChecksumError(
                f"{row_context}: fields differ; "
                f"missing={sorted(fields - actual)}; "
                f"extra={sorted(actual - fields)}"
            )
        yield row, row_context


def _parse_layout(key, row, context):
    actual = set(row) if isinstance(row, dict) else set()
    required = LAYOUT_FIELDS
    allowed = required | {"build_stock_prefix"}
    if not required <= actual <= allowed:
        raise ChecksumError(
            f"{context}: fields differ; "
            f"missing={sorted(required - actual)}; "
            f"extra={sorted(actual - allowed)}"
        )
    roms = row["roms"]
    if (
        not isinstance(roms, list)
        or not roms
        or len(set(roms)) != len(roms)
        or any(not isinstance(rom, str) or not rom for rom in roms)
    ):
        raise ChecksumError(f"{context}.roms must be a unique nonempty array")
    if not isinstance(row["evidence"], str) or not row["evidence"].strip():
        raise ChecksumError(f"{context}.evidence must be nonempty text")
    rom_size = _require_int(row, "rom_size", context)
    if rom_size <= 0:
        raise ChecksumError(f"{context}.rom_size must be positive")

    sum16_domains = []
    for domain_row, domain_context in _parse_domain_rows(
        row["sum16"], SUM16_FIELDS, f"{context}.sum16"
    ):
        domain_key = _validate_key(domain_row["key"], domain_context)
        field = _require_int(domain_row, "field", domain_context)
        start = _require_int(domain_row, "start", domain_context)
        end = _require_int(domain_row, "end", domain_context)
        _validate_range(start, end, 2, rom_size, domain_context)
        if field % 2 or field + 2 > rom_size:
            raise ChecksumError(f"{domain_context}.field is not an in-image u16")
        sum16_domains.append(Sum16Domain(
            key=domain_key,
            field=field,
            start=start,
            end=end,
            exclusions=_parse_exclusions(
                domain_row, start, end, 2, domain_context
            ),
        ))

    runtime32_domains = []
    for domain_row, domain_context in _parse_domain_rows(
        row["runtime32"], RUNTIME32_FIELDS, f"{context}.runtime32"
    ):
        domain_key = _validate_key(domain_row["key"], domain_context)
        start = _require_int(domain_row, "start", domain_context)
        end = _require_int(domain_row, "end", domain_context)
        _validate_range(start, end, 4, rom_size, domain_context)
        field_values = {
            name: _require_int(domain_row, name, domain_context)
            for name in ("xor_field", "sum_field")
        }
        for name, field in field_values.items():
            if field % 4 or field + 4 > rom_size:
                raise ChecksumError(
                    f"{domain_context}.{name} is not an in-image u32"
                )
        runtime32_domains.append(Runtime32Domain(
            key=domain_key,
            start=start,
            end=end,
            exclusions=_parse_exclusions(
                domain_row, start, end, 4, domain_context
            ),
            **field_values,
        ))

    domains = tuple(sum16_domains) + tuple(runtime32_domains)
    domain_keys = tuple(domain.key for domain in domains)
    if len(set(domain_keys)) != len(domain_keys):
        raise ChecksumError(f"{context}: checksum domain keys must be unique")
    order = row["recalculation_order"]
    if (
        not isinstance(order, list)
        or len(order) != len(set(order))
        or set(order) != set(domain_keys)
    ):
        raise ChecksumError(
            f"{context}.recalculation_order must contain every domain key once"
        )

    checksum_fields = tuple(
        (domain.key, domain.key, domain.field, 2)
        for domain in sum16_domains
    ) + tuple(
        field
        for domain in runtime32_domains
        for field in (
            (domain.key, f"{domain.key}_xor", domain.xor_field, 4),
            (domain.key, f"{domain.key}_sum", domain.sum_field, 4),
        )
    )
    occupied = set()
    for _domain_key, field_name, field, width in checksum_fields:
        field_bytes = set(range(field, field + width))
        if occupied & field_bytes:
            raise ChecksumError(f"{context}: checksum field {field_name} overlaps")
        occupied.update(field_bytes)
    order_index = {domain_key: index for index, domain_key in enumerate(order)}
    for domain in sum16_domains:
        required = {
            offset
            for field_domain, _name, field, width in checksum_fields
            if (
                field_domain == domain.key
                or order_index[field_domain] > order_index[domain.key]
            )
            for offset in range(field, field + width, 2)
            if domain.start <= offset < domain.end
        }
        if not required <= domain.exclusions:
            missing = ", ".join(
                hex(value) for value in sorted(required - domain.exclusions)
            )
            raise ChecksumError(
                f"{context}.{domain.key}.exclusions misses stored fields: {missing}"
            )
    for domain in runtime32_domains:
        required = {
            field & ~3
            for field_domain, _name, field, width in checksum_fields
            if (
                domain.start <= field
                and field + width <= domain.end
                and (
                    field_domain == domain.key
                    or order_index[field_domain] > order_index[domain.key]
                )
            )
        }
        if not required <= domain.exclusions:
            missing = ", ".join(hex(value) for value in sorted(required - domain.exclusions))
            raise ChecksumError(
                f"{context}.{domain.key}.exclusions misses stored field words: {missing}"
            )

    prefix = None
    if "build_stock_prefix" in row:
        prefix_context = f"{context}.build_stock_prefix"
        raw = row["build_stock_prefix"]
        if not isinstance(raw, dict) or set(raw) != {"end", "sha256", "retained_sum16"}:
            raise ChecksumError(f"{prefix_context}: expected end, sha256 and retained_sum16")
        end = _require_int(raw, "end", prefix_context)
        _validate_range(0, end, 2, rom_size, prefix_context)
        digest = raw["sha256"]
        if not isinstance(digest, str) or re.fullmatch(r"[a-f0-9]{64}", digest) is None:
            raise ChecksumError(f"{prefix_context}.sha256 must be a lowercase SHA-256")
        retained = raw["retained_sum16"]
        if not any(
            domain.key == retained and domain.end <= end and domain.field + 2 <= end
            for domain in sum16_domains
        ):
            raise ChecksumError(f"{prefix_context}.retained_sum16 must lie entirely in the prefix")
        if any(
            field < end < field + width
            for _, _, field, width in checksum_fields
        ):
            raise ChecksumError(f"{prefix_context}.end bisects a checksum field")
        prefix = BuildStockPrefix(end, digest, retained)

    return ChecksumLayout(
        key=key,
        roms=tuple(roms),
        rom_size=rom_size,
        sum16_domains=tuple(sum16_domains),
        runtime32_domains=tuple(runtime32_domains),
        recalculation_order=tuple(order),
        evidence=row["evidence"],
        build_stock_prefix=prefix,
    )


@lru_cache(maxsize=None)
def load_registry(path=DEFAULT_REGISTRY):
    path = Path(path)
    try:
        with path.open("rb") as source:
            document = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ChecksumError(f"checksum registry cannot be loaded: {path}: {error}") from error
    if set(document) != {"schema_version", "layout"}:
        raise ChecksumError(f"{path}: expected only schema_version and layout")
    if document["schema_version"] != 2:
        raise ChecksumError(f"{path}: unsupported schema_version")
    raw_layouts = document["layout"]
    if not isinstance(raw_layouts, dict) or not raw_layouts:
        raise ChecksumError(f"{path}: no [layout.*] entries")
    layouts = {
        key: _parse_layout(key, row, f"{path} [layout.{key}]")
        for key, row in raw_layouts.items()
    }
    by_rom = {}
    for layout in layouts.values():
        for rom in layout.roms:
            if rom in by_rom:
                raise ChecksumError(f"{path}: ROM {rom} belongs to two layouts")
            by_rom[rom] = layout
    return layouts, by_rom


def layout_for_rom(rom, path=DEFAULT_REGISTRY, *, for_build=False):
    """Return exact checksum geometry, optionally enforcing the build prefix."""
    _layouts, by_rom = load_registry(Path(path))
    try:
        layout = by_rom[rom]
    except KeyError as error:
        raise ChecksumError(f"no checksum layout is registered for {rom}") from error
    if not for_build and layout.build_stock_prefix is not None:
        return replace(layout, build_stock_prefix=None)
    return layout


def _validated_data(image, layout):
    data = bytes(image)
    if len(data) != layout.rom_size:
        raise ChecksumError(
            f"image has {len(data)} bytes, expected {layout.rom_size} for {layout.key}"
        )
    return data


def _require_stock_prefix(data, layout):
    prefix = layout.build_stock_prefix
    if prefix is not None and sha256(data[:prefix.end]).hexdigest() != prefix.sha256:
        raise ChecksumError(f"{layout.key}: bytes below {prefix.end:#x} differ from stock")


def _read_unsigned(data, offset, width):
    return int.from_bytes(data[offset : offset + width], "big")


def _write_unsigned(data, offset, width, value):
    data[offset : offset + width] = value.to_bytes(width, "big")


def _native_words(data, start, end, width, exclusions):
    """Prepare current complete words without modifying the image.

    Zero is neutral for both checksum operations. Exclusions therefore
    require no per-word membership test after preparation. Other argument
    shapes retain the scalar reader's partial-range and input behavior.
    """
    if (type(data) not in (bytes, bytearray)
            or type(start) is not int or type(end) is not int
            or type(exclusions) is not frozenset
            or any(type(offset) is not int for offset in exclusions)
            or not 0 <= start <= end <= len(data) or (end - start) % width):
        return None
    words = array('H' if width == 2 else 'I')
    if words.itemsize != width:
        return None
    words.frombytes(memoryview(data)[start:end])
    if sys.byteorder != 'big':
        words.byteswap()
    for offset in exclusions:
        if start <= offset < end and (offset - start) % width == 0:
            words[(offset - start) // width] = 0
    return words


def _sum16(data, start, end, exclusions=frozenset()):
    words = _native_words(data, start, end, 2, exclusions)
    if words is not None:
        return sum(words) & 0xFFFF
    total = 0
    for offset in range(start, end, 2):
        if offset in exclusions:
            continue
        total = (total + _read_unsigned(data, offset, 2)) & 0xFFFF
    return total


def _runtime32(data, start, end, exclusions=frozenset()):
    words = _native_words(data, start, end, 4, exclusions)
    if words is not None:
        return reduce(xor, words, 0), sum(words) & 0xFFFFFFFF
    xor_value = 0
    sum_value = 0
    for offset in range(start, end, 4):
        if offset in exclusions:
            continue
        value = _read_unsigned(data, offset, 4)
        xor_value ^= value
        sum_value = (sum_value + value) & 0xFFFFFFFF
    return xor_value, sum_value


def _checksum_values(values):
    standard = {
        key: values[key]
        for key in VALUE_FIELDS
        if key in values
    }
    extra = tuple(
        (key, value)
        for key, value in values.items()
        if key not in VALUE_FIELDS
    )
    return ChecksumValues(**standard, extra=extra)


def stored_values(image, layout):
    """Read every stored checksum reference for one layout."""
    data = _validated_data(image, layout)
    values = {
        domain.key: _read_unsigned(data, domain.field, 2)
        for domain in layout.sum16_domains
    }
    for domain in layout.runtime32_domains:
        values[f"{domain.key}_xor"] = _read_unsigned(
            data, domain.xor_field, 4
        )
        values[f"{domain.key}_sum"] = _read_unsigned(
            data, domain.sum_field, 4
        )
    return _checksum_values(values)


def calculate_values(image, layout):
    """Calculate every reference from the currently stored image."""
    data = _validated_data(image, layout)
    values = {
        domain.key: _sum16(
            data, domain.start, domain.end, domain.exclusions
        )
        for domain in layout.sum16_domains
    }
    for domain in layout.runtime32_domains:
        xor_value, sum_value = _runtime32(
            data, domain.start, domain.end, domain.exclusions
        )
        values[f"{domain.key}_xor"] = xor_value
        values[f"{domain.key}_sum"] = sum_value
    return _checksum_values(values)


def verify(image, layout):
    """Return stored and calculated values without mutating the image."""
    data = _validated_data(image, layout)
    _require_stock_prefix(data, layout)
    prefix = layout.build_stock_prefix
    return ChecksumVerification(
        stored=stored_values(data, layout),
        calculated=calculate_values(data, layout),
        retained=() if prefix is None else (prefix.retained_sum16,),
    )


def require_valid(image, layout, context="ROM image"):
    """Return verification or raise with every mismatched field."""
    result = verify(image, layout)
    if result.valid:
        return result
    details = ", ".join(
        f"{name}=stored:{getattr(result.stored, name):#x}"
        f"/calculated:{getattr(result.calculated, name):#x}"
        for name in result.mismatches
    )
    raise ChecksumError(f"{context}: checksum mismatch: {details}")


def recalculate(image, layout):
    """Close checksums in dependency order and preserve any build stock prefix."""
    data = bytearray(_validated_data(image, layout))
    _require_stock_prefix(data, layout)
    prefix = layout.build_stock_prefix
    prefix_end = 0 if prefix is None else prefix.end
    sum16_by_key = {domain.key: domain for domain in layout.sum16_domains}
    runtime32_by_key = {
        domain.key: domain for domain in layout.runtime32_domains
    }
    for key in layout.recalculation_order:
        if key in sum16_by_key:
            domain = sum16_by_key[key]
            if domain.field < prefix_end:
                continue
            value = _sum16(
                data, domain.start, domain.end, domain.exclusions
            )
            _write_unsigned(data, domain.field, 2, value)
        else:
            domain = runtime32_by_key[key]
            xor_value, sum_value = _runtime32(
                data, domain.start, domain.end, domain.exclusions
            )
            if domain.sum_field >= prefix_end:
                _write_unsigned(data, domain.sum_field, 4, sum_value)
            if domain.xor_field >= prefix_end:
                _write_unsigned(data, domain.xor_field, 4, xor_value)

    result = bytes(data)
    require_valid(result, layout, f"recalculated {layout.key} image")
    return result


def checksum_byte_offsets(layout):
    """Return the complete set of bytes owned by checksum references."""
    return frozenset(
        offset
        for _name, start, width in layout.checksum_fields
        for offset in range(start, start + width)
    )
