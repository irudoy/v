// Entry wrappers for the exact JK08A CAN telemetry runtime.
//
// The main wrapper preserves the displaced FUN_00020DFE call and captures
// after its coherent interrupt-disabled boundary. The knock wrapper latches
// the completed interval before FUN_000493E8 clears its event count. This latch
// is refreshed on every base tick, so a divisor greater than one can overwrite
// an interval before publication. Startup clears only the active 256-byte
// telemetry allocation before continuing the existing Rolling Launch and
// map-switching startup chain.

.org 0x000D4280
telemetry_main_wrapper:
sts.l pr,@-r15
mov.l @(telemetry_main_stock,pc),r0
jsr @r0
nop
mov.l @(telemetry_control_poll_entry,pc),r0
jsr @r0
nop
mov.l @(telemetry_capture_entry,pc),r0
jsr @r0
nop
lds.l @r15+,pr
rts
nop

.align 4
telemetry_main_stock:
.long 0x00020DFE
telemetry_control_poll_entry:
.long 0x000D4EA0
telemetry_capture_entry:
.long 0x000D4340

.org 0x000D42B0
telemetry_knock_wrapper:
sts.l pr,@-r15
mov.l @(telemetry_knock_state,pc),r1
mov.l @(telemetry_knock_count,pc),r2
mov.b @r2,r0
mov.b r0,@(0xC,r1)
mov.l @(telemetry_knock_mask,pc),r2
mov.b @r2,r0
mov.b r0,@(0xD,r1)
mov.l @(telemetry_knock_stock,pc),r0
jsr @r0
nop
lds.l @r15+,pr
rts
nop

.align 4
telemetry_knock_state:
.long 0xFFFF5E00
telemetry_knock_count:
.long 0xFFFF2142
telemetry_knock_mask:
.long 0xFFFF2150
telemetry_knock_stock:
.long 0x000493E8

.org 0x000D42F0
telemetry_startup_wrapper:
sts.l pr,@-r15
mov.l @(telemetry_startup_state,pc),r1
mov #0x40,r2
mov #0x0,r0
telemetry_startup_clear_loop:
mov.l r0,@r1
add 0x4,r1
dt r2
bf telemetry_startup_clear_loop
mov.l @(telemetry_startup_stock,pc),r0
jsr @r0
nop
lds.l @r15+,pr
rts
nop

.align 4
telemetry_startup_state:
.long 0xFFFF5E00
telemetry_startup_stock:
.long 0x000D38A0
