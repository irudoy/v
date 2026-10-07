# GNU SH-ELF firmware instruction verification

This directory is the mandatory independent executable gate for every firmware
patch that changes instruction bytes. It uses the GNU SH-2E assembler, linker,
and instruction-set simulator in a pinned Debian container rather than Ghidra
p-code.

The default gate is fully repository-contained. Verification of the separate
npkern project is optional, external, and revision-locked.

## Repository-contained gate

Run the complete current runtime gate from the repository root:

```bash
make verify-firmware
```

The first run builds the image defined by `Dockerfile`; later runs reuse Docker
layers. The runner selects the `default` Docker context without changing
the caller's configured context.

`VQ_SH_ELF_IMAGE` selects another compatible local image name.
`VQ_SH_ELF_SKIP_BUILD=1` skips the image build only when that image was already
built from the current Dockerfile.

The gate performs these checks:

1. Assemble every current Map Switching, Rolling Launch, and CAN telemetry
   source unit with GNU `sh-elf-as --isa=sh2e`. This covers the canonical JK08A
   units and every rendered JK00C, JK00D, JK78C, 1ND0A, 1ND3B, and 1ME3B
   target unit. A unit that includes a generated header of `patches/`, as the
   telemetry capture and control units include the profile identity
   `can-telemetry-identity.h`, reaches the assembler with the integer symbols
   of the header written as numbers; the telemetry harness compiles with
   `patches/` on its include path and installs the configuration record
   `TELEMETRY_CONFIGURATION` of the same header.
   Targets without a declared capability have no synthetic stage or payload.
2. Reconstruct each fill-aware ROM envelope and require byte identity with the
   corresponding SHA-locked payload in the tracked manifest.
3. Independently compose the current non-flashable capability-specific
   fixtures for JK08A, JK00C, JK00D, JK78C, 1ND0A, 1ND3B, and 1ME3B and
   enforce their declared write sets, entries, hooks, pointers, mailbox record,
   stock-image identity, and stage hashes. The SH7058 images are one MiB; the
   SH7059 1ND and 1ME3B images are 1.5 MiB.
4. Execute every declared Map Switching selector, adapter, limiter, startup,
   feedback, Rolling Launch behavior, telemetry HCAN1 initialization, control
   polling, runtime enable overrides, capture, bank publication, page request,
   ACK, abort, preemption, corruption, and ISR path with distinct fixture
   values that expose wrong slots or addresses. The 8MFK cases include both
   CVTC target families, the two-byte-aligned throttle limiter container,
   mailbox 26, and the stock-ISR tail chain. The 1ND cases include both fuel
   banks, both warm-idle banks, the shared cold-idle family, native fuel-cut
   caps and curves, the exact stock fuel-cut state machine, the throttle
   scalar, Rolling Launch final-mask coordination, mailbox 26, and the stock-ISR
   tail chain. JK78C executes the same VQ37 capability cases through its
   independent SH7058 addresses, stock hooks, RAM sources, and checksums.
   1ME3B executes them through its own SH7059 addresses with the target bit
   layout: the native fuel-cut state byte keeps the active and armed flags in
   bits 3 and 2. The ASCD cases of every target set the MAIN switch bit of the
   ASCD flag byte at the position of its layout: bit 7 on JK08A, JK00C, and
   JK00D, bit 4 on JK78C, bit 5 on 1ND, and bit 1 on 1ME3B. One selector case
   and one Rolling Launch gate case set every other bit of the byte, which
   neither aborts the selector nor fails the gate. The Rolling Launch
   fuel-cut flag cases set the active cut bit of the stock RPM fuel-cut state
   of each target: bit 2 on JK08A, bit 6 on JK00C and JK00D, and the active
   bit of the native rev-limit state byte on the VQ37 targets, bit 4 on
   JK78C, bit 5 on 1ND, and bit 3 on 1ME3B. One case sets every other bit of
   the byte, and on the VQ37 targets a final mask that inhibits all six
   cylinders, and requires the flag clear; the VQ37 fuel coordinator cases
   require the state byte unchanged. The VQ37 Rolling Launch hold cases run
   the engine and then the coordinator wrapper at engine speeds below, at, and
   above cut and at and below restore in both hold modes and in observe mode,
   and require the request, its latch, and the final mask of each pass: the
   request latches at cut, holds down to restore, releases below it, stays
   released between the thresholds, and latches again at cut; a latch other
   than 1 publishes no request; an abort clears the latch; and activation
   clears a latch left in IDLE at a saturated capture, whose captured speed
   lies between restore and cut. The telemetry knock surface cases set
   the high-detonation bit of the knock surface byte of each target, bit 6 on
   every target except 1ME3B and bit 7 on 1ME3B, whose capture moves it into
   wire bit 6 and clears the other bits of the wire byte; one case sets every
   other bit of the byte and requires wire bit 6 clear. The
   VQ37 ignition cases select all five slots of the two executed 16x16
   surfaces. The 1ND and JK78C cases pass the three equal-byte surfaces of the
   gated coordinator half, which the 1ME3B coordinator does not carry, through
   the adapter while a non-default slot is active. The harness
   names those three bases by the placeholders `0x0000991a`, `0x0000e91a`, and
   `0x0000ea1a`, which the target renderer rewrites to the profile symbols
   `ignition_gated_surface_1` to `ignition_gated_surface_3`. The 1ND and 1ME3B
   targets add the adapter of the four 8x8 state-code ignition surfaces: every slot and
   both invalid selector values of each family, plus one unknown base that must
   reach the stock 8x8 lookup unchanged. The harness names the four bases by
   the placeholders `0x0000f610`, `0x0000f710`, `0x0000f690`, and `0x0000f6d0`,
   and the stock 8x8 lookup is a return stub of the dynamic fixture. The three
   targets differ in adapter count and entry count; each
   marker carries its own values, and the verifier sums the case counts the
   markers report.
5. Apply only the documented simulator transformations after exact byte
   identity succeeds: high-RAM data-literal relocation and explicit stubs for
   unchanged stock callees outside the implementation under test. The Rolling
   Launch fixture uses a deterministic, PC-relative-alignment-aware stock
   serializer stub to seed the CAN payload before executing both feedback
   layers. The VQ37 fixture stubs the stock final-mask fuel coordinator with a
   deterministic routine that publishes a distinct base mask to the aliased
   final-mask byte and returns that byte zero-extended, so the wrapper return
   path is executed against an exact expected value. The telemetry fixture
   replaces the stock knock slice evaluator of every target with a stub that
   stores a staged 32-bit value at a staged address, counts the call, and
   overwrites `r0..r7`. The harness stages the offset-binary metric of the
   evaluated channel through the block at `0x0100ff00` of the test window, so
   a knock margin wrapper that reads its operands before the stock call, or
   that relies on a register across it, fails the case. The telemetry fixture
   also installs a simulator-only TRAPA vector after byte identity is proven.
   TRAPA creates the architectural exception stack. The canonical combined
   SLE1 ISR returns through its unchanged `RTE` instruction. Each 8MFK wrapper
   restores all interrupted registers, including `r0` in the `JMP` delay slot,
   and tail-chains to an explicit simulator-only `RTE` stub for the unchanged
   stock ISR. The same tail-chain boundary is executed for the VQ37 mailbox-26
   wrappers.
6. Execute the exact unsafe delayed-branch incident words at their ROM addresses
   and require an illegal-instruction stop, while a control fixture that changes
   only the delay-slot word returns normally.
7. Execute the stock instruction regions whose behavior the entity files state
   (`verify_stock_code.py`). The JK08A MAF ADC slice reconstructs both unsigned
   word reads, the six-bit logical shifts, and the two word stores, including
   the return delay slot. The immediate MMIO-base prologue stays byte-bound
   outside the slice; the harness supplies its mapped R4 context and relocates
   only the declared output-window pool word. Independent bank values, signed
   word boundaries, discarded low bits, maximum counts, read-only MMIO, and
   neighboring output bytes have literal expectations.
   The MAF scaling fixture reconstructs the complete bank-selected publisher,
   coefficient guard, and unsigned Q1.15 scaler at their stock addresses.
   Cases execute both banks, bit3 guard bypass, inclusive coefficient bounds,
   reset to the stock ROM word, the raw-full-scale increment after scaling,
   unsigned product truncation, word saturation, and MACL preservation in the
   scaler's return delay slot. Only five declared RAM pool words are aliased;
   the bounds, reset word, call targets, and tested instructions stay stock.
   The publisher's final signed cap comparison follows EXTU.W, so its taken
   branch is unreachable from the function entry. Explicit direct entry supplies
   a wide R5 and the producer's saved return frame to execute both outcomes
   without changing tested instructions. These branch cases establish no
   reachable ADC state or physical meaning for the coefficient bypass mode.
   A separate battery fixture reconstructs its complete publisher and the
   same guard and scaler. Literal cases distinguish the raw word copy, input
   byte truncation after the two-bit shift, and final byte cap from the MAF
   word contract. They exercise both coefficient modes, all bound edges,
   input byte wrap, signed-word boundaries, and byte saturation without a
   full-scale increment. Six declared RAM literals alone are aliased. The
   stock publisher restores GBR and PR, and the harness also checks MACL,
   mode and source preservation, and every neighboring output byte.
   The MAF compensation fixture reconstructs the complete bank-indexed
   preprocessor and unsigned divider. First-call cases bind masks 1 and 2 to
   bit0 and bit1 and preserve the sibling bank and other flag bits. Initialized
   cases check the unsigned 32-bit numerator's split products, the saturated
   previous-word denominator, quotient truncation, and modulo-65536 output.
   Five successive calls per bank retain the literal sequence 200, 172, 169,
   168, 168 for K=0x00180000. The stock bias 80 prevents a zero denominator
   from the function entry; explicit entry at its zero test supplies the full
   saved frame and checks the raw+1 word alternative. Direct divider cases
   cover the short quotient, wide divisors, and zero-divisor fault record.
   Four declared RAM literals alone are aliased. Every tested instruction,
   natural return, calibration word, mode byte, and read-only input remains
   stock; MACL, GBR, and saved R12/R13/R14 are checked after execution.
   The MAF transfer fixture reconstructs both lookups and word publications,
   including bank 2's store in the BSR delay slot. The complete implicit
   64-point word wrapper, its eight-shift body, and unsigned linear finisher
   retain their stock addresses and returns. Literal cases check both curves,
   low-12-bit input truncation, 16-count cells, fractional truncation, unsigned
   cells, both interpolation directions, argument wrap, and the sign-extended
   last-cell return whose caller stores only the word. Direct body cases
   execute the byte-cell alternative with explicit format context. The
   unchanged following callee 0x0003b320 executes only its stock zero-selection
   path and natural return; its other calibration-selected paths gain no
   execution claim. Four declared RAM literals alone are aliased. After both
   word stores and that callee, the boundary at 0x0003a950 restores PR from
   stack offset zero outside all tested instructions. Cases check MACL, GBR,
   the input base, both input words, stock tables, and neighboring RAM.
   The MAF filter fixture reconstructs the complete bank-indexed working copy
   and first-order filter. It executes both unsigned word copies and outputs,
   byte argument truncation, bit5 copy/weighted selection, stock coefficient
   26/256, floor rounding, and the one-count rising correction. Five successive
   filtered calls per bank retain the literal sequence 101, 192, 274, 347, 413
   for input 1000 from zero. The copy's cap and negative-value branches are
   unreachable after EXTU.W; direct entry supplies wide R2 values. With stock
   coefficient 26, a lower input makes the weighted result strictly below the
   previous word, so the downward anti-stall branch is also unreachable from
   the function entry. Direct post-arithmetic entry supplies input, previous,
   and weighted words plus the saved GBR/MACL frame to execute both corrections
   and both skip paths. These cases establish no live calibration or physical
   time constant. Three declared RAM pool words alone are aliased. All stock
   instructions, coefficient data, natural returns, input words, flag bits,
   sibling-bank values, MACL, GBR, saved registers, and neighbors are checked.
   The per-bank contribution fixture reconstructs 345 instructions across
   the complete MAF producer and its six-shift signed division helper.
   Both banks execute active correction and fallback modes, byte-truncated
   bank arguments, all inhibitor combinations, nonzero latches, unsigned
   word inputs, signed correction histories, word clamps, and residual signs.
   Literal cases distinguish truncation toward zero at /8, /512, and /256
   from floor at the final /64. Fallback cases distinguish low-32-bit
   multiplication before logical shifts from an unbounded weighted sum.
   Wide reference inputs and fixture-only weight variants cover software
   boundaries without asserting live reachability. Explicit post-base entry
   at `0x0003b042` supplies a complete saved stock frame and local state to
   execute otherwise unreachable signed 24-bit residual bounds and the
   active output cap; all tested instructions and natural returns stay stock.
   Repeated calls keep external references fixed and exercise producer-owned
   correction state; they establish no scheduler cadence or physical scale.
   Five declared RAM pool words alone are aliased. MACL, GBR, saved registers,
   inputs, sibling state, mode bytes, calibration, and neighbors are checked.
   The combined-MAF fixture reconstructs the complete 22-instruction sum.
   It executes signed bank contributions, sign-extended correction words,
   unsigned auxiliary words, 32-bit wrap at every addition, and the signed
   zero clamp after the final sum. Literal cases cover the largest positive
   longword, the smallest negative longword, positive and negative overflow,
   and cancellation of signed and unsigned words. Both RAM pool words alone
   are aliased; natural return and GBR restoration execute unchanged. Cases
   check the returned and stored longword, preserved registers, all input
   bytes, and output neighbors. They establish no live overflow or physical
   identity of the auxiliary term.
   The primary BFS fixture reconstructs 378 instructions across speed
   selection, split-product arithmetic, Q7 compensation, and the complete
   unsigned divide and remainder helpers. Positive signed aggregate selects
   the primary calculation; zero or negative values publish zero. Normal
   mode selects either unsigned speed word by bit5; alternate incoming mode
   uses eight times its cached speed byte. Each count is clamped to at least
   64. The product after /256 retains 40 bits, and a zero denominator selects
   the fixed cap without recording a helper fault. Literal cases cover stock
   coherent aggregate bounds, explicit wide-product wrap, unsigned division
   boundaries, final factor 9163/65536, Q7 coefficient extremes, output
   saturation, and mismatched cached quarter BFS. Those explicit contexts
   establish no full-entry reachability or live calibration claim.
   Seven declared RAM pool words alone are aliased. Independent GNU assembly
   binds 828 bytes; the decoded static test additionally binds pre-entry
   context for 930 bytes in total. The boundary at `0x0003b908` restores PR
   from SP+24 outside tested instructions, before the rate stage. Cases
   check the stock cache/register result, source words, coefficient, flags,
   neighboring RAM, and ROM coefficients. The helper restores the external
   C frame after recording the stock slice's register and MACL changes.
   The fallback lookup and final BFS publication remain outside this proof.
   The BFS limiting fixture reconstructs 163 instructions across the bit7
   selector, both corrected working-word paths, implicit byte lookup, direct
   diagnostic grid, and exact word publication. All 256 coordinate bytes
   execute for the stock limit curve and explicit rising/descending patterns.
   Cases retain directional floor increments, signed correction truncation,
   the zero clamp, below/equal/above cap, natural last-cell signed return,
   byte argument wrap, diagnostic row and throttle-column boundaries, and
   zero above the grid's speed range. Explicit word-format body entry covers
   the shared cell-width branch without claiming that the byte wrapper uses
   word cells. The pre-entry ROM mode mask and correction cache association
   are statically bound; the preceding producers do not execute here.
   Six declared RAM pool words alone are aliased. Independent GNU assembly
   binds 400 bytes; the decoded static test binds 509 bytes. The boundary at
   `0x0003bc80` restores PR from SP+0 after the tested BFS word store. Cases
   check MACL, GBR, the publication pointer, all source bytes, the normal cap
   byte's preservation in diagnostic mode, tables, and neighboring RAM.
   The Q7 load fixture reconstructs the 32-instruction normalization slice
   and its unsigned divider. Entry R5 contains the preceding unsigned BFS
   word; a separate byte proof binds its stock load and preservation. Cases
   execute the cached saturation check, explicit word reread, both division
   delay slots, byte publication, stock reference 27226, word/reference
   boundaries, and the zero-reference fault record. Artificial mismatched
   cache/RAM inputs distinguish the cached cap from the second quotient's
   low-byte store; they establish no reachable race. Direct divider cases
   execute the wide-divisor path outside the word-only normalization entry.
   Only three declared RAM pointers are aliased. The boundary at 0x0003bd5c
   restores PR from SP+0 outside all tested instructions. Cases check saved
   registers, MACL, GBR, R11, the reference word, inputs, and neighboring RAM.
   The load-snapshot fixture reconstructs the scheduler's two BFS history
   stores and complete 28-byte copy call. The unchanged length dispatcher
   selects 0x0002213a through its stock table entry; its JMP delay slot loads
   the last source longword before the seven descending longword stores.
   Cases cover all source bytes, word and byte sign boundaries, independent
   patterns, unchanged source and guards, and three successive snapshots.
   Five declared RAM pool words alone are aliased. The copier returns through
   its natural RTS and R3-pop delay slot; the boundary at 0x00020f1c restores
   PR from SP+0 outside tested instructions. The helper frame is shared with
   the normalization fixture. This proof covers the length-28 selection and
   byte-zero view, without a complete scheduler, other copy lengths, or
   hardware atomicity claim.
   The JK08A axis-search fixtures reconstruct the
   byte and word kernels and their unsigned fraction divider. Cases use the
   stock fuel, ignition, and torque row axes and independent literal offsets
   and fractions. They check clamping, exact points, unequal intervals,
   quarter-count coordinates of the byte kernel, unsigned word boundaries,
   both divider outcomes, output guards, and read-only axis data. The byte
   kernel multiplies each stored point by four; the word kernel compares
   the stored unsigned word directly. Both return through stock instructions.
   A separate direct-byte fixture searches both main CVTC axes without a
   point multiplier, including the forced maximum load coordinate. The
   implicit eight-point fixture uses the stock injection and cold-timing
   curves and checks byte argument truncation, flat and fractional results,
   and the sign-extended last-cell return that callers convert to unsigned.
   Synthetic ascending and descending byte and word arrays exercise both
   cell-width branches and both linear interpolation directions. The direct
   shared-body calls remain below the wrapper's last-cell boundary. These
   fixtures preserve all tested instructions, original pools, and stock
   returns, with no RAM-literal relocations or stock-function stubs.
   The JK08A crank-capture fixture reconstructs
   the word read of OSBR1, capture-history update, initialization branches,
   and both period stores. The earlier MMIO-base load and its signed pool
   word stay bound outside the executable slice; the harness supplies the
   mapped base in R11. Cases check the first-sample sentinel, preserved flag
   bits, zero intervals, unsigned word wrap, both signed-word transitions,
   the read-only MMIO window, and neighboring RAM.
   The JK08A tooth-period fixtures reconstruct
   the conditional normalization and ordinary copy as separate instruction
   spans, with their original pool data between them. The harness supplies
   the base registers, current interval, and masked synchronization snapshot
   from the prologue's entry state. It checks the fixed-point approximation
   on positive multiples of three, unsigned word boundaries, independent
   reference and tooth intervals, and unchanged input windows.
   The fallback quotient fixture reconstructs the stock caller and unsigned
   divider, checks the newly published interval rather than the preceding
   interval, and checks both word stores across quotient overflow. Its
   simulator boundary restores PR from a prepared stack slot after the
   stock JSR replaces it; the restoration and return lie outside all tested
   instructions. The boundary refuses misaligned or unsupported stack
   offsets, overlap with pool data, and use with a natural stock return.
   The JK08A event-interval slice
   `0x00028afa..0x00028b41` retains the producer's mode, holdoff,
   subtraction, unsigned wrap adjustment, divide-by-32 publication, marker,
   previous-capture refresh, and returns. Its harness supplies the mapped
   previous-capture pointer in R1; the preceding MOV.W pointer load at
   `0x00028af8` lies outside the executable slice. Its original pointer word
   remains in the reconstruction. The fixture changes only declared
   high-RAM longword pools and preserves all instruction bytes in the slice.
   Expected cases cover both sides of each selector, wrapping and
   nonwrapping differences, equal captures, count boundaries, input and
   window preservation, marker bits, and both stock return paths.
   The JK08A median producer
   `0x0003df2c..0x0003dfc5` and its signed divider
   `0x00021bbc..0x00021cd5` share an independent reconstruction at their
   stock addresses. The harness checks every strict order and ties of
   three unsigned samples, history shifting, quotient truncation and byte
   saturation, a zero period with a nonzero retained median, and diagnostic
   copying without a history update. Direct divider entries cover positive
   and negative operands, short and long divisors, and zero recording.
   Only declared RAM pool words are aliased; both functions retain their
   stock returns. The history and output windows retain all other bytes,
   and the mode, source, and period inputs remain unchanged.
   The JK08A primary RPM producer
   `0x00038272..0x0003829d` and its unsigned divider
   `0x00021ce0..0x00021dc5` share an independent reconstruction at their
   stock addresses. The harness takes the mode flags, event interval,
   output word, and divider entry from the meaning files. It executes
   inhibit selection, zero-divisor recording, quotient truncation,
   saturation, and the unsigned word/longword divisor boundary. Direct
   divider entries also exercise the short-quotient branch, its boundary,
   and the maximum unsigned return value. Only the declared high-RAM
   pool words change in the simulator; both functions return through their
   stock instructions. The output window and mode flags retain all other
   bytes, and zero division writes the stock diagnostic record.
   The JK08A region `0x0003e1fe..0x0003e26b`
   contains the enabled non-fault arithmetic of the RPM-drop producer.
   Its GNU reconstruction links on `0x0003e1fc`, with two padding bytes
   outside the region, to preserve PC-relative longword alignment.
   `stock_invoke_gbr` supplies the aliased `satisfied-macaque/ram` address
   as GBR. The harness takes current speed, four-sample-old speed, and the
   preceding filter snapshot from the meaning addresses. Reviewed expected
   literals distinguish rising speed with nonzero history, equal speed,
   falling speed, truncation, and saturation; every neighboring byte stays
   unchanged. The only simulator changes are the high-RAM pool word and the
   RTS/NOP boundary at `0x0003e26c`; the arithmetic instructions stay stock.
   Mode selection, history shifting, and publication are outside this slice.
   The JK78C region `0x000fcbb0..0x000fcbed` of the
   ASCD task `0x000fb9c0` holds the coolant flag and the MAIN switch block.
   The verifier links its GNU reconstruction `stock_jk78c_ascd_main.s` at the
   region start and requires byte identity with the stock image for the region
   and the four pool words that it loads. The fixture aliases the two high-RAM
   pool words, places an RTS/NOP pair at `0x000fcbee` directly after the
   region, and keeps the region bytes stock. `stock_invoke.s` calls the region
   with R12 set to the stock pool literal that `0x000fc9ca` loads and with GBR
   0, as the stock firmware runs. The harness takes the address of
   `ascd_state/ram`, the mask of its named bit `main`, and the address of
   `button_state/ram` on the layout from the entity files and executes every
   branch outcome: the button source, the alternative source that bit 7 of the
   calibration byte `0x0000894f` selects, which the harness sets in the fixture
   for two cases and then restores, and both outcomes of the coolant threshold.
   Each case requires the MAIN bit to follow its source, the other bits of the
   flag byte to keep their values, and every other byte of the flag window to
   stay unchanged. The JK00C function `0x00050bf8..0x00050c99` and the JK00D
   function `0x00050bf4..0x00050c95` are the main RPM fuel-cut state machines
   of the two relocated 8MFK layouts. The reconstructions
   `stock_jk00c_rpm_fuel_cut.s` and `stock_jk00d_rpm_fuel_cut.s` hold each
   function and the five pool words that it loads; the fixture aliases the two
   high-RAM pool words, and the function returns through its own RTS, whose
   delay slot restores the GBR that it saves. The shared harness
   `stock_rpm_fuel_cut_harness.c` takes the address of `fuel_inhibit/ram`,
   the masks of its named bits `armed` and `active`, the engine speed word
   `rpm/ram`, and the threshold table `rev_limit_fuel_cut/tbl` from the entity
   files, and the delay counter, the pair selector, and the configuration and
   delay bytes, which no entity file names, from the region. It requires the
   stock configuration to select the pair by bit 4 of the selector, reads the
   thresholds from the fixture, and executes both pairs: speed below, at, and
   above the cut-on word with the arm clear and set, a zero and a nonzero cut
   delay counter, a nonzero delay byte that the harness sets in the fixture for
   one case and then restores, and speed at, above, and below the release word
   with the cut active. Each case requires both named bits, the delay counter,
   and the return value, the other bits of the state byte to keep their
   values, the engine speed word, and every other byte of the window around
   GBR to stay unchanged.

A successful run prints `VQ_SH_ELF_MAP_SWITCHING`,
`VQ_SH_ELF_ROLLING_LAUNCH`, `VQ_SH_ELF_ROLLING_VERIFY`,
`VQ_SH_ELF_CAN_TELEMETRY`, `VQ_SH_ELF_CAN_TELEMETRY_VERIFY`,
`VQ_SH_ELF_RUNTIME_TARGET`, `VQ_SH_ELF_RUNTIME_TARGETS`,
`VQ_SH_ELF_STOCK_CODE`, and `VQ_SH_ELF_VERIFY` markers with `status=PASS`. The markers calculate current
instruction, case, branch, relocation, and composition values at runtime; this
document does not duplicate them.

The target payload registry is a tracked product of the same pinned GNU
toolchain. Rebuild it after an intentional target-source or address-profile
change with:

```bash
make runtime-targets-generate
```

## Main fuel compensation

The JK08A main-compensation region reconstructs 301 instructions and 962 bound
bytes at their stock addresses. Its 3494 cases cover the full surface/bypass
selector, all column bytes, every row-axis breakpoint and adjacent coordinates,
endpoint clamps, four distinct surfaces, directional rounding, column-first
interpolation, the three bounded bypass sources, and exact byte publication.
Direct wrapper calls cover word/byte argument truncation and sign-extended
exact-cell returns; direct unsigned-divider calls include a zero denominator.
The static contract additionally binds the preceding input-base and cached-RPM
loads, for 996 bytes whose individual corruptions are rejected.

The tested slice begins at `0003c1c0`, joins the surface at `0003c284`, and ends
after the `ffff1160` byte store at `0003c29c`. Byte row-axis points are multiplied
by four; column-axis points are direct bytes. The two axis kernels return a cell
and truncated Q0.16 fraction. The byte finisher interpolates columns in each
active row before rows, with separately truncated ascending and descending
increments. Both zero fractions permit a sign-extended exact-cell return; the
coordinator publishes its unsigned low byte.

The simulator aliases only the three declared RAM pool words after exact byte
comparison. An external return continuation at SP+4 leaves the column argument
byte at SP+3 intact and restores PR beyond the tested instructions. The table,
axes, control bytes, source RAM, neighboring bytes, cached RPM, input base, MACL,
and GBR are checked for preservation. Explicit surface/control patterns are
simulator input contexts. Preceding writers and physical mode identities are
outside the executable slice; engineering scales retain their existing levels.

## External npkern gate

Run the external gate separately:

```bash
make verify-npkern
```

Or request it after the repository-contained gate:

```bash
tools/sh-elf-run/run.sh --with-npkern --verbose
```

The default checkout is `../../oss/npkern` relative to this repository.
`VQ_NPKERN_SOURCE` may point to another checkout, but `run-npkern.sh` requires
that path to be the Git root, at the exact revision embedded in the script, and
completely clean. It does not fetch, clone, select a mirror, or modify the
external project.

If the checkout is absent, the external command reports `status=SKIP` and
`hardware_ready=NO`. A wrong revision, nested Git root, or dirty tree is a hard
failure. The repository-contained gate remains independent of npkern
availability.

The npkern verifier builds exact-address SH7058 and SH7059 CAN targets in
read-only and explicitly write-enabled configurations, executes parser,
ISO-TP, and flash-boundary fixtures, checks production-to-simulator byte
identity outside declared relocation literals, and verifies the unchanged
legacy SH7058 K-line target.

### Factory loader ABI

The CAN targets load through the factory reprogramming services `0x27`,
`0x34`, `0x36`, `0x37`, and `0xBF` of the stock diagnostic dispatcher, in that
order. The dispatcher selects each service handler with a PC-relative `mov.l`
from its literal pool:

| ROM | Dispatcher | SID | Literal-pool entry | Handler |
| --- | --- | --- | --- | --- |
| JK08A | `0x0002F928` | `0x27` | `0x0002FB44` | `0x00033578` |
| JK08A | `0x0002F928` | `0x34` | `0x0002FB5C` | `0x00034410` |
| JK08A | `0x0002F928` | `0x36` | `0x0002FB3C` | `0x000345F4` |
| JK08A | `0x0002F928` | `0x37` | `0x0002FB40` | `0x0003469C` |
| JK08A | `0x0002F928` | `0xBF` | `0x0002FB38` | `0x0003475C` |
| 1ND0A | `0x00035098` | `0x27` | `0x00035290` | `0x00039278` |
| 1ND0A | `0x00035098` | `0x34` | `0x00035294` | `0x0003A200` |
| 1ND0A | `0x00035098` | `0x36` | `0x000352C8` | `0x0003A494` |
| 1ND0A | `0x00035098` | `0x37` | `0x000352CC` | `0x0003A55C` |
| 1ND0A | `0x00035098` | `0xBF` | `0x000352C4` | `0x0003A624` |

`tools/tests/test_npkern_can_verifier.py` reads every row from the registered
stock image, requires the entry to hold the handler, and requires a `mov.l`
between the dispatcher entry point and the literal-pool entry to load it. Each
target in `verify_npkern_can.py` spans the loader-owned window from `origin`
to `boundary`, and its `aligned_limit` is that window rounded down to 32
bytes; the same test holds the relation.

## BFS rate state

The JK08A rate-state fixture reconstructs 310 instructions and 678 bound bytes
across the rate arithmetic, latch/timer coordinator, signed correction,
optional blend, natural six-shift helper, and diagnostic-record predicate.
Its 461 cases cover both unsigned 15-bit paths, product and word saturation,
same-value increment, latch boundaries, timer combinations, every mode-byte
value, independent inhibitor combinations, signed rounding and clamps,
weighted publication, and the natural word-sentinel query.

The caller passes R4=-1 in the query's JSR delay slot. The unchanged predicate
returns zero for that signed word regardless of diagnostic-record contents.
Its active third timer therefore decrements toward zero. Eight explicit
post-query entries at `0x0003BA6A` supply artificial zero or nonzero R0 values
to execute both timer arms; nonzero results establish no stock reachability.
Isolated correction and blend entries retain separate register-context scope.

Seven declared high-RAM pool words alone are aliased. A boundary outside the
tested code at `0x0003BB86` restores PR from SP+24 through R1, preserving the
cached R5. Cases compare all eight output states, read-only RAM, calibration,
32 bytes of fragment stack, and distinct before/after C-ABI register states.
Fragment register observations remain separate from the containing function's
entry and return contract. The static test binds 734 bytes, including the
preceding cache/flag/base loads, and rejects every single-byte corruption.
Published counts derive from the registered region and emitted execution
marker. The optional exact-PC observer below adds per-context helper-call
counts through the same registered execution API and byte-bound fixture.

## Knock threshold lookup

The registered JK08A knock-threshold fixture reconstructs 184 instructions
and binds 635 bytes, including the stock selector, six rows, word axis and
last neighboring word. Its 829 cases execute the complete accessor and its
word-axis wrapper, search, divider and unsigned linear finisher through
natural stock returns. Factory calibration is checked before artificial
selector, table or axis contexts. Every stock knot, adjacent coordinate and
interval midpoint is exercised for all six rows.

The accessor requires a one-based channel in 1..6 and contains no channel
guard. Its result is stored at the selected word; natural R0 is twice the
channel and R2 holds the threshold. Descending interpolation truncates the
positive decrement before subtraction. The last-cell path still reads the
following word even with zero fraction, so that word is bound too.

Only three high-RAM pool words are aliased. Cases compare the full aliased
RAM outside the selected output, sibling words, calibration and stack
footprints. Stock preserved registers and the external C caller ABI have
distinct before/after observations. Comparison, count publication, metric
production, reference learning, physical channel identity and engineering
scale are outside this executable slice. The detailed contract is in
[`JK08A.knock-detection.md`](../../defs/JK08A.knock-detection.md).

## Knock timing-state selection

`jk08a-knock-state-selection` binds 70 instructions, 208 bytes and 11615
literal cases: 7671 explicit post-lookup entries and 3944 standalone
alternative entries. The direct path computes widened signed R2 from the
signed target word and `256*(H-(uint32(R0)&127))`. The alternative path slews
the target within source +/-1280, applies the unsigned-byte floor -256*N
and caps at zero. Normal gate bits select these paths; standalone entry
executes only the alternative arithmetic.

The first lookup and second lookup are not executed. Static anchors bind
their tables, call/delay pairs and bases; explicit contexts supply their
operands. The second mask and stack byte store execute. All low7 differences,
both widened overflow directions, every gate byte and negative-bound byte,
valid slew/floor/cap neighbors and unreachable floor outcomes are checked.
Six RAM pool aliases leave the instruction words unchanged.

Every case checks full literal register exits, T/MACL, SP/driver PR, the
64-byte frame, separate external C ABI, all calibration/context bytes and
all other RAM bytes. The output publication slots are preserved. Natural PR
from the preceding lookup, full coordinator execution and hardware behavior
remain outside the proof. Separate conversion composes the low-word wrap
and signed-byte result without a joint execution claim or signed monotonic
claim across wrap. The narrow contract is in
[`JK08A.ignition-state.md`](../../defs/JK08A.ignition-state.md).

## Knock event correction publication

`jk08a-knock-event-publication` binds 26 instructions, 76 bytes and 8754
literal cases. Explicit RAM contexts supply signed S/W/C; the full
independent incoming R6 supplies P in 0..65535. The widened signed32 sum
S+W is published to `ffff1ff8`; the signed byte at `ffff12d6` is
`max(-128,min(127,S+W+C-P))`. Subsequent arithmetic retains the shared
register sum without RAM readback. The separately seeded `ffff1ff6` word
is preserved and supplies no numeric input to this slice.

Cases cover signed extrema, word-range crossings and both clamp edges.
Every case checks both publications, T, general/special registers,
SP/driver PR, the entire frame, independent C ABI, all calibration/pool
bytes and every other RAM byte. The natural R13 anchor at `0004da7c`
and other exact base anchors are not executed; the driver supplies their
register contexts. Declared high-RAM pool aliases preserve all checked
instructions. Full builder execution, timer/latch behavior, P production,
bypass paths, full-function return, cadence and hardware behavior remain
outside the proof. The narrow contract is in
[`JK08A.ignition-state.md`](../../defs/JK08A.ignition-state.md).

## Knock event retard

`jk08a-knock-event-retard` binds 63 instructions, 147 bytes and 7408 literal
cases. Explicit RAM contexts exercise all four combinations of Q (RAM flag
bit5 or bit2) and G (ROM mode bit5). K, A and B are signed bytes; H is the
unsigned high byte of the source word. Q0 writes -A; Q1/G0 writes min(K,-A);
Q1/G1 writes min(K-H,-B). With G1 the companion is -B for Q0 or min(K,-B)
for Q1; G0 preserves its complete prior word.

Stock mode `0x7c` and artificial mode contexts are labelled separately.
There are 3605 stock-mode and 3803 artificial cases. In the 3676 G0 cases the
companion retains the complete prior word through the no-store branch.
Coverage includes signed boundaries, high/low word contamination, independent
RAM bits and all ROM mode bytes. Every case checks output/retention, T, all
general/special registers, SP/driver PR, the full 52-byte frame, independent
caller ABI, all calibration/pool bytes and all other RAM bytes. Four RAM pool
aliases leave checked instruction words intact. The ordinary return boundary
at `0004da2a` is outside stock spans. Full builder mode reachability, timer/latch
behavior, producer identities, later summation, cadence and hardware behavior
remain outside the proof. The narrow contract is in
[`JK08A.ignition-state.md`](../../defs/JK08A.ignition-state.md).

## Knock event integration

`jk08a-knock-integration` binds 39 instructions, 114 bytes and 4035 literal
cases: 3967 event entries and 68 quiet entries. Independent event R4 is in
0..255; the 32-bit MUL.L consumes it without an in-fragment EXTU.B. RAM count
is seeded independently. The event result is signed saturation of S-307*R4;
the quiet result is signed saturation of S+13. Both clear the RAM count and
are alternative entry views, not sequential updates or a dispatch inference
from R4=0.

All byte counts, signed state boundaries and in-domain saturation transitions
are covered. MACL contains the event product or retains the quiet input.
Per-case checks bind the working arithmetic register, T, all general/special
registers, SP/driver PR, the full 52-byte frame, independent C caller ABI,
calibrations and all other RAM bytes. Five RAM pool aliases preserve all
checked instruction words. The ordinary return at `00049582` is outside
stock spans. Separate static dispatcher checks at `0004952c/0004952e` do not
execute the dispatcher or quiet predicate. Complete coordinator modes,
cadence, producer lifecycles and hardware behavior remain outside this proof.

## Knock timing-byte conversion

`jk08a-knock-timing-byte` binds 16 stock instructions, 48 bytes and 65650 cases.
The cases comprise all 65536 low words and 114 literal cases with independent
upper words. Entry `0004964a` sign-extends the incoming R2 low word to R12;
the delay-slot store publishes the raw word to `ffff121a`. The sign-dependent
255 adjustment and logical shift/reconstruction publish the signed byte
`trunc0(int16(ffff121a)/256)` to `ffff22fa`.

The two R9 anchors and their pools bind the explicit `ffff22f8` base without
executing its producers. Pool `000496c8` is the sole high-RAM alias. The return
boundary at `000496da` lies outside tested instructions. Per-case checks cover
outputs, neighbors, all general/special registers, T, SP/PR, the complete
52-byte frame, independent caller ABI and calibration/context anchors.

Every literal case checks all other 64k RAM bytes. Full RAM is observed at each
256-case sweep block boundary; the sweep does not assert full per-case RAM
observation, and compensating writes within a block remain outside snapshot
coverage. Both fixed stock stores have checked bases and outputs. Complete
coordinator modes, preceding calculation, cadence and hardware behavior remain
outside the bounded conversion proof.

## Knock threshold comparison

The registered JK08A comparison fixture reconstructs 314 instructions and
binds 963 bytes. Its 1100 cases contain 1048 comparisons and 52 direct shift
contexts. The comparison executes the natural threshold accessor and its real
word-axis, divider and linear helpers before the strict unsigned predicate
`metric > 0x80000000 + threshold`. Equality clears the condition. Selected
channels are `1..6`; metric production and the caller's channel-zero guard are
outside the bounded entry.

Status bit 6, the local byte at SP+12, the selected bitmap bit and the saturated
event count are checked independently. Legal shifts `0..5` execute the real
bitmap helper; isolated cases cover `6..7`, negative counts and counts `>=32`.
Positive shift counts `8..31` are outside this executable envelope. Stock and
artificial mode-byte contexts, every legal channel, strict predicate edges and
count boundaries retain separate literal expectations.

Eight high-RAM pool words alone are aliased. Cases check the full remaining
RAM, sibling metrics and thresholds, calibration, a 52-byte frame and distinct
fragment/C-ABI observations. Nested saved words include the wrapper/linear
tail slot, which holds the left cell on descending paths. The boundary at
`0x0004A386` restores driver PR from SP+16 through R1 outside tested code.
Reference learning, complete evaluator dispatch, physical timing and hardware
behavior are separate from this proof. The detailed contract is in
[`JK08A.knock-detection.md`](../../defs/JK08A.knock-detection.md).

## Optional exact PC observation

`Dockerfile.pctrace` builds a separate GNU16.3 simulator with a small host-only
observer. The default Dockerfile, runner and registered firmware gates retain
their existing contracts. The observer records the fetched instruction word
at its actual PC, including the actual delay-slot PC. It does not alter guest
registers, operations, memory, ROM or fixture bytes, and successful observation
preserves host errno. Observation is disabled unless explicitly requested.

The source archive is GNU's official
`https://ftp.gnu.org/gnu/gdb/gdb-16.3.tar.xz`, SHA256
`bcfcd095528a987917acf9fff3f1672181694926cc18d609c99d0042c00224c5`.
Use its existing ignored directory as the named `gnu-source` build context;
do not commit the archive or extracted tree. The recipe checks that archive,
the reviewed patch, and both pristine and modified `sim/sh/interp.c` digests.
It retains and compares the original assembler, compiler and simulator binary
digests while adding `/opt/gnu-sh-trace/bin/sh-elf-run`.

Build the primary stock image by its existing recipe, then build the separate
optional image from the repository root. Set `GNU_SOURCE_DIRECTORY` to the
existing directory containing the exact `gdb-16.3.tar.xz` archive.

```bash
docker --context default build \
  --build-context "gnu-source=$GNU_SOURCE_DIRECTORY" \
  --build-arg STOCK_IMAGE=vq-sh-elf-run:16.3 \
  -f tools/sh-elf-run/Dockerfile.pctrace \
  -t vq-sh-elf-run:16.3-pctrace .
PC_IMAGE_ID=$(docker --context default image inspect \
  --format '{{.Id}}' vq-sh-elf-run:16.3-pctrace)
```

Use the immutable ID for every validation command and preserve the resulting
reports in ignored output directories. Create each output directory empty
before its command; the tools refuse an occupied retained directory.

```bash
mkdir -p tmp/pc-observation/probe tmp/pc-observation/bfs
docker --context default run --rm --network none \
  --mount "type=bind,source=$PWD,target=/workspace,readonly" \
  --mount "type=bind,source=$PWD/tmp/pc-observation/probe,target=/observation" \
  --entrypoint python3 "$PC_IMAGE_ID" \
  tools/sh-elf-run/probe_pc_observation.py \
  --image-id "$PC_IMAGE_ID" --output /observation
```

The probe independently assembles the stock seven-instruction signed helper
at `0x000224fa`, binds its bytes to the SHA-locked JK08A ROM, and requires two
exact ordinary/return/delay PC sequences. Original simulator, observation
disabled, filtered observation and unfiltered observation must produce the
same values and errno result. Ten malformed or unwritable requests must stop
with exit 125. The report records the immutable image ID supplied by the host,
the actual simulator and linked ELF digests, and the trace digests.

Before using observations from an image as an assertion, run the complete
primary repository-contained GNU gate in that same image:

```bash
docker --context default run --rm --network none \
  --mount "type=bind,source=$PWD,target=/workspace,readonly" \
  "$PC_IMAGE_ID"
docker --context default run --rm --network none \
  --mount "type=bind,source=$PWD,target=/workspace,readonly" \
  --mount "type=bind,source=$PWD/tmp/pc-observation/bfs,target=/observation" \
  --entrypoint python3 "$PC_IMAGE_ID" \
  tools/sh-elf-run/verify_bfs_pc_observation.py \
  --image-id "$PC_IMAGE_ID" --output /observation
```

The BFS command delegates fixture identity, compilation and all 461 cases to
the primary `stock.run_region` API. It pins the dedicated assembly, harness,
literal case order, named Region contract, native harness bindings and the
invoker's own function block. Unrelated Region or invoker additions remain
permitted. Linked ELF markers and actual wrapper bytes bind the observation
after relocation. Every helper opcode, complete sequence and delay flag must
match stock bytes.

The trace separates 461 caller frames. Literal assertions check 20 correction
contexts and 7 blend contexts individually, covering zero, one and two helper
calls with 38 checked helper entries. The other 434 frames retain observed counts
without count assertions. A whole-run total cannot substitute for these
per-context expectations. Arithmetic outputs, RAM, calibration and ABI checks
continue to belong to the unchanged primary harness.

The observer's opt-in environment is `VQ_SH_PC_TRACE_FILE` plus
`VQ_SH_PC_TRACE_FORMAT=v1`. Optional `VQ_SH_PC_TRACE_RANGES` contains up to 8
comma-separated hexadecimal half-open `low:high` ranges. The tool selects only
the helper and compiled invoker ranges to avoid tracing the C RAM loops.
Unsupported requests, open/write/close errors and zero selected records fail
with exit 125. `pc_observation.py` accepts only raw ASCII bytes, exact LF syntax,
one header, one terminal complete footer, the exact positive record count and
a zero process exit. Pure refusal tests run through ordinary pytest discovery:

```bash
uv run pytest -q tools/tests/test_sh_pc_observation.py
```

This optional observer establishes direct invocation counts under the declared
execution contexts. Hardware eligibility still requires the mandatory byte,
execution and hardware validation contracts. Build logs, source archives,
ELFs, binaries, traces and observation reports remain ignored.

## Bank base-pulse builder

The stock Region `jk08a-bank-base-pulse` executes the complete natural
function at 0004ead4..0004eba2: 103 instructions, 232 bound bytes and
6184 literal cases. The natural RTS and MACL-restoring delay slot remain
exact. Only three high-RAM pointer longwords are simulator aliases; the
ROM pointer and arithmetic constant FFFF3800 remain unchanged.

Both legal bank selectors use independent full R4 upper bits and raw
unsigned16 RAM inputs. The gate covers conditional LTFT inclusion,
both control choices, strict control threshold, lower trim clamp, low32
product, unsigned offset wrap, zero-precursor bypass and cap equality.
Factory and artificial calibration/software contexts remain distinct.
Full machine-domain decreases prevent positive signs in the six shared
chain views.

Each case checks literal output and all fifteen GPRs, final T, complete
observed full SR, natural special-register/PR/SP restoration, distinct
external C ABI, the entire 80-byte frame, every other RAM byte and all
bound calibration/pool bytes. The SR setup retains GNU MD/RB and all
other nonT bits, reads actual SR after LDC, and verifies their preservation.
Stock saved GBR/MACL occupy SP-8/SP-4; capture above SP+32 does not
overlap the SP-48..SP+31 observer.

`defs/JK08A.fuel.md` section `Bounded bank base-pulse builder` owns the
explicit inputs and arithmetic. Named owner and registered-stock
contracts in `tools/kb/tests/test_bank_base_pulse_chain.py` bind this
publication to its actual registered Region, literal array, harness loop
and result marker. Caller dispatch, upstream production, live operating
states, physical units and hardware mapping remain separate evidence.

## Simulator boundaries

GNU `sh-elf-run` cannot map the ECU high-RAM windows. The gate first proves the
original literal bytes, then aliases validated `0xFFFE8000..0xFFFFFFFF` data
literals into a 64-KiB test window by their low 16 bits. Instruction bytes and
control-flow addresses remain unchanged. This covers both the SH7058
`0xFFFFxxxx` application RAM and the SH7059 1ND and 1ME3B `0xFFFExxxx`
application RAM.

HCAN status registers are write-one-to-clear in silicon but ordinary memory in
the simulator. Canonical simultaneous mailbox-26/mailbox-28 ISR cases place the
two flags in independent TXACK1 and ABACK1 words, so both mailbox paths execute
in one TRAPA exception without modifying instructions under test. The 8MFK
and VQ37 tail-chain cases exercise mailbox 26 alone and together with unrelated
stock mailbox-28 flags, then verify the target wrapper's register-preserving
stock-ISR boundary.
Individual ACK and abort cases execute each custom write-one-to-clear
instruction and boundary path. Mailbox-31 cases likewise execute RXPR1, RFPR1,
and UMSR1 writes, including data, remote-only, retained-remote, malformed, and
invalid-configuration paths; the fixture observes the write values rather than
emulating their hardware clearing effect.

The simulator does not model HCAN-II, the SH7058/SH7059 flash controller, or the
external watchdog. The 1.5-MiB target harness places its test driver beyond the
complete ROM image; this relocation affects only harness code, not target
instructions. The npkern marker therefore remains
`hardware_ready=NO`. Repository firmware fixtures also do not emulate the full
ECU, power sequencing, analog inputs, or engine.

Passing this gate proves a bounded software execution contract. It does not
make an image eligible for flashing without static review and the project's
bench, readback, and engine validation gates.

## Adding an instruction-changing patch

The same change that introduces a patch must extend this gate. Its verifier
must:

1. Independently assemble the source or reconstruct declared raw words and
   prove identity with the exact instructions emitted into the ROM.
2. Execute every changed entry and reachable branch outcome, including delay
   slots, call/return paths, failure paths, and relevant boundary inputs.
3. Use distinct fixture values where equal production defaults could conceal a
   wrong address, slot, width, or branch.
4. Declare simulator-only relocations and stock-function stubs, apply them only
   after byte identity, and leave instructions and control-flow addresses under
   test unchanged.
5. Add deterministic host-side tests and make `run.sh` execute the new
   repository-contained check.

A simulator limitation is not a waiver. Until an equivalent executable check
exists, the image remains ineligible for hardware testing.

## Bounded JK08A knock reference learning

`jk08a-knock-reference-learning` executes the complete RAM-only learner
and the real diagnostic predicate through natural stock calls and returns.
The exact-stock envelope binds 132 instructions, 304 bound bytes and
7336 cases: 264 instruction bytes and 40 data bytes, comprising 36 pool bytes and 4 calibration bytes.
The source is `stock_jk08a_knock_reference_learning.s`; a separate
`stock_knock_reference_learning_invoke.s` enters through the shared
invoker. The original literal result marker matches the Region key and
case count. Guest instructions, branch/delay slots and result text retain
their reconstructed bytes.

The ordered KB definitions supply the reference bank, unsigned sample
vector, two channel bytes, diagnostic-record base, selector byte, weight
byte and reset word. Five validated RAM pool words are aliased after
independent GNU byte comparison. The real predicate address, all other
pool values and calibration bytes retain stock identity. The fixture
uses no stock-function stub or synthetic boundary return.

The matrix contains 5256 normal learning cases, 540 forced reset cases and 1540
direct predicate cases. There are 5796 natural learner calls.
Stock calibration supplies 2015 stock normal cases and 18 stock forced cases,
totaling 2033 stock natural cases. The normal legal
channel domain is 1..6 with eight uint16 samples/old words and byte W.
The coefficients W and 255-W divide by 256; only q<old adds one.
The complete domain has q<=65279 and result<=65280, so it cannot take
the final upper clamp. Forced reset publishes the raw reset word to all
48 reference words across six rows. Artificial calibration cases remain
distinct from stock contexts.

Each case checks all fifteen GPRs, actual final SR.T, special registers,
natural SP/PR, a distinct external C ABI and the 80-byte observed frame
around the 36-byte natural save footprint. All 64k aliased RAM and all 40 bound
pool/calibration bytes are checked. Normal learning permits only the selected
16-byte reference row to change; forced reset permits the 96-byte reference bank; direct
predicate calls permit no RAM changes. Independent expectations cover
all 42048 normal output words and all 7336 register/flag vectors.
SR is not injected and non-T preservation is outside this fixture.

The two real diagnostic ids are 012d and 013f. Both bit7 outcomes,
short-circuit/reset branches, all record bytes, independent R4 upper
words and the low-word-ffff sentinel are covered. Static acquisition and
caller anchors remain separate from this execution. Other signed diagnostic
indices, complete record-array extent and hardware behavior are outside
this bounded proof. Physical sensor and
channel identity, diagnostic producers, acquisition, timing, engineering
units and full evaluator dispatch are not established by the bounded
RAM-only proof. The narrow mechanism contract is
`defs/JK08A.knock-detection.md#bounded-knock-reference-learning`.

## LTFT publication

The registered GNU16.3 Region jk08a-ltft-publication executes the
complete publisher at 57B26 with its second span at 57BD4..57C34 and real
predicate at 25E20..25E44: 108 instructions, 268 bound bytes and
12028 literal cases. Natural RTS/delay slots remain stock. Eight
high-RAM longword pools are aliases; the three words, both ROM pointers
and real helper pointer remain unchanged. The fixed caller uses id 0129;
the predicate sentinel branch/MOV at 25E3E is identity-only, with no
direct sentinel or independent helper upper-word execution claim.

Both legal banks use full incoming R4 with varied upper bits, independent
uint16 selected/adjustment words, full byte controls and unsigned U versus
signed V. The exact uint32 sum, both limit bypasses, active lower-then-upper
comparisons and all four neutral causes have independent expectations.
Stock and artificial/reversed bounds remain distinct. Full-domain
underflow and low-word wrap prevent broad positive signs in the two
shared publication views.

Each case checks output bytes, all fifteen GPRs and final T, full prepared
SR nonT preservation, natural special registers/PR/SP, distinct external
C ABI, all other RAM bytes and all 52 data bytes. The 80-byte observer
uses matching SP-48..SP+31 origins, with natural R13/R14/PR saves at
SP-4/-8/-12. Independent continuation and capture above SP+32 are
separate checks. RAM/data snapshots are per literal, without block
aggregation; an arbitrary full incoming SR=0/1 is not claimed.

The specification section Bounded LTFT publication defines inputs and
arithmetic. The mandatory contracts test_ltft_publication_chain_owner_contract
and test_ltft_publication_registered_stock_contract in
tools/kb/tests/test_ltft_publication_chain.py bind the exact Region, stock
bytes, independent literal output/T/GPR vectors, typed conditions, scoped
widths and Region/header-array/C-loop publication counts. Missing owners,
registration, header or publication sections fail these contracts.
The shared predicate retains its separate knock-reference direct-context
proof; those cases belong to that fixture and are not LTFT case counts.

Each legal bank has 6014 cases. Each incoming T value has 6014 cases.
There are 8564 factory-bound and 3464 artificial-bound contexts.
The envelope has 216 instruction bytes and 52 bound data bytes.

    raw = uint32(L+A-25600)
    active = ((M&(b+1))==0) and (U>V)
    limited = min(hi,max(lo,raw)) if active else raw
    neutral = diagnostic_byte1.bit7 or F.bit0
              or (G.bit0 and H.bit1) or (K.bit6 and H.bit0)
    output = 25600 if neutral else uint16(limited)

All held notes/properties/evidence and ledger selectors, existing units,
producer interpretations and other layouts are preserved. Caller dispatch,
upstream producers, physical mapping, percentages, timing, live-state
reachability, complete coordinator execution and hardware behavior remain
separate evidence.

## Injection start-delay publication

`jk08a-injection-start-delay` binds 404 instructions, 871 bound bytes, and
6855 literal cases for the natural `521a8` publisher and real `21bbc/21e14`
quotient/remainder helpers. Its envelope contains 808 instruction bytes and
63 data bytes. Nine high-RAM aliases relocate pool addresses while preserving
the instruction bytes, numeric constants, ROM and helper targets. Natural
calls and returns execute with `boundary=False`.

The first selected-speed product retains its uint32 wrap. Full unsigned16
speed, pulse, floor, and end words produce a nonnegative delay; control bit 5
enables a clamped unsigned-byte decrement. Division by 120 yields a quotient
stored through uint8, a clamped remainder byte, and a separate bit-0 forced
value 3. The 32-case control/T/register cross-product covers all eight relevant
bit combinations. The matrix includes 5446 primary and 1409 alternate speed
contexts, 4446 short and 2409 long helper paths, all 120 remainders,
5610 stock and 1245 artificial calibration contexts. The zero-numerator path
executes 1304 times. Invalid helper domains, sign correction, and the main
negative-angle adjustment are identity-only.

Each case checks both result bytes, all fifteen GPRs, actual full SR, natural
PR/SP, GBR/MACH/MACL, every other 64k RAM byte, all 63 data bytes, a 96-byte
frame at `SP-64..SP+31`, and a separate external C ABI snapshot. The prefix
preserves MD/RB, injects T, clears M/Q explicitly, and records actual prepared
SR. Frame origins agree and the exit capture begins at SP+32.

Two unconditional contracts require canonical owners, the registered Region,
exact execution sources, count bindings, and the three arithmetic-only chain
steps with sign `none`. Single-byte mutations are refused across the complete
bound envelope. The unsigned ROM83EA scalar states this conditional consumer.
Physical units, peripheral producers, complete scheduling, and hardware
behavior retain separate evidence requirements.

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
The 6 arithmetic records bound by the publisher and copy fixtures
comprise four publisher records and these two copies. They establish no physical scale
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

## Bounded injection slot construction

The bounded `00054a64..00054ac6` slice binds 50 instructions,
152 bound bytes and 8508 literal cases. Entry contexts are R2=255,
R5=ffff8510, R14=ffff4555 and GBR=ffff1ff4. Four RAM literal aliases
and the corresponding incoming base-register aliases place high RAM in
simulator memory after exact instruction identity. The original 52 pool
and order-table bytes are bound. The entry-preparation bytes at
`00054a56..00054a62` retain static identity; the prologue is not executed.
An appended RTS/NOP at `00054ac8` returns outside the stock slice.

The cylinder input c is an unsigned byte in 1..6. Two fixed stock ROM
lookups at `0002268e` and `0002269b` yield c in this domain. Counter
`ffff4555` saturates at 255. History `ffff1526` ORs `1<<(c-1)`.
Control byte `ffff8513`.bit5 selects unsigned lead `ffff2364` or constant 3.
The negative difference receives one addition of 6 before byte storage.
Cylinder 1, lead 7 and bit5 set stores 255; mathematical modulo-6 yields 5.
For a given c, lead <= c+5 makes the stored byte equal modulo-6 in 0..5.
The uniform bound lead <= 6 covers all six legal cylinder inputs.

The 2 arithmetic records at native injection_phase steps 15 and 16
bind lead and cylinder inputs to slot `ffff20b4` through the sequencer.
They use sign `none` and the exact bounded expression:

```text
F = (uint8(ffff8513)>>5)&1; L = F*uint8(ffff2364)+(1-F)*3; d = uint8(ffff11de)-1-L; to = uint8(d+6*min(1,max(0,-d)))
```

The matrix has 12 early contexts, 6144 enabled-lead contexts,
48 disabled-lead contexts, 2048 full-control-byte contexts and
256 counter-byte contexts. Enabled lead covers 0..255 for each legal c,
both incoming T values and two complete GPR variants. Control contexts
cover all 256 raw byte values, including other bits and sign extension.
Counter contexts cover every byte and both saturation branch outcomes.
EARLY_ONLY=1 executes the first twelve literals; the mandatory Region
uses EARLY_ONLY=0 and requires the complete declared count.

Each case observes all fifteen GPRs, actual prepared complete SR/T,
MACH, MACL, GBR, PR/SP, the immutable 76-byte context, all 96 frame bytes,
an independent outer C ABI, all 64k RAM bytes and every bound ROM byte.
Only counter, history and slot stores may change RAM. This slice has no
stock call, MMIO access or internal frame write. The shared invocation
prefix preserves its accepted instruction bytes and its SR preparation.

Full-byte lead values are explicit consumer contexts. Complete prologue
and tail behavior, upstream producer bounds, live scheduling, physical
cylinder identity and hardware reachability require separate evidence.
This proof does not establish that lead values above six occur in service.

## Bounded injection pending-mask selection

The accepted lookup and two selection entries bind 32 instructions,
80 bound bytes and 9216 literal cases. The direct lookup at
`00054d06..00054d0a` requires slot 0..5 and reads the six stock masks
`02 04 08 10 20 01` at `00022695`. Entry `00054bdc` supplies the
zero-lead-delta context: it clears pending byte `ffff2228`, computes the
next cursor as old cursor+1 below 5 and zero otherwise, and accepts only
a matching target slot. Acceptance stores the cursor and the looked-up
mask. Entry `00054c0e` supplies the negative-lead-delta context and clears
only the pending byte. The boundary at `00054d0c` is outside all three
stock spans; its RTS/NOP adds no sequencer semantics. One RAM literal
and incoming GBR/R14 alone use simulator RAM aliases.

The matrix contains 12 early contexts, 6144 valid-slot zero-delta contexts,
1500 invalid-slot contexts, 1024 negative-delta contexts, 24 accepted
direct lookups and 512 full-cursor extreme-invalid-slot contexts. The
zero-delta and negative-delta inputs cover complete unsigned byte domains;
direct lookup contexts keep the necessary valid table-index bound.
Earlier mode gates and earlier mode exits, positive-delta catch-up, stock
calls and MMIO are outside these spans. Native step 17 retains a separate
complete-selection question; this fixture does not assert that every
sequencer path without an accepted slot clears pending.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires its complete declared count. Each case observes
all fifteen GPRs, actual complete SR including T, MACH, MACL, GBR, PR/SP,
the immutable 76-byte incoming context, all 96 frame bytes, an independent
outer C ABI, all 64k RAM bytes and every bound pool byte. The unchanged
shared invocation prepares the entry and observes the return. Software
execution establishes no live reachability, physical scale or hardware
behavior outside the declared instruction entries.

## Bounded injection reciprocal splitter

The complete `00028e7c..00028e9c` helper binds 17 instructions,
36 bound bytes and 12826 literal cases. It takes a full unsigned 32-bit
input M in R4 and independent word and byte output pointers in R5/R6.
The ROM word `00028ea0` is 6554. The actual operator is
`Q=floor(uint32(6554*M)/65536)` with word Q and byte `uint8(M-10*Q)`.
There is no saturating quotient cap. Both quotient-zero branch outcomes,
the word store in its BT/S delay slot, and the natural return with MACL
restoration in its delay slot execute. No literal or instruction alias
is needed. Prepared output pointers are explicit helper contexts; this
generic fixture does not identify all callers' destinations.

For M in 0..255, Q equals floor(M/10). Larger operands can differ through
reciprocal precision and low-32-bit wrap. The early M=200000 context
executes Q=20001 and residue byte 246. The matrix contains 12 early
contexts, 2816 coarse word-period products, 9450 product-wrap seam
contexts, 512 complete unsigned-byte/T contexts and 36 raw-32-bit corners.
All byte-valued remainders contribute wrap-seam boundaries where present.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires its complete declared count. Each case observes
all fifteen GPRs, actual complete SR including T, MACH, MACL, GBR, PR/SP,
the immutable 76-byte incoming context, all 96 frame bytes, an independent
outer C ABI, all 64k RAM bytes and every bound pool byte. The unchanged
shared invocation prepares the entry and observes the return. Software
execution establishes no live reachability, physical scale or hardware
behavior outside the declared instruction entries.

## Bounded injection argument splitting and phase normalization

The caller at `0002b660..0002b6cc`, its complete phase normalizer at
`00028dc8..00028e7a` and its real reciprocal splitter bind 162 instructions,
350 bound bytes and 12668 literal cases. A=uint8(R4) executes in the
BT/S delay slot on both mode-bit6 outcomes. With bit6 clear, byte-domain
division by ten is exact: initial count is max(0,floor(A/10)-1), and
remainder is A%10 plus ten when the quotient is nonzero. The normalizer
reads raw position byte `ffff13b2` and writes count word `ffff13b8` and
remainder byte `ffff193b`. With bit6 set, A<120 stores count zero and
remainder A; other byte values store count one and remainder A-120.

At position 4 the normalizer maps count 4 to 3 with remainder+10, 5 to 3
with remainder+20, and 6..15 to count-2. At position 9 it maps 9 to 8
with remainder+10 and counts >=10 to count-2 with remainder+20. Other
raw position bytes map 1 to zero with remainder+10, 2 to zero with
remainder+20, 3..12 to count-2, 13 to ten with remainder+10, 14 to ten
with remainder+20, and 15..24 to count-4. Other counts are unchanged.
Byte additions keep uint8 storage while scratch GPRs retain signed
byte extension. This full raw consumer domain does not expand the
physical tooth domain.

The matrix contains 12 early contexts, 2560 normal byte/valid-position
contexts, 1536 fallback contexts, 3328 complete raw-position contexts,
1536 complete control-byte contexts, 288 upper-argument-bit contexts,
32 direct clamp contexts and 3376 direct normalizer contexts. The direct
clamp supplies entry `0002b676` to cover the signed clamp unreachable
after byte truncation. The normalizer uses its natural return. Caller
entries return through a PR restore at stack offset 24 in a boundary
at `0002b6ce`, with R11 as scratch outside the stock bytes. Three RAM
pool words alone are aliased. The prologue, source-argument dispatch,
preceding pending flag and following count decision and MMIO retain
separate evidence. Native step 18 requires composition with those
caller conditions before it gains a complete arithmetic record.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires its complete declared count. Each case observes
all fifteen GPRs, actual complete SR including T, MACH, MACL, GBR, PR/SP,
the immutable 76-byte incoming context, all 96 frame bytes, an independent
outer C ABI, all 64k RAM bytes and every bound pool byte. The unchanged
shared invocation prepares the entry and observes the return. Software
execution establishes no live reachability, physical scale or hardware
behavior outside the declared instruction entries.

## Bounded injection offset multiplication

The `0002b6d4..0002b6f6` multiply and its complete real reciprocal helper
bind 35 instructions, 90 bound bytes and 14118 literal cases. The caller
reads unsigned period word `ffff22bc` and remainder byte `ffff193b`.
It computes M=P*R and passes the actual word output `ffff16c2` and byte
output `ffff166c` to `00028e7c`. The word is Q and the byte is
uint8(M-10*Q). MACL contains M after the helper restores its saved input;
it does not preserve the MACL value before the caller's multiplication.

Native injection_phase step 19 has sign `none`, includes the ordered
caller and real helper, and binds the exact bounded arithmetic:

```text
M = uint16(ffff22bc)*uint8(ffff193b); to = floor(uint32(6554*M)/65536)
```

P=8192,R=4 executes Q=3277 while ordinary division gives 3276.
P=25000,R=8 executes Q=20001 and byte 246. Across full word/byte
consumer contexts the reciprocal product wraps and Q can decrease
when an operand increases. The raw residue is not limited to 0..9.
The matrix contains 12 early contexts, 3328 coarse word/byte products,
9450 wrap-seam contexts, 1280 complete-byte contexts at five word values,
and 48 word-corner contexts. Two declared RAM literals alone are aliased.
The boundary at `0002b6f8` restores PR from stack offset 24 using R11
outside all tested bytes. The preceding zero-count decision, compare
programming, physical timer units and hardware retain separate evidence.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires its complete declared count. Each case observes
all fifteen GPRs, actual complete SR including T, MACH, MACL, GBR, PR/SP,
the immutable 76-byte incoming context, all 96 frame bytes, an independent
outer C ABI, all 64k RAM bytes and every bound pool byte. The unchanged
shared invocation prepares the entry and observes the return. Software
execution establishes no live reachability, physical scale or hardware
behavior outside the declared instruction entries.

## Bounded injection positive-delta mask accumulation

The loop at `00054c54..00054cc6` binds 58 instructions,
138 bound bytes and 11340 literal cases. Its input N=uint8(R6) is a
prepared register context. For N=0 it leaves all RAM unchanged and writes
zero at SP+12 and SP+16. For N>0 each iteration increments the raw cursor
byte `ffff221e`, wraps a resulting byte >=6 to zero, and reads the mask
`02 04 08 10 20 01` at `00022695+cursor`. The final cursor is
`(min(old_cursor,5)+N)%6`. The accumulator ORs the next min(N,6) masks;
N>=6 produces 0x3f. It ORs that accumulator into `ffff20b5`, `ffff157e`
and `ffff16fe`, and clears its bits in `ffff1935`. Upper byte bits in the
four history values are preserved. Signed MOV.B scratch registers retain
their actual full GPR values before unsigned byte storage.

For N>0 the loop saves incoming R9 at SP and restores it, stores N at
SP+12 and stores the accumulated mask at SP+16. Other frame bytes are
held. The boundary at `00054cc8` uses an RTS/NOP outside the stock span.
The two RAM literal bases alone use simulator aliases; incoming R8 is
the stock table base `0002268e`, and incoming GBR is the declared RAM
alias of `ffff1ff4`. ROM instructions, masks and offsets are unchanged.

The matrix contains 12 early contexts, 7168 full-cursor and selected-delta
contexts with both GPR patterns and entry T values, 3072 full-delta
contexts over all six valid cursor values and two GPR patterns, 1024
independent full-byte history contexts and 64 upper-delta-bit contexts.
Every cursor byte and low delta byte occurs. N=0, loop completion,
cursor wrap, repeated complete cycles and both incoming T values execute.
The native owners describe unsigned byte storage and the exact bounded
writer. All 22 complete steps of injection_phase retain their current
bindings. The preceding mode/lead decision, later flag and duration-helper
paths, pending-mask publication, one-shot call, physical channel mapping
and hardware retain separate evidence. These raw direct contexts do not
establish service reachability or the full step-17 selection conditions.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires every literal. Each case observes all fifteen GPRs,
actual complete SR including T, MACH, MACL, GBR, PR/SP, the immutable
76-byte entry context, all 96 frame bytes, a separate twelve-word outer
C ABI, all 64k RAM bytes and every bound ROM pool byte. The original
shared invocation and pinned GNU tools execute the fixture.

## Bounded injection pre-call argument preparation

The mandatory `jk08a-injection-dispatch` Region reconstructs 12 instructions,
38 bound bytes and 9292 literal cases with `EARLY_ONLY=0`. It enters at
00054d0c and observes at 00054d24 before JSR to 0002b64a. The byte at
ffff221d receives uint8(R9). Bit 0 of ffff4251 selects argument 52 when set
and the complete 32-bit word at SP+8 when clear. Other flag bits are retained;
the MOV of 52 executes in the BRA delay slot. R2 holds the stock callee
address at the boundary. Further callee execution has separate evidence.

The stored-word domain includes 4*A for every byte A in 0..255, independent
upper-word contexts and both prepared T values. These are explicit entry
inputs; earlier producer and mode conditions retain their own proof. The
matrix contains 12 early cases, 4096 full-flag cases, 4096 byte-snapshot-word
cases, 1024 previous-lead cases and 64 upper-word cases. Every flag byte and
every previous lead byte is covered. The direct contexts do not establish
caller reachability or all combinations of 32-bit arguments and lead values.

The harness checks all fifteen GPRs and the actual complete SR, MACH, MACL,
GBR, PR/SP, the immutable 76-byte context, 96 frame bytes, an independent
12-word C caller ABI record, 64k RAM and every bound ROM-pool byte. R11 is
the explicit boundary scratch and equals the independently recorded driver
continuation. Fourteen other GPR results bind to the literal matrix. The
frame and RAM checks permit only the stock lead-byte write. The input flag,
saved argument, neighboring frame bytes and other RAM retain their values.

`stock_injection_dispatch_invoke.s` preserves the complete start-delay
observer after a symbol rename and two setup instructions. Those instructions
copy the explicit incoming R4 word into SP+8 before the before-frame capture.
The contract normalizes that insertion and compares the complete remaining
source with `stock_injection_start_delay_invoke.s`. Mutation checks reject
each register result, each bound byte, changed setup offset/source, missing
frame capture, changed Region boundaries and conflicting published counts.

Simulator RAM aliases affect only the declared words at 00054e8c and
00054e9c. The existing boundary stub at 00054d24 loads its continuation
from SP+24 through R11; the interval under test retains its exact ROM bytes.
The pinned GNU tools, image, runner and timeouts remain the standard gate.
The boundary precedes hardware compare and timer accesses; software proof
of argument preparation leaves hardware validation as a separate condition.
