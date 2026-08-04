// Minimal startup selector-initialization gate for the exact JK08A ROM.
//
// The wrapper publishes Map 1 in the reserved selector byte before entering
// the stock initializer. It preserves the caller's PR and installs no limiter,
// lookup, selector-host, calibration, or CAN-feedback behavior.

.org 0x000D22A0
startup_selector_init:
sts.l pr,@-r15
mov.l @(startup_selector_state,pc),r1
mov #0x0,r0
mov.b r0,@r1
mov.l @(startup_stock_initializer,pc),r0
jsr @r0
nop
lds.l @r15+,pr
rts
nop

.align 4
startup_stock_initializer:
.long 0x0002C648
startup_selector_state:
.long 0xFFFF5D00
