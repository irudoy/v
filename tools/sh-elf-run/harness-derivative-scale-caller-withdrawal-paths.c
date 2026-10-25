/* Input driver defined by defs/JK08A.derivative-scale-caller-withdrawal-paths.toml. */
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
#include "derivative-scale-caller-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[DERIVATIVE_SCALE_CALLER_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[DERIVATIVE_SCALE_CALLER_WITHDRAWAL_BOUND_SIZE];
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
    if((input->entry!=0xb78daU && input->entry!=0xb7a3cU) || input->kind>=2U || input->curve_first_00>0xffffU || input->curve_first_01>0xffffU || input->curve_first_02>0xffffU || input->curve_first_03>0xffffU || input->curve_first_04>0xffffU || input->curve_first_05>0xffffU || input->curve_first_06>0xffffU || input->curve_first_07>0xffffU || input->curve_first_08>0xffffU || input->curve_first_09>0xffffU || input->curve_first_10>0xffffU || input->curve_first_11>0xffffU || input->curve_first_12>0xffffU || input->curve_first_13>0xffffU || input->curve_first_14>0xffffU || input->curve_first_15>0xffffU || input->curve_first_16>0xffffU || input->curve_middle_00>0xffffU || input->curve_middle_01>0xffffU || input->curve_middle_02>0xffffU || input->curve_middle_03>0xffffU || input->curve_middle_04>0xffffU || input->curve_middle_05>0xffffU || input->curve_middle_06>0xffffU || input->curve_middle_07>0xffffU || input->curve_middle_08>0xffffU || input->curve_last_00>0xffffU || input->curve_last_01>0xffffU || input->curve_last_02>0xffffU || input->curve_last_03>0xffffU || input->curve_last_04>0xffffU || input->curve_last_05>0xffffU || input->curve_last_06>0xffffU || input->curve_last_07>0xffffU || input->curve_last_08>0xffffU || input->curve_last_09>0xffffU || input->curve_last_10>0xffffU || input->curve_last_11>0xffffU || input->curve_last_12>0xffffU || input->curve_last_13>0xffffU || input->curve_last_14>0xffffU || input->curve_last_15>0xffffU || input->curve_last_16>0xffffU || input->threshold_word>0xffffU || input->ratio_gain_first>0xffU || input->ratio_gain_second>0xffU || input->negative_gain_first>0xffU || input->negative_gain_second>0xffU || input->ratio_gain_middle>0xffU || input->selector_gain_last>0xffU || input->selector_gain_second>0xffU || input->selector_gain_third>0xffU || input->axis_first_style>0xffU || input->axis_middle_style>0xffU || input->axis_last_style>0xffU || input->axis_first_seed>0xffffU || input->axis_middle_seed>0xffffU || input->axis_last_seed>0xffffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x2f98U)=(uint32_t)input->previous_first;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x3228U)=(uint32_t)input->previous_second;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=(uint32_t)input->previous_fault;
    for(index=0;index<ARRAY_SIZE(derivative_scale_caller_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)derivative_scale_caller_withdrawal_controlled[index].address,input->calibration+offset,
            derivative_scale_caller_withdrawal_controlled[index].size);
        offset+=derivative_scale_caller_withdrawal_controlled[index].size;
    }
    if(offset!=DERIVATIVE_SCALE_CALLER_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(derivative_scale_caller_withdrawal_cases);++index){
        const struct path_case *input=&derivative_scale_caller_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,derivative_scale_caller_withdrawal_controlled,ARRAY_SIZE(derivative_scale_caller_withdrawal_controlled));
        snapshot(bound_before,derivative_scale_caller_withdrawal_bound,ARRAY_SIZE(derivative_scale_caller_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-derivative-scale-caller-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(derivative_scale_caller_withdrawal_controlled,ARRAY_SIZE(derivative_scale_caller_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(derivative_scale_caller_withdrawal_bound,ARRAY_SIZE(derivative_scale_caller_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_DERIVATIVE_SCALE_CALLER_WITHDRAWAL status=PASS region=%s cases=%lu\n",DERIVATIVE_SCALE_CALLER_WITHDRAWAL_REGION,index);
    return 0;
}
