/* Natural timing compositor inputs and complete actual state observations. */
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
    uint32_t kind,entry,pattern,outer,inner,curve,mode,enabled,below,coefficient;
    uint32_t composition,reverse_threshold,variant,sr;
};
#include "timing-division-path-cases.h"
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

static uint8_t calibration_before[179];
static void put_word(uint32_t address,uint32_t value)
{
    *(volatile uint16_t *)(uintptr_t)address=(uint16_t)value;
}
static void prepare(const struct path_case *input)
{
    static const uint8_t composition[4][7]={{0,0,0,0,0,128,0},{255,0,127,0,0,255,127},
        {0,255,128,255,255,0,128},{97,13,9,11,5,72,14}};
    static const uint32_t fields[]={0x23bdU,0x23c5U,0x23f1U,0x12dcU,0x15eaU,0x1a7dU,0x23eeU};
    static const uint32_t starts[]={0xc50eU,0x1461aU,0x1464aU,0x11f02U,0x11eeaU,0x9012U};
    static const uint32_t sizes[]={128U,16U,16U,9U,8U,2U};
    volatile uint8_t *ram=(volatile uint8_t *)(uintptr_t)RAM_BASE;
    unsigned index,offset=0;
    uint32_t threshold,first,second;
    memset((void *)(uintptr_t)RAM_BASE,0,RAM_SIZE);
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy((void *)(uintptr_t)starts[index],timing_division_stock_calibrations+offset,sizes[index]);
        offset+=sizes[index];
    }
    if (input->pattern!=0U) {
        static const uint16_t flat[]={0U,0U,1U,254U,255U,256U,65535U};
        for (index=0;index<64U;++index) {
            uint32_t value=input->pattern<=6U ? flat[input->pattern]
                :input->pattern==7U ? index*1024U:input->pattern==8U ? 65535U-index*1024U
                :input->pattern>=10U ? 255U:((index/8U+index%8U)&1U) ? 65535U:0U;
            put_word(0xc50eU+index*2U,value);
        }
        for (index=0;index<8U;++index) {
            uint32_t value=input->pattern<=6U ? (input->pattern==1U ? 211U:255U)
                :input->pattern==7U ? 17U+index*23U:input->pattern==8U ? 238U-index*23U
                :input->pattern>=10U ? input->pattern-10U:(index&1U) ? 255U:1U;
            *(volatile uint8_t *)(uintptr_t)(0x11f02U+index)=(uint8_t)value;
        }
    }
    threshold=*(volatile uint16_t *)(uintptr_t)0x9012U;
    first=input->below ? threshold-1U:threshold;second=first+1U;
    if (second>65535U) second=65535U;
    put_word(RAM_BASE+0x28b8U,input->reverse_threshold ? second:first);
    put_word(RAM_BASE+0x28baU,input->reverse_threshold ? first:second);
    ram[0x2458U]=(uint8_t)input->mode;ram[0x41abU]=(uint8_t)(input->enabled*64U);
    ram[0x106fU]=(uint8_t)input->curve;
    put_word(RAM_BASE+0x10caU,input->outer);put_word(RAM_BASE+0x1024U,input->inner);
    put_word(RAM_BASE+0x1900U,input->coefficient);
    for (index=0;index<ARRAY_SIZE(fields);++index) ram[fields[index]]=composition[input->composition][index];
    ram[0x1348U]=0x3dU;ram[0x134aU]=0x67U;ram[0x134cU]=0x95U;
    ram[0x12d4U]=0xb3U;ram[0x1830U]=0xcaU;ram[0x24d1U]=0xd3U;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=0xa5c3d2e1U;
    offset=0;
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy(calibration_before+offset,(const void *)(uintptr_t)starts[index],sizes[index]);offset+=sizes[index];
    }
}
static void calibration_after(void)
{
    hex((const void *)(uintptr_t)0xc50eU,128U);hex((const void *)(uintptr_t)0x1461aU,16U);
    hex((const void *)(uintptr_t)0x1464aU,16U);hex((const void *)(uintptr_t)0x11f02U,9U);
    hex((const void *)(uintptr_t)0x11eeaU,8U);hex((const void *)(uintptr_t)0x9012U,2U);
}

static int observe(size_t index)
{
    const struct path_case *input=&timing_division_cases[index];
    struct context context,initial;
    struct observation observation;
    unsigned reg;
    prepare(input);
    for (reg=0;reg<15U;++reg)
        context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.gbr=0x12344321U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U|input->outer;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) {
        fprintf(stderr,"timing-division[%lu]: const input context changes\n",(unsigned long)index);
        return 0;
    }
    printf("kb-timing-division-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
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
    for (index=0;index<ARRAY_SIZE(timing_division_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_TIMING_DIVISION status=PASS region=%s cases=%lu\n",
           TIMING_DIVISION_REGION,(unsigned long)ARRAY_SIZE(timing_division_cases));
    return 0;
}
