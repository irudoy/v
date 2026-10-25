/* Natural APC phase normalization inputs with complete state observations. */
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
    uint32_t entry,word,byte,count,remainder,phase;
    struct context context;
};
#include "phase-normalization-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete independent context ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];
static uint8_t calibration_before[8];
static const uint32_t calibration_starts[]={0x28e9eU,0x29020U,0x28ea0U};
static const uint32_t calibration_sizes[]={2U,4U,2U};

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
static void put_word(uint32_t offset,uint32_t value)
{ *(volatile uint16_t *)(uintptr_t)(RAM_BASE+offset)=(uint16_t)value; }
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
    if (!((input->word==0xffff13b8U && input->byte==0xffff193bU)
            || (input->word==0xffff1558U && input->byte==0xffff155aU))
            || (input->entry!=0x28dc8U && input->entry!=0x28e7cU) || input->count>65535U
            || input->remainder>255U || input->phase>255U) return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    put_word(input->word&65535U,input->count);
    put_byte(input->byte&65535U,input->remainder);
    put_byte(0x13b2U,input->phase);
    return 1;
}
static int observe(size_t index)
{
    const struct path_case *input=&phase_normalization_cases[index];
    struct context context=input->context,initial; struct observation observation;
    if (!prepare(input)) return 0;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    snapshot_calibrations();
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-phase-normalization-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)(input->entry==0x28e7cU),(unsigned long)input->entry);
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
    for (index=0;index<ARRAY_SIZE(phase_normalization_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_PHASE_NORMALIZATION status=PASS region=%s cases=%lu\n",
           PHASE_NORMALIZATION_REGION,(unsigned long)ARRAY_SIZE(phase_normalization_cases));
    return 0;
}
