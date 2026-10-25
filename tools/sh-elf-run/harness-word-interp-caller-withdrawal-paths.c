/* Input driver defined by defs/JK08A.word-interp-caller-withdrawal-paths.toml. */
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
#include "word-interp-caller-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[WORD_INTERP_CALLER_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[WORD_INTERP_CALLER_WITHDRAWAL_BOUND_SIZE];
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
    if((input->entry!=0x72f1eU && input->entry!=0xb7b98U) || input->kind>=2U || input->previous_curve>0xffffU || input->curve_word_000>0xffffU || input->curve_word_001>0xffffU || input->curve_word_002>0xffffU || input->curve_word_003>0xffffU || input->curve_word_004>0xffffU || input->curve_word_005>0xffffU || input->curve_word_006>0xffffU || input->curve_word_007>0xffffU || input->curve_word_008>0xffffU || input->curve_word_009>0xffffU || input->curve_word_010>0xffffU || input->curve_word_011>0xffffU || input->curve_word_012>0xffffU || input->curve_word_013>0xffffU || input->curve_word_014>0xffffU || input->curve_word_015>0xffffU || input->curve_word_016>0xffffU || input->curve_word_017>0xffffU || input->curve_word_018>0xffffU || input->curve_word_019>0xffffU || input->curve_word_020>0xffffU || input->curve_word_021>0xffffU || input->curve_word_022>0xffffU || input->curve_word_023>0xffffU || input->curve_word_024>0xffffU || input->curve_word_025>0xffffU || input->curve_word_026>0xffffU || input->curve_word_027>0xffffU || input->curve_word_028>0xffffU || input->curve_word_029>0xffffU || input->curve_word_030>0xffffU || input->curve_word_031>0xffffU || input->curve_word_032>0xffffU || input->curve_word_033>0xffffU || input->curve_word_034>0xffffU || input->curve_word_035>0xffffU || input->curve_word_036>0xffffU || input->curve_word_037>0xffffU || input->curve_word_038>0xffffU || input->curve_word_039>0xffffU || input->curve_word_040>0xffffU || input->curve_word_041>0xffffU || input->curve_word_042>0xffffU || input->curve_word_043>0xffffU || input->curve_word_044>0xffffU || input->curve_word_045>0xffffU || input->curve_word_046>0xffffU || input->curve_word_047>0xffffU || input->curve_word_048>0xffffU || input->curve_word_049>0xffffU || input->curve_word_050>0xffffU || input->curve_word_051>0xffffU || input->curve_word_052>0xffffU || input->curve_word_053>0xffffU || input->curve_word_054>0xffffU || input->curve_word_055>0xffffU || input->curve_word_056>0xffffU || input->curve_word_057>0xffffU || input->curve_word_058>0xffffU || input->curve_word_059>0xffffU || input->curve_word_060>0xffffU || input->curve_word_061>0xffffU || input->curve_word_062>0xffffU || input->curve_word_063>0xffffU || input->curve_word_064>0xffffU || input->surface_style>0xffU || input->surface_row_axis_style>0xffU || input->surface_column_axis_style>0xffU || input->curve_low_axis_style>0xffU || input->curve_high_axis_style>0xffU || input->surface_seed>0xffffU || input->surface_row_axis_seed>0xffffU || input->surface_column_axis_seed>0xffffU || input->curve_low_axis_seed>0xffffU || input->curve_high_axis_seed>0xffffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x1d08U)=(uint32_t)input->source_value;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1d12U)=(uint16_t)input->previous_curve;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x2d04U)=(uint32_t)input->previous_surface;
    for(index=0;index<ARRAY_SIZE(word_interp_caller_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)word_interp_caller_withdrawal_controlled[index].address,input->calibration+offset,
            word_interp_caller_withdrawal_controlled[index].size);
        offset+=word_interp_caller_withdrawal_controlled[index].size;
    }
    if(offset!=WORD_INTERP_CALLER_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(word_interp_caller_withdrawal_cases);++index){
        const struct path_case *input=&word_interp_caller_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,word_interp_caller_withdrawal_controlled,ARRAY_SIZE(word_interp_caller_withdrawal_controlled));
        snapshot(bound_before,word_interp_caller_withdrawal_bound,ARRAY_SIZE(word_interp_caller_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-word-interp-caller-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(word_interp_caller_withdrawal_controlled,ARRAY_SIZE(word_interp_caller_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(word_interp_caller_withdrawal_bound,ARRAY_SIZE(word_interp_caller_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_WORD_INTERP_CALLER_WITHDRAWAL status=PASS region=%s cases=%lu\n",WORD_INTERP_CALLER_WITHDRAWAL_REGION,index);
    return 0;
}
