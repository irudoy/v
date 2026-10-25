/* Separate stock knock stage inputs and complete raw state; no expected outputs. */
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
#include "knock-access-cases.h"
static const char *const knock_access_kind_names[]={"normalization","metric","threshold","comparison"};
#define knock_access_kind knock_access_kind_names[KNOCK_ACCESS_KIND]
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete independent context ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];
static uint8_t calibration_before[KNOCK_ACCESS_CALIBRATION_SIZE];

static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer;size_t index;
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
    for (index=0;index<ARRAY_SIZE(knock_access_calibration_starts);++index) {
        unsigned size=knock_access_calibration_sizes[index];
        memcpy(calibration_before+offset,(const void *)(uintptr_t)knock_access_calibration_starts[index],size);
        offset+=size;
    }
}
static void print_calibrations(void)
{
    unsigned index;
    for (index=0;index<ARRAY_SIZE(knock_access_calibration_starts);++index)
        hex((const void *)(uintptr_t)knock_access_calibration_starts[index],knock_access_calibration_sizes[index]);
}
static void put_long(uint32_t offset,uint32_t value)
{ *(volatile uint32_t *)(uintptr_t)(RAM_BASE+offset)=value; }
static int prepare(const struct path_case *input)
{
    unsigned index,offset=0;uint32_t channel=input->channel;
    if (input->kind!=KNOCK_ACCESS_KIND || channel<1U || channel>6U
            || (input->selector!=0x82U && input->selector!=0x8aU)) return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    put_byte(0x11deU,(input->selector&8U) ? input->other : channel);
    put_byte(0x2143U,(input->selector&8U) ? channel : input->other);
    if (input->kind==0U) {
        if (input->entry!=((input->selector&8U) ? 0x4a3b0U : 0x4a26aU)) return 0;
        put_byte(0x2154U,input->blocks);put_byte(0x87e1U,input->flag);
        put_word(0x2152U,input->multiplier);
        for (index=0;index<8U;++index) put_word(0x2132U+2U*index,input->bins[index]);
    } else if (input->kind==1U) {
        if (input->entry!=(input->scope==2U ? 0x49e96U : 0x4a2b6U)) return 0;
        for (index=0;index<8U;++index) {
            put_word(0x20c2U+2U*index,input->sample[index]);
            put_word(0x2178U+16U*(channel-1U)+2U*index,input->reference[index]);
        }
        put_long(0x2274U+4U*(channel-1U),input->sum_input);
    } else {
        if (input->entry!=(input->kind==2U ? 0x49ffcU : 0x4a2eeU)) return 0;
        put_word(0x11f4U,input->speed);
        if (input->kind==3U) {
            put_long(0x21d8U+4U*(channel-1U),input->biased_input);
            put_byte(0x2142U,input->event_count);put_byte(0x24c2U,input->status);
            put_byte(0x2150U,input->bitmap);
        }
    }
    for (index=0;index<ARRAY_SIZE(knock_access_calibration_starts);++index) {
        unsigned size=knock_access_calibration_sizes[index];
        memcpy((void *)(uintptr_t)knock_access_calibration_starts[index],input->calibration+offset,size);
        offset+=size;
    }
    return 1;
}
static int observe(size_t index)
{
    const struct path_case *input=&knock_access_cases[index];
    struct context context=input->context,initial;struct observation observation;
    if (!prepare(input)) return 0;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    snapshot_calibrations();memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-knock-access-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->kind,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
    printf("\",\"observation\":\"");hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\"");rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\"");print_calibrations();printf("\"}\n");
    return 1;
}
int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(knock_access_cases);++index) if (!observe(index)) return 1;
    printf("VQ_SH_ELF_KNOCK_ACCESSES status=PASS region=%s kind=%s cases=%lu\n",
           KNOCK_ACCESS_REGION,knock_access_kind,(unsigned long)ARRAY_SIZE(knock_access_cases));
    return 0;
}
