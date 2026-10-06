# JK08A injection start-delay

## Bounded injection start-delay publication

The natural publisher at `7mfk:000521a8` and its quotient and remainder
callees at `00021bbc` and `00021e14` bind 404 instructions, 871 bound bytes,
and 6855 literal cases. The envelope contains 808 instruction bytes and
63 data bytes. Nine high-RAM pointer aliases relocate data addresses for the
simulator; instruction bytes, numeric constants, ROM pointers, helper targets,
delay slots, and natural calls and returns remain byte-identical. The fixture
uses `boundary=False` and executes both helpers without stock-function stubs.

The selected speed R is `uint16(ffff10ca)` when
`uint8(ffff4184).bit6` is set, otherwise `uint16(ffff11bc)`. The coefficient is
`K = floor(uint32(16*R*50331)/65536)`; the first multiplication retains its
low32 wrap. P is the maximum of the six unsigned16 words at
`ffff23d4..ffff23de` and the unsigned16 floor at `ffff241c`.
The pulse fraction is `p = min(255,floor(K*P/65536))`.
With `E = uint16(ffff192e)`, the nonnegative delay is
`D0 = max(0,2*E-4*p)`. If `uint8(ffff24c9).bit5` is set,
`D = max(0,D0-ROM8[0x000083ea])`; otherwise `D = D0`.
The scalar at ROM83EA is an unsigned byte with factory value 30.

Both helpers receive D in `0..131070` and divisor 120. The byte at
`ffff23f0` receives `uint8(floor(D/120))` unless
`uint8(ffff4251).bit0` forces 3. The byte at `ffff23bf` receives
`floor(min(116,max(4,D%120))/4)`. The full quotient register and remainder
accumulator have distinct identities from the stored bytes. Negative
numerators, zero/negative/wide divisors, helper sign correction, and the main
negative-angle adjustment are identity-only within this caller domain.

The 4 arithmetic records in `injection_phase`, steps 9, 10, 11, and 12,
use only this publisher as their proof path. Their sign is `none` under the
admitted full-word and byte-store domains. Executed stock contexts give lead
`0 -> 6` for R `5333 -> 5334`, `255 -> 0` for E `15359 -> 15360`, and
`0 -> 255` for P `0 -> 6`. The first-product and quotient-byte wraps prevent
a universal direction for the lead byte. The angle byte has a separate
periodic remainder: with factory calibration 30, an executed context
stores `29 -> 1` for E `15359 -> 15360`, as D changes `30718 -> 30720`
and D%120 changes `118 -> 0`. The angle is independent of the lead
override. Upper remainder clamps 116 through 120 give the same stored
byte after floor division by 4; this equivalence states no intermediate
register or instruction identity. Address-base relations identify indexed
storage; the base owners are not extra numerical inputs. The unsigned scalar owner
`injection_start_delay_decrement/tbl` belongs to `injection_timing/block`
and states only this conditional reader. The independent reader at `4e03e`
has a separate evidence scope.

The matrix contains 5446 primary-speed and 1409 alternate-speed contexts,
4446 short-helper and 2409 long-helper paths, all 120 remainders,
5610 stock-delay contexts, and 1245 artificial delay-byte contexts.
The control cross-product has 32 cases covering all eight relevant bit
combinations, both incoming T values, and both register contexts.
All three full control-byte domains are represented. Factory calibration 30
permits only even D; odd D uses artificial odd calibration contexts.
The zero-numerator path executes in 1304 cases.

Every literal checks all fifteen GPRs, T and full SR relative to the actual
prepared SR, GBR, MACH, MACL, natural PR/SP, the immutable input context,
both result bytes, every other byte of the 64k RAM image, all 63 data bytes,
the complete frame `SP-64..SP+31`, and an independent external C ABI snapshot.
The prefix preserves MD/RB and other current nonT bits except the explicitly
cleared M/Q state. It records the actual prepared SR before guest GPR loads.
Both frame snapshots share the same origin; the exit capture starts at SP+32.
Short-path low accumulator bits and long-path save locations have independent
literal expectations.

The mandatory owner and registered-stock contracts bind these counts to the
canonical Region, header, harness loop, typed symbols, conditional relations,
and exact instruction/data bytes. The independent arithmetic evaluation uses
the existing Grammar and exact rational values. The software proof covers
this consumer and these helper domains; acquisition, full scheduler
reachability, operating cadence, physical units and calibration purpose,
and hardware behavior require their own evidence.

## Bounded injection result snapshot

The caller slice `00021314..0002131a` and its real byte-copy helper
`00022558..0002258e` bind 32 instructions, 72 bound bytes and
1700 literal cases. Entry registers are explicit: R11=00022558 and
R12=140. The two original pool words identify source `ffff23bc` and
destination `ffff2330`. The natural JSR delay slot supplies length 140.
The helper copies in ascending byte order, checks the limit after each
byte, and returns through its stock RTS and R2-restoring delay slot.
Only the two high-RAM data pointers are aliased for the simulator.

The copy places `ffff23f0 -> ffff2364` at offset 52 and
`ffff23bf -> ffff2333` at offset 3. Native `injection_phase`
steps 13 and 14 state `to = uint8(from)` through the ordered caller and
real helper. The sign is `positive` for the unsigned-byte source domain.
The 6 arithmetic records of the complete chain comprise the four
publisher records and these two copies. They establish no physical scale
or upstream production claim.

The matrix contains 1024 affine caller contexts, 280 isolated-byte caller contexts,
384 direct helper contexts, and 12 successive caller contexts.
Every source position in the affine contexts takes all 256 byte values.
The isolated contexts exercise each of the 140 source positions independently.
Direct calls cover lengths 0, 1, 2, 3, 4, 5, 6, 7, 139, 140, 141 and 255,
all sixteen source/destination alignments, and both incoming T values.
Two register contexts cover both caller T values. Successive contexts
retain the preceding RAM state. A twelve-case preliminary matrix includes
the caller and every early helper exit before full execution.

Every case checks all fifteen GPRs, complete SR relative to the recorded
prepared SR, MACH, MACL, GBR, PR/SP, the immutable 76-byte input context,
the complete 96-byte frame, all 64k RAM bytes, both pool words, and an
independent external C ABI snapshot. Source and neighboring RAM bytes
remain unchanged; only the declared destination bytes receive source bytes.
The helper saves R2/R3/R4 even on its zero-length path.

The simulator boundary at `0002131c` restores PR from SP+24 using R7,
then returns outside all tested instructions. The caller's observed R7
therefore holds the boundary continuation; this is not a stock R7-preservation
claim. Direct helper calls retain incoming R7 and use the natural return.
The existing shared invocation prefix clears M/Q, sets entry T, and preserves
the other observed SR bits. Separate static bytes identify the upstream
R11 helper pool and the R12 length preparation; the executable slice begins
with explicit input registers. Complete scheduler execution, live cadence,
other copy calls, overlapping-source domains, hardware atomicity, and
hardware readiness retain separate evidence.
