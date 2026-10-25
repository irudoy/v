/* Explicit natural independent-leopard inputs and complete actual state observations. */
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
    uint32_t entry,pattern,left0,right0,left1,right1,point0,point1,variant,sr;
};
#include "independent-leopard-path-cases.h"
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
static uint8_t calibration_before[sizeof(independent_leopard_stock_calibrations)];
static void put_word(uint32_t address,uint32_t value)
{ *(volatile uint16_t *)(uintptr_t)address=(uint16_t)value; }
static void write_curve(uint32_t pattern)
{
    static const uint8_t rising[]={0,40,80,120}, falling[]={200,100,50,0};
    const uint8_t *bytes=0; uint32_t index,fill=0;
    if (pattern==0U) return;
    if (pattern==2U) bytes=rising;
    else if (pattern==3U) bytes=falling;
    else fill=pattern==4U ? 100U : pattern==5U ? 255U : 0U;
    for (index=0;index<4U;++index)
        *(volatile uint8_t *)(uintptr_t)(0x12522U+index)=(uint8_t)(bytes?bytes[index]:fill);
}
static void prepare(const struct path_case *input)
{
    volatile uint8_t *ram=(volatile uint8_t *)(uintptr_t)RAM_BASE;
    memset((void *)(uintptr_t)RAM_BASE,0,RAM_SIZE);
    memcpy((void *)(uintptr_t)0x12522U,independent_leopard_stock_calibrations,4U);
    memcpy((void *)(uintptr_t)0x12526U,independent_leopard_stock_calibrations+4U,4U);
    write_curve(input->pattern);
    put_word(RAM_BASE+0x288cU,input->left0); put_word(RAM_BASE+0x288eU,input->left1);
    put_word(RAM_BASE+0x4020U,input->right0); put_word(RAM_BASE+0x4022U,input->right1);
    ram[0x3529U]=(uint8_t)input->point0; ram[0x352aU]=(uint8_t)input->point1;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=0xa5c3d2e1U;
    memcpy(calibration_before,(const void *)(uintptr_t)0x12522U,4U);
    memcpy(calibration_before+4U,(const void *)(uintptr_t)0x12526U,4U);
}
static int observe(size_t index)
{
    const struct path_case *input=&independent_leopard_cases[index];
    struct context context,initial; struct observation observation; unsigned reg;
    prepare(input);
    for (reg=0;reg<15U;++reg) context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.gbr=0x12344321U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U|input->point0;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-independent-leopard-observation {\"schema\":1,\"index\":%lu,\"kind\":0,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context,sizeof(context));
    printf("\",\"observation\":\""); hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\""); rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\""); rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\""); hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\"");
    hex((const void *)(uintptr_t)0x12522U,4U); hex((const void *)(uintptr_t)0x12526U,4U);
    printf("\"}\n");
    return 1;
}
int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(independent_leopard_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_INDEPENDENT_LEOPARD status=PASS region=%s cases=%lu\n",
           INDEPENDENT_LEOPARD_REGION,(unsigned long)ARRAY_SIZE(independent_leopard_cases));
    return 0;
}
