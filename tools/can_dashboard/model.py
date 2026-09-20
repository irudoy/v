"""Pure live-data model and deterministic demo frames for the dashboard."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace
import math
from pathlib import Path
import time

from tools.logs import can_telemetry


STOCK_RPM_ID = 0x180
ASCD_BUTTON_ID = 0x239
VEHICLE_SPEED_ID = 0x280
PRND_ID = 0x421
DASHBOARD_STATE_ID = 0x551
DEFAULT_CAN_ID = 0x6F0
DEFAULT_BITRATE = 500_000
BASE_TICK_SECONDS = 0.01024
OBSERVED_IDS = (
    STOCK_RPM_ID,
    ASCD_BUTTON_ID,
    VEHICLE_SPEED_ID,
    PRND_ID,
    DASHBOARD_STATE_ID,
)

PRND_CODES = {
    0x08: "P",
    0x10: "R",
    0x18: "N",
    0x20: "D",
    0x28: "DS",
    0x80: "M1",
    0x88: "M2",
    0x90: "M3",
    0x98: "M4",
    0xA0: "M5",
}
ASCD_BUTTON_CODES = {
    0x20: "RELEASE",
    0x10: "RES",
    0x08: "SET",
    0x02: "CANCEL",
}
# 0x551 byte 5 carries the three-bit ASCD display state in bits 4..6 over the
# low nibble 0x2. Stock code writes states 0, 4, 5, and 6; the runtime injects
# state 4 for map-selection feedback and state 7 for Rolling Launch ACTIVE.
DASHBOARD_STATE_CODES = {
    0x02: "STOCK",
    0x42: "ASCD STATE 4",
    0x52: "ASCD STATE 5",
    0x62: "ASCD STATE 6",
    0x72: "ASCD STATE 7",
}

# A knock margin latch that reports the idle value saw no evaluation of its
# channel between two captures of its context, or a margin that the signed
# word cannot hold. The model keeps the last evaluated margin of that channel.
KNOCK_MARGIN_IDLE = 0x7FFF
KNOCK_MARGIN_FIELDS = tuple(
    f"knock_margin_min_ch{channel}_raw" for channel in range(1, 7)
)

DASHBOARD_CALIBRATIONS = {
    "final_timing_raw": can_telemetry.Calibration("timing_command_deg"),
    "knock_timing_state_raw": can_telemetry.Calibration(
        "knock_timing_state", 1 / 256
    ),
    "app1_raw": can_telemetry.Calibration("app1_v", 1 / 200),
    "app2_raw": can_telemetry.Calibration("app2_v", 1 / 200),
    "tps_b1_raw": can_telemetry.Calibration("tps_b1_v", 1 / 200),
    "tps_b2_raw": can_telemetry.Calibration("tps_b2_v", 1 / 200),
    "absolute_throttle_raw": can_telemetry.Calibration(
        "absolute_throttle_percent", 100 / 255
    ),
    "fuel_temperature_did_source_raw": can_telemetry.Calibration(
        "fuel_temperature_deg_c", 1.0, -50
    ),
    "oil_temperature_did_source_raw": can_telemetry.Calibration(
        "oil_temperature_deg_c", 1.0, -50
    ),
}


def _dashboard_engineering_values(raw):
    values = {
        calibration.target: calibration.apply(raw[source])
        for source, calibration in DASHBOARD_CALIBRATIONS.items()
        if source in raw
    }
    if "knock_surface_state" in raw:
        values["knock_surface_mode"] = (
            "HIGH DETONATION"
            if raw["knock_surface_state"] & 0x40
            else "HIGH OCTANE"
        )
    return values


@dataclass(frozen=True)
class FrameRecord:
    arbitration_id: int
    data: bytes
    timestamp: float | None = None
    received_monotonic: float | None = None
    is_extended_id: bool = False
    is_remote_frame: bool = False
    is_error_frame: bool = False


@dataclass(frozen=True)
class LiveStats:
    snapshot_hz: float
    telemetry_frame_hz: float
    completed_groups: int
    missed_snapshots: int
    unexpected_tick_steps: int
    producer_restarts: int
    incomplete_groups: int
    malformed_frames: int
    schema_mismatches: int
    error_frames: int
    last_snapshot_age: float | None


def _window_rate(samples, now, window=2.0):
    while samples and now - samples[0] > window:
        samples.popleft()
    if len(samples) < 2:
        return 0.0
    elapsed = samples[-1] - samples[0]
    return (len(samples) - 1) / elapsed if elapsed > 0 else 0.0


class DashboardModel:
    """Retain the latest fixed and rotating fields from strict snapshots."""

    def __init__(
        self,
        profile="tuning",
        can_id=DEFAULT_CAN_ID,
        tick_divisor=1,
        schema_path=can_telemetry.DEFAULT_SCHEMA,
    ):
        if type(tick_divisor) is not int or not 1 <= tick_divisor <= 0xFF:
            raise ValueError("tick_divisor must be in 1..255")
        self.profile = profile
        self.can_id = can_id
        self.tick_divisor = tick_divisor
        self.schema_path = Path(schema_path)
        self.decoder = can_telemetry.Decoder(
            profile, can_id, self.schema_path
        )
        self.raw = {}
        self.engineering = {}
        self.updated_at = {}
        self.schema_verified = False
        self.context_name = None
        self.last_tick = None
        self.last_run = None
        self.last_snapshot_monotonic = None
        self.missed_snapshots = 0
        self.unexpected_tick_steps = 0
        self.error_frames = 0
        self.stock_rpm = None
        self.vehicle_speed_raw = None
        self.vehicle_speed_kmh = None
        self.gear = "?"
        self.gear_raw = None
        self.ascd_button = "?"
        self.ascd_button_raw = None
        self.dashboard_state = "?"
        self.dashboard_state_raw = None
        self.gps_lat = None
        self.gps_lon = None
        self.gps_status = "not observed on primary CAN"
        self._snapshot_times = deque()
        self._telemetry_frame_times = deque()

    def process_frame(self, frame, now=None):
        """Consume a source-neutral frame and return a completed snapshot."""
        if not isinstance(frame, FrameRecord):
            raise TypeError("frame must be FrameRecord")
        if now is None:
            now = (
                frame.received_monotonic
                if frame.received_monotonic is not None
                else time.monotonic()
            )
        if frame.is_error_frame:
            self.error_frames += 1
            return None
        if frame.is_extended_id or frame.is_remote_frame:
            return None

        self._decode_stock_context(frame)
        if frame.arbitration_id != self.can_id:
            return None
        self._telemetry_frame_times.append(now)
        snapshot = self.decoder.feed(
            frame.arbitration_id,
            frame.data,
            frame.timestamp,
        )
        self.schema_verified = self.decoder.schema_verified
        if snapshot is None:
            return None

        if self.last_run is not None and snapshot.run != self.last_run:
            # The controller restarted, so its tick counter starts a new run
            # and the distance across the gap is not a snapshot count.
            self.last_tick = None
        self.last_run = snapshot.run
        if self.last_tick is not None:
            delta = snapshot.unwrapped_tick - self.last_tick
            if delta % self.tick_divisor:
                self.unexpected_tick_steps += 1
            if delta > self.tick_divisor:
                self.missed_snapshots += max(0, delta // self.tick_divisor - 1)
        self.last_tick = snapshot.unwrapped_tick
        self.last_snapshot_monotonic = now
        self._snapshot_times.append(now)
        self.schema_verified = snapshot.schema_verified
        self.context_name = snapshot.context_name
        fields = {
            name: value
            for name, value in snapshot.fields.items()
            if name not in KNOCK_MARGIN_FIELDS or value != KNOCK_MARGIN_IDLE
        }
        self.raw.update(fields)
        for name in fields:
            self.updated_at[name] = now
        if self.schema_verified:
            retained = replace(snapshot, fields=dict(self.raw), schema_verified=True)
            self.engineering.update(can_telemetry.engineering_values(retained))
            self.engineering.update(_dashboard_engineering_values(self.raw))
        return snapshot

    def _decode_stock_context(self, frame):
        data = bytes(frame.data)
        if frame.arbitration_id == STOCK_RPM_ID and len(data) >= 2:
            self.stock_rpm = int.from_bytes(data[0:2], "big") / 8
        elif frame.arbitration_id == VEHICLE_SPEED_ID and len(data) >= 6:
            self.vehicle_speed_raw = int.from_bytes(data[4:6], "big")
            self.vehicle_speed_kmh = self.vehicle_speed_raw / 100
        elif frame.arbitration_id == ASCD_BUTTON_ID and len(data) >= 4:
            self.ascd_button_raw = data[3]
            self.ascd_button = ASCD_BUTTON_CODES.get(
                data[3], f"0x{data[3]:02X}"
            )
        elif frame.arbitration_id == PRND_ID and data:
            self.gear_raw = data[0]
            if data[0] == 0:
                self.gear = "TRANSITION"
            else:
                self.gear = PRND_CODES.get(data[0], f"0x{data[0]:02X}")
        elif frame.arbitration_id == DASHBOARD_STATE_ID and len(data) >= 6:
            self.dashboard_state_raw = data[5]
            self.dashboard_state = DASHBOARD_STATE_CODES.get(
                data[5], f"0x{data[5]:02X}"
            )

    def stats(self, now=None):
        now = time.monotonic() if now is None else now
        snapshot_hz = _window_rate(self._snapshot_times, now)
        frame_hz = _window_rate(self._telemetry_frame_times, now)
        age = None
        if self.last_snapshot_monotonic is not None:
            age = max(0.0, now - self.last_snapshot_monotonic)
        return LiveStats(
            snapshot_hz=snapshot_hz,
            telemetry_frame_hz=frame_hz,
            completed_groups=self.decoder.completed_groups,
            missed_snapshots=self.missed_snapshots,
            unexpected_tick_steps=self.unexpected_tick_steps,
            producer_restarts=self.decoder.producer_restarts,
            incomplete_groups=self.decoder.incomplete_groups,
            malformed_frames=self.decoder.malformed_frames,
            schema_mismatches=self.decoder.schema_mismatches,
            error_frames=self.error_frames,
            last_snapshot_age=age,
        )

    def field_age(self, name, now=None):
        now = time.monotonic() if now is None else now
        updated = self.updated_at.get(name)
        return None if updated is None else max(0.0, now - updated)

    def value(self, name, default=None):
        if self.schema_verified and name in self.engineering:
            return self.engineering[name]
        return self.raw.get(name, default)

    @property
    def high_detonation_selected(self):
        if not self.schema_verified or "knock_surface_state" not in self.raw:
            return None
        return int(bool(self.raw["knock_surface_state"] & 0x40))

    @property
    def telemetry_status_flags(self):
        value = self.raw.get("telemetry_status", 0)
        return {
            "overrun_latched": bool(value & 0x01),
            "abort_latched": bool(value & 0x02),
            "event_overflow": bool(value & 0x04),
            "preempted": bool(value & 0x08),
        }


class DemoGenerator:
    """Generate wire-valid tuning groups with realistic changing values."""

    def __init__(
        self,
        can_id=DEFAULT_CAN_ID,
        profile="tuning",
        schema_path=can_telemetry.DEFAULT_SCHEMA,
    ):
        self.can_id = can_id
        _document, profiles = can_telemetry.load_schema(schema_path)
        try:
            self.profile = profiles[profile]
        except KeyError as error:
            raise ValueError(f"unknown telemetry profile: {profile}") from error
        self.context_by_page_and_tag = {
            (item["page"], item["tag"]): item
            for item in self.profile["contexts"]
        }
        self.context_count = 1 + max(
            tag for _page, tag in self.context_by_page_and_tag
        )

    @staticmethod
    def _encode(payload, offset, field, value):
        width = field["width"]
        signed = field["signed"]
        minimum = -(1 << (width * 8 - 1)) if signed else 0
        maximum = (1 << (width * 8 - (1 if signed else 0))) - 1
        value = max(minimum, min(maximum, int(round(value))))
        payload[offset:offset + width] = value.to_bytes(
            width, "big", signed=signed
        )

    def _values(self, elapsed):
        wave = (math.sin(elapsed * 0.9) + 1) / 2
        rpm = 850 + 3100 * wave
        load = 18 + 62 * wave
        maf_total = 4 + rpm * load / 28_000
        injection = 1.4 + load / 28
        cvtc = 4 + 27 * wave
        return {
            "rpm_raw": rpm / 12.5,
            "final_timing_raw": 8 + 12 * (1 - wave),
            "apc_command_raw": 80 + 90 * wave,
            "fuel_inhibit_mask": 0,
            "maf_b1_raw": (1.05 + 2.2 * wave) * 200,
            "maf_b2_raw": (1.08 + 2.15 * wave) * 200,
            "maf_total_raw": maf_total * 100,
            "front_oxygen_sensor_b1_raw": 128 + 12 * math.sin(elapsed * 2.1),
            "bfs_raw": (2.0 + 4.0 * wave) * 2048,
            "front_oxygen_sensor_b2_raw": 128 + 11 * math.sin(elapsed * 2.0 + 0.2),
            **{
                f"injection_{index}_raw": (injection + index * 0.02) * 100
                for index in range(6)
            },
            "telemetry_status": 0,
            "knock_timing_state_raw": 0x1020,
            "knock_surface_state": 0,
            "knock_count_latched": 1 if wave > 0.94 else 0,
            "knock_channel_mask_latched": 0x04 if wave > 0.94 else 0,
            "app1_raw": 250 + 700 * wave,
            "app2_raw": 245 + 690 * wave,
            "tps_b1_raw": 300 + 2500 * wave,
            "absolute_throttle_raw": 20 + 180 * wave,
            "tps_b2_raw": 310 + 2480 * wave,
            "intake_cvtc_actual_b1_raw": (cvtc + 64) * 2,
            "intake_cvtc_actual_b2_raw": (cvtc - 0.5 + 64) * 2,
            "intake_cvtc_target_raw": (5 + 35 * wave + 64) * 2,
            "exhaust_cvtc_target_raw": (20 * wave + 64) * 2,
            "calculated_load_raw": load * 255 / 100,
            "throttle_request_bounded_raw": 900 + 2400 * wave,
            "engine_torque_state_raw": (45 + 210 * wave) * 10,
            "injection_end_angle_raw": 266 + 134 * wave,
            "exhaust_cvtc_actual_b1_raw": (2 + 18 * wave + 64) * 2,
            "throttle_target_shared_raw": 1000 + 2600 * wave,
            "throttle_target_channel_0_raw": 1050 + 2550 * wave,
            "throttle_target_channel_1_raw": 1030 + 2520 * wave,
            "exhaust_cvtc_actual_b2_raw": (1.5 + 17.5 * wave + 64) * 2,
            "coolant_raw": 90 + 50,
            "iat_raw": 32 + 50,
            "fuel_temperature_did_source_raw": 78,
            "oil_temperature_did_source_raw": 126,
            "af_state_factor_raw": 16_384,
            "stft_b1_raw": (
                100 + 1.7 * math.sin(elapsed * 0.4)
            ) * 256,
            "stft_b2_raw": (
                100 + 1.4 * math.sin(elapsed * 0.4 + 0.3)
            ) * 256,
            "intake_cvtc_duty_b1_raw": (18 + 55 * wave) * 256 / 100,
            "intake_cvtc_duty_b2_raw": (19 + 54 * wave) * 256 / 100,
            "ltft_b1_raw": 102.1 * 256,
            "ltft_b2_raw": 101.6 * 256,
            "timing_state_2023_raw": 0x12,
            "timing_state_564c_raw": 0x20,
            "protocol_version": 2,
            "profile_id": self.profile["id"],
            "profile_crc16": int(self.profile["crc16_ccitt_false"], 0),
            "snapshot_overrun_count": 0,
            "tx_abort_count": 0,
            "intake_cvtc_duty_command_b1_raw": (18 + 55 * wave) * 100 / 39,
            "intake_cvtc_duty_command_b2_raw": (19 + 54 * wave) * 100 / 39,
            "ltft_learned_b1_raw": 101.8 * 256,
            "ltft_adjustment_b1_raw": 100.3 * 256,
            "exhaust_cvtc_duty_b1_word_raw": (12 + 48 * wave) * 1024 / 100,
            "exhaust_cvtc_duty_b2_word_raw": (13 + 47 * wave) * 1024 / 100,
            "atmospheric_pressure_raw": 100,
            "battery_voltage_raw": 175,
            "front_af_sensor_b1_word_raw": 1200 + 500 * wave,
            "front_af_sensor_b2_word_raw": 1180 + 510 * wave,
            "af_adjustment_b1_raw": 0x4000 + 400 * math.sin(elapsed),
            "secondary_tps_b1_raw": 280 + 2450 * wave,
            "secondary_tps_b2_raw": 290 + 2430 * wave,
            "af_adjustment_b2_raw": 0x4000 + 380 * math.sin(elapsed + 0.2),
            **{
                name: (
                    KNOCK_MARGIN_IDLE
                    if index == 5 and wave < 0.5
                    else -120 - 40 * index
                    if index == 2 and wave > 0.94
                    else 900 - 650 * wave + 35 * index
                )
                for index, name in enumerate(KNOCK_MARGIN_FIELDS)
            },
        }

    def group(self, tick, elapsed=None):
        elapsed = tick * BASE_TICK_SECONDS if elapsed is None else elapsed
        values = self._values(elapsed)
        values["tick16"] = tick & 0xFFFF
        pages = [bytearray(8) for _ in range(self.profile["page_count"])]
        for page, payload in enumerate(pages):
            payload[0] = (((tick & 0x0F) << 4) | page) & 0xFF
        for field in self.profile["fields"]:
            self._encode(
                pages[field["page"]],
                field["offset"],
                field,
                values[field["name"]],
            )
        context_tag = (tick - 1) % self.context_count
        for page in (9, 10):
            pages[page][1] = context_tag
            offset = 2
            context = self.context_by_page_and_tag[(page, context_tag)]
            for field in context["fields"]:
                self._encode(
                    pages[page], offset, field, values[field["name"]]
                )
                offset += field["width"]
        return tuple(
            FrameRecord(self.can_id, bytes(payload), elapsed)
            for payload in pages
        )

    def stock_context(self, tick, elapsed=None):
        elapsed = tick * BASE_TICK_SECONDS if elapsed is None else elapsed
        values = self._values(elapsed)
        rpm = int(values["rpm_raw"] * 12.5)
        rpm_payload = bytearray(8)
        rpm_payload[0:2] = int(rpm * 8).to_bytes(2, "big")
        prnd = bytearray(8)
        prnd[0] = 0x20
        button = bytearray(8)
        button[3] = 0x20
        speed = bytearray(8)
        speed_kmh = 55 * ((math.sin(elapsed * 0.9) + 1) / 2)
        speed[4:6] = int(speed_kmh * 100).to_bytes(2, "big")
        dashboard = bytearray(8)
        dashboard[5] = 0x72 if rpm > 3200 else 0x02
        return (
            FrameRecord(STOCK_RPM_ID, bytes(rpm_payload), elapsed),
            FrameRecord(PRND_ID, bytes(prnd), elapsed),
            FrameRecord(ASCD_BUTTON_ID, bytes(button), elapsed),
            FrameRecord(VEHICLE_SPEED_ID, bytes(speed), elapsed),
            FrameRecord(DASHBOARD_STATE_ID, bytes(dashboard), elapsed),
        )
