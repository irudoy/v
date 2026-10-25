/* Input driver defined by defs/JK08A.state-surface-caller-withdrawal-paths.toml. */
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
#include "state-surface-caller-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[STATE_SURFACE_CALLER_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[STATE_SURFACE_CALLER_WITHDRAWAL_BOUND_SIZE];
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
    if((input->entry!=0x647e8U) || input->kind>=1U || input->byte_1082>0xffU || input->byte_1083>0xffU || input->byte_11ae>0xffU || input->word_13dc>0xffffU || input->word_13de>0xffffU || input->byte_1861>0xffU || input->byte_1873>0xffU || input->byte_244f>0xffU || input->byte_2450>0xffU || input->byte_3373>0xffU || input->word_40c6>0xffffU || input->config_8799>0xffU || input->config_8b3f>0xffU || input->surface_value_0>0xffU || input->surface_value_1>0xffU || input->surface_value_2>0xffU || input->surface_value_3>0xffU || input->surface_value_4>0xffU || input->surface_value_5>0xffU || input->surface_value_6>0xffU || input->surface_value_7>0xffU || input->surface_value_8>0xffU || input->surface_value_9>0xffU || input->surface_value_10>0xffU || input->surface_value_11>0xffU || input->surface_value_12>0xffU || input->surface_value_13>0xffU || input->surface_value_14>0xffU || input->surface_value_15>0xffU || input->selection_value_0>0xffU || input->selection_value_1>0xffU || input->selection_value_2>0xffU || input->selection_value_3>0xffU || input->selection_value_4>0xffU || input->selection_value_5>0xffU || input->selection_value_6>0xffU || input->selection_value_7>0xffU || input->selection_value_8>0xffU || input->selection_value_9>0xffU || input->selection_value_10>0xffU || input->selection_value_11>0xffU || input->selection_value_12>0xffU || input->selection_value_13>0xffU || input->selection_value_14>0xffU || input->selection_value_15>0xffU || input->row_axis_0>0xffU || input->row_axis_1>0xffU || input->row_axis_2>0xffU || input->row_axis_3>0xffU || input->col_axis_0>0xffU || input->col_axis_1>0xffU || input->col_axis_2>0xffU || input->col_axis_3>0xffU || input->curve_value_0>0xffU || input->curve_value_1>0xffU || input->curve_value_2>0xffU || input->curve_value_3>0xffU || input->curve_value_4>0xffU || input->curve_value_5>0xffU || input->curve_value_6>0xffU || input->curve_value_7>0xffU || input->curve_value_8>0xffU || input->curve_value_9>0xffU || input->curve_value_10>0xffU || input->curve_value_11>0xffU || input->curve_value_12>0xffU || input->curve_value_13>0xffU || input->curve_value_14>0xffU || input->curve_value_15>0xffU || input->split_value_0>0xffU || input->split_value_1>0xffU || input->split_value_2>0xffU || input->split_value_3>0xffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1082U)=(uint8_t)input->byte_1082;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1083U)=(uint8_t)input->byte_1083;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11aeU)=(uint8_t)input->byte_11ae;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x13dcU)=(uint16_t)input->word_13dc;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x13deU)=(uint16_t)input->word_13de;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1861U)=(uint8_t)input->byte_1861;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1873U)=(uint8_t)input->byte_1873;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x244fU)=(uint8_t)input->byte_244f;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2450U)=(uint8_t)input->byte_2450;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x3373U)=(uint8_t)input->byte_3373;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x40c6U)=(uint16_t)input->word_40c6;
    for(index=0;index<ARRAY_SIZE(state_surface_caller_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)state_surface_caller_withdrawal_controlled[index].address,input->calibration+offset,
            state_surface_caller_withdrawal_controlled[index].size);
        offset+=state_surface_caller_withdrawal_controlled[index].size;
    }
    if(offset!=STATE_SURFACE_CALLER_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(state_surface_caller_withdrawal_cases);++index){
        const struct path_case *input=&state_surface_caller_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,state_surface_caller_withdrawal_controlled,ARRAY_SIZE(state_surface_caller_withdrawal_controlled));
        snapshot(bound_before,state_surface_caller_withdrawal_bound,ARRAY_SIZE(state_surface_caller_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-state-surface-caller-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(state_surface_caller_withdrawal_controlled,ARRAY_SIZE(state_surface_caller_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(state_surface_caller_withdrawal_bound,ARRAY_SIZE(state_surface_caller_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_STATE_SURFACE_CALLER_WITHDRAWAL status=PASS region=%s cases=%lu\n",STATE_SURFACE_CALLER_WITHDRAWAL_REGION,index);
    return 0;
}
