/* Input driver defined by defs/JK08A.misfire-tail-dispatch-withdrawal-paths.toml. */
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
#include "misfire-tail-dispatch-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[MISFIRE_TAIL_DISPATCH_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[MISFIRE_TAIL_DISPATCH_WITHDRAWAL_BOUND_SIZE];
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
    if((input->entry!=0x7c494U) || input->kind>=1U || input->byte_11b2>0xffU || input->byte_24c4>0xffU || input->byte_3834>0xffU || input->byte_4096>0xffU || input->word_409e>0xffffU || input->word_40a0>0xffffU || input->word_40a2>0xffffU || input->byte_41d2>0xffU || input->byte_4241>0xffU || input->byte_4251>0xffU || input->byte_444c>0xffU || input->byte_444d>0xffU || input->config_8354>0xffU || input->config_8656>0xffU || input->config_8bda>0xffU || input->config_186ce>0xffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11b2U)=(uint8_t)input->byte_11b2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24c4U)=(uint8_t)input->byte_24c4;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x3834U)=(uint8_t)input->byte_3834;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4096U)=(uint8_t)input->byte_4096;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x409eU)=(uint16_t)input->word_409e;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x40a0U)=(uint16_t)input->word_40a0;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x40a2U)=(uint16_t)input->word_40a2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41d2U)=(uint8_t)input->byte_41d2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4241U)=(uint8_t)input->byte_4241;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4251U)=(uint8_t)input->byte_4251;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x444cU)=(uint8_t)input->byte_444c;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x444dU)=(uint8_t)input->byte_444d;
    for(index=0;index<ARRAY_SIZE(misfire_tail_dispatch_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)misfire_tail_dispatch_withdrawal_controlled[index].address,input->calibration+offset,
            misfire_tail_dispatch_withdrawal_controlled[index].size);
        offset+=misfire_tail_dispatch_withdrawal_controlled[index].size;
    }
    if(offset!=MISFIRE_TAIL_DISPATCH_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(misfire_tail_dispatch_withdrawal_cases);++index){
        const struct path_case *input=&misfire_tail_dispatch_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,misfire_tail_dispatch_withdrawal_controlled,ARRAY_SIZE(misfire_tail_dispatch_withdrawal_controlled));
        snapshot(bound_before,misfire_tail_dispatch_withdrawal_bound,ARRAY_SIZE(misfire_tail_dispatch_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-misfire-tail-dispatch-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(misfire_tail_dispatch_withdrawal_controlled,ARRAY_SIZE(misfire_tail_dispatch_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(misfire_tail_dispatch_withdrawal_bound,ARRAY_SIZE(misfire_tail_dispatch_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_MISFIRE_TAIL_DISPATCH_WITHDRAWAL status=PASS region=%s cases=%lu\n",MISFIRE_TAIL_DISPATCH_WITHDRAWAL_REGION,index);
    return 0;
}
