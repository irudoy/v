# Ghidra headless tools

This directory contains Java GhidraScript extractors, focused inspection tools,
assembly helpers, and deterministic SH-2E p-code fixtures. Ghidra output is
derived data. Reviewed CSV annotations, assembly, layout manifests, stock ROM
identities, and hardware records remain the tracked evidence sources.

Tool versions and machine-local project locations are recorded in
`../README.md`. The wrapper selects JDK 21 and the Homebrew Ghidra installation:

```bash
tools/ghidra/headless-analyze.sh <project-dir> <project-name> <Ghidra options>
```

## Import

Import an exact ROM as a raw, big-endian SH-2E program using Ghidra's SH-2A FPU
language:

```bash
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -import rom-images/23710-JK08A/1JK08A-20260726-stock.bin \
  -processor "SuperH:BE:32:SH-2A" \
  -loader BinaryLoader -loader-baseAddr 0x0
```

`-process` accepts the program name stored inside the Ghidra project, not a ROM
filesystem path. Ghidra projects and export directories remain outside Git.

## On-demand decompilation and listings

`decompile.sh` decompiles functions and, with `-l`, dumps their complete
listings without a GUI. The ROM key selects the Ghidra program, outputs land in
`~/tools/ghidra-projects/export-<ROM>/` as `decomp_<addr>.c` and
`funclisting_<addr>.txt`, cached files are reused, and the output paths are
printed:

```bash
tools/ghidra/decompile.sh -l 0002a5cc 0002a36a
tools/ghidra/decompile.sh -r JK00C -o /tmp/inspect 000bfe88
tools/ghidra/decompile.sh -r 1ND3B -p <program-name> 0007d3e8
```

A program keeps the file name it was imported under. `program_name.py` reads
the project index `<project>.rep/idata/~index.dat` and takes the program named
after the registered stock image, or else the only root-folder program whose
name contains the ROM key; `-p` names the program directly. Every headless run
starts with `ProgramSha256.java`, which reports the executable SHA-256 that
Ghidra recorded at import. The wrapper stages the output and moves it into the
export directory only when that value equals the SHA-256 of the registered
stock image, so a program cannot stand in for a different dump.

`-f` reruns Ghidra for files that already exist. The script wraps
`DecompileFuncs.java` and `DumpFuncListing.java`; the project location and
name follow `GHIDRA_PROJECT_DIR` and `GHIDRA_PROJECT_NAME` when set.

## Canonical structure exports

`ExportGraph.java` writes `funcs.csv` and `calls.csv`.
`ExportXrefs.java` writes peripheral, RAM, and literal-pool references to
`xrefs.csv`. `ExportFunctionSignatures.java` writes relocation-tolerant
`function_signatures.csv`, call-site ordinal data to `function_sites.csv`, and
ROM literal/reference data and direct SH7058/SH7059 RAM references from
`0xFFFE8000` upward to `function_references.csv`.
`ExportFunctionTokens.java` writes normalized
instruction sequences for bounded structural-similarity review. Literal values
and symbol addresses are folded, while register numbers remain part of the
instruction shape. A typical read-only export is:

```bash
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -process <program-name> -noanalysis -readOnly \
  -scriptPath tools/ghidra \
  -postScript ExportGraph.java <export-dir> \
  -postScript ExportXrefs.java <export-dir> \
  -postScript ExportFunctionSignatures.java <export-dir> \
  -postScript ExportFunctionTokens.java <export-dir>
```

`RecoverFuncs.java`, `AnalyzeFuncs.java`, and `RenameFuncs.java` intentionally
mutate the local Ghidra project and must run without `-readOnly`. A seed that
`RecoverFuncs.java` disassembles itself carries no operand references until
`AnalyzeFuncs.java` runs the program analyzers over the created bodies; without
that pass `xrefs.csv` lists no RAM or peripheral access for the recovered
functions. `symbols.csv` is the tracked function-name registry. Export after
those mutations persist successfully.

The complete ROM loader performs header, foreign-key, address, and source-model
preflight before graph writes; see `../memgraph/README.md`.

## Script groups

| Group | Scripts | Purpose |
|---|---|---|
| Structure | `ExportGraph`, `ExportXrefs`, `ExportFunctionSignatures`, `ExportFunctionTokens`, `RecoverFuncs`, `AnalyzeFuncs`, `RenameFuncs` | Maintain and export function, call, reference, and cross-ROM signature structure |
| Map discovery | `FindInterpCore`, `MapInventory`, `DirectLookupInventory`, `ResolveAccessors`, `ScanFlags` | Discover interpolation families, operands, accessors, axes, and local selectors |
| Diagnostics | `ExportDiagnosticRefs`, `ScanImmoAnchors`, `TraceRamAccesses`, `InventoryGbrAccesses`, `InventoryPointerArgs` | Produce semantic-free review inputs for diagnostic and RAM binding analysis |
| Inspection | `InspectAddress`, `DumpListing`, `DumpFuncListing`, `DecompileFuncs`, `FindTableRefs`, `FindPoolWords` | Inspect ownership, references, functions, listings, pools, and decompilation |
| Patch construction | `AuditFreeRegion`, `AssembleSh2` | Prove erased envelopes and assemble bounded Ghidra payload fixtures |
| P-code execution | `EmulateThrottleLimiter`, `EmulateMapSwitching*` | Execute stock limiter behavior and reconstruct current map-switching behavior in Ghidra |

Each script documents its positional arguments in its source header. Generated
CSV and listings belong in a machine-local export directory.

## Cross-ROM function correspondence

`ExportFunctionSignatures.java` hashes exact instruction bytes, mnemonic
sequences, and normalized instruction shapes for every recovered function.
The companion site export records each `jsr` and `bsr` by instruction ordinal
inside its function. The reference export records loaded bytes and pool
locations for ROM references and direct SH7058/SH7059 RAM targets at the same
ordinal.
Ordinals keep resolver callsites, literals, and direct application-state
accesses comparable when a homologous function changes instruction widths or
literal-pool placement.

`tools/rom_correspondence.py` pairs unique exact-byte functions first and then
unique normalized shapes. With two interpolation registries, their reviewed
correspondence file, and complete resolver censuses, it also emits candidate
map and axis address pairs. Ambiguous source or target operands are retained
with a non-unique status rather than guessed.

Run the comparison through the repository entry point:

```bash
make rom-correspondence \
  CORRESPONDENCE_SOURCE_EXPORT=tmp/source-export \
  CORRESPONDENCE_TARGET_EXPORT=tmp/target-export \
  CORRESPONDENCE_OUTPUT=tmp/function-correspondence.csv
```

`CORRESPONDENCE_ARGS` passes optional script flags for the selected analysis
mode. The Make target remains the supported orchestration boundary; the Python
module owns the comparison logic.

Cross-generation analysis can also compare complete operand byte extents
inside paired explicit interpolation contracts. A `unique` exact-storage row
means that one equal-byte target was found among those compared contracts. It
does not exclude a recalibrated homolog with different bytes and therefore is
not sufficient for automatic semantic projection.

A unique exact map-storage pair may anchor an accessor pair when each side has
one accessor for that map in the same reviewed contract. The ordered-entity
mode then compares the anchored accessor's callsites by wrapper-local order,
requiring equal callsite and branch cardinality. Exact-storage, accessor, and
ordered-entity CSVs remain independent candidate reports. Agreement strengthens
structural evidence; disagreement requires instruction-level review.

The optional structural mode starts from unique function hashes and reviewed
interpolation kernel and wrapper pairs. It adds accessors with unique
interpolation-call signatures, then iteratively adds functions with a unique
incoming and outgoing fingerprint against at least two mapped neighbors.
Structural map and axis candidates use wrapper-local call order, not equal
instruction ordinals. This mode remains a candidate generator and does not
promote graph similarity into semantic inheritance.

## RAM writer instruments

`TraceRamAccesses.java` resolves constant addresses through the decompiler,
`InventoryGbrAccesses.java` resolves GBR-relative accesses through the nearest
`ldc` site, and `InventoryPointerArgs.java` joins pool-constant call arguments
with parameter-relative stores. None of them sees a block copy whose address or
length is built by register arithmetic: on JK78C the periodic-list walker
`FUN_00020F1A` latches whole RAM blocks through `FUN_00022164` and
`FUN_000225C0`, so a cell without a direct static writer is checked against its
copy groups before any other conclusion.

## Address inspection

`InspectAddress.java` combines address ownership, inbound references, and
optional decompilation for all participating functions:

```bash
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -process <program-name> -noanalysis -readOnly \
  -scriptPath tools/ghidra \
  -postScript InspectAddress.java <output-dir-or-dash> 1495a 21ce0
```

Use a dash for stdout-only inspection. Use `DumpListing` for instruction-level
context, `DumpFuncListing` for a complete function body, `FindPoolWords` for
resolved `mov.w` literals, and `FindTableRefs` for a bounded table range.

## Operand resolver

`ResolveAccessors.java` works from the same kernel-slot-wrapper-callsite set as
the map inventory. It compares linear backtracking with decompiler data flow,
preserves branch-selected operand sets, resolves reviewed byte-copy helpers,
and emits one `accessors.<kernel>.csv` per registered interpolation entry.

Run it once for every entry in `defs/JK08A.interp.csv`. The loader rejects a
missing census, unsupported branching alignment, an accessor absent from the
exported function set, or a target image that does not match its registry.
Algorithm and ingestion details are in `../map-analysis-pipeline.md`.

A library that fuses wrapper, kernel, and axis search into one self-contained
leaf per access has no wrapper level: callers load the leaf address from a
literal-pool word and `jsr` it. The `fused` token after the entry address
selects the direct census in both `ResolveAccessors.java` and
`MapInventory.java`: the entry is its own wrapper, the sites are the call
references to the entry, and the slot is the pool word the site loaded. The
registry declares such an entry with `kernel` equal to `wrapper`. 1ME3B is the
precedent; its 34 registered leaves are censused with

```bash
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -process 11ME3B-20260825-stock.bin -noanalysis -readOnly \
  -scriptPath tools/ghidra \
  -postScript ResolveAccessors.java ~/tools/ghidra-projects/export-1ME3B 2a9f4 fused
```

repeated per registry row.

## Stock throttle-limiter p-code coverage

`EmulateThrottleLimiter.java` SHA-locks the stock JK08A ROM and executes the
unmodified function at `0x0007584E`. Its focused cases cover the disabled early
return, filter initialization and recurrence, coolant hysteresis, all dynamic
threshold directions and gates, steady-state request boundaries, fast-ramp
transition, recovery tracking and rollback, forced neutral, auxiliary output,
and equality behavior.

An optional CSV path enables a 7200..7800 candidate-RPM sweep at four APP
requests. The same run publishes the most restrictive request through exact
stock functions `0x00070D82` and `0x00079030`, then executes an isolated target
projection through `0x0003DE4C`, `0x000730FC`, `0x00072C3C`, and both channel
calls to `0x0006F48C`:

```bash
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -process 1JK08A-20260726-stock.bin -noanalysis -readOnly \
  -scriptPath tools/ghidra \
  -postScript EmulateThrottleLimiter.java <output.csv>
```

The projection seeds unrelated signed bounds as permissive, sets idle and
subtractive area terms to zero, and enables symmetric normal channel handling.
It verifies exact composition but is not a vehicle target prediction. Generated
CSV output is a local test artifact and is not tracked.

## Current map-switching p-code coverage

The current runtime is reconstructed from `patches/map-switching-layout.toml`,
`patches/map-switching-payloads.toml`, and the assembly sources named by the
layout.

| Harness | Responsibility |
|---|---|
| `EmulateMapSwitchingComposition.java` | Reconstruct the closed composition and execute every declared selector, adapter, startup, limiter, and feedback entry |
| `EmulateMapSwitchingBoot.java` | Execute the stock startup thunk, initializer, wrapper, lookup path, and limiter commit |
| `EmulateMapSwitchingReset.java` | Execute the TRAPA startup path and a scheduler period while checking reset and RAM boundaries |
| `EmulateMapSwitchingSelector.java` | Exercise selector state, release, commit, and fail-closed inputs |
| `EmulateMapSwitchingAdapters.java` | Exercise current lookup adapters, normalization, dispatch, and register preservation |
| `EmulateMapSwitchingLimiter.java` | Exercise atomic limiter publication and RAM shadows |
| `EmulateMapSwitchingFeedback.java` | Exercise CAN feedback serialization, timing, and payload preservation |

`tools/sh-elf-run/verify_map_switching.py` independently reconstructs the exact
instruction bytes with GNU SH tools and executes the current composition. The
Ghidra harnesses complement that mandatory gate; they do not replace it.

## Retired stage harness replacement

The removed hardware-isolation harnesses targeted intermediate images that are
not build products. Their current responsibilities and durable evidence are:

| Retired harness | Current replacement | Durable result record |
|---|---|---|
| `EmulateMapSwitchingTrampoline.java` | `Boot`, `Reset`, `Composition`, and GNU startup execution | `patches/hardware-results.toml` |
| `EmulateMapSwitchingSelectorInit.java` | `Boot`, `Reset`, `Composition`, and GNU startup execution | `patches/hardware-results.toml` |
| `EmulateMapSwitchingLimiterGate.java` | `Limiter`, `Boot`, `Reset`, `Composition`, and GNU limiter execution | `patches/hardware-results.toml` |
| `EmulateMapSwitchingLookupGate.java` | `Adapters`, `Composition`, GNU adapter execution, and the delay-slot negative fixture | `patches/hardware-results.toml` |

Git history retains the stage-specific builders and harness source. The result
manifest retains image identities, readbacks, outcomes, and the unsafe
delay-slot incident without keeping retired build paths live.

## Safety boundary

P-code behavior is not silicon behavior. Ghidra does not model every SH-2E
hardware rule or peripheral. A firmware image is ineligible for hardware
testing unless the current GNU executable gate passes. Bench observation,
controlled write/readback, and vehicle behavior remain separate evidence.
