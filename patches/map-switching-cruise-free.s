// JK08A cruise-free Map Switching selector, stationary 0x284 latch, and
// startup/arbitration helpers.
//
// Dedicated expansion RAM: 0xFFFF6000..0xFFFF601F (32 bytes):
//   +0x00  stationary_flags (bit0=observed, bit1=stationary_valid)
//   +0x01  stationary_age   (10.24 ms ticks since last 0x284 frame, 0xFF init)
//   +0x02  last_raw_speed   (BE16 raw payload[4:6] from 0x284, 0xFFFF init)
//   +0x04  cf_phase         (0=IDLE_WAIT_RELEASE, 1=ARMED_ENTER, 2=ACTIVE_PRESSED, 3=ACTIVE_RELEASED)
//   +0x05  cf_debounce      (consecutive ticks meeting target pedal state)
//   +0x06  tach_mode        (0=OFF, 1=STATIONARY_MENU, 2=BRAKE_APP_RPM0)
//   +0x07  tach_slot        (1..5 active tach display slot, 0=inactive)
//   +0x08  cf_last_reason   (last block/abort reason code 0..6)
//   +0x09  active_source    (0=startup, 1=ASCD_moving, 2=brake_app, 3=ASCD_menu)
//   +0x0A  menu_phase       (0=IDLE, 1=HOLDING_CANCEL, 2=ACTIVE)
//   +0x0B  menu_slot        (1..5 candidate slot in stationary menu, 0=inactive)
//   +0x0C  menu_timer       (BE16 hold/inactivity counter in 51.2 ms ticks)
//   +0x0E  cf_selected_slot (1..5 candidate slot in brake+APP mode, 0=inactive)
//
// MSCF v2 configuration block sits at 0x000D6800..0x000D681F (32 bytes).
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
mov.l @(stat_config_addr,pc),r6
bsr cf_validate_cfg_local
nop
tst r0,r0
bt stat_return

mov.l @(stat_port_state,pc),r1
mov.b @r1,r0
tst 0x80,r0
bt stat_reset_unobserved
mov.l @(stat_hcan1_state,pc),r1
mov.b @r1,r0
tst 0x1,r0
bt stat_reset_unobserved

mov.l @(stat_rx_state,pc),r1
mov.b @r1,r0
tst 0x8,r0
bt stat_no_new_frame

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
mov.b @(0x7,r6),r0
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
stat_config_addr:
.long 0x000D6800
stat_port_state:
.long 0xFFFF4185
stat_hcan1_state:
.long 0xFFFF4195
stat_rx_state:
.long 0xFFFF3B37
stat_rx_raw_hi:
.long 0xFFFF3B3D

// ---------------------------------------------------------------------------
// 3. cruise_free_step @ 0x000D6900 (through cf_commit_with_mil & validator)
// Entry called by selector_host with r4 mode:
//   0 = idle -> run Mode 3 stateful RPM==0 brake+APP selector, mirror active bit
//   1 = hard block -> clear cf + menu + tach, reason=6, mirror
//   2 = moving ASCD committed -> source=1, clear cf + menu + tach, mirror
//   3 = menu owned tick -> clear brake+APP only (keep menu + tach), reason=6, mirror
//   4 = feedback active -> if cf_phase in (2,3) continue Mode 3, else clear brake+APP, reason=6
// ---------------------------------------------------------------------------
.org 0x000D6900
cruise_free_step:
sts.l pr,@-r15
mov.l @(cf_ram_base,pc),r5
mov.l @(cf_config_base,pc),r6
bsr cf_validate_cfg_local
nop
tst r0,r0
bt cf_fail_config

mov r4,r0
cmp/eq 0x1,r0
bt cf_mode_hard_block
cmp/eq 0x2,r0
bt cf_mode_ascd_commit
cmp/eq 0x3,r0
bt cf_mode_menu_block
cmp/eq 0x4,r0
bf cf_mode_run_check
mov.b @(0x4,r5),r0
tst 0x2,r0
bt cf_mode_menu_block

cf_mode_run_check:
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

// Precondition 2: live stationary contract.
bsr 0x000D6D1C
nop
bf cf_fail_stationary

// Precondition 3: brake switch (FFFF2451.7). Release while active (phase 2/3) commits.
mov.l @(cf_brake_byte,pc),r1
mov.b @r1,r0
tst 0x80,r0
bt cf_brake_released_check

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

// Mid-body handlers & fail trampolines.
cf_mode_hard_block:
mov #0x6,r0
mov.b r0,@(0x8,r5)
bra cf_clear_all_and_mirror
nop
cf_mode_ascd_commit:
mov #0x1,r0
mov.b r0,@(0x9,r5)
cf_clear_all_and_mirror:
mov #0x0,r0
mov.w r0,@(0x4,r5)
mov.w r0,@(0x6,r5)
mov.w r0,@(0xA,r5)
mov.l r0,@(0xC,r5)
bra cf_mirror_and_return
nop
cf_mode_menu_block:
mov #0x6,r0
mov.b r0,@(0x8,r5)
mov #0x0,r0
mov.w r0,@(0x4,r5)
mov.b r0,@(0xE,r5)
bra cf_mirror_and_return
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
cf_clear_mode3:
mov #0x0,r0
mov.w r0,@(0x4,r5)
mov.b r0,@(0xE,r5)
mov.b @(0x6,r5),r0
cmp/eq 0x2,r0
bf cf_mirror_and_return
mov #0x0,r0
mov.w r0,@(0x6,r5)
bra cf_mirror_and_return
nop

// Brake released: commit cf_selected_slot if phase in (2,3) and slot in 1..5.
cf_brake_released_check:
mov.b @(0x4,r5),r0
tst 0x2,r0
bt cf_fail_brake
mov.b @(0xE,r5),r0
extu.b r0,r4
add -0x1,r4
mov #0x5,r0
cmp/hs r0,r4
bt cf_fail_brake
mov #0x2,r7
bsr 0x000D6FC8
nop
mov #0x0,r0
mov.b r0,@(0x8,r5)
bra cf_clear_mode3
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
mov #0x4,r0
cmp/hs r0,r7
bt cf_clear_mode3
mov r7,r0
tst 0x2,r0
bt cf_check_target_pedal
mov.b @(0xE,r5),r0
extu.b r0,r1
add -0x1,r1
mov #0x5,r0
cmp/hs r0,r1
bt cf_clear_mode3

// Unified debounce: even phase (0,2) needs r4==1; odd phase (1,3) needs r4==2.
cf_check_target_pedal:
mov r7,r0
and 0x1,r0
add 0x1,r0
cmp/eq r4,r0
bf cf_clear_debounce
mov.b @(0x5,r5),r0
extu.b r0,r2
add 0x1,r2
mov r6,r1
add 0x16,r1
mov.b @r1,r0
extu.b r0,r3
cmp/hs r3,r2
bf cf_store_debounce

// Debounce met: even phases advance phase+1 (0->1, 2->3); odd phases enter or cycle.
mov r7,r0
tst 0x1,r0
bf cf_press_action
add 0x1,r7
mov r7,r0
mov.b r0,@(0x4,r5)
bra cf_clear_debounce
nop

cf_press_action:
mov r7,r0
cmp/eq 0x1,r0
bf cf_cycle_slot
// Phase 1 -> enter selection mode showing active map (no increment) + 1 MIL flash.
mov.l @(cf_selector_state,pc),r1
mov.b @r1,r0
extu.b r0,r4
add 0x1,r4
mov #0x1,r0
mov.b r0,@(0x4,r1)
mov.b r0,@(0x5,r1)
mov #0x0,r0
mov.b r0,@(0x6,r1)
bra cf_set_active_slot
nop

cf_cycle_slot:
mov.b @(0xE,r5),r0
extu.b r0,r4
add 0x1,r4
mov #0x6,r0
cmp/hs r0,r4
bf cf_set_active_slot
mov #0x1,r4

cf_set_active_slot:
mov r4,r0
mov.b r0,@(0xE,r5)
mov #0x2,r0
mov.b r0,@(0x4,r5)
mov #0x0,r0
mov.b r0,@(0x5,r5)
mov.b @(0x5,r6),r0
tst 0x4,r0
bt cf_mirror_and_return
mov #0x2,r0
mov.b r0,@(0x6,r5)
mov r4,r0
mov.b r0,@(0x7,r5)
bra cf_mirror_and_return
nop

cf_store_debounce:
mov r2,r0
mov.b r0,@(0x5,r5)
bra cf_mirror_and_return
nop

cf_clear_debounce:
mov #0x0,r0
mov.b r0,@(0x5,r5)

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

// Fixed-anchor shared helper: validate MSCF v2 record at r6; r5 = CF RAM.
// On failure clears CF[0..7] and CF[0xA..0xF] fail-closed and returns r0 = 0.
// On success returns r0 = 1. Clobbers r0, r1, r2. Preserves r4, r5, r6, r7.
.org 0x000D6AE8
cf_validate_cfg_local:
mov.l @r6,r1
mov.l @(cf_magic_word,pc),r2
cmp/eq r2,r1
bf cf_cfg_bad
mov.b @(0x4,r6),r0
cmp/eq 0x2,r0
bf cf_cfg_bad
mov.l @(0x1C,r6),r1
mov.l @(cf_sentinel_word,pc),r2
cmp/eq r2,r1
bf cf_cfg_bad
mov.l @(0x18,r6),r1
tst r1,r1
bf cf_cfg_bad
mov.b @(0x5,r6),r0
tst 0xF0,r0
bf cf_cfg_bad
mov.b @(0x6,r6),r0
tst r0,r0
bt cf_cfg_bad
mov.b @(0x7,r6),r0
extu.b r0,r1
add -0x1,r1
mov #-0x2,r2
extu.b r2,r2
cmp/hs r2,r1
bt cf_cfg_bad
mov.w @(0x14,r6),r0
tst r0,r0
bt cf_cfg_bad
mov r6,r1
add 0x16,r1
mov.b @r1+,r0
tst r0,r0
bt cf_cfg_bad
mov.b @r1,r0
tst r0,r0
bf cf_cfg_bad
mov.w @(0x8,r6),r0
extu.w r0,r1
mov.w @(0x10,r6),r0
extu.w r0,r2
cmp/hs r1,r2
bf cf_cfg_bad
mov.w @(0x12,r6),r0
extu.w r0,r1
cmp/hi r2,r1
bf cf_cfg_bad
mov.w @(0xA,r6),r0
extu.w r0,r2
cmp/hs r1,r2
bf cf_cfg_bad
mov.w @(0xC,r6),r0
extu.w r0,r2
cmp/hs r1,r2
bf cf_cfg_bad
mov #0x1,r0
rts
nop
cf_cfg_bad:
mov.l @(cf_unobserved,pc),r0
mov.l r0,@r5
mov #0x0,r0
mov.l r0,@(0x4,r5)
mov.w r0,@(0xA,r5)
mov.l r0,@(0xC,r5)
rts
nop

.align 4
cf_ram_base:
.long 0xFFFF6000
cf_config_base:
.long 0x000D6800
cf_selector_state:
.long 0xFFFF5D00
cf_diag_status:
.long 0xFFFF2A84
cf_rpm_fine:
.long 0xFFFF11EE
cf_rpm_coarse:
.long 0xFFFF11BC
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
cf_unobserved:
.long 0x00FFFFFF

// ---------------------------------------------------------------------------
// 4. cruise_free_ascd_enabled @ 0x000D6BA0 (64 bytes)
// Validates MSCF v2 and returns r0 = 1 if flags.bit0 (ASCD) is set (leaving
// r5 = CF RAM and r6 = MSCF config). Otherwise clears ASCD transient bytes
// (sel[1..3]), menu state (cf[0xA..0xD]), and menu tach (if tach_mode==1)
// and returns r0 = 0.
// ---------------------------------------------------------------------------
.org 0x000D6BA0
cruise_free_ascd_enabled:
sts.l pr,@-r15
mov.l @(ascd_en_cf_ram,pc),r5
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
mov.w r0,@(0xA,r5)
mov.w r0,@(0xC,r5)
mov.b @(0x6,r5),r0
cmp/eq 0x1,r0
mov #0x0,r0
bf ascd_en_return
mov.w r0,@(0x6,r5)
ascd_en_return:
lds.l @r15+,pr
rts
nop

.align 4
ascd_en_cf_ram:
.long 0xFFFF6000
ascd_en_cfg:
.long 0x000D6800
ascd_en_sel:
.long 0xFFFF5D00
