// Fuel-cut coordinator wrapper for exact JK08A Rolling Launch.
//
// Periodic table index 28 calls this entry in place of the stock six-channel
// fuel-output inhibit coordinator. The wrapper runs the coordinator first, so
// every stock inhibit, diagnostic and Power Balance contribution is retained.
// A request word of 0x0001..0x003F in the Rolling Launch state is then ORed
// into the final cylinder mask. Zero and any request with a bit outside the six
// cylinder bits leave the stock mask unchanged. The engine runs at table index
// 1, so the mask always carries the request of the current scheduler pass. The
// wrapper returns the exact r0 value of the stock coordinator.

.org 0x000D6000
rolling_launch_fuel_cut_wrapper:
sts.l pr,@-r15
mov.l @(rl_fuel_stock_coordinator,pc),r0
jsr @r0
nop
mov.l r0,@-r15
mov.l @(rl_fuel_state_address,pc),r1
mov.w @(0x14,r1),r0
extu.w r0,r0
tst r0,r0
bt rl_fuel_return
mov #-0x40,r1
tst r1,r0
bf rl_fuel_return
mov.l @(rl_fuel_final_mask_address,pc),r1
mov.b @r1,r2
or r2,r0
mov.b r0,@r1
rl_fuel_return:
mov.l @r15+,r0
lds.l @r15+,pr
rts
nop

.org 0x000D6030
rl_fuel_stock_coordinator:
.long 0x0004ED88
rl_fuel_state_address:
.long 0xFFFF5D40
rl_fuel_final_mask_address:
.long 0xFFFF22E0
