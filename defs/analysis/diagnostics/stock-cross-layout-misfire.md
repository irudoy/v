# Stock misfire registration on 1ND, JK78C, JK00C and JK00D

The stock reporters select local indices 10 through 16. The exact 12-byte
descriptors encode P0306 through P0300 in that order. Descriptor byte 8 is
`0x40` in all seven records. The separate attribute halfword comes from the
pointer at `attribute_table + 4 * index`.

## Exact descriptors and attributes

| Stock ROM | Descriptor base | Attribute pointer base | P0300 / P0301 / P0302 / P0303 / P0304 / P0305 / P0306 attribute addresses | All seven attributes |
| --- | --- | --- | --- | --- |
| 1ND0A | `0001be00` | `0001cd84` | `00017a70 / 00017a64 / 00017a66 / 00017a68 / 00017a6a / 00017a6c / 00017a6e` | `00b0` |
| 1ND3B | `0001be00` | `0001cd84` | `00017a70 / 00017a64 / 00017a66 / 00017a68 / 00017a6a / 00017a6c / 00017a6e` | `00b0` |
| JK78C | `0001b7ac` | `0001c5ec` | `00017436 / 0001742a / 0001742c / 0001742e / 00017430 / 00017432 / 00017434` | `00b0` |
| JK00C | `0001c4e0` | `0001d2b4` | `000185c4 / 000185b8 / 000185ba / 000185bc / 000185be / 000185c0 / 000185c2` | `0030` |
| JK00D | `0001c500` | `0001d2d4` | `000185e4 / 000185d8 / 000185da / 000185dc / 000185de / 000185e0 / 000185e2` | `0030` |

| DTC and index | Exact bytes | 1ND0A | 1ND3B | JK78C | JK00C | JK00D |
| --- | --- | --- | --- | --- | --- | --- |
| P0300, 16 | `06070d000000030040000000` | `0001bec0` | `0001bec0` | `0001b86c` | `0001c5a0` | `0001c5c0` |
| P0301, 15 | `05000d000000030140000000` | `0001beb4` | `0001beb4` | `0001b860` | `0001c594` | `0001c5b4` |
| P0302, 14 | `05010d000000030240000000` | `0001bea8` | `0001bea8` | `0001b854` | `0001c588` | `0001c5a8` |
| P0303, 13 | `05020d000000030340000000` | `0001be9c` | `0001be9c` | `0001b848` | `0001c57c` | `0001c59c` |
| P0304, 12 | `05030d000000030440000000` | `0001be90` | `0001be90` | `0001b83c` | `0001c570` | `0001c590` |
| P0305, 11 | `05040d000000030540000000` | `0001be84` | `0001be84` | `0001b830` | `0001c564` | `0001c584` |
| P0306, 10 | `05050d000000030640000000` | `0001be78` | `0001be78` | `0001b824` | `0001c558` | `0001c578` |

The two 1ND stock ROMs contain identical bytes from `0001bdfc` to the end
of the images. This includes the report code, its literals, the scheduler
slot and the two tables. The seven attribute halfwords and the relevant
group-enable and lane-floor bytes also agree when read separately from each
stock ROM, within the earlier region where the images differ.

## Periodic decisions and cylinder selection

Both layouts test bit `0x80` of a group-enable byte with stock value `0xe0`.
The 1ND schedule word at `00022250` selects `000b6384`. Its indirect call at
`000b63be` reaches `000c1c2c` through `ROM32[000b6610]`. The JK78C diagnostic
task loads `ROM32[0009c4f4] = 000a48fc` at `0009c2ba` and calls it at
`0009c2bc`.

| Stage | 1ND0A and 1ND3B | JK78C |
| --- | --- | --- |
| Group enable and comparison | `ROM8[0001aee2] = e0`, `000c1c4a..000c1c4e` | `ROM8[0001a892] = e0`, `000a4918..000a491c` |
| Decision routine | `000c1c2c` | `000a48fc` |
| Selector entry and decision call sites | `000c41f8` from `000c3074`, `000c33f8`, `000c3658`, `000c3932`, `000c3ba6` | `000a6bf8` from `000a5afc`, `000a6168`, `000a63d8`, `000a65e6` |
| Example six-lane count base | `fffeacba` at `000c343a`, through `fffeacc4` | `ffff3a4a`, passed at `000a5f90` to `000a69cc` |
| Inclusive per-lane floor | `ROM8[000087a7] = 06`, read at `000c3438` | `ROM8[00008738] = 06`, read in the call delay slot at `000a5f92` |
| Result rebuild and two-lane aggregate test | Clears low seven bits at `000c3436`, sets lane masks at `000c3448..000c348e`, sets aggregate at `000c349a` | Clears the reviewed masks at `000a69d8` and `000a69dc`, sets lane masks at `000a69ec..000a6a30`, sets aggregate at `000a6a3c` |

For the reviewed window branch, each of six successive unsigned count words
corresponds to cylinder 1 through 6 in ascending address order. A word at
or above the floor sets its local cylinder bit. Two or more qualifying
lanes set the aggregate bit. Other admitted window and retention paths can
also set the aggregate bit.

The selectors first consider the local aggregate bit and the prior
aggregate runtime status. Either causes P0300 selection. If there is a prior
cylinder result under runtime record byte 2 mask `0x04` and none of the
prior cylinder results matches the current bitmap, they select P0300.
Otherwise, the first present local bit in cylinder order 6, 5, 4, 3, 2, 1
selects the cylinder-specific record. The argument splits into group
`argument >> 1` and selector parity `argument & 1` for retained snapshots.
The argument itself is independent of the cylinder number.

| DTC | 1ND local mask at `fffeb888` and transfer | JK78C local mask and index load |
| --- | --- | --- |
| P0300 | `0x01`, call `000c4412` | `ffff4566 & 0x40`, calls `000a6f10` and `000a6f20` |
| P0301 | `0x40`, tail jump `000c440c` | `ffff4565 & 0x10`, index load `000a6f04` |
| P0302 | `0x20`, tail jump `000c43fc` | `ffff4565 & 0x08`, index load `000a6efc` |
| P0303 | `0x10`, tail jump `000c43ec` | `ffff4565 & 0x04`, index load `000a6ef2` |
| P0304 | `0x08`, tail jump `000c43dc` | `ffff4565 & 0x02`, index load `000a6ee8` |
| P0305 | `0x04`, tail jump `000c43cc` | `ffff4565 & 0x01`, index load `000a6ede` |
| P0306 | `0x02`, tail jump `000c43bc` | `ffff4566 & 0x80`, index load `000a6ed0` |

The six JK78C cylinder branches join at `000a6f06`. The 1ND target resolves
via `ROM32[000c4450] = 000ba0b8`. The JK78C target resolves via
`ROM32[000a6f8c] = 0009dfa8`.

## Common registration

The 1ND dispatcher invokes the marker `000ce048` at `000ba126`. The marker
sets bit 7 of byte 1 at `fffed298 + 3 * index`, writes the activity byte
`fffebf4a` at `000ce0c6`, and reads the attribute pointer at `000ce0ca`.
The dispatcher calculates `12 * index`, checks descriptor byte 8 at
`000ba144..000ba148`, and takes the bit-6 path for every P030x record. The
store at `000ba166` sets low bits `0x03` of runtime record byte 2.

JK78C calculates the same descriptor stride and tests byte 8 at
`0009e036..0009e042`. Its bit-6 path calls `0009e5ae` at `0009e044` with the
original local index. This helper sets low bits `0x03` of byte 2 at
`ffff5e94 + 3 * index` through stores `0009e5d0` and `0009e5da`. The
dispatcher also uses the attribute pointer table at `0009e0e6` on its other
record path.

## 1ND scheduled count production

Both 1ND images select the window wrapper `000b6840` through
`ROM32[00021f04]`. The wrapper calls preparation `00046560` at `000b6844`,
calls production `000c51c0` at `000b684a`, and tail-jumps to the MAF
high-circuit delay reload `000c1aba` at `000b6850`. The reload uses
the stock upper limit `0x03d4` at `00008df4` and the word reload `0x00be`
at `00008dd4`. Its input words are `fffe8024` and `fffe8026`.

Event preparation publishes `ffff8038.bit7` at `00046596` and shifts or
fills the interval history at `fffe8dac`. The count producer checks the
group configuration and pending bit before clearing the pending bit at
`000c51fa`. After the history count reaches 13, the producer calls the
refresh routine `000c6914` at `000c5230`. The direct path copies history
slots 3, 8 and 9 from `fffe8db8`, `fffe8dcc` and `fffe8dd0` into
`fffeabc0`, `fffeabc4` and `fffeabc8` at `000c6b22`, `000c6b24` and
`000c6b26`. The producer combines the refreshed words as
`(T1 - T0) + 5 * (T1 - T2)` at `000c527a..000c5292`.

The corrected path uses the [same Q15 cylinder cases](SH7059.misfire.md#corrected-timing-words).
The stock correction switch at `000087a5` sets bit 7. Admission requires
the ready bit `fffeb8af.bit7`, a clear inhibit `fffeb8e2.bit5`, a set
local qualifier `fffeb865.bit7`, and correction age `fffece8c >= 20`.
The refresh checks all five halfwords at `fffece96` against the inclusive
limits `0x7eb5..0x8148` at `000092e4..000092e7`. It records correction
selection in `fffeb8ae.bit2`.

| Bank | Base | Aggregate / cylinder store | Decision reader or qualifier |
| --- | --- | --- | --- |
| Primary | `fffeacb8` | `000c6184` / `000c618e` | `000c30f2` |
| Companion | `fffeacaa` | `000c6178` / `000c6194` | `000c2df0` |
| Saturating | `fffeac9c` | `000c61aa` / `000c61b8`, `000c62de` / `000c62ec`, `000c6422` / `000c6430` | `000c3c68` |
| Repeated-history | `fffeac80` | `000c62be` / `000c62c8` | `000c36d0` |
| Alternate-history | `fffeac8e` | `000c6402` / `000c640c` | `000c412e`, read at `000c413e` |

Each bank contains the aggregate word and six cylinder words. The
repeated-history path requires bit 12 and at least four set bits in
bits 0 through 11 at `000c6248..000c6278`. The saturating bank uses
`fffeb8af.bit2` to limit updates across the three producer paths and
saturates the selected words at `0xffff`. The decision clears this bank
at `000c1ef8`. It also clears the four other banks at `000c1d3a..000c1d40`.
The alternate qualifier uses stock pair and residual factors `0xe6`
and `0x1a` from `00008a33..00008a34` after testing the aggregate against
the caller's unsigned floor.

## JK00C and JK00D comparison

Both stock ROMs contain the selector at `000893f6` with identical selector
instructions across `[000895c8, 00089716)`. The local result byte is
`ffff43a2` on JK00C and `ffff43b6` on JK00D. The bit assignments are
`0x01` for the aggregate and `0x02` through `0x40` in cylinder order 6
through 1. Both use the shared cylinder call `000896f8` and aggregate calls
`00089702` and `00089712`. The target `ROM32[00089774] = 000808e0` is the DTC
dispatcher. Its descriptor base literal at `00080b2c` distinguishes the two
catalogs. The bit-6 class branch calls `00080c5a` at `00080922` in both
images. These sites establish registration correspondence for P030x.

## JK00C and JK00D count production

### Scheduled decision and report path

In both stock images, the scheduler table word `ROM32[00021b8c]` is
`0007ee9c`. The diagnostic task loads `ROM32[0007f110] = 000871ac`
at `0007eed8` and calls it at `0007eeda` with a NOP delay slot.

| Instruction or data | JK00C | JK00D |
| --- | --- | --- |
| Decision entry | `000871ac` | `000871ac` |
| Decision control base, loaded at `000871c0` | `ffff431c` | `ffff4330` |
| Group configuration byte read and tested at `000871c8..000871cc` | `ROM8[0001b63e] = 80` | `ROM8[0001b65e] = 80` |
| Bitmap builder entry | `000891da` | `000891da` |
| Bitmap builder GBR literal, `ROM32[00089290]` | `ffff4346` | `ffff435a` |
| Bitmap, `GBR + 0x5c` | `ffff43a2` | `ffff43b6` |
| Report selector | `000893f6` | `000893f6` |

Stock group configuration sets mask `0x80`. The branch at `000871cc`
takes the path that skips the early exit at `000871d0` to `00088f02`.

The three calls to the bitmap builder use stock byte floors of 6. At
`0008833e`, `r5 = ROM32[000884e4] + (0x4c << 2)` and the delay slot
loads the floor into `r4`. At `00088760` and `000887e0`, `r5` is the
same base plus `0x13e` and the second floor address supplies `r4`.

| Builder call and floor-load delay slot | Floor on JK00C | Floor on JK00D |
| --- | --- | --- |
| `0008833e`, `00088340` | `ROM8[00008880] = 06` | `ROM8[00008881] = 06` |
| `00088760`, `00088762` | `ROM8[00008881] = 06` | `ROM8[00008882] = 06` |
| `000887e0`, `000887e2` | `ROM8[00008881] = 06` | `ROM8[00008882] = 06` |

| Window | JK00C aggregate and six lane words | JK00D aggregate and six lane words |
| --- | --- | --- |
| First call | `ffff3912`, `ffff3914..ffff391e` | `ffff3926`, `ffff3928..ffff3932` |
| Second and third calls | `ffff3920`, `ffff3922..ffff392c` | `ffff3934`, `ffff3936..ffff3940` |

The following call at `00088344` loads the selector from
`ROM32[000884ec]` and passes the stage argument from `r12` in the delay
slot. The second builder call branches to the selector call at
`000889d0` and passes the stage argument from `r9`.

### Scheduled count producer

Both images schedule `0007f2ec` through `ROM32[00021898]`. The wrapper
calls event preparation `0003dcd0` at `0007f2f0` and count producer
`0008a1a4` at `0007f2f6` through literals `0007f300` and `0007f304`.
Event preparation tests bit `0x80` in `ffff84f2` at `0003dce8..0003dcec`,
clears it at `0003dcfa`, and sets bit `0x80` in `ffff84f8` at
`0003dcfc..0003dd02`. The producer's group enable is the same stock
byte as the decision's. The producer requires the `ffff84f8` bit and
clears it at `0008a1c4..0008a1d4`.

At `0008a1da..0008a1e0`, the producer requires at least 13 in the
history count for the refresh branch. The count is `ffff394c` on JK00C
and `ffff3960` on JK00D. Event preparation shifts the timing history at
`0003dd16..0003dd2c` and increments that count with saturation at 255
at `0003dd2e..0003dd46`. The shorter history path retains `0x80` as the
initial value for the producer's deviation history.

After refreshing timing inputs, `0008a21c..0008a23e` supplies
`(T1 - T0) + 5 * (T1 - T2)` to `0008b6d0`. The three longwords
`T0`, `T1`, `T2` are `ffff382c`, `ffff3830`, `ffff3834` on JK00C and
`ffff3840`, `ffff3844`, `ffff3848` on JK00D. The formula is on raw timing
values. `0008a9f6..0008aa82` shifts the event history, may set its low bit,
and clears the history when its outer admission fails.

| Count path operation | Instruction | JK00C | JK00D |
| --- | --- | --- | --- |
| Test `0x1000` in the updated 16-bit event history | `0008ac88..0008ac92` | `ffff3806` | `ffff381a` |
| Require both low bits of the count-admission byte | `0008acae..0008acb6` | `ffff4371` | `ffff4385` |
| Increment second aggregate and first aggregate | `0008acc4`, `0008acca` | `ffff3920`, `ffff3912` | `ffff3934`, `ffff3926` |
| Read and scale the unsigned cylinder index | `0008accc..0008acd0` | `ffff4194` | `ffff41a8` |
| Increment the selected second and first cylinder words | `0008acd8`, `0008acde` | second and first aggregate bases plus `2 * index` | second and first aggregate bases plus `2 * index` |

Each increment stores a 16-bit result. The producer zeroes both seven-word
banks at `0008a6d2/0008a6d4`, at `0008abda/0008abdc`, and at
`0008ad28/0008ad2a`. It also has individual reset loops at `0008ac4e`
and `0008ac62`. The decision routine's reset loops write the same banks
at `00087312/00087316` and `00087716/00087718`.

### Capture and direct timing inputs

Both layouts use the same capture-to-history path for the direct timing
inputs. The end path reads `ICR0A` at `0002ae94`, subtracts the saved
start at `ffff84d4`, and publishes the interval magnitude at
`0002aea6`. The start path reads `ICR0A` at `0002aec8` and stores it at
`0002aecc`. Both stock start and end tooth bytes are 9. Event preparation
`0003dcd0` consumes `ffff84f2.bit7`, sets `ffff84f8.bit7`, and shifts or
fills the interval history. The direct path in refresh routine `0008b308`
copies the same slots `3`, `8`, and `9` at `0008b4ca`, `0008b4d0`,
and `0008b4d6`.

| Evidence | JK00C | JK00D |
|---|---|---|
| End and start ROM teeth | `00008c0c`, `00008c0d` | `00008c0d`, `00008c0e` |
| Interval history base | `ffff1e1c` | `ffff1e24` |
| Slot 3 -> `T0` | `ffff1e28` -> `ffff382c` | `ffff1e30` -> `ffff3840` |
| Slot 8 -> `T1` | `ffff1e3c` -> `ffff3830` | `ffff1e44` -> `ffff3844` |
| Slot 9 -> `T2` | `ffff1e40` -> `ffff3834` | `ffff1e48` -> `ffff3848` |

### Corrected timing inputs

The common refresh entry `0008b308` applies the same five-factor bounds,
the same three cylinder cases, and the same direct and out-of-range
outcomes. Its helper `0008b4e2` implements the same split-half Q15
arithmetic. The JK00 refresh uses bit 1 of the output byte and bit 6 of
the following byte for the ready latch.

| Gate or state | JK00C | JK00D |
|---|---|---|
| ROM enable bit 7 set | `ROM8[0000887f] = 0x80` | `ROM8[00008880] = 0x80` |
| Ready latch bit 6 set | `ffff43bd` | `ffff43d1` |
| Inhibit bit 7 clear | `ffff43e7` | `ffff43fb` |
| Factor base, inclusive range `0x7eb5..0x8148` | `ffff560a` | `ffff561e` |
| Local admission bit 4 set | `ffff4385` | `ffff4399` |
| Age and floor | `ffff5600`, `ROM8[00008810] = 0x14` | `ffff5614`, `ROM8[00008811] = 0x14` |
| Output bit 1 | `ffff43bc` | `ffff43d0` |

### Window count banks

The five banks have the same aggregate-plus-six-word layout on both JK00
images. The paired stores are `0008acc4`, `0008acca`, `0008acd8`, and
`0008acde`. The repeated-history branch tests bit 12 and at least four
prior history hits at `0008ad84..0008adb2`. The two later indexed
increment blocks store at `0008ade8` and `0008adf6`, and at `0008af12`
and `0008af20`. The saturating bank can receive increments from the three history paths. The common reset at `0008a6d0..0008a6e2` clears four
banks; the saturating bank is outside that loop.

| Role | JK00C base | JK00D base |
|---|---|---|
| Primary, runtime threshold path | `ffff3920` | `ffff3934` |
| Companion, shifted accumulator path | `ffff3912` | `ffff3926` |
| Saturating | `ffff3904` | `ffff3918` |
| Repeated-history | `ffff38e8` | `ffff38fc` |
| Alternate-history | `ffff38f6` | `ffff390a` |

The producer caps saturating aggregate and cylinder counts at `0xffff`.
It tests and sets the shared bit `0x04` in `ffff43bd` or `ffff43d1`.
The first path sets it at `0008ad10`, and the producer clears it at
`0008af8e`. The decision resets the seven words at `0008750a`. A separate
decision path at `00088ede..00088efa` snapshots the same seven words to
`ffff5924` on JK00C or `ffff5938` on JK00D.

The repeated-history qualifier `000892be` first requires the aggregate
`A` to meet the caller floor. It rejects a cylinder whose count lies in
`[(13 * A) >> 8, (64 * A) >> 8)`. The stock coefficients are `40 0d`
at `00008aeb` on JK00C and `00008aec` on JK00D. The alternate qualifier
`0008932e` tests the aggregate floor, then the sum for pairs `(1, 4)`,
`(2, 5)` and `(3, 6)` against `(230 * A) >> 8`. For a qualifying pair,
the sum of the other four cylinder counts must be below `(26 * A) >> 8`.
The stock coefficients `e6 1a` are at `00008b7d` or `00008b7e`.
The decision calls the repeated-history qualifier at `00088ae2`. It
calls the alternate qualifier at `00088aea` if the first returns zero.

### Decision readiness and aggregate thresholds

The early readiness branch evaluates the following conditions before
publishing its ready bit `0x10`. The following mode test at
`0008763e..0008764a` sets bit `0x20` because the stock mode byte is
`0x28` at `00008b2d` on JK00C and `00008b2e` on JK00D. The decision's
reset loop at `00087716/00087718` runs when bit `0x20` is clear.

| Predicate | Instruction | JK00C | JK00D |
| --- | --- | --- | --- |
| Latch is zero | `0008757c..00087580` | `ffff4520` | `ffff4534` |
| Operating bit `0x40` is set | `00087586..0008758a` | `ffff4367` | `ffff437b` |
| Composite helper and record predicates return zero | `00087592..000875f2` | `0002652a` and `000264fc` for `0x127`, `0x128`, `0`, `0x12e`, `0x14`, `-1` | same |
| Battery-voltage snapshot is at least `0x89` | `000875f8..00087606` | `ffff1113` | same |
| Readiness history counter is at least 1 | `0008760e..00087616` | `ffff41ee`, `ROM8[000083bc] = 01` | `ffff4202`, same ROM byte |
| Operating input is `0x06 <= value < 0x98` | `00087620..00087634` | `ffff11bb`, `ROM8[00008903..00008904] = 06 98` | `ffff11bb`, `ROM8[00008904..00008905] = 06 98` |
| Ready state bits `0x10` and `0x20` | `00087636..000876ba` | `ffff43f9` | `ffff440d` |

The first decision path uses a strict aggregate comparison at
`00088110..0008811a`. Its first-window count must exceed the 32-bit
accumulator shifted right by 8. The accumulator is `ffff37f4` on JK00C
and `ffff3808` on JK00D. The producer updates it at `0008a964` by adding
an indexed, zero-extended ROM byte. The second decision path compares
its second-window aggregate to a runtime threshold word at
`000883fa..0008840c`, and uses an inclusive comparison. The threshold
word is `ffff2c38` on JK00C and `ffff2c4c` on JK00D. Once that comparison
passes, `00088458..0008848a` computes and stores a byte from
`100 * maximum_cylinder_count / aggregate_count`.

### Bitmap instructions

The two images have identical instructions for `000891da..00089248`.
The builder zero-extends the caller's byte at `000891e4`, clears the low
seven bitmap bits at `000891e6`, then compares the six zero-extended
16-bit counts with the floor. Each comparison is inclusive.

| Cylinder | Read | Compare | Result write | Mask |
| --- | --- | --- | --- | --- |
| 1 | `000891e8` | `000891ec` | `000891f2` | `0x40` |
| 2 | `000891f6` | `000891fa` | `00089202` | `0x20` |
| 3 | `00089204` | `00089208` | `00089210` | `0x10` |
| 4 | `00089212` | `00089216` | `0008921e` | `0x08` |
| 5 | `00089220` | `00089224` | `0008922c` | `0x04` |
| 6 | `0008922e` | `00089232` | `0008923a` | `0x02` |

`0008923c..00089244` sets aggregate mask `0x01` when at least two lanes
qualify. The selector can also receive an aggregate bit set by its caller
in the delay slots of `00088bf6` and `00088e02`.

## Open evidence

The physical cylinder attribution of the upstream crank events, the full
set of admission and reset paths, and vehicle monitor completion retain
separate evidence requirements. The upstream owner of the JK00C and JK00D
cylinder index and the physical scale of the timing words remain open.
