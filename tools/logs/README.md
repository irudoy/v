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

`can_telemetry.py` strictly reconstructs the fixed JK08A custom telemetry
groups described by `../../patches/can-telemetry-schema.json`. It accepts the
compact `ID#DATA` candump form, filters one configured standard ID, requires
page 0 followed by strictly increasing page IDs, verifies the five-bit header
sequence against `tick16`, discards incomplete or preempted groups, and unwraps
`tick16` modulo 65536.

Decode a capture to one JSON object per complete snapshot:

```bash
python3 tools/logs/can_telemetry.py \
  --profile core32 \
  --can-id 0x6F0 \
  capture.log > snapshots.jsonl
```

`core32` is bound to the selected generated schema out of band. `wide54`
starts with `schema_verified=false` and enables engineering-unit transforms
only after context tag 3 reports the exact protocol version, profile ID, and
profile CRC16. A later health mismatch disables conversion and increments the
reported mismatch counter. Raw source values remain present in every accepted
snapshot; transforms are emitted only for scales explicitly declared by the
schema.

The final stderr marker reports complete, incomplete, malformed, and
schema-mismatch counts. The decoder never fills a missing page, combines
different sequence groups, or interpolates a dropped snapshot.

The Windows live dashboard in `../can_dashboard/` uses this same decoder. It
retains the latest values from rotating contexts, exposes loss and queue health,
and keeps candidate transforms visibly distinct from proven physical outputs.

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

MLG has a 16-bit timestamp with 10 us resolution, so it wraps after about
0.655 seconds. The converter inserts hold-last bridge records whenever source
updates are farther than 0.3 seconds apart. The local UltraLog parser detects
a wrap only when the raw timestamp drop exceeds 30,000 ticks; the 0.3-second
limit guarantees a wrapped drop of at least 35,536 ticks. This preserves every
source update without making elapsed time ambiguous to that parser.

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
