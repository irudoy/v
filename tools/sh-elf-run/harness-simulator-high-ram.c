/* Data-memory alias and dual-bank/MMIO probes for GNU SH-2E simulator. */
#include <stdint.h>
#include <stdio.h>

#ifndef PROBE_CASE
#define PROBE_CASE 0
#endif

#define BYTE(address) (*(volatile uint8_t *)(uintptr_t)(address))
#define WORD(address) (*(volatile uint16_t *)(uintptr_t)(address))
#define LONG(address) (*(volatile uint32_t *)(uintptr_t)(address))
#define REQUIRE(condition) do { if (!(condition)) return __LINE__; } while (0)

int main(void)
{
#if PROBE_CASE == 0
    LONG(0x01010000u) = 0x98765432u;
    LONG(0xFFFF0000u) = 0xA1B2C3D4u;
    REQUIRE(LONG(0x01000000u) == 0xA1B2C3D4u);
    LONG(0xFFFF84E8u) = 0x11223344u;
    REQUIRE(LONG(0x010084E8u) == 0x11223344u);
    REQUIRE(BYTE(0xFFFF84E8u) == 0x11u);
    REQUIRE(BYTE(0xFFFF84EBu) == 0x44u);
    REQUIRE(WORD(0xFFFF84EAu) == 0x3344u);
    WORD(0xFFFF84EAu) = 0x89ABu;
    REQUIRE(WORD(0x010084EAu) == 0x89ABu);
    REQUIRE(*(volatile int16_t *)(uintptr_t)0xFFFF84EAu == -30293);
    BYTE(0xFFFF8511u) = 0x80u;
    REQUIRE(BYTE(0x01008511u) == 0x80u);
    REQUIRE(*(volatile int8_t *)(uintptr_t)0xFFFF8511u == -128);
    LONG(0x010084E8u) = 0xFEDCBA98u;
    REQUIRE(LONG(0xFFFF84E8u) == 0xFEDCBA98u);
    REQUIRE(WORD(0xFFFF84EAu) == 0xBA98u);
    REQUIRE(BYTE(0xFFFF84E8u) == 0xFEu);
    BYTE(0x01008511u) = 0x35u;
    REQUIRE(BYTE(0xFFFF8511u) == 0x35u);
    WORD(0x010084EAu) = 0x2468u;
    REQUIRE(WORD(0xFFFF84EAu) == 0x2468u);
    LONG(0xFFFFF5C0u) = 0x10203040u;
    REQUIRE(LONG(0x0100F5C0u) == 0x10203040u);
    LONG(0xFFFFFFFCu) = 0xABCDEF98u;
    REQUIRE(LONG(0x0100FFFCu) == 0xABCDEF98u);
    REQUIRE(WORD(0xFFFFFFFEu) == 0xEF98u);
    REQUIRE(BYTE(0xFFFFFFFFu) == 0x98u);
    REQUIRE(LONG(0x01010000u) == 0x98765432u);
#elif PROBE_CASE == 1
    uint32_t value;
    __asm__ volatile ("mov.w @%1,%0" : "=r" (value) : "r" (0xFFFF84EBu) : "memory");
    return value;
#elif PROBE_CASE == 2
    uint32_t value;
    __asm__ volatile ("mov.l @%1,%0" : "=r" (value) : "r" (0xFFFF84EAu) : "memory");
    return value;
#elif PROBE_CASE == 3
    __asm__ volatile ("mov.w %0,@%1" : : "r" (0x1357u), "r" (0xFFFF84EBu) : "memory");
#elif PROBE_CASE == 4
    __asm__ volatile ("mov.l %0,@%1" : : "r" (0x13572468u), "r" (0xFFFF84EAu) : "memory");
#elif PROBE_CASE == 5
    return BYTE(0xFFFE8511u);
#elif PROBE_CASE == 6
    return BYTE(0xFFFF8511u);
#elif PROBE_CASE == 7
    return WORD(0xFFFF84EAu);
#elif PROBE_CASE == 8
    return LONG(0xFFFF84E8u);
#elif PROBE_CASE == 9
    BYTE(0xFFFF8511u) = 0x80u;
#elif PROBE_CASE == 10
    WORD(0xFFFF84EAu) = 0x89ABu;
#elif PROBE_CASE == 11
    LONG(0x010084E8u) = 0x11223344u;
    REQUIRE(BYTE(0x010084E8u) == 0x11u);
    REQUIRE(WORD(0x010084EAu) == 0x3344u);
#elif PROBE_CASE == 12
    /* sh7059-mmio dual-bank separation + MMIO shadow + legacy canary. */
    LONG(0x0100F73Cu) = 0xCAFEBABEu;
    LONG(0x0100F010u) = 0xDEADBEEFu;
    BYTE(0xFFFE8511u) = 0xA5u;
    BYTE(0xFFFF8511u) = 0x5Au;
    REQUIRE(BYTE(0x01020511u) == 0xA5u);
    REQUIRE(BYTE(0x01008511u) == 0x5Au);
    REQUIRE(BYTE(0xFFFE8511u) == 0xA5u);
    REQUIRE(BYTE(0xFFFF8511u) == 0x5Au);
    /* Lower-bank and upper-bank exact endpoints. */
    LONG(0xFFFE8000u) = 0x11223344u;
    LONG(0xFFFEFFFCu) = 0x55667788u;
    LONG(0xFFFF0000u) = 0x99AABBCCu;
    LONG(0xFFFFEFFCu) = 0xDDEEFF00u;
    REQUIRE(LONG(0x01020000u) == 0x11223344u);
    REQUIRE(LONG(0x01027FFCu) == 0x55667788u);
    REQUIRE(LONG(0x01000000u) == 0x99AABBCCu);
    REQUIRE(LONG(0x0100EFFCu) == 0xDDEEFF00u);
    /* Signed narrow reads across lower bank. */
    WORD(0xFFFE81B6u) = 0x8001u;
    REQUIRE(*(volatile int16_t *)(uintptr_t)0xFFFE81B6u == -32767);
    BYTE(0xFFFE9473u) = 0x80u;
    REQUIRE(*(volatile int8_t *)(uintptr_t)0xFFFE9473u == -128);
    /* Allowed MMIO shadow registers land in [0x01028000, 0x01029000). */
    BYTE(0xFFFFF010u) = 0x80u;
    BYTE(0xFFFFF011u) = 0x01u;
    BYTE(0xFFFFF016u) = 0xFAu;
    WORD(0xFFFFF75Cu) = 0x1234u;
    WORD(0xFFFFF75Eu) = 0x0010u;
    REQUIRE(BYTE(0x01028010u) == 0x80u);
    REQUIRE(BYTE(0x01028011u) == 0x01u);
    REQUIRE(BYTE(0x01028016u) == 0xFAu);
    REQUIRE(WORD(0x0102875Cu) == 0x1234u);
    REQUIRE(WORD(0x0102875Eu) == 0x0010u);
    /* Legacy tail [0x0100F000, 0x01010000) must remain untouched. */
    REQUIRE(LONG(0x0100F73Cu) == 0xCAFEBABEu);
    REQUIRE(LONG(0x0100F010u) == 0xDEADBEEFu);
#elif PROBE_CASE == 13
    /* sh7058-mmio upper bank + allowed MMIO shadow. */
    LONG(0x0100F73Cu) = 0x13572468u;
    LONG(0xFFFF0000u) = 0x10203040u;
    LONG(0xFFFFEFFCu) = 0x50607080u;
    REQUIRE(LONG(0x01000000u) == 0x10203040u);
    REQUIRE(LONG(0x0100EFFCu) == 0x50607080u);
    WORD(0xFFFFF75Eu) = 0x0010u;
    REQUIRE(WORD(0x0102875Eu) == 0x0010u);
    REQUIRE(LONG(0x0100F73Cu) == 0x13572468u);
#elif PROBE_CASE == 14
    /* Unmapped MMIO address must bus-error in mmio layouts. */
    return BYTE(0xFFFFF800u);
#elif PROBE_CASE == 15
    /* Wrong width on PCDR (byte instead of halfword) must bus-error. */
    return BYTE(0xFFFFF73Eu);
#elif PROBE_CASE == 16
    /* Wrong width on SCI2 SMR2 (halfword instead of byte) must bus-error. */
    return WORD(0xFFFFF010u);
#elif PROBE_CASE == 17
    /* Below SH7059 lower RAM base (0xFFFE7FFF) must bus-error. */
    return BYTE(0xFFFE7FFFu);
#elif PROBE_CASE == 18
    /* SCI2 + PCDR peripheral probe under sh7059-mmio with M95320 enabled. */
    BYTE(0x0101101Cu) = 3u;
    /* Ordinary RAM / legacy tail writes must not trigger SPI counters. */
    WORD(0x0100F73Eu) = 0x0000u;
    WORD(0x0100F73Eu) = 0x0010u;
    REQUIRE(LONG(0x01011014u) == 0u);
    REQUIRE(LONG(0x01011010u) == 0u);
    /* Drive WREN (0x06) through real PCDR/SCI2 MMIO addresses. */
    WORD(0xFFFFF73Eu) = 0x0010u;
    WORD(0xFFFFF73Eu) = 0x0000u;
    REQUIRE(WORD(0x0102873Eu) == 0x0000u);
    (void)BYTE(0xFFFFF014u);
    BYTE(0xFFFFF013u) = 0x06u;
    BYTE(0xFFFFF014u) = 0x7Fu;
    (void)BYTE(0xFFFFF014u);
    BYTE(0xFFFFF014u) = 0xBFu;
    WORD(0xFFFFF73Eu) = 0x0010u;
    REQUIRE(WORD(0x0102873Eu) == 0x0010u);
    REQUIRE(LONG(0x01011014u) == 1u);
    /* Drive RDSR (0x05) and verify WEL bit (0x02) returned via RDR2. */
    WORD(0xFFFFF73Eu) = 0x0000u;
    (void)BYTE(0xFFFFF014u);
    BYTE(0xFFFFF013u) = 0x05u;
    BYTE(0xFFFFF014u) = 0x7Fu;
    (void)BYTE(0xFFFFF014u);
    BYTE(0xFFFFF014u) = 0xBFu;
    (void)BYTE(0xFFFFF014u);
    BYTE(0xFFFFF013u) = 0xFFu;
    BYTE(0xFFFFF014u) = 0x7Fu;
    REQUIRE((BYTE(0xFFFFF015u) & 0x03u) == 0x02u);
    (void)BYTE(0xFFFFF014u);
    BYTE(0xFFFFF014u) = 0xBFu;
    WORD(0xFFFFF73Eu) = 0x0010u;
    REQUIRE(LONG(0x01011010u) == 1u);
#else
#error Unsupported probe
#endif
    puts("VQ_SH_HIGH_RAM_PROBE status=PASS");
    return 0;
}
