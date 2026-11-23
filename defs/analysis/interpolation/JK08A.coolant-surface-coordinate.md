# Coolant and raw inner coordinates of the complete composite accessor


## Exact retained association

The original claim is
`67ea4ac6db403b3ab511331bb5458664a609d62ba4ec108af92d838cb2c6288c`:
RAM106F has an indexed_by reader association with primitive 26040. The actual
caller 52576 reads RAM106F at 52582, sign-extends it into R0 and executes EXTU.B
R0,R5 at 52586. RAM10F0 is read at 52588 and supplies R6 in the actual 5258E delay
slot of call 5258C. The primitive contains no fixed RAM106F load.

The second original claim is
`d0df00bf9ee0140245e733faeb242b1b9181608c1d2bd1c6a3854ebfa2fecbfd`:
raw RAM10F0 has an indexed_by reader association with the same primitive.
The actual delay-slot R6 argument supplies this second coordinate. The
primitive contains no fixed RAM10F0 load. Its unit is `raw`; its physical
quantity and engineering scale remain unresolved.

One joint group of 2 ordinary owning operations appends one identity proof to
each reader association. Both complete native owners and both complete
function documents remain fixed. The units `normalized coolant index` and
`raw`, unset semantic widths and signedness, indexed_by roles, original
forward/reverse support and reliance, diagnostic bindings, writers, copies,
inputs, other links, ledgers, evidence and TEST positions remain exact.
The proof grants no new physical units, scale, geometry, scheduling, producer
or hardware admission.

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
