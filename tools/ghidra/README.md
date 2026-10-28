# Ghidra headless tools

This directory contains Java GhidraScript extractors, focused inspection tools,
assembly helpers, and deterministic SH-2E p-code fixtures. Ghidra output is
derived data. Reviewed CSV annotations, assembly, layout manifests, stock ROM
identities, and hardware records remain the tracked evidence sources.

Tool versions and machine-local project locations are recorded in
`../README.md`. The wrapper uses the pinned Ghidra release and JDK 21:

```bash
tools/ghidra/headless-analyze.sh <project-dir> <project-name> <Ghidra options>
```

`GHIDRA_HOME` selects the installation containing `Ghidra/` and `support/`;
`JAVA_HOME` selects the JDK containing `bin/java`. Explicit paths work on Linux
and macOS without Homebrew:

```bash
GHIDRA_HOME=/opt/ghidra JAVA_HOME=/opt/jdk-21 \
  tools/ghidra/headless-analyze.sh <project-dir> <project-name> <Ghidra options>
```

Each unset path uses its Homebrew installation: `ghidra` for Ghidra and
`openjdk@21` for the JDK. The wrapper preserves each supplied path, rejects an
unusable installation, and refuses a Ghidra version different from the pin in
`headless-analyze.sh`.

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
filesystem path. Ghidra projects and local export directories remain outside
Git; the normalized L0 exports of every layout live in `l0/`.

## Version change

The wrapper refuses an installation whose version differs from its pin, and
`brew pin ghidra` holds the Homebrew formula at that version. A new pin
reanalyzes every program of the project before the L0 export:

```bash
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -process <program-name>
```

Without `-noanalysis` and `-readOnly`, HeadlessAnalyzer reruns the
auto-analysis of the installed version over the whole program and saves it.
The reanalysis recreates the function fragments of the analysis artifacts that
[Function fragments](#function-fragments) describes, so each program of a
layout with a registry `merges/<layout>.csv` then runs `MergeFuncs.java` with
that registry, and each program of a layout with `symbols/<layout>.csv` runs
`RenameFuncs.java` with it:

```bash
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -process <program-name> -noanalysis -scriptPath "$PWD/tools/ghidra" \
  -postScript MergeFuncs.java "$PWD/tools/ghidra/merges/<layout>.csv"
```

`export-l0.sh` then re-exports every layout; each manifest records the pinned
version, and the `l0` check of `kb check` fails on a manifest of another
version or on a fragment of a registry that the export lists as a function
entry. The export logs a `review:` line for every function of a `kb` symbol
of the layout whose entry disappears or whose body changes size, and for every
new entry inside a former body. Each reported function is re-reviewed before
the export is committed: a new fragment of an artifact joins its function
through the registry and another run of `MergeFuncs.java`, and a real split
moves the ledger rows and `kb` symbols to the functions that hold the code.
The decompilation outputs follow without a manual purge, because their cache
key includes the digest of the L0 manifest.

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

A configured layout prepares reviewed entries and fragments in every on-demand
session before code output. The installed `kb.ghidra_preparation` module
supplies the same exact-image plan as the L0 export. The repository
`preparation.py` entry exposes that API without a second implementation.
The installed console requires no repository-specific Python import path.
The program remains read-only. Output digests, the primary
code scripts, and the preparation inputs bind the cache key. A changed key
requires verified replacement outputs before the previous cache is removed.
A failed script, missing requested output, rejected preparation, or promotion
error retains accepted code and its key. The primary process log is retained
when output acceptance fails. Cache replacement has exception rollback; it is
not a filesystem-wide or graph transaction.

A program keeps the file name it was imported under. `program_name.py` reads
the project index `<project>.rep/idata/~index.dat` and takes the program named
after the registered stock image, or else the only root-folder program whose
name contains the ROM key; `-p` names the program directly. Every headless run
includes `ProgramSha256.java`, which reports the executable SHA-256 that
Ghidra recorded at import. Configured preparation performs its preflight before
that output script. The wrapper stages the output and moves it into the
export directory only when that value equals the SHA-256 of the registered
stock image, so a program cannot stand in for a different dump.

`-f` reruns Ghidra for files that already exist. The script wraps
`DecompileFuncs.java` and `DumpFuncListing.java`; the project location and
name follow `GHIDRA_PROJECT_DIR` and `GHIDRA_PROJECT_NAME` when set.

The cached outputs are valid for one program state. `.decompile-key` in the
export directory binds the pinned Ghidra release, the program name, the image
digest, and the primary code scripts. For a layout's L0 image, it also binds
the L0 manifest, `symbols/<layout>.csv`, and configured preparation inputs.
`program_name.py --cache-key` reports that key. `.decompile-files.json` binds
each cached output to its digest. A changed key prevents reuse of the previous
state but preserves the accepted directory until replacement passes verification.
Stale code files are removed only from the staged replacement. Verified output
files, their digests, and their key replace the accepted cache together.
A failed preparation, output script, requested file, or promotion preserves
the accepted cache and key. Unrelated local files remain in the directory.

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
instruction shape. Every row carries its instruction address, so the rows of
one function list its body, which can be non-contiguous. A typical read-only
export is:

```bash
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -process <program-name> -noanalysis -readOnly \
  -scriptPath tools/ghidra \
  -postScript ExportGraph.java <export-dir> \
  -postScript ExportXrefs.java <export-dir> \
  -postScript ExportFunctionSignatures.java <export-dir> \
  -postScript ExportFunctionTokens.java <export-dir>
```

`RecoverFuncs.java`, `AnalyzeFuncs.java`, `MergeFuncs.java`, and
`RenameFuncs.java` change the in-memory program. A standalone maintenance run
without `-readOnly` persists those changes. Configured exact-image preparation
applies recovery, analysis, and joins under `-readOnly` in every export and
on-demand session instead of depending on a saved project mutation.

`RecoverFuncs.java --seeds-only` accepts only listed, aligned reviewed entries
and does not run the outside-function sweep. It refuses an unapproved split,
invalid seed, failed creation, or cancellation. Existing exact entries are
idempotent successes. The separately invoked broad mode retains its
outside-function recovery contract.

A seed that `RecoverFuncs.java` disassembles carries no operand references
until `AnalyzeFuncs.java` runs the program analyzers over the created bodies.
`PrepareProgram.java` invokes these existing primary scripts, applies the
reviewed joins, and verifies instruction owners, exact body bytes, addressed
references, and unchanged other functions. A registered borrowed fragment
keeps every instruction and non-stack reference. Abstract stack-space annotations
may be recomputed for its joined frame; every removed or added annotation is
recorded in its receipt. Other functions retain their full reference snapshots.
This exception does not apply to ROM, RAM, peripheral, flow, or register references.
Its image preflight checks both the imported executable digest and the current
ROM memory before mutations. Exact
entry-pointer, prologue, branch, literal, and restoration pins come from
`seeds/<layout>.toml`. The per-layout registry also specifies the prepared
body, reviewed fragment, cited sites, direct references, and forbidden
incidental entries. Structural preparation does not establish complete
interrupt execution or hardware behavior.

`symbols/<layout>.csv` is the tracked function-name registry of one layout.
`RenameFuncs.java` applies it to a program, and the Memgraph loaders and ROM
atlas read it through `tools/rom_sources.py`. Every row must name a function
entry of the layout's L0. A generated knowledge name is not a curated function
name.

The complete ROM loader performs header, foreign-key, address, and source-model
preflight before graph writes; see `../memgraph/README.md`.

## Function fragments

The auto-analysis of SH-2E code cuts some functions into fragments:

- the Shared Return Calls analyzer gives a `bra` whose target is a function
  entry a `CALL_RETURN` flow override, so the jump becomes a call and the
  target stays a function of its own;
- a function created at the first instruction after a literal pool cuts the
  body of the function whose branch reaches that instruction.

The body of the real function then ends at the fragment, and the exports
attribute the fragment's instructions, references, and calls to the fragment.
`merges/<layout>.csv` is the tracked repair registry of one layout: each row
names a function entry, one fragment that belongs to it, and the branches that
reach the fragment. `MergeFuncs.java` clears the flow overrides of those
branches, removes the fragment functions, and recomputes the body of the entry
in one transaction, which it rolls back when the recomputed body lacks a
fragment or a referencing branch. A registry lists only reviewed fragments;
the `review:` lines of the L0 export and the `sites` check of `kb check`
report candidates.

## L0 exports

`export-l0.sh` writes the L0 of one layout of `rom-images/homology.toml` into
`l0/<layout>/`: the structure exports above without function names, the
accessor census of every interpolation kernel of the layout, and
`manifest.toml` with the image digest, the program name, the pinned Ghidra
version, the census plan, the digest of every export script, and the digest
and row count of every file. `tools/kb/SPEC.md` defines the files, the normal
form, and the manifest; `uv run kb check` verifies them.

```bash
tools/ghidra/export-l0.sh jk00d --jobs 4
tools/ghidra/export-l0.sh jk00d --check --jobs 4
```

The census runs one `ResolveAccessors.java` session per kernel, so a function
that the resolver recovers in memory stays out of the census of other kernels.
Every configured core and census session independently applies the same
reviewed preparation plan. It binds the actual core, census, and code output
scripts, the configuration, and the selected layout's census registry as well
as the preparation scripts and builders. A session-specific wire and sealed
receipt bind its exact inputs, current image, verified preservation, and fresh output
digests. A script failure aborts following scripts, and a process exit of zero
without a matching complete receipt is not accepted. Receipts remain in the
raw stage, not in L0. `--from-stage` verifies every receipt and output digest
against the current inputs; it does not relabel an old stage with current
preparation hashes.

The manifest records configured preparation inputs in a per-layout table,
separate from the shared export-script table. The L0 check reconstructs the
prepared instruction-byte digest from the registered image at the exported
sites, verifies the reviewed body and joins, and rejects incidental outside
entries. Layouts without seed registries have no preparation requirement.
Verified replacement directories retain the accepted directory until
promotion succeeds. A promotion exception restores it; a failed restoration
retains the backup and reports its path. This is exception rollback, not a
cross-system or crash transaction.
`[l0.census.<layout>]` in `tools/kb/config.toml` names the interpolation
registry and the byte-copy helpers of each layout. `--jobs N` runs N headless
sessions at once, each on its own copy of the project, because a Ghidra project
admits one process at a time. `--check` exports into a temporary directory and
compares every file byte for byte with `l0/<layout>/`. `--stage DIR` keeps the
raw export, and `--from-stage DIR` normalizes a kept raw export without running
Ghidra. The export refuses a program whose recorded SHA-256 differs from the
registered image and a raw export that lacks a file.

## Script groups

| Group | Scripts | Purpose |
|---|---|---|
| Structure | `ExportGraph`, `ExportXrefs`, `ExportFunctionSignatures`, `ExportFunctionTokens`, `RecoverFuncs`, `AnalyzeFuncs`, `MergeFuncs`, `RenameFuncs` | Maintain and export function, call, reference, and cross-ROM signature structure |
| Map discovery | `FindInterpCore`, `MapInventory`, `DirectLookupInventory`, `ResolveAccessors`, `ScanFlags` | Discover interpolation families, operands, accessors, axes, and local selectors |
| Diagnostics | `ExportDiagnosticRefs`, `TraceRamAccesses`, `InventoryGbrAccesses`, `InventoryPointerArgs` | Produce semantic-free review inputs for diagnostic and RAM binding analysis |
| Inspection | `InspectAddress`, `DumpListing`, `DumpFuncListing`, `DecompileFuncs`, `FindTableRefs`, `FindPoolWords` | Inspect ownership, references, functions, listings, pools, and decompilation |
| Patch construction | `AuditFreeRegion` | Prove erased envelopes for bounded payload placement |
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
  CORRESPONDENCE_SOURCE_EXPORT=l0/jk00d \
  CORRESPONDENCE_TARGET_EXPORT=l0/jk00c \
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

## Safety boundary

P-code behavior is not silicon behavior. Ghidra does not model every SH-2E
hardware rule or peripheral. A firmware image is ineligible for hardware
testing unless the current GNU executable gate passes. Bench observation,
controlled write/readback, and vehicle behavior remain separate evidence.
