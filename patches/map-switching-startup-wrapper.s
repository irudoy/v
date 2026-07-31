// Startup wrapper for the exact JK08A five-slot selector.
//
// The wrapper runs the stock initializer first, reads the retained selector
// index, commits both limiter shadows with map-1 fallback, and returns through
// the caller's original PR.

.org 0x000D22A0
startup_wrapper:
sts.l pr,@-r15
mov.l @(startup_stock_initializer,pc),r0
jsr @r0
nop
mov.l @(startup_selector_state,pc),r1
mov.b @r1,r4
extu.b r4,r4
mov.l @(startup_commit_entry,pc),r0
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
