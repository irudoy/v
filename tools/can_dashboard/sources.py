"""Background PCAN, demo, PEAK TRC, and candump replay sources."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import time

from tools.can_dashboard.model import (
    BASE_TICK_SECONDS,
    DEFAULT_BITRATE,
    DEFAULT_CAN_ID,
    OBSERVED_IDS,
    DemoGenerator,
    FrameRecord,
)
from tools.logs import peak_trc_audit
from tools.logs.can_telemetry import parse_candump_line


@dataclass(frozen=True)
class SourceStatus:
    state: str
    detail: str


@dataclass(frozen=True)
class PcanConfiguration:
    channel: str = "PCAN_USBBUS1"
    bitrate: int = DEFAULT_BITRATE
    can_id: int = DEFAULT_CAN_ID
    listen_only: bool = True
    reset_channel: bool = False


def _reset_pcan_channel(channel):
    """Release a PCAN-Basic channel before opening it again.

    MacCAN can retain an initialized channel after an interrupted client. The
    Cansult macOS tools avoid that state by explicitly uninitializing the
    handle before constructing python-can's Bus. The return code is
    intentionally ignored: an already-uninitialized channel is the desired
    precondition, and the following Bus initialization reports real failures.
    """
    from can.interfaces.pcan.basic import PCANBasic, PCAN_CHANNEL_NAMES

    normalized = channel.strip().upper()
    try:
        handle = PCAN_CHANNEL_NAMES[normalized]
    except KeyError as error:
        raise ValueError(f"unknown PCAN channel: {channel}") from error
    PCANBasic().Uninitialize(handle)


def _check_pcan_driver():
    """Load the PCAN-Basic library without changing channel state."""
    from can.interfaces.pcan.basic import PCANBasic

    PCANBasic()


def run_pcan(config, stop_event, emit):
    """Read selected frames through python-can's PCAN-Basic backend."""
    try:
        import can
    except ImportError:
        emit(SourceStatus("error", "python-can is not installed"))
        return

    filters = [
        {"can_id": can_id, "can_mask": 0x7FF, "extended": False}
        for can_id in (config.can_id, *OBSERVED_IDS)
    ]
    state = can.BusState.PASSIVE if config.listen_only else can.BusState.ACTIVE
    try:
        if config.reset_channel:
            _reset_pcan_channel(config.channel)
        bus = can.Bus(
            interface="pcan",
            channel=config.channel,
            bitrate=config.bitrate,
            state=state,
            can_filters=filters,
            receive_own_messages=False,
            ignore_config=True,
        )
    except Exception as error:
        if config.reset_channel:
            try:
                _reset_pcan_channel(config.channel)
            except Exception:
                pass
        emit(SourceStatus("error", f"PCAN initialization failed: {error}"))
        return

    mode = "listen-only" if config.listen_only else "active/ACK"
    emit(SourceStatus("connected", f"{config.channel}, {config.bitrate} bit/s, {mode}"))
    terminal_error = None
    try:
        while not stop_event.is_set():
            try:
                message = bus.recv(timeout=0.1)
            except Exception as error:
                terminal_error = f"PCAN receive failed: {error}"
                break
            if message is None:
                continue
            emit(FrameRecord(
                arbitration_id=message.arbitration_id,
                data=bytes(message.data),
                timestamp=message.timestamp,
                received_monotonic=time.monotonic(),
                is_extended_id=message.is_extended_id,
                is_remote_frame=message.is_remote_frame,
                is_error_frame=message.is_error_frame,
            ))
    finally:
        cleanup_errors = []
        try:
            bus.shutdown()
        except Exception as error:
            cleanup_errors.append(f"shutdown failed: {error}")
        if config.reset_channel:
            try:
                _reset_pcan_channel(config.channel)
            except Exception as error:
                cleanup_errors.append(f"channel release failed: {error}")
        if cleanup_errors:
            detail = "; ".join(cleanup_errors)
            terminal_error = (
                f"{terminal_error}; {detail}" if terminal_error else detail
            )
        if terminal_error:
            emit(SourceStatus("error", terminal_error))
        else:
            emit(SourceStatus("stopped", "PCAN channel closed"))


def run_demo(can_id, stop_event, emit):
    generator = DemoGenerator(can_id)
    emit(SourceStatus("connected", "deterministic demo source"))
    tick = 1
    started = time.monotonic()
    deadline = started
    while not stop_event.is_set():
        now = time.monotonic()
        if now < deadline:
            stop_event.wait(deadline - now)
            continue
        elapsed = now - started
        for frame in generator.group(tick, elapsed):
            emit(FrameRecord(
                frame.arbitration_id,
                frame.data,
                frame.timestamp,
                now,
            ))
        if tick % 10 == 0:
            for frame in generator.stock_context(tick, elapsed):
                emit(FrameRecord(
                    frame.arbitration_id,
                    frame.data,
                    frame.timestamp,
                    now,
                ))
        tick = (tick + 1) & 0xFFFF
        deadline += BASE_TICK_SECONDS
        if now - deadline > 0.25:
            deadline = now + BASE_TICK_SECONDS
    emit(SourceStatus("stopped", "demo source stopped"))


def _wait_for_replay(timestamp, first_timestamp, started, speed, stop_event):
    if first_timestamp is None:
        first_timestamp = timestamp
    target = started + (timestamp - first_timestamp) / speed
    delay = target - time.monotonic()
    if delay > 0 and stop_event.wait(delay):
        return first_timestamp, False
    return first_timestamp, True


def _run_peak_replay(path, stop_event, emit, speed):
    trace = peak_trc_audit.load_trace(path)
    first_timestamp = None
    started = time.monotonic()
    records = sorted(
        (*trace.frames, *trace.status_records),
        key=lambda record: record.number,
    )
    for record in records:
        if stop_event.is_set():
            break
        timestamp = record.offset_ms / 1000.0
        first_timestamp, ready = _wait_for_replay(
            timestamp,
            first_timestamp,
            started,
            speed,
            stop_event,
        )
        if not ready:
            break
        if isinstance(record, peak_trc_audit.StatusRecord):
            if record.kind == "Error":
                emit(FrameRecord(
                    arbitration_id=0,
                    data=b"",
                    timestamp=timestamp,
                    received_monotonic=time.monotonic(),
                    is_error_frame=True,
                ))
            continue
        emit(FrameRecord(
            arbitration_id=record.can_id,
            data=record.data,
            timestamp=timestamp,
            received_monotonic=time.monotonic(),
            is_extended_id=record.extended,
            is_remote_frame=record.remote,
        ))


def _run_candump_replay(path, stop_event, emit, speed):
    first_timestamp = None
    started = time.monotonic()
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            if stop_event.is_set():
                break
            parsed = parse_candump_line(line)
            if parsed is None:
                continue
            can_id, payload, timestamp = parsed
            if timestamp is not None:
                first_timestamp, ready = _wait_for_replay(
                    timestamp,
                    first_timestamp,
                    started,
                    speed,
                    stop_event,
                )
                if not ready:
                    break
            emit(FrameRecord(
                can_id,
                payload,
                timestamp,
                time.monotonic(),
            ))


def run_replay(path, stop_event, emit, speed=1.0):
    if (
        not isinstance(speed, (int, float))
        or not math.isfinite(speed)
        or speed <= 0
    ):
        emit(SourceStatus("error", "replay speed must be positive"))
        return
    path = Path(path)
    emit(SourceStatus("connected", f"replay {path.name}"))
    try:
        if path.suffix.lower() == ".trc":
            _run_peak_replay(path, stop_event, emit, speed)
        else:
            _run_candump_replay(path, stop_event, emit, speed)
    except (OSError, UnicodeError, peak_trc_audit.TraceError) as error:
        emit(SourceStatus("error", f"replay failed: {error}"))
        return
    emit(SourceStatus("stopped", "replay complete"))
