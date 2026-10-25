/* Explicit bounded messy-roadrunner inputs and complete actual state observations. */
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
    uint32_t entry,pattern,axis,word,base,variant,sr;
};
#include "messy-roadrunner-path-cases.h"
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
static uint8_t calibration_before[sizeof(messy_roadrunner_stock_calibrations)];
static void write_table(uint32_t pattern)
{
    uint32_t index,value;
    if (pattern==0U) return;
    for (index=0;index<8U;++index) {
        if (pattern==1U) value=0U;
        else if (pattern==2U) value=1U;
        else if (pattern==3U) value=2U;
        else if (pattern==4U) value=255U;
        else value=pattern==5U ? index*32U : 255U-index*32U;
        *(volatile uint8_t *)(uintptr_t)(0x11f3aU+index)=(uint8_t)value;
    }
}
static void write_axis(uint32_t pattern)
{
    uint32_t index;
    if (pattern==0U) return;
    for (index=0;index<8U;++index)
        *(volatile uint8_t *)(uintptr_t)(0x11aefU+index)=(uint8_t)(index*32U+(pattern==2U ? 1U : 0U));
}
static void prepare(const struct path_case *input)
{
    static const uint32_t starts[]={0x11f3aU,0x11aefU};
    static const uint32_t sizes[]={9U,8U};
    unsigned index,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,0,RAM_SIZE);
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy((void *)(uintptr_t)starts[index],messy_roadrunner_stock_calibrations+offset,sizes[index]);
        offset+=sizes[index];
    }
    write_table(input->pattern); write_axis(input->axis);
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x8e08U)=(uint16_t)input->base;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x8ec0U)=0xd3e4f506U;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x8fdeU)=0xa7b8U;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=0xa5c3d2e1U;
    offset=0;
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy(calibration_before+offset,(const void *)(uintptr_t)starts[index],sizes[index]);
        offset+=sizes[index];
    }
}
static void calibration_after(void)
{
    hex((const void *)(uintptr_t)0x11f3aU,9U);
    hex((const void *)(uintptr_t)0x11aefU,8U);
}
static int observe(size_t index)
{
    const struct path_case *input=&messy_roadrunner_cases[index];
    struct context context,initial; struct observation observation; unsigned reg;
    prepare(input);
    for (reg=0;reg<15U;++reg) context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.r[2]=input->word; context.r[8]=RAM_BASE+0x8e08U; context.r[11]=0x21bbcU;
    context.gbr=RAM_BASE+0x8e34U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-messy-roadrunner-observation {\"schema\":1,\"index\":%lu,\"kind\":0,\"entry\":%lu,\"context\":\"",
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
    for (index=0;index<ARRAY_SIZE(messy_roadrunner_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_MESSY_ROADRUNNER status=PASS region=%s cases=%lu\n",
           MESSY_ROADRUNNER_REGION,(unsigned long)ARRAY_SIZE(messy_roadrunner_cases));
    return 0;
}
