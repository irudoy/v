# JK08A RPM-Drop State

## Status and scope

This document records the exact JK08A/JK03A path that derives a filtered
engine-speed-drop class and explains the four-byte calibration at `0x1202E`.
The code establishes an RPM-domain Boolean gate. It does not establish an
initial ignition-retard quantity, and the address-free A2L family match is not
used as semantic evidence.

The downstream state participates in DFCO and several other coordinators, and
the byte magnitude carries no information beyond zero versus nonzero, so the
calibration stays hidden from tuning-editor output.

## Current engine-speed word

`FUN_0003DEEC` is the sole whole-program writer of `0xFFFF114A`. Its normal
path computes:

```text
R = floor(0xA2C2 / uint16[0xFFFF22BC])
```

`0xFFFF22BC` is the normalized captured engine-event interval. A selected
alternate path copies `0xFFFF11F4`, the independently established RPM/12.5
word, directly into `0xFFFF114A`. This binds `R` to the same RPM/12.5 domain.
Another runtime gate writes zero instead.

## Positive RPM-drop filter

`FUN_0003E1DA` maintains the current sample and four preceding samples at
`0xFFFF1F6E..0xFFFF1F76`. On the enabled non-fault filter path, let:

```text
R   = current uint16[0xFFFF114A]
H4  = four-sample-old uint16[0xFFFF1F76]
P   = uint16[0xFFFF1E58]
K   = ROM8[0x84A4] = 64

if H4 < R:
    F = 0
else:
    D = H4 - R
    F = min(65535, K*D + floor((256-K)*P/256))
```

The function writes `F` to `0xFFFF1E50`. Dispatcher `FUN_000209D8` copies the
eight-byte block `0xFFFF1E50..0xFFFF1E57` to
`0xFFFF1E58..0xFFFF1E5F`, so `P` is the preceding filter snapshot. In Q8
terms, the non-rising recurrence is a 0.25 input and 0.75 history filter over
the four-sample RPM drop. Rising speed writes zero independently of `P`;
equal speed retains the truncated history term. `0003e20a..0003e20c`
compares the zero-extended samples and branches to the zero store at
`0003e268..0003e26a` when `H4 < R`.

The crank/cam fault predicate `FUN_00025E4E` returning nonzero selects
`ROM8[0x84A3]<<8`, stock `0xFF00`. With a zero result and
`0xFFFF24B8.bit6` clear, the producer writes zero. Both mode paths initialize
the current sample and all four history words to `R`; a zero predicate result
with bit 6 set selects the filter path and shifts the history after the store.

## Calibration 0x1202E

When `0xFFFF2459.bit5` is clear, `FUN_0003E1DA` calculates:

```text
q = clamp(uint16[0xFFFF114A] - 96, 0, 255)
B = interp_u8_1d4(ROM[0x1202E], q)
```

The implicit interpolation nodes are `q = 0, 64, 128, 192`. In the established
RPM/12.5 domain they correspond to 1200, 2000, 2800, and 3600 RPM. The lookup
result is copied to `0xFFFF1EE0` and `0xFFFF257A`, and the current published
state `0xFFFF1072` is forced to zero.

When `0xFFFF2459.bit5` is set, the lookup is not repeated. The retained byte
`B = uint8[0xFFFF257A]` controls publication:

```text
if B != 0 and 0xFFFF2451.bit7 == 0:
    0xFFFF1072 = 0
else:
    0xFFFF1072 = floor(uint16[0xFFFF1E50] / 256)
```

`FUN_00038618` keeps the port H base `0xFFFFF728` (`ROM16[0x386B2]`) at
`@(4,r15)` and at `0x0003870C..0x00038720` reads the 16-bit `PHDR` word at
`0xFFFFF72C`, tests bit 1 (`tst #2`), and writes the result to
`0xFFFF2451.bit7` with direct polarity: the bit is set while PH1 reads high.
`PHDR` bit 1 is `PH1DR`, and PH1 is SH7058 FP-256H pin 64. The diagnostic
status packer `FUN_0002E0D4` copies `0xFFFF2451.bit7` to bit 2 of
`0xFFFF3345` at `0x0002E27C..0x0002E286`, and the service-0x22 table
publishes that byte as DID `0x1305` with support mask `0x44`:

```text
ROM32[0x22A08] = 0xFFFF3345
ROM32[0x22A0C] = 0x00011E44
ROM8 [0x11E44] = 0x44
```

A structured Nissan diagnostic profile names DID `0x1305` bit 2 `BRAKE SW`.
The factory manuals define `BRAKE SW` as the ON/OFF condition of the stop lamp
switch signal and `BRAKE SW1` as that of the ASCD brake switch signal, and
place the two signals on ECM terminals 122 and 126:

| Manual section | Data monitor | Terminal 122, stop lamp switch (P) | Terminal 126, ASCD brake switch (BR) |
| --- | --- | --- | --- |
| 2007 G35 Sedan, VQ35HR | EC-118, EC-120 | EC-500, EC-404 | EC-500, EC-403 |
| 2013 G Sedan, VQ25HR | EC-735, EC-736 | EC-1005 | EC-1006, EC-938 |
| 2013 G Sedan, VQ37VHR | EC-160, EC-161 | EC-568 | EC-568, EC-469 |

The harness continuity checks connect stop lamp switch connector E110
terminal 2 to ECM connector M107 terminal 122 (2007 EC-407, 2013 ICC section
CCS-58) and ASCD brake switch connector E109 terminal 2 to M107 terminal 126
(2007 EC-404).

Terminal 122 reads 0 V with the brake pedal fully released and battery
voltage with the pedal slightly depressed, with the ignition switch OFF.
Terminal 126 reads battery voltage released and 0 V depressed, with the
ignition switch ON. The 2013 tables measure both against ECM ground terminal
128.

PH1 is a terminal 122 candidate by signal identity: the DID bit that the
profile names `BRAKE SW` is the direct copy of PH1, and every covered section
places the stop lamp switch signal on terminal 122. With a non-inverting input
stage the bit is set with the pedal depressed, as `BRAKE SW` ON requires; a
connection to terminal 126 would need an inverting stage for the same
reading. The manuals describe export-market ECMs and harnesses, and the
250GT board is not covered by them. The pin tracer connector table
(`tools/pin-tracer/`) labels terminal 122 `BRAKE` and terminal 126 `BNCSW`.

Bench check on the owned JK08A board:

1. Unpowered: measure the resistance from ECM terminal 122 to MCU pin 64. A
   direct or series-resistor path confirms the route; terminal 126 to pin 64
   is the negative control. A transistor stage shows no DC path and leaves
   the route to step 2. Record the route in the pin tracer.
2. Powered with the ignition input on: switch terminal 122 between 0 V and
   battery voltage and read DID `0x1305` bit 2. The candidate predicts the bit
   clear at 0 V and set at battery voltage. The bit follows
   `0xFFFF2451.bit7`, so the reading also fixes the polarity of the input
   stage.

The same packer copies `0xFFFF2459.bit5` to bit 0 of the DID `0x1302` byte
`0xFFFF3342` at `0x0002E154..0x0002E162`. The profile names that bit
`CLSD THL POS`, which the factory manual defines as the idle position computed
by the ECM from the accelerator pedal position sensor signal.

All four stock cells at `0x1202E` equal 200. The magnitude is never used after
the lookup: zero and nonzero are the only operational classes. Stock JK08A
therefore requires the PH1-derived `BRAKE SW` bit to publish the RPM-drop value
while the `CLSD THL POS` bit `0xFFFF2459.bit5` is set. Replacing 200 with any
other nonzero byte has no effect; replacing a cell with zero bypasses that PH1
requirement for the corresponding pre-mode RPM range.

## Scheduled state and DFCO use

Scheduler `FUN_00020DFE` copies `0xFFFF1072..0xFFFF1079` to
`0xFFFF106A..0xFFFF1071`. `0xFFFF106A` is therefore the scheduled RPM-drop
class, not a coolant-temperature byte.

Several consumers classify it with the first three bytes of ROM sequence
`0x11CB5 = [4, 8, 12, 32]`:

| `0xFFFF106A` | Class index |
|---:|---:|
| `0..3` | 0 |
| `4..7` | 1 |
| `8..11` | 2 |
| `12..255` | 3 |

The fourth byte, 32, is present in ROM but is not compared by these four-class
loops. The DFCO restore classifier uses the class to select raw RPM/25 floors
from `0x1299C = [36, 48, 54, 62]`, corresponding to 900, 1200, 1350, and 1550
RPM. `FUN_0005038A` and `FUN_000503E0` also use the class with threshold 4 in
exit-delay and state handling.

## Definition boundary

`0x1202E` is retained in the canonical map ledger with code confidence and an
exact Boolean-gate role. It is hidden from RomRaider and TunerPro because:

- its old Initial Retard Quantity identity is contradicted by the machine path;
- byte magnitude is irrelevant beyond zero versus nonzero;
- changing a cell to zero alters DFCO-related state selection and multiple
  other consumers.

Hardware validation requires logging `0xFFFF114A`, `0xFFFF1E50`,
`0xFFFF257A`, `0xFFFF1072`, `0xFFFF106A`, `0xFFFF2451.bit7`, and
`0xFFFF2459.bit5` across lift-off and reapplication events.
