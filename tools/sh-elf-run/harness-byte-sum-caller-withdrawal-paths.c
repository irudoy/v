/* Input driver defined by defs/JK08A.byte-sum-caller-withdrawal-paths.toml. */
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
#include "byte-sum-caller-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[BYTE_SUM_CALLER_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[BYTE_SUM_CALLER_WITHDRAWAL_BOUND_SIZE];
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
    if((input->entry!=0x464deU) || input->kind>=1U || input->byte_1716>0xffU || input->word_173c>0xffffU || input->word_173e>0xffffU || input->byte_1740>0xffU || input->byte_1741>0xffU || input->byte_1742>0xffU || input->word_1748>0xffffU || input->word_174c>0xffffU || input->byte_174f>0xffU || input->byte_22e4>0xffU || input->curve_value_0>0xffU || input->curve_value_1>0xffU || input->curve_value_2>0xffU || input->curve_value_3>0xffU || input->curve_value_4>0xffU || input->curve_value_5>0xffU || input->curve_value_6>0xffU || input->curve_value_7>0xffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1716U)=(uint8_t)input->byte_1716;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x173cU)=(uint16_t)input->word_173c;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x173eU)=(uint16_t)input->word_173e;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1740U)=(uint8_t)input->byte_1740;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1741U)=(uint8_t)input->byte_1741;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1742U)=(uint8_t)input->byte_1742;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1748U)=(uint16_t)input->word_1748;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x174cU)=(uint16_t)input->word_174c;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x174fU)=(uint8_t)input->byte_174f;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x22e4U)=(uint8_t)input->byte_22e4;
    for(index=0;index<ARRAY_SIZE(byte_sum_caller_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)byte_sum_caller_withdrawal_controlled[index].address,input->calibration+offset,
            byte_sum_caller_withdrawal_controlled[index].size);
        offset+=byte_sum_caller_withdrawal_controlled[index].size;
    }
    if(offset!=BYTE_SUM_CALLER_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(byte_sum_caller_withdrawal_cases);++index){
        const struct path_case *input=&byte_sum_caller_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,byte_sum_caller_withdrawal_controlled,ARRAY_SIZE(byte_sum_caller_withdrawal_controlled));
        snapshot(bound_before,byte_sum_caller_withdrawal_bound,ARRAY_SIZE(byte_sum_caller_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-byte-sum-caller-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(byte_sum_caller_withdrawal_controlled,ARRAY_SIZE(byte_sum_caller_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(byte_sum_caller_withdrawal_bound,ARRAY_SIZE(byte_sum_caller_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_BYTE_SUM_CALLER_WITHDRAWAL status=PASS region=%s cases=%lu\n",BYTE_SUM_CALLER_WITHDRAWAL_REGION,index);
    return 0;
}
