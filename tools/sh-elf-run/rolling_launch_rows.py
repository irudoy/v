#!/usr/bin/env python3
"""Generate the GNU gate rows of exact JK08A Rolling Launch from the model.

Every row holds a complete base record and extension, the inputs of one call,
and the complete records that the schema 6 model in patches/rolling_launch.py
expects after it. The harness writes the configuration and the efficiency
table of the row into the simulator ROM image, runs the composed entry, and
compares every byte. The rows cover the gate boundaries, the activation
threshold and its latch, the four invalid-speed reasons, release, rearm,
recovery from each failing check, the startup record, and the stock and ready
outcomes of the ignition publisher.

The ignition publisher also rejects an adapter command outside its contract:
a trim outside 0..40 or above the trim of the run while ready. The model
never produces such a command, so those rows expect the stock branch of
ignition_step.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import rolling_launch as model  # noqa: E402


SLOTS = (
    model.Slot(integral_gain=4, max_trim_rpm=20, max_trim_speed=10, floor_command=60,
               launch_rpm_native=400, launch_speed_threshold=100,
               launch_soft_width_native=40),
    model.Slot(),
    model.Slot(integral_gain=0, max_trim_rpm=40, max_trim_speed=40, floor_command=120,
               launch_rpm_native=300, launch_speed_threshold=1,
               launch_soft_width_native=0),
    model.Slot(integral_gain=32767, launch_rpm_native=32767,
               launch_speed_threshold=65535, launch_soft_width_native=32606),
    model.Slot(),
)
# Maps 0, 2 and 3 are enabled. Map 0 holds RPM below 10.0 km/h with a 40-step
# soft width, map 2 has a zero soft width and a threshold of 0.1 km/h, and
# map 3 carries the largest valid slot values.
CALIBRATION = model.Calibration(
    mode=model.Mode.HOLD, enable_mask=0x0D, coolant_min=40, coolant_max=120,
    min_speed=50, max_speed=1500, min_rpm_native=160, min_pedal=100,
    target_speed_offset=-20, window_width=40, window_top=20, u_rate_limit=50,
    integrator_limit=100, abort_above=150, abort_below=100, run_timeout_ticks=50,
    rearm_ticks=3, speed_frame_age_limit=10, slots=SLOTS,
)
OBSERVE = replace(CALIBRATION, mode=model.Mode.OBSERVE)
TABLE = model.EfficiencyTable((1000,) + tuple(1000 - 12 * trim for trim in range(1, 41)))
SPARK = model.SparkCutState(
    quiet_events=7, cut_count=3, accumulators=(111, 2222, 3333, 4444, 5555, 666),
    consumed_q_sum=0x12345678, eligible_event_counter=0x4321,
)
GOOD = model.Inputs(
    active_index=0, button=model.BUTTON_CANCEL, speed=300, speed_frame_age=0,
    hcan1_state=0x01, port_input_state=0x80, speed_wire_word=0x1234,
    rpm_native=300, pedal=500, coolant=80,
)
# A state that the model rejects selects its corrupt-state and stock branches.
REJECTED_PHASE = 3
PUBLICATION = struct.Struct(">BBBBHH")
# Bits 8..31 of the wide S of the publisher rows; P carries their complement.
HIGH = 0x5AA5C3
VARIANTS = (None, "periodic", "controller", "engine")
# The source branches whose outcome the controller and engine variants omit:
# the lower integrator clamp and the COOLDOWN pass without a valid
# configuration and table.
CONTROLLER_NEGATIVE_EDGE = "bt rl_spd_integrator_lower"
ENGINE_NEGATIVE_EDGE = "bt rl_cooldown_valid"
# The harness runs these dashboard feedback cases of its own.
FEEDBACK_CASES = 8
CONFIG_HEAD = 0x28


def _set(data, offset, fmt, value):
    data = bytearray(data)
    struct.pack_into(">" + fmt, data, offset, value)
    return bytes(data)


def _get(data, offset, fmt):
    return struct.unpack_from(">" + fmt, data, offset)[0]


def _calibration(config):
    return model.Calibration.from_bytes(config)


def _table(table):
    return model.EfficiencyTable(struct.unpack(">41H", table))


def _decode(base, extension):
    try:
        return model.decode_state(base, extension)
    except ValueError:
        return None


def _raw_state(base, extension):
    values = {}
    for fields, buffer in ((model.BASE_STATE_FIELDS, base),
                           (model.EXTENSION_FIELDS, extension)):
        values.update({name: _get(buffer, offset, fmt) for name, offset, fmt in fields})
    if values["actuation_ready"] in (0, 1):
        values["actuation_ready"] = bool(values["actuation_ready"])
    return model.RuntimeState(**values)


def _kept_spark(base):
    """Base counters and accumulators that recovery keeps, with reset events."""
    return model.SparkCutState(
        quiet_events=_get(base, 0x1C, "B"), cut_count=_get(base, 0x1D, "B"),
        accumulators=tuple(_get(base, offset, fmt)
                           for _name, offset, fmt in model.BASE_ACCUMULATOR_FIELDS),
    )


def _publish(base, extension, state):
    """Apply the fields that a publication stores to the input records."""
    base, extension = bytearray(base), bytearray(extension)
    PUBLICATION.pack_into(
        extension, 0x08, state.stock_command, state.effective_command,
        state.applied_trim, int(state.actuation_ready), state.applied_efficiency,
        state.wire_efficiency)
    struct.pack_into(">BB", extension, 0x1E, state.wire_mode_trim, state.wire_status)
    struct.pack_into(">H", base, 0x1A, state.cut_fraction)
    return bytes(base), bytes(extension)


@dataclass(frozen=True)
class Publication:
    """The records and r5 after one ignition publication."""
    base: bytes
    extension: bytes
    r5: int
    stock_wide: int
    effective_wide: int
    state: model.RuntimeState


def ignition_publication(records, stock, effective, *, apc=0x00, contract=True, high=HIGH,
                         name="publication"):
    """Return the publication of the publisher for S, P and one record pair.

    A record that the model rejects, a record without CONFIG_VALID and a P
    other than the model command publish the stock command.
    """
    base, extension = records
    fallback = bool(apc & 0x40)
    decoded = _decode(base, extension)
    if decoded is None:
        state = replace(_raw_state(base, extension), phase=REJECTED_PHASE)
    else:
        state = decoded[0]
    stock_wide = (high << 8) | stock
    result = model.ignition_step(state, stock, CALIBRATION, TABLE, apc_fallback=fallback)
    publish = decoded is not None and bool(state.flags & model.Flag.CONFIG_VALID)
    if effective is None:
        effective = result.effective_command
    if publish and effective != result.effective_command:
        if contract:
            raise ValueError(f"{name}: P differs from the model command")
        publish = False
    if not publish:
        stock_state = replace(state, flags=state.flags & ~model.Flag.CONFIG_VALID)
        result = model.ignition_step(stock_state, stock, CALIBRATION, TABLE,
                                     apc_fallback=fallback)
    effective_wide = ((high ^ 0xFFFFFF) << 8) | effective
    base_out, extension_out = _publish(base, extension, result)
    if decoded is not None and publish:
        expected = model.encode_state(result, decoded[1])
        if expected != (base_out, extension_out):
            raise ValueError(f"{name}: publication fields differ from the model record")
    r5 = effective_wide if publish and result.actuation_ready else stock_wide
    return Publication(base_out, extension_out, r5, stock_wide, effective_wide, result)


def engine_pass(records, inputs, config=None, table=None):
    """Return the records, the map 1 restore and the state after one engine pass."""
    config = CALIBRATION.to_bytes() if config is None else config
    table = TABLE.to_bytes() if table is None else table
    base, extension = records
    decoded = _decode(base, extension)
    if decoded is None:
        state = replace(model.RuntimeState(), phase=REJECTED_PHASE)
        spark = _kept_spark(base)
    else:
        state, spark = decoded
    result = model.engine_step(state, inputs, _calibration(config), _table(table))
    if result.reset_event_instrumentation != (decoded is None):
        raise ValueError("unexpected event-counter reset")
    restore = result.limiter_action == model.LimiterAction.RESTORE_MAP_1
    if restore and result.limiter_index != 0:
        raise ValueError("recovery restores a map other than map 1")
    base_out, extension_out = model.encode_state(result.state, spark)
    return base_out, extension_out, restore, result.state


@dataclass(frozen=True)
class EngineRow:
    name: str
    config: int
    inputs: model.Inputs
    base: bytes
    extension: bytes
    base_out: bytes
    extension_out: bytes
    restore: bool
    periodic: bool = False


@dataclass(frozen=True)
class PublisherRow:
    name: str
    config: int
    apc: int
    r3: int
    r4: int
    r5: int
    base: bytes
    extension: bytes
    base_out: bytes
    extension_out: bytes
    r5_out: int


@dataclass(frozen=True)
class FractionRow:
    name: str
    error: int
    width: int
    fraction: int


class Rows:
    """Collect the configurations and rows of one gate run."""

    def __init__(self):
        self.configs = []
        self.engine = []
        self.ignition = []
        self.control = []
        self.fraction = []
        self._names = set()
        self.startup = model.encode_state(model.RuntimeState(), model.SparkCutState())

    def _name(self, name):
        if name in self._names:
            raise ValueError(f"duplicate gate row {name}")
        self._names.add(name)
        return name

    def config(self, config, table):
        key = (bytes(config), bytes(table))
        if key not in self.configs:
            self.configs.append(key)
        return self.configs.index(key)

    def engine_row(self, name, records, inputs, *, config=None, table=None,
                   periodic=False, corrupt=False):
        config = CALIBRATION.to_bytes() if config is None else config
        table = TABLE.to_bytes() if table is None else table
        base, extension = records
        if corrupt != (_decode(base, extension) is None):
            raise ValueError(f"{name}: the model {'rejects' if not corrupt else 'accepts'} "
                             "the record")
        base_out, extension_out, restore, state = engine_pass(records, inputs, config, table)
        self.engine.append(EngineRow(
            self._name(name), self.config(config, table), inputs, base, extension,
            base_out, extension_out, restore, periodic))
        return state

    def ignition_row(self, name, records, stock, effective, *, apc=0x00,
                     contract=True, high=HIGH):
        """Run the publisher with wide commands; contract rows take P from the model.

        Bits 8..31 of S hold ``high`` and those of P hold its complement. The
        APC byte selects the fallback through bit 6 alone. The publisher
        returns P only with the ready mark of the model and S otherwise; a
        row whose P differs from the model command expects the stock
        publication.
        """
        base, extension = records
        result = ignition_publication(records, stock, effective, apc=apc, contract=contract,
                                      high=high, name=name)
        self.ignition.append(PublisherRow(
            self._name(name), self.config(CALIBRATION.to_bytes(), TABLE.to_bytes()),
            apc, 0, result.stock_wide, result.effective_wide, base, extension,
            result.base, result.extension, result.r5))
        return result.state

    def control_row(self, name, state, law):
        """Run the control publisher with the law output of a controller in r3."""
        base, extension = model.encode_state(state, SPARK)
        torque = law if state.regulator_kind == model.RegulatorKind.SPEED else state.torque_fraction
        result = model._publish_actuation(
            replace(state, law_output=law, torque_fraction=torque), TABLE)
        base_out, extension_out = model.encode_state(result, SPARK)
        self.control.append(PublisherRow(
            self._name(name), self.config(CALIBRATION.to_bytes(), TABLE.to_bytes()), 0,
            law, 0x000D6320, 0, base, extension, base_out, extension_out, 0))

    def fraction_row(self, name, error, width):
        self.fraction.append(FractionRow(
            self._name(name), error, width, model.rpm_fraction(error, width)))


def records(state, spark=SPARK):
    return model.encode_state(state, spark)


def mutate(state, region, offset, fmt, value, spark=SPARK):
    base, extension = records(state, spark)
    if region == "base":
        return _set(base, offset, fmt, value), extension
    return base, _set(extension, offset, fmt, value)


def step(state, inputs, calibration=CALIBRATION, table=TABLE):
    return model.engine_step(state, inputs, calibration, table).state


def _config(**changes):
    return replace(CALIBRATION, **changes).to_bytes()


def build(variant=None):
    """Return the rows of the positive run, or of one negative variant.

    Each variant removes one covered path and keeps every row a model row:
    "periodic" runs the engine row of the periodic wrapper directly,
    "controller" keeps the integrator above its lower bound, and "engine"
    drops the COOLDOWN rows with an invalid configuration or table.
    """
    if variant not in VARIANTS:
        raise ValueError(f"unknown gate row variant {variant!r}")
    rows = Rows()
    idle = model.RuntimeState()
    good = GOOD

    # Configuration head, slots and efficiency table: each check fails alone.
    config = CALIBRATION.to_bytes()
    table = TABLE.to_bytes()
    head = (
        ("magic", 0x00, "H", 0x524D), ("schema", 0x02, "B", 5), ("mode", 0x03, "B", 2),
        ("mask", 0x04, "B", 0x20), ("options", 0x05, "B", 1),
        ("coolant-order", 0x06, "B", 121), ("speed-order", 0x08, "H", 1501),
        ("rpm-zero", 0x0C, "H", 0), ("rpm-span", 0x0C, "H", 32767),
        ("offset-above", 0x10, "h", -150), ("offset-below", 0x10, "h", 100),
        ("above-zero", 0x1A, "B", 0), ("below-zero", 0x1B, "B", 0),
        ("window-zero", 0x12, "B", 0), ("rate-zero", 0x14, "H", 0),
        ("rate-high", 0x14, "H", 1001), ("reserved-16", 0x16, "H", 1),
        ("limit-high", 0x18, "H", 1001), ("reserved-1c", 0x1C, "B", 1),
        ("reserved-1d", 0x1D, "B", 1), ("timeout-zero", 0x1E, "H", 0),
        ("timeout-sign", 0x1E, "H", 0x8000), ("rearm-zero", 0x20, "H", 0),
        ("rearm-sign", 0x20, "H", 0x8000), ("age-zero", 0x22, "B", 0),
        ("age-ff", 0x22, "B", 0xFF), ("reserved-23", 0x23, "B", 1),
        ("inverse", 0x24, "H", 0xADB4), ("head-marker", 0x26, "H", 0xA55B),
        ("end-marker", 0x64, "H", 0xA55B),
        ("slot-gain", CONFIG_HEAD + 0x0, "h", -1),
        ("slot-trim-rpm", CONFIG_HEAD + 0x2, "B", 41),
        ("slot-trim-speed", CONFIG_HEAD + 0x3, "B", 41),
        ("slot-floor", CONFIG_HEAD + 0x4, "B", 121),
        ("slot-reserved", CONFIG_HEAD + 0x5, "B", 1),
        ("slot-launch-sign", CONFIG_HEAD + 0x6, "H", 0x8000),
        ("slot-launch-min", CONFIG_HEAD + 0x6, "H", 160),
        ("slot-threshold", CONFIG_HEAD + 0x8, "H", 0),
        ("slot-width", CONFIG_HEAD + 0xA, "H", 240),
        ("slot4-floor", CONFIG_HEAD + 4 * 12 + 0x4, "B", 121),
    )
    for name, offset, fmt, value in head:
        changed = _set(config, offset, fmt, value)
        if _calibration(changed).is_valid():
            raise ValueError(f"cfg-{name} stays valid")
        rows.engine_row(f"cfg-{name}", records(idle), good, config=changed)
    for name, index, value in (("e0", 0, 999), ("zero", 5, 0), ("high", 40, 1001)):
        changed = _set(table, 2 * index, "H", value)
        rows.engine_row(f"table-{name}", records(idle), good, table=changed)
    for name, changes in (
        ("cfg-valid-order", dict(min_speed=300, max_speed=300)),
        ("cfg-valid-offset-above", dict(target_speed_offset=-149)),
        ("cfg-valid-offset-below", dict(target_speed_offset=99)),
        ("cfg-valid-rate", dict(u_rate_limit=1000)),
        ("cfg-valid-limit", dict(integrator_limit=1000)),
        ("cfg-valid-age", dict(speed_frame_age_limit=254)),
        ("cfg-valid-width", dict(slots=(replace(SLOTS[0], launch_soft_width_native=239),
                                        *SLOTS[1:]))),
    ):
        rows.engine_row(name, records(idle), good, config=_config(**changes))

    # IDLE gates in priority order, each failing alone, and their boundaries.
    for name, inputs in (
        ("gate-pass", good),
        ("gate-map-5", replace(good, active_index=5)),
        ("gate-map-255", replace(good, active_index=255)),
        ("gate-map-1-disabled", replace(good, active_index=1)),
        ("gate-map-4-disabled", replace(good, active_index=4)),
        ("gate-map-3", replace(good, active_index=3)),
        ("gate-selector-phase", replace(good, selector_phase=1)),
        ("gate-selector-count", replace(good, selection_count=1)),
        ("gate-selector-elapsed", replace(good, selector_elapsed=1)),
        ("gate-feedback-pulses", replace(good, feedback_pulses=1)),
        ("gate-feedback-phase", replace(good, feedback_phase=1)),
        ("gate-feedback-ticks", replace(good, feedback_ticks=1)),
        ("gate-feedback-reserved", replace(good, feedback_reserved=1)),
        ("gate-main", replace(good, ascd_status=0x80)),
        ("gate-main-foreign", replace(good, ascd_status=0x7F)),
        ("gate-button-released", replace(good, button=model.BUTTON_RELEASED)),
        ("gate-button-zero", replace(good, button=0)),
        ("gate-button-set", replace(good, button=model.BUTTON_SET)),
        ("gate-source-hcan", replace(good, hcan1_state=0xFE)),
        ("gate-source-port", replace(good, port_input_state=0x7F)),
        ("gate-value-ffff", replace(good, speed_wire_word=0xFFFF)),
        ("gate-value-ff00", replace(good, speed_wire_word=0xFF00)),
        ("gate-value-00ff", replace(good, speed_wire_word=0x00FF)),
        ("gate-stale-11", replace(good, speed_frame_age=11)),
        ("gate-stale-10", replace(good, speed_frame_age=10)),
        ("gate-stale-255", replace(good, speed_frame_age=255)),
        ("gate-speed-low", replace(good, active_index=2, speed=49)),
        ("gate-speed-min", replace(good, active_index=2, speed=50)),
        ("gate-speed-high", replace(good, speed=1501)),
        ("gate-speed-max", replace(good, speed=1500)),
        ("gate-rpm-invalid", replace(good, rpm_native=0x8000)),
        ("gate-rpm-low", replace(good, rpm_native=159)),
        ("gate-rpm-min", replace(good, rpm_native=160)),
        ("gate-pedal-low", replace(good, pedal=99)),
        ("gate-pedal-min", replace(good, pedal=100)),
        ("gate-coolant-low", replace(good, coolant=39)),
        ("gate-coolant-min", replace(good, coolant=40)),
        ("gate-coolant-max", replace(good, coolant=120)),
        ("gate-coolant-high", replace(good, coolant=121)),
        ("gate-priority", replace(good, active_index=1, selector_phase=1, ascd_status=0x80,
                                  pedal=0)),
        ("threshold-below", replace(good, speed=99)),
        ("threshold-at", replace(good, speed=100)),
        ("threshold-w0", replace(good, active_index=2, speed=0)),
    ):
        rows.engine_row(name, records(idle), inputs)
    rows.engine_row("gate-speed-min-off", records(idle), replace(good, active_index=2, speed=1),
                    config=_config(min_speed=0))
    rows.engine_row("gate-speed-max-off", records(idle), replace(good, speed=65535),
                    config=_config(max_speed=0))
    rows.engine_row("gate-target-ceiling", records(idle),
                    replace(good, active_index=2, speed=65530),
                    config=_config(max_speed=0, target_speed_offset=99))

    # A CANCEL edge captures a usable speed once. A failed edge keeps its
    # capture, and an edge without a usable speed leaves the capture invalid.
    held = step(idle, replace(good, pedal=0))
    lost = step(idle, replace(good, hcan1_state=0))
    rows.engine_row("capture-invalid", records(lost), good)
    rows.engine_row("capture-kept", records(held), replace(good, speed=310))
    for name, speed in (("window-above", 431), ("window-above-edge", 430),
                        ("window-below", 179), ("window-below-edge", 180)):
        rows.engine_row(name, records(held), replace(good, speed=speed))

    # ACTIVE SPEED and RPM holds.
    speed_hold = step(idle, good)
    rpm_hold = step(idle, replace(good, speed=80))
    zero_width = step(idle, replace(good, active_index=2, speed=0))
    low_hold = step(idle, replace(good, speed=110))
    observe_speed = step(idle, good, OBSERVE)
    observe_rpm = step(idle, replace(good, speed=80), OBSERVE)
    zero_gain = step(idle, replace(good, active_index=2, speed=300))
    for state, kind in ((speed_hold, model.RegulatorKind.SPEED),
                        (rpm_hold, model.RegulatorKind.RPM),
                        (zero_width, model.RegulatorKind.RPM),
                        (zero_gain, model.RegulatorKind.SPEED)):
        if state.phase != model.Phase.ACTIVE or state.regulator_kind != kind:
            raise ValueError("an activation row does not reach its hold")
    for name, inputs in (
        ("speed-continue", replace(good, speed=290)),
        ("speed-above", replace(good, speed=431)),
        ("speed-above-edge", replace(good, speed=430)),
        ("speed-below", replace(good, speed=179)),
        ("speed-below-edge", replace(good, speed=180)),
        ("speed-map-change", replace(good, active_index=2)),
        ("speed-map-invalid", replace(good, active_index=5)),
        ("speed-release", replace(good, button=model.BUTTON_RELEASED)),
        ("speed-set", replace(good, button=model.BUTTON_SET)),
        ("speed-zero", replace(good, button=0)),
        ("speed-main", replace(good, ascd_status=0x80)),
        ("speed-source", replace(good, hcan1_state=0)),
        ("speed-port", replace(good, port_input_state=0)),
        ("speed-value", replace(good, speed_wire_word=0xFFFF)),
        ("speed-stale", replace(good, speed_frame_age=11)),
        ("speed-pedal", replace(good, pedal=0)),
        ("speed-rpm", replace(good, rpm_native=100)),
        ("speed-coolant", replace(good, coolant=200)),
    ):
        rows.engine_row(name, records(speed_hold), inputs)
    rows.engine_row("speed-mode-change", records(speed_hold), good,
                    config=OBSERVE.to_bytes())
    rows.engine_row("speed-config", records(speed_hold), good,
                    config=_set(config, 0, "H", 0))
    rows.engine_row("speed-table", records(speed_hold), good,
                    table=_set(table, 0, "H", 999))
    rows.engine_row("speed-capture", records(replace(speed_hold, input_status=0x0F)), good)
    rows.engine_row("speed-timeout", records(replace(speed_hold, run_ticks=49)), good)
    rows.engine_row("speed-timeout-edge", records(replace(speed_hold, run_ticks=48)), good)
    rows.engine_row("speed-latch", records(low_hold), replace(good, speed=95))
    rows.engine_row("speed-observe", records(observe_speed), replace(good, speed=290),
                    config=OBSERVE.to_bytes())
    rows.engine_row("speed-periodic", records(speed_hold), replace(good, speed=285),
                    periodic=variant != "periodic")
    for name, rpm in (("rpm-below-band", 360), ("rpm-band-low", 361),
                      ("rpm-band-high", 399), ("rpm-target", 400), ("rpm-above", 401),
                      ("rpm-high", 1000)):
        rows.engine_row(name, records(rpm_hold), replace(good, speed=80, rpm_native=rpm))
    rows.engine_row("rpm-latch", records(rpm_hold), replace(good, speed=150, rpm_native=380))
    rows.engine_row("rpm-source", records(rpm_hold),
                    replace(good, speed=80, rpm_native=380, hcan1_state=0))
    rows.engine_row("rpm-observe", records(observe_rpm), replace(good, speed=80, rpm_native=380),
                    config=OBSERVE.to_bytes())
    for name, rpm in (("w0-below", 299), ("w0-target", 300)):
        rows.engine_row(name, records(zero_width),
                        replace(good, active_index=2, speed=0, rpm_native=rpm))

    # Speed controller branches at the map 0 gain of 4 and the integrator
    # limit of 1600 sixteenths; the zero gain of map 2 reaches the remaining
    # accumulate outcomes.
    for name, error, integrator, fraction in (
        ("ctrl-freeze-low", 30, 0, 500), ("ctrl-accumulate-down", 30, 1600, 500),
        ("ctrl-freeze-high", -30, 0, 400), ("ctrl-accumulate-up", -30, -1600, 900),
        ("ctrl-command-low", 30, -16, 40), ("ctrl-integrator-upper", -1, 1598, 600),
        ("ctrl-integrator-lower", 10, -1550 if variant == "controller" else -1590, 150),
        ("ctrl-command-high", -30, 1600, 1000),
        ("ctrl-proportional", 0, 0, 500), ("ctrl-window-top", 20, 0, 500),
        ("ctrl-window-bottom", -20, 0, 500), ("ctrl-window-19", 19, 0, 500),
        ("ctrl-window-minus-19", -19, 0, 500),
    ):
        state = replace(speed_hold, integrator=integrator, torque_fraction=fraction,
                        law_output=fraction)
        rows.engine_row(name, records(state), replace(good, speed=280 + error))
    for name, error, integrator in (("ctrl-zero-gain-high", -20, 0),
                                    ("ctrl-zero-gain-low", 30, -160)):
        state = replace(zero_gain, integrator=integrator)
        rows.engine_row(name, records(state), replace(good, active_index=2, speed=280 + error))

    # Ready holds: the control publisher keeps ready and recomputes q.
    ready_speed = model.ignition_step(speed_hold, 20, CALIBRATION, TABLE)
    ready_rpm = model.ignition_step(rpm_hold, 20, CALIBRATION, TABLE)
    ready_cut = model._publish_actuation(
        replace(ready_speed, torque_fraction=500, law_output=500), TABLE)
    for state in (ready_speed, ready_rpm, ready_cut):
        if not state.actuation_ready:
            raise ValueError("a ready row is not ready")
    rows.engine_row("ready-speed", records(ready_speed), replace(good, speed=290))
    rows.engine_row("ready-speed-cut", records(ready_cut), replace(good, speed=275))
    rows.engine_row("ready-rpm", records(ready_rpm), replace(good, speed=80, rpm_native=380))
    rows.engine_row("ready-abort", records(ready_cut), replace(good, button=model.BUTTON_RELEASED))

    # COOLDOWN rearms after three released passes with a valid configuration.
    cooldown = step(speed_hold, replace(good, button=model.BUTTON_RELEASED))
    released = replace(good, button=model.BUTTON_RELEASED)
    rows.engine_row("cool-rearm", records(cooldown), released)
    rows.engine_row("cool-rearm-done", records(replace(cooldown, rearm_ticks=2)), released)
    rows.engine_row("cool-rearm-max", records(replace(cooldown, rearm_ticks=32767)), released)
    rows.engine_row("cool-held", records(replace(cooldown, rearm_ticks=2)), good)
    if variant != "engine":
        rows.engine_row("cool-config", records(cooldown), released,
                        config=_set(config, 0, "H", 0))
        rows.engine_row("cool-table", records(cooldown), released,
                        table=_set(table, 80, "H", 0))

    # Recovery from every failing check of the record.
    ready_observe = replace(observe_speed, actuation_ready=True)
    for name, state, region, offset, fmt, value in (
        ("phase", idle, "base", 0x00, "B", 3),
        ("reason", idle, "base", 0x01, "B", 26),
        ("map", speed_hold, "base", 0x04, "B", 5),
        ("mode", speed_hold, "base", 0x05, "B", 2),
        ("latched", speed_hold, "base", 0x1E, "B", 41),
        ("reserved", idle, "base", 0x1F, "B", 1),
        ("reserved-active", ready_speed, "base", 0x1F, "B", 0x80),
        ("kind", speed_hold, "extension", 0x00, "B", 3),
        ("status", idle, "extension", 0x01, "B", 32),
        ("trim", idle, "extension", 0x0A, "B", 41),
        ("ready", idle, "extension", 0x0B, "B", 2),
        ("flag-13", idle, "base", 0x02, "H", 0x2000),
        ("flag-15", idle, "base", 0x02, "H", 0x8000),
        ("torque", speed_hold, "base", 0x0E, "H", 1001),
        ("command", speed_hold, "base", 0x16, "H", 1001),
        ("q", idle, "base", 0x1A, "H", 1001),
        ("law", speed_hold, "extension", 0x16, "H", 1001),
        ("efficiency-zero", idle, "extension", 0x0C, "H", 0),
        ("efficiency-high", idle, "extension", 0x0C, "H", 1001),
        ("effective", idle, "extension", 0x09, "B", 1),
        ("idle-q", idle, "base", 0x1A, "H", 5),
        ("ready-cooldown", cooldown, "extension", 0x0B, "B", 1),
        ("ready-trim", ready_speed, "base", 0x1E, "B", ready_speed.applied_trim - 1),
        ("ready-q", ready_cut, "base", 0x1A, "H", ready_cut.cut_fraction + 1),
        ("ready-q-rpm", ready_rpm, "base", 0x1A, "H", ready_rpm.cut_fraction + 1),
        ("idle-mode", idle, "base", 0x05, "B", 1),
        ("idle-kind", idle, "extension", 0x00, "B", 1),
        ("idle-run", idle, "base", 0x06, "H", 1),
        ("idle-rearm", idle, "base", 0x08, "H", 1),
        ("idle-latched", idle, "base", 0x1E, "B", 1),
        ("cooldown-rearm", cooldown, "base", 0x08, "H", 0x8000),
        ("active-rearm", speed_hold, "base", 0x08, "H", 1),
        ("active-run", speed_hold, "base", 0x06, "H", 0x8000),
        ("active-kind", speed_hold, "extension", 0x00, "B", 0),
        ("speed-selected", speed_hold, "extension", 0x1C, "H", speed_hold.selected_target + 1),
        ("speed-target-rpm", speed_hold, "base", 0x14, "H", 1),
        ("speed-rpm-error", speed_hold, "base", 0x18, "H", 1),
        ("speed-control-error", speed_hold, "extension", 0x02, "h", speed_hold.control_error + 1),
        ("speed-law", speed_hold, "extension", 0x16, "H", speed_hold.law_output - 1),
        ("rpm-target-zero", rpm_hold, "base", 0x14, "H", 0),
        ("rpm-target-sign", rpm_hold, "base", 0x14, "H", 0x8000),
        ("rpm-selected", rpm_hold, "extension", 0x1C, "H", rpm_hold.selected_target + 1),
        ("rpm-target-speed", rpm_hold, "base", 0x0C, "H", 1),
        ("rpm-torque", rpm_hold, "base", 0x0E, "H", 1),
        ("rpm-speed-error", rpm_hold, "base", 0x10, "H", 1),
        ("rpm-integrator", rpm_hold, "base", 0x12, "H", 1),
        ("rpm-command", rpm_hold, "base", 0x16, "H", 1),
        ("rpm-control-error", rpm_hold, "extension", 0x02, "h", rpm_hold.control_error + 1),
        ("views-efficiency", idle, "extension", 0x0E, "H", 1000 ^ 1),
        ("views-trim", speed_hold, "extension", 0x1E, "B", 0x01),
        ("views-status", speed_hold, "extension", 0x1F, "B", 0x00),
    ):
        rows.engine_row(f"corrupt-{name}", mutate(state, region, offset, fmt, value), good,
                        corrupt=True)
    rows.engine_row("corrupt-ready-observe", records_unchecked(ready_observe), good, corrupt=True)

    # Ignition publisher: stock and ready outcomes.
    rows.ignition_row("ign-startup", records(idle), 30, None)
    rows.ignition_row("ign-idle", records(held), 30, None)
    rows.ignition_row("ign-cooldown", records(cooldown), 30, None)
    rows.ignition_row("ign-observe", records(observe_speed), 30, None)
    rows.ignition_row("ign-apc", records(speed_hold), 20, None, apc=0x40)
    rows.ignition_row("ign-apc-foreign", records(speed_hold), 20, None, apc=0xBF)
    rows.ignition_row("ign-speed", records(speed_hold), 20, None)
    rows.ignition_row("ign-speed-cut", records(ready_cut), 20, None)
    rows.ignition_row("ign-rpm", records(rpm_hold), 20, None)
    rows.ignition_row("ign-rpm-ready", records(ready_rpm), 25, None)
    rows.ignition_row("ign-rpm-cut", records(step(
        rpm_hold, replace(good, speed=80, rpm_native=380))), 20, None)
    rows.ignition_row("ign-floor", records(speed_hold), 55, None)
    rows.ignition_row("ign-above-floor", records(speed_hold), 70, None)
    rows.ignition_row("ign-wide", records(rpm_hold), 0x14, None, high=0xFFFFFF)
    rows.ignition_row("ign-trim-latched", records(speed_hold), 20, 31, contract=False)
    rows.ignition_row("ign-trim-range", records(held), 20, 61, contract=False)
    rows.ignition_row("ign-trim-negative", records(speed_hold), 20, 19, contract=False)
    # A trim within the latched trim outside a ready hold: the publisher
    # applies S, whatever P the adapter passes.
    rows.ignition_row("ign-apc-trim", records(speed_hold), 20, 30, apc=0x40, contract=False)
    rows.ignition_row("ign-idle-trim", records(held), 20, 25, contract=False)
    rows.ignition_row("ign-observe-trim", records(observe_speed), 20, 25, contract=False)
    rows.ignition_row("ign-config-valid", records(replace(
        speed_hold, flags=speed_hold.flags & ~model.Flag.CONFIG_VALID)), 20, 30, contract=False)
    rows.ignition_row("ign-corrupt", mutate(speed_hold, "base", 0x00, "B", 3), 20, 30,
                      contract=False)

    # Control publisher outside ACTIVE, which the engine never calls it in.
    rows.control_row("ctl-idle", idle, 400)
    rows.control_row("ctl-cooldown", cooldown, 0)

    for name, error, width in (
        ("frac-zero", 0, 40), ("frac-positive", 1, 40), ("frac-max", 32767, 40),
        ("frac-w0", -1, 0), ("frac-band-edge", -40, 40), ("frac-below-band", -41, 40),
        ("frac-band", -39, 40), ("frac-band-top", -1, 40), ("frac-wide", -1, 32767),
        ("frac-wide-low", -32766, 32767), ("frac-min", -32768, 32767), ("frac-unit", -1, 1),
    ):
        rows.fraction_row(name, error, width)
    return rows


def records_unchecked(state, spark=SPARK):
    """Encode a state that the model rejects, with its derived wire views."""
    base, extension = bytearray(model.STATE_SIZE), bytearray(model.EXTENSION_SIZE)
    for fields, buffer in ((model.BASE_STATE_FIELDS, base), (model.EXTENSION_FIELDS, extension)):
        for name, offset, fmt in fields:
            struct.pack_into(">" + fmt, buffer, offset, int(getattr(state, name)))
    valid_base, _valid_extension = model.encode_state(model.RuntimeState(), spark)
    base[0x1C:0x1E] = valid_base[0x1C:0x1E]
    base[0x20:] = valid_base[0x20:]
    for name, offset, fmt in model.EXTENSION_VIEW_FIELDS:
        source = spark if name in model.EXTENSION_EVENT_FIELD_NAMES else state
        struct.pack_into(">" + fmt, extension, offset, int(getattr(source, name)))
    return bytes(base), bytes(extension)


@dataclass(frozen=True)
class InterruptScenario:
    """One engine pass that an injected ignition publication interrupts.

    ``kind`` selects the claims of the pass: "steady" passes keep an ACTIVE
    ready record that every publication accepts, "activation" passes leave
    IDLE, "abort" passes leave ACTIVE and "recovery" passes repair a
    rejected record. A "republication" pass is an activation pass whose
    handler stores ``prior``, the publication-owned bytes of a first
    publication after the kind store, before it runs the second
    publication. The injected publisher receives the wide S and P of
    ``stock`` and ``effective``.
    """
    name: str
    kind: str
    regulator: model.RegulatorKind
    inputs: model.Inputs
    base: bytes
    extension: bytes
    stock: int
    effective: int
    prior: bytes = b""


# The bytes that an ignition publication stores: q at base +0x1A, S, P, a,
# ready, e and wire e at extension +0x08, and the wire views at +0x1E.
PUBLICATION_BYTES = ((0, 0x1A, 0x1C), (1, 0x08, 0x10), (1, 0x1E, 0x20))


def publication_bytes(records):
    """The publication-owned bytes of a record pair, in PUBLICATION_BYTES order."""
    return b"".join(records[region][start:end] for region, start, end in PUBLICATION_BYTES)


def with_publication_bytes(records, prior):
    """The record pair with its publication-owned bytes replaced by ``prior``."""
    parts = [bytearray(records[0]), bytearray(records[1])]
    offset = 0
    for region, start, end in PUBLICATION_BYTES:
        parts[region][start:end] = prior[offset:offset + end - start]
        offset += end - start
    return bytes(parts[0]), bytes(parts[1])


def first_publication(scenario):
    """The publication-owned bytes of a publication after the kind store of an activation.

    Until a publication rewrites it, the status view keeps kind NONE of the
    IDLE record, so the publication fails the check and stores the stock
    command, q = 0 and the wire views of the new kind and of the sample of
    the pass.
    """
    records = (scenario.base, scenario.extension)
    passed = engine_pass(records, scenario.inputs)[3]
    stock = model.ignition_step(replace(passed, flags=passed.flags & ~model.Flag.CONFIG_VALID),
                                scenario.stock, CALIBRATION, TABLE)
    return publication_bytes(_publish(*records, stock))


# The sampled fields of a pass, which precede every transition store.
SAMPLE_FIELDS = frozenset({
    "rpm_sample_native", "speed_sample", "cancel_speed_capture", "accepted_button",
    "speed_age", "input_status",
})


def interrupt_scenarios():
    """Return the passes of the interrupt rows.

    The IDLE record of both activations keeps a map index, a law output and a
    control error of an earlier hold that differ from the activation values,
    so that every activation store changes an observable field. Its law
    output 0 is the q = 1000 law of an RPM hold released at its ceiling.
    A second RPM activation starts from that record without the control
    error. A republication pass repeats each activation with the first
    publication after the kind store.
    """
    good = GOOD
    idle = model.RuntimeState()
    speed_hold = step(idle, good)
    rpm_hold = step(idle, replace(good, speed=80))
    ready_speed = model.ignition_step(speed_hold, 20, CALIBRATION, TABLE)
    ready_cut = model._publish_actuation(
        replace(ready_speed, torque_fraction=500, law_output=500), TABLE)
    ready_rpm = model.ignition_step(rpm_hold, 20, CALIBRATION, TABLE)
    stale = replace(idle, active_index_snapshot=3, law_output=0, control_error=55)
    rpm_inputs = replace(good, speed=80, rpm_native=380)
    scenarios = (
        InterruptScenario("irq-rpm-steady", "steady", model.RegulatorKind.RPM, rpm_inputs,
                          *records(ready_rpm), 50, 60),
        InterruptScenario("irq-speed-steady", "steady", model.RegulatorKind.SPEED,
                          replace(good, speed=275), *records(ready_cut), 55, 60),
        InterruptScenario("irq-rpm-activation", "activation", model.RegulatorKind.RPM,
                          replace(good, speed=80), *records(stale), 50, 60),
        InterruptScenario("irq-speed-activation", "activation", model.RegulatorKind.SPEED,
                          good, *records(stale), 55, 60),
        InterruptScenario("irq-abort", "abort", model.RegulatorKind.SPEED,
                          replace(good, button=model.BUTTON_RELEASED), *records(ready_cut),
                          55, 60),
        InterruptScenario("irq-recovery", "recovery", model.RegulatorKind.SPEED, good,
                          *mutate(ready_speed, "base", 0x1E, "B", ready_speed.applied_trim - 1),
                          55, 60),
        InterruptScenario("irq-rpm-activation-without-error", "activation",
                          model.RegulatorKind.RPM, replace(good, speed=80),
                          *records(replace(stale, control_error=0)), 50, 60),
    )
    scenarios += tuple(
        replace(item, name=item.name.replace("activation", "republication"),
                kind="republication", prior=first_publication(item))
        for item in scenarios if item.kind == "activation")
    for scenario in scenarios:
        decoded = _decode(scenario.base, scenario.extension)
        if (decoded is None) != (scenario.kind == "recovery"):
            raise ValueError(f"{scenario.name}: the model check of the record differs")
        final = engine_pass((scenario.base, scenario.extension), scenario.inputs)[3]
        expected_phase = {"steady": model.Phase.ACTIVE, "activation": model.Phase.ACTIVE,
                          "republication": model.Phase.ACTIVE,
                          "abort": model.Phase.COOLDOWN, "recovery": model.Phase.COOLDOWN}
        if final.phase != expected_phase[scenario.kind] or (
                scenario.kind in ("steady", "activation", "republication")
                and final.regulator_kind != scenario.regulator):
            raise ValueError(f"{scenario.name}: the pass does not reach its outcome")
    return scenarios


def interrupt_finals(scenario):
    """Return the records that a pass with one publication inside it may leave.

    These are the records of a publication before the pass and after it.
    Corrupt-state recovery clears both records after its check, so a
    publication between the check and the clear also leaves the records of
    the pass without a publication.
    """
    records = (scenario.base, scenario.extension)
    before = ignition_publication(records, scenario.stock, scenario.effective,
                                  contract=False)
    publish_first = engine_pass((before.base, before.extension), scenario.inputs)[:2]
    passed = engine_pass(records, scenario.inputs)[:2]
    after = ignition_publication(passed, scenario.stock, scenario.effective, contract=False)
    finals = (publish_first, (after.base, after.extension))
    return finals + ((passed,) if scenario.kind == "recovery" else ())


def render_interrupts(scenarios):
    """Return the C header of the interrupt rows."""
    lines = [
        "/* Generated by tools/sh-elf-run/rolling_launch_rows.py from the schema 6",
        "   model in patches/rolling_launch.py. */",
        "struct rl_inputs {",
        "    uint8_t selector[8];",
        "    uint8_t ascd, button, age, hcan, port, coolant;",
        "    uint16_t speed, wire, rpm, pedal;",
        "};",
        "struct irq_scenario {",
        "    const char *name;",
        "    struct rl_inputs in;",
        "    uint8_t base[44], ext[32];",
        "    uint32_t stock, effective;",
        "    uint8_t has_prior, prior[12];",
        "};",
        f"static const uint8_t rl_config[102] = {_bytes(CALIBRATION.to_bytes())};",
        f"static const uint8_t rl_table[82] = {_bytes(TABLE.to_bytes())};",
        "static const struct irq_scenario irq_scenarios[] = {",
    ]
    for scenario in scenarios:
        stock = ignition_publication((scenario.base, scenario.extension), scenario.stock,
                                     scenario.effective, contract=False)
        prior = scenario.prior or bytes(12)
        if len(prior) != 12:
            raise ValueError(f"{scenario.name}: prior publication bytes differ in size")
        lines.append(
            f'    {{"{scenario.name}", {_inputs(scenario.inputs)},\n'
            f"     {_bytes(scenario.base)},\n     {_bytes(scenario.extension)},\n"
            f"     0x{stock.stock_wide:08x}U, 0x{stock.effective_wide:08x}U,\n"
            f"     {int(bool(scenario.prior))}, {_bytes(prior)}}},")
    lines.append("};")
    return "\n".join(lines) + "\n"


def _inputs(values):
    selector = (values.active_index, values.selector_phase, values.selection_count,
                values.selector_elapsed, values.feedback_pulses, values.feedback_phase,
                values.feedback_ticks, values.feedback_reserved)
    return (f"{{{_bytes(selector)}, {values.ascd_status}, {values.button}, "
            f"{values.speed_frame_age}, {values.hcan1_state}, {values.port_input_state}, "
            f"{values.coolant}, {values.speed}, {values.speed_wire_word}, "
            f"{values.rpm_native}, {values.pedal}}}")


def _bytes(data):
    return "{" + ",".join(f"0x{value:02x}" for value in data) + "}"


def _signed(value):
    return f"(int32_t){value}" if value >= 0 else f"(int32_t)({value})"


def render(rows, variant=None):
    """Return the C header of one gate run."""
    lines = [
        "/* Generated by tools/sh-elf-run/rolling_launch_rows.py from the schema 6",
        "   model in patches/rolling_launch.py. */",
        "struct rl_inputs {",
        "    uint8_t selector[8];",
        "    uint8_t ascd, button, age, hcan, port, coolant;",
        "    uint16_t speed, wire, rpm, pedal;",
        "};",
        "struct engine_row {",
        "    const char *name;",
        "    uint8_t config, restore, periodic;",
        "    struct rl_inputs in;",
        "    uint8_t base[44], ext[32], base_out[44], ext_out[32];",
        "};",
        "struct publisher_row {",
        "    const char *name;",
        "    uint8_t config, apc;",
        "    uint32_t r3, r4, r5, r5_out;",
        "    uint8_t base[44], ext[32], base_out[44], ext_out[32];",
        "};",
        "struct fraction_row {",
        "    const char *name;",
        "    int32_t error;",
        "    uint32_t width, fraction;",
        "};",
        f"#define RL_CONFIG_COUNT {len(rows.configs)}U",
        "static const uint8_t rl_configs[RL_CONFIG_COUNT][102] = {",
        *(f"    {_bytes(config)}," for config, _table in rows.configs),
        "};",
        "static const uint8_t rl_tables[RL_CONFIG_COUNT][82] = {",
        *(f"    {_bytes(table)}," for _config, table in rows.configs),
        "};",
        f"static const uint8_t rl_startup_base[44] = {_bytes(rows.startup[0])};",
        f"static const uint8_t rl_startup_ext[32] = {_bytes(rows.startup[1])};",
        "static const struct engine_row engine_rows[] = {",
    ]
    for row in rows.engine:
        lines.append(
            f'    {{"{row.name}", {row.config}, {int(row.restore)}, {int(row.periodic)}, '
            f"{_inputs(row.inputs)},\n"
            f"     {_bytes(row.base)},\n     {_bytes(row.extension)},\n"
            f"     {_bytes(row.base_out)},\n     {_bytes(row.extension_out)}}},")
    lines.append("};")
    for name, entries in (("ignition_rows", rows.ignition), ("control_rows", rows.control)):
        lines.append(f"static const struct publisher_row {name}[] = {{")
        for row in entries:
            lines.append(
                f'    {{"{row.name}", {row.config}, {row.apc}, 0x{row.r3:08x}U, '
                f"0x{row.r4:08x}U, 0x{row.r5:08x}U, 0x{row.r5_out:08x}U,\n"
                f"     {_bytes(row.base)},\n     {_bytes(row.extension)},\n"
                f"     {_bytes(row.base_out)},\n     {_bytes(row.extension_out)}}},")
        lines.append("};")
    lines.append("static const struct fraction_row fraction_rows[] = {")
    for row in rows.fraction:
        lines.append(f'    {{"{row.name}", {_signed(row.error)}, {row.width}U, {row.fraction}U}},')
    lines.append("};")
    return "\n".join(lines) + "\n"


def counts(rows):
    return {
        "engine": len(rows.engine),
        "ignition": len(rows.ignition),
        "control": len(rows.control),
        "fraction": len(rows.fraction),
    }


def main(argv=None):
    rows = build()
    sys.stdout.write(render(rows))
    print(" ".join(f"{key}={value}" for key, value in counts(rows).items()), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
