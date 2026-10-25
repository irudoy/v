/* Exact existing coherent prefix followed by the complete pedal comparator. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
struct snapshot_context {uint32_t r[15],gbr,mach,macl,entry_t;};
struct context {uint32_t r[15],gbr,mach,macl,entry_sr,fifth;};
struct snapshot_observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[96],frame_after[96];uint32_t sr_before;
};
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];uint32_t sr_before;
};
struct span {uint32_t address,size;};
#include "pedal-snapshot-high-state-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct snapshot_context)==76U,"existing complete snapshot context");
_Static_assert(sizeof(struct snapshot_observation)==380U,"existing complete snapshot observer");
_Static_assert(offsetof(struct snapshot_observation,frame_before)==184U,"existing snapshot entry frame");
_Static_assert(offsetof(struct snapshot_observation,frame_after)==280U,"existing snapshot exit frame");
_Static_assert(offsetof(struct snapshot_observation,sr_before)==376U,"existing snapshot SR input");
_Static_assert(sizeof(struct context)==80U,"complete comparator context");
_Static_assert(offsetof(struct context,fifth)==76U,"ordinary stack argument");
_Static_assert(sizeof(struct observation)==572U,"existing complete ordinary observer");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete comparator entry frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete comparator exit frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete comparator SR input");
extern void stock_invoke_injection_start_delay(uint32_t,const struct snapshot_context *,struct snapshot_observation *);
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t before[RAM_SIZE],after_snapshot[RAM_SIZE],before_comparator[RAM_SIZE];
static uint8_t calibration_before[PEDAL_CALIBRATION_SIZE],bound_before[PEDAL_BOUND_SIZE];

static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer;size_t n;
    for(n=0;n<size;++n)printf("%02x",(unsigned)data[n]);
}
static void rle(const uint8_t *data,size_t size)
{
    size_t start=0;
    while(start<size){size_t end=start+1U;while(end<size&&data[start]==data[end])++end;
        printf("%s%lu:%02x",start?",":"",(unsigned long)(end-start),(unsigned)data[start]);start=end;}
}
static void snapshot_spans(uint8_t *output,const struct span *spans,size_t count)
{
    size_t i,offset=0;
    for(i=0;i<count;++i){memcpy(output+offset,(const void *)(uintptr_t)spans[i].address,spans[i].size);offset+=spans[i].size;}
}
static void print_spans(const struct span *spans,size_t count)
{
    size_t i;
    for(i=0;i<count;++i)hex((const void *)(uintptr_t)spans[i].address,spans[i].size);
}
static void prepare(const struct paired_case *input)
{
    size_t i,j,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,input->pattern,RAM_SIZE);
    for(i=0;i<ARRAY_SIZE(pedal_ram_fields);++i){
        const struct span *field=&pedal_ram_fields[i];
        volatile uint8_t *target=(volatile uint8_t *)(uintptr_t)(RAM_BASE+field->address);
        for(j=0;j<field->size;++j)target[j]=(uint8_t)(input->ram[i]>>(8U*(field->size-j-1U)));
    }
    memcpy((void *)(uintptr_t)(RAM_BASE+0x277EU),input->block,260U);
    for(i=0;i<ARRAY_SIZE(pedal_calibration);++i){
        memcpy((void *)(uintptr_t)pedal_calibration[i].address,
            pedal_calibration_blobs[input->calibration_index]+offset,pedal_calibration[i].size);
        offset+=pedal_calibration[i].size;
    }
}
int main(void)
{
    size_t index;
    for(index=0;index<ARRAY_SIZE(pedal_cases);++index){
        const struct paired_case *input=&pedal_cases[index];
        struct snapshot_context snapshot_context=input->snapshot,snapshot_input;
        struct context context=input->comparator,comparator_input;
        struct snapshot_observation first;struct observation second;
        prepare(input);snapshot_input=snapshot_context;comparator_input=context;
        memset(&first,0xA6,sizeof(first));memset(&second,0xA6,sizeof(second));
        memcpy(before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot_spans(calibration_before,pedal_calibration,ARRAY_SIZE(pedal_calibration));
        snapshot_spans(bound_before,pedal_bound,ARRAY_SIZE(pedal_bound));
        stock_invoke_injection_start_delay(PEDAL_SNAPSHOT_ENTRY,&snapshot_context,&first);
        memcpy(after_snapshot,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        memcpy(before_comparator,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        stock_invoke_ignition_consumer(PEDAL_COMPARATOR_ENTRY,&context,&second);
        printf("kb-pedal-snapshot-high-state-observation {\"schema\":1,\"index\":%lu,\"snapshot_entry\":%lu,\"entry\":%lu,\"snapshot_context\":\"",
            (unsigned long)index,(unsigned long)PEDAL_SNAPSHOT_ENTRY,(unsigned long)PEDAL_COMPARATOR_ENTRY);
        hex(&snapshot_input,sizeof(snapshot_input));printf("\",\"snapshot_context_after\":\"");hex(&snapshot_context,sizeof(snapshot_context));
        printf("\",\"snapshot_observation\":\"");hex(&first,sizeof(first));
        printf("\",\"context\":\"");hex(&comparator_input,sizeof(comparator_input));
        printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&second,sizeof(second));
        printf("\",\"ram_before\":\"");rle(before,RAM_SIZE);
        printf("\",\"ram_after_snapshot\":\"");rle(after_snapshot,RAM_SIZE);
        printf("\",\"ram_before_comparator\":\"");rle(before_comparator,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(pedal_calibration,ARRAY_SIZE(pedal_calibration));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(pedal_bound,ARRAY_SIZE(pedal_bound));printf("\"}\n");
    }
    printf("VQ_SH_ELF_PEDAL_SNAPSHOT_HIGH_STATE status=PASS region=jk08a-pedal-snapshot-high-state-paths cases=%lu\n",
        (unsigned long)index);return 0;
}
