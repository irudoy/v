/* Explicit natural denominator inputs and complete actual state observations. */
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
    uint32_t kind,entry,pattern,row,column,curve,gate,override,high,low,variant,sr;
};
#include "timing-denominator-path-cases.h"
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
    const uint8_t *data=pointer;
    size_t index;
    for (index=0;index<size;++index)
        printf("%02x",(unsigned)data[index]);
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

static uint8_t calibration_before[sizeof(timing_denominator_stock_calibrations)];
static void put_word(uint32_t address,uint32_t value)
{
    *(volatile uint16_t *)(uintptr_t)address=(uint16_t)value;
}
static uint32_t surface_word(uint32_t pattern,uint32_t index)
{
    if (pattern==1U) return 0U;
    if (pattern==2U) return 1U;
    if (pattern==3U || pattern>=8U) return 255U;
    if (pattern==4U) return 65535U;
    if (pattern==5U) return index*200U;
    if (pattern==6U) return 65535U-index*200U;
    return ((index/16U)+(index%16U))&1U ? 65535U : 0U;
}
static uint32_t curve_word(uint32_t pattern,uint32_t index)
{
    if (pattern==1U || pattern==8U) return 0U;
    if (pattern==2U || pattern==9U) return 1U;
    if (pattern==3U) return 255U;
    if (pattern==4U || (pattern==7U && (index&1U))) return 65535U;
    if (pattern==5U) return 20U+index*30U;
    if (pattern==6U) return 235U-index*30U;
    return 1U;
}
static void prepare(const struct path_case *input)
{
    static const uint32_t starts[]={0xc98eU,0x13478U,0x13498U,0x14afaU,0x134b8U,0x16948U,0x18846U,0x18866U,0x18dd6U,0x18886U,0x83c1U};
    static const uint32_t sizes[]={512U,32U,32U,18U,16U,512U,32U,32U,18U,16U,1U};
    static const uint32_t surfaces[]={0xc98eU,0x16948U};
    static const uint32_t curves[]={0x14afaU,0x18dd6U};
    volatile uint8_t *ram=(volatile uint8_t *)(uintptr_t)RAM_BASE;
    unsigned index,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,0,RAM_SIZE);
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy((void *)(uintptr_t)starts[index],timing_denominator_stock_calibrations+offset,sizes[index]);
        offset+=sizes[index];
    }
    if (input->pattern!=0U) {
        for (index=0;index<256U;++index) {
            uint32_t value=surface_word(input->pattern,index);
            put_word(surfaces[0]+index*2U,value);put_word(surfaces[1]+index*2U,value);
        }
        for (index=0;index<8U;++index) {
            uint32_t value=curve_word(input->pattern,index);
            put_word(curves[0]+index*2U,value);put_word(curves[1]+index*2U,value);
        }
    }
    *(volatile uint8_t *)(uintptr_t)0x83c1U=(uint8_t)((*(volatile uint8_t *)(uintptr_t)0x83c1U&~2U)|(input->gate?2U:0U));
    put_word(RAM_BASE+0x412aU,input->row);put_word(RAM_BASE+0x35ceU,input->row);
    put_word(RAM_BASE+0x11b6U,input->column);put_word(RAM_BASE+0x10bcU,input->curve);
    put_word(RAM_BASE+0x4138U,input->high);put_word(RAM_BASE+0x413aU,input->low);put_word(RAM_BASE+0x35f0U,input->low);
    put_word(RAM_BASE+0x243cU,0x1357U);put_word(RAM_BASE+0x1d26U,0x2468U);
    put_word(RAM_BASE+0x2c6cU,0xa1b2U);put_word(RAM_BASE+0x2c6eU,0xa3b4U);put_word(RAM_BASE+0x2cfeU,0xa5b6U);
    put_word(RAM_BASE+0x35d2U,0xb1b2U);put_word(RAM_BASE+0x35d0U,0xb3b4U);put_word(RAM_BASE+0x35d8U,0xb5b6U);
    ram[0x41fbU]=(uint8_t)input->override;ram[0x4214U]=(uint8_t)input->override;
    ram[0x2cfdU]=0xa7U;ram[0x35d6U]=0xb7U;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=0xa5c3d2e1U;
    offset=0;
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy(calibration_before+offset,(const void *)(uintptr_t)starts[index],sizes[index]);
        offset+=sizes[index];
    }
}
static void calibration_after(void)
{
    hex((const void *)(uintptr_t)0xc98eU,512U);hex((const void *)(uintptr_t)0x13478U,32U);
    hex((const void *)(uintptr_t)0x13498U,32U);hex((const void *)(uintptr_t)0x14afaU,18U);
    hex((const void *)(uintptr_t)0x134b8U,16U);hex((const void *)(uintptr_t)0x16948U,512U);
    hex((const void *)(uintptr_t)0x18846U,32U);hex((const void *)(uintptr_t)0x18866U,32U);
    hex((const void *)(uintptr_t)0x18dd6U,18U);hex((const void *)(uintptr_t)0x18886U,16U);
    hex((const void *)(uintptr_t)0x83c1U,1U);
}

static int observe(size_t index)
{
    const struct path_case *input=&timing_denominator_cases[index];
    struct context context,initial;
    struct observation observation;
    unsigned reg;
    prepare(input);
    for (reg=0;reg<15U;++reg)
        context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.gbr=0x12344321U;context.mach=0x13579bdfU;context.macl=0x2468ace0U;
    context.entry_sr=input->sr;context.fifth=0xb6c70000U|input->row;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) {
        fprintf(stderr,"timing-denominator[%lu]: const input context changes\n",(unsigned long)index);
        return 0;
    }
    printf("kb-timing-denominator-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->kind,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));
    printf("\",\"context_after\":\"");hex(&context,sizeof(context));
    printf("\",\"observation\":\"");hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\"");rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\"");calibration_after();
    printf("\"}\n");
    return 1;
}

int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(timing_denominator_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_TIMING_DENOMINATOR status=PASS region=%s cases=%lu\n",
           TIMING_DENOMINATOR_REGION,(unsigned long)ARRAY_SIZE(timing_denominator_cases));
    return 0;
}
