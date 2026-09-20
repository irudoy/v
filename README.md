# VQ HR ECU Tuning

Reverse engineering, calibration definition, and firmware verification for
Hitachi CAN ECUs used with Nissan and Infiniti VQ25HR, VQ35HR, and VQ37VHR
engines.

## Current state

- Stock ROM identity and provenance are tracked for owned and reference SH7058
  and SH7059 images. `JK08A` is the active hardware target and the canonical
  code profile for the exact JK00A/JK03A/JK03B/JK08A family.
- The stock collection has two exact-code families, one near-code SH7058
  family, one distinct SH7058 image, and one distinct SH7059 image. Pairwise
  fixed-address and relocated window measurements are reproducible from the
  tracked homology registry.
- The headless analysis path exports firmware structure from Ghidra, rebuilds a
  queryable Memgraph index from tracked inputs, and projects reviewed facts into
  RomRaider XML, TunerPro XDF, and a map ledger.
- The unified builder composes the current capability-specific runtime for
  JK00A, JK03A, JK03B, JK08A, JK00C, JK00D, JK78C, 1ND0A, 1ND3B, and 1ME3B.
  Map Switching, Rolling Launch, and custom CAN telemetry are available on all
  ten targets. VQ37 targets use their native fuel-cut caps and interpolated
  curves for map slots, while Rolling Launch adds an exact all-cylinder
  request after the stock final-mask coordinator. The builder preserves target
  calibration state, closes each ROM's checksum domains, and emits a
  machine-readable build manifest.
- One canonical annotation and presentation layer plus explicit relocated
  correspondences generate target-specific RomRaider XML and TunerPro XDF
  files for all ten stock identities. The two SH7059 1ND images share one
  reviewed address layout while retaining independent identities and values.
- Instruction-changing patches have a repository-contained GNU SH-2E
  executable gate. It independently assembles and executes the canonical JK08A
  runtime and the target-specific JK00C, JK00D, JK78C, 1ND0A, 1ND3B, and
  1ME3B projections.
  Software verification does not replace bench, readback, or engine validation.
- Concrete tuned images, local calibration profiles, build recipes, active tune
  identities, and generated test artifacts are intentionally outside Git.

## Authority

| Information | Canonical source |
|---|---|
| Addressed technical claims and evidence | `defs/*.csv`, TOML manifests, assembly, and narrow repository specifications |
| Stock ROM identity, provenance, hashes, and homology | `rom-images/roms.csv`, `rom-images/homology.toml`, `rom-images/homology.csv`, and `rom-images/README.md` |
| Derived-image identity and hardware result | `patches/hardware-results.toml` |
| Query and relationship index | Reproducible Memgraph projection built by tracked loaders |
| XML, XDF, ledger, and counters | Generated projections, never handwritten authority |
| Change chronology | Git history |

## Repository map

| Path | Responsibility |
|---|---|
| `rom-images/` | Versioned stock dumps and provenance registry |
| `defs/` | Canonical JK08A annotations, target identities, and generated editor projections |
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
- Custom CAN telemetry design: [`patches/can-telemetry.md`](patches/can-telemetry.md)
- PCAN dashboard: [`tools/can_dashboard/README.md`](tools/can_dashboard/README.md)
- CAN and MLVLG logging tools: [`tools/logs/README.md`](tools/logs/README.md)
- Runtime ownership and reserves: [`patches/runtime-reservations.md`](patches/runtime-reservations.md)
- Exact JK08A HCAN1 model: [`defs/JK08A.can.md`](defs/JK08A.can.md)
- Exact JK78C HCAN model: [`defs/JK78C.can.md`](defs/JK78C.can.md)
- Exact JK78C VVEL target model: [`defs/JK78C.vvel.md`](defs/JK78C.vvel.md)
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
| Docker in the `desktop-linux` context | Memgraph ingestion and the GNU SH-2E execution gate |
| Node.js and npm | ROM-atlas validation and the pin-tracer contract |
| Ghidra with JDK 21 | Headless structure export, decompilation, and p-code fixtures |
| PEAK PCAN-USB with the vendor driver | Live telemetry capture, logging, and the dashboard |
| An external reflash tool with an OBD interface it supports | Reading a stock image and writing a built image |

`make setup` installs the locked environment with `uv sync --frozen`. The
repository declares no runtime Python dependencies; the graph client and the
test runner are development dependencies of the tracked tooling. The dashboard
installs its own platform dependencies from
`tools/can_dashboard/requirements-*.txt`. Component versions and their local
locations are in the deployment table of
[`tools/README.md`](tools/README.md#local-deployment), which
`tools/version_index.py --check` holds to the files that execute them.

Ghidra is needed for structure export alone. `make check` and
`make defs-generate` both query a running, populated Memgraph instance, because
the definition model is validated against the graph. `make test`,
`make verify-firmware`, and the ROM builder read tracked inputs and need
neither.

## From a stock read to a flashed image

1. Read the ECU with an external reflash tool and register the image through
   [`rom-images/new-rom-intake.md`](rom-images/new-rom-intake.md): identity,
   hash, provenance, family boundary, and atlas manifest.
2. Export structure from Ghidra, ingest the tracked layers into Memgraph, and
   review addressed claims into `defs/` sources.
3. Generate the editor projections and the map ledger with `make defs-generate`
   and inspect the calibration in RomRaider or TunerPro.
4. Compose the runtime with `make rom-build`, which applies the capability
   patches, preserves target calibration state, closes every checksum domain,
   and emits a build manifest.
5. Gate the result: `make check`, `make test`, and `make verify-firmware`
   execute the changed instruction bytes against independently assembled
   SH-2E fixtures.
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

`make verify` includes the repository-contained GNU SH-2E Docker gate. The
direct Python test contract remains `uv run pytest -q`; the pin-tracer contract
is documented beside that tool.

`make runtime-targets-generate` regenerates the tracked JK00C, JK00D, JK78C,
1ND0A, 1ND3B, and 1ME3B GNU SH-2E payload locks and capability-specific stage hashes
from the registered address profiles.

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
point. Map Switching, capability-gated Rolling Launch, CAN telemetry, checksum
closure, and the final write-set audit run through the same command:

```bash
make rom-verify INPUT=tmp/input.bin
make rom-build INPUT=tmp/input.bin OUTPUT=tmp/output.bin
make rom-build INPUT=tmp/input.bin OUTPUT=tmp/output.bin \
  PROFILE=tmp/profile.toml
```

`make defs-generate` regenerates XML/XDF pairs for every registered target,
the canonical JK08A map ledger, and the common definition validation from an
already running and populated Memgraph instance. `DEFS_ROM=<ROM>` limits
definition generation to one target; canonical ledgers are derived from the
same target and inheritance registries. ROM builds use immutable-byte automatic
detection unless `ROM=<ROM>` is explicit. `make check` reads the same running
instance for its definition-model validation. No root target starts, mutates,
or backs up Memgraph, flashes hardware, or deletes temporary files. Each narrow
README retains the detailed subsystem contract.

Per-family address policy, switched calibration families, actuator, telemetry
schema, checksum closure, and hardware status are tabulated in
[`rom-images/support-matrix.md`](rom-images/support-matrix.md). The registered
builder series and their address profiles are in
[`patches/rom-builder.md`](patches/rom-builder.md). Only JK08A carries scoped
vehicle evidence; every other target is untested on bench and vehicle
hardware.
