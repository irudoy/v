#include <stdint.h>
#include <stdio.h>

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(PRIMARY_ENTRY) \
    || !defined(PRIMARY_BASE) || !defined(AGGREGATE) || !defined(PRIMARY_SPEED) \
    || !defined(ALTERNATE_SPEED) || !defined(SPEED_FLAGS) || !defined(QUARTER_BFS) \
    || !defined(COMPENSATION) || !defined(COMPENSATED_BFS) || !defined(CONTROL_BYTE) \
    || !defined(K_ADDRESS) || !defined(FACTOR_ADDRESS) || !defined(E_ADDRESS) \
    || !defined(DIVIDER_ENTRY) || !defined(REMAINDER_ENTRY) || !defined(FAULT_ADDRESS)
#error "the verifier defines the primary BFS input, cache, coefficients, and unsigned helpers"
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U
extern uint32_t stock_invoke_bfs_base(uint32_t, const void *, uint32_t *);
extern uint32_t stock_invoke_r1(uint32_t, uint32_t, uint32_t);

struct primary_case {
    const char *name;
    uint8_t mode, speed;
    uint16_t rpm, alternate;
    uint8_t flags;
    uint32_t aggregate;
    uint16_t k;
    uint8_t factor, e, compensation, control;
    uint32_t quarter;
    uint16_t output;
};

struct consumer_case {
    const char *name;
    uint32_t cached;
    uint8_t compensation;
    uint16_t output;
    uint32_t quotient, product;
};

struct remainder_case {
    const char *name;
    uint32_t numerator, denominator, result, fault;
};

static const struct primary_case primary_cases[] = {
    {"primary-ordinary", 0, 128, 64, 65535, 0, 1000, 26806, 109, 3, 128, 165, 8311, 8311},
    {"aggregate-00000000", 0, 128, 64, 65535, 0, 0, 26806, 109, 3, 128, 165, 0, 0},
    {"aggregate-00000001", 0, 128, 64, 65535, 0, 1, 26806, 109, 3, 128, 165, 8, 8},
    {"aggregate-00000002", 0, 128, 64, 65535, 0, 2, 26806, 109, 3, 128, 165, 16, 16},
    {"aggregate-000000ff", 0, 128, 64, 65535, 0, 255, 26806, 109, 3, 128, 165, 2119, 2119},
    {"aggregate-00000100", 0, 128, 64, 65535, 0, 256, 26806, 109, 3, 128, 165, 2127, 2127},
    {"aggregate-0000ffff", 0, 128, 64, 65535, 0, 65535, 26806, 109, 3, 128, 165, 65535, 65535},
    {"aggregate-00010000", 0, 128, 64, 65535, 0, 65536, 26806, 109, 3, 128, 165, 65535, 65535},
    {"aggregate-00010001", 0, 128, 64, 65535, 0, 65537, 26806, 109, 3, 128, 165, 65535, 65535},
    {"aggregate-00ffffff", 0, 128, 64, 65535, 0, 16777215, 26806, 109, 3, 128, 165, 65535, 65535},
    {"aggregate-02000000", 0, 128, 64, 65535, 0, 33554432, 26806, 109, 3, 128, 165, 65535, 65535},
    {"aggregate-02017ffc", 0, 128, 64, 65535, 0, 33652732, 26806, 109, 3, 128, 165, 65535, 65535},
    {"aggregate-02017ffd", 0, 128, 64, 65535, 0, 33652733, 26806, 109, 3, 128, 165, 65535, 65535},
    {"aggregate-7fffffff", 0, 128, 64, 65535, 0, 2147483647, 26806, 109, 3, 128, 165, 65535, 65535},
    {"aggregate-80000000", 0, 128, 64, 65535, 0, 2147483648, 26806, 109, 3, 128, 165, 0, 0},
    {"aggregate-ffffffff", 0, 128, 64, 65535, 0, 4294967295, 26806, 109, 3, 128, 165, 0, 0},
    {"normal-rpm-0", 0, 128, 0, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"alternate-rpm-0", 0, 128, 64, 0, 32, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"normal-rpm-1", 0, 128, 1, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"alternate-rpm-1", 0, 128, 64, 1, 32, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"normal-rpm-63", 0, 128, 63, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"alternate-rpm-63", 0, 128, 64, 63, 32, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"normal-rpm-64", 0, 128, 64, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"alternate-rpm-64", 0, 128, 64, 64, 32, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"normal-rpm-65", 0, 128, 65, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"alternate-rpm-65", 0, 128, 64, 65, 32, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"normal-rpm-127", 0, 128, 127, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"alternate-rpm-127", 0, 128, 64, 127, 32, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"normal-rpm-128", 0, 128, 128, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"alternate-rpm-128", 0, 128, 64, 128, 32, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"normal-rpm-21844", 0, 128, 21844, 65535, 0, 123456, 26806, 109, 3, 128, 165, 3006, 3006},
    {"alternate-rpm-21844", 0, 128, 64, 21844, 32, 123456, 26806, 109, 3, 128, 165, 3006, 3006},
    {"normal-rpm-21845", 0, 128, 21845, 65535, 0, 123456, 26806, 109, 3, 128, 165, 3006, 3006},
    {"alternate-rpm-21845", 0, 128, 64, 21845, 32, 123456, 26806, 109, 3, 128, 165, 3006, 3006},
    {"normal-rpm-21846", 0, 128, 21846, 65535, 0, 123456, 26806, 109, 3, 128, 165, 3005, 3005},
    {"alternate-rpm-21846", 0, 128, 64, 21846, 32, 123456, 26806, 109, 3, 128, 165, 3005, 3005},
    {"normal-rpm-65535", 0, 128, 65535, 65535, 0, 123456, 26806, 109, 3, 128, 165, 1001, 1001},
    {"alternate-rpm-65535", 0, 128, 64, 65535, 32, 123456, 26806, 109, 3, 128, 165, 1001, 1001},
    {"byte-speed-0", 64, 0, 64, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"byte-speed-1", 64, 1, 64, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"byte-speed-7", 64, 7, 64, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"byte-speed-8", 64, 8, 64, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"byte-speed-9", 64, 9, 64, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"byte-speed-31", 64, 31, 64, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"byte-speed-32", 64, 32, 64, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"byte-speed-33", 64, 33, 64, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"byte-speed-127", 64, 127, 64, 65535, 0, 123456, 26806, 109, 3, 128, 165, 64635, 64635},
    {"byte-speed-128", 64, 128, 64, 65535, 0, 123456, 26806, 109, 3, 128, 165, 64130, 64130},
    {"byte-speed-255", 64, 255, 64, 65535, 0, 123456, 26806, 109, 3, 128, 165, 32191, 32191},
    {"unrelated-mode-bits", 0, 128, 128, 1024, 223, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"selected-alternate-with-other-bits", 0, 128, 128, 1024, 255, 123456, 26806, 109, 3, 128, 165, 64130, 64130},
    {"k-0", 0, 128, 65535, 65535, 0, 305419896, 0, 109, 3, 128, 165, 0, 0},
    {"k-1", 0, 128, 65535, 65535, 0, 305419896, 1, 109, 3, 128, 165, 92, 92},
    {"k-255", 0, 128, 65535, 65535, 0, 305419896, 255, 109, 3, 128, 165, 23582, 23582},
    {"k-256", 0, 128, 65535, 65535, 0, 305419896, 256, 109, 3, 128, 165, 23674, 23674},
    {"k-32768", 0, 128, 65535, 65535, 0, 305419896, 32768, 109, 3, 128, 165, 65535, 65535},
    {"k-65535", 0, 128, 65535, 65535, 0, 305419896, 65535, 109, 3, 128, 165, 65535, 65535},
    {"factor-0", 0, 128, 65535, 65535, 0, 305419896, 26806, 0, 3, 128, 165, 0, 0},
    {"factor-1", 0, 128, 65535, 65535, 0, 305419896, 26806, 1, 3, 128, 165, 22743, 22743},
    {"factor-128", 0, 128, 65535, 65535, 0, 305419896, 26806, 128, 3, 128, 165, 65535, 65535},
    {"factor-255", 0, 128, 65535, 65535, 0, 305419896, 26806, 255, 3, 128, 165, 65535, 65535},
    {"denominator-byte-0", 0, 128, 65535, 65535, 0, 123456, 26806, 109, 0, 128, 165, 65535, 65535},
    {"denominator-byte-1", 0, 128, 65535, 65535, 0, 123456, 26806, 109, 1, 128, 165, 3006, 3006},
    {"denominator-byte-255", 0, 128, 65535, 65535, 0, 123456, 26806, 109, 255, 128, 165, 11, 11},
    {"zero-aggregate-zero-denominator", 0, 128, 64, 65535, 0, 0, 26806, 109, 0, 128, 165, 0, 0},
    {"zero-numerator-zero-denominator", 0, 128, 64, 65535, 0, 1, 0, 109, 0, 128, 165, 65535, 65535},
    {"signed-negative-zero-denominator", 0, 128, 64, 65535, 0, 4294967295, 26806, 109, 0, 128, 165, 0, 0},
    {"fixed-cap-468478", 0, 128, 64, 65535, 0, 468478, 256, 1, 1, 128, 165, 1023, 1023},
    {"exact-fixed-cap-468478", 0, 128, 64, 65535, 0, 468478, 16384, 1, 1, 128, 165, 65500, 65500},
    {"fixed-cap-468479", 0, 128, 64, 65535, 0, 468479, 256, 1, 1, 128, 165, 1023, 1023},
    {"exact-fixed-cap-468479", 0, 128, 64, 65535, 0, 468479, 16384, 1, 1, 128, 165, 65500, 65500},
    {"fixed-cap-468480", 0, 128, 64, 65535, 0, 468480, 256, 1, 1, 128, 165, 1023, 1023},
    {"exact-fixed-cap-468480", 0, 128, 64, 65535, 0, 468480, 16384, 1, 1, 128, 165, 65501, 65501},
    {"fixed-cap-468728", 0, 128, 64, 65535, 0, 468728, 256, 1, 1, 128, 165, 1023, 1023},
    {"exact-fixed-cap-468728", 0, 128, 64, 65535, 0, 468728, 16384, 1, 1, 128, 165, 65535, 65535},
    {"fixed-cap-468729", 0, 128, 64, 65535, 0, 468729, 256, 1, 1, 128, 165, 1023, 1023},
    {"exact-fixed-cap-468729", 0, 128, 64, 65535, 0, 468729, 16384, 1, 1, 128, 165, 65535, 65535},
    {"fixed-cap-468730", 0, 128, 64, 65535, 0, 468730, 256, 1, 1, 128, 165, 1023, 1023},
    {"exact-fixed-cap-468730", 0, 128, 64, 65535, 0, 468730, 16384, 1, 1, 128, 165, 65535, 65535},
    {"fixed-cap-468735", 0, 128, 64, 65535, 0, 468735, 256, 1, 1, 128, 165, 1023, 1023},
    {"exact-fixed-cap-468735", 0, 128, 64, 65535, 0, 468735, 16384, 1, 1, 128, 165, 65535, 65535},
    {"fixed-cap-468736", 0, 128, 64, 65535, 0, 468736, 256, 1, 1, 128, 165, 1024, 1024},
    {"exact-fixed-cap-468736", 0, 128, 64, 65535, 0, 468736, 16384, 1, 1, 128, 165, 65535, 65535},
    {"fixed-cap-468737", 0, 128, 64, 65535, 0, 468737, 256, 1, 1, 128, 165, 1024, 1024},
    {"exact-fixed-cap-468737", 0, 128, 64, 65535, 0, 468737, 16384, 1, 1, 128, 165, 65535, 65535},
    {"compensation-0", 0, 128, 128, 65535, 0, 123456, 26806, 109, 3, 0, 165, 65535, 0},
    {"compensation-1", 0, 128, 128, 65535, 0, 123456, 26806, 109, 3, 1, 165, 65535, 511},
    {"compensation-127", 0, 128, 128, 65535, 0, 123456, 26806, 109, 3, 127, 165, 65535, 65023},
    {"compensation-128", 0, 128, 128, 65535, 0, 123456, 26806, 109, 3, 128, 165, 65535, 65535},
    {"compensation-129", 0, 128, 128, 65535, 0, 123456, 26806, 109, 3, 129, 165, 65535, 65535},
    {"compensation-255", 0, 128, 128, 65535, 0, 123456, 26806, 109, 3, 255, 165, 65535, 65535},
    {"wide-multiplier-003fffff", 0, 128, 65535, 65535, 0, 4194303, 65535, 255, 255, 128, 165, 2290, 2290},
    {"wide-multiplier-007fffff", 0, 128, 65535, 65535, 0, 8388607, 65535, 255, 255, 128, 165, 4581, 4581},
    {"wide-multiplier-00ffffff", 0, 128, 65535, 65535, 0, 16777215, 65535, 255, 255, 128, 165, 9162, 9162},
    {"wide-multiplier-01000000", 0, 128, 65535, 65535, 0, 16777216, 65535, 255, 255, 128, 165, 9163, 9163},
    {"wide-multiplier-01000001", 0, 128, 65535, 65535, 0, 16777217, 65535, 255, 255, 128, 165, 9163, 9163},
    {"wide-multiplier-12345678", 0, 128, 65535, 65535, 0, 305419896, 65535, 255, 255, 128, 165, 1223, 1223},
    {"wide-multiplier-7fffffff", 0, 128, 65535, 65535, 0, 2147483647, 65535, 255, 255, 128, 165, 4581, 4581},
};

static const struct consumer_case consumer_cases[] = {
    {"consumer-00000000-0", 0, 0, 0, 0, 0},
    {"consumer-00000000-255", 0, 255, 0, 0, 0},
    {"consumer-00000001-127", 1, 127, 0, 0, 127},
    {"consumer-00000001-128", 1, 128, 1, 1, 128},
    {"consumer-00000001-255", 1, 255, 1, 1, 255},
    {"consumer-0000007f-1", 127, 1, 0, 0, 127},
    {"consumer-00000080-1", 128, 1, 1, 1, 128},
    {"consumer-00000081-1", 129, 1, 1, 1, 129},
    {"consumer-00007fff-255", 32767, 255, 65278, 65278, 8355585},
    {"consumer-00008000-255", 32768, 255, 65280, 65280, 8355840},
    {"consumer-0000ffff-128", 65535, 128, 65535, 65535, 8388480},
    {"consumer-0000ffff-255", 65535, 255, 65535, 130558, 16711425},
    {"consumer-00010000-128", 65536, 128, 65535, 65536, 8388608},
    {"consumer-7fffffff-2", 2147483647, 2, 65535, 33554431, 4294967294},
    {"consumer-80000000-2", 2147483648, 2, 0, 0, 0},
    {"consumer-ffffffff-255", 4294967295, 255, 65535, 33554430, 4294967041},
};

static const struct remainder_case remainder_cases[] = {
    {"remainder-00000000-00000001", 0, 1, 0, 3735928559},
    {"remainder-000000ff-00000001", 255, 1, 0, 3735928559},
    {"remainder-000000ff-00000002", 255, 2, 1, 3735928559},
    {"remainder-0000ffff-000000ff", 65535, 255, 0, 3735928559},
    {"remainder-0000feff-000000ff", 65279, 255, 254, 3735928559},
    {"remainder-0000ff00-000000ff", 65280, 255, 0, 3735928559},
    {"remainder-00010000-0000ffff", 65536, 65535, 1, 3735928559},
    {"remainder-ffffffff-0000ffff", 4294967295, 65535, 0, 3735928559},
    {"remainder-ffffffff-00010000", 4294967295, 65536, 65535, 3735928559},
    {"remainder-7fffffff-ffffffff", 2147483647, 4294967295, 2147483647, 3735928559},
    {"remainder-ffffffff-ffffffff", 4294967295, 4294967295, 0, 3735928559},
    {"remainder-0000007b-00000000", 123, 0, 0, 1102},
};

struct window { uint32_t start; size_t size; uint8_t before[0x70]; };
static struct window windows[] = {
    {0xffff1de0U, 0x70, {0}}, {0xffff1110U, 0x70, {0}},
    {0xffff11d0U, 0x20, {0}}, {0xffff2460U, 0x10, {0}},
    {0xffff24acU, 0x10, {0}}, {0xffff1058U, 0x18, {0}},
    {0xffff9810U, 0x10, {0}},
};

static volatile uint8_t *ram(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (address & 0xffffU));
}

static void set_word(uint32_t address, uint16_t value)
{
    *(volatile uint16_t *)ram(address) = value;
}

static void set_longword(uint32_t address, uint32_t value)
{
    *(volatile uint32_t *)ram(address) = value;
}

static int fail(const char *name, const char *field, uint32_t actual, uint32_t expected)
{
    printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s field=%s actual=%08lx expected=%08lx\n",
           name, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static void prepare(const struct primary_case *test)
{
    size_t w, byte;
    for (w = 0; w < ARRAY_SIZE(windows); ++w)
        for (byte = 0; byte < windows[w].size; ++byte)
            ram(windows[w].start)[byte] = (uint8_t)(29U * byte + 31U * w + 7U);
    set_longword(AGGREGATE, test->aggregate);
    set_longword(QUARTER_BFS, 0xdeadbeefU);
    set_word(PRIMARY_SPEED, test->rpm);
    set_word(ALTERNATE_SPEED, test->alternate);
    ram(SPEED_FLAGS)[0] = test->flags;
    ram(COMPENSATION)[0] = test->compensation;
    ram(CONTROL_BYTE)[0] = test->control;
    set_word(COMPENSATED_BFS, 0xa55a);
    set_longword(FAULT_ADDRESS, 0xdeadbeefU);
    *(volatile uint16_t *)(uintptr_t)K_ADDRESS = test->k;
    *(volatile uint8_t *)(uintptr_t)FACTOR_ADDRESS = test->factor;
    *(volatile uint8_t *)(uintptr_t)E_ADDRESS = test->e;
    for (w = 0; w < ARRAY_SIZE(windows); ++w)
        for (byte = 0; byte < windows[w].size; ++byte)
            windows[w].before[byte] = ram(windows[w].start)[byte];
}

static int preserved(const char *name, int primary, int fault)
{
    size_t w, byte;
    for (w = 0; w < ARRAY_SIZE(windows); ++w)
        for (byte = 0; byte < windows[w].size; ++byte) {
            uint32_t address = windows[w].start + (uint32_t)byte;
            if ((primary && address >= QUARTER_BFS && address - QUARTER_BFS < 4U)
                || (!fault && address >= COMPENSATED_BFS && address - COMPENSATED_BFS < 2U)
                || (fault && address >= FAULT_ADDRESS && address - FAULT_ADDRESS < 4U))
                continue;
            if (ram(address)[0] != windows[w].before[byte])
                return fail(name, "read-only-input-mode-cache-or-neighbor", address, 0);
        }
    return 1;
}

static int check(const struct primary_case *test, uint32_t result, const uint32_t *state,
                 uint32_t quotient, uint32_t product, int primary)
{
    const uint32_t expected[] = {
        product, quotient, 65535, test->control,
        (uint32_t)(uintptr_t)ram(PRIMARY_BASE), DIVIDER_ENTRY,
        (uint32_t)(uintptr_t)ram(SPEED_FLAGS - 1U),
    };
    size_t index;
    if (result != test->output || *(volatile uint16_t *)ram(COMPENSATED_BFS) != test->output)
        return fail(test->name, "returned-or-published-word", result, test->output);
    if (primary && *(volatile uint32_t *)ram(QUARTER_BFS) != test->quarter)
        return fail(test->name, "quarter-bfs-longword", *(volatile uint32_t *)ram(QUARTER_BFS), test->quarter);
    for (index = 0; index < ARRAY_SIZE(expected); ++index)
        if (state[index] != expected[index])
            return fail(test->name, "arithmetic-register-macl-gbr-or-divider", state[index], expected[index]);
    if (*(const volatile uint16_t *)(uintptr_t)K_ADDRESS != test->k
        || *(const volatile uint8_t *)(uintptr_t)FACTOR_ADDRESS != test->factor
        || *(const volatile uint8_t *)(uintptr_t)E_ADDRESS != test->e)
        return fail(test->name, "read-only-calibration", 1, 0);
    return preserved(test->name, primary, 0);
}

static uint32_t invoke(uint32_t entry, const struct primary_case *test, uint32_t cached, uint32_t *state)
{
    const uint32_t context[] = {
        test->mode, test->speed, cached, (uint32_t)(uintptr_t)ram(PRIMARY_BASE),
        (uint32_t)(uintptr_t)ram(SPEED_FLAGS - 1U), DIVIDER_ENTRY,
    };
    return stock_invoke_bfs_base(entry, context, state);
}

static int run_primary(const struct primary_case *test)
{
    uint32_t result, state[7], product = test->quarter * test->compensation;
    prepare(test);
    result = invoke(PRIMARY_ENTRY, test, 0x87654321U, state);
    return check(test, result, state, product >> 7, product, 1);
}

static int run_consumer(const struct consumer_case *test)
{
    struct primary_case context = primary_cases[0];
    uint32_t result, state[7];
    context.name = test->name;
    context.compensation = test->compensation;
    context.output = test->output;
    prepare(&context);
    result = invoke(REGION_ENTRY, &context, test->cached, state);
    return check(&context, result, state, test->quotient, test->product, 0);
}

static int run_remainder(const struct remainder_case *test)
{
    uint32_t result;
    prepare(primary_cases);
    result = stock_invoke_r1(REMAINDER_ENTRY, test->numerator, test->denominator);
    if (result != test->result || *(volatile uint32_t *)ram(FAULT_ADDRESS) != test->fault)
        return fail(test->name, "remainder-or-zero-fault", result, test->result);
    return preserved(test->name, 0, 1);
}

int main(void)
{
    size_t index, cases = 0;
    for (index = 0; index < ARRAY_SIZE(primary_cases); ++index) {
        if (!run_primary(primary_cases + index)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(consumer_cases); ++index) {
        if (!run_consumer(consumer_cases + index)) return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(remainder_cases); ++index) {
        if (!run_remainder(remainder_cases + index)) return 1;
        ++cases;
    }
    *(volatile uint16_t *)(uintptr_t)K_ADDRESS = 26806;
    *(volatile uint8_t *)(uintptr_t)FACTOR_ADDRESS = 109;
    *(volatile uint8_t *)(uintptr_t)E_ADDRESS = 3;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY,
           (unsigned long)cases);
    return 0;
}
