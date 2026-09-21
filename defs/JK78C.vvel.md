# Exact JK78C VVEL target model

## Scope

This specification records the VVEL target task, its fifteen-mode target
selector, the exact sensor and diagnostic bindings of the selector inputs, and
the unit boundary of the target surfaces of the exact JK78C stock image
registered in `../rom-images/roms.csv`.
It separates code-proven selection logic and stored scales from candidate
engineering units, candidate vendor table names, and physical valve response.

The private VVEL bus, the command-word latch, and the composition of frame
`0x22B` are in `JK78C.can.md`. Interpolation contracts are in
`JK78C.interp.csv`. The factory service manual is authoritative for sensor
roles, DTC names, and CONSULT names. The exact ROM is authoritative for the
selection logic and the stored scales.

Addresses are ROM offsets or SH7058 RAM cells. `ROM8[a]` and `ROM16[a]` are
stock calibration bytes and big-endian words. Periodic-list entries refer to
the 144-entry list at `0x00021A4C` walked by `FUN_00020F1A` once per
background-loop pass; a pass is the tick of every counter below.

## Data flow

```text
coolant ffff1069, IAT ffff268c,
idle target ffff226c, RPM/12.5 ffff11a2 --> FUN 00059c2c --> ffff455b.bit7 (hot-intake idle)
RPM/25 ffff11a3, CLSD THL POS ffff23b8.bit6, ffff4573.bit1 --> FUN 0005a0da --> ffff456f.bit7 (above idle)
MAP ffff375e, booster ffff2666, speed ffff10fc --> FUN 0005a314 --> ffff4565.bit6 (throttled)
knock state ffff23c6.bit6, learning window ffff23e5.bit1, fail-safe ffff4577.bit0
        |
        v
FUN 00054e16 snapshot ffffa204.. --> mode machine --> mode byte ffffa22f --> ffff2808, ffff2830
        |
        v
RPM/3.125 ffff11a6, torque ffff2e26, demand ffff2350, load ffff238a,
shaft angles ffff2670/ffff2672, temperatures ffff1066/ffff1069
        --> FUN 000564a4 --> fifteen (duration, VTC) pairs at ffffa124..
        --> FUN 000557b2 selects the pair indexed by ffffa22f
        |
        v
target shaft angle (1/512 deg) --> curve 0x156DC/0x156FC --> bound words --> command ffff44aa
        --> latch ffff443e --> frame 0x22B bytes 0..1, DID 0x125C
```

`FUN_00054FD0` is entry 98 of the periodic list and owns the machine, the
resolver call, and the command word. `FUN_00054E16` copies the machine inputs
into `0xFFFFA204` onward: `0xFFFFA204` from `0xFFFF2672`, `0xFFFFA206` from
`0xFFFF2670`, `0xFFFFA208` from `0xFFFF10B6`, `0xFFFFA212` from
`0xFFFF455B.bit7`, `0xFFFFA213` from `0xFFFF4565.bit6`, `0xFFFFA214` from
`0xFFFF23B8.bit6`, `0xFFFFA215` from `0xFFFF23C4.bit6`, `0xFFFFA216` from
`0xFFFF4577.bit0`, `0xFFFFA217` from `0xFFFF4578.bit6`, `0xFFFFA218` from
`0xFFFF4578.bit7`, `0xFFFFA219` from `0xFFFF1066`, and `0xFFFFA21A` from
`0xFFFF1069`. `FUN_00054FD0` fills the monitor bytes `0xFFFFA308` from
`0xFFFF44DF.bit6`, `0xFFFFA309` from `0xFFFF44DF.bit7`, and `0xFFFFA30A`
from `0xFFFF23AF.bit4`.

`0xFFFF23B8.bit6` is the per-pass latch that `FUN_00020F1A` takes from
`0xFFFF23B9.bit6` at `0x000210A0`. `FUN_0008D710`, the eighth step of the
chain `FUN_0008D004` (pointer 23 of the list at `0x00021940`), is the only
producer of `0xFFFF23B9.bit6`. The diagnostic status packer `FUN_00031A0C`
copies the same bit to bit 0 of `0xFFFF34EC`, the DID `0x1302` byte
(`ROM32[0x22AA4]`, support mask `ROM8[0x1354B]` = `0x3F`). A structured Nissan
diagnostic profile names that bit `CLSD THL POS`, which the factory manual
defines as the idle position computed by the ECM from the accelerator pedal
position sensor signal. The bit is set when `0xFFFF23B1.bit6` or
`0xFFFF2422.bit7` is set and `FUN_000AE5F2` passes, or when the readiness
test fails: with `0xFFFF45BC.bit1`, `0xFFFF45C0.bit0`, and `0xFFFF24F7` all
clear the test is `0xFFFF44DA.bit2` clear (`0xFFFF23C1 & 0x30` = 0),
otherwise `0xFFFF45A0.bit7` clear (the bit sets at `0xFFFF43D0` = 0 and
clears above 4, under the `0xFFFF45C0.bit6` and `ROM8[0x8968]` gates). `FUN_000AE5F2` passes when
`0xFFFF44DF.bit6` is clear, `0xFFFF23AF.bit4` is set, and not
(`0xFFFF4500.bit0` set, `0xFFFF451D.bit2` clear, `0xFFFF36FA` and
`0xFFFF36FB` both below 20). `0xFFFF4573.bit1` is written only by
`FUN_00054FD0` at `0x000554C2` from the byte output of the resolver
`FUN_000564A4`, which `FUN_00056DCA` forms as the idle-model engagement
flag: mode byte 5, model state `0xFFFFA367` = 0, the model counter
`0xFFFFA369` at or above `ROM8[0x8B07]` = 1, the scaled demand margin at or
above `ROM8[0x8B05]` = 20, and the model duration at or below curve
`0x00016C64` (stock 21504 at every point); or the model latch `0xFFFFA368`
set with `0xFFFFA36B` = 0. Mode 15 requires that flag clear, so the
above-idle condition excludes passes on which the idle model is engaged.

The predicate cells resolve as follows.

- `0xFFFF23B1.bit6` is the direct copy of `PHDR` bit 1 (`0xFFFFF72C`, PH1)
  that the input sampler `FUN_0003BD78` takes at `0x0003BE74`. `FUN_00031A0C`
  copies it to bit 2 of `0xFFFF34EF`, the DID `0x1305` byte
  (`ROM32[0x22ABC]`, support mask `ROM8[0x1354E]` = `0x54`). The profile names
  that bit `BRAKE SW`, which the factory manual defines as the condition of
  the stop lamp switch signal.
- `0xFFFF2422.bit7` latches `0xFFFF2428.bit7` through the block copy
  `0xFFFF241D <- 0xFFFF2423`. `FUN_000AF340` sets it when `FUN_000AE5F2`
  passes, `0xFFFF23AF.bit0` is set, and either `0xFFFF45C6.bit4` with
  `0xFFFF450D.bit0` or both bits of `0xFFFF4514 & 0x30` are set.
  `FUN_000AE65E` forms those bits from the fault-status bytes of the two
  accelerator pedal sensors: `0xFFFF4514.bit5` from bit 7 of `0xFFFF6102` or
  `0xFFFF6105`, `0xFFFF4514.bit4` from bit 7 of `0xFFFF6108` or `0xFFFF610B`,
  and `0xFFFF45C6.bit4` from bit 7 of any of those bytes or `0xFFFF610E`. The
  term asserts the status on an accelerator pedal sensor fault.
- `0xFFFF23AF` is the per-pass latch of `0xFFFF23B1` (`0x0002108A`), so
  `0xFFFF23AF.bit4` follows the flag that `FUN_00029404` sets for codes 2..4
  of its state machine. `0xFFFF44DF` is the per-pass latch of `0xFFFF44E0`
  (`0x00021246`).
- `0xFFFF23C1.bit5` and `0xFFFF23C1.bit4` are the released-pedal flags of the
  two accelerator pedal sensors. `FUN_00091F68` copies the sensor word
  `0xFFFF3850` to `0xFFFF26F6` (the DID `0x120D` source through the latch
  `0xFFFF25F8`) and sets bit 5 while that word is at or below the learned
  released word `0xFFFF5AB6` plus `ROM16[0x8F0A]` = 16 plus 6, or plus 10
  while `0xFFFF240F.bit4` holds the previous result. `FUN_0008CF40` does the
  same for bit 4 with the word `0xFFFF26FA` (DID `0x120E`, latch
  `0xFFFF25FC`), the learned word `0xFFFF5AB8`, and `0xFFFF240F.bit3`. Either
  flag clears when its word leaves `[ROM16[0x8D40], ROM16[0x8D3C]]` =
  `[60, 964]` or a fault-status byte of its sensor has bit 7 set.
- `0xFFFF45BC.bit1`, `0xFFFF45C0.bit0`, and `0xFFFF24F7` select the second
  test while a request bound or the shift window is active. `0xFFFF45BC.bit1`
  latches `0xFFFF45C6.bit1`, which `FUN_0009ABB0` copies from
  `0xFFFF23F9.bit4` on stock (`ROM8[0x8383]` = `0x2C`, bit 1 clear); the
  request stages `FUN_0009474C` and `FUN_00094AAC` set `0xFFFF23F9.bit4` when
  a lower bound raises the signed request (`ROM8[0x894F]` = `0x49`,
  `0xFFFF44E5.bit5` set). `0xFFFF45C0.bit0` latches `0xFFFF45CA.bit0`, which
  `FUN_00098CA0` sets when the signed request `0xFFFF2390` is below the
  bounded lower-path request. `0xFFFF24F7` is the shift-window byte of
  `FUN_0009832C`: `0xFF` while `0xFFFF44E9 & 0x60` is nonzero or
  `0xFFFF45CA.bit6` is set and the pass counter `0xFFFF36B5` is at or below
  the window byte `0xFFFF36B4`, otherwise 0. `FUN_00096CE0` sets
  `0xFFFF45CA.bit6` while the index bytes `0xFFFF1076` and `0xFFFF1077`
  differ with `0xFFFF45CA.bit2` clear. The two bytes latch `0xFFFF1079` and
  `0xFFFF107A`, the zero-based current-gear and target-gear indices that
  `FUN_000EC214` decodes from byte 3 of the transmission frame `0x174` (low
  and high nibble, values 1 through 7, every other value as zero). The HCAN1
  dispatcher `FUN_000EB58C` calls that parser only for a receive record with
  standard ID `0x174`; the record table `0x0000944A` holds none, and the only
  other writer, `FUN_000EDB00`, stores zero in both bytes. No reachable store
  makes the two bytes differ, so this term leaves `0xFFFF45CA.bit6` clear on
  the stock image.
- `0xFFFF43D0` latches `0xFFFF43DC` through the block copy
  `0xFFFF43C8 <- 0xFFFF43D4`. `FUN_000902E0` writes it as a quarter of the
  demanded throttle-angle word: curve `0x000167E4` over axis `0x00014538`,
  the area-to-angle direction of the pair, evaluated at half the demand-area
  word `0xFFFF184A` of `FUN_00092A80`. The curve starts at 0, so the second
  test reads a zero demanded angle as the closed position and releases it
  above 4.
- `0xFFFF1078` latches `0xFFFF107B`, and `0xFFFF107E` holds the previous-pass
  `0xFFFF1078` (block copies `0xFFFF107C <- 0xFFFF1076` and
  `0xFFFF1076 <- 0xFFFF1079`, three bytes each, in that order).
  `FUN_0008D970` writes `0xFFFF107B` as the throttle-opening byte: `0x505B`
  / 65536 of the throttle-angle word `0xFFFF4260` above the reference word
  `0xFFFF2854`, saturated at 255 (`ROM8[0x8954]` = `0x02`, bit 0 clear), or
  `ROM8[0x8557]` = 10 while `0xFFFF45C7.bit7` is set. `FUN_000433BC` forms
  `0xFFFF4260` from the two selected throttle sensor words: each passes
  through the angle-to-area direction of the same curve pair, and the mean
  area returns through the area-to-angle direction.

## Exact diagnostic bindings

Service-0x22 pointer tables (family `0x11` at `0x00022718`, family `0x12` at
`0x00022918`) bind the selector inputs and the outputs:

| DID | Exact source | Model cell | Identity |
|---:|---:|---|---|
| `0x1101` | `0xFFFF106F` | `0xFFFF1069`, previous-cycle copy (`0xFFFF1064 <- 0xFFFF106A`, 6 bytes) | coolant temperature, degC + 50 |
| `0x1102` | `0xFFFF117C` | `0xFFFF10FC`, written by `FUN_0003DADC` | vehicle speed, 2 km/h per count |
| `0x1106` | `0xFFFF278A` | `0xFFFF268C`, latch `0xFFFF25D8 <- 0xFFFF26D6` (254 bytes) | intake air temperature, degC + 50 |
| `0x1201` | `0xFFFF11E0` | `0xFFFF11A2`, `0xFFFF11A3`, `0xFFFF11A6`, `0xFFFF10B6` | engine speed; shifted words of the same period measurement at 12.5, 25, 3.125, and 12.5 RPM per count |
| `0x1218` | `0xFFFF2350` | resolver input k11 | demand coordinate, unnamed in the catalogs |
| `0x125A`, `0x125B` | `0xFFFF42C0`, `0xFFFF42C2` | not a resolver input | VVEL POSITION SEN B1/B2 |
| `0x125C` | `0xFFFF443E` | latch of `0xFFFF44AA` | command word |
| `0x125D`, `0x125E` | `0xFFFF276E`, `0xFFFF2770` | `0xFFFF2670`, `0xFFFF2672`, same latch | VVEL TIM B1/B2, control-shaft angle |

Two range monitors bind the pressure channel that routes the throttled mode.
Both compare a 16-bit sensor word against the same window and reach the
descriptor table through `FUN_0009DFA8`:

| Record | Descriptor | Code | Raiser | Monitored cell | Window |
|---:|---:|---|---|---|---|
| `0x67` | `0x0001BC80`, bytes `230300000000010a00000000` | P010A, manifold absolute pressure sensor | `FUN_000E43B8` | `0xFFFF375E` | outside `[ROM16[0x9296], ROM16[0x9294]]` = `[1024, 65024]` |
| `0x68` | `0x0001BC8C`, bytes `230200000000055500000000` | P0555, brake booster pressure sensor | `FUN_000E44CE` | `0xFFFF26D2`, latch of `0xFFFF27D0` | outside `[ROM16[0x9290], ROM16[0x928E]]` = `[1024, 65024]` |

`FUN_000E44CE` calls `FUN_000E43B8` first and then runs the booster check in a
body that lies below its entry; the two monitors share one literal pool at
`0x000E44D8..0x000E451C`. Both gates are identical in shape:
`0xFFFF44DF.bit6` clear, `0xFFFF23AF.bit4` set, `0xFFFF5F88.bit7` and
`0xFFFF6117.bit7` clear, the enable bit in `ROM8[0x1A8AF]` (bit 3 for P010A,
bit 2 for P0555; stock `0x2C` sets both), and an inhibit byte at zero
(`0xFFFF24B0` for P010A, `0xFFFF24B8` for P0555, reloaded with
`ROM8[0x89DD]` = `ROM8[0x8A1D]` = 50 while `0xFFFF44DF.bit6` is set). The record
is raised only after the pass counter `0xFFFF46B9` or `0xFFFF46BA` has run down
from `ROM8[0x8991]` = `ROM8[0x8993]` = 50. The sensor words are 10-bit ADC
samples shifted left by 6, so the window is 0.08..4.97 V of a 5 V scale.

## Pressure channel

The ADC sampler `FUN_0002AA88` cycles an 8-step counter at `0xFFFF1688` and
selects the external multiplexer through bits `0x2000`, `0x4000`, and `0x8000`
of port word `0xFFFFF74E`. In cycle 4 it stores `0xFFFFF822 >> 6` at
`0xFFFF256E` and `0xFFFFF802 >> 6` at `0xFFFF3868`. `FUN_0002A488` copies
`0xFFFF256E` to `0xFFFF2568` in the main loop.

MAP sensor path (P010A monitor):

- `0xFFFF375E` is the filtered `0xFFFF2568 << 6` (`FUN_00043EEC` while
  `0xFFFF23E4.bit1`, filter order `ROM8[0x8B81]` = 1) or the learned value
  `0xFFFF3722` (`FUN_00043F60`, counter `0xFFFF346C`, sum `0xFFFF3760`,
  `ROM16[0x8DF8]` = 2, flag `0xFFFF453D.bit1`). `FUN_00043E90` sets
  `0xFFFF23E4.bit1` and the timer `0xFFFF251B` = `ROM8[0x89DA]` = 100 while
  `|0xFFFF1078 - 0xFFFF10F0|` exceeds `ROM8[0x8813]` = 3 or `ROM8[0x83AA]` = 3.
- `0xFFFF57C4` is the learned atmospheric reference. `FUN_00043CDE` (entry 96)
  interpolates curve `0x000135E8` = `51, 63, 77, 91, 106, 120, 134, 149` by
  `0xFFFF11A3` over the implicit axis `0x000132D6` = `0..224` into
  `0xFFFF2948`. With the engine turning (`0xFFFF10B6 * 4 > ROM8[0x877E]` = 10)
  the reference averages `0xFFFF375E` with order `ROM8[0x82EC]` = 1 only while
  `0xFFFF4772` is zero and `0xFFFF107E <= 0xFFFF1078`; `0xFFFF1078` above the
  curve reloads `0xFFFF4772` with `ROM8[0x8814]` = 20. With the engine stopped
  the reference is the mean of `0xFFFF375E` and itself. `FUN_00043C94` clamps
  it to `[ROM16[0x9246], ROM16[0x9244]]` = `[40450, 58461]`, which is
  3.09..4.46 V. `FUN_00043E0E` counts passes with `0xFFFF375E >= 0xFFFF57C4`
  at `0xFFFF21BB` and applies the clamp after five.
- `0xFFFF4AC2` is the scaled reference: `FUN_00021E0C` division of the
  reference plus `ROM8[0x8816]` = 20, saturated at `0xFFFF`, while
  `ROM8[0x8ADA]` = 255; otherwise `0xFFFF`. `FUN_00044034` scales
  `0xFFFF375E` into `0xFFFF3314` on the same path.

Brake booster path (P0555 monitor), `FUN_00045A4C`:

- `0xFFFF42E2` copies `0xFFFF3868`. `0xFFFF27D0` is the first-order filtered
  `0xFFFF3868 << 6` with gain `ROM8[0x8B76]` = 64 and first-pass
  initialization through `0xFFFF45AE.bit1`. The periodic-list latch copies it
  to `0xFFFF26D2`, the cell the P0555 monitor reads.
- `0xFFFF2764` is the scaled booster pressure: `FUN_00021E0C(0xFF,
  ROM8[0x8823] = 28, 0xFFFF27D0)` plus `ROM8[0x8817]` = 20, saturated at
  `0xFFFF`, while `ROM8[0x8ADB]` = 255; otherwise `0xFFFF`. The same latch
  copies it to `0xFFFF2666`.

`FUN_00021E0C` and `FUN_00021CE8` are the fixed-point division helpers
(divisor in `r0`, dividend in `r1`, 8 or 16 fractional bits, error code
`0x44E` to `0xFFFF9748` on a zero divisor).

Booster vacuum and the throttled-mode flag, `FUN_0005A314` (entry 97):

- `0xFFFF3338 = max(0, 0xFFFF4AC2 - 0xFFFF2666)`, scaled reference minus
  scaled booster pressure.
- `0xFFFF4577` bits 6 and 5 latch vehicle speed `0xFFFF10FC` above
  `ROM8[0x8B17]` = 2 and `ROM8[0x8B18]` = 7 counts (4 and 14 km/h) with
  hysteresis `ROM8[0x8AFE]` = 1. They select `0xFFFF3324` from `ROM16[0x9094]`
  = 0, `ROM16[0x9096]` = 467, and `ROM16[0x9098]` = 547.
- `0xFFFF4515.bit0` is `0xFFFF3338 >= 0xFFFF3324 + ROM16[0x909C]` = 10.
  `0xFFFF455E.bit1` follows it: booster vacuum sufficient.
- `0xFFFF455E.bit0` (sensor abnormal) clears when `0xFFFF4573.bit4` is set or
  when `0xFFFF4516.bit7` is clear, `0xFFFF23AF.bit6` is clear or
  `0xFFFF23BD.bit5` or `.bit4` is set, `0xFFFF23AF.bit6` is clear or
  `0xFFFF10FC < ROM8[0x8AFA]` = 254, and `0xFFFF5FCA.bit7` and
  `0xFFFF5FCD.bit7` are clear. `0xFFFF4516.bit7` holds with the pass timer
  `0xFFFF4753` = `ROM8[0x8429]` = 3 and `0xFFFF482C` = `ROM8[0x8428] << 2` = 32.
- `0xFFFF4565.bit6 = !(0xFFFF455E.bit1 && !0xFFFF455E.bit0)`: the throttled
  mode is requested while booster vacuum is insufficient or the sensor is
  abnormal.

The physical unit of the scaled words `0xFFFF4AC2`, `0xFFFF2764`, and
`0xFFFF3338` is not code-proven; the division constants and the thresholds 467
and 547 are stored values only.

## Mode machine

The mode byte `0xFFFFA22F` (previous value `0xFFFFA294`, published to
`0xFFFF2808` and `0xFFFF2830`) is the VVEL and VTC control mode. Entry
functions write it: `FUN_000575E2` mode 1 at initialization, `FUN_00054CAA`
mode 0 at machine reset, `FUN_000543EA` modes 2 and 11, `FUN_000542FA` modes
2 and 6, `FUN_00054AE8` mode 3, `FUN_00054AC4` mode 4, `FUN_00054A62` modes 5
and 10, `FUN_00054C5A` modes 7 and 8, `FUN_00054918` modes 7, 8, and 9,
`FUN_00054AAC` mode 12, `FUN_00054A4A` mode 13, `FUN_00054A94` mode 15. The
image holds no write of the value 14: mode 14 is unreachable and the resolver
computes its pair as dead data. `FUN_000546BA` dispatches events: `0xE` and
`0x15` to mode 4, `0xF` to 15, 5, or 10, `0x14` to 12 or 13, and switches
between 5 and 10 on the learning-window flag. `FUN_0005461A` maps `0x10`/`0x12`
to 12 or 13, `0x11`/`0x13` to 15, 5, or 10, `0xD` to 3, and 5 to 4; otherwise
it defers to the cold and warm resolvers `FUN_00053C3E` and `FUN_00053D06`.

Modes 6 through 9 are the fail-safe branch over the snapshot flags
`0xFFFFA216`, `0xFFFFA217`, and `0xFFFFA218` and the monitor bytes
`0xFFFFA308`, `0xFFFFA309`, and `0xFFFFA30A`. `FUN_00053B0C` raises event
10 while any fail-safe flag is set, and event 4 while all three are clear
and either `0xFFFFA274` = 1 with the word `0xFFFFA21E` at or above
`ROM16[0x8E2C]` = 5, `0xFFFFA308` clear, and `0xFFFFA309` set, or
`0xFFFFA309` clear with `0xFFFFA208 / 4` below `ROM8[0x8495]` = 32.
`FUN_00053A7C` raises event `0xB` while `0xFFFFA309` is set, `0xFFFFA22B` = 1
or `0xFFFFA308` is set, and a fail-safe flag is set. `FUN_000542FA` enters
mode 6 on event 4 (previous mode to `0xFFFFA294`, counter `0xFFFFA21C`
cleared) and calls `FUN_00054C5A` on events 10 and 11, which enters mode 8
when `0xFFFFA217` or `0xFFFFA218` is set and mode 7 otherwise.
`FUN_00054918` moves mode 7 or 8 to mode 9 on event 8, raised by
`FUN_00053DC6` on the same monitor test with `0xFFFFA28C`, `0xFFFFA222`,
`0xFFFFA308`, and `0xFFFFA309`; returns to 7 or 8 on event 6 while
`0xFFFFA22B` = 1 and `0xFFFFA309` is set; and leaves through
`FUN_000543EA(7)` while `0xFFFFA30A` is clear. `FUN_00053EEA` writes
`0xFFFFA22B`; `FUN_00053BB0` and `FUN_00053E18` keep the internal timers
`0xFFFFA274` and `0xFFFFA28C`.

The pass counter `0xFFFFA220` saturates at `0xFFFF`; the mode-2 entry clears
it. Stock `ROM16[0x9194]` = 2000 passes bounds the second cold path.

| Mode | Duration source | VTC source | Selection |
|---:|---|---|---|
| 1 | `ROM16[0x926E] * 0.05` = 28.5 | 0 | initial after reset |
| 2, 11 | start-up value `0xFFFFA194` | 0 | `FUN_000543EA`; counter reset |
| 3 | `0x00016A54` by coolant `0xFFFF1069`, `* 0.05` | `0x00016A94`, gated by flag `0xFFFFA362` with hysteresis `ROM8[0x8AA7]` = 53 and `ROM8[0x8AA8]` = 0 | cold branch: `0xFFFFA21A` below `ROM8[0x84A6]` or `0xFFFFA219` below `ROM8[0x84A4]`, all stock 120 = 70 degC |
| 4 | `0x00016D14` by `0xFFFF11A6`, `* 0.05` (stock 50..72) | `0x000108CE` by `0xFFFF11A6` and load `0xFFFF238A`, `(raw - 0x8000) / 2` | throttled mode: `0xFFFF4565.bit6`, or the cold path with `0xFFFF23B8.bit6` after 2000 passes |
| 5 | idle model `0xFFFFA1B0` (`FUN_00056BAA` chain) | `450 + ROM16[0x8D8E] / 512 - (0xFFFFA1B8 + 0xFFFFA1BC) / 2` | warm, `0xFFFF455B.bit7`, `0xFFFF4565.bit6`, and `0xFFFF456F.bit7` clear, learning window closed |
| 6 | 28.5 | 0 | `FUN_000542FA` on event 4: fail-safe flags clear, monitor test of `FUN_00053B0C` |
| 7 | `ROM16[0x927A] * 0.05` = 50.0 | 0 | `FUN_00054C5A` on events 10 and 11: `0xFFFF4577.bit0` set, `0xFFFF4578.bit6` and `.bit7` clear |
| 8 | filtered actual duration `0xFFFFA180` | 0 | `FUN_00054C5A` on events 10 and 11: `0xFFFF4578.bit6` or `.bit7` set |
| 9 | 50.0 while `0xFFFF4577.bit0`, else `0xFFFFA180` | 0 | `FUN_00054918` on event 8 from mode 7 or 8: monitor test of `FUN_00053DC6` |
| 10 | `ROM16[0x9006] * 0.05` = 28.5 | `(ROM16[0x9008] - 0x8000) / 2` = 0 | as mode 5 with the learning window `0xFFFF23E5.bit1` open |
| 12 | `max(0x0000E1CE, 0x0001600A) * 0.05` | 0 | hot-intake idle `0xFFFF455B.bit7`, knock state `0xFFFF23C6.bit6` clear |
| 13 | `max(0x0000E24E, 0x0001601A) * 0.05` | 0 | hot-intake idle with the knock state set |
| 14 | 50.0 | 0 | unreachable: no write of 14 to `0xFFFFA22F` |
| 15 | `0x00016BB4` by `0xFFFF11A6`, `* 0.005` (stock 33..72) | `0x00016DC4` by `0xFFFF11A6`, `(raw - 0x8000) / 2` | warm, above idle `0xFFFF456F.bit7`, no hot-intake or throttled request |

`FUN_000557B2` selects pair `m` of the fifteen at `0xFFFFA124 + 8 * (m - 1)`
by the mode byte. The mode 15 scale is fixed by the float literal
`0x3BA3D70A` = 0.005; every other duration map is scaled by 0.05.

Supporting values:

- `0xFFFFA180` (`FUN_0005693A`) is the first-order filtered actual duration
  derived from the shaft angle `0xFFFF2670` (`0xFFFF4578.bit7` set) or
  `0xFFFF2672` through the pair `0x000156FC`/`0x000156DC`, gain
  `ROM16[0x9266]` = 11990.
- `0xFFFFA194` (`FUN_00056AB4`) is `0x00015E32` by the selected temperature
  `0xFFFF1066` over axis `0x00017204` = `10..160` (-40..110 degC), `* 0.05`,
  while `0xFFFF45CA.bit1` is clear; otherwise a ramp between `ROM16[0x91C6]`
  = 1240 (62.0) and `ROM16[0x91C8]` = 1300 (65.0) with step `ROM16[0x9198]`
  = 32768 * 2^-15 per pass, direction by `0xFFFF10B6` against `ROM16[0x8EC6]`
  = 8 and `ROM16[0x8EC8]` = 36, reset in modes 1 and 6.
- `0xFFFF23C6.bit6` is the high-detonation state written by `FUN_00062780`
  (entry 73). `0xFFFF23E5.bit1` is the learning window held by `FUN_00080CEC`
  and `FUN_00080D62` (CONSULT `VVEL LEARN`). `0xFFFF4577.bit0` is written by
  the fault handler `FUN_000BDF90`.

## Selector inputs

Hot-intake idle, `FUN_00059C2C` (entry 94 through `FUN_0005A210`):
`0xFFFF4569.bit5` latches `0xFFFF268C` (hysteresis `ROM8[0x85D6]` = 3) at or
above curve `0x00013F88` = `255, 255, 255, 255, 255, 130, 110, 90`, or
`0x00013F90` = `90, 70, 50, 50, 50, 50, 50, 50` while `0xFFFF23C6.bit6` is
set, interpolated by coolant `0xFFFF1069` over axis `0x00014208` = `90..160`
(40..110 degC) into `0xFFFF34FA`. `0xFFFF4553.bit2` is
`FUN_0002737C(0xFFFF11A2, 0xFFFF226C + ROM8[0x879D] = 20, ROM8[0x85D4] = 24)`:
engine speed at or below the idle target plus 250 RPM with 300 RPM hysteresis.
`0xFFFF455B.bit7` is both latches set. `0xFFFF226C` is the target idle speed
byte at 12.5 RPM per count: `FUN_0005B418` sums adders and `FUN_0005B298`
clamps the sum to `ROM8[0x87AF]` = `ROM8[0x87B5]` = 64 (800 RPM) under
`0xFFFF23AF.bit0`, `0xFFFF23F5.bit7`, `0xFFFF23CB.bit0`, and `ROM8[0x8968]` =
`0x80`.

Above idle, `FUN_0005A0DA` (same entry): `0xFFFF4542.bit0` is
`FUN_0002737C(0xFFFF11A3, ROM8[0x8784] = 40, ROM8[0x85D3] = 4)`, engine speed
at or below 1000 RPM with 100 RPM hysteresis; the three conditional adders
`ROM8[0x8782]`, `ROM8[0x8785]`, and `ROM8[0x8783]` are zero in stock.
`0xFFFF456F.bit7` is that latch clear, `0xFFFF23B8.bit6` set, and
`0xFFFF4573.bit1` clear; `0xFFFF329C` stores the threshold.

Throttled mode: the booster vacuum path above.

Cold branch: `FUN_00054B2C` takes the cold path while the coolant snapshot
`0xFFFFA21A` is below `ROM8[0x84A6]` or the selected-temperature snapshot
`0xFFFFA219` is below `ROM8[0x84A4]`, the previous mode is not 5, 10, 12, or
13, and, from mode 4, `0xFFFFA21A` is also below `ROM8[0x84A5]`. All three are
120 in stock, the 70 degC grid point of axis `0x00014208`.

## Target surfaces and scales

| Address | Geometry | Axis input | Stored scale | Reader |
|---:|---|---|---|---|
| `0x0000E1CE` | 8x8 u16, axes `0x000160CA` = `128..640` and `0x000160DA` = `250..2000` | `0xFFFF11A6` (400..2000 RPM) and `0xFFFF2E26` | 0.05 per count, stock 900..1180 = 45.0..59.0 | mode 12 |
| `0x0000E24E` | 8x8 u16, same axes | same | same, stock identical to `0x0000E1CE` | mode 13 |
| `0x0001600A`, `0x0001601A` | 8-point u16, axis `0x00015FFA` = `100..800` | `0xFFFF2350` | 0.05, stock all 900 = 45.0 | floors of modes 12 and 13 |
| `0x00016BB4` | 16-point u16, axis `0x00016CA4` | `0xFFFF11A6` | 0.005, stock 33..72 | mode 15 |
| `0x00016DC4` | 16-point u16, axis `0x00016E74` | `0xFFFF11A6` | VTC, zero at `0x8000`, 0.5 per count | mode 15 |
| `0x00016D14` | 16-point u16 | `0xFFFF11A6` | 0.05, stock 50..72 | mode 4 |
| `0x000108CE` | 16x16 u16, axes `0x00016DE4` = `256..2176` and `0x00016E04` = `4100..65535` | `0xFFFF11A6` (800..6800 RPM) and `0xFFFF238A` (6.3..100 %) | VTC, zero at `0x8000`, stock about `0x8000` | mode 4 |
| `0x00016A54`, `0x00016A94` | curves by coolant | `0xFFFF1069` | 0.05; VTC | mode 3 |
| `0x00015E32` | curve, axis `0x00017204` = `10..160` | `0xFFFF1066` | 0.05 | start-up value |
| `0x000156DC`, `0x000156FC` | pair `0..15536` and `12800..37351` | shaft angle or command | angle to command and back | `FUN_00054FD0`, `FUN_0004D3CE`, `FUN_0005693A` |
| `0x000160BA`, `0x00016A74` | curves | task inputs | command bound minus `abs(0xFFFF5E8E)` | `FUN_00054FD0` |
| `0x0001609A`, `0x000160AA` | curves | task inputs | diagnostic floor | `FUN_000BF0C0`, `FUN_000BF122` |

Code-proven scales: engine-speed counts of 3.125, 12.5, and 25 RPM;
temperature counts of degC + 50; vehicle speed of 2 km/h per count; duration
floats of 0.05 and 0.005 per stored count; VTC floats of 0.5 per stored count
with zero at `0x8000`; shaft angle words of 1/512 degree; load fraction
`0xFFFF238A` with full scale `0xFFFF`.

Candidate scales: `0xFFFF2E26` as target torque at 0.1 Nm per count (axis
25..200 Nm); `0xFFFF2350` as demand at 1/8 percent per count (axis
12.5..100 %); the duration float as camshaft degrees of valve-event duration
and the VTC float as degrees of intake-cam advance, both taken from vendor
documentation and not from the code.

Every surface, curve, and axis in the table above is registered in
`vq37-native-tables.toml` with its exact stock block hash, literal-pool
bindings, editor name, and scale, and reaches the JK78C definition through that
registry. The 1ND targets register the same roles at their own addresses; their
resolver indexes the hot-intake idle surfaces by coolant temperature and
intake air temperature (degC + 50), reads a mode 14 surface that its machine
selects on the hot-intake idle request with the knock state set and the idle
target at or above 650 RPM, and carries no floor curves. 1ME3B registers the
JK78C role set at its own addresses: its resolver `0x062FAC` keeps the
engine-speed and torque axes, holds 50.0 at every point of both floor curves,
stores the constant 50.0 for mode 14, reads the cold pair and the shaft-angle
conversion inline, and leaves the throttled pair to `0x063534`.

The registry also carries the tables that stand beside the resolver set. All
four images hold byte-identical second copies of the shaft-angle conversion
and of both monitor floors. In JK78C `FUN_0004FCB8` converts the two measured
angle words `0xFFFF2670` and `0xFFFF2672` through the copy `0x0001B00A` over
`0x0001AFEA` and publishes the mean of the two results times 1/512 as the
float `0xFFFF9E98` for `FUN_0004F3FE`. `FUN_00059B82` and `FUN_00059B64`,
entries `0x00021BC0` and `0x00021BBC` of a function-pointer list, interpolate
the floor copies `0x0001B28A` and `0x0001B29A` by the word `0xFFFF11BC` into
`0xFFFF380A` and `0xFFFF380C`; the deficit monitors `FUN_000BF0C0` and
`FUN_000BF122` take the maximum of those two words and the primary floor words
`0xFFFF3276` and `0xFFFF3278`. `0xFFFF11BC` latches
`0xFFFF11F0 = (12000000 / (ROM8[0x87AB] * period 0xFFFF2230)) >> 1` with
`ROM8[0x87AB] = 3`, which equals the `2000000 / period` form of the primary
coordinate `0xFFFF11A6` for a second period measurement. The two period
samplers are twins: the event handler `FUN_0002095C` calls `FUN_0002B548`
(period `0xFFFF11E8` of the primary coordinate) and `FUN_0002B5AC` (period
`0xFFFF2230`) back to back through the adjacent pointer words `0x00020B20` and
`0x00020B24`. Both take the difference of the same capture word `0xFFFF1864`,
which the interrupt handler `FUN_0002B8FA` stores at `0x0002C356`, under the
same gate (`0xFFFF241E` bit 5 clear and the byte `0xFFFF2544` zero) and shift it right by
five; they differ only in the previous-capture cells `0xFFFF84D4` and
`0xFFFF84D8`. Both words therefore span the same crank interval, and
`0xFFFF11BC` carries the 3.125 RPM count weight of `0xFFFF11A6`.

The state-code dispatcher `FUN_000657E4` reads its own hot-intake idle pair
`0x000102CE` (state code 5) and `0x0001034E` (state codes 6 and 7) over the
axes `0x00016CF4` and `0x00016CE4`, with `min(0xFFFF, 0xFFFF11AC << 2)` and
the load byte `0xFFFF1032 << 8` as coordinates, for the state bytes
`0xFFFF43F2` and `0xFFFF4480`, and publishes the duration word `0xFFFF122C`.
`FUN_0004678C`, entry 43 of the periodic list `0x00021A4C` (pointer word
`0x00021AF8`; the VVEL task `FUN_00054FD0` is entry 98), writes all three
state cells from the published mode byte `0xFFFF2808`. `FUN_0004692A` maps
the mode to the state code: mode 5 gives 2, mode 3 gives 3, mode 10 gives 4,
mode 12 gives 5, mode 13 gives 6, mode 14 gives 7, mode 15 gives 8, and every
other mode gives 1. The 1ND mapper `FUN_0004C4B8` and the 1ME3B mapper
`FUN_00050310` implement the same table in a different instruction form.
Mode 14 is unreachable on JK78C, so code 7 is never produced. `0xFFFF43F2`
holds the current code. `FUN_00046978` keeps in `0xFFFF4480` the code that was
current before the latest mode change (state block `0xFFFF9959`: held code,
last code, and last mode at offset `0x0F`). `FUN_000468C6` forms the crossfade
weight `0xFFFF43F0`: the accumulator `0xFFFF9954` restarts from zero when the
code differs from `0xFFFF9958`, grows by the step word `0xFFFF2824` on every
pass, and saturates at `0x8000` = 1.0; while the current or the previous code
is 8, the weight is the word `0xFFFF281E` instead. The start-up initializer
`FUN_000302D4` seeds both code bytes.
1ME3B carries the same pair in `FUN_0007448C`; the 1ND dispatcher
`FUN_00070514` reads the resolver surfaces at those positions. The delay curve
of the stepped throttled approach and the start-up blend target exist only in
1ME3B.

## Vendor correspondence

Vendor definitions describe a three-dimensional main duration surface over
engine speed and load, separate two-dimensional wide-open-throttle and overrun
curves, and shaft limit curves. The resolver holds one pair of
three-dimensional duration surfaces, `0x0000E1CE` and `0x0000E24E`, and both
are selected by the hot-intake idle condition over 400..2000 RPM. The normal
running mode 15 reads a single engine-speed curve. No duration surface in the
resolver is selected by throttle position or by an overrun condition. The
vendor names therefore remain unassigned; the selection conditions above are
the only names this specification carries.

## Evidence boundary

Code-exact: the mode machine, the fifteen target pairs, the selector
conditions, the DID bindings, the descriptor records P010A and P0555, and the
stored scales listed as code-proven.

Open: the ECM terminal of the PH1 input behind `0xFFFF23B1.bit6`; the
physical unit of the signed request words behind `0xFFFF45C0.bit0` and
`0xFFFF23F9.bit4`; the physical unit of the scaled pressure words; whether `0xFFFF1CE2` (DID `0x1116` source
through `FUN_0004185A`) and `0xFFFF256E` sample the same MAP input; the
candidate scales above; and the agreement of the computed command with DID
`0x125C` on live data. The pass period follows the vector-120 handler and
is not measured on this target.
