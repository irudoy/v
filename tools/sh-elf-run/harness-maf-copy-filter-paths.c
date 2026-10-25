/* Natural copy/filter inputs and complete independent state observations. */
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
struct path_case { uint32_t entry,kind,argument,input,previous,flags,coefficient,variant,sr; };
#include "maf-copy-filter-path-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete independent context ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
_Static_assert(sizeof(maf_copy_filter_stock_calibrations)==1U,"one declared coefficient byte");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];

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
static int prepare(const struct path_case *input)
{
    uint32_t bank=input->argument&255U,index;
    if (bank>1U || input->kind>1U) return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    for (index=0;index<2U;++index) {
        put_word(0x1054U+index*2U,input->kind==0U && index==bank ? input->input : 0x6c19U);
        put_word(0x1058U+index*2U,input->kind==1U && index==bank ? input->input : 0xa55aU);
        put_word(0x1df0U+index*2U,index==bank ? input->previous : 0x7abcU);
    }
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2461U)=(uint8_t)input->flags;
    memcpy((void *)(uintptr_t)0x870aU,maf_copy_filter_stock_calibrations,1U);
    *(volatile uint8_t *)(uintptr_t)0x870aU=(uint8_t)input->coefficient;
    return 1;
}
static int observe(size_t index)
{
    const struct path_case *input=&maf_copy_filter_cases[index];
    struct context context,initial; struct observation observation; unsigned reg;
    uint8_t coefficient_before;
    if (!prepare(input)) return 0;
    for (reg=0;reg<15U;++reg) context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.r[4]=input->argument;
    context.gbr=0x12344321U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    coefficient_before=*(volatile uint8_t *)(uintptr_t)0x870aU;
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-maf-copy-filter-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->kind,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context,sizeof(context));
    printf("\",\"observation\":\""); hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\""); rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\""); rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\""); hex(&coefficient_before,1U);
    printf("\",\"calibration_after\":\""); hex((const void *)(uintptr_t)0x870aU,1U);
    printf("\"}\n");
    return 1;
}
int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(maf_copy_filter_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_MAF_COPY_FILTER status=PASS region=%s cases=%lu\n",
           MAF_COPY_FILTER_REGION,(unsigned long)ARRAY_SIZE(maf_copy_filter_cases));
    return 0;
}
