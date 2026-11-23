# External references

Reference sources for the **VQ HR ECU** project; see `../AGENTS.md`. The
ignored `local/` directory holds optional UpRev and EcuTek reference copies.

Project-authored manifests and mirror wrappers are in English. Original
primary-source documents preserve the source language; Markdown conversions
use English while preserving the source structure and technical content.

## Nissan definition submodules

`nissan-definitions/` contains pinned public Nissan definition repositories for
comparison only:

| Path | Upstream | Role |
|---|---|---|
| `nissan-definitions/Pytrex-NissanDefinitions` | `Pytrex/NissanDefinitions` | Canonical public Nissan RomRaider collection and address-free A2L vocabulary |
| `nissan-definitions/a33b-NissanDefs` | `a33b/NissanDefs` | Earlier collection and VQ37VHR comparison definitions |

The submodules have no upstream license file and are not republished by this
repository; Git stores their pinned commit references. Their addresses belong
to other ECUIDs and cannot be copied to JK08A. Geometry, vocabulary, and scaling
remain candidate comparison evidence until exact target code establishes a
claim.

Initialize or update the pinned content with standard Git submodule commands.
Changing a pin is a reviewed source update and must be accompanied by the
relevant catalog and definition verification.

## Documents

| File (`.pdf` + `.md`) | Pages | Type | Contents |
|------------------------|------:|------|----------|
| `renesas-sh7059-sh7058s-hardware-manual` | 1050 | Renesas datasheet | SH7058S / SH7059 F-ZTAT hardware manual: **SH-2E** core, flash (1.0 / 1.5 MB), RAM, on-chip **HCAN-II** (CAN 2.0B), FPU, peripherals, and registers. |
| `pcmflash-module-list` | 18 | PCMflash list | Reflash modules. **Module 18 "Nissan/Infiniti CAN-bus"** includes `EFI SH705927N (Hitachi SH7059/1.5MB) [RD/WR/CK]`; **Module 42** is `"Denso SH705X Bootloader"`. |
| `bosch-lsu-4.9-datasheet` | 4 | Bosch datasheet | Bosch LSU 4.9 sensor: planar ZrO2, five-wire, single-cell; basis of the AEM UEGO X-Series. |
| `nissan-ners-techinfo` | 9 | Nissan first-party | NERS (Nissan ECU Reprogramming Software) over J2534: signed calibrations by part number only, without a raw dump. |
| `motec-m150-datasheet` | 7 | MoTeC datasheet | M150 ECU I/O, including ten half-bridge outputs, and specifications. |
| `local/uprev/UpRev-Nissan-Tuning-Guide-Rev2` | 28 | UpRev vendor guide | Nissan/Infiniti tuning guide: stock-ECU reflashing, boost, failsafes, NATS, and licensing context. Includes `.pdf` and MarkItDown `.md`. |
| `local/uprev/UpRev-User-Guide-Rev2` | 12 | UpRev vendor guide | UpRev user guide for reflash tooling and workflow. PDF only. |
| `local/uprev/ECU-Bench-Harness-Pinouts` | 1 | UpRev vendor guide | One-page ECU bench-harness pinout. PDF only. |

## SHA-256 of original PDFs

- `renesas-sh7059-sh7058s-hardware-manual.pdf` - `6d8b0e3511ed583df0bec31d0d28641d1b06b23042985f41ad2d9df44fccd8ca`
- `pcmflash-module-list.pdf` - `3168d6e18d4d3de22d65a6926ce66c3019ed16252b325314a857223818520673`
- `bosch-lsu-4.9-datasheet.pdf` - `049837312a1edfb9e01e5fa767e86ab2a67697cc3fafd20c9b02674e51dac8c7`
- `nissan-ners-techinfo.pdf` - `5488a68bacd51bb4f77f0ad628184530d690abb9ab81ab3d06ba0801922b1b6a`
- `motec-m150-datasheet.pdf` - `ca9f400d314ebeecd7e3cdbd7c7a4bab9280737154519ab6c2286dbd4845910c`
- `local/uprev/UpRev-Nissan-Tuning-Guide-Rev2.pdf` - `e337931010c4c9996f7f9556947f63613c73fe847c66a5b810878a665e48707e`
- `local/uprev/UpRev-User-Guide-Rev2.pdf` - `f6ade3f275e234c6533c640ff0fadba4ceb3ffa212aa846c2b488ee83dd3d5bd`
- `local/uprev/ECU-Bench-Harness-Pinouts.pdf` - `335650facbc45a3a3d056e196fb78c715f8c352f4e92bad75c158fa425cbe4f8`

## Source URLs

- Renesas SH7059 / SH7058S hardware manual (SH-2E, REJ09B0177): https://www.renesas.com/en/document/mah/sh-2e-sh7059-f-ztattm-sh7058s-f-ztattm-hardware-manual
- PCMflash module list: https://scanmatik.ru/downloads/PCM_module_list.pdf
- Bosch LSU 4.9 datasheet mirror: https://www.milspecwiring.com/DATA%20SHEETS/lambda/BoschLSU4.9Sensor.pdf
- Nissan NERS TechInfo: https://www.nissan-techinfo.com/documents/Nissan_TechInfo_Ners.pdf
- MoTeC M150 datasheet mirror: https://www.milspecwiring.com/DATA%20SHEETS/ECU/M150.pdf
- UpRev Nissan Tuning Guide: https://uprev.com/wp-content/uploads/2023/05/UpRev-Nissan-Tuning-Guide-Rev2.pdf
- UpRev document downloads: https://www.uprev.com/support/
- NissanECU RE wiki mirror under `nissanecu-wiki/`: https://nissanecu.miraheze.org/wiki/Main_Page
- RomRaider Nissan ECU unbrick and hard-reflash thread under `romraider/`: https://www.romraider.com/forum/viewtopic.php?f=65&t=12821
- EcuTek 370Z ProECU Tuning Guide: https://ecutek.atlassian.net/wiki/spaces/SUPPORT/pages/7143430
- EcuTek 370Z RaceROM Supplement: https://ecutek.atlassian.net/wiki/spaces/SUPPORT/pages/6881638

To restore a PDF locally, use its path above and convert it to `*.md` with
MarkItDown when a text copy is needed.

## RomRaider Nissan ECU unbrick thread

`romraider/unbrick-hard-reflash-nissan-ecu/` contains a complete Markdown
mirror of the five-page RomRaider thread `HOW TO: Unbrick and/or Hard Reflash
Nissan ECU (Step-by-Step)`. The archive contains all **64 posts** and all **48
content images**, stored locally in an adjacent `images/` directory. Forum
emoticons are represented by their text alternatives. Two downloadable archive
attachments were absent from the saved source, so their links still point to
the original forum. The printable views were retrieved on **2026-08-02**.

## NissanECU RE wiki local mirror

`nissanecu-wiki/` is a complete mirror of fenugrec's community Nissan ECU
reverse-engineering wiki: **30 pages and 34 images**. Rendered HTML
(`?action=render`) was converted with `html2text`, and image links point to local
files under `img/`. Source: https://nissanecu.miraheze.org, licensed under
**CC BY-SA 4.0**, retrieved 2026-07-15. The index and P0 relevance are documented
in `nissanecu-wiki/README.md`.

The key pages are `Firmware_re` (SID tree, SID27/36 seed-key handling, and
LOADER/FID metadata), `Checksums`, `Eeprom_code` / `Eeprom_dumps` (immobilizer
and nonvolatile data outside flash), `Communication_Protocols` / `C2_14230` /
`Std_14230`, `Ecu_hw` / `Bootmode` (hardware and SH705x boot mode), and annotated
reference ROMs `Rom_an_cf43d` / `cf48d` / `al500`. Unlike PDF primary sources,
the complete mirror, including text and small images, is versioned.

## EcuTek 370Z ProECU local conversion

`local/ecutek/` holds optional copies of two EcuTek Support pages from the Confluence
`SUPPORT` space under `Vehicle Specific Guides / Nissan / 370Z`. It includes
**173 images** and Markdown converted from rendered HTML obtained from the public
REST API (`body.export_view`), with images stored locally. The copies were retrieved
on 2026-07-16. The local conversion index and notes are in `local/ecutek/README.md`.

The 370Z uses the VQ37VHR with VVEL, the same HR architecture as ROMs `1ND0A`
and `1ND3B`, so both pages are directly relevant. Where A2L provides table shape,
element type, scaling, and axis semantics, the vendor documentation provides
meaning: calculation chains, map-selection conditions, and documented defaults
whose numeric values can be searched directly in a dump.

- `tuning-guide/` covers ProECU tables for `Ignition`, `Fuelling`,
  `Camshaft Timing`, `Boost Control`, `Accelerator and Throttle`, `Limiters`,
  `Sensor Scaling`, `Torque`, and `Idle`.
- `racerom-supplement/` covers RaceROM `Map Switching`, `Launch Control`,
  `Per Gear Rev Limits`, `Flat Foot Shifting`, `Flex Fuel`, `Speed Density`,
  `Custom Maps`, `Failsafe`, CAN I/O, and `Valet Mode`.

`Map Switching` and `Limiters` describe mechanics represented in the pipeline as
`:Flag {role:'selector'}` and `threshold`; see the current analysis stages in
`tools/map-analysis-pipeline.md`.

## Machine-readable vendor dictionaries

`vendor/` projects vendor documentation into CSV for Stage 5 of the map
pipeline. It contains a name catalog (`catalog.csv`,
371 entries, 243 factory entries) and anchor facts (`facts.csv`, 138 constants,
units, mechanics, and vendor-declared gaps). `tools/memgraph/load_vendor.py`
loads them as `:VendorEntry` and `:VendorFact`. The method, `origin` rule, and
`concept` annotation are documented in `vendor/README.md`.

This layer exists because the Map Lists in both EcuTek documents are
**screenshots**, so neither grep nor a text-only agent can access their name
catalog. UpRev is continuous prose without a map tree. The source
transcriptions, `proecu-maps.csv` and `uprev-maps.csv`, are handwritten;
`tools/vendor/build_catalog.py` generates the combined catalog. Edit the source
transcriptions rather than the generated file.

## Nissan factory ESM stored locally

Two scoped factory service manuals are stored locally. Both support precise
identification of ECU mechanics and logic through factory circuit diagrams,
connector pinouts, diagnostic procedures, and system-operation descriptions.
Each directory documents its own retention boundary and the recovery path for
omitted manual modules.

| Manual | Directory | Retained PDFs | Engine |
|---|---|---:|---|
| 2007 Infiniti G35 Sedan | `nissan-esm-2007-g35-sedan/` | 29 | VQ35HR |
| 2013 Infiniti G Sedan | `nissan-esm-2013-g37-sedan/` | 31 | VQ37VHR, VQ25HR |

The machine-readable diagnostic projections are stored separately under
`diagnostics/nissan-esm-2007-g35-sedan/` and
`diagnostics/nissan-esm-2013-g37-sedan/`. Their scope, provenance contract,
source revision, and completeness boundary are documented in
`diagnostics/README.md`.

- **Nissan ESM - 2007 Infiniti G35 Sedan (V36), VQ35HR engine.** The retained
  factory-manual subset contains 29 PDFs selected for diagnostic, electrical,
  and firmware evidence. Because the 2007 G35 Sedan uses VQ35HR, its ECM section
  is a reference for the homologous NATS architecture in the HR firmware under
  study, including VQ37VHR `1ND*`.
  Repository path: `refs/nissan-esm-2007-g35-sedan/`.

  The omitted modules remain recoverable from Git history or the complete
  official 2007 Infiniti G35 Sedan ESM distribution.

  Relevant sections:

  - `SECURITY CONTROL SYSTEM.pdf` - NATS / immobilizer (IMMU), BCM master logic,
    security ID, and indicator. SEC-41/42 specifies BCM-to-ECM ID verification
    and ECM start inhibition for an unregistered ID. SEC-165 assigns the
    `Inhibit engine cranking` failsafe to B2192/B2193. SEC-41 defines
    B2192/P1611 as `ID DISCORD, IMMU-ECM`, where the BCM-to-ECM ID check returns
    NG. SEC-42 defines B2193/P1612 as `CHAIN OF ECM-IMMU`, where ECM-to-BCM
    communication is inactive.
  - `ENGINE CONTROL SYSTEM.pdf` - VQ35HR ECM immobilizer input, start
    permission, inputs, and outputs. Table EC-525 names P1610 `LOCK MODE` and
    points to SEC-37, whose heading associates P1610 with B2190
    `NATS ANTENNA AMP`. The P1610 name alone therefore does not associate a
    specific RAM Lock bit without firmware verification. EC-117 defines
    `A/F SEN1 (B1/B2)` as an A/F signal computed by the ECM. EC-187 plots
    increasing signal voltage with increasing air-fuel ratio, while EC-188 and
    EC-484 specify fluctuation around 2.2 V on a warmed engine held at 2,000 rpm
    without load. EC-121 documents the `FUEL INJECTION` active test.
  - `STARTING SYSTEM.pdf` - starter and crank permission; cranking without a
    start directs diagnostics to engine control / EC.
  - `BODY CONTROL SYSTEM.pdf` - BCM as immobilizer master and key/antenna
    integration.
  - `LAN SYSTEM.pdf` - CAN topology, gateway, bus distribution, and CAN IDs.
  - `POWER SUPPLY, GROUND & CIRCUIT ELEMENTS.pdf` - connector pinout and
    power/ground circuits.
  - `METER, WARNING LAMP & INDICATOR.pdf` - security indicator, immobilizer
    blinking, and lamp logic.
  - `POWER CONTROL SYSTEM.pdf` and `STEERING CONTROL SYSTEM.pdf` - power and
    ignition modes and, where applicable, the steering lock.

- **Nissan ESM - 2013 Infiniti G Sedan (V36), VQ37VHR and VQ25HR engines.**
  Publication `SM3E-1V36U0`, edition August 2012. The retained factory-manual
  subset contains 31 PDFs. This is the exact factory manual for the engine and
  platform behind ROMs `JK78C`, `1ND0A`, and `1ND3B`, so it is the authority for
  VQ37VHR diagnostic names, per-bank identity, and VVEL system operation. Its
  VQ25HR sections cover the Mexico-market variant (GI-23) with the engine of
  the `JK08A` target.
  Repository path: `refs/nissan-esm-2013-g37-sedan/`.

  Relevant sections:

  - `ENGINE CONTROL SYSTEM.pdf` - VQ37VHR ECM. EC-136 states that the ECM
    commands target valve lift to the VVEL control module and receives the
    control shaft actual angle back over CAN, so the control shaft position
    sensor is not a direct ECM input. EC-407 through EC-420 name every VVEL DTC
    pair with its bank: P100A/P100B response at EC-407, P1087/P1088 small event
    angle at EC-411, P1089/P1092 control shaft position sensor at EC-412, and
    P1090/P1093 actuator motor at EC-416, with the lower code assigned to bank 1
    in every pair. P1091 at EC-420 covers the shared actuator motor relay. The
    ECM DTC index at EC-581 and EC-582 carries the same bank suffixes as the
    Consult display names. EC-162 defines the `VVEL TIM-B1` and `VVEL TIM-B2`
    monitors in `deg` of control shaft angle and the `VVEL POSITION SEN-B1` and
    `-B2` monitors in volts. EC-30 specifies the control shaft position sensor
    adjustment standard of 500 +/- 48 mV, taken at VVEL control module connector
    E15 terminals 3 and 4 for bank 1 and terminals 5 and 6 for bank 2.
  - `ENGINE MECHANICAL.pdf` - VVEL ladder assembly, actuator sub assembly, and
    control shaft hardware, with per-bank part identification.
  - `SECURITY CONTROL SYSTEM.pdf`, `BODY CONTROL SYSTEM.pdf`, and
    `LAN SYSTEM.pdf` - the VQ37VHR generation of the NATS, BCM, and CAN topology
    described for the 2007 manual above.
  - `POWER SUPPLY, GROUND & CIRCUIT ELEMENTS.pdf` and `STARTING SYSTEM.pdf` -
    connector pinout, power and ground circuits, and crank permission.
