// Schema 6 record check and wire views for exact JK08A Rolling Launch.
//
// The structural check returns T=1 when the base state at 0xFFFF5D40 and
// the extension at 0xFFFF6100 decode as a schema 6 model state: every field
// lies in its range, the reserved byte is zero, the fields of the inactive
// regulator are zero and the wire views agree with the fields they
// summarize. The ignition publisher runs the entry at 0xD7000 from the
// crank-tooth interrupt, where the engine cannot run. The engine runs the
// entry at 0xD7008 before every pass; it masks interrupts for the whole
// check, so a publication cannot split the fields it reads. Both entries
// restore the SR of the caller and return the result in T.
//
// The views routine receives r7=extension, r1=applied trim a, r2=ready and
// r3=efficiency e and returns r1 = (mode/trim << 8) | status for +0x1E and
// r3 = (e << 16) | wire e for +0x0C:
//   mode/trim = a | kind SPEED << 6 | ready << 7
//   wire e    = e | kind SPEED << 14 | ready << 15
//   status    = kind | (input_status & 7) << 2 | CANCEL << 5 | RELEASED << 6
//               | ready << 7
// It changes r0, r2 and T. The stored-views entry loads a, ready and e from
// the extension in r7 first.

.org 0x000D7000
// Structural check: T=1 when the base and extension records decode as a
// schema 6 model state with consistent wire views and a zero reserved byte.
// It changes r0..r3, r6, r7 and T and preserves r4, r5, r8..r15, PR and the
// remaining SR bits.
rolling_launch_state_check:
stc sr,r0
mov.l r0,@-r15
bra rl_check_begin
nop
rolling_launch_state_check_masked:
stc sr,r0
mov.l r0,@-r15
or 0xf0,r0
ldc r0,sr
rl_check_begin:
sts.l pr,@-r15
mov.l @(rl_sc_state_address,pc),r6
mov.l @(rl_sc_extension_address,pc),r7
// Byte fields against their maxima; offset bit 7 selects the extension.
mov.l @(rl_sc_byte_limits,pc),r2
mov #0xa,r3
rl_check_byte_next:
mov.b @r2+,r0
cmp/pz r0
bt rl_check_byte_base
and 0x7f,r0
mov.b @(r0,r7),r0
bra rl_check_byte_compare
nop
rl_check_byte_base:
mov.b @(r0,r6),r0
rl_check_byte_compare:
extu.b r0,r0
mov.b @r2+,r1
cmp/hi r1,r0
bt rl_check_fail_near
dt r3
bf rl_check_byte_next
// Flag bits 13 and 15 are never assigned.
mov.w @(0x2,r6),r0
shlr8 r0
tst 0xa0,r0
bf rl_check_fail_near
// Torque fraction, torque command, q and law output in thousandths, and an
// efficiency of 1..1000.
mov.w @(rl_sc_u_one,pc),r3
mov.w @(0xe,r6),r0
extu.w r0,r0
cmp/hi r3,r0
bt rl_check_fail_near
mov.w @(0x16,r6),r0
extu.w r0,r0
cmp/hi r3,r0
bt rl_check_fail_near
mov.w @(0x1a,r6),r0
extu.w r0,r0
cmp/hi r3,r0
bt rl_check_fail_near
mov.w @(0x16,r7),r0
extu.w r0,r0
cmp/hi r3,r0
bt rl_check_fail_near
mov.w @(0xc,r7),r0
extu.w r0,r0
add -0x1,r0
cmp/hs r3,r0
bt rl_check_fail_near
// The effective command exceeds the stock command by the applied trim.
mov.b @(0x8,r7),r0
extu.b r0,r1
mov.b @(0x9,r7),r0
extu.b r0,r0
sub r1,r0
mov r0,r1
mov.b @(0xa,r7),r0
cmp/eq r0,r1
bf rl_check_fail_near
// Without ready, q is zero. Ready needs ACTIVE hold, an applied trim within
// the latched trim and the q of the regulator law.
mov.b @(0xb,r7),r0
tst r0,r0
bf rl_check_ready
mov.w @(0x1a,r6),r0
tst r0,r0
bf rl_check_fail
bra rl_check_phase
nop
// The range checks above lie beyond the bt/bf reach of rl_check_fail.
rl_check_fail_near:
bra rl_check_fail
nop
rl_check_ready:
mov.b @r6,r0
cmp/eq 0x1,r0
bf rl_check_fail
mov.b @(0x5,r6),r0
cmp/eq 0x1,r0
bf rl_check_fail
mov #0x1e,r0
mov.b @(r0,r6),r0
mov r0,r1
mov.b @(0xa,r7),r0
cmp/hs r0,r1
bf rl_check_fail
mov.b @r7,r0
mov r0,r1
mov.w @(0x16,r7),r0
mov r0,r2
mov.w @(0xc,r7),r0
extu.w r0,r3
mov.l @(rl_sc_q_entry,pc),r0
jsr @r0
nop
mov r0,r1
mov.w @(0x1a,r6),r0
extu.w r0,r0
cmp/eq r1,r0
bf rl_check_fail
rl_check_phase:
mov.b @r6,r0
cmp/eq 0x1,r0
bt rl_check_active
cmp/eq 0x2,r0
bt rl_check_cooldown
// IDLE: observe, no regulator, no timers and no latched trim.
mov.b @(0x5,r6),r0
mov r0,r1
mov.b @r7,r0
or r0,r1
mov.w @(0x6,r6),r0
or r0,r1
mov.w @(0x8,r6),r0
or r0,r1
mov #0x1e,r0
mov.b @(r0,r6),r0
or r0,r1
tst r1,r1
bf rl_check_fail
bra rl_check_views
nop
rl_check_cooldown:
mov.w @(0x8,r6),r0
cmp/pz r0
bf rl_check_fail
bra rl_check_views
nop
rl_check_active:
mov.w @(0x8,r6),r0
tst r0,r0
bf rl_check_fail
mov.w @(0x6,r6),r0
cmp/pz r0
bf rl_check_fail
mov.b @r7,r0
cmp/eq 0x1,r0
bt rl_check_rpm
cmp/eq 0x2,r0
bf rl_check_fail
// SPEED: the RPM loop is zero and the speed fields agree.
mov.w @(0x1c,r7),r0
mov r0,r1
mov.w @(0xc,r6),r0
cmp/eq r0,r1
bf rl_check_fail
mov.w @(0x14,r6),r0
mov r0,r1
mov.w @(0x18,r6),r0
or r0,r1
tst r1,r1
bf rl_check_fail
mov.w @(0x2,r7),r0
mov r0,r1
mov.w @(0x10,r6),r0
cmp/eq r0,r1
bf rl_check_fail
mov.w @(0x16,r7),r0
mov r0,r1
mov.w @(0xe,r6),r0
cmp/eq r0,r1
bf rl_check_fail
bra rl_check_views
nop
// RPM: a target of 1..32767, a zero speed loop and agreeing RPM fields.
rl_check_rpm:
mov.w @(0x14,r6),r0
cmp/pl r0
bf rl_check_fail
mov r0,r1
mov.w @(0x1c,r7),r0
cmp/eq r0,r1
bf rl_check_fail
mov.l @(0xc,r6),r0
mov r0,r1
mov.l @(0x10,r6),r0
or r0,r1
mov.w @(0x16,r6),r0
or r0,r1
tst r1,r1
bf rl_check_fail
mov.w @(0x2,r7),r0
mov r0,r1
mov.w @(0x18,r6),r0
cmp/eq r0,r1
bf rl_check_fail
rl_check_views:
bsr rolling_launch_load_views
nop
mov.l @(0xc,r7),r0
cmp/eq r0,r3
bf rl_check_fail
mov.w @(0x1e,r7),r0
extu.w r0,r0
// r1 = 0 marks a valid record; the result moves to T after the SR restore.
xor r0,r1
rl_check_return:
lds.l @r15+,pr
mov.l @r15+,r0
ldc r0,sr
tst r1,r1
rts
nop
rl_check_fail:
mov #0x1,r1
bra rl_check_return
nop


// Wire views of the stored applied trim, ready and efficiency.
rolling_launch_load_views:
mov.b @(0xa,r7),r0
extu.b r0,r1
mov.b @(0xb,r7),r0
extu.b r0,r2
mov.w @(0xc,r7),r0
extu.w r0,r3

rolling_launch_views:
mov.b @r7,r0
cmp/eq 0x2,r0
mov r1,r0
bf rl_views_kind
or 0x40,r0
rl_views_kind:
tst r2,r2
bt rl_views_ready
or 0x80,r0
rl_views_ready:
mov r0,r1
and 0xc0,r0
shll8 r0
or r3,r0
shll16 r3
or r0,r3
mov.b @(0x1,r7),r0
and 0x7,r0
shll2 r0
mov r0,r2
mov.b @r7,r0
or r0,r2
mov #0x14,r0
mov.b @(r0,r7),r0
cmp/eq 0x2,r0
bf rl_views_cancel
add 0x20,r2
rl_views_cancel:
cmp/eq 0x20,r0
bf rl_views_released
add 0x40,r2
rl_views_released:
mov r1,r0
and 0x80,r0
or r2,r0
shll8 r1
or r0,r1
rts
nop

.align 4
rl_sc_state_address:
.long 0xFFFF5D40
rl_sc_extension_address:
.long 0xFFFF6100
rl_sc_byte_limits:
.long 0x000D71EA
rl_sc_q_entry:
.long 0x000D661A
rl_sc_u_one:
.word 1000
// Offset and maximum pairs: phase, reason, map, mode, latched trim and the
// reserved byte of the base; kind, input_status, applied trim and ready of
// the extension, whose offsets carry bit 7.
rl_sc_byte_limit_table:
.byte 0x00,0x02,0x01,0x19,0x04,0x04,0x05,0x01,0x1e,0x28,0x1f,0x00
.byte 0x80,0x02,0x81,0x1f,0x8a,0x28,0x8b,0x01
