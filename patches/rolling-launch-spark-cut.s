// Dwell-arming cut actuator for exact JK08A.
//
// The crank-tooth handler 0x00028EA2 arms each dwell start at the expiry of a
// GR11B countdown slot: it calls the unsigned divider through literal
// 0x000296C0 (call sites 0x000294B2 and 0x0002954A) at interrupt mask 8, writes
// GR11B and then, at mask 15, enables the dwell of mask 0xFFFF13D1 only while
// 0xFFFF8511.bit7 is clear. The literal enters this actuator instead. No
// GR11A or GR11B service runs between the actuator and that enable check, so
// a veto set here withholds exactly the dwell being armed. The actuator
// preserves r0..r7, PR and the interrupt mask and leaves through the stock
// divider 0x00021CE0 with its dividend in r1 and divisor in r0, restoring r0
// in the delay slot of the tail jump. It runs without loops.
//
// Actuator bytes of the state at 0xFFFF5D40, written only by this actuator:
//   +0x1C u8  quiet events: 0 while ACTIVE, else a count saturating at 255
//   +0x1D u8  cut counter, wrapping
//   +0x20 u16 accumulators of the armed cylinders 1..6, in sixths of a
//             thousandth of a cut
// and of the extension at 0xFFFF6100:
//   +0x10 u32 consumed q sum, wrapping
//   +0x18 u16 eligible arming counter, wrapping
//
// In an ACTIVE hold with the cut fraction q <= 1000 at state +0x1A, an arming
// is eligible with the sync bit 0xFFFF8501.bit7, without the P0335 APC
// fallback 0xFFFF24C9.bit6, when the stock check would enable it
// (0xFFFF84EA.bit7 and 0xFFFF4185.bit7 set, 0xFFFF13D2 zero, 0xFFFF8511.bit7
// clear), and when 0xFFFF13D1 holds one cylinder bit of 0x01..0x20. An
// ineligible arming leaves every accumulator and counter unchanged. An
// eligible arming reads q once, adds 6 * q to the accumulator of the armed
// cylinder, adds q to the consumed q sum and counts the arming; a sum of 6000
// subtracts 6000, sets the dwell-start veto 0xFFFF8511.bit7 and counts the
// cut. These writes run in one section with interrupts masked. Outside an
// ACTIVE hold, and for an out-of-range accumulator, the accumulators return
// to offsets that differ by exact sixths in firing order. During an ACTIVE
// hold the misfire-monitor latch 0xFFFF436F receives the marker 0x01 when it
// is zero; in IDLE after 14 quiet events it is cleared while it holds 0x01.
// That check-and-store also runs with interrupts masked.

.org 0x000D60C0
rolling_launch_spark_cut:
mov.l r0,@-r15
sts.l pr,@-r15
mov.l r1,@-r15
mov.l r2,@-r15
mov.l r3,@-r15
mov.l r4,@-r15
mov.l r5,@-r15
mov.l r6,@-r15
mov.l r7,@-r15
stc sr,r0
mov.l r0,@-r15
mov.l @(rl_cut_state_address,pc),r5
bsr 0x000D6780
nop
tst r2,r2
bt rl_cut_reset
mov.w @(0x1a,r5),r0
extu.w r0,r1
mov.w @(rl_cut_u_one,pc),r3
cmp/hi r3,r1
bt rl_cut_reset
mov.l @(rl_cut_sync_address,pc),r3
mov.b @r3,r0
tst 0x80,r0
bt rl_cut_chain
mov.l @(rl_cut_apc_mode_address,pc),r3
mov.b @r3,r0
tst 0x40,r0
bf rl_cut_chain
mov.l @(rl_cut_output_state_address,pc),r3
mov.b @r3,r0
tst 0x80,r0
bt rl_cut_chain
mov.l @(rl_cut_port_state_address,pc),r3
mov.b @r3,r0
tst 0x80,r0
bt rl_cut_chain
mov.l @(rl_cut_veto_address,pc),r3
mov.b @r3,r0
tst 0x80,r0
bf rl_cut_chain
mov.l @(rl_cut_dwell_mask_address,pc),r3
mov.b @(0x1,r3),r0
tst r0,r0
bf rl_cut_chain
mov.b @r3,r0
extu.b r0,r0
tst r0,r0
bt rl_cut_chain
mov r0,r7
add -0x1,r7
tst r0,r7
bf rl_cut_chain
mov #0x40,r7
cmp/hs r7,r0
bt rl_cut_chain
mov #0x4,r5
tst 0x2a,r0
bt rl_cut_index_4
add 0x2,r5
rl_cut_index_4:
tst 0xc,r0
bt rl_cut_index_8
add 0x4,r5
rl_cut_index_8:
tst 0x30,r0
bt rl_cut_index_ready
add 0x8,r5
rl_cut_index_ready:
mov r5,r0
mov.w @(r0,r4),r7
extu.w r7,r7
mov.w @(rl_cut_one,pc),r3
cmp/hs r3,r7
bt rl_cut_reset
mov r1,r2
shll r2
add r1,r2
shll r2
add r2,r7
mov #0x0,r2
cmp/hs r3,r7
bf rl_cut_commit
sub r3,r7
mov #0x1,r2
rl_cut_commit:
mov.l @(rl_cut_extension_address,pc),r3
stc sr,r6
mov r6,r0
or 0xf0,r0
ldc r0,sr
mov r5,r0
mov.w r7,@(r0,r4)
mov.l @(0x10,r3),r0
add r1,r0
mov.l r0,@(0x10,r3)
mov.w @(0x18,r3),r0
add 0x1,r0
mov.w r0,@(0x18,r3)
tst r2,r2
bt rl_cut_unmask
mov.l @(rl_cut_veto_address,pc),r3
mov.b @r3,r0
or 0x80,r0
mov.b r0,@r3
mov.b @(0x1,r4),r0
add 0x1,r0
mov.b r0,@(0x1,r4)
rl_cut_unmask:
ldc r6,sr
bra rl_cut_chain
nop
rl_cut_reset:
mov.w @(rl_cut_offset_1,pc),r0
mov.w r0,@(0x4,r4)
mov.w @(rl_cut_offset_2,pc),r0
mov.w r0,@(0x6,r4)
mov.w @(rl_cut_offset_3,pc),r0
mov.w r0,@(0x8,r4)
mov.w @(rl_cut_offset_4,pc),r0
mov.w r0,@(0xa,r4)
mov.w @(rl_cut_offset_5,pc),r0
mov.w r0,@(0xc,r4)
mov.w @(rl_cut_offset_6,pc),r0
mov.w r0,@(0xe,r4)
rl_cut_chain:
mov.l @r15+,r0
ldc r0,sr
mov.l @r15+,r7
mov.l @r15+,r6
mov.l @r15+,r5
mov.l @r15+,r4
mov.l @r15+,r3
mov.l @r15+,r2
mov.l @r15+,r1
lds.l @r15+,pr
mov.l @(rl_cut_stock_divider,pc),r0
jmp @r0
mov.l @r15+,r0

.org 0x000D61E0
rl_cut_state_address:
.long 0xFFFF5D40
rl_cut_sync_address:
.long 0xFFFF8501
rl_cut_apc_mode_address:
.long 0xFFFF24C9
rl_cut_output_state_address:
.long 0xFFFF84EA
rl_cut_port_state_address:
.long 0xFFFF4185
rl_cut_veto_address:
.long 0xFFFF8511
rl_cut_dwell_mask_address:
.long 0xFFFF13D1
rl_cut_extension_address:
.long 0xFFFF6100
rl_cut_stock_divider:
.long 0x00021CE0
rl_cut_u_one:
.word 1000
rl_cut_one:
.word 6000
rl_cut_offset_1:
.word 250
rl_cut_offset_2:
.word 2250
rl_cut_offset_3:
.word 4250
rl_cut_offset_4:
.word 1250
rl_cut_offset_5:
.word 3250
rl_cut_offset_6:
.word 5250
