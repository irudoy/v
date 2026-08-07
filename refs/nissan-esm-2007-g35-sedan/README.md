# 2007 Infiniti G35 Sedan ESM source scope

This directory contains the project-relevant subset of the original 56-module
factory ESM. The retained 29 PDFs consist of every module that produces a
tracked diagnostic fragment, plus `STARTING SYSTEM.pdf` and
`POWER SUPPLY, GROUND & CIRCUIT ELEMENTS.pdf`, which are cited directly by the
project knowledge base and source manifest.

The following 27 modules produce no diagnostic fragments and have no callers,
links, or project evidence that depends on their local copies:

- `ACCELERATOR CONTROL SYSTEM.pdf`
- `BODY REPAIR.pdf`
- `BRAKE SYSTEM.pdf`
- `CLUTCH.pdf`
- `ENGINE COOLING SYSTEM.pdf`
- `ENGINE LUBRICATION SYSTEM.pdf`
- `ENGINE MECHANICAL.pdf`
- `EXHAUST SYSTEM.pdf`
- `EXTERIOR.pdf`
- `FOREWORD.pdf`
- `FRONT AXLE.pdf`
- `FRONT SUSPENSION.pdf`
- `FUEL SYSTEM.pdf`
- `GENERAL INFORMATION.pdf`
- `GLASS & WINDOW SYSTEM.pdf`
- `HEATER & AIR CONDITIONING SYSTEM.pdf`
- `HORN.pdf`
- `INSTRUMENT PANEL.pdf`
- `INTERIOR.pdf`
- `MAINTENANCE.pdf`
- `PARKING BRAKE SYSTEM.pdf`
- `POWER OUTLET.pdf`
- `REAR AXLE.pdf`
- `REAR SUSPENSION.pdf`
- `SEAT BELT.pdf`
- `STEERING SYSTEM.pdf`
- `VENTILATION SYSTEM.pdf`

The omitted modules remain recoverable by their exact paths from Git history or
from the complete official 2007 Infiniti G35 Sedan ESM distribution. No Git
history is rewritten. `tools/diagnostics/extract_esm.py` enforces the retained
document count and regenerates the machine-readable projection from this
directory.
