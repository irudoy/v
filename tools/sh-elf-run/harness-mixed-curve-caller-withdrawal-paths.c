/* Input driver defined by defs/JK08A.mixed-curve-caller-withdrawal-paths.toml. */
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
#include "mixed-curve-caller-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[MIXED_CURVE_CALLER_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[MIXED_CURVE_CALLER_WITHDRAWAL_BOUND_SIZE];
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
    if((input->entry!=0x3b498U && input->entry!=0x41db6U && input->entry!=0x4bdc2U && input->entry!=0x659aeU) || input->kind>=4U || input->byte_1170>0xffU || input->byte_2465>0xffU || input->byte_2468>0xffU || input->byte_1765>0xffU || input->byte_1763>0xffU || input->byte_1f62>0xffU || input->byte_2315>0xffU || input->byte_2458>0xffU || input->byte_23bd>0xffU || input->byte_23c5>0xffU || input->byte_23f1>0xffU || input->byte_12dc>0xffU || input->byte_15ea>0xffU || input->byte_1a7d>0xffU || input->byte_41ab>0xffU || input->byte_106f>0xffU || input->byte_134c>0xffU || input->byte_1348>0xffU || input->byte_134a>0xffU || input->byte_12d4>0xffU || input->byte_24d1>0xffU || input->byte_23ee>0xffU || input->byte_1830>0xffU || input->byte_15eb>0xffU || input->byte_2485>0xffU || input->word_1e60>0xffffU || input->word_114e>0xffffU || input->word_120e>0xffffU || input->word_1e62>0xffffU || input->word_1138>0xffffU || input->word_1752>0xffffU || input->word_2266>0xffffU || input->word_28b8>0xffffU || input->word_28ba>0xffffU || input->word_1024>0xffffU || input->word_10ca>0xffffU || input->word_1900>0xffffU || input->word_18e4>0xffffU || input->word_2408>0xffffU || input->word_18ca>0xffffU || input->word_22e8>0xffffU || input->word_18cc>0xffffU || input->surface_word_00>0xffffU || input->surface_word_01>0xffffU || input->surface_word_02>0xffffU || input->surface_word_03>0xffffU || input->surface_word_04>0xffffU || input->surface_word_05>0xffffU || input->surface_word_06>0xffffU || input->surface_word_07>0xffffU || input->surface_word_08>0xffffU || input->surface_word_09>0xffffU || input->surface_word_10>0xffffU || input->surface_word_11>0xffffU || input->surface_word_12>0xffffU || input->surface_word_13>0xffffU || input->surface_word_14>0xffffU || input->surface_word_15>0xffffU || input->surface_word_16>0xffffU || input->surface_word_17>0xffffU || input->surface_word_18>0xffffU || input->surface_word_19>0xffffU || input->surface_word_20>0xffffU || input->surface_word_21>0xffffU || input->surface_word_22>0xffffU || input->surface_word_23>0xffffU || input->surface_word_24>0xffffU || input->surface_word_25>0xffffU || input->surface_word_26>0xffffU || input->surface_word_27>0xffffU || input->surface_word_28>0xffffU || input->surface_word_29>0xffffU || input->surface_word_30>0xffffU || input->surface_word_31>0xffffU || input->surface_word_32>0xffffU || input->surface_word_33>0xffffU || input->surface_word_34>0xffffU || input->surface_word_35>0xffffU || input->surface_word_36>0xffffU || input->surface_word_37>0xffffU || input->surface_word_38>0xffffU || input->surface_word_39>0xffffU || input->surface_word_40>0xffffU || input->surface_word_41>0xffffU || input->surface_word_42>0xffffU || input->surface_word_43>0xffffU || input->surface_word_44>0xffffU || input->surface_word_45>0xffffU || input->surface_word_46>0xffffU || input->surface_word_47>0xffffU || input->surface_word_48>0xffffU || input->surface_word_49>0xffffU || input->surface_word_50>0xffffU || input->surface_word_51>0xffffU || input->surface_word_52>0xffffU || input->surface_word_53>0xffffU || input->surface_word_54>0xffffU || input->surface_word_55>0xffffU || input->surface_word_56>0xffffU || input->surface_word_57>0xffffU || input->surface_word_58>0xffffU || input->surface_word_59>0xffffU || input->surface_word_60>0xffffU || input->surface_word_61>0xffffU || input->surface_word_62>0xffffU || input->surface_word_63>0xffffU || input->implicit_word_00>0xffffU || input->implicit_word_01>0xffffU || input->implicit_word_02>0xffffU || input->implicit_word_03>0xffffU || input->implicit_word_04>0xffffU || input->implicit_word_05>0xffffU || input->implicit_word_06>0xffffU || input->implicit_word_07>0xffffU || input->implicit_word_08>0xffffU || input->implicit_word_09>0xffffU || input->implicit_word_10>0xffffU || input->implicit_word_11>0xffffU || input->implicit_word_12>0xffffU || input->implicit_word_13>0xffffU || input->implicit_word_14>0xffffU || input->implicit_word_15>0xffffU || input->implicit_word_16>0xffffU || input->implicit_word_17>0xffffU || input->implicit_word_18>0xffffU || input->implicit_word_19>0xffffU || input->implicit_word_20>0xffffU || input->implicit_word_21>0xffffU || input->implicit_word_22>0xffffU || input->implicit_word_23>0xffffU || input->implicit_word_24>0xffffU || input->implicit_word_25>0xffffU || input->implicit_word_26>0xffffU || input->implicit_word_27>0xffffU || input->implicit_word_28>0xffffU || input->implicit_word_29>0xffffU || input->curve_timing_00>0xffU || input->curve_timing_01>0xffU || input->curve_timing_02>0xffU || input->curve_timing_03>0xffU || input->curve_timing_04>0xffU || input->curve_timing_05>0xffU || input->curve_timing_06>0xffU || input->curve_timing_07>0xffU || input->curve_timing_08>0xffU || input->curve_scale_00>0xffU || input->curve_scale_01>0xffU || input->curve_scale_02>0xffU || input->curve_scale_03>0xffU || input->curve_scale_04>0xffU || input->curve_scale_05>0xffU || input->curve_scale_06>0xffU || input->curve_scale_07>0xffU || input->curve_scale_08>0xffU || input->threshold_word>0xffffU || input->gain_byte>0xffU || input->axis_outer_style>0xffU || input->axis_inner_style>0xffU || input->axis_timing_style>0xffU || input->axis_scale_style>0xffU || input->axis_outer_seed>0xffffU || input->axis_inner_seed>0xffffU || input->axis_timing_seed>0xffU || input->axis_scale_seed>0xffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1170U)=(uint8_t)input->byte_1170;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2465U)=(uint8_t)input->byte_2465;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2468U)=(uint8_t)input->byte_2468;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1765U)=(uint8_t)input->byte_1765;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1763U)=(uint8_t)input->byte_1763;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1f62U)=(uint8_t)input->byte_1f62;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2315U)=(uint8_t)input->byte_2315;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2458U)=(uint8_t)input->byte_2458;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x23bdU)=(uint8_t)input->byte_23bd;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x23c5U)=(uint8_t)input->byte_23c5;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x23f1U)=(uint8_t)input->byte_23f1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x12dcU)=(uint8_t)input->byte_12dc;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x15eaU)=(uint8_t)input->byte_15ea;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1a7dU)=(uint8_t)input->byte_1a7d;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41abU)=(uint8_t)input->byte_41ab;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x106fU)=(uint8_t)input->byte_106f;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x134cU)=(uint8_t)input->byte_134c;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1348U)=(uint8_t)input->byte_1348;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x134aU)=(uint8_t)input->byte_134a;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x12d4U)=(uint8_t)input->byte_12d4;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24d1U)=(uint8_t)input->byte_24d1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x23eeU)=(uint8_t)input->byte_23ee;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1830U)=(uint8_t)input->byte_1830;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x15ebU)=(uint8_t)input->byte_15eb;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2485U)=(uint8_t)input->byte_2485;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1e60U)=(uint16_t)input->word_1e60;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x114eU)=(uint16_t)input->word_114e;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x120eU)=(uint16_t)input->word_120e;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1e62U)=(uint16_t)input->word_1e62;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1138U)=(uint16_t)input->word_1138;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1752U)=(uint16_t)input->word_1752;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x2266U)=(uint16_t)input->word_2266;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x28b8U)=(uint16_t)input->word_28b8;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x28baU)=(uint16_t)input->word_28ba;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1024U)=(uint16_t)input->word_1024;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x10caU)=(uint16_t)input->word_10ca;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1900U)=(uint16_t)input->word_1900;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x18e4U)=(uint16_t)input->word_18e4;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x2408U)=(uint16_t)input->word_2408;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x18caU)=(uint16_t)input->word_18ca;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x22e8U)=(uint16_t)input->word_22e8;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x18ccU)=(uint16_t)input->word_18cc;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=(uint32_t)input->previous_fault;
    for(index=0;index<ARRAY_SIZE(mixed_curve_caller_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)mixed_curve_caller_withdrawal_controlled[index].address,input->calibration+offset,
            mixed_curve_caller_withdrawal_controlled[index].size);
        offset+=mixed_curve_caller_withdrawal_controlled[index].size;
    }
    if(offset!=MIXED_CURVE_CALLER_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(mixed_curve_caller_withdrawal_cases);++index){
        const struct path_case *input=&mixed_curve_caller_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,mixed_curve_caller_withdrawal_controlled,ARRAY_SIZE(mixed_curve_caller_withdrawal_controlled));
        snapshot(bound_before,mixed_curve_caller_withdrawal_bound,ARRAY_SIZE(mixed_curve_caller_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-mixed-curve-caller-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(mixed_curve_caller_withdrawal_controlled,ARRAY_SIZE(mixed_curve_caller_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(mixed_curve_caller_withdrawal_bound,ARRAY_SIZE(mixed_curve_caller_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_MIXED_CURVE_CALLER_WITHDRAWAL status=PASS region=%s cases=%lu\n",MIXED_CURVE_CALLER_WITHDRAWAL_REGION,index);
    return 0;
}
