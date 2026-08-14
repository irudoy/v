"""Fail-closed configuration model for the JK08A CAN telemetry runtime."""

from __future__ import annotations

from dataclasses import dataclass
import struct

from patches import can_telemetry_profile


CONFIG_MAGIC = 0x4354
CONFIG_VERSION = 1
CONFIG_INTEGRITY = 0x54454C31
CONFIG_SIZE = 16
STOCK_MAILBOX_RECORD = bytes.fromhex("05000000")


@dataclass(frozen=True)
class Configuration:
    enabled: bool = False
    can_id: int = 0x6F0
    profile: str = "core32"
    tick_divisor: int = 1

    def is_valid(self, manifest=None):
        manifest = manifest or can_telemetry_profile.load_manifest()
        return all((
            type(self.enabled) is bool,
            type(self.can_id) is int,
            1 <= self.can_id <= 0x7FF,
            self.profile in manifest.profile_by_name,
            type(self.tick_divisor) is int,
            1 <= self.tick_divisor <= 0xFF,
        ))

    @property
    def profile_spec(self):
        return can_telemetry_profile.load_manifest().profile_by_name[
            self.profile
        ]

    def to_bytes(self, manifest=None):
        manifest = manifest or can_telemetry_profile.load_manifest()
        if not self.is_valid(manifest):
            raise ValueError("CAN telemetry configuration is invalid")
        profile = manifest.profile_by_name[self.profile]
        return struct.pack(
            ">H6BHHI",
            CONFIG_MAGIC,
            CONFIG_VERSION,
            int(self.enabled),
            profile.profile_id,
            profile.page_count,
            self.tick_divisor,
            0,
            self.can_id,
            profile.crc16,
            CONFIG_INTEGRITY,
        )

    @classmethod
    def from_bytes(cls, data, manifest=None):
        manifest = manifest or can_telemetry_profile.load_manifest()
        data = bytes(data)
        if len(data) != CONFIG_SIZE:
            raise ValueError(
                f"CAN telemetry configuration is {len(data)} bytes, "
                f"expected {CONFIG_SIZE}"
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
        ) = struct.unpack(">H6BHHI", data)
        if enabled not in (0, 1):
            raise ValueError("CAN telemetry enable byte is invalid")
        profile = manifest.profile_by_id.get(profile_id)
        if profile is None:
            raise ValueError("CAN telemetry profile ID is invalid")
        if not all((
            magic == CONFIG_MAGIC,
            version == CONFIG_VERSION,
            page_count == profile.page_count,
            tick_divisor != 0,
            reserved == 0,
            1 <= can_id <= 0x7FF,
            profile_crc == profile.crc16,
            integrity == CONFIG_INTEGRITY,
        )):
            raise ValueError("CAN telemetry configuration contract differs")
        result = cls(bool(enabled), can_id, profile.name, tick_divisor)
        if not result.is_valid(manifest):
            raise ValueError("CAN telemetry decoded configuration is invalid")
        return result

    def mailbox_record(self):
        if not self.enabled:
            return STOCK_MAILBOX_RECORD
        encoded_id = self.can_id << 5
        return bytes((0x04, 0x08, encoded_id >> 8, encoded_id & 0xFF))


def default_configuration():
    manifest = can_telemetry_profile.load_manifest()
    return Configuration(
        enabled=False,
        can_id=manifest.candidate_can_id,
        profile="core32",
        tick_divisor=manifest.candidate_tick_divisor,
    )
