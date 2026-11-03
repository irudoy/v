// Per-map slots and ignition-trim compensation for exact JK08A Rolling Launch.
//
// The configuration record at 0xD6220 carries five map slots at +0x28, six
// bytes each, and an end marker at +0x46:
//   +0x0 s16 integral gain Ki, 0..0x7FFF
//   +0x2 u8  maximum trim z, degrees of APC command, 0..40
//   +0x3 u8  floor command, the latest APC command that the trim may reach
//   +0x4 u16 trim efficiency e = (256 - F(z)) * 1000 / 256 in thousandths,
//            1..1000, and 1000 when z is 0
//
// The slot validator completes the configuration check of the engine, which
// jumps to it with r3 holding the record; it returns 1 in r0 for five valid
// slots and the end marker, else 0, and changes only r0..r4 and T.
//
// The trim unit runs between the speed controller and the RPM ceiling unit
// with r3 holding the flags, r4 the record and r5 the state. It stores the cut
// fraction c = 1000 - min(1000, 1000 * u / e) of the slot of the activation
// map in state +0x1A, which the spark-cut actuator consumes, so the fired
// events of a trimmed hold deliver u. It then tail-jumps to the ceiling unit
// with r3, r4 and r5 unchanged and changes only r0, r1, r2, r7, MACL and T.
// The stock unsigned divider at 0x21CE0 receives r0=divisor and r1=dividend
// and preserves r2 through r7.

.org 0x000D6268
rolling_launch_slot_validator:
mov r3,r4
add 0x28,r4
mov #0x5,r2
rl_slot_next:
mov.w @r4,r0
cmp/pz r0
bf rl_slot_invalid
mov.b @(0x2,r4),r0
extu.b r0,r1
mov #0x28,r0
cmp/hi r0,r1
bt rl_slot_invalid
mov.w @(0x4,r4),r0
extu.w r0,r0
tst r0,r0
bt rl_slot_invalid
mov.w @(rl_slot_u_one,pc),r3
cmp/hi r3,r0
bt rl_slot_invalid
tst r1,r1
bf rl_slot_trimmed
cmp/eq r3,r0
bf rl_slot_invalid
rl_slot_trimmed:
add 0x6,r4
dt r2
bf rl_slot_next
mov.w @r4,r0
extu.w r0,r0
mov.w @(rl_slot_end_marker,pc),r1
extu.w r1,r1
cmp/eq r1,r0
bf rl_slot_invalid
mov #0x1,r0
rts
nop
rl_slot_invalid:
mov #0x0,r0
rts
nop

.org 0x000D62B4
rl_slot_u_one:
.word 1000
rl_slot_end_marker:
.word 0xA55A

.org 0x000D62B8
rolling_launch_trim:
sts.l pr,@-r15
mov.b @(0x4,r5),r0
extu.b r0,r0
mov r0,r1
shll r1
shll2 r0
add r1,r0
add r4,r0
add 0x2C,r0
mov.w @r0,r0
extu.w r0,r7
mov.w @(0xE,r5),r0
extu.w r0,r1
mov.w @(rl_trim_u_one,pc),r2
cmp/eq r2,r7
bt rl_trim_fired
mulu.w r2,r1
sts macl,r1
mov r7,r0
mov.l @(rl_trim_unsigned_divide,pc),r2
jsr @r2
nop
mov r0,r1
mov.w @(rl_trim_u_one,pc),r2
cmp/hi r2,r1
bf rl_trim_fired
mov r2,r1
rl_trim_fired:
sub r1,r2
mov r2,r0
mov.w r0,@(0x1A,r5)
lds.l @r15+,pr
mov.l @(rl_trim_ceiling_entry,pc),r0
jmp @r0
nop

.org 0x000D6300
rl_trim_unsigned_divide:
.long 0x00021CE0
rl_trim_ceiling_entry:
.long 0x000D6068
rl_trim_u_one:
.word 1000
