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

### 1ND Q15 estimator and admission

The 1ND0A and 1ND3B stock images share the estimator and its scheduler
sites. The window wrapper selected by `ROM32[00021f04]` calls
`000c51c0`. At history count 13 and above, the producer calls the ratio
collector `000c6560`, factor updater `000c6764`, and refresh `000c6914`
at `000c5224`, `000c522a`, and `000c5230`, respectively.

The ICI0A vector at `00020154` selects `0002c948`. The handler
publishes the newest interval in `fffe8dac` at `0002dc42` and the
mapped attribution byte in `fffeb634` at `0002dc4c`. The collector
reads the interval-history endpoints `B[1]` and `B[7]` at `000c660c`
and `000c660e` and the attribution byte at `000c6618`. It discards
the partial cohort if unsigned `B[1] < B[7]`. Otherwise it
accumulates only for cylinder attribution 6.

| Collector admission | Exact 1ND predicate |
|---|---|
| Operating gate and fuel mask | `fffe947b.bit6` set and `fffe92e4 == 0x3f` |
| Decision readiness and correction control | `fffeb8fa.bit5` set and `fffeb8e2.bit5` clear |
| Delay and input difference | `fffebb22 == 0` and `fffeb843.bit4` set |
| Operating input and local inhibit | `fffe81e0 < ROM8[00008826] = 0x50` and `fffeb854.bit6` clear |

The [shared estimator arithmetic](SH7059.misfire.md#estimating-the-five-timing-correction-factors)
uses `d = trunc_toward_zero(int32(B[7] - B[1]) / 6)`. For index
`j = 0..4`, it forms `R = uint32(B[1] + (5-j) * d)` and
`X = B[6-j]`, right shifts both words together until `R <= 0x1ffff`,
and stages the low 16 bits of the unsigned quotient `(R << 15) / X`.
The collector adds the halfwords to five 32-bit sums and publishes the
new cohort count. It clears the sums and count on rejected operating gates
or reverse endpoint order. It starts a new cohort when the old count
reaches the stock length of 8.

| State and operation | Address and instruction |
|---|---|
| Raw ratio halfwords | `fffeac68`, store `000c6686` |
| Five longword sums | `fffead18`, sum loop `000c66a0` |
| Cohort count | `fffeab8d`, publish `000c66d4` |
| Mean halfwords | `fffeacda`, loop `000c67c4`, stores `000c67cc`, `000c67d4`, `000c67ea` |
| Factor table and age | `fffece96` and `fffece8c`, blend `000c68d0`, factor store `000c68e6`, age store `000c6900` |
| Correction-ready latch | `fffeb8af.bit7`, set at `000c67ba` and cleared at `000c692c` when `ffff8031.bit7` is clear |

The updater requires `N >= ROM8[00008732] = 8`, sets the ready latch,
and stages `mean[j] = uint16(sum[j] / N)`. A zero
correction age admits a direct five-word copy. Later cohorts use three
averages with the old factor, yielding
`floor((mean[j] + 7 * old_Q[j]) / 8)`. Stock
`ROM8[0000872b] = 5` and `ROM16[00008f3c] = 33` select the point
at which a single absolute difference of at least 33 resets all five
factors to `0x8000` and clears age. The explicit request
`fffeb8e2.bit4` also resets all five factors and age, and the updater
clears the request at `000c6780`. Completed updates increment age up
to 255.

### Sources of the 1ND gates

The injector arbitration function `000760cc` stores the final
six-channel mask at `000766f0`. The collector requires the entire
byte to equal `0x3f`.

The status publisher `0009e8ec`, called from `0009e0ec` at
`0009e1d0`, writes `fffe947b.bit6` at `0009ea22`. It sets the
bit when either of these branches succeeds:

- At least one of `fffe9473.bit6` and `fffe94e9.bit3` is set and
  the call to `000ce212` returns nonzero.
- The raw status selection at `0009e9d4..0009ea04` selects a set bit.
  It selects `fffeb7ee.bit2` when `fffeb8eb.bit7`, `fffeb8f1.bit1`,
  and `fffeb8cc.bit5` are clear and both `fffe95cb` and `fffe95f8`
  are zero. Otherwise it selects `fffeb8cc.bit4`.

The helper `000ce212` requires `fffeb7f3.bit4` clear and
`fffe9471.bit4` set. It then returns one if `fffeb818.bit0` is clear,
`fffeb836.bit1` is set, or either unsigned word at `fffea918` and
`fffea91a` reaches 20.

The periodic decision at `000c1c2c` publishes `fffeb8fa.bit5` at
`000c213a`. Stock `ROM8[000089f4] = 0x2a` sets the enable mask
`0x08`, so the admitted branch at `000c2118` sets bit 5. The
nearby rejection branches clear bits 4 and 5. The admitted branch
requires, among its readiness conditions, sample count
`fffeb686 >= 1` and `0x06 <= fffe81a8 < 0x5a`.

With `ffff8023.bit7` set, the decision sets `fffeb843.bit4` at
`000c224c` when `uint8(fffe81ae) - uint8(fffe81ad) <= 8`, using
`ROM8[00008436]`. It clears the bit at `000c224e` when the
difference exceeds 8. The window producer asserts the separate
`fffeb854.bit6` inhibit at `000c5a30` and clears it on the other
branch at `000c5a0a`. The collector clears the same bit on its
cohort restart and rejected-gate reset paths.

The control routine `000c6ec8` is called at `000b68fa` from
`000b68f0`, selected by `ROM32[00022048]`. It writes the explicit
reset request at `000c6f96` or `000c70ca`. On the
`ffff803a.bit7` and `ffff8031.bit7` admitted path:

- At age 20 or above, the first request path requires
  `(fffed706 & 0xc0) == 0xc0` and `fffeb8e1.bit0` set.
- Below age 20 with the inhibit clear, it remembers the selector at
  `fffeb66d` in `fffecfd0`. With the first value already recorded,
  a first change records a second value in `fffecfd1` and requests
  reset if the absolute signed-byte difference is at least 2. A
  later selector that matches neither remembered value also requests
  reset.

The same routine can assert the inhibit at `000c7008` when the
selector differs from stock `ROM8[00008227] = 0x18` by at least 2
or when age is at least 20 and the selector matches neither remembered
value. The release branch reaches `000c70a2` after its stock hold
count of 250. It requests reset at `000c70ca` if the retry count
reaches 2 or the correction age is below 20.
The periodic decision also clears the inhibit and request bits in its
reset paths at `000c1de2` and `000c1ebe`.

The estimator and its refresh dependencies are visible in the 1ND
registration chain. The typed writer links retain the readiness, reset,
and inhibit publishers across the separate scheduled paths. Live
gate combinations and the physical interpretation of the raw selector
remain open.

## JK78C event, timing, and count production

Stock schedule word `ROM32[00021900] = 0009c6b8` selects the producer wrapper.
It calls event preparation `00041c24` at `0009c6bc`, calls count production
`000a79c4` at `0009c6c2`, then tail-jumps to delay reload `000a47c2` at
`0009c6c8`. The diagnostic schedule is independent. `ROM32[00021c38]`
selects `0009c284`, which calls decision `000a48fc` at `0009c2bc`.

### Capture and history

`0002b8fa` uses the nonzero event index at `ffff11c8` and compares the tooth
at `ffff13a8` with the end byte `ROM8[000089cc] = 9`. With the prior-start
bit `ffff84f9.bit7` set, it takes the magnitude of the 32-bit capture at
`fffff434` minus `ffff84dc`. It stores the interval to `ffff1d24` at
`0002cde6`, stores the attribution byte `ROM8[000226c4 + event]` to
`ffff4348` at `0002cdf0`, and sets `ffff84fa.bit7` at `0002cdf8`. The
attribution table starts `00 04 05 06 01 02 03`. The start byte at
`000089ce` is also 9. The later branch at `0002ce04..0002ce14` saves the
current capture at `ffff84dc` and sets `ffff84f9.bit7`.

The preparation routine clears `ffff84fa.bit7` and sets `ffff8500.bit7`
at `00041c44` and `00041c4e`. If `ffff439a` reaches stock floor 1 and
the previous-start bit is set, it shifts slots 0..12 of the 14-longword
interval history at `ffff1d24` into slots 1..13 at `00041c68..00041c78`.
It increments `ffff3a74` with saturation at `0xff`. Two other saturating
ages, `ffff3a75` and `ffff3a76`, follow watcher masks `ffff44e0 & 0x40`
and `ffff45be & 0x10`, respectively. Invalid preparation fills slots 1..13
with the newest interval and clears all three ages at `00041cea..00041cf2`.

Production requires `ROM8[0001a892] & 0x80` and `ffff8500.bit7`. Stock
group byte `0xe0` permits the group. The producer clears the pending bit at
`000a79f4`. Starting at history age 13, calls `000a7a02`, `000a7a08`, and
`000a7a0e` run factor collection `000a8816`, factor update `000a8a32`, and
timing refresh `000a8b72`. The refresh copies slots 3, 8, and 9 to
`ffff3950`, `ffff3954`, and `ffff3958` on its direct path. The producer
forms `(T1 - T0) + 5 * (T1 - T2)` at `000a7a3c..000a7a56`. It maintains
offset-binary deviation streams at `ffff3a58`, `ffff3a5e`, and `ffff3a64`
and seeds a stream with `0x80` while the history is too short. The other
two expressions use history slots `(7, 10, 4)` and `(7, 13, 1)` with
weights `(6, -3, -3)`.

On an admitted cylinder-six sample, the collector generates five ratio
halfwords at `ffff39f8`, adds them to the five longword sums at `ffff3aa8`,
and advances the cohort byte at `ffff3921`. The updater requires the stock
cohort minimum of eight. It raises factor readiness, publishes means
directly at correction age zero, and blends later cohorts with the previous
factors. Inconsistent mature factors reset the age and restore unity.

The stock correction switch `ROM8[00008736] = 0x80` permits the corrected
path. It requires `ffff4584.bit7`, clear `ffff45b4.bit5`, `ffff4548.bit6`,
and `ffff5a90 >= 20`. All five factors at `ffff5a9a` must be in the
inclusive ROM range `0x7eb5..0x8148`. Helper `000a8d4c` applies the
unsigned Q15 factor for the cylinder cases. The refresh sets
`ffff4583.bit2` on correction selection. An out-of-range cylinder within
the selected path retains the previous words. The direct path clears
the selection bit and writes all three words at `000a8d34/3a/40`.

### Banks, resets, and consumers

The producer reads the attribution byte from `ffff4348`, doubles it, and
uses that offset from each aggregate base. A bank contains the aggregate
and six cylinder halfwords. Both bits `0xc0` of `ffff4533` must be set for
the reviewed increments.

| Bank and aggregate | Aggregate / lane increment | Decision consumer | Producer / decision reset stores |
| --- | --- | --- | --- |
| Primary `ffff3a48` | `000a8514 / 000a8528` | `000a5baa`, `000a61bc`, lane base `ffff3a4a` at `000a5f0c/8c` | `000a7ef6`, `000a8420`, `000a84aa`, `000a8578` / `000a4a62`, `000a4e96` |
| Companion `ffff3a3a` | `000a851a / 000a852e` | `000a58e4`, `000a5b4a`, lane base `ffff3a3c` at `000a5af2` | `000a7ef4`, `000a841e`, `000a8496`, `000a857a` / `000a4a5e`, `000a4e94` |
| Saturating `ffff3a2c` | `000a8548/5a`, `000a8676/8c`, `000a87aa/c0` | `000a66d4` | Decision `000a4c60` |
| Repeated history `ffff3a10` | `000a864a / 000a8658` | `000a6ac0` reads aggregate at `000a6ad0` and lanes at `000a6afe` | `000a7efa`, `000a85b6`, `000a85da`, `000a869c`, `000a86e4` / `000a4a46`, `000a4e9a` |
| Alternate history `ffff3a1e` | `000a8780 / 000a878e` | `000a6b30` reads aggregate at `000a6b48` and pairs the lanes | `000a7efe`, `000a8714`, `000a8734`, `000a87e8` / `000a4a5a`, `000a4e9e` |

The primary and companion use bit 12 of history `ffff392a`. The repeated
bank requires bit 12 of `ffff3926` and four or more set bits in its lower
12 positions. The alternate bank uses bit 12 of `ffff3928`. Each admitted
branch calls `000a8d6e` before setting `ffff4584.bit2`, so the shared event
word `ffff5a98` saturates and increments at most once per pass. The
saturating bank uses `ffff4584.bit3` and clips both increments at
`0xffff`. The producer clears bit 2 at `000a8404` and bit 3 at `000a87fc`.
Decision bit `ffff454d.bit0` requests a companion reset. Bit 1 requests
the repeated and alternate resets. `ffff454e.bit7` requests a primary reset
and clears its auxiliary bins. The producer consumes these requests at
`000a858a`, `000a8594`, and `000a87f6`.

The primary branch also calls `000a8d90`, which maintains six saturating
byte bins `ffff3bac..ffff3bb1` split by two input ranges and three bands.
It also updates `ffff5a8e` and `ffff3920` under its secondary gate. The
repeated and alternate paths separately increment the joint history word
`ffff3a0e` at `000a8642` and `000a8778`. Weighted accumulators at
`ffff3918` and `ffff391c` add table entries on their admitted branches and
clear on the shared admission failure at `000a8206/08`.

The repeated qualifier admits the caller floor with no lane in the middle
share band, using stock factors `0x0d` and `0x40`. The alternate qualifier
uses factors `0xe6` and `0x1a` for pair and residual floors. The decision's
three calls to `000a69cc` use the six companion words once and the six
primary words twice, all with stock floor 6. The builder sets cylinder bits
in `ffff4565/66` and sets the aggregate bit when two lanes qualify. The
decision also calls `000a689a` at `000a5e4c` and `000a6026`. That helper
checks primary aggregate below stock floor `0x0011` and current flags before
updating the retained state and seven runtime record byte-2 masks. The
decision passes admitted stages to `000a6bf8` for P0300..P0306 selection.

JK00C/D preserve the event handshake, history slots, and primary/companion
pair, with different addresses. The wider five-bank split matches the 1ND
count paths. The JK78C producer also retains the offset-binary deviation
streams and the distinct two-byte result bitmap at `ffff4565/66`.

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

### Cylinder attribution at crank capture

Application vector 84 at `00020154` selects the ICI0A handler
`00029b2a` on both images. The end-of-interval path reads the event
index at `ffff11ee` and skips capture when it is zero. It requires the
configured end tooth and the armed-start bit `ffff84f1 & 0x80`. After
publishing the interval magnitude, it uses the event index to read
`ROM8[000226e8 + event]` and publishes the resulting cylinder index.
For event indices 1 through 6 the stock table selects cylinders
4, 5, 6, 1, 2, and 3, respectively.

| Operation | Instruction on both images | JK00C | JK00D |
| --- | --- | --- | --- |
| Read event index | `0002ae6e` | `ffff11ee` | `ffff11ee` |
| Read ICR0A and store interval | `0002ae94`, `0002aea6` | `fffff434`, `ffff1e1c` | `fffff434`, `ffff1e24` |
| Load indexed table byte and publish cylinder | `0002aeaa`, `0002aeb0` | `000226e8`, `ffff4194` | `000226e8`, `ffff41a8` |
| Set the capture-ready bit | `0002aeb4..0002aeb8` | `ffff84f2 & 0x80` | `ffff84f2 & 0x80` |

The event preparation consumes the capture-ready bit. The window producer
and timing refresh consume the same cylinder byte. The count producer
uses its unsigned value as the halfword index after the aggregate word,
and the refresh uses it to choose the Q15 factor combination.

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

### Estimating the timing correction factors

The scheduled window producer calls the ratio collector at `0008a1e2`,
factor updater at `0008a1e8`, and refresh at `0008a1ee` after the
capture history reaches 13 entries. Both stock ROMs use the collector
at `0008afa8` and updater at `0008b1c8` with layout-specific RAM literals.

| Collector condition | JK00C | JK00D |
| --- | --- | --- |
| Initial enable and state | `ffff24dd & 0x20` set, `ffff2354 = 0x3f` | `ffff24e5 & 0x20` set, `ffff235c = 0x3f` |
| Secondary enable and inhibit | `ffff43f9 & 0x20` set, `ffff43e7 & 0x80` clear | `ffff440d & 0x20` set, `ffff43fb & 0x80` clear |
| Delay and decision enable | `ffff45fa = 0`, `ffff4368 & 0x20` set | `ffff460e = 0`, `ffff437c & 0x20` set |
| Raw operating byte and local hold flag | `ffff11f7 < 0x50`, `ffff4378 & 0x40` clear | `ffff11f7 < 0x50`, `ffff438c & 0x40` clear |

The periodic decision `000871ac` publishes the secondary enable at
`0008764a`. The stock configuration byte is `0x28` on both images and
sets the selector mask `0x08`. The admitted path requires a sample count
of at least 1, raw snapshot `ffff11bb` in `[0x06, 0x98)` and battery
snapshot `ffff1113 >= 0x89`, along with the preceding fault checks.
It clears the enable at `0008766a` or `000876b6` on rejected paths.
The decision reads the count byte at `ffff41ee` on JK00C and
`ffff4202` on JK00D.

When `ffff84c3 & 0x80` is set, the same decision sets the other
enable bit if `u8(ffff11c2) - u8(ffff11c1) <= 8`, and clears it
otherwise. The stock bound is `ROM8[000084a2]`, and the single
store at `0008781c` writes either result.

The first two rejected tests reload the delay from the stock value
`0x1e` and clear the sums and cohort count. Other rejected operating
tests clear the same cohort without reloading the delay. On an admitted
pass, an old count of 8 or greater clears the cohort before collection.
Collection requires the published cylinder index 6 and
`B[1] >= B[7]`, where `B` is the raw crank interval history. A reversed
endpoint order clears the sums and cohort count.

The collector computes
`d = trunc_toward_zero(int32(B[7] - B[1]) / 6)` using `00021c48`.
For each factor index `j = 0..4`, it sets
`R = uint32(B[1] + (5 - j) * d)` and `X = B[6 - j]`.
It shifts both operands right together until `R <= 0x1ffff`, calls the
unsigned divider `00021d6c` with `R << 15` and `X`, and accumulates the
low halfword of the quotient into the corresponding 32-bit sum. The
cohort count increments after all five additions.

The updater sets the ready bit when the count reaches the stock floor
of 8 and divides each sum by the cohort count. It copies the means over
the factor array at age zero. Otherwise it averages each mean with the
same old factor three times, giving
`floor((mean + 7 * old_factor) / 8)`. At age 5 or greater, a difference
of at least 33 in any lane resets the entire array to `0x8000` and age
to zero. A separate request at mask `0x40` of the inhibit byte clears
the request and performs the same unity and age reset. A completed
copy or blend increments the age with saturation at 255.

| Estimator value | JK00C | JK00D |
| --- | --- | --- |
| Five ratio halfwords | `ffff38d0` | `ffff38e4` |
| Five sum longwords | `ffff397c` | `ffff3990` |
| Cohort count | `ffff37fd` | `ffff3811` |
| Five mean halfwords | `ffff3942` | `ffff3956` |
| Ready state bit | `ffff43bd & 0x40` | `ffff43d1 & 0x40` |
| Stock operating limit, delay reload | `00008905`, `00008c4c` | `00008906`, `00008c4d` |
| Stock cohort floor, outlier age, difference, blend count | `0000880f`, `00008807`, `00009124`, `00008877` | `00008810`, `00008808`, `00009132`, `00008878` |

The collector stages the halfwords at `0008b0c6`, stores the sums at
`0008b144` and increments the count at `0008b152`. The updater's ready
store is `0008b226`, its mean store is `0008b234`, and its factor stores
are `0008b24e`, `0008b2a6`, and `0008b2d4`. The raw interval unit and
the mechanical phase of the capture edge require separate evidence.

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
separate evidence requirements. The physical scale of the JK00 timing
words remains open.
