// VQ37 fuel-cut coordinator wrapper for Rolling Launch.
//
// The scheduler calls this entry at the stock fuel coordinator slot. The
// wrapper executes the displaced coordinator first so every stock inhibit and
// diagnostic contribution is retained. An exact 0x003F request in dedicated
// Rolling Launch state then adds all six cylinder bits to the final mask.
// Any other request value is fail-open and leaves the stock result unchanged.
// The wrapper returns the exact r0 value produced by the stock coordinator.

.org 0x000D5000
rolling_launch_fuel_cut_wrapper:
sts.l pr,@-r15
mov.l @(rl_fuel_stock_coordinator,pc),r0
jsr @r0
nop
mov.l r0,@-r15
mov.l @(rl_fuel_state_address,pc),r1
mov.w @(0x14,r1),r0
extu.w r0,r0
mov #0x3F,r1
cmp/eq r1,r0
bf rl_fuel_return
mov.l @(rl_fuel_final_mask_address,pc),r1
mov.b @r1,r0
or 0x3F,r0
mov.b r0,@r1
rl_fuel_return:
mov.l @r15+,r0
lds.l @r15+,pr
rts
nop

.org 0x000D5040
rl_fuel_stock_coordinator:
// Template token replaced by the exact target profile before assembly.
.long 0x000A0000
rl_fuel_state_address:
.long 0xFFFF5D40
rl_fuel_final_mask_address:
.long 0xFFFF22E0
