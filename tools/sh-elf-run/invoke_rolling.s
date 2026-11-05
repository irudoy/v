    ! Simulator-only call helper of the Rolling Launch GNU gate.
    !
    ! uint32_t invoke_regs(uint32_t entry, uint32_t *regs)
    ! regs[1..14] hold r1..r14 on entry to the callee, and the T, S, I, Q
    ! and M bits of regs[15] replace those of SR; the simulator keeps its
    ! other SR bits. On return regs[0..14] hold r0..r14 and regs[15] holds SR
    ! after the callee, and the result is the callee r0. The helper calls the
    ! entry through r0, so no entry receives an r0 argument. It restores the
    ! r8..r14 and PR of its C caller.
    .text
    .balign 2
    .global _invoke_regs
    .type _invoke_regs,@function
_invoke_regs:
    sts.l pr,@-r15
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    mov.l r5,@-r15
    stc sr,r0
    mov.w @(invoke_sr_bits,pc),r2
    not r2,r3
    and r3,r0
    mov.l @(60,r5),r1
    and r2,r1
    or r1,r0
    ldc r0,sr
    mov r4,r0
    mov.l @(4,r5),r1
    mov.l @(8,r5),r2
    mov.l @(12,r5),r3
    mov.l @(16,r5),r4
    mov.l @(24,r5),r6
    mov.l @(28,r5),r7
    mov.l @(32,r5),r8
    mov.l @(36,r5),r9
    mov.l @(40,r5),r10
    mov.l @(44,r5),r11
    mov.l @(48,r5),r12
    mov.l @(52,r5),r13
    mov.l @(56,r5),r14
    mov.l @(20,r5),r5
    jsr @r0
    nop
    mov.l r0,@-r15
    stc sr,r0
    mov.l r0,@-r15
    mov.l @(8,r15),r0
    mov.l r1,@(4,r0)
    mov.l r2,@(8,r0)
    mov.l r3,@(12,r0)
    mov.l r4,@(16,r0)
    mov.l r5,@(20,r0)
    mov.l r6,@(24,r0)
    mov.l r7,@(28,r0)
    mov.l r8,@(32,r0)
    mov.l r9,@(36,r0)
    mov.l r10,@(40,r0)
    mov.l r11,@(44,r0)
    mov.l r12,@(48,r0)
    mov.l r13,@(52,r0)
    mov.l r14,@(56,r0)
    mov r0,r1
    mov.l @r15+,r0
    mov.l r0,@(60,r1)
    mov.l @r15+,r0
    mov.l r0,@r1
    add #4,r15
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    lds.l @r15+,pr
    rts
    nop
    .balign 2
invoke_sr_bits:
    .short 0x03f3
    .size _invoke_regs,.-_invoke_regs
