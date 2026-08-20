"""MLVLG recording for decoded VQ CAN telemetry snapshots."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import tempfile

from tools.logs import mlvlg


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA = ROOT / "patches" / "can-telemetry-schema.json"
MAX_GAP_SECONDS = 0.3
SYNC_RECORD_INTERVAL = 100


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


RAW_FIELD_DISPLAY = {
    "tick16": ("Telemetry tick", "", 1.0, 0.0, 0, "Transport"),
    "rpm_raw": ("Engine speed", "rpm", 12.5, 0.0, 0, "Engine"),
    "final_timing_raw": (
        "Timing command*", "deg", 1.0, 0.0, 0, "Ignition"
    ),
    "apc_command_raw": ("APC command", "", 1.0, 0.0, 0, "Throttle"),
    "fuel_inhibit_mask": (
        "Fuel inhibit mask", "", 1.0, 0.0, 0, "Injection"
    ),
    "maf_b1_raw": ("MAF bank 1*", "V", 1 / 200, 0.0, 3, "Air"),
    "maf_b2_raw": ("MAF bank 2*", "V", 1 / 200, 0.0, 3, "Air"),
    "maf_total_raw": (
        "Total airflow*", "g/s", 1 / 100, 0.0, 2, "Air"
    ),
    "af_b1_raw": ("A/F bank 1", "raw", 1.0, 0.0, 0, "Fuel"),
    "bfs_raw": (
        "Base fuel schedule*", "ms", 1 / 2048, 0.0, 3, "Fuel"
    ),
    "af_b2_raw": ("A/F bank 2", "raw", 1.0, 0.0, 0, "Fuel"),
    "telemetry_status": (
        "Telemetry status", "raw", 1.0, 0.0, 0, "Transport"
    ),
    "knock_timing_state_raw": (
        "Knock timing state", "state", 1 / 256, 0.0, 3, "Knock"
    ),
    "knock_surface_state": (
        "Knock surface state", "raw", 1.0, 0.0, 0, "Knock"
    ),
    "knock_count_latched": (
        "Knock interval count", "", 1.0, 0.0, 0, "Knock"
    ),
    "knock_channel_mask_latched": (
        "Knock channel mask", "raw", 1.0, 0.0, 0, "Knock"
    ),
    "app1_raw": ("APP 1*", "V", 1 / 200, 0.0, 3, "Throttle"),
    "app2_raw": ("APP 2*", "V", 1 / 200, 0.0, 3, "Throttle"),
    "tps_b1_raw": ("TPS bank 1*", "V", 1 / 200, 0.0, 3, "Throttle"),
    "absolute_throttle_raw": (
        "Absolute throttle", "raw", 1.0, 0.0, 0, "Throttle"
    ),
    "tps_b2_raw": ("TPS bank 2*", "V", 1 / 200, 0.0, 3, "Throttle"),
    "intake_cvtc_actual_b1_raw": (
        "Intake CVTC actual B1*", "degCA", 0.5, -64.0, 1, "CVTC"
    ),
    "intake_cvtc_actual_b2_raw": (
        "Intake CVTC actual B2*", "degCA", 0.5, -64.0, 1, "CVTC"
    ),
    "intake_cvtc_target_b1_raw": (
        "Intake CVTC target*", "degCA", 0.5, -64.0, 1, "CVTC"
    ),
    "intake_cvtc_target_b2_raw": (
        "Exhaust CVTC target*", "degCA", 0.5, -64.0, 1, "CVTC"
    ),
    "calculated_load_raw": (
        "Calculated load", "%", 100 / 255, 0.0, 1, "Engine"
    ),
    "coolant_raw": ("Coolant", "degC", 1.0, -50.0, 0, "Temperature"),
    "iat_raw": ("Intake air", "degC", 1.0, -50.0, 0, "Temperature"),
    "fuel_temperature_did_source_raw": (
        "Fuel temperature*", "degC", 1.0, -50.0, 0, "Temperature"
    ),
    "oil_temperature_did_source_raw": (
        "Oil temperature*", "degC", 1.0, -50.0, 0, "Temperature"
    ),
    "af_state_factor_raw": (
        "A/F state factor", "", 1 / 16384, 0.0, 4, "Fuel"
    ),
    "stft_b1_raw": (
        "STFT bank 1", "%", 1 / 256, -25600.0, 2, "Fuel"
    ),
    "stft_b2_raw": (
        "STFT bank 2", "%", 1 / 256, -25600.0, 2, "Fuel"
    ),
    "intake_cvtc_duty_b1_raw": (
        "CVTC duty B1", "%", 100 / 256, 0.0, 1, "CVTC"
    ),
    "intake_cvtc_duty_b2_raw": (
        "CVTC duty B2", "%", 100 / 256, 0.0, 1, "CVTC"
    ),
    "ltft_b1_raw": (
        "LTFT bank 1", "%", 1 / 256, -25600.0, 2, "Fuel"
    ),
    "ltft_b2_raw": (
        "LTFT bank 2", "%", 1 / 256, -25600.0, 2, "Fuel"
    ),
    "timing_state_2023_raw": (
        "Timing state 2023", "raw", 1.0, 0.0, 0, "Ignition"
    ),
    "timing_state_564c_raw": (
        "Timing state 564C", "raw", 1.0, 0.0, 0, "Ignition"
    ),
    "protocol_version": (
        "Protocol version", "", 1.0, 0.0, 0, "Transport"
    ),
    "profile_id": ("Profile ID", "", 1.0, 0.0, 0, "Transport"),
    "profile_crc16": (
        "Profile CRC16", "raw", 1.0, 0.0, 0, "Transport"
    ),
    "snapshot_overrun_count": (
        "Snapshot overrun count", "", 1.0, 0.0, 0, "Transport"
    ),
    "tx_abort_count": (
        "TX abort count", "", 1.0, 0.0, 0, "Transport"
    ),
}


def _injection_display(index: int):
    return (
        f"Injection calc {index}*",
        "ms",
        1 / 100,
        0.0,
        2,
        "Injection",
    )


def _raw_binding(name: str) -> FieldBinding:
    display = RAW_FIELD_DISPLAY.get(name)
    if display is None and name.startswith("injection_") and name.endswith("_raw"):
        display = _injection_display(int(name.split("_")[1]))
    if display is None:
        display = (name, "raw", 1.0, 0.0, 0, "Telemetry")
    field_name, units, scale, transform, digits, category = display
    return FieldBinding(
        spec=mlvlg.FieldSpec(
            name=field_name,
            units=units,
            category=category,
            field_type=mlvlg.MLG_F32,
            display_style=mlvlg.MLG_FLOAT,
            scale=scale,
            transform=transform,
            digits=digits,
        ),
        source=name,
    )


def build_bindings(
    profile: str, schema_path: Path = DEFAULT_SCHEMA
) -> tuple[FieldBinding, ...]:
    document = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    try:
        selected = next(
            item for item in document["profiles"] if item["name"] == profile
        )
    except StopIteration as error:
        raise ValueError(f"unknown telemetry profile: {profile}") from error

    names = [field["name"] for field in selected["fields"]]
    for context in selected.get("contexts", ()):
        names.extend(field["name"] for field in context["fields"])

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
    bindings.extend(_raw_binding(name) for name in names)
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
                    "Vehicle speed*",
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
            FieldBinding(
                mlvlg.FieldSpec(
                    "gps_lat", "deg", "GPS", mlvlg.MLG_F32, digits=6
                ),
                "gps_lat",
                "attribute",
            ),
            FieldBinding(
                mlvlg.FieldSpec(
                    "gps_lon", "deg", "GPS", mlvlg.MLG_F32, digits=6
                ),
                "gps_lon",
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
        finally:
            self._stream.close()

        if self.event_records == 0:
            self.temporary.unlink(missing_ok=True)
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
            if self.output.exists() and not self.force:
                raise FileExistsError(
                    f"output appeared during recording: {self.output}"
                )
            os.replace(self.temporary, self.output)
        except Exception:
            self.temporary.unlink(missing_ok=True)
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

    def abort(self) -> None:
        if not self._closed:
            self._closed = True
            self._stream.close()
        self.temporary.unlink(missing_ok=True)
