/* Input driver defined by defs/JK08A.signed-abs-register-helper-withdrawal-paths.toml. */
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
#include "signed-abs-register-helper-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[SIGNED_ABS_REGISTER_HELPER_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[SIGNED_ABS_REGISTER_HELPER_WITHDRAWAL_BOUND_SIZE];
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
    
    if((input->entry!=0x22590U) || input->kind>=1U || input->raw_control_byte_0>0xffU || input->raw_control_byte_1>0xffU || input->raw_control_byte_2>0xffU || input->raw_control_byte_3>0xffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x0U)=(uint8_t)0xa5U;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2c1cU)=(uint8_t)input->raw_control_byte_0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2c1dU)=(uint8_t)input->raw_control_byte_1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2c1eU)=(uint8_t)input->raw_control_byte_2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2c1fU)=(uint8_t)input->raw_control_byte_3;

    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(signed_abs_register_helper_withdrawal_cases);++index){
        const struct path_case *input=&signed_abs_register_helper_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,signed_abs_register_helper_withdrawal_controlled,ARRAY_SIZE(signed_abs_register_helper_withdrawal_controlled));
        snapshot(bound_before,signed_abs_register_helper_withdrawal_bound,ARRAY_SIZE(signed_abs_register_helper_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-signed-abs-register-helper-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(signed_abs_register_helper_withdrawal_controlled,ARRAY_SIZE(signed_abs_register_helper_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(signed_abs_register_helper_withdrawal_bound,ARRAY_SIZE(signed_abs_register_helper_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_SIGNED_ABS_REGISTER_HELPER_WITHDRAWAL status=PASS region=%s cases=%lu\n",SIGNED_ABS_REGISTER_HELPER_WITHDRAWAL_REGION,index);
    return 0;
}
