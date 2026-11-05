/* Interrupt rows of the GNU SH-2E gate of exact JK08A Rolling Launch schema 6.
 *
 * The scenarios come from rolling_launch_rows.py. Each scenario runs one
 * engine pass at SR.I = 0 through invoke_regs. A request of the simulator
 * interrupt hook enters irq_rolling_handler inside one pass; the handler runs
 * the ignition publisher with the wide S and P of the scenario at SR.I = 8,
 * as the crank-tooth interrupt does, and records the base record and the
 * extension that the publication observes and leaves. The handler stores
 * its return marker immediately before RTE. Every scenario prints its
 * observations, and verify_rolling_launch.py compares them with the model.
 * The harness checks r8..r14, the stack pointer, GBR and the SR.I and SR.S
 * bits of every pass and of the publication. */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "rolling_launch_irq_rows.h"

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))

#define TEST_RAM_BASE 0x01000000U

#define SELECTOR_STATE 0xffff5d00U
#define RL_STATE 0xffff5d40U
#define RL_STATE_SIZE 44U
#define RL_EXTENSION 0xffff6100U
#define RL_EXTENSION_SIZE 32U
/* RL_CONFIG and RL_TABLE come from verify_rolling_launch.harness_definitions. */

#define SPEED 0xffff113cU
#define RPM 0xffff11bcU
#define SPEED_RAW 0xffff3b3dU
#define SPEED_AGE 0xffff3b38U
#define HCAN1_STATE 0xffff4195U
#define PORT_STATE 0xffff4185U
#define BUTTON_CODE 0xffff2a85U
#define ASCD_STATUS 0xffff41aeU
#define PEDAL 0xffff2672U
#define COOLANT 0xffff1077U
#define APC_MODE_SNAPSHOT 0xffff24c9U

#define RL_ENGINE 0x000d38e4U
#define IGNITION_PUBLISHER 0x000d6540U

#define SR_I_S 0x000000f2U
#define SR_ENGINE 0x00000000U
#define SR_PUBLISHER 0x00000080U
#define IRQ_RETURNED 0x52455445U

extern uint32_t invoke_regs(uint32_t entry, uint32_t *regs);
extern void irq_rolling_handler(void);
void irq_rolling_publish(void);

volatile uint32_t irq_vectors[256] __attribute__((aligned(1024)));
volatile uint32_t irq_rolling_returned;
static volatile uint32_t irq_hits, irq_r4, irq_r5, irq_sr, irq_saved;
static uint8_t seen[RL_STATE_SIZE + RL_EXTENSION_SIZE];
static uint8_t published[RL_STATE_SIZE + RL_EXTENSION_SIZE];
static const struct irq_scenario *current;
static uint32_t regs[16], irq_regs[16];

static volatile uint8_t *ram_pointer(uint32_t original)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (original & 0xffffU));
}

static volatile uint8_t *rom_pointer(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)address;
}

static void write_bytes(volatile uint8_t *target, const uint8_t *source, size_t size)
{
    size_t index;

    for (index = 0; index < size; ++index)
        target[index] = source[index];
}

static void read_records(uint8_t *target)
{
    size_t index;

    for (index = 0; index < RL_STATE_SIZE; ++index)
        target[index] = ram_pointer(RL_STATE)[index];
    for (index = 0; index < RL_EXTENSION_SIZE; ++index)
        target[RL_STATE_SIZE + index] = ram_pointer(RL_EXTENSION)[index];
}

static void write_u16(volatile uint8_t *target, uint16_t value)
{
    target[0] = (uint8_t)(value >> 8);
    target[1] = (uint8_t)value;
}

static void load_inputs(const struct rl_inputs *in)
{
    write_bytes(ram_pointer(SELECTOR_STATE), in->selector, sizeof(in->selector));
    ram_pointer(ASCD_STATUS)[0] = in->ascd;
    ram_pointer(BUTTON_CODE)[0] = in->button;
    ram_pointer(SPEED_AGE)[0] = in->age;
    ram_pointer(HCAN1_STATE)[0] = in->hcan;
    ram_pointer(PORT_STATE)[0] = in->port;
    ram_pointer(COOLANT)[0] = in->coolant;
    write_u16(ram_pointer(SPEED), in->speed);
    ram_pointer(SPEED_RAW)[0] = (uint8_t)(in->wire >> 8);
    ram_pointer(SPEED_RAW + 1U)[0] = (uint8_t)in->wire;
    write_u16(ram_pointer(RPM), in->rpm);
    write_u16(ram_pointer(PEDAL), in->pedal);
}

static uint32_t distinct(size_t index)
{
    return 0xc0de0000U | (uint32_t)(index << 8) | (uint32_t)index;
}

/* Called by irq_rolling_handler at SR.I = 8 with the registers of the
   interrupted pass saved. */
void irq_rolling_publish(void)
{
    size_t index;
    int preserved = 1;

    ++irq_hits;
    read_records(seen);
    for (index = 1; index < 15U; ++index)
        irq_regs[index] = distinct(index) ^ 0x00ff00ffU;
    irq_regs[3] = 0;
    irq_regs[4] = current->stock;
    irq_regs[5] = current->effective;
    irq_regs[15] = SR_PUBLISHER;
    (void)invoke_regs(IGNITION_PUBLISHER, irq_regs);
    for (index = 8; index < 15U; ++index)
        if (irq_regs[index] != (distinct(index) ^ 0x00ff00ffU))
            preserved = 0;
    irq_r4 = irq_regs[4];
    irq_r5 = irq_regs[5];
    irq_sr = irq_regs[15];
    irq_saved = (uint32_t)preserved;
    read_records(published);
}

static void print_bytes(const char *name, const uint8_t *bytes, size_t size)
{
    size_t index;

    printf(" %s=", name);
    for (index = 0; index < size; ++index)
        printf("%02x", (unsigned int)bytes[index]);
}

static int run_scenario(const struct irq_scenario *scenario)
{
    uint8_t final[RL_STATE_SIZE + RL_EXTENSION_SIZE];
    uint32_t sp_before, sp_after, gbr_before, gbr_after;
    size_t index;
    int preserved = 1;

    current = scenario;
    write_bytes(ram_pointer(RL_STATE), scenario->base, RL_STATE_SIZE);
    write_bytes(ram_pointer(RL_EXTENSION), scenario->ext, RL_EXTENSION_SIZE);
    load_inputs(&scenario->in);
    ram_pointer(APC_MODE_SNAPSHOT)[0] = 0;
    irq_hits = irq_r4 = irq_r5 = irq_sr = irq_saved = 0;
    irq_rolling_returned = 0;
    for (index = 0; index < sizeof(seen); ++index)
        seen[index] = published[index] = 0;
    for (index = 1; index < 15U; ++index)
        regs[index] = distinct(index);
    regs[3] = regs[4] = regs[5] = 0;
    regs[15] = SR_ENGINE;
    __asm__ volatile ("mov r15,%0" : "=r" (sp_before) : : "memory");
    __asm__ volatile ("stc gbr,%0" : "=r" (gbr_before) : : "memory");
    (void)invoke_regs(RL_ENGINE, regs);
    __asm__ volatile ("mov r15,%0" : "=r" (sp_after) : : "memory");
    __asm__ volatile ("stc gbr,%0" : "=r" (gbr_after) : : "memory");
    for (index = 8; index < 15U; ++index)
        if (regs[index] != distinct(index))
            preserved = 0;
    read_records(final);
    printf("VQ_SH_ELF_ROLLING_IRQ case=%s hits=%lu returned=%08lx preserved=%d sp=%d gbr=%d "
           "sr=%08lx irq_preserved=%lu irq_r4=%08lx irq_r5=%08lx irq_sr=%08lx",
           scenario->name, (unsigned long)irq_hits, (unsigned long)irq_rolling_returned,
           preserved, sp_after == sp_before, gbr_after == gbr_before,
           (unsigned long)(regs[15] & SR_I_S), (unsigned long)irq_saved,
           (unsigned long)irq_r4, (unsigned long)irq_r5, (unsigned long)(irq_sr & SR_I_S));
    print_bytes("seen", seen, sizeof(seen));
    print_bytes("published", published, sizeof(published));
    print_bytes("final", final, sizeof(final));
    printf("\n");
    return preserved && sp_after == sp_before && gbr_after == gbr_before;
}

int main(void)
{
    size_t index;

    for (index = 0; index < ARRAY_SIZE(irq_vectors); ++index)
        irq_vectors[index] = (uint32_t)(uintptr_t)irq_rolling_handler;
    __asm__ volatile ("ldc %0,vbr\n\tnop" : : "r" (irq_vectors) : "memory");
    write_bytes(rom_pointer(RL_CONFIG), rl_config, sizeof(rl_config));
    write_bytes(rom_pointer(RL_TABLE), rl_table, sizeof(rl_table));
    for (index = 0; index < ARRAY_SIZE(irq_scenarios); ++index)
        if (!run_scenario(&irq_scenarios[index]))
            return 1;
    printf("VQ_SH_ELF_ROLLING_IRQ status=DONE scenarios=%lu\n",
           (unsigned long)ARRAY_SIZE(irq_scenarios));
    return 0;
}
