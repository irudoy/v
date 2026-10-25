/* Natural bank-pulse stage inputs and complete raw state; no expected outputs. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define ARRAY_SIZE(value) (sizeof(value)/sizeof((value)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr,fifth; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];
    uint32_t sr_before;
};
#include "bank-pulse-stage-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete independent context ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];
static uint8_t calibration_before[BANK_PULSE_STAGE_CALIBRATION_SIZE];

static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer;size_t index;
    for (index=0;index<size;++index) printf("%02x",(unsigned)data[index]);
}
static void rle(const uint8_t *data,size_t size)
{
    size_t start=0;
    while (start<size) {
        size_t end=start+1U;
        while (end<size && data[end]==data[start]) ++end;
        printf("%s%lu:%02x",start ? "," : "",(unsigned long)(end-start),(unsigned)data[start]);
        start=end;
    }
}
static void put_word(uint32_t offset,uint32_t value)
{ *(volatile uint16_t *)(uintptr_t)(RAM_BASE+offset)=(uint16_t)value; }
static void put_byte(uint32_t offset,uint32_t value)
{ *(volatile uint8_t *)(uintptr_t)(RAM_BASE+offset)=(uint8_t)value; }
static void snapshot_calibrations(void)
{
    unsigned index,offset=0;
    for (index=0;index<ARRAY_SIZE(bank_pulse_stage_calibration_starts);++index) {
        unsigned size=bank_pulse_stage_calibration_sizes[index];
        memcpy(calibration_before+offset,(const void *)(uintptr_t)bank_pulse_stage_calibration_starts[index],size);
        offset+=size;
    }
}
static void print_calibrations(void)
{
    unsigned index;
    for (index=0;index<ARRAY_SIZE(bank_pulse_stage_calibration_starts);++index)
        hex((const void *)(uintptr_t)bank_pulse_stage_calibration_starts[index],bank_pulse_stage_calibration_sizes[index]);
}
static int prepare(const struct path_case *input)
{
    unsigned index,offset=0;
    if (input->kind>1U) return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    if (input->kind==0U) {
        if (input->entry!=0x4e974U || input->source_flags>255U || input->cap_flags>255U
                || input->output_flags>255U || input->bfs>65535U || input->alternate_bfs>65535U
                || input->speed>65535U || input->cap_floor>65535U || input->multiplier>65535U
                || input->transient_raw>65535U || input->gain>65535U || input->bank0>65535U
                || input->bank1>65535U || input->pulse_floor>65535U) return 0;
        put_byte(0x245dU,input->source_flags);put_byte(0x24d2U,input->cap_flags);
        put_byte(0x24a1U,input->output_flags);put_word(0x1024U,input->bfs);
        put_word(0x123eU,input->alternate_bfs);put_word(0x11bcU,input->speed);
        put_word(0x34f6U,input->cap_floor);put_word(0x22e6U,input->multiplier);
        put_word(0x2300U,input->transient_raw);put_word(0x165eU,input->gain);
        put_word(0x40b6U,input->bank0);put_word(0x40b8U,input->bank1);
    } else {
        if (input->entry!=0x4eba2U || input->channel>5U || (input->raw_r4&255U)!=input->channel
                || input->mask>255U || input->flag>255U || input->multiplier>255U
                || input->even_base>65535U || input->odd_base>65535U || input->additive>65535U
                || input->subtractive>65535U || input->opening>65535U || input->a>65535U
                || input->c>65535U || input->b>65535U || input->d>65535U) return 0;
        put_byte(0x22e0U,input->mask);put_word(0x191cU,input->even_base);
        put_word(0x191eU,input->odd_base);put_word(0x2436U,input->opening);
        put_word(0x1396U+input->channel*2U,input->additive);
        put_word(0x1466U+input->channel*2U,input->subtractive);
    }
    for (index=0;index<ARRAY_SIZE(bank_pulse_stage_calibration_starts);++index) {
        unsigned size=bank_pulse_stage_calibration_sizes[index];
        memcpy((void *)(uintptr_t)bank_pulse_stage_calibration_starts[index],input->calibration+offset,size);
        offset+=size;
    }
    return 1;
}
static int observe(size_t index)
{
    const struct path_case *input=&bank_pulse_stage_cases[index];
    struct context context=input->context,initial;struct observation observation;
    if (!prepare(input)) return 0;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    snapshot_calibrations();memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-bank-pulse-stage-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->kind,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
    printf("\",\"observation\":\"");hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\"");rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\"");print_calibrations();printf("\"}\n");
    return 1;
}
int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(bank_pulse_stage_cases);++index) if (!observe(index)) return 1;
    printf("VQ_SH_ELF_BANK_PULSE_STAGES status=PASS region=%s cases=%lu\n",
           BANK_PULSE_STAGE_REGION,(unsigned long)ARRAY_SIZE(bank_pulse_stage_cases));
    return 0;
}
