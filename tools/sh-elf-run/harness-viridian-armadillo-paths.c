/* Explicit natural viridian-armadillo inputs and complete actual state observations. */
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
    uint32_t entry,pattern,axis,divisor,selector,dividend,scale,coordinate,factor,stage_factor,variant,sr;
};
#include "viridian-armadillo-path-cases.h"
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
static uint8_t calibration_before[sizeof(viridian_armadillo_stock_calibrations)];
static void put_word(uint32_t address,uint32_t value)
{ *(volatile uint16_t *)(uintptr_t)address=(uint16_t)value; }
static void write_table(uint32_t pattern)
{
    uint32_t index;
    if (pattern==0U) return;
    for (index=0;index<8U;++index) put_word(0x14e42U+index*2U,0U);
    if (pattern==3U) { put_word(0x14e42U,100U); put_word(0x14e44U,300U); return; }
    put_word(0x14e50U,pattern==1U ? 1000U : 2000U);
}
static void write_axis(uint32_t pattern)
{
    uint32_t index;
    if (pattern==0U) return;
    for (index=0;index<8U;++index) put_word(0x13bb8U+index*2U,(pattern==2U ? 0x100U : 0U)+index*0x200U);
}
static void prepare(const struct path_case *input)
{
    static const uint32_t starts[]={0x14e42U,0x13bb8U,0x8832U,0x8a30U};
    static const uint32_t sizes[]={18U,16U,1U,7U};
    unsigned index,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,0,RAM_SIZE);
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy((void *)(uintptr_t)starts[index],viridian_armadillo_stock_calibrations+offset,sizes[index]);
        offset+=sizes[index];
    }
    write_table(input->pattern); write_axis(input->axis);
    *(volatile uint8_t *)(uintptr_t)0x8832U=(uint8_t)input->factor;
    *(volatile uint8_t *)(uintptr_t)0x8a30U=(uint8_t)input->stage_factor;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=0xa5c3d2e1U;
    offset=0;
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy(calibration_before+offset,(const void *)(uintptr_t)starts[index],sizes[index]);
        offset+=sizes[index];
    }
}
static void calibration_after(void)
{
    hex((const void *)(uintptr_t)0x14e42U,18U);
    hex((const void *)(uintptr_t)0x13bb8U,16U);
    hex((const void *)(uintptr_t)0x8832U,1U);
    hex((const void *)(uintptr_t)0x8a30U,7U);
}
static int observe(size_t index)
{
    const struct path_case *input=&viridian_armadillo_cases[index];
    struct context context,initial; struct observation observation; unsigned reg;
    prepare(input);
    for (reg=0;reg<15U;++reg) context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.r[4]=input->divisor; context.r[5]=input->selector;
    context.r[6]=input->dividend; context.r[7]=input->scale;
    context.gbr=0x12344321U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=input->coordinate;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-viridian-armadillo-observation {\"schema\":1,\"index\":%lu,\"kind\":0,\"entry\":%lu,\"context\":\"",
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
    for (index=0;index<ARRAY_SIZE(viridian_armadillo_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_VIRIDIAN_ARMADILLO status=PASS region=%s cases=%lu\n",
           VIRIDIAN_ARMADILLO_REGION,(unsigned long)ARRAY_SIZE(viridian_armadillo_cases));
    return 0;
}
