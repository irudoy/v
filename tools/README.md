# Tool index

The canonical reverse-engineering path is headless:

```text
stock ROM + tracked annotations
  -> Ghidra structure exports
  -> reproducible Memgraph query index
  -> reviewed definition and ledger projections
```

Ghidra projects, third-party applications, and generated exports are
machine-local. Loaders never promote graph structure to firmware semantics;
durable claims remain in tracked CSV, TOML, assembly, and specifications.

## Navigation

| Area | Responsibility | Contract |
|---|---|---|
| Ghidra | Import ROMs, recover structure, export calls/xrefs, inspect addresses, and run p-code fixtures | [`ghidra/README.md`](ghidra/README.md) |
| Memgraph | Validate tracked sources, ingest ROM and diagnostic layers, audit provenance, query relationships, and back up graph state | [`memgraph/README.md`](memgraph/README.md) |
| Knowledge model | Specify the per-layout symbols, meanings, links, and evidence, the `kb` entry point, and the transition from the current registries | [`kb/SPEC.md`](kb/SPEC.md) |
| Map analysis | Inputs, graph schema, current analysis stages, confidence, provenance, and reproducibility | [`map-analysis-pipeline.md`](map-analysis-pipeline.md) |
| Definitions | Project reviewed facts into RomRaider XML, TunerPro XDF, and the map ledger | [`mapkit/README.md`](mapkit/README.md) |
| Diagnostics | Build, validate, ingest, and query factory and community diagnostic evidence | [`diagnostics/README.md`](diagnostics/README.md) |
| SH-2E execution | Independently assemble exact patch bytes and execute firmware behavior fixtures | [`sh-elf-run/README.md`](sh-elf-run/README.md) |
| Logs | Audit PEAK CAN traces and convert CONSULT-style CSV recordings to MegaLogViewer MLG | [`logs/README.md`](logs/README.md) |
| CAN dashboard | Display VQ custom telemetry through PCAN-USB on Windows and macOS | [`can_dashboard/README.md`](can_dashboard/README.md) |
| Pin tracer | Record reviewed ECM terminal-to-board-to-MCU continuity observations | [`pin-tracer/README.md`](pin-tracer/README.md) |
| ROM atlas | Generate an interactive flash layout from reviewed evidence and patch manifests | [`romviz/README.md`](romviz/README.md) |
| ROM homology | Measure exact ranges, fixed-address deltas, and relocated exact code windows across stock images | [`../rom-images/README.md#homology-baseline`](../rom-images/README.md#homology-baseline) |
| Vendor catalog | Rebuild the machine-readable vendor vocabulary used by map analysis | [`../refs/vendor/README.md`](../refs/vendor/README.md) |
| ROM composition | Build and verify complete exact-family runtime images | [`../patches/rom-builder.md`](../patches/rom-builder.md) |

## Tracked components

| Path | Role |
|---|---|
| `rom_sources.py` | Resolve ROM identities, canonical annotation inheritance, exact images, and export roots |
| `diagnostic_context.py` | Render reviewed diagnostic bindings for definition and ledger projections |
| `ghidra/*.java` | Deterministic GhidraScript extraction, inspection, and p-code fixtures |
| `memgraph/ingest.py` | Complete preflight and ordered ingestion for one ROM |
| `memgraph/ingest_diagnostics.py` | Validate and ingest the global diagnostic corpus |
| `mapkit/emit_def.py` | Emit the paired XML and XDF projections |
| `mapkit/definition_targets.py` | Bind target editor identity and stock ROM to canonical exact-code definition sources |
| `mapkit/definition_projections.py` | Validate and apply SHA-bound relocated map and axis correspondences |
| `census_homology.py` | Pair the accessor census of two ROMs at table level and validate the tracked ledger |
| `maps/build_tracker.py` | Emit the reviewable map ledger projection |
| `diagnostics/*.py` | Source-preserving diagnostic import and read-only query layer |
| `can_dashboard/app.py` | Tkinter live view for strict custom telemetry and stock CAN context |
| `can_dashboard/widgets.py` | Responsive flow, grid, scroll, copyable status, and tool button widgets |
| `can_dashboard/icons.py` | Vector button icons drawn on a Tk canvas at the caption size |
| `can_dashboard/package_windows.py` | Reproducible portable Windows source-package generator |
| `can_dashboard/package_macos.py` | Native arm64 macOS application and ZIP generator |
| `sh-elf-run/run.sh` | Repository-contained instruction execution gate |
| `sh-elf-run/run-npkern.sh` | Optional exact-revision external npkern gate |
| `romviz/build.py` | Self-contained interactive ROM address-space atlas generator |
| `romviz/architecture.py` | Firmware architecture gate, model export, and block, impact, path, and chain queries |
| `rom_homology.py` | Validate declared ROM families and regenerate pairwise homology measurements |
| `version_index.py` | Hold the deployment table to the version pins builds, containers, and wrappers execute |
| `single_source.py` | Hold repeated constants, ROM lists, and published counts to the file that owns each |

The full Python contract is configured in `../pyproject.toml` and runs with
`uv run pytest -q`. JavaScript tests belong to the pin tracer and are documented
there. Firmware execution tests belong to `sh-elf-run/README.md`.

## Local deployment

This table is the single project record for machine-local component versions
and locations. Narrow tool documents describe usage but do not name versions.
`version_index.py --check` reads every pin below from the file that executes it
and fails when the table or another tool document carries a different value.

| Component | Version | Local location or source |
|---|---|---|
| Ghidra | 12.1.2 with JDK 21 and ARM native libraries | Homebrew; `$(brew --prefix ghidra)/libexec`; pinned in `ghidra/headless-analyze.sh` |
| Ghidra project | Local project | `~/tools/ghidra-projects/vq-hr` |
| Memgraph MAGE | 3.11.0 | `memgraph/docker-compose.yml` |
| Memgraph Lab | 3.11.0 | `memgraph/docker-compose.yml` |
| `mcp-memgraph` | 0.4.1 | `../.mcp.json`; machine-local and untracked, so the gate checks it only where it exists |
| GNU SH toolchain | GCC 13.3.0, binutils 2.44, GDB SH simulator 16.3 | Image built from `sh-elf-run/Dockerfile`; the simulator version is required by `sh-elf-run/verify_map_switching.py` |
| Python | 3.11 | `../pyproject.toml` and `../uv.lock` |
| CAN dashboard | 8.12.0 | `can_dashboard/__init__.py` |
| PyInstaller | 6.21.0 | `can_dashboard/requirements-macos-build.txt` |
| `python-can` | 4.6.1 | The three `can_dashboard/requirements-*.txt` pins |
| `tzdata` | 2026.3 | `can_dashboard/requirements-windows.txt` |
| External npkern source | Revision locked by `run-npkern.sh` | Default `../../oss/npkern` |

## Local services and ports

| Endpoint | Purpose | Boundary |
|---|---|---|
| `127.0.0.1:7687` | Memgraph Bolt | Empty local authentication; Docker Desktop context |
| `127.0.0.1:7444` | Memgraph log stream | Compose network to Lab |
| `127.0.0.1:3100` | Memgraph Lab | Optional local browser UI |
| `127.0.0.1:47809` | Dashboard UDP telemetry feed | Local datagrams to a log viewer |
| `127.0.0.1:8765` | Pin tracer static server | Local browser UI started on demand |

Memgraph must run in the `desktop-linux` Docker context. Starting another copy
under Lima or Colima can split IPv4 and IPv6 `localhost` traffic between two
independent databases. The complete startup, recovery, and ingestion contract
is in `memgraph/README.md`.

## Headless inspection

The pipeline does not use a Ghidra GUI. Function decompilation and listings on
demand come from `ghidra/decompile.sh`, which runs headless Ghidra against the
local project and caches its output in the machine-local export directory; a
request for functions that are not cached yet completes in seconds. The
project-scoped `mcp-memgraph` server is read-only and is suitable for headless
queries after tracked loaders build the graph.

## Data boundaries

- `tools/memgraph/data/` is ignored persistent database state. Tracked loaders
  are the reproducibility boundary; do not edit the bind mount manually.
- Ghidra projects and exports remain outside Git under local project paths.
- XML, XDF, the map ledger, and diagnostic tables are generated projections.
- Hardware-result identities belong in `../patches/hardware-results.toml`, not
  in command documentation.
- Concrete tuned images and local profiles remain outside the repository.
