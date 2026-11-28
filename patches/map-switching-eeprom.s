// JK08A two-copy ping-pong EEPROM persistence runtime for Map Switching (#194).
//
// Reserved EEPROM pages (4 KiB ST M95320 on SCI2 0xFFFFF010, CS PCDR.4 0xFFFFF73E):
//   Page A (0x34): 0x0680..0x069F (16-byte record in bytes 0..15; 16..31 preserved)
//   Page B (0x38): 0x0700..0x071F (16-byte record in bytes 0..15; 16..31 preserved)
//
// 16-byte big-endian record layout:
//   +0x00..0x01  "MS" (0x4D, 0x53)
//   +0x02        version (1=legacy slot only, 2=slot + telemetry autostart)
//   +0x03        packed state: low nibble slot (1..5), bit 7 telemetry_autostart
//                (v1 requires bits 7..4 == 0; v2 requires bits 6..4 == 0)
//   +0x04..0x07  monotonic u32 generation
//   +0x08..0x0B  IEEE 802.3 CRC-32 over bytes 0..7
//   +0x0C..0x0F  commit marker (0xA65DC39E valid / 0x00000000 invalid)
//
// 16-byte ROM configuration (MSPE v1) sits at 0x000D7200..0x000D720F.
// Dedicated RAM state sits at 0xFFFF6020..0xFFFF605F (64 bytes, base r8):
//   +0x00  phase             (0=IDLE, 1=PRE_WIP, 2=WAIT_INVAL, 3=WAIT_BODY,
//                             4=WAIT_COMMIT, 5=QUARANTINE)
//   +0x01  active_page       (0=0x0680, 1=0x0700, 0xFF=NONE)
//   +0x02  committed_state   (0=none, else slot 1..5 | (autostart ? 0x80 : 0))
//   +0x03  boot_flags        (bit0=boot_ok, bit1=boot_ambiguous)
//   +0x04  active_generation (u32)
//   +0x08  pending_state     (0 or slot 1..5 | (autostart ? 0x80 : 0))
//   +0x09  dest_page         (0 or 1)
//   +0x0A  debounce_ticks    (u16)
//   +0x0C  wip_ticks         (u8)
//   +0x0D  retry_state       (u8)
//   +0x0E  retry_count       (u8)
//   +0x0F  last_error        (u8, 0..8)
//   +0x10  staged_generation (u32)
//   +0x14  write_count       (u32)
//   +0x18..0x27  staged_record[16]
//   +0x28..0x37  scratch[16]
//   +0x38..0x3F  zero_buf[8] (always 0x00; first 4 bytes supply INVALID_MARKER)
//
// Telemetry autostart handoff uses bits 4..5 of telemetry_status (0xFFFF5E07):
//   bit 4 (0x10) = autostart_enabled (desired state; toggled by 0x6F1 control)
//   bit 5 (0x20) = autostart_saved   (1 when boot_ok && committed matches desired)
//
// All public entries preserve r8..r14 and PR.

// ---------------------------------------------------------------------------
// 1. eeprom_boot_restore @ 0x000D7210
// Called by startup_wrapper on cold boot after stock 0x0002C648.
// Initializes cruise-free RAM (0x000D6820), zeroes persistence RAM, clears
// telemetry_status autostart bits, restores the newest valid slot 0..4 into
// 0xFFFF5D00 and autostart bits into telemetry_status, and returns slot in r0.
// ---------------------------------------------------------------------------
.org 0x000D7210
eeprom_boot_restore:
mov.l r8,@-r15
mov.l r9,@-r15
mov.l r10,@-r15
mov.l r11,@-r15
mov.l r12,@-r15
sts.l pr,@-r15

// Initialize cruise-free RAM state on cold boot.
mov.l @(ee_cruise_free_init_1,pc),r0
jsr @r0
nop

// Zero all 64 bytes of persistence RAM (0xFFFF6020..0xFFFF605F).
mov.l @(ee_ram_base_1,pc),r8
mov r8,r1
mov #0x0,r0
mov #0x10,r2
ee_boot_zero_loop:
mov.l r0,@r1
add 0x4,r1
dt r2
bf ee_boot_zero_loop

// Clear telemetry_status autostart bits (0x30) fail-closed before reading EEPROM.
mov.l @(ee_telemetry_status_1,pc),r1
mov.b @r1,r0
and 0xCF,r0
mov.b r0,@r1

// Default active_page = 0xFF (NONE).
mov #-0x1,r0
mov.b r0,@(0x1,r8)

// Validate MSPE v1 config and enabled bit.
bsr ee_validate_cfg
nop
tst r0,r0
bf ee_boot_cfg_ok
bra ee_boot_ret_map1
nop
ee_boot_cfg_ok:

// Acquire SCI2 for bounded read-only restore.
mov.l @(ee_sci2_acquire_1,pc),r0
jsr @r0
nop

// Check RDSR: reject bus timeout or active WIP (bit 0 set, including 0xFF fault).
bsr ee_spi_rdsr
nop
cmp/pz r0
bf ee_boot_read_fail
tst 0x1,r0
bf ee_boot_read_fail

// Read 16 bytes of Page A (0x0680) into scratch (r8 + 0x28).
mov.w @(ee_page_a_const,pc),r4
mov r8,r5
add 0x28,r5
mov #0x10,r6
bsr ee_spi_read_n
nop
tst r0,r0
bf ee_boot_read_fail
mov r8,r4
add 0x28,r4
bsr ee_decode_record
nop
mov r0,r9
mov r1,r10

// Read 16 bytes of Page B (0x0700) into scratch (r8 + 0x28).
mov.w @(ee_page_b_const,pc),r4
mov r8,r5
add 0x28,r5
mov #0x10,r6
bsr ee_spi_read_n
nop
tst r0,r0
bf ee_boot_read_fail
mov r8,r4
add 0x28,r4
bsr ee_decode_record
nop
mov r0,r11
mov r1,r12

// Release SCI2 before publishing result.
mov.l @(ee_sci2_release_1,pc),r0
jsr @r0
nop

// Select active copy from (state_a=r9, gen_a=r10) and (state_b=r11, gen_b=r12).
tst r9,r9
bf ee_boot_has_a
tst r11,r11
bf ee_boot_pick_b
// Neither page valid: mark boot_ok=1, keep active_page=0xFF, return Map 1 (0).
mov #0x1,r0
mov.b r0,@(0x3,r8)
bra ee_boot_ret_map1
nop

ee_boot_has_a:
tst r11,r11
bt ee_boot_pick_a
// Both pages valid: compare diff = gen_b - gen_a (unsigned 32-bit modular).
mov r12,r2
sub r10,r2
tst r2,r2
bt ee_boot_ambiguous
mov.l @(ee_half_range_const,pc),r3
cmp/eq r3,r2
bt ee_boot_ambiguous
cmp/pz r2
bt ee_boot_pick_b

ee_boot_pick_a:
mov #0x0,r0
mov.b r0,@(0x1,r8)
mov r9,r0
mov.b r0,@(0x2,r8)
mov.l r10,@(0x4,r8)
bra ee_boot_publish
nop

ee_boot_pick_b:
mov #0x1,r0
mov.b r0,@(0x1,r8)
mov r11,r0
mov.b r0,@(0x2,r8)
mov.l r12,@(0x4,r8)

ee_boot_publish:
mov #0x1,r0
mov.b r0,@(0x3,r8)
mov.b @(0x2,r8),r0
mov r0,r2
mov #0x20,r3
tst 0x80,r0
bt ee_boot_store_telem
mov #0x30,r3
ee_boot_store_telem:
mov.l @(ee_telemetry_status_1,pc),r1
mov.b @r1,r0
or r3,r0
mov.b r0,@r1
mov r2,r0
and 0x0F,r0
add -0x1,r0
mov.l @(ee_selector_state_1,pc),r1
mov.b r0,@r1
bra ee_boot_epilogue
nop

ee_boot_ambiguous:
mov #0x3,r0
mov.b r0,@(0x3,r8)
mov #0x7,r0
mov.b r0,@(0xF,r8)
bra ee_boot_ret_map1
nop

ee_boot_read_fail:
mov.l @(ee_sci2_release_1,pc),r0
jsr @r0
nop
mov #0x8,r0
mov.b r0,@(0xF,r8)

ee_boot_ret_map1:
mov #0x0,r0

ee_boot_epilogue:
lds.l @r15+,pr
mov.l @r15+,r12
mov.l @r15+,r11
mov.l @r15+,r10
mov.l @r15+,r9
mov.l @r15+,r8
rts
nop

// ---------------------------------------------------------------------------
// 1b. eeprom_warm_sync @ 0x000D7330
// Called by startup_wrapper on warm reinit after telemetry_startup_wrapper
// cleared telemetry RAM. Re-mirrors desired autostart (bit 4) and saved (bit 5)
// from preserved persistence RAM into telemetry_status without touching ee_ram
// or SPI, then returns validated active selector slot index (0..4, else 0) in r0.
// ---------------------------------------------------------------------------
.org 0x000D7330
eeprom_warm_sync:
mov.l @(ee_ram_base_1,pc),r1
mov.b @(0x3,r1),r0
cmp/eq 0x1,r0
bf ee_warm_ret_slot
mov.b @(0x2,r1),r0
extu.b r0,r3
mov.b @(0x8,r1),r0
extu.b r0,r2
tst r2,r2
bf ee_warm_chk_saved
tst r3,r3
bt ee_warm_ret_slot
mov r3,r2
ee_warm_chk_saved:
mov #0x0,r4
tst r3,r3
bt ee_warm_chk_en
mov r2,r0
xor r3,r0
tst 0x80,r0
bf ee_warm_chk_en
mov #0x20,r4
ee_warm_chk_en:
mov r2,r0
tst 0x80,r0
bt ee_warm_store
mov #0x10,r0
or r0,r4
ee_warm_store:
mov.l @(ee_telemetry_status_1,pc),r1
mov.b @r1,r0
and 0xCF,r0
or r4,r0
mov.b r0,@r1
ee_warm_ret_slot:
mov.l @(ee_selector_state_1,pc),r1
mov.b @r1,r0
extu.b r0,r0
mov #0x4,r1
cmp/hi r1,r0
bf ee_warm_done
mov #0x0,r0
ee_warm_done:
rts
nop

.align 2
ee_page_a_const:
.word 0x0680
ee_page_b_const:
.word 0x0700

.align 4
ee_cruise_free_init_1:
.long 0x000D6820
ee_ram_base_1:
.long 0xFFFF6020
ee_selector_state_1:
.long 0xFFFF5D00
ee_telemetry_status_1:
.long 0xFFFF5E07
ee_sci2_acquire_1:
.long 0x000670C2
ee_sci2_release_1:
.long 0x0006714C
ee_half_range_const:
.long 0x80000000

// ---------------------------------------------------------------------------
// 2. eeprom_task_wrapper @ 0x000D73A0
// Hooks periodic scheduler slot 0x00021B38 (10.24 ms, SR.I=15) over 0x00068254.
// Arbitrates exclusive EEPROM ownership with the stock queue and advances the
// three-phase ping-pong writer one non-blocking step per tick.
// ---------------------------------------------------------------------------
.org 0x000D73A0
eeprom_task_wrapper:
mov.l r8,@-r15
mov.l r9,@-r15
mov.l r10,@-r15
sts.l pr,@-r15

mov.l @(ee_ram_base_2,pc),r8
mov.b @r8,r0
extu.b r0,r9
tst r9,r9
bt ee_task_idle_phase
bra ee_task_active_phase
nop

ee_task_idle_phase:
// Phase IDLE: run stock EEPROM scheduler entry first, then require stock idle.
mov.l @(ee_stock_sched_2,pc),r0
jsr @r0
nop
mov.l @(ee_stock_busy_2,pc),r1
mov.b @r1,r0
tst r0,r0
bf ee_task_done_jump

// Require valid enabled MSPE config and boot_flags == 1 (boot_ok && !ambiguous).
bsr ee_validate_cfg
nop
tst r0,r0
bt ee_task_done_jump
mov.b @(0x3,r8),r0
cmp/eq 0x1,r0
bf ee_task_done_jump

// Read active selector slot index (0..4) -> desired_slot (1..5), then merge
// desired telemetry autostart bit (0x10 in telemetry_status -> bit 7 in state).
mov.l @(ee_selector_state_2,pc),r1
mov.b @r1,r0
extu.b r0,r4
mov #0x4,r1
cmp/hi r1,r4
bt ee_task_done_jump
add 0x1,r4
mov.l @(ee_telemetry_status_2,pc),r2
mov.b @r2,r0
tst 0x10,r0
bt ee_task_cmp_committed
mov #-0x80,r3
extu.b r3,r3
or r3,r4

ee_task_cmp_committed:
// Skip write if committed_state already equals desired_state; assert autostart_saved (0x20).
mov.b @(0x2,r8),r0
extu.b r0,r1
cmp/eq r4,r1
bf ee_task_need_write
mov.b @r2,r0
or 0x20,r0
mov.b r0,@r2
mov #0x0,r0
mov.b r0,@(0x8,r8)
mov.w r0,@(0xA,r8)
ee_task_done_jump:
bra ee_task_return
nop

ee_task_need_write:
// Reflect autostart_saved (bit 5): set iff a committed record exists and its
// autostart bit (bit 7) already matches desired_state (r4).
tst r1,r1
bt ee_task_clear_saved
mov r4,r0
xor r1,r0
tst 0x80,r0
bf ee_task_clear_saved
mov.b @r2,r0
or 0x20,r0
bra ee_task_store_saved
nop
ee_task_clear_saved:
mov.b @r2,r0
and 0xDF,r0
ee_task_store_saved:
mov.b r0,@r2
// Require all five write-admission safety gates before counting debounce.
bsr ee_write_admitted
nop
tst r0,r0
bf ee_task_admitted_idle
mov #0x0,r0
mov.w r0,@(0xA,r8)
bra ee_task_return
nop

ee_task_admitted_idle:
// Enforce per-slot retry bound.
mov.l @(ee_cfg_base_2,pc),r6
mov.b @(0xD,r8),r0
extu.b r0,r1
cmp/eq r4,r1
bf ee_task_debounce
mov.b @(0xE,r8),r0
extu.b r0,r2
mov.b @(0x9,r6),r0
extu.b r0,r3
cmp/hs r3,r2
bt ee_task_done_jump

ee_task_debounce:
mov.b @(0x8,r8),r0
extu.b r0,r1
cmp/eq r4,r1
bt ee_task_inc_debounce
// New pending slot: reset debounce to 1 and reset retry budget if slot changed.
mov r4,r0
mov.b r0,@(0x8,r8)
mov #0x1,r2
mov.b @(0xD,r8),r0
extu.b r0,r1
cmp/eq r4,r1
bt ee_task_store_debounce
mov r4,r0
mov.b r0,@(0xD,r8)
mov #0x0,r0
mov.b r0,@(0xE,r8)
bra ee_task_store_debounce
nop

ee_task_inc_debounce:
mov.w @(0xA,r8),r0
extu.w r0,r2
add 0x1,r2

ee_task_store_debounce:
mov r2,r0
mov.w r0,@(0xA,r8)
mov.w @(0x6,r6),r0
extu.w r0,r3
cmp/hs r3,r2
bf ee_task_done_jump

// Debounce met: stage destination page, generation, and 16-byte record.
mov.b @(0x1,r8),r0
extu.b r0,r1
tst r1,r1
bf ee_stage_dest_a
mov #0x1,r0
bra ee_stage_dest_store
nop
ee_stage_dest_a:
mov #0x0,r0
ee_stage_dest_store:
mov.b r0,@(0x9,r8)

// next_gen = (active_page == 0xFF) ? 0 : (active_generation + 1).
mov #-0x1,r2
extu.b r2,r2
cmp/eq r2,r1
bt ee_stage_gen_zero
mov.l @(0x4,r8),r2
add 0x1,r2
bra ee_stage_gen_store
nop
ee_stage_gen_zero:
mov #0x0,r2
ee_stage_gen_store:
mov.l r2,@(0x10,r8)

// Build 16-byte staged_record at r8 + 0x18: "MS", 2, state, gen, crc32, VALID.
mov r8,r5
add 0x18,r5
mov #0x4D,r0
mov.b r0,@r5
mov #0x53,r0
mov.b r0,@(0x1,r5)
mov #0x2,r0
mov.b r0,@(0x2,r5)
mov r4,r0
mov.b r0,@(0x3,r5)
mov.l r2,@(0x4,r5)
mov r5,r4
bsr ee_crc32_8
nop
mov r8,r5
add 0x18,r5
mov.l r0,@(0x8,r5)
mov.l @(ee_valid_marker_2,pc),r0
mov.l r0,@(0xC,r5)

mov #0x0,r0
mov.b r0,@(0xC,r8)
mov #0x1,r0
mov.b r0,@r8
bra ee_task_return
nop

// ---------------------------------------------------------------------------
// Active transaction phases (1..5): stock 0x00068254 is deferred until IDLE.
// Phase 5 (QUARANTINE) retains exclusive EEPROM ownership after an abort or
// timeout until a fresh RDSR confirms BOTH WIP==0 and WEL==0.
// ---------------------------------------------------------------------------
ee_task_active_phase:
mov.b @(0x9,r8),r0
tst r0,r0
bf ee_dest_is_b
mov.w @(ee_page_a_2,pc),r10
bra ee_active_acquire
nop
ee_dest_is_b:
mov.w @(ee_page_b_2,pc),r10
bra ee_active_acquire
nop

.align 2
ee_page_a_2:
.word 0x0680
ee_page_b_2:
.word 0x0700

ee_active_acquire:
mov.l @(ee_sci2_acquire_2,pc),r0
jsr @r0
nop

// Poll RDSR: handle SPI timeout or WIP busy.
bsr ee_spi_rdsr
nop
cmp/pz r0
bf ee_active_spi_fail
tst 0x1,r0
bt ee_active_wip_ready

// WIP still busy: release SCI2. In QUARANTINE stay quarantined until WIP clears.
mov.l @(ee_sci2_release_2,pc),r0
jsr @r0
nop
mov r9,r0
cmp/eq 0x5,r0
bt ee_task_wip_ret
mov.b @(0xC,r8),r0
extu.b r0,r1
add 0x1,r1
mov r1,r0
mov.b r0,@(0xC,r8)
mov.l @(ee_cfg_base_2,pc),r6
mov.b @(0x8,r6),r0
extu.b r0,r2
cmp/hs r2,r1
bf ee_task_wip_ret
mov #0x2,r4
bsr ee_abort_tx
nop
ee_task_wip_ret:
bra ee_task_return
nop

ee_active_spi_fail:
mov.l @(ee_sci2_release_2,pc),r0
jsr @r0
nop
mov r9,r0
cmp/eq 0x5,r0
bt ee_task_wip_ret
mov #0x1,r4
bsr ee_abort_tx
nop
bra ee_task_return
nop

ee_active_wip_ready:
mov r9,r0
cmp/eq 0x5,r0
bf ee_active_not_quarantine
// Quarantine recovery: exit ONLY when a fresh RDSR itself proves WIP==0 and
// WEL==0. If WEL==1, issue WRDI and stay in PHASE_QUARANTINE for re-check.
mov r3,r0
tst 0x2,r0
bt ee_quarantine_clear
bsr ee_spi_wrdi
nop
mov.l @(ee_sci2_release_2,pc),r0
jsr @r0
nop
bra ee_task_return
nop
ee_quarantine_clear:
mov.l @(ee_sci2_release_2,pc),r0
jsr @r0
nop
mov #0x0,r0
mov.b r0,@r8
bra ee_task_return
nop

ee_active_not_quarantine:
mov r9,r0
cmp/eq 0x1,r0
bt ee_phase_pre_wip
cmp/eq 0x2,r0
bt ee_phase_wait_inval
cmp/eq 0x3,r0
bt ee_phase_wait_body
bra ee_phase_wait_commit
nop

// Phase 1: check admission, write INVALID_MARKER (4 zeros from r8+0x38) to dest+12.
ee_phase_pre_wip:
bsr ee_write_admitted
nop
tst r0,r0
bt ee_active_inhibit_fail
mov r10,r4
add 0xC,r4
mov r8,r5
add 0x38,r5
mov #0x4,r6
bsr ee_spi_write_slice
nop
mov r0,r9
mov.l @(ee_sci2_release_2,pc),r0
jsr @r0
nop
tst r9,r9
bf ee_active_spi_post_rel
mov #0x0,r0
mov.b r0,@(0xC,r8)
mov #0x2,r0
mov.b r0,@r8
bra ee_task_return
nop

// Phase 2: read back dest+12 == 0, check admission, write 12-byte body to dest+0.
ee_phase_wait_inval:
mov r10,r4
add 0xC,r4
mov r8,r5
add 0x28,r5
mov #0x4,r6
bsr ee_spi_read_n
nop
tst r0,r0
bf ee_active_spi_fail
mov r8,r5
add 0x28,r5
mov.l @r5,r0
tst r0,r0
bf ee_active_inval_fail
bsr ee_write_admitted
nop
tst r0,r0
bt ee_active_inhibit_fail
mov r10,r4
mov r8,r5
add 0x18,r5
mov #0xC,r6
bsr ee_spi_write_slice
nop
mov r0,r9
mov.l @(ee_sci2_release_2,pc),r0
jsr @r0
nop
tst r9,r9
bf ee_active_spi_post_rel
mov #0x0,r0
mov.b r0,@(0xC,r8)
mov #0x3,r0
mov.b r0,@r8
bra ee_task_return
nop

ee_active_inhibit_fail:
mov.l @(ee_sci2_release_2,pc),r0
jsr @r0
nop
mov #0x6,r4
bsr ee_abort_tx
nop
bra ee_task_return
nop

ee_active_inval_fail:
mov.l @(ee_sci2_release_2,pc),r0
jsr @r0
nop
mov #0x3,r4
bsr ee_abort_tx
nop
bra ee_task_return
nop

ee_active_spi_post_rel:
mov #0x1,r4
bsr ee_abort_tx
nop
bra ee_task_return
nop

// Phase 3: read back 16 bytes (0..11 == staged_body && 12..15 == 0), check
// admission, then write VALID_MARKER (r8+0x24) to dest+12.
ee_phase_wait_body:
mov r10,r4
mov r8,r5
add 0x28,r5
mov #0x10,r6
bsr ee_spi_read_n
nop
tst r0,r0
bt ee_body_read_ok
bra ee_active_spi_fail
nop
ee_body_read_ok:
mov r8,r4
add 0x18,r4
mov r8,r5
add 0x28,r5
mov #0x3,r6
bsr ee_cmp_words
nop
tst r0,r0
bt ee_active_body_fail
mov r8,r5
add 0x34,r5
mov.l @r5,r0
tst r0,r0
bf ee_active_body_fail
bsr ee_write_admitted
nop
tst r0,r0
bt ee_active_inhibit_fail
mov r10,r4
add 0xC,r4
mov r8,r5
add 0x24,r5
mov #0x4,r6
bsr ee_spi_write_slice
nop
mov r0,r9
mov.l @(ee_sci2_release_2,pc),r0
jsr @r0
nop
tst r9,r9
bf ee_active_spi_post_rel
mov #0x0,r0
mov.b r0,@(0xC,r8)
mov #0x4,r0
mov.b r0,@r8
bra ee_task_return
nop

ee_active_body_fail:
mov.l @(ee_sci2_release_2,pc),r0
jsr @r0
nop
mov #0x4,r4
bsr ee_abort_tx
nop
bra ee_task_return
nop

// Phase 4: read back all 16 bytes and verify exact match with staged_record.
ee_phase_wait_commit:
mov r10,r4
mov r8,r5
add 0x28,r5
mov #0x10,r6
bsr ee_spi_read_n
nop
mov r0,r9
mov.l @(ee_sci2_release_2,pc),r0
jsr @r0
nop
tst r9,r9
bf ee_active_spi_post_rel
mov r8,r4
add 0x18,r4
mov r8,r5
add 0x28,r5
mov #0x4,r6
bsr ee_cmp_words
nop
tst r0,r0
bt ee_active_commit_fail

// Commit succeeded: update active page, committed state, generation, and write_count.
mov.b @(0x9,r8),r0
mov.b r0,@(0x1,r8)
mov.b @(0x8,r8),r0
extu.b r0,r1
mov.b r0,@(0x2,r8)
mov.l @(0x10,r8),r0
mov.l r0,@(0x4,r8)
mov #0x0,r0
mov.b r0,@r8
mov.b r0,@(0x8,r8)
mov.w r0,@(0xA,r8)
mov.b r0,@(0xC,r8)
mov.b r0,@(0xE,r8)
mov.b r0,@(0xF,r8)
mov.l @(0x14,r8),r0
add 0x1,r0
mov.l r0,@(0x14,r8)
// Assert autostart_saved (bit 5) if live autostart_enabled (bit 4) still matches committed bit 7.
mov.l @(ee_telemetry_status_2,pc),r2
mov.b @r2,r0
mov r0,r3
and 0x10,r0
shll2 r0
shll r0
xor r1,r0
tst 0x80,r0
bf ee_commit_done
mov r3,r0
or 0x20,r0
mov.b r0,@r2
ee_commit_done:
bra ee_task_return
nop

ee_active_commit_fail:
mov #0x5,r4
bsr ee_abort_tx
nop

ee_task_return:
lds.l @r15+,pr
mov.l @r15+,r10
mov.l @r15+,r9
mov.l @r15+,r8
rts
nop

.align 4
ee_ram_base_2:
.long 0xFFFF6020
ee_cfg_base_2:
.long 0x000D7200
ee_selector_state_2:
.long 0xFFFF5D00
ee_telemetry_status_2:
.long 0xFFFF5E07
ee_stock_sched_2:
.long 0x00068254
ee_stock_busy_2:
.long 0xFFFF2CD4
ee_sci2_acquire_2:
.long 0x000670C2
ee_sci2_release_2:
.long 0x0006714C
ee_valid_marker_2:
.long 0xA65DC39E

// ---------------------------------------------------------------------------
// 3. Internal helpers (config, admission, abort, CRC32, decode, SPI framing)
// ---------------------------------------------------------------------------

// Compare r6 longwords at r4 and r5; returns r0=1 equal, 0 mismatch.
ee_cmp_words:
mov.l @r4+,r1
mov.l @r5+,r2
cmp/eq r2,r1
bf ee_cmp_fail
dt r6
bf ee_cmp_words
mov #0x1,r0
rts
nop
ee_cmp_fail:
mov #0x0,r0
rts
nop

// Abort current write transaction with error code in r4.
// Enters PHASE_QUARANTINE (5) so stock EEPROM access stays deferred until a
// fresh RDSR confirms BOTH WIP==0 and WEL==0.
ee_abort_tx:
mov #0x5,r0
mov.b r0,@r8
mov #0x0,r0
mov.w r0,@(0xA,r8)
mov.b r0,@(0xC,r8)
mov r4,r0
mov.b r0,@(0xF,r8)
mov.b @(0xE,r8),r0
extu.b r0,r1
add 0x1,r1
mov r1,r0
mov.b r0,@(0xE,r8)
rts
nop

// Validate MSPE v1 config at 0x000D7200 and check enabled bit 0.
// Returns r0=1 valid and enabled, 0 otherwise.
ee_validate_cfg:
mov.l @(ee_cfg_addr_3,pc),r6
mov.l @r6,r1
mov.l @(ee_cfg_magic_3,pc),r2
cmp/eq r2,r1
bf ee_cfg_invalid
mov.b @(0x4,r6),r0
cmp/eq 0x1,r0
bf ee_cfg_invalid
mov.b @(0x5,r6),r0
cmp/eq 0x1,r0
bf ee_cfg_invalid
mov.w @(0x6,r6),r0
extu.w r0,r0
tst r0,r0
bt ee_cfg_invalid
mov.b @(0x8,r6),r0
extu.b r0,r0
tst r0,r0
bt ee_cfg_invalid
mov.b @(0x9,r6),r0
extu.b r0,r0
tst r0,r0
bt ee_cfg_invalid
mov.w @(0xA,r6),r0
extu.w r0,r0
tst r0,r0
bf ee_cfg_invalid
mov.l @(0xC,r6),r1
mov.l @(ee_cfg_sentinel_3,pc),r2
cmp/eq r2,r1
bf ee_cfg_invalid
mov #0x1,r0
rts
nop
ee_cfg_invalid:
mov #0x0,r0
rts
nop

// Check all JK08A write-admission safety gates (ignition, shutdown, cranking, Vbat).
// Returns r0=1 admitted, 0 inhibited.
ee_write_admitted:
// 1. Live PLDR.4 (0xFFFFF75E bit 4 == 1).
mov.l @(ee_pldr_addr,pc),r1
mov.w @r1,r0
tst 0x10,r0
bt ee_admit_no
// 2. Debounced IG ON (FFFF4185.7 == 1) and NOT cranking (FFFF4185.6 == 0).
mov.l @(ee_port_state_addr,pc),r1
mov.b @r1,r0
tst 0x80,r0
bt ee_admit_no
tst 0x40,r0
bf ee_admit_no
// 3. Not shutting down or reinitializing: FFFF4213.7==0, FFFF39DC==0, FFFF84A8==0.
mov.l @(ee_shutdown_req_addr,pc),r1
mov.b @r1,r0
tst 0x80,r0
bf ee_admit_no
mov.l @(ee_shutdown_state_addr,pc),r1
mov.l @r1,r0
tst r0,r0
bf ee_admit_no
mov.l @(ee_reinit_mode_addr,pc),r1
mov.l @r1,r0
tst r0,r0
bf ee_admit_no
// 4. Battery voltage >= 0x8A (138 counts = 11.04 V at FFFF1188).
mov.l @(ee_vbat_addr,pc),r1
mov.b @r1,r0
extu.b r0,r2
mov #-0x76,r3
extu.b r3,r3
cmp/hs r3,r2
bf ee_admit_no
mov #0x1,r0
rts
nop
ee_admit_no:
mov #0x0,r0
rts
nop

// Standard IEEE 802.3 CRC-32 over 8 bytes at r4; returns r0 = crc32.
// Clobbers r0..r6.
ee_crc32_8:
mov #-0x1,r0
mov #0x8,r5
mov.l @(ee_crc_poly,pc),r3
ee_crc_byte_loop:
mov.b @r4+,r1
extu.b r1,r1
xor r1,r0
mov #0x8,r6
ee_crc_bit_loop:
shlr r0
bf ee_crc_no_xor
xor r3,r0
ee_crc_no_xor:
dt r6
bf ee_crc_bit_loop
dt r5
bf ee_crc_byte_loop
not r0,r0
rts
nop

// Decode and validate 16-byte record at r4.
// Accepts v1 (byte3 in 1..5) and v2 (byte3 low nibble in 1..5, bits 6..4 == 0,
// bit 7 = telemetry_autostart). Returns r0 = packed state if valid else 0,
// r1 = generation.
ee_decode_record:
sts.l pr,@-r15
mov r4,r7
// Check commit marker (bytes 12..15 == 0xA65DC39E).
mov.l @(0xC,r7),r1
mov.l @(ee_valid_marker_3,pc),r2
cmp/eq r2,r1
bf ee_dec_bad
// Check "MS", version 1 or 2, and valid packed state in byte 3.
mov.b @r7,r0
cmp/eq 0x4D,r0
bf ee_dec_bad
mov.b @(0x1,r7),r0
cmp/eq 0x53,r0
bf ee_dec_bad
mov.b @(0x2,r7),r0
cmp/eq 0x1,r0
bt ee_dec_v1
cmp/eq 0x2,r0
bf ee_dec_bad
mov.b @(0x3,r7),r0
tst 0x70,r0
bf ee_dec_bad
and 0x0F,r0
mov r0,r2
bra ee_dec_slot_check
nop
ee_dec_v1:
mov.b @(0x3,r7),r0
extu.b r0,r2
ee_dec_slot_check:
tst r2,r2
bt ee_dec_bad
mov #0x5,r1
cmp/hi r1,r2
bt ee_dec_bad
// Verify IEEE CRC-32 over bytes 0..7 against stored CRC at bytes 8..11.
mov r7,r4
bsr ee_crc32_8
nop
mov.l @(0x8,r7),r1
cmp/eq r1,r0
bf ee_dec_bad
mov.b @(0x3,r7),r0
extu.b r0,r0
mov.l @(0x4,r7),r1
lds.l @r15+,pr
rts
nop
ee_dec_bad:
mov #0x0,r0
mov #0x0,r1
lds.l @r15+,pr
rts
nop

.align 4
ee_cfg_addr_3:
.long 0x000D7200
ee_cfg_magic_3:
.long 0x4D535045
ee_cfg_sentinel_3:
.long 0x5AA5A55A
ee_pldr_addr:
.long 0xFFFFF75E
ee_port_state_addr:
.long 0xFFFF4185
ee_shutdown_req_addr:
.long 0xFFFF4213
ee_shutdown_state_addr:
.long 0xFFFF39DC
ee_reinit_mode_addr:
.long 0xFFFF84A8
ee_vbat_addr:
.long 0xFFFF1188
ee_crc_poly:
.long 0xEDB88320
ee_valid_marker_3:
.long 0xA65DC39E

// ---------------------------------------------------------------------------
// 4. Low-level bounded SCI2 SPI framing (SCI2=0xFFFFF010, PCDR.4=0xFFFFF73E)
// Uses r7 as sticky frame error accumulator (0 on ok, -1 on timeout/ORER).
// ---------------------------------------------------------------------------

// Drain any stale RDRF/ORER on SCI2 (read-before-clear) and assert CS low.
// Clobbers r0, r1, r2.
ee_cs_low:
mov.l @(ee_sci2_base,pc),r1
mov.b @(0x4,r1),r0
tst 0x60,r0
bt ee_cs_low_assert
mov.b @(0x5,r1),r0
mov.b @(0x4,r1),r0
and 0x9F,r0
mov.b r0,@(0x4,r1)
ee_cs_low_assert:
mov.l @(ee_pcdr_addr,pc),r1
mov.w @r1,r0
mov.w @(ee_cs_clear_mask,pc),r2
and r2,r0
mov.w r0,@r1
rts
nop

// Wait bounded TEND (SSR2.2) so the 8th clock edge finishes before CS rises,
// then deassert CS high (PCDR |= 0x0010) with stock 6-iteration settle loop.
// Marks sticky r7 = -1 if TEND times out. Clobbers r0, r1, r2.
ee_cs_high:
cmp/pz r7
bf ee_cs_high_raise
mov.l @(ee_sci2_base,pc),r1
mov #0x40,r2
ee_wait_tend:
mov.b @(0x4,r1),r0
tst 0x4,r0
bf ee_cs_high_raise
dt r2
bf ee_wait_tend
mov #-0x1,r7
ee_cs_high_raise:
mov.l @(ee_pcdr_addr,pc),r1
mov.w @r1,r0
or 0x10,r0
mov.w r0,@r1
mov #0x6,r2
ee_cs_settle:
dt r2
bf ee_cs_settle
rts
nop

// Transfer 1 byte in r4 over SCI2. If sticky error r7 < 0, returns -1 immediately.
// Checks TDRE before transmit, detects ORER as hard error, waits bounded RDRF,
// and clears only RDRF (0xBF) via Renesas read-before-clear.
// Clobbers r0, r1, r2. Preserves r3, r4, r5, r6, r8..r14.
ee_spi_xfer_byte:
cmp/pz r7
bf ee_xfer_aborted
mov.l @(ee_sci2_base,pc),r1
mov #0x40,r2
ee_wait_tdre:
mov.b @(0x4,r1),r0
tst 0x80,r0
bf ee_tdre_ready
dt r2
bf ee_wait_tdre
bra ee_xfer_timeout
nop
ee_tdre_ready:
mov r4,r0
mov.b r0,@(0x3,r1)
mov.b @(0x4,r1),r0
and 0x7F,r0
mov.b r0,@(0x4,r1)
mov #0x40,r2
ee_wait_rdrf:
mov.b @(0x4,r1),r0
tst 0x20,r0
bf ee_xfer_timeout
tst 0x40,r0
bf ee_rdrf_ready
dt r2
bf ee_wait_rdrf
ee_xfer_timeout:
mov #-0x1,r7
ee_xfer_aborted:
mov #-0x1,r0
rts
nop
ee_rdrf_ready:
mov.b @(0x5,r1),r0
extu.b r0,r2
mov.b @(0x4,r1),r0
and 0xBF,r0
mov.b r0,@(0x4,r1)
mov r2,r0
rts
nop

// Read M95320 status register (RDSR 0x05). Returns r0 = r3 = status byte or -1.
ee_spi_rdsr:
sts.l pr,@-r15
mov #0x0,r7
bsr ee_cs_low
nop
mov #0x5,r4
bsr ee_spi_xfer_byte
nop
mov #-0x1,r4
bsr ee_spi_xfer_byte
nop
mov r0,r3
bsr ee_cs_high
nop
cmp/pz r7
bt ee_rdsr_ok
mov #-0x1,r3
ee_rdsr_ok:
mov r3,r0
lds.l @r15+,pr
rts
nop

// Issue standalone WRDI (0x04) frame with fresh sticky error accumulator.
// Returns r0 = 0 on success, -1 on SPI timeout.
ee_spi_wrdi:
sts.l pr,@-r15
mov #0x0,r7
bsr ee_cs_low
nop
mov #0x4,r4
bsr ee_spi_xfer_byte
nop
bsr ee_cs_high
nop
mov r7,r0
lds.l @r15+,pr
rts
nop

// Read r6 bytes from EEPROM address r4 into buffer r5 (READ 0x03).
// Returns r0 = 0 on success, -1 on SPI timeout.
ee_spi_read_n:
sts.l pr,@-r15
mov #0x0,r7
mov r4,r3
bsr ee_cs_low
nop
mov #0x3,r4
bsr ee_spi_xfer_byte
nop
mov r3,r4
shlr8 r4
bsr ee_spi_xfer_byte
nop
mov r3,r4
bsr ee_spi_xfer_byte
nop
ee_read_loop:
mov #-0x1,r4
bsr ee_spi_xfer_byte
nop
mov.b r0,@r5
add 0x1,r5
dt r6
bf ee_read_loop
bsr ee_cs_high
nop
mov r7,r0
lds.l @r15+,pr
rts
nop

// Execute WREN (0x06) -> WRITE (0x02, addr=r4, data=r5, len=r6) -> WRDI (0x04).
// Returns r0 = 0 on success, -1 on SPI timeout.
ee_spi_write_slice:
sts.l pr,@-r15
mov #0x0,r7
mov r4,r3
// Frame 1: WREN 0x06
bsr ee_cs_low
nop
mov #0x6,r4
bsr ee_spi_xfer_byte
nop
bsr ee_cs_high
nop
// Frame 2: WRITE 0x02 + addr_hi + addr_lo + data[0..r6-1]
bsr ee_cs_low
nop
mov #0x2,r4
bsr ee_spi_xfer_byte
nop
mov r3,r4
shlr8 r4
bsr ee_spi_xfer_byte
nop
mov r3,r4
bsr ee_spi_xfer_byte
nop
ee_write_loop:
mov.b @r5+,r4
bsr ee_spi_xfer_byte
nop
dt r6
bf ee_write_loop
bsr ee_cs_high
nop
// Frame 3: WRDI 0x04
bsr ee_cs_low
nop
mov #0x4,r4
bsr ee_spi_xfer_byte
nop
bsr ee_cs_high
nop
mov r7,r0
lds.l @r15+,pr
rts
nop

.align 2
ee_cs_clear_mask:
.word 0xFFEF

.align 4
ee_pcdr_addr:
.long 0xFFFFF73E
ee_sci2_base:
.long 0xFFFFF010
