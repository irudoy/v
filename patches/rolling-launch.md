# Rolling Launch runtime

Rolling Launch is an optional runtime layered on the complete five-slot
Map Switching composition. While CANCEL is held it captures vehicle speed as
the hold target and runs a speed-hold controller that publishes a torque
fraction. Hold mode latches an all-cylinder fuel-cut request above the
captured engine speed plus a ceiling offset and releases it below a
hysteresis, and a wrapper of the stock fuel-output inhibit coordinator merges
the request into the final cylinder mask. It runs
on the exact `7mfk` images JK00A, JK03A, JK03B, and JK08A. The relocated
targets JK00C, JK00D, JK78C, 1ND0A, 1ND3B, and 1ME3B carry no Rolling Launch
runtime.

The authoritative implementation sources are:

- `rolling-launch-layout.toml` for ROM/RAM ownership, hooks, and diagnostics;
- `rolling-launch-payloads.toml` for exact assembled payload bytes;
- `rolling_launch.py` for the independent state, calibration, and controller
  model;
- `hardware-results.toml` for immutable image identities and hardware outcomes.

The canonical JK08A runtime is software-verified. No payload consumes the
torque fraction, so an image of this runtime holds no vehicle speed, and the
only torque reduction it applies is the RPM ceiling request of hold mode.
Such an image is not a vehicle candidate. The designed consumer of the torque
fraction is the dwell-start veto under "Speed-hold cut actuator" (issue #100).

The target-vehicle evidence below comes from exact local combined images of
the registered historical endpoint `schema-3-fuel-shadow-hold`, which held RPM
through the fuel-cut shadow of the selected map. It qualifies button decoding,
dashboard states, repeated rearm, and the full software fuel-inhibit mask. The
vehicle-speed capture, the controller, the coordinator wrapper, and the
ceiling request have no vehicle evidence. Physical spark timing and electrical
injector output remain unmeasured. Concrete profiles, derived images, and
active tune identities remain local and unversioned.

## Functional model

The runtime has three phases:

```text
IDLE -> ACTIVE -> COOLDOWN -> IDLE
```

`IDLE` evaluates activation gates. Activation captures the selected map, the
configured mode, native RPM, and the target speed, and starts the controller
from full torque with an empty integrator. `ACTIVE` runs the controller on
every tick that passes its gates and owns the fuel-cut request of hold mode.
Any abort releases the request and enters `COOLDOWN`. `COOLDOWN` requires the
released button code `0x20` for the configured rearm period before returning
to `IDLE`.

Button codes follow the target vehicle's debounced ASCD representation:

| Code | Meaning |
| --- | --- |
| `0x02` | CANCEL, activation request |
| `0x08` | SET, map-selection request |
| `0x20` | all buttons released |
| `0x00` | invalid, fail closed |

The runtime never treats zero as a release. Invalid phase, snapshot, timer,
torque-fraction, or configuration state restores Map 1 through the limiter
commit path, clears the runtime state, and enters a safe cooldown.

## Activation gates

Activation requires every gate to pass in this order:

1. The 40-byte configuration record is structurally valid.
2. The active map index is within Maps 1 through 5.
3. Rolling Launch is enabled for the active map.
4. Selector phase, count, and elapsed time are idle.
5. Visual-feedback pulse, phase, tick, and reserved fields are idle.
6. The MAIN switch bit of the stock ASCD flag byte is clear.
7. The stable button is CANCEL.
8. The receive age of the vehicle-speed frame is within the configured limit.
9. Vehicle speed lies inside the configured activation range; a zero bound
   disables its side of the range.
10. Engine speed meets the configured minimum.
11. Pedal position meets the configured minimum; zero disables this gate.
12. Coolant temperature is inside the configured range.
13. Run and rearm timers are valid.

The first failed gate is recorded as the abort reason. `ACTIVE` evaluates the
same gates on every tick, except that gate 9 becomes the speed-error window:
the vehicle speed minus the captured target must stay within the configured
distances above and below the target. Map or mode changes while active abort
the run before any gate reason. Timeout, CANCEL release, an invalid button, a
stale speed frame, a speed outside the window, or SET also abort. SET records
a map-request abort so map selection can begin after rearm.

Vehicle speed is the word `0xFFFF113C` in km/h*10, which the stock receive
handler of CAN frame `0x284` publishes (`../defs/JK08A.can.md`). Gate 8 reads
the stock receive age `0xFFFF3B38` of that record. `FUN_000C3994` advances the
age on every pass of the pending-task table `0x00021834`, which runs every
10.24 ms like the Rolling Launch tick, and a pass that processes a new frame
clears it; it saturates at 255. Frame `0x284` arrives every 20 ms, so the age
stays at 0 to 2. One count is 10.24 ms, and the default limit of 10 tolerates
102.4 ms without a frame. A lost speed frame therefore refuses activation and
aborts a run with `SPEED_FRAME_STALE`.

The age stays at zero while `0xFFFF4185` bit 7 is clear and advances only
while `0xFFFF4195` bit 0 is set. Outside those CAN states a lost frame leaves
the age below the limit and `0xFFFF113C` at its last value, so only the run
timeout and the CANCEL release end the hold. The vehicle check that this age
follows frame `0x284` alongside the speed word is open (issue #103).

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

## Modes

| Mode | Torque fraction | Fuel cut |
| --- | --- | --- |
| `observe` | computed and published | unchanged |
| `hold` | computed and published | all-cylinder request latched above the RPM ceiling |

## Speed-hold controller

Activation captures the vehicle speed and native RPM of the activation tick:

```text
target = clamp(speed + target_offset, 0, 0xFFFF)
```

Speeds are km/h*10. The torque fraction `u` and the command are thousandths
of full torque; the integrator holds sixteenths of one thousandth. Activation
sets `u = 1000` and empties the integrator. On the activation tick and on
every `ACTIVE` tick that passes its gates and the run timer, the controller
computes:

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
zero while `e >= window_top`, and linear between. The integrator falls
while the speed is above the target, rises while it is below, and freezes
while its step would deepen a saturated sum. The stock unsigned divider
`0x00021CE0` forms the quotient. The state record publishes `e`, `I`, the
command, and `u`. The controller runs only on ticks whose speed error lies
inside the abort window `-abort_below <= e <= abort_above`.

## Fuel-cut request

In `hold`, every `ACTIVE` tick that runs the controller evaluates the RPM
ceiling latch at state offset `+0x18`:

```text
cut     = captured_rpm + ceiling_offset
restore = cut - ceiling_hysteresis
latch   = 1 if rpm > cut
          else latch and rpm > restore
```

The tick publishes the request `0x003F` in the state record while the latch is
set, so the cut starts strictly above the ceiling and ends at or below the
restore point. Both sums are formed in 32 bits, so a high captured RPM never
wraps below either threshold. Every engine entry clears the request first, so
only such a tick publishes it. Activation and every abort clear the latch, and
an abort releases the request in the tick that detects the abort. `observe`
clears the latch and never publishes a request. No mode writes the fuel-cut
shadow of the selected map.

The speed controller calls the leaf unit at `0x000D6068`, which evaluates the
latch and adds the hold, ceiling, and fuel-cut flags to the published flags.

Periodic scheduler entry 28 at `0x000219DC` calls the fuel-cut wrapper in
place of the stock six-channel fuel-output inhibit coordinator `0x0004ED88`
(`../defs/JK08A.fuel-inhibit.md`). The wrapper runs the coordinator first, so
every stock contribution remains, then ORs a request of `0x0001..0x003F`
into the final cylinder mask at `0xFFFF22E0` and returns the coordinator's
`r0`. Zero and any request with a bit outside the six cylinder bits leave the
stock mask unchanged. Entry 1 runs the engine before entry 28, so the mask
carries the request of the same scheduler pass, and an abort releases the cut
in the pass that detects it. An interrupt-context reader of the mask can
observe the stock result between the coordinator store and the merge.

## Primary ignition command

The primary ignition-command hook at `0x0004E198` stays on the Rolling Launch
layer. Its adapter tail-jumps to the stock consumer `0x0002A892` with every
argument register unchanged, so the APC command keeps its stock value in
every phase and mode.

## Speed-hold cut actuator

The speed-hold controller publishes the torque fraction, and no payload
consumes it. The designed actuator cuts torque by withholding the dwell of
selected ignition events, and the `GR11A` spark handler sets the veto
(issue #100). The fuel-inhibit mask through the coordinator wrapper remains
the hard limit and the abort path. The runtime runs on the `7mfk` layout; the other
layouts receive it after its vehicle acceptance on `7mfk`. The stock
mechanisms are described in `../defs/JK08A.ignition-output.md`, the misfire
readiness gate in `../defs/JK08A.diagnostics.md`, the inhibit history in
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
interrupts masked. The cam fallback reads `0xFFFF8511` in `0x0002B768` and in
the fallback branch of `0x0002AF38`, which arms a dwell while
`0xFFFF24C9.bit6` and bit 5 or 6 of `0xFFFF8518` are set and enables the high
byte only while `0xFFFF8511.bit7` is clear (`0x0002B344..0x0002B358`). Every
cut point therefore passes all events through while `0xFFFF24C9.bit6` is set.

### Cut point

The veto is set from the `GR11A` spark handler. The table lists it with the
two alternative points:

| Cut point | Veto delivery | Authority | Decision latency | Patch footprint |
| --- | --- | --- | --- | --- |
| Spark handler (chosen): table entry `0x000202E4` redirected to a wrapper that branches to `0x0002AB24` | No `GR11B` match falls between a spark and the dwell start of its successor, so the veto reaches the dwell of the successor that the handler writes to `0xFFFF13D3`. Above about 110 degrees of dwell the successor can be armed before the spark, and that event fires. | Every event | The preceding spark, 120 crank degrees before the target spark | One table word and a wrapper in the `GR11A` interrupt |
| Countdown divider: literal `0x000296C0` redirected to a wrapper that tail-calls `0x00021CE0` | A `GR11B` match with priority above 8 can preempt between the wrapper and the mask-15 section, and that event fires. | Every event | The arming tooth, within 10 degrees of the dwell start | One literal word and a wrapper in the crank-tooth interrupt, run at every countdown expiry |
| Ignition hook `0x0004E198` | The veto reaches the next dwell that a countdown arms, of the current cylinder or its successor. A dwell already armed consumes it, and that event fires. | Depends on the spark and dwell angles | The event tooth | The existing ignition adapter; no new hook |

The wrapper decides the veto before it branches to `0x0002AB24`, which clears
`0xFFFF8517.bit7` at `0x0002ABAC..0x0002ABAE`. It sets the veto only while
`0xFFFF8517.bit7` and the sync bit `0xFFFF8501.bit7` are set and
`0xFFFF24C9.bit6` is clear. The stock handler treats a `GR11A` match as a
spark event only with `0xFFFF8517.bit7`, and it advances `0xFFFF13D3` only
with `0xFFFF8501.bit7`. The no-pending branch of the dwell timeout
(`0x0002B498..0x0002B4C8`) produces a `GR11A` match without
`0xFFFF8517.bit7`; a veto at that match would withhold an extra dwell and
miscount the cut events.

All three points use the same stock veto, so the open hardware questions are
the same: the absence of a spark at the coil on a vetoed event, the behavior
of the igniter driver stage with a withheld dwell, the A/F sensors and closed
loop with unburned charge in the exhaust, and the misfire monitor gating on
the vehicle. The interrupt priorities of the `GR11A` and
`GR11B` matches are not established; a spark handler delayed past the arming
of the next dwell meets the same edge case as a large dwell angle.

The spark handler uses the same stock veto and failure direction as the
countdown divider, adds no code to the crank-tooth interrupt, has no `GR11B`
service in its veto window, and redirects the table entry of a handler that
has no other caller. The countdown divider is not used because a `GR11B`
match with priority above 8 can take its veto inside the crank-tooth
interrupt. The ignition hook is not used because its authority depends on the
spark and dwell angles. The edge case of the spark handler needs a dwell
angle above about 110 degrees, and a log of `0xFFFF237A` over the hold range
shows whether the hold reaches it. Above 120 degrees the `GR11B` match of the
successor precedes the spark, so the veto passes to the following arming and
the cut moves by one cylinder; the wrapper sets no veto above about 110
degrees, which keeps the cut accounting per cylinder.

### Torque paths outside the ignition cut

The stock rotational-speed request limiter reaches the throttle plates of
both banks through the signed-request arbitration at the 10.24 ms cadence, and
the vehicle has held engine speed with it. As a hold actuator it has full
authority and keeps every cylinder firing at its normal mixture, so the
misfire monitor and the exhaust see no cut. The actual-torque word follows the
reduced airflow, and the release waits for the plates to open and the manifold
to fill; plate response time is unmeasured. The v2 design excludes throttle
control.

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
dwell angle `0xFFFF237A` is a periodic snapshot with a stock range of 0..114
degrees and cannot express a per-event cut.

The fuel-inhibit mask is not the speed-hold actuator. With single-channel
injection events, a change of a partial mask acts on each channel at its next
event, with no carry-over through the history `0xFFFF1935`. Start pulses and
catch-up events that address several channels are all-or-nothing. No stock
post-cut enrichment keys off the DFCO state; the publisher `0x000556EC` reacts
only to the full mask `0x3F`. Closed-loop trims do not read the mask and keep
correcting while cylinders are cut. At high cut fractions the wall film of a
cut port evaporates and must rebuild when the cylinder resumes.

### Misfire monitor gating

A withheld spark and a fuel cut both leave the misfire monitor running,
because no readiness condition reads the inhibit mask or the DFCO state. On
activation the actuator design stores the marker `0x01` into latch `0xFFFF436F` when
the latch is zero. The readiness gate then fails, which clears bits 6 and 7 of
`0xFFFF4251` and the P030 working state. The COOLDOWN -> IDLE transition
clears the latch only while it holds `0x01`, so a stock value is never
overwritten. The stock writer stores calibration byte `ROM8[0x00008C2E]`
(`0x32` in stock), so the rule requires that byte to differ from `0x01`. The
check-and-store of the marker runs in the task of `0x00082C8A` or with
interrupts masked, so it cannot interleave with the stock writer. The P030
metrics span thirteen event periods, so the latch stays held for at least
thirteen events after the last cut. The rearm period must cover that span; one
second covers it above 260 RPM.

## Configuration

The strict 40-byte schema-4 record contains:

| Field | Contract |
| --- | --- |
| magic, inverse, end marker | fixed integrity sentinels |
| schema | version 4 |
| mode | observe or hold |
| enable mask | one bit per map, unused bits clear |
| options | zero |
| coolant minimum/maximum | ordered byte range |
| minimum/maximum speed | km/h*10 words; zero disables that side; two nonzero bounds are ordered |
| minimum RPM | nonzero native value |
| minimum pedal | native value; zero disables the gate |
| target offset | signed km/h*10, strictly inside both abort distances |
| window width | nonzero byte, km/h*10 |
| window top | byte, km/h*10 |
| rate limit | 1..1000 thousandths per tick |
| integral gain | 0..0x7FFF |
| integrator limit | 0..1000 thousandths |
| abort above/below | nonzero bytes, km/h*10 |
| RPM ceiling offset | nonzero native value |
| run timeout and rearm | 1..0x7FFF ticks |
| speed-frame age limit | 1..254 counts of the stock receive age |
| RPM ceiling hysteresis | byte at `+0x23`, 1..255 native, at most the ceiling offset |

The built-in production profile is `observe-map1-test`: Map 1 enabled,
`observe` mode, and the controller defaults of the reference model. The
layout declares no hold actuator (`hold_actuator = false`) until the
torque-fraction actuator of #100 exists, and `make preflash` refuses an image
that enables a map in `hold` mode while it is false. The
relocated targets take the built-in `observe` profile with no enabled maps,
and their images receive no Rolling Launch bytes. A strict local TOML profile
can select either mode, any map mask, and every controller field. Every field
is mandatory, unknown fields are rejected, and enabled maps use one-based
numbers. See `rom-builder.md` for the profile schema and build invocation.

RomRaider and XDF expose the per-map enable bits, the pedal requirement as a
switch, and independent calibration tables for the unsigned activation and
controller fields. The signed target offset, the coolant maximum, and the run
and rearm periods stay in the build profile. Raw aggregate records remain
implementation data, not a tuning interface. Generated definitions are
projections of the live JK08A source annotations and layouts.

## Allocation and hooks

Every range names an exclusive end, as `runtime-reservations.md` does.

| Region or address | Size | Purpose |
| --- | ---: | --- |
| `0x000D3860..0x000D38E4` | 132 | periodic, selector-arbiter, and startup wrappers |
| `0x000D38E4..0x000D3EA0` | 1,468 | state engine, gates, and configuration check |
| `0x000D3EA0..0x000D3F60` | 192 | primary ignition-command pass-through |
| `0x000D3F60..0x000D3F80` | 32 | retired configuration span, erased |
| `0x000D40C0..0x000D41E0` | 288 | speed-hold controller |
| `0x000D41E0..0x000D4280` | 160 | dashboard feedback arbiter |
| `0x000D6000..0x000D6040` | 64 | fuel-cut coordinator wrapper |
| `0x000D6040..0x000D6068` | 40 | configuration record |
| `0x000D6068..0x000D60C0` | 88 | RPM ceiling latch |
| `0xFFFF5D40..0xFFFF5D5C` | 28 | runtime state |

Schemas 1 through 3 kept a 32-byte record at `0x000D3F60`. The span stays
claimed and erased inside the Rolling Launch write set, so the registered
historical endpoints keep extracting their record from it. The Map Switching
map copies at `0x000D3F80` leave no room to grow the record in place.

Every registered historical endpoint leaves the RPM ceiling span
`0x000D6068..0x000D60C0` erased, and its signature binds that erased span.
The speed-hold runtime without the ceiling latch, whose state has 24 bytes, is
not a registered endpoint: the builder and `make preflash` classify its images
as an unknown Rolling Launch state and refuse them.
Its schema-4 record holds zero in the hysteresis byte `+0x23`, which is
outside the field contract, so that record is also invalid for the current
runtime.

The composition replaces six declared call targets:

- periodic scheduler entry 1 at `0x00021970`;
- map-selector host at `0x000CE8DC`;
- startup state initialization at `0x00027D28`;
- primary ignition-command consumer at `0x0004E198`;
- dashboard feedback call at `0x000C3FA4`;
- periodic scheduler entry 28 at `0x000219DC`, the fuel-output inhibit
  coordinator.

The dashboard hook redirects the existing map-feedback wrapper call to the
Rolling Launch arbiter. The arbiter invokes that wrapper before applying its
own state. Every wrapper calls its displaced function where required.
Allocation and hook bytes are authoritative only in
`rolling-launch-layout.toml`.

## State and diagnostics

The canonical 28-byte state records phase, abort reason, flags, map/mode
snapshots, run and rearm timers, captured RPM, target speed, the torque
fraction after the rate limit, the speed error, the integrator, the fuel-cut
request, the command before the rate limit, and the RPM ceiling latch; its
last two bytes are reserved and zero. An `ACTIVE` state with a latch other
than 0 or 1 is corrupt. The nine diagnostic views read fixed offsets of that
record.

The flags publish every satisfied gate, `ACTIVE`, hold, and the RPM ceiling
latch. The fuel-cut flag of an active state reports the ceiling request or bit 2,
the active cut bit of the main RPM fuel-cut state byte. The other bits of the
byte leave the flag clear.

Raw engineering DIDs expose nine two-byte views:

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

These DIDs are custom instrumentation, not factory CONSULT parameters. They are
useful only when the diagnostic client can request the raw identifiers and are
not a prerequisite for runtime correctness.

## Composition

`build_rom.py` is the production entry point. It starts from the registered
stock image, installs the current Map Switching composition, applies the
target-specific Rolling Launch stage with the selected profile, adds the CAN
telemetry layer, recalculates all checksum domains, and verifies the final
closed write set.

The composition and assembly modules require the exact base composition and
bind every byte to the declared layout and payload manifests.

The canonical runtime uses `0xFFFF5D40..0xFFFF5D5C` for active state and
`0x000D6000..0x000D60C0` for the fuel-cut wrapper, the configuration record,
and the RPM ceiling latch. The cross-runtime ledger assigns
`0x000D60C0..0x000D6800` and
`0xFFFF6100..0xFFFF6200` exclusively to future Rolling Launch revisions. These
reserves are erased and outside every exact current write set. See
`runtime-reservations.md`.

The implementation inventory is:

| Artifact | Responsibility |
| --- | --- |
| `rolling-launch-layout.toml` | allocation, hooks, diagnostics, and defaults |
| `rolling-launch-payloads.toml` | exact assembled payloads |
| `rolling-launch-engine.s` | state engine, gates, and configuration check |
| `rolling-launch-speed-controller.s` | speed-hold controller |
| `rolling-launch-rpm-ceiling.s` | RPM ceiling latch and request |
| `rolling-launch-ignition-adapter.s` | primary ignition-command pass-through |
| `rolling-launch-feedback.s` | dashboard feedback arbitration |
| `rolling-launch-fuel-cut-wrapper.s` | fuel-cut coordinator wrapper |
| `rolling_launch.py` | independent fail-closed model |
| `rolling_launch_layout.py` | structural validation |
| `rolling_launch_assembly.py` | payload and source-byte validation |
| `rolling_launch_compose.py` | pure in-memory composition |
| `apply_rolling_launch.py` | builder stage: source checks and application |
| `build_rom.py` | production composition and checksum closure |
| `runtime_endpoints.py` | historical endpoint identities and record extraction |
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
   corrupt-state recovery, map isolation, rearm boundary, controller bound,
   and the ceiling latch with its hysteresis.
5. The GNU SH fixture independently executes the same current payload bytes
   across all changed entries, branches, delay slots, call/return paths, and
   boundary cases, with controller expectations taken from the reference
   model.
6. Every final difference is inside the combined component and checksum write
   sets.
7. The generated definition tables agree with the configuration contract.
8. `build_rom.py --verify-only` accepts the exact candidate input and profile.

Software verification does not authorize a flash. The vehicle-speed capture,
the controller, the ceiling latch, corrupt-state recovery, and map changes
while active remain software-only boundaries, and no actuator consumes the
torque fraction. A physical timing claim requires a crank-referenced
measurement, and an injector-pulse claim requires an electrical measurement at
the output path.
