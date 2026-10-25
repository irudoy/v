/* Explicit bounded normalization inputs and complete actual state observations. */
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
    uint32_t entry,kind,pattern,selected,coordinate,coefficient_coordinate,variant,sr;
};
#include "normalization-path-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"independent lookup fifth argument ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];
static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer; size_t index;
    for (index=0;index<size;++index) printf("%02x",(unsigned)data[index]);
}
static void rle(const uint8_t *bytes,size_t size)
{
    size_t start=0;
    while (start<size) {
        size_t end=start+1U;
        while (end<size && bytes[end]==bytes[start]) ++end;
        printf("%s%lu:%02x",start ? "," : "",(unsigned long)(end-start),(unsigned)bytes[start]);
        start=end;
    }
}
static uint8_t calibration_before[sizeof(normalization_stock_calibrations)];
static void table_words(uint32_t at,uint32_t value)
{
    unsigned index;
    for (index=0;index<16U;++index) *(volatile uint16_t *)(uintptr_t)(at+index*2U)=(uint16_t)value;
}
static void write_calibrations(const struct path_case *input)
{
    unsigned index;uint32_t selected=input->selected==1U ? 0x1459aU : 0x145caU;
    if (input->pattern==0U) return;
    table_words(0x1495aU,50000U);table_words(0x1459aU,10000U);table_words(0x145caU,10000U);
    if (input->pattern==1U || input->pattern==2U) table_words(selected,input->pattern==1U ? 1000U : 2000U);
    else if (input->pattern>=3U && input->pattern<=6U) {
        const uint32_t values[]={0U,1000U,2000U,50000U};table_words(0x1495aU,values[input->pattern-3U]);
    } else if (input->pattern==7U) {table_words(0x1495aU,65535U);table_words(selected,65535U);}
    else for (index=0;index<16U;++index) {
        uint16_t value=(uint16_t)(input->pattern==8U ? index*4096U : 65535U-index*4096U);
        *(volatile uint16_t *)(uintptr_t)(0x1495aU+index*2U)=value;
        *(volatile uint16_t *)(uintptr_t)(selected+index*2U)=value;
    }
    for (index=0;index<16U;++index) {
        *(volatile uint16_t *)(uintptr_t)(0x13a98U+index*2U)=(uint16_t)(index*16U);
        *(volatile uint16_t *)(uintptr_t)(0x15ce0U+index*2U)=(uint16_t)(index*4096U);
    }
}
static void prepare(const struct path_case *input)
{
    static const uint32_t starts[]={0x1495aU,0x1459aU,0x145caU,0x13a98U,0x15ce0U};
    static const uint32_t sizes[]={34U,34U,34U,32U,32U};
    unsigned index,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,0,RAM_SIZE);
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy((void *)(uintptr_t)starts[index],normalization_stock_calibrations+offset,sizes[index]);
        offset+=sizes[index];
    }
    write_calibrations(input);
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x2b68U)=0xa3b4U;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x8d60U)=0x11223344U;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x8d68U)=0xa7b8U;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x8d6aU)=0xc9daU;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=0xa5c3d2e1U;
    offset=0;
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy(calibration_before+offset,(const void *)(uintptr_t)starts[index],sizes[index]);
        offset+=sizes[index];
    }
}
static void calibration_after(void)
{
    hex((const void *)(uintptr_t)0x1495aU,34U);
    hex((const void *)(uintptr_t)0x1459aU,34U);
    hex((const void *)(uintptr_t)0x145caU,34U);
    hex((const void *)(uintptr_t)0x13a98U,32U);
    hex((const void *)(uintptr_t)0x15ce0U,32U);
}
static int observe(size_t index)
{
    const struct path_case *input=&normalization_cases[index];
    struct context context,initial; struct observation observation; unsigned reg;
    if (input->kind==0U) prepare(input);
    else {
        unsigned offset=0,index;
        const uint32_t starts[]={0x1495aU,0x1459aU,0x145caU,0x13a98U,0x15ce0U};
        const uint32_t sizes[]={34U,34U,34U,32U,32U};
        for (index=0;index<ARRAY_SIZE(starts);++index) {
            memcpy(calibration_before+offset,(const void *)(uintptr_t)starts[index],sizes[index]);
            offset+=sizes[index];
        }
    }
    for (reg=0;reg<15U;++reg) context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.r[6]=input->coefficient_coordinate; context.r[8]=1U; context.r[10]=input->coordinate;
    context.r[12]=RAM_BASE+0x28f8U; context.r[13]=0x15ce0U; context.r[14]=0x264f8U;
    context.gbr=RAM_BASE+0x8d58U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-normalization-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->kind,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context,sizeof(context));
    printf("\",\"observation\":\""); hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\""); rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\""); rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\""); hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\""); calibration_after();
    printf("\"}\n");
    return 1;
}
int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(normalization_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_NORMALIZATION status=PASS region=%s cases=%lu\n",
           NORMALIZATION_REGION,(unsigned long)ARRAY_SIZE(normalization_cases));
    return 0;
}
