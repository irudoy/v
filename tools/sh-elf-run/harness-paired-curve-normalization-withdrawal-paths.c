/* Input driver defined by defs/JK08A.paired-curve-normalization-withdrawal-paths.toml. */
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
#include "paired-curve-normalization-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[PAIRED_CURVE_NORMALIZATION_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[PAIRED_CURVE_NORMALIZATION_WITHDRAWAL_BOUND_SIZE];
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
    if((input->entry!=0x655b4U && input->entry!=0x65b08U) || input->kind>=2U || input->word_119e>0xffffU || input->word_11a0>0xffffU || input->byte_11a2>0xffU || input->byte_11c1>0xffU || input->byte_11c2>0xffU || input->byte_12df>0xffU || input->byte_15ea>0xffU || input->word_18cc>0xffffU || input->word_18ce>0xffffU || input->word_18d4>0xffffU || input->byte_23e2>0xffU || input->byte_23f1>0xffU || input->byte_2404>0xffU || input->byte_413f>0xffU || input->config_8710>0xffU || input->curve_axis_0>0xffU || input->curve_axis_1>0xffU || input->curve_axis_2>0xffU || input->curve_axis_3>0xffU || input->curve_axis_4>0xffU || input->curve_axis_5>0xffU || input->curve_axis_6>0xffU || input->curve_axis_7>0xffU || input->curve_axis_8>0xffU || input->curve_axis_9>0xffU || input->curve_axis_10>0xffU || input->curve_axis_11>0xffU || input->curve_axis_12>0xffU || input->curve_axis_13>0xffU || input->curve_axis_14>0xffU || input->curve_axis_15>0xffU || input->curve_value_0>0xffU || input->curve_value_1>0xffU || input->curve_value_2>0xffU || input->curve_value_3>0xffU || input->curve_value_4>0xffU || input->curve_value_5>0xffU || input->curve_value_6>0xffU || input->curve_value_7>0xffU || input->curve_value_8>0xffU || input->curve_value_9>0xffU || input->curve_value_10>0xffU || input->curve_value_11>0xffU || input->curve_value_12>0xffU || input->curve_value_13>0xffU || input->curve_value_14>0xffU || input->curve_value_15>0xffU || input->curve_value_16>0xffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x119eU)=(uint16_t)input->word_119e;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x11a0U)=(uint16_t)input->word_11a0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11a2U)=(uint8_t)input->byte_11a2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11c1U)=(uint8_t)input->byte_11c1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11c2U)=(uint8_t)input->byte_11c2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x12dfU)=(uint8_t)input->byte_12df;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x15eaU)=(uint8_t)input->byte_15ea;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x18ccU)=(uint16_t)input->word_18cc;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x18ceU)=(uint16_t)input->word_18ce;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x18d4U)=(uint16_t)input->word_18d4;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x23e2U)=(uint8_t)input->byte_23e2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x23f1U)=(uint8_t)input->byte_23f1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2404U)=(uint8_t)input->byte_2404;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x413fU)=(uint8_t)input->byte_413f;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=(uint32_t)input->dword_9818;
    for(index=0;index<ARRAY_SIZE(paired_curve_normalization_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)paired_curve_normalization_withdrawal_controlled[index].address,input->calibration+offset,
            paired_curve_normalization_withdrawal_controlled[index].size);
        offset+=paired_curve_normalization_withdrawal_controlled[index].size;
    }
    if(offset!=PAIRED_CURVE_NORMALIZATION_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(paired_curve_normalization_withdrawal_cases);++index){
        const struct path_case *input=&paired_curve_normalization_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,paired_curve_normalization_withdrawal_controlled,ARRAY_SIZE(paired_curve_normalization_withdrawal_controlled));
        snapshot(bound_before,paired_curve_normalization_withdrawal_bound,ARRAY_SIZE(paired_curve_normalization_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-paired-curve-normalization-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(paired_curve_normalization_withdrawal_controlled,ARRAY_SIZE(paired_curve_normalization_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(paired_curve_normalization_withdrawal_bound,ARRAY_SIZE(paired_curve_normalization_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_PAIRED_CURVE_NORMALIZATION_WITHDRAWAL status=PASS region=%s cases=%lu\n",PAIRED_CURVE_NORMALIZATION_WITHDRAWAL_REGION,index);
    return 0;
}
