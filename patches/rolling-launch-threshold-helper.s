// Adaptive threshold capture helper for exact JK08A Rolling Launch.
//
// The helper runs once when IDLE activates. It derives the effective native
// RPM hysteresis as clamp(round(captured_rpm * ratio / 100), min, max), where
// ratio is stored in tenths of one percent. It publishes Restore and the
// ignition-retard band start in dedicated state words. The effective retard
// ramp is max(configured minimum ramp, 2 * effective hysteresis), capped by
// the captured RPM offset. The stock unsigned divider receives r0=divisor and
// r1=dividend and preserves r2 through r7.

.org 0x000D4140
rolling_launch_threshold_helper:
sts.l pr,@-r15
mov.l @(rl_threshold_config_address,pc),r4
mov.l @(rl_threshold_state_address,pc),r5
mov.w @(0xA,r5),r0
mov r0,r2
extu.w r2,r2
mov r4,r1
add 0x1B,r1
mov.b @r1,r0
extu.b r0,r3
mulu.w r3,r2
sts macl,r1
mov.w @(rl_threshold_rounding,pc),r0
add r0,r1
mov.w @(rl_threshold_ratio_divisor,pc),r0
mov.l @(rl_threshold_unsigned_divide,pc),r3
jsr @r3
nop
mov r0,r2

// Clamp the proportional result to the configured native-RPM endpoints.
mov r4,r1
add 0x10,r1
mov.b @r1,r0
extu.b r0,r0
cmp/hs r0,r2
bt rl_threshold_min_ready
mov r0,r2
rl_threshold_min_ready:
mov.b @(0x1,r1),r0
extu.b r0,r0
cmp/hs r2,r0
bt rl_threshold_max_ready
mov r0,r2
rl_threshold_max_ready:

// Restore is Cut minus the effective hysteresis.
mov.w @(0xC,r5),r0
mov r0,r3
extu.w r3,r3
sub r2,r3
mov r3,r0
mov.w r0,@(0xE,r5)

// Widen the retard ramp with hysteresis, while remaining inside RPM offset.
shll r2
mov.b @(0x9,r4),r0
extu.b r0,r1
cmp/hs r1,r2
bt rl_threshold_ramp_min_ready
mov r1,r2
rl_threshold_ramp_min_ready:
mov.w @(0xE,r4),r0
extu.w r0,r1
cmp/hs r2,r1
bt rl_threshold_ramp_max_ready
mov r1,r2
rl_threshold_ramp_max_ready:

// Band start never precedes the captured activation RPM.
mov.w @(0xC,r5),r0
mov r0,r3
extu.w r3,r3
sub r2,r3
mov.w @(0xA,r5),r0
extu.w r0,r1
cmp/hs r1,r3
bt rl_threshold_start_ready
mov r1,r3
rl_threshold_start_ready:
mov r3,r0
mov.w r0,@(0x12,r5)
lds.l @r15+,pr
rts
nop

.org 0x000D41C0
rl_threshold_config_address:
.long 0x000D3F60
rl_threshold_state_address:
.long 0xFFFF5D40
rl_threshold_unsigned_divide:
.long 0x00021CE0
rl_threshold_rounding:
.word 500
rl_threshold_ratio_divisor:
.word 1000
