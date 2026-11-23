# Memgraph projection and ingestion

Memgraph is a reproducible query index over tracked firmware, annotation, and
diagnostic evidence. It is not a handwritten authority. A complete ingest may
replace graph-owned nodes and relationships; durable claims must therefore live
in the source CSV, TOML, assembly, or specifications referenced by the loaders.

## Service

The primary knowledge API runs Memgraph MAGE for the current working tree:

```bash
uv run kb instance up
uv run kb sync
uv run kb instance down
```

The main working tree uses `bolt://127.0.0.1:7687` with empty local authentication.
Linked working trees use the instance and port selected by `kb instance`.
The port comes from `[instances].ports` in `../kb/config.toml`, with an
exclusive upper bound, and is recorded in that tree's `.kb/instance.toml`.
The main Compose instance also publishes Lab at `http://127.0.0.1:3100` and
the log-stream port. Linked working-tree instances publish their Bolt port.
The service and port index is in [`../README.md`](../README.md#local-services-and-ports).

`kb instance` invokes Docker through the caller's daemon selection. The local
macOS deployment uses the `desktop-linux` context; Linux can use its configured
Docker daemon without a context of that name. Keep instance management on the
same daemon. The GNU firmware gate has a separate fixed `default` context,
described in [`../sh-elf-run/README.md`](../sh-elf-run/README.md#run-the-patch-gate).

Persistent snapshots and WAL live in the gitignored `tools/memgraph/data/`
bind mount. Do not edit or replace this directory during normal ingestion.

## Input ownership

| Layer | Tracked inputs | Loader owner |
|---|---|---|
| Firmware structure | `funcs.csv`, `calls.csv`, and `xrefs.csv` of the L0 of the ROM's layout in `l0/<layout>/`, and the function names of `tools/ghidra/symbols/<layout>.csv` | `load_graph.py`, `load_xrefs.py` |
| Map structure and measured values | Resolver censuses of the L0, ROM registry, interpolation registry, findings, and axis facts | `load_maps.py` |
| Reviewed firmware claims | `defs/registries/<source>.funcs.csv`, `vars.csv`, `findings.csv`, `axes.csv`, and inheritance model | `load_code.py` |
| Diagnostic bindings | `defs/registries/<source>.diagnostic-bindings.csv` | `load_diagnostic_bindings.py` |
| Global diagnostic corpus | `refs/diagnostics/` projections and source manifests | `ingest_diagnostics.py` |
| Vendor vocabulary | `refs/vendor/` projections | `load_vendor.py` |
| Reference A2L catalog | Pinned reference definitions | `load_a2l.py` |

`tools/rom_sources.py` resolves the target ROM, canonical annotation source,
exact image hashes, code-equality ranges, the layout whose L0 holds the ROM's
code, and the curated function names of that layout. A function without a
curated name is `FUN_<addr>` in the graph.

## Diagnostic corpus

Validate all tracked diagnostic source packs without changing the graph:

```bash
uv run python tools/memgraph/ingest_diagnostics.py --dry-run
```

`uv run kb sync` replaces and audits the diagnostic scope before rebuilding
dependent firmware bindings. The source-preserving extraction and query contract is
in `../diagnostics/README.md`.

## ROM ingestion

Preflight one ROM without graph writes:

```bash
uv run python tools/memgraph/ingest.py JK08A --strict --dry-run
```

`uv run kb sync` builds the diagnostic corpus, then each catalog ROM in the fixed
owner order, followed by the vendor vocabulary and pinned A2L catalog:

```text
load_graph.py
  -> load_xrefs.py
  -> load_maps.py
  -> load_code.py
  -> load_diagnostic_bindings.py
  -> provenance_report.py audit
```

The read-only ROM preflight validates headers, foreign keys, addresses, ROM identity, inherited
code ranges, map geometry, diagnostic bindings, and claim dependencies before
the first graph write. Preflight first holds the L0 of the ROM's layout to its
manifest, the Ghidra pin, and the image catalog. `--l0-dir` reads another
directory in the L0 format, such as a staged export, without that check.

The compiler supplies one driver under the primary writer lock to every retained
layer algorithm. Owned annotation and interpolation CSVs are private temporary
views of its current model; the generated working-tree copies are not inputs.
An absent manual catalog contributes no reviewed claims. Firmware structure and
measurements still come from the declared L0 and exact image. The fingerprint
covers the layer code, diagnostic corpus, external vocabularies, inheritance
registry, pinned A2L bytes, and their owned knowledge sources. The compiler
publishes Meta after all layers pass and the input fingerprint still matches.
A failed layer leaves Meta absent, so isolated readers refuse the partial graph.
Exact-input `CompatibilityState` records retain completed independent groups
across a failed sync or a change to the common compiler fingerprint. Each ROM's
coupled layer sequence reloads as a unit; vendor vocabulary and A2L reload
together. Corpus replacement invalidates all dependent ROM records before its
builder removes diagnostic bindings. A record is written only after the whole
group passes a second input check. Builders consume private, read-only copies
of captured bytes; restoration of a temporarily modified working file cannot
change those inputs. The complete census filename inventory is captured so
unexpected files retain the map builder's refusal. `kb sync --full`
reconstructs every group.
Separate loader commands refuse writes and direct callers to `kb sync`.
JK03A receives canonical semantic annotations through
`defs/rom-inheritance.toml` and reads the L0 of layout `7mfk`, but retains its
own ROM measurements and graph layer.

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

The `kb` MCP server checks freshness before answering queries. Tracked definition,
diagnostic, map-tracker, and provenance readers use `kb.reader.session`, which
holds the primary lock, checks the fingerprint, rejects mutation clauses and
write procedures, and rolls back its read transaction. Schema discovery requires the compose option
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
