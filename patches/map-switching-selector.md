# JK08A map-switching selector contract

## Scope and status

This specification defines the selector, storage layout, input-compatibility
gate, and patch contract for JK08A. The exact stock image is the protected code
baseline:

```text
rom-images/23710-JK08A/1JK08A-20260726-stock.bin
SHA-256 ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23
```

The patcher also accepts checksum-valid JK08A images whose lower
calibration/configuration partition differs from stock. The complete
`0x20000..0xFFFFF` partition, ROM identity, patch anchors, and erased allocation
must still match the exact baseline.

The target pilot has five slots and eight switchable calibration families. Six
families use fail-closed lookup adapters. The two directly accessed rev-limiter
families use complete RAM shadows refreshed as part of the same atomic commit.
At patch time, Map 2 through Map 5 receive exact copies of the input Map 1
bytes. Selection therefore has no intended control effect before manual tuning.

`map-switching-layout.toml` is the authoritative ROM/RAM allocation and hook
manifest. `map_switching_layout.py` validates exact and compatible inputs and
materializes identical slot storage in memory. `map_switching_selector.py` is
the executable selector, adapter, and limiter-shadow reference model.
`map_switching_assembly.py` validates the source-level address, literal, ABI,
and delay-slot contract for implemented SH slices.
`map_switching_compose.py` validates all locked blobs and applies code,
calibration copies, pointer tables, and hooks to an in-memory image without
exposing an output-file operation. `map-switching-payloads.toml` stores the
seven validated machine-code spans as hexadecimal data.
`apply_map_switching.py` is the output boundary: it validates the input and
payloads, invokes the compatible-input composition, recalculates every JK08A
checksum domain, proves byte preservation outside the declared write set, and
creates a ROM plus MD5 sidecar without overwriting a different file.
`tools/ghidra/EmulateMapSwitchingComposition.java` independently reconstructs
the same complete fixture from the exact Ghidra program and executes every
machine-code scenario against final composed addresses.
`tools/mapkit/map_switching.py` projects the same addresses into the common
JK08A RomRaider and TunerPro definitions.

Seven independent SH units are implemented: the selector host, shared
fail-closed adapter helper, four lookup adapters, startup wrapper, atomic
limiter transaction, CAN serializer wrapper, and feedback pulse engine. Ghidra
12.1.2 assembles and round-trip decodes their 387 instructions and 158 literal
bytes. The source validator restricts all injected code to the 28 used
mnemonics listed for the SH7058S SH-2E core in Renesas REJ09B0177 section 2.4.1;
the SH-2A Ghidra profile cannot introduce an unaudited instruction. Its
SuperH p-code emulators pass 17 selector, 47 adapter, 14
startup/limiter, and nine feedback cases. The seven generated raw blobs are
SHA-256 locked in the layout manifest. Their complete spans are tracked in the
payload bundle; independently rebuilt raw blobs and listings remain
regenerable temporary artifacts. The complete-composition harness passes the
same 87 cases over 4530 instructions, executes all ten declared code entries,
and verifies the locked fixture SHA-256 and write boundary. The patcher extends
this pure composition with input compatibility, checksum recalculation,
non-overwriting file creation, and final preservation checks.

The differentiated candidate
`tmp/1JK08A-20260726-map-sw-tune.bin`, SHA-256
`d61853b7c1f1b2b29d3ccf2a551be8dacebeef65b82b464d0327fc9b11e93e5d`,
has a hardware result of FAIL. PCMFlash reported a successful write, but the
modified ECU did not start the engine and did not identify through PCMFlash.
Installing the stock ECU restored normal engine start on the same vehicle.
On the bench, the modified ECU produces no application CAN traffic, and
PCMFlash module 18 cannot identify, read, or write it. A normal complete
readback is therefore unavailable, and the actually programmed user MAT cannot
be recovered with the available paths. Native SH7058 boot mode is a separate
hardware path through SCI and mode/reset pins, but it does not provide a
pre-erase dump path. Transitioning that mode into its programming/erasing state
automatically erases the user MAT and user boot MAT, as specified by the
Renesas hardware manual. A binary comparison cannot establish the root cause
for this ECU. The pre-fix candidate remains unchanged as a controlled
reproduction image, not as the current runtime release. A replacement ECU must
have a recorded baseline, working recovery path, supply-current measurement,
and complete PCMFlash log before that reproduction write.

The candidate file itself passes the available independent static gates:

- the installed RomRaider `ChecksumALT` implementation verifies 2/2 regions;
- the installed RomRaider `ChecksumALT2` implementation verifies 4/4 regions;
- all seven injected code spans, 15 hook literals, and eight pointer tables are
  byte-identical to the generated map-switching image;
- the 394 differences from the generated image consist of 12 checksum bytes
  and 382 calibration bytes, including the global Cold Ignition edits and the
  manually differentiated slot maps;
- reset-selection bytes at `0x8000`, `0x8080`, and `0xFFF80..0xFFF87` are
  identical in the working, generated, and differentiated images.

The reset-fixed successor is
`tmp/1JK08A-20260726-map-sw-tune-fixed-reset.bin`, SHA-256
`3e37f03a2ac879714556ab720fa657eb4132d1b22ecdccbb2c4edce631842ced`
and MD5 `4985aaec122bd62fd9d636346529a953`. It differs from the pre-fix
candidate at 38 bytes inside the 120-byte upgrade write set: the fallback
zero-fill literal, startup-wrapper span, and recalculated checksum fields.
Every calibration byte remains exact. The installed RomRaider independently
verifies `ChecksumALT` 2/2 and `ChecksumALT2` 4/4. Its hardware status is
untested.

The official PCMFlash module list declares the SH7058 protocol as a one-MiB
`RD/WR/CK` protocol rather than a calibration-only protocol. It does not
publish erase-block selection or post-write comparison behavior. A skipped,
partially programmed, or otherwise corrupted flash block remains possible but
cannot be established without the original PCMFlash operation log or a
readback. No candidate-file difference found in this audit explains the
complete loss of application startup and PCMFlash identification.

The unresolved evidence branches are the actual programming transaction,
board-level power/reset/clock state, and behavior inside the hardware-oriented
initialization calls that the p-code harness must stub. The original PCMFlash
log can establish which address ranges and verification stages the tool
reported. Measurements on the failed ECU can classify a power, reset, clock,
or watchdog failure. A known-working replacement ECU permits staged A/B images
that isolate allocation, startup, selector, and CAN-feedback hooks. The
available evidence does not rank these branches.

## Pilot calibration scope

The pilot contains these independently switched storage families:

| Group | Canonical JK08A table | Stock address | Shape |
|---|---|---:|---|
| Ignition | Ignition Timing Trim Main | `0x09A1A` | `16x16 uint8` |
| Ignition | Ignition Timing Trim High Det | `0x09B1A` | `16x16 uint8` |
| Fuel | Fuel Targets | `0x0B33A` | `16x16 uint8` |
| Fuel | Fuel Compensation Main | `0x0A29A` | `16x16 uint8` |
| Rev limiter | Rev Limit - Fuel Cut | `0x0934E` | `2x2 uint16` |
| Rev limiter | Rev Limit - Throttle Cut | `0x0942C` | `1x uint16` |
| Overrun | Over Run Fuel Cut | `0x12718` | `1x16 uint8` |
| Overrun | Over Run Fuel Restore | `0x12818` | `1x16 uint8` |

The ignition pair is switched together so the high-detonation fallback cannot
remain on a different slot. The two main fuel tables are switched together
because one provides the target projection and the other is a multiplicative
fuel-duration correction. The two rev-limiter objects are switched together
because code places them in separate upper-speed intervention paths.

Scope selection does not promote evidence confidence. The tuner-facing AFR
projection for Fuel Targets and the physical names and scales of the rev
limiters remain candidate evidence. No non-identical values for those objects
may reach an engine image before controlled hardware validation.

The underlying ignition bytes include the timing value in bits 0 through 6 and
the knock-window flag in bit 7. Slot copies preserve the complete byte. Derived
definitions may expose the timing and flag as separate masked editor views, but
both views address the same slot-specific storage.

Cold Ignition Timing `0x0991A`, Stationary Rev Limiter `0x085D9`, the speed
limiter, shared axes, knock sensitivity, VTC/VVEL, sensor models, and diagnostic
objects remain global in the pilot.

Exact-ROM access paths, hook literals, copy allocations, and fail-closed
selection behavior are closed for all eight families at the reference-model
level. The six adapter-backed families have assembled and p-code-emulated
accessors, and both direct limiter families have an assembled atomic shadow
transaction and startup path. The selector and feedback paths are also
assembled and p-code-emulated. Deterministic byte composition is closed for the
locked `10, 10` feedback configuration, including execution of all 87 p-code
cases against the complete composition. The patcher recalculates and verifies
all checksum domains. V36 meter behavior, real selector input, timing, and
engine behavior remain hardware gates.

## Stock input and scheduling anchors

`FUN_000CF020` debounces the ASCD steering-switch ladder and publishes:

| Address | Meaning |
|---|---|
| `0xFFFF2A85` | current stable one-hot code |
| `0xFFFF2A86` | previous stable one-hot code |

The accepted codes are:

| Code | State |
|---:|---|
| `0x00` | released |
| `0x02` | CANCEL |
| `0x08` | SET/COAST |
| `0x10` | RESUME/ACCEL |
| `0x20` | MAIN pulse |

The host task at `FUN_000CE854` executes the relevant stock calls in this order:

```text
FUN_000CF020 -> FUN_000D09D8 -> FUN_000913D0
```

Literal `0xCE8DC` is read only at `0xCE872` and contains
`0x000D09D8`. The host hook changes that literal to `0x000D2108`. The injected
wrapper calls `FUN_000D09D8` first, runs the selector, and returns to `0xCE878`.
The resulting order is:

```text
FUN_000CF020
  -> injected host wrapper
       -> FUN_000D09D8
       -> selector
       -> diagnostic mirror
  -> FUN_000913D0
```

The stock current/previous bytes and P1564 input remain unchanged. A direct
branch at the accepted-state store `0xCF1B2` is not part of the contract:
`0xD2108` is outside the SH-2E `BSR` displacement range from that site.

The wrapper preserves PR around its nested calls. Injected code uses only
caller-saved `r0..r7`; it preserves `r8..r14`, GBR, MACH, MACL, and the caller's
stack layout. At the exact call site, the following `FUN_000913D0` call has no
register arguments, and `FUN_000CE854` reloads or overwrites its later
caller-saved values. No live `r0..r7` value from `FUN_000D09D8` crosses the
wrapper boundary.

`map-switching-selector-host.s` fills `0xD2108..0xD226F` with 168
instructions and 24 literal bytes. Its locked SHA-256 is:

```text
7cc557156f89d764b4e2a224bfc2159fe78e4e519e8645692b9783abbb49472e
```

The host calls the displaced stock function first, validates the published
index, feedback state, selector phase, count, and timeout, blocks input during
valid feedback, and invokes the locked limiter commit only after a complete
gesture. It clears corrupt transient state, mirrors bit 7 of `0xFFFF2A84`, and
never writes the stock input or ASCD control fields.

`EmulateMapSwitchingSelector.java` executes the selector and limiter blobs
together. Its 17 cases cover every phase transition, map 1 and map 5 commits,
timeout, sixth-pulse abort, ASCD abort, active and corrupt feedback, corrupt
selector state, invalid-index map-1 recovery, diagnostic mirroring, and
protected-register preservation. All cases pass over 1471 executed
instructions.

## Selector state

The selector owns eight bytes:

| Address | Field | Reset |
|---|---|---:|
| `0xFFFF5D00` | `active_index` | `0` |
| `0xFFFF5D01` | `phase` | `IDLE` (`0`) |
| `0xFFFF5D02` | `selection_count` | `0` |
| `0xFFFF5D03` | `elapsed_ticks` | `0` |
| `0xFFFF5D04` | `feedback_pulses_remaining` | `0` |
| `0xFFFF5D05` | `feedback_phase` | `IDLE` (`0`) |
| `0xFFFF5D06` | `feedback_ticks` | `0` |
| `0xFFFF5D07` | reserved | `0` |

Indices are zero-based internally:

| User-visible map | `active_index` |
|---:|---:|
| 1 | `0` |
| 2 | `1` |
| 3 | `2` |
| 4 | `3` |
| 5 | `4` |

The selector state is followed by two active limiter shadows:

| RAM range | Purpose |
|---|---|
| `0xFFFF5D10..0xFFFF5D1B` | 12-byte fuel-cut cluster shadow |
| `0xFFFF5D20..0xFFFF5D3B` | 28-byte throttle-limit cluster shadow |
| `0xFFFF5D28..0xFFFF5D29` | selected throttle scalar inside the cluster |
| `0xFFFF1796..0xFFFF1797` | stock throttle runtime scalar, refreshed on commit |

The aligned byte at `0xFFFF5D00` is the publication field. Limiter shadows and
the stock runtime scalar are updated while interrupts are masked, then the new
active index is stored as the final operation before SR is restored. Adapter
lookups therefore retain the old slot until both direct-access shadows are
complete. No partially updated calibration state is observable under this
contract, and no pointer is stored in selector RAM.

Any invalid active index resolves to map 1. Any invalid phase, count, or timeout
value clears the transient state without accepting the current transition.

## Reset default and free RAM

A whole-program `TraceRamAccesses.java` pass covers all 2315 exact-JK08A
functions with zero decompilation failures.

- Resolved application accesses below the stack stop at `0xFFFF5CF9`.
- The only unresolved indexed candidate near the boundary is the loop at
  `0xA842E..0xA8436`. It copies 223 words from
  `0xFFFF9AC8..0xFFFF9C85` into `0xFFFF5B34..0xFFFF5CF1`.
- A focused repeat over `0xFFFF5D00..0xFFFF5D3B` reports zero resolved
  accesses, constant call arguments, and remaining indexed candidates.
- No resolved access, constant call argument, or remaining indexed candidate
  reaches the wider `0xFFFF5D00..0xFFFF6FFF` interval.
- Initial SP is `0xFFFF7FFC`; the candidate state is outside the stack area.

Fallback startup function `FUN_0000284E` clears
`0xFFFF7000..0xFFFF7247`. Literal `0x29CC` is its unique start-address input.
The pre-fix candidate changed:

```text
ROM32[0x29CC]: 0xFFFF7000 -> 0xFFFF5D00
```

The same loop would clear `0xFFFF5D00..0xFFFF7237`; its following loops would
still clear `0xFFFF7238..0xFFFF7247`. This adds 1216 longword stores on the
fallback path and clears a continuous range much larger than the declared
60-byte reservation.

The exact power-on path does not execute this function. `FUN_0000261C` reads
`ROM8[0x8000]=0xFF` and `ROM8[0x8080]=0xEE`, producing `0xFE`, and matches the
header marker `ROM32[0xFFF84]=0x4E4855F9`. It enters TRAPA `0x3E`, whose vector
is `FUN_00027E24`. That handler calls the stock startup thunk and then remains
in its scheduler loop. It does not return to the fallback call of
`FUN_00002B8E`, which is the only caller of `FUN_0000284E`. The candidate and
both comparison images contain identical branch inputs and header marker.

The `0x29CC` hook therefore did not establish a map-1 default on the exact
normal reset path. The current schema-2 layout removes the write and retains
`ROM32[0x29CC]=0xFFFF7000` as a read-only input anchor. The startup wrapper
stores zero to `active_index` before the stock initializer runs, then commits
map 1 after the initializer returns. Startup lookups and both limiter shadows
therefore use map 1 without clearing unrelated RAM.

The Python test named `test_reference_model_defaults_to_map_1` expresses this
required contract through a newly constructed reference-model state. The
source validator separately requires the zero-store before the first JSR and a
second zero before the limiter commit. The exact reset harness below executes
the fixed machine code for all retained selector seeds.

The stock thunk at `FUN_00027CE4` tail-jumps through its unique literal at
`0x27D28`, which contains `0x0002C648`. The literal changes to `0x000D22A0`.
The startup wrapper publishes map 1, calls `FUN_0002C648`, refreshes both
limiter shadows for map 1, updates `0xFFFF1796`, and returns with the caller's
PR and callee-saved registers intact. Every invocation re-establishes the
required reset default.

## Gesture grammar

The selector runs only after the stock five-sample debounce. It observes
transitions from `previous stable` to `current stable`; repeated stable samples
do not increment the count.

Arming is allowed only when `0xFFFF41AE.bit7 == 0`, the exact status source
identified as ASCD OFF. Enabling ASCD while armed aborts the gesture and retains
the active map.

For five slots:

```text
released -> SET                         arm, count=0
SET -> CANCEL -> SET                    count=count+1
SET -> released with count=1            commit map 1
SET -> released with count=2            commit map 2
SET -> released with count=3            commit map 3
SET -> released with count=4            commit map 4
SET -> released with count=5            commit map 5
```

The selector timeout is 100 selector invocations, including the arming
invocation. The wall-clock duration is not claimed because the period of
`FUN_000CE854` has not been measured. Expiration wins over a transition on the
same invocation.

The following conditions abort and retain the active map:

- release before the first complete CANCEL pulse;
- RESUME/ACCEL or MAIN while armed;
- any transition that does not match the current phase;
- a sixth CANCEL pulse with five configured slots;
- timeout expiration;
- ASCD becoming enabled;
- corrupt selector state.

The electrical ladder must produce the direct debounced sequence
`SET -> CANCEL -> SET` while SET is held and CANCEL is tapped. This remains a
hardware gate.

## Free ROM and placement

The last exact-JK08A function is `FUN_000D1F70`, whose body ends at `0xD20FF`.
Words `0xD2100..0xD2107` are its literal pool. The half-open region
`[0xD2108, 0xFFF80)` contains 188024 bytes of `0xFF` and no instructions,
defined data, or function bodies.

The complete fill tail has seven Ghidra `DATA` references. These include
calibration values interpreted as addresses and a computed store reference;
their existence prevents treating the complete fill tail as unreferenced.
The first reference target is `0xE1C2A`. The conservative half-open allocation
region is therefore `[0xD2108, 0xE1C2A)`: 64290 bytes of `0xFF` with no
instructions, defined data, function bodies, or inbound Ghidra references.

The eight-byte record at `0xFFF80..0xFFF87` is preserved:

```text
01 ff ff ff 4e 48 55 f9
```

Bytes after that record are not claimed as free space. The manifest claims the
half-open interval `[0xD2108, 0xD3860)`:

| ROM range | Purpose |
|---|---|
| `0xD2108..0xD226F` | host wrapper, selector, diagnostic mirror, and feedback queue control |
| `0xD2270..0xD229F` | shared fail-closed adapter selection helper |
| `0xD22A0..0xD22FF` | startup and limiter-shadow initialization wrapper |
| `0xD2300..0xD233F` | overrun lookup adapter |
| `0xD2340..0xD237F` | ignition lookup adapter |
| `0xD2380..0xD23BF` | fuel-compensation lookup adapter |
| `0xD23C0..0xD23FF` | fuel-target lookup adapter |
| `0xD2400..0xD247F` | overrun Cut and Restore copies |
| `0xD2480..0xD24FF` | alignment reserve |
| `0xD2500..0xD28FF` | Ignition Timing Trim Main copies |
| `0xD2900..0xD2CFF` | Ignition Timing Trim High Det copies |
| `0xD2D00..0xD30FF` | Fuel Targets copies |
| `0xD3100..0xD34FF` | Fuel Compensation Main copies |
| `0xD3500..0xD351F` | Rev Limit - Fuel Cut copies |
| `0xD3520..0xD3527` | Rev Limit - Throttle Cut copies |
| `0xD3528..0xD353F` | alignment reserve |
| `0xD3540..0xD35DF` | eight five-entry ROM pointer tables |
| `0xD35E0..0xD365F` | CAN 0x551 CRUISE-feedback wrapper |
| `0xD3660..0xD375F` | atomic limiter-shadow commit |
| `0xD3760..0xD385F` | fail-closed feedback pulse engine and frame-count configuration |
| `0xD3860..0xE1C29` | unallocated within the conservative free region |
| `0xE1C2A..0xFFF7F` | fill tail, not allocated by this contract |

Code ranges are fixed envelopes; assembly must fit each entry without changing
the calibration or pointer-table addresses. Unused bytes remain `0xFF`.

`AuditFreeRegion.java D2108 D385F FF` is the reproducible gate for the claimed
allocation interval. `AuditFreeRegion.java D2108 E1C29 FF` additionally checks
the remaining conservative region. Both runs require `status=PASS` with zero
bad bytes, instructions, data objects, functions, and references.

## Verified calibration accessors

### Adapter-backed families

Six families enter stock interpolation wrappers through replaceable function
literals. Each injected adapter recognizes only its approved canonical bases,
selects one pointer from the manifest table, and tail-jumps to the original
wrapper with the incoming PR. Every unrecognized base passes through unchanged.
An invalid index selects map 1.

| Family | Stock base | Stock wrapper | Hook literals | Adapter | Maps 2-5 |
|---|---:|---:|---|---:|---|
| Over Run Fuel Cut | `0x12718` | `0x26388` | `0x4FDD0` | `0xD2300` | `0xD2400`, `0xD2410`, `0xD2420`, `0xD2430` |
| Over Run Fuel Restore | `0x12818` | `0x26388` | `0x50258` | `0xD2300` | `0xD2440`, `0xD2450`, `0xD2460`, `0xD2470` |
| Ignition Timing Trim Main | `0x09A1A` | `0x26230` | `0x496C0`, `0x4E474`, `0x4E58C` | `0xD2340` | `0xD2500`, `0xD2600`, `0xD2700`, `0xD2800` |
| Ignition Timing Trim High Det | `0x09B1A` | `0x26230` | `0x496C0`, `0x4E474`, `0x4E58C` | `0xD2340` | `0xD2900`, `0xD2A00`, `0xD2B00`, `0xD2C00` |
| Fuel Targets | `0x0B33A` | `0x261B8` | `0xC0020` | `0xD23C0` | `0xD2D00`, `0xD2E00`, `0xD2F00`, `0xD3000` |
| Fuel Compensation Main | `0x0A29A` | `0x261F0` | `0x2CF1C`, `0x3C388` | `0xD2380` | `0xD3100`, `0xD3200`, `0xD3300`, `0xD3400` |

The ignition adapter receives Main, High Det, and Cold bases from shared call
sites. It redirects `0x09A1A` and `0x09B1A` only. Cold
`0x0991A` and every other base continue to stock storage. The overrun adapter
likewise leaves the Bosch tables `0x126E4` and `0x1298C` unchanged.

`FUN_0004FBE2` calls the overrun Cut wrapper for Bosch at `0x4FC08` and Hitachi
at `0x4FC16`. `FUN_00050018` calls the Restore wrapper for Bosch at `0x500AC`
and Hitachi at `0x500BC`. These mixed call sites require base discrimination;
redirecting every call would switch the wrong family.

The adapter pseudocode is common:

```text
if r4 is not an approved canonical base:
    jump to stock wrapper with incoming PR

index = uint8[0xFFFF5D00]
if index >= 5:
    index = 0
r4 = ROM32[family_pointer_table + index * 4]
jump to stock wrapper with incoming PR
```

The wrapper-specific input registers and callee-visible state remain unchanged.

### Assembled adapter slice

`tools/ghidra/AssembleSh2.java` uses Ghidra's stand-alone
`AssemblyBuffer`, so assembly does not patch the exact stock program. It emits
a bounded raw blob, round-trip decodes every instruction with the same
`SuperH:BE:32:SH-2A` language, and refuses to overwrite a different output.
The layout locks the two units:

| Unit | ROM envelope | Instructions | Data bytes | Blob SHA-256 |
|---|---|---:|---:|---|
| Shared helper | `0xD2270..0xD229F` | 11 | 4 | `40cea0183a38d189808b7637ea47cb594d8cb56ee615efb246c714da5f499a34` |
| Four adapters | `0xD2300..0xD23FF` | 48 | 64 | `1e3b12d0c436fca39d092a7a06e875b12c75fd8a8d000c90a402a27e088b068a` |

`map_switching_assembly.py` independently verifies that each entry label and
literal matches the authoritative manifest. The source may use only
`r0..r4`; it cannot modify `r5..r15`, PR, GBR, MACH, or MACL and contains no
explicit SR access. SH comparison instructions may update the caller-clobbered
T bit; p-code execution verifies that every other SR bit remains unchanged.
Every recognized path loads the stock-wrapper address in a `BRA` delay slot
and tail-jumps through `r3`; every pass-through path also tail-jumps through
`r3` with a `NOP` delay slot.

`tools/ghidra/EmulateMapSwitchingAdapters.java` executes the assembled bytes,
not the Python reference model. Its 47 cases cover all five slots for all six
families, active indices 5 and 255, Cold Ignition, both Bosch overrun bases,
unknown fuel bases, exact stock-wrapper destinations, and preservation of
`r5..r15`, PR, GBR, MACH, and MACL. The result is 47/47 PASS over 676
executed instructions.

This closes the standalone machine-code gate for lookup adapters. The
complete-composition harness separately executes the adapters with the
remaining injected units, exact pointer tables, and copied calibration bytes
at final addresses. Neither gate proves interrupt or hardware behavior.
Assembly and emulation use Ghidra only; radare2 is not a dependency of this
path.

### Direct rev-limiter families

`FUN_0004F282` is the only function with a true 32-bit pointer to
`0x0934E`; its unique literal at `0x4F468` is read three times. The function
reads the 8-byte `2x2 uint16` Rev Limit - Fuel Cut table and the adjacent stock
words at `0x09356` and `0x09358`. The hook therefore redirects the complete
12-byte cluster:

```text
ROM32[0x4F468]: 0x0000934E -> 0xFFFF5D10
stock cluster:  02 64 02 54 02 54 01 70 00 00 00 00
```

Only the first eight bytes are slot-specific. Maps 2-5 are at `0xD3500`,
`0xD3508`, `0xD3510`, and `0xD3518`. Shadow refresh appends the four unchanged
stock bytes so alternate branches retain their exact behavior.

The throttle path has three distinct consumers:

| Function | Literal | Base | Role |
|---|---:|---:|---|
| `FUN_0002C648` | `0x2CF9C` | `0x0942C` | stock initialization into `0xFFFF1796` |
| `FUN_0007584E` | `0x75964` | `0x09424` | runtime reads across a 28-byte cluster |
| `FUN_00077892` | `0x77BAC` | `0x0942C` | secondary scalar consumer |

The initialization literal remains stock. Runtime literals change to
`0xFFFF5D20` and `0xFFFF5D28`. The shadow preserves the full stock cluster and
replaces only bytes 8-9:

```text
stock cluster:
00 4c 00 c8 05 dc 07 d0 25 80 ff ff 00 00 00 10
ff ff 00 00 00 05 00 1e 00 32 00 b6

maps 2-5 scalar storage:
0xD3520, 0xD3522, 0xD3524, 0xD3526
```

The direct `BSR` callers of `FUN_0004F282`, `FUN_0007584E`, and
`FUN_00077892` cannot reach `0xD21xx` within the SH-2E displacement range.
RAM shadows avoid call-site trampolines and preserve the surrounding cluster
semantics.

### Atomic commit

A valid gesture produces a requested index while the published index remains
unchanged. `prepare_calibration_commit()` resolves the limiter source bytes
first. The machine-code implementation then performs this transaction:

1. Save SR and mask interrupts.
2. Write the complete 12-byte fuel-cut shadow.
3. Write the complete 28-byte throttle shadow.
4. Write the selected throttle scalar to stock runtime RAM `0xFFFF1796`.
5. Clear transient selector fields.
6. Store the validated `active_index` byte last.
7. Restore SR.

All adapter-backed lookups use the published byte, while direct consumers use
the shadows completed before that publication. The critical-section duration
and interrupt-latency impact require bench measurement. Non-identical slot
values are prohibited until the composition gate is repeated with final
feedback counts and preemption behavior is measured.

### Assembled limiter transaction and startup wrapper

`map-switching-limiter-commit.s` occupies `0xD3660..0xD375F`. Its 56
instructions and 36 literal bytes produce the locked blob:

```text
e1e296e0d2f1dccef21982f14f4e3e1aebdc39fba6b68ae8b3e2ecbc16d5a5aa
```

The function saves SR before validation, normalizes every index outside 0..4
to map 1, sets `SR.IMASK=15`, performs all runtime writes, publishes
`active_index` as the last write, and restores the exact entry SR. The Fuel Cut
source begins at `0x0934E` and its stock tail begins at `0x09356`; both are
2-byte aligned rather than 4-byte aligned. The implementation therefore copies
all 12 fuel bytes with `MOV.W`. `MOV.L` would violate the SH7058 alignment
contract for map 1. The throttle cluster begins at aligned `0x09424` and is
copied as seven longwords before its selected word is replaced.

`map-switching-startup-wrapper.s` occupies `0xD22A0..0xD22FF`. Its 14
instructions and 12 literal bytes produce:

```text
352db08c013f1f3b91551afea5a12db60cb160698d7239e1e8ac7271054ac4a3
```

The wrapper saves the incoming PR, publishes map 1 through `r0` without
changing the initializer's incoming `r4`, calls exact stock initializer
`0x2C648`, commits map 1 atomically, restores PR, and returns. The
source-level validator proves both map-1 writes around the initializer, the SR
mask/write/publication order, word-aligned fuel copies, leaf commit ABI, and
both `JSR` delay slots.

`tools/ghidra/EmulateMapSwitchingLimiter.java` executes both locked blobs. Its
14 cases cover direct commit and startup paths for indices 0 through 5 and 255.
It uses the exact stock 12-byte Fuel Cut and 28-byte throttle containers,
distinct synthetic values for maps 2-5, and sentinels around all reserved RAM.
All cases preserve entry SR, PR, `r8..r15`, GBR, MACH, and MACL; produce the
complete shadows and `0xFFFF1796`; clear bytes 1-7; publish the requested index
for direct commits and map 1 for every startup case; and leave every
surrounding sentinel unchanged. The result is 14/14 PASS over 1542 executed
instructions.

`tools/ghidra/EmulateMapSwitchingBoot.java` closes a narrower integration gap
left by those unit cases. It loads a complete patched ROM, starts at the real
stock thunk `0x27CE4`, executes the injected wrapper, the complete 1906-byte
body of `FUN_0002C648`, the injected fuel-compensation adapter, the stock
fuel-compensation lookup wrapper at `0x261F0`, and the limiter commit. Fourteen
unchanged direct callees of the stock initializer use deterministic return-zero
stubs so the test does not claim peripheral or full-reset emulation. The
reset-fixed candidate returns through the expected PR after 1809 instructions,
preserves the stack and all callee-saved registers, forces map 1, and produces
both complete limiter shadows and `0xFFFF1796`.

`tools/ghidra/EmulateMapSwitchingReset.java` extends the integration check to
the exact TRAPA handler at `0x27E24`. It executes the working base image, the
generated reset-fixed image, and the reset-fixed tuned candidate with
nine initial selector bytes: `00`, `01`, `02`, `03`, `04`, `05`, `7F`, `80`,
and `FF`. Each execution reaches the real thunk from its actual caller,
executes the complete stock initializer body and injected startup path, and
continues through the first complete scheduler-loop iteration. Six pre-thunk,
14 initializer, and five post-thunk hardware-oriented callees use the same
deterministic return-zero stubs in all images.

The fixed differential run passes over 51,057 executed instructions. All
images
restore the thunk ABI, reach the same scheduler state, and leave every RAM byte
outside the declared reservation, selected runtime scalar, and stale stack
frames below the restored SP identical. The live scheduler stack remains in
the byte-for-byte comparison. The minimum observed SP is `0xFFFF7F84`, above
the reserved RAM. The generated and differentiated images independently
produce the exact map-1 fuel shadow, throttle shadow, zeroed selector state,
and map-1 `0xFFFF1796` value for every seed. The test does not emulate the
stubbed peripheral functions and cannot prove the actual flash contents or
silicon behavior.

## Composition and output gates

`map_switching_compose.py` accepts exactly the seven manifest-locked assembly
blobs. It validates every length and SHA-256, materializes 32 calibration
copies and eight five-entry pointer tables, applies all 14 hook literals, and
places every assembly unit at its declared final address. The complete result
is compared byte-for-byte with the declared write set.

The locked exact-stock fixture produces:

```text
in_memory_sha256=499f25ed560bf8e5bc00138e29ceabf740d2f13303eb07604f2e11b537bebb16
changed_bytes=5372
permitted_write_bytes=5880
feedback_frame_counts=10,10
instruction_placements=387
code_entries=10
```

The 5880-byte write set consists of 5824 bytes allocated under the layout plus
56 bytes occupied by the 14 four-byte hook literals. Filler bytes and source
bytes that already equal their composed values are permitted writes but do not
appear in `changed_bytes`. Any changed byte outside this set fails validation.
Every source instruction is also tied to the corresponding bytes at its final
absolute address, and all ten declared code entries must begin on an
instruction. Ghidra independently round-trip decodes the same SHA-locked blobs.

`EmulateMapSwitchingComposition.java` begins with the exact one-MiB stock
program, independently applies the seven blobs, 14 hooks, 32 copies, and eight
pointer tables, and refuses any fixture whose hash or write boundary differs.
Each scenario receives a fresh emulator loaded with the complete fixture.
Deterministic stubs replace only the three stock callees outside the injected
implementation; feedback cases may additionally replace only the two
frame-count bytes. The harness executes the same 17 selector, 47 adapter, 14
startup/limiter, and nine feedback scenarios over 4530 instructions. It
reaches all ten declared code entries, checks real copied calibration bytes,
verifies exact limiter SR restoration, and permits only the caller-clobbered T
bit to differ on comparison-heavy adapter, selector, and feedback paths.

This hash identifies an ephemeral verification result, not a ROM release.
Stored checksum fields remain stock, `flashable=false`, and the pure composer
has no output-file option. Nine Python cases cover deterministic composition,
complete blob-set enforcement, hash rejection, hooks, copies, pointer tables,
locked feedback counts, rejection of an out-of-contract byte, and static
agreement between the Ghidra harness and the authoritative layout manifest.

`apply_map_switching.py` owns file creation. Its compatible-input gate permits
changes only below `0x20000`, while requiring the exact calibration identity,
hook anchors, CAN serializer anchors, erased allocation, and complete protected
upper partition. It also requires a self-consistent input checksum state. The
patcher initializes all 32 alternate-map copies from the input Map 1 values,
installs the eight pointer tables, 14 hooks, and seven tracked payloads, then
recalculates checksums in this order:

```text
self-test B -> self-test A -> SUM16 A -> SUM16 B
```

The final declared write set contains the 5880 composition bytes plus 20
checksum-reference bytes. Every input byte outside this set must remain exact.
The output is independently checksum-verified before an exclusive create, and
an MD5 sidecar is created for the flashing workflow. Thirteen patcher cases and
four checksum cases cover compatible calibration changes, exact preservation,
slot initialization, payload locks, checksum recalculation, wrong identity,
changed code or anchors, occupied storage, repeat application, and
non-overwriting output behavior.

`upgrade_map_switching_reset.py` accepts only the complete pre-fix runtime. It
requires the old `0x29CC` value and startup-wrapper SHA-256, every other tracked
payload and hook, exact pointer tables, the stock protected upper partition
outside declared map-switching and checksum storage, JK08A identity, and valid
input checksums. It restores the stock fallback literal, installs the fixed startup
wrapper, recalculates checksums, and rejects every output difference outside
those two spans and checksum fields. The 120-byte permitted set produces 38
changed bytes for the differentiated candidate while preserving every manual
calibration byte. Seven upgrade tests cover exact migration, permitted lower
and slot calibration preservation, runtime-hook, protected-code, and unlocked
payload rejection, plus non-destructive output naming.

## Common definition projection and calibration ownership

Map slots are numbered `Map 1` through `Map 5`. Firmware, layout manifests,
and generated definitions do not assign preset meanings such as daily, sport,
overrun, or valet. Calibration values are edited manually after the selector,
accessors, and definition projection pass their validation gates.

Every approved switchable calibration family is projected as five separate
tables in the common `defs/JK08A.xml` and `defs/JK08A.xdf`. All five tables
remain in the canonical functional category:

```text
<functional category>
  Map 1 - <table name>
  Map 2 - <table name>
  Map 3 - <table name>
  Map 4 - <table name>
  Map 5 - <table name>
```

Map 1 points to the stock table address. Maps 2 through 5 point to their
allocated ROM copies. The generated table names include the slot number, while
the category and all five instances reuse the established units, scaling,
axes, storage type, mask, and editor increments from the canonical JK08A
definition. Shared axes remain single stock objects unless a later exact-code
contract makes an axis switchable.

The initial map-switching image contains identical bytes in all five instances.
No generator assigns different values to maps 2 through 5.
`patches/map-switching-layout.toml` owns copy addresses, geometry, pointer
tables, hooks, and RAM shadows. Both the calibration materializer and definition
projection consume this manifest, so ROM storage, RomRaider XML, and TunerPro
XDF cannot drift.

The projection contains 40 slot-specific calibration tables. The masked bit-7
views for both switched ignition families add ten slot-specific editor views,
for 50 slot-specific views in total. Cold ignition keeps its one global masked
view. A read-only validation against the live graph and tracked common
definitions reports:

```text
canonical graph maps:       446
projected maps:             478
calibration tables:          44
masked views:                11
slot calibration tables:     40
slot masked views:           10
slot editor views:           50
```

`tools/mapkit/validate_map_switching.py` renders every RomRaider table fragment
and the complete TunerPro model, parses both tracked outputs, verifies identical
materialized bytes in all slots, and writes no artifact.

The common `JK08A.xml` and `JK08A.xdf` cover both the stock image and the
project map-switching image under the unchanged `JK08A` identity. In a stock
image, Map 2 through Map 5 point to erased `0xFF` allocations and are not
referenced by runtime code. Their presence in the definition does not imply
stock map-switching support. Calibrations not approved for runtime switching
remain single global entries in their established functional categories. Code,
pointer tables, selector state, diagnostic instrumentation, NATS, DTC controls,
and checksum fields are not presented as per-slot calibrations. No separate
`JK08A-MS5` identity or definition artifact exists.

## Diagnostic observation

After each selector invocation, the wrapper mirrors default versus non-default
selection into bit 7 of `0xFFFF2A84`:

```text
map 1:      value & 0x7f
map 2..5:  value | 0x80
```

Bits 0..6 remain the stock ASCD lamp-status value. The exact service 0x22 path
returns `0xFFFF2A84` as the first data byte for DID 0x130E and
`0xFFFF2A82` as its second, stock support-mask byte. The graph contains one
stock writer, `FUN_000CF020`, and one control-independent consumer,
`FUN_0003235C`, for `0xFFFF2A84`.

Bit 7 is intentionally absent from the stock support mask. Observation uses the
raw `0x22130E` response, not a factory label. The mirror is a prototype
instrumentation field, not a claimed Nissan status bit. It proves failover to
map 1 versus selection of an alternate map; the visual pulse count identifies
the exact slot.

## Driver-visible confirmation

The official UpRev tuning guide describes five switchable map slots and treats
a flashing cruise-control light as the expected map-switching feedback. This
contract provides a separate JK08A implementation with the same user-level
capacity, without claiming UpRev's internal design.

After a valid commit, the CRUISE indicator flashes the one-based map number:

| Active map | Pulses |
|---:|---:|
| 1 | 1 |
| 2 | 2 |
| 3 | 3 |
| 4 | 4 |
| 5 | 5 |

The pulse request is queued only after the active-index byte is committed.
Selector input remains disabled for the duration of the confirmation sequence.
An invalid active index produces one pulse and retains map 1.

The factory manual establishes the physical route:

```text
ECM ASCD status CAN signal -> unified meter and A/C amp. -> CRUISE indicator
```

The exact JK08A transport boundary is:

```text
ROM 0x09766: 03 08 aa 20
  type 3 -> transmit mailbox
  DLC 8
  standard ID 0xaa20 >> 5 -> 0x551

FUN_000C3ED2
  compares the 0xaa20 control word
  reads its unique serializer literal at 0xC3FA4
  stock literal value -> FUN_000C5372

FUN_000C5372
  writes payload bytes 0..7 to 0xFFFF3AD5..0xFFFF3ADC
  writes the status state in byte 5 at 0xFFFF3ADA
```

The serializer constructs the byte-5 low two-bit state and preserves unrelated
fields in the same byte. A homologous Z34 community decoder identifies state
value `2` as active cruise status in CAN frame 0x551 byte 5. Its byte and value
align exactly with the JK08A serializer. The pilot intentionally uses this
state as a hardware-test hypothesis; applicability to the V36 meter remains
candidate evidence until the target vehicle confirms it.

Literal `0xC3FA4` has one Ghidra reference, from `0xC3F3A` in
`FUN_000C3ED2`. The manifest redirects it from `0x000C5372` to
`0x000D35E0`. The feedback wrapper calls the stock serializer first and then,
only while a pulse is active, replaces:

The exact call sequence is `MOV.L @(0xC3FA4,PC),r3` at `0xC3F3A`, `JSR @r3`
at `0xC3F3C`, and `NOP` in the delay slot. `FUN_000C5372` is a leaf that
returns through `RTS` at `0xC5504`; its observed register set is
`r0/r2/r4..r7`. The injected wrapper preserves PR around both nested calls and
uses only caller-saved registers. The dispatcher branches from `0xC3F40` to
the common block at `0xC3FB2`, whose live loop state is held in `r10..r14`.
Those registers remain unchanged across the wrapper, and no serializer return
value is consumed.

```text
0xFFFF3ADA.bits0..1 = 2  for lamp on
0xFFFF3ADA.bits0..1 = 0  for lamp off
```

All upper six bits and all other payload bytes retain the stock serializer
result. The wrapper advances the pulse engine once per frame 0x551
serialization. `map_switching_selector.py` expresses the on and off durations
as counts of serializer invocations. The pilot locks both phases to ten frames;
their wall-clock duration depends on the target's actual frame period. It must
not blink the lamp by modifying `0xFFFF41AE`, `0xFFFF4252`, or another stock
ASCD control state.

The assembled ABI wrapper occupies `0xD35E0..0xD365F`, always calls stock
serializer `0xC5372` first, and then calls the leaf pulse engine at `0xD3760`.
Their locked SHA-256 values are:

```text
b8e8c20cd365f27b7a8df59318f22911621ef51a33dfefc128563940be558d36
c3a10706e283bc53c5634730d7ad96a5c49bebd8dc22536f96cfc411ef46a784
```

The engine stores its two uint8 configuration bytes at `0xD3848`: on-frame
count followed by off-frame count. The locked pilot values are `10, 10`. A
zero/zero pair disables the overlay, clears a queued feedback sequence on the
next 0x551 serialization, and preserves the complete stock payload. A partially
configured pair also fails closed.

`EmulateMapSwitchingFeedback.java` uses a deterministic serializer stub that
writes `0xA5` to byte 5 before every engine invocation. Nine cases and 17
invocations verify disabled behavior, 1x1 and 2x2 frame sequences, invalid
phase/count state, incomplete configuration, preservation of payload bytes
0-4 and 6-7, upper-bit preservation in byte 5, protected registers, and stack
balance. All cases pass over 841 executed instructions.

## Checksum impact

| Change | SUM16 A | SUM16 B | self-test A | self-test B |
|---|---|---|---|---|
| startup literal `0x29CC` | no | no | no | no |
| startup wrapper literal `0x27D28` | no | yes | yes | no |
| host literal `0xCE8DC` | no | yes | yes | no |
| adapter hook literals | no | yes | yes | no |
| limiter-shadow hook literals | no | yes | yes | no |
| feedback serializer literal `0xC3FA4` | no | yes | yes | no |
| injected and storage range `0xD2108..0xD385F` | no | yes | yes | no |

The adapter row covers `0x4FDD0`, `0x50258`, `0x496C0`, `0x4E474`,
`0x4E58C`, `0x2CF1C`, `0x3C388`, and `0xC0020`. The limiter-shadow row covers
`0x4F468`, `0x75964`, and `0x77BAC`. Hook literals and complete ranges are
machine-readable in the layout manifest.

The existing recalculation order remains mandatory:

```text
self-test B -> self-test A -> SUM16 A -> SUM16 B
```

`jk08a_checksums.py` implements this order and independently verifies all six
stored references. `apply_map_switching.py` refuses an inconsistent input and
verifies the recalculated output before writing it.

## Validation gates before an engine test

1. Patch a checksum-valid compatible input with `apply_map_switching.py` and
   retain the reported input/output SHA-256 values and MD5 sidecar.
2. Verify that Map 2 through Map 5 equal the input Map 1 in all eight families,
   all checksum domains pass, and the common `JK08A` XML/XDF projection matches
   the layout.
3. Confirm the raw ladder sequence `SET -> CANCEL -> SET` on the target switch
   assembly.
4. With the vehicle stationary and the engine stopped, confirm that CAN 0x551
   byte 5 state `2` produces the CRUISE indication and that the locked `10, 10`
   timing gives a visible pulse. This is the first silicon check of the explicit
   feedback hypothesis and does not require a separate stock-period capture.
5. Verify one through five indication pulses and confirm that stock ASCD control
   state remains unchanged.
6. Confirm reset Map 1 and raw DID 0x130E bit 7 on a bench ECU or the target
   vehicle.
7. Measure the extended startup clear and commit critical-section latency.
8. Confirm unchanged lookup outputs for every input index in all five selector
   states.
9. Start the engine with byte-identical maps and exercise all five selections
   before changing any alternate map.

Ground truth remains the physical ECU and engine.
