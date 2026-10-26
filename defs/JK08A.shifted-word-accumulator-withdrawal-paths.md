# Natural shifted word accumulator

`defs/JK08A.shifted-word-accumulator-withdrawal-paths.toml` binds 82 stock
instructions in one natural function span, 10 literal pools, three four-byte
RAM pointer aliases and three scalar calibration inputs. Entry `000a5398`
returns through its stock RTS and delay slot. It calls no helper or scheduler.

The function clears word `ffff3334` when `ffff244f.bit5` is clear. With that
bit set, native byte `ffff84c3.bit6` gates accumulation. The byte metric at
`ffff338a` must exceed unsigned byte threshold `00008cba`. Active accumulation
uses `S=floor(uint16(ffff1040)*uint8(000083ec)/256)` and
`P=(uint8(ffff338a)-uint8(00008cba))*S`.

Byte `00008a0d` selects the shift path. Zero uses `P` directly. A nonzero value
shifts while the iteration count is less than that byte or less than 8. Before
each shift, a value at least `0x800000` becomes `0x00ffffff` and terminates the
loop. The publication adds the resulting value shifted right by 16 to the
previous unsigned word and saturates to `65535`. A zero product with shift byte
255 takes the complete 255-iteration path. The first product overflow branch
is infeasible: `floor(65535*255/256)=65279`, below `65536`.

The exact original reader relations from surface roots `0000abba` and
`0000abfa` to this function have no direct physical operand in its complete
natural closure. Its full physical ROM source set consists of the pinned pools
and the three scalar inputs. This absence supplies no table extent, declared
element width, physical unit or inference about a different entry. The full
surface summaries, raw scale, diagnostic associations, other readers, reverse
properties and dependencies through produced RAM values remain intact.

The independent numerical equations and separately composed complete CPU,
frame, physical operand and branch state bind the real word publication.
Fixed-other input groups require a changed actual stored word for every active
gate, metric, word, prior value and scalar calibration. Matching final word
bytes cannot replace the complete returned state or physical operand stream.

The observation uses the existing 80-byte context, 572-byte result and both
192-byte frame images. It retains complete ordinary 64 KiB RAM and a complete
native `ffff8400..ffff84ff` window, using the existing publication-inhibit
memory premise. The native window must equal its ordinary-RAM mirror before
and after each invocation. The native word literal `84c3` and every instruction
remain exact. Only the three declared full pointer pools relocate into
`01000000..0100ffff`. There are no stock-function stubs, synthetic returns or
instruction substitutions.

The sources participate in the existing scalar RAM leaf withdrawal family and
complete GNU primary lifecycle. Their preparation establishes no accepted
execution, native publication, TEST qualification, scheduling, scale, unit or
hardware fact. The package acceptance consumes the exact current full native
owners, retained function, ledger selectors and all original TEST positions.


## Shared owning source boundary

The shared descriptor contains 134 exact access originals: 123 readers and
eleven individually pinned writers, 100 complete datum owners, 74 complete
functions and 126 matching ledger selectors (118 datum-end selectors and
8 function-end selectors). All 134 exact normal unlink operations form one
complete phase. Thirty-three independent components use the same complete
original COPY primary. The existing registry contains 39 families and
82 captures. Five complete function transitions retain eight exact
function-end selector withdrawals.

The accumulator adds two exact originals and one complete unchanged function.
Four preceding records share its two table owners. Only their three proposed
image fields change to the complete three-reader postimage of each owner;
the other 128 preceding records and all 73 complete functions remain exact.
Full preceding images remain recoverable and have exact separate current
image pins. Native types, evidence, TEST positions, ledger order, calibration
semantics and downstream RAM and producer dependencies remain mandatory.
The native8400/256 transport and observer retain their existing complete
window; the finite source-oracle admission names only this component.
Source completion grants no identity, scale, units, executable, native
publication, whole-ECU or hardware admission.
