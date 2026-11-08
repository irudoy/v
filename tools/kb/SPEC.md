# kb: knowledge model and entry point

This specification defines how the repository stores and serves what it knows
about the HR-series firmware, and `kb`, the tool through which people and
agents read and change that knowledge. It fixes the storage of symbols,
meanings, families, links, and evidence; names and references; layouts; the
compiler, the graph schema, and the graph fingerprint; per-worktree graph
instances; the `kb` commands and the MCP server; the gates; the projection
registry; current fact owners; and the access guard.

Knowledge representation transfer is complete. Current command and fact-owner
contracts live in `tools/kb/contracts.toml`; benchmark questions, their output
budgets, and content expectations live in `tools/kb/bench.toml`.

## 1. Model

- Knowledge is stored in git as small TOML files: one file per meaning and one
  per designed entity. Ledgers, address profiles, correspondence CSVs, native
  table registries, telemetry tables, and editor definitions are generated
  from those files.
- Three layers:
  - L0 is the machine extraction of each code layout from Ghidra: functions,
    calls, references, the instruction stream, and access censuses, with a
    provenance manifest.
  - L1 is knowledge about code: a symbol is a code object of one layout, and a
    meaning groups the homologous symbols of all layouts.
  - L2 is the project's features: stream fields, Map Switching, Rolling
    Launch, editor presentation, and the parity catalog of EcuTek and UpRev
    functions, declared through L1 names.
- Every symbol has one name. A meaning that has a semantic name gives it to
  all its symbols, and the layout qualifies each one. A symbol of an unnamed
  meaning carries a generated two-word name of its own.
- For every layout a meaning has either a symbol with evidence or a status.
  `absent` ("the mechanism does not exist") and `unresolved` ("the search
  bound no symbol") are stored with their evidence and search; `unknown` is
  computed for a layout that has neither a symbol nor a stored status.
- Strict homology holds inside a code family. A symbol of another family joins
  a meaning only with evidence on its own code; otherwise the relation is an
  `analog` hint that no gate reads.
- `kb` is the single entry point: one Python API behind a CLI and an MCP
  server. Reads, writes, and checks are commands; files are the storage
  format, not the interface. People browse knowledge in the ROM atlas.
- The compiler validates the files and loads them into Memgraph with MAGE.
  The `:Meta` node carries the fingerprint of the inputs, and every reader of
  the graph compares it with its working tree. Docker Desktop and Memgraph are
  a required environment of the project.
- Graph algorithms propose candidates for exploration: architecture blocks,
  subsystems of new layouts, homologs. Gates never read candidates.

Requirements the model meets:

- Every knowledge change is a git diff that passes the gates.
- A fact is declared once; every other occurrence is a projection whose inputs
  are fingerprinted.
- People and agents read and write through `kb`.
- Every symbol has a short unique name that can be used in discussion and
  resolved by a command.
- An edit of a project feature shows its insertion points on every layout and
  does not build over a gap or a contradiction.

Exclusions:

- `kb` has no blind mode.
- No language-model extraction and no fuzzy node merging produce facts. Graph
  structure is not semantics.
- graphify is not connected. [Commands](#12-commands) and
  [Access guard](#15-access-guard) list the mechanisms `kb` takes over from
  it.
- RomRaider XML, TunerPro XDF, RomRaider plugin files, and the host decoder
  stay generated files that anyone may read; `kb` does not replace them.

## 2. Terms

| Term | Definition |
|---|---|
| Image | A stock ROM dump registered in `rom-images/roms.csv` |
| Family | A code family of `rom-images/homology.toml` |
| Layout | The executable address space shared by the images of a family whose code is byte-identical; one layout per exact-code family and one per image otherwise |
| Symbol | A code object of one layout at one address: function, RAM cell, peripheral register, table, axis, constant, hook site, DID entry, or DTC record |
| Meaning | What a symbol is; it groups homologous symbols of different layouts and is the storage unit of L1 |
| Designed entity | A stage, block, endpoint, chain, signal, field, or feature; it is named by a chosen slug |
| Name | The semantic name of a meaning, the generated name of a symbol of an unnamed meaning, or the slug of a designed entity |
| Reference | Text that `kb` resolves to a meaning, a symbol, or a designed entity |
| Status | The per-layout state of a meaning that has no symbol there: `absent`, `unresolved`, or `unknown` |
| Link | A typed relation between meanings or symbols, stored at one end |
| Evidence | A typed record that supports a claim and points at L0, image bytes, a specification, a measurement, or an external source |
| Analog | A hint that a meaning of another family plays a similar role; it carries no evidence and no inheritance |
| Projection | A generated file with a declared generator, inputs, and consumers |
| Producer | The origin class of a graph element: `l0`, `claim`, `derived`, or `candidate` |
| Fingerprint | The hash of every compiler input and of the compiler version |

## 3. Layouts and families

`rom-images/homology.toml` stays the owner of families and gains the layouts
of each family:

| Layout | Family | Family kind | Images | L0 image |
|---|---|---|---|---|
| `7mfk` | `sh7058_7mfkavn86` | exact-code | JK00A, JK03A, JK03B, JK08A | JK08A |
| `jk00c` | `sh7058_8mfk` | near-code | JK00C | JK00C |
| `jk00d` | `sh7058_8mfk` | near-code | JK00D | JK00D |
| `jk78c` | `sh7058_jk78c` | distinct-code | JK78C | JK78C |
| `1nd` | `sh7059_1nd` | exact-code | 1ND0A, 1ND3B | 1ND0A |
| `1me3b` | `sh7059_1me3b` | distinct-code | 1ME3B | 1ME3B |

Each family declares `layouts` as an inline table from layout id to the image
whose export forms the layout's L0:

```toml
[family.sh7058_7mfkavn86]
layouts = { 7mfk = "JK08A" }

[family.sh7058_8mfk]
layouts = { jk00c = "JK00C", jk00d = "JK00D" }
```

- A family with `same_address_inheritance = true` has exactly one layout, and
  its L0 image is the family's canonical image. Every other family has one
  layout per member, and each layout's L0 image is that member.
  `tools/rom_homology.py --check` enforces both rules.
- A layout id matches `[0-9a-z]{2,8}` and never changes. Layout ids and kind
  names are disjoint.
- A symbol belongs to a layout. Calibration values belong to images: a table,
  axis, or constant symbol reads its values from each image of its layout.
- Canonical order of layouts is lexicographic by id.
- `kb family new` records a family with the census report of the new image as
  its evidence; `kb family add` adds an image to a family and, when the family
  does not inherit addresses, a layout. Both write `homology.toml` through its
  canonical writer (a comment-preserving TOML round trip) and then run
  `rom_homology.py --check`.

## 4. Storage

### 4.1 Tree

```text
kb/
  fn/ ram/ reg/ tbl/ axis/ const/ hook/ did/ dtc/   meanings, one file each
  stage/ block/ endpoint/ chain/                     architecture entities
  signal/ field/ feature/                            project features
  names.csv                                          symbol names of legacy registries
l0/
  <layout>/manifest.toml                             L0 provenance
  <layout>/*.csv                                     L0 extraction
tools/kb/
  SPEC.md  README.md  config.toml  bench.toml  projections.toml
  domain-words.txt  hook.py  and the package sources
.kb/                                                 ignored; per working tree
  instance.toml  lock  cache/  memgraph/
```

- `kb/names.csv` holds the generated names of symbols whose knowledge still
  lives in a legacy registry. Its columns are `layout,kind,address,name,former`,
  sorted by layout, kind, and address; `former` lists former names separated
  by spaces. `kb sync` draws the names of symbols that enter from a legacy
  registry without a semantic name and appends their rows. A row stays when
  the meaning of its symbol takes a semantic name, and its name then resolves
  as a former name. A symbol leaves `names.csv` in the conversion commit of
  its registry. The decoder-owned rows and exact inactive reservations remain
  primary names. `[names] owners_checked` requires every remaining
  row to have the SID 0x22 decoder as its only active declarer or an exact
  `[names] reserved` entry with its full row and a permanent-reservation reason.
- `.ignore` at the repository root lists `/kb/` and `/l0/`, anchored at the
  root so that `tools/kb/` stays searchable, and ripgrep-based search skips
  both trees.
- `.gitignore` lists `.kb/`.

### 4.2 File format

Entity files are TOML 1.0 in UTF-8 with LF line endings and a final newline.
The `kb` writer defines the canonical form, and `kb check` requires every file
to equal the canonical rendering of its own parse:

- Keys appear in the order of the schema in [Entities](#7-entities); absent
  optional keys are omitted, never written empty.
- Addresses are strings of eight lowercase hexadecimal digits, for example
  `"ffff102c"` and `"0003b75c"`.
- A string of up to 72 characters is a basic string on one line. A longer
  string is a multiline basic string that opens with `"""` and a newline and
  is wrapped greedily at word boundaries within 78 columns; every line but
  the last ends in a space and a backslash, so the value contains no
  newline. A paragraph break is a new array element.
- An array that does not fit in 78 columns puts one element per line, each
  followed by a comma.
- Integers are decimal, except DID numbers and offsets, which are
  hexadecimal with the `0x` prefix.
- Arrays of tables are sorted by the keys the schema names for them;
  symbols by layout and address.
- Files carry no comments, because comments are not data and the writer does
  not keep them.

### 4.3 File names

- A meaning is stored at `kb/<kind>/<name>.toml`, where `<name>` is its
  semantic name or, while it has none, the generated name of its symbol on
  the `home` layout, or of its only symbol.
- A designed entity is stored at `kb/<kind>/<slug>.toml`.
- A rename, or a change of `home` in an unnamed meaning, moves the file in
  the same write. A change of `home` moves the file to the generated name of
  the new home symbol and rewrites no reference: the former file name stays
  the generated name of a symbol of the meaning and keeps naming it.

## 5. Names and references

### 5.1 Name forms

| Form | Grammar | Used by |
|---|---|---|
| Semantic name | `[a-z][a-z0-9]*(_[a-z0-9]+)*`, 3 to 48 characters | meanings |
| Slug | the semantic-name grammar | designed entities |
| Generated name | `<adjective>-<noun>`, lowercase letters and one hyphen | symbols of unnamed meanings |

The underscore and the hyphen separate the two classes at a glance: a name
with an underscore or a single word carries meaning, a two-word hyphenated
name is a placeholder that says nothing about the symbol. Architecture ids
such as `crank-cam` become slugs such as `crank_cam` when the architecture
converts.

The `TIERS` constant and its comment in [`kb.model`](src/kb/model.py) own the
precedence of names contributed by entity files and registries.

### 5.2 References

The full reference of a symbol is `<name>/<kind>/<layout>-<address>`, for
example `normalized_bfs_snapshot/ram/7mfk-ffff102c` or, with a generated
name, `bouncing-badger/ram/7mfk-ffff1e38`. A meaning is `<name>/<kind>` and a
designed entity is `<slug>/<kind>`. Examples in this document use
illustrative names wherever no registry carries one yet.

`kb` prints full references and accepts, in this order of precedence:

1. a full reference; a name, kind, or address that disagrees with the store
   resolves to the current symbol and reports the reference as stale;
2. `<layout>:<address>`, the symbol at an address;
3. `<name>/<kind>/<layout>` or `<name>/<layout>`, the symbol of a meaning on a
   layout;
4. `<name>/<kind>` or `<name>`, a meaning, a designed entity, or the symbol
   that carries a generated name;
5. a former name or former reference, which resolves through its redirect and
   reports the current reference;
6. a bare address, which lists the symbols at that address on every layout.

An ambiguous input lists its candidates with kinds and layouts instead of
choosing one.

References stored in files take four forms: `<name>/<kind>` for a meaning
or a designed entity, `<name>/<kind>/<layout>` for a symbol,
`<layout>:<address>` for a location, which evidence uses in `at`, and
`<feature>.<allocation>` for RAM or ROM that a feature allocates, which each
target of the feature places ([Designed entities](#79-designed-entities)).
`kb rename`, `kb merge`, and `kb move` rewrite every stored reference they
affect.

Prose may cite entities as `[[<reference>]]`. `kb check` resolves every such
citation, and the same commands rewrite them. A bare address in prose is
plain text: in the prose of a meaning or a designed entity it refers to the
entity's `home` layout, in the prose of a symbol to the symbol's layout, and
in the note of an evidence item to the layout of its `at`.
`kb show` annotates bare addresses with the names of the symbols at them and,
for another layout, translates an address whose meaning has a symbol there.

### 5.3 Uniqueness

- A semantic name is unique within its kind.
- A generated name is unique across all kinds, and no semantic name or slug
  equals it.
- Former names and former references stay reserved permanently.
- At most one symbol exists per layout, kind, and address.

### 5.4 Generated names

- The source is the two-word slug generator of `coolname` (BSD-2-Clause),
  locked in `uv.lock`. It yields adjective and noun pairs whose words are
  lowercase letters without a hyphen.
- `kb` draws candidates with `random.SystemRandom`. No salt is used and no
  part of a name is derived from an address, so correcting an address never
  changes a name.
- `kb` rejects a candidate that:
  - equals a current or former name of any kind;
  - contains a word made only of the letters a to f, which reads as a
    hexadecimal value;
  - contains a word of the domain dictionary, which is the union of
    `tools/kb/domain-words.txt` and the words of semantic names, signal
    labels, and editor table names;
  - lies within Damerau-Levenshtein distance 2 of a current or former name.
- `kb` retries until a candidate passes and fails after the attempt limit in
  `tools/kb/config.toml`.
- A symbol receives a generated name when it enters the store without a
  semantic name: a new symbol of an unnamed meaning, or a symbol of a legacy
  registry that `kb sync` enrolls. The `names` check fails while
  such a symbol lacks its name.

### 5.5 Renames, merges, and moves

- `kb rename <meaning> <semantic-name>` names a meaning with a name that no
  other meaning of the kind holds as its name, another name, or a former name
  of it or of one of its symbols. The file takes the name; each entry drops
  its generated name and keeps its previous full reference as its first
  `former` reference; a previous semantic name becomes a former name of the
  meaning; and every reference and `[[...]]` citation of the entity files to
  a previous name names the new one, all in one write. The rename refuses a
  meaning with two files until `kb merge` joins them, and a meaning whose
  name a registry states until that registry converts, since the registry
  owns its facts until its conversion.
- `kb merge <a> <b>` joins two symbols at the same layout, kind, and address,
  or two meanings found to be one. The survivor keeps its name; the other name
  becomes a redirect.
- `kb move <symbol> <layout>:<address>` corrects the address of a symbol on
  its layout. The entry takes the address and the evidence of the candidate
  at it that the search of `kb.match` finds from the symbol on the layout of
  `--from` or from the home symbol, or the stated evidence; its previous full
  reference becomes its first `former` reference, and every reference and
  `[[...]]` citation of the entity files to that reference names the new one.
  The move refuses another layout, the home symbol as the start of its own
  search, and a location that holds a symbol of another meaning, which `kb
  merge` joins.
- `kb move <symbol> <meaning>` corrects a wrong homology. The entry of the
  symbol leaves the file of its meaning, or its row leaves `kb/names.csv`,
  and the symbol enters the file of the target with its keys besides its
  level and note; the `[[source]]` entries of its layout leave the file of
  the former meaning and join those of the target. The symbol takes the
  target meaning's name if it has one and keeps its generated name
  otherwise, which it draws when it has none;
  its previous full reference becomes its first `former` reference. The
  evidence is stated, or it is that of the candidate at the address of the
  symbol that the search of `kb.match` finds from the symbol of the target on
  the layout of `--from`, the symbol that the target reference names, or the
  home symbol of the target. Every reference and `[[...]]` citation of the
  entity files to the previous full reference, or to the symbol of the former
  meaning on its layout, names the symbol in the target, and a reference to
  its generated name names a named target. The move refuses a target with a
  symbol on the layout, the only symbol of a meaning, which `kb merge` joins,
  the home symbol of an unnamed meaning, which `kb rename` names first, and
  the layout of a stated `home`. A registry that states the symbol with its
  former meaning joins them again when the model compiles, and a name that a
  registry gives the symbol names the meaning that holds it; the move is
  refused with exit code 3 when the compiled model does not join the symbol
  with the target alone or changes the key of either meaning, until that
  registry converts.
- Two sessions that create the same symbol produce two names. The uniqueness
  gate on layout, kind, and address fails, and `kb merge` resolves it.

## 6. Kinds

| Kind | Layer | Address | Object |
|---|---|---|---|
| `fn` | L1 | ROM entry | Function |
| `ram` | L1 | RAM | RAM cell: byte, word, long word, or the byte holding a bit field |
| `reg` | L1 | MCU I/O | On-chip peripheral register or mailbox cell |
| `tbl` | L1 | ROM | Calibration datum read as data: table, curve, scalar, or flag byte |
| `axis` | L1 | ROM | Axis breakpoint array |
| `const` | L1 | ROM | Program datum outside calibration: literal word, pointer or jump table, record |
| `hook` | L1 | ROM | ROM word that a project feature redirects: a literal-pool entry or pointer slot |
| `did` | L1 | ROM | Service 0x22 pointer-table slot of one DID |
| `dtc` | L1 | ROM | DTC descriptor record |
| `stage` | L1, designed | none | Architecture stage |
| `block` | L1, designed | none | Functional block |
| `endpoint` | L1, designed | none | Actuator or bus endpoint of a block |
| `chain` | L1, designed | none | Calculation chain with ordered steps |
| `signal` | L2, designed | none | Observation need of tuning work and its coverage |
| `field` | L2, designed | none | Field of the telemetry stream |
| `feature` | L2, designed | none | Project feature or parity-catalog function |

`reg` holds the peripheral registers and HCAN mailbox cells that the JK08A
variable ledger carries next to RAM; a register meaning spans the layouts of
one MCU at the same address with the hardware manual as evidence. `signal`
belongs to L2 because it records what tuning work needs to observe and how the
stream covers it; the quantity itself is a `ram` meaning.

## 7. Entities

Tables in this section list keys in canonical order. A meaning file holds its
own keys, then its feature tables, then the arrays `[[symbol]]`, `[[status]]`,
`[[link]]`, and `[[analog]]`, in that order.

### 7.1 Levels

| Level | Meaning |
|---|---|
| `pattern` | The claim rests on resemblance only: shape, neighbourhood, or a name |
| `candidate` | A hypothesis that the code does not close |
| `code` | The claim follows from L0, image bytes, and reviewed code |
| `silicon` | The claim is confirmed on the owned ECU |

- Levels are ordered `pattern` < `candidate` < `code` < `silicon`.
- Claims with a level: the identity of a meaning (`level`) and of a symbol
  (`level`), a scale (`scale_level`), a contract (`contract_level`), a named
  bit or value, and a diagnostic binding. A symbol claims its identity or
  its scale when it states `level` or `scale_level`, and a symbol that the
  files own on another layout than the home of its meaning claims its
  identity at the `level` of the meaning. A claim of a meaning takes the
  evidence of its symbols that supports it, except homology evidence and the
  scale evidence of a symbol with a scale claim of its own; a symbol claim
  takes the evidence of its symbol, and its identity is grounded as the
  `homology` check grounds the symbol.
- A `candidate` claim needs at least one evidence item or dependency. A
  `code` claim needs grounding: evidence of a kind that grounds `code`
  ([Evidence](#76-evidence)), or a `relies` dependency on a claim with
  grounding or on a structure that the program holds; a dependency grounds
  no more than `code`. A `silicon` claim needs `hardware` evidence whose
  `key` names a record of `patches/hardware-results.toml` whose
  `hardware_status` is `pass`. A `hardware` item without such a record and
  an `arithmetic` item whose equation does not hold ground nothing.
- `relies` on a link or an evidence item names the property of its `to` end
  that the owning claim rests on:

| `relies` | Bound on the owning claim | Legacy suffix |
|---|---|---|
| `structure` | None when the program holds the `to` symbol as the code object the claim uses, `pattern` otherwise | `@structural` |
| `level` | The effective level of the `to` entity | `@confidence` |
| `contract` | The effective `contract_level` of the `to` function | `@contract_conf` |
| `scale` | The effective `scale_level` of the `to` entity | `@scale_conf` |

- The program holds a `fn` symbol that is a function entry of L0, and
  another symbol that an L0 reference names at an address of its storage,
  that typed `indirect` evidence places, or that the `source` link of a
  `did` symbol names in a DID table entry of the images. The facts of L0 and
  of the images are exact facts of the program that the ECU runs, so a held
  structure does not bound the claim.
- The `to` symbol of a link is the symbol of its `to` end on the home layout
  of the owning meaning, or else the home symbol of the `to` end; a `trace`
  item names its `to` symbol. `level`, `scale`, and `contract` name the
  claim of the `to` symbol when it states one, else the claim of its
  meaning, and a `to` end without that claim bounds at `pattern`.
- The effective level of a claim is the minimum of its declared level and
  the bounds of the links and evidence items of that claim that carry
  `relies`. Links and evidence without `relies` state facts and do not bound
  the claim. Mutual dependencies resolve to the greatest fixed point, so a
  cycle takes the minimum of its members.
- The `levels` check fails when a declared level exceeds its effective
  level, and names the dependency that bounds the claim and the end of the
  chain of such dependencies: a claim declared at that level, a `to` end
  without the claim, or a structure that the program does not hold.

### 7.2 Meanings

Keys of every meaning:

| Key | Type | Required | Content |
|---|---|---|---|
| `title` | string of at most 72 characters | yes | What the meaning is, in one line |
| `summary` | string | no | The mechanism: what produces the datum, what reads it, and how |
| `note` | array of strings | no | Caveats, open questions, and context the summary does not carry |
| `level` | level | yes | Level of the identity claim |
| `home` | layout id | when the meaning has more than one symbol and none on 7mfk | The layout of a symbol of the meaning that bare addresses in prose refer to; without it, a meaning with a 7mfk symbol takes 7mfk and a meaning with one symbol takes its layout |
| `role` | string | for `fn` and `tbl` | The role from the vocabulary of the kind |
| `block` | block reference | for reviewed `fn` meanings | The architecture block; other kinds may pin one |
| `former` | array of names | no | Former names, each a permanent redirect to this meaning |

Keys by kind:

| Kind | Key | Content |
|---|---|---|
| `ram`, `reg` | `width` | Access width in bits: 8, 16, or 32 |
| | `signed` | Two's complement when true |
| | `unit`, `scale`, `to_raw`, `scale_level` | [Scale](#scale) |
| | `[[bit]]` | Named bits of a bit field: `bit`, `name`, `summary`, `level`, and `[[bit.evidence]]`; the `[[bit]]` of a symbol replaces the bits of the meaning on its layout |
| | `[[value]]` | Named values of an enumeration: `value`, `name`, `summary`, `reachable`, `level`, and `[[value.evidence]]` |
| `tbl` | `access` | Lookup form: `explicit`, `implicit-2d`, `direct-scalar`, `direct-row-major`, `direct-indexed`, or `compare` |
| | `cols`, `rows` | Dimensions; a scalar or a flag byte is 1 by 1 |
| | `storage` | Element type: `uint8`, `int8`, `uint16`, `int16`, `uint32`, `int32`, or `float32` |
| | `unit`, `scale`, `to_raw`, `scale_level` | [Scale](#scale) |
| | `role` | `table`, `threshold`, or `dead` |
| `axis` | `quantity` | Quantity of the breakpoints, from the vocabulary in `tools/kb/config.toml`: `rpm`, `load`, `temp`, `raw`, and others |
| | `points`, `storage` | Number of breakpoints and element type |
| | `unit`, `scale`, `to_raw`, `scale_level` | [Scale](#scale) |
| `fn` | `role` | `accessor`, `service`, `driver`, `monitor`, `wrapper`, `dispatch`, `init`, `handler`, `selector`, `consumer`, `kernel`, or `finisher` |
| | `contract` | Inputs, outputs, and side effects in registers, RAM, and ROM |
| | `contract_level` | Level of the contract claim |
| | `[interp]` | Interpolation signature of a kernel or wrapper: `access` (`explicit` or `implicit`), `kernel` (a `fn` reference to the function that holds the kernel entry), `offset` (the distance of the kernel entry from the entry of `kernel`, when the entry lies inside it), `cols`, `rows`, `step`, `storage`, `x_storage`, and `y_storage` |
| `const` | `width`, `count`, `storage` | Element width in bits, element count, and element type |
| `hook` | `width` | Width of the redirected word in bits |
| `did` | `number` | DID number |
| | `width` | Response length in bytes |
| `dtc` | `code` | DTC code, such as `P0335` |
| | `group` | Descriptor group, such as `misfire` |
| | `disabled` | The attribute value that disables the DTC |

A `[[value]]` with `reachable = false` names a value that no writer stores;
it needs evidence. A `dtc` symbol carries `index`, the position of its record
in the descriptor table, and `attribute`, the address of its attribute word,
because both differ by layout.

#### Scale

- `scale` is an expression in `x`, the raw value, in the expression grammar
  of the editor definitions: numbers, `x`, `+`, `-`, `*`, `/`, and
  parentheses. `to_raw` is its inverse, and `unit` names the engineering unit.
- `scale_level` is the level of the scale claim; it can be lower than the
  identity `level`. A `code` scale needs grounding evidence with
  `supports = "scale"`.
- A field of the telemetry stream that reads the meaning uses this scale; a
  field never restates it ([Designed entities](#79-designed-entities)).

### 7.3 Symbols

| Key | Content |
|---|---|
| `layout` | Layout id |
| `address` | Eight lowercase hexadecimal digits |
| `name` | Generated name; present only in a meaning without a semantic name |
| `level` | Level of the claim that this symbol is the meaning on its layout; defaults to the meaning's `level` |
| `former` | Former full references of the symbol |
| `images` | Images of the layout that the symbol applies to, when not all |
| Overrides | `width`, `signed`, `storage`, `cols`, `rows`, `points`, `count`, `quantity`, `unit`, `scale`, `to_raw`, `scale_level`, `summary`, `[interp]`, `[editor]`, and `[[bit]]` where the layout differs from the meaning; for `dtc`, `index` and `attribute` |
| `note` | Prose about this layout |
| `[[symbol.evidence]]` | Evidence of identity or homology |

- An anchor symbol carries evidence with `supports = "identity"` of a kind
  that grounds its level on its own layout, or its meaning has a link with
  `relies` that holds on the layout through evidence of that layout.
- A file-owned symbol with an explicitly declared identity `level = "candidate"`
  needs no anchor. Its evidence, named bits, and claim levels satisfy their
  checks.
- Every other file-owned symbol is an anchor or carries evidence with
  `supports = "homology"` whose `to` names a symbol of the same meaning, or
  the location on the layout of such a symbol that the evidence compares
  with `at`. The homology chain of such a symbol reaches an anchor.
- Homology evidence is `masked-match`, `literal-pool`, `function-match`,
  `call-ordinal`, `interp-contract`, `did-table`, or `byte-identical`
  evidence, `l0` evidence of the symbol's own layout, or `manual` evidence
  for a place that the MCU sets, such as a register or a slot of the vector
  table: the symbol and its counterpart lie at one address, and the
  counterpart cites the same key of the MCU hardware manual as identity
  evidence. The same kinds apply inside a family and across families, and a
  match that is not unique grounds no more than `candidate`. `vendor`,
  `registry`, and `diagnostic` evidence never supports homology, and name,
  neighbourhood, or graph similarity is not evidence.
- A symbol stores no calibration values. The image catalog fixes the bytes of
  every image, and `kb show` reads the values from them.

### 7.4 Statuses

| Key | Content |
|---|---|
| `layout` | Layout id |
| `state` | `absent` or `unresolved` |
| `method` | For `unresolved`: the evidence kind of the search, such as `masked-match` |
| `target` | For `unresolved`: what the search looked for, as a reference or a location |
| `count` | For `unresolved`: the number of matches; 0 for none, 1 for one candidate that cannot be bound, more than 1 for an ambiguous search |
| `candidate` | For `unresolved` with `count` 1: the location of the candidate on the layout |
| `l0` | For `unresolved`: the first 16 hexadecimal digits of the SHA-256 of the layout's L0 manifest at search time |
| `note` | Prose |
| `[[status.evidence]]` | Required for `absent` |

- A layout carries at most one symbol or one status of a meaning.
- `absent` states that the mechanism does not exist on the layout. Its
  evidence comes from the layout's own code, for example a DID table without
  the DID or a producer path that the code lacks.
- `unresolved` states that a search bound no symbol: it found none, more
  than one, or one candidate that cannot be bound. A status of one candidate
  locates it as `candidate`, and its `note` states why it is not bound:
  `kb bind` refuses the location, or the identity of the candidate is not
  established. When the L0 manifest of the layout changes, the search is
  stale: `kb brief` lists it, and staleness is not a check failure.
- `unknown` is computed for a layout without a symbol or a status of a
  required meaning. A meaning is required on a layout when a feature that
  targets the layout requires it, directly or through a field, or when the
  meaning has a symbol on another layout of the same family.

### 7.5 Links

A link is stored at one end and read in both directions.

| Key | Content |
|---|---|
| `type` | Link type |
| `to` | Reference to a meaning or a designed entity |
| `slot` | `x` or `y` for `index` and `axis`; `bit0` to `bit31` for a `selector` or `threshold` whose `to` is a bit field |
| `offset` | Offset for `base` and `target`; for `source`, the position in the response of the byte that `to` supplies, when a DID assembles its response from single bytes |
| `via` | Array of `fn` references that carry the relation |
| `layouts` | Array of layout ids that restricts materialization |
| `relies` | The property of `to` that the owning claim rests on |
| `supports` | The claim of the owning meaning that `relies` bounds: `identity` (the default), `scale`, or `contract` |
| `reverse_relies` | The property of the owning meaning that the claim of `to` rests on, for a relation that the legacy registries state at both ends |
| `reverse_supports` | The claim of `to` that `reverse_relies` bounds, with the values of `supports` |
| `role` | The legacy token role; required on `depends` |
| `note` | Prose |
| `[[link.evidence]]` | Evidence of the relation |

| Type | Stored at | `to` | Meaning | Verified by |
|---|---|---|---|---|
| `writer` | `ram`, `reg` | `fn` | The function writes the datum | L0: a store access |
| `reader` | `ram`, `reg`, `tbl`, `axis`, `const` | `fn` | The function reads the datum | L0: a load access or a literal reference |
| `input` | `ram`, `reg` | datum | The datum is computed from `to` | Evidence |
| `copy` | `ram`, `reg` | `ram`, `reg` | The datum is a copy of `to`, made by `via` | Evidence |
| `index` | `tbl`, `axis` | `ram`, `reg` | `to` is the coordinate `slot` of the lookup | L0: the accessor census |
| `axis` | `tbl` | `axis` | `to` is the axis of `slot` | L0: the accessor census or the lookup header |
| `lookup` | `ram`, `reg` | `tbl` | The datum is the output of a lookup of `to` | Evidence |
| `selector` | datum or `fn` | datum or `fn` | The value of `to`, or its function result, selects between alternatives | Evidence |
| `threshold` | datum or `fn` | `tbl`, `ram` | The datum or function compares with `to` | Evidence |
| `base` | `ram` | `ram` | The datum is addressed at `offset` from `to` | `indirect` evidence |
| `target` | `hook` | `fn`, `tbl`, `const` | The stock word points at `to`, plus `offset` | Image bytes of every image of the layout |
| `source` | `did` | `ram`, `reg`, `tbl`, `const` | The DID returns `to` | Image bytes: the DID table entry |
| `monitor` | `dtc` | `fn` | `to` sets the DTC | Evidence |
| `depends` | any | any | An untyped dependency with its legacy `role` | Evidence |

- A link claims every layout where both ends have symbols, unless `layouts`
  restricts it.
- The stated layouts of a link are the layouts of its evidence locations and
  of `layouts`; a link with neither states the layout of its owning symbol or
  the home of its meaning. `kb link` and the join of two links in `kb merge`
  extend `layouts`, where the link has it, to the layouts of its evidence, so
  that `layouts` lists every stated layout. Several entries of one link join
  their `layouts` in their order, and the `links` check fails on a link whose
  evidence lies outside its `layouts`.
- Entries of one link that both carry and lack `layouts`, in one file or in a
  file and a registry, lift into one link restricted to the union of the
  listed layouts: an entry without `layouts` claims no other layout. The
  `links` check notes such a link without failing. An unrestricted claim
  leaves `layouts` off every entry of its link, and a restriction states it
  on every entry. The writer makes no such entries: `kb link` refuses
  `layouts` for a held link without them, and a rewrite of `kb merge` or
  `kb rename` that makes such entries entries of one link is refused, also
  when their other keys differ. A `kb set-link` earlier in the batch states
  or removes the restriction.
- A `selector` whose `to` is a function states the result condition in its
  note and has no `slot`; bit slots describe a datum, not a return register.
- On each claimed layout a link holds when its verifier reproduces it, when
  an `indirect` evidence item of that layout explains the access, or, for a
  type that evidence verifies, when evidence of that layout supports it or
  the link holds on another layout of the same family.
- A link that does not hold on a claimed layout is unverified there. `kb
  show` marks it, and the `links` check fails on it.
- A link states a dependency of its owner on `to`, except that the function
  of a `reader` depends on the datum, and a `depends` link reads by its role:
  with `consumer` or `writes`, `to` depends on the owner; `homolog` and
  `match` state no dependency. `kb impact` and `kb path` follow dependencies
  from what a change starts at to what it reaches.

### 7.6 Evidence

| Key | Content |
|---|---|
| `kind` | Evidence kind |
| `supports` | `identity`, `homology`, `scale`, `contract`, or `role`; `role` covers the `role` key, bits, and values |
| `at` | A location, `<layout>:<address>` |
| `to` | A reference |
| `relies` | [Levels](#71-levels) |
| `count` | Number of matches: for `masked-match` and `function-match`, the occurrences of the words or of the hash on the layout of `at` times those on the layout of `to`; for `call-ordinal`, the addresses that the call at `to` relates in the way that the call at `at` relates the symbol |
| `value` | The observed value: bytes, a literal, an ordinal, a hash class, or an equation |
| `sha256` | Digest of compared bytes |
| `mode` | For `indirect`: `pointer`, `gbr`, `window`, `block-copy`, `snapshot-copy`, `coherent-copy`, `did-pointer`, `diagnostic-output`, `arithmetic-argument`, `calculation-dependency`, `arithmetic-factor`, `io-access`, `maf-access`, `ram-clear-access`, `counter-array-access`, `phase-normalization-access`, `learning-transfer-access`, `bank-pulse-access`, `knock-access`, `closed-loop-admission-access`, `closed-loop-coordinate-access`, `rpm-inhibit-access`, `snapshot-output`, or `base` |
| `path` | A repository path |
| `key` | An identifier inside `path`, a source pack, or a registry |
| `note` | Prose |

| Kind | Content | Required keys | Grounds up to |
|---|---|---|---|
| `l0` | An access, call, or reference of L0 at `at` | `at` | `code` |
| `literal-pool` | The pool literal at `at`, which is `value` and the address of the symbol, and the literal at the location `to`, the address of the counterpart; a load of the pool at `at` aligns with a load of the pool at `to`, or has the ordinal of such a load in a homologous function | `at`, `to`, `value` | `code` |
| `masked-match` | The `value` masked instruction words from `at` equal those from the location `to`; `value` reaches `[match] words` of `tools/kb/config.toml`, and an instruction at one offset of both runs relates the symbol and its counterpart | `at`, `to`, `count`, `value` | `code` when `count` is 1 |
| `function-match` | Equal exact, mnemonic, or shape hash of the L0 functions at `at` and `to`; `value` names the hash class. The functions are the symbol and its counterpart, or, for a datum, have one length and an instruction pair at one ordinal that relates the symbol and its counterpart | `at`, `to`, `count`, `value` | `code` when `count` is 1 |
| `call-ordinal` | The calls at `at` and at the location `to` are the call `value` of homologous functions and relate the symbol and its counterpart in the same way | `at`, `to`, `count`, `value` | `code` when `count` is 1 |
| `interp-contract` | Two functions with one interpolation contract, and a location `to` is the entry of the counterpart. For two wrappers, `key` is the entry of the counterpart, the `[interp]` keys `access`, `offset`, `cols`, `rows`, `step`, `storage`, `x_storage`, and `y_storage` agree, and the L0 body of each wrapper calls the entry of its kernel unless the wrapper is its own kernel. For two kernels, `key` is the kernel entry on the layout of the counterpart that a wrapper of one meaning calls there, while that wrapper's symbol on the layout of the symbol calls its own kernel entry | `to`, `key` | `code` |
| `did-table` | The DID's slot in the service pointer table of the image | `at`, `value` | `code` |
| `byte-identical` | Identical bytes over positive, complete ROM ranges: the exact hash of two L0 functions, or equal-sized data storage on every applicable image | `at`, `to`, `sha256` | `code` |
| `rom-bytes` | Bytes of every image of the layout at `at` | `at`, `value` | `code` |
| `unbound-constant` | A retained legacy constant without a verified address and byte binding | `value` | none |
| `unverified-site` | A retained legacy site whose code relationship is not reproduced | `at` | none |
| `l0-context` | A reviewed site's reproducible structured context: `key` is `reference`, `body`, `pointer`, or `linked`, and `value` holds the subject's `span` and optional `named` addresses | `at`, `key`, `value` | `code` |
| `trace` | The claim follows through the contract or behavior of a function | `to`, `relies` | `code` |
| `indirect` | An access that L0 does not attribute directly; mode `base` verifies only that the instruction or pool literal at `at` references the symbol's address minus `value`, not the complete indexing or copy path | `at`, `mode` | `code` |
| `spec` | A narrow specification of the repository, a decoding rule, or a published standard | `path` or `key` | `code` |
| `arithmetic` | An equation that `kb check` evaluates | `value` | `code` |
| `test` | The Python file `path` of the repository defines the test function `key`; verification checks its AST definition and does not execute the test | `path`, `key` | `code` |
| `manual` | A vehicle or MCU manual of the source packs; a key with a prefix of `[manual] mcu` of `tools/kb/config.toml` cites the MCU hardware manual | `key` | `candidate`; `code` for the identity of a `reg` meaning from the MCU hardware manual |
| `diagnostic` | A record of the diagnostic corpora | `key` | `candidate` |
| `registry` | A legacy or vendor definition entry | `value` or `path` | `candidate` |
| `vendor` | A competitor product or catalog | `key` | `candidate` |
| `hardware` | A measurement on the owned ECU | `key` | `silicon` when the record of `patches/hardware-results.toml` passes |

- Evidence of one layout names locations of that layout; homology evidence
  names the other symbol in `to`.
- A byte-identity comparison requires an applicable ROM image on both sides
  and a positive range wholly inside every such image. Both ranges pass this
  check before their hashes are compared. RAM identities use reviewed `l0`
  access/address evidence.
- Masking clears the operand bits that encode an address the layouts place
  differently: the displacements of PC-relative loads, of `mova`, of
  branches, and of GBR accesses. A region is a maximal run of equal masked
  words through an instruction of each layout; it matches when its words
  occur once on each layout, and an instruction aligns when one region of
  at least `[match] words` matches and no other region of it is as long.
- Two instructions relate the symbol and its counterpart in the same way when
  they touch them as the address of a load, a store, or an update through a
  base register that holds a pool literal on every path, as the literal of a
  PC-relative load, as the target of a call, or as one operand of a census
  call. Homologous functions are the symbols of one `fn` meaning or two
  functions whose hash of one class is unique on both layouts.
- The `levels` check evaluates every `arithmetic` equation
  `<expression>=<number>`: the expression of numbers, `+`, `-`, `*`, `/`,
  `^` with an integer exponent, and parentheses, evaluated exactly, rounds
  to the number at the decimal places that the number states. The
  `image-bytes` check compares every typed `rom-bytes` value with the images
  of the layout.
- An `indirect` base item places a datum or a slot that no instruction
  touches: at the first load of VBR when the symbol lies in the vector table
  that VBR bases, else at the first instruction that touches the nearest
  address below the symbol, within `[match] base` bytes, as a literal, an
  access, or a census operand.
- An `l0` item cites the instruction that produces the address. A census
  operand counts at its call when data flow describes it, or, with the `sp`
  kind of symbolic propagation or the `copy` kind of a copy-helper match, at
  a complete delayed call, whose slot the export evaluates before the callee
  starts; backtrack columns never count. A
  Ghidra reference on the delay slot of any delayed transfer, `bt/s` and
  `bf/s` included, that derives its register from registers alone, by a copy,
  a register sum or difference, an extension, or a shift, counts at a site at
  a lower address of the same body that names the same address: an
  instruction outside such slots or a census operand of a call. With no site
  of those kinds at a lower address, the reference of the slot counts; a
  register sum, an extension, or a shift there computes a new value. An immediate addition in a slot always produces a new
  address, and its reference counts.
- An `l0-context` item reproduces its recorded classification on current L0
  and image bytes. Its span is positive and does not exceed the table's
  storage, or is one byte for another kind. The footprint grants no physical
  unit or conversion; every supported claim requires the recorded
  classification to hold. `unbound-constant` and `unverified-site` items
  retain source assertions without grounding a level.
- Historical stock-proof evidence remains data. Its archived file references use
  `git:archive/stock-proofs-2026-10-26:<repository-path>[#fragment]`.
  Archived TEST items and TEST items without `supports` provide no grounding.
  Ordinary reads and writes do not import or execute the archived implementation.

### 7.7 Analogs

`[[analog]]` records that a meaning of another family plays a similar role:

| Key | Content |
|---|---|
| `to` | Reference to a meaning of another family |
| `note` | Required: what is similar and what differs |

An analog carries no evidence, no level, and no inheritance. Gates never read
analogs. `kb show` and the atlas show them, and `kb suggest` may start a
search from them.

### 7.8 Feature tables in meanings

Presentation and diagnostic bindings are L2 data stored in the meaning they
describe, so a rename or a move carries them:

| Table | On | Keys |
|---|---|---|
| `[editor]` | `tbl`, `axis`, `const` | `name`, `category`, `order`, `emit`, `format`, `fine`, `coarse`, `mask`, `constant_content`, `static_axis`, `static_axis_name`, `static_axis_operand`, `static_axis_x`, `static_axis_x_name`, `static_axis_y`, `static_axis_y_name` |
| `[[editor.view]]` | `tbl`, `const` | A masked view: `name`, `category`, `mask`, `unit`, `scale`, `to_raw`, `format`, `fine`, `coarse` |
| `[logparam]` | `ram`, `reg` | RomRaider logger parameter: `id`, `unit`, `scale`, `static_axis_name` |
| `[[diagnostic]]` | any meaning | Diagnostic binding: `id`, `kind`, `label`, `key`, `claim` (an inline table of `label` and `id`), `applicability`, `scope` (image or layout ids), `priority`, `level`, `note`, and `[[diagnostic.evidence]]` |
| `[[ledger]]` | a meaning with a legacy row | View selectors: `registry`, `order`, selected `fields`, `notes` indices, evidence indices for `identity`, `contract`, and `scale`; optional diagnostic `binding`, curated `title` or former `name`, and `storage_description` |
| `[[ledger.dependency]]` | a ledger view | A selected canonical link: token `role`, meaning `to`, link `type`, claiming `end`, optional `link_role`, `relies`, `supports`, and optional numeric `offset` with its `offset_text` spelling |
| `[[ledger.offset]]` | a ledger view | The selected indirect `evidence` index and its numeric offset spelling in `text` |
| `[[source]]` | any meaning | Specification anchor: `path` of a narrow specification, its `sha256` when the anchor was bound, the `sections` and the `anchor` that state the meaning, an optional `role`, and the `layout` whose symbol the anchor states; an entry without `layout` states the meaning on every layout |

`editor.name` is the name the editors show; it is not the name of the
meaning. `editor.static_axis_operand` is a reference to the `ram` or `reg`
meaning whose value the static axis labels. `editor.constant_content = true`
marks a native VQ37 table whose stock cells may all hold one bits as a
reviewed calibration value; the native table registry rejects such a block
of an unmarked table as erased flash. That registry covers the VQ37VHR images
and, for the target-native tables that their relocated JK08A definition cannot
state, the 8MFK images JK00C and JK00D. The role set of each family, VQ37VHR
or 8MFK, is the union of the roles that its images carry: every image of the
family carries each role of that set or declares it absent with a reason, and
an absence outside that set is stale. The generators of the editor
definitions, the RomRaider files, and the diagnostic bindings read these
tables.

Ledger selectors reproduce column presence and row order without owning a
second copy of semantic facts. Dependencies require the selected type,
direction, layout, offset, role, and claim to hold; evidence and note indices
are unique nonnegative integers. An offset spelling must equal the selected
numeric value. A curated name selects the current or a former name, and a
storage description does not supply a semantic unit.

`kb unlink` removes the dependency selectors of the removed link at both
claiming ends and the accessor column when it removes that accessor. The
`kb select` command selects one existing native relation and claim in an
existing owned ledger row, identified by exact `registry` and `order`.
It neither creates a row nor changes its other selectors or facts. The
`ledgers` check rejects selectors whose facts or indices no longer hold,
including in a planned write. New evidence, columns, and notes enter a view
when its selectors explicitly select them.

### 7.9 Designed entities

| Kind | Keys |
|---|---|
| `stage` | `title`, `lane` (`flow` or `support`), `order`, `summary` |
| `block` | `title`, `stage`, `summary`, `generic` (a service block that no single stage owns), `specs`, `home`, `order` |
| `endpoint` | `title`, `direction` (`input`, `output`, or `bidirectional`), `block`, `peripheral`, `summary`, `registers` (`reg` references), `functions` (`fn` references), `specs`, `order` |
| `chain` | `title`, `summary`, `quantity`, `output`, `specs`, `home`, `order`, and `[[step]]` |
| `signal` | `title`, `domain`, `priority`, `coverage`, `basis`, `observes`, `note` |
| `field` | `signal`, `source`, `origin`, `width`, `signed`, `scale`, `profiles`, `page`, `offset`, `context`, `position`, and `[dashboard]` |
| `feature` | `title`, `summary`, `specs`, `acceptance`, `requires`, `vendor`, and `[[target]]` |

`specs` is an array of repository paths of narrow specifications.

Architecture entities retain their array position from 1 as `order`. It
preserves block voting and display order; stage order places the columns.

Blocks:

- A `fn` meaning joins a block through its `block` key; a `ram`, `tbl`, or
  other meaning may pin a block with the same key.

Chains:

- `[[step]]` keys: `from`, `to`, `effect`, `sign` (`positive`, `negative`,
  or `none`), `via` (an array of `fn` references), `note`, `specs`, and
  an optional `[step.research]` source record.
  Steps are ordered by their position in the array.
- `effect` is one of `scales`, `looks-up`, `indexes`, `converts`, `adds`,
  `multiplies`, `selects`, `compares`, `subtracts`, `copies`, `gates`,
  `limits`, `stores`, `filters`, `feeds`, `integrates`, `schedules`,
  `receives`, `overrides`, `masks`, `drives`, `detects`, `transmits`, or
  `learns`.
- A step `note` states only the arithmetic that relates `to` to `from`.
  Conditions and alternatives are links of the meanings (`selector`, `copy`,
  `threshold`), so queries reach them.
  `[chains.arithmetic]` of `tools/kb/config.toml` declares address, number,
  and name tokens; initially available variables; memory readers; unary
  operators; binary operators in increasing precedence; and the exact arity
  of each arithmetic function. A note holds equations separated by `;`.
  An equation assigns an address or a variable to an expression; `=` may
  continue with an equivalent expression. A temporary variable is available
  after its equation, within that note. Expressions admit numeric constants,
  addresses, available variables, indexed reads, configured functions and
  operators, and parentheses. Text conditions, comparisons, units, unknown
  variables, and malformed expressions fail. Syntax grants no evidence or
  claim level and does not evaluate an equation.
  `kb audit --section chain-notes` reports
  rejected notes with their exact text and step binding. A write refuses a
  new rejection, including a change to a held note, its ends, ordered calls,
  effect, or sign. The mandatory `chains` gate enforces the configured
  arithmetic grammar for every present note.
- `[step.research]` preserves an unresolved original prose statement outside
  the arithmetic note. Its state is `unresolved`, not a layout search status
  or a claim level. It contains `source_commit` (the complete immutable Git
  commit), `source_path` (the same owning chain), `source_sha256`, `order`,
  `step_sha256`, and `original` (canonical JSON of every original step field).
  The source bytes, exact original text, ordered references, repeated calls,
  effect, sign and specifications must agree with that historical source.
  The current step preserves every original field except its prose `note`,
  which the complete source record retains. The writer refuses removal or
  modification of an existing unresolved record, including whole-array
  replacement. Transfer provides no arithmetic or executable proof, typed
  condition, physical identity, claim-level promotion or hardware readiness.
  Deferred semantic review remains separately counted and source-bound.
  Layout symbols and absent/unresolved search statuses retain their own
  meanings; an unreviewed text does not create a search status.
- `output` is a reference to the meaning the chain computes.

Signals:

- `priority` is `core`, `high`, `medium`, or `research`; `coverage` is
  `fixed`, `rotating`, `latched`, `stock-can`, `external`, or `absent`;
  `basis` is `exact-code`, `exact-code+homologous-diagnostic`,
  `measurement-requirement`, `passive-can`, or `patch-design`.
- `observes` is an array of meaning references and allocation references,
  in the order in which the catalog lists the sources: an observed address
  inside the RAM that a feature allocates is the allocation of that feature
  at the address and width. The DIDs of a signal
  come from the `did` meanings whose `source` is an observed meaning, and its
  current fields from the fields whose `signal` names it; neither is stored.

Fields:

- `origin` is `ecu_ram`, `rom_configuration`, `runtime_state`, or
  `telemetry_state`: where the value of the field lives. The key is not
  `kind`, which names the kind of every entity.
- `signal` names the signal that the field serves. An `ecu_ram` field
  requires it; a field of another origin may carry it.
- The `source` of an `ecu_ram` field is a `ram` or `reg` meaning, and the
  field takes its scale and unit from that meaning. The source of a field of
  another origin is an allocation, named after the field without the `_raw`
  suffix, of the feature that owns its address: the configuration record of
  `can_telemetry` for `rom_configuration`, the state record of
  `can_telemetry` for `telemetry_state`, and the active RAM of
  `map_switching` or `rolling_launch` for `runtime_state`. A field of another
  origin carries `scale`; an `ecu_ram` field carries no semantic scale,
  and the profile renders the scale, the values, or the named bits of its source meaning
  ([telemetry profile projection](src/kb/adapters/telemetry.py)).
- A numeric source file owns its unit, including its absence; the legacy
  RAM ledger does not supply a replacement. Enumerations and bit fields
  without a file unit retain the ledger's storage description. If no unit,
  scale, values, or named bits are established, the profile presents
  `raw count` with identity conversion. This host storage view does not
  assert semantic scale keys or evidence, including when the profile
  converts again. An `ecu_ram` field may explicitly carry `scale = "raw count"`
  to expose the stored word while preserving an unresolved native unit or
  conversion. Every other field-local scale is forbidden. A partial or unrenderable
  conversion refuses projection.
- `width`, in bytes, and `signed` describe the field on the wire. On every
  layout that a feature requiring the field targets, the `widths` check
  requires the width to fit the symbol that the field reads there, and the
  `fields` check requires `signed` to agree with the `signed` that the
  symbol states.
- `profiles`, `page`, and `offset` place a stream field; `context` and
  `position` place a context field.
- `[dashboard]` is the host presentation of the field: `label`, the name of
  its recorded channel and of its row; `digits`; `group`, the category of
  the recorded channel; and optionally `description`, the text shown over the
  name; `unit`, for a value whose scale states no unit; `hexadecimal`;
  `panel` with `order`, the panel of the dashboard that shows the field and
  its position there, and `panel_label`, the name of the row where it
  differs from `label`; and `[dashboard.feed]` with `key`, `name`, `format`,
  `minimum`, `maximum`, and `step`, the channel of the live feed that
  publishes the value. The unit, the conversion, and the names of the values
  and bits come from the scale, and a feed channel publishes a conversion.
  A field without `[dashboard]` is recorded under its name and stays off
  the panels.

Features:

- `summary` states what the feature does, and `specs` names the
  specifications that state how it works and the observable criterion that
  it works. A feature without a specification in the repository, such as a
  competitor function of the parity catalog, states that criterion in
  `acceptance`. `requires` lists the meanings and designed entities it needs
  on every target layout; `vendor` lists the competitor products that offer
  it, for the parity catalog.
- `[[target]]` keys: `layout`, `status` (`supported`, `planned`, or
  `unsupported`), `note`, `basis`, `requires`, `unsupported`, and the keys of the feature.
  An `unsupported` target names in `note` the meanings whose status blocks
  it; `basis` holds the prose of the review behind the target by topic.
  `requires` of a target lists the meanings that the feature needs on its
  layout beyond those that its key tables, roles, and hooks name.
  `REQUIRES` carries all of them with the layouts of the targets that name
  them, and `kb gaps` reports those unavailable there: a meaning without a
  symbol, except the source of a field whose role a symbol of the target
  fills, and the source of a field that the target lists as `unsupported`.
- `families` (`map_switching`) and `symbols` are tables of the keys of the
  patch build, whose entries name the meaning of each key on the layout of
  the target; a role key enters `roles` instead. `variants` lists the
  symbols that a build variant selects with the variant, and `unsupported`
  the meanings of the feature that the layout does not support, each with a
  `note`; a meaning that has no symbol on the layout also carries a status
  there.
  A telemetry target can mark a source role `unsupported` while its native
  symbol exists, for example when its bit layout requires an unimplemented
  wire conversion. Numeric profiles, correspondence rows, and the support
  matrix keep that field unavailable without discarding its native binding.
- The `runtime` feature holds the runtime allocation of each layout, its
  ROM and RAM relocation, and the build variants, with the prose of a bound
  in `notes`; its `7mfk` target holds the envelope that the other layouts
  relocate. `can_telemetry` holds the wire constants, profiles, contexts,
  and the catalog keys `telemetry_profile`, `full_rate_hz`, and
  `rotating_divisor`; its targets hold the telemetry mailbox, its mask, and the
  payload offset of the feedback record, with the prose of each in `notes`,
  and its `7mfk` target the addresses of the capture table, the
  configuration record, and the state record. `can_telemetry` requires every
  field; its `requires` is derived from the field files, not stored.
  A field is unavailable on a layout where its source meaning has a status
  and no symbol fills the role of the field; the list of those fields is
  derived, not stored.
  `definitions` holds `default_emit` and the switches of the editor
  definitions, each with its position among the switches as `order`, and
  each of its targets holds in `images` the header metadata,
  checksums, switch addresses, exposed features, prose (`note`), and the
  basis of the review (`basis`) of each image with a definition, in
  `requires` the meanings whose tables and axes the definition of the layout
  relocates, in `variants` the symbols that a variant of the definition
  selects with the variant, and in `omitted` the symbols that the definition
  leaves out with the reason.
- `map_switching`, `rolling_launch`, and `can_telemetry` hold their layout
  keys and, under their own hook keys, the `hook` meanings they redirect with
  the replacement of each. The build applies them in that order, so the value
  of a word before a feature redirects it is the replacement of the last
  earlier feature that redirects the same word, or the stock value; it is
  derived, not stored. The prose of the first feature that redirects a word
  belongs to the `hook` symbol, and the prose of a later feature is the
  `note` of its hook key.
- RAM and ROM that a feature allocates are not meanings. Each target lists
  them in `allocations`, a table of allocation names whose entries hold the
  `address` and the `width` in bytes on the layout of the target, and fields
  and signals refer to them as `<feature>.<allocation>`. Allocations of one
  target may overlap, as a DID word and the bytes that telemetry fields read
  from it do.
- A feature key that names a meaning may take on a layout a symbol of another
  meaning, which fills the role of the key there. The target of that layout
  lists such keys in `roles`, a table of key names whose entries hold the
  `symbol` and a `note`; the symbol keeps its own meaning, and the key names
  no symbol on that layout. On the VQ37VHR layouts the state byte of the
  native rev-limit fuel cut, a meaning of its own, fills the role of the fuel
  inhibit state, whose named bit `active` the rolling launch reports, and the
  final six-cylinder inhibit mask that the rolling launch extends there is a
  key of its own. A register is physical:
  a key whose register lies at another address on a layout than on `7mfk`
  takes there the meaning of that register in its role. A telemetry field
  reads on a layout the cell that the consumers there take: a cell of another
  meaning than the source of the field fills the role of the field, as the
  `jk78c` Fuel Compensation surfaces take their column from a snapshot of a
  producer of their own while the homolog of the `7mfk` coordinate indexes
  another surface.
- An address in a target key takes the form of a symbol address; sizes,
  deltas, masks, and indices stay numbers.

## 8. L0

L0 is the machine extraction of one layout, stored in `l0/<layout>/` and
exported from the Ghidra program of the layout's L0 image.

### 8.1 Files

| File | Columns | Content |
|---|---|---|
| `manifest.toml` | | Provenance ([Manifest](#83-manifest)) |
| `funcs.csv` | `addr,size,is_thunk,is_external` | Function entries |
| `calls.csv` | `src,dst` | Call edges |
| `xrefs.csv` | `func_addr,periph_addr,kind` | Peripheral, RAM, and literal-pool references, deduplicated |
| `function_signatures.csv` | `addr,size,instructions,exact_sha256,mnemonic_sha256,shape_sha256` | Instruction hashes per function |
| `function_sites.csv` | `func_addr,ins_addr,ordinal,mnemonic` | Call sites by instruction ordinal |
| `function_references.csv` | `func_addr,ins_addr,ordinal,mnemonic,ref_addr,width,value_hex,ref_type` | References with loaded bytes and pool locations |
| `function_tokens.csv` | `func_addr,ins_addr,ordinal,mnemonic,shape` | The instruction stream of every function |
| `accessors.<kernel>.csv` | the columns of `ResolveAccessors.java` | Lookup callsites with operands and verdicts, one file per kernel |

- `funcs.csv` omits the Ghidra function name, because `RenameFuncs.java`
  writes project names into programs. Names come from
  `tools/ghidra/symbols/<layout>.csv` until their conversion into L1
  (the current owners in `tools/kb/contracts.toml`).
- `function_tokens.csv` carries `ins_addr`, so the instruction stream and
  function bodies need no listing.
- `accessors.<kernel>.csv` covers every kernel of the layout's interpolation
  registry, as the census plan of the manifest lists them.

### 8.2 Normal form

- UTF-8, LF line endings, one header row, and CSV quoting only where a value
  requires it.
- Addresses are eight lowercase hexadecimal digits; other integers are
  decimal.
- Rows are unique and sorted by their columns in order.
- No row carries a date, a local path, a user name, or a program name.

### 8.3 Manifest

```toml
layout = "jk00d"
image = "JK00D"
image_sha256 = "<SHA-256 of the registered stock image>"
program = "<program name inside the Ghidra project>"
ghidra = "<Ghidra version>"

[census]
interp = "defs/JK00D.interp.csv"
kernels = ["00027344", "00027548"]
fused = []
copy_helpers = ["000225e4"]

[scripts]
"ExportGraph.java" = "<SHA-256 of the script>"

[files."funcs.csv"]
sha256 = "<SHA-256 of the file>"
rows = 0
```

- `image_sha256` equals the catalog digest of the L0 image, and `ghidra`
  equals the pin in `tools/ghidra/headless-analyze.sh`.
- `census` is the census plan: the interpolation registry of the layout,
  every kernel it lists, the kernels whose wrapper is the kernel itself
  (`fused`), and the block-copy helpers of `[l0.census.<layout>]` in
  `tools/kb/config.toml`. A changed registry or configuration requires a new
  export.
- `scripts` lists every export script with its digest. A changed script
  requires a new export, and the `l0` check reports the layouts it affects.
- `files` lists every file with its digest and row count.

### 8.4 Export and audit

- `tools/ghidra/export-l0.sh <layout>` selects the program of the layout's
  L0 image and verifies its SHA-256 as `tools/ghidra/decompile.sh` does, runs
  the export scripts headless, normalizes the CSV files, and writes
  `l0/<layout>/` with its manifest.
- The census runs one headless session per kernel, so a function that the
  resolver recovers in memory does not carry over into the census of another
  kernel.
- `--jobs <n>` runs the sessions in parallel, each worker on its own copy of
  the Ghidra project, because a project admits one process at a time.
- `tools/ghidra/export-l0.sh <layout> --check` exports into a temporary
  directory and compares the result byte for byte with the tracked files.
- `--stage <dir>` keeps the raw session outputs, and `--from-stage <dir>`
  builds `l0/<layout>/` from them without Ghidra.
- `--batch <file>` plans the census from the registry of the layout that the
  native batch file renders, as `kb apply --dry-run` plans the batch, so
  the census of a kernel that the batch adds precedes the batch. The `census`
  issues of the batch do not refuse that plan, and every other issue does.
  The stage keeps the rendered registry as `proposed.interp.csv`, and a
  preparation of the layout binds its bytes as the census registry input.
  `kb apply <file>` then writes the batch, `kb project` writes the same
  registry, and the `l0` check of `make check` compares the census of the
  manifest with it. A `--from-stage` build with `--batch` requires the same
  rendered registry in the stage.
- A census that the L0 manifest of a layout holds and the tracked registry
  does not plan is pending. The graph loader refuses a census outside the
  registry, so while a census is pending a write plans over the model
  without a graph refresh: its batch names meanings by key and symbols by
  location. The write is refused unless its registries plan every pending
  census, and the graph loads the census with the model of the written
  batch.
- A layout joins with a new export of all its files; a partial export, an
  export of another program, or an image digest other than the catalog digest
  is refused.
- `tools/ghidra/merges/<layout>.csv` lists the reviewed function fragments of
  the layout, each with the function it belongs to; `MergeFuncs.java` joins
  them in the program before the export, and the `l0` check requires every
  join in the exported bodies.
- The export logs a `review:` line for every function of a `fn` symbol of
  the layout whose entry disappears, whose size changes, or whose former body
  holds a new entry, and each reported function is re-reviewed before the
  export is committed.

### 8.5 Derivations

The compiler derives, as `derived` elements:

- Function bodies: the instruction addresses of each function in
  `function_tokens.csv`. A body can be non-contiguous; `size` in `funcs.csv`
  is not an address range.
- Access width from the mnemonic suffix: `.b` is 8 bits, `.w` 16, and `.l`
  32.
- Access mode, load or store, from the mnemonic and the operand order.
- Literal pairing: a register holds a pool literal at an instruction when
  every path from the function entry reaches the instruction with that
  literal, loaded by a PC-relative `mov.l` or `mov.w`, copied by `mov`,
  `extu`, or `exts`, offset by `add #imm` or by a register of known value, or
  moved into GBR by `ldc` and out of it by `stc`. A register holds a known
  value without a literal after `mov #imm` or `mova`, and after a shift of a
  known value by `shll`, `shal`, `shlr`, `shar`, `shll2`, `shll8`, `shll16`,
  `shlr2`, `shlr8`, or `shlr16`; a shifted literal is no longer a literal. A
  delay slot executes on the path of its branch, and a call clears r0 through
  r7 after its delay slot. An access through such a register yields the
  accessed address, the literal, its pool address, and the base register; an
  R0-indexed access whose index is unknown yields the table base. `stc
  gbr,Rn` with a literal in GBR yields the literal as the address that it
  takes, with mode `literal` and base `gbr`: the register passes the block
  on, for example as the source of a block copy or a table argument.
- The function that contains an instruction address, and the table that
  contains a ROM address, from the `tbl` symbols and their dimensions.

### 8.6 Local exports

- Decompilations and listings stay in the export directory of
  `tools/ghidra/` as the cache of `kb code`, which calls
  `tools/ghidra/decompile.sh`. The cache is keyed by the Ghidra pin, the
  program, and the image, and for the L0 image of a layout by the digests of
  its L0 manifest and its name registry; a request under another key empties
  it first.
- `interp_core.csv`, `diagnostic_refs.csv`, flag scans, table references,
  and RAM slices stay local research exports. A gate that needs one of them
  first moves it into L0 with a manifest entry.

## 9. Compiler

The compiler turns the tracked inputs into the graph. `kb sync` runs it, and
every `kb` command runs it first when the graph is stale.

### 9.1 Inputs

- Entity files under `kb/` and `kb/names.csv`.
- L0 of every layout under `l0/`.
- `rom-images/homology.toml`, `rom-images/roms.csv`, and the stock images the
  catalog lists.
- `tools/kb/config.toml`, the restricted `tools/kb/owners.toml`, and
  `tools/kb/projections.toml`.
- Retained source registries read by their declared adapters.
- The modules of the compiler under `tools/kb/src/kb/`. The modules of the
  command line, the read commands, the checks, and the instances do not change
  the graph and are no inputs.

### 9.2 Phases

1. Parse every input. A syntax error reports the path and line.
2. Require the canonical form of every entity file.
3. Resolve names: semantic names, generated names, slugs, former names, and
   `kb/names.csv` form one name table; every reference, link target, and
   citation resolves through it.
4. Build the model: symbols per layout; links of a meaning materialized on
   every layout where both ends have symbols; `unknown` for every layout of a
   required meaning that has neither a symbol nor a status; literal loads of
   L0 paired with the access instructions that use them.
5. Run the checks of [Checks](#13-checks).
6. Load the graph ([Graph schema](#10-graph-schema)).
7. Write `:Meta` last. A graph without `:Meta`, or with a fingerprint other
   than the reader's, is stale.

### 9.3 Producers

Every node and relationship carries `producer` and `src`:

| Producer | Origin | `src` |
|---|---|---|
| `l0` | An L0 row | The L0 file path |
| `claim` | An entity file or a legacy registry row | The file path |
| `derived` | A compiler rule over `l0` and `claim` elements | The rule name |
| `candidate` | A graph algorithm run | The algorithm and its parameters |

Gates read `l0`, `claim`, and `derived` elements. `candidate` elements exist
only for exploration commands.

### 9.4 Fingerprint

The fingerprint is the SHA-256 of the sorted list of (path, git blob hash) of
every input, followed by the compiler version and the schema version. It
covers the working tree, not only `HEAD`: a modified input contributes the
hash of its current content.

`:Meta` stores:

| Property | Value |
|---|---|
| `fingerprint` | The fingerprint of the loaded inputs |
| `commit` | `HEAD` at load time |
| `dirty` | Whether any input differed from `HEAD` |
| `compiler` | The compiler version |
| `schema` | The graph schema version |
| `worktree` | The absolute path of the working tree |
| `loaded_at` | The load time in UTC |

Every reader, including `kb`, the graph readers of the tools, and the gates,
computes the fingerprint of its working tree and compares it with `:Meta`
before the first query. `kb` syncs on a mismatch; a gate or a tool raises
`StaleGraph` with the command that syncs.

### 9.5 Incremental sync

- `.kb/cache/hashes.json` maps each input path to its size, modification time,
  and git blob hash; a hash is recomputed only when size or modification time
  changes.
- The L0 part of a layout, its `Function`, `Location`, `CALL`, and `ACCESS`
  elements with the derived literal pairs, reloads when the digest of its L0
  files, its images, the address spaces of its MCU, and the compiler modules
  that build its rows changes.
  `Layout.loaded` holds that digest after a complete load of the part.
- The claim part, every `claim` element and the `derived` elements that
  follow from claims, reloads as a whole when the fingerprint changes; it
  loads in seconds.
- `AT` and the verification of symbol links are recomputed after every
  reload.
- `kb sync --full` clears the compiler's elements and loads everything.

### 9.6 Lock

`.kb/lock` serializes reads, syncs and writes within a working tree. While
held, its contents are a JSON object with these fields:

| Field | Value |
|---|---|
| `version` | Lock-status format version, `1` |
| `pid` | Holder process id |
| `token` | Unique token of this lock acquisition |
| `command` | Array of the holder's command arguments |
| `operation` | `sync` during graph synchronization, otherwise `null` |
| `stage` | Current stage, or an empty string outside synchronization |
| `progress` | Nonnegative counter, increasing at stage transitions |

A waiting process prints the holder's command and process id. During a graph
sync it also shows stage transitions. A newly observed greater `progress`
counter from the same `pid` and `token`, with `operation = "sync"`, renews
the waiting deadline by the timeout in `tools/kb/config.toml`. The first
status, another holder, ordinary contention, and a sync without further
progress do not renew it; an expired deadline exits with code 7 and names
the holder and its current stage. A reload can exceed the timeout in total
while its stages advance within that limit.

The native and compatibility loaders publish structured stage transitions;
the status is independent of human-readable log text. A read that triggers
synchronization announces it before the reload. Synchronization restores the
ordinary holder status on exit, and releasing the lock clears its contents,
also after a loader failure. Partial, malformed, unsupported-version and
legacy plain-text records do not extend a wait.

### 9.7 Legacy graph

Every element the compiler writes carries the label `:Kb` in addition to its
own labels. The compiler deletes and replaces only `:Kb` elements, preserving
other data in the same Memgraph instance.

## 10. Graph schema

The compiler loads Memgraph with MAGE. Every node and relationship it writes
carries `producer` and `src` ([Producers](#93-producers)), and every node it
writes carries the label `:Kb` in addition to its own label.

### 10.1 Nodes

| Label | `key` | Properties | Producer |
|---|---|---|---|
| `Meta` | `meta` | `fingerprint`, `commit`, `dirty`, `compiler`, `schema`, `worktree`, `loaded_at` | `derived` |
| `Family` | Family id | `kind`, `mcu` | `claim` |
| `Layout` | Layout id | `family`, `l0` (manifest digest), `loaded` (digest of the loaded L0 part) | `claim` |
| `Image` | Image id | `sha256` | `claim` |
| `Meaning` | `<name>/<kind>` | `kind`, `name`, `former`, `title`, `level`, `effective`, `home`, `role`, and the kind keys | `claim` |
| `Symbol` | `<layout>-<address>/<kind>` | `name`, `generated`, `former`, `layout`, `address`, `level`, `effective`, overrides | `claim` |
| `Entity` | `<slug>/<kind>` | `kind`, `title`, and the keys of the kind | `claim` |
| `Step` | `<chain slug>#<order>` | `effect`, `sign`, `note`, `specs` | `claim` |
| `Function` | `<layout>:<address>` | `size`, `thunk`, `external`, signature hashes | `l0` |
| `Location` | `<layout>:<address>` | `space` (`ram`, `rom`, or `io`) | `l0` |
| `Candidate` | `<algorithm>:<run>:<id>` | `algorithm`, `params`, `score` | `candidate` |

- The `Symbol` key does not contain the name, so a rename changes a property
  and no key. `name` of a symbol is the name of its full reference: its
  meaning's name, or its generated name while the meaning has none.
  `generated` is the generated name of `kb/names.csv`, and `former` lists the
  former names that still resolve ([References](#52-references)).
- Evidence items are a list property `evidence` of maps on the node or
  relationship they support. An item with `to` also yields a `CITES`
  relationship, so impact queries follow evidence dependencies.

### 10.2 Relationships

| Type | From | To | Properties | Producer |
|---|---|---|---|---|
| `IN` | `Layout`, `Image` | `Family`, `Layout` | | `claim` |
| `HAS` | `Meaning` | `Symbol` | | `claim` |
| `AT` | `Symbol` | `Function`, `Location` | | `derived` |
| `STATUS` | `Meaning` | `Layout` | `state`, `method`, `target`, `count`, `l0`, `stale` | `claim`; `derived` for `unknown` |
| `CALL` | `Function` | `Function` | `sites`, `weight` (1 for block suggestions) | `l0` |
| `SHARED_RAM` | `Function` | `Function` | `weight` (distinct RAM locations read or written by both functions; pointer-only literals excluded) | `derived` |
| `ACCESS` | `Function` | `Location` | `modes`, `sites` | `l0`, `derived` for paired literals, `census` for census copy operands |
| `WRITER`, `READER`, `INPUT`, `COPY`, `INDEX`, `AXIS`, `LOOKUP`, `SELECTOR`, `THRESHOLD`, `BASE`, `TARGET`, `SOURCE`, `MONITOR`, `DEPENDS` | `Meaning` | `Meaning` | the link keys | `claim` |
| the same types | `Symbol` | `Symbol` | `layout`, `verified`, and the link's `role`, `slot`, and `offset` | `derived` |
| `CITES` | `Meaning`, `Symbol` | `Meaning`, `Symbol`, `Entity` | `kind`, `supports`, `relies` | `claim` |
| `ANALOG` | `Meaning` | `Meaning` | `note` | `claim` |
| `BLOCK` | `Meaning`, `Entity` (endpoint) | `Entity` (block) | | `claim` |
| `STAGE` | `Entity` (block) | `Entity` (stage) | | `claim` |
| `REGISTER`, `FUNCTION` | `Entity` (endpoint) | `Meaning` | | `claim` |
| `STEP` | `Entity` (chain) | `Step` | `order` | `claim` |
| `FROM`, `TO`, `THROUGH` | `Step` | `Meaning` | `order` for `THROUGH` | `claim` |
| `OUTPUT` | `Entity` (chain) | `Meaning` | | `claim` |
| `OBSERVES` | `Entity` (signal) | `Meaning` | | `claim` |
| `SERVES` | `Entity` (field) | `Entity` (signal) | | `claim` |
| `CARRIES` | `Entity` (field) | `Meaning` | | `claim` |
| `REQUIRES` | `Entity` (feature) | `Meaning`, `Entity` | `layouts` for the `requires` of targets | `claim` |
| `TARGETS` | `Entity` (feature) | `Layout` | `status` and the keys of the target except `requires`, `allocations` among them | `claim` |
| `PROPOSES` | `Candidate` | any node | `score` | `candidate` |

- A link declared on a meaning is a relationship between meanings. The
  compiler also materializes it between the symbols of every claimed layout,
  with `verified` stating whether it holds there ([Links](#75-links)).
- One `CALL` joins a caller and a callee, and one `ACCESS` of each producer
  joins a function and a location, so path queries see one edge per pair.
  `sites` of a `CALL` lists the call instructions. `sites` of an `ACCESS`
  holds one map per instruction with `site`, `mode`, `width`, and for a pool
  literal `pool`, for a paired literal also `literal`, `base`, and
  `indexed`, and for a census copy operand `operand`, `kernel`, and `wrapper`;
  `modes` lists the distinct modes.
- `ACCESS` with producer `l0` records every reference of an instruction to RAM
  or a register, with the reference type of L0 as mode, every data or
  parameter reference to ROM, and every pool literal that names RAM or a
  register, with mode `literal`. `ACCESS` with producer `derived` records the
  literal pairs of [Derivations](#85-derivations), with modes `load`, `store`,
  and `update`, and `literal` for a `stc gbr` that takes the literal of GBR.
  `ACCESS` with producer `census` and mode `copy` records the ROM source of a
  census copy operand, which a reviewed copy helper copies into the stack
  buffer that a census call passes: the function whose body holds the census
  call reads that source, at the census call, because the export records the
  operand there. Only an operand at a complete delayed call qualifies, as for
  the `site:` evidence of the ledgers.

### 10.3 Constraints and indexes

- Every label has a uniqueness constraint on `key`. Memgraph builds no index
  for a constraint, so every label also has an index on `key`, and `:Kb` has
  a label index.
- Indexes: `Symbol(layout, address)`, `Symbol(name)`, `Meaning(name)`,
  `Location(layout, address)`, `Location(layout)`, `Function(layout, address)`,
  and `Function(layout)`.
- `schema` in `:Meta` is the schema version of the compiler. A reader built
  for another schema version treats the graph as stale.

### 10.4 Coexistence with the current graph

The labels and types above differ from those that the loaders of
`tools/memgraph/` write for code and for the diagnostic corpora, among them
`Func`, `Reg`, `Map`, `Axis`, `Interp`, `Rom`, `Claim`, `CALLS`, `ACCESSES`,
`VIA`, `USES`, `RESTS_ON`, `AXIS_X`, `AXIS_Y`, and `KERNEL`. Both sets live
in the main instance, and the compiler deletes and replaces only `:Kb` elements.

## 11. Instances

Memgraph Community holds one database per server, so every working tree has
its own server.

- The main working tree uses the compose service of `tools/memgraph/` on its
  published port.
- A linked working tree gets a container from the same image, which `kb`
  reads from the compose file, with its data under `.kb/memgraph/` and a host
  port on the loopback interface drawn from the range in
  `tools/kb/config.toml`.
- `.kb/instance.toml` records the container name, the port, the image, and the
  time of last use. `kb` resolves its connection from this file, so no bolt
  address of a linked working tree appears in tracked text. The environment
  variable `KB_BOLT` overrides the connection for tests against a scratch
  server.
- `kb instance up|down|status|prune` manages the container of the current
  working tree. `prune` stops containers idle longer than the idle limit in
  `tools/kb/config.toml` and removes the containers of working trees that no
  longer exist; `up` runs `prune` first.
- The maximum number of running instances is a parameter of
  `tools/kb/config.toml`.
- A linked working tree's graph is rebuilt from git by `kb sync`; only the
  main instance is backed up.

## 12. Commands

### 12.1 Invocation

`tools/kb` is a uv workspace member that installs the `kb` console script, so
`uv run kb <command>` works in every working tree after `make setup`.
`uv run kb mcp` serves the same operations over MCP on standard input and
output.

The read commands whose syntax ends in `[<read options>]` take these
options:


In a read command, `--layout <l>` restricts the answer to one layout.
`tools/kb/contracts.toml` declares the command syntax, read options and exit
codes. Tests bind those declarations to the parser and MCP command list.

### 12.2 Read commands

`kb show` prints the note of each symbol under the line of the symbol in its
`layouts` section, and the notes count toward the budget of the answer.

`kb at --literal` adds a separate view of exact exported 32-bit ROM load
values equal to the requested location's numeric value. Matches retain the
function, instruction, ordinal, pool address, width, raw bytes and reference
type. Their use is unclassified: a matching value does not establish a memory
access, and zero matches do not establish absence of runtime access. The
default address view and its structured output retain their existing contract.

### 12.3 Write commands

`kb rebase-reviews --layout <l> --from-l0 <digest>` maintains source-bound
unresolved access and width records after a validated L0 export. It changes
only the `l0` binding when the exact `(kind, subject, claim_sha256)` reproduces
and the current difference retains its `detail` and `sources`. The record's
`state`, `reason`, and all other fields remain unchanged. It refuses malformed
or duplicate selected records and a source digest other than the stated old
digest or the current export. Current exact records are a no-op. Reviews of
other layouts stay unchanged.

Changed, vanished, new, and otherwise unmatched differences are listed and
receive no review or updated binding. Old unmatched records remain in place;
the operation can succeed while the `code` check still fails. A custom reason
that differs from the generated `detail` also remains in place unless
`--reasons-reviewed` is explicit. The operation lists the custom text for
inspection. That flag acknowledges a separate review of any code, pointer,
call-path, or other source details named by the reason; exact discrepancy
reproduction alone does not validate those details. No review becomes
evidence or a resolved claim.

The equivalent batch operation has `cmd = "rebase-reviews"`, `layout`,
`from_l0`, and optional boolean `reasons_reviewed`. Such a batch contains only
review-rebase operations. Under the primary lock it compiles before graph
synchronization, plans the owner diff, applies the complete-model refusal
gate, and validates the selected export. A dry run writes no owner and does
not synchronize the graph. A write uses the primary file writer and then
synchronizes the graph. Changed source inputs during planning refuse the
operation before an owner write. It does not supply multi-file or graph rollback.

`kb retire` keeps the canonical owner document at its existing path and adds
`retired = true`. The complete document retains its semantic, generated and
former names, symbols, evidence, notes and outgoing relationships. Inactive
documents contribute only a `Retired` name index, with no active meaning,
symbol, designed entity, target or executable claim. Their names remain
permanently reserved. A reference to an inactive name reports its state with
exit code 5. A repeated retirement of its full meaning or entity key writes
nothing.

Retirement refuses an incoming relation, evidence dependency, architecture
step, field source, feature requirement or target reference. It also refuses
a remaining registry declarer or a generated consumer selector, including a
ledger, curated CSV, editor/logger presentation, interpolation view,
diagnostic binding or parity inventory. Consumers must leave through their
owner operations before retirement. `set` cannot change `retired`; generic
batches cannot rewrite, remove or reactivate an inactive owner. The writer
lock, dry run, complete-model refusal gate and source preservation apply as
they do to other writes. No active project entity is retired by the transfer
of its representation.

For a native function meaning whose symbols have no function entry in the
validated L0, `kb retire <meaning>/fn --withdraw-ledger <registry>:<order>`
can explicitly withdraw its active ledger projections. Repeat the option to
name every owned selector exactly once. A live or unavailable L0 entry,
another native owner, a curated selector, or any other consumer refuses the
operation. The complete inactive document keeps the ledger records as
historical data; the projections omit them. The equivalent `retire` batch
operation takes a `withdraw_ledger` array of `registry:order` strings.

This explicit withdrawal resolves a canonical meaning key on the source model
under the writer lock, validates its layouts' L0, and checks the unchanged
source fingerprint before writing. It synchronizes the graph after the source
repair, so the removed function cannot obstruct the repair by requiring a
fresh graph first. Dry run writes and synchronizes nothing. Review rebasing
remains a separate operation.

Ordinary native writes:

1. takes the lock, syncs a stale graph, and resolves its references on it;
2. builds the change in memory and compiles the model with the changed files
   in place of those on disk;
3. refuses the whole change with exit code 3 when the result has an issue of
   a model check of [Checks](#13-checks), a registry disagreement, or a
   `chain-notes` rejection of `kb audit` that the working tree lacks, or
   contradicts what an operation
   expects of it, such as the meaning of a moved symbol, and prints those
   issues and contradictions;
4. writes the files in canonical form through temporary files and renames,
   updates the graph, and writes `:Meta`;
5. prints the changed files and one line per change.

`--dry-run` stops after step 3 and prints the diff of the change; a write
draws its generated names anew.

The reservation-only `kb move --legacy-reservation` is a narrow structural
repair operation. Its corrected legacy registries and verified L0 already
hold an explicit, non-implicit function at the new entry, omit the old
entry, and preserve the old fragment under a registered seed/merge pair.
A dependency-only symbol does not establish a corrected function owner.
Under the same writer lock it compiles current
sources before graph synchronization, plans one existing reservation-key
change, and refuses an occupied destination, entity ownership, changed
symbol or meaning facts, or new model issues. The generated name and former
names stay unchanged, and the old full named reference resolves to the
current symbol. It creates no entity document and draws no generated name.
Its dry run writes nothing and does not sync. Source correction, accepted
L0, reservation writing, and graph synchronization are distinct operations;
this mode does not provide a multi-file/graph transaction. Generic move
arguments and a reservation-only batch are not part of this contract.

The file of a meaning that has none starts with the entry of its home symbol,
which joins the file with the registries that state the meaning. A symbol
that a file takes leaves `kb/names.csv`: in an unnamed meaning its generated
name becomes the `name` of its entry, and its other names become `former`
references.

- `kb bind` refuses a layout where the meaning has a symbol and a location
  that holds a symbol of another meaning, which `kb merge` joins. Without
  `--evidence`, the evidence is that of the candidate at the location that
  the search of `kb.match` finds from the symbol on the layout of `--from`,
  the symbol that the reference names, or the home symbol; a `to` that names
  a symbol becomes its location. A location that is no candidate is refused
  with the candidates. A new symbol of an unnamed meaning draws a generated
  name. A meaning without a stated `home` that the new symbol gives more than
  one symbol states its current home, unless that home is 7mfk; the target of
  `kb move` and the survivor of `kb merge` keep their home in the same way.
  The status of the layout leaves the file.
- `kb set` writes the keys of a meaning, of the entry of its symbol that the
  reference or `--layout` names, of a designed entity, or of the target of a
  feature on `--layout`. A value is a TOML value or else a string, an empty
  value unsets its key and the tables that the removal empties, and a dotted
  key names a key of a table; a table joins the held table key by key, and an
  array of tables such as `[[bit]]` replaces the held one. A meaning takes
  the keys of its schema besides `former` and its symbols, statuses, links,
  and analogs; a symbol entry takes the keys of a symbol besides `layout`,
  `address`, `name`, and `former`; a feature takes every key besides
  `target`, since its file states the facts of the feature under keys of its
  own, as the wire constants, `profiles`, and `contexts` of `can_telemetry`;
  a feature target takes `status`, `note`, `basis`, `requires`, `unsupported`, and the keys
  that a target of its feature states, and a key that no target of the
  feature states needs a declared key schema of the feature; another designed
  entity takes the keys of its schema, including arrays of tables. A key at
  any depth is bare, and a quoted key of dotted parts is refused with the
  nested key that it spells. A chain's
  `step` array replaces the held steps in the stated order, with repeated
  calls in `via` preserved. A batch can replace steps and their meanings'
  conditions together, and the chain checks run before any file is written.
  A key outside those, a value against its schema, and an unset key that the table
  lacks are refused.
- `kb new <kind> <layout>:<address>` starts the file of a meaning with the
  symbol at a location that holds no symbol of a meaning. The `--evidence`
  items state the identity of the symbol on its layout, which makes it an
  anchor ([Symbols](#73-symbols)). `--name` gives the meaning a semantic
  name by the rules of `kb rename`; otherwise the symbol keeps the generated
  name of its row of `kb/names.csv`, whose other names become `former`
  references, or draws one. `kb new <kind> <slug>` starts the empty file of a
  designed entity of a supported kind: `feature`, `signal`, `field`, `stage`,
  `block`, `endpoint`, or `chain`. The empty file of a field fails the `fields` and
  `widths` checks, and that of a chain fails `chains`, so a batch starts either
  entity with `new` and a `set` of its keys, including the chain's output and
  steps.
- `kb absent` requires evidence.
- `kb absent` and `kb unresolved` refuse a layout where the meaning has a
  symbol, which `kb move` corrects, unless its evidence does not ground it:
  every item is of a kind without a level ([Evidence](#76-evidence)), the
  symbol states no level besides `candidate`, it lies off the home of the
  meaning, and no `[[source]]` anchor of its layout or without a layout
  states it. The status replaces such a
  symbol: its entry, or its row of `kb/names.csv`, leaves the store, and the
  diff names it.
- `kb unresolved` records the `method`, `target`, and `count` of that search
  with the `l0` digest of the layout, or those that `--method`, `--target`,
  and `--count` state together. A search that finds one candidate is refused
  with the `kb bind` that records it, unless `--candidate` names that
  candidate. `--candidate` with `--note` records one candidate that cannot be
  bound, with count 1, and a stated search with count 1 requires both. A
  repeat with the `method`, `target`,
  and `count` of the held status keeps its `note` unless `--note` states one.
- `kb merge <meaning> <other>` keeps the name and the file of the meaning.
  Each symbol of the other meaning takes the evidence of the join: the
  `--evidence` items at its layout, or else the evidence of the candidate at
  its address that the search of `kb.match` finds as for `kb bind`. The merge
  refuses a layout where both meanings have a symbol, a symbol without that
  evidence, and an unnamed meaning with a named other. The entries of the
  other file, or those that `kb/names.csv` names, move into the file of the
  meaning; in a named meaning the name of each moved symbol becomes its first
  `former` reference, and the name of a named other becomes a former name of
  the meaning. The statuses, keys, links, analogs, and former names of the
  other file join those of the file: a status of a layout that gains a symbol
  leaves the file, and a status or key that both meanings state agrees, or
  the merge is refused. The other file leaves the store, every reference and
  `[[...]]` citation of the entity files to a name of the other meaning names
  the meaning, links of one type, target, slot, and offset whose keys agree
  join, and a link of the meaning to itself leaves its file. Links of one
  type, target, slot, and offset with and without `layouts` are refused
  ([Links](#75-links)). A later operation of the batch that names the other
  meaning is refused and names the meaning instead.
- The `[[source]]` entries ([Feature tables](#78-feature-tables-in-meanings))
  of the two files join: an entry equal to a held entry appears once, and
  every entry keeps its keys, its `layout` among them. The merge is refused
  when an entry of each file has the same `layout`, `path`, and `anchor` and
  another `sha256`, with both entries in the refusal and neither kept; when
  an anchor `FUN_<address>` of one file names another address than the
  symbol that the other file brings to the layout of the anchor; and when an
  entry without `layout` would cover a layout that the merge adds to its
  meaning. The two files of one meaning and `kb move <symbol> <meaning>`
  join their entries by the same rules.
- `kb link <from> <type> <to>` writes a link of [Links](#75-links) into the
  file of `<from>` with the keys of a link besides `type`, `to`, and
  `evidence` as `<key>=<value>` and the `--evidence` items; `to` is stored as
  the reference of its meaning. A link of the file with the same type,
  target, `slot`, and `offset` takes the new keys and evidence: `via`,
  `layouts`, `supports`, and `reverse_supports` join, and another key agrees
  with the held value or the link is refused. `layouts` for a held link
  without them is refused, since it would narrow the claim of that link;
  `kb set-link` restricts it. A link that adds nothing is refused.
- `kb unlink <from> <type> <to>` removes a link of that type and target from
  the file of `<from>`; `slot=` and `offset=` choose among several, and more
  than one match exits with 4. A link that only a registry states is
  refused, since the registry owns its facts until its conversion.
- `kb set-link <from> <type> <to>` replaces mutable properties of exactly one
  native relation in an existing owned source file. The source model must
  hold that file and relation before the batch; the relation names its
  target as the earlier merges of the batch rewrite it. Exact
  `--slot` and
  `--offset` selectors identify it; omitted selectors require absent keys,
  and an explicit zero offset differs from an absent offset. Offsets are
  nonnegative integers, excluding booleans. Type, target, slot, offset, and
  evidence are immutable. Mutable keys are `via`, `layouts`, `relies`,
  `supports`, `reverse_relies`, `reverse_supports`, `role`, and `note`,
  checked against the link schema and vocabulary. A value replaces the held
  value, including an array; an empty assignment removes an existing key.
  Missing or ambiguous native links, invalid values, immutable keys, and
  conflicting or duplicate unsets are refused. Exact repetitions are
  idempotent. The command changes no other link or ledger selector. The
  complete batch retains the resulting native link, its original evidence,
  and the original ledger dependencies of both ends with the native claims
  they select. A later merge or rename of the batch rewrites their
  references and moves them with the entries of a merged file; a later join
  of the link keeps each replaced value and may add array items. Different
  edits to the same link belong in one operation; a conflicting later edit
  refuses the complete batch.
- `kb select <meaning> <registry> <order>` adds one `ledger.dependency`
  selector with required string keys `role`, `to`, `type`, `end`, `relies`,
  and `supports`, and optional `link_role`, numeric `offset`, and
  `offset_text`. Keys follow section 7.8. The exact owned row must exist in
  the source model of the batch; its order is a nonnegative integer, not a
  boolean. A symbol reference for `meaning` or `to` names its meaning; the
  selected row belongs to the subject's `7mfk` symbol. The token role, link
  type, claiming end, layout, offset, link role,
  and claim must match exactly one canonical relation and one native
  document relation. Registry claims cannot supply the native claim.
  The claim's `tokens.SUPPORTS` column must exist in the registry header.
  `curated` and `diagnostic-bindings` do not project dependency selectors and
  are refused.
  Missing or duplicate rows, missing or ambiguous relations, unknown keys or
  vocabulary, and mismatched directions or claims are refused. An exact
  unique repeated selector is idempotent; an incompatible or duplicate
  selector is refused rather than replaced. No link, evidence, property, or
  unrelated selector changes. The complete batch must retain the row in its
  original owned file, the exact unique selector, and its native relation
  and claim; a later removal or incompatible change refuses the whole batch.
- `kb merge` of the two files of one meaning, which the `names` check
  reports, takes `<name>/<kind>` as the file of that name and joins the
  entries of each symbol that both files state: the name that the other file
  gives the symbol becomes a `former` reference, and the keys and evidence of
  the entries join.
- An evidence item is a TOML inline table, for example `kind = "l0", at =
  "jk00c:00043f10"`, with the keys of its kind ([Evidence](#76-evidence)).

A batch is a TOML file of `[[op]]` tables, each with `cmd` and the arguments
of one command under their names: `kind`, `meaning`, `other`, `symbol` as a
location for `new`, `slug`, `name` as a semantic name, `ref`, `layout`,
`type`, `to`, `keys` as a table for `set`, `link`, and `unlink`, `unset` as
an array of dotted keys for `set`, `evidence` as an array of tables, `from`,
`level`, `method`, `target`, `count`, and `note`; `select` uses `meaning`,
`registry`, `order`, and `dependency` as a table. `set-link` uses `meaning`,
`type`, `to`, optional `selector` with `slot` and `offset`, a `keys` table,
and an `unset` array of mutable property names. `kb apply` applies all
operations or none. Each operation resolves existing references and searches
on the working tree, and edits the files as the earlier operations leave
them. References to a meaning that an earlier `new` starts use its pending
document, including symbols that a later `bind` adds; they remain ambiguous
when they also name an existing entity. The source model stays intact, and
the complete rendered result passes every check before file or graph writes.
`set` also names a designed entity that an earlier `new` starts. An operation
that names a file that an earlier one removes is refused, and so is an
operation on a meaning that an earlier one renames, since a batch renames a
meaning after its other operations. Subagents write only through batches,
so the parent reviews one diff.

### 12.4 Output

- Output is plain text that states full references, one fact per line.
- Elements that are not claims carry their producer: `[l0]`, `[derived]`, or
  `[candidate]`.
- `kb` estimates tokens as UTF-8 bytes divided by three, rounded up. When an
  answer exceeds its budget, the first line reads `TRUNCATED`, states the shown
  and total item counts, and names the option or narrower command that shows
  the rest. Sections are cut in reverse priority: evidence first, identity
  last.
- A node whose degree exceeds the 99th percentile of its kind is a hub. `kb
  impact` and `kb path` do not expand hubs; they print the hub with its degree
  and the option that expands it.
- `kb impact` closes transitively over the dependencies between data: the
  links whose both ends are data. A function reference starts at the data and
  DTCs it writes. The functions that read the reference or a datum of the
  closure, the functions that depend on a function reference, and the claims
  that cite the reference follow without expansion, because a function that
  reads a datum need not compute each of its outputs from it. The fields that
  carry the reference or a datum of the closure follow, and the features that
  require any of them, the reference, or such a feature, with the targets that
  state a requirement of one target; chains express ordered calculations. The insertion
  points of a meaning state every layout: the accesses or calls of its symbol,
  or else its status. A field reaches the features that require it and the
  signal it serves; its insertion points are its source on every layout that
  such a feature targets: the symbol that fills its role in a target, the
  symbol of its source meaning, the status of that meaning, or for another
  origin than `ecu_ram` the allocation that the owning feature states there
  or its `7mfk` address moved by the `ram_delta` or `rom_delta` of the
  `runtime` target, marked `[derived]`. A feature reaches the features that
  require it; its insertion points are its target on every layout, with the
  status, the injected ROM and RAM of a runtime, and each hook site with its
  replacement.
- `kb path` searches the dependencies between data and those through the
  functions that read, write, and call: from the first reference to the
  second, then from the second to the first, then in any direction. Of paths
  of one length, those with more links between data come first. When a path
  through hubs is shorter, the answer states its length and the `--expand`
  options of its hubs.
- `kb find` prefilters by trigrams, ranks exact, prefix, and substring matches
  in that tier order, and orders each tier by the squared coverage of the
  query words weighted by inverse document frequency. When the second result
  scores within 10 percent of the first, the output says the query is
  ambiguous.

### 12.5 Exit codes


### 12.6 MCP

`kb mcp` exposes one tool `kb_<command>` per read command and `kb_apply` for
writes, with the same arguments, budgets, and exit semantics as errors;
`kb_apply` takes the path of a batch and `dry_run`. The transport is
newline-delimited JSON-RPC on standard input and output. The local `.mcp.json`
registers it; `tools/kb/README.md` gives the entry.

## 13. Checks

`uv run kb check` runs every active check over the working tree. Each
failure is one line with the file, the key, and the command that fixes or
explains it. `--changed` runs the checks whose inputs differ from those of
their last pass. The inputs of a check are the files that it reads and the
source and configuration of `kb`: the `l0` check reads L0, the image catalog,
the layouts, the Ghidra pin, the export scripts, and the census and join
registries; the `sites` check reads the function ledgers, L0, and the images
of the layouts; the model checks read the inputs of the fingerprint, the
census registries, and the Python files that `test` evidence names; the
`projections` and `guard` checks take every tracked file as an input.
`.kb/cache/checks.json` records for each check the digest of its inputs at
its last pass and the files that it read beyond those it states in advance.
`make check` runs `uv run kb check`.

| Check | Requires |
|---|---|
| `l0` | Every manifest matches its files, digests, and row counts; the image digest matches the catalog; the Ghidra version matches the pin; the script digests match the scripts of `tools/ghidra/`; every file is in normal form; every join of `tools/ghidra/merges/<layout>.csv` holds: the entry is a function entry, the fragment is none, and the fragment lies in the body of the entry |
| `census` | Every kernel entry that a row of an interpolation registry of the model plans for the census of a layout that reads the registry has its census file `accessors.<kernel>.csv` in `l0/<layout>/`. A write that plans a kernel without it is refused before any file changes; `tools/ghidra/export-l0.sh <layout> --batch <file>` exports the census of the change in the batch file first (section 8.4), and `kb apply <file>` then writes the change |
| `sites` | Every `site:` token of a row of the function ledger `defs/<image>.funcs.csv` of the L0 image of a layout that is an instruction of an L0 function lies in the body of the row's function, of a function the row names outside its prose columns, or of a function that the row's function calls, is called by, or continues into in sequence, or its instruction references the row's function |
| `schema` | Every entity file and every adapted registry row has the keys, types, and vocabularies of its kind; each named bit of a meaning or a symbol has a number below the access width, a name, and a level of the vocabulary, and no other bit of its list repeats its number or its name; a stated `home` of a meaning is the layout of one of its symbols, and a meaning with more than one symbol and none on 7mfk states its `home` |
| `canonical` | Every entity file equals the canonical rendering of its parse |
| `names` | Name grammar; uniqueness within a kind for semantic names and across kinds for generated names; former names stay reserved; a new generated name passes the rules of [Generated names](#54-generated-names) when it is drawn |
| `references` | Every stored reference and every `[[...]]` citation resolves, and none uses a former name |
| `symbols` | At most one symbol per layout, kind, and address; at most one symbol or status per meaning and layout; every address lies in the address space of its kind on the MCU of the layout; every `fn` symbol is a function entry of L0 |
| `homology` | Every file-owned symbol whose identity level is not explicitly declared `candidate` is an anchor or reaches one through homology evidence of an accepted kind ([Symbols](#73-symbols)); every identity and homology evidence item whose kind L0 or the images decide holds ([Evidence](#76-evidence)); every typed evidence item of a named bit lies on the layout of a symbol of its meaning, and each whose kind L0 decides holds for that symbol |
| `levels` | No declared level exceeds its effective level; `candidate` claims carry evidence, and `code` and `silicon` claims grounding; every `hardware` key names a record whose `hardware_status` is `pass`; every `arithmetic` equation holds ([Levels](#71-levels)) |
| `ledgers` | Every owned ledger view selects existing evidence and notes and a canonical dependency with the selected direction, layout, offset, role, and claim; the selected curated name is current or former |
| `links` | The kinds of both ends and the keys match the link type; `layouts` covers the evidence layouts; every link holds on every claimed layout ([Links](#75-links)) |
| `widths` | Access widths in L0 agree with the `width` of `ram` and `reg` symbols; every field width fits its source: on every layout that a feature requiring an `ecu_ram` field targets, the symbol that the field reads states a width of at least the bits of the field, and the allocation of a field of another origin holds at least its bytes |
| `code` | Declared writer and reader relations reproduce through normalized L0 accesses; wider RAM and register accesses have an exact unresolved review with a reason, claim digest and L0 digest; new, changed, duplicate and vanished differences fail |
| `image-bytes` | `rom-bytes` values, those of the named bits included, hook `target` words, DID table entries, and the storage and dimensions of `tbl`, `axis`, and `const` symbols agree with every image of the layout |
| `statuses` | `absent` carries evidence; `unresolved` carries `method`, `target`, `count`, and `l0`, and with count 1 a `candidate` location on its layout and a `note`; stale searches are reported and do not fail |
| `writers` | Each store of a `ram` or `reg` symbol that aligns on the layout of another symbol of its meaning aligns with a store of that symbol, in both directions between the home symbol and each other symbol; `[writers] review` of `tools/kb/config.toml` lists the contradictions under review, each as the symbol and the store site, and an entry that no longer reproduces fails |
| `blocks` | Stages, blocks, and endpoints carry the required text metadata of the generated view; order is a positive integer where stated; named specifications are repository files; every reviewed `fn` meaning has a block or appears in the unplaced report, as `tools/romviz/architecture.py check` reports them; every block names a stage |
| `chains` | Required metadata is nonempty text, and named specifications are repository files; every step resolves; `effect` and `sign` are in their vocabularies; a step note is text and matches the arithmetic grammar of `tools/kb/config.toml`; `output` is the `to` of a step |
| `fields` | Every field names a source of its origin, and every `ecu_ram` field a signal; an `ecu_ram` field carries no semantic scale, allowing only the explicit `raw count` storage view, and its source is a `7mfk` `ram` or `reg` symbol outside the RAM that a feature allocates; on every layout that a feature targets, each source meaning of its fields has a symbol or a status, or a symbol fills the role of the field in the target, and the `signed` of the field agrees with the symbol that it reads where the symbol states one; a field of another origin carries its scale, and its source is the allocation named after the field without `_raw` inside a region of its origin that the feature of the allocation owns |
| `projections` | Every registered path matches tracked files that no other projection claims; its inputs, consumers, and generator paths exist; a projection of a `kb` function that applies equals its rendering; every tracked file outside `kb/` and `l0/` whose first six lines declare it generated is registered |
| `guard` | `.claude/settings.json` and `.codex/hooks.json` are tracked and run `tools/kb/hook.py` synchronously before every guarded tool, including the Codex `apply_patch`; `.ignore` lists the guarded trees and the guarded projections that apply; the hook refuses a read and an edit in every tree, an edit of every projection that applies, and a read of every guarded projection that applies |

A write command runs the model checks on its result and refuses the issues
that the result adds to those of the working tree ([Write
commands](#123-write-commands)).

The `homology` check covers the symbols that the entity files of `kb/` own:
those that only files state and those whose file entry states evidence. It
also verifies every non-legacy `indirect` item with mode `base` and every
non-legacy `test` item of a symbol, regardless of its owner or `supports`.
A failed base item remains a check failure even when the `levels` report
holds the symbol's structure. The additional checks do not change ownership,
other indirect modes, or the treatment of other legacy tokens. A
file entry that only names a symbol of a registry joins the file with the
meaning, and the registry keeps the symbol's evidence. The `statuses` check
covers the statuses that the files state. The conversion of each registry
extends both. The `image-bytes`, `writers`, and `levels` checks cover the
whole model; the symbol claims of the `levels` check follow the symbols that
the files own.

An evidence item that an adapter maps from a legacy token keeps the token in
`legacy`. The `schema` check does not require the keys of its kind, and the
`image-bytes` check does not compare it with the images; `kb audit`
lists every such item that lacks them, under each registry that states it,
until the conversion of that registry types it.

## 14. Projections

`tools/kb/projections.toml` registers every generated file of the repository,
including the files that current generators already produce:

```toml
[[projection]]
path = "defs/JK08A.{funcs,vars,findings,axes,dtc,diagnostic-bindings}.csv"
generator = "kb.ledger_projection:registries"
inputs = ["kb/", "l0/7mfk/", "tools/kb/src/kb/ledger_projection.py"]
consumers = ["tools/maps/build_tracker.py"]
read = "guarded"
```

| Key | Meaning |
|---|---|
| `path` | Generated file, a pattern, or `<file>#<name>` for the section of a file between `<!-- <name>:begin -->` and `<!-- <name>:end -->`; in a pattern `*`, `?`, and `[...]` match within one path segment and `{a,b}` lists alternatives |
| `generator` | The function `kb.<module>:<function>` that renders it from the repository root, which returns the text, or for a pattern {path: text} of its files; or the command of its current generator |
| `check` | For a command projection, the read-only argument array of the same producer with `--check`; a source placeholder binds an explicitly supplied `VQ_` path variable |
| `inputs` | Paths whose change requires regeneration |
| `consumers` | Tools, tests, and external programs that read it |
| `read` | `guarded`: agents read the knowledge through `kb`; `open`: anyone reads the file |

- A projection is regenerated byte-identically. `uv run kb project` renders
  the projections of `kb` functions that apply under the lock of the writes,
  `uv run kb project --check` compares them without writing, and the
  `projections` check compares them with their rendering and the tracked
  files of a pattern with the files of its rendering. A projection of another generator keeps
  the gate of that generator; the check requires its files and the repository
  paths of its command to exist.
- A tracked file outside `kb/` and `l0/` whose first six lines declare it
  generated (`generated by`, `generated from`, or `do not edit`) is
  registered.
- `tools/check_projection_contract.py` requires a declared checker for every
  command projection, with the same producer and arguments and no write mode.
  `make check` runs this contract gate and the available source comparisons.
  `--run` executes every native and command comparison, requires every external
  source before starting, and withholds results if the compiler fingerprint
  changes across the run. `VQ_OBD2TOOLS_SOURCE` names the exact pinned checkout
  required for the external obd2tools corpus; an unavailable source blocks the
  complete run and supplies no reproduction evidence.
- No projection is edited by hand: the access guard refuses the edit and the
  check reports the difference.
- Editor definitions, the TunerPro and RomRaider files, and the host decoder
  are `open`. Ledgers and registries whose facts live in `kb/` are `guarded`.
- A projection without consumers is removed.
- `AGENTS.md` carries one generated section, the projection `AGENTS.md#kb`
  between `<!-- kb:begin -->` and `<!-- kb:end -->`: the access rules, the
  table of questions and commands, and the current fact owners.
- `rom-images/support-matrix.md` carries the generated section `features`,
  the projection `rom-images/support-matrix.md#features`: a table with a row
  for each layout and the images that share its addresses and a column for
  each feature in the order of the build, whose cell states the status of the
  target and what the model derives from it (the runtime ROM and RAM, the
  switched and unsupported map families, the telemetry mailbox, the `ecu_ram`
  fields whose source the layout lacks or whose wire role is unsupported, and the other required meanings
  without a symbol by the state of their status), then a table of the title,
  summary, and specifications of each feature. The feature targets hold the
  facts and the section only shows them; a specification that names no file
  refuses the rendering.

## 15. Access guard

The guard keeps agents on `kb` for knowledge that has an owner file under
`kb/`, `l0/`, or a guarded projection. It is a convenience boundary, not a
security boundary: the gates validate every file whatever wrote it.

- The tracked `.claude/settings.json` registers a PreToolUse hook for `Read`,
  `Edit`, `Write`, `MultiEdit`, `NotebookEdit`, `Grep`, `Glob`, and `Bash`.
  The tracked `.codex/hooks.json` registers the same tools and `apply_patch`;
  Codex sends shell calls as `Bash` and patches as `apply_patch`, with the
  command in `tool_input.command`. The hook command resolves the git root so
  that starting a session in a subdirectory preserves the hook location.
  Project hooks require a trusted Codex project layer and review of their
  exact definition through `/hooks`, as specified by the
  [Codex hook contract](https://learn.chatgpt.com/docs/hooks).
  The hook runs `tools/kb/hook.py` with the Python of the working tree's
  `.venv`, or `python3` without it. The hook uses only the Python standard
  library and reads its path lists from `[guard]` of `tools/kb/config.toml`
  and from `tools/kb/projections.toml`, and the stage from
  `tools/kb/bench.toml`. Python older than 3.11 or missing `tomllib` produces
  a deliberate denial that names the required interpreter. Any other
  failure denies the call with exit status 2 and a reason that names the
  error and `KB_GUARD=off`.
- Claude Code cancels a command hook that reaches its timeout, 600 s by
  default, and discards its output. A `PreToolUse` call whose hook times out
  continues through the normal permission flow unless the hook sets
  `onFailure: "block"` (Claude Code 2.1.295 or later); a hook that fails to
  start, or exits with a status other than 0 or 2, also lets the call
  proceed. These rules follow the
  [Claude Code hook contract](https://code.claude.com/docs/en/hooks). The
  tracked hook sets neither `timeout` nor `onFailure`, so the guard bounds
  its own decision: a decision checks at most `PATH_BUDGET` (10,000) shell
  paths, counting each literal operand and each match of a file pattern, or
  the pattern itself when it matches nothing, and runs for at most
  `DECISION_SECONDS` (5 s). A call that exceeds either budget is denied with
  a reason that names the budget. In the main thread of the hook, with no
  other real-time timer, `SIGALRM` interrupts the decision at its time
  budget. Elsewhere the decision checks its deadline at each shell path and
  at its end: a call that runs past the deadline is denied, but a slow step
  runs to its end.
- The hook denies with `permissionDecision = "deny"` and a reason that names
  the command to use:

| Tool call | Decision | Reason names |
|---|---|---|
| `Edit`, `Write`, `MultiEdit`, `NotebookEdit` under `kb/`, `l0/`, or on a projection that applies | Deny | The write command, or the generator of the projection |
| `apply_patch` that adds, updates, deletes, or moves a file under `kb/`, `l0/`, or on a projection that applies | Deny | The write command, or the generator of the projection |
| `Read` under `kb/` | Deny | `kb show` and `kb raw` with the reference the path maps to |
| `Read` under `l0/` | Deny | `kb at`, `kb code`, and `kb cypher` |
| `Read` of a guarded projection | Deny | `kb show`, `kb where`, or `kb find` |
| `Grep` or `Glob` whose path lies in a guarded tree or file | Deny | `kb find` |
| `Bash` that reads or searches a guarded operand, or edits a guarded tree or projection, outside a trusted runner | Deny | The matching `kb` command |

- The git allow list covers `status`, `add`, `commit`, `diff`, `log`,
  `show`, `restore`, `checkout`, `switch`, `stash`, `rebase`, `merge`,
  `mv`, and `rm`, so diffs stay reviewable. Explicit blob reads, commit message
  files, `grep`, `diff --no-index`, output files and worktree file edits receive
  their file checks before that allow list applies. Index-only operations
  retain their access. `make` and repository scripts read their inputs as the
  gates do.
- Shell inspection preserves quoted data, actual operators and here-document
  bodies. It checks redirections and active command substitutions before
  trusted runners. Absolute glob operands retain their root and symbolic links
  resolve to their targets. A subshell restores its parent working directory
  and variables. Bare tree operands are paths, while search patterns and
  literal draft bodies are data. Known codex-messaging scripts treat `--text`
  as data and `--file` as a file operand. Literal pipeline data becomes file
  operands when `xargs` invokes a command that can access files. Python program
  arguments receive operand checks separately from the program text. Known
  shell variables expand before path checks. An unresolved absolute operand
  whose fixed prefix is outside the repository and its ancestors stays open;
  the prefix resolves symbolic links before that decision.
  Bounded literal `for` lists check every iteration value without executing the
  commands. Unknown lists keep their iteration values unresolved and are data
  apart from their patterns, which receive read checks. Reserved words such as
  `do` and `then` and wrappers such as `timeout` and `env` leave the decision
  to the command they precede; wrapper options that take a value check it as an
  operand.
  The `gh issue` and `gh pr` operations `create`, `view`, `comment`, `close`,
  `reopen` and `edit` treat issue numbers, URLs, branches and text options
  such as `--comment`, `--body` and `--title` as data; `--body-file` (`-F`),
  `--template` (`-T`) and `--recover` remain read operands. `gh api` treats its endpoint and field values as data;
  `--input` and `-F` values that start with `@` remain read operands, and an
  unresolved `-F` value receives the operand check. Redirections and active
  substitutions retain their checks before these option roles apply.
  `jq` treats its program text, the values of `--arg`, `--argjson` and
  `--indent`, and the operands after `--args` or `--jsonargs` as data; its
  input files, the files of `--slurpfile`, `--rawfile` and `--argfile`, and
  the program file of `-f` remain read operands. A jq program, or the text
  of a program file, that holds an `import`, `include` or `modulemeta` token,
  a program file that cannot be read, `-L`, and a program that a shell
  expansion supplies are denied. `exit` and `return` take no file operands.
  A relative `ln` target resolves against the directory of its link, and
  every word after `--` is an `ln` operand.
  A brace pattern in an operand expands to at most 256 alternatives, and an
  operand with more is denied, as is an operand with a brace sequence such
  as `{0..9}`. A value with whitespace is a quoted or document value, which
  no shell or Python call brace-expands, so it is checked as written; a
  shell word with an unquoted brace expands even where an alternative holds
  a quoted space.
- Inline Python inspection accepts finite literal file operations and metadata
  transformations over captured responses. File paths support literals,
  unique simple bindings and path joins; a name that any other form also
  binds, such as a loop, tuple, walrus, annotated or augmented assignment
  target, a match capture or an import, has no literal value, and a known
  call whose name the program binds is an unknown operation; known string
  and metadata operations keep literal source headers as data. `Path` joins all of its arguments.
  `csv` reads and writes only the file objects that `open` checks, and a
  `replace` call with two or more arguments on a value other than a module
  is string replacement. In a program that names a protected reference, a
  dynamic file operand and namespace access such as `sys.modules`,
  `__dict__` or `__builtins__` are denied: a dynamic path may reach a
  guarded file through a link or a rebound namespace. Unknown operations
  involving protected references are conservatively denied. The hook does not execute Python
  programs or provide general Python analysis. Unknown shell operations use
  conservative checks of their possible file operands.
- The guard decides before the call runs and from the call text alone, so
  forms that hide a protected path or create it during the call lie outside
  the convenience boundary. The guard admits:
  - a Python program without a protected constant that builds a protected
    path at run time, such as
    `open(''.join(['k', 'b', '/names.csv']))`;
  - a Python script file such as `python3 tmp/script.py`, whose text the
    guard does not read;
  - a link that Python creates with a relative target, which resolves
    against the link directory while the guard checks it against the working
    directory, such as `os.symlink('../kb/names.csv', 'tmp/zz.txt')`;
  - the value of a long option that holds a brace pattern, such as
    `base64 --input=l{x,0}/7mfk/funcs.csv`, since such a value is not
    checked as a path;
  - a jq program file that the decision reads before the call writes it:
    `jq -f /dev/stdin` with a here-document reads the empty standard input
    of the hook, and a program file that the same command rewrites is
    checked in its prior state;
  - the combined GNU form `ln -st <directory> <target>`, since only a
    separate `-t` names the target directory;
  - a link that an earlier part of the same compound command moves or
    reaches through another link, such as
    `ln -s ../kb/names.csv tmp/x/zz.txt && mv tmp/x/zz.txt tmp/zz.txt && cat tmp/zz.txt`
    or `ln -s .. tmp/up && ln -s up/kb/names.csv tmp/zz.txt && cat tmp/zz.txt`,
    since the link does not exist when the guard resolves the later operand.
- An edit of a file with a marked section is an edit of the projection when
  it changes the section or its markers.
- A Codex patch checks every source and move destination. For an update of
  a marked projection it reconstructs the file without writing it and
  compares the generated section. A patch whose operations or required
  context cannot be inspected is denied. A Codex shell call uses its
  `workdir` when supplied, otherwise the session working directory.
- A directory above the guarded trees and projections stays open to reads
  and searches.
- `.ignore` excludes the root trees `kb/` and `l0/` and guarded projections
  from ripgrep, so a repository-wide `Grep` does not return their contents.
- The Memgraph MCP server and Memgraph Lab stay open for exploring the main
  instance. They read the graph without the fingerprint check, so a gate, a
  generator, or an evidence item never rests on their answers; `kb cypher`
  answers the same queries over the working tree's instance.
- `KB_GUARD=off` in the hook environment disables the hook for maintenance
  when no valid session override exists. `kb guard on|off --session <id>`
  records an override for an explicit root session UUID in this working tree.
  Its atomic local JSON
  record binds the canonical project path and session UUID. The hook reads
  it by the event's `session_id`; a valid record takes precedence over the
  environment, and invalid records grant no exception. `kb guard status
  --session <id> [--json]` reads the saved override without writes or graph
  access; `mode = null` states no valid override and makes no claim about a
  remote hook's environment. The override applies to active sessions without
  restarting them. Other sessions and hook definitions retain their settings.
  Subagents and forks with the same root `session_id` share its override.
  Codex uses its ordinary executable and launch command.
- Hooks apply to subagents. Agents without hook support follow the generated
  section of `AGENTS.md`, and the gates catch the rest.

## 16. Graph algorithms

MAGE procedures of the instance propose candidates for exploration:

| Use | Procedures | Subgraph | Output |
|---|---|---|---|
| Blocks for unplaced functions | `leiden_community_detection.get_subgraph` | `Function` nodes of one layout with `CALL` edges and edges between functions that access the same `Location`, weighted by the number of shared locations | Communities; an unplaced function gets the block that dominates the placed members of its community, or a new block |
| Subsystems of a new layout | `community_detection.get_subgraph` | The L0 of the layout | Proposed subsystems, including those without homologs |
| Homolog channel of `kb suggest` | `node_similarity.jaccard_pairwise`, `node_similarity.cosine_pairwise`, `node_similarity.overlap_pairwise` | Functions of two layouts with their callees, the meanings of the locations they access, and their literal values | Ranked candidate symbols, each with the evidence kinds that could confirm it |
| Ranking | `pagerank.get`, `betweenness_centrality.get`, `katz_centrality.get`, `degree_centrality.get` | Links and calls of one layout | The order of gaps in `kb brief` and the hub threshold of [Output](#124-output) |
| Islands | `weakly_connected_components.get` | Meanings and links | Meanings without a path to a feature or a chain |
| Loops and cut points | `cycles.get`, `bridges.get` | Chain steps and data links | Feedback loops of calculations, and single links whose change separates a chain |

- Results are `Candidate` nodes with `PROPOSES` relationships. Each carries
  the procedure, its parameters, and the fingerprint of the graph it ran on,
  and `kb` reuses results while the fingerprint holds.
- Gates never read candidates, and a candidate is never evidence. Accepting
  one is a write command that records evidence of an accepted kind.
- `kb instance up` verifies that the instance provides every procedure the
  compiler calls.

## 17. Cases

The cases show the model on data of the current registries and L0 exports.
Names that no registry carries yet are illustrative, `<digest>` stands for a
manifest digest prefix, `<n>` for a count, and fields leave out their stream
placement keys.

### 17.1 Normalized load across layouts

On `7mfk`, the producer `FUN_0003b75c` stores
`min(255, floor(uint16[ffff1026] * 128 / ROM16[00009534]))` at `ffff1048`,
and the scheduler `FUN_00020dfe` copies `0x1c` bytes from `ffff1048` to
`ffff102c` through the block copier at the call `00020f18`. On `jk00c` and
`jk00d`, the 32 instruction words at `0003cacc` equal those at `7mfk`
`0003bd1c` with PC-relative displacements masked, and the literals map
`ffff1048` to `ffff1050`; the scheduler `00020e30` copies the block from
`ffff1050` to `ffff1034` at `00020f50`. On `jk78c`, `1nd`, and `1me3b` the
masked producer has no match. The telemetry stream publishes the snapshot.

`kb/ram/normalized_bfs.toml`:

```toml
title = "Normalized Base Fuel Schedule in 1/128 of the reference"
summary = """
The newest Base Fuel Schedule word as a ratio to the calibration reference: \
min(255, floor([[base_fuel_schedule/ram]] * 128 / [[bfs_reference/tbl]])). \
Raw 128 is 100 percent of the reference, and raw 255 is the saturation."""
level = "code"
home = "7mfk"
width = 8
signed = false
unit = "percent of the Base Fuel Schedule reference"
scale = "x*100/128"
to_raw = "x*128/100"
scale_level = "code"

[[symbol]]
layout = "7mfk"
address = "ffff1048"

[[symbol.evidence]]
kind = "l0"
supports = "identity"
at = "7mfk:0003bd5a"
note = "The only direct store to the byte."

[[symbol.evidence]]
kind = "trace"
supports = "identity"
to = "divide_u32/fn"
relies = "contract"

[[symbol]]
layout = "jk00c"
address = "ffff1050"

[[symbol.evidence]]
kind = "masked-match"
supports = "homology"
at = "jk00c:0003cacc"
to = "7mfk:0003bd1c"
count = 1
value = 32

[[symbol]]
layout = "jk00d"
address = "ffff1050"

[[symbol.evidence]]
kind = "masked-match"
supports = "homology"
at = "jk00d:0003cacc"
to = "7mfk:0003bd1c"
count = 1
value = 32

[[status]]
layout = "1me3b"
state = "unresolved"
method = "masked-match"
target = "7mfk:0003bd1c"
count = 0
l0 = "<digest>"

[[status]]
layout = "1nd"
state = "unresolved"
method = "masked-match"
target = "7mfk:0003bd1c"
count = 0
l0 = "<digest>"

[[status]]
layout = "jk78c"
state = "unresolved"
method = "masked-match"
target = "7mfk:0003bd1c"
count = 0
l0 = "<digest>"

[[link]]
type = "writer"
to = "bfs_producer/fn"
relies = "structure"
```

`kb/ram/normalized_bfs_snapshot.toml`:

```toml
title = "Scheduler snapshot of the normalized Base Fuel Schedule"
summary = """
The scheduler copies the block that starts at [[normalized_bfs/ram]] to the \
block that starts here once per pass, so the readers of one pass see one \
value. It is the column coordinate of the ignition and intake-cam target \
maps."""
note = ["The physical name Cylinder Filling Up Efficiency is a candidate."]
level = "code"
home = "7mfk"
width = 8
signed = false
unit = "percent of the Base Fuel Schedule reference"
scale = "x*100/128"
to_raw = "x*128/100"
scale_level = "code"

[[symbol]]
layout = "7mfk"
address = "ffff102c"

[[symbol]]
layout = "jk00c"
address = "ffff1034"

[[symbol]]
layout = "jk00d"
address = "ffff1034"

[[symbol]]
layout = "jk78c"
address = "ffff1032"

[[status]]
layout = "1me3b"
state = "unresolved"
method = "masked-match"
target = "7mfk:0003bd1c"
count = 0
l0 = "<digest>"

[[status]]
layout = "1nd"
state = "unresolved"
method = "masked-match"
target = "7mfk:0003bd1c"
count = 0
l0 = "<digest>"

[[link]]
type = "copy"
to = "normalized_bfs/ram"
via = ["coherent_snapshot/fn", "block_copy_odd/fn"]
relies = "level"

[[link.evidence]]
kind = "indirect"
at = "7mfk:00020f18"
mode = "block-copy"
note = "0x1c bytes from ffff1048 to ffff102c."

[[link.evidence]]
kind = "indirect"
at = "jk00c:00020f50"
mode = "block-copy"
note = "0x1c bytes from ffff1050 to ffff1034."

[[link.evidence]]
kind = "indirect"
at = "jk00d:00020f50"
mode = "block-copy"
note = "0x1c bytes from ffff1050 to ffff1034."

[[link]]
type = "reader"
to = "exhaust_cvtc_target_accessor/fn"
relies = "level"
```

The snapshot symbols are anchors: the `copy` link carries `relies` and holds
on each layout through evidence of that layout.

`kb/field/normalized_load_raw.toml`:

```toml
signal = "normalized_load/signal"
source = "normalized_bfs_snapshot/ram"
origin = "ecu_ram"
width = 1
signed = false
```

`kb/signal/normalized_load.toml`:

```toml
title = "Normalized engine load"
domain = "air"
priority = "core"
coverage = "fixed"
basis = "exact-code"
observes = ["normalized_bfs_snapshot/ram"]
```

The field takes `x*100/128` from the meaning. The meaning has a status on
`1nd` and `1me3b`, so the field is unavailable there, and the `fields` check
accepts it.

```text
$ uv run kb where normalized_bfs_snapshot
normalized_bfs_snapshot/ram  code  home 7mfk  Scheduler snapshot of the normalized Base Fuel Schedule
1me3b  unresolved  masked-match 7mfk:0003bd1c  count 0
1nd    unresolved  masked-match 7mfk:0003bd1c  count 0
7mfk   ffff102c  code  copy of normalized_bfs/ram/7mfk-ffff1048  indirect block-copy 7mfk:00020f18
jk00c  ffff1034  code  copy of normalized_bfs/ram/jk00c-ffff1050  indirect block-copy jk00c:00020f50
jk00d  ffff1034  code  copy of normalized_bfs/ram/jk00d-ffff1050  indirect block-copy jk00d:00020f50
jk78c  ffff1032  code  copy of normalized_bfs/ram/jk78c-ffff1042

$ uv run kb at jk00d:ffff1034
normalized_bfs_snapshot/ram/jk00d-ffff1034  ram 8-bit unsigned  code
  title   Scheduler snapshot of the normalized Base Fuel Schedule
  scale   x*100/128 percent of the Base Fuel Schedule reference
  copy    normalized_bfs/ram/jk00d-ffff1050 via coherent_snapshot/fn/jk00d-00020e30
  field   normalized_load_raw/field  signal normalized_load/signal
  [l0]    readers: <n> sites in <n> functions (kb show --layout jk00d lists them)

$ uv run kb gaps --feature can_telemetry --layout 1nd
can_telemetry on 1nd: fields whose source has no symbol
  normalized_load_raw/field  normalized_bfs_snapshot/ram  unresolved  masked-match 7mfk:0003bd1c  count 0
```

### 17.2 A JK08A chain step

`defs/JK08A.architecture.toml` states one step of the engine-speed chain as:

```toml
[[chain.step]]
from = "ffff22bc"
to = "ffff114a"
effect = "converts"
sign = "negative"
via = ["0003deec"]
note = "ffff114a = floor(0xA2C2/ffff22bc) in RPM/12.5; ffff24c9.bit5 copies ffff11f4 instead and ffff417f.bit5 writes zero."
```

In the model, the step keeps the arithmetic and the conditions become links
of the destination meaning. `kb/chain/engine_speed.toml`, with the other
steps left out:

```toml
title = "Engine speed"
summary = """
The ICI0A crank handler forms the 10-degree tooth time ffff22bc on every \
tooth and, on the tooth-7 engine event, the 120-degree interval ffff11fc; \
ffff1196 = 32000000/ffff11fc is engine speed, and its shifted words and \
scheduler snapshots index the maps."""
quantity = "Engine speed, RPM*5.12 counts"
output = "engine_speed/ram"
specs = [
    "defs/JK08A.cvtc.md",
    "defs/JK08A.fuel.md",
    "defs/JK08A.rpm-drop-state.md",
]
home = "7mfk"

[[step]]
from = "tooth_time/ram"
to = "rpm_12_5/ram"
effect = "converts"
sign = "negative"
via = ["rpm_12_5_producer/fn"]
note = "ffff114a = floor(0xA2C2 / ffff22bc)"
```

`kb/ram/rpm_12_5.toml`:

```toml
title = "Current engine speed, RPM/12.5 word"
level = "code"
width = 16
signed = false
unit = "rpm"
scale = "x*12.5"
to_raw = "x/12.5"
scale_level = "code"

[[symbol]]
layout = "7mfk"
address = "ffff114a"

[[link]]
type = "writer"
to = "rpm_12_5_producer/fn"
relies = "structure"

[[link]]
type = "input"
to = "tooth_time/ram"
via = ["rpm_12_5_producer/fn"]
relies = "structure"

[[link]]
type = "copy"
to = "rpm_12_5_source/ram"
via = ["rpm_12_5_producer/fn"]
relies = "structure"

[[link]]
type = "selector"
to = "engine_speed_mode/ram"
slot = "bit5"
note = "Set: the producer copies ffff11f4 in place of the conversion."

[[link]]
type = "selector"
to = "engine_speed_inhibit/ram"
slot = "bit5"
note = "Set: the producer writes zero."
```

The ledger evidence of `ffff114a` converts to the `writer` link and to two
`input` links ([ledger dependency mapping](src/kb/adapters/ledgers.py)); review turns the
second into the `copy` link and adds the selectors that the step note
stated. Benchmark question 12 in [`bench.toml`](bench.toml) reads:

```text
$ uv run kb show 7mfk:0003deec
rpm_12_5_producer/fn/7mfk-0003deec  fn accessor  code
  block   engine_speed/block  stage estimation/stage
  step    engine_speed/chain #<n>  tooth_time/ram -> rpm_12_5/ram  converts negative  floor(0xA2C2 / ffff22bc)
  writes  rpm_12_5/ram/7mfk-ffff114a
  select  engine_speed_mode/ram bit5, engine_speed_inhibit/ram bit5
```

### 17.3 VVEL on JK78C

The VQ37VHR layouts `jk78c`, `1nd`, and `1me3b` belong to three families.
The mode byte `ffffa22f` of `jk78c` selects one of fifteen duration and VTC
pairs that the resolver computes; no writer stores the value 14. Each layout
reads the running duration target through pointer loads in its own code, so
each symbol is an anchor with evidence of its own layout.

`kb/ram/vvel_mode.toml`:

```toml
title = "VVEL and VTC control mode"
summary = """
The mode machine stores the control mode here, and [[vvel_pair_selector/fn]] \
selects the duration and VTC pair of the mode from the pairs that \
[[vvel_duration_resolver/fn]] computes."""
level = "code"
width = 8
signed = false

[[value]]
value = 14
name = "fixed_duration"
summary = "Duration 50.0 and VTC 0; the resolver computes the pair as dead data."
reachable = false
level = "code"

[[value.evidence]]
kind = "spec"
supports = "role"
path = "defs/JK78C.vvel.md"
note = "The image holds no write of the value 14 to ffffa22f."

[[value]]
value = 15
name = "running"
summary = "Warm, above idle, with no hot-intake or throttled request."
level = "code"

[[value.evidence]]
kind = "trace"
supports = "role"
to = "vvel_mode_running/fn"
relies = "contract"

[[symbol]]
layout = "jk78c"
address = "ffffa22f"

[[link]]
type = "writer"
to = "vvel_mode_running/fn"
relies = "structure"
```

`kb/tbl/vvel_duration_running.toml`:

```toml
title = "VVEL Duration Target - Running"
summary = """
Duration target of the running mode of [[vvel_mode/ram]]: the resolver \
interpolates it by engine speed and scales the count by the float literal \
0.005 before the selector publishes the command."""
level = "code"
home = "jk78c"
role = "table"
access = "explicit"
cols = 16
rows = 1
storage = "uint16"
unit = "deg"
scale = "x*0.005"
to_raw = "x/0.005"
scale_level = "candidate"

[editor]
name = "VVEL Duration Target - Running"
category = "Variable Valve Timing / VVEL Duration"
order = 10
format = "0.000"
fine = 0.005
coarse = 0.05

[[symbol]]
layout = "1me3b"
address = "00017276"
note = "The resolver stores the value in pair 14 of its thirty-float output."

[[symbol.evidence]]
kind = "l0"
supports = "identity"
at = "1me3b:00063400"
note = "Loads the table for resolver 00062fac; 00063ee0 loads it for 00063cd4."

[[symbol]]
layout = "1nd"
address = "000171c2"

[[symbol.evidence]]
kind = "l0"
supports = "identity"
at = "1nd:0005f764"
note = "Loads the table for resolver 0005f468; 0005fe5c loads it for 0005fd88."

[[symbol]]
layout = "jk78c"
address = "00016bb4"

[[symbol.evidence]]
kind = "l0"
supports = "identity"
at = "jk78c:00056680"
note = "Loads the table for resolver 000564a4; 00056f78 loads it for 00056dca."

[[link]]
type = "axis"
to = "vvel_speed_axis/axis"
slot = "x"

[[link]]
type = "reader"
to = "vvel_duration_resolver/fn"
relies = "structure"

[[analog]]
to = "intake_cvtc_target_main/tbl"
note = """
Both set an intake valve event target from engine speed: VVEL through lift \
and duration, CVTC through cam phase only."""
```

`vvel_mode/ram` has a symbol on `jk78c` only. A feature that requires it on
`1nd` or `1me3b` sees `unknown` there until a search records a symbol or a
status. The analog links the VQ37VHR table to the table of the 7MFK family
for readers and for `kb suggest`, and no check reads it.

Communities over the calls and shared RAM of `jk78c` propose a block for the
unplaced VVEL functions:

```text
$ uv run kb suggest --blocks --layout jk78c
[candidate] leiden_community_detection on jk78c: calls and shared locations
  community <n>: <n> functions, no placed member -> new block
    vvel_duration_resolver/fn/jk78c-000564a4
    vvel_pair_selector/fn/jk78c-000557b2
    vvel_mode_running/fn/jk78c-00054a94
    <generated name>/fn/jk78c-000543ea
  accept: kb new block <slug>; kb set <fn> block=<slug>/block
```

Accepting writes claims through `kb new` and `kb set`; the candidate stays a
candidate and is replaced on the next run.

## 18. Operational boundaries

Knowledge representation transfer is complete. Reconciliation reviews with a
reason are supported unresolved data; a review does not verify an access,
change evidence, or raise a claim level. Stock-code executable qualification
is not a migration acceptance requirement.

The execution gate is required for changed patch instructions and their
necessary environment. Stock-code claims express uncertainty through levels
and review records. A new executable stock-code proof requires a named patch
obligation or calibration decision and prior user agreement on that scenario.

Evidence records remain data when their implementation is archived. Archived
TEST evidence and TEST evidence without `supports` provide no grounding. A
claim with no other grounding is a `candidate`; L0, image bytes and analyzed
code retain their independent grounding roles.

`contracts.toml` owns the command and ownership declarations consumed by KB.
`bench.toml` owns benchmark questions, budgets and content expectations.
Documentation is not an input to those readers. The knowledge-access section
of `AGENTS.md` has one generator, `kb.project:agents`, and one projection check.

Small packages state their user scenario and the knowledge or capability they
change. Run affected tests immediately; full checks run before flashing and
before closing an engineering track. A package that doubles its estimated
size or time, or changes direction, stops for a user decision.
