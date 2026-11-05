"""Exact historical CAN telemetry endpoints accepted for calibration
extraction and upgrade.

Each endpoint of ``can-telemetry-history.toml`` freezes its own geometry: the
unit payloads at their spans, the hook words with the value below the
telemetry layer (``stock``) and the endpoint value, the configuration record,
the erased reserve, and the mailbox record with its stock value. The record
decodes under the frozen contract of its protocol version. An endpoint
therefore stays recognizable when the current telemetry layout moves a unit,
a hook or a record, or when the current configuration protocol changes.
"""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import struct
import tomllib

from patches import can_telemetry


REGISTRY = Path(__file__).with_name("can-telemetry-history.toml")
REGISTRY_SCHEMA_VERSION = 2
BYTE_ORDER = "big"
# The logical profile that every registered endpoint transmits.
PROFILE_NAME = "tuning"
ENDPOINT_KEYS = frozenset({
    "key", "roms", "protocol_version", "profile_id", "page_count",
    "profile_crc16", "configuration_address", "reserved_rom_start",
    "reserved_rom_end", "mailbox_record_address", "mailbox_record_stock",
    "hooks", "units",
})


@dataclass(frozen=True)
class Protocol:
    """The frozen configuration record and mailbox record of one protocol."""

    version: int
    magic: int
    integrity: int
    size: int
    format: str
    max_can_id: int

    def encode(self, configuration, endpoint):
        return struct.pack(
            self.format,
            self.magic,
            self.version,
            int(configuration.enabled),
            endpoint.profile_id,
            endpoint.page_count,
            configuration.tick_divisor,
            0,
            configuration.can_id,
            endpoint.profile_crc16,
            self.integrity,
        )

    def decode(self, record, endpoint):
        record = bytes(record)
        if len(record) != self.size:
            raise ValueError(
                f"historical CAN telemetry configuration is {len(record)} "
                f"bytes, expected {self.size}"
            )
        (
            magic,
            version,
            enabled,
            profile_id,
            page_count,
            tick_divisor,
            reserved,
            can_id,
            profile_crc,
            integrity,
        ) = struct.unpack(self.format, record)
        if not all((
            magic == self.magic,
            version == self.version,
            enabled in (0, 1),
            profile_id == endpoint.profile_id,
            page_count == endpoint.page_count,
            tick_divisor != 0,
            reserved == 0,
            1 <= can_id <= self.max_can_id,
            profile_crc == endpoint.profile_crc16,
            integrity == self.integrity,
        )):
            raise ValueError(
                "historical CAN telemetry configuration contract differs"
            )
        return can_telemetry.Configuration(
            bool(enabled), can_id, PROFILE_NAME, tick_divisor
        )

    @staticmethod
    def mailbox_record(can_id):
        encoded_id = can_id << 5
        return bytes((0x04, 0x08, encoded_id >> 8, encoded_id & 0xFF))


PROTOCOLS = {
    2: Protocol(
        version=2,
        magic=0x4354,
        integrity=0x54454C32,
        size=16,
        format=">H6BHHI",
        max_can_id=0x7FE,
    ),
}


@dataclass(frozen=True)
class Unit:
    key: str
    start: int
    payload: bytes

    @property
    def end(self):
        return self.start + len(self.payload)


@dataclass(frozen=True)
class Hook:
    key: str
    address: int
    width: int
    stock: int
    value: int

    @property
    def end(self):
        return self.address + self.width


@dataclass(frozen=True)
class Endpoint:
    key: str
    roms: tuple[str, ...]
    protocol_version: int
    profile_id: int
    page_count: int
    profile_crc16: int
    configuration_address: int
    reserved_rom_start: int
    reserved_rom_end: int
    mailbox_record_address: int
    mailbox_record_stock: int
    hooks: tuple[Hook, ...]
    units: tuple[Unit, ...]

    @property
    def protocol(self):
        return PROTOCOLS[self.protocol_version]

    @property
    def configuration_end(self):
        return self.configuration_address + self.protocol.size

    def write_ranges(self):
        """Return the (start, end) spans that the endpoint writes. The
        reserve stays erased stock ROM and is not among them."""
        return (
            *((unit.start, unit.end) for unit in self.units),
            (self.configuration_address, self.configuration_end),
            (self.mailbox_record_address, self.mailbox_record_address + 4),
            *((hook.address, hook.end) for hook in self.hooks),
        )

    def write_offsets(self):
        return frozenset(
            offset
            for start, end in self.write_ranges()
            for offset in range(start, end)
        )

    def record(self, source):
        return bytes(source[self.configuration_address : self.configuration_end])

    def configuration(self, record):
        return self.protocol.decode(record, self)

    def encode(self, configuration):
        return self.protocol.encode(configuration, self)

    def matches(self, source):
        """Return whether ``source`` carries the complete endpoint at its own
        addresses with a valid record and its mailbox record."""
        if not all(
            source[unit.start : unit.end] == unit.payload for unit in self.units
        ):
            return False
        reserve = source[self.reserved_rom_start : self.reserved_rom_end]
        if reserve != bytes([0xFF]) * len(reserve):
            return False
        if not all(
            int.from_bytes(source[hook.address : hook.end], BYTE_ORDER)
            == hook.value
            for hook in self.hooks
        ):
            return False
        try:
            model = self.configuration(self.record(source))
        except ValueError:
            return False
        start = self.mailbox_record_address
        return source[start : start + 4] == self.protocol.mailbox_record(
            model.can_id
        )

    def strip(self, source):
        """Return ``source`` with the bytes below the endpoint: erased units
        and record, the stock hook words and the stock mailbox record."""
        data = bytearray(source)
        for unit in self.units:
            data[unit.start : unit.end] = bytes([0xFF]) * len(unit.payload)
        data[self.configuration_address : self.configuration_end] = (
            bytes([0xFF]) * self.protocol.size
        )
        for hook in self.hooks:
            data[hook.address : hook.end] = hook.stock.to_bytes(
                hook.width, BYTE_ORDER
            )
        start = self.mailbox_record_address
        data[start : start + 4] = self.mailbox_record_stock.to_bytes(
            4, BYTE_ORDER
        )
        return data


def _int(value, low, high):
    return type(value) is int and low <= value <= high


def _hooks(rows):
    hooks = []
    for item in rows:
        if (
            set(item) != {"key", "address", "width", "stock", "value"}
            or not isinstance(item["key"], str)
            or not _int(item["width"], 1, 4)
            or not _int(item["address"], 0, 0xFFFFFFFF)
            or not _int(item["stock"], 0, (1 << 8 * item["width"]) - 1)
            or not _int(item["value"], 0, (1 << 8 * item["width"]) - 1)
            or item["stock"] == item["value"]
        ):
            raise ValueError("historical telemetry hook contract differs")
        hooks.append(Hook(**item))
    if not hooks or len({hook.key for hook in hooks}) != len(hooks):
        raise ValueError("historical telemetry hook keys differ")
    return tuple(hooks)


def _units(rows):
    units = []
    for item in rows:
        if (set(item) != {"key", "start", "end", "payload"}
                or type(item["start"]) is not int or type(item["end"]) is not int):
            raise ValueError("historical telemetry unit contract differs")
        unit = Unit(item["key"], item["start"], bytes.fromhex(item["payload"]))
        if not unit.payload or unit.end != item["end"]:
            raise ValueError("historical telemetry unit size differs")
        units.append(unit)
    if not units or len({unit.key for unit in units}) != len(units):
        raise ValueError("historical telemetry unit keys differ")
    return tuple(units)


@lru_cache(maxsize=1)
def endpoints():
    with REGISTRY.open("rb") as source:
        raw = tomllib.load(source)
    if (set(raw) != {"schema_version", "endpoint"}
            or raw["schema_version"] != REGISTRY_SCHEMA_VERSION):
        raise ValueError("historical telemetry registry schema differs")
    found = []
    for row in raw["endpoint"]:
        if (set(row) != ENDPOINT_KEYS
                or row["protocol_version"] not in PROTOCOLS
                or not isinstance(row["key"], str) or row["key"] in {"absent", "current"}
                or not row["roms"] or len(set(row["roms"])) != len(row["roms"])
                or not _int(row["profile_id"], 1, 0x7F)
                or not _int(row["page_count"], 1, 16)
                or not _int(row["profile_crc16"], 0, 0xFFFF)
                or not all(_int(row[name], 0, 0xFFFFFFFF) for name in (
                    "configuration_address", "reserved_rom_start",
                    "reserved_rom_end", "mailbox_record_address",
                    "mailbox_record_stock"))
                or row["reserved_rom_start"] >= row["reserved_rom_end"]):
            raise ValueError("historical telemetry endpoint identity differs")
        endpoint = Endpoint(
            **{key: value for key, value in row.items()
               if key not in ("units", "hooks", "roms")},
            roms=tuple(row["roms"]),
            hooks=_hooks(row["hooks"]),
            units=_units(row["units"]),
        )
        spans = sorted((
            *endpoint.write_ranges(),
            (endpoint.reserved_rom_start, endpoint.reserved_rom_end),
        ))
        if any(left[1] > right[0] for left, right in zip(spans, spans[1:])):
            raise ValueError("historical telemetry endpoint writes overlap")
        found.append(endpoint)
    if len({endpoint.key for endpoint in found}) != len(found):
        raise ValueError("historical telemetry endpoint keys repeat")
    return tuple(found)


def endpoint(key):
    return next((item for item in endpoints() if item.key == key), None)


def write_offsets(rom):
    """Return every offset that a registered endpoint of ``rom`` writes."""
    offsets = set()
    for item in endpoints():
        if rom in item.roms:
            offsets |= item.write_offsets()
    return frozenset(offsets)
