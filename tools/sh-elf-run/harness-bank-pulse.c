/* Natural bank base-pulse inputs with complete state observations. */
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
struct path_case {
    uint32_t entry,raw_r4,s,l,e,precursor,additive,offset,c0,c1,f1,f2,initial_t,variant;
    struct context context;
};
#include "bank-pulse-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete independent context ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];
static uint8_t calibration_before[26];
static const uint32_t calibration_starts[]={0x893dU,0x8940U,0x4ebe2U,0x4ebe4U,0x4ec00U,0x4ec04U,0x4ec08U,0x4ec18U,0x4ec1cU};
static const uint32_t calibration_sizes[]={1U,1U,2U,2U,4U,4U,4U,4U,4U};

static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer; size_t index;
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
static void snapshot_calibrations(void)
{
    unsigned index,offset=0;
    for (index=0;index<ARRAY_SIZE(calibration_starts);++index) {
        memcpy(calibration_before+offset,(const void *)(uintptr_t)calibration_starts[index],calibration_sizes[index]);
        offset+=calibration_sizes[index];
    }
}
static void print_calibrations(void)
{
    unsigned index;
    for (index=0;index<ARRAY_SIZE(calibration_starts);++index)
        hex((const void *)(uintptr_t)calibration_starts[index],calibration_sizes[index]);
}
static int prepare(const struct path_case *input)
{
    uint32_t bank=input->raw_r4&255U,shift=bank*2U;
    if (bank>1U || input->entry!=0x4ead4U || input->f1>255U || input->f2>255U
            || input->s>65535U || input->l>65535U || input->e>65535U
            || input->precursor>65535U || input->additive>65535U || input->offset>65535U
            || input->c0>65535U || input->c1>65535U) return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    put_word(0x22dcU+shift,input->s); put_word(0x2302U+shift,input->l);
    put_word(0x2a24U+shift,input->e); put_word(0x18c0U+shift,input->precursor);
    put_word(0x2310U+shift,input->offset); put_word(0x2436U,input->additive);
    put_word(0x22e6U,input->c0); put_word(0x22e8U,input->c1);
    *(volatile uint8_t *)(uintptr_t)0x893dU=(uint8_t)input->f1;
    *(volatile uint8_t *)(uintptr_t)0x8940U=(uint8_t)input->f2;
    return 1;
}
static int observe(size_t index)
{
    const struct path_case *input=&bank_pulse_cases[index];
    struct context context=input->context,initial; struct observation observation;
    if (!prepare(input)) return 0;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    snapshot_calibrations();
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-bank-pulse-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,0UL,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context,sizeof(context));
    printf("\",\"observation\":\""); hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\""); rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\""); rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\""); hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\""); print_calibrations();
    printf("\"}\n");
    return 1;
}
int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(bank_pulse_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_BANK_PULSE status=PASS region=%s cases=%lu\n",
           BANK_PULSE_REGION,(unsigned long)ARRAY_SIZE(bank_pulse_cases));
    return 0;
}
