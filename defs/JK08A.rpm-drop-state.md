# JK08A RPM-Drop State

## Status and scope

This document records the exact JK08A/JK03A path that derives a filtered
engine-speed-drop class and explains the four-byte calibration at `0x1202E`.
The code establishes an RPM-domain Boolean gate. It does not establish an
initial ignition-retard quantity, and the address-free A2L family match is not
used as semantic evidence.

The downstream state participates in DFCO and several other coordinators. The
physical identity of the SH7058 PH9 input remains unresolved, so the
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

`FUN_0003E1DA` maintains four samples at
`0xFFFF1F6E..0xFFFF1F76`. On the normal filter path, let:

```text
R   = current uint16[0xFFFF114A]
H4  = four-sample-old uint16[0xFFFF1F76]
D   = max(H4 - R, 0)
P   = uint16[0xFFFF1E58]
K   = ROM8[0x84A4] = 64
F   = min(65535, K*D + floor((256-K)*P/256))
```

The function writes `F` to `0xFFFF1E50`. Dispatcher `FUN_000209D8` copies the
eight-byte block `0xFFFF1E50..0xFFFF1E57` to
`0xFFFF1E58..0xFFFF1E5F`, so `P` is the preceding filter snapshot. In Q8
terms, the stock recurrence is a 0.25 input and 0.75 history filter over the
positive four-sample RPM drop. Separate initialization and disabled branches
write `0xFF00` or zero and initialize the RPM history.

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

`FUN_00038618` copies SH7058 `PHDR.PH9DR` to `0xFFFF2451.bit7` with direct
polarity. PH9 is MCU pin 74. Its ECM terminal and physical switch identity are
not established.

All four stock cells at `0x1202E` equal 200. The magnitude is never used after
the lookup: zero and nonzero are the only operational classes. Stock JK08A
therefore requires the PH9-derived bit to publish the RPM-drop value while the
upstream mode bit is set. Replacing 200 with any other nonzero byte has no
effect; replacing a cell with zero bypasses that PH9 requirement for the
corresponding pre-mode RPM range.

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
- the PH9 physical input identity is unresolved;
- changing a cell to zero alters DFCO-related state selection and multiple
  other consumers.

Hardware validation requires logging `0xFFFF114A`, `0xFFFF1E50`,
`0xFFFF257A`, `0xFFFF1072`, `0xFFFF106A`, `0xFFFF2451.bit7`, and
`0xFFFF2459.bit5` across lift-off and reapplication events.
