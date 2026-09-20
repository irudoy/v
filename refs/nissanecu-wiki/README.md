# nissanecu-wiki - local NissanECU RE wiki mirror

Complete mirror of fenugrec's community Nissan/Infiniti ECU reverse-engineering
wiki at `https://nissanecu.miraheze.org`: **29 pages** in the Main namespace plus
`Nissan ECU RE:About`, and **34 images** under `img/`. It is a primary source for
firmware mechanics, immobilizer and seed-key handling, checksums, protocols, and
SH705x hardware.

- Format: rendered HTML (`?action=render`) converted to Markdown with
  `html2text`; image links point to local files under `img/`. Every page has a
  header with its source URL.
- License: **CC BY-SA 4.0**, attributed to the NissanECU RE wiki and its
  contributors.
- Retrieved: **2026-07-15**.

## P0 material: immobilizer, seed-key, and nonvolatile data

- `Firmware_re.md` (46 KB) - firmware structure: IVT and power-on reset,
  `NHU\xF8` signature, **LOADER / FID metadata**, ISO14230 SID parsing tree,
  **SID27 seed-key and SID36 keys**, and checksum references. This is the central
  page.
- `Checksums.md` - transport and content checksums, sum+XOR / RIPEMD-160, and
  covered regions.
- `Eeprom_code.md`, `Eeprom_dumps.md` - external EEPROM use for immobilizer,
  marriage, and nonvolatile data outside flash.
- `SID22.md` - ReadDataByIdentifier.
- `Bootmode.md` - SH705x boot mode and recovery flashing through PCB test points.
- `Wdt.md` - watchdog.

## Protocols and communication

- `Communication_Protocols.md` (14.5 KB) - K-line / CAN overview and diagnostic
  stack.
- `C2_14230.md` - Consult-II over ISO14230.
- `Std_14230.md` - ISO14230 (KWP2000) and its SIDs.
- `Connect.md`, `Tools.md` - connections and tooling such as nisprog, freediag,
  and cables.

## Hardware and MCU

- `Ecu_hw.md` (9.4 KB) - ECU hardware, CAN and K-line transceivers, layout, and
  PCB hardware versions.
- `Sh_dev.md`, `Sh_docs.md` - SH705x devices and documentation, including
  datasheets and the SH-2E core.

## Annotated reference ROMs for homology

- `Rom_an.md` - ROM annotation method.
- `Rom_an_cf43d.md`, `Rom_an_cf48d.md` - analyzed VQ35DE ROMs for
  cross-reference.
- `Rom_an_al500.md` - analysis of another ROM.
- `Rom_db.md` - database of known ROMs with ECUID, FID, and loader.

## Tuning and maps

- `Nissan_Map_Functionality.md`, `Tuning.md`, `Nissan_Tuning.md`, and
  `Nissan.md`; some are redirects or stubs.

## Nissan AUD diagnostic protocol

- `AUD.md`, `AUD_debug_tool.md`; `AUD_AUD_debug_tool.md` is the same page under a
  subpage alias.

## Administrative pages

- `Main_Page.md`, `Nissan_ECU_RE_About.md`, and
  `RE5R05A_TCM_Analysis.md`; the last covers the transmission and is outside the
  engine scope.

## Mirror refresh procedure

1. List pages through
   `.../w/api.php?action=query&list=allpages&apnamespace=0&aplimit=500`, plus
   `apnamespace=4`.
2. Fetch each page as `.../wiki/<Title>?action=render`, process it with
   `html2text` using `body_width=0`, and add a source-URL header.
3. Download Markdown-linked images into `img/` and rewrite the links to local
   paths.
4. Verify licensing through the API using
   `meta=siteinfo&siprop=rightsinfo`.
