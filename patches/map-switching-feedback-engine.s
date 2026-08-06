// Fail-closed CRUISE-indicator pulse engine for CAN 0x551.
//
// The function runs after the exact stock serializer. It changes only bits
// 5-6 of payload byte 5 while a structurally valid feedback sequence is
// active. Zero or incomplete frame-count configuration disables feedback,
// clears its transient state, and preserves the complete stock payload.
//
// feedback_phase_counts contains two uint8 values:
//   byte 0 - on-frame count
//   byte 1 - off-frame count
//
// The locked payload retains the hardware-tested ten-frame baseline. Complete
// compositions override the two data bytes with the manifest defaults after
// installing this unit. The function is a leaf and uses caller-saved r0..r7.

.org 0x000D3760
cruise_feedback_engine:
mov.l @(feedback_selector_state,pc),r5
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
mov r0,r7
cmp/eq 0x0,r0
bt feedback_clear
mov #0x6,r1
cmp/hs r1,r0
bt feedback_clear
mov.b @(0x6,r5),r0
extu.b r0,r1

mov.l @(feedback_status_byte,pc),r4
mov.b @r4,r0
and 0x9F,r0
mov r0,r7
mov r6,r0
cmp/eq 0x1,r0
bf feedback_status_off
mov #0x60,r0
bra feedback_status_merge
nop
feedback_status_off:
mov #0x0,r0
feedback_status_merge:
or r7,r0
mov.b r0,@r4

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
rts
nop

feedback_advance_on:
cmp/hs r2,r1
bf feedback_store_ticks
mov #0x2,r0
mov.b r0,@(0x5,r5)
mov #0x0,r0
mov.b r0,@(0x6,r5)
rts
nop

feedback_store_ticks:
mov r1,r0
mov.b r0,@(0x6,r5)
rts
nop

feedback_idle:
mov r5,r1
add 0x4,r1
mov.l @r1,r0
tst r0,r0
bt feedback_return

feedback_clear:
mov #0x0,r0
mov.b r0,@(0x4,r5)
mov.b r0,@(0x5,r5)
mov.b r0,@(0x6,r5)
mov.b r0,@(0x7,r5)
feedback_return:
rts
nop

.org 0x000D3840
feedback_selector_state:
.long 0xFFFF5D00
feedback_status_byte:
.long 0xFFFF3ADA
feedback_phase_counts:
.word 0x0A0A
