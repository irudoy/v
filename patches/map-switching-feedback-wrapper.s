// CAN 0x551 feedback wrapper for the exact JK08A serializer hook.
//
// The wrapper always runs the stock serializer first, then calls the separate
// fail-closed pulse engine. It preserves the dispatcher's PR and stack layout.

.org 0x000D35E0
cruise_feedback_wrapper:
sts.l pr,@-r15
mov.l @(feedback_stock_serializer,pc),r0
jsr @r0
nop
mov.l @(feedback_engine_entry,pc),r0
jsr @r0
nop
lds.l @r15+,pr
rts
nop

.org 0x000D3640
feedback_stock_serializer:
.long 0x000C5372
feedback_engine_entry:
.long 0x000D3760
