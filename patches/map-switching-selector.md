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

The target pilot has five slots and ten switchable calibration families. Eight
families use fail-closed lookup adapters. The two directly accessed rev-limiter
families use complete RAM shadows refreshed as part of the same atomic commit.
At patch time, Map 2 through Map 5 receive exact copies of the input Map 1
bytes. Selection therefore has no intended control effect before manual tuning.

`map-switching-layout.toml` is the authoritative ROM/RAM allocation and hook
manifest. `map_switching_layout.py` validates exact and compatible inputs and
materializes identical slot storage in memory. `map_switching_selector.py` is
the executable selector, adapter, and limiter-shadow reference model.
`map_switching_assembly.py` validates the source-level address, literal, ABI,
and delay-slot contract for implemented SH slices, then independently decodes
every control transfer and PC-relative reference from the locked machine word.
`map_switching_compose.py` validates all locked blobs and applies code,
calibration copies, pointer tables, and hooks to an in-memory image without
exposing an output-file operation. `map-switching-payloads.toml` stores the
eight validated machine-code spans as hexadecimal data.
`apply_map_switching.py` is the output boundary: it validates the input and
payloads, invokes the compatible-input composition, recalculates every JK08A
checksum domain, proves byte preservation outside the declared write set, and
creates a ROM plus MD5 sidecar without overwriting a different file.
`tools/ghidra/EmulateMapSwitchingComposition.java` independently reconstructs
the same complete fixture from the exact Ghidra program and executes every
machine-code scenario against final composed addresses.
`tools/mapkit/map_switching.py` projects the same addresses into the common
JK08A RomRaider and TunerPro definitions.

Eight independent SH assembly units are implemented: the selector host, shared
fail-closed adapter helper, four legacy lookup adapters, four-family DFCO
adapter, startup wrapper, atomic limiter transaction, CAN serializer wrapper,
and feedback pulse engine. Ghidra 12.1.2 assembles and round-trip decodes their
418 instructions and 194 literal bytes. The source validator restricts all
injected code to an explicit 29-mnemonic subset
mnemonics listed for the SH7058S SH-2E core in Renesas REJ09B0177 section 2.4.1;
the SH-2A Ghidra profile cannot introduce an unaudited instruction. Global
source and machine validation requires `NOP` after every delayed control
transfer, preventing any instruction from acquiring delay-slot-specific
hardware semantics. Its
SuperH p-code emulators pass 17 selector, 76 adapter, 14
startup/limiter, and nine feedback cases. The eight generated raw blobs are
SHA-256 locked in the layout manifest. Their complete spans are tracked in the
payload bundle; independently rebuilt raw blobs and listings remain
regenerable temporary artifacts. The complete-composition harness passes the
same 116 cases over 5152 instructions, executes all eleven declared code entries,
and verifies the locked fixture SHA-256 and write boundary. The patcher extends
this pure composition with input compatibility, checksum recalculation,
non-overwriting file creation, and final preservation checks.

Vehicle testing identifies `0x20`, rather than `0x00`, as the released
steering-switch code. CAN frame `0x239`, byte 4 counted from one, carries
`0x20` with all buttons released, `0x02` for CANCEL, `0x08` for SET, and
`0x10` for RESUME. The custom multimap base and Rolling Launch Overlay 20 both
passed PCMFlash identification and application startup, but map selection did
not arm and Rolling Launch could not rearm after its first activation. The
shared cause was the incorrect `0x00` release assumption. The current selector
uses `0x20` for arming and commit and treats `0x00` as invalid. Overlay 21,
SHA-256
`1e6866e96e77fba203166b38f5efcfd83b6bcad609b7e0ada67727cd5fddc0c9`,
contains this correction. Target-vehicle testing confirms functional selection
of Maps 2 and 3. Its byte-5 low-bit feedback command has status `FAIL`: the
injected states are present on CAN 0x551, but the V36 combination meter does not
change the requested indicator. A later Map 2 -> Map 3 selection proves that
the queue drains and does not block the selector. The current feedback engine
uses the serializer's byte-5 bits 5-6 with mask `0x60`, on value `0x60`, and off
value `0x00`. Its executable gates pass, while target-vehicle meter behavior
retains hardware status `UNTESTED`.

The differentiated candidate
`1JK08A-20260726-map-sw-tune.bin`, SHA-256
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

The controlled reproduction on a fresh bench ECU establishes an image-specific
failure. Its initial identification was `1JK00C00000`. Three consecutive stock
writes each survived a power cycle and identified as `1JK08A00000`; the next
write selected
`C:\Users\rudoo\OneDrive\Desktop\rom\1JK08A-20260726-map-sw-tune.bin`,
reported success, and was followed by two failed identifications. The complete
PCMFlash 1.2.0 log records the same erase, area-1 transfer, validation, and
completion stages for all four operations. Stock transfer durations were 128,
131, and 131 seconds; the candidate transfer took 129 seconds. Validation took
about one second, while a complete one-MiB read on the same bench took 227
seconds. The readable log contains no programmed address ranges, input-file
digest, or byte-comparison result. The selected Windows file has independently
confirmed SHA-256
`d61853b7c1f1b2b29d3ccf2a551be8dacebeef65b82b464d0327fc9b11e93e5d`,
which is exact to the locally audited candidate. This excludes a random
transport failure and a stale or different input file as the leading
explanations, but it does not bind the resulting user MAT to those bytes.

The candidate file itself passes the available checksum and byte-identity
gates, which did not cover the SH-2E delay-slot PC rule:

- RomRaider source commit
  `874325319be98fc487e3875e5b26d25b8869e162`, compiled directly from
  `/Users/isrudoy/src/oss/RomRaider`, verifies `ChecksumALT` 2/2 and
  `ChecksumALT2` 4/4;
- all seven injected code spans, 15 hook literals, and eight pointer tables are
  byte-identical to the generated map-switching image;
- the 394 differences from the generated image consist of 12 checksum bytes
  and 382 calibration bytes, including the global Cold Ignition edits and the
  manually differentiated slot maps;
- reset-selection bytes at `0x8000`, `0x8080`, and `0xFFF80..0xFFF87` are
  identical in the working, generated, and differentiated images.

The reset-fixed successor is
`1JK08A-20260726-map-sw-tune-fixed-reset.bin`, SHA-256
`3e37f03a2ac879714556ab720fa657eb4132d1b22ecdccbb2c4edce631842ced`
and MD5 `4985aaec122bd62fd9d636346529a953`. It differs from the pre-fix
candidate at 38 bytes inside the 120-byte upgrade write set: the fallback
zero-fill literal, startup-wrapper span, and recalculated checksum fields.
Every calibration byte remains exact. RomRaider source commit
`874325319be98fc487e3875e5b26d25b8869e162` verifies `ChecksumALT` 2/2 and
`ChecksumALT2` 4/4. This image still contains the unsafe first-revision lookup
adapter and has status `OBSOLETE_FAIL_ROOT_CAUSE`; it must not be written.

The official PCMFlash module list declares the SH7058 protocol as a one-MiB
`RD/WR/CK` protocol rather than a calibration-only protocol. It does not
publish erase-block selection or post-write comparison behavior.

The successful marker transaction has a complete hardware readback. The input
SHA-256 is
`e1fef7ccf862243be7b231b26865c9cd099283993cfe8c73abb9952b1e5358b7`;
the readback SHA-256 is
`d5cb0000f77c8c1112d912474cbb471f78051805027e3358fbedc28cf1bf58b3`.
They differ at exactly 128 bytes in the single line
`[0x8080, 0x8100)`: the input contains `0xEE`, while the readback contains
`0x00`. Replacing that input line with 128 zero bytes produces the readback
exactly. Every other byte matches, including the complete marker line
`[0xD2280, 0xD2300)`, all five changed checksum bytes, all 14 stock hooks,
and the rest of the one-MiB image. Both files independently satisfy all six
checksum references. PCMFlash did not alter any stored checksum field relative
to the already valid input. The layer responsible for the exceptional
`0x8080` transformation remains to be isolated.

The PCMFlash progress denominator does not independently establish programming
coverage. The public manual describes this value as a counter of transferred
blocks and subblocks, without specifying their byte size or requiring read and
write to use the same transfer unit. One MiB contains 8192 native 128-byte
SH7058S programming units but 16384 64-byte read payloads. The observed bench
values of approximately 16640 during read and approximately 7900 during write
are therefore compatible with different protocol framing. If the exact write
denominator is 7936, it arithmetically matches 128-byte programming of
`[0x8000, 0x100000)`, but neither the approximate observation nor the public
protocol documentation proves that address range. The PCMFlash log records the
transfer stages but not the GUI denominators. The marker transfer lasted 128
seconds, while its full readback area took 1705 seconds. The one-MiB input is a
raw address image, not a container with a generic effective-range field; any
selected or protected address range is part of the PCMFlash module protocol.

The `0x8080` line is outside every documented JK08A checksum domain. In the
reset selector, the input image produces
`0xFF & (0xEE | 0xF0) = 0xFE`, while the hardware readback produces
`0xFF & (0x00 | 0xF0) = 0xF0`. Both values pass the accepted `0xF0..0xFE`
range, match the header marker at `0xFFF84`, and enter TRAPA `0x3E`. Neither
variant reaches the fallback call that uses the `0x29CC` clear-start literal.

The complete pre-flash `1JK03B_7MFKAVN86` baseline has SHA-256
`a9aa7a337375b7c9419b0970c32674e98f12ea4215c079898190c5c771a96f1a`
and independently satisfies all six checksum references. Its complete
`[0x8080, 0x8100)` line contains `0xEE`, exactly like the marker input, while
the post-write readback contains `0x00`. The same read path therefore exposed
the input value before programming and the changed value afterwards; this was
not preservation of an ECU-specific baseline line. The baseline differs from
the marker input at 675 bytes spanning `0x8200..0xD22FF` in 57 native
128-byte lines. Every one of those 675 bytes equals the marker input in the
post-write readback. The post-write image additionally differs from the
baseline at all 128 bytes of the `0x8080` line. The successful transaction
therefore applies all available input deltas and separately transforms one
line that was identical in the baseline and input. The available evidence does
not distinguish an optional checksum-correction transformation from a core
module-18 programming rule. A controlled write of an already checksum-valid
gate image with checksum correction disabled can isolate those layers; recovery
mode is not required for the responding ECU.

The pre-fix candidate differs from its known-working tuned base below `0x8000`
at exactly one byte, `0x29CE`. This changes the longword literal at `0x29CC`
from `0xFFFF7000` to `0xFFFF5D00`; the exact reset audit establishes that its
containing initialization path does not execute on the observed TRAPA power-on
path. Every executable hook and the complete injected tail are at or above
`0x8000`. Consequently, even if the conditional `[0x8000, 0x100000)` write
hypothesis is confirmed, omission of the lower 32 KiB does not explain the
loss of startup.

An expanded read-only p-code diagnostic executes the exact reset path,
`FUN_00020DFE`, all 124 entries in its periodic table, and their software
callees for the working and pre-fix images. Only SCI2 wait primitive
`FUN_00066BD0` is stubbed inside the periodic path because it requires a
physical peripheral response. All nine retained selector seeds complete the
first full period over 3,386,971 total instructions with minimum SP
`0xFFFF7DA0`. For map 1, the working image executes 187,918 instructions and
the pre-fix image executes 188,212, a delta of 294; their complete RAM states
match outside the declared selector/shadow reservation, selected runtime
scalar, and released stack frames. Maps 2 through 5 contain intentionally
different calibrations, so their diagnostic verifies completion, protected
registers, SR, selector state, and limiter shadows without requiring equal
application RAM.

The first complete reconstructed software period does not reproduce the
failure. The marker readback proves that normal module-18 programming can
install a newly non-`0xFF` line in the injected tail and preserve every
checksum byte. It does not reconstruct either failed pre-fix user MAT, so a
candidate-specific omission is not logically excluded, but generic omission
of the new tail is no longer the leading branch. The prepared second gate
isolates execution through the startup hook and a minimal tail trampoline.
Individual runtime hooks, hardware-oriented initialization, asynchronous
interrupts, and later periods remain subsequent silicon-only branches.

`build_map_switching_marker.py` implements the first staged hardware gate. It
accepts only the known-working tuned base with SHA-256
`1bf9978ba1d870216bd85ff69aed25243a77f186231718dcfffd9bb411529471`,
replaces the complete erased line `[0xD2280,0xD2300)` with 128 zero bytes,
recalculates all six checksum references, and proves that all 14 runtime hooks
remain stock. The generated image
`1JK08A-20260726-immo-e2-pops-fuel-throttle-ofc-v2-marker-only-d2280.bin`
has SHA-256
`e1fef7ccf862243be7b231b26865c9cd099283993cfe8c73abb9952b1e5358b7`
and MD5 `ae982b7e05fdd04af51f4136637f60cd`. It differs from its base at all
128 marker bytes and five checksum bytes: `0x8201`, `0x96DE..0x96DF`, and
`0x20000..0x20001`. No executable payload, hook, pointer table, or calibration
copy is installed. Write, power cycle, identification, tail readback, checksum
comparison, and normalized full-image comparison pass on the bench. The only
raw comparison difference is the accepted `0x8080` variant described above.
The marker gate therefore has status `PASS_WITH_0x8080_VARIANT`.

`build_map_switching_trampoline.py` implements the second staged hardware gate.
Its only accepted source is the successful marker readback with SHA-256
`d5cb0000f77c8c1112d912474cbb471f78051805027e3358fbedc28cf1bf58b3`,
which already contains the accepted zero-filled `0x8080` line. The gate changes
startup pointer `ROM32[0x27D28]` from `0x0002C648` to `0x000D22A0` and installs
this 12-byte payload at `0xD22A0`:

```text
d001  mov.l @(0xD22A8,pc),r0
402b  jmp @r0
0009  nop
0000  alignment fill
0002c648  stock initializer literal
```

The `JMP` preserves the original caller's `PR`; loading `r0=0x2C648` also
restores the value seen by the stock initializer on the original path. No RAM
write, stack operation, selector logic, calibration copy, pointer table, or
other runtime hook is present. Ghidra 12.1.2 independently assembles and
round-trip decodes the three physical instructions and four literal bytes. The
12-byte payload SHA-256 is
`5e3e791f1a0d302b905db989c9a646440a69fe531921a246a21f3082712eb603`.

The generated image is
`1JK08A-20260726-immo-e2-pops-fuel-throttle-ofc-v2-startup-trampoline-d22a0.bin`:

- SHA-256:
  `6b1df699f614151a7ddd09595671de021b7131d5524b16d1f27a9fed888abc55`;
- MD5: `8598014aa80faa4fff4faccba6cae17d`;
- 23 changed bytes relative to the readback source: three hook bytes, eight
  nonzero trampoline bytes, and 12 checksum bytes;
- a 36-byte permitted set: four hook bytes, 12 trampoline bytes, and 20
  checksum-reference bytes;
- all six checksum references pass, all other 13 hooks remain stock, and all
  bytes in the marker line outside `[0xD22A0,0xD22AC)` remain zero.

`EmulateMapSwitchingTrampoline.java` executes the complete stock initializer
from the real startup thunk against the hardware readback and gate images.
Fourteen unchanged direct callees use identical deterministic return-zero
stubs. The baseline and gate return through the same original `PR` with
byte-identical complete RAM and all compared registers, the same minimum SP
`0xFFFF7FBC`, and 1680 versus 1682 Ghidra p-code steps. The two-step delta
represents `MOV.L` plus `JMP` with its delay-slot `NOP`.

The 2026-08-04 PCMFlash transaction gives the gate hardware status
`PASS_EXACT`. Writing completed successfully at 11:18:30, identification at
11:19:29 reported `1JK08A00000`, and the complete read finished successfully at
11:48:15. A final identification at 11:50:41 reported the same software. The
readback is byte-identical to the input image and has the same SHA-256
`6b1df699f614151a7ddd09595671de021b7131d5524b16d1f27a9fed888abc55`.
All six checksum references pass. The current PCMFlash journal containing this
transaction and the subsequent selector-init transaction has SHA-256
`382804d07e7ea391c39346d24a966672d19e0e934f5d806a3f87481a9cb505d2`.
This result excludes generic omission of the startup hook or tail and excludes
the transparent `0x27D28 -> 0xD22A0 -> 0x2C648` path as the direct cause of
`FAIL-BOOT`.

`build_map_switching_selector_init.py` implements the third staged hardware
gate. Its only accepted source is the exact successful trampoline readback.
The already installed startup hook remains unchanged, while the transparent
tail is replaced by this 28-byte wrapper at `[0xD22A0,0xD22BC)`:

```text
4f22  sts.l pr,@-r15
d105  mov.l @(0xD22B8,pc),r1
e000  mov #0x0,r0
2100  mov.b r0,@r1
d002  mov.l @(0xD22B4,pc),r0
400b  jsr @r0
0009  nop
4f26  lds.l @r15+,pr
000b  rts
0009  nop
0002c648  stock initializer literal
ffff5d00  selector-state literal
```

The wrapper performs exactly one persistent application-RAM write:
`RAM8[0xFFFF5D00]=0`, selecting Map 1 before the stock initializer. It preserves
the original `PR`, returns with the same register state, and installs no
limiter, lookup adapter, selector host, calibration copy, pointer table, or CAN
feedback. Ghidra independently assembles and round-trip decodes ten physical
instructions and eight literal bytes. The payload SHA-256 is
`906991815705fe9a0b91d3817fab1a59d4664e3f04ad126820d969e47d7f5612`.

The generated image is
`1JK08A-20260726-immo-e2-pops-fuel-throttle-ofc-v2-startup-selector-init-d22a0.bin`:

- SHA-256:
  `7dcb43b2181c030bde772999b674afb72a8cd196e93a0aae3fecf90069ed62d3`;
- MD5: `f9d6e71af479a7169368d675e5a314cc`;
- 33 changed bytes relative to the successful trampoline readback: 21 payload
  bytes and 12 checksum bytes;
- a 48-byte permitted set: 28 selector-init bytes and 20 checksum-reference
  bytes;
- all six checksum references pass, the startup hook remains `0xD22A0`, and
  the other 13 hooks remain stock.

`EmulateMapSwitchingSelectorInit.java` compares the successful trampoline
readback and third gate from the real startup thunk through the complete stock
initializer. The gate changes only the selector sentinel `0xA5` to Map 1 at
`0xFFFF5D00` outside the released stack. Final registers are identical. The
initializer stack is exactly shifted down by four bytes, the saved outer `PR`
is exact, and the initializer return address changes only from the original
caller to the wrapper continuation. The source and gate take 1682 and 1688
Ghidra p-code steps, with minimum SP `0xFFFF7FBC` and `0xFFFF7FB8` respectively.

The 2026-08-04 PCMFlash transaction gives the selector-init gate hardware
status `PASS_EXACT`. Writing the exact file completed successfully at 12:19:54.
Identification after the power cycle reported `1JK08A00000` at 12:21:42. The
complete one-MiB read finished successfully at 12:50:19, and final
identification reported the same software at 12:51:58. The readback
`1JK08A-20260726-immo-e2-pops-fuel-throttle-ofc-v2-startup-selector-init-d22a0_readback.bin`
is byte-identical to the input image and has the same SHA-256
`7dcb43b2181c030bde772999b674afb72a8cd196e93a0aae3fecf90069ed62d3`.
All six stored checksum references equal their independently calculated
values. This excludes the isolated persistent selector write and its complete
`PR`-preserving wrapper as the direct cause of `FAIL-BOOT`.

`build_map_switching_limiter.py` constructs the aggregate limiter endpoint.
Its only accepted source is the exact successful selector-init readback. The
image installs the final startup wrapper and atomic limiter commit, initializes
Map 2 through Map 5 from the input Map 1 for only the two rev-limiter families,
materializes their two five-entry pointer tables, and replaces these three
direct limiter literals:

```text
ROM32[0x4F468]: 0x0000934E -> 0xFFFF5D10
ROM32[0x75964]: 0x00009424 -> 0xFFFF5D20
ROM32[0x77BAC]: 0x0000942C -> 0xFFFF5D28
```

No selector-host call, lookup adapter, adapter-backed calibration copy or
pointer table, or CAN-feedback component is present. Startup is the only caller
of the limiter commit and always supplies index zero. The resulting runtime
therefore exercises complete Map 1 fuel-cut and throttle shadows without
enabling a map-selection path.

The generated image is
`1JK08A-20260726-immo-e2-pops-fuel-throttle-ofc-v2-startup-limiter-map1-d3660.bin`:

- SHA-256:
  `1833922fc7d3428ed9f9998a99281d4c02b66c027cc39f7620aa3a79d541964a`;
- MD5: `b3586f278e236499d7e0816bad1a8e46`;
- 314 changed bytes relative to the successful selector-init readback: 80
  startup-wrapper bytes, 138 limiter-commit bytes, 32 limiter-copy bytes, 40
  pointer-table bytes, 12 direct-hook bytes, and 12 checksum bytes;
- a 464-byte permitted set: the 96-byte startup-wrapper envelope, 256-byte
  limiter-commit envelope, 40 limiter-copy bytes, 40 pointer-table bytes, 12
  direct-hook bytes, and 20 checksum-reference bytes;
- all six checksum references pass, Map 2 through Map 5 are byte-identical to
  input Map 1 for both limiter families, and every non-limiter runtime hook and
  storage range remains at the preceding stage.

Ghidra 12.1.2 independently rebuilds the final startup and limiter spans with
SHA-256 `352db08c013f1f3b91551afea5a12db60cb160698d7239e1e8ac7271054ac4a3`
and `e1e296e0d2f1dccef21982f14f4e3e1aebdc39fba6b68ae8b3e2ecbc16d5a5aa`.
The isolated limiter harness passes 14/14 cases over 1542 p-code instructions.
`EmulateMapSwitchingLimiterGate.java` differentially executes the exact source
and gate images from the real startup thunk through the complete stock
initializer. The source and gate take 1688 and 1795 steps, an exact delta of
107, and both have minimum SP `0xFFFF7FB8`. The gate clears all eight selector
bytes, creates the exact 12-byte fuel shadow and 28-byte throttle shadow from
Map 1, preserves the Map 1 value in `0xFFFF1796`, restores SR exactly, preserves
all protected registers, and leaves every RAM byte outside the reservation
equal to the source run. The aggregate image has hardware status `PASS_EXACT`
through the exact limiter Overlay 05 input/readback pair.

`build_map_switching_limiter_overlays.py` decomposes that aggregate endpoint
into five cumulative, atomic hardware overlays. Every output is a complete
one-MiB ROM, not a partial patch. Each image is built from the preceding planned
image in memory, all six checksum references are recalculated at every step,
and no intermediate hardware readback becomes the next source. The exact
successful selector-init readback remains the single chain root.

| Stage | Newly active component | Direct limiter hooks | SHA-256 | MD5 |
|---:|---|---:|---|---|
| 01 | Inactive limiter commit, Map 1-equivalent copies, and pointer tables | 0 | `9bb1704f93a6050593abbf30b450cc1b75bc4d141ed4455b7528148de69f56c4` | `0b945f8909358e704039cc15386b14df` |
| 02 | Final startup wrapper and execution of limiter commit | 0 | `135512525ed64b7728348a2b8859e9a7b607f931f57f6a7951e0d2d7dc847da5` | `58e187733c04e5dc42417c0edc7ce408` |
| 03 | Fuel-cut base hook at `0x4F468` | 1 | `22f824be2e9ca941b42760de27accc7cd1c7365e23a0b19eda29387fd1dd196c` | `f21f4c62933aa1ce5d4d0ce7f37f0505` |
| 04 | Throttle-cluster base hook at `0x75964` | 2 | `3aa4bce11eb9030dc688c04744170e8aee61b1b9f8e3dd99a57a4d5ca1f626db` | `bc1df55ec410d0c2053c5cd1021a016a` |
| 05 | Throttle-scalar base hook at `0x77BAC` | 3 | `1833922fc7d3428ed9f9998a99281d4c02b66c027cc39f7620aa3a79d541964a` | `b3586f278e236499d7e0816bad1a8e46` |

The adjacent-image permitted sets contain 356 bytes for stage 01, 116 bytes
for stage 02, and 24 bytes for each hook stage. The actual adjacent changes are
222, 92, 15, 15, and 15 bytes respectively; checksum references account for
12, 12, 11, 11, and 11 of those bytes. Stage 05 is byte-identical to the
aggregate limiter endpoint above.

The complete readback
`1JK08A-20260726-immo-e2-pops-fuel-throttle-ofc-v2-limiter-overlay-05-throttle-scalar-hook-77bac_readback.bin`
is byte-identical to the written Overlay 05 image. Both files have SHA-256
`1833922fc7d3428ed9f9998a99281d4c02b66c027cc39f7620aa3a79d541964a`
and MD5 `b3586f278e236499d7e0816bad1a8e46`, and all six stored checksum
references equal their independently calculated values. The PCMFlash log with
SHA-256 `809c25bb063b0c89aced8caf53564e0547459babd81a510a3c7dcb5c7357e5ba`
records the selected Overlay 05 file at 14:32:55, successful write completion
at 14:35:26, post-write identification as `1JK08A00000` at 14:36:01, and
successful completion of the full read at 15:04:38 on 2026-08-04.

The ordered SHA-256 manifest is
`1JK08A-20260726-immo-e2-pops-fuel-throttle-ofc-v2-limiter-overlay.sha256`.
`EmulateMapSwitchingLimiterGate.java` executes all five exact images. Stage 01
is behaviorally identical to the selector-init source at 1688 p-code steps and
does not reach limiter commit. Stages 02 through 05 reach the commit and finish
at 1795 steps, the exact 107-step delta. Every run has minimum SP
`0xFFFF7FB8`; the five stages pass their cumulative hook contract, exact RAM
reservation contract, protected-register checks, and complete RAM comparison
outside the reservation.

All five cumulative writes, power cycles, and identifications report
`1JK08A00000` on the bench ECU. Stages 01 through 04 have hardware status
`PASS`, and the complete limiter endpoint at stage 05 has hardware status
`PASS_EXACT`: inactive code and storage, startup commit, fuel-cut RAM shadow,
throttle-cluster RAM shadow, and throttle-scalar RAM shadow all coexist without
loss of application startup or PCMFlash identification, and the final user MAT
equals the intended image byte for byte. No intermediate readback was used; the
complete readback was obtained after stage 05. This excludes the complete
limiter endpoint as the direct cause of the reproduced `FAIL-BOOT` and excludes
a PCMFlash transformation of that endpoint.

The first lookup-chain revision used adapter blob SHA-256
`1e3b12d0c436fca39d092a7a06e875b12c75fd8a8d000c90a402a27e088b068a`.
Its inactive Overlay 06, SHA-256
`4973ad83818d800325401bf49377a4074002b0f056ba1b9274ce25f9cfaf9a2d`,
survived the write and power cycle and identified as `1JK08A00000`. Overlay 07,
SHA-256 `7e766b957454f7b22524528fd9e922060cac587d2f46a4fdb5f96e1db758e5ea`,
activated only the DFCO Entry literal at `0x4FDD0`. PCMFlash completed erase,
transfer, validation, and completion without an error, but both subsequent
identification attempts returned error 2180. The complete journal has SHA-256
`431e66fc1d76686c7e8635c7c56a3535dadaa754c718000706818852759165e8`.

The failure is caused by a PC-relative `MOV.L` in each selected adapter path's
`BRA` delay slot. Renesas REJ09B0171 section 6.1.34 specifies that a PC-relative
move immediately after a delayed branch uses the branch destination plus two
as its PC basis. In the activated path, `BRA` at `0xD2314` targets `0xD2270`.
The delay-slot instruction at `0xD2316`, encoded as `D304`, therefore reads the
longword at `0xD2280`, `0x042E432B`, instead of the intended stock-wrapper
literal `0x00026388` at `0xD2328`. The shared helper then executes `JMP @r3`
to `0x042E432B`. The Ghidra p-code model resolved the load against the static
instruction address and therefore produced a false PASS for this hardware
rule. All first-revision lookup overlays and complete ROMs containing that
adapter blob are unsafe and must not be written.

`build_map_switching_lookup_overlays.py` emits revision 2 from the exact
successful Overlay 05 bytes. The fixed adapters load each stock-wrapper address
before dispatch and use `NOP` in every `BRA` delay slot. Stage 06 installs the
inactive shared helper, four lookup adapters, six Map 1-equivalent family
copies, and six pointer tables. Stages 07 through 14 activate one lookup literal
each. The startup-time fuel-compensation literal at `0x2CF1C`, which is reached
inside the stock initializer, remains last. Selector-host and CAN-feedback code
and hooks remain absent throughout the chain.

| Stage | Newly active component | Active lookup hooks | SHA-256 | MD5 |
|---:|---|---:|---|---|
| 06 | Inactive helper, adapters, Map 1-equivalent copies, and pointer tables | 0 | `990c7aff5dc62f33682900ff93b30b4888bd7171147689b1d43c58c13452d59f` | `19117705b5efa7ed53900af0c989c2c9` |
| 07 | DFCO Entry lookup literal at `0x4FDD0` | 1 | `95049dca436d74375954bf2e8586525573f9c7b864636144e9b5195130a8a6ba` | `619311f5941d5a570531c088a53bdcb8` |
| 08 | DFCO Full Restore lookup literal at `0x50258` | 2 | `50d6b59b1a236bf141eba2c5f74687fd440962510aa13e49a7414e42c1324e7b` | `13fadaf3fc0fa5e8678ae044b03e450e` |
| 09 | Ignition lookup literal at `0x496C0` | 3 | `b2941317c94f130833e350065980e96d44e1b60eef7c9e2ca6ce88b4b002bb89` | `168dfe3a155782a9960f72b9febc0e36` |
| 10 | Ignition lookup literal at `0x4E474` | 4 | `bc93046ef2d22cbe5f109c32745774e707e5246eb2e6b80b7cea44b1d5bd202a` | `94e77e558c21d8f42c33994bdd12034a` |
| 11 | Ignition lookup literal at `0x4E58C` | 5 | `7dae4b294a7833753ef3c3d4b64a61ba417a66bb894209bcabaf315b48f9b0ca` | `bc26a7aa8ad807d8b3ba8eeb5192c7bb` |
| 12 | Fuel Compensation lookup literal at `0x3C388` | 6 | `dc7dadadcc679eca88f07093967080051dc00994bbb7085b231596b040df475e` | `1ab39d163f242b18ebcbe6168eb37e1a` |
| 13 | Fuel Targets lookup literal at `0xC0020` | 7 | `80aa12d99145d1e51861c885f78485075e135b1cd218654d4abb7a5871c2837e` | `da8483cbe57a3672f3444b98b19fdbbc` |
| 14 | Startup Fuel Compensation lookup literal at `0x2CF1C` | 8 | `f0a03f6fef205aa1ac42e4471dd0bad995a7082c35d24bdb639fc342ccdda892` | `f1865bc339166c90151d7a32f7f4e136` |

Stage 06 changes 4542 bytes relative to Overlay 05: 4530 payload/storage
bytes and 12 checksum bytes, within a 4668-byte adjacent permitted set. Each
hook stage has a 24-byte permitted set and changes three hook bytes plus nine
or ten checksum bytes. Every image is one MiB and passes all six checksum
references. The final image equals an independently constructed combined lookup
endpoint while retaining the successful limiter runtime.

The ordered SHA-256 manifest is
`1JK08A-20260726-immo-e2-pops-fuel-throttle-ofc-v2-map-switching-overlay-v2-lookup.sha256`.
Ghidra 12.1.2 independently rebuilds the 48-byte helper and 256-byte adapter
spans with their locked SHA-256 values and passes 47/47 legacy-adapter p-code
cases over 718 instructions. The current complete-composition harness passes
116 cases over 5152 instructions, and the exact Overlay 06/07 caller gate passes seven cases
over 2333 instructions. RomRaider source commit
`874325319be98fc487e3875e5b26d25b8869e162` verifies revision-2 stages 06 and 07
as `ChecksumALT` 2/2 and `ChecksumALT2` 4/4, and recalculation is byte-identical.
The revision-2 lookup chain has hardware status `PASS_EXACT`. PCMFlash wrote
stages 06 through 14 in order, and identification returned `1JK08A00000`,
`7MFKAVN86`, and `23710-JK08A` after every stage. Stages 06 through 13 have
status `PASS`. The complete stage-14 readback is byte-identical to its input;
both have SHA-256
`f0a03f6fef205aa1ac42e4471dd0bad995a7082c35d24bdb639fc342ccdda892`
and MD5 `f1865bc339166c90151d7a32f7f4e136`, and all six stored checksum
references equal the independently calculated values. The PCMFlash log has
SHA-256 `bb23b1dd25b3f7c0681cecec2258d458591efe7afacff2c18b05113d11c954a2`.
This result validates application startup and PCMFlash identification with the
corrected adapters and all eight lookup hook literals active on the bench ECU.
It does not establish lookup behavior under engine conditions. Selector-host
execution and CAN feedback remain absent from this chain and retain separate
hardware gates.

`build_map_switching_full_dfco_overlays.py` emits five cumulative corrected
hardware gates from the byte-identical stage-14 readback. Stage 15 installs the inactive
96-byte four-family DFCO adapter, four Map 1-equivalent Hold copies, four Map
1-equivalent Intermediate Restore copies, and their pointer tables. Stage 16
routes the shared Hold and Entry call site at `0x4FDD0` through the new adapter.
Stage 17 routes the shared Full and Intermediate Restore call site at `0x50258`
through the same adapter. Stages 15 through 17 have no selector-host code or
hook and therefore remain fixed on Map 1. Stage 18 installs the 360-byte
selector-host unit and activates the scheduler literal at `0xCE8DC`, while the
CAN serializer literal at `0xC3FA4` remains stock and both feedback units
remain erased. A completed selector gesture would queue visual feedback that
cannot drain, so no map-selection gesture is permitted on stage 18. Stage 19
installs the 128-byte feedback wrapper, the 256-byte pulse engine, and the
serializer hook. Stage 19 equals the complete ten-family runtime endpoint for
the hardware source.

| Stage | Newly active component | SHA-256 | MD5 |
|---:|---|---|---|
| 15 | Inactive full-DFCO adapter, Hold and Intermediate Restore Map 1 storage | `5b7816f7be70e12f1312dbff9727df9a5677192811515ce8f6b66d1793bea7f2` | `c26b83085b76befe0ace9aaa7f99e0b6` |
| 16 | Shared Hold and Entry hook at `0x4FDD0` | `84796d58bdd3c45ba4c6774f936bedd54109cbee7a60053dcecf0b38c4777e58` | `aeea9d950f02ed177298fa03ca3fb7b1` |
| 17 | Shared Full and Intermediate Restore hook at `0x50258` | `e89bd22402e416c9178286b554b1d1d054586c49096574d1c88d9bd5e96f9e0d` | `a3bbd6562236859726824bce5311746f` |
| 18 | Corrected selector host and scheduler hook; boot-only, no map gesture | `f42f2ec56b590c7e82b17a343dc966c7c27c1981dde528815020e7d974d30b8c` | `738b0af89283fac2b47e83c187394326` |
| 19 | CAN feedback wrapper, pulse engine, and serializer hook; corrected complete runtime | `bcc34d531530e86b74de362df0db6c3c59597fa8095baaa056f6e4ba82ab7386` | `84f42719c82d1d554fdcce31a3367e1d` |

Stages 15 through 19 change `270, 9, 9, 365, 216` bytes from their immediate
predecessors inside adjacent permitted sets of `284, 24, 24, 384, 408` bytes.
Every image is one MiB, passes all six checksum references, preserves every
byte outside its cumulative component and checksum write set, and is locked to
source SHA-256
`f0a03f6fef205aa1ac42e4471dd0bad995a7082c35d24bdb639fc342ccdda892`.
The tracked `build_map_switching_full_dfco_overlays.py` tool defines the
corrected chain and ordered manifest with prefix
`1JK08A-map-switching-safe-v4`; generated output has no canonical directory.

The 2026-08-05 hardware run used the superseded stage-18 SHA-256
`4732168ad4aa0f8b8bf11e0b25b1ae506eed50713c789d3fb4297fafa9c37ac0`
and stage-19 SHA-256
`e2fb90d5d9f2ba23c09cb55ee77732175ae0753aabe77f8e7363a84554218ea1`.
Startup and identification passed for stages 15 through 19, but vehicle testing
showed that the selector cannot arm because those images require a nonexistent
`0x00` released-button code. No stage-19 readback or PCMFlash log accompanies
that report. The corrected generic stages 18 and 19 remain unflashed. The
selector implementation in custom Overlay 21 has target-vehicle evidence:
selector input and map commits pass, while its historical low-bit CAN 0x551
indicator field fails the V36 display-semantic gate. The current bits 5-6
feedback engine passes the software gates and remains hardware-untested.
Concrete tune profiles, per-image build recipes, generated ROMs, checksum
sidecars, and logs remain local artifacts outside the repository.

The complete instruction audit covers all 418 final-runtime instructions. It
independently verifies 40 delayed transfers and their encoded `NOP` slots, 52
PC-relative references and their effective literal addresses, 79 direct branch
targets, and 21 indirect control-transfer encodings. The startup-trampoline and
startup-selector-init gate sources add 13 alternative instruction instances,
three delayed transfers, and three PC-relative references under the same gate.
All ten source units, including the two historical startup gates, rebuild
through Ghidra with their exact locked hashes.
The corrected exact-stock full-ROM fixture has SHA-256
`b092abe21ca412a88e3ced398354763a3ab6b778f5a1c3b3a8e2e4e507ce232f`;
its startup harness passes at 1810 instructions and its exact reset differential
passes nine seeds at 33,660 instructions. No other delayed slot contains an
executable instruction, and no other PC-relative reference resolves away from
its declared literal.

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
| Overrun | DFCO Hold RPM Threshold | `0x126E4` | `1x16 uint8` |
| Overrun | DFCO Entry RPM Threshold | `0x12718` | `1x16 uint8` |
| Overrun | DFCO Full Restore RPM Threshold | `0x12818` | `1x16 uint8` |
| Overrun | DFCO Intermediate Restore RPM Threshold | `0x1298C` | `1x16 uint8` |

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
selection behavior are closed for all ten families at the reference-model
level. The eight adapter-backed families have assembled and p-code-emulated
accessors, and both direct limiter families have an assembled atomic shadow
transaction and startup path. The selector and feedback paths are also
assembled and p-code-emulated. Deterministic byte composition is closed for the
locked `10, 10` feedback configuration, including execution of all 116 p-code
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
| `0x00` | invalid/unobserved vehicle state |
| `0x02` | CANCEL |
| `0x08` | SET/COAST |
| `0x10` | RESUME/ACCEL |
| `0x20` | released, all buttons off |

The MAIN state is represented separately by `0xFFFF41AE.bit7`; it is not a
button code in the selector grammar. The code assignments above are confirmed
by the vehicle capture of CAN frame `0x239`, byte 4. The final mapping from the
captured frame to `0xFFFF2A85` remains subject to the Overlay 21 functional
test, while the previous `0x00` release interpretation is contradicted by the
captured neutral state and the observed selector behavior.

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
ebc0fb3e4ccd177e47c4420b90fb49a360e00f3bedceca11b3cdf2a4590e6e4c
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
protected-register preservation. All cases pass over 1468 executed
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
`ROM8[0x8000]=0xFF` and the first byte at `0x8080`. An input value of `0xEE`
produces selector `0xFE`; the marker hardware readback value `0x00` produces
selector `0xF0`. Both are accepted, match header marker
`ROM32[0xFFF84]=0x4E4855F9`, and enter TRAPA `0x3E`, whose vector is
`FUN_00027E24`. That handler calls the stock startup thunk and then remains in
its scheduler loop. It does not return to the fallback call of
`FUN_00002B8E`, which is the only caller of `FUN_0000284E`.

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
released (0x20) -> SET                  arm, count=0
SET -> CANCEL -> SET                    count=count+1
SET -> released (0x20) with count=1     commit map 1
SET -> released (0x20) with count=2     commit map 2
SET -> released (0x20) with count=3     commit map 3
SET -> released (0x20) with count=4     commit map 4
SET -> released (0x20) with count=5     commit map 5
```

The selector timeout is 100 selector invocations, including the arming
invocation. The wall-clock duration is not claimed because the period of
`FUN_000CE854` has not been measured. Expiration wins over a transition on the
same invocation.

The following conditions abort and retain the active map:

- release before the first complete CANCEL pulse;
- RESUME/ACCEL, `0x00`, or another unexpected code while armed;
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
half-open interval `[0xD2108, 0xD4000)`:

| ROM range | Purpose |
|---|---|
| `0xD2108..0xD226F` | host wrapper, selector, diagnostic mirror, and feedback queue control |
| `0xD2270..0xD229F` | shared fail-closed adapter selection helper |
| `0xD22A0..0xD22FF` | startup and limiter-shadow initialization wrapper |
| `0xD2300..0xD233F` | overrun lookup adapter |
| `0xD2340..0xD237F` | ignition lookup adapter |
| `0xD2380..0xD23BF` | fuel-compensation lookup adapter |
| `0xD23C0..0xD23FF` | fuel-target lookup adapter |
| `0xD2400..0xD247F` | DFCO Entry and Full Restore copies |
| `0xD2480..0xD24DF` | four-family DFCO lookup adapter |
| `0xD24E0..0xD24F3` | DFCO Hold five-entry pointer table |
| `0xD24F4..0xD24FF` | alignment reserve |
| `0xD2500..0xD28FF` | Ignition Timing Trim Main copies |
| `0xD2900..0xD2CFF` | Ignition Timing Trim High Det copies |
| `0xD2D00..0xD30FF` | Fuel Targets copies |
| `0xD3100..0xD34FF` | Fuel Compensation Main copies |
| `0xD3500..0xD351F` | Rev Limit - Fuel Cut copies |
| `0xD3520..0xD3527` | Rev Limit - Throttle Cut copies |
| `0xD3528..0xD353B` | DFCO Intermediate Restore five-entry pointer table |
| `0xD353C..0xD353F` | alignment reserve |
| `0xD3540..0xD35DF` | eight five-entry ROM pointer tables |
| `0xD35E0..0xD365F` | CAN 0x551 CRUISE-feedback wrapper |
| `0xD3660..0xD375F` | atomic limiter-shadow commit |
| `0xD3760..0xD385F` | fail-closed feedback pulse engine and frame-count configuration |
| `0xD3860..0xD3F7F` | unallocated by map switching; available to a separately validated extension |
| `0xD3F80..0xD3FBF` | DFCO Hold copies |
| `0xD3FC0..0xD3FFF` | DFCO Intermediate Restore copies |
| `0xD4000..0xE1C29` | unallocated within the conservative free region |
| `0xE1C2A..0xFFF7F` | fill tail, not allocated by this contract |

Code ranges are fixed envelopes; assembly must fit each entry without changing
the calibration or pointer-table addresses. Unused bytes remain `0xFF`.

`AuditFreeRegion.java D2108 D3FFF FF` is the reproducible gate for the claimed
allocation interval. `AuditFreeRegion.java D2108 E1C29 FF` additionally checks
the remaining conservative region. Both runs require `status=PASS` with zero
bad bytes, instructions, data objects, functions, and references.

## Verified calibration accessors

### Adapter-backed families

Eight families enter stock interpolation wrappers through replaceable function
literals. Each injected adapter recognizes only its approved canonical bases,
selects one pointer from the manifest table, and tail-jumps to the original
wrapper with the incoming PR. Every unrecognized base passes through unchanged.
An invalid index selects map 1.

| Family | Stock base | Stock wrapper | Hook literals | Adapter | Maps 2-5 |
|---|---:|---:|---|---:|---|
| DFCO Hold RPM Threshold | `0x126E4` | `0x26388` | `0x4FDD0` | `0xD2480` | `0xD3F80`, `0xD3F90`, `0xD3FA0`, `0xD3FB0` |
| DFCO Entry RPM Threshold | `0x12718` | `0x26388` | `0x4FDD0` | `0xD2480` | `0xD2400`, `0xD2410`, `0xD2420`, `0xD2430` |
| DFCO Full Restore RPM Threshold | `0x12818` | `0x26388` | `0x50258` | `0xD2480` | `0xD2440`, `0xD2450`, `0xD2460`, `0xD2470` |
| DFCO Intermediate Restore RPM Threshold | `0x1298C` | `0x26388` | `0x50258` | `0xD2480` | `0xD3FC0`, `0xD3FD0`, `0xD3FE0`, `0xD3FF0` |
| Ignition Timing Trim Main | `0x09A1A` | `0x26230` | `0x496C0`, `0x4E474`, `0x4E58C` | `0xD2340` | `0xD2500`, `0xD2600`, `0xD2700`, `0xD2800` |
| Ignition Timing Trim High Det | `0x09B1A` | `0x26230` | `0x496C0`, `0x4E474`, `0x4E58C` | `0xD2340` | `0xD2900`, `0xD2A00`, `0xD2B00`, `0xD2C00` |
| Fuel Targets | `0x0B33A` | `0x261B8` | `0xC0020` | `0xD23C0` | `0xD2D00`, `0xD2E00`, `0xD2F00`, `0xD3000` |
| Fuel Compensation Main | `0x0A29A` | `0x261F0` | `0x2CF1C`, `0x3C388` | `0xD2380` | `0xD3100`, `0xD3200`, `0xD3300`, `0xD3400` |

The ignition adapter receives Main, High Det, and Cold bases from shared call
sites. It redirects `0x09A1A` and `0x09B1A` only. Cold
`0x0991A` and every other base continue to stock storage. The DFCO adapter
recognizes all four live overrun tables dynamically: `0x12718` is the rising-edge entry threshold,
`0x126E4` is the held-request threshold, `0x12818` is the lower/full-restore
threshold, and `0x1298C` is the upper/intermediate-restore threshold. Every
other base continues to stock storage.

`FUN_0004FBE2` calls the overrun Cut wrapper for `0x126E4` at `0x4FC08` and
`0x12718` at `0x4FC16`. `FUN_00050018` calls the Restore wrapper for `0x1298C`
at `0x500AC` and `0x12818` at `0x500BC`. These mixed call sites require base
discrimination; redirecting every call would switch an unapproved table.

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
The layout locks the three adapter units:

| Unit | ROM envelope | Instructions | Data bytes | Blob SHA-256 |
|---|---|---:|---:|---|
| Shared helper | `0xD2270..0xD229F` | 11 | 4 | `40cea0183a38d189808b7637ea47cb594d8cb56ee615efb246c714da5f499a34` |
| Four adapters | `0xD2300..0xD23FF` | 48 | 64 | `a938e1334e7850a0c368c50e98dbbdf67bc2589524025659a31d5b5f328c0e6c` |
| Four-family DFCO adapter | `0xD2480..0xD24DF` | 27 | 36 | `2a5a65671e077400b753cb7fabb15c0520ddd7e96be8234e44297b6cd7052ba7` |

`map_switching_assembly.py` independently verifies that each entry label and
literal matches the authoritative manifest. The source may use only
`r0..r4`; it cannot modify `r5..r15`, PR, GBR, MACH, or MACL and contains no
explicit SR access. SH comparison instructions may update the caller-clobbered
T bit; p-code execution verifies that every other SR bit remains unchanged.
Every adapter loads the stock-wrapper address into `r3` before dispatch. Every
recognized path uses `NOP` in the `BRA` delay slot and tail-jumps through `r3`;
every pass-through path also tail-jumps through `r3` with a `NOP` delay slot.
The source validator rejects every other `BRA` delay-slot instruction. This is
required because an SH-2E PC-relative move in that slot derives its PC from the
branch destination rather than the static slot address.

`tools/ghidra/EmulateMapSwitchingAdapters.java` executes the assembled bytes,
not the Python reference model. Its 76 cases cover all five slots for all eight
families, active indices 5 and 255, Cold Ignition, the historical overrun
pass-through cases, unknown bases, exact stock-wrapper destinations, and
preservation of `r5..r15`, PR, GBR, MACH, and MACL. The result is 76/76 PASS
over 1286 executed instructions.

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

`map_switching_compose.py` accepts exactly the eight manifest-locked assembly
blobs. It validates every length and SHA-256, materializes 40 calibration
copies and ten five-entry pointer tables, applies all 14 hook literals, and
places every assembly unit at its declared final address. The complete result
is compared byte-for-byte with the declared write set.

The locked exact-stock fixture produces:

```text
in_memory_sha256=108613e626f883ecca7a5733b739edafaacaee663909bfb115a6e8dda0d64c19
changed_bytes=5638
permitted_write_bytes=6144
feedback_frame_counts=10,10
instruction_placements=418
code_entries=11
```

The 6144-byte write set consists of 6088 bytes allocated under the layout plus
56 bytes occupied by the 14 four-byte hook literals. Filler bytes and source
bytes that already equal their composed values are permitted writes but do not
appear in `changed_bytes`. Any changed byte outside this set fails validation.
Every source instruction is also tied to the corresponding bytes at its final
absolute address, and all eleven declared code entries must begin on an
instruction. Ghidra independently round-trip decodes the same SHA-locked blobs.

`EmulateMapSwitchingComposition.java` begins with the exact one-MiB stock
program, independently applies the eight blobs, 14 hooks, 40 copies, and ten
pointer tables, and refuses any fixture whose hash or write boundary differs.
Each scenario receives a fresh emulator loaded with the complete fixture.
Deterministic stubs replace only the three stock callees outside the injected
implementation; feedback cases may additionally replace only the two
frame-count bytes. The harness executes the same 17 selector, 76 adapter, 14
startup/limiter, and nine feedback scenarios over 5152 instructions. It
reaches all eleven declared code entries, checks real copied calibration bytes,
verifies exact limiter SR restoration, and permits only the caller-clobbered T
bit to differ on comparison-heavy adapter, selector, and feedback paths.

This hash identifies an ephemeral verification result, not a ROM release.
Stored checksum fields remain stock, `flashable=false`, and the pure composer
has no output-file option. Python tests cover deterministic composition,
complete blob-set enforcement, hash rejection, hooks, copies, pointer tables,
locked feedback counts, rejection of an out-of-contract byte, and static
agreement between the Ghidra harness and the authoritative layout manifest.

`apply_map_switching.py` owns file creation. Its compatible-input gate permits
changes only below `0x20000`, while requiring the exact calibration identity,
hook anchors, CAN serializer anchors, erased allocation, and complete protected
upper partition. It also requires a self-consistent input checksum state. The
patcher initializes all 40 alternate-map copies from the input Map 1 values,
installs the ten pointer tables, 14 hooks, and eight tracked payloads, then
recalculates checksums in this order:

```text
self-test B -> self-test A -> SUM16 A -> SUM16 B
```

The final declared write set contains the 6144 composition bytes plus 20
checksum-reference bytes. Every input byte outside this set must remain exact.
The output is independently checksum-verified before an exclusive create, and
an MD5 sidecar is created for the flashing workflow. Patcher and checksum tests
cover compatible calibration changes, exact preservation,
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

The projection contains 50 slot-specific calibration tables. The masked bit-7
views for both switched ignition families add ten slot-specific editor views,
for 60 slot-specific views in total. Cold ignition keeps its one global masked
view. A read-only validation against the live graph and tracked common
definitions reports:

```text
canonical graph maps:       450
projected maps:             490
calibration tables:          58
masked views:                11
slot calibration tables:     50
slot masked views:           10
slot editor views:           60
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

The serializer reads `RAM8[0xFFFF40D0] & 7`, shifts it left by four, clears
payload mask `0x70`, and writes the three-bit state into byte-5 bits 4..6. It
constructs byte-5 bits 0..1 independently from `0xFFFF4185`, `0xFFFF2451`, and
`0xFFFF417F`. The current feedback engine changes only bits 5-6 with mask
`0x60`, leaving bit 4 and both independently constructed low bits intact.

Public G37/370Z captures report complete byte-5 values `0x02` for MAIN OFF,
`0x62` for MAIN ON, and `0x42` for SET/engaged. They map exactly to internal
serializer states `0`, `6`, and `4` in bits 4..6. The target-vehicle failure is
consistent with the historical low-bit override: its injected `2/0` sequence is
present on the bus, but no requested indicator changes. Successful later
selection of Map 3 proves that the wrapper still advances and completes the
queued Map 2 feedback sequence.

The current feedback contract remains on CAN 0x551 byte 5 and changes only mask
`0x60`: on value `0x60`, off value `0x00`. With ASCD inactive, the
stock-first wrapper produces `0x62` and `0x02` while preserving bits 0..4 and
7. This mapping is code-grounded and supported by public vehicle captures, but
it retains hardware-test status until the V36 combination meter confirms it.

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
0xFFFF3ADA.bits5..6 = 3  for candidate pulse on
0xFFFF3ADA.bits5..6 = 0  for candidate pulse off
```

All other byte-5 bits and all other payload bytes retain the stock serializer
result. The wrapper
advances the pulse engine once per frame 0x551
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
925a7ebc321e965bfed0fdfdc7e06287b6b794b0525226c4bd9a11187bc1f66f
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
balance. All cases pass over 856 executed instructions.

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

1. On a known-working bench ECU, write the SHA-locked marker-only image, power
   cycle, confirm identification, and obtain a complete readback. Require exact
   marker and checksum bytes plus a full-image comparison that permits only an
   explicitly characterized reset-selector line. The 2026-08-04 transaction
   passes with the sole `0x8080` variant described above.
2. Write the startup-trampoline gate built only from the successful marker
   readback, power cycle, confirm identification, and obtain a complete
   readback. Require the exact startup hook, 12-byte trampoline, checksum
   references, and all other bytes. The 2026-08-04 transaction has status
   `PASS_EXACT`: the readback equals the input byte for byte.
3. Write the startup selector-init gate built only from the successful
   trampoline readback, power cycle, confirm identification, and obtain a
   complete readback. Require exact equality with the input image. This gate
   adds one persistent RAM write to `0xFFFF5D00` and no other runtime feature.
   The 2026-08-04 transaction has status `PASS_EXACT`: the readback equals the
   input byte for byte.
4. Write the five cumulative limiter overlays strictly in numeric order. After
   every write, power cycle and confirm identification before proceeding. Do
   not require an intermediate readback. Stage 01 installs inactive payload and
   storage, stage 02 executes startup commit with stock consumers, and stages
   03 through 05 activate the fuel, throttle-cluster, and throttle-scalar hooks
   one at a time. All five stages pass on the bench ECU; stages 01 through 04
   have hardware status `PASS`, and the byte-identical stage 05 readback gives
   the complete limiter endpoint hardware status `PASS_EXACT`.
5. Write revision-2 lookup overlays 06 through 14 strictly in numeric order.
   Do not write the first-revision files whose names lack `overlay-v2`. Stage 06
   installs inactive code and Map 1-equivalent storage. Stages 07 through 14
   activate literals `0x4FDD0`, `0x50258`, `0x496C0`, `0x4E474`, `0x4E58C`,
   `0x3C388`, `0xC0020`, and `0x2CF1C` one at a time. The chain has status
   `PASS_EXACT`: stages 06 through 13 pass write, power cycle, and
   identification, while the byte-identical stage-14 readback gives the
   complete lookup endpoint status `PASS_EXACT`.
6. Write full-DFCO stages 15 through 17 in numeric order, power cycle, and
   confirm identification after each write. Stage 15 installs inactive code,
   Map 1-equivalent Hold and Intermediate Restore storage, and pointer tables.
   Stage 16 activates the shared Hold and Entry hook. Stage 17 activates the
   shared Full and Intermediate Restore hook. Selector-host and CAN feedback
   remain absent in all three stages.
7. Write stage 18, power cycle, and confirm identification without operating
   the ASCD selector buttons. This stage is a boot-only selector-host gate; a
   completed selection would queue feedback that cannot drain while the CAN
   serializer remains stock. Then write stage 19, power cycle, confirm
   identification, and optionally obtain a complete readback before functional
   map selection. Stage 19 adds CAN feedback and is the complete runtime endpoint.
   The 2026-08-05 run reports `PASS` for stages 15 through 19. A complete
   readback remains optional evidence for upgrading the final endpoint to
   `PASS_EXACT`; it is not required to begin the non-running functional test.
8. Patch a checksum-valid compatible input with `apply_map_switching.py` and
   retain the reported input/output SHA-256 values and MD5 sidecar.
9. Verify that Map 2 through Map 5 equal the input Map 1 in all ten families,
   all checksum domains pass, and the common `JK08A` XML/XDF projection matches
   the layout.
10. The target switch assembly passes the raw ladder sequence
   `SET -> CANCEL -> SET` and commits Maps 2 and 3.
11. Treat the historical CAN 0x551 byte-5 low-bit state `2` as rejected. Its
   injected state reaches the bus, but the requested indicator remains
   unchanged.
12. Compose a local hardware candidate at a caller-selected path, retain its
   SHA-256 and MD5 with the local test record, write that candidate, and confirm
   one through five CRUISE indications with the engine stopped and ASCD
   inactive. The installed field uses byte-5 mask `0x60`, on `0x60`, and off
   `0x00`.
13. Confirm reset Map 1 by the selected calibration behavior after an ignition
   cycle; no custom diagnostic request is part of this procedure.
14. Measure the extended startup clear and commit critical-section latency.
15. Confirm unchanged lookup outputs for every input index in all five selector
   states.
16. Start the engine with byte-identical maps and exercise all five selections
   before changing any alternate map.

Ground truth remains the physical ECU and engine.
