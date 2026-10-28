# JK08A bounded closed-loop publication and learning

The stock `7mfk` contracts bind three independent execution boundaries to the
stock image. The arithmetic describes software inputs, not their producers,
physical units, permission cadence or a jointly executed feedback cycle.
Hardware readiness is NO. Live permission and scheduling remain subject to
CONSULT-III Plus observation or bench validation before hardware testing.

## Post-feedback STFT publication

The boundary is `0005ca08..0005ca5e`, the final publication fragment of
`divergent-grasshopper/fn` at `0005c910`. Its preceding feedback calculation is
outside this contract. The supplied 32-byte caller save frame contains the real
saved PR and R8..R14. The original epilogue, RTS and delay slot execute.

Let `M` be the independent byte at `ffff99c4`, `P` the independent byte at
`ffff9925`, and `F = (M >> 1) & 1`. For each bank, the output is
`(1-F)*W + F*256*min(125,max(75,P))`. Bank 1 copies the unsigned word at
`ffff40ac` to `ffff22dc`; bank 2 copies `ffff40ae` to `ffff22de`.
The held working word has positive influence on its output; the forced branch
is constant in that word.

The mode and forced-percent bytes have a verified software reader. Their
producer semantics, physical units and cadence are independent obligations.

## Learned-grid selection

The complete entry is `successful-tarantula/fn` at `0005796c`.
It calls the real stock fill helper at `00058092`, auxiliary reset helper at
`000580e8` and diagnostic byte-1 bit-7 predicate at `00025e20`. The predicate
receives descriptor index 297. Other predicate indices have byte identity only.

Let `b = uint8(R4)` in 0..1. Upper register bits are independent. The prior
packed byte at `ffff130a+b` supplies load index `O = packed & 7` and speed
index `O = (packed >> 3) & 7`; its upper two bits do not affect either search.
The unsigned load word at `ffff1024` uses eight byte thresholds at `00012592`,
scaled by 256, and unsigned hysteresis at `0000881b`. The speed byte at
`ffff11ae` uses eight byte thresholds at `000126dc` and
`floor(ROM8[0000881a]/4)` hysteresis.

For either search, let `X` be its input, `A` its byte axis, `s` its scale and
`H` its hysteresis. The first-break raw index is the number of consecutive
thresholds `A[1]..A[7]` satisfying `X >= s*A[i]`. Subtract one when the raw
index exceeds `O` and `X < s*(A[O+1]+H)`. Add one when it is below `O` and
`X > s*(A[O]-H)`. Neither axis is required to be sorted. The addressed cell
is `8*speed_index + load_index`, in 0..63.

Bank 1 uses the 64-word grid at `ffff4b90`; bank 2 uses `ffff4b10`.
The candidate cell must lie inclusively between `256*ROM8[00008a9e]` and
`256*ROM8[00008a9f]`. Bit 0 at `ffff41b5` and bit 7 at `ffff5a94`
independently force reset. The diagnostic predicate executes only after the
range and control-byte checks permit it. Reset clears the selected bank's
adjustment word at `ffff45a0+2*b`, fills all 64 learned words with 25600 and
clears all 64 auxiliary bytes at `ffff49f0-64*b` through the real helpers.
The selected output at `ffff2306+2*b` is the candidate word or 25600. The
packed output byte is `8*speed_index + load_index` on both paths.

The selected-cell influence has sign `none` over this unsigned domain. With
the stock bounds, a cell of 23039 publishes 25600 through reset, while a cell
of 23040 publishes 23040.

## Learning permission producers

`FUN 00058740` writes bank bits 0 and 1 of both permission bytes and preserves
bits 2..7. The store at `00058f30` publishes `ffff1457` from the composite
bank predicates at `ffff8868` and `ffff886c`. The store at `0005906c` publishes
`ffff1458` from the independent predicates at `ffff8860` and `ffff8864`.
Bank 1 uses bit 0 and bank 2 uses bit 1 in each byte.

The latter predicates require the per-bank eligibility counter to exceed one,
then bound a saturated signed signal difference and a separate absolute
derivative word. The high byte of the absolute difference must not exceed
`ROM8[000082eb]`; the absolute word at `ffff28fa+2*b` must not exceed
`ROM16[00008f52]`. The raw signal identities and the physical causes of every
composite gate remain unreviewed. A set permission bit alone establishes no
physical learning rate.

`FUN 00057900` produces `ffff41b5.bit0` from request `ffff99d8.bit5` and latch
`ffff4201.bit6`. A set request with a clear latch sets both the pulse and the
latch. A following call with the latch set clears the pulse. A clear request
clears both and clears `ffff424f.bit4`; the preceding pulse and set latch can
set that completion bit before the pulse clears. The exact diagnostic request
identity remains open. The other reviewed direct writers preserve bit 0.

The matched JK78C producer at `00073e78` uses bit 6 of `ffff4514`, rather than
the 7mfk bit 0. Its native binding retains that mask. The shared telemetry
field remains unavailable there until a wire conversion is implemented.

## Bounded learned-grid update

The complete entry is `rousing-rhino/fn` at `00057d1e`. It executes the
real absolute-value helper at `00022590`, word fill helper at `00058092` and
auxiliary helper at `000580e8`. Let `b = uint8(R4)` in 0..1 and the packed
byte at `ffff130a+b` be explicitly in 0..63. The two independent permit bytes
at `ffff1458` and `ffff1457` must each contain bit `b`.

Let `W = RAM16[ffff134e+2*b]`, `S = RAM16[ffff22dc+2*b]` and
`L = RAM16[ffff2306+2*b]`, each independently unsigned. The three bytes at
`ffff2c21` select region 0..3 by the first-break search of
`abs(W-25600) > 256*threshold[i]`. The coefficient is the addressed byte at
`000129c6+region`, or `ROM8[00008a9d]` when the selected auxiliary cell is zero.
Compute `q = trunc0((W-25600)*coefficient/256)`. If `q == 0` and `S != 25600`,
add +1 for `W >= 25600` or -1 otherwise. The enabled cell receives
`max(256*ROM8[00008a9e], min(256*ROM8[00008a9f], L+delta))`.
The upper bound is applied before the lower bound, including inverted bounds.
Disabled calls preserve the full RAM image, including the addressed cell.

The STFT influence has sign `none`: STFT controls only the minimum-step gate,
while its direction follows the independent `W`. The arithmetic does not
identify the producer of `W` or infer a physical learning rate.

For auxiliary byte `C`, set `N = uint8(C+1)` and `D = ROM8[000088f5]`.
Its intermediate value is `max(0,N-D)` when `N+D > 255`, otherwise `N`.
Retain that value only when
`256*ROM8[0000839d] <= W < 256*ROM8[0000839c]`; otherwise clear the cell.
The enabled call changes only one learned word and one auxiliary byte in the
selected bank. The other 63 cells and the sibling bank remain observable.
