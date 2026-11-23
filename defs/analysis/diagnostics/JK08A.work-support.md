# JK08A work-support adjustments

This specification binds service `0x3B` to the stored ignition-timing and
idle-speed adjustments. Local identifier (LID) 1 adjusts timing byte
`0xFFFF564C`, which DID `0x112D` publishes. LID 2 adjusts idle byte
`0xFFFF56F6`, whose snapshot `0xFFFF5690` DID `0x112E` publishes. The 2007
G35 sedan manual (VQ35HR) and the VQ25HR section of the 2013 G sedan manual
list the matching CONSULT work-support items `TARGET IGN TIM ADJ` and
`TARGET IDLE RPM ADJ` with condition `IDLE CONDITION` and mark both as not
necessary in the usual service procedure.

The timing adjustment only retards: its range is `-5..0` crank degrees. It
enters the final timing coordinate only inside a coolant, engine-speed, and
base-fuel-schedule window that lies above idle speed. The idle adjustment
only raises: its range is `0..20` counts.

## Service 0x3B

Dispatcher `FUN 0002F928` compares the service identifier with `0x3B` at
`0x2F9EA` and selects handler `FUN 00034194` through literal `0x2FB0C`. The
request carries a LID, a value, and a control byte:

```text
3B LID VALUE CONTROL
0xFFFF8005  LID      -> 0xFFFF4004
0xFFFF8006  VALUE    -> 0xFFFF2B94
0xFFFF8007  CONTROL  -> 0xFFFF2B95
```

LID 0 answers `7B 00` followed by the four bytes at `0x11E3D`, the address
that `ROM32[0x22E30]` holds. The bytes are `C0 00 00 00`; with the first
identifier in the most significant bit, the bitmap advertises LIDs 1 and 2.

LIDs 1 through 20 read `ROM16[0x22E32 + 2 * LID]`. Its high byte is the offset
of the LID's flag byte from `0xFFFF99F4`, its low byte is the apply mask `m`,
and the store mask is `m << 1`. The value slot is `0xFFFF99DB + LID`. LIDs 21
and above answer negative response code `0x12`.

| LID | Table words | Flag byte | Apply bits | Store bits | Value slots |
|---:|---|---:|---|---|---|
| 1 | `0x0001` | `0xFFFF99F4` | 0 | 1 | `0xFFFF99DC` |
| 2 | `0x0004` | `0xFFFF99F4` | 2 | 3 | `0xFFFF99DD` |
| 3 | `0x0010` | `0xFFFF99F4` | 4 | 5 | `0xFFFF99DE` |
| 4 | `0x0040` | `0xFFFF99F4` | 6 | 7 | `0xFFFF99DF` |
| 5..8 | `0x0101..0x0140` | `0xFFFF99F5` | 0, 2, 4, 6 | 1, 3, 5, 7 | `0xFFFF99E0..0xFFFF99E3` |
| 9..12 | `0x0201..0x0240` | `0xFFFF99F6` | 0, 2, 4, 6 | 1, 3, 5, 7 | `0xFFFF99E4..0xFFFF99E7` |
| 13..16 | `0x0301..0x0340` | `0xFFFF99F7` | 0, 2, 4, 6 | 1, 3, 5, 7 | `0xFFFF99E8..0xFFFF99EB` |
| 17..20 | `0x0401..0x0440` | `0xFFFF99F8` | 0, 2, 4, 6 | 1, 3, 5, 7 | `0xFFFF99EC..0xFFFF99EF` |

The control byte selects the operation:

| Control | LIDs 1..3 | LIDs 4..20 |
|---|---|---|
| `0x00` | status copy `0xFFFF40CC` must be `0xFF`; sets the apply bit, clears the store bit, and writes VALUE to the slot | status copy `0xFFFF4112` must be `0xFF`; same bit and slot writes |
| `0x55` | status copy `0xFFFF40CC` must be `0xFF`; sets the store bit, clears the apply bit, and writes VALUE to the slot | negative response `0x12` |
| `0xFF` | clears both bits and zeroes the slot | same |
| other | negative response `0x12` | same |

The positive response is `7B LID` (`FUN 000343B8`). A failed status check
answers with the status byte as the negative response code (`0x34348`), so
the tester receives the reason codes of the status table below. The handler
sends its negative responses through `FUN 00034114`.

The homologous P32M Nissan diagnostic profile defines requests `3B 01 00 00`
(`DataWrite.ADVADJ - RAM`, a signed value at one unit per count) and
`3B 02 00 00` (`DataWrite.CRRCT IDL RPM - RAM`, value `NSET4` at 12.5 rpm per
count), with control values `0 = FLASH`, `85 = UPDATE`, and `255 = FINISH`.
In JK08A code, control `0x55` (85) produces the store edge of the
stored-record section, control `0x00` applies the value without storing it,
and control `0xFF` ends the adjustment.

Diagnostic-state reset `FUN 0002E81A` zeroes flag bytes
`0xFFFF99F4..0xFFFF99F9`, value slots `0xFFFF99DC..0xFFFF99F3`, and
`0xFFFF99D8..0xFFFF99D9` together with the service-0x30 state that
`FUN 0002E76E` clears. Transport state machine `FUN 0002EA0A` calls it at
`0x2EC2A` when transport state `0xFFFF821C` is 8 and `0xFFFF8468` is neither
3 nor 4; `FUN 000CA69C` also calls it. Besides control `0xFF`, this reset
ends an active adjustment.

## Periodic order

Scheduler `FUN 00020DFE` walks 124 pointers at `0x2196C..0x21B58` in its loop
at `0x212EC`. It takes snapshots before the loop and copies result blocks
after it. The adjustment path uses these steps of one pass:

```text
before the loop  0xFFFF1114..0xFFFF1193 -> 0xFFFF1094..0xFFFF1113  (0x20F56)
                 0xFFFF417E -> 0xFFFF4180, 0xFFFF417F -> 0xFFFF417E (0x21076, 0x2107E)
                 0xFFFF4184 -> 0xFFFF4186, 0xFFFF4185 -> 0xFFFF4184 (0x2108C, 0x21092)
                 0xFFFF41A6 -> 0xFFFF41A8                           (0x210BA)
pointer 0x219EC  FUN 00041E84 -> FUN 00043AEE -> FUN 000420B8: idle adjustment
pointer 0x21A80  FUN 00068670: coolant gate, automatic request, status, edges
pointer 0x21A84  FUN 00035318 -> FUN 00034FE4: LIDs 4..20
pointer 0x21A88  FUN 0004D888 -> FUN 0004AAD0: timing adjustment
pointer 0x21B38  FUN 00068254 -> FUN 00068040: stored-record requests
after the loop   0xFFFF4124..0xFFFF417B -> 0xFFFF40CC..0xFFFF4123  (0x2132C)
                 0xFFFF56B2..0xFFFF5717 -> 0xFFFF564C..0xFFFF56B1  (0x21334)
```

The first block copy includes `0xFFFF115A -> 0xFFFF10DA`. The last one
includes the timing adjustment `0xFFFF56B2 -> 0xFFFF564C` and the idle
adjustment `0xFFFF56F6 -> 0xFFFF5690`. The service-0x3B handler therefore
checks the status of the last completed pass.

`FUN 00068670` calls `FUN 00068270`, `FUN 000682A2`, `FUN 000682E0`,
`FUN 000682F6`, `FUN 0006836E`, `FUN 000683B6`, and `FUN 000683CC` in this
order and ends with a branch to `FUN 000685F2`.

## Session status

`FUN 000683CC` writes status `0xFFFF4124` on every pass. The status is the
first failing check in this order:

| Status | Failing check | Meaning of the check |
|---:|---|---|
| `0xA2` | `0xFFFF42D4` nonzero or `0xFFFF4184` bit 6 set | computed START SIGNAL or its 25.6 s afterrun |
| `0xA3` | `0xFFFF41A6` bit 1 clear | raw coolant snapshot `0xFFFF1071` below `ROM8[0x8CC8] = 110` |
| `0xA1` | `0xFFFF41B9` bit 0 set | stored-record read failure |
| `0xA4` | `0xFFFF10DA >= 0xE0` | snapshot of `0xFFFF115A` |
| `0xA5` | `0xFFFF244F` bit 5 clear | states 0 and 1 of `0xFFFF39D8` |
| `0x10` | `0xFFFF41A6` bit 5 set | countdown of state 4 of `FUN 0007F870` |
| `0xA6` | `0xFFFF4184` bit 7 clear | debounced `PLDR` bit 4 low |
| `0xFF` | none | accepted |

`0xFFFF41AA` bit 4 is set exactly when the status is `0xFF`. `0xFFFF4125` is
0 when the status is accepted, 2 when `0xA1` is the only failing check, and 1
otherwise.

`FUN 000683B6` loads `0xFFFF42D4` with `ROM8[0x8283] = 250` on every pass
while computed START SIGNAL `0xFFFF4184` bit 6 is set. The countdown lies in
the 102.4 ms block of base-tick handler `FUN 0002040C`, so status `0xA2`
holds for 25.6 s after the signal clears.

`FUN 00068270` sets `0xFFFF41A6` bit 1 while raw coolant snapshot
`0xFFFF1071` lies within `ROM8[0x8CC8] = 110` and `ROM8[0x8CC7] = 255`. Under
`deg C = raw - 50` the lower bound is 60 deg C.

`FUN 00038618` debounces `PLDR` bit 4 (`0xFFFFF75E`) in state `0xFFFF39C4`.
State 0 moves to 2 and loads countdown `0xFFFF25D5` with 5 when the pin reads
0; state 2 returns to 0 when the pin reads 1 and moves to 1 when the countdown
reaches 0; state 1 returns to 0 when the pin reads 1. Bit 7 of `0xFFFF4185`
is clear in state 1 and set otherwise, and the scheduler copies
`0xFFFF4185` to `0xFFFF4184`. The countdown lies in the 10.24 ms block, so
bit 7 clears after the pin has read 0 for five decrements. `PLDR` bit 4 is the
input that application startup `FUN 00027E24` waits for.

`FUN 0007F870` sets `0xFFFF41A6` bit 5 while its state `0xFFFF3131` is 4 and
countdown `0xFFFF42E5` lies within 1..100 (`0x7FA46`), and clears the bit
when the countdown reaches 0 (`0x7FA4A`). `FUN 00027530` sets `0xFFFF244F`
bit 5 for states 2..4 of `0xFFFF39D8` and clears it for states 0 and 1.

## Adjustment routing

`FUN 000683CC` forms one-pass rising-edge pulses of the store bits and routes
the value slots while the status is accepted:

| LID | Store edge | Previous level | Active while accepted |
|---:|---|---|---|
| 1 | `0xFFFF41AA` bit 2 | `0xFFFF41AA` bit 1 | `0xFFFF424C` bit 4 |
| 2 | `0xFFFF41EE` bit 0 | `0xFFFF41EF` bit 7 | `0xFFFF41EF` bit 3 and `0xFFFF3168 = min(0xFFFF99DD, ROM8[0x8909] = 20)` |
| 3 | `0xFFFF41B3` bit 6 | `0xFFFF41B3` bit 5 | `0xFFFF56BA = 0xFFFF99DE` |

A LID is active while its apply bit or its store bit is set. The LID-2
minimum compares unsigned bytes.

## Timing adjustment

`FUN 0004AAD0` writes `0xFFFF56B2`:

```text
0xFFFF41B9 bit 0 set   -> 0
0xFFFF424C bit 4 set   -> clamp_s8(0xFFFF99DC, ROM8[0x821D] = -5, ROM8[0x821C] = 0)
0xFFFF424C bit 5 set   -> clamp(step(0xFFFF10DA), -5, 0)
otherwise              -> 0xFFFF29C6 when it lies within -5..0, else 0
```

The step of the automatic branch is 0 below `0x20`, `4 - 2 * (x >> 5)` from
`0x20`, and -8 from `0xC0`. The scheduler copies `0xFFFF56B2` to
`0xFFFF564C`.

`FUN 0004DBE8` adds `0xFFFF564C` to the timing sum with coefficient 1 in crank
degrees only while bits 1..5 of `0xFFFF5B31` are clear. The bits carry
hysteresis:

| Bit | Input | Window opens | Window closes |
|---:|---|---|---|
| 1 | raw coolant `0xFFFF1079` | at or above 110 (60 deg C) | below 107 |
| 2 | RPM/25 `0xFFFF11B3` | at or above `ROM8[0x8897] = 48` (1200 rpm) | below 40 (1000 rpm) |
| 3 | RPM/25 `0xFFFF11B3` | at or below 120 (3000 rpm) | above `ROM8[0x8896] = 128` (3200 rpm) |
| 4 | Q7 normalized base fuel schedule `0xFFFF1048` | at or above `ROM8[0x8768] = 64` | below 60 |
| 5 | Q7 normalized base fuel schedule `0xFFFF1048` | at or below 92 | above `ROM8[0x8767] = 96` |

Idle speed lies below the engine-speed window, so the adjustment has no
effect at the work-support condition `IDLE CONDITION`.

## Idle-speed adjustment

`FUN 000420B8` writes `0xFFFF56F6` while stock `ROM8[0x870E] = 0x28` has bit
0 clear:

```text
0xFFFF41B9 bit 0 set   -> 0
0xFFFF41EF bit 3 set   -> min(0xFFFF3168, ROM8[0x8909] = 20)
0xFFFF41EF bit 4 set   -> (0xFFFF10DA >> 5) << 2 below 0xC0, else 4
otherwise              -> 0xFFFF316A when at most 20, else 0
```

All three values are unsigned. The function then raises its local aggregate
to at least `min(255, 0xFFFF56F6 + ROM8[0x12754])` with stock
`ROM8[0x12754] = 44` and passes the aggregate to `FUN 00041F2C`. The
scheduler copies `0xFFFF56F6` to `0xFFFF5690`. The homologous profile scale of
12.5 rpm per count gives the stock limit of 20 counts as 250 rpm.

## Automatic branch

A second request path sets `0xFFFF41AA` bit 0 (timing) or `0xFFFF41EF` bit 6
(idle) without a tester:

- `FUN 000682E0` sets `0xFFFF41AA` bit 3 once `0xFFFF244F` bit 5 is set, and
  no static writer clears it. `FUN 000682F6` runs its checks only while the
  bit is clear, so it decides before the first pass with `0xFFFF244F` bit 5
  set after RAM initialization.
- `FUN 000682F6` requires `0xFFFF41A6` bit 1, at least three changes of
  `0xFFFF417E` bit 6 counted by `FUN 000682A2` in `0xFFFF2B72`, stock
  `ROM8[0x8B34] = 0x81` (bit 1 clear, bit 0 set), stock
  `ROM8[0x8B42] = 0xE0` (bit 4 clear, bits 5 and 6 set), `0xFFFF41B9` bit 0
  clear, and `0xFFFF10DA < 0xE0`. `0xFFFF417E` bit 6 then selects the timing
  request when set and the idle request when clear; a failing condition
  clears both.
- `FUN 0006836E` withdraws both requests when `0xFFFF41A6` bit 1 falls or bit
  5 rises (`0xFFFF41A8` holds the previous-pass byte), the timing request
  while LID 1 is active, and the idle request while LID 2 is active.
- `FUN 000685F2` copies the timing request to `0xFFFF424C` bit 5 and the idle
  request to `0xFFFF41EF` bit 4 when `0xFFFF42D4` is zero, `0xFFFF4184` bit 6
  is clear, `0xFFFF41A6` bit 1 is set, `0xFFFF244F` bit 5 is set,
  `0xFFFF41A6` bit 5 is clear, and `0xFFFF4184` bit 7 is set; the idle copy
  also needs stock-clear `ROM8[0x870E]` bit 0. Otherwise, with `0xFFFF4184`
  bit 7 set, it clears both bits.
- A pending request with `0xFFFF4184` bit 7 clear latches a stored-record
  write.

The branch is dormant in JK08A. `0xFFFF417E` is the scheduler copy of
`0xFFFF417F`, and no static writer changes `0xFFFF417F` bit 6: its writers
change bit 2 (`FUN 00038618`), bit 3 (`FUN 0006EFBC`), bit 4
(`FUN 00078A86`), bit 5 (`FUN 00027530`), and bit 7 (`FUN 0002F66E`,
`FUN 00032DC8`). The change counter therefore stays below 3. `0xFFFF10DA` is
the scheduler snapshot of `0xFFFF115A`, which has no static writer and which
startup initializer `FUN 00027C50` zeroes; its only other static reader,
`FUN 000703B2`, reads it only while stock-clear `ROM8[0x8B36]` bit 6 is set.
Without a writer, status `0xA4` does not occur and both step values are 0. A
static census does not exclude an interrupt, DMA, or peripheral writer of
either cell.

## Stored records

`FUN 00068040` requests record writes through key byte `0xFFFF2CD6`, record
word `0xFFFF2CE2`, and writer flag `0xFFFF9A65` bit 5. On entry,
`0xFFFF9A65` bit 4 clears bits 4 and 5. Each action below runs only while bit
5 is clear and then sets it:

| Trigger | Set by | Action |
|---|---|---|
| latch `0xFFFF41AB` bit 7 | LID-1 store edge with accepted status, or pending timing request with `0xFFFF4184` bit 7 clear | `0xFFFF29C6 = 0xFFFF56B2`; record `0x74` with high byte `0xFFFF56B2` and low byte `0xFFFF316A`; clears `0xFFFF41AA` bit 0 and the latch |
| latch `0xFFFF41EF` bit 5 | LID-2 store edge with accepted status, or pending idle request with `0xFFFF4184` bit 7 clear | `0xFFFF316A = 0xFFFF3168`; record `0x74` with high byte `0xFFFF29C6` and low byte `0xFFFF316A`; clears `0xFFFF41EF` bits 6 and 5 |
| edge `0xFFFF41B3` bit 6 | LID-3 store edge | record `0x7E` with high byte `0xFFFF56BA` and low byte 0 |

The two latches wait while the writer is busy. The LID-3 edge lasts one pass
and is dropped when the writer is busy in that pass. Record `0x74` holds the
timing adjustment in its high byte and the idle adjustment in its low byte.
After these actions the same function requests records `0x73`, `0x4E`, and
`0x70` for other state.

Startup step `FUN 000686B8`, called by `FUN 0002D120`, reads records `0x74`
and `0x7E` through stable-read wrapper `FUN 0006727C` while `0xFFFF41B9` bit 0
is clear. The wrapper compares two reads of SCI2 read primitive
`FUN 00066BD0` for up to `ROM8[0x8A37] = 3` attempts, clears `0xFFFF41B9`
bit 0 on agreement, and sets it when no attempt agrees. When the bit is clear
after both reads, the step loads `0xFFFF29C6` and `0xFFFF316A` from record
`0x74` and `0xFFFF56BA` from the high byte of record `0x7E`.

## LID 3 and LIDs 4..20

LID 3 writes `0xFFFF99DE`. While LID 3 is active and the status is accepted,
`FUN 000683CC` copies the slot to `0xFFFF56BA`, and the LID-3 store edge
writes record `0x7E`. `0xFFFF56BA` is the signed input of the alternative
common-MAF-correction mode of `FUN 0003B320`, which stock flags disable. The
LID-0 bitmap does not advertise LID 3.

LIDs 4..20 use status `0xFFFF416A`, which `FUN 00034FE4` writes at pointer
`0x21A84` through thunk `FUN 00035318`: `0xFF` when `0xFFFF41B9` bit 0 is
clear and `0xFFFF4184` bit 7 is set, otherwise `0xA1` when `0xFFFF41B9` bit 0
is set and `0xA6` when it is clear. `0xFFFF420D` bit 0 marks acceptance.
While accepted, each active LID 4..20 copies its slot
`0xFFFF99DF..0xFFFF99EF` to `0xFFFF5564..0xFFFF5574`. `FUN 00031718` and
`FUN 00037020` read that block; its calibrated quantities are not identified.
The LID-0 bitmap does not advertise LIDs 4..20.

## Diagnostic identity

The exact service-0x22 pointer table binds both adjustments:

```text
ROM32[0x22760] = 0xFFFF564C   # DID 0x112D, timing adjustment
ROM32[0x22764] = 0xFFFF5690   # DID 0x112E, idle adjustment snapshot
```

Homologous sources give consistent names. The P32M profile names DID
`0x112D` `CRRCTD IGN TIM` and DID `0x112E` `CRRCT IDL RPM` at 12.5 rpm per
count. The 370Z CAN logger names them `Corrected Ignition Timing Advance` and
`Corrected Idle RPM`, and the obd2tools parameter list names them as the
ignition-timing and idle-speed corrections.

The factory work-support rows are catalog operations
`nissan-esm-2007-g35-sedan-v1:engine-control-system:p0116:work_support:target-ign-tim-adj-0cac96d2`,
`nissan-esm-2007-g35-sedan-v1:engine-control-system:p0116:work_support:target-idle-rpm-adj-96472b34`,
`nissan-esm-2013-g37-sedan-v1:engine-control-system:p0732:work_support:target-ign-tim-adj-0cac96d2`,
and
`nissan-esm-2013-g37-sedan-v1:engine-control-system:p0732:work_support:target-idle-rpm-adj-96472b34`.

## Evidence boundary

The JK08A code proves the request format, status checks, routing, window,
and record layout. No tester capture of service `0x3B` exists for the target
vehicle, so the assignment of the CONSULT work-support screens to LIDs 1 and
2 rests on the homologous request names and the DID identity. The unit of the
idle aggregate of `FUN 000420B8` and the target idle speed that results from
the idle adjustment are not code-proven. The SCI2 memory device behind
`FUN 00066BD0` is not traced on the board.
