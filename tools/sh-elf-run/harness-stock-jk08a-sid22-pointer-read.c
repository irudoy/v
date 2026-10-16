#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "sid22-pointer-read-cases.h"

#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif

extern void sid22_invoke(uint32_t *);
static uint32_t state[80];
static uint8_t expected[65536];
static uint8_t ring_before[256], ring_after[256];
static uint8_t source_before[4], source_after[4];

static volatile uint8_t *ram(uint32_t address)
{
    if (address >= 0xffff8000U && address < 0xffff8500U)
        return (volatile uint8_t *)(uintptr_t)(address - 0xffff8000U + 0x2000U);
    return (volatile uint8_t *)(uintptr_t)(0x01000000U + (address & 65535U));
}

static uint8_t source(uint32_t address)
{
    return address >= 0xffff0000U ? *ram(address) : *(volatile uint8_t *)(uintptr_t)address;
}

static void word_expected(unsigned offset, uint32_t value)
{
    unsigned i;
    for (i = 0; i < 4; ++i) expected[offset + i] = (uint8_t)(value >> (24U - 8U * i));
}

static uint32_t read_word(unsigned offset)
{
    uint32_t value = 0;
    unsigned i;
    for (i = 0; i < 4; ++i) value = (value << 8) | *ram(0xffff0000U + offset + i);
    return value;
}

static int fail(const struct sid22_case *test, const char *field, uint32_t actual, uint32_t wanted)
{
    printf("SID22_FAIL id=%s field=%s actual=%08lx expected=%08lx\n",
           test->id, field, (unsigned long)actual, (unsigned long)wanted);
    return 0;
}

static void hex(const uint8_t *bytes, unsigned count, char *out)
{
    static const char digits[] = "0123456789abcdef";
    unsigned i;
    for (i = 0; i < count; ++i) {
        out[2U * i] = digits[bytes[i] >> 4];
        out[2U * i + 1U] = digits[bytes[i] & 15U];
    }
    out[2U * count] = 0;
}

static void array(const uint32_t *values, unsigned count)
{
    unsigned i;
    putchar('[');
    for (i = 0; i < count; ++i) printf("%s%lu", i ? "," : "", (unsigned long)values[i]);
    putchar(']');
}

static void byte_array(const uint8_t *values, unsigned count)
{
    unsigned i;
    putchar('[');
    for (i = 0; i < count; ++i) printf("%s%u", i ? "," : "", (unsigned)values[i]);
    putchar(']');
}

static int run_case(const struct sid22_case *test)
{
    unsigned i, offset, end = 0;
    uint32_t args[2], result;
    char first[513], last[513];
    for (i = 0; i < 65536; ++i)
        *ram(0xffff0000U + i) = (uint8_t)(i * 29U + (i >> 8) + test->value);
    for (i = 0; i < test->width; ++i)
        if (test->sources[i] >= 0xffff0000U) *ram(test->sources[i]) = test->values[i];
    *ram(0xffff8005U) = (uint8_t)(test->did >> 8);
    *ram(0xffff8006U) = (uint8_t)test->did;
    *ram(0xffff8007U) = (uint8_t)test->length;
    *ram(0xffff8008U) = (uint8_t)(test->value ^ 0x96U);
    *ram(0xffff8105U) = (uint8_t)test->start;
    *ram(0xffff8488U) = (uint8_t)test->flag;
    for (i = 0; i < 16; ++i) *ram(0xfffff000U + i) = 0;
    for (i = 0; i < 65536; ++i) expected[i] = *ram(0xffff0000U + i);
    for (i = 0; i < 256; ++i) ring_before[i] = *ram(0xffff810aU + i);
    for (i = 0; i < test->width; ++i) source_before[i] = source(test->sources[i]);
    expected[0x3236] = (uint8_t)(test->did >> 8);
    expected[0x3237] = (uint8_t)test->did;
    expected[0x8212] = (uint8_t)test->length;
    expected[0x8214] = (uint8_t)(test->value ^ 0x96U);
    if (test->transport) {
        uint8_t payload[7];
        payload[0] = 0x62; payload[1] = (uint8_t)(test->did >> 8); payload[2] = (uint8_t)test->did;
        for (i = 0; i < test->width; ++i) payload[3U + i] = test->values[i];
        for (i = 0; i < 3U + test->width; ++i) {
            offset = (test->start + i) & 255U;
            expected[0x810aU + offset] = payload[i];
        }
        end = ((test->start + 2U + test->width) & 255U) + 1U;
        if ((test->did >> 8) == 0x11U && test->width == 1U) end &= 255U;
        args[0] = (uint32_t)(int32_t)(int8_t)test->start;
        args[1] = end;
        if (test->did == 0x1146U && test->flag) expected[0x2f71] = 0;
    } else { args[0] = 0x22U; args[1] = test->error; }
    word_expected(0xf000, args[0]); word_expected(0xf004, args[1]);
    word_expected(0xf008, 1); word_expected(0xf00c, test->transport ? 1U : 2U);
    memset(state, 0, sizeof(state));
    sid22_invoke(state);
    for (i = 0; i < 65536; ++i)
        if (*ram(0xffff0000U + i) != expected[i]) {
            printf("SID22_RAM_OFFSET id=%s offset=%04x\n", test->id, i);
            return fail(test, "complete RAM footprint", *ram(0xffff0000U + i), expected[i]);
        }
    for (i = 0; i < test->width; ++i) {
        source_after[i] = source(test->sources[i]);
        if (source_before[i] != test->values[i] || source_after[i] != test->values[i])
            return fail(test, "independent source byte", source_after[i], test->values[i]);
    }
    for (i = 0; i < 256; ++i) ring_after[i] = *ram(0xffff810aU + i);
    for (i = 0; i < 7; ++i)
        if (state[8U + i] != 0x18283848U + i * 0x01010101U)
            return fail(test, "natural callee-saved register", state[8U + i], 0x18283848U + i * 0x01010101U);
    if (state[20] != state[21] || state[19] != state[22])
        return fail(test, "natural SP/PR", state[21], state[20]);
    for (i = 0; i < 4; ++i)
        if (state[40U + i] != state[24U + i])
            return fail(test, "lower frame guard", state[40U + i], state[24U + i]);
    if (state[52] != state[22] || state[53] != state[14] || state[54] != state[13] || state[55] != state[12])
        return fail(test, "natural saved frame", state[52], state[22]);
    for (i = 0; i < 12; ++i)
        if (state[56U + i] != state[68U + i])
            return fail(test, "independent C caller ABI", state[68U + i], state[56U + i]);
    if (!test->transport) result = 0x6bU;
    else if ((test->did >> 8) != 0x11U) result = 0x5aU;
    else if (test->did == 0x1146U && test->flag) result = 0x679U;
    else result = (uint32_t)(int32_t)(int8_t)(test->did & 255U);
    if (state[0] != result) return fail(test, "return value", state[0], result);
    hex(ring_before, 256, first); hex(ring_after, 256, last);
    printf("SID22_CASE {\"index\":%u,\"id\":\"%s\",\"gpr\":", test->index, test->id);
    array(state, 15);
    printf(",\"sr_after\":%lu,\"gbr\":%lu,\"mach\":%lu,\"macl\":%lu,\"pr\":%lu,"
           "\"sp_before\":%lu,\"sp_after\":%lu,\"continuation\":%lu,\"sr_before\":%lu,",
           (unsigned long)state[15], (unsigned long)state[16], (unsigned long)state[17],
           (unsigned long)state[18], (unsigned long)state[19], (unsigned long)state[20],
           (unsigned long)state[21], (unsigned long)state[22], (unsigned long)state[23]);
    printf("\"stub_args\":[%lu,%lu],\"stub_count\":%lu,\"stub_kind\":%lu,\"return_value\":%lu,",
           (unsigned long)read_word(0xf000), (unsigned long)read_word(0xf004),
           (unsigned long)read_word(0xf008), (unsigned long)read_word(0xf00c), (unsigned long)state[0]);
    printf("\"sources_before\":"); byte_array(source_before, test->width);
    printf(",\"sources_after\":"); byte_array(source_after, test->width);
    printf(",\"buffer_before\":\"%s\",\"buffer_after\":\"%s\",", first, last);
    printf("\"frame_before\":"); array(state + 24, 16);
    printf(",\"frame_after\":"); array(state + 40, 16);
    printf(",\"caller_abi_before\":"); array(state + 56, 12);
    printf(",\"caller_abi_after\":"); array(state + 68, 12);
    puts(",\"ram_checked_bytes\":65536,\"outside_writes_unchanged\":true,\"lower_guard_unchanged\":true}");
    return 1;
}

int main(void)
{
    unsigned index, count = EARLY_ONLY ? sizeof(sid22_early_indices) / sizeof(sid22_early_indices[0])
                                      : sizeof(sid22_cases) / sizeof(sid22_cases[0]);
    for (index = 0; index < count; ++index)
        if (!run_case(&sid22_cases[EARLY_ONLY ? sid22_early_indices[index] : index])) return 1;
    if (EARLY_ONLY)
        printf("VQ_SH_ELF_SID22_SUBSET status=PASS region=jk08a-sid22-pointer-read cases=%u production=false\n", count);
    else printf("VQ_SH_ELF_STOCK_CODE status=PASS region=jk08a-sid22-pointer-read cases=%u\n", count);
    return 0;
}
