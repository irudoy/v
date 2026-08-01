
# JK08A - definition annotation log

RE log for working definitions `JK08A.xml` and `JK08A.xdf` for the project's own dump
`rom-images/23710-JK08A/1JK08A-20260726-stock.bin`
(Nissan Skyline V36 250GT, VQ25HR, 23710-JK08A, SH7058 / 1 MiB, JDM).
SHA-256 `ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23`.

Forum-sourced `JK03A` remains a separate donor ROM. The images differ at 121 byte
positions in calibration/config, but none falls within the 2312 functions in the Ghidra
export. All 16 `rom_const` values from structured evidence match. Of 443 maps, only four
currently unnamed candidate curves differ: `0x15360`, `0x15380`, `0x19090`, and
`0x190b0`; all 229 axes match. `JK08A.*` is the sole live source of structural and
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
- Layer measured from the image [CONFIRMED]: values of all 443 maps and 229 axes are
  read from each ROM's registered image by the same run that builds the layer (Stage 4,
  `tools/mapkit`). JK08A uses `1JK08A-20260726-stock.bin`. Axes carry their points and
  monotonicity; maps carry content range and hash. Two signals remain open: one axis is
  not read by reverse linear search (`0x119B2`), and 18 maps contain only `0xFF`.
- Element encoding [CONFIRMED]: a 1D map's input reads the element, while for a 2D map
  the finisher reads it; all five 2D finishers read elements as unsigned.
  `storagetype` is known for all 443 maps in the graph. Three byte-oriented 2D
  finishers handle bit7 differently: `0x26770` treats it as part of the value,
  `0x267CC` treats it as a pass-through flag over a 7-bit value, and `0x268A4`
  saturates it (values 0..127). See "2D map element encoding".
- The catalog contains **443 maps**: the resolver obtains 436 through 34 entries
  (248 explicit-axis and 188 implicit-axis), while the manual layer declares seven:
  three direct comparator tables, two implicit-2d input maps for `0x26040`, and two
  direct per-cylinder Knock Slice maps. No map belongs to more than one family; the
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
  explicit allowlist of 12 calibration tables and three masked ignition views.
  Research maps and inactive families remain in the graph and ledger. Calibration
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
- Paired contribution curves: 1D-64 uint16 maps `0x141F4`/`0x14274` have
  code-level operational semantics through a complete exact-JK08A machine trace.
  Their physical identification as MAF remains `candidate`; sensor identity,
  bank/channel mapping, units, and nontrivial scale are unknown. Injector latency,
  speed limiter, and the remainder of the `0x12xxx` cluster are not annotated.


## Exact JK08A paired-contribution trace

The stock image is the primary machine-evidence source. The complete 456-byte listing
of `FUN_0003B520` closes the def-use path that was absent from the donor-derived
artifact:

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

Code therefore proves paired contribution and partition semantics, but it does not
prove that the physical inputs are MAF signals. The unique catalog-family match and
homologous VQ35HR factory monitor keep the MAF binding at `candidate` confidence.


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
`00085a70` derives thresholds for a crankshaft-rotation nonuniformity monitor; their
role is `table` and sentinel is `0x80`. Code does not establish the physical input
quantity or map-value multiplier. The monitor name, inferred from algorithm shape as a
misfire detector, is not established by code and remains `candidate`. Confirmation was
independently checked against the image and graph outside agent runs
(`wf_94cbe023-181`, pilot Section 8 gate).


### Misfire-monitor component - classifier, readiness, and counters (accessor FUN_00082c8a)

The threshold trio feeds one subsystem. Accessor `FUN_00082c8a` and consumer
`FUN_00085a70` form a crankshaft-rotation-nonuniformity misfire detector. Run
`wf_94cbe023-181` annotated the entire component, containing 14 maps, 3 axes, and
7 flags. It was originally consolidated in `08a5b04:defs/JK03A.findings.csv` and
transferred to `defs/JK08A.findings.csv`. Its remaining nodes are:

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

**Five-level ladder `0x1265A`..`0x1268A` (candidate, threshold).** Four boundaries
`t0..t3` through wrapper `0x26388`, implicit 1D-16, classify `ffff1024>>8` into level
`ffff2b4b`; the complete meaning of the boundaries is not traced.

**Counting readiness `ffff41d2` (gates).** Two thresholds feed condition
`ffff41d2 & 3 == 3`, which enables incrementing misfire counters:

- `0x12DE2` (candidate) sets bit 0 of `ffff41d2` at site `0x8397a` when
  `output(2*ffff1070) <= ffff1071` and three related checks pass.
- `0x12026` (candidate) sets bit 1 at site `0x8391a` through `ffff42a8 == 0` and masks
  `ffff244f`/`ffff4184`.
- Bit 2 is a combined counting permission formed from six conditions, including
  `ffff4251 & 0x80` and windows over `ffff11b3`/`ffff1024>>8`; `00082c8a` reads it as
  `pbVar[0x4e] & 4`. Its confidence is `candidate`: two terms are bits 0/1 from the
  previous pass.

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

Component confidence is `code` for the trio, classifier, event counters, and flags
`ffff4217`/`ffff41c3`/`ffff4218`; it is `candidate` for the ladder, readiness gates, and
bit 2 of `ffff41d2`. Threshold-map scales have not been derived (offset-binary), while
counter scale is identity in event-count units.


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
shared between families. The manual layer declares three direct comparator tables,
two implicit-2d input maps for `0x26040`, and two direct per-cylinder Knock Slice maps,
bringing the complete graph to **443 maps**.


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

In the graph, 256 of 586 `:ACCESSES` edges carry an uncollapsed axis
(`kind5/kind6=sp`), and 14 of 229 axes are named by nothing else. The fallback can be
wrong for axes just as it can for bases. Direct evidence is site `0x735ac`, which names
`0x8000` as an axis even though erased flash begins there:

```
0x8000 as words: [65535, 65535, 65535, 65535, ...]   # entire array is 0xFFFF
```

An axis named only by the fallback therefore stays at `pattern`, not `candidate`.
Any collapsed site (`pool`, `slice`, or `const`) promotes it to `candidate`; without
such a site, the fallback word is a heuristic. Axes of all nine maps emitted by the
definition are collapsed.

The same mechanism creates ambiguous geometry. `0x14114` carries two axes on its
`:AXIS_X` edge, `0xE98E` and `0x8000`, both from `k5=sp` sites in accessor `0x73432`
using entry `0x264f8`. Meanwhile `0xE98E` itself is a 16x16 map through entry
`0x262e0`, whose `r6` axis is `0x14114`; all eight of those sites are collapsed
(`pool`/`slice`). Data shape does not resolve this mutual declaration, but operand
confidence does: the collapsed side states a fact, while the uncollapsed side guesses.
The definition gate rejects such a map; resolution belongs to Stage 6.


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

Axis `0x11ECE` uses different RAM input `ffff11bc`, and machine arithmetic establishes
comparison domain `x*4` in internal units. User-facing RPM scale `x*50` and range
400..7400 rpm remain `candidate` from A2L homology. Code confirms axis structure but
not its physical unit.


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

The returned Boolean enters `FUN_0004ED88`, which combines global and
per-channel inhibit masks and writes `0xFFFF22E0`.


### Over Run Fuel Cut and Restore tables

The deceleration fuel-cut path is a separate sequence in `FUN_0004ED88`
[CONFIRMED by code]:

```text
FUN_0004FBE2  cut request
  + FUN_00050018  restore/inhibit state
  -> FUN_000503E0  timed fuel-cut state machine
  -> aggregate mask
  -> ffff22e0
```

Both threshold accessors use `uint8[0xFFFF106F]` as their 16-point input and
compare selected table outputs with `uint8[0xFFFF11B3]`. `FUN_000384FE`,
`FUN_000384CC`, and scheduler `FUN_00020DFE` prove that `ffff11b3` is engine
speed in RPM/25 representation.

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

| address | code role | registry family | stored scale |
|---|---|---|---|
| `0x126E4` | first cut threshold | Bosch Fuel Cut | `x*25 RPM` |
| `0x12718` | second cut threshold | JECS/Hitachi Fuel Cut | `x*25 RPM` |
| `0x12818` | second restore threshold | JECS/Hitachi Fuel Restore | `x*25 RPM` |
| `0x1298C` | first restore threshold | Bosch Fuel Restore | `x*25 RPM` |

The Bosch versus JECS/Hitachi names rest on the exact four-table order declared
by the Nissan A2L registry and repeated in homologous Nissan definitions. JK08A
is a Hitachi ECU, so `0x12718` and `0x12818` are the operational family pair.
The firmware still contains and reads both family thresholds under
mode-dependent branches. The working definitions expose only the operational pair
as `Overrun Fuel Cut` and `Overrun Fuel Cut Restore` under `Fuelling / Overrun`;
the Bosch pair remains in the graph, ledger, and presentation source.

At 80 deg C, the JECS/Hitachi cells are 1050 RPM cut and 900 RPM restore. At
110 deg C they are 1400 RPM cut and 1200 RPM restore. Calibration edits require
hardware validation because additional gates, offsets, delays, and state
transitions can prevent or defer the visible result.

The stock six-channel scheduling path remains:

```text
FUN_000522C4
  -> FUN_0005727A
  -> FUN_00052034
  -> FUN_00051A98
  -> FUN_00051F1E
  -> FUN_0002C13C
```

`FUN_00052034` writes pulse/update eligibility mask `0xFFFF1220` from
`0xFFFF22E0`, per-channel state, and signed-difference threshold
`ROM8[0x87FE]<<7`. `FUN_0002C13C` schedules selected ATU-II channel 8
down-counters. No diagnostic fuel-cut-state binding is claimed.


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

The physical sample quantity represented by `0xFFFF1026`,
`0xFFFF1024`, and `0xFFFF1028` remains unknown.


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


### Independent calculated-load and fallback schedule paths

The exact JK08A image closes the complete path from `0x1491A` to the standard
calculated-load response:

- `FUN_0008083C` indexes the 16-cell uint16 table by
  `uint8[0xFFFF11B3] << 8`. Wrapper `FUN_000263F4` uses the complete interpolation
  kernel `FUN_00026A60` and unsigned linear finisher `FUN_00026740` below
  coordinate `0xF000`; the upper branch returns cell 15.
- With lookup result `M`, the producer calculates
  `q = floor((uint16[0xFFFF1024] << 8) / M)`. If
  `ROM8[0x870E].bit4` is set, it additionally calculates
  `q = floor((q << 7) / uint8[0xFFFF329F])`; a zero optional divisor forces 255.
  The final value is clamped to 255 and written to `0xFFFF413E`. Other entry gates
  can force 0 or 255.
- Factory diagnostic dispatcher `FUN_00035634` selects the Mode 01 handler
  `FUN_00035856`. Its PID `0x04` branch returns `0xFFFF413E` directly through the
  response-byte writer. Freeze-frame code copies the same byte. Standard physical
  conversion is `100*A/255`.

Code therefore establishes the calculated-load normalization role of `0x1491A` and
the exact output representation. The A2L name `Load Base Fuel Schedule Table`, BFS
unit, multiplier `x*0.000488`, and static RPM axis remain catalog-level candidates.

Table `0x15630` belongs to an independent path and has no machine connection to the
two-channel `0x141F4`/`0x14274` branch:

- Initialization in `FUN_0002C648` looks up `M` by
  `uint8[0xFFFF1077] << 8`, writes raw `M` to `0xFFFF1E44`,
  `floor(M/4)` to `0xFFFF1E40`, and writes
  `min(65535, floor(M*uint8[0xFFFF1160]/512))` to `0xFFFF1062`.
- Runtime function `FUN_0003B75C` reads the table only on a fallback path. The
  fallback is selected when `uint8[0xFFFF2804] == 0`, when
  `0xFFFF4185.bit7` is set and `0xFFFF437A != 0`, or when
  `0xFFFF4185.bit6` is set and `uint8[0xFFFF2804] < 0x20`. It writes
  `min(65535, floor(floor(M/4)*uint8[0xFFFF1160]/128))` to `0xFFFF1062`.
  The main branch creates the same common result through independent arithmetic
  without reading `0x15630`.
- `FUN_00039316` uses `4*0xFFFF1062` as an absolute-difference tolerance.
  `FUN_0003A750` uses the same four-times value as a comparison width around
  `ROM8[0x8AD9] << 8`. These consumers close the operational path but do not name
  its physical quantity.

The generated name `Fallback Source Table - BFS candidate scale (0x15630)` reflects
the code boundary. Shape matching to the catalog entry `Cranking Base Fuel Schedule
Table` and multiplier `x*0.000488 BFS` remain candidate evidence only.


### UDS SID 0x22 ignition, injection, and intake-CVTC response paths

The exact JK08A UDS dispatcher and ReadDataByIdentifier handler establish the
request-to-RAM path independently of public PID lists:

- `FUN_0002F928` compares the service byte with `0x22` at `0x2F9C4` and jumps
  through literal-pool entry `0x2FB00` to `FUN_0003235C`.
- `FUN_0003235C` indexes the `0x11xx` pointer table at `0x226AC` or the `0x12xx`
  table at `0x2289C`. A normal `0x11xx` entry returns one byte. A normal `0x12xx`
  entry returns two consecutive bytes in big-endian order. Both paths emit
  positive response SID `0x62`.
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
With `0xFFFF2497.bit2` clear, current speed coordinate `0xFFFF11BC` at or above the
selected activation threshold arms optional delay `0xFFFF24F1`; stock
`ROM8[0x8C69] = 0` activates state bit 2 immediately. While active, speed below the
selected release threshold clears the state. The returned Boolean enters
`FUN_0004ED88`, which converts any active global inhibit condition to mask `0x3F` and
writes the final six-channel injection-output mask `0xFFFF22E0`.

The public HR A2L catalog defines the matching 2x2 layout as Normal/Reverse columns,
Cut/Restore rows, with `x*12.5 RPM`. Under that candidate physical interpretation the
stock values are:

| Fuel state | Normal | Reverse |
|---|---:|---:|
| Cut | 7650 RPM | 7450 RPM |
| Restore | 7450 RPM | 4600 RPM |

Code proves the table address, 2x2 layout, hysteresis, active state, and global
six-injector inhibit path. Axis labels and the RPM multiplier remain catalog-supported
candidates pending CONSULT/bench validation.


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
`400..7400 rpm` at scale `x*50`. Kernel `0x269C4` converts points to internal domain
`x*4` for comparison with RAM `ffff11bc`; this internal representation is not the
RomRaider user scale.

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

Registry `JK08A.dtc.csv` contains 29 analyzed descriptor/attribute pairs for catalyst,
rear O2, rear O2 heater, EVAP, manufacturer-specific P1422, and NATS P1610. In
28 emissions records, stock attribute `0x00A0` contains bits `0x80` and `0x20`:
`0x80` participates in OBD/emissions representation, while `0x20` is used when
initializing runtime diagnostic status.

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
descriptor entry. Six additional patches are generated from the registry `group`
column: `catalyst`, `evap`, `manufacturer_specific`, `nats`, `rear_o2`, and
`rear_o2_heater`. These patches contain 4, 26, 2, 1, 16, and 8 entries respectively,
covering the same 57 mutable ranges as the 29 individual patches. No patch combines
all DTC groups. Individual and group patches overlap by design and every entry carries
the exact stock bytes as `basedata`.

P1610 is at index 40: descriptor `0x19540` contains
`0D 05 00 00 00 00 16 10 00 00 00 00`, and its associated attribute is at
`0x160FE`. Its stock and disabled values are both `0000`, so P1610 suppression changes
only the 12-byte descriptor. Generator `emit_def.py` emits only the P1610 descriptor
switch in RomRaider and only the descriptor entry in both TunerPro patch scopes.


## Candidate areas [CANDIDATE] - require confirmation from code

- Ignition timing: trio `0x991A`/`0x9A1A`/`0x9B1A` is annotated at `code`
  confidence as Cold/High Octane/High Detonation Ignition Timing Maps. Trio
  `0xB61A`/`0xB71A`/`0xB81A` contains thresholds for the crankshaft-rotation
  nonuniformity monitor and does not enter the ignition path.
- Strong pointer anchors without attribution: `0x0975A` with 13 references and
  `0x11FB6` / `0x11EBE` with 3 each. Pointer clusters in `0x16000..0x163xx` form a
  calibration region for fuel/torque.
- Limiter physical closure: `0x942C` has a continuous code path through the signed
  limiter arbiter and controller stages to shared request coordinate `ffff19c6`.
  Exact UDS bindings expose four banked throttle-position feedback values and the
  throttle-motor relay state, but no static path reaches a bank-specific angle command,
  motor PWM register, or ECM terminal. `0x934E` has a continuous code path into the
  global six-channel fuel-output inhibit mask; its Normal/Reverse labels and RPM scale
  still require hardware validation.


### ETC / electronic throttle - inverse conversion pairs (accessor FUN_0003b498)

Component `0x3b498`, containing 20 maps and 22 accessors, is an electronic-throttle
and airflow-calculation subsystem. Its structural backbone consists of **inverse
pairs**, where a map and its axis are each other, both 1D-32:
`0x13202`<->`0x155a0`, `0x15500`<->`0x15690`, and
`0x15540`<->`0x156d0`. Code establishes the pairs through wrapper `0x26524`, kernel
`0x26984`, sites `0x3b6c2`/`0x3b6e0`/`0x3e5e6`/`0x3e604`, and accessors
FUN_0003b520/FUN_0003e548. Physical identities flow/opening-area and scales
`x*0.0008`/`x*0.001525879` come from a catalog shape match to 1D-32 ETC rather than
a trace. RAM axis inputs are unresolved, so the pairs' physical semantics remain
`candidate`.

Selector flags, with selector role established and semantics candidate, are bits 0/1
of `ffff23a6`, which select the source for interpolation `0x13202`/`0x155a0` in
FUN_0003e548, and bit6 of `ffff4246`, which makes FUN_0003b468 forward
`ffff3a76` to `ffff1e60` when clear or select ROM default `0x916c` when set. Consumers
(`0x3b468`, `0x6f236`, `0x70d20`, `0x72e5e`, `0x74728`, `0x7acb4`, `0x7b2c8`,
`0x82604`) confirm a closed throttle/airflow/torque loop: FUN_0003b468 writes
`ffff3a76` to `ffff1e60`, which FUN_0003b498 reads back. They do not establish
physical units. Maps `0xe98e` of the 16x16 torque class, `0xd68e`/`0x10b0e` of the
8x8 class, flat maps `0x14cea`/`0x15082` containing `0xFFFF`, and `0x15062` cannot be
classified as `dead` because no disabling branch is found. `0x14ea2` is read by a
different accessor, FUN_0007ab18; ROM[`0x83c1`] bit0=0 makes its branch unreachable
and establishes `role=dead`.


### Ignition-angle accumulator in degrees - `ffff23ee` (accessor FUN_0004afdc)

Component `0x4afdc` adds a set of maps into a **signed ignition-angle sum** in degrees
at `ffff23ee`. Mode-selected base maps are `0x12196`/`0x1219e`/`0x121a6`, three
variants of which `0x12196` and `0x121a6` are byte-identical. Wrapper `0x26370` reads
them by index `ffff11b2`; the result with bias `-0x80` reaches `ffff1511` as a sum
term. Corrections are `0x11f0a`/`0x11f12`, with branch selected by bit2 of
`ffff244f`; `0x11f1a`, gated by bits 0 and 1 of `ffff22e1`; and flat-zero but live
`0x11f22`. They feed `ffff12db` and use index `ffff106f`. 2D surface `0x9dba` is
read from two banks selected through `ffff2442`/`ffff2443` by wrapper `0x26140`;
folding `(r1+r2-256)/2-128` reaches `ffff1514`.

Code establishes element conversion `x-128` for the base and 2D maps; double `-128`
means one `-128` per bank. Unit "degrees" and qualifier "idle" come from catalog and
vendor evidence, P6, so semantics remain `candidate`: code proves a signed angle
quantity at `ffff23ee`, but not specifically an idle path. Gate flags have code-proven
structure and candidate semantics: bit2 of `ffff244f` selects the correction branch,
bit5 of `ffff41de` gates the base, bit6 of `ffff41ab` gates a throttle subsection,
and bit4 of `ffff248d` selects an adaptive-learn path that writes `ffff1513`, consumed
by learn routine `0x4e112`. Throttle-gated pair `0x11efa`, flat at 100, and `0x147ca`,
uint16 range 15..55, reaches the sum as addend `uVar8` through `mul.l`/`0x21ce0`.
Its exact role, whether knock limit, torque ratio, or timing limit, is unresolved.
Base maps use index `ffff11b2`; corrections use `ffff106f`. These are two different
inputs, so the cluster has no single "engine speed" axis.

The exact SID `0x22` ignition-timing response path uses internal coordinate
`ffff11d4` and response byte `ffff2022`. No direct data-flow edge from the
`ffff23ee` accumulator to that path is established. The `ffff23ee` association
with the factory `IGN TIMING` monitor therefore remains a separate candidate.


### Rate-limited speed hysteresis (accessor FUN_0006205c)

Component `0x6205c` maintains a rate-limited hysteretic speed state in `ffff33a8`
(Q12) and writes a clamped value to `ffff33a4`. `0x13182`, an upper threshold,
`0x131a2`, a byte-identical lower threshold, and `0x131c2`, a direct assignment on one
branch, contain values around 7300 and are read as RPM. Code does not establish their
multiplier, so this remains candidate. `0x133d2` is ramp rate; all values are zero, so
rate=0, but the map is read and is not `dead`. `0x145ca` is multiplied by constant
map `0x1495a`, flat at 50000, through `0x21ce0`. Catalog axis `0x15ce0`, 10..160 in
steps of 10, is candidate Coolant Temp (F). Consumers of outputs
`ffff33a4`/`ffff33a8` are unidentified, so the structural rev-limit/overrun-cut
hypothesis remains candidate. **Section 6 discrepancy:** catalog shape 1D-16 suggests
Fuel Cut/Restore RPM with scale `x*25` and uint8 elements, but the actual maps are
uint16 with raw values around 7300; the catalog scale does not transfer.


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


### Crossfade blend of calibration curves - `0x7a592` / `0x7a804` (accessors FUN_0007a592, FUN_0007a804)

Both components form output by a linear Q15 blend:
`out = ((0x8000-w)*a + w*b) >> 15`, where `a` and `b` are interpolations of two
1D curves and `w` is a weight from a separate 2D map. Code establishes the complete
mechanism. Wrappers `0x26270`/`0x265f0`, kernels `0x26848`/`0x26b28`, and finishers
`0x26740`/`0x26d10` are decompiled; the "NOT ANNOTATED" caveat does not apply to this
path.

Weight maps at **code confidence**, recorded in `findings.csv`, are `0xd78e` for
0x7a592 with output `ffff31c8` and `0x16f48` for 0x7a804 with output `ffff35f4`.
They are 2D Q15 weights with scale `x/32768`; content contains only `0`/`0x8000`,
which performs hard branch selection. Multiplier evidence is pivot `0x8000` and
consumer shift `>>15`, not a catalog. `0x18d36` in 0x7a804 is also included: a Q15
multiplicative trim applied to the blend result when its gate is set. Its calibration
is flat at `0x8000`, trim=1.0 and therefore a no-op, but the branch is not dead.

Blend endpoints remain **candidate**. Code establishes structural role as term a/b,
pairing, axis `0x14f82`, and input `ffff2698`, but not the domain. In 0x7a592, pairs are
`0x1480a`/`0x1482a` when `ffff249f`&2==0 and `0x15360`/`0x15380` when nonzero, with
`0x15380` outside the component. In 0x7a804, they are
`0x18cf6`/`0x18d16`/`0x19090`/`0x190b0`. Catalog concepts load-100pct, fuel-target,
vtc-advance, and overrun-fuel-cut cover the entire geometry class but do not identify
one table. They establish a class, not identity. Endpoint labels
"load-limit"/"torque-request" were rejected as P6.

Blend control flags have code-established roles and candidate physical meaning:
bit7 at `0x83c1` selects map weight `0xd78e`/`0x16f48` versus constant `0x8000`;
bit1 of `ffff249f` selects the endpoint pair; bit6 of `ffff245e` gates trim
application; and bit6 of `ffff4214` overrides the final output from `ffff35ea`.
Rejected claims were bit0 of `ffff41f3`, where the override-gate mechanism is code but
label "load" is P6, and bit1 of `ffff249f` in 0x7a804, whose map pairing was inverted
in the claim. The latter was downgraded and the pairs were corrected from the trace.


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
`0x18e86`/`0x18f96`/`0x18e46` were downgraded to candidate. The reciprocal role is
confirmed by trace, but the physical quantity and unit are not, because RAM inputs
`ffff1d08`/`ffff1d10`/`ffff35fe` lack an identified source.

Code-confidence flags: bit6 of `ffff24ac` is a one-shot initialization latch that
gates a single baseline lookup of map `0x18766`, with test-then-set in `0x73824`;
bit5 at `0x89fb` selects interpolation versus direct passthrough in `0x74728`.
Bit4 of `ffff24ac`, claimed as threshold "clamp activated", received no verdict and
remains candidate. Code establishes signed centering `x-0x8000` for `0x175c8`, but
whether the correction applies to fuel, spark, or torque remains unresolved.
Consumers `0x73a44`/`0x74728`/`0x749bc` are arbitration/limiter paths with no named
sink.


### Additive base plus a gated product/sum - `0x55098`, `0x54ee0`

Both accessors assemble a 16-bit output as an **additive base plus a gated set of
table terms**, with saturation.

`0x55098`, output `ffff15ce`: base `ffff2ff0` plus a product of four byte multipliers
`>>12`, saturated to `0xffff`. `0x12ede` is one of four equivalent multipliers, with
neutral value 64 from default `0x40`; bit6 of `ffff246b` gates its application at
**code** confidence. Code establishes the multiplier's neutral value 64 and table
role. Label "compensation" and scale `x/64` remain candidate because shift `>>12` is
distributed across four factors and does not pin an individual scale. Base-mode
selectors bit6 of `ffff4184` and bit6 of `ffff84c3` were rejected: the switching
mechanism is code, but label "enrichment curves" is P6, and the `ffff84c3` claim joined
two mutually exclusive branches. Kernel `0x26a84`, reached by wrapper `0x26388`
through a jump/jump table, is **NOT ANNOTATED** for the component's four maps, which
remain candidate.

`0x54ee0`: output is a sum of terms, each under an OR combination of flag bits.
Code-confidence enable gates are calibration ROM byte `0x8b37`, `ffff1239`, bits 0/1
of `ffff230e`, bits 0/1 of `ffff161a` under joint condition `0x4000 < ...`, and bit1
of `ffff2485`, a one-shot initialization latch inside term2. All are selectors/gates
by control flow; the physical quantities of the terms are not traced.


### Map-variant selector flags - `0x413cc`, `0x4d2a6`, `0xbe5bc`, `0xc0d90`

A recurring pattern uses a calibration byte in ROM or RAM to select a map shape or
variant by bit. Code establishes the selector/gate role; the physical meaning of the
selection remains candidate.

- `0x413cc`: bit3 at `0x8710` selects map shape, implicit wrapper `0x26388` versus
  explicit `0x264a0` with axis `0x12778`; bit1 of `ffff244f` selects a curve pair,
  35..101 versus 27..122; bit1 of `ffff2451` gates the differential term contribution,
  multiplying by output `0x12704` with `>>3` or zeroing it.
- `0x4d2a6`: bit3 of `ffff24a9` provides hysteresis for `ffff1071` against calibration
  `0x8e03`, a threshold; bit6 of `ffff24a9` is a gate from parity of the
  `FUN_000259d0` result; bit5 of `ffff2458` selects the branch that combines outputs
  `ffff1636..1638`.
- `0xbe5bc`: bit0 at `0x8616` selects a map family, implicit
  `0x12e72`/`0x12e7a` through `0x26370` versus explicit
  `0x12e82`/`0x12e8a` through `0x26474` with axis `0x11bdb`. One family is live and
  the other dead, but the artifact does not contain the byte value, so it cannot
  identify which family is dead.
- `0xc0d90`: `ffff14c8` selects a 1D-16 variant, `0x15b10` versus out-of-component
  `0x15ad0`.


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
Physical axis inputs `ffff11bc`, `ffff1024`, and `ffff10d2` come from callers outside
the components, so their units do not reach `code` confidence.

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
a Section 6 shape-versus-trace discrepancy.


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
- `0x12a32` in FUN_000507ce is a threshold for `ffff11bc` with hysteresis 16. All
  cells equal `255`, making the threshold constant at 510 and the axis inert. The
  read is unconditional, so the map is not `dead`.
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
  relation `load[%] = 100 * (ffff1024 * 256 / x) / 255`; scale `x*0.000488`
  in ms BFS comes from the catalog, so `scale_conf = candidate`.


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

- The agent assigns `role=dead` to `0x14BCA`, but its disposition is `writes`:
  two sites write `ffff282e`, and there are no indexed readers. Absence of a reader
  does not prove a disabled branch, so the claim does not enter the manual layer.
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

- 27 Map semantics claims at `code`: `0x12522`, `0x12526`, `0x1292C`, `0x153B0`,
  `0x153B8`, `0x11C6D`, `0x11E56`, `0x11F0A`, `0x11F12`, `0x11F1A`, `0x11F22`,
  `0x11FBE`, `0x11FE6`, `0x12006`, `0x12032`, `0x12086`, `0x1208E`, `0x12096`,
  `0x120CE`, `0x1211E`, `0x12126`, `0x1212E`, `0x1215E`, `0x12176`, `0x1218E`,
  `0x12196`, and `0x1219E`. This confidence applies to a threshold, multiplicative,
  limiting, additive, or blending role directly proven by the machine trace;
- three Map semantics claims at `candidate`: `0x1202E` remains the catalog hypothesis
  Initial Retard Quantity because no external reader was found for stores to
  `ffff1ee0`/`ffff257a`; `0x141F4` and `0x14274` are 64-point `uint16` transfer curves
  with stores to `ffff1056`/`ffff1054`, but machine def-use within `0x3B520` does not
  establish the physical MAF identity or channel;
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
  `x/65536`, `0x15630` has the catalog BFS scale `x*0.000488` at `candidate`, and
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

The 29 entries in `JK08A.dtc.csv` generate 57 native `TableSwitch` controls under one
`Diagnostics / DTC` category. Each of the 28 emissions records has adjacent
`1/2 Descriptor` and `2/2 Attribute` controls. Both select either `Enabled (Stock)` or
`Disabled` and must use the same state before saving. P1610 uses descriptor `0x19540`;
its attribute at `0x160FE` remains `0000` in both states, so only its descriptor switch
is present. DTC suppression through these controls has not been validated on hardware.

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
ABI, and delay-slot contract of implemented SH source slices. The selector provides
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
  references. The manifest claims `[0xD2108, 0xD3860)` for code, 32 calibration
  copies, eight five-entry pointer tables, the CAN feedback wrapper, and its
  separate pulse engine.
  `AuditFreeRegion.java` reproduces both the claimed-range and conservative-range
  gates.
- Six families are adapter-backed. Overrun uses stock wrapper `0x26388`, ignition uses
  `0x26230`, Fuel Compensation Main uses `0x261F0`, and Fuel Targets uses `0x261B8`.
  Each adapter redirects approved bases only and tail-jumps every other base to the
  stock wrapper. Cold ignition and the Bosch overrun pair remain global.
- `patches/map-switching-adapter-helper.s` owns `0xD2270..0xD229F`, and
  `patches/map-switching-adapters.s` owns `0xD2300..0xD23FF`. Ghidra 12.1.2
  assembles and round-trip decodes 59 instructions and 68 literal bytes. The two raw
  blobs are locked by SHA-256 in the layout. Ghidra SuperH p-code passes 47/47 cases
  over 676 executed instructions: all five slots for all six families, indices 5 and
  255 falling back to map 1, Cold Ignition and Bosch pass-through, unknown fuel-base
  pass-through, exact stock-wrapper destinations, and preservation of `r5..r15`, PR,
  GBR, MACH, and MACL. Comparison instructions may change the caller-clobbered T
  bit; every other SR bit remains unchanged. This path uses no radare2 and creates
  no ROM.
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

`tools/mapkit/validate_map_switching.py` validates the live 446-map graph and the
478-map common projection without writing files. The tracked definitions contain
44 calibration tables and 11 masked views. The switchable subset contains 40
calibration tables plus ten ignition bit-7 views, for 50 slot-specific editor
views. Both formats retain the common `JK08A` identity; no separate map-switching
definition exists.

In a stock image, Map 2 through Map 5 expose erased `0xFF` allocations that runtime
code does not reference. Their presence in the common definition does not imply
stock map-switching support. Global engine-model, sensor, diagnostic, NATS, code,
pointer, and checksum objects are not duplicated per slot.

The target pilot contains eight independently switched storage families:

- Ignition Timing Trim Main `0x09A1A`;
- Ignition Timing Trim High Det `0x09B1A`;
- Fuel Targets `0x0B33A`;
- Fuel Compensation Main `0x0A29A`;
- Rev Limit - Fuel Cut `0x0934E`;
- Rev Limit - Throttle Cut `0x0942C`;
- Hitachi Over Run Fuel Cut `0x12718`;
- Hitachi Over Run Fuel Restore `0x12818`.

Main and High Det timing are paired so a detonation-mode transition cannot cross
slots. Fuel Targets and Fuel Compensation Main form the main fuel group. Fuel Cut
and Throttle Cut form the runtime rev-limiter group. This grouping does not
promote evidence confidence: the tuner-facing AFR projection of Fuel Targets and
the physical names and scales of the rev limiters remain candidate until
controlled hardware validation. Cold Ignition Timing, Stationary Rev Limiter,
speed limiting, axes, knock sensitivity, VTC/VVEL, sensor models, and diagnostic
objects remain global in the pilot.

The timing maps retain complete bytes in every copy: bits 0 through 6 carry the
timing adjustment and bit 7 carries the knock-window flag. RomRaider and TunerPro
may expose both masked views without creating separate storage.

All eight families have exact-ROM access traces, fail-closed reference behavior,
allocated copies, pointer tables, and executable model tests. All eight runtime
access paths have standalone assembled and p-code-emulated units: fail-closed lookup
adapters for six families and one atomic shadow transaction for both limiter
families. The selector host is also assembled and SHA-locked. Its 17 Ghidra p-code
cases cover the state machine, commits, aborts, feedback blocking, diagnostic
mirror, invalid-index recovery, and protected registers. The CAN feedback wrapper
and leaf pulse engine are assembled and SHA-locked. Nine p-code cases cover 17
serializer invocations and preserve every payload field except byte 5 bits 0-1.
Their locked frame counts are `10, 10`; a zero/zero pair remains the fail-closed
disabled configuration. The deterministic in-memory composition
applies all seven blobs, 14 hooks, 32 copies, and eight pointer tables. It changes
5372 bytes inside the 5880-byte declared write set and has fixture SHA-256
`499f25ed560bf8e5bc00138e29ceabf740d2f13303eb07604f2e11b537bebb16`.
It ties all 387 instruction byte pairs and ten code entries to their final
absolute addresses. `EmulateMapSwitchingComposition.java` independently rebuilds
that fixture from the exact Ghidra program and passes all 87 scenarios over 4530
instructions. Every scenario starts from a fresh complete image, all ten code
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

## Next step

Map switching is the active hardware-validation track. The locked `10, 10`
composition passes disassembly plus 17 selector, 47 adapter, 14 startup/limiter,
and nine feedback p-code cases. The file-writing patcher and checksum
recalculation pass their preservation and negative-input tests.

The next gate is an end-to-end target-vehicle test with byte-identical maps. With
the vehicle stationary and engine stopped, verify the steering-switch ladder,
CAN 0x551 byte 5 state `2`, visible `10, 10` pulse timing, and one through five
indications without changing stock ASCD state. Then confirm reset Map 1, raw DID
0x130E bit 7, startup and critical-section timing, and unchanged engine behavior
while selecting all five identical maps. A separate stock-period capture is not
a prerequisite for this first test.

The map-annotation backlog remains represented in ledger `JK08A.maps.csv`. The frozen
positional worklist of 396 source positions has been processed in full, positions 0-395.
The next semantic pass is built from the current projection, which contains 60
`candidate` maps without semantics. This is a separate follow-up worklist, not a
continuation of the frozen slice. Map-analysis results are recorded as findings in
`JK08A.findings.csv`, not written to the ledger: the ledger is a graph projection, so
direct edits would not survive regeneration.

Column `vals` partitions the follow-up work: 17 of the 60 open maps contain one value
across the entire table. These comprise 13 maps with `0..0`, two with `32768..32768`,
one with `65535..65535`, and one with `16..16`. `tools/mapkit/show.py` prints a map with
its axes (`show.py b33a` prints the grid in physical units together with both axes).

The entry-point inventory is complete: 39 regional entry points are listed and all 35
table-driven entries have been transcribed. Open questions remaining after the
transcription:

- **Only backtracking identifies two bases** - `0xA05A` and `0x15320`. At selector site
  `0xBE39A`, data flow does not resolve pair `0xA05A`/`0xA09A`; at `0x661BE`,
  backtracking disagrees with data-flow base `0x15330`. Neither backtracking value is a
  fact. Alternatives `0x12412`, `0x1252A`, and `0x12B32` are resolved as `phi` nodes
  and are present in the graph.
- **14 axes occur only on fallback branches** at `pattern` confidence, and `0x14114`
  carries two axes on a single edge. This has the same Stage 6 status and rationale; see
  "An axis also selects a branch". This group also includes `0x119B2`, the only axis
  not read by the core's inverse linear search.
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
  The `x-64` scale of `0xB61A`/`0xB71A`/`0xB81A` has already been
  resolved by trace and refuted: finisher `0x268a4` saturates cells >= `0x80`, so the
  value cannot represent degrees (see "Rotation-monitor thresholds").

Follow-up worklist for 60 `candidate` maps without semantics:

1. Classify by geometry (from the wrapper or primitive), `A2L` scale, and value
   signature: MAF, injector latency, rev/speed limiter, and the large `0x12xxx` cluster
   (primitives `0x26370` and `0x26388`). EV18A and the ProECU 370Z guide
   (`refs/ecutek/`, stock VQ37VHR maps) are donor checklists for names and geometry, not
   addresses; VVEL-specific details do not apply to the non-VVEL VQ25HR.
2. Record a finding in `JK08A.findings.csv` (map semantics, confidence, and units) and,
   when its axis is resolved, in `JK08A.axes.csv`; record the name and category in
   `JK08A.overrides.toml`. `emit_def.py` builds the definition on the next run. Verify
   against the map shape and downstream RAM output.

The scale of the open portion makes it a candidate for a Dynamic Workflow, following
the project's immo RE process: parallel tracing plus adversarial review over headless
artifacts. The JK08A graph in Memgraph (`ExportGraph.java`) provides kernel caller trees
directly.

Structural row and column orientation is resolved for the five 2D maps through kernel
`0x26944`. The physical names RPM/load and multiplier `x*50` remain at `candidate`: the
code reads raw RAM inputs but does not show their writers. Separate axis `0x11ECE` has
the confirmed internal scale `x*4` without a physical name.
