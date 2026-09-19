# JK08A computed START SIGNAL and selected-temperature gate

This specification binds the selected-temperature path to its exact runtime
and diagnostic identities. The alternate branch is a zero sentinel, not a
second physical temperature sensor.

## Battery-voltage identity

SH7058 `ADDR0` at `0xFFFFF800` reads MCU channel AN0. In JK08A, AN0 is fed by
an external analog multiplexer selected through `PFDR` bits PF13..PF15 at
`0xFFFFF74E`.

The cyclic sampler `0x000280D8` establishes this sequence:

| Scan phase | PF15..PF13 while sampled | ADDR0 destination | Bound meaning |
|---:|:---:|---:|---|
| 1 | `000` | `0xFFFF1D60` | engine coolant input |
| 2 | `001` | `0xFFFF1D6E` | battery-voltage input |
| 8 | `111` | `0xFFFF100A` | fuel-temperature input |

Direct reader `0x00028668` independently selects code `000` for the coolant
path and code `111` for the fuel-temperature path. After phase 8, the cyclic
sampler clears PF13..PF15 back to code `000`.

`0x00039A9E` reads the phase-2 word at `0xFFFF1D6E`, stores its shifted byte,
runs the existing conversion helpers, saturates the result to 255, and writes
`0xFFFF1188`. The exact service-0x22 pointer table contains:

```text
ROM32[0x226B8] = 0xFFFF1188             # DID 0x1103
```

A homologous measured diagnostic definition identifies DID `0x1103` as
battery voltage with `V = raw * 0.08`. This gives the selector threshold raw
100 an engineering value of 8.00 V. The exact JK08A response identity is
code-proven. The conversion helpers leave the byte equal to the ten-bit sample
shifted right by two, and the ROM limits of the DTC monitors reproduce the
factory battery-voltage test conditions of 10, 10.5, 11, and 16 V at 0.08 V per
count; `JK08A.diagnostics.md` derives the scale.

## Computed START SIGNAL identity

`0x00038D44` computes a retained start-state Boolean and writes it to
`0xFFFF4185.bit6`. The same Boolean is mirrored through this exact chain:

```text
0xFFFF4185.bit6
  -> 0xFFFF24AE.bit7
  -> 0x0002E0D4
  -> 0xFFFF3342.bit1
  -> DID 0x1302 response bit 1
```

The service-0x22 table entry for DID `0x1302` points to `0xFFFF3342`, with
support mask `0x3F`:

```text
ROM32[0x229F0] = 0xFFFF3342
ROM32[0x229F4] = 0x00011E41
ROM8 [0x11E41] = 0x3F
```

A structured Nissan diagnostic profile names DID `0x1302` bit 1 `START
SIGNAL`. The VQ35HR factory manual independently defines this value as a state
computed by the ECM from engine speed and battery voltage and specifies that
it displays OFF after the engine starts regardless of the physical starter
input. The diagnostic bit mapping and JK08A dataflow therefore bind
`0xFFFF4185.bit6` to computed START SIGNAL rather than to a generic
engine-running or temperature mode.

## Stateful temperature selection

Selector `0x0003967A` reads:

- `S = 0xFFFF4185.bit6`, computed START SIGNAL;
- `B = uint8[0xFFFF1188]`, battery-voltage response raw;
- `L = 0xFFFF24BE.bit6`, the transition latch.

Its complete state transition is:

| Condition | L after call | Return | Selected pair |
|---|:---:|:---:|---|
| `S = 1` and `B < 100` | 0 | 1 | current coolant |
| condition false and `L = 0` | 1 | 1 | current coolant once |
| condition false and `L = 1` | 1 | 0 | zero sentinel |

Raw 100 belongs to the condition-false branch. At 0.08 V per count the
continuously selected coolant case is exactly computed START SIGNAL ON with
battery voltage below 8.00 V.

Coordinator `0x000394B8` maps the return value to these bytes:

| Return | Raw byte | Normalized byte | Meaning |
|:---:|---:|---:|---|
| 1 | `0xFFFF1079` | `0xFFFF1077` | current engine coolant |
| 0 | `0xFFFF107E` | `0xFFFF1080` | stock lifecycle zero sentinel |

The normal initializer clears the fallback bytes, recovery paths clear them,
and the whole-application writer audit finds no runtime producer. A raw zero
from this branch must not be rendered as `-50 deg C`; the coolant conversion
does not apply to the sentinel.

## Diagnostic-readiness consequence

`0x000804CE` sets `0xFFFF422F.bit4` once:

```text
uint8[0xFFFF1071] - uint8[0xFFFF106E] >= 20
```

The first operand is the periodic raw-coolant snapshot. The second is the
periodic selected-raw snapshot. While the primary pair is selected, the two
values are equal. After the transition to the zero sentinel, ordinary coolant
raw values at or above 20 satisfy the difference test. This latch is therefore
a post-start or low-voltage-transition qualifier, not evidence of a second
physical temperature.

The P030 counting-readiness path also consumes the selected pair. On the zero
sentinel branch, `0xFFFF106E = 0` fails its minimum raw threshold of 40 and
the normalized zero index selects lower-threshold value 255. The branch is an
inhibit state, not a physical-temperature observation.

## Evidence boundary

Target CarScanner captures taken immediately after the telemetry drive show
control-module voltage 13.92 V and `[NC] Starter` value 0 at hot idle. The
second observation is consistent with computed START SIGNAL being OFF but is
not proven to be the same DID. Neither observation is synchronized with the
CAN capture or a cranking transition. A synchronized cranking capture would
verify transition timing on the target; it is not required to distinguish the
zero sentinel from a second temperature sensor.
