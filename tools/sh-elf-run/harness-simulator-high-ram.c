/* Data-memory alias probes; no ECU instruction or peripheral is modeled. */
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
#else
#error Unsupported probe
#endif
    puts("VQ_SH_HIGH_RAM_PROBE status=PASS");
    return 0;
}
