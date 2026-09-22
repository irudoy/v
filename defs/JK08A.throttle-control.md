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
| `0x943A` | 30 | Recovery-envelope rate when target gear is above TCM gear phase |
| `0x943C` | 50 | Recovery-envelope rate for every other gear relation |
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
step. Under the vehicle-confirmed `x*0.78125 RPM` scale recorded in
[`JK08A.limiters.md`](JK08A.limiters.md#rotational-speed-request-limiter), those
boundaries correspond to 0.78125 RPM above and 10.9375 RPM below the threshold.

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
Initializer `0002C648` loads the same value. A whole-program census found no
other writer or computed-address candidate for `FFFF25B0`; it is not a
countdown. Under the recovered stock lifecycle it remains nonzero, while
`FFFF24A3.bit2` alone switches from the fast rate to the normal rate after a
nonpositive-ramp transition.

The independent final term applies on both active and inactive branches:

```text
Q = clamp_s16(R_new + floor(2000*delta/128))
```

Recovery envelope `H=FFFF19DC` tracks `Q` immediately only when `Q < H`,
`Q < A`, and target gear index `FFFF1083` is greater than current gear index
`FFFF1082`. Otherwise it increases toward `0x7FFF` by 30 when target gear is
greater than TCM gear-phase index `FFFF1064`, or by 50 otherwise. Output is
`min(Q,H)`. If `H` is more restrictive than `Q`, the function restores
`FFFF19DA` to its entry value so the hidden ramp cannot advance behind the
recovery envelope.

The three indices have exact CAN bindings:

- CAN `0x174` payload byte 3 high nibble is target gear and the low nibble is
  current gear. Nibble values 1 through 7 become zero-based indices 0 through
  6; every other value becomes zero.
- CAN `0x177` payload byte 2 bits 0 through 2 form the zero-based TCM
  gear-phase index.
- `00020DFE` snapshots the live decoded bytes into `FFFF1083`, `FFFF1082`, and
  `FFFF1064` before the limiter consumes them.

Passive target transitions `0x44 -> 0x34 -> 0x33` and
`0x22 -> 0x32 -> 0x33` establish that the high nibble changes first for both
downshifts and upshifts. In stable gears the `0x177` low-three-bit value equals
current gear minus one; during a shift it changes after the target nibble and
before the current nibble. This proves an operational phase index but does not
identify the exact mechanical engagement boundary.

`FFFF4252.bit1` overrides the result with neutral `0x7FFF` and synchronizes the
ramp from shared request `FFFF19C6`. When the final output is below `A` and
`FFFF1083 > FFFF1082`, the function writes an auxiliary centered request from
the five-word table at `0x14384` and duration `0x943E` to `FFFF2400` and
`FFFF413C`. Otherwise it writes `-0x8000` and zero. The table index is
`min(FFFF1083, 4)` and its stock centered values are
`[1000, 1300, 1300, 1000, 1000]`.

The stock-selected producer `00077892` sets `FFFF4252.bit1` only when all of
these conditions hold:

```text
FFFF418F.bit4 == 1
FFFF1082 != FFFF1083
FFFF4253.bit6 == 0
```

`FFFF4253.bit6` is a separately calculated transition-inhibit aggregate.
`FFFF418F.bit4` is the scheduler latch of `FFFF419B.bit4`: `00020DFE` copies
`FFFF4194..FFFF419F` to `FFFF4188..FFFF4193` every pass, and `0007724C` sets
`FFFF419B.bit4` exactly when TCM field `FFFF3A2E`, CAN `0x174` byte 4 bits 5
through 7 decoded by `000C47EA`, equals 3. Primary startup clears `FFFF418F`,
and its direct writers change bits 0 and 1 only. The forced-neutral branch is
therefore active only on a pass that follows TCM field value 3; the 2026-09-22
road captures carry that value in 4-3 and 3-2 downshifts at 2200..3987.5 RPM
([`JK08A.can.md`](JK08A.can.md#transmission-request-interface)). It is a
transition mismatch condition rather than an upshift-only condition;
direction-specific behavior uses the separate `target > current` comparisons
above.

## Secondary use of `0x942C`

Stock-selected transmission coordinator `00077892` also reads `0x942C`. It
derives a gear-indexed unsigned value from `FFFF10E6` and table `0x15212`, caps
that value at `0x942C`, floors it at `0x94B2=0x0500`, stores it in
`FFFF32EC`, and subtracts `4*FFFF11B6` before building signed candidate
`FFFF4162`.

The downstream activation chain is exact:

```text
0x942C -> FFFF32EC -> FFFF4162
  -> 000777FA while FFFF41A6.bit3 is set
  -> FFFF3480 / FFFF3484
  -> 00079030 -> FFFF19C6
```

Before common completion, `00077892` sets `FFFF41A6.bit3` only when
`FFFF4252.bit1` is set or retained byte `FFFF4413` is nonzero. It writes
`FFFF4413=ROM8[0x8B07]=0x1E` only on the same bit-1 branch, startup clears the
byte, and `0002040C` decrements it with its 10.24 ms byte block, so bit 3 stays
set for 307.2 ms after the last bit-1 pass. Both prerequisites follow TCM field
`FFFF3A2E == 3` through latch `FFFF418F.bit4`, so the secondary candidate
constrains `FFFF19C6` only during such an episode and its hold. The 2026-09-22
road captures carry the field value in 4-3 and 3-2 downshifts, and
`FFFF19C6` lies below the pre-limiter request in 80 passes inside those
episodes ([`JK08A.can.md`](JK08A.can.md#transmission-request-interface)). A
calibration-only `0x942C` A/B test is isolated from this secondary path only
outside such episodes and their holds, and only while external diagnostics or
another patch do not mutate these state bytes.

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

## Requested-torque conversion coordinates

`0xE98E` and its trustful copy `0x175C8` are 16x16 offset-binary surfaces.
Row axes `0x11D0C` and `0x18716` hold byte points, and column axes `0x14114`
and `0x18AC6` hold uint16 points. Each trustful table, axis, and constant named
in this section equals its primary counterpart byte for byte in the stock ROM.

`0003DE4C` writes both row coordinates on every pass:

```text
FFFF1702 = max(32, FFFF11B6)
FFFF1CCA = max(32, FFFF11D0)
```

`FFFF11B6` and `FFFF11D0` are scheduler snapshots of
`FFFF11EE = FFFF1196 >> 4 = floor(2000000 / FFFF11FC)` and `FFFF1208`.
`000385BC` computes
`FFFF1208 = floor(floor(12000000 / (ROM8[0x88FB] * FFFF22D4)) / 2)` with
`ROM8[0x88FB] = 3`. `00028B5C` samples `FFFF22D4` from the same capture and
under the same gates as `00028AF8` samples `FFFF11FC`, and `0002B768`,
`0002C648`, and `00099A48` store one value to both words, so `FFFF22D4` equals
`FFFF11FC` and `FFFF1208 = floor(2000000 / FFFF11FC)`. Both row coordinates
are therefore engine speed in 3.125 RPM counts, clamped at 100 RPM.

Wrappers `000262E0` and `00026660` pass the row coordinate to byte cores
`00026A0C` and `00026BC4`, which multiply every stored axis point by 16 before
the comparison. Inverse lookups `00073432` and `00073628` apply the same
multiplication. One stored row-axis count is therefore 50 RPM, and the row
points decode to 800 through 6400 RPM in 400 RPM steps and 7200 RPM. Every
forward lookup of `0xE98E` passes `FFFF1702` as the row input except
throttle-rev limiter `0007584E`, which passes `FFFF11B6`; the two differ only
below 100 RPM. Every lookup of `0x175C8` passes `FFFF1CCA`.

`00073948` forms the forward column coordinate from first-channel word
`FFFF1332`:

```text
FFFF12A0 = min(0xFFFF, 2 * area(min(0xFFFF, 4 * FFFF1332)))
FFFF1824 = floor(4 * floor(FFFF12A0 * 65536 / ROM8[0x8D8F]) / FFFF1702)
FFFF1980 = lookup(0x15690 over 0x15500, FFFF1824)
             while FFFF1824 <= ROM16[0x1553E]
FFFF1980 = lookup(0x156D0 over 0x15540, min(0xFFFF, FFFF1824 >> 4))
             otherwise
FFFF19BA = lookup(0xE98E, row FFFF1702, column FFFF1980) + 0x8000
```

`area(x)` interpolates `0x13202` over `0x155A0`. `ROM8[0x8D8F] = 100`, and
`ROM16[0x1553E] = 45187` is the last point of `0x15500`. With `FFFF1702` in
3.125 RPM counts, `FFFF1824 = 8192 * FFFF12A0 / RPM`: the column input is an
opening area divided by engine speed. `00073A44` writes `FFFF1CA8`,
`FFFF1CE0`, `FFFF1D0E`, and `FFFF1D1A` with the same formulas over row
`FFFF1CCA`, tables `0x18766`/`0x190D0`, `0x18FD6`/`0x18E86`, and
`0x18F96`/`0x18E46`, and constants `ROM8[0x15F82]` and `ROM16[0x18EC4]`.

The inverse direction uses the same rows. `00073432` produces `FFFF198A` and
`FFFF1984` as described above, and `00073628` inverse-searches the
`FFFF1CCA` row of `0x175C8` for `FFFF19C6 + 0x8000` and writes `FFFF1D14`.

Other consumers evaluate the surfaces at fixed or locally formed columns.
`000702C6`, `00075540`, `00075C48`, and `0007AB18` read `0xE98E`, and
`000749BC` reads `0x175C8`, at column `0xFFFF`, the last column; `0007584E`
reads `0xE98E` at column 0. `000753D4` and `00074728` convert the first area
point, `ROM16[0x13202]` or `ROM16[0x18766]`, through the lower segment over the
current row coordinate, and `0007A9FC` and `0007ACB4` form their column inputs
through the same lower-segment conversion.

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

| RPM | APP 5000 | APP 10000 | APP 20000 | APP 30000 |
|---:|---:|---:|---:|---:|
| 7200 | 5437 | 10437 | 20437 | 30437 |
| 7300 | 5296 | 10296 | 20296 | 30296 |
| 7400 | 5140 | 10140 | 20140 | 30140 |
| 7500 | 5000 | 10000 | 20000 | 30000 |
| 7600 | 2601 | 7601 | 17601 | 27601 |
| 7700 | 466 | 5466 | 15466 | 25466 |
| 7800 | -638 | 3086 | 13086 | 23086 |

Values above APP are neutral in the signed-min arbitration. The exact 7500
row is the transition point under the RPM conversion. The isolated
APP-5000 downstream projection produces symmetric channel targets 1820 at
7200 through 7600, 549 at 7700, and 18 at 7800. This proves executable
composition and both code channels; it is not a vehicle prediction. Real
targets also depend on idle/opening-area additions, the inflow-area
subtraction, controller bounds, fault modes, diagnostics, and current feedback.

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

`FFFF120E` is an inflow opening area in four times the raw `0x13202` area
counts, written by `00069374`; the same area enters the alpha-N coordinate of
Fuel Compensation Main described in `JK08A.fuel.md`. Outside the clamp,
`FFFF19B2 + (FFFF120E >> 2) = FFFF183E + FFFF1340`: the throttle target area
and the inflow area together equal the composed request area.

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
idle/opening-area base, inflow-area subtraction, channel corrections, target
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
  cut, but it is not a fuel-cut threshold. Its secondary transmission-request
  calculation reaches the common request boundary during a gear change in
  which TCM field `FFFF3A2E` (CAN `0x174` byte 4 bits 5 through 7) reads 3 and
  for the 307.2 ms hold after it, which the road captures show in 4-3 and 3-2
  downshifts. An A/B test must not externally force `FFFF418F.bit4`,
  `FFFF4252.bit1`, `FFFF4413`, or `FFFF41A6.bit3`, must record that CAN field,
  and compares the primary limiter outside those episodes.
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
