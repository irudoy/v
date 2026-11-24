# Diagnostic catalog tooling

These scripts create source-preserving diagnostic and CAN projections under
`refs/diagnostics/` and provide a read-only query interface over their Memgraph
projection. They do not transmit diagnostic commands or modify an ECU.

## Pipeline

```text
factory PDFs + exact ROMs + pinned public sources
  -> deterministic CSV/JSONL projections
  -> offline schema, count, and foreign-key preflight
  -> source-specific Memgraph claims
  -> reviewed per-ROM firmware bindings
  -> read-only Cypher and CLI queries
```

Every semantic claim retains its source pack, source document, exact fragment,
applicability, and verification status. Conflicting names, scales, formulas,
CAN layouts, and DTC records remain distinct claims. The graph does not merge
them into one inferred answer.

The complete corpus contract, source manifests, provenance fields, and
regeneration commands are documented in `../../refs/diagnostics/README.md`.

## Source projections

| Tool | Source | Output scope |
|---|---|---|
| `extract_esm.py` | Retained Nissan V36 factory ESM PDFs | Documents, page fragments, DTCs, monitors, operations, CAN routes, and extraction gaps |
| `extract_rom_dtc.py` | Exact registered ROM images and descriptor layout | Per-ROM DTC descriptor and attribute records |
| `import_370z_logger.py` | Retained 370Z CAN Logger snapshot | Parameters, requests, CAN frames, and payload bindings |
| `import_obd2tools.py` | Pinned obd2tools checkout | Nissan-family parameter and request candidates |
| `import_ecudocs.py` | Retained ecudocs profile snapshot | Structured ECU profile claims and request placement |
| `import_nissan_datatable.py` | Legacy Nissan data-table PDF | Consult I registers, requests, and operation definitions |
| `sid22_inventory.py` | Exact SHA-locked JK08A, JK00C/D, JK78C, 1ND0A/1ND3B, 1ME3B, and 1EK7A ROMs | Semantic-free service-0x22 DID, width, and response-source inventory |
| `tuning_signal_coverage.py` | Exact DID inventory and custom-CAN schema | Validated current and unresolved tuning-observation coverage |

All importers validate exact source revision or PDF identity where their source
manifest provides one. `--check` parses and validates without replacing tracked
outputs. The ESM check byte-compares every CSV and page-fragment output with
the same renderer used for generation, and refuses missing, changed or extra
CSV projections. Source-specific expected inventory is stored in each
`source_pack.toml`, not duplicated here. `extract_esm.py` reads dataset
identity, vehicle identity, the engine sections of a multi-engine manual,
retained-document count, and its default output directory from the `--pack`
source pack, so one extractor serves every retained ESM corpus.

ESM extraction validates every declared expected inventory before writing:
documents, unique ECM DTC codes, diagnostic parameters, operations and CAN
signals. Unknown expected-inventory keys and invalid counts are errors.
`discovery.csv` records recognized document sections and `unparsed.csv` records
recognized sections without structured rows; both are extractor QA reports
covered by the byte-comparison gate.

PDF extraction requires Poppler's `pdftotext` and `pdfinfo` on PATH. The ESM
entry point reports both installed releases and its reference release, whose
project record is the deployment table in `../README.md`. Other releases must
satisfy the same declared inventory and exact-output checks. A mismatch names
the inventory count or projection path and leaves existing outputs intact.
The PDF entry points, `extract_esm.py` and `import_nissan_datatable.py`, are
not part of `make check`; run their `--check` after changing an extractor, a
source pack, or a retained PDF.

Examples:

```bash
uv run python tools/diagnostics/extract_esm.py \
  refs/nissan-esm-2007-g35-sedan --check
uv run python tools/diagnostics/extract_esm.py \
  refs/nissan-esm-2013-g37-sedan \
  --pack refs/diagnostics/nissan-esm-2013-g37-sedan/source_pack.toml --check
uv run python tools/diagnostics/extract_rom_dtc.py --check
uv run python tools/diagnostics/import_370z_logger.py --check
uv run python tools/diagnostics/import_ecudocs.py --check
```

Run the same command without `--check` only when intentionally regenerating its
tracked source projection. Review the resulting diff before graph ingestion.
All public importers and the ROM descriptor extractor compare every rendered
CSV/JSONL file with its existing output in `--check` mode, including missing
and unexpected files. A failed comparison preserves all existing outputs.
`make check` runs both ESM corpora, ROM descriptors, the 370Z CAN Logger and
ecudocs corpora, and the pinned NissanDatatable source. The public importers
default to tracked snapshots in `refs/diagnostic-sources/`. Each snapshot's
`source.toml` binds its upstream URL, revision, license and exact file hashes.
The importers reject missing, changed or incorrectly pinned retained inputs.
An explicit external Git checkout must match the same revision and preserve
the selected source files. Restore damaged snapshots from the repository.
The PDF importer defaults to the tracked PDF and pin in
`refs/nissan-datatable/`; an explicit PDF path must match the same identity.

The service-0x22 response inventory writes to standard output:

```bash
uv run python tools/diagnostics/sid22_inventory.py
uv run python tools/diagnostics/sid22_inventory.py --layout 1EK7A --format json
uv run python tools/diagnostics/sid22_inventory.py --layout 1ND0A --format json
```

The tool SHA-locks the complete ROM, the publisher backing through its natural
return and PC-relative pool, and all six pointer table extents. It inventories
declared records through the next table or the known end of each extent.
Some publishers admit family 0x13 indices that overlap the adjacent
0x14 table. The inventory lists those addresses
only in their declared family. A `conditional` response uses the listed
byte source when the publisher's status check permits it and returns zero
otherwise.
Physical names and units are separate reviewed claims, such as the bindings
in `defs/registries/JK08A.diagnostic-bindings.csv`.

The tuning-coverage report cross-checks the reviewed signal catalog against the
exact DID inventory and every tuning field in the current custom-CAN profile:

```bash
uv run python tools/diagnostics/tuning_signal_coverage.py
uv run python tools/diagnostics/tuning_signal_coverage.py --format json
```

Its source is `defs/registries/JK08A.tuning-signals.toml`, the projection of the `signal`
entities of `kb`. The report distinguishes
fixed-rate and rotating stream coverage, stock-CAN context, quantities absent
from the ECU, unresolved runtime semantics, and observations requiring new
instrumentation or external measurement.

## Graph model

The diagnostic projection contains source packs, documents, fragments,
vehicles, ECUs, DTC identities and source definitions, diagnostic parameters
and requests, CAN signals and frames, operation definitions, and reviewed
firmware bindings. Every source-derived semantic node is a claim with a
`RESTS_ON` edge to its exact fragment.

The global diagnostic scope is owned by
`tools/memgraph/ingest_diagnostics.py`. Replacing that scope invalidates the
dependent per-ROM `DiagnosticBinding` layer; complete ROM ingestion rebuilds
those bindings afterward. Commands and transaction behavior are documented in
`../memgraph/README.md`.

## Reviewed firmware bindings

`defs/registries/<source>.diagnostic-bindings.csv` joins one firmware `Func`, `Reg`, `Map`,
or `Axis` to a diagnostic parameter, DTC code, or CAN signal and its exact
source claim. The JK08A view is generated from the `diagnostic` tables of the
owned `kb` meanings; other layouts retain their registry as the owner until
their conversion stage.

Each row keeps these decisions independent:

- `confidence` is the strength of the firmware association and is limited to
  `pattern`, `candidate`, or `code` in the static layer;
- `applicability` describes how closely the diagnostic source matches the ROM;
- `rom_scope` determines whether an exact-code inheritance edge may carry the
  row to another ROM;
- `priority` orders review work without changing confidence;
- `evidence` binds machine addresses and claim dependencies.

Names and matching prose are search aids only. They never create a binding.
The loader resolves the firmware target, diagnostic identity, exact source
claim, ROM scope, and every evidence dependency before graph replacement.
Static analysis cannot emit `silicon` confidence.

Addressed technical results belong in the structured JK08A annotation layer.
Detailed fuel, ignition, limiter, DFCO, and diagnostic implications belong in
the narrow documents under `defs/`, not in this tool contract.

## Candidate extraction

`ExportDiagnosticRefs.java` produces a semantic-free inventory of 16-bit ROM
references and instruction immediates in the machine-local export directory.
`extract_static_bindings.py` joins exact known service `0x22` DIDs to that
inventory and records the RAM references of the same function from `xrefs.csv`
of the ROM's L0 as a review worklist:

```bash
uv run python tools/diagnostics/extract_static_bindings.py JK08A \
  --export-dir <ghidra-export-dir>
```

The generated candidate CSV is deliberately incompatible with the binding
loader. A DID literal and nearby RAM address remain candidates until a trace
establishes request dispatch, returned value, conversion, and evidence scope.
Use `TraceRamAccesses.java` for indexed RAM producers after the dispatcher path
is known; see `../ghidra/README.md`.

## Read-only query CLI

The CLI issues static Bolt queries only. `operation` displays definitions and
cannot execute them.

```bash
uv run python tools/diagnostics/query.py dtc P0605
uv run python tools/diagnostics/query.py dtc P0455 --details
uv run python tools/diagnostics/query.py dtc-search "knock sensor"
uv run python tools/diagnostics/query.py monitor 221201
uv run python tools/diagnostics/query.py monitor "intake valve timing"
uv run python tools/diagnostics/query.py can "Engine speed"
uv run python tools/diagnostics/query.py operation "POWER BALANCE"
uv run python tools/diagnostics/query.py binding P0327 --rom JK08A
uv run python tools/diagnostics/query.py coverage
uv run python tools/diagnostics/query.py conflicts
```

Place `--json` before the subcommand for machine-readable output. Multiword
semantic searches require an adjacent phrase while accepting spaces, hyphens,
and slashes as separators. Applicability and verification status remain visible
in every result. `conflicts` compares normalized affine conversions and unit
aliases rather than merely different source notation.

Reusable query reviews are stored in
`tools/memgraph/diagnostics_queries.cypher`.

## DBC export boundary

`export-dbc` writes a local derived file and never changes the graph or ECU:

```bash
uv run python tools/diagnostics/query.py export-dbc /private/tmp/vq-verified.dbc
```

Only payload bindings explicitly marked `hardware_verified` are eligible.
Factory signal routes and community payload definitions alone are insufficient.

## Verification

```bash
uv run pytest -q tools/diagnostics/tests
uv run python tools/memgraph/ingest_diagnostics.py --dry-run
```

The tests derive expected inventories from source manifests, enforce exact
source provenance and foreign keys, preserve duplicate and conflicting claims,
reject executable operation semantics, and require provenance for every graph
claim.
