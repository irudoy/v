/* Explicit natural uptight-duck inputs and complete actual state observations. */
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
    uint32_t entry,pattern,axis,coordinate,dividend,threshold,side,variant,sr;
};
#include "uptight-duck-path-cases.h"
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
static uint8_t calibration_before[sizeof(uptight_duck_stock_calibrations)];
static void put_word(uint32_t address,uint32_t value)
{ *(volatile uint16_t *)(uintptr_t)address=(uint16_t)value; }
static void write_words(uint32_t address,uint32_t pattern)
{
    uint32_t index,value;
    if (pattern==0U) return;
    for (index=0;index<32U;++index) {
        value=pattern==1U ? 0U : pattern==2U ? index*20U : pattern==3U && index==31U ? 4000U : pattern==4U ? 1000U : 0U;
        put_word(address+index*2U,value);
    }
}
static void write_axis(uint32_t pattern)
{
    uint32_t index;
    if (pattern==0U) return;
    for (index=0;index<32U;++index)
        put_word(0x13ca8U+index*2U,pattern==1U ? index*100U : 10U+index*100U);
}
static void prepare(const struct path_case *input)
{
    static const uint32_t starts[]={0x15bf0U,0x15c40U,0x15c80U,0x13ca8U,0x8c8cU};
    static const uint32_t sizes[]={66U,64U,66U,64U,1U};
    unsigned index,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,0,RAM_SIZE);
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy((void *)(uintptr_t)starts[index],uptight_duck_stock_calibrations+offset,sizes[index]);
        offset+=sizes[index];
    }
    write_words(0x15bf0U,input->side);
    write_words(0x15c80U,input->pattern);
    write_axis(input->axis);
    *(volatile uint8_t *)(uintptr_t)0x8c8cU=(uint8_t)input->threshold;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=0xa5c3d2e1U;
    offset=0;
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy(calibration_before+offset,(const void *)(uintptr_t)starts[index],sizes[index]);
        offset+=sizes[index];
    }
}
static void calibration_after(void)
{
    hex((const void *)(uintptr_t)0x15bf0U,66U); hex((const void *)(uintptr_t)0x15c40U,64U);
    hex((const void *)(uintptr_t)0x15c80U,66U); hex((const void *)(uintptr_t)0x13ca8U,64U);
    hex((const void *)(uintptr_t)0x8c8cU,1U);
}
static int observe(size_t index)
{
    const struct path_case *input=&uptight_duck_cases[index];
    struct context context,initial; struct observation observation; unsigned reg;
    prepare(input);
    for (reg=0;reg<15U;++reg) context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.r[4]=input->dividend; context.r[5]=input->coordinate; context.r[6]=RAM_BASE+0x3000U;
    context.gbr=0x12344321U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U|input->coordinate;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-uptight-duck-observation {\"schema\":1,\"index\":%lu,\"kind\":0,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->entry);
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
    for (index=0;index<ARRAY_SIZE(uptight_duck_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_UPTIGHT_DUCK status=PASS region=%s cases=%lu\n",
           UPTIGHT_DUCK_REGION,(unsigned long)ARRAY_SIZE(uptight_duck_cases));
    return 0;
}
