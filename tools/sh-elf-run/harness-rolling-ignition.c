/* Dwell-veto kernel and exact stock-divider ABI observation. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define RAM_BASE 0x01000000U
#define STATE 0xffff5d40U
#define EXTENSION 0xffff6100U
#define VETO 0x000d60c0U
#define DIVIDER 0x00021ce0U

struct context { uint32_t r[15], gbr, mach, macl, entry_sr, fifth_argument; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[192], frame_after[192];
    uint32_t sr_before;
};
extern void stock_invoke_ignition_consumer(uint32_t, const struct context *, struct observation *);
_Static_assert(sizeof(struct context) == 80U, "complete context ABI");
_Static_assert(sizeof(struct observation) == 572U, "complete observer ABI");
#ifdef VQ_ALIAS_COLLISION
volatile uint32_t alias_collision __attribute__((section(".alias_collision"))) = 1;
#endif

static volatile uint8_t *ram(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)(RAM_BASE + (address & 65535U));
}

static uint16_t u16(const volatile uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] << 8) | p[1];
}

static uint32_t u32(const volatile uint8_t *p)
{
    return ((uint32_t)u16(p) << 16) | u16(p + 2);
}

static void put16(volatile uint8_t *p, uint16_t value)
{
    p[0] = (uint8_t)(value >> 8);
    p[1] = (uint8_t)value;
}

static void put32(volatile uint8_t *p, uint32_t value)
{
    put16(p, (uint16_t)(value >> 16));
    put16(p + 2, (uint16_t)value);
}

static int fail(unsigned row, const char *field, uint32_t actual, uint32_t expected)
{
    fprintf(stderr, "dwell_veto[%u] %s actual=%08lx expected=%08lx\n",
            row, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

#ifdef VQ_BUILDERS
struct command_case {
    uint32_t stock, command, fallback, publisher, candidate, returned;
    uint8_t configuration[102], before[76], after[76];
};
#include "rolling-ignition-cases.h"

/* These spans contain ordinary fixture memory, including the explicitly
   controlled APC register state. Peripheral events are separate steps. */
struct arena {
    uint8_t apc[0x1600], flags[0x200], peripheral[0x400], record[76];
};
static struct arena initial, primary, secondary, consumer;

static void capture(struct arena *image)
{
    memcpy(image->apc, (const void *)ram(0xffff1000U), sizeof(image->apc));
    memcpy(image->flags, (const void *)ram(0xffff8400U), sizeof(image->flags));
    memcpy(image->peripheral, (const void *)ram(0xfffff400U), sizeof(image->peripheral));
    memcpy(image->record, (const void *)ram(STATE), 44);
    memcpy(image->record + 44, (const void *)ram(EXTENSION), 32);
}

static void restore(const struct arena *image)
{
    memcpy((void *)ram(0xffff1000U), image->apc, sizeof(image->apc));
    memcpy((void *)ram(0xffff8400U), image->flags, sizeof(image->flags));
    memcpy((void *)ram(0xfffff400U), image->peripheral, sizeof(image->peripheral));
    memcpy((void *)ram(STATE), image->record, 44);
    memcpy((void *)ram(EXTENSION), image->record + 44, 32);
}

static int records(unsigned row, const struct command_case *test)
{
    unsigned i;
    for (i = 0; i < 76; ++i) {
        uint8_t actual = i < 44 ? ram(STATE)[i] : ram(EXTENSION)[i - 44];
        if (actual != test->after[i]) return fail(row, "published record", actual, test->after[i]);
    }
    return 1;
}

static int builder_row(unsigned row, const struct command_case *test, unsigned phase, unsigned dwell)
{
    struct context context;
    struct observation observation;
    unsigned i, offset = (120U - dwell) & 255U;
    memset((void *)(uintptr_t)RAM_BASE, 0, 65536);
    memcpy((void *)(uintptr_t)0xd6320U, test->configuration, 102);
    memcpy((void *)ram(STATE), test->before, 44);
    memcpy((void *)ram(EXTENSION), test->before + 44, 32);
    *ram(0xffff11d4U) = (uint8_t)(110U - (test->stock & 255U));
    *ram(0xffff24c9U) = test->fallback ? 0x40 : 0;
    *ram(0xffff13b2U) = (uint8_t)phase;
    *ram(0xffff13bdU) = 1;
    *ram(0xffff13c9U) = *ram(0xffff13d3U) = 1;
    *ram(0xffff13d1U) = 2;
    *ram(0xffff8501U) = *ram(0xffff84eaU) = *ram(0xffff4185U) = 0x80;
    *ram(0xffff850eU) = 0x80;
    *ram(0xffff4195U) = 1;
    *ram(0xffff237aU) = (uint8_t)dwell;
    put16(ram(0xffff22bcU), 1000);
    put16(ram(0xffff11fcU), 12000);
    put16(ram(0xffff1586U), 10000);
    put16(ram(0xffff158aU), 10000);
    put16(ram(0xfffff5c0U), 10000);
    put16(ram(0xfffff746U), 0x1f00);
    put16(ram(0xfffff738U), 0x8000);
    put32(ram(0xfffff430U), 320000);
    memset(&context, 0, sizeof(context));
    for (i = 0; i < 15; ++i) context.r[i] = 0x10203040U + i*0x01010101U;
    context.gbr = 0x12344321U;
    context.mach = 0x10203040U;
    context.macl = 0x50607080U;
    context.entry_sr = 0x80;
    if (test->publisher) {
        context.r[4] = test->stock;
        context.r[5] = test->candidate;
        stock_invoke_ignition_consumer(0xd6540U, &context, &observation);
        if (observation.exit[14] != test->returned)
            return fail(row, "publisher r5", observation.exit[14], test->returned);
        if (observation.exit[15] != test->stock)
            return fail(row, "publisher r4", observation.exit[15], test->stock);
        if (memcmp(observation.abi_before, observation.abi_after, 36))
            return fail(row, "publisher preserved ABI", 1, 0);
        return records(row, test);
    }
    capture(&initial);
    stock_invoke_ignition_consumer(0x4df82U, &context, &observation);
    if (*ram(0xffff2022U) != test->command)
        return fail(row, "shared command", *ram(0xffff2022U), test->command);
    if (!records(row, test)) return 0;
    capture(&primary);
    restore(&initial);
    memcpy((void *)ram(STATE), test->after, 44);
    memcpy((void *)ram(EXTENSION), test->after + 44, 32);
    *ram(0xffff2022U) = (uint8_t)test->command;
    context.r[4] = test->command;
    stock_invoke_ignition_consumer(0x2a892U, &context, &observation);
    capture(&consumer);
    if (memcmp(&primary, &consumer, sizeof(primary)))
        return fail(row, "primary consumer argument", u16(ram(0xffff1558U)),
                    (uint16_t)((uint16_t)primary.apc[0x558] << 8) | primary.apc[0x559]);
    restore(&primary);
    stock_invoke_ignition_consumer(0x4e080U, &context, &observation);
    if (u32(ram(EXTENSION + 0x10)) != 0)
        return fail(row, "builder consumes no q", u32(ram(EXTENSION + 0x10)), 0);
    capture(&secondary);
    restore(&primary);
    *ram(0xffff2230U) = (uint8_t)offset;
    context.r[4] = test->command + offset;
    stock_invoke_ignition_consumer(0x2acbaU, &context, &observation);
    capture(&consumer);
    if (memcmp(&secondary, &consumer, sizeof(secondary)))
        return fail(row, "secondary consumer argument", context.r[4], test->command + offset);
    return 1;
}

int main(void)
{
    static const unsigned phases[] = {0, 4, 9};
    static const unsigned dwells[] = {0, 30, 60, 86, 90, 94, 110, 119, 120, 121};
    unsigned i, p, d, rows = 0;
    for (i = 0; i < sizeof(command_cases)/sizeof(command_cases[0]); ++i) {
        if (command_cases[i].publisher) {
            if (!builder_row(rows, &command_cases[i], 0, 90)) return 1;
            ++rows;
            continue;
        }
        for (p = 0; p < 3; ++p) for (d = 0; d < 10; ++d) {
#ifdef VQ_BUILDER_COVERAGE
            if (p || d) continue;
#endif
            if (!builder_row(rows, &command_cases[i], phases[p], dwells[d])) {
                fprintf(stderr, "command_case=%u phase=%u dwell=%u\n", i, phases[p], dwells[d]);
                return 1;
            }
            ++rows;
        }
    }
    printf("RL_IGNITION_BUILDERS status=PASS rows=%u stock_consumers=primary,secondary model_records=complete\n", rows);
    return 0;
}
#else
static int kernel_row(unsigned row, unsigned phase, unsigned mode, unsigned q,
                      unsigned mask, unsigned guard, unsigned seed)
{
    static const uint16_t offsets[] = {250, 2250, 4250, 1250, 3250, 5250};
    static const uint32_t sr[] = {0, 0x80, 0xf1, 0x381};
    struct context context;
    struct observation baseline, actual;
    volatile uint8_t *state = ram(STATE), *extension = ram(EXTENSION);
    uint16_t accumulators[6];
    uint32_t sum = 0xffffffd0U;
    unsigned i, cylinder = 0, quiet = seed == 1 ? 255 : (seed == 4 ? 0 : 13);
    unsigned latch = seed == 2 ? 0 : (seed == 3 ? 2 : 1);
    unsigned count = 255, events = 65535, veto = guard == 6 ? 0xa0 : 0x20;
    unsigned hold = phase == 1 && mode == 1, cut = 0;

    memset(&context, 0, sizeof(context));
    memset(&baseline, 0, sizeof(baseline));
    memset(&actual, 0, sizeof(actual));
    for (i = 0; i < 15; ++i) context.r[i] = 0x10203040U + i * 0x01010101U;
    context.r[0] = 10;
    context.r[1] = 0xfedcba98U ^ row;
    context.gbr = 0x12344321U;
    context.mach = 0x10203040U;
    context.macl = 0x50607080U;
    context.entry_sr = sr[seed % 4];
    stock_invoke_ignition_consumer(DIVIDER, &context, &baseline);

    for (i = 0; i < 44; ++i) state[i] = 0;
    for (i = 0; i < 32; ++i) extension[i] = 0;
    state[0] = (uint8_t)phase;
    state[5] = (uint8_t)mode;
    put16(state + 0x1a, (uint16_t)q);
    state[0x1c] = (uint8_t)quiet;
    state[0x1d] = (uint8_t)count;
    for (i = 0; i < 6; ++i) {
        accumulators[i] = seed == 4 ? 6000 : (uint16_t)(offsets[i] + 100);
        if (seed == 5) accumulators[i] = (uint16_t)(6000U - 6*q);
        if (seed == 6) accumulators[i] = (uint16_t)(5999U - 6*q);
        if (seed == 7) accumulators[i] = 5999;
        put16(state + 0x20 + 2*i, accumulators[i]);
    }
    put32(extension + 0x10, sum);
    put16(extension + 0x18, (uint16_t)events);
    *ram(0xffff436fU) = (uint8_t)latch;
    *ram(0xffff8501U) = guard == 1 ? 0 : 0x80;
    *ram(0xffff24c9U) = guard == 2 ? 0x40 : 0;
    *ram(0xffff84eaU) = guard == 3 ? 0 : 0x80;
    *ram(0xffff4185U) = guard == 4 ? 0 : 0x80;
    *ram(0xffff13d1U) = (uint8_t)mask;
    *ram(0xffff13d2U) = guard == 5 ? 1 : 0;
    *ram(0xffff8511U) = (uint8_t)veto;

    quiet = phase == 1 ? 0 : (quiet < 255 ? quiet + 1 : 255);
    if (hold && latch == 0) latch = 1;
    else if (phase == 0 && latch == 1 && quiet >= 14) latch = 0;
    if (!hold || q > 1000) {
        memcpy(accumulators, offsets, sizeof(accumulators));
    } else if (!guard && mask && mask <= 32 && !(mask & (mask - 1))) {
        while ((1U << cylinder) != mask) ++cylinder;
        if (accumulators[cylinder] >= 6000) {
            memcpy(accumulators, offsets, sizeof(accumulators));
        } else {
            unsigned value = accumulators[cylinder] + 6*q;
            if (value >= 6000) { value -= 6000; cut = 1; }
            accumulators[cylinder] = (uint16_t)value;
            sum += q;
            events = (events + 1) & 65535;
            if (cut) { veto |= 128; count = (count + 1) & 255; }
        }
    }
    stock_invoke_ignition_consumer(VETO, &context, &actual);
    for (i = 0; i < 20; ++i)
        if (actual.exit[i] != baseline.exit[i]) return fail(row, "divider ABI", actual.exit[i], baseline.exit[i]);
    if (actual.sp != baseline.sp) return fail(row, "stack", actual.sp, baseline.sp);
    if (memcmp(actual.abi_before, actual.abi_after, 40)) return fail(row, "caller ABI", 1, 0);
    if (state[0x1c] != quiet) return fail(row, "quiet", state[0x1c], quiet);
    if (state[0x1d] != count) return fail(row, "cut count", state[0x1d], count);
    if (*ram(0xffff436fU) != latch) return fail(row, "misfire latch", *ram(0xffff436fU), latch);
    if (*ram(0xffff8511U) != veto) return fail(row, "veto", *ram(0xffff8511U), veto);
    if (u16(state + 0x1a) != q) return fail(row, "q ownership", u16(state + 0x1a), q);
    if (u32(extension + 0x10) != sum) return fail(row, "consumed q", u32(extension + 0x10), sum);
    if (u16(extension + 0x18) != events) return fail(row, "eligible count", u16(extension + 0x18), events);
    for (i = 0; i < 6; ++i)
        if (u16(state + 0x20 + 2*i) != accumulators[i])
            return fail(row, "accumulator", u16(state + 0x20 + 2*i), accumulators[i]);
    return 1;
}

int main(void)
{
    static const unsigned phases[] = {0, 1, 2, 255};
    static const unsigned modes[] = {0, 1, 255};
    static const unsigned fractions[] = {0, 1, 166, 167, 500, 999, 1000, 1001};
    static const unsigned masks[] = {0, 1, 2, 4, 8, 16, 32, 3, 64, 128};
    unsigned p, m, q, c, g, s, rows = 0;
    for (p = 0; p < 4; ++p)
    for (m = 0; m < 3; ++m)
    for (q = 0; q < 8; ++q)
    for (c = 0; c < 10; ++c)
    for (g = 0; g < 7; ++g)
    for (s = 0; s < 8; ++s) {
#ifdef VQ_VETO_COVERAGE
        if (g && !(p == 1 && m == 1 && q == 5 && c == 1 && s == 0)) continue;
        if (!g && !(p == 1 && m == 1) && !(q == 4 && c == 1)) continue;
#endif
        if (!kernel_row(rows, phases[p], modes[m], fractions[q], masks[c], g, s)) return 1;
        ++rows;
    }
    printf("RL_DWELL_VETO_KERNEL status=PASS rows=%u divider=stock alias=enabled hardware_ready=false\n", rows);
    return 0;
}
#endif
