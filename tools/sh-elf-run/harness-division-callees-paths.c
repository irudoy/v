/* Direct division ABI, zero-divisor word store and complete state observations. */
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
    uint32_t kind,entry,divisor,dividend,previous_fault,variant,sr;
};
#include "division-callees-path-cases.h"
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

static int observe(size_t index)
{
    const struct path_case *input=&division_callees_cases[index];
    struct context context,initial;
    struct observation observation;
    unsigned reg;
    memset((void *)(uintptr_t)RAM_BASE,(int)((0x5dU+input->variant*37U)&255U),RAM_SIZE);
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=input->previous_fault;
    for (reg=0;reg<15U;++reg)
        context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.r[0]=input->divisor;
    context.r[1]=input->dividend;
    context.gbr=0x12344321U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U|(input->divisor&65535U);
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) {
        fprintf(stderr,"division-callees[%lu]: const input context changes\n",(unsigned long)index);
        return 0;
    }
    printf("kb-division-callees-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->kind,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context,sizeof(context));
    printf("\",\"observation\":\""); hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\""); rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\""); rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\"");
    printf("\",\"calibration_after\":\"");
    printf("\"}\n");
    return 1;
}

int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(division_callees_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_DIVISION_CALLEES status=PASS region=%s cases=%lu\n",
           DIVISION_CALLEES_REGION,(unsigned long)ARRAY_SIZE(division_callees_cases));
    return 0;
}
