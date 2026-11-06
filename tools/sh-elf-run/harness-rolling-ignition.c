/* Exact stock ignition paths, dwell suppression and instruction-boundary IRQs. */
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
    uint32_t stock, command, fallback, publisher, candidate, returned, ordinary;
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

#ifdef VQ_COUPLED
volatile uint32_t rolling_irq_observation[13];
static uint32_t vectors[256] __attribute__((aligned(1024)));
static unsigned pins, spark_edges[6], dwell_edges[6];

static void pin_registers(void)
{
    put16(ram(0xfffff746U), (uint16_t)((pins & 31U) << 8));
    put16(ram(0xfffff738U), (uint16_t)((pins & 32U) << 10));
}

static void service(uint32_t handler)
{
    uint32_t old_vbr, old_sr, entry_sr, table = (uint32_t)(uintptr_t)vectors;
    vectors[64] = handler;
    __asm__ volatile ("stc vbr,%0" : "=r" (old_vbr));
    __asm__ volatile ("stc sr,%0" : "=r" (old_sr));
    entry_sr = (old_sr & ~0xf0U) | 0x80U;
    __asm__ volatile ("ldc %0,vbr" : : "r" (table) : "memory");
    __asm__ volatile ("ldc %0,sr\n\tnop\n\ttrapa #0x40" : : "r" (entry_sr) : "memory");
    __asm__ volatile ("ldc %0,sr" : : "r" (old_sr) : "memory");
    __asm__ volatile ("ldc %0,vbr" : : "r" (old_vbr) : "memory");
}

static void compare_event(unsigned reset)
{
    unsigned i, mask = (u16(ram(0xfffff700U)) >> (reset ? 8 : 0)) & 63U;
#ifdef VQ_LEGACY_LATE_VETO
    if (!reset) *ram(0xffff8511U) |= 0x80;
#endif
    for (i = 0; i < 6; ++i) if (mask & (1U << i)) {
        if (reset && (pins & (1U << i))) ++dwell_edges[i];
        if (!reset && !(pins & (1U << i))) ++spark_edges[i];
    }
    if (reset) pins &= ~mask; else pins |= mask;
    pin_registers();
    service(reset ? 0x2af38U : 0x2ab24U);
}

static unsigned tooth_time(unsigned n)
{
    /* Phase zero skips the two nominal positions before the first tooth
       and after every ten physical teeth. One nominal degree is 100 ticks. */
    return 10000U + 1000U*n + 2000U*((n + 9U)/10U);
}

static void engine_inputs(unsigned button)
{
    put16(ram(0xffff113cU), 500);
    put16(ram(0xffff11bcU), 280);
    put16(ram(0xffff3b3dU), 5000);
    *ram(0xffff3b38U) = 0;
    *ram(0xffff4195U) = 1;
    *ram(0xffff4185U) = 0x80;
    *ram(0xffff2a85U) = (uint8_t)button;
    *ram(0xffff2672U) = 100;
    *ram(0xffff1077U) = 150;
    *ram(0xffff5d00U) = *ram(STATE + 4);
}

static int release_engine(unsigned row)
{
    struct context context;
    struct observation observation;
    memset(&context, 0, sizeof(context));
    engine_inputs(0x20);
    stock_invoke_ignition_consumer(0xd38e4U, &context, &observation);
    if (*ram(STATE) != 2 || *ram(STATE + 1) != 7 || u16(ram(STATE + 0x1a)) != 0)
        return fail(row, "engine CANCEL release", *ram(STATE + 1), 7);
    return 1;
}

static int coupled_row(unsigned row, const struct command_case *test, unsigned dwell,
                       unsigned q, unsigned tooth_first, unsigned release_at)
{
    unsigned n, now = 10000, a_done = 0, b_done = 0, expected_cut = q != 0;
    unsigned expected_q = q, expected_events = 1, released = 0;
    if (!builder_row(row, test, 0, dwell)) return 0;
    {
        struct context context;
        struct observation observation;
        unsigned efficiency = u16(ram(EXTENSION + 0xc)), law = 1000U - q;
        memset(&context, 0, sizeof(context));
        if (*ram(EXTENSION) == 2) {
            law = (law*efficiency + 999U)/1000U;
            q = 1000U - (1000U*law/efficiency);
        }
        context.r[3] = law;
        context.r[4] = 0xd6320U;
        context.r[5] = STATE;
        context.entry_sr = 0x80;
        stock_invoke_ignition_consumer(0xd6500U, &context, &observation);
        if (u16(ram(STATE + 0x1a)) != q)
            return fail(row, "coherent control publication", u16(ram(STATE + 0x1a)), q);
        expected_cut = q != 0;
        expected_q = q;
    }
    memset(spark_edges, 0, sizeof(spark_edges));
    memset(dwell_edges, 0, sizeof(dwell_edges));
    pins = 62; /* Cylinder one has an existing dwell; the successor is high. */
    pin_registers();
    put16(ram(STATE + 0x22), (uint16_t)(q ? 6000U - 6U*q : 2250U));
    if (release_at == 1) {
        if (!release_engine(row)) return 0;
        released = 1;
        expected_cut = expected_q = expected_events = 0;
    }
    for (n = 1; n < 32 && (!a_done || !b_done); ++n) {
        unsigned next = tooth_time(n), guard = 0;
        while (++guard < 8) {
            unsigned a = !a_done && (*ram(0xffff8517U) & 0x80);
            unsigned b = !b_done && (*ram(0xffff8518U) & 0x80);
            unsigned at = u16(ram(0xfffff5c2U)), bt = u16(ram(0xfffff5c4U));
            unsigned selected = b && (!a || bt < at), deadline = selected ? bt : at;
            if ((!a && !b) || deadline > next || (tooth_first && deadline == next)) break;
            if (deadline < now) return fail(row, "compare scheduled in past", deadline, now);
            now = deadline;
            put16(ram(0xfffff5c0U), (uint16_t)now);
            compare_event(selected);
            if (selected) b_done = 1; else a_done = 1;
        }
        if (a_done && b_done) break;
        now = next;
        put16(ram(0xffff158aU), (uint16_t)now);
        put16(ram(0xfffff5c0U), (uint16_t)now);
        service(0x28ea2U);
        if (release_at == 2 && !released && u16(ram(EXTENSION + 0x18))) {
            if (!release_engine(row)) return 0;
            released = 1;
        }
    }
    if (!a_done || !b_done) return fail(row, "both compares complete", a_done + b_done, 2);
    if (dwell_edges[1] != !expected_cut)
        return fail(row, "successor dwell edge", dwell_edges[1], !expected_cut);
    if (u16(ram(EXTENSION + 0x18)) != expected_events)
        return fail(row, "one eligible arming", u16(ram(EXTENSION + 0x18)), expected_events);
    if (u32(ram(EXTENSION + 0x10)) != expected_q)
        return fail(row, "consumed q", u32(ram(EXTENSION + 0x10)), expected_q);
    if ((*ram(0xffff8511U) & 0xc0U) != (expected_cut ? 0x40U : 0))
        return fail(row, "consistent GR11B sequence", *ram(0xffff8511U), expected_cut ? 0x40 : 0);
    if (release_at == 3 && !release_engine(row)) return 0;
    {
        struct context context;
        struct observation observation;
        unsigned i;
        memset(&context, 0, sizeof(context));
        *ram(0xffff13bdU) = *ram(0xffff13c9U) = 2;
        /* The next event uses the real primary builder. Its set-arming
           recovery must preserve the already selected successor cut. */
        put16(ram(0xffff158aU), (uint16_t)now);
        stock_invoke_ignition_consumer(0x4df82U, &context, &observation);
        for (i = 0; i < 32 && u16(ram(0xffff1558U)); ++i) {
            now += 1000;
            put16(ram(0xffff158aU), (uint16_t)now);
            put16(ram(0xfffff5c0U), (uint16_t)now);
            service(0x28ea2U);
        }
        if (u16(ram(0xffff1558U))) return fail(row, "recovery countdown", i, 0);
        if (expected_cut && (u16(ram(0xfffff700U)) & 0x0200))
            return fail(row, "tooth recovery re-enables selected cut", 1, 0);
        compare_event(0);
        if (spark_edges[1] != !expected_cut)
            return fail(row, "successor spark edge", spark_edges[1], !expected_cut);
        /* An immediate primary scheduling call takes the other recovery
           entry. Both paths see the same retained bit6 interlock. */
        context.r[4] = 10;
        pins |= 2;
        pin_registers();
        *ram(0xffff13d1U) = 2;
        stock_invoke_ignition_consumer(0x2a892U, &context, &observation);
        if (expected_cut && (u16(ram(0xfffff700U)) & 0x0200))
            return fail(row, "primary recovery re-enables selected cut", 1, 0);
    }
    return 1;
}

#ifdef VQ_ENGINE_IRQ
static int engine_irq_main(void)
{
    const struct command_case *test = command_cases + VQ_IRQ_CASE;
    struct context context;
    struct observation observation;
    uint32_t old_vbr, table = (uint32_t)(uintptr_t)vectors, sp;
    unsigned i;
    if (!builder_row(0, test, 0, 90)) return 1;
    memset(&context, 0, sizeof(context));
    context.r[3] = 0;
    context.r[4] = 0xd6320U;
    context.r[5] = STATE;
    context.entry_sr = 0x80;
    stock_invoke_ignition_consumer(0xd6500U, &context, &observation);
    if (u16(ram(STATE + 0x1a)) != 1000) return 2;
    put16(ram(STATE + 0x22), 5999);
    put16(ram(0xffff1558U), 0);
    put16(ram(0xffff1448U), 1);
    put16(ram(0xffff144aU), 0);
    *ram(0xffff13d1U) = 2;
    *ram(0xffff8511U) = 0;
    engine_inputs(VQ_IRQ_RELEASE ? 0x20 : 2);
    for (i = 0; i < 13; ++i) rolling_irq_observation[i] = 0;
    vectors[84] = 0x28ea2U;
    __asm__ volatile ("stc vbr,%0" : "=r" (old_vbr));
    __asm__ volatile ("ldc %0,vbr" : : "r" (table) : "memory");
    __asm__ volatile ("mov r15,%0" : "=r" (sp));
    context.entry_sr = 0;
    stock_invoke_ignition_consumer(0xd38e4U, &context, &observation);
    __asm__ volatile ("ldc %0,vbr" : : "r" (old_vbr) : "memory");
    if (memcmp(observation.abi_before, observation.abi_after, 36)
            || observation.abi_before[10] != observation.abi_after[10]) {
        fail(0, "interrupted engine preserved ABI", 1, 0);
        return 1;
    }
    if (*ram(STATE) != (VQ_IRQ_RELEASE ? 2 : 1)
            || u16(ram(STATE + 0x1a)) != (VQ_IRQ_RELEASE ? 0 : 500)) {
        fail(0, "interrupted engine final q", u16(ram(STATE + 0x1a)), VQ_IRQ_RELEASE ? 0 : 500);
        return 1;
    }
    printf("RL_IGNITION_IRQ status=PASS release=%u final_phase=%u final_q=%u stack=%08lx",
           VQ_IRQ_RELEASE, *ram(STATE), u16(ram(STATE + 0x1a)), (unsigned long)sp);
    for (i = 0; i < 13; ++i) printf(" v%u=%08lx", i, (unsigned long)rolling_irq_observation[i]);
    printf("\n");
    return 0;
}
#endif

int main(void)
{
#ifdef VQ_ENGINE_IRQ
    (void)coupled_row;
    return engine_irq_main();
#else
    unsigned i, d, q, order, release, rows = 0;
    for (i = 0; i < sizeof(command_cases)/sizeof(command_cases[0]); ++i) {
        const struct command_case *test = command_cases + i;
        if (!test->ordinary || test->publisher || test->before[0] != 1 || test->before[5] != 1
                || test->fallback || test->command < 60 || test->command > 120
                ) continue;
#ifdef VQ_LEGACY_LATE_VETO
        if (test->command == 120)
            return coupled_row(0, test, 90, 1000, 1, 0) ? 0 : 1;
#endif
        for (d = 0; d < sizeof(coupled_dwells)/sizeof(coupled_dwells[0]); ++d) for (q = 0; q <= 1000; q += 500)
            for (order = 0; order < 2; ++order) for (release = 0; release < 4; ++release) {
                if (!coupled_row(rows, test, coupled_dwells[d], q, order, release)) {
                    fprintf(stderr, "coupled_case=%u P=%u d=%u q=%u order=%u release=%u\n",
                            i, (unsigned)test->command, coupled_dwells[d], q, order, release);
                    return 1;
                }
                ++rows;
            }
    }
    printf("RL_IGNITION_COUPLED status=PASS rows=%u\n", rows);
    return 0;
#endif
}
#else
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
#endif
#else
static int kernel_row(unsigned row, unsigned phase, unsigned mode, unsigned q,
                      unsigned mask, unsigned guard, unsigned seed, unsigned cycle)
{
    static const uint16_t offsets[] = {250, 2250, 4250, 1250, 3250, 5250};
    static const uint32_t sr[] = {0, 0x80, 0xf1, 0x381};
    struct context context;
    struct observation baseline, actual;
    volatile uint8_t *state = ram(STATE), *extension = ram(EXTENSION);
    uint16_t accumulators[6];
    uint32_t sum = 0xffffffd0U;
    unsigned i, pass, cylinder = 0;
    unsigned quiet = seed == 1 ? 255 : (seed == 4 ? 0 : (seed == 6 ? 12 : (seed == 7 ? 254 : 13)));
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
    state[0x1e] = 0x28;
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

    for (pass = 0; pass < (cycle ? 22U : (hold ? 1U : 3U)); ++pass) {
        if (cycle) {
            phase = pass < 2 ? 0 : (pass < 4 ? 1 : (pass < 6 ? 2 : 0));
            state[0] = (uint8_t)phase;
            hold = phase == 1 && mode == 1;
        }
        if (!cycle && pass == 2 && phase == 0) {
            latch = 1;
            *ram(0xffff436fU) = 1;
        }
        cut = 0;
        quiet = phase == 1 ? 0 : (quiet < 255 ? quiet + 1 : 255);
        if (hold && latch == 0) latch = 1;
        else if (phase == 0 && latch == 1 && quiet >= 14) latch = 0;
        if (!hold || q > 1000) {
            memcpy(accumulators, offsets, sizeof(accumulators));
        } else if (!guard && !(veto & 128) && mask && mask <= 32 && !(mask & (mask - 1))) {
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
        if (state[0x1e] != 0x28) return fail(row, "trim ownership", state[0x1e], 0x28);
        if (state[0x1f] != (hold || phase > 2 ? 0 : phase+1))
            return fail(row, "reset phase", state[0x1f], hold || phase > 2 ? 0 : phase+1);
        if (*ram(0xffff436fU) != latch) return fail(row, "misfire latch", *ram(0xffff436fU), latch);
        if (*ram(0xffff8511U) != veto) return fail(row, "veto", *ram(0xffff8511U), veto);
        if (u16(state + 0x1a) != q) return fail(row, "q ownership", u16(state + 0x1a), q);
        if (u32(extension + 0x10) != sum) return fail(row, "consumed q", u32(extension + 0x10), sum);
        if (u16(extension + 0x18) != events) return fail(row, "eligible count", u16(extension + 0x18), events);
        for (i = 0; i < 6; ++i)
            if (u16(state + 0x20 + 2*i) != accumulators[i])
                return fail(row, "accumulator", u16(state + 0x20 + 2*i), accumulators[i]);
    }
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
        if (!kernel_row(rows, phases[p], modes[m], fractions[q], masks[c], g, s, 0)) return 1;
        ++rows;
    }
    if (!kernel_row(rows++, 0, 1, 500, 1, 0, 0, 1)) return 1;
    printf("RL_DWELL_VETO_KERNEL status=PASS rows=%u divider=stock alias=enabled hardware_ready=false\n", rows);
    return 0;
}
#endif
