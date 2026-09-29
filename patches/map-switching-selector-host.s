// Selector host for the exact JK08A five-slot map-switching pilot.
//
// The wrapper calls the displaced stock host first, validates all selector
// state, blocks input while visual feedback is active, and invokes the atomic
// limiter commit only after a complete SET/CANCEL gesture. It mirrors map 1
// versus maps 2-5 in the prototype diagnostic bit without changing stock ASCD
// input or control state.
//
// The function uses caller-saved r0..r7 and preserves PR and the stack layout.

.org 0x000D2108
selector_host:
sts.l pr,@-r15
mov.l @(host_stock_function,pc),r0
jsr @r0
nop
mov.l @(host_selector_state,pc),r5

// An invalid published index fails closed through the complete limiter commit.
mov.b @r5,r4
mov #0x5,r0
cmp/hs r0,r4
bf host_feedback_validate
mov #0x0,r4
mov.l @(host_limiter_commit,pc),r0
jsr @r0
nop
bra host_mirror
nop

// Feedback phase 1 or 2 blocks selector input. Invalid feedback is cleared.
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
mov r5,r1
add 0x4,r1
mov.l @r1,r0
tst r0,r0
bf host_clear_all_transient

// Validate phase, count, and elapsed tick invariants before accepting input.
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
cmp/eq 0x0,r0
bf host_abort_selector

// The MAIN switch bit of the stock ASCD flag byte aborts an armed gesture.
host_check_ascd:
mov.l @(host_ascd_status,pc),r1
mov.b @r1,r0
mov #-0x80,r1
tst r1,r0
bf host_abort_selector

// Timeout expiration wins over the transition on the same invocation.
mov r6,r0
cmp/eq 0x0,r0
bt host_load_codes
add 0x1,r3
mov #0x64,r0
cmp/hs r0,r3
bt host_abort_selector
mov r3,r0
mov.b r0,@(0x3,r5)

host_load_codes:
mov.l @(host_current_code,pc),r1
mov.b @r1,r4
add 0x1,r1
mov.b @r1,r7
mov r6,r0
cmp/eq 0x0,r0
bt host_phase_idle
cmp/eq 0x1,r0
bt host_phase_set
bra host_phase_cancel
nop

host_phase_idle:
mov r7,r0
cmp/eq 0x20,r0
bf host_mirror
mov r4,r0
cmp/eq 0x8,r0
bf host_mirror
mov #0x1,r0
mov.b r0,@(0x1,r5)
mov #0x1,r0
mov.b r0,@(0x3,r5)
bra host_mirror
nop

host_phase_set:
mov r7,r0
cmp/eq 0x8,r0
bf host_abort_selector
mov r4,r0
cmp/eq 0x8,r0
bt host_mirror
cmp/eq 0x2,r0
bt host_set_to_cancel
cmp/eq 0x20,r0
bf host_abort_selector
mov r2,r0
cmp/eq 0x0,r0
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
bra host_mirror
nop

host_set_to_cancel:
mov #0x2,r0
mov.b r0,@(0x1,r5)
bra host_mirror
nop

host_phase_cancel:
mov r7,r0
cmp/eq 0x2,r0
bf host_abort_selector
mov r4,r0
cmp/eq 0x2,r0
bt host_mirror
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
bra host_mirror
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

host_mirror:
mov.l @(host_selector_state,pc),r5
mov.b @r5,r4
mov.l @(host_diagnostic_status,pc),r1
mov.b @r1,r0
mov #0x7F,r2
and r2,r0
tst r4,r4
bt host_store_mirror
mov #-0x80,r2
or r2,r0
host_store_mirror:
mov.b r0,@r1
lds.l @r15+,pr
rts
nop

.org 0x000D2258
host_stock_function:
.long 0x000D09D8
host_selector_state:
.long 0xFFFF5D00
host_current_code:
.long 0xFFFF2A85
host_ascd_status:
.long 0xFFFF41AE
host_diagnostic_status:
.long 0xFFFF2A84
host_limiter_commit:
.long 0x000D3660
