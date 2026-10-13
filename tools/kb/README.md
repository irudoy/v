# kb

`kb` is the entry point of the knowledge model that
[`SPEC.md`](SPEC.md) specifies. The package implements the specification
stage by stage; this document describes the commands and modules that exist.

## Commands

`uv run python tools/check_projection_contract.py` validates the read-only
argument array declared for every command producer in `projections.toml`.
`--run` executes the native projection check and every declared command check,
then verifies that the compiler fingerprint is unchanged before publishing
their output. It requires all source inputs before starting any checker.
`VQ_OBD2TOOLS_SOURCE` supplies the original checkout at the importer's exact
commit; an absent checkout blocks the complete run. `make check` validates
these declarations and executes the comparisons with available tracked source
packs. Its success does not establish reproduction of the missing obd2tools
source pack.

`kb gaps --catalog` lists both project features and the complete competitor
inventory, with acceptance criteria, per-layout status and unresolved ECU
requirements. Catalog provenance does not establish an ECU implementation.
`kb suggest <ref> --layout <layout>` reports the existing function-signature
and instruction-alignment channels without binding or raising claim levels.

`kb family new` and `kb family add` require a registered stock image, a
source-target census report, matching exported L0 and the stock family gates.
The family writer preserves unrelated facts and comments in the primary
homology source. A distinct family has its own layout and meanings.

`kb retire <ref> --dry-run` checks the incoming consumers of a whole owned
meaning or designed entity. Retirement retains the complete canonical
document and all names, and contributes only an inactive name index.

The consolidated transition uses `uv run python -m kb.transition prepare
--source-commit <commit> --output tmp/<plan>.json` to construct one in-memory
overlay and check preservation and model gates. Its plan binds exact source
bytes, the compiler fingerprint and the source commit. `uv run python -m
kb.transition apply tmp/<plan>.json` checks the exact prepared payload, repeats
source, existing-fact preservation and model gates, and writes the complete
primary overlay; graph synchronization and final project
gates follow the source write. Executable, semantic and hardware review debts
remain independent of this representation transfer.

`owners.toml` declares the remaining name owners and exact unresolved code
and source-binding reviews. Its strict schema permits only these declarations;
it cannot override export, census, MCU, or matcher settings in `config.toml`.
The compiler fingerprints both sources. Separating these owners keeps the
accepted L0 producer contract independent of its review inventory.

Configuration readers select and read current execution settings and owner
declarations on every call. They reuse only immutable serialization of a
successful TOML parse of exact source text, with a 64 MiB content budget.
Every call returns separate documents and validates the owner schema.
Syntax errors are not retained, and a supplied parser executes directly.
The test-local source preparation also scopes configuration reads by root
and effective adapter order; original compilers and checks execute.
Each scope parses its own first request. Equal text and serialized values
share immutable retained storage; every hit returns a separate document.
Scoped references and contents consume one bounded preparation budget.

Native TOML documents use the runtime's in-memory marshal encoding. Dates
and supplied parsers retain pickle encoding, including aliases and cycles.
Both encodings return separate mutable containers and retain float bits.
Injection fixture checks compare the complete image before asserting the
Boolean result. Expected corruption refusals retain a bounded explanation
under ordinary and verbose pytest output.

Canonical rendering prepares a bounded set of known-key schema traversals.
Current values, inferred fields, nested specifications, and schema changes
are inspected on every render. Custom schemas and changed methods retain
their direct lookups. The renderer retains no document or check result.
Built-in empty values use their direct container or scalar behavior, and
wrapped strings accumulate their current line width. Comparable model values
return exact immutable atoms directly; subclasses retain their general path.
Private root schemas and string wrapping programs have bounded retention.
Current grammar identities, classifiers, escaping and line widths select the
rendering path; mutable declarations and changed callbacks execute directly.
Public schemas remain independent of the renderer's private preparation.

Test-definition evidence reads the current UTF-8 file bytes on each request.
Successful preparation with the standard AST readers reuses only immutable
function names for the exact filename and bytes. Supplied AST readers execute
directly without hashing or retaining their callables or results. Retention
has an entry bound and a source-byte bound; larger files execute parsing
directly. Syntax
and decoding errors are not cached. Removed definitions are refused without
a cache reset, while nested, method and async definitions retain their AST
scope. This checks definition existence without executing the function; it
does not establish a collected passing test or execution grounding.

The registered 1ME3B image-scan TEST witness additionally requires a local
qualified execution receipt to award code grounding. Its scope covers aligned
pointer values in occupied bytes and direct PC-relative branches to the region
entry. Interior control flow and private lookup-literal preservation remain
unverified. Unregistered TEST items retain their legacy, unqualified behavior.
Definition inspection and model construction do not require a receipt.

Ordinary pytest hooks optionally write a candidate through
`--kb-test-candidate=<path>` for the exact registered case. The candidate binds
actual collection, parameters and terminal phases, the explicit supported
facts, the captured profile preparation, consumed image bytes, current source
inputs and portable public model values. A candidate is not a completed
execution receipt. The bounded runner's actual process exit and stream hashes
are supplied to `uv run python -m kb.test_evidence <candidate> --process
<process.json> --stdout <stdout> --stderr <stderr>` after the process finishes.
The finalizer validates the candidate's terminal-output hash before atomically
publishing `.kb/test-receipts/1me3b-image-scan.json`. A failed invocation retains
an earlier qualified record. Receipt and terminal bytes, source inputs, model
values and exact identity-claim scope are checked again on reuse in both
grounding paths; mismatches supply no CODE. The producer and independent
finalizer bind the complete native model. An unrelated writer overlay retains
grounding only while the supported meaning, symbols, evidence, relationships,
geometry and execution settings agree with that record. Overlays of execution
inputs refuse reuse. Knowledge ownership and unrelated review records remain
independent of the image-scan identity. The same scope applies after a writer
saves its result and the compiler rebuilds it without an overlay. Exact profile,
layout, telemetry, family, catalog, ROM, program and identity-owner inputs govern
reuse. The full producer input manifest remains independent finalized provenance.
Checking does not execute the case.

The Python conversion API provides `convert.planning(root)` for a read-only
group under the writer lock. Empty overlays share one native compilation and
its model checks within that group. Each registry keeps its own before model,
conversion, exact fact comparison, refusal comparison, and projection checks.
Nonempty overlays compile independently. Source changes, changed default
adapter order, and mutation of the shared model refuse the group; no result
or check pass is retained by the context after exit. Its model digest uses
an iterative traversal of values and shared references, including cycles.
The digest streams the same length-prefixed protocol-5 records through a
bounded byte buffer; large records pass directly to the hasher. Its accepted
packet hashes and current-state mutation contracts are gated.
Independent model construction, complete model digests and writer model checks
pause automatic collection for one synchronous allocation phase. Each phase
restores the caller's collection mode on success and failure, including nested
calls. A shared reentrant lock serializes these phases across threads before
reading the caller's mode. Collection thresholds and the caller's frozen
generation stay fixed;
ordinary collection can release temporary model cycles after the phase.
These phases retain no model or check result beyond their existing owners.
Ledger evidence requests the current manual prefixes only when its recognizer
iterates them. Registry, trace, hardware and arithmetic terminals retain their
own recognition paths without reading unused prefixes.

```bash
uv run kb sync                       # compile, draw names of new symbols, load the graph
uv run kb sync --full                # reload every element of the graph
uv run kb instance up                # start the graph instance of this working tree
uv run kb instance status            # instances of the repository and their state
uv run kb guard off --session <id>   # disable only this project's root session guard
uv run kb guard on --session <id>    # enable only this project's root session guard
uv run kb guard status --session <id> --json   # the saved override, without querying the graph
uv run kb cypher "MATCH (m:Meaning {name: \$n}) RETURN m" --param n=hcan1_init
uv run kb check                      # every active check; exit 1 on a failure
uv run kb check --only l0            # one check
uv run kb check --changed            # the checks whose inputs differ from those of their last pass
uv run kb audit                      # disagreements between registries and the levels of claims
uv run kb audit --section levels     # one section, which the audit alone computes
uv run kb audit --section research   # source-bound unresolved semantic statements
uv run kb prepare-research <source-commit> --output tmp/transfer.toml
uv run kb code 7mfk:00026742         # decompilation of the function whose body holds the address
uv run kb code 7mfk:00026740 -l      # decompilation and listing
uv run kb code hcan1_init --layout 1nd   # decompilation of a function symbol, or of the symbol of a meaning
uv run kb at jk00d:ffff1034          # the symbol at an address, or the allocation or datum that holds it, and its L0 facts
uv run kb show 7mfk:0000a4aa         # identity, keys, block and chain steps, feature roles, layouts, links, L0 accessors, notes, evidence
uv run kb where hcan1_init           # the symbol or status of a meaning on every layout
uv run kb impact 7mfk:0000a4aa       # what a change reaches, with the insertion points
uv run kb impact normalized_load_raw/field   # the features that require a field and its source on every layout
uv run kb path 7mfk:ffff1079 7mfk:ffff2326   # shortest typed paths between two entities
uv run kb find knock threshold       # meanings and designed entities ranked by name, former name, title, and summary
uv run kb brief                      # graph state, layouts, stage, owners, legacy names, gaps, and the questions
uv run kb gaps --feature can_telemetry --layout 1nd   # required meanings without a symbol, by status
uv run kb log <ref>                  # former references and recorded profile address corrections
uv run kb raw <ref>                  # the file of an entity and the registry rows that state it
uv run kb suggest --blocks --layout jk78c   # MAGE communities propose blocks for unplaced functions
uv run kb bench                      # the acceptance questions of the current stage
uv run kb mcp                        # the read commands and kb_apply as MCP tools on stdio
uv run kb project                    # render the projections that kb generates, such as AGENTS.md#kb
uv run kb project --check            # exit 1 when a projection differs from its rendering
uv run kb fmt                        # rewrite the entity files of kb/ in canonical form
uv run kb new <kind> <layout>:<address> --evidence '<item>' --dry-run   # a meaning with the symbol at a location
uv run kb new feature <slug> --dry-run   # a designed entity
uv run kb bind <meaning> <layout>:<address> --dry-run   # a symbol of a meaning on another layout
uv run kb absent <meaning> --layout <l> --evidence '<item>'   # the mechanism does not exist on a layout
uv run kb unresolved <meaning> --layout <l>   # the search that finds no unique symbol
uv run kb link <from> <type> <to> [<key>=<value>...] --dry-run   # a typed link with its keys and evidence
uv run kb set-link <from> <type> <to> <key>=<value>... --dry-run
                                              # replace properties of one existing native link
uv run kb unlink <from> <type> <to> --dry-run   # a link of the file of a meaning
uv run kb select <meaning> <registry> <order> <key>=<value>... --dry-run
                                              # select an existing native relation in an owned ledger row
uv run kb merge <meaning> <other> --dry-run   # two meanings, or two files of one meaning, as one
uv run kb rename <meaning> <semantic-name> --dry-run   # the semantic name of a meaning
uv run kb set <ref> <key>=<value> --dry-run   # keys of a meaning, a symbol, a designed entity, or a feature target
uv run kb move <symbol> <layout>:<address> --dry-run   # the address of a symbol on its layout
uv run kb move <symbol> <meaning> --dry-run   # a symbol into the meaning that it belongs to
uv run kb move <generated>/fn/<layout>-<old> <layout>:<new> --legacy-reservation --dry-run
                                              # preserve a generated name after a reviewed legacy/L0 repair
uv run kb apply <batch.toml>         # a batch of write operations as one change
```

- `kb check` runs the active checks, which `make check` includes: `l0`;
  `sites` over the function ledgers ([L0](#l0)); the
  model checks `schema`, `canonical`, `names`, `references`, `symbols`,
  `links`, `widths`, `fields`, `ledgers`, `blocks`, and `chains` over the entity files and the compiled
  registries; the matcher
  checks `homology`, `image-bytes`, `statuses`, and `writers`, and the
  claim check `levels`
  ([Matchers](#matchers)); and `projections` and `guard`
  ([Projections and the access guard](#projections-and-the-access-guard)).
  A check may print notes, lines marked `note:` that do not fail it.
  The schema checks RAM and register access widths in bits for meanings and
  per-layout symbol overrides before writes. Field widths keep their byte
  contract. The `code` check compares declared RAM and register widths with
  normalized L0 accesses and retains exact source-bound unresolved differences.
  The `source-bindings` check verifies complete typed-anchor coverage of the
  VVEL and CAN specifications against their exact bytes and declared layouts.
  `--changed` runs the checks whose inputs differ from those of their last
  pass: the files a check reads and the source and configuration of `kb`.
  `.kb/cache/checks.json` records the digest of the inputs of each check at
  its last pass and the files beyond its stated inputs that it read, the
  Python files of `test` evidence.
  The `ledgers` check also runs before a write: an evidence replacement cannot
  leave an invalid view index, and `kb unlink` withdraws the removed relation's
  selected dependency tokens at both claiming ends.
  `kb select` restores a dependency selector for one existing native relation
  and claim in the exact owned ledger `registry` and `order`. The row must
  exist before the batch. Required dependency keys are `role`, `to`, `type`,
  `end`, `relies`, and `supports`; optional keys are `link_role`, `offset`,
  and `offset_text`. It does not change links, evidence, properties, or other
  selectors. A symbol reference names its meaning; the selected row belongs
  to that meaning's `7mfk` symbol. Missing or ambiguous rows and relations,
  mismatched directions
  or claims, and incompatible duplicate selectors are refused. One exact
  repeated selector writes nothing. The final batch must retain the selected
  claim, its row, and its native relation.
  The selected claim must have a corresponding evidence column in the
  registry; `curated` and `diagnostic-bindings` do not project dependency
  selectors and are refused.
  `blocks` verifies declared stages, placements of reviewed home functions,
  and typed endpoint members. Architecture entities require the metadata of
  their generated view, positive order values, and repository-local named
  specification files. `chains` verifies symbols on the home layout,
  ordered function paths, effects, signs, a destination output, unique step
  pairs, acyclic flow, and arithmetic notes. `kb audit --section chain-notes`
  checks arithmetic against `[chains.arithmetic]` of `config.toml`; writes
  refuse a new rejected note or a change to its exact text or step binding
  (ends, ordered calls, effect, or sign). The mandatory `chains` gate enforces
  that grammar. A step can retain unresolved semantics in a separate research
  record bound to every original field and immutable source bytes. Generic
  batch replacement cannot drop or change that record. The research audit and
  brief report this separate semantic queue; transfer supplies no proof or
  typed condition and changes no layout search status or claim level.
- `kb prepare-research <source-commit> --output tmp/transfer.toml` prepares one
  primary writer batch for the unresolved prose in all chains. It checks the
  complete original source document, preserves every ordered step field and
  keeps valid arithmetic unchanged. The command writes only a new preparation
  artifact under `tmp/` or `.kb/`; applying it uses the ordinary atomic writer
  gate. A repeated transfer changes no record. The final package gate checks
  original reconstruction and reports unresolved semantics separately.
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
- `kb audit` prints `disagreements`, where two registries
  state different values of one fact; `names`, the registry names of a meaning
  that lose to a name of higher precedence; `untyped`, legacy evidence tokens
  that lack the keys of their evidence kind, under the registry that states
  each; and `levels`, also a mandatory model gate from stage 5,
  the claims above their effective level with the dependency that bounds
  each and the end of its chain, the `candidate` claims without evidence,
  the `code` and `silicon` claims without grounding, the `hardware` keys
  without a passing record, and the `arithmetic` equations that do not hold
  (SPEC, section 7.1); and `chain-notes`, notes outside the configured
  arithmetic grammar, with their exact text and parse failure.
  `--section` computes only the named sections. Write commands compare
  `disagreements` and `chain-notes` with the working tree as well as the
  mandatory model checks. An audit report does not change claim levels.
- `kb code` shows the function whose L0 body holds a location
  `<layout>:<address>`, the function symbol that a reference names, or the
  symbol of a meaning on `--layout` or else on its home layout, and calls
  `tools/ghidra/decompile.sh` for that function's layout image. The
  decompilations and listings stay in the local export directory as the cache
  of `kb code`; `-f` reruns Ghidra. An answer longer than its budget in
  `config.toml` starts with a `TRUNCATED:` line; `--budget` and `--full`
  change the budget.
- `kb mcp` serves each read command as the MCP tool `kb_<command>`, and
  `kb apply` as `kb_apply`, over newline-delimited JSON-RPC on standard input
  and output. A tool takes the
  arguments of its command under their option names (`no_sync` for
  `--no-sync`) and returns the output of the command with the same budget; a
  nonzero exit code gives an error result that starts with `exit <code>`.
  Child processes write to the standard error. The local `.mcp.json` of a
  working tree registers the server:

  ```json
  "kb": {"type": "stdio", "command": "uv", "args": ["run", "kb", "mcp"]}
  ```

- `kb move --legacy-reservation` preserves one generated function name after
  the legacy registries and L0 have accepted a registered seed/fragment entry
  repair. It requires the old full generated reference and a destination on
  the same layout, an explicit non-implicit legacy function at the new entry,
  the registered preparation and merge, cited sites owned by that entry,
  no old legacy symbol, and no occupied destination reservation.
  It compiles and plans under the primary writer lock before any graph sync,
  so sync cannot draw another name at the repaired address. It changes only
  the reservation key, preserves its name and former names, does not adopt a
  symbol into an entity file, and refuses changed symbol/meaning facts or new
  model issues. `--dry-run` writes no sources and does not sync the graph.
  Legacy-source correction, L0 acceptance, the reservation write, and graph
  loading are distinct operations, not one filesystem/graph transaction.
- Exit codes follow the specification: 1 for failed checks, 2 for usage
  errors, 3 for a refused write, 4 for an ambiguous reference, 5 for an
  unknown layout, address, or entity, 6 for a failed Ghidra run or an
  unavailable or stale graph, and 7 for a lock timeout.

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
  expanding them; a function reference starts at the data it writes. The
  fields that carry a datum of the closure and the features that require
  them follow. The insertion points of a meaning state every layout, with
  its status where it has no symbol; those of a field are its source on
  every layout that a requiring feature targets, and those of a feature are
  its target status, runtime spans, and hook sites on every layout.
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
  requires, on the layout of a target that names it in its key tables,
  roles, hooks, or `requires`, as the `definitions` targets list the tables
  and axes of their definitions, and
  on the layouts of a family where another layout has its symbol;
  `--feature` lists the requirements of one feature, `--layout` one layout.
- `kb brief` uses the same required binding rows as `kb gaps`, with complete
  totals by feature, layout, and state. Its priority sample ranks a missing
  binding by the number of affected project features, then required fields,
  then link degree; family-only requirements follow project requirements.
  The sample does not reduce the totals or the complete `gaps` JSON array.
- `kb log` reads full former references from the owning symbol entries,
  including entries of every symbol of a meaning. It also lists address
  corrections of the profile keys that current feature targets associate
  with that meaning, from the first-parent Git history of
  `patches/rom-address-profiles.toml`. Each correction retains its commit,
  layout, table, key, and both addresses. Inherited copies and changes between
  numeric and hexadecimal string representations share one address.
  History entries are previous declarations; `kb show` states current facts
  and their evidence.
- `kb show` and `kb where` show analog hints in either direction with their
  required similarities-and-differences note. An analog names a meaning,
  including one without a symbol, without joining symbols, inheriting levels,
  or entering dataflow, homology, or claim dependencies. The atlas reads the
  same `ANALOG` relations.
- `kb bench` answers every question of `bench.toml` that the current stage
  activates, with `--full`, and passes a question when its answer exits with
  0, matches every `expect` pattern, fits its budget, and stays below its
  baseline: the output of the `rg` and file reads that answer the question
  over the registries. Patterns use multiline regular expressions and
  require nonempty content. Invalid or missing contracts, unknown question
  ids, and selections with no active question are usage errors. `--all`
  includes later stages, including with `--only <id>`.
  `tools/single_source.py` compares the questions, budgets, and stages of
  `bench.toml` with the table of section 18 of the specification and validates
  every content contract, including those of later stages. Patterns gate
  required content; model and executable gates verify the stated facts.

For an ECU source meaning with no engineering scale, enumeration, or named
bits, the telemetry projection emits `raw count` as a host storage view.
It leaves the meaning's unit, conversion, level, and evidence unasserted.
Partial or unrenderable engineering conversions still refuse projection.

## Write commands

`kb new`, `kb set`, `kb bind`, `kb absent`, `kb unresolved`, `kb link`,
`kb set-link`, `kb unlink`, `kb select`, `kb merge`, `kb rename`, and `kb move` write one operation, and
`kb apply` the operations of a TOML file of `[[op]]` tables, as one change
under `.kb/lock` (section 12.3 of the specification). A change resolves its
references on a current graph, edits the entity files in memory, and compiles
the model with them in place of the files on disk (`compile.build` with an
overlay). When the result has an issue of a model check or a registry
disagreement that the working tree lacks, or contradicts what an operation
expects of it, the change is refused with exit code 3 and the issues, and
nothing is written; otherwise the files are written through temporary files
and renames, and the graph loads the compiled result. `--dry-run` prints the
diff instead of writing; the write draws the generated names of the diff
anew. A batch renames a meaning after its other operations: an operation on a
meaning that an earlier operation renames is refused. `set` also names a
designed entity that an earlier `new` of the batch starts, so a batch starts
a field or a chain with its keys, whose empty file fails the checks.

- The file of a meaning without one starts with the entry of the home symbol,
  so that the file joins the meaning that the registries state. The row of
  `kb/names.csv` of that symbol moves into its entry: the generated name of a
  symbol of an unnamed meaning becomes its `name`, and the other names become
  `former` references.
- `kb new <kind> <layout>:<address> --evidence <item>` starts the file of a
  meaning with the symbol at a location that holds no symbol of a meaning and
  the evidence of its identity on its layout, which makes it an anchor, named
  by `--name` or else by the generated name of the row of the symbol or a
  drawn one. `kb new <kind> <slug>` starts the empty file of a designed entity
  of a kind that the store holds.
- `kb set <ref> <key>=<value>...` writes keys of a meaning, of the entry of
  the symbol that the reference or `--layout` names, of a designed entity, or
  of the target of a feature on `--layout`. A value is a TOML value or else a
  string, an empty value unsets the key, and a dotted key names a key of a
  table; a table joins the held one key by key, and an array of tables such
  as `[[bit]]` replaces it. A batch states the keys as `[op.keys]` and the
  removed ones as `unset`. The keys that other commands own, such as the
  symbols, statuses, links, analogs, and former names of a meaning and the
  layout, address, and names of a symbol entry, are refused. A feature takes
  every key besides its targets, as the wire constants and `profiles` of
  `can_telemetry`. Another designed entity takes every key of its schema,
  including the `step` array of a chain. Setting that array replaces all
  held steps in the stated order and preserves repeated calls in `via`.
  A batch can replace steps and add their typed conditions together. The
  model checks refuse invalid references, cycles, or an empty chain before
  either the entity files or the graph are written.
- `kb bind <meaning> <layout>:<address>` records the evidence of the
  candidate that `match.search` finds at the address, from the symbol on the
  layout of `--from`, the symbol that the reference names, or the home
  symbol; `--evidence` states the items instead. It refuses a layout where the
  meaning has a symbol, a location of another meaning, and a location that the
  search does not find. A new symbol of an unnamed meaning draws a generated
  name, and the file pins `home` when the symbol would move it.
- `kb absent <meaning> --layout <l> --evidence <item>` and `kb unresolved
  <meaning> --layout <l>` replace the status of the layout in the file. An
  unresolved status records the method, the target, and the count of the
  search with the L0 digest of the layout, or those of `--method`, `--target`,
  and `--count`; a search with one candidate is refused with the `kb bind`
  that records it.
- `kb link <from> <type> <to> [<key>=<value>...]` writes a link with its keys
  and `--evidence` items into the file of `<from>`, or joins them to the link
  of the file with the same type, target, `slot`, and `offset`: `via`,
  `layouts`, `supports`, and `reverse_supports` join, and another key agrees
  with the held value. `kb unlink <from> <type> <to>` removes a link of the
  file, which `slot=` and `offset=` choose among several; a link that only a
  registry states is refused.
- `kb set-link <from> <type> <to> <key>=<value>...` replaces mutable properties
  of one existing link in the owned file of `<from>`. `--slot` and `--offset`
  select the exact held values; an omitted selector selects an absent key,
  so an absent offset differs from an explicit zero. The offset is a
  nonnegative integer. Type, target, slot, offset, and evidence stay fixed.
  Mutable keys are `via`, `layouts`, `relies`, `supports`, `reverse_relies`,
  `reverse_supports`, `role`, and `note`; arrays replace the held arrays.
  An empty assignment removes an existing mutable key. A batch uses
  `cmd = "set-link"`, `meaning`, `type`, `to`, optional `selector`, `keys`,
  and `unset`. Unknown keys, invalid values, missing or duplicate native
  links, and links or owner files created earlier in the batch are refused.
  Exact repeated edits write nothing. Combine different property edits of
  one link in one operation: the complete batch retains each operation's
  resulting link, its evidence, and the original ledger dependencies of
  both ends with their native claims. Other links and selectors are unchanged.
- `kb rename <meaning> <semantic-name>` renames the file of the meaning. Each
  entry drops its generated name and keeps its previous full reference as its
  first `former` reference, a previous semantic name becomes a former name of
  the meaning, and the references of every entity file to a previous name name
  the new one. A name that another meaning of the kind holds as its name, one
  of its other names, or a former name of one of its symbols is refused, and
  so is a meaning whose name a registry states until that registry converts.
- `kb merge <meaning> <other>` moves the symbols of the other meaning into
  the file of the meaning, each with the evidence of its join: the
  `--evidence` items at its layout, or the candidate of the search as for
  `kb bind`. A named meaning keeps the former name of each moved symbol as a
  `former` reference. The statuses, keys, links, analogs, and former names of
  the other file join where they agree, the other file is removed, and the
  references of every entity file to the other names, including `[[...]]`
  citations, name the meaning. The two files of one meaning, which the `names`
  check reports, join entry by entry, and the name that the other file gives
  a symbol becomes its `former` reference.
- `kb move <symbol> <layout>:<address>` corrects the address of a symbol on
  its layout. The entry takes the evidence of the candidate at the new address
  that the search finds from the symbol on the layout of `--from` or from the
  home symbol, or the `--evidence` items, and keeps its previous full
  reference as its first `former` reference; every reference and `[[...]]`
  citation of the entity files to that reference names the new one. It
  refuses another layout, the home symbol as the start of its own search, and
  a location of another meaning.
- `kb move <symbol> <meaning>` moves the entry of a symbol, or its row of
  `kb/names.csv`, into the file of the meaning that it belongs to, with the
  evidence of the search from a symbol of that meaning or the `--evidence`
  items. The symbol takes the name of a named target and keeps or draws a
  generated name in an unnamed one; its previous full reference becomes its
  first `former` reference, and the references to it by that reference or by
  a name of its former meaning on its layout name it in the target. The
  change is refused when the compiled result does not join the symbol with
  the symbols of the target alone, as when a registry states it with its
  former meaning, or changes the key of either meaning, as when a registry
  names the symbol.
- An evidence item is a TOML inline table, for example `--evidence 'kind =
  "l0", at = "jk00c:00043f10"'`, and a batch states it as an `[[op.evidence]]`
  table.
- A status that a registry states stays until the conversion of that
  registry: a symbol on its layout fails the `symbols` check, and a status of
  another state disagrees with it, so either write is refused.

## L0

`l0/<layout>/` holds the normalized Ghidra exports of each layout of
`rom-images/homology.toml` with `manifest.toml`.
[`../ghidra/README.md`](../ghidra/README.md#l0-exports) describes
`tools/ghidra/export-l0.sh`. The `l0` check verifies, for every layout:

- the manifest against the layout, the image catalog digest, the Ghidra pin,
  the digests of the export scripts, and the census plan of `config.toml` and
  the interpolation registry;
- the file set, each file's digest and row count, and the normal form;
- every join of the fragment registry `tools/ghidra/merges/<layout>.csv`: the
  entry is a function entry, the fragment is none, and the fragment lies in
  the body of the entry
  ([`../ghidra/README.md`](../ghidra/README.md#function-fragments)).

A file whose digest the check has verified in normal form is recorded in
`.kb/cache/l0-normal.json`, so a repeated check hashes the files and skips
the parse.

The export logs a `review:` line for every function of a `fn` symbol of the
layout whose entry disappears, whose size changes, or whose former body holds
a new entry, so a reanalysis that splits or joins a reviewed function is
re-reviewed before its export is committed.

The `sites` check reads the function ledger `defs/<image>.funcs.csv` of the
L0 image of each layout. A `site:` token that is an instruction of an L0
function lies in the body of the row's function, of a function that the row
names outside its prose columns, or of a function that the row's function
calls, is called by, or continues into in sequence; otherwise the site
instruction references the row's function. A failure is a site cited under
the wrong function or a function that the analysis cut into fragments.

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
| `files` | `kb/<kind>/<name>.toml` | The meanings of the converted registries with their symbols, statuses, links, and evidence; the features with their targets; the telemetry fields with the `7mfk` symbols of their source meanings, which `can_telemetry` requires, and the source symbols whose unit their files state; the signals with the `7mfk` symbols of the meanings and the allocations that they observe; architecture stages, blocks, endpoints, and ordered chains |
| `layouts` | `patches/map-switching-layout.toml`, `patches/rolling-launch-layout.toml`, `patches/can-telemetry-layout.toml`, `patches/jk08a-runtime-reservations.toml` | The `7mfk` hook words with their canonical keys, their `target` links, and their replacements in the `7mfk` targets; the `tbl` symbols of the map families in `families` of the `7mfk` target; the payload offset of the feedback record; the `did` symbols of the rolling DID slots with the allocations of `rolling_launch`; the RAM that each feature allocates on `7mfk`, whose addresses name no meaning |
| `dids` | `tools/diagnostics/sid22_inventory.py` over the JK08A image | `did` symbols of the `7mfk` service 0x22 table with `source` links to the data they return |

Evidence tokens map by the table of section 20.7 of the specification: a
dependency token becomes a link stored at the end its type names or `trace`
evidence, and a token target without a registry row becomes an implicit
symbol of the kind its role and address admit.

The canonical DTC ledger states three complete expected `rom_const` spans per
row: its descriptor, attribute pointer slot, and stock attribute. The adapter
checks the index and geometry against `refs/diagnostics/rom-dtc/layouts.toml`
and binds the row's code, addresses, and stock attribute to those spans before
emitting typed `rom-bytes` identity evidence without `legacy`. `image-bytes`
verifies them on every applicable image; the compiler does not refresh the
expected bytes. The converted ledgers contain typed evidence without
`legacy`. A reproduced site holds a checked `l0-context` footprint; an
unreproduced one is `unverified-site`. A constant without a verified address
and byte binding is `unbound-constant`. The unverified items ground no level.

`indirect_base` uses eight lowercase hexadecimal site digits and a nonnegative
ASCII decimal or lowercase `0x` offset. It maps to `indirect` evidence on the
row's layout with `mode = "base"` and the integer offset as `value`. The
existing dependency `base:<address>[+<offset>]@structural` remains a link.
A `test` path is relative to the repository and ends in `.py`; its nonempty
`/`-separated segments contain only ASCII letters, digits, `_`, `.`, and `-`,
and no segment is `.` or `..`. Its function key is an ASCII Python identifier
other than a keyword. It maps to `test` evidence with that `path` and `key`.
The registry retains ownership of its facts until conversion.

The entity files own the facts of a registry from the commit that converts
it, and the compiler leaves out the adapters of the converted registries
(`adapters.CONVERTED`); the module of such an adapter renders the registry as
a projection of the files.

| Registry | Converted in stage | Entity files | Generators |
|---|---|---|---|
| `defs/*.interp.csv`, `defs/JK08A-*.interp-correspondence.csv` | 3 | `fn` meanings with `[interp]`, the evidence of their symbols, and the `unresolved` statuses of the `interp-contract` search | `kb.adapters.interp:registries`, `kb.adapters.interp:correspondences` |
| `defs/vq37-native-tables.toml`, `defs/vq37-native-fuel-cut.toml` | 3 | `tbl`, `axis`, `fn`, `ram`, and `const` meanings with symbols on `jk78c`, `1nd`, and `1me3b`: the keys and `[editor]` of the native tables, the evidence of their symbols, their `reader` and `axis` links, and their `absent` statuses | `kb.adapters.native:tables`, `kb.adapters.native:fuel_cut` |
| `defs/definition-projections.toml`, `defs/JK08A-*.definition-addresses.csv` | 3 | `tbl` and `axis` meanings with the row items of their symbols and the `absent` and `unresolved` statuses of the rows; the `definitions` targets of `kb/feature/definitions.toml` with `images`, `requires`, `variants`, and `omitted` | `kb.adapters.definitions:addresses`, `kb.adapters.definitions:projections` |
| `patches/rom-address-profiles.toml`, `patches/*-runtime-correspondence.csv`, the symbol and hook-key tables of `patches/runtime_targets.py` | 3 | `hook`, `fn`, `ram`, `reg`, `tbl`, `const`, and `did` meanings with the row items of their symbols, the `target` links of the hook words, and the `absent` and `unresolved` statuses of the rows; the targets of `runtime`, `map_switching`, `rolling_launch`, and `can_telemetry` in `kb/feature/` with their key tables, roles, `requires`, `variants`, `unsupported`, `notes`, and `basis` | `kb.adapters.profiles:address_profiles`, `kb.adapters.profiles:correspondences` |
| `patches/can-telemetry-profile.toml` | 4 | `field` entities with their keys, `signal`, and `source`; the unit, scale, scale level, values, and named bits of the source meanings of the `ecu_ram` fields; the wire constants, `profiles`, and `contexts` of `kb/feature/can_telemetry.toml`, the addresses of its `7mfk` target, and the allocations of the `7mfk` targets of `can_telemetry`, `map_switching`, and `rolling_launch` | `kb.adapters.telemetry:profile` |
| `defs/JK08A.tuning-signals.toml` | 4 | `signal` entities with their keys and the meanings and allocations that they observe; the widths of the observed meanings and the identity item of an observed symbol that no evidence grounds; the catalog keys of `kb/feature/can_telemetry.toml` | `kb.adapters.signals:catalog` |
| `defs/JK08A.overrides.toml` | 4 | `[editor]` of the `7mfk` tables and axes with their masked views and `[logparam]` of the `7mfk` RAM; `default_emit` and the switches of `kb/feature/definitions.toml` and the JK08A entry of its `7mfk` target | `kb.adapters.overrides:presentation` |
| `defs/JK08A.{funcs,vars,findings,axes,dtc,diagnostic-bindings}.csv`, `tools/ghidra/symbols/7mfk.csv` | 5 | Symbol properties, typed evidence, canonical links with both claiming ends, diagnostic tables, and curated names in the meaning files; `[[ledger]]` selectors retain the legacy views | `kb.ledger_projection:registries`, `kb.ledger_projection:curated_names` |
| `defs/JK08A.architecture.toml` | 6 | Architecture stages, blocks, endpoints, ordered chains and their steps; meaning `block` placements | `kb.architecture_projection:registry` |
| `tools/ghidra/symbols/1nd.csv` | 9 | Owned function names and exact row/prose selectors in the `1nd` symbol entries | `kb.adapters.curated:registry` |

`uv run python -m kb.convert <registry> [--dry-run]` converts a registry
under `.kb/lock`. It compiles the model with the adapters of the compiler and
the registry's adapter, writes the facts that the registry's adapter states
into the files of their meanings through the change of the write commands,
and compiles the model from those files with the adapters of the compiler.
It refuses the conversion with exit code 3 when the two models differ beyond
the rules of the registry, when the files add an issue of a model check or a
registry disagreement, or when a projection of the registry differs from its
file; otherwise it writes the files and `kb/names.csv` and loads the result
into the graph. On a converted tree it writes nothing. Before the stage 5
conversion, `uv run python -m kb.ledger_projection --normalize [--dry-run]`
orders complete evidence token texts lexically, retains every token, and
compares all model facts before writing the CSV files.

The architecture converter compares every property, reference, ordered step,
note, and block placement before writing. It verifies an L0 identity anchor
for each symbol previously declared only by a chain, without changing the
symbol's semantic level. The generated TOML preserves every fact and the
order used for block voting. Architecture references require a symbol on the
entity's home layout and cannot substitute one from another layout.

`kb suggest --blocks --layout <layout>` runs the installed read-only MAGE
Leiden procedure on that layout's functions, calls, and weighted shared-RAM
pairs. A call weighs 1; a shared-RAM pair weighs the number of distinct RAM
locations both functions read or write; a pointer-only literal is excluded.
Repeated sites and access producers count once. The procedure uses gamma 1.0,
theta 0.01, and resolution 1.0. A community proposes its most represented existing block, retains all
tied blocks as alternatives, or proposes a new block when none is placed.
Candidates require review and do not change blocks, levels, or source facts.

The ledger converter preserves all cells and row order except for removed
`wave` and `arg` process tokens. It records the classification of each site
and reproduces its structured context on L0. Every adopted symbol receives a
verified identity anchor; a verified base item states placement only.
`[[ledger]]` tables select the columns, owner notes, typed evidence, and
canonical links of each view. A dependency selector must match the link's
type, direction, layout, offset, role, and supported claim. Offset spellings
retain decimal or hexadecimal presentation and must equal the numeric fact.
A curated alias selects a current or former name. A legacy storage label is
separate from a numeric telemetry source's absent semantic unit.

The rules of the interpolation registries:

- The meaning of every symbol that the registries state takes `[interp]`,
  and each symbol an entry with the override of its layout and the typed
  evidence of the registries, whose `to` becomes a location.
- A wrapper symbol that no other registry states takes `l0` identity
  evidence at the first instruction of its body that calls its kernel entry,
  or at its entry when it is its own kernel.
- An item of an entry states an item of the registries when it equals the
  item or adds only the note of a correspondence row to it.
- An `unsupported` correspondence becomes an `unresolved` status with the L0
  digest of its layout and without the registry evidence.

`defs/<ROM>.interp.csv` lists, by address, the wrappers of the layout of its
image, each with the entry of its kernel: the address of the `kernel`
function on the layout plus `offset`. `defs/JK08A-<ROM>.interp-correspondence.csv`
lists a `mapped` row for each `interp-contract` item of a wrapper of the
image's layout toward `7mfk`, and an `unsupported` row for each `unresolved`
status whose method is `interp-contract`, by source wrapper.

The rules of the native registries:

- A meaning takes `home` where the registries state it, and each key that
  they state for its symbols where one of them has the value of the meaning.
- Each symbol that they declare takes an entry with its overrides of those
  keys, its `images`, its notes, and its evidence. An axis that they only
  name is a symbol that another registry declares. An item of an entry
  states an evidence item of the registries when it equals the item or adds
  only the note of a correspondence row to it.
- Each link takes an entry with its slot, its role, and the evidence of every
  symbol that states it, and each `absent` status an entry with its note and
  evidence. The notes of a file precede those of the registries in the note
  of its symbol.

`defs/vq37-native-tables.toml` lists for each target, by address, the `tbl`
and `axis` meanings with `[editor]` whose home is the layout of a target and
whose symbol the image carries, with the pointer bindings from the evidence
of their `reader` links with the role `accessor`, the axes from their `axis`
links, the note from the file entry of the symbol, and `values_sha256` from
the image, and then the meanings absent on the layout by name.
`defs/vq37-native-fuel-cut.toml` lists for each target the symbols of the
fuel-cut meanings on its layout with the call and the scheduler word from
their evidence, the values from the image, the size and the digest of the
function from L0, and the pointer bindings from the `reader` links to the
function.

The rules of the definition registries:

- Each target symbol of a row takes the item of its row first in its entry,
  with the prose of the row as `note`: the item toward the `7mfk` symbol
  that `kb.match.typed` gives, whose kind is the `function_kinds` of the row,
  or `l0` evidence for an `l0`, a `reviewed-target`, or a `stock-inert-path`
  row. An `l0` item lies at the first census operand of the storage of its
  symbol, or else at the first instruction that touches the storage, where
  it verifies.
- A `7mfk` symbol of a row that no evidence grounds takes `l0` identity
  evidence of the same placement, and one that only the registries state
  takes an entry.
- An `absent` status is the one that the file of its meaning states with its
  evidence; an `unresolved` status takes the search of the `7mfk` symbol on
  its layout, the L0 digest of the layout, and the prose of the row.
- `kb/feature/definitions.toml` takes a `[[target]]` for each layout that a
  projection targets, with its images, the meanings that its rows require,
  its variants, and its omitted surfaces.

`defs/<source>-<LAYOUT>.definition-addresses.csv` has a row for each meaning
that the `definitions` target of its layout requires. The row item of a
symbol is its first evidence item that is homology evidence toward the `7mfk`
symbol, which gives a `homologous` row, or `l0` identity evidence on its own
layout, which gives a `reviewed-target` row; a symbol that `omitted` lists
and a status give `unsupported` rows. `defs/definition-projections.toml` has
`[projection.<ROM>]` for each image of a `definitions` target other than
`7mfk`, with its note wrapped within 79 columns as `comment`.

The rules of the address profiles and the correspondence files:

- A symbol that a correspondence row states takes its row item first in its
  entry, with the text of the row as `note`: an item of its entry that states
  the row, or else the homology item toward the `7mfk` symbol of its meaning
  for a `mapped` row and the identity item of its own layout for a
  `target-specific` row. The homology item is the item that `kb.match.typed`
  gives, a `manual` item where the hardware manual of the MCU or its vector
  table places the symbol at the address of its origin, or an `l0` item; the
  identity item is the test of a row whose symbol no instruction reaches, the
  entry of a function, the `did-table` item of a DID slot, an `l0` item, or
  the `indirect` base item of a hook with the `rom-bytes` item of its stock
  word. An `l0` item lies at the entry of a function, and otherwise at the
  first census operand of the storage, the first instruction that touches
  it, the first load of one of its words from a literal pool, or the first
  place whose L0 references name it, where it verifies.
- A symbol that only the registries state and no row states takes the same
  homology item, or else the identity item; a `7mfk` symbol that a homology
  item of the conversion reaches and no evidence grounds takes its identity
  item. A wrapper with `[interp]` that only the registries state takes the
  `l0` identity item of the interpolation conversion, at the first call of
  its kernel entry.
- The `rom-bytes` items of the image-byte keys stay, a note that only the
  registries state for a symbol is dropped, and the names that only the
  registries state become `former` names. The `target` link of each hook word
  of another layout than `7mfk` takes the `rom-bytes` item of the word.
- A status that the file of its meaning states keeps its entry; an
  `unresolved` status takes the search of the `7mfk` symbol on its layout,
  the L0 digest of the layout, and the text of its row.
- `kb/feature/<feature>.toml` of `runtime`, `map_switching`,
  `rolling_launch`, and `can_telemetry` takes a `[[target]]` for each layout
  with the keys of its target.

`patches/rom-address-profiles.toml` has a profile for the image of each
layout other than `7mfk` with a `runtime` target and an `inherits` profile for
each other image of the layout, with the keys of its targets, the addresses
of their symbols and roles, the stock word that the `target` link of a hook
meaning reaches, the replacement of the previous feature as the `base` of a
hook, the fields whose source meaning has a status on the layout as
`telemetry_unavailable`, and the `basis` of the targets as `evidence`.
`patches/<layout>-runtime-correspondence.csv` exists for each layout whose
`runtime` target states `notes`. The row item of a symbol is the first
evidence item of its entry that is homology evidence toward `7mfk`, which
gives a `mapped` row, or identity evidence of its own layout other than image
bytes, which gives a `target-specific` row; a role gives a `target-specific`
row with its note, an `unsupported` entry and a status `unsupported` rows,
an allocation is `mapped` where it is the `7mfk` bound plus the relocation of
the profile, and a number where it equals the `7mfk` value.

`patches/runtime_targets.py` reads the `7mfk` side of the feature targets
through `kb.targets`, which reads the entity files without compiling the
model and with the standard library alone, since the firmware gate imports
the module with the Python of its container: the addresses of the `symbols`
of the `7mfk` targets with the `can_telemetry` numbers and record words, the
per-layout key of each hook of a `map_switching` target by the `7mfk` word of
its meaning, the keys of a target, the meaning that fills a key of a target
on a layout, which the `symbols` of the target give, or else its role, and
the number of a named bit on a layout, which the `[[bit]]` of the symbol
entry of the layout gives, or else that of the meaning. The adapter of the
address profiles reads the same key tables and hooks for the model before a
conversion.

The rules of the telemetry profile:

- Each field takes `kb/field/<name>.toml` with its keys, its `signal` as the
  reference of its signal, and its `source`: for an `ecu_ram` field the
  reference of the meaning of its `7mfk` symbol, whose entry must hold
  evidence where only the profile and the entity files state the symbol, and
  for another field its allocation as `<feature>.<allocation>`.
- The file of a source meaning takes the unit, the scale, and the scale
  level that the scale of its field gives, a bare `raw` as the scale `x`, or
  the values of an enumeration or the named bits of `bits: <n> <NAME>, ...`,
  which must equal the keys of the meaning; values and bits agree by number
  and name. A scale that the conversion cannot split fails the `fields`
  check, and the conversion refuses it. The remaining text of the scale
  becomes the summary of a meaning
  whose summary in the model it is and whose file states no other, and
  otherwise a note of its file; the names that only the profile states
  become `former` names.
- `kb/feature/can_telemetry.toml` takes the wire constants, `profiles`, and
  `contexts`, and the existing `7mfk` target of each feature takes the keys
  and the allocations that the profile gives it.

`patches/can-telemetry-profile.toml` has the wire constants of
`can_telemetry`, the mailbox and the addresses of its `7mfk` target, its
`profiles`, the stream fields by page and offset, and the fields of each
context by position. The `source` of an `ecu_ram` field is the address of
the `7mfk` symbol of its meaning, and its `scale` the string that the unit,
the scale, and the scale level of the meaning give, or else its values as
an enumeration or its named bits as `bits: <n> <NAME>, ...`, each by number;
another field has the address of its allocation on a `7mfk` target and the
scale of its file. When a numeric source meaning has no unit, scale, values,
or named bits, the profile presents `raw count` with identity conversion.
This host storage view adds no scale, unit, or evidence to the source
meaning, including during repeat conversion of the profile. A partial or
unrenderable conversion refuses projection. Numeric
telemetry source files own their units, including absence; the legacy RAM
ledger does not restore a storage description as a semantic unit. The
conversion lists each `ecu_ram` scale that the projection renders in
another string and refuses any other change of the file.

The rules of the signal catalog:

- Each signal takes `kb/signal/<id>.toml` with its keys and, in `observes`,
  the reference of the meaning of each `7mfk` symbol that it observes and
  each allocation, in the order of its sources.
- The file of an observed meaning takes the `width` of its `7mfk` symbol,
  as the key of the meaning where the meaning has that width and otherwise
  as the override of the entry; an observed symbol that no evidence grounds
  takes its identity item.
- `kb/feature/can_telemetry.toml` takes `telemetry_profile`,
  `full_rate_hz`, and `rotating_divisor`.

`defs/JK08A.tuning-signals.toml` lists the signals by domain, by priority
from `core` to `research`, and by id. Its `sources` and `widths` are the
addresses and the widths of the observed `7mfk` symbols and allocations in
the order of `observes`, its `current_fields` the fields whose `signal` names
the signal, by observed source and in the order of the profile, and its
`dids` the DIDs that return an observed meaning, by source and by number.

The rules of the presentation layer:

- The file of the meaning of each `7mfk` table, axis, and RAM that the layer
  names takes its `[editor]` or `[logparam]`: as the key of the meaning where
  the meaning holds the same value, and otherwise as the key of the entry of
  the symbol. `static_axis_operand` becomes the reference of the meaning of
  its operand.
- `kb/feature/definitions.toml` takes `default_emit` and the switches, each
  with its position as `order`, and its `7mfk` target the JK08A entry of
  `images`, whose notes are one paragraph each; the entry keeps `basis` and
  the other keys that the layer does not state.

`defs/JK08A.overrides.toml` has, after its header, `[presentation]`, the
exposed features, `[logparam.<address>]` by address, `[rom]` with its
comment, the checksums, the switches by `order`, `[table.<address>]` by the
`order` of the editor and by address with the masked views of each table
after it, and `[axis.<address>]` by address. Each note is wrapped at 79
columns, and the file has no other comments than its header. The conversion
lists each comment that it drops and each note that it wraps anew, and
refuses any other change of the file.

## Matchers

`kb.match` decides evidence on L0 and the images of each layout (sections
7.3, 7.6, and 13 of the specification). The code of a layout is the masked
instruction word at every instruction address of its L0 bodies, where masking
clears the displacements of PC-relative loads, `mova`, branches, and GBR
accesses. A region is a maximal run of equal masked words that aligns an
instruction of one layout with one of another; an instruction aligns when a
region of at least `[match] words` occurs once on each layout and no other
region of the instruction is as long. Aligned instructions relate two
addresses in the same way when they load, store, or update them through a
pool literal, load them as a literal, call them, or pass them as one operand
of a census call.

| Check | Scope |
|---|---|
| `homology` | File-owned symbols: each identity and homology item holds, and a verified chain reaches an anchor. Every non-legacy `indirect`/`base` and `test` item of a symbol is also verified, regardless of ownership or `supports` |
| `image-bytes` | Hook `target` words, the sources of DID entries, and each typed `rom-bytes` and `did-table` item, on every image the symbol applies to |
| `statuses` | The statuses of the entity files: `absent` carries evidence, and `unresolved` states its search; a search older than the L0 of its layout prints a note |
| `writers` | Every `ram` and `reg` meaning: a store of one symbol that aligns on the layout of another symbol aligns with a store of that symbol |
| `levels` | Every declared level stays within its effective level and evidence grounding; hardware records pass and arithmetic equations hold. Hardware results are inputs of the cached gate |

A base item verifies that L0 references `symbol.address - value` at `at` on
the symbol's layout. This is base placement, not verification of the complete
address path: indexing, copy lengths and boundaries, branches, and delay slots
require separate fixed-byte/address-math tests. The `homology` check fails a
bad base item even if `levels` holds the structure. Other indirect modes keep
their existing verification boundary. A `test` item verifies only that the
Python AST defines its key; neither `homology` nor `kb audit` executes the
function or establishes a passing test result. The model checks include the
named Python files in their inputs; the repository test runner executes them.

`[writers] review` of `config.toml` lists the contradictions of the writer
gate that await review, each as the symbol and the store site on its layout.
The gate fails on every other contradiction and on an entry that no longer
reproduces.

`match.search` lists the candidates for the counterpart of a symbol on
another layout, each with the evidence item that states it and the number of
aligned sites and function pairs that vote for it. `match.code` keeps the
index of a layout in `.kb/cache/match/<layout>.pickle`, keyed by the L0
manifest, the image digest, the census plan, `[match] words`, and the sources
of the matcher and the derivations; a rebuild takes a few seconds per layout.
A loaded index lives as long as the process. Loading pauses automatic garbage
collection and restores the caller's collection mode on success and failure.
The loader leaves the caller's frozen generation and collection thresholds
unchanged; unrelated temporary models remain collectable.

## Graph

`kb sync` builds the model and compatibility layers in the Memgraph instance
of the working tree. The compiler owns the load order and the writer lock;
the former loader entry points expose their layer builders to it. The
compatibility layers retain their established node and relationship contracts
for definition, map, diagnostic, and provenance consumers. A complete build
writes `Meta` last, and a failed layer leaves no accepted fingerprint.

Compatibility completion is independent of `Meta`. Each ROM is one coupled
group: functions, memory accesses, maps, reviewed claims, and diagnostic
bindings. A group reloads when the exact bytes or presence of its L0 files,
images, logical current-model views, complete census inventory, source model,
curated names, diagnostic corpus, or producer modules change. Temporary view
directory names and the common compiler fingerprint do not identify a group.
The external vendor vocabulary and pinned A2L form one group.

`CompatibilityState` records completion only after every builder in its group
returns and a second exact-input check passes. Its record is removed before
destructive writes. A failed build retains completed independent groups for
the next sync, while `Meta` remains absent. Rebuilding the diagnostic corpus
invalidates every ROM completion before deleting shared diagnostic bindings,
including a rebuild caused only by a missing corpus completion record.
`kb sync --full` clears completion records and reconstructs every group.
Group and layer progress reports loading, completion, and reuse immediately.

Builders read private, read-only byte copies of every data input, with the
same logical directory structure and without links to working files. The
completion digest binds those consumed copies and captured arguments. A
temporary working-file mutation followed by restoration cannot change a
builder's inputs. The entire census filename inventory is captured, including
unexpected files that the map builder must refuse. Final checks still compare
the working inputs and the common fingerprint before accepting completion
and publishing `Meta`.

| Part | Elements | Reloads when |
|---|---|---|
| L0 of a layout | `Function`, `Location`, `CALL`, and `ACCESS` with producer `l0` or `derived` | the digest of its L0 files, its images, the address spaces of its MCU, or the modules `derive`, `l0graph`, `sh2`, and `values` changes |
| Claims | `Family`, `Layout`, `Image`, `Meaning`, `Symbol`, `HAS`, the link types between meanings and between symbols, `STATUS`, and `CITES` | the fingerprint changes |
| Joins | `AT` from symbols to the L0 nodes at their addresses, and `verified` on the `WRITER` and `READER` links of symbols | either part reloads |

- `ACCESS` with producer `l0` comes from `function_references.csv`: every
  reference to RAM or a register with its reference type as mode, every data
  or parameter reference to ROM, and every pool literal that names RAM or a
  register, with mode `literal`. `ACCESS` with producer `derived` comes from
  literal pairing, with modes `load`, `store`, and `update`, and `literal`
  for a `stc gbr` that takes the literal of GBR. One `ACCESS` per
  producer joins a function and a location, and its `sites` list holds one
  map per instruction.
- A writer link of a symbol is verified by a normalized `store`, `update`,
  `write`, or `read_write` access of the function to the symbol's location.
  A reader link uses `load`, `update`, `read`, `read_write`, `literal`, `data`,
  or `param`. A block copy loads
  only the destination address, so its writer stays unverified until
  `indirect` evidence explains it.
- The fingerprint covers every input: the model inputs, the compiler
  modules, `l0/`, and the images of the catalog. The modules of the command
  line, the read and write commands, the MCP server, the checks, the
  projections, the guard, and the instances, which `compile.NOT_COMPILER`
  lists, are no inputs. `.kb/cache/hashes.json` keeps the git blob hash of each file
  by size and modification time. `:Meta` is deleted first and written last.
- The main working tree uses the compose service of
  [`../memgraph/`](../memgraph/README.md). `kb instance up` in a linked
  working tree starts a container from the compose image with its data in
  `.kb/memgraph/` and a loopback port from `[instances] ports`, and records
  it in `.kb/instance.toml`; `prune`, which `up` runs first, removes the
  containers of vanished working trees and stops idle ones. `KB_BOLT`
  overrides the Bolt address for tests against a scratch server.
- Graph consumers use `kb.reader.session`: it holds the primary writer lock,
  checks the fingerprint, refuses mutation clauses and discovered write
  procedures and every `periodic.*` procedure, and rolls back its read
  transaction. CLI and MCP graph answers retain that boundary through
  rendering; source-only checks, audits and code answers hold the same lock.
  A changed source fingerprint refuses the complete buffered answer before
  it reaches standard output. Compiler caches use the current fingerprint;
  literal-pair caches bind their exact token, image and producer inputs.
  A source change during construction refuses the result without caching it.
- MCP validates required arguments and primitive and array shapes before
  command dispatch. Invalid requests and unexpected command failures receive
  individual errors; subsequent requests remain available. Driver connection
  and configuration failures use graph error code 6.
- Acceptance snapshots create missing output parents under `tmp/`, refuse
  paths outside that directory and existing receipts, and report filesystem
  failures with usage error code 2. Exclusive creation preserves a receipt
  that appears after path validation.

## Projections and the access guard

`projections.toml` registers every generated file of the repository with its
generator, inputs, consumers, stage, and read mode, as section 14 of the
specification states. `uv run kb project` renders under `.kb/lock` the
projections of `kb` functions whose stage the transition has reached, such
as the `AGENTS.md#kb` section, the `features` section of
`rom-images/support-matrix.md`, the interpolation, native, and definition
registries, the address profiles with the correspondence files, and the
telemetry profile; the generator of a pattern returns the text of each of
its files; `--check` writes nothing and exits with 1 when a projection
differs from its rendering. A projection of another generator keeps that
generator and its gate. The `projections` check requires every entry to
match tracked files that no other entry claims and to name existing paths,
compares each projection of `kb` with its rendering and the tracked files of
a pattern with the files of its rendering, and requires every tracked file
whose first lines declare it generated to be registered.

Each feature file carries `title`, `summary`, and `specs`, the
specifications that state how the feature works and its acceptance
criterion. `kb.matrix` renders the `features` section of
`rom-images/support-matrix.md` from the feature targets: a row for each
layout, a column for each feature in the order of the build, and in each cell
the status of the target with the runtime ROM and RAM, the switched and
unsupported map families, the telemetry mailbox, the fields whose source the
layout lacks, and the other required meanings without a symbol by the state
of their status; a table of the title, summary, and specifications of each
feature follows.

The files decide the owner of a registry of a stage that has started:
`kb brief` and `AGENTS.md#kb` name the owner after conversion once every
tracked file that the registry's row of section 19 names is a projection of
`kb` that applies or a Python module that imports `kb` and that no adapter
reads, and the registry until then. A registry whose conversion leaves no
such file converts when `converted` of `bench.toml` lists it. The
`projections` check requires each row of section 19 to state one stage and
each entry of `converted` to name a row whose stage has started and whose
files do not convert it. `kb brief` counts the rows of `kb/names.csv` by the
first stage that converts a registry stating their symbol, by the registries
that state their symbol when none of them converts, and the rows that
reserve the name of a symbol that no registry states.

`hook.py` is the access guard of section 15. The tracked
`.claude/settings.json` and `.codex/hooks.json` run it before `Read`, `Edit`,
`Write`, `MultiEdit`, `NotebookEdit`, `Grep`, `Glob`, and `Bash`; Codex also
registers the canonical `apply_patch` name. Both use the Python of `.venv`,
or `python3` without it. The Codex command resolves the hook from the git
root, including when a session starts in a subdirectory. It refuses reads,
searches, and edits of `kb/` and
`l0/`, edits of the projections that apply, and reads of the guarded ones,
and names the command that answers instead. A shell command passes when it
changes the directory or runs `kb`, a git subcommand of the allow list,
`make`, or a script under `tools/` or `patches/`. `KB_GUARD=off` in the
hook process environment disables the guard for maintenance. Codex patch
checks include every added, updated, deleted, and moved file. An update of a
file with a generated section passes only when that section stays intact;
the check reconstructs its content without applying the patch. Shell checks
use the tool's `workdir` when supplied. The `guard` check requires both
settings to be tracked, synchronous, and to cover every tool, `.ignore` to
list the guarded paths, and the hook to refuse sample calls on each.

Codex loads project hooks from its trusted project configuration layer.
Use `/hooks` to review and trust the exact hook definition before it runs;
changed definitions require another review. Hook errors do not block a tool
call, and the `python3` fallback must satisfy the Python requirement in
`pyproject.toml` for `tomllib`.
Run `uv sync --frozen` to provide the working tree's supported interpreter.
These hooks guide knowledge access; the source checks validate the resulting
files. See the [Codex hook contract](https://learn.chatgpt.com/docs/hooks).

For a shared Codex app-server, manage the KB guard override directly:

```sh
uv run kb guard off --session <session-id>
uv run kb guard on --session <session-id>
uv run kb guard status --session <session-id> --json
```

Run these commands in this working tree. `--session` requires an explicit root
session UUID. The command records `on` or `off` atomically under
`~/.local/state/vq-kb-guard/<project-path-sha256>/<session-id>.json`. The hook reads
the record using the event's `session_id`, so an active session does not need
to restart and a remote server does not need the client's environment. A valid
record overrides the hook environment; absent, unreadable, or malformed records
retain the environment fallback. Other sessions,
working trees, and hook definitions retain their settings. Subagents and forks
that share a root `session_id` share its switch. The switch persists until an
explicit `on` or `off` command. `status` reads only the saved override and writes
nothing. Its JSON `mode` is `null` without a valid record; this does not report
the effective environment of a remote hook. The command does not access the
graph or change hook definitions, the Codex executable, shell startup files, or
`PATH`. Start or resume Codex with its ordinary command.

## Modules

| Module | Role |
|---|---|
| `kb.repo` | Repository paths, the image catalog, the layouts, and the configuration |
| `kb.vocab` | Kinds, levels, link types, evidence kinds, and the other vocabularies |
| `kb.tokens` | Legacy evidence tokens and their evidence items |
| `kb.model` | Symbols, meanings, links, and the builder that joins them |
| `kb.store` | Entity files of `kb/`, their canonical rendering, and `kb fmt` |
| `kb.targets` | The feature targets and the symbols of their meanings, read from the entity files for the patch build |
| `kb.adapters` | Adapters of the entity files and of the legacy registries |
| `kb.names` | `kb/names.csv`, the domain dictionary, and generated names |
| `kb.compile` | The compiler from the tracked inputs, or from those with an overlay of changed files, to the model |
| `kb.checks` | The model checks and the audit |
| `kb.arithmetic` | Chain-note equations under the configured arithmetic grammar, without evaluation or stock-code grounding |
| `kb.levels` | Claims, effective levels, grounding, and the `levels` section of the audit |
| `kb.fingerprint` | Input paths, git blob hashes, and the fingerprint |
| `kb.passes` | The inputs of the checks and the record of their passes, which `kb check --changed` compares |
| `kb.lock` | `.kb/lock` |
| `kb.instance` | Graph instances by working tree |
| `kb.graph` | Claim rows, loading, `:Meta`, and read-only queries |
| `kb.l0graph` | Graph rows of the L0 part of a layout |
| `kb.values` | Property values the graph stores |
| `kb.refs` | References of the read commands and their resolution |
| `kb.answer` | Answers, sections, token counts, and budgets |
| `kb.read` | The read commands |
| `kb.history` | Full former symbol references and recorded profile address corrections |
| `kb.write` | The write commands: changes of the entity files, the checks of their result, and batches |
| `kb.mcp` | The read commands and `kb_apply` as MCP tools over JSON-RPC on standard input and output |
| `kb.spec` | The stages, the ownership table, and the acceptance questions of the specification |
| `kb.project` | `projections.toml`, `kb project`, the `projections` check, the owners of the current stage, the count of `kb/names.csv` by stage, and the `AGENTS.md#kb` section |
| `kb.matrix` | The `features` section of `rom-images/support-matrix.md` |
| `kb.convert` | The conversions of legacy registries into entity files |
| `kb.architecture_projection` | The generated architecture view of owned entities and meaning placements |
| `kb.suggest` | Read-only MAGE block candidates over calls and shared RAM |
| `kb.guard` | The `guard` check of the settings, `.ignore`, and the hook |
| `kb.l0` | L0 export, normal form, manifest, the fragment registries, the export review, and the `l0` check |
| `kb.sh2` | SH-2E instruction decoding for the derivations |
| `kb.derive` | Function bodies and literal pairing over L0 and the layout image |
| `kb.sites` | Reproduction of the `site:` evidence of the ledgers from L0, and the `sites` check |
| `kb.match` | Masked matching, evidence verification, grounding, counterpart search, and the writer gate over L0 |
| `kb.cli` | The command line |

Literal pairing propagates register values through the control flow of each
function body. A register holds a pool literal at an instruction when every
path from the function entry reaches the instruction with that literal,
copied or offset by immediates or by registers of known value; a call clears
r0 through r7 after its delay slot. Immediates and shifts of known values
give a register a known value without a literal, so an index built by
`mov #imm`, `shll8`, and `add #imm` resolves. An access through a register
that holds a literal yields the accessed address, the literal, its pool
address, and the base register. An R0-indexed access whose index is unknown
yields the table base. `stc gbr,Rn` with a literal in GBR yields that literal
with mode `literal`, since the register passes the block on.

`kb.sites` classifies each `site:` token of a ledger row by the first relation
that connects it to the row in L0: a reference at the site, the body of a
function the row names, a 32-bit pointer in the image, or the body of a
function that L0 links to the row's subject. The tests require the share of
the JK08A ledgers that stage 1 of the specification states.

## Configuration

`bench.toml` holds the acceptance questions with their commands, budgets,
stages, baselines, and required `expect` patterns, the highest stage that has
started, and `converted`,
the registries whose conversion leaves no file that `kb` renders or that
reads `kb`.
`config.toml` lists the L0 export scripts, the census plan of each layout, the
instance limits and ports, the lock timeout, the output budgets of the
commands, the address spaces of each MCU, the manual prefixes of legacy
`spec:` tokens, the axis quantities, the attempt limit of generated names,
the trees and git allow list of the access guard, the region length of the
matchers, and the writer contradictions under review. `projections.toml`
registers the generated files. `domain-words.txt` lists the words a generated name must
not contain, beside the words of semantic names, signal titles, and editor
table names. `.kb/` holds the per-worktree state and is
ignored by git.

## Tests

```bash
uv run pytest -q tools/kb/tests
KB_TEST_BOLT=bolt://localhost:<port> uv run pytest -q tools/kb/tests/test_graph.py
```

The second form also loads the whole model, in about a minute, into the
scratch server that `KB_TEST_BOLT` names and that the test clears.
`test_spec.py` binds the command tables of section 12 of the specification to
the parser: the syntax of every row whose stage has started parses, every
command and option of the parser appears in such a row, the MCP tools are the
read commands of those rows, and the exit codes are those of section 12.5.
