/* Explicit natural quiet-cat inputs and complete actual state observations. */
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
    uint32_t entry,pattern,index,source,other,coordinate,side,flag,gate,wide,variant,sr;
};
#include "quiet-cat-path-cases.h"
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
static uint8_t calibration_before[sizeof(quiet_cat_stock_calibrations)];
static void write_curve(uint32_t pattern,uint32_t address)
{
    uint32_t index,value;
    if (pattern==0U) return;
    for (index=0;index<8U;++index) {
        value=pattern==1U ? 100U : pattern==2U ? 10U+index*12U : 255U;
        *(volatile uint8_t *)(uintptr_t)(address+index)=(uint8_t)value;
    }
}
static void prepare(const struct path_case *input)
{
    static const uint32_t starts[]={0x123eaU,0x12412U,0x11be3U,0x8616U,0x8615U,0x8d64U,0x87afU,0x87b4U};
    static const uint32_t sizes[]={9U,9U,8U,1U,1U,7U,1U,1U};
    volatile uint8_t *ram=(volatile uint8_t *)(uintptr_t)RAM_BASE;
    unsigned index,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,0,RAM_SIZE);
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy((void *)(uintptr_t)starts[index],quiet_cat_stock_calibrations+offset,sizes[index]);
        offset+=sizes[index];
    }
    write_curve(input->pattern,input->index?0x12412U:0x123eaU);
    *(volatile uint8_t *)(uintptr_t)0x8616U=(uint8_t)(input->gate?1U:0U);
    if (input->wide) *(volatile uint8_t *)(uintptr_t)0x8615U=0x40U;
    ram[0x1224U+(uint8_t)input->index]=(uint8_t)input->source;
    ram[0x1262U+(uint8_t)input->index]=(uint8_t)input->other;
    ram[0x11aeU]=(uint8_t)input->coordinate;
    ram[0x2772U]=(uint8_t)input->side; ram[0x1071U]=(uint8_t)input->side;
    ram[0x24a7U]=(uint8_t)(input->flag?1U:0U);
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=0xa5c3d2e1U;
    offset=0;
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy(calibration_before+offset,(const void *)(uintptr_t)starts[index],sizes[index]);
        offset+=sizes[index];
    }
}
static void calibration_after(void)
{
    hex((const void *)(uintptr_t)0x123eaU,9U); hex((const void *)(uintptr_t)0x12412U,9U);
    hex((const void *)(uintptr_t)0x11be3U,8U); hex((const void *)(uintptr_t)0x8616U,1U);
    hex((const void *)(uintptr_t)0x8615U,1U); hex((const void *)(uintptr_t)0x8d64U,7U);
    hex((const void *)(uintptr_t)0x87afU,1U); hex((const void *)(uintptr_t)0x87b4U,1U);
}
static int observe(size_t index)
{
    const struct path_case *input=&quiet_cat_cases[index];
    struct context context,initial; struct observation observation; unsigned reg;
    prepare(input);
    for (reg=0;reg<15U;++reg) context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.r[4]=input->index;
    context.gbr=0x12344321U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U|input->index;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-quiet-cat-observation {\"schema\":1,\"index\":%lu,\"kind\":0,\"entry\":%lu,\"context\":\"",
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
    for (index=0;index<ARRAY_SIZE(quiet_cat_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_QUIET_CAT status=PASS region=%s cases=%lu\n",
           QUIET_CAT_REGION,(unsigned long)ARRAY_SIZE(quiet_cat_cases));
    return 0;
}
