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
- intake-cam actual timing, exhaust-cam actual timing, and their common targets
  have distinct exact RAM publications;
- a returned value can have mode-dependent transforms, so one affine diagnostic
  formula is not automatically a universal internal representation.

The exact cam-timing pointer bindings currently are:

| DID | Exact returned byte | Firmware role |
|---|---:|---|
| `0x1164` | `0xFFFF2324` | bank-1 actual exhaust-cam timing |
| `0x1165` | `0xFFFF2325` | bank-2 actual exhaust-cam timing |
| `0x1166` | `0xFFFF2327` | common conditioned exhaust-cam target |
| `0x122F` | `0xFFFF1AAC` | bank-1 exhaust-VTC duty |
| `0x1230` | `0xFFFF1AAE` | bank-2 exhaust-VTC duty |

`FUN_0008F168` independently consumes the actual and target exhaust values in
the monitor paths associated with P1078/P1084 and P0014/P0024. This closes the
subsystem identity without relying on a community label. The centered-byte
arithmetic is exact; the `raw * 0.5 - 64 degCA` conversion remains homologous
candidate evidence because public profiles disagree on the multiplier.

Exact pointer identity does not establish an ECM terminal, peripheral channel,
or physical unit. Those remain separate claims and are not promoted by name
similarity.

## Dynamic local-identifier streaming

The exact JK08A diagnostic dispatcher routes SID `0xAC` to `FUN_00033810`
and SID `0x21` to `FUN_000328C0`. Together they implement a stock, volatile
byte-gather stream. This mechanism changes diagnostic-session RAM only; it
does not patch executable code or flash and it is not a periodic broadcast-CAN
publisher.

The following byte strings are application payloads. KWP format, target and
source headers, length encoding, and checksum remain transport framing and are
not included:

```text
Define:   AC 81 (83 A3 A2 A1 A0)+
Success:  EC 81

Read:     21 81 TXM NRS
Response: 61 81 DATA...
```

For descriptor `0x83`, `A3` is the most-significant address byte and `A0` is
the least-significant byte. `FUN_0002F2D4` reconstructs the address in
big-endian order. Each descriptor adds one 32-bit source pointer and exactly
one response byte. A two-byte word therefore needs two descriptors, normally
for `address` and `address + 1`; a four-byte value needs four. Response bytes
retain descriptor order.

A fresh `0x81` definition resets the output count. Before each descriptor the
parser requires the current count to be at most `0x3D`, so a definition made
only from `0x83` descriptors can contain 62 output bytes. Compact descriptor
`0x01` expands a predefined local ID to four consecutive pointers. Descriptor
`0x02` selects the predefined `0x11` through `0x16` table families and expands
the selected entry to its declared width. Those compact forms can add multiple
output bytes at one parser step; arbitrary-address logger profiles should use
`0x83` and enforce the 62-byte limit themselves.

The resulting pointer array begins at `0xFFFF9820`, its byte count is stored at
`0xFFFF9920`, and the active dynamic LID is stored at `0xFFFF3EE2`. Successful
definition returns only `EC 81`; the ECU does not echo the pointer schema, so
the client must retain the exact ordered profile. The definition is runtime
state and must be recreated after diagnostic-session or ECU reset.

### Read validation and memory safety

The dynamic read path accepts only a LID above `0x80` that equals the active
value. It accepts transmission modes `0x04` and `0x06`; other modes, a stale
LID, malformed definition, or rejected address produce NRC `0x12` through the
common negative-response builder.

SID `0xAC` does not apply a general memory-map or side-effect check while
storing a pointer. SID `0x21` treats `0xFFFE0000..0xFFFE0FFF` as a special
asynchronous range, rejects `0xFFFE1000..0xFFFEFFFF`, and directly
byte-dereferences other entries. Direct dereference is not a safety guarantee:
an arbitrary peripheral or invalid address can have side effects or fault.
Hardware use is limited to reviewed, side-effect-free exact-RAM sources.

### Transmission modes

`FUN_000328C0` stores `TXM` at `0xFFFF8212` and `NRS` at `0xFFFF8214` before
building the first response.

- Mode `0x04` increments finite-response counter `0xFFFF8213` in transmit
  completion handler `FUN_0002F12C`. Responses continue until the counter
  reaches `NRS`, then the handler clears both counter and mode. Intermediate
  transmissions use `FUN_0002F866` without redispatching SID `0x21`; this path
  does not establish a fresh pointer-list read between responses.
- Mode `0x06` bypasses the `NRS` comparison. The transmit-complete handler sets
  `0xFFFF82E4.bit7`; diagnostic state machine `FUN_0002EA0A` clears the flag,
  transitions through its response states, and calls dispatcher
  `FUN_0002F928`. The dispatcher invokes `FUN_000328C0` again, rebuilding
  `61 81 DATA...` from the current source bytes for every response. `NRS` is
  stored but does not terminate this stream.

Mode `0x06` is therefore the stock mechanism for successive live samples. It
removes one request per parameter and reads all selected bytes into one fixed
schema, but response width still consumes serial bandwidth. Continuous does
not mean one new physical measurement per response: freshness is bounded by
both the response cadence and each source variable's producer cadence.

### Snapshot boundary

`FUN_000328C0` traverses `0xFFFF9820` and dereferences each pointer in order.
It does not mask interrupts or copy the selected sources into an atomic staging
buffer first. An interrupt or scheduled producer can therefore update part of
a multi-byte value or one group of related values while the response is being
built. Byte order is deterministic, but time coherence is not.

The unmodified-ROM stream is suitable for discovery and compact tuning logs
when tearing is measured and tolerated. A coherent high-rate profile requires
an executable change that captures selected values at one known scheduler
boundary and exposes sequence, ECU tick, validity, and age. Such a patch falls
under the repository's independent SH-2E executable-verification gate.

Static code establishes service grammar and repeat behavior but not the active
vehicle's KWP framing, selected SCI baud rate, adapter turnaround, or achieved
cadence. Those remain bench measurements using raw request and response
timestamps before engine use.

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
