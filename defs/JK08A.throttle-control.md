# JK08A electronic-throttle control

## Scope and evidence boundary

This specification models the stock JK08A path from the dual accelerator-pedal
inputs to the SH7058S ATU-II PWM registers. Function addresses, RAM data flow,
integer transforms, branch predicates, and peripheral-register assignments are
exact-code claims for `1JK08A-20260726-stock.bin`.

The firmware proves two accelerator-pedal channels, two throttle-feedback
channels, two target channels, and two complementary PWM pairs. It does not by
itself prove which code channel is intake bank 1 or bank 2, which polarity opens
the throttle, or which ECM connector terminals reach the motor driver. This
document therefore uses `channel 0` and `channel 1` at the actuator boundary.
The catalog throttle-angle, opening-area, and requested-torque names and their
engineering scales remain candidate physical interpretations where the
structured definition rows say so.

## Stock data path

The normal enabled path is:

```text
AN10 / AN17
  -> 0002862C, 00072B68, 0006E826, 0006EC68
  -> FFFF2672 -> periodic snapshot FFFF266E
  -> 00075590, 00075306, 00075396, 000753D4, 00075540
  -> APP-derived signed request candidate FFFF243C
  -> request-limit candidates and 00071508 / 00070D82 / 00079030
  -> bounded shared signed request FFFF19C6
  -> 00073432 -> stock-active inverse coordinate FFFF198A
  -> 000730FC -> unsigned opening-area-domain request FFFF183E
  -> 00072C3C -> shared target-area word FFFF19B2
  -> 0006F48C -> channel targets FFFF28BC / FFFF28BE
  -> 000CB1CA -> scaled targets FFFF387A / FFFF387C
  -> 000CC720 feedback selection and fixed-point regulator
  -> effort FFFF37B8 / FFFF37BC and direction FFFF369A / FFFF369B
  -> 000CC5F0 / 000CC6A2
  -> duty FFFF374C / FFFF374E and direction masks
  -> 000407C0
  -> BFR6A/B, BFR6C/D at FFFFF510..FFFFF516
```

`FFFF40C6` is not part of the motor-command chain. `000710BC` independently
converts `FFFF183E / 2` through the `0x155A0`/`0x13202` inverse pair and divides
the result by four. It is a derived common opening-coordinate monitor.

## Accelerator-pedal front end

`0002862C` obtains aligned A/D results for AN10 and AN17 from `0002DF5C`, shifts
each result right by six, and publishes 10-bit samples `FFFF362C` and
`FFFF362E`. The adjusted channels are:

```text
pedal_0 = signed(FFFF362C - FFFF55C0)
pedal_1 = signed(2 * FFFF362E - FFFF55C2)
```

`0006EC68` clamps the adjusted channels at zero, normally takes their minimum,
applies mode-controlled substitution and optional rate limiting, and writes
`FFFF2672`. Periodic scheduler `00020DFE` snapshots that word to `FFFF266E`.

`00075590` contains an exact piecewise normalization using the stock words at
`0x8FF2..0x8FF6`:

```text
if FFFF266E <= 45:  FFFF1E6C = 0
if FFFF266E >= 170: FFFF1E6C = 1500
otherwise:          FFFF1E6C = floor((FFFF266E - 45) * 1500 / 125)
```

The normalized word is combined with other bounded offsets and corrections
before `FFFF18F2` is published. `FFFF18F2` is therefore not a pure pedal
percentage.

`00075306` conditionally scales signed `FFFF18F2` through `FFFF19A2`,
`FFFF23FC`, and ROM word `0x944E`, then writes `FFFF19D4`. `00075396` selects
that value or `FFFF19BA` into `FFFF19D0` according to mode and fault flags.

`000753D4` also computes the direct Q15 pedal fraction using stock lower word
`ROM16[0x94E4] = 0` and upper word `ROM16[0x94E8] = 170`:

```text
FFFF18C8 = clamp_u16(floor(FFFF266E * 32768 / 170), 0, 32768)
```

The stock `0x89FB.bit5` is set. The active branch selects the greater of
`FFFF18C8` and the `0x10B0E` lookup, records it in `FFFF19BE`, caps the applied
coefficient at `0xA000`, and applies the signed bounded adjustment to
`FFFF19D0`. The result is `FFFF19D2`. `00075540` normalizes `FFFF19D2`, performs
the inverse conversion through `0xE98E`, RPM axis `0x11D0C`, and coordinate
table `0x14114`, and publishes APP-derived signed request candidate
`FFFF243C`.

## Rotational-speed request limiter

`FFFF243C` is an input to the request-limit subsystem rather than a direct
throttle target. Periodic-table index 11 reaches `0007584E` once per
`00020DFE` scheduler pass. Passive target-CAN timing establishes a period of
`10.24 ms`, or `97.65625 Hz`, for the target ECU.

The exact stock calibration inputs are:

| Address | Stock value | Code role |
|---|---:|---|
| `0x9424` | 76 | Threshold-blend gain, divided by 1024 |
| `0x9426` | 200 | Normal ramp rate, divided by 128 |
| `0x9428` | 1500 | Fast ramp rate, divided by 128 |
| `0x942A` | 2000 | Independent final rate, divided by 128 |
| `0x942C` | 9600 | Base threshold; `0xFFFF` disables the state machine |
| `0x942E` | `0xFFFF` | Optional mode-controlled threshold cap |
| `0x9430` | 0 | Dynamic-threshold decrement |
| `0x9434` | `0xFFFF` | Coolant-latch alternate threshold and decrement floor |
| `0x9436` | 0 | Dynamic-threshold increment |
| `0x943A` | 30 | Recovery-envelope rate for the high-context branch |
| `0x943C` | 50 | Recovery-envelope rate for the other branch |
| `0x943E` | 182 | Auxiliary-request duration |

Words `0x9432=16` and `0x9438=5` are adjacent to this cluster but are not read
by `0007584E`.

If `ROM16[0x942C] == 0xFFFF`, the function writes neutral signed output
`0x7FFF` to `FFFF19D8` and returns. It does not update the filter, dynamic
threshold, ramp, recovery envelope, or auxiliary outputs on that pass.

For the enabled path, let `N=uint16(FFFF11B6)`. The filter update is:

```text
first pass: S_new = min(65535, 4*N), S_blend = S_new
later pass: S_blend = S_entry
            S_new = min(65535, N + floor(3*S_entry/4))
```

`S_new` is stored in `FFFF1794`. Stable input converges to `4*N`; filter error
is multiplied by `3/4` on each pass. At the measured cadence this corresponds
to a 35.6 ms exponential time constant, 24.7 ms half-life, and about 106 ms to
remove 95 percent of a step error.

The coolant-indexed latch in `FFFF249E.bit0` follows:

```text
latch_next = raw_coolant + (16 if latch_entry else 0) >= 255
```

It sets at raw 255, remains set at raw 239, and clears at raw 238. Exact DID
conversion `deg C = raw - 50` gives theoretical boundaries of 205, 189, and
188 deg C. This is not an ordinary warm-engine threshold. The stock alternate
word is also `0xFFFF`, so the latch has no stock effect on the threshold.

The desired threshold is `min(0x942C, 0x9434)` while that latch is set and
`0x942C` otherwise. `FFFF84C3.bit7` gates movement of dynamic threshold
`D=FFFF1796`: a lower desired value subtracts `0x9430` with floor `0x9434`, and
a higher desired value adds `0x9436` with a cap at the desired value. Equality
holds the state. `FFFF4188.bit1` additionally applies `min(D, 0x942E)`. Stock
rates are zero and both alternate caps are `0xFFFF`, so the normal stock state
remains `D=9600`.

The blended threshold is:

```text
L = clamp_u16(S_blend + floor(76 * (D - S_blend) / 1024))
delta = L - S_new
```

The use of `S_blend` from function entry and `S_new` for `delta` is an exact
one-sample split. It materially increases reduction during a rising-speed
transient. At steady speed, a value one count above `D` produces `delta=-1`
because SH-2E arithmetic shifts round negative products down. Below `D`, gaps
of 1 through 13 counts produce `delta=0`; a 14-count gap is the first positive
step. Under the candidate `x*0.78125 RPM` scale, those boundaries correspond to
0.78125 RPM above and 10.9375 RPM below the threshold.

Let `A=FFFF243C`, `O=FFFF19D8` from the previous pass,
`R=FFFF19DA`, and `B(N)` be the first-column forward lookup of `0xE98E` at the
current speed, centered by subtracting `0x8000`. The ramp branch is entered only
when signed `O < A`; equality takes the inactive branch.

On the active branch, a nonpositive `R` sets `FFFF24A3.bit2`. While
`FFFF25B0 != 0` and that bit remains clear, the 1500 fast rate applies and the
intermediate ramp has an additional zero floor. Otherwise the 200 normal rate
applies. Both branches then enforce the `B(N)` lower bound and `0x7FFF` upper
bound:

```text
fast:   R_new = min(0x7FFF, max(B(N), 0, R + floor(1500*delta/128)))
normal: R_new = min(0x7FFF, max(B(N),    R + floor( 200*delta/128)))
```

On the inactive branch, `R` is replaced with `A` when `O < 0x7FFF`,
`FFFF25B0` is loaded with `ROM8[0x8A9B]=100`, and `FFFF24A3.bit2` is cleared.
The independent final term applies on both active and inactive branches:

```text
Q = clamp_s16(R_new + floor(2000*delta/128))
```

Recovery envelope `H=FFFF19DC` tracks `Q` immediately only when `Q < H`,
`Q < A`, and `FFFF1083 > FFFF1082`. Otherwise it increases toward `0x7FFF` by
30 when `FFFF1083 > FFFF1064`, or by 50 otherwise. Output is `min(Q,H)`. If
`H` is more restrictive than `Q`, the function restores `FFFF19DA` to its
entry value so the hidden ramp cannot advance behind the recovery envelope.
The physical identities of the three context bytes remain unresolved.

`FFFF4252.bit1` overrides the result with neutral `0x7FFF` and synchronizes the
ramp from shared request `FFFF19C6`. When the final output is below `A` and
`FFFF1083 > FFFF1082`, the function writes an auxiliary centered request from
the five-word table at `0x14384` and duration `0x943E` to `FFFF2400` and
`FFFF413C`. Otherwise it writes `-0x8000` and zero. The table index is
`min(FFFF1083, 4)` and its stock centered values are
`[1000, 1300, 1300, 1000, 1000]`.

## Shared signed-request arbitration

`00071508` selects the most restrictive signed candidate, `00070D82` publishes
the controller/limiter selection, and `00079030` applies the final signed bounds
before writing `FFFF19C6`.

`00073432` selects or interpolates the current RPM row of `0xE98E` and
inverse-searches two centered values:

```text
FFFF19C6 + 0x8000 -> FFFF198A
FFFF243C + 0x8000 -> FFFF1984
```

The direct `FFFF1984` branch in `000730FC` is guarded by `0x870C.bit7`. The
stock byte is `0x44`, so bit 7 is clear and this optional branch is skipped.
The stock-active request is the shared, already arbitrated `FFFF198A` path.
This distinction prevents the direct APP inverse coordinate from being
mistaken for the normal actuator command.

`000730FC` combines the selected inverse coordinate with its local threshold
and state words, converts it through either the `0x15500`/`0x15690` or
`0x15540`/`0x156D0` pair, applies `FFFF1702` and ROM byte `0x8D8F`, and clamps
the result against the first `0x13202` value and the uint16 boundary. The final
unsigned request is `FFFF183E`.

The rotational-speed request limiter belongs to this same continuous request
chain. It remains independent of the hard fuel-cut mask described in
`JK08A.limiters.md` and `JK08A.fuel-inhibit.md`.

## Executable stock-ROM sweep

`tools/ghidra/EmulateThrottleLimiter.java` executes the unmodified
SHA-256-locked stock instructions at `0007584E`, all declared state-machine
boundaries, and an isolated downstream projection through `00070D82`,
`00079030`, `0003DE4C`, `000730FC`, `00072C3C`, and both calls to `0006F48C`.
The sweep holds speed stable, starts from the APP request, runs 20 limiter
passes or 204.8 ms, and makes all other signed bounds permissive.

The current SHA-locked gate passes 51 state and sweep cases, executes 253522
stock instructions, and emits 28 sweep rows. Its synthetic calibration writes
are restricted to branches that stock-neutral values otherwise make inert.

The resulting signed limiter requests are:

| Candidate RPM | APP 5000 | APP 10000 | APP 20000 | APP 30000 |
|---:|---:|---:|---:|---:|
| 7200 | 5437 | 10437 | 20437 | 30437 |
| 7300 | 5296 | 10296 | 20296 | 30296 |
| 7400 | 5140 | 10140 | 20140 | 30140 |
| 7500 | 5000 | 10000 | 20000 | 30000 |
| 7600 | 2601 | 7601 | 17601 | 27601 |
| 7700 | 466 | 5466 | 15466 | 25466 |
| 7800 | -638 | 3086 | 13086 | 23086 |

Values above APP are neutral in the signed-min arbitration. The exact 7500
row is the transition point under the candidate RPM conversion. The isolated
APP-5000 downstream projection produces symmetric channel targets 1820 at
7200 through 7600, 549 at 7700, and 18 at 7800. This proves executable
composition and both code channels; it is not a vehicle prediction. Real
targets also depend on idle/opening-area additions, learned subtraction,
controller bounds, fault modes, diagnostics, and current feedback.

## Opening-area composition and lift-off behavior

The stock actuator target does not become zero merely because the pedal
candidate reaches its lower end.

`000476A0` forms a saturated upper term:

```text
FFFF133E = sat_u16(FFFF122A * ROM16[0x92FC] >> 13)
```

`000476D2` forms an idle/opening-area base in the same raw domain:

```text
base = lookup(0x1465A, FFFF106F << 8)
correction = lookup(0x1469A, FFFF11BC)
FFFF1340 = min(sat_u16(base + correction), FFFF133E)
```

The exact raw combination and downstream use are code-proven. The catalog
`ISC Opening Area` name and physical scale remain candidate semantics.

With `FFFF24D2.bit0 == 0` and `FFFF24CE.bit2 == 0`, `00072C3C` uses the normal
composition:

```text
FFFF19B2 = clamp_u16(FFFF183E + FFFF1340 - (FFFF120E >> 2))
FFFF19B6 = sat_u16(FFFF183E + FFFF2A1C)
```

The alternate branch converts final channel targets `FFFF28BC` and
`FFFF28BE` back through `0x13202`/`0x155A0` and sums them. That branch is a
mode/fallback feedback path, not the source of the normal request.

`0006F48C` converts the shared `FFFF19B2` area through the same inverse pair,
adds a channel-specific signed correction when its normal controller branch is
selected, and clamps each result. The stock lower target is
`ROM16[0x9574] = 15`. The normal upper target is either
`clamp(raw(0x12DAA) * 13, 908, 2908)` or the fixed
`ROM16[0x9578] * 4 = 2908`, depending on the feature flag. Diagnostic records
`0x6F`/`0x121` and `0x70`/`0x122` can apply stricter caps. The resulting
channel words are `FFFF28BC` and `FFFF28BE`.

Consequently, lift-off response combines at least the shared request,
idle/opening-area base, learned/subtractive term, channel corrections, target
bounds, and diagnostic caps. DFCO entry and hold calibrations decide fuel
state; they do not independently define the throttle target.

## Throttle feedback and regulator

`0003E75A` builds two feedback estimates for each channel from a six-sample
path. Its direct-A/D fallback reads channel 7 for code channel 0 and channel 11
for code channel 1. Exact external sensor and bank identities remain unproven.

The two normalized feedback candidates are:

```text
FFFF2660[i] = clamp_u16(FFFF38A8[i] - 64 * FFFF454E[i] + 0x2000)
FFFF2664[i] = max(0, trunc0((FFFF38E8[i] - 64 * FFFF55B0[i]) / 4) + 0x2000)
```

Here the array notation uses a two-byte stride. `trunc0` means truncation
toward zero, including the explicit add-three correction before the arithmetic
right shift for negative values.

The function-pointer table at `0xCC7DC..0xCC7FC` fixes the per-channel order in
`000CC720`:

1. `000CAFBC` plausibility-selects the two feedback candidates.
2. `000CB078` applies fault/fallback gating.
3. `000CB140` computes feedback magnitude and direction relative to the common
   closed reference `sat_u16(ROM8[0x8CB6] * 64 + 0x2000)`.
4. `000CB1CA` converts `FFFF28BC[i]` to
   `sat_u16(target * 16 + 0x2000)`.
5. `000CB224` selects the normal target or a fault reference.
6. `000CB2B6` computes target magnitude and direction relative to the same
   closed reference.
7. `000CB354` masks target magnitude resolution and applies stock multiplier
   `0x070A`.
8. `000CB41C` selects regulator gains and mode coefficients.
9. `000CB614` executes the stateful fixed-point regulator.
10. `000CC5F0` and `000CC6A2` publish duty and direction for each channel.

`000CB614` reads both feedback and target magnitude/direction pairs, maintains
per-channel state, writes effort magnitude `FFFF37B8`/`FFFF37BC`, and writes
direction `FFFF369A`/`FFFF369B`. Its bounded state at `FFFF2628`/`FFFF262C` is
capped by `ROM32[0x96BC] = 0x000D0000` and is snapshotted to
`FFFF2630`/`FFFF2634` for the next pass. The state word is not the motor duty
and is not a simple instantaneous error.

`000CC5F0` reads the effort magnitude with the unsigned `0xE0` offset from base
`FFFF36D8`, which resolves to `FFFF37B8`/`FFFF37BC`. It shifts the magnitude
right by six, applies the `FFFF39B0` supply-compensation divisor derived with
`ROM16[0x933A]`, clamps the intermediate command to 500, then applies the
stock literal cap 490. The output words are `FFFF374C` and `FFFF374E`.
`000CC6A2` translates regulator direction values `-0x10` and `0x0F` into the
bit masks at `FFFF36DC` and `FFFF385E`.

## ATU-II PWM boundary

`000407C0` converts each duty word to the timer domain:

```text
pwm = min(320, floor(duty500 * 320 / 500))
```

It writes one member of each complementary pair and clears the other according
to the two direction masks. Disabled output clears all four words. A separate
fault branch writes fixed `0x40` and `0x60` values with polarity selected by an
engine-state comparison.

| Code channel | Register pair | MCU output pins | Package pins |
|---|---|---|---|
| 0 | `FFFFF510` BFR6A, `FFFFF512` BFR6B | TO6A/PB0, TO6B/PB1 | 145, 146 |
| 1 | `FFFFF514` BFR6C, `FFFFF516` BFR6D | TO6C/PB2, TO6D/PB3 | 147, 149 |

The register names, addresses, ATU-II channel, port functions, and package-pin
numbers come from the local Renesas SH7058S/SH7059 hardware manual. Continuity
from those package pins through the ECM board, H-bridge, connector, and each
throttle motor remains a bench-measurement boundary. Neither bank assignment
nor opening polarity is asserted in the definition layer.

## Calibration implications

- `0x942C` can reduce the shared throttle/airflow request before the hard fuel
  cut, but it is not a fuel-cut threshold.
- `0x1465A`, `0x1469A`, `0x92FC`, `FFFF120E`, and the lower/upper target bounds
  participate in the lift-off target even when the APP-derived request is at
  its minimum.
- `0x12DAA` bounds the per-channel target. Its catalog degree scale is not
  sufficient evidence for direct editing because the code applies a raw
  multiply and clamps before the actuator regulator.
- `FFFF40C6` is suitable as a common derived opening monitor, but it cannot be
  used as proof of the per-channel motor command or actual plate position.
- Any instruction patch in this path requires the mandatory exact-byte SH-2E
  executable gate. Calibration-only experiments still require controlled
  hardware validation because channel identity, polarity, and physical scales
  are not all code-proven.
