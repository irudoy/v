// Vehicle-speed hold controller for exact JK08A Rolling Launch.
//
// The engine calls the controller on the activation pass and on every ACTIVE
// pass that passed all gates and the run timer, so the speed error lies inside
// the abort window. With e = speed - target in km/h*10, the controller forms
// u_p = clamp((W_top - e) * 1000 / W, 0, 1000) and steps the integrator by
// -(Ki * e), with the Ki of the slot of the activation map, unless the step
// deepens a saturated sum u_p + integrator / 16. The integrator stays within
// 16 * limit. The command clamp(u_p + integrator / 16, 0, 1000) moves u by at
// most the configured rate per pass. The trim unit at 0xD62B8 then stores the
// cut fraction and tail-jumps to the RPM ceiling unit at 0xD6068, which adds
// the hold flag, the ceiling latch, and the request.
// The stock unsigned divider at 0x21CE0 receives r0=divisor and r1=dividend
// and preserves r2 through r7.

.org 0x000D40C0
rolling_launch_speed_controller:
sts.l pr,@-r15
mov.l @(rl_spd_state_address,pc),r5
mov.l @(rl_spd_config_address,pc),r4
mov.l @(rl_spd_speed_address,pc),r1
mov.w @r1,r2
extu.w r2,r2
mov.w @(0xC,r5),r0
extu.w r0,r0
sub r0,r2
mov r2,r0
mov.w r0,@(0x10,r5)

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
mov r0,r1
shll r1
shll2 r0
add r1,r0
add r4,r0
add 0x28,r0
mov.w @r0,r0
muls.w r0,r2
sts macl,r1
neg r1,r1
mov.w @(0x12,r5),r0
mov r0,r7
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
mov.w @(rl_spd_u_one,pc),r3
cmp/ge r3,r0
bf rl_spd_accumulate
cmp/pl r1
bf rl_spd_accumulate
rl_spd_freeze:
mov #0x0,r1
rl_spd_accumulate:
add r1,r7
mov.w @(0x18,r4),r0
shll2 r0
shll2 r0
cmp/gt r0,r7
bf rl_spd_integrator_upper
mov r0,r7
rl_spd_integrator_upper:
neg r0,r0
cmp/ge r0,r7
bt rl_spd_integrator_lower
mov r0,r7
rl_spd_integrator_lower:
mov r7,r0
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

// Publish ACTIVE; the trim unit stores the cut fraction and the RPM ceiling
// unit adds hold, the latch, and the request.
mov.b @(0x2,r5),r0
or 0x10,r0
mov r0,r3
mov.l @(rl_spd_ceiling_entry,pc),r0
jsr @r0
nop
mov.l @(rl_spd_fuel_cut_status,pc),r2
mov.b @r2,r0
tst 0x04,r0
bt rl_spd_flags_store
mov #0x20,r7
or r7,r3
rl_spd_flags_store:
mov r3,r0
mov.b r0,@(0x2,r5)
lds.l @r15+,pr
rts
nop

.org 0x000D41C0
rl_spd_state_address:
.long 0xFFFF5D40
rl_spd_config_address:
.long 0x000D6220
rl_spd_speed_address:
.long 0xFFFF113C
rl_spd_unsigned_divide:
.long 0x00021CE0
rl_spd_ceiling_entry:
.long 0x000D62B8
rl_spd_fuel_cut_status:
.long 0xFFFF2497
rl_spd_u_one:
.word 1000
