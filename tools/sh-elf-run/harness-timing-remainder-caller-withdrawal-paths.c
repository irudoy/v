/* Input driver defined by defs/JK08A.timing-remainder-caller-withdrawal-paths.toml. */
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
#include "timing-remainder-caller-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[TIMING_REMAINDER_CALLER_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[TIMING_REMAINDER_CALLER_WITHDRAWAL_BOUND_SIZE];
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
    if((input->entry!=0x4d99cU && input->entry!=0x521a8U) || input->kind>=2U || input->byte_24c5>0xffU || input->byte_24cb>0xffU || input->byte_11f9>0xffU || input->byte_11fa>0xffU || input->byte_22fa>0xffU || input->byte_24c2>0xffU || input->byte_2378>0xffU || input->byte_229d>0xffU || input->byte_24c0>0xffU || input->byte_25fc>0xffU || input->byte_24cc>0xffU || input->byte_2459>0xffU || input->byte_226c>0xffU || input->byte_40e7>0xffU || input->byte_2356>0xffU || input->byte_12d6>0xffU || input->byte_4184>0xffU || input->byte_24c9>0xffU || input->byte_4251>0xffU || input->byte_23bf>0xffU || input->byte_23f0>0xffU || input->word_11d6>0xffffU || input->word_11d8>0xffffU || input->word_23c2>0xffffU || input->word_237e>0xffffU || input->word_2000>0xffffU || input->word_1ff6>0xffffU || input->word_10ca>0xffffU || input->word_11bc>0xffffU || input->word_23d4>0xffffU || input->word_23d6>0xffffU || input->word_23d8>0xffffU || input->word_23da>0xffffU || input->word_23dc>0xffffU || input->word_23de>0xffffU || input->word_241c>0xffffU || input->word_192e>0xffffU || input->curve_word_00>0xffffU || input->curve_word_01>0xffffU || input->curve_word_02>0xffffU || input->curve_word_03>0xffffU || input->curve_word_04>0xffffU || input->curve_word_05>0xffffU || input->curve_word_06>0xffffU || input->curve_word_07>0xffffU || input->curve_word_08>0xffffU || input->mode_flag>0xffU || input->counter_reload>0xffU || input->remainder_offset>0xffU || input->first_gain>0xffU || input->second_gain>0xffU || input->axis_style>0xffU || input->axis_seed>0xffffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24c5U)=(uint8_t)input->byte_24c5;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24cbU)=(uint8_t)input->byte_24cb;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11f9U)=(uint8_t)input->byte_11f9;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11faU)=(uint8_t)input->byte_11fa;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x22faU)=(uint8_t)input->byte_22fa;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24c2U)=(uint8_t)input->byte_24c2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2378U)=(uint8_t)input->byte_2378;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x229dU)=(uint8_t)input->byte_229d;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24c0U)=(uint8_t)input->byte_24c0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x25fcU)=(uint8_t)input->byte_25fc;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24ccU)=(uint8_t)input->byte_24cc;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2459U)=(uint8_t)input->byte_2459;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x226cU)=(uint8_t)input->byte_226c;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x40e7U)=(uint8_t)input->byte_40e7;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2356U)=(uint8_t)input->byte_2356;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x12d6U)=(uint8_t)input->byte_12d6;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4184U)=(uint8_t)input->byte_4184;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24c9U)=(uint8_t)input->byte_24c9;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4251U)=(uint8_t)input->byte_4251;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x23bfU)=(uint8_t)input->byte_23bf;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x23f0U)=(uint8_t)input->byte_23f0;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x11d6U)=(uint16_t)input->word_11d6;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x11d8U)=(uint16_t)input->word_11d8;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x23c2U)=(uint16_t)input->word_23c2;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x237eU)=(uint16_t)input->word_237e;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x2000U)=(uint16_t)input->word_2000;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1ff6U)=(uint16_t)input->word_1ff6;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x10caU)=(uint16_t)input->word_10ca;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x11bcU)=(uint16_t)input->word_11bc;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x23d4U)=(uint16_t)input->word_23d4;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x23d6U)=(uint16_t)input->word_23d6;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x23d8U)=(uint16_t)input->word_23d8;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x23daU)=(uint16_t)input->word_23da;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x23dcU)=(uint16_t)input->word_23dc;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x23deU)=(uint16_t)input->word_23de;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x241cU)=(uint16_t)input->word_241c;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x192eU)=(uint16_t)input->word_192e;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x1ff8U)=(uint32_t)input->history_word;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=(uint32_t)input->previous_fault;
    for(index=0;index<ARRAY_SIZE(timing_remainder_caller_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)timing_remainder_caller_withdrawal_controlled[index].address,input->calibration+offset,
            timing_remainder_caller_withdrawal_controlled[index].size);
        offset+=timing_remainder_caller_withdrawal_controlled[index].size;
    }
    if(offset!=TIMING_REMAINDER_CALLER_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(timing_remainder_caller_withdrawal_cases);++index){
        const struct path_case *input=&timing_remainder_caller_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,timing_remainder_caller_withdrawal_controlled,ARRAY_SIZE(timing_remainder_caller_withdrawal_controlled));
        snapshot(bound_before,timing_remainder_caller_withdrawal_bound,ARRAY_SIZE(timing_remainder_caller_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-timing-remainder-caller-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(timing_remainder_caller_withdrawal_controlled,ARRAY_SIZE(timing_remainder_caller_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(timing_remainder_caller_withdrawal_bound,ARRAY_SIZE(timing_remainder_caller_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_TIMING_REMAINDER_CALLER_WITHDRAWAL status=PASS region=%s cases=%lu\n",TIMING_REMAINDER_CALLER_WITHDRAWAL_REGION,index);
    return 0;
}
