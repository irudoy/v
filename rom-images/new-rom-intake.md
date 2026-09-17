# New ROM intake

This specification is the entry point for one previously unmodelled stock flash
image. It fixes the order of work: register the identity, measure the image,
select a scenario branch, and either onboard the image or park it as a declared
stock identity.

The branches are read from four onboarded families. They are a starting
hypothesis, not a closed taxonomy. An image whose signals conflict is recorded
as unclassified rather than forced into the nearest branch.

## Outcome

Intake ends in one of two complete states.

- **Onboarded.** The image has a declared family, a registered checksum layout,
  a definition target, and a generated XML/XDF pair. Runtime capabilities are
  independently gated and may follow later.
- **Registered stock identity.** The image has provenance, a hash, a declared
  family boundary, ROM-atlas participation, and whatever the Step 2 measurements
  carry without an analysis layer, which today means the DTC registry. No
  image holds this state today; `1ME3B` passed through it with a registered
  checksum layout and an interpolation registry on top of the diagnostic layer
  before its correspondence registry and definition target were published.

A definition published on candidate-grade evidence is not a third state.

## Step 1 - Register the identity

Every branch starts here, including one that ends at a registered stock
identity.

| Deliverable | Location |
|---|---|
| Stock image | `23710-<PART>/<LABEL>-<YYYYMMDD>-stock.bin` |
| Registry row with SHA-256 and provenance note | `roms.csv` |
| Package provenance and applicability boundary | `23710-<PART>/README.md` |
| Hitachi hardware identifier and application | `README.md` |
| Atlas manifest | `../tools/romviz/roms/<LABEL>.toml` |

The ROM label is the five-character part-number suffix.

Read identifiers out of the image rather than from the dump tool: the MCU
marking `SH705822N` or `SH705927N`, the nine-character software base
identifier, and the doubled `1<LABEL>00000` software version whose label field
begins at `0x008205`. PCMFlash module 18 reports the part number, software
version, and base, and does not report the Hitachi hardware number. That number
comes from the ECU label when the block is owned.

## Step 2 - Measure

Three measurements select the branch. Run all three before proposing scope.

### Whole-image homology

```bash
uv run python tools/rom_homology.py
```

The tool rewrites `homology.csv` for every registered pair and validates the
declarations in `homology.toml`. Recorded bands from the current collection:

| Band | Evidence | Example |
|---|---|---|
| `exact-code` | Declared executable ranges byte-identical | JK00A against JK08A |
| `near-code` | Myers similarity 0.979 with insertions and relocations | JK00C against JK00D |
| `distinct-code` | Myers 0.790 to 0.815, symmetric exact 64-byte code windows near 19 percent | 1ME3B against 1ND0A |

Both MCU classes place the calibration region at `0x008200:0x020000`. An image
that does not is a Branch E case.

### Interpolation-library relocation

This measurement separates the two `distinct-code` branches and is the single
largest cost driver. It is not covered by a tracked tool.

For each interpolation kernel registered in `../defs/<MODELLED>.interp.csv`,
extract 32-byte windows at every even offset across the first 256 bytes of the
kernel and search each window across the whole candidate image. Repeat for
every modelled ROM whose MCU class matches.

Measured against the thirteen `1ND0A` kernels:

| Candidate | Windows found per kernel |
|---|---|
| JK78C | 76 to 112 of 128, all thirteen kernels |
| 1ME3B | 0 of 128, all thirteen kernels |

A relocated library returns most windows for every kernel and carries the
contract registry with it. An independent library returns none and requires
full recovery.

### Diagnostic carry

```bash
uv run python tools/mapkit/dtc_projection.py <LABEL>
```

The projection locates the descriptor records and the attribute pointer table
in the candidate image and carries a canonical record only when exactly one
target record is byte-identical. It reports the carried count and the absent
codes. This works before any structural export exists and is independent of the
branch: 1ME3B carries 38 codes with `P0443`, `P1422`, and the exhaust valve
timing codes absent while holding no other analysis layer.

Declare the tracked registry as the `dtc` layer of the atlas manifest. Every
registered image does, so the atlas diagnostics layer is populated before any
structure is recovered.

An image where the tool cannot locate a descriptor run is a Branch E case.

## Step 3 - Select the branch

| Signal | Branch | Precedent |
|---|---|---|
| Declared executable ranges byte-identical to a canonical ROM | A | JK00A, JK03A, JK03B |
| Same lineage, relocations and insertions, address inheritance invalid | B | JK00C, JK00D |
| Divergent code, interpolation library relocates from a modelled ROM | C | 1ND0A, 1ND3B |
| Divergent code, no library relocates | D | JK78C, 1ME3B |
| Signals conflict or no signal applies | E | none |

### Branch A - exact-code member of a modelled family

Differences are confined to calibration, identity, diagnostic, and checksum
storage below `0x020000`. Nothing structural is recovered.

Deliverables: an `../defs/rom-inheritance.toml` entry carrying both hashes, the
exact ranges, and evidence from a complete function-range comparison against
the canonical export; an `../defs/rom-identities.toml` identity; the atlas
manifest. The family checksum layout and address profile already cover the
member, so `../patches/checksum-layouts.toml` and
`../patches/rom-address-profiles.toml` gain a ROM label rather than a new
entry. `make defs-generate` then emits the pair.

The inheritor keeps its own image and value measurements. No semantic CSV or
presentation TOML is copied.

### Branch B - near-code member of a modelled family

Address inheritance is invalid, but the sibling is close enough that
correspondence can be composed rather than recovered. JK00C was established by
composing reviewed JK08A-to-JK00D operands through unique exact or normalized
JK00D-to-JK00C function matches.

Deliverables: a target interpolation registry when the library relocated; a
`../defs/<SOURCE>-<TARGET>.definition-addresses.csv` covering every visible
stock map and required axis, with a `unsupported` row and evidence wherever no
unique target homolog exists; a checksum layout; a definition projection; an
address profile and runtime target payloads when runtime capabilities are in
scope. The JK00C and JK00D correspondence registries hold about 280 rows each.

### Branch C - distinct code with a relocated interpolation library

Whole-image similarity sits in the divergent band, but the interpolation
kernels of a modelled ROM relocate into the candidate. The contract registry
transfers on equal wrapper bytes and reviewed library order, which removes the
most expensive stage.

Deliverables are the same list as Branch B. The correspondence registry is
compact because the semantic set is already reviewed on the sibling:
`JK08A-1ND.definition-addresses.csv` covers 31 target maps, thirteen axes, and
thirteen explicitly unsupported source maps.

Equal wrapper bytes establish the contract registry. They do not by themselves
establish map semantics or equal calibration geometry.

### Branch D - distinct code with an independent interpolation library

No modelled kernel relocates. The interpolation library, the accessors, and the
table census are recovered from the candidate image through the headless Ghidra
stage: `FindInterpCore.java`, `MapInventory.java`,
`DirectLookupInventory.java`, and `ResolveAccessors.java`, followed by the
target interpolation registry and correspondence review. This is the full cost
that JK78C paid.

The first script in that stage assumes the library is reached through a
literal-pool slot and two levels of indirection. A library that fuses wrapper,
kernel, and axis search into one self-contained leaf per access does not carry
that signature, and `FindInterpCore.java` then ranks unrelated indirect-call
layers instead. 1ME3B is such an image: its library was located from call-graph
in-degree together with leaf status, and the measurement is in
`23710-1ME3B/README.md`. Treat an empty or implausible core ranking as a
statement about the calling convention, not as evidence that the image has no
library.

A fused library is registered with `kernel` equal to `wrapper` per leaf and
censused with the `fused` token of `ResolveAccessors.java`, which takes the
call references to the leaf as the sites. Leaf geometry is read from the leaf
itself: the unrolled axis search gives point count and axis element, the cell
loads give storage type, the row stride gives the second dimension, and an
implicit leaf gives its step from the index shift and its point count from the
clamp. The 1ME3B leaves reproduce the `1ND` contract vocabulary exactly, so a
registry row can be checked against the sibling's rows even though no code
relocates.

The correspondence registry of a fused-library image is established through
the nearest modelled image rather than through the canonical ROM.
`JK08A-1ME3B.definition-addresses.csv` carries the reviewed `1ND` semantic set
to 1ME3B: every source map and axis is bound through a 1ND0A structural
function match that reads the target address at the same call ordinal, or
through a target function that reproduces the 1ND0A reader's operand set,
selector arms, and call order, always through the leaf whose contract equals
the 1ND0A wrapper and always at exact target storage. The registry records 40
mapped rows and sixteen unsupported source maps: the thirteen VQ37 rows plus the
three canonical ignition surfaces, because the target ignition coordinator
carries only its mode-selected surfaces and no function reproduces the gated
stock-inert trio path of 1ND0A. The projection declares checksum support and
no runtime allocation.

Three levers reduce the remaining work and are worth measuring first, because
they hold even when no code relocates. Values below are the 1ME3B measurements.

- The diagnostic layer carries automatically. See Step 2.
- Calibration content survives even when its layout does not. All thirteen
  `1ND` axes and 19 of 31 `1ND` maps are present in 1ME3B as exact 32-byte
  blocks, none at the same address, with deltas clustering in locally constant
  groups. This is a candidate generator for the correspondence registry and is
  not evidence.
- Checksum domains reproduce at the sibling's field addresses. The four `1ND`
  SUM16 domains hold in 1ME3B at the same field addresses and the runtime XOR
  and SUM fields move to `0x0096F4` and `0x0096FC`, which reduces the checksum
  stage to locating the verifier functions. In 1ME3B the incremental SUM16
  verifier is byte-identical to the `1ND` one at the same address, the runtime
  accumulators read the same exclusions from the moved fields, and the layout
  is registered as `sh7059_1me3b`.

### Branch E - unclassified

Select this when the MCU class is new, the calibration boundary differs, the
descriptor run is absent, the image is not a Hitachi CAN ECU of this family, or
two branch signals disagree.

Record every measurement, state which signals conflict, and consult the user
before choosing scope. Do not stretch a branch to cover the image and do not
publish a definition to close the gap.

## Fixed requirements

These hold in every branch.

1. A published definition always has a registered checksum layout.
   `checksum = false` is not an admissible state for an emitted target, because
   an editor session would otherwise leave the image with an unresolved
   checksum.
2. Structural correspondence is established through the nearest already
   modelled image by MCU and engine, not necessarily through the canonical
   annotation ROM. The declared `source` of a projection remains the canonical
   annotation ROM, which is the only live semantic and presentation layer.
3. Byte equality of calibration content is a candidate. A target address enters
   a definition projection only with target storage, geometry, consumer path,
   and stock image binding.
4. A source map without a unique target homolog is recorded as `unsupported`
   with its evidence. No canonical graph map is created speculatively and no
   source calibration value is copied into another ROM.
5. Every patch that adds, removes, replaces, or redirects executable
   instructions extends and passes `../tools/sh-elf-run/`.
6. XML, XDF, ledgers, and diagnostic projections are outputs. Edit the declared
   sources and regenerate.
7. The generated RomRaider identity omits `flashmethod`. A dump tool does not
   establish a validated flashing path.

Definition emission reads the canonical Memgraph projection of the source ROM.
A relocated target does not need its own graph layer to emit. A target export
and graph layer are analysis aids for Branch C and Branch D.

## Points that require the user

Stop and ask at these points rather than choosing a default.

- **Scope.** Whether the image is onboarded or parked as a registered stock
  identity. Branch D in particular carries a full recovery cost that is worth
  confirming before it starts.
- **Branch E.** Any conflict between the Step 2 signals.
- **Confidence promotion.** Raising a claim from candidate to code confidence
  when byte equality is the only available evidence.
- **Architectural removal.** Declaring a canonical role absent from the target
  rather than relocated. This is a durable claim about the target architecture
  and needs the same standard as
  `support-matrix.md` applies to VQ37 exhaust camshaft timing control.
- **Runtime allocation.** Adding map switching, Rolling Launch, or CAN
  telemetry to a new target, including the flash and RAM regions the profile
  claims.
- **Hardware.** Any bench read, flash write, or CONSULT-III Plus validation.

## When the branch stops fitting

The branch selected in Step 3 is a scope hypothesis. A measurement taken later
may contradict it: a library that relocates only in part, a calibration region
that is relaid out rather than shifted, an image that carries a modelled family
at one boundary and diverges at another.

Record the contradiction and the measurements that produced it, and re-select
the branch. Keep the boundary the evidence supports rather than the one the
branch predicts. Parking an image as a registered stock identity is a complete
outcome and is preferable to closing a gap with an assumption.

## Related specifications

- Analysis and definition pipeline: `../tools/map-analysis-pipeline.md`
- ROM family and support parity: `support-matrix.md`
- Definition sources and projections: `../defs/README.md`
- Production ROM composition: `../patches/rom-builder.md`
- Headless structure extraction: `../tools/ghidra/README.md`
- Correspondence candidates: `../tools/rom_correspondence.py`
