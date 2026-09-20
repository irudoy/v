# VQ CAN telemetry dashboard

Current dashboard version: `6.0.0`.

This Tkinter application displays and records VQ custom CAN telemetry from a
PEAK PCAN-USB adapter on Windows or macOS. The host application is ROM-agnostic:
it loads the selected wire-schema JSON and never imports a firmware manifest,
checks a ROM identity, or uses producer RAM addresses. The bundled schema
provides the incompatible schema-2 `tuning` profile with these defaults:

- PCAN channel `PCAN_USBBUS1`;
- classical CAN at `500000 bit/s`;
- standard ID `0x6F0`;
- `tuning`, divisor 1;
- listen-only PCAN state.

The fixed dashboard presentation targets the semantic field names in the
`tuning` profile. Any ROM-specific producer may implement that wire contract;
producer hooks, RAM addresses, and mailbox ownership stay outside the host
schema. `--schema` selects another compatible schema file. Listen-only mode
suppresses CAN transmission and ACK participation. In active/ACK mode the only
application frames sent by the dashboard are schema-declared START and STOP
commands initiated by the stream button.

The version has one source in `tools/can_dashboard/__init__.py`. It is visible
in the window title, main heading, Windows portable-package directory,
`VERSION.txt`, and macOS `Info.plist`. Semantic-version major changes denote an
incompatible UI, CLI, or MLG contract; minor changes add compatible
functionality; patch changes preserve both contracts.

The Windows driver package installs the PCAN-Basic DLL in the system directory.
The dashboard accesses it through `python-can` 4.6.1. PEAK documents the
PCAN-Basic DLL as the supported interface between an application and the device
driver, and `python-can` documents `PCAN_USBBUS1`, passive state, and
`500000 bit/s` for this adapter. The portable package also installs `tzdata`
2026.3 so IANA timezones used by the TRC converter are available on Windows.

On macOS, `python-can` uses the third-party MacCAN `libPCBUSB` user-space
driver. Version 0.13 supports PCAN-USB on Intel and Apple silicon. The dashboard
follows the proven Cansult connection sequence and releases the PCAN-Basic
channel before opening it and after shutdown. This reset is enabled by default
on macOS and can be disabled with `--no-reset-channel` when another process
intentionally owns the channel. Close other PCAN clients before normal use.
The native application embeds Python, Tk, `python-can`, and its data files;
MacCAN remains a system driver and is not copied into the application.

Each source run has a generation identifier. Reconnect, replay replacement,
and source stop invalidate queued events from the retired worker before a new
model is created. Terminal source status is retained even when the frame queue
is full, and PCAN receive or shutdown failures remain visible as errors rather
than being replaced by a normal stopped state.

## Portable Windows package

Build the ignored transfer archive from the repository root:

```bash
python3 tools/can_dashboard/package_windows.py \
  --output tmp/vq-can-telemetry-v6.0.0-windows.zip
```

On the Windows laptop:

1. Install the current PEAK PCAN-USB driver and verify the adapter with
   PCAN-View at `500 kbit/s`.
2. Install 64-bit Python 3.11 from python.org with the `py` launcher.
3. Extract the complete ZIP to a writable directory.
4. Run `install.cmd` once. It creates `.venv` and installs `python-can`.
5. Run `run-demo.cmd` to verify the UI without CAN hardware.
6. Run `run-dashboard.cmd` for listen-only vehicle capture.
7. Use `run-dashboard-active.cmd` when START/STOP control is required or when
   an isolated ECU needs this adapter to provide CAN ACK.

The package also includes `convert-trc-to-mlg.cmd`. Pass one or more PEAK TRC
1.1 paths to it after `install.cmd`; each result is written beside its source.

The default hardware filter accepts custom telemetry plus stock context IDs
`0x180`, `0x239`, `0x280`, `0x421`, and `0x551`. They provide an independent
RPM cross-check, vehicle speed, ASCD input, selector state, and dashboard
indication state.

## Stream control

The bundled schema reserves `data_can_id + 1` for control, so the selectable
data ID range is `0x001..0x7FE`. With the default data ID `0x6F0`, the control
ID is `0x6F1`. The exact frames are:

| Command | Payload |
| --- | --- |
| START | `54 45 4C 32 02 01 B6 32` |
| STOP | `54 45 4C 32 02 00 A6 13` |

Both frames are standard 11-bit classical CAN with DLC 8. The last two bytes
are CRC-16/CCITT-FALSE over the first six. START forces streaming on until ECU
reset even when the firmware definition flag disables startup streaming. STOP
forces it off until reset. A running 11-frame group is allowed to finish before
STOP becomes silent.

A single stream button sends them. It offers START, switches to STOP once the
driver confirms the START transmission, and returns to START when the source is
stopped or replaced.

The button requires an active/ACK PCAN connection. The dashboard rejects the
command in listen-only, demo, and replay modes. `sent` means the PCAN driver
accepted the transmit request; the protocol has no response frame, so reception
of new telemetry after START is the end-to-end confirmation.

## Native macOS application

Build the ignored arm64 application and transfer archive from the repository
root:

```bash
make dashboard-package-macos
```

The target writes:

- `tmp/VQ CAN Telemetry.app` for direct local use;
- `tmp/vq-can-telemetry-v6.0.0-macos-arm64.zip` for transfer.

The build uses pinned PyInstaller 6.21.0 in `onedir`, `windowed` mode. It embeds
the tested Python/Tk runtime and all Python dependencies, preserves bundle
symlinks in the ZIP, records version 6.0.0 in `Info.plist`, and applies an
ad-hoc signature. The build gate verifies the arm64 architecture, deep code
signature, complete bundle metadata, and a hidden deterministic UI/demo run.
The same gate loads the frozen `python-can` PCAN backend and the installed
MacCAN library without changing a channel's state. It extracts the completed
ZIP and revalidates the archived application before accepting the package.

On the target Mac, install MacCAN `libPCBUSB` 0.13, extract the ZIP, and open
`VQ CAN Telemetry.app`. No Python installation or shell launcher is needed.
The main source starts in listen-only mode; clear the visible `Listen-only`
control when stream control or ACK participation is required. A downloaded
ad-hoc-signed build is not notarized, so the first launch may require Finder's
Open action after the archive source and SHA-256 are verified.

The `0x551` display uses neutral labels `ASCD STATE 6` and `ASCD STATE 7`.
Exact-target observation shows that custom state 6 illuminates SET together
with CRUISE, so it is not labeled CRUISE-only. The correct CRUISE-only state
remains pending a passive stock-state correlation.

Schema 2 names `0xFFFF2326` as `intake_cvtc_target_raw` and `0xFFFF2327` as
`exhaust_cvtc_target_raw`, matching their recovered common-target roles.
Actual intake and exhaust positions for both banks are present in the current
profile. The displayed `(raw-128)*0.5 degCA` conversion is code-proven for
both cam families: the exhaust monitor and the intake cam-coordinate consumer
compare target and actual positions in raw units with the cam edge phases that
the capture handlers count in 0.5 crank degrees.

## Direct repository run

Install the Windows dependency and start the module from the repository root:

```text
py -3.11 -m pip install -r tools\can_dashboard\requirements-windows.txt
py -3.11 -m tools.can_dashboard.app
```

Useful modes:

```text
py -3.11 -m tools.can_dashboard.app --demo
py -3.11 -m tools.can_dashboard.app --replay capture.log
py -3.11 -m tools.can_dashboard.app --active
py -3.11 -m tools.can_dashboard.app --channel PCAN_USBBUS2
py -3.11 -m tools.can_dashboard.app --record drive.mlg
```

On macOS with `libPCBUSB` already installed, the equivalent repository run is:

```bash
uv run --with-requirements tools/can_dashboard/requirements-macos.txt \
  python -m tools.can_dashboard.app \
  --channel PCAN_USBBUS1 --bitrate 500000 \
  --can-id 0x6F0 --profile tuning --tick-divisor 1 \
  --schema patches/can-telemetry-schema.json
```

The macOS default includes the channel reset. Pass `--no-reset-channel` only
when preserving another client's PCAN-Basic ownership is intentional.

Replay accepts PEAK PCAN-View TRC 1.1 files directly, including the `.trc`
captures used by the project. It also accepts compact candump lines such as
`(12.500000) can0 6F0#A001020304050607`.

## MLG recording

`Record MLG` selects a destination and starts an atomic MLVLG v2 recording.
Only complete strict telemetry snapshots produce records. `Stop MLG`, source
stop, source replacement, and window close finalize and validate the file.
No new output is left when no complete snapshot was received; an existing file
selected for replacement remains unchanged in that case. Existing files require
an explicit replacement confirmation in the UI and are rejected by `--record`.

Frames already queued when recording starts update the display but are not
written to the new file. The first MLG event therefore cannot predate the
recording start or be collapsed onto elapsed time zero.

A record carries the time its frame reached the interface, which the block
timestamp resolves to 10 us. The PCAN clock is used whenever the driver reports
one, and the host receive clock otherwise; elapsed time starts at the offset of
the first recorded frame from the recording start. The host dequeue time alone
collapses a burst drained from the driver queue onto a single tick and makes
distinct snapshots share one timestamp. An interface clock that steps
backwards, or ahead of the host clock by more than one second, is abandoned
without breaking elapsed time.

The `tuning` MLG schema has 87 channels: time, schema state, every fixed and
rotating custom-telemetry field, a decoded high-detonation-surface selector,
stock CAN RPM, vehicle speed, selector code, ASCD input, and dashboard state.
Decoded telemetry and context values use F32, so a rotating context that has
not arrived yet can be represented as `NaN` rather than a fabricated zero.

Channel names carry no candidate marker; the marker stays in the units, as it
does on the display. MegaLogViewer lists a channel whose name contains `*` but
draws nothing when it is selected, observed in MegaLogViewer MS Lite 4.6.09, so
a channel name holds identity only. MegaLogViewer evaluates a channel as
`(raw + transform) * scale`, so descriptor transforms are expressed in raw
counts. Both numbers are derived from the calibrations the dashboard applies to
the same field, and the recorder tests bind every channel value to the live
engineering value. `tools/logs/mlg_restamp.py` applies a corrected field table
to files recorded earlier without rewriting their data.

MLG has a wrapping 16-bit 10-us block timestamp. A hold-last bridge record is
inserted when complete snapshots are more than 0.3 seconds apart, which keeps
the wrap sequence unambiguous to the local UltraLog parser. Normal divisor-1
traffic needs no bridge records.

No geographic-coordinate signal is verified on the captured primary CAN
network. The display keeps latitude and longitude slots that read `--`, and the
recording declares no GPS channels rather than storing channels that hold only
`NaN`. A real route requires a separately captured and decoded AV/navigation
network or another GPS source. The logger never invents coordinates from
vehicle speed.

## Window layout

The window opens inside the current screen and remains usable down to
`560x460`. Header controls, status fields, and health counters flow into
additional rows instead of leaving the window, hero cards and detail panels
regrid into as many equal columns as the width allows, and the card and panel
area scrolls vertically when the remaining height is short.

`Connect`/`Disconnect` is one button that follows whether a source worker runs;
`Demo` and `Replay` replace the running source directly. `Record MLG`/`Stop MLG`
follows the recording state.

The card and panel area answers both a mouse wheel and a trackpad gesture
anywhere over its content. Tk reports trackpad scrolling as its own event, so
each input is bound separately, and the scrollbar keeps its stock bindings.

Every status value carries a title, shortens to the available width with a
trailing ellipsis, and reports its title and full text on hover. A click copies
the untruncated text to the clipboard. Detail-panel values behave the same way,
so a long value cannot widen its column. The health counters below the panels
are separate fields: producer tick, completed groups, schema mismatches, CAN
error frames, producer snapshot overruns, producer transmit aborts, and
telemetry status flags.

Status and health fields reserve the width of their widest expected value, so
live values change in place instead of shifting the fields beside them. A value
longer than its reserve is elided, and hover and click still report it in full.

## Display semantics

The decoder retains the latest values from the paired page-9 and page-10
contexts for all five tags.
Schema-dependent conversions stay disabled until the in-band health context
matches protocol version, profile ID, and CRC16. The bundled schema declares
profile ID 5 with CRC16 `0xE144`; a producer that reports another profile ID
or CRC keeps raw values only, because its slots carry other quantities. The
CRC covers the wire layout alone, so a restated field name or scale string
leaves it unchanged. Stale context values remain visible while their update
cadence is one fifth of the snapshot rate.

Context tag 4 carries six knock margin latches, one per knock channel. Each
latch holds the minimum of `threshold - metric` in evaluator units over the
evaluations of its channel since the previous capture of the tag, saturated at
-32768 for an exceedance. A negative value is an evaluation that the stock
comparison counts as a knock event. The idle value 32767 reports that the
channel had no evaluation in that interval or a margin that the signed word
cannot hold. With one evaluation of a channel per engine cycle and the base
snapshot rate, every interval holds an evaluation only above about 2350 rpm.
Stock threshold rows 3 and 5 hold `0xFFFF`, so those two channels report the
idle value on stock calibration. The model keeps the last evaluated margin of
a channel while its latch reports the idle value, and a channel without any
evaluation yet stays `NaN` in a recording. The channel-to-cylinder assignment
is not established, so the fields are named by channel.

A field marked with `*` uses a candidate transform; engine torque state at
`raw * 0.1 Nm` is the only one. The current conversions are:

| Display | Source | Conversion | Evidence boundary |
| --- | --- | --- | --- |
| vehicle speed | `0x280` bytes 4..5 | big-endian `raw / 100 km/h` | target field and zero state confirmed; the firmware divides the word by 10, filters it, divides by 20, and publishes twice that byte as J1979 PID 0x0D km/h |
| APP 1/2 | telemetry words | `raw / 200 V` | ten-bit ADC counts; range monitors accept 60..964 and 60..1000 counts, which is 0.30..4.82 V and 0.30..5.00 V against factory bands of 0.5..1.0 V released and 4.2..4.8 V depressed; a 5.0 V full-scale reading would fault sensors inside those bands |
| TPS bank 1/2 | telemetry words | `raw / 200 V` | ten-bit ADC counts; range monitors accept 60..964 counts, which is 0.30..4.82 V against factory terminal criteria of more than 0.36 V released and less than 4.75 V depressed |
| MAF bank 1/2 | `0xFFFF101C`, `0xFFFF101E` | `raw / 200 V` | ten-bit ADC counts with a unit-nominal Q1.15 trim; the calibration sequence centres on 900 counts, which is 4.50 V, and recordings read 0.425 V with the engine stopped against an expected 0.4 V |
| injection pulse 1..6 | `0xFFFF23C8..0xFFFF23D3` | `raw / 100 ms` | one count is 10 us: the ATU-II channel-8 down-counters run at `Pphi / 64` and the scheduler adds `800 * raw / 256` steps; a compensated software command, not a measured injector-open duration |
| Base Fuel Schedule | `0xFFFF1026` | `raw / 2048 ms` | the fixed normalizers between the schedule and the 10 us pulse word multiply to `(1/8) * (100/256) = 100/2048`; the pulse additionally carries the common gain of 0.75..0.85, both trims, and the injector opening time, and a replay of that chain reproduces the recorded pulse with a median ratio of 1.000 |
| fuel/oil temperature | `0xFFFF1074`, `0xFFFF2876` | `raw - 50 degC` | outputs of thermistor table `0x12DEA` and of the byte-identical oil curve `0x12C6E`, whose code J1979 PIDs 0x05 and 0x0F declare as `degC + 50`; the factory sensor tables give 20.5 and 52 degC at their 20 and 50 degC reference voltages |
| battery voltage | `0xFFFF1188` byte | `raw * 0.08 V` | ten-bit sample shifted right by two; the ROM limits 125, 131, 137, and 200 of the DTC monitors are the factory test conditions of 10, 10.5, 11, and 16 V; established from ROM constants and factory specifications, not from firmware arithmetic |
| short/long fuel trim | telemetry Q8.8 words | `raw / 256 - 100 percent` | exact neutral representation and target diagnostic agreement |
| timing coordinate | `final_timing_raw` signed byte | `raw degBTDC` | J1979 PID 0x0E publishes `110 - apc_command` as degrees before TDC, which is this coordinate on the normal path; upstream stock coordinate during a Rolling Launch late override, not a measured spark angle |
| total airflow | `0xFFFF3852` word | `raw / 100 g/s` | J1979 PID 0x10 publishes the same `105 * 0xFFFF105C / 256` product as g/s*100; the ECU's airflow model, not a hardware measurement |
| coolant and intake air | `0xFFFF1079`, `0xFFFF2837` | `raw - 50 degC` | J1979 PIDs 0x05 and 0x0F publish the same `0x12DEA` transfer codes minus 10 as `A - 40` degC |
| absolute throttle | `0xFFFF1075` byte | `raw * 100 / 255 percent` | J1979 PID 0x11 returns the byte as `A * 100 / 255` percent |
| APC command | `apc_command_raw` byte | raw | effective software command consumed by the APC scheduler; normal-path timing coordinate is `110 - raw` |
| knock timing state | `0xFFFF121A` signed word | `raw / 256 state` | exact Q8 software state; its physical unit remains unresolved |
| knock margin ch 1..6 | telemetry latches `0xFFFF5E10..0xFFFF5E1B` | raw signed evaluator units | the wrapper behind the only literal of the knock slice evaluator repeats the stock `threshold + 0x80000000 < metric` comparison on the values the evaluator leaves in RAM; the unit of the metric is the summed and gain-scaled sensor difference and has no physical conversion |
| active hot surface | `0xFFFF2466.bit6` | clear = High Octane, set = High Detonation | exact selector; other bits in the byte have separate roles |
| exhaust CVTC target and actual B1/B2 | `0xFFFF2327`, `0xFFFF2324..2325` | `(raw - 128) * 0.5 degCA` | code-proven edge-phase count; recordings keep the actual bytes within two counts of a steady target in 98 percent of Map 3 samples |
| intake CVTC target and actual B1/B2 | `0xFFFF2326`, `0xFFFF2442..2443` | `(raw - 128) * 0.5 degCA` | code-proven edge-phase count, advance positive; recordings keep the actual bytes within two counts of a steady target in 95 to 100 percent of samples |
| intake CVTC duty monitor and command B1/B2 | `0xFFFF2440..2441`, `0xFFFF23B4..23B5` | `raw * 39 / 100 percent` | code-proven ATU-II conversion of the command; both pairs share context tag 1 and come from one capture pass; profile 3 recordings, which sampled the pairs one pass apart, keep the monitor within three counts of the command in 80 percent of active records with a mean difference below 0.2 count |
| exhaust CVTC duty B1/B2 words | `0xFFFF1AAC`, `0xFFFF1AAE` | `raw * 100 / 1024 percent` | code-proven output-stage conversion |
| end of injection after intake TDC | `0xFFFF192E` word | `raw * 2 - 590 degATDC` | the word holds `2 * min(y, 209)` and `raw * 2` is the code-proven delay in crank degrees after the reference tooth; the intake-TDC anchor rests on the reference-tooth and cylinder-order analysis and is a firmware coordinate, not a measured injector event; JK00C, JK00D, JK78C, 1ND, and 1ME3B stream their homologous word with the same anchor |

The MLG descriptor applies the exact Q8 scale to `Knock timing state` and keeps
the original `Knock surface state` bitfield. The additional
`High-detonation surface selected` channel exposes bit 6 as an ON/OFF field for
plotting and filtering without discarding the raw byte.

The CarScanner comparison follows the CAN recording rather than sharing a
clock with it. It corroborates transforms but cannot prove equality for values
that can change between captures. Injection values are compensated software
commands rather than verified electrical injector-open durations, and timing is
a software command, not a measured spark angle. The current top-card label `Timing command` names
`final_timing_raw`; during a Rolling Launch late override it is the upstream
stock coordinate rather than the effective command. The detailed `APC command`
field carries the effective command.

Health indicators include complete snapshot and frame rates, tick-derived
loss, incomplete and malformed groups, schema mismatches, source queue drops,
telemetry status flags, and the rotating overrun and abort counters.

Convert an existing PEAK trace without replay timing:

```bash
python3 tools/logs/trc_to_mlg.py schema2-capture.trc
```

The converter and live recorder use the same selected wire schema, MLVLG
schema, and validator. The converter accepts the same `--schema` option.

## Hardware evidence boundary

The 2026-08-17 schema-1 `wide54`, divisor-1 capture contains 35,811 complete snapshots
at 97.599 Hz. After synchronization to the first page 0, it has zero malformed
or incomplete groups, tick gaps, schema mismatches, nonzero telemetry status,
snapshot overruns, TX aborts, PCAN warnings, and PCAN errors. Whole-bus average
load is 57.185% to 69.437%, and the maximum rolling 100 ms estimate is 59.006%
to 71.650% at `500 kbit/s`.

Observed selector codes are `08=P`, `10=R`, `18=N`, `20=D`, `28=DS`,
`80=M1`, `88=M2`, `90=M3`, `98=M4`, and `A0=M5`. Codes `98` and `A0` are
operator-confirmed observations outside the saved trace. ASCD byte 3 code
`10` is RESUME/ACCEL and has the same evidence boundary.

That capture establishes the dashboard source path, stock context bindings,
mailbox-26 operation, and the earlier bus-load level. Dashboard 6.0.0 does not
decode schema 1. The eleven-frame schema-2 stream requires its own bounded
target-vehicle capture before normal logging use.
