# JK08A five-slot map switching

This document defines the current map-switching runtime for the exact JK08A
code base. The runtime provides five calibration slots, a steering-wheel
selector, atomic limiter publication, and CRUISE-lamp confirmation.

The authoritative storage, hook, family, and payload metadata is held in:

- `map-switching-layout.toml` for ROM/RAM ownership and runtime structure;
- `map-switching-payloads.toml` for exact assembled payload bytes;
- `map_switching_selector.py` for the independent state and publication model;
- `hardware-results.toml` for immutable historical image identities and
  hardware outcomes.

This document does not define a concrete tuned image. Calibration profiles,
derived ROM bytes, and active tune identities remain local and unversioned.

## Status and scope

The current endpoint is software-verified. Vehicle capture of firmware `1.11`
confirms Map 2 and Map 3 commits, serialized pulse counts, and selected
calibration effects. It rejects the current visual ON state: state 6
illuminates SET together with CRUISE on the exact target. The timing is 30
serializer invocations ON followed by 30 invocations OFF for each pulse.
Hardware status is read only from `hardware-results.toml`; successful results
from earlier compositions do not qualify a changed endpoint.

The runtime switches these families:

| Family | Access path |
| --- | --- |
| DFCO hold | lookup adapter |
| DFCO cut | lookup adapter |
| DFCO full restore | lookup adapter |
| DFCO intermediate restore | lookup adapter |
| high-octane ignition timing-state surface | lookup adapter |
| high-detonation ignition timing-state surface | lookup adapter |
| default/post-transition timing-state addend (`0x12196`) | lookup adapter |
| warm DFCO-transition timing-state addend (`0x1219E`) | lookup adapter |
| exhaust CVTC target | lookup adapter |
| main fuel compensation | lookup adapter |
| fuel-cut limiter cluster | RAM shadow |
| throttle limiter cluster | RAM shadow |

Shared axes, sensor models, VTC/VVEL data, diagnostic controls, NATS data, and
all unlisted calibrations remain single-copy stock data.

## Slot contract

`map-switching-layout.toml` declares five one-based user slots. The runtime
stores a zero-based active index. Map 1 occupies each stock calibration address;
Maps 2 through 5 occupy layout-owned ROM ranges.

When the production builder receives an unpatched base, it initializes Maps 2
through 5 from Map 1. When it migrates a complete compatible runtime, it
preserves every existing Map 2 through Map 5 calibration byte. The builder
rejects partial runtimes, unknown payloads, mixed hooks, and modifications to
protected code.

The ten adapter-backed families select a ROM base for the active slot before
entering the displaced stock lookup. The two limiter families use RAM shadows
because their consumers read clusters through several paths that cannot be
changed independently.

## Selector input

The selector host runs after the stock ASCD input debounce and consumes the
stock previous/current one-hot button pair:

| Code | Meaning |
| --- | --- |
| `0x02` | CANCEL |
| `0x08` | SET/COAST |
| `0x10` | RESUME/ACCEL |
| `0x20` | all buttons released |
| `0x00` | invalid, fail closed |

Selection is enabled only while stock ASCD is inactive, Rolling Launch does not
own the selector host, the selector state is structurally valid, and visual
feedback is idle.

The user gesture is:

```text
released -> SET                    arm, count = 0
SET -> CANCEL -> SET               add one completed pulse
SET -> released                    commit the counted slot
```

One through five completed CANCEL pulses select Maps 1 through 5. SET remains
held while CANCEL is tapped. A release before the first completed pulse does
not commit a map.

The selector resets its transient state and retains the validated active map
for any of these conditions:

- ASCD becomes active;
- RESUME, zero, or another unexpected code appears while armed;
- a transition does not match the current phase;
- the count exceeds the slot count;
- the gesture reaches its timeout;
- selector or feedback state is corrupt.

An invalid active index resolves to Map 1. The timeout is defined by the
reference model and exact assembly payload, not by a user-editable table.

## Atomic publication

Map publication is a prepare-and-commit transaction:

1. Validate the requested index.
2. Copy the requested fuel-cut and throttle limiter clusters into temporary
   registers or the inactive preparation area.
3. Enter the interrupt-masked commit section.
4. Publish both limiter shadows, the selected throttle scalar, and the active
   index as one indivisible operation.
5. Restore the processor status register.
6. Queue visual feedback only after the commit succeeds.

The dedicated RAM reservation is:

| Range | Purpose |
| --- | --- |
| `0xFFFF5D00..0xFFFF5D07` | active index, selector state, and feedback state |
| `0xFFFF5D10..0xFFFF5D1B` | fuel-cut limiter shadow |
| `0xFFFF5D20..0xFFFF5D3B` | throttle limiter shadow and selected scalar |

Startup calls the displaced stock initializer first, initializes Map 1 limiter
shadows, and leaves the selector idle. The stock fallback clear boundary remains
unchanged.

The selected `0x942C` word is present both inside the complete throttle-cluster
shadow and at `0xFFFF1796`, the dynamic-threshold state consumed by
`FUN_0007584E`. The existing scalar hook at `0x77BAC` also exposes the selected
word to `FUN_00077892`, which calculates a transmission-derived signed request.
Exact whole-program tracing establishes that its downstream selector
`FFFF41A6.bit3` is cleared before common request publication throughout the
recovered stock lifecycle. The secondary calculation therefore cannot affect
the shared request unless external diagnostics or another patch mutate the
transition state. Controlled `0x942C` A/B profiles rely on this explicit state
boundary.

## VQ37 projected variant

JK78C, 1ND0A, and 1ND3B use fourteen target-specific families. The VQ37
layout retains the four DFCO rows and two ignition surfaces, provides a default
and an alternate family for both warm-idle timing and fuel compensation, and
replaces the canonical 2x2 fuel-cut table with two uint16 caps plus independent
eight-point activation and release curves. The duplicated pairs are read with
one index byte through one interpolator and carry no engine-bank identity, so
each family is named by the selector arm that reaches it. The throttle limiter remains one selected
uint16 scalar. The source exhaust-CVTC 16x16 surface is not projected because
the target uses a different branch-selected curve model whose exact editor
binding is not established.

The common projected RAM allocation is:

| Range | Purpose |
| --- | --- |
| `0xFFFF0C00..0xFFFF0C07` | active index, selector state, and feedback state |
| `0xFFFF0C10..0xFFFF0C13` | activation and release fuel-cut caps |
| `0xFFFF0C14..0xFFFF0C33` | activation and release fuel-cut curves |
| `0xFFFF0C38..0xFFFF0C39` | selected throttle scalar |

The limiter commit uses two-byte transfers because the 1ND stock containers
are only word-aligned. Target-specific literal hooks redirect the complete
stock 190-byte fuel-cut state machine to these shadows. JK78C binds one cap
pair and one adjacent curve pair; 1ND binds the activation and release curve
pointers independently. Exact stock coordinator, predicate, calibration, and
RAM bindings are recorded in `../defs/vq37-native-fuel-cut.toml`.

## Visual feedback

The feedback wrapper calls the stock CAN serializer first. While a valid pulse
sequence is active, it replaces the complete three-bit ASCD state in bits 4..6
of byte 5 in CAN frame `0x551`:

| Phase | State | Masked value | Exact-target result |
| --- | ---: | --- | --- |
| ON | `6` | `0x60` | CRUISE and SET illuminate; rejected for CRUISE-only feedback |
| OFF | `0` | `0x00` | both indicators off |

All bits outside this field remain the stock serializer result. The full-field
mask prevents stock bit 4 from altering the injected state, but it does not make
state 6 CRUISE-only on the target meter. The pulse count is the selected
one-based map number. Selector input is blocked until the queue is empty.
Invalid feedback state clears the queue and preserves the stock frame. A
zero/zero phase-count configuration disables feedback; a partially zero
configuration is invalid.

Firmware `1.9` introduced the full-field isolation fix by changing the engine
immediate at ROM offset `0xD37A1` from `0x9F` to `0x8F`. Firmware `1.11`
retains the exact `0x8F` byte, and its capture shows map pulses as `0x62`, not
`0x72`. The fix therefore closes accidental inheritance of state bit 4. It does
not establish the lamp semantics of the explicitly selected state 6.

The current layout default is 30 ON invocations and 30 OFF invocations. The
serializer runs every `Tcan = 10.24 ms`, while frame `0x551` is transmitted
every `10*Tcan = 102.4 ms`. Each phase therefore lasts about 307 ms and exposes
about three transmitted frames, not 30 CAN frames. In the combined runtime, a
Rolling Launch dashboard arbiter runs after this wrapper only when the pre-call
feedback state is idle. A queued map pulse has strict priority over Rolling
Launch indication for the complete serialized frame.

The stock ASCD state machine makes internal state 5 the leading CRUISE-only
candidate: DID `0x130E` reports CRUISE on and SET off in that state, while
state 4 sets the SET source and state 6 toggles it. The pointer-mediated
transfer into serializer source `0xFFFF40D0` is not statically resolved, so CAN
state 5 (`0x50`) remains unverified. Hardware correlation is deferred while
target-vehicle diagnostics are unavailable. Work resumes with a passive stock
CRUISE MAIN `OFF -> ON -> OFF` capture on the current firmware. No executable
feedback value changes before that correlation.

## Active calibration evidence

The firmware `1.11` moving capture is bound to its exact image and trace hashes
in `hardware-results.toml`. The input stream contains a two-pulse selector
gesture committed at trace offset `112.3953 s`, followed by exactly two
post-commit feedback pulses. A three-pulse gesture committed at `178.1622 s`
is followed by exactly three post-commit feedback pulses. The engine remains
at stationary idle across each commit without a fuel-inhibit transition or an
abrupt timing-coordinate discontinuity. This is consistent with the atomic
publication contract.

The same trace supplies a causal calibration check. Under warm lift-off below
`5000 RPM`, the initial stock-family segment contains 957 full `0x3F` fuel
inhibit samples among 1,534 selected samples. Map 2 contains zero among 2,132,
and Map 3 contains zero among 6,098. The six calculated injection words remain
nonzero in the selected-map intervals. Map 1, Map 4, and Map 5 have identical
bytes for every switched family in this exact image, so the initial segment is
a stock-family fingerprint rather than a unique in-band slot identifier.

Only six of the twelve switched families differ between Maps 2 and 3 in this
local image: all four warm DFCO threshold families, the `0x12196` timing-state
family, and the column-0 release cell of main fuel cut `0x0934E`. High-octane
timing state, high-detonation timing state, `0x1219E` warm transition timing,
exhaust CVTC target, the main fuel-compensation surface, and the
request-limiter scalar are
byte-identical between the two slots. They cannot explain an A/B difference in
this capture. Exact per-image calibration values remain local and unversioned.

Map 2 and Map 3 have the same fuel, high-octane timing state,
high-detonation timing state, idle-timing, and request-limiter content relevant
to the matched lift-off window. Their slot-specific `0x12196` content differs.
At `4000..4400 RPM`, matched warm
lift-off samples have the same median calculated injection value and nearly
identical BFS, while the median final timing coordinate changes from 14 on
Map 2 to -2 on Map 3. The exact 16-count output difference matches the
per-slot calibration difference. Exact selector analysis identifies `0x12196`
as the default/post-transition source and `0x1219E` as the warm transition
source while its 85-count timer is nonzero. This establishes that the
`0x12196` family is operational during warm deceleration and that its centered
result reaches the final software timing coordinate. The catalog-derived
`Cold Idle` label is retained only as provenance, not as the presentation name
or an exclusive physical qualifier. A crank-referenced degree scale remains
unverified.

The moving capture is also sufficient to isolate `0x12818` within the changed
restore pair. Every selected sample is in the stock speed-count-4-or-above
classifier, where exact code ignores upper/intermediate table `0x1298C` and
compares RPM only with the effective lower/full-restore threshold. Entry and
Hold changes are therefore unnecessary for the observed DFCO suppression.

This capture does not distinguish Map 2 from Map 3 through DFCO below
`5000 RPM`, because both calibrations intentionally suppress the state in that
region. It also does not reach the per-slot main fuel-limiter boundary. Those
specific slot differences remain unexercised.

## Diagnostic mirror

The selector mirrors default versus non-default map state into bit 7 of
`0xFFFF2A84`. Raw DID `0x130E` exposes that byte for engineering observation.
The bit is custom instrumentation and has no factory CONSULT status meaning.
It is not required for normal selection or feedback.

## ROM composition

`build_rom.py` is the production entry point. It composes the current
Map Switching, Rolling Launch, and CAN telemetry runtimes, applies a local
calibration profile, recalculates checksums, and verifies a closed write set.
`apply_map_switching.py` is an isolated diagnostic stage and is not the
production image workflow.

The pure composition modules intentionally do not create flashable files. They
bind exact input identity, anchors, hooks, layouts, assembly payload digests,
and allowed write ranges. The production checksum dependency order is:

```text
self-test B -> self-test A -> SUM16 A -> SUM16 B
```

The builder preserves all calibration outside declared component ranges. See
`rom-builder.md` for the complete image and output contract.

The layout's broad `claimed_rom` range is a legacy compatibility envelope. It
contains unused gaps and addresses assigned to later composition layers, so it
is not exclusive ownership. Exact active writes come from
`map_switching_compose.py`. The cross-runtime ledger reserves
`0x000D6800..0x000D7000` and `0xFFFF6000..0xFFFF6100` exclusively for future
Map Switching revisions. See `runtime-reservations.md`.

## Implementation inventory

| Artifact | Responsibility |
| --- | --- |
| `map-switching-layout.toml` | authoritative allocation, hooks, families, and defaults |
| `map-switching-payloads.toml` | exact assembled payloads |
| `map_switching_layout.py` | structural validation |
| `map_switching_selector.py` | independent state and transaction model |
| `map_switching_assembly.py` | payload validation and source-byte binding |
| `map_switching_compose.py` | pure in-memory composition |
| `apply_map_switching.py` | isolated diagnostic application |
| `build_rom.py` | production composition and checksum closure |
| `../tools/ghidra/EmulateMapSwitching.java` | exact SH-2E p-code execution |
| `../tools/sh-elf-run/verify_map_switching.py` | independent GNU SH executable gate |
| `../tools/mapkit/` | RomRaider, XDF, and ledger projections |
| `hardware-results.toml` | immutable hardware-result registry |

Generated XML, XDF, and ledger files are projections of the live JK08A
annotation set and layout. They are not independent sources of semantics.

## Verification gates

A composition is software-valid only when all applicable checks pass:

1. Exact JK08A size, identity bytes, and input checksums match.
2. Stock anchors and protected-code bytes match their declared values.
3. Exact active ROM writes, active RAM, and shared future reserves are
   disjoint from every other owner.
4. Assembly sources reproduce the exact payload bytes in the manifests.
5. Every hook and pointer table has either the complete stock form or the exact
   current form; mixed states are rejected.
6. Every output difference is inside the closed component and checksum write
   sets.
7. The Python reference model covers valid transitions, abort paths, corrupt
   state, slot boundaries, atomic publication, and feedback behavior.
8. Ghidra executes the exact injected bytes and all relevant branches and delay
   slots.
9. The GNU SH runner independently executes the changed entries and validates
   their observable effects.
10. Definition generation and validation agree with the layout and source CSV.
11. `build_rom.py --verify-only` accepts the exact candidate input and profile.

Software verification does not authorize flashing. Hardware validation must
confirm the raw ASCD gesture, all five selections, limiter isolation, map-family
behavior, feedback timing, diagnostic observability where used, and normal
stock operation. Final semantic claims require CONSULT3P or bench evidence and
engine validation.
