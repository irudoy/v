# Exact JK08A HCAN1 model

## Scope

This specification records the stock HCAN1 mailbox configuration and the
transmit path used by the exact JK08A stock image registered in
`../rom-images/roms.csv`.
It separates code-proven controller behavior from payload names that still
depend on vehicle capture or homologous diagnostic evidence.

The Renesas SH7058S hardware manual is authoritative for register behavior.
The exact ROM is authoritative for the application configuration.

## Mailbox table

`FUN_000C2FBE` reads 30 four-byte records from ROM `0x0000975A`. Record `i`
configures physical HCAN1 mailbox `i + 1`; mailbox 0 and mailbox 31 are
initialized separately. A record contains:

```text
byte 0: firmware type
byte 1: DLC
byte 2: high byte of STDID << 5
byte 3: low byte of STDID << 5
```

The firmware types have the following exact effects:

| Type | MBC | Direction | Mailbox activity interrupt |
| ---: | ---: | --- | --- |
| 1 | `010` | receive | masked |
| 2 | `010` | receive | enabled |
| 3 | `000` | transmit | masked |
| 4 | `000` | transmit | enabled |
| 5 | `111` | inactive | masked |

The stock records are:

| Physical mailbox | Record | Type | Direction | DLC | Standard ID |
| ---: | ---: | ---: | --- | ---: | ---: |
| 1 | `0x975A` | 3 | TX | 5 | `0x239` |
| 2 | `0x975E` | 1 | RX | 8 | `0x2B0` |
| 3 | `0x9762` | 3 | TX | 3 | `0x6E2` |
| 4 | `0x9766` | 3 | TX | 8 | `0x551` |
| 5 | `0x976A` | 3 | TX | 8 | `0x1F9` |
| 6 | `0x976E` | 3 | TX | 3 | `0x580` |
| 7 | `0x9772` | 3 | TX | 7 | `0x182` |
| 8 | `0x9776` | 3 | TX | 8 | `0x180` |
| 9 | `0x977A` | 3 | TX | 7 | `0x160` |
| 10 | `0x977E` | 1 | RX | 3 | `0x560` |
| 11 | `0x9782` | 1 | RX | 6 | `0x177` |
| 12 | `0x9786` | 1 | RX | 8 | `0x174` |
| 13 | `0x978A` | 1 | RX | 7 | `0x176` |
| 14 | `0x978E` | 1 | RX | 8 | `0x284` |
| 15 | `0x9792` | 1 | RX | 8 | `0x354` |
| 16 | `0x9796` | 1 | RX | 8 | `0x245` |
| 17 | `0x979A` | 1 | RX | 5 | `0x1A5` |
| 18 | `0x979E` | 1 | RX | 8 | `0x5C5` |
| 19 | `0x97A2` | 3 | TX | 4 | `0x512` |
| 20 | `0x97A6` | 1 | RX | 4 | `0x342` |
| 21 | `0x97AA` | 1 | RX | 8 | `0x54C` |
| 22 | `0x97AE` | 1 | RX | 8 | `0x35D` |
| 23 | `0x97B2` | 1 | RX | 8 | `0x358` |
| 24 | `0x97B6` | 1 | RX | 6 | `0x215` |
| 25 | `0x97BA` | 1 | RX | 6 | `0x625` |
| 26 | `0x97BE` | 5 | inactive | 0 | none |
| 27 | `0x97C2` | 1 | RX | 8 | `0x280` |
| 28 | `0x97C6` | 4 | TX | 0 | configured at runtime |
| 29 | `0x97CA` | 2 | RX | 0 | configured at runtime |
| 30 | `0x97CE` | 2 | RX | 0 | configured at runtime |

The table proves configured capability, not traffic observed on a particular
vehicle. A passive capture is required to establish actual presence, period,
jitter, and payload behavior.

## Stock broadcast transmit path

The stock periodic path has two separate stages in the 69-entry table at
`0x21834` that dispatcher `FUN_000209D8` drains while `0xFFFF84B9` bit 4 is
pending. Handler `FUN_0002040C` sets that bit on the same tenth-invocation
phase that makes `FUN_00020DFE` run, so both tables advance once per `Tcan`:

1. `FUN_000C38DE`, entry 61 at `0x00021928`, scans only type-3 records and
   calls `FUN_000C3746` for eligible transmissions.
2. `FUN_000C3DE4`, entry 63 at `0x00021930`, scans only type-3 records and
   serializes the payload for a subsequent scan.

The scan therefore precedes payload preparation in the same scheduler cycle.
Each table record has a ten-byte software state record at
`0xFFFF3AB5 + 10*i`; the last eight bytes are its payload. The submitter copies
that payload into physical mailbox `i + 1` and requests transmission through
TXPR.

Type-4 mailbox 28 does not enter either type-3 scan. Its mailbox-empty event is
handled by the HCAN1 SLE1 interrupt at `FUN_000C7914` in stock firmware.

The stock type-3 frames are:

| Standard ID | DLC | Physical mailbox | Serializer | Relative cadence |
| ---: | ---: | ---: | ---: | ---: |
| `0x160` | 7 | 9 | `0x000C590E` | `Tcan` |
| `0x180` | 8 | 8 | `0x000C577A` | `Tcan` |
| `0x182` | 7 | 7 | `0x000C5558` | `Tcan` |
| `0x1F9` | 8 | 5 | `0x000C5236` | `Tcan` |
| `0x239` | 5 | 1 | `0x000C5ABE` | `2*Tcan` |
| `0x512` | 4 | 19 | `0x000C509E` | `Tcan`, conditional |
| `0x551` | 8 | 4 | `0x000C5372` | `10*Tcan` |
| `0x580` | 3 | 6 | `0x000C5508` | `10*Tcan` |
| `0x6E2` | 3 | 3 | `0x000C5100` | `10*Tcan` |

The code-proven period is `Tcan = 204800 / Pphi` seconds. Passive vehicle
timestamps establish `Pphi = 20 MHz` and `Tcan = 10.24 ms`. Frame `0x512`
additionally requires `0xFFFF4231.bit2`.

## Proven payload boundaries

The following payload claims are sufficiently narrow for use as cross-checks:

- `0x180` bytes 0 and 1 and `0x1F9` bytes 2 and 3 contain big-endian engine
  speed with `RPM = raw / 8`.
- `0x180` byte 5 and the top two bits of byte 6 contain a ten-bit source from
  `0xFFFF279C`, limited to 1000. Accelerator-pedal semantics remain a
  homologous and live-correlation claim.
- `0x239` byte 3 receives one-hot steering-switch code `0xFFFF36D8`.
- `0x551` byte 0 receives coolant snapshot `0xFFFF3FA4`; code 0 is the lower
  saturation and positive codes use the exact `code - 40` transform.
- `0x551` byte 5 bits 4 through 6 contain `0xFFFF40D0 & 7`, the complete
  three-bit ASCD display state. `FUN_00020DFE` latches `0xFFFF40D0` from state
  `0xFFFF4128` through the `0x58`-byte block copy at `0x2132C`. `FUN_000CEABC`
  writes the state at `0xCEE1A`: 6 for `0xFFFF41AD.bit1` or for
  `0xFFFF424C.bit0` with `0xFFFF4251.bit1`, else 4 for `0xFFFF424E.bit1`, else
  5 for `0xFFFF4251.bit1`, else 0. The same function holds SET-lamp flag
  `0xFFFF4252.bit0` set in state 4, clear in states 0 and 5, and inverts it on
  a countdown reloaded with 20 in state 6; `FUN_000CF020` reports CRUISE LAMP in DID
  `0x130E` for states 4, 5, and 6. State 4 is CRUISE with steady SET, state 5
  is CRUISE alone, and state 6 is CRUISE with blinking SET. The block executes
  only while `ROM8[0x8B28]` has bit 0 set and bit 1 clear; stock `0x2B` keeps
  the state at 0.
- `0x551` byte 4 is forced to zero in exact JK08A.
- `0x174` byte 3 high nibble is target gear and its low nibble is current gear.
  Values 1 through 7 become zero-based indices 0 through 6; every other value
  becomes zero. `FUN_000C47EA` publishes the live pair and `FUN_00020DFE`
  snapshots it for request-limiter use.
- `0x174` byte 4 bits 5 through 7 are a TCM status field published to
  `0xFFFF3A2E` by `FUN_000C47EA`; `FUN_0007724C` maps value 3 to
  `0xFFFF419B` bits 3 and 4, and bit 4 is the source of transition-neutralizer
  latch `0xFFFF418F.bit4`. Byte 4 bits 0 through 3 and byte 5 bits 6 and 7 feed
  two further status bytes. The moving-load capture `new-log-full.trc` holds
  value 3 for 850 ms inside one closed-pedal 4-3 downshift and value 0
  everywhere else, including the 19 other gear changes.
  [Transmission request interface](#transmission-request-interface) gives the
  path of value 3 to shared request `0xFFFF19C6` and the road captures of
  2026-09-22. The TCM-side meaning of the field is not established.
- `0x177` byte 2 bits 0 through 2 are a zero-based TCM gear-phase index decoded
  by `FUN_000C4ACE`. Higher bits are independent status flags. The same
  decoder stores byte 4 in `0xFFFF283E` and the shift-code index of byte 5 in
  `0xFFFF282C`: 15 when bit 7 is set and bits 3 through 6 otherwise.

- `0x180` bytes 2 through 4 and `0x160` bytes 0 through 2 carry four 12-bit
  torque-domain words; the next section gives their code path.
- `0x160` byte 3 with the top two bits of byte 4 is ten-bit word `0xFFFF40D2`,
  and byte 5 with the top two bits of byte 6 is its bitwise complement
  `0xFFFF3D6E`.
- `0x182` byte 4 is `min(255, trunc(255 * m / 727))` with
  `m = max(u16[0xFFFF40C6], u16[0xFFFF40E4])` and divisor `ROM16[0x8FF0]`;
  `0xFFFF40C6` is the common opening-coordinate monitor and `0xFFFF40E4` is the
  scheduler latch of `0xFFFF413C`. Byte 3 would carry
  `max(0, s16[0xFFFF18DC]) >> 3`, but stock `ROM8[0x8B32].bit0 = 0` leaves it
  zero.
- `0x182` and `0x1F9` carry no 12-bit torque word. `0x1F9` byte 6 is
  `0xFFFF2332`, the scheduler latch of `0xFFFF23BE`, and the low seven bits of
  byte 7 are `0xFFFF2366`, the latch of `0xFFFF23F2`.

Other field names require a code trace or a synchronized vehicle capture.
Geometry copied from a Z34 frame list is not exact JK08A evidence.

## Torque words in frames `0x160` and `0x180`

`FUN_00079E70` packs the torque-domain words for CAN. `FUN_00079DE4`, entry 58
of the 69-entry pending-task table at `0x00021834`, runs TCM status decoder
`FUN_0007724C`, `FUN_00078A86`, and `FUN_00079824`, then branches through the
trampoline at `0x0007A050` into the packer. Every packed word is

```text
word = clamp(trunc0(source / 5) + 800, 0, 4094)
```

The division is runtime helper `0x00021BBC` with divisor 5. Code 4095 is the
explicit invalid value that `0xFFFF4221.bit2` selects for the two actual-torque
words. One CAN count is five raw torque counts and count 800 is zero.

| Packed word | Frame field | Source |
| --- | --- | --- |
| `0xFFFF3F96` | `0x180` byte 2, byte 3 bits 7..4 | `0xFFFF2380`, latch of net engine torque `0xFFFF240C` |
| `0xFFFF3F90` | `0x180` byte 3 bits 3..0, byte 4 | `0xFFFF4108`, latch of pre-limiter request `0xFFFF4160` |
| `0xFFFF3FA0` | `0x160` byte 0, byte 1 bits 7..4 | `0xFFFF4106`, latch of limited request `0xFFFF415E` |
| `0xFFFF3F98` | `0x160` byte 1 bits 3..0, byte 2 | `max(min(0xFFFF23A8, 0xFFFF2382), 0xFFFF2374)`, latches of `0xFFFF2434`, parallel net torque `0xFFFF240E`, and `0xFFFF2400` |
| `0xFFFF3F9C` | no stock serializer | `0xFFFF237C + 0xFFFF2384`, latches of base term `0xFFFF2408` and accessory sum `0xFFFF2410` |

The latches belong to two scheduler block copies of `FUN_00020DFE`: 140 bytes
`0xFFFF23BC -> 0xFFFF2330` at `0x00021318` and 88 bytes
`0xFFFF4124 -> 0xFFFF40CC` at `0x0002132C`. While `ROM8[0x870C].bit7` and
`0xFFFF4248.bit1` are both set, the source of `0xFFFF3FA0` becomes the maximum
of `0xFFFF4106` and `0xFFFF410A`, the latch of transmission request candidate
`0xFFFF4162`. Stock `ROM8[0x870C] = 0x44` leaves that branch disabled.

The static path from Engine Torque Map `0x10B8E` to frame `0x180` is:

1. `FUN_00065928` writes centered map result `0xFFFF18CA`.
2. `FUN_000659AE` adds base term `0xFFFF2408` and writes state `0xFFFF18CC`.
3. `FUN_00065B08` applies the spark-efficiency factor
   `(256 - F(retard)) / 256` and writes `0xFFFF18CE`. The retard is base
   ignition angle `0xFFFF23F1` minus `0xFFFF11A2`, the latch of clamped timing
   sum `0xFFFF11DA`. `F` is table `0x11D24` over axis `0x1199E`.
4. `FUN_00065CD8` scales by `(6 - n) / 6`, where `n` is the inhibited-cylinder
   count of `FUN_00065D42`, subtracts `0xFFFF2408` and RPM-curve correction
   `0xFFFF14E2`, and writes `0xFFFF18D0`.
5. `FUN_00065DE4` filters the result into `0xFFFF18D2`.
6. `FUN_00065E2C` subtracts accessory sum `0xFFFF2410` and writes `0xFFFF240C`.
7. The scheduler latch `0xFFFF2380`, packer `FUN_00079E70`, and serializer
   `FUN_000C577A` deliver the word to bytes 2 and 3.

Stages 3 through 6 run inside `FUN_00065E54`, entry 96 of the 124-entry
periodic table. The parallel channel `FUN_00065860` repeats stages 3 through 6
with the factor evaluated at latched timing-state byte `0xFFFF2404` and writes
`0xFFFF240E`.

`FUN_00079030` writes both request words. `0xFFFF4160` is duplicated selection
`0xFFFF2438` and `0xFFFF415E` is the minimum of its two bounded request paths;
both are clamped to `[0xFFFF413A, 0xFFFF4138]`. They share the packing of net
engine torque, so the signed request coordinate of `FUN_00079030` is a torque
request in the raw units of `0xFFFF18CC`.

The moving-load capture `new-log-full.trc`, registered in
`../patches/hardware-results.toml`, contains 35,810 complete samples:

| Word | Range in counts | Idle median |
| --- | ---: | ---: |
| `0x180` actual torque | 653..1252 | 820 |
| `0x180` pre-limiter request | 773..1293 | 811 |
| `0x160` limited request | 773..1293 | |
| `0x160` parallel actual torque | 653..1252 | |

- The two actual-torque words differ in 508 samples that form 11 intervals,
  all inside gear changes reported by `0x174` byte 3. In every interval the
  `0x180` word falls below the `0x160` word, by 13 to 194 counts at the deepest
  sample, while the two request words stay equal. The spark-efficiency stage
  of the `0x180` channel is therefore the path that lowers reported torque
  during a gear change.
- The limited request is below the pre-limiter request in 121 samples that
  form five intervals in second gear between 3666 and 4303 RPM, outside gear
  changes, and never above it.
- Closed-pedal samples above 2000 RPM have a median actual-torque word of 724
  counts and a minimum of 694.

No tracked source declares the physical scale of the raw torque domain. At
candidate `0.1 Nm` per raw count one CAN count is `0.5 Nm`, and the
actual-torque range of the capture above spans -73.5..226 Nm.

The road audit `tools/logs/torque_scale_audit.py`, recorded under
`engine_torque_scale.vehicle_2026_09_22` in `../patches/hardware-results.toml`,
bounds the scale with 982 converter-coupled full-pedal points in 12 segments.
Net torque is state `0xFFFF18CC` minus the replayed base term `0xFFFF2408` and
a remainder of 10.0 raw, the median difference from the `0x180` word in 3,883
TRC samples. With the nominal vehicle constants and zero grade, the flywheel
torque that the longitudinal force balance requires is 0.921 of net torque at
`0.1 Nm` per raw count, and 0.766..1.109 over the box of vehicle constants.
Each scale requires a road grade:

| Torque read as flywheel torque | Median grade, nominal constants | Median grade over the box |
| --- | ---: | ---: |
| net at `0.0625 Nm` | -9.14 percent | -13.49..-5.26 percent |
| net at `0.08 Nm` | -3.97 percent | -8.23..1.24 percent |
| net at `0.1 Nm` | 2.69 percent | -3.05..8.2 percent |
| net at `0.125 Nm` | 10.72 percent | 4.14..17.52 percent |
| gross state at `0.1 Nm` | 9.35 percent | 3.48..15.96 percent |

- The 104 neutral-coast windows imply grades of -3.52..6.98 percent at the
  nominal road load, so scale `0.0625 Nm` requires a road steeper than every
  coast.
- Two adjacent gears of one run share the road. The scale at which their
  implied grades agree spans 0.0603..0.1226 Nm per raw count over the six gear
  pairs and the box, so scale `0.125 Nm` lies above every pair.
- Scales `0.08 Nm` and `0.1 Nm` stay compatible. Road grade, vehicle mass,
  driveline efficiency, and the CAN speed scale are not measured, and the runs
  do not separate the two scales. By operator report, the `xxx` captures are
  Map 1 and Map 3 acceleration comparisons on several road stretches, the
  roads of the runs have grade, and neither vehicle mass nor tire pressure is
  known.
- Gross state `0xFFFF18CC` still contains base term `0xFFFF2408`, and read as
  flywheel torque at `0.1 Nm` it requires a median uphill grade of 9.35 percent.

## Transmission request interface

The TCM sends frames `0x174`, `0x176`, and `0x177` back to back every 10 ms.
Besides the gear pair, `0x174` carries two words in the packed torque domain,
word A in byte 0 and byte 1 bits 7..4 and word B in byte 1 bits 3..0 and
byte 2, and the status byte 4 with a rolling counter in bits 0..3 and the
status field in bits 5..7. `0x177` carries byte 4 and the shift code of byte 5.

- `FUN_000C47EA` stores words A and B in `0xFFFF3F8C` and `0xFFFF3F8E`.
  `FUN_0007724C` writes `min(5 * word - 4000, 0x7FFF)`, the inverse of the
  packing above, to `0xFFFF2872` and `0xFFFF2874`, and ORs `0x18` into
  `0xFFFF419B` for status value 3.
- `FUN_00020DFE` copies 260 bytes `0xFFFF277E -> 0xFFFF267A` and 12 bytes
  `0xFFFF4194 -> 0xFFFF4188` on every scheduler pass, so `0xFFFF2770` is the
  latch of word B, `0xFFFF2728` of shift-code index `0xFFFF282C`,
  `0xFFFF273A` of `0x177` byte 4 `0xFFFF283E`, and `0xFFFF418F` of
  `0xFFFF419B`.

Stock `ROM8[0x83C1] = 0x2C` and `ROM8[0x870C] = 0x44` select coordinator
`FUN_00077892`. It and common completion `FUN_000777FA`, which it tail-calls,
feed request boundary `FUN_00079030` on every pass:

1. `0xFFFF4252.bit1` is set on a pass in which `0xFFFF418F.bit4` is set,
   current gear index `0xFFFF1082` differs from target gear index
   `0xFFFF1083`, and inhibit `0xFFFF4253.bit6` is clear. Such a pass loads
   hold byte `0xFFFF4413` with `ROM8[0x8B07] = 30` and advances counter
   `0xFFFF3443`, limited to 255; every other pass clears the counter.
   `FUN_0002040C` decrements the hold byte with its 10.24 ms block, so the hold
   ends 307.2 ms after the last bit-1 pass.
2. `0xFFFF41A6.bit3` is set while bit 1 is set or the hold byte is nonzero.
3. With code `min(0xFFFF2728, 15)`, floor `0xFFFF34DA` is
   `ROM16[0x144F2 + 2 * code] - 0x8000` and `0xFFFF41FD.bit4` is set while bit
   1 is set, the counter is at most `ROM8[0x11E01 + code]`, and
   `0xFFFF245D.bit2` is set or `0xFFFF1210` is at most `ROM16[0x94B6] = 91`;
   otherwise the floor is -32768.
4. On a bit-1 pass, candidate `0xFFFF4162` is the maximum of the floor and the
   target term built from `0xFFFF32EC`, limited to `0xFFFF4138` and, under
   `ROM8[0x8B08].bit0`, to the word B latch `0xFFFF2770`. On every other pass
   it is `min(0xFFFF34A4, 0xFFFF2770)`.
5. While bit 3 is set, `FUN_000777FA` publishes `min(0xFFFF34C8, candidate)`
   as lower bound `0xFFFF3484` and, under `ROM8[0x89C5].bit0`, the candidate as
   upper bound `0xFFFF3480`. `FUN_00079030` raises its working request to the
   lower bound and caps it at the upper bound before its remaining bounds and
   the store to `0xFFFF19C6`.

The stock option bytes `ROM8[0x8B08] = 0x01` and `ROM8[0x89C5] = 0x19` enable
both terms. The stock floor table gives 300 for code 4 and 500 for codes 6, 8,
9, and 11, for 30, 20, 20, 30, and 20 passes; every other code has no floor.
The target term caps `0xFFFF32EC` at the throttle-limit scalar
`ROM16[0x942C]`. `FUN_0006425A` copies the latched byte 4 `0xFFFF273A` to
`0xFFFF3373` under `ROM8[0x8B3F].bit4`, set in stock `0x18`; the path from
`0xFFFF3373` to the timing command is not traced.

The road audit `tools/logs/tcm_shift_audit.py`, recorded under
`transmission_interface.vehicle_2026_09_22` in
`../patches/hardware-results.toml`, checks the instruction bytes of this path
in the image that ran and replays two Map 3 captures with 49 shift events
through gears 1..5 in D and in M1..M5:

- The byte 4 counter advances by one modulo 16 in all 34,187 consecutive TCM
  group pairs, and bit 4 stays clear.
- The status field carries only 0 and 3. Value 3 fills 798 frames of 5
  episodes, all in 4-3 and 3-2 downshifts at 2200..3987.5 RPM, beginning
  30..40 ms after the target change and lasting 1.05..2.051 s. The 6
  downshifts of the same types at 700..1087.5 RPM and the 13 downshifts of
  other types carry none.
- Word A stays 4094. Word B holds 1820 outside the episode windows; it reads
  940 in the one D episode and restarts at 976..1084 after each episode, with
  steps of 4..24 for 0.63..4.232 s.
- The `0x180` request word equals the packed `0xFFFF19C6` in all but 80 of
  33,373 passes. In those passes the packed `0xFFFF19C6` lies below the
  `0x180` request; they form 9 runs inside the episode windows and lie at most
  0.306 s after the latest value-3 frame, inside the 307.2 ms hold.
- `0xFFFF19C6` equals the unpacked word B in 20 of the 22 passes in which that
  word lies below the `0x180` request. In the first episode, a 4-3 downshift at
  2512.5 RPM, `0xFFFF19C6` holds the code-9 floor of 500 for 30 consecutive
  passes from 44.864 s while the `0x180` request reads 1455..1855.
- The `0x160` limited word equals the `0x180` request in all 33,373 passes.
- The 32 bursts of `0x177` byte 4 lie inside shift events. The `0x180`
  actual-torque word falls below the `0x160` parallel word 18..29 ms after the
  onset of each of the 20 upshift bursts; the 12 downshift bursts and the 5
  upshifts without a burst show no divergence, and all 613 divergence passes
  lie in burst or episode windows.
- The `0x177` byte 5 code stays constant through each of the 49 shift events
  and holds `0x78` outside them. The observed codes are 0, 1, 2, and 3 for
  upshifts 1-2 through 4-5, 4 for 2-1, 5 for 3-1, 6 for 3-2, 9 for 4-3, and 13
  for 5-4.
- The highest APP1 at the 19 downshifts in D is 152 raw, and the shared
  throttle target rises by at most 244 raw in the 17 closed-pedal downshifts.

The status path therefore lowers the shared request in these downshifts and
is not seen to raise it. The captures contain no kickdown and no downshift in
D with the pedal pressed. The bound terms `0xFFFF4162`, `0xFFFF3480`, and
`0xFFFF3484`, the floor gate inputs, and target word `0xFFFF32EC` are not
streamed, so a floor or a target bound is visible only where the `0x180`
request exceeds it. The image reads the throttle-limit scalar from
map-switching word `0xFFFF5D28` instead of `ROM16[0x942C]`.

## Passive vehicle capture evidence

Three PEAK PCAN-View TRC 1.1 captures recorded on 2026-08-16 provide the
current vehicle baseline. The nominal bitrate was configured as `500 kbit/s`.
The raw traces remain local and untracked; their hashes and exact firmware
identities are registered in `../patches/hardware-results.toml`.

| Firmware label | Recorded context | Frames | Observed span | Standard IDs |
| --- | --- | ---: | ---: | ---: |
| `1.8` | startup | 30,481 | 15.660 s | 49 |
| `1.8` | idle, ASCD input, and stationary PRND selection | 100,000 | 51.398 s | 44 |
| `1.10` | idle, ASCD input, and stationary Rolling Launch trials | 233,442 | 120.053 s | 44 |

All 363,923 records are received standard data frames. The traces contain no
extended, RTR, warning, or error records. Absence of error records is
conclusive only when PCAN-View error-frame logging was enabled during capture.

The 44 IDs common to the idle and Rolling Launch captures are:

```text
002 160 174 176 177 180 182 1A5 1B4 1F9 215 216 239 245 280 284 285
2A0 2B0 2B3 2B4 2DE 351 354 355 358 35D 421 515 51F 540 541 542 54A
54B 54C 551 560 580 5C5 60D 625 6C2 6E2
```

The startup capture additionally contains `0x71D`, `0x71E`, `0x71F`, `0x72D`,
and `0x72E`. Neither conditional ECM frame `0x512` nor telemetry candidate
`0x6F0` occurs in any endpoint-disabled capture. A separate enabled capture
establishes successful `0x6F0` coexistence under moving load and accepts the ID
for the current tuning-telemetry use. The ID has lower arbitration priority
than all observed stock ECM broadcasts through `0x6E2`, but higher priority
than the five startup-only IDs.

Measured ECM periods agree with the code-derived schedule:

| ID | Median period | P99 range across captures |
| ---: | ---: | ---: |
| `0x160` | 10.2 ms | 10.6 to 10.7 ms |
| `0x180` | 10.2 ms | 11.0 to 11.3 ms |
| `0x182` | 10.2 ms | 11.0 to 11.4 ms |
| `0x1F9` | 10.2 ms | 11.0 to 11.3 ms |
| `0x239` | 20.5 ms | 21.4 to 21.7 ms |
| `0x551` | 102.4 ms | 104.9 to 105.8 ms |
| `0x580` | 102.3 to 102.4 ms | 105.2 to 105.8 ms |
| `0x6E2` | 102.3 to 102.4 ms | 105.5 to 106.0 ms |

The `10*Tcan` median of 102.4 ms yields `Tcan = 10.24 ms`; substitution into
`Tcan = 204800 / Pphi` establishes `Pphi = 20 MHz`. The `1.8` and `1.10`
captures have identical normal-operation ID and DLC sets and no material ECM
period or jitter regression.

Across 18,267 paired scheduler cycles, `0x180` bytes 0 and 1 exactly equal the
following `0x1F9` bytes 2 and 3. The second copy arrives 0.4 to 1.8 ms later.
This independently confirms the shared big-endian engine-speed source and the
`RPM = raw / 8` transform.

Live control correlations establish `0x239` byte 3 values `0x20` for release,
`0x10` for RESUME/ACCEL, `0x08` for SET, and `0x02` for CANCEL. The saved
2026-08-17 trace contains release, SET, and CANCEL; the `0x10` RESUME/ACCEL
code is an operator-confirmed live observation outside that saved trace. Frame
`0x551` byte 5 preserves low nibble `0x02` while injected state 6 appears as
`0x62` during firmware `1.11` map feedback and injected state 7 appears as
`0x72` during Rolling Launch ACTIVE. Exact-target observation establishes that
state 6 illuminates SET together with CRUISE. The `0x8F` immediate of that
firmware clears all three state bits before inserting `0x60`, so the SET lamp
is a property of state 6 on the exact target, not a retained state-7 bit. This
agrees with the stock encoding, in which state 6 is CRUISE with a blinking SET
lamp. State 7 has no stock producer. The current runtime inserts only stock
states: state 4 (`0x42`) for the map feedback ON phase and for Rolling Launch
ACTIVE, state 5 (`0x52`) for a failed held Rolling Launch attempt, and state 0
for the OFF phase and COOLDOWN. The 2026-09-21 road captures of the current
runtime contain 19 map selections: each CANCEL tap while SET is held appears as
a one- or two-frame `0x52` run, and SET release is followed by as many `0x42`
pulses as the selected map number, each two frames ON and two frames OFF. Each
of the six moving CANCEL holds of the mixed Map 3 drive appears as one `0x42`
interval, and switching CRUISE MAIN leaves byte 5 at `0x02`. Operator
observation in the same session establishes that each state-4 map feedback
pulse lights SET together with CRUISE.
[`../patches/hardware-results.toml`](../patches/hardware-results.toml) holds
the observation under `map_switching.feedback_vehicle_2026_09_21`.

The 2026-09-22 Map 2 Rolling Launch TRC carries 1,733 frames of `0x551`, in
which byte 5 holds `0x02` 1,494 times, `0x42` 183 times, and `0x52` 56 times.
Four SET gestures select Maps 5, 2, 1, and 2. Each of the 10 CANCEL taps
appears as a two- or three-frame `0x52` run, and each commit is followed by
as many `0x42` pulses as the selected map number, two frames ON and two frames
OFF. The first ON frame follows SET release by 73.6 to 113.6 ms, and the pulse
starts of one selection lie 407.9 to 409.9 ms apart on average. A 3.196 s
CANCEL hold on Map 1, where Rolling Launch is disabled, shows 31 frames of
`0x52` and no `0x42`, and presses inside the Rolling Launch rearm period keep
byte 5 at `0x02`. Operator observation in the same session establishes that
the Map 5 and Map 2 pulses light SET together with CRUISE, that the CANCEL hold
on Map 1 lights CRUISE alone, and that ASCD does not engage.
[`../patches/hardware-results.toml`](../patches/hardware-results.toml) holds
the observation under `map_switching.feedback_vehicle_2026_09_22`.

Target-vehicle selector observations establish the following `0x421` byte-0
mapping:

| Code | Selector state | Evidence |
| ---: | --- | --- |
| `0x08` | P | saved trace and operator confirmation |
| `0x10` | R | saved trace and operator confirmation |
| `0x18` | N | saved trace and operator confirmation |
| `0x20` | D | saved trace and operator confirmation |
| `0x28` | DS | saved trace and operator confirmation |
| `0x80` | M1 | saved trace and operator confirmation |
| `0x88` | M2 | saved trace and operator confirmation |
| `0x90` | M3 | saved trace and operator confirmation |
| `0x98` | M4 | 2026-09-22 saved trace and operator confirmation |
| `0xA0` | M5 | 2026-09-22 saved trace and operator confirmation |

Transient zero appears between some detents and is not a stable selector
position. No M6 or M7 code is inferred from the numeric pattern.

The same moving capture establishes transmission payload sequencing independent
of selector frame `0x421`:

| Shift observation | `0x174` byte 3 sequence | `0x177` low-three-bit sequence |
| --- | --- | --- |
| downshift 4 to 3 | `0x44 -> 0x34 -> 0x33` | `3 -> 2` between target and current updates |
| downshift 3 to 2 | `0x33 -> 0x23 -> 0x22` | `2 -> 1` between target and current updates |
| upshift 2 to 3 | `0x22 -> 0x32 -> 0x33` | `1 -> 2` between target and current updates |

The high nibble therefore represents target gear and changes before the
low-nibble current gear for both shift directions. In stable first through
fourth gear, the `0x177` value equals current gear minus one; the 2026-09-22
road captures extend this to all 24,009 stable-gear TCM groups of gears 1..5,
where the `0x176` speed ratio matches the current gear in 20,640 of 20,741
groups and another gear in none, and the `0x421` manual position equals the
target gear in all 1,955 manual frames. Its intermediate
timing establishes an operational TCM phase index but does not prove the exact
mechanical engagement boundary. These payloads are received by the ECM:
stock mailbox records `0x9786=01 08 2E 80` and `0x9782=01 06 2E E0` encode
standard IDs `0x174` and `0x177` as `STDID << 5`.

### Enabled telemetry moving-load evidence

The 2026-08-17 `1.11` schema-1 capture records 1,000,000 standard received data frames
over 366.920 seconds with PCAN-View error-frame recording enabled. It contains
286,493 `0x6F0` frames and 35,811 complete `wide54` divisor-1 groups after the
initial partial group. Every accepted tick advances by one. Schema mismatch,
incomplete group, malformed group after synchronization, telemetry status,
snapshot-overrun, transmit-abort, PCAN warning, and PCAN error counts are all
zero. Measured whole-bus load is 57.185% to 69.437% on average, with a
59.006% to 71.650% peak over a rolling 100 ms window.

Frame `0x280` bytes 4 and 5 form a big-endian moving quantity. The homologous
Z34 formula `raw / 100 km/h` yields 0.00 to 68.54 km/h in this target capture
and returns to zero at the operator-confirmed stationary end. This establishes
the target field location and zero state. The firmware confirms the scale:
`FUN_000C4506` divides the word by 10 into `0xFFFF113C`, `FUN_0003A174`
filters it into `0xFFFF115E`, `FUN_0003A254` divides that by 20 into
`0xFFFF118E`, and J1979 Mode 01 PID `0x0D` returns twice that byte as km/h, so
the word is km/h*100 by the ECU's declaration. A synchronized independent
speed reference remains a hardware check of the vehicle, not of the scale.

### Navigation-coordinate boundary

The captured primary CAN network has no verified latitude or longitude
signal. The factory AV/navigation topology connects the GPS antenna directly
to the AV control unit, which calculates vehicle position from GPS, gyro,
vehicle speed, and map data. Its primary-CAN signal chart carries vehicle
context into that unit but does not identify a geographic-coordinate broadcast.
The separate AV communication network was not present in the OBD PCAN capture.

Accordingly, no primary-CAN ID or byte layout is assigned to latitude or
longitude. The dashboard and MLG schema reserve `gps_lat` and `gps_lon` for
UltraLog compatibility, expose their source as unavailable on primary CAN,
and store `NaN` until a separate AV-network or external-GPS capture establishes
an exact binding. Vehicle speed is not integrated into a synthetic route.

## Mailbox-empty interrupt

Vector-table word `0x000203A0` points to `FUN_000C7914`. The ISR checks only
physical mailbox 28, represented by bit `0x1000` in HCAN1 TXACK1 and ABACK1.
It clears HCAN1 IRR bit 8 with word `0x0100`. A successful mailbox-28
transmission calls `FUN_000C6B68`; the abort path does not.

Relevant HCAN1 addresses are:

| Address | Register or field |
| ---: | --- |
| `0xFFFFD808` | IRR1; bit 8 is mailbox empty |
| `0xFFFFD820` | TXPR1 for physical mailboxes 16 through 31 |
| `0xFFFFD830` | TXACK1 |
| `0xFFFFD838` | ABACK1 |
| `0xFFFFD840` | RXPR1; bit 15 is mailbox-31 data-frame pending |
| `0xFFFFD848` | RFPR1; bit 15 is mailbox-31 remote-frame pending |
| `0xFFFFD850` | MBIMR1; zero enables a mailbox activity interrupt |
| `0xFFFFD858` | UMSR1; bit 15 reports mailbox-31 unread-message overflow |
| `0xFFFFDC40` | physical mailbox 26 control base |
| `0xFFFFDC48` | physical mailbox 26 eight-byte data field |
| `0xFFFFDCE0` | physical mailbox 31 control base |
| `0xFFFFDCE8` | physical mailbox 31 eight-byte data field |

For physical mailbox 26, the corresponding TXPR1, TXACK1, ABACK1, and MBIMR1
bit is bit 10, or `0x0400`.

## Safe extension boundary

Physical mailbox 26 is the only table-owned inactive mailbox that can be
promoted without replacing a stock receive or transmit role. The telemetry
runtime uses a type-4 record to configure it as a transmit mailbox and enable
its mailbox-empty interrupt while keeping it outside the stock type-3 scans.

Mailbox 31 is initialized separately as inactive by the complete HCAN1
initializer at `0x000C338A`. The initializer is called through pointers at
`0x0002D7FC` during primary startup and `0x000C3B10` during recovery. The
SH7058S transmit-cancellation limitation applies only when mailbox 31 is a
transmit buffer. The telemetry runtime calls the complete stock initializer,
preserves its return value, and then configures mailbox 31 as MBC `010`, DLC 8,
standard receive for the control ID. Its activity interrupt stays masked.
The direct physical mailbox ID word uses `STDID << 4`, not the table-record
encoding `STDID << 5`; the lower nibble contains RTR, IDE, and extended-ID
bits. Control ID `0x6F1` is therefore written as `0x6F10`.

The stock receive scans cover only the 30 table-backed mailboxes 1 through 30.
Telemetry therefore polls mailbox-31 RXPR1 at its interrupt-disabled scheduler
boundary. It also checks RTR and clears the corresponding RXPR1, RFPR1, and
UMSR1 bits, so a remote request or overflow cannot leave the mailbox blocked.

SH7058S hardware-manual section 17.7.6 permits changing the identifier of a
transmit mailbox whenever its corresponding TXPR bit is clear. After mailbox 26
reports TXACK or ABACK and the handler clears the flag, firmware could write a
different standard ID to `0xFFFFDC40`, update the payload, and request another
transmission without reconfiguring MBC or entering halt mode. Current telemetry
schema 2 does not use this capability: all eleven pages use one build-selected
standard ID and the identifier record remains constant while the endpoint is
active.

The implemented custom telemetry layer always promotes mailbox 26 to type 4 so
a runtime START command can activate a build whose startup flag is disabled.
The transmitter remains idle until streaming is enabled. The layer replaces
the SLE1 vector with one
combined handler that services mailbox 26 and reproduces the complete stock
mailbox-28 success and abort behavior before executing `RTE`. The stock handler
cannot be called with `JSR` because it owns the exception return, and an
indirect tail jump would consume a general register whose entry value the stock
prologue must preserve. The combined handler therefore saves `r0..r7` and PR,
services the bounded queue, executes the exact mailbox-28 side effects, restores
the interrupted state, and returns through one `RTE`.

The custom telemetry implementation that uses this boundary is specified in
`../patches/can-telemetry.md`.
