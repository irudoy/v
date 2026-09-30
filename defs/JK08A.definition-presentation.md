# JK08A tuning-editor presentation

## Purpose

The presentation layer for RomRaider and TunerPro is `[editor]` of the `7mfk`
tables and axes and `[logparam]` of the `7mfk` RAM in `kb/`, with the default
visibility, the switches, and the JK08A header metadata of
`kb/feature/definitions.toml`. `uv run kb project` renders it into
`JK08A.overrides.toml`, which the definition generators read, and
`uv run kb set <meaning> editor.<key>=<value>` edits one key. The layer
supplies editor names, functional categories, visibility, ordering, and edit
increments without changing the graph-backed map identity, geometry, scaling,
or evidence.

`tools/mapkit/presentation_audit.py` validates the layer before definition
generation. The audit keeps storage addresses, raw transforms, and
source-vocabulary artifacts out of visible names and checks that every
map-switching family uses the same name as its canonical table.

## Naming policy

Visible names describe the runtime role first and the variant second:

```text
Ignition Timing Surface - High-Octane State
Timing-State Addend - Warm DFCO Transition
Throttle Angle-to-Area Conversion - Validation Copy
Map 3 - DFCO Full Restore RPM Threshold
```

Storage addresses, raw transforms such as `x-128`, units, and confidence belong
in table metadata and comments. They are not part of the editor name.

The Nissan source term `Trustful` denotes a duplicate validation table. The
editor uses `Validation Copy`, which states the operational requirement: paired
tables must remain identical unless exact code establishes a different rule.

The names of the internal-calculation calibrations that the sweeps over
`0x11C6D..0x153B8`, `0x11E9E..0x12808`, and `0x11F6A..0x19190` identified are
operational. They state the value role that code confirms, the proven
arithmetic use, or an explicitly marked catalog hypothesis; the physical
signals of those calculations are unresolved.

## Functional taxonomy

The visible calibration hierarchy uses these primary domains:

- `Fuelling` for MAF transfer, BFS constants, load normalization, injection,
  compensation, and deceleration fuel cut;
- `Ignition Timing` for timing-state surfaces, state-path controls, state
  corrections, and knock thresholds;
- `Electronic Throttle Control` for pedal thresholds, requested-torque
  conversion, and throttle geometry;
- `Torque Model` for the engine-torque surface and its runtime terms;
- `Variable Valve Timing` for intake and exhaust CVTC target surfaces;
- `Limiters` for moving and stationary engine-speed controls.

Map Switching keeps all five storage slots in the category of the canonical
calibration. The `Map N - ` prefix identifies storage selection and does not
create a separate functional category. The common JK08A definitions expose
all five slots: Map 1 is the stock storage, and Map 2 through Map 5 point into
the allocated project layout and are active at runtime only with the
map-switching patch.

Rolling Launch exposes its validated activation thresholds, bounded-retard
ramp width, RPM offset, and RPM hysteresis as direct tables. Five independent
masked controls edit bits 0 through 4 of the `enable_mask` byte and preserve
every other map-enable bit.

## Axes

Calibration axes stay embedded in their tables; the definitions carry no
separate editable reference views of axes. `[editor]` of an axis sets only its
name, display format, and edit increments, and its facts stay in the graph and
`JK08A.axes.csv`.

## Logger parameters

`[logparam]` of the meaning of a runtime lookup operand names the RomRaider
Logger parameter that carries its physical quantity for the Overlay Log, the
axis units of that parameter, and the name of the static axis whose reviewed
labels it compares with. A ROM array axis names the parameter when its scale
evidence rests on exactly that `indexed_by` operand, its units equal the
declared units, and both sides convert through the same multiplier: the
declaration repeats the axis expression in `scale`, or code establishes the
axis scale. A static axis names it when the map declares `static_axis_operand`
and carries labels under the declared name. The IDs are the external
parameters that the CAN dashboard live value feed publishes
(`tools/can_dashboard/live_feed.py`). A relocated target definition leaves out
every declaration whose parameter the feed publishes from a telemetry field
that the target encodes from a cleared zero source.

## Visibility boundary

Maps that pass the definition gate are visible by default (`default_emit` of
`definitions`). Internal, diagnostic-internal, internal-coordinate, and
unidentified research maps carry an explicit `emit = false` in their own
`[editor]` and remain in the canonical ledger.

Four reviewed tables remain in the canonical graph and ledger but are hidden
from both tuning editors:

| Address | Runtime role | Visibility reason |
|---|---|---|
| `0x0ABBA` | Knock-sensor circuit monitor mode A | Diagnostic-only surface; the direction of effect on the verdict is unresolved |
| `0x0ABFA` | Knock-sensor circuit monitor mode B | Diagnostic-only surface; the direction of effect on the verdict is unresolved |
| `0x120F6` | Conditional DFCO entry delay | Selected only by a stock-inactive feature branch |
| `0x1491A` | Diagnostic Calculated Load reference | Changes diagnostic publication, not the engine-control load coordinate |

Hiding a table is a presentation decision. Its address, exact access path,
semantics, and evidence remain available for analysis and can be reconsidered
without rediscovery.

The rotation-monitor threshold maps `0x0B61A`, `0x0B71A`, and `0x0B81A` have a
structure that code confirms and an unresolved physical scale (offset binary
with a `0x80` sentinel). The definition gate keeps them out of both editors,
and they have no presentation entries; `JK08A.notes.md` names their canonical
rows.

## Verification

Run the source audit and paired-definition tests with:

```bash
uv run python tools/mapkit/presentation_audit.py
uv run pytest -q tools/mapkit/tests
```

The generated XML and XDF must then be reproduced together through
`tools/mapkit/emit_def.py`; neither generated file is an editable authority.
