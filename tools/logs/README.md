# Logging tools

## PEAK TRC bus audit

`peak_trc_audit.py` parses strict PCAN-View TRC 1.1 classical-CAN captures. It
validates every message number, timestamp, ID, DLC, and data length; inventories
IDs and DLCs; reports period percentiles and payload diversity; counts RTR,
warning, and error records; checks a candidate telemetry ID; and estimates
average and rolling-window bus load. The parser follows the official
[PEAK trace format specification](https://www.peak-system.com/produktcd/Develop/PC%20interfaces/Windows/PCAN-Basic%20API/PCAN-Parameter_Documentation.pdf#page=130).

The reader streams one row at a time: `iter_records` checks numbering and
timestamp order as rows arrive, so conversion and replay memory does not grow
with the capture. Record rows are strict ASCII. Comment rows are decoded as
CP1251, the Windows code page that PCAN-View writes on a Cyrillic system, and
an undecodable comment byte never rejects the capture.

A last row that ends without a line terminator and does not parse is a cut
tail, which an operating-system crash, a power loss, a full disk, or a copy of
a capture still being written leaves behind. The reader stops before it,
emits an `IncompleteTailWarning` that names its line and size, and records it
as `incomplete_tail` of the record stream and of `load_trace`. A row that
does not parse anywhere else, including a last row with its terminator,
rejects the capture. The Rolling Launch audit prints the excluded row under
its capture line.

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
profile CRC16 of the schema. A later health mismatch disables conversion and
increments the reported mismatch counter. Raw source values remain present in
every accepted snapshot under their field names, and a verified snapshot adds
`engineering`, the value of every field whose scale states a conversion, keyed
by the field name without the `_raw` suffix. The schema gives each field the
factor and offset, unit, candidate flag, values, or named bits that its scale
string states, and the decoder refuses a schema whose terms differ from its
scale strings.

The decoder retains the last reported `(protocol version, profile ID, CRC16)`
identity even when it rejects a mismatching health group. A producer restart
clears the previous run's identity until a health context reports another one.

Fuel-trim words retain the firmware's Q8.8 absolute-percent representation,
whose neutral value is 100.00%. The engineering correction emitted by the
decoder is therefore `raw / 256 - 100 percent`.

The producer keeps `tick16` in RAM and restarts it with the controller, so a
capture that spans an ignition cycle carries several producer runs. A tick that
falls back into the opening window `0x0000..0x00FF` from a larger value opens a
new run: the decoder keeps decoding, restarts the unwrapped tick, reports the
run index on every snapshot, counts the restart, and requires a fresh health
context before it reports the wire contract as verified again. A backwards step
outside that window is still rejected as a stale group, and a 16-bit wrap stays
inside the current run. Snapshots of different runs are never treated as
adjacent, so the audits below skip pairs that cross a restart.

STOP disables the producer and holds `tick16`, so the snapshot after START
carries the next tick and the tick does not count the time of the pause. The
time-based audits time snapshots by tick inside a running stream, where the
recorded frame time carries host queueing jitter, and add the recorded time of
each pause. A recorded step longer than `STREAM_GAP_SECONDS` of
`can_telemetry.py` (0.1 s) between snapshots of one run is a candidate. Host
queueing only delays a frame, so the lowest recorded time less tick time near
a candidate follows the stream clock: a pause raises it by the pause duration,
while a host stall that the application drains as one burst returns to the
level before it. The floor before a candidate spans `STREAM_FLOOR_SECONDS`
(1 s) of ticks, and the floor after it spans the recorded step plus that time,
which reaches past a drained burst. A candidate whose floor rises by more than
`STREAM_GAP_SECONDS` is a pause of that rise: the audits keep its duration and
never treat the snapshots on its two sides as adjacent.

The final stderr marker reports complete, incomplete, malformed, and
schema-mismatch counts together with the number of producer restarts. The
decoder never fills a missing page, combines different sequence groups, or
interpolates a dropped snapshot.

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

python3 tools/logs/cvtc_target_audit.py \
  --coolant-bands cold \
  --calibration-image tmp/1JK08A-tune-v3-1.bin \
  dashboard-recording.mlg
```

Without `--calibration-image`, the tool uses the hash-verified registered JK08A
stock ROM. An explicit image is hashed and reported, and every replay constant,
axis, and surface is read directly from that image.

An input that starts with the `MLVLG\0` signature is read as a dashboard or
`trc_to_mlg.py` recording; any other input is read as a PEAK TRC. The recorder
stores every telemetry field as its raw wire integer in F32 and an absent
field as NaN, so the eight replay inputs are exact, and it records the
snapshot's `schema_verified` state. The decoder never accepts two consecutive
groups with the same tick: a record that repeats the preceding `tick16` is a
hold-last bridge record and must repeat every channel except Date and Elapsed.
The tool rebuilds run and unwrapped tick from the event records with the
decoder's tick rule and rejects a value that is not a wire integer of the
field. An MLG therefore yields the same verified snapshot sequence as the TRC
it was converted from, and every figure of the report matches. The MLG report
gives `records=` and `bridge=` in place of the frame count and
`retained_context_max_age=n/a`, because the recording does not carry the
context tag of each snapshot; `--can-id` applies only to a TRC.

The report tests same-snapshot and preceding-snapshot input alignment, separates
downstream neutralization from direct map disagreement, and reports stable
active intervals where the reconstructed map result remains unchanged for a
selected number of source cycles. `--coolant-bands` restricts every comparison
to source snapshots whose replay falls in the listed bands (`cold`, `blend`,
`warm`). Intake conditioning is evaluated against
`0xFFFF2326`; exhaust conditioning is evaluated against `0xFFFF2327`. Schema 2
also carries actual exhaust positions for both banks. The target fields are
named `intake_cvtc_target_raw` and `exhaust_cvtc_target_raw`, matching the two
common conditioned targets.

`cold_dependent_active_to_active` keeps the active comparisons whose
coolant-selected byte differs from the main-surface byte: the cold surface
decides each of these predictions, and a replay from the main surface alone
misses all of them. The line reports `n=0` in the warm band.

The intake report also compares `0xFFFF2326` with the replayed byte
`0xFFFF1553`, over every comparison (`alternate_ffff1553_to_reference_a`) and
over the comparisons in which both bytes differ from `0x80`
(`alternate_ffff1553_active_to_active`). `FUN_000BDB66` forms the byte from
engine-speed table `0x122EA` and coolant-index weight `0x122F2`, and
`FUN_000BDC66` conditions it in place of the coolant-selected map byte while
`0xFFFF24A7` bit 1 is set. `cvtc_intake_state_audit.py` reconstructs that bit
and the operating bit that neutralizes the target, and it identifies the
rising-value ramp of the conditioner by its countdown period.

The audit validates only paths exercised by the capture. A warm-engine log with
the correction selector clear cannot validate the cold surface, coolant blend,
or conditional correction, and a cold-band interval in which the intake target
follows `0xFFFF1553` does not exercise the cold surface. Agreement in raw
software coordinates also does not prove the physical camshaft response. Both
degree conversions are code-proven through the 0.5-degree edge-phase count of
the capture handlers and the raw-unit comparison of target and actual bytes.

## JK08A intake-CVTC state audit

`cvtc_intake_state_audit.py` replays the two bits of `FUN_000BD20A` that
decide the source of intake target `0xFFFF2326` for each verified snapshot of
a dashboard MLG recording and partitions the intake comparisons of
`cvtc_target_audit.py` by the predicted path.

```bash
python3 tools/logs/cvtc_intake_state_audit.py \
  --calibration-image tmp/1JK08A-tune-v3-1.bin \
  dashboard-recording.mlg
```

Idle-source bit `0xFFFF24A7` bit 1 sets while every idle-source term passes:
engine-speed byte `0xFFFF11B2` at least `ROM8[0x8715]` plus `ROM8[0x8716]`
and held down to `ROM8[0x8715]`, BFS word `0xFFFF1024` at least
`ROM16[0x921E]`, raw coolant above `ROM8[0x871C]` and at most `ROM8[0x871B]`,
raw oil temperature above `ROM8[0x871A]` and at most `ROM8[0x8719]` while
`ROM8[0x8616]` bit 0 is set, raw IAT from `ROM8[0x8718]` to below
`ROM8[0x8717]` while `ROM8[0x870F]` bit 0 is set, battery snapshot
`0xFFFF1108` above `ROM8[0x8E0A]` and at most `ROM8[0x8E07]`, `CLSD THL POS`,
and vehicle-speed byte `0xFFFF110E` at most `ROM8[0x871D]`. Each temperature
term carries a hysteresis of 3 counts. A
failing pass reloads re-arm counter `0xFFFF2527` from `ROM8[0x8713]`; after
the first activation of a producer run the bit stays clear until that counter
expires.

Operating bit `0xFFFF246B` bit 6 is set while the idle-source bit is set or
while the battery term, the pedal off `CLSD THL POS` (with
`ROM8[0x8940]` bit 1 clear), raw coolant at most `ROM8[0x8E00]`, engine-speed
byte at least `ROM8[0x8DE9]` with a release offset of 16, and a coolant floor
all pass. Latch `0xFFFF5B2C` bit 6 selects the floor: raw coolant above
`ROM8[0x8E06]` while the latch is set and above `ROM8[0x8E03]` while it is
clear, both with a hysteresis of 3. The latch sets at raw coolant 125 and
clears below 65. While the operating bit is clear, `FUN_000BDC66` stores
neutral `0x80` unless active test IOLID 0x19 runs.

The recording carries neither the pedal idle position, the speed byte, the
fault and inhibit terms, the start delay, the re-arm decrementer, nor the
latch. `--app1-released-max` bounds `CLSD THL POS` by APP1 raw (default 153),
the speed byte is `floor(10 * vehicle_speed_kmh) // 20` of the dashboard
`0x280` speed, the unobservable terms pass, `--rearm-snapshots` sets the
re-arm wait in snapshot ticks (default 988), and `--latch` selects the
initial latch state (default both). Every constant comes from the calibration
image, and the rise rule requires reload table `0x12EFE` (or `0x12F06`) to
hold one nonzero countdown period.

The report gives the engine-speed byte of the first snapshot and, for each
coolant band, the elapsed and raw-coolant extent of the source snapshots of
its comparisons and their maximum vehicle speed. For each band it gives the
model-free discriminating count: among
the comparisons whose coolant-selected byte differs from `0x80`, from the
main-surface byte, and from the replayed `0xFFFF1553` byte, how many targets
equal each of the four. For each initial latch state it gives the class of
every comparison: `start_unresolved` for the leading comparisons that only
the start delay decides, `neutral_*` for a predicted clear operating bit,
`idle_exact`, `idle_rise`, and `idle_other` for a predicted set idle-source
bit, and `map_*` for the map path with its agreement. A rise is a run of at
least three one-count target steps spaced exactly one countdown period apart,
together with the period before its first step. The report also lists the
failing idle-source terms of each predicted-neutral comparison whose
`0xFFFF1553` byte is active and the comparisons that differ from the replayed
`0xFFFF1553` byte or from both replays.

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
from captured `0xFFFF121A` as a conditional reconstruction. When both control
bytes are available, `branch_input_pairs` counts consecutive full-rate samples
that recover the branch inputs, and `direct_difference_inputs` counts those
with current `0xFFFF2467.bit6` set and prior `0xFFFF2469.bit7` clear. The latter
byte is captured after the coordinator updates it, so the current sample's
bit 7 belongs to the next evaluation. Missing samples, stream pauses, and
decimation leave no recoverable pair.

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

The `tuning` output contains 88 fields: `Date`, `Elapsed`, schema state, every
fixed and rotating telemetry value, and six stock-CAN context values. Missing
rotating contexts use IEEE 754 `NaN`. Candidate engineering transforms carry
`*` in the channel units, matching the dashboard.

The gross torque-model state, bounded torque request, shared area-domain
target, and both flow-column coordinates use `cnt` and identity transforms.
This is a storage presentation without an engineering-scale assertion. Their
source notes retain the unresolved physical-unit hypotheses and references.

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
MS Lite 4.6.09. Candidate transforms are therefore marked in the units.
Recorded channels take both numbers from the conversion that the schema states
for the field, the one the dashboard applies, and the recorder tests bind every
channel value to the live engineering value across a raw range.

## JK08A MLG relation audit

`mlg_relation_audit.py` replays the code-level relations between the raw
channels of a dashboard MLVLG recording. Channels are matched to their wire
sources through the recorder field table, so any recording with the schema-2
`tuning` layout is accepted, and every replay constant, curve, and axis is
read from the calibration image. Engine speed in every relation is the RPM/12.5
coordinate `0xFFFF11F4`, which the audit takes from stock CAN RPM as
`(round(8 * rpm) // 25) >> 2`, because frame `0x180` carries `25 * 0xFFFF11EE`
and the coordinate is `0xFFFF11EE >> 2`. The relations are:

- the live intake-VTC duty pair against its scheduler latch, the duty
  command pair;
- intake and exhaust actual positions against a target unchanged for the
  selected number of records;
- the published total-airflow word against `floor(105 * (A + B) / 256)` of
  the two MAF transfer outputs at steady sensor inputs;
- the J1979 Calculated Load byte against its exact formula for the same and
  the prior record;
- Base Fuel Schedule against the primary-branch producer with `Q = A + B` and
  `N` twice the RPM/12.5 coordinate at steady inputs;
- each closed-loop compensated pulse word as a linear fit against
  `BFS * STFT / 0x6400 / 20.48`;
- the `110 - final timing = APC command` identity, the fuel-inhibit mask
  values, the `-307` and `+13` steps of the knock timing state, the
  high-detonation selector, long-term trim values, and raw sensor ranges.

```bash
python3 tools/logs/mlg_relation_audit.py \
  --calibration-image tmp/1JK08A-tune-v2-2.bin \
  tmp/2026-09-17_17-44-20_vq-can-telemetry-v4.0.1.mlg
```

Without `--calibration-image`, the tool uses the hash-verified registered
JK08A stock ROM. `--hold` sets the number of unchanged prior records that
qualify a steady input (default 6) and `--target-hold` the steady-target
window (default 100). The output is one `key = value` line per statistic in
TOML syntax, so a run can be carried into `patches/hardware-results.toml`.

Every relation is evaluated in raw software units. Agreement proves that the
recorded channels are the quantities the code connects; it does not prove a
physical unit, and the injection fit reports the gain and additive term of
the pulse chain rather than an electrical pulse width.

## JK08A long-term trim audit

`ltft_publication_audit.py` relates the long-term trim channels of schema-2
`tuning` recordings to the LTFT publisher `FUN 00057B26` and the learned-cell
selector `FUN 0005796C` of the calibration image. It compares each bank's
tag-0 learned cell and adjustment term with its tag-2 published word.
Bank 1 uses `0xFFFF2306`, `0xFFFF5648`, and `0xFFFF2302`; bank 2 uses
`0xFFFF2308`, `0xFFFF564A`, and `0xFFFF2304`. The
tag phase is the tick residue on which front A/F word `0xFFFF2780` changes; a
recording with more than one residue is refused. Brackets, learned pairs,
cell visits, and intervals lie inside one running stream; the capture seconds
include the recorded duration of stream pauses.

`summands_b1_available` and `summands_b2_available` state which comparisons
the recording supports. Bank 1 retains its historical output keys; bank 2
uses the `b2_` prefix for publication and learning figures. A recording without
bank 2 summands reports their absence and emits no bank 2 comparison figures.
The duty-pair audit likewise reports `intake_duty_bN_pair_available` when the
recording carries only live intake-CVTC duty. Historical scheduler-latch
channels remain readable by their recorded names.

The learning-control figures count the observed bank bits of both permit
bytes and bit 0 of the neutralization byte. They state sample availability
and both-permit overlap for each bank. They assign no physical cause to a
closed composite gate and do not infer a learning rate from a permission bit.

- Publication: a tag-2 refresh is bracketed when the tag-0 refreshes two
  ticks before and three ticks after it predict the same word
  `clamp(learned + adjustment - 0x6400)`. The audit counts exact matches,
  exact matches with a non-neutral prediction, forced neutral words, other
  values, and refreshes between two different predictions. It clamps
  unconditionally; the publisher skips the clamp on `0xFFFF230E` bit `b` or
  when `uint16[0xFFFF15FC] <= int16[0xFFFF15FE]`, which the stream does not
  carry.
- Learning: a learned change is a difference between tag-0 refreshes five
  ticks apart. The selector is replayed from Base Fuel Schedule and the RPM/50
  word with the axes and hysteresis read from the image. A change between two
  tag-0 samples of one replayed cell visit of at least five snapshots is an
  in-visit change, and an update when it stays within
  `max|STFT - 0x6400| * max(gain) >> 8` of the capture.
- Permits: for each bank, the intervals of bit `b` of `0xFFFF1458` with
  their standstill and moving seconds by the dashboard `0x280` speed, and
  the ticks they expect at one tick
  per `ROM8[0x57CA1]` revolutions of the stock engine-speed word, the reload
  immediate of `FUN 00057C78`. The `0xFFFF1457` pulses are rising edges of
  bit `b`, with the share inside a `0xFFFF1458` interval; fewer pulses than
  expected ticks mean that snapshots miss the one-pass pulse. The audit
  counts permit snapshots below `ROM8[0x8CFD]` coolant or with af_adjustment
  outside `ROM16[0x8ECC] < value <= ROM16[0x8ECE]`, the seconds from the
  warm window start to the first permit, and af_adjustment decreases under a
  permit with the share whose permit clears before one tag period after the
  later sample. An in-visit update counts with the permit or the pulse when
  that bit is set between its two tag-0 samples. A `0xFFFF41B5.bit0` pulse
  counts as a refill when both learned words read `0x6400` at the next tag-0
  refresh. A recording without the permit bytes emits none of these figures.
  A snapshot that lacks a permit byte is unobserved, not clear: it ends an
  interval, and a drop or an update whose window shows neither the sought bit
  nor the opposite bit counts as unobserved. The figures also report the
  unobserved snapshots of the capture and those between the warm window start
  and the first permit, which make its time an upper bound.
- Warm window: the part of the capture after coolant reaches `ROM8[0x8CFD]`,
  with its D, P, and closed-loop proxy seconds and the fueled snapshots whose
  RPM/12.5 word reaches the `0xC0` MAF summary gate of `FUN 0004F736`.
- Drive profile: D time, the seconds and intervals inside `--speed-band`,
  the final P interval with its median STFT, and the D intervals with the full
  fuel-inhibit mask.

```bash
python3 tools/logs/ltft_publication_audit.py \
  --calibration-image tmp/1JK08A-tune-v3-1.bin \
  tmp/logs-09-22/7-cruise.mlg
```

Without `--calibration-image`, the tool uses the hash-verified registered
JK08A stock ROM. `--speed-band` sets the speed band in km/h (default 80 100).
The output is one `key = value` line per statistic in TOML syntax.

Every relation is evaluated in raw software units. The closed-loop proxy and
the replayed cell are software constructions, not recorded ECU states.
Profiles before 8 carry the bank 2 published word without its summands and
none of the permit bytes. Profiles 8 and 9 carry the summands of both banks
but not the composite gate terms of `FUN 00058740`. Profile 8 carries the three
control bytes on page 3 of every snapshot; profile 9 carries them only while
its dynamic page 3 holds configuration 0.

## JK08A Rolling Launch captures

`rolling_launch_audit.py` reads the verified snapshots of a dashboard MLVLG
recording or a strict schema-2 `tuning` TRC and audits the Rolling Launch
hold. Each snapshot carries the stock button and dashboard frames, vehicle
speed, coolant, and the fuel-inhibit, timing, pedal, BFS, knock-surface, and
exhaust-CVTC telemetry sources, and the Rolling Launch phase and abort reason.
The other Rolling Launch fields are slots of the page configurations of the
dynamic page (`can-telemetry.md`, Dynamic page). The configuration byte of a
snapshot names the slots it carries; the reader leaves the others None,
because the dashboard holds the last value of a slot that the snapshot does
not carry.

```bash
python3 tools/logs/rolling_launch_audit.py --image <flashed image> <capture>...
```

- Engine speed is the coordinate `0xFFFF11F4` in counts of 12.5 RPM, which
  the reader takes from stock frame `0x180`. The frame is sampled at another
  instant of the cycle, so every RPM word is the interval between the frames
  recorded with the snapshot and with the next one, widened by 8 counts,
  100 RPM, beyond the excursion that registry entry
  `can_telemetry.stock_speed_bracket_2026_09_22` records.
- A TRC is replayed through the dashboard model. It adds the times of the
  first and last page of every snapshot group and of the `0x239` and `0x551`
  context frames, measured from the trace start.

The hold audit reads the Rolling Launch record of the flashed image at the
span of the runtime endpoint that `patches/runtime_endpoints.py` classifies:
the current schema 6 record with its efficiency table, or the record of a
registered historical endpoint, with one integral gain for every map
(schema 4) or per-map slots with the fixed ignition trim (schema 5). The
first output line names the endpoint. The audit reports every run of
contiguous `ACTIVE` snapshots. A historical endpoint carries the speed hold
alone:

- The speed error of every `ACTIVE` snapshot lies inside the abort window.
- The replay of `patches/rolling_launch.py` starts from zero integrator and
  full torque after `IDLE`, and from the published values of a run without
  its `IDLE` predecessor. The model integrator follows each published error;
  a published integrator must equal it and replaces it, and a snapshot
  without the error leaves it unknown. A published torque fraction must lie
  within the model step from the previous fraction, or from the range that
  the rate limit allows after a snapshot without the fraction.
- Configuration 1 (`launch_law`) carries the error, the fraction, and the
  cut-request counter on every tick, so every fraction of a run that starts
  after `IDLE` equals its model step. Configuration 2
  (`launch_law_integrator`) alternates its groups: a group-0 snapshot follows
  the integrator of the group-1 snapshot before it, and its fraction lies
  within the model range of the two-tick step.
- In hold mode, the cut requests from the `IDLE` snapshot before a run
  through the snapshot after it lie within the cuts that the delivered
  fractions owe the spark events of the bracketed engine speed: three events
  per revolution, the fraction ranges on both sides of each tick update, the
  2.75 cuts of the accumulator offsets, the truncation of six accumulators,
  and one event at each end. The counter counts the cut requests of the
  spark actuator, not withheld sparks: a requested cut whose dwell arming
  precedes the dwell-start veto still fires.
- The floor ticks of a hold run count the snapshots whose stock APC command,
  `110 - final_timing_raw` modulo 256, plus the trim of the map slot lies
  past the floor command of the slot.
- The abort reason is the context value five snapshots after the run, which
  the rotation has refreshed since the abort.
- The target range is the `0x280` speed minus the published error; it stays
  narrow while the speed word follows that frame.

The current runtime selects the RPM or the speed regulator at activation. The
packed views of configurations 3 through 6 name the regulator kind of every
snapshot, and a run keeps one kind:

- Configuration 3 (`rl6_law`) carries the control error, the law output, the
  cut-request counter, and the applied trim with the actuation-ready bit on
  every tick. Under the RPM regulator every output equals the fraction of the
  error and the soft width of the map slot, and the error plus the target of
  the slot lies between the stock frames. Under the speed regulator the
  replay above checks the outputs of a run that starts after `IDLE`. Without
  the ready bit the applied trim is zero; with it the trim stays within the
  trim of the regulator, and the floor ticks count the snapshots whose trim
  the floor clips.
- Group 1 of configuration 4 (`rl6_actuation`) checks the published cut
  fraction q against the law output and the efficiency, kind, and ready bit
  of the same snapshot: zero without the ready bit, `1000 - p` under the RPM
  regulator, and the cut fraction of `u` at the efficiency under the speed
  regulator; the efficiency is a table value of a trim up to the trim of the
  regulator. Group 0 carries the consumed q sum and the counter together:
  between two of its snapshots the cut requests lie strictly within six of
  the owed cuts, the q sum difference over 1000, and from the group-0
  snapshot before a run through the one after it they lie in
  `(owed - 3.25, owed + 2.75]`. A gap or an interval that owes too many cuts
  for the 8-bit counter leaves the bound open.
- Configuration 5 (`rl6_inputs`) checks the speed-input bits, the accepted
  CANCEL, the speed frame age, a speed sample in the decoded range of the
  `0x284` word, one target per run, the RPM target of the map slot, the RPM
  sample between the stock frames, and the shared command: the effective
  command is the stock command, or the stock command with the trim clipped
  by the floor. The speed target equals the speed sample of the snapshot
  that first shows the accepted CANCEL after `IDLE` plus the target speed
  offset of the endpoint (`selected_target=checked`). An edge snapshot of
  group 1, which carries no speed sample, brackets the target between the
  speed samples of the contiguous group-0 snapshots before and after it
  plus the offset (`bracketed`). A capture without the edge, a neighbour,
  or across a gap reports the target `unchecked`. A TRC also checks every
  speed sample against the `0x284` frames of the frame age limit and two
  ticks before its group: the sample equals the word over ten of a frame
  whose word is not `0xFFFF`.
- Configuration 6 (`rl6_release`) adds q without the ready bit and the
  release: the snapshot that shows the accepted RELEASED after a run and
  every inactive snapshot after it up to the next run or a gap publish a
  zero cut fraction, and the cut-request counter of the release snapshot
  holds through that interval. The runtime takes no veto decision after
  RELEASED, so a single cut request after the release snapshot fails. A
  dwell that a decision at its arming suppressed at or before the release
  tick can still miss its spark after the release without a cut request; at
  most the spark of each such dwell is missing. A cut request up to the
  release snapshot belongs to the run: the tooth handlers of the release
  tick precede the engine pass that accepts RELEASED.

A q derived from configuration 3 is not a published q; configurations 4 and
6 publish it.

The veto geometry places, for every `ACTIVE` snapshot of a hold-mode run,
the spark of cylinder n against the reset arming of cylinder n + 1. The
spark lies at the primary command after tooth 7, and the reset edge
`120 - dwell` degrees after the command of reset builder `0x0004E080`.
Scheduler `0x0002ACBA` arms it one decade early, on the tooth that
normalizer `0x00028DC8` places across the gap. The margin is the arming
angle less the primary command: a positive margin is on time, zero is
coincident, and a negative margin arms the dwell before the spark. The
facts and their sources are beside the constants of
`rolling_launch_audit.py`.

- A historical endpoint sets a dwell-start veto at the spark of cylinder n,
  which the reset arming of cylinder n + 1 reads, so a requested cut is
  withheld only when the arming follows the spark. Its check takes the
  dwell from group 0 of configurations 1 and 2 and the stock command from
  the final timing; the primary command adds the trim of the map slot up to
  its floor, and the reset builder reads the stock command. The cut
  requests of each class follow the counter, and the requests up to the
  first inactive snapshot follow the last `ACTIVE` one. The check reports
  `veto=PASS` when every covered snapshot is on time and is informational.
- The current runtime decides the veto of a cylinder at its dwell arming,
  before the stock permission check, and consumes q there, so the order
  needs no margin. The geometry of configuration 5, whose group 0 carries
  the dwell and group 1 the engine speed and the stock and effective
  commands, classifies the snapshots where a dwell-start veto comes late:
  the coincident and late snapshots, whose arming does not follow the spark
  of the previous cylinder. The effective command reaches both schedulers.
  Each snapshot pairs with each snapshot of the configuration one tick away
  and takes the smallest margin; a snapshot without a pair is missing.

Each run reports its coverage, the `ACTIVE` snapshots of a veto
configuration against all `ACTIVE` snapshots, the snapshots of each class,
and the smallest margin with its engine speed, dwell, and commands. A
current run also reports the classified snapshots, their share of the
covered snapshots with a pair, and their engine-speed range, and the
regulation of the classified and the other `ACTIVE` snapshots: the range
and mean of the error of the regulated quantity against its target and of
the published q. The error is the published control error where a snapshot
carries it; otherwise it is the `0x180` engine speed less the launch RPM of
the map slot under the RPM regulator, or the `0x280` speed less the selected
target of the run under the speed regulator. Configuration 5 carries no q,
so the q of a classified snapshot reads `n/a`; configurations 4 and 6
publish q for the other class.

The replay steps the controller once per snapshot, so the audit refuses a
capture whose snapshots do not step by one tick, which a tick divisor above 1
produces. A run with an `ACTIVE` snapshot that carries none of the hold
fields of the endpoint is a coverage gap: the ECU installs configuration 0
at every start, so a run before the host selects a hold configuration
again carries none of them. The audit prints the count of such snapshots
and their configuration IDs, checks nothing in the run, and continues with
the other runs and captures. A law failure, a requested-cut count outside
its bounds, a run without a checked snapshot, which includes such a run, or
a capture without an `ACTIVE` run makes the exit status 1; the cut-request
bounds of configuration 4 are the verdict of
the actuation. The classification and the regulation of the current runtime
are reports without thresholds: a missing pair or a capture without an
`ACTIVE` snapshot of configuration 5 is a coverage gap, which the audit
prints. The veto check of a historical endpoint is informational.

`--thresholds` adds the acceptance report of a hold session. Every window
and threshold value comes from that local TOML file, which the session
confirms before the image; the audit holds no default. Every key except
`rpm_spread_rpm` is mandatory, and unknown keys are refused. The values
below show the format and are not recommended settings:

```toml
schema_version = 1

[window]
steady_after_s = 1.0
min_steady_s = 1.0
band_hz = [3.0, 7.0]
band_min_s = 2.0

[rpm]
p5_below_soft_rpm = 100
p5_below_hard_rpm = 200
p95_above_rpm = 200
peak_above_rpm = 500

[speed]
mean_error_kmh = 0.5
speed_spread_kmh = 1.0
rpm_spread_rpm = 200

[series]
repeats = 3
```

The steady window of a run starts `steady_after_s` after its first `ACTIVE`
snapshot. A window shorter than `min_steady_s` reads `n/a`: the run checks
entry and exit but no steady dynamics. Over the window the audit reports the
5th and 95th percentiles and their width of the engine speed, the share of
snapshots whose trim the floor command clips, and the RMS of the `band_hz`
component of the engine speed and the vehicle speed. The percentiles are
the first and last cut of `statistics.quantiles(n=20, method="inclusive")`,
which interpolates linearly between order statistics. Runs split at a
missing tick, so a window is tick-contiguous; the band uses the longest
segment with a value, and a segment shorter than `band_min_s` reads `n/a`.
The transform removes a least-squares line from the segment and applies a
Hann window, normalized by its energy, so a sine well inside the band reads
its RMS.

- The RPM regulator: the peak and the mean of the engine speed less the
  launch RPM `Nt` of the map slot. The run passes when P5 >= `Nt - W -
  p5_below_soft_rpm` with the soft width `W` of the slot, P95 <= `Nt +
  p95_above_rpm`, and the peak <= `Nt + peak_above_rpm`. A slot with
  `W = 0` is a hard two-step whose cut saws the engine speed below `Nt`,
  so its P5 bound is `Nt - p5_below_hard_rpm`.
- The speed regulator: the percentiles of the speed and of the speed error,
  and the mean speed error. The error is the published control error or
  speed error, otherwise the `0x280` speed less the selected target. The
  run passes when the absolute mean error <= `mean_error_kmh`, the speed
  width <= `speed_spread_kmh`, and the engine-speed width <= `rpm_spread_rpm`.
  A file without `rpm_spread_rpm` reports the engine-speed width and leaves
  it out of the verdict: in a gear the engine speed follows the vehicle
  speed, and its width beyond that is the driveline response to the cut.
  At a speed target of 0, a window at 0 km/h has a speed error and a speed
  width of 0 by construction: the speed checks do not apply, so such a run
  fails on the engine-speed width or reads `n/a`. Without `rpm_spread_rpm`
  it has no judged check: it reads `n/a`, and its series stays
  `INCOMPLETE`. The current runtime holds a standstill with the RPM
  regulator, whose bounds judge it, because every slot has a launch speed
  threshold of at least 0.1 km/h. The target is the
  selected target, or else the median of the targets that the speed and
  the published error of each snapshot imply, which reads 0 within
  0.5 km/h because the two values are sampled at different instants. At
  another target, a logger speed of 0 km/h throughout the window has no
  speed width, so that check reads `n/a`.

A missing value that a check needs makes the verdict `n/a`. A series is
the runs of one map, regulator kind and standstill state of a capture: a
standstill run has a speed target of 0 or reads 0 km/h throughout.
Snapshots carry no gear or pedal context, so these keys approximate the
series of a session plan. A series fails when one judged run fails and
passes when at least `repeats` runs are judged and pass; otherwise it is
incomplete. The acceptance report leaves the exit status unchanged.

The DFT bins of a segment of N snapshots lie 1 / (N * 10.24 ms) apart, about
1 Hz for 1 s, and the Hann window spreads a component over two bins on each
side, so the band edges are soft. With `band_hz = [3.0, 7.0]` a 1 s segment
reads about 41% of the RMS of a 3 Hz sine, 92% at 4 Hz, and still 39% at
8 Hz; a 2 s segment reads 92% at 3.5 Hz, the full RMS from 4 to 6 Hz, and
below 1% at 2.5 and 8 Hz. The audit refuses a `band_min_s` below 2.0.

The same reader joins raw bus evidence to the holds of an MLG recording:

```bash
python3 tools/logs/rolling_launch_audit.py \
  --image tmp/rl-v2/build-103/rl-103.bin \
  --reference-mlg tmp/2026-11-03_22-01-12_vq-can-telemetry-v10.1.1.mlg \
  --bus-json tmp/rl-2-bus-audit.json tmp/rl-2.trc
```

The join matches the 16-bit telemetry tick and verifies the overlapping
snapshot contents. It handles a tick wrap before the MLG begins and reports
holds missing from a truncated TRC. Repeated ticks that make the join
ambiguous, or matching ticks with different contents, refuse the join.

- Release is the first `0x239` transition from CANCEL `0x02` to released
  `0x20` through a hold or within one second after it. Times are milliseconds
  from the TRC header's start, including the offset of a truncated trace.
- The next `0x180` frame gives a frame delay and its equivalent in four-stroke
  engine cycles, `delay_ms * RPM / 120000`. This is a sampling figure, not
  physical torque recovery. The ECU estimate in `0x180` and its parallel
  estimate in `0x160` do not account for the added spark veto. Equality of
  those words through a cut cannot establish full shaft torque. `0x174`
  words A and B are requests from the TCM, not actual torque. The report
  leaves physical recovery unmeasured and reports the release of cut
  requests from the cut-request counter separately.
- Phase is a fixed field of page 2, current in every snapshot. Counter
  increments are modulo 256. The last cut request lies between adjacent
  coherent snapshots; their first-page times are capture proxies, not
  interrupt-event timestamps. An increment in the first non-ACTIVE snapshot
  spans the transition and does not establish a cut request after it. The
  audit checks all subsequent inactive snapshots up to the next hold, rejects
  incomplete coverage as a release proof, and bounds how many cut requests
  straddle or follow the raw release frame.
- The snapshot button attribute is host context from `0x239`, not the stable
  ECU input `0xFFFF2A85`, which these recordings do not carry. A
  `BUTTON_RELEASED` abort bounds acceptance of the stable release between
  the last ACTIVE and first non-ACTIVE snapshots: the runtime consumes the
  debounced input after the stock ASCD task and aborts in that pass.
  `PEDAL_LOW` and `RPM_LOW` aborts precede acceptance, since an accepted
  released code overrides those gate reasons with `BUTTON_RELEASED`.
  The audit keeps these inferred input bounds separate from observations
  and compares the release of cut requests with both the raw CAN code and
  the inferred stable input.
- The `0x176` output/turbine ratio is reported over each hold and compared
  with stable-gear medians using the field decoder and selection of
  `tcm_shift_audit.py`. Neutral ratios do not identify a driving gear.
- Speed frames `0x284` and `0x280` use big-endian bytes 4 and 5. The selected
  JK08A receiver maps `0xFFFF` to zero and divides by ten into 0.1 km/h
  counts. Subtracting the published speed error must admit one constant
  target throughout a hold. The last two preceding frames, at most 40 ms
  old, bracket the asynchronous sampling. This tests source compatibility
  without fitting a target. It does not supply a direct speed-word
  measurement outside the hold. The report also compares the two bus
  speeds inside and outside holds and measures the frame periods.

## JK08A engine-torque scale audit

`torque_scale_audit.py` bounds the physical scale of the JK08A raw torque
domain with full-pedal road runs in dashboard MLVLG recordings or strict
schema-2 `tuning` TRC captures.

```bash
python3 tools/logs/torque_scale_audit.py \
  --calibration-image tmp/1JK08A-tune-v3-1.bin \
  --cruise tmp/logs-09-22/7-cruise.mlg \
  --remainder tmp/logs-09-22/5-shifts-map-3.trc \
  --remainder tmp/logs-09-22/5-downshifts-map-3.trc \
  --remainder tmp/logs-09-22/11-map-2-rl.trc \
  tmp/logs-09-22/ex-torque-2nd-gear.mlg \
  tmp/logs-09-22/5-downshifts-map-3.trc \
  tmp/logs-09-22/xxx-0-100-map-*.mlg \
  tmp/logs-09-22/xxx-3rd-gear-map-*.mlg
```

- The cruise capture gives the stock RPM per CAN km/h of the
  converter-locked fifth gear, the median over one-second windows at 60 km/h
  or more whose samples stay within 0.5 percent of the window median. The
  RE5R05A ratios of the 2007 G35 service manual scale it to the other gears.
- Base term `0xFFFF2408` is replayed from the calibration image: table
  `0x154A0` over RPM axis `0x14ABA` with a Q0.16 fraction, minus
  `floor(bfs_raw * ROM16[0x92AC] / ROM16[0x9534])`, saturated at zero. The
  TRC captures give the remainder between `engine_torque_state_raw` minus the
  base term and the `0x180` actual-torque word, read at the midpoint of its
  five-count interval, over samples with APP1 of 600 raw or more, a timing
  command of 20 or more, and no fuel inhibit.
- A segment is an interval of APP1 at 900 raw or more that lasts at least
  1.5 s inside a running stream; a stream pause ends it, as it ends a neutral
  coast. Points lie 0.1 s apart and use line fits over 0.2 s on each side. A
  point needs a turbine-to-engine speed ratio of 0.90..1.00 in one gear, the
  gear of the manual selector position when one is engaged, a timing command
  of 15 or more, no fuel inhibit, and 2500 RPM or more. A fall of engine speed
  faster than 1500 RPM/s marks a shift, which removes the points from 0.5 s
  before to 0.7 s after it.
- The flywheel torque of a point is the road force of vehicle and rotating
  mass, rolling and aerodynamic load, and grade, divided by the turbine
  radians per metre and the driveline efficiency, plus the engine and turbine
  inertia terms. The converter torque ratio is 1 inside the coupling range.
  The vehicle constants are assumptions with a nominal value and a box range;
  the audit reports each figure at the nominal constants and over all 256
  corners of the box.
- Each candidate scale receives the road grade that the force balance
  requires. Two adjacent gears of one run share a short stretch of road, so
  the scale at which their mean implied grades agree does not depend on the
  grade. Neutral coasts give the grade that the nominal road load implies.

The output is one `key = value` line per figure in TOML syntax. The captures
do not measure road grade, vehicle mass, tire radius, or true vehicle speed,
so the audit bounds the scale and does not determine it.

### CONSULT steady points

`--consult-points` compares steady readings of the CONSULT-III TCM data
monitor with the `0x180` words of TRC captures. It runs alone or after the
road-run figures.

```bash
python3 tools/logs/torque_scale_audit.py --consult-points tmp/logs/consult-points.toml
```

```toml
tolerance_s = 15                 # search radius around each point, default 15
min_seconds = 2                  # optional thresholds of a steady interval,
word_spread = 2                  # shown with their defaults
rpm_spread = 100
app1_spread = 20

[[point]]
capture = "block5.trc"           # relative to the directory of this file
time = "14:32:10"                # local time of the reading, or offset_s
engine_torque_nm = 182           # ENGINE TORQUE
eng_torque_d_nm = 190            # optional ENG TORQUE D
engine_speed_rpm = 2400          # optional, selects the steady interval
gear = 4                         # optional
note = "M4, 80 km/h"             # optional
```

- `time` is the wall-clock time of the computer that recorded the TRC: the
  dashboard and PCAN-View store a local `$STARTTIME`, and the point lies on
  the day of the capture start. `offset_s` gives the TRC offset instead.
- A steady interval lasts `min_seconds` or more, holds a valid `0x180`
  actual word within `word_spread` words, engine speed within `rpm_spread`
  RPM, and APP1 within `app1_spread` raw, has no fuel inhibit, and does not
  span a stream pause. With `engine_speed_rpm`, every sample lies within
  100 RPM of it. The point takes the steady interval nearest to its time
  inside the search radius, the longer one on a tie; a point without one is
  reported and left out of the fits. The output repeats the radius and the
  thresholds.
- A point without a steady interval reports a candidate: among the windows
  of `min_seconds` inside the search radius, regardless of
  `engine_speed_rpm`, the one whose largest ratio of a spread to its
  threshold is smallest, the nearest to the point among equals. The
  `consult_candidate_*` lists follow the point order with its start, length,
  spreads, median word, and engine speed, and `-1` for a point that has a
  steady interval or no window. Spreads within the thresholds trace the
  rejection to the engine speed or the time of the point.
- The raw count of a word is the midpoint of its five-count interval. The
  fit gives `ENGINE TORQUE = slope * raw + intercept`, the slope through the
  origin, the largest residual, and the largest deviation of each candidate
  scale. `ENG TORQUE D` is fitted against the `0x180` request word when three
  or more points carry it. `-1` marks a request word that the interval does
  not carry.

Whether the RE5R05A TCM of the vehicle offers ENGINE TORQUE is not
established; the readings establish only the scale of the value that the TCM
displays.

## JK08A transmission interface audit

`tcm_shift_audit.py` replays strict schema-2 `tuning` TRC captures against the
TCM frames `0x174`, `0x176`, and `0x177` and the ECU frames `0x180` and
`0x160`. `--rom` names the image that ran during the captures; the default is
the stock JK08A ROM.

```bash
python3 tools/logs/tcm_shift_audit.py \
  --rom tmp/1JK08A-tune-v3-1.bin \
  tmp/logs-09-22/5-shifts-map-3.trc \
  tmp/logs-09-22/5-downshifts-map-3.trc
```

- The ROM check compares the exact instruction bytes of the path from the TCM
  frames to shared request `0xFFFF19C6` in `FUN_000C47EA`, `FUN_0007724C`,
  `FUN_00020DFE`, `FUN_0002040C`, `FUN_00077892`, `FUN_000777FA`,
  `FUN_00079030`, `FUN_000C4ACE`, and `FUN_0006425A`, and derives the `code_`
  addresses, tables, and option bytes from the literals of those
  instructions. `code_matches_stock` compares them with the stock ROM.
  `scalar_source` is the literal from which `FUN_00077892` reads the
  throttle-limit scalar of its gear-indexed target, so a map-switching image
  that redirects it still matches the stock path.
- A TCM group is a `0x174` frame followed by one `0x176` and one `0x177`
  frame within 2 ms; an incomplete or late group stops the audit. A telemetry
  snapshot pairs with the last `0x180` and `0x160` frames between the first
  pages of the next two snapshots, and only snapshots of consecutive ticks
  form a pass.
- A status episode is a run of value-3 frames of the `0x174` byte 4 status
  field whose frames lie at most 0.1 s apart. Word B has settled when 10
  consecutive frames carry its default, the most frequent word B of the
  capture. An episode window runs from 0.03 s before the first value-3 frame
  to 0.05 s after word B settles, and an episode outside a completed shift
  event stops the audit.
- A floor pass lies in an episode window, and its `0xFFFF19C6` equals the
  floor-table entry of the shift code of the episode and differs from the
  `0x180` request.
- A burst is a run of nonzero `0x177` byte 4 frames that ends at the first
  gap of more than 1 zero frame. Its window runs from 0.03 s before its first
  to 0.5 s after its last nonzero frame. A pass diverges when the `0x180`
  actual-torque word differs from the `0x160` parallel word. The pedal and
  timing references of a burst come from the 0.3 s before it. An upshift
  without a burst is checked for divergence from the target change to 0.3 s
  after its shift window closes.
- Word B binds a pass when the last 4 TCM groups at most 0.03 s before it
  carry a word B other than the default and every such word unpacks below the
  unpacked `0x180` request. Passes in which the `0x180` request differs from
  the packed `0xFFFF19C6` form one run while they lie at most 0.03 s apart.
- The gear signal uses stable-gear groups in D, DS, or M1..M5 whose target
  and current gear agree in gears 1..5 and whose `0x177` byte 5 holds `0x78`.
  The gear phase must equal the current gear minus one. A speed ratio matches
  a gear when output over turbine speed lies within 2 percent of the inverse
  RE5R05A ratio of that gear, counted with turbine speed 800 or more and output
  speed 300 or more raw. Each manual `0x421` frame compares its position with
  the target gear of the latest TCM group.
- A downshift counts as closed-pedal when APP1 stays at 160 raw or less from
  its target change to the end of its shift window.
- The pedal class of a downshift in D or DS follows APP1 at its target change:
  closed at 160 raw or less, full at 900 raw or more, the full-pedal threshold
  of `torque_scale_audit.py`, and pressed in between. A downshift in M1..M5
  is manual. The TCM sends no kickdown flag, so the full class is defined by
  the pedal alone.
- Profiles 8 and later stream reduction state `0xFFFF1866` on a fixed page
  and transition state `0xFFFF23C2` on the dynamic page in the default
  configuration only. A snapshot without a field leaves it unobserved; an
  unobserved snapshot ends a run.
- `0xFFFF1866` is direct when it equals `0x177` byte 4 shifted left by 8 for
  one of the TCM groups at most 0.03 s before the first page of the snapshot.
  Where those groups differ, the index of the newest matching group, from 0
  for the newest, gives the lag. A zero state while every group carries a
  nonzero byte 4 is cleared, and any other nonzero state is other. Runs of
  other states report their peak, a nonzero low byte, monotonic decrease,
  and the burst, shift event, selector, and gear at their start.
- A run of nonzero `0xFFFF23C2` follows the latest burst, else the latest
  nonzero `0xFFFF1866` run, that starts by the run start and ends at most
  0.03 s, the binding window, before it. `preceding` names that run;
  `onset_lag_s` is measured from its start and `preceding_gap_s` from its
  end, and `none` with `-1` marks a run that follows neither. The relation
  is temporal, not causal: `0xFFFF23C2` also depends on `0xFFFF186E`,
  `0xFFFF186C`, and the difference of `0xFFFF23F1` and `0xFFFF2404`, which no
  stream carries, so runs that follow neither are expected. The final-timing
  reference is the median of the 0.3 s before the run. Each burst window is
  covered fully, partly, or not at all by snapshots that carry the field.
- `--events PATH` writes one CSV row per shift event to a new file. The event
  window runs from 0.03 s before the target change to 0.5 s after its shift
  window closes; APP1 maximum covers the shift window only. `pedal_word_start`
  is the pedal word that the TCM receives in `0x180`, byte 5 and bits 7..6
  of byte 6, in the pass at the target change, and `pedal_word_max` its
  maximum over the shift window. A blank cell marks a quantity that the
  window does not observe.

The analysis of a drive needs a TRC: the TCM and `0x160`/`0x180` frames are
not part of an MLG recording. The dashboard writes it beside the MLG while it
records, and the dynamic page stays in the default configuration so that
`0xFFFF23C2` is streamed.

The output is one `key = value` line per figure in TOML syntax. Every figure
is a raw CAN or software quantity; the TCM-side meaning of the status field
and of words A and B is outside the captures.

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

The decoder and `trc_to_mlg.py` verify only the current profile, so a capture
of an earlier profile requires a repository revision whose generated schema
matches its recorded profile CRC. `mlg_relayout.py` carries a dashboard
recording of an earlier profile into the current channel layout.

## MLG record retiming

`mlg_retime.py` rebuilds record times from the `Telemetry tick` channel. The
producer emits one telemetry group per tick at a fixed period, so the tick is
the sample index of a running stream: a host clock that stamps a frame when the
application dequeues it collapses a drained burst onto one 10 us block
timestamp, and the tick index restores the true spacing. STOP holds the tick,
so a stream pause keeps its recorded duration; the stream-pause rule of the
telemetry decoder above tells it from a drained host stall.

```bash
python3 tools/logs/mlg_retime.py --dry-run tmp/drive.mlg
python3 tools/logs/mlg_retime.py tmp/drive.mlg --output tmp/drive-retimed.mlg
```

The tool writes a new file and never edits the source. Block timestamps and the
`Date` and `Elapsed` channels follow the tick index and the stream pauses; every
other recorded value is copied unchanged. The tick period is measured over the
running snapshots unless `--period-ms` provides it. The pause floors depend on
the period, so the measurement starts from the nominal tick of the dashboard
model and repeats with the measured period until it settles. The first record
keeps its recorded offset from the start of the recording, so the
reconstructed span matches the recorded one.
A log whose records repeat a tick, such as one holding bridge records, is
refused: the tick index cannot order them. A log that spans a producer restart
is refused for the same reason: the tick index restarts with the controller and
the real gap across the restart is not recorded in it.

## MLG channel relayout

`mlg_relayout.py` carries a dashboard MLG recording into the channel layout
that the recorder writes for the current profile. A recorded channel whose
name, without the candidate marker, names a current channel keeps every
recorded value. A current channel the recording lacks reads `NaN` in every
record, as the recorder writes a field it has not received, and a recorded
channel the current profile does not bind is left out; the tool lists both
sets.

```bash
python3 tools/logs/mlg_relayout.py tmp/drive.mlg --output-dir tmp/current
```

Blocks keep their order, counters, and timestamps, markers keep their text,
and the header keeps the start time, so the time base and the bridge records
of the recording stay unchanged. The tool writes a new file and never replaces
its source or, without `--force`, an existing output. A recording without the
`Date`, `Elapsed`, or `Telemetry tick` channel is not a dashboard recording
and is refused.

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
uv run pytest -q tools/logs/tests
```
