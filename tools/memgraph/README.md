# Memgraph projection and ingestion

Memgraph is a reproducible query index over tracked firmware, annotation, and
diagnostic evidence. It is not a handwritten authority. A complete ingest may
replace graph-owned nodes and relationships; durable claims must therefore live
in the source CSV, TOML, assembly, or specifications referenced by the loaders.

## Service

The compose stack runs Memgraph MAGE and the optional Lab UI in Docker Desktop:

```bash
docker context use desktop-linux
docker compose -f tools/memgraph/docker-compose.yml up -d
docker compose -f tools/memgraph/docker-compose.yml down
```

Bolt is available at `bolt://127.0.0.1:7687` with empty local authentication.
Lab is available at `http://127.0.0.1:3100`. Versions and all project ports are
recorded once in `../README.md`.

Persistent snapshots and WAL live in the gitignored `tools/memgraph/data/`
bind mount. Do not edit or replace this directory during normal ingestion.

## Input ownership

| Layer | Tracked inputs | Loader owner |
|---|---|---|
| Firmware structure | Ghidra `funcs.csv`, `calls.csv`, and `xrefs.csv` exports | `load_graph.py`, `load_xrefs.py` |
| Map structure and measured values | Resolver censuses, ROM registry, interpolation registry, findings, and axis facts | `load_maps.py` |
| Reviewed firmware claims | `defs/<source>.funcs.csv`, `vars.csv`, `findings.csv`, `axes.csv`, and inheritance model | `load_code.py` |
| Diagnostic bindings | `defs/<source>.diagnostic-bindings.csv` | `load_diagnostic_bindings.py` |
| Global diagnostic corpus | `refs/diagnostics/` projections and source manifests | `ingest_diagnostics.py` |
| Vendor vocabulary | `refs/vendor/` projections | `load_vendor.py` |
| Reference A2L catalog | Pinned reference definitions | `load_a2l.py` |

`tools/rom_sources.py` resolves the target ROM, canonical annotation source,
exact image hashes, code-equality ranges, and default Ghidra export directory.

## Diagnostic corpus

Validate all tracked diagnostic source packs without changing the graph:

```bash
uv run python tools/memgraph/ingest_diagnostics.py --dry-run
```

Run the same command without `--dry-run` to replace the graph-owned diagnostic
scope after validation. The source-preserving extraction and query contract is
in `../diagnostics/README.md`.

## ROM ingestion

Preflight one ROM without graph writes:

```bash
uv run python tools/memgraph/ingest.py JK08A --strict --dry-run
```

Run without `--dry-run` to execute the fixed owner order:

```text
load_graph.py
  -> load_xrefs.py
  -> load_maps.py
  -> load_code.py
  -> load_diagnostic_bindings.py
  -> provenance_report.py audit
```

Preflight validates headers, foreign keys, addresses, ROM identity, inherited
code ranges, map geometry, diagnostic bindings, and claim dependencies before
the first graph write. `--export-dir` overrides the registered local Ghidra
export only for an explicitly selected export.

The diagnostic corpus must exist before a ROM ingest that loads diagnostic
bindings. `ingest_diagnostics.py` owns the corpus and clears every
`:DiagnosticBinding` node when it commits, so a corpus reload is followed by
`load_diagnostic_bindings.py` for each bound ROM. Until that runs, definition
projections omit their static diagnostic context and
`tools/mapkit/validate_map_switching.py` reports a difference from the tracked
common definitions. JK03A receives canonical semantic annotations through
`defs/rom-inheritance.toml` but retains its own ROM measurements and graph
layer.

## Provenance audit

The tracked source columns declare claim-specific evidence. Effective
confidence is computed from these claims and their `RESTS_ON` dependencies; it
is not written back as a second authority.

```bash
uv run python tools/memgraph/provenance_report.py audit JK08A --strict
uv run python tools/memgraph/provenance_report.py weakest JK08A Func 00021ce0 confidence
uv run python tools/memgraph/provenance_report.py impact JK08A Map 0001495a structural
```

The first command checks the complete stored projection against tracked
sources. The other commands explain one weakest dependency path or reverse
impact set. The schema and confidence rules are specified in
`../map-analysis-pipeline.md`.

## Read-only agent access

The project-scoped `mcp-memgraph` server connects to Bolt over stdio and blocks
mutating Cypher. It is an optional query surface over a graph built by the
tracked loaders. Schema discovery requires the compose option
`--schema-info-enabled=true`, which is already set.

Queries intended for repeatable review belong in `queries.cypher` or
`diagnostics_queries.cypher`. Ad hoc read-only queries may inspect the same
projection but do not create durable facts.

## Backup

`backup.py` reads the gitignored `backup.local.toml`; use
`backup.example.toml` as its schema. It validates an SMB mount, obtains a
project lock, creates a gzip-compressed `DUMP DATABASE` and native snapshot,
writes a manifest and SHA-256 files directly to temporary NAS paths, validates
the bundle, and publishes it atomically.

After a task changes graph data or schema, check the interval:

```bash
python3 tools/memgraph/backup.py --status
```

If `due=true`, create one interval-controlled backup:

```bash
python3 tools/memgraph/backup.py --if-due
```

Use `--force` only for an explicit immediate-backup request. Forced mode
bypasses the local and remote 24-hour interval checks but not locking, mount
validation, dump validation, hashes, or atomic publication. Source-only and
documentation-only tasks do not trigger the automatic check.

## Recovery boundary

Compose enables WAL and snapshot recovery at startup. If startup reports a
missing RocksDB `.ldb` only under metadata directories such as `settings`,
`auth`, `databases/.durability`, or `telemetry`, stop the service and preserve
the exact failing directory under a timestamped sibling name before restart.
Do not move or delete `snapshots/` or `wal/`. Confirm `RETURN 1` over Bolt and a
stable container restart count before running any loader.

## Tests

Memgraph unit tests do not require a running database:

```bash
uv run pytest -q tools/memgraph/tests
```

Graph-dependent verification is the dry-run preflight plus the strict
provenance audit against the currently running projection.
