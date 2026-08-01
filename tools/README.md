# tools - VQ HR ECU RE stack

Reverse-engineering stack infrastructure. The canonical path is **headless Ghidra -> Memgraph
(MAGE) -> LLM agent**: deterministic Java GhidraScript extractors write CSV files, loaders build
the graph as the system of record, and the pipeline runs autonomously or in batches without a GUI.
The agent reads the graph through the `mcp-memgraph` MCP server described in "Memgraph MCP"; it is
headless-native and part of the canonical path. GhydraMCP is an optional interactive accelerator
for live reverse-engineering sessions, described in "GhydraMCP bridge", which requires a GUI and
is outside the critical path. Design, map/flag pipeline, and component roles are documented in
`../AGENTS.md`, `map-flag-pipeline.md`, and the corresponding RE-stack note in Obsidian.

The catalog-wide map sweep is specified in `map-sweep.md`: work unit, wave order, pilot blinding,
submission schema, and gates. The same document defines the read-only caller-semantics harness
`tools/sweep/caller_ab_experiment.py` and its two frozen profiles. The provider-neutral 8-map JK08A
`closure-v1` profile closed without an effect estimate on 2026-07-30: its registered run stopped
after the 10 Prep calls because only two of five caller cards survived adversarial Verify. Opaque
arms and scoring did not run. The profile and its complete operator contract in
`sweep/agent-workflow.md` remain frozen for reproducibility; any further attempt is a new
preregistered experiment. The historical 24-map JK03A `full-v4` profile retains its frozen Claude
Code Dynamic Workflow v3 contract and exact model allowlist.

For both profiles, `freeze` accepts two independent byte-identical builds of map artifacts with
two blind audits and records the exact recursive inventory of the Ghidra export root, embedded
builder and runtime protocol sources, and a private HMAC mapping. Prep creates candidates, while
`finalize-cards` requires complete manual approval with exact payload digests before constructing
`verified` and neutral `placebo` cards. Controls receive a byte-identical sham card. The Python
control plane binds embedded `artifact_text` to `artifact_sha256`, verifies citations and
Analyze/Verify linkage, and rejects fallback, retry, cache reuse, executor drift, incomplete
coverage, and arm markers. Scoring retains each blind score separately. The result reports the
observed paired contrast, sets `causal_claim=false`, and never modifies canonical CSV files.
Manual approval and fresh-launch attestation remain operator trust boundaries rather than
cryptographic proof of human actions.

Git tracks project configuration, wrappers, loaders, analysis scripts, and the browser-based pin
tracer. Large third-party tools and Ghidra projects remain outside the repository because they are
machine-local; their locations are listed below.

## Components and locations

| Component | Version | Location | In git |
|-----------|---------|----------|--------|
| Ghidra | 12.1.2 (JDK 21, ARM native libraries) | `brew`; `GHIDRA_INSTALL_DIR=$(brew --prefix ghidra)/libexec` | no |
| GhydraMCP plugin (optional, interactive) | v3.0.0-rc.1 for ghidra12.1.2 | `.../libexec/Ghidra/Extensions/Ghydra` | no |
| GhydraMCP bridge / CLI (optional, interactive) | v3.0.0-rc.1 | clone at `~/tools/GhydraMCP` (`.venv`, Python 3.11) | no |
| Memgraph MAGE + Lab | mage 3.11.0 | Docker (`memgraph/docker-compose.yml`) | **yes** (compose) |
| `mcp-memgraph` MCP (agent graph access) | 0.2.0 (through `uv`, Python 3.13) | `.mcp.json` at repository root | no (global gitignore) |
| Ghidra project | - | `~/tools/ghidra-projects/vq-hr` | no |
| Headless wrapper | - | `ghidra/headless-analyze.sh` | **yes** |
| ECU pin tracer | schema v1 | `pin-tracer/index.html` | **yes** |

## Manual board tracing

`pin-tracer/index.html` is an offline workspace for tracing the three VQ HR ECM
connectors through observed board components to Renesas SH7058 FP-256H pins.
Its complete interface is available in English and Russian; the selected display
language is persisted without translating operator-entered observations. It
stores work in browser local storage and exports
`vq-hr-ecu-pin-tracer/v1` JSON. The full source, interaction, export, and
provenance contract is in `pin-tracer/README.md`.

A reviewed export supplies the physical bridge from an ESM terminal name to an
MCU peripheral candidate. Firmware work can then verify pin multiplexing, find
the corresponding peripheral-register xrefs, and follow those functions into
control paths and calibration users. Continuity alone does not establish map
semantics or justify `silicon` confidence. No automatic Memgraph ingestion is
implemented; pin-tracer JSON remains a reviewed operator artifact until a
loader and canonical trace storage are added.

## Ports

- `8192`+ - GhydraMCP plugin HTTP ports: the first CodeBrowser uses 8192, the second 8193, and so
  on; the bridge discovers them automatically.
- `7687` - Memgraph Bolt for the `neo4j` driver and Lab; `7444` - log streaming to Lab.
- `3100` - Memgraph Lab UI at http://localhost:3100.
- Memgraph ports are explicitly bound to `127.0.0.1`, the IPv4 loopback, and the stack runs in the
  Docker Desktop context. A second stack in another context such as Lima or colima could occupy
  `127.0.0.1` and push Docker Desktop to IPv6 (`::1`), causing IPv4-first `localhost` and Lab to
  access different data.

## Start the stack

```bash
# 1. Memgraph (MAGE: Louvain, Leiden) - Docker Desktop context ONLY
docker context use desktop-linux            # otherwise a second stack splits localhost
docker compose -f tools/memgraph/docker-compose.yml up -d
#    Data persists in the tools/memgraph/data/ bind mount (snapshots+WAL, gitignored).
#    Graph recovery at startup is automatic (--data-recovery-on-startup).
#    Verify Louvain:
#    docker exec -i vq-memgraph-mage mgconsole <<< "CALL mg.procedures() YIELD name WHERE name CONTAINS 'community_detection' RETURN name;"

# 2. (Optional) Ghidra GUI - only for interactive MCP; see "GhydraMCP bridge".
#    The headless pipeline in step 3 and later is GUI-independent. Starts the HTTP plugin on 8192.
ghidraRun    # the brew wrapper selects JDK 21
#    Then open or create the project, open the program in CodeBrowser, and enable
#    File > Configure > Developer -> GhydraMCPPlugin once.

# 3. Import a dump headlessly (SH-2E core -> SH-2A variant with FPU, big-endian)
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -import rom-images/23710-1ND0A/11ND0A-20260715-stock.bin \
  -processor "SuperH:BE:32:SH-2A" -loader BinaryLoader -loader-baseAddr 0x0
```

### Memgraph startup metadata recovery

If Memgraph exits because a RocksDB `MANIFEST` references a missing `.ldb`
under `settings`, `auth`, `databases/.durability`, or `telemetry`, stop the
Memgraph service before changing the bind mount. Rename only the exact
directory named by the error to a sibling with a
`.corrupt-YYYYMMDD-HHMMSS` suffix, then start the service again. The renamed
directory is retained for inspection and rollback. Do not move or delete
`snapshots/` or `wal/`: graph recovery uses those directories. Verify Bolt
with `RETURN 1` before running a loader, and confirm that the container restart
count remains stable.

## Memgraph MCP (agent graph access)

The agent accesses the graph through the `mcp-memgraph` MCP server over stdio at project scope.
The `.mcp.json` file is at the repository root but excluded by the global gitignore, so create it
on a new machine with the command below. The server is **headless-native**: Memgraph is a server
and requires no GUI, so this MCP works in autonomous runs. It operates in **read-only** mode:
`CREATE/MERGE/DELETE/SET/DROP/REMOVE` are blocked server-side, and only
`memgraph/load_*.py` loaders write to the graph. The compose configuration enables
`--schema-info-enabled=true`, allowing MCP schema discovery through `SHOW SCHEMA INFO`.

```bash
claude mcp add memgraph --scope project \
  -e MCP_TRANSPORT=stdio -e MEMGRAPH_URL=bolt://localhost:7687 \
  -- uv run --with mcp-memgraph --python 3.13 mcp-memgraph
claude mcp list        # memgraph: ✔ Connected
```

The project-scope server requires approval on first launch (`claude` -> approve); otherwise
`claude mcp list` shows `Pending approval`. Tools include `run_query`, `get_schema`,
`get_configuration`, `get_index` / `get_constraint` / `get_storage` / `get_procedures`,
`get_page_rank`, `get_betweenness_centrality`, `get_node_neighborhood`, `search_node_vectors`.

MCP analytical tools operate on all stored nodes, where `:Reg`/`:USES` dominate the call graph.
Raw PageRank therefore ranks RAM registers highest. Use `run_query` with a call-graph projection
for meaningful results; see section 8.2 of `map-flag-pipeline.md`.

## GhydraMCP bridge in Claude Code (optional interactive path)

**Role and boundaries.** GhydraMCP accelerates live reverse-engineering sessions in which a person
and an agent inspect a subsystem. It provides interactive decompilation, xrefs, and call graphs
against a live project within seconds. The plugin is an HTTP server inside the CodeBrowser GUI and
therefore **requires an open project and program**; otherwise tools return empty results. The
`ghydra` CLI mode below is a client for the same plugin and has the same GUI dependency. This MCP
therefore **does not participate in autonomous or batch runs** such as workflows, cron jobs, and
metric regressions; those use the canonical headless path. The bridge does not expose the complete
low-level API required by the operand resolver, including `HighFunction`, CALLIND signatures, and
GBR register context, so that functionality is headless-only. Parameterized headless scripts
answer common interactive questions without a GUI: `DecompileFuncs`, `PoolUsers`, `DumpListing`,
`FindTableRefs`, and `FindPoolWords` by address or literal value.

Register it as the `ghydra` stdio MCP server at local scope for the vq project:

```bash
claude mcp add ghydra --env GHIDRA_HYDRA_HOST=localhost -- \
  ~/tools/GhydraMCP/.venv/bin/python ~/tools/GhydraMCP/bridge_mcp_hydra.py
claude mcp list        # ghydra: ✔ Connected
```

Tools in the `ghydra` namespace include `instances_list` (call first),
`functions_list/decompile`, `xrefs_list`, `analysis_get_callgraph`, `data_list_strings`,
renaming, annotations, and others. The plugin requires an open CodeBrowser with a program;
otherwise tools return empty results.

CLI alternative without MCP: `~/tools/GhydraMCP/.venv/bin/ghydra --json functions list`.

## Graph export (headless)

The GUI-free Ghidra -> Memgraph pipeline uses Java GhidraScript scripts in `ghidra/`, with no
PyGhidra dependency, and loaders in `memgraph/` over the `neo4j` Bolt driver. Run it through
`headless-analyze.sh`.

| Script | Purpose | Output |
|--------|---------|--------|
| `ghidra/ExportGraph.java` | Call graph: functions and CALLS | `funcs.csv`, `calls.csv` |
| `ghidra/ExportXrefs.java` | Peripheral/RAM accesses at `0xFFFE8000` and above, plus literal pools | `xrefs.csv` |
| `ghidra/ExportDiagnosticRefs.java` | Semantic-free 16-bit ROM-reference and instruction-immediate inventory for reviewing SID 0x22 candidates | `diagnostic_refs.csv` |
| `ghidra/TraceRamAccesses.java` | Resolve decompiler p-code LOAD/STORE effective addresses and constant call arguments in a selected RAM range. Optional `--candidates` records unresolved indexed expressions that contain concrete RAM anchors. Arguments: `<outdir> <lo> <hi> [--candidates] [<func_addr>...]` | `ram_accesses.csv`, `ram_calls.csv`, optional `ram_access_candidates.csv` |
| `ghidra/AuditFreeRegion.java` | Verify that an inclusive ROM interval contains one fill byte value and no Ghidra instructions, defined data, function bodies, or inbound references. Arguments: `<lo> <hi> [fill]` | stdout with `status=PASS` or `status=FAIL`; a failed audit also raises a script error |
| `ghidra/AssembleSh2.java` | Assemble a bounded label-aware SH source slice through Ghidra's stand-alone `AssemblyBuffer`, round-trip decode every 16-bit instruction, fill unused bytes, and refuse to overwrite a different output. Arguments: `<source> <output> <base> <end> [fill] [listing]` | raw blob and optional listing outside Git |
| `ghidra/EmulateMapSwitchingSelector.java` | Execute the SHA-locked selector host with the limiter commit; verify state transitions, commits, aborts, feedback blocking, diagnostic mirroring, invalid-index recovery, and protected registers. Arguments: `<selector_blob> <commit_blob>` | stdout with `VQ_SELECTOR_EMU status=PASS` |
| `ghidra/EmulateMapSwitchingAdapters.java` | Execute the two SHA-locked JK08A adapter blobs in Ghidra's SuperH p-code emulator; verify five slots, invalid-index fallback, unrecognized-base pass-through, exact stock-wrapper destinations, and protected-register preservation. Arguments: `<helper_blob> <adapters_blob>` | stdout with `VQ_ADAPTER_EMU status=PASS` |
| `ghidra/EmulateMapSwitchingLimiter.java` | Execute the SHA-locked startup and limiter-commit blobs using exact stock limiter containers, synthetic slot values, and RAM sentinels; verify normalized indices, complete shadows, publication, runtime scalar, SR restoration, return ABI, and write boundaries. Arguments: `<startup_blob> <commit_blob>` | stdout with `VQ_LIMITER_EMU status=PASS` |
| `ghidra/EmulateMapSwitchingBoot.java` | Execute a complete patched ROM from the stock startup thunk through the injected wrapper, the full 1906-byte stock initializer body, the injected fuel-compensation adapter, the stock lookup wrapper, and the limiter commit. Unchanged direct callees of the initializer are deterministic return-zero stubs. The harness verifies stack and callee-saved registers, invalid-index normalization, both limiter shadows, and the stock runtime scalar. Argument: `<patched_rom>` | stdout with `VQ_BOOT_EMU status=PASS` |
| `ghidra/EmulateMapSwitchingReset.java` | Differentially execute a working ROM, generated map-switching ROM, and optional tuned ROM from the exact TRAPA handler through the real startup thunk and one complete scheduler-loop iteration. It checks that nine retained selector values all initialize map 1, plus thunk ABI, scheduler checkpoint state, exact limiter outputs, stack floor, and all RAM outside the declared reservation, selected runtime scalar, and stale stack frames below the restored SP. The live scheduler stack remains compared. Arguments: `<working_rom> <patched_rom> [tuned_rom]` | stdout with `VQ_RESET_EMU status=PASS` |
| `ghidra/EmulateMapSwitchingFeedback.java` | Execute the SHA-locked CAN wrapper and pulse engine with a deterministic serializer stub; verify fail-closed configuration, pulse timing, payload preservation, protected registers, and stack balance. Arguments: `<wrapper_blob> <engine_blob>` | stdout with `VQ_FEEDBACK_EMU status=PASS` |
| `ghidra/EmulateMapSwitchingComposition.java` | Build the exact one-MiB composition from the stock Ghidra program, seven SHA-locked blobs, 14 hooks, 32 copies, and eight pointer tables, then execute all 87 p-code cases from fresh complete-image states. It verifies the fixture hash, write boundary, checksum-field preservation, all ten code entries, limiter SR restoration, and preservation of every non-T SR bit on caller-clobbered paths. Arguments: the seven blobs in manifest order | stdout with `VQ_COMPOSITION_EMU status=PASS` |
| `ghidra/DecompileFuncs.java` | C pseudocode for specified functions | `decomp_<addr>.c` |
| `ghidra/ScanImmoAnchors.java` | Scan immo DTC constants P1610-P1615 and B2193, plus DTC-table clusters | `immo_anchors.csv`, `immo_tables.csv` |
| `ghidra/FindTableRefs.java` | Identify users of a ROM address range or table base through direct and literal-pool references | `table_refs.csv` |
| `ghidra/FindPoolWords.java` | Find PC-relative `mov.w` loads whose literal-pool value matches one or more supplied hexadecimal words. This avoids treating arbitrary equal data words as references. Arguments: `<word_hex>...` | stdout |
| `ghidra/MapInventory.java` | Census maps from an interpolation kernel: value slots -> wrappers -> call sites, with linear `r4/r5/r6` backtracking | `map_inventory.csv` |
| `ghidra/FindInterpCore.java` | Detect interpolation kernels and entries through a data scan in Stage 1: code-address slot plus two indirection levels. Arguments: `<outdir> [<min_wrappers>]` | `interp_core.csv` |
| `ghidra/ScanFlags.java` | Detect GBR flags locally around accessors and guard functions in Stage 6 using the "load - bit test - branch" triple and derive role from CFG branches. Arguments: `<outdir> <func_addr>...` | `flags.csv` |
| `ghidra/ResolveAccessors.java` | Resolve accessor operands using decompiler data flow against backtracking, recover functions for unmarked sites, and expand operand sets (`MULTIEQUAL`) into one row per branch; run once per kernel | `accessors.<kernel>.csv` |
| `ghidra/ProbeResolver.java` | Headless probe for resolver condition A: determine whether the decompiler recovers constant `r4/r5/r6` at interpolation CALLIND sites, baseline versus forced `0x26320` signature; `-readOnly` diagnostic | stdout |
| `ghidra/DirectLookupInventory.java` | Census the implicit-axis bank with a forward scan from its slot, derive primitive geometry from code, and recover operands with linear backtracking | `direct_lookup_inventory.csv` |
| `ghidra/DumpListing.java` | Disassemble an address neighborhood with resolved references | `listing_<addr>.txt` |
| `ghidra/DumpFuncListing.java` | Disassemble an entire function using its body as the boundary. Intended for short arithmetic-library functions whose register-passed argument convention is visible only from the full body. Arguments: `<outdir> <addr...>` | `funclisting_<addr>.txt` |
| `ghidra/FuncAt.java` | Report the function containing an address, including entry, size, and bounds, to assign pool slots through Ghidra function boundaries. Arguments: `<addr...>` | stdout |
| `ghidra/RefsTo.java` | Report instructions referencing an address, their functions, and reference types; the referencing instruction identifies a pool-slot owner. Arguments: `<addr...>` | stdout |
| `ghidra/PoolUsers.java` | Report the function owning an address, pool slot or body, along with its decompilation and referencing instructions. Arguments: `<outdir> <addr...>` | `decomp_<addr>.c` |
| `ghidra/RecoverFuncs.java` | Mark code outside functions as functions; optional verified hexadecimal entry seeds disassemble missing code or split an auto-analysis function that absorbed a known entry. Arguments: `[<addr>...]` | Ghidra project |
| `ghidra/RenameFuncs.java` | Apply curated names from `symbols.csv` to project functions | Ghidra project |
| `ghidra/symbols.csv` | Function-name registry `(addr,name,note)`, the reverse-engineering source of truth | tracked |
| `memgraph/load_graph.py` | Load `:Func` and `:CALLS`, then Louvain over the ROM call-graph projection | Memgraph |
| `memgraph/load_xrefs.py` | Load `:Reg` and `:USES`, including immo analytics for CAN/SCI/RXPR | Memgraph |
| `rom_sources.py` | Resolve the canonical annotation set through `defs/rom-inheritance.toml`; verify exact-code relationships by SHA-256 and byte ranges while always reading values from the target image | tracked |
| `memgraph/load_maps.py` | Calibration layer: resolver censuses plus canonical `interp.csv`, `findings.csv`, and `axes.csv` resolved through `rom-inheritance.toml`, with values read from the target image in Stage 4 -> `:Interp`/`:Map`/`:Axis` and `:ACCESSES`/`:VIA`/`:KERNEL`/`:AXIS_X`/`:AXIS_Y` | Memgraph |
| `memgraph/load_a2l.py` | Load `:A2LEntry` from `A2L.xml` as an address-free, ROM-independent HR-family reference for maps, scalars, and switches | Memgraph |
| `memgraph/load_code.py` | Load the claim-specific layer from canonical `funcs.csv`, `vars.csv`, `findings.csv`, and `axes.csv`: claim properties, exact `:RESTS_ON` projection, and `(:Rom)-[:ANNOTATIONS_FROM]->(:Rom)`; `code`/`silicon` requires factual evidence for every Func/Reg/Map/Axis property; run last after target owners | Memgraph |
| `memgraph/load_diagnostic_bindings.py` | Validate and load the reviewed per-ROM bridge from firmware nodes to diagnostic parameters, DTC codes, or CAN signals; preserve confidence, source applicability, inheritance scope, and priority independently | Memgraph |
| `memgraph/ingest.py` | Complete target-ROM ingest: offline source, export, and image preflight followed by `load_graph -> load_xrefs -> load_maps -> load_code -> load_diagnostic_bindings -> provenance audit`; `--dry-run` leaves the graph unchanged and `--strict` also requires effective confidence and grounding | Memgraph |
| `memgraph/ingest_diagnostics.py` | Validate and load the source-preserving DTC, diagnostic request, parameter, operation, and CAN claim layer without modifying code or calibration nodes; replacement invalidates dependent per-ROM diagnostic bindings | Memgraph |
| `memgraph/diagnostics_queries.cypher` | Query catalog for ROM DTC coverage, source conflicts, diagnostic parameters, CAN routes, and reviewed firmware bindings | tracked |
| `diagnostics/extract_static_bindings.py` | Join exact known service 0x22 DIDs to `diagnostic_refs.csv` and same-function RAM references as a review-only worklist; never creates graph claims | CSV outside Git |
| `diagnostics/*.py` | Deterministic ESM, ROM, and pinned public-source importers plus the read-only diagnostic and binding query CLI and hardware-verified DBC export | tracked CSV/JSONL, Memgraph reads |
| `memgraph/backup.py` | Final agent-workflow step: check the 24-hour interval and SMB mount, then write `DUMP DATABASE`, native snapshot, manifest, and SHA-256 directly to NAS | NAS |
| `memgraph/provenance_report.py` | Read-only exact audit, weakest path, and reverse impact over complete claim identity; `--strict` enables effective-confidence and grounding gates | stdout |
| `memgraph/queries.cypher` | Query catalog for maps, sweep components, projection centrality, reference catalogs, and individual structural gates. `provenance_report.py` performs claim-specific exact audits. Parameter: `$rom` | tracked |
| `maps/build_tracker.py` | Project the graph catalog into the canonical-ROM ledger `defs/<rom>.maps.csv`, including static diagnostic priority and context; an inheriting ROM permits only an explicitly specified temporary output path | tracked |
| `logs/csv_to_mlg.py` | Convert long-form diagnostic CSV updates into validated MLVLG v2 snapshots with timestamp-gap bridging | tracked |
| `sweep/build_artifacts.py` | Build blind sweep artifacts: component `comp-<addr>.md`, frozen map `map-<addr>.md`, or shared axis `axis-<addr>.md`. Axis focus aggregates all related maps and accessors. Shape, values, axes, pseudocode, listings, census operands, and catalogs remain visible; current answers are hidden through an allowlist verified on every run. Budgets must be nonnegative; the frozen caller experiment requires `8`/`24`. Arguments: `<outdir> [--accessor <addr>] [--min-maps N] [--focus-map <addr>] [--focus-axis <addr>]` | Markdown |
| `sweep/caller_ab_experiment.py` | Read-only control plane for caller-semantics profiles: closed-inconclusive 8-map JK08A `closure-v1`, historical 24-map JK03A `full-v4`, frozen HMAC manifests, prep approval, opaque conditions, terminal evidence binding, blind scoring, and per-control verifier gates; canonical CSV remains unchanged | JSON/Markdown outside git |
| `sweep/agent_protocol.py` | Provider-neutral task, receipt, executor, and archive protocol for `closure-v1`; validates isolated no-tools execution, JSON Schema responses, exact Analyze/Verify linkage, raw-output digests, and executor identity without launching a model | JSON outside git |
| `sweep/agent_workflow.py` | Local CLI for building Analyze/Verify/Score batches, validating agent-produced result bundles, and assembling or revalidating provider-neutral agent-run archives | JSON outside git |
| `mapkit/rom.py` | Image library: validate the `rom-images/roms.csv` registry and SHA-256, read arrays, and measure them. Used by `load_maps.py` and package scripts | tracked |
| `mapkit/emit_def.py` | Project the graph, reviewed static diagnostic context, `defs/<rom>.dtc.csv` DTC registry, and the tuner-facing visibility and presentation policy in `defs/<rom>.overrides.toml` into RomRaider `defs/<rom>.xml` and TunerPro `defs/<rom>.xdf`; contract in section 9 of `map-flag-pipeline.md` | tracked as P5 is committed |
| `mapkit/map_switching.py` | Clone the eight canonical JK08A calibration families into the five slot addresses from `patches/map-switching-layout.toml`, preserving graph geometry, scaling, axes, masks, and global maps | imported by the common JK08A definition generator and validator |
| `mapkit/validate_map_switching.py` | Validate the five-slot projection against the live graph and exact ROM, verify identical materialized calibration bytes, and require the tracked common `JK08A.xml` and `JK08A.xdf` to match the projection without a separate identity | stdout; no artifact writes |
| `../patches/map_switching_assembly.py` | Cross-check implemented SH source labels, regions, literal pools, protected registers, control transfers, delay slots, and the explicit SH7058S SH-2E instruction subset against the authoritative map-switching layout; optionally validate generated blobs by manifest SHA-256 | stdout; no ROM write |
| `../patches/map_switching_compose.py` | Apply all seven SHA-locked blobs, 14 hooks, 32 calibration copies, and eight pointer tables to exact stock by default or an explicitly validated compatible input through the library API; reject every change outside the declared composition write set | stdout; no output-file option |
| `../patches/map-switching-payloads.toml` | Store the complete SHA-locked SH-2E assembly-unit spans as hexadecimal data for deterministic patcher use | tracked |
| `../patches/jk08a_checksums.py` | Calculate, verify, and recalculate JK03A/JK08A SUM16 and runtime XOR+SUM domains in dependency order | imported by the patcher and tests |
| `../patches/upgrade_map_switching_reset.py` | Upgrade only the complete pre-fix map-switching runtime with an exact protected upper partition outside declared map-switching and checksum storage: restore the stock fallback zero-fill anchor, install the fixed startup wrapper, recalculate checksums, and preserve every calibration byte | ROM plus MD5 sidecar; non-overwriting |
| `../patches/apply_map_switching.py` | Validate a checksum-valid JK08A input against the exact identity, anchors, erased allocation, and protected upper ROM; initialize alternate maps from input Map 1, install the tracked runtime, recalculate checksums, prove input-byte preservation, and create a non-overwriting ROM plus MD5 sidecar | derived ROM and `.md5` |
| `mapkit/presentation.py` | Normalize functional categories shared by the RomRaider and TunerPro projections without encoding confidence in the category name | imported by both renderers |
| `mapkit/tunerpro.py` | Render XDF 1.70 tables, preserving conversions for split bit fields, reversible two-state patches, 29 individual DTC patches, and group DTC patches from the shared definition model | imported by `emit_def.py` |
| `mapkit/show.py` | Display a map or axis in physical units: the graph supplies shape, axes, and scale, while the image supplies values. Arguments: `[<rom>] <addr>...` | stdout |
| `mapkit/ptrscan.py` | Find pointers to an address by scanning both constant forms, `mov.l` and `mov.w`, without Ghidra or a project. Arguments: `[<rom>] <addr> [<addr_hi>]` | stdout |

```bash
D=~/tools/ghidra-projects/export-1ND0A
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -process 1ND0A_Stock.bin \
  -noanalysis -scriptPath tools/ghidra -postScript ExportGraph.java "$D"
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -process 1ND0A_Stock.bin \
  -noanalysis -scriptPath tools/ghidra -postScript ExportXrefs.java "$D"
uv run --no-project --with neo4j python tools/memgraph/load_graph.py "$D" 1ND0A
uv run --no-project --with neo4j python tools/memgraph/load_xrefs.py "$D" 1ND0A
```

`-process` accepts a program name inside the Ghidra project, not a path under
`rom-images`. The current `vq-hr` project stores programs under the names
`1ND0A_Stock.bin`, `as7058.bin` (JK03A), and
`1JK00D_8MFK36N15-20260726-013734.bin`. The JK08A import command below creates
the `1JK08A-20260726-stock.bin` program.

### Maps: function marking, operand resolution, and graph loading

The map census starts from a shared interpolation engine. Slots containing its pointer identify
wrappers, and call references to wrapper entries identify sites. Both access families use this
structure, so `ResolveAccessors` handles them through one mechanism: the implicit-axis bank
primitive is a wrapper around its own shift chain. The `defs/JK08A.interp.csv` registry lists
entries, one row per family/engine/entry address/geometry. For 1D entries the table element comes
from entry code; for 2D entries it comes from finisher code. Axis point count and element type come
from the search clamp, equal to `(points-1) * element_size`. Run once per engine, producing one
census file each.

Decompiler data flow recovers operands: `r4` is the table base and `r5`/`r6` are explicit-axis
addresses. Linear backtracking remains the gate baseline. Sections 6 and 7 of
`map-flag-pipeline.md` describe the mechanism.

The canonical `export-JK08A-exact` is built from the owned stock image
`1JK08A-20260726-stock.bin`. The legacy `export-JK08A`, derived from exact-code donor `JK03A`,
is retained only as a comparison artifact. Exact-image code bytes match JK03A over
`0x000000..0x0081ff` and `0x020000..0x0fffff`; all 2312 donor function entries are present in the
exact program, and all 13 accessor censuses have the same row sets. The exact auto-analysis also
retains three additional function entries. Map and axis values always come from the registered
JK08A image. The commands below reproduce the canonical export from the separate JK08A Ghidra
program without overwriting the donor-derived artifact.

```bash
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -import rom-images/23710-JK08A/1JK08A-20260726-stock.bin \
  -processor "SuperH:BE:32:SH-2A" -loader BinaryLoader -loader-baseAddr 0x0
D=~/tools/ghidra-projects/export-JK08A-exact
# Use a function rather than a variable: zsh does not word-split an unquoted $H, so a variable
# invocation would silently do nothing.
H() { tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
        -process 1JK08A-20260726-stock.bin \
        -noanalysis -scriptPath tools/ghidra "$@"; }
# 1. Restore verified function entries absorbed by auto-analysis, mark remaining code outside
#    functions, and export the graph in ONE mutating run. These seeds are valid because their
#    bytes and entries were compared with the exact-code JK03A program.
#    ExportXrefs reads the persisted marking in a separate read-only run.
H -postScript RecoverFuncs.java \
  24c2 27d2c 474a4 476d2 763e2 764cc 7c166 a8a5a b7fa6 \
  -postScript ExportGraph.java "$D"
H -readOnly -postScript ExportXrefs.java "$D"
#    Export exact 16-bit references for the review-only diagnostic worklist.
H -readOnly -postScript ExportDiagnosticRefs.java "$D"
uv run --no-project --with neo4j python \
  tools/diagnostics/extract_static_bindings.py JK08A --export-dir "$D"
# 2. Operands: run the resolver for every registered engine. Approximately 100 seconds per census.
for K in 26944 26984 26b84 26a5c 26a60 26a64 26a74 26a7c 26a80 26a84 26a88 26740 26c1c; do
  H -readOnly -postScript ResolveAccessors.java "$D" $K
done
# 3. Complete target-ROM ingest. Before deleting any nodes, preflight validates headers, values,
#    foreign keys, censuses, ROM/SHA, evidence resolution, and factual evidence for every
#    code/silicon Func/Reg/Map/Axis property.
#    The global diagnostic corpus must already be loaded.
#    Order: graph -> xrefs -> maps -> code -> diagnostic bindings -> exact audit.
uv run --no-project --with neo4j python tools/memgraph/ingest.py JK08A --strict
# Preflight and exact commands only, without modifying the graph:
uv run --no-project --with neo4j python tools/memgraph/ingest.py JK08A \
  --strict --dry-run
# Exact-code JK03A uses the same live annotation set but its own export, image, map measurements,
# and graph layer. Only diagnostic rows with rom_scope=exact-code transfer:
uv run --no-project --with neo4j python tools/memgraph/ingest.py JK03A \
  --export-dir ~/tools/ghidra-projects/export-JK03A --strict
# 4. HR reference catalog: ROM-independent and loaded once per family rather than per dump.
uv run --no-project --with neo4j python tools/memgraph/load_a2l.py
# 5. Generated projections after a successful audit.
uv run --no-project --with neo4j python tools/maps/build_tracker.py JK08A
uv run --no-project --with neo4j python tools/mapkit/emit_def.py JK08A
# Read-only validation of the five-slot model embedded in the tracked common
# JK08A XML/XDF files.
uv run --no-project --with neo4j python tools/mapkit/validate_map_switching.py
# The diagnostic JK03A ledger is temporary:
uv run --no-project --with neo4j python tools/maps/build_tracker.py \
  JK03A /private/tmp/JK03A.maps.csv
```

### Map-switching assembly verification

The implemented assembly slices contain the selector host, shared fail-closed
selector helper, four lookup adapters, startup wrapper, limiter commit, CAN
serializer wrapper, and feedback pulse engine. They are built and executed
independently of any ROM image:

```bash
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -process 1JK08A-20260726-stock.bin -noanalysis -readOnly \
  -scriptPath tools/ghidra \
  -postScript AssembleSh2.java \
    patches/map-switching-selector-host.s \
    /private/tmp/jk08a-map-switching-selector-host.bin \
    D2108 D2270 FF \
    /private/tmp/jk08a-map-switching-selector-host.lst \
  -postScript AssembleSh2.java \
    patches/map-switching-adapter-helper.s \
    /private/tmp/jk08a-map-switching-adapter-helper.bin \
    D2270 D22A0 FF \
    /private/tmp/jk08a-map-switching-adapter-helper.lst \
  -postScript AssembleSh2.java \
    patches/map-switching-adapters.s \
    /private/tmp/jk08a-map-switching-adapters.bin \
    D2300 D2400 FF \
    /private/tmp/jk08a-map-switching-adapters.lst \
  -postScript AssembleSh2.java \
    patches/map-switching-startup-wrapper.s \
    /private/tmp/jk08a-map-switching-startup-wrapper.bin \
    D22A0 D2300 FF \
    /private/tmp/jk08a-map-switching-startup-wrapper.lst \
  -postScript AssembleSh2.java \
    patches/map-switching-limiter-commit.s \
    /private/tmp/jk08a-map-switching-limiter-commit.bin \
    D3660 D3760 FF \
    /private/tmp/jk08a-map-switching-limiter-commit.lst \
  -postScript AssembleSh2.java \
    patches/map-switching-feedback-wrapper.s \
    /private/tmp/jk08a-map-switching-feedback-wrapper.bin \
    D35E0 D3660 FF \
    /private/tmp/jk08a-map-switching-feedback-wrapper.lst \
  -postScript AssembleSh2.java \
    patches/map-switching-feedback-engine.s \
    /private/tmp/jk08a-map-switching-feedback-engine.bin \
    D3760 D3860 FF \
    /private/tmp/jk08a-map-switching-feedback-engine.lst \
  -postScript EmulateMapSwitchingAdapters.java \
    /private/tmp/jk08a-map-switching-adapter-helper.bin \
    /private/tmp/jk08a-map-switching-adapters.bin \
  -postScript EmulateMapSwitchingLimiter.java \
    /private/tmp/jk08a-map-switching-startup-wrapper.bin \
    /private/tmp/jk08a-map-switching-limiter-commit.bin \
  -postScript EmulateMapSwitchingSelector.java \
    /private/tmp/jk08a-map-switching-selector-host.bin \
    /private/tmp/jk08a-map-switching-limiter-commit.bin \
  -postScript EmulateMapSwitchingFeedback.java \
    /private/tmp/jk08a-map-switching-feedback-wrapper.bin \
    /private/tmp/jk08a-map-switching-feedback-engine.bin \
  -postScript EmulateMapSwitchingComposition.java \
    /private/tmp/jk08a-map-switching-selector-host.bin \
    /private/tmp/jk08a-map-switching-adapter-helper.bin \
    /private/tmp/jk08a-map-switching-adapters.bin \
    /private/tmp/jk08a-map-switching-startup-wrapper.bin \
    /private/tmp/jk08a-map-switching-limiter-commit.bin \
    /private/tmp/jk08a-map-switching-feedback-wrapper.bin \
    /private/tmp/jk08a-map-switching-feedback-engine.bin \
  -postScript EmulateMapSwitchingBoot.java \
    PATCHED-ROM.bin \
  -postScript EmulateMapSwitchingReset.java \
    WORKING-ROM.bin PATCHED-ROM.bin TUNED-ROM.bin
python3 patches/map_switching_assembly.py \
  --blob selector_host=/private/tmp/jk08a-map-switching-selector-host.bin \
  --blob adapter_select_helper=/private/tmp/jk08a-map-switching-adapter-helper.bin \
  --blob lookup_adapters=/private/tmp/jk08a-map-switching-adapters.bin \
  --blob startup_wrapper=/private/tmp/jk08a-map-switching-startup-wrapper.bin \
  --blob limiter_commit=/private/tmp/jk08a-map-switching-limiter-commit.bin \
  --blob cruise_feedback_wrapper=/private/tmp/jk08a-map-switching-feedback-wrapper.bin \
  --blob cruise_feedback_engine=/private/tmp/jk08a-map-switching-feedback-engine.bin
python3 patches/map_switching_compose.py \
  --blob selector_host=/private/tmp/jk08a-map-switching-selector-host.bin \
  --blob adapter_select_helper=/private/tmp/jk08a-map-switching-adapter-helper.bin \
  --blob lookup_adapters=/private/tmp/jk08a-map-switching-adapters.bin \
  --blob startup_wrapper=/private/tmp/jk08a-map-switching-startup-wrapper.bin \
  --blob limiter_commit=/private/tmp/jk08a-map-switching-limiter-commit.bin \
  --blob cruise_feedback_wrapper=/private/tmp/jk08a-map-switching-feedback-wrapper.bin \
  --blob cruise_feedback_engine=/private/tmp/jk08a-map-switching-feedback-engine.bin
python3 patches/apply_map_switching.py INPUT.bin \
  --output OUTPUT-map-switching.bin
python3 patches/upgrade_map_switching_reset.py PRE-FIX.bin \
  --output PRE-FIX-fixed-reset.bin
```

The boot-path harness reads `PATCHED-ROM.bin` independently of the stock Ghidra
program and requires a complete one-MiB patched image. The reset-path harness
uses the stock program only for its SH language and reads all executable bytes
from its two or three one-MiB input images. Hardware-oriented callees receive
identical deterministic stubs in each image, so the result is differential and
does not claim peripheral emulation. Its RAM comparison excludes only the
declared map-switching reservation, an explicitly selected tuned scalar, and
stale stack frames below the restored SP; the live scheduler stack remains in
the comparison.

The seven locked outputs contain 387 instructions and 158 literal bytes.
The four isolated harnesses and the complete-composition harness each pass
87/87 Ghidra p-code cases over 4530 executed instructions: 17 selector,
47 adapter, 14 startup/limiter, and nine feedback cases. The composition run
executes all ten declared code entries against exact final addresses and real
copied calibration bytes. Only deterministic stock-callee stubs and, in
feedback tests, the two documented frame-count bytes differ between a test
state and the validated complete fixture. The limiter transaction restores the
exact entry SR. Comparison-heavy wrapper and adapter paths preserve every SR
bit except the caller-clobbered T bit.

The reset-path differential over the working base, generated composition, and
reset-fixed tuned candidate passes nine selector seeds and 51,057 executed
instructions. Every seed initializes map 1 and reaches the first complete
scheduler-loop boundary with a minimum SP of `0xFFFF7F84`. The exact normal
path enters TRAPA `0x3E` and never reaches fallback zero-fill function
`0x284E`. The layout therefore retains `0x29CC=0xFFFF7000` as a read-only stock
anchor, while the startup wrapper publishes map 1 before the stock initializer
and commits map 1 after it returns.

The Fuel Cut transaction uses word copies because stock addresses `0x0934E`
and `0x09356` are not longword-aligned. Feedback frame counts at `0xD3848` are
locked to `10, 10`. State `2` in CAN 0x551 byte 5 is an explicit V36
hardware-test hypothesis. Ghidra uses the `SuperH:BE:32:SH-2A` language, while
the source validator permits only 28 used mnemonics listed for the
SH7058S SH-2E core in Renesas REJ09B0177 section 2.4.1. radare2 is not part of
the assembly or verification path. Generated raw blobs and listings are
regenerable temporary artifacts, while their complete validated spans are
tracked in `map-switching-payloads.toml`. The in-memory composer produces
deterministic fixture SHA-256
`499f25ed560bf8e5bc00138e29ceabf740d2f13303eb07604f2e11b537bebb16`,
with 5372 changed bytes inside a 5880-byte declared write set. It retains
feedback counts `10, 10`, verifies 387 final instruction placements and ten
code entries, does not recalculate checksum fields, reports `flashable=false`,
and cannot write a ROM file. `apply_map_switching.py` is the separate file
output boundary: it accepts compatible lower-partition calibration changes,
uses the tracked payloads, recalculates all checksum domains, permits changes
only within the 5880 composition bytes and 20 checksum-reference bytes, and
creates an MD5 sidecar.

`upgrade_map_switching_reset.py` accepts only a complete pre-fix map-switching
image with the locked old startup wrapper, the old `0x29CC=0xFFFF5D00` literal,
all remaining payloads, hooks, and pointer tables intact, the exact stock upper
partition outside declared map-switching and checksum storage, and valid input checksums. It
restores the stock `0x29CC=0xFFFF7000` anchor, installs the reset-fixed startup
wrapper, recalculates all checksum domains, and proves that all calibration
bytes remain unchanged. Its permitted set contains the four-byte anchor, the
96-byte startup-wrapper span, and 20 checksum bytes.

### RomRaider and TunerPro: NATS and DTC controls

`defs/JK08A.xml` contains a `TableSwitch` at `0x08725` with states
`Enabled (Stock) = 01` and `Disabled (IMMO OFF) = 00`. The switch directly clears bit0 of the
factory Developer Immobilizer flag.

The same definition contains 57 native DTC `TableSwitch` controls generated
from `defs/JK08A.dtc.csv`. Each of the 28 emissions records has adjacent
`1/2 Descriptor` and `2/2 Attribute` controls under `Diagnostics / DTC`.
Both controls must be set to `Enabled (Stock)` or both to `Disabled` before
saving. P1610 uses descriptor `0x19540`; its attribute at `0x160FE` is `0000`
in both states, so P1610 has only the descriptor control.

Native checksum handlers run in this order:

1. `alt` recalculates runtime self-test B.
2. `alt2` recalculates runtime self-test A and both SUM16 checksums.

The patcher produces the same result after validating the exact stock ROM:

```bash
python3 patches/apply_immo_off.py --rom JK08A
```

The resulting
`rom-images/23710-JK08A/mods/immo-off/1JK08A-20260727-immo-off.bin`
differs from stock by one bit. Engine start and operation were confirmed on the vehicle.
The patcher preserves the one-bit immo-off contract. P1610 and the other DTC
record changes are controlled only through the definition and require separate
hardware tests.

The same generator writes `defs/JK08A.xdf` for TunerPro. Each of the 29 DTC
records is one atomic `XDFPATCH`: 28 patches contain a descriptor entry and an
attribute entry, while P1610 contains only its descriptor entry. Six additional
patches group records by the manifest `group` field:

| Group | DTC records | Patch entries |
|-------|------------:|--------------:|
| `catalyst` | 2 | 4 |
| `evap` | 13 | 26 |
| `manufacturer_specific` | 1 | 2 |
| `nats` | 1 | 1 |
| `rear_o2` | 8 | 16 |
| `rear_o2_heater` | 4 | 8 |

The group patches cover 57 mutable ranges in total. There is no all-DTC patch.
Individual and group patches intentionally overlap; each patch is internally
atomic, while partial use across scopes makes the corresponding group state
indeterminate. Every entry contains exact stock `basedata`.

The TunerPro XDF also represents Developer Immobilizer as a one-entry
reversible patch. It contains no `XDFCHECKSUM`: editor-side checksum processing
is outside the definition contract, and the flashing workflow corrects
checksums. The split low-7-bit and bit-7 ignition-map views use per-cell address
variables in invertible conversion equations so an edit preserves the
complementary field.

JK08A uses an explicit tuner-facing allowlist in the shared presentation layer.
The generated XML and XDF contain 12 calibration tables and three masked
ignition views; research maps, internal calculations, inactive-family maps, and
standalone reference-axis views remain outside the working editor tree without
being removed from the graph or ledger.

Categories in both generated definitions follow a vendor-style functional tree:
`Fuelling`, `Ignition Timing`, and `Limiters`, with separate `Diagnostics` and
`NATS` controls. They do not partition content by confidence. Names omit ROM
addresses; address and evidence remain in comments or descriptions. The shared
presentation policy removes trailing `(traced)` and `(candidate)` annotations
while retaining map confidence in table comments or descriptions and scale
confidence in `[cand]` unit annotations. XDF header categories use zero-based
indices; one-based `CATEGORYMEM` values refer to those header entries.

### Memgraph backup

Backup runs only as the final step of the agent workflow. Cron and `launchd` are not used.
Create the local configuration from `memgraph/backup.example.toml`; it is not tracked:

```toml
smb_url = "smb://server/Backup"
mount_point = "/Volumes/Backup"
backup_subdir = "vq-memgraph"
minimum_interval_hours = 24
container_name = "vq-memgraph-mage"
mount_timeout_seconds = 30
command_timeout_seconds = 900
```

Checking whether a backup is due does not connect to the NAS:

```bash
python3 tools/memgraph/backup.py --status
```

When the interval has elapsed, the command mounts the share through macOS Keychain and writes the
backup set directly to `/Volumes/Backup/vq-memgraph/.<timestamp>.partial-*`. It publishes the
completed directory by rename only after gzip and SHA-256 validation:

```bash
python3 tools/memgraph/backup.py --if-due
```

`minimum_interval_hours` cannot be less than 24. Local `memgraph/backup.state.json` contains only
the time and path of the last successful backup. A native snapshot is tied to the Memgraph
version. `manifest.json` records the container image, snapshot timestamp, node/edge/index counts,
git commit, and worktree state.

Manual map inspection uses the same facts without Ghidra:

```bash
uv run --no-project --with neo4j python tools/mapkit/show.py b33a   # grid in physical units + axes
uv run --no-project python tools/mapkit/ptrscan.py 11ebe 11ece      # identify pointers to the array
```

The loader consumes every catalog census in one run rather than one kernel per run because it
recreates layer nodes. Loading a second kernel separately would delete the first kernel's maps.
For the same reason, the manual layer and Stage 4 run together: the finding and measurement live
on the same node as the census fact. A census absent from the registry stops loading because its
axis model is unknown. Loading also stops if a census found tables through an entry whose geometry
is undeclared.

`load_code.py` runs last among provenance-target owners because earlier loaders delete their nodes
and all incoming and outgoing `:RESTS_ON` edges. It reads four canonical CSV files, validates nodes
and claim-specific properties, requires factual evidence for every `code`/`silicon` property,
builds 3424 claim-specific JK08A edges, and performs an exact expected-versus-actual audit in one
transaction. Local source gates pass with zero Map/Axis debt. Global `--strict` also passes: the
current JK08A has 1131 source claims and 3424 expected edges;
`effective below declared=0`, `without grounding=0`, 44 cyclic SCCs, and 0
ungrounded SCCs. Read-only verification and interactive queries:

`load_diagnostic_bindings.py` runs after `load_code.py` because its reviewed
claims target firmware nodes and rest on both firmware evidence and
source-specific diagnostic claims. It resolves all dependencies before
replacing a ROM's binding projection. `defs/JK08A.diagnostic-bindings.csv`
contains 41 source rows: 19 exact-code claims and 22 exact-ROM DTC claims. JK03A
inherits only the 19 exact-code rows. Static confidence cannot exceed `code`;
hardware evidence is outside this pipeline milestone.

```bash
uv run --no-project --with neo4j python tools/memgraph/provenance_report.py audit JK08A
uv run --no-project --with neo4j python \
  tools/memgraph/provenance_report.py weakest JK08A Func 00021ce0 confidence
uv run --no-project --with neo4j python \
  tools/memgraph/provenance_report.py impact JK08A Map 0001495a structural
uv run --no-project --with neo4j python \
  tools/diagnostics/query.py binding P0327 --rom JK08A
```

Handwritten sources do not declare table or axis values; the image does. On every run, Stage 4
reads values from the image using addresses and shapes from the census. The image is selected by
ROM label from `rom-images/roms.csv` and verified by SHA-256. Without that check, a substituted
dump would not necessarily fail but could produce 229 axes of plausible values from the wrong
image. Each axis stores its points and monotonicity; each map stores its range and content hash.

The reference censuses, `MapInventory.java` per kernel and `DirectLookupInventory.java` for the
bank, are reproduced site-for-site by the resolver and strictly covered by base addresses. They
remain the comparison baseline for section 7 gates, while the resolver builds the catalog.

`load_a2l` loads the `A2L.xml` catalog into the graph as 188 `:A2LEntry` nodes: 106 maps,
36 scalars, and 46 switches. The base definition has no addresses because the catalog identifies
classes rather than locations; identity, not offsets, transfers between dumps. RomRaider notation
is normalized by axis count (`2D` -> `dims=1`, `3D` -> `dims=2`), while `shape` uses the wrapper
vocabulary (`16x16`, `1D-8`). `:MATCHES` edges are built after Stage 4. Of the matching keys a
`:Map` initially has only `dims`; analysis, not the catalog, supplies scale family and axis
semantics.

With `-readOnly`, `RecoverFuncs` counts and reports without persisting function marking, acting as
a dry run. Without `-readOnly`, it writes the marking to the project for `ExportGraph` to consume.
For JK08A, 38,627 instructions in 494 regions produce 353 functions, increasing the total from
1958 to 2312, after which wrappers `0x26100` and `0x26230` acquire callers.

Across 13 JK08A censuses there are 587 rows for 554 call sites. Data flow recovers a ROM base at
551 call sites, compared with 493 for backtracking. The graph contains **446 maps**: 248
explicit-axis, 188 implicit-axis, 2 implicit two-dimensional, 3 direct row-major,
4 comparator tables, and 1 direct-indexed table. It also has 229 axes, 592 unique accesses, and 47
interpolation nodes, consisting of 34 wrappers and 13 engines.

| Family | Engines | Sites | `bt_r4` | `df_r4` | Wrappers | Maps |
|--------|---------|-------|---------|---------|----------|------|
| explicit-axis | 3 | 327 | 288 | 326 | 24 | 232 |
| implicit-axis | 10 | 227 | 205 | 225 | 10 | 184 |

Base-source distribution across 554 call sites is 407 pool slots, 102 backward slices, 27 phi
nodes producing 59 branch rows, 15 `SymbolicPropogator` fallbacks producing 16 census rows, and 3
unresolved dynamic cases (`dyn`). The loader verifies from its rows that the two families share no
tables. The manual layer declares ten maps outside the census access models,
for a catalog total of 446.

The resolver reproduces both reference censuses site-for-site, 327 and 227 sites, and covers every
reference base. It also recovers 13 additional explicit-axis tables and 16 additional bank tables.
Data validates the new bank tables: 12 of 16 are monotonic, while the remaining four are plateaus
or windows such as `[0,0,0,0,0,0,255,255,255,255,0,0,0,0,0,0]`, indicating calibration
structure rather than noise.

The three unresolved `dyn` bases are marked rather than silently lost. Site `0x4a02c` also has an
empty backtrack result, so its base is dynamic rather than missed. Its axis pointer `0x15340` is
recovered but does not create a node: without a map, the axis purpose is unknown. The census keeps
the value and Stage 6 will restore it when the base is resolved.

Only data flow supplies graph bases. Linear backtracking remains a gate baseline and contributes
no facts. It is wrong on all ten baseline catalog discrepancies: it recovers an axis instead of a
base, loses delay-slot arithmetic, or chooses an arbitrary element of a selector set. Fifteen
projected accesses have an unresolved base with `kind=sp`, represented by 16 census rows before a
full duplicate collapses. The recovered value is one element of a branch-selected set; Stage 6
recovers the complete set.

Fallback behavior is similarly unreliable for axes. There are 256 projected accesses at 247 call
sites with an unresolved axis (`kind5`/`kind6=sp`), and 14 of 229 axes depend solely on this
fallback. Those axes are marked `pattern`; any resolved site raises them to `candidate`. A direct
counterexample is site `0x735ac`, which reports `0x8000` as an axis even though that address
contains erased flash. The same mechanism produces ambiguous geometry: `0x14114` has axes
`0xE98E` and `0x8000` on one edge. Definition gates reject this map until Stage 6 resolves it.

Axis element type belongs to the `(wrapper, axis)` pair rather than the engine. A wrapper calls a
separate search for each axis and can use different searches. `0x262E0` uses byte search
`0x26A0C` for `r5`, clamp 15, and word search `0x26984` for `r6`, clamp 30. `0x26660` uses the
same mixed pair through `0x26BC4`/`0x26B84`. Two of the 22 two-axis wrappers behave this way. The
call delay-slot clamp equals `(points-1) * element_size` and independently confirms the point
count for all 24 wrappers. Image measurement, not code reading, exposed the mismatch: axes
`0x11D0C` and `0x18716`, originally declared as words, are not monotonic as words but produce the
same stepped load curve as bytes. See the axis-element section in `defs/JK08A.notes.md`.

### Locating immo through DTC anchors

The ECM represents immo status as DTCs P1610-P1615 in group `0x0d`. Follow this path from
numeric immo DTC constants to the DTC table and its addressing code. The immo CAN ID is not
publicly documented, so the anchors are numeric:

```bash
D=~/tools/ghidra-projects/export-1ND0A
H() { tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
        -process 1ND0A_Stock.bin -noanalysis -scriptPath tools/ghidra "$@"; }
H -postScript ScanImmoAnchors.java "$D"              # immo DTCs + DTC-table cluster
H -postScript FindTableRefs.java  "$D" 1b000 1c400   # identify table users
H -postScript DumpListing.java    "$D" <addr>...     # use sites (reference -> value)
```

For 1ND0A the result is DTC table `0x1bdfc`, with 12-byte records and DTC at `+0x0a`; immo block
indices 42-47; and status engine `immo_dtc_status_engine` at `000b741e` -> RAM DTC status at
`0xFFFED700` and above. The corresponding Obsidian project note contains details and the remaining
injection-gate work.

### Updating function names (reverse engineering -> graph)

Confirmed function names, replacing `FUN_xxxxxxxx`, are maintained in git as the single source of
truth in `tools/ghidra/symbols.csv` with `(addr,name,note)` columns. Ghidra and Memgraph are
consumers: the script applies names to the project for decompilation, and export carries them into
the graph.

```bash
D=~/tools/ghidra-projects/export-1ND0A
SYM=$(pwd)/tools/ghidra/symbols.csv
H() { tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
        -process 1ND0A_Stock.bin -noanalysis -scriptPath tools/ghidra "$@"; }
# 1-2. Run RenameFuncs + ExportGraph in ONE headless invocation. Consecutive separate runs can
#      race for the Ghidra project lock; the second opens read-only and does not export names.
H -postScript RenameFuncs.java "$SYM" -postScript ExportGraph.java "$D"   # names -> project -> funcs.csv
uv run --no-project --with neo4j python tools/memgraph/load_graph.py "$D" 1ND0A   # 3. -> graph
uv run --no-project --with neo4j python tools/memgraph/load_xrefs.py "$D" 1ND0A   #    restore USES
```

The direction is one-way: edit `symbols.csv` -> Ghidra + Memgraph. Renames performed in Lab or the
Ghidra GUI do not flow back into git and are lost on reload, so add new findings to `symbols.csv`.
`load_graph` recreates `:Func` with DETACH DELETE, so run `load_xrefs` immediately afterward or
peripheral `:USES` edges will be lost.

## Restore on a new machine

1. `brew install ghidra` installs openjdk@21 and builds ARM native libraries.
2. `docker compose -f tools/memgraph/docker-compose.yml up -d`.
3. Add Memgraph MCP with `claude mcp add` as described under "Memgraph MCP". `uv` must be in
   `PATH`; approve the project-scope server on first launch.
4. Optional interactive path: download `Ghydra-*-ghidra12.1.2.zip` from
   starsong-consulting/GhydraMCP releases and extract it under
   `$(brew --prefix ghidra)/libexec/Ghidra/Extensions/`.
5. Optional interactive path: clone GhydraMCP, run
   `uv venv .venv && uv pip install -e .`, and add it with `claude mcp add` as shown above.

The plugin's `ghidraVersion` in `extension.properties` must match the installed Ghidra version.
After `brew upgrade ghidra`, reinstall the plugin build for the new version.
