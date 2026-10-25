# Coolant coordinate and complete composite accessor

`JK08A.coolant-surface-coordinate-paths.toml` binds 209 stock instructions in
1 actual entry path and 7 spans, 14 literal pools, 2 four-byte RAM pointer
aliases and 16 calibration spans. The complete 52576 entry has 49 instructions.
Its 7 stock entry paths contain 52576, 26040, 26AE0, 263D8, 26770, 26740 and
the complete 26A60 body. The 80-byte context, 572-byte observer and 192-byte
frame preserve 20 independent context fields. All 65536 RAM bytes remain
observable. There are 2 raw input blobs containing 80 input bytes.

## Exact retained association

The original claim is
`67ea4ac6db403b3ab511331bb5458664a609d62ba4ec108af92d838cb2c6288c`:
RAM106F has an indexed_by reader association with primitive 26040. The actual
caller 52576 reads RAM106F at 52582, sign-extends it into R0 and executes EXTU.B
R0,R5 at 52586. RAM10F0 is read at 52588 and supplies R6 in the actual 5258E delay
slot of call 5258C. The primitive contains no fixed RAM106F load.

One ordinary owning operation appends one identity proof. The complete owner,
both complete function documents, unit `normalized coolant index`, unset
semantic width and signedness, indexed_by role, reverse support and reliance,
diagnostic bindings, writer, copy, input, other links, ledger, evidence and
TEST positions remain exact. The proof grants no new physical units, scale,
geometry, scheduling, producer or hardware admission.

## Actual surface coordinates and full returns

The 8x8 byte surface occupies 64 physical bytes at A8EA. The two 26AE0 calls
return an index floor(coordinate/32) and raw fraction (coordinate%32)*2048.
The wrapper clears the fraction when its index is seven. It restores its
saved table pointer, R8 and PR before the actual tail to 26770 with stride 8.

The complete surface kernel retains both row and column fraction branches,
ordered physical corner reads and both directions of the integer equation
first +/- floor(abs(second-first)*fraction/65536). A zero row/column fraction
uses its actual reduced read set. With both fractions zero, MOV.B can return
a sign-extended full R0. The real 52590 instruction extends this return to the
unsigned R14 that supplies the later product.

RAM1222 is loaded as a signed word and extended to unsigned before the
coordinate multiplication 32 and cap 65535. The real 263D8 call receives the
capped unsigned coordinate. Its endpoint threshold is 57344; endpoint returns
are sign-extended words. Other paths execute the complete word kernel 26A60
and tail to 26740. The word curve occupies 8 physical words at 14ED2.
The caller extends the full returned R0 to unsigned16 in R2 at 525AE.

MUL.L at 525B0 multiplies the actual R14 surface byte and R2 word. The full
product in MACL is shifted right by 7, capped at 65535 and stored from full R2
to the actual RAM1652 word at 525CC. The physical quantity of this composite
product remains unresolved. Prior1652 is not read.

## Complete state and independent acceptance

The root allocates 16 stack bytes, preserves R14, PR, MACL and GBR, and restores
R14 in the natural 525D4 RTS delay slot at 525D6. R8-R13 and MACH remain
preserved. GBR is rebased to relocated RAM1068 and restored on the real exit.
The wrapper and surface helper retain their complete saved words and actual
nested call frames. Only T can change in SR; incoming I/M/Q and other controls
remain fixed.

Independent numerical equations require the ordered physical ROM/RAM reads,
real helper arguments, full signed returns, fractions, product and final word.
The instruction-state consumer requires complete CPU, RAM and frame equality,
exact opcodes, natural calls/tails/returns, delay slots and source identities.
Held-other RAM106F alternatives must change the actual 1652 publication through
the real surface result. Input echoes and altered write sets are insufficient.
Independent prior1652 alternatives must preserve the complete final CPU, RAM
and frame. The full byte-surface and word-interpolation caller originals are
mandatory from the identical primary execution.

The existing observer and GNU lifecycle transport complete raw inputs and
observations. Source preparation and local commits do not establish executable
acceptance or native publication.
