# ICI0A bounded ratio-cell action

## Placement and entry boundary

JK00A, JK03A, JK03B, and JK08A retain separate exact-image SHA-256 bindings
and independently execute the declared stock slices. Image identities and
source paths belong to `rom-images/roms.csv`. Expected instruction and data
spans are retained in `tools/mapkit/tests/fixtures/ici0a_ratio_path.json`.
The tests do not derive expected spans from the image under test.

ROM32[00020154] = 00028ea2 is the entry anchor. ROM32[00000970] = 00029588
is not used as this ISR vector anchor. The unrelated RAM-offset access at
`0004009e` is outside this fixture and its executable coverage.

Live TST at `00029586` controls BF at `00029588`. The fragment borrows the
software frame of `00028ea2`; it is not an independent interrupt entry.
The retained prologue saves the general registers, PR, MACL, and GBR. The
static software frame is 0x64 bytes, comprising the saved words and local
space. The restore tail at `0002a294` ends in RTE at `0002a2ba`.
No prologue, restore tail, or RTE is executed. A separate integer window
executes the actual preceding load, TST, and BF, then stops before either
fragment continuation.

R8 loads `ffff128c` at `00028f06` from `00029020`. R14 loads sign-extended
`ffff84fb` at `0002904a` from `0002914a`. The writer and reader execute
their own PC-relative word loads:

```text
ROM16[00029150] = ROM16[0002938e] = 06e0
ffff128c + 06e0 = ffff196c
```

The MOV.B writer at `000290cc` and MOV.B reader at `0002927c` touch that
same cell. The divider is a called arithmetic helper, not the direct RAM
reader. The test does not certify tracked function ownership or accepted L0.
The stock placement/action proof is independent of function recovery,
merge registries, preparation receipts, and committed structure exports.

## Incoming operands and executed action

R12 previous and R13 current are independent incoming unsigned 16-bit operands.
Their measurement and producers are not part of these windows. Independent
upper register bits exercise the actual EXTU.W narrowing. The gate byte at
`ffff8505` is an independent input, as are its unrelated bits, the retained
cell value and the skip-tail mode byte. The reader's incoming R0 status is
independent and must not be substituted with a seeded ratio result.

```text
byte = retained if gate bit 7 is clear
byte = 255 if current == 0
byte = min(255, floor(64 * previous / current)) otherwise
```

Producer execution begins at `0002909a` and stops at `000290ce` or `0002911c`.
The entry includes the actual gate byte load and TST. Gate-clear execution
retains the ratio cell. Its included skip tail can set gate bit 7 when the
independent mode is at least two; it preserves all other gate bits. The
subsequent broader state machine is excluded.

A nonzero current executes EXTU.W on both operands and three SHLL2 operations
on previous. The JSR delay slot at `000290b6` executes the third SHLL2.
The real divider at `00021bbc` executes in place and returns to `000290b8`.
The dividend is at most 64 * 65535; the nonzero divisor is at most 65535.
These unsigned-positive operands select the divider's supported narrow-
and wide-quotient paths. The divider preserves its saved registers and
restores the incoming stack pointer. The quotient then passes the strict
unsigned clamp and a byte store. Zero current bypasses the divider.
The divider does not read the ratio cell. Division-by-zero diagnostics,
negative operands, a full signed-divider contract, and larger divisors are
outside this caller-specific proof.

Reader execution begins at `00029272` and stops at `00029286` or `000292ec`.
A set bit 7 of its incoming status skips the cell read. Otherwise the reader
loads the same cell as one byte, loads ROM8[00008c89] = 118, and zero-extends
both operands. The reader compares unsigned byte > 118.
The following maximum/minimum state-store paths are excluded. The reader
window does not write RAM or seed a previously computed ratio byte.

## Executable proof and exclusions

The named placement/action test is
`tools/mapkit/tests/test_ici0a_ratio_path.py#test_ici0a_ratio_cell_path`.
The legacy byte-cell owner cites it as identity evidence for the bounded
placement/action sites. Its typed base evidence names the load at
`00028f06` and offset `0x6e0`; the accepted L0 separately establishes
that `000290cc` and `0002927c` belong to handler `00028ea2`.
The arithmetic contract test is
`tools/mapkit/tests/test_ici0a_ratio_path.py#test_ici0a_ratio_numeric_contract`.
Neither test inserts owner evidence or changes a knowledge claim's level.

The unchanged PathSh2 executes the retained stock instructions in place.
There are no opcode extensions, stubs, relocations, or computed output seeds.
The caller's incoming register/stack context is explicitly declared. Gate,
mode, previous/current intervals, reader status, prior cell, and unrelated
register state are inputs; the active-path ratio result is computed by the
executed stock divider and writer.

Each window records its incoming registers, stack and RAM, permitted writes,
and boundaries. Executed PCs, delay slots, call/return sites, ROM loads,
RAM inputs, byte/word/long widths, stack restores, and neighboring cells
have fail-closed contracts. The unchanged interpreter refuses an unmapped
read even when a later instruction could write the cell. Producer writes
are limited to the ratio cell, declared gate arming, and the actual stack
save/argument lanes. Reader and fragment-classification windows write none.

The matrix covers zero current, zero previous, unsigned 127/128 and
32767/32768 boundaries, 65535, quotient 255 and saturation beyond it,
all produced byte values, every gate byte, both status-bit outcomes, all
reader status bytes, independent upper register bits, and both nonzero
divider return paths. Exact threshold equality at 118 is false; 119 is true.
Each image executes independently rather than substituting a representative.

Every retained span and image pin has a binding negative. Separate supported
instruction mutants reach the changed instruction or changed-literal load
without running the binding check as their rejection. They distinguish
input widths, gate polarity, the third shift in the call delay slot, writer
width/offset, strict clamp, reader width/offset and unsigned extension,
threshold operands, comparison equality, and divider return/dataflow.
Binding refusal, unsupported instructions, and step limits are not semantic passes.

The evidence covers placement and this bounded integer action. It excludes
full ISR control flow, RTE execution, peripheral capture and the measuring
producer, physical tooth identity, crank degree or time units, every-tooth
runtime, complete gap detection and downstream state updates, interrupt
scheduling and timing, sensor accuracy, actuator behavior, engine validation,
and hardware eligibility. Software gates do not grant flashing approval.
