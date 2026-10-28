"""Exact historical telemetry endpoints accepted for calibration extraction."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import tomllib

from patches import can_telemetry, can_telemetry_profile


REGISTRY = Path(__file__).with_name("can-telemetry-history.toml")


@dataclass(frozen=True)
class Unit:
    key: str
    start: int
    payload: bytes

    @property
    def end(self):
        return self.start + len(self.payload)


@dataclass(frozen=True)
class Endpoint:
    key: str
    roms: tuple[str, ...]
    protocol_version: int
    profile_id: int
    page_count: int
    profile_crc16: int
    units: tuple[Unit, ...]

    def manifest(self):
        profile = can_telemetry_profile.Profile(
            "tuning", self.profile_id, self.page_count, self.profile_crc16
        )
        return SimpleNamespace(profile_by_id={self.profile_id: profile},
                               profile_by_name={profile.name: profile})

    def configuration(self, record):
        manifest = self.manifest()
        model = can_telemetry.Configuration.from_bytes(record, manifest)
        if model.to_bytes(manifest) != record:
            raise ValueError("historical telemetry configuration does not round trip")
        return model

    def matches(self, source, layout):
        current = layout.assembly_unit_by_key
        return (set(current) == {unit.key for unit in self.units}
                and all(unit.start == current[unit.key].span.start
                        and unit.end == current[unit.key].span.end
                        and source[unit.start:unit.end] == unit.payload
                        for unit in self.units))


@lru_cache(maxsize=1)
def endpoints():
    with REGISTRY.open("rb") as source:
        raw = tomllib.load(source)
    if set(raw) != {"schema_version", "endpoint"} or raw["schema_version"] != 1:
        raise ValueError("historical telemetry registry schema differs")
    found = []
    for row in raw["endpoint"]:
        if (set(row) != {"key", "roms", "protocol_version", "profile_id", "page_count",
                         "profile_crc16", "units"}
                or row["protocol_version"] != can_telemetry.CONFIG_VERSION
                or not isinstance(row["key"], str) or row["key"] in {"absent", "current"}
                or not row["roms"] or len(set(row["roms"])) != len(row["roms"])
                or any(type(row[name]) is not int for name in
                       ("profile_id", "page_count", "profile_crc16"))
                or not 1 <= row["profile_id"] <= 0x7F or not 1 <= row["page_count"] <= 16
                or not 0 <= row["profile_crc16"] <= 0xFFFF):
            raise ValueError("historical telemetry endpoint identity differs")
        units = []
        for item in row["units"]:
            if (set(item) != {"key", "start", "end", "payload"}
                    or type(item["start"]) is not int or type(item["end"]) is not int):
                raise ValueError("historical telemetry unit contract differs")
            unit = Unit(item["key"], item["start"], bytes.fromhex(item["payload"]))
            if not unit.payload or unit.end != item["end"]:
                raise ValueError("historical telemetry unit size differs")
            if any(unit.start < held.end and held.start < unit.end for held in units):
                raise ValueError("historical telemetry units overlap")
            units.append(unit)
        if not units or len({unit.key for unit in units}) != len(units):
            raise ValueError("historical telemetry unit keys differ")
        found.append(Endpoint(**{key: value for key, value in row.items()
                                 if key not in ("units", "roms")},
                              roms=tuple(row["roms"]), units=tuple(units)))
    if len({endpoint.key for endpoint in found}) != len(found):
        raise ValueError("historical telemetry endpoint keys repeat")
    return tuple(found)


def endpoint(key):
    return next((item for item in endpoints() if item.key == key), None)
