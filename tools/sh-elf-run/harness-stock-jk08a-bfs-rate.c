#include <stdint.h>
#include <stdio.h>
#include "stock-jk08a-bfs-rate-cases.h"

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(PRIMARY_ENTRY) || !defined(CORRECTION_ENTRY) \
    || !defined(BLEND_ENTRY) || !defined(POST_QUERY_ENTRY) || !defined(QUERY_ENTRY) \
    || !defined(PRIMARY_BASE) || !defined(MODE_BASE) || !defined(Q7_SOURCE) \
    || !defined(SELECTED_SOURCE) || !defined(COEFFICIENT) || !defined(REFERENCE) \
    || !defined(WORKING) || !defined(BLENDED) || !defined(CORRECTION) \
    || !defined(FLAGS) || !defined(ALPHA) || !defined(ENABLE) \
    || !defined(DIAGNOSTIC) || !defined(WEIGHT) || !defined(BLEND_PRIOR) \
    || !defined(TIMER_FIRST) || !defined(TIMER_SECOND) || !defined(TIMER_THIRD) \
    || !defined(SOURCE_FIRST) || !defined(SOURCE_SECOND) || !defined(MONITOR) \
    || !defined(MODE) || !defined(CORRECTION_GAIN) || !defined(LATCH_SET) \
    || !defined(LATCH_CLEAR) || !defined(QUERY_RECORDS)
#error "the verifier binds every tested entry, source, state, and calibration"
#endif

#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define TEST_RAM_BASE 0x01000000U
#define STOCK_MACH 0x60718293U
#define STOCK_MACL 0xa4b5c6d7U
#define STOCK_R10 0x20304050U
#define STOCK_R11 0x31415161U

extern uint32_t stock_invoke_bfs_rate(uint32_t, const uint32_t *, uint32_t *);

enum scope { FULL, CORRECTION_ONLY, BLEND_ONLY, POST_QUERY, QUERY_ONLY };
struct outputs {
    uint16_t working, blended, correction;
    uint8_t flags, first, second, third, monitor;
};

/* SR, PR, MACL, MACH, GBR, R14..R0, fragment SP, return continuation,
 * and independent before/after C ABI snapshots. All registers are observed;
 * the fragment is allowed its stock scratch registers and live allocations. */
static uint32_t state[62];
static uint8_t before[0x10000];
static uint8_t calibration_before[4];
static const uint32_t calibration_addresses[] = {
    LATCH_SET, LATCH_CLEAR, CORRECTION_GAIN, MODE
};
static const uint32_t abi_literals[] = {
    0x18283848U, 0x19293949U, 0x1a2a3a4aU, 0x1b2b3b4bU,
    0x1c2c3c4cU, 0x1d2d3d4dU, 0x1e2e3e4eU,
    0x12344321U, 0x10203040U, 0x50607080U
};
static enum scope selected_scope;

static volatile uint8_t *ram(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (address & 0xffffU));
}

static uint32_t alias(uint32_t address)
{
    return (uint32_t)(uintptr_t)ram(address);
}

static void set_word(uint32_t address, uint16_t value)
{
    *(volatile uint16_t *)ram(address) = value;
}

static uint16_t get_word(uint32_t address)
{
    return *(const volatile uint16_t *)ram(address);
}

static int check(const char *name, const char *field, uint32_t actual, uint32_t expected)
{
    if (actual == expected) return 1;
    printf("STOCK_FAIL %s %s %s actual=%08lx expected=%08lx\n", REGION_KEY,
           name, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static void prepare(void)
{
    size_t byte;
    for (byte = 0; byte < sizeof(before); ++byte)
        ram(0xffff0000U)[byte] = (uint8_t)(byte * 29U + 7U);
    *(volatile uint8_t *)(uintptr_t)LATCH_SET = 202U;
    *(volatile uint8_t *)(uintptr_t)LATCH_CLEAR = 200U;
    *(volatile uint8_t *)(uintptr_t)MODE = 0x7aU;
    *(volatile uint8_t *)(uintptr_t)CORRECTION_GAIN = 160U;
    set_word(SELECTED_SOURCE, 0U);
    set_word(Q7_SOURCE, 0U);
    set_word(COEFFICIENT, 0U);
    set_word(REFERENCE, 0U);
    set_word(WORKING, 0U);
    set_word(BLENDED, 0xa55aU);
    set_word(CORRECTION, 0xa55aU);
    ram(ALPHA)[0] = 0U;
    ram(FLAGS)[0] = 0U;
    ram(SOURCE_FIRST)[0] = 0U;
    ram(SOURCE_SECOND)[0] = 0U;
    ram(ENABLE)[0] = 0U;
    ram(DIAGNOSTIC)[0] = 0U;
    ram(TIMER_FIRST)[0] = 0U;
    ram(TIMER_SECOND)[0] = 0U;
    ram(TIMER_THIRD)[0] = 0U;
    ram(MONITOR)[0] = 0xa5U;
    ram(QUERY_RECORDS + 2U)[0] = 0xffU;
}

static void snapshot(enum scope scope)
{
    size_t byte;
    selected_scope = scope;
    for (byte = 0; byte < sizeof(before); ++byte)
        before[byte] = ram(0xffff0000U)[byte];
    for (byte = 0; byte < ARRAY_SIZE(calibration_addresses); ++byte)
        calibration_before[byte] =
            *(const volatile uint8_t *)(uintptr_t)calibration_addresses[byte];
}

static int output_byte(size_t byte, uint32_t address, size_t width)
{
    size_t first = address & 0xffffU;
    return byte >= first && byte < first + width;
}

static int preserved(const char *name)
{
    size_t byte;
    for (byte = 0; byte < sizeof(before); ++byte) {
        int writable = 0;
        if (selected_scope == FULL) {
            writable = output_byte(byte, WORKING, 2U)
                || output_byte(byte, BLENDED, 2U)
                || output_byte(byte, CORRECTION, 2U)
                || output_byte(byte, FLAGS, 1U)
                || output_byte(byte, TIMER_FIRST, 1U)
                || output_byte(byte, TIMER_SECOND, 1U)
                || output_byte(byte, TIMER_THIRD, 1U)
                || output_byte(byte, MONITOR, 1U);
        } else if (selected_scope == CORRECTION_ONLY) {
            writable = output_byte(byte, CORRECTION, 2U);
        } else if (selected_scope == BLEND_ONLY) {
            writable = output_byte(byte, BLENDED, 2U);
        } else if (selected_scope == POST_QUERY) {
            writable = output_byte(byte, TIMER_THIRD, 1U)
                || output_byte(byte, MONITOR, 1U)
                || output_byte(byte, CORRECTION, 2U)
                || output_byte(byte, BLENDED, 2U);
        }
        if (!writable && before[byte] != ram(0xffff0000U)[byte])
            return check(name, "read-only-input-or-neighbor", (uint32_t)byte, 0xffffffffU);
    }
    for (byte = 0; byte < ARRAY_SIZE(calibration_addresses); ++byte)
        if (!check(name, "calibration-preservation",
                   *(const volatile uint8_t *)(uintptr_t)calibration_addresses[byte],
                   calibration_before[byte])) return 0;
    return 1;
}

static int verify_outputs(const char *name, struct outputs expected)
{
    size_t byte;
    int weighted = ram(ENABLE)[0] & 1U;
    int copy;
    weighted = weighted && !(ram(DIAGNOSTIC)[0] & 4U) && (expected.flags & 0x80U);
    copy = selected_scope != QUERY_ONLY
        && (*(const volatile uint8_t *)(uintptr_t)MODE & 0x10U) && !weighted;
    for (byte = 0; byte < 32U; ++byte) {
        uint32_t first = state[46U + byte / 4U];
        uint32_t last = state[54U + byte / 4U];
        unsigned shift = 24U - 8U * (byte % 4U);
        uint8_t want = (uint8_t)(first >> shift);
        if (byte == 16U && selected_scope != BLEND_ONLY && selected_scope != QUERY_ONLY)
            want = ram(ENABLE)[0] & 1U;
        if (byte >= 20U && byte < 24U && copy) {
            uint32_t signed_word = (uint32_t)(int32_t)(int16_t)expected.working;
            want = (uint8_t)(signed_word >> shift);
        }
        if (!check(name, "fragment-frame-byte", (uint8_t)(last >> shift), want)) return 0;
    }
    return check(name, "working", get_word(WORKING), expected.working)
        && check(name, "blended", get_word(BLENDED), expected.blended)
        && check(name, "correction", get_word(CORRECTION), expected.correction)
        && check(name, "flags", ram(FLAGS)[0], expected.flags)
        && check(name, "first-timer", ram(TIMER_FIRST)[0], expected.first)
        && check(name, "second-timer", ram(TIMER_SECOND)[0], expected.second)
        && check(name, "third-timer", ram(TIMER_THIRD)[0], expected.third)
        && check(name, "monitor", ram(MONITOR)[0], expected.monitor)
        && preserved(name);
}

static uint32_t reg(unsigned number) { return state[19U - number]; }

static int invoke(const char *name, uint32_t entry, uint32_t r0, uint32_t r4,
                  uint32_t q, uint32_t flags, uint32_t r13, uint32_t local_flag)
{
    size_t item;
    const uint32_t context[] = {
        r0, 0U, 0x22334455U, 0x33445566U, r4, q, 0x66778899U,
        get_word(REFERENCE), alias(PRIMARY_BASE), get_word(COEFFICIENT),
        STOCK_R10, STOCK_R11, alias(MODE_BASE), r13, flags,
        alias(BLENDED), STOCK_MACH, STOCK_MACL, local_flag
    };
    if (entry == PRIMARY_ENTRY
        && (!check(name, "entry-q7", q, get_word(Q7_SOURCE))
            || !check(name, "entry-flags", flags, ram(FLAGS)[0]))) return 0;
    (void)stock_invoke_bfs_rate(entry, context, state);
    for (item = 0; item < ARRAY_SIZE(abi_literals); ++item) {
        if (!check(name, "caller-abi-seed", state[22U + item], abi_literals[item])
            || !check(name, "caller-abi-preservation", state[34U + item],
                      state[22U + item])) return 0;
    }
    if (!check(name, "caller-sp", state[44], state[32])
        || !check(name, "caller-pr", state[45], state[33])
        || !check(name, "fragment-sp", state[20] + 76U, state[32])
        || !check(name, "fragment-return", state[1], state[21])
        || !check(name, "stock-gbr", state[4], alias(BLENDED))
        || !check(name, "stock-mach", state[3], STOCK_MACH)
        || !check(name, "stock-r8", reg(8), alias(PRIMARY_BASE))
        || !check(name, "stock-r9", reg(9), context[9])
        || !check(name, "stock-r10", reg(10), STOCK_R10)
        || !check(name, "stock-r11", reg(11), STOCK_R11)
        || !check(name, "stock-r12", reg(12), alias(MODE_BASE))) return 0;
    if (entry == QUERY_ENTRY) {
        uint32_t index = (uint32_t)(int32_t)(int16_t)r4;
        uint32_t offset = index * 3U;
        int sentinel = index == 0xffffffffU;
        return check(name, "query-r13", reg(13), context[13])
            && check(name, "query-r14", reg(14), context[14])
            && check(name, "query-macl", state[2], STOCK_MACL)
            && check(name, "query-record-pointer", reg(1), alias(QUERY_RECORDS))
            && check(name, "query-record-address", reg(2),
                     sentinel ? context[2] : alias(QUERY_RECORDS) + offset)
            && check(name, "query-r3", reg(3), context[3])
            && check(name, "query-r4", reg(4), context[4])
            && check(name, "query-r6", reg(6), context[6])
            && check(name, "query-record-offset", reg(7),
                     sentinel ? context[7] : offset)
            && check(name, "query-condition-bit", state[0] & 1U,
                     reg(0) ? 0U : 1U);
    }
    /* R1 is the simulator continuation's scratch register. Stock R0..R7,
     * R13, R14, MACL, and SR are live allocations at this fragment boundary,
     * rather than the callee-saved contract of the complete producer. */
    return check(name, "boundary-r1", reg(1), state[21])
        && check(name, "stock-mode-pointer", reg(13), MODE)
        && check(name, "stock-limiter-selection", reg(5),
                 *(const volatile uint8_t *)(uintptr_t)MODE & 0x10U);
}

int main(void)
{
    size_t index, cases = 0U;
    for (index = 0; index < ARRAY_SIZE(rate_cases); ++index) {
        const struct rate_case *t = rate_cases + index;
        struct outputs expected = {t->expected, t->expected, 0U,
            (uint8_t)(t->flags & 0x7fU), 0U, 0U, 0U, 0x25U};
        prepare();
        set_word(Q7_SOURCE, t->q); set_word(SELECTED_SOURCE, t->source);
        set_word(COEFFICIENT, t->coefficient); set_word(REFERENCE, t->reference);
        set_word(WORKING, t->previous); ram(FLAGS)[0] = t->flags;
        snapshot(FULL);
        if (!invoke(t->name, PRIMARY_ENTRY, 0U, 0U, t->q, t->flags, 65535U, 0U)
            || !verify_outputs(t->name, expected)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(correction_cases); ++index) {
        const struct correction_case *t = correction_cases + index;
        struct outputs expected = {t->current, 0xa55aU, (uint16_t)t->expected,
            0U, 0U, 0U, 0U, 0xa5U};
        prepare(); *(volatile uint8_t *)(uintptr_t)MODE = 0U;
        *(volatile uint8_t *)(uintptr_t)CORRECTION_GAIN = t->gain;
        set_word(WORKING, t->current); set_word(REFERENCE, t->prior);
        ram(ENABLE)[0] = 1U; ram(DIAGNOSTIC)[0] = 4U;
        snapshot(CORRECTION_ONLY);
        if (!invoke(t->name, CORRECTION_ENTRY, 0U, 0U, 0U, 0U, MODE, 0U)
            || !verify_outputs(t->name, expected)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(blend_cases); ++index) {
        const struct blend_case *t = blend_cases + index;
        struct outputs expected = {t->current, t->expected, 0xa55aU,
            0x80U, 0U, 0U, 0U, 0xa5U};
        prepare(); ram(ENABLE)[0] = 1U; ram(FLAGS)[0] = 0x80U;
        ram(WEIGHT)[0] = t->gain;
        set_word(WORKING, t->current); set_word(BLEND_PRIOR, t->prior);
        snapshot(BLEND_ONLY);
        if (!invoke(t->name, BLEND_ENTRY, 0U, 0U, 0U, 0x80U, MODE, 1U)
            || !verify_outputs(t->name, expected)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(timer_cases); ++index) {
        const struct timer_case *t = timer_cases + index;
        struct outputs expected = {0U, 0U, 0U, 0U,
            t->expected, t->expected, t->third, t->monitor};
        prepare(); ram(TIMER_FIRST)[0] = t->previous;
        ram(TIMER_SECOND)[0] = t->previous; ram(TIMER_THIRD)[0] = t->previous;
        ram(SOURCE_FIRST)[0] = t->active ? 0x80U : 0U;
        ram(SOURCE_SECOND)[0] = t->active ? 0x40U : 0U;
        snapshot(FULL);
        if (!invoke("timers", PRIMARY_ENTRY, 0U, 0U, 0U, 0U, 65535U, 0U)
            || !verify_outputs("timers", expected)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(latch_cases); ++index) {
        const struct latch_case *t = latch_cases + index;
        struct outputs expected = {0U, 0U, 0U, t->expected, 0U, 0U, 0U, 0x25U};
        prepare(); set_word(Q7_SOURCE, t->q); set_word(REFERENCE, t->reference);
        set_word(WORKING, 77U); ram(ALPHA)[0] = t->alpha; ram(FLAGS)[0] = t->flags;
        snapshot(FULL);
        if (!invoke(t->name, PRIMARY_ENTRY, 0U, 0U, t->q, t->flags, 65535U, 0U)
            || !verify_outputs(t->name, expected)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(coupled_cases); ++index) {
        const struct coupled_case *t = coupled_cases + index;
        struct outputs expected = {t->working, t->blended, (uint16_t)t->correction,
            t->flags, 0U, 0U, 0U, 0x25U};
        prepare(); set_word(COEFFICIENT, t->coefficient);
        set_word(REFERENCE, t->reference); set_word(BLEND_PRIOR, t->prior);
        ram(ALPHA)[0] = t->alpha; ram(ENABLE)[0] = t->enable;
        ram(DIAGNOSTIC)[0] = t->diagnostic; ram(WEIGHT)[0] = t->gain;
        snapshot(FULL);
        if (!invoke(t->name, PRIMARY_ENTRY, 0U, 0U, 0U, 0U, 65535U, 0U)
            || !verify_outputs(t->name, expected)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(timer_combinations); ++index) {
        const struct timer_combination *t = timer_combinations + index;
        struct outputs expected = {0U, 0U, 0U, 0U,
            t->first, t->second, t->third, t->monitor};
        prepare(); ram(SOURCE_FIRST)[0] = (t->mask & 1U) ? 0x80U : 0x7fU;
        ram(SOURCE_SECOND)[0] = (t->mask & 2U) ? 0x40U : 0xbfU;
        /* This independent record pattern cannot override the -1 sentinel. */
        ram(QUERY_RECORDS + 2U)[0] = (t->mask & 4U) ? 0xffU : 0U;
        snapshot(FULL);
        if (!invoke("timer-combinations", PRIMARY_ENTRY, 0U, 0U, 0U, 0U, 65535U, 0U)
            || !verify_outputs("timer-combinations", expected)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(mode_cases); ++index) {
        const struct mode_case *t = mode_cases + index;
        struct outputs expected = {0U, t->blended, 0U, 0U,
            4U, 4U, t->third, t->monitor};
        prepare(); *(volatile uint8_t *)(uintptr_t)MODE = t->mode;
        ram(SOURCE_FIRST)[0] = 0x80U; ram(SOURCE_SECOND)[0] = 0x40U;
        ram(TIMER_THIRD)[0] = 255U; ram(MONITOR)[0] = 0x37U;
        snapshot(FULL);
        if (!invoke("mode-byte", PRIMARY_ENTRY, 0U, 0U, 0U, 0U, 65535U, 0U)
            || !verify_outputs("mode-byte", expected)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(condition_cases); ++index) {
        const struct condition_case *t = condition_cases + index;
        struct outputs expected = {399U, t->blended, (uint16_t)t->correction,
            (t->mask & 4U) ? 0x80U : 0U, t->first, t->second, 0U, t->monitor};
        prepare(); set_word(COEFFICIENT, 65535U); set_word(REFERENCE, 200U);
        set_word(BLEND_PRIOR, 1000U); ram(ALPHA)[0] = (t->mask & 4U) ? 255U : 0U;
        ram(ENABLE)[0] = (t->mask & 1U) ? 1U : 0xfeU;
        ram(DIAGNOSTIC)[0] = (t->mask & 2U) ? 4U : 0xfbU;
        ram(SOURCE_FIRST)[0] = (t->mask & 8U) ? 0x80U : 0x7fU;
        ram(SOURCE_SECOND)[0] = (t->mask & 16U) ? 0x40U : 0xbfU;
        ram(WEIGHT)[0] = 128U;
        snapshot(FULL);
        if (!invoke("conditions", PRIMARY_ENTRY, 0U, 0U, 0U, 0U, 65535U, 0U)
            || !verify_outputs("conditions", expected)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(post_query_cases); ++index) {
        const struct post_query_case *t = post_query_cases + index;
        struct outputs expected = {1234U, 1234U, 0U, 0U,
            t->first, t->second, t->third, t->monitor};
        prepare(); set_word(WORKING, 1234U);
        ram(TIMER_FIRST)[0] = t->first; ram(TIMER_SECOND)[0] = t->second;
        ram(TIMER_THIRD)[0] = t->previous;
        snapshot(POST_QUERY);
        /* W, latch and timers are already published. R4 is the caller's -1;
         * only R0 supplies the artificial post-call predicate return value. */
        if (!invoke(t->name, POST_QUERY_ENTRY, t->result, 0xffffffffU,
                    0U, 0U, MODE, 0U) || !verify_outputs(t->name, expected)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(query_cases); ++index) {
        const struct query_case *t = query_cases + index;
        struct outputs expected = {0U, 0xa55aU, 0xa55aU, 0U, 0U, 0U, 0U, 0xa5U};
        prepare(); ram(QUERY_RECORDS + 2U + 3 * t->index)[0] = t->bits;
        snapshot(QUERY_ONLY);
        if (!invoke(t->name, QUERY_ENTRY, 0U, t->argument, 0U, 0U, MODE, 0U)
            || !check(t->name, "query-return", reg(0), t->expected)
            || !check(t->name, "query-result-register", reg(5), t->expected)
            || !verify_outputs(t->name, expected)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(natural_timer_cases); ++index) {
        const struct natural_timer_case *t = natural_timer_cases + index;
        struct outputs expected = {0U, t->blended, 0U, 0U,
            0U, 0U, t->third, t->monitor};
        prepare(); *(volatile uint8_t *)(uintptr_t)MODE = t->mode;
        ram(TIMER_THIRD)[0] = t->previous;
        snapshot(FULL);
        if (!invoke("natural-sentinel-timer", PRIMARY_ENTRY, 0U, 0U, 0U, 0U, 65535U, 0U)
            || !verify_outputs("natural-sentinel-timer", expected)) return 1;
        ++cases;
    }
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",
           REGION_KEY, (unsigned long)cases);
    return 0;
}
