# VQ HR ECU Pin Tracer

This directory contains an offline workspace for manually tracing the
128-terminal VQ HR ECM connector set to the Renesas SH7058 FP-256H MCU.

## Data sources

- ECM connector layout and terminal names were transcribed from the user-provided
  one-page `ecu pinout.pdf`, SHA-256
  `9126b97d5530863ecbf568a140f8d3726f7b9db909d19a8e8e36de13c70b15a2`.
- ECM terminal descriptions and direction labels were checked against
  `ENGINE CONTROL SYSTEM.pdf` from the 2007 G35 Sedan factory service manual,
  SHA-256
  `f34ae5e56df11de9e069b3dcd637d4fc509321ce8ac3f7eb0dfc3293e3ac55fc`,
  service pages EC-489 through EC-500. Terminal 87 is marked as an output in
  the table even though its power-steering-pressure sensor voltage is an ECM
  input; the workspace exposes this source conflict instead of silently
  choosing the printed direction.
- MCU package pin numbers and multiplexed functions come from
  `refs/renesas-sh7059-sh7058s-hardware-manual.pdf`, SHA-256
  `6d8b0e3511ed583df0bec31d0d28641d1b06b23042985f41ad2d9df44fccd8ca`,
  figure 1.2, table 1.3, and the SH7058 Rev. 3 comparison appendix. The main
  table describes the SH7058S/SH7059 superset; eleven SSU alternate functions
  absent from SH7058 Rev. 3 are deliberately omitted.
- Preloaded relationships are explicitly hypotheses. Injector and ignition
  candidates combine the peripheral family used by the target firmware with an
  older Nissan SH7055 channel pattern. Their exact physical pin and cylinder
  assignment is not established. Cross-model candidates are labeled
  separately, and CAN candidates assert only a permitted MCU multiplexer
  pairing.

## Use

For predictable local-storage behavior, serve the directory from the repository:

```bash
python3 -m http.server 8765 --directory tools/pin-tracer
```

Open `http://localhost:8765/` in a current browser. Select an ECM terminal and an
enabled MCU pin, choose a topology template, record the observed component path,
and save the connection. Every saved pair represents a route physically followed
by continuity measurement or visual board inspection. Directly opening
`index.html` also works in browsers that permit local storage for `file:` pages.

Use the compact `EN` / `RU` switch to select the interface language. The choice
applies to controls, tooltips, signal descriptions, topology guidance, validation
messages, and generated route templates. It is stored separately from tracing
data, included in exported workspace preferences, and survives `Clear workspace`.
Changing the interface language does not translate operator-entered component
paths or comments, so recorded observations remain verbatim.

ECM terminal colors follow the same functional category legend as MCU pins.
Terminal groups 1-8, 49-56, and 121-128 are drawn wider because the connector
drawing shows physically wider cavities. This presentation does not assign a
current rating. Hover over any ECM terminal to see its complete connector,
factory signal label, expanded function, service-table direction, and expanded
wire color in the browser tooltip. The selected-terminal card repeats those
semantics in the connection editor.

Selecting an ECM terminal automatically highlights every MCU pin whose
documented capabilities match the generic signal class. A pin can belong to
more than one class, for example timer and communication. Bus, power, clock,
debug, reset, NMI, and watchdog pins remain disabled until the advanced-pin
option is enabled. Selecting an MCU pin first performs the inverse operation and
highlights every populated ECM terminal whose generic endpoint classes overlap
the MCU pin capabilities.

The browser stores connections in local storage under
`vq-hr-ecu-pin-tracer-v1`. Export the workspace to JSON after every tracing
session. Import replaces the current browser workspace after confirmation.
Saved connection lines remain hidden by default to keep the package view
readable. Enable `Show saved lines` when the complete routing overlay is useful.
The active connection under selection is always shown.

Import and local restoration require the workspace's source SHA-256 bindings
to match the reference revisions used by the application. A missing or differing
binding names the source and reports its expected and received digest.

A failed restoration preserves the original stored payload verbatim. Language
and checkbox changes leave that record untouched, and new connections cannot
be saved until recovery or discard. `Export JSON` downloads the original record
with an `-unrestored` filename suffix. A valid `Import JSON` replaces it only
after confirmation; `Clear workspace` explicitly discards it after confirmation,
including when no connections could be loaded. The storage status retains the
error and the available actions through language changes.

The topology box is a generic circuit template, not an observed path. The route
field is intentionally blank for a new pair and must contain the component path
found on the physical board. `Use template` copies the selected generic template
into the field as an editable starting point; it still requires verification
against the board. CAN, K-line, supply, and ground guidance explicitly describes
shared or branching endpoint models instead of implying one-to-one
connector-to-MCU wiring.

## Export contract and downstream use

An exported `vq-hr-ecu-pin-tracer/v1` file is an operator record of manual work
on a physical board. Each connection contains an ECM terminal, an MCU package
pin, a generic topology class, the mandatory component path observed on the
board, an optional comment, and creation/update timestamps. Top-level SHA-256
values bind the workspace to the connector pinout, Renesas manual, and Nissan
service-manual revision used by the UI. Display preferences, including the
interface language, are not evidence.

Reviewed exports are intended to provide the hardware link between factory
signal semantics and firmware analysis:

1. Map an ESM terminal label to its observed protection, conditioning, driver,
   transceiver, or ASIC path and then to an SH7058 package pin.
2. Check the exact firmware pin-function-controller configuration and identify
   the corresponding ADC, timer, serial, interrupt, or GPIO registers.
3. Follow register xrefs into firmware functions and use the resulting
   signal-to-code path to prioritize unresolved map, flag, and control-path
   hypotheses.
4. Design a targeted CONSULT3P, logging, or bench test for the remaining
   behavioral claim.

Physical continuity establishes board connectivity, not map semantics,
direction under every operating state, or runtime use of a multiplexed MCU
function. A trace therefore narrows and grounds firmware analysis but does not
by itself promote a Map or Axis claim to `silicon`.

The v1 schema does not identify the exact ECU, PCB revision, MCU marking,
operator, instrument, or tracing session. Before an export is admitted as
project evidence, keep it with a review record containing those provenance
fields and do not merge observations from different boards. A future schema
revision should carry this provenance directly. No Memgraph loader currently
consumes pin-tracer JSON; reviewed exports remain operator artifacts until that
loader and a canonical storage location are defined.

## Tests

Run the model, validation, and embedded-data tests with Node.js:

```bash
cd tools/pin-tracer
npm test
```

The test suite covers signal classification, topology suggestions, import
validation, duplicate prevention, statistics, HTML escaping, language-catalog
parity, locale persistence, and translation coverage for every populated ECM
description, source note, MCU hypothesis, topology family, and evidence label.
It also verifies the integrity of all ECM and MCU pin data embedded in the page.
Reference hashes protect the audited 102 populated ECM terminals and all 256
SH7058 package positions from unreviewed transcription changes.

Preloaded hypotheses remain suggestions and are never saved as traced pairs
automatically.

## Limits

- The source PDF lists only populated ECM terminals. Unlisted terminal positions
  remain visible without an assigned signal.
- MCU pin multiplexing depends on pin-function-controller configuration in the
  exact firmware.
- Preloaded exact-looking target pairs remain unverified until continuity,
  component-path, and pin-function-controller evidence agree.
- Connector signals can terminate at a custom ASIC or driver rather than at one
  MCU pin. Such routes should name the intermediate component and shared
  interface.
- Package orientation and continuity must be verified on the exact ECU hardware
  revision before recording a traced pair.
