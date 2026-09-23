"""Pure live-data model and deterministic demo frames for the dashboard."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace
import math
from pathlib import Path
import time

from tools.can_dashboard.acceleration import AccelerationTimer
from tools.can_dashboard.selected_map import MAP_COUNT, MapTracker
from tools.logs import can_telemetry


TCM_GEAR_ID = 0x174
STOCK_RPM_ID = 0x180
ASCD_BUTTON_ID = 0x239
VEHICLE_SPEED_ID = 0x280
PRND_ID = 0x421
DASHBOARD_STATE_ID = 0x551
DEFAULT_CAN_ID = 0x6F0
DEFAULT_BITRATE = 500_000
BASE_TICK_SECONDS = 0.01024
OBSERVED_IDS = (
    TCM_GEAR_ID,
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
# 0x174 byte 3 carries the target gear in its high nibble and the current gear
# in its low nibble. The ECU reads nibbles 1 through 7 as gears; P and N read
# 0xAA and R reads 0x99.
TCM_GEARS = range(1, 8)
ASCD_BUTTON_CODES = {
    0x20: "RELEASE",
    0x10: "RES",
    0x08: "SET",
    0x02: "CANCEL",
}
# 0x551 byte 5 carries the three-bit ASCD display state in bits 4..6 over the
# low nibble 0x2. Stock code writes states 0, 4, 5, and 6. The runtime injects
# state 4 for map-selection feedback and Rolling Launch ACTIVE and state 5 for a
# failed held attempt; firmware through 1.11 injects states 6 and 7.
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
# Retired profile IDs name some slots of the current profile differently.
# The model keeps such a slot under its current name, so the display, the
# MLG recorder, and the replay treat every ID alike.
RENAMED_FIELDS = {
    "timing_state_564c_raw": "ignition_timing_adjustment_raw",
}
# Rolling Launch phase and abort reason codes of the runtime state bytes
# 0xFFFF5D40 and 0xFFFF5D41, in the order of the enumerations of
# patches/rolling_launch.py.
ROLLING_LAUNCH_PHASES = ("IDLE", "ACTIVE", "COOLDOWN")
ROLLING_LAUNCH_ABORT_REASONS = (
    "NONE",
    "CONFIG INVALID",
    "MAP INDEX INVALID",
    "MAP DISABLED",
    "SELECTOR BUSY",
    "FEEDBACK BUSY",
    "ASCD ACTIVE",
    "BUTTON RELEASED",
    "BUTTON INVALID",
    "SPEED LOW",
    "RPM LOW",
    "PEDAL LOW",
    "COOLANT OUTSIDE",
    "RESERVED 13",
    "TIMEOUT",
    "MAP REQUEST",
    "STATE CORRUPT",
    "MAP CHANGED",
    "MODE CHANGED",
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
    "secondary_tps_b1_raw": can_telemetry.Calibration(
        "secondary_tps_b1_v", 1 / 200
    ),
    "secondary_tps_b2_raw": can_telemetry.Calibration(
        "secondary_tps_b2_v", 1 / 200
    ),
    "absolute_throttle_raw": can_telemetry.Calibration(
        "absolute_throttle_percent", 100 / 255
    ),
    "fuel_temperature_did_source_raw": can_telemetry.Calibration(
        "fuel_temperature_deg_c", 1.0, -50
    ),
    "oil_temperature_did_source_raw": can_telemetry.Calibration(
        "oil_temperature_deg_c", 1.0, -50
    ),
    "apc_command_raw": can_telemetry.Calibration("apc_command_deg", -1.0, 110),
    "ignition_timing_adjustment_raw": can_telemetry.Calibration(
        "ignition_timing_adjustment_deg", signed_bits=8
    ),
    "throttle_request_bounded_raw": can_telemetry.Calibration(
        "torque_request_nm", 0.1
    ),
    "throttle_target_shared_raw": can_telemetry.Calibration(
        "throttle_area_request_cm2", 0.0008
    ),
    # One target count is one count of throttle opening coordinate table
    # 0x155A0, whose code scale is the J1979 PID 0x11 gradient
    # 0x505B / 65536 / 4 * 100 / 255 percent.
    "throttle_target_channel_0_raw": can_telemetry.Calibration(
        "throttle_target_b1_percent", 34285 / 1114112
    ),
    "throttle_target_channel_1_raw": can_telemetry.Calibration(
        "throttle_target_b2_percent", 34285 / 1114112
    ),
    # One coordinate count is one count of the column axis the coordinate
    # indexes directly, 0x14114 and 0x11D4C, so the conversion is the
    # candidate percent scale of that axis.
    "request_flow_raw": can_telemetry.Calibration(
        "request_flow_percent", 0.00152588
    ),
    "alpha_n_flow_raw": can_telemetry.Calibration(
        "alpha_n_flow_percent", 0.390625
    ),
    "front_af_sensor_b1_word_raw": can_telemetry.Calibration(
        "af_sensor_b1_v", 1 / 200
    ),
    "front_af_sensor_b2_word_raw": can_telemetry.Calibration(
        "af_sensor_b2_v", 1 / 200
    ),
    "af_adjustment_b1_raw": can_telemetry.Calibration(
        "af_adjustment_b1", 0.002, signed_bits=16
    ),
    "af_adjustment_b2_raw": can_telemetry.Calibration(
        "af_adjustment_b2", 0.002, signed_bits=16
    ),
    # The zero-based slot index of the map-switching runtime names Map
    # index + 1; the runtime reads an index outside the slots as Map 1.
    "active_map_index": can_telemetry.Calibration(
        "selected_map_number", 1.0, 1
    ),
}

FUEL_INHIBIT_ALL = 0x3F


def _set_bits(mask):
    return " ".join(str(bit + 1) for bit in range(8) if mask >> bit & 1)


def inhibited_cylinders(mask):
    """Name the cylinders a fuel inhibit mask cuts; bit k is cylinder k + 1."""
    if mask == 0:
        return "none"
    if mask == FUEL_INHIBIT_ALL:
        return "all"
    return f"cyl {_set_bits(mask)}"


def knock_channels(mask):
    """Name the knock channels a latched mask holds; bit c - 1 is channel c."""
    return "none" if mask == 0 else f"ch {_set_bits(mask)}"


def _code_name(names, code):
    return names[code] if 0 <= code < len(names) else f"0x{code:02X}"


def current_field_name(name):
    """Return the current name of a field that a retired ID names."""
    return RENAMED_FIELDS.get(name, name)


def profile_field_names(profile):
    """Return the current fixed and context field names of one profile."""
    return tuple(
        current_field_name(field["name"]) for field in profile["fields"]
    ) + tuple(
        current_field_name(field["name"])
        for context in profile.get("contexts", ())
        for field in context["fields"]
    )


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
    if "fuel_inhibit_mask" in raw:
        values["fuel_inhibit_cylinders"] = inhibited_cylinders(
            raw["fuel_inhibit_mask"]
        )
    if "knock_channel_mask_latched" in raw:
        values["knock_channels_latched"] = knock_channels(
            raw["knock_channel_mask_latched"]
        )
    if "rolling_launch_phase" in raw:
        values["rolling_launch_phase_name"] = _code_name(
            ROLLING_LAUNCH_PHASES, raw["rolling_launch_phase"]
        )
    if "rolling_launch_abort_reason" in raw:
        values["rolling_launch_abort_name"] = _code_name(
            ROLLING_LAUNCH_ABORT_REASONS, raw["rolling_launch_abort_reason"]
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
class SnapshotRecord:
    """One snapshot of a dashboard MLG recording, raw values by source."""

    timestamp: float
    values: dict
    received_monotonic: float | None = None


FRAME_CLOCK_TOLERANCE_SECONDS = 1.0


def _finite(value) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def speed_counts(stock_rpm):
    """The ECU engine-speed word FFFF11EE from a stock engine-speed value.

    Bytes 0 and 1 of frame 0x180 carry that word multiplied by 25 and
    saturated at 0xFFFF, and the decoded value is the byte pair over 8, so
    the pair recovers the word. The result counts 3.125 RPM.
    """

    if not _finite(stock_rpm):
        return None
    return int(round(stock_rpm * 8)) // 25


def rpm_counts(stock_rpm):
    """The ECU engine-speed coordinate FFFF11F4 in counts of 12.5 RPM.

    FUN_000384FE writes FFFF11EE as FFFF1196 >> 4 and FFFF11F4 as
    FFFF1196 >> 6 in one pass, so the coordinate is the word FFFF11EE that
    the stock frame publishes shifted by two.
    """

    counts = speed_counts(stock_rpm)
    return None if counts is None else counts >> 2


class FrameClock:
    """Elapsed seconds of one source session, measured on the frame clock.

    A frame carries the time it reached the interface, while the host dequeue
    time collapses a burst drained from the driver queue onto a single tick.
    Elapsed time starts at the offset of the first frame from the session
    start and then advances by the interface step, or by the host receive step
    when the source reports no frame time. An interface clock that steps
    backwards, or ahead of the host clock by more than the queueing
    tolerance, is abandoned without breaking elapsed time.
    """

    def __init__(self, started: float):
        self.started = started
        self.source_clock = False
        self._source_time = None
        self._host_time = None
        self._elapsed = 0.0

    def elapsed(self, frame, fallback: float):
        host_time = (
            frame.received_monotonic
            if _finite(frame.received_monotonic)
            else fallback
        )
        if not _finite(self.started) or not _finite(host_time):
            return None
        if host_time < self.started:
            return None
        source_time = (
            frame.timestamp
            if _finite(frame.timestamp) and frame.timestamp >= 0.0
            else None
        )
        if self._host_time is None:
            self.source_clock = source_time is not None
            self._source_time = source_time
            self._host_time = host_time
            self._elapsed = host_time - self.started
            return self._elapsed
        host_step = max(host_time - self._host_time, 0.0)
        source_step = (
            source_time - self._source_time
            if self.source_clock
            and source_time is not None
            and self._source_time is not None
            else None
        )
        if source_step is None:
            step = host_step
        elif 0.0 <= source_step <= host_step + FRAME_CLOCK_TOLERANCE_SECONDS:
            step = source_step
        else:
            self.source_clock = False
            step = host_step
        self._source_time = source_time
        self._host_time = host_time
        self._elapsed += step
        return self._elapsed


class DriveObserver:
    """Feed the selected-map tracker and the acceleration timer.

    Both consume source time: the interface or file time of a frame, or the
    elapsed time of a recorded snapshot. Replay restores a copy of this
    observer at a seek target, so everything it keeps is plain state.
    """

    def __init__(self, can_id=DEFAULT_CAN_ID):
        self.can_id = can_id
        self.map = MapTracker()
        self.acceleration = AccelerationTimer()

    def frame(self, time, can_id, data):
        self.map.activity(time)
        if can_id == self.can_id:
            if len(data) == 8 and data[0] & 0x0F == 0:
                self.map.tick(time, int.from_bytes(data[1:3], "big"))
        elif can_id == VEHICLE_SPEED_ID and len(data) >= 6:
            self.acceleration.speed(
                time, int.from_bytes(data[4:6], "big") / 100
            )
        elif can_id == ASCD_BUTTON_ID and len(data) >= 4:
            self.map.button(time, data[3])
        elif can_id == DASHBOARD_STATE_ID and len(data) >= 6:
            self.map.dashboard(time, data[5])

    def record(self, time, values):
        self.map.activity(time)
        tick = values.get("tick16")
        if _finite(tick):
            self.map.tick(time, int(tick))
        speed = values.get("vehicle_speed_kmh")
        if _finite(speed):
            self.acceleration.speed(time, speed)
        button = values.get("ascd_button_raw")
        if _finite(button):
            self.map.button(time, int(button))
        dashboard = values.get("dashboard_state_raw")
        if _finite(dashboard):
            self.map.dashboard(time, int(dashboard))


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
    """Retain the latest fixed and rotating fields from strict snapshots.

    The fields belong to the profile ID the stream identifies. A stream of a
    retired ID keeps the fields of that ID, and a change of ID drops every
    retained field the new ID does not carry.
    """

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
        self.profile_id = None
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
        self.tcm_gear = None
        self.ascd_button = "?"
        self.ascd_button_raw = None
        self.dashboard_state = "?"
        self.dashboard_state_raw = None
        self.gps_lat = None
        self.gps_lon = None
        self.gps_status = "not observed on primary CAN"
        self.drive = DriveObserver(can_id)
        self.clock = None
        self.recorded_groups = 0
        self._record_tick = None
        self._record_run = 0
        self._record_unwrapped = None
        self._field_names = profile_field_names(self.decoder.profile)
        self._version_fields = {
            profile_id: frozenset(profile_field_names(version))
            for profile_id, version in self.decoder.versions.items()
        }
        # A recording of a retired ID carries the fields of that ID, which the
        # current profile need not publish, so a record is read over every
        # name a known profile names and then limited to the fields of the ID
        # the record itself states.
        self._known_field_names = tuple(
            dict.fromkeys(
                self._field_names
                + tuple(
                    name
                    for version in self.decoder.versions.values()
                    for name in profile_field_names(version)
                )
            )
        )
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

        event_time = self._event_time(frame, now)
        if event_time is not None:
            self.drive.frame(
                event_time, frame.arbitration_id, bytes(frame.data)
            )
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
        self._accept_snapshot(snapshot, now)
        return snapshot

    def process_record(self, record, now=None):
        """Consume one snapshot of a dashboard MLG recording.

        The recording holds the raw value of every field at each snapshot, so
        a record replaces a decoded group: it carries no page, context tag,
        or health context of its own, and its verification is the one the
        recording dashboard held.
        """
        if not isinstance(record, SnapshotRecord):
            raise TypeError("record must be SnapshotRecord")
        if now is None:
            now = (
                record.received_monotonic
                if record.received_monotonic is not None
                else time.monotonic()
            )
        values = record.values
        self.drive.record(record.timestamp, values)
        self._record_stock_context(values)
        tick = values.get("tick16")
        if not _finite(tick):
            return None
        tick16 = int(tick) & 0xFFFF
        if self._record_tick is None:
            unwrapped = tick16
        else:
            delta = (tick16 - self._record_tick) & 0xFFFF
            if delta == 0 or delta >= 0x8000:
                if not can_telemetry.is_producer_restart(
                    self._record_tick, tick16
                ):
                    return None
                self._record_run += 1
                unwrapped = tick16
            else:
                unwrapped = self._record_unwrapped + delta
        self._record_tick = tick16
        self._record_unwrapped = unwrapped
        verified = values.get("schema_verified") == 1
        profile_id = values.get("profile_id")
        profile_id = (
            int(profile_id) if verified and _finite(profile_id) else None
        )
        carried = self._version_fields.get(profile_id, self._field_names)
        fields = {}
        for name in self._known_field_names:
            value = values.get(name)
            if name in carried and _finite(value):
                fields[name] = int(round(value))
        snapshot = can_telemetry.Snapshot(
            tick16=tick16,
            run=self._record_run,
            unwrapped_tick=unwrapped,
            sequence=tick16 & 0x0F,
            fields=fields,
            context_tag=None,
            context_name=None,
            schema_verified=verified,
            timestamp=record.timestamp,
            profile_id=profile_id,
        )
        self.recorded_groups += 1
        self._accept_snapshot(snapshot, now)
        return snapshot

    def _event_time(self, frame, now):
        if self.clock is not None:
            return self.clock.elapsed(frame, now)
        return frame.timestamp if _finite(frame.timestamp) else now

    def _accept_snapshot(self, snapshot, now):
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
        if (
            snapshot.profile_id is not None
            and snapshot.profile_id != self.profile_id
        ):
            self._select_version(snapshot.profile_id)
        fields = {
            current_field_name(name): value
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

    def _select_version(self, profile_id):
        """Keep only the retained fields that the new profile ID carries."""
        self.profile_id = profile_id
        names = self._version_fields.get(profile_id)
        if names is None:
            return
        for retained in (self.raw, self.updated_at):
            for name in [name for name in retained if name not in names]:
                del retained[name]
        # The snapshot that selected the ID rebuilds the engineering values.
        self.engineering.clear()

    def _set_gear(self, code):
        self.gear_raw = code
        if code == 0:
            self.gear = "TRANSITION"
        else:
            self.gear = PRND_CODES.get(code, f"0x{code:02X}")

    def _set_tcm_gear(self, code):
        current = code & 0x0F
        self.tcm_gear = current if current in TCM_GEARS else None

    def _set_ascd_button(self, code):
        self.ascd_button_raw = code
        self.ascd_button = ASCD_BUTTON_CODES.get(code, f"0x{code:02X}")

    def _set_dashboard_state(self, code):
        self.dashboard_state_raw = code
        self.dashboard_state = DASHBOARD_STATE_CODES.get(code, f"0x{code:02X}")

    def _decode_stock_context(self, frame):
        data = bytes(frame.data)
        if frame.arbitration_id == STOCK_RPM_ID and len(data) >= 2:
            self.stock_rpm = int.from_bytes(data[0:2], "big") / 8
        elif frame.arbitration_id == TCM_GEAR_ID and len(data) >= 4:
            self._set_tcm_gear(data[3])
        elif frame.arbitration_id == VEHICLE_SPEED_ID and len(data) >= 6:
            self.vehicle_speed_raw = int.from_bytes(data[4:6], "big")
            self.vehicle_speed_kmh = self.vehicle_speed_raw / 100
        elif frame.arbitration_id == ASCD_BUTTON_ID and len(data) >= 4:
            self._set_ascd_button(data[3])
        elif frame.arbitration_id == PRND_ID and data:
            self._set_gear(data[0])
        elif frame.arbitration_id == DASHBOARD_STATE_ID and len(data) >= 6:
            self._set_dashboard_state(data[5])

    def _record_stock_context(self, values):
        rpm = values.get("stock_rpm")
        if _finite(rpm):
            self.stock_rpm = rpm
        speed = values.get("vehicle_speed_kmh")
        if _finite(speed):
            self.vehicle_speed_raw = int(round(speed * 100))
            self.vehicle_speed_kmh = self.vehicle_speed_raw / 100
        for name, setter in (
            ("gear_raw", self._set_gear),
            ("ascd_button_raw", self._set_ascd_button),
            ("dashboard_state_raw", self._set_dashboard_state),
        ):
            code = values.get(name)
            if _finite(code):
                setter(int(code))
        if "tcm_gear" in values:
            # A recording stores NaN where the TCM reports no forward gear.
            gear = values["tcm_gear"]
            self.tcm_gear = (
                int(gear) if _finite(gear) and int(gear) in TCM_GEARS else None
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
            completed_groups=(
                self.decoder.completed_groups + self.recorded_groups
            ),
            missed_snapshots=self.missed_snapshots,
            unexpected_tick_steps=self.unexpected_tick_steps,
            producer_restarts=(
                self.decoder.producer_restarts + self._record_run
            ),
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
    def engine_speed_counts(self):
        """Engine speed in the RPM/12.5 counts of the ECU coordinate FFFF11F4.

        A profile that publishes the coordinate serves it from the snapshot.
        Otherwise the stock engine-speed frame carries the word the coordinate
        is a shift of, so the two sources name one quantity.
        """
        published = self.raw.get("rpm_raw")
        if published is not None:
            return int(published)
        return rpm_counts(self.stock_rpm)

    @property
    def telemetry_map(self):
        """Return the map the telemetry map index names, or None."""
        if not self.schema_verified:
            return None
        number = self.engineering.get("selected_map_number")
        if number is None:
            return None
        number = int(number)
        return number if 1 <= number <= MAP_COUNT else 1

    @property
    def selected_map(self):
        """The telemetry map index, else the map the stock bus implies."""
        number = self.telemetry_map
        return self.drive.map.number if number is None else number

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
        timing = round(8 + 12 * (1 - wave))
        bfs_ms = 2.0 + 4.0 * wave
        launch = wave > 0.97
        return {
            "stock_rpm": rpm,
            # Both flow coordinates rise with the opening area at a given
            # engine speed, so the demo drives them from the same load wave.
            "request_flow_raw": 655 * load,
            "alpha_n_flow_raw": 16 + 2.39 * load,
            "final_timing_raw": timing,
            "apc_command_raw": 110 - timing,
            "fuel_inhibit_mask": 0,
            "maf_b1_raw": (1.05 + 2.2 * wave) * 200,
            "maf_b2_raw": (1.08 + 2.15 * wave) * 200,
            "maf_total_raw": maf_total * 100,
            # Raw load 128 is the stock JK08A reference schedule word 27226.
            "normalized_load_raw": min(255, bfs_ms * 2048 * 128 / 27226),
            "bfs_raw": bfs_ms * 2048,
            "rolling_launch_phase": 1 if launch else 0,
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
            "tps_b1_raw": 100 + 720 * wave,
            "absolute_throttle_raw": 20 + 180 * wave,
            "tps_b2_raw": 104 + 716 * wave,
            "intake_cvtc_actual_b1_raw": (cvtc + 64) * 2,
            "intake_cvtc_actual_b2_raw": (cvtc - 0.5 + 64) * 2,
            "intake_cvtc_target_raw": (5 + 35 * wave + 64) * 2,
            "exhaust_cvtc_target_raw": (20 * wave + 64) * 2,
            "calculated_load_raw": load * 255 / 100,
            "throttle_request_bounded_raw": 70 + 2400 * wave,
            "engine_torque_state_raw": (45 + 210 * wave) * 10,
            "injection_end_angle_raw": 266 + 134 * wave,
            "exhaust_cvtc_actual_b1_raw": (2 + 18 * wave + 64) * 2,
            "throttle_target_shared_raw": 800 + 26_000 * wave,
            "throttle_target_channel_0_raw": 60 + 2200 * wave,
            "throttle_target_channel_1_raw": 64 + 2190 * wave,
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
            "active_map_index": 0,
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
            # IDLE names its first failed gate: CANCEL is not held.
            "rolling_launch_abort_reason": 0 if launch else 8,
            "battery_voltage_raw": 175,
            "front_af_sensor_b1_word_raw": 440 + 12 * math.sin(elapsed * 2.1),
            "front_af_sensor_b2_word_raw": 438 + 11 * math.sin(elapsed * 2.0 + 0.2),
            "af_adjustment_b1_raw": round(60 * math.sin(elapsed)),
            "secondary_tps_b1_raw": 98 + 722 * wave,
            "secondary_tps_b2_raw": 102 + 718 * wave,
            "af_adjustment_b2_raw": round(55 * math.sin(elapsed + 0.2)),
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
        rpm = int(values["stock_rpm"])
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
        tcm = bytearray(8)
        gear = min(5, 1 + int(speed_kmh // 12))
        tcm[3] = gear << 4 | gear
        return (
            FrameRecord(TCM_GEAR_ID, bytes(tcm), elapsed),
            FrameRecord(STOCK_RPM_ID, bytes(rpm_payload), elapsed),
            FrameRecord(PRND_ID, bytes(prnd), elapsed),
            FrameRecord(ASCD_BUTTON_ID, bytes(button), elapsed),
            FrameRecord(VEHICLE_SPEED_ID, bytes(speed), elapsed),
            FrameRecord(DASHBOARD_STATE_ID, bytes(dashboard), elapsed),
        )
