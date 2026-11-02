// RPM ceiling latch for exact JK08A Rolling Launch.
//
// The speed controller calls this unit on every pass that runs the controller,
// with r3 holding the high flag byte, r4 the configuration record, and r5 the
// state record. Observe mode releases the latch and publishes no request. Hold
// mode sets the hold flag, latches when native RPM exceeds the captured RPM
// plus the ceiling offset, keeps the latch while RPM exceeds that sum minus the
// hysteresis, and releases it at or below. While latched it publishes the
// all-cylinder request 0x003F and the ceiling and fuel-cut flags. The sums are
// formed in 32 bits, so a high captured RPM never wraps below a threshold. The
// unit changes only r0, r1, r2, r7, T, the flags in r3, the request, and the
// latch.

.org 0x000D6068
rolling_launch_rpm_ceiling:
mov.b @(0x5,r5),r0
cmp/eq 0x1,r0
bf rl_ceil_release
mov #0x40,r7
or r7,r3
mov.w @(0xA,r5),r0
extu.w r0,r1
mov.w @(0x1C,r4),r0
extu.w r0,r0
add r0,r1
mov.l @(rl_ceil_rpm_address,pc),r2
mov.w @r2,r0
extu.w r0,r2
cmp/hi r1,r2
bt rl_ceil_latch
mov.w @(0x18,r5),r0
tst r0,r0
bt rl_ceil_release
mov r4,r7
add 0x23,r7
mov.b @r7,r0
extu.b r0,r0
sub r0,r1
cmp/hi r1,r2
bf rl_ceil_release
rl_ceil_latch:
mov #0x1,r0
mov.w r0,@(0x18,r5)
mov #0x3F,r0
mov.w r0,@(0x14,r5)
mov #-0x60,r7
or r7,r3
rts
nop
rl_ceil_release:
mov #0x0,r0
mov.w r0,@(0x18,r5)
rts
nop

.org 0x000D60B4
rl_ceil_rpm_address:
.long 0xFFFF11BC
