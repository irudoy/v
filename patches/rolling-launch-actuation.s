// Actuation publishers for exact JK08A Rolling Launch.
//
// The control publisher at 0xD6500 runs after every controller step with
// r4=configuration, r5=base state and r3=law output u. With interrupts
// masked from its first store through the commit of the body, it stores u
// as the law output at extension +0x16 and, in SPEED, as the torque fraction
// at base +0x0E, takes the stored command tuple, and takes ready only in
// ACTIVE hold, and publishes e = E[a] and q for u.
//
// The ignition publisher at 0xD6540 runs from the crank-tooth interrupt with
// r4=wide stock command S and r5=wide effective command P from the ignition
// adapter, and returns in r5 the command to apply. A record that fails the
// structural check, a base record without CONFIG_VALID, or an applied trim
// a = P - S outside 0..40, or above the latched trim while ready, publishes
// the stock command and returns r5 = S: P = S, a = 0, e = 1000, ready = 0
// and q = 0. Only an engine pass with a valid configuration and efficiency
// table sets CONFIG_VALID, and every ACTIVE record comes from such a pass.
// Otherwise it returns r5 = P and publishes ready = ACTIVE hold without the
// APC fallback 0xFFFF24C9 bit 6.
//
// The common body at 0xD6580 receives r1=a, r2=ready, r6=(S<<8)|P and the SR
// of the caller on the stack. It computes e = 1000 for a = 0 and E[a]
// otherwise, q = 0 without ready, 1000 - law in RPM and
// 1000 - min(1000, 1000 * law / e) in SPEED, and the wire views through the
// views routine of the record check. It stores S, P, a, ready, e and the
// views with interrupts masked and q last, and returns with the SR of the
// caller.
//
// Both publishers preserve r4, r8..r15 and PR, and the control publisher
// preserves r5; r0..r3, r6, r7, MACL and T are caller-clobbered. The stock
// unsigned divider at 0x21CE0 receives r0=divisor and r1=dividend and
// preserves r2 through r7.

.org 0x000D6500
rolling_launch_control_publisher:
stc sr,r0
mov.l r0,@-r15
or 0xf0,r0
ldc r0,sr
mov.l @(rl_act_extension_address,pc),r7
mov r3,r0
mov.w r0,@(0x16,r7)
mov.b @r7,r0
cmp/eq 0x2,r0
bf rl_act_control_tuple
mov r3,r0
mov.w r0,@(0xe,r5)
rl_act_control_tuple:
mov.w @(0x8,r7),r0
extu.w r0,r6
mov.b @(0xa,r7),r0
extu.b r0,r1
mov.b @(0xb,r7),r0
extu.b r0,r2
mov.b @r5,r0
cmp/eq 0x1,r0
bf rl_act_control_idle
mov.b @(0x5,r5),r0
cmp/eq 0x1,r0
bt rl_act_control_publish
rl_act_control_idle:
mov #0x0,r2
rl_act_control_publish:
bra rolling_launch_actuation
nop

.org 0x000D6540
rolling_launch_ignition_publisher:
stc sr,r0
mov.l r0,@-r15
sts.l pr,@-r15
mov.l @(rl_act_state_check,pc),r0
jsr @r0
nop
lds.l @r15+,pr
bf rl_act_ignition_stock
mov.l @(rl_act_state_address,pc),r3
mov.w @(0x2,r3),r0
tst 0x1,r0
bt rl_act_ignition_stock
extu.b r4,r6
extu.b r5,r1
sub r6,r1
mov #0x28,r0
cmp/hi r0,r1
bt rl_act_ignition_stock
mov #0x0,r2
mov.b @r3,r0
cmp/eq 0x1,r0
bf rl_act_ignition_publish
bra rl_act_ignition_ready
nop

.org 0x000D6580
rolling_launch_actuation:
mov.l r4,@-r15
mov.l r5,@-r15
sts.l pr,@-r15
mov.l @(rl_act_extension_address,pc),r7
mov.w @(rl_act_u_one,pc),r3
tst r1,r1
bt rl_act_efficiency_ready
mov r1,r0
shll r0
mov.l @(rl_act_efficiency_address,pc),r3
mov.w @(r0,r3),r3
extu.w r3,r3
rl_act_efficiency_ready:
mov #0x0,r5
tst r2,r2
bt rl_act_commit
mov.l r1,@-r15
mov.l r2,@-r15
mov.b @r7,r0
mov r0,r1
mov.w @(0x16,r7),r0
mov r0,r2
bsr rolling_launch_q
nop
mov r0,r5
mov.l @r15+,r2
mov.l @r15+,r1
rl_act_commit:
shll16 r6
mov r1,r0
shll8 r0
or r2,r0
or r0,r6
mov.l @(rl_act_views,pc),r0
jsr @r0
nop
mov.l @(rl_act_state_address,pc),r4
stc sr,r0
or 0xf0,r0
ldc r0,sr
mov.l r6,@(0x8,r7)
mov.l r3,@(0xc,r7)
mov r1,r0
mov.w r0,@(0x1e,r7)
mov r5,r0
mov.w r0,@(0x1a,r4)
lds.l @r15+,pr
mov.l @r15+,r5
mov.l @r15+,r4
mov.l @r15+,r0
ldc r0,sr
rts
nop

// Ignition publisher, continued: ready in ACTIVE hold without the APC
// fallback, and then an applied trim within the latched trim.
rl_act_ignition_ready:
mov.b @(0x5,r3),r0
cmp/eq 0x1,r0
bf rl_act_ignition_publish
mov.l @(rl_act_apc_mode_address,pc),r0
mov.b @r0,r0
tst 0x40,r0
bf rl_act_ignition_publish
mov #0x1e,r0
mov.b @(r0,r3),r0
cmp/hs r1,r0
bf rl_act_ignition_stock
mov #0x1,r2
rl_act_ignition_publish:
shll8 r6
extu.b r5,r0
or r0,r6
bra rolling_launch_actuation
nop
rl_act_ignition_stock:
mov r4,r5
extu.b r4,r6
mov r6,r0
shll8 r6
or r0,r6
mov #0x0,r1
mov #0x0,r2
bra rolling_launch_actuation
nop

// q for r1=kind, r2=law and r3=e of a ready hold. Changes r0..r2, MACL and T.
rolling_launch_q:
mov r1,r0
cmp/eq 0x1,r0
bt rl_q_rpm
sts.l pr,@-r15
mov.w @(rl_act_u_one,pc),r1
mulu.w r1,r2
sts macl,r1
mov r3,r0
mov.l @(rl_act_unsigned_divide,pc),r2
jsr @r2
nop
lds.l @r15+,pr
mov.w @(rl_act_u_one,pc),r1
cmp/hi r1,r0
bf rl_q_limited
mov r1,r0
rl_q_limited:
neg r0,r0
add r1,r0
rts
nop
rl_q_rpm:
mov.w @(rl_act_u_one,pc),r0
sub r2,r0
rts
nop

.align 4
rl_act_extension_address:
.long 0xFFFF6100
rl_act_state_address:
.long 0xFFFF5D40
rl_act_efficiency_address:
.long 0x000D6390
rl_act_unsigned_divide:
.long 0x00021CE0
rl_act_state_check:
.long 0x000D7000
rl_act_views:
.long 0x000D7190
rl_act_apc_mode_address:
.long 0xFFFF24C9
rl_act_u_one:
.word 1000
