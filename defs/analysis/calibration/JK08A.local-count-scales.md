# Candidate local count conversions

## Claim and ownership

`defs/registries/JK08A.findings.csv` owns the home scale of these two tables at knowledge
stage 4. Both identity confidence and scale confidence remain `candidate`.
The local count arithmetic identifies no physical quantity, engineering unit,
stock mode reachability, or hardware result.
There is no hardware validation for either conversion.

| Table | Meaning | Unit retained by the owner | Scale | Inverse |
| --- | --- | --- | --- | --- |
| `0000c98e` | `accomplished-alpaca/tbl` | `raw with offset 32768` | `x-32768` | `x+32768` |
| `0001295c` | `sparkling-grebe/tbl` | `raw` | `x*2` | `x/2` |

Image identities and source paths belong to `rom-images/roms.csv`.

## Centered word at 0000c98e

### Local sample and domain

`raw` is the uint16 return sample from the `0000c98e` lookup, in domain
`0..65535`. It is not the unrelated signed term supplied to the later consumer.
The local conversion is:

```text
centered = signed16((raw - 32768) & 0xffff) = raw-32768
centered domain = -32768..32767
raw = centered + 32768
```

This equality concerns the stored word and its signed read. The producer's
`EXTS.W` alone is not the scale: the low-word store is essential when `raw` has
bit 15 set. The inverse is exact over the centered signed domain; it does not
undo subsequent addition, clamping, or flag replacement.

The caller binds table `0000c98e`, word axes `00013478` and `00013498`, and wrapper
`000262a8`. The first input is the word at `ffff412a`, passed in R7 by the call's
`0007b2f4` delay slot; the second input is the word at `ffff11b6`, placed at
stack offset 2 by `0007b2e8`. These inputs are independently seeded raw
coordinates, not physically named signals. The wrapper, its axis helpers and
word-cell reads, and their actual calls and returns execute. With both fractions
zero, `0002688e` reads the selected cell in a delay slot and `0002689c` returns
without calling finisher `00026740`.
The gate covers exact/end points and clamped high endpoints, not fractional
explicit-axis division or the nonzero-fraction finisher paths. Entry into
`00026c78`, `00026d10`, or `00026af8` is
rejected. Distinct corner cells distinguish both input placements and prevent a
flat calibration from concealing a swapped coordinate.

### Storage and bounded consumer

Producer segment `0007b2f6..0007b308` forms the offset and writes the word to
`ffff2c6e`. Consumer `0007b35a..0007b390` reads that exact word with `MOV.W` at
`0007b35e`, adds an independently supplied signed16 term, and applies signed
lower and upper bounds from `ffff413a` and `ffff4138`:

```text
local = min(upper, max(lower, centered + other))
if ffff41fb.bit5: local = upper
if ffff41fb.bit4: local = lower
ffff2c6c = local
```

The final store is the delay slot at `0007b390`; bit 4 has priority if both
replacement bits are set. The gate observes the word write, the signed word
read, both clamp outcomes, flag replacements, and the final word store.
The executed raw samples are `0`, `1`, `0x7ffe`, `0x7fff`, `0x8000`, `0x8001`,
`0xfffe`, and `0xffff`. The other term samples are `-32768`, `-1`, `0`, `1`,
and `32767`; bound pairs are the full signed range, `-100..100`, and `0..0`.
All combinations of bits 4 and 5 execute. These are fixture operands, not
measured simultaneous ECU samples. An exhaustive arithmetic round trip over
all uint16 values supplements, but does not expand, this instruction-execution
sample coverage.

### Stock-disabled path and excluded calculations

The stock-disabled lookup is tested independently. Stock `ROM8[000083c1]=0x2c`
has mask `0x02` clear, so `0007b2de` branches to the fallback. No table read or
`ffff2c6e` write occurs, and `0007b39e` copies `ffff243c` to `ffff2c6c`.
The enabled fixture sets this data bit in memory. Its arithmetic proof does not
establish that stock operation executes the map branch.

The alternate table lookup, divider, and producer of the other signed term in
`0007b30a..0007b358` are outside the gate. The consumer receives that term as an
independent incoming operand. Full function entry/epilogue, state lifecycle,
physical quantity, and downstream actuator effects are not asserted.

## Local bound at 0001295c

### Lookup sample and domain

`raw` is the uint8 lookup sample stored at `ffff172e`, in domain `0..255`.
`00044a48` loads table `0001295c`; byte input `ffff106f` reaches wrapper
`00026370` through call `00044a50` and unsigned delay-slot conversion
`00044a52`. Byte store `00044a5a` preserves the result. For input below 224,
kernel `00026a80` and finisher `00026740` execute real fractional interpolation;
at or above 224, the wrapper selects cell 7 directly. Wrapper and helper
calls and returns execute without stubs.

Unequal ascending and descending calibration samples test interpolation and
input boundaries independently of the stock flat table. Constant calibration
variants test the unsigned result and subsequent bound for every byte value.
Neither input conversion nor the table's physical quantity is identified by
these operational checks.

### Two local clamps

The first consumer reads `ffff172e` at `000453b2`, zero-extends it, and shifts it
at `000453b8`. The comparison selects the original signed16 value or `2*raw`;
the replacement shift is the `000453c2` delay slot. Store `00045444` writes the
selected word to stack offset 8.

The second consumer reads `ffff172e` at `000455c6`, zero-extends it, and shifts
it at `000455cc`. Its independently supplied signed16 value has an unsigned
byte from `ffff13f7` added before comparison. If replacement is required,
`000455d6` shifts in the branch delay slot; `000455dc` stores the word to stack
offset 8.

```text
bound = 2*raw                       # 0..510 local count domain
first = min(value, bound)
second = min(value + pre_added, bound)
raw = bound/2                       # exact only on the even bound grid
```

`value` is a separate incoming consumer operand, not another observation of the
lookup sample. `pre_added` is a separate byte in `0..255`. Boundary execution
uses signed extrema, `-1`, `0`, and values immediately below, at, and above the
bound, with pre-addition samples `0`, `1`, and `255`. Both keep and replacement
paths execute, including both replacement delay slots. The inverse `x/2` does
not encode an arbitrary odd count as a whole byte and does not reconstruct a
value already changed by the clamp.

### Normal and alternate completion

Normal completion reads another independent byte, `ffff15b4`, adds twice that
byte after the local clamp, and caps the result at 32767 before word store
`0004561e` to `ffff1230`:

```text
final = min(local + 2*u8(ffff15b4), 32767)
raw = 128, value = 300, pre_added = 0
local = 256, u8(ffff15b4) = 255, final = 766
```

This executed 766 counterexample establishes that `2*raw` is not a universal
final-output bound. On these local paths the upper bound is at most 510 and the
extra term at most 510, so normal saturation is not reached by those lookup
operands. Separate saturation cases supply an independent incoming operand at
stack offset 8 near 32767. Those cases prove the completion region's cap, not
attainability of that operand from the reviewed lookup and clamp.

For nonzero completion selector R9, execution follows the actual call and its
delay slot, stopping at `0002c626` before that function executes. Its return,
alternate final result, surrounding mode selection, and preceding adaptive
calculations are outside the gate. Neither complete-function behavior nor
physical output units are asserted.

## Negative checks and evidence boundary

Fixed-span mutants change map literals, register operands, widths, branches,
centering instructions, or delay slots. They fail the fixed byte binding.
Separate execution mutants bypass that binding and compare the returned machine
observations with an independent arithmetic oracle. They remove centering,
change the signed word read to a byte read, omit comparison/replacement shifts
on both bound paths, omit unsigned byte extension, change the post-clamp
addition, or invert the normal saturation branch. Observational helpers do not
embed the expected scale, so a failed arithmetic observation is not confused
with a rejected byte snapshot.

These software checks retain both candidate scales and the existing owner units
and inverses. They provide no hardware validation, physical promotion, or
permission to flash a modified image.
