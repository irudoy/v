// Armed-event quiet and misfire-latch service for the dwell veto.
// Input r5 is the base state. Output r4 points to its quiet-event byte and
// r2 is one exactly for ACTIVE HOLD. The helper changes r0..r4, r7 and T,
// preserves r5, r6, r8..r15 and PR, and preserves the interrupt mask.
// The latch read/modify/write is masked at level 15.

.org 0x000D6780
rolling_launch_spark_events:
mov r5,r4
add 0x1c,r4
mov.b @r5,r0
mov r0,r1
mov #0x0,r2
cmp/eq 0x1,r0
bf rl_cut_quiet_count
mov #0x0,r0
mov.b r0,@r4
mov.b @(0x5,r5),r0
cmp/eq 0x1,r0
bf rl_cut_latch
mov #0x1,r2
bra rl_cut_latch
nop
rl_cut_quiet_count:
mov.b @r4,r0
cmp/eq -0x1,r0
bt rl_cut_latch
add 0x1,r0
mov.b r0,@r4
rl_cut_latch:
mov.l @(rl_cut_misfire_latch_address,pc),r3
stc sr,r7
mov r7,r0
or 0xf0,r0
ldc r0,sr
mov.b @r3,r0
tst r2,r2
bt rl_cut_latch_release
tst r0,r0
bf rl_cut_latch_done
mov #0x1,r0
mov.b r0,@r3
bra rl_cut_latch_done
nop
rl_cut_latch_release:
cmp/eq 0x1,r0
bf rl_cut_latch_done
tst r1,r1
bf rl_cut_latch_done
mov.b @r4,r0
extu.b r0,r0
mov #0xd,r1
cmp/hi r1,r0
bf rl_cut_latch_done
mov #0x0,r0
mov.b r0,@r3
rl_cut_latch_done:
ldc r7,sr
rts
nop
.align 4
rl_cut_misfire_latch_address:
.long 0xFFFF436F
