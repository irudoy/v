// JK08A EcuTek-style stationary cruise map-switching menu (Mode 1) and shared
// commit+MIL helper.
//
// Placed at c_start + 0x620..0x800 (0x000D6E20..0x000D7000 on JK08A, 480 bytes).
// Called from selector_host with r4 = (main_pressed << 1) | feedback_active.
//
// Return value r0:
//   0x00  proceed to moving ASCD direct SET/CANCEL gesture in selector_host
//   0x80  hand off r4=0 (idle -> Mode 3 brake+APP) to cruise_free_step
//   0x81  hand off r4=1 (hard block) to cruise_free_step
//   0x83  hand off r4=3 (menu owned tick) to cruise_free_step
//   0x84  hand off r4=4 (feedback active) to cruise_free_step
//
// Uses caller-saved r0..r7 and preserves PR.

.org 0x000D6E20
cruise_free_menu:
sts.l pr,@-r15
mov.l r4,@-r15
bsr 0x000D6BA0
nop
mov.l @r15+,r7
tst r0,r0
bt menu_ret_idle_or_fb

// ASCD enabled: MAIN pressed aborts moving ASCD, menu, and brake+APP.
mov r7,r0
tst 0x2,r0
bf menu_abort_sel

// If moving ASCD gesture is already armed (sel[1] != 0), let it finish unless
// feedback is active. If sel[1] == 0, ensure sel[2..3] are clean.
mov.l @(menu_sel_ram,pc),r1
mov.b @(0x1,r1),r0
tst r0,r0
bt menu_check_idle_sel
mov r7,r0
tst 0x1,r0
bf menu_abort_sel
bra menu_ret_zero
nop

menu_check_idle_sel:
mov.b @(0x2,r1),r0
mov r0,r2
mov.b @(0x3,r1),r0
or r2,r0
tst r0,r0
bf menu_abort_sel

// Precompute r2 = accel_pressed (0/1) first (cf_accel_pressed clobbers r3),
// then r3 = stationary_live (0/1) (cf_stationary_live preserves r2).
mov #0x0,r2
bsr 0x000D6D5C
nop
bf menu_accel_done
mov #0x1,r2
menu_accel_done:
mov #0x0,r3
bsr 0x000D6D1C
nop
bf menu_stat_done
mov #0x1,r3
menu_stat_done:

// Load ASCD button bytes: r4 = current, r1 = previous.
mov.l @(menu_current_code,pc),r1
mov.b @r1+,r4
extu.b r4,r4
mov.b @r1,r1
extu.b r1,r1

// Dispatch menu_phase (cf[0xA]): 0=IDLE, 1=HOLDING_CANCEL, 2=ACTIVE.
mov.b @(0xA,r5),r0
cmp/eq 0x0,r0
bt menu_phase_idle
cmp/eq 0x1,r0
bt menu_phase_holding
cmp/eq 0x2,r0
bt menu_phase_active
bra menu_abort_active
nop

menu_phase_idle:
tst r3,r3
bt menu_to_moving
mov r7,r0
tst 0x1,r0
bf menu_ret_fb
tst r2,r2
bf menu_ret_idle
mov.b @(0x4,r5),r0
tst 0x2,r0
bf menu_ret_idle
mov r4,r0
cmp/eq 0x2,r0
bf menu_ret_idle
mov #0x1,r0
mov.w r0,@(0xC,r5)
mov.b @(0x6,r6),r0
cmp/eq 0x1,r0
bt menu_enter_active
mov #0x1,r0
mov.b r0,@(0xA,r5)
mov #0x0,r0
mov.b r0,@(0xB,r5)
bra menu_ret_owned
nop

menu_abort_sel:
mov.l @(menu_sel_ram,pc),r1
mov #0x0,r0
mov.b r0,@(0x1,r1)
mov.b r0,@(0x2,r1)
mov.b r0,@(0x3,r1)
mov #-0x7F,r0
bra menu_exit
nop

menu_to_moving:
mov r7,r0
tst 0x1,r0
bf menu_ret_fb
menu_ret_zero:
mov #0x0,r0
bra menu_exit
nop

menu_ret_idle_or_fb:
mov r7,r0
tst 0x1,r0
bt menu_ret_idle
menu_ret_fb:
mov #-0x7C,r0
bra menu_exit
nop
menu_ret_idle:
mov #-0x80,r0
bra menu_exit
nop

menu_phase_holding:
tst r2,r2
bf menu_holding_drop
tst r3,r3
bt menu_holding_drop
mov r7,r0
tst 0x1,r0
bf menu_holding_drop
mov r4,r0
cmp/eq 0x2,r0
bt menu_holding_inc
menu_holding_drop:
mov #0x0,r0
mov.w r0,@(0xA,r5)
mov.w r0,@(0xC,r5)
tst r2,r2
bf menu_ret_owned
tst r3,r3
bt menu_to_moving
bra menu_ret_idle_or_fb
nop

menu_holding_inc:
mov.w @(0xC,r5),r0
extu.w r0,r2
add 0x1,r2
mov r2,r0
mov.w r0,@(0xC,r5)
mov.b @(0x6,r6),r0
extu.b r0,r1
cmp/hs r1,r2
bf menu_ret_owned

menu_enter_active:
mov.l @(menu_sel_ram,pc),r1
mov.b @r1,r0
extu.b r0,r4
add 0x1,r4
mov #0x1,r0
mov.b r0,@(0x4,r1)
mov.b r0,@(0x5,r1)
mov #0x0,r0
mov.b r0,@(0x6,r1)
mov #0x2,r0
mov.b r0,@(0xA,r5)
bra menu_store_slot
nop

menu_phase_active:
mov.b @(0xB,r5),r0
extu.b r0,r7
tst r2,r2
bf menu_abort_active
mov r7,r0
add -0x1,r0
mov #0x5,r2
cmp/hs r2,r0
bt menu_abort_active
tst r3,r3
bt menu_commit_active
mov r4,r0
tst r0,r0
bt menu_abort_active
cmp/eq r1,r4
bt menu_tick_timeout
cmp/eq 0x2,r0
bt menu_commit_active
cmp/eq 0x10,r0
bt menu_step_up
cmp/eq 0x8,r0
bf menu_tick_timeout

// COAST/SET (0x08) edge: -1 with wrap 1 -> 5.
mov r7,r4
add -0x1,r4
tst r4,r4
bf menu_store_slot
mov #0x5,r4
bra menu_store_slot
nop

menu_tick_timeout:
mov.w @(0xC,r5),r0
extu.w r0,r2
add 0x1,r2
mov r2,r0
mov.w r0,@(0xC,r5)
mov.w @(0x14,r6),r0
extu.w r0,r1
cmp/hs r1,r2
bt menu_commit_active
mov r7,r4
bra menu_update_tach
nop

// RES/ACCEL (0x10) edge: +1 with wrap 5 -> 1.
menu_step_up:
mov r7,r4
add 0x1,r4
mov #0x6,r0
cmp/hs r0,r4
bf menu_store_slot
mov #0x1,r4

menu_store_slot:
mov r4,r0
mov.b r0,@(0xB,r5)
mov #0x0,r0
mov.w r0,@(0xC,r5)

menu_update_tach:
mov.b @(0x5,r6),r0
tst 0x4,r0
bt menu_clear_tach_owned
mov #0x1,r0
mov.b r0,@(0x6,r5)
mov r4,r0
mov.b r0,@(0x7,r5)
bra menu_ret_owned
nop

menu_commit_active:
mov r7,r4
add -0x1,r4
mov #0x3,r7
bsr cf_commit_with_mil
nop

menu_abort_active:
mov #0x0,r0
mov.w r0,@(0xA,r5)
mov.w r0,@(0xC,r5)
menu_clear_tach_owned:
mov #0x0,r0
mov.w r0,@(0x6,r5)

menu_ret_owned:
mov #-0x7D,r0
menu_exit:
extu.b r0,r0
lds.l @r15+,pr
rts
nop

// Fixed-anchor shared helper @ c_start + 0x7C8 (56 bytes):
// Commit slot index r4 (0..4), queue 1 MIL flash, set cf[9] = r7 (active_source),
// and reload r5 = cf_ram. Clobbers r0, r1, r4.
.org 0x000D6FC8
cf_commit_with_mil:
sts.l pr,@-r15
mov.l r7,@-r15
mov.l @(menu_limiter_commit,pc),r0
jsr @r0
nop
mov.l @(menu_sel_ram,pc),r1
mov #0x1,r0
mov.b r0,@(0x4,r1)
mov.b r0,@(0x5,r1)
mov #0x0,r0
mov.b r0,@(0x6,r1)
mov.l @(menu_cf_ram,pc),r5
mov.l @r15+,r0
mov.b r0,@(0x9,r5)
lds.l @r15+,pr
rts
nop

.align 4
menu_cf_ram:
.long 0xFFFF6000
menu_sel_ram:
.long 0xFFFF5D00
menu_current_code:
.long 0xFFFF2A85
menu_limiter_commit:
.long 0x000D3660
