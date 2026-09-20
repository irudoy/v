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
python3 tools/can_dashboard/package_windows.py \
  --output tmp/vq-can-telemetry-windows.zip
```

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

The target writes:

- `tmp/VQ CAN Telemetry.app` for direct local use;
- `tmp/vq-can-telemetry-macos-arm64.zip` for transfer.

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

Replay accepts PEAK PCAN-View TRC 1.1 files directly, including the `.trc`
captures used by the project. It also accepts compact candump lines such as
`(12.500000) can0 6F0#A001020304050607`.

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

The `load` channel is derived, and the datagram leaves it out. It is the
coordinate that the ECU indexes its maps by: a Q7 ratio of the Base Fuel
Schedule word to a ROM-specific reference word, saturated at one byte. One word
of either operand is 1/2048 ms; stock JK08A holds 27226 at `ROM16[0x9534]`,
which RomRaider shows as 13.294 in the table `Fuelling / Load Model / Internal
Load Normalization Reference`. The plugin file states the arithmetic and binds
`reference` to that table:

```properties
udp.item.2.expression=min(255, floor(round(bfs_ms*2048)*128/reference))*100/128
udp.item.2.table.reference=Internal Load Normalization Reference
```

RomRaider evaluates the expression with the stored word of the ROM open in its
editor, so the host schema and the dashboard settings stay ROM-neutral and no
calibration value is typed by hand. The value follows the image in the editor:
a ROM other than the flashed one shifts `load` on every load axis, and with no
ROM open `VQ Engine Load` reads 0. The `VQ CAN Telemetry` entry of the Logger
`Plugins` menu shows the reference word and the ROM file it comes from.

`--publish-udp [HOST:]PORT` turns the feed on at that endpoint for one run
without changing the settings file.

| Key | RomRaider Logger ID | Units | Source |
| --- | --- | --- | --- |
| `rpm` | `X_VQ_Engine_Speed` | RPM | `rpm_raw * 12.5` |
| `load` | `X_VQ_Engine_Load` | % | derived by RomRaider from `bfs_ms` and the reference word of the open ROM |
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

### RomRaider table overlay

RomRaider Logger receives the feed through its UDP external data source. The
plugin file declares the same channel table and the listening endpoint, so
the dashboard writes it: `INSTALL PLUGIN` in the `FEED` dialog places
`vq-telemetry.plugin` in the per-user RomRaider folder,
`~/.RomRaider/plugins` (`%USERPROFILE%\.RomRaider\plugins` on Windows), which
a RomRaider build whose UDP data source supports derived items reads beside
its own `plugins` folder when Logger starts. The file is out of date after an
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
by coordinates inside itself, without row frames. The card and panel area
scrolls vertically when the remaining height is short. `PRIMARY` and
`EXTENDED` select the panel set.

The four detail panels of a set share one row and shrink with the window down
to a `250 px` cell. A narrower window folds them into two rows of two, and a
window below two such cells into one column; a folded grid fills its rows
evenly and leaves no single panel on a row of its own. A shrinking panel takes
width from its value column first, from 19 down to 13 characters, and then
elides its labels in the middle, which keeps a trailing bank or channel suffix
readable. Hover over a label reports its full text.

Tool buttons are flat, carry a lit state, and are drawn the same on every
platform. A button is a label inside a frame whose background is the
one-pixel border, and the border takes the focus color under keyboard focus.
No label of the window has a highlight ring of its own: macOS Tk 9 draws the
ring of a label in the coordinates of its parent instead of the window, which
shifts the ring by the offset of the parent and draws it across the text.

| Button | Function | Lit |
| --- | --- | --- |
| `ACK` | selects the active/ACK state for the next PCAN connection | active/ACK selected |
| `CONNECT` / `DISCONNECT` | one button that follows whether a source worker runs | source running |
| `DEMO`, `REPLAY` | replace the running source directly | never |
| `STREAM` | sends START, then STOP once START is confirmed | STOP offered |
| `REC` | starts and stops the MLG recording | recording |
| `FEED` | opens the live value feed dialog | feed running |
| `CARDS` | opens the hero-row card dialog | never |
| `LIGHT` / `DARK` | switches to the named color theme | never |

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
calculated injection, and coolant temperature. The selector position is a row
of the `Temperatures and context` panel and remains available as a card.

### Themes and settings

The dark theme is a black high-contrast scheme; the light theme is a white
scheme for daylight. The theme button rebuilds the window in the other theme
and leaves the source, the recording, and the displayed values in place.

The theme, the card list, and the live value feed persist in a per-user JSON
file:

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
