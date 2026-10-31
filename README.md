# VQ HR ECU Tuning

Reverse engineering, calibration definition, and firmware verification for
Hitachi CAN ECUs used with Nissan and Infiniti VQ25HR, VQ35HR, and VQ37VHR
engines.

## Current state

- Stock ROM identity and provenance are tracked for owned and reference SH7058
  and SH7059 images. `JK08A` is the active hardware target and the canonical
  code profile for the exact JK00A/JK03A/JK03B/JK08A family.
- The stock collection includes exact-code and near-code SH7058 families and
  distinct SH7058 and SH7059 images. Pairwise
  fixed-address and relocated window measurements are reproducible from the
  tracked homology registry.
- The headless analysis path exports firmware structure from Ghidra, rebuilds a
  queryable Memgraph index from tracked inputs, and projects reviewed facts into
  RomRaider XML, TunerPro XDF, and a map ledger.
- The unified builder composes the capability-specific runtime for the targets
  registered by `patches/runtime_targets.py` and their address profiles.
  Map Switching and custom CAN telemetry are available on all registered
  targets, and Rolling Launch on JK00A, JK03A, JK03B, and JK08A. Map Switching
  and Rolling Launch take their input from the steering switch buttons, which
  JK00A, JK03A, JK03B, JK00C, JK00D, 1ND0A, and 1ND3B decode only once the
  Cruise Control Switch of their definitions selects the ICC switch. VQ37
  targets use their native fuel-cut caps and interpolated curves for map
  slots. The builder preserves target
  calibration state, closes each ROM's checksum domains, and emits a
  machine-readable build manifest.
- One canonical annotation and presentation layer plus explicit relocated
  correspondences generate target-specific RomRaider XML and TunerPro XDF
  files for the registered stock identities. The SH7059 1ND images share one
  reviewed address layout while retaining independent identities and values.
- Instruction-changing patches have a repository-contained GNU SH-2E
  executable gate. It independently assembles and executes the canonical JK08A
  runtime and the relocated projections registered by `patches/runtime_targets.py`.
  Software verification does not replace bench, readback, or engine validation.
- Concrete tuned images, local calibration profiles, build recipes, active tune
  identities, and generated test artifacts are intentionally outside Git.

## Authority

| Information | Canonical source |
|---|---|
| Addressed technical claims and evidence | `kb` meanings and typed evidence, unconverted registries, TOML manifests, assembly, and narrow repository specifications |
| Stock ROM identity, provenance, hashes, and homology | `rom-images/roms.csv`, `rom-images/homology.toml`, `rom-images/homology.csv`, and `rom-images/README.md` |
| Derived-image identity and hardware result | `patches/hardware-results.toml` |
| Query and relationship index | Reproducible Memgraph projection built by tracked loaders |
| XML, XDF, ledger, and counters | Generated projections, never handwritten authority |
| Change chronology | Git history |

## Repository map

| Path | Responsibility |
|---|---|
| `rom-images/` | Versioned stock dumps and provenance registry |
| `defs/` | JK08A annotation views, architecture, target identities, and generated editor projections |
| `patches/` | ROM builder, layouts, payloads, assembly, checksums, and patch tests |
| `tools/ghidra/` | Headless structure extraction and Ghidra p-code fixtures |
| `tools/memgraph/` | Reproducible graph ingestion, provenance audit, and backup |
| `tools/mapkit/`, `tools/maps/` | Definition and ledger projection |
| `tools/diagnostics/` | Factory and community diagnostic corpus tooling |
| `tools/logs/` | Strict CAN decoders, PEAK audit, and MLVLG conversion |
| `tools/can_dashboard/` | Portable Windows and macOS PCAN-USB live telemetry dashboard |
| `tools/sh-elf-run/` | Independent GNU SH-2E executable verification |
| `tools/pin-tracer/` | Reviewed physical ECM terminal-to-MCU tracing workspace |
| `hardware/` | KiCad bench harnesses and bring-up scripts for the ECU, including SH7058S native boot recovery |
| `refs/` | Primary references and tracked machine-readable projections |

## Entry points

- New ROM intake: [`rom-images/new-rom-intake.md`](rom-images/new-rom-intake.md)
- ROM identity and provenance: [`rom-images/README.md`](rom-images/README.md)
- ROM family and support parity: [`rom-images/support-matrix.md`](rom-images/support-matrix.md)
- Canonical annotations and generated definitions: [`defs/README.md`](defs/README.md)
- Production ROM composition: [`patches/rom-builder.md`](patches/rom-builder.md)
- Map-switching runtime: [`patches/map-switching-selector.md`](patches/map-switching-selector.md)
- Rolling Launch runtime: [`patches/rolling-launch.md`](patches/rolling-launch.md)
- Cruise Control Switch: [`patches/cruise-control-switch.md`](patches/cruise-control-switch.md)
- Custom CAN telemetry design: [`patches/can-telemetry.md`](patches/can-telemetry.md)
- PCAN dashboard: [`tools/can_dashboard/README.md`](tools/can_dashboard/README.md)
- CAN and MLVLG logging tools: [`tools/logs/README.md`](tools/logs/README.md)
- Runtime ownership and reserves: [`patches/runtime-reservations.md`](patches/runtime-reservations.md)
- Exact JK08A HCAN1 model: [`defs/JK08A.can.md`](defs/JK08A.can.md)
- Exact JK78C HCAN model: [`defs/JK78C.can.md`](defs/JK78C.can.md)
- Exact JK78C VVEL target model: [`defs/JK78C.vvel.md`](defs/JK78C.vvel.md)
- Exact VQ37 intake-CVTC solenoid output stage: [`defs/JK78C.cvtc.md`](defs/JK78C.cvtc.md)
- Exact JK08A intake/exhaust-CVTC model: [`defs/JK08A.cvtc.md`](defs/JK08A.cvtc.md)
- Analysis and definition pipeline: [`tools/map-analysis-pipeline.md`](tools/map-analysis-pipeline.md)
- Tool navigation and local deployment: [`tools/README.md`](tools/README.md)
- Memgraph ingestion: [`tools/memgraph/README.md`](tools/memgraph/README.md)
- Definition generation: [`tools/mapkit/README.md`](tools/mapkit/README.md)
- Executable verification: [`tools/sh-elf-run/README.md`](tools/sh-elf-run/README.md)

## Prerequisites

| Requirement | Used by |
|---|---|
| `uv`, which provisions the pinned Python | Every Python entry point, `make setup`, and `uv run pytest -q` |
| Docker with Compose | Memgraph ingestion through the configured daemon; GNU SH-2E execution through the local `default` context |
| Node.js and npm | ROM-atlas validation and the pin-tracer contract |
| Ghidra with JDK 21 | Headless structure export, decompilation, and p-code fixtures |
| Poppler with `pdftotext` and `pdfinfo` on PATH | Factory ESM and legacy Nissan PDF extraction and projection checks |
| PEAK PCAN-USB with the vendor driver | Live telemetry capture, logging, and the dashboard |
| An external reflash tool with an OBD interface it supports | Reading a stock image and writing a built image |

`make setup` installs the locked environment with `uv sync --frozen`, initializes
the pinned reference submodules, starts the working tree's Memgraph instance,
and builds every graph layer from tracked inputs through `kb sync`. The
workspace package `kb` supplies the knowledge API, graph client, name
generator, and text matcher. The test runner is a development dependency. The dashboard
installs its own platform dependencies from
`tools/can_dashboard/requirements-*.txt`. Build and dependency files own the
versions used by their consumers. Local tool locations are listed in
[`tools/README.md`](tools/README.md#local-deployment).

Ghidra is needed for structure export alone. `make check`,
`make defs-generate`, and the ROM-atlas tests query a running, populated
Memgraph instance. The definition model is validated against the graph, and
the atlas reads its layout symbols after a fingerprint check.
`make verify-firmware` and the ROM builder read tracked inputs and need
neither Ghidra nor Memgraph.

## From a stock read to a flashed image

1. Read the ECU with an external reflash tool and register the image through
   [`rom-images/new-rom-intake.md`](rom-images/new-rom-intake.md): identity,
   hash, provenance, family boundary, and atlas manifest.
2. Export structure from Ghidra, ingest the tracked layers into Memgraph, and
   review addressed claims into `defs/` sources.
3. Generate the editor projections and the map ledger with `make defs-generate`
   and inspect the calibration in RomRaider or TunerPro.
4. Compose the runtime from the stock image with `make rom-build`, which
   applies the capability patches, closes every checksum domain, and emits a
   build manifest. `make rom-extract` and `make rom-calibrate` carry the
   calibration of an earlier image to the new build.
5. Qualify the result with `make preflash`: the image rebuilds byte for byte
   from its stock image at a clean commit with a green `Verify` run, and the
   patch tests and the GNU SH-2E gate of its ROM pass.
6. Flash the built image with the external tool, then validate on a bench and
   in the vehicle. Software gates do not establish hardware behavior.

The repository contains no flashing tool. `refs/` records the external module
lists and recovery procedures, and `hardware/` documents the bench harness that
enters SH7058S native boot mode when a normal reflash path is unavailable.

## Root orchestration

The root `Makefile` delegates to the tracked subsystem entry points without
moving build logic into Make recipes. Run `make help` for the complete target
and variable list. Common read-only workflows are:

```bash
make check
make test
make verify
```

`make test` runs Python tests without the `slow` marker and the pin-tracer
contract. `make test-full` includes the complete Python and pin-tracer
contracts. `make test-python` and direct `uv run pytest -q` include every
Python test. `make test-python-fast` selects the same Python tests as
`make test`. `make test-changed` runs the fast tests of the subsystems that
changed since `origin/master`, counting commits, the worktree, and untracked
files: `tools/test-map.toml` maps the paths to test directories, the target
prints the selected directories before it runs them, and a path that the map
does not cover selects `make test`.

`make verify` runs firmware qualification, source checks, and `make test-full`.
It includes the repository-contained GNU SH-2E Docker gate and is required
before closing an engineering track; a green `Verify` run of the exact commit
counts as that run (see [Continuous verification](#continuous-verification)).
`make preflash` qualifies one built image for flashing. The pin-tracer contract
is documented beside that tool.

`make runtime-targets-generate` regenerates GNU SH-2E payload locks and
capability-specific stage hashes for the relocated targets registered by
`patches/runtime_targets.py`, using their declared address profiles.

`make check` independently assembles and byte-compares that manifest and the
canonical JK08A telemetry manifest using the same pinned GNU toolchain.
`make telemetry-update` derives the telemetry layout locks and the telemetry
manifest after an intentional change of the telemetry profile or sources, then
regenerates the relocated payload manifest.

Build the self-contained ROM atlas HTML with:

```bash
make romviz
```

The target rebuilds the ignored `tmp/romviz/rom-atlas.html` artifact for every
flash ROM registered in `rom-images/roms.csv`. `ROMS="JK08A JK00C"` limits the
atlas to an explicit selection. The target does not start a server or watch
source files.

Build the portable Windows PCAN dashboard archive with:

```bash
make dashboard-package
```

Build the native macOS PCAN dashboard application and archive with:

```bash
make dashboard-package-macos
```

The unified production builder remains the only complete modified-ROM entry
point. Its input is a registered stock image. Map Switching, capability-gated
Rolling Launch, CAN telemetry, checksum closure, and the final write-set audit
run through the same command; calibration moves between images through
extraction and application:

```bash
make rom-verify INPUT=STOCK.bin
make rom-build INPUT=STOCK.bin OUTPUT=tmp/output.bin
make rom-build INPUT=STOCK.bin OUTPUT=tmp/output.bin \
  PROFILE=tmp/profile.toml
make rom-extract INPUT=tmp/tuned.bin \
  CALIBRATION=tmp/tuned-calibration.toml PROFILE=tmp/tuned-profile.toml
make rom-calibrate INPUT=tmp/output.bin \
  CALIBRATION=tmp/tuned-calibration.toml OUTPUT=tmp/calibrated.bin
make preflash INPUT=tmp/calibrated.bin ROM=JK08A
```

`make preflash` qualifies one built image of one exact ROM for flashing. The
image must carry the immutable identity of that ROM, change stock bytes only
inside its calibration ranges, builder write sets, and checksum fields, and
rebuild byte for byte from the registered stock image with the settings and
calibration that it carries. The tracked worktree must equal HEAD, and the
`Verify` workflow must have a green run of that exact commit; a running,
failed, cancelled, or missing run refuses the image, and runs of other commits
do not count. The target then runs the patch tests of that ROM through
`pytest --rom` and the GNU SH-2E gate through `tools/sh-elf-run/run.sh --rom`.
It writes no tracked file.

`make defs-generate` regenerates XML/XDF pairs for every registered target,
the canonical JK08A map ledger, and the common definition validation from an
already running and populated Memgraph instance. `DEFS_ROM=<ROM>` limits
definition generation to one target; canonical ledgers are derived from the
same target and inheritance registries. ROM builds use immutable-byte automatic
detection unless `ROM=<ROM>` is explicit. `make check` reads the same running
instance for its definition-model validation. No root target starts, mutates,
or backs up Memgraph, flashes hardware, or deletes temporary files. Each narrow
README retains the detailed subsystem contract.

Per-family address policy, the feature targets of each layout with their
switched calibration families and unavailable telemetry fields, actuator,
checksum closure, and hardware status are tabulated in
[`rom-images/support-matrix.md`](rom-images/support-matrix.md). The registered
builder series and their address profiles are in
[`patches/rom-builder.md`](patches/rom-builder.md). Only JK08A carries scoped
vehicle evidence; every other target is untested on bench and vehicle
hardware.

## Continuous verification

The `Verify` workflow in [`.github/workflows/verify.yml`](.github/workflows/verify.yml)
runs the steps of `make verify` on GitHub-hosted Ubuntu runners for every push
to `master` and on manual dispatch. Its two jobs run in parallel:

| Job | Steps |
|---|---|
| Firmware gate | `make verify-firmware` |
| Source checks and tests | `kb instance up`, `kb sync`, `kb check`, `make check`, `make test-full` |

Both jobs load the GNU SH-2E gate image from the Actions cache under the
fingerprint of its build inputs and build it when the inputs change; a stale
image is refused as in a local run. The source job restores the Memgraph data
of the closest earlier graph, so `kb sync` loads only the changed parts; a
manual dispatch with `full` builds the graph in an empty instance.
`kb instance up` starts the Compose services, so every run includes the pull
of the Memgraph and Lab images. `make check` and `make test-full` also run
after a failed `kb check`, so one run reports every failure.

A run takes about 20 minutes when the caches hold the gate image and a recent
graph, and about 30 minutes when it builds both; the source job sets the
duration. A newer push to `master` cancels the run of the previous push, so
under frequent pushes only the newest commit receives a completed run.
`make preflash` accepts only a commit with a green run; build the image to
flash from such a commit.

A green run of an exact commit is the full verification of that commit, apart
from these exclusions:

| Excluded check | Reason | Where it runs |
|---|---|---|
| Dashboard GUI tests | The runner has no display; pytest reports them as skipped with `Tk display is unavailable` | Local `make verify` |
| Tests of untracked road captures and local images | Their inputs are not in the repository; pytest reports them as skipped | Local `make verify` in a checkout that holds the inputs |
| `tools/check_projection_contract.py --run` | It requires every registered source, including the external checkout named by `VQ_OBD2TOOLS_SOURCE` | Manual run with every source; `make verify` does not include it |
