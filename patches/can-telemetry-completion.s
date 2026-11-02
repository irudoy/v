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
// The transmitted telemetry_status byte is byte 7 of page 7.
telemetry_completion_status_bank:
add 0x3F,r4
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
cmp/eq 0xB,r0
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
.long 0xFFFF5E78
telemetry_completion_mailbox26_mask:
.word 0x0400
telemetry_completion_mailbox_empty_mask:
.word 0x0100

.org 0x000D4A70
// Dynamic page commands of the telemetry control frame. The control poll
// enters with r4 = bytes 0..3 and r5 = bytes 4..7 of a frame that lacks the
// TEL2 magic; bytes 6..7 carry CRC-16/CCITT-FALSE of bytes 0..5.
// DEFAULT C0 00 00 00 00 00 installs the default configuration.
// SET C1 id d a2 a1 a0 stages slot (d >> 4) & 7, below six, of group d >> 7,
// of width d & 0xF at 0xFF000000 + a2a1a0, for configuration ID 1..127; a new
// ID restarts the staging.
// COMMIT C2 id g n0 n1 00 installs the staged ID with group 0 of n0 slots and,
// for g = 2, group 1 of n1 slots, when the staging holds exactly those slots
// and each group fits six bytes.
// Any other frame clears the staging and advances the saturating reject
// counter; the active configuration stays unchanged.
telemetry_dynamic_command:
sts.l pr,@-r15
mov.l r8,@-r15
mov.l r9,@-r15
mov.l r10,@-r15
mov.l r11,@-r15
mov.l @(telemetry_dynamic_command_state,pc),r8
mov.l @(telemetry_dynamic_command_crc,pc),r0
jsr @r0
nop
extu.w r5,r1
cmp/eq r1,r0
bf telemetry_dynamic_reject
mov r4,r0
shlr16 r0
shlr8 r0
exts.b r0,r0
cmp/eq -0x40,r0
bt telemetry_dynamic_default
cmp/eq -0x3F,r0
bt telemetry_dynamic_set
cmp/eq -0x3E,r0
bt telemetry_dynamic_commit
telemetry_dynamic_reject:
mov.b @(0x3,r8),r0
cmp/eq -0x1,r0
bt telemetry_dynamic_clear
add 0x1,r0
mov.b r0,@(0x3,r8)
telemetry_dynamic_clear:
mov #0x0,r0
mov.w r0,@(0x6,r8)
mov.b r0,@(0x8,r8)
telemetry_dynamic_return:
mov.l @r15+,r11
mov.l @r15+,r10
mov.l @r15+,r9
mov.l @r15+,r8
lds.l @r15+,pr
rts
nop

telemetry_dynamic_default:
mov r4,r0
shll8 r0
tst r0,r0
bf telemetry_dynamic_reject
mov r5,r0
shlr16 r0
tst r0,r0
bf telemetry_dynamic_reject
mov #0x0,r0
mov.b r0,@r8
bra telemetry_dynamic_clear
nop

telemetry_dynamic_set:
mov r4,r0
shlr16 r0
exts.b r0,r9
cmp/pl r9
bf telemetry_dynamic_reject
mov r4,r7
shll16 r7
mov r5,r0
shlr16 r0
or r0,r7
mov r7,r0
shlr16 r0
shlr8 r0
shlr2 r0
shlr2 r0
mov r0,r10
and 0x7,r0
mov #0x6,r1
cmp/hs r1,r0
bt telemetry_dynamic_reject
mov r7,r1
mov.l @(telemetry_dynamic_command_slot,pc),r0
jsr @r0
nop
tst r0,r0
bt telemetry_dynamic_reject
mov.b @(0x8,r8),r0
cmp/eq r9,r0
bt telemetry_dynamic_set_store
mov r9,r0
mov.b r0,@(0x8,r8)
mov #0x0,r0
mov.w r0,@(0x6,r8)
telemetry_dynamic_set_store:
mov r10,r1
shll2 r1
add r8,r1
add 0x50,r1
mov.l r7,@r1
mov #0x1,r2
telemetry_dynamic_set_bit:
tst r10,r10
bt telemetry_dynamic_set_mask
shll r2
add -0x1,r10
bra telemetry_dynamic_set_bit
nop
telemetry_dynamic_set_mask:
mov.w @(0x6,r8),r0
or r2,r0
mov.w r0,@(0x6,r8)
bra telemetry_dynamic_return
nop

telemetry_dynamic_commit:
mov r4,r0
shlr16 r0
extu.b r0,r9
tst r9,r9
bt telemetry_dynamic_reject
mov.b @(0x8,r8),r0
cmp/eq r9,r0
bf telemetry_dynamic_reject
mov r5,r0
shlr16 r0
tst 0xFF,r0
bf telemetry_dynamic_reject
mov r4,r0
extu.b r0,r0
mov r8,r2
add 0x50,r2
bsr telemetry_dynamic_group
nop
tst r0,r0
bt telemetry_dynamic_reject
mov r0,r10
mov #0x1,r11
mov r5,r0
shlr16 r0
shlr8 r0
tst r0,r0
bt telemetry_dynamic_commit_groups
mov r8,r2
add 0x70,r2
bsr telemetry_dynamic_group
nop
tst r0,r0
bt telemetry_dynamic_reject
shll8 r0
or r0,r10
mov #0x2,r11
telemetry_dynamic_commit_groups:
mov r4,r0
shlr8 r0
extu.b r0,r0
cmp/eq r11,r0
bf telemetry_dynamic_reject
mov.w @(0x6,r8),r0
cmp/eq r10,r0
bf telemetry_dynamic_reject
mov r8,r1
add 0x50,r1
mov r8,r2
add 0x10,r2
mov #0x10,r3
telemetry_dynamic_commit_copy:
mov.l @r1+,r0
mov.l r0,@r2
add 0x4,r2
dt r3
bf telemetry_dynamic_commit_copy
mov r4,r0
mov.b r0,@(0x4,r8)
mov r5,r0
shlr16 r0
shlr8 r0
mov.b r0,@(0x5,r8)
mov r11,r0
mov.b r0,@(0x1,r8)
mov #0x0,r0
mov.b r0,@(0x2,r8)
mov r9,r0
mov.b r0,@r8
bra telemetry_dynamic_clear
nop

// In: r0 = the slot count of a group, r2 = its first staged slot. Out:
// r0 = the mask of the staged slots that the count requires, or 0 when the
// count is outside 1..6 or the slots are wider than six bytes in all.
// Clobbers r1, r2, r3, r6 and r7.
telemetry_dynamic_group:
mov r0,r3
mov #0x0,r6
mov #0x6,r7
tst r3,r3
bt telemetry_dynamic_group_fail
cmp/hi r7,r3
bt telemetry_dynamic_group_fail
telemetry_dynamic_group_slot:
shll r6
add 0x1,r6
mov.l @r2+,r0
shlr16 r0
shlr8 r0
and 0xF,r0
sub r0,r7
dt r3
bf telemetry_dynamic_group_slot
cmp/pz r7
bf telemetry_dynamic_group_fail
mov r6,r0
rts
nop
telemetry_dynamic_group_fail:
mov #0x0,r0
rts
nop

.align 4
telemetry_dynamic_command_state:
.long 0xFFFF5F00
telemetry_dynamic_command_crc:
.long 0x000D44B0
telemetry_dynamic_command_slot:
.long 0x000D4460
