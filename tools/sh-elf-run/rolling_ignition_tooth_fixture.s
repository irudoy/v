! Simulator-only tooth context after the original ISR prologue.
! The bounded fixture executes the stock arming and recovery instructions,
! then the original epilogue. Crank decoding and unrelated dispatch are absent.
    .section .tooth_fixture,"ax"
    .balign 4
    .global _rolling_tooth_fixture
_rolling_tooth_fixture:
    mov.l .Ltooth_log,r3
    mov.l .Ltooth_state,r1
    mov.b @r1,r2
    extu.b r2,r2
    mov.l r2,@r3
    mov.b @(5,r1),r0
    extu.b r0,r2
    mov.l r2,@(4,r3)
    mov.w @(0x1a,r1),r0
    extu.w r0,r2
    mov.l r2,@(8,r3)
    mov.l .Ltooth_extension,r1
    mov.b @(0xb,r1),r0
    extu.b r0,r2
    mov.l r2,@(12,r3)
    mov.b @r1,r2
    extu.b r2,r2
    mov.l r2,@(16,r3)
    mov.w @(0x16,r1),r0
    extu.w r0,r2
    mov.l r2,@(20,r3)
    mov.w @(0xc,r1),r0
    extu.w r0,r2
    mov.l r2,@(24,r3)
    mov.b @(0xa,r1),r0
    extu.b r0,r2
    mov.l r2,@(28,r3)
    mov.l .Ltooth_r8,r8
    mov.l .Ltooth_r9,r9
    mov.l .Ltooth_r14,r14
    mov.l .Ltooth_entry,r0
    jmp @r0
    nop
    .balign 4
.Ltooth_r8: .long 0xffff128c
.Ltooth_r9: .long 0xffff1ff4
.Ltooth_r14: .long 0xffff84fb
.Ltooth_entry: .long 0x000292ec
.Ltooth_log: .long _rolling_irq_observation
.Ltooth_state: .long 0xffff5d40
.Ltooth_extension: .long 0xffff6100

    .org 0x100
    .global _rolling_tooth_fixture_exit
_rolling_tooth_fixture_exit:
    mov.l .Lexit_log,r3
    mov.l .Lexit_extension,r1
    mov.l @(0x10,r1),r2
    mov.l r2,@(32,r3)
    mov.w @(0x18,r1),r0
    extu.w r0,r2
    mov.l r2,@(36,r3)
    mov.l .Lexit_state,r1
    add #0x1d,r1
    mov.b @r1,r2
    extu.b r2,r2
    mov.l r2,@(40,r3)
    mov r15,r2
    add #108,r2
    mov.l r2,@(44,r3)
    mov #1,r2
    mov.l r2,@(48,r3)
    mov.l .Lexit_epilogue,r0
    jmp @r0
    nop
    .balign 4
.Lexit_log: .long _rolling_irq_observation
.Lexit_extension: .long 0xffff6100
.Lexit_state: .long 0xffff5d40
.Lexit_epilogue: .long 0x0002a294
