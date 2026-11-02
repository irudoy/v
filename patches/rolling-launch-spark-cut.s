// Spark-handler cut actuator for exact JK08A.
//
// Interrupt-table entry 0x000202E4 (IMI11A, the GR11A match) enters the
// wrapper at the ATU11 interrupt level. The wrapper saves r0..r7 and SR,
// updates the actuator bytes of the Rolling Launch state, restores SR, r1..r7
// and, in the JMP delay slot, r0, so the stock handler 0x0002AB24 receives
// the machine state of its entry. It runs without loops.
//
// Actuator bytes of the state at 0xFFFF5D40, written only by this wrapper:
//   +0x1C u8  quiet events: 0 while ACTIVE, else a count saturating at 255
//   +0x1D u8  cut counter, wrapping
//   +0x1E u16 reserved, zero
//   +0x20 u16 accumulators of event cylinders 1..6 (0xFFFF13C9), in sixths
//             of a thousandth of a cut
//
// A match without 0xFFFF8517.bit7 is a forced timeout match and passes
// through unchanged. In an ACTIVE hold with u <= 1000, a spark is eligible
// with the sync bit 0xFFFF8501.bit7, without the P0335 APC fallback
// 0xFFFF24C9.bit6, with the dwell angle 0xFFFF237A at most 110 degrees, and
// with a cylinder number of 1..6. An ineligible spark leaves every
// accumulator unchanged. An eligible spark adds 6 * (1000 - u) to the
// accumulator of its cylinder; a sum of 6000 subtracts 6000 and sets the
// dwell-start veto 0xFFFF8511.bit7 with interrupts masked. Outside an ACTIVE
// hold, and for an out-of-range accumulator, the accumulators return to
// offsets that differ by exact sixths in firing order. During an ACTIVE hold
// the misfire-monitor latch 0xFFFF436F receives the marker 0x01 when it is
// zero; in IDLE after 14 quiet events it is cleared while it holds 0x01. Both
// check-and-stores run with interrupts masked.

.org 0x000D60C0
rolling_launch_spark_cut:
mov.l r0,@-r15
mov.l r1,@-r15
mov.l r2,@-r15
mov.l r3,@-r15
mov.l r4,@-r15
mov.l r5,@-r15
mov.l r6,@-r15
mov.l r7,@-r15
stc sr,r0
mov.l r0,@-r15
mov.l @(rl_spark_veto_address,pc),r6
mov.b @(0x6,r6),r0
tst 0x80,r0
bt rl_spark_chain
mov.l @(rl_spark_state_address,pc),r5
mov r5,r4
add 0x1c,r4
mov.b @r5,r0
mov r0,r1
mov #0x0,r2
cmp/eq 0x1,r0
bf rl_spark_quiet_count
mov #0x0,r0
mov.b r0,@r4
mov.b @(0x5,r5),r0
cmp/eq 0x1,r0
bf rl_spark_latch
mov #0x1,r2
bra rl_spark_latch
nop
rl_spark_quiet_count:
mov.b @r4,r0
not r0,r3
tst r3,r3
bt rl_spark_latch
add 0x1,r0
mov.b r0,@r4
rl_spark_latch:
mov.l @(rl_spark_misfire_latch_address,pc),r3
stc sr,r7
mov r7,r0
or 0xf0,r0
ldc r0,sr
mov.b @r3,r0
tst r2,r2
bt rl_spark_latch_release
tst r0,r0
bf rl_spark_latch_done
mov #0x1,r0
mov.b r0,@r3
bra rl_spark_latch_done
nop
rl_spark_latch_release:
cmp/eq 0x1,r0
bf rl_spark_latch_done
tst r1,r1
bf rl_spark_latch_done
mov.b @r4,r0
extu.b r0,r0
mov #0xd,r1
cmp/hi r1,r0
bf rl_spark_latch_done
mov #0x0,r0
mov.b r0,@r3
rl_spark_latch_done:
ldc r7,sr
tst r2,r2
bt rl_spark_reset
mov.w @(0xe,r5),r0
extu.w r0,r1
mov.w @(rl_spark_u_one,pc),r3
cmp/hi r3,r1
bt rl_spark_reset
mov.l @(rl_spark_sync_address,pc),r3
mov.b @r3,r0
tst 0x80,r0
bt rl_spark_chain
mov.l @(rl_spark_apc_mode_address,pc),r3
mov.b @r3,r0
tst 0x40,r0
bf rl_spark_chain
mov.l @(rl_spark_dwell_address,pc),r3
mov.b @r3,r0
extu.b r0,r0
mov #0x6e,r3
cmp/hi r3,r0
bt rl_spark_chain
mov.l @(rl_spark_cylinder_address,pc),r3
mov.b @r3,r0
extu.b r0,r0
add -0x1,r0
mov #0x6,r3
cmp/hs r3,r0
bt rl_spark_chain
shll r0
add 0x4,r0
mov.w @(r0,r4),r7
extu.w r7,r7
mov.w @(rl_spark_cut_one,pc),r3
cmp/hs r3,r7
bt rl_spark_reset
mov.w @(rl_spark_u_one,pc),r2
sub r1,r2
shll r2
mov r2,r1
shll r2
add r1,r2
add r2,r7
cmp/hs r3,r7
bf rl_spark_store
sub r3,r7
mov.w r7,@(r0,r4)
stc sr,r3
mov r3,r0
or 0xf0,r0
ldc r0,sr
mov.b @r6,r0
or 0x80,r0
mov.b r0,@r6
ldc r3,sr
mov.b @(0x1,r4),r0
add 0x1,r0
mov.b r0,@(0x1,r4)
bra rl_spark_chain
nop
rl_spark_store:
mov.w r7,@(r0,r4)
bra rl_spark_chain
nop
rl_spark_reset:
mov.w @(rl_spark_offset_1,pc),r0
mov.w r0,@(0x4,r4)
mov.w @(rl_spark_offset_2,pc),r0
mov.w r0,@(0x6,r4)
mov.w @(rl_spark_offset_3,pc),r0
mov.w r0,@(0x8,r4)
mov.w @(rl_spark_offset_4,pc),r0
mov.w r0,@(0xa,r4)
mov.w @(rl_spark_offset_5,pc),r0
mov.w r0,@(0xc,r4)
mov.w @(rl_spark_offset_6,pc),r0
mov.w r0,@(0xe,r4)
rl_spark_chain:
mov.l @r15+,r0
ldc r0,sr
mov.l @r15+,r7
mov.l @r15+,r6
mov.l @r15+,r5
mov.l @r15+,r4
mov.l @r15+,r3
mov.l @r15+,r2
mov.l @r15+,r1
mov.l @(rl_spark_stock_handler,pc),r0
jmp @r0
mov.l @r15+,r0

.org 0x000D61E8
rl_spark_veto_address:
.long 0xFFFF8511
rl_spark_state_address:
.long 0xFFFF5D40
rl_spark_misfire_latch_address:
.long 0xFFFF436F
rl_spark_sync_address:
.long 0xFFFF8501
rl_spark_apc_mode_address:
.long 0xFFFF24C9
rl_spark_dwell_address:
.long 0xFFFF237A
rl_spark_cylinder_address:
.long 0xFFFF13C9
rl_spark_stock_handler:
.long 0x0002AB24
rl_spark_u_one:
.word 1000
rl_spark_cut_one:
.word 6000
rl_spark_offset_1:
.word 250
rl_spark_offset_2:
.word 2250
rl_spark_offset_3:
.word 4250
rl_spark_offset_4:
.word 1250
rl_spark_offset_5:
.word 3250
rl_spark_offset_6:
.word 5250
