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

The current endpoint is software-verified and requires controlled hardware
validation before flashing. The current visual-feedback timing is 30 serializer
invocations ON followed by 30 invocations OFF for each pulse. Hardware status is
read only from `hardware-results.toml`; successful results from earlier
compositions do not qualify the current endpoint.

The runtime switches these families:

| Family | Access path |
| --- | --- |
| DFCO hold | lookup adapter |
| DFCO cut | lookup adapter |
| DFCO full restore | lookup adapter |
| DFCO intermediate restore | lookup adapter |
| main ignition trim | lookup adapter |
| high-detonation ignition trim | lookup adapter |
| cold-idle ignition timing | lookup adapter |
| idle ignition timing | lookup adapter |
| fuel targets | lookup adapter |
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

## Visual feedback

The feedback wrapper calls the stock CAN serializer first. While a valid pulse
sequence is active, it replaces the complete three-bit ASCD state in bits 4..6
of byte 5 in CAN frame `0x551`:

| State | Masked value |
| --- | --- |
| CRUISE on, SET off | `6` (`0x60`) |
| CRUISE off, SET off | `0` (`0x00`) |

All bits outside this field remain the stock serializer result. Replacing all
three state bits prevents the serializer's low ASCD bit from adding SET during
an active CRUISE-only pulse. The pulse count is the selected one-based map
number. Selector input is blocked until the queue is empty. Invalid feedback
state clears the queue and preserves the stock frame. A zero/zero phase-count
configuration disables feedback; a partially zero configuration is invalid.

The current layout default is 30 ON invocations and 30 OFF invocations. Wall
time depends on the target serializer period and must be measured on hardware.
In the combined runtime, a Rolling Launch dashboard arbiter runs after this
wrapper only when the pre-call feedback state is idle. A queued map pulse has
strict priority over Rolling Launch indication for the complete serialized
frame.

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
