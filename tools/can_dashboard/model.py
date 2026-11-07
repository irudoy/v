"""Pure live-data model and deterministic demo frames for the dashboard."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
from pathlib import Path
import time

from tools.can_dashboard.acceleration import AccelerationTimer
from tools.can_dashboard.selected_map import MAP_COUNT, MapTracker
from tools.can_dashboard import stock
from tools.logs import can_telemetry, can_telemetry_schema


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
    *stock.IDS,
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
    0x01: "MAIN",
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
# A knock surface state with bit 6 set selects the high-detonation ignition
# surface, and one with bit 6 clear the high-octane surface.
HIGH_DETONATION_MASK = 0x40
FUEL_INHIBIT_ALL = 0x3F
# The Rolling Launch hold of the demo source: an RPM regulator at 3900 RPM in
# 12.5 RPM counts with a soft width of 200 RPM, a trim of 10 degrees, an
# efficiency of 82 percent, and an APC command floor. The values are
# plausible and belong to no image calibration.
DEMO_LAUNCH_TARGET = 312
DEMO_LAUNCH_SOFT_WIDTH = 16
DEMO_LAUNCH_TRIM = 10
DEMO_LAUNCH_EFFICIENCY = 820
DEMO_LAUNCH_FLOOR = 120
DEMO_SPARK_EVENTS_PER_REVOLUTION = 3


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


def knock_surface_mode(state):
    """Name the ignition surface a knock surface state selects."""
    return "HIGH DETONATION" if state & HIGH_DETONATION_MASK else "HIGH OCTANE"


# Fields whose value the dashboard names in code rather than by the values or
# bits of their scale.
CODE_DISPLAYS = {
    "fuel_inhibit_mask": inhibited_cylinders,
    "knock_channel_mask_latched": knock_channels,
    "knock_surface_state": knock_surface_mode,
}


def _spelled(name):
    return name.replace("_", " ")


def _packed_display(field):
    """The display of a packed scale: the value of its bit range by its
    conversion or named values, then the names of its set bits."""
    packed = field["field"]
    mask = (1 << (packed["high"] - packed["low"] + 1)) - 1
    bits = tuple(
        (entry["bit"], _spelled(entry["name"])) for entry in field["bits"]
    )
    if "values" in packed:
        names = {
            entry["value"]: _spelled(entry["name"]) for entry in packed["values"]
        }

        def value_text(value):
            return names.get(value, f"0x{value:02X}")
    else:
        conversion = packed["conversion"]
        digits = field.get("dashboard", {}).get("digits", 0)
        unit = can_telemetry.DISPLAY_UNITS.get(
            packed.get("unit", ""), packed.get("unit", "")
        )

        def value_text(value):
            number = value * conversion["factor"] + conversion["offset"]
            return f"{number:.{digits}f}" + (f" {unit}" if unit else "")

    return lambda raw: ", ".join((
        value_text(raw >> packed["low"] & mask),
        *(name for bit, name in bits if raw >> bit & 1),
    ))


def field_display(field, calibration=None):
    """Return the function from the raw value of a field to the value the
    dashboard shows, or None for a field it shows raw.

    A code display names a mask in code; otherwise the calibration of the
    field applies, or the named values or named bits of its scale, or the
    packed value of its scale followed by the names of its set bits. A code
    without a name reads in hexadecimal.
    """
    if field["name"] in CODE_DISPLAYS:
        return CODE_DISPLAYS[field["name"]]
    if calibration is not None:
        return calibration.apply
    if "field" in field:
        return _packed_display(field)
    if "values" in field:
        names = {
            entry["value"]: _spelled(entry["name"]) for entry in field["values"]
        }
        return lambda code: names.get(code, f"0x{code:02X}")
    if "bits" in field:
        bits = tuple(
            (entry["bit"], _spelled(entry["name"])) for entry in field["bits"]
        )
        return lambda mask: ", ".join(
            name for bit, name in bits if mask >> bit & 1
        ) or "none"
    return None


@dataclass(frozen=True)
class FrameRecord:
    arbitration_id: int
    data: bytes
    timestamp: float | None = None
    received_monotonic: float | None = None
    is_extended_id: bool = False
    is_remote_frame: bool = False
    is_error_frame: bool = False
    dlc: int | None = None
    recording_started: float | None = None
    recording_elapsed: float | None = None


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


# One count of the ECU engine-speed coordinate FFFF11F4.
RPM_PER_COUNT = 12.5


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


RATE_WINDOW_SECONDS = 2.0


def _trim_window(samples, now, window=RATE_WINDOW_SECONDS):
    while samples and now - samples[0] > window:
        samples.popleft()


def _window_rate(samples, now, window=RATE_WINDOW_SECONDS):
    _trim_window(samples, now, window)
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
        for field in stock.FIELDS:
            setattr(self, field.key, None)
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
        fields = can_telemetry.profile_fields(self.decoder.profile)
        self._field_names = tuple(field["name"] for field in fields)
        self._configuration_field = can_telemetry.configuration_field(
            self.decoder.profile
        )
        self._dynamic_names = can_telemetry.dynamic_field_names(
            self.decoder.profile
        )
        self.configuration_labels = can_telemetry.configuration_labels(
            self.decoder.profile
        )
        # The configuration byte of the dynamic page of the last snapshot.
        self.page_configuration = None
        # Both converted fields and fields shown raw require a verified layout.
        self._displays = {}
        self._raw_keys = {}
        for field in fields:
            key = can_telemetry.engineering_key(field["name"])
            display = field_display(
                field, self.decoder.calibrations.get(field["name"])
            )
            if display is None:
                self._raw_keys[key] = field["name"]
            else:
                self._displays[key] = (field["name"], display)
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
        # An offline consumer never asks for the rates, so the window is
        # trimmed as it grows.
        _trim_window(self._telemetry_frame_times, now)
        snapshot = self.decoder.feed(
            frame.arbitration_id,
            frame.data,
            frame.timestamp,
        )
        if snapshot is None:
            if self.schema_verified and not self.decoder.schema_verified:
                self._clear_telemetry()
            self.schema_verified = self.decoder.schema_verified
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
        fields = {}
        for name in self._field_names:
            value = values.get(name)
            if _finite(value):
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
        if (
            snapshot.run != self.last_run
            or snapshot.schema_verified != self.schema_verified
        ):
            # Values from an unverified layout cannot become valid merely
            # because a later health context matches the selected schema.
            self._clear_telemetry()
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
        _trim_window(self._snapshot_times, now)
        self.schema_verified = snapshot.schema_verified
        if snapshot.profile_id is not None:
            self.profile_id = snapshot.profile_id
        fields = {
            name: value
            for name, value in snapshot.fields.items()
            if name not in KNOCK_MARGIN_FIELDS or value != KNOCK_MARGIN_IDLE
        }
        selector = snapshot.fields.get(self._configuration_field)
        if selector is not None:
            if (
                self.page_configuration is not None
                and (selector ^ self.page_configuration) & 0x7F
            ):
                # Another configuration fills the dynamic page, so the
                # values that only the previous one carried are not current.
                self._clear_fields(self._dynamic_names - snapshot.fields.keys())
            self.page_configuration = selector
        self.raw.update(fields)
        for name in fields:
            self.updated_at[name] = now
        if self.schema_verified:
            self.engineering.update(
                (key, display(self.raw[name]))
                for key, (name, display) in self._displays.items()
                if name in self.raw
            )

    def _clear_telemetry(self):
        self.raw.clear()
        self.engineering.clear()
        self.updated_at.clear()
        self.page_configuration = None

    def _clear_fields(self, names):
        for name in names:
            self.raw.pop(name, None)
            self.updated_at.pop(name, None)
            self.engineering.pop(can_telemetry.engineering_key(name), None)

    @property
    def page_configuration_id(self):
        """The configuration ID that the verified dynamic page echoes, or
        None."""
        if not self.schema_verified or self.page_configuration is None:
            return None
        return self.page_configuration & 0x7F

    @property
    def page_configuration_label(self):
        """The label of the echoed configuration, or None."""
        configuration_id = self.page_configuration_id
        if configuration_id is None:
            return None
        return self.configuration_labels.get(
            configuration_id, f"Unknown ID {configuration_id}"
        )

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
        for key, value in stock.decode(frame.arbitration_id, data).items():
            setattr(self, key, value)
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
        for field in stock.FIELDS:
            value = values.get(field.key)
            setattr(self, field.key, value if _finite(value) else None)
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

    def value(self, key, default=None):
        """The shown value of a metric key: the engineering value of a
        verified schema, or the raw value of a field shown raw."""
        if not self.schema_verified:
            return default
        if key in self.engineering:
            return self.engineering[key]
        name = self._raw_keys.get(key)
        return default if name is None else self.raw.get(name, default)

    @property
    def engine_speed_counts(self):
        """Engine speed in the RPM/12.5 counts of the ECU coordinate FFFF11F4.

        The stock engine-speed frame carries the word the coordinate is a
        shift of, so the frame serves the coordinate.
        """
        return rpm_counts(self.stock_rpm)

    @property
    def telemetry_map(self):
        """Return the map the telemetry map index names, or None."""
        if not self.schema_verified:
            return None
        index = self.raw.get("active_map_index")
        if index is None:
            return None
        # The runtime reads an index outside the map slots as Map 1.
        return index + 1 if 0 <= index < MAP_COUNT else 1

    @property
    def selected_map(self):
        """The telemetry map index, else the map the stock bus implies."""
        number = self.telemetry_map
        return self.drive.map.number if number is None else number

    @property
    def high_detonation_selected(self):
        if not self.schema_verified or "knock_surface_state" not in self.raw:
            return None
        return int(bool(self.raw["knock_surface_state"] & HIGH_DETONATION_MASK))

    @property
    def telemetry_status_flags(self):
        if not self.schema_verified:
            return {}
        value = self.raw.get("telemetry_status", 0)
        return {
            "overrun_latched": bool(value & 0x01),
            "abort_latched": bool(value & 0x02),
            "event_overflow": bool(value & 0x04),
            "preempted": bool(value & 0x08),
        }


class DemoGenerator:
    """Generate wire-valid tuning groups with realistic changing values.

    A field without a curve of its own takes the default value of its schema,
    so that a new telemetry field needs no demo value. The page commands of
    `control` select the configuration of the dynamic page.
    """

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
        self.fields = can_telemetry.profile_fields(self.profile)
        self.dynamic = self.profile["_layout"].dynamic
        self.configuration_field = can_telemetry.configuration_field(self.profile)
        self.page_configuration = 0
        self.page_group = 0
        self._staging = None
        self.consumed_q_sum = 0

    def control(self, payload):
        """Apply one page command of the control ID as the runtime does and
        report whether it is accepted.

        DEFAULT installs configuration 0. SET stages the width of one slot of
        a configuration ID; a SET of another ID restarts the staging. COMMIT
        installs the staged ID when the profile defines it with exactly the
        staged groups and slot widths, and the next snapshot carries its
        first group. A rejected frame clears the staging and keeps the active
        configuration. The demo has no RAM, so slot addresses go unchecked.
        """
        data = bytes(payload)
        valid = (
            self.dynamic is not None
            and len(data) == 8
            and can_telemetry_schema.crc16_ccitt_false(data[:6])
            == int.from_bytes(data[6:], "big")
        )
        if valid and data[:6] == bytes((0xC0, 0, 0, 0, 0, 0)):
            self._install(0)
            return True
        configuration_id = data[1] if valid else 0
        if (
            valid
            and data[0] == 0xC1
            and 1 <= configuration_id <= 0x7F
            and data[2] >> 4 & 7 < 6
            and data[2] & 0x0F in (1, 2, 4)
        ):
            if self._staging is None or self._staging[0] != configuration_id:
                self._staging = (configuration_id, {})
            self._staging[1][data[2] >> 7, data[2] >> 4 & 7] = data[2] & 0x0F
            return True
        if (
            valid
            and data[0] == 0xC2
            and self._staging is not None
            and self._staging[0] == configuration_id
        ):
            groups = self.dynamic.configurations.get(configuration_id, ())
            counts = [len(placed) for placed in groups] + [0, 0]
            widths = {
                (group, slot): field["width"]
                for group, placed in enumerate(groups)
                for slot, (field, _offset) in enumerate(placed)
            }
            if (
                groups
                and data[2:6] == bytes((len(groups), *counts[:2], 0))
                and self._staging[1] == widths
            ):
                self._install(configuration_id)
                return True
        self._staging = None
        return False

    def _install(self, configuration_id):
        self.page_configuration = configuration_id
        self.page_group = 0
        self._staging = None

    def _page_slots(self, values):
        """Return the (field, offset) pairs of the group that the next
        snapshot carries, or None for the default configuration, and set its
        configuration byte. A two-group configuration alternates its groups
        per snapshot."""
        if not self.page_configuration:
            return None
        groups = self.dynamic.configurations[self.page_configuration]
        group = self.page_group
        self.page_group = (group + 1) % len(groups)
        values[self.configuration_field] = self.page_configuration | group << 7
        return groups[group]

    @staticmethod
    def _rolling_launch(rpm, speed_kmh, timing, launch):
        """Return the views of the Rolling Launch engine.

        ACTIVE holds the RPM regulator of the demo with the trim applied;
        IDLE publishes the inputs with the button released. The views of one
        snapshot agree with each other, but no image calibration produces
        them.
        """
        rpm_sample = round(rpm / 12.5)
        stock_command = 110 - timing
        if not launch:
            return {
                "rolling_launch_control_error_raw": 0,
                "rolling_launch_law_output_raw": 0,
                "rolling_launch_mode_trim": 0,
                "rolling_launch_cut_fraction_raw": 0,
                "rolling_launch_efficiency": 1000,
                "rolling_launch_speed_sample_raw": speed_kmh * 10,
                "rolling_launch_selected_target_raw": 0,
                # Inputs valid, frame age within the limit, source ready,
                # and the button released.
                "rolling_launch_status": 0x1C | 0x40,
                "rolling_launch_rpm_sample_raw": rpm_sample,
                "rolling_launch_stock_command_raw": stock_command,
                "rolling_launch_effective_command_raw": stock_command,
                "rolling_launch_accepted_button_raw": 0x20,
                "rolling_launch_speed_age_raw": 2,
                "ignition_dwell_angle_raw": 52,
            }
        error = rpm_sample - DEMO_LAUNCH_TARGET
        # The firing permission p falls from 1000 at the soft-width edge to
        # 0 at the target, and the cut fraction q is its complement.
        law = 0 if error >= 0 else min(1000, -error * 1000 // DEMO_LAUNCH_SOFT_WIDTH)
        return {
            "rolling_launch_control_error_raw": error,
            "rolling_launch_law_output_raw": law,
            # The trim value with ACTUATION_READY in bit 7; RPM leaves the
            # SPEED bit clear.
            "rolling_launch_mode_trim": DEMO_LAUNCH_TRIM | 0x80,
            "rolling_launch_cut_fraction_raw": 1000 - law,
            "rolling_launch_efficiency": DEMO_LAUNCH_EFFICIENCY | 0x8000,
            "rolling_launch_speed_sample_raw": speed_kmh * 10,
            "rolling_launch_selected_target_raw": DEMO_LAUNCH_TARGET,
            # RPM, the speed inputs valid, CANCEL accepted, and actuation
            # ready.
            "rolling_launch_status": 0x01 | 0x1C | 0x20 | 0x80,
            "rolling_launch_rpm_sample_raw": rpm_sample,
            "rolling_launch_stock_command_raw": stock_command,
            "rolling_launch_effective_command_raw": max(
                stock_command, min(stock_command + DEMO_LAUNCH_TRIM, DEMO_LAUNCH_FLOOR)
            ),
            "rolling_launch_accepted_button_raw": 0x02,
            "rolling_launch_speed_age_raw": 2,
            "ignition_dwell_angle_raw": 46,
        }

    def _consume_cuts(self, values):
        """Advance the wrapping q sum over the spark events of one ACTIVE
        tick and publish it with the count of cut requests it implies."""
        if values["rolling_launch_phase"]:
            events = (
                values["stock_rpm"] / 60
                * DEMO_SPARK_EVENTS_PER_REVOLUTION * BASE_TICK_SECONDS
            )
            self.consumed_q_sum = (
                self.consumed_q_sum
                + round(values["rolling_launch_cut_fraction_raw"] * events)
            ) & 0xFFFFFFFF
        values["rolling_launch_consumed_q_sum_raw"] = self.consumed_q_sum
        values["rolling_launch_cut_counter"] = self.consumed_q_sum // 1000 & 0xFF

    @staticmethod
    def _default(field, wave):
        """Return the demo raw value of a field without a curve of its own.

        A field with a feed channel sweeps the range of the channel on the
        shared wave, converted back to raw by the schema; any other field
        reads zero.
        """
        feed = field.get("dashboard", {}).get("feed")
        if feed is None:
            return 0
        conversion = field["conversion"]
        value = feed["minimum"] + (feed["maximum"] - feed["minimum"]) * wave
        return (value - conversion["offset"]) / conversion["factor"]

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
        values = {
            "stock_rpm": rpm,
            # Both flow coordinates rise with the opening area at a given
            # engine speed, so the demo drives them from the same load wave.
            "request_flow_raw": 655 * load,
            "alpha_n_flow_raw": 16 + 2.39 * load,
            "final_timing_raw": timing,
            "apc_command_raw": 110 - timing,
            "maf_b1_raw": (1.05 + 2.2 * wave) * 200,
            "maf_b2_raw": (1.08 + 2.15 * wave) * 200,
            "maf_total_raw": maf_total * 100,
            # Raw load 128 is the stock JK08A reference schedule word 27226.
            "normalized_load_raw": min(255, bfs_ms * 2048 * 128 / 27226),
            "bfs_raw": bfs_ms * 2048,
            "rolling_launch_phase": 1 if launch else 0,
            **{
                f"injection_{index}_raw": (injection + index * 0.02) * 100
                for index in range(2)
            },
            "knock_timing_state_raw": 0x1020,
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
            "protocol_version": 2,
            "profile_id": self.profile["id"],
            "profile_crc16": int(self.profile["crc16_ccitt_false"], 0),
            "telemetry_page_configuration": 0,
            "ltft_learned_b1_raw": 101.8 * 256,
            "ltft_adjustment_b1_raw": 100.3 * 256,
            "ltft_learned_b2_raw": 101.2 * 256,
            "ltft_adjustment_b2_raw": 100.4 * 256,
            "fuel_learning_permit_a_raw": 3,
            "fuel_learning_permit_b_raw": 3,
            "ltft_publication_neutral_control_raw": 0,
            "knock_state_snapshot_raw": 0x40 if wave > 0.5 else 0,
            "knock_branch_state_raw": 0,
            "transmission_reduction_state_raw": 0x1800 if launch else 0,
            "torque_transition_state_raw": 0x0400 if launch else 0,
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
            **self._rolling_launch(rpm, 55 * wave, timing, launch),
        }
        for field in self.fields:
            if field["name"] not in values:
                values[field["name"]] = self._default(field, wave)
        return values

    def group(self, tick, elapsed=None):
        elapsed = tick * BASE_TICK_SECONDS if elapsed is None else elapsed
        values = self._values(elapsed)
        values["tick16"] = tick & 0xFFFF
        self._consume_cuts(values)
        slots = self._page_slots(values)
        pages = [bytearray(8) for _ in range(self.profile["page_count"])]
        for page, payload in enumerate(pages):
            payload[0] = (((tick & 0x0F) << 4) | page) & 0xFF
        for field in self.profile["fields"]:
            # The slots of a configuration replace the default fields of the
            # data bytes, and the bytes after the last slot stay zero.
            if (
                slots is not None
                and field["page"] == self.dynamic.page
                and field["offset"] < self.dynamic.configuration_offset
            ):
                continue
            self._encode(
                pages[field["page"]],
                field["offset"],
                field,
                values[field["name"]],
            )
        for field, offset in slots or ():
            self._encode(
                pages[self.dynamic.page], offset, field, values[field["name"]]
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

    def stock_context(self, tick, elapsed=None, *, bus_detail=False):
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
        details = (
            FrameRecord(0x176, (500).to_bytes(2, "big") + (1000).to_bytes(2, "big") + bytes(3), elapsed),
            FrameRecord(0x177, bytes((0, 0, gear - 1, 0, 0, 0x78)), elapsed),
            FrameRecord(0x160, bytes.fromhex("32032000000000"), elapsed),
            FrameRecord(0x284, bytes(speed), elapsed),
        ) if bus_detail else ()
        return (
            FrameRecord(TCM_GEAR_ID, bytes(tcm), elapsed),
            *details,
            FrameRecord(STOCK_RPM_ID, bytes(rpm_payload), elapsed),
            FrameRecord(PRND_ID, bytes(prnd), elapsed),
            FrameRecord(ASCD_BUTTON_ID, bytes(button), elapsed),
            FrameRecord(VEHICLE_SPEED_ID, bytes(speed), elapsed),
            FrameRecord(DASHBOARD_STATE_ID, bytes(dashboard), elapsed),
        )
