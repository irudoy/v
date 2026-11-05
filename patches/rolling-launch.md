# Rolling Launch runtime

Rolling Launch is an optional runtime layered on the complete five-slot
Map Switching composition. While CANCEL is held it limits engine torque with
the ignition alone: in hold mode it withholds the dwell of a fraction `q` of
the eligible ignition events through a wrapper of the dwell-arming divider
and retards the fired events by a fixed trim of the active map. The vehicle
speed at activation selects one of two regulators against the speed threshold
of the active map. Below the threshold an RPM regulator cuts engine speed at
the launch engine speed of the map; at or above it a SPEED regulator holds the
vehicle speed captured when CANCEL is pressed. The runtime writes no fuel-cut
request: the stock fuel-output inhibit coordinator, the stock fuel-cut
conditions, and the stock engine-speed limiter of the image act unchanged. It
runs on the exact `7mfk` images JK00A, JK03A, JK03B, and JK08A. The relocated
targets JK00C, JK00D, JK78C, 1ND0A, 1ND3B, and 1ME3B carry no Rolling Launch
runtime.

The authoritative implementation sources are:

- `rolling-launch-layout.toml` for ROM/RAM ownership, hooks, and diagnostics;
- `rolling-launch-payloads.toml` for exact assembled payload bytes;
- `rolling_launch.py` for the independent state, calibration, and controller
  model;
- `hardware-results.toml` for immutable image identities and hardware outcomes.

The current runtime is configuration schema 6. Its layout declares no hold
actuator (`hold_actuator = false`) until the veto delivery of the spark-cut
actuator, open in issue #150, has executable qualification; `make preflash`
refuses an image that enables a map in hold mode while that field is false.
No schema 6 image has vehicle evidence.

The target-vehicle evidence below comes from exact local images of registered
historical endpoints, whose units, records, and fuel paths
`runtime_endpoints.py` binds by their own addresses. The endpoint
`schema-3-fuel-shadow-hold` held RPM through the fuel-cut shadow of the
selected map; its sessions qualify button decoding, dashboard states, repeated
rearm, and the full software fuel-inhibit mask. The endpoint
`schema-4-uniform-gain` held vehicle speed with the spark cut, an RPM ceiling,
and a fuel-cut wrapper; its session under "Vehicle evidence of the hold"
establishes the combustion loss of vetoed events. These results belong to
their endpoints and do not qualify the schema 6 regulators. Physical spark
timing and electrical injector output remain unmeasured. Concrete profiles,
derived images, and active tune identities remain local and unversioned.

## Functional model

The runtime has three phases:

```text
IDLE -> ACTIVE -> COOLDOWN -> IDLE
```

`IDLE` evaluates activation gates and captures the vehicle speed on the
accepted CANCEL edge. Activation captures the selected map, the configured
mode, and native RPM, selects the regulator kind, and latches the target and
the trim of that kind for the map. `ACTIVE` runs the regulator on every tick
that passes its gates. Any abort publishes `q = 0` and enters `COOLDOWN`.
`COOLDOWN` keeps the regulator kind and the trim and requires the released
button code `0x20` for the configured rearm period before returning to
`IDLE`, which clears both.

Button codes follow the target vehicle's debounced ASCD representation:

| Code | Meaning |
| --- | --- |
| `0x02` | CANCEL, activation request |
| `0x08` | SET, map-selection request |
| `0x20` | all buttons released |
| `0x00` | invalid, fail closed |

The runtime never treats zero as a release. Invalid phase, snapshot, timer,
regulator, actuation, or configuration state restores Map 1 through the
limiter commit path, clears the engine part of the state record and the state
extension, and enters a safe cooldown. The spark-cut counters and accumulators
keep their own reset.

## Activation gates

Activation requires every gate to pass in this order:

1. The 102-byte configuration record, its five map slots, and the efficiency
   table are structurally valid.
2. The active map index is within Maps 1 through 5.
3. Rolling Launch is enabled for the active map.
4. Selector phase, count, and elapsed time are idle.
5. Visual-feedback pulse, phase, tick, and reserved fields are idle.
6. The MAIN switch bit of the stock ASCD flag byte is clear.
7. The stable button is CANCEL.
8. The vehicle-speed source is ready: `0xFFFF4195` bit 0 and `0xFFFF4185`
   bit 7 are set.
9. The raw vehicle-speed word is not the invalid wire value `0xFFFF`.
10. The receive age of the vehicle-speed frame is within the configured limit.
11. The speed captured on the CANCEL edge is valid.
12. For the SPEED regulator, vehicle speed lies inside the configured
    activation range; a zero bound disables its side of the range. The RPM
    regulator applies no speed range.
13. Engine speed is a native value of at most 32767.
14. Engine speed meets the configured minimum.
15. Pedal position meets the configured minimum; zero disables this gate.
16. Coolant temperature is inside the configured range.
17. Run and rearm timers are valid.

The first failed gate is recorded as the abort reason. A SPEED activation is
also refused while the speed error of the target already lies outside the
abort window. `ACTIVE` evaluates the same gates on every tick, except that
gate 12 of the SPEED regulator becomes the speed-error window: the vehicle
speed minus the target must stay within the configured distances above and
below the target. Map or mode changes while active abort the run before any
gate reason. Timeout, CANCEL release, an invalid button, a speed input that is
not ready, invalid, or stale, a speed outside the window, or SET also abort
either regulator. SET records a map-request abort so map selection can begin
after rearm, and a release records `BUTTON_RELEASED` in place of the gate
reason that it causes.

Vehicle speed is the word `0xFFFF113C` in km/h*10, which the stock receive
handler of CAN frame `0x284` publishes (`../defs/JK08A.can.md`). Gate 10 reads
the stock receive age `0xFFFF3B38` of that record. `FUN_000C3994` advances the
age on every pass of the pending-task table `0x00021834`, which runs every
10.24 ms like the Rolling Launch tick, and a pass that processes a new frame
clears it; it saturates at 255. Frame `0x284` arrives every 20 ms, so the age
stays at 0 to 2. One count is 10.24 ms, and the default limit of 10 tolerates
102.4 ms without a frame. A lost speed frame therefore refuses activation and
aborts a run with `SPEED_FRAME_STALE`.

The age stays at zero while `0xFFFF4185` bit 7 is clear and advances only
while `0xFFFF4195` bit 0 is set, so gate 8 requires both bits before the age
counts. The decoded speed word carries no validity flag: the stock decoder
stores zero for the invalid wire word `0xFFFF`. Gate 9 therefore reads the raw
word through its two unaligned bytes `0xFFFF3B3D` and `0xFFFF3B3E`; a raw zero
with a ready source and an admissible age is a valid standstill. The vehicle
check that this age follows frame `0x284` alongside the speed word is open
(issue #103).

In `IDLE`, the edge of the stable button code `0xFFFF2A85` from another code to
CANCEL stores the current vehicle speed as the CANCEL capture when the
configuration is valid and gates 8 to 10 pass; otherwise the capture is
invalid until the next press. The capture is that of the stable code, not of
the raw frame `0x239`, and any code other than CANCEL clears it. A press in
`COOLDOWN` does not capture, so a capture never bypasses the rearm period.

On JK08A, gate 6 follows the MAIN switch itself: the MAIN switch bit is set
only while MAIN is pressed. The MAIN state that each press toggles,
`0xFFFF4251.bit1`, and `0xFFFF424E.bit1`, which selects ASCD display state 4,
are not gate inputs. The CANCEL hold is therefore made with the cruise MAIN
state off, under the rule that `map-switching-selector.md` states for the
selector gestures.

Gate 7 needs the CANCEL code of the steering switch decoder, which exists only
while bit 0 of the cruise control configuration byte is set. JK00A, JK03A,
and JK03B hold `0x00` there, so Rolling Launch never arms on them until the
Cruise Control Switch of their definitions selects ICC Switch (5 Buttons)
(`cruise-control-switch.md`).

While Rolling Launch is `ACTIVE` or `COOLDOWN`, the selector arbiter bypasses
the custom map selector and calls the displaced stock ASCD host. This prevents
both runtimes from modifying shared state during one gesture.

## Regulator selection

Activation compares the vehicle speed with `launch_speed_threshold` of the
active map: a lower speed selects the RPM regulator, an equal or higher speed
the SPEED regulator. The kind holds for the whole run; crossing the threshold
while `ACTIVE` neither changes it nor ends the run. Transmission and brake
states are not inputs.

| Kind | Target | Trim | Law output |
| --- | --- | --- | --- |
| RPM | `launch_rpm_native` of the map | `max_trim_rpm` of the map | firing fraction `p` |
| SPEED | `clamp(capture + target_speed_offset, 0, 0xFFFF)` | `max_trim_speed` of the map | torque fraction `u` |

The SPEED target takes the CANCEL capture even when the gates admit the
activation on a later tick, so the offset applies once to the speed of the
press. The captured RPM remains a diagnostic value of both kinds. The trim of
the selected kind is copied into the state at activation, and the run uses
that copy.

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
| run timeout | 781 | 7.997 s |
| rearm | 98 | 1.004 s |

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

### Historical-endpoint vehicle evidence

The mixed Map 3 drive of the 2026-09-21 road session is the moving Rolling
Launch capture of the historical endpoint `schema-3-fuel-shadow-hold`.
`hardware-results.toml` records it under
`rolling_launch.map_3_vehicle_2026_09_21`, and its figures come from the
recording and from the configuration record of the recorded image. The recording holds
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
`rolling_launch.map_2_vehicle_2026_09_22`, and its figures come from the
trace and from the configuration record of the recorded image. The trace holds 17,320 consecutive verified telemetry snapshots over
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

### Vehicle evidence of the hold

`hardware-results.toml` records the 2026-11-03 session of the v2 hold image,
the historical endpoint `schema-4-uniform-gain`,
on Map 3 under `rolling_launch.v2_hold_vehicle_2026_11_03`: stationary holds
in neutral and moving holds in second and third gear, each capture with a
dashboard recording and a TRC. Every hold passes the hold audit: the published
torque fraction follows the model, the cut counter lies inside the cuts that
the fractions owe, no fuel mask appears outside `ACTIVE`, and no new cut
request follows the first inactive snapshot. The cut counter counts requested
cuts, not withheld sparks. A veto carried to the next cylinder can still
withhold one event after the exit. At
standstill the fraction settles at the proportional value of a zero error,
the all-cylinder fuel cut latches near the ceiling and releases at the
hysteresis, and engine speeds below `min_rpm_native` refuse activation.

The spark cut acts on the engine. With the fuel mask clear, the APC command
at its stock value, and no transmission reduction request, the veto is the
only active torque actuator: at wide-open throttle the vehicle stops
accelerating inside a hold and accelerates at once after the release, and in
neutral at an unchanged throttle the engine speed settles below the speed it
reaches after the release. The front A/F sensor reads lean inside the holds
at unchanged open-loop fueling, and in closed loop the short-term trim rises
to its cap. The holds produce no exhaust pops: the unburnt charge leaves at
stock timing. The operator reports no DTC in the ECU or the TCM after the
session. The clean DTC readout agrees with the misfire-monitor blanking
through the cut; it does not prove every branch of the blanking.

With `integral_gain` 0 the speed error settles within about 1 s at the
proportional equilibrium, a small positive offset, without drift. The speed
source selected by the image is frame `0x284`, both inside and outside a
hold. Its big-endian bytes 4 and 5, divided by ten into 0.1 km/h counts,
admit one constant target when the published error is subtracted through
each road hold covered by the TRC; frame `0x280` does not. The MLG has no
direct channel for `0xFFFF113C`, so the hold error and ROM selection establish
this result, while its value outside holds is not directly measured. Both
bus speeds keep their relative offset outside holds as well.

The raw CAN join matches TRC and MLG by telemetry tick and snapshot contents,
including a tick wrap before the stationary MLG starts. It covers the road
hold at MLG t=98.657 s; the first two road holds precede the retained TRC.
The `0x176` output/turbine ratio remains around the stable-gear median of
each road hold, with no change of gear, and reads zero in neutral. The
hardware record owns the per-hold figures.

The first `0x180` frame after a released `0x239` code bounds the sampling
delay alone. Its estimated torque equals the parallel `0x160` word through
the holds: neither estimate accounts for the added spark veto. `0x174`
words A and B are TCM requests. These words cannot time restoration of full
physical torque. The veto counter bounds the last veto request between
adjacent coherent snapshots; it does not time the last withheld spark or the
recovery of torque. Phase is a fixed field of page 2 and is current
every tick. In every TRC-covered hold, the counter is constant after the
first non-ACTIVE snapshot through the following inactive interval. An
increment ending at that first snapshot spans the phase transition, rather
than proving a veto request after it.

The last-request intervals on the first-page capture clock extend beyond one
four-stroke engine cycle after the raw released `0x239` frame in some holds.
The stable input `0xFFFF2A85` is not logged: the MLG button channel is host
context from `0x239`, sampled at group completion. A `BUTTON_RELEASED`
abort bounds acceptance of the stable release between the last ACTIVE and
first non-ACTIVE snapshots. Gate aborts `PEDAL_LOW` and `RPM_LOW` precede
acceptance, since the released input overrides those reasons. Under this
runtime contract, the last observed veto request falls within one snapshot
interval of acceptance, or before it. The post-frame counts belong to the
interval before or ending at the phase exit; no veto request after the first
inactive snapshot is observed. Attribution of the full input delay to the
stock five-sample filter remains indirect without its input byte.

The hardware record owns the per-hold timestamps, count bounds, RPM, and
cycle bounds. First-page times are capture proxies rather than interrupt
timestamps; they include unmeasured publication latency. The one-cycle
criterion measured from the raw CAN frame is not accepted. M-mode
acceptance and integral gain selection remain open in issue #103. Spark
angle at the crankshaft and the electrical output at the coil terminals
remain outside the measurement.

## Modes

| Mode | Regulator | Ignition events |
| --- | --- | --- |
| `observe` | computed and published; `q = 0` | unchanged |
| `hold` | computed and published; `q` from the law output and the applied trim | dwell of a fraction `q` of eligible events withheld; fired events carry the trim of the run up to the floor |

Neither mode writes a fuel-cut request, the fuel-cut shadow of a map, or the
final fuel-inhibit mask. Periodic scheduler entry 28 at `0x000219DC` holds the
stock fuel-output inhibit coordinator `0x0004ED88`
(`../defs/JK08A.fuel-inhibit.md`).

Fractions are thousandths. On the activation tick and on every `ACTIVE` tick
that passes its gates and the run timer, the regulator of the run computes its
law output; the actuation under "Ignition command and actuation" turns it into
`q`.

## RPM regulator

The RPM regulator compares native engine speed with the launch engine speed
`Nt` of the map, in native counts of 12.5 RPM, and computes the firing
fraction `p` with the soft width `W = launch_soft_width_native`:

```text
error = rpm - Nt
p = 0                        if error >= 0
p = 1000                     if error < 0 and (W = 0 or error <= -W)
p = (-error * 1000) // W     otherwise
```

`W = 0` is a hard two-step boundary: every eligible event fires below `Nt`
and every one is cut at or above it. A positive `W` cuts a fraction that rises
linearly from zero at `Nt - W` to all events at `Nt`; the engine speed settles
inside that zone. The products are 32-bit, and only a positive numerator is
divided by a nonzero width. The regulator has no integrator and no rate limit,
so the first tick at `Nt` requests a full cut, and the trim efficiency does
not enter `q = 1000 - p`. The configuration contract keeps
`min_rpm_native < Nt - W`, so the zone lies above the minimum engine speed of
gate 14. The stock engine-speed limiter of the image remains the overspeed
protection, and a profile chooses `Nt` below it.

The state record publishes the target and the error of the run, and the
extension publishes `p` as the law output. The SPEED fields of the record hold
zero during an RPM run.

## SPEED regulator

Speeds are km/h*10. The torque fraction `u` and the command are thousandths;
the integrator holds sixteenths of one thousandth. Activation sets `u = 1000`
and empties the integrator. `integral_gain` belongs to the slot of the map
snapshot of the activation. Each tick computes:

```text
e = speed - target
u_p = clamp((window_top - e) * 1000 // window_width, 0, 1000)
step = -(integral_gain * e)
step = 0 if (u_p + I // 16 <= 0 and step < 0)
         or (u_p + I // 16 >= 1000 and step > 0)
I = clamp(I + step, -16 * integrator_limit, 16 * integrator_limit)
command = clamp(u_p + I // 16, 0, 1000)
u = clamp(command, u - rate_limit, u + rate_limit)
```

The proportional fraction is full torque while `e <= window_top - window_width`,
zero while `e >= window_top`, and linear between; the edges are decided before
the division, so only a positive numerator is divided. `I // 16` rounds toward
negative infinity. The integrator falls while the speed is above the target,
rises while it is below, and freezes while its step would deepen a saturated
sum. The controller runs only on ticks whose speed error lies inside the abort
window `-abort_below <= e <= abort_above`. The state record publishes `e`,
`I`, the command, and `u`, which is also the law output; the RPM fields of the
record hold zero during a SPEED run.

## Efficiency table

The fired events of a trimmed run deliver a fraction of their torque. The
builder derives the efficiency table `E[0..40]`, 41 words at `0x000D6390`
beside the configuration record, from the stock spark-efficiency pair
`0x00011D24`/`0x0001199E` of the image:

```text
E[0] = 1000
E[z] = (256 - F(z)) * 1000 // 256        z = 1..40
```

`F` interpolates the 16-point table linearly with a truncated result on
rising and falling segments (`F(20) = 45`, `E[20] = 824`); its axis starts at
0, rises strictly, and reaches 40. Both regulators share the table. The
runtime requires `E[0] = 1000` and `1 <= E[z] <= 1000`; gate 1 refuses any
other table.

The table is neither calibration nor a profile setting. Every build writes it
from F of the image, a calibration transfer derives it again after writing the
F-table bytes, and the extracted settings exclude it. A slot edit leaves it
current; an edit of F or its axis makes it stale. `make preflash` refuses an
image whose stored table differs from F of that image and names the command
that derives the table again:

```bash
uv run python patches/refresh_rolling_launch.py tmp/edited.bin \
  --output tmp/ready.bin
```

The command accepts only an image with a valid current schema 6 record. It
changes only the table and the checksums, then requires a byte-identical stock
rebuild with the image's calibration. Invalid settings, historical records, and
unknown or partial runtimes are refused. `make preflash` still requires a clean
commit, its green Verify run, and executable qualification. The table stays
hidden in the editors: a manual table can diverge from F, and deriving it
from the actual image keeps both consistent.

## Ignition command and actuation

The adapter at the primary ignition-command hook `0x0004E198` applies the
trim `z` of the run to the last stock command `S`:

```text
P = max(S, min(S + z, floor_command))
a = P - S
```

The APC command counts retard, and the timing is `110 - command` degrees,
so the largest floor, 120, limits the trim to 10 degrees ATDC. The adapter
keeps the stock command outside an `ACTIVE` hold, while the P0335 APC
fallback `0xFFFF24C9.bit6` is set, and for a map snapshot outside Maps 1
through 5; it never advances the timing. One effective command `P` reaches
the stock primary consumer `0x0002A892` and `apc_output` `0xFFFF2022`, which
the secondary builder `0x0004E080` and the diagnostics read, so the dwell
start and the spark of an event follow the same command.

The cut fraction uses the efficiency of the applied trim `a`, not of `z`:

```text
q = 0                                       outside an ACTIVE hold or before ready
q = 1000 - p                                RPM
q = 1000 - min(1000, 1000 * u // E[a])      SPEED
```

When the floor clips the trim (`S + z > floor_command`), `a` is smaller than
`z` and `E[a]` larger, so the SPEED cut follows the torque that the fired
events deliver: `(1 - q) * E[a]` equals `u` while `u <= E[a]`, and every
event fires at `u >= E[a]`. A run without trim has `a = 0`, `E[0] = 1000`,
and `q = 1000 - u`.

The adapter publishes `S`, `P`, `a`, and `E[a]`, marks the actuation ready for
the current `ACTIVE` hold, and recalculates `q` from the current law output;
the regulator recalculates `q` from a new law output with the last applied
`a`. Activation clears the ready mark, so `q` stays zero until the adapter
applies the first command of the run, and the P0335 fallback clears it again. An abort
publishes `q = 0` in the tick that detects it; the stock command returns at
the next call of the adapter.

The adapter passes `S` and `P` to the ignition publisher at `0x000D6540`,
which runs the record check first. It publishes `P` with the ready mark only
for an `ACTIVE` hold with `CONFIG_VALID`, without the P0335 APC fallback, and
with `a` in 0..40 and within the trim of the run. Any other input publishes
the stock command, `P = S` with `a = 0`, `E[0]`, no ready mark, and `q = 0`,
whatever `P` the adapter passes. Only an engine pass with a valid
configuration and efficiency table sets `CONFIG_VALID`, so the publisher does
not repeat the configuration check on every ignition event. The publisher
returns the command that the adapter applies: `P` with a published trim and
`S` on the stock path, so the applied command always matches the
publication.

The engine runs in the periodic scheduler with interrupts enabled, and the
ignition publisher runs from the crank-tooth interrupt between any two engine
instructions outside a masked section. Every record state that a publication
can observe in a steady `ACTIVE` pass passes the record check:

- the engine runs the record check through its masked entry at `0x000D7008`,
  so a publication cannot split the fields that the check reads;
- each regulator stores its error pair, base `+0x10` or `+0x18` with
  extension `+0x02`, as one masked store group;
- the control publisher masks interrupts before it stores the law output at
  extension `+0x16` and, in SPEED, the torque fraction at base `+0x0E`, and
  keeps them masked while it reads `S`, `P`, `a`, and the ready mark and while
  the body computes `E[a]`, `q`, and the wire views and stores them with `q`
  last;
- the engine reads, computes, and stores the wire views at the end of every
  pass with interrupts masked.

The integrator and the controller command have no field that the check
couples to them, and they are stored outside the masked groups.

Transitions keep store orders instead of masks. Activation stores the phase
first, the mode after the map, the law output 1000 before the kind, and the
trim of the run last, so the adapter computes `P = S` until the hold is
complete. The law output 1000 gives `q = 0` for both kinds. An abort stores
the phase first. `COOLDOWN` and `IDLE` records carry no ready mark, and
corrupt-state recovery clears the phase before the extension. No mixed state
inside an abort, the return from `COOLDOWN` to `IDLE`, or corrupt-state
recovery passes the check as an `ACTIVE` ready record: a publication inside
them fails the check and publishes the stock command, which is the correct
command there. Inside activation the phase `ACTIVE` meets kind `NONE` until
the kind store, and the status view at extension `+0x1F` keeps kind `NONE`
of the `IDLE` record until a publication or the masked wire views at the end
of the pass rewrite it, so the first publication inside activation fails the
check and publishes the stock command. After the kind store that
publication stores the status view of the new kind. A second publication
after the trim store and before the control publisher then passes the check
once the control error at extension `+0x02` equals the error of the
regulator: activation clears the regulator error, so an `IDLE` record without
a control error passes from the trim store on, and one with the control error
of an earlier hold passes after the error pair of the regulator. Before that
point the second publication fails the check and publishes the stock
command. No regulator reads the control error, so the control error of an
earlier hold delays only that ready mark, at `q = 0`. A second publication that passes publishes the ready mark and `P` of
the complete hold with the law output 1000, so `q = 0`; the control publisher
takes that ready mark and commits `q` of its law, which leaves the records of
a publication after the pass. At
high engine speed the crank-tooth interrupt runs more than once in an engine
pass, so both outcomes occur. Neither publishes a nonzero `q` before the
control publisher commits the law of the pass. The input sample precedes every transition. A sampled change that alters the
wire views fails the check and occurs only on a pass that aborts or outside
`ACTIVE`; other sampled fields are coupled to no control field, so a
publication between the sample and the first store of an abort acts as if it
ran before the pass.

## Spark-cut actuator

In hold mode the dwell-arming wrapper consumes the cut fraction `q` of either
regulator and selects the events whose dwell it requests to withhold. The
wrapper executes at the countdown expiry, before the stock permission check.
The coupled GNU fixture covers the bounded normal-mode scheduling path.
Integration qualification and vehicle acceptance remain open in issue #150;
`hold_actuator = false` keeps enabled HOLD images outside preflash
qualification. The runtime targets the `7mfk` layout. The stock mechanisms
are described in `../defs/JK08A.ignition-output.md`, the misfire readiness gate
in `../defs/JK08A.diagnostics.md`, the inhibit history in
`../defs/JK08A.fuel-cut-consumer.md`, and the throttle request path in
`../defs/JK08A.throttle-control.md`.

### Dwell-start veto

A cut event is withheld before its dwell starts. With `0xFFFF8511.bit7` set
when a countdown slot arms a dwell, the enable check withholds the high-byte
action, so the coil receives no dwell. The `GR11B` match is still serviced:
it leaves no pin to time out, and the sequence guard moves bit 7 into bit 6,
which blocks the recovery at the set arming of that cylinder. The `GR11A`
match finds the pin high and produces no spark, and both output sequences
advance as on a fired event.

The veto fails toward a fired event. A dwell armed before the bit is set
consumes the bit at its `GR11B` service and fires, so a misplaced or late veto
never leaves a coil energized. Handler `0x0002AF38` is the only stock writer
of `0xFFFF8511`, so a cut point sets the bit with one `OR.B` on `GBR` or with
interrupts masked. The P0335 APC fallback scheduler reads `0xFFFF8511` in
`0x0002B768` and in the fallback branch of `0x0002AF38`, which arms a dwell while
`0xFFFF24C9.bit6` and bit 5 or 6 of `0xFFFF8518` are set and enables the high
byte only while `0xFFFF8511.bit7` is clear (`0x0002B344..0x0002B358`). Every
cut point therefore passes all events through while `0xFFFF24C9.bit6` is set.

### Cut point

Literal `0x000296C0` redirects the stock unsigned divider `0x00021CE0` to
wrapper `0x000D60C0`. The countdown slots load it at `0x000294A2` and
`0x0002953A` and call it at `0x000294B2` and `0x0002954A`. The wrapper decides
the veto for the one-hot armed pin mask `0xFFFF13D1`, executes the displaced
divider with its original arguments and preserves the divider's caller ABI.
Table entry `0x000202E4` holds the stock `GR11A` handler `0x0002AB24`.

The divider calls run at interrupt mask 8. The stock `GR11A` and `GR11B`
sources also have priority 8 and cannot preempt the wrapper or the interval
before the countdown raises its mask to 15 for the compare and enable check.
The priority-10 cam interrupt reaches the ignition dispatcher only through
APC fallback. The periodic mode snapshot cannot change during the tooth
handler, so a cam fallback publication cannot interrupt a normal-mode
publication. The exact register and instruction anchors are in
`../defs/JK08A.ignition-output.md`.

The veto decision belongs to the arming event, independently of the order of
the preceding spark, reference tooth and dwell compare. The coupled gate
must establish delivery through the tooth gap, commands `119..160`, and the
`P = 120`, `d = 90` coincidence. An event accepted before release retains its
own stock guard and recovery state; an arming after the phase leaves ACTIVE
creates no cut request.

### Cut selection

The wrapper at `0x000D60C0` saves `r0..r7`, `PR` and `SR`. The event helper at
`0x000D6780` services quiet events and the misfire latch and returns whether
the phase and mode select ACTIVE HOLD. The wrapper reads `q` once as an
aligned word at base `+0x1A` (`0xFFFF5D5A`). These are its only Rolling Launch
control inputs. It restores the caller's registers and SR before tail-calling
`0x00021CE0` with the original divisor and dividend; the stock divider
produces the return value and its arithmetic flags.

An arming is eligible with the sync bit `0xFFFF8501.bit7` set, APC fallback
`0xFFFF24C9.bit6` clear, output-state bit `0xFFFF84EA.bit7` and port-state bit
`0xFFFF4185.bit7` set, `0xFFFF13D2` zero, and stock veto bit `0xFFFF8511.bit7`
clear. The mask `0xFFFF13D1` must contain exactly one of bits 0..5. Invalid
masks pass through without advancing the accumulators or event integrals.
The decision applies no dwell-angle ceiling.

Each armed pin bit has an accumulator, in increasing bit-position order:

```text
acc[c] = acc[c] + 6 * q
cut    = acc[c] >= 6000
acc[c] = acc[c] - 6000 if cut
```

Outside ACTIVE HOLD, for `q > 1000`, and at an eligible arming whose selected
accumulator is outside `0..5999`, all accumulators return to the offsets
`1000 * k + 250`, with `k = (0, 2, 4, 1, 3, 5)`. An ineligible arming leaves
them unchanged. The model checks the cut-accounting bounds of its eligible
cylinder sequence; qualification against the stock arming order belongs to
the coupled gate.

An eligible arming uses its one q sample for the decision and adds it to the
wrapping 32-bit `consumed_q_sum` at extension `+0x10`. It increments the
wrapping 16-bit `eligible_event_counter` at extension `+0x18`, including an
eligible ACTIVE HOLD event with `q = 0`. A selected cut sets
`0xFFFF8511.bit7` and increments the wrapping cut-request counter. The
accumulator, both integrals, veto and counter are committed in one section
at interrupt mask 15. The counter records requests; physical delivery remains
a vehicle acceptance boundary.

The first arming outside ACTIVE HOLD sets no veto and resets the
accumulators. The runtime leaves the stock handling of an already accepted
arming intact. `q = 1000` selects every eligible event. The run timeout bounds
every hold, and the rearm period separates holds.

### Ignition output hardware

The 2007 G35 Sedan service manual for the VQ35HR
(`../refs/nissan-esm-2007-g35-sedan/ENGINE CONTROL SYSTEM.pdf`) describes the
output that the veto acts on:

- EC-466: the power transistor of the coil amplifies the ECM ignition signal
  and switches the primary circuit on and off; that switching induces the
  secondary high voltage.
- EC-490: ECM connector F101 terminals 20, 16, 12, 11, 15, and 19 carry the
  individual ignition signals No. 1..6, which read 0-0.2 V at idle.
- EC-468 and EC-469: coil terminal 1 receives the ECM signal, terminal 2 is
  ground, and terminal 3 holds battery voltage through the condenser with the
  key ON and no signal.

A vetoed event gets no dwell enable, no recovery, and no timeout pin, so its
PULS pin keeps the level it holds between dwells and the ignition signal of
its cylinder keeps its rest level. The power transistor leaves the primary
off, and the coil produces no spark: the circuit stays in its rest state with
the key ON. The polarity and the internal protection of the ECM output stage
between the PULS pin and the terminal are not established. Neither the
service manual nor the JK08A DTC inventory defines an ignition-circuit DTC
(P0351..P0356), so the misfire monitor is the only stock detector of a
withheld spark. CONSULT POWER BALANCE cuts injectors, not sparks, so it does
not exercise this path. The session under "Vehicle evidence of the hold"
confirms the combustion loss of the vetoed events; the electrical level at
the ECM terminals remains unmeasured.

### Torque paths outside the ignition cut

The stock rotational-speed request limiter reaches the throttle plates of
both banks through the signed-request arbitration at the 10.24 ms cadence, and
the vehicle has held engine speed with it. As a hold actuator it has full
authority and keeps every cylinder firing at its normal mixture, so the
misfire monitor and the exhaust see no cut. The actual-torque word follows the
reduced airflow, and the release waits for the plates to open and the manifold
to fill; plate response time is unmeasured. Rolling Launch does not use
throttle control.

The transmission reduction request of frame `0x177` reaches the timing path
only: `0xFFFF3373` -> `0xFFFF1866` -> `0xFFFF1870` -> `0x00065270` ->
`0xFFFF186A` -> `0x00063F30` -> `0xFFFF23C2` -> `0x0004D99C`. Its authority is
the retard authority of the spark-efficiency pair `0x00011D24`/`0x0001199E`,
which is below the reduction that a hold needs, so it serves the retard trim
rather than the cut.

Handler `0x000C4D08` decodes frame `0x1A5` into a 12-bit value with a rolling
counter, and `0x00079824` stores `raw * 5 - 4000` in `0xFFFF27F4` with status
bits in `0xFFFF4197` and `0xFFFF4198`. No reader of `0xFFFF27F4` is present
in the exported code, and no consumer of the decoded value is identified, so
no stock torque request from the chassis controller is established.

### Rejected mechanisms

Omitting a compare is not a safe cut. A skipped set compare ends in a late
spark forced by the dwell timeout, a skipped reset compare ends in a
short-dwell spark from the recovery, and a cleared `0xFFFF13D1` trips the
sequence guard, which also withholds the following cylinder. The immobilizer
inhibit `0xFFFF4198.bit1` forces `0xFFFF13D1` to zero, so it fails the same
way on a single event.

The other stock enable conditions of the arming are not cut points.
`0xFFFF84EA.bit7` and `0xFFFF13D2` are state of the crank-tooth and capture
handlers. `0xFFFF4185.bit7` is the debounced port input that the stock
debouncer `0x00038618` rewrites and that the fuel schedule also reads. The
dwell angle `ignition_dwell_angle/ram` at `0xFFFF237A` is the coil dwell
angle in crank degrees. It is the periodic snapshot of `0xFFFF2406`, bounded
by producer `0x0004C1E4` to 0..114. Builder `0x0004E080` derives the
GR11B reset-edge offset as `120 - angle`, placing the reset edge that angle
before the following spark; the reset-offset source and dwell angle name
the mechanism and physical quantity of the same byte. The narrow hardware
record `rolling_launch.v2_hold_vehicle_2026_11_03.dwell_angle` supports the
unit: `angle * 1000 / (6 * RPM)` gives a dwell time that falls from 4.6 ms
near idle to 3.0 ms at 6000 RPM. Electrical timing at the coil terminals is
outside that measurement. The periodic snapshot cannot express a per-event
cut. The dynamic field `ignition_dwell_angle_raw` carries this meaning.

The fuel-inhibit mask is not a Rolling Launch actuator. With single-channel
injection events, a change of a partial mask acts on each channel at its next
event, with no carry-over through the history `0xFFFF1935`. Start pulses and
catch-up events that address several channels are all-or-nothing. No stock
post-cut enrichment keys off the DFCO state; the publisher `0x000556EC` reacts
only to the full mask `0x3F`. Closed-loop trims do not read the mask and keep
correcting while cylinders are cut. At high cut fractions the wall film of a
cut port evaporates and must rebuild when the cylinder resumes.

### Misfire monitor gating

A withheld spark and a fuel cut both leave the misfire monitor running,
because no readiness condition reads the inhibit mask or the DFCO state.
During an `ACTIVE` hold the arming-event helper stores the marker `0x01` into
latch `0xFFFF436F` at every armed event that finds the latch zero. The readiness
gate then fails, which clears bits 6 and 7 of `0xFFFF4251` and the P030
working state. The helper counts the armed events outside `ACTIVE` in the
quiet-event byte, which saturates at 255. In `IDLE`, once that count reaches
14, it clears the latch only while the latch holds `0x01`, so a stock value is
never overwritten. The P030 metrics span thirteen event periods. The quiet-event delay retains
the marker while the stock output state of an accepted arming completes.

The stock writer at `0x00082FC8` in `0x00082C8A` stores calibration byte
`ROM8[0x00008C2E]` (`0x32` in stock) with a plain `MOV.B`. The calibration
transfer and `make preflash` refuse a calibration that sets that byte to
`0x01`. Both check-and-stores of the helper run in the crank-tooth interrupt with
interrupts masked, so neither interleaves with the stock writer.

## Configuration

The strict 102-byte schema-6 record at `0x000D6320` has a 40-byte head and
five 12-byte map slots at `+0x28`. The head contains:

| Field | Contract |
| --- | --- |
| magic, inverse, head marker | fixed integrity sentinels |
| schema | version 6 |
| mode | observe or hold |
| enable mask | one bit per map, unused bits clear |
| options | zero |
| coolant minimum/maximum | ordered byte range |
| minimum/maximum speed | km/h*10 words of the SPEED activation range; zero disables that side; two nonzero bounds are ordered |
| minimum RPM | native value, 1..32766 |
| minimum pedal | native value; zero disables the gate |
| target offset | signed km/h*10, `-abort_above < offset < abort_below` |
| window width | nonzero byte, km/h*10 |
| window top | byte, km/h*10 |
| rate limit | 1..1000 thousandths per tick |
| reserved word `+0x16` | zero |
| integrator limit | 0..1000 thousandths |
| abort above/below | nonzero bytes, km/h*10 |
| reserved bytes `+0x1C`, `+0x1D`, `+0x23` | zero |
| run timeout and rearm | 1..0x7FFF ticks |
| speed-frame age limit | 1..254 counts of the stock receive age |

Slot `n` at `+0x28 + 12 * n` belongs to Map `n + 1`, and the end marker
`0xA55A` follows the last slot at `+0x64`:

| Slot offset | Field | Contract |
| --- | --- | --- |
| `+0` | integral gain | signed word, 0..0x7FFF, SPEED only |
| `+2` | RPM trim | byte, 0..40 APC command counts |
| `+3` | speed-hold trim | byte, 0..40 APC command counts |
| `+4` | floor command | byte, 0..120, the latest APC command of either trim |
| `+5` | reserved | zero |
| `+6` | launch RPM | native word, above the minimum RPM and at most 0x7FFF |
| `+8` | launch speed threshold | km/h*10 word, 1..0xFFFF |
| `+0xA` | launch soft width | native word, below launch RPM minus the minimum RPM |

Every slot is validated whether or not its map is enabled. The RPM limits are
an arithmetic contract, not recommended settings.

The built-in profile is `observe` with every map disabled: launch RPM one
count above the minimum RPM, threshold 1, soft width 0, and both trims 0. It
is a valid disabled record of every family, not a hardware test profile. The
relocated targets take it, and their images receive no Rolling Launch bytes.
A strict local TOML profile of schema 4 selects the mode, the map mask, every
head field, and the slot fields as a scalar or a list of five values; the
launch RPM, threshold, soft width, and integral gain of every map are
mandatory. Unknown fields are rejected, and enabled maps use one-based
numbers. See `rom-builder.md` for the profile schema and build invocation.

RomRaider and XDF expose the per-map enable bits, the pedal requirement as a
switch, and independent calibration tables for the unsigned activation and
controller fields. Each map exposes the launch speed threshold in km/h, the
launch RPM and the soft width in RPM, where a zero width is the hard two-step,
the RPM trim and the speed-hold trim in degrees, Ki, and the timing floor in
degrees ATDC. The floor display is `floor_command - 110`, with inverse
`ATDC + 110`; negative values are before TDC. The gain is limited to
0..32767, and each trim to 0..40. The efficiency table and the reserved fields
are hidden. A slot edit leaves the efficiency table current; an edit of F
requires the refresh command. Slot addresses derive from the configuration
address of the runtime layout and the schema-6 slot offset and stride. The
signed target offset, coolant maximum, and run and rearm periods stay in the
build profile. Raw aggregate records remain implementation data, not a tuning
interface. Generated definitions are projections of the live JK08A source
annotations and layouts.

## Allocation and hooks

Every range names an exclusive end, as `runtime-reservations.md` does.

| Region or address | Size | Purpose |
| --- | ---: | --- |
| `0x000D3860..0x000D38E4` | 132 | periodic, selector-arbiter, and startup wrappers |
| `0x000D38E4..0x000D3EA0` | 1,468 | state engine, gates, and configuration check |
| `0x000D3EA0..0x000D3F60` | 192 | primary ignition-command adapter |
| `0x000D3F60..0x000D3F80` | 32 | retired schema 1 to 3 configuration span, erased |
| `0x000D40C0..0x000D41E0` | 288 | SPEED regulator |
| `0x000D41E0..0x000D4280` | 160 | dashboard feedback arbiter |
| `0x000D6000..0x000D6040` | 64 | removed fuel-cut wrapper span, erased |
| `0x000D6040..0x000D6068` | 40 | retired schema-4 configuration span, erased |
| `0x000D6068..0x000D60C0` | 88 | removed RPM ceiling span, erased |
| `0x000D60C0..0x000D6220` | 352 | spark-cut actuator |
| `0x000D6220..0x000D6268` | 72 | retired schema-5 configuration span, erased |
| `0x000D6268..0x000D6320` | 184 | removed schema-5 slot-validator and trim span, erased |
| `0x000D6320..0x000D6386` | 102 | configuration record |
| `0x000D6386..0x000D6390` | 10 | padding, erased |
| `0x000D6390..0x000D63E2` | 82 | efficiency table |
| `0x000D63E2..0x000D6400` | 30 | padding, erased |
| `0x000D6400..0x000D6480` | 128 | RPM regulator |
| `0x000D6480..0x000D6500` | 128 | RPM firing fraction |
| `0x000D6500..0x000D6540` | 64 | control publisher of the actuation |
| `0x000D6540..0x000D6580` | 64 | ignition publisher of the actuation |
| `0x000D6580..0x000D6680` | 256 | common actuation body |
| `0x000D6680..0x000D6780` | 256 | slot and efficiency-table validator |
| `0x000D7000..0x000D7200` | 512 | record check and wire views |
| `0xFFFF5D40..0xFFFF5D6C` | 44 | runtime state |
| `0xFFFF6100..0xFFFF6120` | 32 | runtime state extension |

Schemas 1 through 3 kept a 32-byte record at `0x000D3F60`, schema 4 a 40-byte
record with one integral gain for every map at `0x000D6040`, and schema 5 a
72-byte record with 6-byte slots at `0x000D6220`. These spans, the removed
fuel-cut wrapper, RPM ceiling, slot-validator, and trim spans, and the padding
stay claimed and erased inside the current Rolling Launch write set. Each
registered historical endpoint places its units, hook words, DID slots and
record by its own addresses in `runtime_endpoints.py`, so classification and
extraction of its images do not depend on the current layout. No historical
record states the launch RPM, threshold, and soft width of schema 6, so
extraction reports a historical record with its fields and writes no profile.
The Map Switching map copies at `0x000D3F80` leave no room to grow the record
in place.

Every registered endpoint before schema 5 leaves the slot-validator and trim
span `0x000D6268..0x000D6320` erased. The endpoints before schema 4 also leave
the RPM ceiling span `0x000D6068..0x000D60C0` and the spark-cut span
`0x000D60C0..0x000D6220` erased and the `GR11A` table entry at the stock
handler. Every signature binds those bytes.
The speed-hold runtime without the ceiling latch, whose state has 24 bytes, is
not a registered endpoint: the builder and `make preflash` classify its images
as an unknown Rolling Launch state and refuse them.

The composition replaces six declared targets:

- periodic scheduler entry 1 at `0x00021970`;
- map-selector host at `0x000CE8DC`;
- startup state initialization at `0x00027D28`;
- primary ignition-command consumer at `0x0004E198`;
- dashboard feedback call at `0x000C3FA4`;
- dwell-arming divider literal at `0x000296C0`, whose displaced target is
  `0x00021CE0`.

The `GR11A` table entry at `0x000202E4` holds stock handler `0x0002AB24`.

It restores the stock words that the fuel path of the schema 4 and 5
endpoints replaced: periodic scheduler entry 28 at `0x000219DC` holds the
stock fuel-output inhibit coordinator `0x0004ED88`, and the DID pointer slots
`0x00022914` and `0x00022960` of `0x121E` and `0x1231` hold `0xFFFFFFFF`.
Classification refuses a current image that holds any word of that fuel path.

The dashboard hook redirects the existing map-feedback wrapper call to the
Rolling Launch arbiter. The arbiter invokes that wrapper before applying its
own state. Every wrapper calls its displaced function where required.
Allocation and hook bytes are authoritative only in
`rolling-launch-layout.toml`.

## State and diagnostics

The 44-byte state record at `0xFFFF5D40` and the 32-byte extension at
`0xFFFF6100` are separate allocations. `STATE_FIELDS` of `rolling_launch.py`
names the offset and format of every field of both; the telemetry
configurations and the hold audit read them through that map.

The record holds phase, abort reason, flags, map/mode snapshots, run and
rearm timers, captured RPM, the SPEED target, the torque fraction after the
rate limit, the speed error, the integrator, the command before the rate
limit, the RPM target, the RPM error, the cut fraction `q` at `+0x1A`, and the
trim of the run at `+0x1E`. The fields of the regulator that a run does not
use hold zero. The spark-cut actuator owns the quiet-event count and the cut
counter at `+0x1C` and `+0x1D` and the six accumulators at `+0x20..+0x2C`;
`+0x1F` is a reserved zero byte.

The extension holds the regulator kind, the input status bits, the error of
the regulator, the RPM and speed samples, the stock and effective commands,
the applied trim, the actuation-ready mark, `E[a]`, the consumed `q` sum and
the eligible-event counter of the actuator, the accepted button code, the
speed age, the law output, the CANCEL capture, the target of the run, and
three packed views for telemetry: `E[a]` with the kind and the ready mark,
the applied trim with the kind and the ready mark, and the kind with the input
bits, the CANCEL and released codes, and the ready mark.

The startup wrapper clears both allocations. Corrupt-state recovery clears
the engine part `+0x00..+0x1C` of the record, the trim of the run, the
reserved byte, and the extension. Both then store `E[0] = 1000` and its wire
view. An `ACTIVE` state requires the RPM or SPEED kind, a law output and
`q` of 0..1000, a ready mark of 0 or 1, a trim of 0..40, zero reserved
fields, and zero fields of the unused regulator; with the ready mark set, the
applied trim does not exceed the trim of the run and `q` equals the actuation
of the published law output and `E[a]`. Any other `ACTIVE` state is corrupt.

The flags publish every satisfied gate, `ACTIVE`, and hold. Bits 13 and 15
are always clear. Abort reasons 22 to 25 name the invalid speed value, the
speed source that is not ready, the invalid RPM input, and the invalid CANCEL
capture; the other reasons keep their numbers.

Raw engineering DIDs expose two-byte views of the state record:

| DID | View |
| --- | --- |
| `0x1211` | phase and abort reason |
| `0x1212` | flags |
| `0x1213` | map and mode snapshot |
| `0x1216` | run ticks |
| `0x1217` | rearm ticks |
| `0x1224` | captured RPM |
| `0x1227` | target speed |
| `0x1228` | torque fraction |
| `0x1229` | speed error |
| `0x121D` | integrator |
| `0x121F` | command before the rate limit |
| `0x1232` | quiet-event count (high byte) and cut counter (low byte) |

The SPEED views `0x1227`, `0x1228`, `0x1229`, `0x121D`, and `0x121F` read zero
during an RPM run. The RPM target, the RPM error, and the extension have no
DID; the telemetry configurations read them as state views.

Every view uses a free pointer slot of the service `0x22` table of family
`0x12`, whose records outside the low bytes `0x00`, `0x20`, and `0x40`
answer two bytes. Every historical endpoint before the spark cut publishes
the views `0x1211` to `0x1229` and leaves the slots of `0x121D`, `0x121E`,
`0x121F`, `0x1231`, and `0x1232` stock. The schema 4 and 5 endpoints
also publish `0x121D`, `0x121F`, `0x1232`, the fuel-cut request `0x121E`, and
the RPM ceiling latch `0x1231`. The current runtime keeps the slots of
`0x121E` and `0x1231` stock and does not reuse their numbers.

These DIDs are custom instrumentation, not factory CONSULT parameters. They are
useful only when the diagnostic client can request the raw identifiers and are
not a prerequisite for runtime correctness.

## Composition

`build_rom.py` is the production entry point. It starts from the registered
stock image, installs the current Map Switching composition, applies the
target-specific Rolling Launch stage with the selected profile and the
efficiency table derived from F of the image, adds the CAN telemetry layer,
recalculates all checksum domains, and verifies the final closed write set.

The composition and assembly modules require the exact base composition and
bind every byte to the declared layout and payload manifests. While the layout
states `payloads_ready = false`, the layout loader accepts the ABI alone and
the builder refuses composition.

The canonical runtime uses `0xFFFF5D40..0xFFFF5D6C` and
`0xFFFF6100..0xFFFF6120` for active state and `0x000D40C0..0x000D4280`,
`0x000D6000..0x000D6780`, and `0x000D7000..0x000D7200` for its claimed ROM
extensions. The cross-runtime ledger assigns
`0x000D6780..0x000D6800`, `0xFFFF6120..0xFFFF6160`, and
`0xFFFF6160..0xFFFF6200` exclusively to future Rolling Launch revisions; the
first RAM span is the scratch budget of the veto delivery. These reserves are
erased and outside every exact current write set. See
`runtime-reservations.md`.

The implementation inventory is:

| Artifact | Responsibility |
| --- | --- |
| `rolling-launch-layout.toml` | allocation, hooks, diagnostics, and defaults |
| `rolling-launch-payloads.toml` | exact assembled payloads |
| `rolling-launch-wrappers.s` | periodic, selector-arbiter, and startup wrappers |
| `rolling-launch-engine.s` | state engine, gates, and configuration check |
| `rolling-launch-speed-controller.s` | SPEED regulator |
| `rolling-launch-spark-cut.s` | spark-cut actuator and misfire latch |
| `rolling-launch-ignition-adapter.s` | primary ignition-command adapter |
| `rolling-launch-rpm.s` | RPM regulator and firing fraction |
| `rolling-launch-actuation.s` | control and ignition publishers, actuation body, and `q` |
| `rolling-launch-validator.s` | map-slot and efficiency-table validator |
| `rolling-launch-state-check.s` | record check and wire views |
| `rolling-launch-spark-events.s` | armed-event quiet and misfire-latch service |
| `rolling-launch-feedback.s` | dashboard feedback arbitration |
| `rolling_launch.py` | independent fail-closed model |
| `rolling_launch_layout.py` | structural validation |
| `rolling_launch_assembly.py` | payload and source-byte validation |
| `rolling-launch-flow.toml` | register conventions of the units and of their stock and Map Switching callees |
| `rolling_launch_flow.py` | control-flow and dataflow check of the units |
| `rolling_launch_compose.py` | pure in-memory composition |
| `apply_rolling_launch.py` | builder stage: source checks and application |
| `build_rom.py` | production composition, efficiency table, and checksum closure |
| `refresh_rolling_launch.py` | efficiency-table normalization of an edited image |
| `runtime_endpoints.py` | historical endpoint identities, runtime classification, and record extraction |
| `../tools/sh-elf-run/verify_rolling_launch.py` | controller verifier integration |
| `../tools/sh-elf-run/verify_rolling_launch_ignition.py` | coupled ignition, recovery and dwell-veto GNU gate |
| `hardware-results.toml` | immutable hardware-result registry |

## Verification gates

A candidate is software-valid only when all applicable checks pass:

1. The exact selected stock base and complete current Map Switching composition
   match the registered target profile.
2. ROM/RAM ownership, stock anchors, hooks, restored stock words, diagnostic
   pointers, and payload digests match their manifests.
3. Assembly sources reproduce the exact injected bytes. The flow check of
   the assembly validation builds the control-flow graph of every function
   of the units and requires the convention that `rolling-launch-flow.toml`
   declares for it: the registers it reads and writes and its outputs, an
   empty stack and the entry PR at every return and tail jump, no register
   live after a call that the callee writes without an output, and the T of
   every conditional branch, T-reading call and T output from a comparison,
   a test, a declared producer, a callee T output or the T of the caller,
   with every comparison and test consumed. The declarations of the stock
   and Map Switching callees bind their calls.
4. The independent model covers every gate, phase transition, abort reason,
   corrupt-state recovery, map isolation, rearm boundary, the CANCEL capture,
   the regulator selection, the hard and soft RPM zone, the SPEED controller
   bounds, the map slots, the efficiency table, the ignition command and the
   actuation with its ready mark, and the cut selection, consumed-`q`
   accounting, resets, and misfire latch of the spark-cut actuator.
5. The GNU SH fixture independently executes the same current payload bytes
   of the wrappers, the engine, both controllers, the publishers, the
   actuation, the slot validator and the record check against rows that the
   reference model derives, and compares the complete test RAM, the
   preserved registers, SP, GBR and SR after every call. Its trace covers
   every instruction, both outcomes of every branch, every delay slot, every
   call with its return, and every literal target of each register transfer,
   and three negative row sets leave exactly the obligations of their
   omitted paths unmet: the periodic wrapper, and the integrator lower-limit
   outcome of the speed controller and the cooldown validity outcome of the
   engine, each with the block that only it reaches.
   Interrupt rows run the ignition publisher from an injected interrupt at
   every interleaving with the loads and stores of steady `ACTIVE` passes of
   both kinds, of an activation of each kind, of an abort and of
   corrupt-state recovery. They
   require acceptance only outside the masked sections, the model
   publication of every observed record, final records of a publication
   before or after the pass or, inside recovery, of the recovery alone, the
   stock command from every first publication between the error pair of the
   RPM activation and the publisher mask, and the store orders of the
   transitions. The hook requests one interrupt per run, so a republication
   pass of each activation stores the bytes of the executed first
   publication after the kind store before its publication. Every such
   second publication after the trim store publishes the model command of
   its record, and each that passes the check publishes the ready mark and
   `P` with `q = 0` and leaves the records of a publication after the pass.
   An RPM activation from an `IDLE` record without a control error passes
   at every such boundary.
   The ignition gate binds both command builders and schedulers, the
   phase normalizer, the tooth countdown and recovery, the stock GR11A/GR11B
   handlers, the adapter and the veto into one path. The veto kernel checks
   its complete divider ABI, eligibility, q consumption, counters and latch
   against a separate C reference.
6. Every final difference is inside the combined component and checksum write
   sets.
7. The generated definition tables agree with the configuration contract.
8. `build_rom.py --verify-only` accepts the exact candidate input and profile.

The `--rolling-ignition` scope executes the coupled builders and schedulers,
the phase-zero tooth-gap sequence, both compare handlers, both recovery
entries, release boundaries and tooth interrupts inside the periodic engine.
Its H9/H32 windows bound the recorded scheduling defect; the compare and pin
events are explicit simulator inputs. The narrow GNU README declares the
excluded crank decoder and the fixture-only context and observation code.
The native firmware pipeline requires this scope. Full image integration
qualification and vehicle acceptance remain open in issue #150, so the
image is ineligible for hardware testing.

Software verification does not authorize a flash. The CANCEL capture, both
regulators, the actuation, the spark cut and its veto delivery, corrupt-state
recovery, and map changes while active remain software-only boundaries of
schema 6. A physical timing claim requires a crank-referenced
measurement, and an injector-pulse claim requires an electrical measurement at
the output path.
