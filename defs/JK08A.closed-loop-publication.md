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

### Learning tick

`unique-aardwolf/fn` at `0005911c` calls `FUN 00057c78` only while
`ffff41ad.bit4` is set. `FUN 00057c78` sets tick bit `ffff249d.bit1` when start
bit `ffff4184.bit6` is clear and counter `ffff25fa` is zero, and then reloads
the counter with the immediate of `00057ca0`. While the start bit is set it
reloads the counter without a tick. `FUN 000208f8` decrements the five counters
from `ffff25f6` once per three cylinder events, one crank revolution, so a tick
occurs once per reload count of revolutions. `FUN 00057c78` stores
`ffff2474.bit5 = (FUN 00025d02(0x0129) != 0)`, the dual-bank MAF diagnostic
record, calls `FUN 00058740`, and clears the tick bit. The scheduler entry of
`0005911c` is indirect, so the call period is not established.

Before that stage `FUN 00057c34(b)` advances counter `ffff12ee+b` and, when it
reaches `ROM8[000082c4]`, copies `af_adjustment` `ffff45a0+2*b` to
`ffff12f0+2*b` and clears the counter. `0005911c` stores
`ffff28fa+2*b = sat16(ffff28b8+2*b - ffff29e2+2*b)`, the nominal word minus
the observed word.

### Composite gate

`FUN 00058740` evaluates, for bank `b`:

```text
C_b = ffff22e1.bit(b)
      && ffff1071 >= ROM8[00008cfd]
      && |d_b| <= ROM16[00008fa4] / 500
      && ROM16[00008ecc] < int16(ffff45a0+2*b) <= ROM16[00008ece]
      && ffff15ce == 0
      && MODE_b
      && !ffff4250.bit2 && !ffff2474.bit5 && !ffff41be.bit2 && !ffff2486.bit4
d_b = int16(((33*ffff12f0+2*b - 33*ffff87ec+2*b) & 0x3fffffff) >> 14)
MODE_b = (T26_b && !T58_b) || T22 || ffff24d0.bit5 || ffff24ce.bit1
T22   = !ffff2459.bit5 && ffff24d1.bit7 && ffff23bc < 2
T26_b = ffff2eab+b == 0 && ffff2ead+b == 0 && T24 && ffff24d1.bit7
        && !ffff29d5.bit(b) && !ffff29d4.bit(b)
T24   = ffff881a / 5 > ROM8[00008704]
```

Each call ends by storing `ffff12f0+2*b` in `ffff87ec+2*b`. A bound below one
admits an increase of the latched copy below 16384/33 raw and fails on any
decrease, so a decrease fails `C_b` for one call. `ffff2459.bit5` is the
closed-throttle bit; `T22` is the off-idle mode and `T26_b` the idle mode.

`ffff881a = min(0xffdc, ffff87f0 + 1)` while `ffff110e <= ROM8[00008706]`,
`ffff3140 / 40 <= ROM8[00008705]` and `ffff2459.bit5` hold, else 0;
`ffff87f0` keeps the value of the previous call. `T58_b` is set while the
episode counter `ffff8800+b` exceeds `ROM8[000083ba]`. The counter advances
when the composite predicate of the previous call rises with the stability
predicate of the previous call set, and `ffff13ab+b` receives its value.

### Published predicates

```text
cnt_b = C_b ? min(255, ffff87fe+b + tick) : 0        stored in ffff87fe+b
P_b   = cnt_b > 1
ffff1457.bit(b) = tick && P_b && C_b
ffff1458.bit(b) = P_b && (|X_b - X'_b| >> 8) <= ROM8[000082eb]
                  && |int16(ffff28fa+2*b)| <= ROM16[00008f52]
X_b   = (min(65535, ffff22dc+2*b * ffff28b8+2*b / 8000) * 0x8b51 >> 14) >> 1
```

`X_b` is sampled on tick calls into `ffff87f6+2*b`, and `X'_b` is the sample of
the previous tick at `ffff8828+2*b`. `ffff1620`, `ffff131c` and `ffff1552`
publish `C_b`, `P_b` and `T58_b` in bit `b`. One failing call of `C_b` clears
`cnt_b`, so a permit returns after two further ticks. `ffff1457` is set for one
call per tick; `ffff1458` holds between ticks. A set permission bit alone
establishes no physical learning rate.

### Inputs with open meaning

The code fixes the conditions above; the physical meaning of these inputs
remains open:

- `ffff22e1.bit(b)`: the feedback calculation `0005cbec` sets it at `0005d612`
  when `ffff894e+b` is nonzero. `ffff894e` is the OR of `ffff893d`,
  `ffff8943`, `ffff894c` and elapsed flag `ffff8969`, stored at `0005d1b2`;
  bank 2 uses `ffff893e`, `ffff8944`, `ffff894d` and `ffff896a`, stored at
  `0005d1ce`. The sources are not reviewed.
- `ffff24d1.bit7`: `FUN 00069374` stores `ffff90f0` there at `0006d4c8`, with
  `ffff90f0 = ffff90ec || (ffff48a8 >> 16) >= ROM16[000090c0]`. `ffff48a8` is
  a saturating 32-bit sum that `00069374` advances at `0006ced2`; its operands
  and reset are not reviewed.
- `ffff3140` and `ffff23bc`: idle-air words that `00069374` stores at
  `0006cbf4`/`0006cc2e` and `0006db90`.
- `ffff15ce`: the composite output of `FUN 00055098`.
- `ffff24d0.bit5`, `ffff24ce.bit1`, `ffff4250.bit2`, `ffff41be.bit2`,
  `ffff2486.bit4`, `ffff41ad.bit4`, `ffff2eab..ffff2eae` and
  `ffff29d4`/`ffff29d5`: the writers of these bits are not reviewed; L0
  records no writer of `ffff29d4` or `ffff29d5`.
- The reset of the episode counters `ffff8800+b` is not traced.

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
