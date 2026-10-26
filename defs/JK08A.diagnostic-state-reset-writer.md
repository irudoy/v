# Diagnostic-state reset writer

`JK08A.diagnostic-state-reset-writer-paths.toml` binds 272 stock instructions in 1 entry and 4 spans,
30 literal pools, 6 four-byte RAM pointer aliases and 31 calibration spans.
The closure contains 3 complete functions: the root `2E81A`, its obligatory
`2E76E` callee and its obligatory `CD75C` callee. The internal literal at
`2E780` separates two code spans of `2E76E`. Independent assembly reconstructs
the complete code and every PC-relative pool. Signed native word literals
and the two natural call targets retain their stock bytes. Only declared
four-byte ordinary RAM pointers receive simulator aliases.

The existing ordinary observer uses an 80-byte context, 572-byte observer and
192-byte frame. Its 20 complete context words and all 65536 ordinary RAM bytes
are observed before and after each root invocation. The existing multi-bank
`native_io_before/after` transport records 2304 native snapshot bytes in
3 native snapshot banks: `FFFF8400/256`, `FFFF9900/1792` and `FFFFF500/256`.
The descriptor binds 27 exact native permissions by PC, address or loop
range, access width and mode. The complete snapshots include unused
preservation canaries. Actual ordinary shadows and native publications are
checked separately against independent logical-state and physical-state
views.

`2E76E` clears byte operands at `FFFF9924..FFFF99D3` through its real loops,
writes `FF` at `FFFF2B96`, and clears bit 5 at `FFFF4232` in its real RTS
delay slot. The root then clears `FFFF99F4..FFFF99F9`,
`FFFF99DC..FFFF99F3` and `FFFF99D8..FFFF99D9`. It applies `3F` to
`FFFF9A6B`, clears `FFFF8422/8423/8462/8463`, and applies `EF` to
`FFFF4198`.

The root calls `CD75C` through the real indirect target. Pre-delay `R4` is
two; the real `EXTU.B` delay slot supplies the full unsigned byte loaded
from `FFFF40BE`. The callee retains its complete behavior:

- It clears the declared ordinary byte, word and long operands and both
  byte ranges `FFFF30B2..FFFF30D1` and `FFFF30D2..FFFF30F1`.
- Its ordered byte masks include `FE` at `FFFF4251`, `FB` at `FFFF41DE`,
  `BF` at `FFFF41F2`, `7F` at `FFFF41FC`, `FD` at `FFFF41FE`, and the
  separate mask sequences at `FFFF41B9`, `FFFF41BA`, `FFFF41BB`,
  `FFFF41E1` and `FFFF41F5`. It clears the two native bytes at
  `FFFF9F08/9F09`.
- Bit 6 of `FFFF41E1`, after the real preceding `DF` mask, selects the
  native halfword path. An enabled path writes `u8(ROM[8DFC])*125` at
  `FFFFF588/F58A`, `u8(ROM[8DFD])*125` at `FFFFF58C/F58E`, and zero
  at `FFFFF590/F592/F594/F596`, in the exact instruction order. It then
  clears bit 6 at `FFFF41E1`. An inhibited path preserves all those
  native halfwords.
- The signed byte loads, unsigned byte extensions, full multiplication
  carriers and MACL values remain visible in the independent intermediate
  equations. The callee restores its saved full MACL, GBR and R14.

The root clears `FFFF40BE`, applies `FE` at `FFFF41DE` and `9F` at
`FFFF41A4`, and clears `FFFF2985`. Its real outer frame saves R14 at
entry SP minus four, PR at entry SP minus eight, and GBR at entry SP
minus twelve. The callee saves R14, MACL and GBR at entry SP minus
sixteen, twenty and twenty-four. Every four-byte save and restore, the
complete surrounding frame, both real calls, all return addresses and
the outer RTS-delay R14/SP restore are admitted together.

The numerical specification independently describes the final byte clears,
combined masks and native halfword products. Separate manually declared
instruction-carrier equations describe every intermediate CPU, SR, GBR,
PR, MACH, MACL, stack and ordered physical operand. Both must agree with
the stock byte-surface reconstruction and the actual complete exit and
snapshots. All 13 conditional sites require both outcomes, including every
loop boundary and the native halfword gate. Every feasible instruction
and real delay slot is required.

The selected writer is the single byte-zero store at `2E84A` to
`FFFF99DE`. It occurs at zero-based loop iteration two, with the full R14
store carrier equal to zero. Its physical PC, mode, address, width,
register, value, pointer and counter are bound to that real loop. All raw
target priors `0..255` are required with every other complete input fixed
on both native halfword paths. The final target byte is always zero;
different final outputs are not an obligation of this constant writer.
Every nonzero prior changes in the actual native snapshot, while the
separate ordinary shadow retains its original value.

The optional native products have their own obligations: all raw values
of each physical ROM byte occur with every other complete input fixed,
and the actual paired halfwords follow the unsigned product equations.
Complete raw read-byte preimages, ordinary state, native canaries, code,
pools, aliases, consumed source bytes, terminal streams and pinned GNU
toolchain identities are required by the same original capture.

The retained original is
`939c9a3b6a4bbc89b4d0183a02aa6bcbe3024a8716b51676cd36dca5eb9e487a`:
`rare-butterfly/ram` has a writer relation to `amber-wildcat/fn`.
This exact relation receives one identity-support evidence append. The
complete owner and all three functions, other readers and writers,
symbol evidence, ledgers and TEST origins retain their recorded facts.
Native width and signedness remain unset; the existing unit remains
`raw`. Physical operand ranges supply no native object geometry, unit
conversion, natural caller, scheduling or peripheral side-effect
qualification. Hardware qualification requires the project bench and
live-data evidence.
