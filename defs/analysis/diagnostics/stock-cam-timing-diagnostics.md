# Stock cam timing readouts and monitors

## Service 0x22 cam timing records

The family `0x11` response handler uses the low request byte to select a
four-byte pointer. For each identifier below it reads the single byte at
that pointer. The intake pair and the intake target use the existing
centered byte representation, `(raw - 128) * 0.5` crank degrees. The
1EK7A target byte is the high byte of the word rooted at the same address.
Its diagnostic copy remains one byte wide.

| ROM | Family 0x11 pointer table | Intake B1 `0x1135` | Intake B2 `0x1163` | Common intake target `0x113a` |
| --- | --- | --- | --- | --- |
| JK00A, JK03A, JK03B, JK08A | `000226ac` | `ffff2442` | `ffff2443` | `ffff2326` |
| JK00C | `00022738` | `ffff24c6` | `ffff24c7` | `ffff239a` |
| JK00D | `00022738` | `ffff24ce` | `ffff24cf` | `ffff23a2` |
| JK78C | `00022718` | `ffff239c` | `ffff239d` | `ffff227a` |
| 1ND0A and 1ND3B | `00022a70` | `fffe945d` | `fffe945e` | `fffe9326` |
| 1ME3B | `00022ae4` | `fffe942d` | `fffe942e` | `fffe92f4` |
| 1EK7A | `00022b78` | `fffe9439` | `fffe943a` | `fffe92f0` |

Each table record is at `table + 4 * low_byte`. The analogous fields for
actual exhaust timing and common target retain the same identifiers across
the stock images. Their source meanings depend on the layout.

| ROM | `0x1164` source | `0x1165` source | `0x1166` source | Applicable source role |
| --- | --- | --- | --- | --- |
| JK00A, JK03A, JK03B, JK08A | `ffff2324` | `ffff2325` | `ffff2327` | Actual exhaust phase pair and common target |
| JK00C | `ffff2398` | `ffff2399` | `ffff239b` | Actual exhaust phase pair and common target |
| JK00D | `ffff23a0` | `ffff23a1` | `ffff23a3` | Actual exhaust phase pair and common target |
| JK78C | `ffff239e` | `ffff239f` | `ffff23a4` | Legacy diagnostic byte slots |
| 1ND0A and 1ND3B | `fffe945f` | `fffe9460` | `fffe9466` | Legacy diagnostic byte slots |
| 1ME3B | `fffe942f` | `fffe9430` | `fffe9436` | Legacy diagnostic byte slots |
| 1EK7A | `fffe943b` | `fffe943c` | `fffe9442` | Legacy diagnostic byte slots, with an internal arithmetic consumer for `0x1166` |

VQ37 exports leave the actual exhaust phase and target meanings absent. The
pointer entries establish what RAM the service reads. Their sampled runtime
values and any indirect producers for the legacy phase bytes remain open.
On 1EK7A, `00138240` loads `r12 = -128` at `00138260` and writes its low
byte `0x80` to `fffe9442` at `00138366` and `001383e8`. The calculation
at `0013e010` reads that byte at `0013e070` and `0013e1d2` and uses its
unsigned value multiplied by `0.5`. The byte retains its generic diagnostic
slot identity on that layout.

## Intake cam capture endpoints

Vector 100 at `00020194` dispatches IMI1E and captures GR1E at `fffff44c`.
Vector 101 at `00020198` dispatches IMI1F and captures GR1F at `fffff44e`.
The instructions below bind the newly attributed endpoints to both the
interrupt and its register. The SH7059 pair has its capture path in the
[hardware acquisition specification](../airflow/SH7059.sensor-acquisition.md).

| ROM | IMI1E entry and GR1E read | IMI1F entry and GR1F read |
| --- | --- | --- |
| JK00C and JK00D | `0002af46 / 0002afbe` | `0002b254 / 0002b2ce` |
| JK78C | `0002cef4 / 0002cf8c` | `0002d2ee / 0002d388` |
| 1ND0A and 1ND3B | `0002dd58 / 0002dec6` | `0002e0e0 / 0002e286` |

The 1ND IMI1F handler initializes `r7` to `fffff440` at
`0002e11a..0002e120`. `MOV.W @(0x0e,r7),r0` at `0002e286` and
`0002e2de` reads the GR1F capture with that fixed base. The boundary here
is the MCU capture register. Connector pins and mechanical reference zero
remain hardware questions.

## JK00C and JK00D CVTC

### Descriptor and attribute inventory

All 12 records are present in both images at the same indices. Each
descriptor occupies 12 bytes and encodes the DTC at offset 6. The tables
begin at `0001c4e0`/`0001c500`. The parallel 4-byte pointers begin at
`0001d2b4`/`0001d2d4`. The descriptor, attribute pointer slot, and pointed
attribute each move by `0x20` from JK00C to JK00D for these records.

| DTC and path | Index | JK00C record / pointer / attribute | JK00D record / pointer / attribute | Attribute |
| --- | ---: | --- | --- | --- |
| P0075 intake solenoid 1 | 50 | `0001c738 / 0001d37c / 00018764` | `0001c758 / 0001d39c / 00018784` | `00a0` |
| P0081 intake solenoid 2 | 51 | `0001c744 / 0001d380 / 00018766` | `0001c764 / 0001d3a0 / 00018786` | `00a0` |
| P0078 exhaust magnet 1 | 64 | `0001c7e0 / 0001d3b4 / 0001877c` | `0001c800 / 0001d3d4 / 0001879c` | `00a0` |
| P0084 exhaust magnet 2 | 65 | `0001c7ec / 0001d3b8 / 0001877e` | `0001c80c / 0001d3d8 / 0001879e` | `00a0` |
| P1078 exhaust sensor 1, A | 129 | `0001caec / 0001d4b8 / 00018774` | `0001cb0c / 0001d4d8 / 00018794` | `02a0` |
| P1084 exhaust sensor 2, A | 130 | `0001caf8 / 0001d4bc / 00018776` | `0001cb18 / 0001d4dc / 00018796` | `02a0` |
| P1078 exhaust sensor 1, B | 131 | `0001cb04 / 0001d4c0 / 00018778` | `0001cb24 / 0001d4e0 / 00018798` | `02a0` |
| P1084 exhaust sensor 2, B | 132 | `0001cb10 / 0001d4c4 / 0001877a` | `0001cb30 / 0001d4e4 / 0001879a` | `02a0` |
| P0011 intake timing 1 | 205 | `0001ce7c / 0001d5e8 / 0001875c` | `0001ce9c / 0001d608 / 0001877c` | `0020` |
| P0021 intake timing 2 | 206 | `0001ce88 / 0001d5ec / 0001875e` | `0001cea8 / 0001d60c / 0001877e` | `0020` |
| P0014 exhaust timing 1 | 207 | `0001ce94 / 0001d5f0 / 00018758` | `0001ceb4 / 0001d610 / 00018778` | `0020` |
| P0024 exhaust timing 2 | 208 | `0001cea0 / 0001d5f4 / 0001875a` | `0001cec0 / 0001d614 / 0001877a` | `0020` |

### Scheduling and record calls

Both images have dispatch slot `00021b8c` pointing at periodic diagnostic
task `0007ee9c`. The task invokes the independent intake path at `0007eee6`
through `0009ef7c`/`0009ef68`, the main intake coordinator at `0007f044`
through `00092b14`, and the exhaust coordinator `00093e1c` at `0007f04a`.
The calls have no local enable branch. Admission and per-bank decisions
belong to the called routines. `00090f98` and `000808e0` are the local
intermediate and full record paths, respectively.

| Record | Intermediate JK00C / JK00D | Full JK00C / JK00D |
| --- | --- | --- |
| P0011 main intake | `00093d20 / 00093d20` | `00093d42 / 00093d42` |
| P0021 main intake | `00093d66 / 00093d66` | `00093d8a / 00093d8a` |
| P0011 independent intake | `0009eaf6 / 0009eae2` | `0009eb16 / 0009eb02` |
| P0021 independent intake | `0009eb5e / 0009eb4a` | `0009eb80 / 0009eb6c` |
| P0075 intake | `00093dac / 00093dac` | `00093dba / 00093dba` |
| P0081 intake | `00093dc8 / 00093dc8` | `00093dd6 / 00093dd6` |
| P1078 exhaust A | `00094622 / 00094622` | `00094648 / 00094646` |
| P1084 exhaust A | `00094660 / 0009465e` | `0009467e / 0009467c` |
| P1078 exhaust B | `00094694 / 00094690` | `000946b4 / 000946ae` |
| P1084 exhaust B | `000946c8 / 000946c4` | `000946e8 / 000946e2` |
| P0014 exhaust rest | `000946fc / 000946f6` | `0009476a / 00094766` |
| P0024 exhaust rest | `0009479a / 00094794` | `000947d4 / 000947cc` |
| P0014 exhaust tracking | `00094800 / 000947f8` | `00094836 / 0009482c` |
| P0024 exhaust tracking | `00094860 / 00094856` | `000948a8 / 0009489e` |
| P0078 exhaust | `000948d2 / 000948c8` | `000948e4 / 000948da` |
| P0084 exhaust | `000948f6 / 000948ea` | `00094908 / 000948fa` |

The calls use unsigned descriptor indices. Negative
8-bit immediates in the timing and sensor paths are zero-extended before
entering the reporter, and the exhaust performance paths retain the
positive index in a register through the call delay slot. The neighboring
`000bfccc`/`000bfcac` call at `000c0662`/`000c0642` uses `0x41 << 2`
in its delay slot, selecting index `0x104`.

### Intake timing and solenoid checks

The main intake coordinator `00092b14` calls qualifier `00092e08` at
`00092bfa` and record routing `00093d08` at `00092c00`. The qualifier
has a reset path selected by mask `0x04` at state-base offset `0xdb`.
For routine timing evaluation it requires the common running bit `0x80`
set and starter bit `0x40` clear, the battery window `125 < B <= 200`,
an elapsed startup countdown at zero, and local qualification bits for
the operating state and bank. `B` is the unsigned byte at `ffff1113`.
The ROM lower/upper bytes are `00008e48/00008e45` on JK00C and
`00008e4b/00008e48` on JK00D. The 60-count startup-window reload is
`ROM8[00008e36/00008e39]`. The qualifier calls all three bank workers
for each bank with their respective admit arguments.

| Worker | Entry on both images | Main admission or decision |
| --- | --- | --- |
| Intake timing | `000937c8` | Uses the biased target-actual byte and an operating-window table. With active state and the input window qualified, counts samples and writes the result bits when the count exceeds the selected window. Loss of qualification clears or reloads the corresponding state. |
| Solenoid with running qualification | `00093a7c` | With battery, running/starter and bank admission qualified, accepts command byte zero or `0xff`. For zero command either of the two bank driver-status bytes must equal 1. For `0xff` it uses the bank bit of the periodic status snapshot. |
| Solenoid without running qualification | `00093c28` | The caller requires the running bit clear, an additional local inhibit bit clear, and the same battery window. The worker requires the periodic bank run-request copy and command byte `0xff`, then counts the qualifying status bit. |

The running solenoid worker sets the intermediate bit at a count of 10
and the full report bit at 100. JK00C reads `00008b32` and `00008b34`.
JK00D reads `00008b33` and `00008b35`. The second worker uses the same
100-count full threshold and can set both bits on the same pass. These
are qualifying monitor counts. Reset branches clear the bank counter.
Every cell of the 8-by-8 intake operating-window table is 60 in these
stock images. The bases are `0000990e` and `0000991e`. The main timing
worker checks whether the count exceeds its selected window.

| Eight-bit field | JK00C | JK00D | Bank selection |
| --- | --- | --- | --- |
| Main timing intermediate result | `ffff3718` | `ffff372c` | bits 0/1 |
| Main timing full report result | `ffff3715` | `ffff3729` | bits 0/1 |
| Intake solenoid intermediate result | `ffff3719` | `ffff372d` | bits 0/1 |
| Intake solenoid full report result | `ffff3716` | `ffff372a` | bits 0/1 |

The separate intake path reaches `0009e874`/`0009e860` from the periodic
wrapper only with ROM bits `0x08` or `0x04` enabled, reset bit clear and
runtime admission `0x40` set. The per-bank enables are bits `0x08/0x04`
of `ROM8[0001b66f/0001b68f] = 0xff`. The worker requires the same battery
window, local readiness masks, the clear related-record predicates, target
`0x80`, and an expired holdoff for at least one admitted bank. Helper
`0009ebe8`/`0009ebd4` clamps and biases the actual-position error and tests
the two error windows selected by the admission bits. A still-qualified
out-of-window error can call the intermediate and full paths independently
when their countdowns reach zero. The default reloads in both images are
90 each. In JK00C, the intermediate countdowns are `ffff4557/ffff4556`
and the full countdowns are `ffff4553/ffff4550`. In JK00D they are
`ffff456b/ffff456a` and `ffff4567/ffff4564`. Each reported path also
copies its three-byte runtime record to its snapshot.

### Exhaust CVTC checks

The coordinator `00093e1c` builds bank-specific admits and calls the five
workers below, with bank index 0/1 in R4 and the enable in R5. It uses
the routine front gate `0x80` set and `0x40` clear in the running/starter
byte, predicate `00026966` zero and halfword `ffff2c42/ffff2c56` zero. The position
sensor branch additionally requires a separate readiness bit and uses
ROM masks `0x80/0x40` for path A and `0x20/0x10` for path B. Exhaust
performance uses the battery byte window `125 < B <= 203`, related-record
and state gates, and masks `0x02/0x01`. The battery limits are at
`00008e49/00008e46` on JK00C and `00008e4c/00008e49` on JK00D. The
magnet arm has its own running/starter and periodic-admission tests,
`137 < B <= 200`, and ROM masks `0x02/0x01`.

| Stock enable byte | JK00C | JK00D | Value |
| --- | --- | --- | --- |
| Exhaust position sensor A/B | `0001b661` | `0001b681` | `f0` |
| Exhaust rest and tracking performance, independent intake performance | `0001b66f` | `0001b68f` | `ff` |
| Exhaust magnet circuit | `0001b64e` | `0001b66e` | `03` |

| Exhaust worker | JK00C | JK00D | Full-result byte JK00C / JK00D |
| --- | --- | --- | --- |
| Sensor path A | `00094d3e` | `00094d2c` | `ffff3688 / ffff369c` |
| Sensor path B | `00094e44` | `00094e30` | `ffff3689 / ffff369d` |
| Rest performance | `00094f0e` | `00094efa` | `ffff368a / ffff369e` |
| Target-tracking performance | `0009517a` | `00095166` | `ffff368b / ffff369f` |
| Magnet circuit | `000952fa` | `000952e6` | `ffff368c / ffff36a0` |

All five result bytes use bits 0/1 for the two banks. The position workers
set a bank arm bit and request a reset of the capture path on first arm.
Their adjacent capture-status byte uses bits `6+b` for A and `4+b` for B.
The two paths use separate bank countdowns. A uses `ffff456c/456d` and B uses `ffff4566/4567`
in JK00C, A `ffff4580/4581` and B `ffff457a/457b` in JK00D. A clear
indicator or missing admit reloads the corresponding countdown to 100.
The reload bytes are `00008e61` and `00008e70`. With the indicator set
and countdown zero the worker sets its result bit.
The full reporter keeps both descriptor indices for each bank distinct.

Rest performance requires target byte `0x80` and tests two biased
position-error windows with distinct conditions and paired countdowns.
It reloads a pair when the error is in range or admission drops. An
out-of-window error sets the intermediate and full bits when their
countdowns reach zero. The shared stock reload pair is 90/90 at
`00008e5a` and `00008e63` in JK00C and `00008e69` and `00008e72`
in JK00D. Target tracking admits only with
the tracking delay expired, the current target nonneutral, related-record
and operating-window predicates clear, and an unjudged bank. It counts
qualifying sample passes against the selected operating window and also
tests the bank's biased target-actual error. The rest and tracking branches
share indices 207/208 while keeping their result bytes and report sites
separate.
The exhaust operating-window table at `0000994e`/`0000995e` also contains
60 in all 64 cells. The target-tracking error bounds are `0x80 +/- 34`
in both images, from the two ROM bytes at offsets 0 and 2 of
`0000896e`/`0000896f`.

The exhaust magnet worker requests the bank with duty word zero and
requires the request bit to return through its periodic copy. For JK00C
the duty words are `ffff1b04/ffff1b06`. JK00D uses `ffff1b0c/ffff1b0e`.
The two driver-status bytes are `ffff10aa/ffff10ab` for bank 1 and
`ffff10ac/ffff10ad` for bank 2. It increments the bank byte counter with
saturation while either status equals 1. The intermediate threshold is
10 and the full threshold is 100, at `00008b31/00008b33` in JK00C and
`00008b32/00008b34` in JK00D. The intermediate result is `ffff3695` or
`ffff36a9`, and the count starts at `ffff369e` or `ffff36b2`. Loss of
enable, zero-duty eligibility, or qualifying driver state can clear the
count. The full-result latch prevents new counting for that bank.

### Countdown service and scope

The local `0002040c` ISR advances the compare register by `0x140` at
`00020440` and services nested divide-by-ten nonzero countdown groups.
The CVTC byte countdowns lie in the second nested byte group, spanning
246 bytes from `ffff447f`/`ffff4493`, with the load/decrement/store loop
at `000206d6..000206e2`. Each nonzero countdown in that group decrements
once per 100 base ISR invocations. The bank increment counters are local
worker state. The tick ratio alone supplies no bench timing or fault
confirmation. Exact capture pulse polarity, physical voltage/angle scale,
and a full upstream interpretation of every operating-window bit are
outside this binding.

## JK78C intake CVTC and cam position diagnostics

### Exact diagnostic record identities

The stock table contains 304 12-byte descriptors from `0001b7ac` up to
`0001c5ec`. The SAE code is the big-endian halfword at descriptor offset 6.
The attribute pointer slot is `0001c5ec + 4 * index`. The four
intake CVTC decisions and six distinct cam-position records use the indices below.

| Code | Decimal index | Descriptor address / exact bytes | Attribute pointer slot / target |
| --- | ---: | --- | --- |
| P0011 | 194 | `0001c0c4 / 370300000000001100000000` | `0001c8f4 / 000175b2` |
| P0021 | 195 | `0001c0d0 / 370200000000002100000000` | `0001c8f8 / 000175b4` |
| P0075 | 49 | `0001b9f8 / 130400000000007500000000` | `0001c6b0 / 000175be` |
| P0081 | 50 | `0001ba04 / 130300000000008100000000` | `0001c6b4 / 000175c0` |
| P0340 | 64 | `0001baac / 180500000000034000000000` | `0001c6ec / 00017386` |
| P0340 | 65 | `0001bab8 / 180400000000034000000000` | `0001c6f0 / 00017388` |
| P0340 | 66 | `0001bac4 / 180300000000034000000000` | `0001c6f4 / 0001738a` |
| P0345 | 127 | `0001bda0 / 2a0200000000034500000000` | `0001c7e8 / 0001737e` |
| P0345 | 128 | `0001bdac / 2a0100000000034500000000` | `0001c7ec / 00017380` |
| P0345 | 129 | `0001bdb8 / 2a0000000000034500000000` | `0001c7f0 / 00017382` |

All ten attribute targets hold `00a0`. The distinct P0340 and P0345
records carry different selectors and have different runtime state
despite the repeated SAE code. The table contains no P0010, P0012,
P0013, P0014, P0020, P0022, P0023, P0024, P0076, P0077, P0082,
P0083, P0365, P0390, P1140 or P1145 descriptor.

### Scheduling and report transfers

Periodic diagnostic dispatcher `0009c284` calls the primary intake
coordinator wrapper `000afef8` at `0009c41a` via
`ROM32[0009c5d4]`. The wrapper calls coordinator `000b028c`
and report multiplexer `000b15ec`. It also services an
initialization branch through `000b0078` under `ffff45c6 & 8`.
The separate call at `0009c2c8` via `ROM32[0009c4fc]` runs
`000bac06`, which owns the independent intake timing monitor and
the three cam/crank phase checks below.

| Decision | Primary direct marker | Primary full report | Independent marker / full report |
| --- | --- | --- | --- |
| P0011 index 194 | `000b15fe` | `000b1620` | `000ba6f8 / 000ba71c` |
| P0021 index 195 | `000b1644` | `000b1668` | `000ba774 / 000ba79a` |
| P0075 index 49 | `000b168a` | `000b1698` |  |
| P0081 index 50 | `000b16a6` | `000b16b4` |  |

Direct marker calls pass the local index to `000ae480`. The full
report dispatcher `0009dfa8` also calls that marker. The marker sets
bit 7 of byte 1 at `ffff5e94 + 3 * index` and sets
`ffff4ba0` to one. It stores the activity byte at `000ae4e0`.
The timing paths copy the selected three-byte code state after
either transfer. The primary snapshots are `ffff628d` and
`ffff6290`. The independent snapshots are `ffff6287` and
`ffff628a`. The four solenoid transfers have no such copy.
The primary dispatch reads distinct bank bits 0 and 1 in each
gate byte shown in the table.

| Flags | Marker byte | Full-report byte |
| --- | --- | --- |
| Timing | `ffff3841` | `ffff383d` |
| Circuit | `ffff3842` | `ffff383e` |

### Primary position and solenoid qualification

`000b028c` compares the limited selected target word
`ffff227c`, read at `000b06ee`, with the bank event-offset words
`ffff23a0/ffff23a2`, read at `000b06fc` and `000b072c`.
The selected-target limiter `000e6492` writes `ffff227c` at
`000e651c` or `000e662c`. The exported target byte at
`ffff227a` is a separate cell. Both event-offset words already
belong to `intake_event_offset_b1/ram` and
`intake_event_offset_b2/ram`. Their normal producer `000e6226`
is separate from the startup initializer `000e56d4`, which
stores the `0x8000` sentinel at `000e56fc` and `000e57e8`.

For each bank the coordinator stores
`clamp(u16(target) - u16(measured) + 128, 0, 255)` at
`ffff1466/ffff1467` via `000b0726` and `000b0758`.
It also selects a provisional pass-count limit from the
`0000953a` byte surface indexed by eight-bucket raw axes
`000131e8/000131f0`. Every stock cell is `0x3c`.
The retained count limit at `ffff13a1` is updated if the
absolute selected-versus-reference word difference fits
`ROM8[00008b74] = 2` or the provisional limit increases.
The reference word here is `ffff2280`.

The coordinator derives per-bank readiness from operating-state
hysteresis, prior diagnostic and settle flags, and an unsigned
battery window `0x7d < ffff10f4 <= 0xc8`. The wrapper admits the
primary timing lanes through `ROM8[0001a8c3] = 0xfc` masks
`0x08/0x04`, the companion timing lanes through
`ROM8[0001a8e1] = 0xcf` masks `0x80/0x40`, and the solenoid
lanes through `ROM8[0001a89f] = 0x18` masks `0x10/0x08`.
These six stock masks are set. The primary timing permissions
also require the common runtime permit and clear prerequisite
phase records. Each stage receives bank 0 and bank 1 separately.

| Stage | Function | Stock checks and result |
| --- | --- | --- |
| Primary performance | `000b0e08` | Rejects the target sentinel `0x8000`, pending circuit state, local inhibits and a target-delta byte above 2. Checks the centered error strictly outside `[102,154]` from the two `0x1a` bytes at `000087df..000087e0`. A qualified count in `ffff1985/ffff1986` greater than `ffff13a1` evaluates the retained case and publishes the bank timing marker and full-report bits. |
| Primary solenoid circuit | `000b10ee` | Uses endpoint duty bytes `ffff239a/ffff239b` only at values 0 or 255. Compares the endpoint to the bank bit in feedback status byte `ffff2632`, counts the mismatch in `ffff37c2/ffff37c3` and sets marker at count 10 or full-report at count 100. Limits are `ROM8[00008933..00008934]`. |
| Complementary solenoid circuit | `000b1238` | Requires endpoint duty 255 and the selected feedback bit after the separate readiness gate. At count 100 it sets both report bits using the bound at `00008934`. |
| Companion timing qualification | `000b132a` | Uses its own readiness and elapsed-byte pair `ffff1987/ffff1988`, checks the same selected target and target delta, and compares the count with `ROM8[00008378] = 59`. The extra path transfers indices 298/299, which encode P0524. |

The separate P0524 transfers use marker calls
`000b1502/000b1510` and common dispatch `000b1518`. The
descriptors at `0001c5a4/0001c5b0` have attribute pointer slots
`0001ca94/0001ca98`, target `000175ba/000175bc`, value `00a0`.
This establishes the companion report dependency of the timing
qualifier. The physical input behind the recorded code remains open.

### Independent timing decision

The independent scenario qualifier `000ba186` runs if either
bit `0x08` or `0x04` of `ROM8[0001a8c3]` is set.
`000bac06` then calls the independent timing decision `000ba350`
at `000bace2` when `ffff45c6 & 8` is clear and
`ffff4528 & 0x10` is set. On the alternate edge it calls
`000ba8d2`. The bank-specific code-path enables in `000ba350`
are those same masks in `0001a8c3`, whose stock value is `0xfc`.

Both banks use reference byte `0xb4` from `00008302` (bank 1)
and `00008305` (bank 2). The decision requires the unsigned
battery snapshot at `ffff10f4` to be above `0x7d` and at most
`0xc8`, from `00008b65` and `00008b64`.
Bank 1 marker/full-report byte countdowns are `ffff471c` and
`ffff4718`, respectively. Bank 2 uses `ffff471b` and
`ffff4715`. With the bank enabled and compare helper `000ba848`
returning one, each zero countdown allows its own transfer. The
rejection paths load marker value 90 from `00008b54` and
full-report value 90 from `00008b50` in both banks.

The interpreter reads capture bytes `ffff221a/ffff221b`
in `000ba848`. Each result is
`clamp(u8(capture) - u8(reference), -128, 127) + 128`, stored
at `ffff16d2/ffff16d3`. Either enabled scenario can qualify the
retained error when it lies strictly outside `[102,154]`.
Their two stock tolerance pairs at `000087e1..000087e2` and
`00008636..00008637` both read `0x1a,0x1a`.
The associated scenario logic also requires the selected target
to equal `0x8000`, the corresponding scenario bit, and a zero
admission countdown. This sentinel check at `000ba636` precedes
the independent error comparison. The comparator reads its reference from a separate operand.

### Cam capture inputs

| Bank | Vector slot / handler | ATU-II capture register | Exact halfword reads | Capture word / derived byte |
| --- | --- | --- | --- | --- |
| 1 | `00020198 / 0002d2ee` | GR1F `fffff44e` | `0002d388`, `0002d434` | `ffff2216` at `0002d448`, `ffff221a` at `0002d5a0/0002d5aa` |
| 2 | `00020194 / 0002cef4` | GR1E `fffff44c` | `0002cf8c`, `0002d012` | `ffff2218` at `0002d026`, `ffff221b` at `0002d17a/0002d1bc` |

The two handlers load `fffff440` into R14 at `0002d328` and
`0002cf2e`. Displacements `0x0e` and `0x0c` reach GR1F and
GR1E. The later reads feed the corresponding RAM capture stores.
The independent comparator uses the separate derived byte lanes.

### Cam/crank phase monitor branches

The three cam/crank checks called by `000bac06` join the same
report dispatcher `0009dfa8` with the local indices below.

| Check | Calls from coordinator | P0340 transfer | P0345 transfer | Companion P0335 transfer |
| --- | --- | --- | --- | --- |
| `000b987c` | `000bac3e` | `000b9924`, index 64 | `000b996c`, index 127 | `000b99b6`, index 67 |
| `000b9a94` | `000bac8a` | `000b9b74`, index 65 | `000b9bcc`, index 128 | `000b9d6a`, index 68 |
| `000b9e1c` | `000bacba` | `000b9f28`, index 66 | `000b9f84`, index 129 | `000ba056`, index 69 |

For each check `000bac06` pairs two dedicated stock selector
bits with the corresponding bit at `ROM8[0001a8b6]`.
The two mode bytes `ROM8[0001a8a4] = 0x3f` and
`ROM8[0001a8b6] = 0x07` admit all three checks.
Their shared runtime conditions are `ffff45c6 & 8` clear and
`ffff4528 & 0x10` set. When the entry gate fails, the
coordinator takes the corresponding initialization path at
`000b9a2a`, `000b9dd0`, or `000ba124`.

The first check tests bank activity bytes `ffff4331/ffff4330`
equal to zero after its common admission. The stock battery clauses
include the floor `0x4b` and the live computed bound
`max(u8(ffff3745) - 12, 0)`. The bank countdowns at
`ffff4747/ffff4748` reload to 100 from `0000839b` and
each reports at zero. The companion crank countdown is
`ffff4749`, stock reload 100 from `0000839c`.

The second check uses the battery floor `0x4c`, prerequisite
record status and cam-state gates. Its bank conditions test
`ffff4331/ffff4330 == 1` together with their respective
`ffff24f8/ffff24fb` gates. Bank countdowns
`ffff4744/ffff4745` reload to 150 from `00008397`. The
companion crank countdown at `ffff4746` reloads to 60 from
`00008398`.

The third check qualifies the operating state and requires a
separate sample count of at least five. The two bank event
counters at `ffff2ab1/ffff2ab2` report at or above four,
from `00008399`. The companion counter at `ffff2ab3`
uses four from `0000839a`. All three families retain their
separate record selectors.

Physical interpretation of some prerequisite state bytes,
countdown tick duration, and the measured engine behavior remain
outside the static review.

## 1ND0A and 1ND3B intake CVTC

### Scheduled primary and independent timing decisions

| Route | Exact stock path |
| --- | --- |
| Schedule entry | `ROM32[00022250] = 000b6384` |
| Primary | `000b6512` calls `000cff10` through `ROM32[000b66ec]`. The wrapper calls `000d0308` at `000d0102` and tail-jumps to `000d1518` at `000d010e`. |
| Independent timing | `000b63ca` calls `000dbcc8` through `ROM32[000b6618]`. Its qualifying branch calls `000db484` at `000dc10e`. |

Both routes can select the same P0011 or P0021 record. The primary
coordinator also qualifies the two solenoid circuit records and two bank
records encoded as P0524.

#### Primary wrapper and input state

The wrapper forms eligibility masks for bank 1 and bank 2. It tests
bit 7 of runtime record byte 1 for indices 67 through 72 at
`000cff46..000cffa8`, the common readiness bit `fffeb842 & 0x20`
at `000cffae`, and bit 7 at `fffed67d` at `000cffbe`.
The group bytes supply the bank masks.

| ROM byte | Stock on both images | Routed bank selections |
| --- | --- | --- |
| `0001af13` | `fc` | `0x08` bank 1 and `0x04` bank 2 for the P0011/P0021 path. The wrapper writes its bank permits to `fffea9e6`. |
| `0001aeef` | `18` | `0x10` bank 1 and `0x08` bank 2 for the circuit path. The wrapper writes the bank permits to `fffea67c`. |
| `0001af31` | `cf` | `0x80` bank 1 and `0x40` bank 2 of the alternate timing path. The wrapper writes its bank permits to `fffea9eb`. |

The coordinator reads the selected common target word `fffe9328`
at `000d05b2`. The target limiter `0010ecf8` writes this word at
`0010ed96`, `0010edbc`, `0010eddc`, and `0010edee`.
This is the selected word adjacent to the public target byte. The
coordinator subtracts each measured unsigned word and stores
`clamp(target - measurement + 128, 0, 255)`.

| Bank | Measured 16-bit word and load | Centered error byte and store |
| --- | --- | --- |
| 1 | `fffe9462`, `000d06e8` | `fffe849e`, `000d0714` |
| 2 | `fffe9464`, `000d0706` | `fffe849f`, `000d0728` |

The arguments to the timing and circuit qualifiers also depend on the
coordinator's operating bits and on
`125 < uint8(RAM8[fffe80fc]) <= 200`, tested through
`ROM8[00008c52] = 0x7d` and `ROM8[00008c51] = 0xc8`.
The battery snapshot is the existing `wild-markhor/ram`. An asserted
reset bit `fffeb8f7 & 0x02` takes the return at `000d0556` before
the primary qualifiers.

| Argument production | Additional conditions in the coordinator |
| --- | --- |
| Primary timing at `000d05ac..000d063c` | `fffeb7f3 & 0x40` set and `& 0x10` clear, `fffeba76` zero, `fffeb8a3 & 0x1c == 0x1c`, `fffe94ca & 0x80` set, and the bank permit in `fffea9e6`. |
| Alternate timing at `000d063e..000d0668` | Same outer mode, battery and delay tests, `fffe94cb & 0x18 == 0x18`, `fffeb8a3 & 0x0c == 0x0c`, and the bank permit in `fffea9eb`. |
| Staged circuit at `000d0686..000d06aa` | `fffeb7f3 & 0x50 == 0x50`, `fffeb842 & 0x20` set and the bank permit in `fffea67c`. |
| Alternate circuit at `000d06ac..000d06e2` | `fffeb7f3 & 0x40`, `fffe9471 & 0x10` and `fffeb7ff & 0x20` all clear, at least one of the bytes at `fffeb9f3` and `fffeb9f0` is at least 2, and the bank permit in `fffea67c`. |

#### Primary P0011 and P0021 timing qualification

The coordinator calls `000d0d70` at `000d08c2` and `000d0948`,
respectively with bank 0 and bank 1. Each bank requires its admission
argument, a clear bank report flag, clear bit 7 at `fffed335`,
`fffed338`, `fffed6dd`, and `fffed6e0`, zero circuit counters
`fffeaa00/fffeaa01`, a zero word at `fffe9bea`, and selected target other than
`0x8000`. The helper also requires the absolute selected-target step
at `fffe89fc` to be at most `ROM8[00008c66] = 2`. It checks the
previous selected target at `fffe932e` through the coordinator's
absolute-difference computation at `000d0778..000d079a`.

The coordinator indexes the stock 8-by-8 byte count table at `000097f0`
using the speed and coolant breakpoints starting at `0001356a` and
`00013572`. Every table cell is `0x3c` in both images. The chosen
cell is published at `fffe843e` and supplies the runtime threshold
byte `fffe83d4`. On a target step above 2, the update retains the
larger of the previous threshold and selected cell. Otherwise it stores
the selected cell.

| Quantity | Bank 1 | Bank 2 |
| --- | --- | --- |
| Start delay | `fffe9521` | `fffe9522` |
| Saturating qualifying-pass count | `fffe89fd` | `fffe89fe` |
| Window excursion bit at `fffe84a0` | `0x01` | `0x02` |
| Marker and full report masks | `0x01` | `0x02` |

The delay reload is `ROM8[0000837a] = 10` when its gate fails.
When admitted and the delay is zero, ROM bit `00008023:0x80` enables
the saturating pass count at `000d0eec`. Stock `0xff` enables the
increment. At `000d0f62/000d0f6e`, a centered error above 154 or below
102 qualifies the excursion. The upper and lower deviations come from
`00008870/00008871`, both `0x1a`. A count strictly above the runtime
threshold advances the stored excursion into the marker and full-report
flags when their state conditions hold. A separate state branch passes
the original P0011 or P0021 index to `000ce100` at `000d0f2a`.

#### Primary P0075 and P0081 solenoid circuit qualification

The coordinator calls staged qualifier `000d0fb0` at
`000d08c8/000d094e`. It calls the alternate bank-1 qualifier
`000d1132` at `000d08ce` and evaluates the corresponding bank-2
path at `000d0952..000d09bc`. The staged path checks its nonzero
admission argument, existing report flags, bank-local command and state
bits, and the bank bit in `fffe9736`. Shared state inputs include
`fffe9972`, `fffe994a` and `fffea9ee/fffea9ef`. The bit in
`fffe9736` can reset the bank counter or qualify its saturating
increment according to the selected staged branch.

The alternate path tests the bank bit in `fffe9973`, the command
comparison bit in `fffea9ee` and the corresponding status in
`fffe9736`. It can increment the same counter and set both report
bits once the full threshold is met. The counters are `fffeaa00`
and `fffeaa01`. The staged thresholds are inclusive
`ROM8[000089f6] = 10` for the marker and
`ROM8[000089f7] = 100` for the full report.
The alternate path uses the full threshold of 100 for both flags.

The stock scheme byte `00008561` is `0x05` in 1ND0A and `0x0d` in
1ND3B. Bit `0x04` is set in both. The primary coordinator reads the
two 16-bit PWM command words at `fffe9694` and `fffe9696`.
The selected stock branches store bank bits for command zero and
command equality to `ROM16[000094d6] = 0xf333` in
`fffea9ef` and `fffea9ee`. The 8-bit command source is selected
only with scheme bit `0x04` clear.

#### Alternate primary timing route and the two P0524 records

The coordinator calls `000d11cc` for bank 1 at `000d08d4` and
tail-calls it for bank 2 at `000d09d4`. This route has its own
per-bank authorization argument, count `fffe89ff/fffe8a00`, delay
`fffe9523/fffe9524`, and excursion bits at `fffe84a1`. It shares
the selected target and centered error bytes with primary timing.

The argument comes from the bank permits at `fffea9eb` when
the operating-state tests at `000d063e..000d0668` pass. The scheme
difference in bit `0x08` participates at `000d0600..000d060e`.
1ND0A goes straight to `000d0610`. 1ND3B can skip the subsequent
argument production when the bank-independent state at `fffeb89c`
has bit `0x04` set and `fffeb8a4 & 0x02` is clear. The shared
voltage and outer readiness checks still apply.

The alternate routine requires a non-neutral target, clear selected
record bits, the applicable local state and a target step at most 2.
It rearms its delay from the same stock value 10. With zero delay,
ROM `00008023:0x80` permits saturating count. It checks the centered
error against upper and lower deviations at `00008875/00008874`,
which are `0x1a` and `0xff`. The computed lower bound is
`128 - 255 = -127`, so the unsigned error byte cannot satisfy the
strict lower excursion. The upper one requires a byte above 154.
A count strictly above `ROM8[00008394] = 0x3b` and the recorded
excursion cause the following calls.

| Bank | Indexed marker | Full report | Complementary state service |
| --- | --- | --- | --- |
| 1 | `000d13a6`, index 309 | `000d13ae`, index 309 | `000d13ce`, index 309 |
| 2 | `000d1396`, index 310 | `000d13ae`, index 310 | `000d13ce`, index 310 |

The marker and full reporter receive a complete unsigned index, including
the high byte. These calls use two stock descriptors encoded as P0524.
The bank assignment follows the argument to `000d11cc`. The
complementary service clears bit 7 of runtime record byte 1 at
`000ce118` and clears the shared selection when it names this index.
The physical failure behind the P0524 code remains open.

#### Primary report and snapshot stores

| DTC | Per-bank mask | Early marker call | Full reporter call |
| --- | --- | --- | --- |
| P0011 | `0x01` | `000d152e` | `000d1562` |
| P0021 | `0x02` | `000d1596` | `000d15ca` |
| P0075 | `0x01` | `000d15fc` | `000d160e` |
| P0081 | `0x02` | `000d1620` | `000d1632` |

The dispatcher reads timing marker and full flags at `fffeaaaf`
and `fffeaaab`, and circuit marker and full flags at `fffeaab0`
and `fffeaaac`. On the timing branches it copies the selected
three-byte record into bank 1 snapshot `fffed6e2` or bank 2
snapshot `fffed6e5` after the marker or full report.
The circuit branches skip these copies. A tail branch at `000d1642`
leads to local flag cleanup `000d0112` for `fffeb7ed & 0x10` set.

### Independent capture-based P0011 and P0021 timing qualification

The wrapper checks group enables `ROM8[0001aef4] = 0x3f` and
`ROM8[0001af06] = 0x07`. The stock bit `0001aef4:0x20` selects
the active setup at `000dbcf6`. Both the setup and the call at
`000dc10e` require `fffeb8f7 & 0x02` clear and readiness
`fffeb842 & 0x20` set. Otherwise the wrapper takes its cleanup
or re-arm path.

The decision routine builds a two-bit scenario mask. Scenario 1
requires `(fffeb8a5 & 0x55) == 0x55` and zero at `fffeba77`.
Scenario 2 requires `fffe947a & 0x40`, `fffeb8a7 & 0x80`,
`(fffeb8a4 & 0x14) == 0x14`, `(fffeb8a5 & 0x44) == 0x44`,
and zero at `fffeba78`. The common branch requires any scenario,
`fffe80d8 & 0x02` clear and the stock battery snapshot range of
`(125, 200]`. The guard at `000db532..000db66e` requires mask
`0x60` clear in selected diagnostic state bytes. The reviewed
registered guards include P0340, P0345, P0011 and P0021.
The separate word-addressed state at `fffed67c` also supplies a
guard byte. Its role as a registered DTC is unresolved.

Under the applicable scenario bit, the routine requires the selected
target `fffe9328` to equal `0x8000` and the delay at `fffeb9b4`
or `fffeb9c8` to be zero. Their matching reload bytes are
`ROM8[000084d4] = 0x0a` and `ROM8[00008663] = 0x0a`.
Failure reloads the affected delay. If neither branch qualifies,
the function neutralizes the centered errors and rearms the bank
timers.

The decision reads the unsigned capture-derived phase bytes at
`fffe92be/fffe92bf`. Vector slots `00020198/00020194` select IMI1F
`0002e0e0` for bank 1 and IMI1E `0002dd58` for bank 2.
The bank 1 stores are `0002e368/0002e418` and the bank 2 stores
are `0002dfaa/0002e094`. The monitor stores
`128 + clamp(sample - reference, -128, 127)` at `fffe8710/fffe8711`
through `000db75a/000db830`. The bank references are
`ROM8[00008311] = 0xb4` and `ROM8[00008314] = 0xb4`.
Both scenario windows use inclusive centered bounds of 102 and 154.
The deviations at `00008872..00008873` and
`00008694..00008695` are `1a 1a` in both images.

| DTC | Marker timer | Full timer | Marker / full call | Three-byte snapshot |
| --- | --- | --- | --- | --- |
| P0011 | `fffeba74` | `fffeba70` | `000db7ba` / `000db7e0` | `fffed6dc`, byte 1 at `fffed6dd` |
| P0021 | `fffeba73` | `fffeba6d` | `000db896` / `000db8b4` | `fffed6df`, byte 1 at `fffed6e0` |

The independent branch compares the bank error strictly outside the
window and checks the respective bit at `0001af13`. An expired marker
timer calls the indexed marker, and an expired full timer calls the
dispatcher. Each positive action copies the indexed runtime record.
Failed bank qualification reloads the marker from
`ROM8[00008c40] = 30` and full delay from `ROM8[00008c3c] = 30`.
Vector slot `000201e4` selects the ATU-II channel 3A compare service
`0002040c`. It advances the compare by 320 hardware timer counts
at `00020466..00020476`. The cascaded dividers at
`0002059a..000205a2` and `0002063c..00020644` admit one pass per
100 interrupts. The independent delays and timers decrement at
`000206e8` inside `[fffeb98e, fffeba85)`. The primary start delays
decrement at `00020662` inside `[fffe9516, fffe9590)`. Both byte
loops preserve zero. The qualification-pass counters above
increment in their diagnostic routine.

### Exact descriptors and visibility

The common marker at `000ce048` sets bit 7 of byte 1 of the runtime
record and signals report activity at `fffebf4a`. The full report
dispatcher at `000ba0b8` calls the marker at `000ba126`. The
descriptor base is `0001be00` with stride 12 and the attribute
pointer base is `0001cd84` with stride four. Runtime records have
base `fffed298` and stride three.

| DTC and bank | Index | Exact descriptor bytes at address | Attribute pointer slot -> word | Runtime record |
| --- | --- | --- | --- | --- |
| P0011 B1 | 198 | `0001c748` `370300000000001100000000` | `0001d09c -> 00017bfe = 00a0` | `fffed4ea` |
| P0021 B2 | 199 | `0001c754` `370200000000002100000000` | `0001d0a0 -> 00017c00 = 00a0` | `fffed4ed` |
| P0075 B1 | 52 | `0001c070` `130400000000007500000000` | `0001ce54 -> 00017c0a = 00a0` | `fffed334` |
| P0081 B2 | 53 | `0001c07c` `130300000000008100000000` | `0001ce58 -> 00017c0c = 00a0` | `fffed337` |
| P0524 B1 | 309 | `0001cc7c` `550700000000052400000000` | `0001d258 -> 00017c06 = 00a0` | `fffed637` |
| P0524 B2 | 310 | `0001cc88` `550600000000052400000000` | `0001d25c -> 00017c08 = 00a0` | `fffed63a` |

Each exact code occurs once except P0524, which occurs in the two
separate bank records. The surveyed normal descriptor table contains
no P0010/P0020 or P052A/P052B/P052C/P052D entries. Both SCI1 and CAN
Mode 03/07 test attribute bit `0x0080`, present in all six
descriptors. The Mode 07 masks computed from record bytes 0 and 1
also pass the stock group bytes above. Actual response inclusion
still follows the runtime record status and transport gates.

### Pair comparison and unresolved semantics

The named group bytes, voltage limits, window limits, report timers,
capture references, count table and descriptor attributes match both
images. The scheme difference at `00008561` changes the conditional
qualification described above. Offset `00008c43` also changes
`0x2a -> 0x32` from 1ND0A to 1ND3B. The coordinator uses this
unsigned threshold with hysteresis 16 at `000d0346..000d0362`
to publish bit `0x20` at `fffeb8a5`. Adjacent differences at
`00008c3e` and `000089f8..000089f9` lie outside the reload and
count tests cited above.

The source proves which records the active scheduling routes can select
and their exact gates. The physical meaning of individual unnamed
admission flags, the extension status at `fffed67c`, and on-engine
behavior of the P0524 route remain open.

## 1ME3B and 1EK7A qualification inputs

### Periodic entry and bank selection

| Operation | 1ME3B | 1EK7A |
| --- | --- | --- |
| Periodic diagnostics slot and entry | `000222c8` -> `000c0040` | `0002235c` -> `000c4884` |
| Scheduler calls primary wrapper | `000c01b0` -> `000da270` | `000c4a00` -> `000e464c` |
| Wrapper coordinator and report calls | `000da57e` -> `000da8a8`, tail `000da58a` -> `000dbae0` | `000e495a` -> `000e4d3c`, tail `000e4966` -> `000e607c` |
| Scheduler calls independent timing parent | `000c008c` -> `000e66d4` | `000c48d0` -> `000f10e0` |
| Parent calls independent timing monitor | `000e6b2e` -> `000e5e54` | `000f14b8` -> `000f0608` |

The wrapper sets both stock primary timing bank bits at `fffeab0e` / `fffeae32` when the common phase and operating gate passes and `fffed80f` / `fffede3e` has both bits of `0x60` clear. The phase gate tests `0x60` of byte 2 of each three-byte diagnostic entry and requires the engine operating bit `fffeb9a7 & 0x40` / `fffebd3d & 0x01`. The corresponding descriptor index groups are P0340 `66..68` / `67..69`, P0345 `130..132` / `131..133`, and P0335 `69..71` / `70..72`. The preceding byte 1 test of `0x80` converges at the same byte 2 check for either outcome. The stock timing selectors `0001afeb` / `0001ba17` are `0xfc` with bank bits `0x08` and `0x04` set. The P0524 bank bits follow the same common predicate on the stock path and use the separate `0x80` and `0x40` selectors. Each destination mask uses `1 << bank`, with zero-based bank index. The periodic parent of the independent monitor branches around its call when its own disable condition holds.

### Primary timing limit and phase-error qualification

| Role | 1ME3B | 1EK7A |
| --- | --- | --- |
| First axis input and read | `fffe818e` at `000dacac` | `fffe81b3` at `000e5228` |
| First axis base | `00013296` | `000136fe` |
| Coolant snapshot and read | `fffe8073` at `000dacd0` | `fffe8097` at `000e524e` |
| Second axis base | `0001329e` | `00013706` |
| 8 by 8 unsigned byte count table and read | `000098d4` at `000dacfa` | `00009a4c` at `000e5278` |
| Current table cell store | `000dad0c` to `fffe8404` | `000e528a` to `fffe8428` |
| Current target minus retained target | `fffe92f6` minus `fffe92fe` | `fffe92f2` minus `fffe92fa` |
| Saturated absolute delta store, threshold 2 | `000dad1e` to `fffe89a0`, ROM `00008cbe` | `000e52a6` to `fffe89b0`, ROM `00008d2b` |
| Effective count limit stores | `000dad2c`, `000dad7c` to `fffe839f` | `000e52aa`, `000e52b4` to `fffe83c3` |
| Bank 1 / bank 2 qualification counters | `fffe89a1` / `fffe89a2` | `fffe89b1` / `fffe89b2` |
| Timing qualifier, B1 and B2 call sites | `000db304`, `000dae40`, `000daec4` | `000e5738`, `000e5310`, `000e532c` |

Both tables use the two ascending byte axes `22 24 26 28 2a 2c 38 40` and `78 7d 82 87 8c 91 96 aa`. Each loop starts with index 1 and compares the input against axis entries 1 through 7, advancing for equality or greater. The selected cell is at row-major offset `8 * (first_index - 1) + second_index - 1`. All 64 cells are `0x3c` in both stock images. The coordinator replaces the effective limit when the target-step magnitude is at most 2. On a larger step it retains the maximum of the current cell and the previous limit. The qualifier itself requires the step magnitude at most 2, so the stock effective limit on an admitted pass is 60.

The primary coordinator also tests the engine-speed snapshot `fffe8194` / `fffe81ba`. It publishes the high-speed admission bit at `fffeba0c & 0x10` / `fffebdaf & 0x20` using the identical assertion and retention floors of 136 and 120. The stock comparison bytes are `00008c78` / `00008cf0`. The primary timing argument requires that bit, coolant conditions, the primary bank-enable mask and the common operating window. On 1ME3B the stock speed publication at `000420e6` and scheduler copy `00021348..00021384` produce the high byte of `u16(fffe8176) >> 3`, at most 31. This gate clears even from a set previous state. On 1EK7A `00043172` publishes `min(u16(fffe819a) >> 6, 255)` and the scheduler carries it into `fffe81ba`, allowing those comparisons to pass under their corresponding runtime conditions.

The qualifier additionally requires the supplied bank argument to be nonzero, the bank report bit clear, the selected target different from `0x8000`, the target-step byte at most 2, and the range/timer conditions. It tests both solenoid DTC statuses and the two secondary timing record snapshots for `0x60` in byte 2. Neither bank's circuit count may be nonzero. The ROM cell must be nonzero, the bank holdoff must be zero, and the bank post-completion inhibit must be clear. The counter increments saturating at 255 on `ffff8023 & 0x80`. The snapshot task copies `ffff8024` to `ffff8023` at `0002127c` / `000212b6` before copying `ffff801b` to `ffff8024`. While the counter is at most 60, a centered primary error outside `[102, 154]` sets that bank's excursion bit if the in-window latch is clear. An in-window result sets the latch and clears the excursion. When the count exceeds 60 with the in-window latch clear and excursion set, the qualifier sets both the marker and full-report request bits. An already set in-window latch instead reaches the indexed state-service path and marks the bank complete. The schedules and list of runtime conditions establish the software predicate.

The independent monitor remains a separate P0011/P0021 path. Its inputs are the capture-byte error and neutral-target, battery and scenario admission. Its stock full-report calls and state snapshot feedback are described in `SH7059.intake-cvtc.md`.

### Solenoid electrical qualification

The stock command scheme byte is `0x0d`, testing bit `0x04` at `00008576` / `000085aa`. The scheduler mirrors the full-resolution bank command words. The coordinator compares each snapshot with zero and the full-command equality value `0xf333`. The byte-mode branch tests the alternate command byte against `0x00` or `0xff`. The per-bank comparisons set and clear independent zero and full masks. 1ME3B inlines both classifications in the coordinator. 1EK7A calls `000e5f62` twice.

| Role | 1ME3B | 1EK7A |
| --- | --- | --- |
| Live bank 1 / bank 2 PWM words | `fffe9692` / `fffe9694` | `fffe96b8` / `fffe96ba` |
| Command snapshot words | `fffe966a` / `fffe966c` | `fffe968c` / `fffe968e` |
| Full-command ROM word | `000095a8` | `00009702` |
| Full / zero state bytes | `fffeab16` / `fffeab17` | `fffeae3a` / `fffeae3b` |
| Full / zero stores | `000dae3c`, `000daec2` / `000dae26`, `000daeaa` | `000e5fa0`, `000e5fa8` / `000e5f8e` |
| Staged circuit active, live / snapshot | `fffe99e2` / `fffe9a1e` | `fffe9a2c` / `fffe9a64` |
| Alternate circuit active, live / snapshot | `fffe99e3` / `fffe9a1f` | `fffe9a2d` / `fffe9a65` |
| Scheduler transfer | Longword `fffe99e0` at `000214a2` to `fffe9a1c` at `000214b2`, low two bytes | `0x38`-byte copy `fffe99f8` -> `fffe9a30` at `000214d6`, offsets `0x34` and `0x35` |
| Electrical feedback, live / snapshot | `fffe98bf` / `fffe9759` | `fffe98fd` / `fffe9785` |
| Scheduler transfers electrical feedback | `00021448`, block offset `0xb1` | `000214a6`, block offset `0xb5` |
| Circuit count bytes | `fffeab2a` / `fffeab2b` | `fffeae50` / `fffeae51` |

The 1ME3B scheduler slot `00021fcc` selects `000427d4`. At `0004291e` and `00042938`, the task reads the 16-bit Port A data register PADR `fffff726`. It sets or clears feedback bit 0 from mask `0x0004` (PA2, stores `0004292a` and `00042936`) and feedback bit 1 from mask `0x0008` (PA3, stores `00042944` and `0004294a`). The register and masks are code-bound. The external pin mapping requires hardware evidence. 1EK7A has exact pointer `00022058` -> `000437c4` and literal `00043a14` -> `fffe98fd`. The prepared Ghidra and normalized L0 function are unavailable at `000437c4`, leaving its exact load and store anchors open.

The staged qualifier sets the per-bank live active bit when an admitted zero or full command is present. The prior active bit from the scheduler must already be set, or it resets the circuit count and returns. With that snapshot set, a zero command counts feedback clear and a full command counts feedback set. A nonmatching feedback state clears the count. A command between the two endpoints returns without advancing. Counts at or above 10 set the marker bit, and counts at or above 100 set the full-report bit. The already-reported path clears the live active bit when the engine operating bit is set.

The alternate qualifier tests its own prior active bit and the full command. It counts consecutive feedback-set passes, resetting on clear feedback or missing history. At 100 it sets both marker and full-report bits. 1ME3B uses `000db6e8` for bank 1 and inlines bank 2 in `000daed2..000daf40`, with marker and full stores `000daf32` and `000daf36`. 1EK7A uses `000e5bdc` for both banks (`000e531c`, `000e5338`). Both branches share each bank's circuit count and the dispatch masks. Wrapper and coordinator reset paths clear the applicable report masks.

### Phase-dependent P0524 qualifier

| Role | 1ME3B | 1EK7A |
| --- | --- | --- |
| Bank enable byte and read on the admitted stock path | `0001b009` = `0xcf` at `000da508` | `0001ba35` = `0xcf` at `000e48e4` |
| Bank mask written by the wrapper | `fffeab13` | `fffeae37` |
| Qualifier, bank 1 call / bank 2 tail call | `000db7ac`, `000dae54` / `000daf66` | `000e5cc2`, `000e5322` / `000e5352` |
| Result flag byte and set | `fffeabed` at `000db95a` | `fffeaf1d` at `000e5e74` |
| Bank 1 / bank 2 count | `fffe89a3` / `fffe89a4` | `fffe89b3` / `fffe89b4` |
| Bank delay base and stock reload | `fffe94f5`, `ROM8[00008382] = 0x0a` | `fffe9502`, `ROM8[00008395] = 0x0a` |
| Count limit | `ROM8[0000839b] = 0x3b` | `ROM8[000083b0] = 0x3b` |
| Lower / upper error deviations | `00008899..0000889a = ff 1a` | `00008907..00008908 = ff 1a` |
| Bank 1 / bank 2 direct marker sites | `000db946` / `000db936` | `000e5e60` / `000e5e50` |
| Full reporter call for either index | `000db94e` | `000e5e68` |

The dedicated qualifier receives a separate bank-admission argument from the coordinator. The battery window is `125 < sample <= 200`. The argument also requires the main operating bit set, the common inhibit bit clear and the coordinator's shared holdoff expired. On 1ME3B `000dabc2..000dabec` tests `fffe949b & 0x60 == 0x60`, `fffeba0c & 0x0c == 0x0c` and the selected bit of `fffeab13`. On 1EK7A `000e5104..000e5132` tests `fffe94a6 & 0x0c == 0x0c`, `fffebdaf & 0x18 == 0x18` and the selected bit of `fffeae37`. The first mask in each layout comes from the neighboring coordinate byte `fffe8195` / `fffe81bb` at `000daa70` / `000e4f06`. The second comes from the coolant snapshot. The shared scheme test additionally requires `fffeba0d & 0x02` when `fffeba05 & 0x04` is set on 1ME3B, or `fffebdb0 & 0x08` when `fffebda8 & 0x10` is set on 1EK7A. Both stock scheme bytes enable that test.

The qualifier requires the selected P0524 result bit clear, both circuit counts zero, solenoid records and independent timing snapshots clear of `0x60`, the inhibit word zero, a non-neutral target, and a target-step magnitude at most 2. It requires an expired bank delay and the post-completion bit clear. The counter increments on the same `ffff8023 & 0x80` tick as the primary timing counter and saturates at 255. A target change clears completion bits and restarts affected counters. The separate window, excursion and completion storage keeps this result independent of the primary timing request bits. The known ATU-II channel 3A countdown loop at `00020668` covers both primary timing holdoffs and both P0524 holdoffs in each layout's `0x82`-byte countdown range.

The qualifier reads the same centered primary error pair as P0011/P0021. Stock lower deviation 255 makes `error < 128 - 255` false for every unsigned error byte. Positive error `> 154` can set the excursion bit while the in-window latch stays clear. Once the count is `> 59`, a retained excursion and clear in-window latch select the direct marker and full reporter for the bank's P0524 index. The set bit prevents repeat qualification until reset. The alternate branch following an in-window result calls the indexed state service instead. The P0524 selection here derives from phase error and operating conditions. A pressure transducer input is not required by the traced qualifier.

### Descriptor binding

The source uses a 12-byte descriptor stride and a separate four-byte attribute pointer stride. Descriptor and pointer roots are `0001bf58` / `0001cf00` on 1ME3B and `0001c998` / `0001da3c` on 1EK7A. Each listed stock attribute sets bit 7. This meets the attribute test of the Mode 03/07 handlers. Record state and group restrictions remain applicable.

| Layout | Bank and code | Index | Descriptor location and exact bytes | Attribute pointer slot -> halfword location = value |
| --- | --- | --- | --- | --- |
| 1ME3B | B1 P0011 | 199 | `0001c8ac` `370300000000001100000000` | `0001d21c` -> `00017cc8` = `00a0` |
| 1ME3B | B2 P0021 | 200 | `0001c8b8` `370200000000002100000000` | `0001d220` -> `00017cca` = `00a0` |
| 1ME3B | B1 P0075 | 51 | `0001c1bc` `130400000000007500000000` | `0001cfcc` -> `00017cd4` = `00a0` |
| 1ME3B | B2 P0081 | 52 | `0001c1c8` `130300000000008100000000` | `0001cfd0` -> `00017cd6` = `00a0` |
| 1ME3B | B1 P0524 | 310 | `0001cde0` `550700000000052400000000` | `0001d3d8` -> `00017cd0` = `00a0` |
| 1ME3B | B2 P0524 | 311 | `0001cdec` `550600000000052400000000` | `0001d3dc` -> `00017cd2` = `00a0` |
| 1EK7A | B1 P0011 | 199 | `0001d2ec` `370300000000001100000000` | `0001dd58` -> `000186f4` = `00a8` |
| 1EK7A | B2 P0021 | 200 | `0001d2f8` `370200000000002100000000` | `0001dd5c` -> `000186f6` = `00a8` |
| 1EK7A | B1 P0075 | 52 | `0001cc08` `130400000000007500000000` | `0001db0c` -> `00018700` = `00a8` |
| 1EK7A | B2 P0081 | 53 | `0001cc14` `130300000000008100000000` | `0001db10` -> `00018702` = `00a8` |
| 1EK7A | B1 P0524 | 310 | `0001d820` `550700000000052400000000` | `0001df14` -> `000186fc` = `00a0` |
| 1EK7A | B2 P0524 | 311 | `0001d82c` `550600000000052400000000` | `0001df18` -> `000186fe` = `00a0` |

The P0524 paths use separate bank descriptors and distinct report selector bytes.

### Remaining evidence

- The 1EK7A Port A publisher candidate needs a prepared function and the exact per-bank feedback stores. The stock scheduler copy and the consumption of its result are established independently.
- The `ffff8023` snapshot assignment is verified. The complete event propagation to that snapshot and the observed qualification cadence remain open. Confirmation of the electrical fault response, sensor wiring and P0524 physical behavior remains a bench task.
- P0340 and P0345 records appear here as admission inputs. Their own producer monitors need a separate phase-sensor analysis. This analysis establishes the exact P0011/P0021, P0075/P0081 and P0524 report paths.
