# JK08A evidence index

## Purpose and scope

This file is the compact evidence index for the canonical JK08A annotation
layer. It is not a status report, execution journal, worklist, or generated
catalog. The exact stock ROM identity and provenance are owned by
`rom-images/roms.csv` and `rom-images/README.md`.

JK08A is the sole live annotation source for its verified exact-code family.
`defs/rom-inheritance.toml` projects those annotations onto JK03A while each ROM
retains its own image measurements, Ghidra export, graph nodes, and applicable
diagnostic bindings.

## Evidence routing

| Evidence or decision | Canonical location |
|---|---|
| Interpolation entries, geometry, storage type, and implicit steps | `JK08A.interp.csv` |
| Map semantics, role, scaling, confidence, evidence, and note | `JK08A.findings.csv` |
| Axis semantics and scaling | `JK08A.axes.csv` |
| Function semantics and callable contracts | `JK08A.funcs.csv` |
| RAM and peripheral semantics | `JK08A.vars.csv` |
| Firmware-to-diagnostic associations | `JK08A.diagnostic-bindings.csv` |
| DTC descriptor and attribute edit ranges | `JK08A.dtc.csv` |
| Definition names, categories, visibility, and presentation | `JK08A.overrides.toml` |
| Exact target/source relationship | `rom-inheritance.toml` |
| Measured catalog and open semantic work | Generated `JK08A.maps.csv` |
| RomRaider and TunerPro output | Generated `JK08A.xml` and `JK08A.xdf` |
| Hardware-derived image identities and outcomes | `patches/hardware-results.toml` |

Evidence listings and decompilation are reproducible from the exact Ghidra
program using `tools/ghidra/`. Source claim rows retain the relevant address,
site, constant, dependency, and confidence rather than embedding full listings
in this index.

## Stable analysis rules

### Exact image first

An address from another ECUID is never transferred directly. A2L, vendor
documentation, and homologous ROMs provide vocabulary, geometry hypotheses,
and comparison anchors. Target addresses, values, reachability, and code claims
come from the exact registered image or a hash- and range-verified exact-code
inheritance relation.

### Use sites define array roles

The same ROM array can be a map at one site and an axis at another. Forward and
inverse lookup pairs may read the same points in opposite directions. Role,
orientation, and scaling therefore follow the accessor and consumer, not array
shape or address alone.

### Geometry is structural evidence

The interpolation entry and finisher establish dimensions, element width, axis
clamps, and table orientation. They do not establish physical meaning. For the
explicit two-axis convention, the `r5` axis labels table rows and the `r6` axis
labels columns in the generated editors.

### Branch-selected operands remain sets

A `MULTIEQUAL` at an accessor represents real calibration selection. Resolver
output preserves aligned operand tuples rather than selecting one branch or
forming a Cartesian product. A backtrack/data-flow conflict stays visible until
the controlling path is reviewed.

### GBR is local

Functions establish their own GBR base. Analysis resolves GBR from each
containing function or retains a caller-relative result; no global GBR value is
valid for the firmware.

### Reference does not prove liveness

A table can be present and referenced while a stock configuration byte skips
its read. A zero or fill-valued map can be a live neutral calibration, a
saturated threshold, a sentinel, or unused flash. Only the consumer and gating
trace establish the role. Re-enabling a stock-disabled path requires a new
review of its complete behavior.

### Claims have independent confidence

Map identity, function contract, and physical scale use separate confidence and
evidence. A code-proven address can retain candidate engineering units. A
code-proven diagnostic pointer can use a homologous name without making that
source exact for JK08A.

### Absence of a static reader is a boundary

A complete p-code census with no resolved reader or writer narrows the software
model but does not exclude an interrupt, DMA transfer, peripheral side effect,
or unmodeled hardware path. Such gaps remain explicit hardware questions.

## Subsystem specifications

The following documents own complete current subsystem models:

- `JK08A.fuel.md` - dual-bank MAF, Base Fuel Schedule, Fuel Compensation Main,
  multiplier, trims, calculated pulse words, and injector-output boundary;
- `JK08A.dfco.md` - deceleration fuel-cut thresholds, delays, state machine,
  arbitration, and output path;
- `JK08A.fuel-inhibit.md` - all global fuel-output inhibit contributors and
  final mask precedence;
- `JK08A.limiters.md` - main and stationary engine-speed fuel cuts plus the
  separate request limiter;
- `JK08A.throttle-control.md` - dual accelerator-pedal acquisition, signed
  request arbitration, opening-area composition, per-channel targets,
  throttle feedback, fixed-point regulation, and the ATU-II PWM boundary;
- `JK08A.ignition-output.md` - final timing coordinate, late-retard insertion,
  APC scheduling, and fallback gate;
- `JK08A.diagnostics.md` - UDS publication, diagnostic bindings, rear-O2,
  catalyst, EVAP, and P0128 monitor boundaries;
- `patches/map-switching-selector.md` - current five-slot runtime and gates;
- `patches/rolling-launch.md` - current Rolling Launch behavior and safety;
- `patches/immo-off-developer-flag.md` - Developer Immobilizer execution path;
- `tools/map-analysis-pipeline.md` - current discovery, graph, provenance, and
  definition projection contract.

## Addressed evidence groups

This index points to structured rows without reproducing their fields.

### Airflow and main fuel

- MAF curves `0x141F4` and `0x14274`, their ADC/DID path, contribution shares,
  and Base Fuel Schedule chain are represented across `findings.csv`,
  `funcs.csv`, `vars.csv`, and `diagnostic-bindings.csv` and modeled in
  `JK08A.fuel.md`.
- Fuel Compensation Main `0x0A29A`, fuel target control `0x0B33A`, common gain,
  transient additive terms, parity bases, and the calculated six-channel words
  are owned by the same structured layer and fuel specification.

### Fuel cuts and rotational limits

- Main fuel cut `0x0934E`, stationary cut state, DFCO cut/restore families, the
  aggregate inhibit mask, and request limiter `0x0942C` are modeled in
  `JK08A.limiters.md`, `JK08A.dfco.md`, and `JK08A.fuel-inhibit.md`.
- Target-vehicle A/B evidence establishes that the lower/full-restore table
  `0x12818` can veto moving entry while the stock Hold and Entry request pair
  remains unchanged. Under stock compile-time flags, upper/intermediate table
  `0x1298C` affects the low-speed class-2 band but is ignored at speed count 4
  and above. Exact image and capture identities are owned by
  `patches/hardware-results.toml`.
- Rotation-monitor threshold maps `0x0B61A`, `0x0B71A`, and `0x0B81A` are not
  ignition maps. Their role, saturated finisher behavior, and dead-table
  conclusion are canonical in `JK08A.findings.csv` and the associated function
  and variable rows.

### Ignition, knock, and CVTC

- The cold, high-octane, and high-detonation ignition triplet, masked knock
  window, shared axes, and candidate physical scales are represented in the map
  and axis claims. Final command-to-APC behavior is modeled separately in
  `JK08A.ignition-output.md`.
- Timing-state table `0x12196` is the default/post-transition addend and
  `0x1219E` is the warm DFCO-transition addend for the nonzero portion of an
  85-count timer. Table `0x121A6` is stock-inert because its feature flag is
  clear and its lifecycle word cannot satisfy the strict threshold. All three
  use a code-proven `x-128` transform. Target-vehicle evidence establishes
  one-for-one final-coordinate propagation for `0x12196`; the catalog Cold
  Idle qualifier and physical degree scale are not target-proven semantics.
- The intake-CVTC main, cold, and conditional correction surfaces and their
  coolant blend are represented by the map, function, variable, and diagnostic
  rows. Candidate physical degree conversion remains distinct from code-proven
  centered arithmetic.
- Accelerator-pedal hysteresis `0x08FDC`/`0x08FDE` is an ETC state threshold,
  not an engine-speed limiter. Exact sensor and DTC relationships are recorded
  in the structured claims.

### Electronic throttle

- The stock command route is `ffff243c` through the shared signed-request
  subsystem to `ffff19c6`, inverse coordinate `ffff198a`, opening-area request
  `ffff183e`, shared target `ffff19b2`, channel targets `ffff28bc`/`ffff28be`,
  regulator effort `ffff37b8`/`ffff37bc`, and ATU-II BFR6A-D. The complete
  branch and hardware boundary are modeled in `JK08A.throttle-control.md`.
- Direct inverse coordinate `ffff1984` is calculated from `ffff243c`, but its
  `000730fc` branch is disabled by stock `0x870c.bit7 = 0`. `ffff40c6` is a
  derived common opening monitor rather than a motor-command word.
- Lift-off retains an idle/opening-area contribution at `ffff1340` before the
  per-channel target limits. DFCO state and throttle target therefore remain
  separate control decisions.

### Diagnostic and emissions models

- UDS pointer publication, fuel trims, calculated injection pulse DIDs, intake
  cam timing, rear O2, catalyst, heater, EVAP, and P0128 relationships are
  routed through `JK08A.diagnostic-bindings.csv` and summarized in
  `JK08A.diagnostics.md`.
- Duplicate DTC codes retain separate exact descriptor records and paths.
  Definition controls come only from `JK08A.dtc.csv`.

### Research-only calculations

- Filter weights, reciprocal coordinates, offset-binary transforms, composite
  coefficients, monitor windows, stock-zero model terms, and unresolved torque
  surfaces remain addressed claims in `findings.csv`, `funcs.csv`, `vars.csv`,
  and `axes.csv`.
- These rows stay hidden from editor output through explicit presentation
  policy when their physical semantics or scaling is incomplete. Hiding is not
  deletion and does not lower their review visibility in the ledger.

## Open evidence classes

The live worklist is derived from `JK08A.maps.csv` and read-only graph queries,
not stored as frozen positions in this file. Current open classes include:

- candidate maps without a closed semantic consumer trace;
- fallback, dynamic, or branch-selected operands that require local control
  analysis;
- physical scale or axis meaning supported only by homologous catalogs;
- software arrays whose hardware producer or consumer is not visible to the
  complete application-code p-code census;
- stock-disabled branches whose behavior after calibration change is not
  validated;
- diagnostic names or conversions that lack exact target hardware evidence.

`tools/memgraph/queries.cypher` derives the current sets. Accepted conclusions
are written into canonical source rows, followed by dry-run, ingestion, strict
provenance audit, and definition regeneration.

## Verification boundary

Graph topology, exact code traces, diagnostic sources, and executable simulator
gates remain distinct evidence layers. Only a controlled bench or vehicle test
can establish silicon behavior. An instruction-changing image also requires the
mandatory GNU SH-2E gate under `tools/sh-elf-run/` before hardware testing.
