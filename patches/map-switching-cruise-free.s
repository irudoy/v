// JK08A cruise-free Map Switching selector, stationary 0x284 latch, and
// startup/arbitration helpers.
//
// Dedicated expansion RAM: 0xFFFF6000..0xFFFF601F (32 bytes):
//   +0x00  stationary_flags (bit0=observed, bit1=stationary_valid)
//   +0x01  stationary_age   (10.24 ms ticks since last 0x284 frame, 0xFF init)
//   +0x02  last_raw_speed   (BE16 raw payload[4:6] from 0x284, 0xFFFF init)
//   +0x04  cf_phase         (0=IDLE_WAIT_RELEASE, 1=ARMED_RELEASED, 2=PRESSED_LATCHED)
//   +0x05  cf_debounce      (consecutive ticks meeting target pedal state)
//   +0x06  tach_ticks       (remaining 0x551 ticks for tach slot display)
//   +0x07  tach_slot        (1..5 active tach display slot, 0=inactive)
//   +0x08  cf_last_reason   (last block/abort reason code 0..6)
//   +0x09  active_source    (0=startup, 1=ASCD, 2=cruise_free)
//
// MSCF v1 configuration block sits at 0x000D6800..0x000D681F (32 bytes).
// All entry points preserve callee-saved registers and use only r0..r7 and PR.

// ---------------------------------------------------------------------------
// 1. cruise_free_startup_init @ 0x000D6820 (32 bytes)
// ---------------------------------------------------------------------------
.org 0x000D6820
cruise_free_startup_init:
mov.l @(cf_init_ram,pc),r1
mov #0x0,r0
mov #0x8,r2
cf_init_zero_loop:
mov.l r0,@r1
add 0x4,r1
dt r2
bf cf_init_zero_loop
mov.l @(cf_init_ram,pc),r1
mov #-0x1,r0
mov.b r0,@(0x1,r1)
mov.w r0,@(0x2,r1)
rts
nop

.align 4
cf_init_ram:
.long 0xFFFF6000

// ---------------------------------------------------------------------------
// 2. stationary_rx_wrapper @ 0x000D6840 (192 bytes)
// Hooked at 0x00021850 (stock 0x000C3B14 hcan1_receive_payload_dispatch).
// ---------------------------------------------------------------------------
.org 0x000D6840
stationary_rx_wrapper:
sts.l pr,@-r15
mov.l @(stat_stock_rx_dispatch,pc),r0
jsr @r0
nop

mov.l @(stat_cf_ram,pc),r5
// Check both HCAN1 receive gates: port_ready (FFFF4185.7) & hcan1_init (FFFF4195.0).
mov.l @(stat_port_state,pc),r1
mov.b @r1,r0
tst 0x80,r0
bt stat_reset_unobserved
mov.l @(stat_hcan1_state,pc),r1
mov.b @r1,r0
tst 0x1,r0
bt stat_reset_unobserved

// Check new-frame event bit set by 000C3B14 on 0x284 (FFFF3B37.3).
mov.l @(stat_rx_state,pc),r1
mov.b @r1,r0
tst 0x8,r0
bt stat_no_new_frame

// New 0x284 frame arrived: latch BE16(FFFF3B3D..3B3E) and reset age to 0.
mov.l @(stat_rx_raw_hi,pc),r1
mov.b @r1+,r2
extu.b r2,r2
shll8 r2
mov.b @r1,r3
extu.b r3,r3
or r3,r2
mov r2,r0
mov.w r0,@(0x2,r5)
mov #0x0,r0
mov.b r0,@(0x1,r5)
tst r2,r2
bf stat_new_nonzero
mov #0x3,r0
mov.b r0,@r5
bra stat_return
nop
stat_new_nonzero:
mov #0x1,r0
mov.b r0,@r5
bra stat_return
nop

// No new frame this 10.24 ms tick: increment saturating age and test freshness.
stat_no_new_frame:
mov.b @(0x1,r5),r0
extu.b r0,r2
mov #-0x1,r0
extu.b r0,r3
cmp/hs r3,r2
bt stat_age_done
add 0x1,r2
mov r2,r0
mov.b r0,@(0x1,r5)
stat_age_done:
mov.b @r5,r0
tst 0x1,r0
bt stat_return
mov.w @(0x2,r5),r0
extu.w r0,r0
tst r0,r0
bf stat_clear_valid
mov.l @(stat_config_addr,pc),r4
mov.b @(0x7,r4),r0
extu.b r0,r3
cmp/hi r3,r2
bt stat_clear_valid
mov #0x3,r0
mov.b r0,@r5
bra stat_return
nop

stat_clear_valid:
mov #0x1,r0
mov.b r0,@r5
bra stat_return
nop

stat_reset_unobserved:
mov #0x0,r0
mov.b r0,@r5
mov #-0x1,r0
mov.b r0,@(0x1,r5)
mov.w r0,@(0x2,r5)

stat_return:
lds.l @r15+,pr
rts
nop

.align 4
stat_stock_rx_dispatch:
.long 0x000C3B14
stat_cf_ram:
.long 0xFFFF6000
stat_port_state:
.long 0xFFFF4185
stat_hcan1_state:
.long 0xFFFF4195
stat_rx_state:
.long 0xFFFF3B37
stat_rx_raw_hi:
.long 0xFFFF3B3D
stat_config_addr:
.long 0x000D6800

// ---------------------------------------------------------------------------
// 3. cruise_free_step @ 0x000D6900 (672 bytes)
// Entry called by selector_host with r4 mode:
//   0 = ASCD idle -> run cruise-free cyclic selector, then mirror active bit
//   1 = ASCD armed/blocked or feedback active -> clear cf transient, mirror
//   2 = ASCD committed -> mark active_source=1, arm tach if allowed & stopped
//       & stationary, clear cf transient, mirror
// ---------------------------------------------------------------------------
.org 0x000D6900
cruise_free_step:
sts.l pr,@-r15
mov.l @(cf_ram_base,pc),r5
mov r4,r0
cmp/eq 0x1,r0
bt cf_mode_blocked_jump
cmp/eq 0x2,r0
bt cf_mode_ascd_jump

// Mode 0: validate MSCF config and check cruise_free_enabled (flags bit 1).
mov.l @(cf_config_base,pc),r6
bsr cf_validate_cfg_local
nop
tst r0,r0
bt cf_fail_config
mov.b @(0x5,r6),r0
tst 0x2,r0
bt cf_fail_config

// Precondition 1: engine stopped (fine RPM == 0 && coarse RPM == 0).
mov.l @(cf_rpm_fine,pc),r1
mov.w @r1,r0
extu.w r0,r0
tst r0,r0
bf cf_fail_rpm
mov.l @(cf_rpm_coarse,pc),r1
mov.b @r1,r0
extu.b r0,r0
tst r0,r0
bf cf_fail_rpm

// Precondition 2: stationary contract holds (gates, valid, raw==0, age<=limit).
mov.l @(cf_port_state,pc),r1
mov.b @r1,r0
tst 0x80,r0
bt cf_fail_stationary
mov.l @(cf_hcan1_state,pc),r1
mov.b @r1,r0
tst 0x1,r0
bt cf_fail_stationary
mov.b @r5,r0
and 0x3,r0
cmp/eq 0x3,r0
bf cf_fail_stationary
mov.w @(0x2,r5),r0
extu.w r0,r0
tst r0,r0
bf cf_fail_stationary
mov.b @(0x1,r5),r0
extu.b r0,r2
mov.b @(0x7,r6),r0
extu.b r0,r3
cmp/hi r3,r2
bt cf_fail_stationary

// Precondition 3: brake switch held (FFFF2451.7 == 1).
mov.l @(cf_brake_byte,pc),r1
mov.b @r1,r0
tst 0x80,r0
bt cf_fail_brake

// Precondition 4: dual APP1 / APP2 valid range and |APP1 - APP2| <= diff_max.
mov.l @(cf_app1_addr,pc),r1
mov.w @r1,r2
extu.w r2,r2
mov.l @(cf_app2_addr,pc),r1
mov.w @r1,r3
extu.w r3,r3

mov.w @(0x8,r6),r0
extu.w r0,r1
cmp/hs r1,r2
bf cf_fail_pedal
cmp/hs r1,r3
bf cf_fail_pedal
mov.w @(0xA,r6),r0
extu.w r0,r1
cmp/hi r1,r2
bt cf_fail_pedal
mov.w @(0xC,r6),r0
extu.w r0,r1
cmp/hi r1,r3
bt cf_fail_pedal

mov r2,r4
cmp/hs r3,r2
bt cf_diff_pos
mov r3,r4
sub r2,r4
bra cf_diff_check
nop
cf_diff_pos:
sub r3,r4
cf_diff_check:
mov.w @(0xE,r6),r0
extu.w r0,r1
cmp/hi r1,r4
bt cf_fail_pedal
bra cf_classify_pedal
nop

// Mid-body trampolines keep all bt/bf targets within +-254 bytes.
cf_mode_blocked_jump:
mov #0x6,r0
bra cf_reset_reason
nop
cf_mode_ascd_jump:
bra cf_mode_ascd_commit
nop
cf_fail_config:
mov #0x1,r0
bra cf_reset_reason
nop
cf_fail_rpm:
mov #0x2,r0
bra cf_reset_reason
nop
cf_fail_stationary:
mov #0x3,r0
bra cf_reset_reason
nop
cf_fail_brake:
mov #0x4,r0
bra cf_reset_reason
nop
cf_fail_pedal:
mov #0x5,r0
cf_reset_reason:
mov.b r0,@(0x8,r5)
mov #0x0,r0
mov.b r0,@(0x4,r5)
mov.b r0,@(0x5,r5)
bra cf_mirror_and_return
nop

// Classify pedal: r4 = 1 (released), 2 (pressed), 0 (deadband).
cf_classify_pedal:
mov #0x0,r4
mov.w @(0x10,r6),r0
extu.w r0,r1
cmp/hi r1,r2
bt cf_test_pressed
cmp/hi r1,r3
bt cf_test_pressed
mov #0x1,r4
bra cf_state_machine
nop
cf_test_pressed:
mov.w @(0x12,r6),r0
extu.w r0,r1
cmp/hs r1,r2
bf cf_state_machine
cmp/hs r1,r3
bf cf_state_machine
mov #0x2,r4

cf_state_machine:
mov #0x0,r0
mov.b r0,@(0x8,r5)
mov.b @(0x4,r5),r0
extu.b r0,r7
mov r7,r0
cmp/eq 0x0,r0
bt cf_phase_wait_release
cmp/eq 0x1,r0
bt cf_phase_armed
cmp/eq 0x2,r0
bt cf_phase_wait_release
// Corrupt phase -> reset to IDLE_WAIT_RELEASE.
mov #0x0,r0
mov.b r0,@(0x4,r5)
mov.b r0,@(0x5,r5)
bra cf_mirror_and_return
nop

// Phase 0 (IDLE_WAIT_RELEASE) or Phase 2 (PRESSED_LATCHED): wait for released.
cf_phase_wait_release:
mov r4,r0
cmp/eq 0x1,r0
bf cf_clear_debounce
mov.b @(0x5,r5),r0
extu.b r0,r2
add 0x1,r2
mov r6,r1
add 0x15,r1
mov.b @r1,r0
extu.b r0,r3
cmp/hs r3,r2
bf cf_store_debounce
mov #0x1,r0
mov.b r0,@(0x4,r5)
mov #0x0,r0
mov.b r0,@(0x5,r5)
bra cf_mirror_and_return
nop

// Phase 1 (ARMED_RELEASED): wait for deliberate press to advance cyclic slot.
cf_phase_armed:
mov r4,r0
cmp/eq 0x2,r0
bf cf_clear_debounce
mov.b @(0x5,r5),r0
extu.b r0,r2
add 0x1,r2
mov r6,r1
add 0x15,r1
mov.b @r1,r0
extu.b r0,r3
cmp/hs r3,r2
bf cf_store_debounce

// Debounced tap complete -> cyclic advance (active + 1) % 5.
mov.l @(cf_selector_state,pc),r1
mov.b @r1,r0
extu.b r0,r4
add 0x1,r4
mov #0x5,r0
cmp/hs r0,r4
bf cf_do_commit
mov #0x0,r4
cf_do_commit:
mov.l @(cf_limiter_commit,pc),r0
jsr @r0
nop
mov.l @(cf_selector_state,pc),r1
mov.b @r1,r0
extu.b r0,r4
add 0x1,r4
mov r4,r0
mov.b r0,@(0x4,r1)
mov #0x1,r0
mov.b r0,@(0x5,r1)
mov #0x0,r0
mov.b r0,@(0x6,r1)
mov.l @(cf_ram_base,pc),r5
mov #0x2,r0
mov.b r0,@(0x4,r5)
mov #0x0,r0
mov.b r0,@(0x5,r5)
mov #0x2,r0
mov.b r0,@(0x9,r5)
bra cf_arm_tach_if_allowed
nop

cf_store_debounce:
mov r2,r0
mov.b r0,@(0x5,r5)
bra cf_mirror_and_return
nop

cf_clear_debounce:
mov #0x0,r0
mov.b r0,@(0x5,r5)
bra cf_mirror_and_return
nop

// Mode 2: ASCD committed. Record source=1, clear cf transient, arm tach if
// enabled, stationary, and engine stopped.
cf_mode_ascd_commit:
mov #0x0,r0
mov.b r0,@(0x4,r5)
mov.b r0,@(0x5,r5)
mov #0x1,r0
mov.b r0,@(0x9,r5)
mov.l @(cf_selector_state,pc),r1
mov.b @r1,r0
extu.b r0,r4
add 0x1,r4
mov.l @(cf_rpm_fine,pc),r1
mov.w @r1,r0
extu.w r0,r0
tst r0,r0
bf cf_mirror_and_return
mov.l @(cf_rpm_coarse,pc),r1
mov.b @r1,r0
extu.b r0,r0
tst r0,r0
bf cf_mirror_and_return
mov.b @r5,r0
and 0x3,r0
cmp/eq 0x3,r0
bf cf_mirror_and_return

cf_arm_tach_if_allowed:
mov.l @(cf_config_base,pc),r6
bsr cf_validate_cfg_local
nop
tst r0,r0
bt cf_mirror_and_return
mov.b @(0x5,r6),r0
tst 0x4,r0
bt cf_mirror_and_return
mov.b @(0x6,r6),r0
tst 0x4,r0
bt cf_mirror_and_return
mov r6,r1
add 0x14,r1
mov.b @r1,r0
extu.b r0,r0
tst r0,r0
bt cf_mirror_and_return
mov.b r0,@(0x6,r5)
mov r4,r0
mov.b r0,@(0x7,r5)

cf_mirror_and_return:
mov.l @(cf_selector_state,pc),r5
mov.b @r5,r4
mov.l @(cf_diag_status,pc),r1
mov.b @r1,r0
mov #0x7F,r2
and r2,r0
tst r4,r4
bt cf_store_mirror
mov #-0x80,r2
or r2,r0
cf_store_mirror:
mov.b r0,@r1
lds.l @r15+,pr
rts
nop

// Local helper: validate MSCF v1 header at r6; returns r0=1 valid, 0 invalid.
// Clobbers r0, r1, r2. Preserves r4, r5, r6, r7.
cf_validate_cfg_local:
mov.l @r6,r1
mov.l @(cf_magic_word,pc),r2
cmp/eq r2,r1
bf cf_cfg_bad
mov.b @(0x4,r6),r0
cmp/eq 0x1,r0
bf cf_cfg_bad
mov.l @(0x1C,r6),r1
mov.l @(cf_sentinel_word,pc),r2
cmp/eq r2,r1
bf cf_cfg_bad
mov.l @(0x18,r6),r1
tst r1,r1
bf cf_cfg_bad
mov r6,r1
add 0x16,r1
mov.w @r1,r0
extu.w r0,r0
tst r0,r0
bf cf_cfg_bad
mov r6,r1
add 0x15,r1
mov.b @r1,r0
extu.b r0,r0
tst r0,r0
bt cf_cfg_bad
mov.w @(0x10,r6),r0
extu.w r0,r1
mov.w @(0x12,r6),r0
extu.w r0,r2
cmp/hi r1,r2
bf cf_cfg_bad
mov #0x1,r0
rts
nop
cf_cfg_bad:
mov #0x0,r0
rts
nop

.align 4
cf_ram_base:
.long 0xFFFF6000
cf_config_base:
.long 0x000D6800
cf_selector_state:
.long 0xFFFF5D00
cf_limiter_commit:
.long 0x000D3660
cf_diag_status:
.long 0xFFFF2A84
cf_rpm_fine:
.long 0xFFFF11EE
cf_rpm_coarse:
.long 0xFFFF11BC
cf_port_state:
.long 0xFFFF4185
cf_hcan1_state:
.long 0xFFFF4195
cf_brake_byte:
.long 0xFFFF2451
cf_app1_addr:
.long 0xFFFF269E
cf_app2_addr:
.long 0xFFFF26A2
cf_magic_word:
.long 0x4D534346
cf_sentinel_word:
.long 0xA55A5AA5

// ---------------------------------------------------------------------------
// 4. cruise_free_ascd_enabled @ 0x000D6BA0 (64 bytes)
// Returns r0 = 1 if MSCF config is valid and flags.bit0 (ASCD) is set;
// otherwise clears ASCD transient bytes (0xFFFF5D01..03) and returns r0 = 0.
// ---------------------------------------------------------------------------
.org 0x000D6BA0
cruise_free_ascd_enabled:
sts.l pr,@-r15
mov.l @(ascd_en_cfg,pc),r6
bsr cf_validate_cfg_local
nop
tst r0,r0
bt ascd_en_disabled
mov.b @(0x5,r6),r0
and 0x1,r0
tst r0,r0
bf ascd_en_return
ascd_en_disabled:
mov.l @(ascd_en_sel,pc),r1
mov #0x0,r0
mov.b r0,@(0x1,r1)
mov.b r0,@(0x2,r1)
mov.b r0,@(0x3,r1)
ascd_en_return:
lds.l @r15+,pr
rts
nop

.align 4
ascd_en_cfg:
.long 0x000D6800
ascd_en_sel:
.long 0xFFFF5D00
