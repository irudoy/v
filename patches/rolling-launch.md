# Rolling Launch runtime

Rolling Launch is an optional runtime layered on the complete five-slot
Map Switching composition. While CANCEL is held it captures vehicle speed as
the hold target and runs a speed-hold controller that publishes a torque
fraction `u`. Hold mode withholds the dwell of a fraction `1 - u` of the
eligible ignition events through a wrapper of the `GR11A` spark handler. It
also latches an all-cylinder fuel-cut request above the captured engine speed
plus a ceiling offset and releases it below a hysteresis, and a wrapper of the
stock fuel-output inhibit coordinator merges the request into the final
cylinder mask. It runs
on the exact `7mfk` images JK00A, JK03A, JK03B, and JK08A. The relocated
targets JK00C, JK00D, JK78C, 1ND0A, 1ND3B, and 1ME3B carry no Rolling Launch
runtime.

The authoritative implementation sources are:

- `rolling-launch-layout.toml` for ROM/RAM ownership, hooks, and diagnostics;
- `rolling-launch-payloads.toml` for exact assembled payload bytes;
- `rolling_launch.py` for the independent state, calibration, and controller
  model;
- `hardware-results.toml` for immutable image identities and hardware outcomes.

The canonical JK08A runtime is software-verified. In hold mode the spark-cut
actuator under "Speed-hold cut actuator" consumes the torque fraction, and the
RPM ceiling request remains the hard limit. The vehicle evidence of the hold,
the spark cut included, is under "Vehicle evidence of the hold".

The target-vehicle evidence below comes from exact local combined images of
the registered historical endpoint `schema-3-fuel-shadow-hold`, which held RPM
through the fuel-cut shadow of the selected map. It qualifies button decoding,
dashboard states, repeated rearm, and the full software fuel-inhibit mask. The
vehicle-speed capture, the controller, the coordinator wrapper, the ceiling
request, and the spark cut are outside that endpoint; their vehicle evidence
is under "Vehicle evidence of the hold". Physical spark timing and electrical
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

1. The 72-byte configuration record and its five map slots are
   structurally valid.
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

### Vehicle evidence of the hold

`hardware-results.toml` records the 2026-11-03 session of the v2 hold image
on Map 3 under `rolling_launch.v2_hold_vehicle_2026_11_03`: stationary holds
in neutral and moving holds in second and third gear, each capture with a
dashboard recording and a TRC. Every hold passes the hold audit: the published
torque fraction follows the model, the cut counter lies inside the cuts that
the fractions owe, and no fuel mask or cut appears outside `ACTIVE`. At
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
session, so the misfire-monitor blanking holds through the cut.

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
physical torque. The veto counter provides ECU-side release timing between
adjacent coherent snapshots. Phase is a fixed field of page 2 and is current
every tick. In every TRC-covered hold, the counter is constant after the
first non-ACTIVE snapshot through the following inactive interval. An
increment ending at that first snapshot spans the phase transition, rather
than proving a veto after it.

The last-veto intervals on the first-page capture clock extend beyond one
four-stroke engine cycle after the raw released `0x239` frame in some holds.
The stable input `0xFFFF2A85` is not logged: the MLG button channel is host
context from `0x239`, sampled at group completion. A `BUTTON_RELEASED`
abort bounds acceptance of the stable release between the last ACTIVE and
first non-ACTIVE snapshots. Gate aborts `PEDAL_LOW` and `RPM_LOW` precede
acceptance, since the released input overrides those reasons. Under this
runtime contract, the observed veto ends within one snapshot interval of
acceptance, or before it. The post-frame counts belong to the interval
before or ending at the phase exit; no continued veto after the first
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

| Mode | Torque fraction | Ignition events | Fuel cut |
| --- | --- | --- | --- |
| `observe` | computed and published | unchanged | unchanged |
| `hold` | computed and published | dwell of a fraction `q` of eligible events withheld; fired events carry the trim of the map slot | all-cylinder request latched above the RPM ceiling |

## Speed-hold controller

Activation captures the vehicle speed and native RPM of the activation tick:

```text
target = clamp(speed + target_offset, 0, 0xFFFF)
```

Speeds are km/h*10. The torque fraction `u`, the command, and the cut
fraction `q` are thousandths; the integrator holds sixteenths of one
thousandth. Activation sets `u = 1000`, `q = 0`, and empties the
integrator. `integral_gain`, `max_trim` (`z`), and `trim_efficiency`
(`eff`) belong to the slot of the map snapshot of the activation. On the
activation tick and on every `ACTIVE` tick that passes its gates and the
run timer, the controller computes:

```text
e = speed - target
u_p = clamp((window_top - e) * 1000 // window_width, 0, 1000)
step = -(integral_gain * e)
step = 0 if (u_p + I // 16 <= 0 and step < 0)
         or (u_p + I // 16 >= 1000 and step > 0)
I = clamp(I + step, -16 * integrator_limit, 16 * integrator_limit)
command = clamp(u_p + I // 16, 0, 1000)
u = clamp(command, u - rate_limit, u + rate_limit)
q = 1000 - min(1000, 1000 * u // eff)
```

The proportional fraction is full torque while `e <= window_top - window_width`,
zero while `e >= window_top`, and linear between. The integrator falls
while the speed is above the target, rises while it is below, and freezes
while its step would deepen a saturated sum. The stock unsigned divider
`0x00021CE0` forms both quotients. The state record publishes `e`, `I`, the
command, `u`, and `q`. The controller runs only on ticks whose speed error
lies inside the abort window `-abort_below <= e <= abort_above`.

The fired events of a trimmed slot deliver the fraction `eff` of their
torque, so the cut fraction compensates: the delivered torque
`(1 - q) * eff` equals `u` while `u <= eff`, and every event fires at
`u >= eff`. A slot without trim stores `eff = 1000`, and `q = 1000 - u`.
The builder derives `eff` from the stock spark-efficiency pair
`0x00011D24`/`0x0001199E`:

```text
eff = (256 - F(z)) * 1000 // 256
```

`F` interpolates the 16-point table linearly with a truncated result
(`F(20) = 45`, `eff = 824`). `make preflash` refuses an image whose stored
efficiency differs from the pair in that image and names the command that
rederives the hidden value after editor changes:

```bash
uv run python patches/refresh_rolling_launch.py tmp/edited.bin \
  --output tmp/ready.bin
```

The command changes only the efficiency words and checksums, then requires a
byte-identical stock rebuild with the image's calibration. Independent invalid
settings and unknown or partial runtimes are refused. `make preflash` still
requires a clean commit, its green Verify run and executable qualification.
The efficiency stays hidden in the editors: a manual paired field can diverge
from the trim, and a fixed list of F nodes becomes stale when F is calibrated.
Deriving it from the actual image avoids both inconsistencies. Calibration
transfer derives the words after applying the F-table bytes as well.

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

The adapter at the primary ignition-command hook `0x0004E198` applies the
retard trim of the map slot and tail-jumps to the stock consumer
`0x0002A892`:

```text
command = max(stock, min(stock + z, floor_command))
```

The APC command counts retard, and the timing is `110 - command` degrees,
so `floor_command` 120 limits the trim to 10 degrees ATDC. The adapter
keeps the stock command outside an `ACTIVE` hold, while the P0335 APC
fallback `0xFFFF24C9.bit6` is set, and for a map snapshot outside Maps 1
through 5; it never advances the timing. It changes `r0..r4` only, and
every other argument register reaches the stock consumer unchanged.

The stored efficiency assumes the full trim. When the floor clips the
trim (`stock + z > floor_command`), the applied retard is smaller than `z`,
the fired events deliver more than `eff`, and the cut withholds more events
than the delivered torque needs. The speed loop absorbs the difference, and
the hold audit reports the clipped ticks of every run.

## Speed-hold cut actuator

In hold mode a wrapper of the `GR11A` spark handler consumes the torque
fraction: it withholds the dwell of selected ignition events. The
fuel-inhibit mask through the coordinator wrapper remains the hard limit and
the abort path. The runtime runs on the `7mfk` layout; the other
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
interrupts masked. The P0335 APC fallback scheduler reads `0xFFFF8511` in
`0x0002B768` and in the fallback branch of `0x0002AF38`, which arms a dwell while
`0xFFFF24C9.bit6` and bit 5 or 6 of `0xFFFF8518` are set and enables the high
byte only while `0xFFFF8511.bit7` is clear (`0x0002B344..0x0002B358`). Every
cut point therefore passes all events through while `0xFFFF24C9.bit6` is set.

### Cut point

The veto is set from the `GR11A` spark handler. The table lists it with the
two alternative points:

| Cut point | Veto delivery | Authority | Decision latency | Patch footprint |
| --- | --- | --- | --- | --- |
| Spark handler (chosen): table entry `0x000202E4` redirected to a wrapper that branches to `0x0002AB24` | No `GR11B` match falls between a spark and the dwell start of its successor, so the veto reaches the dwell of the successor that the handler writes to `0xFFFF13D3`. Above about 110 degrees of dwell the successor can be armed before the spark, and that event fires. | Every event | The preceding spark, 120 crank degrees before the target spark | One table word and a wrapper in the `GR11A` interrupt |
| Countdown divider: literal `0x000296C0` redirected to a wrapper that tail-calls `0x00021CE0` | The divider call runs at mask 8 and the `GR11B` match at level 8, so no `GR11B` service falls between the wrapper and the mask-15 section. | Every event | The arming tooth, within 10 degrees of the dwell start | One literal word and a wrapper in the crank-tooth interrupt, run at every countdown expiry |
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

All three points use the same stock veto and the same ignition output
("Ignition output hardware"). `0x00028D3C` writes `0x8FFF` to `IPRJ`
(`0xFFFFED12`), which places ATU channel 11 at level 8: `IMI11A`, the
`GR11A` match at vector 184 and table entry `0x000202E4`, and `IMI11B`, the
`GR11B` match at vector 186 and table entry `0x000202EC`, with
`VBR = 0x00020004`. A `GR11B` match therefore cannot preempt the spark
handler. An interrupt above level 8 can delay it, and a spark handler delayed
past the arming of the next dwell meets the same edge case as a large dwell
angle.

The spark handler uses the same stock veto and failure direction as the
countdown divider, adds no code to the crank-tooth interrupt, has no `GR11B`
service in its veto window, and redirects the table entry of a handler that
has no other caller. The countdown divider is not used because its wrapper would run at every
countdown expiry inside the crank-tooth interrupt. The ignition hook is not used because its authority depends on the
spark and dwell angles. The edge case of the spark handler needs a dwell
angle above about 110 degrees, and a log of `0xFFFF237A` over the hold range
shows whether the hold reaches it. Above 120 degrees the `GR11B` match of the
successor precedes the spark, so the veto passes to the following arming and
the cut moves by one cylinder; the wrapper sets no veto above about 110
degrees, which keeps the cut accounting per cylinder.

### Cut selection

The wrapper at `0x000D60C0` enters from table entry `0x000202E4` at interrupt
level 8, saves `r0..r7` and `SR`, and restores them before it branches to
`0x0002AB24`. It restores `r0` in the delay slot of that branch, so the stock
handler receives the machine state of its entry. It runs without loops.

A `GR11A` match without `0xFFFF8517.bit7` is a forced timeout match and passes
through unchanged. In an `ACTIVE` hold with `q <= 1000`, a spark is eligible
with the sync bit `0xFFFF8501.bit7`, without the P0335 APC fallback
`0xFFFF24C9.bit6`, with the dwell angle `0xFFFF237A` at most 110 degrees, and
with an event cylinder `0xFFFF13C9` of 1..6. The veto at the match of event
cylinder `c` withholds the dwell of its successor `ROM8[0x22680 + c]`, a
bijection, so the balance per event cylinder is the balance per cut cylinder.

Six accumulators, one per event cylinder, count sixths of a thousandth of a
cut:

```text
acc[c] = acc[c] + 6 * q
cut    = acc[c] >= 6000
acc[c] = acc[c] - 6000 if cut
```

Outside an `ACTIVE` hold, for `q > 1000`, and at an eligible match whose
accumulator holds 6000 or more, every accumulator returns to its offset
`1000 * k + 250`, with `k = (0, 2, 4, 1, 3, 5)` for event cylinders 1..6. The
offsets differ by exact sixths in firing order, so over whole engine cycles
the cuts total those of one accumulator. For every `q` and every start
cylinder the cuts of an aligned 36-event period are within one of
`36 * q / 1000`, those of any 36 consecutive eligible events within three,
and those of every cylinder within one of the mean. The bound of 36
consecutive events holds with a margin of 0.016 events (2.984 at
`q = 556`), so a change of the offsets requires the full sweep over every
`q` and every start cylinder again. A single accumulator would cut the same cylinders whenever `q` is a
multiple of 1/6. An ineligible match leaves every accumulator unchanged, so
the cut fraction applies to eligible events.

A cut sets `0xFFFF8511.bit7` with interrupts masked and increments the
wrapping cut counter. The first match that sees the state leave `ACTIVE` sets
no veto and resets the accumulators. At most one carried-over event follows:
the successor dwell vetoed at the preceding spark, because `0x0002AF38` is the
only writer of `0xFFFF8511` and the runtime never clears it.

`u = 0` cuts every eligible event. The run timeout bounds every hold (default
781 ticks, 7.997 s), and the rearm period separates holds (default 98 ticks,
1.004 s).

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
because no readiness condition reads the inhibit mask or the DFCO state.
During an `ACTIVE` hold the spark wrapper stores the marker `0x01` into latch
`0xFFFF436F` at every armed match that finds the latch zero. The readiness
gate then fails, which clears bits 6 and 7 of `0xFFFF4251` and the P030
working state. The wrapper counts the armed matches outside `ACTIVE` in the
quiet-event byte, which saturates at 255. In `IDLE`, once that count reaches
14, it clears the latch only while the latch holds `0x01`, so a stock value is
never overwritten. The P030 metrics span thirteen event periods, and the
carried-over veto of the first match outside `ACTIVE` is the last cut, so the
latch stays held for at least thirteen events after the last cut.

The stock writer at `0x00082FC8` in `0x00082C8A` stores calibration byte
`ROM8[0x00008C2E]` (`0x32` in stock) with a plain `MOV.B`. The calibration
transfer and `make preflash` refuse a calibration that sets that byte to
`0x01`. Both check-and-stores of the wrapper run in the `GR11A` interrupt with
interrupts masked, so neither interleaves with the stock writer.

## Configuration

The strict 72-byte schema-5 record has a 40-byte head and five 6-byte map
slots at `+0x28`. The head contains:

| Field | Contract |
| --- | --- |
| magic, inverse, end marker | fixed integrity sentinels |
| schema | version 5 |
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
| reserved word `+0x16` | zero |
| integrator limit | 0..1000 thousandths |
| abort above/below | nonzero bytes, km/h*10 |
| RPM ceiling offset | nonzero native value |
| run timeout and rearm | 1..0x7FFF ticks |
| speed-frame age limit | 1..254 counts of the stock receive age |
| RPM ceiling hysteresis | byte at `+0x23`, 1..255 native, at most the ceiling offset |

Slot `n` at `+0x28 + 6 * n` belongs to Map `n + 1`, and the end marker
`0xA55A` follows the last slot at `+0x46`:

| Slot field | Contract |
| --- | --- |
| integral gain | signed word, 0..0x7FFF |
| max trim | byte, 0..40 APC command counts |
| floor command | byte, the latest APC command of the trim |
| trim efficiency | word, 1..1000 thousandths; 1000 when the trim is zero |

The built-in production profile is `hold-map1-test`: Map 1 enabled, `hold`
mode, and the controller defaults of the reference model. The layout declares
the spark-cut hold actuator (`hold_actuator = true`); `make preflash` refuses
an image that enables a map in `hold` mode while that field is false. The
relocated targets take the built-in `observe` profile with no enabled maps,
and their images receive no Rolling Launch bytes. A strict local TOML profile
can select either mode, any map mask, every controller field, and the slot
fields as a scalar or a list of five values. Every head field is mandatory,
unknown fields are rejected, and enabled maps use one-based numbers. The
builder writes the trim efficiency of each slot from the stock
spark-efficiency pair. See `rom-builder.md` for the profile schema and build invocation.

RomRaider and XDF expose the per-map enable bits, the pedal requirement as a
switch, and independent calibration tables for the unsigned activation and
controller fields. Each map slot exposes Ki at `+0`, maximum trim at `+2` in
degrees, and the timing floor at `+3` in degrees ATDC. Its display is
`floor_command - 110`, with inverse `ATDC + 110`; negative values are before
TDC. The gain is limited to 0..32767, and the trim to 0..40. The derived word at
`+4` is hidden and must be refreshed after changing the trim or F, including
when a trim is disabled. Slot addresses derive from the configuration address
of the runtime layout and the schema-5 slot offset and stride.
The signed target offset, coolant maximum, and run and rearm periods stay in
the build profile. Raw aggregate records remain
implementation data, not a tuning interface. Generated definitions are
projections of the live JK08A source annotations and layouts.

## Allocation and hooks

Every range names an exclusive end, as `runtime-reservations.md` does.

| Region or address | Size | Purpose |
| --- | ---: | --- |
| `0x000D3860..0x000D38E4` | 132 | periodic, selector-arbiter, and startup wrappers |
| `0x000D38E4..0x000D3EA0` | 1,468 | state engine, gates, and configuration check |
| `0x000D3EA0..0x000D3F60` | 192 | primary ignition-command trim adapter |
| `0x000D3F60..0x000D3F80` | 32 | retired configuration span, erased |
| `0x000D40C0..0x000D41E0` | 288 | speed-hold controller |
| `0x000D41E0..0x000D4280` | 160 | dashboard feedback arbiter |
| `0x000D6000..0x000D6040` | 64 | fuel-cut coordinator wrapper |
| `0x000D6040..0x000D6068` | 40 | retired schema-4 configuration span, erased |
| `0x000D6068..0x000D60C0` | 88 | RPM ceiling latch |
| `0x000D60C0..0x000D6220` | 352 | spark-cut actuator |
| `0x000D6220..0x000D6268` | 72 | configuration record |
| `0x000D6268..0x000D62B8` | 80 | map-slot validator |
| `0x000D62B8..0x000D6320` | 104 | trim cut-fraction unit |
| `0xFFFF5D40..0xFFFF5D6C` | 44 | runtime state |

Schemas 1 through 3 kept a 32-byte record at `0x000D3F60`, and schema 4 a
40-byte record with one integral gain for every map at `0x000D6040`. Both
spans stay claimed and erased inside the Rolling Launch write set, so the
registered historical endpoints keep extracting their records from them.
Extraction maps a schema-4 record to five slots with its gain and no trim. The Map Switching
map copies at `0x000D3F80` leave no room to grow the record in place.

Every registered historical endpoint leaves the slot-validator and trim span
`0x000D6268..0x000D6320` erased. The endpoints before schema 4 also leave
the RPM ceiling span `0x000D6068..0x000D60C0` and the spark-cut span
`0x000D60C0..0x000D6220` erased and the `GR11A` table entry at the stock
handler. Every signature binds those bytes.
The speed-hold runtime without the ceiling latch, whose state has 24 bytes, is
not a registered endpoint: the builder and `make preflash` classify its images
as an unknown Rolling Launch state and refuse them.
Its schema-4 record holds zero in the hysteresis byte `+0x23`, which is
outside the field contract, so that record is also invalid for the current
runtime.

The composition replaces seven declared targets:

- periodic scheduler entry 1 at `0x00021970`;
- map-selector host at `0x000CE8DC`;
- startup state initialization at `0x00027D28`;
- primary ignition-command consumer at `0x0004E198`;
- dashboard feedback call at `0x000C3FA4`;
- periodic scheduler entry 28 at `0x000219DC`, the fuel-output inhibit
  coordinator;
- `GR11A` interrupt-table entry at `0x000202E4`, the spark handler
  `0x0002AB24`.

The dashboard hook redirects the existing map-feedback wrapper call to the
Rolling Launch arbiter. The arbiter invokes that wrapper before applying its
own state. Every wrapper calls its displaced function where required.
Allocation and hook bytes are authoritative only in
`rolling-launch-layout.toml`.

## State and diagnostics

The canonical 44-byte state records phase, abort reason, flags, map/mode
snapshots, run and rearm timers, captured RPM, target speed, the torque
fraction after the rate limit, the speed error, the integrator, the fuel-cut
request, the command before the rate limit, the RPM ceiling latch, and the
cut fraction `q` at `+0x1A`. The spark-cut actuator owns
`+0x1C..+0x2C`: the quiet-event count, the cut counter, a reserved zero word,
and the six accumulators. Corrupt-state recovery clears the first 28 bytes,
and the startup wrapper clears all 44. An `ACTIVE` state with a latch other
than 0 or 1 is corrupt. The diagnostic views read fixed offsets of that
record.

The flags publish every satisfied gate, `ACTIVE`, hold, and the RPM ceiling
latch. The fuel-cut flag of an active state reports the ceiling request or bit 2,
the active cut bit of the main RPM fuel-cut state byte. The other bits of the
byte leave the flag clear.

Raw engineering DIDs expose two-byte views of the state:

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
| `0x121E` | fuel-cut request |
| `0x121F` | command before the rate limit |
| `0x1231` | RPM ceiling latch |
| `0x1232` | quiet-event count (high byte) and cut counter (low byte) |

Every view uses a free pointer slot of the service `0x22` table of family
`0x12`, whose records outside the low bytes `0x00`, `0x20`, and `0x40`
answer two bytes. Every historical endpoint publishes the views `0x1211`
to `0x1229` and leaves the slots of `0x121D`, `0x121E`, `0x121F`,
`0x1231`, and `0x1232` stock.

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

The canonical runtime uses `0xFFFF5D40..0xFFFF5D6C` for active state and
`0x000D6000..0x000D6320` for the fuel-cut wrapper, the RPM ceiling latch,
the spark-cut actuator, the configuration record, the slot validator, and
the trim unit. The cross-runtime ledger assigns `0x000D6320..0x000D6800` and
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
| `rolling-launch-spark-cut.s` | spark-cut actuator and misfire latch |
| `rolling-launch-ignition-adapter.s` | primary ignition-command trim adapter |
| `rolling-launch-trim.s` | map-slot validator and trim cut fraction |
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
   the map slots, the trim cut fraction and ignition command, the ceiling
   latch with its hysteresis, and the cut selection, eligibility, resets,
   and misfire latch of the spark-cut actuator.
5. The GNU SH fixture independently executes the same current payload bytes
   across all changed entries, branches, delay slots, call/return paths, and
   boundary cases, with controller expectations taken from the reference
   model, including the slot validator, the trim unit against a table of
   model cut fractions, and the ignition adapter against a table of model
   commands. The spark wrapper runs through `TRAPA` and the composed `GR11A`
   table entry against a C reference of the cut selection, which checks every
   register, `SR` at the stock handler entry, and the per-period cut
   bounds.
6. Every final difference is inside the combined component and checksum write
   sets.
7. The generated definition tables agree with the configuration contract.
8. `build_rom.py --verify-only` accepts the exact candidate input and profile.

Software verification does not authorize a flash. The vehicle-speed capture,
the controller, the ceiling latch, the spark cut, corrupt-state recovery, and
map changes while active remain software-only boundaries. A physical timing claim requires a crank-referenced
measurement, and an injector-pulse claim requires an electrical measurement at
the output path.
