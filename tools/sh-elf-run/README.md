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
marker. The installed simulator has no instruction-trace or PC-profile
support; the contract does not publish a directly observed helper-call count.

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
