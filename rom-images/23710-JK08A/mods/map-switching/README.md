# JK08A ten-family map switching

`1JK08A-20260726-immo-e2-pops-fuel-throttle-ofc-v2-map-switching-full-dfco-v3.bin`
is the production composition of the complete five-slot runtime over the
checksum-valid tuned JK08A input.

| Property | Value |
|---|---|
| Size | 1,048,576 bytes |
| Source SHA-256 | `1bf9978ba1d870216bd85ff69aed25243a77f186231718dcfffd9bb411529471` |
| Output SHA-256 | `0efb43e6cf1feba91bf0beb19120d8f54d996a72650868a5469a0d81ede98da6` |
| Output MD5 | `693917aad583784b082f0cec77bad4cc` |
| Checksum references | all six valid |
| Software verification | PASS under the superseded `0x00` release model |
| Hardware overlay chain | PASS for stages 15 through 19 on 2026-08-05 |
| Functional map selection | FAIL: selector does not arm with released code `0x20` |
| Production-image write | not performed |

The runtime switches ten calibration families per slot: DFCO Hold, Entry,
Full Restore, and Intermediate Restore thresholds; two ignition trim tables;
Fuel Targets; Fuel Compensation Main; and both rev-limiter families. The
selector, atomic limiter commit, startup initialization, and CAN 0x551 visual
feedback are active.

The production image and hardware-test stage 19 are byte-identical except for
the complete `0x8080..0x80FF` line. The production input retains `0xEE`; the
PCMFlash readback-derived hardware chain contains the already accepted
zero-filled variant. This line is outside every documented JK08A checksum
domain and has already passed ECU identification in the earlier gates.

## Historical hardware overlay chain

The five cumulative test images are retained under
`tmp/old/hardware-full-dfco/`. They were written in numeric order over the
exact successful stage-14 readback with SHA-256
`f0a03f6fef205aa1ac42e4471dd0bad995a7082c35d24bdb639fc342ccdda892`.

| Stage | File suffix | SHA-256 | Purpose |
|---:|---|---|---|
| 15 | `full-dfco-payload-map1.bin` | `5b7816f7be70e12f1312dbff9727df9a5677192811515ce8f6b66d1793bea7f2` | Install inactive four-family DFCO adapter and Map 1-equivalent Hold and Intermediate Restore storage |
| 16 | `dfco-hold-entry-hook-4fdd0.bin` | `84796d58bdd3c45ba4c6774f936bedd54109cbee7a60053dcecf0b38c4777e58` | Activate shared Hold and Entry hook |
| 17 | `dfco-full-intermediate-restore-hook-50258.bin` | `e89bd22402e416c9178286b554b1d1d054586c49096574d1c88d9bd5e96f9e0d` | Activate shared Full and Intermediate Restore hook |
| 18 | `selector-host-boot-only-no-map-gesture.bin` | `4732168ad4aa0f8b8bf11e0b25b1ae506eed50713c789d3fb4297fafa9c37ac0` | Activate selector host with CAN feedback absent |
| 19 | `can-feedback-full-runtime.bin` | `e2fb90d5d9f2ba23c09cb55ee77732175ae0753aabe77f8e7363a84554218ea1` | Activate CAN feedback and complete the runtime |

Stages 15 through 17 do not execute the selector. Stage 18 is an identification
and boot gate only: no map-selection gesture is permitted because queued
feedback cannot drain while the serializer hook remains stock. Functional
selection starts only after stage 19. Every file is one MiB, passes all six
checksum references, has an MD5 sidecar, and is listed in the ordered manifest
`1JK08A-map-switching-safe-v3-full-dfco.sha256` in the same directory.

The 2026-08-05 hardware run reports startup and identification `PASS` for every
stage from 15 through 19. Vehicle testing reports functional selection `FAIL`:
CAN frame `0x239`, byte 4, uses `0x20` for all buttons off, while the selector
requires a `0x00 -> SET` transition. No final readback accompanies the report,
so the endpoint is not classified as `PASS_EXACT`. The production file itself
remains unflashed; its runtime is byte-identical to stage 19 outside the
accepted `0x8080..0x80FF` line variant.

The current GNU SH-2E gate independently reproduces all eight corrected Ghidra
blobs, audits 414 instructions, executes 116 map-switching cases including the
`0x20` neutral transition, and verifies the original unsafe delay-slot pair as
a failing control. Ghidra p-code executes the same 116 cases and reaches all 11
implementation entries. The corrected custom runtime is distributed as
Overlay 21 under `tmp/`, leaving these historical stage hashes unchanged.

## Corrected hardware chain

`patches/build_map_switching_full_dfco_overlays.py` keeps stages 15 through 17
byte-identical to the historical chain and replaces stages 18 and 19 with the
corrected selector implementation. The generated files and ordered manifest
are under `tmp/hardware-button-release-fix/` with prefix
`1JK08A-map-switching-safe-v4`:

| Stage | SHA-256 | MD5 | Hardware status |
|---:|---|---|---|
| 18 | `f42f2ec56b590c7e82b17a343dc966c7c27c1981dde528815020e7d974d30b8c` | `738b0af89283fac2b47e83c187394326` | untested |
| 19 | `52568ec1006df01c2524afe505a4ed9c8b00aa15bf5ea2a946d74107bbd97b84` | `7f07334311ff0f3add57c95f3730f36e` | untested |

Every corrected image passes all six checksum references and the closed-write
set checks. The byte-equivalent corrected selector in custom Overlay 21 passes
target-vehicle Map 2 and Map 3 selection. Its visual-feedback field fails the
V36 display-semantic gate: the injected CAN 0x551 byte-5 low-bit sequence is
present on the bus without a lamp response. Exact JK08A serialization and
public G37/370Z states identify byte-5 mask `0x60`, on `0x60`, off `0x00` as
the next feedback-only hardware candidate. The exact generic stage-18 and
stage-19 files remain unflashed and retain `untested` status.
