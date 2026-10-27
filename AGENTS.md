# VQ HR ECU Tuning - agent rules

This repository reverse engineers and verifies Hitachi CAN ECUs for VQ25HR,
VQ35HR, and VQ37VHR engines on Renesas SH7058/SH7059 SH-2E MCUs. The active
target is the owned `23710-JK08A` ECU from a V36 Skyline 250GT.

## Workspace boundary

- Repository artifacts are technical and machine-oriented. Write all
  repository documentation, annotations, comments, messages, and generated
  human-readable text in English.
- Planning and human project knowledge live in the Russian-language Obsidian
  vault at
  `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault/Electronics/VQ HR ECU Tuning`.
- The vault entry point is `VQ HR ECU Tuning`.
- Do not mention the private vault or its path in public repository content;
  this file is the only repository location for that path.
- After every task, update the vault in Russian when the result changes the
  plan, current status, a decision, an open question, or durable knowledge.
- Stock ROMs, structured evidence, assembly, patch mechanisms, definitions,
  generators, and verification belong in Git.
- Concrete tuned images, per-image profiles and recipes, active tune identities,
  logs, and generated test outputs must not be committed.

## Evidence and safety

- Ground truth is in the silicon. Graph structure is not semantics.
- Treat Memgraph as a reproducible derived query index. Durable claims belong
  in tracked CSV, TOML, assembly, or narrow specifications.
- Verify claims that affect hardware with CONSULT-III Plus live data or a bench
  before flashing; validate final behavior in the engine when applicable.
- Every patch that adds, removes, replaces, or redirects executable
  instructions must extend and pass `tools/sh-elf-run/`.
- The executable gate must bind exact ROM instruction bytes to an independently
  assembled or reconstructed SH-2E fixture and execute all changed entries,
  branch outcomes, delay slots, call/return paths, and relevant boundaries.
- Document simulator-only relocations and stock-function stubs. They must not
  alter the instruction bytes under test.
- A simulator limitation leaves an image ineligible for hardware testing until
  equivalent executable coverage exists.
- Software gates complement static auditing and hardware validation; they do
  not replace either.

## Work approach

Use small packages that state a user scenario and the knowledge or capability
they change before implementation. Scenarios include calibration, a runtime
feature, ROM porting, subsystem research and a hardware session.

Run affected tests immediately. Full verification runs before flashing and
before closing an engineering track. Source preparation without execution
followed by one deferred acceptance run is not a supported workflow.

Stop a package and ask the user when it doubles its estimated size or active
time, or changes direction. Waiting and calendar delay are not active work.

Knowledge representation transfer is accepted. Reconciliation reviews with
reasons are supported unresolved data. Do not create executable proofs of
stock-code claims unless a named patch-instruction obligation or calibration
decision cannot proceed without one and the user agrees to that scenario.
Such proofs belong in an optional package outside the main dependency path.

Use the KB CLI directly for ordinary knowledge reads. Execution receipts and
command timeouts belong to acceptance runs that require them. Do not create
one-off duplicate runners. Do not use `caffeinate` or change system sleep
settings for project commands.

Issues and planning notes state the result, decision and open question for a
human reader. Keep execution receipts, hashes, exit codes and timing details
in local results and Git.

## Gates and commits

- `make check` validates tracked sources and projections. `make test` runs
  Python tests without the `slow` marker and the pin-tracer contract.
  `make test-full` runs the complete Python and pin-tracer contracts;
  `make test-python` and direct `uv run pytest -q` include every Python test.
  `make verify-firmware` runs the repository-contained GNU SH-2E execution gate.
  `make verify` runs firmware qualification, source checks, and `make test-full`.
- Run affected checks for each small package. Changes to instruction bytes,
  address profiles, or runtime allocation require `make verify` for acceptance.
  Full checks also run before flashing and before track closure. A local
  commit records source state and does not establish successful acceptance.
- Keep machine facts in TOML or CSV owners. Do not repeat repository-owned
  counts in handwritten prose. Each generated section
  has one generator and one consistency check; code and tests do not parse
  prose to recover machine facts.
- `defs/JK08A.architecture.toml` places every reviewed function in one block and
  binds every calculation step to a ledger relation or to a named specification.
  A review that adds a function, a map, or a calculation extends it in the same
  commit; `tools/romviz/architecture.py suggest` ranks candidate blocks and
  `check` reports what remains unplaced. `make check` runs that gate and rebuilds
  the atlas, so the architecture view follows the ledgers on every build.
- Commit coherent changes locally on `master` without waiting for a separate
  instruction. A commit changes one subsystem; explain any cross-subsystem
  exception in its body. Leave unrelated worktree content and other sessions'
  changes unstaged.
- Commit messages follow Conventional Commits: `type(scope): description`,
  with an optional scope. Use `feat`, `fix`, `docs`, `refactor`, `perf`,
  `test`, `build`, `ci`, `chore`, `revert`, or `style` for the change type.
- Keep the English description concise and in the present tense. Put details
  in the body, separated from the header by a blank line.
- Do not use breaking-change markers (`!` or `BREAKING CHANGE`) or agent,
  tool, model, or session attribution.

## Issues

- GitHub issues of `irudoy/vhrev` track the problems and planned work of the
  project. Record every problem that a task finds and does not fix as an
  issue: a defect, a failing, missing, or weak gate, a stale projection, a
  contradiction between tracked sources, an unverified hardware claim, or an
  open question that blocks work.
- Search the open issues before creating one, and extend a matching issue
  instead of opening a duplicate.
- An issue states the observed behavior, relevant source paths, impact,
  proposed fix and checkable acceptance criteria. Keep it short and readable;
  execution receipts, hashes and process timing belong in local results and
  Git. Issues are repository content: write them in English and do not mention
  the private vault.
- Give every issue the type Bug, Task, or Feature, an `area:` label, and a
  `priority:` label, and attach it as a sub-issue of its track epic, an issue
  labelled `epic`.
- Keep issues current. Read the open issues of a subsystem before changing it.
  After a task, update every issue that it affects: check off the acceptance
  criteria it meets, record new findings or a changed scope, and close the
  issue with the commit that resolves it once all its criteria hold, or as not
  planned when a decision retires it.

## Authorized project operations

- Tracked Memgraph loaders and migrations may change project graph data or
  schema when required by the task. Do not make ad hoc durable graph mutations.
- The tracked Memgraph backup tool may connect to the configured SMB/NAS and
  create project-data backups without separate confirmation.
- Issues of `irudoy/vhrev` may be created, edited, commented on, labelled,
  re-parented, and closed under the rules of the Issues section without
  separate confirmation.
- Apart from issues, these permissions do not cover `git push`, publication,
  messages, PRs, deployment, or unrelated external systems.
- Do not push unless the user explicitly requests it.

## Memgraph backup

- Check the backup interval only after a task changes Memgraph data or graph
  schema, and create the backup when the check reports one is due.
- Do not run an automatic check for source, documentation, or other local file
  changes that leave the graph unchanged.
- Force an immediate backup only on an explicit user request.
- The commands and the backup contract are in `tools/memgraph/README.md`.

## Working conventions

- Read `README.md` and the narrow README beside the subsystem being changed.
- Preserve user changes and unrelated dirty worktree content.
- Generated XML, XDF, ledgers, and diagnostic projections are outputs; edit
  their declared sources and regenerate them.
- Keep text declarative and current. Git and the vault journal retain history.

<!-- kb:begin -->

## Knowledge access

Generated by `uv run kb project AGENTS.md#kb` from `tools/kb/contracts.toml` and
`tools/kb/bench.toml`.

- Start with `uv run kb brief`: the graph, the layouts, the owners,
  and the open gaps. `uv run kb` answers what the repository knows
  about the symbols, meanings, links, statuses, and evidence of every
  layout, and the MCP server `kb` serves the same read commands as the
  tools `kb_<command>`. Ask `kb` before searching the registries or reading
  `l0/`.
- The access guard `tools/kb/hook.py` denies reading, searching, and editing
  `kb/` and `l0/`, reading the guarded projections, and editing the files
  that `tools/kb/projections.toml` registers as generated; its reason names
  the command to use. `uv run kb guard off --session <id>` disables it
  for one root session; `on` enables it and `status` shows its saved override.
  `KB_GUARD=off` in the hook environment is the fallback without an override.
- The table below names the current owner of each fact. Change a fact in
  its owner, then regenerate its projections.

| Question | Command |
|---|---|
| What is at an address of another layout | `uv run kb at jk00d:ffff1034` |
| Where a meaning is on every layout | `uv run kb where normalized_load/ram` |
| What depends on a table | `uv run kb impact 7mfk:0000a4aa` |
| How coolant temperature reaches the intake-cam target | `uv run kb path 7mfk:ffff1079 7mfk:ffff2326` |
| Which telemetry sources lack a symbol on a layout | `uv run kb gaps --feature can_telemetry --layout 1nd` |
| Candidates for a producer on another family | `uv run kb suggest 7mfk:0003b75c --layout jk78c` |
| Find entities by words | `uv run kb find knock threshold` |
| The code of a function | `uv run kb code jk78c:000564a4` |
| The history of a symbol through its corrections | `uv run kb log apc_output` |
| The state of the knowledge base | `uv run kb brief` |
| Why telemetry fields are unavailable on a layout | `uv run kb gaps --feature can_telemetry --layout 1me3b` |
| The block and chain steps of a function | `uv run kb show 7mfk:0003deec` |
| The reviewed function facts of a JK08A ledger address | `uv run kb show 7mfk:0003c3ac` |

| Registry | Facts | Owner |
|---|---|---|
| `rom-images/roms.csv` | Images and digests | itself |
| `rom-images/homology.toml` | Families, relationships and layouts | itself |
| `defs/rom-identities.toml`, `defs/rom-inheritance.toml` | Image identities and definition inheritance | themselves |
| Ghidra export directories | Code structure | `l0/<layout>/` |
| `tools/ghidra/symbols/7mfk.csv` | Curated function names of `7mfk` | Names of `fn` meanings |
| `tools/ghidra/symbols/1nd.csv` | Curated function names of `1nd` | Names of `fn` meanings |
| `kb/names.csv` | Generated names of decoder-owned symbols and permanent inactive reservations | itself, with exact owner declarations in `tools/kb/owners.toml` |
| `patches/rom-address-profiles.toml` | Target symbols, hooks, DIDs, telemetry sources and their unavailability, runtime allocations and variants, and their evidence | Meanings and statuses; targets of `runtime`, `map_switching`, `rolling_launch`, and `can_telemetry` |
| `patches/*-runtime-correspondence.csv` | Correspondence of source and target symbols by feature domain | Symbols and statuses |
| Symbol and hook-key tables of `patches/runtime_targets.py` | `7mfk` symbols of the feature meanings and the per-layout hook keys | Symbols and feature targets |
| `defs/definition-projections.toml`, `defs/JK08A-*.definition-addresses.csv` | Relocated definition settings and table addresses | Targets of `definitions`; `tbl` and `axis` meanings and their statuses |
| `defs/*.interp.csv`, `defs/*.interp-correspondence.csv` | Interpolation kernels and wrappers | `fn` meanings with `[interp]` |
| `defs/vq37-native-tables.toml`, `defs/vq37-native-fuel-cut.toml` | Native tables and the fuel-cut mechanism of the VQ37VHR layouts | Meanings with symbols on `jk78c`, `1nd`, and `1me3b` |
| `tools/diagnostics/sid22_inventory.py` | The decoder of the JK08A service 0x22 tables | itself; the `did` symbols of `7mfk` and their `source` links derive from it and the image bytes |
| `defs/JK08A.tuning-signals.toml` | Observation needs | `kb/signal/` |
| `patches/can-telemetry-profile.toml` | Fields, contexts, and wire constants | `kb/field/`; `can_telemetry` |
| `defs/JK08A.overrides.toml` | Editor presentation, logger parameters, checksums, and switches | `[editor]` and `[logparam]` tables; `definitions` |
| Generated telemetry copies: the schema, payload bindings, the host decoder, and dashboard metadata | Placement, conversions, units, names of values and bits, and host presentation of the fields | Generated from fields and meanings |
| `defs/JK08A.funcs.csv`, `defs/JK08A.vars.csv`, `defs/JK08A.findings.csv`, `defs/JK08A.axes.csv` | Code knowledge of `7mfk` | `kb/fn/`, `kb/ram/`, `kb/reg/`, `kb/tbl/`, `kb/axis/` |
| `defs/JK08A.dtc.csv` | DTC descriptors of `7mfk` | `kb/dtc/` |
| `defs/JK08A.diagnostic-bindings.csv` | Diagnostic bindings | `[[diagnostic]]` tables |
| `defs/JK08A.architecture.toml` | Stages, blocks, endpoints, and chains | `kb/stage/`, `kb/block/`, `kb/endpoint/`, `kb/chain/` |
| Code graph of the `tools/memgraph/` loaders | Derived index | The compiler |
| `defs/JK78C.vvel.md`, `defs/JK78C.can.md` | Typed function anchors and selected RAM roles of the VVEL and CAN specifications, including explicit layout comparisons | Meanings with declared-layout symbols and exact `[[source]]` bindings |
| `defs/JK08A.maps.csv` | Map tracker | `tools/maps/build_tracker.py`, which reads the graph |
| `defs/1ND0A-1ME3B.census-correspondence.csv` | Census output | Input of `kb family new` and `kb suggest` |
| `defs/<ROM>.xml`, `defs/<ROM>.xdf`, RomRaider plugin files, the host decoder | Editor and logger definitions | Their generators, which read `kb` |
| `patches/hardware-results.toml` | Hardware records | itself; `hardware` evidence cites it |
| `patches/map-switching-layout.toml`, `patches/rolling-launch-layout.toml`, `patches/can-telemetry-layout.toml`, `patches/jk08a-runtime-reservations.toml`, `patches/checksum-layouts.toml`, `patches/runtime-target-payloads.toml` | Patch design; the `7mfk` hook words, map families, DID slots, and the RAM that each feature allocates, which the adapters read | themselves |
| Source packs under `refs/` | External corpora | themselves; `manual` and `diagnostic` evidence cites them |
| Narrow specifications under `defs/` | Mechanisms in prose | themselves; `specs` keys and `spec` evidence cite them |

<!-- kb:end -->
