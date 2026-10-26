# ICI0A bounded ratio-cell action

## Placement and entry boundary

Image identities and source paths belong to `rom-images/roms.csv`.

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
reader.
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

## Evidence boundary

The model describes placement and this bounded integer action. It excludes
full ISR control flow, RTE execution, peripheral capture and the measuring
producer, physical tooth identity, crank degree or time units, every-tooth
runtime, complete gap detection and downstream state updates, interrupt
scheduling and timing, sensor accuracy, actuator behavior, engine validation,
and hardware eligibility. Software gates do not grant flashing approval.
