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
from tools.logs.can_telemetry_schema import PAGE_COMMANDS


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
    # The least time in seconds after the previous control frame. The ECU
    # consumes at most one control frame per 10.24 ms tick from a mailbox
    # that does not overwrite, so frames of one configuration keep a spacing.
    spacing: float = 0.0


class ControlPacing:
    """The request that waits for its spacing and the send time of the
    previous control frame of one connection."""

    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.pending = None
        self.last_sent = None

    def wait(self, limit):
        """The receive timeout that wakes the sender when the pending
        request is due, at most ``limit``."""
        if self.pending is None or self.last_sent is None:
            return limit
        due = self.last_sent + self.pending.spacing - self.clock()
        return max(0.0, min(limit, due))


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


def _send_control_requests(bus, can_module, config, requests, emit, pacing=None):
    """Send the queued control frames in order, each no sooner than its
    spacing after the previous frame; a request whose spacing has not
    elapsed waits in ``pacing`` for a later call."""
    if requests is None:
        return
    if pacing is None:
        pacing = ControlPacing()
    while True:
        request = pacing.pending
        if request is None:
            try:
                request = requests.get_nowait()
            except queue.Empty:
                return
        if (
            pacing.last_sent is not None
            and pacing.clock() - pacing.last_sent < request.spacing
        ):
            pacing.pending = request
            return
        pacing.pending = None
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
            pacing.last_sent = pacing.clock()
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


def run_pcan(config, stop_event, emit, control_requests=None, capture=None):
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
        _run_pcan(config, stop_event, emit, control_requests, capture)
    finally:
        _PCAN_SESSION.release()


def _run_pcan(config, stop_event, emit, control_requests, capture=None):
    """Read selected frames through python-can's PCAN-Basic backend."""
    try:
        import can
    except ImportError:
        emit(SourceStatus("error", "python-can is not installed"))
        return

    data_ids = {config.can_id, *OBSERVED_IDS}
    state = can.BusState.PASSIVE if config.listen_only else can.BusState.ACTIVE
    try:
        if config.reset_channel:
            _reset_pcan_channel(config.channel)
        bus = can.Bus(
            interface="pcan",
            channel=config.channel,
            bitrate=config.bitrate,
            state=state,
            # Select data after recv so error-frame identifiers are preserved.
            can_filters=None,
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
    pacing = ControlPacing()
    try:
        emit(SourceStatus("connected", f"{config.channel}, {config.bitrate} bit/s, {mode}"))
        while not stop_event.is_set():
            _send_control_requests(
                bus,
                can,
                config,
                control_requests,
                emit,
                pacing,
            )
            try:
                message = bus.recv(timeout=pacing.wait(0.1))
            except Exception as error:
                terminal_error = f"PCAN receive failed: {error}"
                break
            if message is None:
                continue
            frame = FrameRecord(
                arbitration_id=message.arbitration_id,
                data=bytes(message.data),
                timestamp=message.timestamp,
                received_monotonic=time.monotonic(),
                is_extended_id=message.is_extended_id,
                is_remote_frame=message.is_remote_frame,
                is_error_frame=message.is_error_frame,
                dlc=getattr(message, "dlc", None),
            )
            if capture is not None:
                frame = capture(frame)
            if not frame.is_error_frame and (
                frame.is_extended_id or frame.arbitration_id not in data_ids
            ):
                continue
            emit(frame)
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


def _demo_control(generator, requests, emit):
    """Consume at most one queued control frame, as the ECU does per tick.

    A page frame on the control ID reaches the page commands of the
    generator and reports `sent`, as a PCAN transmission does; the demo,
    like the ECU, answers no frame. START and STOP have no demo
    counterpart and report an error.
    """
    if requests is None:
        return
    try:
        request = requests.get_nowait()
    except queue.Empty:
        return
    if request.command not in PAGE_COMMANDS.values():
        emit(ControlStatus(
            "error",
            f"telemetry {request.command.upper()} has no demo counterpart",
            request.command,
        ))
        return
    if request.can_id == generator.can_id + 1:
        generator.control(request.payload)
    emit(ControlStatus(
        "sent",
        f"telemetry {request.command.upper()} sent to the demo source",
        request.command,
    ))


def run_demo(
    can_id,
    stop_event,
    emit,
    profile="tuning",
    schema_path=None,
    capture=None,
    control_requests=None,
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
        # A COMMIT applies to the group of the same tick.
        _demo_control(generator, control_requests, emit)
        for frame in generator.group(tick, elapsed):
            received = FrameRecord(
                frame.arbitration_id,
                frame.data,
                frame.timestamp,
                now,
            )
            emit(capture(received) if capture is not None else received)
        if tick % 10 == 0:
            for frame in generator.stock_context(tick, elapsed, bus_detail=True):
                received = FrameRecord(
                    frame.arbitration_id,
                    frame.data,
                    frame.timestamp,
                    now,
                )
                emit(capture(received) if capture is not None else received)
        tick = (tick + 1) & 0xFFFF
        deadline += BASE_TICK_SECONDS
        if now - deadline > 0.25:
            deadline = now + BASE_TICK_SECONDS
    emit(SourceStatus("stopped", "demo source stopped"))

