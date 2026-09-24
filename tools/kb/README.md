# kb

`kb` is the entry point of the knowledge model that
[`SPEC.md`](SPEC.md) specifies. The package implements the specification
stage by stage; this document describes the commands and modules that exist.

## Commands

```bash
uv run kb check                      # every active check; exit 1 on a failure
uv run kb check --only l0            # one check
uv run kb code 7mfk:00026742         # decompilation of the function whose body holds the address
uv run kb code 7mfk:00026740 -l      # decompilation and listing
```

- `kb check` runs the `l0` check, which `make check` includes.
- `kb code` resolves an address to the function whose L0 body holds it and
  calls `tools/ghidra/decompile.sh` for that function's layout image. The
  decompilations and listings stay in the local export directory as the cache
  of `kb code`; `-f` reruns Ghidra. An answer longer than its budget in
  `config.toml` starts with a `TRUNCATED:` line; `--budget` and `--full`
  change the budget.
- Exit codes follow the specification: 1 for failed checks, 2 for usage
  errors, 5 for an unknown layout or address, and 6 for a failed Ghidra run.

## L0

`l0/<layout>/` holds the normalized Ghidra exports of each layout of
`rom-images/homology.toml` with `manifest.toml`.
[`../ghidra/README.md`](../ghidra/README.md#l0-exports) describes
`tools/ghidra/export-l0.sh`. The `l0` check verifies, for every layout:

- the manifest against the layout, the image catalog digest, the Ghidra pin,
  the digests of the export scripts, and the census plan of `config.toml` and
  the interpolation registry;
- the file set, each file's digest and row count, and the normal form.

A file whose digest the check has verified in normal form is recorded in
`.kb/cache/l0-normal.json`, so a repeated check hashes the files and skips
the parse.

## Modules

| Module | Role |
|---|---|
| `kb.repo` | Repository paths, the image catalog, the layouts, and the configuration |
| `kb.l0` | L0 export, normal form, manifest, and the `l0` check |
| `kb.sh2` | SH-2E instruction decoding for the derivations |
| `kb.derive` | Function bodies and literal pairing over L0 and the layout image |
| `kb.sites` | Reproduction of the `site:` evidence of the ledgers from L0 |
| `kb.cli` | The command line |

Literal pairing propagates register values through the control flow of each
function body. A register holds a pool literal at an instruction when every
path from the function entry reaches the instruction with that literal,
copied or offset by immediates; a call clears r0 through r7 after its delay
slot. An access through such a register yields the accessed address, the
literal, its pool address, and the base register. An R0-indexed access whose
index is unknown yields the table base.

`kb.sites` classifies each `site:` token of a ledger row by the first relation
that connects it to the row in L0: a reference at the site, the body of a
function the row names, a 32-bit pointer in the image, or the body of a
function that L0 links to the row's subject. The tests require the share of
the JK08A ledgers that stage 1 of the specification states.

## Configuration

`config.toml` lists the L0 export scripts, the census plan of each layout, and
the output budgets of the commands. `.kb/` holds the per-worktree state and is
ignored by git.

## Tests

```bash
uv run pytest -q tools/kb/tests
```
