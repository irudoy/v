// Primary APC command pass-through for exact JK08A Rolling Launch.
//
// The primary ignition command hook stays on the Rolling Launch layer. Input
// r4 is the stock uint8 command; the adapter tail-jumps to the stock consumer
// 0x2A892 with every argument register unchanged.

.org 0x000D3EA0
rolling_launch_ignition_adapter:
mov.l @(rl_ign_stock_consumer,pc),r0
jmp @r0
nop

.org 0x000D3EA8
rl_ign_stock_consumer:
.long 0x0002A892
