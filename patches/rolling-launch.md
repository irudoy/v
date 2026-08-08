# JK08A Rolling Launch

Rolling Launch is an optional JK08A runtime layered on the complete five-slot
map-switching composition. It captures engine speed while CANCEL is held,
installs a temporary map-specific fuel-cut window, and can apply bounded
retard-only ignition control.

The authoritative implementation sources are:

- `rolling-launch-layout.toml` for ROM/RAM ownership, hooks, and diagnostics;
- `rolling-launch-payloads.toml` for exact assembled payload bytes;
- `rolling_launch.py` for the independent state and calibration model;
- `hardware-results.toml` for immutable image identities and hardware outcomes.

The current candidate is software-verified and hardware-untested. Earlier
overlay results do not qualify the current runtime. Concrete profiles, derived
images, and active tune identities remain local and unversioned.

## Functional model

The runtime has three phases:

```text
IDLE -> ACTIVE -> COOLDOWN -> IDLE
```

`IDLE` evaluates activation gates. `ACTIVE` owns the temporary limiter overlay
and optional ignition command. Any abort restores the selected map limiter and
enters `COOLDOWN`. `COOLDOWN` requires the released button code `0x20` for the
configured rearm period before returning to `IDLE`.

Button codes follow the target vehicle's debounced ASCD representation:

| Code | Meaning |
| --- | --- |
| `0x02` | CANCEL, activation request |
| `0x08` | SET, map-selection request |
| `0x20` | all buttons released |
| `0x00` | invalid, fail closed |

The runtime never treats zero as a release. Invalid phase, snapshot, timer, or
configuration state restores Map 1 through the limiter commit path, clears the
runtime state, and enters a safe cooldown.

## Activation gates

Activation requires every gate to pass in this order:

1. The 32-byte configuration record is structurally valid.
2. The active map index is within Maps 1 through 5.
3. Rolling Launch is enabled for the active map.
4. Selector phase, count, and elapsed time are idle.
5. Visual-feedback pulse, phase, tick, and reserved fields are idle.
6. Stock ASCD is inactive.
7. The stable button is CANCEL.
8. Vehicle speed meets the configured minimum; zero disables this gate.
9. Engine speed meets the configured minimum.
10. Pedal position meets the configured minimum; zero disables this gate.
11. Coolant temperature is inside the configured range.
12. Run and rearm timers are valid.

The first failed gate is recorded as the abort reason. Map or mode changes while
active abort the run. Timeout, CANCEL release, an invalid button, or SET also
abort. SET records a map-request abort so map selection can begin after rearm.

While Rolling Launch is `ACTIVE` or `COOLDOWN`, the selector arbiter bypasses
the custom map selector and calls the displaced stock ASCD host. This prevents
both runtimes from modifying shared state during one gesture.

## Modes

| Mode | Fuel limiter | Ignition |
| --- | --- | --- |
| `observe` | unchanged | unchanged |
| `rpm_hold` | temporary captured-RPM window | unchanged |
| `rpm_hold_retard` | temporary captured-RPM window | bounded retard-only command |

On activation, the runtime captures native RPM and derives:

```text
cut = captured + offset
proportional_hysteresis = round(captured * hysteresis_ratio / 100)
hysteresis = clamp(
    proportional_hysteresis,
    minimum_hysteresis,
    maximum_hysteresis,
)
restore = cut - hysteresis
```

The native RPM unit is 12.5 RPM. The runtime writes the first eight bytes of the
shared fuel-cut shadow under an interrupt mask and leaves the rest of the
selected map limiter cluster intact. Abort restores the full selected map
shadow through the map-switching limiter commit. A corrupt state uses Map 1 as
the fail-closed source.

## Bounded ignition control

`rpm_hold_retard` computes a band below the temporary cut point:

```text
effective_retard_ramp = min(
    offset,
    max(minimum_retard_ramp, 2 * hysteresis),
)
band_start = max(captured, cut - effective_retard_ramp)
```

At or below `band_start`, the stock ignition command is preserved. Between
`band_start` and `cut`, the controller interpolates from the stock command to
the configured target. At or above `cut`, it requests the target.

The target command must be in the accepted native range `110..117`. The
controller never advances timing: if the stock command already represents
equal or later timing, the stock value is retained. Bit 6 of `0xFFFF24C9`
selects a crank/cam diagnostic fallback path and forces the stock command.
Observe and `rpm_hold` modes always preserve the stock command.

Physical ignition behavior must be correlated with an external timing
reference before retard mode is enabled on an engine. A diagnostic command
trace alone does not prove spark timing at the cylinder.

## Configuration

The strict 32-byte record contains:

| Field | Contract |
| --- | --- |
| magic, inverse, end marker | fixed integrity sentinels |
| schema | version 3 |
| mode | observe, RPM hold, or RPM hold plus retard |
| enable mask | one bit per map, unused bits clear |
| options | zero |
| coolant minimum/maximum | ordered byte range |
| minimum speed | byte; zero disables the gate |
| minimum RPM | nonzero native value |
| minimum pedal | native value; zero disables the gate |
| RPM offset | nonzero native value |
| minimum hysteresis | positive native value |
| maximum hysteresis | at least the minimum and below the RPM offset |
| hysteresis ratio | positive percentage stored in tenths of one percent |
| minimum retard ramp | positive and no larger than the RPM offset |
| run timeout and rearm | positive bounded tick counts |
| target commands | one validated byte for each map |

The built-in production profile is `rpm-hold-map1-test`: Map 1 enabled,
`rpm_hold` mode, and ignition retard disabled. A strict local TOML profile is
required for other calibration. Every field is mandatory, unknown fields are
rejected, and enabled maps use one-based numbers. See `rom-builder.md` for the
profile schema and build invocation.

RomRaider and XDF expose independent Rolling Launch calibration tables where a
safe representation exists. Raw aggregate records remain implementation data,
not a tuning interface. Generated definitions are projections of the live
JK08A source annotations and layouts.

## Allocation and hooks

| Region or address | Purpose |
| --- | --- |
| `0x000D3860..0x000D38E3` | periodic, selector-arbiter, and startup wrappers |
| `0x000D38E4..0x000D3E9F` | state engine and limiter helpers |
| `0x000D3EA0..0x000D3F5F` | ignition adapter |
| `0x000D3F60..0x000D3F7F` | configuration record |
| `0x000D40C0..0x000D413F` | bounded ignition controller |
| `0x000D4140..0x000D41DF` | adaptive threshold helper |
| `0xFFFF5D40..0xFFFF5D53` | runtime state |

The composition replaces four declared call targets:

- periodic scheduler index 0 at `0x00021970`;
- map-selector host at `0x000CE8DC`;
- startup state initialization at `0x00027D28`;
- primary ignition-command consumer at `0x0004E198`.

Every wrapper calls its displaced stock function where required. Allocation and
hook bytes are authoritative only in `rolling-launch-layout.toml`.

## State and diagnostics

The 20-byte state records phase, abort reason, flags, map/mode snapshots, run
and rearm timers, captured RPM, cut RPM, restore RPM, the observed stock and
effective ignition commands, and the captured retard-band start.

Raw engineering DIDs expose nine two-byte views:

| DID | View |
| --- | --- |
| `0x1211` | phase and abort reason |
| `0x1212` | flags |
| `0x1213` | map and mode snapshot |
| `0x1216` | run ticks |
| `0x1217` | rearm ticks |
| `0x1224` | captured RPM |
| `0x1227` | cut RPM |
| `0x1228` | restore RPM |
| `0x1229` | stock effective ignition command |

These DIDs are custom instrumentation, not factory CONSULT parameters. They are
useful only when the diagnostic client can request the raw identifiers and are
not a prerequisite for runtime correctness.

## Composition

`build_rom.py` is the production entry point. It starts from an exact compatible
JK08A base or a complete migratable runtime, installs the current map-switching
composition, applies Rolling Launch with the selected profile, recalculates all
checksum domains, and verifies the final closed write set.

`apply_rolling_launch.py` is an isolated diagnostic stage. The composition and
assembly modules operate in memory and do not expose a flashable output path.
They require the exact base composition and bind every byte to the declared
layout and payload manifests.

The implementation inventory is:

| Artifact | Responsibility |
| --- | --- |
| `rolling-launch-layout.toml` | allocation, hooks, diagnostics, and defaults |
| `rolling-launch-payloads.toml` | exact assembled payloads |
| `rolling_launch.py` | independent fail-closed model |
| `rolling_launch_layout.py` | structural validation |
| `rolling_launch_assembly.py` | payload and source-byte validation |
| `rolling_launch_compose.py` | pure in-memory composition |
| `apply_rolling_launch.py` | isolated diagnostic application |
| `build_rom.py` | production composition and checksum closure |
| `../tools/ghidra/EmulateRollingLaunch.java` | exact p-code execution |
| `../tools/sh-elf-run/verify_rolling_launch.py` | independent GNU SH gate |
| `hardware-results.toml` | immutable hardware-result registry |

## Verification gates

A candidate is software-valid only when all applicable checks pass:

1. The exact JK08A base and complete current map-switching composition match.
2. ROM/RAM ownership, stock anchors, hooks, diagnostic pointers, and payload
   digests match their manifests.
3. Assembly sources reproduce the exact injected bytes.
4. The independent model covers every gate, phase transition, abort reason,
   corrupt-state recovery, map isolation, rearm boundary, limiter action, and
   ignition boundary.
5. Ghidra executes the exact bytes across all changed entries, branches, delay
   slots, call/return paths, and boundary cases.
6. The GNU SH fixture independently executes the same current payload bytes.
7. Every final difference is inside the combined component and checksum write
   sets.
8. The generated definition tables agree with the configuration contract.
9. `build_rom.py --verify-only` accepts the exact candidate input and profile.

Software verification does not authorize flashing. The first hardware gate is
a stationary, controlled `rpm_hold` test with retard disabled. It must confirm
activation, captured and cut RPM behavior, timeout, release, cooldown, rearm,
map isolation, normal ASCD behavior, and subsequent map selection. Retard mode
requires a separate controlled test after physical timing correlation and must
remain within the verified interpolation band.
