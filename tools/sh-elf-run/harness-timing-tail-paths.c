/* Explicit stock timing-tail inputs and complete actual state observations. */
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
    uint32_t kind,entry,pattern,coordinate,curve,minimum,enabled,reverse_threshold,variant,sr;
};
#include "timing-tail-path-cases.h"
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

static uint8_t calibration_before[sizeof(timing_tail_stock_calibrations)];
static void put_word(uint32_t address,uint32_t value)
{
    *(volatile uint16_t *)(uintptr_t)address=(uint16_t)value;
}
static void prepare(const struct path_case *input)
{
    static const uint32_t starts[]={0x11efaU,0x147caU,0x1460aU,0x11eeaU,0x9010U};
    static const uint32_t sizes[]={9U,18U,16U,8U,2U};
    volatile uint8_t *ram=(volatile uint8_t *)(uintptr_t)RAM_BASE;
    uint32_t first=input->minimum,second=first<65535U ? first+1U:65535U;
    unsigned index,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,0,RAM_SIZE);
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy((void *)(uintptr_t)starts[index],timing_tail_stock_calibrations+offset,sizes[index]);offset+=sizes[index];
    }
    if (input->pattern!=0U) {
        static const uint16_t flat[]={0U,0U,1U,254U,255U,256U,65535U};
        for (index=0;index<8U;++index) {
            uint32_t word=input->pattern<=6U ? flat[input->pattern]
                :input->pattern==7U ? index*8192U:input->pattern==8U ? 65535U-index*8192U
                :input->pattern>=10U ? 255U:(index&1U) ? 65535U:0U;
            uint32_t byte=input->pattern<=6U ? (input->pattern==1U ? 211U:255U)
                :input->pattern==7U ? 17U+index*23U:input->pattern==8U ? 238U-index*23U
                :input->pattern>=10U ? input->pattern-10U:(index&1U) ? 255U:1U;
            put_word(0x147caU+index*2U,word);
            *(volatile uint8_t *)(uintptr_t)(0x11efaU+index)=(uint8_t)byte;
        }
    }
    put_word(RAM_BASE+0x28b8U,input->reverse_threshold ? second:first);
    put_word(RAM_BASE+0x28baU,input->reverse_threshold ? first:second);
    ram[0x41abU]=(uint8_t)(input->enabled*64U);ram[0x106fU]=(uint8_t)input->curve;
    put_word(RAM_BASE+0x10caU,input->coordinate);put_word(RAM_BASE+0x1900U,0xa3b4U);
    ram[0x1347U]=0x3dU;ram[0x1349U]=0x67U;ram[0x134bU]=0x95U;ram[0x12d5U]=0xb3U;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=0xa5c3d2e1U;
    offset=0;
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy(calibration_before+offset,(const void *)(uintptr_t)starts[index],sizes[index]);offset+=sizes[index];
    }
}
static void calibration_after(void)
{
    hex((const void *)(uintptr_t)0x11efaU,9U);hex((const void *)(uintptr_t)0x147caU,18U);
    hex((const void *)(uintptr_t)0x1460aU,16U);hex((const void *)(uintptr_t)0x11eeaU,8U);
    hex((const void *)(uintptr_t)0x9010U,2U);
}

static int observe(size_t index)
{
    const struct path_case *input=&timing_tail_cases[index];
    struct context context,initial;
    struct observation observation;
    unsigned reg;
    prepare(input);
    for (reg=0;reg<15U;++reg)
        context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.r[9]=RAM_BASE+0x1068U;context.r[10]=RAM_BASE+0x128cU;context.r[13]=RAM_BASE+0x41a9U;
    context.gbr=RAM_BASE+0x128cU; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U|input->coordinate;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) {
        fprintf(stderr,"timing-tail[%lu]: const input context changes\n",(unsigned long)index);
        return 0;
    }
    printf("kb-timing-tail-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
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
    for (index=0;index<ARRAY_SIZE(timing_tail_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_TIMING_TAIL status=PASS region=%s cases=%lu\n",
           TIMING_TAIL_REGION,(unsigned long)ARRAY_SIZE(timing_tail_cases));
    return 0;
}
