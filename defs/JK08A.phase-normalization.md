# Natural JK08A APC phase normalization accesses

`JK08A.phase-normalization.toml` binds the complete natural entry
00028DC8..00028E7C and splitter 00028E7C..00028E9E to the existing
`stock_jk08a_injection_tooth.s`.
The normalizer has no helper calls or synthetic observing return. Its
natural RTS instructions and delay-slot stores remain tested stock bytes.
The fixture relocates only the longword base literal at 00029020 from
FFFF128C to 0100128C. The word offset 0126 at 00028E9E selects position
byte FFFF13B2. The multiplier word 6554 at 00028EA0 belongs to the splitter.
All literals are observed before and after every call.

Normalizer R4 and R5 explicitly select one of two native word/byte pairs:
FFFF13B8/FFFF193B or FFFF1558/FFFF155A. These are pointer premises for
the exact natural normalizer entry. Saved stock caller instructions at
0002B6BC..0002B6CC and 0002AAD8..0002AB12 bind the corresponding pointer
construction and call delay slots. The complete caller bodies, source
argument dispatch, interrupt state and scheduler reachability are outside
this bounded normalizer execution.

The shared 80-byte context and 572-byte observer retain all GPRs, special
registers, full SR, frame, SP, PR, independent caller ABI, complete relocated
RAM and eight literal bytes. The raw C adapter records inputs and actual
outputs without an expected-value table. Private source/header identities,
GNU reconstruction, image/fixture/object/ELF/toolchain identities, commands
and terminal streams bind the original complete COPY primary. No separate
receipt, observer ABI or execution framework is introduced.

## Independent scalar and physical boundary

The independent consumer reuses `stock_injection_programmer_model.normalized`
for the scalar count, remainder and scratch-register equations. Separate
instruction-state equations execute the unchanged stock bytes. Physical
comparison retains the phase read at 00028DCE, word read at 00028DD0,
conditional word stores at 00028E02/00028E52/00028E62/00028E6E, byte
reads at 00028E04/00028E64/00028E70 and byte stores at 00028E08/00028E76.
The phase9/count9 path includes the repeated word read at 00028E0A after
the count8 store. The RTS delay-slot word and byte stores are actual
transfers, with exact widths, addresses, directions and values.

Phase4, phase9 and the default phase path have separate boundary inputs.
Unsigned word high bits, raw byte sign bits and modulo256 additions remain
explicit. Every conditional outcome and each exact owning transfer require
positive observations. Both pointer pairs have word and byte value/output
alternatives with every other memory byte, register and literal held fixed.
Full state comparison preserves unselected pairs and neighboring bytes.

## Natural splitter and full R4 semantics

The existing 17-instruction splitter retains its natural return and the
MACL-restoring RTS delay slot at00028E9C. R4 is an explicit complete
unsigned register input; R5 selects the word pointer and R6 the byte
pointer. The original normalizer retains its separate R4/R5 pointer
premises. The raw capture retains every other register, memory byte,
literal and caller state while the splitter argument varies.

The separate full-register equations are:

    product = uint32(R4 * 6554)
    count = product >> 16
    remaining = uint32(R4 - 10*count)
    byte = uint8(remaining)

The word store at00028E94 executes in the BT/S delay slot for both branch
outcomes. The byte store at00028E98 is also unconditional. Zero count skips
the subtract instruction while preserving the same remaining value.
MACL, MACH, GBR, natural SP/PR, the outer ABI and all unselected RAM are
preserved. Independent instruction equations and exact physical transfers
require the multiplier read, both stores, complete scratch state and both
conditional outcomes.

For explicitly bounded byte inputs0..255, count and byte equal quotient
and remainder modulo ten. Full R4 follows the low32 product and truncation
equations; no unbounded quotient-by-ten interpretation follows from the
function name. The raw matrix includes byte inputs and separate full-word
boundaries. Positive argument alternatives hold all other context, input
RAM and literals fixed and separately vary each output. Neither prior
output word nor byte is read by the splitter.

The owning splitter relations are writer28E94/FFFF1558 and
writer28E98/FFFF155A. The normalizer and splitter bind ten exact
original/proposed claim items in four complete native documents. Shared
vivacious-petrel and peridot-pony postimages contain their normalizer and
splitter evidence together, with their semantic types unset. Explicit
pointer premises establish no full caller, argument producer, scheduler,
physical unit, scale or hardware behavior.

## Bounded programmer offset and real helper

`JK08A.phase-programmer.toml` binds the existing
`stock_jk08a_injection_offset.s` at0002B6D4..0002B6F8 and its real
00028E7C..00028E9E helper. The entry explicitly assumes that control has
reached the offset calculation after the count decision. Period word
FFFF22BC and remainder byte FFFF193B are software inputs. The body
zero-extends them, multiplies them and constructs both output pointers.
JSR0002B6F4 calls00028E7C with R4=period*remainder,
R5=010016C2 and R6=0100166C after the actual delay-slot ADD.

The separate equations retain the full product M and the helper's low32
multiply by6554. Word FFFF16C2 receives floor(uint32(6554*M)/65536),
and byte FFFF166C receives uint8(M-10*Q). The reciprocal product can
wrap, the quotient can decrease and the residue need not be0..9.
P=8192,R=4 gives Q3277 and byte254; P=25000,R=8 gives Q20001 and
byte246. MACL retains M after the natural helper restores it. The
incoming MACL before the caller multiply is a separate context value.

Only the longword pools0002B864 and0002B874 are relocated to the
01000000 RAM alias. Every instruction and other literal retains its
stock bytes and address. The natural helper returns to0002B6F8. An
independently assembled observing return at that address restores the
outer PR from SP+24 through R7, outside all tested instruction spans.
The complete programmer prologue, count decision, following compare
programming, native MMIO, scheduling and hardware behavior retain
separate evidence. The fixture uses no stock-function stub.

Required component `phase_programmer_paths` belongs to the same original
complete COPY primary as `phase_normalization_paths`. It uses the same
80-byte context, 572-byte observer, complete relocated RAM, frame, ABI,
SR and literal observations. Its private header reads only the first
four input columns of all14118 existing offset literals, followed by
explicit period/remainder, context and T boundaries. Expected-output
columns do not enter raw inputs. Separate state, scalar, physical,
post-delay call and branch consumers require both stores and exact
return paths. Positive period and remainder alternatives separately
vary each output while every other input remains fixed.

Owning programmer relations bind writer2B64A/FFFF16C2 to the helper
word store00028E94 and writer2B64A/FFFF166C to byte store00028E98.
The complete family retains all ten normalizer/splitter original and
proposed claim items. Amphibian-panda retains unsigned16 in its symbol;
injection_offset_reciprocal_residue retains inherited unsigned8 from
its meaning. Their full native documents and existing TEST positions
remain part of the exact grouped transition.

## Owning metadata boundary

`JK08A.phase-access-claims.toml` pins 12 exact original relations in six
complete owner documents. Normalizer owners retain their reader and writer
in one shared postimage; programmer owners retain their full documents.
Existing ordinary `link` operations append the exact complete twelve-item
batch. The whole transition preserves every
other native value, semantic type, ledger, original symbol/link evidence
position and TEST origin. Huge-lori retains unsigned16 and economic-collie
retains unsigned8. Vivacious-petrel and peridot-pony retain unset width and
signedness; physical word/byte accesses infer no semantic type.

Unique exact owning appends are neutral to existing physical scopes only
when their complete canonical relation digest matches the pinned postimage.
Changed or duplicated items and all other native values retain their scope
effect. Full native publication, TEST origin and COPY/injection/coherent/
SID22 scope equality remain required. The evidence supports its owning
access identity only. It grants no reverse function level, engineering
units, scale, live scheduling, hardware reachability or peripheral effect.
Source preparation qualifies no original review.
