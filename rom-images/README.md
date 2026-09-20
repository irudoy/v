# ROM images - dump manifest

Ground-truth ROM dumps for the **VQ HR ECU** project: images from the RomRaider
forum and owned reads from physical ECUs.

Original binaries (`*.bin`) are versioned in Git; duplicate archives are not
stored. This file is the identification manifest. Dumps are identified by
`sha256`.

A previously unmodelled image enters the project through
[`new-rom-intake.md`](new-rom-intake.md), which classifies it, selects a
scenario branch, and states what that branch inherits and must recover.

## Layout and naming

The top level contains only ECM part-number directories in `23710-XXXXX` format,
the shared manifest, and the machine-readable registry:

```text
rom-images/
  23710-XXXXX/
    README.md                 # only when the directory has additional evidence
    <rom-id>-<YYYYMMDD>-stock.bin
    <rom-id>-<YYYYMMDD>-stock.bin.md5
    <other artifacts>
  README.md
  homology.toml             # declared code families and comparison method
  homology.csv              # generated pairwise measurements
  roms.csv
```

`rom-id` comes from the calibration identifier inside the ROM, for example
`1JK08A` or `11ND0A`. The date is:

- the read date for an owned dump;
- the repository import date for an external stock image.

An MD5 sidecar is named `<binary>.md5` and uses GNU format:
`<md5> *<filename>`. SHA-256 is the primary identifier and is recorded in
`roms.csv`; a directory README is present only for additional package,
provenance, hardware, or comparison evidence.

Generated JK08A tuning images are not stored under `rom-images`. Concrete tune
profiles, per-image build recipes, generated ROMs, checksum sidecars, active
tune identities, and logs remain local artifacts outside the repository. The
repository records only universal patch, composition, definition, and
verification contracts for derived JK08A images.

The layout, names, registries, generated homology report, and MD5 sidecars are
checked with:

```bash
uv run python tools/rom_homology.py --check
uv run python -m unittest patches.tests.test_rom_images_layout -v
```

`1ND0A` / `1ND3B` (1.5 MiB, SH7059, JDM) and `JK78C` (1.0 MiB, SH7058,
USDM) are **VQ37VHR** images of the same engine across two ECU generations. They
form a homolog pair for reverse engineering. `1ME3B` (1.5 MiB, SH7059, JDM)
is a third **VQ37VHR** image on the same MCU class as the `1ND` pair, but with
an independent application layout. `JK00A`, `JK03A`, `JK03B`, and
`JK08A` (1.0 MiB, SH7058, JDM) share their known executable ranges and form one
cross-application exact-code family. JK00A is for the **VQ35HR** PV36 Skyline
350GT; JK03A, JK03B, and JK08A are for the **VQ25HR** V36 Skyline 250GT. JK03A
is a forum package containing `ROM + external SPI EEPROM`; the other three are
owned reads without EEPROM dumps. `JK00C` and `JK00D` (1.0 MiB, SH7058) are
owned ROMs from physical **VQ35HR**-class bench ECUs. They form a near-code
family with extensive exact content but nonuniform address relocations and are
distinct from the shared `7MFKAVN86` exact-code family.

The MCU core is **SH-2E** (SH-2 plus a single-precision FPU), as confirmed by the
Renesas datasheet
(`../refs/renesas-sh7059-sh7058s-hardware-manual.pdf`). In Ghidra, load it as
`SuperH:BE:32:SH-2A`, the only built-in variant with an FPU.

## Dumps

| File | Size (bytes) | Flash / MCU | ECM part # | Vehicle | Engine | Market | Bus |
|------|-------------:|-------------|------------|---------|--------|--------|-----|
| `23710-1ME3B/11ME3B-20260825-stock.bin` | 1,572,864 (0x180000) | 1.5 MiB / SH7059 (`SH705927N`) | 23710-1ME3B | KY51 Fuga | VQ37VHR | JDM | CAN |
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
A dismantler listing for the exact part number records Hitachi hardware
`MEC100-190` on a `DBA-V36` registered 2007/2 with the `VQ25-HRTM` engine,
5AT `RE5R05A`, and FR drive.
The immobilizer path is analyzed in
`../patches/immo-off-developer-flag.md`. The directory README records the
package relationship.

`JK08A` is an owned read from the target V36 Skyline 250GT ECU dated 2026-07-26.
It was read with PCMFlash 1.2.0, module 18, through Scanmatik-SM2 USB. The ROM
contains `1JK08A00000`, `7MFKAVN86`, and `SH705822N`. It differs from JK03A at
121 byte positions within `0x008200..0x0190c9`, while
`0x000000..0x0081ff` and the entire `0x020000..0x0fffff` range are
byte-identical. The executable code and Developer Immobilizer flag at `0x8725`
are an exact match; calibration/configuration data is not identical. The package
does not contain an EEPROM read or PCMFlash screenshot. The directory README
records target-specific comparison evidence.

`JK00A` is an owned read dated 2026-08-04. PCMFlash identification and ROM
strings record calibration `1JK00A00000`, software `7MFKAVN86`, and type
`SH705822N`; the original filename records Hitachi hardware `MEC100-120 C1`,
lot `7515`. Public exact-part listings associate it with the automatic JDM PV36
Skyline 350GT and VQ35HR. Its known executable ranges are byte-identical to the
VQ25HR JK03A, JK03B, and JK08A images despite the different engine application.
JK00A differs from those images at 9,125, 9,118, and 9,163 byte positions,
respectively, all within `0x008200..0x0191ad`. The directory README records
the original read identity and confidence boundary.

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

`1ME3B` is an owned bench read dated 2026-08-25 from a physical ECU whose
donor is a JDM KY51 Fuga with VQ37VHR. PCMFlash identification and ROM strings
record calibration `11ME3B00000`, software `9FZ3V5DD1`, and type `SH705927N`;
the ECU label records Hitachi hardware `MEC108-280 D1`, lot `0705`. The image
shares the SH7059 class, the 1.5 MiB flash, and the boot and vector blocks
with the `1ND` pair, differing below `0x008200` at only 14 byte positions, but
its application is independently laid out and reaches `0x139dc3` against
`0x12c98f`. It reproduces the four `1ND` SUM16 checksum
domains at their `1ND` field addresses and relocates the application XOR and
SUM fields to `0x0096f4` and `0x0096fc`. Its diagnostic descriptor region is
byte-identical to `1ND0A` across 1,936 bytes at a constant `+0x164`
relocation and carries the VQ37 group `0x37` sequence without exhaust camshaft
records. That region holds 334 descriptor records at `0x1bf58` and their
attribute pointers at `0x1cf00`, from which `../defs/1ME3B.dtc.csv` carries 38
codes. The directory README contains the complete identification and comparison
evidence.

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
  the stock-source registry; immutable hardware-tested identities are recorded
  in `../patches/hardware-results.toml`.

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
  **high confidence**. A dismantler listing for the exact part number carries
  the same 2WD 5AT VQ25HR application and adds Hitachi hardware `MEC100-190` at
  **marketplace-grade** confidence. The `ST95320-20260715-nats-sync.bin` EEPROM
  dump is from the same post.
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
- `1ME3B`: an owned physical ECU with a bench PCMFlash read. The part number,
  calibration, software ID, MCU class, hardware identifier, and hashes have
  local provenance. The donor JDM KY51 Fuga and its VQ37VHR engine are known
  directly from the vehicle the ECU was removed from, giving **high
  confidence**. The external EEPROM was not read.
- The `1ND0A` vs `1ND3B` delta, including model year, trim, and revision, and
  their exact model years remain unknown.

### Hitachi hardware identifiers

The Hitachi hardware identifier is printed on the ECU label. It is independent
of the Nissan `23710-` part number and of the flash content, and PCMFlash
module 18 does not report it, so it is recorded only where a label or a listing
for the exact part number carries it.

| ROM | Hitachi hardware | Lot | Identifier source |
| --- | --- | --- | --- |
| JK00A | `MEC100-120 C1` | 7515 | ECU label, owned hardware |
| JK00C | `MEC100-120 C1` | 6Z03 | ECU label, owned hardware |
| JK03A | `MEC100-190` | not recorded | dismantler listing for the exact part number |
| JK03B | `MEC100-191 A1` | 7911 | ECU label, owned hardware |
| 1ME3B | `MEC108-280 D1` | 0705 | ECU label, owned hardware |
| JK00D | not recorded | | owned hardware; the label is not transcribed |
| JK08A | not recorded | | owned hardware; the label is not transcribed |
| 1ND0A | not recorded | | forum package carries no label |
| 1ND3B | not recorded | | forum package carries no label |
| JK78C | not recorded | | catalog identification carries no label |

The identifier does not determine flash content in either direction. JK00A and
JK00C carry the same `MEC100-120 C1` hardware, hold different software
identifiers, and are not an exact-code pair; JK00A and JK03B carry different
hardware and share exact executable ranges. Family classification is
established by the byte measurements in `homology.toml` and `homology.csv`.

Two family-to-MCU bindings are local facts: the `MEC100` images carry
`SH705822N` and the `MEC108` image carries `SH705927N`.

The hardware family tracks the Nissan part-number block rather than the chassis
or the engine. Catalog entries hold one family per block:

| Part-number block | Hitachi family | Catalog application |
| --- | --- | --- |
| `JK6x` | `MEC100-0xx`, `MEC100-1xx` | 2007 Infiniti G35 3.5L |
| `JK0x` | `MEC100-1xx` | JDM V36 Skyline, VQ25HR and VQ35HR |
| `JK7x` | `MEC105-0xx` | 2008 Infiniti G37 3.7L |
| `JJ5x`, `JU6x`, `JU7x` | `MEC107-2xx`, `MEC107-5xx` | 2009 Infiniti G37 3.7L |
| `1ND` | `MEC107-7xx` | 2009 Infiniti G37 3.7L |
| `1NJ` | `MEC109-6xx` | 2010 Infiniti G37 3.7L |
| `1ME` | `MEC108-2xx` | Fuga Y51, VQ37VHR |

A chassis-and-engine match constrains nothing on its own, because one chassis
crosses families with the model year. The G37 3.7L moves from `MEC105` in 2008
to `MEC107` in 2009 and `MEC109` in 2010, and a JDM CKV36 370GT with VQ37VHR is
published at `MEC105-180 D1`.

The five images without a recorded identifier therefore sit in a family band
read from their part-number block: JK08A and JK00D in `MEC100-1xx`, JK78C in
`MEC105-0xx`, and the `1ND` pair in `MEC107-7xx`. Nine catalog entries from
`23710-1ND4C` through `23710-1ND8B` hold `MEC107-700 D1`, `MEC107-720 D1`, or
`MEC107-740 D1`, which places the family but not the suffix. No public record
pairs the exact part numbers `23710-1ND0A`, `23710-1ND3B`, `23710-JK78C`,
`23710-JK08A`, or `23710-JK00D` with a hardware number, so no exact assignment
is made. The JK00D and JK08A labels are readable on the owned hardware and
would settle two of the five without any external source.

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
- JK03A / MEC100-190 (exact part, DBA-V36 2007/2, VQ25-HRTM, 5AT RE5R05A, FR): https://autoparts.beforward.jp/detail/Computers---Sensors/Computers-Engine---ECU/PA33205361/
- MEC100-191 (V36 2.5): https://www.ebay.com/itm/116037193818
- MEC107 published as an SH7059 design: https://ecu.design/ecu-pinout/pinout-hitachi-sh7059-mec107-nissan/
- MEC100 published as an SH7058 design: https://ecu.design/ecu-pinout/pinout-hitachi-sh7058-mec100-nissan/
- MEC105-0xx = 2008 Infiniti G37 3.7L hardware: https://mintt.com/23710-jk70c-2008-infiniti-g37-3-7l-pcm-engine-computer-ecm-ecu-programmed-plug-play-mec105-012-a1.html
- MEC105-180 D1 (JDM CKV36 370GT, VQ37VHR, AT): https://www.ebay.com/itm/274957220047
- 1ND block = MEC107-7xx (23710-1ND7A, 2009 Infiniti G37): https://www.fs1inc.com/23710-1nd7a-2009-infiniti-g37-3-7l-pcm-engine-computer-ecm-ecu-programmed-plug-play.html
- 1ND block, MEC107-700 D1 variant (23710-1ND4C): https://mintt.com/23710-1nd4c-2009-infiniti-g37-3-7l-pcm-engine-computer-ecm-ecu-programmed-plug-play-mec107-700-d1.html
- 1ND block, MEC107-740 D1 variant (23710-1ND8A): https://mintt.com/23710-1nd8a-2009-infiniti-g37-3-7l-pcm-engine-computer-ecm-ecu-programmed-plug-play-mec107-740-d1.html
- 1NJ block = MEC109-6xx (23710-1NJ3C, 2010 Infiniti G37): https://www.fs1inc.com/23710-1nj3c-2010-infiniti-g37-3-7l-pcm-engine-computer-ecm-ecu-programmed-plug-play-mec109-650-c2.html
- MEC107-2xx block (23710-JJ50B, 2009 Infiniti G37): https://www.fs1inc.com/23710-jj50b-2009-infiniti-g37-3-7l-pcm-engine-computer-ecm-ecu-programmed-plug-play.html
- MEC108-270 C1 (Fuga KNY51, VQ37VHR, AT): https://jdmnewyork.com/products/jdm-subaru-legacy-b4-bm9-2-5l-automatic-ecu-engine-control-unit-22765ab032-ej25-copy
- JK7x = 2008 Infiniti G37 3.7L: https://www.fs1inc.com/23710-jk78a-2008-infiniti-g37-3-7l-pcm-engine-computer-ecm-ecu-programmed-plug-play.html
- 23710 = Nissan ECM part-number prefix: https://parts.nissanusa.com/parts/nissan-engine-control-module-ecm-23710zv24a
- Renesas SH7059 / SH7058S (SH-2E core, 1.5 / 1.0 MiB flash): https://www.renesas.com/en/document/mah/sh-2e-sh7059-f-ztattm-sh7058s-f-ztattm-hardware-manual
- PCMflash module list (Module 18 SH705927N / SH7059): https://scanmatik.ru/downloads/PCM_module_list.pdf
- VQ engine / VVEL: https://en.wikipedia.org/wiki/Nissan_VQ_engine

Ground truth is in the hardware. A part number and forum thread are orientation
points; disassembly provides the final cross-check.

## Homology baseline

`homology.toml` declares the current family boundaries and the exact byte ranges
that support same-address inheritance. `homology.csv` is generated by
`../tools/rom_homology.py` from every registered `*-stock.bin` image after
verifying its SHA-256. The report contains fixed-address byte and page metrics
plus a conservative address-independent code metric. The latter counts exact
64-byte windows from `0x020000` onward that occur at any even target address and
excludes low-information fill blocks.

The current separation between binary homology, definition parity, runtime
features, verification, and hardware evidence is summarized in
[`support-matrix.md`](support-matrix.md).

The baseline identifies five implementation groups:

| Group | Images | Classification | Builder and definition consequence |
|---|---|---|---|
| SH7058 `7MFKAVN86` | JK00A, JK03A, JK03B, JK08A | Exact code; differences are confined to `0x008200:0x020000` | One same-address series profile can cover all four images while reading calibration values from the selected image |
| SH7059 `1ND` | 1ND0A, 1ND3B | Exact code; 5,251 differing bytes are confined to `0x008200:0x01bdfc` | One SH7059 structural analysis and builder series can cover both images; the exact checksum layout is registered |
| SH7058 `8MFK` | JK00C, JK00D | Near code with insertions, deletions, and relocations | Share semantic identifiers, but require address maps and independently validated patch points |
| SH7058 JK78C | JK78C | Distinct code base in the current collection | Uses an independent layout, checksum model, audited allocation, target payloads, and executable gate |
| SH7059 `1ME3B` | 1ME3B | Distinct code base in the current collection | Carries a registered checksum layout, a fused interpolation registry with its census, a SHA-bound definition target established through `1ND0A` structural correspondence, and its own address profile and builder target; every address in that profile is independently recovered rather than inherited |

### Exact-code families

The `7MFKAVN86` images are byte-identical in `0x000000:0x008200` and
`0x020000:0x100000`. All 2,312 confirmed executable JK08A function ranges are
therefore exact across the family. The current JK08A checksum implementation
validates all six stored domains in every member. The four images also have the
same 15 stock Map Switching hook values, the same empty runtime allocation, the
same diagnostic pointer slots, and the same stock CAN mailbox record. The
production builder registers all four exact identities under
`sh7058_7mfkavn86`, uses JK08A as the canonical executable layout, and restores
builder-owned bytes from the selected member's stock image. No code relocation
is required within this family.

The reviewed JK08A table layer also transfers structurally within this family.
At the same addresses, JK03A has 460 of 464 table byte ranges identical to
JK08A, JK03B has 454, and JK00A has 271. All 48 reviewed DTC descriptor and
attribute pairs are identical in all four images. Generated definitions must
measure the selected ROM values rather than copy JK08A values, especially for
JK00A, but they can share the recovered accessors, geometry, semantics, and
presentation source. `defs/rom-inheritance.toml` binds all three inheritors to
the canonical source, while `defs/rom-identities.toml` supplies distinct editor
identity blocks. The generated XML/XDF files therefore expose the common
structure without embedding JK08A calibration values in another target.

The `1ND` pair is byte-identical in `0x000000:0x008200` and
`0x020000:0x180000`. All 1,909 functions in the current 1ND0A Ghidra census are
exact in 1ND3B. The registered checksum profile reproduces four SUM16 fields
and one runtime XOR+SUM domain in both images. The generated definitions and
production builder share one address profile and executable layout while
retaining independent image identities, calibration values, and stage hashes.

### Near-code family

JK00C and JK00D have only 55.4819 percent byte equality at the same offsets
because local changes shift later content. Address-independent matching finds
73.4272 percent conservative exact 64-byte code-window coverage in both
directions. The Myers comparison in `radiff2 6.1.6` reports similarity `0.979`
and edit distance `43,104`, confirming a common code lineage with relatively
small edits rather than independent implementations.

Direct reuse of JK08A or JK00D addresses is unsafe. JK00C and JK00D match none
of the 15 current JK08A Map Switching stock hooks, and their checksum fields
and application state are relocated. Reviewed homologs show that the
higher-level algorithms survive at target-specific addresses.

`../patches/rom-address-profiles.toml` binds both exact stock images to the
audited ROM range `0x000de800:0x000e2700`, the audited RAM range
`0xffff6000:0xffff6600`, every current runtime hook, the split exhaust-CVTC
banks, Rolling Launch diagnostics, HCAN mailbox ownership, and every schema-2
telemetry source. The production builder consumes these profiles together with
target-specific GNU SH-2E payload locks. The executable gate binds every
emitted target instruction to the corresponding stock bytes and exercises the
relocated Map Switching, Rolling Launch, and CAN telemetry paths.

### Significantly different groups

The conservative exact 64-byte window overlap is about 15 percent between the
`7MFKAVN86` and `8MFK` families, about 8 percent between `8MFK` and JK78C,
about 1.3 percent between JK78C and the SH7059 `1ND` family, and about 19
percent between `1ME3B` and `1ND`. These values are not semantic similarity
scores. They establish that same-address or raw byte inheritance is
inappropriate.

`1ME3B` shares the SH7059 class, the 1.5 MiB flash, and the boot and vector
blocks with the `1ND` pair; below `0x008200` it differs from 1ND0A at only 14
byte positions, namely a four-byte value at `0x005fe0`, the stored SUM16 fields
at `0x005ffe` and `0x006efe`, and the software identifier at `0x006f09`. Its
executable region is a separate layout.
`radiff2 6.1.6` reports Myers similarity `0.815` and edit distance `581,292`
for `1ME3B` against `1ND0A`. The same metric reads `0.790` for the declared
divergent JK08A and JK00D pair and `0.979` for the near-code JK00C and JK00D
pair, so `1ME3B` sits in the divergent band. Two structures still carry across
at relocated addresses: the four `1ND` SUM16 checksum domains reproduce at
their `1ND` field addresses while the application XOR and SUM fields move from
`0x009610` and `0x009618` to `0x0096f4` and `0x0096fc`, and the diagnostic
descriptor region is byte-identical across 1,936 bytes at a constant `+0x164`
relocation, placing `1ND0A` `0x01c558:0x01cce8` at `0x01c6bc:0x01ce4c`.

JK78C and the `1ND` family form a useful VQ37VHR cross-generation homolog pair.
Reviewed shared algorithms establish semantic correspondence, while each
family retains its own flash size, addresses, checksum scheme, free-space
audit, stock hooks, and payload locks. No raw address or patch eligibility is
inherited across the pair.

Historical Developer Immobilizer validation, map-switching, and Rolling Launch
artifacts are not retained under `rom-images/`. Their byte contracts, hashes,
and hardware evidence remain documented under `../patches/`.
