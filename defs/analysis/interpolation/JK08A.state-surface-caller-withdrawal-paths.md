# JK08A state surface caller withdrawal

Source bindings: `JK08A.state-surface-caller-withdrawal-paths.toml`.


## Complete state and arithmetic boundary


ROM8B3F bit16 selects the state comparison mode. Both1082/1083 byte loads
sign-extend before the actual unsigned32 comparisons. A lower1083 value
selects the surface path, a greater value selects the split path, and equality
preserves the outputs. With bit16 clear,244F bit64 selects the surface path;
otherwise2450 bit32 selects the split path; otherwise244F bit1 selects the
implicit curve. The remaining path preserves every prior publication.

The surface path copies raw3373 to1873 and writes65535 to13DE. It clips1082
to1..4 and1083 to0..3, then reads exactly one byte at
B60A+4*(clipped1082-1)+clipped1083. That byte publishes to1861 and enters
the last byte of a four-byte local argument. The real26084 wrapper reloads
all four local bytes at caller_SP-24 before EXTU.B. The preceding three bytes
retain their complete incoming frame values. The independent physical sequence
binds both the one-byte store at6486C and the full word load at2609A, their
order, exact SP positions, registers and the post-delay26944 entry argument.

The wrapper supplies data B5FA..B60A, four raw byte knots at11FE2..11FE6
and four at11FDE..11FE2. Raw11AE and the selected local byte are the two
coordinates. A backward scan selects the rightmost qualifying knot. A strict
interior bracket is positive even for unordered raw knots: every later knot
has already failed the coordinate comparison. No global monotonicity premise
narrows the byte inputs. Real26C78 divides the bounded fraction numerator;
real26770 and26740 perform the selected zero-, one- or two-dimensional byte
blend with their complete calls, stack saves and signed endpoint promotion.
The final EXTU.B result multiplies unsigned3373 and publishes its word to13DC.

The split path clips1083 to1..4 and reads the corresponding raw byte at12B62.
Its unsigned-byte product with3373 shifts by8 using the exact SHLR8, SWAP.W,
EXTS.B and XTRCT sequence, then publishes a byte to1873. The unsigned
remainder3373-published1873 multiplies the raw byte at11FF2+index and writes
13DE. ROM8799 multiplies3373 and writes13DC. Every input cell is independent.
The products are at most65025, and floor(a*b/256)<=b. The negative adjustment
at6493E..64944 and the residual clamp at64960 are therefore unreachable.

The implicit path clears1873 and clips1083 to1..4. The raw byte at
11FE6+7+clipped1083 multiplies3373 and writes13DE. The full unsigned40C6
word multiplies literal2D0E, shifts logically by15, subtracts32 and clips
to0..255. The real26370/26A80 byte path reads eight raw cells at11FE6.
Coordinates below224 interpolate adjacent bytes with a32-unit step; coordinates
at or above224 execute the natural signed MOV.B endpoint return at26380.
The caller applies EXTU.B, multiplies3373 and publishes13DC. The shared16-byte
preimage11FE6..11FF6 binds the eight curve cells and both distinct four-byte
state/residual arrays without granting an owning map geometry.

All working modes publish13DC at64A04 with R0=0x150. The natural return at
64A10 restores GBR, MACL, PR, R14 and R13, including the final delay-slot pop.
The unchanged mode retains every output preimage and its actual returned R0.
The source requires 28 two-sided conditions and 4 fixed conditions. The29
excluded instructions are the16 instructions before the actual26A80 entry,
the seven word-cell sibling instructions, the two zero-divisor instructions
and the four caller instructions excluded by the exact unsigned product bounds.
All excluded bytes remain bound in the complete source fixture.

## Physical causality and complete native postimages

Fixed-other alternatives require changed actual R0 or final bytes at a common
real computed publication outside the controlled RAM input. Complete CPU, SR,
RAM, frame, calibration and bound preimages remain fixed. Input echoes,
unchanged common values and a changed write-set alone fail. Every raw surface,
packed selection, axis, implicit curve, state factor and residual cell remains
independent. Both selected ROM roots require physical interval absence for
every access direction and domain label. No replacement identity is inferred.


Full actual-original, independent arithmetic, raw state/axis/byte products,
local-byte/full-word carrier, implicit endpoint, CPU/SR/RAM/frame/physical/
call/delay/return/causal/native/prior/full-function/type/role/TEST/ledger/scope/
review and published-count refusals remain mandatory. Source preparation grants
no executable acceptance, owning replacement, reverse donation, geometry,
scale, units, natural-caller reachability or hardware admission.

The complete byte-factor caller boundary is specified in
`defs/analysis/arithmetic/JK08A.byte-factor-caller-withdrawal-paths.md`. All121 preceding full
records,current images and64 complete functions remain exact. An additional
complete function transition removes one individually pinned reverse writer
selector;the preceding two transitions,row79,row99,eight writer identities
and eighteen indexed_by originals remain exact. Both real byte curves,signed
word promotion,partial products and the percentage delay-slot store are required.
