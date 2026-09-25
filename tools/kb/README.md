# kb

`kb` is the entry point of the knowledge model that
[`SPEC.md`](SPEC.md) specifies. The package implements the specification
stage by stage; this document describes the commands and modules that exist.

## Commands

```bash
uv run kb sync                       # compile, draw names of new symbols, load the graph
uv run kb sync --full                # reload every element of the graph
uv run kb instance up                # start the graph instance of this working tree
uv run kb instance status            # instances of the repository and their state
uv run kb cypher "MATCH (m:Meaning {name: \$n}) RETURN m" --param n=hcan1_init
uv run kb check                      # every active check; exit 1 on a failure
uv run kb check --only l0            # one check
uv run kb audit                      # disagreements between registries
uv run kb code 7mfk:00026742         # decompilation of the function whose body holds the address
uv run kb code 7mfk:00026740 -l      # decompilation and listing
```

- `kb check` runs the active checks, which `make check` includes: `l0`, and
  the model checks `schema`, `names`, `references`, `symbols`, and `links`
  over the compiled registries.
- `kb sync` compiles the registries into the model, appends a generated name
  to `kb/names.csv` for every symbol that has neither a semantic name nor a
  row, and loads the graph under `.kb/lock`. The `names` check fails until
  `kb sync` has named every such symbol.
- `kb cypher` runs one read-only query after the fingerprint check: it
  refuses write clauses and write procedures with exit code 2, runs the query
  in a transaction that it rolls back, and syncs a stale graph first unless
  `--no-sync` is given, which exits with code 6 instead. `--param` binds a
  query parameter, `--json` prints the records as JSON without a budget.
- `kb instance up|down|status|prune` manages the graph instance of the working
  tree ([Graph](#graph)).
- `kb audit` prints three sections: `disagreements`, where two registries
  state different values of one fact; `names`, the registry names of a meaning
  that lose to a name of higher precedence; and `untyped`, legacy evidence
  tokens that lack the keys of their evidence kind.
- `kb code` resolves an address to the function whose L0 body holds it and
  calls `tools/ghidra/decompile.sh` for that function's layout image. The
  decompilations and listings stay in the local export directory as the cache
  of `kb code`; `-f` reruns Ghidra. An answer longer than its budget in
  `config.toml` starts with a `TRUNCATED:` line; `--budget` and `--full`
  change the budget.
- Exit codes follow the specification: 1 for failed checks, 2 for usage
  errors, 5 for an unknown layout or address, 6 for a failed Ghidra run or an
  unavailable or stale graph, and 7 for a lock timeout.

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

## Model

The compiler reads every legacy registry through its adapter in
`kb.adapters`, in two passes: each adapter declares its symbols, names, keys,
and statuses, and then relates them, so that a link target resolves against
the symbols of every registry. Symbols of one registry key join one meaning;
the meaning takes the semantic name of the highest precedence that a registry
gives it, and otherwise the generated name of its symbol on its home layout.

| Adapter | Registry | Symbols |
|---|---|---|
| `curated` | `tools/ghidra/symbols/<layout>.csv` | `fn` symbols with curated names |
| `ledgers` | `defs/JK08A.{funcs,vars,findings,axes,dtc,diagnostic-bindings}.csv` | `7mfk` symbols with their keys, links, and evidence |

Evidence tokens map by the table of section 20.7 of the specification: a
dependency token becomes a link stored at the end its type names or `trace`
evidence, and a token target without a registry row becomes an implicit
symbol of the kind its role and address admit.

## Graph

`kb sync` loads the model into the Memgraph instance of the working tree.
Every node it writes carries the label `Kb`, and it deletes and replaces only
`Kb` elements, so the graph of the loaders of `tools/memgraph/` stays intact.

| Part | Elements | Reloads when |
|---|---|---|
| L0 of a layout | `Function`, `Location`, `CALL`, and `ACCESS` with producer `l0` or `derived` | the digest of its L0 files, its images, or the modules `compile`, `derive`, `graph`, and `sh2` changes |
| Claims | `Family`, `Layout`, `Image`, `Meaning`, `Symbol`, `HAS`, the link types between meanings and between symbols, `STATUS`, and `CITES` | the fingerprint changes |
| Joins | `AT` from symbols to the L0 nodes at their addresses, and `verified` on the `WRITER` and `READER` links of symbols | either part reloads |

- `ACCESS` with producer `l0` comes from `function_references.csv`: every
  reference to RAM or a register with its reference type as mode, every data
  or parameter reference to ROM, and every pool literal that names RAM or a
  register, with mode `literal`. `ACCESS` with producer `derived` comes from
  literal pairing, with modes `load`, `store`, and `update`. One `ACCESS` per
  producer joins a function and a location, and its `sites` list holds one
  map per instruction.
- A writer link of a symbol is verified by a store access of the function to
  the symbol's location, and a reader link by any access. A block copy loads
  only the destination address, so its writer stays unverified until
  `indirect` evidence explains it.
- The fingerprint covers every input: the model inputs, `l0/`, and the images
  of the catalog. `.kb/cache/hashes.json` keeps the git blob hash of each file
  by size and modification time. `:Meta` is deleted first and written last.
- The main working tree uses the compose service of
  [`../memgraph/`](../memgraph/README.md). `kb instance up` in a linked
  working tree starts a container from the compose image with its data in
  `.kb/memgraph/` and a loopback port from `[instances] ports`, and records
  it in `.kb/instance.toml`; `prune`, which `up` runs first, removes the
  containers of vanished working trees and stops idle ones. `KB_BOLT`
  overrides the Bolt address for tests against a scratch server.

## Modules

| Module | Role |
|---|---|
| `kb.repo` | Repository paths, the image catalog, the layouts, and the configuration |
| `kb.vocab` | Kinds, levels, link types, evidence kinds, and the other vocabularies |
| `kb.tokens` | Legacy evidence tokens and their evidence items |
| `kb.model` | Symbols, meanings, links, and the builder that joins them |
| `kb.adapters` | Adapters of the legacy registries |
| `kb.names` | `kb/names.csv`, the domain dictionary, and generated names |
| `kb.compile` | The compiler from the tracked inputs to the model |
| `kb.checks` | The model checks and the audit |
| `kb.fingerprint` | Input paths, git blob hashes, and the fingerprint |
| `kb.lock` | `.kb/lock` |
| `kb.instance` | Graph instances by working tree |
| `kb.graph` | Graph rows, loading, `:Meta`, and read-only queries |
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

`config.toml` lists the L0 export scripts, the census plan of each layout, the
instance limits and ports, the lock timeout, the output budgets of the
commands, the address spaces of each MCU, the manual prefixes of legacy
`spec:` tokens, the axis quantities, and the attempt limit of generated names. `domain-words.txt` lists the words a generated name must
not contain, beside the words of semantic names, signal labels, and editor
table names. `.kb/` holds the per-worktree state and is
ignored by git.

## Tests

```bash
uv run pytest -q tools/kb/tests
KB_TEST_BOLT=bolt://localhost:<port> uv run pytest -q tools/kb/tests/test_graph.py
```

The second form also loads the whole model, in about a minute, into the
scratch server that `KB_TEST_BOLT` names and that the test clears.
