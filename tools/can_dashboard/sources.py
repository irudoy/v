"""Background PCAN and demo sources."""

from __future__ import annotations

from dataclasses import dataclass
import queue
import threading
import time

from tools.can_dashboard.model import (
    BASE_TICK_SECONDS,
    DEFAULT_BITRATE,
    DEFAULT_CAN_ID,
    OBSERVED_IDS,
    DemoGenerator,
    FrameRecord,
)


# The application owns one PCAN source, including its asynchronous cleanup.
_PCAN_SESSION = threading.Lock()


@dataclass(frozen=True)
class SourceStatus:
    state: str
    detail: str


@dataclass(frozen=True)
class ControlStatus:
    state: str
    detail: str
    command: str | None = None


@dataclass(frozen=True)
class ControlRequest:
    command: str
    can_id: int
    payload: bytes


@dataclass(frozen=True)
class PcanConfiguration:
    channel: str = "PCAN_USBBUS1"
    bitrate: int = DEFAULT_BITRATE
    can_id: int = DEFAULT_CAN_ID
    listen_only: bool = False
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


def _send_control_requests(bus, can_module, config, requests, emit):
    if requests is None:
        return
    while True:
        try:
            request = requests.get_nowait()
        except queue.Empty:
            return
        if config.listen_only:
            emit(ControlStatus(
                "error",
                "stream control requires an active/ACK connection",
                request.command,
            ))
            continue
        try:
            message = can_module.Message(
                arbitration_id=request.can_id,
                data=request.payload,
                is_extended_id=False,
                is_remote_frame=False,
            )
            bus.send(message, timeout=0.1)
        except Exception as error:
            emit(ControlStatus(
                "error",
                f"telemetry {request.command.upper()} failed: {error}",
                request.command,
            ))
            continue
        emit(ControlStatus(
            "sent",
            f"telemetry {request.command.upper()} sent on 0x{request.can_id:03X}",
            request.command,
        ))


def run_pcan(config, stop_event, emit, control_requests=None):
    """Serialize PCAN open, receive and complete cleanup across reconnects."""
    if stop_event.is_set():
        emit(SourceStatus("stopped", "PCAN connection cancelled"))
        return
    if not _PCAN_SESSION.acquire(blocking=False):
        emit(SourceStatus("connecting", "waiting for previous PCAN source to close"))
        while not stop_event.is_set():
            if _PCAN_SESSION.acquire(timeout=0.1):
                break
        else:
            emit(SourceStatus("stopped", "PCAN connection cancelled"))
            return
    try:
        if stop_event.is_set():
            emit(SourceStatus("stopped", "PCAN connection cancelled"))
            return
        _run_pcan(config, stop_event, emit, control_requests)
    finally:
        _PCAN_SESSION.release()


def _run_pcan(config, stop_event, emit, control_requests):
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
    terminal_error = None
    try:
        emit(SourceStatus("connected", f"{config.channel}, {config.bitrate} bit/s, {mode}"))
        while not stop_event.is_set():
            _send_control_requests(
                bus,
                can,
                config,
                control_requests,
                emit,
            )
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


def run_demo(
    can_id,
    stop_event,
    emit,
    profile="tuning",
    schema_path=None,
):
    options = {"profile": profile}
    if schema_path is not None:
        options["schema_path"] = schema_path
    generator = DemoGenerator(can_id, **options)
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

