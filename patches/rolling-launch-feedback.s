// Dashboard feedback arbitration for the combined JK08A runtime.
//
// The map-switching feedback wrapper and pulse engine always run first. A
// nonzero map-feedback state owns the serialized frame for this invocation.
// Otherwise Rolling Launch replaces the complete three-bit ASCD field:
//   IDLE with a failed CANCEL-held attempt - state 6
//   ACTIVE                            - state 7
//   COOLDOWN                          - state 0
// The field is the latched stock ASCD display state. State 6 is the stock
// fault state: CRUISE is lit and the SET lamp blinks on its own timer, which
// the exact target shows as SET following CRUISE. State 7 has no stock
// producer.
// Normal IDLE and corrupt phases preserve the stock serializer result.

.org 0x000D41E0
rolling_launch_feedback_arbiter:
sts.l pr,@-r15
mov.l @(rl_feedback_selector_state,pc),r1
add 0x4,r1
mov.l @r1,r0
mov.l r0,@-r15
mov.l @(rl_feedback_base_wrapper,pc),r0
jsr @r0
nop
mov.l @r15+,r0
tst r0,r0
bf rl_feedback_return

mov.l @(rl_feedback_state,pc),r1
mov.b @r1,r0
cmp/eq 0x0,r0
bt rl_feedback_idle
cmp/eq 0x1,r0
bt rl_feedback_active
cmp/eq 0x2,r0
bf rl_feedback_return
mov #0x0,r2
bra rl_feedback_apply
nop

rl_feedback_active:
mov #0x70,r2
bra rl_feedback_apply
nop

rl_feedback_idle:
mov.b @(0x1,r1),r0
tst r0,r0
bt rl_feedback_return
mov.w @(0x2,r1),r0
extu.w r0,r0
tst 0x20,r0
bt rl_feedback_return
mov #0x60,r2

rl_feedback_apply:
mov.l @(rl_feedback_status_byte,pc),r1
mov.b @r1,r0
and 0x8F,r0
or r2,r0
mov.b r0,@r1

rl_feedback_return:
lds.l @r15+,pr
rts
nop

.org 0x000D4270
rl_feedback_base_wrapper:
.long 0x000D35E0
rl_feedback_selector_state:
.long 0xFFFF5D00
rl_feedback_state:
.long 0xFFFF5D40
rl_feedback_status_byte:
.long 0xFFFF3ADA
