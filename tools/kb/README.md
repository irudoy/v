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
uv run kb at jk00d:ffff1034          # the symbol at an address, or the allocation or datum that holds it, and its L0 facts
uv run kb show 7mfk:0000a4aa         # identity, keys, block and chain steps, feature roles, layouts, links, L0 accessors, notes, evidence
uv run kb where hcan1_init           # the symbol or status of a meaning on every layout
uv run kb impact 7mfk:0000a4aa       # what a change reaches, with the insertion points
uv run kb path 7mfk:ffff1079 7mfk:ffff2326   # shortest typed paths between two entities
uv run kb find knock threshold       # meanings and designed entities ranked by name, former name, title, and summary
uv run kb brief                      # graph state, layouts, stage, owners, gaps, and the questions
uv run kb gaps --feature can_telemetry --layout 1nd   # required meanings without a symbol, by status
uv run kb log <ref>                  # renames and generated names of an entity
uv run kb raw <ref>                  # the registry rows that state an entity
uv run kb bench                      # the acceptance questions of the current stage
uv run kb mcp                        # the read commands as MCP tools on stdio
uv run kb project                    # render the projections that kb generates, such as AGENTS.md#kb
uv run kb fmt                        # rewrite the entity files of kb/ in canonical form
```

- `kb check` runs the active checks, which `make check` includes: `l0`; the
  model checks `schema`, `canonical`, `names`, `references`, `symbols`, and
  `links` over the entity files and the compiled registries; and
  `projections` and `guard`
  ([Projections and the access guard](#projections-and-the-access-guard)).
- `kb fmt` rewrites the entity files of `kb/`, or those it names, in the
  canonical form of section 4.2 of the specification under `.kb/lock`; the
  `canonical` check requires every file to equal the canonical rendering of
  its parse.
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
- `kb audit` prints four sections: `disagreements`, where two registries
  state different values of one fact; `names`, the registry names of a meaning
  that lose to a name of higher precedence; `untyped`, legacy evidence tokens
  that lack the keys of their evidence kind, under the registry that states
  each; and `unsplit`, the scales of
  telemetry fields that the adapter cannot split into the keys of their
  source meanings.
- `kb code` resolves an address to the function whose L0 body holds it and
  calls `tools/ghidra/decompile.sh` for that function's layout image. The
  decompilations and listings stay in the local export directory as the cache
  of `kb code`; `-f` reruns Ghidra. An answer longer than its budget in
  `config.toml` starts with a `TRUNCATED:` line; `--budget` and `--full`
  change the budget.
- `kb mcp` serves each read command as the MCP tool `kb_<command>` over
  newline-delimited JSON-RPC on standard input and output. A tool takes the
  arguments of its command under their option names (`no_sync` for
  `--no-sync`) and returns the output of the command with the same budget; a
  nonzero exit code gives an error result that starts with `exit <code>`.
  Child processes write to the standard error. The local `.mcp.json` of a
  working tree registers the server:

  ```json
  "kb": {"type": "stdio", "command": "uv", "args": ["run", "kb", "mcp"]}
  ```

- Exit codes follow the specification: 1 for failed checks, 2 for usage
  errors, 4 for an ambiguous reference, 5 for an unknown layout, address, or
  entity, 6 for a failed Ghidra run or an unavailable or stale graph, and 7
  for a lock timeout.

## Read commands

The read commands resolve references against the graph of the working tree
after the fingerprint check and sync a stale graph first unless `--no-sync`
is given. A reference is a full reference `<name>/<kind>/<layout>-<address>`,
`<layout>:<address>`, `<name>/<kind>/<layout>` or `<name>/<layout>`,
`<name>/<kind>` or `<name>`, a former name, or a bare address with
`--layout`, in that order of precedence. A stale full reference or a former
name resolves with a note that names the current reference.

- Output states full references, one fact per line; an element that is not a
  claim carries its producer, `[l0]` or `[derived]`. `--json` prints the
  structured answer without a budget.
- An answer longer than its budget in `config.toml` loses its lowest-priority
  sections first, evidence before details, links, facts, and identity, and
  starts with a `TRUNCATED:` line that names the option or narrower command
  that shows the rest. `--budget` and `--full` change the budget.
- `kb impact` closes transitively over the links between data and lists the
  functions that read the reference or a datum of the closure without
  expanding them; a function reference starts at the data it writes.
  `kb path` searches dataflow through data and through the functions that
  read, write, and call, then the reverse direction, then any direction.
  Both leave nodes above the 99th degree percentile of their kind unexpanded
  and name the `--expand` option; `kb path` states a shorter path through
  hubs when one exists.
- `kb gaps` lists the required meanings without a symbol on a layout, grouped
  by status: `unknown`, `unresolved` with its search and `stale` when the L0
  manifest of the layout changed since, and `absent` with its first typed
  evidence. A meaning is required on the layouts that a feature targets when
  the feature requires it directly or through the `source` of a field it
  requires, and on the layouts of a family where another layout has its
  symbol; `--feature` lists the requirements of one feature, `--layout` one
  layout.
- `kb bench` answers every question of `bench.toml` that the current stage
  activates, with `--full`, and passes a question when its answer exits with
  0, fits its budget, and stays below its baseline: the output of the `rg`
  and file reads that answer the question over the registries. `--all` also
  runs the questions of later stages, and `--only <id>` runs one.
  `tools/single_source.py` compares the questions, budgets, and stages of
  `bench.toml` with the table of section 18 of the specification.

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

The compiler reads the entity files of `kb/` and every legacy registry
through its adapter in `kb.adapters`, in two passes: each adapter declares its
symbols, names, keys, and statuses, and then relates them, so that a link
target resolves against the symbols of every registry. Symbols of one meaning
file or one registry key join one meaning; the meaning takes the name of its
file, or else the semantic name of the highest precedence that a registry
gives it, and otherwise the generated name of its symbol on its home layout.
A file states references as text, which resolve once the meanings are named;
a reference that names nothing fails the `references` check.

| Adapter | Registry | Symbols |
|---|---|---|
| `files` | `kb/<kind>/<name>.toml` | The meanings of the converted registries with their symbols, statuses, links, and evidence; the targets of the features |
| `curated` | `tools/ghidra/symbols/<layout>.csv` | `fn` symbols with curated names |
| `ledgers` | `defs/JK08A.{funcs,vars,findings,axes,dtc,diagnostic-bindings}.csv` | `7mfk` symbols with their keys, links, and evidence |
| `profiles` | `patches/rom-address-profiles.toml`, `patches/*-runtime-correspondence.csv`, `patches/runtime_targets.py`, and the canonical feature layouts | Target symbols, hook words, DIDs, and telemetry sources with their statuses; the feature targets with the roles that a symbol of another meaning fills on a layout |
| `definitions` | `defs/definition-projections.toml`, `defs/JK08A-*.definition-addresses.csv` | `tbl` and `axis` symbols of the definition projections; the `definitions` target |
| `interp` | `defs/*.interp.csv`, `defs/JK08A-*.interp-correspondence.csv` | `fn` symbols of kernels and wrappers with `[interp]` |
| `native` | `defs/vq37-native-tables.toml`, `defs/vq37-native-fuel-cut.toml` | `tbl`, `axis`, `fn`, and `ram` symbols of the native tables and the fuel-cut mechanism of the VQ37VHR layouts |
| `dids` | `tools/diagnostics/sid22_inventory.py` over the JK08A image | `did` symbols of the `7mfk` service 0x22 table with `source` links to the data they return |
| `signals` | `defs/JK08A.tuning-signals.toml` | `signal` entities that observe `7mfk` meanings or feature allocations, the widths of those meanings, and the catalog keys of `can_telemetry` |
| `telemetry` | `patches/can-telemetry-profile.toml`, `patches/can-telemetry-layout.toml`, `patches/jk08a-runtime-reservations.toml` | `field` entities that carry `7mfk` meanings with their scales and units or name feature allocations; the wire keys of `can_telemetry` and the addresses of its `7mfk` target |
| `overrides` | `defs/JK08A.overrides.toml`, `tools/mapkit/definition_projections.py` | `[editor]` of `7mfk` tables and axes with their masked views, `[logparam]` of `7mfk` RAM; the presentation keys and switches of `definitions` and the JK08A entry of its `7mfk` target |
| `architecture` | `defs/JK08A.architecture.toml` | `stage`, `block`, `endpoint`, and `chain` entities with the chain steps; the `block` key of the `7mfk` functions and signals of each block |

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
| L0 of a layout | `Function`, `Location`, `CALL`, and `ACCESS` with producer `l0` or `derived` | the digest of its L0 files, its images, the address spaces of its MCU, or the modules `derive`, `l0graph`, `sh2`, and `values` changes |
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
- The fingerprint covers every input: the model inputs, the compiler
  modules, `l0/`, and the images of the catalog. The modules of the command
  line, the read commands, the MCP server, the checks, the projections, the
  guard, and the instances, which `compile.NOT_COMPILER` lists, are no
  inputs. `.kb/cache/hashes.json` keeps the git blob hash of each file
  by size and modification time. `:Meta` is deleted first and written last.
- The main working tree uses the compose service of
  [`../memgraph/`](../memgraph/README.md). `kb instance up` in a linked
  working tree starts a container from the compose image with its data in
  `.kb/memgraph/` and a loopback port from `[instances] ports`, and records
  it in `.kb/instance.toml`; `prune`, which `up` runs first, removes the
  containers of vanished working trees and stops idle ones. `KB_BOLT`
  overrides the Bolt address for tests against a scratch server.

## Projections and the access guard

`projections.toml` registers every generated file of the repository with its
generator, inputs, consumers, stage, and read mode, as section 14 of the
specification states. `uv run kb project` renders the projections of `kb`
functions, such as the `AGENTS.md#kb` section; a projection of another
generator keeps that generator and its gate. The `projections` check requires
every entry to match tracked files that no other entry claims and to name
existing paths, compares each projection of `kb` with its rendering, and
requires every tracked file whose first lines declare it generated to be
registered.

`hook.py` is the access guard of section 15. The tracked
`.claude/settings.json` runs it before `Read`, `Edit`, `Write`, `MultiEdit`,
`NotebookEdit`, `Grep`, `Glob`, and `Bash` with the Python of `.venv`, or
`python3` without it. It refuses reads, searches, and edits of `kb/` and
`l0/`, edits of the projections that apply, and reads of the guarded ones,
and names the command that answers instead. A shell command passes when it
changes the directory or runs `kb`, a git subcommand of the allow list,
`make`, or a script under `tools/` or `patches/`. `KB_GUARD=off` in the
environment of the session disables the guard for maintenance. The `guard`
check requires the settings to be tracked and to cover every tool, `.ignore`
to list the guarded paths, and the hook to refuse a sample call on each.

## Modules

| Module | Role |
|---|---|
| `kb.repo` | Repository paths, the image catalog, the layouts, and the configuration |
| `kb.vocab` | Kinds, levels, link types, evidence kinds, and the other vocabularies |
| `kb.tokens` | Legacy evidence tokens and their evidence items |
| `kb.model` | Symbols, meanings, links, and the builder that joins them |
| `kb.store` | Entity files of `kb/`, their canonical rendering, and `kb fmt` |
| `kb.adapters` | Adapters of the entity files and of the legacy registries |
| `kb.names` | `kb/names.csv`, the domain dictionary, and generated names |
| `kb.compile` | The compiler from the tracked inputs to the model |
| `kb.checks` | The model checks and the audit |
| `kb.fingerprint` | Input paths, git blob hashes, and the fingerprint |
| `kb.lock` | `.kb/lock` |
| `kb.instance` | Graph instances by working tree |
| `kb.graph` | Claim rows, loading, `:Meta`, and read-only queries |
| `kb.l0graph` | Graph rows of the L0 part of a layout |
| `kb.values` | Property values the graph stores |
| `kb.refs` | References of the read commands and their resolution |
| `kb.answer` | Answers, sections, token counts, and budgets |
| `kb.read` | The read commands |
| `kb.mcp` | The read commands as MCP tools over JSON-RPC on standard input and output |
| `kb.spec` | The stages, owners, and acceptance questions of the specification |
| `kb.project` | `projections.toml`, `kb project`, the `projections` check, and the `AGENTS.md#kb` section |
| `kb.guard` | The `guard` check of the settings, `.ignore`, and the hook |
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

`bench.toml` holds the acceptance questions with their commands, budgets,
stages, and baselines, and the current stage.
`config.toml` lists the L0 export scripts, the census plan of each layout, the
instance limits and ports, the lock timeout, the output budgets of the
commands, the address spaces of each MCU, the manual prefixes of legacy
`spec:` tokens, the axis quantities, the attempt limit of generated names,
and the trees and git allow list of the access guard. `projections.toml`
registers the generated files. `domain-words.txt` lists the words a generated name must
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
