# VQ HR ECU Tuning

Reverse engineering and calibration tools for Hitachi CAN ECUs used with Nissan
and Infiniti VQ25HR, VQ35HR, and VQ37VHR engines.

> [!WARNING]
> This is a personal research project.
> Use it at your own risk. A bad flash or calibration can brick the ECU, damage
> the engine, or make the car unsafe to drive. Have all calibration work performed
> by a qualified tuner. Validate the exact image and ECU on a bench before road use.

## Implemented features

- **Editor definitions** for [RomRaider and TunerPro](defs/README.md), with
  calibration tables, axes, and supported switches for each registered ROM.
- **[ROM builder](patches/rom-builder.md)** with calibration transfer, checksum
  verification, and a build manifest.
- **[Map Switching](patches/map-switching-selector.md)** for selecting calibration
  slots with the steering-wheel switches.
- **[Custom CAN telemetry](patches/can-telemetry.md)** with a
  [PCAN-USB dashboard](tools/can_dashboard/README.md) for Windows and macOS and
  [log conversion tools](tools/logs/README.md).
- **Firmware analysis and verification** through the [knowledge base](tools/kb/README.md),
  [ROM atlas](tools/romviz/README.md), and [GNU SH-2E simulator](tools/sh-elf-run/README.md).

## ECU and vehicle support

Match the exact ECU part number and ROM identity. Vehicle applications describe
the registered images. See [ROM provenance](rom-images/README.md#provenance-and-confidence)
for the evidence behind each application. ECU part numbers below use the Nissan
and Infiniti `23710-` prefix.

| ROM family | ECU suffixes | Vehicle application | Software support | Recorded road tests |
| --- | --- | --- | --- | --- |
| 7MFKAVN86 | JK00A, JK03A, JK03B, JK08A | Nissan Skyline PV36 350GT (VQ35HR, JK00A) and V36 250GT (VQ25HR) | Editor definitions, Map Switching, CAN telemetry | Map Switching, CAN telemetry |
| 8MFK | JK00C, JK00D | Skyline PV36 350GT (JK00C hardware-family match). JK00D donor unknown. | Editor definitions, Map Switching, CAN telemetry | None recorded |
| JK78C | JK78C | 2008 Infiniti G37 3.7L (VQ37VHR, catalog match) | Editor definitions, Map Switching, CAN telemetry | None recorded |
| 1ND | 1ND0A, 1ND3B | Nissan Skyline CKV36 coupe (VQ37VHR, forum attribution) | Editor definitions, Map Switching, CAN telemetry | None recorded |
| 1ME3B | 1ME3B | Nissan Fuga KY51 (VQ37VHR) | Editor definitions, Map Switching, CAN telemetry | None recorded |
| 1EK7A | 1EK7A | 2013 Nissan 370Z Z34, manual (VQ37VHR, JDM, donor-reported) | Editor definitions, Map Switching, CAN telemetry | None recorded |

The road records are for JK08A-based images running on a physical
`23710-JK00D` ECU. Each record applies to its exact image. See the
[hardware results](patches/hardware-results.toml) and the
[full support matrix](rom-images/support-matrix.md) for per-ROM limitations,
telemetry coverage, and bench evidence.

## Setup and prerequisites

Install Git, Make, `uv`, and Docker with Compose for the analysis workspace.
Install Node.js and npm for the atlas and pin-tracer checks and Poppler
(`pdftotext` and `pdfinfo`) for the diagnostic source checks.

```sh
make setup
uv run kb brief
```

`make setup` installs the locked Python environment, initializes the pinned
reference submodules, and builds the local Memgraph index. The
[tool index](tools/README.md#local-deployment) lists task-specific dependencies,
including Ghidra with JDK 21 for new structure exports and the PEAK driver for
live PCAN-USB capture.

## Build and verify

Use a registered stock ROM and the definition for its exact identity.
[ROM intake](rom-images/new-rom-intake.md) describes how to register a new
stock read. [Definition generation](tools/mapkit/README.md) and the
[analysis pipeline](tools/map-analysis-pipeline.md) describe where to record
reviewed findings and how to regenerate their projections.

```sh
make rom-verify INPUT=STOCK.bin
make rom-build INPUT=STOCK.bin OUTPUT=tmp/output.bin
make rom-extract INPUT=tmp/tuned.bin \
  CALIBRATION=tmp/tuned-calibration.toml PROFILE=tmp/tuned-profile.toml
make rom-calibrate INPUT=tmp/output.bin \
  CALIBRATION=tmp/tuned-calibration.toml OUTPUT=tmp/calibrated.bin
make preflash INPUT=tmp/calibrated.bin ROM=JK08A
```

The [builder guide](patches/rom-builder.md) covers runtime profiles, calibration
transfer, and supported targets. Keep tuned images and profiles outside Git.

Before flashing, run `make preflash` with GitHub CLI (`gh`) available.
It requires a clean checkout and a successful `Verify` run for its exact
commit. It rebuilds the image byte for byte from the matching stock ROM and runs
the patch tests and SH-2E gate for that ROM. Actual flashing uses a separate
tool and its supported OBD interface.

```sh
make check
make test
make verify
```

- `make check` checks tracked sources, generated projections, and KB answers.
  It uses a populated Memgraph instance.
- `make test` runs the fast Python tests and the pin-tracer tests.
  `make test-changed` selects affected tests. `make test-full` also runs the
  slow Python tests.
- `make verify` runs the firmware gate, source checks, and full tests.

Run `make help` for targets and options, including definition generation, the
ROM atlas, and dashboard packaging.

## Continuous verification

The [Verify workflow](.github/workflows/verify.yml) runs on pushes to
`master` and on manual dispatch. It runs the GNU SH-2E firmware gate and
checks sources and tests against an initialized Memgraph index. Select
`full` on manual dispatch to rebuild the graph from an empty instance.

| Check outside the standard CI run | Where to run it |
| --- | --- |
| Dashboard GUI tests | Local `make verify` with a display |
| Tests that use local road captures or images | Local `make verify` with the matching inputs |
| `tools/check_projection_contract.py --run` | Manual run with all registered sources, including `VQ_OBD2TOOLS_SOURCE` |

## Contributing

Pull requests and feedback are welcome. Small fixes, documentation,
reproducible firmware findings, and reports from bench or road tests are all
useful. For a ROM-specific report, include the ECU part number, ROM ID, and
the steps or conditions that reproduce the result. Open an
[issue](https://github.com/irudoy/vhrev/issues) for feedback or a bug report.

## License

The original project code is available under the
[PolyForm Noncommercial License 1.0.0](LICENSE). Third-party firmware and
reference materials are subject to their respective terms.
