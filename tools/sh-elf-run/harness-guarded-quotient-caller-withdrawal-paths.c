/* Input driver defined by defs/JK08A.guarded-quotient-caller-withdrawal-paths.toml. */
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
struct span { uint32_t address,size; };
#include "guarded-quotient-caller-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[GUARDED_QUOTIENT_CALLER_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[GUARDED_QUOTIENT_CALLER_WITHDRAWAL_BOUND_SIZE];
static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer;size_t index;
    for(index=0;index<size;++index)printf("%02x",(unsigned)data[index]);
}
static void rle(const uint8_t *data,size_t size)
{
    size_t first=0;
    while(first<size){
        size_t last=first+1U;
        while(last<size && data[last]==data[first])++last;
        printf("%s%lu:%02x",first ? "," : "",(unsigned long)(last-first),(unsigned)data[first]);
        first=last;
    }
}
static void snapshot(uint8_t *output,const struct span *spans,size_t count)
{
    size_t index,offset=0;
    for(index=0;index<count;++index){
        memcpy(output+offset,(const void *)(uintptr_t)spans[index].address,spans[index].size);
        offset+=spans[index].size;
    }
}
static void print_spans(const struct span *spans,size_t count)
{
    size_t index;
    for(index=0;index<count;++index)hex((const void *)(uintptr_t)spans[index].address,spans[index].size);
}
static int prepare(const struct path_case *input)
{
    size_t index,offset=0;
    if((input->entry!=0x532aeU && input->entry!=0x74b68U && input->entry!=0x75306U) || input->kind>=3U || input->byte_230e>0xffU || input->byte_2485>0xffU || input->byte_161a>0xffU || input->byte_1601>0xffU || input->byte_15df>0xffU || input->byte_1660>0xffU || input->byte_1680>0xffU || input->byte_193d>0xffU || input->byte_1600>0xffU || input->byte_417e>0xffU || input->byte_249b>0xffU || input->byte_245f>0xffU || input->byte_24d2>0xffU || input->word_22e8>0xffffU || input->word_1426>0xffffU || input->word_15ce>0xffffU || input->word_15fe>0xffffU || input->word_2ff0>0xffffU || input->word_2422>0xffffU || input->word_17f8>0xffffU || input->word_1210>0xffffU || input->word_19a2>0xffffU || input->word_23fc>0xffffU || input->word_18f2>0xffffU || input->word_19d4>0xffffU || input->word_9092>0xffffU || input->word_914e>0xffffU || input->word_9150>0xffffU || input->word_944e>0xffffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x230eU)=(uint8_t)input->byte_230e;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2485U)=(uint8_t)input->byte_2485;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x161aU)=(uint8_t)input->byte_161a;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1601U)=(uint8_t)input->byte_1601;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x15dfU)=(uint8_t)input->byte_15df;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1660U)=(uint8_t)input->byte_1660;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1680U)=(uint8_t)input->byte_1680;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x193dU)=(uint8_t)input->byte_193d;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1600U)=(uint8_t)input->byte_1600;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x417eU)=(uint8_t)input->byte_417e;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x249bU)=(uint8_t)input->byte_249b;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x245fU)=(uint8_t)input->byte_245f;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24d2U)=(uint8_t)input->byte_24d2;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x22e8U)=(uint16_t)input->word_22e8;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1426U)=(uint16_t)input->word_1426;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x15ceU)=(uint16_t)input->word_15ce;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x15feU)=(uint16_t)input->word_15fe;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x2ff0U)=(uint16_t)input->word_2ff0;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x2422U)=(uint16_t)input->word_2422;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x17f8U)=(uint16_t)input->word_17f8;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1210U)=(uint16_t)input->word_1210;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x19a2U)=(uint16_t)input->word_19a2;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x23fcU)=(uint16_t)input->word_23fc;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x18f2U)=(uint16_t)input->word_18f2;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x19d4U)=(uint16_t)input->word_19d4;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=(uint32_t)input->previous_fault;
    for(index=0;index<ARRAY_SIZE(guarded_quotient_caller_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)guarded_quotient_caller_withdrawal_controlled[index].address,input->calibration+offset,
            guarded_quotient_caller_withdrawal_controlled[index].size);
        offset+=guarded_quotient_caller_withdrawal_controlled[index].size;
    }
    if(offset!=GUARDED_QUOTIENT_CALLER_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(guarded_quotient_caller_withdrawal_cases);++index){
        const struct path_case *input=&guarded_quotient_caller_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,guarded_quotient_caller_withdrawal_controlled,ARRAY_SIZE(guarded_quotient_caller_withdrawal_controlled));
        snapshot(bound_before,guarded_quotient_caller_withdrawal_bound,ARRAY_SIZE(guarded_quotient_caller_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-guarded-quotient-caller-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(guarded_quotient_caller_withdrawal_controlled,ARRAY_SIZE(guarded_quotient_caller_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(guarded_quotient_caller_withdrawal_bound,ARRAY_SIZE(guarded_quotient_caller_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_GUARDED_QUOTIENT_CALLER_WITHDRAWAL status=PASS region=%s cases=%lu\n",GUARDED_QUOTIENT_CALLER_WITHDRAWAL_REGION,index);
    return 0;
}
