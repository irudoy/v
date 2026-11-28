// Selector host for JK08A five-slot map switching with stationary menu,
// moving cruise direct gesture, and cruise-free brake+APP arbitration.
//
// Calls the displaced stock ASCD host first, validates active index and
// feedback state, samples ASCD MAIN, and delegates stationary menu + arbitration
// to cruise_free_menu(r4 = (main << 1) | feedback_active):
//   r0 = 0x00   proceed to moving ASCD SET/CANCEL gesture
//   r0 = 0x80+m hand off mode m (0, 1, 3, 4) directly to cruise_free_step(r4)
//
// Uses caller-saved r0..r7 and preserves PR and stack layout.

.org 0x000D2108
selector_host:
sts.l pr,@-r15
mov.l @(host_stock_function,pc),r0
jsr @r0
nop
mov.l @(host_selector_state,pc),r5

// An invalid published index fails closed through the complete limiter commit.
mov.b @r5,r4
extu.b r4,r4
mov #0x5,r0
cmp/hs r0,r4
bf host_feedback_validate
mov #0x0,r4
mov.l @(host_limiter_commit,pc),r0
jsr @r0
nop
bra host_finalize_block
nop

// Validate feedback state; record feedback_active in r4 bit 0.
host_feedback_validate:
mov.b @(0x5,r5),r0
cmp/eq 0x0,r0
bt host_feedback_idle
cmp/eq 0x1,r0
bt host_feedback_active
cmp/eq 0x2,r0
bf host_clear_all_transient
host_feedback_active:
mov.b @(0x4,r5),r0
cmp/eq 0x0,r0
bt host_clear_all_transient
mov #0x6,r1
cmp/hs r1,r0
bt host_clear_all_transient
mov #0x1,r4
bra host_read_main
nop

host_feedback_idle:
mov.l @(0x4,r5),r0
tst r0,r0
bf host_clear_all_transient
mov #0x0,r4

// Sample ASCD MAIN bit into r4 bit 1 (ignored inside helper if ascd_enabled=0).
host_read_main:
mov.l @(host_ascd_status,pc),r1
mov.b @r1,r0
tst 0x80,r0
bt host_call_menu
add 0x2,r4
host_call_menu:
mov.l @(host_cf_menu,pc),r0
jsr @r0
nop
mov.l @(host_selector_state,pc),r5
tst 0x80,r0
bt host_validate_moving
and 0x0F,r0
mov r0,r4
bra host_finalize
nop

// Moving ASCD path (ascd_enabled=1, MAIN=0, feedback_active=0, menu idle).
// Note: when sel[1]==0, cruise_free_menu already verified sel[2]==sel[3]==0.
host_validate_moving:
mov r5,r1
add 0x1,r1
mov.b @r1+,r6
mov.b @r1+,r2
mov.b @r1,r3
mov r6,r0
tst r0,r0
bt host_load_codes
mov #0x6,r0
cmp/hs r0,r2
bt host_abort_selector
mov #0x64,r0
cmp/hs r0,r3
bt host_abort_selector
mov r6,r0
cmp/eq 0x1,r0
bt host_validate_armed
cmp/eq 0x2,r0
bf host_abort_selector
host_validate_armed:
tst r3,r3
bt host_abort_selector
// Timeout expiration wins over the transition on the same invocation.
add 0x1,r3
mov #0x64,r0
cmp/hs r0,r3
bt host_abort_selector
mov r3,r0
mov.b r0,@(0x3,r5)

host_load_codes:
mov.l @(host_current_code,pc),r1
mov.b @r1+,r4
mov.b @r1,r7
mov r6,r0
tst r0,r0
bt host_phase_idle
cmp/eq 0x1,r0
bt host_phase_set

host_phase_cancel:
mov r7,r0
cmp/eq 0x2,r0
bf host_abort_selector
mov r4,r0
cmp/eq 0x2,r0
bt host_finalize_block
cmp/eq 0x8,r0
bf host_abort_selector
add 0x1,r2
mov #0x6,r0
cmp/hs r0,r2
bt host_abort_selector
mov r2,r0
mov.b r0,@(0x2,r5)
mov #0x1,r0
mov.b r0,@(0x1,r5)
bra host_finalize_block
nop

host_phase_idle:
mov r7,r0
cmp/eq 0x20,r0
bf host_finalize_idle
mov r4,r0
cmp/eq 0x8,r0
bf host_finalize_idle
mov #0x1,r0
mov.b r0,@(0x1,r5)
mov.b r0,@(0x3,r5)
bra host_finalize_block
nop

host_phase_set:
mov r7,r0
cmp/eq 0x8,r0
bf host_abort_selector
mov r4,r0
cmp/eq 0x8,r0
bt host_finalize_block
cmp/eq 0x2,r0
bt host_set_to_cancel
cmp/eq 0x20,r0
bf host_abort_selector
mov r2,r0
tst r0,r0
bt host_abort_selector
mov r2,r4
add -0x1,r4
mov.l @(host_limiter_commit,pc),r0
jsr @r0
nop
mov.l @(host_selector_state,pc),r5
mov r4,r0
add 0x1,r0
mov.b r0,@(0x4,r5)
mov #0x1,r0
mov.b r0,@(0x5,r5)
mov #0x2,r4
bra host_finalize
nop

host_set_to_cancel:
mov #0x2,r0
mov.b r0,@(0x1,r5)
bra host_finalize_block
nop

host_clear_all_transient:
mov #0x0,r0
mov.b r0,@(0x4,r5)
mov.b r0,@(0x5,r5)
mov.b r0,@(0x6,r5)
host_abort_selector:
mov #0x0,r0
mov.b r0,@(0x1,r5)
mov.b r0,@(0x2,r5)
mov.b r0,@(0x3,r5)
host_finalize_block:
mov #0x1,r4
bra host_finalize
nop

host_finalize_idle:
mov #0x0,r4
host_finalize:
mov.l @(host_cf_finalize,pc),r0
jsr @r0
nop
lds.l @r15+,pr
rts
nop

.org 0x000D2254
host_stock_function:
.long 0x000D09D8
host_selector_state:
.long 0xFFFF5D00
host_current_code:
.long 0xFFFF2A85
host_ascd_status:
.long 0xFFFF41AE
host_limiter_commit:
.long 0x000D3660
host_cf_menu:
.long 0x000D6E20
host_cf_finalize:
.long 0x000D6900
