// JK08A multi-channel feedback extension and stationary tachometer wrappers.
//
// Provides:
//   - cruise_free_feedback_ext @ 0x000D6BE0: validates MSCF config, ticks and
//     interlocks optional tachometer hold state, and returns lamp_mask (bits
//     0..1 of feedback_mode) to cruise_feedback_engine.
//   - tach_180_wrapper @ 0x000D6CA0: hooked at 0x000C3F98 (stock 0x000C577A).
//   - tach_1f9_wrapper @ 0x000D6CC0: hooked at 0x000C3FA8 (stock 0x000C5236).
//   - tach_override_apply @ 0x000D6CE0: hard-interlocked BE16(slot * 0x1F40)
//     override for 0x180 (0xFFFF3AFD..3AFE) and 0x1F9 (0xFFFF3AE1..3AE2).
//
// Uses only caller-saved r0..r7, MACL, and PR.

// ---------------------------------------------------------------------------
// 1. cruise_free_feedback_ext @ 0x000D6BE0 (192 bytes)
// ---------------------------------------------------------------------------
.org 0x000D6BE0
cruise_free_feedback_ext:
mov.l @(fbext_config,pc),r6
mov.l @(fbext_cf_ram,pc),r5

// Validate MSCF magic, version, reserved words, and sentinel.
mov.l @r6,r1
mov.l @(fbext_magic,pc),r2
cmp/eq r2,r1
bf fbext_invalid_cfg
mov.b @(0x4,r6),r0
cmp/eq 0x1,r0
bf fbext_invalid_cfg
mov.l @(0x1C,r6),r1
mov.l @(fbext_sentinel,pc),r2
cmp/eq r2,r1
bf fbext_invalid_cfg
mov.l @(0x18,r6),r1
tst r1,r1
bf fbext_invalid_cfg
mov r6,r1
add 0x16,r1
mov.w @r1,r0
extu.w r0,r0
tst r0,r0
bf fbext_invalid_cfg

// Advance or clear tach_ticks countdown under hard RPM==0 && stationary gate.
mov.b @(0x6,r5),r0
extu.b r0,r2
tst r2,r2
bt fbext_clear_orphan_slot
mov.b @(0x5,r6),r0
tst 0x4,r0
bt fbext_clear_tach
mov.b @(0x6,r6),r0
tst 0x4,r0
bt fbext_clear_tach
mov.b @(0x7,r5),r0
extu.b r0,r3
tst r3,r3
bt fbext_clear_tach
mov #0x6,r1
cmp/hs r1,r3
bt fbext_clear_tach
mov.l @(fbext_rpm_fine,pc),r1
mov.w @r1,r0
extu.w r0,r0
tst r0,r0
bf fbext_clear_tach
mov.l @(fbext_rpm_coarse,pc),r1
mov.b @r1,r0
extu.b r0,r0
tst r0,r0
bf fbext_clear_tach
mov.b @r5,r0
and 0x3,r0
cmp/eq 0x3,r0
bf fbext_clear_tach

add -0x1,r2
mov r2,r0
mov.b r0,@(0x6,r5)
tst r2,r2
bf fbext_return_lamp
mov.b r0,@(0x7,r5)
bra fbext_return_lamp
nop

fbext_clear_orphan_slot:
mov #0x0,r0
mov.b r0,@(0x7,r5)
bra fbext_return_lamp
nop

fbext_clear_tach:
mov #0x0,r0
mov.b r0,@(0x6,r5)
mov.b r0,@(0x7,r5)

fbext_return_lamp:
mov.b @(0x6,r6),r0
and 0x3,r0
rts
nop

fbext_invalid_cfg:
mov #0x0,r0
mov.b r0,@(0x6,r5)
mov.b r0,@(0x7,r5)
rts
nop

.align 4
fbext_config:
.long 0x000D6800
fbext_cf_ram:
.long 0xFFFF6000
fbext_magic:
.long 0x4D534346
fbext_sentinel:
.long 0xA55A5AA5
fbext_rpm_fine:
.long 0xFFFF11EE
fbext_rpm_coarse:
.long 0xFFFF11BC

// ---------------------------------------------------------------------------
// 2. tach_180_wrapper @ 0x000D6CA0 (32 bytes)
// Hooked at 0x000C3F98 (stock 0x000C577A).
// ---------------------------------------------------------------------------
.org 0x000D6CA0
tach_180_wrapper:
sts.l pr,@-r15
mov.l @(tach_stock_180,pc),r0
jsr @r0
nop
mov.l @(tach_180_payload,pc),r4
bsr tach_override_apply
nop
lds.l @r15+,pr
rts
nop

.align 4
tach_stock_180:
.long 0x000C577A
tach_180_payload:
.long 0xFFFF3AFD

// ---------------------------------------------------------------------------
// 3. tach_1f9_wrapper @ 0x000D6CC0 (32 bytes)
// Hooked at 0x000C3FA8 (stock 0x000C5236).
// ---------------------------------------------------------------------------
.org 0x000D6CC0
tach_1f9_wrapper:
sts.l pr,@-r15
mov.l @(tach_stock_1f9,pc),r0
jsr @r0
nop
mov.l @(tach_1f9_payload,pc),r4
bsr tach_override_apply
nop
lds.l @r15+,pr
rts
nop

.align 4
tach_stock_1f9:
.long 0x000C5236
tach_1f9_payload:
.long 0xFFFF3AE1

// ---------------------------------------------------------------------------
// 4. tach_override_apply @ 0x000D6CE0 (160 bytes)
// Input: r4 = address of big-endian RPM high byte in CAN TX payload buffer.
// ---------------------------------------------------------------------------
.org 0x000D6CE0
tach_override_apply:
mov.l @(tach_config,pc),r6
mov.l @(tach_cf_ram,pc),r5

mov.l @r6,r1
mov.l @(tach_magic,pc),r2
cmp/eq r2,r1
bf tach_return
mov.b @(0x4,r6),r0
cmp/eq 0x1,r0
bf tach_return
mov.l @(0x1C,r6),r1
mov.l @(tach_sentinel,pc),r2
cmp/eq r2,r1
bf tach_return
mov.b @(0x5,r6),r0
tst 0x4,r0
bt tach_return
mov.b @(0x6,r6),r0
tst 0x4,r0
bt tach_return

mov.b @(0x6,r5),r0
extu.b r0,r0
tst r0,r0
bt tach_return
mov.b @(0x7,r5),r0
extu.b r0,r2
tst r2,r2
bt tach_return
mov #0x6,r1
cmp/hs r1,r2
bt tach_return

// Hard interlock: strictly RPM == 0 && stationary_valid.
mov.l @(tach_rpm_fine,pc),r1
mov.w @r1,r0
extu.w r0,r0
tst r0,r0
bf tach_abort_clear
mov.l @(tach_rpm_coarse,pc),r1
mov.b @r1,r0
extu.b r0,r0
tst r0,r0
bf tach_abort_clear
mov.b @r5,r0
and 0x3,r0
cmp/eq 0x3,r0
bf tach_abort_clear

// Compute wire = tach_slot * 0x1F40 (1000..5000 RPM at wire/8 RPM).
mov.w @(tach_wire_step,pc),r3
extu.w r3,r3
mulu.w r2,r3
sts macl,r1
mov r1,r0
shlr8 r0
mov.b r0,@r4
mov r1,r0
mov.b r0,@(0x1,r4)
rts
nop

tach_abort_clear:
mov #0x0,r0
mov.b r0,@(0x6,r5)
mov.b r0,@(0x7,r5)
tach_return:
rts
nop

.align 4
tach_config:
.long 0x000D6800
tach_cf_ram:
.long 0xFFFF6000
tach_magic:
.long 0x4D534346
tach_sentinel:
.long 0xA55A5AA5
tach_rpm_fine:
.long 0xFFFF11EE
tach_rpm_coarse:
.long 0xFFFF11BC
tach_wire_step:
.word 0x1F40
