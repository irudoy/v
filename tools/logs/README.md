# Logging tools

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
