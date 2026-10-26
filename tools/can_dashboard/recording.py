"""MLVLG recording for decoded VQ CAN telemetry snapshots."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import math
import os
from pathlib import Path
import tempfile

from tools.logs import mlvlg
from tools.logs import can_telemetry


DEFAULT_SCHEMA = can_telemetry.DEFAULT_SCHEMA
MAX_GAP_SECONDS = 0.3
SYNC_RECORD_INTERVAL = 100
LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class FieldBinding:
    spec: mlvlg.FieldSpec
    source: str
    source_kind: str = "raw"


@dataclass(frozen=True)
class RecordingSummary:
    output: Path
    output_existed: bool
    fields: int
    event_records: int
    bridge_records: int
    record_length: int
    output_size: int

    @property
    def records(self) -> int:
        return self.event_records + self.bridge_records


@dataclass(frozen=True)
class RecoverySummary:
    source: Path
    output: Path
    validation: mlvlg.ValidationSummary
    excluded_bytes: int
    tail_error: str | None


def _publish_recording(temporary: Path, output: Path, *, force: bool = False) -> None:
    if force:
        os.replace(temporary, output)
    else:
        os.link(temporary, output)
        temporary.unlink()


def recover_recording(source: Path, output: Path) -> RecoverySummary:
    """Copy and validate the retained record prefix without changing its source."""
    source, output = Path(source), Path(output)
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    prefix = mlvlg.scan_mlg_prefix(source)
    source_size = source.stat().st_size
    if source_size < prefix.valid_bytes:
        raise mlvlg.MlvlgError("recording became shorter after prefix validation")
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        prefix=f".{output.name}.recovery.", suffix=".tmp", dir=output.parent
    )
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as destination, source.open("rb") as original:
            remaining = prefix.valid_bytes
            while remaining:
                chunk = original.read(min(remaining, 1024 * 1024))
                if not chunk:
                    raise mlvlg.MlvlgError("recording became shorter during recovery")
                if destination.write(chunk) != len(chunk):
                    raise OSError("short recording recovery write")
                remaining -= len(chunk)
            destination.flush()
            os.fsync(destination.fileno())
        validation = mlvlg.validate_mlg(temporary)
        if validation != prefix.validation:
            raise mlvlg.MlvlgError("copied recording prefix differs from its validation")
        _publish_recording(temporary, output)
    except Exception:
        try:
            temporary.unlink(missing_ok=True)
        except OSError as error:
            LOG.warning("incomplete recovery copy retained at %s: %s", temporary, error)
        raise
    return RecoverySummary(
        source=source, output=output, validation=validation,
        excluded_bytes=source_size-prefix.valid_bytes, tail_error=prefix.tail_error,
    )


def current_channel_name(name: str) -> str:
    """Return the name of a recorded channel without candidate marks.

    A channel keeps its identity when its transform gains or loses the
    candidate marker.
    """

    return name.replace("*", "").strip()


def mlg_scaling(calibration) -> tuple[float, float]:
    """Return the MLVLG scale and transform of one field calibration.

    MegaLogViewer evaluates ``(raw + transform) * scale``, so the transform is
    expressed in raw counts rather than in engineering units. A field without
    a calibration records its raw value.
    """

    if calibration is None:
        return 1.0, 0.0
    return calibration.factor, calibration.offset / calibration.factor


def _field_binding(field, calibration) -> FieldBinding:
    """The MLVLG channel of one telemetry field.

    The name, digits, and category are the presentation of the field in the
    schema, the units are its display unit, and the scale and transform are
    the calibration the dashboard itself applies, so a recorded channel
    cannot drift away from the live value. An asterisk in the units marks a
    candidate conversion, exactly as the dashboard marks it.
    """

    dashboard = field.get("dashboard", {})
    scale, transform = mlg_scaling(calibration)
    return FieldBinding(
        spec=mlvlg.FieldSpec(
            name=dashboard.get("label", field["name"]),
            units=can_telemetry.display_unit(field),
            category=dashboard.get("group", "Telemetry"),
            field_type=mlvlg.MLG_F32,
            display_style=mlvlg.MLG_FLOAT,
            scale=scale,
            transform=transform,
            digits=dashboard.get("digits", 0),
        ),
        source=field["name"],
    )


def build_bindings(
    profile: str, schema_path: Path = DEFAULT_SCHEMA
) -> tuple[FieldBinding, ...]:
    _document, profiles = can_telemetry.load_schema(schema_path)
    try:
        selected = profiles[profile]
    except KeyError as error:
        raise ValueError(f"unknown telemetry profile: {profile}") from error

    calibrations = can_telemetry.calibrations(selected)

    bindings = [
        FieldBinding(
            mlvlg.FieldSpec(
                "Date",
                "sec",
                "Time",
                mlvlg.MLG_U32,
                mlvlg.MLG_DATE,
                digits=0,
            ),
            "date",
            "synthetic",
        ),
        FieldBinding(
            mlvlg.FieldSpec(
                "Elapsed", "s", "Time", mlvlg.MLG_F32, digits=4
            ),
            "elapsed",
            "synthetic",
        ),
        FieldBinding(
            mlvlg.FieldSpec(
                "Schema verified",
                "",
                "Transport",
                mlvlg.MLG_F32,
                mlvlg.MLG_ON_OFF,
                digits=0,
            ),
            "schema_verified",
            "attribute",
        ),
    ]
    bindings.extend(
        _field_binding(field, calibrations.get(field["name"]))
        for field in can_telemetry.profile_fields(selected)
    )
    bindings.extend(
        (
            FieldBinding(
                mlvlg.FieldSpec(
                    "High-detonation surface selected",
                    "",
                    "Knock",
                    mlvlg.MLG_F32,
                    mlvlg.MLG_ON_OFF,
                    digits=0,
                ),
                "high_detonation_selected",
                "attribute",
            ),
            FieldBinding(
                mlvlg.FieldSpec(
                    "Stock CAN RPM", "rpm", "Context", mlvlg.MLG_F32, digits=0
                ),
                "stock_rpm",
                "attribute",
            ),
            FieldBinding(
                mlvlg.FieldSpec(
                    "Vehicle speed",
                    "km/h",
                    "Context",
                    mlvlg.MLG_F32,
                    digits=2,
                ),
                "vehicle_speed_kmh",
                "attribute",
            ),
            FieldBinding(
                mlvlg.FieldSpec(
                    "Selector code", "raw", "Context", mlvlg.MLG_F32, digits=0
                ),
                "gear_raw",
                "attribute",
            ),
            FieldBinding(
                mlvlg.FieldSpec(
                    "Gear", "", "Context", mlvlg.MLG_F32, digits=0
                ),
                "tcm_gear",
                "attribute",
            ),
            FieldBinding(
                mlvlg.FieldSpec(
                    "ASCD input code", "raw", "Context", mlvlg.MLG_F32, digits=0
                ),
                "ascd_button_raw",
                "attribute",
            ),
            FieldBinding(
                mlvlg.FieldSpec(
                    "Dashboard state code",
                    "raw",
                    "Context",
                    mlvlg.MLG_F32,
                    digits=0,
                ),
                "dashboard_state_raw",
                "attribute",
            ),
        )
    )
    return tuple(bindings)


class TelemetryMlgRecorder:
    """Write atomic MLVLG files from complete dashboard snapshots."""

    def __init__(
        self,
        output: Path,
        profile: str,
        start_epoch: float,
        *,
        force: bool = False,
        schema_path: Path = DEFAULT_SCHEMA,
    ):
        if not math.isfinite(start_epoch) or start_epoch < 0:
            raise ValueError(f"invalid recording start time: {start_epoch!r}")
        self.output = Path(output)
        self.profile = profile
        self.start_epoch = float(start_epoch)
        self.force = force
        self.bindings = build_bindings(profile, schema_path)
        self.fields = tuple(binding.spec for binding in self.bindings)
        self.output_existed = self.output.exists()
        if self.output_existed and not force:
            raise FileExistsError(f"output already exists: {self.output}")
        self.output.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.output.name}.",
            suffix=".tmp",
            dir=self.output.parent,
        )
        self.temporary = Path(temporary_name)
        stream = os.fdopen(descriptor, "wb")
        try:
            writer = mlvlg.StreamWriter(
                stream,
                self.fields,
                math.floor(self.start_epoch),
            )
        except Exception:
            stream.close()
            self.temporary.unlink(missing_ok=True)
            raise
        self._stream = stream
        self._writer = writer
        self.event_records = 0
        self.bridge_records = 0
        self._last_elapsed: float | None = None
        self._last_values: tuple[int | float, ...] | None = None
        self._closed = False
        self.retained_path: Path | None = self.temporary
        self.close_error: OSError | None = None

    def _values(self, model, elapsed: float) -> tuple[int | float, ...]:
        values = []
        for binding in self.bindings:
            if binding.source_kind == "synthetic":
                if binding.source == "date":
                    value = math.floor(self.start_epoch + elapsed + 1e-9)
                elif binding.source == "elapsed":
                    value = elapsed
                else:
                    raise AssertionError(binding.source)
            elif binding.source_kind == "attribute":
                value = getattr(model, binding.source, None)
                if value is None:
                    value = math.nan
            else:
                value = model.raw.get(binding.source, math.nan)
            values.append(value)
        return tuple(values)

    def _bridge_values(self, elapsed: float) -> tuple[int | float, ...]:
        if self._last_values is None:
            raise AssertionError("bridge requested before the first event")
        values = list(self._last_values)
        values[0] = math.floor(self.start_epoch + elapsed + 1e-9)
        values[1] = elapsed
        return tuple(values)

    def append(self, model, elapsed: float) -> None:
        if self._closed:
            raise ValueError("recording is already closed")
        if not math.isfinite(elapsed) or elapsed < 0:
            raise ValueError(f"invalid recording elapsed time: {elapsed!r}")
        if self._last_elapsed is not None and elapsed < self._last_elapsed:
            raise ValueError(
                f"recording time decreased from {self._last_elapsed} to {elapsed}"
            )
        try:
            self._append(model, elapsed)
        except (OSError, ValueError):
            self.abort()
            raise

    def _append(self, model, elapsed: float) -> None:
        if self._last_elapsed is not None:
            bridge_elapsed = self._last_elapsed + MAX_GAP_SECONDS
            while bridge_elapsed < elapsed - 1e-12:
                self._writer.write(
                    self._bridge_values(bridge_elapsed), bridge_elapsed
                )
                self.bridge_records += 1
                bridge_elapsed += MAX_GAP_SECONDS

        values = self._values(model, elapsed)
        self._writer.write(values, elapsed)
        self.event_records += 1
        self._last_elapsed = elapsed
        self._last_values = values
        if self._writer.data_records % SYNC_RECORD_INTERVAL == 0:
            self._stream.flush()
            os.fsync(self._stream.fileno())

    def close(self) -> RecordingSummary:
        if self._closed:
            raise ValueError("recording is already closed")
        self._closed = True
        try:
            self._stream.flush()
            os.fsync(self._stream.fileno())
            self._stream.close()
        except OSError:
            self.abort()
            raise

        if self.event_records == 0:
            self.temporary.unlink(missing_ok=True)
            self.retained_path = None
            return RecordingSummary(
                output=self.output,
                output_existed=self.output_existed,
                fields=len(self.fields),
                event_records=0,
                bridge_records=0,
                record_length=self._writer.record_length,
                output_size=(
                    self.output.stat().st_size
                    if self.output.exists()
                    else 0
                ),
            )

        try:
            validation = mlvlg.validate_mlg(self.temporary)
            if validation.fields != len(self.fields):
                raise mlvlg.MlvlgError(
                    "validated MLVLG field count differs from the writer"
                )
            if validation.record_length != self._writer.record_length:
                raise mlvlg.MlvlgError(
                    "validated MLVLG record length differs from the writer"
                )
            if validation.data_records != self._writer.data_records:
                raise mlvlg.MlvlgError(
                    "validated MLVLG record count differs from the writer"
                )
            _publish_recording(self.temporary, self.output, force=self.force)
            self.retained_path = self.output.absolute()
        except Exception:
            self.abort()
            raise

        return RecordingSummary(
            output=self.output,
            output_existed=self.output_existed,
            fields=len(self.fields),
            event_records=self.event_records,
            bridge_records=self.bridge_records,
            record_length=self._writer.record_length,
            output_size=self.output.stat().st_size,
        )

    def abort(self) -> Path | None:
        """Stop writing and retain the file, including any incomplete tail."""
        self._closed = True
        try:
            self._stream.close()
        except OSError as error:
            self.close_error = error
        return self.retained_path
