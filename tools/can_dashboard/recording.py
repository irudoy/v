"""MLVLG recording for decoded VQ CAN telemetry snapshots."""

from __future__ import annotations

from dataclasses import dataclass
import math
import os
from pathlib import Path
import tempfile

from tools.logs import mlvlg
from tools.logs import can_telemetry
from tools.can_dashboard import model


DEFAULT_SCHEMA = can_telemetry.DEFAULT_SCHEMA
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


# Field identity for the MLVLG header. Scale and transform never appear here:
# they are derived from the calibrations the dashboard itself applies, so a
# recorded channel cannot drift away from the live value. An asterisk in the
# units marks a candidate transform, exactly as the dashboard marks it.
RAW_FIELD_DISPLAY = {
    "tick16": ("Telemetry tick", "", 0, "Transport"),
    "request_flow_raw": ("QH0 flow potential", "%*", 2, "Throttle"),
    "final_timing_raw": ("Timing command", "degBTDC", 0, "Ignition"),
    "apc_command_raw": ("APC command", "degBTDC", 0, "Ignition"),
    "fuel_inhibit_mask": ("Fuel inhibit mask", "", 0, "Injection"),
    "maf_b1_raw": ("MAF bank 1", "V", 3, "Air"),
    "maf_b2_raw": ("MAF bank 2", "V", 3, "Air"),
    "maf_total_raw": ("Total airflow", "g/s", 2, "Air"),
    "normalized_load_raw": ("Engine load", "%", 1, "Engine"),
    "bfs_raw": ("Base fuel schedule", "ms", 3, "Fuel"),
    "rolling_launch_phase": ("Rolling Launch phase", "", 0, "Context"),
    "telemetry_status": ("Telemetry status", "raw", 0, "Transport"),
    "knock_timing_state_raw": ("Knock timing state", "state", 3, "Knock"),
    "knock_surface_state": ("Knock surface state", "raw", 0, "Knock"),
    "knock_count_latched": ("Knock interval count", "", 0, "Knock"),
    "knock_channel_mask_latched": ("Knock channel mask", "", 0, "Knock"),
    **{
        f"knock_margin_min_ch{channel}_raw": (
            f"Knock margin ch {channel}", "cnt", 0, "Knock"
        )
        for channel in range(1, 7)
    },
    "app1_raw": ("APP 1", "V", 3, "Throttle"),
    "app2_raw": ("APP 2", "V", 3, "Throttle"),
    "tps_b1_raw": ("TPS bank 1", "V", 3, "Throttle"),
    "absolute_throttle_raw": ("Absolute throttle", "%", 1, "Throttle"),
    "tps_b2_raw": ("TPS bank 2", "V", 3, "Throttle"),
    "intake_cvtc_actual_b1_raw": (
        "Intake CVTC actual B1", "degCA", 1, "CVTC"
    ),
    "intake_cvtc_actual_b2_raw": (
        "Intake CVTC actual B2", "degCA", 1, "CVTC"
    ),
    "intake_cvtc_target_raw": ("Intake CVTC target", "degCA", 1, "CVTC"),
    "exhaust_cvtc_target_raw": ("Exhaust CVTC target", "degCA", 1, "CVTC"),
    "calculated_load_raw": ("Calculated load", "%", 1, "Engine"),
    "throttle_request_bounded_raw": (
        "Bounded throttle request", "Nm*", 1, "Throttle"
    ),
    "engine_torque_state_raw": ("Engine torque state", "Nm*", 1, "Engine"),
    "injection_end_angle_raw": (
        "End of injection after intake TDC", "degATDC", 0, "Injection"
    ),
    "exhaust_cvtc_actual_b1_raw": (
        "Exhaust CVTC actual B1", "degCA", 1, "CVTC"
    ),
    "exhaust_cvtc_actual_b2_raw": (
        "Exhaust CVTC actual B2", "degCA", 1, "CVTC"
    ),
    "throttle_target_shared_raw": (
        "Shared throttle target", "cm2*", 2, "Throttle"
    ),
    "throttle_target_channel_0_raw": (
        "Throttle target channel 0", "%", 2, "Throttle"
    ),
    "throttle_target_channel_1_raw": (
        "Throttle target channel 1", "%", 2, "Throttle"
    ),
    "coolant_raw": ("Coolant", "degC", 0, "Temperature"),
    "iat_raw": ("Intake air", "degC", 0, "Temperature"),
    "fuel_temperature_did_source_raw": (
        "Fuel temperature", "degC", 0, "Temperature"
    ),
    "oil_temperature_did_source_raw": (
        "Oil temperature", "degC", 0, "Temperature"
    ),
    "af_state_factor_raw": ("A/F state factor", "", 4, "Fuel"),
    "stft_b1_raw": ("STFT bank 1", "%", 2, "Fuel"),
    "stft_b2_raw": ("STFT bank 2", "%", 2, "Fuel"),
    "intake_cvtc_duty_b1_raw": ("CVTC duty B1", "%", 1, "CVTC"),
    "intake_cvtc_duty_b2_raw": ("CVTC duty B2", "%", 1, "CVTC"),
    "ltft_b1_raw": ("LTFT bank 1", "%", 2, "Fuel"),
    "ltft_b2_raw": ("LTFT bank 2", "%", 2, "Fuel"),
    "active_map_index": ("Selected map", "", 0, "Context"),
    "alpha_n_flow_raw": ("QH0 flow quantity", "%*", 2, "Fuel"),
    "protocol_version": ("Protocol version", "", 0, "Transport"),
    "profile_id": ("Profile ID", "", 0, "Transport"),
    "profile_crc16": ("Profile CRC16", "raw", 0, "Transport"),
    "snapshot_overrun_count": ("Snapshot overrun count", "", 0, "Transport"),
    "tx_abort_count": ("TX abort count", "", 0, "Transport"),
    "intake_cvtc_duty_command_b1_raw": (
        "Intake CVTC duty command B1", "%", 1, "CVTC"
    ),
    "intake_cvtc_duty_command_b2_raw": (
        "Intake CVTC duty command B2", "%", 1, "CVTC"
    ),
    "ltft_learned_b1_raw": ("LTFT learned bank 1", "%", 2, "Fuel"),
    "ltft_adjustment_b1_raw": ("LTFT adjustment bank 1", "%", 2, "Fuel"),
    "exhaust_cvtc_duty_b1_word_raw": (
        "Exhaust CVTC duty B1 word", "%", 1, "CVTC"
    ),
    "exhaust_cvtc_duty_b2_word_raw": (
        "Exhaust CVTC duty B2 word", "%", 1, "CVTC"
    ),
    "rolling_launch_abort_reason": (
        "Rolling Launch reason", "", 0, "Context"
    ),
    "battery_voltage_raw": ("Battery voltage", "V", 2, "Context"),
    "front_af_sensor_b1_word_raw": ("Front A/F sensor B1", "V", 3, "Fuel"),
    "front_af_sensor_b2_word_raw": ("Front A/F sensor B2", "V", 3, "Fuel"),
    "af_adjustment_b1_raw": ("A/F adjustment B1", "*", 3, "Fuel"),
    "af_adjustment_b2_raw": ("A/F adjustment B2", "*", 3, "Fuel"),
    "secondary_tps_b1_raw": ("Secondary TPS B1", "V", 3, "Throttle"),
    "secondary_tps_b2_raw": ("Secondary TPS B2", "V", 3, "Throttle"),
}

def current_channel_name(name: str) -> str:
    """Return the name of a recorded channel without candidate marks.

    A channel keeps its identity when its transform gains or loses the
    candidate marker.
    """

    return name.replace("*", "").strip()


MLG_CALIBRATIONS = {
    **can_telemetry.RAW_CALIBRATIONS,
    **model.DASHBOARD_CALIBRATIONS,
}


def mlg_scaling(source: str) -> tuple[float, float]:
    """Return the MLVLG scale and transform for one raw telemetry field.

    MegaLogViewer evaluates ``(raw + transform) * scale``, so the transform is
    expressed in raw counts rather than in engineering units.
    """

    calibration = MLG_CALIBRATIONS.get(source)
    if calibration is None:
        return 1.0, 0.0
    return calibration.factor, calibration.offset / calibration.factor



def _injection_display(index: int):
    return (f"Injection calc {index}", "ms", 2, "Injection")


def _raw_binding(name: str) -> FieldBinding:
    display = RAW_FIELD_DISPLAY.get(name)
    if display is None and name.startswith("injection_") and name.endswith("_raw"):
        display = _injection_display(int(name.split("_")[1]))
    if display is None:
        display = (name, "raw", 0, "Telemetry")
    field_name, units, digits, category = display
    scale, transform = mlg_scaling(name)
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
    _document, profiles = can_telemetry.load_schema(schema_path)
    try:
        selected = profiles[profile]
    except KeyError as error:
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
