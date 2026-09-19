# JK08A diagnostic publication and monitor model

## Scope

This document describes the stable relationships between exact JK08A firmware
data flow and the source-preserving diagnostic corpus. Addressed claims,
evidence sites, source-claim identities, applicability, ROM scope, and review
priority remain canonical in `JK08A.diagnostic-bindings.csv`, `JK08A.funcs.csv`,
`JK08A.vars.csv`, `JK08A.findings.csv`, and `JK08A.dtc.csv`.

The static layer distinguishes three questions:

1. Which exact firmware object publishes or consumes a value?
2. Which source-specific diagnostic claim names or scales that value?
3. Does hardware on the target ECU confirm the physical interpretation?

A code-proven pointer or dispatcher answers the first question. A factory or
community source answers the second with its own applicability. Only a bench or
vehicle observation answers the third.

## UDS data publication

`FUN_0003235C` is the exact ReadDataByIdentifier publisher for the reviewed
service `0x22` ranges. Its pointer tables bind selected DIDs to RAM bytes or
words. The function contract and every reviewed pointer site are recorded once
in `JK08A.funcs.csv`; individual semantic joins are recorded in
`JK08A.diagnostic-bindings.csv`.

The current reviewed model establishes these durable behaviors:

- multiple ignition-timing DIDs are aliases for one published byte rather than
  independent timing states;
- fuel-trim DIDs return the high bytes of four internal Q8.8-percent words and
  agree with the exact Mode 01 STFT/LTFT ordering;
- injection-pulse DIDs return the first two words of the six-channel calculated
  pulse array described in `JK08A.fuel.md`;
- intake-cam actual timing, exhaust-cam actual timing, and their common targets
  have distinct exact RAM publications;
- a returned value can have mode-dependent transforms, so one affine diagnostic
  formula is not automatically a universal internal representation.

The exact cam-timing pointer bindings currently are:

| DID | Exact returned byte | Firmware role |
|---|---:|---|
| `0x1164` | `0xFFFF2324` | bank-1 actual exhaust-cam timing |
| `0x1165` | `0xFFFF2325` | bank-2 actual exhaust-cam timing |
| `0x1166` | `0xFFFF2327` | common conditioned exhaust-cam target |
| `0x122F` | `0xFFFF1AAC` | bank-1 exhaust-VTC duty |
| `0x1230` | `0xFFFF1AAE` | bank-2 exhaust-VTC duty |

`FUN_0008F168` independently consumes the actual and target exhaust values in
the monitor paths associated with P1078/P1084 and P0014/P0024. This closes the
subsystem identity without relying on a community label. The centered-byte
arithmetic and the `(raw - 128) * 0.5 degCA` conversion are exact: the
channel-1A capture handlers count the cam edge phases in 0.5 crank degrees, as
recorded in the CVTC note.

Exact pointer identity does not establish an ECM terminal, peripheral channel,
or physical unit. Those remain separate claims and are not promoted by name
similarity.

### Declared service-0x22 inventory

`tools/diagnostics/sid22_inventory.py` SHA-locks the exact JK08A ROM, the
1,256-byte publisher at `0x0003235C`, and all six pointer-table extents. It
reconstructs only declared response width and byte sources; physical names and
conversions remain in reviewed diagnostic bindings.

The publisher accepts response modes `0x04` and `0x06` and dispatches six DID
families:

| DID family | Pointer table | Record shape | Declared entries | Publisher bound |
|---|---|---|---:|---|
| `0x11xx` | `0x226AC..0x2289C` | 124 records, 4-byte stride; lows `00`, `20`, `40`, and `60` return four sequential bytes, other declared records return one byte | 82 | none |
| `0x12xx` | `0x2289C..0x229E0` | 81 records, 4-byte stride; lows `00`, `20`, and `40` return four sequential bytes, other declared records return two sequential bytes | 60 | none |
| `0x13xx` | `0x229E0..0x22A88` | 21 records, 8-byte stride; low `00` returns four sequential bytes, other records return two independently addressed bytes | 20 | low byte `<=0x14` |
| `0x14xx` | `0x22A88..0x22B0C` | 33 records, 4-byte stride; lows `00` and `20` return four sequential bytes, other declared records return one byte | 31 | none |
| `0x15xx` | `0x22B0C..0x22BAC` | 20 records, 8-byte stride; low `00` returns four sequential bytes, other records return two independently addressed bytes | 19 | low byte `<=0x13` |
| `0x16xx` | `0x22BB0..0x22CB0` | 64 records, 4-byte stride; lows `00` and `20` return four sequential bytes, other declared records return one byte | 64 | low byte `<=0x3F` |

The resulting exact inventory contains 276 declared DIDs. A pointer value of
`0xFFFFFFFF` suppresses an ordinary record. DID `0x120B` is the single special
case: its sentinel slot selects a dedicated dynamic two-byte publisher branch
and therefore remains part of the declared inventory.

Families `0x11`, `0x12`, and `0x14` do not check the low byte against their
table extent before calculating a record address. Unsupported low bytes can
therefore index records in an adjacent ROM table. This is read-side aliasing,
not evidence that the resulting DID is declared or semantically valid. Runtime
profiles use only inventoried DIDs and never rely on that behavior.

## J1979 Mode 01 publication

`FUN_00035856`, reached from `FUN_00035634` while the session selector
`0xFFFF8491` equals 1, answers J1979 Mode 01 requests. Each PID converter is
exact code, and the standard definition of the PID fixes the engineering scale
that the ECU declares for the internal source. The declared scales are the
ECU's own conversions, not hardware measurements: the airflow is the firmware
model of the transfer curves, and the temperatures are transfer codes of the
ADC samples. PID `0x01` masks `0xFFFF493E`, and PID `0x03` returns the
fuel-system status bytes `0xFFFF3F2C` and `0xFFFF3F2D`.

| PID | Source | Exact arithmetic | J1979 definition | Declared internal scale |
|---|---|---|---|---|
| `0x04` | `0xFFFF413E` | byte unchanged | `A * 100 / 255` percent load | 100/255 percent per count |
| `0x05` | `0xFFFF3FA4` | byte unchanged; `FUN_0008092E` forms the snapshot as `max(lookup(0x12DEA, 0xFFFF1186) - 10, 0)` | `A - 40` degC | the lookup output `0xFFFF1079` is `degC + 50` |
| `0x06`..`0x09` | `0xFFFF22DC`, `0xFFFF2302`, `0xFFFF22DE`, `0xFFFF2304` | `min(255, floor(word / 200))` | `(A - 128) * 100 / 128` percent trim | Q8.8 percent words: STFT bank 1, LTFT bank 1, STFT bank 2, LTFT bank 2 |
| `0x0B` | `0xFFFF16D2` word | `floor((word * 118 + 98304) / 65536)` | `A` kPa | word is `(kPa - 1.5) * 65536 / 118` |
| `0x0C` | `0xFFFF11F4` word | `min(65535, 50 * word)` as two bytes | `(256 A + B) / 4` RPM | 12.5 RPM per count |
| `0x0D` | `0xFFFF118E` | `min(255, 2 * byte)` | `A` km/h | 2 km/h per count; the chain is CAN `0x280` bytes 4..5 (km/h*100) -> `0xFFFF113C` (/10) -> `0xFFFF115E` (filter) -> /20 |
| `0x0E` | `0xFFFF2022` | `clamp((110 - byte) * 2, -128..127) + 128` with `ROM8[0x83D5] = 110` | `A / 2 - 64` degrees before TDC | `110 - raw` is crank degrees of advance, and `0xFFFF11D4` is degBTDC |
| `0x0F` | `0xFFFF3F41` | byte unchanged; `FUN_0003D832` copies lane 0 of `0xFFFF3F42`, where `FUN_0003D4A8` writes `max(lookup(0x12DEA, uint8(0xFFFF1D58 >> 2)) - 10, 0)` | `A - 40` degC | the transfer code is `degC + 50`, and AN1 lane 0 is the intake-air-temperature channel |
| `0x10` | `0xFFFF105C` word | `(105 * word) >> 8` as two bytes with `ROM8[0x83EC] = 105`; DID `0x1209` word `0xFFFF3852` is the same product | `(256 A + B) / 100` g/s | 105/25600 g/s per count of the total, and `0xFFFF3852` is g/s*100 |
| `0x11` | `0xFFFF1075` | byte unchanged | `A * 100 / 255` percent | absolute throttle, 100/255 percent per count |
| `0x13` | `ROM8[0x8936]` | byte unchanged | oxygen sensors present | stock 0: no sensors declared |
| `0x14`..`0x19` | `0xFFFF1D44 / 5`, `0xFFFF118C`, `0xFFFF1D46 / 5`, `0xFFFF118D` with the bank trims | helper `FUN_000357DC` | `A * 0.005` V and trim | inactive: the helper answers negatively while `ROM8[0x8936]` is zero |
| `0x1C` | `ROM8[0x8696]` | byte unchanged | OBD standard | stock 0 |
| `0x21` | `0xFFFF560C` longword | `floor(value / 2548)`, `0xFFFF` from `0x09F3F60C` | km with MIL on | 1/2548 km per count |

The trim division by 200 converts internal percent*256 into the J1979 byte
domain, where 100 percent is raw 128, and independently establishes the
identities and scale of DIDs `0x1123` through `0x1126`. The airflow declaration
is the reference for the MAF transfer curves `0x14274` and `0x141F4`: their
outputs sum into `0xFFFF105C`, so one output count is `105 / 25600` g/s with
the stock factor. The A2L unit of `MAF Factor` (`x * 0.0001` kg/hr) yields
0.0109 kg/hr per count of the same total against 0.01477 kg/hr from the PID
declaration; the discrepancy is recorded at the finding.

## Dynamic local-identifier streaming

The exact JK08A diagnostic dispatcher routes SID `0xAC` to `FUN_00033810`
and SID `0x21` to `FUN_000328C0`. Together they implement a stock, volatile
byte-gather stream. This mechanism changes diagnostic-session RAM only; it
does not patch executable code or flash and it is not a periodic broadcast-CAN
publisher.

The following byte strings are application payloads. KWP format, target and
source headers, length encoding, and checksum remain transport framing and are
not included:

```text
Define:   AC 81 (83 A3 A2 A1 A0)+
Success:  EC 81

Read:     21 81 TXM NRS
Response: 61 81 DATA...
```

For descriptor `0x83`, `A3` is the most-significant address byte and `A0` is
the least-significant byte. `FUN_0002F2D4` reconstructs the address in
big-endian order. Each descriptor adds one 32-bit source pointer and exactly
one response byte. A two-byte word therefore needs two descriptors, normally
for `address` and `address + 1`; a four-byte value needs four. Response bytes
retain descriptor order.

A fresh `0x81` definition resets the output count. Before each descriptor the
parser requires the current count to be at most `0x3D`, so a definition made
only from `0x83` descriptors can contain 62 output bytes. Compact descriptor
`0x01` expands a predefined local ID to four consecutive pointers. Descriptor
`0x02` selects the predefined `0x11` through `0x16` table families and expands
the selected entry to its declared width. Those compact forms can add multiple
output bytes at one parser step; arbitrary-address logger profiles should use
`0x83` and enforce the 62-byte limit themselves.

The resulting pointer array begins at `0xFFFF9820`, its byte count is stored at
`0xFFFF9920`, and the active dynamic LID is stored at `0xFFFF3EE2`. Successful
definition returns only `EC 81`; the ECU does not echo the pointer schema, so
the client must retain the exact ordered profile. The definition is runtime
state and must be recreated after diagnostic-session or ECU reset.

### Read validation and memory safety

The dynamic read path accepts only a LID above `0x80` that equals the active
value. It accepts transmission modes `0x04` and `0x06`; other modes, a stale
LID, malformed definition, or rejected address produce NRC `0x12` through the
common negative-response builder.

SID `0xAC` does not apply a general memory-map or side-effect check while
storing a pointer. SID `0x21` treats `0xFFFE0000..0xFFFE0FFF` as a special
asynchronous range, rejects `0xFFFE1000..0xFFFEFFFF`, and directly
byte-dereferences other entries. Direct dereference is not a safety guarantee:
an arbitrary peripheral or invalid address can have side effects or fault.
Hardware use is limited to reviewed, side-effect-free exact-RAM sources.

### Transmission modes

`FUN_000328C0` stores `TXM` at `0xFFFF8212` and `NRS` at `0xFFFF8214` before
building the first response.

- Mode `0x04` increments finite-response counter `0xFFFF8213` in transmit
  completion handler `FUN_0002F12C`. Responses continue until the counter
  reaches `NRS`, then the handler clears both counter and mode. Intermediate
  transmissions use `FUN_0002F866` without redispatching SID `0x21`; this path
  does not establish a fresh pointer-list read between responses.
- Mode `0x06` bypasses the `NRS` comparison. The transmit-complete handler sets
  `0xFFFF82E4.bit7`; diagnostic state machine `FUN_0002EA0A` clears the flag,
  transitions through its response states, and calls dispatcher
  `FUN_0002F928`. The dispatcher invokes `FUN_000328C0` again, rebuilding
  `61 81 DATA...` from the current source bytes for every response. `NRS` is
  stored but does not terminate this stream.

Mode `0x06` is therefore the stock mechanism for successive live samples. It
removes one request per parameter and reads all selected bytes into one fixed
schema, but response width still consumes serial bandwidth. Continuous does
not mean one new physical measurement per response: freshness is bounded by
both the response cadence and each source variable's producer cadence.

### Snapshot boundary

`FUN_000328C0` traverses `0xFFFF9820` and dereferences each pointer in order.
It does not mask interrupts or copy the selected sources into an atomic staging
buffer first. An interrupt or scheduled producer can therefore update part of
a multi-byte value or one group of related values while the response is being
built. Byte order is deterministic, but time coherence is not.

The unmodified-ROM stream is suitable for discovery and compact tuning logs
when tearing is measured and tolerated. A coherent high-rate profile requires
an executable change that captures selected values at one known scheduler
boundary and exposes sequence, ECU tick, validity, and age. Such a patch falls
under the repository's independent SH-2E executable-verification gate.

Static code establishes service grammar and repeat behavior but not the active
vehicle's KWP framing, selected SCI baud rate, adapter turnaround, or achieved
cadence. Those remain bench measurements using raw request and response
timestamps before engine use.

## Analog sensor count domain and voltage scale

The on-chip A/D unit returns ten-bit results left-aligned in a sixteen-bit
register. Samplers `FUN_0002862C` and `FUN_000280D8` shift each aligned result
right by six, so every analog diagnostic word is an unsigned count in
`0..1023`. Three reviewed transforms sit on top of that domain:

- `FUN_0003C408` multiplies the MAF samples by Q1.15 coefficient `0xFFFF4970`,
  saturates to `0xFFFF`, and adds one when the sample is full scale `0x03FF`,
  so the published span is `0..1024`;
- `FUN_0003E4CC` subtracts the paired throttle samples from `0x0400`, which
  inverts throttle-position sensor 2 about the same full scale;
- the second accelerator-pedal word carries twice its sample, which the factory
  parameter list states as internal conversion of the sensor 2 signal.

No reviewed instruction converts any of these words to volts. The Mode 01
dispatcher ends at PID `0x21` and declares no voltage PID, and the oxygen
sensor voltage PIDs stay inactive while `ROM8[0x8936]` is zero. The unit is
therefore a property of the display, and the ROM range limits fix it against
the factory reference values.

| Monitor | Word | Accepted counts | At 5 mV per count |
| --- | --- | --- | --- |
| `0x000A7040` | `0xFFFF269E` | `ROM16[0x8FFC] = 60` .. `ROM16[0x8FF8] = 964` | 0.30 .. 4.82 V |
| `0x000A70F0` | `0xFFFF26A2` | `ROM16[0x8FFC] = 60` .. `ROM16[0x8FFA] = 1000` | 0.30 .. 5.00 V |
| `0x000A7418` | `0xFFFF2756`, `0xFFFF2758` | `ROM16[0x9550] = 60` .. `ROM16[0x954E] = 964` | 0.30 .. 4.82 V |
| `0x000A75C0` | `0xFFFF275E`, `0xFFFF2760` | `ROM16[0x9550] = 60` .. `ROM16[0x954E] = 964` | 0.30 .. 4.82 V |

The factory documents give the matching acceptance bands: accelerator-pedal
sensor 1 reads 0.5 .. 1.0 V released and 4.2 .. 4.8 V depressed, pedal sensor 2
reads half of that at the ECM terminal and the same band on the display,
throttle-position sensor 1 stays above 0.36 V released and below 4.75 V
depressed, and the paired sensor 2 mirrors those two criteria.

At 5 mV per count every limit sits just outside its band: 4.82 V clears the
4.8 V pedal maximum and the 4.75 V throttle maximum, 5.00 V is exactly twice
the 2.5 V terminal maximum of pedal sensor 2, and 0.30 V clears the 0.36 V
released minimum from below. A reference of 5.0 V over the full ten-bit span
puts the same limits at 4.707 V, 4.707 V, and 4.883 V, which are inside the
factory bands; the ECU would then set P2123, P0223, or P2128 on a vehicle whose
readings the factory tables call normal. Two further constants agree with 5 mV
per count: the `0x0400` complement spans 5.12 V, and the two mirrored throttle
criteria span 5.11 V; the MAF calibration sequence `FUN_000662F6` and
`FUN_0006635C` returns stock coefficient `0x8000` at an eight-sample average of
900 counts and accepts 856 .. 944 counts, which is a design point of 4.50 V
with a symmetric window of 4.28 .. 4.72 V.

Target-vehicle recordings agree with the same reading. The released pedal words
hold 151 counts, or 0.755 V against the 0.5 .. 1.0 V band, and reach 940 counts
at full stroke, or 4.70 V against the 4.2 .. 4.8 V band. The MAF words read 85
counts with the engine stopped, or 0.425 V against an expected 0.4 V, and 197
.. 241 counts at warm idle, or 0.99 .. 1.21 V against the 0.8 .. 1.1 V band of
the homologous 3.5-litre engine.

The scale is therefore `V = raw / 200` for the pedal, throttle, and MAF
diagnostic words. It is established from ROM constants and factory
specifications, not from firmware arithmetic, and it implies a ten-bit span of
5.12 V referred to the ECM terminal. A pin-referred measurement on the target
ECU remains the open hardware item.

## Thermistor transfer code of the fuel and oil temperatures

Every reviewed temperature channel shifts its ten-bit sample right by two and
passes the byte through implicit-axis primitive `FUN_000263A0`: 32 points, a
step of 8 input counts, an input limit of 248, and a uint8 output. One input
count is four ten-bit counts, or 20 mV under the scale of the previous section.

| Channel | Sample | Input byte | Table | Transfer code | Published byte |
| --- | --- | --- | --- | --- | --- |
| coolant | `0xFFFF1D60`, AN0 mux code 000 | `0xFFFF1186` | `0x12DEA` | `0xFFFF1187` | DID `0x1101` byte `0xFFFF1079`; PID `0x05` as code - 10 |
| intake air | `0xFFFF1D58`, AN1 lane 0 | shifted in place | `0x12DEA` | `0xFFFF2838`, `0xFFFF3F42` | DID `0x1106`; PID `0x0F` as code - 10 |
| fuel | `0xFFFF100A`, AN0 mux code 111 | `0xFFFF1178` | `0x12DEA` | `0xFFFF1F89` | DID `0x1104` byte `0xFFFF1074` |
| engine oil | `0xFFFF1D5C`, AN0 mux code 010 | `0xFFFF117B` | `0x12C6E` | `0xFFFF1F94` | DID `0x111F` byte `0xFFFF2876` |

Curve `0x12C6E` equals table `0x12DEA` byte for byte over all 32 points:

```text
255 241 200 174 160 149 141 134 128 122 118 113 109 105 101  97
 93  90  86  82  78  74  70  66  61  57  51  45  38  27   8   0
```

J1979 Mode 01 PIDs `0x05` and `0x0F` publish the `0x12DEA` output minus 10
under the standard definition `A - 40` degC, so the ECU declares the output
code as `degC + 50`. The fuel byte is an output of that table and the oil byte
an output of an identical table through the same primitive, so
`degC = raw - 50` holds for DIDs `0x1104` and `0x111F` by code. Mode 01 itself
declares no oil-temperature or fuel-temperature PID.

Fuel publisher `FUN_00039788` and oil producer `FUN_0003EB84` filter the
sample through `FUN_0003A5E0` and publish the code through the same limiter: a
higher code is taken at once, the previous byte is held while the code plus two
exceeds it, and a larger drop publishes the code plus two. The previous fuel
byte `0xFFFF107C` is the copy of `0xFFFF1074` that dispatcher `FUN_000209D8`
makes at `0x00020CBA`, after periodic table `0x21834`, through the eight-byte
block `0xFFFF1072..0xFFFF1079 -> 0xFFFF107A..0xFFFF1081`. The fuel publisher
substitutes service-0x30 value byte `0xFFFF992D` while active bit `0xFFFF99C5`
bit 1 is set. The oil producer publishes `0xFF` while the input byte is outside
`3..241` or a P0197, P0198, or P0196 record is stored, and zero while
`ROM8[0x8616]` bit 0 is clear.

Coolant coordinator `FUN_000394B8` publishes DID `0x1101` byte `0xFFFF1079` the
same way. Transfer code `0xFFFF1187` from `FUN_00039550` passes limiter
`FUN_00039588` against previous byte `0xFFFF1081` while the input byte is within
`3..241`, and service-0x30 value byte `0xFFFF9924` replaces it while active bit
`0xFFFF99C4` bit 0 is set. Outside the input range the coordinator sets
`0xFFFF2461` bit 6 and publishes fail-safe ramp `FUN_000395AE`:
`min(90 + n, 130)`. Step counter `n` at `0xFFFF1F8C` is zero while `0xFFFF2451`
bit 5 is clear and otherwise rises by one per six ticks of the 1.024 s
countdown `0xFFFF24F7`, so the ramp covers its 40 counts in 245.8 s. The factory
fail-safe table for P0117 and P0118 gives 40 degC at ignition ON or START,
80 degC after about four minutes, and a time-dependent value between them. The
ramp therefore fixes `degC = raw - 50` at one degC per count without reference
to the thermistor table.

The factory thermistor reference tables agree with the table at 20 mV per
input count:

| Factory reference | Voltage | Factory degC | Code | `code - 50` |
| --- | --- | --- | --- | --- |
| coolant, engine oil | 4.4 V | -10 | 41.5 | -8.5 |
| coolant, fuel tank, engine oil | 3.5 V | 20 | 70.5 | 20.5 |
| intake air | 3.3 V | 25 | 75.5 | 25.5 |
| coolant, fuel tank, engine oil | 2.2 V | 50 | 102 | 52 |
| intake air | 1.2 V | 80 | 131 | 81 |
| coolant, engine oil | 0.9 V | 90 | 144 | 94 |
| engine oil | 0.6 V | 110 | 163.5 | 113.5 |

The factory voltages carry one decimal place, which is 2.5 degC at the 90 degC
point and 4.4 degC at the 110 degC point of the table.

The oil-temperature monitors use the same coding. `FUN_00099E00` reports P0197
while snapshot `0xFFFF10FB` of the input byte is below 3 and P0198 while it is
242 or above, which is an input below 0.06 V or from 4.84 V; `ROM8[0x18701] =
0x03` enables both. It calls rationality monitors `FUN_00099EFE` and
`FUN_0009A0D4`, which report descriptor `0xE4`, P0196, only while
`ROM8[0x18702]` bit 2 is set. The stock byte is `0xF9`, so JK08A skips both,
while their constants remain in the image and follow the factory confirmation
procedure:

| Constant | Value | Compared byte | Under `degC + 50` | Factory procedure |
| --- | --- | --- | --- | --- |
| `ROM8[0x8CDA]` | 130 | coolant latch `0xFFFF5508`, at least | 80 degC | coolant above 80 degC before the soak |
| `ROM8[0x8CDB]` | 90 | start-latched coolant `0xFFFF106E` and second byte `0xFFFF452C`, at most | 40 degC | coolant and intake air below 40 degC |
| `ROM8[0x8CC9]` | 6 | absolute difference of the two, below | 6 degC | difference within 6 degC |
| `ROM8[0x8964]` | 170 | oil snapshot `0xFFFF2772`, above | 120 degC | fault criterion |
| `ROM16[0x9372]` | 300 | ticks of `0xFFFF84C3` bit 6 | | idle for 5 minutes |
| `ROM8[0x8CD9]`, `ROM8[0x8962]`, `ROM8[0x8963]` | 100, 50, 6 | coolant above, oil below, oil span below | 50 degC, 0 degC, 6 degC | stuck-low criterion of `FUN_00099EFE` |

## Battery-voltage scale

`FUN_00039A9E` publishes DID `0x1103` byte `0xFFFF1188`. It copies the phase-2
AN0 mux sample `0xFFFF1D6E`, selector code 001, to `0xFFFF1FC4`, stores the
sample shifted right by two in `0xFFFF1FC6`, passes that byte through guard
`FUN_00067188` and Q1.15 scaler `FUN_000671D8` with coefficient `0xFFFF4970`,
the trim shared with the MAF words, and saturates the result to 255. With the
stock coefficient `0x8000` the byte equals the sample shifted right by two, so
one count is 20 mV at the converter input. Scheduler `FUN_00020DFE` copies the
byte to snapshot `0xFFFF1108`, which the DTC monitors read.

No reviewed instruction converts the byte to volts, and Mode 01 declares no
module-voltage PID. The scale follows from the limits that the monitors apply
to the snapshot. Five constants dominate the comparisons that the reading
functions apply to the two bytes: 100, 125, 131, 137, and 200. They are the
integer parts of 8, 10, 10.5, 11, and 16 times 12.5, and constants 50, 75, 112,
150, 163, and 175 sit on the same 12.5-count lattice at 4, 6, 9, 12, 13, and
14 V.

| Monitor | DTCs | Accepted byte | At 0.08 V per count | Factory test condition |
| --- | --- | --- | --- | --- |
| `FUN_000995C4` | P0011, P0021 | `ROM8[0x8E0A] = 125 <` byte `<= ROM8[0x8E07] = 200` | 10.00 .. 16.00 V | between 10 V and 16 V |
| `FUN_0008F168` | P0014, P0024 | `ROM8[0x8E0B] = 125 <` byte `<= ROM8[0x8E08] = 203`, and `137 <` byte `<= 200` | 10.00 .. 16.24 V | between 10 V and 16 V |
| `FUN_00093C40` | P0031, P0051, P0052 | `ROM8[0x82B4] = 131 <=` byte `< 200` | 10.48 .. 16.00 V | between 10.5 V and 16 V |
| `FUN_0009426E` | P0130, P0150 | `137 <=` byte `< 200` | 10.96 .. 16.00 V | more than 11 V |
| `FUN_0009678C` | P2A00 | `137 <=` byte `< 200` | 10.96 .. 16.00 V | more than 11 V |
| `FUN_000AC0D4` | P0462, P0463 | `137 <=` byte `< 200` | 10.96 .. 16.00 V | more than 11 V |
| `FUN_000A40F4` | P0506, P0507 | byte `>= 100` and byte `>= 137` | from 8.00 V and from 10.96 V | more than 11 V |
| `FUN_00099EFE`, `FUN_0009A0D4` | P0196 | byte `> 137` | above 10.96 V | more than 11 V |

A scale of 20 V over 255 counts puts the same limits at 9.80, 10.27, 10.75, and
15.69 V and meets none of the factory values. The monitors of the accelerator
pedal and throttle position sensors accept the byte from 100, or 8.00 V, where
the factory procedure asks for more than 10 V, and `FUN_0008B93A` accepts
`131 <=` byte `< 200` for P0038 where the factory procedure states between 11 V
and 16 V; the factory condition is the narrower one in both cases.

The scale is therefore `V = raw * 0.08` for DID `0x1103`. It is established
from ROM constants and factory specifications, not from firmware arithmetic.
Against 20 mV per count at the converter input it implies a 4:1 divider between
the battery terminal and the multiplexer input, and a full-scale byte of
20.40 V. Target recordings hold 157 .. 180 counts, or 12.56 .. 14.40 V, around
a diagnostic reading of 13.92 V. Raw 100, the limit of the computed START
SIGNAL gates, is 8.00 V. A pin-referred measurement on the target ECU remains
the open hardware item.

## Intake-air-temperature and P0128 model

The exact DID table points the reviewed intake-air-temperature DID to
`0xFFFF2837`, the `0x12DEA` transfer code of the filtered AN1 lane-0 sample.
J1979 Mode 01 PID `0x0F` returns `0xFFFF3F41`, the same transfer code of the
unfiltered lane-0 sample minus 10, and the standard defines the PID as `A - 40`
degC, so the ECU declares the code as `degC + 50` and the `raw - 50` conversion
of the DID follows from code. Homologous measured Nissan diagnostics agree. The
scheduler copies the DID byte into the previous-cycle snapshot consumed by the
P0128 thermostat model; the firmware trace establishes the byte flow but not
target-ECU terminal continuity.

The P0128 model contains several map-weighted balance terms. Their exact
arithmetic and DTC association are recorded in the map, function, variable, and
diagnostic-binding rows. Several involved maps, axes, and configuration
coefficients are zero in stock JK08A, making their individual contributions
zero while the surrounding scheduler and state machine remain live. A stock
zero term is not equivalent to absent code, and a calibrated change requires a
new behavior and hardware review.

## Rear oxygen sensor and catalyst monitors

The rear oxygen sensor model contains independent paths that must not be merged:

- a bank-indexed dispatcher for slow response and low/high voltage descriptor
  pairs;
- a second high-voltage descriptor path using separate working arrays;
- a rear-heater circuit monitor with independent low and high thresholds;
- a command/status observation DID whose bit names come from a homologous
  profile;
- an independent catalyst-efficiency result dispatcher;
- a calibrated catalyst-limit branch using a bank metric and limit array.

Duplicate DTC codes can therefore represent distinct descriptor records and
firmware paths. `JK08A.dtc.csv` and the diagnostic corpus preserve them rather
than collapsing by public code.

The calibrated catalyst-limit branch is stock-unreachable because its unsigned
limit table is zero. The independent result dispatcher remains present, so the
stock-zero branch does not disable the entire P0420/P0430 subsystem. Internal
rear-O2 and catalyst metric units remain unresolved.

## EVAP monitors

The exact firmware contains a shared EVAP diagnostic coordinator plus separate
pressure and leak-monitor paths. Several coordinator branches are skipped by
stock configuration even though their producer and descriptor code exists.
Other leak and range paths remain outside those gates.

The fuel-level-derived EVAP coordinate uses a meter CAN payload field, a slow
filter, and a table whose stock cells are all the same sentinel. Downstream code
uses the resulting high byte in signed and unsigned forms. The exact path proves
fuel-level monitor context and sentinel behavior, not voltage, percentage, or
tank-volume conversion.

The canonical binding rows distinguish:

- exact descriptor and dispatcher identity;
- stock reachability of a specific branch;
- producer and consumer relationships;
- homologous factory terminology;
- unresolved physical metric and unit.

Changing a configuration-disabled or sentinel calibration requires review of
the re-enabled control path and cannot inherit the stock liveness conclusion.

## Static binding review

Candidate extraction starts from a semantic-free Ghidra reference inventory.
A DID literal and same-function RAM reference remain a worklist item until a
trace closes request dispatch, returned storage, conversion, and source scope.
The candidate output is deliberately incompatible with the binding loader.

Accepted rows require machine-address evidence and one exact source claim.
Firmware confidence, source applicability, inheritance scope, and priority are
independent. Static rows cannot use `silicon` confidence.

The tooling and query interface are documented in
`../tools/diagnostics/README.md`. The graph projection and provenance audit are
documented in `../tools/memgraph/README.md`.

## Hardware boundary

Static analysis does not establish physical sensor conversion, terminal
assignment, full monitor enable conditions, peripheral side effects, or target
vehicle behavior. Hardware promotion requires the exact ROM, a controlled input
or operating condition, the expected diagnostic response, and an independent
electrical or vehicle observation. A homologous manual or community logger can
define a test hypothesis but cannot close this boundary.
