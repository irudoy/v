// Selector host for JK08A five-slot map switching with cruise-free arbitration.
//
// Calls the displaced stock ASCD host first, validates active index and
// feedback state, runs the ASCD SET/CANCEL state machine when enabled in the
// MSCF config, and hands off to cruise_free_step(r4) before returning:
//   r4 = 0  ASCD idle: run cruise-free cyclic selector, then mirror active bit
//   r4 = 1  ASCD armed/blocked or feedback active: clear cruise-free transient,
//           record arbitration reason, then mirror active bit
//   r4 = 2  ASCD committed: record ASCD source, arm optional tach if stationary
//           and stopped, clear cruise-free transient, then mirror active bit
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

// Feedback phase 1 or 2 blocks both selectors. Invalid feedback is cleared.
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
bra host_abort_selector
nop

host_feedback_idle:
mov.l @(0x4,r5),r0
tst r0,r0
bf host_clear_all_transient

// Check MSCF config bit 0 (ascd_enabled). Helper clears ASCD transient bytes
// when returning 0 (disabled or invalid config) so cruise-free can evaluate.
mov.l @(host_ascd_enabled,pc),r0
jsr @r0
nop
mov.l @(host_selector_state,pc),r5
tst r0,r0
bt host_finalize_idle

// Validate ASCD phase, count, and elapsed tick invariants.
mov r5,r1
add 0x1,r1
mov.b @r1+,r6
mov.b @r1+,r2
mov.b @r1,r3
mov #0x6,r0
cmp/hs r0,r2
bt host_abort_selector
mov #0x64,r0
cmp/hs r0,r3
bt host_abort_selector
mov r6,r0
cmp/eq 0x0,r0
bt host_validate_idle
cmp/eq 0x1,r0
bt host_validate_armed
cmp/eq 0x2,r0
bf host_abort_selector
host_validate_armed:
tst r3,r3
bt host_abort_selector
bra host_check_ascd
nop
host_validate_idle:
mov r2,r0
or r3,r0
tst r0,r0
bf host_abort_selector

// The MAIN switch bit of the stock ASCD flag byte aborts both selectors.
host_check_ascd:
mov.l @(host_ascd_status,pc),r1
mov.b @r1,r0
tst 0x80,r0
bf host_abort_selector

// Timeout expiration wins over the transition on the same invocation.
mov r6,r0
tst r0,r0
bt host_load_codes
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
host_ascd_enabled:
.long 0x000D6BA0
host_cf_finalize:
.long 0x000D6900
