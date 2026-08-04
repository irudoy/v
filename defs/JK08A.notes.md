
# JK08A - definition annotation log

RE log for working definitions `JK08A.xml` and `JK08A.xdf` for the project's own dump
`rom-images/23710-JK08A/1JK08A-20260726-stock.bin`
(Nissan Skyline V36 250GT, VQ25HR, 23710-JK08A, SH7058 / 1 MiB, JDM).
SHA-256 `ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23`.

Forum-sourced `JK03A` remains a separate donor ROM. The images differ at 121 byte
positions in calibration/config, but none falls within the 2312 functions in the Ghidra
export. All 16 `rom_const` values from structured evidence match. Of 450 maps, only four
currently unnamed candidate curves differ: `0x15360`, `0x15380`, `0x19090`, and
`0x190b0`; all 230 axes match. `JK08A.*` is the sole live source of structural and
semantic claims for the exact-code pair. `defs/rom-inheritance.toml` projects them onto
a separate JK03A layer, while map ranges and hashes are measured from each ROM's own
dump during every ingest. There is no live `defs/JK03A.*` set.

Commit-qualified paths such as `ba85fba:defs/JK03A.maps.csv` below refer to immutable
historical inputs of completed workflows. They preserve the original donor name as
provenance and are not paths in the current `JK08A` layer.


## Status

- Identification: operational. The dump identifies itself with string `JK08A` at
  address `0x8205` (= the definition's `internalidaddress`) and calibration
  `1JK08A00000`. RomRaider identifies the ROM as JK08A from the romid skeleton.
- Canonical headless export `export-JK08A-exact` comes from the separate Ghidra program
  imported from `1JK08A-20260726-stock.bin` (`SuperH:BE:32:SH-2A`, base 0x0, 1 MiB).
  It contains 2315 functions and 63182 xrefs. Every one of the 2312 JK03A donor entries
  is present, while exact auto-analysis retains three additional entries. Code bytes
  match JK03A over `0x000000..0x0081ff` and `0x020000..0x0fffff`; all 13 resolver
  censuses have identical row sets. Legacy `export-JK08A` remains a comparison artifact
  and is not the default ingest source.
- Annotated at `code` confidence: three 16x16 uint8 maps
  `0xB61A/0xB71A/0xB81A` through interpolator `0x26320` are sentinel thresholds, not
  ignition maps. `0xB61A` and `0xB71A` block the branch with value `0x80`; range
  `0xB81A` is 33..63, so its comparison with `0x80` is invariantly true and the map
  has `role=dead`. Axis `0x11ECE` of accessor `0x4BBEE` is indexed by `ffff11bc` in
  internal-count scale `x*4`; code does not establish the physical name RPM.
- Annotated [CONFIRMED]: kernel `0x26944` plus dimension-specific wrappers
  (`0x26320`=16x16, `0x26084`=4x4, `0x264a0`=1D-16).
  A 4x4 family `0xA49A`/`0xAB6A` was found (accessors `0x52f00`/`0x54ee0`, axes
  `0x11D00`/`0x11B67`, interp `0x26084`) along with 1D curve `0x129D2`
  (`0xb997c`, axis `0x11B7B`, interp `0x264a0`). Geometry is confirmed; semantics
  remain TBD.
- Table-access library [CONFIRMED]: calibration-table reads go through region
  `0x26000..0x26E00` with 39 entry points: 35 lead to tables and 4 to arithmetic and
  RAM operations. Enumeration of region entries is the catalog completeness boundary
  and its only verifiable boundary: it scans every aligned BE word in ROM whose value
  lies inside the region. See "Table-access library".
- Two access models [CONFIRMED]: explicit-axis uses breakpoint arrays through pointers
  in `r5`/`r6`, with 24 wrappers and a separate search for each axis. An axis element
  defines the clamp for its call (`(points-1) * size`), not the kernel: 2 of the 22
  two-axis wrappers use different values for their axes. See "An axis element defines
  the clamp for its search". implicit-axis has no axis array and uses N points at a
  uniform step over the raw input, implemented by a bank of 10 primitives
  (`0x26358..0x2642C` and `0x266A0`).
- Layer measured from the image [CONFIRMED]: values of all 450 maps and 230 axes are
  read from each ROM's registered image by the same run that builds the layer (Stage 4,
  `tools/mapkit`). JK08A uses `1JK08A-20260726-stock.bin`. Axes carry their points and
  monotonicity; maps carry content range and hash. Two signals remain open: one axis is
  not read by reverse linear search (`0x119B2`), and 18 maps contain only `0xFF`.
- Element encoding [CONFIRMED]: a 1D map's input reads the element, while for a 2D map
  the finisher reads it; all five 2D finishers read elements as unsigned.
  `storagetype` is known for all 450 maps in the graph. Three byte-oriented 2D
  finishers handle bit7 differently: `0x26770` treats it as part of the value,
  `0x267CC` treats it as a pass-through flag over a 7-bit value, and `0x268A4`
  saturates it (values 0..127). See "2D map element encoding".
- The catalog contains **450 maps**: the resolver obtains 436 through 34 entries
  (248 explicit-axis and 188 implicit-axis), while the manual layer declares 14 across
  five families: four comparator, five direct-row-major, two implicit-2d, two
  direct-scalar, and one direct-indexed map. No map belongs to more than one family; the
  loader verifies this.
- Map progress is tracked by ledger `JK08A.maps.csv`, a projection of the catalog from
  the graph (`tools/maps/build_tracker.py`): one row per map with family, entry, kernel,
  shape, element, axes, accessors, confidence, role, and semantics. It is not edited
  directly: entry geometry lives in `JK08A.interp.csv`, map findings in
  `JK08A.findings.csv`, axis findings in `JK08A.axes.csv`, and `load_maps.py` loads
  them into the graph. Open work consists of rows at `candidate` confidence with empty
  semantics; the script prints the counters, so this log does not duplicate them.
- Definitions `JK08A.xml` and `JK08A.xdf` are graph projections from
  `tools/mapkit/emit_def.py` plus presentation layer `JK08A.overrides.toml`: names,
  visibility, categories, ordering, and editor steps. The working definition is an
  explicit allowlist of 18 canonical maps and three masked ignition views.
  Non-emitted research maps remain in the graph and ledger. Calibration
  axes are embedded in their tables rather than emitted as separate editable views.
  Categories use the functional UpRev/EcuTek organization and do not encode
  confidence. A map below `code` is marked `[candidate]` in the generated evidence
  comment, while a scale below `code` receives suffix `[cand]` in its units; address
  and multiplier are separate claims. Manual XML or XDF edits do not survive
  regeneration.
- Annotated at `code` confidence: `0xA29A` is a Fuel Compensation Map. Its unsigned
  byte is used in fuel calculation as a multiplicative correction; A2L defines scale
  `x*0.78125%` with neutral raw 128 = 100%. `0xB33A` is a centered raw control table:
  when `ffff2466.bit6=1`, code calculates
  `clamp_u8(this - map_0xAB4A + 128)`, otherwise it passes the value directly to
  `ffff1c5d`. Its tuner-facing gasoline-AFR projection is `1881.6/x` at `candidate`
  confidence from the HR A2L and vendor fuel-target descriptions.
- Maps `0x991A`/`0x9A1A`/`0x9B1A` are Cold, High Octane, and High Detonation Ignition
  Timing Maps. Code selects the mode, separates bit7 as the knock window, and uses the
  low 7 bits as a signed-offset timing correction. Shared axes `0x11ECE`/`0x11EBE`
  have user scales RPM `x*50` and Cylinder Filling `x*0.78125%` at `candidate`
  confidence from A2L homology. RomRaider orientation: X Axis=filling/columns,
  Y Axis=speed/rows. The definition exposes the low 7 timing bits and bit7 Knock
  Window as separate masked views over the same ROM region.
- Annotated [CONFIRMED]: 8x8 pair `0xAB0A`/`0xB23A` through accessor `0xBEFB0`.
  `0xAB0A` supplies an additive raw correction to the target of an aperiodic filter;
  `0xB23A` supplies new-sample fraction `x/65536`. Both remain research-only and are
  hidden from the working definition. Catalog names "Transient Fuel Corr" remain
  [CANDIDATE]; the physical nature of the inputs and filtered quantity is unknown.
- Annotated [CONFIRMED]: scalar `0x942C` is the calibrated upper rotational-speed
  threshold in a throttle-control limiter path. `0xFFFF` disables the branch;
  otherwise `FUN_0007584E` tracks current speed and writes one input of the signed
  minimum arbiter in `FUN_00071508`, whose result enters controller calculation
  `FUN_000702C6`. The public HR label `Throttle Rev Limiter` and scale `x*0.78125 RPM`
  remain [CANDIDATE] catalog/homology claims. The stock value is 7500 RPM.
- Annotated [CONFIRMED PATH]: `0x934E` is the active 2x2 engine-speed fuel-cut
  table. `FUN_0004F282` selects one activation/release pair, maintains
  `0xFFFF2497.bit2`, and returns that state directly to aggregate six-channel
  fuel-output inhibit builder `FUN_0004ED88`. The public HR A2L layout gives
  Normal/Reverse columns, Cut/Restore rows, and candidate scale `x*12.5 RPM`.
  Stock cells decode to 7650/7450 RPM for Normal and 7450/4600 RPM for Reverse.
- Annotated [CONFIRMED]: `0x8FDC`/`0x8FDE` is accelerator-pedal high-state
  hysteresis, not an engine-speed limiter. Scheduler `FUN_00020DFE` copies current
  state `0xFFFF246A.bit7` to previous-cycle state `0xFFFF246D.bit7`. The compared
  input is produced from A/D channels AN10 and AN17. Exact DID `0x120D`/`0x120E`
  bindings and P2122/P2123/P2127/P2128 monitor paths identify the paired
  accelerator-pedal sensors. The raw activation/release thresholds are 610/528.
- Annotated [CONFIRMED]: `FUN_0005185c` performs six calculation lookups through
  `0x26370`. `0x121FE` is a composite-calculation base curve, not an RPM threshold:
  its result is multiplied by a centered factor from `0x121AE`, normalized by 8192,
  saturated to 255, and written to `ffff1531` before a second three-factor product
  forms `ffff1532`.
- Annotated [CONFIRMED]: `FUN_0004F324` implements the stationary rev limiter with
  1800/1500 RPM fuel-cut/restore hysteresis at `0x85D9`/`0x85DA`. Exact firmware
  traces its required zero-speed input from CAN frame `0x280` through
  `ffff113c`, `ffff115e`, `ffff118e`, and snapshot `ffff110e`. See
  "Stationary rev limiter and fuel-output inhibit path".
- Annotated [CONFIRMED]: a calibration byte can disable a table-read branch.
  `FUN_00051700` selects a table set by `byte[0x8D92] bit3`; at `0x7A`, tables
  `0x12206`/`0x121F6` are not read. A code reference to a table does not mean the table
  is live; the graph assigns `role=dead` to such bases. See "A branch can be disabled
  by calibration".
- Annotated [CONFIRMED]: K2Y decel timing. Timing calculation `0x82c8a` addresses no
  decel/cut flag base, so it has no decel-gated advance branch; `mTKADVA` is not
  represented by any explicit-axis map. The same calculation uses `0x26370`
  (slot `0x838bc`), so decel advance through implicit-axis maps is not excluded.
- MAF transfer curves: `0x14274` is the 64-point uint16 bank-1 curve and
  `0x141F4` is the bank-2 curve. Exact code traces SH7058 AN4/AN15 through DID
  `0x1204`/`0x1205`, both curves, combined MAF DID `0x1209`, and Base Fuel
  Schedule DID `0x1208`. The voltage and mass-flow engineering conversions remain
  hardware-validation targets. Injector latency, speed limiter, and the remainder
  of the `0x12xxx` cluster are not annotated.


## Exact JK08A MAF channels, transfer curves, and contribution trace

The stock image establishes a continuous dual-bank path from the MCU A/D registers to
the factory diagnostic response and the MAF calibrations:

- `FUN_00028098` reads SH7058 `ADDR4` (`0xFFFFF808`) and `ADDR15`
  (`0xFFFFF826`), shifts each aligned result right by six, and writes ten-bit samples
  `ffff1d62` and `ffff1d64`. The hardware manual maps these registers to AN4 at MCU
  pin 90/H18 and AN15 at MCU pin 104/L20.
- `FUN_0003C408` scales the two samples through shared Q1.15 coefficient
  `ffff4970`, writes `ffff101c`/`ffff101e`, and adds one for full-scale raw sample
  `0x03ff`. `FUN_00067188` constrains the coefficient to `0x7900..0x8700` and
  restores stock `ROM16[0x92BE] = 0x8000` outside that range. The normal transform
  is therefore identity except that sample 1023 is published as 1024.
- The exact service-0x22 pointer table maps DID `0x1204` at `0x228AC` to
  `ffff101c` and DID `0x1205` at `0x228B0` to `ffff101e`. Homologous diagnostic
  definitions name them MAS A/F SE-B1 and MAS A/F SE-B2. The firmware mapping is
  therefore AN4 -> bank 1 and AN15 -> bank 2.
- `FUN_0003AE8A` preprocesses these words into `ffff1e48`/`ffff1e4a`.
  `FUN_0003A904` interpolates bank-1 curve `0x14274` from the low 12 bits of
  `ffff1e48` and writes output `A` to `ffff1054`; it interpolates bank-2 curve
  `0x141F4` from `ffff1e4a` and writes output `B` to `ffff1056`.
- The implicit lookup advances one cell for 16 input counts. The independently
  cataloged static MAF axis advances by 0.08 V, consistent with the homologous
  DID conversion of 0.005 V per count. The working definitions expose
  `0.00..5.04 V` as a candidate axis; the stored output remains raw.
- `FUN_0003A982` copies the outputs to `ffff1058`/`ffff105a`.
  `FUN_0003B27E` combines both values with `ffff2368`, filters and saturates the
  sum into `ffff1df4`, subtracts stock offset `ROM16[0x93CE] = 320`, and writes
  `ffff105c`. `FUN_0003C3AC` publishes
  `ffff3852=min(65535,floor(105*ffff105c/256))`; the exact DID table maps this word
  to MASS AIRFLOW DID `0x1209` at `0x228C0`.

A whole-program p-code scan found the following complete writer boundaries:

- `FUN_00028098` is the only writer of `ffff1d62`/`ffff1d64`;
- the indexed store in `FUN_0003C408`, called only with indices 0 and 1, is the
  only writer of `ffff101c`/`ffff101e`;
- `ffff2368` has three readers and no direct or computed-address writer. Startup
  clear `FUN_00027C50` covers it within `[ffff1000,ffff261c)`. A complete Ghidra
  direct-reference audit of `DMAOR` and every byte of the four
  `SAR`/`DAR`/`DMATCR`/`CHCR` register blocks found no recovered DMA destination
  covering the word. It therefore remains zero in the recovered normal
  application-code and statically recovered DMAC configuration.
- DMAC channels 0, 1, and 3 have no statically resolved source, destination, or
  count setup in the application. Channel 2 is the only recovered complete
  setup: `FUN_0004A5AC` and interrupt
  handler `FUN_0004A6D4` select ADC2 `ADDR24` at `0xFFFFF840` or `ADDR28` at
  `0xFFFFF848`, write `DAR2=0xFFFF86CC+0x80*uint8[ffff20c0]`, set
  `DMATCR2=128`, and install `CHCR2=0x010D110D`. The manual decodes this as an
  ADC2-requested, source-reloaded, byte-size transfer with an incrementing
  destination and completion interrupt. The two destination buffers cover
  `ffff86cc..ffff874b` and `ffff874c..ffff87cb`, far outside `ffff2368`.
  `TraceRamAccesses` does not currently sign-extend the immediate-built
  peripheral addresses in this code, so its empty DMAC-window output is not
  evidence; the DMAC result rests on the direct register references and complete
  function listings.

The complete 456-byte listing of `FUN_0003B520` establishes the secondary
contribution-share use of the same transfer outputs:

- `FUN_0003A904` interpolates `0x14274` from the low 12 bits of `ffff1e48` and
  writes output `A` to `ffff1054` at `0x3A938`. It interpolates `0x141F4` from
  the low 12 bits of `ffff1e4a` and writes output `B` to `ffff1056` at `0x3A94E`.
- Sites `0x3B53C..0x3B558` calculate
  `wA=uint8(trunc0((A<<8)/(A+B)))` through signed divider `0x21BBC` and write
  the byte to `ffff3d44`.
- Sites `0x3B55A..0x3B572` calculate
  `wB=uint8(trunc0((B<<8)/(A+B)))` and write it to `ffff3d45`.
- Stock outputs of both curves are strictly positive, so `A+B` is nonzero and
  each quotient is below 256. Initializer `FUN_00059298` sets both contribution
  bytes to 128 before runtime recalculation.
- A separate piecewise conversion produces unsigned common value `T=ffff2842`.
  Sites `0x3B600..0x3B61C` write `ffff2844=(T*wA)>>8`, while
  `0x3B624..0x3B640` write `ffff2846=(T*wB)>>8`.
- The machine listing contains blocks `0x3B5D0`, `0x3B60C`, and `0x3B630` that
  the decompiler removes. Their signed-correction paths are unreachable for the
  unsigned nonnegative operands in this calculation.

The contribution branch does not feed `ffff3a76`. The latter is produced by a
separate branch in the same function from `ffff284a`/`ffff284c` through inverse pair
`0x13202`/`0x155A0`. `FUN_0003B468` writes `ffff3a76` to `ffff1e60` when
`ffff4246.bit6=0`; when the bit is 1 it writes ROM word `0x916C`.

The contribution branch does not establish the engineering unit of the transfer
output. The physical MAF identity and bank mapping instead follow from the exact
AN4/AN15 -> DID `0x1204`/`0x1205` -> curves -> DID `0x1209` chain. ECM-terminal
continuity and all engineering conversions remain hardware-validation boundaries.


## Method

No complete open definition exists for JK08A. Reference definition
`Pytrex .../G35/JK03A.xml` is an empty identifier (romid + checksum, 0 tables).
Structural donor **EV18A** (350Z HR, SH7058/1MB non-VVEL, same
`internalidaddress=0x8205`, 190 tables) supplies names, axes, and scaling through
inheritance `base="A2L"`, but its `storageaddress` values do not apply to this dump.
Verification: `Load Base Fuel @0x16A00` is all `0x8000` (padding), while
`Target Idle RPM @0x1472D` is noise. The JDM 2.5L calibration layout differs from
USDM 3.5L. Even EV15A and EV18A, both 350Z HR, place the same maps at different
addresses. Therefore, addresses are recovered from the dump itself.

Table geometry (dimensions/type/scaling/axes) matches the HR family and comes from
catalog `A2L.xml`; only addresses differ. Key maps from A2L:

- Ignition timing maps are 16x16 uint8 with scaling
  `Degrees Adjustment (x-64)`, X=Cylinder Filling and Y=Engine Speed axes
  (both dynamic uint8, 16 points). In EV18A, three consecutive maps at step `0x100`
  are Cold `0x9976`, HiOct `0x9A76`, and HiDet `0x9B76`, with shared axes
  X `0x13E9B` and Y `0x13EAB`.
- Target AFR Map is 16x16 uint8 with scaling `1881.6/x` and the same axes.
- Rev Limit (Fuel Cut) is uint16 2x2 with scaling `RPM (x*12.5)`.

Annotation tools (reproducible scratchpad):

- `a2l_geom.py` - table geometry from A2L.
- `find_maps.py` - scan for pairs of monotonic uint8 axes and triples of 16x16 blocks.
- `ptrscan.py` - scan for 32-bit BE pointers into calibration regions (table bases).
- `viz.py` - print 16x16 blocks and axes for visual identification.
- `agg_tref.py` - aggregate `FindTableRefs` by owner function to find base triples at
  step `0x100`.
- `transpose_all.py` - verify axis orientation by physical behavior of timing/AFR
  across rows and columns, 5/5 maps.


## Confirmed [CONFIRMED]


### Rotation-monitor thresholds - `0xB61A / 0xB71A / 0xB81A` (accessor FUN_00082c8a)

`FindTableRefs 9000..c000` plus aggregation by function (`agg_tref.py`) found a single
function with three bases at step `0x100`: `FUN_00082c8a` (@0x82c8a) loads
`0xB81A/0xB61A/0xB71A`. Assembly at `0x832a0` (`DumpListing`):

```
mov.l ...,r4 = 0000b81a   ; TABLE
mov.l ...,r5 = 00011b6b   ; AXIS X
mov.l ...,r6 = 00011b8b   ; AXIS Y
mov.l ...,r2 = 00026320   ; INTERP
jsr  @r2                  ; interp(table, axisX, axisY, cur_x, cur_y)
mov.b r2,@(ffff314a)      ; result in RAM
```

- Maps: three 16x16 uint8 maps share first row
  `[41,41,41,43,43,43,43,44,45,46,47,48,48,48,48,48]` and diverge below it. The
  branch selects bit 0 of register `ffff4217` (`mov.b @(0x93,gbr)`, `gbr=ffff4184`,
  `tst #1`): `0xB81A` is unconditional, with output in `ffff314a` (site `0x832be`);
  within the pair, bit clear selects `0xB61A` (`0x832e0`) and bit set selects
  `0xB71A` (`0x832fa`), both writing `ffff314b`. Store base is `ffff28f8`, with
  offsets `0x852`/`0x853`.
- Axes, each with 16 monotonic points; row/column association is in "Map axes":
  - `0x11B6B` (speed, rows): `[12,16,20,24,32,40,50,60,70,80,90,100,110,120,
    130,150]`, `x*50` => 600..7500.
  - `0x11B8B` (load, columns): `[8,16,20,24,28,32,36,40,44,48,56,64,80,96,112,
    136]`.
- Interpolator `FUN_00026320` (48 B) is a wrapper over primitives `0x26350/0x26354`.
  `0x26320` has a single caller, `0x82c8a`, so it is a local wrapper; the actual common
  interpolation code consists of primitives reachable through `PTR_FUN` slots, which
  feed the graph catalog.

**These are not ignition maps.** The annotation "Ignition Adj Map, Degrees Adjustment
(x-64), Cold/HiOct/HiDet family" came from A2L catalog geometry, a triple of 16x16 uint8
maps at step `0x100`, rather than code: P6. The consumer trace disproves it:

- **Cell 128 means "no value", not a number.** Finisher `0x268a4` loads `0x80`
  (`mov.w 0x26940`) and, for every participating cell, executes `cmp/hs 0x80; bt` to
  common exit `mov r6,r0; rts`, returning `0x80` without interpolation. Cell counts at
  128 are 136 of 256 in `b61a`, 38 in `b71a`, and none in `b81a`. This arithmetically
  disproves scale "x-64 degrees": 136 cells would mean +64 degrees over 53% of the map,
  while the kernel does not even interpolate those cells. The consumer checks the same
  sentinel: `*(char*)ffff314a != -0x80`.
- **The output does not enter the ignition path.** Exactly two functions read
  `ffff314a`/`ffff314b`: the accessor itself and consumer `FUN_00085a70`, whose register
  trace contains counters, 12-bit shift registers, and flags
  (`ffff37d8..ffff3826`, `ffff37f8`, `ffff3806`). It has no timing scheduler.
- **Consumer behavior.** Through `FUN_000224f8`, `FUN_00085a70` derives thresholds
  `ffff3100..ffff3105` and `ffff306e..ffff3070` from `ffff314a`/`ffff314b`, then compares
  their windows with metric `ffff3820`/`ffff3816` (offset-binary, `0x80` = zero).
  Matches populate per-cylinder shift registers and raise DTC flags.
- **`FUN_00086b0c` calculates the metric** and is called only from `00085a70`.
  Calculation occurs only when six 16-bit coefficients at `ffff55a2` lie between ROM
  bounds `0x9452`=32437 and `0x9454`=33096, or `0x8000 +/- 1%`. Six unity-normalized
  coefficients with a +/-1% tolerance on a six-cylinder engine correct crankshaft
  trigger-wheel nonuniformity.
- **Initializer `FUN_00082bd8`** writes `-128` (`0x80`) to every metric byte
  (`ffff3816..381b`, `ffff381c..381f`, `ffff3820..3826`), confirming encoding
  `0x80 = neutral`.
- **Channel calibration bytes** `000087c1..c6` are `60 ff 40 40 ff 60`; value `0xff`
  disables a channel (`ffff3101`, `ffff3104`).

Code establishes that the three maps are base surfaces f(speed, load), from which
`00085a70` derives thresholds for a misfire monitor; their role is `table` and sentinel
is `0x80`. The exact component/data-flow path is `00085a70 -> state consumed by 00082c8a
-> 00084cd0 -> 0007d8b8`, ending at P0300..P0306. Code does not establish the physical
input quantity or map-value multiplier. The image and graph independently preserve the same trace
(`wf_94cbe023-181`, pilot Section 8 gate).


### Rotational-irregularity component - classifier, readiness, and counters (accessor FUN_00082c8a)

The threshold trio feeds one subsystem. Coordinator `FUN_00082c8a`, detection core
`FUN_00085a70`, and local DTC reporter `FUN_00084cd0` form a code-proven misfire
monitor. The component contains 14 maps, 3 axes, and 7 flags. Its structural findings
are consolidated in `defs/JK08A.findings.csv`. Its remaining nodes are:

**Load classifier `0x1261A` / `0x1263A` / `0x12CBE` (code, threshold).** Three 1D-16
curves over axis `0x1264A` with input `ffff11ae`; their output is compared with
`ffff1024>>8`:

- `0x1261A` is the upper boundary: when `ffff1024>>8 >=` its output, it sets bit 6
  (`0x40`) of register `ffff41c3` at site `0x839a4`.
- `0x1263A` is the lower boundary: within the middle band, it sets bit 5 (`0x20`) of
  `ffff41c3`.
- Condition `ffff41c3 & 0x60 != 0` enables detector operation in `00085a70`; with both
  bits clear, the feature-collection branch does not execute.
- `0x12CBE` duplicates curve `0x1263A` in an inhibit role: it writes
  `ffff444a`/`ffff444c`/`ffff444d`, which `00085a70` reads.

**Five-level ladder `0x1265A`..`0x1268A` (code, threshold).** Four boundaries
`t0..t3` through wrapper `0x26388`, implicit 1D-16, classify `ffff1024>>8` into state
`ffff2b4b` in the closed range 0..4. The only external consumer is `00085a70`, which
uses that state as the index of ROM byte table `0x11A28` and adds the selected byte to
32-bit accumulators `ffff36e8` and `ffff36ec`. JK03A and JK08A are byte-identical at
the four maps and the five reachable table bytes. The stock thresholds are
255/254/253/252, and `ROM[0x11A28..0x11A2C] = ff ff ff ff ff`, so the state varies but
both accumulator increments remain 255 for every state. This proves the operational
selector role. Exact DID `0x1208` identifies `ffff1024` as the current Base Fuel
Schedule sample; the downstream meaning of the invariant increment table remains
unresolved.

**Counting readiness `ffff41d2.bits0/1` (code).** A whole-program p-code census of all
2,315 functions found 79 exact accesses to byte `ffff41d2` and no unresolved
candidates. Coordinator `FUN_00082c8a` is the only resolved writer that changes bits 0
or 1. Its initialization block clears both with mask `0xfc`; the normal path
recalculates bit 1 at `0x8391a` and bit 0 at `0x8397a`. Every other resolved writer
changes only bits 4, 5, or 7 and preserves the low pair.

Bit 1 is an inter-cycle validation latch. Let `F = ffff244f.bit5`. The generic code
refreshes `ffff42a8` when `F == 0`, or when `F != 0`, `ffff4184.bit6 == 1`, and
`ROM8[0x8afc].bit3 == 0`. A refresh writes `ROM8[0x8499]` when `ffff422d.bit4` is set
and the `0x12026` lookup result otherwise. Bit 1 is set only when the latch equals zero,
`F != 0`, and either `ffff4184.bit6 == 0` or `ROM8[0x8afc].bit3 == 1`.

Stock JK03A and JK08A contain `ROM8[0x8afc] = 0x28`, `ROM8[0x8499] = 0xb4`, and eight
zero cells at `0x12026`. The stock lifecycle therefore reduces to:

- startup initializer `FUN_00027ac0` clears effective longword span
  `[ffff261c,ffff4514)`, including `ffff41d2`, `ffff422d`, and `ffff42a8`;
- the conditional initializers in `FUN_0002fc24` and `FUN_00034b70` clear all three
  bytes again through effective span `[ffff1000,ffff5cf4)`;
- while `F == 0`, every normal coordinator pass refreshes `ffff42a8` to zero and
  clears bit 1;
- while `F != 0`, the latch remains zero and the normal coordinator pass sets bit 1.

`FUN_00027530` maintains five-state longword `ffff39d8`: states 2..4 set bit 5 in both
`ffff2451` and `ffff244f`, while states 0/1 clear it. Scheduler `FUN_00020dfe` also
copies `ffff2451` to `ffff244f`. An exhaustive `ffff422d` scan found 30 exact accesses
and no candidates; its seven resolved writers change only bits 0, 1, 2, 3, 5, or 6.
They preserve bit 4 after its startup clear. An exhaustive exact-address scan of
`ffff42a8` found only the two writes and one read in `FUN_00082c8a`. Therefore the
structural `0xb4` branch is not reached under the proven stock application-code
lifecycle, the latch stays zero, and the normal coordinator update makes bit 1 follow
`F`. The physical meaning of `ffff422d.bit4` remains unresolved.

Bit 0 is set exactly when all four unsigned conditions pass:

1. `ffff1071 < ROM8[0x8cff] = 150`;
2. `ffff1071 >= lookup_u8(0x12de2, min(2*ffff1070, 255))`;
3. `ffff106e >= ROM8[0x8d01] = 40`;
4. `ffff2736 >= ROM8[0x8b50] = 40`.

Scheduler `FUN_00020dfe` snapshots current raw coolant `ffff1079` to `ffff1071`.
`FUN_000394b8` and stateful selector `FUN_0003967a` form current selected pair
`ffff1076`/`ffff1078`; the scheduler snapshots it to `ffff106e`/`ffff1070`. On the
primary-pair branch, these are raw coolant `ffff1079` and normalized coolant
`ffff1077`. On the alternate branch they come from application-lifecycle zero bytes
`ffff107e`/`ffff1080`. Selector bit `ffff24be.bit6` makes the alternate branch stateful:
the first pass outside the primary condition still selects the primary pair, while
subsequent passes select the zero fallback until the primary condition clears the latch.
The physical mode represented by this selector condition remains unresolved.

Normal startup reaches `FUN_00027c50` before the main loop. Its descriptor-driven
longword loop starts at `ffff1000` and continues while the pointer is below unaligned
stop `ffff261a`, giving effective write span `[ffff1000,ffff261c)`; this contains
`ffff107e..ffff1080`. Conditional services `FUN_0002fc24` and `FUN_00034b70` use
unaligned stop `ffff5cf2`, giving effective write span `[ffff1000,ffff5cf4)` on
command/recovery paths. A whole-program
p-code scan of `ffff107e..ffff1080` resolves four reads and no writes: one read of each
selected fallback byte in `FUN_000394b8` and two reads of adjacent byte `ffff107f` in
`FUN_00038618`. The broader `ffff1000..ffff10ff` writer audit excludes the only three
indexed stores whose arithmetic could appear to approach the block: their complete
caller sets restrict the indices to 0 and 1, yielding only `ffff101c/101e`,
`ffff104c/1050`, and `ffff1058/105a`. Large function `FUN_00069374` only reads
`ffff106a+4/+7` and `ffff1094+0x30/+0x48/+0x5c`. No application runtime producer for
the fallback bytes exists in the stock image. An external or peripheral writer is not
established by static analysis.

On the primary-pair branch, normalized coolant is 0 below raw 10,
`floor(240*(raw-10)/150)` for raw 10..169, and 255 at raw 170 or above. With stock
`0x12de2 = ff ff ff 2b 2b 2b 2b 2b`, the first three temperature conditions reduce
exactly to raw coolant 43..149, or `-7 <= coolant deg C < 100` under the exact DID
0x1101 conversion `deg C = raw-50`. On the alternate branch, the selected raw snapshot
is zero and therefore fails the independent `ffff106e >= 40` P030 readiness condition.
The zero fallback is an inhibit path, not a second code-produced temperature scale.

The fourth condition uses an AN1-derived running-minimum chain rather than a direct
sensor snapshot. Cyclic sampler `FUN_000280d8` reads aligned SH7058 A/D result register
ADDR1 at `fffff802`, shifts it right by six, and writes 10-bit sample `ffff1d58` on
internal phase 1 and `ffff1d5a` on phase 3. The SH7058 hardware manual maps ADDR1 to
channel AN1 at MCU pin 87/G18. A whole-program p-code pass resolves exactly these two
direct writes and no computed-address writer candidates in `ffff1d58..ffff1d5b`.
The corresponding ECM terminal and physical signal remain unresolved. The two phases
can reflect external selection that is not visible from the common MCU input.

`FUN_0003d832` calls `FUN_0003d258` for indices 0 and 1. Bits 0 and 1 of `ffff3f3e`
admit alternate invocations, and `ffff3f44` marks the first sample of each lane. The
first admitted sample is copied to `ffff2832/ffff2834`; later samples use
`floor((3*previous + sample)/4)` with a one-count upward anti-stall correction. Under
stock configuration bytes `0x8b34 = 0x81` and `0x8b42 = 0xe0`, `FUN_0003d2dc`
converts `uint8(filtered >> 2)` through shared table `0x12dea` and writes
`ffff2838/ffff2839`. The alternate configuration branch writes fixed code 75. Table
reuse does not assign coolant identity or the coolant engineering scale to this AN1
path.

`FUN_0003d45c` is the indexed runtime writer omitted by exact-address xrefs. For each
lane it updates `ffff3f4c[index]` only when `ffff4185.bit6 == 0`,
`ffff417f.bit5 == 0`, and the corresponding `ffff3f3e` phase bit is set; the update
occurs only when the current transfer code is below the retained value. The accumulator
is therefore monotonically nonincreasing. Normal startup executes `FUN_00027ac0`,
which clears the containing range, then reaches `FUN_0002d120` through tail helper
`FUN_00027c34`, seeding `ffff3f4c/ffff3f4d` to 255. Conditional services
`FUN_0002fc24` and `FUN_00034b70` clear the accumulator to zero on their command or
recovery paths without reseeding it inside those functions.

`FUN_0003d832` copies accumulator element 0 to `ffff283c`; `FUN_0003d702` writes
`ffff283a = max(ffff283c-offset, 0)`, with offset 0 when `ffff1076 < 90` and
`abs(ffff454c-ffff1076) < 12`, and offset 15 otherwise. Scheduler `FUN_00020dfe` uses
the exact byte-copy contract of `FUN_00022558` to map `ffff283a` to `ffff2736` through
the 0x104-byte snapshot. P030 readiness requires `ffff2736 >= 40`, equivalent to
`ffff3f4c >= 40` on the zero-offset branch and `ffff3f4c >= 55` on the 15-count
branch. `FUN_0003d7b4` transiently copies exact DID 0x1106 source `ffff2837` to
`ffff283a`, but `FUN_0003d702` overwrites it in the same invocation; the final source
is not assigned intake-air-temperature semantics.

Exactly five external functions consume the low pair, and every one requires
`ffff41d2 & 3 == 3`: snapshot matcher `000847dc`, auxiliary state service `00085020`,
detection core `00085a70`, six-bucket operating-range updater `00086d2a`, and
revolution-window producer `000872d0`. `FUN_00086d2a` bins calculated-load code at 128
and RPM/25 at 64 and 160, then saturating-increments one of six counters; failure of the
low-bit gate clears all six. All other resolved readers of `ffff41d2` test only bits 4,
6, or 7.

Bit 2 remains a coordinator-local event latch. It is set at `0x83848` after bits 0/1
and additional operating gates pass, tested at `0x8444a` before incrementing
`ffff3115`, and cleared at `0x84552`. No external reader consumes bit 2 in the exhaustive
census.

**Event-count thresholds `0x1497A` / `0x14982` (code, threshold).** Two constant
1D-4 uint16 curves through wrapper `0x263bc`, with input
`min(max(ffff106f-0x20,0)<<9, 0xffff)`, contain 33 and 60:

- `0x1497A` -> `ffff2b90`, compared with counter `ffff3806[0]`, the aggregate element
  of a seven-element array whose elements [1..6] correspond to the six V6 cylinders.
- `0x14982` -> `ffff2b92`, compared with counter `ffff37da`.

**Event flag, bit 7 of `ffff4218` (code).** `00085a70` sets it when
`popcount(ffff36f4 & 0x0fff) > 2`; the low window bit is accumulated when
`ffff314a != -0x80 && ffff3102 <= ffff3820`. `00082c8a` reads it as a condition for
bit 3 of register `ffff41c6`. This links the trio to event counting through
`ffff314a` and its threshold.

**Exact P0300..P0306 reporter (code).** `FUN_00084cd0` has exactly four callers, all
inside `FUN_00082c8a` at `0x83D7C`, `0x84398`, `0x84544`, and `0x84794`. Its tail
calls common fault dispatcher `FUN_0007d8b8` with these exact descriptor indices:

| Runtime selector | Descriptor index | Record | DTC |
|---|---:|---:|---|
| `ffff4200.bit7` | `0x0A` | `0x193D8` | P0306 |
| `ffff41ff.bit0` | `0x0B` | `0x193E4` | P0305 |
| `ffff41ff.bit1` | `0x0C` | `0x193F0` | P0304 |
| `ffff41ff.bit2` | `0x0D` | `0x193FC` | P0303 |
| `ffff41ff.bit3` | `0x0E` | `0x19408` | P0302 |
| `ffff41ff.bit4` | `0x0F` | `0x19414` | P0301 |
| `ffff4200.bit6` or no individual selector | `0x10` | `0x19420` | P0300 |

Individual selectors are tested in table order from P0306 through P0301; the first
active selector wins. P0300 is selected when bit 6 forces aggregate reporting, when
operating gates suppress individual selection, or when no individual selector is
active. The reporter also tests bit 2 of the seven three-byte runtime DTC records at
`ffff5718 + 3*index + 2`.

**Reporter argument and retained groups (code).** Whole-caller data flow restricts the
argument to `0..5`; there is no other caller. The encoding is exact:

| Argument | Group (`arg >> 1`) | Retention path (`arg & 1`) | Caller outcome bit in `ffff5b2b` |
|---:|---:|---|---|
| 0 | 0 | Preserve other groups | Set bit 6 |
| 1 | 0 | Retain only group 0 | Clear bits 4..6 |
| 2 | 1 | Preserve other groups | Set bit 5 |
| 3 | 1 | Retain only group 1 | Clear bits 4..6 |
| 4 | 2 | Preserve other groups | Set bit 4 |
| 5 | 2 | Retain only group 2 | Clear bits 4..6 |

The odd path clears the two nonselected payloads and their retention markers, then
sets bit 3 of `ffff5b2c`. The even path does not clear other groups. Group 0 capture
requires `ffff41c1.bit1 == 0`; argument 0 sets that latch after capture. Groups 1 and
2 capture unconditionally. Every group contains the same operating-point payload:

| Group | RPM/12.5 word from `ffff11bc` | Calculated-load byte from `ffff413e` | Coolant byte from `ffff3fa4` | Retention marker |
|---:|---|---|---|---|
| 0 | `ffff4a70` | `ffff4a45` | `ffff4ac6` | `ffff5b2a.bit2` |
| 1 | `ffff4a72` | `ffff4a46` | `ffff4ac7` | `ffff5b2a.bit0` |
| 2 | `ffff4a74` | `ffff4a47` | `ffff4ac8` | `ffff5b2b.bit7` |

Each capture clears the corresponding auxiliary pair `ffff4a4a..4c` and
`ffff48c2..c4`; every capture also clears `ffff4a49`.

**Coolant payload producer (code).** `FUN_0002c4f8` obtains a 16-bit analog result
through `FUN_00028668(0)`, stores it at `ffff1d60`, and writes
`uint8(result >> 2)` to `ffff1186`. Lookup `00012DEA(ffff1186)` writes exact UDS DID
0x1101 response byte `ffff1079`. `FUN_0008092e` repeats the same lookup and writes
`ffff3fa4 = max(output - 10, 0)`. DID 0x1101 has `deg C = raw - 50`, so snapshot code
0 represents coolant at or below -40 deg C; positive snapshot code `A` represents
`A - 40 deg C`. This identifies only the `ffff1186` invocation of shared table
`0x12DEA`; other input sources of that table remain physically unresolved.

**Revolution cadence and completion flags (code, corroborated by homologous ESM).**
The exact scheduler path begins at `FUN_000208f8`. Both callers are engine-event
paths that update the current-cylinder state. Each admitted event sets
`ffff84ba.bit7`; modulo-3 counter `ffff9f24` sets `ffff84ba.bit6` after every third
event. `FUN_000209d8` uses that pending bit to run the three-entry table at
`0x21960`; its second entry is `FUN_0007c494`, which tail-calls window producer
`FUN_000872d0`. Three current-cylinder events per crankshaft revolution on the V6
therefore give one producer invocation per revolution. The VQ35HR ESM independently
describes the exact P0300..P0306 monitor as checking CKP variation every 200 engine
revolutions for one-trip TWC-damage detection and every 1,000 engine revolutions for
two-trip emissions-deterioration detection. The ESM supplies homologous diagnostic
terminology; the exact JK08A code supplies the counters and scheduler relation.

`FUN_000872d0` maintains three 16-bit admitted-revolution counters. Stock JK03A and
JK08A both contain `ROM8[0x8354] = 1`, `ROM8[0x8656] = 1`, and
`ROM8[0x186CE] = 0x80`:

| Completion flag | Counter | Stock threshold | Reporter arguments available when serviced |
|---|---|---:|---|
| `ffff4241.bit5` | `ffff409e` | `200 * ROM8[0x8354] = 200` | `0/1` |
| `ffff4241.bit7` | `ffff40a0` | `1000` | `2/3` or `4/5` |
| `ffff4241.bit6` | `ffff40a2` | `200 * ROM8[0x8656] = 200` | first `0/1`, later `2/3` or `4/5` |

The first two counters increment together only while `ffff444d == 0`; the third uses
`ffff444c == 0`. Clearing `ffff4251.bit7` or either of `ffff41d2.bits0/1` resets all
three. Qualified interval-sample count `ffff3834` below 31, or a nonzero per-track
inhibit, freezes the affected counters rather than clearing them. Threshold checks
precede gate evaluation and increments in each producer call. Coordinator
`FUN_00082c8a` consumes and clears completion bits independently in the order bit 5,
bit 7, bit 6, so simultaneous window completions are handled in one coordinator pass.
The matrix proves that retained groups are result families shared by multiple windows,
not one-to-one cadence identifiers.

**Engine-speed qualification (code).** `FUN_000384fe` writes
`ffff11e8 = ffff1196 >> 3`; `FUN_0003846e` then writes
`ffff11ea = min(255, ffff11e8 >> 3) = min(255, ffff1196 >> 6)`. Scheduler
`FUN_00020dfe` calls copy helper `FUN_000220f8` for the 56-byte
`ffff11d4..ffff120b -> ffff119c..ffff11d3` block, which maps `ffff11ea` to
`ffff11b2` and word `ffff11f4` to `ffff11bc`. Because
`ffff11f4 = ffff1196 >> 6`, both snapshot destinations use the exact RPM/12.5
count scale. Byte `ffff11b2` saturates at 255; its implicit 1D-8 nodes
0, 32, ..., 224 correspond to 0, 400, ..., 2800 RPM. Word `ffff11bc` retains the
unsaturated engine-speed coordinate.

Once-per-revolution `FUN_0007c4e0` applies hysteresis to `ffff11b2` through
`ffff24c4.bit7`. A clear state sets at stock `ROM8[0x8BDA] = 32` (400 RPM). An
already-set state adds four counts before comparison, so it remains set at 28
(350 RPM) and clears below that value. While set, the function increments saturating
counter `ffff4096`; while clear, it resets the counter. Stock JK03A and JK08A contain
the same threshold byte.

`FUN_0003cf24` and coordinator `FUN_00082c8a` both require
`ffff4096 >= ROM8[0x83B8]`; the stock byte is 1. The coordinator's below-threshold
path clears `ffff4251.bits6/7`. Whole-program p-code passes over all 2,315 functions
found four exact accesses and no unresolved candidates for each of `ffff4096` and
`ffff24c4`. `FUN_0007c4e0` is the sole writer of `ffff4096` and the sole bit-7 writer
of `ffff24c4`; the other exact write, in `FUN_000593ac`, ORs only bit 6.

**Common readiness gate `ffff4251.bit7` (code).** Coordinator `FUN_00082c8a` is
the only function that writes bits 6 or 7 of this multipurpose byte. Its stock
success path requires every condition below:

| Condition | Exact stock requirement | Failure effect |
|---|---|---|
| Speed-qualified revolution age | `ffff4096 >= ROM8[0x83B8] = 1` | Clear bits 6/7 |
| Latched local inhibit | `ffff436f == 0` | Clear bits 6/7 |
| Shared diagnostic permission | `ffff41c8.bit7 == 1` | Clear bits 6/7 |
| Composite runtime-record gate | `FUN_00025a12() == 0` | Clear bits 6/7 |
| Six direct runtime-record gates | `FUN_000259e4(index) == 0` for `0x129`, `0x12A`, `0`, `0x130`, `0x14`, and `-1` | Clear bits 6/7 |
| AN0-derived snapshot | unsigned `ffff1108 >= 0x89` | Clear bits 6/7 |
| Engine speed | `ROM8[0x88E4] <= ffff11ae < ROM8[0x88E5]`, stock `6 <= value < 0x98` | Clear bits 6/7 |

Byte `ffff11ae` is RPM/50, so the speed interval is exactly
`300 <= RPM < 7600`. Scheduler `FUN_00020dfe` populates `ffff1108` from current
byte `ffff1188` through the 128-byte
`ffff1114..ffff1193 -> ffff1094..ffff1113` snapshot copy. `FUN_00039a9e`
produces `ffff1188` from SH7058 ADC channel AN0 at MCU pin 86/H17. The ECM terminal,
physical signal, and engineering scale remain unresolved. A whole-program p-code
pass found 96 exact reads of `ffff1108`, no direct writes, and no unresolved
candidates; the block-copy helper explains the absent direct store.

The runtime-record helpers have closed contracts. `FUN_000259e4(index)` addresses
the third byte of `ffff5718 + 3*index` and returns 1 when bit 5 or bit 6 is set. It
returns 0 when both bits are clear, and signed index `-1` returns 0 without a RAM
read. `FUN_00025a12` OR-reduces that predicate over index `0x14`, the range
`0x47..0x4C`, and the range `0x8A..0x8C`; its two calls with `-1` are inert. The
coordinator therefore admits the gate only when none of the listed diagnostic
runtime records carries either operational result-state bit. These internal bits
are not assigned UDS status names, and the physical grouping of the checked records
remains unresolved.

The local inhibit is a latch, not a countdown. Before testing the common gate,
`FUN_00082c8a` checks `ffff84c3.bit6` and unsigned `ffff2b73` against
`ROM8[0x8500] = 5`. If both conditions pass, it writes
`ROM8[0x8C2E] = 0x32` to `ffff436f`. A second whole-program p-code pass found only
this write and the subsequent gate read among all 2,315 functions, with no unresolved
candidates and no statically resolved clear. Reset-time or pointer-mediated
initialization remains unresolved; no time unit is assigned.

After all prerequisites pass, the coordinator first sets `ffff4251.bit6`. Stock
`ROM8[0x8AFC] = 0x28` has bit 3 set, so the same path then sets bit 7
unconditionally. If that ROM bit were clear, the alternate branch would set bit 7
when `ffff4184.bit6` is clear and clear bit 7 when it is set. Stock JK03A contains
the same constants `01`, `05`, `06 98`, `28`, and `32` at the five gate locations,
and its executable code is byte-identical to JK08A.

The exhaustive external bit-7 consumers are:

- `FUN_000847dc`, the retained operating-point snapshot matcher;
- `FUN_00085020`, an auxiliary P030 state service called only by the coordinator;
- `FUN_00085a70`, which gates the weighted accumulators and counter groups;
- `FUN_000867c4`, the five-channel accumulation helper called only by
  `FUN_00085a70`;
- `FUN_000872d0`, which resets all three revolution-window counters when the gate is
  clear.

The coordinator also reads bit 7 after writing it and resets its P030 accumulators
and related working state when clear. A whole-program `TraceRamAccesses.java` pass
found 81 exact accesses to byte `ffff4251`, no unresolved candidates, and 20 writer
functions. Machine-mask inspection shows that the other 19 writers affect only bits
0..5. The read in engine-event driver `FUN_00029588` tests bit 0, not bit 7, and is
not part of this gate.

**ATU-II capture-interval history qualification (code).** Byte `ffff13b2` is an
ATU-II engine-event mode selector. `FUN_00029588` dispatches values 0, 4, 6, 7, 8,
and 9. When the selector equals `ROM8[0x8BDC] = 9` and `ffff84f1.bit7` indicates a
valid previous capture, the function reads the 32-bit ATU-II channel 0A input-capture
register `ICR0A` at `fffff434`, stores `abs(ICR0A - ffff84d4)` at `ffff1dac`,
and sets coalescing flag `ffff84f2.bit7`. A second comparison uses
`ROM8[0x8BDD] = 9`; the same selector-9 invocation refreshes `ffff84d4` from
`ICR0A` and sets `ffff84f1.bit7`. The first selector-9 capture therefore seeds the
reference, and every subsequent selector-9 invocation produces an interval between
consecutive `ICR0A` captures.

A whole-program exact-address pass found nine reads of `ffff13b2`, no writes, and no
unresolved candidate anchored at the byte. A broader pass over
`ffff128c..ffff13ff` produced 107 candidate writes. The 103 direct base-relative
candidates start at offset `0x18A`, beyond target offset `0x126`. The four
pointer-table writes in `FUN_00040e6c` resolve only to `fffff74e` and
`ffff1e92..ffff1f10`. Review of all seven constant-address calls likewise found no
writer capable of reaching `ffff13b2`. Its initializer or runtime producer and the
physical names of selector modes remain unresolved.

`FUN_0003cf24` consumes and clears `ffff84f2.bit7`, shifts the 14-longword history
`ffff1dac..ffff1de0`, and updates saturating history-age counters. Invalid speed or
prior-reference state fills the history with the current interval and resets all three
age counters. On valid samples, `ffff3834` increments only while configuration
`ffff4247.bit6` is set; otherwise it resets. Detection core `FUN_00085a70` requires
`ffff3834 >= 19`, while revolution-window producer `FUN_000872d0` requires
`ffff3834 >= 31`. These thresholds count accepted consecutive selector-9 capture
intervals. Static code does not establish how many selector-9 captures occur per
crankshaft revolution or unit time, so neither threshold is converted to revolutions
or duration.

An exact-byte whole-program p-code pass over all 2,315 JK08A functions found 12
accesses to `ffff4247` in eight functions and no unresolved candidate. The sole
resolved write is `FUN_000d093c`, which preserves the byte and ORs bit 4. A broader
source-boundary pass over `ffff4000..ffff42ff` found no base-relative,
pointer-derived, or constant-address write capable of producing bit 6. The bit-6
feature name and its startup, retained-memory, or external configuration source remain
unresolved.

**Snapshot reuse (code).** Before later result handling, `FUN_00082c8a` passes all
three retained groups to `FUN_000847dc`. Under `ffff4251.bit7` and
`ffff41d2.bits0/1`, the matcher returns 1 exactly when:

- current RPM/12.5 word `ffff11bc` is in
  `[max(snapshot_speed - 30, 0), min(snapshot_speed + 30, 255))`; the 30-count
  tolerance is 375 RPM;
- current calculated-load code `ffff413e` is in
  `[floor(8 * snapshot_load / 10), floor(12 * snapshot_load / 10))`;
- current and retained coolant codes are both below 110 or both at least 110.

Coolant code 110 is 70 deg C. The payload and match contract are therefore exact
operating-point snapshot semantics. The window cadence is exact, but the firmware does
not name the diagnostic phases represented by groups 0..2. Those identities remain
deliberately numbered.

**P030 result-latch lifecycle (code).** Bit 3 of `ffff5b2c` is a global result latch
shared by the seven exact P0306..P0300 runtime records, not a retention marker for one
snapshot group. The reporter argument supplies an operational polarity:

- even arguments set one of `ffff5b2b.bits4..6` before dispatch;
- odd arguments clear all three selector bits and set `ffff5b2c.bit3` before dispatch.

All seven descriptors have byte 8 equal to `0x40`, so common dispatcher
`FUN_0007d8b8` routes them to `FUN_0007dc32`. That handler always sets bits 0 and 1 in
the selected record's third byte. A nonzero selector mask calls `FUN_0008c942`, which
sets record bits 3 and 6. A zero selector mask sets record bit 5, calls
`FUN_0008c968` to set record bit 4, and sets `ffff5b2c.bit3`. The odd reporter tail
sets the same latch once more after dispatch. These redundant writes make the
odd-polarity latch independent of the descriptor-specific subpath.

`FUN_0008042c` scans the seven third bytes in descriptor order from P0306 to P0300.
Third-byte bit 6 terminates the scan without retaining the global latch. Bit 5, tested
after bit 6, terminates the scan and retains the latch. Records carrying neither bit
clear `ffff2461.bit3` and advance. Therefore `ffff5b2c.bit3` survives reconciliation
exactly when the first record carrying either result bit has bit 5 set and bit 6 clear.

The clear and cleanup paths are also closed:

- the `ffff424f.bit2` initialization block in `FUN_00082c8a` clears the latch with all
  retained snapshot state;
- `FUN_0007c57a` increments saturating counter `ffff4a49` while the latch and its
  maintenance gates are active. At count 3 it clears bit 5 from the second and third
  bytes of all seven P030 records, the global latch, all three snapshot payloads and
  markers, the group-0 capture latch, and auxiliary group bytes;
- common record-aging pass `FUN_0007cf14` clears the global latch when an aged record
  belongs to exact descriptor indices `0x0A..0x10`;
- group-0 and group-2 cleanup functions `FUN_0007c8fa` and `FUN_0007c9a8` defer their
  bit-6 and retained-payload cleanup while the global latch remains set.

The internal record-bit transitions and odd/even reporter polarity are exact. Static
code does not establish UDS names for these bits, physical pass/fail meaning for either
polarity, diagnostic phase names for groups 0..2, or a physical-time duration for the
maintenance counts. The separate 200/1000-revolution completion cadence is exact.

Component confidence is `code` for the trio, classifier, five-state selector,
readiness bits 0..2, event counters, retained operating-point snapshots, snapshot
matcher, revolution-window cadence, P030 runtime result lifecycle, and flags
`ffff4217`/`ffff41c3`/`ffff4218`.
Threshold-map scales have not been derived (offset-binary), while counter scale is
identity in event-count units. The exact P0300..P0306 path establishes the physical
monitor class as misfire detection; the internal metric and threshold engineering units
remain unresolved.


### Table-access library - region `0x26000..0x26E00` [CONFIRMED]

Calibration tables are read through a library of small functions occupying contiguous
region `0x26000..0x26E00`. The region partitions strictly: every pointer target inside
it is addressed either only from outside, making it an entry called by application
code, or only from inside, making it implementation code such as kernels, finishers,
and shift chains. There are no mixed targets.

Enumeration of region entries is the catalog completeness boundary, and it is
verifiable: every aligned BE word in ROM whose value lies inside the region is scanned.
Earlier roots were incomplete:

- The call tree of `0x26944` does not see entries using other kernels.
- Finisher `0x26740` does not see 2D wrappers because they reach it transitively through
  a 1D kernel and do not retain the finisher address in their own pool. It also does not
  see the non-interpolating family that never calls a finisher (`0x260BC`).

There are 39 even-valued entries; an odd value cannot be an SH-2 entry and represents
coincidental data. Of these, 35 access tables and 4 do not:

| entry | slots | purpose |
|---|---:|---|
| `0x2657C` | 4 | signed multiplication with a variable shift |
| `0x26014` | 6 | wrapper around `0x2657C` for a negative multiplier |
| `0x265C4` | 11 | saturating addition to INT_MIN/INT_MAX on overflow |
| `0x26DA8` | 3 | write to a RAM structure; reads no table |

Two access models are distinguished by axis representation:

| model | axis | reference census |
|---|---|---|
| explicit-axis | breakpoint array through a pointer in `r5`/`r6`; the kernel searches downward for a point | `MapInventory.java`, one run per kernel |
| implicit-axis | no array; N points at a uniform step over raw input | `DirectLookupInventory.java`, one run per bank |

The models differ in operand interpretation, not call structure. In both, a slot holds
a pointer to a common engine, a specialized entry jumps to it, and an accessor calls
the entry through `jsr`. A bank primitive is therefore a wrapper, while the shift chain
is its kernel. `ResolveAccessors` covers both families with one mechanism whose census
registry is `JK08A.interp.csv`. Unique sites match the reference censuses: 327
explicit-axis and 227 implicit-axis. Expanding selector alternatives turns 554 sites
into 587 rows.

The resolver yields **436 maps**, 248 explicit-axis and 188 implicit-axis, with no map
shared between families. The manual layer declares 14 maps across five families: four
comparator, five direct-row-major, two implicit-2d, two direct-scalar, and one
direct-indexed map, bringing the complete graph to **450 maps**.


### explicit-axis: three kernels and 24 wrappers [CONFIRMED]

The kernels are byte-identical except for axis-element width. The decisive difference
is the downward-search step: `ADD #-1,R4` for a byte axis versus `ADD #-2,R4` for a
word axis.

| kernel | axis | wrappers | maps | sub-helper |
|---|---|---:|---:|---|
| `0x26944` | bytes | 11 | 111 | `0x26C78` |
| `0x26984` | words | 7 | 114 | `0x26C78` |
| `0x26B84` | words | 6 | 23 | `0x26BC0` |

Wrappers are arranged as a bank: a body followed by a private pool containing two
slots, kernel and finisher. Canonical form at `0x26474`:

```
26474: 4f22  STS.L PR,@-R15
26476: 2f46  MOV.L R4,@-R15        ; save table pointer
26478: 6053  MOV   R5,R0           ; R0 = axis pointer
2647a: 656c  EXTU.B R6,R5          ; R5 = input & 0xff       <- INPUT width
2647c: d707  MOV.L @(0x2649c),R7   ; R7 = kernel 0x26944
2647e: 470b  JSR   @R7
26480: e407  MOV   #0x07,R4        ; delay slot: clamp       <- GEOMETRY
26482: 66f6  MOV.L @R15+,R6        ; R6 = table pointer
26484: 364c  ADD   R4,R6           ; add index from kernel
26486: 8461  MOV.B @(1,R6),R0      ; y1                      <- ELEMENT width
26488: 620c  EXTU.B R0,R2
2648a: 6353  MOV   R5,R3           ; R3 = fraction from kernel
2648c: 6160  MOV.B @R6,R1          ; y0
2648e: 4f26  LDS.L @R15+,PR
26490: d601  MOV.L @(0x26498),R6   ; R6 = finisher 0x26740
26492: 462b  JMP   @R6             ; tail jump
26494: 601c  EXTU.B R1,R0          ; delay slot
```

Wrapper geometry is read from its code and does not require caller traces. The clamp
in the delay slot (`MOV #imm,R4`) defines the number of axis points, while row stride
(`MOV #imm,R5` or a pool constant) defines row width. For a word axis, the clamp is in
bytes: `0xE = 2*7` means 8 points and `0x1E = 2*15` means 16 points. This rule
reproduces all five wrappers whose dimensions were previously established by an
independent trace: `0x26084`=4x4, `0x26140`=8x8, and
`0x261B8`/`0x261F0`/`0x26320`=16x16.

Complete wrapper geometry is in entry registry `JK08A.interp.csv`, which supplies it
to the graph. Notable cases:

- `0x262E0` and `0x26660` use axes of different widths in one map, with clamps 15 and
  30 for byte and word axes.
- `0x26550` combines a word axis with byte elements: `SHLR R4` converts the byte offset
  produced by the kernel back to an element index.
- `0x260BC` performs **a read without interpolation**: it does not call a finisher and
  reads a point directly (`RTS` plus `MOV.B @R4,R0` in the delay slot). Row stride is
  pool constant `0x260F8 = 4`, not an immediate. This family had remained an open
  question in the log; it exists.

There are seven finishers, and `0x26740` is not common to all of them. A 1D entry reads
the element itself, while a 2D finisher reads it, so the `storagetype` of a 2D map
comes from here. See "2D map element encoding".

| finisher | entries | element | behavior |
|---|---|---|---|
| `0x26740` | 1D entries for kernels `0x26944` and `0x26984`, plus `0x2642C` | defined by entry | 1D linear interpolation |
| `0x26AF8` | 1D entries for kernel `0x26B84` | defined by entry | same operation; formula is identical |
| `0x26770` | `0x26084`, `0x26100`, `0x26140`, `0x26178`, `0x261B8`, `0x261F0` | uint8 | byte-oriented 2D |
| `0x267CC` | `0x26230` | uint8, bit7 flag | 2D over 7 bits with pass-through bit7 |
| `0x268A4` | `0x26320` | uint8, 0..127 | byte-oriented 2D; `>= 128` saturates output |
| `0x26848` | `0x26270`, `0x262A8`, `0x262E0` | uint16 | word-oriented 2D |
| `0x26B28` | `0x265F0`, `0x26628`, `0x26660` | uint16 | word-oriented 2D |

Linear interpolation at `0x26740`; branching avoids signed overflow on a descending
segment:

```c
if (y1 < y0) return y0 - ((y0 - y1) * frac >> 16);
return y0 + ((y1 - y0) * frac >> 16);
```

Registers are `y0=R0`, `y1=R2`, and `frac=R3`, matching wrapper code directly.


### 2D map element encoding [CONFIRMED]

A 2D map element is read by the finisher, not the entry. The entry supplies indices
and fractions for both axes (`r0`/`r1` for rows, `r2`/`r3` for columns, `r4` for the
base, and `r5` for row stride) and reaches the finisher with a tail jump. This
establishes `storagetype` for all 69 2D maps in the catalog.

All five 2D finishers read elements as **unsigned**, applying `EXTU.B` or `EXTU.W` to
both operands of every interpolation. There is no `EXTS` instruction anywhere in
region `0x26740..0x26BC4`.

One output appears signed on the exact-hit path: when both axis fractions are zero, the
value reaches `RTS` directly from `MOV.B @R4,R0`, which sign-extends. The evidence comes
from interpolation, not this path. The extension is dead because the caller truncates
the result back to a byte, as accessor `0x82c8a` does with
`mov.b r2,@(ffff314a)`. For a signed element, transition `0xFF -> 0x01` would be
interpolated downward from 255 to 1 because `0x26740` compares `y1 < y0` over unsigned
operands.

The three byte-oriented finishers interpret bit7 differently:

- `0x26770` uses a plain uint8: the entire byte is the value.
- `0x267CC` treats bit7 as a flag. It interpolates the low 7 bits
  (`AND R9,R2` with `R9 = 0x7F` for every operand), then takes bit7 from the base cell
  and returns it in the result (`TST R1,R2; OR R1,R0` with `R1 = 0x80`). Its sole entry
  is `0x26230`, serving maps `0x991A`/`0x9A1A`/`0x9B1A`.
- `0x268A4` treats bit7 as saturation. Every cell is tested with `CMP/HS` against 128;
  if any bit7 is set, the complete sample output becomes 128 (`MOV R6,R0`), restricting
  values to 0..127. Its sole entry is `0x26320`, serving maps
  `0xB61A`/`0xB71A`/`0xB81A`.

`0x268A4` explains the shape of `0xB61A`: 136 of its 256 cells equal 128 and form a
contiguous "high speed at low load" region. They are saturation markers rather than
values, so the map is defined on the complement of this region. `0xB81A` has no such
cells and ranges from 33 to 63.

`0x260BC` is the only 2D entry without a finisher: it reads a point directly and
discards calculated fractions for both axes. Interpolation cannot prove the type here,
so three independent signals converge. Both callers, `0x79538` at sites `0x7969C` and
`0x796E6`, truncate the result to a byte, making sign extension dead here as well. The
rest of the 2D family is unsigned. Data in both maps form monotonic surfaces
(`0xAAEA` = 10..200) that a signed read would break into `20 100 -56 -56`.


### implicit-axis: primitive bank `0x26358..0x2642C` and `0x266A0` [CONFIRMED]

There is no axis array: the axis is uniform, with points `0..(N-1)` at step `step` and
the last point as the limit. There is no wrapper layer either: an accessor calls a
primitive directly through a pool slot. Canonical form at `0x26370`:

```
26370: 9007  MOV.W @(0x26382,PC),R0   ; R0 = 224 = limit
26372: 655c  EXTU.B R5,R5             ; input & 0xff
26374: 3502  CMP/HS R0,R5             ; T = (input >= limit)
26376: 8902  BT 0x2637e               ; out of range: RTS, R0 = MOV.B @(7,R4)
26378: d602  MOV.L @(0x26384,PC),R6   ; R6 = core
2637a: 462b  JMP @R6
2637c: e300  MOV #0x00,R3             ; delay slot: R3 = 0
```

| entry | points | step | limit | element | core | slots | tables |
|---|---:|---:|---:|---|---|---:|---:|
| `0x26358` | 4 | 64 | 192 | u8 | `0x26A7C` | 5 | 5 |
| `0x26370` | 8 | 32 | 224 | u8 | `0x26A80` | 61 | 92 |
| `0x26388` | 16 | 16 | 240 | u8 | `0x26A84` | 31 | 57 |
| `0x263A0` | 32 | 8 | 248 | u8 | `0x26A88` | 7 | 2 |
| `0x263BC` | 4 | 16384 | 0xC000 | u16 | `0x26A5C` | 2 | 4 |
| `0x263D8` | 8 | 8192 | 0xE000 | u16 | `0x26A60` | 13 | 13 |
| `0x263F4` | 16 | 4096 | 0xF000 | u16 | `0x26A64` | 11 | 10 |
| `0x26410` | 64 | 256 | 0x3F00 | u16 | `0x26A74` | 1 | 2 |
| `0x2642C` | 16 | 16 | 240 | u8 | `0x26740` | 1 | 1 |
| `0x266A0` | 16 | 4096 | 0xF000 | u16 | `0x26C1C` | 2 | 2 |

Column "slots" comes from the reference census of slots containing the primitive
pointer; "tables" comes from bases recovered by the graph resolver. A slot is not a
call, and a primitive can serve more tables than it has slots.

Geometry in every row was obtained by two independent methods, which agree in all ten
cases:

1. The limit is a constant in primitive code; the edge of the range is read at offset
   `MOV.B @(N-1,R4)` or `MOV.W @(2*(N-1),R4)`. This gives the point count.
2. The step comes from the entry into a shift chain. Chain `0x26A5C..0x26A94` consists
   of consecutive `SHLR R5` / `ROTCR R3` pairs. Entry K pairs above the merge yields
   `index = raw >> K`, so `step = 2^K`.

Identity `limit = (points-1) * step` holds for every row. This is not curve fitting but
the family definition: arithmetic defines the axis and no separate breakpoint table
exists.

`0x26A5C`..`0x26A88` are not seven functions but shifted entries into one chain. Their
4-byte spacing is exactly one `SHLR`/`ROTCR` pair. `0x26C1C` is a second independent
copy of the same chain with 12 pairs and step 4096.

At merge point `0x26A94`, `SWAP.W R3,R3; SHLR8 R0; TST R0,R0; BT` selects element
width. The selector is **the limit itself**: limit >= 256 means a word table, with no
separate flag in code. Both branches end in `EXTU.B` / `EXTU.W`, so **values are
unsigned**. Only the edge remains signed because an input >= limit returns through
`MOV.B`/`MOV.W` without `EXTU`.

`0x2642C` differs from the bank in its output: the result is reduced by
`DAT_0002646C = 128`, making values offset-binary with 128 as zero, a signed correction
map.

SH-2-specific census model [CONFIRMED]: **all 107 sites for `0x26370` set `r5` in the
delay slot** (`_extu.b rN,r5` after `jsr`). A backward-only backtrack such as
`MapInventory` would recover no input. A slot is not a call: `FUN_0005185c` has one
slot at `0x5197c` and performs 6 lookups through it.

Data validation: of the 81 `0x26370` tables recovered by the reference census,
75 are monotonic, either increasing or decreasing. Random bytes would show this with
probability about 5e-5, so the addresses are genuine. Exactly one table, `0x122E2`, is
filled with `0xAA` and is therefore unprogrammed.

`0x26740` is not the bank kernel but a lower-level primitive [CONFIRMED]. Its pointer
is held by **12 functions**: six explicit-axis wrappers (`0x26474`, `0x264A0`,
`0x264CC`, `0x264F8`, `0x26524`, `0x26550`), 2D finisher `0x26770`, four other
internal interpolation entries (`0x267CC`, `0x26848`, `0x268A4`, `0x26A60`), and
`0x2642C` itself. Each of the other nine primitives is private to one kernel: one slot
and one reference. A census by `0x26740` therefore yields 230 sites instead of one.
The registry declares it as a wrapper, counting only sites through `0x2642C`. Discarded
sites are not lost from their own families: 216 belong to explicit-axis censuses, while
13 internal entries do not read tables at all.

Resolver comparison against the bank reference: both find 227 unique sites, but
`df_r4` resolves 225 versus 205. Selector expansion produces 236 rows and
**188 maps**. This adds 20 to the original census of 168 maps: data flow supplied
16 bases at previously unresolved sites, while four more appeared as `MULTIEQUAL`
alternatives. No reference base is lost, and every site resolved by both methods agrees;
`DirectLookupInventory` was correct wherever it returned an answer.

The reference misses come from `poolValueOf`, which accepts a reference only within
`0x800` bytes of the instruction under the literal-pool rule. At sites such as
`0x716C0`, it treats the base as a delay-slot expression (`jsr @r7; _add 0x8,r4`), while
the valid Ghidra reference to `0x12A2A` lies farther away. Data confirms all sixteen
data-flow additions: 12 are monotonic, while the other four are plateaus and windows
such as `[0,0,0,0,0,0,255,255,255,255,0,0,0,0,0,0]`, calibration structure rather
than noise.


### 2D with implicit axes - `0x26040` [CONFIRMED geometry]

This entry lies outside both census models. `0x26040` calls `0x26AE0` for each axis,
making the axes implicit as in the primitive bank, then passes the result to 2D finisher
`0x26770` with row stride 8. There are two 8x8 maps: `0xA8EA` through accessor
`0x52576` and `0x9EDA` through accessor `0x526A0`. Both use inputs
`byte[0xFFFF106F]` and `byte[0xFFFF10F0]`.

The element is `uint8`, established by finisher `0x26770`; see "2D map element
encoding". Data in `0xA8EA` independently agrees: its first row
`126 126 127 129 130 131 132 132` is monotonic, whereas a signed read would introduce
discontinuity `127 -> -127`.


### Operand sets: selectors expand by branch [CONFIRMED]

A base or axis selected by branching reaches the call through p-code `MULTIEQUAL`.
Collapsing such an operand to one value is incorrect: all alternatives exist in ROM,
and runtime state selects the executed one. The resolver emits a separate row for each
branch with `verdict=selector`, `k4/k5/k6=phi`, and a `branch` number. Operands from the
same branch are associated by their input index in `MULTIEQUAL`, without taking the
Cartesian product of independent sets.

In the complete JK08A resolver, 40 sites carry a selector: 37 with two branches, one
with three, and two with six. Within the catalog's 34 declared entries, these correspond
to 28 unique sites. Expansion produces 587 rows for 554 unique sites and adds 20 maps
relative to collapsing the set to one element. Selection conditions remain Stage 6
input: the base list is known, but the branch meaning and controlling
`:Flag {role:'selector'}` require separate analysis.

`0x64344`, using wrapper `0x26474`, expands to six tables through `r5`:

```
00064316  mov r5,r0 ; cmp/eq 0x1,r0
0006431a  mov.l @(0x64498,pc),r4   ; r4 = 0x12b5a
0006431e  mov.l @(0x6449c,pc),r4   ; r4 = 0x12b52
00064328  mov.l @(0x644a0,pc),r4   ; r4 = 0x12b2a
00064332  mov.l @(0x644a4,pc),r4   ; r4 = 0x12b3a
00064336  mov.l @(0x644a8,pc),r4   ; r4 = 0x12b32
00064344  jsr @r2                  ; -> 0x26474
00064346  _mov.l r4,@r15           ; references: 12b4a 12b52 12b5a 12b2a 12b32 12b3a
```

At `0xbe39a`, using wrapper `0x26140`, `tst r13,r13; bt 0xbe384` skips a load, but the
decompiler does not lift both bases into `MULTIEQUAL`: both data-flow rows retain
`0xA09A`, while the fallback names `0xA05A`. This is not evidence for adding `0xA05A`
to the graph. After expansion, 15 unique sites still have fallback `k4=sp`. Backtrack
names two bases outside the graph, `0xA05A` and `0x15320`; its value is not a fact until
code resolves the discrepancy.


### An axis also selects a branch - 14 fallback-only axes [CONFIRMED]

In the graph, 256 of 595 `:ACCESSES` edges carry an uncollapsed axis
(`kind5/kind6=sp`), and 14 of 230 axes are named by nothing else. The fallback can be
wrong for axes just as it can for bases. Direct evidence is site `0x735ac`, which names
`0x8000` as an axis even though erased flash begins there:

```
0x8000 as words: [65535, 65535, 65535, 65535, ...]   # entire array is 0xFFFF
```

An axis named only by the fallback therefore stays at `pattern`, not `candidate`.
Any collapsed site (`pool`, `slice`, `const`, or reviewed `copy`) promotes it to `candidate`; without
such a site, the fallback word is a heuristic. Axes of all nine maps emitted by the
definition are collapsed.

The same mechanism creates an apparent reciprocal declaration. Census fallback for
accessor `0x73432` reports `0x8000` beside `0x14114`, while `0xE98E` itself is a 16x16
map through entry `0x262e0` with `0x14114` as its collapsed `r6` axis. The complete
machine listing resolves the conflict. FUN_00073432 first interpolates a local
16-point row from `0xE98E`, then delay-slot instruction `0x735AE` replaces `r5` with
the stack-row pointer before the inverse lookup. Value `0x8000` is added only to the
signed request. Table `0x14114` supplies the returned coordinate values and is also
the normal column axis of `0xE98E`. The fallback-only `0x8000` axis remains a
structural census artifact and is not a semantic or scaling source.


### An axis element defines its search clamp, not the kernel [CONFIRMED]

A wrapper calls search separately for each axis, and those calls can use different
slots. `0x262E0` and `0x262A8` are both 16x16 through kernel `0x26984`, but their code
differs:

```
000262a8:  mov.l 0x262dc,r7   ; [0x262dc] = 0x26984
000262b4:  jsr   @r7          ; search axis r5
000262b6:  mov   #30,r4       ;   clamp 30 - delay slot
000262c2:  jsr   @r7          ; search axis r6 - SAME r7
000262c4:  mov   #30,r4       ;   clamp 30

000262e0:  mov.l 0x26318,r7   ; [0x26318] = 0x26a0c   <- byte search
000262ec:  jsr   @r7          ; search axis r5
000262ee:  mov   #15,r4       ;   clamp 15
000262fa:  mov.l 0x2631c,r7   ; [0x2631c] = 0x26984   <- word, DIFFERENT pointer
000262fc:  jsr   @r7          ; search axis r6
000262fe:  mov   #30,r4       ;   clamp 30
00026304:  shll  r0           ; byte-axis index doubled to word stride
```

The clamp equals `(points - 1) * element size`: for 16 points, a byte axis gives 15
and a word axis gives 30. It therefore supplies both facts at once, axis length and
element size. Element type is a property of the wrapper-axis pair, not the kernel.
Two of the 22 two-axis wrappers are mixed: `0x262E0` (`0x26A0C`/`0x26984`) and
`0x26660` (`0x26BC4`/`0x26B84`), both with byte r5 and word r6. Clamps in all
24 wrappers independently confirm the point counts in the registry.

Measurement from the image in Stage 4, rather than code reading, exposed the mismatch.
Axes `0x11D0C` and `0x18716`, declared as words, do not increase when read as words.
As bytes they form the same load staircase `[16,24,32,...,128,144]` at two independent
addresses and are byte-identical. Reading the same region as words runs beyond the end
of the array: after the 16 staircase bytes is another array,
`[0,0,0,0,0,0,0,0,0,1,4,9,16,25,36,45]`. After correcting the registry, both axes
increase and converge by content into one shared axis, as expected.


### Axis `0x119B2` is not read by reverse linear search [CONFIRMED]

This is the catalog's only non-increasing axis: `[156, 112, 75, 38]`, decreasing.
Kernel `0x26944` searches from the highest point downward for the first breakpoint
`<=` the current value. On a decreasing array, that returns the last index for every
input above 38, so the array cannot operate as an axis.

Three independent signals converge on the absence of calibration there:

- The map that reads it, `0x9C5A`, a 4x4 map through `0x26084`, contains only `0xFF`
  and is therefore unprogrammed flash.
- The image contains no occurrence of constant `0x119B2` (`mapkit/ptrscan.py`): the
  pointer is computed rather than loaded from a pool, matching `k6=slice` at its sole
  site `0x7a43e@0x7a498`.
- A normal increasing staircase begins nearby at `0x119A0`:
  `[6,9,12,15,18,20,22,24,26,28,31,34,37,40,50,100,150,200]`; `0x119B2` falls within
  its tail.

All-`0xFF` content alone is not evidence because a saturated limit looks the same, and
17 catalog maps have this content. Here the conjunction of all three signals is the
evidence. Resolution belongs to Stage 6 with other branch-selected operand sites.


### Inverse lookup: array pairs are read in both directions [CONFIRMED]

The same array can be a map base and the axis of another map. The graph contains
18 such addresses; 14 form seven mutual pairs:
`0x1199E`/`0x11D24`, `0x13202`/`0x155A0`, `0x15500`/`0x15690`,
`0x15540`/`0x156D0`, `0x18766`/`0x190D0`, `0x18E46`/`0x18F96`, and
`0x18E86`/`0x18FD6`. Both sides of pair `0x15500`/`0x15690` use wrapper `0x26524`:
site `0x732A8` uses base `0x15500` with axis `0x15690`, while `0x72E1E`, `0x7549A`,
and `0x7AAE0` reverse them. These are forward and inverse tables of one relationship,
not an annotation contradiction: the site defines the role, not the array itself.


### Reciprocal nonlinear coordinate pair `0x1199E`/`0x11D24` [CONFIRMED]

The 16-byte arrays exchange table and axis roles. Define
`F(z) = interp_u8(0x11D24, axis 0x1199E, z)` and
`G(q) = interp_u8(0x1199E, axis 0x11D24, q)`. The breakpoints of `F` are
`[0,3,6,9,12,15,18,20,22,24,26,28,31,34,37,40]`; its returned values are
`[0,1,4,9,16,25,36,45,54,64,76,88,107,129,153,179]`. The second lookup reverses
these roles. Code proves an operational reciprocal transform, not an exact
mathematical inverse at every interpolated integer.

Four consumers establish the transform's arithmetic:

- `FUN_0006469C` forms
  `x=clamp_u8(s8[ffff23f1]-s8[ffff2404])`, `a=F(x)`, and
  `y=floor((0xff00-u8[ffff1862]*(256-a))/256)`, then writes
  `clamp_s8(s8[ffff23f1]-G(y))` to `ffff1346`.
- `FUN_00063F30` uses the same forward-blend-inverse construction with weight
  `ffff186a` to update bounded Q8 state `ffff23c2`. A mode selected by
  `ffff2482.bit2` instead evaluates `F` at two separated coordinates, updates
  `ffff14c0` and `ffff2ec3`, and counts `ffff23c2` down to zero.
- `FUN_000655B4` and `FUN_00065B08` apply channel-specific coordinate increments and
  calculate `trunc0(K*(256-F(x1))/(256-F(x0)))`, where
  `K=s16[ffff18cc]`. Their alternate paths use
  `trunc0(K*(256-F(x))/256)` or copy the paired channel. Signed saturation produces
  `ffff18d4` and `ffff18ce`. The divisor is always nonzero because `max(F)=179`, so
  `256-F(x)>=77`.

The convex, near-square table shape is descriptive evidence only. The physical
quantity, engineering units, and names of the two channel states remain unresolved.


### Map axes: orientation is proven, physical scale remains candidate

Kernel `0x26944` performs a one-dimensional axis search. It reads `byte[axis + i]`
from `i=15` downward, finds the first breakpoint `<=` the current value, then a second
stage through `PTR@0x26980` calculates the fraction. The wrapper calls the kernel twice:
first for `r5` and the current value in `r7`, then for `r6` and the current value from
the stack. Both indices reach the finisher.

The finisher addresses a cell as
`cell = table + idxY_wrap + idxX_wrap * 0x10`. Therefore, wrapper axis `r5` supplies
rows, the slow index, and axis `r6` supplies columns. In RomRaider terms, X Axis maps
to columns and Y Axis to rows. This orientation is a structural fact independent of
the physical axis names.

In several families, the current value for axis `r5` comes from
`byte[0xFFFF11AE]`, while axis `r6` receives other RAM quantities, including the high
byte of `word[0xFFFF1024]` and `word[0xFFFF11F4]`. Accessor code confirms raw uint8
indexing, but the export lacks the writer for structure `0xFFFF119C..0xFFFF11B7` that
would associate `0xFFFF11AE` with physical engine speed. Shapes of axes `0x11B6B`,
`0x12F2E`, and `0x11CF0` are compatible with RPM and multiplier `x*50`, but this is a
`candidate` catalog interpretation rather than code evidence.

Axis `0x11ECE` uses RPM/12.5 word `ffff11bc`. Machine arithmetic multiplies each raw
axis point by four before comparison, which establishes user-facing scale `x*50 RPM`
and range 400..7400 RPM at `code` confidence. A2L homology independently agrees with
the same scale.


### Correction and filter weight `0xAB0A`/`0xB23A`, FUN_000BEFB0

Accessor `0xBEFB0` reads two 8x8 uint8 maps through an interpolator. `0xAB0A` supplies
a separate correction addend in range 4..37: code adds `uint8[ffff1071]`, subtracts
`0x32`, and multiplies the result by a coefficient from `ffff3502`. This coefficient
comes from adjacent map `0xB23A`, which is constant at 27, and serves as the new-sample
weight in an aperiodic filter:
`new = old*(65536-K)/65536 + target*K/65536`. The operational formulas for both maps
have `code` confidence. The physical name of the filtered quantity and catalog identity
as accel/decel fuel compensation remain `candidate`.

Code confirms only raw axis inputs: `byte[0xFFFF11AE]` for rows and the high byte of
`word[0xFFFF1024]` for columns. Axis addresses are `0x120AE`/`0x120B6` for `0xAB0A` and
`0x12858`/`0x12860` for `0xB23A`. Names RPM/load and RPM multiplier `x*50` are based on
point shape and remain `candidate`.

A diagnostic analog is `0xa52e4`, which selects one of two 8x8 maps
`0xABFA`/`0xABBA`, with shared RPM axis `0x12BE2` [800..3600] and load axis
`0x12BEA`, according to condition
`byte[0xFFFF3427] > byte[0x8796]`, where the ROM threshold is `0x5F`=95. The result
passes through `ffff338a` and accumulator `ffff3334` to states
P0327/P0328/P0332/P0333. Code confirms the monitor role for knock-sensor circuits;
the selector's physical quantity and output scale are unknown.


### Stationary rev limiter and fuel-output inhibit path

`FUN_0004F324` is the stationary rev-limiter state machine [CONFIRMED by code].
Its first entry condition is `byte[0xFFFF110E] == 0`. The exact source chain is:

```text
CAN 0x280 bytes 4..5, big-endian
  -> FUN_000C4506, divide by 10
  -> ffff113c
  -> FUN_0003A174 filtered ffff115e
  -> FUN_0003A254, divide by 20
  -> current byte ffff118e
  -> FUN_00020DFE snapshot
  -> previous-cycle byte ffff110e
```

Homologous observed Z34 CAN data identifies frame `0x280` bytes 4 and 5 as vehicle
speed with an approximate `raw/100 km/h` conversion. The two exact firmware
divisions produce approximately 2 km/h per `ffff110e` count. The required zero
value unambiguously limits the state machine to a stationary vehicle. The EcuTek
catalog independently contains a `Stationary Rev Limiter`.

The other entry requirements are `0xFFFF244F.bit2 == 1` and
`0xFFFF2458.bit5 == 0`. `FUN_00038618` forms the current source of
`0xFFFF244F.bit2` from:

```text
uint8[ffff1188] <= 100 or (uint8[ffff1164] & 0x04) == 0
```

`ffff1188` originates at ADC channel AN0, MCU pin 86/H17. `ffff1164.bit2`
originates at PHDR bit 4, MCU pin 67/B19, with active-low polarity. Their ECM
terminals and physical signal names remain unresolved. `ffff2458.bit5` belongs
to a broader inhibit/fail-safe state and also remains physically unnamed.

Map `0x124D2` advances readiness accumulator `0xFFFF16A6`. ROM word `0x911C`
contains its inclusive threshold of 381 counts. With readiness set, the
RPM/50 byte at `0xFFFF11AE` controls fuel-cut state bit 5:

| address | raw | scale | stationary threshold |
|---|---:|---:|---:|
| `0x85D9` | 36 | `x*50 RPM` | fuel cut at 1800 RPM |
| `0x85DA` | 30 | `x*50 RPM` | fuel restore below 1500 RPM |
| `0x911C` | 381 | accumulator counts | readiness |

The state machine loads timer `0xFFFF258A` with 100 on entry and after every
readiness update. `FUN_0002040C` decrements that byte every tenth base interrupt.
The lookup coordinate is
`clamp((signed16(0xFFFF11BC)-160)/2, 0, 255)`, and each expiry adds
`lookup(0x124D2)-128` with saturation. At or below 2000 RPM the stock step is
zero. In the high-RPM limiter region it is 127, so exactly three expiries reach
`3*127 = 381`, or 300 countdown counts. The exact countdown period is
`204800/Pphi`; candidate `Pphi = 20 MHz` gives about 3.072 seconds.

The returned Boolean enters `FUN_0004ED88`, which combines global and
per-channel inhibit masks and writes `0xFFFF22E0`.


### Over Run Fuel Cut and Restore tables

The complete deceleration fuel-cut model is maintained in
[`JK08A.dfco.md`](JK08A.dfco.md). Its static path is code-confirmed:

```text
FUN_0004FBE2  cut request
  + FUN_00050018  restore classifier
  + FUN_0004FE9C/FUN_0005038A  entry and exit delays
  -> FUN_000503E0  five-state DFCO machine
  -> FUN_0004ED88  aggregate six-channel arbitration
  -> ffff22e0
  -> injector pulse eligibility and ATU-II one-shot scheduling
```

All four coolant-indexed RPM tables are live in exact JK08A code. The A2L
Bosch/JECS labels describe source families but do not identify inactive tables
in this executable:

| address | exact JK08A role | stored scale |
|---|---|---|
| `0x126E4` | held-request threshold | `x*25 RPM` |
| `0x12718` | rising-edge entry threshold | `x*25 RPM` |
| `0x12818` | lower/full-restore threshold | `x*25 RPM` |
| `0x1298C` | upper/intermediate-restore threshold | `x*25 RPM` |

`FUN_0004FBE2` uses the current and previous snapshots of
`0xFFFF2459.bit5` to distinguish a rising DFCO-mode edge from a held request.
`FUN_00050018` always interpolates both restore maps and returns class 0, 1, 2,
or 3 for remain-cut, master inhibit, intermediate restore, or full restore.

The coolant axis is also code-traced. Exact UDS DID `0x1101` returns
`ffff1079`; homologous measured diagnostic data defines
`coolant_deg_C = raw-50`. `FUN_00039634` converts this byte to current index
`ffff1077`, and the scheduler copies it to `ffff106f`:

```text
raw < 10       -> index 0
10 <= raw < 170 -> floor(240*(raw-10)/150)
raw >= 170     -> index 255
```

Implicit lookup nodes `0,16,...240` therefore represent coolant temperatures
`-40,-30,...110 deg C`.

Normal startup proves a timer input of `Pphi/64`; the DFCO timer cadence is
exactly `204800/Pphi` seconds per count. The board-level 10 MHz crystal and
manual `Pphi = EXTAL*2` relation imply a candidate 10.24 ms per count. Stock
entry delays are 40, 60, or 75 counts depending on runtime branches, while the
normal stage-2 and exit delays are zero. Conditional map `0x120F6` is a
code-proven stage-1 entry-delay table but is selected only by a non-stock
configuration branch.

The state byte `0xFFFF14C1` has closed states 0 through 4 and mask table
`[0x00, 0x00, 0x15, 0x3F, 0x15]` at `0x2371C`. Zero stock stage-2 and exit
delays make the partial-mask states transient in the normal path. A separate
release branch rotates a short fallback history across injector events near
750 RPM.

The output path is:

```text
ffff22e0
  -> FUN_0004EBA2  per-channel override selection
  -> FUN_00052034/FUN_00051A98  pulse/update eligibility
  -> FUN_0002C13C  fallback selection and ATU-II scheduling
```

This proves an inhibit/override chain to the six ATU-II channel 8 one-shot
outputs. It does not prove that a diagnostic injector-duration value becomes
zero: masked channels select fallback and override words rather than a literal
zero at every stage. Physical injector closure, channel-to-cylinder order, the
upstream mode-bit identity, and the candidate timing conversion remain hardware
validation items.


### A branch can be disabled by calibration - a table is referenced but not read

`FUN_00051700` at `0x51700`, 336 B, adjacent to `FUN_0005185c` and sharing its pool,
reads its own table set through the same primitive. A **ROM byte**, not engine state,
selects the set:

```c
bVar6 = *PTR_DAT_00051970 & 8;   // byte[0x8d92] & 8
if (bVar6 == 0) { lookup(0x12206); lookup(0x121F6); lookup(0x121AE); }
if (bVar6 != 0) { lookup(0x121E6); lookup(0x121AE); lookup(0x121CE); }
```

`byte[0x8D92] = 0x7A` means bit3 = 1, so the second branch is live.
**This firmware does not read `0x12206` or `0x121F6`**. Editing their values has no
effect unless the bit is changed.

Cluster `0x121AE..0x1220E` is a mode set rather than threshold pairs. `0x121C6`,
`0x121CE`, and `0x121D6` are byte-identical
(`[128,128,128,96,90,90,90,90]`), as are `0x121B6` and `0x121BE`. One profile is
replicated by mode, and calibration selects the mode.

This yields a general annotation rule: a code reference to a table does not make that
table live. ROM adjacency and a plausible shape, such as a second curve always below
the first and resembling hysteresis, do not replace a branch trace. The graph assigns
`role=dead` to such bases, and the finding names the selector.

The internal six-channel writer in `FUN_00051A98` belongs to the disabled
`ROM8[0x8D92].bit3=0` branch. One of its calibrated conditions is:

```text
ROM8[0x87FD]<<3 <= uint16[0xFFFF1024] - uint16[0xFFFF1028]
```

Scheduler `FUN_00020DFE` proves the relation between these words. At
`0x20F04..0x20F14` it copies the old `0xFFFF1024` value to `0xFFFF1028`,
then copies new source `0xFFFF1026` to `0xFFFF1024`. The condition therefore
tests a positive current-minus-previous sample increase of at least 200 raw
counts. It is not a stock Over Run Fuel Cut threshold: stock
`ROM8[0x8D92] = 0x7A` has bit 3 set and skips the writer, the `0x87FD`
comparison, and the `0x121EE` calculation path. `0x87FD` is not exposed as an
editable scalar.

`FUN_0005185C` independently tests
`signed16[0xFFFF10B8] < -ROM8[0x86AE]`. With `ROM8[0x86AE]=0`, any negative
input slope sets bit `0x10` of `0xFFFF24D2`. No direct consumer connects this
bit to the aggregate `0xFFFF22E0`; the detector is not used as proof for the
`FUN_0004F324` mode identity.

The three sample words carry Base Fuel Schedule. `ROM32[0x228BC] = 0xFFFF1026`
makes `0xFFFF1026` the exact two-byte big-endian response source for UDS DID
`0x1208`. A whole-program p-code scan found only the init writer in
`FUN_0002C648` and runtime writer in `FUN_0003B75C`, with no unresolved
computed-address candidates. The every-fourth-base-interrupt table at `0x21818`
runs `FUN_0003B75C` at index 3. The main-loop scheduler then rolls newest
`0xFFFF1026` into current `0xFFFF1024` and current into previous
`0xFFFF1028` every tenth base interrupt. The physical base-interrupt period is
not established.

A structured homologous Nissan diagnostic profile names DID `0x1208`
`B/FUEL SCHDL` and defines `raw/2048 ms`. The VQ35HR factory ESM independently
defines Base Fuel Schedule as the fuel-injection pulse width programmed before
learned onboard correction. The exact JK08A address and producer identity have
code confidence. The engineering conversion remains candidate until CONSULT3P
or bench measurements confirm it on JK08A.


### Throttle rev limiter scalar `0x942C`, FUN_0007584E [CONFIRMED PATH]

`ROM16[0x942C] = 0x2580`. Three independent layers identify its role:

- Code initializes dynamic threshold `0xFFFF1796` from `0x942C` at
  `0x2CE68..0x2CE70`.
- `FUN_0007584E` treats `0xFFFF` as a disabled sentinel and writes neutral
  `0x7FFF` to `0xFFFF19D8`. On the enabled path it multiplies current rotational-speed
  coordinate `0xFFFF11B6` by four, rate-limits `0xFFFF1796` toward the selected
  threshold, and writes signed candidate `0xFFFF19D8`.
- `FUN_00071508` includes `0xFFFF19D8` in a signed minimum cascade and writes selected
  limit `0xFFFF243A`.

The speed state is exact: the first pass stores `min(65535, 4*N)` and later
passes store `min(65535, N + floor(3*S_previous/4))`, where
`N = uint16[0xFFFF11B6]`. Stable input therefore converges to `4*N`. Stock
increment and decrement steps at `0x9430` and `0x9436` are zero and the
alternative cap at `0x9434` is `0xFFFF`, so normal-path threshold
`0xFFFF1796` remains at initialized value `0x2580`.

The other direct runtime reader, `FUN_00077892`, is a separate branch. It caps a
derived unsigned value at `ROM16[0x942C]`, applies lower bound
`ROM16[0x94B2] = 0x0500`, and writes `0xFFFF32EC`. The same function is the only
reader of that RAM word. This proves an auxiliary upper-bound use but does not assign
the branch a physical throttle, speed, or gear-control meaning.

The exact downstream request path is:

```text
ROM16[0x942c]
  -> FUN_0007584e -> ffff19d8
  -> FUN_00071508 -> ffff243a
  -> FUN_000702c6 -> controller state ffff1878
  -> FUN_00070cd6 -> ffff188c
  -> FUN_00070d20 -> ffff19c0
  -> FUN_00070d82 -> ffff2438 and ffff19c2
  -> FUN_00079030 -> ffff19c6
  -> FUN_00073432 / FUN_00073628 -> downstream interpolation branches
```

Scheduler `FUN_000702A0` calls the controller stages in the order
`702C6 -> 7038A -> 703B2 -> 7054A -> 70670 -> 70812 -> 70CD6 -> 70D20 ->
70D82`. `FUN_00070D82` implements the final selection:

- with `0xFFFF2490.bit1 = 0`, it selects `0xFFFF243A`;
- with the bit set, it selects `0xFFFF19C0`;
- with the bit set and `0xFFFF25D6 = 0`, it takes the signed minimum of
  `0xFFFF19C0` and `0xFFFF243A`.

The selected signed value is written identically to `0xFFFF2438` and
`0xFFFF19C2`. `FUN_00079030` reads both copies, applies additional
mode-controlled signed bounds, and writes `0xFFFF19C6`. `FUN_00073432` adds
numeric bias `0x8000` to this value to form an unsigned interpolation key and
writes `0xFFFF1984`/`0xFFFF198A`; `FUN_000730FC` consumes both outputs.
`FUN_00073628` uses the same `0xFFFF19C6` coordinate in a parallel branch
through `0xFFFF1D14`.

This trace closes the limiter path to a shared signed request coordinate in the
airflow/torque controller. It does not close a path to a bank-specific throttle
angle, an SH7058 timer/PWM register, or an ECM terminal. No direct call or data
edge from `FUN_00070D20` to `FUN_0003B498` is present; the functions belong to a
larger connected controller subsystem, but component membership is not a motor
output proof.

The adjacent calibrated branch `FUN_00075798` reads `ROM16[0x9476] = 0x0708`, writes
`0xFFFF19DE`, and feeds the same signed minimum cascade. Public EV18A definitions place
`Throttle Rev Limiter` at `0x9478` and `Speed Limiter` at `0x94C2`; both corresponding
JK08A scalars preserve an offset of `-0x4C`:

```text
EV18A 0x9478 -> JK08A 0x942C
EV18A 0x94C2 -> JK08A 0x9476
```

The HR A2L catalog defines `Throttle Rev Limiter` as one uint16 value with multiplier
`x*0.78125 RPM`. This converts stock `0x2580 = 9600` to 7500 RPM. The independently
cataloged speed multiplier converts `0x0708 = 1800` to 180 km/h, supporting the second
layout anchor. The working fuel-cut table at `0x934E` has a candidate Normal activation
threshold of 7650 RPM and Normal release threshold of 7450 RPM. The throttle setting is
therefore 150 RPM below fuel-cut activation and 50 RPM above fuel-cut release, consistent
with throttle intervention preceding the final fuel cut.

#### Independent exact throttle-feedback and relay anchors

`FUN_0003235C` is the exact JK08A UDS ReadDataByIdentifier handler. Its high-byte
`0x12` table at `0x2289C` provides four independent throttle-position feedback
anchors:

| DID | exact RAM word | reviewed diagnostic identity |
|---|---|---|
| `0x120F` | `0xFFFF2756` | `TP SEN 1-B1` |
| `0x1210` | `0xFFFF275E` | `TP SEN 2-B1` |
| `0x124B` | `0xFFFF285C` | `TP SEN 1-B2` |
| `0x124C` | `0xFFFF2864` | `TP SEN 2-B2` |

The pointer values are present at `0x228D8`, `0x228DC`, `0x229C8`, and
`0x229CC`. Reviewed Nissan diagnostic profiles bind the DIDs to the parameter
names, and the factory VQ35HR manual defines all four as throttle-position
sensor voltages. The manual also states that sensor 2 is converted internally,
so its displayed value differs from the ECM terminal voltage.

The second-bank processing branch is partially closed in exact code.
`FUN_0003E4CC` writes `0xFFFF2864` as `0x0400 - uint16[0xFFFF363C]`, subtracts
learned offset `0xFFFF561C`, clamps the signed correction, and writes
`0xFFFF2860`. `FUN_0003E63C` can select that corrected value into
`0xFFFF284C`; it selects the paired channel into `0xFFFF284A`, runs both
through inverse pair `0x13202`/`0x155A0`, and writes their combined result.
`FUN_0003B520` consumes `0xFFFF284A` and `0xFFFF284C` in the two-bank
ETC/airflow component.

For relay state, high-byte `0x13` table `0x229E0` maps DID `0x130A` to
`0xFFFF2C56`. The record's support pointer selects `ROM8[0x11A39] = 0x10`,
which marks bit 4 as supported. `FUN_0002E2E8` sets that bit only when
`0xFFFF24D2.bit3 = 1` and `0xFFFF4255.bit3 = 0`. Reviewed diagnostic profiles
and the factory manual identify bit 4 as `THRTL RELAY`, the throttle-control
motor relay condition determined by the ECM. This is a reported control state,
not the physical relay pin.

These anchors provide a hardware-observable feedback boundary for validating
`0x942C`. They do not create a static data edge from `0xFFFF19C6` to the
position-sensor words.

#### Controlled hardware validation

The calibration label and `x*0.78125 RPM` multiplier remain `candidate` until
the following differential test succeeds:

1. Use a chassis or engine dynamometer with an operator-controlled abort. Do
   not use stationary free revving: the independent stationary fuel limiter at
   1800 RPM can mask this path.
2. Record a stock baseline with `ENG SPEED`, `ACCEL SEN 1/2`, all four
   `TP SEN` values, `THRTL RELAY`, `INJ PULSE-B1/B2`, calculated load, and DTC
   state.
3. Change only `0x942C` from stock `0x2580` to `0x0F00`, which is 3000 RPM
   under the candidate multiplier. Keep the main fuel-cut table at its stock
   7650 RPM setting so fuel cut cannot mask the observation.
4. At nonzero wheel speed and modest stable load, sweep from below 2500 RPM
   toward 3300 RPM while keeping accelerator demand steady. Abort on a new
   DTC, `THRTL RELAY = OFF`, disagreement between paired position sensors, or
   unexpected engine behavior.
5. A positive result is coordinated closing movement in both throttle banks
   near 3000 RPM while accelerator demand remains steady, the relay remains
   on, and injection pulse remains present. Fuel pulse disappearing before
   throttle feedback moves indicates a fuel-cut or fail-safe intervention and
   does not validate `0x942C`.
6. Restore the stock word and repeat the same sweep. The intervention must move
   back out of the 3000 RPM test window.

The generated definitions expose one cell as `Rev Limit - Throttle Cut` under
`Limiters / Rev Limit`. The vendor-style name remains a candidate physical
interpretation; the definition description states the proven request boundary
and the unresolved motor-output boundary.


### Base Fuel Schedule producer, fallbacks, and calculated load

The exact JK08A image closes the runtime Base Fuel Schedule chain before the
calculated-load normalization:

- `FUN_0003A904` completes a dual-channel processing pass and calls
  `FUN_0003B252`. The latter writes
  `0xFFFF1E38 = max(0, int32[0xFFFF1DF8] + int32[0xFFFF1DFC] +
  int16[0xFFFF1E2A] + uint16[0xFFFF2368])`.
- `FUN_0003B320` runs immediately before the per-bank and combined calculations
  and completely defines signed common correction `0xFFFF1E2A`. Let
  `A = (ROM8[0x86F9] & 0x20) != 0`,
  `B = (ROM8[0x8B3F] & 1) != 0`, `C = ROM8[0x8782]`,
  `U = uint8[0xFFFF1E73]`, and `S = int8[0xFFFF56BA]`. Its branches are:
  `!A && !B -> 0`; `!A && B -> floor(C*S/32)`;
  `A && B -> preserve the prior word`; and, for `A && !B`,
  `5 <= U <= 122 -> floor(C*(U-123)/32)`,
  `133 <= U <= 250 -> floor(C*(U-133)/32)`, otherwise zero. Five SH-2E
  `shar` instructions implement floor division for negative products.
  JK08A has `ROM8[0x86F9] = 0xDC`, `ROM8[0x8B3F] = 0x18`, and
  `ROM8[0x8782] = 10`, so `A=false` and `B=false`: every stock invocation
  writes zero. The stock aggregate therefore simplifies to
  `max(0, int32[0xFFFF1DF8] + int32[0xFFFF1DFC] +
  uint16[0xFFFF2368])`.
- A complete p-code pass over all 2,315 functions found one resolved
  application-code read of `0xFFFF1E73`, inside `FUN_0003B320`, and no direct
  or computed-address writer. This absence is not required for the stock-zero
  result because the ROM flags bypass the read. `0xFFFF56BA` has two resolved
  writers. `FUN_000686B8` stores the high byte of stable-read key `0x7E` after
  `FUN_0006727C` accepts two equal reads; `FUN_000683CC` can copy
  `0xFFFF99DE` under runtime gates. The low-level primitive `FUN_00066BD0`
  uses SCI2 TDR2, SSR2, and RDR2 to read two consecutive byte addresses. The
  SH7058 manual establishes those peripheral-register identities, but neither
  the external peer nor the correction's physical quantity follows from the
  transaction mechanics.
- JK03A has byte-identical code and the same calibration bytes. The JK00D
  structural homolog at `0x3C0CC` uses `0x8713 = 0xDC`,
  `0x8B73 = 0x18`, and `0x879D = 10`, selecting the same zero-write branch.
  The JK78C structural body near `0x3FA48` uses `0x85F6 = 0xCC`,
  `0x8968 = 0x80`, and `0x866B = 0`, also selecting a zero write. The
  corresponding piecewise body has no byte-level match in 1ND0A/1ND3B, whose
  MAF chain is structurally different, so this correction semantic is not
  transferred to those ROMs.
- Unsigned auxiliary contribution `0xFFFF2368` has a closed stock lifecycle in
  JK08A. A complete p-code pass over all 2,315 functions found only reads at
  `0x3B23C`, `0x3B268`, and `0x3B29E`, with no direct or computed-address writer;
  startup initializer `FUN_00027C50` clears the containing range
  `[0xFFFF1000,0xFFFF261C)`. The complete direct-reference audit described above
  excludes every recovered DMAC transfer setup in the analyzed application. An
  unresolved computed peripheral access, external bus master, or execution
  outside the analyzed application remains beyond this static boundary, and the
  physical meaning of the disabled contribution is not assigned.
- The JK03A exact-code pair inherits the same address, readers, startup clear,
  and DMAC configuration. JK00D translates the word to `0xFFFF23E6`: structural
  consumers `0x3BFD0`, `0x3BFFE`, and `0x3C02A` provide its only three accesses
  in a complete 2,387-function p-code pass, all reads, while initializer
  `FUN_000288BC` clears `[0xFFFF1000,0xFFFF26C4)`. JK00D therefore independently
  has the same normal application-code zero result.
- The JK78C combined and total MAF structural bodies at `0x3F97C` and `0x3F9A8`
  read the translated unsigned term `0xFFFF22B8`; startup body `0x2A61C` clears
  `[0xFFFF1000,0xFFFF2564)`. Its per-bank body differs and JK78C is not present
  as an analyzed Ghidra program for a whole-program p-code census, so the
  no-writer result is not transferred. The 1ND0A/1ND3B MAF chain has no
  byte-level match for these consumer bodies, so no auxiliary-term semantic is
  transferred to SH7059.
- The primary branch of `FUN_0003B75C` uses three separate ROM scalars. Let
  `Q = uint32[0xFFFF1E38]`, `F = ROM8[0x8A27] = 109`,
  `K = ROM16[0x9284] = 26806`, `E = ROM8[0x88FB] = 3`, and `N` be the
  selected engine-speed count clamped to at least 64. The exact split multiply
  and quotient/remainder sequence is equivalent to
  `fixed = min(floor(floor(F*K*Q/256)/(E*N)), 0x726F9)`, followed by
  `0xFFFF1E40 = floor(fixed*9163/65536)`. Random equivalence testing over
  100,000 input tuples reproduced the instruction sequence exactly. The cap
  maps to 65535 after the final multiply and shift; the next input would map to
  65536, proving an intentional uint16 saturation boundary.
- Exact code establishes `0x9284` as the Base Fuel Schedule multiplier and
  `0x8A27` as a distinct airflow-unit scalar. UpRev calls the former K - Fuel
  Multiplier and states `MAF * K = BFS`; A2L calls it K-Value and supplies the
  candidate `ms/kg` unit. The separate A2L MAF Factor entry supplies uint8,
  `kg/hr`, and `x*0.0001`, and its description places it in the main fuel
  calculation as Nissan's factory alternative to changing K. Those properties
  match `0x8A27`, not `0x9284`.
- `ROM8[0x88FB]` is 3 in all six project ROMs. It also scales an
  engine-frequency calculation in `FUN_000385BC` and another schedule path in
  `FUN_0005E278`, matching the three intake events per crankshaft revolution of
  a four-stroke V6. Byte `0x89FB`, stock value `0x20`, is unrelated: its many
  readers test individual mode bits in torque and throttle functions.
- The fallback branch is selected when `uint8[0xFFFF2804] == 0`, when
  `0xFFFF4185.bit7` is set with nonzero `0xFFFF437A`, or when
  `0xFFFF4185.bit6` is set with `uint8[0xFFFF2804] < 0x20`. It looks up `M`
  from uint16 table `0x15630` by normalized coolant index
  `uint8[0xFFFF1077] << 8`, writes `M` to `0xFFFF1E44`, and writes
  `floor(M/4)` to `0xFFFF1E40`.
- Both branches calculate
  `f = min(65535, floor(0xFFFF1E40*uint8[0xFFFF1160]/128))` and write it to
  `0xFFFF1062`. Let
  `T = sat_u32(4*f*uint16[0xFFFF115C])` and
  `P = uint16[0xFFFF1F30]*uint16[0xFFFF1E06]`. With
  `ROM8[0x8D92].bit4` clear, `0xFFFF1DEE` receives the saturated
  `(T+P)>>13` result with the one-count anti-stall rule. With bit 4 set, as in
  stock `ROM8[0x8D92] = 0x7A`, it receives
  `min(65535, max(P-T,0)>>13)`.
- Under its enable gates, signed correction `0xFFFF1060` is
  `clamp_s16(arithmetic_shift7(160*(0xFFFF1DEE-0xFFFF1E06)))`; otherwise it
  is zero. Stock bit-4 processing selects `0xFFFF1DEC` either directly from
  `0xFFFF1DEE` or through
  `(c*0xFFFF1DEE + (256-c)*0xFFFF1E04)>>8`, where `c=uint8[0xFFFF1EE1]`.
  Dispatcher `FUN_000209D8` copies the 24-byte working block after every
  producer pass, making `0xFFFF1E04` and `0xFFFF1E06` the prior selected and
  unblended samples.
- When `0xFFFF2449.bit7` is clear, the nonnegative corrected candidate is
  capped by RPM/25 curve `0x12C9E`, whose byte result is shifted left by eight,
  and written to `0xFFFF1026`. When the bit is set, direct 3x4 uint8 grid
  `0x974E` supplies the word. Its rows cover RPM ranges below 800, 1600, and
  2400; 2400 RPM and above produces zero. Columns use `0xFFFF1075` thresholds
  7, 15, and 22. The stock cells are
  `36 3c 4c 61 / 32 34 40 5a / 30 31 38 54`, and the selected byte is shifted
  left by eight.

The adjacent literal-pool order `[K][MAF Factor][event scalar]` transfers across
all exact and structural project homologs:

| ROM | Engine | K-Value | MAF Factor | Event scalar |
|-----|--------|---------|------------|--------------|
| 1ND0A | VQ37VHR | `0x9106 = 26806` | `0x8939 = 133` | `0x8838 = 3` |
| 1ND3B | VQ37VHR | `0x9106 = 26806` | `0x8939 = 133` | `0x8838 = 3` |
| JK78C | VQ37VHR | `0x8F80 = 26806` | `0x8896 = 131` | `0x87AB = 3` |
| JK03A | VQ25HR | `0x9284 = 26806` | `0x8A27 = 109` | `0x88FB = 3` |
| JK08A | VQ25HR | `0x9284 = 26806` | `0x8A27 = 109` | `0x88FB = 3` |
| JK00D | VQ35HR | `0x931C = 26806` | `0x8A4D = 132` | `0x891B = 3` |

The value pattern is consistent with the roles: K remains an architecture
constant, the event scalar remains the V6 count, and MAF Factor changes with
engine and calibration. With the A2L scale, each JK08A aggregate count is
`109*0.0001 kg/hr = 0.00302778 g/s`. The independent dimensional closure is:

- `RPM = 1.5625*N`, established by the common engine-speed source;
- firmware coefficient expressed against RPM:
  `1.5625/256 * 9163/65536 = 0.0008533708751`;
- expected coefficient for `kg/hr * ms/kg`, three intake events per revolution,
  Base Fuel Schedule `raw/2048 ms`, and the quarter-BFS intermediate:
  `0.0001/60 * 2048/4 = 0.0008533333333`.

The 43.994 ppm difference is consistent with the firmware's integer conversion
constant and independently supports the A2L MAF Factor and K-Value scales. The
scales remain source-derived until hardware validation.

This closure also selects the community-measured `raw/100 g/s` conversion for
DID `0x1209` as the working candidate. Its exact producer can reach about 26,800
raw counts, so the conflicting structured-profile `raw*1 g/s` formula would
imply about 26,800 g/s; `raw/100` gives a plausible ceiling near 268 g/s.
Hardware validation remains required.

Initialization in `FUN_0002C648` uses the same `0x15630` fallback table. For
`q = min(65535, floor(M*uint8[0xFFFF1160]/512))`, it writes `q` to
`0xFFFF1062` and `min(65535,4*q)` to the working schedule words and
`0xFFFF1026`. This is the only non-runtime direct writer found by the
whole-program p-code scan.

The calculated-load path consumes the current scheduler snapshot:

- `FUN_0008083C` indexes 16-cell uint16 table `0x1491A` by
  `uint8[0xFFFF11B3] << 8`. Wrapper `FUN_000263F4` uses the complete uint16
  interpolation path below coordinate `0xF000`; the upper branch returns cell
  15.
- With lookup result `M`, it calculates
  `q = floor((uint16[0xFFFF1024] << 8) / M)`. If
  `ROM8[0x870E].bit4` is set, it additionally calculates
  `q = floor((q << 7) / uint8[0xFFFF329F])`; a zero optional divisor forces
  255. The final value is clamped to 255 and written to `0xFFFF413E`. Other
  entry gates can force 0 or 255.
- `FUN_00035856` returns `0xFFFF413E` for J1979 Mode 01 PID `0x04`, with
  standard conversion `100*A/255`.

Exact DID `0x1208` identifies the numerator and producer output as Base Fuel
Schedule, so `0x1491A` is a same-dimension 100% normalization reference and
`0x15630` is a Base Fuel Schedule fallback source. The structured homologous
Nissan profile defines the full word as `raw/2048 ms`; this makes the high-byte
tables use `raw/8 ms`. The conversion, the `Cranking` qualifier for `0x15630`,
and tuner-facing RPM-axis labels remain candidates pending a controlled
CONSULT3P or bench measurement.


### UDS SID 0x22 ignition, fuel-trim, injection, and intake-CVTC response paths

The exact JK08A UDS dispatcher and ReadDataByIdentifier handler establish the
request-to-RAM path independently of public PID lists:

- `FUN_0002F928` compares the service byte with `0x22` at `0x2F9C4` and jumps
  through literal-pool entry `0x2FB00` to `FUN_0003235C`.
- `FUN_0003235C` indexes the `0x11xx` pointer table at `0x226AC` or the `0x12xx`
  table at `0x2289C`. A normal `0x11xx` entry returns one byte. A normal `0x12xx`
  entry returns two consecutive bytes in big-endian order. Both paths emit
  positive response SID `0x62`.
- Pointer `ROM32[0x228BC] = 0xFFFF1026` binds DID `0x1208` to the newest Base
  Fuel Schedule word. The structured homologous Nissan profile names the same
  DID `B/FUEL SCHDL` and defines `raw/2048 ms`; the address binding is exact and
  the engineering conversion remains a hardware-validation target.
- Entries `0x1107`, `0x1108`, `0x1109`, and `0x110A` at pointer-table locations
  `0x226C8..0x226D4` all address byte `0xFFFF2022`. They are exact aliases for
  one firmware value, not four independent runtime coordinates.
  `FUN_0004DF82` normally writes
  `ROM8[0x83D5] - uint8[0xFFFF11D4]`, where stock `ROM8[0x83D5] = 110`.
  A community definition for DID `0x110A` uses display conversion `110 - raw`,
  exactly inverting the normal firmware transform. Other control modes add
  stock `ROM8[0x8C95] = 10` with saturation, subtract stock
  `ROM8[0x83EA] = 30` and cap by stock `ROM8[0x864A] = 80`, or force
  `110 - 20 = 90`. The single affine formula therefore describes only the
  normal response path.
- The upstream data flow closes a calibration-to-diagnostic slice:
  `0x147DA -> FUN_0004D99C -> 0xFFFF12D6 -> FUN_0004DBE8 ->`
  `0xFFFF11D4 -> FUN_0004DF82 -> 0xFFFF2022 -> FUN_0003235C ->`
  DIDs `0x1107..0x110A`. Map `0x147DA` is a `1D-8` uint16 table with stock
  values `0, 5, 6, 7, 8, 9, 10, 11` and explicit axis `0x13C48`.
  `FUN_0004D99C` interpolates it by word `0xFFFF237E`, stores the raw result in
  `0xFFFF2000`, multiplies by a selected byte coefficient, divides by 100,
  subtracts the quotient from a signed intermediate, clamps to `[-128, 127]`,
  and writes `0xFFFF12D6`. `FUN_0004DBE8` conditionally includes that correction
  while forming final internal ignition-timing coordinate `0xFFFF11D4`.
  This establishes the narrow ignition-timing correction role at `code`
  confidence. The specific operating mode, physical degree unit, and producer
  of axis input `0xFFFF237E` remain unresolved. A full p-code scan of all 2,315
  defined functions found only the read at `0x4DA82`, with no exact or
  base-plus-offset writer.
- Entries `0x1123`, `0x1124`, `0x1125`, and `0x1126` at pointer-table locations
  `0x22738..0x22744` address the high bytes of big-endian words
  `0xFFFF22DC`, `0xFFFF22DE`, `0xFFFF2302`, and `0xFFFF2304`. Exact J1979
  handler `FUN_00035856` independently identifies those words: Mode 01 PIDs
  `0x06`, `0x07`, `0x08`, and `0x09` read them in the standard order STFT B1,
  LTFT B1, STFT B2, and LTFT B2. Every branch returns
  `min(255, floor(word/200))`. Combining this transform with the standard PID
  scale proves that each internal word represents percent multiplied by 256.
  Initialization routine `FUN_000593AC` writes `0x6400`, exactly 100 percent,
  to all four words. The SID `0x22` path returns only each high byte, so the
  reviewed community conversion `raw - 100` yields signed correction percent
  with neutral raw 100.
- `FUN_0005C910` publishes STFT. It first calls the two-bank closed-loop
  calculation `FUN_0005CBEC`, whose final working words are
  `0xFFFF40AC/0xFFFF40AE`, and normally copies them to
  `0xFFFF22DC/0xFFFF22DE`. An alternate control mode takes one byte, clamps it
  to 75..125, shifts it left by eight, and writes the same forced value to both
  banks. The exact output routing and scale are established; the narrower
  physical names of internal feedback terms in `FUN_0005CBEC` remain
  unresolved.
- `FUN_0005911C` coordinates the adaptive LTFT path for parameter 0 (bank 1)
  and parameter 1 (bank 2). `FUN_0005796C` selects one Q8.8-percent cell from
  a 64-word RAM grid at `0xFFFF4B90` or `0xFFFF4B10`. The 8x8 operating-region
  index uses word `0xFFFF1024` against ROM thresholds at `0x12592` and
  engine-speed byte `0xFFFF11AE` against thresholds at `0x126DC`. The RPM
  thresholds are 0, 1000, 1500, 2200, 3400, 4400, 5400, and 6400 RPM. Selected
  cells are copied to `0xFFFF2306/0xFFFF2308`; invalid state resets all 64
  cells of the affected bank to `0x6400`.
- `FUN_00057D1E` adapts the selected grid cell through a signed step and clamps
  it to stock limits 90..110 percent from ROM bytes `0x8A9E/0x8A9F`.
  `FUN_00058168` maintains a second bank term at
  `0xFFFF5648/0xFFFF564A`. Final producer `FUN_00057B26` calculates
  `selected_cell + bank_term - 0x6400`, conditionally clamps it to 90..110
  percent using ROM bytes `0x8E5B/0x8E5A`, forces `0x6400` under fault/control
  gates, and writes diagnostic LTFT words `0xFFFF2302/0xFFFF2304`. A focused
  `TraceRamAccesses.java` pass over all 2,315 functions resolved the indexed
  stores at `0x57C2A`; all functions decompiled successfully. The physical
  meaning of the `0xFFFF1024` grid dimension and the exact learning cadence
  remain unresolved.
- Entries `0x1206` and `0x1207` point to `0xFFFF23C8` and `0xFFFF23CA`.
  `FUN_0004ECAC` calls `FUN_0004EAD4` for two base terms and then calls
  `FUN_0004EBA2` for channel indices 0..5. `FUN_0004EBA2` writes the six
  consecutive words at `0xFFFF23C8+2*i`. It selects the base by channel parity,
  adds signed correction `0xFFFF1396+2*i`, conditionally subtracts
  `0xFFFF1466+2*i`, and applies direct-indexed byte `0x129C0+i` as Q1.7 before
  uint16 saturation. All six stock bytes at `0x129C0` are `0x80`, so the
  multiplier is 1.0.
  A homologous structured Nissan profile defines them as `INJ PULSE-B1` and
  `INJ PULSE-B2` with conversion `raw/100 ms`. The VQ35HR factory manual defines
  the corresponding CONSULT parameters as the actual injection pulse width
  compensated by the ECM input signals.
- Entry `0x1135` points to byte `0xFFFF2442`. The exact firmware uses
  `0xFFFF2442/0xFFFF2443` as a two-bank centered angle pair in the
  `0x9DBA` ignition-angle path, and initializer `FUN_000BCD44` writes `0x80` to
  both bytes. Runtime writer `FUN_000BD9F0` is called for channels 0 and 1 by
  `FUN_000BD170` and writes
  `clamp_u8(0x80 + reference[channel] - capture[channel])`; a hardware-control
  branch forces neutral `0x80`. Reference bytes `0xFFFF4799/0xFFFF479A` are
  initialized from ROM bytes `0x831C/0x8321` and maintained by
  `FUN_000BDF5C`. Capture bytes `0xFFFF22CC/0xFFFF22CD` trace to ATU-II channel
  1A GR1F and GR1E processing in `FUN_0002A5CC` and `FUN_0002A36A`.
  Homologous VQ35HR sources identify `0x1135` as intake valve timing bank 1.
  Community diagnostic definitions support candidate conversion
  `raw*0.5-64 degCA`; exact code proves the centered representation but not the
  physical scale.

The exact table rejects prior community candidates `0x1211/0x1212` for injection
and `0x1127/0x1128` for intake CVTC because their entries are `0xFFFFFFFF`.
No definition or hardware test uses those unsupported identifiers.

`TraceRamAccesses.java` scanned all 2,315 defined functions over selected range
`0xFFFF128C..0xFFFF4FFF`. It resolved 29,579 exact accesses, retained 2,679
unresolved indexed candidates with concrete anchors in that range, and found
131 constant RAM call arguments. The indexed candidates expose the six-channel
injection and two-channel CVTC writers that direct xrefs miss.


### Working engine-speed fuel cut `0x934E`, FUN_0004F282 [CONFIRMED PATH]

`FUN_0004F282` directly consumes the first four uint16 words at `0x934E` as two
activation/release pairs:

| State | Column 0 | Column 1 |
|---|---:|---:|
| activation | 612 | 596 |
| release | 596 | 368 |

Stock `ROM8[0x8B38] = 0x63` leaves bit 7 clear, so the alternate words
`0x9356`/`0x9358` are outside the stock path. `0xFFFF2468.bit4` selects column 0 or 1.
With `0xFFFF2497.bit2` clear, current RPM/12.5 word `0xFFFF11BC` at or above the
selected activation threshold arms optional delay `0xFFFF24F1`; stock
`ROM8[0x8C69] = 0` activates state bit 2 immediately. While active, speed below the
selected release threshold clears the state. The returned Boolean enters
`FUN_0004ED88`, which converts any active global inhibit condition to mask `0x3F` and
writes the final six-channel injection-output mask `0xFFFF22E0`.

Exact code establishes `x*12.5 RPM` through producer `FUN_000384FE` and the snapshot
copy in `FUN_00020DFE`. The public HR A2L catalog identifies the matching 2x2 layout
as Normal/Reverse columns and Cut/Restore rows. The stock values are:

| Fuel state | Normal | Reverse |
|---|---:|---:|
| Cut | 7650 RPM | 7450 RPM |
| Restore | 7450 RPM | 4600 RPM |

Code proves the table address, 2x2 layout, RPM multiplier, hysteresis, active state,
and global six-injector inhibit path. The Normal/Reverse column labels remain
catalog-supported candidates pending CONSULT/bench validation.


### Unified rev-limiter arbitration [CONFIRMED PATH]

The complete static model is maintained in
[`JK08A.limiters.md`](JK08A.limiters.md). Periodic table `0x21970` calculates
the `0x942C` request branch at index 11, its signed-minimum arbitration at index
18, controller selection at index 20, request boundary at index 21, and
downstream inverse-coordinate stages at index 22. `FUN_0004ED88` calculates the
separate six-channel fuel-output mask at index 27.

The exact fuel-mask expression is:

```text
G = 0x3F when any global Boolean cutoff is active, otherwise 0x00
P = G | DFCO_mask | count_mask
R = runtime_replacement when enabled, otherwise P
ffff22e0 = (R | auxiliary_mask) & 0x3F
```

Main RPM fuel cut and stationary RPM fuel cut both enter `G`, so neither has
priority over the other and either produces all six bits. The runtime
replacement can substitute their result together with DFCO/count bits; the
auxiliary mask is applied after that replacement. The `0x942C` path does not
enter this expression and cannot delay or clear hard fuel cut. If its request
reduction does not keep speed below the selected `0x934E` activation threshold,
the main limiter independently asserts `0x3F` later in the same periodic pass.


### Accelerator-pedal high-state hysteresis `0x8FDC`/`0x8FDE`, FUN_00047A56 [CONFIRMED]

`FUN_00047A56` compares `word[0xFFFF266E]` with one of two thresholds:

- previous-cycle `0xFFFF246D.bit7 == 0` selects activation threshold
  `0x8FDC = 0x0262` (610);
- previous-cycle `0xFFFF246D.bit7 == 1` selects release threshold
  `0x8FDE = 0x0210` (528);
- comparison true sets current `0xFFFF246A.bit7`; comparison false clears it.

Scheduler `FUN_00020DFE` copies three current state bytes
`0xFFFF246A..0xFFFF246C` to previous-cycle bytes
`0xFFFF246D..0xFFFF246F`, closing exact activation/release hysteresis.

The compared input is a normalized dual-channel analog quantity:

```text
AN10 -> ffff362c -> ffff27a0 = sample - offset
AN17 -> ffff362e -> ffff27a4 = 2*sample - offset
                         min/clamp/rate limit -> ffff2672 -> ffff266e
```

Exact service-0x22 pointers map DID `0x120D` and `0x120E` to
`0xFFFF269E` and `0xFFFF26A2`. The same values feed exact JK08A diagnostic
monitor functions that dispatch descriptor indices for
P2123/P2122 and P2128/P2127. Homologous diagnostic definitions name the DIDs
Accelerator Pedal Position 1 and 2. This evidence establishes the accelerator-pedal
subsystem and excludes an RPM interpretation. The exact downstream meaning of the
high state, such as WOT or kickdown, remains unassigned.

The two uint16 cells remain in the graph and ledger as
`Accelerator Pedal High-State Hysteresis (0x8FDC)` in normalized ADC counts.
They are research-only and hidden from the working definitions. Adjacent words
at `0x8FD8` belong to other functions and are excluded.


### K2Y decel ignition (`mTKADVA`) - no decel-gated branch in timing calculation [CONFIRMED]

A2L `mTKADVA`, Deceleration Advance, 8 uint8, `Degrees`, static MBT axis
`[0,8..56]`, is not represented by any map in the interpolation family. Three address
facts establish this:

- Timing calculation `FUN_00082c8a`, 6060 B at range `0x82c8a..0x84436`, which uses
  base maps `0xB61A/71A/81A`, addresses no decel/cut flag base. Its range contains no
  slot for `0xFFFF24CE`, `0xFFFF246A`, `0xFFFF245C`, or `0xFFFF2468`, which have
  59/14/40/30 occurrences respectively across the ROM. Therefore, the main timing
  calculation contains no decel-gated advance branch.
- Static MBT axis `[0,8,16,24,32,40,48,56]` physically appears in ROM at `0x12389`,
  but it is the head of shared linear axis 0..128 at step 8 (`0x1238A`, 17 entries).
  `FUN_0008152a` at `0x81724` and `FUN_00081d74` at `0x81f56` read it through
  interpolator `FUN_00082090(table, axis, x)`, where
  `x = byte[DAT_00082084+0x12]`. The table is not a degree-based advance map but fuel
  enrichment, identified by ASCII label "Jccastnonqu" near `0x1236A`; its output is
  multiplied into the fuel path, not timing. The axis is shared, not specific to K2Y.
- Curves `0x1261A` and `0x1263A`=`0x12CBE` in `FUN_00082c8a` are interpolated over
  RPM axis `0x1264A` (`x*50`) and operate as window-threshold comparators. Comparing
  them with the current value enables or disables correction flags
  (`pbVar5[0x3f]`, `pbVar5[0xbb]`). They are enabling-window thresholds, not tables of
  an added timing angle.

Scope of the conclusion: decel-gated advance is absent from the main timing
calculation, and no explicit-axis map represents `mTKADVA`. Primitive `0x26370` does
appear in this calculation at slot `0x838bc`, so decel advance through implicit-axis
maps in another function is not excluded.


### 4x4 family `0xA49A` / `0xAB6A` (interp `0x26084`)

`FindTableRefs 11B60..11B90` finds accessors `0x52f00` at `0x52f58` and `0x54ee0`
at `0x54fd0`. Both load `r4`=table, `r5`=`0x11D00`, `r6`=`0x11B67`,
`r2`=`0x26084`, then execute `jsr`. Wrapper `0x26084` is 4x4. Each axis has
4 points: X `0x11D00` `[20,40,56,64]`, Y `0x11B67` `[51,102,154,205]`.
The table input is sensor `0xFFFF11AE`, also used as an ignition-axis input, making
`0xFFFF11AE` a shared axis sensor. Maps, each 16 B:

- `0xA49A`: `[26,29,45,43 / 26,24,35,42 / 26,24,36,42 / 35,38,42,42]`.
- `0xAB6A = 0xA49A + 0x6D0`: a neighboring family member with the same skeleton.

Semantics [CANDIDATE]: a small 4x4 uint8 map/limit; sensors have not been fully traced.


### 1D curve `0x129D2` (interp `0x264a0`, axis `0x11B7B`)

At `0xb997c` / `0xb9984`, `r4`=`0x129D2`, `r5`=`0x11B7B`,
`r2`=`0x264a0`, followed by `jsr`. The input is the high byte of u16 at
`0xFFFF4524`, and the result is stored in `0xFFFF329F`. Axis `0x11B7B` is
`[0,5,6,25,50,75,100,125,150,175,200,225,255]`, approximately 16 points.
Semantics remain [CANDIDATE].


### Operational semantics of `0xB33A` and `0xA29A`

- Through `FUN_000BFDC0`, `0xB33A` is an offset-encoded control table with neutral
  value 128. When `ffff2466.bit6=1`, code calculates
  `clamp_u8(this - map_0xAB4A + 128)`; otherwise it passes raw directly to
  `ffff1c5d`. The centered `x-128` operation has `code` confidence as raw arithmetic,
  not as a physical scale. The tuner definition uses candidate gasoline AFR
  `1881.6/x`, with the same expression as its inverse.
- Through `FUN_0002C648`, `0xA29A` participates in the multiplicative portion of a
  fuel calculation followed by saturation. Its geometry, axes, and constant layout
  offset `+0x5C` from EV18A `0xA2F6` identify it as Fuel Compensation Map. A2L defines
  scale `x*0.78125%`, with raw 128 = 100%.

The finisher preserves structural axis orientation. Row axis `0x11CF0` has RPM scale
`x*50`, and column axis `0x11D4C` has QH0 Flow Quantity scale `x*0.390625%`; both
physical scales remain `candidate` from A2L.


### Ignition-map axes `0x11ECE`/`0x11EBE`

Row axis `0x11ECE` contains
`[8,12,16,24,32,40,48,56,64,72,88,104,120,128,136,148]`, corresponding to
`400..7400 RPM` at scale `x*50`. Kernel `0x269C4` converts points to RPM/12.5
domain with `x*4` for comparison with RAM `ffff11bc`; the exact producer and
snapshot-copy chain raises this axis scale to `code` confidence.

Column axis `0x11EBE` contains 16 points `8..128`, corresponding to
`6.25..100%` Cylinder Filling at scale `x*0.78125`. Entry `0x26230` uses both axes
for maps `0x991A`/`0x9A1A`/`0x9B1A`.


### Accessor-interpolator FUN_0004bbee (`0x4bbee`)

`FindTableRefs 11ebe..11ece` finds one node, `0x4bbee`: `0x11EBE` is loaded as a
literal at `0x4BCCC`, and `0x11ECD` directly at `0x4BCD0`. `DumpListing` resolves
the literal pool:

- ROM tables: `0x11E9E`, `0x11EBE` (X), `0x11ECD` (Y), `0x1243A`, `0x12462`.
- RAM: sensor inputs `0xFFFF119C`/`0xFFFF2466`/`0xFFFF128C`, output `0xFFFF15ED`.

The code implements two-channel logic, branching on flag `&0x40`, with interpolation
and clamping.


### Ignition-triplet trace

`FUN_0004E1C0` passes bases `0x991A`, `0x9A1A`, and `0x9B1A` plus shared axes
`0x11ECE`/`0x11EBE` to `0x26230`. Masks `0x7F` and `0x80` split every lookup result:
the low 7 bits participate in timing correction, while bit7 is retained as a
knock-window flag. `FUN_000493E8` contains additional selection and blending of the
high-octane and high-detonation results. Constant address offset `+0x5C` from EV18A is
the same for all three maps and their A2L identities.


### Retarded-ignition calibration strategy

Tables `0x991A`/`0x9A1A`/`0x9B1A` are additive corrections to calculated MBT, not
final timing relative to TDC. The low Cylinder Filling region at medium and high speed
allows retarded combustion during overrun. Accelerator-pedal position and Cylinder
Filling use different scales: pedal position of 10-15% does not imply selecting the
10-15% filling column.

Stock overrun fuel cut remains a separate control loop. Retarded timing cannot create
exhaust combustion when injection is fully cut, so calibration is validated together
with fuel-cut state, `INJ PULSE`, actual `IGN TIMING`, and lambda. Timing-region
boundaries are made gradual, without a step between adjacent cells.

Fuel Compensation Map `0xA29A` is an independent layer. It acts over a broad
steady-state region and is not a retarded-ignition enable. Changes to this map are
validated with wideband lambda independently of the timing tables.


### Knock Slice and knock-sensor-circuit monitoring

`0x1108E` is an active 16x6 uint16 Knock Slice Map: 16 points at `400..6400 rpm` for
each of six cylinders. `FUN_00049FFC` selects the cylinder row, interpolates a
threshold, and stores it for comparison in `FUN_0004A238`. A2L defines scale
`x*0.0015259`. Value `0xFFFF` raises the threshold to the uint16 upper boundary and
practically prevents knock-count accumulation through this comparison.

`0x10F8E` has the same geometry and value structure, but a direct code xref to its bank
has not been localized. It remains `candidate` with a separate parallel-bank name.

Maps `0xABBA`/`0xABFA` do not represent AFR or transient enrichment.
`FUN_000A52E4` selects them by `byte[ffff3427] > 95`, writes the result to `ffff338a`,
and chain `ffff338a -> ffff3334 -> ffff4204` forms states
P0327/P0328/P0332/P0333. The physical map scale and direction in which a cell change
affects the final DTC verdict are unknown.

Knock Slice and monitor surfaces are not mandatory parts of a retarded-ignition
strategy. Stock knock protection remains intact unless a separate change objective is
defined and validated on the test bench.


### DTC descriptor and attribute

The main DTC descriptor table begins at `0x19360`, with a 12-byte record size.
The pointer table for uint16 attributes begins at `0x1A14C`:

```text
record(index)        = 0x19360 + index*12
dtc_code(index)      = BE16[record(index) + 6]
attribute_ptr(index) = BE32[0x1A14C + index*4]
```

Registry `JK08A.dtc.csv` contains 36 analyzed descriptor/attribute pairs for misfire,
catalyst, rear O2, rear O2 heater, EVAP, manufacturer-specific P1422, and NATS P1610.
The seven P0300..P0306 records use stock attribute `0x0030`. In 28 other emissions
records, stock attribute `0x00A0` contains bits `0x80` and `0x20`: `0x80` participates
in OBD/emissions representation, while `0x20` is used when initializing runtime
diagnostic status.

DTC suppression changes the descriptor and its associated attribute as one logical
record. Clearing only one object leaves an incomplete diagnostic state. The RomRaider
definition exposes each mutable range through a native `TableSwitch`. An ordinary DTC
therefore has adjacent `1/2 Descriptor` and `2/2 Attribute` controls in one category.
Both controls must use the same state before saving. The operation suppresses DTC
publication but does not by itself prove that the physical monitor or sensor controller
stops. Front A/F sensors are not part of the listed rear-O2/catalyst group.

The TunerPro definition represents the logical record as one reversible `XDFPATCH`.
Each ordinary record patch has a 12-byte descriptor entry and a two-byte attribute
entry, so the editor applies both ranges as one operation. P1610 has only its
descriptor entry. Seven additional patches are generated from the registry `group`
column: `catalyst`, `evap`, `manufacturer_specific`, `misfire`, `nats`, `rear_o2`, and
`rear_o2_heater`. These patches contain 4, 26, 2, 14, 1, 16, and 8 entries respectively,
covering the same 71 mutable ranges as the 36 individual patches. No patch combines
all DTC groups. Individual and group patches overlap by design and every entry carries
the exact stock bytes as `basedata`.

P1610 is at index 40: descriptor `0x19540` contains
`0D 05 00 00 00 00 16 10 00 00 00 00`, and its associated attribute is at
`0x160FE`. Its stock and disabled values are both `0000`, so P1610 suppression changes
only the 12-byte descriptor. Generator `emit_def.py` emits only the P1610 descriptor
switch in RomRaider and only the descriptor entry in both TunerPro patch scopes.


### Exact rear O2 and catalyst monitor paths

The exact JK08A descriptor indices close the rear O2 monitor paths without assigning
a physical scale to the internal working bytes:

- `FUN_00089D92(bank)` calls common fault dispatcher `FUN_0007D8B8` with indices
  `0xA7/0xA8` for P0139/P0159, `0xAB/0xAC` for P0137/P0157, and
  `0xA9/0xAA` for the path-A P0138/P0158 descriptors. The corresponding
  records are `0x19B34..0x19B70`.
- P0139/P0159 is selected when either bank-indexed byte at `0xFFFF26E9` or
  `0xFFFF26EB` is below `ROM8[0x851B] = 0x80`. P0137/P0157 is selected when
  `0xFFFF2726[bank] < ROM8[0x8ABE] = 0x24`. Path-A P0138/P0158 is selected
  when `0xFFFF2724[bank] >= ROM8[0x8ABD] = 0xFF`.
- `FUN_0008A258(bank)` implements a second high-condition path. Working arrays
  `0xFFFF42B0[bank]` and `0xFFFF42B2[bank]` reload from
  `ROM8[0x8BCE] = 5`; a zero in either array under the monitor gates dispatches
  index `0xAD/0xAE`. Exact records `0x19B7C/0x19B88` contain the second
  P0138/P0158 pair.
- `FUN_00089A88` compares the same primary values on complementary outcomes but
  calls `FUN_000B4EF8`, not common fault dispatcher `0x7D8B8`. Its call alone is
  not labeled as a pass or fail operation.

A whole-program `TraceRamAccesses.java` pass over all 2,315 defined functions found
the indexed reads and reset stores for `0xFFFF26E9`, `0xFFFF26EB`, `0xFFFF2724`,
and `0xFFFF2726`, but no direct runtime producer. `FUN_00089310` initializes the
first three values to zero and `0xFFFF2724` to `0xFF`; `FUN_0008AA46` repeats the
reset. Runtime production is pointer-mediated or otherwise unresolved. These bytes
are therefore documented as exact monitor metrics, not as raw sensor voltage or a
time quantity.

Two direct catalyst-efficiency dispatch paths are present:

- `FUN_000A2254` selects a bank from runtime state and calls `FUN_0007D8B8` with
  index `0x11` or `0x12`. Exact descriptor records `0x1942C` and `0x19438`
  contain P0420 and P0430.
- Per-bank dispatcher `FUN_000A38DC` calls metric producer `FUN_000A2D66`, limit
  producer `FUN_000A2EE4`, and evaluator `FUN_000A2F56` in order.
  `FUN_000A2D66` scales a bank byte, accumulates a saturated uint16 sum, divides
  it by the bank sample count, caps the average at 255, and writes
  `0xFFFF314D[bank]`. `FUN_000A2EE4` interpolates 1D-8 uint8 table `0x11FB6`
  by byte `0xFFFF11B2` and writes `0xFFFF2B6F[bank]`. `FUN_000A2F56` calls the
  common fault dispatcher only when unsigned metric `0xFFFF314D[bank]` is below
  that limit.

All eight stock cells at `0x11FB6` are zero. An unsigned byte cannot be below zero,
so this calibrated P0420/P0430 branch is statically unreachable in unmodified JK08A.
The independent `FUN_000A2254` result path remains present. Code proves the table's
narrow operational association and stock liveness result; it does not prove the
physical quantity, engineering unit, or the effect of changing this calibration on
hardware.


### Exact rear O2 heater circuit monitor and command status

The four exact rear O2 heater descriptors are consecutive but their high/low order
differs from the branch order in the monitor:

| Index | Record | DTC | Exact monitor condition |
|---:|---:|---|---|
| `0xAF` | `0x19B94` | P0038 | bank 1 feedback `>= 0xEC` |
| `0xB0` | `0x19BA0` | P0058 | bank 2 feedback `>= 0xEC` |
| `0xB1` | `0x19BAC` | P0037 | bank 1 feedback `< 0x0C` |
| `0xB2` | `0x19BB8` | P0057 | bank 2 feedback `< 0x0C` |

`FUN_0008B604` invokes `FUN_0008B93A(0)` at `0x8B65A` and
`FUN_0008B93A(1)` at `0x8B7C6`. The bank-indexed monitor reads
`0xFFFF2722[bank]`, compares it with `ROM8[0x8AAF] = 0x0C` and
`ROM8[0x8AB0] = 0xEC`, and calls common fault dispatcher `FUN_0007D8B8` with
the descriptor indices above. In-range state reloads `0xFFFF4293[bank]` from
`ROM8[0x8AB2] = 5`; fault dispatch is reached only when this state byte is zero.
The major exact gates also include `0xFFFF41C8` bit 7, byte `0xFFFF1108` from
`ROM8[0x8AB4] = 0x83` through 199, the selected bit in `0xFFFF2403`, the high
byte of `0xFFFF17A2 + 2*bank` at or above `ROM8[0x8A38] = 3`, and a zero
`0xFFFF42C4[bank]` state on the main path.

A whole-program `TraceRamAccesses.java` scan over all 2,315 defined functions
found direct coordinator reads at `0x8B70E/0x8B8BA` and three pointer-recovered
reads in `FUN_0008B93A` at `0x8B9D6`, `0x8BAD6`, and `0x8BB0E`. It found no
write to `0xFFFF2722..0xFFFF2723`. The feedback producer is pointer-mediated,
external, or unresolved, so the raw byte is not assigned a current or voltage
scale.

The observable command-status path is distinct from the fault-feedback path:

- The exact DID `0x130B` record at `0x22A38` returns byte `0xFFFF2C57` and
  support mask `ROM8[0x11A3A] = 0x03`.
- `FUN_0002E2E8` maps `0xFFFF2377` bit 0 to supported response bit 1. It maps
  input bit 1 to supported response bit 0 because `ROM8[0x8B2A] = 0x09` has
  bit 2 clear.
- A homologous structured Nissan P32M profile identifies response bit 1 as
  `HO2S2 HTR (B1)` and bit 0 as `HO2S2 HTR (B2)`. These physical names retain
  `nissan_family_candidate` applicability; the pointer, support mask, bit
  packing, and input bits are exact-code facts.
- `FUN_000A38DC` calls `FUN_000A25FA(bank)`, which observes the same input bits,
  maintains a per-bank latch in `0xFFFF3298`, and clears
  `0xFFFF4295[bank]` when the selected command bit is inactive.

A second whole-program scan found only the reads at `0x2E3CA` and `0xA2600`
and no write to `0xFFFF2377`. The firmware writer, MCU peripheral, output driver,
and board route therefore remain unresolved. The homologous VQ35HR factory ESM
maps ECM connector F101 terminal 17 to bank-1 `O2HR1` and terminal 33 to bank-2
`O2HR2`, describes the DTCs as heater current outside the normal range, and gives
a sensor-heater resistance of 3.4..4.4 ohm at 25 deg C. Those manual facts do not
establish continuity from the JK08A firmware state to either physical terminal.
Bench measurement or reviewed board continuity is required to close that boundary.


## Candidate areas [CANDIDATE] - require confirmation from code

- Ignition timing: trio `0x991A`/`0x9A1A`/`0x9B1A` is annotated at `code`
  confidence as Cold/High Octane/High Detonation Ignition Timing Maps. Trio
  `0xB61A`/`0xB71A`/`0xB81A` contains thresholds for the crankshaft-rotation
  nonuniformity monitor and does not enter the ignition path.
- Strong pointer anchors without attribution: `0x0975A` with 13 references and
  `0x11EBE` with 3. Pointer clusters in `0x16000..0x163xx` form a
  calibration region for fuel/torque.
- Limiter physical closure: `0x942C` has a continuous code path through the signed
  limiter arbiter and controller stages to shared request coordinate `ffff19c6`.
  Exact UDS bindings expose four banked throttle-position feedback values and the
  throttle-motor relay state, but no static path reaches a bank-specific angle command,
  motor PWM register, or ECM terminal. `0x934E` has a continuous code path into the
  global six-channel fuel-output inhibit mask; its Normal/Reverse labels and RPM scale
  still require hardware validation.


### Electronic-throttle angle/area and QH0/torque transforms

Component `0x3b498`, containing 20 maps and 22 accessors, includes the primary
target-throttle reciprocal pair `0x13202`<->`0x155a0`. Table `0x13202` is a monotonic
1D-32 uint16 angle-to-area curve, while `0x155a0` is its monotonic angle coordinate.
The same arrays exchange table and axis positions for the inverse area-to-angle lookup.
Exact duplicate pair `0x18766`<->`0x190d0` forms the parallel trustful channel.

The HR A2L catalog contains exactly two matching 1D-32 entries: `Target Throttle Valve
Opening Table` and its `Trustful` copy. Both use opening area `x*0.0008 cm^2` over TVO
`x*0.0275 degrees`. The stock primary/trustful arrays are byte-identical. The separate
catalog entry `Throttle Body Opening Area Calibration Table` has the same output shape
but no trustful partner and therefore does not explain the duplicated firmware family.

Code independently establishes the bidirectional transform. FUN_0003E548 and
FUN_0003E63C multiply two selected feedback coordinates by four, convert each through
`0x13202`, average the results in the area domain, reverse the relation through
`0x155a0`, divide by four, and write the recovered coordinate. FUN_0003B520 performs
the same forward conversion for `ffff284a`/`ffff284c` before combining the area-domain
results. Exact DID `0x124C` and its preprocessing path bind one exposed source to
second-bank throttle-position sensor feedback. The Target Throttle Valve Opening names
and engineering scales remain `candidate` until CONSULT3P or bench validation.

The same subsystem contains two 16x16 offset-binary surfaces:

- primary `0x0E98E`, with byte RPM axis `0x11D0C` and uint16 coordinate axis
  `0x14114`;
- trustful `0x175C8`, with byte RPM axis `0x18716` and uint16 coordinate axis
  `0x18AC6`.

All three primary arrays are byte-identical to their trustful counterparts. Normal
2D consumers use the surfaces in the forward direction and subtract `0x8000` from
the result before signed arithmetic. FUN_00073432 and FUN_00073628 implement the
inverse direction: each selects or interpolates a complete 16-point surface row at
the current RPM, adds `0x8000` to a signed request, searches the generated row, and
returns a value from `0x14114` or `0x18AC6`. The results are written to
`ffff1984`/`ffff198a` and `ffff1d14`.

This exact forward/inverse topology and duplicate layout match A2L `QH0/ Torque
Conversion Map` plus `Trustful`, whose description requires both maps to remain
identical. Candidate physical scales are requested torque `x*0.1-3276.8 Nm`, QH0
flow potential `x*0.00152588%`, and RPM `x*50`. Code proves offset-binary output
centering and reciprocal-coordinate use; hardware validation remains required for
the physical labels and multipliers.

Reciprocal pairs `0x15500`<->`0x15690` and `0x15540`<->`0x156d0` form an additional
piecewise conversion whose physical quantity remains unresolved. Selector bits 0/1
of `ffff23a6` choose sources for the target-throttle transform. Bit 6 of `ffff4246`
selects whether FUN_0003B468 forwards `ffff3a76` to `ffff1e60` or uses ROM default
`0x916c`. Maps `0x14cea`, `0x15082`, and `0x15062` remain live unless a disabling
branch is demonstrated. ROM[`0x83c1`].bit0 clears the alternative `0x14ea2` branch
in FUN_0007AB18 and establishes `role=dead` for that map.


### Static ignition command path to APC

The periodic scheduler table at `0x21970` establishes the calculation order used by
the timing state. Index 63 reaches map selector `0x4e1c0` through thunk `0x4e576`,
index 64 invokes knock/high-detonation coordinator `0x493e8`, index 65 invokes
transition coordinator `0x65434`, and index 70 invokes timing coordinator `0x4d888`.
The relevant order inside `0x4d888` is `0x4aad0`, `0x4af38`, the intervening state
stages, `0x4d2a6`, `0x4afdc`, `0x4bdc2`, and `0x4c136`. Index 71 function `0x62fa4`
writes `ffff23ea`; no external consumer connects that byte to the actuator path.

Selector `0x4e1c0` reads the shared 16x16 maps and writes two intermediate samples,
`ffff160f` and `ffff1610`. Bit 6 of `ffff2466` chooses hot surface `0x9a1a` when
clear and `0x9b1a` when set. Coolant-coordinate byte `ffff1071` and ROM thresholds
106 and 131 select cold surface `0x991a`, a linear cold/hot blend, or the selected
hot surface. Endpoint bit 7 is preserved with OR while only the low seven bits are
blended. The normal primary sample uses runtime coordinate `ffff102c`; the paired
sample uses `0xff` at the relevant endpoint. These surfaces feed state, control, and
limits before the engine-event command and are not direct final-angle tables.

Two static paths connect the selected hot-map state to the event command:

1. `0x493e8` independently looks up `0x9a1a` and `0x9b1a`, forms signed word
   `ffff121a`, and publishes its high byte as `ffff22fa`. The direct path is
   `ffff22fa -> 0x4d99c -> ffff12d6`.
2. `0x4af38` extracts `ffff23bd` from selected sample `ffff160f`; `0x4bdc2` writes
   `ffff1830`; `0x4c136` latches `ffff2404`; and `0x63f30` writes Q8 transition
   state `ffff23c2`. Stock ROM byte `0x8710=0x7c` has bit 5 set, so `0x4d99c`
   consumes the high byte of `ffff23c2`. This path spans multiple periodic passes.

The knock loop uses per-cylinder threshold surface `0x1108e`. Accessor `0x49ffc`
selects one of six rows and interpolates it by speed; evaluator `0x4a238` updates
event state; coordinator `0x493e8` updates `ffff2466.bit6`; and selector `0x4e1c0`
uses that bit on the following pass. Parallel surface `0x10f8e` has no direct xref.

Accumulator `0x4afdc` combines the mode-selected bases
`0x12196`/`0x1219e`/`0x121a6`, coolant-indexed corrections
`0x11f0a`/`0x11f12`/`0x11f1a`/`0x11f22`, two-bank surface `0x9dba`, and multiplier
`0x147ca`. Its final expression is
`clamp_s8(s8(ffff1514) + u8(ffff12db) + s8(ffff1511) + u8(ffff1512) +
u8(ffff1349) - 128)` at `ffff23ee`. The alternate branch of `0x4bdc2` carries
`ffff23ee` into the same multi-pass state path. A separate branch derives
`ffff1513` from `ffff2404`; `0x4e112` only moves it one count toward zero, and no
reference connects `ffff1513` directly to `ffff11d4` or an APC compare.

Engine-event scheduler `0x208f8` invokes table index 4, `0x4e162`. Its exact order is
`0x4e112 -> 0x4e0c2 -> 0x4d99c -> 0x4dbe8 -> 0x4df82 -> 0x4e080`.
Function `0x4d99c` combines map/state terms and conditional map `0x147da` into
signed correction `ffff12d6`. Function `0x4dbe8` applies mode-dependent bounds and
publishes final timing coordinate `ffff11d4`. Its conditional input `ffff564c` is a
periodic snapshot copied from `ffff56b2`; `0x4aad0` is the sole direct writer of
`ffff56b2`.

The actuator-facing chain is:

`ffff11d4 -> 0x4df82 -> ffff2022 -> 0x2a892 -> GR11A`

`ffff2022 + offset(0x4e080) -> 0x2acba -> GR11B`

The normal `0x4df82` transform is `ROM8[0x83d5] - ffff11d4`, with
`ROM8[0x83d5]=110`. The result at `ffff2022` is both the primary APC command and
the common source for UDS DIDs `0x1107..0x110a`. Function `0x4e080` calculates a
nonnegative secondary offset from `120 - ffff237a` and an optional ROM subtraction.

Capture handler `0x2b768` derives a wrap-corrected event interval and stores its
unsigned quotient by 12 at `ffff22bc`. Schedulers `0x2a892` and `0x2acba` split the
command into quotient and remainder by 10, calculate
`floor(ffff22bc * remainder / 10)`, and program `GR11A` at `0xfffff5c2` and `GR11B`
at `0xfffff5c4`. `TCNT11` is at `0xfffff5c0`, `TSR11` at `0xfffff5ca`, and `POPCR`
at `0xfffff700`. The SH7058 hardware manual establishes that low POPCR bits set the
selected PULS output on GR11A compare and high POPCR bits reset it on GR11B compare.
Firmware structure does not establish the external driver polarity, which compare
edge corresponds to spark, the physical degree scale, or cylinder-to-pin continuity
on the target ECU.

Transient table `0x11f6a` has a separate closed operational role. Function `0x7b650`
looks it up, scales the result into `ffff1393`, and `0x7b7c0` uses
`32*ffff1393` with `32*ROM8[0x8383]` hysteresis to maintain `ffff2478.bit6`.
Catalog evidence places the table in the Initial Retard Quantity family but does not
distinguish its five mode variants. No direct path from bit 6 to `ffff11d4` or an APC
compare is established. Candidate table `0x1202e` writes `ffff1ee0` and `ffff257a`;
no external readers connect either sink to the command path.

Static code establishes the software command path through both APC compare
registers. Hardware validation remains required for physical angle units, pulse
polarity, cylinder outputs, the physical qualifier of `0x147da`, and the source
semantics of `ffff237e` and `ffff237a`.


### Rate-limited raw-state and paired-output component (accessor FUN_0006205c)

Component `0x6205c` maintains unsigned Q12 accumulator `ffff33a8`. On the normal
path, `T = lookup(0x13182)`, `H = lookup(0x131a2)`, and
`S = lookup(0x133d2)`. Initialization writes `H << 12`. When `H < T`, the update
adds `S`; otherwise it subtracts `S`. Both paths clamp the accumulator to `T` when
the update crosses the target. The alternate path writes
`lookup(0x131c2) << 12` directly. Stock maps `0x13182` and `0x131a2` are
byte-identical, and every cell of `0x133d2` is zero, so the normal stock update is
neutral while the lookup remains live.

Map `0x1495a` supplies coefficient `K`; all stock cells equal 50000. Selector inputs
choose `U` from primary curve `0x1459a` or default curve `0x145ca`, after which code
forms `Q = min(floor(U * K / 50000), 65535)`. With
`A = min(ffff33a8 >> 12, 65535)`, the enabled gate publishes
`ffff33a4 = max(A, Q)` and the disabled gate publishes `ffff33a4 = A`.

A separate mode branch looks up paired maps `0x14de2` and `0x14e02`, stores their
results in `ffff2ffa` and `ffff2ffc`, and returns them through the two-word output
pair. Both maps and their shared axis `0x13b98` contain only zeros in stock JK08A,
so the live override branch publishes a zero pair.

The physical quantity, engineering scales, subsystem identity, selector meanings,
and caller-visible purpose of the output pair remain unresolved. Values near 7300
and catalog shape matches do not establish RPM, rev-limit, overrun-cut, or coolant
temperature semantics.


### RAM initialization and constant tables (accessors FUN_0002c648, FUN_00069374)

`0x2c648` is an init/reset routine called by `0x27ce4`; it fills RAM with
`0xff`, `0x80`, and defaults. Observed map reads perform one-time initialization and
do not establish semantics. A cluster of flat 1D curves shares input `ffff1077` at
`ffff1072+5`, catalog candidate coolant temperature. `0x15630` is a descending uint16
curve, catalog candidate Cranking Base Fuel Schedule. `0x69374` is a large accessor
17182 bytes long. Map `0x11f3a` is traced to a local consumer:
`interp_u8*64/125` is added to `ffff8e08`; the result with offset `0x7fbe` is saturated
to uint16 and written to `ffff8fde`. Its physical quantity is unknown. Three
byte-identical maps `0x237c4`/`0x237e4`/`0x23804` are `2^index` tables; index 1..8 is
constrained by `cmp/gt #8`, and values are 2..256. They likely serve three
channels/banks. Code establishes the integer index but not the physical meaning of
the mask.


### `0x121FE` composite calculation base curve

`FUN_0005185C` reads `0x121FE` through implicit one-dimensional accessor `0x26370`
using unsigned byte `0xFFFF106F` [CONFIRMED by code]. It independently reads
`0x121AE` and calculates:

```text
g = max(0, 8192 + (lookup(0x121AE) - 64) * uint8[0xFFFF10BF])
ffff1531 = min(255, trunc0(lookup(0x121FE) * g / 8192))
ffff1532 = min(255, trunc0(ffff1531 * ffff1528 * ffff152b / 16384))
```

`0x121FE` is therefore a base curve in a composite calculation, not an RPM
comparison threshold. The physical quantities of `ffff1531` and `ffff1532` remain
unresolved. Index `ffff106f` is the previous-cycle normalized coolant-temperature
index, but this input identity does not turn the composite curve into an Over Run
Fuel Cut threshold.


## Mass-pass Wave 2 (22 components, 4-7 maps)

Run `wf_c84014bf-ecc` covered 105 maps with adversarial validation of code claims.
Blinding held: 193 agent accesses and 0 poison-path accesses. Of 59 code-confidence
claims, 31 survived validation: maps 3/9, axes 4/10, and flags 24/40. Twenty-four were
disproven; four received no verdict because the refutation step failed and were
downgraded to candidate: maps `0x1484a` in 0x7a592 and `0x14a2a` in 0x55098, axis
`0x18e46`, and bit4 of flag `ffff24ac` in 0x72f1e. Nearly every rejection had the
same basis: trace mechanics were correct, but a physical label such as "load",
"enrichment", "target", or "low-weight" had been imported from a same-geometry catalog
entry, P6, rather than traced to the quantity. For the first time in the pass,
emittable **maps** reached code confidence, specifically Q15 blend weights, rather than
only `dead`/`threshold` roles.


### Parallel raw-output crossfade channels - `0x7a592` / `0x7a804`

FUN `0x7a592` and FUN `0x7a804` are parallel calculation channels in one raw
domain. Both consume uint16 coordinate `ffff2698` without rescaling. Their explicit
breakpoint axes `0x14f82` and `0x18f76` are byte-identical and contain
`0, 56, 112, ..., 840`. Code passes the coordinate directly as an unsigned lookup
key. The physical quantity, engineering unit, and independent axis scale remain
unresolved.

Bit 1 of `ffff249f` selects one endpoint pair in each channel:

- clear: first channel `0x1480a`/`0x1482a`, second channel
  `0x18cf6`/`0x18d16`;
- set: first channel `0x15360`/`0x15380`, second channel
  `0x19090`/`0x190b0`.

The clear-branch curves are duplicated across channels:
`0x1480a == 0x18cf6` and `0x1482a == 0x18d16`. All four set-branch
curves are byte-identical. Consequently, the crossfade weight cannot change the stock
result when bit 1 is set. Each endpoint has a code-confidence operational annotation
with raw identity scaling. This confidence asserts the selected A/B role and exact
consumer arithmetic, not a physical load, torque, fuel, VTC, or overrun identity.

Each channel forms a Q15 crossfade:
`blend = floor((A*(32768-w) + B*w)/32768)`. Map `0xd78e` supplies first-channel
weight `w` through scratch word `ffff31c8`; map `0x16f48` supplies second-channel
weight through `ffff35f4`. ROM byte `0x83c1` bit 7 selects the interpolated weight or
a constant `0x8000` source. Both weight maps contain only `0` and `0x8000`, so their
stock cells select one endpoint directly. The actual blend results are `ffff2a7c`
and `ffff35ca`; the weight scratch words are not blend outputs.

Bit 6 of `ffff245e` gates a channel-specific Q15 trim. The first channel uses map
`0x1484a`; the second uses `0x18d36`. Both 16-point maps are flat at `0x8000`, or
unity, while both lookup paths remain reachable. Common coefficient `ffff31e2`,
produced by FUN `0x7a4de`, is applied as another Q15 multiplier. Stock upper-limit
map `0x14fa2` keeps this common coefficient at unity.

Bounds and overrides produce final channel words `ffff2a7a` and `ffff35cc`.
FUN `0x79a98` coordinates common upper bound `ffff3024`, first-channel override
source `ffff3026`, and gate `ffff41f3` bit 0. FUN `0x79ba4` coordinates
second-channel source `ffff35ea` and gate `ffff4214` bit 6. The two channels publish
scaled counterparts `ffff1210` and `ffff1248` using
`floor(value*727/800)`.

FUN `0x8d194` closes the structural relationship between the channels. Under its
entry gates it writes
`ffff2c1c = abs(uint16(ffff2a7a) - uint16(ffff35cc))`; a difference greater than 26
can invoke service dispatcher `0x7d8b8` with argument `0x62` after a local countdown.
This proves parallel checked outputs without identifying the physical subsystem.


### Offset-binary axes of FUN_0005fac0 interpolators - `0x602f2`, `0x617ea`, `0x5fdb0`

These three components are interpolators called by common function `0x5fac0`, whose
body lies outside the components. Their uint16 axes use **offset-binary** storage:
zero is `0x8000`, and the search key is `0x8000 + (arg>>8)`. Code proves offset
`0x8000` twice. A pool literal is added to the key with `add r3,r6`, then cancels in
the finisher fraction `param_2 - axis_elem`, establishing `0x8000` as pure bias and
`x-32768` as a trace conclusion rather than a catalog scale. The 1D-8 shape has no
such multiplier in the catalog.

At **code confidence** in `axes.csv` are `0x15da0` for map `0x15306`, `0x15db0` for
map `0x153a0`, and `0x13a68` for map `0x14e82`. The physical delta quantity remains
unknown because `arg` comes from `0x5fac0`, so units are empty. Axes
`0x15d60`/`0x15d70` in 0x5fdb0 were rejected: the offset is confirmed by code, but
the claim confused two same-geometry twins, `0x14c9a`/`0x14cba`, with a shared hash
and assigned the wrong index, a P6 trap. Confidence was downgraded to candidate.

Path structure is code-established while physical meaning remains candidate. Four maps
form two sign-selected pairs for positive and negative argument branches. They act
multiplicatively and are unity-normalized, at 128 for uint8 Q7 and 32768 for uint16
Q15; in this calibration they are flat and neutral. Catalog 1D-8 concepts
cranking-initial/fuel-comp/fuel-target/idle-ignition identify a class but not an
identity. Content-anchor validation found no match.


### Reciprocal transfer pairs - `0x72f1e` (accessors FUN_00072f1e, FUN_00073824, FUN_00074728)

The component contains **reciprocal pairs** of tables in which each table is the axis
of the other: `{0x18e86,0x18fd6}` for the low range and
`{0x18e46,0x18f96}` for the high range, whose input is `>>4`. Branching in `0x72f1e`
selects the pair. Code establishes the structure through wrapper `0x26714`, kernel
`0x26b84`, reverse linear search, and upper boundary `[+0x3e]`. Its shape is a
wide-range linearization, candidate airflow/MAF class.

At **code confidence** structurally, axis `0x18fd6` belongs to table `0x18e86` at site
`0x7386c`. It has no scale because the kernel compares points in raw form, so it is not
added to `axes.csv`, which is the scale layer; its role is recorded here. Partners
`0x18e86`/`0x18f96`/`0x18e46` remain candidate. The reciprocal role is confirmed by
trace, but the physical quantity and unit are unresolved because RAM inputs
`ffff1d08`/`ffff1d10` lack an identified source.

Bit 6 of `ffff24ac` is a one-shot initialization latch that gates a single baseline
lookup of trustful target-throttle opening-area table `0x18766`, with test-then-set in
`0x73824`. Table `0x190d0` performs its inverse area-to-angle conversion. These arrays
are byte-identical to primary pair `0x13202`/`0x155a0`; their physical identity and
scales remain candidate. Bit 5 at `0x89fb` selects interpolation versus direct
passthrough in `0x74728`. Bit 4 of `ffff24ac`, claimed as threshold "clamp activated",
received no verdict and remains candidate.

Downstream consumers `0x73a44`/`0x74728`/`0x749bc` use trustful QH0/torque surface
`0x175c8` over axes `0x18716`/`0x18ac6` and subtract `0x8000` from its result. The
surface identity is supported by its exact primary/trustful family; the individual
consumers remain arbitration or limiter paths without a physical output sink.


### Centered two-bank bypass-relative multiplier - `0x12EDE`, `0x55098`

`FUN 0x55098` selects the fourth byte factor of a composite product from the two-bank
centered intake-cam timing pair. When `ffff246b.bit6` is set, it computes
`min(u8[ffff2442], u8[ffff2443])` and interpolates `0x12EDE` on explicit axis
`0x11BFB` through wrapper `0x264A0`. When the bit is clear, it substitutes raw `64`
in the same factor slot. The selected byte is written to `ffff1b14`.

The exact output is:

```text
ffff15ce = min(
  65535,
  u16(ffff2ff0)
  + ((u8(ffff1680) * u8(ffff193d) * u8(ffff1955) * u8(ffff1b14)) >> 12)
)
```

The map scale `x/64` is code-proven as a bypass-relative gain: raw `64` reproduces
the clear-bit factor and raw `18` contributes `18/64 = 0.28125` of that factor. The
scale does not assign an absolute fixed-point representation to all four factors or
physical units to `ffff15ce`. Axis points are raw values 48, 68, 88, 108, 128, 138,
148, 158, 168, 178, 188, 198, 208, 218, 228, and 248. Candidate conversion
`(x-128)*0.5` gives `-40..60 degCA`; the raw minimum selector and intake-cam source
pair are code facts, while the engineering conversion requires hardware validation.

Coordinator `0x57608` calls `0x55098`, `0x52F00`, `0x54EE0`, and `0x554AE` in that
order. `0x52F00` calls `0x532AE`, which consumes `ffff15ce`, and writes its 32-bit
return to `ffff15f8`. Ignition-angle accumulator `0x4AFDC` uses `ffff15f8` as a
coordinate between ROM thresholds. `0x554AE` also forms
`ffff231a=sat_u16(0x4000+ffff15f8+ffff230c+ffff15da)`. These paths establish
consumption without identifying the physical subsystem.

JK03A has byte-identical map and axis bytes at the same addresses. VQ35HR JK00D
contains homologous `FUN 0x56FC8` with the same 312-byte control/arithmetic shape,
the same 16 axis points at `0x13EB8`, and homologous table `0x1528B`. Its table uses
64/0/64 regions and its gate tests a different bit, while the minimum-bank selector,
bypass value 64, and four-factor product remain invariant.

`FUN 0x54EE0` assembles a separate saturated sum in `ffff230c`. Its first term uses
maps `0x12562`, `0x12572`, and `0x12582`; the latter two are Q6 coefficients. An
additional term uses map `0xA49A`, bytes `ffff1600` and current `ffff1b14`, and
`ROM8[0x87E8]`. Calibration byte `0x8B37`, `ffff1239`, bits 0/1 of `ffff230e`, bits
0/1 of `ffff161a`, and `ffff2485.bit1` gate individual terms. Their control-flow roles
are exact; the physical quantities of the terms remain unresolved.


### Map-variant selector flags - `0x413cc`, `0x4d2a6`, `0xbe5bc`, `0xc0d90`

A recurring pattern uses a calibration byte in ROM or RAM to select a map shape or
variant by bit. Code establishes the selector/gate role; the physical meaning of the
selection remains candidate.

- `0x413cc`: bit3 at `0x8710` selects map shape, implicit wrapper `0x26388` versus
  explicit `0x264a0` with axis `0x12778`; bit1 of `ffff244f` selects a curve pair,
  35..101 versus 27..122; bit1 of `ffff2451` gates the differential term contribution,
  multiplying by output `0x12704` with `>>3` or zeroing it.
- `0x4d2a6`: bit3 of `ffff24a9` sets at `ffff1071 >= 107` and clears at
  `ffff1071 <= 103`; bit6 sets at `ffff1071 <= 170` and clears at
  `ffff1071 >= 174`. Bit5 of `ffff2458` selects the response-curve coefficient
  branch unconditionally; with the bit clear, map `0x124b2` selects between the
  response-curve and bank-deviation coefficient branches.
- `0xbe5bc`: bit0 at `0x8616` selects a map family, implicit
  `0x12e72`/`0x12e7a` through `0x26370` versus explicit
  `0x12e82`/`0x12e8a` through `0x26474` with axis `0x11bdb`. One family is live and
  the other dead, but the artifact does not contain the byte value, so it cannot
  identify which family is dead.
- `0xc0d90`: for channel `p`, `(ffff14c8 & (p+1)) != 0` selects `0x15ad0`, while
  a clear bit selects `0x15b10`. Both maps are members of the same accessor
  component and are byte-identical in stock JK08A.


### Intake-cam-deviation ignition correction - `0x4d2a6`

`FUN_0004d2a6` writes centered correction byte `ffff1a7d`. Shared response curve
`C(x)` is map `0x125ca` over axis `0x125ba`. Three calls evaluate `T0`, `T1`, and
`T2` from coordinates derived from centered intake-cam bytes `ffff2442`/`ffff2443`
and reference bytes `ffff2324..ffff2327`.

The response-curve branch interpolates coefficient `W` from 16x16 map `0x0a4aa`
using `RPM/50` and `uint8[ffff102c] >> 3`. Its exact code-level scale is `W/512`:

```text
c0 = max(0, 64 + trunc0(W * (T0 - T2) / 512))
c1 = max(0, 64 + trunc0(W * (T1 - T2) / 512))
```

The high-`ffff102c` fallback branch interpolates coefficient `K` from map
`0x09f1a` over the same runtime coordinates. Its exact scale is `K/256`:

```text
d0 = max(0, 64 + trunc0(K * (uint8[ffff1a8d] - 128) / 256))
d1 = max(0, 64 + trunc0(K * (uint8[ffff1a8c] - 128) / 256))
```

The normal gated result is:

```text
ffff1a7d = clamp_u8(floor((c0 + c1) / 2) + min(d0, d1, 64) - 64)
```

Ignition-angle functions `0x4afdc`, `0x4bdc2`, and `0x62fa4` consume this byte
as `ffff1a7d - 64` or an algebraically equivalent centered term. Code establishes
the intake-cam-deviation and ignition path, both coefficient normalizations, and
the coolant hysteresis. The reference-byte identities, engineering degree scale,
and final calibration name remain unresolved.


### Duplicate signed-endpoint surfaces - `0x74028` and `0x7604c`

Four 16x16 uint16 surfaces form two endpoint pairs: `0x171c8`/`0x16fc8` and
`0x0de8e`/`0x0e08e`. All four have content hash `7ea800ce2e95136a`, range
`32249..50049`, and offset-binary value conversion `x-32768`. The common runtime
coordinates are:

```text
x = uint16[ffff1210]
y = uint16[ffff10d2]                              if ffff4255.bit7 == 0
y = max(uint16[ffff10d2], uint16[ffff10e2])      if ffff4255.bit7 == 1
```

Axes `0x13d14`/`0x18916` are byte-identical and span `0..727`; axes
`0x13d34`/`0x18936` are byte-identical and span `0..2000`.

`FUN_00074028` writes decoded endpoints to `ffff1cfc` and `ffff1cfe`.
`FUN_000740ae` moves Q0.16 weight `ffff1d0c` by 300 toward 0 or 65535 according
to `ffff245c.bit2`, and `FUN_000740e2` writes:

```text
ffff1cf6 = floor(((65536-w) * A + w * B) / 65536)
```

The second pair follows the same arithmetic through `FUN_0007604c`, endpoints
`ffff18ec`/`ffff18ee`, weight `ffff2420`, and `FUN_00076108`. Stock
`ROM8[0x8b3f]=0x18` passes the first gate, while `ROM8[0x89fa]=0x40` has bit5
clear and skips this evaluator and blend. `FUN_00074c08` can later blend
`ffff18e8` with `ffff18e6` into `ffff18f4` through Q0.16 weight `ffff2422`.

The endpoint maps are equal for every stock coordinate, so neither endpoint
weight changes the stock result. The physical quantity and engineering unit are
unresolved.

Axis `0x13d14` also serves as a 1D-16 identity output table for the conditional
inverse evaluator `FUN_00076AD0`. The function selects its secondary coordinate as:

```text
y = uint16[ffff1152]                              if ffff4255.bit7 == 0
y = max(uint16[ffff1152], uint16[ffff1162])       if ffff4255.bit7 == 1
```

It interpolates each row of `0x0de8e` at `y` and places the resulting 16 signed-
surface storage words on the stack. This dynamic vector is the search axis passed
to `0x264f8`; `0x13d14` is the returned-value table. The offset-binary search target
is `signed16[ffff18ea]+32768` when `ROM8[0x89fa].bit5` is set, or
`signed16[ffff3394]+32768` when `ROM8[0x8b29].bit6` is the sole entry gate. The
first inverse coordinate is stored in `ffff1f60`.

A second direct row-major surface begins at `0x0e28e`. It is not part of the
forward endpoint pair and was absent from the wrapper-based map census because
`FUN_00076AD0` reads its rows directly. The same `y` slice becomes a second dynamic
search axis; inverse lookup through `0x13d14` writes `ffff1e7a`. All 256 stock cells
are zero, so every decoded cell is -32768 and every stored search-axis cell is zero.
For a positive offset-binary target, the search reaches terminal coordinate 727.
Additional gates permit:

```text
ffff1f5e = floor((uint8[ffff3e72] * uint16[ffff1f60]
                + (255-uint8[ffff3e72]) * uint16[ffff1e7a]) / 255)
```

The selected inverse coordinate is restored into the first-channel `0..800` domain:

```text
ffff2816 = min(800, floor(inverse_coordinate * 800 / 727))
```

`FUN_000D16C2` performs the reciprocal `floor(ffff2816*727/800)` conversion before
its later state and bounds logic. This establishes code-level scaling for axes
`0x13d14` and `0x18916` as `x*800/727`; it does not identify the physical quantity.
Stock `ROM8[0x89fa]=0x40` has bit5 clear and `ROM8[0x8b29]=0x29` has bit6 clear, so
the inverse body is disabled and `FUN_00076AD0` copies `ffff2a7a` to `ffff2816`.

The mechanism is conserved outside the exact-code pair. VQ35HR JK00D keeps the
two-surface algorithm with identity table `0x160e6`, populated primary surface
`0x0f922`, and all-zero alternate surface `0x0fd22`. VQ37VHR 1ND0A keeps a simplified
one-surface inverse at `FUN_000AAB28`, identity table `0x155e2`, surface `0x0f6c8`,
and the same `727/800` range conversion. The first-channel physical quantity remains
unresolved; the rejected load-limit and torque-request labels are not reinstated.


### Offset-binary additive curve selector - `0xc0d90`

Maps `0x15ad0` and `0x15b10` are 1D-16 uint16 curves over shared axis `0x149ca`.
The axis points are `8,16,...,128`, and the runtime coordinate is
`uint8[ffff11ae]`. For channel `p` in `{0,1}`:

```text
map = 0x15ad0 if (ffff14c8 & (p+1)) != 0 else 0x15b10
ffff1a98[p] = interp_u16(map, axis 0x149ca, uint8[ffff11ae])
```

`FUN_000bced0` initializes `ffff1a98` and `ffff1a9a` to neutral `0x8000`.
`FUN_000c1dec` consumes the selected output with the parallel pair
`ffff1a86`/`ffff1a88` as:

```text
u16[ffff1a86 + 2*p] + u16[ffff1a98 + 2*p] - 65536
= (A - 32768) + (B - 32768)
```

This proves offset-binary conversion `x-32768` and inverse `x+32768`. Both maps
have content hash `1f73c08bd51a5611`, range `32778..32786`, and identical stock
contents, so selector `ffff14c8` cannot change the stock value. The physical
quantity and engineering unit are unresolved.


### Section 6 discrepancy and one-time init reads - `0x2c4f8` (accessor FUN_0002c4f8)

**Section 6 discrepancy:** catalog entry `0x12dea` is 1D-32
"Electronic Throttle Control / accel-throttle", uint16 with 7 records. The trace shows
a **descending** uint8 curve 255..0 reused by seven unrelated consumers with different
inputs. The decreasing shape conflicts with accel->throttle, and uint8 elements
conflict with catalog uint16; only the dimension matches. This is recorded as a
discrepancy and not resolved. Interpolation kernel `0x26a88` is NOT ANNOTATED for this
map, so semantics remain candidate.

Flat `0xFF` maps `0x120be`/`0x12c3a`, identical by hash, are read once during
initialization in `0x3995a` under bit2 of `ffff24b8`, an init-once latch at **code**
confidence using `tst 0x4` / `or 0x4`. Without a trace of the calibration-layer write,
content `0xFF` is ambiguous between unprogrammed flash and a saturated limit. Flat
`0x4c` map `0x12d8a` is an additive correction to peripheral word `ffff5620`.


## Mass-pass Wave 3a (18 components, 3 maps)

Of 43 code-confidence claims, 20 survived: maps 5/15, flags 15/28, and axes 0.
Twenty-three were rejected, with no failed refutations. Blinding held at 133 accesses
and 0 poison accesses. For the first time in the pass, surviving maps carry three
different code-derived scales: a Q16 weight, a 4x4 weight `x/256`, and offset-binary
trim `x-128`. Physical axes remain unresolved for all three, so the maps are recorded
in `findings.csv` but not emitted. This follows Wave 2 discipline: value scale is
derived from code, while axis semantics are not.


### Blend weights - continuation of the Q15 line - `0x1488a` (FUN_00070e4c), `0x9eca` (FUN_0007a090)

- `0x1488a`: Q16 weight for blending two 16x16 maps, A=`0x1050e` and B=`0x1070e`.
  With `w=interp(0x1488a)`, output is
  `A*(0x10000-w) + B*w >>16`. Pivot `0x10000` and shift `>>16` establish `x/65536`
  from code; the 1D-16 catalog has no such multiplier, so this is not P6. Twin
  `0x720c4` reads the same weight, making it a shared blend curve. Axis input
  `ffff1a78`, a latch of `ffff10d2` under gate bit3 of `ffff417e`, is physically
  unresolved. Content is all zero, so weight is always 0 and the blend resolves to A.
  It is inert in JK08A, but its calibration structure is valid.
- `0x9eca`: 4x4 interpolation weight in
  `bVar9*RAM(ffff2c80) + (0x100-bVar9)*RAM(ffff2c7e) >>8`, establishing `x/256` from
  code. **Section 6 discrepancy:** the 4x4 catalog gives `x*0.78125`, unity=128,
  while code gives unity=256; trace evidence `0x100-bVar9` and `>>8` prevails. The
  branch is gated by bit1 of `ffff41b7`, and the full map block by bit3 of `ffff4208`.

This continues the Wave 2 line of Q15 weights `0xd78e`/`0x16f48`/`0x18d36`.
Blending a quantity pair with a map-supplied weight is a stable HR idiom, and consumer
pivot and shift establish the scale without a catalog. The physical class of the
blended quantities remains unknown.


### Subtracted offset-binary trim - `0xab4a` applied to base `0xb33a` (FUN_000bfdc0)

4x4 surface `0xab4a` is subtracted from base map `0xb33a` when bit6 of `ffff2466`
equals 1: output `ffff1c5d = clamp((b33a - ab4a) + 0x80)`; otherwise only `b33a` is
used. Value 128 means no trim, while range 128..148 subtracts 0..20. Literal `0x80`,
the pedestal, and subtraction establish centered raw arithmetic from code. Base
`0xB33A` is also confirmed as an offset-encoded table in the same domain; physical
name Target AFR and gasoline-AFR projection `1881.6/x` remain a catalog hypothesis.
The conversion maps raw 128 to 14.70 AFR, raw 168 to 11.20 AFR, and raw 178 to
10.57 AFR. Bit3 of `ffff2468` selects the Y-axis input source:
when clear, or when bit0 of `ffff5773` is clear, normal source `ffff102c` is used;
otherwise `0xff` forces the top of the Y axis.


### Floor curves for a target quantity - `0x12908`/`0x12918` (FUN_00046938)

These are byte-identical 1D-16 maps with hash `786c40a671b09d6c`, selected by bit3 of
`ffff4250`. Output reaches `ffff171a`; consumer `0x474a4` takes
`max(uVar4, ffff171a<<3)`, making it a lower limit for quantity `ffff122a` in an
air/throttle target calculation with opening-area multipliers. Consumer max establishes
the floor role from code. The map's own scale is not derived: the consumer applies
`<<3`, but that does not establish the unit of the map itself. **Section 6
discrepancy:** catalog 1D-16 / A2L concepts load-100pct and overrun-fuel-cut conflict
with the trace, which shows a floor for a target quantity. Voting does not resolve the
conflict.


### Rich flag layer - gates and selectors around analyzed maps (15 survivors)

Wave 3a recovered dense control flow around the analyzed maps. `findings.csv` has no
columns for flags, so this log is their durable location. By role:

- **Calculation-branch gates:** bit3 of `ffff4208` enables the full FUN_0007a090 map
  block; bit1 of `ffff41b7` enables reading `0x9eca` and blending; bit3 of
  `ffff417e` latches the `0x1488a` blend input; bit6 of `ffff2466` enables trim
  `0xab4a`; bit5 of `ffff2458` enables peak-hold and implicit map `0x12042` in
  FUN_00046938; bit4 of `ffff41da`, "event already counted this pass", gates
  saturating increment of counter `ffff54ea`.
- **Neutral-fallback gates:** `ffff41d0` appears in two components, bit3 in
  FUN_000473ac and bit1 in FUN_00056bd0. It is a compensation disable/fault latch:
  when set, the accessor writes neutral `0x80` instead of interpolating maps
  `0x1233a` or special path `0x1230a`.
- **Path and source selectors:** bit6 at `0x89fb` selects a raw blend or a rate-limited
  path in FUN_00070e4c; bit1 of `ffff24d0` selects path 2 bypassing maps in
  FUN_00056bd0; bit1 of `ffff24a7` selects a rate/constant branch versus threshold
  comparison in FUN_000bdb66; bit3 of `ffff2468` selects the Y-axis input source in
  FUN_0005594a and FUN_000bfdc0; bit4 of `ffff2484` selects special path `0x1230a`
  in FUN_00056bd0; bit7 of `ffff24a2` enables blend output `ffff15eb`, while clear
  forces neutral -128.

The common pattern surrounds a calibration map with calibration bits that select a
read branch, input source, or neutral fallback `0x80`. A runtime gate does not make a
branch dead: output depends on a RAM bit while the map remains readable. `role=dead`
requires a trace showing calibration-disabled execution, not a runtime condition.


### Physical labels rejected and separated from operational semantics

Wave 3a rejected 23 of 43 earlier broadly worded claims. Trace mechanics were correct,
but physical labels had been imported from a catalog or shape. Physical names for maps
`0x1233a`/`0x12352`/`0x12dd2` in FUN_000473ac and
`0x122ea`/`0x122f2` in FUN_000bdb66 remain candidate. Narrow operational claims are
separated: `0x1233a` has `code` confidence as an unsigned multiplier in a composite
correction, with candidate scale `x/128`; `0x122ea` has `code` confidence as a
centered offset-binary table with scale `x-128`. Physical labels for
`0x1214e`/`0xa9aa`/`0x12552` in FUN_0005594a and `0xb2fa` in FUN_000bfdc0 also
remain candidate. The claim that `0xB33A` is a trim base agrees with an independent
code finding: `0xB33A` is an offset-encoded control table with neutral 128, but
physical name Target AFR is unconfirmed. The working tuner definition exposes the
candidate `1881.6/x` gasoline-AFR projection and retains `[cand]` in its units.
Physical axis inputs `ffff1024` and `ffff10d2` come from callers outside the
components, so their units do not reach `code` confidence. Input `ffff11bc` is exact
RPM/12.5 through its producer and snapshot-copy chain.

Reissue chain: five code-confidence maps are in `findings.csv`; none is emitted.
Three have scales but physically unresolved axes, while the floor maps lack a scale as
well. The definition remains byte-identical, as in Wave 2.


## Mass-pass Wave 3b (45 components, 2 maps)

Of 78 code-confidence claims, 45 survived: maps 6/13, flags 39/64, and axes 0/1.
Thirty-two were rejected. One refutation failed for `00047a56` because the
StructuredOutput retry cap was reached; under Wave 1 discipline it was downgraded to
candidate. Blinding held: 275 accesses, 265 Read and 10 Bash, with 0 poison accesses.
Code survival of 58% lies within the range of Waves 2-3a, 53%/47%; map-only survival
6/13=46% exceeds the earlier 33%. Flags raise the aggregate because control flow is
less susceptible to P6, but map survival is also increasing.


### Base multiplier - continuation of the gain line - `0x12bda`/`0x14a7a` (FUN_000b1e48)

One component contains a "multiplier * base" pair. Base table `0x14a7a`, u16 through
wrapper `0x264cc` and kernel `0x26984`, supplies the multiplicand. Multiplier map
`0x12bda`, through wrapper `0x26474` and kernel `0x26944`, multiplies it and divides
by 64. Product and `>>6` are visible in the instruction flow: `mul.l` at `0xb1ecc`,
then three `shlr2` instructions at `0xb1ed4/d6/d8`, equal to division by 64. Pivot 64,
unity at raw=64, and shift establish multiplier scale `x/64` from code rather than a
catalog. Flat value 64 means output=base and multiplier 1.0. Base `0x14a7a` has no
independent scale; bypass default 100 suggests percentage, so it remains candidate.
This is the same idiom as Q15/Q16 weights in Waves 2-3a: consumer pivot and shift
establish scale, not the physical class of the quantity. `0x12bda` is recorded in
`findings.csv` with code scale but has no annotated axis, so it is not emitted.


### Accelerator-pedal high-state comparator `0x8FDC`/`0x1473A` (FUN_00047A56)

Component `00047A56` uses raw activation/release thresholds 610/528 at
`0x8FDC`/`0x8FDE` for normalized dual-channel accelerator-pedal input `ffff266e`.
Scheduler `00020DFE` copies current output `ffff246a.bit7` to previous-cycle selector
`ffff246d.bit7`, so the pair is code-confirmed hysteresis. Twin `0x1473A` is an
interpolated variant of the same raw threshold, but calibration disables its branch
with `0000870c.bit7=0`, giving it `code/dead` from the branch trace. Proving
unreachability does not require the mathematics of kernel `0x26A60`.


### Other surviving maps - `0x12262` (FUN_00094f26), `0x1462a` (FUN_000a0ee8)

- `0x12262`: 1D-16 limit in a two-bank diagnostic monitor. Its output multiplies
  measured `*(ffff2bda+bank*2)` and is compared with ROM threshold `*(0x9070)`;
  an exceedance sets per-bank fault flags and event `0xf4`/`0xf6`. Candidate scale
  `x/128` comes from rounding constant `0x7f` before `0x224f8`; code does not confirm
  the divisor as 128 rather than 255, so no scale columns are populated.
  `code/table`.
- `0x1462a`: increment step, ramp-up, for an integrator. The interpolated output is
  added to state `ffff45a0`/`ffff45a2`, constrained to [floor..cap], and written back.
  Claim for twin `0x1463a`, a decrement step, was rejected because the symmetric path
  was not traced. State scale and unit are unknown. `code/table`.


### Rich flag layer - 39 survivors around analyzed maps

As in Wave 3a, control flow is dense. CSV has no columns for flags, so this log is
their durable location. Register banks are the same: `ffff41xx`/`ffff24xx` for
calibration bits in RAM and `0x86xx`/`0x84xx` for ROM configuration bytes. By role:

- **Master enables and input gates:** bit7 of `ffff84c0` enables the complete map-read
  path in FUN_0003c4a0 and `0002c59c`; `ffff2458` provides master enable at
  `0004fbe2` and correction enable in `0x170a`/`00044500`;
  `ffff41b0`/`ffff41b8`/`ffff41c6` provide input gates and a one-shot completion flag
  for FUN_000b1e48; `ffff41bc` is the init-once flag for filter `000befb0`.
- **Source/branch selectors:** `ffff2451` plus `ffff4185` select the path in
  FUN_0003c4a0 and `0002c59c`; `ffff10d2` selects one of two component maps in
  `00074c82`; `ffff2465`/`ffff24c2` select the calibration-limit source in
  `00062c68`; `ffff4184` selects input source/mode in `0004c1e4`; `ffff41e1` selects
  state-machine mode in `00079538`; `ffff4214` selects source local_34 in `0007b0a0`;
  ROM configuration `00008616`/`00008615` selects a map/addend in `000be32a`;
  `ffff41e5` selects a bypass constant versus interpolation in `000b1e48`.
- **Override clamps:** bits 4/5 of `ffff41fb` force output `ffff2c6c` to lower/upper
  limits `ffff413a`/`ffff4138` in `0007b2c8`; `ffff4251` forces fixed value `0x18`
  in `0004c1e4`; full-byte gate `ffff25b9` transitions OFF->ON in `0004f662`.
- **Thresholds and status outputs:** `ffff41fb` is set when uVar10 >= 800 in
  `0007af78`; `ffff4214` reports result >= 800 in `0007b0a0`; `ffff9651` is the
  comparison result for map `0x15182` in `0009cdd8`; `ffff24b4`/`ffff24c6` hold a
  monitor condition/aggregate in `00047a56`.

The pattern is unchanged: bits selecting branches, input sources, or overrides to a
limit or neutral surround a calibration map. A runtime gate is not dead: the map is
read and output depends on the bit.


### 32 of 78 rejected - the same P6, with symmetric twins not traced

Trace mechanics were correct, but physical labels came from catalogs or shapes.
Maps removed from code confidence are `0x12a22`/`0x12a2a`, multipliers with 0x80=1.0
in FUN_00071650; `0x12272`, twin of `0x12262` in FUN_00094f26; `0x1463a`, decrement
counterpart to ramp-up `0x1462a`; `0x12a8a`/`0x12a92`, debounce-threshold curves in
FUN_000bd20a; and `0xb23a`, IIR-lag coefficient in FUN_000befb0. The sole axis claim,
`ffff110e` in `00047a56`, was rejected because it is an unlabeled implicit axis.
Symmetric pairs such as increment/decrement and active/alternate curve consistently
split: one branch traces to an output, while the paired branch does not.

Five code-confidence maps from this pass remain in `findings.csv`. `0x8FDC` is emitted
as accelerator-pedal high-state hysteresis after its current/previous state and analog
source chains are closed. `0x12BDA` has a code scale but no annotated axis; the other
maps also lack complete scales and remain excluded.


## Mass-pass Wave 4 (79 singleton components, 1 map)

Of 116 code-confidence claims, 60 survived: maps 2/8, axes 2/7, and flags 56/101.
Fifty were rejected. Four refutations failed, for `000522c4`, `000659ae`,
`000a643c`, and `000bfc2e`, and two returned empty verdicts; all were downgraded to
candidate under Wave 1 discipline. Code survival of 52% lies within the Wave 2-3b
range, 53/47/58%. Map-only survival was 2/8=25%; a singleton is the weakest class
because an isolated map is most exposed to P6. Blinding held across 194 agents and
342 accesses, 333 Read and 9 Bash, with 0 poison accesses. The safety classifier did
not process component `000763e2` because of a false trigger at the Section 7 boundary.
The gap is recorded and was not filled by an extra pass.

Both surviving maps are non-emittable, one threshold and one dead. Neither surviving
axis entered `axes.csv`: one is a Section 6 "not an axis" discrepancy, and the other
is an implicit RAM input with no ROM object. The wave adds two rows to
`findings.csv`; `axes.csv` and `overrides.toml` remain unchanged.


### Diagnostic limit and dead twin - `0x12870`, `0x12e3a`

- `0x12870` in FUN_000aacc0 is a lower limit for a DTC monitor. The interpolated
  output is a threshold: measured byte `ffff16d4` below the limit increments debounce
  `ffff1846`, gated by bit6 of `ffff84c3`; at calibrated threshold `0x8b71`, it raises
  fault bit `0x04` in `ffff24a1` and calls DTC `FUN_000b4ef8(0x2f)`. The map and axis
  contain only `0x00`, so limit=0 and the fault branch is unreachable. Calibration
  neutralizes the monitor; this is not dead flash because it is connected to a live
  monitor. Scale remains candidate because the 1D-16 catalog and A2L conflict with
  the traced min-limit, so no scale columns are populated. `code/threshold`.
- `0x12e3a` in FUN_000bcd44 is an interpolated 1D-8 map with all cells equal to 5,
  not executed in this image. ROM configuration byte `0x8616` bit0=1 directs both
  accessors, `000bcd44` and `000bec52`, to twin `0x12e32` at `0x12e3a-8` with axis
  `0x11bcb`; branch `0x12e3a`/`0x11bd3` is dead. This is `code/dead` from the gate
  trace, verified three ways: C if/else, SH tst/bt, and both listings. It follows the
  same symmetric-twin pattern as Wave 3b.


### Section 6 discrepancy: the resolver treated a bias constant as an axis - `0x73432`/`0x8000`

The sweep resolver assigned `0x8000` as an axis from the `r5` snapshot before the
delay slot at site `000735ac`. The trace shows that `0x8000`=32768 is a numeric bias
constant. It is added to RAM input `ffff19c6`/`ffff243c` to recenter it as unsigned
and form the interpolation key (`000735a0` sets r5=0x8000; `000735a6` performs
add r5,r6). It is never dereferenced as an array base. The real axis is
`r15`=local_50; delay-slot instruction `000735ae` `_mov r15,r5` overwrites the
snapshot before the call. The 16 `0xFFFF` words listed as an "axis" are empty-ROM data
read at `0x8000`. This is not an axis and does not enter `axes.csv`; it is recorded as
a Section 6 shape-versus-trace discrepancy. The generated local row comes from
`0x0E98E` over RPM axis `0x11D0C`; `0x14114` is passed as the inverse lookup's value
table. The lookup converts offset-binary requested torque into the QH0 coordinate and
writes `ffff1984` or `ffff198a`. Parallel FUN_00073628 performs the same operation
with byte-identical trustful family `0x175C8`/`0x18716`/`0x18AC6` and writes
`ffff1d14`.


### Implicit axis x*2 established by code - `0x0a643c`/`ffff3510`

Interpolation index is `saturate(byte@ffff3510 << 1, 255)`: `shll` at `000a6464`
doubles it, followed by saturation to `0xFF` at `000a6468`-`000a646c`. Prescale
`x*2` comes from an actual `shll` instruction, not a catalog; the match to
"Dwell RPM Table" x*2 is irrelevant. The axis is implicit and has no catalog X Axis.
The physical quantity of input `ffff3510` is unresolved, so `scale_expr` describes
RAM-to-index conversion rather than physics. There is no axis ROM object, making this
log its durable location. Flags from the same component failed refutation, one of the
four failures, and remain candidate; only the axis claim survived.


### Flag layer - 56 survivors around candidate maps

As in Waves 3a/3b, control flow is dense and CSV has no flag columns. Banks are the
same: `ffff24xx`/`ffff41xx`/`ffff92xx` for calibration bits in RAM and
`0x86xx`/`0x87xx` for ROM configuration. Rich nodes:

- **Map read/recalculation gates:** bit7 of `ffff2464` skips interpolation in
  `0004b790`; `ffff24cc` mask 0x2 gates `0004d99c`;
  `ffff2481`+`ffff2458`+`ffff249d` form a triple read condition in `00052be8`;
  `ffff24c0` gates the entire branch in `00068cb8`; `ffff248b` selects a map path
  versus `0x8000` in `0007173c`.
- **Master gates and status latches:** `0005525a` contains master gate `ffff2458`
  plus threshold latches `ffff2492`/`ffff2493`, six flags. `0004f324` uses
  `ffff2458.bit5` as an inhibit and `ffff245d.bit6` in its readiness gate.
  In stock `ROM8[00008d92].bit3=1` mode, `00052034` writes six-channel pulse/update
  mask `ffff1220`; `00051a98` only reads the prepared per-channel bit.
- **Selectors and hysteresis:** `00071448` contains hysteresis comparators
  `ffff24a4`/`ffff24a1`, combined enable `ffff249a`, default selector `0x7fff`
  `ffff2466`, and second gate `0x870f`, five flags; `0009b816` contains init guard
  `ffff9290`, mode selector `ffff930d`, and reset gate `ffff9310`; `00056ea6` contains
  mode/override selector `ffff24a0`.
- **Threshold results:** `0005651c` uses `ffff2474`/`ffff2493` for comparisons with a
  map output; `00060fb4` stores the comparison result for map `0x12362` in
  `ffff8cb4`.

The pattern is unchanged: branch, source, and override bits surround a calibration
map. A runtime gate is not dead because the map is read and output depends on the bit.


### 50 of 116 rejected - P6, symmetric twins, and unannotated kernels

P6 dominates: trace mechanics are correct, but the physical label comes from a shape
catalog, 1D-8/1D-16, or an A2L record name and is not confirmed by trace. Symmetric
pairs, such as increment/decrement and active/alternate curve, split because one branch
reaches an output while the paired branch is a separate component outside the
boundary. Unannotated interpolation kernels reachable through jumps
`0x26944`/`0x26984`/`0x26a80`/`0x26a84` cap map-value semantics at candidate, allowing
only control flow and fully visible axis inputs to survive. Of 7 axis claims, 2
survived; neither can be written to a file, as described above.

Reissue chain: two new code-confidence maps enter `findings.csv`; neither is emitted,
one threshold and one dead, and neither has an annotated code-scale axis. Axes,
`overrides.toml`, and `maps.csv` semantics are unchanged. The definition remains
byte-identical, as in Waves 2-3b.


## Code-layer pass: unannotated-kernel hint (84 maps, 17 findings)

The pass targets maps whose interpolation kernel is not represented as a function.
Kernels `0x26944`, `0x26984`, `0x26a80`, and `0x26a84` have listings but no
pseudocode, so Waves 2-4 capped such maps at `candidate`. The artifact explicitly
declares this condition, "the kernel is provided as a listing and the trace through it
must use the listing", removing the cap. Two batches were processed: 40 singleton
components, with 16 `code` claims and 13 survivors, and 44 maps in 14 multi-map
components, with 5 claims and 4 survivors. Blinding was structural: the artifact was
the sole source, used by 84 agents with 0 violations.

This pass is tracked separately from the waves because it uses a different unit of
work, a map rather than a component, and a different population. Its rates are not
combined with wave metrics.


### Confidence is determined by map role, not component size

| role | singleton | multi-map | combined |
|---|---:|---:|---:|
| `threshold` | 11/14 | 3/6 | **14/20 = 70%** |
| `table` | 2/25 | 0/36 | **2/61 = 3.3%** |
| `dead` | 0/1 | 1/2 | 1/3 |

Population composition, not component size, explains the raw batch rates
13/40 = 32.5% versus 4/44 = 9.1%: thresholds comprise 35% of the first batch and
14% of the second. Normalized to a common role mix, both yield about 17%.

This establishes the method boundary: **with the current artifact, `code` confidence
is attainable for a threshold and practically unattainable for a table.** One
branching comparison establishes threshold meaning, so its trace is short and fully
contained in the component. A table value passes through interpolation into arithmetic
and RAM, reaching the artifact boundary before a physical quantity. Surviving claims
repeatedly state that the trace establishes role and index model but not quantity and
unit. The two surviving tables, `0x14e52` and `0x1491a`, are cases where the consumer
performs the arithmetic locally.


### Monitor and DTC limits - six maps

This is the most productive class: a map output is not substituted into an expression
but only compared, and the comparison branch leads to setting a fault code.

- `0x11f4a` in FUN_000bb844 is an upper limit for monitor `ffff10aa`, DTC `0x011a`.
  Arithmetic from the image identifies the monitored quantity:
  `Q/256 = 0.24536 * u16[ffff10aa] - 125`; constants 201 and 125 are read from the
  site listing.
- `0x23dd4` in FUN_000a71a0 and `0x23ddc` in FUN_000a773a are mismatch tolerances for
  pairs of 16-bit quantities. The first output is never written to RAM; its only
  consumers are two `cmp/gt` instructions. For the second, exceedance sets a channel
  bit and reloads a debounce timer; expiration raises DTC `0xea` / `0x115`.
- `0x11fb6` in FUN_0002c254 is a per-bank limit published externally by diagnostic
  request handler `000362d2`. All eight cells are zero, but it is not `dead`: the
  value reaches a live branch. With its gate set, verdict "within limits" is
  unreachable because unsigned comparison `ffff314d < 0` is impossible.
- `0x12a62` in FUN_000a543c is a limit for `ffff3334` that sets a sticky bit. Its role
  signature is an alternate accessor branch that places a single ROM constant
  `0x8b0a` into the same slot `ffff32ee`, making a scalar and map interchangeable.
- `0x12fc6` in FUN_000a643c is the accumulation threshold for `ffff2b80`, with scale
  `x * 2560` read directly from the consumer. Triggering is one-shot: the latch sets
  the same bit `ffff41dc` whose clear state the accessor requires before updating its
  output.


### Windows, gates, and dwell - five maps

- `0x12e62` / `0x12e52` in FUN_000a681c / FUN_000a6838 are lower and upper boundaries
  of one window over `(u16 ffff1024) >> 8`, both by axis `ffff11b3`, and both consumed
  in exactly one predicate. The upper map contains only `0xFF`, placing the limit at
  the domain maximum: it is false only for `ffff1024 >= 0xFF00`, so the window is
  lower-bounded and open above. The trace, not shape, establishes the meaning of
  all-`0xFF` here.
- `0x12e1a` in FUN_000793d2 is a three-stage threshold. Three bits of `ffff420a`
  come from `M`, `M + ROM[0x8d36]`, and `M + ROM[0x8d37]`; they gate transfer
  `ffff336b -> ffff3368`. Comparator body `000259d0` is outside the artifact, so
  comparison polarity is not proven.
- `0x11ede` in FUN_0005651c is the activation point for channel `ffff123c`.
  Hysteresis is zero in this image because ROM byte at `0x86ea` equals `0x00`.
- `0x12a32` in FUN_000507ce is an engine-speed threshold for RPM/12.5 word
  `ffff11bc` with hysteresis 16 counts. All cells equal `255`, making the threshold
  constant at 510 counts, or 6375 RPM, and the axis inert. The read is unconditional,
  so the map is not `dead`.
- `0x12136` in FUN_00056ea6 is confirmation dwell in accessor passes. This is the
  only case in the pass with a strictly established unit: the value is compared with
  an integer counter incremented by 1 each pass, so a fractional scale is impossible.


### Adaptive-correction min/max pair - `0x12954` / `0x1295c`

FUN_00044910 writes both flat maps, and both received `code` confidence for role rather
than physical meaning. Lower limit `0x12954` is read through `ffff172f` as a
**signed** byte, so `240` means `-16`; upper limit `0x1295c` is read through
`ffff172e` as unsigned and applied as `min(value, 2*cell)`. The window in this image is
`-16..+256`. Sign interpretation comes from code: a min/max pair with different sign
handling itself rules out unsigned reading of the lower boundary, which would produce
window `240..256` for a loop step of `+/-1`. Monitor `00054152` independently confirms
the association by checking
`(short)[ffff1230] == (int8)[ffff172f]`.


### Two tables whose consumer arithmetic closes the scale

- `0x14e52` in FUN_00064a1c is the new-value weight of an aperiodic filter:
  `new = (target*K + prev*(0x10000-K)) >> 16`. Complement to `0x10000` and
  16-bit shift establish unity arithmetically without a catalog. Dump values are
  decimal: listing annotation `[=1f401f40]` means `0x1f40 = 8000` and
  `K = 0.1221`, not `0.5`.
- `0x1491a` in FUN_0008083c is the 100% reference for calculated load. This is the
  pass's only map with an external association: the division result reaches
  `ffff413e`, calculated load for J1979 mode 01 PID `0x04`. Dispatcher `00035856`
  returns it as a byte, and it also enters freeze-frame data. The trace establishes
  relation `load[%] = 100 * (ffff1024 * 256 / x) / 255`. Exact DID `0x1208`
  identifies `ffff1024` as current Base Fuel Schedule. Scale `x/2048 ms` is shared
  by the HR catalog and a structured homologous Nissan diagnostic profile, so
  `scale_conf = candidate` until hardware validation.


### Dead branch proven by an image byte - `0x122b2`

Its sole read site lies behind conjunction `(ROM[0x893f] & 0x10) != 0` AND
`(ffff41e5 & 0x04) != 0`. Byte `0x893f` in the image equals `0xc0`, so bit `0x10`
is clear. The address is in flash and code does not rewrite it, making the branch
unreachable. Both condition branches lead to live twin `0x12282`, which has the same
profile shifted by one cell. `dead` role comes from the branch trace and image
constant, not value shape.


### An empty consumer section is declared, not omitted

`code` confidence requires a trace to a consumer. A map without an "Output consumers"
section is counted in the denominator with no chance of entering the numerator. In the
44-map batch, 9 maps had no section and none survived. For four maps,
`0x9e8a`, `0x12c9e`, `0x14cea`, and `0x15062`, the section was built for the component
and disappeared when narrowed to the map. The pass's headline rate is calculated over
the 35 maps with consumers.

The section is always printed, and an empty query states why it is empty. There are
three distinct cases that silence previously made indistinguishable: the accessor
does not write RAM at all, so the trace ends there and output returns to the caller or
is compared in place; a written value has no reader outside the component because the
branch is dead or the accessor itself reads it; or readers lie above the shareability
cutoff because the register is a bus and its consumers say nothing specific about the
map. The second and third cases print a register table with external-reader counts.
For `0x14cea`, nobody reads five of six written registers, while fifteen functions read
the sixth.


### Consumer-pseudocode budget does not suppress confidence

For each map, the artifact prints the complete consumer table but limits C pseudocode
to the 24 most specific consumers and declares the cut. Survival where the budget cut
the list is higher than where it did not, 2/13 versus 2/31. The cut sorts by ascending
reader count for the linking register, so the list head remains closest to the map
output.

Reissue chain: 17 new `code` rows enter `findings.csv`; both `table` maps are emitted,
`0x1491a` and `0x14e52`. Fourteen `threshold` and one `dead` map are non-emittable by
construction because the gate requires `table` role. The definition grows from 7 to
9 tables, and `overrides.toml` receives two name/category records. `0x1491a` has a
catalog scale and is emitted with suffix `[cand]`; `0x14e52` has a scale derived from
consumer arithmetic and is emitted without the suffix. Axes are unchanged.

One finding concerns the manual layer itself. Geometry, family, and accessor do not
belong in `findings.csv`; the inventory supplies them, and repetition would create a
second source for one fact, which the loader rejects. Scale follows the same design:
`scale_expr` and `to_byte` contain pure arithmetic whose invertibility is checked by
substitution, while prose belongs in `note`. Identity `x` with `units = raw` means
code applies no multiplier and carries no confidence. It is a refusal to assert a
scale, not a `candidate` fact.


### Map role cannot be predicted statically

The pass would cost four times less if a threshold could be distinguished from a table
before launching an agent: `code` survives for thresholds in 70% of cases and for
tables in 3.3%. Signals were tested on an unbiased sample of 74 maps for which an agent
returned a role regardless of whether refutation later accepted the claim. The sample
contains 17 thresholds, 23%.

| signal | separation |
|---|---|
| access family | `explicit` 0/13, `implicit` 17/61 = 28% |
| flat values | flat 32%, non-flat 16% |
| singleton map in component | 33% versus 12-17% |
| accessor size | < 256 bytes 28%, 1 KiB and above 12% |
| output comparison in consumer | top 15 by comparison share: 47%, containing 7 of 17 thresholds |
| comparison of associated quantity in accessor | threshold: 7 comparisons versus 2 counts; table: 9 versus 7 |

The last row is measured after output attribution, on the map quantity itself rather
than a mixture of quantities in a broad accessor. Its lift over the base rate is only
1.26x. Granularity does not separate the classes and is not the cause.

No signal improves precision enough to change pass economics. An apparent 89%
threshold rate among `implicit` maps when the same sample is restricted to `code`
confidence is selection bias: a threshold survives refutation twenty times more often
than a table, so the survivor pool is saturated with thresholds.

The cause lies in the role definition. A threshold is defined not by the presence of a
comparison but by where that comparison leads in control flow: a fault code, sticky
bit, or gate. Nearly every ECU quantity is compared somewhere for limiting, validity
checking, or saturation. Consumer syntax does not carry the distinction.


### The second consumer ring is too large; output attribution is the bottleneck

Graph measurements of tracing beyond the first RAM write show that a median map's first
consumer ring contains 5 functions and 4.2 KiB of machine code, while the second
contains 89 functions and 66 KiB, 11.4x more code. Pseudocode is 5-7 times longer than
machine code, and pass cost follows line count, so the complete second ring does not
fit in the artifact.

Pool resolution extracts from the first ring the expressions with which a consumer
touches an accessor output, using `pool()` in `tools/sweep/build_artifacts.py`.
The access resolves for 246 of the measured 384 maps, and 218 expressions contain
arithmetic. On the control pair of surviving tables, the cut succeeds only halfway:
for `0x1491a`, it shows external publication of `ffff413e` and comparisons over it;
for `0x14e52`, it shows unrelated flag registers because the accessor itself calculates
the Q16 multiplier.

Both failures have one cause: without output attribution, it is unknown which register
written by an accessor carries the value of a specific map. A broad accessor writes
dozens of registers, with a ROM-wide maximum of 274, and all downstream evidence is
diluted across them.


### Output attribution is recovered from pseudocode

The RAM register receiving a map quantity is derived from accessor text by
`attribute()` in `tools/sweep/build_artifacts.py`: the wrapper is called with the map
base as its first argument, its result is bound to a name, and assignment of that name
to memory appears as a statement. Attribution requires no new Ghidra run; it evaluates
pool-literal arithmetic over the existing export.

The resolution key is an alias. The decompiler places a base into a local variable once,
such as `iVar3 = DAT_0002c7c8;`, and then addresses through it. The expression is
therefore searched as written rather than by pool name. Offsets can also be decimal,
such as `iVar3 + 100`.

Coverage is 254 attributions over 586 `ACCESSES` edges and 222 maps of 439; within the
open worklist, 197 of 396. Site outcomes: 190 sinks are confirmed by graph
`USES{W}` edges; 88 are resolved where no edge exists; 46 writes target an address
assembled in a register; 27 values are not bound to a name; and 135 traces end before
memory.

Cross-validation is independent. All 190 sinks known to the graph are marked by it as
writes from the same accessor, 190 of 190. Attribution uses ROM-literal arithmetic,
while graph annotation uses Ghidra reference analysis, and they agree completely.

The trace boundary is defined by reassignment count, not textual distance. Unrelated
statements can lie between the call and write while the value remains the same
variable. On JK08A, boundary values 2, 3, 4, and 6 all yield the same 254 attributions,
so the 135 terminations are a property of code rather than the cutoff.

For attributed maps, the median consumer count falls from 6, maximum 207, to 0,
maximum 9. Artifact volume across the complete open worklist falls from 48.9 MiB to
39.3 MiB, and the median from 85 KiB to 68 KiB.


### Most map outputs have no reader

For 162 of 222 attributed maps, the output register has no reader outside the accessor.
The quantity is either consumed locally or not consumed at all.

A check for an incomplete read index confirms the result. RAM accesses recovered from
pseudocode with the same arithmetic produce 4650 addresses across 731 functions and
add 2819 accesses absent from the graph, where Ghidra creates no reference for a base
assembled in a register. Direction agrees in 6732 of 6840 overlapping cases. On the
combined index, the number of maps without external consumers changes only by a few.

A window based on write width does not change the result either. A 16-bit quantity
occupies two bytes, and a half-value reader accesses the neighboring address, but this
adds readers for only a few maps. Expanding the window to +/-3 addresses removes
zero-reader cases but also includes adjacent structure fields, which are different
quantities rather than the same one.

This identifies where to look for meaning: for most maps, evidence lies in the accessor
and its call sites rather than a consumer ring. Their consumer section is empty because
of current code state, and the artifact declares this instead of omitting it.


## Pass with output attribution and callee contracts (50 maps, 9 findings)

The pass covers the first 50 rows of the 396-map open worklist. One map is the unit of
work, and the artifact is narrowed to its accessors. Attribution associates a wrapper
call output with a specific RAM register; arithmetic-library contracts close calls for
which Ghidra does not recover register arguments. The artifact remains the agent's sole
input, and blinding validation passed for all 50 maps.

Two batches produced 12 `code` claims, 9 of which survived adversarial validation:
`0xAB0A`, `0xB23A`, `0x9F1A`, `0xC98E`, `0x12312`, `0x124B2`, `0x131A2`,
`0x14114`, and `0x1469A`. Three claims were rejected: `0xC78E`, `0x12292`, and
`0x133D2`. In all three, role, index, and attribution were confirmed while physical
identity was rejected. The harness's mechanical layer is reproducible; the boundary
lies in naming the quantity.

| slice | maps | `code` claims | survived |
|---|---:|---:|---:|
| batch 20 | 20 | 5 | 4 |
| batch 30 | 30 | 7 | 5 |
| without external consumers | 22 | 10 | 8 |
| with external consumers | 28 | 2 | 1 |
| with output attribution | 31 | 10 | 8 |
| without output attribution | 19 | 2 | 1 |
| combined | 50 | 12 | 9 |

Cost was 5,480,410 agent tokens, or 109,608 per map. `code` claims occurred for 45% of
maps without external consumers, 10 of 22, and 7% with consumers, 2 of 28. A chain
closed within the accessor reaches physical meaning more often; a chain through RAM
hits the artifact boundary.

Blockers among 23 candidate maps in the second batch are not mutually exclusive:
15 lack a writer for the input cell, 12 lack a next-hop reader, 10 lack caller code,
and 7 have incomplete listing or pseudocode. Caller code was added to the artifact:
80 unique callers cover 343 of 396 maps, and all decompilations are prepared. The
remaining writer blocker consists of overlapping wider writes and writes through a
pointer argument; neither creates a direct WRITE xref to the specific cell.

The manual layer contains 64 findings. Nine results from this pass have `code`
confidence: seven `table`, one `threshold`, and one `dead`. The catalog contains
54 maps at `code` and 385 at `candidate`. No rejected claim remains in the manual
layer.


## Claim-specific-evidence pass, positions 50-79 (30 maps, 9 findings)

The dynamic workflow processes the next 30 rows of the frozen worklist without a
global barrier: analysis of each map immediately advances to adversarial validation of
its independent claims. The run completed 30 analyses and 21 validations, totaling
51 agents and 5,333,121 tokens. The blinding audit covers all 51 transcripts:
119 `Read` calls address only the assigned artifact path, 51 calls use
`StructuredOutput`, and no other tools or paths appear.

The harness returns 6 surviving Map semantics claims, 17 Map scale claims, and
17 Axis scale claims. These counters validate fields and syntax but do not authorize
writes. Preflight of all 40 ranked claims against `provenance.py`, canonical CSV, and
the live graph shows that only 2 claims are fully resolvable before synthesis, while
102 address tokens lack a valid claim identity. Primary causes are an instruction site
recorded as `writes`/`consumer`/`trace` and a reference to `@scale_conf` on a `Func`
or `Reg`, which has no such property. Synthesis preserves direct instructions as
`site` terminals, map dependencies through `@structural`, and division calls through
the existing `Func.contract_conf`.

Nine rows enter `findings.csv`:

- Map semantics `code`: `0x1495A`, normalization multiplier `/50000`; `0x14EA2`,
  statically unreachable alternative; `0x14FA2`, upper raw limit; `0x153F0`,
  Q12 multiplier; and `0x18C76`, zero additive correction to `0x18C96`.
- Map semantics `candidate` with Map scale `code`: Q7 multipliers
  `0x150F2`/`0x15112` and offset-binary pair `0x18DE6`/`0x18E06`.
- Seven new Map scales at `code`: `/50000`, two `/128`, `/4096`, and three
  `x-32768`.

Synthesis does not transfer three classes of formally surviving results:

- The automated claim assigns `role=dead` to `0x14BCA`, but its disposition is
  `writes`: two sites write `ffff282e`, and a direct-address scan finds no reader.
  The claim does not enter the manual layer. The runtime block snapshot in
  `FUN_00020DFE` publishes `ffff282e` as `ffff272a`, which has seven reads in four
  EVAP functions; the complete manual finding is recorded below.
- Conversion for `0x14CCA` is `(255-min(x,255))/255`. Its clamp cannot be expressed
  exactly as an invertible arithmetic pair in the `load_maps.py` vocabulary, so it
  remains in the artifact instead of becoming a CSV scale.
- Nine Map scale and all 17 Axis scale claims are raw identity `x`. Identity asserts
  no physical unit and receives no `scale_conf` under the loader contract. The 17
  claims cover 12 unique axes, so no row is added to `axes.csv`.

The manual layer contains 73 findings: 59 `code` and 14 `candidate`. Semantics are set
for 69 maps and scale for 44; the open worklist contains 368 `candidate` maps without
semantics. A full ingest creates 482 ranked claims and 682 `RESTS_ON` edges. Exact
audit reports `missing=0`, `extra=0`, `duplicates=0`, and `unresolved=0`. Effective
downgrade remains 109, ungrounded 110, cyclic SCCs 49, and ungrounded SCCs 10.
The 16 new source claims are grounded; report-only debt for older Map/Axis claims
remains 83. RomRaider XML remains byte-identical because the nine new findings fail
the axis-semantics gate or have `threshold`/`dead` roles.


## Claim-specific-evidence pass, positions 80-109 (30 maps, 30 findings)

The dynamic workflow processes 30 rows of the frozen worklist. Thirty analyses advance
immediately to 15 adversarial validations of original `code` claims. Synthesis narrows
physically unresolved responses to verifiable operational semantics; five promoted
claims and `0x11F3A` separately undergo six more blind validations. The strict loop
contains 51 transcripts and 5,081,565 agent tokens. The blinding audit records 91
`Read` calls to the assigned artifact path only and 52 `StructuredOutput` calls:
51 successful results and one retry after truncated JSON. No other tools, paths, or
violations appear.

The primary workflow returns 11 confirmed Map semantics `code`, seven Map scale `code`,
and no Axis scale. Before normalization, 42 ranked claims contain 47 unresolvable
address tokens; 22 claims resolve fully, and nine adversarial survivors are also fully
resolvable. Synthesis replaces instruction targets with `site` terminals,
unannotated Func/Reg/Map/Axis targets with `@structural` dependencies, and arithmetic
helpers with existing `@contract_conf`. The final layer contains 41 new ranked claims
and 121 resolvable address dependencies.

All 30 maps in the batch enter `findings.csv` with narrow wording:

- 16 Map semantics at `code`: three-factor multipliers `0x11EFA`/`0x11F02`,
  correction `0x11F3A`, divisor `0x11FD6`, saturating-decrement step `0x1200E`,
  Q7 multipliers `0x1205A`/`0x1221E`/`0x122AA`, thresholds `0x12116`/`0x12362`,
  centered table `0x122EA`, composite multiplier `0x1233A`, and four `/100`
  coefficients `0x123EA`/`0x123F2`/`0x123FA`/`0x12412`.
- 14 Map semantics at `candidate`: mutual and piecewise-linear 1D-32 pairs plus three
  conditional parameters `0x15BF0`/`0x15C40`/`0x15C80`. Their operational structure
  is established, but the physical quantity is unknown.
- Ten Map scales at `code`: `x/65536` for `0x156D0`, `x*16` for `0x18E46`, three
  `x/128`, `x-128` for `0x122EA`, and four `x/100`. Scale `x/128` for `0x1233A`
  remains `candidate`.
- No Axis claims are added because physical inputs of every axis in the batch remain
  raw.

Catalog identities Throttle Flow Potential, Opening Area, QH0, accel-throttle, and
their physical scales are not transferred. Code establishes mutual pairs and
arithmetic but does not select a physical endpoint. Path-specific `x16`, `>>2`, clamps,
and conditional branches are not declared as a common map scale. Identity `x` is
retained only with `units=raw` and `to_byte=x`; when the unit is unknown, all scale
fields remain empty.

The post-batch snapshot contains 103 findings: 75 `code` and 28 `candidate`.
Catalog Map confidence is 75 `code` and 364 `candidate`; semantics are defined for
99 maps and scale for 59. The ledger contains 338 `candidate` maps without semantics.
A full ingest creates 523 ranked claims and 810 `RESTS_ON` edges. Exact audit reports
`missing=0`, `extra=0`, `duplicate_expected=0`, `duplicate_actual=0`, and
`unresolved=0`. Effective downgrade is 110, ungrounded 110, cyclic SCCs 49,
ungrounded SCCs 10, and report-only Map/Axis debt 83. The RomRaider generator emits
9 tables and two supporting axes; 430 maps fail the gate. Generated XML is
byte-identical to historical `08a5b04:defs/JK03A.xml` because the new tables lack
annotated axes or an independent physical scale.


## Claim-specific-evidence pass, positions 110-139 (30 maps, 30 findings)

The primary dynamic workflow completes 30 analyses and 14 adversarial validations:
44 agents and 4,401,915 tokens. Strict audit of all 44 transcripts records 82 `Read`
calls to the assigned artifact path only, 44 successful `StructuredOutput` calls, and
no other paths, tools, or blinding violations. Additional blind validation of 14
narrowed or promoted claims takes 15 attempts. Fourteen transcripts are valid; one
attempt for `0x1252A` ends with a network error before `StructuredOutput`, and a
separate retry returns a complete result without violating blinding. The `code` claim
for `0x1245A` is rejected: local operations `256-x` and multiplication are visible,
but there is no continuous machine trace from map bytes through interpolation helpers
to `r0`. The other 13 additional claims are confirmed.

Output-binding validation reveals a position-dependent alias for a local RAM base in
Ghidra pseudocode. For `0x125B2`, a global alias incorrectly associates an early write
with `ffff2500`, while base `ffff1ff4` and offset `0x0224` at the write position yield
`ffff2218`. The resolver stores an alias snapshot before every statement and includes
the statement position in the address-expression key. The change affects
output-binding metadata in eight artifacts: `0x1252A`, `0x125A2`, `0x125B2`,
`0x128B0`, `0x12A42`, `0x12A7A`, `0x12B52`, and `0x12C1A`. Two independent builds of
the corrected set are byte-identical. Regression tests cover reassignment of a local
base and verify that a comparison does not clear the active alias.

Synthesis converts instructions to `site` terminals, ordinary dependencies to
`@structural`, and arithmetic helpers to `@contract_conf`; self-dependencies are
removed. The final proposal contains 30 of 30 valid rows and 170 resolvable address
dependencies against canonical CSV, `provenance.py`, and live Memgraph.

All 30 maps in the batch enter `findings.csv`:

- 23 Map semantics at `code`: `0x1252A`, `0x12532`, `0x12552`, `0x12572`, `0x12582`,
  `0x1259A`, `0x125A2`, `0x125AA`, `0x125B2`, `0x128B0`, `0x12964`, `0x12984`,
  `0x12A1A`, `0x12A42`, `0x12A7A`, `0x12A8A`, `0x12A92`, `0x12AE2`, `0x12AF2`,
  `0x12C12`, `0x12C1A`, `0x12C4A`, and `0x12D0A`.
- Seven Map semantics at `candidate`: `0x1245A` plus six mode-selected maps sharing
  sink `ffff3373`, `0x12B2A`, `0x12B32`, `0x12B3A`, `0x12B4A`, `0x12B52`, and
  `0x12B5A`. The artifact does not prove the reaching definition or absence of clobber
  from a specific branch to later consumers.
- 11 Map scales at `code`: three `x/100` for `0x1252A`, `0x12532`, and `0x12964`;
  three `x/128` for `0x12552`, `0x12A1A`, and `0x12A7A`; two `x/64` for `0x12572`
  and `0x12582`; `(x-128)/64` for `0x12A42`; `x/256` for `0x12C4A`; and `x*2` for
  `0x12D0A`.
- No Axis claims are present because input physical units are unknown.

The manual layer contains 133 findings: 98 `code` and 35 `candidate`. Catalog Map
confidence is 98 `code` and 341 `candidate`; semantics are defined for 129 maps and
scale for 89. The ledger contains 308 `candidate` maps without semantics. A full
ingest creates 564 source claims and 1001 `RESTS_ON` edges. Exact audit reports
`missing=0`, `extra=0`, `duplicate_expected=0`, `duplicate_actual=0`, and
`unresolved=0`. Effective downgrade is 100, ungrounded 108, cyclic SCCs 46,
ungrounded SCCs 9, and report-only Map/Axis debt 83. The RomRaider generator emits
9 tables and two supporting axes; 430 maps fail the gate. Control XML generation is
byte-identical to historical `08a5b04:defs/JK03A.xml`.


## Claim-specific-evidence pass, positions 140-169 (30 maps, 30 findings)

Two independent builds of 30 blind artifacts are byte-identical. The primary dynamic
workflow performs 30 analyses and 11 adversarial validations. The analysis attempt for
`0x14A3A` ends with a network error before `StructuredOutput`; a separate blind retry
returns a complete result. Additional refutation validates 16 narrowed claims,
confirming eight and rejecting eight. The validation attempt for `0x13CE8` ends with
the same network error and is completed by a separate blind retry. The strict loop
contains 59 attempts, 57 completed transcripts, and 5,193,838 agent tokens. Audit
records 87 `Read` calls to the assigned artifact path only and 57 successful
`StructuredOutput` calls; the two failed attempts are not counted. No other tools,
paths, or blinding violations appear.

Synthesis converts instructions to `site` terminals, ordinary dependencies to
`@structural`, and arithmetic helpers with known contracts to `@contract_conf`.
Self-dependencies and references to missing graph nodes are removed while exact
instruction anchors are preserved. The final proposal contains 30 of 30 valid rows
and 150 resolvable address dependencies. Grammar and numeric round trips for every
nontrivial scale pass validation.

All 30 maps in the batch enter `findings.csv`:

- 14 Map semantics at `code`: blend coefficient `0x12F7E`; thresholds
  `0x12DB2`/`0x13528`/`0x14CAA`/`0x14E92`; internal multipliers and corrections
  `0x12DAA`/`0x13CE8`/`0x1452A`/`0x1453A`/`0x1454A`/`0x147CA`/`0x14CBA`/`0x14E42`;
  and normalization denominator `0x14AFA`.
- 16 Map semantics at `candidate`: `0x12D82`, `0x12E32`, `0x12E82`, `0x12E8A`,
  `0x13468`, `0x1463A`, `0x147DA`, `0x14A3A`, `0x14A4A`, `0x14C1A`, `0x14C2A`,
  `0x14C9A`, `0x14E82`, `0x14F32`, `0x14F42`, and `0x14F52`. Code establishes
  shape, a write, or local arithmetic, but a complete machine trace or physically
  named consumer is absent.
- Four Map scales at `code`: `x/256` for `0x12F7E` and `x-32768` for
  `0x14C2A`, `0x14CAA`, and `0x14E92`.
- Seven Map scales at `candidate`: `x*0.3575` for `0x12DAA`/`0x12DB2` and
  `x*0.000488` BFS for `0x14A3A`/`0x14A4A`/`0x14C1A`/`0x14E42`/`0x14F32`.
- Four Axis scales at `code`: `x/256` for `0x15C30`,
  `x-32768` for `0x15D60`/`0x15D70`, and `x-32768` for `0x13A68`, augmented with
  exact `site` evidence. Physical input quantities remain raw.

The post-batch snapshot contains 163 findings: 112 `code` and 51 `candidate`.
Catalog Map confidence is 112 `code` and 327 `candidate`; semantics are defined for
159 maps and `scale_expr` for 119. The ledger contains 278 `candidate` maps without
semantics. A full ingest creates 616 source claims and 1192 `RESTS_ON` edges. Exact
audit reports `missing=0`, `extra=0`, `duplicate_expected=0`, `duplicate_actual=0`,
and `unresolved=0`. Effective downgrade is 100, ungrounded 101, cyclic SCCs 45,
ungrounded SCCs 8, and report-only Map/Axis debt 82.

The RomRaider generator emits 13 tables and two supporting axes; 426 maps fail the
gate. The batch adds four neutrally named internal calibrations: `0x13CE8` and
`0x14CBA` at `code`, and `0x14C9A` and `0x14E82` at `candidate`. XML comments preserve
narrow operational semantics and assign no physical quantity. Repeated XML generation
is byte-identical to historical `08a5b04:defs/JK03A.xml`.


## Claim-specific-evidence pass, positions 170-199 (30 maps, 30 findings)

Two independent builds of 30 blind artifacts are byte-identical. The primary dynamic
workflow performs 30 analyses and 18 adversarial validations. Additional refutation
validates 16 narrowed operational claims, confirming all 16. The validation attempt
for `0x237C4` ends with a network error before `StructuredOutput` and is completed by a
separate blind retry. The strict loop contains 65 attempts, 64 completed transcripts,
and 8,289,731 agent tokens. Audit of completed transcripts records 222 `Read` calls to
the assigned artifact path only and 64 successful `StructuredOutput` calls; the failed
attempt is excluded. No other tools, paths, or blinding violations appear.

Primary validation confirms 10 Map semantics `code` claims but rejects evidence for
`0x23804`: an exact index match to an axis node bypasses `0x26C78`, so the claimed
sequential chain through that helper is impossible. Repeated refutation uses exact
path `0x264CC -> 0x26984 -> 0x26740`, confirms write `floor(256/M)` to `ffff9129`,
and confirms its later use as a byte weight. Instructions are normalized to `site`
terminals, ordinary dependencies to `@structural`, and helpers with proven contracts
to `@contract_conf`. Self-dependencies and references to missing graph nodes are
removed while exact instruction anchors are preserved. The final proposal contains
30 of 30 valid rows and 179 resolvable address dependencies. Grammar and numeric round
trips for every nontrivial scale pass validation.

All 30 maps in the batch enter `findings.csv`:

- 25 Map semantics at `code`: `0x14FC2`, `0x14FD2`, `0x14FF2`, `0x15002`, `0x15012`,
  `0x15172`, `0x15182`, `0x15306`, `0x153A0`, `0x153E0`, `0x154A0`, `0x154B0`,
  `0x15580`, `0x15590`, `0x157D0`, `0x18DD6`, `0x237C4`, `0x237E4`, `0x23804`,
  `0x09C5A`, `0x09D2A`, `0x0A49A`, `0x0AAEA`, `0x0AAFA`, and `0x0AB5A`.
  Confidence applies to threshold, multiplicative, limiting, or blending roles
  directly proven by a machine trace; a physical name is not required for narrow
  operational semantics.
- Five Map semantics at `candidate`: `0x14FE2`, `0x15276`, `0x23752`, `0x09CEA`, and
  `0x09E3A`. Their traces end at a stack slot, RAM without a reader, or function
  `0x5D66C` without a contract.
- Ten Map scales at `code`: `x*255` for `0x14FF2`/`0x15002`, `x-32768` for `0x15276`,
  `x/65536` for `0x153E0`, `x/4096` for `0x15580`/`0x15590`, `x*64` for
  `0x157D0`/`0x09CEA`, `x*4` for `0x09C5A`, and `x/10` for `0x0AAFA`.
- Four Map scales at `candidate`: `x*0.000488` BFS for
  `0x15012`/`0x154A0`/`0x154B0`, and `(x-128)*0.5` degrees for `0x0AB5A`.
- Two new Axis scales at `code`: `x*4` for `0x119AE` and `x*8` for `0x119B2`.
  Axis `0x119B2` is non-increasing and fails the kernel's axis requirement, while code
  still proves the scale of its raw representation. Axes `0x15DA0`/`0x15DB0` with
  `x-32768` receive exact `site` evidence.

The function layer contains ten new and ten updated Func semantics at `code`. It records
paired branches `0x15306`/`0x153A0`, Q12 multipliers `0x15580`/`0x15590`, thresholds
`0x15172`/`0x15182` and `0x0AAEA`/`0x0AAFA`, three power-of-two divisor tables
`0x237C4`/`0x237E4`/`0x23804`, and consumer formulas for `0x09D2A`, `0x0A49A`,
`0x18DD6`, and `0x0AB5A`.

The post-batch snapshot contains 193 findings: 137 `code` and 56 `candidate`.
Catalog Map confidence is 137 `code` and 302 `candidate`; semantics are defined for
189 maps and `scale_expr` for 149. The ledger contains 248 `candidate` maps without
semantics. A full ingest creates 672 source claims: 184 Func semantics, 31 Func
contracts, 172 Reg, 193 Map semantics, 76 Map scale, and 16 Axis scale. The projection
contains 1450 `RESTS_ON` edges. Exact audit reports `missing=0`, `extra=0`,
`duplicate_expected=0`, `duplicate_actual=0`, and `unresolved=0`. Effective downgrade
is 99, ungrounded 95, cyclic SCCs 43, ungrounded SCCs 7, and report-only Map/Axis debt
80: 54 Map semantics, 20 Map scale, and 6 Axis scale.

The RomRaider generator emits 15 tables and two supporting axes; 424 maps fail the
gate. Two neutrally named internal calibrations, `0x15306` and `0x153A0`, have `code`
confidence and shared operational role branch multiplier. XML comments assign no
physical quantity. Repeated XML generation is byte-identical to historical
`08a5b04:defs/JK03A.xml`.


## Claim-specific-evidence pass, positions 200-229 (30 maps, 30 findings)

The primary dynamic workflow performs 30 analyses and 12 adversarial validations.
Four analyses end with a transport error before `StructuredOutput` and are completed
by separate blind retries. Additional refutation validates 22 narrowed operational
claims; seven rejected wordings are validated again after their exact findings are
addressed. The complete loop contains 75 attempts, 71 completed transcripts, and
7,729,604 agent tokens. Audit records 193 `Read` calls to the assigned artifact path
only, 71 successful `StructuredOutput` calls, and zero blinding violations. The four
transport failures are not counted as results.

The primary gate confirms six Map semantics `code` and six Map scale `code` claims.
Narrowing physical labels to computational roles adds 15 Map semantics at `code`:
12 from the first validation and three of the seven retried claims. Revalidation
accepts the direct `0xB5DA` path, centering in `0xA9AA`, and constrained write in
`0xD80E`. Formulas for `0xB5CA`/`0xB5EA` remain candidate because the machine window
does not establish `r14=1024` or equality of the two weight reads. `0x9E8A`, `0xF38E`,
`0xF40E`, and `0x11E5E` stop at helper `0x26740` without a complete listing or
contract. For `0x11E5E`, shifting a composite product by 24 also does not allocate
normalization uniquely among the four multipliers.

All 30 maps in the batch enter `findings.csv`:

- 22 Map semantics at `code`: `0xAB6A`, `0xB5DA`, `0xB5FA`, `0x9D3A`, `0x9DBA`,
  `0x9E4A`, `0xA09A`, `0xA9AA`, `0xABBA`, `0xABFA`, `0xB2FA`, `0xB53A`, `0xBB5A`,
  `0xC10E`, `0xC50E`, `0xD68E`, `0xD80E`, `0xFC0E`, `0xFC8E`, `0x10B0E`,
  `0x1198E`, and `0x11E46`.
- Eight Map semantics at `candidate`: `0xB5CA`, `0xB5EA`, `0x9CAA`, `0x9E8A`,
  `0xC18E`, `0xF38E`, `0xF40E`, and `0x11E5E`.
- Seven Map scales at `code`: `x/256` for `0x9D3A`, `x-128` for `0x9DBA` and
  `0xA9AA`, `x/100` for `0xA09A`, `x/4096` for `0xD68E`, `x-32768` for `0xD80E`,
  and `x*100/32768` for `0x10B0E`.
- Four Map scales at `candidate`: `(x-128)*0.5` for `0xB2FA`/`0xB53A`,
  `x*0.002` for `0xC18E`, and `x/256` for `0x11E5E`. There are no new Axis scale
  claims.

The function layer receives nine new Func semantics at `code`: accessors `0x77892`,
`0x77DEC`, `0x647E8`, `0x73BDC`, `0x3EDB4`, `0x4BDC2`, `0x7AB18`, `0x753D4`, and
`0x4B9B4`. Claims record the direct `0xB5DA` path, Q0.8/Q12/Q15 multipliers, threshold
`0xBB5A`, paired uint16 calculation `0xC10E`/`0xC18E`, and composite four-factor
value `ffff22f8`; physical names do not replace operational semantics.

The post-batch snapshot contains 223 findings: 158 `code` and 65 `candidate`.
Catalog Map confidence is 158 `code` and 281 `candidate`; semantics are defined for
219 maps and `scale_expr` for 179. The ledger contains 218 `candidate` maps without
semantics. A full ingest creates 722 source claims: 193 Func semantics, 31 Func
contracts, 172 Reg, 223 Map semantics, 87 Map scale, and 16 Axis scale. The projection
contains 1724 `RESTS_ON` edges. Exact audit reports `missing=0`, `extra=0`,
`duplicate_expected=0`, `duplicate_actual=0`, and `unresolved=0`. Effective downgrade
is 99, ungrounded 95, cyclic SCCs 43, ungrounded SCCs 7, and report-only Map/Axis debt
80.

The RomRaider generator emits 18 tables and two supporting axes; 421 maps fail the
gate. The batch adds `0x1198E`, `0x11E46`, and `0x11E5E`. The first two have narrow
operational semantics at `code`; `0x11E5E` is emitted as candidate with scale explicitly
marked `[cand]`. Presentation overrides use neutral names for internal calculations
and do not assign a physical subsystem.


## Claim-specific-evidence pass, positions 230-259 (30 maps, 30 findings)

The frozen-worklist batch contains 30 1D-16 maps with `uint8` elements, entry
`0x26388`, kernel `0x26A84`, and shared finisher `FUN_00026740`. The finisher contract
has `code` confidence: for `y0=r0`, `y1=r2`, and Q0.16 fraction `f=r3`, the function
returns unsigned linear interpolation
`y0 - floor((y0-y1)*f/65536)` when `y1 < y0` and
`y0 + floor((y1-y0)*f/65536)` when `y1 >= y0`. Complete listing
`0x26740..0x2676C`, including delay slots `0x2675A` and `0x2676C`, establishes both
branches, preservation of `MACL`, and the result in `r0`.

Maps `0x11FF6`, `0x12282`, and `0x12472` remain `candidate`: their available
machine windows do not cover the final write and reverse read of `ffff13ea`, a
saturating three-factor formula, and upper/lower clamps. Map `0x12718` has a complete
machine trace through the final RPM/25 comparisons and is a code-confidence Over Run
Fuel Cut threshold.

`findings.csv` receives 23 Map semantics at `code` and seven at `candidate`; five
Map scales are `code` and four `candidate`. The function layer receives four Func
semantics at `code`: composite accessor `0x56714`, conversion `x*256` in `0x55648`,
weighted calculation `0x46C70`, and paired lookup `0x50018`. No Axis claims are added.

The post-batch snapshot contains 253 findings: 181 `code` and 72 `candidate`.
The catalog contains 439 maps: 181 `code` and 258 `candidate`; semantics are defined
for 249 maps, `scale_expr` for 209, and the ledger contains 188 `candidate` maps
without semantics. `funcs.csv` contains 226 manual rows and `axes.csv` contains
22 findings.

A full ingest creates 766 source claims: 197 Func semantics, 32 Func contracts,
172 Reg, 253 Map semantics, 96 Map scale, and 16 Axis scale. The projection contains
1831 `RESTS_ON` edges. Exact audit reports `missing=0`, `extra=0`,
`duplicate_expected=0`, `duplicate_actual=0`, and `unresolved=0`. Effective downgrade
is 99, ungrounded 95, cyclic SCCs 43, ungrounded SCCs 7, and report-only Map/Axis debt
80.

The RomRaider generator emits 35 maps and two supporting axes: 26 maps are `code`,
nine are `candidate`, and five scales are marked `[cand]`. A total of 404 maps fail
the gate.


## Claim-specific-evidence pass, positions 260-289 (30 maps, 30 findings)

The frozen batch contains 27 1D-16 maps, two 1D-32 maps, and one 1D-4 map:
20 with `uint8` elements and 10 with `uint16`. Access paths are distributed among
five implicit wrappers: `0x26388` for 17 maps, `0x263F4` for 8, `0x266A0` for 2,
`0x263A0` for 2, and `0x26358` for 1. For eight maps through `0x263F4`, the blind
artifact includes the machine tail of shared kernel `0x26A64..0x26AB8`; reads of
adjacent `uint16` values at `0x26AA0`/`0x26AA2`, unsigned extension, and the transfer
to `FUN_00026740` appear in one continuous listing.

Adversarial validation of 15 promotions accepts 12 and rejects three. Maps `0x14CEA`,
`0x15770`, and `0x12C6E` remain `candidate`: the first lacks a closed machine trace for
blending; for the second, the catalog does not associate the divisor with a torque
converter; for the third, the machine listing does not cover the consumer and the
update formula requires saturation `min(t+2,255)`. Two more candidate claims,
`0x12C3A` and `0x11F6A`, are blocked respectively by no reader for `ffff1934` and an
incomplete trace of initial-retard mode.

`findings.csv` receives 25 Map semantics at `code` and five at `candidate`; roles are
25 `table` and five `threshold`. Four Map scales have `code` confidence: `x/256` for
`0x129E2`, and `x/128` for `0x12C02`, `0x12D72`, and `0x12DD2`. Five scales remain
`candidate`: `0x1465A`, `0x15770`, `0x18C96`, and `0x19190`. Map `0x1298C` has a
code-derived RPM/25 comparison scale and Over Run Fuel Restore role. The other maps
have raw identity only. There are no Axis claims.

The function layer receives four Func semantics at `code`: paired lookup accessors
`0x53698`, `0x476D2`, and `0x72378`, plus batch lookup accessor `0x56A7A`. Path
`0x72378` uses wrappers `0x266A0`/`0x266E8` and finisher `0x26AF8`;
`FUN_00026740` does not belong to this path.

The post-batch snapshot contains 283 findings: 206 `code` and 77 `candidate`.
The catalog contains 439 maps: 206 `code` and 233 `candidate`; semantics are defined
for 279 maps, `scale_expr` for 239, and the ledger contains 158 `candidate` maps
without semantics. `funcs.csv` contains 230 manual rows and `axes.csv` contains
22 findings.

A full ingest creates 809 source claims: 201 Func semantics, 32 Func contracts,
172 Reg, 283 Map semantics, 105 Map scale, and 16 Axis scale. The projection contains
1970 `RESTS_ON` edges. Exact audit reports `missing=0`, `extra=0`,
`duplicate_expected=0`, `duplicate_actual=0`, and `unresolved=0`. Effective downgrade
is 99, ungrounded 95, cyclic SCCs 43, ungrounded SCCs 7, and report-only Map/Axis debt
80.

The RomRaider generator emits 60 maps and two supporting axes: 47 maps are `code`,
13 are `candidate`, and ten scales are marked `[cand]`. A total of 379 maps fail the
gate. Presentation overrides for new tables use operational names and do not assign an
unestablished physical subsystem.


## Claim-specific-evidence pass, positions 290-319 (30 maps, 30 findings)

The positions were selected from the frozen worklist object
`ba85fba:defs/JK03A.maps.csv` using the `confidence != code` or empty `semantics` filter;
the source list contains 396 rows. The current ledger was not used to select positions.
The batch contains twenty-two 1D-8 `uint8` maps, four 1D-4 `uint8` maps, two 1D-4
`uint16` maps, and two 1D-64 `uint16` maps. The access path is distributed among
`0x26370` (22 maps), `0x26358` (4), `0x263BC` (2), and `0x26410` (2).

Two independent builds of the 30 blind artifacts are byte-identical. The primary
dynamic workflow produces 56 transcripts: 29 of 30 analyses finish with a claim, and 25
`code` reviews return a verdict. Analysis of `0x11FE6` and review of `0x153B0` terminate
with a WebSocket error before producing a result. Three targeted blind reruns complete
the analysis and review of `0x11FE6` and the review of `0x153B0`; a separate blind review
confirms the `0x153B8` scale. An audit of all 60 transcripts records reads of only the
assigned artifact path, with no other paths or tools used.

All 30 maps in the batch are included in `findings.csv`:

- 29 Map semantics claims at `code`: `0x12522`, `0x12526`, `0x1292C`, `0x153B0`,
  `0x153B8`, `0x11C6D`, `0x11E56`, `0x11F0A`, `0x11F12`, `0x11F1A`, `0x11F22`,
  `0x11FBE`, `0x11FE6`, `0x12006`, `0x12032`, `0x12086`, `0x1208E`, `0x12096`,
  `0x120CE`, `0x1211E`, `0x12126`, `0x1212E`, `0x1215E`, `0x12176`, `0x1218E`,
  `0x12196`, `0x1219E`, `0x141F4`, and `0x14274`. This confidence applies to a threshold, multiplicative,
  limiting, additive, or blending role directly proven by the machine trace;
- one Map semantics claim remains at `candidate`: `0x1202E` is the catalog hypothesis
  Initial Retard Quantity because no external reader was found for stores to
  `ffff1ee0`/`ffff257a`. Independent exact-JK08A analysis promotes `0x141F4` and
  `0x14274` to code-confidence bank-2 and bank-1 MAF transfer curves through the
  AN15/AN4 and DID `0x1205`/`0x1204` paths;
- nine Map scale claims at `code`: `x/100` for `0x12522`/`0x12526`, `x/65536` for
  `0x153B0`/`0x153B8`, `x/256` for `0x11E56`, `x/2048` for `0x12126`, `x/128` for
  `0x1212E`, and `x-128` for `0x12196`/`0x1219E`. The other 21 maps use raw identity;
  there are no Axis claims;
- four maps have the `threshold` role and are not emitted to XML: `0x11C6D`, `0x11F0A`,
  `0x12032`, and `0x12086`. The other 26 have the `table` role.

The field refutation for `0x12096` confirms semantics, attribution, disposition, role,
and index but excludes `site:00026a9c`: that site belongs to the 16-bit branch, while the
target `uint8` map passes through `0x26AAA`/`0x26AAC`/`0x26AAE`. Numerical evidence for
`0x153B0` is split into separate `spec:` tokens without an internal `;` so that every
token remains a valid item in the provenance grammar. The independent review of
`0x153B8` confirms addition of `0x8` to base `0x153B0`, storage of the Q0.16 step in
`ffff17f8`, and its use when updating weight `ffff2422`.

The function layer gains ten Func semantics claims at `code`: `0x3A904`, `0x3E1DA`,
`0x44910`, `0x4AC60`, `0x4C02E`, `0x4F758`, `0x528BE`, `0x5AC54`, `0x638B4`, and
`0x786DA`. Another nine rows gain operational semantics and evidence: `0x2C648`,
`0x3C4A0`, `0x4AC7A`, `0x4B9B4`, `0x4C1E4`, `0x52BE8`, `0x647E8`, `0x68CB8`, and
`0x74C82`. Function contracts do not change; `funcs.csv` contains 240 manually curated
rows.

The post-batch snapshot contains 313 findings: 233 `code` and 80 `candidate`. The
catalog contains 439 maps: 233 `code` and 206 `candidate`; semantics are defined for 309
maps and `scale_expr` for 269. The ledger contains 128 `candidate` maps without semantics.
A full ingest creates 858 source claims: 211 Func semantics, 32 Func contract, 172 Reg,
313 Map semantics, 114 Map scale, and 16 Axis scale. The projection contains 2,159
`RESTS_ON` edges; the exact audit reports `missing=0`, `extra=0`,
`duplicate_expected=0`, `duplicate_actual=0`, and `unresolved=0`. Effective downgrade is
99, with 93 ungrounded claims, 43 cyclic SCCs, 6 ungrounded SCCs, and report-only
Map/Axis debt of 80 (54 Map semantics, 20 Map scale, and 6 Axis scale).

The RomRaider generator emits 86 maps and two supporting axes; 70 maps are at `code`, 16
are at `candidate`, and ten scales are marked `[cand]`. The batch adds 26 tables: 23 at
`code` and three at `candidate`; four thresholds fail the role gate. Presentation
overrides use operational names and explicitly mark the unresolved mode and MAF channel.


## Claim-specific-evidence pass, positions 320-349 (30 maps, 30 findings)

The positions were selected from the frozen worklist object
`ba85fba:defs/JK03A.maps.csv` using the `confidence != code` or empty `semantics` filter;
the current ledger was not used to select positions. All 30 maps are 1D-8, use `uint8`
elements, enter through `0x26370`, use core `0x26A80`, have an implicit uniform axis,
and finish through `FUN_00026740`. Two independent builds of the blind artifacts are
byte-identical. For two target maps, neighboring map `0x09EDA` has no callsite of its
own in the component artifact; machine listings and pseudocode for the target maps are
present.

All 30 maps in the batch are included in `findings.csv`:

- 29 Map semantics claims are at `code` and one, `0x123A2`, is at `candidate`. The
  latter exposes a coefficient for the negative contribution of a signed difference,
  but the complete machine trace to final consumption is not closed;
- roles are distributed across 25 `table` and five `threshold` maps: `0x12332`,
  `0x123AA`, `0x126B0`, `0x126B8`, and `0x12758`. The `threshold` role of pair
  `0x126B0`/`0x126B8` denotes tabulated upper bounds for a `min` operation, while
  `0x12758` supplies a lower bound through `max`;
- two Map scale claims are at `code`: `x-128` for `0x121A6` and `x/128` for
  `0x12432`. The other 28 maps use raw identity. Exact forward and inverse
  substitutions are placed in separate `spec:` tokens; consumer clamping and
  saturation are not included in the map scale;
- there are no new Axis claims: implicit RAM inputs do not produce `axes.csv` rows.

The field refutation identifies three localized evidence defects. For `0x121C6`, target
`ffff1528` is read at `0x519FE`, while `0x519FA` extends neighboring multiplier
`ffff1531`. For `0x121D6`, unsigned transfer of `ffff1534` passes through `0x518F0`,
and implicit RAM input `ffff11B3` is not a ROM axis. For `0x12562`, the conditional
branch and final multiplication stage require sites `0x54F18..0x54F2C` and
`0x54F6E..0x54F76`. The corrected claims pass another blind refutation for every field.
A separate review of `0x126B0` confirms the intended `threshold` role as an upper
calibration bound for `min`.

Claim-specific dependencies use `@structural` when a claim needs only the target node
and its structure rather than the target's semantic confidence. Exact sites
`FUN_000474A4` and `FUN_0005444C` ground downstream consumption for `0x1234A` and
`0x12352`. Address `0x0870B` selects the `0x121A6` branch but does not prove the `x-128`
scale, so it is excluded from `scale_evidence`. After this normalization, the new Map
claims do not increase effective downgrade.

The function layer gains seven new Func semantics claims at `code` and extends existing
claims with operational formulas without changing contracts. `funcs.csv` contains 247
manually curated rows.

The post-batch snapshot contains 343 findings: 262 `code` and 81 `candidate`. The
catalog contains 439 maps: 262 `code` and 177 `candidate`; semantics are defined for 339
maps, `scale_expr` for 299, and the ledger contains 98 `candidate` maps without
semantics.

A full ingest creates 897 source claims: 218 Func semantics, 32 Func contract, 172 Reg,
343 Map semantics, 116 Map scale, and 16 Axis scale. The projection contains 2,339
`RESTS_ON` edges; the exact audit reports `missing=0`, `extra=0`,
`duplicate_expected=0`, `duplicate_actual=0`, and `unresolved=0`. Effective downgrade is
99, with 93 ungrounded claims, 43 cyclic SCCs, 6 ungrounded SCCs, and report-only
Map/Axis debt of 80.

The RomRaider generator emits 111 maps and two supporting axes; 94 maps are at `code`,
17 are at `candidate`, and ten scales are marked `[cand]`. The batch adds 25 tables: 24
at `code` and one at `candidate`; five thresholds fail the role gate. Presentation
overrides use narrow operational names without physical attribution.


## Claim-specific-evidence pass, positions 350-379 (30 maps, 30 findings)

The positions were selected from the frozen worklist object
`ba85fba:defs/JK03A.maps.csv` using the `confidence != code` or empty `semantics` filter;
the source list contains 396 rows. The current ledger was not used to select positions.
All 30 maps are implicit 1D-8: 24 maps store `uint8` and six store `uint16`. After this
batch, positions 380-395, comprising 16 maps, remain in the frozen worklist.

Two independent builds of the 30 blind artifacts are byte-identical. The primary
Dynamic Workflow `wf_6702175a-7ec` (`jk03a-sweep-350-379-wf_6702175a-7ec.js`) contains
57 agent transcripts: 30 analyses and 27 adversarial reviews of `code` claims. The audit
records 95 reads of only the assigned artifact paths and 59 StructuredOutput responses;
four Read size limits were resolved by reading segments of the same file, and two schema
errors by another StructuredOutput response. No other paths, tools, or blind-contract
violations are present.

A separate Dynamic Workflow `wf_ff080de2-12b`
(`jk03a-12f06-adjudication-wf_ff080de2-12b.js`) reviews the narrow `0x12F06` claim with
one agent. When this map is selected, `uint8 ffff106f` is the lookup index, previous
values `ffff1a1e` and `ffff25ee` participate in the gate, and the result is stored in
both registers. The exact change to `ffff2326` is not claimed: subsequent logic involving
`ffff41fa` and `ffff1704` can modify and clamp the intermediate value. Semantics,
evidence, attribution, disposition, role, and index of the narrow claim are confirmed;
the physical meaning of the pair is not established.

All 30 maps in the batch are included in `findings.csv`:

- 27 Map semantics claims are at `code` and three are at `candidate`. `0x12A3A` stores
  `ffff1f78`, but no downstream reader was found; `0x12AB2` similarly stores
  `ffff1f81`; `0x12EFE` stores pair `ffff1a1e`/`ffff25ee`, while the shown read of the
  pair precedes the lookup and does not prove subsequent consumption;
- roles are distributed across 21 `table` and nine `threshold` maps: `0x128D8`,
  `0x128E0`, `0x12944`, `0x12AEA`, `0x12C66`, `0x12FB6`, `0x148EA`, `0x14A2A`,
  and `0x14BEA`;
- seven Map scale claims are at `code`: `x*10` for `0x12C66`, `x/128` for `0x12DCA`,
  `x-128` for `0x12E72` and `0x13016`, `x*2560` for `0x12FB6`, `x/64` for `0x1300E`,
  and `x-32768` for `0x148EA`. Forward and inverse expressions round-trip across the
  element range; the other 23 maps use raw identity;
- there are no new Axis claims. Structured output defines disposition and target for
  all 30 claims: 13 `consumer`, ten `inline_comparison`, and seven `writes`. Together
  with the preceding focused positions 50-349, the format covers all 330 claims at
  positions 50-379.

Manual-layer map `0xA8EA`, included as neighboring context in focused artifact `0x14ED2`,
has no `callsite` by construction. The renderer indicates an absent site rather than a
missing `listing_.txt` export; this case is fixed by a unit test and the
`tools/map-sweep.md` contract.

The function layer gains ten new Func semantics claims at `code`: `0x38618`, `0x3A750`,
`0x3BD74`, `0x43AEE`, `0x45758`, `0x464DE`, `0x6E3D8`, `0x74E4E`, `0xB5C36`, and
`0xBDC66`. Rows `0x522C4`, `0x52576`, and `0x71650` gain operational semantics and
evidence. Function contracts do not change; `funcs.csv` contains 257 manually curated
rows. The presentation layer gains 21 `table` maps at orders 182-202; the three
`candidate` maps use the functional `Internal Calculations` category and retain
their confidence in generated evidence comments.

The post-batch snapshot contains 373 findings: 289 `code` and 84 `candidate`. The
catalog contains 439 maps: 289 `code` and 150 `candidate`; semantics are defined for 369
maps, `scale_expr` for 329, and the ledger contains 68 `candidate` maps without
semantics. A full ingest creates 944 source claims: 228 Func semantics, 32 Func contract,
172 Reg, 373 Map semantics, 123 Map scale, and 16 Axis scale. The projection contains
2,548 `RESTS_ON` edges; the exact audit reports `missing=0`, `extra=0`,
`duplicate_expected=0`, `duplicate_actual=0`, and `unresolved=0`. Effective downgrade is
99, with 93 ungrounded claims, 44 cyclic SCCs, 6 ungrounded SCCs, and report-only
Map/Axis debt of 80.

The RomRaider generator emits 132 maps and two supporting axes; 112 maps are at `code`,
20 are at `candidate`, and ten `code` maps have a scale not established by code. The
batch adds 21 tables: 18 at `code` and three at `candidate`; nine thresholds fail the
role gate. Regeneration preserves SHA-256
`f95a32bbd03f920e23587b2d4450bde9bf08f66a9488cab525535c42097a906b` for the ledger and
`6b8979f134025aefc20e3ac9fc8444686dc5284bbaf85b72002d985a16b5ec41` for the XML. All
47 Memgraph and sweep unit tests pass.


## Claim-specific-evidence pass, positions 380-395 (16 maps, 16 findings)

These positions are the final slice of the frozen worklist object
`ba85fba:defs/JK03A.maps.csv`, built with the `confidence != code` or empty `semantics`
filter. The full list contains 396 rows; the positional pass completes positions 0-395.
The batch contains six implicit 1D-8 `uint16` maps, four implicit 1D-16 and four implicit
1D-8 `uint8` maps, and two implicit-2d 8x8 `uint8` surfaces.

Two independent builds of the 16 blind artifacts are byte-identical. The primary
Dynamic Workflow `wf_2fa7f8dd-eef` (`jk03a-sweep-380-395-wf_2fa7f8dd-eef.js`) contains
15 completed analyses and 12 adversarial reviews; analysis of `0x15082` was completed by
separate recovery run `wf_cb798313-a26` (`jk03a-15082-recovery-wf_cb798313-a26.js`)
after a transport failure. Map liveness for `0x121F6` and `0x12206` is resolved by
separate adjudication run `wf_1f8e4cc3-926`
(`jk03a-dead-branch-adjudication-wf_1f8e4cc3-926.js`) with two analyses and two
independent reviews. The aggregate audit of 34 agent transcripts records 144 `Read`
calls to only the assigned artifact paths, 33 StructuredOutput responses, one expected
transport failure, and zero blind-contract violations.

All 16 maps in the batch are included in `findings.csv`:

- 14 Map semantics claims are at `code` and two, `0x09EDA` and `0xA8EA`, are at
  `candidate`. The blind artifact for both implicit-2d maps lacks the body and contract
  of `0x26040`, which connect a surface cell to returned `r0`; both surfaces retain
  operational but not physical semantics;
- roles are distributed across seven `table`, seven `threshold`, and two `dead` maps.
  ROM byte `ROM[0x8D92]=0x7A` has bit 3 set, so `tst` at `0x51716` clears T, `bf/s` at
  `0x51718` branches to `0x517A8`, and both `0x121F6` and `0x12206` lookups and their
  downstream calculations are skipped;
- three Map scale claims are nontrivial: `0x15082` has the code-proven UQ0.16 scale
  `x/65536`, `0x15630` has the profile-derived BFS scale `x/2048` at `candidate`, and
  `0xA8EA` has the arithmetic-derived scale `x/128` at `candidate`. The durable inverse
  for `0x15082` is recorded as the valid expression `x*65536`; round-trip behavior is
  fixed by separate `spec:` evidence items;
- there are no new Axis claims. Indices `ffff106f` and `ffff10f0` for
  `0x09EDA`/`0xA8EA` are implicit RAM inputs rather than ROM Axis nodes, so neither 2D
  map receives a presentation block;
- disposition and target are populated for all 16 claims: eight `inline_comparison`,
  four `consumer`, two `writes`, and two `dead_control_flow`. The format covers all 346
  focused positions 50-395;
- evidence for `0x12DE2` rests on the actual store to `ffff41d2` at `0x8397A`; site
  `0x83978` loads another base and is excluded from the claim.

The function layer gains four new Func semantics claims at `code`: `0x730FC`, `0x66186`,
`0x3B75C`, and `0x6F8FA`. Rows `0xB5C36`, `0x71448`, `0x82C8A`, and `0x51700` gain
operational semantics and evidence. Function contracts do not change; `funcs.csv`
contains 261 manually curated rows. The presentation layer gains five `table` maps at
orders 203-207: `0x15082`, `0x15330`, `0x15630`, `0x23824`, and `0x12026`.

The snapshot contains 379 findings: 301 `code` and 78 `candidate`. The catalog contains
439 maps: 301 `code` and 138 `candidate`; semantics are defined for 379 maps,
`scale_expr` for 345, and the ledger contains 60 `candidate` maps without semantics. A
full ingest creates 957 source claims: 232 Func semantics, 32 Func contract, 172 Reg,
379 Map semantics, 126 Map scale, and 16 Axis scale. The projection contains 2,630
`RESTS_ON` edges; the exact audit reports `missing=0`, `extra=0`,
`duplicate_expected=0`, `duplicate_actual=0`, and `unresolved=0`. Effective downgrade is
106, with 91 ungrounded claims, 44 cyclic SCCs, 6 ungrounded SCCs, and report-only
Map/Axis debt of 78.

The RomRaider generator emits 137 maps and two supporting axes; 117 maps are at `code`,
20 are at `candidate`, and 11 `code` maps have a scale not established by code. The
batch adds five tables; seven thresholds, two dead maps, and two 2D maps without a ROM
Axis fail the emission gate. Regeneration preserves SHA-256
`eabc535b6a6d380aac69039392f483a81d478bb3bc6479ce032800094836944b` for the ledger and
`7bb043d8aa102e9b5b9f61dba9e1d6a771bea2d24f8fdd6266235e22085d8d7d` for the XML. All
47 Memgraph and sweep unit tests pass.


## Evidence backfill for the earlier Map/Axis layer

The frozen manifest at commit `b02d3b7157d900a0654b1c63f2c200d8154d315b` contains 78
property claims on 58 nodes: 52 `Map.confidence`, 20 `Map.scale_conf`, and 6
`Axis.scale_conf`. The manifest SHA-256 is
`6ef76b7f7e17d9ec95bf1b9cd1e8f974a54d3f59a79af5d6bc894d94452c02bf`; two
independent builds of 58 blind artifacts match with artifact-set SHA-256
`7fef9e35baf8e6f2290a9abd0ac60b974b7f8c98883fca6bc8d34a30b9511011`. A Map
artifact preserves the context of the map component; an Axis artifact aggregates all
maps and accessors associated with the shared axis.

The primary Dynamic Workflow `wf_1348d1fd-75a` contains 58 analyses and 78 separate
adversarial reviews, 136 agents, and zero agent errors. Artifact `0x11FB6` was read to
EOF in separate recovery run `wf_5a0bc63d-82b`. ROM selectors for dead branches
`0x122B2`, `0x12E3A`, and `0x1473A` were reviewed by recovery run `wf_41b9b207-a61`
against exact-code donor `JK03A`; the same `rom_const` values were independently
verified in `JK08A`, preserving `role=dead` and
`output_disposition=dead_control_flow` for these maps. The resulting run set has
SHA-256 `bc2ca9028b340b92e456cde8109f04eb7e2bcc3cc1ddb250d785cafc2e75711b` and a
complete join of 58 analyses and 78 verdicts with no missing identities.

Synthesis yields 28 `accept`, 27 `revise`, and 23 `downgrade` verdicts. Of the frozen
claims, 55 remain at `code` and 23 become `candidate`: Map semantics 41/11, Map scale
13/7, and Axis scale 1/5. The 41 confirmed Map semantics roles comprise 15 `table`, 22
`threshold`, and 4 `dead`; dispositions comprise 11 `consumer`, 22
`inline_comparison`, 4 `writes`, and 4 `dead_control_flow`. Semantics and scale are
resolved independently. The scale of `Axis:0x11CF0` is downgraded separately: identity
`x` confirms raw transfer but not the claimed RPM meaning and `x*50` scale.

Verified evidence is carried over without substantive extension. For 43 claims, 93
incorrectly typed edge tokens undergo the recorded syntactic normalization: 64 ROM
addresses become `site:` tokens with the same address, and 29 RAM dependencies without
a ranked claim are removed. The control plane prohibits address changes and rechecks
factual evidence; offline preflight confirms that all remaining dependencies resolve.
The canonical CSV files contain 379 Map semantics claims (290 `code`, 89 `candidate`),
126 Map scale claims (90 `code`, 36 `candidate`), and 16 Axis scale claims (9 `code`, 7
`candidate`). The earlier-layer debt of `52 + 20 + 6` is zero.

Global strict parsing preserves 976 source claims and 2,759 `RESTS_ON` edges. Candidate
blockers are not promoted without evidence; dependencies that require only the
existence of an address or data flow use `@structural`. Function `0x6205C` is downgraded
to `candidate`: the code shows two thresholds near 7300 but does not prove the
multiplier, consumers of the results, or physical rev-limit semantics. Six cyclic
Func/Reg components receive independent factual grounding at exact instruction sites
without breaking the cycles.

Strict ingest and exact audit pass: `missing=0`, `extra=0`, `duplicate_expected=0`,
`duplicate_actual=0`, `unresolved=0`, zero claims with effective confidence below
declared confidence, zero ungrounded claims, 44 cyclic SCCs, and zero ungrounded SCCs.
The test suites contain 105 sweep tests, 54 Memgraph tests, 10 mapkit/DTC tests, 8
immo-off tests, and 5 ROM-layout tests; all 182 pass.

Two consecutive generations emit 145 maps, two supporting axes, and two NATS
`TableSwitch` entries: 121 maps at `code`, 24 at `candidate`, and 17 maps with a scale
not established at `code`. Table `0x12E1A` has the presentation name
`Interpolated State Byte - raw u8`. The deterministic SHA-256 values are
`38dd792023f6aa406ce7f0b26e011714e67cdf650cd8bc603c4edccff01023e2` for the ledger and
`af3985ae553b8baacf723b2c421565c00dc193a5e044546d4b96e33d1c3fc42f` for the XML.



## RomRaider NATS and DTC switches

The first `TableSwitch` provides the `Enabled (Stock)` and `Disabled (IMMO OFF)` states.
It changes the byte at `0x08725` between `01` and `00`, clearing bit 0 of the stock
Developer Immobilizer flag.

Bit 0 is read by functions `0xA3F96`, `0xBBC88`, `0xBC82E`, and `0xBC9E4`. When it is
zero, `0xBC82E` clears `0xFFFF55E4.bit2`, after which `0xBC9E4` clears motor-inhibit
bit `0xFFFF4198.bit1`. Native checksum handlers run in `alt` -> `alt2` order: selftest B,
then selftest A and SUM16. Derived image
`rom-images/23710-JK08A/mods/immo-off/1JK08A-20260727-immo-off.bin` differs from stock
by one bit. On-vehicle validation confirms engine start and normal operation; P1610
persists after clearing and does not affect engine operation.

The 36 entries in `JK08A.dtc.csv` generate 71 native `TableSwitch` controls under one
`Diagnostics / DTC` category. Each of the 35 ordinary records has adjacent
`1/2 Descriptor` and `2/2 Attribute` controls. Both select either `Enabled (Stock)` or
`Disabled` and must use the same state before saving. P1610 uses descriptor `0x19540`;
its attribute at `0x160FE` remains `0000` in both states, so only its descriptor switch
is present. DTC suppression through these controls has not been validated on hardware.

## Selected aggregate curves and branch coefficient

`FUN_0004569C` selects one of four related uint8 curves. Let
`x = uint8[0xFFFF22E4]`. `ROM8[0x8710].bit3` selects the curve form: set uses explicit
axis `0x12778`, while clear uses the implicit coordinate `min(2*x,255)`.
`0xFFFF244F.bit1` selects curve A (`0x127A8` explicit or `0x12798` implicit) when
clear and curve B (`0x127E8` explicit or `0x127D8` implicit) when set. The selected
lookup is multiplied by four and written to uint16 `0xFFFF1752`. Stock
`ROM8[0x8710]=0x7C` has bit 3 set, so `0x127A8` and `0x127E8` are the active forms in
this function.

The selected term has two exact downstream uses. `FUN_00041DB6` includes it in
`D = u16[0xFFFF1752] + 4*u8[0xFFFF1765] + u8[0xFFFF1763] +
u8[0xFFFF1F62]` and conditionally writes
`clamp(floor(s16[0xFFFF2266]*128/D)+128,0,255)`. `FUN_000468B0` includes it in a
saturating aggregate with `0xFFFF1765`, `0xFFFF1748`, `0xFFFF1230`, `0xFFFF15AC`,
`0xFFFF13F7`, and `0xFFFF170A`, plus optional `0xFFFF1F62`. The physical quantity of
the selected term remains unresolved. `FUN_000413CC` is a separate paired
normalization over the implicit curves `0x12798` and `0x127D8`; it does not read
`ROM8[0x8710]` or select the explicit curves.

`FUN_00069374` selects coefficient K by `0xFFFF420B.bit4`. A clear bit selects the
uint8 curve `0x124F2` by `uint8[0xFFFF10F0]` over axis `0x23814`; a set bit selects
the uint16 curve `0x14E22` by `uint16[0xFFFF31DC]` over axis `0x13798` and limits the
result to 255. It writes K to `0xFFFF90D0` and calculates
`min(65535,floor(K*floor(14*d/64)/128))`, where
`d = (u16[0xFFFF1040]-u16[0xFFFF8DC8]) mod 65536`; the result is written to
`0xFFFF8F0A`. K therefore has the exact Q1.7 scale `x/128`. Every stock cell of
`0x14E22` equals 16 and every point of its axis equals zero, so that branch supplies
the fixed coefficient 0.125. Its physical subsystem remains unresolved.

## Dual-channel conversion and diagnostic coefficients

`FUN_0003EF74` uses `0x12292` as a Q1.7 divisor for two input channels. It indexes
the curve by the high byte of `uint16[0xFFFF4524]` over axis `0x11B47`. For each
source X, it forms `d = sat_s16(X-880)` and, when the range gates pass and divisor C
is nonzero, returns `max(0,880+sat_s16(trunc0(128*d/C)))`; otherwise it retains X.
`ROM8[0x8978].bit3` selects the source pair. Stock value `0xA0` has the bit clear and
selects twice `0xFFFF267C` and twice `0xFFFF267E`; the set branch selects
`0xFFFF2882` and `0xFFFF2884`.

`FUN_0003EDB4` uses the two adjusted coordinates to interpolate common uint16 curve
`0x148FA`. Let Y1/Y2 be these lookup results, A1/A2 the results of correction maps
`0xC10E`/`0xC18E`, O1/O2 signed states `0xFFFF45A0`/`0xFFFF45A2`, and P1/P2 signed
terms `0xFFFF2B54`/`0xFFFF2B56`. The function writes
`clamp(Y1+A1+O1+P1-32768,0,65535)` to `0xFFFF29E2` and the parallel result to
`0xFFFF29E4`. Stock `ROM16[0x8EA4]=0` disables P1/P2. The vendor AFR Conversion Table
name and two-bank fuel-trim context support a physical hypothesis, but code does not
establish an AFR scale.

Maps `0x12262` and `0x12272` are independent Q1.7 multipliers in two-bank diagnostic
paths of `FUN_00094F26`. Each multiplies a signed channel value and divides by 128
with truncation toward zero before a separate threshold comparison. Map `0x129D2` is
a Q1.7 secondary divisor for the calculated-load byte: `FUN_0008083C` conditionally
applies `floor((q<<7)/K)`, with K zero forcing 255. Stock `ROM8[0x870E]=0x28` has bit
4 clear, so this secondary normalization is inactive. Shared curve `0x122D2` feeds
three state controllers, but every consumer tests only zero versus nonzero and
discards the interpolated magnitude.

## Map-switching input anchor

The stock JK08A firmware contains a closed ASCD steering-switch path that can serve as
the first input anchor for a new map-switching design. This is an implementation
candidate for this ROM, not evidence about the internal design of UpRev or another
commercial product.

- Service 0x22 table entries map DID 0x130D to value byte `0xFFFF2A83` and support mask
  `0xFFFF2A81`, and DID 0x130E to value byte `0xFFFF2A84` and support mask
  `0xFFFF2A82`. The pointer records are at `0x22A48..0x22A54`.
- `FUN_000CF020` copies the prior stable code from `0xFFFF2A85` to `0xFFFF2A86`, then
  accepts a replacement only when five consecutive decoded samples
  `0xFFFF2701..0xFFFF2705` are equal.
- The stable one-hot codes are `0x00` released, `0x02` CANCEL, `0x08` SET/COAST,
  `0x10` RESUME/ACCEL, and `0x20` MAIN-button pulse. DID 0x130D independently exposes
  SET, RESUME, and CANCEL as output bits 3, 2, and 1. `FUN_000913D0` reads the same
  stable byte for exact DTC P1564 and masks codes `0x02`, `0x08`, and `0x10` with
  `0x1A`.
- `FUN_000CF020` also packs DID 0x130E. Code establishes its source bits; homologous
  factory and measured diagnostics identify output bit 5 as SET LAMP and bit 2 as
  CRUISE LAMP.
- `FUN_000D093C` initializes the paired support masks from ROM8[`0x8B28`]. DID 0x130D
  can expose masks `0x00`, `0x3F`, `0x31`, or `0x7F`; DID 0x130E exposes `0x00`,
  `0x3F`, or `0x04`.

The 2007 VQ35HR factory manual establishes the physical input form: the MAIN, CANCEL,
SET/COAST, and RESUME/ACCEL buttons form an analog resistor ladder wired directly to
ECM terminal M107-101. A whole-program direct RAM-access scan found no writer for
`0xFFFF2701..0xFFFF2705`; the producer is pointer-mediated or otherwise unresolved.
The exact JK08A ADC channel and MCU pin therefore remain open.

Because the decoder publishes one stable code at a time, a two-button gesture cannot
be modeled as simultaneous bits in `0xFFFF2A85`. On the resistor ladder, pressing
CANCEL while SET is held is expected to produce a transition sequence such as
SET -> CANCEL -> SET, but this electrical behavior requires bench confirmation on the
target steering-switch assembly.

The formal contract is `patches/map-switching-selector.md`.
`patches/map-switching-layout.toml` is the authoritative ROM/RAM allocation and hook
manifest, `patches/map_switching_layout.py` validates it against the exact stock ROM,
and `patches/map_switching_selector.py` is the executable selector and calibration
transaction model. `patches/map_switching_assembly.py` validates the address, literal,
ABI, and delay-slot contract of implemented SH source slices and independently
decodes control transfers and PC-relative effective addresses from the locked
machine words. The selector provides
five slots. A valid gesture contains one through five `SET -> CANCEL -> SET` pulses
and commits only on the final SET release. Any unexpected transition, timeout, sixth
pulse, invalid state, or ASCD enable aborts the gesture and retains the validated
active slot.

The implementation boundary is statically bounded:

- The selector owns `0xFFFF5D00..0xFFFF5D07`; the fuel-cut and throttle clusters use
  shadows at `0xFFFF5D10..0xFFFF5D1B` and `0xFFFF5D20..0xFFFF5D3B`. A complete
  2315-function RAM-access trace has zero failures and zero accesses, call arguments,
  or unresolved indexed candidates in `0xFFFF5D00..0xFFFF5D3B`. The preceding
  application access is at `0xFFFF5CF9`; the only nearby unresolved indexed loop ends
  at `0xFFFF5CF1`.
- Startup literal `0x29CC` remains the read-only stock anchor
  `0xFFFF7000`. The map-switching layout validator rejects any other value and
  the composer does not write this location.
- The unique thunk literal at `0x27D28` redirects stock initializer `0x2C648` through
  a wrapper at `0xD22A0`. The wrapper publishes map 1 before running stock
  initialization without changing its incoming `r4`, then commits map 1 after it
  returns by refreshing both limiter shadows and stock throttle runtime scalar
  `0xFFFF1796` before publishing the active index.
- Literal `0xCE8DC` redirects the scheduled `FUN_000D09D8` call to a wrapper at
  `0xD2108`. The wrapper calls the stock function first, then the selector and
  diagnostic mirror, preserving the stock P1564 path.
- `[0xD2108, 0xE1C2A)` is the conservative free-ROM allocation: 64,290 bytes of
  `0xFF` with no instructions, defined data, function bodies, or inbound Ghidra
  references. The manifest claims `[0xD2108, 0xD4000)` for code, 40 calibration
  copies, ten five-entry pointer tables, the CAN feedback wrapper, and its
  separate pulse engine.
  `AuditFreeRegion.java` reproduces both the claimed-range and conservative-range
  gates.
- Eight families are adapter-backed. DFCO uses stock wrapper `0x26388`, ignition uses
  `0x26230`, Fuel Compensation Main uses `0x261F0`, and Fuel Targets uses `0x261B8`.
  Each adapter redirects approved bases only and tail-jumps every other base to the
  stock wrapper. Cold ignition and unrecognized Bosch overrun bases remain global.
- `patches/map-switching-adapter-helper.s` owns `0xD2270..0xD229F`, and
  `patches/map-switching-adapters.s` owns `0xD2300..0xD23FF`. Ghidra 12.1.2
  assembles and round-trip decodes 59 instructions and 68 literal bytes. The two raw
  blobs are locked by SHA-256 in the layout. The adapter blob is
  `a938e1334e7850a0c368c50e98dbbdf67bc2589524025659a31d5b5f328c0e6c`.
  Every adapter loads its stock-wrapper address before dispatch and uses `NOP` in
  each `BRA` delay slot. This is required because an SH-2E PC-relative move in a
  delayed branch slot uses the branch destination plus two as its PC basis. Ghidra
  SuperH p-code passes 47/47 cases over 718 executed instructions: all five slots
  for all six families, indices 5 and
  255 falling back to map 1, Cold Ignition and Bosch pass-through, unknown fuel-base
  pass-through, exact stock-wrapper destinations, and preservation of `r5..r15`, PR,
  GBR, MACH, and MACL. Comparison instructions may change the caller-clobbered T
  bit; every other SR bit remains unchanged. This path uses no radare2 and creates
  no ROM.
- `patches/map-switching-full-dfco-adapter.s` owns `0xD2480..0xD24DF`.
  It recognizes exact bases `0x126E4`, `0x12718`, `0x12818`, and `0x1298C`,
  selects their five-slot pointer tables, and tail-jumps every other base to
  stock wrapper `0x26388`. Its 27 instructions and 36 literal bytes have locked
  SHA-256 `2a5a65671e077400b753cb7fabb15c0520ddd7e96be8234e44297b6cd7052ba7`.
  The complete adapter harness passes 76 cases over 1286 executed instructions.
- The complete machine-word audit covers all 414 final-runtime instructions: 39
  delayed transfers with encoded `NOP` slots, 52 PC-relative references, 77 direct
  branch targets, and 21 indirect control transfers. The startup-trampoline and
  startup-selector-init sources add 13 alternative instruction instances under the
  same checks. All ten source units rebuild through Ghidra with their locked hashes.
  No additional delayed-slot instruction or misresolved PC-relative reference is
  present.
- `patches/map-switching-startup-wrapper.s` owns `0xD22A0..0xD22FF`, and
  `patches/map-switching-limiter-commit.s` owns `0xD3660..0xD375F`. The latter
  saves and restores exact SR, masks interrupts for every runtime write, fills both
  complete limiter shadows, updates `0xFFFF1796`, clears transient state, and
  publishes the normalized index last. Fuel Cut stock addresses `0x0934E` and
  `0x09356` are only word-aligned, so all 12 fuel bytes use `MOV.W`; the aligned
  28-byte throttle cluster uses seven `MOV.L` copies. Their 71 instructions and 48
  literal bytes are SHA-locked. Fourteen Ghidra p-code cases cover direct commit and
  startup for indices 0-5 and 255 using exact stock containers, synthetic alternate
  slots, and surrounding RAM sentinels. All 14 pass over 1542 executed instructions.
- Rev Limit - Fuel Cut is read with two adjacent stock words through the unique
  `0x4F468` literal, so its active shadow contains the complete 12-byte cluster.
  Throttle limiting is consumed through the `0x09424..0x0943F` cluster and a secondary
  scalar path, so its active shadow preserves all 28 stock bytes and replaces only
  `0x0942C`.
- Limiter shadows, `0xFFFF1796`, and the new index form one SR-protected transaction.
  The active-index byte is stored last. The reference model exposes no partially
  updated state. The standalone SH unit passes source-order and p-code gates. The
  complete locked composition repeats those scenarios at final addresses and
  preserves exact entry SR; interrupt latency remains a hardware validation gate.
- Exact JK08A mailbox record `0x09766 = 03 08 AA 20` configures HCAN1 transmit
  mailbox 3 with DLC 8 and standard ID `0x551`. `FUN_000C3ED2` dispatches that
  record through the unique literal at `0xC3FA4`, whose stock target is serializer
  `FUN_000C5372`. The serializer writes payload bytes to
  `0xFFFF3AD5..0xFFFF3ADC`; byte 5 at `0xFFFF3ADA` contains the low two-bit ASCD
  status state. The hook target `0xD35E0` calls the stock serializer first and may
  replace only those two bits while visual feedback is active.

Map slots have numeric identities only. No firmware or definition artifact assigns
driving-profile semantics to maps 2-5. `tools/mapkit/map_switching.py` projects the
manifest into the common `JK08A.xml` and `JK08A.xdf`. Every approved switchable
family appears as `Map 1` through `Map 5` inside its canonical functional
category, reusing the canonical JK08A storage type, scale, axes, mask, and editor
increments. Map 1 points to stock data; maps 2-5 point to allocated copies
initialized with identical bytes in the first bench image. Calibration values are
edited manually after the identical-map bench gate.

`tools/mapkit/validate_map_switching.py` validates the live 450-map graph and the
490-map common projection without writing files. The tracked definitions contain
58 calibration tables and 11 masked views. The switchable subset contains 50
calibration tables plus ten ignition bit-7 views, for 60 slot-specific editor
views. Both formats retain the common `JK08A` identity; no separate map-switching
definition exists.

In a stock image, Map 2 through Map 5 expose erased `0xFF` allocations that runtime
code does not reference. Their presence in the common definition does not imply
stock map-switching support. Global engine-model, sensor, diagnostic, NATS, code,
pointer, and checksum objects are not duplicated per slot.

The target pilot contains ten independently switched storage families:

- Ignition Timing Trim Main `0x09A1A`;
- Ignition Timing Trim High Det `0x09B1A`;
- Fuel Targets `0x0B33A`;
- Fuel Compensation Main `0x0A29A`;
- Rev Limit - Fuel Cut `0x0934E`;
- Rev Limit - Throttle Cut `0x0942C`;
- DFCO held-request threshold `0x126E4`;
- DFCO rising-edge entry threshold `0x12718`;
- DFCO lower/full-restore threshold `0x12818`;
- DFCO upper/intermediate-restore threshold `0x1298C`.

Main and High Det timing are paired so a detonation-mode transition cannot cross
slots. Fuel Targets and Fuel Compensation Main form the main fuel group. Fuel Cut
and Throttle Cut form the runtime rev-limiter group. This grouping does not
promote evidence confidence: the tuner-facing AFR projection of Fuel Targets and
the physical names and scales of the rev limiters remain candidate until
controlled hardware validation. Cold Ignition Timing, Stationary Rev Limiter,
speed limiting, axes, knock sensitivity, VTC/VVEL, sensor models, and diagnostic
objects remain global in the pilot.

The overrun group is a complete DFCO switch. Hold threshold `0x126E4`, Entry
threshold `0x12718`, Full Restore threshold `0x12818`, and Intermediate Restore
threshold `0x1298C` each have five slot instances. Shared hook `0x4FDD0` carries
Hold or Entry, while shared hook `0x50258` carries Full or Intermediate Restore.
The adapter identifies the exact incoming base before selecting a slot pointer.

The timing maps retain complete bytes in every copy: bits 0 through 6 carry the
timing adjustment and bit 7 carries the knock-window flag. RomRaider and TunerPro
may expose both masked views without creating separate storage.

All ten families have exact-ROM access traces, fail-closed reference behavior,
allocated copies, pointer tables, and executable model tests. All ten runtime
access paths have standalone assembled and p-code-emulated units: fail-closed lookup
adapters for eight families and one atomic shadow transaction for both limiter
families. The selector host is also assembled and SHA-locked. Its 17 Ghidra p-code
cases cover the state machine, commits, aborts, feedback blocking, diagnostic
mirror, invalid-index recovery, and protected registers. The CAN feedback wrapper
and leaf pulse engine are assembled and SHA-locked. Nine p-code cases cover 17
serializer invocations and preserve every payload field except byte 5 bits 0-1.
Their locked frame counts are `10, 10`; a zero/zero pair remains the fail-closed
disabled configuration. The deterministic in-memory composition
applies all eight blobs, 14 hooks, 40 copies, and ten pointer tables. It changes
5630 bytes inside the 6144-byte declared write set and has fixture SHA-256
`ee274610baedd42a46f555589fbc10206d66cc912662cef8eebef219a353b6cd`.
It ties all 414 instruction byte pairs and eleven code entries to their final
absolute addresses. `EmulateMapSwitchingComposition.java` independently rebuilds
that fixture from the exact Ghidra program and passes all 116 scenarios over 5140
instructions. Every scenario starts from a fresh complete image, all eleven code
entries execute, real pointer tables and copied calibration bytes are checked,
the limiter restores exact SR, and the other paths preserve every non-T SR bit.
The composer exposes no output-file operation, leaves stored checksums unchanged,
and reports `flashable=false`.

`map-switching-payloads.toml` tracks the complete SHA-locked machine-code spans.
`apply_map_switching.py` accepts checksum-valid JK08A inputs with lower-partition
calibration/configuration changes while requiring the exact protected upper ROM,
identity, anchors, and erased allocation. It initializes maps 2-5 from the input
Map 1 values, installs the runtime, recalculates all checksum domains through
`jk08a_checksums.py`, proves byte preservation outside the composition and checksum
fields, and creates a non-overwriting ROM plus MD5 sidecar.

`upgrade_map_switching_reset.py` accepts only the complete pre-fix runtime with
the locked old startup wrapper, the old `0x29CC=0xFFFF5D00` literal, all other
payloads, hooks, and pointer tables intact, an exact protected upper partition
outside declared map-switching and checksum storage, and valid input checksums. It restores the
stock anchor, installs the reset-fixed wrapper, recalculates all checksum domains,
and proves that calibration bytes remain unchanged. The reset-fixed tuned candidate
has SHA-256
`3e37f03a2ac879714556ab720fa657eb4132d1b22ecdccbb2c4edce631842ced` and remains
hardware-untested.

Raw DID `0x130E.bit7` is reserved as prototype instrumentation: clear means map 1 and
set means maps 2-5. It is deliberately absent from the stock support mask. The
driver-visible contract uses one through five CRUISE-indicator pulses after a valid
commit. The official UpRev guide independently documents five map slots and a
flashing cruise-control light, but this contract does not claim UpRev's internal
implementation.

The factory manual establishes the ECM ASCD-status CAN signal as the physical route to
the combination meter CRUISE indicator. A homologous Z34 community decoder maps CAN
0x551 byte 5 value `2` to active cruise status. The byte and value align with the
exact JK08A serializer, but V36 applicability remains candidate evidence until a
target-vehicle test confirms the lamp response. Feedback advances once per 0x551
serialization, preserves the upper six bits of byte 5 and every other payload byte,
and does not modify `0xFFFF41AE`, `0xFFFF4252`, or another stock ASCD control state.
The pilot uses ten on frames and ten off frames. Their wall-clock duration depends
on the target's actual 0x551 period. The patcher creates derived map-switching
images; no derived image is versioned in `rom-images/`.

## Current/prior-cycle coefficient surface - `0x0C78E`

Map `0x0C78E` is a live unsigned 16x16 coefficient surface in internal state
calculation `FUN_000a5a06`. Wrapper `0x262A8` evaluates its row axis `0x14F62`
from full uint16 Base Fuel Schedule word `ffff1024` and its column axis `0x13EA4`
from current engine-speed word `ffff11bc`. The row points span raw 0..40960; the
homologous diagnostic conversion `x/2048 ms` remains candidate. The column points
convert by the code-proven `x*12.5 RPM` representation to 0, 800, 1200,
1400..3600, and 10000 RPM.

The current lookup result `C[n]` is written to `ffff3080` and zero-extended before
multiplication. The prior result `C[n-1]` is read from retained state `ffff9ab0`
and also zero-extended. SH instructions at `0xA5DE2..0xA5E02` form two signed
products, shift each right by one, add them, and shift the sum right by two. The
coefficient term is combined with two independently calculated signed terms shifted
right by one and 13. The composite is saturated, split into a signed coarse word and
residual through arithmetic shift by 12, and then adjusted by subtractive map
`0x13CE8`. The bounded coarse output is written to `ffff3106`. At
`0xA6328..0xA632A`, `ffff3080` replaces `ffff9ab0` for the next invocation.

A whole-program p-code scan covers all 2315 recovered functions without decompiler
failures. It finds no access to `ffff3080` or `ffff3106` outside
`FUN_000a5a06`; both addresses are staging fields of this retained state rather than
external publications. The map's physical subsystem and fixed-point value scale are
unresolved. Its `0..64000` range is insufficient to assert a Q0.16 representation.

## Engine Torque surface - `0x10B8E`

Map `0x10B8E` is a live offset-binary 16x16 uint16 Engine Torque surface.
`FUN_00065928` copies the 16-word array at `0x2378C` to a local buffer through
byte-copy helper `0x22558`, then calls wrapper `0x262A8` with map `0x10B8E`, RPM
axis `0x14B4A`, and the local copy as the second axis. Resolver source `copy`
preserves the byte-identical ROM origin of the stack operand in the graph.

The RPM coordinate is current word `ffff11b6`. Axis `0x14B4A` contains
`128, 256, ..., 1664, 1920, 2176, 2432`; candidate catalog scale `x*3.125 RPM`
gives 400..7600 RPM. The second coordinate is

```
q = min(65535, floor(u16[ffff1024] * 40960 / ROM16[0x9534]))
```

and is stored in `ffff15c4`. Stock `ROM16[0x9534]=0x6A5A`. Axis `0x2378C`
contains `0x0000, 0x1000, ..., 0xF000`; candidate catalog scale
`x*160/65536 %` gives 0..150% Cylinder Filling and reduces the coordinate
formula to `100*BFS/scaler`. The lookup result is centered by subtracting
`0x8000` and stored as signed word `ffff18ca`. Raw map range 31944..37084
corresponds to -82.4..431.6 Nm under candidate Engine Torque scale
`x*0.1-3276.8`.

`FUN_000659ae` adds unsigned term `ffff2408` to signed `ffff18ca`, applies a
Q14 multiplier and Q8 complement `256-lookup_u8(0x1245A)`, saturates to int16,
and writes `ffff18cc`. Stock `ROM8[0x87EE]=0` makes the Q14 multiplier unity;
map `0x1245A` and its axis `0x11A55` are flat zero, making the Q8 multiplier
unity. The stock expression is therefore
`ffff18cc=sat_s16(s16[ffff18ca]+u16[ffff2408])`. Functions `0x655B4` and
`0x65B08` consume this state in two nonlinear channels.

`FUN_00065c26` builds `ffff2408` from RPM curve `0x154A0`, a
Base-Fuel-Schedule-dependent subtraction, and a calibrated nonnegative
correction. Stock `ROM8[0x87F3]=32` makes that correction zero. `FUN_000658a4`
scales RPM curve `0x14C1A` by a selected nonnegative byte difference and writes
`ffff14e2`; `FUN_00065cd8` and `FUN_00064a1c` consume it in the same signed
torque-state component. Curves `0x154A0` and `0x14C1A` therefore have code-level
engine-torque base/correction roles, with candidate physical scale `x*0.1 Nm`.
Their shared axis `0x14ABA` has the code-proven `x*12.5 RPM` representation and
spans 800..7600 RPM.

Owned VQ35HR ROM JK00D contains the homologous accessor `FUN_00067be8` with the
same 126-byte structure. It uses map `0x12922`, byte-identical RPM axis
`0x16F3C`, column axis `0x23884`, and scaler `0x95F6=38557`; JK08A uses scaler
27226. The VQ35 map's candidate range -117.0..605.5 Nm and the larger scaler are
consistent independent family evidence for the Engine Torque identity. Physical
units and both catalog-derived percentage/torque scales remain hardware-validation
items.

Map `0x152D6` is the code-proven EVAP negative-pressure leak transfer. Its explicit
axis is `0x13C18`. `FUN_000B2096` indexes the curve by baseline-relative coordinate
`0xFFFF2C92` and stores `0xFFFF3240`; caller `FUN_000B29B8` builds corrected and
saturated coordinate `0xFFFF2C98`, performs the second lookup, and stores
`0xFFFF3242`. The consumer uses only the positive transformed difference, normalizes
it with `0xFFFF2C86`, and writes intermediate `0xFFFF3018`. The final result is
`sat_u16(uint8[0xFFFF2F8D] * uint16[0xFFFF3018] * uint8[0xFFFF2F94] >> 14)` at
`0xFFFF301C`; P0442 and P0456 monitor branches consume its high byte.

Direct producer paths copy shared EVAP sample `0xFFFF10C4` into baseline
`0xFFFF2ABC`, call `FUN_000ABB84`, and clamp a negative return before writing
`0xFFFF2C92`. The helper contract is
`min(65535, floor((uint16(baseline)-uint16(current))*112/32))`; the lower clamp
belongs to its callers. The stored `0x152D6` points differ from `sqrt(12.75*x)` by
less than 0.566 raw at the knots, establishing a square-root-like measured shape but
not an exact formula. The same map and axis byte sequences occur in the registered
VQ37VHR pair at `0x16B32`/`0x15492`, VQ35HR JK00D at
`0x177E8`/`0x15FCA`, VQ25HR JK03A/JK08A at `0x152D6`/`0x13C18`, and JK78C at
`0x16524`/`0x14F5C`.

Factory ESM pages EC-274 and EC-316 identify the surrounding P0442/P0456 strategy
as a negative-pressure leak test. EC-529 defines the Service 06 publication unit as
`1/128 mm2`, but no firmware trace binds that conversion to `0x152D6` or
`0xFFFF301C`; all internal coordinates and results remain raw. Adjacent stock-selected
map `0x12282` also has `code` confidence: its lookup result is one of the two byte
multipliers in the final product. The shared right shift by 14 does not prove an
individual fixed-point scale for either multiplier.

### Intake CVTC main/cold target component - `0x0B43A`, `0x0B53A`, and `0x0AB5A`

`FUN_000BD170` is the two-channel intake CVTC dispatcher. It updates centered timing
bytes `0xFFFF2442` and `0xFFFF2443`, calls target accessor `FUN_000BDA64`, calls coolant
selector `FUN_000BDC66`, and then runs the paired downstream control calculations.
Within this dispatcher, `0x0B43A` is the 16x16 warm/main intake-cam target surface,
`0x0B53A` is the 8x8 cold target surface, and `0x0AB5A` is a conditional 4x4
subtractive correction.

`FUN_000BDA64` indexes all three surfaces by current RPM/50 byte `0xFFFF11AE` and
load-like byte `0xFFFF102C`. It writes the cold result to `0xFFFF1C5E`. The main
result is written to `0xFFFF1C5C`; when `0xFFFF2466.bit6` is set, the stored value is
`clamp_u8(main - correction + 128)`. The code establishes the conditional correction,
but not the physical meaning of the selector bit. The A2L name High Detonation Intake
Cam Timing therefore remains candidate evidence.

Stock raw coolant thresholds are `ROM8[0x8D2E]=106` and `ROM8[0x8D2D]=131`.
`FUN_000BDC66` selects the cold target at `coolant <= 106`, selects the main target at
`coolant > 131`, and uses the following interpolation between the thresholds:

```text
cold + floor((coolant - 106) * (main - cold) / 25)
```

The selected byte is copied to `0xFFFF1BEE`, then mode, rate, and offset logic writes
conditioned target/reference byte `0xFFFF2326`. `FUN_0004D2A6` compares this byte with
both centered intake-cam timing channels in the cam-deviation path. This consumer and
the CVTC dispatcher establish the physical target family independently of the catalog.

Axes `0x12F3E`, `0x12ECA`, and `0x12F9A` have code-proven `RPM = raw * 50` scaling.
Axes `0x12F1E`, `0x12EAA`, and `0x12F92` receive `0xFFFF102C` directly. Their Cylinder
Filling name and `raw * 0.78125%` scale remain A2L candidates because the physical
producer and conversion of `0xFFFF102C` are unresolved. Map values use centered raw
128 in code. The candidate engineering conversion `(raw - 128) * 0.5 degrees` comes
from the HR A2L and homologous intake-cam diagnostics and requires hardware validation.

## P0128 thermostat-model balance terms - `0x0D40E`, `0x14B0A`, `0x14CCA`, and `0x151F2`

`FUN_000B5908` is the P0128 monitor dispatcher. Counter `0xFFFF33F8` makes it invoke
`FUN_000B6B5A` every tenth pass. Its two completion branches pass descriptor index
`0xCB`; the exact descriptor record at `0x19CE4` contains DTC P0128.

At the start of the coordinator, `FUN_000B7B98` evaluates uint16 surface `0x0D40E`.
Axis `0x13D74` receives current RPM/12.5 word `0xFFFF11BC`; axis `0x13DB4` receives
current Base Fuel Schedule word `0xFFFF1024`. The second source has exact DID 0x1208
identity, while its `x/2048 ms` conversion remains a homologous-profile candidate.
A nonzero aggregate six-channel inhibit mask `0xFFFF22E0` forces the surface term to
zero. Otherwise, the lookup is multiplied by the maximum of two selected byte
coefficients and written as uint32 `0xFFFF2D04`.

The whole-program xref projection has one writer and one reader for `0xFFFF2D04`.
`FUN_000B6B5A` calculates

```text
T = sat_u32(ffff3220 + sat_u32(ffff3228 + ffff2f98))
D = (u32[ffff2d04] >> 1) - (T >> 1)
```

and stores `D` in `0xFFFF33FC`. `FUN_000B7C84` clamps it to -107350..107350,
calculates `K=min(ROM8[0x8542]*ROM8[0x8543],10735)`, applies
`trunc0(20000*D/K)`, and saturates the result to -200000..200000 in
`0xFFFF3400`. Stock bytes 20 and 8 give `K=160` and an unsaturated gain of 125.
The transformed term is added to `0xFFFF3348` with signed saturation before the
monitor continues.

Every cell of `0x0D40E` and every point of both axes is zero in JK03A and JK08A.
The stock lookup and `0xFFFF2D04` are therefore always zero, but the scheduled call,
signed balance, scaler, and downstream state are live. Code proves a P0128 model
balance contribution; it does not establish a physical heat-flow quantity or an
engineering scale for the surface values.

The preceding coordinator path also calls `FUN_000B784E`, which looks up three
RPM/12.5 curves over shared axis `0x13CA8`. The result of all-zero curve `0x15C40`
is returned through a stack word and becomes the coordinate for all-zero axis
`0x13FF4` and all-zero uint16 curve `0x14B0A` in `FUN_000B7768`.

The exact UDS table maps DID 0x1106 to `0xFFFF2837`. Homologous measured Nissan
diagnostics identify it as Intake Air Temperature with `deg C = raw - 50`;
`FUN_00020DFE` snapshots the byte to `0xFFFF2733`. `0xFFFF3348` is the signed
P0128 model-temperature state: it is seeded as
`1000000 * uint8[0xFFFF1071] - 50000000`, otherwise loaded from retained state
`0xFFFF9DF0`, and updated by the saturated balance later in the coordinator.
`FUN_000B7768` calculates

```text
L = lookup_u16(0x14B0A, 0x13FF4, lookup_u16(0x15C40, 0x13CA8, RPM_12_5))
d = clamp(trunc0(ffff3348 / 10000) - 100 * uint8[ffff2733] + 5000,
          0, 32767)
ffff2d08 = floor(d * floor(L * ROM8[0x8543] / 256) / 256)
```

The shared `raw - 50` temperature representation makes `d` the nonnegative
model-temperature-minus-IAT difference in 0.01 deg C units. `FUN_000B6B5A` forms
`0xFFFF3220 = sat_u32(0xFFFF2D00 + 0xFFFF2D08)`, placing this term on the
subtractive side of the P0128 balance. The whole-program xref projection has one
writer and one reader for `0xFFFF2D08`. Because `0x14B0A`, `0x13FF4`, and
upstream curve `0x15C40` are all zero, `L` and this term are always zero in stock
JK03A and JK08A. The coefficient's physical heat-transfer interpretation and
engineering scale remain unresolved.

The third accessor, `FUN_000B78DA`, receives previous-cycle coarse vehicle speed
`0xFFFF110E`, the same IAT snapshot and model-temperature state, and nonzero
parameter `P` from RPM/12.5 curve `0x15BF0`. `FUN_000B784E` replaces a zero
`0x15BF0` lookup with one. The accessor calculates

```text
P = lookup_u16(0x15BF0, 0x13CA8, RPM_12_5); if P == 0: P = 1
d = clamp(trunc0(ffff3348 / 20000) - 50 * uint8[ffff2733] + 2500,
          0, 32767)
c = ROM8[0x86D2] if uint8[ffff110e] <= 2 else ROM8[0x86D3]
B = min(floor(d * c / 2), 65535)
q = max(0, 65535 - floor(20 * ROM16[0x9292] * ROM8[0x8819] / P))
x = lookup_u16(0x14CCA, 0x13B38, q)
w = 255 - min(x, 255)
ffff2f98 = floor(P * floor(B * w / 255) / 250)
```

The `raw - 50` IAT representation makes `d` the nonnegative
model-temperature-minus-IAT difference in 0.02 deg C units. Coarse speed selects
two calibrated coefficient bytes at `<=2` versus `>2` counts, approximately
`4 km/h` under the homologous vehicle-speed scale. The map supplies inverse weight
`w`; its clamped conversion is not expressible as an invertible map scale in the
current definition vocabulary. `FUN_000B6B5A` adds `0xFFFF2F98` to
`0xFFFF3228` with uint32 saturation before placing the sum on the subtractive
side of the P0128 balance. The whole-program projection has one writer and one
reader for both `0xFFFF35A0` and `0xFFFF2F98`.

All cells of `0x14CCA`, axis `0x13B38`, and upstream curve `0x15BF0` are zero
in JK03A and JK08A. Stock `P` is therefore one and the map weight is 255. Both
speed-selected coefficients at `0x86D2`/`0x86D3` and both coordinate constants
at `0x9292`/`0x8819` are zero, so `B` and `0xFFFF2F98` are always zero. The
physical heat-transfer interpretation and engineering meaning of `P` remain
unresolved.

The fourth term accessor, `FUN_000B7A3C`, receives conditional parameter `H` from
RPM/12.5 curve `0x15C80`, runtime selector `S` from `0xFFFF178E`, the same IAT
snapshot and model-temperature state, and previous-cycle coarse vehicle speed.
`FUN_000B784E` writes the `0x15C80` result when the model-temperature threshold is
met and one otherwise. `FUN_00048400` constrains `S` to values 0 through 3; code
does not identify the physical subsystem represented by those states. The accessor
calculates

```text
d = clamp(trunc0(ffff3348 / 20000) - 50 * uint8[ffff2733] + 2500,
          0, 32767)
B = min(floor(d * ROM8[0x8A30] / 2), 65535)
A = lookup_u16(0x14E42, 0x13BB8, uint8[ffff110e] << 8)
q = max(0, 65535 - floor(20 * A * ROM8[0x8832] / H)) if H != 0
q = 65535 if H == 0 and A * ROM8[0x8832] == 0 else 0
x = lookup_u16(0x151F2, 0x13BF8, q)
w = 255 - min(x, 255)
K = 10 if S == 0 else ROM8[0x8A35] if S == 1 else
    ROM8[0x8A36] if S == 2 else ROM8[0x8A34]
ffff3228 = K * floor(H * floor(B * w / 255) / 2500)
```

`FUN_000B6B5A` is the only reader of `0xFFFF3228`; it adds the word to
`0xFFFF2F98` with uint32 saturation before placing the sum on the subtractive side
of the P0128 balance. Stock `ROM8[0x8A30]` is zero, so `B` and `0xFFFF3228` are
always zero. `ROM8[0x8832]`, all three table-selected state coefficients, both maps,
and both axes are also zero. The hard-coded coefficient 10 for `S=0` cannot change
the zero result. Code proves a state-weighted inverse-weight term; its physical
heat-transfer interpretation, parameter `H`, and engineering scale remain unresolved.

## EVAP fuel-level coordinate and sentinel - `0x14BCA`

`FUN_000C456C` handles encoded CAN identifier `0x5000` from the meter dispatcher.
It assembles two ten-bit payload fields. The field used here is:

```text
ffff3e24 = payload[1] + ((payload[2] >> 6) & 3) * 256
```

The homologous VQ35HR factory ESM states that the combination meter sends the
fuel-level sensor signal to the ECM over CAN. The exact JK08A diagnostic descriptor indices used by the
consumer are `0x45` for P0461 and `0x46` for P0460, independently fixing the
fuel-level monitor context. Voltage, percentage, and tank-volume conversions remain
unresolved.

`FUN_0003DAC6` scales the field into an unsigned coordinate:

```text
q = min(65535, floor(39680 * uint16[ffff3e24] / 1024))
```

It conditionally retains `q` in `0xFFFF3E26`, then updates slow state `0xFFFF27FC`
through `FUN_0003DA98` with stock coefficient `ROM8[0x8315]=1`, corresponding to
1/256 of the new sample. Initialization seeds the filter directly. Result-state
predicates for indices `0x14A`, `0x45`/P0461, `0x46`/P0460, and `-1` select either
the filtered coordinate or zero. Both the normal and reset paths evaluate
`0x14BCA` over axis `0x13AC8` and write `0xFFFF282E`.

The 16 axis points are:

```text
0, 3642, 3643, 10307, 14918, 19878, 24335, 28558,
32085, 34642, 36580, 38400, 44800, 51200, 57600, 64000
```

The scheduler copies the complete 0x104-byte current-state block to its previous-cycle
snapshot, including `0xFFFF282E -> 0xFFFF272A`. A whole-program p-code scan completed
all 2315 functions with zero failures. It finds exactly two direct writes to
`0xFFFF282E` and seven reads of the snapshot in `FUN_000AE5A4`, `FUN_000AF076`,
`FUN_000B2096`, and `FUN_000B3A54`.

The EVAP consumers use the snapshot high byte in two forms. Signed checks interpret
`0xFFFF` as `-1` and reject operating windows that require a nonnegative value.
`FUN_000B2096` uses the unsigned high byte as the coordinate for coefficient curves
`0x1259A`, `0x125A2`, and `0x125AA`. Stock `ROM8[0x893F]=0xC0` selects `0x125AA`;
coordinate 255 selects its terminal cell, raw 133, in the P0442/P0456 leak-monitor
calculation.

All 16 cells of `0x14BCA` equal `0xFFFF` in JK03A and JK08A. The table therefore
publishes a live, constant sentinel regardless of its input: the signed high byte is
`-1`, while the unsigned high byte is `255`. The map is classified at `code`
confidence as a fuel-level-derived EVAP coordinate and sentinel curve with raw
identity scaling. Its physical engineering conversion remains unresolved.

The strict JK08A projection contains 1660 source claims and 6348 `RESTS_ON` edges.
The exact audit reports zero missing, extra, duplicate, unresolved, downgraded, or
ungrounded claims. The catalog contains 364 `code` maps and 86 `candidate` maps;
semantics are present for 443 maps and scaling for 405. The diagnostic projection
contains 150 reviewed JK08A bindings and 34 inherited exact-code JK03A bindings.

## Main fuel calculation closure

The subsystem model is maintained in `JK08A.fuel.md`. The established static
chain is:

```text
dual-bank MAF -> combined airflow -> newest/current BFS
              -> Fuel Compensation Main 0xA29A through ffff1160
              -> periodic fuel multiplier ffff22e6
              -> current-pass transient and Q14 gain
              -> two bank/parity bases
              -> six raw and six transformed compensated pulse words
```

`FUN_0003BE3C` is the runtime writer that connects `0xA29A` to Q7 coefficient
`0xFFFF1160`; raw 128 is neutral. Separate word `0xFFFF115C` is selected from
other working sources and enters the following BFS stage. These values are not
the same calibration layer.

Periodic table order proves `FUN_0004ED88` inhibit mask at index 27,
`FUN_00057608` fuel-multiplier coordinator at 35, `FUN_00053698` common-gain
builder at 39, transient coordinator `FUN_000522C4` at 41, precursor
`FUN_0004E974` at 42, and six-channel builder `FUN_0004ECAC` at 60. Full mask
`0x3F` makes `FUN_000556EC` publish zero to `0xFFFF22E6` before the pulse
precursor runs.

`FUN_0004E974` produces two bank-indexed words at `0xFFFF18C0/0xFFFF18C2`.
`FUN_0004EAD4` applies STFT, LTFT, an extra bank term, a startup-neutral
`0x8000` correction, and common additive word `0xFFFF2436` to form parity bases
`0xFFFF191C/0xFFFF191E`. `FUN_0004EBA2` reuses them across six channels and
writes raw array `0xFFFF23C8..0xFFFF23D3` plus the exact affine-floor transform
at `0xFFFF23D4..0xFFFF23DF`.

The static hardware boundary remains explicit. The inhibit mask independently
reaches the six ATU-II channel-8 one-shot outputs through `FUN_0002C13C`, but a
whole-program p-code census does not connect either calculated pulse array to
that scheduler's source words. Physical pulse units, terminal order, injector
closure, and any hidden transfer mechanism remain bench or engine validation
items.

## Next step

The corrected revision-2 lookup chain through stage 14 has hardware status
`PASS_EXACT`. The pending hardware gate is the five-image full-DFCO chain from
that exact readback. Stages 15 through 17 install and activate complete per-slot
DFCO handling while selector execution remains absent. Stage 18 activates the
selector host as a boot-only gate and forbids a map-selection gesture. Stage 19
activates CAN feedback and is the complete ten-family runtime endpoint.

The locked `10, 10` composition passes disassembly plus 17 selector, 76 adapter,
14 startup/limiter, and nine feedback p-code cases. GNU `sh-elf-run` independently
assembles all eight payloads and executes the same 116 behavior cases. The
file-writing patcher, checksum recalculation, overlay hash chain, and byte
preservation checks pass their positive and negative tests.

After stages 15 through 19 pass, the first functional target-vehicle test uses
byte-identical maps. With the vehicle stationary and engine stopped, verify the
steering-switch ladder, CAN 0x551 byte 5 state `2`, visible `10, 10` pulse timing,
and one through five indications without changing stock ASCD state. Then confirm
reset Map 1, raw DID 0x130E bit 7, startup and critical-section timing, and
unchanged engine behavior while selecting all five identical maps. A separate
stock-period capture is not a prerequisite for this first test.

The static reverse-engineering priority remains fuel, ignition, and cutoffs;
additional logs are not a prerequisite for the current static track.

The map-annotation backlog remains represented in ledger `JK08A.maps.csv`. The frozen
positional worklist of 396 source positions has been processed in full, positions 0-395.
The follow-up semantic pass is built from the current projection, which contains 7
`candidate` maps without semantics in 4 accessor-connected components. Every open
map is flat. Map-analysis results are recorded
as findings in `JK08A.findings.csv`, not written to the ledger: the ledger is a graph
projection, so direct edits would not survive regeneration.

Column `vals` partitions the follow-up work: six maps contain `0..0`, and one contains
`32768..32768` across the entire table.
`tools/mapkit/show.py` prints a map with its axes
(`show.py b33a` prints the grid in physical units together with both axes).

The entry-point inventory is complete: 39 regional entry points are listed and all 35
table-driven entries have been transcribed. Open questions remaining after the
transcription:

- **Only backtracking identifies two bases** - `0xA05A` and `0x15320`. At selector site
  `0xBE39A`, data flow does not resolve pair `0xA05A`/`0xA09A`; at `0x661BE`,
  backtracking disagrees with data-flow base `0x15330`. Neither backtracking value is a
  fact. Alternatives `0x12412`, `0x1252A`, and `0x12B32` are resolved as `phi` nodes
  and are present in the graph.
- **14 axes occur only on fallback branches** at `pattern` confidence. The census
  projection for `0x14114` still includes false axis `0x8000`, but the complete
  FUN_00073432 listing proves that `0x8000` is an offset-binary bias and the actual
  search axis is an RPM-interpolated stack row from `0x0E98E`; see "An axis also
  selects a branch". This group also includes `0x119B2`, the only axis not read by
  the core's inverse linear search.
- **18 maps contain only `0xFF`** (11 byte maps and 7 word maps), indicating either
  unprogrammed flash or a saturated limit. The signature is identical, and only the
  consumer trace distinguishes them; the data shape alone is not evidence.
- **Liveness** - the inventory detects a code reference but not whether calibration
  enables the branch. Two cases were found behind one gate: `0x121F6` and `0x12206` are
  disabled by ROM byte `0x8D92=0x7A` (see "A branch can be disabled by calibration").
  The complete size of this class is unknown because the inventory model does not cover
  this dimension.
- **Axis semantics outside `0x26944`** - axes through `0x26984` (offset binary,
  `x-32768`) and `0x26714` (reciprocal pairs) were annotated at `code` in wave 2
  (`0x15da0`/`0x15db0`/`0x13a68`/`0x18fd6`); physical units remain unresolved because
  inputs arrive from callers outside the components (`0x5fac0`, `0x60fb4`). Axes
  through `0x26B84` were not analyzed separately.
- **The value multiplier of emitted maps** is not always derived from code: the
  `0x934E` fuel-cut table's `x*12.5` comes from the A2L catalog and native speed-domain
  convergence, is marked with `[cand]` units, and requires hardware confirmation.
  The `x-64` scale does not apply to `0xB61A`/`0xB71A`/`0xB81A`: finisher
  `0x268a4` saturates cells >= `0x80`, so the value cannot represent degrees (see
  "Rotation-monitor thresholds").

Follow-up worklist for 7 `candidate` maps without semantics:

1. Trace paired zero curves `0x154C0` and `0x154E0` through `FUN_0007AF78`, including
   the selector, input coordinate, output destinations, and downstream arithmetic.
2. Record a finding in `JK08A.findings.csv` (map semantics, confidence, and units) and,
   when its axis is resolved, in `JK08A.axes.csv`; record the name and category in
   `JK08A.overrides.toml`. `emit_def.py` builds the definition on the next run. Verify
   against the map shape and downstream RAM output.

The component queue is derived from the current Memgraph projection rather than stored
as a second worklist. The JK08A graph provides accessor-to-map components and caller
trees; each accepted result is recorded in the canonical CSV sources before the graph
and ledger are rebuilt.

Structural row and column orientation is resolved for the five 2D maps through kernel
`0x26944`. Axes driven by `0xFFFF11AE` have code-proven RPM and `x*50` scaling from the
current engine-speed producer. The physical identity and scale of `0xFFFF102C` remain
unresolved; Cylinder Filling and `x*0.78125%` are catalog candidates. Separate axis
`0x11ECE` has its own code-proven RPM scale through `0xFFFF11BC` arithmetic.
