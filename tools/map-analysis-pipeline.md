# Map analysis pipeline

This specification defines the current reproducible path from an exact stock
ROM to reviewed map claims and generated tuning-editor definitions. It covers
tracked inputs, headless Ghidra exports, the derived Memgraph schema, analysis
stages, claim-specific provenance, and output invariants.

Memgraph is a rebuildable query and relationship index. It is not the durable
authority for a claim. Technical facts live in tracked source files and exact
ROM bytes; generated graph nodes, XML, XDF, ledgers, and counts are projections.

## Data flow

```text
stock ROM + tracked source registries
  -> Ghidra headless structure and operand exports
  -> offline source and export preflight
  -> Memgraph relationship projection
  -> code, diagnostic, catalog, and homology review
  -> canonical CSV/TOML claim updates
  -> repeat ingest and strict provenance audit
  -> XML, XDF, and ledger projections
```

## Tracked source inputs

| Source | Authority |
|---|---|
| `rom-images/roms.csv` | ROM label, exact file path, and SHA-256 identity |
| `rom-images/README.md` and per-ROM provenance | Stock source, hardware identity, and applicability boundary |
| `defs/rom-inheritance.toml` | Canonical annotation source, target ROM, exact hashes, and code-equality ranges |
| `tools/ghidra/symbols.csv` | Curated function names |
| `defs/<source>.interp.csv` | Interpolation entry, family, role, geometry, element type, and implicit-axis mechanics |
| `defs/<source>-<target>.interp-correspondence.csv` | Reviewed relocated wrapper and kernel pairs across non-inheriting ROM families |
| `defs/<source>.findings.csv` | Map role, semantics, scaling, confidence, evidence, and manually traced non-interpolation geometry |
| `defs/<source>.axes.csv` | Axis semantics, scaling, confidence, and evidence |
| `defs/<source>.funcs.csv` | Function semantics, contracts, independent confidence fields, and evidence |
| `defs/<source>.vars.csv` | RAM and peripheral semantics, units, confidence, and evidence |
| `defs/<source>.diagnostic-bindings.csv` | Reviewed firmware-to-diagnostic claims with separate applicability and ROM scope |
| `defs/<source>.dtc.csv` | Exact DTC descriptor and attribute edit ranges |
| `defs/<source>.overrides.toml` | Editor names, categories, visibility, presentation, static labels, switches, and checksum declarations |
| `patches/*-layout.toml` | Current map-slot and runtime configuration projection layouts |
| `refs/diagnostics/` | Source-preserving factory and community diagnostic claims |
| `refs/vendor/` and pinned definition submodules | Address-free map vocabulary, shapes, units, documented mechanics, and comparison anchors |

Map and axis values are never copied into handwritten source files. Every
ingest resolves the target image through `roms.csv`, verifies its hash, and
measures values from that image using the recovered address, geometry, and
storage type.

`<source>` is the canonical annotation layer selected by
`rom-inheritance.toml`. An exact-code target receives reviewed source claims but
keeps its own Ghidra export, image measurements, graph nodes, and diagnostic
scope. No copied XML, XDF, ledger, or presentation layer is created for an
inherited target.

## Headless Ghidra exports

Ghidra projects and export directories remain machine-local. Scripts under
`tools/ghidra/` produce deterministic inputs for the loaders:

| Output | Producer | Content |
|---|---|---|
| `funcs.csv`, `calls.csv` | `ExportGraph.java` | Function boundaries and resolved call edges |
| `xrefs.csv` | `ExportXrefs.java` | RAM, peripheral, and literal-pool references |
| `function_signatures.csv`, `function_sites.csv` | `ExportFunctionSignatures.java` | Exact and relocation-tolerant function hashes plus ordinal callsites |
| `map_inventory.csv` | `MapInventory.java` | Kernel slot, wrapper, callsite, and baseline operand census |
| `direct_lookup_inventory.csv` | `DirectLookupInventory.java` | Direct and implicit-axis table census |
| `accessors.<kernel>.csv` | `ResolveAccessors.java` | Backtracking and decompiler-data-flow operands with branch sets and verdicts |
| `flags.csv` | `ScanFlags.java` | Local bit-test and branch candidates around selected code paths |
| `diagnostic_refs.csv` | `ExportDiagnosticRefs.java` | Semantic-free 16-bit diagnostic-reference review input |

`RecoverFuncs.java` may persist reviewed missing entries before export.
`ResolveAccessors.java` also recovers an unmarked function in memory when a
registered callsite otherwise lacks a decompiler function.

The resolver reads `r4`, `r5`, `r6`, and `r7` at interpolation callsites,
dereferences literal-pool slots, folds p-code define-use chains, resolves local
GBR setup, preserves aligned `MULTIEQUAL` branch sets, recognizes explicitly
declared byte-copy helpers, and falls back to instruction propagation without
discarding unresolved dynamic operands. It emits both the earlier linear
backtrack and the data-flow result. `bt_only` is a regression; `conflict` is a
review finding; `selector` preserves multiple legitimate operand tuples.

For non-inheriting families, `tools/rom_correspondence.py` uses unique function
signatures and equal call ordinals to propose addressed map and axis pairs.
Interpolation wrappers must be joined through a reviewed correspondence CSV;
row order and relative address offsets are not evidence. The resulting report
is an input to target-specific review, not a semantic claim source.

## Derived graph schema

Firmware node identity is `{rom, addr}`, with lowercase hexadecimal addresses
without `0x`. Address-free reference catalogs use their own stable source keys.

### Firmware nodes

| Label | Role |
|---|---|
| `Rom` | Exact target identity and canonical annotation-source relationship |
| `Func` | Function structure plus reviewed semantic and contract claims |
| `Reg` | RAM or peripheral location plus reviewed semantic claim |
| `Interp` | Kernel, wrapper, or finisher with recovered geometry and family |
| `Map` | Addressed calibration, threshold, or proven dead table with measured values and independent semantic and scale claims |
| `Axis` | Addressed axis geometry, measured monotonicity, semantic claim, and scale claim |
| `Flag` | Local selector, gate, or threshold candidate tied to a traced path |

### Reference and diagnostic nodes

| Label family | Role |
|---|---|
| `A2LEntry`, `VendorEntry`, `VendorFact` | Address-free HR map vocabulary and documentary anchors |
| `SourcePack`, `SourceDocument`, `SourceFragment` | Exact provenance for diagnostic source claims |
| `DtcCode`, `DiagnosticParameter`, `DiagnosticRequest`, `CanSignal`, `CanFrame` | Canonical diagnostic identities |
| Source-specific `Claim` nodes | Definitions that preserve applicability and verification status |
| `DiagnosticBinding` | Reviewed bridge between one firmware node and one source-specific diagnostic claim |

### Structural relationships

| Relationship | Meaning |
|---|---|
| `Rom-[:ANNOTATIONS_FROM]->Rom` | Verified target-to-canonical annotation inheritance |
| `Func-[:CALLS]->Func` | Resolved call graph edge |
| `Func-[:USES]->Reg` | RAM or peripheral reference |
| `Func-[:ACCESSES]->Map` | Resolved table operand at a callsite |
| `Map-[:VIA]->Interp`, `Interp-[:KERNEL]->Interp` | Wrapper and kernel mechanics |
| `Map-[:AXIS_X|AXIS_Y]->Axis` | Recovered table geometry |
| `Axis-[:INDEXED_BY]->Reg`, `Map-[:WRITES]->Reg` | Reviewed input and output data flow |
| `Flag-[:SELECTS]->Map`, `Flag-[:GATES]->Func` | Local control relationship established by branch analysis |
| `Map-[:MATCHES]->A2LEntry` | Address-free catalog candidate |
| `Map-[:HOMOLOG]->Map`, `Func-[:HOMOLOG]->Func` | Cross-ROM structural candidate |
| `Claim-[:RESTS_ON]->Claim` | Claim-specific evidence dependency |

Catalog concepts are joined by properties when queried. They are not copied
into additional graph edges merely to materialize a vocabulary join.

## Ingest order

The global diagnostic corpus and address-free reference catalogs are loaded
independently of a specific ROM. A complete target-ROM ingest then runs in one
fixed owner order:

```text
load_graph.py
  -> load_xrefs.py
  -> load_maps.py
  -> load_code.py
  -> load_diagnostic_bindings.py
  -> provenance_report.py audit
```

`tools/memgraph/ingest.py <rom> --strict --dry-run` validates all tracked
sources, exact image bindings, export headers, foreign keys, censuses, geometry,
inheritance, diagnostic claims, and provenance before the first graph mutation.
Run without `--dry-run` only after preflight passes. The operational contract is
in `tools/memgraph/README.md`.

Each loader owns and replaces its graph scope. Direct edits in Memgraph or Lab
are not durable and must not be used to preserve project knowledge.

## Claim-specific confidence and provenance

Semantic identity, function contract, and physical scaling are distinct claims.
They use separate local fields such as `confidence`, `contract_conf`, and
`scale_conf`, with matching evidence columns.

| Level | Required basis | Output boundary |
|---|---|---|
| `pattern` | Structural or value pattern without semantics | Never emitted to tuning definitions |
| `candidate` | Consistent address, accessor, geometry, and a bounded semantic match | May be emitted with candidate labeling if all definition gates pass |
| `code` | The exact claim is traced in target or verified exact-code firmware with factual evidence | Emitted under its claim-type gates |
| `silicon` | Bench or CONSULT live-data verification under a documented hardware condition | Still subject to image-level hardware gates before flashing |

Promotion from `pattern` to `candidate` may use structural automation.
Promotion to `code` requires a reviewed trace for the specific property.
Promotion to `silicon` requires hardware evidence. A code-proven association to
a homologous diagnostic definition does not make that definition exact for the
target ROM; firmware confidence and source applicability remain separate.

Evidence tokens use `role:addr@target_property` or
`role:addr+offset@target_property`. Supported address roles include
`consumer`, `writes`, `indexed_by`, `selector`, `threshold`, `from_map`,
`trace`, `homolog`, `base`, and `match`. `@structural` establishes existence or
topology without lowering semantic confidence. Terminal facts such as
`rom_const`, `spec`, `registry`, and `site` ground a claim without another graph
node.

Effective confidence is the weakest local claim along constraining `RESTS_ON`
dependencies. It is computed by `provenance.py` and
`provenance_report.py`, not stored as a second fact. Strict audit rejects an
unresolved evidence reference, missing or extra projected edge, ungrounded
code/silicon claim, self-supporting ungrounded cycle, or effective downgrade.

## Current analysis stages

### 1. Bind the exact ROM

Resolve the ROM label through `roms.csv`, verify SHA-256 and size, and select
the canonical annotation source through `rom-inheritance.toml`. Imported
program identity, graph label, and measured image must refer to the same target.

### 2. Export structure

Recover only reviewed missing function entries, apply tracked names, and export
functions, calls, and xrefs. Produce the semantic-free diagnostic reference
inventory when diagnostic binding work is in scope.

### 3. Recover map mechanics

For every registered interpolation entry, enumerate kernel slots, wrappers,
callsites, table bases, explicit axes, implicit steps, storage widths, and
branch-selected operand sets. Run the direct-lookup census for families outside
the shared interpolation wrappers. Do not infer meaning from shape alone.

### 4. Measure the target image

Validate geometry and read every map and axis from the exact target ROM.
Compute ranges, value hashes, fill state, and monotonicity. These measurements
partition analysis work but do not establish semantics.

### 5. Establish semantics

Trace accessors, callers, RAM inputs, outputs, comparisons, control flow, and
diagnostic bindings. Use address-free A2L and vendor catalogs, exact-code
homology, constant block signatures, and factory documentation as independent
comparison signals. A catalog match or homolog is a candidate until target code
and evidence establish the specific claim.

Diagnostic context may prioritize a map or explain a reviewed relationship. It
does not rename a map automatically or alter firmware confidence.

### 6. Trace selectors, gates, and thresholds

Start from a reviewed map accessor or control path. Follow the branch that
selects an operand, dominates a call, or compares a calibrated scalar. Resolve
GBR from the containing function rather than imposing a global base. Store an
unknown branch role as an open trace, not as proof that no control exists.

### 7. Promote and audit

Update the appropriate canonical CSV claim and evidence, repeat dry-run and
ingestion, and run strict provenance audit. Hardware evidence is recorded
separately from code evidence and does not transfer through homology without an
explicit applicability contract.

### 8. Generate projections

After a successful audit, regenerate the canonical map ledger and the paired
XML/XDF definitions. Review their diff as a projection of the source change.

## Definition generator contract

`tools/mapkit/emit_def.py <rom> [xml-output] [xdf-output]` combines one
in-memory model from:

- graph-projected map geometry, axes, values, semantics, and confidence;
- `defs/<rom>.dtc.csv` exact DTC edit ranges;
- `defs/<rom>.overrides.toml` presentation and visibility;
- current map-switching and Rolling Launch layout projections;
- exact ROM bytes selected by `roms.csv`.

The generator writes RomRaider XML and TunerPro XDF together. The outputs share
calibration geometry, names, categories, views, switches, and exact stock
validation while using the native representation of each editor.

A selected map passes the definition gate only when it has table role,
nonempty semantics, complete geometry, usable scaling, confidence at least
`candidate`, and a presentation name and category. Ambiguous axes, missing
static labels, an override that replaces a recovered fact, an unknown override
address, or an explicitly visible table that fails a gate stops generation.

`presentation.default_emit` controls default visibility. `emit = false` hides a
research table from editor output without removing its graph or ledger facts.
Candidate semantic and scaling claims are labeled in generated descriptions;
functional categories never encode confidence.

DTC records are checked against the exact stock descriptor and attribute bytes.
RomRaider receives coordinated native switches; TunerPro receives atomic
patches for individual records and declared groups. There is no implicit
all-DTC patch.

The map-switching projection reuses canonical Map 1 storage and adds only the
reserved Map 2 through Map 5 editor views declared by the current layout. The
Rolling Launch projection exposes only validated configuration controls. These
editor-only copies do not create speculative canonical `Map` nodes and do not
create another ROM identity.

`tools/maps/build_tracker.py` renders `defs/<rom>.maps.csv` from the graph as a
reviewable catalog snapshot. Open work is represented by its role, confidence,
and empty semantics; no parallel status field is maintained. The ledger, XML,
and XDF must never be edited manually.

Detailed commands and invariants are in `tools/mapkit/README.md`.

## Reproducibility invariants

- Every ROM read is bound to a registered SHA-256 identity.
- Inherited annotations require exact source and target hashes plus verified
  executable-code ranges; values are always measured from the target image.
- Every registered interpolation entry has a complete current census.
- Data-flow resolution must cover the linear-backtrack baseline; conflicts stay
  visible for review.
- Handwritten claims contain semantics and evidence, not copied ROM values.
- Every code or silicon claim has factual grounding and exact projected
  provenance edges.
- Firmware confidence, physical scaling confidence, diagnostic applicability,
  and hardware result are independent dimensions.
- Loaders own graph mutation; direct graph changes are disposable.
- XML, XDF, ledgers, vendor catalogs, and diagnostic tables identify themselves
  as generated projections and reproduce from declared inputs.
- A presentation change cannot replace an addressed technical fact.
- Only hardware evidence can establish silicon behavior. Software and graph
  gates remain necessary but insufficient for flashing.
