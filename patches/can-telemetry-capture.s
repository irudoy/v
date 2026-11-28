// Coherent snapshot builder and mailbox submitter for exact JK08A.
//
// The entry runs with interrupts already masked by FUN_00020DFE. It validates
// the fail-closed ROM configuration, advances the base tick, applies the
// configured divider, builds the inactive frame bank, and atomically publishes
// either an active or replaceable pending snapshot.

.include "can-telemetry-identity.h"

.org 0x000D4340
telemetry_capture:
sts.l pr,@-r15
mov.l @(telemetry_capture_config,pc),r4
mov.w @r4,r0
mov.w @(telemetry_config_magic,pc),r1
cmp/eq r1,r0
bf telemetry_capture_return
mov.b @(0x2,r4),r0
cmp/eq 0x2,r0
bf telemetry_capture_return
mov.b @(0x3,r4),r0
extu.b r0,r0
mov #0x1,r1
cmp/hi r1,r0
bt telemetry_capture_return
mov.b @(0x4,r4),r0
extu.b r0,r5
cmp/eq TELEMETRY_PROFILE_ID,r0
bf telemetry_capture_return
mov #TELEMETRY_PAGE_COUNT,r6
telemetry_capture_check_pages:
mov.b @(0x5,r4),r0
extu.b r0,r0
cmp/eq r6,r0
bf telemetry_capture_return
mov.b @(0x6,r4),r0
extu.b r0,r2
tst r2,r2
bt telemetry_capture_return
mov.b @(0x7,r4),r0
tst r0,r0
bf telemetry_capture_return
mov.w @(0x8,r4),r0
extu.w r0,r0
tst r0,r0
bt telemetry_capture_return
mov.w @(telemetry_config_can_id_max,pc),r1
cmp/hi r1,r0
bt telemetry_capture_return
mov.w @(telemetry_config_crc,pc),r1
telemetry_capture_check_crc:
mov.w @(0xA,r4),r0
cmp/eq r1,r0
bf telemetry_capture_return
mov.l @(0xC,r4),r0
mov.l @(telemetry_config_integrity,pc),r1
cmp/eq r1,r0
bf telemetry_capture_return

mov.l @(telemetry_capture_state,pc),r3
mov.b @(0xB,r3),r0
cmp/eq 0x1,r0
bt telemetry_capture_enabled
cmp/eq 0x2,r0
bt telemetry_capture_return
mov.b @(0x7,r3),r0
tst 0x10,r0
bf telemetry_capture_enabled
mov.b @(0x3,r4),r0
cmp/eq 0x1,r0
bf telemetry_capture_return

telemetry_capture_enabled:
mov r6,r0
mov.b r0,@(0x4,r3)
mov r5,r0
mov.b r0,@(0x5,r3)
mov.w @(0x8,r3),r0
add 0x1,r0
mov.w r0,@(0x8,r3)
mov.b @(0xA,r3),r0
extu.b r0,r1
add 0x1,r1
cmp/hs r2,r1
bt telemetry_capture_due
mov r1,r0
mov.b r0,@(0xA,r3)
bra telemetry_capture_return
nop

telemetry_capture_due:
mov #0x0,r0
mov.b r0,@(0xA,r3)
mov.b @(0x2,r3),r0
tst r0,r0
bt telemetry_capture_idle

mov.b @(0x1,r3),r0
tst r0,r0
bt telemetry_capture_busy_bank
mov.b @(0x7,r3),r0
or 0x1,r0
mov.b r0,@(0x7,r3)
mov.b @(0xE,r3),r0
cmp/eq -0x1,r0
bt telemetry_capture_busy_bank
add 0x1,r0
mov.b r0,@(0xE,r3)

telemetry_capture_busy_bank:
mov.b @r3,r0
tst r0,r0
bt telemetry_capture_busy_bank_b
mov.l @(telemetry_capture_bank_a,pc),r4
bra telemetry_capture_busy_build
nop
telemetry_capture_busy_bank_b:
mov.l @(telemetry_capture_bank_b,pc),r4
telemetry_capture_busy_build:
bsr telemetry_build_bank
nop
mov #0x1,r0
mov.b r0,@(0x1,r3)
bra telemetry_capture_return
nop

telemetry_capture_idle:
mov.b @r3,r0
tst r0,r0
bt telemetry_capture_idle_bank_b
mov.l @(telemetry_capture_bank_a,pc),r4
bra telemetry_capture_idle_build
nop
telemetry_capture_idle_bank_b:
mov.l @(telemetry_capture_bank_b,pc),r4
telemetry_capture_idle_build:
bsr telemetry_build_bank
nop
mov.b @r3,r0
tst r0,r0
bt telemetry_capture_publish_bank_b
mov #0x0,r0
bra telemetry_capture_publish_bank
nop
telemetry_capture_publish_bank_b:
mov #0x1,r0
telemetry_capture_publish_bank:
mov.b r0,@r3
mov #0x0,r0
mov.b r0,@(0x1,r3)
mov.b r0,@(0x3,r3)
mov #0x1,r0
mov.b r0,@(0x2,r3)
bsr telemetry_request_page
nop

telemetry_capture_return:
lds.l @r15+,pr
rts
nop

.align 4
telemetry_capture_config:
.long 0x000D4E00
telemetry_capture_state:
.long 0xFFFF5E00
telemetry_capture_bank_a:
.long 0xFFFF5E20
telemetry_capture_bank_b:
.long 0xFFFF5E78
telemetry_config_integrity:
.long 0x54454C32
telemetry_config_magic:
.word 0x4354
telemetry_config_can_id_max:
.word 0x07FE
telemetry_config_crc:
.word TELEMETRY_PROFILE_CRC

.org 0x000D4460
// Slot check of the dynamic page, shared by the page build and the SET
// command. In: r1 = the slot entry, whose bits 27..24 hold the width and
// bits 23..0 the address above 0xFF000000. Out: r0 = the source pointer, or 0
// when the width is not 1, 2 or 4, the address is not a multiple of the
// width, or a byte of the slot falls outside the RAM window; r2 = the width.
// Clobbers r1.
telemetry_dynamic_slot:
mov r1,r0
shlr16 r0
shlr8 r0
and 0xF,r0
mov r0,r2
cmp/eq 0x1,r0
bt telemetry_dynamic_slot_width
cmp/eq 0x2,r0
bt telemetry_dynamic_slot_width
cmp/eq 0x4,r0
bf telemetry_dynamic_slot_invalid
telemetry_dynamic_slot_width:
add -0x1,r0
and r1,r0
tst r0,r0
bf telemetry_dynamic_slot_invalid
shll8 r1
shlr8 r1
mov.l @(telemetry_dynamic_window_start,pc),r0
cmp/hs r0,r1
bf telemetry_dynamic_slot_invalid
mov.l @(telemetry_dynamic_window_end,pc),r0
sub r2,r0
cmp/hi r0,r1
bt telemetry_dynamic_slot_invalid
// Address bit 16 selects the page base 0xFFFF0000 and its absence the base
// 0xFFFE0000. Both bases derive from RAM literals, so a relocation of the
// RAM literals moves every slot pointer with them.
mov.l r2,@-r15
mov.l @(telemetry_dynamic_page_low,pc),r2
mov.w @(telemetry_dynamic_page_low_bias,pc),r0
add r0,r2
mov.l @(telemetry_dynamic_page_high,pc),r0
sub r2,r0
and r1,r0
add r2,r0
extu.w r1,r1
add r1,r0
mov.l @r15+,r2
rts
nop
telemetry_dynamic_slot_invalid:
mov #0x0,r0
rts
nop

// CRC-16/CCITT-FALSE of command bytes 0..5. In: r4 = bytes 0..3, r5 =
// bytes 4..7. Out: r0 = the CRC. Clobbers r1, r2, r3, r6 and r7. The register
// holds the CRC in bits 31..16, so the shifted-out bit is the T bit.
telemetry_dynamic_crc:
mov #-0x1,r2
shll16 r2
mov.l @(telemetry_dynamic_crc_poly,pc),r7
mov r4,r1
mov #0x6,r6
telemetry_dynamic_crc_byte:
mov r6,r0
cmp/eq 0x2,r0
bf telemetry_dynamic_crc_load
mov r5,r1
telemetry_dynamic_crc_load:
mov r1,r0
shlr16 r0
shlr8 r0
shll16 r0
shll8 r0
xor r0,r2
shll8 r1
mov #0x8,r3
telemetry_dynamic_crc_bit:
shll r2
bf telemetry_dynamic_crc_next
xor r7,r2
telemetry_dynamic_crc_next:
dt r3
bf telemetry_dynamic_crc_bit
dt r6
bf telemetry_dynamic_crc_byte
mov r2,r0
shlr16 r0
rts
nop

.align 4
telemetry_dynamic_window_start:
.long 0x00FF0000
telemetry_dynamic_window_end:
.long 0x00FFC000
telemetry_dynamic_page_low:
.long 0xFFFE8000
telemetry_dynamic_page_high:
.long 0xFFFF0000
telemetry_dynamic_crc_poly:
.long 0x10210000
telemetry_dynamic_page_low_bias:
.word 0x8000

.org 0x000D4500
// Always construct nine fixed pages and both rotating context pages.
telemetry_build_bank:
mov.l @(telemetry_build_state,pc),r3
mov.l @(telemetry_page_table,pc),r5
mov #0x0,r6
telemetry_build_page_loop:
mov.b @(0x9,r3),r0
and 0x0F,r0
shll2 r0
shll2 r0
or r6,r0
mov.b r0,@r4
add 0x1,r4
mov #0x7,r2
mov r6,r0
cmp/eq 0x3,r0
bf telemetry_build_byte_loop
bra telemetry_build_dynamic_page
nop
telemetry_build_byte_loop:
mov.l @r5+,r1
mov.b @r1,r0
mov.b r0,@r4
add 0x1,r4
dt r2
bf telemetry_build_byte_loop
telemetry_build_page_next:
add 0x1,r6
mov r6,r0
cmp/eq 0x9,r0
bf telemetry_build_page_loop

mov.b @(0x9,r3),r0
and 0x0F,r0
shll2 r0
shll2 r0
or 0x9,r0
mov.b r0,@r4
add 0x1,r4
mov.b @(0x6,r3),r0
extu.b r0,r6
mov #0x5,r1
cmp/hs r1,r6
bf telemetry_build_context_valid
mov #0x0,r6
telemetry_build_context_valid:
mov r6,r0
mov.b r0,@r4
add 0x1,r4
mov.l @(telemetry_context_page_9_table,pc),r5
mov r6,r1
telemetry_build_context_page_9_seek:
tst r1,r1
bt telemetry_build_context_page_9_copy
add 0x18,r5
add -0x1,r1
bra telemetry_build_context_page_9_seek
nop
telemetry_build_context_page_9_copy:
mov #0x6,r2
telemetry_build_context_page_9_byte_loop:
mov.l @r5+,r1
mov.b @r1,r0
mov.b r0,@r4
add 0x1,r4
dt r2
bf telemetry_build_context_page_9_byte_loop

mov.b @(0x9,r3),r0
and 0x0F,r0
shll2 r0
shll2 r0
or 0xA,r0
mov.b r0,@r4
add 0x1,r4
mov r6,r0
mov.b r0,@r4
add 0x1,r4
mov.l @(telemetry_context_page_10_table,pc),r5
mov r6,r1
telemetry_build_context_page_10_seek:
tst r1,r1
bt telemetry_build_context_page_10_copy
add 0x18,r5
add -0x1,r1
bra telemetry_build_context_page_10_seek
nop
telemetry_build_context_page_10_copy:
mov #0x6,r2
telemetry_build_context_page_10_byte_loop:
mov.l @r5+,r1
mov.b @r1,r0
mov.b r0,@r4
add 0x1,r4
dt r2
bf telemetry_build_context_page_10_byte_loop

// Context 4 carries the knock margin minimums. Rearm all six latches right
// after their copy; interrupts stay masked, so no evaluation falls between.
mov r6,r0
cmp/eq 0x4,r0
bf telemetry_build_context_advance
mov.w @(telemetry_build_margin_idle,pc),r1
mov r3,r5
add 0x10,r5
mov #0x6,r2
telemetry_build_margin_rearm_loop:
mov.w r1,@r5
add 0x2,r5
dt r2
bf telemetry_build_margin_rearm_loop
telemetry_build_context_advance:
add 0x1,r6
mov #0x5,r1
cmp/hs r1,r6
bf telemetry_build_context_store
mov #0x0,r6
telemetry_build_context_store:
mov r6,r0
mov.b r0,@(0x6,r3)
rts
nop

.align 4
telemetry_build_state:
.long 0xFFFF5E00
telemetry_page_table:
.long 0x000D4C00
telemetry_context_page_9_table:
.long 0x000D4CFC
telemetry_context_page_10_table:
.long 0x000D4D74
telemetry_build_margin_idle:
.word 0x7FFF

.org 0x000D4600
// Knock margin latch behind the only literal of the knock slice evaluator.
// The stock evaluator runs first and leaves the offset-binary metric and the
// threshold of the evaluated channel in RAM. The wrapper repeats the stock
// comparison in biased unsigned form and keeps the per-channel minimum of
// threshold minus metric as a signed word biased by 0x8000. An exceedance
// saturates at -32768. A margin of 32767 or more never undercuts a latch, so
// the idle value 0x7FFF also reports it. Channel 0 and channels above 6
// leave the latches unchanged.
telemetry_knock_margin_wrapper:
sts.l pr,@-r15
mov.l @(telemetry_margin_stock,pc),r0
jsr @r0
nop
mov.l @(telemetry_margin_selector,pc),r1
mov.b @r1,r0
tst 0x8,r0
bt telemetry_margin_primary_channel
mov.l @(telemetry_margin_channel_alternate,pc),r1
bra telemetry_margin_channel
nop
telemetry_margin_primary_channel:
mov.l @(telemetry_margin_channel_primary,pc),r1
telemetry_margin_channel:
mov.b @r1,r0
extu.b r0,r4
tst r4,r4
bt telemetry_margin_return
mov #0x6,r1
cmp/hi r1,r4
bt telemetry_margin_return
add -0x1,r4
mov.l @(telemetry_margin_metric,pc),r1
mov r4,r0
shll2 r0
mov.l @(r0,r1),r7
mov.l @(telemetry_margin_threshold,pc),r1
mov r4,r0
shll r0
mov.w @(r0,r1),r2
extu.w r2,r2
mov.l @(telemetry_margin_bias,pc),r5
add r5,r2
mov.w @(telemetry_margin_idle,pc),r3
add 0x1,r3
cmp/hi r2,r7
bt telemetry_margin_exceeded
sub r7,r2
add r3,r2
bra telemetry_margin_compare
nop
telemetry_margin_exceeded:
sub r2,r7
cmp/hi r3,r7
bf telemetry_margin_negative
mov r3,r7
telemetry_margin_negative:
mov r3,r2
sub r7,r2
telemetry_margin_compare:
mov.l @(telemetry_margin_latch,pc),r1
mov.w @(r0,r1),r5
add r3,r5
cmp/hs r5,r2
bt telemetry_margin_return
sub r3,r2
mov.w r2,@(r0,r1)
telemetry_margin_return:
lds.l @r15+,pr
rts
nop

.align 4
telemetry_margin_stock:
.long 0x0004A238
telemetry_margin_selector:
.long 0x00008B3D
telemetry_margin_channel_alternate:
.long 0xFFFF2143
telemetry_margin_channel_primary:
.long 0xFFFF11DE
telemetry_margin_metric:
.long 0xFFFF21D8
telemetry_margin_threshold:
.long 0xFFFF2144
telemetry_margin_bias:
.long 0x80000000
telemetry_margin_latch:
.long 0xFFFF5E10
telemetry_margin_idle:
.word 0x7FFF

.org 0x000D4700
telemetry_request_page:
mov.l @(telemetry_request_state,pc),r3
mov.b @r3,r0
tst r0,r0
bt telemetry_request_bank_a
mov.l @(telemetry_request_bank_b,pc),r4
bra telemetry_request_bank_selected
nop
telemetry_request_bank_a:
mov.l @(telemetry_request_bank_a_literal,pc),r4
telemetry_request_bank_selected:
mov.b @(0x3,r3),r0
extu.b r0,r1
shll2 r1
shll r1
add r1,r4
mov.l @(telemetry_mailbox_data,pc),r5
mov #0x8,r2
telemetry_request_copy_loop:
mov.b @r4+,r0
mov.b r0,@r5
add 0x1,r5
dt r2
bf telemetry_request_copy_loop
mov.l @(telemetry_txpr1,pc),r1
mov.w @(telemetry_mailbox26_mask,pc),r0
mov.w r0,@r1
rts
nop

.align 4
telemetry_request_state:
.long 0xFFFF5E00
telemetry_request_bank_a_literal:
.long 0xFFFF5E20
telemetry_request_bank_b:
.long 0xFFFF5E78
telemetry_mailbox_data:
.long 0xFFFFDC48
telemetry_txpr1:
.long 0xFFFFD820
telemetry_mailbox26_mask:
.word 0x0400

.org 0x000D4750
// Page 3 of an installed dynamic configuration. The page loop enters with r3
// at the telemetry state, r4 at the first data byte of the page, r5 at row 3
// of the pointer table, r6 = 3 and r2 = 7. Configuration ID 0 returns to the
// byte loop, which copies the default row. Otherwise the slots of the current
// group fill bytes 1..6, padded with zero, byte 7 carries the ID with the
// group in bit 7, and two groups alternate. A slot that fails the slot check,
// or slots wider than six bytes in all, clear the ID, and the page restarts
// from the default row.
telemetry_build_dynamic_page:
mov.l @(telemetry_dynamic_page_state,pc),r1
mov.b @r1,r0
tst r0,r0
bt telemetry_dynamic_page_default
sts.l pr,@-r15
mov.l r8,@-r15
mov.l r9,@-r15
mov.l r10,@-r15
mov r1,r8
mov.b @(0x2,r8),r0
and 0x1,r0
mov r8,r1
add r0,r1
neg r0,r0
and 0x20,r0
add r8,r0
add 0x10,r0
mov r0,r10
mov.b @(0x4,r1),r0
extu.b r0,r9
mov #0x6,r7
telemetry_dynamic_page_slot:
mov.l @r10+,r1
bsr telemetry_dynamic_slot
nop
tst r0,r0
bt telemetry_dynamic_page_reset
cmp/hs r2,r7
bf telemetry_dynamic_page_reset
sub r2,r7
telemetry_dynamic_page_byte:
mov.b @r0+,r1
mov.b r1,@r4
add 0x1,r4
dt r2
bf telemetry_dynamic_page_byte
dt r9
bf telemetry_dynamic_page_slot
telemetry_dynamic_page_pad:
tst r7,r7
bt telemetry_dynamic_page_id
mov #0x0,r0
mov.b r0,@r4
add 0x1,r4
add -0x1,r7
bra telemetry_dynamic_page_pad
nop
telemetry_dynamic_page_id:
mov.b @(0x2,r8),r0
and 0x1,r0
shll8 r0
shlr r0
mov r0,r1
mov.b @r8,r0
or r1,r0
mov.b r0,@r4
add 0x1,r4
add 0x1C,r5
mov.b @(0x1,r8),r0
shlr r0
mov r0,r1
mov.b @(0x2,r8),r0
xor r1,r0
mov.b r0,@(0x2,r8)
// r2 is zero after a built page and 7 after a reset.
telemetry_dynamic_page_return:
mov.l @r15+,r10
mov.l @r15+,r9
mov.l @r15+,r8
lds.l @r15+,pr
tst r2,r2
bf telemetry_dynamic_page_default
bra telemetry_build_page_next
nop
telemetry_dynamic_page_default:
bra telemetry_build_byte_loop
nop
telemetry_dynamic_page_reset:
add -0x6,r4
add r7,r4
mov #0x0,r0
mov.b r0,@r8
mov #0x7,r2
bra telemetry_dynamic_page_return
nop

.align 4
telemetry_dynamic_page_state:
.long 0xFFFF5F00
