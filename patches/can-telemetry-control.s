// HCAN1 mailbox-31 initialization and polled telemetry control for exact JK08A.
//
// Both stock HCAN1 initialization paths call the wrapper. The stock routine
// leaves mailbox 31 inactive and its activity interrupt masked. The wrapper
// validates the producer configuration, clears stale receive flags, programs
// the derived control ID, and changes MBC to receive only after every other
// mailbox field is complete.

.org 0x000D4E10
telemetry_hcan1_init_wrapper:
sts.l pr,@-r15
mov.l @(telemetry_control_stock_hcan1_init,pc),r0
jsr @r0
nop
mov.l r0,@-r15
bsr telemetry_control_config_valid
nop
tst r0,r0
bt telemetry_control_init_return

mov.l @(telemetry_control_config,pc),r4
mov.w @(0x8,r4),r0
add 0x1,r0
shll2 r0
shll2 r0
mov.l @(telemetry_control_mailbox31,pc),r1
mov.w r0,@r1
mov #0x0,r0
mov.w r0,@(0x2,r1)
mov.w r0,@(0x6,r1)
mov.w r0,@(0x10,r1)
mov.w r0,@(0x12,r1)

mov.l @(telemetry_control_mbimr1,pc),r2
mov.w @r2,r0
mov.w @(telemetry_control_mailbox31_mask,pc),r3
or r3,r0
mov.w r0,@r2
mov.l @(telemetry_control_rxpr1,pc),r2
mov.w r3,@r2
mov.l @(telemetry_control_rfpr1,pc),r2
mov.w r3,@r2
mov.l @(telemetry_control_umsr1,pc),r2
mov.w r3,@r2

mov.w @(telemetry_control_receive_dlc8,pc),r0
mov.w r0,@(0x4,r1)

telemetry_control_init_return:
mov.l @r15+,r0
lds.l @r15+,pr
rts
nop

.align 4
telemetry_control_stock_hcan1_init:
.long 0x000C338A
telemetry_control_config:
.long 0x000D4E00
telemetry_control_mailbox31:
.long 0xFFFFDCE0
telemetry_control_rxpr1:
.long 0xFFFFD840
telemetry_control_rfpr1:
.long 0xFFFFD848
telemetry_control_mbimr1:
.long 0xFFFFD850
telemetry_control_umsr1:
.long 0xFFFFD858
telemetry_control_mailbox31_mask:
.word 0x8000
telemetry_control_receive_dlc8:
.word 0x0208

.org 0x000D4EA0
telemetry_control_poll:
sts.l pr,@-r15
bsr telemetry_control_config_valid
nop
tst r0,r0
bt telemetry_control_poll_return

mov.l @(telemetry_control_rxpr1_poll,pc),r1
mov.w @r1,r0
mov.w @(telemetry_control_mailbox31_mask_poll,pc),r2
tst r2,r0
bf telemetry_control_poll_data
mov.l @(telemetry_control_rfpr1_poll,pc),r3
mov.w @r3,r0
tst r2,r0
bf telemetry_control_poll_clear
bra telemetry_control_poll_return
nop

telemetry_control_poll_data:
mov.l @(telemetry_control_mailbox31_poll,pc),r4
mov.w @r4,r0
tst 0x8,r0
bf telemetry_control_poll_clear
mov.b @(0x5,r4),r0
cmp/eq 0x8,r0
bf telemetry_control_poll_clear
mov.l @(0x8,r4),r0
mov.l @(0xC,r4),r1

mov.l @(telemetry_control_rxpr1_poll,pc),r3
mov.w r2,@r3
mov.l @(telemetry_control_rfpr1_poll,pc),r3
mov.w r2,@r3
mov.l @(telemetry_control_umsr1_poll,pc),r3
mov.w r2,@r3

mov.l @(telemetry_control_command_magic,pc),r2
cmp/eq r2,r0
bf telemetry_control_poll_return
mov.l @(telemetry_control_start_tail,pc),r2
cmp/eq r2,r1
bt telemetry_control_start
mov.l @(telemetry_control_stop_tail,pc),r2
cmp/eq r2,r1
bt telemetry_control_stop
bra telemetry_control_poll_return
nop

telemetry_control_poll_clear:
mov.l @(telemetry_control_rxpr1_poll,pc),r3
mov.w r2,@r3
mov.l @(telemetry_control_rfpr1_poll,pc),r3
mov.w r2,@r3
mov.l @(telemetry_control_umsr1_poll,pc),r3
mov.w r2,@r3
bra telemetry_control_poll_return
nop

telemetry_control_start:
mov.l @(telemetry_control_state,pc),r3
mov #0x1,r0
mov.b r0,@(0xB,r3)
mov.l @(telemetry_control_config_poll,pc),r4
mov.b @(0x6,r4),r0
add -0x1,r0
mov.b r0,@(0xA,r3)
bra telemetry_control_poll_return
nop

telemetry_control_stop:
mov.l @(telemetry_control_state,pc),r3
mov #0x2,r0
mov.b r0,@(0xB,r3)
mov #0x0,r0
mov.b r0,@(0x1,r3)
mov.b r0,@(0xA,r3)

telemetry_control_poll_return:
lds.l @r15+,pr
rts
nop

telemetry_control_config_valid:
mov.l @(telemetry_control_config_poll,pc),r4
mov.w @r4,r0
mov.w @(telemetry_control_config_magic,pc),r1
cmp/eq r1,r0
bf telemetry_control_config_invalid
mov.b @(0x2,r4),r0
cmp/eq 0x2,r0
bf telemetry_control_config_invalid
mov.b @(0x3,r4),r0
extu.b r0,r0
mov #0x1,r1
cmp/hi r1,r0
bt telemetry_control_config_invalid
mov.b @(0x4,r4),r0
cmp/eq 0x5,r0
bf telemetry_control_config_invalid
mov.b @(0x5,r4),r0
cmp/eq 0xB,r0
bf telemetry_control_config_invalid
mov.b @(0x6,r4),r0
tst r0,r0
bt telemetry_control_config_invalid
mov.b @(0x7,r4),r0
tst r0,r0
bf telemetry_control_config_invalid
mov.w @(0x8,r4),r0
extu.w r0,r0
tst r0,r0
bt telemetry_control_config_invalid
mov.w @(telemetry_control_data_can_id_max,pc),r1
cmp/hi r1,r0
bt telemetry_control_config_invalid
mov.w @(0xA,r4),r0
mov.w @(telemetry_control_profile_crc,pc),r1
cmp/eq r1,r0
bf telemetry_control_config_invalid
mov.l @(0xC,r4),r0
mov.l @(telemetry_control_config_integrity,pc),r1
cmp/eq r1,r0
bf telemetry_control_config_invalid
mov #0x1,r0
rts
nop

telemetry_control_config_invalid:
mov #0x0,r0
rts
nop

.align 4
telemetry_control_rxpr1_poll:
.long 0xFFFFD840
telemetry_control_rfpr1_poll:
.long 0xFFFFD848
telemetry_control_umsr1_poll:
.long 0xFFFFD858
telemetry_control_mailbox31_poll:
.long 0xFFFFDCE0
telemetry_control_state:
.long 0xFFFF5E00
telemetry_control_config_poll:
.long 0x000D4E00
telemetry_control_command_magic:
.long 0x54454C32
telemetry_control_start_tail:
.long 0x0201B632
telemetry_control_stop_tail:
.long 0x0200A613
telemetry_control_config_integrity:
.long 0x54454C32
telemetry_control_mailbox31_mask_poll:
.word 0x8000
telemetry_control_config_magic:
.word 0x4354
telemetry_control_data_can_id_max:
.word 0x07FE
telemetry_control_profile_crc:
.word 0xE144
