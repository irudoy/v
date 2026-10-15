! Bounded CAN latch caller and its natural byte copier at stock addresses.
    .text
    .balign 4
can_latch_copy:
    mov.l source_pointer,r2
    jsr @r11
    mov #12,r0
    .org 0x210f4 - 0x21094
helper_pointer:
    .long 0x00022558
    .org 0x21234 - 0x21094
destination_origin:
    .long 0xffff4188
    .org 0x2125c - 0x21094
source_pointer:
    .long 0xffff4194
    .org 0x22558 - 0x21094
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
