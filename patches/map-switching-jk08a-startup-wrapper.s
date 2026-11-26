// Startup wrapper for the JK08A five-slot selector with cruise-free state init.
//
// The wrapper publishes map 1 before the stock initializer so every lookup
// performed during initialization uses the safe default, commits both limiter
// shadows for map 1, initializes the cruise-free extension RAM (unobserved
// stationary state), and returns through the caller's original PR.

.org 0x000D22A0
startup_wrapper:
sts.l pr,@-r15
mov.l @(startup_selector_state,pc),r1
mov #0x0,r0
mov.b r0,@r1
mov.l @(startup_stock_initializer,pc),r0
jsr @r0
nop
mov #0x0,r4
mov.l @(startup_commit_entry,pc),r0
jsr @r0
nop
mov.l @(startup_cruise_free_init,pc),r0
jsr @r0
nop
lds.l @r15+,pr
rts
nop

.org 0x000D22E0
startup_stock_initializer:
.long 0x0002C648
startup_selector_state:
.long 0xFFFF5D00
startup_commit_entry:
.long 0x000D3660
startup_cruise_free_init:
.long 0x000D6820
