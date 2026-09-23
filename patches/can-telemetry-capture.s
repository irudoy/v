// Coherent snapshot builder and mailbox submitter for exact JK08A.
//
// The entry runs with interrupts already masked by FUN_00020DFE. It validates
// the fail-closed ROM configuration, advances the base tick, applies the
// configured divider, builds the inactive frame bank, and atomically publishes
// either an active or replaceable pending snapshot.

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
cmp/eq 0x7,r0
bf telemetry_capture_return
mov #0xB,r6
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
mov.l @(telemetry_capture_state,pc),r3
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
mov.l @(telemetry_capture_state,pc),r3
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
.word 0x6474

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
telemetry_build_byte_loop:
mov.l @r5+,r1
mov.b @r1,r0
mov.b r0,@r4
add 0x1,r4
dt r2
bf telemetry_build_byte_loop
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
