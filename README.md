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
- Runtime ownership and reserves: [`patches/runtime-reservations.md`](patches/runtime-reservations.md)
- Exact JK08A HCAN1 model: [`defs/JK08A.can.md`](defs/JK08A.can.md)
- Analysis and definition pipeline: [`tools/map-analysis-pipeline.md`](tools/map-analysis-pipeline.md)
- Tool navigation and local deployment: [`tools/README.md`](tools/README.md)
- Memgraph ingestion: [`tools/memgraph/README.md`](tools/memgraph/README.md)
- Definition generation: [`tools/mapkit/README.md`](tools/mapkit/README.md)
- Executable verification: [`tools/sh-elf-run/README.md`](tools/sh-elf-run/README.md)

The Python test contract is `uv run pytest -q`; the pin-tracer contract is
documented beside that tool. Each narrow README owns its operational commands.
