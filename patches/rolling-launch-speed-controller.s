// Vehicle-speed hold controller for exact JK08A Rolling Launch.
//
// The engine calls the controller with r4=configuration and r5=base state on
// the activation pass and on every ACTIVE SPEED pass that passed all gates
// and the run timer, so the speed error lies inside the abort window. With
// e = speed - target in km/h*10, the controller forms
// u_p = clamp((W_top - e) * 1000 / W, 0, 1000) and steps the integrator by
// -(Ki * e), with the Ki of the slot of the activation map, unless the step
// deepens a saturated sum u_p + integrator / 16. The integrator stays within
// 16 * limit. The command clamp(u_p + integrator / 16, 0, 1000) moves u by at
// most the configured rate per pass. The controller stores e in base +0x10
// and extension +0x02, the integrator, the command and u in base +0x12,
// +0x16 and +0x0E, and u as the law output in extension +0x16, and then ends
// in the control publisher at 0xD6500 with r4 and r5 unchanged.
// The stock unsigned divider at 0x21CE0 receives r0=divisor and r1=dividend
// and preserves r2 through r7.

.org 0x000D40C0
rolling_launch_speed_controller:
sts.l pr,@-r15
mov.l @(rl_spd_speed_address,pc),r1
mov.w @r1,r2
extu.w r2,r2
mov.w @(0xC,r5),r0
extu.w r0,r0
sub r0,r2
mov r2,r0
mov.w r0,@(0x10,r5)
mov.l @(rl_spd_extension_address,pc),r7
mov.w r0,@(0x2,r7)

// Windowed proportional fraction.
mov r4,r1
add 0x12,r1
mov.b @r1,r0
extu.b r0,r3
mov.b @(0x1,r1),r0
extu.b r0,r0
sub r2,r0
mov #0x0,r6
cmp/pl r0
bf rl_spd_integrator
mov.w @(rl_spd_u_one,pc),r6
cmp/hs r3,r0
bt rl_spd_integrator
mov r6,r1
mulu.w r0,r1
sts macl,r1
mov r3,r0
mov.l @(rl_spd_unsigned_divide,pc),r3
jsr @r3
nop
mov r0,r6

// Integrator step at the Ki of the map slot, frozen while it deepens a
// saturated sum.
rl_spd_integrator:
mov.b @(0x4,r5),r0
extu.b r0,r0
shll2 r0
mov r0,r1
shll r1
add r1,r0
add r4,r0
add 0x28,r0
mov.w @r0,r0
muls.w r0,r2
sts macl,r1
neg r1,r1
mov.w @(0x12,r5),r0
mov r0,r3
shar r0
shar r0
shar r0
shar r0
add r6,r0
cmp/pl r0
bt rl_spd_sum_positive
cmp/pz r1
bt rl_spd_accumulate
bra rl_spd_freeze
nop
rl_spd_sum_positive:
mov.w @(rl_spd_u_one,pc),r2
cmp/ge r2,r0
bf rl_spd_accumulate
cmp/pl r1
bf rl_spd_accumulate
rl_spd_freeze:
mov #0x0,r1
rl_spd_accumulate:
add r1,r3
mov.w @(0x18,r4),r0
shll2 r0
shll2 r0
cmp/gt r0,r3
bf rl_spd_integrator_upper
mov r0,r3
rl_spd_integrator_upper:
neg r0,r0
cmp/ge r0,r3
bt rl_spd_integrator_lower
mov r0,r3
rl_spd_integrator_lower:
mov r3,r0
mov.w r0,@(0x12,r5)

// Command before the rate limit.
shar r0
shar r0
shar r0
shar r0
add r6,r0
cmp/pz r0
bt rl_spd_command_nonnegative
mov #0x0,r0
rl_spd_command_nonnegative:
mov.w @(rl_spd_u_one,pc),r1
cmp/gt r1,r0
bf rl_spd_command_ready
mov r1,r0
rl_spd_command_ready:
mov.w r0,@(0x16,r5)
mov r0,r2

// Move u toward the command by at most the configured rate.
mov.w @(0x14,r4),r0
mov r0,r3
mov.w @(0xE,r5),r0
mov r0,r1
add r3,r0
cmp/gt r0,r2
bf rl_spd_rate_upper
mov r0,r2
rl_spd_rate_upper:
sub r3,r1
cmp/ge r1,r2
bt rl_spd_rate_lower
mov r1,r2
rl_spd_rate_lower:
mov r2,r0
mov.w r0,@(0xE,r5)
mov.w r0,@(0x16,r7)
lds.l @r15+,pr
mov.l @(rl_spd_control_publisher,pc),r0
jmp @r0
nop

.align 4
rl_spd_speed_address:
.long 0xFFFF113C
rl_spd_extension_address:
.long 0xFFFF6100
rl_spd_unsigned_divide:
.long 0x00021CE0
rl_spd_control_publisher:
.long 0x000D6500
rl_spd_u_one:
.word 1000
