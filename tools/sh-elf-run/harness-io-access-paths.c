/* Explicit bounded software transfers and complete separate native-bank observations. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define NATIVE_SIZE 1536U
#define ARRAY_SIZE(value) (sizeof(value)/sizeof((value)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr,fifth; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];
    uint32_t sr_before;
};
struct path_case {
    uint32_t entry,kind,group,pattern,slot,selector,param,word,prior,variant,sr;
};
#include "io-access-path-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete independent context ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
_Static_assert(sizeof(io_access_stock_calibrations)==512U,"complete declared descriptor inputs");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static const uint32_t native_starts[]={0xffffd900U,0xfffff400U,0xfffff700U};
static const uint32_t native_sizes[]={1024U,256U,256U};
static const uint8_t native_fills[]={0xa5U,0x5cU,0x6dU};
static const uint32_t calibration_starts[]={0x975aU,0x23ac4U};
static const uint32_t calibration_sizes[]={120U,392U};
static uint8_t ram_before[RAM_SIZE],native_before[NATIVE_SIZE],native_after[NATIVE_SIZE];
static uint8_t calibration_before[sizeof(io_access_stock_calibrations)];
static struct observation previous;
static uint32_t previous_kind=0xffffffffU,previous_group=0xffffffffU;

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
static void snapshot_native(uint8_t *output)
{
    unsigned index,offset=0;
    for (index=0;index<ARRAY_SIZE(native_starts);++index) {
        memcpy(output+offset,(const void *)(uintptr_t)native_starts[index],native_sizes[index]);
        offset+=native_sizes[index];
    }
}
static void snapshot_calibrations(uint8_t *output)
{
    unsigned index,offset=0;
    for (index=0;index<ARRAY_SIZE(calibration_starts);++index) {
        memcpy(output+offset,(const void *)(uintptr_t)calibration_starts[index],calibration_sizes[index]);
        offset+=calibration_sizes[index];
    }
}
static void calibration_after(void)
{
    unsigned index;
    for (index=0;index<ARRAY_SIZE(calibration_starts);++index)
        hex((const void *)(uintptr_t)calibration_starts[index],calibration_sizes[index]);
}
static void prepare(const struct path_case *input)
{
    unsigned index,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,0,RAM_SIZE);
    for (index=0;index<ARRAY_SIZE(native_starts);++index)
        memset((void *)(uintptr_t)(RAM_BASE+(native_starts[index]&65535U)),native_fills[index],native_sizes[index]);
    if (input->kind==0U)
        *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0xf430U)=input->word;
    else if (input->kind==1U)
        *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0xf754U)=(uint16_t)input->word;
    for (index=0;index<ARRAY_SIZE(native_starts);++index)
        memcpy((void *)(uintptr_t)native_starts[index],
               (const void *)(uintptr_t)(RAM_BASE+(native_starts[index]&65535U)),native_sizes[index]);
    for (index=0;index<ARRAY_SIZE(calibration_starts);++index) {
        memcpy((void *)(uintptr_t)calibration_starts[index],io_access_stock_calibrations+offset,calibration_sizes[index]);
        offset+=calibration_sizes[index];
    }
    if (input->kind==3U && input->pattern!=0U)
        memcpy((void *)(uintptr_t)(0x975aU+input->slot*4U),io_access_records[input->pattern],4U);
}
static int observe(size_t index)
{
    const struct path_case *input=&io_access_cases[index];
    struct context context,initial; struct observation observation; unsigned reg;
    if (input->kind==2U) {
        if (previous_kind!=1U || previous_group!=input->group) return 0;
    } else prepare(input);
    for (reg=0;reg<15U;++reg) context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.gbr=0x12344321U;
    if (input->kind==0U) context.r[4]=input->param;
    else if (input->kind==1U) context.r[4]=input->selector;
    else if (input->kind==2U) {
        context.r[4]=previous.exit[15];
        context.gbr=previous.exit[4];
    } else {
        context.r[7]=1U<<(input->slot+1U);
        context.r[9]=input->prior;
        context.r[11]=input->slot;
    }
    context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    snapshot_native(native_before);
    snapshot_calibrations(calibration_before);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    snapshot_native(native_after);
    printf("kb-io-access-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->kind,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context,sizeof(context));
    printf("\",\"observation\":\""); hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\""); rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\""); rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"native_io_before\":\""); hex(native_before,sizeof(native_before));
    printf("\",\"native_io_after\":\""); hex(native_after,sizeof(native_after));
    printf("\",\"calibration_before\":\""); hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\""); calibration_after();
    printf("\"}\n");
    previous=observation; previous_kind=input->kind; previous_group=input->group;
    return 1;
}
int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(io_access_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_IO_ACCESS status=PASS region=%s cases=%lu\n",
           IO_ACCESS_REGION,(unsigned long)ARRAY_SIZE(io_access_cases));
    return 0;
}
