# JK08A tuning-editor presentation

## Purpose

`JK08A.overrides.toml` is the canonical presentation layer for RomRaider and
TunerPro. It supplies editor names, functional categories, visibility, ordering,
and edit increments without changing the graph-backed map identity, geometry,
scaling, or evidence.

`tools/mapkit/presentation_audit.py` validates the source layer before
definition generation. The audit keeps storage addresses, raw transforms, and
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
create a separate functional category.

## Visibility boundary

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

## Verification

Run the source audit and paired-definition tests with:

```bash
uv run python tools/mapkit/presentation_audit.py
uv run pytest -q tools/mapkit/tests
```

The generated XML and XDF must then be reproduced together through
`tools/mapkit/emit_def.py`; neither generated file is an editable authority.
