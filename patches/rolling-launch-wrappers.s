// Scheduling, selector-arbitration, and startup wrappers for exact JK08A.
//
// The periodic wrapper replaces table index 1, calls the displaced stock
// function first, and then runs the Rolling Launch engine once per exact
// periodic scheduler pass. The selector arbiter leaves normal map switching
// unchanged only in IDLE. ACTIVE, COOLDOWN, and corrupt states call the
// displaced stock ASCD host directly. The startup wrapper clears only the
// dedicated 28-byte Rolling Launch state before the existing map-switching
// startup wrapper initializes map 1 and both limiter shadows.

.org 0x000D3860
rolling_launch_periodic_wrapper:
sts.l pr,@-r15
mov.l @(rolling_launch_periodic_stock,pc),r0
jsr @r0
nop
mov.l @(rolling_launch_engine_entry,pc),r0
jsr @r0
nop
lds.l @r15+,pr
rts
nop

.org 0x000D3880
rolling_launch_selector_arbiter:
mov.l @(rolling_launch_state_address,pc),r1
mov.b @r1,r0
cmp/eq 0x0,r0
bt rolling_launch_selector_idle
mov.l @(rolling_launch_stock_ascd_host,pc),r0
jmp @r0
nop
rolling_launch_selector_idle:
mov.l @(rolling_launch_map_selector_host,pc),r0
jmp @r0
nop

.org 0x000D38A0
rolling_launch_startup_wrapper:
sts.l pr,@-r15
mov.l @(rolling_launch_state_address_startup,pc),r1
mov #0x0,r0
mov #0x7,r2
rolling_launch_startup_clear_loop:
mov.l r0,@r1
add 0x4,r1
dt r2
bf rolling_launch_startup_clear_loop
mov.l @(rolling_launch_base_startup,pc),r0
jsr @r0
nop
lds.l @r15+,pr
rts
nop

.org 0x000D38C8
rolling_launch_periodic_stock:
.long 0x000A9554
rolling_launch_engine_entry:
.long 0x000D38E4
rolling_launch_state_address:
.long 0xFFFF5D40
rolling_launch_stock_ascd_host:
.long 0x000D09D8
rolling_launch_map_selector_host:
.long 0x000D2108
rolling_launch_state_address_startup:
.long 0xFFFF5D40
rolling_launch_base_startup:
.long 0x000D22A0
