// Fail-closed multi-channel indicator pulse engine for JK08A CAN 0x551.
//
// Runs after the stock 0x551 serializer. Calls cruise_free_feedback_ext first
// to advance/interlock optional tachometer hold ticks and return the validated
// lamp mask from MSCF config:
//   bit 0 (0x01) - CRUISE/SET lamps in 0x551 byte 5 (0xFFFF3ADA, mask 0x70)
//   bit 1 (0x02) - MIL request in 0x551 byte 3 (0xFFFF3AD8, bit 5 / 0x20)
//
// Zero lamp mask, invalid MSCF config, or zero/incomplete phase counts clears
// transient feedback state and preserves the complete stock 0x551 payload.
// Preserves PR and uses caller-saved r0..r7.

.org 0x000D3760
cruise_feedback_engine:
sts.l pr,@-r15
mov.l @(feedback_cf_ext,pc),r0
jsr @r0
nop
mov.l r0,@-r15

mov.l @(feedback_selector_state,pc),r5
tst r0,r0
bt feedback_clear

mov.w @(feedback_phase_counts,pc),r2
extu.w r2,r2
tst r2,r2
bt feedback_clear
mov r2,r3
extu.b r3,r3
shlr8 r2
extu.b r2,r2
tst r2,r2
bt feedback_clear
tst r3,r3
bt feedback_clear

mov.b @(0x5,r5),r0
mov r0,r6
cmp/eq 0x0,r0
bt feedback_idle
cmp/eq 0x1,r0
bt feedback_active
cmp/eq 0x2,r0
bf feedback_clear

feedback_active:
mov.b @(0x4,r5),r0
cmp/eq 0x0,r0
bt feedback_clear
mov #0x6,r1
cmp/hs r1,r0
bt feedback_clear
mov.b @(0x6,r5),r0
extu.b r0,r1

// Channel 0: CRUISE and SET lamps (0x551 byte 5, bits 4..6).
mov.l @r15,r0
tst 0x1,r0
bt feedback_check_mil
mov.l @(feedback_status_byte,pc),r4
mov.b @r4,r0
and 0x8F,r0
mov r0,r7
mov r6,r0
cmp/eq 0x1,r0
bf feedback_status_off
mov #0x40,r0
bra feedback_status_merge
nop
feedback_status_off:
mov #0x0,r0
feedback_status_merge:
or r7,r0
mov.b r0,@r4

// Channel 1: MIL request (0x551 byte 3, bit 5, active-high 0x20).
feedback_check_mil:
mov.l @r15,r0
tst 0x2,r0
bt feedback_advance
mov.l @(feedback_mil_byte,pc),r4
mov.b @r4,r0
and 0xDF,r0
mov r0,r7
mov r6,r0
cmp/eq 0x1,r0
bf feedback_mil_store
mov #0x20,r0
or r0,r7
feedback_mil_store:
mov r7,r0
mov.b r0,@r4

feedback_advance:
add 0x1,r1
mov r6,r0
cmp/eq 0x1,r0
bt feedback_advance_on

cmp/hs r3,r1
bf feedback_store_ticks
mov.b @(0x4,r5),r0
add -0x1,r0
tst r0,r0
bt feedback_clear
mov.b r0,@(0x4,r5)
mov #0x1,r0
mov.b r0,@(0x5,r5)
mov #0x0,r0
mov.b r0,@(0x6,r5)
bra feedback_return
nop

feedback_advance_on:
cmp/hs r2,r1
bf feedback_store_ticks
mov #0x2,r0
mov.b r0,@(0x5,r5)
mov #0x0,r0
mov.b r0,@(0x6,r5)
bra feedback_return
nop

feedback_store_ticks:
mov r1,r0
mov.b r0,@(0x6,r5)
bra feedback_return
nop

feedback_idle:
mov.l @(0x4,r5),r0
tst r0,r0
bt feedback_return

feedback_clear:
mov #0x0,r0
mov.b r0,@(0x4,r5)
mov.b r0,@(0x5,r5)
mov.b r0,@(0x6,r5)
mov.b r0,@(0x7,r5)

feedback_return:
add 0x4,r15
lds.l @r15+,pr
rts
nop

.org 0x000D3840
feedback_selector_state:
.long 0xFFFF5D00
feedback_status_byte:
.long 0xFFFF3ADA
feedback_phase_counts:
.word 0x0A0A
.word 0xFFFF
feedback_mil_byte:
.long 0xFFFF3AD8
feedback_cf_ext:
.long 0x000D6BE0
