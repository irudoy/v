# refs/vendor - vendor catalogs and anchor facts

Machine-readable dictionaries and facts from tuning-software vendors for the **HR**
architecture, used as evidence by the map pipeline (`tools/map-analysis-pipeline.md`). Three
independent dictionaries describe the same hardware. They triangulate one another rather
than duplicate the same information:

| Dictionary | Source | Contribution | Storage |
|---|---|---|---|
| **ProECU** (EcuTek) | `refs/ecutek/` | factory map-name tree, documented defaults, VQ37VHR mechanics | this directory |
| **UpRev** | `refs/uprev/` | axes in ROM terms (BFS), calculation chain, DTC codes | this directory |
| **A2L** (RomRaider / Pytrex) | `defs/` | geometry, element type, scaling, axis semantics, descriptions | graph, `tools/memgraph/load_a2l.py` |

None of the three is complete. A2L provides geometry, scale, and axis semantics, resolving
gaps explicitly acknowledged by vendors, such as the rev-limiter map axis and knock-threshold
scale. Vendor documents provide mechanics, map-selection conditions, and **documented
defaults**, which are numeric values that can be searched directly in a dump. Agreement among
three independent sources about one subject provides stronger confidence than any source alone.

## Contents

| File | Contents | Entries |
|---|---|---|
| `proecu-maps.csv` | ProECU name catalog, transcribed verbatim from map-tree screenshots | 295 |
| `uprev-maps.csv` | UpRev catalog: names, axes, and outputs extracted from prose | 76 |
| `catalog.csv` | Combined catalog with derived `origin` and `concept` columns | 371 |
| `facts.csv` | Anchor facts: constants, units, axes, mechanics, and vendor gaps | 138 |

`catalog.csv` is generated from the first two files. Edit the source transcriptions rather
than the generated catalog, then rebuild it with `make vendor-catalog`.

## Method

**ProECU.** The "Map List" sections in both EcuTek documents are screenshots of a map tree,
so neither grep nor a text-reading agent can access the catalog. Entries were transcribed
manually and verbatim. Source capitalization, punctuation, and typos are preserved, including
ProECU's uncertainty markers (`Idle Target #1a - ??`, `Possible Idle rel #1`,
`Sensor Multiplier Unk`, `Torque Filtering Unknown Hi`) and `(unused)` labels. The screenshots
show names only; they contain no axes, geometry, or scaling.

**UpRev.** The document is continuous prose without a map tree, but each section names axes
and output meaning. Names, axes, and outputs were extracted from the text and represented in
the same record form as ProECU.

**Combination.** `catalog.csv` is the union of both catalogs with normalized `origin` and
`concept` fields. No entry is discarded or renamed. Names remain verbatim, and all analysis
resides in separate columns.

## The origin column

The `factory` / `patch` / `unknown` classification distinguishes factory content from
vendor-injected patches. Only `origin=factory` entries (**243 of 371**) can annotate a stock
ROM. A `patch` entry describes foreign code and is retained for completeness and analysis of
patched ROMs.

| Condition | origin |
|---|---|
| ProECU document `racerom-supplement` | `patch` |
| ProECU tree branch `EcuTek RaceROM Maps//...` | `patch` |
| Remaining ProECU entries | `factory` |
| UpRev ARC and Simplified Timing sections, NATS, Single Bank O2 Hack | `patch` |
| Remaining UpRev entries | `factory` |
| UpRev Cruise Enabled and MT Swap switches | `unknown` |

The `vendor` column identifies the patch owner: `ecutek` means RaceROM and `uprev` means ARC.

**Group labels are unreliable and are not part of the rule.** `Rev Limit Per Gear Mode1-4`
are RaceROM maps placed under `Limiters` beside factory `Rev Limit - Fuel Cut` maps. Origin is
determined by the source document, explicit tree root, and the ProECU UI origin column
(`RaceROM`, covering 37 entries), not by the group label.

## The concept column

`concept` is the dictionary join key: records sharing one value describe the same entity. It
is assigned only where the relationship is justified: **170 of 371 entries**, with **27
concepts covered by both dictionaries**. An empty value means "link not established", not
"no link exists".

The A2L catalog uses the same key (`:A2LEntry.concept`, **45 of 188 entries**; annotation is
implemented in `tools/memgraph/load_a2l.py`). This file defines the vocabulary: an A2L concept
absent from `catalog.csv` joins to nothing, so the A2L loader rejects unknown values. All three
dictionaries converge on **23 concepts**, 17 of them covered by both vendors.

Concept granularity is a calibration family rather than one table. `vvel-duration` covers
seven ProECU records (Cold, Main, Overrun, WOT, and others), while `idle-ignition` covers
nine. Variants of one function (Cold/High Detonation/High Octane and Trustful check copies)
share the same value.

The motivating example is `bfs-multiplier`: ProECU calls it
`BFS Multiplier (K-Factor)`, UpRev calls it `K - Fuel Multiplier`, and A2L calls it `K-Value`
with unit `ms/kg` and description "Air volume pulse width conversion constant". The unit
confirms the link: UpRev's `MAF * K = BFS` formula turns mass multiplied by ms/kg into pulse
width in milliseconds.

A2L `MAF Factor` (`kg/hr`) is a **different** quantity corresponding to ProECU
`MAF Sensor Scale (% to g/s) for Load` (`maf-gps-scalar`). A2L distinguishes the two directly:
it states that the factor can be used instead of adjusting K and is Nissan's factory method
for MAF scaling. This matches EcuTek's advice to leave K unchanged and adjust the second value
for larger MAF housings.

Exact JK08A code resolves both scalars. `ROM16[0x9284] = 26806` is K-Value, while
`ROM8[0x8A27] = 109` is MAF Factor. `FUN_0003B75C` multiplies both with the combined
MAF aggregate before dividing by `ROM8[0x88FB] = 3` and engine speed. A second function,
`FUN_00082604`, reads the same three scalars and again uses MAF Factor separately from K.
The adjacent literal-pool signature transfers between families: MAF Factor is
133 in 1ND0A/1ND3B, 131 in JK78C, 109 in JK03A/JK08A, and 132 in JK00D; K stays 26806
and the V6 event scalar stays 3. The A2L scale gives 0.0109 kg/hr per aggregate count in
JK08A. The physical units remain subject to hardware validation.

Names alone cannot establish a link. A2L `MAF Voltage Lower Limit` appears to match
`MAF Voltage Min Allowed`, but A2L describes its threshold as AFM power-supply fault judgment
that raises P0102. EcuTek's value places the ECM in safe/limp mode **without a DTC**. They are
different quantities, so neither link is assigned. Descriptions and geometry decide, not
string similarity.

## What the combined catalog provides

Each dictionary fills gaps in another:

- **Axes.** UpRev names the load axis by its ROM quantity, `Base Fuel Schedule`. ProECU calls
  the same axis `Engine Load (%)`, after division. The original quantity matters when matching
  a table found in a dump: the stored axis is BFS.
- **Calculation chain.** ProECU states that K multiplies Mass Airflow into Engine Load. UpRev
  separates the chain into `MAF * K = BFS`, then `Load = BFS / Calculated Load[RPM]`.
  ProECU's factory `100% Engine Load = 39.8 BFS` is the value in UpRev's `Calculated Load`
  table.
- **Axes absent from ProECU.** ProECU does not identify the `Idle Target` axis. UpRev states
  that it is coolant temperature and is static.
- **An axis unknown to a vendor.** ProECU explicitly says that the `Rev Limit` map input axis
  is unknown. A2L identifies it as `State` with `Normal` and `Reverse` points; the other axis,
  `Fuel`, contains `Cut` and `Restore`. One 2x2 map replaces two ProECU maps. This explains the
  recommendation to set all values equal: make forward and reverse identical. An accessor
  trace must still confirm the structure.
- **Duplicate sets.** ProECU shows two overrun fuel-cut map sets (`#1`, `#2`) without explaining
  the difference, noting only that testing used set #2. A2L explains that the sets belong to
  different ECU families, Bosch and JECS/Hitachi; the active set is the one matching the ECU.
- **Dead calibrations.** ProECU labels maps `(unused)`, while UpRev states that fan-control
  tables from the previous generation remain in some ECUs but are unused. A `dead` role is an
  expected stock-ROM state rather than a catalog error.
- **Check copies.** ProECU calls them `Trustful`, and UpRev uses the `(Alt)` suffix. Together
  they cover accelerator pedal, TPS, torque, throttle, and VVEL. UpRev adds the failure code:
  **P0605**. Two byte-identical ROM tables are a factory pattern, not a duplicate catalog entry.

## Dictionary disagreements

The catalog records disagreements without selecting a winner:

| Subject | ProECU | UpRev | State |
|---|---|---|---|
| Open loop | target AFR **below** 14.7 enters it | **any** target other than 14.7 enters it | unresolved |
| Enrichment-map axes | RPM x Engine Load; output adjusts target AFR | Volumetric Flow Ratio x RPM; output is a plenum-air fraction | A2L has both: `Fuel Compensation Map` (QH0 Flow Quantity x Engine Speed, "directly trim Base Fuel Schedule") matches UpRev, while the KHOT temperature pair matches ProECU enrichment. The dictionaries probably describe **different** maps, though `fuel-comp` currently groups them |
| VVEL valve lift | 25 degCam -> 0.75 mm, 70 degCam -> 11.50 mm | no exact measurements; assumes a linear relationship | ProECU is more informative |
| Number of factory ignition maps | nine: five `Mode A1 Adj`, four `Mode B1` | three: Main, High Det, Cold | A2L also has three (Cold, High Detonation, High Octane), so UpRev `Main` = A2L `High Octane`; the nine ProECU entries remain unidentified |

All three sources agree that factory ignition maps are **adjustments**, not absolute timing.
ProECU uses `Ignition MBT Adjustment`, UpRev describes a timing trim added to internally
calculated timing, and A2L uses `Degrees Adjustment (x-64)` and explicitly says that the map
value is added to or subtracted from calculated MBT advance. UpRev explains that MBT is
computed by a formula rather than stored in a base timing table. A2L names the inputs under
`Ignition Timing//MBT Calculation`: flame speed, unburned-gas density, ignition delay,
dilution, EGR, and related coefficients.

## Gaps resolved by A2L

| Gap | Source acknowledging it | A2L information |
|---|---|---|
| Fuel-cut map axis | ProECU: "The Input axis to these maps is currently unknown" | axis is **coolant temperature**, value is engine speed (`x*25`), map is 1D-16 |
| Why two fuel-cut sets exist | ProECU: "Only the #2 maps are used during our testing" | sets belong to different ECU families, `Bosch` and `JECS`; one description says "used for Bosch ECU's only" |
| Knock-threshold scale | ProECU and UpRev do not know the kHz conversion | `Knock Slice Map`, 16x6, axes RPM x **Cylinder**, scale `x*0.0015259` |
| Per-cylinder correction axis | ProECU says it may represent firing order | `Individual Cylinder Fuel Trims`, 1D-6, axis **Cylinder**; this does not prove order |
| FTST limit: 75..125% or 120% | disagreement within the EcuTek document | a calibratable pair, `Short Term Fuel Trim Limits`, 1D-2, rather than a constant |
| Oil-temperature rev limiter | named by UpRev but absent from ProECU | `KT Low Oil Temperature Fuel Cut/Restore`, unit RPM |

## Applicability boundaries

- EcuTek documents **VQ37VHR** (370Z). UpRev describes Nissan platforms more generally, so
  its facts transfer more broadly. `facts.csv` records this in `applies_to`.
- Donor `JK03A` is **VQ25HR without VVEL**. `Cam Timing//VVEL Valve Duration` does not apply,
  while `VTC Valve Advance` does. The VQ37VHR claim that VVEL adjustments complicate ignition
  does not apply to VQ25HR, supporting an expectation of simpler factory ignition logic.
- The catalog is a **lower bound** on the map set. ProECU screenshots are a UI snapshot:
  `100% Engine Load` has prose and a factory value but no Map List entry; the Misc section
  (fan, ESP, gear ratios) has no Map List; and the Accel Pedal tree shows only Normal and Snow
  although prose names four modes. A missing catalog name says nothing about whether a map
  exists in the ROM.

## Open questions

- **ProECU Custom Maps were not extracted.** The Custom Maps section in
  `racerom-supplement` contains the wrong screenshot:
  `images/image2019-8-27_13-22-24.png` shows the RaceROM Controller tree. This is a source
  defect rather than an extraction error. The file differs byte-for-byte from
  `images/image2019-8-27_13-20-43.png` (different SHA-256 and size), but the visible content
  is the same: the screenshot was retaken two minutes later and attached to the adjacent
  section.
- Two `Fuelling` rows both read `AFR Conversion Table Bank 1`; the second is probably
  `Bank 2`. Two `Torque Reduction Ramp after Shift` rows also appear. Both pairs carry `[DUP]`.
- Neither vendor expands the `ETD` suffix. The combined-catalog hypothesis is a
  high-detonation-mode variant; see `facts.csv`, `kind=hypothesis`.

## Findings from ROM dumps

`BFS Multiplier (K-Factor)` has documented default **26806** (`0x68B6`), identical on 2.5 L,
3.5 L, and 3.7 L engines. This supports an HR-architecture constant and matches both vendors'
advice not to change it. The value is identified by a homologous scalar-block signature,
`0000 5E24 A5F0 FFFF [68B6]`, across all ten registry images, once in each:

| ROM | Engine | Address |
|---|---|---|
| 1ME3B | VQ37VHR | `0x9170` |
| 1ND0A | VQ37VHR | `0x9106` |
| 1ND3B | VQ37VHR | `0x9106` |
| JK78C | - | `0x8F80` |
| JK03A | VQ25HR | `0x9284` |
| JK03B | VQ25HR | `0x9284` |
| JK08A | VQ25HR | `0x9284` |
| JK00A | VQ35HR | `0x9284` |
| JK00C | VQ35HR | `0x930E` |
| JK00D | VQ35HR | `0x931C` |

The value alone is insufficient. `0x68B6` is the only word-aligned occurrence in four images,
but appears **twice** in the exact-code JK03A/JK08A pair. The second occurrence at `0x162FA`
lacks the signature and lies in a data region covered by none of the 446 catalog maps or 229
axes, with no functions present. It is a table cell that happens to share the value, not a
second K-Factor. The block signature, rather than the scalar alone, is the anchor.

Confidence is `candidate`: a signature match rather than a code trace. Promotion to `code`
requires tracing the MAF-to-load multiplication and remains in Phase 3 of the roadmap. UpRev
sets a lower range bound of 10,000; the default is about 2.7 times higher.

The `Rev Limit - Fuel Cut Maximum` catalog entry is not assigned to JK03A/JK08A
`0x8FDC`/`0x8FDE`. Exact code identifies that pair through `FUN_00047a56` as
accelerator-pedal high-state hysteresis fed by A/D channels AN10 and AN17. The working
engine-speed fuel-cut table is independently localized at `0x934E` through
`FUN_0004f282`. Nearby documented scalars remain search candidates only when their own
code paths support the identity.
