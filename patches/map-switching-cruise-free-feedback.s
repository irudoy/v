// JK08A MIL feedback extension and stationary tachometer wrappers.
//
// Provides:
//   - cruise_free_feedback_ext @ 0x000D6BE0: validates MSCF v2 via shared
//     cf_validate_cfg_local (0x000D6AE8), enforces the 10.24 ms tachometer and
//     Rolling Launch priority interlock via cf_tach_gate_check, and returns 1
//     if flags.bit3 (mil_enabled) is set else 0.
//   - cf_tach_gate_check @ 0x000D6C08: shared 10.24 ms interlock for
//     tach_mode=1 (stationary menu) and tach_mode=2 (brake+APP RPM==0).
//   - tach_180_wrapper @ 0x000D6CA0: hooked at 0x000C3F98 (stock 0x000C577A).
//   - tach_1f9_wrapper @ 0x000D6CC0: hooked at 0x000C3FA8 (stock 0x000C5236).
//   - tach_override_apply @ 0x000D6CE0: hard-interlocked BE16(slot * 0x1F40)
//     override for 0x180 (0xFFFF3AFD..3AFE) and 0x1F9 (0xFFFF3AE1..3AE2).
//   - cf_stationary_live @ 0x000D6D1C: shared live stationary predicate.
//   - cf_accel_pressed @ 0x000D6D58: shared APP1/APP2 > app_release_max test.
//
// Uses only caller-saved r0..r7, MACL, and PR.

// ---------------------------------------------------------------------------
// 1. cruise_free_feedback_ext @ 0x000D6BE0
// ---------------------------------------------------------------------------
.org 0x000D6BE0
cruise_free_feedback_ext:
sts.l pr,@-r15
mov.l @(fbext_config,pc),r6
mov.l @(fbext_cf_ram,pc),r5
bsr 0x000D6AE8
nop
tst r0,r0
bt fbext_exit
bsr cf_tach_gate_check
nop
mov.b @(0x5,r6),r0
tst 0x8,r0
bt fbext_mil_off
mov #0x1,r0
bra fbext_exit
nop
fbext_mil_off:
mov #0x0,r0
fbext_exit:
lds.l @r15+,pr
rts
nop

// ---------------------------------------------------------------------------
// 2. cf_tach_gate_check
// Input: r5 = CF RAM base, r6 = validated MSCF v2 config base.
// Output: r0 = active tach_slot (1..5) if override permitted, else 0.
// Preserves r4, r5, r6, r7. Clobbers r0..r3.
// ---------------------------------------------------------------------------
cf_tach_gate_check:
sts.l pr,@-r15
mov.b @(0x5,r6),r0
tst 0x4,r0
bt tach_gate_clear
mov.b @(0x6,r5),r0
extu.b r0,r2
tst r2,r2
bt tach_gate_clear
mov.b @(0x7,r5),r0
extu.b r0,r3
add -0x1,r3
mov #0x5,r1
cmp/hs r1,r3
bt tach_gate_clear

mov r2,r0
cmp/eq 0x1,r0
bt tach_gate_mode1
cmp/eq 0x2,r0
bf tach_gate_clear

// tach_mode == 2 (brake+APP): strictly RPM == 0 && live stationary contract.
mov.l @(tach_rpm_fine,pc),r1
mov.w @r1,r0
extu.w r0,r0
tst r0,r0
bf tach_gate_clear
mov.l @(tach_rpm_coarse,pc),r1
mov.b @r1,r0
extu.b r0,r0
tst r0,r0
bf tach_gate_clear
bsr cf_stationary_live
nop
bf tach_gate_clear
bra tach_gate_ok
nop

// tach_mode == 1 (stationary menu): accel pressed aborts menu + tach immediately
// (Rolling Launch priority); motion clears tach immediately while keeping menu
// state so selector_host commits the selected map on its next tick.
tach_gate_mode1:
bsr cf_accel_pressed
nop
bt tach_gate_abort_menu
bsr cf_stationary_live
nop
bf tach_gate_clear

tach_gate_ok:
mov.b @(0x7,r5),r0
extu.b r0,r0
bra tach_gate_done
nop

tach_gate_abort_menu:
mov #0x0,r0
mov.w r0,@(0xA,r5)
mov.w r0,@(0xC,r5)
tach_gate_clear:
mov #0x0,r0
mov.w r0,@(0x6,r5)
tach_gate_done:
lds.l @r15+,pr
rts
nop

.align 4
fbext_config:
.long 0x000D6800
fbext_cf_ram:
.long 0xFFFF6000
tach_rpm_fine:
.long 0xFFFF11EE
tach_rpm_coarse:
.long 0xFFFF11BC

// ---------------------------------------------------------------------------
// 3. tach_180_wrapper @ 0x000D6CA0 (32 bytes)
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
// 4. tach_1f9_wrapper @ 0x000D6CC0 (32 bytes)
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
// 5. tach_override_apply @ 0x000D6CE0 (60 bytes)
// Input: r4 = address of big-endian RPM high byte in CAN TX payload buffer.
// ---------------------------------------------------------------------------
.org 0x000D6CE0
tach_override_apply:
sts.l pr,@-r15
mov.l @(tach_config,pc),r6
mov.l @(tach_cf_ram,pc),r5
bsr 0x000D6AE8
nop
tst r0,r0
bt tach_return
bsr cf_tach_gate_check
nop
tst r0,r0
bt tach_return

// Compute wire = tach_slot * 0x1F40 (1000..5000 RPM at wire/8 RPM).
mov.w @(tach_wire_step,pc),r3
extu.w r3,r3
mulu.w r0,r3
sts macl,r1
mov r1,r0
shlr8 r0
mov.b r0,@r4
mov r1,r0
mov.b r0,@(0x1,r4)

tach_return:
lds.l @r15+,pr
rts
nop

.align 4
tach_config:
.long 0x000D6800
tach_cf_ram:
.long 0xFFFF6000
tach_wire_step:
.word 0x1F40

// ---------------------------------------------------------------------------
// 6. cf_stationary_live @ 0x000D6D1C (60 bytes)
// Input: r5 = CF RAM base, r6 = validated MSCF config base.
// Output: T = 1 iff both live RX gates, observed|valid, raw==0, and age<=limit.
// Preserves r2, r4, r5, r6, r7. Clobbers r0, r1, r3.
// ---------------------------------------------------------------------------
.org 0x000D6D1C
cf_stationary_live:
mov.l @(cf_live_port,pc),r1
mov.b @r1,r0
tst 0x80,r0
bt cf_live_bad
mov.l @(cf_live_hcan,pc),r1
mov.b @r1,r0
tst 0x1,r0
bt cf_live_bad
mov.b @r5,r0
and 0x3,r0
cmp/eq 0x3,r0
bf cf_live_bad
mov.w @(0x2,r5),r0
extu.w r0,r0
tst r0,r0
bf cf_live_bad
mov.b @(0x1,r5),r0
extu.b r0,r3
mov.b @(0x7,r6),r0
extu.b r0,r0
cmp/hs r3,r0
rts
nop
cf_live_bad:
mov #0x1,r0
tst r0,r0
rts
nop

.align 4
cf_live_port:
.long 0xFFFF4185
cf_live_hcan:
.long 0xFFFF4195

// ---------------------------------------------------------------------------
// 7. cf_accel_pressed @ 0x000D6D5C (36 bytes)
// Input: r6 = validated MSCF v2 config base.
// Output: T = 1 iff APP1 > app_release_max or APP2 > app_release_max.
// Preserves r2, r4, r5, r6, r7. Clobbers r0, r1, r3.
// ---------------------------------------------------------------------------
.org 0x000D6D5C
cf_accel_pressed:
mov.w @(0x10,r6),r0
extu.w r0,r3
mov.l @(tach_app1,pc),r1
mov.w @r1,r0
extu.w r0,r0
cmp/hi r3,r0
bt cf_accel_ret
mov.l @(tach_app2,pc),r1
mov.w @r1,r0
extu.w r0,r0
cmp/hi r3,r0
cf_accel_ret:
rts
nop

.align 4
tach_app1:
.long 0xFFFF269E
tach_app2:
.long 0xFFFF26A2
