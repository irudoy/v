# Bounded JK08A RAM initialization writes

The five exact clear paths use stock ROM start and exclusive-limit pointers.
Four bounded window parents are `00027AC0`, `00027C50`, `0002FC24` and
`00034B70`; their tested entries are `00027AE4`, `00027C6E`, `0002FC8A` and
`00034BF4`. The first three entries have explicit incoming GBR premises
`000225F4`, `0002260C` and `0002260C`. The fourth loads its descriptor base
from stock literal `00034DA0`. These premises assert no boot or reset path.

The complete natural helper `00026F30..00026F4C` loads ROM pointer `00022624`
through the exact literal at `00026F9C`. Its descriptor contains start
`FFFF4514` at `00022624` and limit `FFFF5CF2` at `00022628`. The longword store
at `00026F3E` increments its pointer by four and reloads the ROM limit at
`00026F42` before each loop comparison. The stock RTS at `00026F48` and NOP
delay slot return through the unchanged incoming PR. The complete frame,
GBR, MACH and MACL remain unchanged; this helper has no call or frame access.

The native half-open ranges are FFFF261C..FFFF4512, FFFF1000..FFFF261A and
FFFF1000..FFFF5CF2. The last range belongs to both clear services. A store
executes while its aligned start is below the limit. Each final store clears
all four bytes, including the two bytes above the unaligned exclusive limit.
The corresponding physical ends are FFFF4514, FFFF261C and FFFF5CF4.
The natural helper clears `FFFF4514..FFFF5CF4`, including the complete
longword containing `FFFF5B2C` and both bytes above its exclusive limit.
The delay-slot stack writes at `0002FCA2` and `00034C0E` execute on both
loop outcomes and retain the post-increment pointer.
Each pinned stock interval is nonempty, so its initial skip branch falls
through. The loop back edges include both continuing and terminating outcomes.

The fixture relocates only the six declared RAM pointers in the ROM range
table. It places four observing returns at the bounded windows' exclusive
code ends, outside the tested instruction spans. The natural helper retains
its exact stock RTS/NOP and receives no synthetic return. All other instruction and descriptor
bytes remain bound to the owned stock image. Independent equations compare
the actual before/after ROM descriptor snapshots and
the full RAM footprint, exact longword store sequence, registers, SR, frame,
SP, PR and caller ABI. Complete-range equations preserve every byte outside
the rounded physical clear range. Different nonzero RAM seeds distinguish
executed clearing from an initially zero field.

The 15 explicit complete-RAM inputs retain the previous twelve window inputs
and add three nonzero seed/context inputs for the natural helper. Independent
physical equations bind its complete ordered pointer/descriptor reads,
longword stores and repeated ROM limit reads. Its fixed nonempty stock range
requires the initial skip to fall through and both continuing and terminating
loop outcomes. This boundary supplies no empty-range or mutable-descriptor
execution claim.

The independent instruction budget is the maximum of the exact stock prefix,
longword count, loop-body length and two boundary-return instructions. It
applies only to this declared family; the common instruction limit remains
16384. The owning publication appends identity evidence to 43 existing writer
relations in 17 complete owner documents. Native width, signedness, ledger,
other facts and original TEST evidence positions remain fixed. A physical
longword store infers no semantic field width, units, scale or hardware use.
