#include <stdint.h>
#include <stdio.h>

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(BFS_NEWEST) \
    || !defined(BFS_CURRENT) || !defined(BFS_PREVIOUS) || !defined(LIVE_LOAD) \
    || !defined(SNAPSHOT_LOAD) || !defined(COPY_SIZE)
#error "the verifier defines the BFS words and both snapshot endpoints"
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U
#define MACL_SEED 0x89abcdefU
#define WINDOW_START 0xffff1020U
#define WINDOW_SIZE 0x50U

/* The slice uses the normalization helper's SP+0 return continuation. */
extern uint32_t stock_invoke_normalized_load(uint32_t, uint32_t, uint32_t, uint32_t *);

struct snapshot_case {
    const char *name;
    unsigned pattern;
    uint16_t current, newest;
};
static const struct snapshot_case snapshot_cases[] = {
    {"zero-block", 0, 0, 0},
    {"full-block", 1, 0xffff, 0xffff},
    {"ascending-bytes", 2, 0x1234, 0x5678},
    {"descending-bytes", 3, 0x8000, 0x7fff},
    {"alternating-sign-bits", 4, 0x7fff, 0x8000},
    {"independent-longwords", 5, 1, 65534},
    {"first-last-boundaries", 6, 65534, 1},
    {"unsigned-load-byte", 7, 0xa55a, 0x5aa5},
};

struct sequence_case { const char *name; uint16_t current, newest; uint8_t live; };
static const struct sequence_case sequence_cases[] = {
    {"successive-first", 0x1234, 1, 0},
    {"successive-high-word", 1, 0x8000, 128},
    {"successive-last-word", 0x8000, 0xffff, 255},
};

static volatile uint8_t *ram_pointer(uint32_t original)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (original & 0xffffU));
}

static int fail_value(const char *name, const char *field, uint32_t actual, uint32_t expected)
{
    printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s field=%s actual=%08lx expected=%08lx\n",
           name, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static void fill_window(void)
{
    size_t index;
    for (index = 0; index < WINDOW_SIZE; ++index)
        ram_pointer(WINDOW_START)[index] = (uint8_t)(index * 19U + 23U);
}

static void fill_source(unsigned pattern)
{
    size_t index;
    for (index = 0; index < COPY_SIZE; ++index) {
        uint8_t value;
        switch (pattern) {
        case 0: value = 0; break;
        case 1: value = 255; break;
        case 2: value = (uint8_t)index; break;
        case 3: value = (uint8_t)(255U - index); break;
        case 4: value = (index & 1U) ? 0x7f : 0x80; break;
        case 5: value = (uint8_t)(index * 37U + 11U); break;
        case 6: value = index == 0 ? 0 : index + 1U == COPY_SIZE ? 255 : 23; break;
        default: value = (uint8_t)(128U + index); break;
        }
        ram_pointer(LIVE_LOAD)[index] = value;
    }
}

static int invoke_and_check(const char *name, uint16_t old_current, uint16_t newest, uint32_t macl)
{
    uint8_t before[WINDOW_SIZE];
    uint32_t state[6];
    size_t index;
    for (index = 0; index < WINDOW_SIZE; ++index)
        before[index] = ram_pointer(WINDOW_START)[index];
    stock_invoke_normalized_load(REGION_ENTRY, 0xa55a, macl, state);
    if (*(volatile uint16_t *)ram_pointer(BFS_PREVIOUS) != old_current)
        return fail_value(name, "previous-bfs", *(volatile uint16_t *)ram_pointer(BFS_PREVIOUS), old_current);
    if (*(volatile uint16_t *)ram_pointer(BFS_CURRENT) != newest)
        return fail_value(name, "current-bfs", *(volatile uint16_t *)ram_pointer(BFS_CURRENT), newest);
    for (index = 0; index < COPY_SIZE; ++index) {
        uint8_t expected = before[LIVE_LOAD - WINDOW_START + index];
        if (ram_pointer(SNAPSHOT_LOAD)[index] != expected)
            return fail_value(name, "snapshot-byte", ram_pointer(SNAPSHOT_LOAD)[index], expected);
    }
    if (state[0] != macl || state[1] != 0x10203040U || state[2] != 0x13579bdfU
        || state[3] != 0x2468ace0U || state[4] != 0x13572468U || state[5] != 0x00021ce0U)
        return fail_value(name, "preserved-registers-macl-gbr-r11", 1, 0);
    for (index = 0; index < WINDOW_SIZE; ++index) {
        uint32_t address = WINDOW_START + (uint32_t)index;
        if ((address >= BFS_CURRENT && address < BFS_CURRENT + 2U)
            || (address >= BFS_PREVIOUS && address < BFS_PREVIOUS + 2U)
            || (address >= SNAPSHOT_LOAD && address < SNAPSHOT_LOAD + COPY_SIZE))
            continue;
        if (ram_pointer(address)[0] != before[index])
            return fail_value(name, "read-only-newest-source-or-neighbor", address, 0);
    }
    return 1;
}

static int run_snapshot(const struct snapshot_case *test, uint32_t macl)
{
    fill_window();
    fill_source(test->pattern);
    *(volatile uint16_t *)ram_pointer(BFS_CURRENT) = test->current;
    *(volatile uint16_t *)ram_pointer(BFS_NEWEST) = test->newest;
    return invoke_and_check(test->name, test->current, test->newest, macl);
}

static int run_sequence(void)
{
    size_t index;
    fill_window();
    *(volatile uint16_t *)ram_pointer(BFS_CURRENT) = 0x1234;
    for (index = 0; index < ARRAY_SIZE(sequence_cases); ++index) {
        const struct sequence_case *test = sequence_cases + index;
        fill_source(5);
        ram_pointer(LIVE_LOAD)[0] = test->live;
        *(volatile uint16_t *)ram_pointer(BFS_NEWEST) = test->newest;
        if (!invoke_and_check(test->name, test->current, test->newest, MACL_SEED))
            return 0;
    }
    return 1;
}

int main(void)
{
    size_t index;
    for (index = 0; index < ARRAY_SIZE(snapshot_cases); ++index)
        if (!run_snapshot(snapshot_cases + index, MACL_SEED ^ (uint32_t)index))
            return 1;
    if (!run_sequence())
        return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY,
           (unsigned long)(ARRAY_SIZE(snapshot_cases) + ARRAY_SIZE(sequence_cases)));
    return 0;
}
