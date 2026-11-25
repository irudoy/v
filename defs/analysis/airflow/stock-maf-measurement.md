# Stock mass-airflow measurement and diagnostics

The stock ROMs retain a two-channel mass-airflow (MAF) path from analog
acquisition through voltage publication and calibrated airflow transfer.
The diagnostic publisher reads the voltage and total-airflow words. The
MAF electrical and range/performance monitors have their own snapshots,
admission conditions, and DTC report paths.

## Service 0x22 readouts

The family `0x12` handler uses the low request byte as the index of a
four-byte pointer. The default branch appends the byte at the selected
pointer and the byte at the following address, in that order. `0x1204`
and `0x1205` carry the conditioned bank 1 and bank 2 voltage words.
`0x1209` carries the separately scaled total-airflow word.

| ROM | `0x1204` record and source | `0x1205` record and source | `0x1209` record and source |
| --- | --- | --- | --- |
| JK00A, JK03A, JK03B, JK08A | `000228ac` -> `ffff101c` | `000228b0` -> `ffff101e` | `000228c0` -> `ffff3852` |
| JK00C | `00022948` -> `ffff1024` | `0002294c` -> `ffff1026` | `0002295c` -> `ffff396e` |
| JK00D | `00022948` -> `ffff1024` | `0002294c` -> `ffff1026` | `0002295c` -> `ffff3982` |
| JK78C | `00022928` -> `ffff1024` | `0002292c` -> `ffff1026` | `0002293c` -> `ffff3a9a` |
| 1ND0A, 1ND3B | `00022c80` -> `fffe8024` | `00022c84` -> `fffe8026` | `00022c94` -> `fffead0a` |
| 1ME3B | `00022cf4` -> `fffe8024` | `00022cf8` -> `fffe8026` | `00022d08` -> `fffeae4e` |
| 1EK7A | `00022d88` -> `fffe8028` | `00022d8c` -> `fffe802a` | `00022d9c` -> `fffeb186` |

The [service inventory](../../../tools/diagnostics/README.md) verifies the
publisher and pointer tables against each registered image. The four 7MFK
publisher and table regions are byte-identical. The JK08A PID `0x10` path
establishes the `g/s * 100` declaration for its diagnostic word. The
cross-layout pointer and producer matches establish the firmware source
and arithmetic. Physical transfer at the sensor depends on the vehicle.

## 1ME3B and 1EK7A total-airflow calculation and publication

The dual-bank transfer function stores both interpolated halfwords, then
copies the values to the two halfword contribution slots. The same function
also sums the two separate 32-bit bank contributions, a signed correction
halfword and a supplemental unsigned halfword. It floors this 32-bit sum
at zero. The function finishes by restoring its frame and tail-branching
to the separate halfword accumulator.

| Operation | 1ME3B | 1EK7A |
| --- | --- | --- |
| Transfer and tail branch | `0004656a`, `000467e6` -> `00047156` | `00047816`, `00047af4` -> `00048468` |
| Bank 1 halfword contribution | `00046724` -> `fffe8de0` | `000479e4` -> `fffe806e` |
| Bank 2 halfword contribution | `00046734` -> `fffe8de2` | `00047a3e` -> `fffe8070` |
| Supplemental halfword input | `fffe9338` | `fffe9334` |
| 32-bit bank contribution pair | `fffe8d9c` and `fffe8da0` | `fffe8040` and `fffe8044` |
| Signed correction halfword and 32-bit combined store | `fffe8dc6`, `000467de` -> `fffe8dd4` | `fffe8dc6`, `00047ae8` -> `fffe8dd4` |
| Base Fuel Schedule producer reads the 32-bit combined value | `00048298` at `0004832a` | `000495c8` at `0004965a` |
| Halfword accumulator selector | `ROM8[00008943] = 1` | `ROM8[000089ad] = 1` |
| Accumulator store and previous-cycle snapshot | `000471c4` -> `fffe8d98`, `fffe8db0` | `000484d6` -> `fffe8dac`, `fffe8dba` |
| Accumulator snapshot copy in `0002040c` | `00020a22` / `00020a30`, high halfword of the longword | `00020a34` / `00020a38`, halfword |
| Offset and combined halfword store | `ROM16[000092f4] = 0`, `000471d8` -> `fffe804e` | `ROM16[00009438] = 0`, `000484ec` -> `fffe8072` |
| Wire multiplier and publication | `ROM8[000083c1] = 105`, `00048d58` -> `fffeae4e` | `ROM8[000083d9] = 105`, `0004a088` -> `fffeb186` |

The halfword accumulator adds the two unsigned bank halfwords and the
supplemental halfword. With a nonzero selector it calls the mask helper
with `selector - 1` and applies the resulting power-of-two weight to the
previous-cycle accumulator. The unsigned division is
`(sum + (weight - 1) * previous) / weight` with truncation. If the quotient
equals the previous value and is below the unfiltered sum, the accumulator
adds one before saturating to 65535. The combined halfword subtracts a
calibrated unsigned offset with a floor of zero. The diagnostic producer
applies `(ROM8[multiplier] * combined) >> 8`, saturates to 65535, and stores
the result for `0x1209`. The 32-bit corrected value develops in parallel
and feeds the Base Fuel Schedule producer.

The exact producer and physical interpretation of the supplemental halfword
are open. Its reads in the two calculations establish its arithmetic role.

## 7MFK diagnostic dispatch

`00080f82` forwards the asserted bank monitor results to the indexed
reporter `0007d8b8`. JK00A, JK03A, JK03B and JK08A have identical
report dispatch instructions, MAF descriptor records and attributes.
The [7MFK range model](../diagnostics/JK08A.maf-range-monitor.md)
describes the distinct bank range computations and their conditions.

| Input | DTC | Index and descriptor | Attribute address and value | Reporter call |
| --- | --- | --- | --- | --- |
| Bank 1 range | P0101 | `186 / 00019c18` | `00015fd4 / 0670` | `00080f98` |
| Bank 1 circuit low | P0102 | `187 / 00019c24` | `00015fd0 / 06f0` | `00080fa4` |
| Bank 1 circuit high | P0103 | `188 / 00019c30` | `00015fce / 06f0` | `00080fba` |
| Bank 2 range | P010B | `7 / 000193b4` | `00015fda / 0670` | `00080fde` |
| Bank 2 circuit low | P010C | `8 / 000193c0` | `00015fd8 / 06f0` | `00080fd2` |
| Bank 2 circuit high | P010D | `9 / 000193cc` | `00015fd6 / 06f0` | `00080fc6` |

## JK00C and JK00D

### Diagnostic records

Both ROM descriptor tables contain the same six records and attributes at
the same local indices. Descriptors are 12 bytes with the packed code at
offset 6. The 4-byte attribute table pointers select the 16-bit values below.
The descriptor/attribute pointer table bases are `0001c4e0/0001d2b4` in
JK00C and `0001c500/0001d2d4` in JK00D.

| DTC | Index | JK00C descriptor / attribute | JK00D descriptor / attribute | Attribute |
| --- | ---: | --- | --- | --- |
| P0101 | 183 | `0001cd74 / 00018482` | `0001cd94 / 000184a2` | `0670` |
| P0102 | 184 | `0001cd80 / 0001847e` | `0001cda0 / 0001849e` | `06f0` |
| P0103 | 185 | `0001cd8c / 0001847c` | `0001cdac / 0001849c` | `06f0` |
| P010B | 7 | `0001c534 / 00018488` | `0001c554 / 000184a8` | `0670` |
| P010C | 8 | `0001c540 / 00018486` | `0001c560 / 000184a6` | `06f0` |
| P010D | 9 | `0001c54c / 00018484` | `0001c56c / 000184a4` | `06f0` |

The periodic diagnostic task `0007ee9c` calls the MAF coordinator `0008534c`
at `0007eece` via the pool at `0007f108`. The adjacent calls are separate
monitor groups. Reporter `000808e0` accepts a local descriptor index. The
common dispatch function `000854ae` calls it at the sites below after
testing each Boolean. The first-bank indices are zero-extended in the JSR
delay slot. The intervening seventh slot at `000854da` would pass `-1`,
but its only argument producer, `00085a52`, returns constant zero.

| Outcome | P0101 | P0102 | P0103 | P010B | P010C | P010D |
| --- | --- | --- | --- | --- | --- | --- |
| Report call | `000854e6` | `000854d0` | `000854c4` | `0008550a` | `000854fe` | `000854f2` |

`0008534c` runs monitor comparisons only with bit `0x40` set in
`ffff4367` (JK00C) or `ffff437b` (JK00D). `00084834` writes that bit
at `00084872` according to masks `0x80`, `0x18`, and `0x20` of the
three source bytes at offsets `3`, `7`, and `0x6d` from `ffff431c`
or `ffff4330`: the first mask must be set and the other masks clear.
With admission clear, the coordinator reloads the timers and returns
without calling the reporter.

### Sensor transformation and outputs

`00020a06` calls `00028d00` through the pointer at `00021844`, with
the JSR at `00020a7a`. The same acquisition function is present on both
images. It reads the unsigned ADC result halfwords and shifts each right
by six. `ADDR4` feeds bank 1 and `ADDR15` feeds bank 2. The neighboring
`ADDR3` read at `00028d12` is stored in a separate slot.

| Stage | Bank 1 JK00C / JK00D | Bank 2 JK00C / JK00D |
| --- | --- | --- |
| Peripheral register and acquisition read | `fffff808` at `00028d1e` | `fffff826` at `00028d30` |
| Right-aligned sample and store | `ffff1dd6 / ffff1dde` at `00028d2c` | `ffff1dd8 / ffff1de0` at `00028d3e` |
| Scaled circuit word from `0003d1bc` | `ffff1024 / ffff1024` | `ffff1026 / ffff1026` |
| Periodic diagnostic snapshot | `ffff1018 / ffff1018` | `ffff101a / ffff101a` |
| Conditioned transfer input from `0003bc3e` | `ffff1eb4 / ffff1ebc` | `ffff1eb6 / ffff1ebe` |
| ROM transfer curve | `00016656 / 00016676` | `000165d6 / 000165f6` |
| Curve result, then copied word | `ffff105c`, then `ffff1060` | `ffff105e`, then `ffff1062` |

The bank argument of `0003d1bc` selects the sample and circuit word by
two-byte stride. `00069448` checks the shared Q15 gain at `ffff4a62`
or `ffff4a76` when bit 0 of `ffff43fa` or `ffff440e` is clear. It
retains the gain within `0x7900..0x8700` inclusive and otherwise loads
`0x8000` from `0000934a/00009358`. The scaled word returned through
`00069498` is `min(65535, (sample * gain) >> 15)`. `0003d1bc` increments
the scaled word if the input sample is `0x03ff`, then writes it at
`0003d204`. `0003d210` independently copies the ADC sample to the older
bank-specific observation slot. The scheduler at `00020f38` copies
12 bytes from `ffff1020` to `ffff1014`, placing the circuit words into
the monitor snapshot. The snapshot uses the same RAM addresses on both
stock images.

The two-bank signal coordinator `0003b6b8` applies the bank-indexed stages in
order. The two transfer calls at `0003b6e4` and `0003b6fa` use the word input
at `ffff1eb4/ffff1eb6` in JK00C. The call argument is
`uint16(uint16(sample) << 4)`, equivalent to `(sample & 0x0fff) << 4`.
The independent ROM curve blocks in JK00C start at `00016656` and `000165d6`.
The unsigned interpolation entry `00027014` returns the bank words, stored
at `ffff105c/ffff105e` at `0003b6ec/0003b702`. The second store occurs in
the delay slot of the following call. The bank circuit diagnostic words are
`ffff1024/ffff1026`; `0003d1bc` supplies them.

The diagnostic publication function `0003d160` invokes `0003d1bc` for each
bank, then invokes `0003d210` for both banks. At `0003d17e` it tests local
record `0x0127` through `00026938` and publishes the result as one status
bit. It multiplies the unsigned word at `ffff1064` by the unsigned ROM
byte at `000083ee` (`0x69` in JK00C), shifts right by eight, saturates to a
word, and writes the result at `0003d1b0`. The existing KB `maf_total/ram`
name identifies this publication at `ffff396e` in JK00C and `ffff3982`
in JK00D. The immediate operand `ffff1064` is produced by `0003c02a`,
which reads both bank words at `ffff1060/ffff1062`. The publication's input
and output use firmware counts.

The conditioner `0003bc3e` reads the scaled circuit word and initializes
the transfer input directly when the bank's bit is clear. Later calls
derive a correction from the bank accumulator and ROM terms, then store
`uint16(circuit_word - correction)`. `0003b736` copies each curve result
to its adjacent output word. `0003b75e` operates on the copied word and
either copies it to the bank filter state or uses a weighted update with
one-count anti-stall movement towards the input. `0003bcf6` selects the
active or fallback bank contribution, and `0003bffe` publishes the
nonnegative 32-bit aggregate of both contributions, a signed correction
and an unsigned offset. The 32-bit result is `ffff1ea4` in JK00C and
`ffff1eac` in JK00D. The word split used by the diagnostic publication
is independent of that aggregate. `0003c02a` sums the two curve copies
and an unsigned offset, applies its configured smoothing and one-count
anti-stall increment, caps at `0xffff`, subtracts stock floor zero with
a lower limit of zero, then stores the result at `ffff1064`.

### Electrical monitors

The first-bank ROM enable byte is `0001b66c/0001b68c = 0x1d`. The
second-bank enable byte is `0001b63c/0001b65c = 0x07`. These values admit
each high and low monitor, conditional on the common runtime admission.
Every candidate also requires `ffff431f.6` / `ffff4333.6` clear and zero
from the related-record predicate `0002652a`. In the table, `V` is the
unsigned diagnostic snapshot word of the bank, `S` is `RAM16[ffff10d6]`,
and `E` is `RAM8[ffff11c1]`. The high branch additionally requires the
shared byte at `ffff44df/ffff44f3` zero.

| Code | Decision entry | ROM mask | Stock comparison | Main countdown JK00C / JK00D |
| --- | --- | --- | --- | --- |
| P0103 | `0008553c` | Bank 1 `0x04` | `V >= 0x03d4` and `E < 0xc1` | `ffff468c / ffff46a0` |
| P0102 | `000856e8` | Bank 1 `0x08` | `V < 0x0050` and `S > 0x001f` | `ffff4688 / ffff469c` |
| P0102 auxiliary | `000857ea` | Bank 1 `0x08` | `V < 0x0000` and `S >= 0xffff` | `ffff4684 / ffff4698` |
| P010D | `00085614` | Bank 2 `0x01` | `V >= 0x03d4` and `E < 0xc1` | `ffff468a / ffff469e` |
| P010C | `000858aa` | Bank 2 `0x02` | `V < 0x0050` and `S > 0x001f` | `ffff4686 / ffff469a` |
| P010C auxiliary | `00085998` | Bank 2 `0x02` | `V < 0x0000` and `S >= 0xffff` | `ffff4682 / ffff4696` |

The auxiliary predicates cannot pass in either stock ROM because `V` is
unsigned. The two low branches per bank are ORed at the coordinator.
The main countdown reload comes from `00008fc0/00008fce = 0x00be`.
Loss of the candidate also reloads its byte countdown to `0x1e` and
clears the one-shot accounting bit. While the candidate holds, the byte
countdown admits the related-record call to `00090f98`, the zero word
countdown admits the full reporter, and the accounting path tests the
remaining word against `max(0, reload - 10)`. The high-path helper
`00086d7a` also reloads the high timers when either live word falls
below `0x03d4`.

| Calibration | JK00C | JK00D | Raw value |
| --- | --- | --- | --- |
| Upper circuit threshold | `00008fe0` | `00008fee` | `03d4` |
| Lower circuit threshold | `00008fe6` | `00008ff4` | `0050` |
| Auxiliary lower circuit threshold | `00008fe8` | `00008ff6` | `0000` |
| Auxiliary qualifying word | `000091be` | `000091cc` | `ffff` |

### P0101 and P010B range-performance

Bank 1 `00085a56` uses bit `0x10` of the first-bank enable byte. Bank 2
`00086296` uses bit `0x04` of the second-bank enable byte. Both bits are
set in both stock ROMs. The common selector is `00008dcd/00008dcf = 0x7e`.
Bit `0x20` bypasses the model composition, its threshold comparisons,
and the comparison-driven timer reload. The direct branch evaluates
two raw candidates per bank. With `A = RAM8[ffff11c0]`,
`B = RAM16[ffff110a]`, and the bank's snapshot `V`, the exact direct
comparisons on both stock ROMs are:

```text
candidate_1 = A >= 0xa0 && B >= (0x96 << 2) && V < 0x0124
candidate_2 = A < 0x50 && B < (0x24 << 2) && V >= 0x01c4
```

The raw thresholds reside at `00008a72/00008a73`, `00008bfd/00008bfe`,
`0000963c/0000964a` for the first candidate and `00008a74/00008a75`,
`00008bfe/00008bff`, `0000963a/00009648` for the second. The stock
selector also bypasses the candidate-driven reload and capture path:
the returned report decision is the zero test of the bank's word
countdown once the common admission and local static enable hold. The
word countdowns are `ffff468e/ffff46a2` for P0101 and
`ffff4690/ffff46a4` for P010B. Their reset at the coordinator and the
initialization helper `00086d24` uses `5 * ROM8[000082c1] = 1000`. The
range timer reload branches at `00086272` and `00086aa4` are present in
both ROMs and bypassed by the stock selector. The enabled range record
alone cannot establish an on-vehicle report.

### Remaining review

- The timer owner needs a complete indexed-decrement and task-cadence binding.
  KB identifies `0002040c` as a reader/writer of the common timer base, while
  the per-word direct stores above are resets. The raw countdown values are
  therefore reported without an elapsed-time conversion or live report claim.
- The control and calibration terms inside the bank compensation and active
  contribution are separate from the direct trace. Cross-layout equivalence
  of their full state machines requires additional literal and arithmetic review.
- Connector pins, voltage calibration and airflow engineering units require
  hardware evidence. These results bind exact stock programs and firmware counts.

## JK78C

### ADC routing and live MAF words

The task-list word at `000218d0` points to `0002ae4e`. At `0002afe2`
that task calls paired sampler `00031850` with selectors 3 and 15.
The sampler forms `fffff800 + 2 * 3 = fffff806` and
`fffff820 + 2 * (15 - 12) = fffff826`. It reads the corresponding
ADDR3 and ADDR15 halfwords at `0003193c` and `00031946`, and writes
them through the caller's SP+4 and SP+8 pointers at `00031942` and
`00031948`, respectively. The caller logically shifts both words
right by six. Its first store at `0002aff4` selects the ADDR15 result.
Bank assignment follows the downstream indexed consumers.

| Path | Bank 1 | Bank 2 |
| --- | --- | --- |
| ADC register | ADDR15 `fffff826` | ADDR3 `fffff806` |
| Ten-bit sample | `ffff1cf0`, store `0002aff4` | `ffff1cf2`, store `0002b002` |
| Raw sample copy by `00041174` | `ffff1a1a` | `ffff1a1c` |
| Conditioned electrical word from `00041128` | `ffff1024` | `ffff1026` |
| Scheduler snapshot consumed by electrical and range checks | `ffff1018` | `ffff101a` |

Task-list entry `000218e0` selects publisher `000410cc`. The entry
calls `00041128` for bank arguments 0 and 1, followed by
`00041174` for each bank. The first routine calls coefficient guard
`00085754`; when `ffff45c9 & 1` is clear the guard restores
`ffff4bf8` to `ROM16[00008fae] = 0x8000` if it is outside
`[0x7900, 0x8700]`. Scaling helper `000857a4` returns the
unsigned saturated Q15 product of that shared coefficient and the
selected sample. Parent `00041128` adds one when the input sample is
`0x03ff`, then bounds its output to a word and stores at `0004116a`.
The raw-copy store is the return delay slot at `00041180`.
The scheduler at `00020f6e` copies 12 bytes from `ffff1020`
to `ffff1014`, independently sampling the two MAF words above.

The routing is established at the MCU converter registers. Analog pin
and sensor terminal wiring and physical voltage are outside this
static evidence. The JK08A AN4/AN15 bindings cannot stand in for
the JK78C AN15/AN3 bindings.

### Transfer and flow conditioning

Task-list word `0002190c` selects the dual-bank calculation
`0003f038`. It first calls correction-state producer `0003f17c`
and preprocessor `0003f5ba` for indices 0 and 1. The preprocessor
selects the live words at `ffff1024/ffff1026` and the initialization
bits `1/2` in `ffff3bc6`. With the selected bit clear it copies the
live word and sets the bit. Otherwise, for previous prepared word
`p` and bank-specific longword `K` at `ffff3be8 + 4 * bank`:

```text
divisor = min(65535, p + ROM16[00009236])  # stock 80
numerator = floor(K * ROM16[00009230] / 65536)  # stock 335
prepared = low16(live - floor(numerator / divisor))
```

The stores are at `0003f5f0` and `0003f69c`. The earlier
raw ADC value is preserved separately. The output word wraps on
subtraction; the stock divisor offset makes the zero-divisor
alternative unreachable.

`0003f17c` seeds the bank's `K` with
`ROM16[0000927c] << 16` (stock word 24) and sets that bank's
initialization bit. Its later paths clear the correction when the
episode gates reject, or retain a Q16-scaled fraction using
`ROM16[00009104] = 0xff3c`. A one-shot branch applies a further
byte factor derived from the bank's captured episode state.
Longword stores to `K` are at `0003f4ec`, `0003f57c` and
`0003f5a4`. The source computation qualifies events using the
live bank electrical word and the independent inputs in
`ffff3bb8` and `ffff1079` blocks.

| Operation | Bank 1 | Bank 2 |
| --- | --- | --- |
| Prepared word | `ffff1dbc` | `ffff1dbe` |
| Transfer table base | `0001561c` | `0001559c` |
| Lookup call | `0003f064` | `0003f07a` |
| Unfiltered transfer word | `ffff1044`, store `0003f06c` | `ffff1046`, store `0003f082` |
| Working copy through `0003f0ec` | `ffff1048` | `ffff104a` |
| Filtered word through `0003f114` | `ffff1d64` | `ffff1d66` |

Both tables contain 64 words. Wrapper `00028238` takes
`(prepared & 0x0fff) << 4`, interpolates with implicit step
`0x100` below `0x3f00` and takes the last cell at or above
`0x3f00`. The first and last stock words are `0x0000/0xef4c`
in bank 1 and `0x0000/0xf2ba` in bank 2.
The output stage copies each bank to its working word. If
`ffff23c1 & 8` is set, `0003f114` computes
`floor((26 * input + 230 * previous) / 256)` with a one-word step
toward the input if the weighted result stalls at the previous value.
Otherwise it stores the working word directly. The coefficient
`26` comes from `ROM8[00008604]`.
Per-bank contribution stage `0003f6ae` feeds nonnegative aggregate
`0003f97c` at `ffff1da4`. The distinct total-airflow publication
in `000410cc` scales `ffff104c` by `ROM8[0000839e]`, shifts
right eight and stores the saturated word at `ffff3a9a` (stock
multiplier 105).

### Diagnostic scheduling and descriptor dispatch

Periodic dispatcher `0009c284` calls MAF coordinator `000a2cbc`
at `0009c2b6` via `ROM32[0009c4f0]`. The coordinator has a reset
branch qualified by `ffff45c6 & 8`. It admits evaluation only while
`ffff4528 & 0x10` is set. Otherwise it reloads the timer and
counter state. The admitted branch calls the low-circuit candidates,
both index variants of range checker `000a3410`, both high-circuit
candidates, and Boolean dispatcher `000a2e30` at `000a2daa`.

The stock 304-record table starts at `0001b7ac`, with 12 bytes per
record and SAE code at offset 6. Its companion pointer table starts
at `0001c5ec`. The following transfers call `0009dfa8`, with the
local index in R4 or in the call delay slot.

| DTC | Decimal index | Descriptor address / bytes | Attribute target / word | JSR |
| --- | ---: | --- | --- | --- |
| P0101 | 172 | `0001bfbc / 340400000000010100000000` | `000172f6 / 06b0` | `000a2e68` |
| P0102 | 173 | `0001bfc8 / 340300000000010200000000` | `000172f2 / 06f0` | `000a2e52` |
| P0103 | 174 | `0001bfd4 / 340200000000010300000000` | `000172f0 / 06f0` | `000a2e46` |
| P010B | 7 | `0001b800 / 040200000000010b00000000` | `000172fc / 06b0` | `000a2e8c` |
| P010C | 8 | `0001b80c / 040100000000010c00000000` | `000172fa / 06f0` | `000a2e80` |
| P010D | 9 | `0001b818 / 040000000000010d00000000` | `000172f8 / 06f0` | `000a2e74` |

The seventh dispatch branch at `000a2e5c` passes -1. The common
reporter returns for -1 at `0009dfb0..0009dfb6`. For these six
indices it invokes `000ae480` at `0009e016`, then selects the
regular record path because every MAF descriptor has byte 8 equal
to zero. The marker sets bit 7 of byte 1 at
`ffff5e94 + 3 * index` through `000ae4b6` and sets the shared
activity byte `ffff4ba0` at `000ae4e0`.

### Electrical low and high decisions

Bank-1 electrical enable byte `ROM8[0001a8c0] = 0x1c` sets
the low and high masks `0x08` and `0x04`. Bank 2 uses
`ROM8[0001a890] = 0x07` with low and high masks `0x02`
and `0x01`. The stock bytes admit both sides for both banks.
Candidates share the requirement that `ffff44df & 0x40` is
clear and helper `00027390` returns zero. The helper tests mask
`0x60` of runtime status byte `ffff5ed2`.

| Candidate | Bank 1 entry / countdown | Bank 2 entry / countdown | Additional stock predicates |
| --- | --- | --- | --- |
| Primary low | `000a307e / ffff483a` | `000a324e / ffff4838` | `u16(ffff10b6) > 31`, bank sample strictly below `ROM16[00008cd8] = 80` |
| Secondary low | `000a3186 / ffff4836` | `000a3310 / ffff4834` | `u16(ffff10b6) >= ROM16[00008e68] = 65535`, bank sample strictly below `ROM16[00008cda] = 0` |
| High | `000a2ec4 / ffff483e` | `000a2fa2 / ffff483c` | `ffff46a5 == 0`, `ffff11a3 < 193`, bank sample at least `ROM16[00008cd0] = 980` |

Inputs called bank samples here are the two electrical snapshots
`ffff1018/ffff101a`. The coordinator ORs the two low candidates
for each bank. The secondary low branch cannot satisfy the unsigned
strict sample bound in this stock image. Each eligible candidate
returns true when its main countdown is zero. The rejected path
reloads the main countdown to `ROM16[00008cb0] = 190` and
the corresponding byte countdown to 30. A zero byte countdown
also invokes `000ae480` directly with the corresponding index
before the main candidate returns. The byte and main countdown
therefore serve distinct paths.

### Stock range-performance decision

`000a3410(0)` and `000a3410(1)` run at `000a2d88`
and `000a2d8e`. Bank 1 tests `ROM8[0001a8c0] & 0x10`,
and bank 2 tests `ROM8[0001a890] & 0x04`. Both are set.
`ROM8[00008b10] = 0x1e` leaves bit 5 clear, so both evaluations
take the modeled branch. The alternate direct-comparison path is
present in code.

| Model operand | Binding |
| --- | --- |
| Per-bank operating input | `u16(ffff269c + 2 * bank)`, scaled left two with clamp to `0xffff` for the first two lookups |
| First shared curve | data `00014538`, axis `000167e4`, wrapper `0002834c` |
| Piecewise conversion | tables `0001627a / 0001625a` with wrapper `0002821c` and split coordinate `0x3c00` |
| Three byte factors | `00013970` against axis `00013980`; implicit curves `00013f80` and `00013d76`; product shifted right 14 and clamped to 255 |
| Two-dimensional correction | word surface `0000c6ce` with axes `00013980 / 000159b2`, interpolator `00028108` |
| Comparison references | threshold byte pair `ffff12d8/ffff12d9`; model byte pair `ffff1594/ffff1595` written by `000a4510` |
| Electrical branch word | live monitor snapshot `ffff1018/ffff101a` |

The modeled eligibility includes prerequisite DTC status bytes
clear under mask `0x60`, `ffff45c7 & 0x80` clear, and the
normalized gate from `00027390` clear. It checks the operating word
at `ffff5e60` against immediate `0x9200` and checks short-term
history deltas. The stock inclusive delta bounds are `[-26, 26]`
for each of the two checked word-derived byte differences,
`[-128, 127]` for the signed history-byte delta and final
signed byte, and `[-45, 45]` for the signed history-word delta.

The main predicates are distinct. The modeled low-air candidate
requires `model_byte < threshold_byte`, eligibility, the operating
byte `ffff11a2 >= 112` and the per-bank operating word at least
`ROM16[00008cd6] >> 2 = 127`. The high-signal candidate requires
the electrical snapshot at least `ROM16[00009232] = 443`, eligibility,
the operating byte at least the saturated helper-derived limit and
below `ROM8[000082af] = 80`, and the per-bank operating word in
`4 < value < 44`. At least one qualified candidate and a zero
word at `ffff4844 + 2 * bank` return true to the wrapper. On
rejection that shared per-bank timer is reloaded to
`5 * ROM8[000082b3] = 500`. Separate branch timers and latches
preserve event counts and snapshot context.

The exact code binds the listed operands and report gates. The
physical labels for several engine-state operands, decrement cadence
in seconds, and measured fault behavior are unresolved. The
static result establishes which branch the stock configuration selects.

## 1ND0A and 1ND3B

### Acquisition and sensor word publication

| Stage | Bank 1 | Bank 2 |
| --- | --- | --- |
| A/D result | ADDR15 at `fffff826`, read at `00033010` | ADDR3 at `fffff806`, read at `0003300a` |
| A/D output | Caller `SP+4` | Caller `SP+8` |
| Right-aligned unsigned sample | `fffe8d76` at `0002bf78` | `fffe8d78` at `0002bf7a` |
| Live sensor word | `fffe8024` at `00045726` | `fffe8026` at `0004568c` |
| Diagnostic snapshot word | `fffe8018` at `0002128a` | `fffe801a` at `00021290` |

The schedule pointer at `00021ed0` selects acquisition task `0002bd82`.
At `0002bf5e` it calls paired sampler `00032f20` with selectors 3 and 15.
The sampler uses the result-bank bases `fffff800` and `fffff820`, computes
the even register offsets, and stores the two hardware halfwords through
the supplied pointers. The caller shifts each unsigned result right by six.

The schedule pointer at `00021ee4` selects publisher `0004563c`.
It calls `000456e2` with channel zero at `00045648` and inlines the
bank-2 publication. Both paths call gain guard `00094254` and scaler
`000942a0`. If `fffeb8fd & 0x40` is clear, the guard replaces the shared
gain `fffebfa8` outside `0x7900..0x8700` with `0x8000`. These values
come from ROM bytes `00008739..0000873a = 87 79` and word
`00009134 = 8000`, identical in both images. The scaler stores
`min(0xffff, (sample * gain) >> 15)` as a word. Each publisher adds
one to the scaler's halfword when its original sample equals `0x03ff`.
The periodic publisher also copies the two raw samples to
`fffe8a9e/fffe8aa0` at `00045690/00045692`.

The snapshot section of `00021218` copies the live words at
`00021286..00021290`. The range and main circuit branches use the snapshots.
The scheduled high-circuit timer reload uses the live words.

### Transfer curves and combined quantities

Schedule pointer `00021f10` selects `00042f50`. It calls the bank-state
update `0004324c` for both channels and the bank-1 conditioner
`000437a2` with channel zero at `00042f64`. Once each lane's bit in
`fffeae36` is set, the conditioner takes its current live voltage word
minus the correction and floors at zero. With its bit clear each lane
copies the live word and sets the bit. The first-copy stores are
`000437c4` and `00042fca`. Subsequent stores are at
`00043828/0004382e` and `00042fbc/00042fc4`.

The correction uses the unsigned previous conditioned word plus
`ROM16[00009450] = 0x0050` saturated to `0xffff` as denominator.
It uses the unsigned product of `ROM16[0000944a] = 0x014f` and the
lane's 32-bit state `fffeae58/fffeae5c`, shifted right by 16, as
numerator. Both images agree on these constants.

| Stage | Bank 1 | Bank 2 |
| --- | --- | --- |
| Conditioned input word | `fffe8e48`, read `00042fd2` | `fffe8e4a`, read `00042fe6` |
| Interpolation call | `00042fdc -> 00028854` | `00042fee -> 00028854` |
| Curve base | `00015b42` | `00015ac2` |
| Curve output halfword | `fffe804a` at `00042fe4` | `fffe804c` at `00042ffa` |
| Curve cells 0, 1, 63 | `0000, 00e6, f19f` | `0000, 00ec, f17b` |
| SHA-256 of the 128-byte curve | `5ae46b49b876a830f14af95bf677808914d18ef21513ea8dd643ea8224771097` | `0a30fdd80507685b774a603cbe5741363447a2f282bf5737b3ce9a5372a1e539` |

The bank curves contain 64 unsigned 16-bit cells with an implicit step of
256 lookup-coordinate counts. The call argument is
`(conditioned_word & 0x0fff) << 4`. Below `0x3f00`, the kernel at
`00028eb8` selects cells `x >> 8` and `(x >> 8) + 1` and uses
`uint16(x << 8)` as the Q0.16 fraction. It interpolates the unsigned
word cells with truncation of the signed delta magnitude. At and above
`0x3f00` the wrapper returns cell 63 sign-extended, and both callers
publish the low halfword. Each 128-byte curve agrees across 1ND0A and
1ND3B and matches the corresponding stock 1ME3B bank curve byte for byte.

The coordinator copies or filters the curve words into
`fffe8df0/fffe8df2` at `0004310a/0004318c`. When
`fffe9483 & 0x08` is set it blends each previous word and current curve
word with current weight `ROM8[00008650] = 0x1a` on a denominator of
256, correcting a truncated result that would stick at the previous word
by one count toward the current word. When the bit is clear it copies.

Two independent consumers combine the banks:

- At `0004318e/00043192`, the coordinator calls bank-contribution routine
  `00043838`. Its primary branch blends the corresponding unsigned
  `fffe8e10/fffe8e14` longword and filtered curve contribution with
  weights `256 - k` and `k`, where `k = ROM8[000089b9] = 0x80`,
  and clamps the bank longword at `0xffffff`. Its alternate branch
  uses bank-indexed compensation and can return signed contributions.
  At `00043196..000431b2`, the coordinator adds the two bank contribution
  longwords `fffe8df8/fffe8dfc`, signed auxiliary word `fffe8e22`,
  and unsigned shared word `fffe9368`, floors the resulting signed
  longword at zero, and stores `fffe8e30`. The base-fuel schedule
  producer `00044c70` reads `fffe8e30` at `00044cfe`.
- At `000431ba`, the coordinator tail-branches to `00043b12`. This
  routine adds the unsigned bank working words `fffe804e/fffe8050` and
  `fffe9368` to form `S`. The bank working words are written at
  `000430b0/000430c0` from the current curve outputs. Stock
  `ROM8[00008917] = 1` selects the filter formula with denominator one,
  so the pre-offset word is `min(S, 0xffff)`, stored at `00043b8c`
  in `fffe8df4`. The routine publishes
  `max(0, pre_offset - ROM16[0000925c])` at `00043b98` in
  `fffe8052`. The stock offset is zero in both images. The periodic
  publisher at `000456b4..000456d4` scales `fffe8052` by
  `ROM8[000083ba] = 0x69`, shifts right by eight, saturates to
  `0xffff`, and writes the diagnostic word `fffead0a`.

ROM `0000863f` has bit `0x20` clear and `000086ca` is zero in both
images. ROM `00008a2e` is `0x18` on 1ND0A and `0x80` on 1ND3B.
Bit 0 is clear in both, so the path at `00043006..0004300e` writes
zero to the signed auxiliary word in both stock images.

### Periodic admission and circuit thresholds

Schedule slot `00022250` selects `000b6384`. Its call at `000b63b8`
reaches `000bfba0` through `ROM32[000b6608]`. The coordinator admits
the decision branches if `fffeb842 & 0x20` is set. With the master bit
clear, it reloads the circuit and range timers at `000c0144..000c018a`
and returns. With the master bit set, the individual circuit results also
require `fffeb7f3 & 0x10` clear and helper `00027a5c` to return zero.
The helper rejects set bits in mask `0x60` of selected crank/cam
diagnostic status bytes (indices 20, 67 through 72, and 131 through 133).
The per-bank ROM enable inputs are shared with the range entry.

| ROM byte | Stock 1ND0A and 1ND3B | Enabled branches |
| --- | --- | --- |
| `0001af10` | `1c` | `0x04` P0103, `0x08` P0102, `0x10` P0101 |
| `0001aee0` | `07` | `0x01` P010D, `0x02` P010C, `0x04` P010B |
| `00008bf2` | `7e` | `0x20` selects scalar range qualification |

A primary low result needs the corresponding snapshot strictly below
`ROM16[00008dfc] = 0x0050` and `RAM16[fffe80be] >= 0x0020`. The
alternate low paths require `RAM16[fffe80be] >= ROM16[00008fb4] = 0xffff`
and the snapshot strictly below `ROM16[00008dfe] = 0`. The latter
comparison has no qualifying unsigned input. The coordinator ORs each
bank's alternate result with its primary low result. A high result needs
the snapshot at or above `ROM16[00008df4] = 0x03d4`,
`uint8(RAM8[fffe81ad]) <= 0xc0`, and `RAM8[fffeb9f9] == 0`.
The raw limits agree across both images.

| DTC | Word delay | Early byte | Episode mask at `fffeb87f` | Saturating count | Main early marker | Main full report |
| --- | --- | --- | --- | --- | --- | --- |
| P0102 | `fffebbd2` | `fffebafa` | `08` | `fffec79c` | `000bfca2` | `000c0102` |
| P0103 | `fffebbd6` | `fffebafc` | `10` | `fffec79a` | `000bffa6` | `000c00f6` |
| P010C | `fffebbd0` | `fffebafb` | `40` | `fffec79d` | `000bfe32` | `000c0122` |
| P010D | `fffebbd4` | `fffebafd` | `80` | `fffec79b` | `000c008a` | `000c0118` |

Alternate low P0102 uses word `fffebbce`, byte `fffebaf8`, episode
mask `0x04`, count `fffec79e`, and marker call `000bfd48`.
Alternate low P010C uses word `fffebbcc`, byte `fffebaf9`, episode
mask `0x20`, count `fffec79f`, and marker call `000bfee4`.
Circuit failure of the operating checks reloads
the word from `ROM16[00008dd4] = 0x00be` and the byte to `0x1e`.
The periodic decrement loops store at `0002060e/00020632`. Zero in
the early byte admits a call to `000ce048`. Zero in the word admits
the full report. A word below the independent episode threshold
`0x00be - 10 = 0x00b4) allows a count increment once per episode, capped
at `0xff`.

The misfire window wrapper `000b6840`, scheduled at `00021f04`,
tail-jumps at `000b6850` to `000c1aba`. That function independently
reloads the P0103 and P010D timers when the corresponding live word is
strictly below `0x03d4`. The stores are at `000c1ad4/000c1ad6` and
`000c1aea/000c1aec`. Equality preserves the timers.

### P0101 and P010B range/performance

The common bank-indexed function `000c076c` receives zero at
`000bff4c` and one at `000bff52`. Its selectors test bits
`0001af10:0x10` and `0001aee0:0x04`, respectively. Stock
`ROM8[00008bf2] = 0x7e` sets bit `0x20`. The test at `000c07c4`
clears T and the `bf` at `000c07c6` selects scalar qualification
at `000c07cc`. The bank's decision returns in R0 at `000c180c`.

| Scalar candidate | Stock conditions |
| --- | --- |
| Lower snapshot at `000c07d0..000c07fe` | `uint8(fffe81ac) >= 0xa0`, `uint16(fffe80f2 + 2*bank) >= 4 * 0x96`, and snapshot `< ROM16[0000944e] = 0` |
| Upper snapshot at `000c0808..000c0834` | `uint8(fffe81ac) < 0x50`, `uint16(fffe80f2 + 2*bank) < 4 * 0x24`, and snapshot `>= ROM16[0000944c] = 0x01bb` |

The state-byte thresholds come from `00008958` and `0000895b`.
The bank-word thresholds come from `00008a92` and `00008a93`.
All four are common to 1ND0A and 1ND3B. The strict comparison with
zero leaves the lower candidate unreachable. The upper candidate
requires mask `0x60` clear in byte 2 of records 86 and 271 (both
P0605), `fffeb8f8 & 0x20` clear, and the crank/cam guard at
`00027a5c` to return zero. Tests at `000c0836..000c087a` enforce
these conditions. Failure reloads the bank word at
`fffebbdc + 2*bank` to `5 * ROM8[000082be] = 500` at
`000c08ce`. An admitted zero word sets the positive result at
`000c088c`. The periodic word loop at `00020632` decrements the
countdown. The body also keeps the smallest encountered remaining
countdown coordinate as `floor(countdown / 5)` in the bank byte at
`fffec7a0 + bank`.

#### ROM-selectable full model

Clearing `00008bf2:0x20` selects the full model at `000c08d0`.
It computes and compares the quantities below before using its
own qualification predicates. The stock pair takes the scalar route.

The area model applies `00028968` to the 64-word throttle-angle to
opening-area curve at `000149ee` using the 64-word axis at `00016e02`.
The two bank calls at `000c08ec/000c090c` use
`min(0xffff, uint16(RAM16[fffe97a6 + 2*bank]) * 4)`. Another lookup
at `000c0984` uses the unsigned word at `fffea944`. The model uses
the high bytes of the paired 16-word denominator curves at `00016878`
and `00016858`. It looks up `u * 4` below `u = 0x3c00` and
`u - 0x3c00` on the upper branch. The auxiliary three-factor product
at `000c0aa2/000c0ab2/000c0ac8` uses 16 byte cells at `00013da2`
with byte axis `00013db2` and two eight-byte curves at
`0001441e` and `00014204`. The call at `000c0b18` indexes the
16-by-16 word surface at `0000cbc8` using `00013db2` and the
16-word axis `00015fa0`. All ten data or axis spans are identical
across both images.

The model publishes its threshold byte at `fffe82f0 + bank` at
`000c0bc4`. The bank observation builder `000c188c` is called at
`000c0bfc` and stores the observed byte at `fffe85d0 + bank` at
`000c1a56`. The caller compares these as unsigned bytes at
`000c128c`. A strict observed-below-threshold result sets the
low-model candidate. The separate voltage candidate is set for a snapshot
at or above `ROM16[0000944c] = 0x01bb` at `000c129e`.

The observation builder uses `RAM16[fffe89c0]` with a floor of 64
from its caller, the per-bank word at `fffe803a + 2*bank`, the state
byte at `fffe80d4`, and ROM factors `ROM8[00008838] = 3`,
`ROM16[00009106] = 0x68b6`, `ROM8[00008939] = 0x85`, and
`ROM16[0000940a] = 0x9f38`. It bounds the final byte at
`0xff` and handles zero denominators. Adjacent ROM bytes
`0000883b` and `0000893c` differ (1ND0A/1ND3B values
`2c/34` and `ff/00`). The reviewed builder reads offsets
`00008838` and `00008939`, whose values agree.

The full-model admission path at `000c0fac..000c11c4` tests mask `0x60`
in existing record status bytes, clears eligibility when
`fffeb8f8 & 0x20` is set or `00027a5c` returns nonzero, and
bounds the running values below. Both images use the same constants.

| Gate | Stock boundary |
| --- | --- |
| Unsigned word `fffed264` | `>= 0x9200`, immediate at `000c1170` |
| Two signed state deltas | `[-26, 26]` from `00008222..00008223` |
| Signed bank delta against an earlier sample | `[-128, 127]` from `0000822a..0000822b` |
| Signed bank state word at `fffe8428 + 2*bank` | `[-73, 73]` from `00008cca..00008ccd` |
| Signed common state byte at `fffe842c` | `[-128, 127]` from `00008228..00008229` |
| Range low-model timer admission | `fffe81ac >= 0x70` and `uint16(fffe97a6 + 2*bank) >= 127` |
| Range high-side timer admission | Derived lower bound from `fffe81b4`, `fffe81ac < 0x50` and bank word in `[5, 44)` |

At `000c120c` and `000c1288` the model sets or clears each bank's
mask in `fffe82e8` and `fffe82e7` for the respective admissions.
Two bank-indexed auxiliary timers at `fffebbb8` and `fffebbb4` reload
from `ROM16[00008df6] = 500`. The shared per-bank full-report countdown
at `fffebbdc + 2*bank` reloads to `5 * ROM8[000082be] = 500` when
its episode predicate fails. A zero countdown is promoted to a positive
return at `000c13a0` or `000c1684`. The report countdown is decremented
by the periodic word loop at `00020632`.

### Descriptor lookup and report calls

The common dispatcher is `000ba0b8`, loaded from `000c02b4`.
The full call for P0101 is `000c010e` after the coordinator tests the
bank-1 return in R9. The full call for P010B is a tail-jump at `000c0140`
after the test of the bank-2 return in R8. The range function returns
a decision to its caller, and the caller has no separate early-marker
call for either range code. The dispatcher calls marker `000ce048`
at `000ba126`. The marker sets runtime record byte 1 mask `0x80`
and writes report activity at `fffebf4a`.

| DTC | Index | Descriptor and exact bytes | Attribute pointer slot -> word | Runtime record |
| --- | --- | --- | --- | --- |
| P0101 | 176 | `0001c640` `340400000000010100000000` | `0001d044 -> 00017910 = 0670` | `fffed4a8` |
| P010B | 7 | `0001be54` `040200000000010b00000000` | `0001cda0 -> 00017916 = 0670` | `fffed2ad` |
| P0102 | 177 | `0001c64c` `340300000000010200000000` | `0001d048 -> 0001790c = 06f0` | `fffed4ab` |
| P0103 | 178 | `0001c658` `340200000000010300000000` | `0001d04c -> 0001790a = 06f0` | `fffed4ae` |
| P010C | 8 | `0001be60` `040100000000010c00000000` | `0001cda4 -> 00017914 = 06f0` | `fffed2b0` |
| P010D | 9 | `0001be6c` `040000000000010d00000000` | `0001cda8 -> 00017912 = 06f0` | `fffed2b3` |

The descriptor base is `0001be00` with stride 12. The separate attribute
pointer table starts at `0001cd84` with stride four. Runtime records start
at `fffed298` with stride three. The exact attribute words agree across
the images in their differing earlier ROM region.

| Transport | Mode 03 handler and attribute tests | Mode 07 handler and attribute test |
| --- | --- | --- |
| SCI1 | `0003c350`, tests `0003c388/0003c40e` | `0003d3f8`, test `0003d482` |
| CAN | Service record `00026abc`, callback `0012109c`, test `001210ee` | Service record `00026b04`, callback `001219fc`, test `00121aaa` |

Both transports require attribute bit `0x0080`. Qualifying P0101 and
P010B events reach the internal dispatcher. Their stock attributes fail
the Mode 03 and Mode 07 visibility gate. The four circuit attributes permit
visibility when runtime byte 2 also meets the relevant mask
(`0x04` for Mode 03, `0x08` for Mode 07). The additional Mode 07
group test at `0003d464` and `00121a8c` indexes ROM base `0001aedc`
with descriptor byte 0 and uses `1 << descriptor byte 1` as its mask.
The matching masks are set for all six stock descriptors. CAN Mode 07
also checks `ROM8[000089f4] & 0x02`, set in stock `0x2a` on both images.

An initialization call at `000bd810` reaches `000c1a64` through
`ROM32[000bda1c]` and seeds these delays. Additional code includes
report helper `000c01a2` and per-branch
processing beginning at `000c0214`. The scheduled route above reaches
its own embedded decisions. The call provenance of the additional helpers
requires a separate dispatch trace.

### Remaining 1ND inputs

The complete alternate bank-contribution equations, some range-model
working values and the call provenance of the additional report helper
`000c01a2` remain open. The sampled voltage, airflow scale and elapsed
qualification time require physical evidence for the exact ECUs.

## 1ME3B and 1EK7A range decisions

### 1ME3B normalization and classification

The coordinator reads `ROM8[0001afe3] = 0x0f` at `000c9a50`. Mask `0x04` admits the computation. `000c9a58` calls readiness evaluator `000ca6cc`. The coordinator sets bit 4 in `fffeb981` when the evaluator returns 1 and byte 2 of the runtime entries for P0106 and P010A has both `0x60` bits clear (`fffed5f9` and `fffed560`, indices 157 and 106). It clears bit 4 otherwise. It calls `000f2b54` at `000c9a98` and `000ca3b0` at `000c9a9c` and reads the report bits at `000c9aa4`.

The stock snapshot task `00021240` copies the longword from `fffe9684` to `fffe965c` at `00021408` and `0002140a`. The monitor input at `fffe965e` is the low halfword of that copy, sourced from live `fffe9686`. The qualifier `000f2b54` reads unsigned `fffe965e` at `000f2b9a`. It writes the raw float at `fffefabc` (`000f2bb2`) as `(u16(fffe965e) / 256) / D`. `D` is `10.0` below unsigned `fffeb8e8 = 100`, `200.0` above `2000`, and `u16(fffeb8e8) * float32(0x3dcccccc)` within the inclusive range. Here `float32` interprets the literal bits as an IEEE single.

The scheduler copies `fffe962e` to `fffe962c` at `000213d0..000213dc`. `0004c8ea` samples that snapshot, accumulating into `fffeaaac` and storing the scaled window result in `fffeaa5c` (`0004c9a8`). The stock count at `00008fa8` is 2. With the publication flag clear at `fffe9478` mask `0x10`, `0004ca0e` stores the coordinate derived from `u16(fffeaa5c)`. Entry `0004ca1a` receives a halfword in R4 and applies the same publication calculation, then stores at `0004ca6c`. For either input word `A`, the stock result is `min(65535, floor(((10 * A * 28) >> 6) / 255) + 20)`. The factor, divisor and addend come from ROM bytes `000088d9`, `00008c0c` and `000088cc`. A zero ROM divisor selects `0xffff` at `0004c9d4` or `0004ca6c`.

The middle admission timer requires all of the following conditions.

| Input | Test | Evidence |
| --- | --- | --- |
| `fffe97c2` | Byte at least `0x28` | `000f2bae..000f2bb8`, ROM `000086db` |
| `fffed3ba` | Halfword at least `0x9acd` | `000f2bbe..000f2bc4`, ROM `00009156` |
| `fffeb953` | Mask `0x40` qualified by timer threshold 1000 | `000f2bc6..000f2bdc`, ROM `000094ac` |
| `fffeb981` | Coordinator bit 4 set | `000f2be2..000f2bee` |
| `fffe9416` | Unsigned word in inclusive range `0x999a..0xe148`, with absolute change from `fffefac2` at most `0x0ccd` | `000f2bf0..000f2c54`, ROM `0000915a`, `0000915c`, `00009178` |
| `fffe8082` | Byte at least `0x06` | `000f2c56..000f2c5e`, ROM `000086da` |

The timer helper `0002861e` resets on false input and initializes the count to zero on the rising invocation. A positive limit qualifies after that many additional consecutive true invocations. The second and third calls at `000f2c94` and `000f2d06` use limits 50 and 500 (`0000947e`, `00009480`). The second result feeds the third. A rising second result initializes the filtered ratio `fffefad8` from the raw float. Other passes call `0002888c` with `a = 0xb333 * float32(0x377fffff)`, which updates `filtered = a * raw + (1 - a) * previous`. The exposed unsigned word `fffe99ac` at `000f2d02` is zero for negative values, `0xffff` above `float32(0x40a3d666)`, and otherwise the truncated product `12800 * filtered`.

After the third timer qualifies, `000f2b54` latches the high bit `0x80` when the filtered ratio is at least `0x9600 * float32(0x38a3d70a)` (about 3), and the low bit `0x40` when it is at most `0x1900 * float32(0x38a3d70a)` (about 0.5). The words are at `00008e3e` and `00008e40`. Each condition persists while the third timer qualifies, allowing both bits to be set across passes. A false third result clears both bits. The comparison uses the float at `fffefad8` before conversion to `fffe99ac`.

The classifier `000ca3b0` reads the bank 1 and bank 2 published voltage snapshots at `fffe8018` and `fffe801a`. Scheduler `00021240` copies them from `fffe8024` and `fffe8026` at `000212b2` and `000212b8`. The classifier requires mask `0x04` in `ROM8[0001afb8] = 0x07`, mask `0x10` in `ROM8[0001afe8] = 0x1c`, and `abs(u16(fffe8018) - u16(fffe801a)) > ROM8[000086dc] = 60` to attribute the ratio decision. With a single ratio bit and passing discrepancy, high requests P0101 and low requests P010B. The both-bits branch sets both requests when the discrepancy passes. Its fail path clears both requests at `000ca496..000ca4a0`. `000c96fc` then dispatches the asserted result indices.

### 1EK7A measured-to-estimated model

`000ce8ac` publishes a freshly computed estimate at `000ced28` and `000ced2c` and calls `00105ab0` at `000ced2a`. `00105ab0` mirrors selected runtime flags and reads `ROM8[0001ba44] = 0x00` at `00105b70`. The `0x20` and `0x40` tests both fail. The branch at `00105b8c` goes to the existing-state reader at `00105fdc`, leaving the calculation, its dispatch preparation, the qualifier and their timers unexecuted on this stock image.

The configured branch uses `u16(fffe967e)` as its numerator. Snapshot task `00021274` copies it from the low halfword of the `fffe96a8` longword at `00021468..0002146c`, sourced from live `fffe96aa`. The scheduler also copies `fffe96ac` to `fffe9680` at `0002146e..00021472`. Before the monitor call, the MAF coordinator replaces both locations with the same fresh estimate. `000cec74..000ced2c` indexes the unsigned byte lookup at `00014702` through `0002b588` with `u8(fffe8104)`. With `P = lookup_result * u16(fffea7c0)` and `G = u16(fffed9aa)`, the stored estimate is `min(65535, floor(G * P / (128 * 0x9e48)))`. The code splits `P` at bit 8 and reconstructs the quotient and remainder in 32-bit pieces. For any unsigned 32-bit `n`, `(n * 0xcf061d9f) >> 47` equals `floor(n / 0x9e48)`, since `0xcf061d9f * 0x9e48 - 2^47 = 30392` and `(2^32 - 1) * 30392 < 2^47`. The denominator in the monitor comes from the coordinator's fresh store on the observed call path.

The monitor computes two operating coordinates. `N = u16(fffe81b6) >> 1`. The low halfword of the scheduler copy at `0002139a..000213aa` derives from the live engine-speed update word `fffe81ee`, written at `000430d6` in `000430b8`. `L` is `u8(fffe8100)` when mask `0x40` in `ROM8[000086bc]` is clear, otherwise `2 * u8(fffe810a)`. Both actual loads are bytes. `ROM8[000086bc] = 0x0c` selects `fffe8100` for the stock calibration. The selector and coordinate are used for both the admission lookup and the ratio correction map.

`00105ba0` interpolates the load-minimum curve at `00016e94` against axis `00015866` and checks `L` against its result. All 16 stock cells are `0xffff`, above the maximum `L` of 255 or 510 under the two selectors. The admission conjunction also requires the absolute change of `L` from the oldest history word at `ffff08c4` to be at most `0x000d` (`00009278`), `fffe97fa` at least `0x28` (`0000873e`), and `fffed9aa` at least `0x9acd` (`0000927a`). `fffebcdf` mask `0x40` must qualify through limit 1000 (`00009602`). The active inputs at `ffff08b7`, `ffff08c0` and all bytes `fffedede..fffedee7` must be clear. `ffff08ba`, `ffff08bb`, `ffff08bd`, `ffff08be` mirror mask `0x60` of four runtime record status bytes and must also be clear. `fffe944d` mask `0x10` must be set and `fffebe09` mask `0x01` clear. The combined admission test qualifies through limit 50 (`000095c4`) and writes `ffff08bc` at `00105d5e`.

| Configured branch stage | Computation and sites |
| --- | --- |
| Operating-coordinate correction | `00105e06` calls `0002ac48` with the table at `0000ff64`, axis `00015886` for `L`, and axis `00015866` for `N`. The interpolated unsigned word is stored in `fffe9b3c` at `00105e1c`. |
| Ratio | `00105e10` reads `fffe9680`, `00105e26` reads `fffe967e`, and `00105e4a` stores the raw float to `ffff08a4`. The numerator and floored denominator are both multiplied by `1/256` before division. The denominator floor is `0x0a00`. |
| Correction and filtering | `00105e4c..00105e56` adds `map_raw / 256 - 128` to the ratio and writes `ffff08ac`. A rising `ffff08bc` initializes the filtered float `ffff08a8` at `00105f0e`. Other passes call `000293b0` with `a = 0x199a * float32(0x377fffff)`. `00105f4a` publishes the filtered result as `clip(trunc(256 * filtered), 0, 65535)` to `fffe9b38`. |
| Bank comparison inputs | `00047816` copies the transfer outputs to bank words `fffe806e` and `fffe8070` at `000479e4` and `00047a3e`. The low halfword of the `00021324/00021334` longword copy supplies `fffe8056`. The high halfword of the `00021328/00021336` copy supplies `fffe8058`. `001060a0` reads these snapshots at `00106182` and `001061a4` and filters them independently with `a = 0x0148 * float32(0x38000006)`. |
| Bounds and result | `00105f4e` calls `001060a0`. With `ffff08bc` set, the helper tests the filtered ratio against scalar and RPM-indexed upper/lower bounds and invokes `00029142` with limit 500 (`000095c6`) for each comparison. Stock `0000926c` / `0000926e` contain `0xffff` / `0x0000`. The 16-cell curves at `00016e34` / `00016e54` repeat those values and share axis `00015866`. All bounds use `1/256` scaling and inclusive comparisons. |

For each of the scalar and curve pairs, an upper result routes to bank 1 if the filtered bank 1 word is at least bank 2, otherwise bank 2. A lower result reverses the assignment, including the tie case. The qualifier latches its per-direction results until the reset flag at `ffff08b5` is set. The coordinate timer at `00105f80` requires admission and `N >= 0x03c0` for limit 500 and supplies separate state-service flags. An asserted marker or full-result flag inhibits its corresponding state-service flag. Stock reaches the reader of these flags even though the writes from the configured path are skipped.

### Descriptor and report paths

The DTC descriptor is 12 bytes, with the packed P-code at offset 6. The separate attribute pointer array uses 4-byte entries. The table below records the exact descriptor and pointer binding on each image.

| Layout | DTC / index | Descriptor address and bytes | Attribute pointer slot and value | Runtime record | State service, marker, full report |
| --- | --- | --- | --- | --- | --- |
| `1me3b` | P0101 / 177 | `0001c7a4` `340400000000010100000000` | `0001d1c4` -> `000179d4` = `0x0670` | `fffed633` | Bit `0x08` in `fffeb981` -> `000c9c6e` full report |
| `1me3b` | P010B / 7 | `0001bfac` `040200000000010b00000000` | `0001cf1c` -> `000179da` = `0x0670` | `fffed435` | Bit `0x04` in `fffeb981` -> `000c9c8e` full report |
| `1ek7a` | P0101 / 346 | `0001d9d0` `640600000000010100000000` | `0001dfa4` -> `000183dc` = `0x0670` | `fffede1e` | `ffff08d7` -> `00105ff8`, `ffff08da` -> `00106018`, `ffff08db` -> `0010604e` |
| `1ek7a` | P010B / 347 | `0001d9dc` `640500000000010b00000000` | `0001dfa8` -> `000183de` = `0x0670` | `fffede21` | `ffff08d6` -> `00105fe8`, `ffff08d9` -> `00106008`, `ffff08d8` -> `00106028` |

Descriptor roots are `0001bf58` and `0001c998`. Attribute pointer roots are `0001cf00` and `0001da3c`. Runtime records use three-byte strides from `fffed420` and `fffeda10`. Full report targets are `000c38f8` and `000c7990`, with a 1EK7A direct marker at `000deb60` and a separate state service at `00124154`. Attribute `0x0670` has bit 7 clear and excludes the descriptors at the stock Mode 03/07 attribute gate on SCI1 and CAN. The branch from `00105b8c` leaves new range outcomes unavailable from cleared state on stock 1EK7A. The retained-state reader has independent call conditions.

### Remaining SH7059 inputs

The measured numerator snapshots feed the ratio models at
`fffe965e` and `fffe967e`. Their live sources are `fffe9686` and
`fffe96aa`. The physical airflow units of those words and of the 1ME3B
normalization coordinate, the upstream role of `fffe9416`, and the
physical identity of the alternate 1EK7A coordinate remain open. The
[detailed circuit paths](../diagnostics/SH7059.native-monitors.md#maf-circuit-range)
trace the independent low and high voltage results.
