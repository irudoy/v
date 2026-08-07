# JK08A diagnostic publication and monitor model

## Scope

This document describes the stable relationships between exact JK08A firmware
data flow and the source-preserving diagnostic corpus. Addressed claims,
evidence sites, source-claim identities, applicability, ROM scope, and review
priority remain canonical in `JK08A.diagnostic-bindings.csv`, `JK08A.funcs.csv`,
`JK08A.vars.csv`, `JK08A.findings.csv`, and `JK08A.dtc.csv`.

The static layer distinguishes three questions:

1. Which exact firmware object publishes or consumes a value?
2. Which source-specific diagnostic claim names or scales that value?
3. Does hardware on the target ECU confirm the physical interpretation?

A code-proven pointer or dispatcher answers the first question. A factory or
community source answers the second with its own applicability. Only a bench or
vehicle observation answers the third.

## UDS data publication

`FUN_0003235C` is the exact ReadDataByIdentifier publisher for the reviewed
service `0x22` ranges. Its pointer tables bind selected DIDs to RAM bytes or
words. The function contract and every reviewed pointer site are recorded once
in `JK08A.funcs.csv`; individual semantic joins are recorded in
`JK08A.diagnostic-bindings.csv`.

The current reviewed model establishes these durable behaviors:

- multiple ignition-timing DIDs are aliases for one published byte rather than
  independent timing states;
- fuel-trim DIDs return the high bytes of four internal Q8.8-percent words and
  agree with the exact Mode 01 STFT/LTFT ordering;
- injection-pulse DIDs return the first two words of the six-channel calculated
  pulse array described in `JK08A.fuel.md`;
- the intake-cam timing DID returns a centered two-bank software value whose
  physical degree conversion remains homologous evidence;
- a returned value can have mode-dependent transforms, so one affine diagnostic
  formula is not automatically a universal internal representation.

Exact pointer identity does not establish an ECM terminal, peripheral channel,
or physical unit. Those remain separate claims and are not promoted by name
similarity.

## Intake-air-temperature and P0128 model

The exact DID table points the reviewed intake-air-temperature DID to an
AN1-derived runtime byte. The scheduler copies that byte into the previous-cycle
snapshot consumed by the P0128 thermostat model. Homologous measured Nissan
diagnostics provide the `raw - 50` temperature conversion; the firmware trace
establishes the byte flow but not target-ECU terminal continuity.

The P0128 model contains several map-weighted balance terms. Their exact
arithmetic and DTC association are recorded in the map, function, variable, and
diagnostic-binding rows. Several involved maps, axes, and configuration
coefficients are zero in stock JK08A, making their individual contributions
zero while the surrounding scheduler and state machine remain live. A stock
zero term is not equivalent to absent code, and a calibrated change requires a
new behavior and hardware review.

## Rear oxygen sensor and catalyst monitors

The rear oxygen sensor model contains independent paths that must not be merged:

- a bank-indexed dispatcher for slow response and low/high voltage descriptor
  pairs;
- a second high-voltage descriptor path using separate working arrays;
- a rear-heater circuit monitor with independent low and high thresholds;
- a command/status observation DID whose bit names come from a homologous
  profile;
- an independent catalyst-efficiency result dispatcher;
- a calibrated catalyst-limit branch using a bank metric and limit array.

Duplicate DTC codes can therefore represent distinct descriptor records and
firmware paths. `JK08A.dtc.csv` and the diagnostic corpus preserve them rather
than collapsing by public code.

The calibrated catalyst-limit branch is stock-unreachable because its unsigned
limit table is zero. The independent result dispatcher remains present, so the
stock-zero branch does not disable the entire P0420/P0430 subsystem. Internal
rear-O2 and catalyst metric units remain unresolved.

## EVAP monitors

The exact firmware contains a shared EVAP diagnostic coordinator plus separate
pressure and leak-monitor paths. Several coordinator branches are skipped by
stock configuration even though their producer and descriptor code exists.
Other leak and range paths remain outside those gates.

The fuel-level-derived EVAP coordinate uses a meter CAN payload field, a slow
filter, and a table whose stock cells are all the same sentinel. Downstream code
uses the resulting high byte in signed and unsigned forms. The exact path proves
fuel-level monitor context and sentinel behavior, not voltage, percentage, or
tank-volume conversion.

The canonical binding rows distinguish:

- exact descriptor and dispatcher identity;
- stock reachability of a specific branch;
- producer and consumer relationships;
- homologous factory terminology;
- unresolved physical metric and unit.

Changing a configuration-disabled or sentinel calibration requires review of
the re-enabled control path and cannot inherit the stock liveness conclusion.

## Static binding review

Candidate extraction starts from a semantic-free Ghidra reference inventory.
A DID literal and same-function RAM reference remain a worklist item until a
trace closes request dispatch, returned storage, conversion, and source scope.
The candidate output is deliberately incompatible with the binding loader.

Accepted rows require machine-address evidence and one exact source claim.
Firmware confidence, source applicability, inheritance scope, and priority are
independent. Static rows cannot use `silicon` confidence.

The tooling and query interface are documented in
`../tools/diagnostics/README.md`. The graph projection and provenance audit are
documented in `../tools/memgraph/README.md`.

## Hardware boundary

Static analysis does not establish physical sensor conversion, terminal
assignment, full monitor enable conditions, peripheral side effects, or target
vehicle behavior. Hardware promotion requires the exact ROM, a controlled input
or operating condition, the expected diagnostic response, and an independent
electrical or vehicle observation. A homologous manual or community logger can
define a test hypothesis but cannot close this boundary.
