# Rolling Launch runtime

Rolling Launch is an optional runtime layered on the complete five-slot
Map Switching composition. It captures engine speed while CANCEL is held,
applies a target-specific all-cylinder fuel-cut actuator, and can apply bounded
retard-only ignition control. The JK00A/JK03A/JK03B/JK08A and JK00C/JK00D
variants use a temporary map-specific fuel-cut window. JK78C, 1ND0A, 1ND3B, and
1ME3B use a final-mask coordinator request without modifying the selected VQ37
maps.

The authoritative implementation sources are:

- `rolling-launch-layout.toml` for ROM/RAM ownership, hooks, and diagnostics;
- `rolling-launch-payloads.toml` for exact assembled payload bytes;
- `rolling_launch.py` for the independent state and calibration model;
- `hardware-results.toml` for immutable image identities and hardware outcomes.

The canonical JK08A candidate is software-verified and has active
target-vehicle evidence from an exact local combined image. The evidence
qualifies button decoding, dashboard states, repeated rearm, the full software
fuel-inhibit mask, captured-RPM-dependent hold behavior, and the bounded
software ignition command on Maps 2 and 3. Physical spark timing and electrical
injector output remain unmeasured. VQ37 projections have no bench or vehicle
result and remain software-only. Earlier overlay results do not qualify the
current runtime. Concrete profiles, derived images, and active tune identities
remain local and unversioned.

## Functional model

The runtime has three phases:

```text
IDLE -> ACTIVE -> COOLDOWN -> IDLE
```

`IDLE` evaluates activation gates. `ACTIVE` owns the target-specific fuel-cut
request and optional ignition command. Any abort restores or republishes the
selected map limiter and enters `COOLDOWN`. `COOLDOWN` requires the released
button code `0x20` for the configured rearm period before returning to `IDLE`.

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
6. The MAIN switch bit of the stock ASCD flag byte is clear.
7. The stable button is CANCEL.
8. Vehicle speed meets the configured minimum; zero disables this gate.
9. Engine speed meets the configured minimum.
10. Pedal position meets the configured minimum; zero disables this gate.
11. Coolant temperature is inside the configured range.
12. Run and rearm timers are valid.

The first failed gate is recorded as the abort reason. Map or mode changes while
active abort the run. Timeout, CANCEL release, an invalid button, or SET also
abort. SET records a map-request abort so map selection can begin after rearm.

On JK08A, gate 6 follows the MAIN switch itself: the MAIN switch bit is set
only while MAIN is pressed. The MAIN state that each press toggles,
`0xFFFF4251.bit1`, and `0xFFFF424E.bit1`, which selects ASCD display state 4,
are not gate inputs. The CANCEL hold is therefore made with the cruise MAIN
state off, under the rule that `map-switching-selector.md` states for the
selector gestures.

While Rolling Launch is `ACTIVE` or `COOLDOWN`, the selector arbiter bypasses
the custom map selector and calls the displaced stock ASCD host. This prevents
both runtimes from modifying shared state during one gesture.

## Scheduler timebase

On the canonical layout, `FUN_00020DFE` walks the 124-entry table at
`0x0002196C`, and the periodic hook replaces entry 1 at `0x00021970`, calls the
displaced stock task, and advances Rolling Launch once per exact
`FUN_00020DFE` pass. Target profiles bind the homologous table and
task explicitly. The timer configuration proves a period of `204800/Pphi`
seconds. Passive
target-CAN timestamps independently establish `Pphi = 20 MHz`, so one runtime
tick is `10.24 ms` on JK08A.

The default configuration therefore gives these exact target durations:

| Field | Ticks | Duration |
| --- | ---: | ---: |
| run timeout | 300 | 3.072 s |
| rearm | 100 | 1.024 s |

The time conversion is a measured target property. It does not by itself
establish the physical spark or injector-output behavior.

## Dashboard indication

The dashboard arbiter calls the complete map-feedback wrapper first. A nonzero
map-feedback state owns that serialized frame, including the final OFF phase;
Rolling Launch does not replace an active map-selection pulse. When map
feedback was idle before the call, Rolling Launch replaces the complete
three-bit ASCD field in bits 4..6 of byte 5 in CAN frame `0x551`:

| Runtime state | Dashboard field |
| --- | --- |
| normal `IDLE` | preserve the stock serializer result |
| failed activation while CANCEL remains held | state 5 (`0x50`), the stock CRUISE-alone state |
| `ACTIVE` | state 4 (`0x40`), the stock CRUISE with steady SET state |
| `COOLDOWN` | state 0 (`0x00`) |
| corrupt phase | preserve the stock serializer result |

A failed attempt requires both a nonzero abort reason and the published
`BUTTON_HELD` gate flag. Releasing CANCEL removes the failure indication on the
next evaluated state. The indication is level-based and does not change the
map-feedback pulse timing.

### Passive CAN evidence

The 2026-08-16 `1.10` vehicle capture contains 233,442 standard frames over
120.053 seconds. Its exact firmware and trace hashes are registered in
`hardware-results.toml`. Frame `0x239` byte 3 contains 4,229 release samples,
282 SET samples, and 1,349 CANCEL samples. Frame `0x551` byte 5 contains 868
stock-value samples at `0x02`, 193 custom state-6 samples at `0x62`, and 111
Rolling Launch ACTIVE state-7 samples at `0x72`: firmware `1.10` emits state 6
for map feedback and for a failed held attempt, and state 7 for `ACTIVE`.
Exact-target observation of map feedback establishes that state 6 illuminates
SET together with CRUISE. The stock display-state writer `FUN_000CEABC`
assigns state 4 to CRUISE with steady SET, state 5 to CRUISE alone, and state 6
to CRUISE with a blinking SET lamp, and produces no state 7;
`../defs/JK08A.can.md` records the encoding. The current runtime emits only
states 0, 4, and 5, which appear as `0x02`, `0x42`, and `0x52`. In the
2026-09-21 road session, each of the six moving CANCEL holds of the mixed Map 3
drive shows one `0x42` ACTIVE interval, and five of the intervals carry the
full `0x3F` fuel-inhibit mask, which the drive shows nowhere else. Every
CANCEL tap of a map-selection gesture shows `0x52` for the tap.
`hardware-results.toml` records the observation under
`map_switching.feedback_vehicle_2026_09_21`. Operator observation of the map
feedback pulses establishes that state 4 lights SET together with CRUISE on the
exact target, and `ACTIVE` sends the same state as a steady level. In the
2026-09-22 road session a CANCEL hold on Map 1 shows state 5 for its whole
length and lights CRUISE alone; `hardware-results.toml` records the observation
under `map_switching.feedback_vehicle_2026_09_22`.

The full-field isolation correction from firmware `1.9` is present in this
runtime: both feedback paths clear mask `0x70` with immediate `0x8F` before
inserting a state. The state-6 result is therefore not caused by preserving the
state-7 bit.

The `0x72` samples form 11 distinct ACTIVE indication intervals. Fast ECM
frames retain a 10.2 ms median period and slow ECM frames retain a 102.3 to
102.4 ms median period both inside and outside custom indication intervals;
their maximum gaps remain below 12.2 ms and 106.2 ms respectively. This gives
no evidence of a scheduler or stock-CAN timing regression in the recorded
stationary conditions.

One repeated CANCEL press begins 0.860 seconds after the preceding release,
before the local build's configured rearm interval expires, and produces no
ACTIVE indication. Later presses produce bounded RPM oscillation around their
temporary hold regions. These observations are consistent with cooldown and
RPM-hold behavior, but CAN engine speed and dashboard state alone do not prove
fuel-cut electrical output or physical spark retard.

### Active tuning-telemetry evidence

The firmware `1.11` moving capture adds direct runtime-state evidence through
the custom telemetry endpoint. Its exact image and trace hashes are registered
in `hardware-results.toml`. Two CANCEL trials occur after a confirmed Map 2
commit and three after a confirmed Map 3 commit. All five trials enter dashboard
state 7 and produce repeated full `0x3F` fuel-inhibit cycles. The individual
cycle counts are 4 and 4 on Map 2, then 6, 4, and 5 on Map 3.

The first full-inhibit transition in each trial occurs at the expected
captured-RPM-dependent upper boundary within the 12.5 RPM telemetry
quantization and normal engine overshoot. Falling RPM clears the mask at the
lower boundary, and repeated cycles remain bounded around the same window.
After CANCEL release, the full mask clears within `6.9..81.1 ms` in all five
trials, and later trials activate again. This qualifies temporary limiter
installation, engine-level RPM hold, release, and rearm on both selected maps.

The APC command reaches the configured bounded-retard region in every trial.
When stock timing is earlier, the command moves through the interpolation band;
when stock timing is already equally late, the stock value is retained. The
normal firmware identity `final_timing = 110 - APC command` holds in 35,444 of
35,811 complete telemetry snapshots. All 367 differences occur in the Map 2 or
Map 3 Rolling Launch intervals: 342 while CANCEL is held and 25 immediately
around release. This is the expected hook ordering. `final_timing_raw` captures
the upstream stock coordinate written before the late override, while
`apc_command_raw` captures the effective command written by the adapter before
the APC scheduler. The result validates the software controller direction and
late-override placement, not physical crankshaft timing.

During full inhibit, the six calculated injection words move to the code-proven
override/fallback region rather than zero. This agrees with the static output
model and does not establish injector-terminal pulse width. A physical spark
reference and electrical injector measurement remain separate evidence gates.

### Current-runtime vehicle evidence

The mixed Map 3 drive of the 2026-09-21 road session is the moving Rolling
Launch capture of the current runtime. `hardware-results.toml` records it under
`rolling_launch.map_3_vehicle_2026_09_21`, and
`../tools/logs/rolling_launch_audit.py` derives its figures from the recording
and from the configuration record of the recorded image. The recording holds
40,298 consecutive telemetry snapshots and no TRC accompanies it, so each event
time is bounded by the 10.24 ms snapshot spacing and each dashboard state by
the 102.4 ms period of frame `0x551`. The drive contains no SET hold, and only
the Map 3 exhaust CVTC target surface reproduces all 40,297 recorded targets
from the prior snapshot, which confirms the Map 3 selection that the capture
name declares.

All six moving CANCEL holds, at 33.2 to 72.1 km/h, enter `ACTIVE` state 4, and
no record shows state 5. The replay of the configuration record bounds the
captured words of the six holds between 2212.5 and 3287.5 RPM; two of them lie
inside the 3112.5 to 3637.5 RPM activation range of the firmware `1.11`
capture. Five holds reach their cut word and cycle the full `0x3F` mask 4, 3,
3, 1, and 1 times while CANCEL is held. No full mask appears outside the
activation windows, which run from the first CANCEL record through the later
of the release and the end of the `ACTIVE` indication and over any full mask
that continues past that point. The second hold keeps APP1 between 0.75 and
0.755 V while engine speed stays between 2175 and 2225 RPM, below its 2412.5 to
2425 RPM cut word, and its stock command 117 is already later than the target
115, so neither the fuel cut nor the retard acts in that activation.

The APC command stays inside the retard-only bound
`stock <= command <= max(stock, target)`, with `stock = 110 - final_timing`, in
every snapshot of the activation windows and reaches the target 115 in the
other five holds. The normal firmware identity
`final_timing = 110 - APC command` holds in 39,961 of the 40,298 snapshots; all
337 differences fall inside the activation windows, 316 while CANCEL is held
and 21 after its release.

Holds 1 and 2 carry no full mask at the release. Holds 3 to 6 show a full mask
at or after the first released `0x239` record: hold 4 continues its cycle, and
holds 3, 5, and 6 start one more. Each of these masks clears while the compared
engine-speed word remains at or above every consistent restore word, so the
clear follows the removal of the temporary window rather than the hysteresis.
The release-to-clear distance lies within 30.7 to 51.2 ms for hold 5 and
51.2 to 71.7 ms for hold 6, inside the `6.9..81.1 ms` range of the firmware
`1.11` trace, and within 61.4 to 81.9 ms for hold 3 and 71.7 to 92.2 ms for
hold 4, which the snapshot spacing does not place on either side of 81.1 ms.
The Map 2 trace of the same image below times one such release with frame
times.

Each later hold starts at least 5.1 s after the preceding release, beyond the
1.024 s rearm period, and activates; the refusal inside that period is not
exercised. The longest hold lasts 1.27 s, and the 3.072 s run timeout is not
exercised. The figures are software quantities; spark angle at the crankshaft
and electrical injector output remain outside the measurement.

The Map 2 run of the 2026-09-22 road session is a TRC of the same image.
`hardware-results.toml` records it under
`rolling_launch.map_2_vehicle_2026_09_22`, and the audit tool derives its
figures from the trace and from the configuration record of the recorded
image. The trace holds 17,320 consecutive verified telemetry snapshots over
177.347 s, and its frame times place each `0x239` and `0x551` frame. SET
gestures commit Maps 5, 2, 1, and 2, frame `0x551` answers them with 5, 2, 1,
and 2 state-4 pulses, and no SET hold follows the last commit. A 3.196 s
CANCEL hold on Map 1, which has Rolling Launch disabled, shows 31 frames of
state 5 and no state 4. The exhaust CVTC replay excludes Map 3: its surface
holds the neutral target, 1,887 recorded targets lie above it, and Maps 1, 2,
4, and 5 share one surface.

Six CANCEL holds on Map 2 enter `ACTIVE` state 4, three while moving at 44.5
to 56.8 km/h and three at standstill. The replay of the configuration record
bounds the captured words of the moving holds at 3300, 3575, and 3275 to
3287.5 RPM, inside the 3112.5 to 3637.5 RPM activation range of the firmware
`1.11` capture, and the moving holds cycle the full `0x3F` mask 9, 10, and 10
times while CANCEL is held. The standstill holds capture 2625 to 2662.5 RPM,
and engine speed stays below their retard band, which starts at 2725 to
2762.5 RPM, so neither the fuel cut nor the retard acts in them. All 357
full-mask snapshots lie inside the activation windows, and no snapshot carries
a partial mask. The APC command stays inside the retard-only bound in every
snapshot of the activation windows and reaches the target 115 in 97, 105, and
64 snapshots of the moving holds. The identity
`final_timing = 110 - APC command` holds in 16,715 of the 17,320 snapshots,
and all 605 differences fall inside the activation windows.

The second moving hold lasts 3.504 s; its retard ends 299 to 306 ticks after
the capture pass and before the release, and its `ACTIVE` indication lasts 30
frames. The standstill holds of 5.163 and 3.894 s each show 30 `ACTIVE`
frames followed by 19 and 7 frames of state 0 while CANCEL remains held. These
runs end by the 300-tick run timeout; the session does not read the abort
reason of DID `0x1211`. Three presses that start 368.1, 287.0, and 327.7 ms
after the preceding release show neither state 4 nor state 5: `COOLDOWN`
restarts its rearm count while a button is pressed. Each hold that starts at
least 6.9 s after the preceding release activates.

Only the third moving hold carries a full mask at the release. The mask clears
86.5 to 92.7 ms after the first released `0x239` frame, above the
`6.9..81.1 ms` range of the firmware `1.11` trace. The replay places the end
of `ACTIVE` 10.2 to 61.4 ms after the released frame in the first moving hold
and 61.4 to 184.3 ms after it in the third. The runtime reads the stock
debounced button code `0xFFFF2A85`, while frame `0x239` carries the
steering-switch code `0xFFFF36D8`; the delay between the two codes is not
established. The figures are software quantities; spark angle at the
crankshaft and electrical injector output remain outside the measurement.

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

The native RPM unit is 12.5 RPM. The VQ25HR/VQ35HR variants write the first
eight bytes of the shared fuel-cut shadow under an interrupt mask and leave the
rest of the selected map limiter cluster intact. Abort restores the full
selected map shadow through the Map Switching limiter commit.

The VQ37 variant clears a dedicated uint16 request at the start of every
periodic pass. In an active non-observe mode, a latch in the state sets when
native RPM reaches `cut` and releases when native RPM falls below `restore`,
and the engine publishes exactly `0x003F` while the latch equals 1. The
latch uses the `cut` and `restore` thresholds that the VQ25HR/VQ35HR variants
write into the stock fuel-cut window. The stock native fuel-cut state machine
keeps the thresholds of the selected map, so Rolling Launch adds cut and
cannot raise the stock limit. Activation, abort, a corrupt state, and startup
clear the latch; the activation pass runs at the captured speed and publishes
no request. The scheduler entry 31 positions after the displaced periodic
task calls a wrapper that first executes the complete stock fuel-mask
coordinator. An exact request then ORs the six cylinder bits
into the coordinator result; zero and every malformed request leave the stock
mask unchanged. The wrapper preserves the stock coordinator's return value.
Activation does not modify the 36-byte native fuel-cut shadow. Abort
republishes the captured map through the common limiter commit, and a corrupt
state uses Map 1 as the fail-closed source.

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

The built-in VQ25HR/VQ35HR production profile is `rpm-hold-map1-test`: Map 1
enabled, `rpm_hold` mode, and ignition retard disabled. VQ37 uses the complete
runtime with the built-in `observe` profile and no enabled maps. A strict local
TOML profile can select any supported mode and map mask. Every field is
mandatory, unknown fields are rejected, and enabled maps use one-based numbers.
See `rom-builder.md` for the profile schema and build invocation.

RomRaider and XDF expose independent Rolling Launch calibration tables where a
safe representation exists. Raw aggregate records remain implementation data,
not a tuning interface. Generated definitions are projections of the live
JK08A source annotations and layouts.

## Allocation and hooks

Every range names an exclusive end, as `runtime-reservations.md` does.

| Region or address | Size | Purpose |
| --- | ---: | --- |
| `0x000D3860..0x000D38E4` | 132 | periodic, selector-arbiter, and startup wrappers |
| `0x000D38E4..0x000D3EA0` | 1,468 | state engine and limiter helpers |
| `0x000D3EA0..0x000D3F60` | 192 | ignition adapter |
| `0x000D3F60..0x000D3F80` | 32 | configuration record |
| `0x000D40C0..0x000D4140` | 128 | bounded ignition controller |
| `0x000D4140..0x000D41E0` | 160 | adaptive threshold helper |
| `0x000D41E0..0x000D4280` | 160 | dashboard feedback arbiter |
| `0xFFFF5D40..0xFFFF5D54` | 20 | runtime state |

The composition replaces five declared call targets:

- periodic scheduler entry 1 at `0x00021970`;
- map-selector host at `0x000CE8DC`;
- startup state initialization at `0x00027D28`;
- primary ignition-command consumer at `0x0004E198`;
- dashboard feedback call at `0x000C3FA4`.

The dashboard hook redirects the existing map-feedback wrapper call to the
Rolling Launch arbiter. The arbiter invokes that wrapper before applying its
own state. Every wrapper calls its displaced function where required.
Allocation and hook bytes are authoritative only in
`rolling-launch-layout.toml` and the applicable target section of
`rom-address-profiles.toml`. VQ37 adds a projected 128-byte fuel-coordinator
wrapper at canonical range `0x000D5000..0x000D5080` and a sixth scheduler hook
for index 31.

## State and diagnostics

The canonical 20-byte state records phase, abort reason, flags, map/mode
snapshots, run and rearm timers, captured RPM, cut RPM, restore RPM, the
observed stock and effective ignition commands, and the captured retard-band
start. VQ37 extends the record to 24 bytes with the exact fuel request and its
latch. The nine diagnostic views retain the same offsets.

The fuel-cut flag of an active state reports the active cut bit of the stock
RPM fuel-cut state of the target: bit 2 of the main RPM fuel-cut state byte
on JK00A, JK03A, JK03B, and JK08A, bit 6 on JK00C and JK00D, and the active
bit of the native rev-limit state byte on VQ37: bit 4 on JK78C, bit 5 on 1ND0A
and 1ND3B, and bit 3 on 1ME3B. The other bits of the byte leave the flag
clear. On VQ37 the Rolling Launch request reaches the final six-cylinder mask
through the coordinator wrapper and leaves the state byte unchanged, so the
flag reports only the stock rev-limit cut.

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
registered base or a complete migratable runtime, installs the current Map
Switching composition, applies the target-specific Rolling Launch stage with
the selected profile, adds the CAN telemetry layer, recalculates all checksum
domains, and verifies the final closed write set.

The composition and assembly modules require the exact base composition and
bind every byte to the declared layout and payload manifests.

The canonical runtime uses `0xFFFF5D40..0xFFFF5D54` for active state. VQ37
uses the projected `0xFFFF0C40..0xFFFF0C58` range. The cross-runtime ledger
assigns `0x000D6000..0x000D6800` and
`0xFFFF6100..0xFFFF6200` exclusively to future Rolling Launch revisions. These
reserves are erased and outside every exact current write set. See
`runtime-reservations.md`.

The implementation inventory is:

| Artifact | Responsibility |
| --- | --- |
| `rolling-launch-layout.toml` | allocation, hooks, diagnostics, and defaults |
| `rolling-launch-payloads.toml` | exact assembled payloads |
| `rolling-launch-feedback.s` | dashboard feedback arbitration |
| `rolling_launch.py` | independent fail-closed model |
| `rolling_launch_layout.py` | structural validation |
| `rolling_launch_assembly.py` | payload and source-byte validation |
| `rolling_launch_compose.py` | pure in-memory composition |
| `apply_rolling_launch.py` | isolated diagnostic application |
| `build_rom.py` | production composition and checksum closure |
| `../tools/sh-elf-run/verify_rolling_launch.py` | independent GNU SH gate |
| `hardware-results.toml` | immutable hardware-result registry |

## Verification gates

A candidate is software-valid only when all applicable checks pass:

1. The exact selected stock base and complete current Map Switching composition
   match the registered target profile.
2. ROM/RAM ownership, stock anchors, hooks, diagnostic pointers, and payload
   digests match their manifests.
3. Assembly sources reproduce the exact injected bytes.
4. The independent model covers every gate, phase transition, abort reason,
   corrupt-state recovery, map isolation, rearm boundary, limiter action, and
   ignition boundary.
5. The GNU SH fixture independently executes the same current payload bytes
   across all changed entries, branches, delay slots, call/return paths, and
   boundary cases.
6. Every final difference is inside the combined component and checksum write
   sets.
7. The generated definition tables agree with the configuration contract.
8. `build_rom.py --verify-only` accepts the exact candidate input and profile.

Software verification and the recorded JK08A target-vehicle result do not
authorize another flash. That image qualifies repeated activation, RPM hold,
release, rearm, and bounded software-command behavior on Maps 2 and 3. VQ37
runtime behavior, timeout, corrupt-state recovery, map changes while active,
and the exact physical spark and injector outputs remain software-only or
unmeasured boundaries. A physical timing claim requires a crank-referenced
measurement, and an injector-pulse claim requires an electrical measurement at
the output path.
