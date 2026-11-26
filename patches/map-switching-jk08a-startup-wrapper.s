// Startup wrapper for the JK08A five-slot selector with cold/warm separation,
// cruise-free state init, and two-copy ping-pong EEPROM boot restore.
//
// Cold vs warm classification uses the immutable stock return address 0x00027C4C
// from the warm operational reinit caller (0x00027C48: bsr 0x00027CE4). It checks
// both direct incoming PR (standalone Map Switching) and the caller-saved PR at
// @(4,r15) (when Rolling Launch's startup wrapper sits between 0x00027CE4 and
// this entry). Cold boot publishes map 1 before 0x0002C648, then runs
// eeprom_boot_restore (which initializes cruise-free RAM and restores the newest
// valid EEPROM slot) and commits limiter shadows. Warm operational reinit runs
// 0x0002C648 while preserving the live selector, cruise-free RAM, and active
// EEPROM persistence state, then recommits limiter shadows for the preserved slot.

.org 0x000D22A0
startup_wrapper:
sts.l pr,@-r15
mov.l @(startup_warm_pr,pc),r1
mov.l @r15,r0
cmp/eq r1,r0
bt startup_warm_reinit
mov.l @(0x4,r15),r0
cmp/eq r1,r0
bt startup_warm_reinit

// Cold boot path: safe map 1 before stock init, then cruise-free + EEPROM restore.
mov.l @(startup_selector_state,pc),r1
mov #0x0,r0
mov.b r0,@r1
mov.l @(startup_stock_initializer,pc),r0
jsr @r0
nop
mov.l @(startup_eeprom_boot_restore,pc),r0
jsr @r0
nop
mov r0,r4
bra startup_do_commit
nop

// Warm reinit path: keep selector, cruise-free, and EEPROM state intact.
startup_warm_reinit:
mov.l @(startup_stock_initializer,pc),r0
jsr @r0
nop
mov.l @(startup_selector_state,pc),r1
mov.b @r1,r0
extu.b r0,r4
mov #0x4,r1
cmp/hi r1,r4
bf startup_do_commit
mov #0x0,r4

startup_do_commit:
mov.l @(startup_commit_entry,pc),r0
jsr @r0
nop
lds.l @r15+,pr
rts
nop

.align 4
startup_stock_initializer:
.long 0x0002C648
startup_selector_state:
.long 0xFFFF5D00
startup_commit_entry:
.long 0x000D3660
startup_eeprom_boot_restore:
.long 0x000D7210
startup_warm_pr:
.long 0x00027C4C
