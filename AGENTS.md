# VQ HR ECU Tuning - AGENTS.md

Reverse engineering and tuning of CAN ECUs for Nissan/Infiniti HR-series engines
(Hitachi ECU, Renesas SH7058 / SH7059 MCU, SH-2E core):

- **VQ37VHR** - VVEL + dual CVTC;
- **VQ35HR**, **VQ25HR** - dual CVTC, without VVEL.

The test platform is an available **V36 Skyline 250GT** with a VQ25HR engine and a
`23710-JK08A` ECU. Its flash ROM was read with PCMFlash. The executable code is
byte-identical to the donor `JK03A`, while calibration and configuration differ
(`rom-images/README.md`). Reflashing uses **SM2PRO** over J2534 in bench/boot mode.
Factory diagnostics use **CONSULT-III Plus** through **Nissan VCI WiFi**.

## Two-workspace model

1. **Git repository** (this directory) - technical, machine-oriented, and binary
   artifacts: ROM dumps, disassembly exports, definition files (XDF / RomRaider),
   checksum scripts (nissutils), Ghidra/Memgraph tooling, and data logs. All
   repository documentation, annotations, comments, messages, and generated
   human-readable text are written in English.
2. **Obsidian vault** - human-oriented documents: plan, roadmap, progress,
   knowledge base, decisions, and open questions. It is the **source of truth for
   planning and project knowledge** and continues to be maintained in Russian. It
   is synchronized through iCloud and available from a phone.
   - Path: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault/🎛️ Electronics/VQ HR ECU Tuning`
   - Entry point (MOC): **`VQ HR ECU Tuning`**.

Planning and knowledge belong in the vault; dumps and scripts belong in the
repository. After every task, the agent checks whether the result changes the
project plan, progress, decisions, open questions, or knowledge base. If it does,
the corresponding vault notes are updated in Russian as the final task step.

## Actions allowed without confirmation

Within the **VQ HR ECU Tuning** project, the following actions are allowed without
showing parameters in advance or obtaining separate user confirmation:

- any changes to the project Memgraph database, including creating, changing, or
  deleting data, indexes, constraints, and other database objects;
- any changes within the project directory in the Obsidian vault at the path
  above, including creating, changing, moving, or deleting notes, directories,
  and attachments;
- creating and updating project-data backups in external storage systems,
  including SMB/NAS, as well as connecting the storage, transferring the data,
  and running the standard backup scripts required for that purpose.

This permission applies only to this project's data and its backups. It does not
cover `git push`, publication, sending messages, or other external-system changes
that are not project-data backups.

## Reverse-engineering stack

The canonical path is headless:

```text
Ghidra (decompilation + call/xref/data-flow export, Java GhidraScript)
  -> Memgraph (structure graph, homology, persistent project memory)
  -> LLM agent (operating on the graph and headless artifacts)
```

The pipeline does not depend on a GUI and runs autonomously or in batch mode.

The local arm64 deployment uses Ghidra 12.1.2 with JDK 21 and native components,
plus Memgraph MAGE with Louvain/Leiden. The agent reads the graph through the
project-scoped, read-only `mcp-memgraph` stdio MCP server. This server is
headless-native and therefore part of the canonical path; loaders remain
responsible for graph writes. GhydraMCP, consisting of the plugin and the
`ghydra` stdio bridge in Claude Code, is an optional interactive accelerator for
live reverse-engineering sessions. It requires an open Ghidra GUI and is outside
the critical path. Versions, ports, startup commands, and roles are documented in
`tools/README.md` and `tools/map-flag-pipeline.md`.

Verification discipline: **ground truth is in the silicon.** Graph structure is
not semantics. Every technical claim must be verified on hardware with
CONSULT3P live data or a bench before flashing; the final result is validated in
the engine.

## Memgraph backup

Memgraph backup is a separate final step in the agent workflow. No operating
system scheduler is used. After a task that changes project files or the graph,
the agent checks whether a backup is due:

```bash
python3 tools/memgraph/backup.py --status
```

If `due=true`, the agent performs one run without separate confirmation:

```bash
python3 tools/memgraph/backup.py --if-due
```

An explicit user request for an immediate backup permits one forced run:

```bash
python3 tools/memgraph/backup.py --force
```

Forced mode bypasses only the local and remote 24-hour interval checks. Locking,
SMB mount validation, dump validation, hashes, and atomic publication remain mandatory.
Agents do not use forced mode for the automatic final backup check.

The script mounts the SMB share from the gitignored
`tools/memgraph/backup.local.toml`, verifies that the destination is an SMB
mount, and `--if-due` does not create a backup more often than once every 24
hours. A backup contains a gzip-compressed `DUMP DATABASE`, a native snapshot, a
manifest, and SHA-256 hashes. Intermediate data is written directly to the NAS.
Read-only work and responses without local changes do not trigger a backup.

## Repository map

- `rom-images/` - ROM dumps (`*.bin`): a VQ37VHR homolog pair from the RomRaider
  forum (SH7058 USDM / SH7059 JDM); the VQ25HR exact-code family comprising
  donor `JK03A`, owned pre-write baseline `JK03B`, and owned target `JK08A`;
  the owned VQ35HR-class bench baselines `JK00C` and `JK00D`, which use
  different code bases; and derived image `1JK08A-20260727-immo-off.bin`.
  Each part number has its own
  `23710-XXXXX` directory; modifications live under `mods/<short-desc>/`. These
  files are versioned. The `rom-images/README.md` manifest records SHA-256,
  part number, identification, and provenance. A dump is identified by SHA-256.
- `refs/` - external datasheets and manuals (Renesas SH7059 hardware manual,
  PCMflash module list, Bosch LSU 4.9, NERS, MoTeC M150, UpRev), the complete
  2007 Infiniti G35 Sedan factory ESM with 56 PDFs under
  `refs/nissan-esm-2007-g35-sedan/`, plus the NissanECU RE wiki mirror under
  `refs/nissanecu-wiki/`. The machine-readable ESM projection is stored
  separately under `refs/diagnostics/nissan-esm-2007-g35-sedan/`. Original PDFs,
  MarkItDown conversions (`*.md`), and `refs/README.md` are versioned.
- `tools/` - reverse-engineering infrastructure: `ghidra/` contains Java
  extractors, `headless-analyze.sh`, and `symbols.csv`; `memgraph/` contains the
  Memgraph MAGE `docker-compose.yml` and `load_*.py` loaders;
  `maps/build_tracker.py` builds the ledger; `mapkit/emit_def.py` generates the
  RomRaider XML and TunerPro XDF definitions; `pin-tracer/` records manually
  observed ECM-terminal-to-MCU routes. Reviewed pin-tracer JSON connects ESM
  signal semantics to peripheral-register and firmware xref analysis, but
  physical continuity alone does not prove map semantics. `map-flag-pipeline.md`
  specifies the map pipeline, and `README.md` records versions, ports, and
  commands. Ghidra, GhydraMCP, and Ghidra projects remain outside Git.
- `AGENTS.md` - this file.
- `.gitignore` - ignores operating-system debris, scratch data, and regenerable
  Ghidra/Memgraph caches. Content artifacts such as ROMs, datasheets,
  definitions, and mirrors are versioned.
- `defs/` - table definitions. `JK08A.*` is the only live annotation set for the
  exact-code family. `rom-inheritance.toml` projects it onto a separate JK03A
  measurement layer without copying source CSV, ledger, or XML files. JK03B
  remains an inventoried binary without an export, graph layer, or annotation
  inheritance entry.
  `defs/reference/` contains submodules with public RomRaider Nissan definitions
  (Pytrex and a33b); their manifest and relevance are in `defs/README.md`.
- `patches/` - the immo-off specification and patcher
  (`immo-off-developer-flag.md`, `apply_immo_off.py`,
  `tests/test_immo_off.py`), the ROM-library layout test
  (`tests/test_rom_images_layout.py`), and the ROM checksum specification
  (`rom-selftest-checksum.md`, covering SUM16, runtime self-test domains, and
  recalculation order). The derived image is under
  `rom-images/23710-JK08A/mods/immo-off/`. Ghidra exports and the Ghidra project
  are regenerable and remain outside the repository under
  `~/tools/ghidra-projects/`.

## Conventions

- Repository language: English, with technical precision and no invented facts.
  Terms that are more precise in their original form remain untranslated.
- Obsidian vault language: Russian.
- Text describes the current state declaratively rather than narrating the work
  that produced it.
- Do not push without an explicit user request.
