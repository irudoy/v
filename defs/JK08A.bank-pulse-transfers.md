# Natural JK08A bank base-pulse transfers

`JK08A.bank-pulse-transfers.toml` binds the complete stock function
0004EAD4..0004EBA2 to the existing bank base-pulse assembly. Its natural
RTS at 0004EB9E executes the MACL-restoring delay slot at 0004EBA0.
Only the three declared RAM pointer pools relocate to simulator storage.
The ROM pointer, word offsets and FFFF3800 arithmetic literal retain
their stock values. No observing return or stock-function stub is installed.

The low byte of the independent incoming R4 selects bank0 or bank1.
Upper-byte controls retain the actual EXTU.B behavior. This premise
establishes no upstream bank producer or physical bank-to-cylinder order.
Every numerical operand retains the existing bounded unsigned-word
consumer interpretation. Native signedness and engineering units remain
separate facts.

## Independent original

The legacy bank base-pulse header supplies input words, flag bytes,
incoming R4/T and a context variant. Expected output, expected registers,
final T and group columns are ignored. A source contract changes these
columns independently without changing capture inputs. Additional
single-word alternatives hold the complete context, every other RAM byte
and all calibration bytes fixed.

The common 80-byte context and 572-byte observer retain all GPRs, special
registers, full SR, frame, SP, PR, independent caller ABI and the complete
relocated RAM image. The raw C adapter records actual state without
expected results. All pointer, offset and flag bytes are observed before
and after each invocation. The exact private assembly, legacy input header,
generated input header, raw driver and observer bind the original COPY
primary together with image/fixture/object/ELF/toolchain identities,
commands and bounded terminal streams.

Independent instruction-state equations execute the unchanged bytes.
Separate scalar equations retain the existing base-pulse formula:

```
include_L = flag1.bit1 or selected_control <= 16384
trim = max(0,S + include_L*L + E - 25600*(1 + include_L))
product = uint32(I*trim)
intermediate = A + floor(product/65536)
corrected = floor(uint32(256*intermediate + O - 32768)/256) if I!=0 else intermediate
output = min(65535,corrected)
```

Flag1.bit1 selects LTFT read 0004EB04 and bypasses both control words
and flag2. Otherwise flag2.bit4 selects one control word. A selected
control <=16384 reaches LTFT read 0004EB42; a larger control omits it.
The independent precursor I is read at 0004EB5E. I=0 bypasses both the
offset read at 0004EB7A and its arithmetic. MUL.L retains its low32
product, the offset calculation retains unsigned wrap, and the cap
preserves equality and both neighboring outcomes. No monotone effect
is inferred from the complete unsigned machine domain.

The physical consumer requires the exact order, datum addresses, sites,
word/byte widths, directions and values of all RAM transfers and both
conditional flag reads. It separately compares the arithmetic scratch
registers, final cap T and complete RAM footprint. Every required
conditional outcome and each positive reader alternative is required.
The selected result word is the only RAM modification; the sibling bank,
other operands, frame and caller state retain their declared contracts.

## Precursor and channel stages

`JK08A.bank-pulse-stages.toml` binds the complete existing precursor
0004E974 and channel builder 0004EBA2, including the real 00021CE0
unsigned divider, 0002657C signed fixed-point multiply, 000224F8 shift
and 0005B7EC affine helper. Each stock assembly unit is independently
reconstructed. A pointer alias changes only the first longword of a
larger pool; the remaining ROM pointers and values retain their bytes.
Natural returns, delay slots and every tested instruction remain stock.

The additional raw component uses 16 input-only prefix rows from each
legacy stage header and explicit finite control, calibration and word
boundary inputs. Expected results, expected GPRs and local-frame columns
are ignored. The existing full legacy GNU regions and their complete
matrices retain their contracts. Stage contexts state every register,
RAM byte and calibration input independently. The current complete
observer, COPY primary and strict private-source protocol are shared
with the base-pulse component.

The precursor reuses `stock_precursor_model.arithmetic`: source selection,
optional speed cap, low32 product extraction, two bank products and real
division, signed transient/gain arithmetic, word clamps and common flag
publication. The physical consumer requires both bank iterations, exact
RAM and ROM transfers, actual helper order and post-delay operands.
FFFF40B8 is read at 0004EA10 on the second iteration; FFFF18C2 is stored
at 0004EA62 in the real loop delay slot. Positive bank1 alternatives hold
the complete context, every other RAM byte and all calibrations fixed.

The channel builder admits uint8(R4) in 0..5 with independent upper bits.
Its aggregate mask selects the opening word for both outputs or the
parity base, signed additive/subtractive words and conditional multiplier.
The true shift and affine helpers retain low32 arithmetic and saturated
branches. The result at FFFF23C8+2*i is stored at 0004EC9E; i=1 binds
the owning FFFF23CA relation. The transformed result and every other
RAM byte remain part of the complete footprint comparison. Explicit
calibration contexts establish no live calibration or actuator behavior.

Both input signs and reachable helper paths have explicit inputs. The
unsigned divider receives a nonzero unsigned16 divisor: the caller
bypasses its zero-divisor path and supplies either speed or 25600. Its
wide-divisor branch is outside these premises. Every fixed-point call
supplies exponent -2, retaining the real two-step left-shift loop and
excluding the nonnegative-exponent branch. These guards grant no
interior-entry or unconstrained helper-domain coverage.

## Owning publication

`JK08A.bank-pulse-access-claims.toml` pins 9 exact original relations in
eight complete owner documents. Five base-pulse readers bind FFFF18C2, FFFF22DE,
FFFF2304, FFFF2312 and FFFF2A26. One writer binds FFFF191E.
The precursor adds the FFFF40B8 reader and FFFF18C2 writer; the channel
adds the FFFF23CA writer. Both famous-grouse relations share one complete
postimage. Both conditional LTFT sites belong to their exact relation.
Seven owners retain semantic width16 and unset signedness. Injection_1
retains unset width and signedness. All owners preserve original ledgers, all
other layouts, link properties, symbol/link evidence positions and TEST
origins.

One exact nine-item ordinary `link` batch uses the existing writer.
The complete proposed documents append only their owning proof items.
Only a unique exact pinned append with its complete canonical claim
digest is neutral to an existing physical scope. Changed, duplicated,
misplaced or unrelated attachments and changed native values retain
their scope effect. Full publication, every TEST origin and exact COPY,
injection, coherent and SID22 scopes remain required.

Owning evidence supports access identity only. It grants no reverse
function, scale, units, upstream producer, scheduling or hardware
admission. Source preparation qualifies no original pending review.
