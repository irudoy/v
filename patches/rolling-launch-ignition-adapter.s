// Retard-only primary APC command adapter for exact JK08A.
//
// Input r4 is the stock uint8 command. The adapter records stock/effective
// diagnostic bytes in dedicated RAM. In valid mode 2 ACTIVE state it selects
// max(stock_command, target_command), writes the effective byte back to the
// exact stock diagnostic/secondary-edge source, and tail-jumps to 0x2A892.
// Every inactive, invalid, or APC fallback-mode path tail-jumps with r4
// unchanged. The fallback gate uses exact snapshot 0xFFFF24C9.bit6.

.org 0x000D3EA0
rolling_launch_ignition_adapter:
extu.b r4,r4
mov.l @(rl_ign_state_address,pc),r1
mov r1,r2
add 0x10,r2
mov r4,r0
mov.b r0,@r2
add 0x1,r2
mov.b r0,@r2
mov.l @(rl_ign_apc_mode_address,pc),r3
mov.b @r3,r0
tst 0x40,r0
bf rl_ign_tail
mov.b @r1,r0
cmp/eq 0x1,r0
bf rl_ign_tail
mov.b @(0x5,r1),r0
cmp/eq 0x2,r0
bf rl_ign_tail
mov.b @(0x4,r1),r0
mov r0,r3
extu.b r3,r3
mov #0x5,r0
cmp/hs r0,r3
bt rl_ign_tail
mov.l @(rl_ign_config_address,pc),r1
mov.w @r1,r0
extu.w r0,r0
mov.w @(rl_ign_magic,pc),r2
extu.w r2,r2
cmp/eq r2,r0
bf rl_ign_tail
mov.b @(0x2,r1),r0
cmp/eq 0x1,r0
bf rl_ign_tail
mov.b @(0x3,r1),r0
cmp/eq 0x2,r0
bf rl_ign_tail
mov r3,r0
mov.l @(rl_ign_enable_masks,pc),r2
mov.b @(r0,r2),r2
mov.b @(0x4,r1),r0
and r2,r0
tst r0,r0
bt rl_ign_tail
mov r1,r2
add 0x1C,r2
mov.l @r2,r0
mov.l @(rl_ign_integrity_markers,pc),r2
cmp/eq r2,r0
bf rl_ign_tail
mov r1,r2
add 0x16,r2
mov r3,r0
mov.b @(r0,r2),r2
extu.b r2,r2
mov #0x6E,r0
cmp/hs r0,r2
bf rl_ign_tail
mov #0x76,r0
cmp/hs r0,r2
bt rl_ign_tail
cmp/hs r2,r4
bt rl_ign_store
mov r2,r4
rl_ign_store:
mov.l @(rl_ign_output_address,pc),r1
mov r4,r0
mov.b r0,@r1
mov.l @(rl_ign_state_address,pc),r1
add 0x11,r1
mov.b r0,@r1
rl_ign_tail:
mov.l @(rl_ign_stock_consumer,pc),r0
jmp @r0
nop

.org 0x000D3F38
rl_ign_state_address:
.long 0xFFFF5D40
rl_ign_config_address:
.long 0x000D3F60
rl_ign_output_address:
.long 0xFFFF2022
rl_ign_stock_consumer:
.long 0x0002A892
rl_ign_enable_masks:
.long 0x000D3F4C
rl_ign_enable_mask_bytes:
.byte 0x01,0x02,0x04,0x08,0x10
.align 2
rl_ign_magic:
.word 0x524C
rl_ign_integrity_markers:
.long 0xADB3A55A
rl_ign_apc_mode_address:
.long 0xFFFF24C9
