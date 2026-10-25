/* Input driver defined by defs/JK08A.state-ratio-caller-withdrawal-paths.toml. */
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
#include "state-ratio-caller-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[STATE_RATIO_CALLER_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[STATE_RATIO_CALLER_WITHDRAWAL_BOUND_SIZE];
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
    if((input->entry!=0x64cb2U && input->entry!=0xbdc66U) || input->kind>=2U || input->word_1000>0xffffU || input->byte_106f>0xffU || input->byte_1071>0xffU || input->byte_1082>0xffU || input->byte_1083>0xffU || input->byte_108a>0xffU || input->byte_10e4>0xffU || input->word_13dc>0xffffU || input->word_13de>0xffffU || input->byte_1553>0xffU || input->byte_1704>0xffU || input->word_176a>0xffffU || input->word_1770>0xffffU || input->word_1772>0xffffU || input->word_1774>0xffffU || input->word_1866>0xffffU || input->word_1868>0xffffU || input->byte_1873>0xffU || input->byte_1a1e>0xffU || input->byte_1bee>0xffU || input->byte_1c5c>0xffU || input->byte_1c5e>0xffU || input->byte_2326>0xffU || input->word_240e>0xffffU || input->byte_244f>0xffU || input->byte_2450>0xffU || input->byte_2453>0xffU || input->byte_2454>0xffU || input->byte_246a>0xffU || input->byte_246b>0xffU || input->byte_246d>0xffU || input->byte_247b>0xffU || input->byte_247c>0xffU || input->byte_2482>0xffU || input->byte_248b>0xffU || input->byte_24a3>0xffU || input->byte_24a7>0xffU || input->byte_25ee>0xffU || input->byte_2772>0xffU || input->byte_3373>0xffU || input->byte_418e>0xffU || input->byte_41fa>0xffU || input->byte_4250>0xffU || input->byte_558a>0xffU || input->config_851d>0xffU || input->config_8616>0xffU || input->config_86f9>0xffU || input->config_870c>0xffU || input->config_8710>0xffU || input->config_8b34>0xffU || input->config_8b38>0xffU || input->config_8b3f>0xffU || input->config_8b42>0xffU || input->config_8d2d>0xffU || input->config_8d2e>0xffU || input->config_8ea6>0xffffU || input->config_906c>0xffffU || input->config_9456>0xffffU || input->curve_first_0>0xffU || input->curve_first_1>0xffU || input->curve_first_2>0xffU || input->curve_first_3>0xffU || input->curve_first_4>0xffU || input->curve_first_5>0xffU || input->curve_first_6>0xffU || input->curve_first_7>0xffU || input->curve_second_0>0xffU || input->curve_second_1>0xffU || input->curve_second_2>0xffU || input->curve_second_3>0xffU || input->curve_second_4>0xffU || input->curve_second_5>0xffU || input->curve_second_6>0xffU || input->curve_second_7>0xffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1000U)=(uint16_t)input->word_1000;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x106fU)=(uint8_t)input->byte_106f;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1071U)=(uint8_t)input->byte_1071;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1082U)=(uint8_t)input->byte_1082;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1083U)=(uint8_t)input->byte_1083;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x108aU)=(uint8_t)input->byte_108a;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x10e4U)=(uint8_t)input->byte_10e4;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x13dcU)=(uint16_t)input->word_13dc;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x13deU)=(uint16_t)input->word_13de;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1553U)=(uint8_t)input->byte_1553;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1704U)=(uint8_t)input->byte_1704;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x176aU)=(uint16_t)input->word_176a;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1770U)=(uint16_t)input->word_1770;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1772U)=(uint16_t)input->word_1772;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1774U)=(uint16_t)input->word_1774;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1866U)=(uint16_t)input->word_1866;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1868U)=(uint16_t)input->word_1868;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1873U)=(uint8_t)input->byte_1873;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1a1eU)=(uint8_t)input->byte_1a1e;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1beeU)=(uint8_t)input->byte_1bee;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1c5cU)=(uint8_t)input->byte_1c5c;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1c5eU)=(uint8_t)input->byte_1c5e;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2326U)=(uint8_t)input->byte_2326;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x240eU)=(uint16_t)input->word_240e;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x244fU)=(uint8_t)input->byte_244f;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2450U)=(uint8_t)input->byte_2450;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2453U)=(uint8_t)input->byte_2453;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2454U)=(uint8_t)input->byte_2454;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x246aU)=(uint8_t)input->byte_246a;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x246bU)=(uint8_t)input->byte_246b;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x246dU)=(uint8_t)input->byte_246d;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x247bU)=(uint8_t)input->byte_247b;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x247cU)=(uint8_t)input->byte_247c;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2482U)=(uint8_t)input->byte_2482;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x248bU)=(uint8_t)input->byte_248b;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24a3U)=(uint8_t)input->byte_24a3;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24a7U)=(uint8_t)input->byte_24a7;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x25eeU)=(uint8_t)input->byte_25ee;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2772U)=(uint8_t)input->byte_2772;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x3373U)=(uint8_t)input->byte_3373;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x418eU)=(uint8_t)input->byte_418e;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41faU)=(uint8_t)input->byte_41fa;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4250U)=(uint8_t)input->byte_4250;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x558aU)=(uint8_t)input->byte_558a;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=(uint32_t)input->dword_9818;
    for(index=0;index<ARRAY_SIZE(state_ratio_caller_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)state_ratio_caller_withdrawal_controlled[index].address,input->calibration+offset,
            state_ratio_caller_withdrawal_controlled[index].size);
        offset+=state_ratio_caller_withdrawal_controlled[index].size;
    }
    if(offset!=STATE_RATIO_CALLER_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(state_ratio_caller_withdrawal_cases);++index){
        const struct path_case *input=&state_ratio_caller_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,state_ratio_caller_withdrawal_controlled,ARRAY_SIZE(state_ratio_caller_withdrawal_controlled));
        snapshot(bound_before,state_ratio_caller_withdrawal_bound,ARRAY_SIZE(state_ratio_caller_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-state-ratio-caller-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(state_ratio_caller_withdrawal_controlled,ARRAY_SIZE(state_ratio_caller_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(state_ratio_caller_withdrawal_bound,ARRAY_SIZE(state_ratio_caller_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_STATE_RATIO_CALLER_WITHDRAWAL status=PASS region=%s cases=%lu\n",STATE_RATIO_CALLER_WITHDRAWAL_REGION,index);
    return 0;
}
