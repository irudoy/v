# JK08A computed START SIGNAL and selected-temperature gate

This specification binds the selected-temperature path to its exact runtime
and diagnostic identities. The selected pair is the engine coolant temperature
latched at engine start. Its hold branch re-reads the previous-pass image of
the pair, not a second physical temperature sensor.

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
| condition false and `L = 1` | 1 | 0 | selected pair of the previous pass |

Raw 100 belongs to the condition-false branch. At 0.08 V per count the
continuously selected coolant case is exactly computed START SIGNAL ON with
battery voltage below 8.00 V.

Coordinator `0x000394B8` maps the return value to these bytes:

| Return | Raw byte | Normalized byte | Meaning |
|:---:|---:|---:|---|
| 1 | `0xFFFF1079` | `0xFFFF1077` | current engine coolant |
| 0 | `0xFFFF107E` | `0xFFFF1080` | previous-pass image of the selected pair |

## Previous-pass block

The coordinator is entry 24 of the 69-entry periodic table at `0x21834`.
Dispatcher `0x000209D8` runs the table while `0xFFFF84B9.bit4` is pending;
periodic handler `0x0002040C` sets that bit every tenth base interrupt, the
10.24 ms cadence of the snapshot scheduler. After the last entry the dispatcher
calls block-copy helper `0x00022558`:

```text
0x00020CAE  r1 = ROM32[0x20E6C] = 0xFFFF107A    # destination
0x00020CB8  r2 = ROM32[0x20E74] = 0xFFFF1072    # source
0x00020CBA  jsr 0x00022558
0x00020CBC  r0 = 8                              # length, delay slot
```

Every byte of `0xFFFF1072..0xFFFF1079` therefore has a previous-pass image in
`0xFFFF107A..0xFFFF1081`:

| Current | Image | Content | Reader of the image |
|---:|---:|---|---|
| `0xFFFF1072` | `0xFFFF107A` | RPM-drop publication byte | none |
| `0xFFFF1073` | `0xFFFF107B` | start-latched fuel temperature | hold branch of `0x00039788` |
| `0xFFFF1074` | `0xFFFF107C` | fuel temperature, DID `0x1104` | fall-rate limiter `0x00039874` |
| `0xFFFF1075` | `0xFFFF107D` | absolute throttle byte | `0x00037C1A` |
| `0xFFFF1076` | `0xFFFF107E` | selected raw temperature | hold branch of `0x000394B8` |
| `0xFFFF1077` | `0xFFFF107F` | normalized coolant index | `0x00038618` |
| `0xFFFF1078` | `0xFFFF1080` | selected normalized temperature | hold branch of `0x000394B8` |
| `0xFFFF1079` | `0xFFFF1081` | engine coolant, DID `0x1101` | fall-rate limiter `0x00039588` |

The helper writes through its destination pointer, so the image block has no
literal-address store. Startup initializer `0x00027C50` and clear services
`0x0002FC24` and `0x00034B70` zero it inside their RAM spans.

The hold branch keeps the selected pair at the value of its last coolant
selection. RAM initialization clears `L`, so the first pass selects coolant
once, before the hold branch first reads the image. A computed START SIGNAL
interval with battery voltage below 8.00 V tracks coolant and ends with one
more selection. The selected pair is the engine coolant temperature at engine
start: the raw byte has the coolant scale `deg C = raw - 50`, and the
normalized byte has the normalized coolant scale of `0x00039634`.

Two more gates repeat the state machine with their own latches:

| Gate | Latch | Selected byte | Source | Image on the hold branch |
|---|---|---:|---:|---:|
| `0x0003967A` | `0xFFFF24BE.bit6` | `0xFFFF1076`, `0xFFFF1078` | `0xFFFF1079`, `0xFFFF1077` | `0xFFFF107E`, `0xFFFF1080` |
| `0x0003972A` | `0xFFFF4238.bit1` | `0xFFFF39AE` | `0xFFFF1079` | `0xFFFF39BE` |
| `0x00039902` | `0xFFFF24BD.bit5` | `0xFFFF1073` | `0xFFFF1074` | `0xFFFF107B` |

The image `0xFFFF39BE` comes from the 16-byte copy `0xFFFF39A4..0xFFFF39B3`
to `0xFFFF39B4..0xFFFF39C3`, which the same dispatcher branch performs at
`0x00020CE6`.

## Start-temperature consumers

`0x000804CE` sets `0xFFFF422F.bit4` once:

```text
uint8[0xFFFF1071] - uint8[0xFFFF106E] >= 20
```

The first operand is the periodic raw-coolant snapshot. The second is the
periodic snapshot of the selected raw byte, the coolant temperature at engine
start. The same function sets `0xFFFF422E.bit7` once RPM/12.5 reaches `0x20`
and `0xFFFF422F.bit5` once raw coolant reaches `0x78`. Under
`deg C = raw - 50` the three latches are an engine speed of 400 rpm, a coolant
rise of 20 deg C after engine start, and a coolant temperature of 70 deg C.
The 2013 G factory manual defines driving pattern A by the same three
conditions and the ignition switch turned from ON to OFF. The match binds
`0xFFFF106E` to the coolant temperature at engine start and confirms one
deg C per count of the raw coolant byte.

The P030 counting-readiness path consumes the selected pair as a start
temperature. It requires `0xFFFF106E >= 40`, a start temperature of at least
-10 deg C, and takes the lower coolant threshold from map `0x12DE2` at
`min(2 * 0xFFFF1070, 255)`. From a start temperature of -10 deg C the stock
cells return raw 43, a current coolant temperature of at least -7 deg C.

## Evidence boundary

Target CarScanner captures taken immediately after the telemetry drive show
control-module voltage 13.92 V and `[NC] Starter` value 0 at hot idle. The
second observation is consistent with computed START SIGNAL being OFF but is
not proven to be the same DID. Neither observation is synchronized with the
CAN capture or a cranking transition. A synchronized cranking capture would
verify transition timing on the target; the start-latch identity of the
selected pair does not depend on it.
