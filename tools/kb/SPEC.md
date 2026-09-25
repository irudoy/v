# kb: knowledge model and entry point

This specification defines how the repository stores and serves what it knows
about the HR-series firmware, and `kb`, the tool through which people and
agents read and change that knowledge. It fixes the storage of symbols,
meanings, families, links, and evidence; names and references; layouts; the
compiler, the graph schema, and the graph fingerprint; per-worktree graph
instances; the `kb` commands and the MCP server; the gates; the projection
registry; the migration of current registry fields; the access guard; and the
acceptance questions with their output budgets.

The model is implemented in the stages of [Transition](#21-transition). A
registry keeps the ownership that [Ownership by stage](#19-ownership-by-stage)
assigns it until the stage that converts it lands.

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
  found nothing") are stored with their evidence and search; `unknown` is
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
  its registry; the file is removed in stage 11.
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
  the same write.

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

References stored in files take three forms: `<name>/<kind>` for a meaning
or a designed entity, `<name>/<kind>/<layout>` for a symbol, and
`<layout>:<address>` for a location, which evidence uses in `at`. `kb rename`,
`kb merge`, and `kb move` rewrite every stored reference they affect.

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
  registry that `kb sync` enrolls from stage 2. The `names` check fails while
  such a symbol lacks its name.

### 5.5 Renames, merges, and moves

- `kb rename <meaning> <semantic-name>` names a meaning. Each symbol's
  previous full reference moves to its `former` list, every `[[...]]`
  citation is rewritten, and the file is renamed, all in one write.
- `kb merge <a> <b>` joins two symbols at the same layout, kind, and address,
  or two meanings found to be one. The survivor keeps its name; the other name
  becomes a redirect.
- `kb move <symbol> <meaning>` corrects a wrong homology. The symbol takes the
  target meaning's name if it has one and keeps its generated name otherwise;
  its previous reference becomes a redirect.
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
  bit or value, and a diagnostic binding.
- A `candidate` claim needs at least one evidence item. A `code` claim needs
  evidence of a kind that grounds `code` ([Evidence](#76-evidence)). A
  `silicon` claim needs `hardware` evidence whose `key` names a record of
  `patches/hardware-results.toml` with a passing result.
- `relies` on a link or an evidence item names the property of its `to` end
  that the owning claim rests on:

| `relies` | Bound on the owning claim | Legacy suffix |
|---|---|---|
| `structure` | `code` when L0 of the layout holds the `to` symbol as the code object the claim uses, `pattern` otherwise | `@structural` |
| `level` | The effective level of the `to` entity | `@confidence` |
| `contract` | The effective `contract_level` of the `to` function | `@contract_conf` |
| `scale` | The effective `scale_level` of the `to` entity | `@scale_conf` |

- The effective level of a claim is the minimum of its declared level and
  the bounds of the links and evidence items of that claim that carry
  `relies`. Links and evidence without `relies` state facts and do not bound
  the claim. Mutual dependencies resolve to the greatest fixed point, so a
  cycle takes the minimum of its members.
- The `levels` check fails when a declared level exceeds its effective level.

### 7.2 Meanings

Keys of every meaning:

| Key | Type | Required | Content |
|---|---|---|---|
| `title` | string of at most 72 characters | yes | What the meaning is, in one line |
| `summary` | string | no | The mechanism: what produces the datum, what reads it, and how |
| `note` | array of strings | no | Caveats, open questions, and context the summary does not carry |
| `level` | level | yes | Level of the identity claim |
| `home` | layout id | when the meaning has more than one symbol | The layout that bare addresses in prose refer to; a meaning with one symbol takes its layout |
| `role` | string | for `fn` and `tbl` | The role from the vocabulary of the kind |
| `block` | block reference | for reviewed `fn` meanings from stage 6 | The architecture block; other kinds may pin one |
| `former` | array of names | no | Former names, each a permanent redirect to this meaning |

Keys by kind:

| Kind | Key | Content |
|---|---|---|
| `ram`, `reg` | `width` | Access width in bits: 8, 16, or 32 |
| | `signed` | Two's complement when true |
| | `unit`, `scale`, `to_raw`, `scale_level` | [Scale](#scale) |
| | `[[bit]]` | Named bits of a bit field: `bit`, `name`, `summary`, `level`, and `[[bit.evidence]]` |
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
| | `[interp]` | Interpolation signature of a kernel or wrapper: `access` (`explicit` or `implicit`), `kernel` (a `fn` reference), `cols`, `rows`, `step`, `storage`, `x_storage`, and `y_storage` |
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
| Overrides | `width`, `signed`, `storage`, `cols`, `rows`, `points`, `count`, `unit`, `scale`, `to_raw`, and `scale_level` where the layout differs from the meaning; for `dtc`, `index` and `attribute` |
| `note` | Prose about this layout |
| `[[symbol.evidence]]` | Evidence of identity or homology |

- An anchor symbol carries evidence with `supports = "identity"` of a kind
  that grounds its level on its own layout, or its meaning has a link with
  `relies` that holds on the layout through evidence of that layout.
- Every other symbol carries evidence with `supports = "homology"` whose `to`
  names a symbol of the same meaning, or the location on the layout of such
  a symbol that the evidence compares with `at`. Every homology chain reaches
  an anchor.
- Homology evidence is `masked-match`, `literal-pool`, `function-match`,
  `call-ordinal`, `interp-contract`, `did-table`, or `byte-identical`
  evidence, or `l0` evidence of the symbol's own layout. The same kinds apply
  inside a family and across families, and a match that is not unique grounds
  no more than `candidate`. `vendor`, `registry`, and `diagnostic` evidence
  never supports homology, and name, neighbourhood, or graph similarity is
  not evidence.
- A symbol stores no calibration values. The image catalog fixes the bytes of
  every image, and `kb show` reads the values from them.

### 7.4 Statuses

| Key | Content |
|---|---|
| `layout` | Layout id |
| `state` | `absent` or `unresolved` |
| `method` | For `unresolved`: the evidence kind of the search, such as `masked-match` |
| `target` | For `unresolved`: what the search looked for, as a reference or a location |
| `count` | For `unresolved`: the number of matches; 0 for none, more than 1 for an ambiguous search |
| `l0` | For `unresolved`: the first 16 hexadecimal digits of the SHA-256 of the layout's L0 manifest at search time |
| `note` | Prose |
| `[[status.evidence]]` | Required for `absent` |

- A layout carries at most one symbol or one status of a meaning.
- `absent` states that the mechanism does not exist on the layout. Its
  evidence comes from the layout's own code, for example a DID table without
  the DID or a producer path that the code lacks.
- `unresolved` states that a search found no unique symbol. When the L0
  manifest of the layout changes, the search is stale: `kb brief` lists it,
  and staleness is not a check failure.
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
| `offset` | Offset for `base` and `target` |
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
| `selector` | datum or `fn` | datum | `to` selects between alternatives | Evidence |
| `threshold` | datum or `fn` | `tbl`, `ram` | The datum or function compares with `to` | Evidence |
| `base` | `ram` | `ram` | The datum is addressed at `offset` from `to` | `indirect` evidence |
| `target` | `hook` | `fn`, `tbl`, `const` | The stock word points at `to`, plus `offset` | Image bytes of every image of the layout |
| `source` | `did` | `ram`, `reg`, `const` | The DID returns `to` | Image bytes: the DID table entry |
| `monitor` | `dtc` | `fn` | `to` sets the DTC | Evidence |
| `depends` | any | any | An untyped dependency with its legacy `role` | Evidence |

- A link claims every layout where both ends have symbols, unless `layouts`
  restricts it.
- On each claimed layout a link holds when its verifier reproduces it, when
  an `indirect` evidence item of that layout explains the access, or, for a
  type that evidence verifies, when evidence of that layout supports it or
  the link holds on another layout of the same family.
- A link that does not hold on a claimed layout is unverified there. `kb
  show` marks it, and from stage 8 the `links` check fails on it.
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
| `count` | Number of matches |
| `value` | The observed value: bytes, a literal, an ordinal, a hash class, or an equation |
| `sha256` | Digest of compared bytes |
| `mode` | For `indirect`: `pointer`, `gbr`, `window`, `block-copy`, or `base` |
| `path` | A repository path |
| `key` | An identifier inside `path`, a source pack, or a registry |
| `note` | Prose |

| Kind | Content | Required keys | Grounds up to |
|---|---|---|---|
| `l0` | An access, call, or reference of L0 at `at` | `at` | `code` |
| `literal-pool` | The pool literal at `at` and the literal at the location `to`, at the same ordinal of homologous code; `value` is the literal at `at` | `at`, `to`, `value` | `code` |
| `masked-match` | Instruction words at `at` equal to those at the location `to` with PC-relative displacements masked; `value` is the word count | `at`, `to`, `count`, `value` | `code` when `count` is 1 |
| `function-match` | Equal exact, mnemonic, or shape hash of two functions; `value` names the hash class, and `count` is the number of functions of the layout with that hash | `at`, `to`, `count`, `value` | `code` when `count` is 1 |
| `call-ordinal` | The call or the call operand at the same ordinal of homologous functions; `count` is the number of candidates at that ordinal | `at`, `to`, `count`, `value` | `code` when `count` is 1 |
| `interp-contract` | The same interpolation contract and operands | `to`, `key` | `code` |
| `did-table` | The DID's slot in the service pointer table of the image | `at`, `value` | `code` |
| `byte-identical` | Identical bytes over a range | `at`, `to`, `sha256` | `code` |
| `rom-bytes` | Bytes of every image of the layout at `at` | `at`, `value` | `code` |
| `trace` | The claim follows through the contract or behavior of a function | `to`, `relies` | `code` |
| `indirect` | An access that L0 does not attribute directly | `at`, `mode` | `code` |
| `spec` | A narrow specification of the repository, a decoding rule, or a published standard | `path` or `key` | `code` |
| `arithmetic` | An equation that `kb check` evaluates | `value` | `code` |
| `test` | An executable test of the repository | `path`, `key` | `code` |
| `manual` | A vehicle or MCU manual of the source packs | `key` | `candidate`; `code` for the identity of a `reg` meaning from the MCU hardware manual |
| `diagnostic` | A record of the diagnostic corpora | `key` | `candidate` |
| `registry` | A legacy or vendor definition entry | `value` or `path` | `candidate` |
| `vendor` | A competitor product or catalog | `key` | `candidate` |
| `hardware` | A measurement on the owned ECU | `key` | `silicon` when the record of `patches/hardware-results.toml` passes |

- Evidence of one layout names locations of that layout; homology evidence
  names the other symbol in `to`.
- `kb check` evaluates every `arithmetic` equation and compares every
  `rom-bytes` value with the images of the layout.

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
| `[editor]` | `tbl`, `axis`, `const` | `name`, `category`, `order`, `emit`, `format`, `fine`, `coarse`, `mask`, `static_axis`, `static_axis_name`, `static_axis_operand`, `static_axis_x`, `static_axis_x_name`, `static_axis_y`, `static_axis_y_name` |
| `[[editor.view]]` | `tbl`, `const` | A masked view: `name`, `category`, `mask`, `unit`, `scale`, `to_raw`, `format`, `fine`, `coarse` |
| `[logparam]` | `ram`, `reg` | RomRaider logger parameter: `id`, `unit`, `scale`, `static_axis_name` |
| `[[diagnostic]]` | any meaning | Diagnostic binding: `id`, `kind`, `label`, `key`, `claim` (an inline table of `label` and `id`), `applicability`, `scope` (image or layout ids), `priority`, `level`, `note`, and `[[diagnostic.evidence]]` |

`editor.name` is the name the editors show; it is not the name of the
meaning. The generators of the editor definitions, the RomRaider files, and
the diagnostic bindings read these tables.

### 7.9 Designed entities

| Kind | Keys |
|---|---|
| `stage` | `title`, `lane` (`flow` or `support`), `order`, `summary` |
| `block` | `title`, `stage`, `summary`, `generic` (a service block that no single stage owns), `specs`, `home` |
| `endpoint` | `title`, `direction` (`input`, `output`, or `bidirectional`), `block`, `peripheral`, `summary`, `registers` (`reg` references), `functions` (`fn` references), `specs` |
| `chain` | `title`, `summary`, `quantity`, `output`, `specs`, `home`, and `[[step]]` |
| `signal` | `title`, `domain`, `priority`, `coverage`, `basis`, `observes`, `note` |
| `field` | `signal`, `source`, `kind`, `width`, `signed`, `scale`, `profiles`, `page`, `offset`, `context`, `position` |
| `feature` | `title`, `summary`, `acceptance`, `requires`, `vendor`, and `[[target]]` |

`specs` is an array of repository paths of narrow specifications.

Blocks:

- A `fn` meaning joins a block through its `block` key; a `ram`, `tbl`, or
  other meaning may pin a block with the same key.

Chains:

- `[[step]]` keys: `from`, `to`, `effect`, `sign` (`positive`, `negative`,
  or `none`), `via` (an array of `fn` references), `note`, and `specs`.
  Steps are ordered by their position in the array.
- `effect` is one of `scales`, `looks-up`, `indexes`, `converts`, `adds`,
  `multiplies`, `selects`, `compares`, `subtracts`, `copies`, `gates`,
  `limits`, `stores`, `filters`, `feeds`, `integrates`, `schedules`,
  `receives`, `overrides`, `masks`, `drives`, `detects`, `transmits`, or
  `learns`.
- A step `note` states only the arithmetic that relates `to` to `from`.
  Conditions and alternatives are links of the meanings (`selector`, `copy`,
  `threshold`), so queries reach them.
- `output` is a reference to the meaning the chain computes.

Signals:

- `priority` is `core`, `high`, `medium`, or `research`; `coverage` is
  `fixed`, `rotating`, `latched`, `stock-can`, `external`, or `absent`;
  `basis` is `exact-code`, `exact-code+homologous-diagnostic`,
  `measurement-requirement`, `passive-can`, or `patch-design`.
- `observes` is an array of meaning references. The DIDs of a signal come
  from the `did` meanings whose `source` is an observed meaning, and its
  current fields from the fields whose `signal` names it; neither is stored.

Fields:

- `kind` is `ecu_ram`, `rom_configuration`, `runtime_state`, or
  `telemetry_state`.
- `signal` names the signal that the field serves. An `ecu_ram` field
  requires it; a field of another kind may carry it.
- The `source` of an `ecu_ram` field is a `ram` or `reg` meaning, and the
  field takes its scale and unit from that meaning. The source of a
  `rom_configuration` field is a `tbl` or `const` meaning, of a
  `runtime_state` field an allocation of the `runtime` feature, and of a
  `telemetry_state` field a state item of the `can_telemetry` feature. Only
  fields whose kind is not `ecu_ram` carry `scale`.
- `width`, in bytes, and `signed` describe the field on the wire. The
  `fields` check requires them to fit the source meaning.
- `profiles`, `page`, and `offset` place a stream field; `context` and
  `position` place a context field.

Features:

- `acceptance` states the observable criterion that the feature works;
  `requires` lists the meanings and designed entities it needs on every
  target layout; `vendor` lists the competitor products that offer it, for
  the parity catalog.
- `[[target]]` keys: `layout`, `status` (`supported`, `planned`, or
  `unsupported`), `note`, and the keys of the feature. An `unsupported`
  target names in `note` the meanings whose status blocks it.
- The `runtime` feature holds the runtime allocation of each layout, its
  ROM and RAM relocation, and the build variants. `can_telemetry` holds the
  wire constants, profiles, and contexts, and each of its targets lists in
  `unavailable` the fields whose source meaning has a status on the layout.
  `definitions` holds the image header metadata, checksums, and switches of
  the editor definitions.
- `map_switching`, `rolling_launch`, and `can_telemetry` hold their layout
  keys and, under their own hook keys, the `hook` meanings they redirect with
  the replacement of each. The build applies them in that order, so the value
  of a word before a feature redirects it is the replacement of the last
  earlier feature that redirects the same word, or the stock value; it is
  derived, not stored.
- RAM and ROM that a feature allocates are not meanings. The feature names
  its allocations, and fields and hooks refer to them by allocation name.

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
  ([Ownership by stage](#19-ownership-by-stage)).
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
- A layout joins with a new export of all its files; a partial export, an
  export of another program, or an image digest other than the catalog digest
  is refused.

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
  moved into GBR by `ldc`. A delay slot executes on the path of its branch,
  and a call clears r0 through r7 after its delay slot. An access through
  such a register yields the accessed address, the literal, its pool address,
  and the base register; an R0-indexed access whose index is unknown yields
  the table base.
- The function that contains an instruction address, and the table that
  contains a ROM address, from the `tbl` symbols and their dimensions.

### 8.6 Local exports

- Decompilations and listings stay in the export directory of
  `tools/ghidra/` as the cache of `kb code`, which calls
  `tools/ghidra/decompile.sh`.
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
- `tools/kb/config.toml` and `tools/kb/projections.toml`.
- Until a registry converts, the registry itself, read by its adapter
  ([Migration map](#20-migration-map)).
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

`.kb/lock` serializes syncs and writes within a working tree. A waiting
process prints the holder's command and process id and waits up to the
timeout in `tools/kb/config.toml`, then exits with code 7.

### 9.7 Legacy graph

Until stage 7 the graph also holds the elements that the loaders of
`tools/memgraph/` write for the current readers. Every element the compiler
writes carries the label `:Kb` in addition to its own labels, and the
compiler deletes and replaces only `:Kb` elements. The legacy loaders and
readers keep using the main instance until their stage converts them.

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
| `Step` | `<chain slug>#<order>` | `effect`, `sign`, `note` | `claim` |
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
| `CALL` | `Function` | `Function` | `sites` | `l0` |
| `ACCESS` | `Function` | `Location` | `modes`, `sites` | `l0`, `derived` for paired literals |
| `WRITER`, `READER`, `INPUT`, `COPY`, `INDEX`, `AXIS`, `LOOKUP`, `SELECTOR`, `THRESHOLD`, `BASE`, `TARGET`, `SOURCE`, `MONITOR`, `DEPENDS` | `Meaning` | `Meaning` | the link keys | `claim` |
| the same types | `Symbol` | `Symbol` | `layout`, `verified`, and the link's `role`, `slot`, and `offset` | `derived` |
| `CITES` | `Meaning`, `Symbol` | `Meaning`, `Symbol`, `Entity` | `kind`, `supports`, `relies` | `claim` |
| `ANALOG` | `Meaning` | `Meaning` | `note` | `claim` |
| `BLOCK` | `Meaning` | `Entity` (block) | | `claim` |
| `STAGE` | `Entity` (block) | `Entity` (stage) | | `claim` |
| `REGISTER`, `FUNCTION` | `Entity` (endpoint) | `Meaning` | | `claim` |
| `STEP` | `Entity` (chain) | `Step` | `order` | `claim` |
| `FROM`, `TO`, `THROUGH` | `Step` | `Meaning` | | `claim` |
| `OUTPUT` | `Entity` (chain) | `Meaning` | | `claim` |
| `OBSERVES` | `Entity` (signal) | `Meaning` | | `claim` |
| `SERVES` | `Entity` (field) | `Entity` (signal) | | `claim` |
| `CARRIES` | `Entity` (field) | `Meaning` | | `claim` |
| `REQUIRES` | `Entity` (feature) | `Meaning`, `Entity` | | `claim` |
| `TARGETS` | `Entity` (feature) | `Layout` | `status` | `claim` |
| `PROPOSES` | `Candidate` | any node | `score` | `candidate` |

- A link declared on a meaning is a relationship between meanings. The
  compiler also materializes it between the symbols of every claimed layout,
  with `verified` stating whether it holds there ([Links](#75-links)).
- One `CALL` joins a caller and a callee, and one `ACCESS` of each producer
  joins a function and a location, so path queries see one edge per pair.
  `sites` of a `CALL` lists the call instructions. `sites` of an `ACCESS`
  holds one map per instruction with `site`, `mode`, `width`, and for a pool
  literal `pool`, and for a paired literal also `literal`, `base`, and
  `indexed`; `modes` lists the distinct modes.
- `ACCESS` with producer `l0` records every reference of an instruction to RAM
  or a register, with the reference type of L0 as mode, every data or
  parameter reference to ROM, and every pool literal that names RAM or a
  register, with mode `literal`. `ACCESS` with producer `derived` records the
  literal pairs of [Derivations](#85-derivations), with modes `load`, `store`,
  and `update`.

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
in the main instance until stage 7, and the compiler deletes and replaces
only `:Kb` elements.

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
  `tools/kb/config.toml`; stage 1 sets it from the measured memory of a graph
  with the L0 of all layouts.
- A linked working tree's graph is rebuilt from git by `kb sync`; only the
  main instance is backed up.
- Until stage 7 the legacy readers connect to the main instance from every
  working tree, as they do now.

## 12. Commands

### 12.1 Invocation

`tools/kb` is a uv workspace member that installs the `kb` console script, so
`uv run kb <command>` works in every working tree after `make setup`.
`uv run kb mcp` serves the same operations over MCP on standard input and
output.

Options common to the read commands:

| Option | Effect |
|---|---|
| `--layout <id>` | Restrict the answer to one layout |
| `--budget <tokens>` | Output budget; the default per command is in `tools/kb/config.toml` |
| `--full` | No budget |
| `--json` | Structured output for programs, without a budget |
| `--no-sync` | Fail instead of syncing a stale graph |
| `--expand <ref>` | `kb impact` and `kb path`: expand a hub; repeatable |
| `--limit <n>` | `kb path`: paths to print; `kb find`: results to print |

### 12.2 Read commands

| Command | Answers |
|---|---|
| `kb brief` | Graph state, layouts with symbol and status counts, the current transition stage and registry owners, open gaps ranked by feature impact, stale searches, pending candidates, and the table of questions and commands |
| `kb show <ref>` | The entity: identity, symbols per layout, statuses, links in both directions grouped by type, evidence, analogs, and citations |
| `kb at <layout>:<address>` | The symbol at the address or the function or table that contains it, and the L0 facts at that address |
| `kb where <ref>` | The symbol or status of a meaning on every layout |
| `kb impact <ref>` | Every entity that depends on the reference through links, chains, fields, and features, with the insertion points per layout of a change to it |
| `kb path <a> <b>` | The shortest typed paths between two entities |
| `kb gaps [--feature <f>] [--layout <l>] [--catalog]` | Required meanings without a symbol, grouped by status |
| `kb suggest <ref> --layout <l>` | Candidate symbols of a meaning on a layout, one line per channel with the evidence kind it would record |
| `kb suggest --blocks --layout <l>` | Block candidates for the unplaced functions of a layout ([Graph algorithms](#16-graph-algorithms)) |
| `kb find <text>` | Entities ranked by name, former name, title, and summary |
| `kb code <ref> [--layout <l>]` | Decompilation or listing of a function symbol through `tools/ghidra/decompile.sh` and its cache |
| `kb log <ref>` | The history of the entity through renames and redirects |
| `kb raw <ref>` | The canonical file of the entity |
| `kb cypher <query>` | A read-only Cypher query over the working tree's instance after the fingerprint check |
| `kb audit` | Disagreements of one fact between registries (stage 2) |
| `kb bench [--all] [--only <id>]` | The acceptance questions of the current stage, or all, against their budgets and baselines ([Acceptance questions](#18-acceptance-questions)) |
| `kb check [--changed]` | The gates of [Checks](#13-checks) |

### 12.3 Write commands

| Command | Effect |
|---|---|
| `kb new <kind> <layout>:<address>` | A meaning with one symbol, named or with a generated name |
| `kb new <kind> <slug>` | A designed entity |
| `kb set <ref> <key>=<value>...` | Keys of an entity or a symbol |
| `kb bind <meaning> <layout>:<address>` | A symbol of an existing meaning on another layout, with evidence |
| `kb absent <meaning> --layout <l>` | Status `absent` with the evidence that removes the mechanism |
| `kb unresolved <meaning> --layout <l>` | Status `unresolved` with the method and target of the search |
| `kb link <from> <type> <to>` / `kb unlink` | A typed link and its evidence |
| `kb rename`, `kb merge`, `kb move` | [Renames, merges, and moves](#55-renames-merges-and-moves) |
| `kb retire <ref>` | Retires a meaning or designed entity; its names stay reserved |
| `kb family new`, `kb family add` | [Layouts and families](#3-layouts-and-families) |
| `kb apply <batch> [--dry-run]` | A batch of the operations above as one change |
| `kb fmt [<path>...]` | Rewrites entity files in canonical form after a merge |
| `kb sync [--full]` | Compiles and loads the graph |
| `kb instance up\|down\|status\|prune` | [Instances](#11-instances) |

Every write:

1. takes the lock and syncs a stale graph;
2. builds the change in memory and runs the schema, reference, uniqueness, and
   affected checks on the result;
3. refuses the whole change with exit code 3 and the failed checks when any
   check fails;
4. writes the files in canonical form through temporary files and renames,
   updates the graph, and writes `:Meta`;
5. prints the changed files and one line per change.

A batch is a TOML file of `[[op]]` tables, each with `cmd` and the arguments
of one command. `kb apply` applies all operations or none. Subagents write
only through batches, so the parent reviews one diff.

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
  reads a datum need not compute each of its outputs from it. Chains, fields,
  and features join the closure in their stages.
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

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | A check failed |
| 2 | Usage error |
| 3 | Write refused |
| 4 | Ambiguous reference |
| 5 | Reference not found |
| 6 | Graph unavailable or stale |
| 7 | Lock timeout |

### 12.6 MCP

`kb mcp` exposes one tool per read command and `kb_apply` for writes, with the
same arguments, budgets, and exit semantics as errors. The local `.mcp.json`
registers it; `tools/kb/README.md` gives the entry.

## 13. Checks

`uv run kb check` runs every active check over the working tree, and
`--changed` runs the checks whose inputs changed, with their dependents. Each
failure is one line with the file, the key, and the command that fixes or
explains it. Stage 1 creates the `kb` package with the `l0` check, and from
then on `make check` runs `uv run kb check`. The current gates keep running
until the stage that replaces them.

| Check | Requires | Active from stage |
|---|---|---|
| `l0` | Every manifest matches its files, digests, and row counts; the image digest matches the catalog; the Ghidra version matches the pin; the script digests match the scripts of `tools/ghidra/`; every file is in normal form | 1 |
| `schema` | Every entity file and every adapted registry row has the keys, types, and vocabularies of its kind | 2 |
| `canonical` | Every entity file equals the canonical rendering of its parse | 3 |
| `names` | Name grammar; uniqueness within a kind for semantic names and across kinds for generated names; former names stay reserved; a new generated name passes the rules of [Generated names](#54-generated-names) when it is drawn | 2 |
| `references` | Every stored reference and every `[[...]]` citation resolves, and none uses a former name | 2 |
| `symbols` | At most one symbol per layout, kind, and address; at most one symbol or status per meaning and layout; every address lies in the address space of its kind on the MCU of the layout; every `fn` symbol is a function entry of L0 | 2 |
| `homology` | Every symbol is an anchor or reaches one through homology evidence of an accepted kind ([Symbols](#73-symbols)) | 3 |
| `levels` | No declared level exceeds its effective level; `code` and `silicon` claims carry grounding evidence; every `hardware` key names a passing record; every `arithmetic` equation holds | Reported by `kb audit` from 2; a gate from 5 |
| `links` | The kinds of both ends and the keys match the link type; every link holds on every claimed layout ([Links](#75-links)) | Kinds from 2; holding from 8 |
| `widths` | Access widths in L0 agree with the `width` of `ram` and `reg` symbols; every field width fits its source | Fields from 4; symbols from 8 |
| `image-bytes` | `rom-bytes` values, hook `target` words, DID table entries, and the storage and dimensions of `tbl`, `axis`, and `const` symbols agree with every image of the layout | Hooks and DIDs from 3; all ROM symbols from 8 |
| `statuses` | `absent` carries evidence; `unresolved` carries `method`, `target`, `count`, and `l0`; stale searches are reported and do not fail | 3 |
| `blocks` | Every reviewed `fn` meaning has a block or appears in the unplaced report, as `tools/romviz/architecture.py check` reports them; every block names a stage | 6 |
| `chains` | Every step resolves; `effect` and `sign` are in their vocabularies; a step note matches the arithmetic grammar of `tools/kb/config.toml`; `output` is the `to` of a step | 6 |
| `fields` | Every field names a source of its kind, and every `ecu_ram` field a signal; an `ecu_ram` field carries no scale; on every layout that a feature targets, each source meaning of its fields has a symbol, or a status and an entry in the target's `unavailable` list | 4 |
| `projections` | Every registered projection equals its rendering, and every generated file is registered | 2 |
| `guard` | `.claude/settings.json` runs `tools/kb/hook.py`; `.ignore` lists the guarded trees and projections; the path lists of the hook match `tools/kb/projections.toml` | 2 |

A write command runs the `schema`, `references`, `names`, `symbols`, and
`canonical` checks on its result and the other active checks on the entities
it touches ([Write commands](#123-write-commands)).

An evidence item that an adapter maps from a legacy token keeps the token in
`legacy`. The `schema` check does not require the keys of its kind; `kb audit`
lists every such item that lacks them until the conversion of its registry
types it.

## 14. Projections

`tools/kb/projections.toml` registers every generated file of the repository,
including the files that current generators already produce:

```toml
[[projection]]
path = "defs/JK08A.funcs.csv"
generator = "kb.project.ledgers:funcs"
stage = 5
inputs = ["kb/fn/", "l0/7mfk/"]
consumers = ["tools/maps/build_tracker.py"]
read = "guarded"
```

| Key | Meaning |
|---|---|
| `path` | Generated file, or a file and a marked section of it |
| `generator` | The function or command that renders it |
| `stage` | The transition stage from which `kb` generates it; a file without `stage` keeps its current generator |
| `inputs` | Paths whose change requires regeneration |
| `consumers` | Tools, tests, and external programs that read it |
| `read` | `guarded`: agents read the knowledge through `kb`; `open`: anyone reads the file |

- A projection is regenerated byte-identically; `kb check` compares every
  registered projection with its rendering.
- No projection is edited by hand: the access guard refuses the edit and the
  check reports the difference.
- Editor definitions, the TunerPro and RomRaider files, and the host decoder
  are `open`. Ledgers and registries whose facts live in `kb/` are `guarded`
  from their conversion stage.
- A projection without consumers is removed in stage 11.
- `AGENTS.md` carries one generated section between the markers
  `<!-- kb:begin -->` and `<!-- kb:end -->`: the table of questions and
  commands and the ownership table of the current stage. The section is a
  projection with its markers as the path suffix.

## 15. Access guard

The guard keeps agents on `kb` for knowledge that has an owner file under
`kb/`, `l0/`, or a guarded projection. It is a convenience boundary, not a
security boundary: the gates validate every file whatever wrote it.

- The tracked `.claude/settings.json` registers a PreToolUse hook for `Read`,
  `Edit`, `Write`, `MultiEdit`, `NotebookEdit`, `Grep`, `Glob`, and `Bash`.
  The hook runs `tools/kb/hook.py`, which uses only the Python standard
  library and reads its path lists from `tools/kb/config.toml` and
  `tools/kb/projections.toml`.
- The hook denies with `permissionDecision = "deny"` and a reason that names
  the command to use:

| Tool call | Decision | Reason names |
|---|---|---|
| `Edit`, `Write`, `MultiEdit`, `NotebookEdit` under `kb/`, `l0/`, or on a projection | Deny | The write command, or the generator of the projection |
| `Read` under `kb/` | Deny | `kb show` and `kb raw` with the reference the path maps to |
| `Read` under `l0/` | Deny | `kb at`, `kb code`, and `kb cypher` |
| `Read` of a guarded projection | Deny | `kb show`, `kb where`, or `kb find` |
| `Grep` or `Glob` whose path lies in a guarded tree or file | Deny | `kb find` |
| `Bash` whose command names a guarded path, unless it is `uv run kb` or a git command from the allow list | Deny | The matching `kb` command |

- The git allow list covers `status`, `add`, `commit`, `diff`, `log`,
  `show --stat`, `restore`, `checkout`, `switch`, `stash`, `rebase`, `merge`,
  `mv`, and `rm`, so diffs stay reviewable.
- `.ignore` excludes the root trees `kb/` and `l0/` and guarded projections
  from ripgrep, so a repository-wide `Grep` does not return their contents.
- The Memgraph MCP server and Memgraph Lab stay open for exploring the main
  instance. They read the graph without the fingerprint check, so a gate, a
  generator, or an evidence item never rests on their answers; `kb cypher`
  answers the same queries over the working tree's instance.
- `KB_GUARD=off` in the environment disables the hook for maintenance.
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
kind = "ecu_ram"
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

The field takes `x*100/128` from the meaning. The `can_telemetry` targets of
`jk78c`, `1nd`, and `1me3b` list `normalized_load_raw/field` in
`unavailable`, and the `fields` check accepts the list because the source
meaning has a status on each of them.

```text
$ uv run kb where normalized_bfs_snapshot
normalized_bfs_snapshot/ram  code  home 7mfk  Scheduler snapshot of the normalized Base Fuel Schedule
1me3b  unresolved  masked-match 7mfk:0003bd1c  count 0
1nd    unresolved  masked-match 7mfk:0003bd1c  count 0
7mfk   ffff102c  code  copy of normalized_bfs/ram/7mfk-ffff1048  indirect block-copy 7mfk:00020f18
jk00c  ffff1034  code  copy of normalized_bfs/ram/jk00c-ffff1050  indirect block-copy jk00c:00020f50
jk00d  ffff1034  code  copy of normalized_bfs/ram/jk00d-ffff1050  indirect block-copy jk00d:00020f50
jk78c  unresolved  masked-match 7mfk:0003bd1c  count 0

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
`input` links ([Evidence tokens](#207-evidence-tokens)); review turns the
second into the `copy` link and adds the selectors that the step note
stated. Question 12 of [Acceptance questions](#18-acceptance-questions) then
reads:

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

## 18. Acceptance questions

Each question is answered by one command within its budget. A token is one
third of a UTF-8 byte of output, rounded up, as in [Output](#124-output). The
baseline is the output an agent reads to answer the same question with `rg`
and file reads over the registries; stage 2 records each baseline in
`tools/kb/bench.toml`, and a `kb` answer must stay within its budget and
below its baseline.

| # | Question | Command | Budget | From stage |
|---|---|---|---|---|
| 1 | What is at an address of another layout | `kb at jk00d:ffff1034` | 600 | 2 |
| 2 | Where a meaning is on every layout | `kb where normalized_bfs_snapshot` | 400 | 3 |
| 3 | What depends on a table | `kb impact 7mfk:0000a4aa` | 1500 | 2 |
| 4 | How coolant temperature reaches the intake-cam target | `kb path 7mfk:ffff1079 7mfk:ffff2326` | 1500 | 2 |
| 5 | Which telemetry sources lack a symbol on a layout | `kb gaps --feature can_telemetry --layout 1nd` | 1000 | 3 |
| 6 | Candidates for a producer on another family | `kb suggest 7mfk:0003b75c --layout jk78c` | 1500 | 9 |
| 7 | Find entities by words | `kb find knock threshold` | 800 | 2 |
| 8 | The code of a function | `kb code jk78c:000564a4` | 4000 | 2 |
| 9 | The history of a symbol through its corrections | `kb log apc_output` | 800 | 3 |
| 10 | The state of the knowledge base | `kb brief` | 2000 | 2 |
| 11 | Why telemetry fields are unavailable on a layout | `kb gaps --feature can_telemetry --layout 1me3b` | 1000 | 3 |
| 12 | The block and chain steps of a function | `kb show 7mfk:0003deec` | 1200 | 6 |

- `tools/kb/bench.toml` becomes the owner of the budgets and stages in stage
  2, and the single-source gate reads this table against it.
- Every stage exit runs the questions active at that stage.

## 19. Ownership by stage

Every fact has one owner at every stage. A registry owns its facts until the
commit of the stage that converts it. From that commit `kb/` owns them, and
the registry is a projection until stage 11 keeps it generated or removes it.

| Registry | Facts | Converted in stage | Owner after conversion | The registry after conversion |
|---|---|---|---|---|
| `rom-images/roms.csv` | Images and digests | not converted | itself | |
| `rom-images/homology.toml` | Families and relationships; layouts from stage 2 | not converted | itself | |
| `defs/rom-identities.toml`, `defs/rom-inheritance.toml` | Image identities and definition inheritance | not converted | themselves | |
| Ghidra export directories | Code structure | 1 | `l0/<layout>/` | Local cache of decompilations, listings, and research exports |
| `tools/ghidra/symbols/<layout>.csv` | Curated function names of `1nd` and `7mfk` | 5 for `7mfk`, 9 for `1nd` | Names of `fn` meanings | Projection that `RenameFuncs.java` applies to Ghidra programs |
| `kb/names.csv` | Generated names of symbols in legacy registries | created in 2 | itself, shrinking with each conversion | Removed in 11 |
| `patches/rom-address-profiles.toml` | Target symbols, hooks, DIDs, telemetry sources and their unavailability, runtime allocations and variants, and their evidence | 3 | Meanings and statuses; targets of `runtime`, `map_switching`, `rolling_launch`, and `can_telemetry` | Projection |
| `patches/*-runtime-correspondence.csv` | Correspondence of source and target symbols by feature domain | 3 | Symbols and statuses | Projection |
| Symbol and hook-key tables of `patches/runtime_targets.py` | `7mfk` symbols of the feature meanings and the per-layout hook keys | 3 | Symbols and feature targets | The module reads them through the `kb` API |
| `defs/definition-projections.toml`, `defs/JK08A-*.definition-addresses.csv` | Relocated definition settings and table addresses | 3 | Target of `definitions`; `tbl` and `axis` symbols | Projection |
| `defs/*.interp.csv`, `defs/*.interp-correspondence.csv` | Interpolation kernels and wrappers | 3 | `fn` meanings with `[interp]` | Projection |
| `defs/vq37-native-tables.toml`, `defs/vq37-native-fuel-cut.toml` | Native tables and the fuel-cut mechanism of the VQ37VHR layouts | 3 | Meanings with symbols on `jk78c`, `1nd`, and `1me3b` | Projection |
| `defs/JK08A.tuning-signals.toml` | Observation needs | 4 | `kb/signal/` | Projection |
| `patches/can-telemetry-profile.toml` | Fields, contexts, and wire constants | 4 | `kb/field/`; `can_telemetry` | Projection |
| `defs/JK08A.overrides.toml` | Editor presentation, logger parameters, checksums, and switches | 4 | `[editor]` and `[logparam]` tables; `definitions`, `map_switching`, and `rolling_launch` | Projection |
| Generated telemetry copies: the schema, payload bindings, the host decoder, and dashboard metadata | Copies checked by `tools/single_source.py` | 4 | Generated from fields and meanings | Projection; the copy checks leave `single_source.py` |
| `defs/JK08A.funcs.csv`, `vars.csv`, `findings.csv`, `axes.csv` | Code knowledge of `7mfk` | 5 | `kb/fn/`, `kb/ram/`, `kb/reg/`, `kb/tbl/`, `kb/axis/` | Projection |
| `defs/JK08A.dtc.csv` | DTC descriptors of `7mfk` | 5 | `kb/dtc/` | Projection; the `dtc.csv` files of other images follow the `dtc` symbols of their layouts in stage 9 |
| `defs/JK08A.diagnostic-bindings.csv` | Diagnostic bindings | 5 | `[[diagnostic]]` tables | Projection |
| `defs/JK08A.architecture.toml` | Stages, blocks, endpoints, and chains | 6 | `kb/stage/`, `kb/block/`, `kb/endpoint/`, `kb/chain/` | Projection |
| Code graph of the `tools/memgraph/` loaders | Derived index | 7 | The compiler | The loaders move into the compiler |
| `defs/JK78C.vvel.md`, `defs/JK78C.can.md` | Symbols of the VVEL and CAN code of `jk78c` | 9 | Meanings with `jk78c` symbols | Narrow specifications of the mechanisms |
| `defs/JK08A.maps.csv` | Map tracker | generated | `tools/maps/build_tracker.py`, which reads the graph from stage 7 | Projection |
| `defs/1ND0A-1ME3B.census-correspondence.csv` | Census output | generated | Input of `kb family new` and `kb suggest` from stage 9 | Generated research output |
| `defs/<ROM>.xml`, `defs/<ROM>.xdf`, RomRaider plugin files, the host decoder | Editor and logger definitions | generated | Their generators, which read `kb` from the stages of their inputs | Projections with `read = "open"` |
| `patches/hardware-results.toml` | Hardware records | not converted | itself; `hardware` evidence cites it | |
| `patches/map-switching-layout.toml`, `patches/rolling-launch-layout.toml`, `patches/can-telemetry-layout.toml`, `patches/jk08a-runtime-reservations.toml`, `patches/checksum-layouts.toml`, `patches/runtime-target-payloads.toml` | Patch design; the `7mfk` hook words, map families, and DID slots that the adapters read from stage 2 | not converted | themselves | |
| Source packs under `refs/` | External corpora | not converted | themselves; `manual` and `diagnostic` evidence cites them | |
| Narrow specifications under `defs/` | Mechanisms in prose | not converted | themselves; `specs` keys and `spec` evidence cite them | |

## 20. Migration map

### 20.1 Adapters and names

- From stage 2 an adapter per registry reads it into the model without
  rewriting it, with the rules of this section. The conversion of a later
  stage writes the same model to `kb/` and turns the registry into a
  projection.
- Adapters join symbols into meanings by registry key: one key of the symbol
  tables of the address profiles, the correspondence files, and
  `patches/runtime_targets.py` across layouts, one native table id across
  targets, one field source across layouts, and one ledger address on
  `7mfk`. A correspondence row joins its target symbol to the meaning of its
  source symbol. Entries at one layout, kind, and address are one symbol.
- Joins apply in the order of their strength: correspondence rows with
  homology evidence (`mapped`), native table ids, field sources, registry
  keys, and correspondence rows that bind a target-specific role; within one
  strength, in the order of the adapters. A join that would give one meaning
  two symbols of one layout is refused, and `kb audit` lists it among the
  disagreements.
- A key of the symbol tables takes the kind `tbl` for a map family, `hook`
  when a feature redirects the word at every address of the key, and
  otherwise the kind that another registry gives a symbol at one of its
  addresses, or else the kind that its addresses admit.
- A meaning takes as its semantic name the registry id that names it: a key
  of `map_families`, `map_symbols`, `rolling_symbols`, or `can_symbols`, a
  key of the symbol tables of `patches/runtime_targets.py`, a native table
  id, or a curated function name of `tools/ghidra/symbols/<layout>.csv`. The
  source meaning of a telemetry field takes the field name without the `_raw`
  suffix. When registries name one meaning differently, the native table id
  wins over the hook key, the hook key over the symbol key, the symbol key
  over the curated function name, and the curated function name over the
  field name. Among symbol keys, a key with an entry on `7mfk` wins over a
  key without one, and then the key that sorts first. `kb audit` lists the
  other names, and the conversion records them as `former` names.
- A `hook` meaning is one ROM word. It takes the canonical key that
  `MAP_HOOK_KEYS` or `VQ37_MAP_HOOK_KEYS` of `patches/runtime_targets.py`
  joins to the per-layout keys of the word, or else the key of the first
  feature in build order that redirects the word; a per-layout key that
  equals the canonical key of another word gives no name. Each feature
  target keeps its own per-layout key for every hook it redirects.
- Architecture ids name designed entities, with hyphens replaced by
  underscores. Every other symbol receives a generated name in
  `kb/names.csv`.

### 20.2 JK08A ledgers

Stage 5. Before the conversion, one commit rewrites every evidence cell in
the canonical token order of the projection. The regenerated ledgers then
equal the originals except for removed `wave` tokens and for `site` tokens,
which the projection emits from L0 for every relation that L0 verifies. The
stage lists both differences, and the consumers of the ledgers pass their
tests on the regenerated files.

`defs/JK08A.funcs.csv`:

| Column | Target |
|---|---|
| `addr` | `fn` symbol on `7mfk` |
| `role` | `role` |
| `semantics` | `summary`, verbatim; the conversion proposes `title` from its first sentence |
| `contract` | `contract` |
| `contract_conf` | `contract_level` |
| `contract_evidence` | Links and evidence with `supports = "contract"` |
| `confidence` | `level` |
| `evidence` | Links and evidence with `supports = "identity"` |
| `note` | `note` |

`defs/JK08A.vars.csv`:

| Column | Target |
|---|---|
| `addr` | `ram` symbol, or `reg` symbol for an address in the peripheral space of the MCU |
| `semantics` | `summary`; proposed `title` |
| `units` | `unit` |
| `confidence` | `level` |
| `evidence` | Links and evidence with `supports = "identity"` |
| `note` | `note` |

`defs/JK08A.findings.csv`:

| Column | Target |
|---|---|
| `addr` | `tbl` symbol |
| `family` | `access`; an empty cell is `explicit` |
| `width`, `height` | `cols`, `rows` |
| `storagetype` | `storage` |
| `accessor` | `reader` link to the accessor |
| `confidence` | `level` |
| `evidence` | Links and evidence with `supports = "identity"` |
| `role` | `role` |
| `semantics` | `summary`; proposed `title` |
| `units` | `unit` |
| `scale_expr`, `to_byte` | `scale`, `to_raw` |
| `scale_conf` | `scale_level` |
| `scale_evidence` | Links and evidence with `supports = "scale"` |
| `note` | `note` |

`defs/JK08A.axes.csv`:

| Column | Target |
|---|---|
| `addr` | `axis` symbol |
| `kind` | `quantity` |
| `units`, `scale_expr`, `to_byte`, `scale_conf` | `unit`, `scale`, `to_raw`, `scale_level` |
| `scale_evidence` | Links and evidence with `supports = "scale"` |
| `note` | `note` |

The axis ledger has no identity column. The identity `level` of an axis is
`code` where the accessor census binds it to a table and `candidate`
otherwise, and `points` and `storage` come from the interpolation signature
of that binding.

`defs/JK08A.dtc.csv`:

| Column | Target |
|---|---|
| `index`, `record_addr`, `attribute_addr` | `dtc` symbol with `index` and `attribute` |
| `dtc`, `group` | `code`, `group` |
| `stock_attribute` | Not stored: image bytes |
| `disabled_attribute` | `disabled` |
| `confidence` | `level` |
| `note` | `title` |

`defs/JK08A.diagnostic-bindings.csv`:

| Column | Target |
|---|---|
| `firmware_label`, `firmware_addr` | The meaning and the `7mfk` symbol that hold the `[[diagnostic]]` table |
| `id`, `kind`, `applicability`, `priority`, `note` | The keys of the same names |
| `diagnostic_label`, `diagnostic_key` | `label`, `key` |
| `source_claim_label`, `source_claim_id` | `claim` |
| `confidence` | `level` |
| `rom_scope` | `scope` |
| `evidence` | `[[diagnostic.evidence]]` |

### 20.3 Address profiles and correspondence

Stage 3. `patches/rom-address-profiles.toml`, per image profile:

| Key | Target |
|---|---|
| `family`, `layout_source`, `inherits` | Derived from `rom-images/homology.toml` and the layouts |
| `rom_size`, `rom_delta`, `ram_delta`, the `free_*` and `injected_*` ROM and RAM bounds, `map_variant`, `telemetry_completion_variant`, `telemetry_zero_source`, `ignition_unreferenced_routine` | Keys of the `runtime` target |
| `capabilities.<feature>` | `status` of the target of `<feature>` |
| A key of `map_families`, `map_symbols`, `rolling_symbols`, or `can_symbols` whose value is an address | Symbol of the meaning the key names |
| `can_symbols` keys `feedback_config_record_value`, `mailbox_record_stock`, and `occupied_mailbox_record_stock` | `rom-bytes` evidence of the symbol at the matching address key |
| `can_symbols` keys `mailbox_index`, `mailbox_mask`, and `feedback_payload_offset` | Keys of the `can_telemetry` target |
| `telemetry_sources.<field>` | Symbol of the source meaning of the field |
| `telemetry_unavailable` | The `unavailable` list of the `can_telemetry` target, and a status of the source meaning of each listed field: `unresolved` when the evidence of the field's correspondence row, or else the telemetry evidence of the profile, states that a search found no counterpart (`no homolog`, `not traced`, `no match`), and `absent` otherwise |
| `map_hooks.<key>` = address, stock, replacement | The `hook` symbol at the address with a `target` link to the meaning at the stock value, and `<key>` with the replacement in the `map_switching` target |
| `rolling_hooks.<key>`, `can_hooks.<key>` = address, stock, base, replacement | The same in the `rolling_launch` and `can_telemetry` targets; `base` is derived ([Designed entities](#79-designed-entities)), and the conversion checks it |
| `rolling_diagnostics.<key>` = DID, pointer address, target, width | The `did` symbol at the pointer address with `number`, and the allocation `<key>` of `rolling_launch` at the target address with `width` |
| `extra_cvtc_storage`, `ignition_state_storage` | ROM allocations of the `map_switching` target |
| `evidence.<topic>` | `note` of the target of the topic's feature: `free_rom` and `free_ram` of `runtime`, `maps` of `map_switching`, `rolling` of `rolling_launch`, and `can` and `telemetry` of `can_telemetry` |

The conversion adds typed evidence to the symbols and statuses whose
locations the evidence text states and lists the text it cannot type.

The canonical feature layouts give the `7mfk` side of the same tables: the
`[[hook]]` entries of `patches/map-switching-layout.toml`,
`patches/rolling-launch-layout.toml`, and `patches/can-telemetry-layout.toml`
the `hook` symbols with their canonical keys and replacements, the
`[[family]]` entries of the map layout the `tbl` symbols of the map
families, and the `[[diagnostic]]` entries of the rolling layout the `did`
symbols. The layouts stay the owners of the patch design.

`patches/*-runtime-correspondence.csv`:

| Column | Target |
|---|---|
| `domain`, `key` | The entry: `telemetry` names a field source, `can_symbol`, `map_symbol`, and `rolling_symbol` a symbol meaning, `map_hook`, `can_hook`, and `rolling_hook` a `hook` meaning, `map` and `map_native` a `tbl` meaning, `allocation` a `runtime` allocation, and `capability` a feature target |
| `source` | The `7mfk` symbol or allocation |
| `target` | The symbol or allocation on the target layout |
| `stock` | The `target` link of a hook, which the `image-bytes` check verifies |
| `variant` | A key of the feature target |
| `status` | For a symbol: `mapped` gives homology evidence, `target-specific` an anchor with evidence of its own layout, and `unsupported` a status; the status of an `unsupported` `map` or `map_native` row gives way to a symbol that another row places in the meaning on the layout. For an allocation or a capability: the `note` of the target key |
| `evidence` | The `note` of the typed evidence item |

The conversion types the evidence of every `mapped` and `target-specific`
symbol row from L0 with the matchers of the `homology` check: literal pools,
call ordinals, function hashes, masked matches, and DID tables. A row that no
matcher reproduces is listed and resolved by review before the conversion
commit.

`defs/JK08A-*.definition-addresses.csv`:

- `entity` gives the kind, `Map` for `tbl` and `Axis` for `axis`; `source`
  and `target` give the symbols; `variant` is a key of the `definitions`
  target; `sites` is derived from L0; `evidence` becomes the `note` of the
  typed evidence.
- `homologous-exact-chain` and `homologous-call` rows give homology evidence
  of the kinds that `function_kinds` names, through a table in
  `tools/kb/config.toml`: `exact-bytes` and `exact-storage` give
  `byte-identical`, the shape, sequence, and reference hashes give
  `function-match`, the call-order, call-signature, and operand kinds give
  `call-ordinal`, and `target-literal` gives `literal-pool`. A value without
  an entry fails the conversion.
- `reviewed-target` rows give an anchor symbol with `l0` evidence.
- `unsupported` rows give a status by their reason: `no-homolog` gives
  `unresolved`; `removed-subsystem`, `removed-dispatch-slot`, and
  `changed-geometry` give `absent`; `stock-inert-path` gives the symbol of
  the homologous surface that the evidence names, which the `definitions`
  target leaves out.

`defs/definition-projections.toml`: every key of `[projection.<ROM>]` and
`[projection.<ROM>.switch]` becomes a key of the `definitions` target of the
image's layout; `addresses` is derived from the symbols.

`defs/*.interp.csv`: each row becomes `[interp]` of the wrapper's `fn`
meaning, with `family` as `access`, `kernel`, `width` and `height` as `cols`
and `rows`, `step`, `storagetype` as `storage`, and `axistype_x` and
`axistype_y` as `x_storage` and `y_storage`. A row of
`defs/*.interp-correspondence.csv` gives the target kernel and wrapper
symbols with `interp-contract` evidence, and an `unsupported` row gives a
status.

`patches/runtime_targets.py`: `CANONICAL_MAP_SYMBOLS`,
`CANONICAL_ROLLING_SYMBOLS`, and `CANONICAL_CAN_SYMBOLS` give the `7mfk`
symbols of the meanings their keys name, with the value keys converted as in
the address profiles. `MAP_HOOK_KEYS` and `VQ37_MAP_HOOK_KEYS` give the
per-layout hook keys of the feature targets and join them to the canonical
keys. `IGNITION_STATE_TEMPLATE` gives the `1nd` table symbols of the four
state-code families; its pointer tables are addresses of the adapter template
before relocation, which the `ignition_state_storage` allocation of each
target replaces.

### 20.4 VQ37VHR native registries

Stage 3. `defs/vq37-native-tables.toml`, per `[[target.<ROM>.table]]` and
`[[target.<ROM>.axis]]` entry. Entries of the images of one layout join into
one symbol, and an entry that only some images of the layout carry gives the
symbol `images`.

| Key | Target |
|---|---|
| `id` | Semantic name of the meaning |
| `address` | Symbol on the layout of `<ROM>` |
| `width`, `height`, `length`, `storagetype`, `kind` | `cols`, `rows`, `points`, `storage`, and the kind |
| `mask` | `mask` of `[editor]` |
| `values_sha256` | Not stored: the image digest fixes the bytes |
| `pointer_bindings` | `l0` evidence at each site and a `reader` link to each accessor |
| `axis_x`, `axis_y` | `axis` links |
| `name`, `category`, `order`, `format`, `fine`, `coarse`, `static_axis`, `static_axis_name` | `[editor]` |
| `units`, `scale_expr`, `to_byte`, `scale_conf` | `unit`, `scale`, `to_raw`, `scale_level` |
| `confidence` | `level` |
| `semantics` | `summary` |
| `note` | `note` of the symbol |

`stock_sha256` of a target is the catalog digest and is not stored.
`[target.<ROM>.absent]` gives an `absent` status of the meaning each key
names, with evidence typed from its text.

`defs/vq37-native-fuel-cut.toml`, per target:

- `function_address` and `coordinator_address` become `fn` symbols;
  `state_address` with `state_armed_mask` and `state_active_mask` becomes a
  `ram` symbol with named bits; `selector_address`, `rpm_address`, and
  `delay_address` become `ram` symbols; `curves_address`, `caps_address`,
  `axis_address`, and `delay_calibration_address` become `tbl` and `axis`
  symbols.
- `axis_values`, `caps_values`, `curve_values`, and
  `delay_calibration_value` are image bytes and become `rom-bytes` evidence
  where a claim rests on them.
- `predicate_call_site`, `predicate_instruction_ordinal`,
  `coordinator_predicate_ordinal`, and `coordinator_pointer_site` become
  `call-ordinal` and `l0` evidence; `pointer_bindings` and
  `ram_pointer_bindings` become `l0` evidence with `reader` links.
- `function_size` and `function_sha256` come from L0, `stock_sha256` is the
  catalog digest, and `evidence` becomes evidence items.

### 20.5 Telemetry, signals, and presentation

Stage 4.

`defs/JK08A.tuning-signals.toml`:

- `id` is the slug; `label` becomes `title`; `domain`, `priority`,
  `coverage`, and `note` keep their names; `evidence` becomes `basis`.
- `sources` becomes `observes`, the meanings of the `7mfk` symbols at those
  addresses, and `widths` must equal their `width`.
- `dids` and `current_fields` are derived, and the conversion requires the
  derived sets to equal the stored ones.
- `telemetry_profile`, `rotating_divisor`, and `full_rate_hz` become keys of
  `can_telemetry`.

`patches/can-telemetry-profile.toml`:

- `[[field]]`: `name` is the slug; `page`, `offset`, `width`, `signed`,
  `profiles`, and `kind` keep their names; `source` becomes a reference to
  the meaning of the `7mfk` symbol at that address, or to the allocation or
  state item of its kind; `signal` comes from the signal whose
  `current_fields` lists the field.
- For an `ecu_ram` field the conversion parses `scale` into the source
  meaning: the arithmetic in `raw` becomes `scale` in `x` with its `unit`, a
  leading `candidate` sets `scale_level = "candidate"`, an enumeration
  becomes `[[value]]` entries, a bit description becomes `[[bit]]` entries,
  and the remaining text joins the summary. A meaning that already has a
  scale must agree. Every string the parser cannot split is listed for
  review.
- `[[context]]` becomes a context of `can_telemetry` with `name`, `page`, and
  `tag`, and each `[[context.field]]` a field with `context` and `position`.
- The wire constants and `[[profile]]` become keys of `can_telemetry`.
- The regenerated profile renders each `ecu_ram` scale from its meaning; the
  conversion commit lists every string that changes, and the consumers pass
  their tests on the regenerated file.

`defs/JK08A.overrides.toml`:

- `[table.<address>]` and `[axis.<address>]` become `[editor]` of the
  meaning at that address, and `[logparam.<address>]` becomes `[logparam]`
  with `units` as `unit`.
- `[[masked_view]]` becomes `[[editor.view]]` of the meaning at `source`,
  with `units`, `expression`, and `to_byte` as `unit`, `scale`, and
  `to_raw`.
- `[rom]`, `[[checksum]]`, `[[switch]]`, and `[presentation]` become keys of
  `definitions`; `[map_switching]` and `[rolling_launch]` become keys of
  those features.
- Comments are dropped, and the conversion lists each one for review against
  the summary of its meaning.

### 20.6 Architecture

Stage 6. `defs/JK08A.architecture.toml`:

- `[[stage]]`: `id` is the slug, `name` becomes `title`, `lane` and `summary`
  keep their names, and the array position becomes `order`.
- `[[block]]`: `id` is the slug with underscores, `name` becomes `title`;
  `stage`, `summary`, `specs`, and `generic` keep their names; `functions`
  becomes the `block` key of each `fn` meaning, and `signals` the `block` key
  of each `ram` meaning.
- `[[endpoint]]`: `name` becomes `title`; `registers` and `functions` become
  references; the other keys keep their names.
- `[[chain]]` and `[[chain.step]]`: `name` becomes `title`; addresses become
  references; the conversion keeps the arithmetic of each note and lists the
  conditions for review as links of the destination meaning
  ([A JK08A chain step](#172-a-jk08a-chain-step)).
- `[sources]` is dropped: the compiler knows its inputs.

### 20.7 Evidence tokens

Adapters from stage 2 and the conversion of stage 5 map each token of an
evidence column by its role, the kind of the row, and the kind of the target:

| Token | Row | Target | Result |
|---|---|---|---|
| `writes:<a>` | `ram`, `reg` | `fn` | `writer` link |
| `writes:<a>` | `fn` | `ram`, `reg` | `writer` link stored at the target |
| `writes:<a>` | `tbl`, `axis` | `ram`, `reg` | `lookup` link stored at the target |
| `consumer:<a>` | datum | `fn` | `reader` link |
| `consumer:<a>` | `fn` | `fn` | `depends` link with role `consumer` |
| `indexed_by:<a>` | `tbl`, `axis` | `ram`, `reg` | `index` link |
| `indexed_by:<a>` | `ram`, `reg` | datum | `input` link |
| `indexed_by:<a>` | `fn` | `ram`, `reg` | `reader` link stored at the target, with role `indexed_by` |
| `from_map:<a>` | `ram`, `reg` | `tbl`, `axis` | The `index` link of the table when its row carries `indexed_by` of the datum; `lookup` when its row carries `writes` of it; `input` otherwise |
| `from_map:<a>` | `fn` | `tbl`, `axis` | `reader` link stored at the table |
| `selector:<a>` | any | datum | `selector` link |
| `threshold:<a>` | any | datum | `threshold` link |
| `base:<a>+<offset>` | `ram` | `ram` | `base` link with `offset` |
| `homolog:<a>`, `match:<a>`, and every other combination | any | any | `depends` link with the token role |
| `trace:<a>` | any | `fn` | `trace` evidence |
| `rom_const:<a>=<value>` | any | ROM | `rom-bytes` evidence |
| `site:<a>` | any | code | `l0` evidence, removed once L0 reproduces the relation it supports |
| `spec:<equation>` | any | | `arithmetic` evidence |
| `spec:<id>` whose id starts with a prefix of `[tokens] manual` in `tools/kb/config.toml`: `esm-`, `sh7058-hw-`, `sh7058-hardware-manual`, and `SH7058S-HW-` | any | | `manual` evidence with the id as `key` |
| `spec:hardware-results:<key>` | any | | `hardware` evidence with the record key |
| `spec:<id>` otherwise | any | | `spec` evidence with the id as `key` |
| `registry:<text>` | any | | `registry` evidence, with a path in `path` and other text in `value` |
| `wave:<n>`, `arg:<text>` | any | | Removed: review process history, which git keeps |

- The target of a dependency token resolves, in the order of its role, to
  the first kind of which a registry places a symbol at the address:

| Role | Resolution order |
|---|---|
| `consumer` | `fn`, `ram`, `reg` |
| `writes` | `ram`, `reg`, `fn` |
| `indexed_by` | `ram`, `reg`, `axis`, `fn`, `tbl`, `const` |
| `selector` | `ram`, `reg`, `fn`, `tbl`, `const` |
| `threshold` | `ram`, `reg`, `tbl` |
| `from_map`, `match` | `tbl`, `axis` |
| `homolog`, `trace` | `fn` |
| `base` | `ram`, `reg` |

- An address where no registry places a symbol of those kinds becomes an
  implicit symbol: `fn` at a function entry of L0, `ram` or `reg` by the
  address space of the MCU, and at another ROM address `tbl` inside the
  calibration region of the family and `const` outside it, or else the first
  ROM kind of the order. An implicit symbol receives a generated name like
  every other symbol without a semantic name.
- The suffixes `@structural`, `@confidence`, `@contract_conf`, and
  `@scale_conf` become `relies` = `structure`, `level`, `contract`, and
  `scale`.
- The column sets `supports`: `evidence` gives `identity`,
  `contract_evidence` gives `contract`, and `scale_evidence` gives `scale`.
- A relation stated at both ends becomes one link at the end that the type
  table of [Links](#75-links) names. The other end's suffix becomes
  `reverse_relies`, the claim of its column `reverse_supports`, and the
  evidence of both ends merges.
- A `site:<a>` token reproduces from L0 by the first of these relations
  between the site and its row: L0 records a reference at the site to the
  row's subject, to an address within its table, or to an address the row
  names; the site lies in the body of a function the row names; the image
  holds the subject or a named address as a 32-bit value at the site; or the
  site lies in the body of a function that L0 links to the subject by a
  reference or by a census call. A row names the addresses of its structured
  columns and evidence tokens, not those of its prose columns.

## 21. Transition

### 21.1 Rules

- The read path over the current registries comes first and the storage
  conversion second, so the schema meets all live data before any registry is
  rewritten.
- A converted registry is generated byte-identically for as long as it has
  consumers, and the access guard refuses a manual edit of it.
- Every fact has one owner at every stage ([Ownership by
  stage](#19-ownership-by-stage)); `AGENTS.md` carries the table of the
  current stage.
- A registry converts in one commit of an idempotent conversion script. The
  script reruns on a rebased tree, and parallel sessions know the freeze
  window of that registry.
- Every stage leaves `make verify` green.

### 21.2 Order

- 0 -> 1 -> 2. Work on stage 2 may start with stage 1, and stage 2 lands
  after it, because its checks and questions read L0.
- 2 -> 3 -> 4.
- 2 -> 5 -> 6.
- 4 and 6 -> 7.
- 5 -> 8.
- 3 and 8 -> 9.
- 4 and 9 -> 10.
- 11 is last.

### 21.3 Stages

| Stage | Content | Exit |
|---|---|---|
| 0. Specification | This document | The specification is agreed |
| 1. L0 in git | The layouts of `rom-images/homology.toml`; normalized exports of every layout with manifests ([L0](#8-l0)); the first instruction-stream exports of JK00C and JK00D; literal-load pairing; decompilation and listings as the local cache of `kb code`; the `kb` package with the `l0` check; the loaders and `tools/rom_sources.py` read L0 from the repository; `.ignore` hides `l0/` from search; graph memory and repository growth measured with L0 of all layouts, and the instance limit of `tools/kb/config.toml` set from the measurement | Every layout in git; the `l0` check in `make check`; a repeated export produces identical files; at least 85 percent of the `site:` addresses of the JK08A ledgers reproduce from L0 |
| 2. Read path | The compiler with adapters of every current registry loads the graph with `:Meta`; readers refuse a stale fingerprint; per-worktree instances; `kb` and MCP for reading, `kb cypher`; semantic names from registry ids and generated names for the other symbols in `kb/names.csv` ([Adapters and names](#201-adapters-and-names)); `kb audit` lists disagreements of one fact between registries; parameters in `tools/kb/config.toml` and budgets in `tools/kb/bench.toml`; the single-source gate reads the layout table and the question table of this document; the access guard; `AGENTS.md` routes knowledge access through `kb` | The questions active at stage 2 are answered within budget; the audit disagreements are resolved; names are stable across builds |
| 3. Feature symbols | `patches/rom-address-profiles.toml`, `patches/*-runtime-correspondence.csv`, `defs/definition-projections.toml` with `defs/JK08A-*.definition-addresses.csv`, `defs/*.interp.csv` with `defs/*.interp-correspondence.csv`, `defs/vq37-native-tables.toml`, `defs/vq37-native-fuel-cut.toml`, and the symbol and hook-key tables of `patches/runtime_targets.py` convert into meanings with symbols and statuses and into the targets of `runtime`, `definitions`, and the project features ([Address profiles and correspondence](#203-address-profiles-and-correspondence)); the JK08A telemetry producers and the reasons of `telemetry_unavailable` become symbols and statuses; writes through `kb bind`, `kb absent`, and `kb unresolved`; the writer gate over L0 | The old files are generated byte-identically; restoring the `apc_output` binding that commit `904ce7e` replaced fails the writer gate; the layout comparison is uniform for all targets |
| 4. Features on L2 | Fields reference signals and source meanings, and the scale comes from the meaning; source tables, the schema, payload bindings, the decoder, and dashboard metadata are generated; Map Switching, Rolling Launch, and editor presentation; generated copies leave `single_source.py`; the feature by layout matrix | Replaying the four-field telemetry change of commit `ca5dbb0` on a branch changes one to three source files per field, `kb impact` lists the insertion points on every layout, and `make verify` is green |
| 5. JK08A ledgers | Ledger rows convert into meanings with `fn`, `ram`, `reg`, `tbl`, and `axis` symbols; evidence becomes typed links at one end, and duplicate pairs collapse; `site:` tokens that L0 reproduces are removed after a check of each; prose becomes the summary and the note | The ledgers regenerate from the files without loss; `kb show` answers at any address; tokens measured against the grep path over a ledger |
| 6. Architecture | Stages, blocks, endpoints, and chains become entities, and a step note keeps only its arithmetic; romviz reads the graph and builds the atlas from the symbols of each layout; the atlas searches symbols by name and shows the symbols of a meaning across layouts, statuses, and analogs; block candidates for unplaced functions come from communities over the call graph and shared RAM | The numbers of `architecture.py check` reproduce; every layout with symbols has an atlas |
| 7. Graph readers | `mapkit/emit_def.py` with its gate `validate_map_switching.py`, `mapkit/show.py`, `maps/build_tracker.py`, `diagnostics/query.py`, `memgraph/provenance_report.py`, and their tests read the graph through the `kb` API with the fingerprint check; the loaders of `tools/memgraph/` move into the compiler; `make setup` starts Memgraph and loads the graph from git in one command | No tool reads the graph without the fingerprint check; a fresh clone passes `make verify` after `make setup`; the graph is rebuilt from git without a backup |
| 8. Code reconciliation | Declared links are checked against L0; writers without an L0 reference are resolved by indirect access kind: pointer, GBR, the `FFFF128C` window, block copy, each with its own evidence kind; ROM symbols are checked against image bytes | Zero unexplained differences; every exception carries a reason |
| 9. Layouts | Exact-code symbols inherit; 8MFK suggestions from the diff of the two images; the `kb suggest` channels; a new image joins a family by its census report, and `kb family new` starts a family whose meanings are its own; the VVEL model of `defs/JK78C.vvel.md` and `defs/JK78C.can.md` converts into meanings with symbols; communities on a new layout propose subsystems without homologs; 1ND and 1ME3B enter directly in the new format | Every pair of project feature and layout has a symbol or a status for each required meaning |
| 10. Parity catalog | EcuTek and UpRev functions become `feature` entities with requirements on L1, an acceptance criterion, and a status per layout; `kb gaps --catalog` reports them | The catalog covers the project's features and the competitor inventory |
| 11. Retirement | Projections without external consumers, old loaders, and copies are removed; XML, XDF, and RomRaider files stay generated; README, `AGENTS.md`, and narrow READMEs describe the final state | No old registry is edited by hand |
