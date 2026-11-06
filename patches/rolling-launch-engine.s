// Fail-closed schema 6 Rolling Launch state machine for exact JK08A.
//
// The engine runs once per exact periodic scheduler pass, 204800/Pphi seconds.
// It keeps the base state at 0xFFFF5D40 in r8, the extension at 0xFFFF6100
// in r9 and the configuration at 0xD6320 in r10 and restores r8..r14 and PR.
// The scheduler runs it with interrupts enabled, so the ignition publisher
// of the crank-tooth interrupt can run between any two instructions outside
// a masked section.
// The pass order follows the schema 6 model:
//   1. The record check at 0xD7008 runs with interrupts masked. A record
//      that the model does not decode as a valid state restores map 1
//      through the limiter commit, clears base 0x00..0x1B, the trim and
//      trim/reset-cache word at 0x1E/0x1F and the extension, and enters COOLDOWN
//      with reason 16. The quiet and cut counters at base 0x1C/0x1D and the
//      six accumulators remain.
//   2. The input sample stores the RPM and speed words, the CANCEL capture,
//      the accepted button and the frame age, and input_status:
//      bit0 raw speed word 0xFFFF3B3D/3E is not FFFF, bit1 frame age within
//      the limit of a valid configuration, bit2 HCAN1 initialized and PL4
//      ready, bit3 RPM at most 32767, bit4 CANCEL capture valid.
//   3. COOLDOWN rearms on a released button. IDLE and ACTIVE publish every
//      satisfied gate and the first failure by priority. IDLE activates RPM
//      below the map speed threshold and SPEED at or above it; a SPEED
//      target below the threshold clears input_status bit4 before the gates.
//      ACTIVE keeps the latched regulator, map, mode and trim.
//   4. Every pass ends with the wire views of the extension, read, computed
//      and stored with interrupts masked.
// The validator at 0xD6680 returns 0 for an invalid configuration, and for a
// valid one bit0 and bit1 for a valid efficiency table; r12 keeps the result,
// which is positive exactly for a valid configuration. The RPM controller at
// 0xD6400 and the speed controller at 0xD40C0 receive r4=configuration and
// r5=base state and end in the control publisher, which commits their law
// output together with q.

.org 0x000D38E4
rolling_launch_engine:
sts.l pr,@-r15
mov.l r8,@-r15
mov.l r9,@-r15
mov.l r10,@-r15
mov.l r11,@-r15
mov.l r12,@-r15
mov.l r13,@-r15
mov.l r14,@-r15
mov.l @(rl_state_address,pc),r8
mov.l @(rl_extension_address,pc),r9
mov.l @(rl_config_address,pc),r10
mov.l @(rl_state_check_entry,pc),r0
jsr @r0
nop
bt rl_state_valid
bra rl_corrupt_state
nop
rl_state_valid:
bsr rl_validate_config
nop
mov r0,r12

// Input sample: r4 = speed word, r3 = button, r7 = frame age, r6 = status.
mov.l @(rl_speed_address,pc),r1
mov.w @r1,r0
mov.w r0,@(0x6,r9)
extu.w r0,r4
mov.l @(rl_rpm_address,pc),r1
mov.w @r1,r0
mov.w r0,@(0x4,r9)
mov #0x0,r6
cmp/pz r0
bf rl_sample_raw
mov #0x8,r6
rl_sample_raw:
// The raw word is unaligned; both bytes FF mark an invalid speed.
mov.l @(rl_speed_raw_address,pc),r1
mov.b @r1+,r0
mov.b @r1,r2
and r2,r0
cmp/eq -0x1,r0
bt rl_sample_age
add 0x1,r6
rl_sample_age:
mov.l @(rl_speed_age_address,pc),r1
mov.b @r1,r0
extu.b r0,r7
mov r12,r0
tst 0x1,r0
bt rl_sample_source
mov #0x22,r0
mov.b @(r0,r10),r0
extu.b r0,r0
cmp/hs r7,r0
bf rl_sample_source
add 0x2,r6
rl_sample_source:
mov.l @(rl_hcan_address,pc),r1
mov.b @r1,r0
tst 0x1,r0
bt rl_sample_button
mov.l @(rl_port_address,pc),r1
mov.b @r1,r0
tst 0x80,r0
bt rl_sample_button
add 0x4,r6
rl_sample_button:
// An accepted CANCEL edge in IDLE captures a usable speed once; any other
// button code clears the capture.
mov.l @(rl_button_address,pc),r1
mov.b @r1,r0
extu.b r0,r3
cmp/eq 0x2,r0
bf rl_sample_no_capture
mov.b @r8,r0
tst r0,r0
bf rl_sample_keep_capture
mov #0x14,r0
mov.b @(r0,r9),r0
cmp/eq 0x2,r0
bt rl_sample_keep_capture
mov r6,r0
and 0x7,r0
cmp/eq 0x7,r0
bf rl_sample_no_capture
add 0x10,r6
mov r4,r0
bra rl_sample_store
nop
rl_sample_keep_capture:
mov.b @(0x1,r9),r0
and 0x10,r0
or r0,r6
mov.w @(0x1a,r9),r0
bra rl_sample_store
nop
rl_sample_no_capture:
mov #0x0,r0
rl_sample_store:
mov.w r0,@(0x1a,r9)
mov r6,r0
mov.b r0,@(0x1,r9)
mov r3,r0
shll8 r0
or r7,r0
mov.w r0,@(0x14,r9)

mov.b @r8,r0
cmp/eq 0x2,r0
bf rl_gate_inputs

// COOLDOWN rearms only with a valid configuration and table and a released
// button.
mov r12,r0
cmp/eq 0x3,r0
bt rl_cooldown_valid
mov #0x1,r0
mov.b r0,@(0x1,r8)
mov #0x0,r0
mov.w r0,@(0x2,r8)
bra rl_cooldown_store_rearm
nop
rl_cooldown_valid:
mov r3,r0
cmp/eq 0x20,r0
mov #0x0,r0
bf rl_cooldown_store_rearm
mov.w @(0x8,r8),r0
add 0x1,r0
mov r0,r1
mov #0x20,r0
mov.w @(r0,r10),r0
cmp/hs r0,r1
mov r1,r0
bf rl_cooldown_store_rearm
mov #0x0,r0
mov.b r0,@r8
mov.w r0,@(0x2,r8)
mov.b r0,@(0x5,r8)
mov.w r0,@(0x6,r8)
mov.b r0,@r9
mov #0x0,r2
mov #0x1e,r0
mov.b r2,@(r0,r8)
mov #0x0,r0
rl_cooldown_store_rearm:
mov.w r0,@(0x8,r8)
bra rl_engine_exit
nop

.align 4
rl_state_address:
.long 0xFFFF5D40
rl_extension_address:
.long 0xFFFF6100
rl_config_address:
.long 0x000D6320
rl_state_check_entry:
.long 0x000D7008
rl_speed_address:
.long 0xFFFF113C
rl_rpm_address:
.long 0xFFFF11BC
rl_speed_raw_address:
.long 0xFFFF3B3D
rl_speed_age_address:
.long 0xFFFF3B38
rl_hcan_address:
.long 0xFFFF4195
rl_port_address:
.long 0xFFFF4185
rl_button_address:
.long 0xFFFF2A85

// r5 = selector map index, r6 = speed target, r14 = regulator kind. IDLE
// derives the kind from the map threshold and the target from the CANCEL
// capture plus the offset; ACTIVE keeps both.
rl_gate_inputs:
mov.l @(rl_gate_selector_address,pc),r1
mov.b @r1,r0
extu.b r0,r5
mov.b @r8,r0
tst r0,r0
bf rl_active_kind
mov #0x0,r14
mov #0x0,r6
mov r12,r0
tst 0x1,r0
bt rl_kind_ready
mov.w @(0x1a,r9),r0
extu.w r0,r6
mov.w @(0x10,r10),r0
add r0,r6
cmp/pz r6
bt rl_target_not_negative
mov #0x0,r6
rl_target_not_negative:
mov #-0x1,r0
extu.w r0,r0
cmp/hi r0,r6
bf rl_target_ready
mov r0,r6
rl_target_ready:
mov #0x4,r0
cmp/hi r0,r5
bt rl_kind_ready
// The speed threshold of map r5 is the configuration word 0x30 + 12 * r5.
mov #0xc,r0
mulu.w r5,r0
sts macl,r0
add 0x30,r0
mov.w @(r0,r10),r0
extu.w r0,r0
mov #0x1,r14
cmp/hs r0,r4
bf rl_kind_ready
mov #0x2,r14
// SPEED with a target below the threshold clears the capture bit, so gate
// 11 refuses either kind until a new press captures again.
cmp/hs r0,r6
bt rl_kind_ready
mov.b @(0x1,r9),r0
and 0xef,r0
mov.b r0,@(0x1,r9)
bra rl_kind_ready
nop
rl_active_kind:
mov.b @r9,r0
extu.b r0,r14
mov.w @(0xc,r8),r0
extu.w r0,r6
rl_kind_ready:

// Gates in model priority. r11 = flags, r13 = first failure.
mov #0x0,r11
mov #0x0,r13
mov r12,r0
tst 0x1,r0
mov #0x1,r1
mov #0x1,r2
bsr rl_gate_fail_t
nop
mov #0x4,r0
cmp/hi r0,r5
mov #0x0,r1
mov #0x2,r2
bsr rl_gate_fail_t
nop
mov.b @(0x4,r10),r0
mov r5,r1
mov #0x4,r2
cmp/hi r2,r1
bt rl_gate_map_call
tst r1,r1
bt rl_gate_map_bit
rl_gate_map_shift:
shlr r0
dt r1
bf rl_gate_map_shift
rl_gate_map_bit:
tst 0x1,r0
rl_gate_map_call:
mov #0x2,r1
mov #0x3,r2
bsr rl_gate_valid_fail_t
nop
mov.l @(rl_gate_selector_address,pc),r7
mov.b @(0x1,r7),r0
mov r0,r2
mov.b @(0x2,r7),r0
or r0,r2
mov.b @(0x3,r7),r0
or r0,r2
tst r2,r2
mov #0x4,r1
mov #0x4,r2
bsr rl_gate_pass_t
nop
mov.l @(0x4,r7),r0
tst r0,r0
mov #0x8,r1
mov #0x5,r2
bsr rl_gate_pass_t
nop
mov.l @(rl_ascd_address,pc),r1
mov.b @r1,r0
tst 0x80,r0
mov #0x10,r1
mov #0x6,r2
bsr rl_gate_pass_t
nop
mov r3,r0
cmp/eq 0x2,r0
mov #0x20,r1
mov #0x8,r2
bsr rl_gate_pass_t
nop
// Speed source ready, speed value, frame age and CANCEL capture come from
// the sampled input_status, which the gate helper leaves in r0.
mov.b @(0x1,r9),r0
tst 0x4,r0
mov #0x0,r1
mov #0x17,r2
bsr rl_gate_fail_t
nop
tst 0x1,r0
mov #0x16,r2
bsr rl_gate_fail_t
nop
tst 0x2,r0
mov #0xd,r2
bsr rl_gate_fail_t
nop
tst 0x10,r0
mov #0x19,r2
bsr rl_gate_fail_t
nop
and 0x7,r0
cmp/eq 0x7,r0
bf rl_gate_speed
mov #0x4,r1
shll8 r1
or r1,r11

// RPM regulation needs no speed range; IDLE checks the activation range and
// ACTIVE SPEED the error window.
rl_gate_speed:
mov r14,r0
cmp/eq 0x1,r0
bf rl_gate_speed_value
mov #0x40,r1
or r1,r11
bra rl_gate_rpm
nop
rl_gate_speed_value:
mov.b @r8,r0
cmp/eq 0x1,r0
bf rl_gate_speed_range
bsr rl_window
nop
bra rl_gate_rpm
nop
rl_gate_speed_range:
mov.w @(0x8,r10),r0
extu.w r0,r0
tst r0,r0
bt rl_gate_speed_low
cmp/hs r0,r4
rl_gate_speed_low:
mov #0x40,r1
mov #0x9,r2
bsr rl_gate_valid_pass_t
nop
mov.w @(0xa,r10),r0
extu.w r0,r0
tst r0,r0
bt rl_gate_speed_high
cmp/hs r4,r0
bt rl_gate_speed_high
mov #-0x41,r1
and r1,r11
rl_gate_speed_high:
mov #0x0,r1
mov #0x13,r2
bsr rl_gate_valid_pass_t
nop

rl_gate_rpm:
mov.b @(0x1,r9),r0
tst 0x8,r0
mov #0x0,r1
mov #0x18,r2
bsr rl_gate_fail_t
nop
// SHLL changes T, so the flag bit precedes the comparison.
mov #0x40,r1
shll r1
mov.w @(0x4,r9),r0
mov r0,r7
mov.w @(0xc,r10),r0
cmp/ge r0,r7
mov #0xa,r2
bsr rl_gate_valid_pass_t
nop
mov.l @(rl_pedal_address,pc),r7
mov.w @r7,r0
extu.w r0,r7
mov.w @(0xe,r10),r0
extu.w r0,r0
cmp/hs r0,r7
mov #0x1,r1
shll8 r1
mov #0xb,r2
bsr rl_gate_valid_pass_t
nop
mov.l @(rl_coolant_address,pc),r7
mov.b @r7,r0
extu.b r0,r7
mov.b @(0x6,r10),r0
extu.b r0,r0
cmp/hs r0,r7
bf rl_gate_coolant
mov.b @(0x7,r10),r0
extu.b r0,r0
cmp/hs r7,r0
rl_gate_coolant:
mov #0x2,r1
shll8 r1
mov #0xc,r2
bsr rl_gate_valid_pass_t
nop
mov #0x8,r1
shll8 r1
mov #0x1,r2
bsr rl_gate_valid
nop
// An invalid efficiency table withdraws CONFIG_VALID and reports reason 1.
mov r12,r0
tst 0x2,r0
bf rl_gate_table_valid
mov #-0x2,r0
and r0,r11
mov #0x1,r13
rl_gate_table_valid:

mov.b @r8,r0
tst r0,r0
bf rl_active_post

// IDLE publishes the gates. A SPEED activation also needs the current error
// inside the abort window.
tst r13,r13
bf rl_idle_store
mov r14,r0
cmp/eq 0x2,r0
bf rl_idle_store
bsr rl_window
nop
rl_idle_store:
mov r11,r0
mov.w r0,@(0x2,r8)
mov r13,r0
mov.b r0,@(0x1,r8)
tst r0,r0
bt rl_activate
bra rl_engine_exit
nop

// Activation latches the map, mode, kind, captured RPM, target and the trim
// of the kind. The controller starts with zero errors and integrator, q = 0,
// ready = 0 and, in SPEED, full torque. The law output 1000 gives q = 0 for
// both kinds and precedes the kind. A first publication inside activation
// fails the check and publishes S: the status view keeps kind NONE of the
// IDLE record. After the kind store it stores the view of the new kind, so a
// second publication after the trim store passes the check once the control
// error equals the cleared regulator error, and publishes ready P with the
// law output 1000 and q = 0.
rl_activate:
mov #0xc,r0
mulu.w r5,r0
sts macl,r1
add r10,r1
add 0x28,r1
mov #0x1,r0
mov.b r0,@r8
mov r5,r0
mov.b r0,@(0x4,r8)
mov.b @(0x3,r10),r0
mov.b r0,@(0x5,r8)
mov #0x7d,r0
shll2 r0
shll r0
mov.w r0,@(0x16,r9)
mov r14,r0
mov.b r0,@r9
mov.w @(0x4,r9),r0
mov.w r0,@(0xa,r8)
mov #0x0,r0
mov.w r0,@(0x6,r8)
mov.w r0,@(0x8,r8)
mov.l r0,@(0x10,r8)
mov.w r0,@(0x16,r8)
mov.l r0,@(0x18,r8)
mov.b r0,@(0xb,r9)
mov r14,r0
cmp/eq 0x1,r0
bf rl_activate_speed
mov.w @(0x6,r1),r0
mov.w r0,@(0x14,r8)
mov.w r0,@(0x1c,r9)
mov #0x0,r0
mov.l r0,@(0xc,r8)
mov.b @(0x2,r1),r0
bra rl_activate_trim
nop
rl_activate_speed:
mov r6,r0
mov.w r0,@(0xc,r8)
mov.w r0,@(0x1c,r9)
mov.w @(0x16,r9),r0
mov.w r0,@(0xe,r8)
mov #0x0,r0
mov.w r0,@(0x14,r8)
mov.b @(0x3,r1),r0
rl_activate_trim:
mov r0,r2
mov #0x1e,r0
mov.b r2,@(r0,r8)
bra rl_publish_active
nop

// ACTIVE: a map or mode change has priority over the gate reasons. SET
// requests a map and RELEASED ends the hold.
rl_active_post:
mov.b @(0x4,r8),r0
extu.b r0,r0
cmp/eq r5,r0
mov #0x11,r2
bf rl_abort
mov.b @(0x3,r10),r0
mov r0,r1
mov.b @(0x5,r8),r0
cmp/eq r1,r0
mov #0x12,r2
bf rl_abort
mov r13,r2
tst r13,r13
bt rl_active_timer
mov r3,r0
cmp/eq 0x8,r0
bf rl_active_release
mov #0xf,r2
rl_active_release:
cmp/eq 0x20,r0
bf rl_abort
mov #0x7,r2
bra rl_abort
nop
rl_active_timer:
mov.w @(0x6,r8),r0
add 0x1,r0
mov r0,r1
mov.w @(0x1e,r10),r0
cmp/hs r0,r1
bf rl_active_continue
mov #0x8,r0
shll8 r0
not r0,r0
and r0,r11
mov #0xe,r2
bra rl_abort
nop
rl_active_continue:
mov r1,r0
mov.w r0,@(0x6,r8)
mov #0x0,r0
mov.b r0,@(0x1,r8)

// Publish ACTIVE and HOLD, then run the latched regulator. Each controller
// ends in the control publisher, which computes q and the wire views.
rl_publish_active:
mov #0x10,r0
shll8 r0
or r0,r11
mov.b @(0x5,r8),r0
cmp/eq 0x1,r0
bf rl_publish_flags
mov #0x40,r0
shll8 r0
or r0,r11
rl_publish_flags:
mov r11,r0
mov.w r0,@(0x2,r8)
mov r10,r4
mov r8,r5
mov r14,r0
cmp/eq 0x1,r0
mov.l @(rl_speed_controller_entry,pc),r0
bf rl_publish_controller
mov.l @(rl_rpm_controller_entry,pc),r0
rl_publish_controller:
jsr @r0
nop
bra rl_engine_exit
nop

// Leave ACTIVE through COOLDOWN with r2 as the reason: q and ready drop at
// once and the regulator, trims and controller fields remain as diagnostics.
// The phase is the first store, so the ignition publisher sees either the
// previous ACTIVE record or a COOLDOWN record, which it publishes as stock.
rl_abort:
mov #0x2,r0
mov.b r0,@r8
mov r2,r0
mov.b r0,@(0x1,r8)
mov r11,r0
mov.w r0,@(0x2,r8)
mov #0x0,r0
mov.w r0,@(0x8,r8)
mov.w r0,@(0x1a,r8)
mov.b r0,@(0xb,r9)
bra rl_engine_exit
nop

rl_corrupt_state:
mov #0x0,r4
mov.l @(rl_limiter_commit,pc),r0
jsr @r0
nop
mov r8,r1
mov #0x0,r0
mov #0x7,r2
rl_corrupt_clear_base:
mov.l r0,@r1
add 0x4,r1
dt r2
bf rl_corrupt_clear_base
mov #0x1e,r0
mov.w r2,@(r0,r8)
mov r9,r1
mov #0x0,r0
mov #0x8,r2
rl_corrupt_clear_extension:
mov.l r0,@r1
add 0x4,r1
dt r2
bf rl_corrupt_clear_extension
mov #0x7d,r0
shll2 r0
shll r0
mov.w r0,@(0xc,r9)
mov #0x2,r0
mov.b r0,@r8
mov #0x10,r0
mov.b r0,@(0x1,r8)

// The wire views follow the stored trim, ready mark and efficiency, which
// the ignition publisher rewrites from the crank-tooth interrupt. The views
// are read, computed and stored with interrupts masked.
rl_engine_exit:
stc sr,r6
mov r6,r0
or 0xf0,r0
ldc r0,sr
mov r9,r7
mov.l @(rl_load_views_entry,pc),r0
jsr @r0
nop
mov.l r3,@(0xc,r9)
mov r1,r0
mov.w r0,@(0x1e,r9)
ldc r6,sr
mov.l @r15+,r14
mov.l @r15+,r13
mov.l @r15+,r12
mov.l @r15+,r11
mov.l @r15+,r10
mov.l @r15+,r9
mov.l @r15+,r8
lds.l @r15+,pr
rts
nop

.align 4
rl_gate_selector_address:
.long 0xFFFF5D00
rl_ascd_address:
.long 0xFFFF41AE
rl_pedal_address:
.long 0xFFFF2672
rl_coolant_address:
.long 0xFFFF1077
rl_speed_controller_entry:
.long 0x000D40C0
rl_rpm_controller_entry:
.long 0x000D6400
rl_limiter_commit:
.long 0x000D3660
rl_load_views_entry:
.long 0x000D7184

// Gate helper: r1 = flag bits, r2 = reason. A pass ORs r1 into r11; a
// failure stores r2 in r13 unless an earlier gate failed. The valid entries
// also fail for an invalid configuration. Only T changes, so the sampled
// button stays in r3.
rl_gate_valid_pass_t:
bf rl_gate_fail
rl_gate_valid:
cmp/pl r12
rl_gate_pass_t:
bf rl_gate_fail
rl_gate_pass:
or r1,r11
rts
nop
rl_gate_valid_fail_t:
bf rl_gate_valid
rl_gate_fail_t:
bf rl_gate_pass
rl_gate_fail:
tst r13,r13
bf rl_gate_return
mov r2,r13
rl_gate_return:
rts
nop

// SPEED error window against r6 for the speed in r4: ABOVE first, then
// BELOW. SPEED_OK holds only when both pass.
rl_window:
sts.l pr,@-r15
mov #-0x41,r1
and r1,r11
mov r4,r7
sub r6,r7
mov.w @(0x1a,r10),r0
extu.w r0,r0
shlr8 r0
cmp/ge r7,r0
mov #0x40,r1
mov #0x14,r2
bsr rl_gate_valid_pass_t
nop
mov.w @(0x1a,r10),r0
extu.b r0,r0
neg r0,r0
cmp/ge r0,r7
bt rl_window_below
mov #-0x41,r1
and r1,r11
rl_window_below:
mov #0x0,r1
mov #0x15,r2
bsr rl_gate_valid_pass_t
nop
lds.l @r15+,pr
rts
nop


// Head check of the configuration in r10: r7 = 1 for a valid head, else 0.
// The validator at 0xD6680 then checks the slots of a valid head and, after
// five valid slots, the efficiency table. It returns r0 = 0 for an invalid
// configuration, and bit0 and bit1 for a valid table otherwise.
rl_validate_config:
mov #0x0,r7
mov.w @r10,r0
mov.w @(rl_head_magic,pc),r1
cmp/eq r1,r0
bf rl_head_done
mov.b @(0x2,r10),r0
cmp/eq 0x6,r0
bf rl_head_done
mov.b @(0x3,r10),r0
mov #0x1,r1
cmp/hi r1,r0
bt rl_head_done
mov.b @(0x4,r10),r0
tst 0xe0,r0
bf rl_head_done
mov.b @(0x5,r10),r0
tst r0,r0
bf rl_head_done
mov.b @(0x6,r10),r0
extu.b r0,r1
mov.b @(0x7,r10),r0
extu.b r0,r0
cmp/hs r1,r0
bf rl_head_done
// Two enabled activation speed bounds are ordered.
mov.w @(0x8,r10),r0
extu.w r0,r1
tst r1,r1
bt rl_head_speed_ordered
mov.w @(0xa,r10),r0
extu.w r0,r0
tst r0,r0
bt rl_head_speed_ordered
cmp/hs r1,r0
bf rl_head_done
rl_head_speed_ordered:
// Minimum RPM 1..32766.
mov.w @(0xc,r10),r0
add -0x1,r0
mov.w @(rl_head_rpm_span,pc),r1
cmp/hs r1,r0
bt rl_head_done
// The target offset lies strictly inside both nonzero abort limits.
mov.w @(0x1a,r10),r0
extu.b r0,r2
tst r2,r2
bt rl_head_done
extu.w r0,r1
shlr8 r1
tst r1,r1
bt rl_head_done
mov.w @(0x10,r10),r0
add r0,r1
cmp/pl r1
bf rl_head_done
sub r0,r2
cmp/pl r2
bf rl_head_done
// Window width nonzero; u rate 1..1000; reserved word zero; integrator
// limit at most 1000; reserved bytes 0x1C/0x1D zero.
mov.w @(0x12,r10),r0
shlr8 r0
tst 0xff,r0
bt rl_head_done
mov.w @(rl_head_u_one,pc),r1
mov.w @(0x14,r10),r0
extu.w r0,r0
add -0x1,r0
cmp/hs r1,r0
bt rl_head_done
mov.w @(0x16,r10),r0
tst r0,r0
bf rl_head_done
mov.w @(0x18,r10),r0
extu.w r0,r0
cmp/hi r1,r0
bt rl_head_done
mov.w @(0x1c,r10),r0
tst r0,r0
bf rl_head_done
// Run timeout and rearm 1..32767; frame age limit 1..254 and reserved byte
// 0x23 zero; inverse magic, head marker and end marker.
mov.w @(0x1e,r10),r0
cmp/pl r0
bf rl_head_done
mov r10,r2
add 0x20,r2
mov.w @r2,r0
cmp/pl r0
bf rl_head_done
mov.b @(0x3,r2),r0
tst r0,r0
bf rl_head_done
mov.b @(0x2,r2),r0
tst r0,r0
bt rl_head_done
cmp/eq -0x1,r0
bt rl_head_done
mov.w @(0x4,r2),r0
mov.w @(rl_head_magic_inverse,pc),r1
cmp/eq r1,r0
bf rl_head_done
mov.w @(rl_head_marker,pc),r1
mov.w @(0x6,r2),r0
cmp/eq r1,r0
bf rl_head_done
mov #0x64,r0
mov.w @(r0,r10),r0
cmp/eq r1,r0
bf rl_head_done
mov #0x1,r7
rl_head_done:
mov.l @(rl_slot_validator_entry,pc),r0
jmp @r0
nop

.align 4
rl_slot_validator_entry:
.long 0x000D6680
rl_head_magic:
.word 0x524C
rl_head_magic_inverse:
.word 0xADB3
rl_head_marker:
.word 0xA55A
rl_head_u_one:
.word 1000
rl_head_rpm_span:
.word 32766
