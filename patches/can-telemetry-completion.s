// Combined HCAN1 SLE1 handler and bounded telemetry queue for exact JK08A.
//
// The vector target handles mailbox 26 and then reproduces the complete stock
// mailbox-28 behavior before RTE. All interrupted general registers and PR are
// preserved. Queue corruption disables only custom transmission.

.org 0x000D4800
telemetry_sle1_isr:
mov.l r0,@-r15
mov.l r1,@-r15
mov.l r2,@-r15
mov.l r3,@-r15
mov.l r4,@-r15
mov.l r5,@-r15
mov.l r6,@-r15
mov.l r7,@-r15
sts.l pr,@-r15
bsr telemetry_handle_completion
nop

mov.l @(telemetry_isr_txack1,pc),r6
mov.w @(telemetry_mailbox28_mask,pc),r5
mov.w @r6,r0
extu.w r0,r0
tst r5,r0
bt telemetry_isr_check_mailbox28_abort
mov.w r5,@r6
mov.l @(telemetry_isr_irr1,pc),r2
mov.w @(telemetry_mailbox_empty_mask,pc),r0
mov.w r0,@r2
mov.l @(telemetry_stock_activity_state,pc),r4
mov #-0x1,r0
mov.b r0,@r4
mov.l @(telemetry_stock_mailbox28_complete,pc),r0
jsr @r0
nop
bra telemetry_isr_restore
nop

telemetry_isr_check_mailbox28_abort:
mov.l @(telemetry_isr_aback1,pc),r6
mov.w @r6,r0
extu.w r0,r0
tst r5,r0
bt telemetry_isr_restore
mov.w r5,@r6
mov.l @(telemetry_isr_irr1,pc),r2
mov.w @(telemetry_mailbox_empty_mask,pc),r0
mov.w r0,@r2
mov.l @(telemetry_stock_activity_state,pc),r4
mov #-0x1,r0
mov.b r0,@r4

telemetry_isr_restore:
lds.l @r15+,pr
mov.l @r15+,r7
mov.l @r15+,r6
mov.l @r15+,r5
mov.l @r15+,r4
mov.l @r15+,r3
mov.l @r15+,r2
mov.l @r15+,r1
mov.l @r15+,r0
rte
nop

.align 4
telemetry_isr_txack1:
.long 0xFFFFD830
telemetry_isr_aback1:
.long 0xFFFFD838
telemetry_isr_irr1:
.long 0xFFFFD808
telemetry_stock_activity_state:
.long 0xFFFFA56F
telemetry_stock_mailbox28_complete:
.long 0x000C6B68
telemetry_mailbox28_mask:
.word 0x1000
telemetry_mailbox_empty_mask:
.word 0x0100

.org 0x000D4900
telemetry_handle_completion:
sts.l pr,@-r15
mov.l @(telemetry_completion_txack1,pc),r4
mov.w @(telemetry_completion_mailbox26_mask,pc),r5
mov.w @r4,r0
extu.w r0,r0
tst r5,r0
bt telemetry_completion_check_abort
mov.w r5,@r4
mov.l @(telemetry_completion_irr1,pc),r4
mov.w @(telemetry_completion_mailbox_empty_mask,pc),r0
mov.w r0,@r4
mov.l @(telemetry_completion_state,pc),r3
mov.b @(0x2,r3),r0
cmp/eq 0x1,r0
bt telemetry_completion_busy_valid
bra telemetry_completion_return
nop
telemetry_completion_busy_valid:
bsr telemetry_validate_queue
nop
tst r0,r0
bf telemetry_completion_queue_valid
bra telemetry_completion_return
nop
telemetry_completion_queue_valid:
mov.b @(0x1,r3),r0
tst r0,r0
bt telemetry_completion_ack_advance

mov.b @(0x3,r3),r0
extu.b r0,r1
add 0x1,r1
mov.b @(0x4,r3),r0
extu.b r0,r2
cmp/hs r2,r1
bt telemetry_completion_ack_switch
mov.b @(0x7,r3),r0
or 0x8,r0
mov.b r0,@(0x7,r3)
telemetry_completion_ack_switch:
bsr telemetry_toggle_active
nop
mov #0x0,r0
mov.b r0,@(0x1,r3)
mov.b r0,@(0x3,r3)
mov.l @(telemetry_completion_request_page,pc),r0
jsr @r0
nop
bra telemetry_completion_return
nop

telemetry_completion_ack_advance:
mov.b @(0x3,r3),r0
extu.b r0,r1
add 0x1,r1
mov.b @(0x4,r3),r0
extu.b r0,r2
cmp/hs r2,r1
bt telemetry_completion_group_done
mov r1,r0
mov.b r0,@(0x3,r3)
mov.l @(telemetry_completion_request_page,pc),r0
jsr @r0
nop
bra telemetry_completion_return
nop

telemetry_completion_group_done:
mov #0x0,r0
mov.b r0,@(0x2,r3)
mov.b r0,@(0x3,r3)
mov.b @r3,r0
tst r0,r0
bt telemetry_completion_status_bank_a
mov.l @(telemetry_completion_bank_b,pc),r4
bra telemetry_completion_status_bank
nop
telemetry_completion_status_bank_a:
mov.l @(telemetry_completion_bank_a,pc),r4
telemetry_completion_status_bank:
add 0x1F,r4
mov.b @r4,r1
not r1,r1
mov.b @(0x7,r3),r0
and r1,r0
mov.b r0,@(0x7,r3)
bra telemetry_completion_return
nop

telemetry_completion_check_abort:
mov.l @(telemetry_completion_aback1,pc),r4
mov.w @r4,r0
extu.w r0,r0
tst r5,r0
bt telemetry_completion_return
mov.w r5,@r4
mov.l @(telemetry_completion_irr1,pc),r4
mov.w @(telemetry_completion_mailbox_empty_mask,pc),r0
mov.w r0,@r4
mov.l @(telemetry_completion_state,pc),r3
mov.b @(0x7,r3),r0
or 0x2,r0
mov.b r0,@(0x7,r3)
mov.b @(0xF,r3),r0
cmp/eq -0x1,r0
bt telemetry_completion_abort_validate
add 0x1,r0
mov.b r0,@(0xF,r3)
telemetry_completion_abort_validate:
mov.b @(0x2,r3),r0
cmp/eq 0x1,r0
bf telemetry_completion_return
bsr telemetry_validate_queue
nop
tst r0,r0
bt telemetry_completion_return
mov.b @(0x1,r3),r0
tst r0,r0
bt telemetry_completion_abort_idle
bsr telemetry_toggle_active
nop
mov #0x0,r0
mov.b r0,@(0x1,r3)
mov.b r0,@(0x3,r3)
mov #0x1,r0
mov.b r0,@(0x2,r3)
mov.l @(telemetry_completion_request_page,pc),r0
jsr @r0
nop
bra telemetry_completion_return
nop
telemetry_completion_abort_idle:
mov #0x0,r0
mov.b r0,@(0x2,r3)
mov.b r0,@(0x3,r3)
bra telemetry_completion_return
nop

telemetry_validate_queue:
mov.b @r3,r0
extu.b r0,r1
mov #0x2,r2
cmp/hs r2,r1
bt telemetry_queue_corrupt
mov.b @(0x1,r3),r0
extu.b r0,r1
cmp/hs r2,r1
bt telemetry_queue_corrupt
mov.b @(0x4,r3),r0
extu.b r0,r2
cmp/eq 0x5,r0
bt telemetry_queue_page_count_valid
cmp/eq 0x8,r0
bf telemetry_queue_corrupt
telemetry_queue_page_count_valid:
mov.b @(0x3,r3),r0
extu.b r0,r1
cmp/hs r2,r1
bt telemetry_queue_corrupt
mov #0x1,r0
rts
nop
telemetry_queue_corrupt:
mov #0x0,r0
mov.b r0,@(0x1,r3)
mov.b r0,@(0x2,r3)
mov.b r0,@(0x3,r3)
rts
nop

telemetry_toggle_active:
mov.b @r3,r0
tst r0,r0
bt telemetry_toggle_to_bank_b
mov #0x0,r0
mov.b r0,@r3
rts
nop
telemetry_toggle_to_bank_b:
mov #0x1,r0
mov.b r0,@r3
rts
nop

telemetry_completion_return:
lds.l @r15+,pr
rts
nop

.align 4
telemetry_completion_state:
.long 0xFFFF5E00
telemetry_completion_txack1:
.long 0xFFFFD830
telemetry_completion_aback1:
.long 0xFFFFD838
telemetry_completion_irr1:
.long 0xFFFFD808
telemetry_completion_request_page:
.long 0x000D4700
telemetry_completion_bank_a:
.long 0xFFFF5E20
telemetry_completion_bank_b:
.long 0xFFFF5E60
telemetry_completion_mailbox26_mask:
.word 0x0400
telemetry_completion_mailbox_empty_mask:
.word 0x0100
