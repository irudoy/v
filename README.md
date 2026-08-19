# VQ HR ECU Tuning

Reverse engineering, calibration definition, and firmware verification for
Hitachi CAN ECUs used with Nissan and Infiniti VQ25HR, VQ35HR, and VQ37VHR
engines.

## Current state

- Stock ROM identity and provenance are tracked for owned and reference SH7058
  and SH7059 images. `JK08A` is the active target; `JK03A` shares its verified
  executable ranges and inherits the canonical JK08A annotation layer.
- The headless analysis path exports firmware structure from Ghidra, rebuilds a
  queryable Memgraph index from tracked inputs, and projects reviewed facts into
  RomRaider XML, TunerPro XDF, and a map ledger.
- The unified JK08A builder composes the current Map Switching, Rolling Launch,
  and custom CAN telemetry runtimes, preserves declared calibration state,
  closes checksum domains, and emits a machine-readable build manifest.
- Instruction-changing patches have a repository-contained GNU SH-2E
  executable gate. Software verification does not replace bench, readback, or
  engine validation.
- Concrete tuned images, local calibration profiles, build recipes, active tune
  identities, and generated test artifacts are intentionally outside Git.

## Authority

| Information | Canonical source |
|---|---|
| Addressed technical claims and evidence | `defs/*.csv`, TOML manifests, assembly, and narrow repository specifications |
| Stock ROM identity, provenance, and hashes | `rom-images/roms.csv` and `rom-images/README.md` |
| Derived-image identity and hardware result | `patches/hardware-results.toml` |
| Query and relationship index | Reproducible Memgraph projection built by tracked loaders |
| XML, XDF, ledger, and counters | Generated projections, never handwritten authority |
| Change chronology | Git history |

## Repository map

| Path | Responsibility |
|---|---|
| `rom-images/` | Versioned stock dumps and provenance registry |
| `defs/` | Canonical JK08A annotations and generated editor projections |
| `patches/` | ROM builder, layouts, payloads, assembly, checksums, and patch tests |
| `tools/ghidra/` | Headless structure extraction and Ghidra p-code fixtures |
| `tools/memgraph/` | Reproducible graph ingestion, provenance audit, and backup |
| `tools/mapkit/`, `tools/maps/` | Definition and ledger projection |
| `tools/diagnostics/` | Factory and community diagnostic corpus tooling |
| `tools/logs/` | Strict CAN decoders, PEAK audit, and MLVLG conversion |
| `tools/can_dashboard/` | Portable Windows and macOS PCAN-USB live telemetry dashboard |
| `tools/sh-elf-run/` | Independent GNU SH-2E executable verification |
| `tools/pin-tracer/` | Reviewed physical ECM terminal-to-MCU tracing workspace |
| `refs/` | Primary references and tracked machine-readable projections |

## Entry points

- ROM identity and provenance: [`rom-images/README.md`](rom-images/README.md)
- Canonical annotations and generated definitions: [`defs/README.md`](defs/README.md)
- Production ROM composition: [`patches/rom-builder.md`](patches/rom-builder.md)
- Map-switching runtime: [`patches/map-switching-selector.md`](patches/map-switching-selector.md)
- Rolling Launch runtime: [`patches/rolling-launch.md`](patches/rolling-launch.md)
- Custom CAN telemetry design: [`patches/can-telemetry.md`](patches/can-telemetry.md)
- PCAN dashboard: [`tools/can_dashboard/README.md`](tools/can_dashboard/README.md)
- CAN and MLVLG logging tools: [`tools/logs/README.md`](tools/logs/README.md)
- Runtime ownership and reserves: [`patches/runtime-reservations.md`](patches/runtime-reservations.md)
- Exact JK08A HCAN1 model: [`defs/JK08A.can.md`](defs/JK08A.can.md)
- Analysis and definition pipeline: [`tools/map-analysis-pipeline.md`](tools/map-analysis-pipeline.md)
- Tool navigation and local deployment: [`tools/README.md`](tools/README.md)
- Memgraph ingestion: [`tools/memgraph/README.md`](tools/memgraph/README.md)
- Definition generation: [`tools/mapkit/README.md`](tools/mapkit/README.md)
- Executable verification: [`tools/sh-elf-run/README.md`](tools/sh-elf-run/README.md)

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

Build the self-contained ROM atlas HTML with:

```bash
make romviz
```

The target always rebuilds the ignored `tmp/romviz/jk08a-rom-atlas.html`
artifact. It does not start a server or watch source files.

Build the portable Windows PCAN dashboard archive with:

```bash
make dashboard-package
```

Build the native macOS PCAN dashboard application and archive with:

```bash
make dashboard-package-macos
```

The unified production builder remains the only complete modified-ROM entry
point. Map Switching, Rolling Launch, CAN telemetry, checksum closure, and the
final write-set audit run through the same command:

```bash
make rom-verify INPUT=tmp/input.bin
make rom-build INPUT=tmp/input.bin OUTPUT=tmp/output.bin
make rom-build INPUT=tmp/input.bin OUTPUT=tmp/output.bin \
  PROFILE=tmp/profile.toml
```

`make defs-generate` regenerates the tracked XML, XDF, and map ledger from an
already running and populated Memgraph instance. No root target starts,
mutates, or backs up Memgraph, flashes hardware, or deletes temporary files.
Each narrow README retains the detailed subsystem contract.
