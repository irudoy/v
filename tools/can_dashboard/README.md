# VQ CAN telemetry dashboard

This Tkinter application displays and records VQ custom CAN telemetry from a
PEAK PCAN-USB adapter on Windows or macOS. The host application is ROM-agnostic:
it loads the selected wire-schema JSON and never imports a firmware manifest,
checks a ROM identity, or uses producer RAM addresses. The bundled schema
provides the incompatible schema-2 `tuning` profile with these defaults:

- PCAN channel `PCAN_USBBUS1`;
- classical CAN at `500000 bit/s`;
- standard ID `0x6F0`;
- `tuning`, divisor 1;
- active/ACK PCAN state.

The fixed dashboard presentation targets the semantic field names in the
`tuning` profile. Any ROM-specific producer may implement that wire contract;
producer hooks, RAM addresses, and mailbox ownership stay outside the host
schema. `--schema` selects another compatible schema file. In active/ACK mode
the adapter acknowledges bus frames, and the only application frames sent by
the dashboard are schema-declared START and STOP commands initiated by the
stream button. The firmware keeps startup streaming disabled by default, so
START is the normal way to begin a capture. Listen-only mode suppresses CAN
transmission and ACK participation. The application connects at start, so
`--listen-only` selects that mode from the first connection; in the window,
disconnect, switch the lit `ACK` button off, and connect again.

The version has one source in `tools/can_dashboard/__init__.py` and is
published, with the pinned dependency versions, in the deployment table of
[`../README.md`](../README.md#local-deployment). It is visible in the window
title, window header, Windows portable-package directory, `VERSION.txt`, and
macOS `Info.plist`. Semantic-version major changes denote an
incompatible UI, CLI, or MLG contract; minor changes add compatible
functionality; patch changes preserve both contracts.

The Windows driver package installs the PCAN-Basic DLL in the system directory.
The dashboard accesses it through `python-can`. PEAK documents the
PCAN-Basic DLL as the supported interface between an application and the device
driver, and `python-can` documents `PCAN_USBBUS1`, passive state, and
`500000 bit/s` for this adapter. The portable package also installs `tzdata`
so IANA timezones used by the TRC converter are available on Windows.

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
make dashboard-package
```

The target writes an ignored `tmp/` archive whose name carries the dashboard
version. `CAN_DASHBOARD_OUTPUT=<path>` selects another path.

On the Windows laptop:

1. Install the current PEAK PCAN-USB driver and verify the adapter with
   PCAN-View at `500 kbit/s`.
2. Install 64-bit Python from python.org with the `py` launcher. `install.cmd`
   names the required version and stops without it.
3. Extract the complete ZIP to a writable directory.
4. Run `install.cmd` once. It creates `.venv` and installs `python-can`.
5. Run `run-dashboard.cmd`. It opens the adapter in active/ACK mode, which
   START/STOP control requires and which gives an isolated ECU its CAN ACK.
   The `DEMO` button runs the UI without CAN hardware.

The package also includes `convert-trc-to-mlg.cmd`. Pass one or more PEAK TRC
1.1 paths to it after `install.cmd`; each result is written beside its source.

The default hardware filter accepts custom telemetry plus stock context IDs
`0x174`, `0x180`, `0x239`, `0x280`, `0x421`, and `0x551`. They provide the
transmission gear, engine speed, vehicle speed, ASCD input, selector state,
and dashboard indication state.

`Engine speed` and `Stock CAN RPM` show frame `0x180`. `FUN_000384FE` shifts
the event-interval engine speed `0xFFFF1196`, RPM * 5.12, right by 4 into
`0xFFFF11EE`, which `FUN_000C577A` multiplies by 25 into frame `0x180` bytes 0
and 1 at `raw / 8` RPM, 3.125 RPM per count, and right by 6 into the
coordinate `0xFFFF11F4` at 12.5 RPM per count that the ECU tables read.
Profile 7 does not stream the coordinate, because the frame carries the word
it is a shift of. A replay of a profile 5 or 6 recording shows the coordinate
as `Engine speed`: it belongs to the snapshot taken at the scheduler boundary,
while the frame is serialized in its own `Tcan` slot and the display holds the
latest frame received, so there the two rows differ by their resolution and
by the change of engine speed between the two sampling moments.

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

A single `STREAM` button sends them. It offers START, lights up and switches to
STOP once the driver confirms the START transmission, and returns to START
when the source is stopped or replaced.

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

The target writes `tmp/VQ CAN Telemetry.app` for direct local use and an
ignored `tmp/` ZIP for transfer whose name carries the dashboard version and
the arm64 architecture. `CAN_DASHBOARD_MACOS_APP_OUTPUT=<path>` and
`CAN_DASHBOARD_MACOS_OUTPUT=<path>` select other paths.

The build uses the PyInstaller pinned in `requirements-macos-build.txt` in
`onedir`, `windowed` mode. It embeds the tested Python/Tk runtime and all
Python dependencies, preserves bundle symlinks in the ZIP, records the
dashboard version in `Info.plist`, and applies an
ad-hoc signature. The build gate verifies the arm64 architecture, deep code
signature, complete bundle metadata, and a hidden deterministic UI/demo run.
The same gate loads the frozen `python-can` PCAN backend and the installed
MacCAN library without changing a channel's state. It extracts the completed
ZIP and revalidates the archived application before accepting the package.

On the target Mac, install MacCAN `libPCBUSB` 0.13, extract the ZIP, and open
`VQ CAN Telemetry.app`. No Python installation or shell launcher is needed.
The main source starts in active/ACK mode. For a listen-only connection,
disconnect, switch the lit `ACK` button off, and connect again, or
start the application with `open -a "VQ CAN Telemetry" --args --listen-only`. A downloaded
ad-hoc-signed build is not notarized, so the first launch may require Finder's
Open action after the archive source and SHA-256 are verified.

The `0x551` display uses neutral labels `ASCD STATE 4` through `ASCD STATE 7`
for byte 5 values `0x42`, `0x52`, `0x62`, and `0x72`, and `STOCK` for `0x02`;
every other value is shown in hexadecimal. The field is the stock ASCD display
state: 4 is CRUISE with steady SET, 5 is CRUISE alone, and 6 is CRUISE with a
blinking SET lamp. The current runtime emits state 4 for map-selection feedback
and Rolling Launch ACTIVE, and state 5 for a failed held Rolling Launch
attempt; firmware through `1.11` emits state 6 for map feedback and the failed
attempt, and state 7 for Rolling Launch ACTIVE.
`../../defs/JK08A.can.md` records the encoding.

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
py -3.11 -m tools.can_dashboard.app --replay drive.mlg --replay-loop
py -3.11 -m tools.can_dashboard.app --listen-only
py -3.11 -m tools.can_dashboard.app --channel PCAN_USBBUS2
py -3.11 -m tools.can_dashboard.app --record drive.mlg
py -3.11 -m tools.can_dashboard.app --settings bench-settings.json
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

[Replay](#replay) describes the accepted files and the transport controls.

## Live value feed

The feed sends the engineering values of the latest complete schema-verified
snapshot to one UDP endpoint. The `FEED` button opens its dialog:

| Control | Meaning |
| --- | --- |
| `PUBLISH` | turns the feed on and off; lit while on |
| `UDP ENDPOINT` | `HOST:PORT` or a port alone, `127.0.0.1:47809` by default |
| `INSTALL PLUGIN` | writes the RomRaider plugin file for the typed endpoint; the caption beside it reports whether the file is installed for this endpoint, out of date, or not installed |

`APPLY` restarts the feed with these values and stores them in the settings
file, so the feed state returns on the next start. `FEED` stays lit while the
feed runs. The feed follows every source, so `DEMO` and `REPLAY` exercise a
receiver without CAN hardware. One datagram is sent per 25 ms source poll
that completed at least one snapshot, so the feed carries the latest snapshot
of each poll and not every snapshot of the group rate. The payload is ASCII:

```text
RRUDP1 rpm=2512.5 bfs_ms=5.81543 timing_deg=24 ...
```

The first token names the format and its version. Every other token is
`key=value` with a finite decimal value of seven significant digits. A channel
without a finite value is left out, and the receiver keeps its previous value.
Nothing is sent until the wire schema is verified. The `Feed` status field
reports the endpoint, the datagram count, and the last send error.

The `load` channel is the coordinate that the ECU indexes its maps by:
snapshot byte `0xFFFF102C` on JK08A, the Base Fuel Schedule as a Q7 ratio to
reference word `ROM16[0x9534]` of the flashed ROM, saturated at raw 255. The
stream carries the byte as `normalized_load_raw`, so the value comes from the
running ECU and needs no ROM open in RomRaider. Raw 128 is 100 percent of the
reference, and raw 255 is 199.2 percent. A replay of a profile 5 recording has
no load byte, and its datagrams leave `load` out.

`--publish-udp [HOST:]PORT` turns the feed on at that endpoint for one run
without changing the settings file.

| Key | RomRaider Logger ID | Units | Source |
| --- | --- | --- | --- |
| `rpm` | `X_VQ_Engine_Speed` | RPM | `0x180` bytes 0..1 `/ 8` |
| `load` | `X_VQ_Engine_Load` | % | `normalized_load_raw * 100 / 128` |
| `bfs_ms` | `X_VQ_Base_Fuel_Schedule` | ms | `bfs_raw / 2048` |
| `timing_deg` | `X_VQ_Timing_Command` | degBTDC | `final_timing_raw` |
| `maf_g_s` | `X_VQ_Total_Airflow` | g/s | `maf_total_raw / 100` |
| `throttle_pct` | `X_VQ_Absolute_Throttle` | % | `absolute_throttle_raw * 100 / 255` |
| `coolant_c` | `X_VQ_Coolant_Temperature` | C | `coolant_raw - 50` |
| `iat_c` | `X_VQ_Intake_Air_Temperature` | C | `iat_raw - 50` |
| `intake_cam_b1_deg`, `intake_cam_b2_deg` | `X_VQ_Intake_Cam_B1`, `X_VQ_Intake_Cam_B2` | degCA | `(raw - 128) * 0.5` |
| `stft_b1_pct`, `stft_b2_pct` | `X_VQ_STFT_B1`, `X_VQ_STFT_B2` | % | `raw / 256 - 100` |
| `ltft_b1_pct`, `ltft_b2_pct` | `X_VQ_LTFT_B1`, `X_VQ_LTFT_B2` | % | `raw / 256 - 100` |
| `battery_v` | `X_VQ_Battery_Voltage` | V | `battery_voltage_raw * 0.08` |
| `throttle_target_pct` | `X_VQ_Throttle_Target` | % | `throttle_target_channel_0_raw * 34285 / 1114112` |
| `request_flow_pct` | `X_VQ_QH0_Flow_Potential` | %* | `request_flow_raw * 0.00152588` |
| `alpha_n_flow_pct` | `X_VQ_QH0_Flow_Quantity` | %* | `alpha_n_flow_raw * 0.390625` |

`throttle_target_pct` carries the channel 0 throttle target, which is the
coordinate of throttle opening table `0x155A0`. Its factor is the code scale of
that axis, so Overlay Log compares the live value with the stored points
directly.

`request_flow_pct` and `alpha_n_flow_pct` carry the column coordinates of the
requested-torque conversion surfaces and of Fuel Compensation Main. Each lookup
compares the stored points of its column axis, `0x14114` and `0x11D4C`, with
the coordinate directly, so each factor is the expression of that axis. The
percent unit of both axes is a catalog candidate, which the `*` marks.

### RomRaider table overlay

RomRaider Logger receives the feed through its UDP external data source. The
plugin file declares the same channel table and the listening endpoint, so
the dashboard writes it: `INSTALL PLUGIN` in the `FEED` dialog places
`vq-telemetry.plugin` in the per-user RomRaider folder,
`~/.RomRaider/plugins` (`%USERPROFILE%\.RomRaider\plugins` on Windows), which
a RomRaider build with the UDP external data source reads beside its own
`plugins` folder when Logger starts. The file is out of date after an
endpoint change and after a dashboard update that changes the channel table;
`INSTALL PLUGIN` replaces it, and Logger reads it at its next start.
`python3 -m tools.can_dashboard.live_feed --write-plugin PATH [--endpoint
[HOST:]PORT]` writes the same file to any other path.

RomRaider derives a Logger ID from the item name as `X_` plus
the name with underscores for spaces. A table axis whose definition carries
that ID in `logparam` follows the live value: with `Overlay Log` enabled on the
table toolbar, RomRaider outlines the cell at the axis values nearest to the
live coordinates.

RomRaider Logger has no transport to this ECU, so it runs with no ECU module
selected and polls external sources alone. The Logger must be started from the
RomRaider editor, because the overlay reaches only tables of the same process.
The Logger samples the last received value; its own CSV is therefore a
resampled copy, and the MLG recording stays the reference log.

## MLG recording

The `REC` button selects a destination and starts an atomic MLVLG v2 recording;
it stays lit while the recording runs. Only complete strict telemetry snapshots
produce records. A second press, source stop, source replacement, and
leaving the window finalize and validate the file. Every way out leads to the
same shutdown: the close button, the quit command of the platform, and the end
of the main loop, so a recording survives a quit the same way it survives a
close.
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

The `tuning` MLG schema has 88 channels: time, schema state, every fixed and
rotating custom-telemetry field, a decoded high-detonation-surface selector,
stock CAN RPM, vehicle speed, selector code, transmission gear, ASCD input,
and dashboard state.
Decoded telemetry and context values use F32, so a rotating context that has
not arrived yet can be represented as `NaN` rather than a fabricated zero.

Channel names carry no candidate marker; the marker stays in the units, as it
does on the display, under the MegaLogViewer naming and scaling rules in
[`../logs/README.md`](../logs/README.md#peak-trc-telemetry-to-mlg). Both
numbers are derived from the calibrations the dashboard applies to the same
field, and the recorder tests bind every channel value to the live engineering
value. `tools/logs/mlg_restamp.py` applies a corrected field table to files
recorded earlier without rewriting their data.

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

## Replay

`REPLAY` opens a PEAK PCAN-View TRC 1.1 trace, a dashboard MLG recording, or a
compact candump log with lines such as
`(12.500000) can0 6F0#A001020304050607`; the suffix selects the reader, and
`--replay PATH` opens a file at start. The file is read completely in the
background before playback. A trace keeps the telemetry frames, the stock
frames the dashboard reads, and the PEAK error records. An MLG recording keeps
one record per snapshot, skips the hold-last bridge records, and requires the
`Elapsed` and telemetry tick channels of a dashboard recording.

TRC and candump frames pass through the telemetry decoder as live frames do.
An MLG record replaces a decoded group: it restores the raw value of every
field, the stock context, and the schema verification that the recording
dashboard held, so the replayed engineering values equal the recorded
channels. A rotating context that had not arrived when the record was written
stays `--`. A record of retired profile 5 restores the fields of that profile,
and a field it does not carry stays `--`.

While a replay is loaded, a transport bar appears under the status fields,
or under the timer bar while it is shown:

| Control | Function |
| --- | --- |
| `PLAY` / `PAUSE`, `Space` | plays or pauses; at the end, `PLAY` starts again from the loop start |
| timeline | a click or drag previews a position, and the release moves the replay there |
| `Left`, `Right` | move 5 s back or forward |
| `Home` | returns to the loop start |
| `LOOP` | repeats the whole replay, or the region between `IN` and `OUT`; lit while on, and turned on at or after the end of the region, it moves the replay to the region start |
| `IN`, `OUT` | start or end the loop region at the current position; lit while set, and a second press clears the point |
| `SAVE LOOP` | writes the region between `IN` and `OUT`, or the whole replay, to a new file in the format of the replay |
| speed | cycles through 0.25x, 0.5x, 1x, 2x, 4x, and 8x |

The keys act in the main window outside the `CH` and `ID` entries, and a tool
button that holds the keyboard focus takes `Space` for itself.
`--replay-speed` sets the starting speed and `--replay-loop` starts with
`LOOP` on. A paused
replay reports `PAUSED` as its link state.

`SAVE LOOP` offers a name made of the source name and the region in seconds,
such as `drive_12.5-40.0s.trc`, in the directory of the source. The output
keeps the reader of the source: a name chosen in the dialog whose suffix
selects another reader receives the suffix of the source, and the output
cannot replace the source. The excerpt holds the records whose replay time
lies inside the region, and its replay time starts at zero on its first
record:

| Source | Excerpt |
| --- | --- |
| PEAK TRC 1.1 | every record of the region, including the frames the dashboard does not read and the PEAK status rows, numbered again from 1; the offsets drop by the offset of the first kept record, `$STARTTIME` and the `Start time` comment move forward by the same amount, and a comment names the source and its offset range |
| candump | the lines of the region, unchanged, because the replay counts candump time from the first line |
| dashboard MLG | the data blocks of the region; `Elapsed` and the block timestamps drop by the elapsed time of the first kept snapshot and the header start moves forward by its whole seconds, `Date` keeps the recorded second, a bridge record is kept only after a kept snapshot, and marker blocks are left out |

The excerpt is written to a temporary file in the output directory, checked
by the validator of its format, and then renamed, so a failed save leaves no
partial file. The note beside the replay time names the saved file or the
reason a save failed, and the next replay clears it.

A position change rebuilds the model at the target. The model replays the
3 s before the target, so rotating contexts and stock frames are current when
playback continues, and the selected map and the acceleration timers resume
from a copy of their state that loading takes every 1 s of source time. Hero
traces restart at the target. When more items fall due than one source poll
processes, playback falls behind the window clock instead of skipping items.
An MLG recording holds one continuous time line, so a position change or a
loop jump ends a running recording.

## Drive context

The `Gear`, `Selected map`, `Rolling Launch`, and `Rolling Launch reason` rows
of the `Temperatures and context` panel show the transmission gear, the
selected map, and the Rolling Launch state, and the optional timer bar shows
the 0-100 and 100-200 km/h times. `GEAR`, `SELECTED MAP`, `0-100 KM/H`,
and `100-200 KM/H` are also available as hero cards.

### Transmission gear

`Gear` is the current gear that the transmission control module reports in
the low nibble of frame `0x174` byte 3, which the TCM sends every 10 ms. The
row follows the gear in D and DS as well as in manual mode. The ECU reads the
nibble values 1 through 7 as gears, and the high nibble holds the target gear,
which changes first in a shift. P and N report `0xAA` and R reports `0x99`,
which carry no forward gear, so the row reads `--`. The MLG recording stores
the value as the `Gear` channel, `NaN` where the TCM reports no forward gear.

### Selected map

Profiles 6 and 7 carry the active map index `0xFFFF5D00` of the map-switching
runtime in context tag 2, and `Selected map` shows the index plus 1. An index
outside 0 through 4 shows `1`, because the runtime resolves an invalid index to
Map 1. Hover over the row name names the stream as the source.

A stream without the index, such as a replay of a profile 5 recording, infers
the map from the stock bus under the runtime contract of
[`../../patches/map-switching-selector.md`](../../patches/map-switching-selector.md):
every controller start selects Map 1, a SET + CANCEL gesture with N CANCEL
taps commits Map N, and the runtime answers the commit with N pulses of ASCD
display state 4 on frame `0x551` byte 5 while it ignores selector input.

| Observation | Shown |
| --- | --- |
| a telemetry run that opens with tick16 at most `0xFF` after at least 1 s without any frame, or a tick16 restart inside the stream | `1` |
| a gesture on frame `0x239` byte 3 answered within 0.6 s of the release by exactly as many ON phases of at most 0.45 s as it counted CANCEL taps, closed by 0.45 s of state 0 | `N` |
| a gesture answered by another pulse count, or by an ON state that cannot be counted | `--` |
| a gesture without feedback | unchanged |

A source that joins a controller run in progress shows `--` until the next
controller start or confirmed selection. Hover over the row name adds the
observation behind the value to the description of the map. The inference
does not follow a selection the bus does not show, such as a commit whose
frames were lost.

### Rolling Launch

`Rolling Launch` shows the phase `0xFFFF5D40` of the Rolling Launch runtime,
`IDLE`, `ACTIVE`, or `COOLDOWN`, and `Rolling Launch reason` shows the abort
reason `0xFFFF5D41` by the names of the runtime enumeration, such as
`BUTTON INVALID` or `TIMEOUT`. In `IDLE` the reason names the first gate that
fails, in `ACTIVE` it reads `NONE`, and in `COOLDOWN` it keeps the reason that
ended the run. A code outside the enumeration shows as hex, such as `0x13`.
The phase refreshes with every snapshot and the reason with context tag 0.
[`../../patches/rolling-launch.md`](../../patches/rolling-launch.md) specifies
the gates and the abort reasons. A replay of a profile 5 recording shows `--`
in both rows.

### Acceleration timer

The `0-100` header button shows the timer bar under the status fields. The
bar is hidden by default, and the choice persists with the other settings.
The timers run while the bar is hidden, so the hero cards keep their results.

The timers read the ABS vehicle speed of frame `0x280`, which reads 0 below
about 1.5 km/h, at its 20 ms period. A 0-100 run arms at standstill and
starts at the first sample above zero, so it starts slightly after the vehicle
begins to move. A 100-200 run arms below 97 km/h and starts where the speed
crosses 100 km/h. A run ends where the speed crosses its end speed; both
crossings are interpolated linearly between the samples around them. A run is
discarded when the speed returns to zero, falls more than 2 km/h below its
peak, gains nothing for 2 s, exceeds 30 s for 0-100 or 60 s for 100-200, or
when samples stop for more than 0.5 s.

The value is amber while a run is timed and then shows the last result beside
the best result of the source. `RESET TIMES` on the timer bar clears both. A
new source starts empty, and a replay position change restores the results
the replay had reached at the target.

## Window layout

The window opens inside the current screen and remains usable down to
`560x460`. The source queue, the MLG recording, and the live value feed run on
a 25 ms timer, and the window is painted on a 50 ms timer of its own. The two
timers stay separate because a toolkit rounds a timer up to the step of its own
event loop: a painting driven from the queue timer lands on the first queue tick
past its interval, which on a platform whose step is coarser than the queue
interval halves the rate the painting interval names. Only the selected panel
set follows live values; the other set is written when its tab is selected. The header is one compact row: the short product name with the
version as `VQCT vX.Y.Z`, source state, channel and data-ID entries, and the
tool buttons; the title of the operating-system window carries the full
product name. Header controls, status fields, and health counters flow into
additional rows instead of leaving the window; a flow bar positions its items
by coordinates inside itself, without row frames. The timer bar follows the
status fields while the `0-100` button shows it, and a loaded replay adds its
transport bar under the status fields or the timer bar. The card
and panel area scrolls vertically when the remaining height is short. `PRIMARY` and
`EXTENDED` select the panel set.

The four detail panels of a set share one row and shrink with the window down
to a `250 px` cell. A narrower window folds them into two rows of two, and a
window below two such cells into one column; a folded grid fills its rows
evenly and leaves no single panel on a row of its own. A shrinking panel takes
width from its value column first, from 19 down to 13 characters, and then
elides its labels in the middle, which keeps a trailing bank or channel suffix
readable. Hover over a label reports its full text.

Tool buttons are flat, carry an icon and a lit state, and are drawn the same
on every platform. A button is a canvas inside a frame whose background is the
one-pixel border, and the border takes the focus color under keyboard focus.
The canvas draws a vector icon of `icons.py` before the caption. The icon is
1.1 em on a side, centered on the capital height of the caption, and drawn in
the text color of the button, so it stays sharp at every display scale and
follows the lit state; a button wider than its content centers the icon and
the caption together. No label or button face of the window has a highlight
ring of its own: macOS Tk 9 draws the ring of a label in the coordinates of
its parent instead of the window, which shifts the ring by the offset of the
parent and draws it across the text.

| Button | Icon | Function | Lit |
| --- | --- | --- | --- |
| `ACK` | `exchange` | selects the active/ACK state for the next PCAN connection | active/ACK selected |
| `CONNECT` / `DISCONNECT` | `plug` | one button that follows whether a source worker runs | source running |
| `DEMO` | `flask` | replaces the running source with the demo source | never |
| `REPLAY` | `folder` | replaces the running source with a replay file | never |
| `STREAM` | `broadcast`; `stop` while STOP is offered | sends START, then STOP once START is confirmed | STOP offered |
| `REC` | `dot`; `stop` while recording | starts and stops the MLG recording | recording |
| `FEED` | `share` | opens the live value feed dialog | feed running |
| `CARDS` | `grid` | opens the hero-row card dialog | never |
| `0-100` | `stopwatch` | shows or hides the acceleration timer bar | timer bar shown |
| `RESET TIMES` | `circular-arrow` | on the timer bar, clears the last and best 0-100 and 100-200 km/h times | never |
| `LIGHT` / `DARK` | `sun` / `moon` | switches to the named color theme | never |

A transport button shows the icon of the action it takes next. The replay bar
uses `play` for `PLAY`, `pause` for `PAUSE`, `repeat` for `LOOP`, `mark-in`
for `IN`, `mark-out` for `OUT`, `floppy` for `SAVE LOOP`, and `fast-forward`
for the speed button, and the tabs use `gauge` for `PRIMARY` and `list` for
`EXTENDED`. The dialogs use `plus` for `ADD`, `minus` for `REMOVE`, `up` for
`UP`, `down` for `DOWN`, `circular-arrow` for `DEFAULTS`, `cross` for
`CANCEL`, `check` for `APPLY`, `share` for `PUBLISH`, and `download` for
`INSTALL PLUGIN`.

### Hero row

The top row shows the chosen metrics as cards with a value, a unit, and a
trace of the last 180 snapshots. The cards always share one row: they split
the width equally and shrink with the window. A narrowing card steps its value
font down from 22 pt to 10 pt, drops the unit, and elides the title; hover over
the title reports the full title, the unit, and the value.

A card asks for a width of its own that its content cannot change: the title
takes one character and the value row holds its size against its labels. The
row is therefore laid out from the width of the row alone, and a value that
does not fit is elided instead of widening every card of the row.

`CARDS` opens a dialog with the available metrics on the left and the shown
cards, left to right, on the right. Every metric of the primary and extended
panels can be a card, and the row holds 0 to 12 cards. `DEFAULTS` restores
engine speed, vehicle speed, calculated load, timing command, total airflow,
calculated injection, and coolant temperature. The selector position, the
transmission gear, and the selected map are rows of the
`Temperatures and context` panel and remain available as cards. The line
under the lists describes the metric chosen last in either list.

### Themes and settings

The dark theme is a black high-contrast scheme; the light theme is a white
scheme for daylight. The theme button rebuilds the window in the other theme
and leaves the source, the recording, and the displayed values in place.

The theme, the card list, the live value feed, and the timer bar choice
persist in a per-user JSON file:

| Platform | File |
| --- | --- |
| macOS | `~/Library/Application Support/VQ CAN Telemetry/settings.json` |
| Windows | `%APPDATA%\VQ CAN Telemetry\settings.json` |
| other | `$XDG_CONFIG_HOME/vq-can-telemetry/settings.json`, `~/.config` by default |

`--settings PATH` selects another file. A missing or damaged file gives the
defaults, unknown metric keys are dropped, and every change replaces the file
atomically. The file holds presentation choices and the live value feed, and
never CAN connection parameters. `--smoke-test` reads and writes no settings
file.

### Log file

The dashboard writes a text log of what an operator cannot read after the
fact: the start of a run with its version, profile and CAN ID, every change of
the telemetry source state, stream commands, recording start, save and
failure, and every unhandled exception of the process, of a worker thread and
of a Tk callback. The Windows launcher runs the application through
`pythonw.exe`, which has no console, so the file is the only trace such an
exception leaves. Telemetry values are never written, so the log grows with
events and not with the length of a run.

| Platform | File |
| --- | --- |
| macOS | `~/Library/Application Support/VQ CAN Telemetry/vq-can-telemetry.log` |
| Windows | `%APPDATA%\VQ CAN Telemetry\vq-can-telemetry.log` |
| other | `$XDG_CONFIG_HOME/vq-can-telemetry/vq-can-telemetry.log`, `~/.config` by default |

Rotation bounds the file and drops the oldest records first: at 512 KiB the
file becomes `vq-can-telemetry.log.1`, two older files are kept beside it, and
the log occupies at most 1.5 MiB.

`--log-file PATH` selects another file and `--no-log-file` runs without one. A
file that cannot be opened leaves the run without a log instead of ending it,
and `--smoke-test` writes no log file.

### Scrolling and status fields

The card and panel area answers both a mouse wheel and a trackpad gesture
anywhere over its content. Tk reports trackpad scrolling as its own event, so
each input is bound separately, and the scrollbar keeps its stock bindings.

The scroller holds the height of its content frame, so a panel or a card that
needs more or less room changes what the content asks for without resizing
that frame. The scroller re-measures what the content asks for on its own, and
the scrollbar and the scrollable region follow it. The column of the scrollbar
holds its width whether it is shown or not, so the content keeps one width in
both states.

Every status value carries a title, shortens to the available width with a
trailing ellipsis, and reports its title and full text on hover. A click copies
the untruncated text to the clipboard. Detail-panel values behave the same way,
so a long value cannot widen its column. The health counters below the panels
are separate fields: producer tick, completed groups, schema mismatches, CAN
error frames, producer snapshot overruns, producer transmit aborts, and
telemetry status flags.

Status and health fields reserve the width of their usual value, so live
values change in place instead of shifting the fields beside them. A value
longer than its reserve is elided, and hover and click still report it in full.

## Display semantics

Hover over a panel row name or a card title describes the metric: the
quantity the ECU or the bus carries, the direction of its scale where it
matters, and the evidence boundary of the conversion. The texts live in
`descriptions.py`, and a test requires one for every metric the window offers.

The decoder retains the latest values from the paired page-9 and page-10
contexts for all five tags.
Schema-dependent conversions stay disabled until the in-band health context
matches protocol version, profile ID, and CRC16. The bundled schema declares
profile ID 7 with CRC16 `0x6474` and keeps the frozen contracts of retired
profiles 6 with CRC16 `0xF14E` and 5 with CRC16 `0xE144`, so a recording of
any of these IDs decodes with the fields of its own profile, and the `Schema`
status field names a retired profile. A producer that reports another profile
ID or CRC keeps raw values only, because its slots carry other quantities. The
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
idle value on stock calibration although they are evaluated. The model keeps
the last evaluated margin of a channel while its latch reports the idle value,
and a channel without any evaluation yet stays `NaN` in a recording. The
fields are named by channel: the channel index is the cylinder number of the
event that opens the knock window, and the combustion event a window observes
is not measured. The metric has no physical unit, so the display labels the
signed evaluator counts `cnt`.

Profiles 6 and 7 do not stream the front heated-oxygen-sensor bytes
`0xFFFF22C4..22C5`, timing state `0xFFFF2023`, or the atmospheric-pressure
byte `0xFFFF4544`: no traced code writes the first three, and every recording
reads them as 0, and the fourth holds the default 207 of the disabled
barometric input. Profile 5 carries them, and the display and the MLG
recording leave them out of its replays.

Profile 7 does not stream the work-support ignition-timing adjustment
`0xFFFF564C` either: only its service-0x3B adjustment changes it, and every
recording reads it as 0. The window has no row for it. Profiles 5 and 6 carry
it, and the model converts it to signed degrees in their replays.

The A/F adjustment words and the ignition-timing adjustment hold signed
producer values. Profiles 6 and 7 declare their slots signed. Profile 5
declares them unsigned, and its scale strings read them as `signed raw`: two's
complement values of the slot width. The model converts the signed value
under every profile, and the MLG recorder stores the signed value, because
MegaLogViewer applies only scale and transform. A replay of a recording that
stored the unsigned value decodes to the same display value.

Profile 5 names the slot of the ignition-timing adjustment
`timing_state_564c_raw`, and recordings of earlier versions name its channel
`Timing state 564C`. The model keeps the slot under the name
`ignition_timing_adjustment_raw` of profile 6 for both profile IDs, and the
replay and `tools/logs/mlg_restamp.py` read the earlier channel as
`Timing adjustment`.

A field marked with `*` uses a candidate transform: engine torque state and
torque request at `raw * 0.1 Nm`, throttle area request at `raw * 0.0008 cm2`,
A/F ADJ at signed `raw * 0.002`, and the requested-torque and Fuel
Compensation Main column coordinates at `raw * 0.00152588` and
`raw * 0.390625` percent. The current conversions are:

| Display | Source | Conversion | Evidence boundary |
| --- | --- | --- | --- |
| transmission gear | `0x174` byte 3 low nibble | 1..7 as the gear, every other value `--` | the ECU reads the nibble values 1 through 7 as gears, and the high nibble is the target gear; the captures carry `0xAA` in P and N and `0x99` in R, and in the 2026-09-22 road captures the `0x176` speed ratio matches the current gear in 20,640 of 20,741 stable-gear TCM groups |
| vehicle speed | `0x280` bytes 4..5 | big-endian `raw / 100 km/h` | target field and zero state confirmed; the firmware divides the word by 10, filters it, divides by 20, and publishes twice that byte as J1979 PID 0x0D km/h |
| APP 1/2 | telemetry words | `raw / 200 V` | ten-bit ADC counts; range monitors accept 60..964 and 60..1000 counts, which is 0.30..4.82 V and 0.30..5.00 V against factory bands of 0.5..1.0 V released and 4.2..4.8 V depressed; a 5.0 V full-scale reading would fault sensors inside those bands |
| TPS bank 1/2 | telemetry words | `raw / 200 V` | ten-bit ADC counts; range monitors accept 60..964 counts, which is 0.30..4.82 V against factory terminal criteria of more than 0.36 V released and less than 4.75 V depressed |
| secondary TPS bank 1/2 | `0xFFFF275E`, `0xFFFF2864` | `raw / 200 V` | ten-bit sensor-2 counts published as DIDs 0x1210 and 0x124C; conditioning stage `FUN_0003E4CC` stores bank 2 as `0x0400 - sample`, so the word rises with throttle opening like sensor 1; the bank 1 range monitor accepts 60..964 counts, which is 0.30..4.82 V |
| MAF bank 1/2 | `0xFFFF101C`, `0xFFFF101E` | `raw / 200 V` | ten-bit ADC counts with a unit-nominal Q1.15 trim; the calibration sequence centres on 900 counts, which is 4.50 V, and recordings read 0.425 V with the engine stopped against an expected 0.4 V |
| injection pulse 1..6 | `0xFFFF23C8..0xFFFF23D3` | `raw / 100 ms` | one count is 10 us: the ATU-II channel-8 down-counters run at `Pphi / 64` and the scheduler adds `800 * raw / 256` steps; a compensated software command, not a measured injector-open duration |
| Base Fuel Schedule | `0xFFFF1026` | `raw / 2048 ms` | the fixed normalizers between the schedule and the 10 us pulse word multiply to `(1/8) * (100/256) = 100/2048`; the pulse additionally carries the common gain of 0.75..0.85, both trims, and the injector opening time, and a replay of that chain reproduces the recorded pulse with a median ratio of 1.000 |
| engine load | `0xFFFF102C` byte | `raw * 100 / 128 percent` | scheduler snapshot of `min(255, floor(BFS * 128 / ROM16[0x9534]))` from `FUN_0003B75C` and the column coordinate of the ignition and intake-cam target maps; 100 percent is the reference schedule, and raw 255 saturates at 199.2 percent |
| fuel/oil temperature | `0xFFFF1074`, `0xFFFF2876` | `raw - 50 degC` | outputs of thermistor table `0x12DEA` and of the byte-identical oil curve `0x12C6E`, whose code J1979 PIDs 0x05 and 0x0F declare as `degC + 50`; the factory sensor tables give 20.5 and 52 degC at their 20 and 50 degC reference voltages |
| battery voltage | `0xFFFF1188` byte | `raw * 0.08 V` | ten-bit sample shifted right by two; the ROM limits 125, 131, 137, and 200 of the DTC monitors are the factory test conditions of 10, 10.5, 11, and 16 V; established from ROM constants and factory specifications, not from firmware arithmetic |
| short/long fuel trim | telemetry Q8.8 words | `raw / 256 - 100 percent` | exact neutral representation and target diagnostic agreement |
| timing coordinate | `final_timing_raw` signed byte | `raw degBTDC` | J1979 PID 0x0E publishes `110 - apc_command` as degrees before TDC, which is this coordinate on the normal path; upstream stock coordinate during a Rolling Launch late override, not a measured spark angle |
| total airflow | `0xFFFF3852` word | `raw / 100 g/s` | J1979 PID 0x10 publishes the same `105 * 0xFFFF105C / 256` product as g/s*100; the ECU's airflow model, not a hardware measurement |
| coolant and intake air | `0xFFFF1079`, `0xFFFF2837` | `raw - 50 degC` | J1979 PIDs 0x05 and 0x0F publish the same `0x12DEA` transfer codes minus 10 as `A - 40` degC |
| absolute throttle | `0xFFFF1075` byte | `raw * 100 / 255 percent` | J1979 PID 0x11 returns the byte as `A * 100 / 255` percent |
| APC command | `0xFFFF2022` byte | `110 - raw degBTDC` | `FUN_0004DF82` normally writes `110 - final timing`, and J1979 PID 0x0E reports `110 - raw` as the timing advance in every mode, so the field is the delivered command also where Rolling Launch or a stock mode moves it away from the timing coordinate; `tools/logs/mlg_relation_audit.py` checks `final timing = 110 - raw` on recordings; a software command, not a measured spark angle |
| fuel inhibit | `0xFFFF22E0` byte | `none`, `all`, or the list of cut cylinders | code-proven bit `k` = injector output `k`: a set bit replaces channel word `k` with the opening time and withholds the channel from the fire mask; output `k` drives cylinder `k + 1` by the diagnostic Power Balance order, which is not measured electrically |
| selected map | `0xFFFF5D00` byte | `raw + 1`, `1` outside 0..4 | active index of the map-switching runtime, which resolves an invalid index to Map 1 |
| Rolling Launch phase and reason | `0xFFFF5D40`, `0xFFFF5D41` bytes | names of the `Phase` and `AbortReason` codes of `patches/rolling_launch.py`, hex outside them | runtime state of the Rolling Launch patch |
| knock timing state | `0xFFFF121A` signed word | `raw / 256 state` | exact Q8 software state; its physical unit remains unresolved |
| knock channels | telemetry latch `0xFFFF5E0D` | `none` or the list of channels | code-proven: the evaluator sets bit `c - 1` on an exceedance of channel `c` |
| knock margin ch 1..6 | telemetry latches `0xFFFF5E10..0xFFFF5E1B` | signed evaluator counts, `cnt` | the wrapper behind the only literal of the knock slice evaluator repeats the stock `threshold + 0x80000000 < metric` comparison on the values the evaluator leaves in RAM; the unit of the metric is the summed and gain-scaled sensor difference and has no physical conversion |
| active hot surface | `0xFFFF2466.bit6` | clear = High Octane, set = High Detonation | exact selector; other bits in the byte have separate roles |
| exhaust CVTC target and actual B1/B2 | `0xFFFF2327`, `0xFFFF2324..2325` | `(raw - 128) * 0.5 degCA` | code-proven edge-phase count; recordings keep the actual bytes within two counts of a steady target in 98 percent of Map 3 samples |
| intake CVTC target and actual B1/B2 | `0xFFFF2326`, `0xFFFF2442..2443` | `(raw - 128) * 0.5 degCA` | code-proven edge-phase count, advance positive; recordings keep the actual bytes within two counts of a steady target in 95 to 100 percent of samples |
| intake CVTC duty live pair and command B1/B2 | `0xFFFF2440..2441`, `0xFFFF23B4..23B5` | `raw * 39 / 100 percent` | code-proven ATU-II conversion; the command pair is the scheduler block-copy latch of the live pair, both pairs share context tag 1 and come from one capture pass, and profile 5 recordings hold them equal in every record |
| exhaust CVTC duty B1/B2 words | `0xFFFF1AAC`, `0xFFFF1AAE` | `raw * 100 / 1024 percent` | code-proven output-stage conversion |
| throttle target B1/B2 | `0xFFFF28BC`, `0xFFFF28BE` | `raw * 34285 / 1114112 percent` | each target is `4 * (TPS counts - learned closed position)`, the coordinate of throttle opening table `0x155A0`; `FUN_0006F236` publishes that coordinate, divided by four and less idle base `0xFFFF28F8`, as J1979 PID 0x11 absolute throttle at gradient `0x505B / 65536`, so one count is `34285 / 1114112` percent of throttle opening and 1.25 mV of the primary sensor; the learned closed position is not streamed, and in steady state the target reads the TPS voltage minus that position; steady-state recordings pair TPS bank 1 with channel 0 and TPS bank 2 with channel 1 at a slope of one quarter |
| throttle area request | `0xFFFF19B2` word | candidate `raw * 0.0008 cm2` | opening area of both throttle bodies in the counts of table `0x13202`; the unit rests on the catalog scale of that table |
| requested-torque column coordinate | `0xFFFF1980` word | candidate `raw * 0.00152588 percent` | `FUN_00073948` looks the coordinate up from an opening area over engine speed and passes it to requested-torque surface `0xE98E`, whose word core `0x26984` compares each point of column axis `0x14114` with it directly; the percent unit is the catalog scale of that axis |
| Fuel Compensation Main column coordinate | `0xFFFF1170` byte | candidate `raw * 0.390625 percent` | `FUN_0003B498` writes the high byte of curve `0x15042` or `0x15022` over an opening area divided by engine speed, and byte core `0x26944` compares each point of column axis `0x11D4C` with it directly; the percent unit is the catalog scale of that axis |
| torque request | `0xFFFF19C6` signed word | candidate `raw * 0.1 Nm` | output of table `0xE98E` minus `0x8000`; at full pedal the recorded request follows the maximum of the table row at the recorded engine speed |
| A/F sensor 1 B1/B2 | `0xFFFF2780`, `0xFFFF2782` | `raw / 200 V` | the ADC count re-based so that the filtered sensor reference reads 440, which is 2.20 V, the value around which the factory data monitor fluctuates warm at 2000 rpm; lower is richer; under sustained enrichment both words read lean of 440, which is unexplained, so the channel does not validate full-load fuelling without an independent wideband |
| A/F ADJ B1/B2 | `0xFFFF45A0`, `0xFFFF45A2` | candidate signed `raw * 0.002` | signed integrators bounded to -500..500 counts, read as signed by every consumer; the factor maps the bounds to -1..1 and the factory running range of -0.330..0.330 to 165 counts; every recording reads 0 |
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
field carries the effective command in the same unit.

Health indicators include complete snapshot and frame rates, tick-derived
loss, incomplete and malformed groups, producer restarts, schema mismatches,
source queue drops, telemetry status flags, and the rotating overrun and abort
counters. A controller restart reopens the telemetry tick, so the dashboard
keeps following the stream across an ignition cycle, counts the restart, and
excludes the gap from the loss count.

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
mailbox-26 operation, and the earlier bus-load level. The dashboard does not
decode schema 1. The eleven-frame schema-2 stream requires its own bounded
target-vehicle capture before normal logging use.
