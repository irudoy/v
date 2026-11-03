// Fail-closed Rolling Launch state machine for exact JK08A.
//
// State layout at 0xFFFF5D40:
//   +0x00 u8  phase: 0 IDLE, 1 ACTIVE, 2 COOLDOWN
//   +0x01 u8  abort reason
//   +0x02 u16 gate and output flags
//   +0x04 u8  active map index snapshot
//   +0x05 u8  active mode snapshot
//   +0x06 u16 run ticks
//   +0x08 u16 rearm ticks
//   +0x0A u16 captured native RPM
//   +0x0C u16 target vehicle speed, km/h*10
//   +0x0E u16 torque fraction u after the rate limit, thousandths
//   +0x10 s16 speed error against the target, km/h*10
//   +0x12 s16 speed integrator, sixteenths of one thousandth
//   +0x14 u16 fuel-cut request: the cylinder mask that the fuel-cut wrapper
//             ORs into the stock coordinator result; cleared on every entry
//   +0x16 u16 torque command before the rate limit, thousandths
//   +0x18 u16 RPM ceiling latch: 0 released, 1 latched
//   +0x1A u16 cut fraction c = 1000 - min(1000, 1000 * u / e) of the trim
//             unit, thousandths; cleared at activation
//
// One tick is one exact periodic scheduler pass: 204800/Pphi seconds. Passive
// target-CAN timing establishes Pphi=20 MHz and a 10.24 ms target period.
// The default calibration enables no map slot. Modes are 0 observe and 1
// hold. Hold latches the all-cylinder request 0x003F when RPM exceeds the
// captured RPM plus the ceiling offset and releases it at or below that sum
// minus the hysteresis. No mode writes the fuel-cut shadow of the selected
// map.

.org 0x000D38E4
rolling_launch_engine:
sts.l pr,@-r15
mov.l @(rl_state_address,pc),r5
mov #0x0,r0
mov.w r0,@(0x14,r5)
mov.b @r5,r0
cmp/eq 0x0,r0
bt rl_dispatch_idle
cmp/eq 0x1,r0
bt rl_dispatch_active
cmp/eq 0x2,r0
bt rl_dispatch_cooldown
bra rl_corrupt_state
nop
rl_dispatch_idle:
bra rl_idle
nop
rl_dispatch_active:
bra rl_active
nop
rl_dispatch_cooldown:
bra rl_cooldown
nop

// IDLE structural invariants prevent a partially initialized state from
// activating. Historical capture and controller diagnostic fields may remain.
rl_idle:
mov.b @(0x4,r5),r0
mov #0x5,r1
cmp/hs r1,r0
bt rl_idle_corrupt
mov.b @(0x5,r5),r0
tst r0,r0
bf rl_idle_corrupt
mov.w @(0x6,r5),r0
extu.w r0,r0
tst r0,r0
bf rl_idle_corrupt
mov.w @(0x8,r5),r0
extu.w r0,r0
tst r0,r0
bf rl_idle_corrupt
bsr rl_evaluate_gates
nop
tst r0,r0
bt rl_idle_activate
bra rl_engine_return
nop
rl_idle_corrupt:
bra rl_corrupt_state
nop
rl_idle_activate:

// Capture the map, mode, native RPM, and target speed. The controller starts
// from full torque, an empty integrator, and a released ceiling latch.
mov.l @(rl_state_address,pc),r5
mov.l @(rl_selector_address,pc),r4
mov.b @r4,r0
mov.b r0,@(0x4,r5)
mov.l @(rl_config_address,pc),r4
mov.b @(0x3,r4),r0
mov.b r0,@(0x5,r5)
mov #0x0,r0
mov.w r0,@(0x6,r5)
mov.w r0,@(0x8,r5)
mov.w r0,@(0x12,r5)
mov.l r0,@(0x18,r5)
mov.l @(rl_rpm_address,pc),r1
mov.w @r1,r0
mov.w r0,@(0xA,r5)
mov.l @(rl_speed_address,pc),r1
mov.w @r1,r2
extu.w r2,r2
mov.w @(0x10,r4),r0
add r0,r2
cmp/pz r2
bt rl_target_not_negative
mov #0x0,r2
rl_target_not_negative:
mov #-0x1,r3
extu.w r3,r3
cmp/hs r2,r3
bt rl_target_not_saturated
mov r3,r2
rl_target_not_saturated:
mov r2,r0
mov.w r0,@(0xC,r5)
mov.w @(rl_u_one,pc),r0
mov.w r0,@(0xE,r5)
mov #0x1,r0
mov.b r0,@r5
bra rl_run_controller
nop

// ACTIVE validates the captured arbitration state, the torque fraction, and
// the ceiling latch before checking runtime gates. Map or mode changes take priority over all
// input-gate reasons.
rl_active:
mov.b @(0x4,r5),r0
mov #0x5,r1
cmp/hs r1,r0
bt rl_active_corrupt
mov.b @(0x5,r5),r0
mov #0x2,r1
cmp/hs r1,r0
bt rl_active_corrupt
mov.w @(0x8,r5),r0
extu.w r0,r0
tst r0,r0
bf rl_active_corrupt
mov.w @(0xE,r5),r0
extu.w r0,r0
mov.w @(rl_u_one,pc),r1
cmp/hi r1,r0
bt rl_active_corrupt
mov.w @(0x18,r5),r0
mov #0x1,r1
cmp/hi r1,r0
bf rl_active_state_valid
rl_active_corrupt:
bra rl_corrupt_state
nop
rl_active_state_valid:
bsr rl_evaluate_gates
nop
mov.l @(rl_state_address,pc),r5
mov.l @(rl_selector_address,pc),r4
mov.b @r4,r2
mov.b @(0x4,r5),r0
cmp/eq r0,r2
bt rl_active_check_mode
mov #0x11,r0
mov.b r0,@(0x1,r5)
bra rl_abort_active
nop
rl_active_check_mode:
mov.l @(rl_config_address,pc),r4
mov.b @(0x3,r4),r0
mov r0,r2
mov.b @(0x5,r5),r0
cmp/eq r0,r2
bt rl_active_check_reason
mov #0x12,r0
mov.b r0,@(0x1,r5)
bra rl_abort_active
nop
rl_active_check_reason:
mov.b @(0x1,r5),r0
tst r0,r0
bt rl_active_timer
mov.l @(rl_button_address,pc),r4
mov.b @r4,r0
cmp/eq 0x8,r0
bf rl_active_check_release
mov #0xF,r0
mov.b r0,@(0x1,r5)
bra rl_abort_active
nop
rl_active_check_release:
cmp/eq 0x20,r0
bf rl_abort_active
mov #0x7,r0
mov.b r0,@(0x1,r5)
bra rl_abort_active
nop

rl_active_timer:
mov.w @(0x6,r5),r0
mov r0,r2
extu.w r2,r2
add 0x1,r2
extu.w r2,r2
mov.l @(rl_config_address,pc),r4
mov.w @(0x1E,r4),r0
mov r0,r3
extu.w r3,r3
cmp/hs r3,r2
bf rl_active_store_timer
mov #0xE,r0
mov.b r0,@(0x1,r5)
mov.b @(0x2,r5),r0
and 0xF7,r0
mov.b r0,@(0x2,r5)
bra rl_abort_active
nop
rl_active_store_timer:
mov r2,r0
mov.w r0,@(0x6,r5)
rl_run_controller:
mov.l @(rl_controller_entry,pc),r0
jsr @r0
nop
bra rl_engine_return
nop

// Leave ACTIVE through COOLDOWN. This tick has already cleared the request,
// and the abort releases the ceiling latch. The controller fields remain as
// diagnostics until the next activation.
rl_abort_active:
mov.l @(rl_state_address,pc),r5
mov #0x0,r0
mov.w r0,@(0x8,r5)
mov.w r0,@(0x18,r5)
mov.b @(0x2,r5),r0
and 0x0F,r0
mov.b r0,@(0x2,r5)
mov #0x2,r0
mov.b r0,@r5
bra rl_engine_return
nop

// COOLDOWN keeps selector input blocked. Rearm advances only while every
// calibration integrity check passes and the stable button code is released.
rl_cooldown:
mov.b @(0x4,r5),r0
mov #0x5,r1
cmp/hs r1,r0
bt rl_corrupt_state
mov.b @(0x5,r5),r0
mov #0x2,r1
cmp/hs r1,r0
bt rl_corrupt_state
mov.w @(0x8,r5),r0
extu.w r0,r0
mov.w @(rl_u16_8000,pc),r1
extu.w r1,r1
cmp/hs r1,r0
bt rl_corrupt_state
bsr rl_validate_config
nop
tst r0,r0
bt rl_cooldown_config_invalid
mov.l @(rl_button_address,pc),r4
mov.b @r4,r0
cmp/eq 0x20,r0
bf rl_cooldown_reset_rearm
mov.l @(rl_state_address,pc),r5
mov.w @(0x8,r5),r0
mov r0,r2
extu.w r2,r2
add 0x1,r2
extu.w r2,r2
mov.l @(rl_config_address,pc),r4
mov r4,r1
add 0x20,r1
mov.w @r1,r0
mov r0,r3
extu.w r3,r3
cmp/hs r3,r2
bf rl_cooldown_store_rearm
mov #0x0,r0
mov.b r0,@r5
mov.b r0,@(0x2,r5)
mov.b r0,@(0x3,r5)
mov.b r0,@(0x5,r5)
mov.w r0,@(0x6,r5)
mov.w r0,@(0x8,r5)
bra rl_engine_return
nop
rl_cooldown_store_rearm:
mov r2,r0
mov.w r0,@(0x8,r5)
bra rl_engine_return
nop
rl_cooldown_reset_rearm:
mov.l @(rl_state_address,pc),r5
mov #0x0,r0
mov.w r0,@(0x8,r5)
bra rl_engine_return
nop
rl_cooldown_config_invalid:
mov.l @(rl_state_address,pc),r5
mov #0x1,r0
mov.b r0,@(0x1,r5)
mov #0x0,r0
mov.b r0,@(0x2,r5)
mov.b r0,@(0x3,r5)
mov.w r0,@(0x8,r5)
bra rl_engine_return
nop

// Invalid state always restores map 1, clears all Rolling Launch RAM, and
// enters COOLDOWN with a persistent STATE_CORRUPT reason.
rl_corrupt_state:
mov #0x0,r4
mov.l @(rl_limiter_commit,pc),r0
jsr @r0
nop
mov.l @(rl_state_address,pc),r5
mov r5,r1
mov #0x0,r0
mov #0x7,r2
rl_corrupt_clear_loop:
mov.l r0,@r1
add 0x4,r1
dt r2
bf rl_corrupt_clear_loop
mov #0x2,r0
mov.b r0,@r5
mov #0x10,r0
mov.b r0,@(0x1,r5)

rl_engine_return:
lds.l @r15+,pr
rts
nop

// Core-local literal pool. SH PC-relative loads are forward-only, so each
// independently sized code section owns the exact addresses it consumes.
.org 0x000D3AE8
rl_state_address:
.long 0xFFFF5D40
rl_selector_address:
.long 0xFFFF5D00
rl_config_address:
.long 0x000D6220
rl_rpm_address:
.long 0xFFFF11BC
rl_speed_address:
.long 0xFFFF113C
rl_limiter_commit:
.long 0x000D3660
rl_button_address:
.long 0xFFFF2A85
rl_controller_entry:
.long 0x000D40C0
rl_u16_8000:
.word 0x8000
rl_u_one:
.word 1000

// Evaluate every gate and publish all satisfied bits. The first failure is
// retained by priority in abort_reason. r0 returns that reason. IDLE checks
// the activation speed range; ACTIVE checks the speed-error window.
.org 0x000D3B0C
rl_evaluate_gates:
sts.l pr,@-r15
mov.l @(rl_gate_state_address,pc),r5
mov #0x0,r0
mov.b r0,@(0x1,r5)
mov.b r0,@(0x2,r5)
mov.b r0,@(0x3,r5)
bsr rl_validate_config
nop
mov r0,r7
tst r0,r0
bt rl_gate_config_fail
mov.b @(0x3,r5),r0
or 0x01,r0
mov.b r0,@(0x3,r5)
bra rl_gate_map_index
nop
rl_gate_config_fail:
mov #0x1,r0
mov.b r0,@(0x1,r5)

rl_gate_map_index:
mov.l @(rl_gate_selector_address,pc),r4
mov.b @r4,r2
extu.b r2,r2
mov #0x5,r1
cmp/hs r1,r2
bf rl_gate_map_index_valid
mov.b @(0x1,r5),r0
tst r0,r0
bf rl_gate_selector
mov #0x2,r0
mov.b r0,@(0x1,r5)
bra rl_gate_selector
nop
rl_gate_map_index_valid:
tst r7,r7
bt rl_gate_map_disabled
mov r2,r0
mov.l @(rl_gate_map_enable_masks,pc),r1
mov.b @(r0,r1),r2
mov.l @(rl_gate_config_address,pc),r1
mov.b @(0x4,r1),r0
and r2,r0
tst r0,r0
bt rl_gate_map_disabled
mov.b @(0x3,r5),r0
or 0x02,r0
mov.b r0,@(0x3,r5)
bra rl_gate_selector
nop
rl_gate_map_disabled:
mov.b @(0x1,r5),r0
tst r0,r0
bf rl_gate_selector
mov #0x3,r0
mov.b r0,@(0x1,r5)

rl_gate_selector:
mov.l @(rl_gate_selector_address,pc),r4
mov.b @(0x1,r4),r0
mov r0,r3
mov.b @(0x2,r4),r0
or r0,r3
mov.b @(0x3,r4),r0
or r3,r0
tst r0,r0
bf rl_gate_selector_fail
mov.b @(0x3,r5),r0
or 0x04,r0
mov.b r0,@(0x3,r5)
bra rl_gate_feedback
nop
rl_gate_selector_fail:
mov.b @(0x1,r5),r0
tst r0,r0
bf rl_gate_feedback
mov #0x4,r0
mov.b r0,@(0x1,r5)

rl_gate_feedback:
mov r4,r1
add 0x4,r1
mov.l @r1,r0
tst r0,r0
bf rl_gate_feedback_fail
mov.b @(0x3,r5),r0
or 0x08,r0
mov.b r0,@(0x3,r5)
bra rl_gate_ascd
nop
rl_gate_feedback_fail:
mov.b @(0x1,r5),r0
tst r0,r0
bf rl_gate_ascd
mov #0x5,r0
mov.b r0,@(0x1,r5)

rl_gate_ascd:
mov.l @(rl_gate_ascd_address,pc),r4
mov.b @r4,r0
tst 0x80,r0
bf rl_gate_ascd_fail
mov.b @(0x3,r5),r0
or 0x10,r0
mov.b r0,@(0x3,r5)
bra rl_gate_button
nop
rl_gate_ascd_fail:
mov.b @(0x1,r5),r0
tst r0,r0
bf rl_gate_button
mov #0x6,r0
mov.b r0,@(0x1,r5)

rl_gate_button:
mov.l @(rl_gate_button_address,pc),r4
mov.b @r4,r0
cmp/eq 0x2,r0
bf rl_gate_button_fail
mov.b @(0x3,r5),r0
or 0x20,r0
mov.b r0,@(0x3,r5)
bra rl_gate_speed_frame
nop
rl_gate_button_fail:
mov.b @(0x1,r5),r0
tst r0,r0
bf rl_gate_speed_frame
mov #0x8,r0
mov.b r0,@(0x1,r5)

// The stock receive age of the vehicle-speed record 13 advances once per
// 10.24 ms tick without a processed 0x284 frame and saturates at 255.
rl_gate_speed_frame:
tst r7,r7
bt rl_gate_speed_frame_fail
mov.l @(rl_gate_speed_age_address,pc),r4
mov.b @r4,r2
extu.b r2,r2
mov.l @(rl_gate_config_address,pc),r4
mov r4,r1
add 0x22,r1
mov.b @r1,r0
extu.b r0,r0
cmp/hs r2,r0
bf rl_gate_speed_frame_fail
mov.b @(0x2,r5),r0
or 0x04,r0
mov.b r0,@(0x2,r5)
bra rl_gate_speed
nop
rl_gate_speed_frame_fail:
mov.b @(0x1,r5),r0
tst r0,r0
bf rl_gate_speed
mov #0xD,r0
mov.b r0,@(0x1,r5)

rl_gate_speed:
tst r7,r7
bt rl_gate_speed_low
mov.l @(rl_gate_speed_address,pc),r4
mov.w @r4,r2
extu.w r2,r2
mov.l @(rl_gate_config_address,pc),r4
mov.b @r5,r0
cmp/eq 0x1,r0
bt rl_gate_speed_window
// A zero activation bound disables that side of the range.
mov.w @(0x8,r4),r0
extu.w r0,r0
tst r0,r0
bt rl_gate_speed_max
cmp/hs r0,r2
bf rl_gate_speed_low
rl_gate_speed_max:
mov.w @(0xA,r4),r0
extu.w r0,r0
tst r0,r0
bt rl_gate_speed_pass
cmp/hs r2,r0
bt rl_gate_speed_pass
mov #0x13,r3
bra rl_gate_speed_fail
nop
rl_gate_speed_window:
mov.w @(0xC,r5),r0
extu.w r0,r0
sub r0,r2
mov r4,r1
add 0x1A,r1
mov.b @r1,r0
extu.b r0,r0
cmp/gt r0,r2
bf rl_gate_speed_below
mov #0x14,r3
bra rl_gate_speed_fail
nop
rl_gate_speed_below:
mov.b @(0x1,r1),r0
extu.b r0,r0
neg r0,r0
cmp/ge r0,r2
bt rl_gate_speed_pass
mov #0x15,r3
bra rl_gate_speed_fail
nop
rl_gate_speed_low:
mov #0x9,r3
rl_gate_speed_fail:
mov.b @(0x1,r5),r0
tst r0,r0
bf rl_gate_rpm
mov r3,r0
mov.b r0,@(0x1,r5)
bra rl_gate_rpm
nop
rl_gate_speed_pass:
mov.b @(0x3,r5),r0
or 0x40,r0
mov.b r0,@(0x3,r5)

rl_gate_rpm:
tst r7,r7
bt rl_gate_rpm_fail
mov.l @(rl_gate_rpm_address,pc),r4
mov.w @r4,r2
extu.w r2,r2
mov.l @(rl_gate_config_address,pc),r4
mov.w @(0xC,r4),r0
extu.w r0,r0
cmp/hs r0,r2
bf rl_gate_rpm_fail
mov.b @(0x3,r5),r0
or 0x80,r0
mov.b r0,@(0x3,r5)
bra rl_gate_pedal
nop
rl_gate_rpm_fail:
mov.b @(0x1,r5),r0
tst r0,r0
bf rl_gate_pedal
mov #0xA,r0
mov.b r0,@(0x1,r5)

rl_gate_pedal:
tst r7,r7
bt rl_gate_pedal_fail
mov.l @(rl_gate_pedal_address,pc),r4
mov.w @r4,r2
extu.w r2,r2
mov.l @(rl_gate_config_address,pc),r4
mov.w @(0xE,r4),r0
extu.w r0,r0
cmp/hs r0,r2
bf rl_gate_pedal_fail
mov.b @(0x2,r5),r0
or 0x01,r0
mov.b r0,@(0x2,r5)
bra rl_gate_coolant
nop
rl_gate_pedal_fail:
mov.b @(0x1,r5),r0
tst r0,r0
bf rl_gate_coolant
mov #0xB,r0
mov.b r0,@(0x1,r5)

rl_gate_coolant:
tst r7,r7
bt rl_gate_coolant_fail
mov.l @(rl_gate_coolant_address,pc),r4
mov.b @r4,r2
extu.b r2,r2
mov.l @(rl_gate_config_address,pc),r4
mov.b @(0x6,r4),r0
extu.b r0,r0
cmp/hs r0,r2
bf rl_gate_coolant_fail
mov.b @(0x7,r4),r0
extu.b r0,r0
cmp/hs r2,r0
bf rl_gate_coolant_fail
mov.b @(0x2,r5),r0
or 0x02,r0
mov.b r0,@(0x2,r5)
bra rl_gate_timer
nop
rl_gate_coolant_fail:
mov.b @(0x1,r5),r0
tst r0,r0
bf rl_gate_timer
mov #0xC,r0
mov.b r0,@(0x1,r5)

rl_gate_timer:
tst r7,r7
bt rl_gate_return
mov.b @(0x2,r5),r0
or 0x08,r0
mov.b r0,@(0x2,r5)
rl_gate_return:
mov.b @(0x1,r5),r0
extu.b r0,r0
lds.l @r15+,pr
rts
nop

// Gate-local literal pool.
.org 0x000D3D1C
rl_gate_state_address:
.long 0xFFFF5D40
rl_gate_selector_address:
.long 0xFFFF5D00
rl_gate_map_enable_masks:
.long 0x000D3D48
rl_gate_config_address:
.long 0x000D6220
rl_gate_ascd_address:
.long 0xFFFF41AE
rl_gate_button_address:
.long 0xFFFF2A85
rl_gate_speed_address:
.long 0xFFFF113C
rl_gate_speed_age_address:
.long 0xFFFF3B38
rl_gate_rpm_address:
.long 0xFFFF11BC
rl_gate_pedal_address:
.long 0xFFFF2672
rl_gate_coolant_address:
.long 0xFFFF1077
rl_gate_map_enable_mask_bytes:
.byte 0x01,0x02,0x04,0x08,0x10

// Full configuration validation is independent of current state and inputs.
// It uses only r0..r4 so callers may retain r5..r7.
.org 0x000D3D50
rl_validate_config:
mov.l @(rl_helper_config_address,pc),r3
mov.w @r3,r0
extu.w r0,r0
mov.w @(rl_helper_config_magic,pc),r1
extu.w r1,r1
cmp/eq r1,r0
bf rl_config_invalid
mov.b @(0x2,r3),r0
cmp/eq 0x5,r0
bf rl_config_invalid
mov.b @(0x3,r3),r0
mov #0x2,r1
cmp/hs r1,r0
bt rl_config_invalid
mov.b @(0x4,r3),r0
and 0xE0,r0
tst r0,r0
bf rl_config_invalid
mov.b @(0x5,r3),r0
tst r0,r0
bf rl_config_invalid
mov.b @(0x6,r3),r0
mov r0,r2
extu.b r2,r2
mov.b @(0x7,r3),r0
extu.b r0,r0
cmp/hs r2,r0
bf rl_config_invalid
// Two enabled activation speed bounds must be ordered.
mov.w @(0x8,r3),r0
extu.w r0,r2
tst r2,r2
bt rl_config_speed_ordered
mov.w @(0xA,r3),r0
extu.w r0,r0
tst r0,r0
bt rl_config_speed_ordered
cmp/hs r2,r0
bf rl_config_invalid
rl_config_speed_ordered:
mov.w @(0xC,r3),r0
extu.w r0,r0
tst r0,r0
bt rl_config_invalid
// The signed target offset lies strictly inside both abort windows.
mov r3,r4
add 0x1A,r4
mov.b @r4+,r0
extu.b r0,r1
tst r1,r1
bt rl_config_invalid
mov.b @r4,r0
extu.b r0,r2
tst r2,r2
bt rl_config_invalid
mov.w @(0x10,r3),r0
add r0,r1
cmp/pl r1
bf rl_config_invalid
sub r0,r2
cmp/pl r2
bf rl_config_invalid
mov r3,r4
add 0x12,r4
mov.b @r4,r0
tst r0,r0
bt rl_config_invalid
mov.w @(rl_helper_u_one,pc),r1
mov.w @(0x14,r3),r0
extu.w r0,r0
tst r0,r0
bt rl_config_invalid
cmp/hi r1,r0
bt rl_config_invalid
mov.w @(0x16,r3),r0
tst r0,r0
bf rl_config_invalid
mov.w @(0x18,r3),r0
extu.w r0,r0
cmp/hi r1,r0
bt rl_config_invalid
mov.w @(0x1C,r3),r0
extu.w r0,r0
tst r0,r0
bt rl_config_invalid
mov.w @(rl_helper_u16_8000,pc),r1
extu.w r1,r1
mov.w @(0x1E,r3),r0
extu.w r0,r0
tst r0,r0
bt rl_config_invalid
cmp/hs r1,r0
bt rl_config_invalid
mov r3,r4
add 0x20,r4
mov.w @r4+,r0
extu.w r0,r0
tst r0,r0
bt rl_config_invalid
cmp/hs r1,r0
bt rl_config_invalid
// The stock receive age saturates at 255, so 255 never expires.
mov.b @r4+,r0
extu.b r0,r0
tst r0,r0
bt rl_config_invalid
mov #-0x1,r1
extu.b r1,r1
cmp/eq r1,r0
bt rl_config_invalid
// The ceiling hysteresis is nonzero and does not exceed the ceiling offset.
mov.b @r4+,r0
extu.b r0,r2
tst r2,r2
bt rl_config_invalid
mov.w @(0x1C,r3),r0
extu.w r0,r0
cmp/hs r2,r0
bf rl_config_invalid
mov.w @r4+,r0
extu.w r0,r0
mov.w @(rl_helper_config_magic_inverse,pc),r1
extu.w r1,r1
cmp/eq r1,r0
bf rl_config_invalid
mov.w @r4,r0
extu.w r0,r0
mov.w @(rl_helper_config_end_marker,pc),r1
extu.w r1,r1
cmp/eq r1,r0
bf rl_config_invalid
mov.l @(rl_helper_slot_validator,pc),r0
jmp @r0
nop
rl_config_invalid:
mov #0x0,r0
rts
nop

.org 0x000D3E58
rl_helper_config_address:
.long 0x000D6220
rl_helper_config_magic:
.word 0x524C
rl_helper_config_magic_inverse:
.word 0xADB3
rl_helper_config_end_marker:
.word 0xA55A
rl_helper_u16_8000:
.word 0x8000
rl_helper_u_one:
.word 1000
.org 0x000D3E68
rl_helper_slot_validator:
.long 0x000D6268
