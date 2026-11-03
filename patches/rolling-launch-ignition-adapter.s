// Primary APC command trim for exact JK08A Rolling Launch.
//
// The primary ignition command hook stays on the Rolling Launch layer. Input
// r4 is the stock uint8 command, whose timing is 110 minus the command, so a
// larger command is later. In an ACTIVE hold of map slot i, without the P0335
// APC fallback 0xFFFF24C9.bit6, the adapter replaces r4 with
// max(stock, min(stock + max_trim[i], floor_command[i])) from the slot table
// of the configuration record, so the trim never advances the stock timing.
// Outside such a hold it passes the stock command. It changes only r0..r4 and
// tail-jumps to the stock consumer 0x2A892 with r5..r7 unchanged.

.org 0x000D3EA0
rolling_launch_ignition_adapter:
mov.l @(rl_ign_state_address,pc),r1
mov.b @r1,r0
cmp/eq 0x1,r0
bf rl_ign_stock
mov.b @(0x5,r1),r0
cmp/eq 0x1,r0
bf rl_ign_stock
mov.l @(rl_ign_apc_mode_address,pc),r2
mov.b @r2,r0
tst 0x40,r0
bf rl_ign_stock
mov.b @(0x4,r1),r0
extu.b r0,r0
mov #0x5,r2
cmp/hs r2,r0
bt rl_ign_stock
mov r0,r2
shll r2
shll2 r0
add r2,r0
mov.l @(rl_ign_slot_table,pc),r2
add r0,r2
mov.b @(0x2,r2),r0
extu.b r0,r3
mov.b @(0x3,r2),r0
extu.b r0,r2
extu.b r4,r1
mov r1,r0
add r3,r0
cmp/hi r2,r0
bf rl_ign_floor_ready
mov r2,r0
rl_ign_floor_ready:
cmp/hi r1,r0
bf rl_ign_stock
mov r0,r4
rl_ign_stock:
mov.l @(rl_ign_stock_consumer,pc),r0
jmp @r0
nop

.org 0x000D3EF4
rl_ign_state_address:
.long 0xFFFF5D40
rl_ign_apc_mode_address:
.long 0xFFFF24C9
rl_ign_slot_table:
.long 0x000D6248
rl_ign_stock_consumer:
.long 0x0002A892
