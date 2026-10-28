# kb

`kb` is the entry point for firmware symbols, meanings, relations and evidence.
[`SPEC.md`](SPEC.md) defines the live model. Knowledge representation transfer
is complete; unresolved review records with reasons are supported data.

`contracts.toml` owns machine-readable command and fact-owner declarations.
`bench.toml` owns benchmark questions and content expectations. Runtime readers
and contract tests do not recover those facts from specification prose.

## Read knowledge

Run commands from the repository root or `tools/kb`:

```bash
uv run kb brief
uv run kb find knock threshold
uv run kb at jk00d:ffff1034
uv run kb where normalized_load/ram
uv run kb raw normalized_load/ram --json --full
uv run kb code jk78c:000564a4 --listing --full
uv run kb --help
```

References can name a meaning, a symbol on a layout, a layout-qualified
address or a former name. `show`, `where`, `impact`, `path`, `gaps` and `log`
provide the corresponding views. Use each command's `--help` for its arguments.
`--json` returns structured data; `--full` removes the ordinary output budget.
A `TRUNCATED:` answer names the option or narrower command that exposes the rest.

Ordinary graph reads check freshness and synchronize stale derived data unless
`--no-sync` requests a refusal. The graph is an index of tracked knowledge.
A successful synchronization does not establish new firmware semantics.
Ordinary reads use the CLI directly, without per-read receipts or wrapper
runners. The MCP server exposes the same supported read commands and `apply`.

`cypher` classifies mutation clauses separately from property names, parameters,
labels, result aliases and references to bound names. Comments and string
literals do not introduce clauses; quoted procedure names retain their actual
identity for the write-procedure check. A classifier acceptance is not a syntax
validation: the graph reports syntax errors through the ordinary CLI, and
unterminated quotes or comments are refused as malformed input. Actual mutation
clauses, transaction commands, discovered write procedures and `periodic`
procedures remain unavailable through this read interface.

## Change an owned fact

Ask KB for the owner and read the complete record before changing it. Native
meanings and designed entities own their declared facts; generated files are
projections. Use supported writers and their documented arguments. A batch
has a reviewable dry run:

```bash
uv run kb apply tmp/operations.toml --dry-run
uv run kb apply --help
```

The writer validates the batch under its lock. Its supported interrupted-write
and recovery boundary is tracked under issue #44; a successful write does not
establish multi-file rollback.

`semantic=false` identifies a generated name. `kb rename` preserves former
knowledge references. Source consumer names and filenames are a separate
refactoring responsibility under issue #71.

Historical unresolved chain records remain data with their original source
and reason. They do not qualify an access, prove a calculation or raise a level.

## Evidence and confidence

Levels distinguish resemblance, a candidate interpretation, grounding in
program structure or bytes, and hardware confirmation. L0, image bytes and
reviewed code retain their independent grounding roles. Graph topology is not
semantics, and software checks do not replace hardware validation.

A historical file reference uses `git:<tag>:<repository-path>[#fragment]`.
Stock-proof evidence uses the local `archive/stock-proofs-2026-10-26` tag.
Archived TEST evidence and TEST evidence without `supports` provide no grounding.
The passive reference parser does not import or execute archive code. Evidence records retain historical paths as data.

Executable stock-code proofs require prior agreement on a named patch obligation
or calibration decision that cannot proceed without one. The main KB path does
not provide proof-package preparation, bounded proof traces or evidence-reuse
commands. Required patch execution verification belongs to `tools/sh-elf-run`.

## Projections and access

`projections.toml` declares each generated file, its generator, inputs, consumers
and read policy. Change the fact in its owner and run its declared generator.
For example:

```bash
uv run kb project 'AGENTS.md#kb'
uv run kb project patches/runtime-bindings.toml
uv run kb project patches/runtime-bindings.toml --check
```

Runtime bindings are a numeric projection consumed by the patch builder without
importing KB. `AGENTS.md#kb` is generated from the machine contracts and benchmark
owner. Each generated section has one generator and one consistency check.

The access guard directs protected data and projection operations to KB.
A refusal names the supported command. Diagnose the prescribed path; a failed
operation does not authorize a guard override or another writer.

Shell checks distinguish file operands from literal draft, here-document and
message text. Redirections and active command substitutions are checked before
trusted commands run. Absolute patterns retain their root, symbolic links use
their targets, and subshell directory changes stay in their scope. Git review
commands remain available; blob reads, message-file reads and worktree writes
still receive the corresponding file checks.
Literal pipeline data receives file checks when `xargs` passes it to a command
that can access files. Python program arguments receive their operand checks.
Known shell variables expand before those checks; an unresolved operand with
an absolute prefix outside the repository and its ancestors is permitted.
Bounded literal `for` lists check each possible value, including nested lists;
unknown iteration values retain conservative operand checks.
For `gh issue` and `gh pr` create, comment, close and edit operations, comment,
body and title options contain data. Body-file options remain read operands.

Inline Python inspection supports literal file paths, simple path bindings and
captured-response metadata transformations. It conservatively refuses unknown
operations involving protected references. It does not execute the program or
provide general Python analysis. The hook requires Python 3.11 with `tomllib`;
an unsuitable fallback interpreter returns a deliberate denial.

## Implementation

| Modules | Responsibility |
|---|---|
| `cli`, `mcp`, `read`, `refs` | Supported entry points and reference resolution |
| `compile`, `model`, `store`, `vocab` | Native data, schema and model construction |
| `levels`, `checks`, `match` | Confidence, invariants and structural matching |
| `graph`, `project`, `targets` | Derived queries and owned projections |
| `spec`, `evidence_ref` | Machine contracts and passive historical references |

`config.toml` owns export, layout, matcher, instance, guard and output settings.
`owners.toml` retains name ownership and reconciliation reviews. `.kb/` holds
per-worktree state and is ignored by Git.

## Checks

Use small packages with a named user scenario and run affected tests immediately.
The Makefile declares repository acceptance targets; full checks run before
flashing and before closing an engineering track. Final acceptance runs the complete suite once; a fast/default and full/preflash
split is needed only if that run exceeds three minutes.

Graph integration tests use the isolated instance selected by `KB_TEST_BOLT`
and clear that instance. Run them against a dedicated test graph.
