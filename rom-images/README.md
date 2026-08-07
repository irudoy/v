# ROM images - dump manifest

Ground-truth ROM dumps for the **VQ HR ECU** project: images from the RomRaider
forum and owned reads from physical ECUs.

Original binaries (`*.bin`) are versioned in Git; duplicate archives are not
stored. This file is the identification manifest. Dumps are identified by
`sha256`.

## Layout and naming

The top level contains only ECM part-number directories in `23710-XXXXX` format,
the shared manifest, and the machine-readable registry:

```text
rom-images/
  23710-XXXXX/
    README.md
    <rom-id>-<YYYYMMDD>-stock.bin
    <rom-id>-<YYYYMMDD>-stock.bin.md5
    <other artifacts>
  README.md
  roms.csv
```

`rom-id` comes from the calibration identifier inside the ROM, for example
`1JK08A` or `11ND0A`. The date is:

- the read date for an owned dump;
- the repository import date for an external stock image.

An MD5 sidecar is named `<binary>.md5` and uses GNU format:
`<md5> *<filename>`. SHA-256 is the primary identifier and is recorded in
`roms.csv` and the directory README.

Generated JK08A tuning images are not stored under `rom-images`. Concrete tune
profiles, per-image build recipes, generated ROMs, checksum sidecars, active
tune identities, and logs remain local artifacts outside the repository. The
repository records only universal patch, composition, definition, and
verification contracts for derived JK08A images.

The layout, names, `roms.csv`, and MD5 sidecars are checked with:

```bash
python3 -m unittest patches.tests.test_rom_images_layout -v
```

`1ND0A` / `1ND3B` (1.5 MiB, SH7059, JDM) and `JK78C` (1.0 MiB, SH7058,
USDM) are **VQ37VHR** images of the same engine across two ECU generations. They
form a homolog pair for reverse engineering. `JK00A`, `JK03A`, `JK03B`, and
`JK08A` (1.0 MiB, SH7058, JDM) share their known executable ranges and form one
cross-application exact-code family. JK00A is for the **VQ35HR** PV36 Skyline
350GT; JK03A, JK03B, and JK08A are for the **VQ25HR** V36 Skyline 250GT. JK03A
is a forum package containing `ROM + external SPI EEPROM`; the other three are
owned reads without EEPROM dumps. `JK00C` and `JK00D` (1.0 MiB, SH7058) are
owned ROMs from physical **VQ35HR**-class bench ECUs and use code bases distinct
from both the shared `7MFKAVN86` family and each other. Documentation for the
physical ECUs and the project is in the Russian-language Obsidian project
`🎛️ Electronics/VQ HR ECU Tuning`; see `../AGENTS.md`.

The MCU core is **SH-2E** (SH-2 plus a single-precision FPU), as confirmed by the
Renesas datasheet
(`../refs/renesas-sh7059-sh7058s-hardware-manual.pdf`). In Ghidra, load it as
`SuperH:BE:32:SH-2A`, the only built-in variant with an FPU.

## Dumps

| File | Size (bytes) | Flash / MCU | ECM part # | Vehicle | Engine | Market | Bus |
|------|-------------:|-------------|------------|---------|--------|--------|-----|
| `23710-1ND0A/11ND0A-20260715-stock.bin` | 1,572,864 (0x180000) | 1.5 MiB / SH7059 * | 23710-1ND0A | V36 Skyline Coupe (CKV36) | VQ37VHR | JDM | CAN * |
| `23710-1ND3B/11ND3B-20260715-stock.bin` | 1,572,864 (0x180000) | 1.5 MiB / SH7059 * | 23710-1ND3B | V36 Skyline Coupe (CKV36) | VQ37VHR | JDM | CAN * |
| `23710-JK00A/1JK00A-20260804-stock.bin` | 1,048,576 (0x100000) | 1.0 MiB / SH7058 (`SH705822N`) | 23710-JK00A | V36 Skyline 350GT (PV36; exact-part marketplace) | VQ35HR | JDM | CAN |
| `23710-JK00C/1JK00C-20260803-stock.bin` | 1,048,576 (0x100000) | 1.0 MiB / SH7058 (`SH705822N`) | 23710-JK00C | V36 Skyline 350GT (PV36; hardware-family) | VQ35HR | JDM | CAN |
| `23710-JK00D/1JK00D-20260726-stock.bin` | 1,048,576 (0x100000) | 1.0 MiB / SH7058 (`SH705822N`) | 23710-JK00D | bench ECU | VQ35HR | unknown | CAN |
| `23710-JK03A/1JK03A-20260715-stock.bin` | 1,048,576 (0x100000) | 1.0 MiB / SH7058 | 23710-JK03A | V36 Skyline 250GT | VQ25HR | JDM | CAN * |
| `23710-JK03B/1JK03B-20260804-stock.bin` | 1,048,576 (0x100000) | 1.0 MiB / SH7058 (`SH705822N`) | 23710-JK03B | V36 Skyline 250GT | VQ25HR | JDM | CAN |
| `23710-JK08A/1JK08A-20260726-stock.bin` | 1,048,576 (0x100000) | 1.0 MiB / SH7058 (`SH705822N`) | 23710-JK08A | V36 Skyline 250GT | VQ25HR | JDM | CAN |
| `23710-JK78C/1JK78C-20260715-stock.bin` | 1,048,576 (0x100000) | 1.0 MiB / SH7058 * | 23710-JK78C | Infiniti G37 (2008-09) | VQ37VHR | USDM | CAN * |

The `23710` prefix is the Nissan/Infiniti part-number prefix for an ECM, according
to the parts.nissanusa catalog.

`JK03A` is the package under `23710-JK03A/`: the main flash image
`1JK03A-20260715-stock.bin` and the external **ST95320 SPI EEPROM**
`ST95320-20260715-nats-sync.bin` (4,096 bytes, NATS
synchronization/adaptation). The MCU (`SH705822N`), software (`7MFKAVN86`), and
calibration (`1JK03A00000`) identify themselves through strings in the image.
The immobilizer path is analyzed in
`../patches/immo-off-developer-flag.md`. The directory README contains the full
package inventory and hashes.

`JK08A` is an owned read from the target V36 Skyline 250GT ECU dated 2026-07-26.
It was read with PCMFlash 1.2.0, module 18, through Scanmatik-SM2 USB. The ROM
contains `1JK08A00000`, `7MFKAVN86`, and `SH705822N`. It differs from JK03A at
121 byte positions within `0x008200..0x0190c9`, while
`0x000000..0x0081ff` and the entire `0x020000..0x0fffff` range are
byte-identical. The executable code and Developer Immobilizer flag at `0x8725`
are an exact match; calibration/configuration data is not identical. The package
does not contain an EEPROM read or PCMFlash screenshot. The directory README
contains the complete local identification.

`JK00A` is an owned read dated 2026-08-04. PCMFlash identification and ROM
strings record calibration `1JK00A00000`, software `7MFKAVN86`, and type
`SH705822N`; the original filename records Hitachi hardware `MEC100-120 C1`,
lot `7515`. Public exact-part listings associate it with the automatic JDM PV36
Skyline 350GT and VQ35HR. Its known executable ranges are byte-identical to the
VQ25HR JK03A, JK03B, and JK08A images despite the different engine application.
JK00A differs from those images at 9,125, 9,118, and 9,163 byte positions,
respectively, all within `0x008200..0x0191ad`. The directory README contains
the complete identification and confidence boundary.

`JK03B` is an owned pre-write read dated 2026-08-04. PCMFlash identification
and ROM strings record calibration `1JK03B00000`, software `7MFKAVN86`, and
type `SH705822N`; the original filename records Hitachi hardware
`MEC100-191 A1`, lot `7911`. Its known executable ranges are byte-identical to
JK03A and JK08A. JK03B differs from JK03A at 118 byte positions in 44 ranges,
all within `0x008200..0x014ff1`, and from JK08A at 229 byte positions in 94
ranges, all within `0x008200..0x0190c9`. Its stock `[0x8080, 0x8100)` line is
filled with `0xEE`, which rules out an unconditional PCMFlash read transform as
the cause of the zero line in the later marker-only readback. The directory
README contains the complete identification and public application evidence.

`JK00C` is an owned pre-write read dated 2026-08-03 from the physical bench ECU
later used for the controlled map-switching failure reproduction. PCMFlash
identification and ROM strings record calibration `1JK00C00000`, software
`8MFKPCN14`, and type `SH705822N`; the original filename records Hitachi
hardware `MEC100-120 C1`, lot `6Z03`. Public hardware-family evidence associates
`MEC100-120 C1` with the automatic JDM PV36 Skyline 350GT and VQ35HR, but an
exact public catalog entry for `23710-JK00C` was not found. JK00C and JK00D
differ at 466,806 byte positions and are not an exact-code pair. The directory
README contains the full provenance and confidence boundary.

`JK00D` is an owned read from a physical bench ECU dated 2026-07-26. PCMFlash
1.2.0 module 18 over Scanmatik-SM2 USB reports `23710-JK00D`, calibration
`1JK00D00000`, main number `8MFK36N15`, type `SH705822N`, and the Hitachi CAN
protocol. The same calibration, main number, and type occur as ROM strings at
`0x8204`, `0x7009`, and `0x50C6`. The package does not contain an external
EEPROM read; this does not establish that the hardware lacks one. The directory
README contains the complete local identification.

`*` Flash sizes (1.0 / 1.5 MiB) and the **SH-2E** core are confirmed by the
Renesas datasheet. The specific on-board chip model (SH7058 vs SH7059) and CAN
bus are inferred from flash size and the Hitachi HR CAN ECU family; final
verification requires disassembly or chip markings. As a cross-check, PCMflash
Module 18 covers `EFI SH705927N (Hitachi SH7059/1.5MB)`, which matches the `1ND`
dump class. Its USDM listing includes
`EFI SH70582xN (Hitachi SH7058/1MB)`, which matches the `JK78C` class. See
`../refs/pcmflash-module-list.md`.

### SHA-256 identification

`roms.csv` is the registry, with one row per dump file: path, ROM graph label,
and SHA-256. It is machine-readable. Stage 4 of the map pipeline resolves the
image by label and verifies its hash before reading values
(`../tools/mapkit/rom.py`), so dump identification is a run precondition rather
than human-only reference data. The label is empty for an image that is not
represented in the graph, such as an EEPROM. Derived images are excluded from
the stock-source registry; their hashes are recorded in the relevant
modification README.

### Provenance and confidence

- `1ND0A`: RomRaider thread t=22253 (CKV36, FID `8FZ35NEE6`). Engine and vehicle
  confidence is high; the part-number-to-CKV36 and FID association is
  **forum-grade** and should be verified from a dump read.
- `1ND3B`: RomRaider thread t=22328, "Does anyone have the CKV36 file?
  (237101ND3B)". High confidence; **forum-grade**.
- `JK78C`: no RomRaider thread was found. Identification comes from part-number
  catalogs, where the 23710-JK7xC series denotes a 2008 Infiniti G37 3.7L.
  **Catalog-grade** (mintt / fs1inc); the replacement list for original
  23710-JK78B names JK78C.
- `JK03A`: RomRaider thread t=11098, "Nissan stock ROM list", Break_Neck post
  p=150228: Skyline V36 VQ25HR 2WD 5AT, 23710-JK03A, software
  `7MFKAVN86`, 7058 MCU, and "ROM + SPI EEPROM". The part number, software, and
  calibration (`1JK03A00000`) are confirmed by strings inside the image, giving
  **high confidence**. The `ST95320-20260715-nats-sync.bin` EEPROM dump is from
  the same post.
- `JK08A`: an owned physical target ECU from a V36 Skyline 250GT. Local
  provenance confirms the part number and read method. ROM content confirms the
  software identifier, calibration, SH7058 class, and flash size, giving
  **high confidence**. The external EEPROM was not read.
- `JK00A`: an owned physical ECU read with PCMFlash. The part number,
  calibration, software ID, MCU class, hardware identifier, and hashes have
  local provenance. Public exact-part records identify the automatic PV36
  Skyline 350GT / VQ35HR application at **marketplace-grade** confidence. Its
  exact-code relationship to JK03A/JK03B/JK08A is established independently by
  ROM comparison. The external EEPROM was not read.
- `JK03B`: an owned physical ECU with a pre-write PCMFlash read. The part
  number, calibration, software ID, MCU class, hardware identifier, and hashes
  have local provenance. Exact-code homology with JK03A/JK08A and public
  exact-part/hardware-family records identify the V36 Skyline 250GT / VQ25HR
  application with **high confidence**. The external EEPROM was not read.
- `JK00C`: an owned physical ECU with a pre-write PCMFlash read. The part
  number, calibration, software ID, MCU class, hardware identifier, and hashes
  have local provenance. The PV36 Skyline 350GT / VQ35HR application is based
  on public `MEC100-120 C1` hardware-family records rather than an exact
  `23710-JK00C` catalog record and is therefore **marketplace-grade**. The
  external EEPROM was not read.
- `JK00D`: an owned physical bench ECU. PCMFlash reading and identification
  confirm the part number, software identifier, calibration, SH7058 class,
  flash size, and CAN protocol, giving **high confidence**. The donor vehicle
  model and market are unknown; the external EEPROM was not read.
- The `1ND0A` vs `1ND3B` delta, including model year, trim, and revision, and
  their exact model years remain unknown.

### Sources

- 1ND0A: https://www.romraider.com/forum/viewtopic.php?f=65&t=22253
- 1ND3B: https://www.romraider.com/forum/viewtopic.php?f=65&t=22328
- V36 Coupe specifications (11ND2A / VQ37VHR / JDM / 2008): https://www.romraider.com/forum/viewtopic.php?f=64&t=22280
- Flash evolution from 1 MB to 1.5 MB: https://www.romraider.com/forum/viewtopic.php?f=65&t=21905
- Nissan stock ROM list (Z34 VQ37VHR loader 705927): https://www.romraider.com/forum/viewtopic.php?f=65&t=11098
- JK03A (V36 VQ25HR 2WD 5AT, ROM + SPI EEPROM, Break_Neck): https://www.romraider.com/forum/viewtopic.php?p=150228#p150228
- JK00A (exact part, PV36 Skyline 350GT, VQ35HR): https://www.carsjp.ru/parts/nissan/skyline/blok_upravleniya_dvs
- JK00A / MEC100-120 (exact part and hardware, PV36, VQ35HR): https://www.wiweb.ru/vladivostok/parts/auto?mark=nissan&model=skyline&page=2&sort=date_asc
- JK03B (exact part, V36 2.5 AT, SH7058): https://otomotiv-forum.com/threads/chip-ttyuning-nissan-skyline-v36-at-2-5i-proshivka-yevro-2-tyun.63512/
- MEC100-191 A1 (V36 250GT, VQ25HR, AT): https://yahoo.aleado.com/lot?auctionID=m403371593
- MEC100-120 C1 (PV36 350GT, VQ35HR, AT): https://www.ebay.com/itm/284029944805
- JK7x = 2008 Infiniti G37 3.7L: https://www.fs1inc.com/23710-jk78a-2008-infiniti-g37-3-7l-pcm-engine-computer-ecm-ecu-programmed-plug-play.html
- 23710 = Nissan ECM part-number prefix: https://parts.nissanusa.com/parts/nissan-engine-control-module-ecm-23710zv24a
- Renesas SH7059 / SH7058S (SH-2E core, 1.5 / 1.0 MiB flash): https://www.renesas.com/en/document/mah/sh-2e-sh7059-f-ztattm-sh7058s-f-ztattm-hardware-manual
- PCMflash module list (Module 18 SH705927N / SH7059): https://scanmatik.ru/downloads/PCM_module_list.pdf
- VQ engine / VVEL: https://en.wikipedia.org/wiki/Nissan_VQ_engine

Ground truth is in the hardware. A part number and forum thread are orientation
points; disassembly provides the final cross-check.

Historical Developer Immobilizer validation, map-switching, and Rolling Launch
artifacts are not retained under `rom-images/`. Their byte contracts, hashes,
and hardware evidence remain documented under `../patches/`.
