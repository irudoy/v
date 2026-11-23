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

The [firmware research issue](https://github.com/irudoy/vhrev/issues/47) tracks
coverage by ROM image and subsystem. Generate the Markdown snapshot for the
issue with:

```bash
uv run kb coverage
```

Ordinary graph reads check freshness and synchronize stale derived data unless
`--no-sync` requests a refusal. The graph is an index of tracked knowledge.
A successful synchronization does not establish new firmware semantics.
The read announces an automatic synchronization. Commands waiting on its lock
show the current stage; new progress from the same synchronization renews the
configured waiting deadline. A stalled synchronization retains the timeout.
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

A symbol on another layout starts from `kb suggest <meaning> --layout
<layout>`, whose candidates carry the evidence items of the matchers.
`kb bind <meaning> <layout>:<address>` without `--evidence` records the
strongest item of that candidate, and every item that `kb suggest --json`
lists is valid evidence of its location, as a TOML inline table of
`--evidence` or as an item of a batch. A search
without a bindable candidate becomes `kb unresolved`, whose stated
`--target` is a location or a reference.

The writer validates the batch under its lock, then records previous file bytes
and modes in `.kb/publication.json` before publishing sources. Native batches
retain that journal through graph synchronization, including generated-name
enrollment. An I/O failure, process interruption or post-write sync refusal
leaves the journal available; ordinary knowledge reads, writes and sync refuse
the incomplete snapshot. Commands waiting for a live publisher use its recorded
lock timeout and renew it on graph-sync progress, without reading potentially
partial configuration. Instance controls and `kb guard status` remain available.

```bash
uv run kb recover --status
uv run kb recover --dry-run
uv run kb recover
```

Recovery checks every recorded path before restoring any source. Each current
file must match its previous state or a state produced by the publication;
manual edits, mode changes, unexpected replacements and symlinks refuse the
operation. An interrupted restoration retains its journal and can resume. The command
restores exact previous source bytes and modes without a guard override or a
Git rollback. It does not accept the proposed batch or relax source and census
gates. The next ordinary command performs the normal freshness check and sync.

If a path conflicts, preserve the manual edit separately, return that path's
content and mode to a recorded previous or produced state, and repeat
`kb recover`. Reapply a retained edit through a KB batch after recovery. Manual
removal of `.kb/publication.json` is not a supported recovery path: it discards
the previous snapshot without establishing source consistency.

This contract covers native writer batches, legacy reservation moves and the
file phase of standalone store writes such as formatting or generated names.
`kb family new --draft` supplies the proposed layout to the L0 exporter.
`kb family new/add` prepares the family registry and homology CSV before
publication. An initial batch also prepares the native bindings and their
interpolation registry. The dry run previews these files after the L0 and
census checks. The journal stays through the published-report check and graph
synchronization. The steps are in [`new-rom-intake.md`](../../rom-images/new-rom-intake.md).
Other projection generators and graph loading do not form one filesystem or
graph transaction. Their broader publication boundary is
tracked under issue #44. The full contract is in
[`SPEC.md`, section 9.8](SPEC.md#98-source-publication-and-recovery).

`semantic=false` identifies a generated name. `kb rename` preserves former
knowledge references. Source consumer names and filenames are a separate
refactoring responsibility under issue #71.

Historical unresolved chain records remain data with their original source
and reason. They do not qualify an access, prove a calculation or raise a level.

Unresolved access and width reviews bind the layout and image identity plus
the names and actual contents of its normalized L0 exports. Preparation input
hashes do not change that binding when the exported data is identical. The L0
check independently validates preparation inputs. Search statuses and matcher
caches retain their manifest identities.

After a corrected export, transfer the still-reproduced reviews through the
supported writer:

```bash
uv run kb rebase-reviews --layout 7mfk --from-l0 <previous-data-digest> --dry-run
```

The previous digest is the `l0` value held by the selected reviews in
`owners.toml`. The dry run prints a diff and lists changed, vanished, new, or
otherwise unmatched differences. The writer changes only `l0` for a record
whose `(kind, subject, claim_sha256)`, detail, and sources reproduce exactly;
its unresolved state and reason remain unchanged. Other layouts stay intact.
Unmatched records remain on disk, so `kb check --only code` still fails until
they receive a separate review. Exit 0 reports a successful operation, not a
complete reconciliation.

Custom reasons can refer to indirect pointer paths or other function details
that the difference key does not cover. The writer lists those reasons and
leaves their records unchanged unless `--reasons-reviewed` is present. Review
the affected code and call paths before using that flag; it preserves the
prose and does not validate it, provide evidence, or raise a level. Run the
same command without `--dry-run` to apply the reviewed diff.

`kb apply` accepts the equivalent `rebase-reviews` operation with `layout`,
`from_l0`, and optional `reasons_reviewed` keys. A review-rebase batch contains
only these operations, keeping claim edits separate from export maintenance.
It compiles under the writer lock and checks the selected L0 before writing.
Changed source inputs during planning refuse the operation before an owner write.
Its dry run does not synchronize the graph; applying a changed owner uses the
primary writer and then synchronizes the graph.

A false function whose entry disappears from validated L0 can retire with
`kb retire <meaning>/fn --withdraw-ledger <registry>:<order> --dry-run`.
Repeat the selector option to name every owned ledger row exactly once.
Other consumers and live function entries still refuse retirement. The
inactive document retains its selectors and names as historical data; they
leave the active projections. This source repair resolves the canonical
meaning key under the writer lock before graph synchronization, so the
vanished entry does not require a successful graph load first.

## Evidence and confidence

Levels distinguish resemblance, a candidate interpretation, grounding in
program structure or bytes, and hardware confirmation. L0, image bytes and
reviewed code retain their independent grounding roles. Graph topology is not
semantics, and software checks do not replace hardware validation.

Byte-identity evidence compares positive, complete ROM ranges on both layouts
and every applicable image. RAM bindings use reviewed L0 access/address
evidence. Matching hashes of empty or truncated ROM slices provide no identity
grounding.

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
unknown iteration values retain conservative operand checks. Other `for` lists
contain data; a pattern in them receives read checks. Reserved words such as
`do` and `then` and wrappers such as `timeout` and `env` leave the decision to
the command they precede.
For `gh issue` and `gh pr` create, view, comment, close, reopen and edit
operations, issue numbers, URLs, branches and text options contain data;
`--body-file` (`-F`), `--template` (`-T`) and `--recover` remain read
operands.
For `gh api`, the endpoint and field values contain data; `--input` and `-F`
values that start with `@` remain read operands, and an unresolved `-F` value
receives the operand check.

Process diagnostics have explicit argument contracts. Quoted patterns and
formats are data, even when they name a KB tree; they do not read that tree.

| Diagnostic | Data arguments | Protected file operands |
|---|---|---|
| `pgrep`, `pkill` | Process patterns, IDs, users, groups, signals and delimiters; `pkill -e` / `--echo`, `pgrep -r` / `--runstates` | `-F` / `--pidfile`, including attached and clustered short options; `--pid`; `-t` / `--terminal` device paths |
| `ps` | Process selectors, output fields and headers, sorting and display options; BSD `aux` / `ax` forms | `-n`, `-N`, `--namelist`; `-t` / `--tty` device paths |
| `lsof` | `-c` command patterns, `-d` descriptors, `-p` / `-u` selectors, bounded field, socket and numeric display forms | Positional paths, `+d` / `+D` directories, `-A` / `-k` / `-m` / `+m` source files, `-e` / `+e` paths and `-D` cache paths |
| `docker ps`, `docker container ls` / `ps` | Filters, output templates and display options | Explicit global configuration and TLS file paths, before or after the subcommand |
| `docker stats`, `docker container stats` | Container names, output templates and display options | The same global configuration and TLS file paths |
| `kb instance status` | Native KB command arguments | The existing trusted KB command contract applies |

Diagnostic exceptions require literal arguments without active parameter,
command, brace or pathname expansion. Quote a regular expression or template
that contains shell metacharacters. Unknown options and unsupported forms of
these diagnostics receive a refusal instead of a data exception. Other Docker
subcommands and cross-dialect `ps -C` / `-M` forms have no diagnostic exception.
Inline scripts and `xargs` retain their existing checks. Shell
redirections, active substitutions, executable paths and symbolic links retain
their file checks. The hook classifies knowledge-file access; a permitted
`pkill` operand does not authorize sending a signal.

The closed subset uses these dialect baselines:

- procps-ng [3.3.17](https://gitlab.com/procps-ng/procps/-/tree/v3.3.17)
  and [4.0.4](https://gitlab.com/procps-ng/procps/-/tree/v4.0.4) option tables,
  and the [upstream manuals](https://gitlab.com/procps-ng/procps/-/tree/master/man);
- the BSD-derived `pgrep`, `pkill` and `ps` manuals shipped with macOS 27.2
  and Apple's [process-tool sources](https://github.com/apple-oss-distributions/adv_cmds);
- the local lsof 4.91 manual and the upstream
  [lsof 4.99.0 manual](https://lsof.readthedocs.io/en/stable/manpage/);
- Docker CLI 29.9.2 `ps` / `stats` help and the
  [Docker CLI reference](https://docs.docker.com/reference/cli/docker/).

When extending a process grammar, inventory file options across the dialect
baselines and check every accepted long data or flag name against them.
`getopt_long` accepts unique prefixes: a name that is an exact data option in
one version can abbreviate a file option in another. Such names retain file
checks or stay unsupported. In procps-ng 3.3.17 and 4.0.4, `--pid` abbreviates
`--pidfile`; the guard checks it as a file operand on every version. Numeric
values such as `--pid 42` pass unless the possible file resolves to a protected
path; dynamic arguments remain refused.
Numeric file names retain path and symbolic-link checks; a numeric PID or
count is data only in a command position whose grammar identifies it as data.
Terminal selectors retain device-path checks for each comma-separated item,
including absolute paths and `/dev` lookup paths with parent traversal.
The regression invariant covers the accepted names and every long-file-option
prefix, in separate-value and `=` forms.

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

`make check` runs `kb bench --check` against the synchronized graph: every
question of `bench.toml` without `needs` must exit successfully, state its
required content, and fit its budget. The check omits the baselines, which run
external search tools, and lists each question that `needs` a capability
beyond the graph as not run, such as the decompilation that needs Ghidra and
the project of its image. `kb bench` answers every question and compares the
answers with the baselines; it runs where those capabilities are installed. A
change of knowledge that invalidates an expectation restates the question in
the same commit.
