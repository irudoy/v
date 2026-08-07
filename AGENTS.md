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
  `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault/🎛️ Electronics/VQ HR ECU Tuning`.
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

## Authorized project operations

- Tracked Memgraph loaders and migrations may change project graph data or
  schema when required by the task. Do not make ad hoc durable graph mutations.
- The tracked Memgraph backup tool may connect to the configured SMB/NAS and
  create project-data backups without separate confirmation.
- These permissions do not cover `git push`, publication, messages, PRs,
  deployment, or unrelated external systems.
- Do not push unless the user explicitly requests it.

## Memgraph backup

- Check backup status only after a task changes Memgraph data or graph schema:

  `python3 tools/memgraph/backup.py --status`

- If the result says `due=true`, run:

  `python3 tools/memgraph/backup.py --if-due`

- Use `--force` only for an explicit user request for an immediate backup.
- Do not run an automatic backup check for source, documentation, or other
  local file changes that leave the graph unchanged.

## Working conventions

- Read `README.md` and the narrow README beside the subsystem being changed.
- Preserve user changes and unrelated dirty worktree content.
- Generated XML, XDF, ledgers, and diagnostic projections are outputs; edit
  their declared sources and regenerate them.
- Keep text declarative and current. Git and the vault journal retain history.
- `CLAUDE.md` is a symbolic link to this file and must remain one.
