# Diagnostic catalog tooling

These scripts build and query the project diagnostic knowledge layer. They do
not use SQLite. Reproducible CSV/JSONL projections under `refs/diagnostics/`
feed Memgraph, where source claims can be compared without collapsing
conflicting evidence.

## Pipeline

```text
factory PDFs + exact ROMs + pinned public sources
  -> deterministic CSV/JSONL projections
  -> offline schema and foreign-key preflight
  -> Memgraph claims and provenance edges
  -> code-traced per-ROM DiagnosticBinding claims
  -> read-only Cypher/CLI queries
```

The loader creates source nodes, canonical identities, and source-specific
claims:

```text
SourcePack -> SourceDocument -> SourceFragment

RomDtcDescriptor -> DtcCode <- DtcDefinition
ParameterDefinition -> DiagnosticParameter
DiagnosticRequest -[:RETURNS]-> DiagnosticParameter
DiagnosticRequest -[:SENDS]-> DiagnosticParameter
CanSignalDefinition -> CanSignal <- CanSignalBinding -> CanFrame
DiagnosticOperation -> SourceFragment

Rom -> DiagnosticBinding -> Func / Reg / Map / Axis
                        -> DiagnosticParameter / DtcCode / CanSignal
                        -> source-specific diagnostic claim
```

Every source-derived semantic node has the `Claim` label and a `RESTS_ON`
relationship to its exact `SourceFragment`. Existing `Func`, `Reg`, `Map`,
`Axis`, and other reverse-engineering layers are not recreated or deleted.
The per-ROM binding layer depends on both graphs and is loaded separately after
the firmware graph.

## Build and validate

All importers accept `--check` to parse and validate without writing output.
Source-specific expected counts are stored in `source_pack.toml` and enforced
again by the Memgraph preflight.

```bash
python3 tools/memgraph/ingest_diagnostics.py --dry-run
python3 -m unittest discover -s tools/diagnostics/tests -v
```

The tests enforce:

- retention of all six source packs regardless of recorded license metadata;
- exact ROM descriptor and unique-DTC counts;
- byte-identical JK03A/JK08A descriptor and attribute-pointer projections;
- exact joins for all 29 curated `defs/JK08A.dtc.csv` rows;
- preservation of duplicate P0605 descriptors;
- 56 ESM documents, 1338 source fragments, 1635 DTC definitions including 169
  ECM codes, 1120 Data Monitor definitions, 316 non-executable operations, and
  106 CAN signal routes;
- preservation of the known SID `0x1201` RPM formula conflict;
- normalization of equivalent affine formulas and unit aliases;
- source-local association between requests and parameter definitions;
- separate CAN route-definition and physical-binding evidence groups;
- page-heading ECU attribution that is not overridden by incidental cross-ECU
  references;
- reconstruction of code-first and title-first DTC indexes, wrapped SRS titles,
  bracket-qualified titles, and fixed-width ESM table rows;
- association of page-start continuation tables with their preceding
  diagnostic mode when another mode starts later on the page;
- isolation of Work Support mode selections within their service-setting row;
- preservation of paired monitor names, units, descriptions, conditions,
  remarks, and operation usage;
- exclusion of table-of-contents references from DTC detail pages;
- `executable=false` for every imported operation;
- exclusion of non-hardware-verified bindings from DBC export;
- rejection of `silicon` confidence in the static binding layer;
- exact-code inheritance only for bindings that explicitly declare that scope;
- separation of firmware confidence from diagnostic-source applicability;
- phrase-bounded semantic search, domain aliases, and applicability-aware result
  ordering;
- a provenance edge for every graph claim.

## Memgraph ingestion

```bash
uv run --no-project --with neo4j \
  python tools/memgraph/ingest_diagnostics.py
```

The loader validates all files before its first graph mutation, replaces all
source claims in the diagnostic graph scope, writes the projection, and audits
graph counts in one transaction. An audit failure rolls the transaction back.
Repeating the command is idempotent, including after source-pack removal or a
load from an alternate `--root`.

Replacing the global diagnostic corpus removes every `DiagnosticBinding`
because each binding rests on a source-specific claim that is about to be
replaced. Run the per-ROM ingest afterward to reconstruct valid bindings:

```bash
uv run --no-project --with neo4j \
  python tools/memgraph/ingest.py JK08A \
  --export-dir ~/tools/ghidra-projects/export-JK08A-exact --strict

uv run --no-project --with neo4j \
  python tools/memgraph/ingest.py JK03A \
  --export-dir ~/tools/ghidra-projects/export-JK03A --strict
```

The main labels are:

- `SourcePack`, `SourceDocument`, `SourceFragment`;
- `VehicleVariant`, `Ecu`, `Rom`;
- `DtcCode`, `DtcDefinition:Claim`, `RomDtcDescriptor:Claim`,
  `DiagnosticSection:Claim`;
- `DiagnosticParameter`, `ParameterDefinition:Claim`,
  `DiagnosticRequest:Claim`, `DiagnosticService`;
- `CanSignal`, `CanSignalDefinition:Claim`, `CanFrame`,
  `CanFrameDefinition:Claim`, `CanSignalBinding:Claim`;
- `DiagnosticOperation:Claim`;
- `DiagnosticBinding:Claim`.

## Static firmware bindings

`defs/<source>.diagnostic-bindings.csv` is the reviewed bridge between the
source-preserving diagnostic corpus and one ROM's firmware graph. A row binds
one `Func`, `Reg`, `Map`, or `Axis` to one `DiagnosticParameter`, `DtcCode`, or
`CanSignal`. It also identifies the exact source claim and machine-address
evidence supporting the association.

The following properties remain independent:

- `confidence` describes the strength of the firmware association and is
  limited to `pattern`, `candidate`, or `code`;
- `applicability` describes how closely the diagnostic source applies to the
  ROM;
- `rom_scope` controls whether a row is exact-ROM only or can cross an
  explicitly verified exact-code inheritance edge;
- `priority` controls worklist ordering without changing confidence.

Names and matching parameter descriptions are search aids only. They never
create a binding. Every row requires a machine-address anchor, and the loader
resolves the firmware target, diagnostic identity, source claim, and every
evidence dependency before replacing the ROM's current projection.

The current static milestone has no hardware-loop completion gate. The binding
loader therefore cannot emit `silicon`; a later hardware-backed workflow may
add that level under a separate evidence contract.

The exact-ROM portion includes code-traced rear O2 and catalyst monitor slices.
`FUN_00089D92` dispatches the P0139/P0159, P0137/P0157, and first
P0138/P0158 descriptor pairs from bank-indexed metrics at `0xFFFF26E9`,
`0xFFFF26EB`, `0xFFFF2726`, and `0xFFFF2724`. `FUN_0008A258` dispatches the
second P0138/P0158 pair from two bank-indexed working arrays at `0xFFFF42B0`
and `0xFFFF42B2`. The duplicate P0138/P0158 rows preserve their distinct exact
descriptor claims rather than collapsing the two firmware paths.

For catalyst efficiency, `FUN_000A2254` independently dispatches descriptor
indices `0x11/0x12` for P0420/P0430. A separate calibrated branch runs
`0x11FB6 -> FUN_000A2EE4 -> 0xFFFF2B6F[bank]`, compares bank metric
`0xFFFF314D[bank]` in `FUN_000A2F56`, and dispatches the same DTC pair only when
the unsigned metric is below the limit. All eight stock cells at `0x11FB6` are
zero, so this particular below-limit fault branch is unreachable in unmodified
JK08A. The independent `FUN_000A2254` result path remains present. Internal
metric units and hardware behavior after calibration changes are unresolved.

The exact rear O2 heater circuit monitor is separate from those voltage and
catalyst paths. `FUN_0008B604` calls bank-indexed `FUN_0008B93A`, which reads
`0xFFFF2722[bank]`. Values below `ROM8[0x8AAF] = 0x0C` dispatch exact
P0037/P0057 descriptors; values at or above `ROM8[0x8AB0] = 0xEC` dispatch
exact P0038/P0058 descriptors. The in-range path reloads monitor state
`0xFFFF4293[bank]` from `ROM8[0x8AB2] = 5`. A whole-program p-code scan found
all five direct or pointer-recovered feedback reads and no write, so the producer
and physical scale remain unresolved.

Exact DID `0x130B` provides an independent observation point. Its record at
`0x22A38` returns `0xFFFF2C57` with support mask `0x03`. Builder
`FUN_0002E2E8` maps `0xFFFF2377` bit 0 to response bit 1 and bit 1 to response
bit 0; `ROM8[0x8B2A] = 0x09` permits the second mapping. A homologous structured
Nissan profile names those supported bits as the bank-1 and bank-2 HO2S2 heater
states. A second whole-program scan found the two readers of `0xFFFF2377` and
no writer. The binding projection therefore records the exact command/status
packing and homologous names but does not claim a firmware-to-MCU-to-terminal
output path.

Map worklist and definition generators render both direct Map bindings and
bindings reachable through a Map or Axis `RESTS_ON` path. Indirect context is
marked with its path and evidence role, such as
`via map evidence: indexed_by` or `via map evidence: writes`. This affects
priority and explanatory text only; it does not change map semantics or
confidence.

### SID 0x22 review worklist

`ExportDiagnosticRefs.java` exports semantic-free references to 16-bit ROM
constants and instruction immediates. The extractor joins exact known service
`0x22` DIDs to those values and lists RAM addresses referenced by the same
function:

```bash
D=~/tools/ghidra-projects/export-JK08A-exact
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -process 1JK08A-20260726-stock.bin \
  -noanalysis -readOnly -scriptPath tools/ghidra \
  -postScript ExportDiagnosticRefs.java "$D"

uv run --no-project --with neo4j \
  python tools/diagnostics/extract_static_bindings.py JK08A
```

The generated `diagnostic-binding-candidates.csv` is a review artifact outside
Git. It is deliberately incompatible with the binding loader. A DID literal
and same-function RAM reference remain candidates until a dispatcher-to-response
data-flow trace establishes the request path, returned value, and conversion.
With the current corpus of 383 known service `0x22` DIDs, the JK08A export
produces 937 source-specific rows. Collapsing duplicate diagnostic claims leaves
197 distinct firmware reference hits for 34 matched DIDs; 58 hits occur in
functions containing more than one known DID. These are queue metrics, not
reviewed bindings.

`TraceRamAccesses.java` resolves decompiler p-code LOAD/STORE effective
addresses and constant call arguments for a selected RAM range. Optional
`--candidates` retains unresolved indexed expressions that contain a concrete
RAM anchor. It is used after the dispatcher trace to find base-plus-offset
runtime producers that are absent from direct xrefs:

```bash
D=~/tools/ghidra-projects/export-JK08A-exact
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -process 1JK08A-20260726-stock.bin \
  -noanalysis -readOnly -scriptPath tools/ghidra \
  -postScript TraceRamAccesses.java "$D" ffff128c ffff4fff --candidates
```

The reviewed JK08A projection binds DIDs `0x1107` through `0x110A` to the
common ignition-timing response byte at `0xFFFF2022`, DIDs `0x1123` through
`0x1126` to the four fuel-trim response words, DIDs `0x1206` and `0x1207` to
the big-endian injection pulse values at `0xFFFF23C8` and `0xFFFF23CA`, and DID
`0x1135` to intake valve timing bank 1 at `0xFFFF2442`.

The four ignition DIDs are exact aliases in pointer-table locations
`0x226C8..0x226D4`. `FUN_0004DF82` normally writes
`110 - uint8[0xFFFF11D4]` to `0xFFFF2022`. A community formula for DID
`0x110A` applies `110 - raw`, exactly inverting this normal firmware transform.
Gated control modes add or subtract stock offsets with saturation, or force a
fixed value, so the affine relation is not universal.

The upstream code path is
`0x147DA -> FUN_0004D99C -> 0xFFFF12D6 -> FUN_0004DBE8 ->`
`0xFFFF11D4 -> FUN_0004DF82 -> 0xFFFF2022 -> FUN_0003235C`.
This establishes map `0x147DA` as a conditional subtractive correction in the
internal ignition-timing coordinate. The exact operating-mode qualifier,
physical degree unit, and producer of axis input `0xFFFF237E` remain unresolved.
The full p-code scan finds one read and no exact or base-plus-offset writer for
that axis input.

The fuel-trim pointer entries at `0x22738..0x22744` address words
`0xFFFF22DC`, `0xFFFF22DE`, `0xFFFF2302`, and `0xFFFF2304`; service `0x22`
returns each high byte. Exact J1979 handler `FUN_00035856` reads the same words
for Mode 01 PIDs `0x06`, `0x07`, `0x08`, and `0x09` in standard STFT B1, LTFT
B1, STFT B2, LTFT B2 order. Each Mode 01 branch returns
`min(255, floor(word/200))`. This proves an internal percent*256 representation:
initializer `FUN_000593AC` writes neutral `0x6400`, UDS raw 100 displays as 0
percent correction through `raw-100`, and Mode 01 raw 128 displays as 0 percent
through the standard formula.

`FUN_0005C910` publishes the two STFT words from working values
`0xFFFF40AC/0xFFFF40AE`; an alternate control path forces a common value
clamped to 75..125 percent. The LTFT path uses 64-word adaptive RAM grids at
`0xFFFF4B90/0xFFFF4B10`. `FUN_0005796C` selects one cell per bank from an 8x8
operating-region index, `FUN_00057D1E` updates selected cells within stock
90..110 percent limits, and `FUN_00057B26` combines the selected cell with a
bank adjustment around `0x6400` before writing `0xFFFF2302/0xFFFF2304`.
Fault and control gates can force neutral. The exact meaning of one grid
coordinate and the learning cadence remain unresolved.

`FUN_0004EBA2` is the exact runtime producer of six consecutive pulse words at
`0xFFFF23C8+2*i`. It selects an even/odd base, adds a signed per-channel
correction, conditionally subtracts a second signed correction, and applies the
direct-indexed Q1.7 multiplier at `0x129C0+i`. All six stock multiplier bytes
are `0x80`, or 1.0. DIDs `0x1206` and `0x1207` return the first two words; the
factory monitor and homologous profile identify them as bank 1 and bank 2
injection pulse width with conversion `raw/100 ms`.

`FUN_000BD9F0` is the exact two-channel runtime writer of
`0xFFFF2442/0xFFFF2443`:

```text
clamp_u8(0x80 + reference[channel] - capture[channel])
```

The reference bytes are `0xFFFF4799/0xFFFF479A`; the capture-derived bytes are
`0xFFFF22CC/0xFFFF22CD`. The latter trace to ATU-II channel 1A registers GR1F
and GR1E. A hardware-control path forces neutral `0x80`, and zero enable byte
`0xFFFF11DE` suppresses the update. Homologous diagnostic definitions support
candidate conversion `raw*0.5-64 degCA`; exact code proves the centered
representation but not this physical scale.

Reusable Cypher examples are in
`tools/memgraph/diagnostics_queries.cypher`.

## Read-only query CLI

The CLI issues static read queries only. The `operation` command displays
definitions; it cannot transmit them.

```bash
uv run --no-project --with neo4j \
  python tools/diagnostics/query.py dtc P0605

uv run --no-project --with neo4j \
  python tools/diagnostics/query.py dtc P0455 --details

uv run --no-project --with neo4j \
  python tools/diagnostics/query.py dtc-search "knock sensor"

uv run --no-project --with neo4j \
  python tools/diagnostics/query.py monitor 221201

uv run --no-project --with neo4j \
  python tools/diagnostics/query.py monitor "intake valve timing"

uv run --no-project --with neo4j \
  python tools/diagnostics/query.py can "Engine speed"

uv run --no-project --with neo4j \
  python tools/diagnostics/query.py can 180

uv run --no-project --with neo4j \
  python tools/diagnostics/query.py operation "POWER BALANCE"

uv run --no-project --with neo4j \
  python tools/diagnostics/query.py binding P0327 --rom JK08A

uv run --no-project --with neo4j \
  python tools/diagnostics/query.py binding 000141f4 --rom JK08A

uv run --no-project --with neo4j \
  python tools/diagnostics/query.py coverage

uv run --no-project --with neo4j \
  python tools/diagnostics/query.py conflicts
```

Add `--json` before the subcommand for machine-readable output.
The default human renderer preserves result sections and prints nested evidence
without truncating it to a fixed table width. DTC output includes source-page
metadata by default; `dtc --details` also includes the full extracted page text.
`dtc-search`, `monitor`, `operation`, and named `can` searches inspect names and
their structured semantic fields. Multiword input is matched as an adjacent
phrase with space, hyphen, and slash separators. Domain aliases cover Consult
abbreviations such as `INT/V`, `EXH/V`, `TP SEN`, and `VVEL`; DTC-only sensor
aliases remain isolated from general monitor search to avoid accidental
substring matches. Exact-manual claims are ranked before homologous and generic
claims, with ECM definitions first at the same applicability level.
Monitor requests are returned only with definitions from the same dataset.
Factory monitor output keeps display content, operating conditions, and
reference-value remarks as separate properties.
CAN route definitions and payload bindings are returned as separate provenance
groups. Signal-name results rank exact factory routes before homologous payload
bindings while preserving each evidence item's applicability, source kind, and
source tier. CAN identifiers accept decimal-looking hexadecimal forms such as
`180` as well as `0x180`. An exact identifier search returns evidence only for
that frame; a signal-name search may return bindings from every matching frame.
The `binding` command searches the reviewed static bridge. Canonical DTCs and
eight-digit firmware addresses are exact identifiers; other terms search
diagnostic names, kinds, and notes. Output always displays confidence and
applicability separately.

The `conflicts` command compares normalized affine factors, offsets, and unit
aliases. Equivalent source notation is not reported as a semantic conflict.

`export-dbc` writes a local derived file but never changes the graph or an ECU:

```bash
uv run --no-project --with neo4j \
  python tools/diagnostics/query.py export-dbc /tmp/vq-verified.dbc
```

Only bindings marked `hardware_verified` are exported. Factory signal matrices
and community payload definitions alone are deliberately insufficient.
