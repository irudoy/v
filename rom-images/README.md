# ROM images - dump manifest

Ground-truth ROM dumps for the **VQ HR ECU** project: images from the RomRaider
forum and owned reads from physical ECUs.

Original binaries (`*.bin`) are versioned in Git; duplicate archives are not
stored. `roms.csv` owns the image inventory and identities; this document
describes provenance, interpretation and the registry workflow. Dumps are
identified by `sha256`.

A previously unmodelled image enters the project through
[`new-rom-intake.md`](new-rom-intake.md), which classifies it, selects a
scenario branch, and states what that branch inherits and must recover.

## Layout and naming

The top level contains only ECM part-number directories in `23710-XXXXX` format,
the shared manifest, and the machine-readable registry:

```text
rom-images/
  23710-XXXXX/
    README.md                 # source, provenance, and comparison evidence
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
`roms.csv`. Every part-number directory carries a README holding the read or
import record, the labels and listings behind its application, and the
comparison evidence specific to that image.

Generated JK08A tuning images are not stored under `rom-images`. Concrete tune
profiles, per-image build recipes, generated ROMs, checksum sidecars, active
tune identities, and logs remain local artifacts outside the repository. The
repository records only universal patch, composition, definition, and
verification contracts for derived JK08A images.

The layout, names, registries, generated homology report, and MD5 sidecars are
checked with:

```bash
uv run python tools/rom_homology.py --check
uv run pytest -q tools/tests/test_rom_images_layout.py
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

[`roms.csv`](roms.csv) supplies paths, hashes, sizes and application metadata.
The README beside each image records the evidence behind its provenance,
physical labels and application assignment.

The `23710` prefix is the Nissan/Infiniti part-number prefix for an ECM, according
to the parts.nissanusa catalog.

Flash sizes (1.0 / 1.5 MiB) and the **SH-2E** core are confirmed by the
Renesas datasheet. The specific on-board chip model (SH7058 vs SH7059) and CAN
bus are inferred from flash size and the Hitachi HR CAN ECU family; final
verification requires disassembly or chip markings. As a cross-check, PCMflash
Module 18 covers `EFI SH705927N (Hitachi SH7059/1.5MB)`, which matches the `1ND`
dump class. Its USDM listing includes
`EFI SH70582xN (Hitachi SH7058/1MB)`, which matches the `JK78C` class. See
`../refs/pcmflash-module-list.md`.

### SHA-256 identification

`roms.csv` is the registry, with one row per dump file: path, ROM graph label,
SHA-256, and a one-line read or import record. It is machine-readable. Stage 4
of the map pipeline resolves the image by label and verifies its hash before
reading values (`../tools/mapkit/rom.py`), so dump identification is a run
precondition rather than human-only reference data. The label is empty for an
image that is not represented in the graph, such as an EEPROM. The note stays a
single line; the evidence behind it belongs in the directory README. Derived
images are excluded from the stock-source registry; immutable hardware-tested
identities are recorded in `../patches/hardware-results.toml`.

### Identity strings

Every image carries two fixed identity blocks. The first begins at `0x006F00`
with the literal `12345` and the second at `0x007000` with `000000`; each holds
an eleven-byte software string nine bytes in. The calibration string is at
`0x008204`, and the MCU type string is at `0x0050C6` for SH7058 and `0x0050D2`
for SH7059.

Image bytes own the calibration and software strings. `read_identity()` in
`../tools/rom_homology.py` reads those fields; `homology.toml` owns the family
identifiers, and `validate_software_ids()` checks them against every member
image. Editor identity metadata is owned by `../defs/rom-identities.toml`.

The owned PCMFlash identification records report the second block when the
image populates it and the first otherwise. Their per-image READMEs identify
the observed record. A shared first block does not establish exact-code
inheritance; the image-byte comparisons do. JK78C has no physical read of its
own, so its reported identifier remains an inference and the editor registry
keeps its `caseid` unknown.

### Provenance and confidence

Read method, identification records, labels, and the public sources behind each
application are in the directory README beside the dump. This table carries the
source kind and the confidence of the vehicle and engine application alone.

| ROM | Source | Application evidence | Confidence |
| --- | --- | --- | --- |
| JK08A | owned target ECU read | the vehicle the ECU is installed in | high |
| JK00A | owned ECU read | public exact-part listings | marketplace-grade |
| JK00C | owned ECU pre-write read | `MEC100-120 C1` hardware-family records | marketplace-grade |
| JK00D | owned bench ECU read | none; donor vehicle and market unknown | not established |
| JK03A | forum package | source post and a dismantler listing for the exact part number | high |
| JK03B | owned ECU pre-write read | exact-part and hardware-family records | high |
| 1ME3B | owned bench ECU read | the vehicle the ECU was removed from | high |
| 1ND0A | forum package | source thread | forum-grade |
| 1ND3B | forum package | source thread | forum-grade |
| JK78C | part-number catalogs | `23710-JK7xC` series and the `23710-JK78B` replacement list | catalog-grade |

A grade qualifies the application only. The calibration string, the MCU type
string, and the flash size are read from the image itself for every entry and
are independent of the sources above, as is family membership, which rests on
the byte measurements in `homology.toml` and `homology.csv`. No external EEPROM
was read for any image.

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

The baseline identifies the registered implementation groups, tabulated with their
address policy and builder consequence in
[`support-matrix.md`](support-matrix.md#family-baseline). The measurements
below explain the family interpretation; current comparison metrics belong to
`homology.csv`, generated from the image bytes and `homology.toml`.

### Exact-code families

The `7MFKAVN86` images are byte-identical in `0x000000:0x008200` and
`0x020000:0x100000`. The reviewed executable ranges are therefore exact across
the family. The selected checksum layout validates its stored domains in every
member. The images also have the same stock Map Switching hook values, empty
runtime allocation, diagnostic pointer slots, and stock CAN mailbox record. The
production builder resolves the registered exact identities under
`sh7058_7mfkavn86`, uses JK08A as the canonical executable layout, and restores
builder-owned bytes from the selected member's stock image. No code relocation
is required within this family.

The reviewed JK08A table layer also transfers structurally within this family.
Table-byte equality is measured from the selected images; the definition and
DTC projections own the reviewed map and descriptor inventories. Generated
definitions must
measure the selected ROM values rather than copy JK08A values, especially for
JK00A, but they can share the recovered accessors, geometry, semantics, and
presentation source. `defs/rom-inheritance.toml` binds the registered inheritors to
the canonical source, while `defs/rom-identities.toml` supplies distinct editor
identity blocks. The generated XML/XDF files therefore expose the common
structure without embedding JK08A calibration values in another target.

The `1ND` pair is byte-identical in `0x000000:0x008200` and
`0x020000:0x180000`. The executable layout is shared; current function totals
belong to the layout's structural export. The registered checksum profile owns
the SUM16 fields and runtime XOR/SUM domain in both images. The generated
definitions and
production builder share one address profile and executable layout while
retaining independent image identities, calibration values, and stage hashes.

### Near-code family

`homology.toml` classifies JK00C and JK00D as a near-code family. Local changes
shift later content, so same-offset equality and address-independent window
coverage are separate metrics in `homology.csv`; neither metric establishes
semantic inheritance.

Direct reuse of JK08A or JK00D addresses is unsafe. JK00C and JK00D match none
of the canonical JK08A Map Switching stock hooks, and their checksum fields
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

`homology.csv` owns the measured window overlap between the declared divergent
groups. Window overlap is not a semantic similarity score and does not permit
same-address or raw-byte inheritance.

`1ME3B` shares the SH7059 class, the 1.5 MiB flash, and the boot and vector
blocks with the `1ND` pair; below `0x008200` its differences include a
four-byte value at `0x005fe0`, the stored SUM16 fields
at `0x005ffe` and `0x006efe`, and the software identifier at `0x006f09`. Its
executable region is a separate layout.
The declared divergent relationship is owned by `homology.toml`. Structures
still carry across at relocated addresses: the `1ND` SUM16 checksum domains
reproduce at
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
