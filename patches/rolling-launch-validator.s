// Configuration and efficiency-table validator for exact JK08A Rolling Launch.
//
// The schema 6 record at 0xD6320 has a 40-byte head, five 12-byte map slots
// at +0x28 and an end marker at +0x64; the efficiency table E[0..40] follows
// at 0xD6390. The engine checks the head and jumps here with r7 = 1 for a
// valid head. The validator checks the five slots of a valid head and returns
// r0 bit0 for a valid record and r0 bit1 for a valid table: E[0] = 1000 and
// every entry 1..1000. It is a leaf that changes r0..r7 and T.

.org 0x000D6680
rolling_launch_slot_validator:
mov.l @(rl_val_config_address,pc),r3
tst r7,r7
bt rl_val_table
mov #0x0,r7
mov.w @(0xc,r3),r0
extu.w r0,r6
// Five slots, independent of the enable mask.
mov r3,r2
add 0x28,r2
mov #0x5,r5
rl_val_slot_next:
mov.w @r2,r0
cmp/pz r0
bf rl_val_table
mov #0x28,r1
mov.b @(0x2,r2),r0
cmp/hi r1,r0
bt rl_val_table
mov.b @(0x3,r2),r0
cmp/hi r1,r0
bt rl_val_table
mov #0x78,r1
mov.b @(0x4,r2),r0
cmp/hi r1,r0
bt rl_val_table
mov.b @(0x5,r2),r0
tst r0,r0
bf rl_val_table
// Launch RPM above the minimum RPM and at most 32767; threshold nonzero;
// soft width below launch RPM minus the minimum RPM.
mov.w @(0x6,r2),r0
cmp/pz r0
bf rl_val_table
mov r0,r1
cmp/hi r6,r1
bf rl_val_table
mov.w @(0x8,r2),r0
tst r0,r0
bt rl_val_table
sub r6,r1
mov.w @(0xa,r2),r0
extu.w r0,r0
cmp/hs r1,r0
bt rl_val_table
add 0xc,r2
dt r5
bf rl_val_slot_next
mov #0x1,r7
rl_val_table:
mov.l @(rl_val_efficiency_address,pc),r2
mov.w @(rl_val_u_one,pc),r1
mov.w @r2+,r0
cmp/eq r1,r0
bf rl_val_return
mov #0x28,r5
rl_val_efficiency_next:
mov.w @r2+,r0
extu.w r0,r0
add -0x1,r0
cmp/hs r1,r0
bt rl_val_return
dt r5
bf rl_val_efficiency_next
add 0x2,r7
rl_val_return:
mov r7,r0
rts
nop

.align 4
rl_val_config_address:
.long 0x000D6320
rl_val_efficiency_address:
.long 0x000D6390
rl_val_u_one:
.word 1000
