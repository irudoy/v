# 2013 Infiniti G Sedan ESM source scope

This directory contains the project-relevant subset of the original 60-module
factory ESM for the 2013 Infiniti G Sedan (V36, VQ37VHR and VQ25HR),
publication `SM3E-1V36U0`, edition August 2012. It is the exact factory manual
for the engine and platform behind ROMs `JK78C`, `1ND0A`, and `1ND3B`.

GI-23 lists the VQ25HR models for Mexico only. `ENGINE CONTROL SYSTEM.pdf`
carries a VQ37VHR section followed by a VQ25HR section, and every page of
either section names its engine on the running header. The VQ25HR section
describes the engine of the `JK08A` target in a different market.

The distribution names each module by its section code. Retained copies are
renamed to the module titles published in the manual's own Quick Reference
Index, which matches the naming used by `nissan-esm-2007-g35-sedan/` and lets
one extractor attribute both corpora to the same ECU identities.

| Code | Retained file | Code | Retained file |
|------|---------------|------|---------------|
| `ADP` | `AUTOMATIC DRIVE POSITIONER.pdf` | `MWI` | `METER, WARNING LAMP & INDICATOR.pdf` |
| `AV` | `AUDIO, VISUAL & NAVIGATION SYSTEM.pdf` | `PCS` | `POWER CONTROL SYSTEM.pdf` |
| `BCS` | `BODY CONTROL SYSTEM.pdf` | `PG` | `POWER SUPPLY, GROUND & CIRCUIT ELEMENTS.pdf` |
| `BRC` | `BRAKE CONTROL SYSTEM.pdf` | `PWC` | `POWER WINDOW CONTROL SYSTEM.pdf` |
| `CCS` | `CRUISE CONTROL SYSTEM.pdf` | `RF` | `ROOF.pdf` |
| `CHG` | `CHARGING SYSTEM.pdf` | `SBC` | `SEAT BELT CONTROL SYSTEM.pdf` |
| `DEF` | `DEFOGGER.pdf` | `SEC` | `SECURITY CONTROL SYSTEM.pdf` |
| `DLK` | `DOOR & LOCK.pdf` | `SN` | `SONAR SYSTEM.pdf` |
| `DLN` | `DRIVELINE.pdf` | `SRC` | `SRS AIRBAG CONTROL SYSTEM.pdf` |
| `EC` | `ENGINE CONTROL SYSTEM.pdf` | `STC` | `STEERING CONTROL SYSTEM.pdf` |
| `EM` | `ENGINE MECHANICAL.pdf` | `STR` | `STARTING SYSTEM.pdf` |
| `EXL` | `EXTERIOR LIGHTING SYSTEM.pdf` | `TM` | `TRANSAXLE & TRANSMISSION.pdf` |
| `GI` | `GENERAL INFORMATION.pdf` | `WCS` | `WARNING CHIME SYSTEM.pdf` |
| `HAC` | `HEATER & AIR CONDITIONING CONTROL SYSTEM.pdf` | `WT` | `ROAD WHEELS & TIRES.pdf` |
| `INL` | `INTERIOR LIGHTING SYSTEM.pdf` | `WW` | `WIPER & WASHER.pdf` |
| `LAN` | `LAN SYSTEM.pdf` | | |

The retained 31 PDFs consist of every module that produces a tracked diagnostic
fragment, plus `STARTING SYSTEM.pdf` and
`POWER SUPPLY, GROUND & CIRCUIT ELEMENTS.pdf`, which carry the crank-permission
and connector evidence cited by the project, and `ENGINE MECHANICAL.pdf`, which
carries the VVEL hardware layout and its per-bank part identification.

The remaining 29 distribution files produce no diagnostic fragments and have no
callers, links, or project evidence that depends on their local copies. The
accelerator control system is split across `ACC-1` and `ACC-2`:

- `ACCELERATOR CONTROL SYSTEM.pdf` (`ACC-1`, `ACC-2`)
- `BODY REPAIR.pdf` (`BRM`)
- `BRAKE SYSTEM.pdf` (`BR`)
- `CLUTCH.pdf` (`CL`)
- `ENGINE COOLING SYSTEM.pdf` (`CO`)
- `ENGINE LUBRICATION SYSTEM.pdf` (`LU`)
- `EXHAUST SYSTEM.pdf` (`EX`)
- `EXTERIOR.pdf` (`EXT`)
- `FRONT AXLE.pdf` (`FAX`)
- `FRONT SUSPENSION.pdf` (`FSU`)
- `FUEL SYSTEM.pdf` (`FL`)
- `GLASS & WINDOW SYSTEM.pdf` (`GW`)
- `HEATER & AIR CONDITIONING SYSTEM.pdf` (`HA`)
- `HORN.pdf` (`HRN`)
- `INSTRUMENT PANEL.pdf` (`IP`)
- `INTERIOR.pdf` (`INT`)
- `MAINTENANCE.pdf` (`MA`)
- `MIRRORS.pdf` (`MIR`)
- `PARKING BRAKE SYSTEM.pdf` (`PB`)
- `POWER OUTLET.pdf` (`PWO`)
- `QUICK REFERENCE INDEX.pdf` (`FWD`)
- `REAR AXLE.pdf` (`RAX`)
- `REAR SUSPENSION.pdf` (`RSU`)
- `SEAT BELT.pdf` (`SB`)
- `SEAT.pdf` (`SE`)
- `SRS AIRBAG.pdf` (`SR`)
- `STEERING SYSTEM.pdf` (`ST`)
- `VENTILATION SYSTEM.pdf` (`VTL`)

The omitted modules remain recoverable from the complete official 2013 Infiniti
G Sedan ESM distribution under their section-code filenames.
`tools/diagnostics/extract_esm.py` enforces the retained document count and
regenerates the machine-readable projection from this directory.
