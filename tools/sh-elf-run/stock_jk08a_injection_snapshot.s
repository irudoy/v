! JK08A scheduler slice at 00021314 and its real byte copier at 00022558.
! R11=00022558 and R12=140 are explicit inputs of the bounded caller.
    .text
    .balign 4
injection_snapshot:
    mov.l snapshot_pointer,r1
    mov.l live_pointer,r2
    jsr @r11
    mov r12,r0
    .org 0x213a0 - 0x21314
snapshot_pointer:
    .long 0xffff2330
live_pointer:
    .long 0xffff23bc
    .org 0x22558 - 0x21314
byte_copy:
    mov.l r2,@-r15
    mov.l r3,@-r15
    mov.l r4,@-r15
    cmp/eq #0,r0
    bt copy_return
    mov r2,r4
    add r0,r4
copy_loop:
    mov.b @r2+,r0
    mov.b r0,@r1
    cmp/hi r2,r4
    bf copy_return
    mov.b @r2+,r0
    mov.b r0,@(1,r1)
    cmp/hi r2,r4
    bf copy_return
    mov.b @r2+,r0
    mov.b r0,@(2,r1)
    cmp/hi r2,r4
    bf copy_return
    mov.b @r2+,r0
    mov.b r0,@(3,r1)
    cmp/hi r2,r4
    add #4,r1
    bt copy_loop
copy_return:
    mov.l @r15+,r4
    mov.l @r15+,r3
    rts
    mov.l @r15+,r2
