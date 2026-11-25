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
| Scheduler transfers electrical feedback | `00021448`, block offset `0xb1` | `000214a6`, `fffe9848` to `fffe96d0`, block offset `0xb5` |
| Circuit count bytes | `fffeab2a` / `fffeab2b` | `fffeae50` / `fffeae51` |

Both periodic tasks read the 16-bit Port A data register PADR `fffff726`.
Each task copies PA2 (mask `0x0004`) to bit 0 for bank 1 and PA3
(mask `0x0008`) to bit 1 for bank 2. The set and clear paths update the
selected bit and preserve the other bits.

| Role | 1ME3B | 1EK7A |
| --- | --- | --- |
| Pending task table and pointer load sites | `00021f8c`, `00020af6` / `0002107c` | `00022018`, `00020b12` / `000210ac` |
| Slot 16 pointer and task entry | `00021fcc` -> `000427d4` | `00022058` -> `000437c4` |
| Bank 1 PADR read and set/clear stores | `0004291e`, `0004292a` / `00042936` | `0004390c`, `00043918` / `00043924` |
| Bank 2 PADR read and set/clear stores | `00042938`, `00042944` / `0004294a` | `00043926`, `00043932` / `00043938` |
| Live byte address in the literal pool | `00042a24` -> `fffe98bf` | `00043a14` -> `fffe98fd` |

On 1EK7A the copy at `000214a6` makes the sampled bits available to the
staged qualifier at `000e5b02`, `000e5b1a` and `000e5b6a` and to the
alternate qualifier at `000e5c14`. The MCU register defines the software
input boundary. Connector routing requires board evidence.

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

## SH7059 qualification clock and phase-sensor diagnostics

### Diagnostic event source

The primary timing and P0524 qualifiers use bit 7 of the periodic
snapshot at `ffff8023`. The application ATU-II compare handler sets the
pending bit. The scheduler publishes it before reloading the pending byte.

#### Pending tick generation

Application vector 120 at `ROM32[000201e4]` selects `0002040c` on both
images. At `00020466..00020476` it reads `GR3A` at `fffff4a2`, adds
`0x140` and writes the next compare. This advances the hardware compare
by 320 channel-3 timer counts per base interrupt. The two nested software
dividers are unsigned 32-bit cells. Each reached comparison increments its
cell before testing 10 and restores zero on completion of that stage.

| Operation | 1ME3B | 1EK7A |
| --- | --- | --- |
| First divide-by-ten counter | `ffff02a8` | `ffff174c` |
| First increment/test/store | `0002059a..000205a2` | `0002059a..000205a2` |
| First reset store | `0002085e` | `00020866` |
| Second divide-by-ten counter | `ffff02ac` | `ffff1750` |
| Second increment/test/store | `0002063e..00020646` | `0002063e..00020646` |
| Second reset store | `0002085a` | `00020862` |
| `OR.B #0x80` to `ffff8024` | `0002073a` | `0002073e` |

The ISR loads `GBR = ffff800c` at `0002044a..0002044c`, then uses
`R0 = 0x18` for the byte update. The update follows the second divider
and precedes the separate third divider. Later paths OR `0x40`, `0x20`
or `0x10` into the same byte. Those operations preserve the pending
`0x80` bit. The source period is therefore `10 * 10 = 100` ISR
invocations, or `100 * 0x140 = 32000` channel-3 timer counts.

#### Channel-3 input clock

| Startup operation | 1ME3B | 1EK7A |
| --- | --- | --- |
| Application calls ATU-II initialization wrapper | `0002e42a` -> `0002dea0` | `0002f132` -> `0002eba8` |
| Wrapper calls ATU-II initialization | `0002dea4` -> `0002c824` | `0002ebac` -> `0002d3c4` |
| Setup calls channel configuration | `0002c8c0` -> `0002c4aa` | `0002d460` -> `0002d04a` |
| Load `TCR3` selector 5 | `0002c50a` | `0002d0aa` |
| Write `TCR3` at `fffff4ac` | `0002c5b2` | `0002d152` |
| Write `PSCR1 = 1` at `fffff404` | `0002c8ec` | `0002d48c` |

The SH7059 hardware manual, sections 11.2.2 and 11.2.3, assigns channel 3
to `PSCR1`. Selector 1 divides the peripheral clock `Pphi` by 2, and
`TCR3.CKSEL = 5` divides that result by 32. With `Pphi` expressed in Hz,
the base compare period is `20480 / Pphi` seconds and the bit-7 request
period is `2048000 / Pphi` seconds.

Both application images program HCAN0 and HCAN1 with `BCR1 = 0xf210`
and `BCR0 = 0x0001`. The low-ROM HCAN1 initializer uses `0xf220`
and `0x0001`. Under sections 5.1, 5.2 and 17.4.4 of the SH7059 hardware
manual, both settings give two peripheral-clock cycles per quantum and
20 quanta per nominal bit (1 sync + 16 TSEG1 + 3 TSEG2). The low-ROM
setting changes the synchronization jump width from two to three
quanta. Thus the nominal CAN bitrate equals `Pphi / 40` and
`Pphi = 2 * EXTAL`.

| Controller path | 1ME3B BCR1 / BCR0 stores | 1EK7A BCR1 / BCR0 stores |
| --- | --- | --- |
| Application HCAN0 | `0011f7ac` / `0011f7b6` | `0013fe08` / `0013fe12` |
| Application HCAN1 | `0011f3aa` / `0011f3b2` | `0013fa06` / `0013fa0e` |
| Low-ROM HCAN1 | `000024a0` / `000024a8` | `0000231a` / `00002320` |

At a confirmed 500 kbit/s on one of these stock controllers, its
nominal `Pphi` is 20 MHz and its `EXTAL` is 10 MHz. This gives a
1.024 ms compare period, a 102.4 ms bit-7 request period and 6.144 s
for 60 nominal P0524 decrement periods. Reloads and request coalescing
affect elapsed monitor time. The exact PCMFlash identifications record
Hitachi CAN communication without a bitrate. The recorded 500 kbit/s
bench traffic is attributed to JK00D. An exact ECU bitrate or board
clock measurement is required to assign these nominal times.

#### Snapshot and pending-byte reload

| Operation | 1ME3B | 1EK7A |
| --- | --- | --- |
| Main-loop snapshot request test | `0002e474..0002e478` | `0002f17c..0002f180` |
| Main-loop snapshot call | `0002e482` | `0002f18a` |
| Scheduler copy entry | `00021240` | `00021274` |
| Set SR interrupt mask to 15 | `00021264` | `00021298` |
| Clear snapshot request | `00021276` | `000212b0` |
| Read pending byte `ffff8024` | `00021278` | `000212b2` |
| Write diagnostic snapshot `ffff8023` | `0002127c` | `000212b6` |
| Read reload byte `ffff801b` | `0002127e` | `000212b8` |
| Reload pending byte `ffff8024` | `00021282` | `000212bc` |

The handler sets `ffff8019 & 0x04` with `OR.B #0x14` at `000204c4`
after a separate divide-by-ten counter reaches its limit. The main loop
tests that request before calling the snapshot routine. The routine
acknowledges the request inside the same protected section as the copy.
The interrupt mask protects the old pending-byte
sample and the following reload as one critical section. The copy stores
the complete pending byte, then stores the complete reload byte. For bit 7
the exact operation is `snapshot = old_pending` and `pending = reload`.
When the reload byte's bit 7 is clear, the copy consumes the pending pulse
and a later copy publishes bit 7 clear until the ISR raises it again. The
pending byte has no event count. Multiple raises before one copy coalesce.

#### Reload-byte initialization

| Application startup operation | 1ME3B | 1EK7A |
| --- | --- | --- |
| Call RAM initialization | `0002e406` -> `0002e0a0` | `0002f10e` -> `0002eda8` |
| ROM32 bounds `ffff8000`, `ffff8068` | `00022a50`, `00022a54` | `00022ae4`, `00022ae8` |
| Load bounds and clear longwords | `0002e0ce..0002e0e0` | `0002edd6..0002ede8` |
| Other application clear stores covering `ffff801b` | `00038492`, `0003d90a` | `0003940e`, `0003e8aa` |

The startup loop writes zero at four-byte intervals from `ffff8000` up to
the exclusive bound `ffff8068`. The store at `ffff8018` covers the reload
byte and leaves bit 7 clear before the application starts the ATU-II
scheduler. The additional application loops begin at `ffff8000`, compare
with the exclusive pointer bound `ffff806a`, and also write zero. The
reviewed application accesses contain no bit-7 setter for the reload byte.

The boot-ROM clear loops at `0000120c` and `00002886` on 1ME3B and
`000010c6` and `000026d8` on 1EK7A also cover this byte with zero stores.
The 1EK7A low-ROM routine `000037e2` has a separate overlapping halfword
store at `0000387a`. It writes a zero-extended byte count to `ffff801a`,
placing the low byte at `ffff801b`. The application startup clear covers
that location. A call from the running application scheduler to this
low-ROM routine has not been established.

#### Consumers

| Bit-7 test and count | 1ME3B | 1EK7A |
| --- | --- | --- |
| Periodic diagnostics slot | `000222c8` -> `000c0040` | `0002235c` -> `000c4884` |
| Periodic diagnostics call to primary wrapper | `000c01b0` -> `000da270` | `000c4a00` -> `000e464c` |
| Timing qualifier entry | `000db304` | `000e5738` |
| `ffff8023` load and test | `000db47a..000db47c` | `000e5894..000e5896` |
| Timing count bytes, banks 1 and 2 | `fffe89a1`, `fffe89a2` | `fffe89b1`, `fffe89b2` |
| P0524 qualifier entry | `000db7ac` | `000e5cc2` |
| `ffff8023` load and test | `000db8ec..000db8ee` | `000e5e02..000e5e04` |
| P0524 count bytes, banks 1 and 2 | `fffe89a3`, `fffe89a4` | `fffe89b3`, `fffe89b4` |

Once its own admission passes, each qualifier increments the selected
unsigned byte with saturation at 255 when the snapshot bit is set. A clear
bit skips that increment. The count limits and the independent countdown
holdoffs are separate from this event source. The count advances only while the related monitor is admitted.

### Cam position monitors

#### Scheduling and registration

The periodic diagnostics slot at `000222c8` selects `000c0040`
on 1ME3B. Its call at `000c008c` reaches the phase diagnostic
parent `000e66d4`. On 1EK7A the corresponding slot, dispatcher,
call and parent are `0002235c`, `000c4884`, `000c48d0` and
`000f10e0`. The parents run three separate phase checks.

| Check | 1ME3B entry | 1EK7A entry | Corresponding JK78C entry |
| --- | --- | --- | --- |
| Activity absence | `000e54b6` | `000efcaa` | `000b987c` |
| Activity-state qualification | `000e56b4` | `000efea8` | `000b9a94` |
| Event-count qualification | `000e5984` | `000f0178` | `000b9e1c` |

Each full report receives an exact local index in R4 and calls
`000c38f8` on 1ME3B or `000c7990` on 1EK7A. The runtime
record is three bytes at `fffed420 + 3 * index` on 1ME3B and
`fffeda10 + 3 * index` on 1EK7A. The reporter invokes the
indexed marker and selects its ordinary record handling because
all six descriptor byte-8 values are zero.
The first two checks also contain companion P0335 reports and the
event-count check has its own distinct P0335 report.

#### Exact descriptor and report bindings

The 12-byte descriptor roots are `0001bf58` and `0001c998`;
the respective four-byte attribute-pointer roots are `0001cf00`
and `0001da3c`. The SAE code is the big-endian word at
descriptor offset 6. The full 12 bytes in each matched row agree
with the corresponding JK78C record even though its index differs.
The attribute target is read from the exact pointer slot above.

| Bank and check | SAE code / descriptor bytes | 1ME3B index, descriptor, pointer, attribute target, report site | 1EK7A index, descriptor, pointer, attribute target, report site |
| --- | --- | --- | --- |
| Bank 1 absence | P0340 `180500000000034000000000` | 66, `0001c270`, `0001d008`, `00017a74`, `000e554e` | 67, `0001ccbc`, `0001db48`, `0001848a`, `000efd42` |
| Bank 1 state | P0340 `180400000000034000000000` | 67, `0001c27c`, `0001d00c`, `00017a76`, `000e5750` | 68, `0001ccc8`, `0001db4c`, `0001848c`, `000eff44` |
| Bank 1 event count | P0340 `180300000000034000000000` | 68, `0001c288`, `0001d010`, `00017a78`, `000e5a66` | 69, `0001ccd4`, `0001db50`, `0001848e`, `000f024c` |
| Bank 2 absence | P0345 `2a0200000000034500000000` | 130, `0001c570`, `0001d108`, `00017a6c`, `000e559a` | 131, `0001cfbc`, `0001dc48`, `00018480`, `000efd8e` |
| Bank 2 state | P0345 `2a0100000000034500000000` | 131, `0001c57c`, `0001d10c`, `00017a6e`, `000e57a4` | 132, `0001cfc8`, `0001dc4c`, `00018482`, `000eff98` |
| Bank 2 event count | P0345 `2a0000000000034500000000` | 132, `0001c588`, `0001d110`, `00017a70`, `000e5aa8` | 133, `0001cfd4`, `0001dc50`, `00018484`, `000f028a` |

Every 1ME3B attribute word is `00a0`. Every 1EK7A attribute word is
`00a8`. The R4 loads for bank 1 are in the report call delay slots.
The higher bank-2 indices use a signed-byte immediate followed by
zero extension in the slot. The companion crank indices in the
three checks are 69/70/71 and 70/71/72, respectively.

The intake CVTC qualifier reads byte 2 of these distinct runtime records
under mask `0x60`. Repeated SAE identifiers therefore retain separate
monitor provenance.

#### Scheduled admission

The parent uses the following masks in a primary and a second-bank ROM
byte. The primary byte also contains the companion crank arms. Either
cam-bank enable or the companion enable is sufficient to schedule the
corresponding helper when the shared runtime gate passes.

| Check | Primary bank 1 | Second byte bank 2 | Primary companion |
| --- | --- | --- | --- |
| Activity absence | `0x20` | `0x04` | `0x04` |
| Activity state | `0x10` | `0x02` | `0x02` |
| Event count | `0x08` | `0x01` | `0x01` |

These bytes are `3f/07` in both stock images at
`0001afcc/0001afde` and `0001b9f8/0001ba0a`, respectively.
The common parent gate requires `fffeba65 & 0x02` clear and
`fffeb9a7 & 0x40` set on 1ME3B. On 1EK7A it requires
`fffebe09 & 0x01` clear and `fffebd3d & 0x01` set. Each helper
applies the lane enable again before its specific report. The parent
call sites are `000e678c/000e684e/000e68cc` and
`000f1190/000f11e8/000f126a` in the order above.

#### Activity absence

The parent captures the live supply byte into a reference on first
entry with its capture latch clear. The common helper gates require
the reference to be at least 131, the live byte to be at least 75,
and the live byte to be below the reference minus 12 with that
difference floored at zero. The helper also requires the activity
admit bit `0x02` in the front-state byte, the shared wait byte zero,
the local hold bit clear and the runtime inhibit clear. On 1ME3B the
front-state bit `0x04` can inhibit because the ROM override bit is
clear. On 1EK7A the override bit is set.

With a qualifying episode, the selected bank's activity byte must
be zero and its countdown must reach zero. Inhibited or nonzero
activity reloads the bank countdown to 100. A rejected supply window
also sets the local hold bit. The parent clears both activity bytes
on the readiness transition before testing absence.

| Input | 1ME3B | 1EK7A |
| --- | --- | --- |
| Front state, shared wait | `fffe80d0/fffe95da` | `fffe80f4/fffe95e7` |
| Local hold bit `0x40` | `fffe946d` | `fffe9479` |
| Helper inhibit | `fffeb990 & 0x08` | `fffebd24 & 0x04` |
| Live and captured reference | `fffe80f0/fffeaa84` | `fffe8116/fffead94` |
| Capture latch | `fffeb98e & 0x04` | `fffebd1f & 0x01` |
| ROM override, limits, drop | `00008a7f/00008bff/000084ac` | `00008af7/00008c7b/000084da` |
| B1/B2 activity bytes | `fffeb761/fffeb760` | `fffebad9/fffebad8` |
| B1/B2 countdowns | `fffebc21/fffebc22` | `fffebfc6/fffebfc7` |
| ROM reload | `000083be` | `000083d2` |

The bank-1 IMI1F capture handler stores the activity byte at
`00030f2a/00031c52`. The bank-2 IMI1E handler stores its byte at
`00030c0c/00031934`. The diagnostic parent's clearing stores for
banks 1/2 are `000e676e/000e676c` and `000f1172/000f1170`.

#### Activity-state qualification

The state helper requires the live supply byte at least 76, the same
inhibit bit clear, the operating byte at least 48, and byte 2 of
each companion P0335 runtime record clear under mask `0x60`.
The common prior-state byte must be nonzero and the selected bank's
prior-state byte must be zero. This check requires activity byte 1
and a zero bank countdown. The reload under lost qualification is 150.

| Input | 1ME3B | 1EK7A |
| --- | --- | --- |
| Operating byte and ROM limit | `fffe9784/0000884c` | `fffe97b0/000088b9` |
| Common, bank 1, bank 2 prior state | `fffe95a7/fffe95a3/fffe95a6` | `fffe95b4/fffe95b0/fffe95b3` |
| B1/B2 countdowns | `fffebc1e/fffebc1f` | `fffebfc3/fffebfc4` |
| ROM supply limit and countdown reload | `00008c01/000083ba` | `00008c7d/000083ce` |

#### Event-count qualification

The count helper also requires live supply at least 76 and the
inhibit clear. It requires `ffff803f & 0x80` set, the same three
P0335 statuses clear under `0x60`, the companion event-count byte
zero, and the operating byte at least 64. On first admission it
clears the acquisition counters and sets an episode latch. It
requires the common acquisition count to reach five and the admitted
bank's event-count byte to reach four. Below the bank threshold,
the qualification flag is set only for a nonzero bank count.

| Input | 1ME3B | 1EK7A |
| --- | --- | --- |
| ROM operating limit and bank count threshold | `000089f2/000083bc` | `00008a64/000083d0` |
| Episode latch | `fffeb989 & 0x40` | `fffebd19 & 0x20` |
| Common acquisition count | `fffe83c0` | `fffe83e4` |
| B1/B2 and companion event-count bytes | `fffe9ca0/fffe9ca1/fffe9ca2` | `fffe9d58/fffe9d59/fffe9d5a` |
| Acquisition count store | `000302a4` | `00030fcc` |
| B1/B2 event-count stores | `00030350/00030332` | `00031078/0003105a` |

The acquisition and two bank-event stores are in `0002f730` and
`00030454`, respectively. The phase-count helper and its parent
also clear the acquisition and event state when qualification drops.

#### Applicability

The exact descriptor bytes and per-bank report roles identify the same
three P0340 and three P0345 records in JK78C, 1ME3B and 1EK7A.
The phase selectors, stock countdowns 100 and 150, and bank threshold
four agree. Descriptor indices, attribute pointers, scheduler gates and raw state
addresses are layout-specific.

### Crank position monitors

#### Descriptor and status identity

Indices are decimal. Descriptor addresses use a 12-byte stride from
`0001bf58` / `0001c998`. The SAE code occupies offsets 6 and 7.
Attribute pointer slots use a four-byte stride from `0001cf00` / `0001da3c`.
Runtime records are three bytes from `fffed420` / `fffeda10`.

| Path | Layout | Index | Descriptor address and bytes | Attribute slot -> word address = value | Runtime base / byte 2 |
| --- | --- | --- | --- | --- | --- |
| Activity absent | 1ME3B | 69 | `0001c294` `180200000000033500000000` | `0001d014` -> `00017a80` = `00a0` | `fffed4ef` / `fffed4f1` |
| Activity absent | 1EK7A | 70 | `0001cce0` `180200000000033500000000` | `0001db54` -> `00018496` = `00a8` | `fffedae2` / `fffedae4` |
| Activity state | 1ME3B | 70 | `0001c2a0` `180100000000033500000000` | `0001d018` -> `00017a82` = `00a0` | `fffed4f2` / `fffed4f4` |
| Activity state | 1EK7A | 71 | `0001ccec` `180100000000033500000000` | `0001db58` -> `00018498` = `00a8` | `fffedae5` / `fffedae7` |
| Capture event count | 1ME3B | 71 | `0001c2ac` `180000000000033500000000` | `0001d01c` -> `00017a84` = `00a0` | `fffed4f5` / `fffed4f7` |
| Capture event count | 1EK7A | 72 | `0001ccf8` `180000000000033500000000` | `0001db5c` -> `0001849a` = `00a8` | `fffedae8` / `fffedaea` |
| Separate group `0x07` | 1ME3B | 20 | `0001c048` `070600000000033500000000` | `0001cf50` -> `00017ba6` = `00a0` | `fffed45c` / `fffed45e` |
| Separate group `0x07` | 1EK7A | 20 | `0001ca88` `070600000000033500000000` | `0001da8c` -> `000185cc` = `00a0` | `fffeda4c` / `fffeda4e` |

The common crank and cam DTC predicate `00027e88` / `000288d0` also
reads the group `0x07` record. The CVTC wrapper checks the group `0x18`
trio. The indexed main reporter receives those three group `0x18` indices
at the call sites below. All four descriptors have attribute bit 7 set.

The group `0x07` byte-2 mask `0x60` reaches the common phase guard,
the periodic misfire decision and the phase diagnostic enable bitmap
on both ROMs. The 1EK7A cold-start evaluator also reads it. A separate
predicate checks `0x20` in the same ten records as the common guard.
The readiness path stores one when all ten pending bits are clear.

| Use of index 20 | 1ME3B | 1EK7A |
| --- | --- | --- |
| Pending-only predicate / first byte-2 load | `00028058` / `0002805c` | `00028aa4` / `00028aa8` |
| Readiness prerequisite store | `000bb48e` -> `fffefa4c` | `000bfaea` -> `ffff00bc` |
| Enable bitmap byte-2 load / bitmap store | `0010fd8c` / `0010f9a6` -> `fffeb8d6` | `00124d7e` / `00124902` -> `fffebc59` |
| Periodic misfire loads | `000cb32a`, `000cb3ea` | `000d09c0`, `000d0b0a` |
| Cold-start load | | `000f430e` |
| Pending scrub byte-2 store | `000c385e` | `000c7902` |
| Stock group selector byte for Mode 07 | `0001afbb = 0x00` | `0001b9e7 = 0x00` |

The alternate very-small-leak monitor calls the pending scrub at
`0010c5c4` / `001206a8`. The scrub increments a saturating counter
and starts scanning at count three. It admits records with descriptor
byte 8 mask `0xc0` clear, subject to explicit index exclusions. Index
20 meets those conditions in the first descriptor range on both ROMs.
The scrub clears `0x20` in bytes 1 and 2. On 1ME3B the same loop
also calls the queue removal routine for the selected index.

The periodic diagnostic wrappers also call the indexed maintenance
functions at `000c299a` / `000c6ac6` from `000c0816` / `000c50c0`.
Their pending pass admits index 20 and clears `0x20` from bytes 1
and 2 when the default counter at `fffec392` / `fffec83e` reaches
three. The byte-2 stores are `000c2ca2` / `000c6e20`. The active
pass admits the same index because descriptor byte 8 has `0xd0`
clear. In maintenance mode one, with byte 2 bit `0x40` set and
bit `0x02` clear, stores `000c2fce` / `000c7042` clear `0x40`
and preserve `0x20`.

SCI1 and CAN Mode 07 require the selector-derived mask `1 << 6`
in the stock group byte. The zero byte excludes this record from the response
independently of its internal status. CAN Mode 03 checks byte 2
mask `0x04` and attribute mask `0x0080` at `0012dc42` /
`0012dc4a` and `0014e5e2` / `0014e5ea`. Its descriptor scan
can publish index 20 if the runtime bit is set and the response
is admitted. The ordinary report branch can
set byte 2 bit `0x20` for a supplied index at `000c3ad6` /
`000c7b0c`. The attribute word `0x00a0` makes this branch skip
the enqueue helper for index 20. The alternate indexed state setter
at `000c4b2e` / `000c9b16` can also set `0x20` for a supplied
index. The examined report calls do not establish which stock path
supplies index 20 to a setter.

The retained queue loader at `000f1f40` / `00104e9c` reads four
index words from storage addresses `0x198..0x19b`. With valid
header, read status and identities, it copies the words to a
shadow queue. When the live prefix differs, the loader copies the
shadow indices to live slots at `000f2180` / `001050de` and sets
the queue flag for non-sentinel slots. This path can restore index
20 if it is already in storage. It leaves the active byte-2 status
of the record unchanged.

Application startup calls the record initializer from `00034800` /
`000355be`. Its first loop clears byte 2 bits 0 through 2, including
the Mode 03 eligibility bit, for each descriptor-backed record.
Index 20 receives the masked store at `000c6fda` / `000cc00e`.
The loop preserves bits `0x20` and `0x40`; the later retained queue
copy leaves both bits unchanged.

The other registered stock layouts use the same index, descriptor and
attribute for P0335 group `0x07`. Each has a common phase check of
byte 2 under `0x60`. The SH7058 7MFK and 8MFK counterparts also
test byte 1 bit 7 in a separate phase predicate. Their SCI1 Mode 07
paths use the same zero group byte and selector mask. The checked CAN
paths on JK00C, JK00D, JK78C and 1ND apply the same filter.

SCI1 Mode 03 on these layouts and CAN Mode 03 on JK00C, JK00D,
JK78C and 1ND scan the runtime records with the same `0x04`
status and `0x0080` attribute masks. That scan does not use the
group byte or the retained queue as a record filter. The 7MFK
CAN service lookup for SID `0x03` at `0002543f` returns `0xff`
and the decoder takes the unsupported-service branch. Its SCI1
Mode 03 path uses the runtime scan.

#### Crank capture input

| Stage | 1ME3B | 1EK7A |
| --- | --- | --- |
| ICI0A vector and entry | `00020154` -> `0002f730` | `00020154` -> `00030454` |
| ICR0A longword read from `fffff434` | `0002f7e6` | `0003050a` |
| Capture activity byte and store of `1` | `fffeb798` at `0002f816` | `fffebb10` at `0003053a` |
| Capture holdoff byte and reload store | `fffe95a7` at `0002f818` | `fffe95b4` at `0003053c` |
| Capture-event counter increment / clear | `fffe9ca2` at `0002f8e8` / `0002f8f4` | `fffe9d5a` at `0003060c` / `00030618` |

The parent bypasses each crank check and reloads its countdown when its
startup and mode predicates request a reset.

On the ICI0A branch selected when `fffe94b6 & 0x40` / `fffe94c2 & 0x40`
is clear, the handler writes activity `1` and loads the holdoff from
`00008827` / `00008891` (stock `40`). The parent clears the activity byte
at `000e6770` / `000f1174` when it enters the fresh absence window under
its mode and initialization predicates. The absence path requires activity
`0`. The state path requires activity `1` and holdoff `0`.

On the same ICI0A branch, `ffff8029 & 0x80` admits a saturating increment
of the sample byte `fffe9202` / `fffe91fe`. The handler sets
`ffff8055 & 0x80` if the captured tooth slot differs from 9. At sample
count at least six, it reads that bit. A clear bit increments the P0335
capture-event counter, saturating at 255. A set bit clears that counter.
The branch also clears the test bit and resets the sample byte. These
operations establish the counted firmware event without assigning it an
external electrical failure waveform.

#### Crank-specific predicates

The three helpers also qualify companion P0340/P0345 records. The
conditions below cover the direct P0335 paths.

##### Activity absence

- Stock selector `0x04` in `0001afcc` / `0001b9f8` enables the crank
  sub-branch. The captured starting battery byte `fffeaa84` / `fffead94`
  must be at least 131. The current battery byte `fffe80f0` / `fffe8116`
  must be at least 75 and strictly below `max(starting_battery - 12, 0)`.
  The constants are `00008bff`, `00008c00`, `000084ac` and `00008c7b`,
  `00008c7c`, `000084da`, respectively.
- The helper also requires `fffe80d0 & 0x02` / `fffe80f4 & 0x02` set,
  `fffe95da` / `fffe95e7` zero, `fffe946d & 0x40` / `fffe9479 & 0x40`
  clear, and `fffeb990 & 0x08` / `fffebd24 & 0x04` clear. On 1ME3B it
  rejects `fffe80d0 & 0x04` set because `ROM8[00008a7f] = 0x18` leaves
  mask `0x80` clear. 1EK7A has `ROM8[00008af7] = 0x80`, which bypasses
  this particular rejection.
- Activity must be zero. The crank byte countdown at `fffebc23` /
  `fffebfc8` reloads to 100 from `000083bf` / `000083d3` on a failed
  branch. While the countdown is nonzero, the helper sets progress bit
  `0x0002` of `fffe9c92` / `fffe9d46`. A qualified zero countdown
  reports index 69 / 70 at `000e55dc` / `000efdd0` and clears that bit.

##### Activity state

- The helper first needs battery byte `fffe80f0` / `fffe8116` at least
  76 (`00008c01` / `00008c7d`) and the same shared inhibit clear
  (`fffeb990 & 0x08` / `fffebd24 & 0x04`). Stock selector `0x02` in
  `0001afcc` / `0001b9f8` enables the crank sub-branch.
- The crank sub-branch requires `fffe95a3` and `fffe95a6` / `fffe95b0`
  and `fffe95b3` both nonzero. It requires `0x60` clear in status byte 2
  of all six P0340/P0345 records. The ICI0A activity byte must be `1`
  and its holdoff must be zero.
- The crank byte countdown at `fffebc20` / `fffebfc5` reloads to 60
  from `000083bb` / `000083cf`. A nonzero countdown under the same
  predicate sets progress bit `0x0008`. A qualified zero countdown
  reports index 70 / 71 at `000e58b2` / `000f00a6` and clears that bit.
  The initial cam-only threshold branch can reset cam work state and
  then continue into this crank sub-branch.

##### Capture event count

- The helper masks interrupts for qualification. It requires battery at
  least 76, the same shared inhibit clear, and `ffff803f & 0x80` set.
  The crank branch requires selector `0x01` in `0001afcc` / `0001b9f8`,
  `0x60` clear in byte 2 of the first two P0335 records, and both
  `fffe95a4` and `fffe95a5` / `fffe95b1` and `fffe95b2` nonzero.
- The crank count must reach `4` from `000083bd` / `000083d1`. A
  qualified count of 1 through 3 sets progress bit `0x0020`. Zero and
  successful reporting clear that bit. A failed crank gate clears the
  count and its sample byte. At or above four the helper reports index
  71 / 72 at `000e5b76` / `000f0348`.
- The companion cam counter preparation tests all three crank records,
  the crank counter being zero and its own operating gates. A nonzero
  crank count resets that cam work state and reaches the crank
  comparison. The cam five-sample threshold applies to the two cam
  comparisons.

#### Countdown service

Application vector `000201e4` selects the ATU-II compare handler
`0002040c` on both layouts. Its first divider reaches ten at
`0002059e` before entering the countdown ranges. The nonzero-byte
decrement store at `000205c8` covers the ICI0A holdoff, within
`[fffe956c, fffe95f5)` / `[fffe9579, fffe9602)`. The decrement store
at `00020610` covers both P0335 countdowns, within
`[fffebc00, fffebd01)` / `[fffebfa3, fffec0b0)`. Both ranges precede
the second divider in the handler. Each byte uses the first divider's
ten-compare cadence while positive. One base interrupt advances the
`GR3A` compare by 320 channel timer counts.

#### Record stores and CVTC admission

The report sites call `000c38f8` / `000c7990` with the exact index
loaded into R4 in the delay slot. The indexed marker `000d83ac` /
`000deb60` sets `0x80` in runtime byte 1. Descriptor byte 8 is zero,
so the full reporter takes the ordinary descriptor path. It ORs `0x03`
into byte 2 and then sets a CVTC-relevant bit through its record-state
handling. One path calls `000d8c74` / `000e2ed4`, which ORs `0x48` into
byte 2 at `000d8c88` / `000e2ee8`. The other ORs `0x20` directly at
`000c3ad6` / `000c7b0c`. Each path therefore makes the indexed byte 2
nonzero under `0x60`.

The same periodic task subsequently calls the intake CVTC wrapper at
`000c01b0` -> `000da270` / `000c4a00` -> `000e464c`. The three crank
status reads are `000da3c6`, `000da3dc`, `000da3f2` / `000e47a2`,
`000e47b8`, `000e47ce`. A set `0x40` or `0x20` skips the common
qualification. The preceding byte 1 `0x80` test converges into the same
byte 2 checks. The other required inputs include the six cam record
tests and the engine operating bit. With both primary timing ROM
selectors enabled at `0001afeb` / `0001ba17`, the selected stock path
sets both bank bits at `fffeab0e` / `fffeae32` only when the common
predicate passes and the separate byte `fffed80f` / `fffede3e` has
`0x60` clear. The common predicate also controls the corresponding
P0524 bank bits under their separate selectors.

The `R4`-shifted transfers near `000d96a4`, `000e9db4`, `000eb4a4`,
`000eb512` / `000f6caa`, `000f6eec`, `000f85c2`, `000f862c` use the same
report entry with `R4 <<= 2` in the delay slot. At the indexed reporter
they select other descriptors, even where the immediate before the
transfer matches a P0335 index.

### Upstream P0524 admission

The coordinator uses the low byte of the 1ME3B big-endian speed word `u16(fffe8176) >> 3` for the P0524 speed window. The stock publication is `000420e6` to `fffe81c8` and the scheduled longword copy at `00021348` / `00021384` sends its low byte to `fffe8195`. Its value wraps modulo 256. 1EK7A writes `min(u16(fffe819a) >> 7, 255)` to `fffe81f3` at `0004319a` and copies it to `fffe81bb` at `000213ac` / `000213c8`. This speed window uses a different byte from the primary P0011/P0021 speed floor.

| Inbound predicate | 1ME3B | 1EK7A | Stock behavior |
| --- | --- | --- | --- |
| Speed lower and upper latches | `fffe949b & 0x60`, `000daa70..000daac6`, limits `00008c98..00008c99` | `fffe94a6 & 0x0c`, `000e4f06..000e4f64`, limits `00008d0d..00008d0e` | Lower onset at 68, retention at 60. Upper onset at 255 and retention at 263 as inclusive maxima, so every byte satisfies the upper comparison. |
| Coolant lower and upper latches | `fffeba0c & 0x0c`, `000daa08..000daa46`, limits `00008c79..00008c7a` | `fffebdaf & 0x18`, `000e4e9e..000e4edc`, limits `00008cf1..00008cf2` | Both stock limits hold at 121 through 170 on assertion, and 118 through 173 with both bits retained. |
| Shared operating and inhibit snapshot | `fffeb953 & 0x50 == 0x40`, `000dab38..000dab5e` | `fffebcdf & 0x50 == 0x40`, `000e4fd4..000e5000` | The periodic snapshot copies the full live state byte. |
| Shared delay load / reload | `fffebbf1` at `000daabe` / `000daade` | `fffebf94` at `000e4f5a` / `000e4f7e` | The nonzero delay reloads to 60 with the main operating bit clear or selected target neutral. An expired delay stays expired in this local branch. |
| Shared delay initialization | `000c7060` reads `ROM8[00008c9d] = 0x3c` | `000cc094` reads `ROM8[00008d12] = 0x3c` | Sets the same byte during monitor initialization. |
| Shared delay decrement | `000206ea`, range `[fffebaff, fffebc00)` | `000206ee`, range `[fffebea7, fffebfa3)` | A nonzero byte decrements every hundredth ATU3A interrupt, after the two divide-by-ten stages. |

At `00021624..00021626` / `00021650..00021652` the snapshot reads `fffeb954` / `fffebce0` and writes `fffeb953` / `fffebcdf`. The live state has a direct set of `0x40` from PLDR bit `0x10` (MCU pin PL4) at `00042cdc` / `00043ccc`. The stock task table selects `00042ce8` at `00021fd0` and `00043cd8` at `0002205c`. The task separately writes the live `0x10` bit at `00042fda` / `00043fd4`. It sets the bit for a nonzero internal result in `r6` and clears it for zero. The 1EK7A entry has the live-byte literal load at `00043cf0`. The stock entry, branch and store are byte-bound. The supplemental operating-enable service for the wrapper reads the same snapshot and additionally checks its own inhibit masks. Its exact outputs and inputs are documented in `SH7059.rear-o2.md`.

The stock scheme byte `0x0d` enables the conditional pair: if the phase-disparity latch (`fffeba05 & 0x04` / `fffebda8 & 0x10`) is set, the paired state bit (`fffeba0d & 0x02` / `fffebdb0 & 0x08`) must be set. The CVTC control task compares the two half-scale intermediate phase words and reloads its delay if the absolute difference is at most `0x1a << 7`. With the stock scheme's bit 0 set, it tests `fffe80ed` / `fffe8113` against `0x32`. A greater reading, its control-enable bit set, a greater phase disparity, an expired delay and the conditional bank-bit tests admit the latch set at `0011bd7a` / `0013a9ba`. When control enable clears, `0011bd96` / `0013a9d6` clears the disparity latch and rearms its delay. The related control paths also clear it at `0011bdec` / `0013aa2c`.

The same state handler sets the paired bit at `0011bdbc` / `0013a9fc`, `0011be1c` / `0013aa58`, or `0011bf06` / `0013aaf0` when handling the separate pending transition in `fffeba05 & 0x08` / `fffebda8 & 0x20`. The set is conditional on the paired bit being clear at entry to each transition. The consumer of the paired bit has no direct dependence on the primary high-speed threshold. The other masks in these packed control bytes have separate owners.

#### Common engine-state diagnostic inhibit

The stock periodic engine-state task writes the live inhibit bit `0x10`. The scheduler copies the live byte to the common diagnostic snapshot before the CVTC coordinator reads it. P0524 admission requires this bit clear.

| Operation | 1ME3B | 1EK7A |
| --- | --- | --- |
| Scheduler pointer | `00021fd0` -> `00042ce8` | `0002205c` -> `00043cd8` |
| Live byte and initial read | `fffeb954` at `00042d02` | `fffebce0` at `00043cf2` |
| Reread preserving the other live bits | `00042ec8` | `00043ebc` |
| Set request and packed mask | `00042f36`, `fffe94a9 & 0x02` | `00043f2a`, `fffe94b5 & 0x04` |
| Release request and packed mask | `00042f8c`, `fffe94a9 & 0x04` | `00043f80`, `fffe94b5 & 0x08` |
| Release / set assignment to `r6` | `00042fa6` / `00042fb8` | `00043f9a` / `00043fb2` |
| Masked live write | `00042fd0..00042fda` | `00043fca..00043fd4` |
| Periodic snapshot store | `00021626` to `fffeb953` | `00021652` to `fffebcdf` |

The entry initializes the next value from the old bit and clears its set and release requests. It latches two pending activity bytes into the stack and clears the original bytes while interrupt priority is raised. Set and release predicates then compute this update:

```text
old = (initial_live_byte & 0x10) != 0
r6 = 0 if release_request else 1 if set_request else old
live = (reread_live_byte & 0xef) | (0x10 if r6 else 0)
```

The release branch wins when both requests are set. It also clears start-mode flags and a separate speed transition byte. The running minimum of the operating coordinate is maintained while `r6` is set and reset to `0xff` when it is clear.

##### Set and release inputs

The common gate requires the live bit `0x40` and either the stock selector bit `0x80` or a runtime companion bit `0x20`. Stock 1ME3B has `ROM8[00008a7f] = 0x18`, so the companion bit is required. Stock 1EK7A has `ROM8[00008af7] = 0x80`, so the ROM selector alone supplies that second input. The independent PL4 path sets the live `0x40` when a halfword read of PLDR `fffff75e` returns bit `0x10` set.

| Role | 1ME3B | 1EK7A |
| --- | --- | --- |
| Runtime companion for common gate | `fffe944b & 0x20` | `fffe9457 & 0x20` |
| Activity bytes exchanged with the interrupt paths | `fffe9205`, `fffe8fbc` | `fffe9201`, `fffe8fb8` |
| Mode bit and state word in the activity predicate | `fffe9443 & 0x10`, `fffe98f0` | `fffe944f & 0x10`, `fffe9938` |
| State-expiry context byte | `fffebcc8` | `fffec077` |
| Transition latch and companion | `fffeba40 & 0x01`, `fffe94a8 & 0x80` | `fffebde4 & 0x20`, `fffe94b3 & 0x01` |
| Transition delay and sampled byte | `fffebbbc`, `fffe98ea` | `fffebf5f`, `fffe9928` |
| Live speed byte | `fffe81cc`, store `00042182` | `fffe81f2`, store `00043172` |
| Stock upper speed and transition-sample limits | `0000886f = 80`, `00008870 = 24` | `000088db = 80`, `000088dc = 24` |

The task requests set under the common gate if either activity byte is nonzero and the activity predicate admits it. That predicate accepts the mode bit clear, or the state word and current expiry-context byte both zero. The alternative set route requires the transition latch and the transition sampled byte below 24, with either the paired transition bit set or the transition delay zero.

The release request is set if any of these conditions hold:

- The common gate fails, or the unsigned live speed byte is at least 80. Both speed publishers use `min(u16(high_resolution_speed) >> 6, 255)` for this byte.
- The minimum recorded operating coordinate is below 137, the current coordinate is greater than 169, and the associated delay byte is zero.
- The old inhibit is set and the first stored lookup result is zero.
- The live speed byte meets or exceeds the second stored lookup result and the associated delay byte is zero.
- The separate state-word expiry bit is set.

| Release input | 1ME3B | 1EK7A |
| --- | --- | --- |
| Recorded minimum, current coordinate, and associated delay | `fffe87db`, `fffe8164`, `fffe95bf` | `fffe87ec`, `fffe818a`, `fffe95cc` |
| Coordinate ROM limits | `00008a55 = 137`, `00008a53 = 169` | `00008aca = 137`, `00008ac8 = 169` |
| Lookup input, first and second ROM tables | `fffe8077`, `0001427a`, `00013bbe` | `fffe809b`, `000146f2`, `00014066` |
| First lookup result | `fffe94d3` | `fffe94df` |
| Second lookup result and delay | `fffe8ee5`, `fffe95ab` | `fffe8ee1`, `fffe95b8` |
| State-word expiry bit | `fffeba3a & 0x02` | `fffebdde & 0x80` |
| Release condition instruction window | `00042f38..00042f8c` | `00043f2c..00043f80` |

These rules identify the software set, hold and clear decisions feeding diagnostic admission. The electrical signal at PL4 on the installed vehicle remains a separate measurement.

### Remaining evidence

The source of an active status for P0335 group `0x07` remains open.
The [nominal ignition reference](SH7059.intake-cvtc.md#nominal-compression-tdc-reference)
locates tooth 3 at 30 crank degrees BTDC for the scheduled cylinder.
The actual captured edge angle, board clock and electrical fault
response require evidence from the exact hardware.
