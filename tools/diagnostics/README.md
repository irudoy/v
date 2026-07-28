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
```

Every source-derived semantic node has the `Claim` label and a `RESTS_ON`
relationship to its exact `SourceFragment`. Existing `Func`, `Reg`, `Map`,
`Axis`, and other reverse-engineering layers are not recreated or deleted.

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

The main labels are:

- `SourcePack`, `SourceDocument`, `SourceFragment`;
- `VehicleVariant`, `Ecu`, `Rom`;
- `DtcCode`, `DtcDefinition:Claim`, `RomDtcDescriptor:Claim`,
  `DiagnosticSection:Claim`;
- `DiagnosticParameter`, `ParameterDefinition:Claim`,
  `DiagnosticRequest:Claim`, `DiagnosticService`;
- `CanSignal`, `CanSignalDefinition:Claim`, `CanFrame`,
  `CanFrameDefinition:Claim`, `CanSignalBinding:Claim`;
- `DiagnosticOperation:Claim`.

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

The `conflicts` command compares normalized affine factors, offsets, and unit
aliases. Equivalent source notation is not reported as a semantic conflict.

`export-dbc` writes a local derived file but never changes the graph or an ECU:

```bash
uv run --no-project --with neo4j \
  python tools/diagnostics/query.py export-dbc /tmp/vq-verified.dbc
```

Only bindings marked `hardware_verified` are exported. Factory signal matrices
and community payload definitions alone are deliberately insufficient.
