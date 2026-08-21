// 8MFK HCAN1 SLE1 wrapper template.
//
// The target projection relocates this source and binds the exact stock ISR.
// The wrapper preserves the interrupted register file, handles the custom
// mailbox through the shared completion routine, and restores r0 in the JMP
// delay slot so the complete stock ISR receives the original machine state.

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
lds.l @r15+,pr
mov.l @r15+,r7
mov.l @r15+,r6
mov.l @r15+,r5
mov.l @r15+,r4
mov.l @r15+,r3
mov.l @r15+,r2
mov.l @r15+,r1
mov.l @(telemetry_stock_sle1_isr,pc),r0
jmp @r0
mov.l @r15+,r0

.align 4
telemetry_stock_sle1_isr:
.long 0x000C7914
