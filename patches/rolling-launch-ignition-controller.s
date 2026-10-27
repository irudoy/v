// RPM-band ignition controller for exact JK08A Rolling Launch.
//
// Input r4 is the stock uint8 command and r2 is the validated per-map late
// command cap, with r4 < r2. The controller reads the lower ramp boundary
// captured by the adaptive-threshold helper. It leaves the stock command
// unchanged at or below that boundary, linearly blends toward the cap inside
// the band, and applies the cap at or above Cut. The comparisons that reach
// the blend require a strict interior RPM, so the unsigned difference
// Cut - band is at least 2. The exact stock unsigned divider at 0x21CE0
// receives r0=divisor and r1=dividend and is called without a zero test.
// It preserves r2/r3; this wrapper saves and restores the incoming PR
// around the call.

.org 0x000D40C0
rolling_launch_ignition_controller:
sts.l pr,@-r15
sub r4,r2
mov.l @(rl_ctrl_state_address,pc),r1
mov.w @(0xC,r1),r0
extu.w r0,r3
mov.l r3,@-r15
mov.w @(0x12,r1),r0
extu.w r0,r3
tst r3,r3
bt rl_ctrl_tail
mov.l @(rl_ctrl_rpm_address,pc),r1
mov.w @r1,r0
extu.w r0,r1
cmp/hi r3,r1
bf rl_ctrl_tail
mov.l @r15,r0
cmp/hs r0,r1
bt rl_ctrl_full
sub r3,r1
sub r3,r0
mulu.w r2,r1
sts macl,r1
mov.l @(rl_ctrl_unsigned_divide,pc),r3
jsr @r3
nop
add r0,r4
bra rl_ctrl_store
nop
rl_ctrl_full:
add r2,r4
rl_ctrl_store:
mov.l @(rl_ctrl_output_address,pc),r1
mov r4,r0
mov.b r0,@r1
mov.l @(rl_ctrl_state_address,pc),r1
add 0x11,r1
mov.b r0,@r1
rl_ctrl_tail:
mov.l @r15+,r0
lds.l @r15+,pr
mov.l @(rl_ctrl_stock_consumer,pc),r0
jmp @r0
nop

.org 0x000D4124
rl_ctrl_state_address:
.long 0xFFFF5D40
rl_ctrl_rpm_address:
.long 0xFFFF11BC
rl_ctrl_unsigned_divide:
.long 0x00021CE0
rl_ctrl_output_address:
.long 0xFFFF2022
rl_ctrl_stock_consumer:
.long 0x0002A892
