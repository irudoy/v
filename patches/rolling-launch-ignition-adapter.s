// Primary APC command adapter for exact JK08A Rolling Launch.
//
// The primary ignition-command hook 0x0004E198 enters the adapter from the
// APC command builder 0x0004DF82, which has stored the stock command S in
// apc_output 0xFFFF2022 and passes it zero-extended in r4. The timing is 110
// minus the command, so a larger command is later. In an ACTIVE HOLD of map
// slot i without the P0335 APC fallback 0xFFFF24C9.bit6, the effective command
// is P = max(S, min(S + z, floor_command[i])), with z the trim latched at
// activation in state +0x1E. A trim above 40 or a floor above 120 leaves
// P = S. The candidate never advances the stock timing, and a stock command
// above 120 passes unchanged. Outside this hold P = S.
//
// The ignition publisher 0x000D6540 receives S in r4 and candidate P in r5
// and returns the command to apply in r5. It returns S when publication is
// refused. The adapter stores that returned command in 0xFFFF2022, which
// the secondary builder 0x0004E080 and the diagnostics read, and passes it
// to the stock primary consumer 0x0002A892 in r4. Both schedulers therefore
// receive one effective command. It restores r5..r7, MACL and PR before the
// stock tail jump; r0..r3 and T are caller-clobbered.

.org 0x000D3EA0
rolling_launch_ignition_adapter:
sts.l pr,@-r15
sts.l macl,@-r15
mov.l r5,@-r15
mov.l r6,@-r15
mov.l r7,@-r15
mov r4,r5
mov.l @(rl_ign_state_address,pc),r1
mov.b @r1,r0
cmp/eq 0x1,r0
bf rl_ign_publish
mov.b @(0x5,r1),r0
cmp/eq 0x1,r0
bf rl_ign_publish
mov.l @(rl_ign_apc_mode_address,pc),r2
mov.b @r2,r0
tst 0x40,r0
bf rl_ign_publish
mov.b @(0x4,r1),r0
extu.b r0,r0
mov #0x5,r2
cmp/hs r2,r0
bt rl_ign_publish
shll2 r0
mov r0,r2
shll r2
add r2,r0
mov.l @(rl_ign_slot_table,pc),r2
add r0,r2
mov.b @(0x4,r2),r0
extu.b r0,r3
mov #0x78,r2
cmp/hi r2,r3
bt rl_ign_publish
mov #0x1e,r0
mov.b @(r0,r1),r0
extu.b r0,r0
mov #0x28,r2
cmp/hi r2,r0
bt rl_ign_publish
extu.b r4,r2
add r2,r0
cmp/hi r3,r0
bf rl_ign_floor_ready
mov r3,r0
rl_ign_floor_ready:
cmp/hi r2,r0
bf rl_ign_publish
mov r0,r5
rl_ign_publish:
mov.l @(rl_ign_publisher,pc),r0
jsr @r0
nop
mov r5,r0
mov.l @(rl_ign_command_address,pc),r1
mov.b r0,@r1
mov r5,r4
mov.l @r15+,r7
mov.l @r15+,r6
mov.l @r15+,r5
lds.l @r15+,macl
lds.l @r15+,pr
mov.l @(rl_ign_stock_consumer,pc),r0
jmp @r0
nop

.org 0x000D3F48
rl_ign_state_address:
.long 0xFFFF5D40
rl_ign_apc_mode_address:
.long 0xFFFF24C9
rl_ign_slot_table:
.long 0x000D6348
rl_ign_command_address:
.long 0xFFFF2022
rl_ign_publisher:
.long 0x000D6540
rl_ign_stock_consumer:
.long 0x0002A892
