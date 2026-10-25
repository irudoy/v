/* Independent raw bank-mask inputs and complete bounded decoder observations. */
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
    uint32_t entry,mask2c,mask2e,mask30,mask39;
    struct context context;
};
#include "closed-loop-admission-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete independent context ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];
static uint8_t calibration_before[13];
static const uint32_t calibration_starts[]={0x8e78U,0xa101eU,0xa1020U,0xa1022U,0xa102aU,0xa114cU};
static const uint32_t calibration_sizes[]={1U,2U,2U,2U,2U,4U};

static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer; size_t index;
    for (index=0;index<size;++index) printf("%02x",(unsigned)data[index]);
}
static void rle(const uint8_t *data,size_t size)
{
    size_t start=0;
    while (start<size) {
        size_t end=start+1U;
        while (end<size && data[end]==data[start]) ++end;
        printf("%s%lu:%02x",start ? "," : "",(unsigned long)(end-start),(unsigned)data[start]);
        start=end;
    }
}
static void put_byte(uint32_t offset,uint32_t value)
{ *(volatile uint8_t *)(uintptr_t)(RAM_BASE+offset)=(uint8_t)value; }
static void snapshot_calibrations(void)
{
    unsigned index,offset=0;
    for (index=0;index<ARRAY_SIZE(calibration_starts);++index) {
        memcpy(calibration_before+offset,(const void *)(uintptr_t)calibration_starts[index],calibration_sizes[index]);
        offset+=calibration_sizes[index];
    }
}
static void print_calibrations(void)
{
    unsigned index;
    for (index=0;index<ARRAY_SIZE(calibration_starts);++index)
        hex((const void *)(uintptr_t)calibration_starts[index],calibration_sizes[index]);
}
static int prepare(const struct path_case *input)
{
    if ((input->entry!=0xa0f04U && input->entry!=0xa0ffeU)
            || input->mask2c>255U || input->mask2e>255U
            || input->mask30>255U || input->mask39>255U) return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    put_byte(0x48c0U,input->mask2c);
    put_byte(0x48beU,input->mask2e);
    put_byte(0x48b7U,input->mask30);
    put_byte(0x48b4U,input->mask39);
    return 1;
}
static int observe(size_t index)
{
    const struct path_case *input=&closed_loop_admission_cases[index];
    struct context context=input->context,initial; struct observation observation;
    if (!prepare(input)) return 0;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    snapshot_calibrations();
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-closed-loop-admission-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)(input->entry==0xa0ffeU),(unsigned long)input->entry);
    hex(&initial,sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context,sizeof(context));
    printf("\",\"observation\":\""); hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\""); rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\""); rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\""); hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\""); print_calibrations();
    printf("\"}\n");
    return 1;
}
int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(closed_loop_admission_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_CLOSED_LOOP_ADMISSION status=PASS region=%s cases=%lu\n",
           CLOSED_LOOP_ADMISSION_REGION,(unsigned long)ARRAY_SIZE(closed_loop_admission_cases));
    return 0;
}
