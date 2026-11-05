// RPM regulator for exact JK08A Rolling Launch.
//
// The RPM controller at 0xD6400 receives r4=configuration and r5=base state
// on the activation pass and on every ACTIVE RPM pass that passed all gates
// and the run timer. It stores err = rpm - target_rpm in base +0x18 and
// extension +0x02 and the firing permission p of the slot of the activation
// map in extension +0x16, and then ends in the control publisher at 0xD6500
// with r4 and r5 unchanged.
//
// The pure fraction at 0xD6480 receives r4=signed err and r5=soft width W
// and returns r0 = p: 0 for err >= 0, 1000 for W = 0 or err <= -W, else
// (-err * 1000) / W. It preserves r4, r5 and PR and changes r1, r2, MACL and
// T. The stock unsigned divider at 0x21CE0 receives r0=divisor and
// r1=dividend and preserves r2 through r7.

.org 0x000D6400
rolling_launch_rpm_controller:
sts.l pr,@-r15
mov.l @(rl_rpm_input_address,pc),r1
mov.w @r1,r0
extu.w r0,r6
mov.w @(0x14,r5),r0
extu.w r0,r0
sub r0,r6
mov r6,r0
mov.w r0,@(0x18,r5)
mov.l @(rl_rpm_extension_address,pc),r7
mov.w r0,@(0x2,r7)
mov.b @(0x4,r5),r0
extu.b r0,r0
shll2 r0
mov r0,r1
shll r1
add r0,r1
add r4,r1
add 0x28,r1
mov.w @(0xa,r1),r0
mov.l r4,@-r15
mov.l r5,@-r15
extu.w r0,r5
mov r6,r4
bsr rolling_launch_rpm_fraction
nop
mov.l @r15+,r5
mov.l @r15+,r4
mov.w r0,@(0x16,r7)
lds.l @r15+,pr
mov.l @(rl_rpm_control_publisher,pc),r0
jmp @r0
nop

.align 4
rl_rpm_input_address:
.long 0xFFFF11BC
rl_rpm_extension_address:
.long 0xFFFF6100
rl_rpm_control_publisher:
.long 0x000D6500

.org 0x000D6480
rolling_launch_rpm_fraction:
mov #0x0,r0
cmp/pz r4
bt rl_rpm_fraction_return
mov.w @(rl_rpm_u_one,pc),r0
tst r5,r5
bt rl_rpm_fraction_return
mov r4,r1
add r5,r1
cmp/pl r1
bf rl_rpm_fraction_return
sts.l pr,@-r15
mov r4,r1
neg r1,r1
mulu.w r0,r1
sts macl,r1
mov r5,r0
mov.l @(rl_rpm_unsigned_divide,pc),r2
jsr @r2
nop
lds.l @r15+,pr
rl_rpm_fraction_return:
rts
nop

.align 4
rl_rpm_unsigned_divide:
.long 0x00021CE0
rl_rpm_u_one:
.word 1000
