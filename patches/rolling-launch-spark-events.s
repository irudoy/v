// Dwell actuator reset, HOLD latch and off-HOLD event service.
// r5 is the state base and r4 its quiet byte. r6 selects HOLD (0),
// first/reset (phase plus one), or IDLE latch service (-1).
// r2 returns one only for HOLD.
// Reset publication and latch check/store are masked; other SR bits survive.
// Every entry preserves PR. The reset entry at 0xD6274 is also called by
// the HOLD q/accumulator checks and leaves its cache invalid.

.org 0x000D6268
rolling_launch_spark_events:
tst r6,r6
bt rl_event_hold
cmp/pz r6
bf rl_event_latch
bra rolling_launch_spark_reset
nop

rolling_launch_spark_reset:
stc sr,r7
mov r7,r0
or 0xf0,r0
ldc r0,sr
mov.w @(rl_event_offset_1,pc),r0
mov.w r0,@(0x4,r4)
mov.w @(rl_event_offset_2,pc),r0
mov.w r0,@(0x6,r4)
mov.w @(rl_event_offset_3,pc),r0
mov.w r0,@(0x8,r4)
mov.w @(rl_event_offset_4,pc),r0
mov.w r0,@(0xa,r4)
mov.w @(rl_event_offset_5,pc),r0
mov.w r0,@(0xc,r4)
mov.w @(rl_event_offset_6,pc),r0
mov.w r0,@(0xe,r4)
mov r6,r0
mov #0x3,r2
cmp/hi r2,r0
bf rl_event_cache_store
mov #0x0,r0
rl_event_cache_store:
mov.b r0,@(0x3,r4)
ldc r7,sr
tst r6,r6
bf rl_event_quiet
rl_event_return:
rts
nop

rl_event_hold:
mov #0x0,r0
mov.b r0,@r4
mov.b r0,@(0x3,r4)
mov #0x1,r2
mov.l @(rl_event_misfire_latch_address,pc),r3
stc sr,r7
mov r7,r0
or 0xf0,r0
ldc r0,sr
mov.b @r3,r0
tst r0,r0
bf rl_event_hold_done
mov #0x1,r0
mov.b r0,@r3
rl_event_hold_done:
ldc r7,sr
rts
nop

rl_event_quiet:
mov.b @r5,r0
cmp/eq 0x1,r0
bf rl_event_quiet_increment
mov #0x0,r0
mov.b r0,@r4
bra rl_event_latch
nop
rl_event_quiet_increment:
mov.b @r4,r0
cmp/eq -0x1,r0
bt rl_event_latch
add 0x1,r0
mov.b r0,@r4
rl_event_latch:
mov #0x0,r2
mov.b @r5,r0
tst r0,r0
bf rl_event_return_lite
mov.b @r4,r0
extu.b r0,r0
mov #0xd,r3
cmp/hi r3,r0
bf rl_event_return_lite
mov.l @(rl_event_misfire_latch_address,pc),r3
stc sr,r7
mov r7,r0
or 0xf0,r0
ldc r0,sr
mov.b @r3,r0
cmp/eq 0x1,r0
bf rl_event_latch_done
mov #0x0,r0
mov.b r0,@r3
rl_event_latch_done:
ldc r7,sr
rl_event_return_lite:
rts
nop

.align 4
rl_event_misfire_latch_address:
.long 0xFFFF436F
rl_event_offset_1:
.word 250
rl_event_offset_2:
.word 2250
rl_event_offset_3:
.word 4250
rl_event_offset_4:
.word 1250
rl_event_offset_5:
.word 3250
rl_event_offset_6:
.word 5250
