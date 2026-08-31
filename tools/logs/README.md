# Logging tools

## PEAK TRC bus audit

`peak_trc_audit.py` parses strict PCAN-View TRC 1.1 classical-CAN captures. It
validates every message number, timestamp, ID, DLC, and data length; inventories
IDs and DLCs; reports period percentiles and payload diversity; counts RTR,
warning, and error records; checks a candidate telemetry ID; and estimates
average and rolling-window bus load. The parser follows the official
[PEAK trace format specification](https://www.peak-system.com/produktcd/Develop/PC%20interfaces/Windows/PCAN-Basic%20API/PCAN-Parameter_Documentation.pdf#page=130).

TRC 1.1 does not record the configured nominal bitrate. Load calculation is
therefore disabled unless the bitrate is supplied explicitly:

```bash
python3 tools/logs/peak_trc_audit.py \
  --bitrate 500000 \
  --candidate-id 0x6F0 \
  --all-ids \
  tmp/can-dump/*.trc
```

The lower load bound counts every successful classical-CAN frame without bit
stuffing. Warning and error records are reported but are not converted into a
bit count because their four status bytes are not CAN payload. An audit with
such records therefore understates total physical occupancy.
The upper bound applies the conservative maximum stuffing count. Both include
intermission. The 100 ms and 1,000 ms peaks use rolling windows rather than
fixed timestamp buckets. A clean trace proves only absence during the recorded
states; it does not establish that an ID is unused in unrecorded vehicle or
diagnostic states. PCAN-View records error frames only when that optional trace
content is enabled, as described by the official
[PCAN-View trace documentation](https://www.peak-system.com/products/software/analysis-software/pcan-view/?no_cache=1&sword_list%5B0%5D=flexible&sword_list%5B1%5D=data&sword_list%5B2%5D=rate).

## Custom CAN telemetry decoder

`can_telemetry.py` strictly reconstructs custom telemetry groups from a selected
wire-schema JSON. The decoder is ROM-agnostic: it does not import a firmware
manifest, inspect producer identity, or depend on RAM addresses. It accepts the
compact `ID#DATA` candump form, filters one configured standard ID, requires
page 0 followed by strictly increasing page IDs, verifies the four-bit header
sequence against `tick16`, discards incomplete or preempted groups, and unwraps
`tick16` modulo 65536. A capture may begin in the tail of a group already in
progress; frames before the first page 0 are ignored as initial synchronization
rather than classified as malformed.

Decode a capture to one JSON object per complete snapshot:

```bash
python3 tools/logs/can_telemetry.py \
  --schema patches/can-telemetry-schema.json \
  --profile tuning \
  --can-id 0x6F0 \
  capture.log > snapshots.jsonl
```

The schema-2 `tuning` profile requires pages 0 through 10. It starts with
`schema_verified=false` and enables engineering-unit transforms only after
page 9 context tag 3 reports the exact protocol version, profile ID, and
profile CRC16. A later health mismatch disables conversion and increments the
reported mismatch counter. Raw source values remain present in every accepted
snapshot; transforms are emitted only for scales explicitly declared by the
schema.

Fuel-trim words retain the firmware's Q8.8 absolute-percent representation,
whose neutral value is 100.00%. The engineering correction emitted by the
decoder is therefore `raw / 256 - 100 percent`.

The final stderr marker reports complete, incomplete, malformed, and
schema-mismatch counts. The decoder never fills a missing page, combines
different sequence groups, or interpolates a dropped snapshot.

The cross-platform live dashboard in `../can_dashboard/` uses this same decoder. It
retains the latest values from rotating contexts, exposes loss and queue health,
and keeps candidate transforms visibly distinct from proven physical outputs.
The generated schema also declares exact START and STOP control frames on
`data_can_id + 1`. `can_telemetry_schema.py` validates their transport fields,
payload length, and CRC for the dashboard. Offline decoders and converters do
not transmit CAN frames.

## JK08A load-coordinate audit

`load_axis_audit.py` reconstructs both load representations from a strict
schema-2 `tuning` TRC and the exact registered JK08A ROM:

- the internal Q7 map coordinate is
  `min(255, floor(BaseFuelSchedule * 128 / ROM16[0x9534]))`;
- the J1979 Mode 01 PID `0x04` byte divides the scheduler BFS snapshot by the
  RPM-dependent 16-point reference at `0x1491A` and clamps the quotient to 255.

Run the audit on a captured drive:

```bash
python3 tools/logs/load_axis_audit.py \
  schema2-capture.trc
```

The report compares the reconstructed diagnostic byte with both the same
telemetry snapshot and the immediately preceding contiguous snapshot. The
latter is the expected alignment because the custom snapshot is taken after
the stock scheduler has copied producer values into its current working
snapshot and executed the periodic tasks. Entry gates in the diagnostic
producer can still force zero or 255, so formula agreement is evidence for the
normal path rather than a replacement for those gates.

The internal coordinate is not J1979 Calculated Load. Both are ratios of Base
Fuel Schedule, but they use different denominators and byte encodings. The
existing telemetry contains enough data to reconstruct the internal
coordinate; no wire-schema or firmware change is required.

## JK08A CVTC target-map audit

`cvtc_target_audit.py` replays the exact stock byte-axis search, Q0.16
interpolation order, coolant selection, and downstream target conditioning
against a strict schema-2 `tuning` capture. The default intake family uses
warm/main map `0xB43A`, cold map `0xB53A`, and correction `0xAB5A`. The
`--target exhaust` family uses `0xB33A`, `0xB2FA`, and `0xAB4A`. The column
coordinate is reconstructed with the same normalized-BFS formula used by
`load_axis_audit.py`; the RPM coordinate comes from the captured RPM/12.5 word.

```bash
python3 tools/logs/cvtc_target_audit.py \
  --calibration-image tmp/1JK08A-tune-v1-11.bin \
  schema2-capture.trc

python3 tools/logs/cvtc_target_audit.py \
  --target exhaust \
  --calibration-image tmp/1JK08A-tune-v1-11.bin \
  schema2-capture.trc
```

Without `--calibration-image`, the tool uses the hash-verified registered JK08A
stock ROM. An explicit image is hashed and reported, and every replay constant,
axis, and surface is read directly from that image.

The report tests same-snapshot and preceding-snapshot input alignment, separates
downstream neutralization from direct map disagreement, and reports stable
active intervals where the reconstructed map result remains unchanged for a
selected number of source cycles. Intake conditioning is evaluated against
`0xFFFF2326`; exhaust conditioning is evaluated against `0xFFFF2327`. Schema 2
also carries actual exhaust positions for both banks. The target fields are
named `intake_cvtc_target_raw` and `exhaust_cvtc_target_raw`, matching the two
common conditioned targets.

The audit validates only paths exercised by the capture. A warm-engine log with
the correction selector clear cannot validate the cold surface, coolant blend,
or conditional correction. Agreement in raw software coordinates also does not
prove the candidate degree conversion or physical camshaft response.

## JK08A ignition timing-state audit

`ignition_surface_audit.py` replays the exact bit-field-aware interpolation of
hot timing-state surfaces `0x9A1A` and `0x9B1A`. It reconstructs the Q7
normalized-BFS coordinate, selects per-map copies from an exact combined image,
and recovers complete map-selection gestures from stock CAN button input.

```bash
python3 tools/logs/ignition_surface_audit.py \
  --calibration-image tmp/1JK08A-tune-v1-11.bin \
  schema2-capture.trc
```

The report keeps the interpolated low-seven timing-state field separate from
the lower-left-cell bit-7 flag, inventories high-detonation selector state and
latched knock events, and reports the Q8 state transitions at map commits. The
`implied_direct_base_q8` value subtracts the conditional direct-branch map term
from captured `0xFFFF121A`; it is not asserted as the active branch because the
current wire profile does not carry `0xFFFF2467` or `0xFFFF2469`.

An explicit calibration image is required to replay Map 2 through Map 5. With
the registered stock image, all recovered slots intentionally resolve to the
canonical Map 1 surfaces. The audit does not convert timing state to physical
crank angle and cannot validate a cold or high-detonation branch absent from
the capture.

## PEAK TRC telemetry to MLG

`trc_to_mlg.py` converts a strict PEAK PCAN-View TRC 1.1 capture directly to
MLVLG v2. It feeds every captured frame through the same dashboard model, emits
one MLG data record per complete custom-telemetry snapshot, and retains the
latest stock RPM, vehicle speed, selector, ASCD, and dashboard-state context.
It does not replay the capture in real time.

```bash
python3 tools/logs/trc_to_mlg.py \
  --schema patches/can-telemetry-schema.json \
  --profile tuning \
  --can-id 0x6F0 \
  --tick-divisor 1 \
  schema2-capture.trc
```

The MLG start timestamp is the PEAK `$STARTTIME` plus the offset of the first
complete telemetry snapshot. PEAK stores its start as an OLE Automation local
date, so `--timezone Asia/Vladivostok` is the default and another IANA timezone
can be selected. Ambiguous and nonexistent local times are rejected rather
than assigned an implicit daylight-saving fold. Existing outputs are rejected
unless `--force` is supplied, and the output path may never resolve to the
source trace.

The `tuning` output contains 81 fields: `Date`, `Elapsed`, schema state, every
fixed and rotating telemetry value, and five stock-CAN context values. Missing
rotating contexts use IEEE 754 `NaN`. Candidate engineering transforms carry
`*` in the channel units, matching the dashboard.

No verified latitude or longitude encoding exists in the captured primary CAN
traffic, so this converter and the dashboard recorder declare no GPS channels.
`csv_to_mlg.py` still emits `gps_lat` and `gps_lon` for CONSULT recordings that
carry coordinates, and a later verified AV/navigation or external GPS decoder
restores the same field contract here.

`mlvlg.py` is the common big-endian MLVLG v2 encoder, decoder, and structural
validator used by this converter, the live dashboard recorder, and
`csv_to_mlg.py`. It checks header layout, descriptor-derived record size, block
counters, complete records, and payload CRC before an atomic output
replacement.

MegaLogViewer evaluates a channel as `(raw + transform) * scale`, so a
descriptor transform is expressed in raw counts rather than in engineering
units. It also refuses to plot a channel whose name contains `*`: the channel
is listed and selectable, and its graph stays empty, observed in MegaLogViewer
MS Lite 4.6.09. Candidate transforms are therefore marked in the units. Recorded channels derive both numbers from the same calibrations the
dashboard applies, and the recorder tests bind every channel value to the live
engineering value across a raw range.

## MLG field restamping

`mlg_restamp.py` rewrites the field descriptors of an existing MLVLG file from
the current telemetry field table. Channel identity, units, display digits,
category, and MegaLogViewer scaling live in the header, so a recording adopts
corrected calibrations without touching its data blocks. Field types and record
layout are preserved, and a channel the current table does not declare keeps
its recorded descriptor.

```bash
python3 tools/logs/mlg_restamp.py --dry-run tmp/*.mlg
python3 tools/logs/mlg_restamp.py tmp/*.mlg
```

Channels are matched by name with the candidate marker removed, so a log
written before the marker moved from names to units is still recognised. The
rewritten file is validated before it atomically replaces the original.

The current decoder and converter intentionally reject historical schema-1
`core32` and `wide54` captures. Those logs require a repository revision whose
generated schema matches their recorded profile CRC.

## Diagnostic CSV to MLG

`csv_to_mlg.py` converts semicolon-delimited, long-form diagnostic logs to
MLVLG v2 files accepted by MegaLogViewer and UltraLog. The expected source
columns are:

```text
SECONDS;PID;VALUE;UNITS;LATITUDE;LONGTITUDE
```

The source contains one parameter update per row. The converter groups rows
with the same timestamp, applies every update, and emits a full MLG snapshot.
Values not observed yet are stored as IEEE 754 `NaN`. Latitude and longitude
are promoted to regular GPS fields when present.

The MLVLG specification defines a 16-bit block timestamp at 10 us per bit, so
it wraps after about 0.655 seconds. The converter inserts hold-last bridge
records whenever source updates are farther than 0.3 seconds apart. The local
UltraLog parser detects a wrap only when the raw timestamp drop exceeds 30,000
ticks; the 0.3-second limit guarantees a wrapped drop of at least 35,536
ticks. This preserves every source update without making elapsed time
ambiguous to that parser.

The first synthetic fields are:

- `Date`: Unix timestamp at one-second resolution;
- `Elapsed`: seconds since the first source row at sub-second resolution;
- `gps_lat` and `gps_lon`: decimal degrees, included when the corresponding
  source columns contain values. These names match the project's CAN logger
  GPS field contract and are detected by the Track Map implementation in the
  local `~/src/oss/UltraLog` branch `feat/gps-track-map`.

Every PID value is stored as a big-endian F32. Empty-unit fields observed only
as zero or one use the MLG On/Off display style. MLG text is ASCII, and names
longer than 33 bytes are shortened by retaining both ends.

Latitude is validated against `[-90, 90]` and longitude against
`[-180, 180]`. Both coordinates use big-endian F32 storage, `deg` units, six
display digits, `GPS` category, unit scale, and zero transform. Their MLG
descriptors match the auto-injected `gps_lat` and `gps_lon` fields in
`~/src/embedded/canlogger`.

The published UltraLog version parses MLG but does not provide Track Map. The
map-specific compatibility statement applies to the local
`~/src/oss/UltraLog` branch `feat/gps-track-map`.

## Usage

Convert logs next to their CSV sources:

```bash
python3 tools/logs/csv_to_mlg.py tmp/logs/*.csv
```

The source date is read from the `YYYY-MM-DD` filename prefix. Unix timestamps
default to `Asia/Vladivostok`; another IANA timezone can be selected:

```bash
python3 tools/logs/csv_to_mlg.py \
  --timezone Asia/Vladivostok \
  --output-dir tmp/mlg \
  tmp/logs/*.csv
```

Existing outputs are rejected unless `--force` is provided. Each generated
file is validated for header layout, record size, rolling counters, and record
CRC before it replaces the temporary output.

## Tests

```bash
python3 -m unittest discover -s tools/logs/tests -v
```
